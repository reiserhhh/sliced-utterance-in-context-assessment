#!/usr/bin/env python
"""X1 — cross-fitted rescue-or-burial of the motion layer's three person-level legs
(F18, registered 2026-07-17 BEFORE run, research-repo commit c029684,
docs/SUICA_THEORY_FORMAL_NOTES_V3.md "## F18 — X1"; release-repo ledger row V7.5-X1,
commit 3a6f5b9). Label-free throughout; zero new data.

The three legs and their original same-sample results:
  1. W10 person susceptibility on gust1_P: split-half r=.441 (ICC-share .381, n=81)
     — audited flaws: cid-parity split, same-sample axis fit, selection-optimism-
     uncorrected null, no matched-stranger / opportunity controls (release
     docs/V7_W10_AUDIT.md).
  2. TGEO-P9 B-gust1: lam 2.223 >> edge 1.386, person-disjoint half replication
     .829, level visibility 0.972 (statically invisible).
  3. V6-E4 gate>=8 residualized comp1: lam 2.137, half replication .784, static
     congruence <= .03.

BINDING DESIGN (F18, not weakened here):
 (i)  Deterministic stable hash split of AUTHORS into DISCOVERY / EVALUATION
      halves via suica_core.factor_discovery.stable_user_split (sha256 of
      salt::user_id, salt "suica-v6-factor-v1"; "confirmation" == EVALUATION).
      ALL axis/factor/eigenvector estimation happens on DISCOVERY authors only;
      EVERY person-level statistic is computed ONLY on EVALUATION authors.
 (ii) Within evaluation authors, split-half statistics use RANDOM half-splits over
      each author's texts (never cid-parity), mean over N_SPLITS=50 seeded splits.
 (iii) W10's stability gets a MATCHED-STRANGER null: author-shuffled pseudo-persons
      matched exactly on text counts (permuting the per-text author-label column
      preserves every author's text count), N_NULL=200 draws, in three variants:
      unstratified, SUBREDDIT-stratified (venue-matched, design iv), and
      m-bin-stratified (opportunity-matched). Venue comes from a deterministic
      cid->subreddit rebuild of the exact candidate frames the window builders
      enumerated (verified by author equality on every scored cid).
 (iv) Axis-selection-in-the-null (audit ground 3): under cross-fitting the axis is
      estimated on authors disjoint from every evaluation statistic, so the null
      need not refit the axis — the selection step had no contact with the
      evaluation sample by construction. Stated, not assumed silently.
 (v)  Capped (P8 cache) and uncapped (F16 pool) arms run separately; the UNCAPPED
      arm is the primary adjudication arm (deeper coverage, avoids the W9/EXPL-3
      cap artifact; the capped arm's W10 evaluation cohort is ~40 authors, far too
      thin to adjudicate a burial honestly). This primacy choice is an
      adjudication decision made at write time, before any number was seen, and
      is recorded here and in the output.

Per-leg adjudication (F18): BURIAL if the cross-fitted headline CI includes 0 OR
the matched-stranger/shuffle null absorbs it (p >= .05). Leans: W10 in [.15,.30]
with CI>0; P9 survives (supra-edge + held-out replication >= .6); E4 attenuates to
replication [.5,.7]. STANDING KILL: all three bury.

Bootstrap: person-level cluster bootstrap over EVALUATION authors, N_BOOT=500.

Reads only existing caches/parquets; writes only results/suica_x1_crossfit_motion/.
No git operations. Seed: 20260717 (registration date).
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

# research-repo scripts.* imports FIRST (F16-established shadowing-hazard pattern:
# both repos ship a same-named PEP-420 "scripts" namespace package; RELEASE_ROOT
# is appended at the END so these resolve against the frozen research-repo copies)
import scripts.run_suica_v6_w2a_delta2_dynamics_v1 as w2a  # noqa: E402
import scripts.run_suica_v6_w10_invisible_anatomy_v1 as w10  # noqa: E402
import scripts.run_suica_tgeo_p9_flow_only_factors_v1 as p9mod  # noqa: E402

RELEASE_ROOT = Path("/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment")
if str(RELEASE_ROOT) not in sys.path:
    sys.path.append(str(RELEASE_ROOT))
from suica_core.factor_discovery import stable_user_split  # noqa: E402

SEED = 20260717
N_SPLITS = 50          # random half-splits per split-half statistic (design ii)
N_NULL = 200           # matched-stranger draws (design iii; >=200 per F18)
N_BOOT = 500           # author-cluster bootstrap draws
N_SHUF_Q = 500         # within-column shuffle draws for fixed-vector quadratic forms
N_VIS = 200            # level-visibility shuffle draws (matches P9 original)

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
UNCAPPED_POOL = ROOT / "results" / "suica_f16_visibility_taxonomy" / "pandora_uncapped_windows_scored19.parquet"
CAPPED_CACHE = ROOT / "results" / "suica_tgeo_p8_functionalization" / "cache_windows_scored19.parquet"
OUT_DIR = ROOT / "results" / "suica_x1_crossfit_motion"
OUT_JSON = OUT_DIR / "X1_CROSSFIT_MOTION.json"
OUT_MD = OUT_DIR / "X1_CROSSFIT_MOTION.md"

CHAR_CANDIDATE = 1200  # same threshold as p7.build_windows / F16 uncapped builder


def jf(x):
    if x is None:
        return None
    xf = float(x)
    return round(xf, 6) if np.isfinite(xf) else None


# ============================================================================
# Venue (subreddit) rebuild: cid in both caches is the ENUMERATION POSITION over
# the length-filtered candidate frame (p7.build_windows for the capped cache;
# F16 load_pandora_uncapped_candidates for the uncapped pool). Rebuilding the
# same candidate frame with subreddit gives a deterministic cid -> subreddit map,
# verified by author equality on every scored cid.
# ============================================================================

def venue_map_capped() -> pd.DataFrame:
    comments = pd.read_parquet(TIER_DIR / "tier_u_comments.parquet",
                               columns=["author", "body", "subreddit"])
    comments["author"] = comments["author"].astype(str)
    body = comments["body"].astype(str)
    cand = comments.loc[body.str.len() >= CHAR_CANDIDATE].reset_index(drop=True)
    out = cand[["author", "subreddit"]].copy()
    out.index.name = "cid"
    return out


def venue_map_uncapped() -> pd.DataFrame:
    frames = []
    for name in ("tier_l_comments_uncapped_v1.parquet", "tier_u_comments_uncapped_v1.parquet"):
        df = pd.read_parquet(TIER_DIR / name, columns=["author", "body", "subreddit"])
        df["author"] = df["author"].astype(str)
        frames.append(df)
    comments = pd.concat(frames, ignore_index=True)
    body = comments["body"].astype(str)
    cand = comments.loc[body.str.len() >= CHAR_CANDIDATE].reset_index(drop=True)
    out = cand[["author", "subreddit"]].copy()
    out.index.name = "cid"
    return out


def verify_venue(df: pd.DataFrame, venue: pd.DataFrame, arm: str) -> pd.Series:
    """Return cid -> subreddit for every cid in df, after verifying the rebuild's
    author matches the cache's user_id on EVERY scored cid."""
    per_cid = df.groupby("cid")["user_id"].first()
    assert per_cid.index.max() < len(venue), f"[{arm}] cid beyond rebuilt candidate frame"
    rebuilt_author = venue["author"].reindex(per_cid.index)
    n_bad = int((rebuilt_author.to_numpy() != per_cid.to_numpy()).sum())
    assert n_bad == 0, f"[{arm}] venue rebuild author mismatch on {n_bad} cids"
    return venue["subreddit"].reindex(per_cid.index)


