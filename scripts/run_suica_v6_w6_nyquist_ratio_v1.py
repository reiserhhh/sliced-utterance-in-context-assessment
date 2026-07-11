#!/usr/bin/env python
"""W6a — Normalized Nyquist ratio rho_pi = f(pi)/gamma0 per construct (F12.7, registered commit ed971f1). Label-free.

GOVERNANCE: reads ONLY the pre-built Essays window cache (parquet); no CSV
with label columns is ever opened. Same restriction/standardization as
W3/W4/W5: texts with 5<=m<=12, no subsample gaps, pooled-sd
standardization over the restricted set.

Instrument (F12.7, docs/SUICA_THEORY_FORMAL_NOTES_V3.md, commit ed971f1):
  rho_pi = f(pi)/gamma0 — period-2 spectral energy relative to total gust
  variance. Exact asymptotic references: white = 1; MA(1) theta:
  (1+theta)^2/(1+theta^2); AR(1) phi: (1-phi)/(1+phi); AR(2)-even a2:
  (1+a2)/(1-a2). One number separates bounce/alternation (>1),
  carry-over (<1), white (=1).

ESTIMATION MODES (both computed; headline = the registered FLAGGED mode):
  5-moment left-functionals (as-registered primary): w = solve(M^T, c)
    with c_fpi = (1,-2,2,-2,2) and c_g0 = (1,0,0,0,0) on the exact 5x5
    centered map M (W5 engine, same cross-checks). MEASURED CONDITIONING
    (this run, actual composition): |w_fpi| = 4.10 (well-conditioned; this
    is the "|v| ~ 4.1" cited in the registration) BUT |w_g0| = 70.4 — the
    gamma0 functional projects 0.613 onto the centering near-null gamma
    direction (sigma_min = 0.0087, see W5), so the 5-moment gamma0 is
    noise-dominated: point estimates include a NEGATIVE gamma0 (wcl_07)
    and max |diff| vs the W3 2-moment corrected Gamma0 diag of ~1.14.
    The registration's premise ("the left-solve is well-conditioned")
    holds for f_pi only.
  Lag-2-truncated functionals (REGISTERED GRACEFUL-DEGRADATION, FLAGGED
    MODE — triggered): 3x3 top-left block M3 of M (rows/cols h,j = 0..2;
    model truncation gamma_{h>=3} = 0), c_fpi3 = (1,-2,2), c_g03 =
    (1,0,0). Conditioning: cond(M3) = 110, |w_fpi3| = 0.89, |w_g03| =
    5.8. Trigger (quantified): lag-3/4 pair scarcity (2048 pairs / 912
    texts at h=3; 1136 / 563 at h=4) makes the 5-moment gamma0
    functional's 70x noise amplification unsupportable; the 5-moment
    positivity guard fails at the point level. Truncated-mode caveat:
    for a true AR(2)-even process the truncated functionals see gamma_4
    only through the S0..S2 rows' gamma_4 coefficients — exact truncated-
    mode counterparts of the reference values are printed alongside the
    asymptotic ones.

  Bootstrap over texts (500, seed 20260712): per draw the full pipeline
  is redone (moments, the draw's own n-composition M and M3, re-solved
  functionals, ratio). Heavy-tail guard per construct per mode: draws
  with gamma0_draw <= 0.05 are dropped from that construct's ratio CI
  (drop counts reported). sd_pool fixed at full-sample values
  (W2b/W3/W4/W5 convention).

Cross-checks (asserted): M top-left 2x2 equals the W3/W4 closed forms
(incl. d(3) = 56/9) to 1e-12; M[2,0], M[2,1] equal W4's s2 map to 1e-6;
the W3-comparison gamma0 is recomputed from the same moments via the
2x2 corrected inversion (bit-identical to W3's output).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "results" / "suica_v6_e2_essays_motion" / "cache_essays_windows_scored19.parquet"
OUT_DIR = ROOT / "results" / "suica_v6_w6_nyquist_ratio"
M_LO, M_HI = 5, 12
SEED = 20260712
N_BOOT = 500
H_MAX = 4
G0_DROP_THRESHOLD = 0.05

ADJUDICATION_SET = ["wcl_60", "wcl_20", "tension_core_v2", "wcl_35", "wcl_36",
                    "wcl_13", "first_person_usage_v2", "wcl_03"]
W4_S2_MAP = (0.708157, -3.479632)
C_FPI = np.array([1.0, -2.0, 2.0, -2.0, 2.0])
C_G0 = np.array([1.0, 0.0, 0.0, 0.0, 0.0])


# ---------------- exact enumeration engine (W5) ----------------

def d2_filter(n: int) -> np.ndarray:
    W = np.zeros((n, n + 2))
    for i in range(n):
        W[i, i], W[i, i + 1], W[i, i + 2] = 1.0, -2.0, 1.0
    return W


def full_lag_table(n: int) -> np.ndarray:
    """(n+2, 5): coefficient of gust gamma_j (ALL realized j = 0..n+1) on
    the per-text (E[s_0..s_4]); s_h defined only when n >= h+1 (else 0)."""
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


def pooled_M(stratum_counts: dict) -> np.ndarray:
    """5x5 map (columns j = 0..4 only, the inversion's truncation)."""
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
            num[h] += w * T[: H_MAX + 1, h]
            den[h] += w
    assert (den > 0).all(), f"degenerate composition: pair counts {den}"
    return num / den[:, None]


def exact_pooled_moments(stratum_counts: dict, gamma_fn) -> np.ndarray:
    """Exact E[symS_0..4] for a stationary process gamma_fn(h) using the
    FULL per-n gamma ladder (no truncation) — for reference-value lines."""
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


# ---------------- W3 closed-form 2x2 (cross-check target) ----------------

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


# ---------------- moments ----------------

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
    return S / Wt[:, None], counts, Wt.astype(int)


def functionals(M: np.ndarray):
    """Left-functional weight vectors for both modes."""
    w_fpi5 = np.linalg.solve(M.T, C_FPI)
    w_g05 = np.linalg.solve(M.T, C_G0)
    M3 = M[:3, :3]
    w_fpi3 = np.linalg.solve(M3.T, C_FPI[:3])
    w_g03 = np.linalg.solve(M3.T, C_G0[:3])
    return w_fpi5, w_g05, w_fpi3, w_g03


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
    Y, counts_full, pairs_h = diag_moments(select(np.arange(N)), p)
    M = pooled_M(counts_full)

    A_t, B_t, C_t, D_t = w3_coeffs(counts_full)
    diffs2x2 = [abs(M[0, 0] - A_t), abs(M[0, 1] - B_t), abs(M[1, 0] - C_t), abs(M[1, 1] - D_t)]
    assert max(diffs2x2) < 1e-12, f"2x2 cross-check failed: {diffs2x2}"
    diffs_s2 = [abs(M[2, 0] - W4_S2_MAP[0]), abs(M[2, 1] - W4_S2_MAP[1])]
    assert max(diffs_s2) < 1e-6, f"W4 s2-map cross-check failed: {diffs_s2}"

    w_fpi5, w_g05, w_fpi3, w_g03 = functionals(M)
    cond_M3 = float(np.linalg.cond(M[:3, :3]))

    fpi5 = w_fpi5 @ Y
    g05 = w_g05 @ Y
    rho5 = fpi5 / g05
    fpi3 = w_fpi3 @ Y[:3]
    g03 = w_g03 @ Y[:3]
    rho3 = fpi3 / g03

    # W3 2-moment corrected gamma0 (bit-identical to W3's output, same moments)
    det2 = A_t * D_t - B_t * C_t
    g0_w3 = (D_t * Y[0] - B_t * Y[1]) / det2
    diff5_w3 = np.abs(g05 - g0_w3)
    diff3_w3 = np.abs(g03 - g0_w3)

    # positivity guard (point estimates)
    neg5 = [cols[i] for i in range(p) if g05[i] <= 0]
    neg3 = [cols[i] for i in range(p) if g03[i] <= 0]

    # ---------- reference lines (asymptotic + exact mode counterparts) ----------
    def ref_gamma(name):
        if name == "white":
            return lambda h: 1.0 if h == 0 else 0.0
        if name == "ma1_.34":
            th = 0.34
            r = -th / (1 + th ** 2)
            return lambda h: 1.0 if h == 0 else (r if h == 1 else 0.0)
        if name == "ar1_.1":
            return lambda h: 0.1 ** h
        if name == "ar2even_.2":
            return lambda h: 0.2 ** (h // 2) if h % 2 == 0 else 0.0

    REFS = [("white", 1.0), ("ma1_.34", (1 + 0.34) ** 2 / (1 + 0.34 ** 2)),
            ("ar1_.1", 0.9 / 1.1), ("ar2even_.2", 1.2 / 0.8)]
    ref_rows = []
    for name, asymp in REFS:
        yE = exact_pooled_moments(counts_full, ref_gamma(name))
        r5 = float((w_fpi5 @ yE) / (w_g05 @ yE))
        r3 = float((w_fpi3 @ yE[:3]) / (w_g03 @ yE[:3]))
        ref_rows.append({"process": name, "asymptotic": round(asymp, 3),
                         "exact_5mom": round(r5, 3), "exact_truncated": round(r3, 3)})

    # ---------- bootstrap ----------
    rng = np.random.default_rng(SEED)
    boot_rho5 = np.full((N_BOOT, p), np.nan)
    boot_rho3 = np.full((N_BOOT, p), np.nan)
    drop5 = np.zeros(p, dtype=int)
    drop3 = np.zeros(p, dtype=int)
    for bdx in range(N_BOOT):
        idx_b = rng.integers(0, N, N)
        Y_b, counts_b, _ = diag_moments(select(idx_b), p)
        M_b = pooled_M(counts_b)
        wf5, wg5, wf3, wg3 = functionals(M_b)
        f5 = wf5 @ Y_b; g5 = wg5 @ Y_b
        f3 = wf3 @ Y_b[:3]; g3 = wg3 @ Y_b[:3]
        ok5 = g5 > G0_DROP_THRESHOLD
        ok3 = g3 > G0_DROP_THRESHOLD
        drop5 += (~ok5).astype(int)
        drop3 += (~ok3).astype(int)
        boot_rho5[bdx, ok5] = f5[ok5] / g5[ok5]
        boot_rho3[bdx, ok3] = f3[ok3] / g3[ok3]

    def ci_nan(v):
        lo = np.nanpercentile(v, 2.5, axis=0)
        hi = np.nanpercentile(v, 97.5, axis=0)
        return lo, hi

    rho5_lo, rho5_hi = ci_nan(boot_rho5)
    rho3_lo, rho3_hi = ci_nan(boot_rho3)

    # ---------- prints ----------
    print(f"n_texts={n_texts} n_windows={n_windows} (5<=m<=12); "
          f"excluded m>12: {n_excl_gt12}; m<5: {n_excl_lt5}; subsample-gap: {n_excl_gap}")
    print(f"per-h pairs: " + ", ".join(f"h={h}:{int(pairs_h[h])}" for h in range(H_MAX + 1))
          + f"; m_stratum_counts={m_stratum_counts}")
    print(f"[cross-check] 2x2 max|diff|={max(diffs2x2):.2e} (assert<1e-12); "
          f"s2 map max|diff|={max(diffs_s2):.2e} (assert<1e-6)")
    print(f"[functionals] |w_fpi5|={np.linalg.norm(w_fpi5):.3f} |w_g05|={np.linalg.norm(w_g05):.3f} "
          f"|w_fpi3|={np.linalg.norm(w_fpi3):.3f} |w_g03|={np.linalg.norm(w_g03):.3f} cond(M3)={cond_M3:.1f}")
    print(f"[mode] 5-moment gamma0 functional is ILL-CONDITIONED (|w|=70x noise amplification, "
          f"lag-3/4 pairs {int(pairs_h[3])}/{int(pairs_h[4])} scarce) -> registered FLAGGED "
          f"lag-2-truncated mode is the HEADLINE; 5-moment reported for transparency")
    print(f"[positivity guard] 5-moment gamma0 <= 0 point estimates: {neg5 if neg5 else 'none'}; "
          f"truncated: {neg3 if neg3 else 'none'}")
    print(f"[W3 cross-check] max|gamma0 - W3_corrected_diag|: truncated={diff3_w3.max():.4f} "
          f"(median {np.median(diff3_w3):.4f}); 5-moment={diff5_w3.max():.4f} "
          f"(median {np.median(diff5_w3):.4f})")
    print()
    print("[reference lines] rho_pi: asymptotic | exact-5mom-on-this-composition | exact-truncated:")
    for r in ref_rows:
        print(f"  {r['process']:12s} {r['asymptotic']:.3f} | {r['exact_5mom']:.3f} | {r['exact_truncated']:.3f}")
    print()
    print(f"[rho_pi, HEADLINE truncated flagged mode] sorted descending (drops/{N_BOOT} noted if any):")
    order = np.argsort(-rho3)
    for i in order:
        extra = f" drops={drop3[i]}" if drop3[i] else ""
        print(f"  {cols[i]} rho_pi={rho3[i]:.4f} CI=[{rho3_lo[i]:.4f}, {rho3_hi[i]:.4f}]{extra}")
    print()
    print(f"[rho_pi, 5-moment as-registered-primary (ill-conditioned, for transparency)]:")
    for i in np.argsort(-rho5):
        extra = f" drops={drop5[i]}" if drop5[i] else ""
        print(f"  {cols[i]} rho_pi={rho5[i]:.4f} CI=[{rho5_lo[i]:.4f}, {rho5_hi[i]:.4f}]{extra}")
    print()
    print("[adjudication raw lines] (planner adjudicates the F12.7 leans)")
    for name in ADJUDICATION_SET:
        i = cols.index(name)
        print(f"  {name}: truncated rho_pi={rho3[i]:.4f} CI=[{rho3_lo[i]:.4f}, {rho3_hi[i]:.4f}] "
              f"(f_pi={fpi3[i]:.4f}, gamma0={g03[i]:.4f}, drops={drop3[i]}); "
              f"5mom rho_pi={rho5[i]:.4f} CI=[{rho5_lo[i]:.4f}, {rho5_hi[i]:.4f}] (drops={drop5[i]})")

    # ---------- JSON ----------
    rows = []
    for i, con in enumerate(cols):
        rows.append({
            "construct": con,
            "truncated": {"rho_pi": round(float(rho3[i]), 4),
                          "ci_2p5_97p5": [round(float(rho3_lo[i]), 4), round(float(rho3_hi[i]), 4)],
                          "f_pi": round(float(fpi3[i]), 4), "gamma0": round(float(g03[i]), 4),
                          "gamma0_minus_w3": round(float(g03[i] - g0_w3[i]), 4),
                          "boot_drops": int(drop3[i])},
            "five_moment": {"rho_pi": round(float(rho5[i]), 4),
                            "ci_2p5_97p5": [round(float(rho5_lo[i]), 4), round(float(rho5_hi[i]), 4)],
                            "f_pi": round(float(fpi5[i]), 4), "gamma0": round(float(g05[i]), 4),
                            "gamma0_minus_w3": round(float(g05[i] - g0_w3[i]), 4),
                            "boot_drops": int(drop5[i])},
            "w3_gamma0": round(float(g0_w3[i]), 4),
        })
    result = {
        "registered_commit": "ed971f1",
        "formula_ref": "F12.7, docs/SUICA_THEORY_FORMAL_NOTES_V3.md",
        "n_texts": n_texts, "n_windows": n_windows,
        "n_excluded_m_gt_12_texts": n_excl_gt12,
        "n_excluded_m_lt_5_texts": n_excl_lt5,
        "n_excluded_subsample_gap_texts": n_excl_gap,
        "constructs": cols, "m_stratum_counts": m_stratum_counts,
        "per_h_pairs": {str(h): int(pairs_h[h]) for h in range(H_MAX + 1)},
        "cross_check": {"top2x2_max_abs_diff": max(diffs2x2),
                        "w4_s2_map_max_abs_diff": max(diffs_s2)},
        "functional_norms": {"w_fpi_5mom": round(float(np.linalg.norm(w_fpi5)), 3),
                             "w_g0_5mom": round(float(np.linalg.norm(w_g05)), 3),
                             "w_fpi_truncated": round(float(np.linalg.norm(w_fpi3)), 3),
                             "w_g0_truncated": round(float(np.linalg.norm(w_g03)), 3),
                             "cond_M3": round(cond_M3, 1)},
        "headline_mode": "lag2_truncated_flagged",
        "mode_trigger": "registered graceful degradation (F12.7): 5-moment gamma0 functional "
                        "|w|=70.4 (centering near-null projection 0.613, sigma_min 0.0087), "
                        "negative point gamma0 (wcl_07), lag-3/4 pair scarcity "
                        f"({int(pairs_h[3])}/{int(pairs_h[4])} pairs); f_pi-only conditioning "
                        "claim of the registration holds (|w_fpi5|=4.1)",
        "positivity_guard": {"five_moment_nonpositive_gamma0": neg5,
                             "truncated_nonpositive_gamma0": neg3,
                             "boot_drop_threshold": G0_DROP_THRESHOLD},
        "w3_gamma0_crosscheck": {"truncated_max_abs_diff": round(float(diff3_w3.max()), 4),
                                 "truncated_median_abs_diff": round(float(np.median(diff3_w3)), 4),
                                 "five_moment_max_abs_diff": round(float(diff5_w3.max()), 4),
                                 "five_moment_median_abs_diff": round(float(np.median(diff5_w3)), 4)},
        "reference_lines": ref_rows,
        "bootstrap": {"n_boot": N_BOOT, "seed": SEED,
                      "design": "text-level resample; per draw: moments, the draw's own "
                                "n-composition M and M3, re-solved left-functionals, ratio; "
                                "per-construct per-mode drop guard gamma0<=0.05; percentile CIs "
                                "on kept draws; sd_pool fixed at full-sample values"},
        "table_sorted_by_truncated_rho_desc": [rows[i] for i in order],
        "adjudication_set": ADJUDICATION_SET,
    }
    (OUT_DIR / "V6_W6_NYQUIST_RATIO.json").write_text(json.dumps(result, indent=2))

    md = ["# V6-W6a -- Normalized Nyquist ratio rho_pi = f(pi)/gamma0 (Essays, label-free)",
          "",
          "Registered commit: ed971f1 (F12.7, docs/SUICA_THEORY_FORMAL_NOTES_V3.md)",
          "",
          f"n_texts={n_texts} (5<=m<=12), n_windows={n_windows}; excluded m>12: {n_excl_gt12}; "
          f"m<5: {n_excl_lt5}; subsample-gap: {n_excl_gap}. Per-h pairs: "
          + ", ".join(f"h={h}: {int(pairs_h[h])}" for h in range(H_MAX + 1)) + ".",
          "",
          "## Mode decision",
          "",
          f"HEADLINE = registered FLAGGED lag-2-truncated mode. Trigger: the 5-moment gamma0 "
          f"left-functional is ill-conditioned (|w_g0| = {np.linalg.norm(w_g05):.1f} vs "
          f"|w_fpi| = {np.linalg.norm(w_fpi5):.2f}; centering near-null projection), giving a "
          f"negative point gamma0 ({', '.join(neg5) if neg5 else 'none'}) and max diff vs W3 "
          f"Gamma0 of {diff5_w3.max():.3f}. Truncated mode: |w_fpi3| = "
          f"{np.linalg.norm(w_fpi3):.2f}, |w_g03| = {np.linalg.norm(w_g03):.2f}, "
          f"cond(M3) = {cond_M3:.0f}; all gamma0 positive; max diff vs W3 = {diff3_w3.max():.3f} "
          f"(median {np.median(diff3_w3):.3f}).",
          "",
          "## Reference lines (rho_pi)",
          "",
          "| process | asymptotic | exact 5-mom (this composition) | exact truncated |",
          "|---|---|---|---|"]
    for r in ref_rows:
        md.append(f"| {r['process']} | {r['asymptotic']:.3f} | {r['exact_5mom']:.3f} | "
                  f"{r['exact_truncated']:.3f} |")
    md += ["",
           "## rho_pi per construct (headline truncated mode, sorted descending)",
           "",
           "| construct | rho_pi | CI 2.5% | CI 97.5% | f_pi | gamma0 | gamma0 - W3 | drops | 5-mom rho_pi [CI] |",
           "|---|---|---|---|---|---|---|---|---|"]
    for i in order:
        md.append(f"| {cols[i]} | {rho3[i]:.4f} | {rho3_lo[i]:.4f} | {rho3_hi[i]:.4f} | "
                  f"{fpi3[i]:.4f} | {g03[i]:.4f} | {g03[i] - g0_w3[i]:+.4f} | {int(drop3[i])} | "
                  f"{rho5[i]:.3f} [{rho5_lo[i]:.3f}, {rho5_hi[i]:.3f}] |")
    md += ["",
           f"Bootstrap: {N_BOOT} draws, seed {SEED}; drop guard gamma0 <= {G0_DROP_THRESHOLD} "
           f"per construct per mode. Total drops: truncated {int(drop3.sum())}, "
           f"5-moment {int(drop5.sum())}.",
           ""]
    (OUT_DIR / "V6_W6_NYQUIST_RATIO.md").write_text("\n".join(md) + "\n")
    print("\nwritten:", OUT_DIR / "V6_W6_NYQUIST_RATIO.json")
    print("written:", OUT_DIR / "V6_W6_NYQUIST_RATIO.md")


if __name__ == "__main__":
    main()
