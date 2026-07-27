#!/usr/bin/env python3
"""Run the V8.2 vector-query and evidence-fidelity planted experiment."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    append_ledger_event,
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_evidence import (  # noqa: E402
    evidence_node,
    evaluate_evidence_fidelity,
    simulate_evidence_world,
    validate_evidence_graph,
    write_evidence_artifact,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "v8_full_experiment.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "v8_full" / "v8_2_evidence")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    evidence = config["evidence"]
    authors = min(120, int(evidence["authors"])) if args.quick else int(evidence["authors"])
    bootstrap_draws = min(500, int(evidence["bootstrap_draws"])) if args.quick else int(evidence["bootstrap_draws"])
    seed = int(config["seed"])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = write_run_manifest(
        args.output_dir / "manifest.json",
        repository_root=ROOT,
        input_paths=[args.config],
        config_path=args.config,
        code_paths=[Path(__file__), ROOT / "suica_core" / "v8_evidence.py"],
        estimand_id="V8.2-evidence-necessity-sufficiency",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    planted = simulate_evidence_world(
        seed=seed,
        authors=authors,
        segments_per_author=int(evidence["segments_per_author"]),
        dimensions=int(evidence["dimensions"]),
        causal_segments=int(evidence["causal_segments"]),
    )
    summary, rows = evaluate_evidence_fidelity(
        planted,
        seed=seed + 1,
        select_count=int(evidence["causal_segments"]),
        bootstrap_draws=bootstrap_draws,
    )
    null_world = simulate_evidence_world(
        seed=seed + 2,
        authors=authors,
        segments_per_author=int(evidence["segments_per_author"]),
        dimensions=int(evidence["dimensions"]),
        causal_segments=int(evidence["causal_segments"]),
        null=True,
    )
    null_summary, null_rows = evaluate_evidence_fidelity(
        null_world,
        seed=seed + 3,
        select_count=int(evidence["causal_segments"]),
        bootstrap_draws=bootstrap_draws,
    )
    frame = pd.DataFrame(rows)
    frame["world"] = "planted"
    null_frame = pd.DataFrame(null_rows)
    null_frame["world"] = "null"
    pd.concat([frame, null_frame], ignore_index=True).to_csv(
        args.output_dir / "metrics_by_author.csv", index=False
    )

    artifact_path = (args.output_dir / "evidence_artifact.json").resolve()
    relative_artifact = str(artifact_path.relative_to(ROOT.resolve()))
    artifact_hash = write_evidence_artifact(
        artifact_path,
        source_span_ids=["plant-support", "plant-counter"],
        measurements={
            "necessity_advantage": float(summary["necessity_advantage_mean"]),
            "null_uncertainty_refusal_rate": float(null_summary["uncertainty_refusal_rate"]),
        },
    )
    graph = {
        "E-support": evidence_node(
            node_id="E-support",
            kind="supporting",
            artifact_path=relative_artifact,
            artifact_hash=artifact_hash,
            source_span_ids=["plant-support"],
            measurement_field="necessity_advantage",
            observed_value=float(summary["necessity_advantage_mean"]),
        ),
        "E-counter": evidence_node(
            node_id="E-counter",
            kind="counterevidence",
            artifact_path=relative_artifact,
            artifact_hash=artifact_hash,
            source_span_ids=["plant-counter"],
            measurement_field="null_uncertainty_refusal_rate",
            observed_value=float(null_summary["uncertainty_refusal_rate"]),
        ),
    }
    valid_errors = validate_evidence_graph(graph, repository_root=ROOT)
    attacks: list[dict[str, Any]] = []
    mutations = {
        "node_hash": lambda candidate: candidate["E-support"].__setitem__("node_sha256", "1" * 64),
        "artifact_hash": lambda candidate: candidate["E-support"].__setitem__("artifact_hash", "2" * 64),
        "dangling_span": lambda candidate: candidate["E-support"].__setitem__("source_span_ids", ["missing"]),
        "forged_value": lambda candidate: candidate["E-support"].__setitem__("observed_value", -999.0),
    }
    for name, mutate in mutations.items():
        candidate = copy.deepcopy(graph)
        mutate(candidate)
        errors = validate_evidence_graph(candidate, repository_root=ROOT)
        attacks.append({"attack": name, "refused": bool(errors), "errors": "|".join(errors)})
    attack_frame = pd.DataFrame(attacks)
    attack_frame.to_csv(args.output_dir / "attack_matrix.csv", index=False)
    (args.output_dir / "evidence_graph.json").write_text(
        json.dumps(graph, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    necessity_sd = float(frame["necessity_advantage"].std(ddof=1))
    standardized_necessity = (
        float(summary["necessity_advantage_mean"]) / max(necessity_sd, 1e-12)
    )
    gates = evidence["gates"]
    checks = {
        "evidence_precision": summary["evidence_precision_ci_lower"] >= float(gates["min_precision_lcb"]),
        "evidence_recall": summary["evidence_recall_ci_lower"] >= float(gates["min_recall_lcb"]),
        "necessity_ci": summary["necessity_advantage_ci_lower"] > 0,
        "necessity_effect": standardized_necessity >= 0.5,
        "sufficiency_median": summary["sufficiency_ratio_median"] >= float(gates["min_sufficiency_median"]),
        "sufficiency_lcb": summary["sufficiency_ratio_ci_lower"] >= float(gates["min_sufficiency_lcb"]),
        "paraphrase_stability": summary["paraphrase_change_sem_q95"] <= float(gates["max_paraphrase_change_sem_q95"]),
        "mechanism_sensitivity": summary["mechanism_flip_detection_rate"] >= float(gates["min_mechanism_flip_detection_rate"]),
        "null_uncertainty_refusal": null_summary["uncertainty_refusal_rate"] >= 0.90,
        "valid_graph": not valid_errors,
        "tamper_refusal": bool(attack_frame["refused"].all()),
    }
    metric_rows = [
        {"world": "planted", **summary, "standardized_necessity": standardized_necessity},
        {"world": "null", **null_summary, "standardized_necessity": None},
    ]
    pd.DataFrame(metric_rows).to_csv(args.output_dir / "metrics.csv", index=False)
    decision = {
        "status": "V8_2_EXPLANATION_FIDELITY_PASS" if all(checks.values()) else "V8_2_EXPLANATION_FIDELITY_NOT_CLOSED",
        "authors_per_world": authors,
        "checks": checks,
        "valid_graph_errors": valid_errors,
        "claim_boundary": (
            "Technical explanation fidelity for a planted additive vector functional. "
            "No psychological or clinical interpretation is licensed."
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
        "# SUICA V8.2 Explanation Fidelity\n\n"
        f"Status: `{decision['status']}`\n\n"
        f"{pd.DataFrame(metric_rows).round(4).to_markdown(index=False)}\n\n"
        "Evidence selection is tested against nuisance-matched random spans, "
        "harmless orthogonal perturbations, mechanism flips, and graph tampering.\n"
    )
    (args.output_dir / "report.md").write_text(report, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