# ============================================================================
# Random split-half machinery (design ii)
# ============================================================================

def split_half_means(ucode: np.ndarray, val: np.ndarray, n_users: int,
                     rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """One random half-split of each user's texts; returns per-user half means.
    Every user has >=2 texts, so both halves are nonempty for every user."""
    n = len(val)
    order = np.lexsort((rng.random(n), ucode))
    counts = np.bincount(ucode, minlength=n_users)
    starts = np.concatenate(([0], np.cumsum(counts)[:-1]))
    pos = np.arange(n) - starts[ucode[order]]
    half = np.empty(n, dtype=np.int8)
    half[order] = (pos % 2).astype(np.int8)
    w0 = (half == 0).astype(float)
    w1 = 1.0 - w0
    c0 = np.bincount(ucode, weights=w0, minlength=n_users)
    c1 = np.bincount(ucode, weights=w1, minlength=n_users)
    s0 = np.bincount(ucode, weights=val * w0, minlength=n_users)
    s1 = np.bincount(ucode, weights=val * w1, minlength=n_users)
    return s0 / np.maximum(c0, 1), s1 / np.maximum(c1, 1)


def pearson_1d(a: np.ndarray, b: np.ndarray) -> float:
    sa, sb = a.std(), b.std()
    if sa == 0 or sb == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def mean_split_half_r(ucode, val, n_users, rng, n_splits=N_SPLITS,
                      return_halves=False):
    rs = np.empty(n_splits)
    halves0 = np.empty((n_users, n_splits)) if return_halves else None
    halves1 = np.empty((n_users, n_splits)) if return_halves else None
    for s in range(n_splits):
        m0, m1 = split_half_means(ucode, val, n_users, rng)
        rs[s] = pearson_1d(m0, m1)
        if return_halves:
            halves0[:, s] = m0
            halves1[:, s] = m1
    if return_halves:
        return rs, halves0, halves1
    return rs


def permute_within_strata(labels: np.ndarray, strata: np.ndarray,
                          rng: np.random.Generator) -> np.ndarray:
    """Permute `labels` within each stratum (single stratum -> full permutation)."""
    n = len(labels)
    idx_sorted = np.lexsort((np.arange(n), strata))
    idx_shuffled = np.lexsort((rng.random(n), strata))
    out = np.empty_like(labels)
    out[idx_sorted] = labels[idx_shuffled]
    return out


# ============================================================================
# Shared eigen helpers (reused from the original P9 script where importable)
# ============================================================================

corr_guarded = p9mod.corr_guarded
top_eigs = p9mod.top_eigs
shuffle_edge = p9mod.shuffle_edge
visibility = p9mod.visibility
top_loadings = p9mod.top_loadings


def qform_shuffle_null(v: np.ndarray, X: np.ndarray, rng, n=N_SHUF_Q):
    """v' corr(X) v observed vs within-column shuffles of X (the fixed vector v
    was estimated on author-disjoint DISCOVERY data, so this null is calibrated
    without refitting the selection step — see module docstring, design iv)."""
    obs = float(v @ corr_guarded(X) @ v)
    null = np.empty(n)
    for b in range(n):
        Xs = X.copy()
        for j in range(X.shape[1]):
            rng.shuffle(Xs[:, j])
        null[b] = float(v @ corr_guarded(Xs) @ v)
    p = float((1 + (null >= obs).sum()) / (1 + n))
    return obs, float(np.percentile(null, 95)), p, null


def cluster_boot_qform(v: np.ndarray, X: np.ndarray, clusters: np.ndarray,
                       rng, n_boot=N_BOOT):
    """Author-cluster bootstrap of v' corr(X) v - 1 (excess co-movement along the
    discovery-fitted axis). Resamples unique clusters with replacement."""
    uniq, inv = np.unique(clusters, return_inverse=True)
    idx_by_c = [np.where(inv == k)[0] for k in range(len(uniq))]
    stats = np.empty(n_boot)
    for b in range(n_boot):
        pick = rng.integers(0, len(uniq), len(uniq))
        rows = np.concatenate([idx_by_c[k] for k in pick])
        stats[b] = float(v @ corr_guarded(X[rows]) @ v) - 1.0
    return [float(np.percentile(stats, 2.5)), float(np.percentile(stats, 97.5))], stats


def cluster_boot_congruence(v_disc: np.ndarray, X: np.ndarray, clusters: np.ndarray,
                            rng, n_boot=N_BOOT):
    """Author-cluster bootstrap of |v_disc . top-eig(corr(X_boot))|."""
    uniq, inv = np.unique(clusters, return_inverse=True)
    idx_by_c = [np.where(inv == k)[0] for k in range(len(uniq))]
    stats = np.empty(n_boot)
    for b in range(n_boot):
        pick = rng.integers(0, len(uniq), len(uniq))
        rows = np.concatenate([idx_by_c[k] for k in pick])
        _, V = top_eigs(corr_guarded(X[rows]), 1)
        stats[b] = abs(float(v_disc @ V[:, 0]))
    return [float(np.percentile(stats, 2.5)), float(np.percentile(stats, 97.5))], stats


# ============================================================================
# Leg 1 — W10 person susceptibility, cross-fitted
# ============================================================================

def w10_leg(df: pd.DataFrame, cols: list, subreddit_by_cid: pd.Series,
            arm: str, rng: np.random.Generator) -> dict:
    disc = df[df["_half"] == "discovery"]
    ev = df[df["_half"] == "confirmation"]

    # --- axis on DISCOVERY authors only (same recipe as the original: W2a's
    # compute_gust1_p, m==3 exact texts — but restricted to discovery authors) ---
    v_raw, eig, n_src = w2a.compute_gust1_p(disc, cols)
    v = v_raw / np.linalg.norm(v_raw)
    order = np.argsort(-np.abs(v))
    top2 = sorted({cols[i] for i in order[:2]})
    guard_pass = set(top2) == {"wcl_02", "wcl_11"}

    # --- discovery pooled residual sd (cross-fit standardization scale) ---
    sub_d = disc[disc["m"] >= 3].sort_values(["cid", "j"]).reset_index(drop=True)
    _, sd_disc = w10.within_text_linear_residuals(sub_d, "cid", cols)
    sd_disc_g = np.where(sd_disc > 0, sd_disc, 1.0)

    # --- evaluation activations (per-text detrend is within-text; the only
    # cross-person quantities — axis and standardization sds — come from discovery) ---
    sub_e = ev[ev["m"] >= 3].sort_values(["cid", "j"]).reset_index(drop=True)
    resid_std_e, sd_e = w10.within_text_linear_residuals(sub_e, "cid", cols)
    resid_raw_e = resid_std_e * np.where(sd_e > 0, sd_e, 1.0)
    a = (resid_raw_e / sd_disc_g) @ v

    # --- per-text mean |a| for evaluation authors with >= 2 qualifying texts ---
    pt = (pd.DataFrame({"user_id": sub_e["user_id"].to_numpy(),
                        "cid": sub_e["cid"].to_numpy(),
                        "m": sub_e["m"].to_numpy(),
                        "abs_a": np.abs(a)})
          .groupby(["user_id", "cid"], sort=False)
          .agg(mean_abs_a=("abs_a", "mean"), m=("m", "first")).reset_index())
    ucnt = pt.groupby("user_id")["cid"].size()
    keep = ucnt.index[ucnt >= 2]
    pt = pt[pt["user_id"].isin(keep)].reset_index(drop=True)
    ucode, uniq_users = pd.factorize(pt["user_id"])
    ucode = ucode.astype(np.int64)
    n_users = len(uniq_users)
    val = pt["mean_abs_a"].to_numpy(float)
    sub_lab = subreddit_by_cid.reindex(pt["cid"]).to_numpy()
    strat_sub, _ = pd.factorize(sub_lab)
    strat_m = np.minimum(pt["m"].to_numpy(int), 6)  # m-bins: 3,4,5,6+

    # stratum mobility coverage
    def coverage(strata):
        s = pd.DataFrame({"s": strata, "u": ucode})
        sz = s.groupby("s")["u"].agg(["size", "nunique"])
        movable = sz.loc[sz["nunique"] >= 2, "size"].sum()
        return float(movable / len(s))

    cov_sub = coverage(strat_sub)
    cov_m = coverage(strat_m)

    # --- headline: mean over N_SPLITS random half-splits (design ii) ---
    rs, h0, h1 = mean_split_half_r(ucode, val, n_users,
                                   np.random.default_rng(rng.integers(2**63)),
                                   return_halves=True)
    headline = float(np.nanmean(rs))

    # --- ICC-style share on evaluation authors ---
    umeans = np.bincount(ucode, weights=val) / np.bincount(ucode)
    icc_share = float(np.var(umeans) / np.var(val)) if np.var(val) > 0 else float("nan")

    # --- author-cluster bootstrap CI of the headline (fixed 50 splits;
    # resampling prices author-sampling variance, the dominant term) ---
    brng = np.random.default_rng(rng.integers(2**63))
    boot = np.empty(N_BOOT)
    for b in range(N_BOOT):
        idx = brng.integers(0, n_users, n_users)
        A = h0[idx] - h0[idx].mean(0)
        B = h1[idx] - h1[idx].mean(0)
        den = np.sqrt((A * A).sum(0) * (B * B).sum(0))
        with np.errstate(invalid="ignore", divide="ignore"):
            rcols = (A * B).sum(0) / den
        boot[b] = float(np.nanmean(rcols))
    ci = [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]

    # --- matched-stranger nulls (design iii/iv): permute author labels over
    # per-text rows (text counts exactly preserved), 3 variants ---
    nulls = {}
    for name, strata in [("count_matched", np.zeros(len(val), dtype=int)),
                         ("subreddit_matched", strat_sub),
                         ("mbin_matched", strat_m)]:
        nrng = np.random.default_rng(rng.integers(2**63))
        draws = np.empty(N_NULL)
        for b in range(N_NULL):
            uc_perm = permute_within_strata(ucode, strata, nrng)
            draws[b] = float(np.nanmean(mean_split_half_r(uc_perm, val, n_users,
                                                          nrng, n_splits=N_SPLITS)))
        p = float((1 + (draws >= headline).sum()) / (1 + N_NULL))
        nulls[name] = {"p": jf(p), "null_mean": jf(draws.mean()),
                       "null_p95": jf(np.percentile(draws, 95)), "n_draws": N_NULL}
    op_p = max(nulls[k]["p"] for k in nulls)  # most conservative absorption test

    # --- cid-parity reference (the ORIGINAL banned estimator, on eval authors,
    # for bridge comparison only — NOT a headline) ---
    parity_ref = w10.person_susceptibility(sub_e, a, "cid")

    # --- opportunity correlates ---
    un_texts = np.bincount(ucode).astype(float)
    umean_logm = (np.bincount(ucode, weights=np.log(pt["m"].to_numpy(float)))
                  / np.bincount(ucode))
    r_ntexts = pearson_1d(umeans, un_texts)
    r_logm = pearson_1d(umeans, umean_logm)

    buried = (ci[0] <= 0.0) or (op_p >= 0.05)
    res = {
        "arm": arm,
        "axis": {"top_eigenvalue": jf(eig), "n_source_m3_texts": int(n_src),
                 "top2_constructs": top2, "w10_drift_guard_would_pass": bool(guard_pass),
                 "top_loadings": top_loadings(v, cols)},
        "n_eval_users": int(n_users), "n_eval_texts": int(len(pt)),
        "headline_mean_split_half_r": jf(headline),
        "split_r_sd_over_splits": jf(np.nanstd(rs)),
        "boot_ci95": [jf(ci[0]), jf(ci[1])], "n_boot": N_BOOT,
        "icc_share_abs_a": jf(icc_share),
        "stranger_nulls": nulls,
        "operative_stranger_p": jf(op_p),
        "stratum_mobility": {"subreddit": jf(cov_sub), "mbin": jf(cov_m)},
        "cid_parity_reference_banned": {k: parity_ref[k] for k in
                                        ("n_users", "r_susceptibility", "icc_share_abs_a")},
        "opportunity": {"r_usermean_vs_n_texts": jf(r_ntexts),
                        "r_usermean_vs_mean_log_m": jf(r_logm)},
        "buried": bool(buried),
    }
    print(f"[W10 {arm}] axis-eig={eig:.3f} (disc n={n_src}) eval users={n_users} "
          f"texts={len(pt)} headline r={headline:.4f} CI={ci} "
          f"stranger p: {[(k, nulls[k]['p']) for k in nulls]} buried={buried}")
    return res


# ============================================================================
# Leg 2 — TGEO-P9 B-gust1, cross-fitted
# ============================================================================

def m3_blocks(part: pd.DataFrame, cols: list):
    m3 = part[part["m"] == 3]
    cnt = m3.groupby("cid").size()
    m3 = m3[m3["cid"].isin(cnt.index[cnt == 3])].sort_values(["cid", "j"])
    W = m3[cols].to_numpy(float).reshape(-1, 3, len(cols))
    users = m3.groupby("cid")["user_id"].first().to_numpy()
    return W, users


def p9_leg(df: pd.DataFrame, cols: list, arm: str, rng: np.random.Generator) -> dict:
    disc = df[df["_half"] == "discovery"]
    ev = df[df["_half"] == "confirmation"]
    Wd, ud = m3_blocks(disc, cols)
    We, ue = m3_blocks(ev, cols)
    # curvature contrasts; the per-column sd scaling of the original is irrelevant
    # to every correlation-based statistic below (corr_guarded re-standardizes
    # columns), so raw contrasts are used and this invariance is stated.
    cur_d = (Wd[:, 0, :] - 2 * Wd[:, 1, :] + Wd[:, 2, :]) / np.sqrt(6.0)
    cur_e = (We[:, 0, :] - 2 * We[:, 1, :] + We[:, 2, :]) / np.sqrt(6.0)
    L_e = We.mean(axis=1)

    lam_d, Vd = top_eigs(corr_guarded(cur_d), 3)
    v_disc = Vd[:, 0]

    lam_e, Ve = top_eigs(corr_guarded(cur_e), 3)
    edge_e = shuffle_edge(cur_e, np.random.default_rng(rng.integers(2**63)))
    rep_top1 = abs(float(v_disc @ Ve[:, 0]))
    rep_max3 = max(abs(float(v_disc @ Ve[:, j])) for j in range(3))

    qrng = np.random.default_rng(rng.integers(2**63))
    q_obs, q_null95, q_p, _ = qform_shuffle_null(v_disc, cur_e, qrng)
    ci, _ = cluster_boot_qform(v_disc, cur_e, ue,
                               np.random.default_rng(rng.integers(2**63)))
    rep_ci, _ = cluster_boot_congruence(v_disc, cur_e, ue,
                                        np.random.default_rng(rng.integers(2**63)))
    vis, vis95 = visibility(v_disc, L_e, np.random.default_rng(rng.integers(2**63)),
                            n=N_VIS)
    level_invisible = bool(vis <= vis95)

    supra_edge = bool(q_p < 0.05)          # fixed-discovery-vector null (primary)
    supra_edge_lam = bool(lam_e[0] > edge_e)  # selection-repeating eval null (secondary)
    buried = (ci[0] <= 0.0) or (q_p >= 0.05)
    res = {
        "arm": arm,
        "n_disc_m3_texts": int(len(cur_d)), "n_eval_m3_texts": int(len(cur_e)),
        "n_eval_users": int(pd.unique(ue).size),
        "disc_gust1_lambda": jf(lam_d[0]),
        "disc_gust1_top_loadings": top_loadings(v_disc, cols),
        "eval_lambda1": jf(lam_e[0]), "eval_shuffle_edge": jf(edge_e),
        "supra_edge_lam_secondary": supra_edge_lam,
        "heldout_replication_top1": jf(rep_top1),
        "heldout_replication_max3": jf(rep_max3),
        "heldout_replication_boot_ci95": [jf(rep_ci[0]), jf(rep_ci[1])],
        "qform_obs": jf(q_obs), "qform_null95": jf(q_null95), "qform_p": jf(q_p),
        "qform_excess_boot_ci95": [jf(ci[0]), jf(ci[1])], "n_boot": N_BOOT,
        "level_visibility_obs": jf(vis), "level_visibility_null95": jf(vis95),
        "level_invisibility_ok": level_invisible,
        "supra_edge": supra_edge,
        "buried": bool(buried),
    }
    print(f"[P9 {arm}] disc lam={lam_d[0]:.3f} eval lam1={lam_e[0]:.3f} "
          f"(edge {edge_e:.3f}) rep={rep_top1:.3f} qform={q_obs:.3f} "
          f"(null95 {q_null95:.3f}, p={q_p:.4f}) excessCI={ci} vis={vis:.3f} "
          f"(null95 {vis95:.3f}) buried={buried}")
    return res


# ============================================================================
# Leg 3 — V6-E4 person motion style, cross-fitted (gate>=8 residualized comp1
# is the adjudicated headline; gate>=5 reported as context)
# ============================================================================

def e4_leg(df: pd.DataFrame, cols: list, arm: str, rng: np.random.Generator,
           gate: int) -> dict:
    g = df.sort_values(["cid", "j"]).groupby("cid")
    D = g[cols].last().to_numpy(float) - g[cols].first().to_numpy(float)
    L = g[cols].mean().to_numpy(float)
    users = g["user_id"].first().to_numpy()
    halves = g["_half"].first().to_numpy()

    dfD = pd.DataFrame(D, columns=cols).assign(user_id=users, _half=halves)
    dfL = pd.DataFrame(L, columns=cols).assign(user_id=users, _half=halves)
    ucnt = dfD["user_id"].value_counts()
    keep = ucnt.index[ucnt >= gate]

    def user_means(part_D, part_L, half):
        mD = (part_D[(part_D["user_id"].isin(keep)) & (part_D["_half"] == half)]
              .groupby("user_id")[cols].mean())
        mL = (part_L[(part_L["user_id"].isin(keep)) & (part_L["_half"] == half)]
              .groupby("user_id")[cols].mean())
        assert list(mD.index) == list(mL.index)
        return mD.to_numpy(float), mL.to_numpy(float), mD.index.to_numpy()

    uD_d, uL_d, _ = user_means(dfD, dfL, "discovery")
    uD_e, uL_e, users_e = user_means(dfD, dfL, "confirmation")

    # discovery-only estimation: standardization stats, static top-4 frame,
    # residualization, comp1 eigenvector
    muD, sdD = uD_d.mean(0), uD_d.std(0)
    sdD_g = np.where(sdD > 0, sdD, 1.0)
    _, V4L_d = top_eigs(corr_guarded(uL_d), 4)
    P = V4L_d @ V4L_d.T
    ZD_d = (uD_d - muD) / sdD_g
    R_d = ZD_d - ZD_d @ P
    lam_d, Vr_d = top_eigs(corr_guarded(R_d), 3)
    v_disc = Vr_d[:, 0]

    # evaluation side: discovery stats and discovery frame applied, then held-out
    # statistics only
    ZD_e = (uD_e - muD) / sdD_g
    R_e = ZD_e - ZD_e @ P
    lam_e, Vr_e = top_eigs(corr_guarded(R_e), 3)
    edge_e = shuffle_edge(R_e, np.random.default_rng(rng.integers(2**63)))
    rep_top1 = abs(float(v_disc @ Vr_e[:, 0]))
    rep_max3 = max(abs(float(v_disc @ Vr_e[:, j])) for j in range(3))
    _, V4L_e = top_eigs(corr_guarded(uL_e), 4)
    static_congr_eval = max(abs(float(v_disc @ V4L_e[:, j])) for j in range(4))
    static_congr_disc = max(abs(float(v_disc @ V4L_d[:, j])) for j in range(4))

    qrng = np.random.default_rng(rng.integers(2**63))
    q_obs, q_null95, q_p, _ = qform_shuffle_null(v_disc, R_e, qrng)
    ci, _ = cluster_boot_qform(v_disc, R_e, users_e,
                               np.random.default_rng(rng.integers(2**63)))
    rep_ci, _ = cluster_boot_congruence(v_disc, R_e, users_e,
                                        np.random.default_rng(rng.integers(2**63)))

    buried = (ci[0] <= 0.0) or (q_p >= 0.05)
    res = {
        "arm": arm, "gate": gate,
        "n_disc_users": int(len(uD_d)), "n_eval_users": int(len(uD_e)),
        "disc_comp1_lambda": jf(lam_d[0]),
        "disc_comp1_top_loadings": top_loadings(v_disc, cols),
        "eval_lambda1": jf(lam_e[0]), "eval_shuffle_edge": jf(edge_e),
        "supra_edge_lam_secondary": bool(lam_e[0] > edge_e),
        "heldout_replication_top1": jf(rep_top1),
        "heldout_replication_max3": jf(rep_max3),
        "heldout_replication_boot_ci95": [jf(rep_ci[0]), jf(rep_ci[1])],
        "static_congruence_eval_frame": jf(static_congr_eval),
        "static_congruence_disc_frame": jf(static_congr_disc),
        "qform_obs": jf(q_obs), "qform_null95": jf(q_null95), "qform_p": jf(q_p),
        "qform_excess_boot_ci95": [jf(ci[0]), jf(ci[1])], "n_boot": N_BOOT,
        "buried": bool(buried),
    }
    print(f"[E4 {arm} gate>={gate}] disc lam={lam_d[0]:.3f} eval lam1={lam_e[0]:.3f} "
          f"(edge {edge_e:.3f}) rep={rep_top1:.3f} static(eval)={static_congr_eval:.3f} "
          f"qform={q_obs:.3f} (null95 {q_null95:.3f}, p={q_p:.4f}) excessCI={ci} "
          f"buried={buried}")
    return res


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    arms = {}
    for arm, path in (("uncapped", UNCAPPED_POOL), ("capped", CAPPED_CACHE)):
        df = pd.read_parquet(path)
        df["user_id"] = df["user_id"].astype(str)
        split = {u: stable_user_split(u) for u in df["user_id"].unique()}
        df["_half"] = df["user_id"].map(split)
        arms[arm] = df
        vc = df.groupby("_half")["user_id"].nunique().to_dict()
        print(f"[{arm}] {len(df)} windows, {df['user_id'].nunique()} users "
              f"({df['cid'].nunique()} texts); split {vc}")

    cols = [c for c in w2a.get_construct_cols(arms["uncapped"]) if c != "_half"]
    cols_c = [c for c in w2a.get_construct_cols(arms["capped"]) if c != "_half"]
    assert cols == cols_c and len(cols) == 19, "construct column mismatch"

    print("[venue] rebuilding cid->subreddit maps (deterministic candidate re-enumeration)...")
    venue_u = venue_map_uncapped()
    venue_c = venue_map_capped()
    sub_by_cid_u = verify_venue(arms["uncapped"], venue_u, "uncapped")
    sub_by_cid_c = verify_venue(arms["capped"], venue_c, "capped")
    print(f"[venue] verified: uncapped {sub_by_cid_u.notna().sum()} cids, "
          f"capped {sub_by_cid_c.notna().sum()} cids (author equality asserted)")

    result: dict = {"meta": {
        "registered_ref": "F18 (X1), research repo commit c029684, "
                          "docs/SUICA_THEORY_FORMAL_NOTES_V3.md; release ledger V7.5-X1, "
                          "commit 3a6f5b9",
        "seed": SEED, "n_splits": N_SPLITS, "n_stranger_null": N_NULL,
        "n_boot": N_BOOT, "n_qform_shuffle": N_SHUF_Q,
        "split_fn": "suica_core.factor_discovery.stable_user_split "
                    "(sha256 salt 'suica-v6-factor-v1'; 'confirmation' = EVALUATION)",
        "primary_arm": "uncapped",
        "primary_arm_rationale": "chosen before any number was computed: deeper "
            "coverage (4602 vs 3622 users; capped W10 evaluation cohort is ~40 "
            "authors — a burial there would be an artifact of induced underpower), "
            "and the capped extraction carries the W9/EXPL-3 cap artifact the F16 "
            "line already moved away from. Capped arm reported in full as the "
            "cap-sensitivity arm.",
        "originals": {
            "w10": {"r": 0.441, "icc_share": 0.381, "n": 81},
            "p9_bgust1": {"lam": 2.223, "edge": 1.386, "half_rep": 0.829,
                          "level_visibility": 0.972},
            "e4_gate8_resid_comp1": {"lam": 2.137, "rep": 0.784,
                                     "static_congruence": 0.03},
        },
    }, "legs": {"w10": {}, "p9": {}, "e4": {}}}

    for arm in ("uncapped", "capped"):
        df = arms[arm]
        sub_by_cid = sub_by_cid_u if arm == "uncapped" else sub_by_cid_c
        result["legs"]["w10"][arm] = w10_leg(df, cols, sub_by_cid, arm, rng)
        result["legs"]["p9"][arm] = p9_leg(df, cols, arm, rng)
        result["legs"]["e4"][arm] = {
            f"gate{gate}": e4_leg(df, cols, arm, rng, gate) for gate in (8, 5)}

    # ---------------- adjudication (primary arm = uncapped) ----------------
    w = result["legs"]["w10"]["uncapped"]
    p = result["legs"]["p9"]["uncapped"]
    e = result["legs"]["e4"]["uncapped"]["gate8"]

    w_lean = (w["boot_ci95"][0] is not None and w["boot_ci95"][0] > 0
              and 0.15 <= w["headline_mean_split_half_r"] <= 0.30)
    p_lean = bool(p["supra_edge"] and p["heldout_replication_top1"] >= 0.6
                  and not p["buried"])
    e_lean = (not e["buried"]
              and 0.5 <= e["heldout_replication_top1"] <= 0.7)
    standing_kill = bool(w["buried"] and p["buried"] and e["buried"])

    result["adjudication"] = {
        "per_leg": {
            "w10": {"buried": w["buried"],
                    "headline": w["headline_mean_split_half_r"],
                    "ci95": w["boot_ci95"],
                    "stranger_p_operative": w["operative_stranger_p"],
                    "lean_a_hit": bool(w_lean)},
            "p9": {"buried": p["buried"],
                   "heldout_replication": p["heldout_replication_top1"],
                   "supra_edge": p["supra_edge"],
                   "level_invisibility_ok": p["level_invisibility_ok"],
                   "lean_b_hit": bool(p_lean)},
            "e4": {"buried": e["buried"],
                   "heldout_replication": e["heldout_replication_top1"],
                   "static_congruence": e["static_congruence_eval_frame"],
                   "lean_c_hit": bool(e_lean)},
        },
        "standing_kill_fires": standing_kill,
        "standing_kill_meaning": "if true: the motion-layer person-level program is "
            "recorded as a same-sample artifact family and T8-prime's kernel-rank "
            "evidentiary base drops to ZERO certified instruments pending the "
            "native corpus (F18 wording; not softened).",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2))
    write_md(result)
    print(f"\nwritten: {OUT_JSON}\nwritten: {OUT_MD}")
    print(f"standing kill fires: {standing_kill}")


