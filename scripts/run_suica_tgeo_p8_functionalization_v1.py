#!/usr/bin/env python
"""T-GEO-P8 — functionalization of the flow (F10.7). Label-free, Tier-U.

P8a (in-range interpolation, m=3): predictor ladder for the mid window —
  grand (cross-fitted) -> person (LOO user mean of mids) -> function-linear
  (the comment's own endpoint average) -> function-quadratic (+ cross-fitted
  population curvature). User-level MAE, bootstrap-over-users CIs.

P8b (out-of-range coordinate race): on m<=3 support a monotone flow in
relative position t and an additive boundary-zone model are NOT identifiable
(F10.7 registration states this); they separate only in the deep interior of
long comments — (start-distance >= 2, end-distance >= 2) cells that short
comments never realize. Three models fitted ONLY on m<=3 user-level cell
means (five observed (tau, delta) cells):
  CONSTANT; RELATIVE FLOW a + b*t + c*t^2 (OLS on 5 cells);
  ADDITIVE ZONES a + s(tau-zone) + e(delta-zone), zones {0,1,2+}
  (exactly identified: a = v01+v10-v11, e1 = v01-a, s1 = v10-a,
   e2 = v02-a, s2 = v20-a).
Shapes transported to m>=4 comments with intercept recalibrated on long
ENDPOINT windows only; judged by MAE and signed bias on INTERIOR windows
(deep-interior subset = genuine out-of-range). Bootstrap over comments.
PILOT status: the long-comment evaluation set is thin (declared in the
F10.7 registration, commit c5a9b4f).
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
from scripts.run_suica_tgeo_p7_flow_curve_v1 import build_windows  # noqa: E402

OUT_DIR = ROOT / "results" / "suica_tgeo_p8_functionalization"
SEED = 20260711
N_BOOT = 500
HIGHLIGHT = ["first_person_usage_v2", "tension_core_v2", "directive_action_v2",
             "novelty_play_v2", "wcl_36", "wcl_54", "wcl_22", "wcl_15",
             "wcl_25", "wcl_02"]


def scored_windows() -> tuple[pd.DataFrame, list[str]]:
    cols = list(a19.V3_BATTERY) + list(a19.OP5_KEPT)
    cache = OUT_DIR / "cache_windows_scored19.parquet"
    if cache.exists():
        return pd.read_parquet(cache), cols
    frame = build_windows()
    scored = a19.score_slices_v2(frame[["user_id", "slice_text"]].assign(
        condition="_", half="_")[["user_id", "condition", "half", "slice_text"]])
    import scripts.run_suica_dev_anchor_performance_v1 as dav
    _, wcl_transform = dav.pandora_style_fit_and_battery()
    wcl = wcl_transform(frame["slice_text"]).reset_index(drop=True)
    src = pd.concat([frame[["cid", "user_id", "j", "m", "t"]].reset_index(drop=True),
                     scored[a19.V3_BATTERY].reset_index(drop=True),
                     wcl[a19.OP5_KEPT]], axis=1)
    src["tau"] = src["j"]
    src["delta"] = src["m"] - 1 - src["j"]
    src.to_parquet(cache)
    return src, cols


def per_user_mae(err: np.ndarray, ucodes: np.ndarray, nu: int) -> np.ndarray:
    cnt = np.bincount(ucodes, minlength=nu).astype(float)
    s = np.bincount(ucodes, weights=np.abs(err), minlength=nu)
    return (s / np.maximum(cnt, 1))[cnt > 0]


def user_mean_mae(err: np.ndarray, ucodes: np.ndarray, nu: int) -> float:
    return float(per_user_mae(err, ucodes, nu).mean())


def p8a(src: pd.DataFrame, cols: list[str], rng) -> list[dict]:
    m3 = src[src["m"] == 3].sort_values(["cid", "j"])
    full = m3.groupby("cid").size()
    m3 = m3[m3["cid"].isin(full.index[full == 3])]
    X = m3[cols].to_numpy(float).reshape(-1, 3, len(cols))
    cids = m3["cid"].to_numpy()[::3]
    users = m3["user_id"].to_numpy()[::3]
    uc = pd.Series(users).value_counts()
    keep = users_mask = np.isin(users, uc.index[uc >= 2])
    X, users, cids = X[keep], users[keep], cids[keep]
    ucodes, uniq = pd.factorize(users)
    nu = len(uniq)
    half = np.array([zlib.crc32(("p8::" + u).encode()) % 2 for u in users])
    print(f"[P8a] m=3 comments {len(X)}, users {nu}")

    mid = X[:, 1, :]
    endp = (X[:, 0, :] + X[:, 2, :]) / 2.0
    rows = []
    for i, c in enumerate(cols):
        y = mid[:, i]
        # grand (cross-fitted by user-half)
        g = np.where(half == 0, y[half == 1].mean(), y[half == 0].mean())
        # person: LOO user mean of mids
        usum = np.bincount(ucodes, weights=y, minlength=nu)
        ucnt = np.bincount(ucodes, minlength=nu).astype(float)
        person = (usum[ucodes] - y) / (ucnt[ucodes] - 1)
        # function rungs
        flin = endp[:, i]
        curv0 = (y - flin)[half == 1].mean()
        curv1 = (y - flin)[half == 0].mean()
        fquad = flin + np.where(half == 0, curv0, curv1)
        errs = {"grand": y - g, "person": y - person,
                "func_linear": y - flin, "func_quad": y - fquad}
        umae = {k: per_user_mae(v, ucodes, nu) for k, v in errs.items()}
        maes = {k: float(v.mean()) for k, v in umae.items()}
        # bootstrap over users (the aggregation unit) for the two key deltas
        d_pf, d_lq = [], []
        n_eff = len(umae["person"])
        for _ in range(N_BOOT):
            bu = rng.integers(0, n_eff, n_eff)
            d_pf.append(float((umae["person"][bu] - umae["func_linear"][bu]).mean()))
            d_lq.append(float((umae["func_linear"][bu] - umae["func_quad"][bu]).mean()))
        rows.append({"construct": c, "mae": {k: round(v, 4) for k, v in maes.items()},
                     "delta_person_minus_funclinear": round(float(np.mean(d_pf)), 4),
                     "delta_pf_ci": [round(float(np.percentile(d_pf, q)), 4) for q in (2.5, 97.5)],
                     "delta_funclinear_minus_funcquad": round(float(np.mean(d_lq)), 4),
                     "delta_lq_ci": [round(float(np.percentile(d_lq, q)), 4) for q in (2.5, 97.5)]})
        if c in HIGHLIGHT:
            print(f"  [P8a {c}] MAE grand {maes['grand']:.3f} person {maes['person']:.3f} "
                  f"func_lin {maes['func_linear']:.3f} func_quad {maes['func_quad']:.3f} "
                  f"| person-funclin {rows[-1]['delta_person_minus_funclinear']:+.3f} "
                  f"CI {rows[-1]['delta_pf_ci']}")
    return rows


def p8b(src: pd.DataFrame, cols: list[str], rng) -> dict:
    short = src[src["m"] <= 3]
    lng = src[src["m"] >= 4]
    n_lc = lng["cid"].nunique()
    interior = lng[(lng["tau"] >= 1) & (lng["delta"] >= 1)]
    deep = lng[(lng["tau"] >= 2) & (lng["delta"] >= 2)]
    print(f"[P8b] long comments {n_lc} ({lng['user_id'].nunique()} users); "
          f"interior windows {len(interior)}, deep {len(deep)}")

    # user-level cell means on the five short cells
    short = short.assign(zt=np.minimum(short["tau"], 2), zd=np.minimum(short["delta"], 2))
    cells = [(0, 1), (1, 0), (0, 2), (1, 1), (2, 0)]
    tvals = np.array([0.0, 1.0, 0.0, 0.5, 1.0])
    cm = {}
    for (zt, zd) in cells:
        sub = short[(short["zt"] == zt) & (short["zd"] == zd)]
        cm[(zt, zd)] = sub.groupby("user_id")[cols].mean().mean(axis=0).to_numpy()
    V = np.array([cm[c] for c in cells])   # (5, 19)

    # ZONES closed form
    a_z = V[0] + V[1] - V[3]
    e1, s1 = V[0] - a_z, V[1] - a_z
    e2, s2 = V[2] - a_z, V[4] - a_z
    s = np.stack([np.zeros_like(s1), s1, s2])   # s[zone]
    e = np.stack([np.zeros_like(e1), e1, e2])
    # RELATIVE quadratic OLS on 5 cells
    D = np.stack([np.ones(5), tvals, tvals ** 2], axis=1)
    beta, *_ = np.linalg.lstsq(D, V, rcond=None)  # (3, 19)
    a_c = V.mean(axis=0)                           # CONSTANT

    def predict(df: pd.DataFrame) -> dict[str, np.ndarray]:
        zt = np.minimum(df["tau"].to_numpy(), 2)
        zd = np.minimum(df["delta"].to_numpy(), 2)
        t = df["t"].to_numpy()
        return {"zones": a_z[None, :] + s[zt] + e[zd],
                "relative": beta[0][None, :] + np.outer(t, beta[1]) + np.outer(t ** 2, beta[2]),
                "constant": np.tile(a_c, (len(df), 1))}

    endpoints = lng[(lng["tau"] == 0) | (lng["delta"] == 0)]
    Y_end = endpoints[cols].to_numpy(float)
    shift = {k: (Y_end - v).mean(axis=0) for k, v in predict(endpoints).items()}

    out = {"n_long_comments": int(n_lc), "n_interior": int(len(interior)),
           "n_deep": int(len(deep)), "models": {}}
    for label, dfe in [("interior", interior), ("deep_interior", deep)]:
        Y = dfe[cols].to_numpy(float)
        ucodes, uniq = pd.factorize(dfe["user_id"])
        preds = {k: v + shift[k][None, :] for k, v in predict(dfe).items()}
        res = {}
        for i, c in enumerate(cols):
            umae = {k: per_user_mae(Y[:, i] - p[:, i], ucodes, len(uniq))
                    for k, p in preds.items()}
            maes = {k: float(v.mean()) for k, v in umae.items()}
            bias = {k: round(float((Y[:, i] - p[:, i]).mean()), 4) for k, p in preds.items()}
            dzr = []
            n_eff = len(umae["zones"])
            for _ in range(N_BOOT):
                bu = rng.integers(0, n_eff, n_eff)
                dzr.append(float((umae["zones"][bu] - umae["relative"][bu]).mean()))
            res[c] = {"mae": {k: round(v, 4) for k, v in maes.items()},
                      "bias": bias,
                      "zones_minus_relative": round(float(np.mean(dzr)), 4),
                      "ci": [round(float(np.percentile(dzr, q)), 4) for q in (2.5, 97.5)]}
            if c in HIGHLIGHT and label == "deep_interior":
                print(f"  [P8b deep {c}] MAE const {maes['constant']:.3f} "
                      f"rel {maes['relative']:.3f} zones {maes['zones']:.3f} "
                      f"| z-r {res[c]['zones_minus_relative']:+.3f} CI {res[c]['ci']}")
        out["models"][label] = res
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    src, cols = scored_windows()
    rng = np.random.default_rng(SEED)
    a_rows = p8a(src, cols, rng)
    b_res = p8b(src, cols, rng)
    result = {"p8a_interpolation_m3": a_rows, "p8b_coordinate_race": b_res}
    (OUT_DIR / "TGEO_P8_FUNCTIONALIZATION.json").write_text(json.dumps(result, indent=2))

    md = ["# T-GEO-P8 — functionalization of the flow (F10.7, label-free)", "",
          "## P8a — in-range interpolation ladder (m=3 mid window, user-level MAE)", "",
          "| construct | grand | person | func linear | func quad | person-funclin [CI] |",
          "|---|---|---|---|---|---|"]
    for r in a_rows:
        if r["construct"] in HIGHLIGHT:
            m = r["mae"]
            md.append(f"| {r['construct']} | {m['grand']} | {m['person']} | "
                      f"{m['func_linear']} | {m['func_quad']} | "
                      f"{r['delta_person_minus_funclinear']:+.3f} {r['delta_pf_ci']} |")
    md += ["", "## P8b — out-of-range coordinate race (fit m<=3, predict m>=4 interiors)",
           "", f"Long comments: {b_res['n_long_comments']}; interior windows "
           f"{b_res['n_interior']}; deep (out-of-range) {b_res['n_deep']}. PILOT.", "",
           "| construct | set | MAE const / relative / zones | zones-relative [CI] |",
           "|---|---|---|---|"]
    for label in ["interior", "deep_interior"]:
        for c in HIGHLIGHT:
            r = b_res["models"][label][c]
            m = r["mae"]
            md.append(f"| {c} | {label} | {m['constant']} / {m['relative']} / {m['zones']} "
                      f"| {r['zones_minus_relative']:+.3f} {r['ci']} |")
    (OUT_DIR / "TGEO_P8_FUNCTIONALIZATION.md").write_text("\n".join(md) + "\n")
    print("written:", OUT_DIR / "TGEO_P8_FUNCTIONALIZATION.md")


if __name__ == "__main__":
    main()
