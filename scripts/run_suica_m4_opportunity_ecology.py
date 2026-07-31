#!/usr/bin/env python3
"""Run M4-B endogenous opportunity-ecology discovery."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, f1_score

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.m4_opportunity_audit import (  # noqa: E402
    audit_m4_opportunity_ecology,
)
from suica_core.m4_opportunity_estimator import (  # noqa: E402
    fit_m4_opportunity_ecology,
)
from suica_core.m4_opportunity_generator import (  # noqa: E402
    M4OpportunitySpec,
    generate_m4_opportunity_world,
)


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _mean_metric(estimate: Any, name: str) -> np.ndarray:
    return 0.5 * (
        np.asarray(estimate.train_metrics[name], dtype=float)
        + np.asarray(estimate.test_metrics[name], dtype=float)
    )


def _total_variation(first: list[float], second: list[float]) -> float:
    return 0.5 * float(np.sum(np.abs(
        np.asarray(first, dtype=float) - np.asarray(second, dtype=float)
    )))


def _matched_metrics(
    estimates: dict[str, Any],
    audits: dict[str, dict[str, Any]],
    thresholds: dict[str, float],
) -> dict[str, float]:
    selection = estimates["exogenous_selection"]
    creation = estimates["endogenous_creation_matched"]
    selection_norm = np.linalg.norm(
        _mean_metric(selection, "selection"),
        axis=1,
    ) / np.sqrt(selection.train_metrics["selection"].shape[1])
    selection_creation_norm = np.linalg.norm(
        _mean_metric(selection, "creation"),
        axis=1,
    )
    creation_selection_norm = np.linalg.norm(
        _mean_metric(creation, "selection"),
        axis=1,
    ) / np.sqrt(creation.train_metrics["selection"].shape[1])
    creation_norm = np.linalg.norm(
        _mean_metric(creation, "creation"),
        axis=1,
    )
    score = np.concatenate([
        (
            selection_creation_norm / thresholds["creation_threshold"]
            - selection_norm / thresholds["selection_threshold"]
        ),
        (
            creation_norm / thresholds["creation_threshold"]
            - creation_selection_norm / thresholds["selection_threshold"]
        ),
    ])
    label = np.concatenate([
        np.zeros(len(selection_norm), dtype=int),
        np.ones(len(creation_norm), dtype=int),
    ])
    mechanism_discrimination = balanced_accuracy_score(
        label,
        score > 0.0,
    )

    fast = estimates["fast_return_equal_marginal"]
    slow = estimates["slow_hysteresis_equal_marginal"]
    persistence = np.concatenate([
        np.mean(_mean_metric(fast, "external_persistence"), axis=1),
        np.mean(_mean_metric(slow, "external_persistence"), axis=1),
    ])
    return_label = np.concatenate([
        np.zeros(len(fast.train_signature), dtype=int),
        np.ones(len(slow.train_signature), dtype=int),
    ])
    return_discrimination = balanced_accuracy_score(
        return_label,
        persistence > 0.40,
    )
    return {
        "selection_creation_menu_half_l1": _total_variation(
            audits["exogenous_selection"]["menu_marginal"],
            audits["endogenous_creation_matched"]["menu_marginal"],
        ),
        "selection_creation_choice_tv": _total_variation(
            audits["exogenous_selection"]["choice_marginal"],
            audits["endogenous_creation_matched"]["choice_marginal"],
        ),
        "selection_creation_mechanism_balanced_accuracy": float(
            mechanism_discrimination
        ),
        "fast_slow_menu_half_l1": _total_variation(
            audits["fast_return_equal_marginal"]["menu_marginal"],
            audits["slow_hysteresis_equal_marginal"]["menu_marginal"],
        ),
        "fast_slow_choice_tv": _total_variation(
            audits["fast_return_equal_marginal"]["choice_marginal"],
            audits["slow_hysteresis_equal_marginal"]["choice_marginal"],
        ),
        "fast_slow_return_balanced_accuracy": float(
            return_discrimination
        ),
    }


def _summarize(metrics: pd.DataFrame) -> pd.DataFrame:
    numeric = [
        column for column in metrics.columns
        if column not in {
            "world",
            "active_mechanisms",
            "matched_group",
            "repetition",
            "seed",
        }
        and pd.api.types.is_numeric_dtype(metrics[column])
    ]
    rows = []
    for world, group in metrics.groupby("world", sort=False):
        row: dict[str, Any] = {"world": world}
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
    repetitions: pd.DataFrame,
    summary: pd.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    targets = config["discovery_targets"]
    active = metrics[~metrics["world"].isin([
        "null_exogenous",
        "hidden_opportunity_alias",
    ])]
    loop_worlds = metrics[metrics["world"].isin([
        "endogenous_creation_matched",
        "history_gated_ecology",
        "selection_creation_compensation",
    ])]
    return_worlds = metrics[metrics["world"].isin([
        "fast_return_equal_marginal",
        "slow_hysteresis_equal_marginal",
    ])]
    gate_world = metrics[metrics["world"] == "history_gated_ecology"]
    alias = metrics[metrics["world"] == "hidden_opportunity_alias"]
    null = metrics[metrics["world"] == "null_exogenous"]
    diagnostics = {
        "mechanism_macro_f1": float(
            repetitions["mechanism_macro_f1"].mean()
        ),
        "active_support_f1": float(active["support_f1"].mean()),
        "active_sign_accuracy": float(active["sign_accuracy"].mean()),
        "loop_geometry": float(loop_worlds["loop_geometry"].mean()),
        "rho_spearman": float(loop_worlds["rho_spearman"].mean()),
        "return_time_spearman": float(
            return_worlds["return_time_spearman"].mean()
        ),
        "recovery_time_spearman": float(
            active["recovery_time_spearman"].mean()
        ),
        "matched_mechanism_balanced_accuracy": float(
            repetitions[
                "selection_creation_mechanism_balanced_accuracy"
            ].mean()
        ),
        "matched_menu_half_l1": float(
            repetitions["selection_creation_menu_half_l1"].mean()
        ),
        "matched_choice_tv": float(
            repetitions["selection_creation_choice_tv"].mean()
        ),
        "return_mechanism_balanced_accuracy": float(
            repetitions["fast_slow_return_balanced_accuracy"].mean()
        ),
        "gate_direction_margin": float(
            gate_world["mean_gate_direction_margin"].mean()
        ),
        "active_same_author_auc": float(
            active["same_author_auc"].mean()
        ),
        "alias_refusal_rate": float(alias["refusal_rate"].mean()),
        "null_false_positive_rate": float(
            null["null_false_positive_rate"].mean()
        ),
    }
    checks = {
        "mechanism_type_recovery": (
            diagnostics["mechanism_macro_f1"]
            >= targets["minimum_mechanism_macro_f1"]
        ),
        "active_edge_support": (
            diagnostics["active_support_f1"]
            >= targets["minimum_active_support_f1"]
        ),
        "edge_sign_recovery": (
            diagnostics["active_sign_accuracy"]
            >= targets["minimum_sign_accuracy"]
        ),
        "loop_geometry": (
            diagnostics["loop_geometry"]
            >= targets["minimum_loop_geometry"]
        ),
        "stability_radius_geometry": (
            diagnostics["rho_spearman"]
            >= targets["minimum_rho_spearman"]
        ),
        "return_geometry": (
            diagnostics["return_time_spearman"]
            >= targets["minimum_return_spearman"]
        ),
        "recovery_geometry": (
            diagnostics["recovery_time_spearman"]
            >= targets["minimum_recovery_spearman"]
        ),
        "matched_marginal_calibration": (
            diagnostics["matched_menu_half_l1"]
            <= targets["maximum_matched_menu_half_l1"]
            and diagnostics["matched_choice_tv"]
            <= targets["maximum_matched_choice_tv"]
        ),
        "matched_mechanism_discrimination": (
            diagnostics["matched_mechanism_balanced_accuracy"]
            >= targets["minimum_matched_balanced_accuracy"]
        ),
        "return_mechanism_discrimination": (
            diagnostics["return_mechanism_balanced_accuracy"]
            >= targets["minimum_return_balanced_accuracy"]
        ),
        "history_gate_specificity": (
            diagnostics["gate_direction_margin"]
            >= targets["minimum_gate_direction_margin"]
        ),
        "active_author_signature": (
            diagnostics["active_same_author_auc"]
            >= targets["minimum_active_same_author_auc"]
        ),
        "hidden_alias_refusal": (
            diagnostics["alias_refusal_rate"]
            >= targets["minimum_alias_refusal_rate"]
        ),
        "null_calibration": (
            diagnostics["null_false_positive_rate"]
            <= targets["maximum_null_false_positive_rate"]
        ),
    }
    required_repetitions = min(
        int(targets["minimum_passing_repetitions"]),
        len(repetitions),
    )
    repetition_checks = {
        "matched_margins": int(np.sum(
            (
                repetitions["selection_creation_menu_half_l1"]
                <= targets["maximum_matched_menu_half_l1"]
            )
            & (
                repetitions["selection_creation_choice_tv"]
                <= targets["maximum_matched_choice_tv"]
            )
        )) >= required_repetitions,
        "matched_discrimination": int(np.sum(
            repetitions[
                "selection_creation_mechanism_balanced_accuracy"
            ] >= targets["minimum_matched_balanced_accuracy"]
        )) >= required_repetitions,
        "type_recovery": int(np.sum(
            repetitions["mechanism_macro_f1"]
            >= targets["minimum_mechanism_macro_f1"]
        )) >= required_repetitions,
    }
    checks.update({
        f"repetition_{name}": passed
        for name, passed in repetition_checks.items()
    })
    identification_core = (
        checks["matched_marginal_calibration"]
        and checks["matched_mechanism_discrimination"]
        and checks["hidden_alias_refusal"]
        and checks["null_calibration"]
    )
    if not checks["matched_marginal_calibration"]:
        decision = "M4_B_INVALID_WORLD_CALIBRATION"
    elif not identification_core:
        decision = "M4_B_NO_GO_IDENTIFICATION"
    elif all(checks.values()):
        decision = "M4_B_ENDOGENOUS_OPPORTUNITY_ECOLOGY_DISCOVERY_PASS"
    else:
        decision = (
            "M4_B_ENDOGENOUS_OPPORTUNITY_ECOLOGY_DISCOVERY_"
            "PASS_WITH_SCOPE_CORRECTION"
        )
    return {
        "estimand_id": config["estimand_id"],
        "decision": decision,
        "checks": checks,
        "diagnostics": diagnostics,
        "world_summary": summary.to_dict(orient="records"),
        "repetition_summary": repetitions.to_dict(orient="records"),
        "claim_boundary": (
            "Finite synthetic opportunity ecology only. The result may "
            "separate selection, creation, return, feedback, and observable "
            "history gates; it does not name a psychological construct or "
            "identify these mechanisms in natural text."
        ),
    }


def _report(
    decision: dict[str, Any],
    summary: pd.DataFrame,
    repetitions: pd.DataFrame,
) -> str:
    checks = "\n".join(
        f"- {'PASS' if passed else 'FAIL'}: `{name}`"
        for name, passed in decision["checks"].items()
    )
    diagnostics = "\n".join(
        f"- `{name}`: {value:.6f}"
        for name, value in decision["diagnostics"].items()
    )
    return f"""# SUICA M4-B Endogenous Opportunity Ecology Discovery

