#!/usr/bin/env python
"""Recheck historical PRED-1 using its token-slice rather than event unit.

The companion event-disjoint audit remains the V6 process-level result. This
script intentionally targets the historical conditional-expression estimand,
with an explicit token-disjoint but not comment-disjoint technical split.
"""
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

from scripts.suica_v2_lib import score_slices_v2  # noqa: E402
from suica_core.joint_process import cohort_from_bucket, same_author_auc, stable_bucket  # noqa: E402
from suica_core.lineage_compatibility import evenly_spread_token_views, paired_correlation_delta  # noqa: E402
from suica_core.suica import PERSONALITY_LEAK_RE  # noqa: E402


CONSTRUCTS = (
    "first_person_usage_v2",
    "directive_action_v2",
    "novelty_play_v2",
    "tension_core_v2",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Local gitignored PANDORA Tier-U parquet.")
    parser.add_argument("--config", type=Path, default=ROOT / "configs/v6_lineage_token_slice_compatibility.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/v6_lineage_token_slice_compatibility")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/V6_LINEAGE_TOKEN_SLICE_COMPATIBILITY.md")
    return parser.parse_args()


def _cohort(author: str, namespace: str) -> str:
    return cohort_from_bucket(stable_bucket(str(author), namespace=namespace))


def _span(values: pd.Series) -> float:
    numeric = pd.to_numeric(values, errors="coerce").dropna().to_numpy(float)
    return float(numeric.max() - numeric.min()) if len(numeric) > 1 else 0.0


def _load_comments(path: Path, cfg: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"missing local PANDORA source: {path}")
    comments = pd.read_parquet(path, columns=["author", "body", "created_utc", "subreddit"])
    source_rows = int(len(comments))
    comments["body"] = comments["body"].fillna("").astype(str)
    leak = comments["body"].map(lambda value: bool(PERSONALITY_LEAK_RE.search(value)))
    minimum = int(cfg["token_slice_estimator"]["minimum_body_characters"])
    work = comments.loc[~leak & comments["body"].str.len().ge(minimum)].copy()
    work["created_utc"] = pd.to_numeric(work["created_utc"], errors="coerce")
    work = work.dropna(subset=["created_utc"])
    work["author"] = work["author"].astype(str)
    work["subreddit"] = work["subreddit"].fillna("__missing__").astype(str)
    work["cohort"] = work["author"].map(lambda value: _cohort(value, str(cfg["cohort_namespace"])))
    return work, {
        "n_source_comments": source_rows,
        "n_excluded_personality_leakage": int(leak.sum()),
        "n_after_text_guard": int(len(work)),
        "external_labels_read": False,
        "raw_text_persisted": False,
    }


def _top_subreddits(work: pd.DataFrame) -> pd.DataFrame:
    counts = work.groupby(["author", "subreddit"], observed=True).size().rename("n").reset_index()
    top = (
        counts.sort_values(["author", "n", "subreddit"], ascending=[True, False, True], kind="stable")
        .drop_duplicates("author")
        .rename(columns={"subreddit": "top_subreddit", "n": "top_n"})
        .set_index("author")
    )
    totals = work.groupby("author", observed=True).size().rename("total")
    work = work.copy()
    work["_top_subreddit"] = work["author"].map(top["top_subreddit"])
    other_subreddits = (
        work.loc[~work["subreddit"].eq(work["_top_subreddit"])]
        .groupby("author", observed=True)["subreddit"].nunique()
        .rename("other_subreddits")
    )
    top = top.join(totals).join(other_subreddits).fillna({"other_subreddits": 0})
    top["other_n"] = top["total"] - top["top_n"]
    return top


def _build_slice_rows(work: pd.DataFrame, cfg: dict[str, Any]) -> tuple[list[dict[str, Any]], pd.DataFrame, dict[str, int]]:
    """Build no-persist token windows from fixed and mixed text streams."""
    spec = cfg["token_slice_estimator"]
    top = _top_subreddits(work)
    required_windows = 2 * int(spec["slices_per_view"])
    candidates = top.index[
        top["other_subreddits"].ge(int(spec["minimum_other_subreddits"]))
    ]
    rows: list[dict[str, Any]] = []
    meta_rows: list[dict[str, Any]] = []
    rejected = {"span": 0, "token_support": 0}
    for author in candidates:
        group = work.loc[work["author"].eq(author)].copy()
        top_subreddit = str(top.loc[author, "top_subreddit"])
        arms = {
            "fixed": group.loc[group["subreddit"].eq(top_subreddit)],
            "mixed": group.loc[~group["subreddit"].eq(top_subreddit)],
        }
        fixed_span, mixed_span = _span(arms["fixed"]["created_utc"]), _span(arms["mixed"]["created_utc"])
        if fixed_span <= 0.0 or mixed_span <= 0.0 or min(fixed_span, mixed_span) / max(fixed_span, mixed_span) < float(spec["minimum_arm_span_ratio"]):
            rejected["span"] += 1
            continue
        candidate_rows: list[dict[str, Any]] = []
        candidate_meta: list[dict[str, Any]] = []
        for arm, events in arms.items():
            text = "\n".join(events.sort_values("created_utc", kind="stable")["body"].astype(str))
            windows = evenly_spread_token_views(
                text,
                slice_tokens=int(spec["slice_tokens"]),
                slices_per_view=int(spec["slices_per_view"]),
            )
            if len(windows) != required_windows:
                candidate_rows = []
                break
            for window in windows:
                candidate_rows.append({
                    "author": str(author),
                    "arm": arm,
                    "technical_view": str(window["technical_view"]),
                    "slice_index": int(window["slice_index"]),
                    "slice_text": str(window["slice_text"]),
                })
            candidate_meta.append({
                "author": str(author),
                "arm": arm,
                "stream_span_days": _span(events["created_utc"]) / 86_400.0,
                "n_source_comments": int(len(events)),
                "n_source_subreddits": int(events["subreddit"].nunique()),
                "n_token_windows": int(len(windows)),
            })
        if not candidate_rows:
            rejected["token_support"] += 1
            continue
        rows.extend(candidate_rows)
        meta_rows.extend(candidate_meta)
    return rows, pd.DataFrame(meta_rows), {"candidate_authors": int(len(candidates)), **rejected}


def _matrix(aggregate: pd.DataFrame) -> pd.DataFrame:
    complete = aggregate.pivot_table(index="author", columns=["arm", "technical_view"], values=list(CONSTRUCTS))
    needed = [(construct, arm, view) for construct in CONSTRUCTS for arm in ("fixed", "mixed") for view in ("left", "right")]
    return complete.dropna(subset=needed)


def main() -> None:
    args = parse_args()
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    comments, provenance = _load_comments(args.input, cfg)
    cohort = str(cfg["token_slice_estimator"]["reporting_cohort"])
    rows, meta, rejection = _build_slice_rows(comments.loc[comments["cohort"].eq(cohort)].copy(), cfg)
    if not rows:
        raise RuntimeError("no token-slice confirmation authors met the frozen protocol")
    scored = score_slices_v2(pd.DataFrame(rows))
    aggregate = scored.groupby(["author", "arm", "technical_view"], observed=True)[list(CONSTRUCTS)].mean().reset_index()
    complete = _matrix(aggregate)
    spec = cfg["token_slice_estimator"]
    metric_rows: list[dict[str, Any]] = []
    for index, construct in enumerate(CONSTRUCTS):
        outcome = paired_correlation_delta(
            complete[(construct, "fixed", "left")],
            complete[(construct, "fixed", "right")],
            complete[(construct, "mixed", "left")],
            complete[(construct, "mixed", "right")],
            bootstrap_iterations=int(spec["bootstrap_iterations"]),
            seed=int(cfg["seed"]) + index,
        )
        metric_rows.append({"construct": construct, "n_authors": int(len(complete)), **outcome})
    metrics = pd.DataFrame(metric_rows)
    targets = set(map(str, spec["historically_supported_constructs"]))
    target_rows = metrics.loc[metrics["construct"].isin(targets)]
    positive = bool(len(target_rows) == len(targets) and target_rows["ci_lo"].gt(0.0).all())
    reverse = bool(target_rows["ci_hi"].lt(0.0).any())
    relation = "UPHELD_LEGACY_TOKEN_ESTIMAND" if positive else (
        "CONTRADICTED_UNDER_TOKEN_SLICE_IMPLEMENTATION" if reverse else "INCONCLUSIVE_NOT_A_REVERSAL"
    )
    fixed_left = complete.loc[:, [(construct, "fixed", "left") for construct in CONSTRUCTS]].to_numpy(float)
    fixed_right = complete.loc[:, [(construct, "fixed", "right") for construct in CONSTRUCTS]].to_numpy(float)
    mixed_left = complete.loc[:, [(construct, "mixed", "left") for construct in CONSTRUCTS]].to_numpy(float)
    mixed_right = complete.loc[:, [(construct, "mixed", "right") for construct in CONSTRUCTS]].to_numpy(float)
    span_ratio = meta.pivot(index="author", columns="arm", values="stream_span_days")
    result = {
        "run_name": cfg["run_name"],
        "provenance": provenance,
        "reporting_cohort": cohort,
        "candidate_authors_before_support": rejection["candidate_authors"],
        "n_complete_authors": int(len(complete)),
        "rejected": {key: value for key, value in rejection.items() if key != "candidate_authors"},
        "median_fixed_to_mixed_span_ratio": float(np.median(span_ratio["fixed"] / np.maximum(span_ratio["mixed"], 1e-12))),
        "fixed_same_author_auc": float(same_author_auc(fixed_left, fixed_right)),
        "mixed_same_author_auc": float(same_author_auc(mixed_left, mixed_right)),
        "historical_constructs_positive": int(target_rows["ci_lo"].gt(0.0).sum()),
        "historical_constructs_total": int(len(targets)),
        "relation": relation,
        "claim_boundary": "token-slice conditional-expression precision only; not event dynamics or personality",
        "external_labels_read": False,
        "raw_text_persisted": False,
    }
    metrics.to_csv(args.output_dir / "token_slice_fixed_rind_constructs.csv", index=False)
    (args.output_dir / "token_slice_result.json").write_text(json.dumps(result, indent=2, default=float) + "\n", encoding="utf-8")
    report = f"""# SUICA V6 Lineage Token-Slice Compatibility\n\n## Scope\n\nThis is a token-slice replication of the historical PRED-1 estimand, not an\nevent-disjoint or temporal-dynamics result. It uses no external labels and\npersists no raw text.\n\n- source comments after personality-report guard: `{provenance['n_after_text_guard']:,}`\n- confirmation candidates before span/token support: `{result['candidate_authors_before_support']:,}`\n- complete paired authors: `{result['n_complete_authors']:,}`\n- fixed/mixed median span ratio: `{result['median_fixed_to_mixed_span_ratio']:.3f}`\n- fixed/mixed vector same-author AUC: `{result['fixed_same_author_auc']:.4f}` / `{result['mixed_same_author_auc']:.4f}`\n\n## Frozen construct contrast\n\n**Relation:** `{relation}`.\n\n{metrics.round(4).to_markdown(index=False)}\n\n## Interpretation\n\nThe token-slice result is compared only with the historical PRED-1 claim. It\ncannot validate or invalidate V6's event-level joint-process geometry or the\nJ3 ordered-transition refusal. `tension_core_v2` is descriptive and is not\npart of the historical three-construct criterion.\n"""
    args.report.write_text(report, encoding="utf-8")
    print(json.dumps(result, indent=2, default=float))


if __name__ == "__main__":
    main()
