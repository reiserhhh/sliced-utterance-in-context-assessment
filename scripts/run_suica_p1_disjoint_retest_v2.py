#!/usr/bin/env python
"""P1: disjoint-text, time-gapped base-score test-retest on Tier U (plan v2).

Early vs late temporal halves (>= 90-day gap), restricted to conditions shared
by both halves so condition composition cannot masquerade as instability.
LOO condition centering within each half. Success: Spearman-Brown-corrected
r >= 0.60 for >= 3 constructs and median SB-corrected r >= 0.50.
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

from scripts.suica_v2_lib import V2_CONSTRUCTS, loo_condition_center, spearman_brown  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default="s128")
    parser.add_argument("--min-shared-conditions", type=int, default=2)
    parser.add_argument("--min-slices-per-half", type=int, default=6)
    parser.add_argument("--min-users-per-condition", type=int, default=3)
    parser.add_argument("--n-boot", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def half_bases(frame: pd.DataFrame, construct: str, shared: pd.DataFrame) -> pd.DataFrame:
    """Per (user, half) base over the user's shared conditions, LOO-centered per half."""
    out = []
    for half, sub in frame.groupby("half"):
        sub = sub.copy()
        sub["_centered"] = loo_condition_center(sub, construct, group_cols=("condition",))
        cell = sub.groupby(["user_id", "condition"], as_index=False)["_centered"].mean()
        cell = cell.merge(shared, on=["user_id", "condition"], how="inner")
        base = cell.groupby("user_id")["_centered"].mean().rename(f"base_{half}")
        out.append(base)
    return pd.concat(out, axis=1)


def main() -> None:
    args = parse_args()
    rng = np.random.default_rng(args.seed)
    frame = pd.read_parquet(TIER_DIR / f"phase2_passA_scored_{args.tag}.parquet")
    users_per_cond = frame.groupby("condition")["user_id"].nunique()
    frame = frame.loc[frame["condition"].map(users_per_cond).ge(args.min_users_per_condition)]

    cell_counts = frame.groupby(["user_id", "condition", "half"]).size().unstack("half").fillna(0)
    shared = cell_counts.loc[(cell_counts.get("early", 0) >= 2) & (cell_counts.get("late", 0) >= 2)]
    shared = shared.reset_index()[["user_id", "condition"]]
    per_user = shared.groupby("user_id").size()
    slices_half = (
        frame.merge(shared, on=["user_id", "condition"]).groupby(["user_id", "half"]).size().unstack("half").fillna(0)
    )
    eligible = set(per_user.loc[per_user >= args.min_shared_conditions].index) & set(
        slices_half.loc[(slices_half.get("early", 0) >= args.min_slices_per_half) & (slices_half.get("late", 0) >= args.min_slices_per_half)].index
    )
    shared = shared.loc[shared["user_id"].isin(eligible)]
    work = frame.merge(shared[["user_id", "condition"]].drop_duplicates(), on=["user_id", "condition"])
    print(f"eligible users: {len(eligible)}; slices used: {len(work)}")

    rows = []
    for construct in V2_CONSTRUCTS:
        bases = half_bases(work, construct, shared).dropna()
        a = bases["base_early"].to_numpy(float)
        b = bases["base_late"].to_numpy(float)
        r = float(np.corrcoef(a, b)[0, 1])
        boots = []
        idx = np.arange(len(a))
        for _ in range(args.n_boot):
            take = rng.choice(idx, size=len(idx), replace=True)
            if np.std(a[take]) < 1e-12 or np.std(b[take]) < 1e-12:
                continue
            boots.append(np.corrcoef(a[take], b[take])[0, 1])
        lo, hi = np.percentile(boots, [2.5, 97.5])
        shuffle_rs = []
        for _ in range(200):
            perm = rng.permutation(len(b))
            shuffle_rs.append(np.corrcoef(a, b[perm])[0, 1])
        rows.append(
            {
                "construct": construct,
                "n_users": int(len(bases)),
                "retest_r": r,
                "retest_r_ci_lo": float(lo),
                "retest_r_ci_hi": float(hi),
                "sb_corrected_r": spearman_brown(r),
                "sb_ci_lo": spearman_brown(float(lo)),
                "sb_ci_hi": spearman_brown(float(hi)),
                "shuffle_control_median_r": float(np.median(shuffle_rs)),
            }
        )
    result = pd.DataFrame(rows)
    out_dir = ROOT / "results" / f"suica_p1_disjoint_retest_v2_{args.tag}"
    out_dir.mkdir(parents=True, exist_ok=True)
    result.to_csv(out_dir / "p1_retest.csv", index=False)
    passing = int((result["sb_corrected_r"] >= 0.60).sum())
    criteria = {
        "sb_ge_060_count": passing,
        "median_sb": float(result["sb_corrected_r"].median()),
        "P1_verdict": "pass" if passing >= 3 and result["sb_corrected_r"].median() >= 0.50 else "fail",
    }
    (out_dir / "p1_results.json").write_text(json.dumps({"criteria": criteria, "rows": rows}, indent=2) + "\n")
    report = ROOT / "reports" / f"suica_p1_disjoint_retest_v2_{args.tag}.md"
    report.write_text(
        "# SUICA P1 Disjoint-Text Test-Retest (v2)\n\n"
        f"Eligible users: {len(eligible)} (gap >= 90 days, shared conditions only)\n\n"
        + result.round(4).to_markdown(index=False)
        + "\n\n```json\n" + json.dumps(criteria, indent=2) + "\n```\n"
    )
    print(result.round(3).to_string(index=False))
    print(json.dumps(criteria, indent=2))


if __name__ == "__main__":
    main()
