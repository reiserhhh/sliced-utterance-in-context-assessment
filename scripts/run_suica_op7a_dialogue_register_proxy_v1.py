#!/usr/bin/env python
"""OP-7a: dialogue-register transfer PROXY on natural Reddit turns.

OP-7 proper (clinical AI-dialogue pilot, N~30-60, echo-rate measurement)
requires data collection and stays OPEN. This proxy answers the within-reach
precursor question on existing Tier-U data: do the frozen style constructs
transport across the conversational-register boundary that Reddit already
contains — TOP-LEVEL comments on a post (broadcast register, parent_id=t3_*)
vs REPLIES to another user's comment (dialogic turn, parent_id=t1_*)?

Design (pre-committed BEFORE execution; Tier-U only, no lockbox contact):
  - Data: the deep 2,000-user sample (cap 1,200/user, same seed/filters as
    extract_suica_tier_u_deep_v3), re-extracted WITH parent_id.
  - Cells: (user, register, temporal half) with contiguous halves per
    register stream (OP-15: parity splits forbidden). Slicing/scoring via the
    frozen rules: per (user, register, half, subreddit) cell, >= 2 comments,
    128-token slices, min 24 tokens, max 10 slices/cell, leak-mask,
    score_slices_v2 + OP-5 kept clusters (19 constructs total).
  - Eligibility: >= 6 slices in each of the four register x half cells.
  - 2x2 correlations, all TIME-SEPARATED and volume-comparable:
      within_top   = r(top_early,   top_late)
      within_reply = r(reply_early, reply_late)
      cross_1      = r(top_early,   reply_late)
      cross_2      = r(reply_early, top_late)
      cross        = mean(cross_1, cross_2)
    Same-occasion cross r(top_early, reply_early) is reported ONLY as the
    adjacency-inflation diagnostic.
  - Level shift: paired Cohen's dz of (reply - top) full-register scores.

Pre-committed criteria:
  C1 (level): |dz| >= 0.5 flagged "material register shift" (descriptive).
  C2 (transport), only for constructs with min(within) >= 0.15:
      register-robust  if cross >= 0.70 * min(within_top, within_reply)
      register-bound   if cross <  0.50 * min(within)
      else indeterminate.
  Battery verdict = fraction register-robust among assessable constructs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.suica import PERSONALITY_LEAK_RE, fixed_token_slices_for_text  # noqa: E402
from scripts.suica_v2_lib import score_slices_v2  # noqa: E402
from scripts.run_suica_op9_embedding_baseline_v3 import rederive_op5_scores, OP5_KEPT, V3_BATTERY  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
DUMP = ROOT / "data_sets" / "PANDORA_official" / "all_comments_since_2015.csv"
DEEP_MANIFEST = TIER_DIR / "tier_u_comments_deep_manifest.json"
DEEP_PARQUET = TIER_DIR / "tier_u_comments_deep.parquet"
OP7A_PARQUET = TIER_DIR / "tier_u_comments_deep_op7a.parquet"
OUT_DIR = ROOT / "results" / "suica_op7a_dialogue_register_proxy_v1"
REPORT = ROOT / "reports" / "suica_op7a_dialogue_register_proxy_v1.md"
USECOLS = ["author", "body", "created_utc", "subreddit", "lang", "parent_id"]
CHUNK = 400_000
CAP_PER_USER = 1200
SEED = 42
MIN_SLICES_PER_CELL = 6
CONSTRUCTS = V3_BATTERY + OP5_KEPT


def extract_with_parent() -> pd.DataFrame:
    if OP7A_PARQUET.exists():
        return pd.read_parquet(OP7A_PARQUET)
    users = set(pd.read_parquet(DEEP_PARQUET, columns=["author"])["author"].astype(str).unique())
    print(f"re-extracting {len(users)} deep users with parent_id")
    counts: dict[str, int] = {}
    for chunk in pd.read_csv(DUMP, usecols=["author"], chunksize=CHUNK):
        vc = chunk.loc[chunk["author"].astype(str).isin(users), "author"].astype(str).value_counts()
        for u, n in vc.items():
            counts[u] = counts.get(u, 0) + int(n)
    keep_p = {u: min(1.0, CAP_PER_USER / max(1, n)) for u, n in counts.items()}
    rng = np.random.default_rng(SEED)
    parts = []
    for chunk in pd.read_csv(DUMP, usecols=USECOLS, chunksize=CHUNK):
        chunk["author"] = chunk["author"].astype(str)
        sub = chunk.loc[chunk["author"].isin(users)].copy()
        if sub.empty:
            continue
        sub = sub.loc[sub["lang"].fillna("en").astype(str).eq("en")]
        body = sub["body"].fillna("").astype(str)
        sub = sub.loc[body.str.len().gt(0) & ~body.isin(["[deleted]", "[removed]"])]
        if sub.empty:
            continue
        p = sub["author"].map(keep_p).fillna(0.0).to_numpy(float)
        sub = sub.loc[rng.random(len(sub)) < p]
        if sub.empty:
            continue
        sub["body"] = sub["body"].astype(str).str.slice(0, 1500)
        parts.append(sub.drop(columns=["lang"]))
    out = pd.concat(parts, ignore_index=True)
    out["created_utc"] = pd.to_numeric(out["created_utc"], errors="coerce")
    out = out.dropna(subset=["created_utc"]).sort_values(["author", "created_utc"]).reset_index(drop=True)
    out.to_parquet(OP7A_PARQUET, index=False)
    return out


def slice_cells(comments: pd.DataFrame) -> pd.DataFrame:
    comments = comments.copy()
    pid = comments["parent_id"].fillna("").astype(str)
    comments["register"] = np.where(pid.str.startswith("t3_"), "top",
                                    np.where(pid.str.startswith("t1_"), "reply", "other"))
    comments = comments.loc[comments["register"].isin(["top", "reply"])]
    rows = []
    for (user, register), g in comments.groupby(["author", "register"], sort=False):
        g = g.sort_values("created_utc")
        cut = len(g) // 2
        for half, part in [("early", g.iloc[:cut]), ("late", g.iloc[cut:])]:
            for sr, cell in part.groupby("subreddit"):
                if len(cell) < 2:
                    continue
                text = "\n".join(cell["body"].astype(str))
                for row in fixed_token_slices_for_text(
                        text, slice_tokens=128, stride=128, min_slice_tokens=24, max_slices=10):
                    if PERSONALITY_LEAK_RE.search(row["slice_text"]):
                        continue
                    rows.append({"user_id": str(user), "register": register, "half": half,
                                 "condition": str(sr), "slice_text": row["slice_text"],
                                 "token_count": row["token_count"]})
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    comments = extract_with_parent()
    reg_counts = (comments["parent_id"].fillna("").astype(str).str[:3].value_counts())
    print("parent_id prefixes:", reg_counts.head(5).to_dict())

    frame = slice_cells(comments)
    print(f"slices: {len(frame)}, users: {frame['user_id'].nunique()}")
    scored = score_slices_v2(frame[["user_id", "register", "half", "condition", "slice_text"]])
    op5 = rederive_op5_scores(frame.rename(columns={"register": "half_tmp"})
                              .assign(half=lambda d: d["half_tmp"] + "_" + d["half"])
                              [["user_id", "half", "slice_text"]])
    op5[["register", "thalf"]] = op5["half"].str.split("_", expand=True) if "half" in op5.columns else None

    cell_v3 = scored.groupby(["user_id", "register", "half"])[V3_BATTERY].mean()
    op5g = op5.rename(columns={"thalf": "temporal_half"})
    cell_op5 = op5g.groupby(["user_id", "register", "temporal_half"])[OP5_KEPT].mean()
    cell_op5.index.names = ["user_id", "register", "half"]
    cell = cell_v3.join(cell_op5, how="left")

    n_slices = frame.groupby(["user_id", "register", "half"]).size().rename("n")
    ok = (n_slices >= MIN_SLICES_PER_CELL).groupby("user_id").sum() == 4
    eligible = ok.index[ok]
    cell = cell.loc[cell.index.get_level_values(0).isin(eligible)]
    n_users = int(len(eligible))
    print(f"eligible users (>= {MIN_SLICES_PER_CELL} slices in all 4 cells): {n_users}")

    def block(register: str, half: str) -> pd.DataFrame:
        return cell.xs((register, half), level=("register", "half"))

    te, tl = block("top", "early"), block("top", "late")
    re_, rl = block("reply", "early"), block("reply", "late")
    common = te.index.intersection(tl.index).intersection(re_.index).intersection(rl.index)
    te, tl, re_, rl = te.loc[common], tl.loc[common], re_.loc[common], rl.loc[common]

    rows = []
    for c in CONSTRUCTS:
        if te[c].isna().all() or re_[c].isna().all():
            continue
        w_top = float(te[c].corr(tl[c]))
        w_rep = float(re_[c].corr(rl[c]))
        cross = float(np.mean([te[c].corr(rl[c]), re_[c].corr(tl[c])]))
        same_occ = float(te[c].corr(re_[c]))
        full_top = pd.concat([te[c], tl[c]], axis=1).mean(axis=1)
        full_rep = pd.concat([re_[c], rl[c]], axis=1).mean(axis=1)
        d = (full_rep - full_top).dropna()
        dz = float(d.mean() / d.std()) if d.std() > 0 else np.nan
        min_w = min(w_top, w_rep)
        if min_w < 0.15:
            verdict = "unassessable(min_within<0.15)"
        elif cross >= 0.70 * min_w:
            verdict = "register-robust"
        elif cross < 0.50 * min_w:
            verdict = "register-bound"
        else:
            verdict = "indeterminate"
        rows.append({"construct": c, "within_top": w_top, "within_reply": w_rep,
                     "cross_time_separated": cross, "same_occasion_cross_diagnostic": same_occ,
                     "level_shift_dz_reply_minus_top": dz, "verdict": verdict})
    out = pd.DataFrame(rows)
    assessable = out.loc[~out["verdict"].str.startswith("unassessable")]
    summary = {
        "n_users_eligible": n_users,
        "n_constructs": len(out),
        "n_assessable": int(len(assessable)),
        "n_register_robust": int((assessable["verdict"] == "register-robust").sum()),
        "n_register_bound": int((assessable["verdict"] == "register-bound").sum()),
        "n_indeterminate": int((assessable["verdict"] == "indeterminate").sum()),
        "material_level_shifts_dz_ge_0.5": out.loc[out["level_shift_dz_reply_minus_top"].abs() >= 0.5,
                                                   "construct"].tolist(),
        "mean_adjacency_inflation": float((out["same_occasion_cross_diagnostic"]
                                           - out["cross_time_separated"]).mean()),
    }
    out.round(4).to_csv(OUT_DIR / "op7a_register_transport.csv", index=False)
    (OUT_DIR / "op7a_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    REPORT.write_text("# OP-7a dialogue-register proxy (top-level vs reply turns)\n\n"
                      + out.round(3).to_markdown(index=False)
                      + "\n\n```json\n" + json.dumps(summary, indent=2) + "\n```\n"
                      + "\nScope note: this is the Reddit-internal register boundary, a PRECURSOR to\n"
                      + "OP-7 (AI-dialogue pilot), which remains open pending data collection.\n")
    print(out.round(3).to_string(index=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
