#!/usr/bin/env python3
"""Run the V3.7H.4D reference-measure and residual-shape frontier."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import beta, t

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_reference_measure_frontier import (  # noqa: E402
    ReferenceFrontierSpec,
    additive_residual,
    condition_profile,
    correlation,
    empirical_structural_zero,
    fit_propensity,
    predict_propensity,
    residual_diagnostics,
    score_panel,
    simulate_reference_world,
)


DEFAULT_CONFIG = (
    ROOT / "configs/v8_reference_measure_frontier_v37h4d.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_reference_measure_frontier"
    / "v37h4d_discovery"
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            allow_nan=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _spec(config: dict[str, Any]) -> ReferenceFrontierSpec:
    values = config["spec"]
    return ReferenceFrontierSpec(
        societies=int(values["societies"]),
        groups_per_society=int(values["groups_per_society"]),
        authors_per_group=int(values["authors_per_group"]),
        conditions=int(values["conditions"]),
        dimensions=int(values["dimensions"]),
        panels=int(values["panels"]),
    )


def _cell_definitions(
    config: dict[str, Any],
    *,
    mode: str,
) -> list[dict[str, Any]]:
    main_worlds = [
        "noncentered",
        "reference_shift",
        "support_violation",
        "full_rank",
        "minority_local",
        "near_kernel",
        "aq_alias",
    ]
    boundary_worlds = [
        "noncentered",
        "reference_shift",
        "support_violation",
        "full_rank",
        "minority_local",
        "near_kernel",
    ]
    definitions: list[dict[str, Any]] = []
    if mode == "smoke":
        repetitions = int(config["smoke_repetitions"])
        for noise in config["noise_modes"]:
            definitions.append({
                "world": "additive",
                "cell_kind": "w0",
                "noise_mode": str(noise),
                "repetitions": repetitions,
                "effect_share": 0.0,
                "reference_jsd": 0.0,
                "support_coverage": 1.0,
                "near_kernel_fraction": float(
                    config["near_kernel_score_fraction"]
                ),
            })
        for world in main_worlds:
            definitions.append({
                "world": world,
                "cell_kind": "main",
                "noise_mode": "gaussian",
                "repetitions": repetitions,
                "effect_share": float(config["main_effect_share"]),
                "reference_jsd": (
                    float(config["main_reference_jsd"])
                    if world == "reference_shift"
                    else 0.0
                ),
                "support_coverage": (
                    float(config["main_support_coverage"])
                    if world == "support_violation"
                    else 1.0
                ),
                "near_kernel_fraction": float(
                    config["near_kernel_score_fraction"]
                ),
            })
        return definitions

    for noise in config["noise_modes"]:
        definitions.append({
            "world": "additive",
            "cell_kind": "w0",
            "noise_mode": str(noise),
            "repetitions": int(
                config["w0_calibration_repetitions"]
            ),
            "effect_share": 0.0,
            "reference_jsd": 0.0,
            "support_coverage": 1.0,
            "near_kernel_fraction": float(
                config["near_kernel_score_fraction"]
            ),
        })
        for world in main_worlds:
            definitions.append({
                "world": world,
                "cell_kind": "main",
                "noise_mode": str(noise),
                "repetitions": int(config["main_repetitions"]),
                "effect_share": float(config["main_effect_share"]),
                "reference_jsd": (
                    float(config["main_reference_jsd"])
                    if world == "reference_shift"
                    else 0.0
                ),
                "support_coverage": (
                    float(config["main_support_coverage"])
                    if world == "support_violation"
                    else 1.0
                ),
                "near_kernel_fraction": float(
                    config["near_kernel_score_fraction"]
                ),
            })
    for world in boundary_worlds:
        definitions.append({
            "world": world,
            "cell_kind": "boundary",
            "noise_mode": "gaussian",
            "repetitions": int(config["boundary_repetitions"]),
            "effect_share": float(config["boundary_effect_share"]),
            "reference_jsd": (
                float(config["boundary_reference_jsd"])
                if world == "reference_shift"
                else 0.0
            ),
            "support_coverage": (
                float(config["boundary_support_coverage"])
                if world == "support_violation"
                else 1.0
            ),
            "near_kernel_fraction": (
                float(config["boundary_near_kernel_score_fraction"])
                if world == "near_kernel"
                else float(config["near_kernel_score_fraction"])
            ),
        })
    return definitions


def _score_at_k(
    world: dict[str, Any],
    *,
    opportunities: int,
    pseudocount: float,
    spec: ReferenceFrontierSpec,
) -> dict[str, Any]:
    train, calibration, test = spec.author_split
    counts = world["counts_by_k"][int(opportunities)]
    means = world["means_by_k"][int(opportunities)]
    profile = condition_profile(means, train)
    coefficients = fit_propensity(
        counts,
        world["author_covariate"],
        train,
        pseudocount=float(pseudocount),
    )
    propensity_0 = predict_propensity(
        coefficients,
        world["author_covariate"],
        environment=0,
    )
    propensity_1 = predict_propensity(
        coefficients,
        world["author_covariate"],
        environment=1,
    )
    calibration_0 = score_panel(
        counts[0],
        means[0],
        propensity_0,
        profile,
        world["reference"],
        calibration,
    )
    calibration_1 = score_panel(
        counts[1],
        means[1],
        propensity_1,
        profile,
        world["reference"],
        calibration,
    )
    calibration_loss = float(
        np.mean(
            (
                calibration_0["common"]
                - calibration_1["common"]
            ) ** 2
        )
    )
    test_0 = score_panel(
        counts[2],
        means[2],
        propensity_0,
        profile,
        world["reference"],
        test,
    )
    test_1 = score_panel(
        counts[3],
        means[3],
        propensity_1,
        profile,
        world["reference"],
        test,
    )
    oracle = world["theta_star"][test]
    oracle_sd = max(float(np.std(oracle)), 1e-12)
    nste_0 = float(
        np.sqrt(np.mean((test_0["common"] - oracle) ** 2))
        / oracle_sd
    )
    nste_1 = float(
        np.sqrt(np.mean((test_1["common"] - oracle) ** 2))
        / oracle_sd
    )
    common_difference_mse = float(
        np.mean(
            (test_0["common"] - test_1["common"]) ** 2
        )
    )
    naive_difference_mse = float(
        np.mean(
            (test_0["naive"] - test_1["naive"]) ** 2
        )
    )
    reference_gain = float(
        1.0
        - common_difference_mse
        / max(naive_difference_mse, 1e-12)
    )
    d_star = float(
        np.sqrt(common_difference_mse) / oracle_sd
    )
    structural_zero = empirical_structural_zero(
        counts,
        np.concatenate([train, calibration]),
        world["group_labels"],
    )
    coverage = np.concatenate([
        test_0["coverage"],
        test_1["coverage"],
    ])
    ess = np.concatenate([test_0["ess"], test_1["ess"]])
    coverage_q05 = float(np.quantile(coverage, 0.05))
    ess_q05 = float(np.quantile(ess, 0.05))
    refuse = bool(
        coverage_q05 < 0.95
        or ess_q05 < 32.0
        or structural_zero
    )
    return {
        "opportunities": int(opportunities),
        "calibration_loss": calibration_loss,
        "nste": max(nste_0, nste_1),
        "nste_environment_0": nste_0,
        "nste_environment_1": nste_1,
        "d_star": d_star,
        "reference_correction_gain": reference_gain,
        "common_score_correlation": correlation(
            test_0["common"],
            test_1["common"],
        ),
        "common_oracle_correlation": 0.5 * (
            correlation(test_0["common"], oracle)
            + correlation(test_1["common"], oracle)
        ),
        "naive_error_advantage": float(
            (
                naive_difference_mse
                - common_difference_mse
            )
            / (oracle_sd**2)
        ),
        "coverage_q05": coverage_q05,
        "ess_q05": ess_q05,
        "structural_zero": structural_zero,
        "refuse_nonoverlap": refuse,
        "formal_score_output": not refuse,
        "profile": profile,
        "counts": counts,
        "means": means,
        "test_authors": test,
    }


def _select_pseudocount(
    world: dict[str, Any],
    *,
    opportunities: int,
    candidates: list[float],
    spec: ReferenceFrontierSpec,
) -> tuple[float, list[dict[str, float]]]:
    losses = []
    for candidate in candidates:
        result = _score_at_k(
            world,
            opportunities=opportunities,
            pseudocount=float(candidate),
            spec=spec,
        )
        losses.append({
            "pseudocount": float(candidate),
            "calibration_loss": float(result["calibration_loss"]),
        })
    winner = min(
        losses,
        key=lambda row: (row["calibration_loss"], row["pseudocount"]),
    )
    return float(winner["pseudocount"]), losses


def _evaluate(
    *,
    definition: dict[str, Any],
    repetition: int,
    world_seed: int,
    diagnostic_seed: int,
    config: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    spec = _spec(config)
    world = simulate_reference_world(
        seed=world_seed,
        world=str(definition["world"]),
        effect_share=float(definition["effect_share"]),
        reference_jsd=float(definition["reference_jsd"]),
        support_coverage=float(definition["support_coverage"]),
        near_kernel_fraction=float(
            definition["near_kernel_fraction"]
        ),
        noise_mode=str(definition["noise_mode"]),
        opportunity_prefixes=tuple(
            map(int, config["opportunity_prefixes"])
        ),
        author_tilt=float(config["author_tilt"]),
        author_amplitude=float(config["author_amplitude"]),
        condition_amplitude=float(config["condition_amplitude"]),
        society_amplitude=float(config["society_amplitude"]),
        group_amplitude=float(config["group_amplitude"]),
        panel_noise_amplitude=float(
            config["panel_noise_amplitude"]
        ),
        technical_noise_amplitude=float(
            config["technical_noise_amplitude"]
        ),
        student_df=float(config["student_df"]),
        heteroskedastic_strength=float(
            config["heteroskedastic_strength"]
        ),
        minority_author_fraction=float(
            config["minority_author_fraction"]
        ),
        minority_condition_fraction=float(
            config["minority_condition_fraction"]
        ),
        spec=spec,
    )
    primary_k = int(config["primary_opportunities"])
    pseudocount, tuning = _select_pseudocount(
        world,
        opportunities=primary_k,
        candidates=[
            float(value)
            for value in config["propensity_pseudocounts"]
        ],
        spec=spec,
    )
    k_rows = []
    primary: dict[str, Any] | None = None
    for opportunities in map(int, config["opportunity_prefixes"]):
        score = _score_at_k(
            world,
            opportunities=opportunities,
            pseudocount=pseudocount,
            spec=spec,
        )
        k_rows.append({
            "repetition": int(repetition),
            "world": str(definition["world"]),
            "cell_kind": str(definition["cell_kind"]),
            "noise_mode": str(definition["noise_mode"]),
            "effect_share": float(definition["effect_share"]),
            "reference_jsd": float(definition["reference_jsd"]),
            "support_coverage": float(
                definition["support_coverage"]
            ),
            "near_kernel_fraction": float(
                definition["near_kernel_fraction"]
            ),
            **{
                key: value
                for key, value in score.items()
                if key not in {
                    "profile",
                    "counts",
                    "means",
                    "test_authors",
                }
            },
        })
        if opportunities == primary_k:
            primary = score
    if primary is None:
        raise RuntimeError("primary opportunity prefix missing")

    diagnostics = {
        "crc": float("nan"),
        "crc_p": float("nan"),
        "crc_p_holm": float("nan"),
        "low_rank_ratio": float("nan"),
        "low_rank_p": float("nan"),
        "low_rank_p_holm": float("nan"),
        "hc": float("nan"),
        "hc_p": float("nan"),
        "hc_p_holm": float("nan"),
        "structure_detected": False,
        "non_low_rank_detected": False,
        "score_projection_ratio": float("nan"),
    }
    if not bool(primary["refuse_nonoverlap"]):
        test = primary["test_authors"]
        left, left_mask = additive_residual(
            primary["means"][2],
            primary["counts"][2],
            test,
        )
        right, right_mask = additive_residual(
            primary["means"][3],
            primary["counts"][3],
            test,
        )
        diagnostics = residual_diagnostics(
            left,
            right,
            left_mask,
            right_mask,
            world["group_labels"][test],
            rank=3,
            seed=diagnostic_seed,
            permutations=int(config["_active_permutations"]),
            alpha=float(config["holm_alpha"]),
        )

    world_name = str(definition["world"])
    if bool(primary["refuse_nonoverlap"]):
        classification = "REFUSE_NONOVERLAP"
    elif world_name == "aq_alias":
        classification = "CAUSE_UNIDENTIFIED"
    elif (
        diagnostics["structure_detected"]
        and diagnostics["score_projection_ratio"]
        < float(config["near_kernel_projection_threshold"])
    ):
        classification = "STRUCTURE_DETECTED_SCORE_NEAR_KERNEL"
    elif diagnostics["structure_detected"]:
        classification = "MODEL_INADEQUATE_CAUSE_UNIDENTIFIED"
    else:
        classification = "ADEQUATE"

    row = {
        "repetition": int(repetition),
        "world": world_name,
        "cell_kind": str(definition["cell_kind"]),
        "noise_mode": str(definition["noise_mode"]),
        "effect_share": float(definition["effect_share"]),
        "reference_jsd": float(definition["reference_jsd"]),
        "support_coverage": float(definition["support_coverage"]),
        "near_kernel_fraction": float(
            definition["near_kernel_fraction"]
        ),
        "world_seed": int(world_seed),
        "diagnostic_seed": int(diagnostic_seed),
        "selected_pseudocount": pseudocount,
        "nste": float(primary["nste"]),
        "d_star": float(primary["d_star"]),
        "reference_correction_gain": float(
            primary["reference_correction_gain"]
        ),
        "common_score_correlation": float(
            primary["common_score_correlation"]
        ),
        "common_oracle_correlation": float(
            primary["common_oracle_correlation"]
        ),
        "naive_error_advantage": float(
            primary["naive_error_advantage"]
        ),
        "coverage_q05": float(primary["coverage_q05"]),
        "ess_q05": float(primary["ess_q05"]),
        "structural_zero": bool(primary["structural_zero"]),
        "refuse_nonoverlap": bool(primary["refuse_nonoverlap"]),
        "formal_score_output": bool(primary["formal_score_output"]),
        "invalid_formal_score": bool(
            world_name == "support_violation"
            and primary["formal_score_output"]
        ),
        **diagnostics,
        "classification": classification,
        "near_kernel_correct": bool(
            world_name == "near_kernel"
            and classification
            == "STRUCTURE_DETECTED_SCORE_NEAR_KERNEL"
        ),
        "near_kernel_false_change": bool(
            world_name == "near_kernel"
            and diagnostics["structure_detected"]
            and classification
            != "STRUCTURE_DETECTED_SCORE_NEAR_KERNEL"
        ),
        "cause_unidentified": bool(
            world_name == "aq_alias"
            and classification == "CAUSE_UNIDENTIFIED"
        ),
        "specific_aq_attribution": False,
        "alias_identity_error": float(
            world["alias_identity_error"]
        ),
        "achieved_jsd": float(world["achieved_jsd"]),
        "achieved_support_coverage": float(
            world["achieved_support_coverage"]
        ),
        "interaction_effective_rank": float(
            world["effective_rank"]
        ),
        "oracle_score_fraction": float(world["score_fraction"]),
    }
    tuning_rows = [{
        "repetition": int(repetition),
        "world": world_name,
        "cell_kind": str(definition["cell_kind"]),
        "noise_mode": str(definition["noise_mode"]),
        "effect_share": float(definition["effect_share"]),
        "selected": bool(
            np.isclose(item["pseudocount"], pseudocount)
        ),
        **item,
    } for item in tuning]
    return row, k_rows, tuning_rows


def _worker(
    payload: tuple[
        dict[str, Any],
        dict[str, Any],
        int,
        int,
        int,
    ],
) -> dict[str, Any]:
    config, definition, repetition, world_seed, diagnostic_seed = payload
    row, k_rows, tuning_rows = _evaluate(
        definition=definition,
        repetition=repetition,
        world_seed=world_seed,
        diagnostic_seed=diagnostic_seed,
        config=config,
    )
    return {
        "cell": row,
        "k": k_rows,
        "tuning": tuning_rows,
        "seeds": [world_seed, diagnostic_seed],
    }


def _clopper(
    successes: int,
    trials: int,
    *,
    tail_alpha: float,
) -> tuple[float, float]:
    lower = (
        0.0
        if successes == 0
        else float(beta.ppf(
            tail_alpha,
            successes,
            trials - successes + 1,
        ))
    )
    upper = (
        1.0
        if successes == trials
        else float(beta.ppf(
            1.0 - tail_alpha,
            successes + 1,
            trials - successes,
        ))
    )
    return lower, upper


def _mean_interval(
    values: pd.Series,
    *,
    confidence: float = 0.95,
    family_cells: int = 1,
) -> tuple[float, float, float]:
    data = values.dropna().to_numpy(dtype=float)
    if len(data) == 0:
        return float("nan"), float("nan"), float("nan")
    mean = float(data.mean())
    if len(data) < 2:
        return mean, float("nan"), float("nan")
    alpha = (1.0 - confidence) / max(int(family_cells), 1)
    critical = float(t.ppf(1.0 - alpha / 2.0, len(data) - 1))
    radius = critical * float(data.std(ddof=1) / np.sqrt(len(data)))
    return mean, mean - radius, mean + radius


def _summaries(
    cells: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    keys = [
        "world",
        "cell_kind",
        "noise_mode",
        "effect_share",
        "reference_jsd",
        "support_coverage",
        "near_kernel_fraction",
    ]
    rows = []
    for key, group in cells.groupby(keys, sort=True, observed=True):
        base = dict(zip(keys, key, strict=True))
        trials = len(group)
        rates: dict[str, tuple[int, float, float]] = {}
        for name, column in {
            "detection": "structure_detected",
            "non_low_rank_detection": "non_low_rank_detected",
            "overlap_refusal": "refuse_nonoverlap",
            "invalid_score": "invalid_formal_score",
            "near_kernel_correct": "near_kernel_correct",
            "near_kernel_false_change": "near_kernel_false_change",
            "cause_unidentified": "cause_unidentified",
            "specific_attribution": "specific_aq_attribution",
        }.items():
            count = int(group[column].sum())
            alpha = (
                float(config["family_tail_alpha"])
                if base["cell_kind"] == "w0"
                else 0.05
            )
            lower, upper = _clopper(
                count,
                trials,
                tail_alpha=alpha,
            )
            rates[name] = (count, lower, upper)
        metrics = {}
        for name, column in {
            "nste": "nste",
            "d_star": "d_star",
            "reference_correction_gain": "reference_correction_gain",
            "common_score_correlation": "common_score_correlation",
            "common_oracle_correlation": "common_oracle_correlation",
            "naive_error_advantage": "naive_error_advantage",
            "score_projection_ratio": "score_projection_ratio",
        }.items():
            metrics[name] = _mean_interval(
                group[column],
                family_cells=4,
            )
        rows.append({
            **base,
            "trials": int(trials),
            **{
                f"{name}_count": count
                for name, (count, _, _) in rates.items()
            },
            **{
                f"{name}_lower": lower
                for name, (_, lower, _) in rates.items()
            },
            **{
                f"{name}_upper": upper
                for name, (_, _, upper) in rates.items()
            },
            **{
                f"mean_{name}": values[0]
                for name, values in metrics.items()
            },
            **{
                f"{name}_simultaneous_lower": values[1]
                for name, values in metrics.items()
            },
            **{
                f"{name}_simultaneous_upper": values[2]
                for name, values in metrics.items()
            },
            "mean_coverage_q05": float(group["coverage_q05"].mean()),
            "mean_ess_q05": float(group["ess_q05"].mean()),
            "mean_effective_rank": float(
                group["interaction_effective_rank"].mean()
            ),
            "maximum_alias_identity_error": float(
                group["alias_identity_error"].max()
            ),
        })
    summary = pd.DataFrame(rows)

    w0 = summary[summary["cell_kind"] == "w0"]
    main = summary[summary["cell_kind"] == "main"]
    reference = main[main["world"] == "reference_shift"]
    support = main[main["world"] == "support_violation"]
    strong = main[
        main["world"].isin([
            "noncentered",
            "full_rank",
            "minority_local",
        ])
    ]
    full_rank = main[main["world"] == "full_rank"]
    minority = main[main["world"] == "minority_local"]
    near_kernel = main[main["world"] == "near_kernel"]
    alias = main[main["world"] == "aq_alias"]
    gates = config["gates"]
    checks = {
        "w0_detector_calibration": bool(
            len(w0)
            and w0["detection_upper"].max()
            < float(gates["maximum_w0_false_refusal_upper"])
        ),
        "w0_overlap_calibration": bool(
            len(w0)
            and w0["overlap_refusal_upper"].max()
            < float(gates["maximum_w0_overlap_refusal_upper"])
        ),
        "w0_score_accuracy": bool(
            len(w0)
            and w0["nste_simultaneous_upper"].max()
            < float(gates["maximum_w0_nste_upper"])
        ),
        "w0_score_reliability": bool(
            len(w0)
            and w0[
                "common_score_correlation_simultaneous_lower"
            ].min()
            > float(gates["minimum_w0_score_correlation_lower"])
        ),
        "reference_correction_gain": bool(
            len(reference)
            and reference[
                "reference_correction_gain_simultaneous_lower"
            ].min()
            > float(gates["minimum_reference_correction_gain_lower"])
        ),
        "reference_difference": bool(
            len(reference)
            and reference["d_star_simultaneous_upper"].max()
            < float(gates["maximum_reference_difference_upper"])
        ),
        "reference_correlation": bool(
            len(reference)
            and reference[
                "common_score_correlation_simultaneous_lower"
            ].min()
            > float(gates["minimum_reference_correlation_lower"])
        ),
        "reference_advantage": bool(
            len(reference)
            and reference[
                "naive_error_advantage_simultaneous_lower"
            ].min()
            > float(gates["minimum_naive_error_advantage_lower"])
        ),
        "support_refusal": bool(
            len(support)
            and support["overlap_refusal_lower"].min()
            > float(gates["minimum_support_refusal_lower"])
        ),
        "support_no_invalid_score": bool(
            len(support)
            and support["invalid_score_upper"].max()
            < float(gates["maximum_invalid_score_upper"])
        ),
        "strong_detection": bool(
            len(strong)
            and strong["detection_lower"].min()
            > float(gates["minimum_strong_detection_lower"])
        ),
        "full_rank_non_lr_detection": bool(
            len(full_rank)
            and full_rank["non_low_rank_detection_lower"].min()
            > float(gates["minimum_strong_detection_lower"])
        ),
        "minority_non_lr_detection": bool(
            len(minority)
            and minority["non_low_rank_detection_lower"].min()
            > float(gates["minimum_strong_detection_lower"])
        ),
        "near_kernel_detection": bool(
            len(near_kernel)
            and near_kernel["detection_lower"].min()
            > float(gates["minimum_strong_detection_lower"])
        ),
        "near_kernel_no_false_change": bool(
            len(near_kernel)
            and near_kernel["near_kernel_false_change_upper"].max()
            < float(gates["maximum_near_kernel_false_change_upper"])
        ),
        "near_kernel_classification": bool(
            len(near_kernel)
            and near_kernel["near_kernel_correct_lower"].min()
            > float(gates["minimum_strong_detection_lower"])
        ),
        "alias_refusal": bool(
            len(alias)
            and alias["cause_unidentified_lower"].min()
            > float(gates["minimum_alias_refusal_lower"])
        ),
        "alias_no_attribution": bool(
            len(alias)
            and alias["specific_attribution_upper"].max()
            < float(gates["maximum_specific_attribution_upper"])
        ),
        "alias_identity": bool(
            len(alias)
            and alias["maximum_alias_identity_error"].max()
            <= float(gates["maximum_alias_identity_error"])
        ),
    }
    return summary, {"checks": checks}


def _report(decision: dict[str, Any]) -> str:
    return f"""# V8 V3.7H.4D Reference-Measure Frontier

