#!/usr/bin/env python
"""Calibrate J0 support thresholds in a frozen synthetic joint-process world.

This is not evidence about people.  It only determines which minimum event and
transition counts can estimate a declared kernel-mean joint-process object at
the target author sample size before real PANDORA endpoints are inspected.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.joint_process import (  # noqa: E402
    random_fourier_map,
    same_author_auc,
    selected_candidate,
    softmax,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/v6_joint_process_stage_j1.json")
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "results/v6_joint_process_stage_j1_calibration")
    parser.add_argument("--report", type=Path,
                        default=ROOT / "reports/V6_JOINT_PROCESS_STAGE_J1_CALIBRATION.md")
    parser.add_argument("--quick", action="store_true", help="Use 20 simulations for a smoke run only.")
    return parser.parse_args()


def _simulate_pair(
    rng: np.random.Generator,
    *,
    n_authors: int,
    event_count: int,
    contexts: int,
    expression_dimensions: int,
    rff_dimensions: int,
    selection_sd: float,
    expression_sd: float,
    transition_sd: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return two independent observations of every synthetic author's process."""
    input_dimensions = contexts + expression_dimensions
    # The same first dimensions map events; doubled dimensions map adjacent pairs.
    event_weights = rng.normal(0.0, 0.55, size=(input_dimensions, rff_dimensions))
    pair_weights = rng.normal(0.0, 0.35, size=(2 * input_dimensions, rff_dimensions))
    phases = rng.uniform(0.0, 2.0 * np.pi, size=rff_dimensions)
    context_effects = rng.normal(0.0, 0.7, size=(contexts, expression_dimensions))
    selection_logits = rng.normal(0.0, selection_sd, size=(n_authors, contexts))
    expression_offset = rng.normal(0.0, expression_sd, size=(n_authors, expression_dimensions))
    # A common persistence is part of the collection process. Only the author
    # deviation is a possible author-conditioned transition component.
    persistence = np.clip(0.55 + rng.normal(0.0, transition_sd, size=n_authors), 0.05, 1.35)
    identity = np.eye(contexts)

    def draw() -> np.ndarray:
        previous = rng.integers(contexts, size=n_authors)
        event_sequence = np.empty((n_authors, event_count, input_dimensions), dtype=float)
        for event_index in range(event_count):
            logits = selection_logits.copy()
            logits[np.arange(n_authors), previous] += persistence
            logits -= logits.max(axis=1, keepdims=True)
            probabilities = np.exp(logits)
            probabilities /= probabilities.sum(axis=1, keepdims=True)
            current = (np.cumsum(probabilities, axis=1) < rng.random(n_authors)[:, None]).sum(axis=1)
            expression = context_effects[current] + expression_offset
            expression += rng.normal(0.0, 1.0, size=(n_authors, expression_dimensions))
            event_sequence[:, event_index, :] = np.concatenate([identity[current], expression], axis=1)
            previous = current
        event_map = random_fourier_map(
            event_sequence.reshape(-1, input_dimensions), event_weights, phases
        ).reshape(n_authors, event_count, rff_dimensions).mean(axis=1)
        pair_values = np.concatenate([event_sequence[:, :-1, :], event_sequence[:, 1:, :]], axis=2)
        pair_map = random_fourier_map(
            pair_values.reshape(-1, 2 * input_dimensions), pair_weights, phases
        ).reshape(n_authors, event_count - 1, rff_dimensions).mean(axis=1)
        return np.concatenate([event_map, pair_map], axis=1)

    return draw(), draw()


