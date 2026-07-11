#!/usr/bin/env python
"""T-GEO-P5 — position-in-text flow (F10.1 with t = position). Label-free, Tier-U.

The cleanest reading of "position within a text": within ONE comment, compare
the opening 128 tokens against the closing 128 tokens (comments >= 288 tokens,
so the windows never overlap and are separated by >= 32 tokens).

Group per F7: (Z/2)^{N_comments} swapping open/close labels within comment.

Statistics (registered in F10.4):
  (1) mean-level shift close - open, USER level primary (per-user mean paired
      diff over their long comments, gate >= 3; sign-flip null over users);
      comment level reported for scale.
  (2) frame flow: per-user mean open vector vs close vector (gate >= 5
      comments), between-person correlation frames, top-4 chordal distance;
      null = per-comment open/close swaps (500 draws).
Registered hunches (stated for honesty, exploratory): directive_action higher
at close; first_person higher at open; frame rotation small.
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
OUT_DIR = ROOT / "results" / "suica_tgeo_p5_position_flow"
SEED = 20260711
MIN_TOKENS = 288
WIN = 128
GATE_MEAN = 3
GATE_FRAME = 5
N_FLIP = 2000
N_FRAME_NULL = 500
TOPK = 4


def long_comment_slices() -> pd.DataFrame:
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
        open_text = " ".join(tokens[:WIN])
        close_text = " ".join(tokens[-WIN:])
        if PERSONALITY_LEAK_RE.search(open_text) or PERSONALITY_LEAK_RE.search(close_text):
            continue
        rows.append({"cid": cid, "user_id": author, "pos": "open", "slice_text": open_text})
        rows.append({"cid": cid, "user_id": author, "pos": "close", "slice_text": close_text})
    return pd.DataFrame(rows)


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


def user_means(D: np.ndarray, codes: np.ndarray, n_users: int) -> np.ndarray:
    out = np.zeros((n_users, D.shape[1]))
    cnt = np.bincount(codes, minlength=n_users).astype(float)
    for j in range(D.shape[1]):
        out[:, j] = np.bincount(codes, weights=D[:, j], minlength=n_users) / np.maximum(cnt, 1)
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = long_comment_slices()
    n_comments = frame["cid"].nunique()
    print(f"long comments kept: {n_comments} from {frame['user_id'].nunique()} users "
          f"({len(frame)} slices)")

    cols = list(a19.V3_BATTERY) + list(a19.OP5_KEPT)
    scored = a19.score_slices_v2(frame[["user_id", "slice_text"]].assign(
        condition="_", half="_")[["user_id", "condition", "half", "slice_text"]])
    import scripts.run_suica_dev_anchor_performance_v1 as dav
    _, wcl_transform = dav.pandora_style_fit_and_battery()
    wcl = wcl_transform(frame["slice_text"]).reset_index(drop=True)
    src = pd.concat([frame[["cid", "user_id", "pos"]].reset_index(drop=True),
                     scored[a19.V3_BATTERY].reset_index(drop=True),
                     wcl[a19.OP5_KEPT]], axis=1)

    wide_o = src[src["pos"] == "open"].set_index("cid")
    wide_c = src[src["pos"] == "close"].set_index("cid")
    cids = wide_o.index.intersection(wide_c.index)
    O = wide_o.loc[cids, cols].to_numpy(float)
    C = wide_c.loc[cids, cols].to_numpy(float)
    authors = wide_o.loc[cids, "user_id"]
    D = C - O
    rng = np.random.default_rng(SEED)

    # (1) mean-level shift, user-level primary
    ud = pd.DataFrame(D, columns=cols).assign(user_id=authors.to_numpy())
    per_user = ud.groupby("user_id").agg(**{c: (c, "mean") for c in cols},
                                         n=("user_id", "size"))
    per_user = per_user[per_user["n"] >= GATE_MEAN]
    mean_rows = []
    for c in cols:
        s = per_user[c].to_numpy(float)
        obs = float(s.mean())
        flips = rng.choice([-1.0, 1.0], size=(N_FLIP, len(s)))
        p = float((np.abs((flips * s).mean(axis=1)) >= abs(obs)).mean())
        mean_rows.append({"construct": c, "n_users": int(len(s)),
                          "user_mean_close_minus_open": round(obs, 4),
                          "frac_users_positive": round(float((s > 0).mean()), 3),
                          "p_signflip": round(p, 4),
                          "comment_mean": round(float(D[:, cols.index(c)].mean()), 4),
                          "comment_sd": round(float(D[:, cols.index(c)].std()), 4)})
        star = " *" if p < 0.005 and abs(obs) > 0 else ""
        print(f"  [shift] {c}: user-mean {obs:+.4f} (n={len(s)}) p={p:.4f}{star}")

    # (2) frame flow with per-comment swap null
    ucounts = authors.value_counts()
    keep_users = ucounts.index[ucounts >= GATE_FRAME]
    mask_rows = authors.isin(keep_users).to_numpy()
    codes, uniq = pd.factorize(authors[mask_rows])
    Of, Cf, Df = O[mask_rows], C[mask_rows], D[mask_rows]
    n_users = len(uniq)
    XO = user_means(Of, codes, n_users)
    XC = user_means(Cf, codes, n_users)
    VO, lamO = corr_frame(XO)
    VC, lamC = corr_frame(XC)
    obs_d = chordal(VO, VC)
    congr = [round(max(abs(float(VO[:, i] @ VC[:, j])) for j in range(TOPK)), 3)
             for i in range(TOPK)]
    null_d = []
    for _ in range(N_FRAME_NULL):
        swap = rng.random(len(Df)) < 0.5
        # swapped comment i contributes C_i to the "open" mean and O_i to the
        # "close" mean, i.e. user open-mean shifts by mean_i(swap_i * D_i)
        delta = user_means(Df * swap[:, None], codes, n_users)
        Vo, _ = corr_frame(XO + delta)
        Vc, _ = corr_frame(XC - delta)
        null_d.append(chordal(Vo, Vc))
    p_frame = float((np.array(null_d) >= obs_d).mean())
    print(f"[frame] users={n_users} chordal(open,close)={obs_d:.4f} "
          f"null95={np.percentile(null_d, 95):.4f} p={p_frame:.4f} congr={congr}")

    result = {"n_long_comments": int(len(cids)), "n_users_frame": int(n_users),
              "mean_shift_user_level": mean_rows,
              "frame_flow": {"chordal_top4_open_close": round(obs_d, 4),
                             "null_mean": round(float(np.mean(null_d)), 4),
                             "null_p95": round(float(np.percentile(null_d, 95)), 4),
                             "p": round(p_frame, 4),
                             "per_pc_best_congruence": congr,
                             "lambda_open": [round(float(x), 3) for x in lamO],
                             "lambda_close": [round(float(x), 3) for x in lamC]}}
    (OUT_DIR / "TGEO_P5_POSITION_FLOW.json").write_text(json.dumps(result, indent=2))
    md = ["# T-GEO-P5 — position-in-text flow: open vs close 128 tokens (label-free)", "",
          f"Comments >= {MIN_TOKENS} tokens: n = {len(cids)}; user-level gate >= {GATE_MEAN} "
          f"for mean shifts, >= {GATE_FRAME} for frames (n = {n_users} users).", "",
          "## Mean-level shift (close - open), user level, sign-flip null",
          "", "| construct | n users | user mean diff | frac > 0 | p |", "|---|---|---|---|---|"]
    for r in sorted(mean_rows, key=lambda r: r["p_signflip"]):
        md.append(f"| {r['construct']} | {r['n_users']} | {r['user_mean_close_minus_open']:+.4f} "
                  f"| {r['frac_users_positive']:.2f} | {r['p_signflip']:.4f} |")
    ff = result["frame_flow"]
    md += ["", "## Frame flow (top-4 subspace, open vs close)",
           "", f"Chordal distance {ff['chordal_top4_open_close']} vs swap-null mean "
           f"{ff['null_mean']} (p95 {ff['null_p95']}), p = {ff['p']}. Per-PC best "
           f"congruence {ff['per_pc_best_congruence']}."]
    (OUT_DIR / "TGEO_P5_POSITION_FLOW.md").write_text("\n".join(md) + "\n")
    print("written:", OUT_DIR / "TGEO_P5_POSITION_FLOW.md")


if __name__ == "__main__":
    main()
