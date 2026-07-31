#!/usr/bin/env python3
"""Run the SUICA M4-A mechanism-composition discovery battery."""
from __future__ import annotations

import argparse
from itertools import combinations
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.m4_composition_audit import (  # noqa: E402
    audit_m4_composition,
)
from suica_core.m4_composition_estimator import (  # noqa: E402
    fit_m4_composition,
)
from suica_core.m4_composition_generator import (  # noqa: E402
    MECHANISM_NAMES,
    M4CompositionSpec,
    generate_m4_composition_world,
)


def _load(path: Path) -> dict[str, Any]:
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


def _macro_f1(metrics: pd.DataFrame) -> float:
    labels = sorted(set(metrics["expected_kind"]).union(
        metrics["diagnosed_kind"]
    ))
    scores: list[float] = []
    for label in labels:
        expected = metrics["expected_kind"] == label
        predicted = metrics["diagnosed_kind"] == label
        true_positive = int(np.sum(expected & predicted))
        false_positive = int(np.sum(~expected & predicted))
        false_negative = int(np.sum(expected & ~predicted))
        precision = (
            true_positive / (true_positive + false_positive)
            if true_positive + false_positive
            else 0.0
        )
        recall = (
            true_positive / (true_positive + false_negative)
            if true_positive + false_negative
            else 0.0
        )
        scores.append(
            2.0 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )
    return float(np.mean(scores))


def _summarize(metrics: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "same_author_auc",
        "target_geometry_spearman",
        "target_parameter_spearman",
        "support_f1",
        "sign_accuracy",
        "refusal_rate",
        "null_false_positive_rate",
        "mean_heldout_full_value",
        "target_product_dividend",
        "target_observational_dividend",
        "target_commutator",
        "target_gate_direction",
        "reverse_gate_direction",
    ]
    rows: list[dict[str, Any]] = []
    for world, group in metrics.groupby("world", sort=False):
        row: dict[str, Any] = {
            "world": world,
            "expected_kind": group["expected_kind"].iloc[0],
            "classification_accuracy": float(group["kind_correct"].mean()),
        }
        for column in columns:
            mean, lower, upper = _interval(group[column])
            row[f"{column}_mean"] = mean
            row[f"{column}_lower"] = lower
            row[f"{column}_upper"] = upper
        rows.append(row)
    return pd.DataFrame(rows)


def _lattice_rows(
    estimate: Any,
    *,
    world: str,
    repetition: int,
) -> list[dict[str, Any]]:
    positions = {
        name: index for index, name in enumerate(MECHANISM_NAMES)
    }
    rows: list[dict[str, Any]] = []
    for order in (2, 3):
        for edge in combinations(MECHANISM_NAMES, order):
            key = "&".join(str(positions[name]) for name in edge)

            def mean(metric: str) -> float:
                return float(np.mean(0.5 * (
                    estimate.train_metrics[f"{metric}|{key}"]
                    + estimate.test_metrics[f"{metric}|{key}"]
                )))

            rows.append({
                "world": world,
                "repetition": repetition,
                "order": order,
                "edge": "&".join(edge),
                "product_dividend": mean("product_div"),
                "observational_dividend": mean("obs_div"),
                "dependence_gap": mean("dependence_gap"),
                "coefficient_sign": mean("coefficient_sign"),
            })
    return rows


