#!/usr/bin/env python
"""E6: react signatures on DEEP data with the correct STRANGER null (OP-2).

v2 (OP-17): round-5 audit fixes applied — matched pair-shared class subsets
for same-user AND stranger correlations, equal gates, two-sided
fresh-pairing cluster bootstrap.

Round-3 lesson applied: individual-signature evidence requires comparing
same-person profile alignment against cross-person (stranger) alignment,
because ipsative profiles share normative class shapes. Deep extraction
(2,000 users, median 1,169 comments) allows thick cells.

Design: conditions = E3 content classes (transported map); temporal halves
(40/60 quantiles, gap >= 90 days); cells >= 6 slices per (user, class, half);
>= 5 shared classes per user across halves.

Pre-committed criteria:
  E6-pass: median(same-user signature r) - median(stranger r) >= 0.10 with
           cluster-bootstrap CI > 0, for >= 2 constructs -> signature channel
           revived with proper null.
  E6-fail: increment < 0.05 for all constructs -> react retired permanently
           on this corpus.
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

from suica_core.suica import PERSONALITY_LEAK_RE, fixed_token_slices_for_text  # noqa: E402
from scripts.suica_v2_lib import V2_CONSTRUCTS, score_slices_v2  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
CLASS_MAP = ROOT / "results" / "suica_e3_e4_choice_class_v2_s128" / "condition_class_map.csv"
OUT_DIR = ROOT / "results" / "suica_e6_react_stranger_null_v3"
REPORT = ROOT / "reports" / "suica_e6_react_stranger_null_v3.md"
SEED = 42
MIN_SLICES_CELL = 6
MIN_SHARED_CLASSES = 5
GAP_DAYS = 90


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cmap = pd.read_csv(CLASS_MAP)
    class_of = dict(zip(cmap["condition"].astype(str), cmap["class_id"].astype(int)))
    comments = pd.read_parquet(TIER_DIR / "tier_u_comments_deep.parquet")
    comments["author"] = comments["author"].astype(str)
    comments["subreddit"] = comments["subreddit"].fillna("__m__").astype(str)
    comments["class_id"] = comments["subreddit"].map(class_of)
    comments = comments.dropna(subset=["class_id"])
    comments["class_id"] = comments["class_id"].astype(int)

    rows = []
    for user, g in comments.groupby("author"):
        t = g["created_utc"].to_numpy(float)
        if len(t) < 60:
            continue
        t40, t60 = np.quantile(t, [0.4, 0.6])
        if (t60 - t40) / 86400 < GAP_DAYS:
            continue
        for half, part in [("early", g.loc[g["created_utc"] <= t40]), ("late", g.loc[g["created_utc"] >= t60])]:
            for cls, cell in part.groupby("class_id"):
                text = "\n".join(cell["body"].astype(str))
                slices = [r for r in fixed_token_slices_for_text(text, slice_tokens=128, stride=128,
                                                                 min_slice_tokens=24, max_slices=10)
                          if not PERSONALITY_LEAK_RE.search(r["slice_text"])]
                if len(slices) < MIN_SLICES_CELL:
                    continue
                for r in slices:
                    rows.append({"user_id": user, "class_id": int(cls), "half": half,
                                 "slice_index": r["slice_index"], "slice_text": r["slice_text"],
                                 "token_count": r["token_count"]})
    frame = pd.DataFrame(rows)
    print(f"E6 slices: {len(frame)} users={frame['user_id'].nunique()}")
    scored = score_slices_v2(frame)

    # Round-5 audit fixes (OP-17): MATCHED estimands — same-user and stranger
    # correlations computed on IDENTICAL pair-shared class subsets, equal
    # gates (>= MIN_SHARED_CLASSES for both), two-sided fresh-pairing
    # cluster bootstrap.
    def pair_metrics(profiles: dict, users: list, rng_local, n_target: int = 4000):
        same_vals, str_vals, owners = [], [], []
        attempts = 0
        while len(str_vals) < n_target and attempts < 20 * n_target:
            attempts += 1
            u, v = rng_local.choice(users, size=2, replace=False)
            if u == v:
                continue
            shared = profiles[u].index.intersection(profiles[v].index)
            if len(shared) < MIN_SHARED_CLASSES:
                continue
            eu = profiles[u].loc[shared, "e"]; lu = profiles[u].loc[shared, "l"]; lv = profiles[v].loc[shared, "l"]
            eu = eu - eu.mean(); lu = lu - lu.mean(); lv = lv - lv.mean()
            if min(eu.std(), lu.std(), lv.std()) < 1e-12:
                continue
            same_vals.append(float(np.corrcoef(eu, lu)[0, 1]))
            str_vals.append(float(np.corrcoef(eu, lv)[0, 1]))
            owners.append((u, v))
        return same_vals, str_vals, owners

    out_rows = []
    for construct in V2_CONSTRUCTS:
        cell = scored.groupby(["user_id", "class_id", "half"], as_index=False)[construct].mean()
        wide = cell.pivot_table(index=["user_id", "class_id"], columns="half", values=construct).dropna()
        profiles: dict[str, pd.DataFrame] = {}
        for user, g in wide.groupby(level=0):
            if len(g) < MIN_SHARED_CLASSES:
                continue
            e = g["early"] - g["early"].mean()
            l = g["late"] - g["late"].mean()
            if e.std() < 1e-12 or l.std() < 1e-12:
                continue
            profiles[user] = pd.DataFrame({"e": e.droplevel(0), "l": l.droplevel(0)})
        users = sorted(profiles)
        same_vals, str_vals, owners = pair_metrics(profiles, users, rng)
        med_same = float(np.median(same_vals))
        med_str = float(np.median(str_vals))
        boots = []
        ulist = np.array(users)
        for b in range(400):
            brng = np.random.default_rng(10_000 + b)
            take = list(brng.choice(ulist, size=len(ulist), replace=True))
            sv, tv, _ = pair_metrics(profiles, take, brng, n_target=1200)
            if len(tv) > 100:
                boots.append(np.median(sv) - np.median(tv))
        lo, hi = np.percentile(boots, [2.5, 97.5]) if boots else (np.nan, np.nan)
        out_rows.append({"construct": construct, "n_users": len(users), "n_pairs": len(str_vals),
                         "median_same_r": med_same, "median_stranger_r": med_str,
                         "increment": med_same - med_str, "inc_ci_lo": float(lo), "inc_ci_hi": float(hi)})
    out = pd.DataFrame(out_rows)
    revived = int(((out["increment"] >= 0.10) & (out["inc_ci_lo"] > 0)).sum())
    dead = bool((out["increment"] < 0.05).all())
    criteria = {"revived_constructs": revived, "E6_verdict": "signature_revived" if revived >= 2 else (
        "react_retired_permanently_this_corpus" if dead else "weak_partial")}
    out.to_csv(OUT_DIR / "e6_signature_stranger.csv", index=False)
    (OUT_DIR / "e6_results.json").write_text(json.dumps(criteria, indent=2) + "\n")
    REPORT.write_text("# SUICA E6 React Signatures with Stranger Null (deep)\n\n"
                      + out.round(4).to_markdown(index=False)
                      + "\n\n```json\n" + json.dumps(criteria, indent=2) + "\n```\n")
    print(out.round(3).to_string(index=False))
    print(json.dumps(criteria, indent=2))


if __name__ == "__main__":
    main()
