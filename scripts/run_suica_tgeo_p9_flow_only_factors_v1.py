#!/usr/bin/env python
"""T-GEO-P9 — flow-only factors (F10.8). Label-free, Tier-U. Reuses the P8
window cache (no re-scoring).

Model per comment: w_k = p + k*s + g_k with Cov(p)=Pi (stable), Cov(s)=Sigma_flow
(ordered flow), Cov(g)=Gamma (gust). Averaging kills gust coherence at 1/m
("stop and the togetherness disappears"); differencing reads motion.

Phases:
  A (existence, all m>=2): D = last - first. Supra-edge components of corr(D)
    (within-column shuffle edge), user-half replication, static visibility of
    each component v via v' C_L v against shuffled-L draws.
  B (flow vs gust, m=3 exact contrasts): l = (w2-w0)/2, q = (w0-2w1+w2)/sqrt(6),
    columns standardized by pooled window sd so Cov(l) = Sigma_flow + Gamma/2 and
    Cov(q) = Gamma share units; Sigma_hat = Cov(l) - Cov(q)/2. Gates for a
    FLOW-ONLY factor: (i) lambda1(Sigma_hat) bootstrap CI excludes 0 AND exceeds
    the window-order permutation draws (attenuation null, stated); (ii) user-half
    replication of the leading vector; (iii) level-space invisibility.
    Gust factors: same gates (edge/replication/invisibility) on corr(q).
  C (person flow-style): per-user mean D over their long comments (gate >= 3);
    corr structure vs the same cohort's person-level static factors.

Registered leans (F10.8, commit a493ff6): A yes; B no-at-this-power (open);
C one component led by first_person/directive decline co-movement.
"""
from __future__ import annotations

import json
import sys
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_suica_c2_purity_all19_v1 as a19  # noqa: E402
from scripts.run_suica_tgeo_p8_functionalization_v1 import scored_windows  # noqa: E402

OUT_DIR = ROOT / "results" / "suica_tgeo_p9_flow_only_factors"
SEED = 20260711
N_SHUF = 500
N_BOOT = 500
N_PERM = 500


def corr_guarded(X: np.ndarray) -> np.ndarray:
    sd = X.std(0)
    Z = np.where(sd > 0, (X - X.mean(0)) / np.where(sd > 0, sd, 1.0), 0.0)
    C = (Z.T @ Z) / max(1, len(Z) - 1)
    np.fill_diagonal(C, 1.0)
    return C


def top_eigs(C: np.ndarray, k: int = 4):
    w, V = np.linalg.eigh(C)
    order = np.argsort(w)[::-1]
    return w[order[:k]], V[:, order[:k]]


def shuffle_edge(X: np.ndarray, rng, n=N_SHUF) -> float:
    mx = []
    for _ in range(n):
        Xs = X.copy()
        for j in range(X.shape[1]):
            rng.shuffle(Xs[:, j])
        mx.append(top_eigs(corr_guarded(Xs), 1)[0][0])
    return float(np.percentile(mx, 95))


def visibility(v: np.ndarray, L: np.ndarray, rng, n=200) -> tuple[float, float]:
    """v' corr(L) v observed, and the 95th pct under within-column shuffles."""
    obs = float(v @ corr_guarded(L) @ v)
    null = []
    for _ in range(n):
        Ls = L.copy()
        for j in range(L.shape[1]):
            rng.shuffle(Ls[:, j])
        null.append(float(v @ corr_guarded(Ls) @ v))
    return obs, float(np.percentile(null, 95))