def write_md(result: dict) -> None:
    a = result["adjudication"]
    md = ["# X1 — cross-fitted rescue-or-burial of the motion layer's three "
          "person-level legs",
          "",
          f"Registered: {result['meta']['registered_ref']}. Seed "
          f"{result['meta']['seed']}. Primary adjudication arm: "
          f"**{result['meta']['primary_arm']}** "
          f"({result['meta']['primary_arm_rationale']})", ""]

    md += ["## Adjudication summary (primary arm)", "",
           "| leg | buried | headline | F18 lean | lean hit |",
           "|---|---|---|---|---|"]
    w, p, e = a["per_leg"]["w10"], a["per_leg"]["p9"], a["per_leg"]["e4"]
    md += [
        f"| W10 susceptibility | {w['buried']} | mean split-half r = {w['headline']} "
        f"CI {w['ci95']}, stranger p = {w['stranger_p_operative']} | r in [.15,.30], CI>0 "
        f"| {w['lean_a_hit']} |",
        f"| TGEO-P9 B-gust1 | {p['buried']} | held-out replication = "
        f"{p['heldout_replication']}, supra-edge = {p['supra_edge']}, level-invisible = "
        f"{p['level_invisibility_ok']} | survives (supra-edge + rep >= .6) | {p['lean_b_hit']} |",
        f"| V6-E4 comp1 (gate>=8 resid) | {e['buried']} | held-out replication = "
        f"{e['heldout_replication']}, static congruence = {e['static_congruence']} | "
        f"rep in [.5,.7] | {e['lean_c_hit']} |",
        "",
        f"**STANDING KILL fires: {a['standing_kill_fires']}** — "
        f"{a['standing_kill_meaning']}", ""]

    for leg, title in (("w10", "Leg 1 — W10 person susceptibility"),
                       ("p9", "Leg 2 — TGEO-P9 B-gust1"),
                       ("e4", "Leg 3 — V6-E4 person motion style")):
        md += [f"## {title}", ""]
        for arm in ("uncapped", "capped"):
            block = result["legs"][leg][arm]
            md += [f"### {arm} arm", "", "```json",
                   json.dumps(block, indent=2), "```", ""]

    md += ["## Design notes / compromises", ""]
    md += [f"- {n}" for n in [
        "Author split: suica_core.factor_discovery.stable_user_split (sha256 of "
        "'suica-v6-factor-v1::user_id' mod 2); 'confirmation' half = EVALUATION. All "
        "axis/eigenvector/frame/standardization estimation on DISCOVERY authors only.",
        "W10 split-half: RANDOM half-splits of each evaluation author's texts, mean "
        "over 50 seeded splits (cid-parity banned; the original cid-parity estimator "
        "is reported once per arm as 'cid_parity_reference_banned' for bridge "
        "comparison only).",
        "Matched-stranger null (W10): author labels permuted over per-text rows, "
        "which preserves every author's text count exactly; three variants "
        "(unstratified, subreddit-stratified, m-bin-stratified). The operative "
        "absorption p is the MAX over variants (most conservative). Venue join was "
        "feasible for BOTH arms via deterministic re-enumeration of the candidate "
        "frames (author equality asserted on every scored cid), so design point (iv) "
        "was NOT dropped.",
        "Null-refit-of-selection (audit ground 3): the axis/eigenvector selection "
        "never touched evaluation authors, so shuffle/stranger nulls with the FIXED "
        "discovery vector are calibrated for the evaluation-side statistics; no "
        "refit inside the null is required under cross-fitting.",
        "P9/E4 have no self-vs-other statistic, so the 'matched-stranger' absorption "
        "test maps to the within-column shuffle null of the fixed-discovery-vector "
        "quadratic form on evaluation data (p >= .05 -> absorbed); burial CI is the "
        "author-cluster bootstrap of (v_disc' corr(X_eval) v_disc - 1).",
        "P9 contrasts: per-column sd scaling of the original script is a no-op for "
        "correlation-based statistics (corr_guarded re-standardizes columns); raw "
        "curvature contrasts used, invariance stated.",
        "E4 evaluation standardization uses DISCOVERY means/sds and the DISCOVERY "
        "static top-4 frame; the static-congruence check additionally reports "
        "congruence against an EVALUATION-fitted static frame.",
        "W10 bootstrap holds the 50 headline splits fixed and resamples evaluation "
        "authors (author-sampling variance is the dominant term; split-randomness "
        "variance is reported separately as split_r_sd_over_splits).",
        "Capped-arm W10 evaluation cohort is ~40 authors; its numbers are reported "
        "but are too thin to carry an adjudication on their own — one reason the "
        "uncapped arm is primary.",
    ]]
    OUT_MD.write_text("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
