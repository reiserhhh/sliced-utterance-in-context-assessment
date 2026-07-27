#!/usr/bin/env python3
"""Run low-order-matched attacks against the M3 mechanism atlas."""
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

from suica_core.m3_mechanism_audit import audit_m3_mechanism_atlas  # noqa: E402
from suica_core.m3_mechanism_stress_estimator import (  # noqa: E402
    fit_m3_mechanism_stress,
)
from suica_core.m3_mechanism_stress_generator import (  # noqa: E402
    M3MechanismStressSpec,
    generate_m3_mechanism_stress_world,
)


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _decision(metrics: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    final = metrics[metrics["events"] == max(config["event_frontier"])]
    gates = config["discovery_gates"]
    checks: dict[str, bool] = {}
    diagnostics: dict[str, Any] = {}
    for world, declaration in config["worlds"].items():
        expected = declaration["expected"]
        cheap = declaration["cheap"]
        if expected is None:
            continue
        expected_rows = final[
            (final["world"] == world)
            & (final["family"] == expected)
        ]
        cheap_rows = final[
            (final["world"] == world)
            & (final["family"] == cheap)
        ]
        expected_auc = float(expected_rows["same_author_auc"].mean())
        cheap_auc = float(cheap_rows["same_author_auc"].mean())
        expected_geometry = float(
            expected_rows["truth_geometry_spearman"].mean()
        )
        cheap_geometry = float(
            cheap_rows["truth_geometry_spearman"].mean()
        )
        diagnostics[world] = {
            "expected": expected,
            "cheap": cheap,
            "expected_auc": expected_auc,
            "cheap_auc": cheap_auc,
            "delta_auc": expected_auc - cheap_auc,
            "expected_geometry": expected_geometry,
            "cheap_geometry": cheap_geometry,
            "delta_geometry": expected_geometry - cheap_geometry,
        }
        checks[f"{world}_absolute"] = (
            expected_auc >= gates["minimum_expected_auc"]
            and expected_geometry >= gates["minimum_expected_geometry"]
        )
        checks[f"{world}_incremental"] = (
            expected_auc - cheap_auc >= gates["minimum_auc_increment"]
            and expected_geometry - cheap_geometry
            >= gates["minimum_geometry_increment"]
        )
    null_max = float(final[
        final["world"] == "null_author"
    ].groupby("family")["same_author_auc"].mean().max())
    diagnostics["null_max_auc"] = null_max
    checks["null_calibration"] = null_max <= gates["maximum_null_auc"]
    return {
        "estimand_id": config["estimand_id"],
        "decision": (
            "M3_MECHANISM_STRESS_DISCOVERY_PASS"
            if all(checks.values())
            else "M3_MECHANISM_STRESS_DISCOVERY_PARTIAL"
        ),
        "checks": checks,
        "diagnostics": diagnostics,
        "claim_boundary": (
            "Low-order-matched synthetic attacks only; no human-text or "
            "psychological construct claim."
        ),
    }


def _report(
    metrics: pd.DataFrame,
    config: dict[str, Any],
    decision: dict[str, Any],
) -> str:
    rows = []
    for world, diagnostic in decision["diagnostics"].items():
        if not isinstance(diagnostic, dict):
            continue
        rows.append({"world": world, **diagnostic})
    table = pd.DataFrame(rows)
    frontier = metrics[
        metrics["expected"] | metrics["cheap"]
    ].groupby(
        ["events", "world", "family", "expected", "cheap"],
        as_index=False,
    ).agg(
        auc=("same_author_auc", "mean"),
        geometry=("truth_geometry_spearman", "mean"),
    )
    checks = "\n".join(
        f"- {'PASS' if value else 'FAIL'}: `{name}`"
        for name, value in decision["checks"].items()
    )
    return f"""# SUICA M3 Low-Order-Matched Mechanism Stress Test

Decision: `{decision["decision"]}`

## Purpose

Atlas V1 recovered deliberately simple author parameters. This attack asks
whether the proposed higher-order summaries still add information after the
corresponding cheap statistic is matched or explicitly included.

## Checks

{checks}

## Final-event diagnostics

{table.to_markdown(index=False)}

## Information frontier

{frontier.to_markdown(index=False)}

## Boundary

Even a pass licenses only synthetic higher-order parameter recovery. It does
not establish a complete mechanism basis, human-text persistence, personality
meaning, or construct validity.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m3_mechanism_stress_discovery.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results" / "m3_mechanism_stress",
    )
    args = parser.parse_args()
    config = _load(args.config)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for events in config["event_frontier"]:
        for repetition in range(config["repetitions"]):
            for world_index, (world, declaration) in enumerate(
                config["worlds"].items()
            ):
                seed = (
                    int(config["seed"])
                    + int(events) * 1_000_003
                    + repetition * 10_007
                    + world_index * 101
                )
                observed, truth = generate_m3_mechanism_stress_world(
                    world=world,
                    spec=M3MechanismStressSpec(
                        **config["base_spec"],
                        events=int(events),
                    ),
                    seed=seed,
                )
                estimate = fit_m3_mechanism_stress(
                    observed,
                    seed=seed + 5_033,
                )
                for row in audit_m3_mechanism_atlas(estimate, truth):
                    rows.append({
                        "events": int(events),
                        "repetition": repetition,
                        "seed": seed,
                        "cheap": row["family"] == declaration["cheap"],
                        **row,
                    })
    metrics = pd.DataFrame(rows)
    decision = _decision(metrics, config)
    metrics.to_csv(args.output_dir / "metrics.csv", index=False)
    with (args.output_dir / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    with (args.output_dir / "config.snapshot.json").open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(config, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    report = _report(metrics, config, decision)
    report_filename = config.get(
        "report_filename",
        "SUICA_M3_MECHANISM_STRESS_DISCOVERY.md",
    )
    (ROOT / "reports" / report_filename).write_text(
        report,
        encoding="utf-8",
    )
    print(json.dumps(decision, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
