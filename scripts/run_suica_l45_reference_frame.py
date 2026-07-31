#!/usr/bin/env python3
"""Run the opened SUICA L4-to-L5 reference-frame discovery battery."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.foundation_reference_frame import (  # noqa: E402
    L45ReferenceSpec,
    aggregate_to_common_facet,
    fit_l45_pipeline,
    fit_reference_frame,
    mdd_metrics,
    normalized_score_error,
    observable_nested_region,
    operator_transport_audit,
    oracle_score_target,
    score_correlation,
    score_panel,
    simulate_l45_world,
)
from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)


NUMERIC_METRICS = (
    "score_correlation",
    "normalized_score_error",
    "truth_isolation_max_abs",
    "minimum_ess_ratio",
    "composition_standardized_error",
    "composition_naive_error",
    "composition_correction_gain",
    "reference_weighted_error",
    "reference_unweighted_error",
    "reference_correction_gain",
    "alias_identity_error",
    "operator_commutation_defect",
    "mdd95",
    "mdd_null_false_positive",
    "mdd_two_mdd_power",
    "uncertainty_coverage",
    "uncertainty_median_radius",
    "uncertainty_successful_draw_rate",
    "hard_cv_loss",
    "soft_cv_loss",
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _observed_only(world: dict[str, Any]) -> dict[str, Any]:
    """Remove generator-only fields without copying the observed arrays."""
    observed = dict(world)
    for role in ("reference", "fit", "test"):
        observed[role] = {
            key: value
            for key, value in world[role].items()
            if key != "stable_field"
        }
    return observed


def _run_one(
    *,
    world_name: str,
    noise_mode: str,
    repetition: int,
    seed: int,
    config: dict[str, Any],
    spec: L45ReferenceSpec,
) -> dict[str, Any]:
    world = simulate_l45_world(
        seed=seed,
        world=world_name,
        noise_mode=noise_mode,
        spec=spec,
    )
    selection_seed = seed + 17
    pipeline = fit_l45_pipeline(
        world,
        candidates=config["candidate_ranks"],
        folds=int(config["selection_folds"]),
        seed=selection_seed,
        soft_noninferiority_margin=float(
            config["soft_noninferiority_margin"]
        ),
    )
    scored = score_panel(world["test"], world, pipeline)
    transport = operator_transport_audit(world)
    row: dict[str, Any] = {
        "world": world_name,
        "noise_mode": noise_mode,
        "repetition": int(repetition),
        "seed": int(seed),
        "pipeline_status": pipeline["status"],
        "score_status": scored["status"],
        "operator_status": transport["status"],
        "estimator": pipeline.get("estimator", ""),
        "selected_rank": pipeline.get("selected_rank", np.nan),
        "cause_attribution_allowed": bool(
            scored.get("cause_attribution_allowed", False)
        ),
        "panel_disjoint_by_generation": True,
        **{metric: np.nan for metric in NUMERIC_METRICS},
    }
    row["alias_identity_error"] = float(world["alias_identity_error"])
    row["operator_commutation_defect"] = float(
        transport["commutation_defect"]
    )
    row["hard_cv_loss"] = pipeline.get("hard_cv_loss", np.nan)
    row["soft_cv_loss"] = pipeline.get("soft_cv_loss", np.nan)

    weighted_frame = fit_reference_frame(
        world["reference"],
        lambda_facet=world["lambda_facet"],
        target_group_weights=world["target_group_weights"],
        ridge=spec.covariance_ridge,
        weighted=True,
    )
    unweighted_frame = fit_reference_frame(
        world["reference"],
        lambda_facet=world["lambda_facet"],
        target_group_weights=world["target_group_weights"],
        ridge=spec.covariance_ridge,
        weighted=False,
    )
    if (
        weighted_frame["status"] == "REFERENCE_FRAME_READY"
        and unweighted_frame["status"] == "REFERENCE_FRAME_READY"
    ):
        truth_center = np.asarray(world["true_reference_center"])
        weighted_error = float(np.linalg.norm(
            weighted_frame["center"] - truth_center
        ))
        unweighted_error = float(np.linalg.norm(
            unweighted_frame["center"] - truth_center
        ))
        row["reference_weighted_error"] = weighted_error
        row["reference_unweighted_error"] = unweighted_error
        row["reference_correction_gain"] = float(
            1.0 - weighted_error / max(unweighted_error, 1e-12)
        )

    aggregate = aggregate_to_common_facet(
        world["test"],
        world["lambda_facet"],
    )
    if aggregate["status"] == "COMMON_FACET_READY":
        raw_target = np.einsum(
            "f,afd->ad",
            world["lambda_facet"],
            world["test"]["stable_field"],
        )
        standardized_error = float(np.sqrt(np.mean(
            (
                np.asarray(aggregate["standardized"]).mean(axis=1)
                - raw_target
            )
            ** 2
        )))
        naive_error = float(np.sqrt(np.mean(
            (
                np.asarray(aggregate["naive"]).mean(axis=1)
                - raw_target
            )
            ** 2
        )))
        row["minimum_ess_ratio"] = float(
            aggregate["minimum_ess_ratio"]
        )
        row["composition_standardized_error"] = standardized_error
        row["composition_naive_error"] = naive_error
        row["composition_correction_gain"] = float(
            1.0 - standardized_error / max(naive_error, 1e-12)
        )

    if scored["status"] == "L5_CANDIDATE_SCORE_READY":
        target = oracle_score_target(
            world["test"],
            world,
            pipeline,
        )
        row["score_correlation"] = score_correlation(
            scored["point"],
            target,
        )
        row["normalized_score_error"] = normalized_score_error(
            scored["point"],
            target,
        )
        mdd = mdd_metrics(scored["left"], scored["right"])
        row["mdd95"] = mdd["mdd95"]
        row["mdd_null_false_positive"] = mdd[
            "null_false_positive"
        ]
        row["mdd_two_mdd_power"] = mdd["two_mdd_power"]

        observed = _observed_only(world)
        observed_pipeline = fit_l45_pipeline(
            observed,
            candidates=config["candidate_ranks"],
            folds=int(config["selection_folds"]),
            seed=selection_seed,
            soft_noninferiority_margin=float(
                config["soft_noninferiority_margin"]
            ),
        )
        observed_score = score_panel(
            observed["test"],
            observed,
            observed_pipeline,
        )
        if observed_score["status"] == "L5_CANDIDATE_SCORE_READY":
            row["truth_isolation_max_abs"] = float(np.max(np.abs(
                np.asarray(scored["point"])
                - np.asarray(observed_score["point"])
            )))

    if (
        repetition < int(config["uncertainty_repetitions"])
        and world_name in set(config["uncertainty_worlds"])
        and pipeline["status"] == "L45_PIPELINE_READY"
    ):
        region = observable_nested_region(
            world,
            pipeline,
            draws=int(config["uncertainty_draws"]),
            tracked_authors=int(config["tracked_authors"]),
            candidates=config["candidate_ranks"],
            folds=int(config["selection_folds"]),
            seed=seed + 31,
            soft_noninferiority_margin=float(
                config["soft_noninferiority_margin"]
            ),
        )
        row["uncertainty_coverage"] = region["coverage"]
        row["uncertainty_median_radius"] = region["median_radius"]
        row["uncertainty_successful_draw_rate"] = region[
            "successful_draw_rate"
        ]
    return row


def _bootstrap_interval(
    values: np.ndarray,
    *,
    rng: np.random.Generator,
    draws: int,
) -> dict[str, float | int]:
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    if not len(finite):
        return {
            "mean": np.nan,
            "lower95": np.nan,
            "upper95": np.nan,
            "n": 0,
        }
    indices = rng.integers(0, len(finite), size=(draws, len(finite)))
    means = finite[indices].mean(axis=1)
    return {
        "mean": float(finite.mean()),
        "lower95": float(np.quantile(means, 0.025)),
        "upper95": float(np.quantile(means, 0.975)),
        "n": int(len(finite)),
    }


def _summarize(
    metrics: pd.DataFrame,
    *,
    seed: int,
    draws: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows: list[dict[str, Any]] = []
    for (world, noise), group in metrics.groupby(
        ["world", "noise_mode"],
        sort=True,
    ):
        for metric in NUMERIC_METRICS:
            interval = _bootstrap_interval(
                group[metric].to_numpy(dtype=float),
                rng=rng,
                draws=draws,
            )
            rows.append({
                "world": world,
                "noise_mode": noise,
                "metric": metric,
                **interval,
            })
    return pd.DataFrame(rows)


def _value(
    summary: pd.DataFrame,
    *,
    world: str,
    noise: str,
    metric: str,
    statistic: str,
) -> float:
    selected = summary[
        (summary["world"] == world)
        & (summary["noise_mode"] == noise)
        & (summary["metric"] == metric)
    ]
    if len(selected) != 1:
        return float("nan")
    return float(selected.iloc[0][statistic])


def _minimum_across_noise(
    summary: pd.DataFrame,
    *,
    world: str,
    metric: str,
    statistic: str,
    noise_modes: list[str],
) -> float:
    values = [
        _value(
            summary,
            world=world,
            noise=noise,
            metric=metric,
            statistic=statistic,
        )
        for noise in noise_modes
    ]
    return min(values) if all(np.isfinite(values)) else float("nan")


def _maximum_across_noise(
    summary: pd.DataFrame,
    *,
    world: str,
    metric: str,
    statistic: str,
    noise_modes: list[str],
) -> float:
    values = [
        _value(
            summary,
            world=world,
            noise=noise,
            metric=metric,
            statistic=statistic,
        )
        for noise in noise_modes
    ]
    return max(values) if all(np.isfinite(values)) else float("nan")


def _decision(
    config: dict[str, Any],
    metrics: pd.DataFrame,
    summary: pd.DataFrame,
) -> dict[str, Any]:
    gates = config["gates"]
    noise_modes = list(config["noise_modes"])
    refusal_expectations = {
        "support_hole": ("score_status", "REFUSE_NONOVERLAP"),
        "choice_response_alias": (
            "pipeline_status",
            "REFUSE_CHOICE_RESPONSE_ALIAS_NO_FACET_PROVENANCE",
        ),
        "person_occasion_alias": (
            "pipeline_status",
            "REFUSE_PERSON_OCCASION_ALIAS",
        ),
        "correlated_replicate_shock": (
            "pipeline_status",
            "REFUSE_CORRELATED_OR_UNDECLARED_OCCASIONS",
        ),
        "operator_kernel": (
            "operator_status",
            "REFUSE_OPERATOR_KERNEL_NONINVERTIBLE",
        ),
    }
    refusal_rates = {
        world: float(np.mean(
            metrics.loc[metrics["world"] == world, column] == expected
        ))
        for world, (column, expected) in refusal_expectations.items()
    }
    uncertainty = metrics[
        metrics["uncertainty_coverage"].notna()
    ]
    truth_isolation = metrics["truth_isolation_max_abs"].dropna()
    valid_operator = metrics[
        metrics["world"] != "operator_kernel"
    ]["operator_commutation_defect"].replace([np.inf, -np.inf], np.nan)
    uncertainty_lower = [
        _value(
            summary,
            world=world,
            noise=noise,
            metric="uncertainty_coverage",
            statistic="lower95",
        )
        for world in config["uncertainty_worlds"]
        for noise in noise_modes
    ]
    uncertainty_mean = [
        _value(
            summary,
            world=world,
            noise=noise,
            metric="uncertainty_coverage",
            statistic="mean",
        )
        for world in config["uncertainty_worlds"]
        for noise in noise_modes
    ]

    extrema = {
        "minimum_clean_score_correlation_lower": _minimum_across_noise(
            summary,
            world="clean",
            metric="score_correlation",
            statistic="lower95",
            noise_modes=noise_modes,
        ),
        "maximum_clean_normalized_error_upper": _maximum_across_noise(
            summary,
            world="clean",
            metric="normalized_score_error",
            statistic="upper95",
            noise_modes=noise_modes,
        ),
        "minimum_composition_gain_lower": _minimum_across_noise(
            summary,
            world="composition_shift",
            metric="composition_correction_gain",
            statistic="lower95",
            noise_modes=noise_modes,
        ),
        "minimum_reference_gain_lower": _minimum_across_noise(
            summary,
            world="reference_mixture",
            metric="reference_correction_gain",
            statistic="lower95",
            noise_modes=noise_modes,
        ),
        "maximum_truth_isolation_error": (
            float(truth_isolation.max())
            if len(truth_isolation)
            else float("inf")
        ),
        "maximum_alias_identity_error": float(
            metrics["alias_identity_error"].max()
        ),
        "maximum_valid_operator_defect": float(valid_operator.max()),
        "minimum_uncertainty_coverage_lower": (
            min(uncertainty_lower)
            if uncertainty_lower
            and all(np.isfinite(uncertainty_lower))
            else 0.0
        ),
        "maximum_uncertainty_coverage_mean": (
            max(uncertainty_mean)
            if uncertainty_mean
            and all(np.isfinite(uncertainty_mean))
            else 1.0
        ),
        "minimum_uncertainty_success_rate": (
            float(
                uncertainty["uncertainty_successful_draw_rate"].min()
            )
            if len(uncertainty)
            else 0.0
        ),
        "maximum_clean_mdd_false_positive_upper": _maximum_across_noise(
            summary,
            world="clean",
            metric="mdd_null_false_positive",
            statistic="upper95",
            noise_modes=noise_modes,
        ),
        "minimum_clean_two_mdd_power_lower": _minimum_across_noise(
            summary,
            world="clean",
            metric="mdd_two_mdd_power",
            statistic="lower95",
            noise_modes=noise_modes,
        ),
    }
    checks = {
        "clean_score_recovery": (
            extrema["minimum_clean_score_correlation_lower"]
            >= float(gates["minimum_clean_score_correlation_lower"])
        ),
        "clean_normalized_error": (
            extrema["maximum_clean_normalized_error_upper"]
            <= float(gates["maximum_clean_normalized_error_upper"])
        ),
        "composition_standardization": (
            extrema["minimum_composition_gain_lower"]
            >= float(gates["minimum_composition_gain_lower"])
        ),
        "reference_mixture_correction": (
            extrema["minimum_reference_gain_lower"]
            >= float(gates["minimum_reference_gain_lower"])
        ),
        "truth_isolation": (
            extrema["maximum_truth_isolation_error"]
            <= float(gates["maximum_truth_isolation_error"])
        ),
        "required_refusals": (
            min(refusal_rates.values())
            >= float(gates["minimum_refusal_rate"])
        ),
        "aq_gauge_alias": (
            extrema["maximum_alias_identity_error"]
            <= float(gates["maximum_alias_identity_error"])
            and not bool(metrics["cause_attribution_allowed"].any())
        ),
        "operator_transport": (
            extrema["maximum_valid_operator_defect"]
            <= float(gates["maximum_operator_transport_defect"])
        ),
        "observable_uncertainty": (
            extrema["minimum_uncertainty_coverage_lower"]
            >= float(gates.get(
                "minimum_uncertainty_coverage_lower",
                gates.get("minimum_uncertainty_coverage", 0.0),
            ))
            and extrema["maximum_uncertainty_coverage_mean"]
            <= float(gates.get(
                "maximum_uncertainty_coverage_mean",
                1.0,
            ))
            and extrema["minimum_uncertainty_success_rate"]
            >= float(gates["minimum_uncertainty_success_rate"])
        ),
        "mdd_false_positive": (
            extrema["maximum_clean_mdd_false_positive_upper"]
            <= float(gates["maximum_mdd_false_positive_upper"])
        ),
        "mdd_power": (
            extrema["minimum_clean_two_mdd_power_lower"]
            >= float(gates["minimum_two_mdd_power_lower"])
        ),
    }
    passed = bool(all(checks.values()))
    return {
        "status": (
            "L45_OPENED_DISCOVERY_CANDIDATE"
            if passed
            else "REFUSE_L45_PROMOTION"
        ),
        "passed": passed,
        "maximum_licensed_layer": "L4_technical_object",
        "target_edge": "E45_reference_scoring",
        "checks": checks,
        "refusal_rates": refusal_rates,
        "extrema": extrema,
        "repetitions": int(config["repetitions"]),
        "formal_confirmation_required": True,
        "claim_boundary": config["claim_boundary"],
    }


def _report(
    config: dict[str, Any],
    decision: dict[str, Any],
    summary: pd.DataFrame,
) -> str:
    selected_pairs = {
        ("clean", "score_correlation"),
        ("clean", "normalized_score_error"),
        ("clean", "mdd_null_false_positive"),
        ("clean", "mdd_two_mdd_power"),
        ("clean", "uncertainty_coverage"),
        ("clean", "uncertainty_successful_draw_rate"),
        ("composition_shift", "composition_correction_gain"),
        ("reference_mixture", "reference_correction_gain"),
        ("informative_precision", "uncertainty_coverage"),
        ("informative_precision", "uncertainty_successful_draw_rate"),
    }
    selected = summary[
        summary.apply(
            lambda row: (row["world"], row["metric"]) in selected_pairs,
            axis=1,
        )
        & (summary["n"] > 0)
    ].copy()
    table = selected.to_markdown(index=False, floatfmt=".4f")
    checks = "\n".join(
        f"- {'PASS' if passed else 'FAIL'}: `{name}`"
        for name, passed in decision["checks"].items()
    )
    return f"""# SUICA L4-to-L5 Reference-Frame Discovery

