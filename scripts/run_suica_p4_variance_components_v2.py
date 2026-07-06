#!/usr/bin/env python
"""P4: base/react separability (plan v2).

Part 1: crossed person x condition variance decomposition (MoM, P0-validated)
on a dense grid of globally common subreddits, with cluster-bootstrap CIs and
a MixedLM corroboration subsample.
Part 2: react-signature stability — per-user if-then profile (condition react
vector) correlated early vs late over shared conditions (CAPS-style test),
with a within-user condition-shuffle null.
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

from scripts.suica_v2_lib import (  # noqa: E402
    V2_CONSTRUCTS,
    cell_table,
    loo_condition_center,
    mom_from_cells,
    mom_variance_components,
)

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default="s128")
    parser.add_argument("--top-subreddits", type=int, default=10)
    parser.add_argument("--min-conditions-in-grid", type=int, default=4)
    parser.add_argument("--min-slices-per-cell", type=int, default=2)
    parser.add_argument("--n-boot", type=int, default=200)
    parser.add_argument("--min-shared-conditions-react", type=int, default=4)
    parser.add_argument("--mixedlm-users", type=int, default=350)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def build_grid(frame: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    cell = frame.groupby(["user_id", "condition"]).size().rename("n").reset_index()
    cell = cell.loc[cell["n"] >= args.min_slices_per_cell]
    cond_cover = cell.groupby("condition")["user_id"].nunique().sort_values(ascending=False)
    top = set(cond_cover.head(args.top_subreddits).index)
    cell = cell.loc[cell["condition"].isin(top)]
    per_user = cell.groupby("user_id").size()
    users = set(per_user.loc[per_user >= args.min_conditions_in_grid].index)
    grid = frame.loc[frame["condition"].isin(top) & frame["user_id"].isin(users)]
    return grid


def react_signatures(passa: pd.DataFrame, construct: str, min_shared: int, rng: np.random.Generator) -> dict:
    sigs: list[float] = []
    null_sigs: list[float] = []
    half_cells = []
    for half in ("early", "late"):
        sub = passa.loc[passa["half"].eq(half)].copy()
        sub["_c"] = loo_condition_center(sub, construct, group_cols=("condition",))
        half_cells.append(sub.groupby(["user_id", "condition"])["_c"].mean().rename(f"m_{half}"))
    cells = pd.concat(half_cells, axis=1, join="inner").dropna().reset_index()
    for user_id, group in cells.groupby("user_id"):
        if len(group) < min_shared:
            continue
        e = group["m_early"].to_numpy(float)
        l = group["m_late"].to_numpy(float)
        e = e - e.mean()
        l = l - l.mean()
        if np.std(e) < 1e-12 or np.std(l) < 1e-12:
            continue
        sigs.append(float(np.corrcoef(e, l)[0, 1]))
        perm = rng.permutation(len(l))
        null_sigs.append(float(np.corrcoef(e, l[perm])[0, 1]))
    return {
        "n_users": len(sigs),
        "median_signature_r": float(np.median(sigs)) if sigs else float("nan"),
        "mean_signature_r": float(np.mean(sigs)) if sigs else float("nan"),
        "null_median_signature_r": float(np.median(null_sigs)) if null_sigs else float("nan"),
    }


def main() -> None:
    args = parse_args()
    rng = np.random.default_rng(args.seed)
    passb = pd.read_parquet(TIER_DIR / f"phase2_passB_scored_{args.tag}.parquet")
    passa = pd.read_parquet(TIER_DIR / f"phase2_passA_scored_{args.tag}.parquet")
    grid = build_grid(passb, args)
    fill = grid.groupby(["user_id", "condition"]).size().reset_index()
    density = len(fill) / (fill["user_id"].nunique() * fill["condition"].nunique())
    print(f"grid: users={fill['user_id'].nunique()} conditions={fill['condition'].nunique()} fill={density:.2f} slices={len(grid)}")

    mom_rows = []
    users = np.array(sorted(grid["user_id"].unique()))
    for construct in V2_CONSTRUCTS:
        cells = cell_table(grid, construct)
        cells_by_user = {u: g for u, g in cells.groupby("user_id")}
        est = mom_from_cells(cells)
        boots = {"person_share": [], "interaction_share": []}
        cell_users = np.array(sorted(cells_by_user))
        for _ in range(args.n_boot):
            take = rng.choice(cell_users, size=len(cell_users), replace=True)
            parts = []
            for dup, u in enumerate(take):
                part = cells_by_user[u].copy()
                part["user_id"] = f"{u}#{dup}"
                parts.append(part)
            bs = mom_from_cells(pd.concat(parts, ignore_index=True))
            boots["person_share"].append(bs["person_share"])
            boots["interaction_share"].append(bs["interaction_share"])
        row = {"construct": construct, **{k: est[k] for k in ("person_share", "condition_share", "interaction_share", "residual_share")}}
        for key in ("person_share", "interaction_share"):
            lo, hi = np.nanpercentile(boots[key], [2.5, 97.5])
            row[f"{key}_ci_lo"], row[f"{key}_ci_hi"] = float(lo), float(hi)
        mom_rows.append(row)
        print(f"  {construct}: person={est['person_share']:.3f} interaction={est['interaction_share']:.3f}")
    mom = pd.DataFrame(mom_rows)

    mixedlm_out = {}
    try:
        import statsmodels.formula.api as smf
        sub_users = users[: args.mixedlm_users]
        for construct in ("first_person_usage_v2", "tension_core_v2"):
            data = grid.loc[grid["user_id"].isin(sub_users), ["user_id", "condition", construct]].dropna().copy()
            data["cell"] = data["user_id"] + ":" + data["condition"]
            data["g"] = 1
            md = smf.mixedlm(f"{construct} ~ 1", data, groups="g",
                             vc_formula={"u": "0 + C(user_id)", "c": "0 + C(condition)", "uc": "0 + C(cell)"})
            fit = md.fit(reml=True, method="lbfgs", maxiter=200)
            names = list(getattr(md, "exog_vc").names) if hasattr(md, "exog_vc") else ["u", "c", "uc"]
            vcs = dict(zip(names, [float(v) for v in np.atleast_1d(fit.vcomp)]))
            resid = float(fit.scale)
            total = sum(vcs.values()) + resid
            mixedlm_out[construct] = {
                "person_share": vcs.get("u", np.nan) / total,
                "condition_share": vcs.get("c", np.nan) / total,
                "interaction_share": vcs.get("uc", np.nan) / total,
                "residual_share": resid / total,
                "n_rows": int(len(data)),
            }
    except Exception as exc:  # pragma: no cover
        mixedlm_out = {"error": str(exc)}

    react_rows = {}
    for construct in V2_CONSTRUCTS:
        react_rows[construct] = react_signatures(passa, construct, args.min_shared_conditions_react, rng)

    out_dir = ROOT / "results" / f"suica_p4_variance_components_v2_{args.tag}"
    out_dir.mkdir(parents=True, exist_ok=True)
    mom.to_csv(out_dir / "p4_mom_shares.csv", index=False)
    react = pd.DataFrame(react_rows).T.reset_index().rename(columns={"index": "construct"})
    react.to_csv(out_dir / "p4_react_signatures.csv", index=False)
    interaction_pos = int((mom["interaction_share_ci_lo"] > 0.005).sum())
    react_pass = int((react["median_signature_r"] >= 0.30).sum())
    criteria = {
        "interaction_ci_positive_count": interaction_pos,
        "react_median_ge_030_count": react_pass,
        "P4_verdict": "pass" if interaction_pos >= 2 and react_pass >= 2 else (
            "partial" if interaction_pos >= 2 or react_pass >= 1 else "fail"),
        "grid_fill": density,
        "mixedlm": mixedlm_out,
    }
    (out_dir / "p4_results.json").write_text(json.dumps(criteria, indent=2, default=float) + "\n")
    report = ROOT / "reports" / f"suica_p4_variance_components_v2_{args.tag}.md"
    report.write_text(
        "# SUICA P4 Variance Components & React Signatures (v2)\n\n## MoM shares (grid)\n\n"
        + mom.round(4).to_markdown(index=False)
        + "\n\n## React signatures (early vs late, shared conditions)\n\n"
        + react.round(4).to_markdown(index=False)
        + "\n\n```json\n" + json.dumps(criteria, indent=2, default=float) + "\n```\n"
    )
    print(react.round(3).to_string(index=False))
    print(json.dumps({k: v for k, v in criteria.items() if k != "mixedlm"}, indent=2, default=float))
    print("mixedlm:", json.dumps(mixedlm_out, indent=2, default=float))


if __name__ == "__main__":
    main()
