#!/usr/bin/env python
"""V6-E3 — gust dynamics (F11.3). Label-free.

Within-text detrended residuals projected on a gust axis give a per-window
gust series gamma_k. Tests (registered leans, commit 8e2b0ba):
  (a) AR(1) of gamma_k vs within-essay order-permutation null — lean ~ 0
      (white gusts); positive AR would upgrade gusts to "weather" (OU-like).
  (b) |gamma_k| by position (5 t-bins): boundary vs interior contrast — lean
      boundary-elevated.
Axes: gust1_E (Essays, from V6-E2 JSON) and gust1_P (PANDORA m=3, recomputed
deterministically from the P8 cache). Corpora: Essays m>=4 (primary),
PANDORA m>=4 (descriptive, thin). Adjacency = consecutive KEPT windows
(subsampled long texts have j gaps; stated).
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

from scripts.run_suica_tgeo_p8_functionalization_v1 import scored_windows  # noqa: E402
from scripts.run_suica_v6_e2_essays_motion_v1 import essays_windows  # noqa: E402

OUT_DIR = ROOT / "results" / "suica_v6_e3_gust_dynamics"
E2_JSON = ROOT / "results" / "suica_v6_e2_essays_motion" / "V6_E2_ESSAYS_MOTION.json"
SEED = 20260712
N_PERM = 500
N_BINS = 5
BIN_EDGES = np.array([0.125, 0.375, 0.625, 0.875])


def detrended_gamma(src: pd.DataFrame, cols: list[str], id_col: str,
                    axis: np.ndarray) -> pd.DataFrame:
    sub = src[src["m"] >= 4].sort_values([id_col, "j"])
    resid_rows = []
    for tid, g in sub.groupby(id_col, sort=True):
        X = g[cols].to_numpy(float)
        k = g["j"].to_numpy(float)
        A = np.column_stack([np.ones(len(k)), k])
        beta, *_ = np.linalg.lstsq(A, X, rcond=None)
        R = X - A @ beta
        for r, (jj, tt) in zip(R, zip(g["j"], g["t"])):
            resid_rows.append({"tid": tid, "j": int(jj), "t": float(tt), "resid": r})
    df = pd.DataFrame(resid_rows)
    RM = np.stack(df["resid"].to_numpy())
    sd = RM.std(0)
    RM = RM / np.where(sd > 0, sd, 1.0)
    df["gamma"] = RM @ (axis / np.linalg.norm(axis))
    return df[["tid", "j", "t", "gamma"]]


def ar_and_position(df: pd.DataFrame, rng) -> dict:
    df = df.sort_values(["tid", "j"]).reset_index(drop=True)
    tids, codes = pd.factorize(df["tid"])
    gam = df["gamma"].to_numpy()
    bins = np.digitize(df["t"].to_numpy(), BIN_EDGES)
    same = tids[1:] == tids[:-1]

    def stats(order: np.ndarray) -> tuple[float, float]:
        gg = gam[order]
        a = np.corrcoef(gg[:-1][same], gg[1:][same])[0, 1]
        ab = np.abs(gg)
        edge = ab[(bins == 0) | (bins == N_BINS - 1)].mean()
        interior = ab[(bins > 0) & (bins < N_BINS - 1)].mean()
        return float(a), float(edge - interior)

    ident = np.arange(len(df))
    ar_obs, pos_obs = stats(ident)
    null_ar, null_pos = [], []
    for _ in range(N_PERM):
        keys = rng.random(len(df))
        perm = np.lexsort((keys, tids))
        order = np.empty(len(df), dtype=int)
        order[perm] = ident  # deal canonical rows to random within-text slots
        null_ar.append(stats(order)[0])
        null_pos.append(stats(order)[1])
    return {"n_texts": int(df["tid"].nunique()), "n_windows": int(len(df)),
            "ar1": round(ar_obs, 4),
            "ar1_null_2p5_97p5": [round(float(np.percentile(null_ar, q)), 4)
                                  for q in (2.5, 97.5)],
            "p_ar1_two_sided": round(float((np.abs(null_ar) >= abs(ar_obs)).mean()), 4),
            "edge_minus_interior_absgamma": round(pos_obs, 4),
            "p_position": round(float((np.array(null_pos) >= pos_obs).mean()), 4)}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    es, cols = essays_windows()
    e2 = json.loads(E2_JSON.read_text())
    gust_e = np.array(e2["C_motion"]["gusts"][0]["vector"], float)

    ps, pcols = scored_windows()
    assert pcols == cols
    pm3 = ps[ps["m"] == 3]
    cnt = pm3.groupby("cid").size()
    pm3 = pm3[pm3["cid"].isin(cnt.index[cnt == 3])].sort_values(["cid", "j"])
    Wp = pm3[cols].to_numpy(float).reshape(-1, 3, len(cols))
    sd_p = pm3[cols].to_numpy(float).std(0)
    sd_p = np.where(sd_p > 0, sd_p, 1.0)
    cur_p = ((Wp[:, 0] - 2 * Wp[:, 1] + Wp[:, 2]) / np.sqrt(6.0)) / sd_p
    Cp = np.corrcoef(cur_p, rowvar=False)
    np.fill_diagonal(Cp, 1.0)
    w, V = np.linalg.eigh(Cp)
    gust_p = V[:, int(np.argmax(w))]

    result = {}
    for corpus, src, id_col in [("essays", es, "eid"), ("pandora", ps, "cid")]:
        for axis_name, axis in [("gust1_E", gust_e), ("gust1_P", gust_p)]:
            df = detrended_gamma(src, cols, id_col, axis)
            r = ar_and_position(df, rng)
            result[f"{corpus}::{axis_name}"] = r
            print(f"  [{corpus} {axis_name}] n_texts={r['n_texts']} AR1={r['ar1']:+.4f} "
                  f"(null {r['ar1_null_2p5_97p5']}, p={r['p_ar1_two_sided']}) "
                  f"edge-int={r['edge_minus_interior_absgamma']:+.4f} (p={r['p_position']})")

    (OUT_DIR / "V6_E3_GUST_DYNAMICS.json").write_text(json.dumps(result, indent=2))
    md = ["# V6-E3 — gust dynamics (label-free)", "",
          "| corpus::axis | texts | AR(1) (p) | edge-interior |gamma| (p) |", "|---|---|---|---|"]
    for k, r in result.items():
        md.append(f"| {k} | {r['n_texts']} | {r['ar1']:+.4f} ({r['p_ar1_two_sided']}) "
                  f"| {r['edge_minus_interior_absgamma']:+.4f} ({r['p_position']}) |")
    (OUT_DIR / "V6_E3_GUST_DYNAMICS.md").write_text("\n".join(md) + "\n")
    print("written:", OUT_DIR / "V6_E3_GUST_DYNAMICS.md")


if __name__ == "__main__":
    main()
