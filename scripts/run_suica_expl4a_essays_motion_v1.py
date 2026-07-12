#!/usr/bin/env python
"""EXPL-4a -- first motion-layer x questionnaire test, Essays DEV half (F14, 97ecca2).

GOVERNANCE (read before touching anything below)
-------------------------------------------------
Split rule, quoted verbatim from docs/SUICA_CLAIMS_LEDGER.md:
  L90-92: "Governance note: Essays used dev-half TEXT only (stable-hash 50/50;
  frozen at data_sets/prepared/suica_tiers_v2/essays_regime_dev_half.csv); Big5
  label columns never loaded; Essays confirm-half untouched for P5."
  L455-456 (audit note): "Essays governance verified clean (labels never
  loaded; 50/50 split exact)."
The frozen dev-half id list is data_sets/prepared/suica_tiers_v2/
essays_regime_dev_half.csv (1,255 user_ids). Its provenance (for the record):
built by scripts/run_suica_rind_regime_test_v3.py L146-149 as
  essays = pd.read_csv(ESSAYS, usecols=["user_id", "text"])
  essays["h"] = essays["user_id"].map(stable_fraction)   # SHA1-derived in [0,1)
  dev = essays.loc[essays["h"] < 0.5]
i.e. a deterministic stable-hash 50/50 split, frozen once and reused ever
since by run_suica_dev_anchor_performance_v1.py, run_suica_v4_composite_v1.py,
and this script. This script does NOT recompute the hash; it reads the frozen
CSV as the single source of truth for dev-half membership.

Two-pass label-free mechanism (this script, `two_pass_dev_labels`):
  Pass 1: pd.read_csv(ESSAYS, usecols=["user_id"]) -- locates the CSV row
    position of every dev-half id. No label column is named in this call.
  Pass 2: pd.read_csv(ESSAYS, usecols=["user_id", *BIG5], skiprows=<callable>)
    where the callable physically excludes every non-dev-half data row at
    parse time. Confirm-half label bytes are never parsed into a DataFrame,
    not even transiently. (Validated against a synthetic file before use;
    see scratchpad test -- not part of this script.)
Text (user_id/text only) is read separately and is NOT gated -- it is not a
label column (same governance framing as run_suica_v6_e2_essays_motion_v1.py:
"the Essays loader reads ONLY columns [user_id, text]").

Banner: EXPLORATORY (Essays dev half, T1). No git commits are made by this
script; it only writes under results/suica_expl4a_essays_motion/.

Section map (per registration)
-------------------------------
A. Reuse results/suica_v6_e2_essays_motion/cache_essays_windows_scored19.parquet
   (label-free, built by run_suica_v6_e2_essays_motion_v1.py). Restrict to
   dev-half users FIRST; every subsequent recomputation (D-comp axes
   included) operates on that restricted cache only.
B. ~12 (here: 13 substantive + 2 structural-missingness indicators = 15)
   per-essay motion features; z-scored.
C. Per-essay MEAN of the 19 construct columns = the level-19 baseline.
D. Per-trait RidgeCV, KFold(5, shuffle, random_state=42); arms L / LM / M;
   reported r = mean of the per-FOLD Pearson r (not a pooled-OOF r -- see
   docstring note in `ridge_arm` for why this reading was chosen).
E. Single-feature Pearson screen, all motion features x 5 traits, flag
   |r| >= .08.
F. Outputs under results/suica_expl4a_essays_motion/.
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

from project_persona.suica import tokenize  # noqa: E402
import scripts.run_suica_c2_purity_all19_v1 as a19  # noqa: E402
import scripts.run_suica_v6_e2_essays_motion_v1 as e2  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
DEV_HALF_FILE = TIER_DIR / "essays_regime_dev_half.csv"
ESSAYS = ROOT / "data_sets" / "prepared" / "big5" / "essays_original_prepared.csv"
CACHE = ROOT / "results" / "suica_v6_e2_essays_motion" / "cache_essays_windows_scored19.parquet"
E2_JSON = ROOT / "results" / "suica_v6_e2_essays_motion" / "V6_E2_ESSAYS_MOTION.json"
OUT_DIR = ROOT / "results" / "suica_expl4a_essays_motion"

SEED = 42
BIG5 = ["Extraversion", "Neuroticism", "Agreeableness", "Conscientiousness", "Openness"]
SCREEN_THRESHOLD = 0.08
ALPHAS = np.logspace(-2, 3, 11)  # matches run_suica_expl3_motion_weightfit_v1.py / EXPL-2

BANNER = "EXPLORATORY (Essays dev half, T1)"
SPLIT_RULE_QUOTE = (
    'docs/SUICA_CLAIMS_LEDGER.md L90-92: "Governance note: Essays used dev-half '
    "TEXT only (stable-hash 50/50; frozen at data_sets/prepared/suica_tiers_v2/"
    'essays_regime_dev_half.csv); Big5 label columns never loaded; Essays '
    'confirm-half untouched for P5." L455-456 audit: "Essays governance verified '
    'clean (labels never loaded; 50/50 split exact)."'
)

MOTION_COLS = ["proj_dcomp1", "proj_dcomp2", "d_first_person", "d_tension", "d_directive",
               "d_novelty", "q_norm", "q_gust1E", "q_missing", "d2_mean_abs", "d2_autocorr",
               "d2_missing", "open_first_person", "m_windows", "log_tokens"]


def load_dev_ids() -> set[str]:
    ids = set(pd.read_csv(DEV_HALF_FILE)["user_id"].astype(str))
    assert len(ids) == 1255, f"frozen dev-half file changed shape: {len(ids)} (expected 1255)"
    return ids


def two_pass_dev_labels(dev_ids: set[str]) -> pd.DataFrame:
    """PASS 1: user_id only. PASS 2: skiprows excludes confirm rows at CSV-parse time."""
    pass1 = pd.read_csv(ESSAYS, usecols=["user_id"], dtype={"user_id": str})
    dev_positions = set(pass1.index[pass1["user_id"].isin(dev_ids)].tolist())
    assert len(dev_positions) == len(dev_ids), (
        f"dev ids missing from essays csv: found {len(dev_positions)} of {len(dev_ids)}")

    def skip_func(line_no: int) -> bool:
        if line_no == 0:
            return False  # header
        return (line_no - 1) not in dev_positions  # skip every confirm-half data row

    labels = pd.read_csv(ESSAYS, usecols=["user_id", *BIG5], dtype={"user_id": str},
                          skiprows=skip_func)
    assert len(labels) == len(dev_ids), f"pass-2 row count {len(labels)} != dev ids {len(dev_ids)}"
    assert set(labels["user_id"]) == dev_ids, "pass-2 returned a different id set than requested"
    assert labels[BIG5].notna().all().all(), "unexpected missing Big5 values in dev half"
    return labels.set_index("user_id")


def dev_text_tokens(user_ids: set[str]) -> pd.Series:
    """Label-free text-only read (never a label column); restricted to the given ids."""
    txt = pd.read_csv(ESSAYS, usecols=["user_id", "text"], dtype={"user_id": str})
    txt = txt.loc[txt["user_id"].isin(user_ids)]
    return txt.set_index("user_id")["text"].astype(str).apply(lambda t: len(tokenize(t)))


def build_d2_stats(cache_dev: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Per-eid second-difference ('D2') gust magnitude + lag-1 autocorrelation, m>=5 only."""
    rows = []
    for eid, grp in cache_dev.sort_values(["eid", "j"]).groupby("eid", sort=True):
        m = int(grp["m"].iloc[0])
        if m < 5:
            continue
        X = grp[cols].to_numpy(float)          # physically present rows, in j order
        d1 = np.diff(X, axis=0)                # first differences, len = n_rows-1
        d2 = np.diff(d1, axis=0)               # second differences, len = n_rows-2
        g = np.linalg.norm(d2, axis=1)         # per-position gust magnitude (>=0)
        mean_abs = float(g.mean())
        c = g - g.mean()
        if len(c) >= 2 and c[:-1].std() > 1e-12 and c[1:].std() > 1e-12:
            autocorr = float(np.corrcoef(c[:-1], c[1:])[0, 1])
        else:
            autocorr = float("nan")
        rows.append({"eid": eid, "d2_mean_abs": mean_abs, "d2_autocorr": autocorr,
                     "n_d2_points": len(g)})
    return pd.DataFrame(rows).set_index("eid")


