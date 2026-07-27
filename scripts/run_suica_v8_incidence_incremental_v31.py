#!/usr/bin/env python3
"""Run the SUICA V8 V3.1 condition-aligned persistent-core battery."""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import run_suica_v8_incidence_incremental as base  # noqa: E402
from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_incidence_incremental import (  # noqa: E402
    simulate_counterfactual_pair,
    simulate_null_population,
)
from suica_core.v8_incidence_incremental_v31 import (  # noqa: E402
    analyze_counterfactual_pair_v31,
    analyze_incidence_population_v31,
)

CAP_STATUSES = {
    "REFUSE_ENUMERATION_CAP",
    "REFUSE_CANDIDATE_CLOSURE_CAP",
}
LOCAL_METRICS = (
    "minimum_same_condition_auc",
    "soft_local_kernel_auc",
    "neighbor_recurrence_auc",
)


def _worker_v31(
    payload: tuple[
        dict[str, Any],
        str,
        str,
        int,
        int,
        str,
    ],
) -> dict[str, Any]:
    config, stage, name, index, repetition, kind = payload
    seed = base._seed(  # noqa: SLF001
        config,
        stage=stage,
        index=index,
        repetition=repetition,
    )
    spec = base._spec(config)  # noqa: SLF001
    closure_cap = int(config["candidate_closure_cap"])
    if kind == "pair":
        pair = simulate_counterfactual_pair(
            seed=seed,
            pair_id=name,
            spec=spec,
        )
        result = analyze_counterfactual_pair_v31(
            pair,
            spec=spec,
            candidate_closure_cap=closure_cap,
            permutation_seed=seed + 9_000_001,
        )
    else:
        population = simulate_null_population(
            seed=seed,
            world=name,
            spec=spec,
        )
        estimate = analyze_incidence_population_v31(
            population["views"],
            population["labels"],
            spec=spec,
            candidate_closure_cap=closure_cap,
        )
        if estimate["status"] in CAP_STATUSES:
            permutation_auc = float("nan")
            status = estimate["status"]
        else:
            permutation = np.random.default_rng(
                seed + 9_000_001
            ).permutation(population["labels"])
            upper = np.triu_indices(spec.authors, 1)
            permutation_truth = (
                permutation[upper[0]] == permutation[upper[1]]
            ).astype(int)
            permutation_auc = float(roc_auc_score(
                permutation_truth,
                np.asarray(estimate["pair_scores"]),
            ))
            status = "ESTIMATE_READY"
        result = {
            "status": status,
            "world": name,
            "estimate": estimate,
            "permutation_auc": permutation_auc,
        }
    return {
        "stage": stage,
        "kind": kind,
        "name": name,
        "seed": seed,
        "repetition": repetition,
        **result,
    }