Decision: `{decision["status"]}`

## Question

Can an anonymous facet-indexed technical vector become a comparable
reference-relative measurement candidate when the reference population,
target facet measure, chart/operator, support rule, occasion universe, and
uncertainty procedure are frozen?

## Design

- Reference, calibration, and scored panels are generated independently.
- Scores standardize event composition to a frozen facet measure before
  applying a frozen population chart.
- Stable-subspace selection uses calibration occasions only.
- Confidence regions jointly resample reference authors, calibration authors,
  within-author occasions, and observed event means; planted truth is accessed
  only after each region is frozen.
- Ten synthetic worlds include heavy tails, support holes, reference-mixture
  shift, A/Q gauge aliases, choice/response aliases, person/occasion aliases,
  correlated repeat shocks, operator kernels, and informative precision.

## Gates

{checks}

## Selected summaries

{table}

## Refusal rates

```json
{json.dumps(decision["refusal_rates"], indent=2)}
```

## Extrema

```json
{json.dumps(decision["extrema"], indent=2)}
```

## Interpretation

Passing this opened discovery battery would show only that a declared
reference-frame construction can recover a planted technical score and refuse
registered nonidentified worlds. It would not establish an L5 score on human
text, a psychological construct, a personality trait, or an application.
Formal promotion requires a separately sealed fresh-seed confirmation and a
real study-specific generalizability design.