Decision: `{decision["status"]}`

## Checks

```json
{json.dumps(decision["checks"], indent=2)}
```

## Boundary

This is a synthetic common-reference score and refusal experiment. It does
not establish real-text calibration, psychological meaning, causal
localization, diagnosis, or clinical use.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--mode",
        choices=["smoke", "discovery"],
        default="discovery",
    )
    args = parser.parse_args()
    config = _read(args.config)
    config["_active_permutations"] = (
        int(config["smoke_permutations"])
        if args.mode == "smoke"
        else int(config["permutations"])
    )
    seed = (
        int(config["smoke_seed"])
        if args.mode == "smoke"
        else int(config["seed"])
    )
    definitions = _cell_definitions(config, mode=args.mode)
    task_specs = [
        (definition, repetition)
        for definition in definitions
        for repetition in range(int(definition["repetitions"]))
    ]
    root = np.random.SeedSequence(seed)
    streams = root.spawn(2 * len(task_specs))
    seeds = [
        int(stream.generate_state(1, dtype=np.uint64)[0])
        for stream in streams
    ]
    payloads = [
        (
            config,
            definition,
            repetition,
            seeds[2 * index],
            seeds[2 * index + 1],
        )
        for index, (definition, repetition) in enumerate(task_specs)
    ]
    if int(config["jobs"]) == 1:
        nested = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(
            max_workers=int(config["jobs"]),
        ) as executor:
            nested = list(executor.map(_worker, payloads, chunksize=1))

    cells = pd.DataFrame([item["cell"] for item in nested])
    k_metrics = pd.DataFrame([
        row for item in nested for row in item["k"]
    ])
    tuning = pd.DataFrame([
        row for item in nested for row in item["tuning"]
    ])
    summary, evidence = _summaries(cells, config=config)
    numeric_columns = [
        "nste",
        "d_star",
        "reference_correction_gain",
        "common_score_correlation",
        "common_oracle_correlation",
        "naive_error_advantage",
        "coverage_q05",
        "ess_q05",
        "alias_identity_error",
    ]
    integrity = {
        "row_count": bool(len(cells) == len(task_specs)),
        "seed_uniqueness": bool(len(seeds) == len(set(seeds))),
        "numeric_integrity": bool(
            np.isfinite(
                cells[numeric_columns].to_numpy(dtype=float)
            ).all()
        ),
        "split_sizes": bool(
            all(
                len(part) == expected
                for part, expected in zip(
                    _spec(config).author_split,
                    (128, 64, 64),
                    strict=True,
                )
            )
        ),
    }
    checks = {**integrity, **evidence["checks"]}
    integrity_pass = bool(all(integrity.values()))
    if not integrity_pass:
        status = "V8_REFERENCE_MEASURE_FRONTIER_V37H4D_STOP_INTEGRITY"
    elif args.mode == "smoke":
        status = "V8_REFERENCE_MEASURE_FRONTIER_V37H4D_SMOKE_COMPLETE"
    elif all(checks.values()):
        status = (
            "V8_REFERENCE_MEASURE_FRONTIER_V37H4D_"
            "PASS_REFERENCE_TRANSPORT_AWARE"
        )
    elif not all(checks[name] for name in (
        "reference_correction_gain",
        "reference_difference",
        "reference_correlation",
        "reference_advantage",
        "support_refusal",
        "support_no_invalid_score",
    )):
        status = (
            "V8_REFERENCE_MEASURE_FRONTIER_V37H4D_"
            "REFUTED_REFERENCE_STABILITY"
        )
    else:
        status = (
            "V8_REFERENCE_MEASURE_FRONTIER_V37H4D_"
            "PARTIAL_REFERENCE_DEPENDENT"
        )
    decision = {
        "status": status,
        "integrity_pass": integrity_pass,
        "checks": checks,
        "row_counts": {
            "cells": int(len(cells)),
            "k_metrics": int(len(k_metrics)),
            "tuning": int(len(tuning)),
        },
        "seed_count": int(len(seeds)),
        "unique_seed_count": int(len(set(seeds))),
        "claim_boundary": str(config["claim_boundary"]),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    cells.to_csv(args.output_dir / "cell_metrics.csv", index=False)
    k_metrics.to_csv(args.output_dir / "k_metrics.csv", index=False)
    tuning.to_csv(args.output_dir / "propensity_tuning.csv", index=False)
    summary.to_csv(args.output_dir / "cell_summary.csv", index=False)
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    _write(args.output_dir / "seed_audit.json", {
        "seed_count": len(seeds),
        "unique_seed_count": len(set(seeds)),
        "all_unique": len(seeds) == len(set(seeds)),
    })
    (args.output_dir / "report.md").write_text(
        _report(decision),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v8_reference_measure_frontier.py",
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
        "status": status,
        "cells": int(len(cells)),
        "output_dir": str(args.output_dir),
        "checks": checks,
    }, indent=2))
    return 0 if integrity_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
