#!/usr/bin/env python3
"""Run the V8-HJIC-1B nuisance-invariance veto battery."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import UTC, datetime
import json
from pathlib import Path
import shutil
import sys
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_relational_lift_support import (  # noqa: E402
    RelationSupportSpec,
    run_relation_support_repetition,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_nuisance_invariance_veto.json"
DEFAULT_OUTPUT = (
    ROOT / "results" / "v8_nuisance_invariance_veto" / "hjic1b_20260731"
)
DEFAULT_REPORT = ROOT / "reports" / "V8_NUISANCE_INVARIANCE_VETO_REPORT.md"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _worker(
    payload: tuple[int, int, dict[str, Any]],
) -> list[dict[str, Any]]:
    repetition, seed, spec_payload = payload
    return run_relation_support_repetition(
        repetition,
        seed=seed,
        spec=RelationSupportSpec(**spec_payload),
        worlds=(
            "SHARED_LATENT",
            "NULL_HIGH_DIM_NUISANCE",
            "COMMON_NUISANCE",
            "CORRELATED_REPLICATE_ERROR",
            "LOW_SINGULAR_GAP",
            "SIMPSON_MIXTURE",
            "LOCALIZED_SIMPSON",
            "PRIVATE_AXES",
            "WEAK_RELATION",
            "COLLIDER_OR_DESCENDANT_Z",
        ),
        apply_nuisance_veto=True,
        refit_bootstrap_residualizer=True,
    )


def _rate(frame: pd.DataFrame, column: str) -> float:
    return float(frame[column].fillna(0).astype(float).mean())


def _evaluate(
    trials: pd.DataFrame,
    gates: dict[str, float],
) -> dict[str, Any]:
    by_world = {
        world: trials.loc[trials["world"].eq(world)]
        for world in trials["world"].unique()
    }
    shared = by_world["SHARED_LATENT"]
    high_dim = by_world["NULL_HIGH_DIM_NUISANCE"]
    low_gap = by_world["LOW_SINGULAR_GAP"]
    weak = by_world["WEAK_RELATION"]
    collider = by_world["COLLIDER_OR_DESCENDANT_Z"]
    simpson = pd.concat(
        [
            by_world["SIMPSON_MIXTURE"],
            by_world["LOCALIZED_SIMPSON"],
        ],
        ignore_index=True,
    )
    basic_negative = pd.concat(
        [
            by_world["COMMON_NUISANCE"],
            by_world["CORRELATED_REPLICATE_ERROR"],
            by_world["PRIVATE_AXES"],
        ],
        ignore_index=True,
    )
    positive = pd.concat([shared, high_dim], ignore_index=True)
    licensed_positive = positive.loc[positive["licensed"].eq(1)]
    fidelity_rate = (
        float(licensed_positive["truth_fidelity_pass"].mean())
        if len(licensed_positive)
        else 0.0
    )
    basic_negative_rates = (
        basic_negative.groupby("world")["licensed"].mean().to_dict()
    )
    diagnostics = {
        "shared_relation_license_rate": _rate(shared, "licensed"),
        "shared_mode_license_rate": _rate(shared, "mode_licensed"),
        "null_high_dim_relation_license_rate": _rate(
            high_dim,
            "licensed",
        ),
        "positive_world_nuisance_veto_rate": _rate(
            positive,
            "nuisance_instability",
        ),
        "licensed_positive_truth_fidelity_rate": fidelity_rate,
        "licensed_positive_count": int(len(licensed_positive)),
        "low_gap_relation_license_rate": _rate(low_gap, "licensed"),
        "low_gap_mode_license_rate": _rate(low_gap, "mode_licensed"),
        "simpson_instability_detection_rate": _rate(
            simpson,
            "nuisance_instability",
        ),
        "simpson_final_license_rate": _rate(simpson, "licensed"),
        "collider_sensitivity_detection_rate": _rate(
            collider,
            "nuisance_instability",
        ),
        "collider_final_license_rate": _rate(collider, "licensed"),
        "weak_relation_license_rate": _rate(weak, "licensed"),
        "weak_relation_nuisance_veto_rate": _rate(
            weak,
            "nuisance_instability",
        ),
        "basic_negative_license_rates": {
            key: float(value)
            for key, value in basic_negative_rates.items()
        },
        "maximum_basic_negative_license_rate": float(
            max(basic_negative_rates.values())
        ),
        "truth_usage_rate": float(
            trials["truth_used_by_license"].astype(float).mean()
        ),
    }
    checks = {
        "shared_relation": bool(
            diagnostics["shared_relation_license_rate"]
            >= gates["minimum_shared_relation_license_rate"]
        ),
        "shared_mode": bool(
            diagnostics["shared_mode_license_rate"]
            >= gates["minimum_shared_mode_license_rate"]
        ),
        "high_dim_null_safety": bool(
            diagnostics["null_high_dim_relation_license_rate"]
            >= gates["minimum_null_high_dim_relation_license_rate"]
            and diagnostics["positive_world_nuisance_veto_rate"]
            <= gates["maximum_positive_world_nuisance_veto_rate"]
        ),
        "licensed_truth_fidelity": bool(
            fidelity_rate
            >= gates["minimum_licensed_truth_fidelity_rate"]
        ),
        "basic_negative_refusal": bool(
            diagnostics["maximum_basic_negative_license_rate"]
            <= gates["maximum_negative_relation_license_rate"]
        ),
        "low_gap_relation_without_mode": bool(
            diagnostics["low_gap_relation_license_rate"]
            >= gates["minimum_low_gap_relation_license_rate"]
            and diagnostics["low_gap_mode_license_rate"]
            <= gates["maximum_low_gap_mode_license_rate"]
        ),
        "simpson_veto": bool(
            diagnostics["simpson_instability_detection_rate"]
            >= gates["minimum_simpson_detection_rate"]
            and diagnostics["simpson_final_license_rate"]
            <= gates["maximum_simpson_final_license_rate"]
        ),
        "collider_sensitivity_veto": bool(
            diagnostics["collider_sensitivity_detection_rate"]
            >= gates["minimum_collider_sensitivity_detection_rate"]
            and diagnostics["collider_final_license_rate"]
            <= gates["maximum_collider_final_license_rate"]
        ),
        "weak_relation_classification": bool(
            diagnostics["weak_relation_license_rate"]
            <= gates["maximum_weak_relation_license_rate"]
            and diagnostics["weak_relation_nuisance_veto_rate"]
            <= gates["maximum_weak_relation_nuisance_veto_rate"]
        ),
        "truth_isolation": bool(
            diagnostics["truth_usage_rate"]
            <= gates["maximum_truth_usage_rate"]
        ),
    }
    return {
        "checks": checks,
        "diagnostics": diagnostics,
        "all_pass": bool(all(checks.values())),
    }


def _summary(trials: pd.DataFrame) -> pd.DataFrame:
    return (
        trials.groupby("world", as_index=False)
        .agg(
            relation_license_rate=("licensed", "mean"),
            mode_license_rate=("mode_licensed", "mean"),
            nuisance_veto_rate=("nuisance_instability", "mean"),
            support_failure_rate=("support_failure", "mean"),
            mean_truth_fidelity=("truth_fidelity", "mean"),
        )
    )


def _report(
    decision: dict[str, Any],
    summary: pd.DataFrame,
    claim_boundary: str,
) -> str:
    diagnostics = decision["diagnostics"]
    lines = [
        "# V8-HJIC-1B Nuisance-Invariance Veto Report",
        "",
        f"Status: `{decision['status']}`",
        "",
        "HJIC-1A remains preserved as a partial result. This follow-up tests "
        "whether a material, permutation-supported raw-versus-conditioned "
        "relation shift can veto an otherwise stable global relation.",
        "",
        "## World summary",
        "",
        summary.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Diagnostics",
        "",
        f"- Shared relation/mode license: "
        f"{diagnostics['shared_relation_license_rate']:.4f} / "
        f"{diagnostics['shared_mode_license_rate']:.4f}.",
        f"- High-dimensional-null relation license: "
        f"{diagnostics['null_high_dim_relation_license_rate']:.4f}; "
        f"positive-world nuisance veto: "
        f"{diagnostics['positive_world_nuisance_veto_rate']:.4f}.",
        f"- Licensed positive truth fidelity: "
        f"{diagnostics['licensed_positive_truth_fidelity_rate']:.4f} "
        f"(n={diagnostics['licensed_positive_count']}).",
        f"- Low-gap relation/mode license: "
        f"{diagnostics['low_gap_relation_license_rate']:.4f} / "
        f"{diagnostics['low_gap_mode_license_rate']:.4f}.",
        f"- Simpson detection/final license: "
        f"{diagnostics['simpson_instability_detection_rate']:.4f} / "
        f"{diagnostics['simpson_final_license_rate']:.4f}.",
        f"- Collider sensitivity/final license: "
        f"{diagnostics['collider_sensitivity_detection_rate']:.4f} / "
        f"{diagnostics['collider_final_license_rate']:.4f}.",
        f"- Weak relation final license/nuisance veto: "
        f"{diagnostics['weak_relation_license_rate']:.4f} / "
        f"{diagnostics['weak_relation_nuisance_veto_rate']:.4f}.",
        "",
        "## Gates",
        "",
    ]
    lines.extend(
        f"- `{key}`: {'PASS' if value else 'FAIL'}"
        for key, value in decision["checks"].items()
    )
    lines.extend([
        "",
        "## Ruling",
        "",
        "Condition sensitivity is a veto on a global invariant relation, not "
        "evidence that conditioning recovered causal truth. Weak relations, "
        "unique-mode failure, and nuisance sensitivity remain distinct refusal "
        "types.",
        "",
        f"Claim boundary: {claim_boundary}",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--jobs", type=int)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    config_path = args.config.resolve()
    config = _read_json(config_path)
    repetitions = int(args.repetitions or config["repetitions"])
    jobs = int(args.jobs or config["jobs"])
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    write_run_manifest(
        output / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=config_path,
        code_paths=[
            Path(__file__).resolve(),
            ROOT / "suica_core" / "v8_relational_lift_support.py",
        ],
        estimand_id=str(config["estimand_id"]),
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )

    payloads = [
        (repetition, int(config["seed"]), dict(config["spec"]))
        for repetition in range(repetitions)
    ]
    if jobs == 1:
        outputs = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as pool:
            outputs = list(pool.map(_worker, payloads))
    trials = pd.DataFrame(
        row
        for output in outputs
        for row in output
    )
    trials.to_csv(output / "nuisance_invariance_trials.csv", index=False)
    evaluated = _evaluate(trials, dict(config["gates"]))
    status = (
        "V8_HJIC1B_NUISANCE_INVARIANCE_VETO_PASS"
        if evaluated["all_pass"]
        else "V8_HJIC1B_NUISANCE_INVARIANCE_VETO_PARTIAL"
    )
    decision = {
        "version": str(config["version"]),
        "estimand_id": str(config["estimand_id"]),
        "status": status,
        "completed_utc": datetime.now(UTC).isoformat(),
        "repetitions": repetitions,
        "external_labels_read": False,
        **evaluated,
        "claim_boundary": str(config["claim_boundary"]),
    }
    _write_json(output / "decision.json", decision)
    summary = _summary(trials)
    summary.to_csv(output / "world_summary.csv", index=False)
    report = _report(decision, summary, str(config["claim_boundary"]))
    (output / "REPORT.md").write_text(report, encoding="utf-8")
    args.report.resolve().parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(output / "REPORT.md", args.report.resolve())
    write_artifact_inventory(
        output,
        output / "artifact_inventory.json",
        exclude_relative_paths=("artifact_inventory.json",),
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
