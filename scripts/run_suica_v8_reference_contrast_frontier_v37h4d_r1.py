#!/usr/bin/env python3
"""Run the gauge-invariant V3.7H.4D R1 reference-contrast frontier."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v8_reference_measure_frontier_v37h4d import (  # noqa: E402
    _clopper,
    _mean_interval,
    _read,
    _score_at_k,
    _select_pseudocount,
    _spec,
    _write,
)
from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_reference_measure_frontier import (  # noqa: E402
    additive_residual,
    condition_profile,
    contrast_bootstrap_interval,
    correlation,
    fit_propensity,
    predict_propensity,
    reference_score,
    score_panel,
    simulate_reference_world,
    wild_residual_diagnostics,
)


DEFAULT_CONFIG = (
    ROOT / "configs/v8_reference_contrast_frontier_v37h4d_r1.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_reference_contrast_frontier"
    / "v37h4d_r1_discovery"
)


def _cell_definitions(
    config: dict[str, Any],
    *,
    mode: str,
) -> list[dict[str, Any]]:
    main_worlds = [
        "reference_shift",
        "contrast_sensitive",
        "contrast_kernel",
        "support_violation",
        "full_rank",
        "minority_local",
        "aq_alias",
    ]
    boundary_worlds = [
        "reference_shift",
        "contrast_sensitive",
        "contrast_kernel",
        "support_violation",
        "full_rank",
        "minority_local",
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
                "reference_jsd": float(config["main_reference_jsd"]),
                "support_coverage": 1.0,
            })
        for world in main_worlds:
            definitions.append({
                "world": world,
                "cell_kind": "main",
                "noise_mode": "gaussian",
                "repetitions": repetitions,
                "effect_share": float(config["main_effect_share"]),
                "reference_jsd": float(config["main_reference_jsd"]),
                "support_coverage": (
                    float(config["main_support_coverage"])
                    if world == "support_violation"
                    else 1.0
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
            "reference_jsd": float(config["main_reference_jsd"]),
            "support_coverage": 1.0,
        })
        for world in main_worlds:
            definitions.append({
                "world": world,
                "cell_kind": "main",
                "noise_mode": str(noise),
                "repetitions": int(config["main_repetitions"]),
                "effect_share": float(config["main_effect_share"]),
                "reference_jsd": float(config["main_reference_jsd"]),
                "support_coverage": (
                    float(config["main_support_coverage"])
                    if world == "support_violation"
                    else 1.0
                ),
            })
    for world in boundary_worlds:
        definitions.append({
            "world": world,
            "cell_kind": "boundary",
            "noise_mode": "gaussian",
            "repetitions": int(config["boundary_repetitions"]),
            "effect_share": float(config["boundary_effect_share"]),
            "reference_jsd": float(config["boundary_reference_jsd"]),
            "support_coverage": (
                float(config["boundary_support_coverage"])
                if world == "support_violation"
                else 1.0
            ),
        })
    return definitions


def _contrast_scores(
    world: dict[str, Any],
    *,
    opportunities: int,
    pseudocount: float,
    config: dict[str, Any],
) -> dict[str, Any]:
    spec = _spec(config)
    train, _, test = spec.author_split
    counts = world["counts_by_k"][int(opportunities)]
    means = world["means_by_k"][int(opportunities)]
    profile = condition_profile(means, train)
    coefficients = fit_propensity(
        counts,
        world["author_covariate"],
        train,
        pseudocount=pseudocount,
    )
    propensity = {
        environment: predict_propensity(
            coefficients,
            world["author_covariate"],
            environment=environment,
        )
        for environment in (0, 1)
    }
    references = [
        world["contrast_reference_0"],
        world["contrast_reference_1"],
    ]
    panel_scores: dict[int, list[dict[str, np.ndarray]]] = {}
    uniform_scores: dict[int, dict[str, np.ndarray]] = {}
    for panel in (2, 3):
        environment = panel % 2
        panel_scores[panel] = [
            score_panel(
                counts[panel],
                means[panel],
                propensity[environment],
                profile,
                reference,
                test,
            )
            for reference in references
        ]
        uniform_scores[panel] = score_panel(
            counts[panel],
            means[panel],
            propensity[environment],
            profile,
            world["reference"],
            test,
        )
    delta_left = (
        panel_scores[2][1]["common"]
        - panel_scores[2][0]["common"]
    )
    delta_right = (
        panel_scores[3][1]["common"]
        - panel_scores[3][0]["common"]
    )
    bootstrap = contrast_bootstrap_interval(
        delta_left,
        delta_right,
        uniform_scores[2]["common"],
        uniform_scores[3]["common"],
        seed=int(config["_active_contrast_seed"]),
        draws=int(config["_active_contrast_bootstrap"]),
    )
    oracle_left = reference_score(
        world["cell_truth"],
        references[0],
    )[test]
    oracle_right = reference_score(
        world["cell_truth"],
        references[1],
    )[test]
    oracle_delta = oracle_right - oracle_left
    estimated_delta = 0.5 * (delta_left + delta_right)
    oracle_scale = max(
        float(np.std(world["theta_star"][test])),
        1e-12,
    )
    bootstrap.update({
        "contrast_oracle_correlation": correlation(
            estimated_delta,
            oracle_delta,
        ),
        "contrast_oracle_nrmse": float(
            np.sqrt(np.mean((estimated_delta - oracle_delta) ** 2))
            / oracle_scale
        ),
        "oracle_d_contrast": float(
            np.sqrt(np.mean(oracle_delta**2)) / oracle_scale
        ),
    })
    return bootstrap


def _evaluate(
    *,
    definition: dict[str, Any],
    repetition: int,
    world_seed: int,
    diagnostic_seed: int,
    contrast_seed: int,
    config: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    spec = _spec(config)
    world = simulate_reference_world(
        seed=world_seed,
        world=str(definition["world"]),
        effect_share=float(definition["effect_share"]),
        reference_jsd=float(definition["reference_jsd"]),
        support_coverage=float(definition["support_coverage"]),
        near_kernel_fraction=0.02,
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
        acquisition_reference_shift=True,
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
    primary = _score_at_k(
        world,
        opportunities=primary_k,
        pseudocount=pseudocount,
        spec=spec,
    )
    config["_active_contrast_seed"] = int(contrast_seed)
    contrast = _contrast_scores(
        world,
        opportunities=primary_k,
        pseudocount=pseudocount,
        config=config,
    )

    diagnostics = {
        "crc": float("nan"),
        "crc_p": float("nan"),
        "crc_p_holm": float("nan"),
        "cross_low_rank_ratio": float("nan"),
        "cross_low_rank_p": float("nan"),
        "cross_low_rank_p_holm": float("nan"),
        "hc": float("nan"),
        "hc_p": float("nan"),
        "hc_p_holm": float("nan"),
        "structure_detected": False,
        "non_low_rank_detected": False,
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
        diagnostics = wild_residual_diagnostics(
            left,
            right,
            left_mask,
            right_mask,
            rank=3,
            seed=diagnostic_seed,
            permutations=int(config["_active_permutations"]),
            alpha=float(config["holm_alpha"]),
        )

    world_name = str(definition["world"])
    if bool(primary["refuse_nonoverlap"]):
        classification = "REFUSE_NONOVERLAP"
    elif world_name == "aq_alias":
        classification = "CAUSE_UNIDENTIFIED_AQ"
    elif diagnostics["structure_detected"]:
        if (
            contrast["d_contrast_upper_90"]
            < float(config["near_contrast_upper"])
        ):
            classification = (
                "STRUCTURE_DETECTED_REFERENCE_CONTRAST_NEAR_KERNEL"
            )
        elif (
            contrast["d_contrast_lower_95"]
            > float(config["sensitive_contrast_lower"])
        ):
            classification = (
                "STRUCTURE_DETECTED_REFERENCE_SENSITIVE"
            )
        else:
            classification = (
                "STRUCTURE_DETECTED_REFERENCE_EFFECT_UNRESOLVED"
            )
    elif (
        contrast["d_contrast_upper_90"]
        < float(config["near_contrast_upper"])
    ):
        classification = "NO_STRUCTURE_REFERENCE_STABLE"
    else:
        classification = "NO_STRUCTURE_REFERENCE_EFFECT_UNRESOLVED"

    row = {
        "repetition": int(repetition),
        "world": world_name,
        "cell_kind": str(definition["cell_kind"]),
        "noise_mode": str(definition["noise_mode"]),
        "effect_share": float(definition["effect_share"]),
        "reference_jsd": float(definition["reference_jsd"]),
        "support_coverage": float(definition["support_coverage"]),
        "world_seed": int(world_seed),
        "diagnostic_seed": int(diagnostic_seed),
        "contrast_seed": int(contrast_seed),
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
        **contrast,
        "classification": classification,
        "reference_sensitive_correct": bool(
            world_name == "contrast_sensitive"
            and classification
            == "STRUCTURE_DETECTED_REFERENCE_SENSITIVE"
        ),
        "contrast_kernel_correct": bool(
            world_name == "contrast_kernel"
            and classification
            == "STRUCTURE_DETECTED_REFERENCE_CONTRAST_NEAR_KERNEL"
        ),
        "false_reference_sensitive": bool(
            world_name in {"additive", "contrast_kernel"}
            and classification
            == "STRUCTURE_DETECTED_REFERENCE_SENSITIVE"
        ),
        "cause_unidentified": bool(
            world_name == "aq_alias"
            and classification == "CAUSE_UNIDENTIFIED_AQ"
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
    return row, tuning_rows


def _worker(
    payload: tuple[
        dict[str, Any],
        dict[str, Any],
        int,
        int,
        int,
        int,
    ],
) -> dict[str, Any]:
    config, definition, repetition, world_seed, diagnostic_seed, contrast_seed = (
        payload
    )
    row, tuning = _evaluate(
        definition=definition,
        repetition=repetition,
        world_seed=world_seed,
        diagnostic_seed=diagnostic_seed,
        contrast_seed=contrast_seed,
        config=config,
    )
    return {
        "cell": row,
        "tuning": tuning,
        "seeds": [world_seed, diagnostic_seed, contrast_seed],
    }


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
    ]
    rows = []
    rate_columns = {
        "detection": "structure_detected",
        "non_low_rank_detection": "non_low_rank_detected",
        "overlap_refusal": "refuse_nonoverlap",
        "invalid_score": "invalid_formal_score",
        "reference_sensitive_correct": "reference_sensitive_correct",
        "contrast_kernel_correct": "contrast_kernel_correct",
        "false_reference_sensitive": "false_reference_sensitive",
        "cause_unidentified": "cause_unidentified",
        "specific_attribution": "specific_aq_attribution",
    }
    metric_columns = {
        "nste": "nste",
        "d_star": "d_star",
        "reference_correction_gain": "reference_correction_gain",
        "common_score_correlation": "common_score_correlation",
        "naive_error_advantage": "naive_error_advantage",
        "d_contrast": "d_contrast",
        "contrast_split_correlation": "contrast_split_correlation",
        "contrast_oracle_nrmse": "contrast_oracle_nrmse",
    }
    for key, group in cells.groupby(keys, sort=True, observed=True):
        base = dict(zip(keys, key, strict=True))
        trials = len(group)
        alpha = (
            float(config["family_tail_alpha"])
            if base["cell_kind"] == "w0"
            else 0.05
        )
        rates = {}
        for name, column in rate_columns.items():
            count = int(group[column].sum())
            lower, upper = _clopper(
                count,
                trials,
                tail_alpha=alpha,
            )
            rates[name] = (count, lower, upper)
        metrics = {
            name: _mean_interval(
                group[column],
                family_cells=4,
            )
            for name, column in metric_columns.items()
        }
        rows.append({
            **base,
            "trials": int(trials),
            **{
                f"{name}_count": values[0]
                for name, values in rates.items()
            },
            **{
                f"{name}_lower": values[1]
                for name, values in rates.items()
            },
            **{
                f"{name}_upper": values[2]
                for name, values in rates.items()
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
    sensitive = main[main["world"] == "contrast_sensitive"]
    kernel = main[main["world"] == "contrast_kernel"]
    support = main[main["world"] == "support_violation"]
    full_rank = main[main["world"] == "full_rank"]
    minority = main[main["world"] == "minority_local"]
    alias = main[main["world"] == "aq_alias"]
    gates = config["gates"]
    checks = {
        "w0_detector_calibration": bool(
            len(w0)
            and w0["detection_upper"].max()
            < float(gates["maximum_w0_false_refusal_upper"])
        ),
        "w0_no_false_sensitive": bool(
            len(w0)
            and w0["false_reference_sensitive_upper"].max()
            < float(gates["maximum_w0_false_sensitive_upper"])
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
        "sensitive_detection": bool(
            len(sensitive)
            and sensitive["detection_lower"].min()
            > float(gates["minimum_strong_detection_lower"])
        ),
        "sensitive_classification": bool(
            len(sensitive)
            and sensitive[
                "reference_sensitive_correct_lower"
            ].min()
            > float(gates["minimum_contrast_classification_lower"])
        ),
        "kernel_detection": bool(
            len(kernel)
            and kernel["detection_lower"].min()
            > float(gates["minimum_strong_detection_lower"])
        ),
        "kernel_classification": bool(
            len(kernel)
            and kernel["contrast_kernel_correct_lower"].min()
            > float(gates["minimum_contrast_classification_lower"])
        ),
        "kernel_no_false_sensitive": bool(
            len(kernel)
            and kernel["false_reference_sensitive_upper"].max()
            < float(gates["maximum_contrast_false_sensitive_upper"])
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
    return f"""# V8 V3.7H.4D R1 Reference-Contrast Frontier