def _run_stage_v31(
    config: dict[str, Any],
    *,
    stage: str,
    repetitions: int,
) -> list[dict[str, Any]]:
    entries = [
        *[
            (pair_id, "pair")
            for pair_id in config["counterfactual_pairs"]
        ],
        *[
            (world, "null")
            for world in config["null_worlds"]
        ],
    ]
    payloads = [
        (
            config,
            stage,
            name,
            index,
            repetition,
            kind,
        )
        for index, (name, kind) in enumerate(entries)
        for repetition in range(repetitions)
    ]
    jobs = int(config["jobs"])
    if jobs <= 1:
        return [_worker_v31(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=jobs) as executor:
        return list(executor.map(
            _worker_v31,
            payloads,
            chunksize=1,
        ))


def _pair_row_v31(row: dict[str, Any]) -> dict[str, Any]:
    output = {
        "stage": row["stage"],
        "kind": row["kind"],
        "pair_id": row.get("pair_id", row["name"]),
        "positive_world": row.get("positive_world"),
        "negative_world": row.get("negative_world"),
        "seed": row["seed"],
        "repetition": row["repetition"],
        "status": row["status"],
        "oracle_distance_relative_error": row.get(
            "oracle_distance_relative_error",
            float("nan"),
        ),
        "fitted_distance_relative_error": row.get(
            "fitted_distance_relative_error",
            float("nan"),
        ),
        "orthogonal_mapping_error": row.get(
            "orthogonal_mapping_error",
            float("nan"),
        ),
        "incremental_auc": row.get("incremental_auc", float("nan")),
        "permutation_auc": row.get("permutation_auc", float("nan")),
        "chaining_error": row.get("chaining_error", False),
    }
    scalar_keys = [
        "status",
        "refused",
        "group_claim",
        "coverage",
        "candidate_core_count",
        "incidence_auc",
        "whole_map_auc",
        *LOCAL_METRICS,
        "group_f1",
        "group_ari",
        "cross_view_core_jaccard",
        "enumeration_nodes",
        "exact_hyperedge_sets",
        "approximate_hyperedge_sets",
        "approximate_precision",
        "approximate_recall",
    ]
    for side in ("positive", "negative"):
        estimate = row.get(side, {})
        for key in scalar_keys:
            output[f"{side}_{key}"] = estimate.get(key)
        output[f"{side}_selected_cores"] = json.dumps(
            estimate.get("selected_cores", []),
            separators=(",", ":"),
        )
    return output


def _null_row_v31(row: dict[str, Any]) -> dict[str, Any]:
    estimate = row["estimate"]
    output = {
        "stage": row["stage"],
        "kind": row["kind"],
        "world": row["world"],
        "seed": row["seed"],
        "repetition": row["repetition"],
        "status": row["status"],
        "permutation_auc": row["permutation_auc"],
    }
    scalar_keys = [
        "status",
        "refused",
        "group_claim",
        "coverage",
        "candidate_core_count",
        "incidence_auc",
        "whole_map_auc",
        *LOCAL_METRICS,
        "group_f1",
        "group_ari",
        "cross_view_core_jaccard",
        "enumeration_nodes",
        "exact_hyperedge_sets",
        "approximate_hyperedge_sets",
        "approximate_precision",
        "approximate_recall",
    ]
    for key in scalar_keys:
        output[f"estimate_{key}"] = estimate.get(key)
    output["selected_cores"] = json.dumps(
        estimate.get("selected_cores", []),
        separators=(",", ":"),
    )
    return output


def _frames_v31(
    rows: list[dict[str, Any]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pairs = pd.DataFrame([
        _pair_row_v31(row) for row in rows
        if row["kind"] == "pair"
    ])
    nulls = pd.DataFrame([
        _null_row_v31(row) for row in rows
        if row["kind"] == "null"
    ])
    return pairs, nulls


def _local_baseline_summary(frame: pd.DataFrame) -> pd.DataFrame:
    output: list[dict[str, Any]] = []
    for pair_id, group in frame.groupby("pair_id", sort=True):
        row: dict[str, Any] = {
            "pair_id": pair_id,
            "repetitions": len(group),
        }
        for side in ("positive", "negative"):
            for metric in LOCAL_METRICS:
                values = pd.to_numeric(
                    group[f"{side}_{metric}"],
                    errors="coerce",
                )
                row[f"{side}_{metric}_median"] = float(values.median())
                row[f"{side}_{metric}_mean"] = float(values.mean())
        output.append(row)
    return pd.DataFrame(output)


def _report_v31(
    decision: dict[str, Any],
    pair_summary: pd.DataFrame,
    null_summary: pd.DataFrame,
    local_summary: pd.DataFrame,
) -> str:
    return f"""# V8 Incremental Incidence V3.1

## Decision

`{decision["status"]}`

V3.1 adds intersection-closed persistent subsets and requires support at the
same condition/radius cell across all views. The exact-core estimator is
compared with three simpler condition-local statistics; no uniqueness claim
is made.

## Counterfactual pairs

{pair_summary.to_markdown(index=False)}

## Simpler local baselines

{local_summary.to_markdown(index=False)}

## Nulls

{null_summary.to_markdown(index=False)}

## Gates

```json
{json.dumps(decision["checks"], indent=2)}
```

## Claim boundary

{decision.get("claim_boundary", "Smoke behavior only.")}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/v8_incidence_incremental_v31.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=(
            ROOT / "results/v8_incidence_incremental/v31"
        ),
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    config = base._read_json(args.config)  # noqa: SLF001
    if args.smoke:
        config = json.loads(json.dumps(config))
        config["jobs"] = 1
        config["discovery_repetitions"] = 1
        config["confirmation_repetitions"] = 3
    args.output_dir.mkdir(parents=True, exist_ok=True)

    discovery = _run_stage_v31(
        config,
        stage="discovery",
        repetitions=int(config["discovery_repetitions"]),
    )
    confirmation = _run_stage_v31(
        config,
        stage="confirmation",
        repetitions=int(config["confirmation_repetitions"]),
    )
    discovery_pairs, discovery_nulls = _frames_v31(discovery)
    pairs, nulls = _frames_v31(confirmation)
    decision = base._decision(  # noqa: SLF001
        pairs,
        nulls,
        config,
        smoke=args.smoke,
    )
    pair_summary = base._pair_summary(  # noqa: SLF001
        pairs,
        seed=int(config["seed"]) + 70_001,
    )
    null_summary = base._null_summary(nulls)  # noqa: SLF001
    local_summary = _local_baseline_summary(pairs)

    discovery_pairs.to_csv(
        args.output_dir / "discovery_pair_metrics.csv",
        index=False,
    )
    discovery_nulls.to_csv(
        args.output_dir / "discovery_null_metrics.csv",
        index=False,
    )
    pairs.to_csv(
        args.output_dir / "confirmation_pair_metrics.csv",
        index=False,
    )
    nulls.to_csv(
        args.output_dir / "confirmation_null_metrics.csv",
        index=False,
    )
    pair_summary.to_csv(
        args.output_dir / "pair_summary.csv",
        index=False,
    )
    null_summary.to_csv(
        args.output_dir / "null_summary.csv",
        index=False,
    )
    local_summary.to_csv(
        args.output_dir / "local_baseline_summary.csv",
        index=False,
    )
    base._write_json(  # noqa: SLF001
        args.output_dir / "decision.json",
        decision,
    )
    base._write_json(  # noqa: SLF001
        args.output_dir / "config_effective.json",
        config,
    )
    (args.output_dir / "report.md").write_text(
        _report_v31(
            decision,
            pair_summary,
            null_summary,
            local_summary,
        ),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v8_incidence_incremental.py",
            ROOT / "suica_core/v8_incidence_incremental_v31.py",
            ROOT / "scripts/run_suica_v8_incidence_incremental.py",
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
        "output_dir": str(args.output_dir),
        "checks": decision["checks"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
