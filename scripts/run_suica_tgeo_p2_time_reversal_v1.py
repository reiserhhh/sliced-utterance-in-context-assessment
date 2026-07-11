#!/usr/bin/env python
"""T-GEO-P2 — time-reversal (drift) null on PANDORA. Label-free, Tier-U.

Ports the v5 T-geometry Layer-I instrument I-1 (trading-agent-claude,
SUICA_V5_TGEOMETRY_REFORMULATION_20260711.md): author-level trait
stationarity asserts invariance under per-author occasion-sequence
reversal (an involution). Reversal maps each author's time slope to its
negative, so under H0 the per-author sign-flip group (Z/2)^N gives the
exact null for the mean slope.

Design (data-independent):
  - Per Tier-U user: eligible conditions replicated verbatim from the
    frozen prep (subreddits with >= 4 comments, top-8; >= 12 comments).
  - K = 4 consecutive equal-count blocks of the user's eligible comments.
  - Per block, per condition: concatenate in time order, slice with the
    frozen slicer (128/24/max 10), drop leak-mask hits, score the four
    v2 constructs; block value = mean over the block's slices; block time
    = mean created_utc.
  - Cohort: all 4 blocks have >= 2 slices AND (t_block4 - t_block1) >= 180
    days.
  - Per user: OLS slope of block value on block time (per year).
  - Statistic: mean slope across users (per construct);
    null: 2000 per-user sign flips; two-sided p.
  - Arms: (a) pooled across the user's conditions (drift = style drift +
    venue-mix drift, confounded — stated); (b) restricted to the user's
    single largest condition (venue mix held constant; the cleaner
    stationarity reading).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_persona.suica import PERSONALITY_LEAK_RE, fixed_token_slices_for_text  # noqa: E402
from scripts.suica_v2_lib import score_slices_v2  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
OUT_DIR = ROOT / "results" / "suica_tgeo_p2_time_reversal"
K = 4
MIN_SPAN_DAYS = 180
N_FLIP = 2000
CONSTRUCTS = ["tension_core_v2", "directive_action_v2",
              "first_person_usage_v2", "novelty_play_v2"]


def block_rows(arm: str) -> pd.DataFrame:
    comments = pd.read_parquet(TIER_DIR / "tier_u_comments.parquet")
    comments["author"] = comments["author"].astype(str)
    comments["subreddit"] = comments["subreddit"].fillna("__missing__").astype(str)
    comments = comments.sort_values(["author", "created_utc"])
    rows = []
    for user, group in comments.groupby("author", sort=False):
        counts = group["subreddit"].value_counts()
        conds = counts.loc[counts >= 4].index.tolist()[:8]
        if len(conds) < 2:
            continue
        sub = group.loc[group["subreddit"].isin(conds)]
        if len(sub) < 12:
            continue
        if arm == "top1":
            sub = sub.loc[sub["subreddit"] == counts.index[0]]
            if len(sub) < 12:
                continue
        cuts = np.array_split(np.arange(len(sub)), K)
        for bi, ix in enumerate(cuts):
            part = sub.iloc[ix]
            tmid = float(part["created_utc"].astype(float).mean())
            for cond, cell in part.groupby("subreddit"):
                if len(cell) < 2:
                    continue
                text = "\n".join(cell["body"].astype(str))
                for row in fixed_token_slices_for_text(
                        text, slice_tokens=128, stride=128,
                        min_slice_tokens=24, max_slices=10):
                    if PERSONALITY_LEAK_RE.search(row["slice_text"]):
                        continue
                    rows.append({"user_id": user, "block": bi, "tmid": tmid,
                                 "slice_text": row["slice_text"]})
    return pd.DataFrame(rows)


def analyze(arm: str) -> list[dict]:
    frame = block_rows(arm)
    print(f"[{arm}] block slices: {len(frame)}")
    scored = score_slices_v2(frame[["user_id", "slice_text"]].assign(
        condition="_", half="_")[["user_id", "condition", "half", "slice_text"]])
    scored = pd.concat([frame[["user_id", "block", "tmid"]].reset_index(drop=True),
                        scored[CONSTRUCTS].reset_index(drop=True)], axis=1)

    counts = scored.groupby(["user_id", "block"]).size().unstack(fill_value=0)
    ok_users = counts.index[(counts >= 2).all(axis=1) & (counts.shape[1] == K)]
    bm = scored.groupby(["user_id", "block"]).agg(
        {**{c: "mean" for c in CONSTRUCTS}, "tmid": "mean"})
    bm = bm.loc[bm.index.get_level_values(0).isin(ok_users)]

    out = []
    rng = np.random.default_rng(20260711)
    for c in CONSTRUCTS:
        slopes = []
        for user, g in bm.groupby(level=0):
            t = g["tmid"].to_numpy(float)
            span = (t.max() - t.min()) / 86400.0
            if span < MIN_SPAN_DAYS:
                continue
            y = g[c].to_numpy(float)
            ty = (t - t.mean()) / (365.25 * 86400.0)   # years, centered
            denom = float((ty ** 2).sum())
            if denom <= 0:
                continue
            slopes.append(float((ty * (y - y.mean())).sum() / denom))
        s = np.array(slopes)
        obs = float(s.mean())
        flips = rng.choice([-1.0, 1.0], size=(N_FLIP, len(s)))
        null_means = (flips * s).mean(axis=1)
        p = float((np.abs(null_means) >= abs(obs)).mean())
        out.append({"arm": arm, "construct": c, "n_users": int(len(s)),
                    "mean_slope_per_year": round(obs, 5),
                    "median_slope": round(float(np.median(s)), 5),
                    "frac_positive": round(float((s > 0).mean()), 3),
                    "signflip_p_two_sided": round(p, 4),
                    "null_sd": round(float(null_means.std()), 5)})
        print(f"  [{arm}] {c}: mean_slope/yr={obs:+.4f} (n={len(s)}) p={p:.4f}")
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    res = analyze("pooled") + analyze("top1")
    (OUT_DIR / "TGEO_P2_TIME_REVERSAL.json").write_text(json.dumps(res, indent=2))
    md = ["# T-GEO-P2 — time-reversal (drift) null on PANDORA (label-free)", "",
          "Per-user OLS slope of block-mean construct value on block time (K=4",
          "equal-count blocks, span >= 180 days); sign-flip null (2000 draws).",
          "Arm 'pooled' confounds style drift with venue-mix drift; arm 'top1'",
          "holds the venue constant.", "",
          "| arm | construct | n | mean slope /yr | frac>0 | p (sign-flip) |",
          "|---|---|---|---|---|---|"]
    for r in res:
        md.append(f"| {r['arm']} | {r['construct']} | {r['n_users']} "
                  f"| {r['mean_slope_per_year']:+.4f} | {r['frac_positive']:.2f} "
                  f"| {r['signflip_p_two_sided']:.4f} |")
    (OUT_DIR / "TGEO_P2_TIME_REVERSAL.md").write_text("\n".join(md) + "\n")
    print("written:", OUT_DIR / "TGEO_P2_TIME_REVERSAL.md")


if __name__ == "__main__":
    main()
