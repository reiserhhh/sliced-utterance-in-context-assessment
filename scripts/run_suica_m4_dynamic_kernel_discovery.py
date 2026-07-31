#!/usr/bin/env python3
"""Run M4-A dynamic noncommuting-kernel and temporal-gate discovery."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.m4_dynamic_kernel_audit import (  # noqa: E402
    audit_m4_dynamic_kernel,
)
from suica_core.m4_dynamic_kernel_estimator import (  # noqa: E402
    fit_m4_dynamic_kernel,
)
from suica_core.m4_dynamic_kernel_generator import (  # noqa: E402
    M4DynamicKernelSpec,
    generate_m4_dynamic_kernel_world,
)


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _summarize(metrics: pd.DataFrame) -> pd.DataFrame:
    numeric = [
        column for column in metrics.columns
        if column not in {"world", "expected_order", "repetition", "seed"}
        and pd.api.types.is_numeric_dtype(metrics[column])
    ]
    rows: list[dict[str, Any]] = []
    for world, group in metrics.groupby("world", sort=False):
        row: dict[str, Any] = {
            "world": world,
            "expected_order": group["expected_order"].iloc[0],
        }
        for column in numeric:
            values = group[column].dropna().to_numpy(dtype=float)
            row[f"{column}_mean"] = (
                float(np.mean(values)) if len(values) else float("nan")
            )
            row[f"{column}_lower"] = (
                float(np.quantile(values, 0.025))
                if len(values) else float("nan")
            )
            row[f"{column}_upper"] = (
                float(np.quantile(values, 0.975))
                if len(values) else float("nan")
            )
        rows.append(row)
    return pd.DataFrame(rows)


def _decision(
    metrics: pd.DataFrame,
    summary: pd.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    targets = config["discovery_targets"]
    active = metrics[metrics["world"].isin([
        "noncommuting_forward_gate",
        "noncommuting_reverse_gate",
    ])]
    commuting = metrics[metrics["world"] == "commuting_null"]
    alias = metrics[metrics["world"] == "gate_role_alias"]
    diagnostics = {
        "active_order_accuracy": float(active["order_accuracy"].mean()),
        "commutator_geometry": float(
            active["commutator_geometry"].mean()
        ),
        "gate_parameter_spearman": float(
            active["gate_parameter_spearman"].mean()
        ),
        "gate_direction_margin": float(
            active["mean_gate_direction_margin"].mean()
        ),
        "path_logscore_gain": float(
            active["mean_path_logscore_gain"].mean()
        ),
        "active_same_author_auc": float(
            active["same_author_auc"].mean()
        ),
        "commuting_same_author_auc": float(
            commuting["same_author_auc"].mean()
        ),
        "active_auc_increment_over_commuting": float(
            active["same_author_auc"].mean()
            - commuting["same_author_auc"].mean()
        ),
        "commuting_order_margin": float(
            commuting["mean_order_margin"].mean()
        ),
        "commuting_gate_margin": float(
            commuting["mean_gate_direction_margin"].mean()
        ),
        "commuting_commutator": float(
            commuting["mean_commutator"].mean()
        ),
        "alias_refusal_rate": float(alias["refusal_rate"].mean()),
    }
    checks = {
        "kernel_order_recovery": (
            diagnostics["active_order_accuracy"]
            >= targets["minimum_order_accuracy"]
        ),
        "commutator_geometry": (
            diagnostics["commutator_geometry"]
            >= targets["minimum_commutator_geometry"]
        ),
        "temporal_gate_strength": (
            diagnostics["gate_parameter_spearman"]
            >= targets["minimum_gate_parameter_spearman"]
        ),
        "temporal_gate_direction": (
            diagnostics["gate_direction_margin"]
            >= targets["minimum_gate_direction_margin"]
        ),
        "heldout_path_likelihood": (
            diagnostics["path_logscore_gain"]
            >= targets["minimum_path_logscore_gain"]
        ),
        "active_author_signature": (
            diagnostics["active_same_author_auc"]
            >= targets["minimum_active_same_author_auc"]
        ),
        "composition_signature_increment": (
            diagnostics["active_auc_increment_over_commuting"]
            >= targets["minimum_active_auc_increment_over_commuting"]
        ),
        "commuting_order_null": (
            abs(diagnostics["commuting_order_margin"])
            <= targets["maximum_commuting_order_margin_abs"]
        ),
        "commuting_gate_null": (
            abs(diagnostics["commuting_gate_margin"])
            <= targets["maximum_commuting_gate_margin_abs"]
        ),
        "commuting_operator_control": all(
            commuting["commuting_control_pass"]
        ),
        "alias_refusal": (
            diagnostics["alias_refusal_rate"]
            >= targets["minimum_alias_refusal_rate"]
        ),
    }
    return {
        "estimand_id": config["estimand_id"],
        "decision": (
            "M4_A_DYNAMIC_KERNEL_GATE_ORDER_DISCOVERY_PASS"
            if all(checks.values())
            else "M4_A_DYNAMIC_KERNEL_GATE_ORDER_DISCOVERY_PARTIAL"
        ),
        "checks": checks,
        "diagnostics": diagnostics,
        "world_summary": summary.to_dict(orient="records"),
        "claim_boundary": (
            "Synthetic transition-kernel composition only. The calibration "
            "regimes identify condition and history operators by design; "
            "this is not human-text persistence or causal identification."
        ),
    }


def _report(
    decision: dict[str, Any],
    summary: pd.DataFrame,
) -> str:
    checks = "\n".join(
        f"- {'PASS' if passed else 'FAIL'}: `{name}`"
        for name, passed in decision["checks"].items()
    )
    return f"""# SUICA M4-A Dynamic Kernel Gate/Order Discovery

