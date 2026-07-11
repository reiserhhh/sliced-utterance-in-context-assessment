#!/usr/bin/env python
"""W4 — MA-vs-AR gust discrimination via lag-2 moments (F12.5, registered commit 5064a0a). Label-free.

GOVERNANCE: reads ONLY the pre-built Essays window cache (parquet); no CSV
with label columns is ever opened. Same restriction as W3: texts with
5<=m<=12, excluding any text whose kept row count != recorded m (subsample
gaps); columns standardized by pooled window sd over the restricted set.

Theory (F12.5, docs/SUICA_THEORY_FORMAL_NOTES_V3.md, commit 5064a0a):
  F12.5.1  The uncentered D2 autocovariance sequence is the 4th-difference
           filter on the gust autocovariances: S_h = sum_l [1,-4,6,-4,1]_l
           gamma_{h+l-2}; so S2 = gamma0 - 4*gamma1 + 6*gamma2 - 4*gamma3
           + gamma4, and under MA(1) (gamma_{h>=2}=0) S2_pred = Gamma0 - 4B
           exactly (entrywise, symmetrized). Verified in this pipeline by
           uncentered enumeration before use.
  F12.5.2  R2 = symS2_obs - S2_pred(Gamma0_hat, B_hat), all three moments
           with their EXACT within-text-centering corrections. Under MA(1)
           E[R2] = 0 (the whole map is linear, so unbiasedness is exact);
           under AR(1) with small phi, R2 ~ 6*phi^2*gamma0 > 0 (attenuated
           by centering); widespread R2 < 0 falls outside both families.
  F12.5.3  Per-construct scalar overidentification: fit the centered
           diagonal triple (S0_cc, symS1_cc, symS2_cc) with each
           one-parameter family (MA(1) theta, AR(1) phi), gamma0 profiled
           analytically; compare residual sums of squares.

METHOD (the d(3) lesson — NO hand-simplified closed forms):
  All centering-corrected coefficient maps are computed by EXACT ENUMERATION.
  For each text length n (D2 rows; windows m = n+2) and each gust lag h,
  build the (n+2)x(n+2) basis Toeplitz G_h (ones at |i-j|=h), form the D2
  rows' covariance W G_h W^T with the [1,-2,1] filter matrix W, apply the
  centering projection P = I - J/n, and read the per-n coefficients of
  gamma_h on (E[S0], E[symS1], E[symS2]) as (mean diag, mean lag-1 diag,
  mean lag-2 diag). Entries are exact rationals realized in float. Pool
  across the actual text composition with natural weights: rows n for S0,
  pairs n-1 for S1, pairs n-2 for S2 (n>=3 for all texts here, so every
  text contributes to S2). CROSS-CHECK (asserted to 1e-12): the pooled
  S0/S1 coefficients of (gamma0, gamma1) must reproduce W3's closed-form
  A, B_coef, C, D_coef including the exact d(3) = 56/9 boundary value.

Pipeline:
  1. Moments S0, symS1 exactly as W3, plus symS2 = symmetrized mean over
     within-text lag-2 pairs of outer(D2_k, D2_{k+2}) (D2 centered within
     text as before).
  2. MA(1) inversion of (S0, symS1) -> (Gamma0_hat, B_hat) using the
     enumerated pooled coefficients (identical to W3 corrected by the
     asserted cross-check). S2_pred = s2g0*Gamma0_hat + s2g1*B_hat
     (pooled enumerated lag-0/lag-1 coefficients of the S2 map applied
     entrywise). R2 = symS2 - S2_pred.
  3. Bootstrap over TEXTS (N_BOOT=500 draws, seed 20260712, resample with
     replacement): each draw recomputes moments AND the pooled coefficient
     maps from the DRAW's own n-composition, then the inversion and R2.
     Records diag-mean R2 and all 19 per-construct diag R2. Percentile
     2.5/97.5 CIs. sd_pool fixed at full-sample values (W2b/W3 convention).
  4. Per-construct scalar overidentification (F12.5.3): for each construct,
     grid over theta (MA(1): gamma1/gamma0 = -theta/(1+theta^2),
     gamma_{h>=2}=0) and phi (AR(1): gamma_h = phi^|h|*gamma0, exact within
     text because only n+2 <= 14 windows exist — the enumerated per-lag
     coefficient table covers every realized lag), both on
     [-0.95, 0.95] step 0.005 (381 points); for fixed theta/phi the triple
     map is linear in gamma0, so gamma0 is profiled by least squares
     (gamma0* = L.y/L.L); winner = smaller RSS; margin = RSS_loser -
     RSS_winner.

Highlighted R2 reporting set (per W4 spec): the W3 CI-solid memory
constructs (wcl_35, wcl_36, first_person_usage_v2, wcl_13, wcl_03 — CI > 0;
plus novelty_play_v2, whose W3 CI touched +0.0000 at the 2.5% bound,
flagged borderline), wcl_60, and the 3 largest |R2| among the remaining
constructs. The full 19-construct table is printed and stored regardless.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "results" / "suica_v6_e2_essays_motion" / "cache_essays_windows_scored19.parquet"
OUT_DIR = ROOT / "results" / "suica_v6_w4_ma_vs_ar"
M_LO, M_HI = 5, 12
SEED = 20260712
N_BOOT = 500
GRID = np.linspace(-0.95, 0.95, 381)

W3_MEMORY_SET = ["wcl_35", "wcl_36", "first_person_usage_v2", "wcl_13", "wcl_03",
                 "novelty_play_v2"]  # last is the W3 borderline (CI touched +0.0000)


# ---------------- exact enumeration engine ----------------

def d2_filter(n: int) -> np.ndarray:
    W = np.zeros((n, n + 2))
    for i in range(n):
        W[i, i], W[i, i + 1], W[i, i + 2] = 1.0, -2.0, 1.0
    return W


def basis_lag_coeffs(n: int, centered: bool = True) -> np.ndarray:
    """(n+2, 3) array: coefficient of gust autocovariance gamma_h on
    (E[s0], E[s1], E[s2]) for one text with n D2 rows (m = n+2 windows)."""
    m = n + 2
    W = d2_filter(n)
    P = np.eye(n) - np.ones((n, n)) / n if centered else np.eye(n)
    out = np.zeros((m, 3))
    for h in range(m):
        if h == 0:
            G = np.eye(m)
        else:
            G = np.zeros((m, m))
            for i in range(m - h):
                G[i, i + h] = 1.0
                G[i + h, i] = 1.0
        M = P @ (W @ G @ W.T) @ P
        s0 = np.trace(M) / n
        s1 = np.diagonal(M, 1).mean() if n >= 2 else 0.0
        s2 = np.diagonal(M, 2).mean() if n >= 3 else 0.0
        out[h] = (s0, s1, s2)
    return out


_BASIS_CACHE: dict = {}


def basis_cached(n: int) -> np.ndarray:
    if n not in _BASIS_CACHE:
        _BASIS_CACHE[n] = basis_lag_coeffs(n)
    return _BASIS_CACHE[n]


def pooled_lag_table(stratum_counts: dict) -> np.ndarray:
    """(max_lag+1, 3) pooled coefficients of gamma_h on (E[S0], E[symS1],
    E[symS2]) for a corpus with stratum_counts = {m: n_texts}. Weights:
    rows n per text for S0, pairs n-1 for S1, pairs n-2 for S2. Strata in
    which lag h is not realized contribute coefficient 0 (correct: gamma_h
    never appears inside such texts) but full weight to the denominator."""
    max_lag = max(stratum_counts) - 1  # largest realized lag = m-1 = n+1
    num = np.zeros((max_lag + 1, 3))
    den = np.zeros(3)
    for m_val, cnt in stratum_counts.items():
        if cnt == 0:
            continue
        n = m_val - 2
        bc = basis_cached(n)
        w = np.array([cnt * n, cnt * (n - 1), cnt * (n - 2)], float)
        num[: n + 2] += bc * w
        den += w
    return num / den


# ---------------- closed-form cross-check targets (W3) ----------------

def a_cf(n): return 6 - 4 / n ** 2
def b_cf(n): return -8 + 4 / n ** 2
def c_cf(n): return -4 + 2 * (n - 2) / (n ** 2 * (n - 1))
def d_cf(n): return 56.0 / 9.0 if n == 3 else 7 - 4 / n ** 2


def w3_closed_form_coeffs(stratum_counts: dict):
    num_a = num_b = num_c = num_d = den0 = den1 = 0.0
    for m_val, cnt in stratum_counts.items():
        n = m_val - 2
        num_a += cnt * n * a_cf(n); num_b += cnt * n * b_cf(n); den0 += cnt * n
        num_c += cnt * (n - 1) * c_cf(n); num_d += cnt * (n - 1) * d_cf(n); den1 += cnt * (n - 1)
    return num_a / den0, num_b / den0, num_c / den1, num_d / den1


# ---------------- moments ----------------

def build_moments(X_by_m: dict) -> dict:
    """S0, symS1 exactly as W3's builder, plus symS2 over lag-2 pairs.
    Also returns the selection's stratum text counts (for coefficient
    pooling)."""
    p = None
    S0_sum = S1_sum = S2_sum = None
    n_d2 = n_pairs = n_pairs2 = 0
    counts = {}
    for m_val in sorted(X_by_m):
        X = X_by_m[m_val]
        n_m = X.shape[0]
        if n_m == 0:
            continue
        if p is None:
            p = X.shape[2]
            S0_sum = np.zeros((p, p)); S1_sum = np.zeros((p, p)); S2_sum = np.zeros((p, p))
        counts[m_val] = n_m
        D2 = X[:, 2:, :] - 2 * X[:, 1:-1, :] + X[:, :-2, :]
        D2c = D2 - D2.mean(axis=1, keepdims=True)
        flat = D2c.reshape(-1, p)
        S0_sum += flat.T @ flat
        n_d2 += flat.shape[0]
        if D2c.shape[1] >= 2:
            A1 = D2c[:, :-1, :].reshape(-1, p)
            B1 = D2c[:, 1:, :].reshape(-1, p)
            S1_sum += A1.T @ B1
            n_pairs += A1.shape[0]
        if D2c.shape[1] >= 3:
            A2 = D2c[:, :-2, :].reshape(-1, p)
            B2 = D2c[:, 2:, :].reshape(-1, p)
            S2_sum += A2.T @ B2
            n_pairs2 += A2.shape[0]
    S0 = S0_sum / n_d2
    symS1 = (S1_sum / n_pairs + (S1_sum / n_pairs).T) / 2.0
    symS2 = (S2_sum / n_pairs2 + (S2_sum / n_pairs2).T) / 2.0
    return {"S0": S0, "symS1": symS1, "symS2": symS2, "counts": counts,
            "n_D2": n_d2, "n_pairs": n_pairs, "n_pairs2": n_pairs2}


def ma_inversion_and_r2(mom: dict, L: np.ndarray):
    """Corrected MA(1) inversion from the enumerated pooled coefficients,
    then the F12.5.2 discriminator R2 = symS2 - S2_pred."""
    A, C = L[0, 0], L[0, 1]
    Bc, Dc = L[1, 0], L[1, 1]
    det = A * Dc - Bc * C
    Gamma0 = (Dc * mom["S0"] - Bc * mom["symS1"]) / det
    B = (A * mom["symS1"] - C * mom["S0"]) / det
    S2_pred = L[0, 2] * Gamma0 + L[1, 2] * B
    R2 = mom["symS2"] - S2_pred
    return Gamma0, B, R2, det


# ---------------- per-construct family fits (F12.5.3) ----------------

def family_maps(L: np.ndarray):
    """Precompute the (381, 3) triple maps per unit gamma0 for both families."""
    max_lag = L.shape[0] - 1
    r = -GRID / (1 + GRID ** 2)
    L_ma = L[0][None, :] + r[:, None] * L[1][None, :]
    powers = GRID[:, None] ** np.arange(max_lag + 1)[None, :]      # (381, max_lag+1)
    L_ar = powers @ L                                               # (381, 3)
    return L_ma, L_ar


def fit_one(y: np.ndarray, L_fam: np.ndarray):
    """Profile gamma0 by least squares at each grid point; return best."""
    denom = (L_fam ** 2).sum(axis=1)
    g0 = (L_fam @ y) / denom
    rss = ((y[None, :] - g0[:, None] * L_fam) ** 2).sum(axis=1)
    k = int(np.argmin(rss))
    return float(GRID[k]), float(rss[k]), float(g0[k])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(CACHE)
    cols = [c for c in df.columns if c not in ("eid", "user_id", "j", "m", "t", "tau", "delta")]

    m_per_text = df.groupby("eid")["m"].first()
    n_excl_gt12 = int((m_per_text > M_HI).sum())
    n_excl_lt5 = int((m_per_text < M_LO).sum())
    keep_eids = m_per_text[(m_per_text >= M_LO) & (m_per_text <= M_HI)].index
    sub = df[df["eid"].isin(keep_eids)].sort_values(["eid", "j"]).reset_index(drop=True)

    sizes = sub.groupby("eid").size()
    m_recorded = sub.groupby("eid")["m"].first()
    gap_eids = sizes.index[sizes != m_recorded.loc[sizes.index]]
    n_excl_gap = int(len(gap_eids))
    if n_excl_gap:
        sub = sub[~sub["eid"].isin(gap_eids)].reset_index(drop=True)

    n_texts = int(sub["eid"].nunique())
    n_windows = int(len(sub))

    sd_pool = sub[cols].to_numpy(float).std(0)
    sd_pool = np.where(sd_pool > 0, sd_pool, 1.0)

    texts = []
    for eid, g in sub.groupby("eid", sort=True):
        m_val = int(g["m"].iloc[0])
        X = g[cols].to_numpy(float) / sd_pool
        texts.append({"m": m_val, "X": X})
    N = len(texts)

    STRATA: dict = {}
    for t in texts:
        STRATA.setdefault(t["m"], []).append(t["X"])
    STRATA = {m_val: np.stack(arrs) for m_val, arrs in STRATA.items()}
    m_stratum_counts = {int(m_val): int(arr.shape[0]) for m_val, arr in STRATA.items()}

    text_m = np.array([t["m"] for t in texts])
    counters: dict = {}
    text_local_idx = np.empty(N, dtype=int)
    for i, t in enumerate(texts):
        text_local_idx[i] = counters.get(t["m"], 0)
        counters[t["m"]] = counters.get(t["m"], 0) + 1

    def select(idx_array):
        X_by_m = {}
        for m_val in STRATA:
            sel = idx_array[text_m[idx_array] == m_val]
            if sel.size == 0:
                continue
            X_by_m[m_val] = STRATA[m_val][text_local_idx[sel]]
        return X_by_m

    # ---------- full-sample moments, pooled maps, cross-check ----------
    mom = build_moments(select(np.arange(N)))
    L = pooled_lag_table(mom["counts"])

    A_cf, B_cf_, C_cf, D_cf = w3_closed_form_coeffs(mom["counts"])
    diffs = [abs(L[0, 0] - A_cf), abs(L[1, 0] - B_cf_), abs(L[0, 1] - C_cf), abs(L[1, 1] - D_cf)]
    assert max(diffs) < 1e-12, f"enumeration/closed-form cross-check failed: {diffs}"

    Gamma0, B, R2, det = ma_inversion_and_r2(mom, L)
    R2_diag = np.diagonal(R2).copy()
    R2_diag_mean = float(R2_diag.mean())

    # ---------- bootstrap ----------
    rng = np.random.default_rng(SEED)
    boot_R2_mean = np.empty(N_BOOT)
    boot_R2_diag = np.empty((N_BOOT, len(cols)))
    for bdx in range(N_BOOT):
        idx_b = rng.integers(0, N, N)
        mom_b = build_moments(select(idx_b))
        L_b = pooled_lag_table(mom_b["counts"])
        _, _, R2_b, _ = ma_inversion_and_r2(mom_b, L_b)
        d = np.diagonal(R2_b)
        boot_R2_mean[bdx] = float(d.mean())
        boot_R2_diag[bdx] = d
    ci_R2_mean = [float(np.percentile(boot_R2_mean, q)) for q in (2.5, 97.5)]
    frac_R2_gt0 = float((boot_R2_mean > 0).mean())
    R2_ci_lo = np.percentile(boot_R2_diag, 2.5, axis=0)
    R2_ci_hi = np.percentile(boot_R2_diag, 97.5, axis=0)

    # ---------- per-construct overidentification ----------
    L_ma, L_ar = family_maps(L)
    fit_rows = []
    for i, con in enumerate(cols):
        y = np.array([mom["S0"][i, i], mom["symS1"][i, i], mom["symS2"][i, i]])
        th, rss_ma, g0_ma = fit_one(y, L_ma)
        ph, rss_ar, g0_ar = fit_one(y, L_ar)
        winner = "MA" if rss_ma < rss_ar else "AR"
        margin = abs(rss_ar - rss_ma)
        fit_rows.append({
            "construct": con,
            "S0_cc": round(float(y[0]), 4), "symS1_cc": round(float(y[1]), 4),
            "symS2_cc": round(float(y[2]), 4),
            "R2_cc": round(float(R2_diag[i]), 4),
            "R2_ci_2p5_97p5": [round(float(R2_ci_lo[i]), 4), round(float(R2_ci_hi[i]), 4)],
            "ma_theta": round(th, 3), "ma_rss": float(f"{rss_ma:.3e}"), "ma_gamma0": round(g0_ma, 4),
            "ar_phi": round(ph, 3), "ar_rss": float(f"{rss_ar:.3e}"), "ar_gamma0": round(g0_ar, 4),
            "winner": winner, "rss_margin": float(f"{margin:.3e}"),
        })
    n_ma = sum(1 for r in fit_rows if r["winner"] == "MA")
    n_ar = len(fit_rows) - n_ma

    # highlighted subset: W3 memory set + wcl_60 + 3 largest |R2| others
    named = set(W3_MEMORY_SET) | {"wcl_60"}
    others = [i for i, c in enumerate(cols) if c not in named]
    others3 = sorted(others, key=lambda i: -abs(R2_diag[i]))[:3]
    highlight = [cols.index(c) for c in W3_MEMORY_SET] + [cols.index("wcl_60")] + others3

    # ---------- prints ----------
    print(f"n_texts={n_texts} n_windows={n_windows} (5<=m<=12); "
          f"excluded m>12: {n_excl_gt12} texts; excluded m<5: {n_excl_lt5} texts; "
          f"excluded subsample-gap texts: {n_excl_gap}")
    print(f"n_D2={mom['n_D2']} n_pairs={mom['n_pairs']} n_pairs2={mom['n_pairs2']}; "
          f"m_stratum_counts={m_stratum_counts}")
    print("[coeff cross-check] enumerated vs W3 closed forms (incl. d(3)=56/9):")
    print(f"  s0(g0)={L[0,0]:.12f} vs A     ={A_cf:.12f} diff={diffs[0]:.2e}")
    print(f"  s0(g1)={L[1,0]:.12f} vs B_coef={B_cf_:.12f} diff={diffs[1]:.2e}")
    print(f"  s1(g0)={L[0,1]:.12f} vs C     ={C_cf:.12f} diff={diffs[2]:.2e}")
    print(f"  s1(g1)={L[1,1]:.12f} vs D_coef={D_cf:.12f} diff={diffs[3]:.2e}")
    print(f"[S2 map] s2(g0)={L[0,2]:.6f} s2(g1)={L[1,2]:.6f} "
          f"(uncentered identity would be +1, -4); det={det:.6f}")
    print()
    print(f"[R2] diag_mean={R2_diag_mean:+.5f} CI=[{ci_R2_mean[0]:+.5f}, {ci_R2_mean[1]:+.5f}] "
          f"frac>0={frac_R2_gt0:.3f}  (n_boot={N_BOOT}, seed={SEED})")
    print()
    print("[R2 highlighted] W3 memory set + wcl_60 + 3 largest |R2| others:")
    for i in highlight:
        tag = " (W3 borderline)" if cols[i] == "novelty_play_v2" else ""
        print(f"  {cols[i]} R2={R2_diag[i]:+.4f} CI=[{R2_ci_lo[i]:+.4f}, {R2_ci_hi[i]:+.4f}]{tag}")
    print()
    print("[overidentification] per-construct MA(1) vs AR(1) fits (diagonal triples):")
    for r in sorted(fit_rows, key=lambda r: -abs(r["R2_cc"])):
        print(f"  {r['construct']} R2={r['R2_cc']:+.4f} "
              f"CI=[{r['R2_ci_2p5_97p5'][0]:+.4f}, {r['R2_ci_2p5_97p5'][1]:+.4f}] "
              f"MA_rss={r['ma_rss']:.3e} (theta={r['ma_theta']:+.3f}) "
              f"AR_rss={r['ar_rss']:.3e} (phi={r['ar_phi']:+.3f}) "
              f"winner={r['winner']} margin={r['rss_margin']:.3e}")
    print()
    print(f"[winners] MA={n_ma} AR={n_ar} of {len(cols)} constructs")

    # ---------- JSON ----------
    result = {
        "registered_commit": "5064a0a",
        "formula_ref": "F12.5, docs/SUICA_THEORY_FORMAL_NOTES_V3.md",
        "n_texts": n_texts, "n_windows": n_windows,
        "n_excluded_m_gt_12_texts": n_excl_gt12,
        "n_excluded_m_lt_5_texts": n_excl_lt5,
        "n_excluded_subsample_gap_texts": n_excl_gap,
        "constructs": cols,
        "m_stratum_counts": m_stratum_counts,
        "n_D2": mom["n_D2"], "n_pairs": mom["n_pairs"], "n_pairs2": mom["n_pairs2"],
        "coefficient_cross_check": {
            "enumerated": {"s0_g0": L[0, 0], "s0_g1": L[1, 0], "s1_g0": L[0, 1], "s1_g1": L[1, 1]},
            "w3_closed_form": {"A": A_cf, "B_coef": B_cf_, "C": C_cf, "D_coef": D_cf},
            "max_abs_diff": max(diffs),
        },
        "s2_map": {"s2_g0": round(float(L[0, 2]), 6), "s2_g1": round(float(L[1, 2]), 6)},
        "pooled_lag_table": [[round(float(x), 8) for x in row] for row in L],
        "det": round(float(det), 6),
        "S0": [[round(float(x), 6) for x in row] for row in mom["S0"]],
        "symS1": [[round(float(x), 6) for x in row] for row in mom["symS1"]],
        "symS2": [[round(float(x), 6) for x in row] for row in mom["symS2"]],
        "Gamma0_hat": [[round(float(x), 6) for x in row] for row in Gamma0],
        "B_hat": [[round(float(x), 6) for x in row] for row in B],
        "R2": [[round(float(x), 6) for x in row] for row in R2],
        "R2_diag_mean": {
            "point": round(R2_diag_mean, 5),
            "ci_2p5_97p5": [round(ci_R2_mean[0], 5), round(ci_R2_mean[1], 5)],
            "frac_draws_gt_0": round(frac_R2_gt0, 3),
        },
        "bootstrap": {"n_boot": N_BOOT, "seed": SEED,
                      "design": "text-level resample; each draw redoes moments, the draw's own "
                                "n-composition enumerated maps, MA(1) inversion, R2; percentile CIs; "
                                "sd_pool fixed at full-sample values (W2b/W3 convention)"},
        "highlighted_constructs": [cols[i] for i in highlight],
        "fit_table_sorted_by_absR2": sorted(fit_rows, key=lambda r: -abs(r["R2_cc"])),
        "winner_counts": {"MA": n_ma, "AR": n_ar},
        "grid": {"lo": -0.95, "hi": 0.95, "step": 0.005, "points": len(GRID)},
    }
    (OUT_DIR / "V6_W4_MA_VS_AR.json").write_text(json.dumps(result, indent=2))

    md = ["# V6-W4 -- MA-vs-AR gust discrimination via lag-2 moments (Essays, label-free)",
          "",
          "Registered commit: 5064a0a (F12.5, docs/SUICA_THEORY_FORMAL_NOTES_V3.md)",
          "",
          f"n_texts={n_texts} (5<=m<=12), n_windows={n_windows}; excluded m>12: {n_excl_gt12}; "
          f"m<5: {n_excl_lt5}; subsample-gap: {n_excl_gap}. "
          f"n_D2={mom['n_D2']}, lag-1 pairs={mom['n_pairs']}, lag-2 pairs={mom['n_pairs2']}.",
          "",
          "Coefficient cross-check (enumeration vs W3 closed forms incl. d(3)=56/9): "
          f"max abs diff = {max(diffs):.2e} (asserted < 1e-12). "
          f"S2 centering map: s2(g0)={L[0,2]:.6f}, s2(g1)={L[1,2]:.6f} (uncentered: +1, -4).",
          "",
          "## Corpus discriminator (F12.5.2)",
          "",
          "| quantity | point | CI 2.5% | CI 97.5% | frac draws > 0 |",
          "|---|---|---|---|---|",
          f"| R2 diag mean | {R2_diag_mean:+.5f} | {ci_R2_mean[0]:+.5f} | {ci_R2_mean[1]:+.5f} | "
          f"{frac_R2_gt0:.3f} |",
          "",
          "## Per-construct overidentification (F12.5.3), sorted by |R2|",
          "",
          "| construct | R2 | CI 2.5% | CI 97.5% | MA rss (theta) | AR rss (phi) | winner | margin |",
          "|---|---|---|---|---|---|---|---|"]
    for r in sorted(fit_rows, key=lambda r: -abs(r["R2_cc"])):
        md.append(f"| {r['construct']} | {r['R2_cc']:+.4f} | {r['R2_ci_2p5_97p5'][0]:+.4f} | "
                  f"{r['R2_ci_2p5_97p5'][1]:+.4f} | {r['ma_rss']:.3e} ({r['ma_theta']:+.3f}) | "
                  f"{r['ar_rss']:.3e} ({r['ar_phi']:+.3f}) | {r['winner']} | {r['rss_margin']:.3e} |")
    md += ["",
           f"Winners: MA={n_ma}, AR={n_ar} of {len(cols)}.",
           "",
           f"Highlighted set (W4 spec): {', '.join(cols[i] for i in highlight)} "
           "(novelty_play_v2 = W3 borderline memory construct)."]
    (OUT_DIR / "V6_W4_MA_VS_AR.md").write_text("\n".join(md) + "\n")
    print("\nwritten:", OUT_DIR / "V6_W4_MA_VS_AR.json")
    print("written:", OUT_DIR / "V6_W4_MA_VS_AR.md")


if __name__ == "__main__":
    main()
