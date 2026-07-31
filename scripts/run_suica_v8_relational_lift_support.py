#!/usr/bin/env python3
"""Run V8-HJIC-1A replicated relational-lift support experiments."""
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


DEFAULT_CONFIG = ROOT / "configs" / "v8_relational_lift_support.json"
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_relational_lift_support"
    / "hjic1a_20260730"
)
DEFAULT_REPORT = ROOT / "reports" / "V8_RELATIONAL_LIFT_SUPPORT_REPORT.md"


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
            "COMMON_NUISANCE",
            "CORRELATED_REPLICATE_ERROR",
            "LOW_SINGULAR_GAP",
            "SIMPSON_MIXTURE",
            "PRIVATE_AXES",
        ),
        apply_nuisance_veto=False,
        refit_bootstrap_residualizer=False,
    )


def _evaluate(
    trials: pd.DataFrame,
    gates: dict[str, float],
) -> dict[str, Any]:
    shared = trials.loc[trials["world"].eq("SHARED_LATENT")]
    low_gap = trials.loc[trials["world"].eq("LOW_SINGULAR_GAP")]
    negative = trials.loc[
        trials["world"].isin(
            (
                "COMMON_NUISANCE",
                "CORRELATED_REPLICATE_ERROR",
                "SIMPSON_MIXTURE",
                "PRIVATE_AXES",
            )
        )
    ]
    licensed_shared = shared.loc[shared["licensed"].eq(1)]
    fidelity_rate = (
        float(licensed_shared["truth_fidelity_pass"].mean())
        if len(licensed_shared)
        else 0.0
    )
    negative_rates = (
        negative.groupby("world")["licensed"].mean().to_dict()
    )
    diagnostics = {
        "shared_relation_license_rate": float(shared["licensed"].mean()),
        "shared_mode_license_rate": float(shared["mode_licensed"].mean()),
        "licensed_shared_truth_fidelity_rate": fidelity_rate,
        "licensed_shared_count": int(len(licensed_shared)),
        "shared_mean_individual_correlation": float(
            shared["mean_individual_correlation"].mean()
        ),
        "low_gap_relation_license_rate": float(
            low_gap["licensed"].mean()
        ),
        "low_gap_mode_license_rate": float(
            low_gap["mode_licensed"].mean()
        ),
        "negative_relation_license_rates": {
            key: float(value)
            for key, value in negative_rates.items()
        },
        "maximum_negative_relation_license_rate": float(
            max(negative_rates.values())
        ),
        "truth_usage_rate": float(
            trials["truth_used_by_license"].astype(float).mean()
        ),
    }
    checks = {
        "shared_relation_nonvacuity": bool(
            diagnostics["shared_relation_license_rate"]
            >= gates["minimum_shared_relation_license_rate"]
        ),
        "shared_mode_identification": bool(
            diagnostics["shared_mode_license_rate"]
            >= gates["minimum_shared_mode_license_rate"]
        ),
        "licensed_relation_fidelity": bool(
            fidelity_rate
            >= gates["minimum_licensed_truth_fidelity_rate"]
        ),
        "negative_world_refusal": bool(
            diagnostics["maximum_negative_relation_license_rate"]
            <= gates["maximum_negative_relation_license_rate"]
        ),
        "low_gap_relation_identification": bool(
            diagnostics["low_gap_relation_license_rate"]
            >= gates["minimum_low_gap_relation_license_rate"]
        ),
        "low_gap_mode_refusal": bool(
            diagnostics["low_gap_mode_license_rate"]
            <= gates["maximum_low_gap_mode_license_rate"]
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


def _summary_table(trials: pd.DataFrame) -> pd.DataFrame:
    return (
        trials.groupby("world", as_index=False)
        .agg(
            relation_license_rate=("licensed", "mean"),
            mode_license_rate=("mode_licensed", "mean"),
            support_failure_rate=("support_failure", "mean"),
            mean_truth_fidelity=("truth_fidelity", "mean"),
            mean_individual_correlation=(
                "mean_individual_correlation",
                "mean",
            ),
        )
    )


def _build_report(
    *,
    decision: dict[str, Any],
    repetitions: int,
    summary: pd.DataFrame,
    claim_boundary: str,
) -> str:
    diagnostics = decision["diagnostics"]
    lines = [
        "# V8-HJIC-1A Relational-Lift Support Report",
        "",
        f"Status: `{decision['status']}`",
        "",
        "## Scope",
        "",
        "This synthetic battery asks when independent replicated text views "
        "license a cross-family relation and when they license a unique "
        "dominant mode. Observable licensing is frozen before synthetic truth "
        "is opened.",
        "",
        f"Repetitions: {repetitions}.",
        "",
        "## World summary",
        "",
        summary.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Key diagnostics",
        "",
        f"- Shared relation license rate: "
        f"{diagnostics['shared_relation_license_rate']:.4f}.",
        f"- Shared unique-mode license rate: "
        f"{diagnostics['shared_mode_license_rate']:.4f}.",
        f"- Truth fidelity among licensed shared worlds: "
        f"{diagnostics['licensed_shared_truth_fidelity_rate']:.4f} "
        f"(n={diagnostics['licensed_shared_count']}).",
        f"- Low-gap relation/mode license rates: "
        f"{diagnostics['low_gap_relation_license_rate']:.4f} / "
        f"{diagnostics['low_gap_mode_license_rate']:.4f}.",
        f"- Maximum negative-world relation license rate: "
        f"{diagnostics['maximum_negative_relation_license_rate']:.4f}.",
        f"- Mean individual correlation in shared worlds: "
        f"{diagnostics['shared_mean_individual_correlation']:.4f} "
        "(diagnostic, not a gate).",
        "",
        "## Gates",
        "",
    ]
    lines.extend(
        f"- `{name}`: {'PASS' if passed else 'FAIL'}"
        for name, passed in decision["checks"].items()
    )
    lines.extend([
        "",
        "## Ruling",
        "",
        "A relation license and a unique-axis license are different claims. "
        "Stable cross-family structure can be measurable even when no unique "
        "dominant direction exists; shared latent variation can also remain "
        "underresolved and must then be refused.",
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

    script_path = Path(__file__).resolve()
    core_path = ROOT / "suica_core" / "v8_relational_lift_support.py"
    write_run_manifest(
        output / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=config_path,
        code_paths=[script_path, core_path],
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
    rows = [row for output in outputs for row in output]
    trials = pd.DataFrame(rows)
    trials.to_csv(output / "relation_support_trials.csv", index=False)

    evaluated = _evaluate(trials, dict(config["gates"]))
    status = (
        "V8_HJIC1A_REPLICATED_RELATIONAL_SUPPORT_PASS"
        if evaluated["all_pass"]
        else "V8_HJIC1A_REPLICATED_RELATIONAL_SUPPORT_PARTIAL"
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
    summary = _summary_table(trials)
    summary.to_csv(output / "world_summary.csv", index=False)
    report = _build_report(
        decision=decision,
        repetitions=repetitions,
        summary=summary,
        claim_boundary=str(config["claim_boundary"]),
    )
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
