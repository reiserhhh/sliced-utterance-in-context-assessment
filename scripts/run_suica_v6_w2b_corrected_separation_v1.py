#!/usr/bin/env python
"""W2b — MA(1)-corrected flow/gust separation + bounce factor on Essays (F12.1-F12.3, registered commit da07462). Label-free.

GOVERNANCE: reads ONLY the pre-built Essays window cache (parquet); no CSV
with label columns is ever opened. Restricted to texts with 5<=m<=12 (the
registered W2b corridor for the wide-difference flow kernel).

Pipeline (formulas per F12.1, docs/SUICA_THEORY_FORMAL_NOTES_V3.md):
  1. Per text (sorted by j): window matrix X_text (m x 19), standardized by
     pooled window sd over the restricted set.
  2. Second differences D2_k = X[k+1] - 2*X[k] + X[k-1], centered within text
     (subtract the text's own mean D2 row).
  3. Pooled moment matrices S0, sym(S1) (over ALL texts) -> exact MA(1)
     inversions Gamma0_hat = (7*S0 + 8*symS1)/10, B_hat = (6*Gamma0_hat - S0)/8.
  4. Corrected flow: per-m-stratum wide-difference covariance Cov_m minus
     2*Gamma0_hat/(m-1)**2, precision-pooled across strata (weights = n_m).
     Bootstrap CI (resample texts, redo steps 3-4 fully), author-half
     replication, level visibility, and the uncorrected baseline (no Gamma0
     subtraction) for comparison.
  5. Bounce factor M = -B_hat; within-text order-permutation null (destroys
     lag-1 alignment; redo steps 2-3); author-half replication; congruence
     with Gamma0_hat's top eigenvector; level visibility.
  6. Per-construct implied MA(1) theta from the B_hat/Gamma0_hat diagonal
     ratio (r_c = -theta/(1+theta**2), solved for theta in [0,1]).
"""
from __future__ import annotations

import json
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "results" / "suica_v6_e2_essays_motion" / "cache_essays_windows_scored19.parquet"
OUT_DIR = ROOT / "results" / "suica_v6_w2b_corrected_separation"
SEED = 20260712
M_LO, M_HI = 5, 12
N_BOOT = 500
N_PERM = 500
N_VIS = 200


def corr_guarded(X):
    sd = X.std(0)
    Z = np.where(sd > 0, (X - X.mean(0)) / np.where(sd > 0, sd, 1.0), 0.0)
    C = (Z.T @ Z) / max(1, len(Z) - 1)
    np.fill_diagonal(C, 1.0)
    return C


def top_eigs(C, k):
    w, V = np.linalg.eigh(C)
    order = np.argsort(w)[::-1]
    return w[order[:k]], V[:, order[:k]]


def visibility(v, L, rng, n=N_VIS):
    obs = float(v @ corr_guarded(L) @ v)
    null = []
    for _ in range(n):
        Ls = L.copy()
        for j in range(L.shape[1]):
            rng.shuffle(Ls[:, j])
        null.append(float(v @ corr_guarded(Ls) @ v))
    return obs, float(np.percentile(null, 95))


def top_loadings(v, cols, k=4):
    idx = np.argsort(-np.abs(v))[:k]
    return [f"{cols[i]}:{v[i]:+.2f}" for i in idx]


def gamma_b_hat_from_X(X_by_m: dict) -> dict:
    """Steps 2-3: per-text second differences (centered within text), pooled
    over ALL texts (across m-strata, vectorized per stratum) into S0 /
    sym(S1), then the exact F12.1 MA(1) inversions Gamma0_hat, B_hat."""
    p = None
    S0_sum = S1_sum = None
    n_d2 = n_pairs = 0
    for m_val in sorted(X_by_m):
        X = X_by_m[m_val]
        if X.shape[0] == 0:
            continue
        if p is None:
            p = X.shape[2]
            S0_sum = np.zeros((p, p))
            S1_sum = np.zeros((p, p))
        D2 = X[:, 2:, :] - 2 * X[:, 1:-1, :] + X[:, :-2, :]           # (n_m, m-2, p)
        D2c = D2 - D2.mean(axis=1, keepdims=True)                     # center within text
        flat = D2c.reshape(-1, p)
        S0_sum += flat.T @ flat
        n_d2 += flat.shape[0]
        if D2c.shape[1] >= 2:
            A = D2c[:, :-1, :].reshape(-1, p)
            Bp = D2c[:, 1:, :].reshape(-1, p)
            S1_sum += A.T @ Bp
            n_pairs += A.shape[0]
    S0 = S0_sum / n_d2
    S1 = S1_sum / n_pairs
    symS1 = (S1 + S1.T) / 2.0
    Gamma0_hat = (7 * S0 + 8 * symS1) / 10.0
    B_hat = (6 * Gamma0_hat - S0) / 8.0
    return {"S0": S0, "S1": S1, "symS1": symS1, "Gamma0_hat": Gamma0_hat,
            "B_hat": B_hat, "n_D2": n_d2, "n_pairs": n_pairs}


