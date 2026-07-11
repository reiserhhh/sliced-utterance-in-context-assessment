#!/usr/bin/env python
"""V6-E4 — person-level flow-only factor: power-raised retry (F11.4).
Label-free, Tier-U. The F10.8 phase-C candidate died at replication .150
(gate >= 3, unresidualized). Retry: gates >= 5 and >= 8 long comments, and a
SHARP arm that residualizes each user's mean-slope vector against the
user-level static top-4 frame BEFORE factoring (invisibility by construction;
the question becomes existence + person-disjoint-half replication).
Registered lean: at gate >= 5 residualized, >= 1 component clears the edge
with half-replication >= .5 (F11.4, commit 8e2b0ba).
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

from scripts.run_suica_tgeo_p8_functionalization_v1 import scored_windows  # noqa: E402

OUT_DIR = ROOT / "results" / "suica_v6_e4_person_motion_retry"
SEED = 20260712
N_SHUF = 500


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


def top_loadings(v, cols, k=4):
    idx = np.argsort(-np.abs(v))[:k]
    return [f"{cols[i]}:{v[i]:+.2f}" for i in idx]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    src, cols = scored_windows()
    g = src.sort_values(["cid", "j"]).groupby("cid")
    D = g[cols].last().to_numpy(float) - g[cols].first().to_numpy(float)
    L = g[cols].mean().to_numpy(float)
    users = g["user_id"].first().to_numpy()

    dfD = pd.DataFrame(D, columns=cols).assign(user_id=users)
    dfL = pd.DataFrame(L, columns=cols).assign(user_id=users)
    result = {"constructs": cols, "arms": []}
    for gate in [5, 8]:
        ucnt = dfD["user_id"].value_counts()
        keep = ucnt.index[ucnt >= gate]
        gD = dfD[dfD["user_id"].isin(keep)].groupby("user_id")[cols].mean()
        uD = gD.to_numpy(float)
        uL = dfL[dfL["user_id"].isin(keep)].groupby("user_id")[cols].mean().to_numpy(float)
        uhalf = np.array([zlib.crc32(("e4::" + u).encode()) % 2 for u in gD.index])
        nu = len(uD)
        # residualize uD against the user-level static top-4 frame
        sdL = uL.std(0)
        ZL = (uL - uL.mean(0)) / np.where(sdL > 0, sdL, 1.0)
        _, V4L = top_eigs(corr_guarded(uL), 4)
        sdD = uD.std(0)
        ZD = (uD - uD.mean(0)) / np.where(sdD > 0, sdD, 1.0)
        # project out level-frame directions from the slope space
        R = ZD - ZD @ V4L @ V4L.T
        for tag, X in [("raw", ZD), ("residualized", R)]:
            edge = shuffle_edge(X, rng)
            lam, V = top_eigs(corr_guarded(X), 6)
            k = int((lam > edge).sum())
            _, V0 = top_eigs(corr_guarded(X[uhalf == 0]), max(k, 1))
            _, V1 = top_eigs(corr_guarded(X[uhalf == 1]), max(k, 1))
            comps = []
            for i in range(k):
                congr = max(abs(float(V0[:, i] @ V1[:, j2])) for j2 in range(max(k, 1)))
                statc = max(abs(float(V[:, i] @ V4L[:, j2])) for j2 in range(4))
                comps.append({"rank": i + 1, "lambda": round(float(lam[i]), 3),
                              "half_congruence": round(congr, 3),
                              "static_congruence": round(statc, 3),
                              "vector": [round(float(x), 4) for x in V[:, i]],
                              "top_loadings": top_loadings(V[:, i], cols)})
                print(f"  [gate>={gate} {tag} comp{i+1}] lam={lam[i]:.3f} (edge {edge:.3f}) "
                      f"congr={congr:.3f} static={statc:.3f} {comps[-1]['top_loadings']}")
            result["arms"].append({"gate": gate, "variant": tag, "n_users": int(nu),
                                   "edge": round(edge, 4), "k_supra": k,
                                   "components": comps})
            if not k:
                print(f"  [gate>={gate} {tag}] no supra-edge components (n={nu})")
    (OUT_DIR / "V6_E4_PERSON_MOTION_RETRY.json").write_text(json.dumps(result, indent=2))
    md = ["# V6-E4 — person-level motion factor retry (label-free)", "",
          "See JSON for component tables (gates 5/8 x raw/residualized)."]
    (OUT_DIR / "V6_E4_PERSON_MOTION_RETRY.md").write_text("\n".join(md) + "\n")
    print("written:", OUT_DIR / "V6_E4_PERSON_MOTION_RETRY.md")


if __name__ == "__main__":
    main()