Decision: `{decision["status"]}`

## Checks

```json
{json.dumps(decision["checks"], indent=2)}
```

## Boundary

This is a synthetic gauge-invariant reference-contrast experiment. Absolute
A/Q allocation, real-text validity, psychological meaning, diagnosis,
clinical use, and causal attribution remain closed.
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
    config["_active_contrast_bootstrap"] = (
        int(config["smoke_contrast_bootstrap"])
        if args.mode == "smoke"
        else int(config["contrast_bootstrap"])
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
    streams = root.spawn(3 * len(task_specs))
    seeds = [
        int(stream.generate_state(1, dtype=np.uint64)[0])
        for stream in streams
    ]
    payloads = [
        (
            config,
            definition,
            repetition,
            seeds[3 * index],
            seeds[3 * index + 1],
            seeds[3 * index + 2],
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
    tuning = pd.DataFrame([
        row for item in nested for row in item["tuning"]
    ])
    summary, evidence = _summaries(cells, config=config)
    numeric_columns = [
        "nste",
        "d_star",
        "reference_correction_gain",
        "common_score_correlation",
        "d_contrast",
        "d_contrast_lower_95",
        "d_contrast_upper_90",
        "contrast_split_correlation",
        "contrast_oracle_nrmse",
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
    }
    checks = {**integrity, **evidence["checks"]}
    integrity_pass = bool(all(integrity.values()))
    reference_core = all(checks[name] for name in (
        "reference_correction_gain",
        "reference_difference",
        "reference_correlation",
        "support_refusal",
        "support_no_invalid_score",
    ))
    if not integrity_pass:
        status = (
            "V8_REFERENCE_CONTRAST_FRONTIER_V37H4D_R1_"
            "STOP_INTEGRITY"
        )
    elif args.mode == "smoke":
        status = (
            "V8_REFERENCE_CONTRAST_FRONTIER_V37H4D_R1_"
            "SMOKE_COMPLETE"
        )
    elif all(checks.values()):
        status = (
            "V8_REFERENCE_CONTRAST_FRONTIER_V37H4D_R1_"
            "PASS_REFERENCE_CONTRAST_AWARE"
        )
    elif not reference_core:
        status = (
            "V8_REFERENCE_CONTRAST_FRONTIER_V37H4D_R1_"
            "REFUTED_REFERENCE_STABILITY"
        )
    else:
        status = (
            "V8_REFERENCE_CONTRAST_FRONTIER_V37H4D_R1_"
            "PARTIAL_REFERENCE_CONTRAST"
        )
    decision = {
        "status": status,
        "integrity_pass": integrity_pass,
        "checks": checks,
        "row_counts": {
            "cells": int(len(cells)),
            "tuning": int(len(tuning)),
        },
        "seed_count": int(len(seeds)),
        "unique_seed_count": int(len(set(seeds))),
        "claim_boundary": str(config["claim_boundary"]),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    cells.to_csv(args.output_dir / "cell_metrics.csv", index=False)
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
            ROOT
            / "scripts/run_suica_v8_reference_measure_frontier_v37h4d.py",
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
