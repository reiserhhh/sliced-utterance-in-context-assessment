#!/usr/bin/env python
"""Calibrate J3 ordered-transition support before reading real text endpoints."""
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

from suica_core.joint_process import same_author_auc  # noqa: E402
from suica_core.ordered_transition import (  # noqa: E402
    block_order_null_operator,
    centered_transition_operator,
    ordered_pairs_from_blocks,
)


def parse_args() -> argparse.Namespace:
    """Parse the frozen synthetic calibration destinations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path,
                        default=ROOT / "configs/v6_ordered_transition_stage_j3.json")
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "results/v6_ordered_transition_stage_j3_calibration")
    parser.add_argument("--report", type=Path,
                        default=ROOT / "reports/V6_ORDERED_TRANSITION_STAGE_J3_CALIBRATION.md")
    parser.add_argument("--quick", action="store_true", help="Small smoke calibration only.")
    return parser.parse_args()


def _view_blocks(
    rng: np.random.Generator,
    *,
    means: np.ndarray,
    scales: np.ndarray,
    rho: np.ndarray,
    events_per_view: int,
    block_size: int,
) -> np.ndarray:
    """Draw independent block-structured autoregressive views for all authors."""
    n_authors, dimensions = means.shape
    blocks_per_view = events_per_view // block_size
    sequence = np.empty((n_authors, events_per_view, dimensions), dtype=float)
    previous = means + rng.normal(size=(n_authors, dimensions)) * scales
    for index in range(events_per_view):
        innovation = rng.normal(size=(n_authors, dimensions)) * scales
        previous = means + rho * (previous - means) + innovation
        sequence[:, index, :] = previous
    return sequence.reshape(n_authors, blocks_per_view, block_size, dimensions)


def _operators_from_views(blocks: np.ndarray, *, null_draws: int, seed_prefix: str) -> tuple[np.ndarray, np.ndarray]:
    """Return real and local-order-null operator vectors for every author view."""
    real, null = [], []
    for index, author_blocks in enumerate(blocks):
        source, target = ordered_pairs_from_blocks(author_blocks)
        real.append(centered_transition_operator(source, target, diagonal_standardize=True))
        null.append(block_order_null_operator(
            author_blocks, draws=null_draws, seed_key=f"{seed_prefix}::{index}", diagonal_standardize=True,
        ))
    return np.vstack(real), np.vstack(null)


def _simulate_once(
    *,
    seed: int,
    n_authors: int,
    events_per_view: int,
    dimensions: int,
    block_size: int,
    author_transition_sd: float,
) -> tuple[float, float, float]:
    """Compare real ordered operators to their matched local-order nulls."""
    rng = np.random.default_rng(seed)
    means = rng.normal(0.0, 0.45, size=(n_authors, dimensions))
    scales = np.exp(rng.normal(0.0, 0.12, size=(n_authors, dimensions)))
    # Every world has a shared weak global serial process; only the declared
    # regime changes author-to-author transition structure.
    rho = np.clip(0.16 + rng.normal(0.0, author_transition_sd, size=(n_authors, dimensions)), -0.45, 0.65)
    left_blocks = _view_blocks(
        rng, means=means, scales=scales, rho=rho,
        events_per_view=events_per_view, block_size=block_size,
    )
    right_blocks = _view_blocks(
        rng, means=means, scales=scales, rho=rho,
        events_per_view=events_per_view, block_size=block_size,
    )
    left_real, left_null = _operators_from_views(left_blocks, null_draws=5, seed_prefix=f"{seed}::left")
    right_real, right_null = _operators_from_views(right_blocks, null_draws=5, seed_prefix=f"{seed}::right")
    real_auc = same_author_auc(left_real, right_real)
    null_auc = same_author_auc(left_null, right_null)
    return float(real_auc), float(null_auc), float(real_auc - null_auc)


def run_calibration(cfg: dict[str, Any], *, quick: bool) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Run null/weak/moderate support calibration without real text data."""
    spec = cfg["calibration"]
    simulations = 8 if quick else int(spec["simulations"])
    n_authors = min(80, int(spec["n_authors"])) if quick else int(spec["n_authors"])
    rows: list[dict[str, Any]] = []
    for support_index, events_per_view in enumerate(spec["candidate_events_per_view"]):
        values: dict[str, list[float]] = {name: [] for name in spec["signal_regimes"]}
        for repetition in range(simulations):
            for regime_index, (regime, parameters) in enumerate(spec["signal_regimes"].items()):
                _, _, delta = _simulate_once(
                    seed=int(cfg["seed"]) + support_index * 100_000 + repetition * 1_000 + regime_index,
                    n_authors=n_authors,
                    events_per_view=int(events_per_view), dimensions=int(spec["event_dimensions"]),
                    block_size=int(spec["block_size"]),
                    author_transition_sd=float(parameters["author_transition_sd"]),
                )
                values[regime].append(delta)
        weak = np.asarray(values["weak"])
        moderate = np.asarray(values["moderate"])
        null = np.asarray(values["null"])
        row = {
            "events_per_view": int(events_per_view),
            "total_events_for_disjoint_views": int(2 * events_per_view),
            "simulations": simulations,
            "n_authors": n_authors,
            "weak_delta_auc_median": float(np.median(weak)),
            "weak_delta_auc_q05": float(np.quantile(weak, 0.05)),
            "moderate_delta_auc_median": float(np.median(moderate)),
            "moderate_delta_auc_q05": float(np.quantile(moderate, 0.05)),
            "null_delta_auc_median": float(np.median(null)),
            "null_delta_auc_q95": float(np.quantile(null, 0.95)),
        }
        row["weak_delta_over_null_median"] = row["weak_delta_auc_median"] - row["null_delta_auc_median"]
        row["moderate_q05_over_null_q95"] = row["moderate_delta_auc_q05"] - row["null_delta_auc_q95"]
        row["qualified"] = bool(
            row["weak_delta_over_null_median"] >= float(spec["minimum_weak_delta_over_null_median"])
            and row["moderate_q05_over_null_q95"] >= float(spec["minimum_moderate_q05_over_null_q95"])
        )
        rows.append(row)
    results = pd.DataFrame(rows)
    qualified = results.loc[results["qualified"]].sort_values("events_per_view", kind="stable")
    selected = None if qualified.empty else {
        "events_per_view": int(qualified.iloc[0]["events_per_view"]),
        "block_size": int(spec["block_size"]),
    }
    decision = {
        "run_name": cfg["run_name"],
        "synthetic_only": True,
        "selected_support": selected,
        "decision": "CALIBRATED" if selected else "REFUSE_NO_CALIBRATED_ORDER_SUPPORT",
        "criteria": {
            "minimum_weak_delta_over_null_median": spec["minimum_weak_delta_over_null_median"],
            "minimum_moderate_q05_over_null_q95": spec["minimum_moderate_q05_over_null_q95"],
        },
    }
    return results, decision


def main() -> None:
    """Write calibration artifacts and no human-data result."""
    args = parse_args()
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    results, decision = run_calibration(cfg, quick=args.quick)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output_dir / "ordered_transition_calibration_grid.csv", index=False)
    (args.output_dir / "ordered_transition_calibration_decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(f"""# SUICA V6 Ordered-Transition J3: Synthetic Calibration

This calibration contains no human text or endpoint label. It asks whether the
centred ordered-transition operator can distinguish a stable author-specific
autoregressive signature from its within-block order null at each support level.

## Decision

`{decision['decision']}`. Selected per-view support: `{decision['selected_support']}`.

## Grid

{results.round(4).to_markdown(index=False)}

## Boundary

The synthetic author transition deviations are a declared estimator stress test,
not a model of a person or proof that PANDORA contains the same mechanism.
""", encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