Decision: `{decision["decision"]}`

## Question

The static M4-A battery detected projection-order sensitivity but did not
compose actual transition kernels. This experiment uses calibration regimes
to estimate condition-only and history-only affine kernels, composes them in
both orders, and scores the two path laws on held-out joint transitions.

## Discovery checks

{checks}

## World summary

{summary.to_markdown(index=False)}

## Interpretation

The experiment distinguishes a true noncommuting transition composition from
a scalar commuting control. A history-to-condition temporal gate is estimated
from held-out transition residuals after choosing the kernel order. A
calibration-free role alias must refuse. These are finite designed synthetic
mechanisms, not natural-language or psychological claims.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m4_dynamic_kernel_discovery.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results" / "m4_dynamic_kernel_discovery",
    )
    args = parser.parse_args()
    config = _load(args.config)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for repetition in range(int(config["repetitions"])):
        for world_index, world in enumerate(config["worlds"]):
            seed = (
                int(config["seed"])
                + repetition * 100_003
                + world_index * 1_009
            )
            observed, truth = generate_m4_dynamic_kernel_world(
                world=world,
                spec=M4DynamicKernelSpec(**config["base_spec"]),
                seed=seed,
            )
            estimate = fit_m4_dynamic_kernel(
                observed,
                **config["estimator"],
            )
            row = audit_m4_dynamic_kernel(
                estimate,
                truth,
                **config["audit"],
            )
            row.update({"repetition": repetition, "seed": seed})
            rows.append(row)

    metrics = pd.DataFrame(rows)
    summary = _summarize(metrics)
    decision = _decision(metrics, summary, config)
    metrics.to_csv(args.output_dir / "metrics.csv", index=False)
    summary.to_csv(args.output_dir / "summary.csv", index=False)
    with (args.output_dir / "decision.json").open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(decision, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    with (args.output_dir / "config.snapshot.json").open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(config, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    report = _report(decision, summary)
    (args.output_dir / "report.md").write_text(report, encoding="utf-8")
    (
        ROOT
        / "reports"
        / "SUICA_M4_DYNAMIC_KERNEL_GATE_ORDER_DISCOVERY.md"
    ).write_text(report, encoding="utf-8")
    print(json.dumps(decision, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
