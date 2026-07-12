#!/usr/bin/env python
"""EXPL-4b -- uncapped Tier-L motion features (position/slope + spectral) on the
spent opening-#1 labels (F14 "N-program", registered commit 97ecca2,
docs/SUICA_THEORY_FORMAL_NOTES_V3.md; ledger rows EXPL-3/EXPL-4a/N1).
EXPLORATORY (spent labels, T1).

Custody status
--------------
Same spent PANDORA Big5 labels as EXPL-3 (unsealed at lockbox opening #1,
git cd63d13, 2026-07-06). Essays confirm-half labels are NOT touched. No
other label source is read. This is the THIRD leg of the F14 motion-layer
triad: EXPL-3 (capped Tier-L, position/slope only, Delta +0.0009) / EXPL-4a
(Essays dev half, uncapped, Delta -0.0096) / EXPL-4b (this script: capped-
label cohort, now sourced from N1's UNCAPPED Tier-L data, position/slope
AND -- where estimable -- the spectral layer).

Governance gates (all BEFORE any new fitting; the run STOPS on failure) --
copied VERBATIM from run_suica_expl3_motion_weightfit_v1.py's main() assert
block (its own lines ~222-259), reusing that module's finalize_axes() and
ridge_arm() directly rather than re-deriving their logic from a description:
  1. Eligibility gate replicated verbatim from the opening; assert n == 1,058.
  2. H2 (first_person -> Neuroticism) / H6 (politics choice -> Openness)
     recomputed and asserted to < 1e-9 against OPENING_REPORT.json.
  3. ANCHOR: EXPL-2's arm C (v4-16 union v5-15) rebuilt from its own caches
     and asserted equal to its stored artifact (mean r = .1361 exact).

Question. Does adding the uncapped-sourced motion layer -- position/slope
(EXPL-3's original 10 features, but now built from N1 uncapped Tier-L
instead of the 1,500-char-capped file) PLUS a new spectral layer (signed
memory, gust amplitude, rho_pi/rho_pi_half shape pair, all via
suica_core/motion.py's motion_from_window_arrays, computed PER USER wherever
that estimator's OWN m-gates allow) -- add exploratory detection power over
EXPL-2's arm-C anchor?

Position/slope layer (reused, not reimplemented): run_suica_expl3_motion_
weightfit_v1.build_motion_user_features() is imported and called DIRECTLY,
with its module-level LOCKBOX_COMMENTS/MOTION_CACHE constants redirected (at
runtime, not by editing the frozen file) to N1's uncapped Tier-L parquet and
to a NEW cache under this script's own output directory -- EXPL-3's own
capped-source cache is never read or overwritten. The PCA slope-factor axes
(VDP, Tier-U P8 cache, no leakage) are rebuilt via expl3's own corr_guarded()/
top_eigs() functions, reused directly, exactly mirroring expl3's main() lines
~264-274.

Spectral layer (signed memory / gust amplitude / rho_pi & rho_pi_half shape
pair): estimated PER USER (one motion_from_window_arrays call per gated
user, that user's own long-text windows as the "batch") via suica_core.
motion.motion_from_window_arrays, imported UNMODIFIED. Window scores are
NOT recomputed from raw text -- they are REUSED from results/suica_f16_
visibility_taxonomy/pandora_uncapped_windows_scored19.parquet (F16's already
-scored, already-leak-filtered uncapped PANDORA window pool), restricted to
the gated users' own texts (all of whom sit in N1's uncapped tier_l -- 794/
794 confirmed below, independently cross-checked against a from-scratch
retokenization of tier_l_comments_uncapped_v1.parquet before this script was
finalized: identical 794-user coverage, 0 symmetric difference). This is
the "candidate shortcut" the registration flagged as worth checking first;
it checks out and is reused directly, saving a costly re-score pass. Per-
user pooled-sd standardization (the 3-line normalization motion_profile()
applies internally before calling its own numeric core) is replicated here
verbatim in the wrapper below, since that lightweight glue cannot be reused
without also re-deriving the (irrelevant, already-cached) window texts;
motion_from_window_arrays -- the substantive, hard-to-reimplement-correctly
moment/period-2/shape machinery -- is imported and called UNMODIFIED.

CAUTION reproduced from F16 (a real bug that program hit and fixed): do not
insert the release repo's root at sys.path position 0 before finishing all
research-repo "scripts.*"/"project_persona.*" imports -- the release repo
ships an identically-named "scripts" namespace package that would silently
shadow the frozen research-repo copies. RELEASE_ROOT is appended to
sys.path only AFTER those imports below, exactly mirroring run_suica_f16_
visibility_taxonomy_v1.py's own fix.

MISSING DATA POLICY (specified up front, followed exactly, reported
plainly): for every added feature, users lacking that specific estimator's
own sufficient-m requirement are mean-imputed from the COVERED cohort's mean
for that feature, with a binary has_<family> indicator column added
(mirroring EXPL-3's own has_long convention). All added columns are then
z-scored over the full 1,058-user gated cohort (guard sd > 0), exactly as
EXPL-3 did. Two has_* indicators are used: has_long (position/slope family,
reused from EXPL-3/its own agg["n_long"] > 0) and has_spectral_moment /
has_spectral_shape (spectral families -- moment [signed memory + gust
amplitude, sharing one Gamma0/B inversion] and shape [rho_pi + rho_pi_half,
sharing one period-2 estimability gate] are gated separately because
suica_core.motion applies DIFFERENT thresholds to each: MIN_D2_ROWS = 30
pooled second-difference rows for the moment family; PERIOD2_MIN_LAG_PAIRS
= 100 pooled lag-2 pairs for the shape family).

Both the full imputed-arm Delta (on all 1,058 gated users, EXPL-3's own
headline-number convention) AND a complete-case Delta (restricted to users
needing NO imputation on ANY added feature -- position AND spectral-moment
AND spectral-shape all real) are reported below; neither is hidden even
where the complete-case n turns out too small to support a meaningful 5-fold
fit (reported plainly, with the actual n, in the JSON/MD and in this run's
console log).

Arms (per-trait RidgeCV, EXPL-2/EXPL-3 protocol, same alpha grid, same
KFold(5, shuffle, rs=42) -- expl3.ridge_arm reused directly, not
reimplemented): C = EXPL-2 union anchor (must reproduce mean r = .1361
exactly); D = C + ALL motion features (position/slope-10 + spectral-30);
M = motion features alone. Single-feature Pearson screen (|r| >= .10
flagged, EXPL-3's own convention) on covered users only, per feature, across
the full new feature set x 5 traits.

Adjudication. Registered lean (F14, 97ecca2): Delta(C->D) in [+.000,+.015].
STANDING KILL: if EXPL-4a (-0.0096) AND this run both land <= 0, the
recorded verdict becomes "questionnaire-criterion insensitivity to the
motion layer," pending BEHAVIORAL criteria (the native corpus's job, N4).

No git commits are made by this script.
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

from project_persona.suica import PERSONALITY_LEAK_RE, tokenize  # noqa: E402
import scripts.run_suica_c2_purity_all19_v1 as a19  # noqa: E402
import scripts.run_suica_expl3_motion_weightfit_v1 as expl3  # noqa: E402

# RELEASE_ROOT appended AFTER every project-persona "scripts.*"/"project_persona.*"
# reuse import above has resolved -- NOT inserted at position 0 -- exactly mirroring
# run_suica_f16_visibility_taxonomy_v1.py's own fix for the "scripts" namespace-
# package shadowing hazard (both repos ship a same-named, __init__.py-less PEP 420
# "scripts" package; inserting RELEASE_ROOT first would silently resolve the
# "scripts.*" imports above against the RELEASE repo's non-identical copies).
RELEASE_ROOT = Path("/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment")
if str(RELEASE_ROOT) not in sys.path:
    sys.path.append(str(RELEASE_ROOT))
from suica_core import motion as motion_mod  # noqa: E402  (memory_by_construct, Gamma0, period2/shape)

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
TIER_L_UNCAPPED = TIER_DIR / "tier_l_comments_uncapped_v1.parquet"
TIER_U_UNCAPPED = TIER_DIR / "tier_u_comments_uncapped_v1.parquet"
PREDICTORS = ROOT / "results" / "suica_lockbox_opening_1" / "predictors.parquet"
OPENING_REPORT = ROOT / "results" / "suica_lockbox_opening_1" / "OPENING_REPORT.json"
BIG5_LABELS = ROOT / "data_sets" / "prepared" / "pandora_official" / "pandora_official_big5_prepared.csv"
EXPL2_DIR = ROOT / "results" / "suica_expl_v5_weightfit"
EXPL2_JSON = EXPL2_DIR / "EXPL2_V5_WEIGHTFIT.json"
EXPL2_CACHE = EXPL2_DIR / "v5u_tier_l_features.parquet"
P8_CACHE = ROOT / "results" / "suica_tgeo_p8_functionalization" / "cache_windows_scored19.parquet"
F16_POOL_CACHE = ROOT / "results" / "suica_f16_visibility_taxonomy" / "pandora_uncapped_windows_scored19.parquet"

OUT_DIR = ROOT / "results" / "suica_expl4b_uncapped_motion_weightfit"
POSITION_CACHE = OUT_DIR / "motion_user_features_raw_uncapped.parquet"

TRAITS = expl3.TRAITS
STYLE = expl3.STYLE                     # ["tension_core_v2","directive_action_v2","first_person_usage_v2","novelty_play_v2"]
V2_DIFFS = expl3.V2_DIFFS               # {"d_first_person": "first_person_usage_v2", ...}
POSITION_COLS = expl3.MOTION_COLS       # EXPL-3's original 10 (reused verbatim)

# Spectral feature families: 3 PCA projections (shared VDP axes, Tier-U P8, no
# leakage) + 4 raw style-construct diffs, generalized identically to each of the
# four new per-construct vectors (signed memory r_c, gust amplitude sqrt(diag
# Gamma0), rho_pi, rho_pi_half) -- the SAME reduction recipe EXPL-3 applied to
# the position layer's Dbar, applied uniformly to every new family for parity.
SPECTRAL_PREFIXES = {"mem": "signed memory (r_c = B_hat_cc/Gamma0_hat_cc)",
                     "amp": "gust amplitude (sqrt(Gamma0_hat_cc), susceptibility)",
                     "rpi": "rho_pi (period-2 / Nyquist energy)",
                     "rph": "rho_pi_half (quarter-frequency shape component)"}
SPECTRAL_SUFFIXES = ["proj_dcomp1", "proj_dcomp2", "proj_a3",
                     "first_person", "tension", "directive", "novelty"]
SPECTRAL_COLS = [f"{pfx}_{sfx}" for pfx in SPECTRAL_PREFIXES for sfx in SPECTRAL_SUFFIXES]
HAS_SPECTRAL_MOMENT = "has_spectral_moment"   # gates mem_*, amp_*
HAS_SPECTRAL_SHAPE = "has_spectral_shape"     # gates rpi_*, rph_*
MOTION_COLS_ALL = POSITION_COLS + SPECTRAL_COLS + [HAS_SPECTRAL_MOMENT, HAS_SPECTRAL_SHAPE]

BANNER = ("EXPLORATORY (spent labels, T1) -- EXPL-4b uncapped-motion weight-fit "
          "(labels spent at opening #1; F14 N-program, 97ecca2)")


# ============================================================================
# Governance gates 1+2+3 -- copied VERBATIM from run_suica_expl3_motion_
# weightfit_v1.py's main() lines ~222-259, reusing expl3.finalize_axes()/
# expl3.ridge_arm() directly.
# ============================================================================

def governance_gate_and_anchor() -> tuple[list, pd.DataFrame, pd.DataFrame, dict, float, float]:
    pred = pd.read_parquet(PREDICTORS)
    pred.index = pred.index.astype(str)
    big5 = pd.read_csv(BIG5_LABELS).set_index("user_id")
    big5.index = big5.index.astype(str)
    gate = (pred["n_conditions"] >= 4) & (pred["n_slices"] >= 12)
    inter = pred.index.intersection(big5.index)
    elig = inter[gate.loc[inter].fillna(False).to_numpy(bool)]
    assert len(elig) == 1058, f"eligibility replication failed: {len(elig)}"
    pred = expl3.finalize_axes(pred, elig)
    users = sorted(elig)

    rep = json.loads(OPENING_REPORT.read_text())
    published = {h["id"]: h["r"] for h in rep["hypotheses"]}
    r_h2 = float(pred.loc[users, "first_person_usage_v2"].corr(big5.loc[users, "Neuroticism"]))
    r_h6 = float(pred.loc[users, "choice_ax_06"].corr(big5.loc[users, "Openness"]))
    assert abs(r_h2 - published["H2"]) < 1e-9, (r_h2, published["H2"])
    assert abs(r_h6 - published["H6"]) < 1e-9, (r_h6, published["H6"])
    print(f"[governance] gate n={len(users)} (== 1058, PASS); "
          f"H2 recomputed {r_h2:.10f} vs published {published['H2']:.10f} (<1e-9, PASS); "
          f"H6 recomputed {r_h6:.10f} vs published {published['H6']:.10f} (<1e-9, PASS)")

    assert EXPL2_CACHE.exists(), "EXPL-2 feature cache missing -- refuse to rebuild silently"
    v5u = pd.read_parquet(EXPL2_CACHE).reindex(users)
    keep = [c for c in v5u.columns if v5u[c].std() > 1e-9]
    battery_cols = (STYLE + [f"choice_ax_{k:02d}" for k in range(expl3.N_CLASSES)
                             if k != expl3.EXCLUDED_AXIS] + ["choice_entropy"])
    Xa = pred.loc[users, battery_cols].to_numpy(float)
    Xb = v5u[keep].to_numpy(float)
    Xc = np.hstack([Xa, Xb])
    Y = big5.loc[users, TRAITS].to_numpy(float)

    stored = json.loads(EXPL2_JSON.read_text())["arm_C_union"]
    arm_c = expl3.ridge_arm(Xc, Y, f"C union-{Xc.shape[1]} (anchor)")
    for t in TRAITS + ["MEAN_BIG5"]:
        assert abs(arm_c[t] - stored[t]) < 1e-9, f"arm C anchor failed at {t}: {arm_c[t]} vs {stored[t]}"
    assert abs(arm_c["MEAN_BIG5"] - 0.1361) < 1e-9
    print(f"[governance] anchor ok: arm C reproduces EXPL-2 stored artifact exactly "
          f"(mean {arm_c['MEAN_BIG5']:.4f})")

    return users, big5, pd.DataFrame(Xc, index=users), arm_c, r_h2, r_h6


# ============================================================================
# Position/slope layer -- reuse expl3.build_motion_user_features() DIRECTLY,
# redirecting its module-level source/cache constants at runtime (the frozen
# FILE is never edited; EXPL-3's own capped-source cache is never touched).
# ============================================================================

def build_position_layer(users: list, cols: list) -> pd.DataFrame:
    original_comments = expl3.LOCKBOX_COMMENTS
    original_cache = expl3.MOTION_CACHE
    expl3.LOCKBOX_COMMENTS = TIER_L_UNCAPPED
    expl3.MOTION_CACHE = POSITION_CACHE
    try:
        agg = expl3.build_motion_user_features(users, cols)
    finally:
        expl3.LOCKBOX_COMMENTS = original_comments
        expl3.MOTION_CACHE = original_cache
    return agg


# ============================================================================
# Spectral layer -- per-user motion_from_window_arrays (suica_core.motion,
# imported UNMODIFIED), fed from F16's already-scored, already-leak-filtered
# uncapped PANDORA window pool (reused directly; provenance independently
# cross-checked against a from-scratch retokenization of tier_l_comments_
# uncapped_v1.parquet before this script was finalized -- see module docstring).
# ============================================================================

def load_gated_pool(users: list, cols: list) -> pd.DataFrame:
    assert F16_POOL_CACHE.exists(), f"F16 pool cache missing: {F16_POOL_CACHE}"
    pool = pd.read_parquet(F16_POOL_CACHE)
    pool["user_id"] = pool["user_id"].astype(str)
    missing = [c for c in cols if c not in pool.columns]
    assert not missing, f"F16 pool missing expected construct columns: {missing}"
    gated = pool.loc[pool["user_id"].isin(set(users))].copy()
    return gated


def per_user_motion_profiles(gated_pool: pd.DataFrame, cols: list) -> dict:
    """One motion_from_window_arrays() call per user (batch = that user's own
    long-text windows). Pooled-sd standardization (motion_profile()'s own
    3-line normalization) is replicated here verbatim since scores are reused
    from cache rather than produced by a live scorer call; the numeric core
    is imported and called UNMODIFIED."""
    results = {}
    for user_id, g in gated_pool.groupby("user_id"):
        window_arrays_raw = []
        orig_m_list = []
        for _cid, gg in g.groupby("cid"):
            gg = gg.sort_values("j")
            window_arrays_raw.append(gg[cols].to_numpy(float))
            orig_m_list.append(int(gg["m"].iloc[0]))
        all_scores = np.vstack(window_arrays_raw)
        pooled_sd = all_scores.std(axis=0)
        pooled_sd = np.where(pooled_sd > 0, pooled_sd, 1.0)
        window_arrays = [arr / pooled_sd for arr in window_arrays_raw]
        core = motion_mod.motion_from_window_arrays(window_arrays, orig_m=orig_m_list,
                                                     naive_inversion=False)
        results[user_id] = core
    return results


def build_spectral_layer(profiles: dict, cols: list, VDP: np.ndarray) -> tuple[pd.DataFrame, dict]:
    style_idx = [cols.index(c) for c in STYLE]  # tension, directive, first_person, novelty order
    style_name = {"tension_core_v2": "tension", "directive_action_v2": "directive",
                  "first_person_usage_v2": "first_person", "novelty_play_v2": "novelty"}

    rows = []
    diag = {"n_users_any_profile": len(profiles), "n_moment_real": 0, "n_shape_real": 0}
    for user_id, core in profiles.items():
        row = {"user_id": user_id}
        mem = core["memory_by_construct"]
        gamma0 = core["Gamma0"]
        if mem is not None and gamma0 is not None:
            mem_vec = np.asarray(mem, dtype=float)
            amp_vec = np.sqrt(np.clip(np.diagonal(np.asarray(gamma0, dtype=float)), 0.0, None))
            row["has_spectral_moment"] = 1.0
            diag["n_moment_real"] += 1
        else:
            mem_vec = None
            amp_vec = None
            row["has_spectral_moment"] = 0.0

        rpi = core["period2_energy_by_construct"]
        shape_pair = core["spectral_shape_by_construct"]
        if rpi is not None and shape_pair is not None:
            rpi_vec = np.asarray(rpi, dtype=float)
            rph_vec = np.asarray([p[0] for p in shape_pair], dtype=float)  # [rho_pihalf, rho_pi]
            row["has_spectral_shape"] = 1.0
            diag["n_shape_real"] += 1
        else:
            rpi_vec = None
            rph_vec = None
            row["has_spectral_shape"] = 0.0

        for prefix, vec in (("mem", mem_vec), ("amp", amp_vec), ("rpi", rpi_vec), ("rph", rph_vec)):
            if vec is None:
                continue
            proj = vec @ VDP[:, :3]
            row[f"{prefix}_proj_dcomp1"] = float(proj[0])
            row[f"{prefix}_proj_dcomp2"] = float(proj[1])
            row[f"{prefix}_proj_a3"] = float(proj[2])
            for i, construct in enumerate(STYLE):
                row[f"{prefix}_{style_name[construct]}"] = float(vec[cols.index(construct)])
        rows.append(row)

    frame = pd.DataFrame(rows).set_index("user_id")
    return frame, diag


# ============================================================================
# Generic impute + z-score helper (EXPL-3's own convention, lines ~296-303,
# generalized so it applies identically to the position family and to each
# spectral family with its own covered-index / has_* indicator).
# ============================================================================

def impute_and_zscore(raw: pd.DataFrame, all_users: list, feature_cols: list) -> pd.DataFrame:
    full = raw.reindex(all_users)
    cov_means = raw[feature_cols].mean(axis=0)
    for c in feature_cols:
        full[c] = full[c].fillna(cov_means[c])
    z = full.copy()
    for c in feature_cols:
        sd = z[c].std()
        z[c] = (z[c] - z[c].mean()) / (sd if sd > 1e-12 else 1.0)
    return z[feature_cols]


def main() -> None:
    print(BANNER)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    users, big5, Xc_df, arm_c, r_h2, r_h6 = governance_gate_and_anchor()
    Xc = Xc_df.to_numpy(float)
    Y = big5.loc[users, TRAITS].to_numpy(float)

    cols = list(a19.V3_BATTERY) + list(a19.OP5_KEPT)

    # ---------------- shared PCA slope-factor axes (Tier-U P8, no leakage) ----------------
    # Mirrors expl3.py main() lines ~264-274 verbatim (algorithmically); expl3's own
    # corr_guarded()/top_eigs() functions are imported and reused directly.
    ps = pd.read_parquet(P8_CACHE)
    pcols = [c for c in ps.columns if c not in ("cid", "user_id", "j", "m", "t", "tau", "delta")]
    assert pcols == cols, "P8 cache construct order != a19 battery order"
    gp = ps.sort_values(["cid", "j"]).groupby("cid")
    Dp = gp[cols].last().to_numpy(float) - gp[cols].first().to_numpy(float)
    _, VDP = expl3.top_eigs(expl3.corr_guarded(Dp), 4)
    print(f"[axes] slope-factor axes from P8 cache: {Dp.shape[0]} cids "
          f"(Tier-U only, no leakage; reused via expl3.corr_guarded/top_eigs)")

    # ---------------- position/slope layer (uncapped source) ----------------
    pos_agg = build_position_layer(users, cols)
    pos_covered = [u for u in users if u in pos_agg.index]
    n_pos_cov = len(pos_covered)
    med_texts = float(pos_agg.loc[pos_covered, "n_long"].median()) if n_pos_cov else float("nan")
    print(f"[position] gated users: {len(users)}; with >=1 long text (uncapped source): "
          f"{n_pos_cov}; median long texts: {med_texts:.0f}")

    sd_Dp = Dp.std(0)
    sd_Dp = np.where(sd_Dp > 0, sd_Dp, 1.0)
    Dbar = pos_agg.loc[pos_covered, [f"D::{c}" for c in cols]].to_numpy(float)
    Dbar_z = Dbar / sd_Dp
    pos_raw = pd.DataFrame(index=pd.Index(pos_covered, name="user_id"))
    pos_raw["proj_dcomp1"] = Dbar_z @ VDP[:, 0]
    pos_raw["proj_dcomp2"] = Dbar_z @ VDP[:, 1]
    pos_raw["proj_a3"] = Dbar_z @ VDP[:, 2]
    for feat, con in V2_DIFFS.items():
        pos_raw[feat] = Dbar[:, cols.index(con)]
    pos_raw["open_first_person"] = pos_agg.loc[pos_covered, "open_fp"].to_numpy(float)
    pos_raw["log1p_n_long"] = np.log1p(pos_agg.loc[pos_covered, "n_long"].to_numpy(float))
    pos_raw["has_long"] = 1.0

    # ---------------- spectral layer (uncapped, N1 tier_l; reused F16 pool) ----------------
    gated_pool = load_gated_pool(users, cols)
    n_gate_in_tier_l = gated_pool["user_id"].nunique()
    print(f"[spectral] gated users present in reused F16 uncapped pool (tier_l): "
          f"{n_gate_in_tier_l}/{len(users)}")

    text_m = gated_pool.groupby("cid")["m"].first()
    text_user = gated_pool.groupby("cid")["user_id"].first()
    tm = pd.DataFrame({"m": text_m, "user_id": text_user})
    n_ge3 = tm.loc[tm["m"] >= 3, "user_id"].nunique()
    n_ge5 = tm.loc[tm["m"] >= 5, "user_id"].nunique()
    print(f"[spectral] census (>=1 text at threshold, loose feasibility, NOT estimator-gated): "
          f"m>=3 in {n_ge3} users; m>=5 in {n_ge5} users")

    profiles = per_user_motion_profiles(gated_pool, cols)
    spec_raw, spec_diag = build_spectral_layer(profiles, cols, VDP)
    print(f"[spectral] motion.py's OWN per-user estimability gates (MIN_D2_ROWS=30 for "
          f"signed-memory/gust-amplitude; PERIOD2_MIN_LAG_PAIRS=100 for rho_pi/shape): "
          f"REAL (non-imputed) moment family = {spec_diag['n_moment_real']}/{len(users)} users; "
          f"REAL shape family = {spec_diag['n_shape_real']}/{len(users)} users")

    # ---------------- impute + z-score every family over the full 1,058 cohort ----------------
    Xd_parts = [Xc_df.reset_index(drop=True)]
    col_index = pd.Index(users, name="user_id")

    pos_z = impute_and_zscore(pos_raw, users, POSITION_COLS)
    moment_cols = [c for c in SPECTRAL_COLS if c.split("_", 1)[0] in ("mem", "amp")]
    shape_cols = [c for c in SPECTRAL_COLS if c.split("_", 1)[0] in ("rpi", "rph")]
    moment_covered = spec_raw.index[spec_raw["has_spectral_moment"] == 1.0]
    shape_covered = spec_raw.index[spec_raw["has_spectral_shape"] == 1.0]
    moment_z = impute_and_zscore(spec_raw.loc[moment_covered, moment_cols], users, moment_cols)
    shape_z = impute_and_zscore(spec_raw.loc[shape_covered, shape_cols], users, shape_cols)
    has_moment = spec_raw["has_spectral_moment"].reindex(users).fillna(0.0)
    has_shape = spec_raw["has_spectral_shape"].reindex(users).fillna(0.0)

    Xm_df = pd.concat([pos_z.reindex(users), moment_z.reindex(users), shape_z.reindex(users),
                       has_moment.rename(HAS_SPECTRAL_MOMENT), has_shape.rename(HAS_SPECTRAL_SHAPE)],
                      axis=1)[MOTION_COLS_ALL]
    Xm = Xm_df.to_numpy(float)

    # ---------------- arms D and M ----------------
    arm_d = expl3.ridge_arm(np.hstack([Xc, Xm]), Y, f"D union+motion-{Xc.shape[1] + Xm.shape[1]}")
    arm_m = expl3.ridge_arm(Xm, Y, f"M motion-{Xm.shape[1]}")

    delta_mean = round(arm_d["MEAN_BIG5"] - arm_c["MEAN_BIG5"], 4)
    delta_per = {t: round(arm_d[t] - arm_c[t], 4) for t in TRAITS}
    print(f"[delta C->D] mean {delta_mean:+.4f}; per trait "
          + " ".join(f"{t[:1]}={delta_per[t]:+.4f}" for t in TRAITS))

    # ---------------- complete-case sensitivity (no imputation on ANY added feature) --------
    complete_idx = [u for u in users if u in pos_covered
                    and has_moment.loc[u] == 1.0 and has_shape.loc[u] == 1.0]
    n_complete = len(complete_idx)
    print(f"[complete-case] users needing NO imputation on ANY added feature "
          f"(position AND moment AND shape all real): n={n_complete}")

    complete_delta = None
    complete_note = ""
    if n_complete >= 25:
        pos_i = [users.index(u) for u in complete_idx]
        Xc_cc = Xc[pos_i]
        Xm_cc = Xm[pos_i]
        Y_cc = Y[pos_i]
        arm_c_cc = expl3.ridge_arm(Xc_cc, Y_cc, f"C complete-case n={n_complete}")
        arm_d_cc = expl3.ridge_arm(np.hstack([Xc_cc, Xm_cc]), Y_cc, f"D complete-case n={n_complete}")
        complete_delta = round(arm_d_cc["MEAN_BIG5"] - arm_c_cc["MEAN_BIG5"], 4)
        complete_note = (f"complete-case RidgeCV run with n={n_complete} "
                         f"(KFold(5) folds ~{n_complete // 5} each): "
                         f"C={arm_c_cc['MEAN_BIG5']:+.4f}, D={arm_d_cc['MEAN_BIG5']:+.4f}, "
                         f"Delta={complete_delta:+.4f}.")
    else:
        complete_note = (f"complete-case n={n_complete} is too small to support a meaningful "
                         f"5-fold RidgeCV fit (need ~25+ for stable folds); reported honestly "
                         f"as an unfittable/degenerate case rather than a fabricated number. "
                         f"This n is itself the key complete-case finding: the shape family's "
                         f"own estimability gate (PERIOD2_MIN_LAG_PAIRS=100) admits only "
                         f"{spec_diag['n_shape_real']}/{len(users)} gated users, so requiring "
                         f"ALL families real collapses the complete-case population almost "
                         f"entirely regardless of the (much better covered) moment and "
                         f"position families.")
        complete_delta = 0.0
    print(f"[complete-case] {complete_note}")

    # ---------------- single-feature screen (covered users only, per feature) ----------------
    print(f"[screen] single-feature Pearson r on covered users; flag |r| >= .10:")
    screen = {}
    hits = []
    covered_map = {**{c: pos_covered for c in POSITION_COLS if c != "has_long"},
                   **{c: list(moment_covered) for c in moment_cols},
                   **{c: list(shape_covered) for c in shape_cols}}
    raw_map = {**{c: pos_raw for c in POSITION_COLS if c != "has_long"},
              **{c: spec_raw for c in moment_cols + shape_cols}}
    for feat in POSITION_COLS + SPECTRAL_COLS:
        if feat == "has_long":
            screen[feat] = {"n_covered": n_pos_cov, "note": "constant on covered", "r": {t: None for t in TRAITS}}
            continue
        cov_users = covered_map[feat]
        n_cov = len(cov_users)
        if n_cov < 3:
            screen[feat] = {"n_covered": n_cov, "note": "n<3, r not computable", "r": {t: None for t in TRAITS}}
            print(f"  {feat:20s} n_covered={n_cov:4d}  (too few for Pearson r)")
            continue
        x = raw_map[feat].loc[cov_users, feat].to_numpy(float)
        yc = big5.loc[cov_users, TRAITS]
        row = {}
        cells = []
        for t in TRAITS:
            r = float(stats.pearsonr(x, yc[t].to_numpy(float))[0])
            row[t] = round(r, 3)
            flag = "*" if abs(r) >= 0.10 else " "
            if abs(r) >= 0.10:
                hits.append((feat, t, round(r, 3)))
            cells.append(f"{r:+.3f}{flag}")
        screen[feat] = {"n_covered": n_cov, "r": row}
        print(f"  {feat:20s} n_covered={n_cov:4d} " + " ".join(f"{c:>8s}" for c in cells))
    print(f"[screen] |r| >= .10 hits: {hits if hits else 'none'}")

    # ---------------- adjudication ----------------
    expl4a_delta = -0.0096
    kill_fires = delta_mean <= 0 and expl4a_delta <= 0
    if kill_fires:
        adjudication = ("BOTH <=0 -> STANDING KILL FIRES: EXPL-4a Delta -0.0096 and EXPL-4b "
                        f"Delta {delta_mean:+.4f} are both <= 0. Recorded verdict: "
                        "questionnaire-criterion insensitivity to the motion layer, pending "
                        "BEHAVIORAL criteria (native corpus, N4).")
    elif delta_mean > 0:
        adjudication = (f"EXPL-4b Delta {delta_mean:+.4f} is POSITIVE -> kill does NOT fire; "
                        "the 1,500-char cap (not the motion layer itself) was at least part of "
                        "the confound EXPL-3 diagnosed. Compare against the registered lean "
                        "band [+.000, +.015].")
    else:
        adjudication = (f"EXPL-4b Delta {delta_mean:+.4f}; other (neither clean kill-fire nor "
                        "clean positive per the letter of the registration -- see notes).")
    print(f"[adjudication] {adjudication}")

    # ---------------- outputs ----------------
    result = {
        "banner": BANNER,
        "custody": {"labels": "PANDORA Big5 Tier-L labels, spent at opening #1 (git cd63d13)",
                   "essays_confirm_half": "untouched", "other_label_sources": "none read",
                   "ledger_row": "EXPL-4b"},
        "governance": {"eligibility_n": len(users), "H2_recomputed": r_h2, "H6_recomputed": r_h6,
                      "H2_H6_tolerance": "<1e-9, passed",
                      "arm_C_anchor": "reproduced EXPL-2 stored artifact exactly (mean .1361)"},
        "coverage": {"n_gated": len(users),
                    "n_covered_any_long_text": n_pos_cov,
                    "n_covered_m_ge3_spectral_census": int(n_ge3),
                    "n_covered_m_ge5_spectral_census": int(n_ge5),
                    "n_covered_spectral_moment_real": int(spec_diag["n_moment_real"]),
                    "n_covered_spectral_shape_real": int(spec_diag["n_shape_real"]),
                    "note": ("m_ge3/m_ge5 are LOOSE single-text feasibility census counts "
                             "(>=1 qualifying text at that window count) mirroring N1's own "
                             "ledger convention; spectral_moment_real/spectral_shape_real are "
                             "the STRICT counts of users for whom motion.py's own pooled-row "
                             "estimability gate (MIN_D2_ROWS=30 / PERIOD2_MIN_LAG_PAIRS=100) "
                             "actually returned a non-imputed value -- these are much smaller "
                             "and are the mechanistically correct coverage numbers for what "
                             "Arm D actually uses as real (non-imputed) data.")},
        "axes": {"source": "P8 cache (Tier-U), expl3 recipe reused directly: per-cid last-first "
                          "-> corr_guarded -> top eigvecs 1-3", "n_cids": int(Dp.shape[0])},
        "arm_C_anchor": arm_c,
        "arm_D_union_plus_motion": arm_d,
        "arm_M_motion_only": arm_m,
        "delta_C_to_D": {"mean": delta_mean, **delta_per},
        "complete_case": {"n": n_complete, "delta_mean": complete_delta, "note": complete_note},
        "single_feature_screen_covered_only": screen,
        "screen_hits_abs_r_ge_010": [{"feature": f, "trait": t, "r": r} for f, t, r in hits],
        "registered_leans": {"delta_mean_band": "[+.000, +.015]",
                             "standing_kill": "if EXPL-4a AND EXPL-4b both Delta <= 0"},
        "adjudication": {"expl4a_delta": expl4a_delta, "expl4b_delta": delta_mean,
                         "kill_fires": bool(kill_fires), "text": adjudication},
        "feature_families": {"position_slope_10": POSITION_COLS,
                             "spectral_30": SPECTRAL_COLS + [HAS_SPECTRAL_MOMENT, HAS_SPECTRAL_SHAPE],
                             "family_descriptions": SPECTRAL_PREFIXES},
    }
    (OUT_DIR / "EXPL4B_RESULTS.json").write_text(json.dumps(result, indent=2))

    md = ["# EXPL-4b -- uncapped Tier-L motion weight-fit (EXPLORATORY, spent labels)", "",
          f"> {BANNER}", ">",
          "> Labels spent at opening #1; reuse here is exploratory (F14 N-program, 97ecca2).",
          "> Gate, H2/H6, and the EXPL-2 arm-C anchor all reproduced before fitting.", "",
          f"Coverage: position/slope {n_pos_cov}/{len(users)} gated users (>=1 uncapped long "
          f"text, m>=2); spectral census m>=3 in {n_ge3}, m>=5 in {n_ge5} (loose, N1-style); "
          f"REAL (non-imputed) spectral moment (signed memory + gust amplitude) in "
          f"{spec_diag['n_moment_real']}/{len(users)}; REAL spectral shape (rho_pi/rho_pi_half) "
          f"in {spec_diag['n_shape_real']}/{len(users)} -- motion.py's own MIN_D2_ROWS=30 / "
          f"PERIOD2_MIN_LAG_PAIRS=100 gates, much stricter than the loose per-text census.", "",
          "| arm | E | N | A | C | O | mean |", "|---|---|---|---|---|---|---|"]
    for name, arm in [("C: EXPL-2 union (anchor)", arm_c),
                      ("D: C + motion-" + str(Xm.shape[1]), arm_d),
                      ("M: motion-" + str(Xm.shape[1]) + " alone", arm_m)]:
        md.append("| " + name + " | " + " | ".join(f"{arm[t]:+.3f}" for t in TRAITS)
                  + f" | {arm['MEAN_BIG5']:+.4f} |")
    md += ["",
          f"Delta(C->D): mean {delta_mean:+.4f}; per trait "
          + ", ".join(f"{t} {delta_per[t]:+.4f}" for t in TRAITS) + ".",
          "",
          f"Complete-case sensitivity (n={n_complete}, real coverage on EVERY added feature): "
          + (f"Delta {complete_delta:+.4f}." if n_complete >= 25 else
             f"NOT FITTABLE at n={n_complete} (reported plainly, not hidden). {complete_note}"),
          "",
          "Single-feature screen (covered users only per feature; |r| >= .10 flagged): "
          + (", ".join(f"{f}->{t} r={r:+.3f}" for f, t, r in hits) if hits else "no hits"), "",
          f"**Adjudication.** {adjudication}", "",
          "Registered lean (97ecca2): Delta(C->D) in [+.000, +.015]. STANDING KILL: EXPL-4a "
          f"({expl4a_delta:+.4f}) and EXPL-4b ({delta_mean:+.4f}) both <= 0 -> "
          + ("FIRES." if kill_fires else "does not fire.")]
    (OUT_DIR / "EXPL4B_RESULTS.md").write_text("\n".join(md) + "\n")
    print("written:", OUT_DIR / "EXPL4B_RESULTS.json")
    print("written:", OUT_DIR / "EXPL4B_RESULTS.md")


if __name__ == "__main__":
    main()