Decision: `{decision["decision"]}`

## Development question

Can identical population-level topic/situation marginals arise from different
author mechanisms: opportunity selection, opportunity generation, feedback,
return dynamics, and observable history gates?

The estimator uses three disjoint roles. Calibration fits the kernels,
selection chooses a registered candidate family, and evaluation is untouched
until the final mechanism audit.

## Discovery checks

{checks}

## Diagnostics

{diagnostics}

## World summary

{summary.to_markdown(index=False)}

## Matched-marginal repetitions

{repetitions.to_markdown(index=False)}

## Interpretation

The primary estimand is a difference in mechanism under matched menu and
choice marginals. Same-author AUC is secondary. Hidden opportunity-source
aliases must refuse even if the total menu remains predictable. All labels
refer to planted simulator channels, not personality, preference, state, or
emotion in human text.

The full feedback-loop geometry is retained. The failed spectral-radius rank
gate is a scope correction: a noisy matrix may preserve its pairwise geometry
while its largest eigenvalue changes order under small perturbations. M4-B
therefore does not license an author stability, criticality, or burst-threshold
score from `rho(J)`.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m4_opportunity_ecology.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results" / "m4_opportunity_ecology",
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=None,
        help="Optional diagnostic cap; the saved config remains unchanged.",
    )
    args = parser.parse_args()
    config = _load(args.config)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    repetition_rows: list[dict[str, Any]] = []
    audit_thresholds = config["audit"]

    repetitions_to_run = (
        int(config["repetitions"])
        if args.repetitions is None
        else min(int(config["repetitions"]), args.repetitions)
    )
    for repetition in range(repetitions_to_run):
        estimates: dict[str, Any] = {}
        audits: dict[str, dict[str, Any]] = {}
        expected_labels: list[str] = []
        predicted_labels: list[str] = []
        for world_index, world in enumerate(config["worlds"]):
            seed = (
                int(config["seed"])
                + repetition * 100_003
                + world_index * 1_009
            )
            observed, truth = generate_m4_opportunity_world(
                world=world,
                spec=M4OpportunitySpec(**config["base_spec"]),
                seed=seed,
            )
            estimate = fit_m4_opportunity_ecology(
                observed,
                **config["estimator"],
            )
            audit = audit_m4_opportunity_ecology(
                estimate,
                truth,
                **audit_thresholds,
            )
            labels = audit.pop("predicted_labels")
            expected_labels.extend([world] * len(labels))
            predicted_labels.extend(labels)
            audit["menu_marginal"] = json.dumps(
                audit["menu_marginal"],
                separators=(",", ":"),
            )
            audit["choice_marginal"] = json.dumps(
                audit["choice_marginal"],
                separators=(",", ":"),
            )
            audit["selected_models"] = json.dumps(
                audit["selected_models"],
                sort_keys=True,
                separators=(",", ":"),
            )
            audit.update({"repetition": repetition, "seed": seed})
            rows.append(audit)
            estimates[world] = estimate
            audits[world] = {
                **audit,
                "menu_marginal": json.loads(audit["menu_marginal"]),
                "choice_marginal": json.loads(audit["choice_marginal"]),
            }
        matched = _matched_metrics(
            estimates,
            audits,
            audit_thresholds,
        )
        matched["mechanism_macro_f1"] = float(f1_score(
            expected_labels,
            predicted_labels,
            average="macro",
            zero_division=0.0,
        ))
        matched["repetition"] = repetition
        repetition_rows.append(matched)

    metrics = pd.DataFrame(rows)
    repetitions = pd.DataFrame(repetition_rows)
    summary = _summarize(metrics)
    decision = _decision(metrics, repetitions, summary, config)
    metrics.to_csv(args.output_dir / "metrics.csv", index=False)
    repetitions.to_csv(
        args.output_dir / "matched_marginal_metrics.csv",
        index=False,
    )
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
    report = _report(decision, summary, repetitions)
    (args.output_dir / "report.md").write_text(report, encoding="utf-8")
    (
        ROOT / "reports" / "SUICA_M4_OPPORTUNITY_ECOLOGY_DISCOVERY.md"
    ).write_text(report, encoding="utf-8")
    print(json.dumps(decision, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
