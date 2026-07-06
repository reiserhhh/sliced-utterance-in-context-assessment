#!/usr/bin/env python
"""E5: trait-state-era-slice spectrum per construct (OP-1, OP-11).

Design: rind held fixed by selection (each user's top subreddit only);
occasions = calendar quarters; slices as replicates. Crossed decomposition
(P0-validated MoM; condition := quarter):
  person share          -> TRAIT
  quarter main effect   -> ERA (population drift)
  person x quarter      -> STATE (within-person occasion deviation)
  residual              -> slice noise
Plus per-occasion STATE measurement precision: within-quarter even/odd
split-half of quarter scores after removing each user's mean (trait).

Pre-committed predictions:
  P-E5a: first_person trait share > state share.
  P-E5b: tension state:trait ratio > first_person state:trait ratio.
  P-E5c: if tension state split-half >= 0.30, per-occasion state monitoring is
         feasible at this text volume; otherwise report it as the required
         design gap (more per-occasion text).
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
from scripts.suica_v2_lib import V2_CONSTRUCTS, cell_table, mom_from_cells, score_slices_v2, spearman_brown  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
OCC = sys.argv[sys.argv.index("--occasion") + 1] if "--occasion" in sys.argv else "quarter"
OUT_DIR = ROOT / "results" / f"suica_e5_trait_state_spectrum_v3_{OCC}"
REPORT = ROOT / "reports" / f"suica_e5_trait_state_spectrum_v3_{OCC}.md"
SEED = 42
MIN_QUARTERS = 4
MAX_SLICES_PER_CELL = 8


def quarter_of(ts: float) -> str:
    t = pd.Timestamp(ts, unit="s", tz="UTC")
    if OCC == "month":
        return f"{t.year}M{t.month:02d}"
    return f"{t.year}Q{(t.month - 1) // 3 + 1}"


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    comments = pd.read_parquet(TIER_DIR / "tier_u_comments.parquet")
    comments["author"] = comments["author"].astype(str)
    comments["subreddit"] = comments["subreddit"].fillna("__m__").astype(str)
    rows = []
    for user, g in comments.groupby("author"):
        top = g["subreddit"].value_counts().index[0]
        sub = g.loc[g["subreddit"].eq(top)].sort_values("created_utc")
        if len(sub) < 12:
            continue
        sub = sub.assign(quarter=sub["created_utc"].map(quarter_of))
        q_counts = sub.groupby("quarter").size()
        quarters = q_counts.loc[q_counts >= 2].index.tolist()
        if len(quarters) < MIN_QUARTERS:
            continue
        for q in quarters:
            cell = sub.loc[sub["quarter"].eq(q)]
            text = "\n".join(cell["body"].astype(str))
            for row in fixed_token_slices_for_text(text, slice_tokens=128, stride=128,
                                                   min_slice_tokens=24, max_slices=MAX_SLICES_PER_CELL):
                if PERSONALITY_LEAK_RE.search(row["slice_text"]):
                    continue
                rows.append({"user_id": user, "condition": q, "slice_index": row["slice_index"],
                             "token_count": row["token_count"], "slice_text": row["slice_text"]})
    frame = pd.DataFrame(rows)
    print(f"E5 slices: {len(frame)} users={frame['user_id'].nunique()} quarters={frame['condition'].nunique()}")
    scored = score_slices_v2(frame)

    spectrum_rows = []
    state_rows = []
    users_all = np.array(sorted(scored["user_id"].unique()))
    for construct in V2_CONSTRUCTS:
        cells = cell_table(scored, construct)
        by_user = {u: g for u, g in cells.groupby("user_id")}
        est = mom_from_cells(cells)
        boots = {"person_share": [], "interaction_share": []}
        cu = np.array(sorted(by_user))
        for _ in range(200):
            take = rng.choice(cu, size=len(cu), replace=True)
            parts = []
            for dup, u in enumerate(take):
                p = by_user[u].copy()
                p["user_id"] = f"{u}#{dup}"
                parts.append(p)
            bs = mom_from_cells(pd.concat(parts, ignore_index=True))
            boots["person_share"].append(bs["person_share"])
            boots["interaction_share"].append(bs["interaction_share"])
        p_lo, p_hi = np.nanpercentile(boots["person_share"], [2.5, 97.5])
        s_lo, s_hi = np.nanpercentile(boots["interaction_share"], [2.5, 97.5])
        trait, era = est["person_share"], est["condition_share"]
        state, resid = est["interaction_share"], est["residual_share"]
        spectrum_rows.append({
            "construct": construct, "trait_share": trait, "trait_ci": f"[{p_lo:.3f},{p_hi:.3f}]",
            "era_share": era, "state_share": state, "state_ci": f"[{s_lo:.3f},{s_hi:.3f}]",
            "slice_noise_share": resid,
            "state_trait_ratio": state / trait if trait > 1e-9 else np.inf,
        })
        # per-occasion state precision: even/odd within quarter, trait removed
        eo = scored.assign(par=scored["slice_index"].astype(int) % 2)
        eo_cell = eo.groupby(["user_id", "condition", "par"])[construct].agg(["mean", "size"]).reset_index()
        wide = eo_cell.pivot_table(index=["user_id", "condition"], columns="par", values="mean").dropna()
        sizes = eo_cell.pivot_table(index=["user_id", "condition"], columns="par", values="size").min(axis=1)
        wide = wide.loc[sizes.reindex(wide.index) >= 2]
        for col in (0, 1):
            wide[col] = wide[col] - wide.groupby(level=0)[col].transform("mean")
        counts = wide.groupby(level=0).size()
        wide = wide.loc[counts.reindex(wide.index.get_level_values(0)).to_numpy() >= 3]
        if len(wide) > 200:
            r = float(np.corrcoef(wide[0], wide[1])[0, 1])
            state_rows.append({"construct": construct, "n_user_quarters": int(len(wide)),
                               "state_split_half_r": r, "state_sb_full": spearman_brown(r)})

    spectrum = pd.DataFrame(spectrum_rows)
    state_prec = pd.DataFrame(state_rows)
    fp = spectrum.set_index("construct")
    checks = {
        "P_E5a_firstperson_trait_gt_state": bool(
            fp.loc["first_person_usage_v2", "trait_share"] > fp.loc["first_person_usage_v2", "state_share"]),
        "P_E5b_tension_stateratio_gt_firstperson": bool(
            fp.loc["tension_core_v2", "state_trait_ratio"] > fp.loc["first_person_usage_v2", "state_trait_ratio"]),
        "P_E5c_tension_state_split_half": float(
            state_prec.set_index("construct").get("state_split_half_r", pd.Series(dtype=float)).get("tension_core_v2", np.nan)),
    }
    spectrum.to_csv(OUT_DIR / "trait_state_spectrum.csv", index=False)
    state_prec.to_csv(OUT_DIR / "state_precision.csv", index=False)
    (OUT_DIR / "e5_results.json").write_text(json.dumps(checks, indent=2, default=float) + "\n")
    REPORT.write_text(
        f"# SUICA E5 Trait-State Spectrum (rind-fixed: top subreddit; occasions: {OCC})\n\n"
        + spectrum.round(4).to_markdown(index=False)
        + "\n\n## Per-occasion state precision (trait removed)\n\n"
        + (state_prec.round(4).to_markdown(index=False) if len(state_prec) else "(insufficient cells)")
        + "\n\n```json\n" + json.dumps(checks, indent=2, default=float) + "\n```\n"
    )
    print(spectrum.round(3).to_string(index=False))
    print("\nstate precision:\n", state_prec.round(3).to_string(index=False) if len(state_prec) else "none")
    print(json.dumps(checks, indent=2, default=float))


if __name__ == "__main__":
    main()
