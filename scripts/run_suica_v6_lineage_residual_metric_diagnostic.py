#!/usr/bin/env python
"""Explain the L1 residual AUC result without changing its frozen endpoint.

This is explicitly post-hoc: it compares scalar split-half reliability and
multivariate author retrieval on the exact L1 source, views, and coordinates.
It never reads endpoint labels or emits raw text.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v6_lineage_compatibility import (  # noqa: E402
    _anchor_matrix,
    _load_comments,
    _paired_view_matrix,
)
from suica_core.joint_process import alignment_permutation_test, disjoint_block_views  # noqa: E402
from suica_core.lineage_compatibility import paired_reliability_change, reference_condition_residuals  # noqa: E402


COORDINATES = (
    "first_person_usage_v2",
    "directive_action_v2",
    "novelty_play_v2",
    "tension_core_v2",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Local gitignored PANDORA Tier-U parquet.")
    parser.add_argument("--config", type=Path, default=ROOT / "configs/v6_lineage_compatibility.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/v6_lineage_residual_metric_diagnostic")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/V6_LINEAGE_RESIDUAL_METRIC_DIAGNOSTIC.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg: dict[str, Any] = json.loads(args.config.read_text(encoding="utf-8"))
    spec = cfg["natural_residual_sensitivity"]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    comments, provenance = _load_comments(args.input, cfg)
    cohorts = {str(spec["reference_cohort"]), str(spec["reporting_cohort"])}
    selected = disjoint_block_views(
        comments.loc[comments["cohort"].isin(cohorts)],
        min_events_per_view=int(spec["technical_events_per_view"]),
        min_transitions_per_view=int(spec["technical_transitions_per_view"]),
        block_size=int(spec["block_size"]),
    ).reset_index(drop=True)
    if selected.empty:
        raise RuntimeError("no J1-compatible technical views available")
    values = _anchor_matrix(selected["body"])
    reference = selected["cohort"].eq(str(spec["reference_cohort"])).to_numpy()
    residual, residual_meta = reference_condition_residuals(
        values,
        selected["subreddit"].astype(str).to_numpy(),
        reference,
        min_reference_events=int(spec["minimum_reference_condition_events"]),
    )
    raw_left, raw_right = _paired_view_matrix(selected, values, str(spec["reporting_cohort"]))
    residual_left, residual_right = _paired_view_matrix(selected, residual, str(spec["reporting_cohort"]))
    if len(raw_left) != len(residual_left):
        raise RuntimeError("raw and residual author alignment diverged")
    rows = []
    for index, coordinate in enumerate(COORDINATES):
        change = paired_reliability_change(
            raw_left[:, index], raw_right[:, index],
            residual_left[:, index], residual_right[:, index],
            bootstrap_iterations=999,
            seed=int(cfg["seed"]) + 300 + index,
        )
        rows.append({"coordinate": coordinate, **change})
    scalar = pd.DataFrame(rows)
    raw_auc = alignment_permutation_test(
        raw_left, raw_right, permutations=int(spec["permutations"]), seed=int(cfg["seed"]) + 400
    )
    residual_auc = alignment_permutation_test(
        residual_left, residual_right, permutations=int(spec["permutations"]), seed=int(cfg["seed"]) + 401
    )
    auc_delta = float(residual_auc["observed_auc"] - raw_auc["observed_auc"])
    reliability_down = int(scalar["ci_hi"].lt(0.0).sum())
    reliability_up = int(scalar["ci_lo"].gt(0.0).sum())
    relation = (
        "AUC_RELIABILITY_DIVERGENCE" if auc_delta >= 0.02 and reliability_down > 0 else
        "AUC_AND_SCALAR_RELIABILITY_MOVE_TOGETHER" if auc_delta >= 0.02 and reliability_up == len(scalar) else
        "NO_SIMPLE_METRIC_DIVERGENCE"
    )
    result = {
        "run_name": "SUICA_V6_LINEAGE_RESIDUAL_METRIC_DIAGNOSTIC_V1_POSTHOC",
        "status": "POSTHOC_EXPLANATORY_ONLY",
        "provenance": provenance,
        "n_confirmation_authors": int(len(raw_left)),
        "multivariate_raw": raw_auc,
        "multivariate_residual": residual_auc,
        "residual_minus_raw_auc": auc_delta,
        "scalar_reliability_up": reliability_up,
        "scalar_reliability_down": reliability_down,
        "relation": relation,
        "residual_metadata": residual_meta,
        "claim_boundary": "metric interpretation only; no personality or centering-theorem reversal",
        "external_labels_read": False,
        "raw_text_persisted": False,
    }
    scalar.to_csv(args.output_dir / "scalar_reliability_change.csv", index=False)
    (args.output_dir / "residual_metric_diagnostic.json").write_text(json.dumps(result, indent=2, default=float) + "\n", encoding="utf-8")
    report = f"""# SUICA V6 Residual Metric Diagnostic\n\n## Status\n\n**POSTHOC_EXPLANATORY_ONLY.** This diagnostic was triggered by the frozen L1\nresidual AUC result. It does not alter L1, PRED-1, or the centering claims.\n\n## Same data, two metrics\n\n- J1-compatible confirmation authors: `{result['n_confirmation_authors']:,}`\n- raw/residual multivariate same-author AUC: `{raw_auc['observed_auc']:.4f}` / `{residual_auc['observed_auc']:.4f}`\n- residual minus raw AUC: `{auc_delta:+.4f}`\n- interpretation: `{relation}`\n\n### Per-coordinate split-half reliability\n\n{scalar.round(4).to_markdown(index=False)}\n\n## Reading\n\nA multivariate AUC uses the geometry of the four-coordinate vector, whereas a\nscalar split-half correlation retains one coordinate’s population variance. A\ndifference between them is an estimand/metric fact, not evidence that either\nraw or residual coordinates are personality. The residual transform is fitted\non discovery condition means only; labels and raw-text artifacts are absent.\n"""
    args.report.write_text(report, encoding="utf-8")
    print(json.dumps(result, indent=2, default=float))


if __name__ == "__main__":
    main()
