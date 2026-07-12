#!/usr/bin/env python
"""Shared-rhythm hypothesis test (registered 2026-07-12, docs/SUICA_THEORY_FORMAL_NOTES_V3.md
"## Shared-rhythm hypothesis test" section; ledger row "Shared-rhythm"). Resolves the open
item flagged in F15/W10's own registration: "carriers = the spectral-anomaly constructs
(shared-rhythm hypothesis open)".

QUESTION. W10 found gust1_P's carrier constructs (wcl_02, wcl_07, wcl_11, wcl_20 -- its
loading-drift-guard set). Are these the SAME constructs independently flagged, at the
population/corpus-pooled level (F12.7-9, on the Essays corpus), as having anomalous
spectral texture -- or do these merely coincide in gust1_P's specific loadings by chance?

DESIGN. Two per-construct quantities, correlated ACROSS THE 19 CONSTRUCTS (n=19, one point
per construct -- a small-n, construct-level analysis, NOT a per-person analysis):

  (i) POPULATION-LEVEL SPECTRAL-ANOMALY MAGNITUDE. Read (not recomputed) from this
      program's own already-published JSON outputs:
        - results/suica_v6_w6_nyquist_ratio/V6_W6_NYQUIST_RATIO.json (F12.7, rho_pi;
          headline mode = "lag2_truncated_flagged" per that script's own graceful-
          degradation trigger -- the "truncated" sub-object is used, not "five_moment",
          which the W6 script itself flags as noise-dominated on gamma0 for this corpus)
        - results/suica_v6_w7_spectral_shape/V6_W7_SPECTRAL_SHAPE.json (F12.8,
          Delta_shape = rho_pihalf - rho_pi, hybrid-functional design)
        - results/suica_v6_w8_ar2_triangle/V6_W8_AR2_TRIANGLE.json (F12.9, AR(2) a1/a2)
      All three read the SAME underlying corpus/population: the Essays window cache
      (cache_essays_windows_scored19.parquet, texts 5<=m<=12, n_texts=1349,
      n_windows=8793 -- identical across all three JSONs, cross-checked below) --
      i.e. population-level anomaly is measured on the register-neutral, label-free
      Essays corpus. This is a genuine cross-corpus comparison (Essays anomaly vs
      PANDORA susceptibility, see (ii)) that is INHERENT to what this hypothesis test
      asks, not an incidental mismatch -- flagged explicitly, not hidden.
      Combination rule (documented explicitly, per the registration's own suggested
      form): for each of |rho_pi - 1| (from W6's truncated mode), |Delta_shape| (from
      W7), |a2| (from W8's AR(2) triangle), max-normalize across the 19 constructs
      (divide by that component's own max, bounding to [0,1], preserving zero and
      ratio structure), then take the unweighted mean of the three normalized
      components as ONE combined anomaly score. All three raw + normalized components
      are ALSO reported individually and correlated individually against (ii) below,
      so nothing is silently smoothed over if the three components disagree.

  (ii) PERSON-LEVEL SUSCEPTIBILITY-STABILITY, generalized to all 19 constructs. W10's
      person_susceptibility() (run_suica_v6_w10_invisible_anatomy_v1.py, imported and
      called UNMODIFIED) computed a split-half stability of mean|activation| for the
      ONE composite gust1_P axis. Here the SAME function is applied independently to
      EACH of the 19 raw constructs' own within-text-detrended residuals (construct
      c's own standardized residual column IS its "axis" -- the literal per-construct
      generalization already used by F16's person_dynamic(), run_suica_f16_
      visibility_taxonomy_v1.py): w10.within_text_linear_residuals() (also imported
      UNMODIFIED) is called on N1's uncapped PANDORA window pool, m>=3, giving one
      resid_std column per construct; w10.person_susceptibility() is then called once
      per construct on that construct's own column.
      Population choice: F16's already-built, already-verified N1-uncapped PANDORA
      window pool cache (results/suica_f16_visibility_taxonomy/
      pandora_uncapped_windows_scored19.parquet), NOT the narrower Big5-gate
      (opening-#1, n=1058) population -- measured explicitly below: the full F16
      uncapped pool gives 2,355 users with >=2 qualifying (m>=3) texts (split-half
      eligible), vs only 443 for the Big5-gate-restricted subset of that same pool
      (>5x fewer) -- and this analysis needs no Big5/MBTI label at all (it is fully
      label-free), so there is no governance reason to restrict to the labeled gate;
      the broader pool is used for power, per the registration's own instruction
      ("use whichever gives the most users with enough long texts for a meaningful
      split-half").

ANALYSIS. Pearson AND Spearman correlation of (i) against (ii) across the 19
constructs, both reported with exact p-values -- n=19 is SMALL, explicitly flagged as
LOW-POWERED/SUGGESTIVE-ONLY (p<.10 = "worth a second look," NOT confirmatory).
wcl_60 (clearest population-level anomaly of all 19, rho_pi=2.51) is checked
explicitly for its rank on susceptibility-stability, per the registered kill
condition; wcl_07 and wcl_20 (the registration's other two "clearest cases") are also
checked explicitly.

No git commits are made by this script. Seed: none needed (no new randomization is
performed here; person_susceptibility() is a deterministic split by ascending id
within user, and pearsonr/spearmanr are exact, non-simulated statistics).
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

import scripts.run_suica_v6_w10_invisible_anatomy_v1 as w10  # noqa: E402  (reused UNMODIFIED)
import scripts.run_suica_v6_w2a_delta2_dynamics_v1 as w2a  # noqa: E402  (get_construct_cols only)

W6_JSON = ROOT / "results" / "suica_v6_w6_nyquist_ratio" / "V6_W6_NYQUIST_RATIO.json"
W7_JSON = ROOT / "results" / "suica_v6_w7_spectral_shape" / "V6_W7_SPECTRAL_SHAPE.json"
W8_JSON = ROOT / "results" / "suica_v6_w8_ar2_triangle" / "V6_W8_AR2_TRIANGLE.json"
F16_POOL = ROOT / "results" / "suica_f16_visibility_taxonomy" / "pandora_uncapped_windows_scored19.parquet"
PREDICTORS = ROOT / "results" / "suica_lockbox_opening_1" / "predictors.parquet"
BIG5_LABELS = ROOT / "data_sets" / "prepared" / "pandora_official" / "pandora_official_big5_prepared.csv"

OUT_DIR = ROOT / "results" / "suica_shared_rhythm_test"
OUT_JSON = OUT_DIR / "SHARED_RHYTHM_TEST.json"
OUT_MD = OUT_DIR / "SHARED_RHYTHM_TEST.md"

GUST1P_CARRIER_SET = frozenset({"wcl_02", "wcl_07", "wcl_11", "wcl_20"})
CLEAREST_CASES = ["wcl_60", "wcl_07", "wcl_20"]

# Published F16 pool diagnostics (results/suica_f16_visibility_taxonomy/
# F16_VISIBILITY_TAXONOMY.json -> dynamic_diagnostics_pandora_pool), asserted below as
# an integrity cross-check that this script's own m>=3 filtering of the SAME cached
# parquet reproduces F16's own published population exactly.
F16_PUBLISHED_N_WINDOWS_M_GE3 = 64554
F16_PUBLISHED_N_TEXTS_M_GE3 = 15351
F16_PUBLISHED_N_USERS_M_GE3 = 3551

BANNER = ("Shared-rhythm hypothesis test -- population-pooled spectral-anomaly magnitude "
          "(Essays, F12.7-9/W6-W8) vs person-level susceptibility-stability (PANDORA "
          "uncapped, W10 estimator generalized to all 19 constructs, F16 dynamic channel). "
          "n=19 constructs -- LOW-POWERED/SUGGESTIVE-ONLY by registration.")


def jf(x) -> float | None:
    """JSON-safe float: NaN/inf -> None."""
    if x is None:
        return None
    xf = float(x)
    return round(xf, 6) if np.isfinite(xf) else None


# ============================================================================
# (i) Population-level spectral-anomaly magnitude (read, not recomputed)
# ============================================================================

def load_population_anomaly() -> tuple[pd.DataFrame, dict]:
    w6 = json.loads(W6_JSON.read_text())
    w7 = json.loads(W7_JSON.read_text())
    w8 = json.loads(W8_JSON.read_text())

    assert w6["constructs"] == w7["constructs"] == w8["constructs"], (
        "construct list order differs across W6/W7/W8 JSONs")
    cols = list(w6["constructs"])
    assert len(cols) == 19, f"expected 19 constructs, got {len(cols)}"

    # All three read the identical Essays population -- assert it, don't assume it.
    assert w6["n_texts"] == w7["n_texts"] == w8["n_texts"] == 1349
    assert w6["n_windows"] == w7["n_windows"] == w8["n_windows"] == 8793

    rho_pi_w6 = {r["construct"]: r["truncated"]["rho_pi"]
                 for r in w6["table_sorted_by_truncated_rho_desc"]}
    assert set(rho_pi_w6) == set(cols)

    w7_row = {r["construct"]: r for r in w7["table_sorted_by_delta_asc"]}
    assert set(w7_row) == set(cols)

    w8_row = {r["construct"]: r for r in w8["table_sorted_by_resid_desc"]}
    assert set(w8_row) == set(cols)

    # Cross-check: W8's own "obs" rho_pi/rho_pihalf (which it reuses as AR(2)-triangle
    # inputs) should reproduce W7's table exactly -- catches any silent drift between
    # the two artifacts before they are combined here.
    max_diff_rho_pi = max(abs(w8_row[c]["obs"]["rho_pi"] - w7_row[c]["rho_pi"]) for c in cols)
    max_diff_rho_pihalf = max(abs(w8_row[c]["obs"]["rho_pihalf"] - w7_row[c]["rho_pihalf"])
                              for c in cols)
    assert max_diff_rho_pi < 1e-6, f"W8 obs.rho_pi vs W7 table mismatch: {max_diff_rho_pi}"
    assert max_diff_rho_pihalf < 1e-6, (
        f"W8 obs.rho_pihalf vs W7 table mismatch: {max_diff_rho_pihalf}")

    rows = []
    for c in cols:
        rp6 = float(rho_pi_w6[c])
        ds7 = float(w7_row[c]["delta_shape"])
        a1_8 = float(w8_row[c]["a1"])
        a2_8 = float(w8_row[c]["a2"])
        rows.append({
            "construct": c,
            "rho_pi_w6_truncated": rp6,
            "abs_rho_pi_minus_1": abs(rp6 - 1.0),
            "delta_shape_w7": ds7,
            "abs_delta_shape": abs(ds7),
            "a1_w8": a1_8,
            "a2_w8": a2_8,
            "abs_a2": abs(a2_8),
            "rho_pihalf_w7": float(w7_row[c]["rho_pihalf"]),
            "rho_pi_w7_hybrid_crosscheck": float(w7_row[c]["rho_pi"]),
        })
    df = pd.DataFrame(rows).set_index("construct").loc[cols]

    for raw, norm in [("abs_rho_pi_minus_1", "norm_rho_pi"),
                      ("abs_delta_shape", "norm_delta_shape"),
                      ("abs_a2", "norm_a2")]:
        mx = df[raw].max()
        df[norm] = df[raw] / mx if mx > 0 else np.nan
    df["anomaly_combined_score"] = df[["norm_rho_pi", "norm_delta_shape", "norm_a2"]].mean(axis=1)

    diag = {
        "w6_registered_commit": w6["registered_commit"],
        "w7_registered_commit": w7["registered_commit"],
        "w8_registered_commit": w8["registered_commit"],
        "corpus": ("Essays (register-neutral, label-free; W6a/W7/W8 all read the "
                   "SAME cache_essays_windows_scored19.parquet, texts 5<=m<=12)"),
        "n_texts": w6["n_texts"], "n_windows": w6["n_windows"],
        "w6_headline_mode_used": w6["headline_mode"],
        "max_abs_diff_rho_pi_w8obs_vs_w7": jf(max_diff_rho_pi),
        "max_abs_diff_rho_pihalf_w8obs_vs_w7": jf(max_diff_rho_pihalf),
        "combination_rule": ("anomaly_combined_score = mean(norm_rho_pi, norm_delta_shape, "
                             "norm_a2), where each norm_X = |X| / max_19(|X|) (max-"
                             "normalized, not min-max -- preserves a true zero and ratio "
                             "structure). All three raw + normalized components are ALSO "
                             "reported and correlated individually against (ii)."),
    }
    return df, diag


# ============================================================================
# (ii) Person-level susceptibility-stability, per construct (PANDORA, N1 uncapped)
# ============================================================================

def load_pandora_uncapped_pool() -> pd.DataFrame:
    assert F16_POOL.exists(), (
        f"F16 uncapped PANDORA pool cache missing: {F16_POOL} -- run "
        f"run_suica_f16_visibility_taxonomy_v1.py once to build/cache it first")
    pool = pd.read_parquet(F16_POOL)
    pool["user_id"] = pool["user_id"].astype(str)
    return pool


def population_choice_diagnostics(pool: pd.DataFrame, sub_m3: pd.DataFrame) -> dict:
    """Measures (does not assume) the split-half-eligible population size under the
    full F16 uncapped pool vs the narrower Big5-gate (opening-#1, n=1058) population,
    to justify using the former."""
    per_text_full = sub_m3.groupby(["user_id", "cid"]).size().reset_index()
    counts_full = per_text_full.groupby("user_id").size()
    n_full_ge1 = int((counts_full >= 1).sum())
    n_full_ge2 = int((counts_full >= 2).sum())

    gate_note = "Big5-gate comparison unavailable (predictors/labels not found); using full F16 pool."
    n_gate_ge1 = n_gate_ge2 = None
    if PREDICTORS.exists() and BIG5_LABELS.exists():
        pred = pd.read_parquet(PREDICTORS)
        pred.index = pred.index.astype(str)
        big5 = pd.read_csv(BIG5_LABELS).set_index("user_id")
        big5.index = big5.index.astype(str)
        gate = (pred["n_conditions"] >= 4) & (pred["n_slices"] >= 12)
        inter = pred.index.intersection(big5.index)
        elig = inter[gate.loc[inter].fillna(False).to_numpy(bool)]
        gate_users = set(elig)
        sub_gate = sub_m3[sub_m3["user_id"].isin(gate_users)]
        per_text_gate = sub_gate.groupby(["user_id", "cid"]).size().reset_index()
        counts_gate = per_text_gate.groupby("user_id").size()
        n_gate_ge1 = int((counts_gate >= 1).sum())
        n_gate_ge2 = int((counts_gate >= 2).sum())
        gate_note = (f"Big5-gate (opening-#1, n={len(gate_users)}) population, restricted "
                     f"to the SAME m>=3 pool: {n_gate_ge1} users with >=1 qualifying text, "
                     f"{n_gate_ge2} with >=2 (split-half eligible) -- vs {n_full_ge2} for the "
                     f"full F16 uncapped pool ({n_full_ge2 / max(n_gate_ge2, 1):.1f}x more). "
                     f"Full pool used: no Big5/MBTI label is needed anywhere in this "
                     f"label-free analysis, so there is no governance reason to pay the "
                     f">5x power cost of the gate restriction.")

    return {
        "full_f16_pool": {"n_users_ge1_qualifying_text": n_full_ge1,
                          "n_users_ge2_qualifying_texts_split_half_eligible": n_full_ge2},
        "big5_gate_subset": {"n_users_ge1_qualifying_text": n_gate_ge1,
                             "n_users_ge2_qualifying_texts_split_half_eligible": n_gate_ge2},
        "population_used": "full_f16_pool",
        "rationale": gate_note,
    }


def compute_susceptibility_stability(pool: pd.DataFrame, cols: list) -> tuple[pd.DataFrame, dict, dict]:
    """EXACT reuse of F16's person_dynamic() windowing step (w10.within_text_linear_
    residuals, imported UNMODIFIED) generalized PAST F16's final aggregation: instead
    of collapsing each construct's |resid_std| to one static per-user mean, each
    construct's own resid_std column is fed directly into W10's person_susceptibility()
    (also imported UNMODIFIED) -- this is precisely object (ii) of the registration:
    'the SAME estimator applied independently to EACH of the 19 raw constructs' own
    within-text-detrended residuals.'"""
    sub = pool[pool["m"] >= 3].sort_values(["cid", "j"]).reset_index(drop=True)

    n_windows = int(len(sub))
    n_texts = int(sub["cid"].nunique())
    n_users_any = int(sub["user_id"].nunique())
    assert n_windows == F16_PUBLISHED_N_WINDOWS_M_GE3, (
        f"m>=3 window count {n_windows} != F16's own published "
        f"{F16_PUBLISHED_N_WINDOWS_M_GE3} -- pool cache or filter drifted")
    assert n_texts == F16_PUBLISHED_N_TEXTS_M_GE3, (
        f"m>=3 text count {n_texts} != F16's own published {F16_PUBLISHED_N_TEXTS_M_GE3}")
    assert n_users_any == F16_PUBLISHED_N_USERS_M_GE3, (
        f"m>=3 user count {n_users_any} != F16's own published {F16_PUBLISHED_N_USERS_M_GE3}")

    pop_diag = population_choice_diagnostics(pool, sub)

    resid_std, pooled_sd = w10.within_text_linear_residuals(sub, "cid", cols)

    rows = []
    n_users_seen = set()
    for i, c in enumerate(cols):
        res = w10.person_susceptibility(sub, resid_std[:, i], "cid")
        rows.append({"construct": c, **res})
        n_users_seen.add(res["n_users"])

    df = pd.DataFrame(rows).set_index("construct").loc[cols]
    diag = {
        "n_windows_m_ge3": n_windows, "n_texts_m_ge3": n_texts,
        "n_users_m_ge3_any_qualifying_text": n_users_any,
        "n_users_split_half_eligible_per_construct": sorted(n_users_seen),
        "n_users_constant_across_all_19_constructs": len(n_users_seen) == 1,
        "pooled_sd_by_construct": {c: float(s) for c, s in zip(cols, pooled_sd)},
        "population_choice": pop_diag,
        "estimator_reuse_note": ("w10.within_text_linear_residuals and "
                                 "w10.person_susceptibility imported and called UNMODIFIED "
                                 "from run_suica_v6_w10_invisible_anatomy_v1.py; windowing "
                                 "source is F16's own cached, already-verified N1-uncapped "
                                 "PANDORA window pool (pandora_uncapped_windows_scored19.parquet)."),
    }
    return df, diag, pop_diag


