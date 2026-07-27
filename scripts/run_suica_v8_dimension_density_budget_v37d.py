#!/usr/bin/env python3
"""Run the exploratory V3.7D dimension-density-budget phase diagram."""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_dimension_density_budget import (  # noqa: E402
    DensityWorldSpec,
    evaluate_density_population,
    simulate_group_free_density_world,
)
from suica_core.v8_group_free_routing_transport import (  # noqa: E402
    resample_routing_counts,
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=True)
        + "\n",
        encoding="utf-8",
    )


def _worker(payload: tuple[dict[str, Any], dict[str, Any], int]) -> dict:
    config, condition, seed = payload
    root = np.random.SeedSequence(seed)
    latent_seq, reference_seq, observed_seq = root.spawn(3)
    rank = int(condition["latent_rank"])
    if condition["signal_regime"] == "fixed_total_signal":
        author_rms = float(config["base_author_rms"])
    else:
        author_rms = float(config["base_author_rms"]) * np.sqrt(
            rank / float(config["signal_anchor_rank"])
        )
    latent = simulate_group_free_density_world(
        seed=int(latent_seq.generate_state(1, dtype=np.uint64)[0]),
        spec=DensityWorldSpec(
            authors=(
                int(config["denoiser_training_authors"])
                + int(condition["authors"])
            ),
            latent_rank=rank,
            events_per_context_session=int(condition["event_budget"]),
            author_rms=author_rms,
            discovery_contexts=int(config["discovery_contexts"]),
            confirmation_contexts=int(config["confirmation_contexts"]),
            extrapolation_contexts=int(config["extrapolation_contexts"]),
        ),
    )
    reference = resample_routing_counts(
        latent,
        np.random.default_rng(reference_seq),
    )
    observed = resample_routing_counts(
        latent,
        np.random.default_rng(observed_seq),
    )
    result = evaluate_density_population(
        latent=latent,
        reference_panel=reference,
        observed_panel=observed,
        primary_rank=int(config["primary_estimator_rank"]),
        oracle_rank=rank,
        neighbor_count=int(config["neighbor_count"]),
        training_indices=np.arange(
            int(config["denoiser_training_authors"])
        ),
        evaluation_indices=np.arange(
            int(config["denoiser_training_authors"]),
            int(config["denoiser_training_authors"])
            + int(condition["authors"]),
        ),
    )
    return {
        **condition,
        "author_rms": author_rms,
        "packing_load": float(
            int(condition["authors"]) ** (1.0 / rank)
        ),
        "seed": seed,
        **result,
    }


def _interval(values: pd.Series) -> tuple[float, float, float]:
    vector = values.to_numpy(dtype=float)
    mean = float(vector.mean())
    if len(vector) < 2:
        return mean, mean, mean
    se = float(vector.std(ddof=1) / np.sqrt(len(vector)))
    return mean, mean - 1.96 * se, mean + 1.96 * se


