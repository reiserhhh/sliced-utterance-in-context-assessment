#!/usr/bin/env python
"""Recheck V3/V4 results as distinct estimands within the V6 guardrails.

This runner is intentionally label-free.  It does not ask whether an older
version or V6 is "right"; it tests whether fixed-rind conditional expression,
the V6 natural process, and condition-residualized expression are distinct and
internally reproducible objects under one current technical-replicate design.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.suica_v2_lib import fast_anchor_rates, score_slices_v2  # noqa: E402
from suica_core.joint_process import (  # noqa: E402
    alignment_permutation_test,
    cohort_from_bucket,
    disjoint_block_views,
    same_author_auc,
    stable_bucket,
)
from suica_core.lineage_compatibility import (  # noqa: E402
    paired_correlation_delta,
    reference_condition_residuals,
    span_spread_disjoint_views,
)
from suica_core.suica import PERSONALITY_LEAK_RE, fixed_token_slices_for_text  # noqa: E402


CONSTRUCTS = (
    "first_person_usage_v2",
    "directive_action_v2",
    "novelty_play_v2",
    "tension_core_v2",
)


def parse_args() -> argparse.Namespace:
    """Parse explicit local data and aggregate-only output destinations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Local gitignored PANDORA Tier-U parquet.")
    parser.add_argument("--config", type=Path, default=ROOT / "configs/v6_lineage_compatibility.json")
    parser.add_argument("--j1-result", type=Path, default=ROOT / "results/v6_joint_process_stage_j1/j1_result.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/v6_lineage_compatibility")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/V6_LINEAGE_COMPATIBILITY_AUDIT.md")
    return parser.parse_args()


def _cohort(author: str, namespace: str) -> str:
    return cohort_from_bucket(stable_bucket(str(author), namespace=namespace))


def _safe_span(values: pd.Series) -> float:
    numeric = pd.to_numeric(values, errors="coerce").dropna().to_numpy(float)
    return float(numeric.max() - numeric.min()) if len(numeric) > 1 else 0.0