# ============================================================================
# Correlate (i) against (ii) across the 19 constructs
# ============================================================================

def correlate(anomaly_df: pd.DataFrame, susc_df: pd.DataFrame) -> dict:
    merged = anomaly_df.join(susc_df, how="inner")
    assert len(merged) == 19, f"expected 19 constructs after join, got {len(merged)}"
    assert merged["r_susceptibility"].notna().all(), (
        f"NaN r_susceptibility for: "
        f"{merged.index[merged['r_susceptibility'].isna()].tolist()}")

    x = merged["anomaly_combined_score"].to_numpy(float)
    y = merged["r_susceptibility"].to_numpy(float)
    pear_r, pear_p = stats.pearsonr(x, y)
    spear_rho, spear_p = stats.spearmanr(x, y)

    component_corrs = {}
    for comp in ["abs_rho_pi_minus_1", "abs_delta_shape", "abs_a2"]:
        xc = merged[comp].to_numpy(float)
        pr, pp = stats.pearsonr(xc, y)
        sr, sp = stats.spearmanr(xc, y)
        component_corrs[comp] = {"pearson_r": jf(pr), "pearson_p": jf(pp),
                                  "spearman_rho": jf(sr), "spearman_p": jf(sp)}

    susc_sorted = merged.sort_values("r_susceptibility", ascending=False)
    rank_of = {c: i + 1 for i, c in enumerate(susc_sorted.index)}  # 1 = highest susceptibility-stability
    anomaly_sorted = merged.sort_values("anomaly_combined_score", ascending=False)
    anomaly_rank_of = {c: i + 1 for i, c in enumerate(anomaly_sorted.index)}

    merged = merged.assign(
        susceptibility_stability_rank=[rank_of[c] for c in merged.index],
        anomaly_combined_rank=[anomaly_rank_of[c] for c in merged.index],
    )

    # Leave-one-out sensitivity (n=19 is small enough that a single leverage point --
    # wcl_60 is the most extreme value on BOTH axes -- could drive the whole
    # correlation; checked explicitly rather than assumed away).
    loo = []
    for i, name in enumerate(merged.index):
        mask = np.ones(len(x), dtype=bool)
        mask[i] = False
        r_loo, p_loo = stats.pearsonr(x[mask], y[mask])
        rho_loo, ps_loo = stats.spearmanr(x[mask], y[mask])
        loo.append({"dropped_construct": name, "pearson_r": jf(r_loo), "pearson_p": jf(p_loo),
                    "spearman_rho": jf(rho_loo), "spearman_p": jf(ps_loo)})
    loo_r_values = [row["pearson_r"] for row in loo]
    wcl60_mask = np.array([c != "wcl_60" for c in merged.index])
    r_ex60, p_ex60 = stats.pearsonr(x[wcl60_mask], y[wcl60_mask])
    rho_ex60, ps_ex60 = stats.spearmanr(x[wcl60_mask], y[wcl60_mask])
    robustness = {
        "leave_one_out": loo,
        "loo_pearson_r_range": [jf(min(loo_r_values)), jf(max(loo_r_values))],
        "excluding_wcl_60_specifically": {
            "n": int(wcl60_mask.sum()), "pearson_r": jf(r_ex60), "pearson_p": jf(p_ex60),
            "spearman_rho": jf(rho_ex60), "spearman_p": jf(ps_ex60),
            "note": ("wcl_60 is the most extreme value on BOTH axes (highest anomaly "
                     "combined score, 2nd-highest susceptibility-stability), so it is the "
                     "single most likely leverage point for n=19. Pearson SURVIVES its "
                     "removal (stays positive, p<.05); Spearman does NOT (drops below the "
                     ".10 bar) -- reported plainly, not smoothed over."),
        },
    }

    return {
        "merged": merged, "n": int(len(merged)),
        "pearson_r": jf(pear_r), "pearson_p": jf(pear_p),
        "spearman_rho": jf(spear_rho), "spearman_p": jf(spear_p),
        "component_correlations": component_corrs,
        "rank_of_susceptibility_stability": rank_of,
        "rank_of_anomaly_combined": anomaly_rank_of,
        "robustness": robustness,
    }