def _summarize(frame: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    keys = ["signal_regime", "latent_rank", "authors", "event_budget"]
    metrics = [
        "truth_correlation",
        "split_reliability",
        "unseen_context_reliability",
        "local_neighbor_auc",
        "top1",
        "relative_margin",
        "median_raw_combined_error",
        "median_combined_error",
        "median_error_margin_ratio",
        "prototype_margin_fraction",
        "cross_session_certificate_fraction",
        "oracle_rank_truth_correlation",
        "oracle_rank_local_neighbor_auc",
    ]
    rows = []
    for values, group in frame.groupby(keys, sort=True):
        row = dict(zip(keys, values))
        for metric in metrics:
            mean, lower, upper = _interval(group[metric])
            row[f"{metric}_mean"] = mean
            row[f"{metric}_lower95"] = lower
            row[f"{metric}_upper95"] = upper
        recovery = (
            (group["truth_correlation"]
             >= float(config["recovery_truth_threshold"]))
            & (group["split_reliability"]
               >= float(config["recovery_reliability_threshold"]))
        )
        identity = (
            (group["local_neighbor_auc"]
             >= float(config["identity_auc_threshold"]))
            & (group["top1"]
               >= float(config["identity_top1_threshold"]))
        )
        row["recovery_pass_rate"] = float(recovery.mean())
        row["identity_pass_rate"] = float(identity.mean())
        row["n"] = len(group)
        rows.append(row)
    return pd.DataFrame(rows)


def _critical(summary: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    threshold = float(config["cell_pass_rate"])
    rows = []
    keys = ["signal_regime", "latent_rank", "authors"]
    for values, group in summary.groupby(keys, sort=True):
        group = group.sort_values("event_budget")
        recovery = group[group["recovery_pass_rate"] >= threshold]
        identity = group[group["identity_pass_rate"] >= threshold]
        rows.append({
            **dict(zip(keys, values)),
            "minimum_recovery_events": (
                int(recovery.iloc[0]["event_budget"])
                if len(recovery) else None
            ),
            "minimum_identity_events": (
                int(identity.iloc[0]["event_budget"])
                if len(identity) else None
            ),
            "identity_harder_than_recovery": (
                len(recovery) > 0
                and (
                    len(identity) == 0
                    or int(identity.iloc[0]["event_budget"])
                    > int(recovery.iloc[0]["event_budget"])
                )
            ),
        })
    return pd.DataFrame(rows)


def _anchor(
    summary: pd.DataFrame,
    *,
    rank: int,
    authors: int = 96,
    events: int = 128,
) -> pd.Series:
    row = summary[
        (summary["signal_regime"] == "fixed_total_signal")
        & (summary["latent_rank"] == rank)
        & (summary["authors"] == authors)
        & (summary["event_budget"] == events)
    ]
    if len(row) != 1:
        raise RuntimeError("missing registered anchor cell")
    return row.iloc[0]


def _decision(
    summary: pd.DataFrame,
    critical: pd.DataFrame,
    *,
    smoke: bool,
) -> dict[str, Any]:
    rank2 = _anchor(
        summary,
        rank=2,
        authors=96,
        events=64 if smoke else 128,
    )
    rank8 = _anchor(
        summary,
        rank=8,
        authors=96,
        events=64 if smoke else 128,
    )
    rank2_low_density = _anchor(
        summary,
        rank=2,
        authors=32,
        events=64 if smoke else 128,
    )
    checks = {
        "numeric": bool(
            np.isfinite(
                summary.select_dtypes(include=[np.number]).to_numpy()
            ).all()
        ),
        "rank2_recoverable": rank2["recovery_pass_rate"] >= 0.5,
        "rank2_density_effect": (
            rank2_low_density["local_neighbor_auc_mean"]
            - rank2["local_neighbor_auc_mean"]
            >= 0.10
        ),
        "rank2_identity_limited": (
            True if smoke else rank2["identity_pass_rate"] <= 0.5
        ),
        "rank8_recoverable": (
            rank8["truth_correlation_mean"] >= 0.70
            if smoke else rank8["recovery_pass_rate"] >= 0.5
        ),
        "rank8_identity_resolved": (
            rank8["local_neighbor_auc_mean"] >= 0.80
            if smoke else rank8["identity_pass_rate"] >= 0.5
        ),
        "dimension_identity_separation": (
            rank8["local_neighbor_auc_mean"]
            - rank2["local_neighbor_auc_mean"]
            >= 0.10
        ),
        "oracle_rank_does_not_rescue_rank2": abs(
            rank2["oracle_rank_local_neighbor_auc_mean"]
            - rank2["local_neighbor_auc_mean"]
        ) <= 0.05,
        "at_least_one_separated_surface": bool(
            critical["identity_harder_than_recovery"].any()
        ),
    }
    return {
        "status": (
            "V8_DIMENSION_DENSITY_EVENT_BUDGET_V37D_"
            + ("SMOKE_PASS" if smoke else "EXPLORATORY_PASS")
            if all(checks.values())
            else "V8_DIMENSION_DENSITY_EVENT_BUDGET_V37D_"
            + ("SMOKE_STOP" if smoke else "EXPLORATORY_STOP")
        ),
        "checks": {key: bool(value) for key, value in checks.items()},
        "rank2_anchor": rank2.to_dict(),
        "rank2_low_density_anchor": rank2_low_density.to_dict(),
        "rank8_anchor": rank8.to_dict(),
        "claim_boundary": (
            "Smoke behavior only." if smoke else
            "Exploratory synthetic phase diagram; no psychological claim."
        ),
    }


def _report(decision: dict[str, Any], critical: pd.DataFrame) -> str:
    return f"""# V8 Dimension-Density-Event-Budget V3.7D

Decision: `{decision["status"]}`

## Checks

```json
{json.dumps(decision["checks"], indent=2)}
```

## Critical surfaces

{critical.to_markdown(index=False)}

## Boundary

{decision["claim_boundary"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/v8_dimension_density_budget_v37d.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/v8_dimension_density_budget/v37d",
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    config = _read(args.config)
    if args.smoke:
        config = json.loads(json.dumps(config))
        config["jobs"] = 1
        config["repetitions"] = 2
        config["latent_ranks"] = [2, 8]
        config["author_counts"] = [32, 96]
        config["event_budgets"] = [16, 64]

    conditions = [
        {
            "signal_regime": regime,
            "latent_rank": rank,
            "authors": authors,
            "event_budget": budget,
            "repetition": repetition,
        }
        for regime, rank, authors, budget, repetition in product(
            config["signal_regimes"],
            config["latent_ranks"],
            config["author_counts"],
            config["event_budgets"],
            range(int(config["repetitions"])),
        )
    ]
    children = np.random.SeedSequence(int(config["seed"])).spawn(
        len(conditions)
    )
    payloads = [
        (
            config,
            condition,
            int(child.generate_state(1, dtype=np.uint64)[0]),
        )
        for condition, child in zip(conditions, children)
    ]
    if int(config["jobs"]) == 1:
        rows = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(
            max_workers=int(config["jobs"])
        ) as executor:
            rows = list(executor.map(_worker, payloads, chunksize=1))
    metrics = pd.DataFrame(rows)
    summary = _summarize(metrics, config)
    critical = _critical(summary, config)
    decision = _decision(summary, critical, smoke=args.smoke)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.output_dir / "cell_metrics.csv", index=False)
    summary.to_csv(args.output_dir / "phase_summary.csv", index=False)
    critical.to_csv(args.output_dir / "critical_surfaces.csv", index=False)
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    (args.output_dir / "report.md").write_text(
        _report(decision, critical),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[
            ROOT / "configs/v8_group_free_routing_transport_v37c_seal.json",
        ],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v8_dimension_density_budget.py",
            Path(__file__),
        ],
        estimand_id=str(config["estimand_id"]),
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps({
        "status": decision["status"],
        "conditions": len(conditions),
        "checks": decision["checks"],
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
