#!/usr/bin/env python
"""Phase-2 data prep: slice + score Tier-U comment streams (plan v2).

Pass A (P1): slices per (user, subreddit-condition, temporal half) with a
>= 90-day gap between halves. Pass B (P2/P4): slices per (user, condition)
over the full stream. Both passes drop personality-leak slices using the
updated PERSONALITY_LEAK_RE and score the frozen v2 constructs.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.suica import PERSONALITY_LEAK_RE, fixed_token_slices_for_text  # noqa: E402
from scripts.suica_v2_lib import score_slices_v2  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
GAP_DAYS = 90


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare SUICA v2 Phase-2 slices.")
    parser.add_argument("--slice-tokens", type=int, default=128)
    parser.add_argument("--max-slices-per-cell", type=int, default=10)
    parser.add_argument("--min-slice-tokens", type=int, default=24)
    parser.add_argument("--min-comments-per-condition", type=int, default=4)
    parser.add_argument("--max-conditions-per-user", type=int, default=8)
    parser.add_argument("--out-tag", default="s128")
    parser.add_argument("--input-parquet", default=str(TIER_DIR / "tier_u_comments.parquet"))
    parser.add_argument("--normalize-apostrophes", action="store_true",
                        help="scorer v3.1: map U+2019/U+2018 to ASCII apostrophe before slicing (OP-18)")
    return parser.parse_args()


def slices_for_cell(user_id: str, condition: str, half: str, texts: list[str], args: argparse.Namespace) -> list[dict]:
    text = "\n".join(texts)
    rows = []
    for row in fixed_token_slices_for_text(
        text,
        slice_tokens=args.slice_tokens,
        stride=args.slice_tokens,
        min_slice_tokens=args.min_slice_tokens,
        max_slices=args.max_slices_per_cell,
    ):
        if PERSONALITY_LEAK_RE.search(row["slice_text"]):
            continue
        rows.append(
            {
                "user_id": user_id,
                "condition": condition,
                "half": half,
                "slice_index": row["slice_index"],
                "token_count": row["token_count"],
                "slice_text": row["slice_text"],
            }
        )
    return rows


def main() -> None:
    args = parse_args()
    comments = pd.read_parquet(args.input_parquet)
    comments["author"] = comments["author"].astype(str)
    if args.normalize_apostrophes:
        comments["body"] = comments["body"].astype(str).str.replace("\u2019", "'", regex=False).str.replace("\u2018", "'", regex=False)
    comments["subreddit"] = comments["subreddit"].fillna("__missing__").astype(str)
    comments = comments.sort_values(["author", "created_utc"])

    rows_a: list[dict] = []
    rows_b: list[dict] = []
    gap_stats: list[dict] = []
    for user_id, group in comments.groupby("author", sort=False):
        counts = group["subreddit"].value_counts()
        conds = counts.loc[counts >= args.min_comments_per_condition].index.tolist()[: args.max_conditions_per_user]
        if len(conds) < 2:
            continue
        sub = group.loc[group["subreddit"].isin(conds)]
        # Pass B: full-stream cells
        for cond, cell in sub.groupby("subreddit"):
            rows_b.extend(slices_for_cell(user_id, cond, "all", cell["body"].tolist(), args))
        # Pass A: temporal halves with gap
        t = sub["created_utc"].to_numpy(float)
        if len(t) < 12:
            continue
        t40, t60 = np.quantile(t, [0.40, 0.60])
        gap_days = (t60 - t40) / 86400.0
        gap_stats.append({"user_id": user_id, "gap_days": gap_days})
        if gap_days < GAP_DAYS:
            continue
        early = sub.loc[sub["created_utc"] <= t40]
        late = sub.loc[sub["created_utc"] >= t60]
        for half, part in [("early", early), ("late", late)]:
            for cond, cell in part.groupby("subreddit"):
                if len(cell) < 2:
                    continue
                rows_a.extend(slices_for_cell(user_id, cond, half, cell["body"].tolist(), args))

    frame_a = pd.DataFrame(rows_a)
    frame_b = pd.DataFrame(rows_b)
    print(f"pass A slices: {len(frame_a)} users={frame_a['user_id'].nunique() if len(frame_a) else 0}")
    print(f"pass B slices: {len(frame_b)} users={frame_b['user_id'].nunique() if len(frame_b) else 0}")
    scored_a = score_slices_v2(frame_a) if len(frame_a) else frame_a
    scored_b = score_slices_v2(frame_b) if len(frame_b) else frame_b
    drop_cols = [c for c in ("slice_text",) if c in scored_a.columns]
    tag = args.out_tag
    scored_a.drop(columns=drop_cols).to_parquet(TIER_DIR / f"phase2_passA_scored_{tag}.parquet", index=False)
    scored_b.drop(columns=drop_cols).to_parquet(TIER_DIR / f"phase2_passB_scored_{tag}.parquet", index=False)
    # Keep raw pass-B slice text separately for the P2b occupancy model.
    frame_b.to_parquet(TIER_DIR / f"phase2_passB_slicetext_{tag}.parquet", index=False)
    manifest = {
        "slice_tokens": args.slice_tokens,
        "passA_slices": int(len(frame_a)),
        "passA_users": int(frame_a["user_id"].nunique()) if len(frame_a) else 0,
        "passB_slices": int(len(frame_b)),
        "passB_users": int(frame_b["user_id"].nunique()) if len(frame_b) else 0,
        "median_gap_days": float(pd.DataFrame(gap_stats)["gap_days"].median()) if gap_stats else None,
        "gap_rule_days": GAP_DAYS,
    }
    (TIER_DIR / f"phase2_manifest_{tag}.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
