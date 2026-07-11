#!/usr/bin/env python
"""T-GEO-P3 — Marchenko-Pastur edge test on the 19-construct battery.
Label-free, Tier-U. Ports the v5 round-13 spectral instrument.

Question: how many factors in the user x construct matrix exceed what a
same-shape random matrix would produce? MP null for standardized data:
eigenvalues of the correlation matrix of pure noise concentrate below
lambda_+ = (1 + sqrt(p/n))^2. Empirical null (heteroscedasticity-robust,
per the v5 round-13 caveat): independent within-column user shuffles,
500 draws, 95th percentile of the largest eigenvalue.

Two matrices are tested:
  (a) user x 19 constructs, half-mean scores, EARLY half;
  (b) the cross-half stability check: factors of early replicated in late
      (loading congruence of supra-edge components).
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

import scripts.run_suica_c2_purity_all19_v1 as a19  # noqa: E402

OUT_DIR = ROOT / "results" / "suica_tgeo_p3_mp_edge"
N_NULL = 500


def eig_corr(X: np.ndarray) -> np.ndarray:
    Z = (X - X.mean(0)) / X.std(0)
    C = (Z.T @ Z) / (len(Z) - 1)
    return np.sort(np.linalg.eigvalsh(C))[::-1]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = a19.rebuild_passA_with_text()
    scored = a19.score_slices_v2(frame[["user_id", "condition", "half", "slice_text"]])
    import scripts.run_suica_dev_anchor_performance_v1 as dav
    _, wcl_transform = dav.pandora_style_fit_and_battery()
    wcl = wcl_transform(frame["slice_text"]).reset_index(drop=True)
    src = pd.concat([frame[["user_id", "condition", "half"]].reset_index(drop=True),
                     scored[a19.V3_BATTERY].reset_index(drop=True),
                     wcl[a19.OP5_KEPT]], axis=1)
    cols = list(a19.V3_BATTERY) + list(a19.OP5_KEPT)

    um = {h: src[src["half"] == h].groupby("user_id")[cols].mean() for h in ["early", "late"]}
    users = um["early"].index.intersection(um["late"].index)
    E = um["early"].loc[users].to_numpy(float)
    L = um["late"].loc[users].to_numpy(float)
    n, p = E.shape
    print(f"matrix: {n} users x {p} constructs")

    lam = eig_corr(E)
    mp_edge = (1 + np.sqrt(p / n)) ** 2

    rng = np.random.default_rng(20260711)
    null_max = []
    for _ in range(N_NULL):
        Xs = E.copy()
        for j in range(p):
            rng.shuffle(Xs[:, j])
        null_max.append(eig_corr(Xs)[0])
    emp_edge = float(np.percentile(null_max, 95))

    k_mp = int((lam > mp_edge).sum())
    k_emp = int((lam > emp_edge).sum())

    # cross-half replication of supra-edge components
    Ze = (E - E.mean(0)) / E.std(0)
    Zl = (L - L.mean(0)) / L.std(0)
    Ce = (Ze.T @ Ze) / (n - 1)
    Cl = (Zl.T @ Zl) / (n - 1)
    we, Ve = np.linalg.eigh(Ce)
    wl, Vl = np.linalg.eigh(Cl)
    order_e = np.argsort(we)[::-1]
    order_l = np.argsort(wl)[::-1]
    congr = []
    for k in range(k_emp):
        ve = Ve[:, order_e[k]]
        # best match among late's top-k_emp components (sign/order free)
        cc = max(abs(float(ve @ Vl[:, order_l[j]])) for j in range(max(k_emp, 1)))
        congr.append(round(cc, 3))

    result = {"n_users": int(n), "p": int(p),
              "mp_edge_analytic": round(float(mp_edge), 4),
              "empirical_edge_95": round(emp_edge, 4),
              "eigenvalues_top10": [round(float(x), 4) for x in lam[:10]],
              "k_above_mp": k_mp, "k_above_empirical": k_emp,
              "cross_half_congruence_topk": congr,
              "note": ("empirical null = independent within-column shuffles, "
                       "500 draws (round-13 heteroscedasticity caveat honored); "
                       "congruence = |dot| of matched early/late eigenvectors")}
    (OUT_DIR / "TGEO_P3_MP_EDGE.json").write_text(json.dumps(result, indent=2))
    md = ["# T-GEO-P3 — MP-edge factor test, 19-construct battery (label-free)", "",
          f"n = {n} users, p = {p}. Analytic MP edge {mp_edge:.3f}; empirical",
          f"95% edge {emp_edge:.3f} (500 within-column shuffles).", "",
          f"Top eigenvalues: {[round(float(x),3) for x in lam[:8]]}",
          f"Components above MP edge: {k_mp}; above empirical edge: {k_emp}",
          f"Cross-half congruence of supra-edge components: {congr}", ""]
    (OUT_DIR / "TGEO_P3_MP_EDGE.md").write_text("\n".join(md))
    print("MP edge", round(mp_edge, 3), "| empirical", round(emp_edge, 3),
          "| k_mp", k_mp, "| k_emp", k_emp, "| congruence", congr)
    print("written:", OUT_DIR / "TGEO_P3_MP_EDGE.md")


if __name__ == "__main__":
    main()
