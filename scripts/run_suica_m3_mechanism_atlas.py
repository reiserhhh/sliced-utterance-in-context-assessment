#!/usr/bin/env python3
"""Run the SUICA M3 micro-to-meso mechanism-atlas discovery."""
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
from suica_core.m3_mechanism_estimator import (  # noqa: E402
    MECHANISM_FAMILIES,
    fit_m3_mechanism_atlas,
)
from suica_core.m3_mechanism_generator import (  # noqa: E402
    M3MechanismWorldSpec,
    generate_m3_mechanism_world,
)


def _read(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _interval(values: pd.Series) -> tuple[float, float, float]:
    array = values.dropna().to_numpy(dtype=float)
    if not len(array):
        return float("nan"), float("nan"), float("nan")
    return (
        float(np.mean(array)),
        float(np.quantile(array, 0.025)),
        float(np.quantile(array, 0.975)),
    )


def _summarize(metrics: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    keys = ["events", "world", "family", "expected"]
    for values, group in metrics.groupby(keys, sort=True, dropna=False):
        events, world, family, expected = values
        for metric in ("same_author_auc", "truth_geometry_spearman"):
            mean, lower, upper = _interval(group[metric])
            rows.append({
                "events": int(events),
                "world": world,
                "family": family,
                "expected": bool(expected),
                "metric": metric,
                "mean": mean,
                "lower95_seed_quantile": lower,
                "upper95_seed_quantile": upper,
                "n": int(group[metric].notna().sum()),
            })
    return pd.DataFrame(rows)


def _selectivity(metrics: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    families = list(MECHANISM_FAMILIES)
    rows: list[dict[str, Any]] = []
    for (events, repetition, world), group in metrics.groupby(
        ["events", "repetition", "world"],
        sort=True,
    ):
        expected = config["positive_worlds"].get(world)
        candidate = group[group["family"].isin(families)]
        winner = candidate.loc[candidate["same_author_auc"].idxmax(), "family"]
        expected_row = group[group["family"] == expected]
        rows.append({
            "events": int(events),
            "repetition": int(repetition),
            "world": world,
            "expected_family": expected,
            "winner": winner,
            "expected_won": bool(expected is not None and winner == expected),
            "expected_auc": (
                float(expected_row["same_author_auc"].iloc[0])
                if len(expected_row)
                else float("nan")
            ),
            "expected_geometry": (
                float(expected_row["truth_geometry_spearman"].iloc[0])
                if len(expected_row)
                else float("nan")
            ),
        })
    return pd.DataFrame(rows)


def _decision(
    metrics: pd.DataFrame,
    selectivity: pd.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    events = max(config["event_frontier"])
    final = metrics[metrics["events"] == events]
    final_selectivity = selectivity[selectivity["events"] == events]
    gates = config["discovery_gates"]
    checks: dict[str, bool] = {}
    diagnostics: dict[str, Any] = {}
    for world, family in config["positive_worlds"].items():
        selected = final[
            (final["world"] == world)
            & (final["family"] == family)
        ]
        auc = float(selected["same_author_auc"].mean())
        geometry = float(selected["truth_geometry_spearman"].mean())
        win_fraction = float(final_selectivity[
            final_selectivity["world"] == world
        ]["expected_won"].mean())
        checks[f"{world}_auc"] = auc >= gates["minimum_expected_auc"]
        checks[f"{world}_geometry"] = (
            geometry >= gates["minimum_expected_geometry"]
        )
        checks[f"{world}_selectivity"] = (
            win_fraction >= gates["minimum_expected_win_fraction"]
        )
        diagnostics[world] = {
            "expected_family": family,
            "mean_auc": auc,
            "mean_geometry": geometry,
            "win_fraction": win_fraction,
        }
    null_max = float(final[
        (final["world"] == "null_author")
        & (final["family"].isin(MECHANISM_FAMILIES))
    ].groupby("family")["same_author_auc"].mean().max())
    opportunity_auc = float(final[
        (final["world"] == "opportunity_only")
        & (final["family"] == "opportunity_profile")
    ]["same_author_auc"].mean())
    residual_families = (
        "distribution_kme",
        "koopman_spectrum",
        "interaction_coupling",
        "higher_order_path",
    )
    opportunity_residual_max = float(final[
        (final["world"] == "opportunity_only")
        & (final["family"].isin(residual_families))
    ].groupby("family")["same_author_auc"].mean().max())
    checks["null_calibration"] = null_max <= gates["maximum_null_auc"]
    checks["opportunity_detection"] = (
        opportunity_auc >= gates["minimum_opportunity_auc"]
    )
    checks["opportunity_residual_control"] = (
        opportunity_residual_max
        <= gates["maximum_opportunity_residual_auc"]
    )
    diagnostics["null_max_auc"] = null_max
    diagnostics["opportunity_auc"] = opportunity_auc
    diagnostics["opportunity_residual_max_auc"] = opportunity_residual_max
    return {
        "estimand_id": config["estimand_id"],
        "decision": (
            "M3_ATLAS_V1_LOW_ORDER_PARAMETER_RECOVERY_PASS"
            if all(checks.values())
            else "M3_ATLAS_V1_LOW_ORDER_PARAMETER_RECOVERY_PARTIAL"
        ),
        "checks": checks,
        "diagnostics": diagnostics,
        "claim_boundary": (
            "Synthetic mechanism selectivity only. No human-text persistence, "
            "personality meaning, construct validity, or clinical claim."
        ),
    }


def _report(
    config: dict[str, Any],
    summary: pd.DataFrame,
    selectivity: pd.DataFrame,
    decision: dict[str, Any],
) -> str:
    final_events = max(config["event_frontier"])
    final_auc = summary[
        (summary["events"] == final_events)
        & (summary["metric"] == "same_author_auc")
    ].copy()
    expected = final_auc[final_auc["expected"]]
    frontier = selectivity[
        selectivity["world"].isin(config["positive_worlds"])
    ].groupby(["events", "world"], as_index=False).agg(
        expected_auc=("expected_auc", "mean"),
        expected_geometry=("expected_geometry", "mean"),
        expected_win_fraction=("expected_won", "mean"),
    )
    checks = "\n".join(
        f"- {'PASS' if value else 'FAIL'}: `{name}`"
        for name, value in decision["checks"].items()
    )
    return f"""# SUICA M3 Micro-to-Meso Mechanism Atlas

Decision: `{decision["decision"]}`

## Question

This discovery does not assume that microscopic event vectors connect directly
to one mesoscopic author axis. It tests whether several distinct intermediate
mechanisms can be recovered selectively from independent event panels.

## Mechanism families

1. state-density distribution beyond the mean;
2. condition-to-response operator (an operational if-then signature);
3. metastable/Koopman slow mode;
4. interactional alignment or susceptibility operator;
5. higher-order path memory beyond a first-order Markov approximation;
6. opportunity profile as a declared non-response confound;
7. a union summary for mixed worlds.

## Discovery checks

{checks}

## Expected-family results at {final_events} events per occasion

{expected[["world", "family", "mean", "lower95_seed_quantile", "upper95_seed_quantile"]].to_markdown(index=False)}

## Sample-information frontier

{frontier.to_markdown(index=False)}

## Diagnostics

```json
{json.dumps(decision["diagnostics"], indent=2, ensure_ascii=False)}
```

## Interpretation

Passing a world means that the registered summary recovers independent-view
author geometry generated by that mechanism and is not merely a mean score.
It does not establish that the mechanism exists in human text or that it is a
personality construct. Failure is informative: it identifies a mechanism that
cannot yet be distinguished at the tested event budget.

The opportunity-only world is especially important. Stable author
reidentification caused only by differing condition exposure must be assigned
to the opportunity profile, while response-residual mechanisms remain near
chance. This separates a measurable author environment from an author
response law.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m3_mechanism_atlas_discovery.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results" / "m3_mechanism_atlas",
    )
    args = parser.parse_args()
    config = _read(args.config)
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    base_spec = dict(config["base_spec"])
    for events in config["event_frontier"]:
        for repetition in range(config["repetitions"]):
            for world_index, world in enumerate(config["worlds"]):
                seed = (
                    int(config["seed"])
                    + 1_000_003 * int(events)
                    + 10_007 * repetition
                    + 101 * world_index
                )
                spec = M3MechanismWorldSpec(
                    **base_spec,
                    events=int(events),
                )
                observed, truth = generate_m3_mechanism_world(
                    world=world,
                    spec=spec,
                    seed=seed,
                )
                estimate = fit_m3_mechanism_atlas(
                    observed,
                    seed=seed + 7_919,
                )
                for row in audit_m3_mechanism_atlas(estimate, truth):
                    rows.append({
                        "events": int(events),
                        "repetition": repetition,
                        "seed": seed,
                        **row,
                    })
    metrics = pd.DataFrame(rows)
    summary = _summarize(metrics)
    selectivity = _selectivity(metrics, config)
    decision = _decision(metrics, selectivity, config)
    metrics.to_csv(output_dir / "metrics.csv", index=False)
    summary.to_csv(output_dir / "summary.csv", index=False)
    selectivity.to_csv(output_dir / "mechanism_selectivity.csv", index=False)
    final = metrics[metrics["events"] == max(config["event_frontier"])]
    for metric, filename in (
        ("same_author_auc", "auc_matrix.csv"),
        ("truth_geometry_spearman", "geometry_matrix.csv"),
    ):
        matrix = final.pivot_table(
            index="world",
            columns="family",
            values=metric,
            aggfunc="mean",
        )
        matrix.to_csv(output_dir / filename)
    frontier = selectivity.groupby(
        ["events", "world"],
        as_index=False,
    ).agg(
        expected_auc=("expected_auc", "mean"),
        expected_geometry=("expected_geometry", "mean"),
        expected_win_fraction=("expected_won", "mean"),
    )
    frontier.to_csv(output_dir / "event_frontier.csv", index=False)
    with (output_dir / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    with (output_dir / "config.snapshot.json").open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    report = _report(config, summary, selectivity, decision)
    report_path = ROOT / "reports" / "SUICA_M3_MECHANISM_ATLAS_DISCOVERY.md"
    report_path.write_text(report, encoding="utf-8")
    print(json.dumps(decision, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
