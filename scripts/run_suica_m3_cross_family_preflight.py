#!/usr/bin/env python3
"""Run power-only M3 cross-family worlds before any confirmation seal."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.m3_cross_family_audit import (  # noqa: E402
    audit_m3_cross_family,
)
from suica_core.m3_cross_family_estimator import (  # noqa: E402
    fit_m3_cross_family,
)
from suica_core.m3_cross_family_generator import (  # noqa: E402
    M3CrossFamilySpec,
    generate_m3_cross_family_world,
)
from suica_core.m3_cross_family_validity import (  # noqa: E402
    audit_m3_cross_family_validity,
)
from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)


CODE_PATHS = (
    ROOT / "suica_core" / "m3_cross_family_contracts.py",
    ROOT / "suica_core" / "m3_cross_family_generator.py",
    ROOT / "suica_core" / "m3_cross_family_estimator.py",
    ROOT / "suica_core" / "m3_cross_family_audit.py",
    ROOT / "suica_core" / "m3_cross_family_validity.py",
    Path(__file__).resolve(),
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _seed(root: int, repetition: int, world_index: int) -> int:
    return int(root + repetition * 1_000_003 + world_index * 10_007)


def _estimator_seed(root: int, repetition: int, world_index: int) -> int:
    label = f"estimator::{repetition}::{world_index}".encode()
    digest = hmac.new(str(root).encode(), label, hashlib.sha256).digest()
    return int.from_bytes(digest[:8], "big") % (2**63 - 1)


def _validity_pass(
    validity: dict[str, float | bool | str],
    gates: dict[str, float],
) -> bool:
    if not bool(validity.get("finite", False)):
        return False
    maximums = {
        "density_normalization_max_error": gates.get(
            "maximum_density_normalization_error",
            1e-10,
        ),
        "moment_tensor_degree4_max_author_range": gates.get(
            "maximum_moment_tensor_error",
            1e-9,
        ),
        "poly3_projection_ratio_max": gates.get(
            "maximum_poly3_projection_ratio",
            1e-10,
        ),
        "nuisance_sum_to_zero_max_error": gates.get(
            "maximum_nuisance_constraint_error",
            1e-10,
        ),
        "actor_dyad_overlap_max": 0.0,
        "theoretical_lag02_max_author_range": gates.get(
            "maximum_theoretical_lag02_range",
            1e-12,
        ),
        "renewal_mean_dwell_max_error": 1e-12,
        "renewal_singleton_probability_max_error": 1e-12,
        "cycle_row_sum_max_error": 1e-12,
        "cycle_uniform_stationarity_max_error": 1e-12,
        "cycle_transpose_pair_max_error": 1e-12,
        "alias_on_support_basis_max_abs": 0.0,
    }
    for key, maximum in maximums.items():
        if key in validity and float(validity[key]) > maximum:
            return False
    if (
        "density_relative_minimum" in validity
        and float(validity["density_relative_minimum"])
        < gates.get("minimum_density", 0.05)
    ):
        return False
    for key in (
        "same_partner_population",
        "all_partners_covered",
        "actor_partner_graph_connected",
    ):
        if key in validity and not bool(validity[key]):
            return False
    if (
        "actor_partner_incidence_rank" in validity
        and validity["actor_partner_incidence_rank"]
        != validity["actor_partner_incidence_expected_rank"]
    ):
        return False
    return True


def _run(config: dict[str, Any]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for repetition in range(int(config["repetitions"])):
        for world_index, (world, declaration) in enumerate(
            config["worlds"].items()
        ):
            seed = _seed(int(config["seed"]), repetition, world_index)
            if isinstance(declaration, str):
                spec_values = dict(config["specs"][declaration])
            else:
                spec_values = dict(config["specs"][declaration["spec"]])
                if "events" in declaration:
                    spec_values["events"] = int(declaration["events"])
            spec = M3CrossFamilySpec(**spec_values)
            observed, truth = generate_m3_cross_family_world(
                world=world,
                spec=spec,
                seed=seed,
            )
            estimate = fit_m3_cross_family(
                observed,
                seed=_estimator_seed(
                    int(config["seed"]),
                    repetition,
                    world_index,
                ),
                **config["estimator"],
            )
            recomputed_validity = audit_m3_cross_family_validity(
                observed,
                truth,
            )
            validity_pass = _validity_pass(
                recomputed_validity,
                config["preflight_gates"],
            )
            main_rows = audit_m3_cross_family(estimate, truth)
            knockout_by_target: dict[str, float] = {}
            if not truth.exact_alias:
                for target in truth.active_targets:
                    knocked, _ = generate_m3_cross_family_world(
                        world=world,
                        spec=spec,
                        seed=seed,
                        disabled=frozenset({target}),
                    )
                    knocked_estimate = fit_m3_cross_family(
                        knocked,
                        seed=_estimator_seed(
                            int(config["seed"]),
                            repetition,
                            world_index,
                        ),
                        **config["estimator"],
                    )
                    knocked_rows = audit_m3_cross_family(
                        knocked_estimate,
                        truth,
                    )
                    target_row = next(
                        row for row in knocked_rows
                        if row["target"] == target
                    )
                    knockout_by_target[target] = float(
                        target_row["expected_geometry"]
                    )
            for row in main_rows:
                target = str(row["target"])
                rows.append({
                    "repetition": repetition,
                    "seed": seed,
                    "validity_pass": validity_pass,
                    "validity_json": json.dumps(
                        recomputed_validity,
                        sort_keys=True,
                    ),
                    "knockout_geometry": knockout_by_target.get(
                        target,
                        float("nan"),
                    ),
                    **row,
                })
    return pd.DataFrame(rows)


def _decision(
    metrics: pd.DataFrame,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    gates = config["preflight_gates"]
    positive = metrics[
        (metrics["target"] != "null")
        & (~metrics["exact_alias"])
    ]
    summary = positive.groupby(
        ["world", "target"],
        as_index=False,
    ).agg(
        seeds=("seed", "nunique"),
        validity_fraction=("validity_pass", "mean"),
        refusal_max=("refusal_count", "max"),
        expected_auc=("expected_auc", "mean"),
        cheap_auc=("cheap_auc", "mean"),
        expected_geometry=("expected_geometry", "mean"),
        cheap_geometry=("cheap_geometry", "mean"),
        heldout_increment=("heldout_increment", "mean"),
        positive_increment_fraction=(
            "heldout_increment",
            lambda values: float(np.mean(np.asarray(values) > 0.0)),
        ),
        off_target_geometry=(
            "off_target_geometry",
            lambda values: float(np.nanmean(np.abs(values)))
            if np.any(np.isfinite(values))
            else float("nan"),
        ),
        knockout_geometry=(
            "knockout_geometry",
            lambda values: float(np.nanmean(np.abs(values)))
            if np.any(np.isfinite(values))
            else float("nan"),
        ),
    )
    checks: dict[str, bool] = {}
    diagnostics: dict[str, Any] = {}
    for row in summary.to_dict(orient="records"):
        key = f"{row['world']}::{row['target']}"
        target_gates = {
            **gates,
            **gates.get("target_overrides", {}).get(
                str(row["target"]),
                {},
            ),
        }
        world_checks = {
            "valid": float(row["validity_fraction"]) == 1.0,
            "no_refusal": int(row["refusal_max"]) == 0,
            "auc": float(row["expected_auc"])
            >= target_gates["minimum_expected_auc"],
            "geometry": float(row["expected_geometry"])
            >= target_gates["minimum_expected_geometry"],
            "increment": float(row["heldout_increment"]) > 0.0,
            "increment_fraction": float(row["positive_increment_fraction"])
            >= target_gates["minimum_positive_increment_fraction"],
            "cheap_chance": abs(float(row["cheap_auc"]) - 0.5)
            <= target_gates["maximum_cheap_auc_deviation"],
            "knockout": float(row["knockout_geometry"])
            <= target_gates["maximum_knockout_geometry"],
        }
        if np.isfinite(row["off_target_geometry"]):
            world_checks["cross_talk"] = (
                float(row["off_target_geometry"])
                <= target_gates["maximum_off_target_geometry"]
            )
        checks[key] = all(world_checks.values())
        diagnostics[key] = {
            "checks": world_checks,
            **row,
        }

    alias = metrics[metrics["exact_alias"]]
    for (world, target), frame in alias.groupby(["world", "target"]):
        alias_auc = float(frame["expected_auc"].mean())
        alias_geometry = float(np.nanmean(np.abs(frame["expected_geometry"])))
        key = f"{world}::{target}"
        alias_checks = {
            "valid": bool(frame["validity_pass"].all()),
            "no_refusal": int(frame["refusal_count"].max()) == 0,
            "auc_chance": abs(alias_auc - 0.5)
            <= gates["maximum_alias_auc_deviation"],
            "geometry_zero": alias_geometry
            <= gates["maximum_alias_geometry"],
        }
        checks[key] = all(alias_checks.values())
        diagnostics[key] = {
            "checks": alias_checks,
            "expected_auc": alias_auc,
            "expected_geometry_abs": alias_geometry,
        }

    null = metrics[metrics["target"] == "null"]
    null_by_family = null.groupby("expected_family")["expected_auc"].mean()
    null_max_deviation = float(np.max(np.abs(null_by_family - 0.5)))
    null_checks = {
        "valid": bool(null["validity_pass"].all()),
        "no_refusal": int(null["refusal_count"].max()) == 0,
        "auc_chance": null_max_deviation
        <= gates["maximum_null_auc_deviation"],
    }
    checks["null_calibration"] = all(null_checks.values())
    diagnostics["null_calibration"] = {
        "checks": null_checks,
        "maximum_auc_deviation": null_max_deviation,
        "by_family": {
            str(key): float(value)
            for key, value in null_by_family.items()
        },
    }
    decision = (
        config.get(
            "ready_decision",
            "M3_CROSS_FAMILY_PREFLIGHT_POWER_READY",
        )
        if all(checks.values())
        else config.get(
            "partial_decision",
            "M3_CROSS_FAMILY_PREFLIGHT_PARTIAL",
        )
    )
    return summary, {
        "estimand_id": config["estimand_id"],
        "decision": decision,
        "checks": checks,
        "diagnostics": diagnostics,
        "confirmation_sealed": False,
        "claim_boundary": (
            "Development-seed synthetic power preflight only. No sealed "
            "confirmation, human-text, personality, or clinical claim."
        ),
    }


def _report(
    summary: pd.DataFrame,
    decision: dict[str, Any],
) -> str:
    failed = [
        key for key, value in decision["checks"].items()
        if not value
    ]
    failures = "\n".join(f"- `{item}`" for item in failed) or "- None"
    return f"""# SUICA M3 Cross-Family Power Preflight

