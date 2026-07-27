#!/usr/bin/env python3
"""Run the SUICA V8 distance-matched incremental-incidence battery."""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import beta
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_incidence_incremental import (  # noqa: E402
    IncrementalSpec,
    analyze_counterfactual_pair,
    analyze_incidence_population,
    simulate_counterfactual_pair,
    simulate_null_population,
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _spec(config: dict[str, Any]) -> IncrementalSpec:
    return IncrementalSpec(
        authors=int(config["authors"]),
        groups=int(config["groups"]),
        conditions=int(config["conditions"]),
        halves=int(config["halves"]),
        observers=int(config["observers"]),
        ambient=int(config["ambient"]),
        event_width=int(config["event_width"]),
        noise_sd=float(config["noise_sd"]),
        epsilon_grid=tuple(
            float(item) for item in config["epsilon_grid"]
        ),
        core_persistence_threshold=float(
            config["core_persistence_threshold"]
        ),
        minimum_group_coverage=float(
            config["minimum_group_coverage"]
        ),
        enumeration_node_cap=int(
            config["enumeration_node_cap"]
        ),
    )


def _seed(
    config: dict[str, Any],
    *,
    stage: str,
    index: int,
    repetition: int,
) -> int:
    offset = {
        "discovery": 0,
        "confirmation": 20_000_000,
    }[stage]
    return (
        int(config["seed"])
        + offset
        + 100_000 * index
        + repetition
    )


def _worker(
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
    seed = _seed(
        config,
        stage=stage,
        index=index,
        repetition=repetition,
    )
    spec = _spec(config)
    if kind == "pair":
        pair = simulate_counterfactual_pair(
            seed=seed,
            pair_id=name,
            spec=spec,
        )
        result = analyze_counterfactual_pair(
            pair,
            spec=spec,
            permutation_seed=seed + 9_000_001,
        )
    else:
        population = simulate_null_population(
            seed=seed,
            world=name,
            spec=spec,
        )
        estimate = analyze_incidence_population(
            population["views"],
            population["labels"],
            spec=spec,
        )
        permutation = np.random.default_rng(
            seed + 9_000_001
        ).permutation(population["labels"])
        upper = np.triu_indices(spec.authors, 1)
        permutation_truth = (
            permutation[upper[0]] == permutation[upper[1]]
        ).astype(int)
        permutation_auc = (
            float(roc_auc_score(
                permutation_truth,
                np.asarray(estimate["pair_scores"]),
            ))
            if estimate["status"] != "REFUSE_ENUMERATION_CAP"
            else float("nan")
        )
        result = {
            "status": (
                "ESTIMATE_READY"
                if estimate["status"] != "REFUSE_ENUMERATION_CAP"
                else "REFUSE_ENUMERATION_CAP"
            ),
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


def _run_stage(
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
        return [_worker(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=jobs) as executor:
        return list(executor.map(_worker, payloads, chunksize=1))


def _pair_row(row: dict[str, Any]) -> dict[str, Any]:
    output = {
        "stage": row["stage"],
        "kind": row["kind"],
        "pair_id": row["pair_id"],
        "positive_world": row["positive_world"],
        "negative_world": row["negative_world"],
        "seed": row["seed"],
        "repetition": row["repetition"],
        "status": row["status"],
        "oracle_distance_relative_error": row[
            "oracle_distance_relative_error"
        ],
        "fitted_distance_relative_error": row[
            "fitted_distance_relative_error"
        ],
        "orthogonal_mapping_error": row[
            "orthogonal_mapping_error"
        ],
        "incremental_auc": row["incremental_auc"],
        "permutation_auc": row["permutation_auc"],
        "chaining_error": row["chaining_error"],
    }
    scalar_keys = [
        "status",
        "refused",
        "group_claim",
        "coverage",
        "candidate_core_count",
        "incidence_auc",
        "whole_map_auc",
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
        estimate = row[side]
        for key in scalar_keys:
            output[f"{side}_{key}"] = estimate.get(key)
        output[f"{side}_selected_cores"] = json.dumps(
            estimate.get("selected_cores", []),
            separators=(",", ":"),
        )
    return output


def _null_row(row: dict[str, Any]) -> dict[str, Any]:
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
    for key in [
        "status",
        "refused",
        "group_claim",
        "coverage",
        "candidate_core_count",
        "incidence_auc",
        "whole_map_auc",
        "group_f1",
        "group_ari",
        "cross_view_core_jaccard",
        "enumeration_nodes",
        "exact_hyperedge_sets",
        "approximate_hyperedge_sets",
        "approximate_precision",
        "approximate_recall",
    ]:
        output[f"estimate_{key}"] = estimate.get(key)
    output["selected_cores"] = json.dumps(
        estimate.get("selected_cores", []),
        separators=(",", ":"),
    )
    return output


def _frames(
    rows: list[dict[str, Any]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pairs = pd.DataFrame([
        _pair_row(row) for row in rows
        if row["kind"] == "pair"
    ])
    nulls = pd.DataFrame([
        _null_row(row) for row in rows
        if row["kind"] == "null"
    ])
    return pairs, nulls


def _bootstrap_mean_interval(
    values: np.ndarray,
    *,
    seed: int,
    confidence: float = 0.90,
    repetitions: int = 5_000,
) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if not len(values):
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    draws = rng.integers(
        0,
        len(values),
        size=(repetitions, len(values)),
    )
    means = values[draws].mean(axis=1)
    alpha = (1.0 - confidence) / 2.0
    return (
        float(np.quantile(means, alpha)),
        float(np.quantile(means, 1.0 - alpha)),
    )


def _one_sided_upper(successes: int, trials: int) -> float:
    if trials <= 0 or successes >= trials:
        return 1.0
    return float(beta.ppf(
        0.95,
        successes + 1,
        trials - successes,
    ))


def _one_sided_lower(successes: int, trials: int) -> float:
    if trials <= 0 or successes <= 0:
        return 0.0
    return float(beta.ppf(
        0.05,
        successes,
        trials - successes + 1,
    ))


def _pair_summary(
    frame: pd.DataFrame,
    *,
    seed: int,
) -> pd.DataFrame:
    output = []
    for index, (pair_id, group) in enumerate(
        frame.groupby("pair_id", sort=True)
    ):
        whole_low, whole_high = _bootstrap_mean_interval(
            group["positive_whole_map_auc"].to_numpy(),
            seed=seed + 100 * index,
        )
        permutation_low, permutation_high = (
            _bootstrap_mean_interval(
                group["permutation_auc"].to_numpy(),
                seed=seed + 100 * index + 1,
            )
        )
        positive_claims = int(
            group["positive_group_claim"].sum()
        )
        negative_claims = int(
            group["negative_group_claim"].sum()
        )
        chaining = int(group["chaining_error"].sum())
        output.append({
            "pair_id": pair_id,
            "repetitions": len(group),
            "oracle_distance_error_max": float(
                group["oracle_distance_relative_error"].max()
            ),
            "fitted_distance_error_max": float(
                group["fitted_distance_relative_error"].max()
            ),
            "whole_map_auc_mean": float(
                group["positive_whole_map_auc"].mean()
            ),
            "whole_map_auc_ci90_low": whole_low,
            "whole_map_auc_ci90_high": whole_high,
            "incidence_auc_median": float(
                group["positive_incidence_auc"].median()
            ),
            "incremental_auc_median": float(
                group["incremental_auc"].median()
            ),
            "group_f1_median": float(
                group["positive_group_f1"].median()
            ),
            "group_ari_median": float(
                group["positive_group_ari"].median()
            ),
            "positive_claim_rate": (
                positive_claims / len(group)
            ),
            "positive_claim_lower95": _one_sided_lower(
                positive_claims,
                len(group),
            ),
            "negative_claim_rate": (
                negative_claims / len(group)
            ),
            "negative_claim_upper95": _one_sided_upper(
                negative_claims,
                len(group),
            ),
            "chaining_error_rate": chaining / len(group),
            "chaining_error_upper95": _one_sided_upper(
                chaining,
                len(group),
            ),
            "cross_view_jaccard_median": float(
                group[
                    "positive_cross_view_core_jaccard"
                ].median()
            ),
            "permutation_auc_mean": float(
                group["permutation_auc"].mean()
            ),
            "permutation_auc_ci90_low": permutation_low,
            "permutation_auc_ci90_high": permutation_high,
            "approximate_precision_median": float(
                group["positive_approximate_precision"].median()
            ),
            "approximate_recall_median": float(
                group["positive_approximate_recall"].median()
            ),
        })
    return pd.DataFrame(output)


def _null_summary(frame: pd.DataFrame) -> pd.DataFrame:
    output = []
    for world, group in frame.groupby("world", sort=True):
        claims = int(group["estimate_group_claim"].sum())
        output.append({
            "world": world,
            "repetitions": len(group),
            "claim_rate": claims / len(group),
            "claim_upper95": _one_sided_upper(
                claims,
                len(group),
            ),
            "incidence_auc_median": float(
                group["estimate_incidence_auc"].median()
            ),
            "whole_map_auc_median": float(
                group["estimate_whole_map_auc"].median()
            ),
            "refusal_rate": float(
                group["estimate_refused"].mean()
            ),
        })
    return pd.DataFrame(output)


def _decision(
    pairs: pd.DataFrame,
    nulls: pd.DataFrame,
    config: dict[str, Any],
    *,
    smoke: bool,
) -> dict[str, Any]:
    gates = config["gates"]
    statuses_ready = bool(
        pairs["status"].eq("ESTIMATE_READY").all()
        and nulls["status"].eq("ESTIMATE_READY").all()
    )
    if smoke:
        checks = {
            "enumeration_ready": statuses_ready,
            "distance_matched": bool(
                pairs["oracle_distance_relative_error"].max()
                <= gates["maximum_oracle_distance_relative_error"]
                and pairs["fitted_distance_relative_error"].max()
                <= gates["maximum_fitted_distance_relative_error"]
            ),
            "positive_recovery": bool(
                pairs["positive_incidence_auc"].min()
                >= gates["minimum_incidence_auc"]
                and pairs["positive_group_f1"].min()
                >= gates["minimum_group_f1"]
                and pairs["positive_group_ari"].min()
                >= gates["minimum_group_ari"]
                and pairs["positive_group_claim"].all()
            ),
            "counterfactual_rejection": bool(
                ~pairs["negative_group_claim"].any()
                and ~pairs["chaining_error"].any()
                and ~nulls["estimate_group_claim"].any()
            ),
            "cross_view_recovery": bool(
                pairs["positive_cross_view_core_jaccard"].min()
                >= gates["minimum_cross_view_core_jaccard"]
            ),
        }
        status = (
            "V8_INCIDENCE_INCREMENTAL_SMOKE_PASS"
            if all(checks.values())
            else "V8_INCIDENCE_INCREMENTAL_SMOKE_STOP"
        )
        return {"status": status, "checks": checks}

    pair_summary = _pair_summary(
        pairs,
        seed=int(config["seed"]) + 70_001,
    )
    null_summary = _null_summary(nulls)
    checks = {
        "enumeration_ready": statuses_ready,
        "oracle_distance_matched": bool(
            pair_summary["oracle_distance_error_max"].max()
            <= gates["maximum_oracle_distance_relative_error"]
        ),
        "fitted_distance_matched": bool(
            pair_summary["fitted_distance_error_max"].max()
            <= gates["maximum_fitted_distance_relative_error"]
        ),
        "whole_map_equivalence": bool(
            pair_summary["whole_map_auc_ci90_low"].min()
            >= gates["minimum_distance_auc_equivalence"]
            and pair_summary["whole_map_auc_ci90_high"].max()
            <= gates["maximum_distance_auc_equivalence"]
        ),
        "incidence_auc": bool(
            pair_summary["incidence_auc_median"].min()
            >= gates["minimum_incidence_auc"]
        ),
        "incremental_auc": bool(
            pair_summary["incremental_auc_median"].min()
            >= gates["minimum_incremental_auc"]
        ),
        "group_f1": bool(
            pair_summary["group_f1_median"].min()
            >= gates["minimum_group_f1"]
        ),
        "group_ari": bool(
            pair_summary["group_ari_median"].min()
            >= gates["minimum_group_ari"]
        ),
        "positive_claim": bool(
            pair_summary["positive_claim_lower95"].min()
            >= gates["minimum_group_claim_rate"]
        ),
        "cross_view_core": bool(
            pair_summary["cross_view_jaccard_median"].min()
            >= gates["minimum_cross_view_core_jaccard"]
        ),
        "counterfactual_claim": bool(
            pair_summary["negative_claim_upper95"].max()
            <= gates["maximum_counterfactual_claim_rate"]
        ),
        "chaining_control": bool(
            pair_summary.loc[
                pair_summary["pair_id"].eq("CF2"),
                "chaining_error_upper95",
            ].max()
            <= gates["maximum_chaining_error_rate"]
        ),
        "null_claim": bool(
            null_summary["claim_upper95"].max()
            <= gates["maximum_counterfactual_claim_rate"]
        ),
        "permutation_equivalence": bool(
            pair_summary["permutation_auc_ci90_low"].min()
            >= gates["minimum_permutation_auc_equivalence"]
            and pair_summary["permutation_auc_ci90_high"].max()
            <= gates["maximum_permutation_auc_equivalence"]
        ),
    }
    if all(checks.values()):
        status = "V8_INCIDENCE_INCREMENTAL_PLANTED_PASS"
    elif (
        checks["counterfactual_claim"]
        and checks["chaining_control"]
        and checks["null_claim"]
    ):
        status = "V8_INCIDENCE_INCREMENTAL_PARTIAL"
    else:
        status = "V8_INCIDENCE_INCREMENTAL_STOP"
    return {
        "status": status,
        "checks": checks,
        "pair_summary": pair_summary.to_dict(orient="records"),
        "null_summary": null_summary.to_dict(orient="records"),
        "claim_boundary": config["claim_boundary"],
    }


def _report(
    decision: dict[str, Any],
    pair_summary: pd.DataFrame,
    null_summary: pd.DataFrame,
) -> str:
    return f"""# V8 Incremental Incidence V3

## Decision

`{decision["status"]}`

## Counterfactual pairs

{pair_summary.to_markdown(index=False)}

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
        default=ROOT / "configs/v8_incidence_incremental_v3.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/v8_incidence_incremental/v3",
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    config = _read_json(args.config)
    if args.smoke:
        config = json.loads(json.dumps(config))
        config["jobs"] = 1
        config["discovery_repetitions"] = 1
        config["confirmation_repetitions"] = 3
    args.output_dir.mkdir(parents=True, exist_ok=True)

    discovery = _run_stage(
        config,
        stage="discovery",
        repetitions=int(config["discovery_repetitions"]),
    )
    confirmation = _run_stage(
        config,
        stage="confirmation",
        repetitions=int(config["confirmation_repetitions"]),
    )
    discovery_pairs, discovery_nulls = _frames(discovery)
    pairs, nulls = _frames(confirmation)
    decision = _decision(
        pairs,
        nulls,
        config,
        smoke=args.smoke,
    )
    pair_summary = _pair_summary(
        pairs,
        seed=int(config["seed"]) + 70_001,
    )
    null_summary = _null_summary(nulls)

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
    _write_json(args.output_dir / "decision.json", decision)
    _write_json(args.output_dir / "config_effective.json", config)
    (args.output_dir / "report.md").write_text(
        _report(decision, pair_summary, null_summary),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v8_incidence_incremental.py",
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