## Claim boundary

{config["claim_boundary"]}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/suica_l45_reference_frame.smoke.json",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "results/suica_l45_reference_frame",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=ROOT / "reports/SUICA_L45_REFERENCE_FRAME_REPORT.md",
    )
    args = parser.parse_args()
    config = _read(args.config)
    output_dir = args.output_root / str(config["run_id"])
    output_dir.mkdir(parents=True, exist_ok=True)
    spec = L45ReferenceSpec(**config["spec"])

    rows: list[dict[str, Any]] = []
    sequences = np.random.SeedSequence(int(config["seed"])).spawn(
        int(config["repetitions"])
    )
    for repetition, root_sequence in enumerate(sequences):
        branches = root_sequence.spawn(
            len(config["worlds"]) * len(config["noise_modes"])
        )
        index = 0
        for world_name in config["worlds"]:
            for noise_mode in config["noise_modes"]:
                seed = int(branches[index].generate_state(
                    1,
                    dtype=np.uint64,
                )[0])
                index += 1
                rows.append(_run_one(
                    world_name=world_name,
                    noise_mode=noise_mode,
                    repetition=repetition,
                    seed=seed,
                    config=config,
                    spec=spec,
                ))

    metrics = pd.DataFrame(rows)
    summary = _summarize(
        metrics,
        seed=int(config["seed"]) + 10_003,
        draws=int(config["summary_bootstrap_draws"]),
    )
    decision = _decision(config, metrics, summary)
    report = _report(config, decision, summary)

    metrics.to_csv(output_dir / "metrics.csv", index=False)
    summary.to_csv(output_dir / "summary.csv", index=False)
    _write(output_dir / "decision.json", decision)
    _write(
        output_dir / "config_effective.json",
        {**copy.deepcopy(config), "resolved_spec": asdict(spec)},
    )
    (output_dir / "report.md").write_text(report, encoding="utf-8")
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(report, encoding="utf-8")
    write_run_manifest(
        output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/foundation_reference_frame.py",
            Path(__file__).resolve(),
        ],
        estimand_id=str(config["estimand_id"]),
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        output_dir,
        output_dir / "artifact_inventory.json",
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