Decision: `{decision["decision"]}`

## Purpose

This development-seed run asks whether one generator-blind estimator suite has
enough power to justify an artifact-sealed fresh-seed confirmation. Failure is
a power or specification finding, not evidence against human personality.

## Target summary

{summary.to_markdown(index=False)}

## Gates not yet satisfied

{failures}

## Boundary

No confirmation truth was sealed or opened. Hyperparameters may still change
only in this preflight branch. Human text, psychological constructs, and
clinical use remain outside scope.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m3_cross_family_preflight.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results" / "m3_cross_family_preflight",
    )
    args = parser.parse_args()
    config = _load(args.config)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    metrics = _run(config)
    summary, decision = _decision(metrics, config)
    metrics.to_csv(args.output_dir / "metrics.csv", index=False)
    summary.to_csv(args.output_dir / "summary.csv", index=False)
    (args.output_dir / "config.snapshot.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = _report(summary, decision)
    report_path = ROOT / config.get(
        "report_path",
        "reports/SUICA_M3_CROSS_FAMILY_PREFLIGHT.md",
    )
    report_path.write_text(report, encoding="utf-8")
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=(),
        config_path=args.config,
        code_paths=CODE_PATHS,
        estimand_id=config["estimand_id"],
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
        exclude_relative_paths=("artifact_inventory.json",),
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
