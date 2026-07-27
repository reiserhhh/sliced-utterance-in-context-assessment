#!/usr/bin/env python3
"""Run the SUICA V8 vanishing-individuality planted-world battery."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import beta, linregress

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_vanishing_individuality import (  # noqa: E402
    VanishingIndividualitySpec,
    analyze_hierarchical_world,
    simulate_hierarchical_c2_world,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_vanishing_individuality.json"
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_vanishing_individuality"
    / "v1_20260725"
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _cases(config: dict[str, Any]) -> list[dict[str, Any]]:
    group = float(config["group_amplitude"])
    individual = float(config["individual_amplitude"])
    cases = [
        {"case_id": "W0_null", "world": "null", "epsilon": 0.0, "group": 0.0},
        {
            "case_id": "W1_group_only",
            "world": "group_only",
            "epsilon": 0.0,
            "group": group,
        },
        {
            "case_id": "W2_individual_only",
            "world": "individual_only",
            "epsilon": individual,
            "group": 0.0,
        },
        {
            "case_id": "W3_joint",
            "world": "joint",
            "epsilon": individual,
            "group": group,
        },
    ]
    cases.extend({
        "case_id": f"W4_epsilon_{float(epsilon):0.2f}",
        "world": "epsilon_ladder",
        "epsilon": float(epsilon),
        "group": group,
    } for epsilon in config["epsilon_ladder"])
    cases.extend([
        {
            "case_id": "W5_continuous_manifold",
            "world": "continuous_manifold",
            "epsilon": 0.0,
            "group": 0.0,
        },
        {
            "case_id": "W6_c1_group_confound",
            "world": "c1_group_confound",
            "epsilon": 0.0,
            "group": 0.0,
        },
        {
            "case_id": "W7_observer_artifact",
            "world": "observer_artifact",
            "epsilon": individual,
            "group": 0.0,
        },
        {
            "case_id": "W8_half_unstable",
            "world": "half_unstable",
            "epsilon": individual,
            "group": 0.0,
        },
    ])
    return cases


def _run_repetition(
    payload: tuple[
        int,
        dict[str, Any],
        VanishingIndividualitySpec,
        list[dict[str, Any]],
    ],
) -> list[dict[str, Any]]:
    repetition, config, spec, cases = payload
    rows = []
    for case_index, case in enumerate(cases):
        seed = (
            int(config["seed"])
            + repetition * 1_000_003
            + case_index * 10_007
        )
        world = simulate_hierarchical_c2_world(
            seed=seed,
            world=str(case["world"]),
            epsilon=float(case["epsilon"]),
            group_amplitude=float(case["group"]),
            spec=spec,
        )
        audit_world = None
        if case["world"] == "observer_artifact":
            audit_world = simulate_hierarchical_c2_world(
                seed=seed + 700_001,
                world="observer_artifact",
                epsilon=float(case["epsilon"]),
                group_amplitude=0.0,
                spec=spec,
            )
        result = analyze_hierarchical_world(
            world,
            seed=seed + 300_001,
            ridge_candidates=tuple(
                map(float, config["ridge_candidates"])
            ),
            permutations=int(config["permutations"]),
            audit_world=audit_world,
        )
        rows.append({
            "case_id": str(case["case_id"]),
            "world": str(case["world"]),
            "epsilon": float(case["epsilon"]),
            "group_amplitude": float(case["group"]),
            "repetition": repetition,
            "seed": seed,
            **result,
        })
    return rows


def _summary(seed_metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    metrics = [
        "author_all_auc",
        "author_within_group_auc",
        "group_auc",
        "within_pairing_statistic",
        "c1_group_auc",
        "confirmation_cluster_ari",
        "group_distance_spearman",
        "estimated_residual_energy",
        "estimated_positive_spectral_energy",
        "estimated_residual_effective_rank",
        "oracle_residual_energy",
        "residual_covariance_aligned_error",
        "mixture_components",
        "mixture_nmse",
        "manifold_neighbors",
        "manifold_nmse",
        "manifold_advantage",
        "continuous_distance_spearman",
        "cross_observer_within_auc",
    ]
    for keys, group in seed_metrics.groupby(
        ["case_id", "world", "epsilon", "group_amplitude"],
        observed=True,
        sort=False,
    ):
        ready = group["numeric_output"].fillna(False).astype(bool)
        values = group.loc[ready]
        row = dict(zip(
            ["case_id", "world", "epsilon", "group_amplitude"],
            keys,
            strict=True,
        ))
        row["repetitions"] = int(len(group))
        row["numeric_output_rate"] = float(ready.mean())
        for metric in metrics:
            row[f"mean_{metric}"] = (
                float(values[metric].mean())
                if len(values) and metric in values
                else float("nan")
            )
            row[f"median_{metric}"] = (
                float(values[metric].median())
                if len(values) and metric in values
                else float("nan")
            )
        p_values = values["within_group_pairing_p"].dropna()
        rejected = int(p_values.le(0.01).sum())
        row["within_pairing_rejection_rate"] = (
            float(rejected / len(p_values))
            if len(p_values)
            else float("nan")
        )
        row["within_pairing_rejection_upper_95"] = (
            float(beta.ppf(
                0.95,
                rejected + 1,
                len(p_values) - rejected,
            ))
            if len(p_values) and rejected < len(p_values)
            else 1.0
        )
        for metric in (
            "author_all_auc",
            "author_within_group_auc",
            "group_auc",
            "c1_group_auc",
            "cross_observer_within_auc",
        ):
            data = values[metric].dropna()
            if len(data) > 1:
                standard_error = float(data.std(ddof=1) / np.sqrt(len(data)))
                row[f"{metric}_ci_lower"] = float(
                    data.mean() - 1.96 * standard_error
                )
                row[f"{metric}_ci_upper"] = float(
                    data.mean() + 1.96 * standard_error
                )
            else:
                row[f"{metric}_ci_lower"] = float("nan")
                row[f"{metric}_ci_upper"] = float("nan")
        rows.append(row)
    return pd.DataFrame(rows)


def _row(summary: pd.DataFrame, case_id: str) -> pd.Series:
    selected = summary.loc[summary["case_id"].eq(case_id)]
    if len(selected) != 1:
        raise RuntimeError(f"expected one summary row for {case_id}")
    return selected.iloc[0]


def _chance(value: float, gates: dict[str, Any]) -> bool:
    return bool(
        float(gates["minimum_chance_auc"])
        <= value
        <= float(gates["maximum_chance_auc"])
    )


def _positive(
    row: pd.Series,
    metric: str,
    gates: dict[str, Any],
) -> bool:
    return bool(
        row[f"mean_{metric}"] >= float(gates["minimum_positive_auc"])
        and row[f"{metric}_ci_lower"]
        > float(gates["minimum_positive_ci_lower"])
    )


def _scaling(summary: pd.DataFrame) -> dict[str, float]:
    ladder = summary.loc[
        summary["world"].eq("epsilon_ladder")
        & summary["epsilon"].ge(0.10)
    ].sort_values("epsilon")

    def fit(column: str) -> tuple[float, float]:
        selected = ladder.loc[ladder[column].gt(0)]
        result = linregress(
            np.log(selected["epsilon"].to_numpy(dtype=float)),
            np.log(selected[column].to_numpy(dtype=float)),
        )
        return float(result.slope), float(result.rvalue**2)

    estimated_slope, estimated_r2 = fit(
        "mean_estimated_residual_energy"
    )
    oracle_slope, oracle_r2 = fit("mean_oracle_residual_energy")
    detectable = float("nan")
    for row in ladder.itertuples(index=False):
        if (
            row.mean_author_within_group_auc >= 0.65
            and row.within_pairing_rejection_rate >= 0.80
        ):
            detectable = float(row.epsilon)
            break
    return {
        "estimated_slope": estimated_slope,
        "estimated_r2": estimated_r2,
        "oracle_slope": oracle_slope,
        "oracle_r2": oracle_r2,
        "minimum_detectable_epsilon": detectable,
    }


def _decision(
    summary: pd.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    gates = config["gates"]
    w0 = _row(summary, "W0_null")
    w1 = _row(summary, "W1_group_only")
    w2 = _row(summary, "W2_individual_only")
    w3 = _row(summary, "W3_joint")
    w4_zero = _row(summary, "W4_epsilon_0.00")
    w5 = _row(summary, "W5_continuous_manifold")
    w6 = _row(summary, "W6_c1_group_confound")
    w7 = _row(summary, "W7_observer_artifact")
    w8 = _row(summary, "W8_half_unstable")
    scaling = _scaling(summary)
    null_upper = float(gates["maximum_null_fpr_upper_95"])
    core = {
        "w0_author_all_chance": _chance(
            w0["mean_author_all_auc"], gates
        ),
        "w0_author_within_chance": _chance(
            w0["mean_author_within_group_auc"], gates
        ),
        "w0_group_chance": _chance(w0["mean_group_auc"], gates),
        "w0_within_type1": bool(
            w0["within_pairing_rejection_upper_95"] <= null_upper
        ),
        "w1_author_all_positive": _positive(
            w1, "author_all_auc", gates
        ),
        "w1_group_positive": _positive(w1, "group_auc", gates),
        "w1_author_within_chance": _chance(
            w1["mean_author_within_group_auc"], gates
        ),
        "w1_within_type1": bool(
            w1["within_pairing_rejection_upper_95"] <= null_upper
        ),
        "w2_author_all_positive": _positive(
            w2, "author_all_auc", gates
        ),
        "w2_author_within_positive": _positive(
            w2, "author_within_group_auc", gates
        ),
        "w2_group_chance": _chance(w2["mean_group_auc"], gates),
        "w2_all_within_agreement": bool(
            abs(
                w2["mean_author_all_auc"]
                - w2["mean_author_within_group_auc"]
            )
            <= float(gates["maximum_individual_all_within_gap"])
        ),
        "w3_author_within_positive": _positive(
            w3, "author_within_group_auc", gates
        ),
        "w3_group_positive": _positive(w3, "group_auc", gates),
        "w4_zero_author_within_chance": _chance(
            w4_zero["mean_author_within_group_auc"], gates
        ),
        "w4_zero_within_type1": bool(
            w4_zero["within_pairing_rejection_upper_95"] <= null_upper
        ),
        "w6_c1_group_positive": _positive(w6, "c1_group_auc", gates),
        "w6_c2_author_chance": _chance(
            w6["mean_author_all_auc"], gates
        ),
        "w6_c2_within_chance": _chance(
            w6["mean_author_within_group_auc"], gates
        ),
        "w6_c2_group_chance": _chance(w6["mean_group_auc"], gates),
        "w7_primary_author_within_positive": _positive(
            w7, "author_within_group_auc", gates
        ),
        "w7_cross_observer_chance": _chance(
            w7["mean_cross_observer_within_auc"], gates
        ),
        "w8_author_within_chance": _chance(
            w8["mean_author_within_group_auc"], gates
        ),
        "w8_within_type1": bool(
            w8["within_pairing_rejection_upper_95"] <= null_upper
        ),
        "epsilon_estimated_quadratic": bool(
            float(gates["minimum_scaling_slope"])
            <= scaling["estimated_slope"]
            <= float(gates["maximum_scaling_slope"])
            and scaling["estimated_r2"]
            >= float(gates["minimum_scaling_r2"])
        ),
        "epsilon_oracle_quadratic": bool(
            float(gates["minimum_scaling_slope"])
            <= scaling["oracle_slope"]
            <= float(gates["maximum_scaling_slope"])
            and scaling["oracle_r2"]
            >= float(gates["minimum_scaling_r2"])
        ),
    }
    geometry = {
        "w1_discrete_cluster_recovery": bool(
            w1["mean_confirmation_cluster_ari"]
            >= float(gates["minimum_group_cluster_ari"])
        ),
        "w1_mixture_predictive_advantage": bool(
            -w1["mean_manifold_advantage"]
            >= float(gates["minimum_predictive_geometry_advantage"])
        ),
        "w5_continuous_relation_recovery": bool(
            w5["mean_continuous_distance_spearman"]
            >= float(gates["minimum_continuous_distance_spearman"])
        ),
        "w5_manifold_predictive_advantage": bool(
            w5["mean_manifold_advantage"]
            >= float(gates["minimum_predictive_geometry_advantage"])
        ),
    }
    if not all(core.values()):
        status = "V8_EPSILON_HIERARCHY_STOP_CORE"
    elif not all(geometry.values()):
        status = "V8_EPSILON_HIERARCHY_CORE_PASS_GEOMETRY_UNRESOLVED"
    else:
        status = "V8_EPSILON_HIERARCHY_FULL_PLANTED_PASS"
    return {
        "status": status,
        "core_checks": core,
        "geometry_checks": geometry,
        "scaling": scaling,
        "headline": {
            "group_only": {
                "author_all_auc": float(w1["mean_author_all_auc"]),
                "author_within_auc": float(
                    w1["mean_author_within_group_auc"]
                ),
                "group_auc": float(w1["mean_group_auc"]),
            },
            "individual_only": {
                "author_all_auc": float(w2["mean_author_all_auc"]),
                "author_within_auc": float(
                    w2["mean_author_within_group_auc"]
                ),
                "group_auc": float(w2["mean_group_auc"]),
            },
            "joint": {
                "author_within_auc": float(
                    w3["mean_author_within_group_auc"]
                ),
                "group_auc": float(w3["mean_group_auc"]),
            },
            "c1_group_confound": {
                "c1_group_auc": float(w6["mean_c1_group_auc"]),
                "c2_group_auc": float(w6["mean_group_auc"]),
            },
            "observer_artifact": {
                "primary_within_auc": float(
                    w7["mean_author_within_group_auc"]
                ),
                "cross_observer_within_auc": float(
                    w7["mean_cross_observer_within_auc"]
                ),
            },
        },
        "claim_boundary": str(config["claim_boundary"]),
    }


def _report(
    decision: dict[str, Any],
    summary: pd.DataFrame,
) -> str:
    columns = [
        "case_id",
        "epsilon",
        "mean_author_all_auc",
        "mean_author_within_group_auc",
        "mean_group_auc",
        "mean_c1_group_auc",
        "within_pairing_rejection_rate",
        "mean_estimated_residual_energy",
        "mean_confirmation_cluster_ari",
        "mean_manifold_advantage",
        "mean_cross_observer_within_auc",
    ]
    return f"""# V8 Vanishing-Individuality Planted-World Battery

