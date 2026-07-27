#!/usr/bin/env python3
"""Execute V8.1-V8.4 and compile the technical-core decision report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


PHASES = (
    ("v8_1_semantic", "run_suica_v8_semantic_transducer.py"),
    ("v8_3_simulation", "run_suica_v8_planted_worlds.py"),
    ("v8_2_evidence", "run_suica_v8_explanation_fidelity.py"),
    ("v8_4_realtext", "run_suica_v8_label_free_pilot.py"),
)


def _decision(path: Path) -> dict:
    if not path.exists():
        return {"status": "MISSING", "checks": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> pd.DataFrame:
    """Read an optional phase table without turning absence into a crash."""
    return pd.read_csv(path, keep_default_na=False) if path.exists() else pd.DataFrame()


def _metric_excerpt(output_root: Path) -> str:
    """Render the registered headline metrics from completed phase artifacts."""
    sections: list[str] = []
    semantic_decision = _decision(output_root / "v8_1_semantic" / "decision.json")
    semantic_metrics = _read_csv(output_root / "v8_1_semantic" / "metrics.csv")
    if not semantic_metrics.empty:
        rows = semantic_metrics.loc[
            semantic_metrics["metric"].isin([
                "macro_f1",
                "worst_event_f1",
                "span_accuracy",
                "polarity_mae",
                "intensity_mae",
                "null_false_positive_rate",
            ])
        ].copy()
        rows.insert(0, "phase", "V8.1")
        sections.append(
            "### V8.1 Semantic channel\n\n"
            f"Parse rate: `{semantic_decision.get('parse_rate', float('nan')):.4f}`; "
            f"stability: `{semantic_decision.get('stability', {})}`\n\n"
            f"{rows.round(4).to_markdown(index=False)}"
        )

    evidence = _read_csv(output_root / "v8_2_evidence" / "metrics.csv")
    if not evidence.empty:
        columns = [
            "world",
            "evidence_precision_mean",
            "evidence_precision_ci_lower",
            "evidence_recall_mean",
            "evidence_recall_ci_lower",
            "necessity_advantage_mean",
            "necessity_advantage_ci_lower",
            "sufficiency_ratio_median",
            "mechanism_flip_detection_rate",
            "uncertainty_refusal_rate",
        ]
        sections.append(
            "### V8.2 Explanation fidelity\n\n"
            f"{evidence[[column for column in columns if column in evidence]].round(4).to_markdown(index=False)}"
        )

    simulation = _read_csv(output_root / "v8_3_simulation" / "metrics.csv")
    if not simulation.empty:
        keys = {
            "theta_geometry_r",
            "theta_same_author_auc",
            "state_r",
            "choice_probability_r",
            "choice_logloss_skill",
            "response_operator_r",
            "response_heldout_r2",
            "history_operator_r",
            "history_heldout_r2",
        }
        rows = simulation.loc[
            simulation["world"].eq("identified_independent")
            & simulation["metric"].isin(keys)
        ].copy()
        sections.append(
            "### V8.3 Planted-world identification\n\n"
            f"{rows[['metric', 'mean', 'ci_lower', 'ci_upper']].round(4).to_markdown(index=False)}"
        )

    real_text = _read_csv(output_root / "v8_4_realtext" / "metrics.csv")
    if not real_text.empty:
        columns = [
            "corpus",
            "endpoint",
            "status",
            "n_discovery",
            "n_calibration",
            "n_confirmation",
            "baseline_confirmation_auc",
            "augmented_confirmation_auc",
            "delta_auc",
            "delta_auc_ci_lower",
            "delta_auc_ci_upper",
            "selected_semantic_weight",
            "semantic_segment_coverage",
            "run_cka",
        ]
        sections.append(
            "### V8.4 Label-free real text\n\n"
            f"{real_text[[column for column in columns if column in real_text]].round(4).to_markdown(index=False)}"
        )
    format_stability = _read_csv(
        output_root / "v8_4_realtext" / "format_perturbation.csv"
    )
    if not format_stability.empty:
        sections.append(
            "### V8.4 Formatting perturbation\n\n"
            f"{format_stability.round(4).to_markdown(index=False)}"
        )
    return "\n\n".join(sections)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "v8_full_experiment.json")
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=ROOT / "results" / "v8_full")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Compile existing phase decisions without rerunning experiments.",
    )
    args = parser.parse_args()
    args.output_root.mkdir(parents=True, exist_ok=True)
    execution_rows = []
    if not args.report_only:
        for phase, script in PHASES:
            command = [
                sys.executable,
                str(ROOT / "scripts" / script),
                "--config",
                str(args.config),
                "--output-dir",
                str(args.output_root / phase),
            ]
            if phase in {"v8_1_semantic", "v8_4_realtext"}:
                command.extend(["--env-file", str(args.env_file)])
            if args.quick:
                command.append("--quick")
            completed = subprocess.run(command, cwd=ROOT, check=False)
            execution_rows.append({
                "phase": phase,
                "script": script,
                "exit_code": int(completed.returncode),
            })
            if completed.returncode != 0:
                break
        execution = pd.DataFrame(execution_rows)
        execution.to_csv(args.output_root / "execution_status.csv", index=False)

    decisions = {
        phase: _decision(args.output_root / phase / "decision.json")
        for phase, _script in PHASES
    }
    technical_pass = (
        decisions["v8_1_semantic"].get("status") == "V8_1_SEMANTIC_CHANNEL_PASS"
        and decisions["v8_3_simulation"].get("status") == "V8_3_ORACLE_IDENTIFICATION_PASS"
        and decisions["v8_2_evidence"].get("status") == "V8_2_EXPLANATION_FIDELITY_PASS"
        and decisions["v8_4_realtext"].get("status") == "V8_4_LABEL_FREE_TECHNICAL_PILOT_PASS"
    )
    final = {
        "status": "V8_TECHNICAL_CORE_PASS" if technical_pass else "V8_TECHNICAL_CORE_NOT_CLOSED",
        "phase_statuses": {
            phase: value.get("status", "MISSING")
            for phase, value in decisions.items()
        },
        "human_validity_status": "V8_5_NOT_RUN",
        "claim_boundary": (
            "Technical core only. Even a full PASS would not validate personality, "
            "emotion, diagnosis, clinical utility, or cross-cultural psychological meaning."
        ),
    }
    (args.output_root / "final_decision.json").write_text(
        json.dumps(final, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    phase_table = pd.DataFrame([
        {"phase": phase, "status": value.get("status", "MISSING")}
        for phase, value in decisions.items()
    ])
    provenance = _decision(args.output_root / "provenance_audit.json")
    report = (
        "# SUICA V8 Full Technical Experiment Report\n\n"
        f"Overall status: `{final['status']}`\n\n"
        f"{phase_table.to_markdown(index=False)}\n\n"
        "A completed phase may validly end in `NOT_CLOSED`; this is an empirical "
        "gate result, not an execution failure.\n\n"
        f"{_metric_excerpt(args.output_root)}\n\n"
        "## Interpretation\n\n"
        "- V8.1 recovered the planted event codebook accurately and safely, but "
        "its registered numeric run-drift gate failed. The LLM is therefore not "
        "licensed as a measurement channel.\n"
        "- V8.2 and V8.3 establish that the evidence contract and the "
        "theta/state/choice/response/history decomposition work in planted "
        "worlds under identified designs. They do not establish human constructs.\n"
        "- V8.4 found no semantic increment over the frozen PANDORA V7 geometry. "
        "MEPS showed a positive corpus-local increment, but real-text run "
        "stability failed, so this remains a follow-up signal rather than a "
        "promoted result.\n\n"
        "## Provenance\n\n"
        f"Status: `{provenance.get('status', 'MISSING')}`; checked files: "
        f"`{provenance.get('checked_files', 0)}`; failed files: "
        f"`{provenance.get('failed_files', 0)}`.\n\n"
        "## Decision boundary\n\n"
        f"{final['claim_boundary']}\n\n"
        "V8.5 repeated-human measurement and external construct validation remain "
        "closed and were not simulated or inferred from these experiments.\n"
    )
    (ROOT / "reports" / "V8_FULL_TECHNICAL_EXPERIMENT_REPORT.md").write_text(
        report,
        encoding="utf-8",
    )
    print(json.dumps(final, ensure_ascii=False, indent=2))
    if args.report_only:
        return 0
    execution = pd.DataFrame(execution_rows)
    return 0 if len(execution) == len(PHASES) and execution["exit_code"].eq(0).all() else 2


if __name__ == "__main__":
    raise SystemExit(main())
