#!/usr/bin/env python
"""T-GEO-P4 — time flow of the POPULATION factor frame (F10.1 with t = time).
Label-free, Tier-U. Reuses the T-GEO-P2 block design verbatim (K=4 equal-count
blocks per user, span >= 180 days; arms pooled / top1).

Per block b: between-person correlation of the 19-construct battery over
user-block means -> top-4 eigenframe V(b) on Gr(4, 19).

Statistics (registered in F10.4):
  D14  = chordal distance d(V(1), V(4))
  PATH = sum_b d(V(b), V(b+1))
Null (F7 group): within-user permutations of block labels (500 draws) —
under factor fixity the 4 block values of a user are exchangeable.
Registered prediction: NO detectable flow beyond the null at block scale
(the F9/P3 constraint); pooled-only flow would indicate venue-mix flow.
Caveat F10.5a: block slice counts vary within user, so block-mean noise is
heteroscedastic and the exchangeability null is approximate.
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
from scripts.run_suica_tgeo_p2_time_reversal_v1 import (  # noqa: E402
    K, MIN_SPAN_DAYS, block_rows)

OUT_DIR = ROOT / "results" / "suica_tgeo_p4_factor_time_flow"
SEED = 20260711
N_PERM = 500
TOPK = 4


def corr_frame(X: np.ndarray, k: int = TOPK) -> tuple[np.ndarray, np.ndarray]:
    sd = X.std(0)
    Z = np.where(sd > 0, (X - X.mean(0)) / np.where(sd > 0, sd, 1.0), 0.0)
    C = (Z.T @ Z) / max(1, len(Z) - 1)
    np.fill_diagonal(C, 1.0)
    w, V = np.linalg.eigh(C)
    order = np.argsort(w)[::-1]
    return V[:, order[:k]], np.sort(w)[::-1][:k]


def chordal(V: np.ndarray, W: np.ndarray) -> float:
    return float(np.sqrt(max(0.0, V.shape[1] - np.linalg.norm(V.T @ W) ** 2)))


def flow_stats(A: np.ndarray) -> tuple[float, float, list]:
    frames = [corr_frame(A[:, b, :]) for b in range(K)]
    d14 = chordal(frames[0][0], frames[K - 1][0])
    path = float(sum(chordal(frames[b][0], frames[b + 1][0]) for b in range(K - 1)))
    lams = [[round(float(x), 3) for x in fr[1]] for fr in frames]
    return d14, path, lams


def analyze(arm: str, cols: list[str], wcl_transform) -> dict:
    frame = block_rows(arm)
    print(f"[{arm}] block slices: {len(frame)}")
    scored = a19.score_slices_v2(frame[["user_id", "slice_text"]].assign(
        condition="_", half="_")[["user_id", "condition", "half", "slice_text"]])
    wcl = wcl_transform(frame["slice_text"]).reset_index(drop=True)
    src = pd.concat([frame[["user_id", "block", "tmid"]].reset_index(drop=True),
                     scored[a19.V3_BATTERY].reset_index(drop=True),
                     wcl[a19.OP5_KEPT]], axis=1)

    counts = src.groupby(["user_id", "block"]).size().unstack(fill_value=0)
    ok = counts.index[(counts >= 2).all(axis=1) & (counts.shape[1] == K)]
    bm = src.groupby(["user_id", "block"]).agg(
        {**{c: "mean" for c in cols}, "tmid": "mean"})
    bm = bm.loc[bm.index.get_level_values(0).isin(ok)]
    spans = bm["tmid"].groupby(level=0).agg(lambda t: (t.max() - t.min()) / 86400.0)
    users = spans.index[spans >= MIN_SPAN_DAYS]
    bm = bm.loc[bm.index.get_level_values(0).isin(users)]
    n = len(users)
    A = bm[cols].to_numpy(float).reshape(n, K, len(cols))
    print(f"[{arm}] cohort users: {n}")

    obs_d14, obs_path, lams = flow_stats(A)
    rng = np.random.default_rng(SEED)
    null_d14, null_path = [], []
    ar = np.arange(n)[:, None]
    for _ in range(N_PERM):
        idx = np.argsort(rng.random((n, K)), axis=1)
        d14, path, _ = flow_stats(A[ar, idx, :])
        null_d14.append(d14)
        null_path.append(path)
    p_d14 = float((np.array(null_d14) >= obs_d14).mean())
    p_path = float((np.array(null_path) >= obs_path).mean())
    print(f"[{arm}] D14={obs_d14:.4f} (null mean {np.mean(null_d14):.4f}, p={p_d14:.4f}) "
          f"PATH={obs_path:.4f} (null mean {np.mean(null_path):.4f}, p={p_path:.4f})")
    return {"arm": arm, "n_users": int(n),
            "d14_top4_chordal": round(obs_d14, 4),
            "d14_null_mean": round(float(np.mean(null_d14)), 4),
            "d14_null_p95": round(float(np.percentile(null_d14, 95)), 4),
            "p_d14": round(p_d14, 4),
            "path_length": round(obs_path, 4),
            "path_null_mean": round(float(np.mean(null_path)), 4),
            "path_null_p95": round(float(np.percentile(null_path, 95)), 4),
            "p_path": round(p_path, 4),
            "lambda_top4_per_block": lams}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cols = list(a19.V3_BATTERY) + list(a19.OP5_KEPT)
    import scripts.run_suica_dev_anchor_performance_v1 as dav
    _, wcl_transform = dav.pandora_style_fit_and_battery()
    res = [analyze("pooled", cols, wcl_transform), analyze("top1", cols, wcl_transform)]
    (OUT_DIR / "TGEO_P4_FACTOR_TIME_FLOW.json").write_text(json.dumps(res, indent=2))
    md = ["# T-GEO-P4 — time flow of the population factor frame (label-free)", "",
          "Top-4 eigenframe per time block (K=4, span >= 180d); chordal distance",
          "block1 vs block4 (D14) and adjacent path length; null = within-user",
          "block-label permutations (500). Heteroscedasticity caveat F10.5a applies.", "",
          "| arm | n users | D14 | null mean (p95) | p | PATH | null mean (p95) | p |",
          "|---|---|---|---|---|---|---|---|"]
    for r in res:
        md.append(f"| {r['arm']} | {r['n_users']} | {r['d14_top4_chordal']} "
                  f"| {r['d14_null_mean']} ({r['d14_null_p95']}) | {r['p_d14']} "
                  f"| {r['path_length']} | {r['path_null_mean']} ({r['path_null_p95']}) "
                  f"| {r['p_path']} |")
        md.append(f"|  |  | lambda/block: {r['lambda_top4_per_block']} |  |  |  |  |  |")
    (OUT_DIR / "TGEO_P4_FACTOR_TIME_FLOW.md").write_text("\n".join(md) + "\n")
    print("written:", OUT_DIR / "TGEO_P4_FACTOR_TIME_FLOW.md")


if __name__ == "__main__":
    main()
