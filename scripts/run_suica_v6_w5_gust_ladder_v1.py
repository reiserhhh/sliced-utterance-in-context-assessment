#!/usr/bin/env python
"""W5 — Gust-ladder inversion: exact 5x5 centered lag-structure estimate (F12.6, registered commit 6669ccc). Label-free.

GOVERNANCE: reads ONLY the pre-built Essays window cache (parquet); no CSV
with label columns is ever opened. Same restriction/standardization as
W3/W4: texts with 5<=m<=12, no subsample gaps, columns standardized by
pooled window sd over the restricted set.

Instrument (F12.6.1, docs/SUICA_THEORY_FORMAL_NOTES_V3.md, commit 6669ccc):
  1. D2 rows centered within text (as W3/W4). Pooled centered symS_h for
     h = 0..4: lag-h pairs exist for n >= h+1; weights = n-h pairs per
     text (S3 needs n>=4 i.e. m>=6; S4 needs n>=5 i.e. m>=7).
  2. EXACT 5x5 CENTERED MAP by unit-vector enumeration (the d(3) lesson —
     no hand closed forms): for each basis gamma-structure e_j (gamma_j=1,
     others 0, j=0..4), build the (n+2)x(n+2) single-band symmetric gust
     Toeplitz, form the D2 rows' covariance with the [1,-2,1] filter,
     apply the centering projection P = I - J/n, read the per-n
     (E[s_0..s_4]) coefficients, and pool under the ACTUAL n-composition
     with per-h pair weights. M[h,j] = coefficient of gamma_j in
     E[symS_h]. Cross-checks (asserted): the top-left 2x2 block equals
     the W3/W4 coefficients (A, B_coef, C, D_coef incl. d(3)=56/9) to
     1e-12; M[2,0], M[2,1] equal W4's s2 map (0.708157, -3.479632) to
     1e-6.
  3. GUST LADDER: gamma_hat = M^{-1} @ (symS_0..symS_4) per construct
     DIAGONAL (19 solves on diagonal 5-vectors), under the truncation
     assumption gamma_{h>=5} = 0. Nyquist spectral value
     f_pi = gamma0 - 2*gamma1 + 2*gamma2 - 2*gamma3 + 2*gamma4.
  4. Bootstrap over texts (N_BOOT=500, seed 20260712): each draw redoes
     moments, the DRAW's own n-composition M, and the solve; percentile
     2.5/97.5 CIs for gamma_1..gamma_4, f_pi, and the ratio statistics.
     Per-n unit-structure tables are precomputed once (they depend only
     on n and j, not the draw); per draw only the pooling weights change.

Classification (F12.6.2 rules, applied in registered order, first match):
  MA1            |g2|,|g3|,|g4| CIs all span 0
  MA2-echo       g2 CI solid, g3 and g4 CIs span 0
  STANDING-WAVE  g2 CI solid AND g4 CI solid positive
  ALTERNATION    g3 CI solid negative
  AR1-decay      g1 CI solid and the CI of (g2/g1 - g1/g0) spans 0
  else INDETERMINATE
Rule booleans and all ratio CIs are stored in the JSON so the planner can
re-adjudicate under any precedence.

Instrument-validity notes (verified before this run, recorded for the
reader): the 5x5 map was validated by exact enumeration self-consistency
(4e-16) and by planted MA(4) Monte Carlo recovery (truncation-valid case,
converges with sqrt(scale)). TRUNCATION CAVEAT: the inversion assumes
gamma_{h>=5}=0; exact-expectation checks show recovery is exact at
Essays-scale memory (AR phi=0.1), mildly shrunk at phi=+0.5, and ALIASED
for strong damped alternation (phi=-0.5 flips the sign of g3 toward 0/+)
and for non-decaying phase-locked alternation (reads as an all-positive
ladder). The AR(2)-even statistic g4/g2 tracks the true a2 well for
a2 <= ~0.5 (0.15->0.165, 0.35->0.351, 0.5->0.43). f_pi is the most
aliasing-robust output. cond(M) ~ 1.7e3: g3/g4 CIs are noise-amplified,
as anticipated by registered lean (d) (INDETERMINATE-AT-THIS-N is an
allowed verdict, no forcing).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "results" / "suica_v6_e2_essays_motion" / "cache_essays_windows_scored19.parquet"
OUT_DIR = ROOT / "results" / "suica_v6_w5_gust_ladder"
M_LO, M_HI = 5, 12
SEED = 20260712
N_BOOT = 500
H_MAX = 4

HIGHLIGHT = ["wcl_20", "wcl_22", "tension_core_v2", "wcl_60", "wcl_35", "wcl_36",
             "wcl_13", "first_person_usage_v2", "wcl_03"]

W4_S2_MAP = (0.708157, -3.479632)


# ---------------- exact enumeration engine ----------------

def d2_filter(n: int) -> np.ndarray:
    W = np.zeros((n, n + 2))
    for i in range(n):
        W[i, i], W[i, i + 1], W[i, i + 2] = 1.0, -2.0, 1.0
    return W


def unit_structure_table(n: int) -> np.ndarray:
    """(5, 5) per-n table: T[j, h] = coefficient of gamma_j (j=0..4) on the
    per-text E[s_h] (h=0..4; mean lag-h product of centered D2 rows),
    with s_h defined only when n >= h+1 (else 0)."""
    m = n + 2
    W = d2_filter(n)
    P = np.eye(n) - np.ones((n, n)) / n
    T = np.zeros((H_MAX + 1, H_MAX + 1))
    for j in range(min(H_MAX, m - 1) + 1):
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
        _TABLES[n] = unit_structure_table(n)
    return _TABLES[n]


def pooled_M(stratum_counts: dict) -> np.ndarray:
    """5x5 map M[h, j] under the given composition {m: n_texts}; per-h pair
    weights cnt*(n-h), strata with n < h+1 contribute nothing to row h."""
    num = np.zeros((H_MAX + 1, H_MAX + 1))
    den = np.zeros(H_MAX + 1)
    for m_val, cnt in stratum_counts.items():
        if cnt == 0:
            continue
        n = m_val - 2
        T = table_cached(n)
        for h in range(H_MAX + 1):
            w = cnt * (n - h)
            if w <= 0:
                continue
            num[h] += w * T[:, h]
            den[h] += w
    assert (den > 0).all(), f"degenerate composition: pair counts {den}"
    return num / den[:, None]


# ---------------- W3/W4 cross-check targets ----------------

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

def diag_moments(X_by_m: dict, p: int):
    """(5, p) pooled centered diagonal moments + composition counts + pair/text counts."""
    S = np.zeros((H_MAX + 1, p))
    Wt = np.zeros(H_MAX + 1)
    counts = {}
    texts_h = np.zeros(H_MAX + 1, dtype=int)
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
                texts_h[h] += n_m
    return S / Wt[:, None], counts, Wt.astype(int), texts_h


def full_moments(X_by_m: dict, p: int):
    """Full p x p symmetrized moment matrices for h=0..4 (full sample only)."""
    S = [np.zeros((p, p)) for _ in range(H_MAX + 1)]
    Wt = np.zeros(H_MAX + 1)
    for m_val in sorted(X_by_m):
        X = X_by_m[m_val]
        if X.shape[0] == 0:
            continue
        n = m_val - 2
        D2 = X[:, 2:, :] - 2 * X[:, 1:-1, :] + X[:, :-2, :]
        D2c = D2 - D2.mean(axis=1, keepdims=True)
        for h in range(H_MAX + 1):
            if n >= h + 1:
                if h == 0:
                    F = D2c.reshape(-1, p)
                    S[h] += F.T @ F
                else:
                    A = D2c[:, :-h, :].reshape(-1, p)
                    B = D2c[:, h:, :].reshape(-1, p)
                    S[h] += A.T @ B
                Wt[h] += D2c.shape[0] * (n - h)
    out = []
    for h in range(H_MAX + 1):
        Sh = S[h] / Wt[h]
        out.append((Sh + Sh.T) / 2.0)
    return out


def ci(v: np.ndarray, axis=0):
    return (np.percentile(v, 2.5, axis=axis), np.percentile(v, 97.5, axis=axis))


def solid(lo: float, hi: float) -> bool:
    return lo > 0 or hi < 0


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

    # ---------- full-sample moments, M, cross-checks ----------
    X_full = select(np.arange(N))
    Y, counts_full, pairs_h, texts_h = diag_moments(X_full, p)      # Y: (5, p)
    symS_full = full_moments(X_full, p)
    M = pooled_M(counts_full)

    A_cf, B_cf_, C_cf, D_cf = w3_closed_form_coeffs(counts_full)
    diffs2x2 = [abs(M[0, 0] - A_cf), abs(M[0, 1] - B_cf_), abs(M[1, 0] - C_cf), abs(M[1, 1] - D_cf)]
    assert max(diffs2x2) < 1e-12, f"2x2 cross-check failed: {diffs2x2}"
    diffs_s2 = [abs(M[2, 0] - W4_S2_MAP[0]), abs(M[2, 1] - W4_S2_MAP[1])]
    assert max(diffs_s2) < 1e-6, f"W4 s2-map cross-check failed: {diffs_s2}"

    cond_raw = float(np.linalg.cond(M))
    Dr = np.diag(1.0 / np.abs(M).sum(axis=1))
    cond_eq = float(np.linalg.cond(Dr @ M))

    G = np.linalg.solve(M, Y)                                        # (5, p) gust ladder
    FPI = G[0] - 2 * G[1] + 2 * G[2] - 2 * G[3] + 2 * G[4]           # (p,)

    # ---------- bootstrap ----------
    rng = np.random.default_rng(SEED)
    boot_G = np.empty((N_BOOT, H_MAX + 1, p))
    boot_FPI = np.empty((N_BOOT, p))
    for bdx in range(N_BOOT):
        idx_b = rng.integers(0, N, N)
        Y_b, counts_b, _, _ = diag_moments(select(idx_b), p)
        M_b = pooled_M(counts_b)
        G_b = np.linalg.solve(M_b, Y_b)
        boot_G[bdx] = G_b
        boot_FPI[bdx] = G_b[0] - 2 * G_b[1] + 2 * G_b[2] - 2 * G_b[3] + 2 * G_b[4]

    G_lo, G_hi = ci(boot_G)                                          # (5, p) each
    FPI_lo, FPI_hi = ci(boot_FPI)                                    # (p,)

    # ratio statistics per draw
    r10 = boot_G[:, 1, :] / boot_G[:, 0, :]                          # g1/g0
    r21 = boot_G[:, 2, :] / boot_G[:, 1, :]                          # g2/g1
    delta_ar = r21 - r10                                             # AR1-decay statistic
    r42 = boot_G[:, 4, :] / boot_G[:, 2, :]                          # g4/g2
    r10_lo, r10_hi = ci(r10); r21_lo, r21_hi = ci(r21)
    del_lo, del_hi = ci(delta_ar); r42_lo, r42_hi = ci(r42)

    # ---------- classification ----------
    rows = []
    for i, con in enumerate(cols):
        g_pt = G[:, i]
        gci = [(float(G_lo[h, i]), float(G_hi[h, i])) for h in range(H_MAX + 1)]
        s = {h: solid(*gci[h]) for h in (1, 2, 3, 4)}
        s3_neg = gci[3][1] < 0
        s4_pos = gci[4][0] > 0
        ar_ratio_spans0 = del_lo[i] <= 0 <= del_hi[i]
        if not s[2] and not s[3] and not s[4]:
            cls = "MA1"
        elif s[2] and not s[3] and not s[4]:
            cls = "MA2-echo"
        elif s[2] and s4_pos:
            cls = "STANDING-WAVE"
        elif s3_neg:
            cls = "ALTERNATION"
        elif s[1] and ar_ratio_spans0:
            cls = "AR1-decay"
        else:
            cls = "INDETERMINATE"
        rows.append({
            "construct": con,
            "g": [round(float(g_pt[h]), 4) for h in range(H_MAX + 1)],
            "g_ci": [[round(gci[h][0], 4), round(gci[h][1], 4)] for h in range(H_MAX + 1)],
            "f_pi": round(float(FPI[i]), 4),
            "f_pi_ci": [round(float(FPI_lo[i]), 4), round(float(FPI_hi[i]), 4)],
            "ratios": {
                "g1_over_g0": {"point": round(float(G[1, i] / G[0, i]), 4),
                               "ci": [round(float(r10_lo[i]), 4), round(float(r10_hi[i]), 4)]},
                "g2_over_g1": {"point": round(float(G[2, i] / G[1, i]), 4),
                               "ci": [round(float(r21_lo[i]), 4), round(float(r21_hi[i]), 4)]},
                "ar_decay_delta": {"point": round(float(G[2, i] / G[1, i] - G[1, i] / G[0, i]), 4),
                                   "ci": [round(float(del_lo[i]), 4), round(float(del_hi[i]), 4)]},
                "g4_over_g2": {"point": round(float(G[4, i] / G[2, i]), 4),
                               "ci": [round(float(r42_lo[i]), 4), round(float(r42_hi[i]), 4)]},
            },
            "rule_booleans": {"g1_solid": s[1], "g2_solid": s[2], "g3_solid": s[3],
                              "g4_solid": s[4], "g3_solid_neg": s3_neg, "g4_solid_pos": s4_pos,
                              "ar_ratio_ci_spans_0": bool(ar_ratio_spans0)},
            "class": cls,
        })
    by_name = {r["construct"]: r for r in rows}
    class_counts: dict = {}
    for r in rows:
        class_counts[r["class"]] = class_counts.get(r["class"], 0) + 1

    # ---------- prints ----------
    print(f"n_texts={n_texts} n_windows={n_windows} (5<=m<=12); "
          f"excluded m>12: {n_excl_gt12}; m<5: {n_excl_lt5}; subsample-gap: {n_excl_gap}")
    print("per-h pooling: " + "; ".join(
        f"h={h}: pairs={int(pairs_h[h])} texts={int(texts_h[h])}" for h in range(H_MAX + 1)))
    print(f"m_stratum_counts={m_stratum_counts}")
    print()
    print("5x5 centered map M (rows h=0..4, cols gamma_0..gamma_4):")
    for h in range(H_MAX + 1):
        print("  [" + " ".join(f"{M[h, j]:+11.6f}" for j in range(H_MAX + 1)) + "]")
    print(f"cond(M) raw={cond_raw:.1f} row-equilibrated={cond_eq:.1f}")
    print(f"[cross-check] 2x2 vs W3/W4 closed forms max|diff|={max(diffs2x2):.2e} (assert<1e-12); "
          f"M[2,0]={M[2, 0]:.6f} M[2,1]={M[2, 1]:.6f} vs W4 s2 map {W4_S2_MAP} "
          f"max|diff|={max(diffs_s2):.2e} (assert<1e-6)")
    print()

    def fmt_row(r):
        parts = [r["construct"]]
        for h in range(1, H_MAX + 1):
            parts.append(f"g{h}={r['g'][h]:+.4f} [{r['g_ci'][h][0]:+.4f},{r['g_ci'][h][1]:+.4f}]")
        parts.append(f"f_pi={r['f_pi']:+.4f} [{r['f_pi_ci'][0]:+.4f},{r['f_pi_ci'][1]:+.4f}]")
        parts.append(f"class={r['class']}")
        return " ".join(parts)

    print("[ladder, highlighted]")
    for name in HIGHLIGHT:
        print("  " + fmt_row(by_name[name]))
    print("[ladder, remaining]")
    for r in rows:
        if r["construct"] not in HIGHLIGHT:
            print("  " + fmt_row(r))
    print()
    print(f"[classes] " + " ".join(f"{k}={v}" for k, v in sorted(class_counts.items())))
    print()
    print("[lean raw numbers] (planner adjudicates)")
    for name in ("wcl_20", "wcl_22"):
        r = by_name[name]
        rr = r["ratios"]["g4_over_g2"]
        print(f"  {name}: g4={r['g'][4]:+.4f} CI=[{r['g_ci'][4][0]:+.4f},{r['g_ci'][4][1]:+.4f}] "
              f"g4/g2={rr['point']:+.4f} CI=[{rr['ci'][0]:+.4f},{rr['ci'][1]:+.4f}]")
    r = by_name["wcl_60"]
    print("  wcl_60 ladder: " + " ".join(
        f"g{h}={r['g'][h]:+.4f}[{r['g_ci'][h][0]:+.4f},{r['g_ci'][h][1]:+.4f}]" for h in range(H_MAX + 1)))
    print("  ratio table (geometric-decay check):")
    for name in ("wcl_35", "wcl_36", "wcl_13"):
        r = by_name[name]
        a, b_, d_ = r["ratios"]["g1_over_g0"], r["ratios"]["g2_over_g1"], r["ratios"]["ar_decay_delta"]
        print(f"    {name}: g1/g0={a['point']:+.4f} CI=[{a['ci'][0]:+.4f},{a['ci'][1]:+.4f}] "
              f"g2/g1={b_['point']:+.4f} CI=[{b_['ci'][0]:+.4f},{b_['ci'][1]:+.4f}] "
              f"delta={d_['point']:+.4f} CI=[{d_['ci'][0]:+.4f},{d_['ci'][1]:+.4f}]")

    # ---------- JSON ----------
    result = {
        "registered_commit": "6669ccc",
        "formula_ref": "F12.6, docs/SUICA_THEORY_FORMAL_NOTES_V3.md",
        "n_texts": n_texts, "n_windows": n_windows,
        "n_excluded_m_gt_12_texts": n_excl_gt12,
        "n_excluded_m_lt_5_texts": n_excl_lt5,
        "n_excluded_subsample_gap_texts": n_excl_gap,
        "constructs": cols,
        "m_stratum_counts": m_stratum_counts,
        "per_h_pooling": {str(h): {"pairs": int(pairs_h[h]), "texts": int(texts_h[h])}
                          for h in range(H_MAX + 1)},
        "M": [[round(float(x), 8) for x in row] for row in M],
        "cond_M": {"raw": round(cond_raw, 1), "row_equilibrated": round(cond_eq, 1)},
        "cross_check": {
            "top2x2_max_abs_diff": max(diffs2x2),
            "w4_s2_map_max_abs_diff": max(diffs_s2),
            "targets": {"A": A_cf, "B_coef": B_cf_, "C": C_cf, "D_coef": D_cf,
                        "w4_s2_map": list(W4_S2_MAP)},
        },
        "truncation_note": "ladder inverted under gamma_{h>=5}=0; see docstring "
                           "instrument-validity notes (exact at Essays-scale memory; "
                           "aliases strong damped/non-decaying alternation; g4/g2 tracks "
                           "AR(2)-even a2 for a2<=~0.5; f_pi most aliasing-robust)",
        "symS_diag": {f"S{h}": [round(float(x), 6) for x in Y[h]] for h in range(H_MAX + 1)},
        "symS_full": {f"S{h}": [[round(float(x), 6) for x in row] for row in symS_full[h]]
                      for h in range(H_MAX + 1)},
        "bootstrap": {"n_boot": N_BOOT, "seed": SEED,
                      "design": "text-level resample; per draw: diagonal moments, the draw's "
                                "own n-composition M, 5x5 solve; percentile CIs; sd_pool fixed "
                                "at full-sample values (W2b/W3/W4 convention)"},
        "ladder_table": rows,
        "class_counts": class_counts,
        "highlighted": HIGHLIGHT,
    }
    (OUT_DIR / "V6_W5_GUST_LADDER.json").write_text(json.dumps(result, indent=2))

    md = ["# V6-W5 -- Gust-ladder inversion (exact 5x5 centered map, Essays, label-free)",
          "",
          "Registered commit: 6669ccc (F12.6, docs/SUICA_THEORY_FORMAL_NOTES_V3.md)",
          "",
          f"n_texts={n_texts} (5<=m<=12), n_windows={n_windows}; excluded m>12: {n_excl_gt12}; "
          f"m<5: {n_excl_lt5}; subsample-gap: {n_excl_gap}.",
          "",
          "Per-h pooling: " + "; ".join(
              f"h={h}: pairs={int(pairs_h[h])}, texts={int(texts_h[h])}" for h in range(H_MAX + 1)),
          "",
          "## 5x5 centered map",
          "",
          "```",
          *("  [" + " ".join(f"{M[h, j]:+11.6f}" for j in range(H_MAX + 1)) + "]" for h in range(H_MAX + 1)),
          "```",
          "",
          f"cond(M): raw {cond_raw:.1f}, row-equilibrated {cond_eq:.1f}. "
          f"Cross-checks: 2x2 vs W3/W4 max diff {max(diffs2x2):.2e}; W4 s2 map max diff {max(diffs_s2):.2e}.",
          "",
          "Truncation caveat: inversion assumes gamma_(h>=5)=0 — exact at Essays-scale memory, "
          "aliases strong alternation; f_pi most robust (see script docstring).",
          "",
          "## Ladder per construct (highlighted first)",
          "",
          "| construct | g1 | g2 | g3 | g4 | f_pi | class |",
          "|---|---|---|---|---|---|---|"]
    ordered = [by_name[n] for n in HIGHLIGHT] + [r for r in rows if r["construct"] not in HIGHLIGHT]
    for r in ordered:
        cells = [r["construct"]]
        for h in range(1, H_MAX + 1):
            cells.append(f"{r['g'][h]:+.4f} [{r['g_ci'][h][0]:+.4f},{r['g_ci'][h][1]:+.4f}]")
        cells.append(f"{r['f_pi']:+.4f} [{r['f_pi_ci'][0]:+.4f},{r['f_pi_ci'][1]:+.4f}]")
        cells.append(r["class"])
        md.append("| " + " | ".join(cells) + " |")
    md += ["",
           "Classes: " + ", ".join(f"{k}={v}" for k, v in sorted(class_counts.items())),
           "",
           "## Registered-lean raw numbers (planner adjudicates)",
           ""]
    for name in ("wcl_20", "wcl_22"):
        r = by_name[name]
        rr = r["ratios"]["g4_over_g2"]
        md.append(f"- {name}: g4={r['g'][4]:+.4f} CI=[{r['g_ci'][4][0]:+.4f},{r['g_ci'][4][1]:+.4f}], "
                  f"g4/g2={rr['point']:+.4f} CI=[{rr['ci'][0]:+.4f},{rr['ci'][1]:+.4f}]")
    r = by_name["wcl_60"]
    md.append("- wcl_60 ladder: " + ", ".join(
        f"g{h}={r['g'][h]:+.4f} [{r['g_ci'][h][0]:+.4f},{r['g_ci'][h][1]:+.4f}]" for h in range(H_MAX + 1)))
    for name in ("wcl_35", "wcl_36", "wcl_13"):
        r = by_name[name]
        a, b_, d_ = r["ratios"]["g1_over_g0"], r["ratios"]["g2_over_g1"], r["ratios"]["ar_decay_delta"]
        md.append(f"- {name}: g1/g0={a['point']:+.4f} [{a['ci'][0]:+.4f},{a['ci'][1]:+.4f}], "
                  f"g2/g1={b_['point']:+.4f} [{b_['ci'][0]:+.4f},{b_['ci'][1]:+.4f}], "
                  f"delta={d_['point']:+.4f} [{d_['ci'][0]:+.4f},{d_['ci'][1]:+.4f}]")
    (OUT_DIR / "V6_W5_GUST_LADDER.md").write_text("\n".join(md) + "\n")
    print("\nwritten:", OUT_DIR / "V6_W5_GUST_LADDER.json")
    print("written:", OUT_DIR / "V6_W5_GUST_LADDER.md")


if __name__ == "__main__":
    main()