## Decision

`{decision["status"]}`

## Headline

```json
{json.dumps(decision["headline"], indent=2)}
```

## Epsilon Scaling

```json
{json.dumps(decision["scaling"], indent=2)}
```

## World Summary

{summary[columns].to_markdown(index=False)}

## Core Checks

```json
{json.dumps(decision["core_checks"], indent=2)}
```

## Geometry Checks

```json
{json.dumps(decision["geometry_checks"], indent=2)}
```

## Boundary

{decision["claim_boundary"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--jobs", type=int)
    args = parser.parse_args()
    config = _read_json(args.config)
    repetitions = (
        int(args.repetitions)
        if args.repetitions is not None
        else int(config["repetitions"])
    )
    jobs = (
        int(args.jobs)
        if args.jobs is not None
        else int(config.get("jobs", 1))
    )
    spec = VanishingIndividualitySpec(**config["spec"])
    cases = _cases(config)
    payloads = [
        (repetition, config, spec, cases)
        for repetition in range(repetitions)
    ]
    rows = []
    if jobs <= 1:
        for payload in payloads:
            rows.extend(_run_repetition(payload))
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            for result in executor.map(
                _run_repetition,
                payloads,
                chunksize=1,
            ):
                rows.extend(result)
    seed_metrics = pd.DataFrame(rows)
    summary = _summary(seed_metrics)
    decision = _decision(summary, config)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    seed_metrics.to_csv(args.output_dir / "seed_metrics.csv", index=False)
    summary.to_csv(args.output_dir / "world_summary.csv", index=False)
    _write_json(args.output_dir / "decision.json", decision)
    _write_json(
        args.output_dir / "config.resolved.json",
        {
            **config,
            "executed_repetitions": repetitions,
            "executed_jobs": jobs,
        },
    )
    (args.output_dir / "report.md").write_text(
        _report(decision, summary),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=args.config,
        code_paths=[
            Path(__file__),
            ROOT / "suica_core" / "v8_vanishing_individuality.py",
            ROOT / "suica_core" / "v8_behavior_c2.py",
        ],
        estimand_id="V8-I15-c2-epsilon-hierarchy-planted",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
