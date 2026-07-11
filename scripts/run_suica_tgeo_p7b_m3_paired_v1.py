#!/usr/bin/env python
"""T-GEO-P7b — composition-free paired position test on the m=3 stratum.
Label-free, Tier-U. Companion to T-GEO-P7 (F10.6).

P7's five-bin curve mixes comment-length composition into the bin VALUES
(interior bins are fed only by long comments). This stratum test removes
composition entirely: comments with exactly m = 3 windows contribute their
OWN open / mid / close windows (t = 0, .5, 1), so every position is
estimated from the same comments. Group per F7: S_3 within comment.

Statistics (user-level primary, gate >= 2 such comments):
  linear   = close - open          (P5 replication inside the stratum)
  curvature = mid - (open+close)/2 (is the interior on the segment between
                                    the endpoints, or off it?)
Null: within-comment permutation of the three windows (2000 draws),
recomputed at the user level. Same registered question as F10.6: the
boundary-register reading predicts significant curvature (interior off the
endpoint segment); a pure gradual flow predicts curvature ~ 0.
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
from scripts.run_suica_tgeo_p7_flow_curve_v1 import build_windows  # noqa: E402

OUT_DIR = ROOT / "results" / "suica_tgeo_p7_flow_curve"
SEED = 20260711
N_FLIP = 2000
GATE_USER = 2
HIGHLIGHT = ["first_person_usage_v2", "tension_core_v2", "directive_action_v2",
             "novelty_play_v2", "wcl_36", "wcl_54", "wcl_22", "wcl_15",
             "wcl_25", "wcl_02"]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = build_windows()
    frame = frame[frame["m"] == 3].reset_index(drop=True)
    n_comments = frame["cid"].nunique()
    print(f"m=3 stratum: {n_comments} comments, {frame['user_id'].nunique()} users, "
          f"{len(frame)} windows")

    cols = list(a19.V3_BATTERY) + list(a19.OP5_KEPT)
    scored = a19.score_slices_v2(frame[["user_id", "slice_text"]].assign(
        condition="_", half="_")[["user_id", "condition", "half", "slice_text"]])
    import scripts.run_suica_dev_anchor_performance_v1 as dav
    _, wcl_transform = dav.pandora_style_fit_and_battery()
    wcl = wcl_transform(frame["slice_text"]).reset_index(drop=True)
    src = pd.concat([frame[["cid", "user_id", "j"]].reset_index(drop=True),
                     scored[a19.V3_BATTERY].reset_index(drop=True),
                     wcl[a19.OP5_KEPT]], axis=1).sort_values(["cid", "j"])

    # per-comment (open, mid, close) score triples
    counts = src.groupby("cid").size()
    full = counts.index[counts == 3]
    src = src[src["cid"].isin(full)]
    X = src[cols].to_numpy(float).reshape(-1, 3, len(cols))   # (n_comments, 3, 19)
    authors = src.groupby("cid", sort=True)["user_id"].first()
    ucodes, uniq = pd.factorize(authors)
    keep_users = pd.Series(ucodes).value_counts()
    keep_users = set(keep_users.index[keep_users >= GATE_USER])
    mask = np.array([c in keep_users for c in ucodes])
    X, ucodes = X[mask], ucodes[mask]
    codes, _ = pd.factorize(ucodes)
    nu = int(codes.max()) + 1
    print(f"after user gate >= {GATE_USER}: {len(X)} comments, {nu} users")

    def user_stat(vals: np.ndarray) -> np.ndarray:
        """comment-level values -> user means -> across-user mean (per construct)."""
        out = np.empty((nu, vals.shape[1]))
        cnt = np.bincount(codes, minlength=nu).astype(float)
        for c in range(vals.shape[1]):
            out[:, c] = np.bincount(codes, weights=vals[:, c], minlength=nu) / cnt
        return out.mean(axis=0)

    lin_obs = user_stat(X[:, 2, :] - X[:, 0, :])
    cur_obs = user_stat(X[:, 1, :] - (X[:, 0, :] + X[:, 2, :]) / 2.0)
    mu = [user_stat(X[:, p, :]) for p in range(3)]

    rng = np.random.default_rng(SEED)
    lin_null = np.empty((N_FLIP, len(cols)))
    cur_null = np.empty((N_FLIP, len(cols)))
    n_c = len(X)
    for d in range(N_FLIP):
        perm = np.argsort(rng.random((n_c, 3)), axis=1)
        Xp = X[np.arange(n_c)[:, None], perm, :]
        lin_null[d] = user_stat(Xp[:, 2, :] - Xp[:, 0, :])
        cur_null[d] = user_stat(Xp[:, 1, :] - (Xp[:, 0, :] + Xp[:, 2, :]) / 2.0)

    rows = []
    for i, c in enumerate(cols):
        p_lin = float((np.abs(lin_null[:, i]) >= abs(lin_obs[i])).mean())
        p_cur = float((np.abs(cur_null[:, i]) >= abs(cur_obs[i])).mean())
        rows.append({"construct": c,
                     "mu_open_mid_close": [round(float(mu[p][i]), 4) for p in range(3)],
                     "linear_close_minus_open": round(float(lin_obs[i]), 4),
                     "p_linear": round(p_lin, 4),
                     "curvature_mid_minus_endpoints": round(float(cur_obs[i]), 4),
                     "p_curvature": round(p_cur, 4)})
        if c in HIGHLIGHT:
            print(f"  [{c}] open/mid/close={rows[-1]['mu_open_mid_close']} "
                  f"lin={lin_obs[i]:+.4f} (p={p_lin:.4f}) "
                  f"curv={cur_obs[i]:+.4f} (p={p_cur:.4f})")

    result = {"n_comments": int(len(X)), "n_users": int(nu),
              "note": ("composition-free: every position estimated from the same "
                       "comments; user-level statistic; S_3 within-comment null"),
              "constructs": rows}
    (OUT_DIR / "TGEO_P7B_M3_PAIRED.json").write_text(json.dumps(result, indent=2))
    md = ["# T-GEO-P7b — m=3 paired stratum (composition-free position test)", "",
          f"{len(X)} comments with exactly 3 windows, {nu} users (gate >= {GATE_USER} "
          f"comments); S_3 within-comment null ({N_FLIP} draws), user-level.", "",
          "| construct | open / mid / close | linear (p) | curvature (p) |",
          "|---|---|---|---|"]
    for r in rows:
        if r["construct"] in HIGHLIGHT:
            md.append(f"| {r['construct']} | {r['mu_open_mid_close']} "
                      f"| {r['linear_close_minus_open']:+.4f} ({r['p_linear']:.4f}) "
                      f"| {r['curvature_mid_minus_endpoints']:+.4f} ({r['p_curvature']:.4f}) |")
    (OUT_DIR / "TGEO_P7B_M3_PAIRED.md").write_text("\n".join(md) + "\n")
    print("written:", OUT_DIR / "TGEO_P7B_M3_PAIRED.md")


if __name__ == "__main__":
    main()