def ridge_arm(X: np.ndarray, Y: np.ndarray, label: str) -> tuple[dict, dict]:
    """Per-trait RidgeCV, KFold(5, shuffle, rs=42).

    Reports the MEAN OF THE PER-FOLD Pearson r (compute r within each held-out
    fold, then average the 5 fold-level r values) -- the literal reading of
    the registration text ("report mean Pearson r across folds per trait").
    This differs from the "pool out-of-fold predictions, compute one r"
    convention used in some earlier SUICA scripts (e.g. run_suica_dev_anchor_
    performance_v1.py, run_suica_expl3_motion_weightfit_v1.py's ridge_arm) --
    flagged explicitly in the final report as an interpretive choice.
    """
    from sklearn.linear_model import RidgeCV
    from sklearn.model_selection import KFold
    from sklearn.preprocessing import StandardScaler
    kf = KFold(n_splits=5, shuffle=True, random_state=SEED)
    splits = list(kf.split(X))
    out, fold_detail = {}, {}
    for j, trait in enumerate(BIG5):
        y = Y[:, j]
        fold_rs = []
        for tr, te in splits:
            sc = StandardScaler().fit(X[tr])
            m = RidgeCV(alphas=ALPHAS).fit(sc.transform(X[tr]), y[tr])
            pred = m.predict(sc.transform(X[te]))
            r_fold = float(stats.pearsonr(pred, y[te])[0])
            fold_rs.append(r_fold)
        out[trait] = round(float(np.mean(fold_rs)), 4)
        fold_detail[trait] = [round(v, 4) for v in fold_rs]
    out["MEAN_BIG5"] = round(float(np.mean([out[t] for t in BIG5])), 4)
    print(f"[{label}] " + " ".join(f"{t[:1]}={out[t]:+.3f}" for t in BIG5)
          + f" mean={out['MEAN_BIG5']:+.4f}")
    return out, fold_detail


