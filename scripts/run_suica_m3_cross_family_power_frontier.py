#!/usr/bin/env python3
"""Estimate the event budget for unresolved M3 cross-family worlds."""
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

from suica_core.m3_cross_family_audit import audit_m3_cross_family  # noqa: E402
from suica_core.m3_cross_family_estimator import fit_m3_cross_family  # noqa: E402
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


def _seed_pass(row: dict[str, Any], gates: dict[str, float]) -> bool:
    passed = bool(
        float(row["expected_auc"]) >= gates["minimum_expected_auc"]
        and float(row["expected_geometry"])
        >= gates["minimum_expected_geometry"]
        and abs(float(row["cheap_auc"]) - 0.5)
        <= gates["maximum_cheap_auc_deviation"]
        and float(row["delta_auc"]) > gates["minimum_delta_auc"]
    )
    if gates.get("require_positive_increment", False):
        passed = passed and float(row["heldout_increment"]) > 0.0
    return passed


def _estimator_seed(root: int, label: str) -> int:
    digest = hmac.new(
        str(root).encode(),
        f"estimator::{label}".encode(),
        hashlib.sha256,
    ).digest()
    return int.from_bytes(digest[:8], "big") % (2**63 - 1)


def _run(config: dict[str, Any]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    world_index = 0
    for family, declaration in config["families"].items():
        for world in declaration["worlds"]:
            for events in declaration["event_frontier"]:
                event_passes: list[bool] = []
                for repetition in range(int(config["repetitions"])):
                    seed = (
                        int(config["seed"])
                        + world_index * 10_000_019
                        + int(events) * 10_007
                        + repetition * 101
                    )
                    spec = M3CrossFamilySpec(
                        authors=int(declaration["authors"]),
                        occasions=int(declaration["occasions"]),
                        events=int(events),
                        dimensions=int(declaration["dimensions"]),
                        partners=int(declaration["partners"]),
                        noise=float(declaration["noise"]),
                    )
                    observed, truth = generate_m3_cross_family_world(
                        world=world,
                        spec=spec,
                        seed=seed,
                    )
                    estimate = fit_m3_cross_family(
                        observed,
                        seed=_estimator_seed(
                            int(config["seed"]),
                            f"{world}::{events}::{repetition}",
                        ),
                        **config["estimator"],
                    )
                    row = audit_m3_cross_family(estimate, truth)[0]
                    validity = audit_m3_cross_family_validity(
                        observed,
                        truth,
                    )
                    gates = {
                        **config["seed_pass"],
                        **config.get("world_overrides", {}).get(world, {}),
                    }
                    seed_pass = _seed_pass(row, gates)
                    event_passes.append(seed_pass)
                    rows.append({
                        "family": family,
                        "events": int(events),
                        "repetition": repetition,
                        "seed": seed,
                        "theoretical_lag02_max_range": float(
                            validity.get(
                                "theoretical_lag02_max_author_range",
                                0.0,
                            )
                        ),
                        "seed_pass": seed_pass,
                        **row,
                    })
                if (
                    bool(config.get("stop_after_resolution", False))
                    and np.mean(event_passes)
                    >= float(config["minimum_power"])
                ):
                    break
            world_index += 1
    return pd.DataFrame(rows)


def _summarize(
    metrics: pd.DataFrame,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    summary = metrics.groupby(
        ["family", "world", "events"],
        as_index=False,
    ).agg(
        seeds=("seed", "nunique"),
        power=("seed_pass", "mean"),
        expected_auc=("expected_auc", "mean"),
        cheap_auc=("cheap_auc", "mean"),
        expected_geometry=("expected_geometry", "mean"),
        delta_auc=("delta_auc", "mean"),
        heldout_increment=("heldout_increment", "mean"),
        positive_increment_fraction=(
            "heldout_increment",
            lambda values: float(np.mean(np.asarray(values) > 0.0)),
        ),
        theoretical_lag02_max_range=(
            "theoretical_lag02_max_range",
            "max",
        ),
    )
    selected: dict[str, int | None] = {}
    for world, frame in summary.groupby("world"):
        passing = frame[
            frame["power"] >= float(config["minimum_power"])
        ].sort_values("events")
        selected[str(world)] = (
            int(passing.iloc[0]["events"])
            if len(passing)
            else None
        )
    return summary, {
        "estimand_id": config["estimand_id"],
        "decision": (
            "M3_CROSS_FAMILY_POWER_FRONTIER_RESOLVED"
            if all(value is not None for value in selected.values())
            else "M3_CROSS_FAMILY_POWER_FRONTIER_PARTIAL"
        ),
        "minimum_power": config["minimum_power"],
        "selected_events": selected,
        "confirmation_sealed": False,
        "claim_boundary": (
            "Development-seed event-budget selection only. No confirmation "
            "or human-text claim."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m3_cross_family_power_frontier.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results" / "m3_cross_family_power_frontier",
    )
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics = _run(config)
    summary, decision = _summarize(metrics, config)
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
    report = f"""# SUICA M3 Cross-Family Event-Power Frontier

Decision: `{decision["decision"]}`

## Selected minimum events

```json
{json.dumps(decision["selected_events"], ensure_ascii=False, indent=2)}
```

## Frontier

{summary.to_markdown(index=False)}

## Boundary

These are public development seeds used only to select a prospective event
budget. They cannot appear in the fresh confirmation.
"""
    (ROOT / config.get(
        "report_path",
        "reports/SUICA_M3_CROSS_FAMILY_POWER_FRONTIER.md",
    )).write_text(
        report,
        encoding="utf-8",
    )
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
