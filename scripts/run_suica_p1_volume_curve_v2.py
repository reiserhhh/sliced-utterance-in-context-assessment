#!/usr/bin/env python
"""P1 companion: disjoint-text retest reliability as a function of text volume.

If P1 fails at current volumes, this curve is the constructive deliverable:
how much text per half a future administration would need. Bins users by
min(slices_early, slices_late) within shared conditions and reports retest r
per bin per construct, plus a Spearman-Brown projection to target volumes.
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

from scripts.suica_v2_lib import V2_CONSTRUCTS, loo_condition_center, spearman_brown  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
TAG = "s128"
BINS = [(6, 11), (12, 19), (20, 29), (30, 60)]


def main() -> None:
    frame = pd.read_parquet(TIER_DIR / f"phase2_passA_scored_{TAG}.parquet")
    users_per_cond = frame.groupby("condition")["user_id"].nunique()
    frame = frame.loc[frame["condition"].map(users_per_cond).ge(3)]
    cell_counts = frame.groupby(["user_id", "condition", "half"]).size().unstack("half").fillna(0)
    shared = cell_counts.loc[(cell_counts.get("early", 0) >= 2) & (cell_counts.get("late", 0) >= 2)].reset_index()[["user_id", "condition"]]
    per_user = shared.groupby("user_id").size()
    shared = shared.loc[shared["user_id"].isin(per_user.loc[per_user >= 2].index)]
    work = frame.merge(shared.drop_duplicates(), on=["user_id", "condition"])
    volumes = work.groupby(["user_id", "half"]).size().unstack("half").fillna(0)
    volumes["min_half"] = volumes[["early", "late"]].min(axis=1)

    bases = {}
    for half in ("early", "late"):
        sub = work.loc[work["half"].eq(half)].copy()
        rows = {}
        for construct in V2_CONSTRUCTS:
            sub["_c"] = loo_condition_center(sub, construct, group_cols=("condition",))
            cell = sub.groupby(["user_id", "condition"])["_c"].mean()
            rows[construct] = cell.groupby("user_id").mean()
        bases[half] = pd.DataFrame(rows)
    joined = bases["early"].join(bases["late"], lsuffix="_e", rsuffix="_l").join(volumes["min_half"]).dropna()

    out_rows = []
    for lo, hi in BINS:
        sel = joined.loc[(joined["min_half"] >= lo) & (joined["min_half"] <= hi)]
        for construct in V2_CONSTRUCTS:
            if len(sel) < 60:
                continue
            r = float(sel[f"{construct}_e"].corr(sel[f"{construct}_l"]))
            mean_tokens = float(sel["min_half"].mean() * 128)
            out_rows.append({"bin": f"{lo}-{hi} slices/half", "n_users": int(len(sel)), "construct": construct,
                             "approx_tokens_per_half": int(mean_tokens), "retest_r": r,
                             "sb_full_length_r": spearman_brown(r)})
    out = pd.DataFrame(out_rows)
    out_dir = ROOT / "results" / f"suica_p1_volume_curve_v2_{TAG}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_dir / "volume_curve.csv", index=False)
    (ROOT / "reports" / f"suica_p1_volume_curve_v2_{TAG}.md").write_text(
        "# SUICA P1 Reliability vs Text Volume (v2)\n\n" + out.round(3).to_markdown(index=False) + "\n"
    )
    print(out.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