def sigma_flow_from_d(D_by_m: dict, Gamma0_hat: np.ndarray):
    """Step 4: per-m-stratum wide-difference covariance Cov_m, precision-
    pooled (weights n_m), with and without the 2*Gamma0_hat/(m-1)**2
    correction. Strata with fewer than 2 selected texts (can occur inside a
    bootstrap resample for the thinnest m=12 stratum) are skipped since
    cross-text covariance is undefined on a single observation."""
    p = Gamma0_hat.shape[0]
    sig_sum = np.zeros((p, p))
    sig_unc_sum = np.zeros((p, p))
    n_total = 0
    for m_val in sorted(D_by_m):
        D = D_by_m[m_val]
        n_sel = D.shape[0]
        if n_sel < 2:
            continue
        Cov_m = np.cov(D, rowvar=False)
        Sigma_m = Cov_m - 2 * Gamma0_hat / (m_val - 1) ** 2
        sig_sum += n_sel * Sigma_m
        sig_unc_sum += n_sel * Cov_m
        n_total += n_sel
    return sig_sum / n_total, sig_unc_sum / n_total, n_total


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    df = pd.read_parquet(CACHE)
    cols = [c for c in df.columns if c not in ("eid", "user_id", "j", "m", "t", "tau", "delta")]

    m_per_text = df.groupby("eid")["m"].first()
    n_excl_gt12 = int((m_per_text > M_HI).sum())
    n_excl_lt5 = int((m_per_text < M_LO).sum())
    keep_eids = m_per_text[(m_per_text >= M_LO) & (m_per_text <= M_HI)].index
    sub = df[df["eid"].isin(keep_eids)].sort_values(["eid", "j"]).reset_index(drop=True)
    n_texts = int(sub["eid"].nunique())
    n_windows = int(len(sub))

    sd_pool = sub[cols].to_numpy(float).std(0)
    sd_pool = np.where(sd_pool > 0, sd_pool, 1.0)

    texts = []
    for eid, g in sub.groupby("eid", sort=True):
        m_val = int(g["m"].iloc[0])
        X = g[cols].to_numpy(float) / sd_pool
        d = (X[-1] - X[0]) / (m_val - 1)
        texts.append({"eid": int(eid), "user_id": str(g["user_id"].iloc[0]),
                      "m": m_val, "X": X, "d": d})
    N = len(texts)

    STRATA: dict = {}
    for t in texts:
        STRATA.setdefault(t["m"], []).append(t)
    for m_val in list(STRATA):
        grp = STRATA[m_val]
        STRATA[m_val] = {"X": np.stack([t["X"] for t in grp]),
                          "d": np.stack([t["d"] for t in grp])}

    text_m = np.array([t["m"] for t in texts])
    text_user = np.array([t["user_id"] for t in texts])
    counters: dict = {}
    text_local_idx = np.empty(N, dtype=int)
    for i, t in enumerate(texts):
        text_local_idx[i] = counters.get(t["m"], 0)
        counters[t["m"]] = counters.get(t["m"], 0) + 1
    text_half = np.array([zlib.crc32(("w2::" + u).encode()) % 2 for u in text_user])

    def select(idx_array):
        X_by_m, D_by_m = {}, {}
        for m_val in STRATA:
            sel = idx_array[text_m[idx_array] == m_val]
            if sel.size == 0:
                continue
            local = text_local_idx[sel]
            X_by_m[m_val] = STRATA[m_val]["X"][local]
            D_by_m[m_val] = STRATA[m_val]["d"][local]
        return X_by_m, D_by_m

    idx_all = np.arange(N)
    X_full, D_full = select(idx_all)

    base = gamma_b_hat_from_X(X_full)
    S0, Gamma0_hat, B_hat = base["S0"], base["Gamma0_hat"], base["B_hat"]
    Sigma_corr, Sigma_uncorr, n_flow_pooled = sigma_flow_from_d(D_full, Gamma0_hat)
    vals, vecs = top_eigs(Sigma_corr, 1)
    lam_corr, V_corr = float(vals[0]), vecs[:, 0]
    vals, _ = top_eigs(Sigma_uncorr, 1)
    lam_uncorr = float(vals[0])

    # ---------- bootstrap CI for the corrected flow lambda1 (resample texts, redo steps 3-4 fully) ----------
    boot_lams = []
    for _ in range(N_BOOT):
        idx_b = rng.integers(0, N, N)
        Xb, Db = select(idx_b)
        mb = gamma_b_hat_from_X(Xb)
        Sig_b, _, _ = sigma_flow_from_d(Db, mb["Gamma0_hat"])
        boot_lams.append(float(top_eigs(Sig_b, 1)[0][0]))
    ci = [float(np.percentile(boot_lams, q)) for q in (2.5, 97.5)]

    # ---------- author-half replication (shared basis for both flow and bounce) ----------
    half_res = {}
    for h in (0, 1):
        idx_h = np.where(text_half == h)[0]
        Xh, Dh = select(idx_h)
        mh = gamma_b_hat_from_X(Xh)
        Sig_h, _, _ = sigma_flow_from_d(Dh, mh["Gamma0_hat"])
        half_res[h] = {"B_hat": mh["B_hat"], "Sigma_flow": Sig_h}
    rep_flow = abs(float(top_eigs(half_res[0]["Sigma_flow"], 1)[1][:, 0]
                         @ top_eigs(half_res[1]["Sigma_flow"], 1)[1][:, 0]))
    rep_bounce = abs(float(top_eigs(-half_res[0]["B_hat"], 1)[1][:, 0]
                           @ top_eigs(-half_res[1]["B_hat"], 1)[1][:, 0]))

    # ---------- level visibility basis: per-text mean of ALL its windows (standardized, restricted set) ----------
    L = np.stack([t["X"].mean(axis=0) for t in texts])
    vis_flow, vis_flow95 = visibility(V_corr, L, rng)

    # ---------- bounce factor ----------
    vals, vecs = top_eigs(-B_hat, 1)
    lam1_bounce, V_bounce = float(vals[0]), vecs[:, 0]

    perm_lams = []
    for _ in range(N_PERM):
        X_perm = {}
        for m_val, arr in STRATA.items():
            n_m, mlen, _ = arr["X"].shape
            perm = np.argsort(rng.random((n_m, mlen)), axis=1)
            X_perm[m_val] = np.take_along_axis(arr["X"], perm[:, :, None], axis=1)
        mp = gamma_b_hat_from_X(X_perm)
        perm_lams.append(float(top_eigs(-mp["B_hat"], 1)[0][0]))
    perm_p = float((np.array(perm_lams) >= lam1_bounce).mean())

    V_gamma0 = top_eigs(Gamma0_hat, 1)[1][:, 0]
    congr_bounce_gamma0 = abs(float(V_bounce @ V_gamma0))
    vis_bounce, vis_bounce95 = visibility(V_bounce, L, rng)

    # ---------- per-construct implied theta ----------
    theta_rows = []
    for i, c in enumerate(cols):
        r_c = float(B_hat[i, i] / Gamma0_hat[i, i])
        if r_c >= 0:
            theta_c = 0.0
        else:
            disc = 1 - 4 * r_c ** 2
            theta_c = 1.0 if disc < 0 else float(np.clip((-1 + np.sqrt(disc)) / (2 * r_c), 0.0, 1.0))
        theta_rows.append({"construct": c, "r_c": round(r_c, 4), "theta_c": round(theta_c, 4)})
    theta_sorted = sorted(theta_rows, key=lambda r: -r["theta_c"])
    top5_theta = theta_sorted[:5]

    # ================= prints =================
    print(f"n_texts={n_texts} n_windows={n_windows} (5<=m<=12); "
          f"excluded m>12: {n_excl_gt12} texts; excluded m<5: {n_excl_lt5} texts")
    print(f"S0/B diag summary: S0 diag mean={S0.diagonal().mean():.4f} "
          f"(min {S0.diagonal().min():.4f}, max {S0.diagonal().max():.4f}); "
          f"B_hat diag mean={B_hat.diagonal().mean():.4f} "
          f"(min {B_hat.diagonal().min():.4f}, max {B_hat.diagonal().max():.4f})")
    print(f"[flow] lam1_corrected={lam_corr:.4f} CI=[{ci[0]:.4f}, {ci[1]:.4f}] "
          f"lam1_uncorrected={lam_uncorr:.4f} half_rep={rep_flow:.3f} "
          f"vis={vis_flow:.3f} (null95={vis_flow95:.3f}) top_loadings={top_loadings(V_corr, cols)}")
    print(f"[bounce] lam1={lam1_bounce:.4f} perm_p={perm_p:.4f} half_rep={rep_bounce:.3f} "
          f"congr_with_Gamma0={congr_bounce_gamma0:.3f} vis={vis_bounce:.3f} "
          f"(null95={vis_bounce95:.3f}) top_loadings={top_loadings(V_bounce, cols)}")
    print("[theta] top5 implied theta: " +
          ", ".join(f"{r['construct']}:{r['theta_c']:.3f}" for r in top5_theta))

    # ================= JSON =================
    result = {
        "seed": SEED,
        "n_texts": n_texts,
        "n_windows": n_windows,
        "n_excluded_m_gt_12_texts": n_excl_gt12,
        "n_excluded_m_lt_5_texts": n_excl_lt5,
        "constructs": cols,
        "m_stratum_counts": {str(m_val): int(STRATA[m_val]["X"].shape[0]) for m_val in sorted(STRATA)},
        "n_D2": base["n_D2"], "n_pairs": base["n_pairs"], "n_flow_pooled_texts": n_flow_pooled,
        "n_boot": N_BOOT, "n_perm": N_PERM,
        "S0": [[round(float(x), 6) for x in row] for row in S0],
        "Gamma0_hat": [[round(float(x), 6) for x in row] for row in Gamma0_hat],
        "B_hat": [[round(float(x), 6) for x in row] for row in B_hat],
        "flow": {
            "lambda1_corrected": round(lam_corr, 4),
            "boot_ci_2p5_97p5": [round(ci[0], 4), round(ci[1], 4)],
            "lambda1_uncorrected": round(lam_uncorr, 4),
            "half_replication": round(rep_flow, 3),
            "level_visibility": round(vis_flow, 3),
            "level_visibility_null95": round(vis_flow95, 3),
            "top_eigenvector": [round(float(x), 4) for x in V_corr],
            "top_loadings": top_loadings(V_corr, cols),
        },
        "bounce": {
            "lambda1": round(lam1_bounce, 4),
            "perm_p": round(perm_p, 4),
            "half_replication": round(rep_bounce, 3),
            "congruence_with_Gamma0": round(congr_bounce_gamma0, 3),
            "level_visibility": round(vis_bounce, 3),
            "level_visibility_null95": round(vis_bounce95, 3),
            "top_eigenvector": [round(float(x), 4) for x in V_bounce],
            "top_loadings": top_loadings(V_bounce, cols),
        },
        "theta_table": theta_rows,
        "theta_top5": top5_theta,
    }
    (OUT_DIR / "V6_W2B_CORRECTED_SEPARATION.json").write_text(json.dumps(result, indent=2))

    md = ["# V6-W2b — MA(1)-corrected flow/gust separation + bounce factor (Essays, label-free)", "",
          f"n_texts={n_texts} (5<=m<=12), n_windows={n_windows}; "
          f"excluded m>12: {n_excl_gt12} texts; m<5: {n_excl_lt5} texts", "",
          "## Flow",
          "| lam1_corrected | CI 2.5% | CI 97.5% | lam1_uncorrected | half_rep | vis | vis_null95 |",
          "|---|---|---|---|---|---|---|",
          f"| {lam_corr:.4f} | {ci[0]:.4f} | {ci[1]:.4f} | {lam_uncorr:.4f} | {rep_flow:.3f} | "
          f"{vis_flow:.3f} | {vis_flow95:.3f} |", "",
          f"Top loadings (flow): {', '.join(top_loadings(V_corr, cols))}", "",
          "## Bounce",
          "| lambda1 | perm_p | half_rep | congr_Gamma0 | vis | vis_null95 |",
          "|---|---|---|---|---|---|",
          f"| {lam1_bounce:.4f} | {perm_p:.4f} | {rep_bounce:.3f} | {congr_bounce_gamma0:.3f} | "
          f"{vis_bounce:.3f} | {vis_bounce95:.3f} |", "",
          f"Top loadings (bounce): {', '.join(top_loadings(V_bounce, cols))}", "",
          "## Implied theta (top 5)",
          "| construct | r_c | theta_c |", "|---|---|---|"]
    md += [f"| {r['construct']} | {r['r_c']:+.4f} | {r['theta_c']:.3f} |" for r in top5_theta]
    (OUT_DIR / "V6_W2B_CORRECTED_SEPARATION.md").write_text("\n".join(md) + "\n")
    print("written:", OUT_DIR / "V6_W2B_CORRECTED_SEPARATION.md")


if __name__ == "__main__":
    main()