def _load_comments(input_path: Path, cfg: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load only fields licensed for the label-free lineage audit."""
    if not input_path.exists():
        raise FileNotFoundError(f"missing local PANDORA source: {input_path}")
    comments = pd.read_parquet(input_path, columns=["author", "body", "created_utc", "subreddit"])
    source_rows = int(len(comments))
    comments["body"] = comments["body"].fillna("").astype(str)
    leak_mask = comments["body"].map(lambda text: bool(PERSONALITY_LEAK_RE.search(text)))
    minimum_chars = int(cfg["fixed_rind_compatibility"]["minimum_body_characters"])
    valid = comments.loc[~leak_mask & comments["body"].str.len().ge(minimum_chars)].copy()
    valid["created_utc"] = pd.to_numeric(valid["created_utc"], errors="coerce")
    valid = valid.dropna(subset=["created_utc"])
    valid["author"] = valid["author"].astype(str)
    valid["subreddit"] = valid["subreddit"].fillna("__missing__").astype(str)
    valid["_source_index"] = np.arange(len(valid), dtype=np.int64)
    valid["cohort"] = valid["author"].map(lambda author: _cohort(author, str(cfg["cohort_namespace"])))
    return valid, {
        "n_source_comments": source_rows,
        "n_excluded_personality_leakage": int(leak_mask.sum()),
        "n_after_text_guard": int(len(valid)),
        "external_labels_read": False,
        "raw_text_persisted": False,
    }


def _top_subreddit_by_author(comments: pd.DataFrame) -> pd.Series:
    """Select one deterministic observed rind for every author."""
    counts = comments.groupby(["author", "subreddit"], observed=True).size().rename("n").reset_index()
    return (
        counts.sort_values(["author", "n", "subreddit"], ascending=[True, False, True], kind="stable")
        .drop_duplicates("author")
        .set_index("author")["subreddit"]
    )


def _slice_rows_for_view(
    events: pd.DataFrame,
    *,
    author: str,
    arm: str,
    view: str,
    cfg: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, float]] | None:
    """Create equal token-budget slices in memory and emit non-text metadata."""
    spec = cfg["fixed_rind_compatibility"]
    selected = events.loc[events["technical_view"].eq(view)].sort_values(
        ["technical_block", "within_block_index"], kind="stable"
    )
    text = "\n".join(selected["body"].astype(str))
    pieces = fixed_token_slices_for_text(
        text,
        slice_tokens=int(spec["slice_tokens"]),
        stride=int(spec["slice_tokens"]),
        min_slice_tokens=24,
        max_slices=int(spec["slices_per_view"]),
    )
    if len(pieces) != int(spec["slices_per_view"]):
        return None
    rows = [
        {
            "author": str(author),
            "arm": str(arm),
            "technical_view": str(view),
            "slice_index": int(piece["slice_index"]),
            "slice_text": str(piece["slice_text"]),
        }
        for piece in pieces
    ]
    metadata = {
        "author": str(author),
        "arm": str(arm),
        "technical_view": str(view),
        "n_events": int(len(selected)),
        "n_subreddits": int(selected["subreddit"].nunique()),
        "time_span_days": _safe_span(selected["created_utc"]) / 86_400.0,
        "evaluated_tokens": int(sum(int(piece["token_count"]) for piece in pieces)),
    }
    return rows, metadata


def _fixed_rind_scalar_audit(comments: pd.DataFrame, cfg: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any]]:
    """Re-estimate the old fixed-versus-mixed precision claim with V6 splits."""
    spec = cfg["fixed_rind_compatibility"]
    cohort = str(spec["reporting_cohort"])
    work = comments.loc[comments["cohort"].eq(cohort)].copy()
    top = _top_subreddit_by_author(work)
    counts = work.groupby(["author", "subreddit"], observed=True).size().rename("n").reset_index()
    total = work.groupby("author", observed=True).size().rename("total")
    top_n = top.rename("top_subreddit").reset_index().merge(
        counts.rename(columns={"n": "top_n"}),
        left_on=["author", "top_subreddit"],
        right_on=["author", "subreddit"],
        how="left",
        validate="one_to_one",
    ).drop(columns="subreddit").set_index("author")
    top_n["other_n"] = total.reindex(top_n.index).to_numpy() - top_n["top_n"].to_numpy()
    work["_top_subreddit"] = work["author"].map(top)
    top_n["other_subreddits"] = (
        work.loc[~work["subreddit"].eq(work["_top_subreddit"])]
        .groupby("author", observed=True)["subreddit"].nunique()
        .reindex(top_n.index)
        .fillna(0)
    )
    events_per_arm = 2 * int(spec["blocks_per_view"]) * int(spec["block_size"])
    eligible = top_n.index[
        top_n["top_n"].ge(events_per_arm)
        & top_n["other_n"].ge(events_per_arm)
        & top_n["other_subreddits"].ge(int(spec["minimum_other_subreddits"]))
    ]
    work = work.loc[work["author"].isin(eligible)].copy()
    slice_rows: list[dict[str, Any]] = []
    view_meta: list[dict[str, Any]] = []
    rejected = {"span": 0, "view_support": 0}
    for author, group in work.groupby("author", observed=True, sort=False):
        top_subreddit = str(top.loc[author])
        fixed = group.loc[group["subreddit"].eq(top_subreddit)].copy()
        mixed = group.loc[~group["subreddit"].eq(top_subreddit)].copy()
        fixed_span = _safe_span(fixed["created_utc"])
        mixed_span = _safe_span(mixed["created_utc"])
        if fixed_span <= 0.0 or mixed_span <= 0.0 or min(fixed_span, mixed_span) / max(fixed_span, mixed_span) < float(spec["minimum_arm_span_ratio"]):
            rejected["span"] += 1
            continue
        arm_views: dict[str, pd.DataFrame] = {}
        for arm, arm_events in (("fixed", fixed), ("mixed", mixed)):
            views = span_spread_disjoint_views(
                arm_events,
                block_size=int(spec["block_size"]),
                blocks_per_view=int(spec["blocks_per_view"]),
            )
            if views.empty:
                arm_views = {}
                break
            arm_views[arm] = views
        if len(arm_views) != 2:
            rejected["view_support"] += 1
            continue
        candidate_rows: list[dict[str, Any]] = []
        candidate_meta: list[dict[str, Any]] = []
        for arm, views in arm_views.items():
            for view in ("left", "right"):
                constructed = _slice_rows_for_view(views, author=str(author), arm=arm, view=view, cfg=cfg)
                if constructed is None:
                    candidate_rows = []
                    break
                rows, meta = constructed
                candidate_rows.extend(rows)
                candidate_meta.append(meta)
            if not candidate_rows:
                break
        if not candidate_rows:
            rejected["view_support"] += 1
            continue
        slice_rows.extend(candidate_rows)
        view_meta.extend(candidate_meta)
    if not slice_rows:
        raise RuntimeError("no confirmation authors met frozen fixed-rind compatibility support")
    scored = score_slices_v2(pd.DataFrame(slice_rows))
    aggregate = scored.groupby(["author", "arm", "technical_view"], observed=True)[list(CONSTRUCTS)].mean().reset_index()
    complete = aggregate.pivot_table(index="author", columns=["arm", "technical_view"], values=list(CONSTRUCTS))
    required = [(construct, arm, view) for construct in CONSTRUCTS for arm in ("fixed", "mixed") for view in ("left", "right")]
    complete = complete.dropna(subset=required)
    rows: list[dict[str, Any]] = []
    for index, construct in enumerate(CONSTRUCTS):
        result = paired_correlation_delta(
            complete[(construct, "fixed", "left")].to_numpy(float),
            complete[(construct, "fixed", "right")].to_numpy(float),
            complete[(construct, "mixed", "left")].to_numpy(float),
            complete[(construct, "mixed", "right")].to_numpy(float),
            bootstrap_iterations=int(spec["bootstrap_iterations"]),
            seed=int(cfg["seed"]) + index,
        )
        rows.append({"construct": construct, "n_authors": int(len(complete)), **result})
    result_frame = pd.DataFrame(rows)
    historical = set(map(str, spec["historically_supported_constructs"]))
    target = result_frame.loc[result_frame["construct"].isin(historical)]
    all_positive = bool(len(target) == len(historical) and target["ci_lo"].gt(0.0).all())
    any_reverse = bool(target["ci_hi"].lt(0.0).any())
    if all_positive:
        relation = "UPHELD_SAME_ESTIMAND"
    elif any_reverse:
        relation = "CONTRADICTED_UNDER_CURRENT_IMPLEMENTATION"
    else:
        relation = "INCONCLUSIVE_NOT_A_REVERSAL"
    meta = pd.DataFrame(view_meta)
    paired_meta = meta.pivot_table(index="author", columns=["arm", "technical_view"], values=["time_span_days", "evaluated_tokens"])
    fixed_tokens = paired_meta["evaluated_tokens"].xs("fixed", level="arm", axis=1).mean(axis=1)
    mixed_tokens = paired_meta["evaluated_tokens"].xs("mixed", level="arm", axis=1).mean(axis=1)
    fixed_span = paired_meta["time_span_days"].xs("fixed", level="arm", axis=1).mean(axis=1)
    mixed_span = paired_meta["time_span_days"].xs("mixed", level="arm", axis=1).mean(axis=1)
    vector_left = complete.loc[:, [(construct, "fixed", "left") for construct in CONSTRUCTS]].to_numpy(float)
    vector_right = complete.loc[:, [(construct, "fixed", "right") for construct in CONSTRUCTS]].to_numpy(float)
    mixed_left = complete.loc[:, [(construct, "mixed", "left") for construct in CONSTRUCTS]].to_numpy(float)
    mixed_right = complete.loc[:, [(construct, "mixed", "right") for construct in CONSTRUCTS]].to_numpy(float)
    vector_metrics = {
        "fixed_same_author_auc": float(same_author_auc(vector_left, vector_right)),
        "mixed_same_author_auc": float(same_author_auc(mixed_left, mixed_right)),
    }
    summary = {
        "reporting_cohort": cohort,
        "candidate_authors_before_span_and_view": int(len(eligible)),
        "n_complete_authors": int(len(complete)),
        "rejected": rejected,
        "events_per_arm": int(events_per_arm),
        "evaluated_slices_per_view": int(spec["slices_per_view"]),
        "median_fixed_to_mixed_token_ratio": float(np.median(fixed_tokens / np.maximum(mixed_tokens, 1.0))),
        "median_fixed_to_mixed_span_ratio": float(np.median(fixed_span / np.maximum(mixed_span, 1e-12))),
        "relation": relation,
        "historical_constructs_positive": int(target["ci_lo"].gt(0.0).sum()),
        "historical_constructs_total": int(len(historical)),
        **vector_metrics,
    }
    return result_frame, summary, {"aggregate": aggregate, "view_metadata": meta}


def _anchor_matrix(texts: pd.Series) -> np.ndarray:
    """Return the four frozen legacy scalar coordinates without label reads."""
    rows = []
    for text in texts.astype(str):
        rates = fast_anchor_rates(text)
        rows.append([
            float(rates["self_focus_rate"]),
            float(math.sqrt(max(0.0, rates["directive_rate"]) * max(0.0, rates["second_person_rate"]))),
            float(rates["novelty_play_rate"]),
            float(0.40 * rates["projective_tension_rate"] + 0.35 * rates["uncertainty_rate"] + 0.25 * rates["conflict_threat_rate"]),
        ])
    return np.asarray(rows, dtype=float)


def _paired_view_matrix(selected: pd.DataFrame, values: np.ndarray, cohort: str) -> tuple[np.ndarray, np.ndarray]:
    """Aggregate event coordinates by technical view and align paired authors."""
    columns = [f"feature_{index}" for index in range(values.shape[1])]
    work = selected.loc[:, ["author", "technical_view", "cohort"]].copy()
    work[columns] = values
    means = work.groupby(["author", "technical_view", "cohort"], observed=True)[columns].mean().reset_index()
    means = means.loc[means["cohort"].eq(cohort)]
    left = means.loc[means["technical_view"].eq("left")].set_index("author")[columns]
    right = means.loc[means["technical_view"].eq("right")].set_index("author")[columns]
    authors = sorted(set(left.index).intersection(right.index))
    return left.loc[authors].to_numpy(float), right.loc[authors].to_numpy(float)


def _natural_residual_sensitivity(comments: pd.DataFrame, cfg: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Compare raw and discovery-condition-residualized anchor geometry.

    This deliberately uses the J1 technical view constructor.  The endpoint is
    author retrieval, not a claim that condition subtraction creates a cleaner
    personality signal.
    """
    spec = cfg["natural_residual_sensitivity"]
    use_cohorts = {str(spec["reference_cohort"]), str(spec["reporting_cohort"])}
    source = comments.loc[comments["cohort"].isin(use_cohorts)].copy()
    selected = disjoint_block_views(
        source,
        min_events_per_view=int(spec["technical_events_per_view"]),
        min_transitions_per_view=int(spec["technical_transitions_per_view"]),
        block_size=int(spec["block_size"]),
    ).reset_index(drop=True)
    if selected.empty:
        raise RuntimeError("no J1-compatible event-disjoint views for residual sensitivity")
    selected["cohort"] = selected["author"].astype(str).map(
        lambda author: _cohort(author, str(cfg["cohort_namespace"]))
    )
    values = _anchor_matrix(selected["body"])
    reference = selected["cohort"].eq(str(spec["reference_cohort"])).to_numpy()
    residual, residual_meta = reference_condition_residuals(
        values,
        selected["subreddit"].astype(str).to_numpy(),
        reference,
        min_reference_events=int(spec["minimum_reference_condition_events"]),
    )
    rows: list[dict[str, Any]] = []
    for index, (name, matrix) in enumerate((("raw_anchor_coordinates", values), ("discovery_condition_residual", residual))):
        left, right = _paired_view_matrix(selected, matrix, str(spec["reporting_cohort"]))
        alignment = alignment_permutation_test(
            left,
            right,
            permutations=int(spec["permutations"]),
            seed=int(cfg["seed"]) + 100 + index,
        )
        rows.append({"representation": name, "n_confirmation_authors": int(len(left)), **alignment})
    frame = pd.DataFrame(rows)
    raw_auc = float(frame.loc[frame["representation"].eq("raw_anchor_coordinates"), "observed_auc"].iloc[0])
    residual_auc = float(frame.loc[frame["representation"].eq("discovery_condition_residual"), "observed_auc"].iloc[0])
    delta = residual_auc - raw_auc
    if delta <= -0.02:
        relation = "COMPATIBLE_ESTIMAND_CHANGE_RESIDUAL_WEAKER"
    elif delta >= 0.02:
        relation = "INVESTIGATE_SCOPE_OR_IMPLEMENTATION_DIFFERENCE"
    else:
        relation = "NO_MATERIAL_RETRIEVAL_CHANGE"
    summary = {
        "n_selected_events": int(len(selected)),
        "n_selected_authors": int(selected["author"].nunique()),
        "raw_to_residual_auc_delta": float(delta),
        "relation": relation,
        **residual_meta,
    }
    return frame, summary


def _read_j1_reference(path: Path) -> dict[str, Any]:
    """Read an existing frozen J1 artifact without rerunning or refitting it."""
    if not path.exists():
        return {"available": False, "reason": f"missing cached J1 artifact: {path}"}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "available": True,
        "decision": data.get("decision"),
        "claim_boundary": data.get("claim_boundary"),
        "ordered_dependence_tested": data.get("ordered_dependence_tested"),
        "alignment": data.get("alignment", []),
        "cross_representation_confirmation_geometry_r": data.get("cross_representation_confirmation_geometry_r"),
        "provenance": data.get("provenance", {}),
    }


