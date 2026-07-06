#!/usr/bin/env python
"""C2 purity decomposition v1 — how much of "style-base stability" is
choice-mediated? (FALSIFIER_MATRIX row T4; estimators licensed by the
wrong-world suite W-B/W-B2.)

Theory backdrop (FORMAL_NOTES Prop F1/F2): under the rind model,
E[y_u] = flesh_u + sum_r P(r|u) rind_r (+ mean gamma). The mix term is
person-stable whenever choice is (T3), so raw/shared-set retest OVERSTATES
flesh stability. With DISJOINT condition sets and independent rind effects,
cov(mix_A, mix_B) = 0, so the disjoint-set estimand isolates flesh.
Class-level rind correlation re-introduces mediation; the class-disjoint
variant removes that too.

Estimands per construct (all Tier-U pass-A data, >= 90-day-gap halves;
NO labels anywhere):
  rho_raw            user mean over all slices, early vs late (P1 estimand)
  rho_shared_matched shared condition set, k conditions per user, SAME set
                     both halves — volume-matched composite comparator
  rho_cond_disjoint  same k count, set A early vs set B late (both orders,
                     averaged) — venue-identity mediation removed
  rho_class_disjoint sets disjoint at frozen-class level — class-level
                     mediation removed as well
  mix_share          cross-fitted covariance accounting (venue effects from
                     the other user fold; share of raw early-late covariance
                     carried by the venue-mix term)

Volume-fairness design: shared_matched and cond_disjoint use the SAME number
of conditions per user per half (k = floor(#shared/2)), so their difference
is not a volume artifact. Sensitivity: k-cell slice-count equalization is
approximate (conditions differ in size); the A/B alternating split plus
both-orders averaging symmetrizes in expectation.

Pre-committed interpretation rule (FALSIFIER_MATRIX): per construct,
C1-mediated share_hat = 1 - rho_cond_disjoint / rho_shared_matched
(clamped to [0,1], defined only when rho_shared_matched >= 0.10):
  share > 0.30  -> THEORY table must relabel that construct's C2 row as
                   "C1+C2 composite" (theory correction);
  share < 0.10  -> flesh reading stands;
  else          -> reported as-is (partial mediation).
H(M) gradient (T9 continuous form): within slice-count quartiles, retest r
by rind-entropy tercile; pre-committed direction: low-entropy tercile >
high-entropy tercile (paired across volume strata).
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

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
CLASS_MAP = ROOT / "results" / "suica_e3_e4_choice_class_v2_s128" / "condition_class_map.csv"
OUT_DIR = ROOT / "results" / "suica_c2_purity_decomposition_v1"
REPORT = ROOT / "reports" / "suica_c2_purity_decomposition_v1.md"
CONSTRUCTS = ["first_person_usage_v2", "directive_action_v2", "tension_core_v2",
              "novelty_play_v2", "adversity_recovery_v2"]
SEED = 42
N_BOOT = 500


def corr(a: pd.Series, b: pd.Series) -> float:
    j = pd.concat([a, b], axis=1).dropna()
    if len(j) < 30 or j.iloc[:, 0].std() == 0 or j.iloc[:, 1].std() == 0:
        return np.nan
    return float(j.iloc[:, 0].corr(j.iloc[:, 1]))


def user_sets(cell: pd.DataFrame) -> dict:
    """cell: index (user, condition), columns early/late cell means (one construct).
    Return per-user shared conditions sorted (deterministic)."""
    out = {}
    for u, g in cell.groupby(level="user"):
        conds = sorted(g.index.get_level_values("condition"))
        if len(conds) >= 2:
            out[u] = conds
    return out


def component_series(cell: pd.DataFrame, class_of: dict) -> pd.DataFrame:
    """Per-user component series computed ONCE; correlations and bootstraps
    operate on this table (users x components) afterwards."""
    sets = user_sets(cell)
    rows = {}
    for u, conds in sets.items():
        k2 = (len(conds) // 2) * 2
        use = conds[:k2]
        A, B = use[0::2], use[1::2]
        g = cell.xs(u, level="user")
        row = {"sh_e": g.loc[A, "early"].mean(), "sh_l": g.loc[A, "late"].mean(),
               "dA_e": g.loc[A, "early"].mean(), "dB_l": g.loc[B, "late"].mean(),
               "dB_e": g.loc[B, "early"].mean(), "dA_l": g.loc[A, "late"].mean()}
        classes = sorted({class_of.get(c, -1) for c in use})
        if len(classes) >= 2:
            clA = set(classes[0::2])
            Ac = [c for c in use if class_of.get(c, -1) in clA]
            Bc = [c for c in use if class_of.get(c, -1) not in clA]
            if Ac and Bc:
                row.update({"cd_e": g.loc[Ac, "early"].mean(), "cd_l": g.loc[Bc, "late"].mean(),
                            "cd2_e": g.loc[Bc, "early"].mean(), "cd2_l": g.loc[Ac, "late"].mean()})
        rows[u] = row
    return pd.DataFrame(rows).T


def estimands_from_series(s: pd.DataFrame) -> dict:
    rho_shared = corr(s["sh_e"], s["sh_l"])
    rho_dis = np.nanmean([corr(s["dA_e"], s["dB_l"]), corr(s["dB_e"], s["dA_l"])])
    if "cd_e" in s.columns:
        rho_cls = np.nanmean([corr(s["cd_e"], s["cd_l"]), corr(s["cd2_e"], s["cd2_l"])])
        n_cls = int(s["cd_e"].notna().sum())
    else:
        rho_cls, n_cls = np.nan, 0
    return {"rho_shared_matched": rho_shared, "rho_cond_disjoint": float(rho_dis),
            "rho_class_disjoint": float(rho_cls),
            "n_users_setbased": int(len(s)), "n_users_classdisjoint": n_cls}


def crossfit_mix_share(long: pd.DataFrame, col: str, rng) -> dict:
    users = long["user_id"].unique()
    fold = pd.Series(rng.integers(0, 2, len(users)), index=users)
    mixes = {}
    for f in (0, 1):
        train = long[long["user_id"].map(fold) != f]
        vhat = train.groupby("condition")[col].mean() - train[col].mean()
        test = long[long["user_id"].map(fold) == f].copy()
        test["vhat"] = test["condition"].map(vhat)
        m = test.dropna(subset=["vhat"]).groupby(["user_id", "half"])["vhat"].mean().unstack()
        for u in m.index:
            if {"early", "late"} <= set(m.columns):
                mixes[u] = (m.at[u, "early"], m.at[u, "late"])
    mixdf = pd.DataFrame(mixes, index=["mix_e", "mix_l"]).T
    um = long.groupby(["user_id", "half"])[col].mean().unstack()
    j = um.join(mixdf).dropna()
    j["f_e"] = j["early"] - j["mix_e"]; j["f_l"] = j["late"] - j["mix_l"]
    cov_raw = float(np.cov(j["early"], j["late"])[0, 1])
    cov_mix = float(np.cov(j["mix_e"], j["mix_l"])[0, 1])
    cov_flesh = float(np.cov(j["f_e"], j["f_l"])[0, 1])
    return {"cov_raw": cov_raw, "cov_mix": cov_mix, "cov_flesh_hat": cov_flesh,
            "mix_share_cov": float(np.clip(cov_mix / cov_raw, 0, 1)) if cov_raw > 0 else np.nan,
            "mediated_total": float(np.clip(1 - cov_flesh / cov_raw, 0, 1)) if cov_raw > 0 else np.nan}


def hm_gradient(long: pd.DataFrame, col: str) -> dict:
    um = long.groupby(["user_id", "half"])[col].mean().unstack().dropna()
    counts = long.groupby("user_id").size().reindex(um.index)
    ent = {}
    for u, g in long[long["user_id"].isin(um.index)].groupby("user_id"):
        p = g["condition"].value_counts(normalize=True).to_numpy()
        ent[u] = float(-(p * np.log(p)).sum())
    ent = pd.Series(ent).reindex(um.index)
    vol_q = pd.qcut(counts, 4, labels=False, duplicates="drop")
    rows, lo_list, hi_list = [], [], []
    for q in sorted(vol_q.dropna().unique()):
        idx = vol_q.index[vol_q == q]
        if len(idx) < 90:
            continue
        terc = pd.qcut(ent.loc[idx], 3, labels=False, duplicates="drop")
        r_lo = corr(um.loc[terc.index[terc == 0], "early"], um.loc[terc.index[terc == 0], "late"])
        r_hi = corr(um.loc[terc.index[terc == 2], "early"], um.loc[terc.index[terc == 2], "late"])
        rows.append({"vol_quartile": int(q), "r_low_entropy": r_lo, "r_high_entropy": r_hi,
                     "n_per_tercile": int((terc == 0).sum())})
        if not (np.isnan(r_lo) or np.isnan(r_hi)):
            lo_list.append(r_lo); hi_list.append(r_hi)
    return {"strata": rows,
            "mean_r_low_entropy": float(np.mean(lo_list)) if lo_list else np.nan,
            "mean_r_high_entropy": float(np.mean(hi_list)) if hi_list else np.nan,
            "direction_low_gt_high": bool(np.mean(lo_list) > np.mean(hi_list)) if lo_list else None}


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long = pd.read_parquet(TIER_DIR / "phase2_passA_scored_s128.parquet")
    long = long.rename(columns={c: c for c in long.columns})
    cmap = pd.read_csv(CLASS_MAP)
    class_of = dict(zip(cmap["condition"], cmap["class_id"]))
    results = {}
    for col in CONSTRUCTS:
        um = long.groupby(["user_id", "half"])[col].mean().unstack().dropna()
        rho_raw = corr(um["early"], um["late"])
        cell = (long.groupby(["user_id", "condition", "half"])[col].mean()
                .unstack("half").dropna())
        cell.index.names = ["user", "condition"]
        series = component_series(cell, class_of)
        est = estimands_from_series(series)
        mix = crossfit_mix_share(long, col, rng)
        share = np.nan
        if est["rho_shared_matched"] and est["rho_shared_matched"] >= 0.10:
            share = float(np.clip(1 - est["rho_cond_disjoint"] / est["rho_shared_matched"], 0, 1))
        # user bootstrap on the precomputed component series (fast, equivalent)
        boot = []
        n = len(series)
        for _ in range(N_BOOT):
            sub = series.iloc[rng.integers(0, n, n)]
            e2 = estimands_from_series(sub)
            if e2["rho_shared_matched"] and e2["rho_shared_matched"] >= 0.10:
                boot.append(float(np.clip(1 - e2["rho_cond_disjoint"] / e2["rho_shared_matched"], 0, 1)))
        ci = (float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))) if len(boot) >= 100 else (np.nan, np.nan)
        verdict = ("relabel_C1C2_composite" if (not np.isnan(share)) and share > 0.30
                   else "flesh_reading_stands" if (not np.isnan(share)) and share < 0.10
                   else "partial_mediation" if not np.isnan(share) else "undetermined")
        results[col] = {"rho_raw": rho_raw, **est, **mix,
                        "c1_mediated_share": share, "share_ci95": ci,
                        "interpretation": verdict,
                        "hm_gradient": hm_gradient(long, col)}
        print(f"{col}: raw={rho_raw:.3f} shared_m={est['rho_shared_matched']:.3f} "
              f"cond_disj={est['rho_cond_disjoint']:.3f} class_disj={est['rho_class_disjoint']:.3f} "
              f"share={share if np.isnan(share) else round(share,3)} mixcov={mix['mix_share_cov']:.3f} "
              f"medtot={mix['mediated_total']:.3f} -> {verdict}")
    (OUT_DIR / "c2_purity_results.json").write_text(json.dumps(results, indent=2, default=float) + "\n")
    rows = []
    for col, r in results.items():
        rows.append({"construct": col, "rho_raw": r["rho_raw"],
                     "rho_shared_matched": r["rho_shared_matched"],
                     "rho_cond_disjoint": r["rho_cond_disjoint"],
                     "rho_class_disjoint": r["rho_class_disjoint"],
                     "c1_share": r["c1_mediated_share"], "ci": str([round(x, 3) if not np.isnan(x) else None for x in r["share_ci95"]]),
                     "mix_share_cov": r["mix_share_cov"], "mediated_total": r["mediated_total"],
                     "verdict": r["interpretation"],
                     "H(M)_low>high": r["hm_gradient"]["direction_low_gt_high"]})
    df = pd.DataFrame(rows)
    REPORT.write_text("# C2 purity decomposition v1 (Tier-U, label-free)\n\n"
                      + df.round(3).to_markdown(index=False)
                      + "\n\nSee docstring for estimand definitions and the interpretation rule "
                        "(round-9 revision note in FALSIFIER_MATRIX); estimators licensed by "
                        "wrong-world suite W-B/W-B2/W-B2c (class-disjoint) / W-B3 "
                        "(mediated_total = upper bound on mediation under coupling). "
                        "Flesh shares are BANDS per the F6.3 alarm (fp ~0.56-0.72); "
                        "see THEORY_BASE 7.1/7.5 and the ledger C2-PURITY row.\n")
    print(df.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
