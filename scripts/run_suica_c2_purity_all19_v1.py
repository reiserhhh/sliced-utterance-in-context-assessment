#!/usr/bin/env python
"""C2 purity decomposition for ALL 19 constructs -> v4 flesh-purity gate.

Extends run_suica_c2_purity_decomposition_v1 (5 v2 constructs) to the 15
OP-5 wcl clusters, so the v4 battery can be assembled family-by-family
under the gate (THEORY_BASE 7.2, provisional thresholds):

  F-family (flesh style trait):  rho_class_disjoint >= 0.15 AND share < 0.30
  C-family (venue signature):    share > 0.30 with class_disjoint < 0.10
  composite:                     everything else determinate
  undetermined:                  rho_shared_matched < 0.10

Data path: pass-A slices must carry TEXT for wcl rederivation. The frozen
prep drops pass-A slice text, so this script REBUILDS pass-A slices with
the exact frozen rules (same functions, same defaults) and HARD-ASSERTS
equivalence with the frozen artifact (row count and per-(user,cond,half)
cell counts) before scoring. Estimators identical to the licensed v1
script (W-B/W-B2/W-B2c/W-B3); shares reported with the same caveats
(mediated_total = upper bound on mediation under coupling; bands per the
F6.3 alarm).

Tier-U only; no labels. Output feeds the v4 registry classification.
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
from scripts.run_suica_op9_embedding_baseline_v3 import rederive_op5_scores, OP5_KEPT, V3_BATTERY  # noqa: E402
from scripts.suica_v2_lib import score_slices_v2  # noqa: E402
from scripts.run_suica_c2_purity_decomposition_v1 import (  # noqa: E402
    component_series, estimands_from_series, crossfit_mix_share, corr)

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
CLASS_MAP = ROOT / "results" / "suica_e3_e4_choice_class_v2_s128" / "condition_class_map.csv"
FROZEN_PASSA = TIER_DIR / "phase2_passA_scored_s128.parquet"
OUT_DIR = ROOT / "results" / "suica_c2_purity_all19_v1"
REPORT = ROOT / "reports" / "suica_c2_purity_all19_v1.md"
SEED = 42
N_BOOT = 300
GAP_DAYS = 90


def rebuild_passA_with_text() -> pd.DataFrame:
    cache = TIER_DIR / "phase2_passA_slicetext_s128_rebuild.parquet"
    if cache.exists():
        return pd.read_parquet(cache)
    comments = pd.read_parquet(TIER_DIR / "tier_u_comments.parquet")
    comments["author"] = comments["author"].astype(str)
    comments["subreddit"] = comments["subreddit"].fillna("__missing__").astype(str)
    comments = comments.sort_values(["author", "created_utc"])
    rows = []
    for user_id, group in comments.groupby("author", sort=False):
        counts = group["subreddit"].value_counts()
        conds = counts.loc[counts >= 4].index.tolist()[:8]
        if len(conds) < 2:
            continue
        sub = group.loc[group["subreddit"].isin(conds)]
        t = sub["created_utc"].to_numpy(float)
        if len(t) < 12:
            continue
        t40, t60 = np.quantile(t, [0.40, 0.60])
        if (t60 - t40) / 86400.0 < GAP_DAYS:
            continue
        early = sub.loc[sub["created_utc"] <= t40]
        late = sub.loc[sub["created_utc"] >= t60]
        for half, part in [("early", early), ("late", late)]:
            for cond, cell in part.groupby("subreddit"):
                if len(cell) < 2:
                    continue
                text = "\n".join(cell["body"].astype(str))
                for row in fixed_token_slices_for_text(
                        text, slice_tokens=128, stride=128, min_slice_tokens=24, max_slices=10):
                    if PERSONALITY_LEAK_RE.search(row["slice_text"]):
                        continue
                    rows.append({"user_id": str(user_id), "condition": str(cond), "half": half,
                                 "slice_text": row["slice_text"]})
    frame = pd.DataFrame(rows)
    frozen = pd.read_parquet(FROZEN_PASSA)
    assert len(frame) == len(frozen), f"rebuild {len(frame)} != frozen {len(frozen)}"
    a = frame.groupby(["user_id", "condition", "half"]).size().sort_index()
    b = frozen.groupby(["user_id", "condition", "half"]).size().sort_index()
    assert a.equals(b), "per-cell counts differ from the frozen pass-A artifact"
    frame.to_parquet(cache, index=False)
    print(f"pass-A rebuild verified against frozen artifact: {len(frame)} slices, cells exact")
    return frame


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = rebuild_passA_with_text()
    scored = score_slices_v2(frame[["user_id", "condition", "half", "slice_text"]])
    wcl = rederive_op5_scores(frame.rename(columns={"half": "half_keep"})
                              .assign(half=lambda d: d["half_keep"])[["user_id", "half", "slice_text"]])
    wcl = pd.concat([frame[["condition"]].reset_index(drop=True),
                     wcl.reset_index(drop=True)], axis=1)
    long_v3 = scored
    cmap = pd.read_csv(CLASS_MAP)
    class_of = dict(zip(cmap["condition"], cmap["class_id"]))

    constructs = {c: long_v3 for c in V3_BATTERY} | {c: wcl for c in OP5_KEPT}
    rows = []
    for col, src in constructs.items():
        um = src.groupby(["user_id", "half"])[col].mean().unstack().dropna()
        rho_raw = corr(um["early"], um["late"])
        cell = (src.groupby(["user_id", "condition", "half"])[col].mean()
                .unstack("half").dropna())
        cell.index.names = ["user", "condition"]
        series = component_series(cell, class_of)
        est = estimands_from_series(series)
        mix = crossfit_mix_share(src.rename(columns={"user_id": "user_id"}), col, rng)
        share = np.nan
        if est["rho_shared_matched"] and est["rho_shared_matched"] >= 0.10:
            share = float(np.clip(1 - est["rho_cond_disjoint"] / est["rho_shared_matched"], 0, 1))
        boot = []
        n = len(series)
        for _ in range(N_BOOT):
            sub = series.iloc[rng.integers(0, n, n)]
            e2 = estimands_from_series(sub)
            if e2["rho_shared_matched"] and e2["rho_shared_matched"] >= 0.10:
                boot.append(float(np.clip(1 - e2["rho_cond_disjoint"] / e2["rho_shared_matched"], 0, 1)))
        ci = (float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))) if len(boot) >= 100 else (np.nan, np.nan)
        if np.isnan(share):
            family = "undetermined"
        elif est["rho_class_disjoint"] >= 0.15 and share < 0.30:
            family = "F-family (flesh trait)"
        elif share > 0.30 and est["rho_class_disjoint"] < 0.10:
            family = "C-family (venue signature)"
        else:
            family = "composite"
        rows.append({"construct": col, "rho_raw": rho_raw,
                     "rho_shared_matched": est["rho_shared_matched"],
                     "rho_cond_disjoint": est["rho_cond_disjoint"],
                     "rho_class_disjoint": est["rho_class_disjoint"],
                     "c1_share": share, "ci_lo": ci[0], "ci_hi": ci[1],
                     "mediated_total_upper": mix["mediated_total"],
                     "v4_family": family})
        print(f"{col}: class_disj={est['rho_class_disjoint']:.3f} share={share if np.isnan(share) else round(share,3)} -> {family}")
    df = pd.DataFrame(rows)
    df.round(4).to_csv(OUT_DIR / "all19_purity.csv", index=False)
    summary = {"n_F_family": int((df["v4_family"].str.startswith("F-")).sum()),
               "n_C_family": int((df["v4_family"].str.startswith("C-")).sum()),
               "n_composite": int((df["v4_family"] == "composite").sum()),
               "n_undetermined": int((df["v4_family"] == "undetermined").sum())}
    (OUT_DIR / "all19_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    REPORT.write_text("# C2 purity decomposition — ALL 19 constructs (v4 gate classification)\n\n"
                      + df.round(3).to_markdown(index=False)
                      + "\n\n```json\n" + json.dumps(summary, indent=2) + "\n```\n\n"
                      "Gate (provisional, THEORY 7.2): F-family iff class-disjoint >= 0.15 AND "
                      "share < 0.30. Estimators licensed by W-B/W-B2/W-B2c/W-B3; mediated_total "
                      "= upper bound under coupling; shares are bands per the F6.3 alarm.\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