def _assumption_delta_table(fixed_summary: dict[str, Any], residual_summary: dict[str, Any], j1: dict[str, Any]) -> pd.DataFrame:
    """Make differences in estimand explicit instead of reporting a winner."""
    return pd.DataFrame([
        {
            "claim_id": "PRED-1",
            "prior_estimand": "fixed selected rind vs mixed rind scalar split-half precision",
            "v6_counterpart": "event-disjoint, span-constrained fixed vs mixed scalar technical views",
            "outcome": fixed_summary["relation"],
            "relation": "UPHELD_SAME_ESTIMAND" if fixed_summary["relation"] == "UPHELD_SAME_ESTIMAND" else "NEEDS_SCOPE_REVIEW",
        },
        {
            "claim_id": "C2/CENTERING",
            "prior_estimand": "raw selection-plus-expression versus condition-centred expression",
            "v6_counterpart": "discovery-only subreddit mean subtraction on J1-compatible anchor coordinates",
            "outcome": residual_summary["relation"],
            "relation": "COMPATIBLE_DIFFERENT_ESTIMAND",
        },
        {
            "claim_id": "V6-J1",
            "prior_estimand": "not present in V3/V4",
            "v6_counterpart": "natural selection-expression-transition geometry",
            "outcome": str(j1.get("decision", "NOT_AVAILABLE")),
            "relation": "NEW_SEPARATE_OBJECT",
        },
        {
            "claim_id": "V6-J3",
            "prior_estimand": "old dynamic/motion hypotheses under their own support worlds",
            "v6_counterpart": "finite centred within-block ordered-transition operator",
            "outcome": "REFUSE_NO_CALIBRATED_ORDER_SUPPORT",
            "relation": "COMPATIBLE_DIFFERENT_ESTIMAND_NOT_A_REVERSAL",
        },
        {
            "claim_id": "V6_FACTOR_DISCOVERY",
            "prior_estimand": "predefined lexical construct reliability",
            "v6_counterpart": "new shared low-dimensional factor-axis confirmation",
            "outcome": "NO_NEW_FACTOR_FAMILY_CONFIRMED",
            "relation": "NOT_A_TEST_OF_PRIOR_CONSTRUCT_VALIDITY",
        },
    ])


