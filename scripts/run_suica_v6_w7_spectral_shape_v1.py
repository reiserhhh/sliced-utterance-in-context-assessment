#!/usr/bin/env python
"""W7a — Spectral shape pair (rho_pi/2, rho_pi) with the hybrid functional (F12.8, registered commit eabc17b). Label-free.

GOVERNANCE: reads ONLY the pre-built Essays window cache (parquet); no CSV
with label columns is ever opened. Same restriction/standardization as
W3-W6: texts with 5<=m<=12, no subsample gaps, pooled-sd standardization
over the restricted set.

Instrument (F12.8, docs/SUICA_THEORY_FORMAL_NOTES_V3.md, commit eabc17b):
  f(pi/2) = gamma0 - 2*gamma2 + 2*gamma4 (c_ph = (1,0,-2,0,2));
  f(pi)   = gamma0 - 2*gamma1 + 2*gamma2 - 2*gamma3 + 2*gamma4
            (c_pi = (1,-2,2,-2,2));
  rho_pihalf = f(pi/2)/gamma0; rho_pi = f(pi)/gamma0;
  Delta_shape = rho_pihalf - rho_pi.
  Exact asymptotic references: white (1, 1, 0); MA(1) ANY theta:
  rho_pihalf = 1 EXACTLY (gamma2 = 0) — sharp invariant; AR(1) phi:
  rho_pihalf = (1-phi^2)/(1+phi^2) (~0.980 at phi=.1), Delta ~ +0.162;
  AR(2)-even a2: rho_pihalf = (1-a2)/(1+a2) (0.667 at a2=.2),
  Delta ~ -0.833. Sign of Delta_shape separates carry-over (positive)
  from even-lag anomaly (negative); rho_pihalf = 1 tests pure-MA(1).

HYBRID FUNCTIONAL (per-functional conditioning discipline, from the W6a
findings): numerator spectral functionals f_pi and f_pihalf from the
5-moment left-solves on the exact 5x5 centered map M (both conditioned:
measured |w_pi| = 4.10 and |w_ph| printed by this script; registered
fallback if |w_ph| > 20 is the truncated-3 functional c = (1,0,-2) on
the 3x3 top-left block, flagged mode); DENOMINATOR gamma0 from the
truncated-3 left-solve c0 = (1,0,0) (|w| = 5.77, the W6a headline
gamma0 — all 19 point estimates positive there).

EXACT INVARIANT CHECKS (asserted at runtime): for a lag-2-banded process
both hybrid functionals are exactly identified on any composition, so
the exact-on-composition MA(1) reference must give rho_pihalf = 1 to
1e-9, and white must give (1, 1, 0) to 1e-9. AR(1)/AR(2)-even
exact-on-composition values (computed with full per-n gamma ladders, no
truncation of the PROCESS) are printed next to the asymptotic ones —
they differ through the estimator's gamma_(h>=5) blindness and the
lag-3/4 pair weighting.

Bootstrap over texts (500, seed 20260712): per draw the full pipeline is
redone (moments, the draw's own n-composition M/M3, re-solved
functionals; the pihalf MODE is fixed by the full-sample decision, not
re-decided per draw). Per-construct drop guard gamma0 <= 0.05 as W6a.
Pairwise shape comparisons P(Delta[a] < Delta[b]) are computed over
paired draws where both constructs survive the guard. sd_pool fixed at
full-sample values (W2b/W3-W6 convention).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "results" / "suica_v6_e2_essays_motion" / "cache_essays_windows_scored19.parquet"
OUT_DIR = ROOT / "results" / "suica_v6_w7_spectral_shape"
M_LO, M_HI = 5, 12
SEED = 20260712
N_BOOT = 500
H_MAX = 4
G0_DROP_THRESHOLD = 0.05
W_PH_FALLBACK_NORM = 20.0

C_PI = np.array([1.0, -2.0, 2.0, -2.0, 2.0])
C_PH = np.array([1.0, 0.0, -2.0, 0.0, 2.0])
C_G0_3 = np.array([1.0, 0.0, 0.0])
C_PH_3 = np.array([1.0, 0.0, -2.0])
W4_S2_MAP = (0.708157, -3.479632)

EVEN_LAG_SET = ["wcl_20", "wcl_22", "tension_core_v2"]
CARRY_SET = ["wcl_35", "wcl_36", "wcl_13", "first_person_usage_v2", "wcl_03"]
BOUNCER_SET = ["wcl_60", "wcl_23"]
PAIRWISE = [("wcl_20", "wcl_35"), ("wcl_22", "wcl_35")]


# ---------------- exact enumeration engine (W5/W6) ----------------

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


def pooled_M(stratum_counts: dict) -> np.ndarray:
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
    return S / Wt[:, None], counts, Wt.astype(int)


def solve_functionals(M: np.ndarray, ph_mode_truncated: bool):
    w_pi = np.linalg.solve(M.T, C_PI)
    M3 = M[:3, :3]
    w_g0 = np.linalg.solve(M3.T, C_G0_3)
    if ph_mode_truncated:
        w_ph = np.linalg.solve(M3.T, C_PH_3)
    else:
        w_ph = np.linalg.solve(M.T, C_PH)
    return w_pi, w_ph, w_g0


def apply_functionals(Y: np.ndarray, w_pi, w_ph, w_g0, ph_mode_truncated: bool):
    fpi = w_pi @ Y
    fph = (w_ph @ Y[:3]) if ph_mode_truncated else (w_ph @ Y)
    g0 = w_g0 @ Y[:3]
    return fpi, fph, g0


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

    # ---------- full-sample moments, map, cross-checks ----------
    Y, counts_full, pairs_h = diag_moments(select(np.arange(N)), p)
    M = pooled_M(counts_full)

    A_t, B_t, C_t, D_t = w3_coeffs(counts_full)
    diffs2x2 = [abs(M[0, 0] - A_t), abs(M[0, 1] - B_t), abs(M[1, 0] - C_t), abs(M[1, 1] - D_t)]
    assert max(diffs2x2) < 1e-12, f"2x2 cross-check failed: {diffs2x2}"
    diffs_s2 = [abs(M[2, 0] - W4_S2_MAP[0]), abs(M[2, 1] - W4_S2_MAP[1])]
    assert max(diffs_s2) < 1e-6, f"W4 s2-map cross-check failed: {diffs_s2}"

    # mode decision on the pihalf functional
    w_ph5_probe = np.linalg.solve(M.T, C_PH)
    ph_mode_truncated = bool(np.linalg.norm(w_ph5_probe) > W_PH_FALLBACK_NORM)
    w_pi, w_ph, w_g0 = solve_functionals(M, ph_mode_truncated)
    norm_pi, norm_ph, norm_g0 = (float(np.linalg.norm(w)) for w in (w_pi, w_ph5_probe, w_g0))
    ph_mode = "truncated3_flagged" if ph_mode_truncated else "five_moment_primary"

    fpi, fph, g0 = apply_functionals(Y, w_pi, w_ph, w_g0, ph_mode_truncated)
    rho_pi = fpi / g0
    rho_ph = fph / g0
    delta = rho_ph - rho_pi
    neg_g0 = [cols[i] for i in range(p) if g0[i] <= 0]

    # ---------- reference lines + exact invariant asserts ----------
    def ref_gamma(name):
        if name == "white":
            return lambda h: 1.0 if h == 0 else 0.0
        if name == "ma1_+.34":
            th = 0.34
            r = -th / (1 + th ** 2)
            return lambda h: 1.0 if h == 0 else (r if h == 1 else 0.0)
        if name == "ar1_+.1":
            return lambda h: 0.1 ** h
        if name == "ar2even_.2":
            return lambda h: 0.2 ** (h // 2) if h % 2 == 0 else 0.0

    th = 0.34
    REFS = [
        ("white", (1.0, 1.0, 0.0)),
        ("ma1_+.34", (1.0, (1 + th) ** 2 / (1 + th ** 2), 1.0 - (1 + th) ** 2 / (1 + th ** 2))),
        ("ar1_+.1", ((1 - 0.01) / (1 + 0.01), 0.9 / 1.1, (1 - 0.01) / (1 + 0.01) - 0.9 / 1.1)),
        ("ar2even_.2", (0.8 / 1.2, 1.2 / 0.8, 0.8 / 1.2 - 1.2 / 0.8)),
    ]
    ref_rows = []
    for name, (aph, api, adl) in REFS:
        yE = exact_pooled_moments(counts_full, ref_gamma(name))
        e_fpi, e_fph, e_g0 = apply_functionals(yE, w_pi, w_ph, w_g0, ph_mode_truncated)
        r_ph, r_pi = float(e_fph / e_g0), float(e_fpi / e_g0)
        ref_rows.append({"process": name,
                         "asymptotic": [round(aph, 4), round(api, 4), round(adl, 4)],
                         "exact_on_composition": [round(r_ph, 4), round(r_pi, 4),
                                                  round(r_ph - r_pi, 4)]})
        if name == "white":
            assert abs(r_ph - 1) < 1e-9 and abs(r_pi - 1) < 1e-9, f"white invariant failed: {r_ph}, {r_pi}"
        if name == "ma1_+.34":
            assert abs(r_ph - 1) < 1e-9, f"MA(1) rho_pihalf=1 invariant failed: {r_ph}"

    # ---------- bootstrap ----------
    rng = np.random.default_rng(SEED)
    boot_rph = np.full((N_BOOT, p), np.nan)
    boot_rpi = np.full((N_BOOT, p), np.nan)
    boot_dlt = np.full((N_BOOT, p), np.nan)
    drops = np.zeros(p, dtype=int)
    for bdx in range(N_BOOT):
        idx_b = rng.integers(0, N, N)
        Y_b, counts_b, _ = diag_moments(select(idx_b), p)
        M_b = pooled_M(counts_b)
        w_pi_b, w_ph_b, w_g0_b = solve_functionals(M_b, ph_mode_truncated)
        f1, f2, g_b = apply_functionals(Y_b, w_pi_b, w_ph_b, w_g0_b, ph_mode_truncated)
        ok = g_b > G0_DROP_THRESHOLD
        drops += (~ok).astype(int)
        boot_rpi[bdx, ok] = f1[ok] / g_b[ok]
        boot_rph[bdx, ok] = f2[ok] / g_b[ok]
        boot_dlt[bdx, ok] = boot_rph[bdx, ok] - boot_rpi[bdx, ok]

    def ci_nan(v):
        return np.nanpercentile(v, 2.5, axis=0), np.nanpercentile(v, 97.5, axis=0)

    rph_lo, rph_hi = ci_nan(boot_rph)
    rpi_lo, rpi_hi = ci_nan(boot_rpi)
    dlt_lo, dlt_hi = ci_nan(boot_dlt)

    # pairwise paired-draw comparisons
    pair_rows = []
    for a, b in PAIRWISE:
        ia, ib = cols.index(a), cols.index(b)
        both = ~np.isnan(boot_dlt[:, ia]) & ~np.isnan(boot_dlt[:, ib])
        frac = float((boot_dlt[both, ia] < boot_dlt[both, ib]).mean())
        pair_rows.append({"pair": f"P(Delta[{a}] < Delta[{b}])", "frac": round(frac, 3),
                          "n_draws_used": int(both.sum())})

    # ---------- prints ----------
    print(f"n_texts={n_texts} n_windows={n_windows} (5<=m<=12); "
          f"excluded m>12: {n_excl_gt12}; m<5: {n_excl_lt5}; subsample-gap: {n_excl_gap}")
    print(f"per-h pairs: " + ", ".join(f"h={h}:{int(pairs_h[h])}" for h in range(H_MAX + 1))
          + f"; m_stratum_counts={m_stratum_counts}")
    print(f"[cross-check] 2x2 max|diff|={max(diffs2x2):.2e} (assert<1e-12); "
          f"s2 map max|diff|={max(diffs_s2):.2e} (assert<1e-6)")
    print(f"[functionals] |w_pi|={norm_pi:.3f} |w_pihalf_5mom|={norm_ph:.3f} "
          f"|w_gamma0_trunc3|={norm_g0:.3f}; pihalf mode = {ph_mode} "
          f"(fallback threshold {W_PH_FALLBACK_NORM})")
    print(f"[positivity] truncated-3 gamma0 <= 0 point estimates: {neg_g0 if neg_g0 else 'none'}; "
          f"boot drop guard gamma0<={G0_DROP_THRESHOLD}, total drops={int(drops.sum())} "
          f"(nonzero: " + (", ".join(f"{cols[i]}={drops[i]}" for i in range(p) if drops[i]) or "none") + ")")
    print()
    print("[reference lines] (rho_pihalf, rho_pi, Delta): asymptotic | exact-on-composition (shipped estimator):")
    for r in ref_rows:
        a1, a2_, a3 = r["asymptotic"]; e1, e2, e3 = r["exact_on_composition"]
        print(f"  {r['process']:11s} ({a1:.3f}, {a2_:.3f}, {a3:+.3f}) | ({e1:.4f}, {e2:.4f}, {e3:+.4f})")
    print("  [invariants asserted: white=(1,1,0), MA(1) rho_pihalf=1, both to 1e-9 on-composition]")
    print()
    print("[shape pair] sorted by Delta_shape ascending:")
    order = np.argsort(delta)
    for i in order:
        extra = f" drops={drops[i]}" if drops[i] else ""
        print(f"  {cols[i]} rho_pihalf={rho_ph[i]:.4f} [{rph_lo[i]:.4f},{rph_hi[i]:.4f}] "
              f"rho_pi={rho_pi[i]:.4f} [{rpi_lo[i]:.4f},{rpi_hi[i]:.4f}] "
              f"Delta={delta[i]:+.4f} [{dlt_lo[i]:+.4f},{dlt_hi[i]:+.4f}]{extra}")
    print()
    print("[adjudication raw lines] (planner adjudicates the F12.8 leans)")
    for label, group in (("even-lag flagged", EVEN_LAG_SET), ("carry-over set", CARRY_SET),
                         ("bouncers", BOUNCER_SET)):
        print(f"  -- {label}:")
        for name in group:
            i = cols.index(name)
            print(f"     {name}: rho_pihalf={rho_ph[i]:.4f} [{rph_lo[i]:.4f},{rph_hi[i]:.4f}] "
                  f"rho_pi={rho_pi[i]:.4f} [{rpi_lo[i]:.4f},{rpi_hi[i]:.4f}] "
                  f"Delta={delta[i]:+.4f} [{dlt_lo[i]:+.4f},{dlt_hi[i]:+.4f}] drops={drops[i]}")
    for r in pair_rows:
        print(f"  {r['pair']} = {r['frac']:.3f} (over {r['n_draws_used']} paired draws)")

    # ---------- JSON ----------
    rows = []
    for i, con in enumerate(cols):
        rows.append({
            "construct": con,
            "rho_pihalf": round(float(rho_ph[i]), 4),
            "rho_pihalf_ci": [round(float(rph_lo[i]), 4), round(float(rph_hi[i]), 4)],
            "rho_pi": round(float(rho_pi[i]), 4),
            "rho_pi_ci": [round(float(rpi_lo[i]), 4), round(float(rpi_hi[i]), 4)],
            "delta_shape": round(float(delta[i]), 4),
            "delta_shape_ci": [round(float(dlt_lo[i]), 4), round(float(dlt_hi[i]), 4)],
            "f_pihalf": round(float(fph[i]), 4), "f_pi": round(float(fpi[i]), 4),
            "gamma0_trunc3": round(float(g0[i]), 4),
            "boot_drops": int(drops[i]),
        })
    result = {
        "registered_commit": "eabc17b",
        "formula_ref": "F12.8, docs/SUICA_THEORY_FORMAL_NOTES_V3.md",
        "n_texts": n_texts, "n_windows": n_windows,
        "n_excluded_m_gt_12_texts": n_excl_gt12,
        "n_excluded_m_lt_5_texts": n_excl_lt5,
        "n_excluded_subsample_gap_texts": n_excl_gap,
        "constructs": cols, "m_stratum_counts": m_stratum_counts,
        "per_h_pairs": {str(h): int(pairs_h[h]) for h in range(H_MAX + 1)},
        "cross_check": {"top2x2_max_abs_diff": max(diffs2x2),
                        "w4_s2_map_max_abs_diff": max(diffs_s2)},
        "functional_norms": {"w_pi_5mom": round(norm_pi, 3),
                             "w_pihalf_5mom": round(norm_ph, 3),
                             "w_gamma0_trunc3": round(norm_g0, 3)},
        "pihalf_mode": ph_mode,
        "pihalf_fallback_threshold": W_PH_FALLBACK_NORM,
        "hybrid_design": "numerators f_pi, f_pihalf = 5-moment left-solves; denominator "
                         "gamma0 = truncated-3 left-solve (per-functional conditioning "
                         "discipline, F12.8)",
        "invariants_asserted": ["white (1,1,0) exact-on-composition to 1e-9",
                                "MA(1) rho_pihalf = 1 exact-on-composition to 1e-9"],
        "positivity": {"trunc3_nonpositive_gamma0": neg_g0,
                       "boot_drop_threshold": G0_DROP_THRESHOLD,
                       "total_drops": int(drops.sum())},
        "reference_lines": ref_rows,
        "bootstrap": {"n_boot": N_BOOT, "seed": SEED,
                      "design": "text-level resample; per draw: moments, the draw's own "
                                "n-composition M/M3, re-solved functionals (pihalf mode fixed "
                                "by the full-sample decision); drop guard gamma0<=0.05; "
                                "percentile CIs on kept draws; sd_pool fixed at full-sample "
                                "values"},
        "table_sorted_by_delta_asc": [rows[i] for i in order],
        "pairwise_paired_draw_comparisons": pair_rows,
        "adjudication_groups": {"even_lag_flagged": EVEN_LAG_SET,
                                "carry_over_set": CARRY_SET,
                                "bouncers": BOUNCER_SET},
    }
    (OUT_DIR / "V6_W7_SPECTRAL_SHAPE.json").write_text(json.dumps(result, indent=2))

    md = ["# V6-W7a -- Spectral shape pair (rho_pi/2, rho_pi) with hybrid functionals (Essays, label-free)",
          "",
          "Registered commit: eabc17b (F12.8, docs/SUICA_THEORY_FORMAL_NOTES_V3.md)",
          "",
          f"n_texts={n_texts} (5<=m<=12), n_windows={n_windows}; excluded m>12: {n_excl_gt12}; "
          f"m<5: {n_excl_lt5}; subsample-gap: {n_excl_gap}. Per-h pairs: "
          + ", ".join(f"h={h}: {int(pairs_h[h])}" for h in range(H_MAX + 1)) + ".",
          "",
          f"Hybrid functionals: |w_pi| = {norm_pi:.2f}, |w_pihalf(5-mom)| = {norm_ph:.2f} "
          f"(mode: {ph_mode}; fallback threshold {W_PH_FALLBACK_NORM}), "
          f"|w_gamma0(trunc-3)| = {norm_g0:.2f}. Invariants asserted on-composition: "
          "white = (1, 1, 0), MA(1) rho_pihalf = 1 (1e-9).",
          "",
          "## Reference lines (rho_pihalf, rho_pi, Delta)",
          "",
          "| process | asymptotic | exact on this composition |",
          "|---|---|---|"]
    for r in ref_rows:
        a1, a2_, a3 = r["asymptotic"]; e1, e2, e3 = r["exact_on_composition"]
        md.append(f"| {r['process']} | ({a1:.3f}, {a2_:.3f}, {a3:+.3f}) | ({e1:.4f}, {e2:.4f}, {e3:+.4f}) |")
    md += ["",
           "## Shape pair per construct (sorted by Delta_shape ascending)",
           "",
           "| construct | rho_pihalf | CI | rho_pi | CI | Delta_shape | CI | drops |",
           "|---|---|---|---|---|---|---|---|"]
    for i in order:
        md.append(f"| {cols[i]} | {rho_ph[i]:.4f} | [{rph_lo[i]:.4f}, {rph_hi[i]:.4f}] | "
                  f"{rho_pi[i]:.4f} | [{rpi_lo[i]:.4f}, {rpi_hi[i]:.4f}] | "
                  f"{delta[i]:+.4f} | [{dlt_lo[i]:+.4f}, {dlt_hi[i]:+.4f}] | {int(drops[i])} |")
    md += ["",
           "## Pairwise paired-draw comparisons",
           ""]
    for r in pair_rows:
        md.append(f"- {r['pair']} = {r['frac']:.3f} (n = {r['n_draws_used']} draws)")
    md += ["",
           f"Bootstrap: {N_BOOT} draws, seed {SEED}; drop guard gamma0 <= {G0_DROP_THRESHOLD}; "
           f"total drops {int(drops.sum())}."]
    (OUT_DIR / "V6_W7_SPECTRAL_SHAPE.md").write_text("\n".join(md) + "\n")
    print("\nwritten:", OUT_DIR / "V6_W7_SPECTRAL_SHAPE.json")
    print("written:", OUT_DIR / "V6_W7_SPECTRAL_SHAPE.md")


if __name__ == "__main__":
    main()
