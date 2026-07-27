#!/usr/bin/env python3
"""Run the V8.3 planted-world component recovery and refusal matrix."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    append_ledger_event,
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_simulation import SimulationSpec, run_simulation_repetition  # noqa: E402


METRICS = (
    "theta_geometry_r",
    "theta_same_author_auc",
    "state_r",
    "state_variance_share_abs_error",
    "choice_probability_r",
    "choice_logloss_skill",
    "response_operator_r",
    "response_heldout_r2",
    "response_own_vs_stranger_delta_mse",
    "history_operator_r",
    "history_heldout_r2",
    "max_off_target_abs_r",
    "min_target_alignment_minus_crosstalk",
)


def _summarize(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for world, group in frame.groupby("world", observed=True, sort=True):
        for metric in METRICS:
            if metric not in group:
                continue
            values = group[metric].replace([np.inf, -np.inf], np.nan).dropna().to_numpy(float)
            if not len(values):
                continue
            rows.append({
                "world": world,
                "metric": metric,
                "n": len(values),
                "mean": float(np.mean(values)),
                "ci_lower": float(np.mean(values) - 1.96 * np.std(values, ddof=1) / np.sqrt(len(values))) if len(values) > 1 else float(values[0]),
                "ci_upper": float(np.mean(values) + 1.96 * np.std(values, ddof=1) / np.sqrt(len(values))) if len(values) > 1 else float(values[0]),
                "q025": float(np.quantile(values, 0.025)),
                "q975": float(np.quantile(values, 0.975)),
            })
    return pd.DataFrame(rows)


def _value(summary: pd.DataFrame, world: str, metric: str, field: str) -> float:
    selected = summary.loc[
        summary["world"].eq(world) & summary["metric"].eq(metric),
        field,
    ]
    return float(selected.iloc[0]) if len(selected) else float("nan")


def _refusal_checks(frame: pd.DataFrame) -> dict[str, bool]:
    expectations = {
        "missing_menu": {"choice": "REFUSE_MENU_UNOBSERVED"},
        "single_occasion": {
            "theta": "REFUSE_SINGLE_OCCASION",
            "state": "REFUSE_SINGLE_OCCASION",
            "choice": "REFUSE_SINGLE_OCCASION",
            "response": "REFUSE_SINGLE_OCCASION",
            "history": "REFUSE_SINGLE_OCCASION",
        },
        "nonrandom_condition": {"response": "REFUSE_CONDITION_NOT_RANDOMIZED"},
        "hidden_history": {"history": "REFUSE_HISTORY_UNOBSERVED"},
        "model_drift": {
            "theta": "REFUSE_MODEL_DRIFT",
            "state": "REFUSE_MODEL_DRIFT",
            "choice": "REFUSE_MODEL_DRIFT",
            "response": "REFUSE_MODEL_DRIFT",
            "history": "REFUSE_MODEL_DRIFT",
        },
    }
    checks: dict[str, bool] = {}
    for world, components in expectations.items():
        panel = frame.loc[frame["world"].eq(world)]
        for component, expected in components.items():
            checks[f"{world}::{component}"] = bool(
                len(panel) and panel[f"{component}_status"].eq(expected).all()
            )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "v8_full_experiment.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "v8_full" / "v8_3_simulation")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    simulation = config["simulation"]
    repetitions = min(12, int(simulation["repetitions"])) if args.quick else int(simulation["repetitions"])
    persons = min(120, int(simulation["persons"])) if args.quick else int(simulation["persons"])
    spec = SimulationSpec(
        persons=persons,
        sessions=int(simulation["sessions"]),
        units_per_session=int(simulation["units_per_session"]),
        dimensions=int(simulation["dimensions"]),
        condition_dimensions=int(simulation["condition_dimensions"]),
        history_dimensions=int(simulation["history_dimensions"]),
        choices=int(simulation["choices"]),
        choice_opportunities=int(simulation["choice_opportunities"]),
        choice_smoothing=float(simulation["choice_smoothing"]),
        noise_sd=float(simulation["noise_sd"]),
        ridge=float(simulation["ridge"]),
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = write_run_manifest(
        args.output_dir / "manifest.json",
        repository_root=ROOT,
        input_paths=[args.config],
        config_path=args.config,
        code_paths=[Path(__file__), ROOT / "suica_core" / "v8_simulation.py"],
        estimand_id="V8.3-theta-state-choice-response-history-identification",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    rows: list[dict[str, Any]] = []
    seed_base = int(config["seed"])
    for world_index, world in enumerate(simulation["worlds"]):
        for repetition in range(repetitions):
            rows.append(run_simulation_repetition(
                seed=seed_base + world_index * 100_000 + repetition,
                world=str(world),
                spec=spec,
            ))
    frame = pd.DataFrame(rows)
    summary = _summarize(frame)
    frame.to_csv(args.output_dir / "metrics_by_repetition.csv", index=False)
    summary.to_csv(args.output_dir / "metrics.csv", index=False)

    refusal_checks = _refusal_checks(frame)
    gates = simulation["gates"]
    positive_worlds = ("identified_independent", "identified_coupled")
    checks = {
        "theta_geometry": min(
            _value(summary, world, "theta_geometry_r", "ci_lower") for world in positive_worlds
        ) >= float(gates["min_theta_geometry_lcb"]),
        "theta_auc": min(
            _value(summary, world, "theta_same_author_auc", "ci_lower") for world in positive_worlds
        ) >= float(gates["min_theta_auc_lcb"]),
        "state_recovery": min(
            _value(summary, world, "state_r", "ci_lower") for world in positive_worlds
        ) >= float(gates["min_state_r_lcb"]),
        "state_variance_share": max(
            _value(summary, world, "state_variance_share_abs_error", "ci_upper")
            for world in positive_worlds
        ) <= float(gates["max_state_share_error"]),
        "choice_recovery": min(
            _value(summary, world, "choice_probability_r", "ci_lower") for world in positive_worlds
        ) >= float(gates["min_choice_r_lcb"]),
        "choice_skill": min(
            _value(summary, world, "choice_logloss_skill", "ci_lower") for world in positive_worlds
        ) >= float(gates["min_choice_logloss_skill"]),
        "response_recovery": min(
            _value(summary, world, "response_operator_r", "ci_lower") for world in positive_worlds
        ) >= float(gates["min_response_r_lcb"]),
        "response_prediction": min(
            _value(summary, world, "response_heldout_r2", "ci_lower") for world in positive_worlds
        ) >= float(gates["min_response_r2_lcb"]),
        "response_own_vs_stranger": min(
            _value(summary, world, "response_own_vs_stranger_delta_mse", "ci_lower")
            for world in positive_worlds
        ) > 0,
        "history_recovery": min(
            _value(summary, world, "history_operator_r", "ci_lower") for world in positive_worlds
        ) >= float(gates["min_history_r_lcb"]),
        "history_prediction": min(
            _value(summary, world, "history_heldout_r2", "ci_lower") for world in positive_worlds
        ) >= float(gates["min_history_r2_lcb"]),
        "independent_crosstalk": _value(
            summary,
            "identified_independent",
            "min_target_alignment_minus_crosstalk",
            "ci_lower",
        ) >= float(gates["min_target_crosstalk_margin"]),
        "null_author_auc": _value(
            summary, "null_components", "theta_same_author_auc", "ci_upper"
        ) <= float(gates["max_null_auc"]),
        "wrong_design_refusal": all(refusal_checks.values()),
    }
    refusal_rows = [
        {"attack": key, "passed": value}
        for key, value in refusal_checks.items()
    ]
    pd.DataFrame(refusal_rows).to_csv(args.output_dir / "attack_matrix.csv", index=False)
    numeric = {
        f"{world}__{metric}": group[metric].dropna().to_numpy(float)
        for world, group in frame.groupby("world", observed=True)
        for metric in METRICS
        if metric in group and group[metric].notna().any()
    }
    np.savez_compressed(args.output_dir / "joint_draws.npz", **numeric)
    decision = {
        "status": "V8_3_ORACLE_IDENTIFICATION_PASS" if all(checks.values()) else "V8_3_IDENTIFICATION_NOT_CLOSED",
        "persons_per_repetition": persons,
        "repetitions_per_world": repetitions,
        "worlds": list(map(str, simulation["worlds"])),
        "checks": checks,
        "refusal_checks": refusal_checks,
        "claim_boundary": (
            "Known synthetic-object recovery and design-refusal calibration only. "
            "Theta/state/choice/response/history are not personality, emotion, "
            "preference, or clinical constructs."
        ),
    }
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest.update(decision)
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    append_ledger_event(
        args.output_dir / "evidence_ledger.jsonl",
        {"estimand_id": manifest["estimand_id"], **decision},
    )
    write_artifact_inventory(args.output_dir, args.output_dir / "artifact_inventory.json")
    report = (
        "# SUICA V8.3 Planted-World Identification\n\n"
        f"Status: `{decision['status']}`\n\n"
        f"{summary.round(4).to_markdown(index=False)}\n\n"
        "All quantities are recovery metrics for known simulated objects. "
        "Wrong-design worlds must refuse the unidentified component.\n"
    )
    (args.output_dir / "report.md").write_text(report, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
