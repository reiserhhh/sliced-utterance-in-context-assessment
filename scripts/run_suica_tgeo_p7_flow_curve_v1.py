#!/usr/bin/env python
"""T-GEO-P7 — flow curve: position as a CONTINUOUS variable (F10.6). Label-free, Tier-U.

Continuizes T-GEO-P5. Non-overlapping 128-token windows inside long comments
(>= 288 tokens); window j of m carries t = j/(m-1) in [0,1]; five bins over t.
Comments with > 12 windows are subsampled to 12 with endpoints preserved
(t keeps the ORIGINAL index). A comment is dropped whole if any kept window
trips the leak mask (position-neutral exclusion).

Question (registered in F10.6 before the run): is the position movement of
P5 edge-localized (openings/closings as discrete micro-registers, interior
homogeneous) or a true flow (movement accumulates along t)?

Null: within-comment permutation of window order (group S_m per comment).
This preserves each comment's SET of t values, hence bin composition —
every p-value is composition-matched by construction.

Statistics: adjacent frame distances d(b,b+1); per-construct adjacent mean
steps; EDGE SHARE = (first+last step)/(all steps), ~ .5 under uniform flow,
-> 1 under edge localization; interior flatness = max interior step vs null.
Sanity anchor: bin4 - bin0 must reproduce P5's open/close direction for
first_person (hard assert before anything is written).
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

from project_persona.suica import PERSONALITY_LEAK_RE, tokenize  # noqa: E402
import scripts.run_suica_c2_purity_all19_v1 as a19  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
OUT_DIR = ROOT / "results" / "suica_tgeo_p7_flow_curve"
SEED = 20260711
MIN_TOKENS = 288
WIN = 128
MAX_WINDOWS = 12
N_BINS = 5
BIN_EDGES = np.array([0.125, 0.375, 0.625, 0.875])
N_NULL = 300
TOPK = 4
HIGHLIGHT = ["first_person_usage_v2", "tension_core_v2", "directive_action_v2",
             "novelty_play_v2", "wcl_36", "wcl_54", "wcl_22", "wcl_15",
             "wcl_25", "wcl_02"]


def build_windows() -> pd.DataFrame:
    comments = pd.read_parquet(TIER_DIR / "tier_u_comments.parquet",
                               columns=["author", "body"])
    comments["author"] = comments["author"].astype(str)
    body = comments["body"].astype(str)
    cand = comments.loc[body.str.len() >= 1200]
    rows = []
    for cid, (author, text) in enumerate(zip(cand["author"], cand["body"].astype(str))):
        tokens = tokenize(text)
        if len(tokens) < MIN_TOKENS:
            continue
        m = len(tokens) // WIN
        if m < 2:
            continue
        keep = (np.unique(np.round(np.linspace(0, m - 1, MAX_WINDOWS)).astype(int))
                if m > MAX_WINDOWS else np.arange(m))
        wrows = []
        ok = True
        for j in keep:
            wtext = " ".join(tokens[j * WIN:(j + 1) * WIN])
            if PERSONALITY_LEAK_RE.search(wtext):
                ok = False
                break
            wrows.append({"cid": cid, "user_id": author, "j": int(j), "m": int(m),
                          "t": float(j / (m - 1)), "slice_text": wtext})
        if ok:
            rows.extend(wrows)
    return pd.DataFrame(rows)


def corr_frame(X: np.ndarray, k: int = TOPK) -> np.ndarray:
    sd = X.std(0)
    Z = np.where(sd > 0, (X - X.mean(0)) / np.where(sd > 0, sd, 1.0), 0.0)
    C = (Z.T @ Z) / max(1, len(Z) - 1)
    np.fill_diagonal(C, 1.0)
    w, V = np.linalg.eigh(C)
    return V[:, np.argsort(w)[::-1][:k]]


def chordal(V: np.ndarray, W: np.ndarray) -> float:
    return float(np.sqrt(max(0.0, V.shape[1] - np.linalg.norm(V.T @ W) ** 2)))


def stats_for(bins: np.ndarray, u: np.ndarray, W: np.ndarray, nu: int,
              n_cols: int) -> dict:
    """User x bin means -> frame steps + mean curves for one bin assignment."""
    key = u * N_BINS + bins
    counts = np.bincount(key, minlength=N_BINS * nu).astype(float)
    M = np.empty((N_BINS * nu, n_cols))
    for c in range(n_cols):
        M[:, c] = np.bincount(key, weights=W[:, c], minlength=N_BINS * nu)
    M = (M / np.maximum(counts, 1)[:, None]).reshape(nu, N_BINS, n_cols)
    present = counts.reshape(nu, N_BINS) > 0

    frames = {}
    d_adj = []
    for b in range(N_BINS - 1):
        sel = present[:, b] & present[:, b + 1]
        Va = corr_frame(M[sel, b, :])
        Vb = corr_frame(M[sel, b + 1, :])
        frames[(b, b + 1)] = (Va, Vb, int(sel.sum()))
        d_adj.append(chordal(Va, Vb))
    mu = np.array([M[present[:, b], b, :].mean(axis=0) for b in range(N_BINS)])
    steps = np.abs(np.diff(mu, axis=0))            # (4, n_cols)
    tot = steps.sum(axis=0)
    edge_share = np.where(tot > 0, (steps[0] + steps[-1]) / np.maximum(tot, 1e-12), 0.5)
    d_adj = np.array(d_adj)
    return {"d_adj": d_adj,
            "frame_edge_share": float((d_adj[0] + d_adj[-1]) / max(d_adj.sum(), 1e-12)),
            "frame_interior_max": float(d_adj[1:-1].max()),
            "mu": mu, "steps": steps, "edge_share": edge_share,
            "interior_max": steps[1:-1].max(axis=0), "present": present,
            "M": M, "frames": frames}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = build_windows()
    cols = list(a19.V3_BATTERY) + list(a19.OP5_KEPT)
    print(f"windows: {len(frame)} from {frame['cid'].nunique()} comments, "
          f"{frame['user_id'].nunique()} users")

    scored = a19.score_slices_v2(frame[["user_id", "slice_text"]].assign(
        condition="_", half="_")[["user_id", "condition", "half", "slice_text"]])
    import scripts.run_suica_dev_anchor_performance_v1 as dav
    _, wcl_transform = dav.pandora_style_fit_and_battery()
    wcl = wcl_transform(frame["slice_text"]).reset_index(drop=True)
    src = pd.concat([frame[["cid", "user_id", "j", "m", "t"]].reset_index(drop=True),
                     scored[a19.V3_BATTERY].reset_index(drop=True),
                     wcl[a19.OP5_KEPT]], axis=1)

    # canonical order (cid, j) so grouped shuffles can be vectorized
    src = src.sort_values(["cid", "j"]).reset_index(drop=True)
    bins0 = np.digitize(src["t"].to_numpy(), BIN_EDGES)
    ucodes, _ = pd.factorize(src["user_id"])
    cid_arr = src["cid"].to_numpy()
    W = src[cols].to_numpy(float)
    nu = int(ucodes.max()) + 1
    n_cols = len(cols)

    obs = stats_for(bins0, ucodes, W, nu, n_cols)
    fp = cols.index("first_person_usage_v2")
    endpoint_fp = float(obs["mu"][4, fp] - obs["mu"][0, fp])
    assert endpoint_fp < 0, f"sanity anchor failed: first_person bin4-bin0 = {endpoint_fp}"
    print(f"sanity anchor ok: first_person bin4-bin0 = {endpoint_fp:+.4f} (P5 direction)")

    # per-bin composition + per-PC congruence vs bin 0 (observed, matched users)
    comp = []
    for b in range(N_BINS):
        inb = bins0 == b
        med_m = float(src.loc[inb, "m"].median())
        comp.append({"bin": b, "windows": int(inb.sum()),
                     "users": int(obs["present"][:, b].sum()), "median_m": med_m})
        print(f"  bin{b}: windows={comp[-1]['windows']} users={comp[-1]['users']} "
              f"median_m={med_m:.0f}")
    congr_curve = []
    for b in range(1, N_BINS):
        sel = obs["present"][:, 0] & obs["present"][:, b]
        V0 = corr_frame(obs["M"][sel, 0, :])
        Vb = corr_frame(obs["M"][sel, b, :])
        congr_curve.append([round(max(abs(float(V0[:, i] @ Vb[:, jj]))
                                      for jj in range(TOPK)), 3) for i in range(TOPK)])

    rng = np.random.default_rng(SEED)
    null = {"d_adj": [], "frame_edge_share": [], "frame_interior_max": [],
            "steps": [], "edge_share": [], "interior_max": []}
    for _ in range(N_NULL):
        keys = rng.random(len(src))
        perm = np.lexsort((keys, cid_arr))
        b_null = np.empty(len(src), dtype=int)
        b_null[perm] = bins0  # deal the canonical (cid,j)-ordered bins to random order
        s = stats_for(b_null, ucodes, W, nu, n_cols)
        for k in null:
            null[k].append(s[k])
    null = {k: np.array(v) for k, v in null.items()}

    p_d_adj = [(round(float(obs["d_adj"][i]), 4),
                round(float((null["d_adj"][:, i] >= obs["d_adj"][i]).mean()), 4))
               for i in range(N_BINS - 1)]
    p_fes = float((null["frame_edge_share"] >= obs["frame_edge_share"]).mean())
    p_fim = float((null["frame_interior_max"] >= obs["frame_interior_max"]).mean())
    print(f"[frame] d_adj (obs,p) = {p_d_adj}")
    print(f"[frame] edge_share = {obs['frame_edge_share']:.3f} (p={p_fes:.4f}) "
          f"interior_max = {obs['frame_interior_max']:.4f} (p={p_fim:.4f})")
    print(f"[frame] per-PC congruence vs bin0: {congr_curve}")

    constructs = []
    for c in cols:
        i = cols.index(c)
        row = {"construct": c,
               "mu_curve": [round(float(x), 4) for x in obs["mu"][:, i]],
               "endpoint_diff": round(float(obs["mu"][4, i] - obs["mu"][0, i]), 4),
               "edge_share": round(float(obs["edge_share"][i]), 3),
               "p_edge_share": round(float((null["edge_share"][:, i] >=
                                            obs["edge_share"][i]).mean()), 4),
               "interior_max_step": round(float(obs["interior_max"][i]), 4),
               "p_interior": round(float((null["interior_max"][:, i] >=
                                          obs["interior_max"][i]).mean()), 4),
               "steps": [round(float(x), 4) for x in obs["steps"][:, i]]}
        constructs.append(row)
        if c in HIGHLIGHT:
            print(f"  [{c}] mu={row['mu_curve']} edge_share={row['edge_share']} "
                  f"(p={row['p_edge_share']}) interior_max={row['interior_max_step']} "
                  f"(p={row['p_interior']})")

    result = {"composition": comp, "sanity_first_person_endpoint": round(endpoint_fp, 4),
              "frame": {"d_adj_obs_p": p_d_adj,
                        "edge_share": round(obs["frame_edge_share"], 4), "p_edge_share": round(p_fes, 4),
                        "interior_max": round(obs["frame_interior_max"], 4), "p_interior": round(p_fim, 4),
                        "per_pc_congruence_vs_bin0": congr_curve,
                        "matched_users_per_pair": [obs["frames"][(b, b + 1)][2]
                                                   for b in range(N_BINS - 1)]},
              "constructs": constructs, "n_null": N_NULL}
    (OUT_DIR / "TGEO_P7_FLOW_CURVE.json").write_text(json.dumps(result, indent=2))

    md = ["# T-GEO-P7 — flow curve: position as a continuous variable (label-free)", "",
          f"Windows: {len(frame)} from {frame['cid'].nunique()} comments >= {MIN_TOKENS} "
          f"tokens ({frame['user_id'].nunique()} users); t = j/(m-1), {N_BINS} bins; "
          f"null = within-comment order permutation ({N_NULL} draws, composition-matched).", "",
          "| bin | windows | users | median m |", "|---|---|---|---|"]
    md += [f"| {c['bin']} | {c['windows']} | {c['users']} | {c['median_m']:.0f} |" for c in comp]
    md += ["", "## Frame (top-4) along t",
           f"Adjacent chordal (obs, p): {p_d_adj}; edge share {obs['frame_edge_share']:.3f} "
           f"(p = {p_fes:.4f}); interior max {obs['frame_interior_max']:.4f} (p = {p_fim:.4f}).",
           f"Per-PC best congruence vs bin 0, b=1..4: {congr_curve}", "",
           "## Mean curves (highlight constructs)", "",
           "| construct | mu(bin0..bin4) | edge share (p) | interior max (p) |",
           "|---|---|---|---|"]
    for row in constructs:
        if row["construct"] in HIGHLIGHT:
            md.append(f"| {row['construct']} | {row['mu_curve']} | {row['edge_share']} "
                      f"({row['p_edge_share']}) | {row['interior_max_step']} "
                      f"({row['p_interior']}) |")
    (OUT_DIR / "TGEO_P7_FLOW_CURVE.md").write_text("\n".join(md) + "\n")
    print("written:", OUT_DIR / "TGEO_P7_FLOW_CURVE.md")


if __name__ == "__main__":
    main()
