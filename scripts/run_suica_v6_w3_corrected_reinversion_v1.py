#!/usr/bin/env python
"""W3 — Essays re-inversion with the F12.4 exact centering-bias correction (registered 0a4a97a). Label-free.

GOVERNANCE: reads ONLY the pre-built Essays window cache (parquet); no CSV
with label columns is ever opened. Restricted to texts with 5<=m<=12 (the
W2b corridor), additionally excluding any text whose actual kept row count
does not equal its recorded m (subsample gaps -- these break the D2/second-
difference construction, which assumes a contiguous, evenly-spaced window
sequence of length exactly m).

Pipeline (formulas per F12.4, docs/SUICA_THEORY_FORMAL_NOTES_V3.md, commit
0a4a97a):
  1. Per text (sorted by j): window matrix X_text (m x 19), standardized by
     pooled window sd over the restricted set.
  2. Second differences D2_k = X[k+1] - 2*X[k] + X[k-1], centered within text
     (subtract the text's own mean D2 row) -- identical construction to W2b.
  3. Pooled moment matrices S0 (over all D2 rows), sym(S1) (over adjacent D2
     pairs), exactly as W2b built them.
  4. TWO inversions of the same (S0, symS1):
       naive:     Gamma0_hat = (7*S0 + 8*symS1)/10 ; B_hat = (6*Gamma0_hat - S0)/8
       corrected: uses the actual pooled n-composition of the restricted
                  Essays set. Per-n coefficients:
                    a(n) = 6 - 4/n**2            b(n) = -8 + 4/n**2
                    c(n) = -4 + 2*(n-2)/(n**2*(n-1))
                    d(n) = 7 - 4/n**2 for n >= 4;  d(3) = 56/9 EXACTLY
                  (n=3 boundary correction to F12.4: the lag-3 D2
                  autocovariance c3 = gamma1 has no partner row inside a
                  3-row text, so the end-row covariance sum is
                  A_end(3) = (3*gamma0 - 5*gamma1)/3, not
                  (3*gamma0 - 4*gamma1)/3; the generic closed form
                  overstates d(3) by exactly 1/3. Verified by exact
                  Toeplitz-covariance enumeration (P C P with
                  P = I - J/n) and by MC at m=5, theta=0.4. a/b/c are
                  exact at all n >= 3.)
                  pooled as A = sum_t n_t*a(n_t)/sum_t n_t (and B_coef with b),
                  C = sum_t (n_t-1)*c(n_t)/sum_t (n_t-1) (and D_coef with d),
                  where n_t = m_t - 2 is the D2-row count of text t actually
                  pooled into S0/symS1. det = A*D_coef - B_coef*C;
                  Gamma0 = (D_coef*S0 - B_coef*symS1)/det;
                  B = (A*symS1 - C*S0)/det.
  5. Per-construct implied MA(1) theta from the B_hat/Gamma0_hat diagonal
     ratio (r_c = B/Gamma0 on the diagonal; theta solved via
     theta = (-1+sqrt(1-4 r_c**2))/(2 r_c) for r_c<0, clipped to [0,1];
     r_c>=0 maps to theta_c=0), computed separately for naive and corrected.
  6. Bootstrap over TEXTS (N_BOOT draws, resample texts with replacement,
     seed 20260712): each draw redoes the FULL pipeline -- D2 rows, S0/symS1,
     the pooled F12.4 coefficients from the DRAW's own n-composition, both
     inversions -- and records (a) corrected and naive B_hat diag means,
     (b) the corrected per-construct SIGNED ratio r_c = B_cc/Gamma0_cc for
     all 19 constructs. Percentile 2.5/97.5 CIs. Standardization (step 1)
     uses the full-sample pooled sd (fixed preprocessing map -- same
     convention as W2b's flow bootstrap, which also did not re-estimate
     sd_pool per draw).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "results" / "suica_v6_e2_essays_motion" / "cache_essays_windows_scored19.parquet"
OUT_DIR = ROOT / "results" / "suica_v6_w3_corrected_reinversion"
M_LO, M_HI = 5, 12
SEED = 20260712
N_BOOT = 500


def a_coef(n):
    return 6 - 4 / n ** 2


def b_coef(n):
    return -8 + 4 / n ** 2


def c_coef(n):
    return -4 + 2 * (n - 2) / (n ** 2 * (n - 1))


def d_coef(n):
    # n=3 boundary: the generic closed form 7 - 4/n**2 assumes the lag-3 D2
    # autocovariance c3 = gamma1 enters the end-row centering sum, but a
    # 3-row text has no lag-3 pair (A_end(3) = (3*gamma0 - 5*gamma1)/3, not
    # (3*gamma0 - 4*gamma1)/3), so d(3) = 56/9 exactly, not 59/9. Verified
    # by exact Toeplitz-covariance enumeration and MC at m=5. For n >= 4 the
    # generic form is exact.
    if n == 3:
        return 56.0 / 9.0
    return 7 - 4 / n ** 2


def theta_from_diag_ratio(r_c: float) -> float:
    """Same root formula used throughout W2/W2b: r_c = B_diag/Gamma0_diag."""
    if r_c >= 0:
        return 0.0
    disc = 1 - 4 * r_c ** 2
    if disc < 0:
        return 1.0
    return float(np.clip((-1 + np.sqrt(disc)) / (2 * r_c), 0.0, 1.0))


def build_moments_and_coefficients(X_by_m: dict) -> dict:
    """Steps 2-3 (identical to W2b's gamma_b_hat_from_X) plus the pooled
    F12.4 coefficient sums (A, B_coef, C, D_coef) using the ACTUAL per-
    stratum n-composition of the texts pooled into S0/symS1."""
    p = None
    S0_sum = S1_sum = None
    n_d2 = n_pairs = 0
    num_a = num_b = num_c = num_d = 0.0
    for m_val in sorted(X_by_m):
        X = X_by_m[m_val]
        n_m = X.shape[0]
        if n_m == 0:
            continue
        if p is None:
            p = X.shape[2]
            S0_sum = np.zeros((p, p))
            S1_sum = np.zeros((p, p))
        n_val = m_val - 2  # D2 rows per text in this stratum
        D2 = X[:, 2:, :] - 2 * X[:, 1:-1, :] + X[:, :-2, :]            # (n_m, n_val, p)
        D2c = D2 - D2.mean(axis=1, keepdims=True)                      # center within text
        flat = D2c.reshape(-1, p)
        S0_sum += flat.T @ flat
        n_d2 += flat.shape[0]
        if D2c.shape[1] >= 2:
            A = D2c[:, :-1, :].reshape(-1, p)
            Bp = D2c[:, 1:, :].reshape(-1, p)
            S1_sum += A.T @ Bp
            n_pairs += A.shape[0]
        # pooled F12.4 coefficient accumulation (row-count weight for a/b,
        # pair-count weight for c/d), matching the actual n_t of every text
        num_a += n_m * n_val * a_coef(n_val)
        num_b += n_m * n_val * b_coef(n_val)
        if n_val >= 2:
            num_c += n_m * (n_val - 1) * c_coef(n_val)
            num_d += n_m * (n_val - 1) * d_coef(n_val)

    S0 = S0_sum / n_d2
    S1 = S1_sum / n_pairs
    symS1 = (S1 + S1.T) / 2.0
    A_pool = num_a / n_d2
    B_pool = num_b / n_d2
    C_pool = num_c / n_pairs
    D_pool = num_d / n_pairs

    Gamma0_naive = (7 * S0 + 8 * symS1) / 10.0
    B_naive = (6 * Gamma0_naive - S0) / 8.0

    det = A_pool * D_pool - B_pool * C_pool
    Gamma0_corrected = (D_pool * S0 - B_pool * symS1) / det
    B_corrected = (A_pool * symS1 - C_pool * S0) / det

    return {
        "S0": S0, "S1": S1, "symS1": symS1, "n_D2": n_d2, "n_pairs": n_pairs,
        "A": A_pool, "B_coef": B_pool, "C": C_pool, "D_coef": D_pool, "det": det,
        "Gamma0_naive": Gamma0_naive, "B_naive": B_naive,
        "Gamma0_corrected": Gamma0_corrected, "B_corrected": B_corrected,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(CACHE)
    cols = [c for c in df.columns if c not in ("eid", "user_id", "j", "m", "t", "tau", "delta")]

    m_per_text = df.groupby("eid")["m"].first()
    n_excl_gt12 = int((m_per_text > M_HI).sum())
    n_excl_lt5 = int((m_per_text < M_LO).sum())
    keep_eids = m_per_text[(m_per_text >= M_LO) & (m_per_text <= M_HI)].index
    sub = df[df["eid"].isin(keep_eids)].sort_values(["eid", "j"]).reset_index(drop=True)

    # exclude texts whose actual kept row count != recorded m (subsample gaps)
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

    # text -> (stratum, local row) mapping so a bootstrap index array maps
    # into the stacked stratum arrays (same machinery as W2b's select())
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

    moments = build_moments_and_coefficients(select(np.arange(N)))
    S0, symS1 = moments["S0"], moments["symS1"]
    Gamma0_naive, B_naive = moments["Gamma0_naive"], moments["B_naive"]
    Gamma0_corrected, B_corrected = moments["Gamma0_corrected"], moments["B_corrected"]

    theta_rows = []
    for i, con in enumerate(cols):
        r_naive = float(B_naive[i, i] / Gamma0_naive[i, i])
        r_corrected = float(B_corrected[i, i] / Gamma0_corrected[i, i])
        theta_rows.append({
            "construct": con,
            "r_naive": round(r_naive, 4),
            "theta_naive": round(theta_from_diag_ratio(r_naive), 4),
            "r_corrected": round(r_corrected, 4),
            "theta_corrected": round(theta_from_diag_ratio(r_corrected), 4),
            "Gamma0_naive_diag": round(float(Gamma0_naive[i, i]), 4),
            "Gamma0_corrected_diag": round(float(Gamma0_corrected[i, i]), 4),
            "B_naive_diag": round(float(B_naive[i, i]), 4),
            "B_corrected_diag": round(float(B_corrected[i, i]), 4),
        })
    theta_sorted = sorted(theta_rows, key=lambda r: -r["theta_naive"])

    B_naive_diag_mean = float(np.diagonal(B_naive).mean())
    B_corrected_diag_mean = float(np.diagonal(B_corrected).mean())
    Gamma0_naive_diag_mean = float(np.diagonal(Gamma0_naive).mean())
    Gamma0_corrected_diag_mean = float(np.diagonal(Gamma0_corrected).mean())

    # ---------- bootstrap over texts (resample with replacement; each draw
    # redoes the FULL pipeline: D2, S0/symS1, the DRAW's own n-composition
    # coefficients, both inversions) ----------
    rng = np.random.default_rng(SEED)
    boot_B_corr_mean = np.empty(N_BOOT)
    boot_B_naive_mean = np.empty(N_BOOT)
    boot_r_corr = np.empty((N_BOOT, len(cols)))
    for bdx in range(N_BOOT):
        idx_b = rng.integers(0, N, N)
        mb = build_moments_and_coefficients(select(idx_b))
        boot_B_corr_mean[bdx] = float(np.diagonal(mb["B_corrected"]).mean())
        boot_B_naive_mean[bdx] = float(np.diagonal(mb["B_naive"]).mean())
        boot_r_corr[bdx] = np.diagonal(mb["B_corrected"]) / np.diagonal(mb["Gamma0_corrected"])

    ci_B_corr = [float(np.percentile(boot_B_corr_mean, q)) for q in (2.5, 97.5)]
    ci_B_naive = [float(np.percentile(boot_B_naive_mean, q)) for q in (2.5, 97.5)]
    frac_B_corr_gt0 = float((boot_B_corr_mean > 0).mean())
    r_point = np.array([float(B_corrected[i, i] / Gamma0_corrected[i, i]) for i in range(len(cols))])
    r_ci_lo = np.percentile(boot_r_corr, 2.5, axis=0)
    r_ci_hi = np.percentile(boot_r_corr, 97.5, axis=0)
    top6_idx = [int(i) for i in np.argsort(-np.abs(r_point))[:6]]
    i60 = cols.index("wcl_60")

    # =============== prints ===============
    print(f"n_texts={n_texts} n_windows={n_windows} (5<=m<=12); "
          f"excluded m>12: {n_excl_gt12} texts; excluded m<5: {n_excl_lt5} texts; "
          f"excluded subsample-gap texts: {n_excl_gap}")
    print(f"n_D2={moments['n_D2']} n_pairs={moments['n_pairs']}; "
          f"pooled coefficients A={moments['A']:.6f} B_coef={moments['B_coef']:.6f} "
          f"C={moments['C']:.6f} D_coef={moments['D_coef']:.6f} det={moments['det']:.6f}")
    print(f"m_stratum_counts={m_stratum_counts}")
    print()
    for r in theta_sorted:
        print(f"{r['construct']} naive_theta={r['theta_naive']:.4f} corrected_theta={r['theta_corrected']:.4f}")
    print()
    print(f"B_diag_mean naive={B_naive_diag_mean:.4f} corrected={B_corrected_diag_mean:.4f}")
    print(f"Gamma0_diag_mean naive={Gamma0_naive_diag_mean:.4f} corrected={Gamma0_corrected_diag_mean:.4f}")
    print()
    print(f"[bootstrap] n_boot={N_BOOT} seed={SEED} (text-level resample; full pipeline per draw)")
    print(f"[bootstrap] B_diag_mean corrected={B_corrected_diag_mean:+.4f} "
          f"CI=[{ci_B_corr[0]:+.4f}, {ci_B_corr[1]:+.4f}] frac_draws_gt_0={frac_B_corr_gt0:.3f}")
    print(f"[bootstrap] B_diag_mean naive={B_naive_diag_mean:+.4f} "
          f"CI=[{ci_B_naive[0]:+.4f}, {ci_B_naive[1]:+.4f}]")
    for i in top6_idx:
        print(f"[bootstrap] r_c corrected {cols[i]}={r_point[i]:+.4f} "
              f"CI=[{r_ci_lo[i]:+.4f}, {r_ci_hi[i]:+.4f}]")
    print(f"[bootstrap] wcl_60 corrected r_c={r_point[i60]:+.4f} "
          f"CI=[{r_ci_lo[i60]:+.4f}, {r_ci_hi[i60]:+.4f}]")

    # =============== JSON ===============
    result = {
        "registered_commit": "0a4a97a",
        "formula_ref": "F12.4, docs/SUICA_THEORY_FORMAL_NOTES_V3.md",
        "n_texts": n_texts,
        "n_windows": n_windows,
        "n_excluded_m_gt_12_texts": n_excl_gt12,
        "n_excluded_m_lt_5_texts": n_excl_lt5,
        "n_excluded_subsample_gap_texts": n_excl_gap,
        "constructs": cols,
        "m_stratum_counts": m_stratum_counts,
        "n_D2": moments["n_D2"],
        "n_pairs": moments["n_pairs"],
        "pooled_coefficients": {
            "A": round(float(moments["A"]), 6),
            "B_coef": round(float(moments["B_coef"]), 6),
            "C": round(float(moments["C"]), 6),
            "D_coef": round(float(moments["D_coef"]), 6),
            "det": round(float(moments["det"]), 6),
        },
        "S0": [[round(float(x), 6) for x in row] for row in S0],
        "symS1": [[round(float(x), 6) for x in row] for row in symS1],
        "Gamma0_naive": [[round(float(x), 6) for x in row] for row in Gamma0_naive],
        "B_naive": [[round(float(x), 6) for x in row] for row in B_naive],
        "Gamma0_corrected": [[round(float(x), 6) for x in row] for row in Gamma0_corrected],
        "B_corrected": [[round(float(x), 6) for x in row] for row in B_corrected],
        "B_diag_mean": {"naive": round(B_naive_diag_mean, 4), "corrected": round(B_corrected_diag_mean, 4)},
        "Gamma0_diag_mean": {"naive": round(Gamma0_naive_diag_mean, 4), "corrected": round(Gamma0_corrected_diag_mean, 4)},
        "theta_table_sorted_by_naive_desc": theta_sorted,
        "bootstrap": {
            "n_boot": N_BOOT,
            "seed": SEED,
            "design": "text-level resample with replacement; each draw redoes D2/S0/symS1, "
                      "the draw's own n-composition F12.4 coefficients, and both inversions; "
                      "percentile 2.5/97.5 CIs; sd_pool fixed at full-sample values (W2b convention)",
            "B_diag_mean_corrected": {
                "point": round(B_corrected_diag_mean, 4),
                "ci_2p5_97p5": [round(ci_B_corr[0], 4), round(ci_B_corr[1], 4)],
                "frac_draws_gt_0": round(frac_B_corr_gt0, 3),
            },
            "B_diag_mean_naive": {
                "point": round(B_naive_diag_mean, 4),
                "ci_2p5_97p5": [round(ci_B_naive[0], 4), round(ci_B_naive[1], 4)],
            },
            "r_c_corrected_top6_abs": [
                {"construct": cols[i], "r_c": round(float(r_point[i]), 4),
                 "ci_2p5_97p5": [round(float(r_ci_lo[i]), 4), round(float(r_ci_hi[i]), 4)]}
                for i in top6_idx
            ],
            "r_c_corrected_all": {
                cols[i]: {"r_c": round(float(r_point[i]), 4),
                          "ci_2p5_97p5": [round(float(r_ci_lo[i]), 4), round(float(r_ci_hi[i]), 4)]}
                for i in range(len(cols))
            },
            "wcl_60_r_c_corrected": {
                "r_c": round(float(r_point[i60]), 4),
                "ci_2p5_97p5": [round(float(r_ci_lo[i60]), 4), round(float(r_ci_hi[i60]), 4)],
            },
        },
    }
    (OUT_DIR / "V6_W3_CORRECTED_REINVERSION.json").write_text(json.dumps(result, indent=2))

    md = ["# V6-W3 -- Essays re-inversion with the F12.4 exact centering-bias correction (label-free)",
          "",
          f"Registered commit: 0a4a97a (F12.4, docs/SUICA_THEORY_FORMAL_NOTES_V3.md)",
          "",
          f"n_texts={n_texts} (5<=m<=12), n_windows={n_windows}; excluded m>12: {n_excl_gt12}; "
          f"m<5: {n_excl_lt5}; subsample-gap texts: {n_excl_gap}",
          "",
          f"Pooled F12.4 coefficients: A={moments['A']:.6f} B_coef={moments['B_coef']:.6f} "
          f"C={moments['C']:.6f} D_coef={moments['D_coef']:.6f} det={moments['det']:.6f}",
          "",
          "## Summary",
          "",
          "| quantity | naive | corrected |",
          "|---|---|---|",
          f"| B_diag_mean | {B_naive_diag_mean:.4f} | {B_corrected_diag_mean:.4f} |",
          f"| Gamma0_diag_mean | {Gamma0_naive_diag_mean:.4f} | {Gamma0_corrected_diag_mean:.4f} |",
          "",
          "## Per-construct implied theta (sorted by naive theta, descending)",
          "",
          "| construct | naive_theta | corrected_theta | r_naive | r_corrected |",
          "|---|---|---|---|---|"]
    md += [f"| {r['construct']} | {r['theta_naive']:.4f} | {r['theta_corrected']:.4f} | "
           f"{r['r_naive']:+.4f} | {r['r_corrected']:+.4f} |" for r in theta_sorted]
    md += ["",
           f"## Bootstrap ({N_BOOT} text-resample draws, seed {SEED})",
           "",
           "Each draw redoes the full pipeline (D2, S0/symS1, the draw's own "
           "n-composition F12.4 coefficients, both inversions). Percentile CIs.",
           "",
           "| quantity | point | CI 2.5% | CI 97.5% | frac draws > 0 |",
           "|---|---|---|---|---|",
           f"| B_diag_mean corrected | {B_corrected_diag_mean:+.4f} | {ci_B_corr[0]:+.4f} | "
           f"{ci_B_corr[1]:+.4f} | {frac_B_corr_gt0:.3f} |",
           f"| B_diag_mean naive | {B_naive_diag_mean:+.4f} | {ci_B_naive[0]:+.4f} | "
           f"{ci_B_naive[1]:+.4f} | - |",
           "",
           "### Corrected signed r_c, 6 largest |r_c| (both signs eligible)",
           "",
           "| construct | r_c | CI 2.5% | CI 97.5% |",
           "|---|---|---|---|"]
    md += [f"| {cols[i]} | {r_point[i]:+.4f} | {r_ci_lo[i]:+.4f} | {r_ci_hi[i]:+.4f} |"
           for i in top6_idx]
    md += ["",
           f"wcl_60 corrected r_c = {r_point[i60]:+.4f} CI=[{r_ci_lo[i60]:+.4f}, {r_ci_hi[i60]:+.4f}]"]
    (OUT_DIR / "V6_W3_CORRECTED_REINVERSION.md").write_text("\n".join(md) + "\n")
    print("\nwritten:", OUT_DIR / "V6_W3_CORRECTED_REINVERSION.json")
    print("written:", OUT_DIR / "V6_W3_CORRECTED_REINVERSION.md")


if __name__ == "__main__":
    main()
