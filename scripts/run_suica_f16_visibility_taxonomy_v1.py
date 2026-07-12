#!/usr/bin/env python
"""F16 -- Visibility taxonomy: static-only / dynamic-only / both / neither, against
every existing external anchor (registered 2026-07-12, docs/SUICA_THEORY_FORMAL_NOTES_V3.md
"## F16" section; ledger row V6-F16, git 32befcf). Operator-ordered generalization of W10's
single hand-built gust1_P composite to EVERY one of the 19 frozen v4-battery constructs.

EXPLORATORY. Three governed anchor tiers, none conflated:
  (i)   PANDORA official Big5, opening-#1 gate (n=1,058) -- SPENT labels. Gate + H2 + H6
        re-verified to <1e-9 against OPENING_REPORT.json BEFORE any fitting (assert block
        copied verbatim from run_suica_expl3_motion_weightfit_v1.py, reusing its own
        finalize_axes() helper rather than re-deriving it from a description).
  (ii)  PANDORA official MBTI axes (EI/SN/TF/JP_cont, ~9,042 users) -- FIRST correlational
        use of these labels against SUICA constructs (previously spent only for LoRA
        training, a different kind of spend). No prior replication target exists for this
        anchor, so no assert-to-published-number step applies here; this run itself
        becomes the reference point for any future reuse. Coverage against tier_l/tier_u
        uncapped is determined empirically, not assumed.
  (iii) Essays Big5, DEV HALF ONLY (1,255 users). load_dev_ids() and two_pass_dev_labels()
        are imported and called VERBATIM from run_suica_expl4a_essays_motion_v1.py; confirm-
        half label bytes are never parsed, even transiently.

For each of the 19 frozen constructs c (construct names read at runtime from an existing
scored cache via w2a.get_construct_cols -- never hardcoded), two channel scores per user u:
  STATIC S_c(u)  = person mean of c over ALL scored windows (no new estimator).
  DYNAMIC D_c(u) = W10's within-text-linear-detrended, pooled-sd-standardized residual
                   activation (within_text_linear_residuals, reused UNMODIFIED), generalized
                   from a single projection onto the gust1_P composite to each construct's
                   OWN axis individually (construct c's own residual column IS its axis --
                   the natural per-construct generalization of "project onto a unit
                   direction"); person score = mean |activation|, m>=3 windows required.

Dynamic scores (and the primary static scores used in the main grid) are built from N1's
UNCAPPED tier_l + tier_u parquets -- NOT the old capped Tier-U cache -- because the entire
point of F16 is to use the deeper coverage N1 unlocked; reusing the capped cache for the
dynamic channel would silently reproduce the W9/EXPL-3 cap-artifact problem. The capped
cache (results/suica_tgeo_p8_functionalization/cache_windows_scored19.parquet) is used
ONLY for the pre-registered cap-sensitivity check on STATIC scores.

Secondary, exploratory-of-exploratory descriptors (signed memory r_c = B_hat_cc/Gamma0_hat_cc
and the rho_pi/rho_pi_half spectral-shape pair), from the RELEASE repo's suica_core/motion.py
(motion_profile, used unmodified): these are corpus/population-POOLED moment estimates, not
per-person scores -- suica_core.motion has no notion of "user" at all, it batches a list of
texts and estimates ONE set of moments per construct for that whole batch (T4 estimability
guard: needs >=30 pooled second-difference rows). They CANNOT be correlated per-person
against per-person anchor labels the way the primary D_c(u)/S_c(u) channels can, so they are
reported as population-level descriptive tables (one per anchor population), explicitly
separate from -- and never counted toward -- the primary static/dynamic classification grid.

BH-FDR (project_persona.suica.bh_fdr) applied SEPARATELY to the pooled static-channel
p-values (19 constructs x up to 14 anchor traits = 266 cells) and the pooled dynamic-channel
p-values (same 266 cells) -- never pooled together, never split per-anchor-set.
Classification per cell: pass = q_bh < .05 AND |r| >= .08.
  BOTH pass -> BOTH; static only -> STATIC-ONLY; dynamic only -> DYNAMIC-ONLY; neither -> NEITHER.

STANDING KILL: if the DYNAMIC-ONLY bucket is empty across the entire grid, W10's headline
motion-only finding demotes from "a general property of the construct space" to "true only
of the one hand-built gust1_P composite" -- this script records that demotion explicitly if
triggered, rather than silently re-describing the result as consistent with W10.

No git commits are made by this script. Seed: 20260712 (this program's registration-date
seed, shared with W2a/W10/E2).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_persona.suica import PERSONALITY_LEAK_RE, tokenize, bh_fdr  # noqa: E402
import scripts.run_suica_c2_purity_all19_v1 as a19  # noqa: E402
import scripts.run_suica_v6_w2a_delta2_dynamics_v1 as w2a  # noqa: E402
import scripts.run_suica_v6_w10_invisible_anatomy_v1 as w10  # noqa: E402
import scripts.run_suica_expl3_motion_weightfit_v1 as expl3  # noqa: E402
import scripts.run_suica_expl4a_essays_motion_v1 as expl4a  # noqa: E402
import scripts.run_suica_dev_anchor_performance_v1 as dav  # noqa: E402

# RELEASE_ROOT is added to sys.path ONLY AFTER every project-persona "scripts.*"
# reuse import above has already resolved (and is appended at the END, not
# inserted at position 0). Both repos ship a same-named, __init__.py-less
# "scripts" namespace package (PEP 420) with several identically-named files
# that are NOT byte-identical (verified: run_suica_c2_purity_all19_v1.py,
# run_suica_dev_anchor_performance_v1.py, run_suica_op5_construct_discovery_v3.py
# differ between the two repos -- only in their internal import source,
# project_persona.suica vs suica_core.suica, themselves verified byte-identical
# modules, but a real shadowing hazard in general). Inserting RELEASE_ROOT
# first (as an earlier version of this script did) silently resolved EVERY
# "scripts.*" import above against the RELEASE repo's copies instead of these
# frozen research-repo ones -- caught and fixed before any numeric result was
# trusted. suica_core itself has no project-persona namesake, so appending
# RELEASE_ROOT at the end, after all "scripts.*" submodules are already cached
# in sys.modules, is sufficient and namespace-safe.
RELEASE_ROOT = Path("/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment")
if str(RELEASE_ROOT) not in sys.path:
    sys.path.append(str(RELEASE_ROOT))
from suica_core.motion import motion_profile  # noqa: E402  (secondary descriptors only)

SEED = 20260712
WIN = 128
MAX_WINDOWS = 12
MIN_TOKENS = 288
CHAR_CANDIDATE = 1200
Q_THRESHOLD = 0.05
EFFECT_FLOOR = 0.08
CAP_SENSITIVITY_THRESHOLD = 0.02
GUST1P_CARRIER_SET = frozenset({"wcl_02", "wcl_07", "wcl_11", "wcl_20"})

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
TIER_L_UNCAPPED = TIER_DIR / "tier_l_comments_uncapped_v1.parquet"
TIER_U_UNCAPPED = TIER_DIR / "tier_u_comments_uncapped_v1.parquet"
PREDICTORS = ROOT / "results" / "suica_lockbox_opening_1" / "predictors.parquet"
OPENING_REPORT = ROOT / "results" / "suica_lockbox_opening_1" / "OPENING_REPORT.json"
BIG5_LABELS = ROOT / "data_sets" / "prepared" / "pandora_official" / "pandora_official_big5_prepared.csv"
MBTI_DIR = ROOT / "data_sets" / "prepared" / "pandora_official" / "mbti_axes"
P8_CACHE = ROOT / "results" / "suica_tgeo_p8_functionalization" / "cache_windows_scored19.parquet"
ESSAYS_CACHE = ROOT / "results" / "suica_v6_e2_essays_motion" / "cache_essays_windows_scored19.parquet"

OUT_DIR = ROOT / "results" / "suica_f16_visibility_taxonomy"
POOL_CACHE = OUT_DIR / "pandora_uncapped_windows_scored19.parquet"
OUT_JSON = OUT_DIR / "F16_VISIBILITY_TAXONOMY.json"
OUT_MD = OUT_DIR / "F16_VISIBILITY_TAXONOMY.md"

BIG5_TRAITS = ["Extraversion", "Neuroticism", "Agreeableness", "Conscientiousness", "Openness"]
MBTI_TRAITS = ["EI_cont", "SN_cont", "TF_cont", "JP_cont"]

BANNER = ("EXPLORATORY -- F16 visibility taxonomy (V6-F16). PANDORA Big5: SPENT labels "
          "(opening #1). PANDORA MBTI axes: FIRST correlational use (label-spending event, "
          "this run). Essays Big5: DEV HALF ONLY.")


# ============================================================================
# Governance gate 1+2: PANDORA Big5 opening-#1 eligibility + H2/H6 (<1e-9)
# Copied VERBATIM from run_suica_expl3_motion_weightfit_v1.py main(), lines
# ~222-241 (the EXPL-1/EXPL-3 assert block), reusing that module's own
# finalize_axes() helper rather than re-deriving its logic from a description.
# ============================================================================

def governance_gate_h2_h6() -> tuple[list, pd.DataFrame, float, float]:
    pred = pd.read_parquet(PREDICTORS)
    pred.index = pred.index.astype(str)
    big5 = pd.read_csv(BIG5_LABELS).set_index("user_id")            # opening L439
    big5.index = big5.index.astype(str)
    gate = (pred["n_conditions"] >= 4) & (pred["n_slices"] >= 12)   # opening L301
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
    return users, big5, r_h2, r_h6


# ============================================================================
# Uncapped PANDORA window pool (N1 tier_l + tier_u), scored on the 19 frozen
# constructs. SAME window-construction pattern as run_suica_tgeo_p7_flow_curve_v1
# .build_windows() (128-token non-overlapping windows, endpoint-preserving
# 12-window subsample, whole-text leak drop), generalized to source from BOTH
# N1 uncapped parquets (tier_l and tier_u author sets are disjoint -- verified
# 0 overlap -- so straight concatenation does not double-count any user).
# ============================================================================

def load_pandora_uncapped_candidates() -> pd.DataFrame:
    frames = []
    for path in (TIER_L_UNCAPPED, TIER_U_UNCAPPED):
        df = pd.read_parquet(path, columns=["author", "body"])
        df["author"] = df["author"].astype(str)
        frames.append(df)
    comments = pd.concat(frames, ignore_index=True)
    body = comments["body"].astype(str)
    cand = comments.loc[body.str.len() >= CHAR_CANDIDATE].reset_index(drop=True)
    return cand


def build_pandora_uncapped_windows(cand: pd.DataFrame) -> pd.DataFrame:
    rows = []
    n_leak = 0
    for cid, (author, text) in enumerate(zip(cand["author"], cand["body"].astype(str))):
        tokens = tokenize(text)
        if len(tokens) < MIN_TOKENS:
            continue
        m = len(tokens) // WIN
        if m < 2:
            continue
        keep = (np.unique(np.round(np.linspace(0, m - 1, MAX_WINDOWS)).astype(int))
                if m > MAX_WINDOWS else np.arange(m))
        wrows = []
        ok = True
        for j in keep:
            wtext = " ".join(tokens[j * WIN:(j + 1) * WIN])
            if PERSONALITY_LEAK_RE.search(wtext):
                ok = False
                n_leak += 1
                break
            wrows.append({"cid": cid, "user_id": author, "j": int(j), "m": int(m),
                          "t": float(j / (m - 1)), "slice_text": wtext})
        if ok:
            rows.extend(wrows)
    frame = pd.DataFrame(rows)
    print(f"[pool] candidates >=1200 chars: {len(cand)}; texts kept (m>=2, leak-clean): "
          f"{frame['cid'].nunique() if len(frame) else 0}; leak-dropped texts: {n_leak}; "
          f"windows: {len(frame)}")
    return frame


def score_pool(frame: pd.DataFrame, wcl_transform, cols: list) -> pd.DataFrame:
    slice_frame = frame[["user_id", "slice_text"]].assign(condition="_", half="_")[
        ["user_id", "condition", "half", "slice_text"]]
    scored = a19.score_slices_v2(slice_frame)
    wcl = wcl_transform(frame["slice_text"]).reset_index(drop=True)
    S = pd.concat([scored[list(a19.V3_BATTERY)].reset_index(drop=True),
                   wcl[list(a19.OP5_KEPT)]], axis=1)[cols]
    out = frame[["cid", "user_id", "j", "m", "t"]].reset_index(drop=True).join(S)
    return out


def load_or_build_pool(cols: list, wcl_transform) -> pd.DataFrame:
    if POOL_CACHE.exists():
        pool = pd.read_parquet(POOL_CACHE)
        print(f"[pool] loaded from cache: {len(pool)} windows / {pool['cid'].nunique()} texts "
              f"/ {pool['user_id'].nunique()} users")
        return pool
    cand = load_pandora_uncapped_candidates()
    frame = build_pandora_uncapped_windows(cand)
    pool = score_pool(frame, wcl_transform, cols)
    pool.to_parquet(POOL_CACHE)
    print(f"[pool] built + scored + cached: {len(pool)} windows / {pool['cid'].nunique()} "
          f"texts / {pool['user_id'].nunique()} users -> {POOL_CACHE.relative_to(ROOT)}")
    return pool


# ============================================================================
# STATIC and DYNAMIC person-level scores
# ============================================================================

def person_static(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    return df.groupby("user_id")[cols].mean()


def person_dynamic(df: pd.DataFrame, cols: list, id_col: str) -> tuple[pd.DataFrame, dict]:
    """Reuses run_suica_v6_w10_invisible_anatomy_v1.within_text_linear_residuals
    UNMODIFIED. Generalizes W10's single gust1_P-projection activation to every
    construct's OWN column (construct c's own residual IS its "axis")."""
    sub = df[df["m"] >= 3].sort_values([id_col, "j"]).reset_index(drop=True)
    if len(sub) == 0:
        return pd.DataFrame(columns=cols), {"n_windows_m_ge_3": 0, "n_texts_m_ge_3": 0,
                                            "n_users_m_ge_3": 0, "pooled_sd": None}
    resid_std, pooled_sd = w10.within_text_linear_residuals(sub, id_col, cols)
    abs_resid = pd.DataFrame(np.abs(resid_std), columns=cols)
    abs_resid["user_id"] = sub["user_id"].to_numpy()
    D = abs_resid.groupby("user_id")[cols].mean()
    diag = {"n_windows_m_ge_3": int(len(sub)), "n_texts_m_ge_3": int(sub[id_col].nunique()),
            "n_users_m_ge_3": int(sub["user_id"].nunique()),
            "pooled_sd": {c: float(s) for c, s in zip(cols, pooled_sd)}}
    return D, diag


# ============================================================================
# Cap-sensitivity check (pre-registered): capped P8 cache vs uncapped-derived
# STATIC scores, for users present in both.
# ============================================================================

def cap_sensitivity_check(uncapped_static: pd.DataFrame, cols: list) -> dict:
    p8 = pd.read_parquet(P8_CACHE)
    p8_cols = w2a.get_construct_cols(p8)
    assert p8_cols == cols, "P8 cache construct order mismatch vs frozen cols"
    capped_static = p8.groupby("user_id")[cols].mean()
    common = uncapped_static.index.intersection(capped_static.index)
    n_common = int(len(common))
    per_construct = {}
    flagged = []
    for c in cols:
        u = uncapped_static.loc[common, c].to_numpy(float)
        k = capped_static.loc[common, c].to_numpy(float)
        diff = u - k
        mean_diff = float(diff.mean())
        mean_abs_diff = float(np.abs(diff).mean())
        if n_common >= 3 and diff.std() > 1e-12:
            t_stat, t_p = stats.ttest_rel(u, k)
            t_p = float(t_p)
        else:
            t_p = float("nan")
        flag = abs(mean_diff) > CAP_SENSITIVITY_THRESHOLD
        if flag:
            flagged.append(c)
        per_construct[c] = {"mean_diff_uncapped_minus_capped": round(mean_diff, 6),
                             "mean_abs_diff": round(mean_abs_diff, 6),
                             "paired_ttest_p": t_p, "flagged_gt_0.02": flag}
    return {"n_common_users": n_common,
            "population_note": ("Overlap population is the Tier-U capped-cache users "
                                 "(P8 cache, 3622 users) intersected with the Tier-U "
                                 "portion of the new uncapped pool -- P8 is the only "
                                 "pre-existing capped GENERAL-window cache available; "
                                 "it does not include the Big5-gate (tier_l) population "
                                 "at all (tier_l and tier_u author sets are disjoint), "
                                 "so this check validates the capping pipeline in "
                                 "general, not the gate anchor population specifically."),
            "per_construct": per_construct,
            "any_flagged": flagged,
            "result": ("FLAGGED: >|.02| systematic diff on " + ", ".join(flagged)) if flagged
                       else "clean: no construct differs by >|.02| (capped vs uncapped static)"}


# ============================================================================
# MBTI axis labels (first correlational use)
# ============================================================================

def load_mbti_axis_labels() -> pd.DataFrame:
    frames = {}
    ref_ids = None
    for axis in MBTI_TRAITS:
        df = pd.read_csv(MBTI_DIR / f"pandora_official_{axis}_prepared.csv",
                          usecols=["user_id", "positive_probability"], dtype={"user_id": str})
        df = df.set_index("user_id")["positive_probability"].rename(axis)
        ids = set(df.index)
        if ref_ids is None:
            ref_ids = ids
        else:
            assert ids == ref_ids, f"{axis} user_id set differs from EI_cont's"
        frames[axis] = df
    out = pd.concat(frames.values(), axis=1)
    return out


# ============================================================================
# Safe Pearson (pairwise-complete, guarded against zero-variance / n<3)
# ============================================================================

def safe_pearson(x: np.ndarray, y: np.ndarray) -> tuple[float, float, int]:
    mask = np.isfinite(x) & np.isfinite(y)
    n = int(mask.sum())
    if n < 3:
        return float("nan"), float("nan"), n
    xf, yf = x[mask], y[mask]
    if xf.std() == 0 or yf.std() == 0:
        return float("nan"), float("nan"), n
    r, p = stats.pearsonr(xf, yf)
    return float(r), float(p), n


# ============================================================================
# Full grid: 19 constructs x anchors x 2 channels
# ============================================================================

def build_grid(cols: list, S: dict, D: dict, anchors: dict) -> list[dict]:
    rows = []
    for anchor_name, (labels_df, traits) in anchors.items():
        s_df, d_df = S[anchor_name], D[anchor_name]
        for construct in cols:
            for trait in traits:
                common_s = s_df.index.intersection(labels_df.index) if len(s_df) else pd.Index([])
                if len(common_s):
                    r_s, p_s, n_s = safe_pearson(s_df.loc[common_s, construct].to_numpy(float),
                                                 labels_df.loc[common_s, trait].to_numpy(float))
                else:
                    r_s, p_s, n_s = float("nan"), float("nan"), 0
                common_d = d_df.index.intersection(labels_df.index) if len(d_df) else pd.Index([])
                if len(common_d):
                    r_d, p_d, n_d = safe_pearson(d_df.loc[common_d, construct].to_numpy(float),
                                                 labels_df.loc[common_d, trait].to_numpy(float))
                else:
                    r_d, p_d, n_d = float("nan"), float("nan"), 0
                rows.append({"anchor": anchor_name, "construct": construct, "trait": trait,
                             "r_static": r_s, "p_static": p_s, "n_static": n_s,
                             "r_dynamic": r_d, "p_dynamic": p_d, "n_dynamic": n_d})
    return rows


def apply_bh_and_classify(rows: list[dict]) -> list[dict]:
    p_static = [row["p_static"] for row in rows]
    p_dynamic = [row["p_dynamic"] for row in rows]
    q_static = bh_fdr(p_static)
    q_dynamic = bh_fdr(p_dynamic)
    for row, qs, qd in zip(rows, q_static, q_dynamic):
        row["q_static_bh"] = qs
        row["q_dynamic_bh"] = qd
        pass_s = (np.isfinite(row["r_static"]) and qs < Q_THRESHOLD
                  and abs(row["r_static"]) >= EFFECT_FLOOR)
        pass_d = (np.isfinite(row["r_dynamic"]) and qd < Q_THRESHOLD
                  and abs(row["r_dynamic"]) >= EFFECT_FLOOR)
        row["pass_static"] = bool(pass_s)
        row["pass_dynamic"] = bool(pass_d)
        if pass_s and pass_d:
            row["classification"] = "BOTH"
        elif pass_s:
            row["classification"] = "STATIC-ONLY"
        elif pass_d:
            row["classification"] = "DYNAMIC-ONLY"
        else:
            row["classification"] = "NEITHER"
    return rows


# ============================================================================
# Secondary, exploratory-of-exploratory descriptors (suica_core/motion.py,
# unmodified). POPULATION-POOLED, not per-person -- reported separately, never
# counted toward the primary classification.
# ============================================================================

def make_batch_scorer(wcl_transform, cols: list):
    def scorer(window_texts: list) -> np.ndarray:
        n = len(window_texts)
        frame = pd.DataFrame({"user_id": ["_"] * n, "condition": "_", "half": "_",
                              "slice_text": window_texts})
        scored = a19.score_slices_v2(frame)
        wcl = wcl_transform(frame["slice_text"]).reset_index(drop=True)
        S = pd.concat([scored[list(a19.V3_BATTERY)].reset_index(drop=True),
                       wcl[list(a19.OP5_KEPT)]], axis=1)[cols]
        return S.to_numpy(float)
    return scorer


def secondary_descriptors(name: str, texts: list, scorer) -> dict:
    t0 = time.time()
    mp = motion_profile(texts, scorer=scorer, axis=None, win=WIN, max_windows=MAX_WINDOWS)
    dt = time.time() - t0
    print(f"[secondary/{name}] n_texts_in={len(texts)} n_texts_used={mp['n_texts_used']} "
          f"n_texts_dropped={mp['n_texts_dropped']} n_windows={mp['n_windows']} "
          f"gamma0_reason={mp['gamma0_reason']} period2_reason={mp['period2_reason']} "
          f"({dt:.1f}s)")
    return mp


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    print(BANNER)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    # ---------------- Governance: PANDORA Big5 gate + H2/H6 (<1e-9) ----------------
    gate_users, big5, r_h2, r_h6 = governance_gate_h2_h6()

    # ---------------- Governance: MBTI axes, first-use banner ----------------
    print("[governance] MBTI-AXIS FIRST-USE / LABEL-SPENDING EVENT: PANDORA official MBTI "
          "axis labels (EI/SN/TF/JP_cont) are being correlated against SUICA constructs for "
          "the FIRST time in this program. No prior replication target exists for this "
          "anchor tier; this run itself becomes the reference point any future reuse must "
          "replicate. (Previously spent only for LoRA CV training -- a different kind of "
          "spend.)")
    mbti_labels = load_mbti_axis_labels()
    n_mbti_users = len(mbti_labels)
    print(f"[governance] MBTI axis labels loaded: {n_mbti_users} users, "
          f"{list(mbti_labels.columns)}")

    tier_l_ids = set(pd.read_parquet(TIER_L_UNCAPPED, columns=["author"])["author"].astype(str))
    tier_u_ids = set(pd.read_parquet(TIER_U_UNCAPPED, columns=["author"])["author"].astype(str))
    assert len(tier_l_ids & tier_u_ids) == 0, "tier_l/tier_u author sets unexpectedly overlap"
    mbti_ids = set(mbti_labels.index)
    mbti_in_tier_l = mbti_ids & tier_l_ids
    mbti_in_tier_u = mbti_ids & tier_u_ids
    mbti_in_either = mbti_in_tier_l | mbti_in_tier_u
    print(f"[coverage] MBTI-axis users ({n_mbti_users}) present in N1 uncapped tier_l: "
          f"{len(mbti_in_tier_l)}; in tier_u: {len(mbti_in_tier_u)}; in EITHER "
          f"(no overlap possible, tier_l/tier_u disjoint): {len(mbti_in_either)} "
          f"({100 * len(mbti_in_either) / n_mbti_users:.1f}%) -- NOT assumed, measured.")

    gate_in_tier_l = set(gate_users) & tier_l_ids
    print(f"[coverage] Big5-gate users ({len(gate_users)}) present in N1 uncapped tier_l: "
          f"{len(gate_in_tier_l)} ({100 * len(gate_in_tier_l) / len(gate_users):.1f}%)")

    # ---------------- Governance: Essays dev-half (two-pass label-free reuse) ----------------
    dev_ids = expl4a.load_dev_ids()
    labels_essays = expl4a.two_pass_dev_labels(dev_ids)
    print(f"[governance] Essays dev-half two-pass label read verified: {len(dev_ids)} dev "
          f"ids, {len(labels_essays)} labels loaded; confirm-half label bytes never parsed.")
    assert ESSAYS_CACHE.exists(), f"Essays window cache missing: {ESSAYS_CACHE}"

    # ---------------- Frozen construct list (never hardcoded) ----------------
    p8_full = pd.read_parquet(P8_CACHE)
    cols = w2a.get_construct_cols(p8_full)
    essays_cache_full = pd.read_parquet(ESSAYS_CACHE)
    cols_e = w2a.get_construct_cols(essays_cache_full)
    assert cols == cols_e, "construct column order differs between P8 and Essays caches"
    assert len(cols) == 19, f"expected 19 frozen constructs, got {len(cols)}"
    print(f"[constructs] {len(cols)} frozen v4-battery constructs (read from P8/Essays "
          f"caches via w2a.get_construct_cols): {cols}")

    # ---------------- Fit the frozen wcl transform ONCE (EXPL-3's precedent) ----------------
    t0 = time.time()
    _style_unused, wcl_transform = dav.pandora_style_fit_and_battery()
    print(f"[wcl] frozen wcl_transform fit on op9_half_slices.parquet ({time.time()-t0:.1f}s)")

    # ---------------- Build/score the N1 uncapped PANDORA window pool ----------------
    pool = load_or_build_pool(cols, wcl_transform)
    uncapped_static = person_static(pool, cols)
    uncapped_dynamic, dyn_diag = person_dynamic(pool, cols, id_col="cid")
    print(f"[dynamic/pandora] {dyn_diag['n_windows_m_ge_3']} windows / "
          f"{dyn_diag['n_texts_m_ge_3']} texts / {dyn_diag['n_users_m_ge_3']} users with "
          f"m>=3 qualifying activation estimates")

    n_gate_static = int(len(uncapped_static.index.intersection(gate_users)))
    n_gate_dynamic = int(len(uncapped_dynamic.index.intersection(gate_users)))
    n_mbti_static = int(len(uncapped_static.index.intersection(mbti_ids)))
    n_mbti_dynamic = int(len(uncapped_dynamic.index.intersection(mbti_ids)))
    print(f"[coverage] Big5-gate: static n={n_gate_static}/{len(gate_users)}, "
          f"dynamic (m>=3) n={n_gate_dynamic}/{len(gate_users)}")
    print(f"[coverage] MBTI-axis: static n={n_mbti_static}/{n_mbti_users}, "
          f"dynamic (m>=3) n={n_mbti_dynamic}/{n_mbti_users}")

    # ---------------- Cap-sensitivity check (pre-registered) ----------------
    cap_check = cap_sensitivity_check(uncapped_static, cols)
    print(f"[cap-sensitivity] n_common_users={cap_check['n_common_users']}; "
          f"{cap_check['result']}")

    # ---------------- Essays: dev-restricted cache, STATIC + DYNAMIC ----------------
    essays_dev_cache = essays_cache_full.loc[
        essays_cache_full["user_id"].astype(str).isin(dev_ids)].copy()
    n_dev_cache = int(essays_dev_cache["eid"].nunique())
    essays_static = person_static(essays_dev_cache, cols)
    essays_dynamic, essays_dyn_diag = person_dynamic(essays_dev_cache, cols, id_col="eid")
    print(f"[coverage] Essays dev-half: {len(dev_ids)} ids, {n_dev_cache} with cache "
          f"coverage (m>=2), static n={len(essays_static)}, dynamic (m>=3) n="
          f"{len(essays_dynamic)} ({essays_dyn_diag['n_texts_m_ge_3']} texts)")

    # ---------------- Build the full grid ----------------
    S = {"pandora_big5": uncapped_static, "mbti_axes": uncapped_static, "essays_big5": essays_static}
    D = {"pandora_big5": uncapped_dynamic, "mbti_axes": uncapped_dynamic, "essays_big5": essays_dynamic}
    anchors = {
        "pandora_big5": (big5.loc[gate_users, BIG5_TRAITS], BIG5_TRAITS),
        "mbti_axes": (mbti_labels, MBTI_TRAITS),
        "essays_big5": (labels_essays[BIG5_TRAITS], BIG5_TRAITS),
    }
    rows = build_grid(cols, S, D, anchors)
    n_cells = len(rows)
    print(f"[grid] {n_cells} (construct x anchor) cells built "
          f"({len(cols)} constructs x {sum(len(t) for _, t in anchors.values())} anchor "
          f"traits across {len(anchors)} anchor sets)")

    rows = apply_bh_and_classify(rows)

    both = [r for r in rows if r["classification"] == "BOTH"]
    static_only = [r for r in rows if r["classification"] == "STATIC-ONLY"]
    dynamic_only = [r for r in rows if r["classification"] == "DYNAMIC-ONLY"]
    neither = [r for r in rows if r["classification"] == "NEITHER"]
    print(f"[classification] BOTH={len(both)} STATIC-ONLY={len(static_only)} "
          f"DYNAMIC-ONLY={len(dynamic_only)} NEITHER={len(neither)} (of {n_cells})")

    standing_kill = len(dynamic_only) == 0
    dyn_only_constructs = sorted({r["construct"] for r in dynamic_only})
    dyn_only_in_carrier_set = [c for c in dyn_only_constructs if c in GUST1P_CARRIER_SET]
    if standing_kill:
        print("[STANDING KILL TRIGGERED] zero (construct, anchor) cells classify "
              "DYNAMIC-ONLY anywhere in the full grid -- W10's headline finding DEMOTES "
              "from 'a general property of the construct space' to 'true only of the "
              "one hand-built gust1_P composite'. Recorded explicitly, not smoothed over.")
    else:
        print(f"[lean check] DYNAMIC-ONLY constructs: {dyn_only_constructs}; of these, in "
              f"the W10 gust1_P carrier set {sorted(GUST1P_CARRIER_SET)}: "
              f"{dyn_only_in_carrier_set}")

    # ---------------- Secondary descriptors (population-pooled, separate table) ----------------
    scorer = make_batch_scorer(wcl_transform, cols)
    cand = load_pandora_uncapped_candidates()

    gate_texts = cand.loc[cand["author"].isin(set(gate_users)), "body"].astype(str).tolist()
    mbti_texts = cand.loc[cand["author"].isin(mbti_in_either), "body"].astype(str).tolist()
    essays_raw = pd.read_csv(expl4a.ESSAYS, usecols=["user_id", "text"], dtype={"user_id": str})
    essays_dev_texts = essays_raw.loc[essays_raw["user_id"].isin(dev_ids), "text"].astype(str).tolist()

    secondary = {
        "pandora_big5_gate": secondary_descriptors("pandora_big5_gate", gate_texts, scorer),
        "mbti_axes_population": secondary_descriptors("mbti_axes_population", mbti_texts, scorer),
        "essays_dev_half": secondary_descriptors("essays_dev_half", essays_dev_texts, scorer),
    }

    # ============================================================================
    # Outputs
    # ============================================================================
    ambiguities = [
        "STATIC scores used for the main grid (both Big5-gate and MBTI-axis anchors) come "
        "from the SAME N1-uncapped PANDORA window pool as the DYNAMIC channel (not the old "
        "capped P8 cache), so both channels are computed on an identical, apples-to-apples "
        "per-user population; the capped P8 cache is used ONLY for the separate, "
        "pre-registered cap-sensitivity validation check, per the registration's explicit "
        "carve-out ('Capped cache is fine only for the pre-registered cap-sensitivity check "
        "on STATIC scores').",
        "The uncapped PANDORA window pool is built from BOTH N1 tier_l AND tier_u parquets "
        "concatenated (verified disjoint author sets, 0 overlap) -- not tier_l alone -- "
        "because the MBTI-axis anchor's governance text explicitly asks for tier_l-OR-tier_u "
        "coverage, and 100% of tier_u's 5,000 authors (vs only 364 of tier_l's 1,412) fall "
        "inside the MBTI-axis population; tier_l alone would have silently discarded the "
        "large majority of reachable MBTI-axis coverage.",
        "The DYNAMIC-channel activation for construct c is that construct's OWN standardized "
        "within-text residual column (a_w = resid_std[:, c]), not a projection onto any "
        "composite direction -- read as the literal per-construct generalization of W10's "
        "single projection onto the gust1_P unit vector (a construct's 'own axis' is the "
        "one-hot/unit basis vector e_c).",
        cap_check["population_note"],
        "Secondary descriptors (signed memory, rho_pi/rho_pi_half spectral-shape pair) from "
        "suica_core/motion.py's motion_profile() are corpus/population-POOLED moment "
        "estimates (T4 guard: >=30 pooled second-difference rows), not per-person scores -- "
        "the release module has no user-level concept at all. They therefore CANNOT be "
        "correlated per-person against per-person anchor labels the way S_c(u)/D_c(u) can; "
        "they are reported as three population-level descriptive snapshots (Big5-gate raw "
        "texts, MBTI-axis-covered raw texts, Essays-dev raw texts) in a clearly separate "
        "table, and play no role whatsoever in the primary classification grid or its BH-FDR.",
        "MBTI axis 'positive_probability' columns are hard 0/1 indicators (not fractional "
        "probabilities) confirmed empirically (crosstab against predicted_label is exactly "
        "diagonal); Pearson r against these is numerically a point-biserial correlation.",
    ]

    result = {
        "banner": BANNER,
        "registration": "F16, docs/SUICA_THEORY_FORMAL_NOTES_V3.md (registered 2026-07-12); "
                       "ledger row V6-F16",
        "governance": {
            "pandora_big5_gate": {"gate_n": len(gate_users), "gate_n_expected": 1058,
                                   "H2_recomputed": r_h2, "H6_recomputed": r_h6,
                                   "H2_H6_tolerance": "<1e-9, PASS (asserted; run would have "
                                                       "stopped on failure)"},
            "mbti_axes_first_use": {
                "banner_present": True,
                "note": "First correlational use of PANDORA MBTI axis labels against SUICA "
                        "constructs in this program; no prior replication target exists; "
                        "this run SPENDS these labels for future SUICA-correlational reuse "
                        "and itself becomes the reference point.",
                "n_mbti_users": n_mbti_users,
                "n_mbti_in_tier_l_uncapped": len(mbti_in_tier_l),
                "n_mbti_in_tier_u_uncapped": len(mbti_in_tier_u),
                "n_mbti_in_either_uncapped": len(mbti_in_either),
            },
            "essays_dev_half": {"two_pass_verified": True, "n_dev_ids": len(dev_ids),
                                "n_labels_loaded": len(labels_essays),
                                "confirm_half_bytes_parsed": False},
            "cap_sensitivity_check": cap_check,
        },
        "coverage": {
            "big5_gate": {"n_gate": len(gate_users),
                          "n_gate_in_tier_l_uncapped": len(gate_in_tier_l),
                          "n_static_covered": n_gate_static,
                          "n_dynamic_covered_m_ge_3": n_gate_dynamic},
            "mbti_axes": {"n_mbti_total": n_mbti_users,
                          "n_in_tier_l_or_tier_u_uncapped": len(mbti_in_either),
                          "n_static_covered": n_mbti_static,
                          "n_dynamic_covered_m_ge_3": n_mbti_dynamic},
            "essays_dev": {"n_dev_ids": len(dev_ids), "n_cache_coverage_m_ge_2": n_dev_cache,
                          "n_static_covered": len(essays_static),
                          "n_dynamic_covered_m_ge_3": len(essays_dynamic),
                          "diag_m_ge_3": essays_dyn_diag},
        },
        "constructs": cols,
        "dynamic_diagnostics_pandora_pool": dyn_diag,
        "grid": rows,
        "grid_summary": {
            "n_cells": n_cells,
            "n_cells_static_family": n_cells,
            "n_cells_dynamic_family": n_cells,
            "BOTH": len(both), "STATIC_ONLY": len(static_only),
            "DYNAMIC_ONLY": len(dynamic_only), "NEITHER": len(neither),
        },
        "standing_kill": {
            "triggered": standing_kill,
            "rule": "if DYNAMIC-ONLY count == 0 across the full grid, W10's finding demotes "
                    "from a general property of the construct space to an artifact of the "
                    "single hand-built gust1_P composite",
            "dynamic_only_constructs": dyn_only_constructs,
            "dynamic_only_in_w10_carrier_set": dyn_only_in_carrier_set,
            "w10_carrier_set": sorted(GUST1P_CARRIER_SET),
        },
        "registered_leans_check": {
            "a_most_static_only_or_neither": len(static_only) + len(neither),
            "b_dynamic_only_count_1_to_4_expected": len(dynamic_only),
            "c_both_rare_0_to_2_expected": len(both),
            "d_standing_kill_triggered": standing_kill,
        },
        "secondary_dynamics_descriptors_NOT_load_bearing": secondary,
        "ambiguities_and_design_decisions": ambiguities,
        "runtime_seconds": round(time.time() - t_start, 1),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, default=lambda o: None))
    print(f"written: {OUT_JSON}")

    # ---------------- Markdown ----------------
    md = ["# F16 -- Visibility taxonomy (EXPLORATORY, V6-F16)", "",
          f"> {BANNER}", "",
          "## Governance", "",
          f"- PANDORA Big5 gate: n={len(gate_users)} (expected 1058, PASS); H2={r_h2:.10f}, "
          f"H6={r_h6:.10f} vs published, both <1e-9 (PASS).",
          f"- MBTI axes: FIRST correlational use / label-spending event (no prior "
          f"replication target). {n_mbti_users} labeled users; "
          f"{len(mbti_in_either)} ({100*len(mbti_in_either)/n_mbti_users:.1f}%) found in "
          f"N1 uncapped tier_l/tier_u ({len(mbti_in_tier_l)} tier_l, "
          f"{len(mbti_in_tier_u)} tier_u).",
          f"- Essays dev-half: two-pass label-free split verified; {len(dev_ids)} dev ids, "
          f"confirm-half bytes never parsed.",
          f"- Cap-sensitivity check: n_common_users={cap_check['n_common_users']}; "
          f"{cap_check['result']}", "",
          "## Coverage", "",
          "| population | n total | static covered | dynamic (m>=3) covered |",
          "|---|---|---|---|",
          f"| Big5 gate | {len(gate_users)} | {n_gate_static} | {n_gate_dynamic} |",
          f"| MBTI axes | {n_mbti_users} | {n_mbti_static} | {n_mbti_dynamic} |",
          f"| Essays dev | {len(dev_ids)} | {len(essays_static)} | {len(essays_dynamic)} |",
          "", f"19 frozen constructs: {', '.join(cols)}", "",
          "## Classification summary", "",
          f"BOTH={len(both)}, STATIC-ONLY={len(static_only)}, "
          f"DYNAMIC-ONLY={len(dynamic_only)}, NEITHER={len(neither)} (of {n_cells} cells)", "",
          ("**STANDING KILL TRIGGERED**: zero DYNAMIC-ONLY cells -- W10's finding demotes "
           "from a general property to a single-composite artifact." if standing_kill else
           f"DYNAMIC-ONLY constructs: {dyn_only_constructs} (W10 carrier-set overlap: "
           f"{dyn_only_in_carrier_set})"), "",
          "## Full grid (construct x anchor x trait, both channels)", "",
          "| anchor | construct | trait | r_static | q_static | r_dynamic | q_dynamic | class |",
          "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['anchor']} | {r['construct']} | {r['trait']} | "
                  f"{r['r_static']:+.4f} | {r['q_static_bh']:.4f} | "
                  f"{r['r_dynamic']:+.4f} | {r['q_dynamic_bh']:.4f} | {r['classification']} |")
    md += ["", "## Secondary, exploratory-of-exploratory descriptors (population-pooled, "
               "NOT load-bearing, NOT part of classification)", ""]
    for name, mp in secondary.items():
        md.append(f"### {name}")
        md.append(f"n_texts_used={mp['n_texts_used']}, n_texts_dropped={mp['n_texts_dropped']}, "
                  f"n_windows={mp['n_windows']}, gamma0_reason={mp['gamma0_reason']}, "
                  f"period2_reason={mp['period2_reason']}")
        if mp["memory_by_construct"] is not None:
            md.append("| construct | signed memory r_c | rho_pi_half | rho_pi |")
            md.append("|---|---|---|")
            shape = mp["spectral_shape_by_construct"]
            for i, c in enumerate(cols):
                mem = mp["memory_by_construct"][i]
                if shape is not None:
                    ph, pi = shape[i]
                else:
                    ph, pi = None, None
                md.append(f"| {c} | {mem:+.4f} | {ph if ph is None else f'{ph:.4f}'} | "
                          f"{pi if pi is None else f'{pi:.4f}'} |")
        md.append("")
    md += ["## Ambiguities / design decisions", ""]
    md += [f"- {a}" for a in ambiguities]
    OUT_MD.write_text("\n".join(md) + "\n")
    print(f"written: {OUT_MD}")
    print(f"[done] total runtime {time.time() - t_start:.1f}s")


if __name__ == "__main__":
    main()