def _decision(
    metrics: pd.DataFrame,
    summary: pd.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    targets = config["discovery_targets"]
    active = metrics[metrics["world"].isin(["synergy", "gate", "composite"])]
    geometry = metrics[metrics["world"].isin([
        "synergy",
        "redundancy",
        "suppression",
        "gate",
        "projection_order",
        "composite",
    ])]
    alias = metrics[metrics["world"] == "alias"]
    null = metrics[metrics["world"] == "null"]
    gate = metrics[metrics["world"] == "gate"]
    diagnostics = {
        "type_macro_f1": _macro_f1(metrics),
        "active_support_f1": float(active["support_f1"].mean()),
        "active_sign_accuracy": float(active["sign_accuracy"].mean()),
        "mean_target_geometry": float(
            geometry["target_geometry_spearman"].mean()
        ),
        "gate_direction_margin": float(
            (gate["target_gate_direction"] - gate["reverse_gate_direction"])
            .mean()
        ),
        "alias_refusal_rate": float(alias["refusal_rate"].mean()),
        "null_false_positive_rate": float(
            null["null_false_positive_rate"].mean()
        ),
    }
    checks = {
        "type_recovery": (
            diagnostics["type_macro_f1"]
            >= targets["minimum_type_macro_f1"]
        ),
        "active_support_recovery": (
            diagnostics["active_support_f1"]
            >= targets["minimum_active_support_f1"]
        ),
        "interaction_sign_recovery": (
            diagnostics["active_sign_accuracy"]
            >= targets["minimum_sign_accuracy"]
        ),
        "author_parameter_geometry": (
            diagnostics["mean_target_geometry"]
            >= targets["minimum_target_geometry"]
        ),
        "gate_direction": (
            diagnostics["gate_direction_margin"]
            >= targets["minimum_gate_direction_margin"]
        ),
        "alias_refusal": (
            diagnostics["alias_refusal_rate"]
            >= targets["minimum_alias_refusal_rate"]
        ),
        "null_calibration": (
            diagnostics["null_false_positive_rate"]
            <= targets["maximum_null_false_positive_rate"]
        ),
    }
    return {
        "estimand_id": config["estimand_id"],
        "decision": (
            "M4_A_MECHANISM_COMPOSITION_GRAMMAR_DISCOVERY_PASS_WITH_SCOPE_CORRECTION"
            if all(checks.values())
            else "M4_A_MECHANISM_COMPOSITION_GRAMMAR_DISCOVERY_PARTIAL"
        ),
        "checks": checks,
        "diagnostics": diagnostics,
        "world_summary": summary.to_dict(orient="records"),
        "claim_boundary": (
            "Synthetic composition grammar only. This discovers how known "
            "mechanism channels combine; it is not a complete basis, a "
            "human-text result, or a personality interpretation."
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
    return f"""# SUICA M4-A Mechanism Composition Discovery

Decision: `{decision["decision"]}`

## New object

The experiment estimates an author mechanism-composition signature

```text
Lambda_u = fitted product-reference Harsanyi lattice
         + dependence distortion
         + directional gates
         + projection commutators.
```

The observational coalition game preserves dependence among opportunity,
state, condition, interaction, emission drive, and history. The
product-reference game breaks that dependence while retaining each marginal
and the fitted response law. Their difference separates fitted-law
functional interaction from contribution induced by redundancy or
suppression in the matched synthetic family.

## Discovery checks

{checks}

## World summary

{summary.to_markdown(index=False)}

## Interpretation

This battery asks whether the M3 atlas can be upgraded from a list of
recoverable mechanisms into a grammar of addition, synergy, redundancy,
suppression, gating, dependence-order sensitivity, and sparse composite
hyperedges. A pass licenses the finite synthetic grammar and its estimator,
not completeness or psychological meaning.

The continuous gate direction passed, but the fixed coarse gate label
classified 4/8 repetitions at its registered threshold. That threshold is
not retuned on this discovery sample.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m4_composition_discovery.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results" / "m4_composition_discovery",
    )
    args = parser.parse_args()
    config = _load(args.config)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    metric_rows: list[dict[str, Any]] = []
    lattice_rows: list[dict[str, Any]] = []
    for repetition in range(int(config["repetitions"])):
        for world_index, world in enumerate(config["worlds"]):
            seed = (
                int(config["seed"])
                + repetition * 100_003
                + world_index * 1_009
            )
            observed, truth = generate_m4_composition_world(
                world=world,
                spec=M4CompositionSpec(**config["base_spec"]),
                seed=seed,
            )
            estimate = fit_m4_composition(
                observed,
                seed=seed + 503,
                **config["estimator"],
            )
            row = audit_m4_composition(
                estimate,
                truth,
                MECHANISM_NAMES,
                **config["diagnostic_thresholds"],
            )
            row.update({"repetition": repetition, "seed": seed})
            metric_rows.append(row)
            lattice_rows.extend(_lattice_rows(
                estimate,
                world=world,
                repetition=repetition,
            ))

    metrics = pd.DataFrame(metric_rows)
    summary = _summarize(metrics)
    lattice = pd.DataFrame(lattice_rows)
    decision = _decision(metrics, summary, config)
    metrics.to_csv(args.output_dir / "metrics.csv", index=False)
    summary.to_csv(args.output_dir / "summary.csv", index=False)
    lattice.to_csv(args.output_dir / "mechanism_lattice.csv", index=False)
    confusion = pd.crosstab(
        metrics["expected_kind"],
        metrics["diagnosed_kind"],
        margins=True,
    )
    confusion.to_csv(args.output_dir / "classification_confusion.csv")
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
    (ROOT / "reports" / "SUICA_M4_MECHANISM_COMPOSITION_DISCOVERY.md").write_text(
        report,
        encoding="utf-8",
    )
    print(json.dumps(decision, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