def run_calibration(cfg: dict[str, Any], *, quick: bool) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Run frozen null/alternative simulations for every support candidate."""
    spec = cfg["calibration"]
    simulations = 8 if quick else int(spec["simulations"])
    n_authors = min(80, int(spec["n_authors"])) if quick else int(spec["n_authors"])
    rows: list[dict[str, Any]] = []
    for candidate_index, candidate in enumerate(spec["candidate_support_pairs"]):
        auc_by_regime: dict[str, list[float]] = {
            name: [] for name in spec["signal_regimes"]
        }
        for repetition in range(simulations):
            seed = int(cfg["seed"]) + candidate_index * 100_000 + repetition
            for regime_index, (name, regime) in enumerate(spec["signal_regimes"].items()):
                left, right = _simulate_pair(
                    np.random.default_rng(seed + regime_index * 50_000), n_authors=n_authors,
                    event_count=int(candidate["min_events"]), contexts=int(spec["contexts"]),
                    expression_dimensions=int(spec["expression_dimensions"]),
                    rff_dimensions=int(spec["rff_dimensions"]),
                    selection_sd=float(regime["selection_sd"]),
                    expression_sd=float(regime["expression_sd"]),
                    transition_sd=float(regime["transition_sd"]),
                )
                auc_by_regime[name].append(same_author_auc(left, right))
        weak = np.asarray(auc_by_regime["weak"])
        moderate = np.asarray(auc_by_regime["moderate"])
        null = np.asarray(auc_by_regime["null"])
        promotion_rate = float(np.mean(null >= float(spec["promotion_auc"])))
        row = {
            "min_events": int(candidate["min_events"]),
            "min_transitions": int(candidate["min_transitions"]),
            "simulations": simulations,
            "n_authors": n_authors,
            "weak_auc_median": float(np.median(weak)),
            "weak_auc_q05": float(np.quantile(weak, 0.05)),
            "moderate_auc_median": float(np.median(moderate)),
            "moderate_auc_q05": float(np.quantile(moderate, 0.05)),
            "null_auc_median": float(np.median(null)),
            "null_auc_q95": float(np.quantile(null, 0.95)),
            "null_promotion_rate": promotion_rate,
        }
        row["qualified"] = bool(
            row["weak_auc_median"] >= float(spec["minimum_weak_auc_median"])
            and row["weak_auc_q05"] >= float(spec["minimum_weak_auc_q05"])
            and row["moderate_auc_q05"] >= float(spec["minimum_moderate_auc_q05"])
            and row["null_promotion_rate"] <= float(spec["maximum_null_promotion_rate"])
        )
        rows.append(row)
    frame = pd.DataFrame(rows)
    selected = selected_candidate(frame)
    decision = {
        "run_name": cfg["run_name"],
        "synthetic_only": True,
        "selected_support": selected,
        "decision": "CALIBRATED" if selected else "REFUSE_NO_CALIBRATED_SUPPORT_THRESHOLD",
        "criteria": {
            "minimum_weak_auc_median": spec["minimum_weak_auc_median"],
            "minimum_weak_auc_q05": spec["minimum_weak_auc_q05"],
            "minimum_moderate_auc_q05": spec["minimum_moderate_auc_q05"],
            "maximum_null_promotion_rate": spec["maximum_null_promotion_rate"],
            "promotion_auc": spec["promotion_auc"],
        },
    }
    return frame, decision


def main() -> None:
    args = parse_args()
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    results, decision = run_calibration(cfg, quick=args.quick)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output_dir / "calibration_grid.csv", index=False)
    (args.output_dir / "calibration_decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(f"""# SUICA V6 Joint-Process J1: Synthetic Support Calibration

## Scope

This simulation selects a minimum natural-event support threshold for the
declared kernel-mean joint-process estimator. It checks a null world plus
weak and moderate author-conditioned worlds. It is not evidence about human
personality, clinical state, language equivalence, or PANDORA.

## Frozen decision

`{decision['decision']}`. Selected support: `{decision['selected_support']}`.

## Calibration grid

{results.round(4).to_markdown(index=False)}

## Interpretation boundary

The synthetic worlds vary only the magnitude of stable author-specific
selection preferences, expression offsets, and transition persistence. The
resulting threshold only rules out clearly under-supported estimators in these
declared worlds. It cannot justify a human interpretation or separate latent
topic from expression in real text.
""", encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