def _markdown_table(frame: pd.DataFrame, *, digits: int = 4) -> str:
    return frame.round(digits).to_markdown(index=False) if not frame.empty else "_No rows._"


def main() -> None:
    """Run the frozen lineage audit and write aggregate-only artifacts."""
    args = parse_args()
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    comments, provenance = _load_comments(args.input, cfg)
    fixed_frame, fixed_summary, _ = _fixed_rind_scalar_audit(comments, cfg)
    residual_frame, residual_summary = _natural_residual_sensitivity(comments, cfg)
    j1_reference = _read_j1_reference(args.j1_result)
    assumptions = _assumption_delta_table(fixed_summary, residual_summary, j1_reference)
    result = {
        "run_name": cfg["run_name"],
        "provenance": provenance,
        "fixed_rind_compatibility": fixed_summary,
        "natural_residual_sensitivity": residual_summary,
        "j1_cached_reference": j1_reference,
        "claim_boundary": "lineage compatibility and estimand separation only; no personality or clinical inference",
        "external_labels_read": False,
        "raw_text_persisted": False,
    }
    fixed_frame.to_csv(args.output_dir / "fixed_rind_constructs.csv", index=False)
    residual_frame.to_csv(args.output_dir / "natural_residual_sensitivity.csv", index=False)
    assumptions.to_csv(args.output_dir / "assumption_delta.csv", index=False)
    (args.output_dir / "lineage_result.json").write_text(json.dumps(result, indent=2, default=float) + "\n", encoding="utf-8")
    j1_table = pd.DataFrame(j1_reference.get("alignment", []))
    report = f"""# SUICA V6 Lineage Compatibility Audit\n\n## Scope\n\nThis is a label-free compatibility audit, not a personality prediction or a vote\nbetween versions. It keeps conditional fixed-rind expression, natural selection\nplus expression, and condition-residualized expression as separate objects.\n\n- source comments after explicit personality-report guard: `{provenance['n_after_text_guard']:,}`\n- external labels read: `{provenance['external_labels_read']}`\n- raw text persisted: `{provenance['raw_text_persisted']}`\n\n## A. Fixed-rind compatibility endpoint\n\n**Relation:** `{fixed_summary['relation']}`.\n\n- confirmation authors before frozen span/view filters: `{fixed_summary['candidate_authors_before_span_and_view']:,}`\n- complete paired authors: `{fixed_summary['n_complete_authors']:,}`\n- fixed/mixed median evaluated-token ratio: `{fixed_summary['median_fixed_to_mixed_token_ratio']:.3f}`\n- fixed/mixed median time-span ratio: `{fixed_summary['median_fixed_to_mixed_span_ratio']:.3f}`\n- vector same-author AUC, fixed/mixed: `{fixed_summary['fixed_same_author_auc']:.4f}` / `{fixed_summary['mixed_same_author_auc']:.4f}`\n\n{_markdown_table(fixed_frame)}\n\nInterpretation: the table tests the historical **conditional-expression precision**\nclaim with event-disjoint, time-spread technical views. It does not measure a\npersonality trait. `tension_core_v2` is reported but does not count toward the\nhistorical three-construct decision because its old positive effect was already\nretracted as a temporal-clustering artifact.\n\n## B. Natural residualization sensitivity\n\n**Relation:** `{residual_summary['relation']}`.\n\n- J1-compatible selected events/authors: `{residual_summary['n_selected_events']:,}` / `{residual_summary['n_selected_authors']:,}`\n- discovery-supported subreddit conditions: `{residual_summary['reference_conditions_supported']:,}`\n- rows using frozen discovery grand-mean fallback: `{residual_summary['rows_using_global_fallback']:,}`\n- residual minus raw same-author AUC: `{residual_summary['raw_to_residual_auc_delta']:+.4f}`\n\n{_markdown_table(residual_frame)}\n\nSubtracting a discovery-only population condition mean creates a different\nobject. It cannot be called a cleaner personality signal merely because it is\nresidualized.\n\n## C. Existing J1 reference (not rerun)\n\n- cached J1 decision: `{j1_reference.get('decision')}`\n- claim boundary: `{j1_reference.get('claim_boundary')}`\n- ordered dependence tested: `{j1_reference.get('ordered_dependence_tested')}`\n- cross-representation geometry correlation: `{j1_reference.get('cross_representation_confirmation_geometry_r')}`\n\n{_markdown_table(j1_table)}\n\nJ1 and fixed-rind reliability are not competing estimates: J1 intentionally\nretains author-selected subreddit choice, while A fixes one selected rind before\nexamining expression. J3's calibrated refusal remains a refusal of one finite\norder-specific operator, not a reversal of either result.\n\n## D. Assumption delta ledger\n\n{_markdown_table(assumptions, digits=3)}\n\n## Decision\n\n- Old V3/V4 conclusions remain historical claims with their own estimands;\n  this audit only changes their status if the same-direction compatibility test\n  reverses under the frozen event-disjoint implementation.\n- V6 factor nonconfirmation does not erase prior predefined construct findings: a\n  low-dimensional shared-axis test is not a test of scalar construct reliability.\n- No result here licenses a personality, clinical, causal, cross-language, or\n  cross-domain claim.\n"""
    args.report.write_text(report, encoding="utf-8")
    print(json.dumps({"fixed_rind": fixed_summary, "residual": residual_summary}, indent=2, default=float))


if __name__ == "__main__":
    main()