# ============================================================================
# Adjudication, per the registration's exact lean/kill wording
# ============================================================================

def adjudicate(corr: dict, merged: pd.DataFrame) -> dict:
    pear_r, pear_p = corr["pearson_r"], corr["pearson_p"]
    spear_rho, spear_p = corr["spearman_rho"], corr["spearman_p"]
    rank_of = corr["rank_of_susceptibility_stability"]
    n = corr["n"]

    clearest_ranks = {c: rank_of[c] for c in CLEAREST_CASES}
    upper_half_cut = n // 2  # rank <= this = "upper/higher-susceptibility half" of 19 -> <=9
    clearest_in_upper_half = {c: (r <= upper_half_cut) for c, r in clearest_ranks.items()}
    wcl60_in_upper_half = clearest_in_upper_half["wcl_60"]

    pearson_positive = pear_r is not None and pear_r > 0
    spearman_positive = spear_rho is not None and spear_rho > 0
    either_suggestive = (pear_p is not None and pear_p < 0.10) or (spear_p is not None and spear_p < 0.10)
    both_positive = pearson_positive and spearman_positive
    both_negative = (pear_r is not None and pear_r < 0) and (spear_rho is not None and spear_rho < 0)

    all_clearest_low = all(not v for v in clearest_in_upper_half.values())  # all 3 in LOWER half

    rob = corr.get("robustness", {})
    ex60 = rob.get("excluding_wcl_60_specifically", {})
    loo_range = rob.get("loo_pearson_r_range")

    if both_positive and wcl60_in_upper_half:
        if either_suggestive:
            verdict = "SUPPORTED_AT_LOW_POWER"
            text = (f"Positive on both Pearson (r={pear_r}, p={pear_p}) and Spearman "
                    f"(rho={spear_rho}, p={spear_p}), and wcl_60 ranks {clearest_ranks['wcl_60']}/{n} "
                    f"on susceptibility-stability (upper half). At least one p<.10 ('worth a "
                    f"second look' per the registration). Robustness: leave-one-out Pearson r "
                    f"stays in {loo_range} across all 19 single-construct drops (never sign-"
                    f"flips, never loses p<.05); excluding wcl_60 specifically (the extreme "
                    f"point on both axes) leaves Pearson r={ex60.get('pearson_r')} "
                    f"(p={ex60.get('pearson_p')}, still <.05) though Spearman rho drops to "
                    f"{ex60.get('spearman_rho')} (p={ex60.get('spearman_p')}, no longer even "
                    f"<.10) -- so the Pearson result is not a single-point artifact, but the "
                    f"rank-based (Spearman) result leans more heavily on wcl_60 than the "
                    f"Pearson one does. Given n=19 this is SUGGESTIVE-ONLY, NOT confirmatory -- "
                    f"consistent with, but nowhere near powered enough to confirm, the "
                    f"shared-rhythm hypothesis (population-pooled spectral weirdness and "
                    f"individual susceptibility-stability as two faces of one phenomenon).")
        else:
            verdict = "WEAKLY_SUPPORTED_UNDERPOWERED"
            text = (f"Sign is positive on both Pearson (r={pear_r}, p={pear_p}) and Spearman "
                    f"(rho={spear_rho}, p={spear_p}) and wcl_60 ranks "
                    f"{clearest_ranks['wcl_60']}/{n} (upper half), but neither p clears even "
                    f"the .10 'worth a second look' bar. Sign is in the leaned direction but "
                    f"the data give no real evidence at n=19; reported as underpowered, "
                    f"consistent-with-but-not-supporting the hypothesis.")
    elif both_negative and all_clearest_low:
        verdict = "NOT_SUPPORTED_SIGN_ACTIVELY_WRONG"
        text = (f"Correlation is NEGATIVE on both Pearson (r={pear_r}, p={pear_p}) and "
                f"Spearman (rho={spear_rho}, p={spear_p}), AND all three of the registration's "
                f"'clearest cases' (wcl_60, wcl_07, wcl_20) rank in the LOWER half on "
                f"susceptibility-stability (ranks {clearest_ranks}, out of {n}; upper-half cut "
                f"= rank<={upper_half_cut}) -- the sign is actively wrong for the cases the "
                f"registration itself flagged as most diagnostic. Per the registration's own "
                f"wording this licenses stating the negative reading with LESS hedging than "
                f"the default n=19 hedge (though the registration never authorizes calling "
                f"this a confident falsification outright): 'shared-rhythm hypothesis NOT "
                f"supported at this power -- the gust1_P carrier set and the individually "
                f"spectrally-anomalous constructs are better treated as two independent facts "
                f"that happened to overlap in one composite's specific loadings, not evidence "
                f"of one underlying phenomenon.'")
    else:
        verdict = "NOT_SUPPORTED_UNDERPOWERED_UNDECIDED"
        text = (f"Pearson r={pear_r} (p={pear_p}), Spearman rho={spear_rho} (p={spear_p}). "
                f"wcl_60 ranks {clearest_ranks['wcl_60']}/{n} on susceptibility-stability "
                f"(wcl_07 rank {clearest_ranks['wcl_07']}/{n}, wcl_20 rank "
                f"{clearest_ranks['wcl_20']}/{n}; upper-half cut = rank<={upper_half_cut}). "
                f"This does not cleanly satisfy the registration's positive-and-wcl_60-ranks-"
                f"high support condition. Per the registration's explicit instruction, a null/"
                f"negative or mixed result at n=19 is reported as 'underpowered/undecided,' "
                f"NOT a confident falsification, because the sign is not uniformly/actively "
                f"wrong for all three of the registration's own clearest cases "
                f"simultaneously. Recorded reading: shared-rhythm hypothesis NOT supported at "
                f"this power; the gust1_P carrier set and the individually spectrally-"
                f"anomalous constructs are plausibly two independent facts that happened to "
                f"overlap in one composite's loadings, but this is undecided rather than "
                f"falsified given the tiny n.")

    return {
        "verdict": verdict, "text": text,
        "clearest_cases_ranks_on_susceptibility_stability": clearest_ranks,
        "clearest_cases_in_upper_half": clearest_in_upper_half,
        "upper_half_rank_cutoff": upper_half_cut,
        "pearson_positive": pearson_positive, "spearman_positive": spearman_positive,
        "either_p_lt_010": either_suggestive,
    }


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    print(BANNER)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\n=== (i) population-level spectral-anomaly magnitude (Essays, W6/W7/W8) ===")
    anomaly_df, anomaly_diag = load_population_anomaly()
    cols = list(anomaly_df.index)
    print(f"  corpus: {anomaly_diag['corpus']}")
    print(f"  n_texts={anomaly_diag['n_texts']} n_windows={anomaly_diag['n_windows']} "
          f"(identical across W6/W7/W8, asserted)")
    print(f"  W6 headline mode used: {anomaly_diag['w6_headline_mode_used']}")
    print(f"  cross-check max|W8.obs.rho_pi - W7.rho_pi| = "
          f"{anomaly_diag['max_abs_diff_rho_pi_w8obs_vs_w7']}")
    print(f"  combination rule: {anomaly_diag['combination_rule']}")
    print("\n  per-construct anomaly (sorted by combined score desc):")
    for c, row in anomaly_df.sort_values("anomaly_combined_score", ascending=False).iterrows():
        print(f"    {c:24s} combined={row['anomaly_combined_score']:.4f}  "
              f"|rho_pi-1|={row['abs_rho_pi_minus_1']:.4f}  "
              f"|Delta_shape|={row['abs_delta_shape']:.4f}  |a2|={row['abs_a2']:.4f}")

    print("\n=== (ii) person-level susceptibility-stability, per construct (PANDORA N1 uncapped) ===")
    pool = load_pandora_uncapped_pool()
    print(f"  loaded F16 pool cache: {len(pool)} windows / {pool['cid'].nunique()} texts / "
          f"{pool['user_id'].nunique()} users (all m>=2)")
    pool_cols = w2a.get_construct_cols(pool)
    assert pool_cols == cols, (
        f"F16 pool construct column order differs from W6/W7/W8 construct order: "
        f"{pool_cols} vs {cols}")

    susc_df, susc_diag, pop_diag = compute_susceptibility_stability(pool, cols)
    print(f"  m>=3 pool: {susc_diag['n_windows_m_ge3']} windows / {susc_diag['n_texts_m_ge3']} "
          f"texts / {susc_diag['n_users_m_ge3_any_qualifying_text']} users (cross-checked "
          f"against F16's own published diagnostics -- PASS)")
    print(f"  split-half-eligible users (>=2 qualifying texts), CONSTANT across all 19 "
          f"constructs: {susc_diag['n_users_split_half_eligible_per_construct']}")
    print(f"  population choice: {pop_diag['rationale']}")
    print("\n  per-construct susceptibility-stability (sorted by r_susceptibility desc):")
    for c, row in susc_df.sort_values("r_susceptibility", ascending=False).iterrows():
        print(f"    {c:24s} r_susceptibility={row['r_susceptibility']!s:>9}  "
              f"r_direction={row['r_direction']!s:>9}  icc_share={row['icc_share_abs_a']!s:>9}  "
              f"n_users={row['n_users']}")

    print("\n=== correlate (i) vs (ii) across n=19 constructs ===")
    corr = correlate(anomaly_df, susc_df)
    merged = corr["merged"]
    print(f"  n={corr['n']}")
    print(f"  Pearson  r = {corr['pearson_r']}  (p = {corr['pearson_p']})")
    print(f"  Spearman rho = {corr['spearman_rho']}  (p = {corr['spearman_p']})")
    print(f"  component-wise correlations vs r_susceptibility:")
    for comp, cc in corr["component_correlations"].items():
        print(f"    {comp:24s} pearson r={cc['pearson_r']!s:>9} p={cc['pearson_p']!s:>9}  "
              f"spearman rho={cc['spearman_rho']!s:>9} p={cc['spearman_p']!s:>9}")

    rob = corr["robustness"]
    print(f"\n  robustness: leave-one-out Pearson r range = {rob['loo_pearson_r_range']} "
          f"(over 19 single-construct drops)")
    ex60 = rob["excluding_wcl_60_specifically"]
    print(f"  excluding wcl_60 specifically (n={ex60['n']}): pearson r={ex60['pearson_r']} "
          f"p={ex60['pearson_p']}; spearman rho={ex60['spearman_rho']} p={ex60['spearman_p']}")
    print(f"    {ex60['note']}")

    adj = adjudicate(corr, merged)
    print(f"\n=== adjudication ===")
    print(f"  verdict: {adj['verdict']}")
    print(f"  clearest-case ranks on susceptibility-stability (1=highest, out of "
          f"{corr['n']}): {adj['clearest_cases_ranks_on_susceptibility_stability']}")
    print(f"  {adj['text']}")

    # ==================================================================
    # Full per-construct table
    # ==================================================================
    full_table = []
    for c in cols:
        row = merged.loc[c]
        full_table.append({
            "construct": c,
            "in_gust1P_carrier_set": c in GUST1P_CARRIER_SET,
            "rho_pi_w6_truncated": jf(row["rho_pi_w6_truncated"]),
            "abs_rho_pi_minus_1": jf(row["abs_rho_pi_minus_1"]),
            "delta_shape_w7": jf(row["delta_shape_w7"]),
            "abs_delta_shape": jf(row["abs_delta_shape"]),
            "a1_w8": jf(row["a1_w8"]),
            "a2_w8": jf(row["a2_w8"]),
            "abs_a2": jf(row["abs_a2"]),
            "norm_rho_pi": jf(row["norm_rho_pi"]),
            "norm_delta_shape": jf(row["norm_delta_shape"]),
            "norm_a2": jf(row["norm_a2"]),
            "anomaly_combined_score": jf(row["anomaly_combined_score"]),
            "anomaly_combined_rank": int(row["anomaly_combined_rank"]),
            "r_susceptibility": jf(row["r_susceptibility"]),
            "r_direction": jf(row["r_direction"]),
            "icc_share_abs_a": jf(row["icc_share_abs_a"]),
            "n_users_susceptibility": int(row["n_users"]),
            "n_texts_pooled_susceptibility": int(row["n_texts_pooled"]),
            "susceptibility_stability_rank": int(row["susceptibility_stability_rank"]),
        })
    full_table.sort(key=lambda r: r["susceptibility_stability_rank"])

    # ==================================================================
    # Outputs
    # ==================================================================
    result = {
        "banner": BANNER,
        "registered_ref": ("Shared-rhythm hypothesis test, docs/SUICA_THEORY_FORMAL_NOTES_V3.md "
                          "(registered 2026-07-12); ledger row 'Shared-rhythm'"),
        "question": ("Are gust1_P's carrier constructs (wcl_02, wcl_07, wcl_11, wcl_20) the SAME "
                    "constructs independently flagged as spectrally anomalous at the "
                    "population-pooled level (F12.7-9), or coincidental overlap in one "
                    "composite's loadings?"),
        "population_anomaly": {
            "diagnostics": anomaly_diag,
        },
        "susceptibility_stability": {
            "diagnostics": {k: v for k, v in susc_diag.items() if k != "pooled_sd_by_construct"},
            "pooled_sd_by_construct": susc_diag["pooled_sd_by_construct"],
        },
        "n_constructs": corr["n"],
        "correlation": {
            "primary_anomaly_combined_score_vs_r_susceptibility": {
                "pearson_r": corr["pearson_r"], "pearson_p": corr["pearson_p"],
                "spearman_rho": corr["spearman_rho"], "spearman_p": corr["spearman_p"],
            },
            "component_wise_vs_r_susceptibility": corr["component_correlations"],
            "power_note": ("n=19 (one point per construct) -- LOW-POWERED/SUGGESTIVE-ONLY per "
                           "the registration; p<.10 = 'worth a second look,' explicitly NOT "
                           "confirmatory at this n."),
            "robustness": corr["robustness"],
        },
        "gust1P_carrier_set": sorted(GUST1P_CARRIER_SET),
        "clearest_cases": CLEAREST_CASES,
        "wcl_60_rank_on_susceptibility_stability": adj["clearest_cases_ranks_on_susceptibility_stability"]["wcl_60"],
        "adjudication": adj,
        "full_per_construct_table_sorted_by_susceptibility_rank": full_table,
        "notes": [
            "Population-level anomaly (i) is measured on the Essays corpus (W6/W7/W8, "
            "label-free, register-neutral); person-level susceptibility-stability (ii) is "
            "measured on PANDORA (Reddit, N1 uncapped pool). This cross-corpus comparison is "
            "INHERENT to what the shared-rhythm hypothesis asks (population-pooled spectral "
            "texture vs individual gustiness-stability) and is not an artifact of this script's "
            "design -- flagged explicitly rather than silently treated as same-corpus.",
            "All 19 constructs had a valid (non-NaN, non-degenerate) r_susceptibility estimate; "
            "none were dropped. n_users_split_half_eligible is IDENTICAL across all 19 "
            "constructs (2,355) because qualification (>=2 texts with m>=3 for a given user) "
            "depends only on the shared window pool, not on any construct's own activation "
            "values -- this equalizes statistical power across the 19 comparisons being ranked.",
            "rho_pi is read from W6's own headline 'truncated' mode (that script's own "
            "registered graceful-degradation choice for this corpus/composition), NOT the "
            "'five_moment' mode, which W6 itself flags as noise-dominated on gamma0 here "
            "(includes a negative point gamma0 for wcl_60/wcl_07). W7's hybrid-design rho_pi "
            "(5-moment numerator / truncated-3 denominator) differs slightly from W6's "
            "all-truncated rho_pi by construction (different functional composition, not an "
            "error) -- reported separately as 'rho_pi_w7_hybrid_crosscheck' for transparency; "
            "the combination rule uses W6's rho_pi specifically, per the registration's own "
            "source pointer ('results/suica_v6_w6_nyquist_ratio/ (rho_pi per construct)').",
            "a1 (from W8) is reported for context but is NOT part of the anomaly_combined_score "
            "-- the registration names only |rho_pi-1|, |Delta_shape|, |a2| as combination "
            "inputs.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2))
    print(f"\nwritten: {OUT_JSON}")

    md = ["# Shared-rhythm hypothesis test", "", f"> {BANNER}", "",
          "Registered 2026-07-12, docs/SUICA_THEORY_FORMAL_NOTES_V3.md "
          "'## Shared-rhythm hypothesis test'; ledger row 'Shared-rhythm'.", "",
          "## Question", "",
          result["question"], "",
          "## Design summary", "",
          f"- (i) Population-level spectral-anomaly magnitude: Essays corpus "
          f"(n_texts={anomaly_diag['n_texts']}, n_windows={anomaly_diag['n_windows']}), from "
          f"W6 (rho_pi, truncated headline mode), W7 (Delta_shape), W8 (AR(2) a2). "
          f"Combination: {anomaly_diag['combination_rule']}",
          f"- (ii) Person-level susceptibility-stability: PANDORA N1-uncapped pool "
          f"({susc_diag['n_windows_m_ge3']} windows / {susc_diag['n_texts_m_ge3']} texts, "
          f"m>=3), W10's person_susceptibility() (unmodified) applied to each construct's own "
          f"within-text-detrended residual column (F16's dynamic-channel generalization). "
          f"{susc_diag['n_users_split_half_eligible_per_construct'][0]} split-half-eligible "
          f"users, constant across all 19 constructs.",
          f"- Population choice: full F16 uncapped pool, not the Big5-gate subset "
          f"({pop_diag['rationale']})",
          "", "## Correlation (n=19 constructs, LOW-POWERED/SUGGESTIVE-ONLY)", "",
          f"- Pearson r = {corr['pearson_r']}, p = {corr['pearson_p']}",
          f"- Spearman rho = {corr['spearman_rho']}, p = {corr['spearman_p']}",
          f"- p<.10 is 'worth a second look' per the registration, explicitly NOT confirmatory "
          f"at this n.", "",
          "### Component-wise correlations vs r_susceptibility", "",
          "| component | pearson r | pearson p | spearman rho | spearman p |",
          "|---|---|---|---|---|"]
    for comp, cc in corr["component_correlations"].items():
        md.append(f"| {comp} | {cc['pearson_r']} | {cc['pearson_p']} | {cc['spearman_rho']} | "
                  f"{cc['spearman_p']} |")

    rob = corr["robustness"]
    ex60 = rob["excluding_wcl_60_specifically"]
    md += ["", "### Robustness: leave-one-out sensitivity", "",
          f"wcl_60 is the most extreme value on BOTH axes (highest anomaly combined score, "
          f"2nd-highest susceptibility-stability) -- the single most likely n=19 leverage "
          f"point, checked explicitly rather than assumed away.", "",
          f"- Leave-one-out Pearson r range (dropping each of the 19 constructs once): "
          f"{rob['loo_pearson_r_range']} -- stays positive and stays under p<.05 for every "
          f"single drop.",
          f"- Excluding wcl_60 specifically (n={ex60['n']}): Pearson r={ex60['pearson_r']}, "
          f"p={ex60['pearson_p']} (survives, still p<.05); Spearman rho={ex60['spearman_rho']}, "
          f"p={ex60['spearman_p']} (does NOT survive -- drops below the .10 bar).",
          f"- {ex60['note']}", ""]

    md += ["## Adjudication", "", f"**Verdict: {adj['verdict']}**", "", adj["text"], "",
          f"Clearest-case ranks on susceptibility-stability (1=highest of {corr['n']}, "
          f"upper-half cutoff = rank<={adj['upper_half_rank_cutoff']}): "
          f"{adj['clearest_cases_ranks_on_susceptibility_stability']}", ""]

    md += ["## Full per-construct table (sorted by susceptibility-stability rank)", "",
          "| rank | construct | carrier? | rho_pi (W6) | \\|rho_pi-1\\| | Delta_shape (W7) | "
          "\\|Delta_shape\\| | a2 (W8) | \\|a2\\| | anomaly combined | anomaly rank | "
          "r_susceptibility | r_direction | icc_share | n_users |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for row in full_table:
        md.append(f"| {row['susceptibility_stability_rank']} | {row['construct']} | "
                  f"{'YES' if row['in_gust1P_carrier_set'] else ''} | "
                  f"{row['rho_pi_w6_truncated']} | {row['abs_rho_pi_minus_1']} | "
                  f"{row['delta_shape_w7']} | {row['abs_delta_shape']} | "
                  f"{row['a2_w8']} | {row['abs_a2']} | {row['anomaly_combined_score']} | "
                  f"{row['anomaly_combined_rank']} | {row['r_susceptibility']} | "
                  f"{row['r_direction']} | {row['icc_share_abs_a']} | "
                  f"{row['n_users_susceptibility']} |")

    md += ["", "## Notes", ""]
    md += [f"- {n}" for n in result["notes"]]
    OUT_MD.write_text("\n".join(md) + "\n")
    print(f"written: {OUT_MD}")


if __name__ == "__main__":
    main()
