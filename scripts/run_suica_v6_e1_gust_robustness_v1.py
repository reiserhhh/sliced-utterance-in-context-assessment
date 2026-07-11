#!/usr/bin/env python
"""V6-E1 — gust robustness sweep on PANDORA (F11.1). Label-free, Tier-U.

Does B-gust1 (the flow-only gust factor, F10.8) survive: (a) venue-class
restriction, (b) temporal median split, (c) user-demeaning of the contrasts,
(d) a 64-token window scale? Registered leans: F11.1 (commit 8e2b0ba).

The cid -> (subreddit, created_utc, body) map is rebuilt deterministically by
replaying the P7 build_windows candidate enumeration (same filter, same
order). Sanity: the recomputed gust1 must be led by wcl_02/wcl_11 (as in
T-GEO-P9) before any arm runs.
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

from project_persona.suica import tokenize  # noqa: E402
import scripts.run_suica_c2_purity_all19_v1 as a19  # noqa: E402
from scripts.run_suica_tgeo_p8_functionalization_v1 import scored_windows  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
CLASS_MAP = ROOT / "results" / "suica_e3_e4_choice_class_v2_s128" / "condition_class_map.csv"
OUT_DIR = ROOT / "results" / "suica_v6_e1_gust_robustness"
SEED = 20260712
MIN_CLASS_N = 60


def corr_guarded(X):
    sd = X.std(0)
    Z = np.where(sd > 0, (X - X.mean(0)) / np.where(sd > 0, sd, 1.0), 0.0)
    C = (Z.T @ Z) / max(1, len(Z) - 1)
    np.fill_diagonal(C, 1.0)
    return C


def top_eigs(C, k=3):
    w, V = np.linalg.eigh(C)
    order = np.argsort(w)[::-1]
    return w[order[:k]], V[:, order[:k]]


def best_congruence(v, X, k=3) -> float:
    """|cos| between v and the best-matching top-k eigenvector of corr(X)."""
    _, V = top_eigs(corr_guarded(X), k)
    return max(abs(float(v @ V[:, j])) for j in range(V.shape[1]))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    src, cols = scored_windows()
    p = len(cols)

    m3 = src[src["m"] == 3]
    cnt = m3.groupby("cid").size()
    m3 = m3[m3["cid"].isin(cnt.index[cnt == 3])].sort_values(["cid", "j"])
    W = m3[cols].to_numpy(float).reshape(-1, 3, p)
    cids = m3["cid"].to_numpy()[::3]
    users = m3["user_id"].to_numpy()[::3]
    sd_w = m3[cols].to_numpy(float).std(0)
    sd_w = np.where(sd_w > 0, sd_w, 1.0)
    q = ((W[:, 0] - 2 * W[:, 1] + W[:, 2]) / np.sqrt(6.0)) / sd_w
    _, Vg = top_eigs(corr_guarded(q), 1)
    g1 = Vg[:, 0]
    lead = [cols[i] for i in np.argsort(-np.abs(g1))[:2]]
    assert set(lead) & {"wcl_02", "wcl_11"}, f"gust1 drifted: leads {lead}"
    print(f"gust1 recomputed, leads {lead} (n={len(q)} m=3 comments)")

    # deterministic cid -> (subreddit, created_utc, body) map
    comments = pd.read_parquet(TIER_DIR / "tier_u_comments.parquet",
                               columns=["author", "subreddit", "body", "created_utc"])
    cand = comments[comments["body"].astype(str).str.len() >= 1200].reset_index(drop=True)
    meta = cand.iloc[cids][["subreddit", "created_utc", "body"]].reset_index(drop=True)
    cmap = pd.read_csv(CLASS_MAP).set_index("condition")["class_id"]
    classes = meta["subreddit"].map(cmap)

    result = {"n_m3": int(len(q)), "gust1_leads": lead,
              "gust1_vector": [round(float(x), 4) for x in g1]}

    # (a) venue classes
    venue_rows = []
    for cl, ix in pd.Series(np.arange(len(q))).groupby(classes.to_numpy()):
        if len(ix) < MIN_CLASS_N or pd.isna(cl):
            continue
        congr = best_congruence(g1, q[ix.to_numpy()])
        venue_rows.append({"class_id": int(cl), "n": int(len(ix)),
                           "gust1_congruence": round(congr, 3)})
        print(f"  [venue class {int(cl)}] n={len(ix)} congr={congr:.3f}")
    result["venue"] = venue_rows

    # (b) temporal median split
    tmed = meta["created_utc"].astype(float).median()
    early = q[meta["created_utc"].astype(float).to_numpy() < tmed]
    late = q[meta["created_utc"].astype(float).to_numpy() >= tmed]
    c_e, c_l = best_congruence(g1, early), best_congruence(g1, late)
    _, Ve = top_eigs(corr_guarded(early), 1)
    cross_t = abs(float(Ve[:, 0] @ top_eigs(corr_guarded(late), 1)[1][:, 0]))
    print(f"  [temporal] early {c_e:.3f} late {c_l:.3f} early-x-late {cross_t:.3f}")
    result["temporal"] = {"early_congruence": round(c_e, 3), "late_congruence": round(c_l, 3),
                          "early_x_late_top1": round(cross_t, 3)}

    # (c) user-demeaned
    uc = pd.Series(users).value_counts()
    mask = np.isin(users, uc.index[uc >= 2])
    dfq = pd.DataFrame(q[mask]).assign(u=users[mask])
    q_dm = (dfq.groupby("u")[list(range(p))].transform(lambda x: x - x.mean())
            .to_numpy(float))
    c_dm = best_congruence(g1, q_dm)
    print(f"  [user-demeaned] n={len(q_dm)} congr={c_dm:.3f}")
    result["user_demeaned"] = {"n": int(len(q_dm)), "congruence": round(c_dm, 3)}

    # (d) 64-token scale on the same comments
    rows64 = []
    for bi, body in enumerate(meta["body"].astype(str)):
        tokens = tokenize(body)
        T = len(tokens)
        if T < 384:
            continue
        mid0 = (T - 64) // 2
        for tag, seg in [("w0", tokens[:64]), ("wm", tokens[mid0:mid0 + 64]),
                         ("wl", tokens[-64:])]:
            rows64.append({"k": bi, "pos": tag, "user_id": users[bi],
                           "slice_text": " ".join(seg)})
    f64 = pd.DataFrame(rows64)
    scored = a19.score_slices_v2(f64[["user_id", "slice_text"]].assign(
        condition="_", half="_")[["user_id", "condition", "half", "slice_text"]])
    import scripts.run_suica_dev_anchor_performance_v1 as dav
    _, wcl_transform = dav.pandora_style_fit_and_battery()
    wcl = wcl_transform(f64["slice_text"]).reset_index(drop=True)
    s64 = pd.concat([f64[["k", "pos"]].reset_index(drop=True),
                     scored[a19.V3_BATTERY].reset_index(drop=True),
                     wcl[a19.OP5_KEPT]], axis=1)
    piv = {pos: s64[s64["pos"] == pos].sort_values("k")[cols].to_numpy(float)
           for pos in ["w0", "wm", "wl"]}
    sd64 = s64[cols].to_numpy(float).std(0)
    sd64 = np.where(sd64 > 0, sd64, 1.0)
    q64 = ((piv["w0"] - 2 * piv["wm"] + piv["wl"]) / np.sqrt(6.0)) / sd64
    c64 = best_congruence(g1, q64)
    lam64, V64 = top_eigs(corr_guarded(q64), 1)
    print(f"  [scale64] n={len(q64)} congr(g1 in top3)={c64:.3f} "
          f"top1-x-g1={abs(float(V64[:,0] @ g1)):.3f}")
    result["scale64"] = {"n": int(len(q64)), "gust1_congruence_top3": round(c64, 3),
                         "top1_x_gust1": round(abs(float(V64[:, 0] @ g1)), 3),
                         "lambda1": round(float(lam64[0]), 3)}

    (OUT_DIR / "V6_E1_GUST_ROBUSTNESS.json").write_text(json.dumps(result, indent=2))
    md = ["# V6-E1 — gust robustness sweep (label-free)", "",
          f"gust1 leads {lead}; venue rows {len(venue_rows)}; see JSON."]
    (OUT_DIR / "V6_E1_GUST_ROBUSTNESS.md").write_text("\n".join(md) + "\n")
    print("written:", OUT_DIR / "V6_E1_GUST_ROBUSTNESS.md")


if __name__ == "__main__":
    main()