def top_loadings(v: np.ndarray, cols: list[str], k=4) -> list[str]:
    idx = np.argsort(-np.abs(v))[:k]
    return [f"{cols[i]}:{v[i]:+.2f}" for i in idx]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    src, cols = scored_windows()
    src = src.sort_values(["cid", "j"]).reset_index(drop=True)
    rng = np.random.default_rng(SEED)
    p = len(cols)

    g = src.groupby("cid")
    first = g[cols].first()   # rows sorted by j within cid -> first/last window
    last = g[cols].last()
    mean = g[cols].mean()
    users = g["user_id"].first()
    D = last.to_numpy(float) - first.to_numpy(float)
    L = mean.to_numpy(float)
    print(f"[A] comments {len(D)}, users {users.nunique()}")

    result: dict = {"constructs": cols}

    # ---- Phase A: existence at scale ----
    C_D = corr_guarded(D)
    edge_D = shuffle_edge(D, rng)
    lam, V = top_eigs(C_D, 6)
    kA = int((lam > edge_D).sum())
    half = np.array([zlib.crc32(("p9::" + u).encode()) % 2 for u in users])
    _, V0 = top_eigs(corr_guarded(D[half == 0]), max(kA, 1))
    _, V1 = top_eigs(corr_guarded(D[half == 1]), max(kA, 1))
    comps = []
    for i in range(kA):
        congr = max(abs(float(V0[:, i] @ V1[:, j2])) for j2 in range(max(kA, 1)))
        vis, vis95 = visibility(V[:, i], L, rng)
        comps.append({"rank": i + 1, "lambda": round(float(lam[i]), 3),
                      "half_congruence": round(congr, 3),
                      "level_visibility": round(vis, 3),
                      "level_shuffle_p95": round(vis95, 3),
                      "top_loadings": top_loadings(V[:, i], cols)})
        print(f"  [A comp{i+1}] lam={lam[i]:.3f} (edge {edge_D:.3f}) congr={congr:.3f} "
              f"vis={vis:.3f} (L-null95 {vis95:.3f}) {comps[-1]['top_loadings']}")
    result["phase_A"] = {"n": int(len(D)), "edge": round(edge_D, 4),
                         "k_supra": kA, "components": comps}

    # ---- Phase B: flow vs gust on m=3 ----
    m3 = src[src["m"] == 3]
    cnt = m3.groupby("cid").size()
    m3 = m3[m3["cid"].isin(cnt.index[cnt == 3])].sort_values(["cid", "j"])
    W = m3[cols].to_numpy(float).reshape(-1, 3, p)
    u3 = m3.groupby("cid")["user_id"].first().to_numpy()
    sd_w = m3[cols].to_numpy(float).std(0)
    sd_w = np.where(sd_w > 0, sd_w, 1.0)
    lin = ((W[:, 2, :] - W[:, 0, :]) / 2.0) / sd_w
    cur = ((W[:, 0, :] - 2 * W[:, 1, :] + W[:, 2, :]) / np.sqrt(6.0)) / sd_w
    Lm3 = W.mean(axis=1)
    n3 = len(lin)
    print(f"[B] m=3 comments {n3}")

    Cl = np.cov(lin, rowvar=False)
    Cq = np.cov(cur, rowvar=False)
    Sig = Cl - Cq / 2.0
    lamS, VS = top_eigs(Sig, 3)
    boot = []
    for _ in range(N_BOOT):
        b = rng.integers(0, n3, n3)
        Sb = np.cov(lin[b], rowvar=False) - np.cov(cur[b], rowvar=False) / 2.0
        boot.append(top_eigs(Sb, 1)[0][0])
    ci = [float(np.percentile(boot, q)) for q in (2.5, 97.5)]
    # attenuation null: permute window order within comment (kills ordered flow
    # only partially: E[(c-a)^2]=2 vs observed 4 — stated in F10.8)
    perm_l1 = []
    for _ in range(N_PERM):
        idx = np.argsort(rng.random((n3, 3)), axis=1)
        Wp = W[np.arange(n3)[:, None], idx, :]
        lp = ((Wp[:, 2, :] - Wp[:, 0, :]) / 2.0) / sd_w
        cp = ((Wp[:, 0, :] - 2 * Wp[:, 1, :] + Wp[:, 2, :]) / np.sqrt(6.0)) / sd_w
        perm_l1.append(top_eigs(np.cov(lp, rowvar=False) - np.cov(cp, rowvar=False) / 2.0, 1)[0][0])
    p_perm = float((np.array(perm_l1) >= lamS[0]).mean())
    h3 = np.array([zlib.crc32(("p9::" + u).encode()) % 2 for u in u3])
    Sig0 = np.cov(lin[h3 == 0], rowvar=False) - np.cov(cur[h3 == 0], rowvar=False) / 2.0
    Sig1 = np.cov(lin[h3 == 1], rowvar=False) - np.cov(cur[h3 == 1], rowvar=False) / 2.0
    _, Va = top_eigs(Sig0, 1)
    _, Vb = top_eigs(Sig1, 1)
    rep = abs(float(Va[:, 0] @ Vb[:, 0]))
    visF, visF95 = visibility(VS[:, 0], Lm3, rng)
    print(f"  [B flow] lam1(Sigma_hat)={lamS[0]:.4f} bootCI={ci} perm-p={p_perm:.4f} "
          f"half-rep={rep:.3f} vis={visF:.3f} (null95 {visF95:.3f}) "
          f"{top_loadings(VS[:, 0], cols)}")

    Cq_corr = corr_guarded(cur)
    edge_q = shuffle_edge(cur, rng)
    lamq, Vq = top_eigs(Cq_corr, 6)
    kq = int((lamq > edge_q).sum())
    _, Vq0 = top_eigs(corr_guarded(cur[h3 == 0]), max(kq, 1))
    _, Vq1 = top_eigs(corr_guarded(cur[h3 == 1]), max(kq, 1))
    gusts = []
    for i in range(kq):
        congr = max(abs(float(Vq0[:, i] @ Vq1[:, j2])) for j2 in range(max(kq, 1)))
        vis, vis95 = visibility(Vq[:, i], Lm3, rng)
        gusts.append({"rank": i + 1, "lambda": round(float(lamq[i]), 3),
                      "half_congruence": round(congr, 3),
                      "level_visibility": round(vis, 3), "level_shuffle_p95": round(vis95, 3),
                      "top_loadings": top_loadings(Vq[:, i], cols)})
        print(f"  [B gust{i+1}] lam={lamq[i]:.3f} (edge {edge_q:.3f}) congr={congr:.3f} "
              f"vis={vis:.3f} (null95 {vis95:.3f}) {gusts[-1]['top_loadings']}")
    result["phase_B"] = {"n_m3": int(n3),
                         "flow": {"lambda1": round(float(lamS[0]), 4),
                                  "boot_ci": [round(x, 4) for x in ci],
                                  "perm_p_attenuation_null": round(p_perm, 4),
                                  "half_replication": round(rep, 3),
                                  "level_visibility": round(visF, 3),
                                  "level_shuffle_p95": round(visF95, 3),
                                  "top_loadings": top_loadings(VS[:, 0], cols)},
                         "gust_edge": round(edge_q, 4), "k_gust": kq, "gusts": gusts}

    # ---- Phase C: person flow-style ----
    dfD = pd.DataFrame(D, columns=cols).assign(user_id=users.to_numpy())
    dfL = pd.DataFrame(L, columns=cols).assign(user_id=users.to_numpy())
    ucnt = dfD["user_id"].value_counts()
    keep = ucnt.index[ucnt >= 3]
    gD = dfD[dfD["user_id"].isin(keep)].groupby("user_id")[cols].mean()
    uD = gD.to_numpy(float)
    uL = dfL[dfL["user_id"].isin(keep)].groupby("user_id")[cols].mean().to_numpy(float)
    uhalf = np.array([zlib.crc32(("p9::" + u).encode()) % 2 for u in gD.index])
    print(f"[C] users {len(uD)} (gate >= 3 long comments)")
    C_uD = corr_guarded(uD)
    edge_uD = shuffle_edge(uD, rng)
    lamu, Vu = top_eigs(C_uD, 6)
    ku = int((lamu > edge_uD).sum())
    lamuL, VuL = top_eigs(corr_guarded(uL), 4)
    _, Vu0 = top_eigs(corr_guarded(uD[uhalf == 0]), max(ku, 1))
    _, Vu1 = top_eigs(corr_guarded(uD[uhalf == 1]), max(ku, 1))
    pcomps = []
    for i in range(ku):
        congr = max(abs(float(Vu0[:, i] @ Vu1[:, j2])) for j2 in range(max(ku, 1)))
        vis, vis95 = visibility(Vu[:, i], uL, rng)
        cong_static = max(abs(float(Vu[:, i] @ VuL[:, j2])) for j2 in range(4))
        pcomps.append({"rank": i + 1, "lambda": round(float(lamu[i]), 3),
                       "half_congruence": round(congr, 3),
                       "level_visibility": round(vis, 3), "level_shuffle_p95": round(vis95, 3),
                       "max_congruence_with_static_factors": round(cong_static, 3),
                       "top_loadings": top_loadings(Vu[:, i], cols)})
        print(f"  [C comp{i+1}] lam={lamu[i]:.3f} (edge {edge_uD:.3f}) congr={congr:.3f} "
              f"vis={vis:.3f} (null95 {vis95:.3f}) static-congr={cong_static:.3f} "
              f"{pcomps[-1]['top_loadings']}")
    result["phase_C"] = {"n_users": int(len(uD)), "edge": round(edge_uD, 4),
                         "k_supra": ku, "components": pcomps}

    # cross-phase congruence of the recurring motion directions
    vA3 = V[:, 2] if kA >= 3 else None
    vB = VS[:, 0]
    vC3 = Vu[:, 2] if ku >= 3 else None
    xp = {}
    if vA3 is not None:
        xp["A3_x_Bflow"] = round(abs(float(vA3 @ vB)), 3)
    if vA3 is not None and vC3 is not None:
        xp["A3_x_C3"] = round(abs(float(vA3 @ vC3)), 3)
    if vC3 is not None:
        xp["Bflow_x_C3"] = round(abs(float(vB @ vC3)), 3)
    result["cross_phase_congruence"] = xp
    print(f"[X] cross-phase congruence: {xp}")

    (OUT_DIR / "TGEO_P9_FLOW_ONLY_FACTORS.json").write_text(json.dumps(result, indent=2))
    md = ["# T-GEO-P9 — flow-only factors (F10.8, label-free)", "",
          f"A: n={len(D)} comments, edge {edge_D:.3f}, k={kA} supra components.",
          f"B: n={n3} m=3 comments; flow lambda1 {lamS[0]:.4f} CI {ci}, perm-p {p_perm:.4f}, "
          f"half-rep {rep:.3f}; gust k={kq}.",
          f"C: n={len(uD)} users, k={ku} supra components.", "",
          "See TGEO_P9_FLOW_ONLY_FACTORS.json for full component tables."]
    (OUT_DIR / "TGEO_P9_FLOW_ONLY_FACTORS.md").write_text("\n".join(md) + "\n")
    print("written:", OUT_DIR / "TGEO_P9_FLOW_ONLY_FACTORS.md")


if __name__ == "__main__":
    main()
