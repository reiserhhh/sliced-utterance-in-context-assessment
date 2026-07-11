#!/usr/bin/env python
"""W8 — AR(2) texture-triangle fit of the three hybrid functionals (F12.9, registered commit e04d5e0). Label-free.

GOVERNANCE: reads ONLY the pre-built Essays window cache (parquet) and the
W3 result JSON (for an r_c integrity cross-check); no CSV with label
columns is ever opened. Same restriction/standardization as W3-W7: texts
with 5<=m<=12, no subsample gaps, pooled-sd standardization.

Claim under test (F12.9, docs/SUICA_THEORY_FORMAL_NOTES_V3.md, commit
e04d5e0): the observed gust textures are regions of ONE family — AR(2)
gusts x_k = a1*x_{k-1} + a2*x_{k-2} + eta on the stationarity triangle
(carry-over: a1>0, a2~0; bounce: a1<0; period-2: a1~0, a2>0; damped
period-4: a1~0, a2<0). MA(1) is NOT nested: genuine one-step echoes must
FAIL the fit (worst overidentification residual) — the sharp test for
wcl_60. KILL: wcl_60 fitting as well as the median construct kills W4's
MA-vs-AR distinction.

Instrument:
  1. Three hybrid estimable functionals per construct diagonal:
       r_c        = B_hat_cc / Gamma0_hat_cc from the W3 corrected
                    2-moment inversion (closed-form pooled coefficients
                    incl. d(3) = 56/9);
       rho_pihalf = (w_ph . S) / (w_g03 . S[:3]), w_ph = 5-moment
                    left-solve of (1,0,-2,0,2) (W7a primary mode);
       rho_pi     = (w_pi . S) / (w_g03 . S[:3]), w_pi = 5-moment
                    left-solve of (1,-2,2,-2,2);
     (hybrid per-functional conditioning discipline, F12.8).
  2. AR(2) reference map, exact for the shipped estimators: grid over the
     stationarity triangle (a1, a2 in [-0.9, 0.9] step 0.02, constrained
     a1 + a2 < 1, a2 - a1 < 1, |a2| < 1), Yule-Walker gust ladder
     gamma_0..11 (gamma0 = 1 WLOG — all three functionals are
     scale-free), pushed through the FULL pooled coefficient matrix
     (pooled coefficient of gamma_j on E[symS_h], j = 0..11, h = 0..4;
     the exact-on-composition expected-value machinery) and then through
     the shipped functionals. Cached once (composition-dependent only).
  3. Weighted grid least squares per construct on the standardized
     3-vector: weights = per-construct bootstrap sds of the three
     functionals from a 300-draw full-pipeline bootstrap of the OBSERVED
     data (seed 20260712). W7a's 500-draw bootstrap is NOT reused (it
     did not record r_c — stated per spec). The SAME 300 draws are then
     refit on the cached grid for percentile CIs of (a1_hat, a2_hat,
     residual); the weights stay fixed at the full-sample bootstrap sds.
  4. Overidentification residual = weighted SSE at the grid optimum
     (3 moments, 2 parameters, 1 dof).

Runtime asserts (verify-don't-trust discipline): engine 2x2 and s2-map
cross-checks as W5-W7; the full pooled ladder map's first five columns
equal the W5 5x5 map (1e-12); the map applied to an AR(2) test ladder
equals the direct exact-pooled-moment computation (1e-12); the grid's
white row gives (r_c, rho_pihalf, rho_pi) = (0, 1, 1) to 1e-9; the grid's
AR(1) a1=0.1 row reproduces W7a's exact-on-composition reference values
to 1e-6; observed r_c reproduces W3's published r_corrected to 1e-3
(rounding of the artifact).

Drop guard per construct per draw: trunc-3 gamma0 <= 0.05 OR 2-moment
Gamma0_hat_cc <= 0.05 (extends the W6a/W7a guard to the r_c denominator;
counts reported). sd_pool fixed at full-sample values (W2b-W7
convention).
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "results" / "suica_v6_e2_essays_motion" / "cache_essays_windows_scored19.parquet"
W3_JSON = ROOT / "results" / "suica_v6_w3_corrected_reinversion" / "V6_W3_CORRECTED_REINVERSION.json"
OUT_DIR = ROOT / "results" / "suica_v6_w8_ar2_triangle"
M_LO, M_HI = 5, 12
SEED = 20260712
N_BOOT = 300
H_MAX = 4
MAX_LAG = 11  # largest realized gust lag on this corpus (m=12 -> n+1 = 11)
G0_DROP_THRESHOLD = 0.05
GRID_VALS = np.linspace(-0.9, 0.9, 91)

C_PI = np.array([1.0, -2.0, 2.0, -2.0, 2.0])
C_PH = np.array([1.0, 0.0, -2.0, 0.0, 2.0])
C_G0_3 = np.array([1.0, 0.0, 0.0])
W4_S2_MAP = (0.708157, -3.479632)

LEAN_A = ["wcl_35", "wcl_36", "wcl_13"]
LEAN_B = ["wcl_20", "wcl_07"]
LEAN_C = ["wcl_60"]
LEAN_D = ["first_person_usage_v2", "wcl_03"]


# ---------------- exact enumeration engine (W5-W7) ----------------

def d2_filter(n: int) -> np.ndarray:
    W = np.zeros((n, n + 2))
    for i in range(n):
        W[i, i], W[i, i + 1], W[i, i + 2] = 1.0, -2.0, 1.0
    return W


def full_lag_table(n: int) -> np.ndarray:
    m = n + 2
    W = d2_filter(n)
    P = np.eye(n) - np.ones((n, n)) / n
    T = np.zeros((m, H_MAX + 1))
    for j in range(m):
        if j == 0:
            G = np.eye(m)
        else:
            G = np.zeros((m, m))
            for i in range(m - j):
                G[i, i + j] = 1.0
                G[i + j, i] = 1.0
        Mm = P @ (W @ G @ W.T) @ P
        for h in range(H_MAX + 1):
            if n >= h + 1:
                T[j, h] = np.diagonal(Mm, h).mean() if h > 0 else np.trace(Mm) / n
    return T


_TABLES: dict = {}


def table_cached(n: int) -> np.ndarray:
    if n not in _TABLES:
        _TABLES[n] = full_lag_table(n)
    return _TABLES[n]


def pooled_full_map(stratum_counts: dict) -> np.ndarray:
    """(5, MAX_LAG+1): pooled coefficient of gamma_j on E[symS_h]; strata
    without lag-h pairs contribute nothing to row h; gamma_j columns with
    j > n+1 receive zero from that stratum (the lag is not realized)."""
    num = np.zeros((H_MAX + 1, MAX_LAG + 1))
    den = np.zeros(H_MAX + 1)
    for m_val, cnt in stratum_counts.items():
        if cnt == 0:
            continue
        n = m_val - 2
        T = table_cached(n)          # (n+2, 5)
        for h in range(H_MAX + 1):
            w = cnt * (n - h)
            if w <= 0:
                continue
            num[h, : n + 2] += w * T[:, h]
            den[h] += w
    assert (den > 0).all(), f"degenerate composition: pair counts {den}"
    return num / den[:, None]


def exact_pooled_moments(stratum_counts: dict, gamma_fn) -> np.ndarray:
    num = np.zeros(H_MAX + 1)
    den = np.zeros(H_MAX + 1)
    for m_val, cnt in stratum_counts.items():
        n = m_val - 2
        T = table_cached(n)
        g_full = np.array([gamma_fn(j) for j in range(n + 2)])
        contrib = g_full @ T
        for h in range(H_MAX + 1):
            w = cnt * (n - h)
            if w <= 0:
                continue
            num[h] += w * contrib[h]
            den[h] += w
    return num / den


def a_cf(n): return 6 - 4 / n ** 2
def b_cf(n): return -8 + 4 / n ** 2
def c_cf(n): return -4 + 2 * (n - 2) / (n ** 2 * (n - 1))
def d_cf(n): return 56.0 / 9.0 if n == 3 else 7 - 4 / n ** 2


def w3_coeffs(stratum_counts: dict):
    num_a = num_b = num_c = num_d = den0 = den1 = 0.0
    for m_val, cnt in stratum_counts.items():
        n = m_val - 2
        num_a += cnt * n * a_cf(n); num_b += cnt * n * b_cf(n); den0 += cnt * n
        num_c += cnt * (n - 1) * c_cf(n); num_d += cnt * (n - 1) * d_cf(n); den1 += cnt * (n - 1)
    return num_a / den0, num_b / den0, num_c / den1, num_d / den1


def diag_moments(X_by_m: dict, p: int):
    S = np.zeros((H_MAX + 1, p))
    Wt = np.zeros(H_MAX + 1)
    counts = {}
    for m_val in sorted(X_by_m):
        X = X_by_m[m_val]
        n_m = X.shape[0]
        if n_m == 0:
            continue
        counts[m_val] = n_m
        n = m_val - 2
        D2 = X[:, 2:, :] - 2 * X[:, 1:-1, :] + X[:, :-2, :]
        D2c = D2 - D2.mean(axis=1, keepdims=True)
        for h in range(H_MAX + 1):
            if n >= h + 1:
                if h == 0:
                    S[h] += (D2c ** 2).sum(axis=(0, 1))
                else:
                    S[h] += (D2c[:, :-h, :] * D2c[:, h:, :]).sum(axis=(0, 1))
                Wt[h] += n_m * (n - h)
    return S / Wt[:, None], counts


def three_functionals(Y: np.ndarray, counts: dict):
    """(r_c, rho_pihalf, rho_pi, gamma0_trunc3, Gamma0_2mom) per construct
    for moments Y (5, p) under composition counts — the shipped hybrid."""
    M = pooled_M_from_full(counts)
    A_t, B_t, C_t, D_t = w3_coeffs(counts)
    det2 = A_t * D_t - B_t * C_t
    G0_2m = (D_t * Y[0] - B_t * Y[1]) / det2
    B_2m = (A_t * Y[1] - C_t * Y[0]) / det2
    r_c = B_2m / G0_2m
    w_pi = np.linalg.solve(M.T, C_PI)
    w_ph = np.linalg.solve(M.T, C_PH)
    w_g0 = np.linalg.solve(M[:3, :3].T, C_G0_3)
    g0_t3 = w_g0 @ Y[:3]
    rho_pi = (w_pi @ Y) / g0_t3
    rho_ph = (w_ph @ Y) / g0_t3
    return r_c, rho_ph, rho_pi, g0_t3, G0_2m


_FULL_MAP_CACHE: dict = {}


def pooled_M_from_full(counts: dict) -> np.ndarray:
    key = tuple(sorted(counts.items()))
    if key not in _FULL_MAP_CACHE:
        _FULL_MAP_CACHE[key] = pooled_full_map(counts)
    return _FULL_MAP_CACHE[key][:, : H_MAX + 1]


def ar2_gamma_ladder(a1: float, a2: float) -> np.ndarray:
    """Yule-Walker AR(2) autocovariances gamma_0..MAX_LAG, gamma0 = 1."""
    g = np.empty(MAX_LAG + 1)
    g[0] = 1.0
    g[1] = a1 / (1.0 - a2)
    for h in range(2, MAX_LAG + 1):
        g[h] = a1 * g[h - 1] + a2 * g[h - 2]
    return g


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(CACHE)
    cols = [c for c in df.columns if c not in ("eid", "user_id", "j", "m", "t", "tau", "delta")]
    p = len(cols)

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

    # ---------- full-sample moments + engine cross-checks ----------
    Y, counts_full = diag_moments(select(np.arange(N)), p)
    FULL_MAP = pooled_full_map(counts_full)          # (5, 12)
    M = FULL_MAP[:, : H_MAX + 1]

    A_t, B_t, C_t, D_t = w3_coeffs(counts_full)
    diffs2x2 = [abs(M[0, 0] - A_t), abs(M[0, 1] - B_t), abs(M[1, 0] - C_t), abs(M[1, 1] - D_t)]
    assert max(diffs2x2) < 1e-12, f"2x2 cross-check failed: {diffs2x2}"
    diffs_s2 = [abs(M[2, 0] - W4_S2_MAP[0]), abs(M[2, 1] - W4_S2_MAP[1])]
    assert max(diffs_s2) < 1e-6, f"W4 s2-map cross-check failed: {diffs_s2}"

    # full-map vs direct exact computation on an AR(2) test ladder
    g_test = ar2_gamma_ladder(0.3, 0.2)
    yE_map = FULL_MAP @ g_test
    yE_dir = exact_pooled_moments(counts_full, lambda h: g_test[h] if h <= MAX_LAG else 0.0)
    assert np.abs(yE_map - yE_dir).max() < 1e-12, "full-map vs direct exact mismatch"

    # ---------- grid cache ----------
    t0 = time.time()
    pts = []
    for a1 in GRID_VALS:
        for a2 in GRID_VALS:
            if (a1 + a2 < 1.0) and (a2 - a1 < 1.0) and (abs(a2) < 1.0):
                pts.append((a1, a2))
    pts = np.array(pts)                                  # (G, 2)
    Gsz = len(pts)
    ladders = np.empty((Gsz, MAX_LAG + 1))
    ladders[:, 0] = 1.0
    ladders[:, 1] = pts[:, 0] / (1.0 - pts[:, 1])
    for h in range(2, MAX_LAG + 1):
        ladders[:, h] = pts[:, 0] * ladders[:, h - 1] + pts[:, 1] * ladders[:, h - 2]
    E_S = ladders @ FULL_MAP.T                           # (G, 5)

    det2 = A_t * D_t - B_t * C_t
    G0_2m_grid = (D_t * E_S[:, 0] - B_t * E_S[:, 1]) / det2
    B_2m_grid = (A_t * E_S[:, 1] - C_t * E_S[:, 0]) / det2
    w_pi = np.linalg.solve(M.T, C_PI)
    w_ph = np.linalg.solve(M.T, C_PH)
    w_g0 = np.linalg.solve(M[:3, :3].T, C_G0_3)
    g0_grid = E_S[:, :3] @ w_g0
    GRID_F = np.column_stack([B_2m_grid / G0_2m_grid,
                              (E_S @ w_ph) / g0_grid,
                              (E_S @ w_pi) / g0_grid])   # (G, 3): r_c, rho_ph, rho_pi
    grid_secs = time.time() - t0

    # grid sanity: white row and AR(1) a1=0.1 row
    i_white = int(np.argmin(np.abs(pts[:, 0]) + np.abs(pts[:, 1])))
    assert abs(pts[i_white, 0]) < 1e-9 and abs(pts[i_white, 1]) < 1e-9
    assert np.abs(GRID_F[i_white] - np.array([0.0, 1.0, 1.0])).max() < 1e-9, \
        f"white grid row failed: {GRID_F[i_white]}"
    i_ar1 = int(np.argmin(np.abs(pts[:, 0] - 0.1) + np.abs(pts[:, 1])))
    # W7a exact-on-composition AR(1) phi=.1 references (hybrid): rho_ph, rho_pi
    yE_ar1 = exact_pooled_moments(counts_full, lambda h: 0.1 ** h)
    ref_ph = float((yE_ar1 @ w_ph) / (yE_ar1[:3] @ w_g0))
    ref_pi = float((yE_ar1 @ w_pi) / (yE_ar1[:3] @ w_g0))
    assert abs(GRID_F[i_ar1, 1] - ref_ph) < 1e-6 and abs(GRID_F[i_ar1, 2] - ref_pi) < 1e-6, \
        "AR(1) grid row does not reproduce the exact reference"

    # ---------- observed functionals + W3 integrity check ----------
    r_obs, rph_obs, rpi_obs, g0t3_obs, G02m_obs = three_functionals(Y, counts_full)
    OBS = np.column_stack([r_obs, rph_obs, rpi_obs])     # (p, 3)
    w3_art = json.loads(W3_JSON.read_text())
    w3_r = {r["construct"]: r["r_corrected"] for r in w3_art["theta_table_sorted_by_naive_desc"]}
    max_rdiff = max(abs(float(r_obs[i]) - w3_r[cols[i]]) for i in range(p))
    assert max_rdiff < 1e-3, f"r_c vs W3 artifact mismatch: {max_rdiff}"

    # ---------- bootstrap (sds AND refit CIs from the same 300 draws) ----------
    rng = np.random.default_rng(SEED)
    boot_F = np.full((N_BOOT, p, 3), np.nan)
    drops = np.zeros(p, dtype=int)
    for bdx in range(N_BOOT):
        idx_b = rng.integers(0, N, N)
        Y_b, counts_b = diag_moments(select(idx_b), p)
        r_b, rph_b, rpi_b, g0t3_b, G02m_b = three_functionals(Y_b, counts_b)
        ok = (g0t3_b > G0_DROP_THRESHOLD) & (G02m_b > G0_DROP_THRESHOLD)
        drops += (~ok).astype(int)
        boot_F[bdx, ok, 0] = r_b[ok]
        boot_F[bdx, ok, 1] = rph_b[ok]
        boot_F[bdx, ok, 2] = rpi_b[ok]
    sds = np.nanstd(boot_F, axis=0, ddof=1)              # (p, 3)
    assert (sds > 0).all(), "zero bootstrap sd encountered"

    # ---------- fits ----------
    def fit_vec(obs3: np.ndarray, sd3: np.ndarray):
        z = (GRID_F - obs3[None, :]) / sd3[None, :]
        sse = (z ** 2).sum(axis=1)
        k = int(np.argmin(sse))
        return pts[k, 0], pts[k, 1], float(sse[k])

    a1_pt = np.empty(p); a2_pt = np.empty(p); resid_pt = np.empty(p)
    for i in range(p):
        a1_pt[i], a2_pt[i], resid_pt[i] = fit_vec(OBS[i], sds[i])

    boot_fit = np.full((N_BOOT, p, 3), np.nan)           # a1, a2, resid
    for bdx in range(N_BOOT):
        for i in range(p):
            if np.isnan(boot_F[bdx, i, 0]):
                continue
            boot_fit[bdx, i] = fit_vec(boot_F[bdx, i], sds[i])

    def ci_nan(v):
        return np.nanpercentile(v, 2.5, axis=0), np.nanpercentile(v, 97.5, axis=0)

    a1_lo, a1_hi = ci_nan(boot_fit[:, :, 0])
    a2_lo, a2_hi = ci_nan(boot_fit[:, :, 1])
    rs_lo, rs_hi = ci_nan(boot_fit[:, :, 2])

    med_resid = float(np.median(resid_pt))
    i60 = cols.index("wcl_60")
    ratio60 = float(resid_pt[i60] / med_resid)
    rank60 = int(1 + (resid_pt > resid_pt[i60]).sum())   # 1 = worst

    # ---------- prints ----------
    print(f"n_texts={n_texts} n_windows={n_windows} (5<=m<=12); "
          f"excluded m>12: {n_excl_gt12}; m<5: {n_excl_lt5}; subsample-gap: {n_excl_gap}")
    print(f"m_stratum_counts={m_stratum_counts}")
    print(f"[cross-check] 2x2 max|diff|={max(diffs2x2):.2e}; s2 map max|diff|={max(diffs_s2):.2e}; "
          f"full-map vs direct exact: pass (1e-12); white grid row (0,1,1): pass (1e-9); "
          f"AR(1) a1=.1 grid row vs exact reference: pass (1e-6); "
          f"observed r_c vs W3 artifact max|diff|={max_rdiff:.2e}")
    print(f"[functionals] |w_pi|={np.linalg.norm(w_pi):.3f} |w_ph|={np.linalg.norm(w_ph):.3f} "
          f"|w_g0_trunc3|={np.linalg.norm(w_g0):.3f} (hybrid, W7a primary mode)")
    print(f"[grid] {Gsz} stationarity-triangle points (91x91 raw, step 0.02); "
          f"cache built in {grid_secs:.3f}s (composition-dependent only)")
    print(f"[bootstrap] n_boot={N_BOOT} seed={SEED}; sds and refit CIs from the SAME draw set "
          f"(W7a's 500-draw set not reused — it lacks r_c); drop guard trunc3-gamma0 or "
          f"2mom-Gamma0 <= {G0_DROP_THRESHOLD}: total drops={int(drops.sum())} "
          f"(nonzero: " + (", ".join(f"{cols[i]}={drops[i]}" for i in range(p) if drops[i]) or "none") + ")")
    print()
    print("[AR(2) triangle fits] sorted by overidentification residual DESCENDING (worst first):")
    order = np.argsort(-resid_pt)
    for i in order:
        print(f"  {cols[i]} a1={a1_pt[i]:+.2f} [{a1_lo[i]:+.2f},{a1_hi[i]:+.2f}] "
              f"a2={a2_pt[i]:+.2f} [{a2_lo[i]:+.2f},{a2_hi[i]:+.2f}] "
              f"resid={resid_pt[i]:.3f} [{rs_lo[i]:.3f},{rs_hi[i]:.3f}]")
    print()
    print("[adjudication raw lines] (planner adjudicates the F12.9 leans)")
    print("  -- lean (a) carry-over set (registered: a1 ~ +0.1, a2 ~ 0, small resid):")
    for name in LEAN_A:
        i = cols.index(name)
        print(f"     {name}: a1={a1_pt[i]:+.2f} [{a1_lo[i]:+.2f},{a1_hi[i]:+.2f}] "
              f"a2={a2_pt[i]:+.2f} [{a2_lo[i]:+.2f},{a2_hi[i]:+.2f}] resid={resid_pt[i]:.3f}")
    print("  -- lean (b) anomalies (registered: wcl_20 a2 ~ +0.15; wcl_07 a2 ~ -0.15..-0.2):")
    for name in LEAN_B:
        i = cols.index(name)
        print(f"     {name}: a1={a1_pt[i]:+.2f} [{a1_lo[i]:+.2f},{a1_hi[i]:+.2f}] "
              f"a2={a2_pt[i]:+.2f} [{a2_lo[i]:+.2f},{a2_hi[i]:+.2f}] resid={resid_pt[i]:.3f}")
    print("  -- lean (c) wcl_60 (registered: WORST residual of the 19):")
    print(f"     wcl_60: resid={resid_pt[i60]:.3f} rank={rank60}/19 (1 = worst); "
          f"a1={a1_pt[i60]:+.2f} a2={a2_pt[i60]:+.2f}")
    print("  -- lean (d) one-step echoes vs carry-over set:")
    carry_resids = [float(resid_pt[cols.index(n)]) for n in LEAN_A]
    for name in LEAN_D:
        i = cols.index(name)
        print(f"     {name}: resid={resid_pt[i]:.3f} (carry-over set resids: "
              + ", ".join(f"{v:.3f}" for v in carry_resids) + ")")
    print(f"  [KILL check] median resid={med_resid:.3f}; wcl_60/median ratio={ratio60:.2f} "
          f"(ratio ~ 1 would fire the kill)")

    # ---------- JSON ----------
    rows = []
    for i, con in enumerate(cols):
        rows.append({
            "construct": con,
            "obs": {"r_c": round(float(r_obs[i]), 4), "rho_pihalf": round(float(rph_obs[i]), 4),
                    "rho_pi": round(float(rpi_obs[i]), 4)},
            "sd": {"r_c": round(float(sds[i, 0]), 4), "rho_pihalf": round(float(sds[i, 1]), 4),
                   "rho_pi": round(float(sds[i, 2]), 4)},
            "a1": round(float(a1_pt[i]), 2), "a1_ci": [round(float(a1_lo[i]), 2), round(float(a1_hi[i]), 2)],
            "a2": round(float(a2_pt[i]), 2), "a2_ci": [round(float(a2_lo[i]), 2), round(float(a2_hi[i]), 2)],
            "resid": round(float(resid_pt[i]), 3),
            "resid_ci": [round(float(rs_lo[i]), 3), round(float(rs_hi[i]), 3)],
            "boot_drops": int(drops[i]),
        })
    result = {
        "registered_commit": "e04d5e0",
        "formula_ref": "F12.9, docs/SUICA_THEORY_FORMAL_NOTES_V3.md",
        "n_texts": n_texts, "n_windows": n_windows,
        "n_excluded_m_gt_12_texts": n_excl_gt12,
        "n_excluded_m_lt_5_texts": n_excl_lt5,
        "n_excluded_subsample_gap_texts": n_excl_gap,
        "constructs": cols, "m_stratum_counts": m_stratum_counts,
        "cross_checks": {"top2x2_max_abs_diff": max(diffs2x2),
                         "w4_s2_map_max_abs_diff": max(diffs_s2),
                         "full_map_vs_direct_exact": "pass 1e-12",
                         "white_grid_row": "pass 1e-9",
                         "ar1_grid_row_vs_exact": "pass 1e-6",
                         "r_c_vs_w3_artifact_max_abs_diff": max_rdiff},
        "functional_norms": {"w_pi": round(float(np.linalg.norm(w_pi)), 3),
                             "w_ph": round(float(np.linalg.norm(w_ph)), 3),
                             "w_g0_trunc3": round(float(np.linalg.norm(w_g0)), 3)},
        "grid": {"n_points": int(Gsz), "raw": "91x91 step 0.02 in [-0.9, 0.9]^2",
                 "constraints": "a1+a2<1, a2-a1<1, |a2|<1",
                 "cache_build_seconds": round(grid_secs, 3),
                 "yule_walker_max_lag": MAX_LAG},
        "bootstrap": {"n_boot": N_BOOT, "seed": SEED,
                      "design": "ONE 300-draw full-pipeline text resample provides BOTH the "
                                "per-construct functional sds (weights) and the refit CIs; "
                                "weights fixed at full-sample bootstrap sds across refits; "
                                "the grid stays at the full-sample composition (draw "
                                "compositions deviate only ~+-3%); W7a's 500-draw set not "
                                "reused (no r_c recorded); drop guard trunc3-gamma0 or "
                                "2mom-Gamma0 <= 0.05",
                      "total_drops": int(drops.sum())},
        "median_resid": round(med_resid, 3),
        "wcl_60_resid_rank_of_19": rank60,
        "wcl_60_resid_over_median": round(ratio60, 2),
        "table_sorted_by_resid_desc": [rows[i] for i in order],
        "leans": {"a_carry_over": LEAN_A, "b_anomalies": LEAN_B, "c_sharp_ma_test": LEAN_C,
                  "d_one_step_echoes": LEAN_D},
    }
    (OUT_DIR / "V6_W8_AR2_TRIANGLE.json").write_text(json.dumps(result, indent=2))

    md = ["# V6-W8 -- AR(2) texture-triangle fit of the three hybrid functionals (Essays, label-free)",
          "",
          "Registered commit: e04d5e0 (F12.9, docs/SUICA_THEORY_FORMAL_NOTES_V3.md)",
          "",
          f"n_texts={n_texts} (5<=m<=12), n_windows={n_windows}; excluded m>12: {n_excl_gt12}; "
          f"m<5: {n_excl_lt5}; subsample-gap: {n_excl_gap}.",
          "",
          f"Grid: {Gsz} stationarity-triangle points (91x91, step 0.02), Yule-Walker ladders to "
          f"lag {MAX_LAG}, exact-on-composition expected functionals; cache {grid_secs:.3f}s. "
          f"Fit: weighted grid LS on (r_c, rho_pihalf, rho_pi); weights = 300-draw bootstrap "
          f"sds; 3 moments, 2 parameters, 1 dof.",
          "",
          "## Fits (sorted by overidentification residual, worst first)",
          "",
          "| construct | a1 | CI | a2 | CI | resid | CI | drops |",
          "|---|---|---|---|---|---|---|---|"]
    for i in order:
        md.append(f"| {cols[i]} | {a1_pt[i]:+.2f} | [{a1_lo[i]:+.2f}, {a1_hi[i]:+.2f}] | "
                  f"{a2_pt[i]:+.2f} | [{a2_lo[i]:+.2f}, {a2_hi[i]:+.2f}] | "
                  f"{resid_pt[i]:.3f} | [{rs_lo[i]:.3f}, {rs_hi[i]:.3f}] | {int(drops[i])} |")
    md += ["",
           f"Median residual = {med_resid:.3f}; wcl_60 residual = {resid_pt[i60]:.3f} "
           f"(rank {rank60}/19, 1 = worst; ratio to median = {ratio60:.2f}).",
           "",
           "Registered leans: (a) carry-over a1~+0.1/a2~0 small resid; (b) wcl_20 a2~+0.15, "
           "wcl_07 a2~-0.15..-0.2, small resids; (c) wcl_60 worst resid (sharp MA test); "
           "(d) one-step echoes resid > carry-over set. KILL: wcl_60 resid ~ median."]
    (OUT_DIR / "V6_W8_AR2_TRIANGLE.md").write_text("\n".join(md) + "\n")
    print("\nwritten:", OUT_DIR / "V6_W8_AR2_TRIANGLE.json")
    print("written:", OUT_DIR / "V6_W8_AR2_TRIANGLE.md")


if __name__ == "__main__":
    main()
