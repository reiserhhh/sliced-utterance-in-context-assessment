#!/usr/bin/env python
"""V6-E2 — Essays transport of the motion layer (F11.2). Label-free.

GOVERNANCE: the Essays loader reads ONLY columns [user_id, text]. The five
trait columns are never loaded; no seal is touched; the confirm-half label
budget is unaffected. One essay per author, so essay-level = author-level.

Sections:
  A position profiles (transport of P7b): per-essay linear (last-first) on
    m>=2; (first, mid, last) triple curvature on m>=3; S_3 within-essay null.
  B law-of-the-wall (m>=4, within-essay demeaned): CV-by-essay comparison of
    zones-only vs t-poly-only vs composite (matched-asymptotics analogy).
  C flow/gust separation + CROSS-CORPUS congruence with PANDORA (gust1,
    flow1, D-components, static top-4 frames) + essay-level flow-only retry.
Registered leans: F11.2 (commit 8e2b0ba).
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

from suica_core.suica import PERSONALITY_LEAK_RE, tokenize  # noqa: E402
import scripts.run_suica_c2_purity_all19_v1 as a19  # noqa: E402
from scripts.run_suica_tgeo_p8_functionalization_v1 import scored_windows  # noqa: E402

ESSAYS = ROOT / "data_sets" / "prepared" / "big5" / "essays_original_prepared.csv"
OUT_DIR = ROOT / "results" / "suica_v6_e2_essays_motion"
SEED = 20260712
WIN = 128
MAX_WINDOWS = 12
N_FLIP = 2000
N_SHUF = 500
N_BOOT = 500
HIGHLIGHT = ["first_person_usage_v2", "tension_core_v2", "directive_action_v2",
             "novelty_play_v2", "wcl_36", "wcl_54", "wcl_22", "wcl_15",
             "wcl_25", "wcl_02", "wcl_11", "wcl_07", "wcl_20"]


def corr_guarded(X):
    sd = X.std(0)
    Z = np.where(sd > 0, (X - X.mean(0)) / np.where(sd > 0, sd, 1.0), 0.0)
    C = (Z.T @ Z) / max(1, len(Z) - 1)
    np.fill_diagonal(C, 1.0)
    return C


def top_eigs(C, k=4):
    w, V = np.linalg.eigh(C)
    order = np.argsort(w)[::-1]
    return w[order[:k]], V[:, order[:k]]


def shuffle_edge(X, rng, n=N_SHUF):
    mx = []
    for _ in range(n):
        Xs = X.copy()
        for j in range(X.shape[1]):
            rng.shuffle(Xs[:, j])
        mx.append(top_eigs(corr_guarded(Xs), 1)[0][0])
    return float(np.percentile(mx, 95))


def visibility(v, L, rng, n=200):
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


def essays_windows() -> tuple[pd.DataFrame, list[str]]:
    cols = list(a19.V3_BATTERY) + list(a19.OP5_KEPT)
    cache = OUT_DIR / "cache_essays_windows_scored19.parquet"
    if cache.exists():
        return pd.read_parquet(cache), cols
    df = pd.read_csv(ESSAYS, usecols=["user_id", "text"])  # LABELS NEVER LOADED
    df = df.dropna(subset=["text"])
    rows = []
    for eid, (uid, text) in enumerate(zip(df["user_id"], df["text"].astype(str))):
        tokens = tokenize(text)
        m = len(tokens) // WIN
        if m < 2:
            continue
        keep = (np.unique(np.round(np.linspace(0, m - 1, MAX_WINDOWS)).astype(int))
                if m > MAX_WINDOWS else np.arange(m))
        wrows, ok = [], True
        for j in keep:
            wtext = " ".join(tokens[j * WIN:(j + 1) * WIN])
            if PERSONALITY_LEAK_RE.search(wtext):
                ok = False
                break
            wrows.append({"eid": eid, "user_id": str(uid), "j": int(j), "m": int(m),
                          "t": float(j / (m - 1)), "slice_text": wtext})
        if ok:
            rows.extend(wrows)
    frame = pd.DataFrame(rows)
    scored = a19.score_slices_v2(frame[["user_id", "slice_text"]].assign(
        condition="_", half="_")[["user_id", "condition", "half", "slice_text"]])
    import scripts.run_suica_dev_anchor_performance_v1 as dav
    _, wcl_transform = dav.pandora_style_fit_and_battery()
    wcl = wcl_transform(frame["slice_text"]).reset_index(drop=True)
    src = pd.concat([frame[["eid", "user_id", "j", "m", "t"]].reset_index(drop=True),
                     scored[a19.V3_BATTERY].reset_index(drop=True),
                     wcl[a19.OP5_KEPT]], axis=1)
    src["tau"] = src["j"]
    src["delta"] = src["m"] - 1 - src["j"]
    src.to_parquet(cache)
    return src, cols


def triples(src: pd.DataFrame, cols: list[str], id_col: str):
    """(first, mid, last) window score arrays for texts with m>=3."""
    sub = src[src["m"] >= 3].sort_values([id_col, "j"])
    firsts, mids, lasts, ids, users = [], [], [], [], []
    for tid, g in sub.groupby(id_col, sort=True):
        if len(g) < 3:
            continue
        X = g[cols].to_numpy(float)
        jm = g["j"].to_numpy()
        mid_j = (g["m"].iloc[0] - 1) // 2
        mi = int(np.argmin(np.abs(jm - mid_j)))
        if mi == 0 or mi == len(g) - 1:
            mi = len(g) // 2
        firsts.append(X[0]); mids.append(X[mi]); lasts.append(X[-1])
        ids.append(tid); users.append(g["user_id"].iloc[0])
    return (np.array(firsts), np.array(mids), np.array(lasts),
            np.array(ids), np.array(users))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    src, cols = essays_windows()
    p = len(cols)
    n_essays = src["eid"].nunique()
    m_med = float(src.groupby("eid")["m"].first().median())
    print(f"essays: {n_essays} with m>=2, windows {len(src)}, median m={m_med:.0f}")
    result: dict = {"n_essays": int(n_essays), "median_m": m_med, "constructs": cols}

    # ---------- A: position profiles ----------
    g = src.sort_values(["eid", "j"]).groupby("eid")
    F = g[cols].first().to_numpy(float)
    Lst = g[cols].last().to_numpy(float)
    Lmean = g[cols].mean().to_numpy(float)
    D = Lst - F
    w0, wm, wl, eids3, users3 = triples(src, cols, "eid")
    lin3 = wl - w0
    cur3 = wm - (w0 + wl) / 2.0
    a_rows = []
    for i, c in enumerate(cols):
        obs_l = float(D[:, i].mean())
        flips = rng.choice([-1.0, 1.0], size=(N_FLIP, len(D)))
        p_l = float((np.abs((flips * D[:, i]).mean(1)) >= abs(obs_l)).mean())
        obs_c = float(cur3[:, i].mean())
        # S_3 null for curvature: permute the triple within essay
        W3 = np.stack([w0[:, i], wm[:, i], wl[:, i]], axis=1)
        null_c = []
        for _ in range(500):
            idx = np.argsort(rng.random(W3.shape), axis=1)
            Wp = np.take_along_axis(W3, idx, axis=1)
            null_c.append(abs((Wp[:, 1] - (Wp[:, 0] + Wp[:, 2]) / 2).mean()))
        p_c = float((np.array(null_c) >= abs(obs_c)).mean())
        a_rows.append({"construct": c, "linear_last_minus_first": round(obs_l, 4),
                       "p_linear": round(p_l, 4), "curvature": round(obs_c, 4),
                       "p_curvature": round(p_c, 4)})
        if c in HIGHLIGHT:
            print(f"  [A {c}] lin={obs_l:+.4f} (p={p_l:.4f}) curv={obs_c:+.4f} (p={p_c:.4f})")
    result["A_position"] = a_rows

    # ---------- B: law of the wall (m>=4, within-essay demeaned, CV by essay) ----------
    b4 = src[src["m"] >= 4].sort_values(["eid", "j"]).copy()
    zt = np.minimum(b4["tau"].to_numpy(), 2)
    zd = np.minimum(b4["delta"].to_numpy(), 2)
    t = b4["t"].to_numpy()
    X_all = np.column_stack([(zt == 1), (zt == 2), (zd == 1), (zd == 2), t, t * t]).astype(float)
    Y_all = b4[cols].to_numpy(float)
    ecodes, _ = pd.factorize(b4["eid"])
    ne = ecodes.max() + 1

    def demean(A):
        cnt = np.bincount(ecodes, minlength=ne).astype(float)
        out = A.copy()
        for j in range(A.shape[1]):
            mu = np.bincount(ecodes, weights=A[:, j], minlength=ne) / cnt
            out[:, j] = A[:, j] - mu[ecodes]
        return out

    Xd = demean(X_all)
    Yd = demean(Y_all)
    fold = np.array([zlib.crc32(f"v6cv::{e}".encode()) % 5 for e in b4["eid"]])
    MODELS = {"zones": [0, 1, 2, 3], "tpoly": [4, 5], "composite": [0, 1, 2, 3, 4, 5]}
    b_rows = []
    for i, c in enumerate(cols):
        mse = {}
        for name, ix in MODELS.items():
            err = np.empty(len(Yd))
            for f in range(5):
                tr, te = fold != f, fold == f
                beta, *_ = np.linalg.lstsq(Xd[tr][:, ix], Yd[tr, i], rcond=None)
                err[te] = Yd[te, i] - Xd[te][:, ix] @ beta
            mse[name] = float(np.mean(err ** 2))
        mse["null"] = float(np.mean(Yd[:, i] ** 2))
        best_single = min(mse["zones"], mse["tpoly"])
        gain = (best_single - mse["composite"]) / mse["null"]
        b_rows.append({"construct": c, "cv_mse": {k: round(v, 5) for k, v in mse.items()},
                       "composite_gain_vs_best_single": round(float(gain), 5)})
        if c in HIGHLIGHT:
            print(f"  [B {c}] null {mse['null']:.4f} zones {mse['zones']:.4f} "
                  f"tpoly {mse['tpoly']:.4f} comp {mse['composite']:.4f} gain {gain:+.5f}")
    result["B_law_of_wall"] = {"n_essays_m4": int(ne), "rows": b_rows}

    # ---------- C: flow/gust + cross-corpus ----------
    sd_w = src[cols].to_numpy(float).std(0)
    sd_w = np.where(sd_w > 0, sd_w, 1.0)
    lin = ((wl - w0) / 2.0) / sd_w
    cur = ((w0 - 2 * wm + wl) / np.sqrt(6.0)) / sd_w
    L3 = Lmean[np.isin(g[cols].first().index.to_numpy(), eids3)]
    half = np.array([zlib.crc32(("v6::" + u).encode()) % 2 for u in users3])
    print(f"[C] m>=3 essays: {len(lin)}")

    Cq = corr_guarded(cur)
    edge_q = shuffle_edge(cur, rng)
    lamq, Vq = top_eigs(Cq, 6)
    kq = int((lamq > edge_q).sum())
    _, Vq0 = top_eigs(corr_guarded(cur[half == 0]), max(kq, 1))
    _, Vq1 = top_eigs(corr_guarded(cur[half == 1]), max(kq, 1))
    gusts = []
    for i in range(kq):
        congr = max(abs(float(Vq0[:, i] @ Vq1[:, j2])) for j2 in range(max(kq, 1)))
        vis, vis95 = visibility(Vq[:, i], L3, rng)
        gusts.append({"rank": i + 1, "lambda": round(float(lamq[i]), 3),
                      "half_congruence": round(congr, 3),
                      "level_visibility": round(vis, 3),
                      "level_shuffle_p95": round(vis95, 3),
                      "vector": [round(float(x), 4) for x in Vq[:, i]],
                      "top_loadings": top_loadings(Vq[:, i], cols)})
        print(f"  [C gust{i+1}] lam={lamq[i]:.3f} (edge {edge_q:.3f}) congr={congr:.3f} "
              f"vis={vis:.3f} ({vis95:.3f}) {gusts[-1]['top_loadings']}")

    Sig = np.cov(lin, rowvar=False) - np.cov(cur, rowvar=False) / 2.0
    lamS, VS = top_eigs(Sig, 2)
    boot = []
    for _ in range(N_BOOT):
        b = rng.integers(0, len(lin), len(lin))
        boot.append(top_eigs(np.cov(lin[b], rowvar=False) - np.cov(cur[b], rowvar=False) / 2, 1)[0][0])
    ci = [float(np.percentile(boot, q)) for q in (2.5, 97.5)]
    S0 = np.cov(lin[half == 0], rowvar=False) - np.cov(cur[half == 0], rowvar=False) / 2
    S1 = np.cov(lin[half == 1], rowvar=False) - np.cov(cur[half == 1], rowvar=False) / 2
    repS = abs(float(top_eigs(S0, 1)[1][:, 0] @ top_eigs(S1, 1)[1][:, 0]))
    visS, visS95 = visibility(VS[:, 0], L3, rng)
    print(f"  [C flow] lam1={lamS[0]:.4f} CI={ci} rep={repS:.3f} vis={visS:.3f} ({visS95:.3f}) "
          f"{top_loadings(VS[:, 0], cols)}")

    # essay-level D factor (flow-only retry at person level)
    C_D = corr_guarded(D)
    edge_D = shuffle_edge(D, rng)
    lamD, VD = top_eigs(C_D, 6)
    kD = int((lamD > edge_D).sum())
    uh = np.array([zlib.crc32(("v6::" + str(u)).encode()) % 2
                   for u in g["user_id"].first().to_numpy()])
    _, VD0 = top_eigs(corr_guarded(D[uh == 0]), max(kD, 1))
    _, VD1 = top_eigs(corr_guarded(D[uh == 1]), max(kD, 1))
    dcomps = []
    for i in range(kD):
        congr = max(abs(float(VD0[:, i] @ VD1[:, j2])) for j2 in range(max(kD, 1)))
        vis, vis95 = visibility(VD[:, i], Lmean, rng)
        dcomps.append({"rank": i + 1, "lambda": round(float(lamD[i]), 3),
                       "half_congruence": round(congr, 3),
                       "level_visibility": round(vis, 3),
                       "level_shuffle_p95": round(vis95, 3),
                       "vector": [round(float(x), 4) for x in VD[:, i]],
                       "top_loadings": top_loadings(VD[:, i], cols)})
        print(f"  [C D-comp{i+1}] lam={lamD[i]:.3f} (edge {edge_D:.3f}) congr={congr:.3f} "
              f"vis={vis:.3f} ({vis95:.3f}) {dcomps[-1]['top_loadings']}")

    # cross-corpus congruences (recompute PANDORA vectors from the P8 cache)
    ps, pcols = scored_windows()
    assert pcols == cols
    pm3 = ps[ps["m"] == 3]
    cnt = pm3.groupby("cid").size()
    pm3 = pm3[pm3["cid"].isin(cnt.index[cnt == 3])].sort_values(["cid", "j"])
    Wp = pm3[cols].to_numpy(float).reshape(-1, 3, p)
    sd_p = pm3[cols].to_numpy(float).std(0)
    sd_p = np.where(sd_p > 0, sd_p, 1.0)
    cur_p = ((Wp[:, 0] - 2 * Wp[:, 1] + Wp[:, 2]) / np.sqrt(6.0)) / sd_p
    lin_p = ((Wp[:, 2] - Wp[:, 0]) / 2.0) / sd_p
    _, VqP = top_eigs(corr_guarded(cur_p), 1)
    SigP = np.cov(lin_p, rowvar=False) - np.cov(cur_p, rowvar=False) / 2
    _, VSP = top_eigs(SigP, 1)
    gp = ps.sort_values(["cid", "j"]).groupby("cid")
    Dp = gp[cols].last().to_numpy(float) - gp[cols].first().to_numpy(float)
    Lp = gp[cols].mean().to_numpy(float)
    _, VDP = top_eigs(corr_guarded(Dp), 4)
    _, VLE = top_eigs(corr_guarded(Lmean), 4)
    _, VLP = top_eigs(corr_guarded(Lp), 4)
    xc = {"gust1_E_x_gust1_P": round(abs(float(Vq[:, 0] @ VqP[:, 0])), 3) if kq else None,
          "flow1_E_x_flow1_P": round(abs(float(VS[:, 0] @ VSP[:, 0])), 3),
          "static_frame_per_rank": [round(max(abs(float(VLE[:, i] @ VLP[:, j2]))
                                              for j2 in range(4)), 3) for i in range(4)],
          "D_comps_E_x_P_best": [[round(abs(float(VD[:, i] @ VDP[:, j2])), 3)
                                  for j2 in range(4)] for i in range(min(kD, 4))]}
    print(f"[X] cross-corpus: {json.dumps(xc)}")

    result["C_motion"] = {"n_m3": int(len(lin)), "gust_edge": round(edge_q, 4),
                          "k_gust": kq, "gusts": gusts,
                          "flow": {"lambda1": round(float(lamS[0]), 4),
                                   "boot_ci": [round(x, 4) for x in ci],
                                   "half_replication": round(repS, 3),
                                   "level_visibility": round(visS, 3),
                                   "level_shuffle_p95": round(visS95, 3),
                                   "vector": [round(float(x), 4) for x in VS[:, 0]],
                                   "top_loadings": top_loadings(VS[:, 0], cols)},
                          "D_edge": round(edge_D, 4), "k_D": kD, "D_components": dcomps,
                          "cross_corpus": xc}
    (OUT_DIR / "V6_E2_ESSAYS_MOTION.json").write_text(json.dumps(result, indent=2))
    md = ["# V6-E2 — Essays transport of the motion layer (label-free, text-only loader)",
          "", f"{n_essays} essays m>=2 (median m {m_med:.0f}); see JSON for full tables.",
          "", f"Cross-corpus congruences: {json.dumps(xc)}"]
    (OUT_DIR / "V6_E2_ESSAYS_MOTION.md").write_text("\n".join(md) + "\n")
    print("written:", OUT_DIR / "V6_E2_ESSAYS_MOTION.md")


if __name__ == "__main__":
    main()