def main() -> None:
    print(BANNER)
    print("[split rule]", SPLIT_RULE_QUOTE)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------- governance: dev half + two-pass label read ----------------
    dev_ids = load_dev_ids()
    print(f"[split] frozen dev-half ids loaded from {DEV_HALF_FILE.relative_to(ROOT)}: {len(dev_ids)}")

    labels = two_pass_dev_labels(dev_ids)
    print(f"[labels] two-pass read complete: pass 1 (user_id only) located dev row positions; "
          f"pass 2 (skiprows-filtered) loaded {len(labels)} Big5 rows for dev-half ids only. "
          f"Confirm-half rows were never parsed into a DataFrame.")

    # ---------------- A: cache, restricted to dev half ----------------
    assert CACHE.exists(), f"expected Essays window cache missing: {CACHE}"
    cache_full = pd.read_parquet(CACHE)
    cols = list(a19.V3_BATTERY) + list(a19.OP5_KEPT)
    e2_result = json.loads(E2_JSON.read_text())
    assert cols == e2_result["constructs"], "construct column order mismatch vs E2 JSON"
    cache_dev = cache_full.loc[cache_full["user_id"].astype(str).isin(dev_ids)].copy()
    n_dev_cache = cache_dev["eid"].nunique()
    print(f"[cache] full cache: {cache_full['eid'].nunique()} essays (m>=2, label-free); "
          f"restricted to dev half: {n_dev_cache} essays")

    g = cache_dev.sort_values(["eid", "j"]).groupby("eid", sort=True)
    m_series = g["m"].first()
    user_series = g["user_id"].first()
    m_desc = m_series.describe()
    print(f"[m distribution, dev-half cache, n={len(m_series)}]")
    print(m_desc.to_string())
    print(f"  m>=3 (q-features computable): {int((m_series >= 3).sum())}; "
          f"m>=5 (D2-features computable): {int((m_series >= 5).sum())}; "
          f"m==5 exactly (degenerate 2-pair D2 autocorr): {int((m_series == 5).sum())}")
    n_m_gt_12 = int((m_series > 12).sum())
    n_m_le_12 = int((m_series <= 12).sum())
    print(f"  m<=12 (cache holds every real window, true lag-1 adjacency): {n_m_le_12} "
          f"({100 * n_m_le_12 / len(m_series):.1f}%); m>12 (cache subsampled to 12 "
          f"representative windows): {n_m_gt_12}")

    F = g[cols].first().to_numpy(float)
    Lst = g[cols].last().to_numpy(float)
    Lmean = g[cols].mean().to_numpy(float)
    eids_order = g[cols].first().index.to_numpy()
    m_arr = m_series.to_numpy(float)
    D = Lst - F                                   # per-eid last-first, dev-half only
    d_slope = D / (m_arr - 1)[:, None]            # "slope vector" d = (last-first)/(m-1)

    # ---------------- B1: recompute D-comp1/D-comp2 -- "the E2 recipe" on the DEV-restricted cache ----------------
    C_D = e2.corr_guarded(D)
    lamD, VD = e2.top_eigs(C_D, 2)
    proj_dcomp1 = d_slope @ VD[:, 0]
    proj_dcomp2 = d_slope @ VD[:, 1]
    print(f"[axes] D-comp1/D-comp2 recomputed on dev-half-restricted cache "
          f"(per-eid last-first -> corr_guarded -> top eigvecs): "
          f"lambda1={lamD[0]:.3f} lambda2={lamD[1]:.3f}")

    # ---------------- B2: d entries for the 4 V3_BATTERY constructs ----------------
    d_first_person = d_slope[:, cols.index("first_person_usage_v2")]
    d_tension = d_slope[:, cols.index("tension_core_v2")]
    d_directive = d_slope[:, cols.index("directive_action_v2")]
    d_novelty = d_slope[:, cols.index("novelty_play_v2")]

    # ---------------- B3: q-contrast (m>=3), norm + gust1_E projection ----------------
    w0, wm, wl, eids3, users3 = e2.triples(cache_dev, cols, "eid")
    q = (w0 - 2 * wm + wl) / np.sqrt(6.0)          # literal registered formula, no sd normalization
    q_norm_covered = np.linalg.norm(q, axis=1)
    gust1_e_vector = np.asarray(e2_result["C_motion"]["gusts"][0]["vector"], dtype=float)
    assert len(gust1_e_vector) == len(cols)
    q_gust1e_covered = q @ gust1_e_vector
    q_frame = pd.DataFrame({"eid": eids3, "q_norm": q_norm_covered,
                            "q_gust1E": q_gust1e_covered}).set_index("eid")
    q_full = q_frame.reindex(eids_order)
    q_missing = q_full["q_norm"].isna().to_numpy(float)
    q_norm_imp = q_full["q_norm"].fillna(q_frame["q_norm"].mean()).to_numpy(float)
    q_gust1e_imp = q_full["q_gust1E"].fillna(q_frame["q_gust1E"].mean()).to_numpy(float)
    print(f"[q-contrast] m>=3 covered: {len(eids3)} of {n_dev_cache}; "
          f"{int(q_missing.sum())} essays (m==2) mean-imputed with q_missing indicator")

    # ---------------- B4: D2 stats (m>=5), mean-impute + indicator ----------------
    d2_frame = build_d2_stats(cache_dev, cols)
    d2_full = d2_frame.reindex(eids_order)
    d2_missing = d2_full["d2_mean_abs"].isna().to_numpy(float)
    d2_mean_abs_imp = d2_full["d2_mean_abs"].fillna(d2_frame["d2_mean_abs"].mean()).to_numpy(float)
    d2_autocorr_imp = d2_full["d2_autocorr"].fillna(d2_frame["d2_autocorr"].mean(skipna=True)).to_numpy(float)
    n_autocorr_nan = int(d2_frame["d2_autocorr"].isna().sum())
    print(f"[D2 stats] m>=5 covered: {len(d2_frame)} of {n_dev_cache}; "
          f"{int(d2_missing.sum())} essays (m<5) mean-imputed with d2_missing indicator; "
          f"within covered essays, {n_autocorr_nan} have a degenerate/undefined autocorr "
          f"(zero-variance 2-3 point series) -- also mean-imputed over the remaining covered essays")

    # ---------------- B5/B6: open_first_person, m, log tokens ----------------
    open_first_person = F[:, cols.index("first_person_usage_v2")]
    token_counts = dev_text_tokens(set(user_series.loc[eids_order].astype(str)))
    tok_arr = user_series.loc[eids_order].astype(str).map(token_counts).to_numpy(float)
    assert np.isfinite(tok_arr).all(), "token count lookup failed for some dev essays"
    log_tokens = np.log(tok_arr)

    # ---------------- assemble motion feature frame (raw, imputed) ----------------
    raw = pd.DataFrame({
        "eid": eids_order, "user_id": user_series.loc[eids_order].astype(str).to_numpy(),
        "proj_dcomp1": proj_dcomp1, "proj_dcomp2": proj_dcomp2,
        "d_first_person": d_first_person, "d_tension": d_tension,
        "d_directive": d_directive, "d_novelty": d_novelty,
        "q_norm": q_norm_imp, "q_gust1E": q_gust1e_imp, "q_missing": q_missing,
        "d2_mean_abs": d2_mean_abs_imp, "d2_autocorr": d2_autocorr_imp, "d2_missing": d2_missing,
        "open_first_person": open_first_person, "m_windows": m_arr, "log_tokens": log_tokens,
    }).set_index("user_id")
    assert raw[MOTION_COLS].notna().all().all(), "unexpected NaN remains in motion features after imputation"

    # global z-score (per spec); per-fold StandardScaler applies again inside ridge_arm, as in EXPL-3
    z = raw[MOTION_COLS].copy()
    for c in MOTION_COLS:
        sd = z[c].std()
        z[c] = (z[c] - z[c].mean()) / (sd if sd > 1e-12 else 1.0)

    level = pd.DataFrame(Lmean, columns=cols, index=raw.index)

    # ---------------- join with dev-half labels (already loaded, label-free-governed) ----------------
    joined_users = [u for u in raw.index if u in labels.index]
    n_final = len(joined_users)
    print(f"[join] dev-half essays with BOTH cache coverage AND labels: {n_final} "
          f"(of {len(dev_ids)} frozen dev-half ids; {n_dev_cache} had cache coverage)")

    Y = labels.loc[joined_users, BIG5].to_numpy(float)
    X_L = level.loc[joined_users].to_numpy(float)
    X_M = z.loc[joined_users, MOTION_COLS].to_numpy(float)
    X_LM = np.hstack([X_L, X_M])

    # ---------------- D: fits ----------------
    arm_L, fold_L = ridge_arm(X_L, Y, "L level-19")
    arm_LM, fold_LM = ridge_arm(X_LM, Y, "LM level+motion-34")
    arm_M, fold_M = ridge_arm(X_M, Y, "M motion-15")
    delta = {t: round(arm_LM[t] - arm_L[t], 4) for t in BIG5 + ["MEAN_BIG5"]}
    print(f"[delta L->LM] mean {delta['MEAN_BIG5']:+.4f}; per trait "
          + " ".join(f"{t[:1]}={delta[t]:+.4f}" for t in BIG5))

    # ---------------- E: single-feature screen ----------------
    print(f"[screen] single-feature Pearson r, motion features x 5 traits (n={n_final}); "
          f"flag |r| >= {SCREEN_THRESHOLD}:")
    screen_rows = []
    yc = labels.loc[joined_users, BIG5]
    header = "  " + f"{'feature':16s}" + " ".join(f"{t[:5]:>9s}" for t in BIG5)
    print(header)
    hits = []
    for feat in MOTION_COLS:
        x = raw.loc[joined_users, feat].to_numpy(float)
        cells = []
        for t in BIG5:
            r, p = stats.pearsonr(x, yc[t].to_numpy(float))
            flag = "*" if abs(r) >= SCREEN_THRESHOLD else " "
            if abs(r) >= SCREEN_THRESHOLD:
                hits.append({"feature": feat, "trait": t, "r": round(float(r), 4), "p": float(p)})
            screen_rows.append({"feature": feat, "trait": t, "r": round(float(r), 4),
                                "p": float(p), "n": int(len(x)),
                                "flag": bool(abs(r) >= SCREEN_THRESHOLD)})
            cells.append(f"{r:+.3f}{flag}")
        print(f"  {feat:16s}" + " ".join(f"{c:>9s}" for c in cells))
    print(f"[screen] |r| >= {SCREEN_THRESHOLD} hits: {hits if hits else 'none'}")

    # ---------------- registered-lean check (F14, docs/SUICA_THEORY_FORMAL_NOTES_V3.md) ----------------
    # Quoted registration (added at commit 97ecca2, this task's own registration commit):
    #   "LEANS: any single motion feature |r| >= .08 in <= 3 of 50 cells; incremental over
    #    a level-feature baseline in [+.00, +.02]; honest coin-flip overall."
    #   "STANDING KILL: if 4a and 4b both land <= 0, the conclusion 'questionnaire-criterion
    #    insensitivity to the motion layer' becomes the recorded verdict pending BEHAVIORAL
    #    criteria (the native corpus's job)."
    n_hits, n_cells = len(hits), len(screen_rows)
    lean_screen_met = n_hits <= 3
    lean_delta_met = 0.0 <= delta["MEAN_BIG5"] <= 0.02
    standing_kill_half = delta["MEAN_BIG5"] <= 0.0
    registered_leans = {
        "quote": "LEANS: any single motion feature |r| >= .08 in <= 3 of 50 cells; incremental "
                 "over a level-feature baseline in [+.00, +.02]; honest coin-flip overall. "
                 "STANDING KILL: if 4a and 4b both land <= 0, the conclusion 'questionnaire-"
                 "criterion insensitivity to the motion layer' becomes the recorded verdict "
                 "pending BEHAVIORAL criteria (the native corpus's job).",
        "source": "docs/SUICA_THEORY_FORMAL_NOTES_V3.md, F14 section (git 97ecca2)",
        "single_feature_lean": {"registered": "<=3 of 50 cells at |r|>=.08",
                                 "actual": f"{n_hits} of {n_cells} cells "
                                           f"({n_hits} of 65 if restricted to the 13 "
                                           f"substantive features, excluding the 2 "
                                           f"missingness indicators)",
                                 "met": lean_screen_met},
        "delta_lean": {"registered": "[+.00, +.02]", "actual": delta["MEAN_BIG5"],
                       "met": lean_delta_met},
        "standing_kill_status": ("EXPL-4a lands <= 0 (" + f"{delta['MEAN_BIG5']:+.4f}"
                                  + ") -- HALF of the standing-kill condition is met; "
                                    "full kill requires EXPL-4b to also land <= 0 "
                                    "(not run by this script)") if standing_kill_half else
                                 ("EXPL-4a lands > 0 (" + f"{delta['MEAN_BIG5']:+.4f}"
                                  + ") -- standing-kill condition NOT triggered by this half"),
    }
    print(f"[registered leans] single-feature lean (<=3 of 50) met: {lean_screen_met} "
          f"({n_hits} hits observed); delta lean ([+.00,+.02]) met: {lean_delta_met} "
          f"(actual {delta['MEAN_BIG5']:+.4f}); standing-kill half-trigger: {standing_kill_half}")

    # ---------------- F: outputs ----------------
    result = {
        "banner": BANNER,
        "registration": "EXPL-4a (F14, research-repo commit 97ecca2) -- first motion-layer x "
                        "questionnaire test, Essays DEV half",
        "split_rule": {"quote": SPLIT_RULE_QUOTE,
                       "frozen_file": str(DEV_HALF_FILE.relative_to(ROOT)),
                       "n_dev_ids": len(dev_ids),
                       "provenance": "scripts/run_suica_rind_regime_test_v3.py L146-149: "
                                     "dev = essays.loc[stable_fraction(user_id) < 0.5] "
                                     "(SHA1-derived deterministic stable fraction), frozen once"},
        "governance": {"two_pass_mechanism":
                       "pass 1 = pd.read_csv(usecols=['user_id']) to locate dev row positions; "
                       "pass 2 = pd.read_csv(usecols=['user_id', *BIG5], skiprows=<callable "
                       "excluding every non-dev data row at parse time>). Confirm-half label "
                       "bytes are never parsed into a DataFrame. Validated on a synthetic file "
                       "before use (not part of this script).",
                       "confirm_half_labels": "untouched (n=" + str(2467 - len(dev_ids)) + ")",
                       "text_reads": "user_id/text only (not a label); read separately for "
                                     "token counts, restricted to dev-half ids"},
        "coverage": {"n_dev_ids": len(dev_ids), "n_dev_with_cache_coverage": int(n_dev_cache),
                     "n_dev_with_cache_and_labels": n_final,
                     "m_distribution": {k: (None if pd.isna(v) else float(v))
                                        for k, v in m_desc.to_dict().items()},
                     "n_m_ge_3": int((m_series >= 3).sum()), "n_m_ge_5": int((m_series >= 5).sum()),
                     "n_m_eq_5": int((m_series == 5).sum()),
                     "n_m_le_12_true_lag1": n_m_le_12, "n_m_gt_12_subsampled_cache": n_m_gt_12,
                     "n_d2_covered_m_ge_5": int(len(d2_frame)),
                     "n_d2_autocorr_degenerate_nan": n_autocorr_nan},
        "features": {"level_19": cols, "motion_15": MOTION_COLS,
                     "motion_feature_notes": {
                         "proj_dcomp1/2": "d=(last-first)/(m-1) projected on D-comp1/2, "
                                          "recomputed from the dev-restricted cache "
                                          "(per-eid last-first -> corr_guarded -> top eigvecs)",
                         "d_first_person/tension/directive/novelty": "raw d entries for the "
                                                                     "4 V3_BATTERY constructs",
                         "q_norm/q_gust1E": "m>=3 triple q=(w0-2wm+wl)/sqrt(6); norm and "
                                            "projection on the frozen gust1_E vector "
                                            "(E2 JSON, not recomputed); mean-imputed + "
                                            "q_missing indicator for m==2",
                         "d2_mean_abs/d2_autocorr": "m>=5 second-difference series over "
                                                     "physically-present cache windows; mean "
                                                     "magnitude + lag-1 autocorr of the "
                                                     "centered series; mean-imputed + "
                                                     "d2_missing indicator for m<5",
                         "open_first_person": "first_person_usage_v2 at j=0",
                         "m_windows/log_tokens": "m and log(re-tokenized full essay text)"}},
        "arm_L_level19": {"per_trait": arm_L, "per_fold": fold_L},
        "arm_LM_level_plus_motion": {"per_trait": arm_LM, "per_fold": fold_LM},
        "arm_M_motion_only": {"per_trait": arm_M, "per_fold": fold_M},
        "delta_L_to_LM": delta,
        "registered_leans": registered_leans,
        "single_feature_screen": screen_rows,
        "screen_hits_abs_r_ge_008": hits,
        "ambiguities_and_design_decisions": [
            "D-comp1/D-comp2 recomputed AFTER restricting the E2 cache to dev-half users only "
            "(not on the full label-free cache) -- reading 'restrict to DEV-half users once "
            "the rule is known' (section A) as applying transitively to every downstream "
            "recomputation, including the axis recipe.",
            "gust1_E vector taken as-is from the existing V6_E2_ESSAYS_MOTION.json (not "
            "recomputed on dev-half-only data), per the literal instruction to pull 'vector "
            "from ... [\"C_motion\"][\"gusts\"][0][\"vector\"]'; this axis was estimated "
            "label-free on the full 2,309-essay cache (dev+confirm text, no labels), so reuse "
            "here has no label-governance implication.",
            "proj_dcomp1/2 use the raw slope vector d dotted with the (correlation-space) "
            "eigenvectors, without an extra per-column standardization of d -- the final "
            "global z-score step normalizes the resulting scalar feature regardless; this "
            "mirrors the 'simpler' framing used for the q-projection in the registration text.",
            "q = (w0-2wm+wl)/sqrt(6) computed WITHOUT the E2 script's extra /sd_w column "
            "normalization -- the registration text gives this exact formula with no sd term; "
            "taken literally rather than importing E2's normalization.",
            "'set NaN -> mean-impute + indicator' was stated explicitly only for the D2 "
            "features (point 4); the same structural-missingness logic was generalized to the "
            "q-contrast features (point 3, m<3), since both are undefined below a window-count "
            "threshold and Ridge/Pearson cannot consume NaNs. This adds 2 indicator columns on "
            "top of the ~12 specified (13 substantive + 2 indicators = 15 motion features).",
            f"D2 second differences use POSITIONALLY adjacent cache rows. For m<=12 essays "
            f"({n_m_le_12} of {n_dev_cache} dev-covered essays; "
            f"{100 * n_m_le_12 / n_dev_cache:.1f}%) these are true consecutive 128-token "
            f"windows. For the {n_m_gt_12} dev-covered essays with m>12 (of 12 such essays "
            f"in the full 2,309-essay corpus), the frozen cache stores only 12 "
            f"linspace-subsampled representative windows, so 'lag-1' there spans a larger "
            f"and uneven token gap -- an inherited property of reusing the cache as "
            f"instructed, not a new choice.",
            f"Lag-1 D2 autocorrelation is close to mathematically degenerate for the median "
            f"essay: m==5 (the modal value, {int((m_series == 5).sum())} of {n_dev_cache} "
            f"dev-covered essays) gives exactly 3 D2 points -> 2 correlation pairs, which is "
            f"always +-1 or NaN by construction. Of the {len(d2_frame)} m>=5 covered essays, "
            f"{n_autocorr_nan} produced a degenerate (zero-variance) NaN autocorrelation, "
            f"mean-imputed along with the structural m<5 NaNs. Reported honestly (see the m "
            f"distribution above) rather than smoothed over.",
            "Section D 'mean Pearson r across folds' was read literally: Pearson r is computed "
            "WITHIN each of the 5 held-out folds and then averaged per trait -- NOT the "
            "'pool out-of-fold predictions, compute one r' convention used by "
            "run_suica_dev_anchor_performance_v1.py and run_suica_expl3_motion_weightfit_v1.py. "
            "Per-fold r values are reported alongside the mean for full transparency.",
            "RidgeCV alpha grid np.logspace(-2, 3, 11) reused from the closest sibling script "
            "(run_suica_expl3_motion_weightfit_v1.py / EXPL-2), since none was specified here.",
            "log_tokens uses an exact re-tokenization of the raw essay text (label-free, "
            "user_id/text-only read) rather than a m*128 proxy, to avoid near-perfect "
            "collinearity with the 'm' feature (m*WIN and m differ only by a constant offset "
            "in log-space under floor division)."],
    }
    (OUT_DIR / "EXPL4A_ESSAYS_MOTION.json").write_text(json.dumps(result, indent=2))

    md = ["# EXPL-4a -- motion-layer x questionnaire test (Essays DEV half, EXPLORATORY T1)", "",
          f"> {BANNER}", f"> F14, research-repo commit 97ecca2. No git commits made by this run.",
          "",
          "## Split rule", "", SPLIT_RULE_QUOTE, "",
          f"Frozen file: `{DEV_HALF_FILE.relative_to(ROOT)}` ({len(dev_ids)} user_ids). "
          "Confirm-half labels were never loaded (two-pass skiprows-filtered read; see script "
          "docstring).", "",
          "## Coverage", "",
          f"Dev-half ids: {len(dev_ids)}. With Essays window cache coverage (m>=2): {n_dev_cache}. "
          f"With BOTH cache coverage and labels: {n_final}.", "",
          "m distribution (dev-half cache):", "", "```", m_desc.to_string(), "```",
          f"m>=3: {int((m_series>=3).sum())}; m>=5: {int((m_series>=5).sum())}; "
          f"m==5 exactly: {int((m_series==5).sum())}.", "",
          "## Arms (per-trait RidgeCV, KFold(5, shuffle, rs=42); r = mean of per-fold r)", "",
          "| arm | E | N | A | C | O | mean |", "|---|---|---|---|---|---|---|"]
    for name, arm in [("L: level-19", arm_L), ("LM: level+motion-34", arm_LM),
                      ("M: motion-15 alone", arm_M)]:
        md.append("| " + name + " | " + " | ".join(f"{arm[t]:+.3f}" for t in BIG5)
                  + f" | {arm['MEAN_BIG5']:+.4f} |")
    md += ["",
           f"Delta(L->LM): mean {delta['MEAN_BIG5']:+.4f}; per trait "
           + ", ".join(f"{t} {delta[t]:+.4f}" for t in BIG5) + ".", "",
           f"## Single-feature screen (|r| >= {SCREEN_THRESHOLD} flagged)", "",
           (", ".join(f"{h['feature']}->{h['trait']} r={h['r']:+.3f}" for h in hits)
            if hits else "no hits at this threshold"),
           "",
           "## Registered-lean check (F14, docs/SUICA_THEORY_FORMAL_NOTES_V3.md, git 97ecca2)",
           "", f"> {registered_leans['quote']}", "",
           f"- Single-feature lean (<=3 of 50 cells at |r|>=.08): **"
           + ("MET" if lean_screen_met else "NOT MET")
           + f"** -- {n_hits} of {n_cells} cells observed.",
           f"- Delta(L->LM) lean ([+.00, +.02]): **" + ("MET" if lean_delta_met else "NOT MET")
           + f"** -- actual {delta['MEAN_BIG5']:+.4f}.",
           f"- Standing-kill status: {registered_leans['standing_kill_status']}.",
           "",
           "## Ambiguities / design decisions", ""]
    md += [f"- {a}" for a in result["ambiguities_and_design_decisions"]]
    (OUT_DIR / "EXPL4A_ESSAYS_MOTION.md").write_text("\n".join(md) + "\n")
    print("written:", OUT_DIR / "EXPL4A_ESSAYS_MOTION.json")
    print("written:", OUT_DIR / "EXPL4A_ESSAYS_MOTION.md")


if __name__ == "__main__":
    main()
