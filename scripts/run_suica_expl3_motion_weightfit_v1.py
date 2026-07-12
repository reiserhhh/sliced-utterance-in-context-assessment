#!/usr/bin/env python
"""EXPL-3 — motion-layer features on the spent-label cohort (F13, registered commit 36293aa). EXPLORATORY (spent labels, T1).

Custody status
--------------
PANDORA Big5 labels for the Tier-L cohort were unsealed at lockbox opening
#1 (git cd63d13, 2026-07-06) and are SPENT for confirmatory use. This
script re-reads those labels for a clearly-labeled exploratory analysis
(operator-ordered, F13). Results are recorded as EXPL-3 and must be
reported as exploratory wherever they appear. Essays confirm-half labels
are NOT touched. No other label source is read.

Governance gates (all BEFORE any new fitting; the run STOPS on failure):
  1. Eligibility gate replicated verbatim from the opening
     (n_conditions >= 4 & n_slices >= 12); assert n == 1,058.
  2. H2 (first_person -> Neuroticism) and H6 (politics choice -> Openness)
     recomputed and asserted to < 1e-9 against OPENING_REPORT.json —
     the EXPL-1 assert block copied verbatim.
  3. ANCHOR: EXPL-2's arm C (v4-16 union v5-15, per-trait RidgeCV,
     KFold(5, shuffle, rs=42)) rebuilt from its own caches and asserted
     equal to its stored artifact (per-trait and mean, at the artifact's
     4-dp rounding, tolerance 1e-9). Only then are motion features added.

Question (F13). How much does the V6 motion layer add to exploratory
detection power on the same spent labels? Feasibility pre-check (recorded
in the registration): tier_l bodies are 1,500-char capped, so m >= 3
windows are prose-impossible — the V6 feature set REDUCES to the
slope/position layer on m = 2 long texts (open/close pairs). Spectral
texture (r_c, rho_pi, shape pair) is NOT computable for labeled users
under the frozen extraction; that cap consequence is part of the answer.

Motion features (per gated user, over their long texts; label-free
construction; axes estimated on TIER-U data only — no leakage):
  candidates: body >= 1200 chars AND tokenize() >= 288 tokens (m >= 2);
  open = first 128 tokens, close = last 128 tokens (P5 geometry);
  PERSONALITY_LEAK_RE on either window drops the text. Windows scored
  with a19.score_slices_v2 + the frozen dav wcl transform (one fit).
  Dbar = user mean of (close - open) 19-vectors. Features (10):
    proj_dcomp1, proj_dcomp2 — Dbar on the PANDORA slope-factor axes,
      recomputed from the P8 cache exactly as run_suica_v6_e2_essays_
      motion_v1.py does (gp.last - gp.first per cid -> corr_guarded ->
      top eigvecs); projections in the axes' correlation space (Dbar
      scaled by the Tier-U Dp column sds — the eigvecs are eigenvectors
      of a correlation matrix, so unit-sd coordinates are their native
      space; scaling choice documented as an ambiguity resolution);
    proj_a3 — same, 3rd top eigvec (the A-comp3 motion-cluster rank);
    d_first_person, d_tension, d_directive, d_novelty — Dbar entries;
    open_first_person — mean opening-window first_person level;
    log1p_n_long, has_long — coverage.
  Standardization: covered users' raw features; uncovered users
  mean-imputed from covered means with has_long = 0; all 10 columns then
  z-scored over the full gated cohort (guard sd > 0). The per-fold
  StandardScaler of the EXPL-2 ridge protocol applies on top, as in all
  arms.

Arms (per-trait RidgeCV, EXPL-2 protocol, same alpha grid and folds):
  C = EXPL-2 union anchor (must reproduce mean r = .1361);
  D = C + 10 motion features; M = motion features alone.
Plus a 10 x 5 single-feature Pearson screen on covered users only
(|r| >= .10 flagged).

Registered leans (36293aa): Delta(C->D) mean in [+.005, +.02]; one
single-feature |r| >= .10 in A or O; M alone in [.03, .07].
KILL: Delta <= 0 -> the position/slope layer adds no exploratory signal
at this cap (recorded as the honest v4->v5->V6 detection verdict).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_persona.suica import PERSONALITY_LEAK_RE, tokenize  # noqa: E402
import scripts.run_suica_c2_purity_all19_v1 as a19  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
BIG5_LABELS = ROOT / "data_sets" / "prepared" / "pandora_official" / "pandora_official_big5_prepared.csv"
PREDICTORS = ROOT / "results" / "suica_lockbox_opening_1" / "predictors.parquet"
OPENING_REPORT = ROOT / "results" / "suica_lockbox_opening_1" / "OPENING_REPORT.json"
LOCKBOX_COMMENTS = TIER_DIR / "tier_l_comments.parquet"
EXPL2_DIR = ROOT / "results" / "suica_expl_v5_weightfit"
EXPL2_JSON = EXPL2_DIR / "EXPL2_V5_WEIGHTFIT.json"
EXPL2_CACHE = EXPL2_DIR / "v5u_tier_l_features.parquet"
P8_CACHE = ROOT / "results" / "suica_tgeo_p8_functionalization" / "cache_windows_scored19.parquet"
OUT_DIR = ROOT / "results" / "suica_expl3_motion_weightfit"
MOTION_CACHE = OUT_DIR / "motion_user_features_raw.parquet"

SEED = 42
EPS = 1e-4
N_CLASSES = 12
EXCLUDED_AXIS = 11
WIN = 128
MIN_TOKENS = 288
STYLE = ["tension_core_v2", "directive_action_v2", "first_person_usage_v2", "novelty_play_v2"]
TRAITS = ["Extraversion", "Neuroticism", "Agreeableness", "Conscientiousness", "Openness"]
V2_DIFFS = {"d_first_person": "first_person_usage_v2", "d_tension": "tension_core_v2",
            "d_directive": "directive_action_v2", "d_novelty": "novelty_play_v2"}
MOTION_COLS = ["proj_dcomp1", "proj_dcomp2", "proj_a3", "d_first_person", "d_tension",
               "d_directive", "d_novelty", "open_first_person", "log1p_n_long", "has_long"]

BANNER = "EXPLORATORY (spent labels, T1) — EXPL-3 motion-layer weight-fit (labels spent at opening #1; F13, 36293aa)"


def finalize_axes(pred: pd.DataFrame, eligible_idx: pd.Index) -> pd.DataFrame:
    """Verbatim replication of opening L232-239 (as EXPL-1/EXPL-2)."""
    shares = pred.loc[eligible_idx, [f"share_{k}" for k in range(N_CLASSES)]]
    pop = shares.mean(axis=0)
    for k in range(N_CLASSES):
        pred.loc[eligible_idx, f"choice_ax_{k:02d}"] = np.log(
            (shares[f"share_{k}"] + EPS) / (pop[f"share_{k}"] + EPS))
    return pred


def ridge_arm(X: np.ndarray, Y: np.ndarray, label: str) -> dict:
    """Per-trait RidgeCV — EXPL-2 protocol verbatim."""
    from sklearn.linear_model import RidgeCV
    from sklearn.model_selection import KFold
    from sklearn.preprocessing import StandardScaler
    kf = KFold(n_splits=5, shuffle=True, random_state=SEED)
    splits = list(kf.split(X))
    out = {}
    for j, trait in enumerate(TRAITS):
        y = Y[:, j]
        preds = np.empty_like(y)
        for tr, te in splits:
            sc = StandardScaler().fit(X[tr])
            m = RidgeCV(alphas=np.logspace(-2, 3, 11)).fit(sc.transform(X[tr]), y[tr])
            preds[te] = m.predict(sc.transform(X[te]))
        r, p = stats.pearsonr(preds, y)
        out[trait] = round(float(r), 4)
    out["MEAN_BIG5"] = round(float(np.mean([out[t] for t in TRAITS])), 4)
    print(f"[{label}] " + " ".join(f"{t[:1]}={out[t]:+.3f}" for t in TRAITS)
          + f" mean={out['MEAN_BIG5']:+.4f}")
    return out


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


def build_motion_user_features(users: list, cols: list) -> pd.DataFrame:
    """Raw per-user motion features over long Tier-L texts (label-free)."""
    if MOTION_CACHE.exists():
        cached = pd.read_parquet(MOTION_CACHE)
        print(f"[motion] loaded raw user features from cache ({len(cached)} covered users)")
        return cached

    com = pd.read_parquet(LOCKBOX_COMMENTS, columns=["author", "body"])
    com["author"] = com["author"].astype(str)
    com = com.loc[com["author"].isin(set(users))]
    body = com["body"].astype(str)
    cand = com.loc[body.str.len() >= 1200]
    print(f"[motion] tier-L comments of gated users: {len(com)}; candidates >=1200 chars: {len(cand)}")

    rows = []
    n_leak = 0
    for author, text in zip(cand["author"], cand["body"].astype(str)):
        tokens = tokenize(text)
        if len(tokens) < MIN_TOKENS:
            continue
        open_w = " ".join(tokens[:WIN])
        close_w = " ".join(tokens[-WIN:])
        if PERSONALITY_LEAK_RE.search(open_w) or PERSONALITY_LEAK_RE.search(close_w):
            n_leak += 1
            continue
        rows.append({"author": author, "open": open_w, "close": close_w})
    print(f"[motion] long texts kept: {len(rows)} (leak-dropped: {n_leak})")

    frame = pd.DataFrame(rows)
    slice_frame = pd.DataFrame({
        "user_id": pd.concat([frame["author"], frame["author"]], ignore_index=True),
        "slice_text": pd.concat([frame["open"], frame["close"]], ignore_index=True),
    })
    n_texts = len(frame)

    scored = a19.score_slices_v2(slice_frame[["user_id", "slice_text"]].assign(
        condition="_", half="_")[["user_id", "condition", "half", "slice_text"]])
    import scripts.run_suica_dev_anchor_performance_v1 as dav
    _, wcl_transform = dav.pandora_style_fit_and_battery()
    wcl = wcl_transform(slice_frame["slice_text"]).reset_index(drop=True)
    S = pd.concat([scored[list(a19.V3_BATTERY)].reset_index(drop=True),
                   wcl[list(a19.OP5_KEPT)]], axis=1)[cols].to_numpy(float)
    O = S[:n_texts]                       # opening windows
    C_ = S[n_texts:]                      # closing windows
    D = C_ - O                            # per-text close-open 19-vector

    per_text = pd.DataFrame({"author": frame["author"]})
    per_text["open_fp"] = O[:, cols.index("first_person_usage_v2")]
    for i, c in enumerate(cols):
        per_text[f"D::{c}"] = D[:, i]

    g = per_text.groupby("author")
    agg = g.mean()
    agg["n_long"] = g.size()
    agg.to_parquet(MOTION_CACHE)
    print(f"[motion] scored {n_texts} texts x 2 windows; covered users: {len(agg)}; cached")
    return agg


def main() -> None:
    print(BANNER)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ------------- governance gate 1: eligibility -------------
    pred = pd.read_parquet(PREDICTORS)
    pred.index = pred.index.astype(str)
    big5 = pd.read_csv(BIG5_LABELS).set_index("user_id")            # opening L439
    big5.index = big5.index.astype(str)
    gate = (pred["n_conditions"] >= 4) & (pred["n_slices"] >= 12)   # opening L301
    inter = pred.index.intersection(big5.index)
    elig = inter[gate.loc[inter].fillna(False).to_numpy(bool)]
    assert len(elig) == 1058, f"eligibility replication failed: {len(elig)}"
    pred = finalize_axes(pred, elig)
    users = sorted(elig)

    # ------------- governance gate 2: H2/H6 to <1e-9 (EXPL-1 block) -------------
    rep = json.loads(OPENING_REPORT.read_text())
    published = {h["id"]: h["r"] for h in rep["hypotheses"]}
    r_h2 = float(pred.loc[users, "first_person_usage_v2"].corr(big5.loc[users, "Neuroticism"]))
    r_h6 = float(pred.loc[users, "choice_ax_06"].corr(big5.loc[users, "Openness"]))
    assert abs(r_h2 - published["H2"]) < 1e-9, (r_h2, published["H2"])
    assert abs(r_h6 - published["H6"]) < 1e-9, (r_h6, published["H6"])
    print(f"gate + H2/H6 consistency ok: H2 {r_h2:.10f} H6 {r_h6:.10f} — match published")

    # ------------- governance gate 3: EXPL-2 arm C anchor -------------
    assert EXPL2_CACHE.exists(), "EXPL-2 feature cache missing — refuse to rebuild silently"
    v5u = pd.read_parquet(EXPL2_CACHE).reindex(users)
    keep = [c for c in v5u.columns if v5u[c].std() > 1e-9]
    battery_cols = STYLE + [f"choice_ax_{k:02d}" for k in range(N_CLASSES)
                            if k != EXCLUDED_AXIS] + ["choice_entropy"]    # opening L330
    Xa = pred.loc[users, battery_cols].to_numpy(float)
    Xb = v5u[keep].to_numpy(float)
    Xc = np.hstack([Xa, Xb])
    Y = big5.loc[users, TRAITS].to_numpy(float)

    stored = json.loads(EXPL2_JSON.read_text())["arm_C_union"]
    arm_c = ridge_arm(Xc, Y, f"C union-{Xc.shape[1]} (anchor)")
    for t in TRAITS + ["MEAN_BIG5"]:
        assert abs(arm_c[t] - stored[t]) < 1e-9, f"arm C anchor failed at {t}: {arm_c[t]} vs {stored[t]}"
    assert abs(arm_c["MEAN_BIG5"] - 0.1361) < 1e-9
    print(f"anchor ok: arm C reproduces EXPL-2 stored artifact exactly (mean {arm_c['MEAN_BIG5']:.4f})")

    # ------------- motion features (label-free construction) -------------
    cols = list(a19.V3_BATTERY) + list(a19.OP5_KEPT)

    # Tier-U slope-factor axes from the P8 cache, exactly as E2 recomputes them
    ps = pd.read_parquet(P8_CACHE)
    pcols = [c for c in ps.columns if c not in ("cid", "user_id", "j", "m", "t", "tau", "delta")]
    assert pcols == cols, "P8 cache construct order != a19 battery order"
    gp = ps.sort_values(["cid", "j"]).groupby("cid")
    Dp = gp[cols].last().to_numpy(float) - gp[cols].first().to_numpy(float)
    _, VDP = top_eigs(corr_guarded(Dp), 4)
    sd_Dp = Dp.std(0)
    sd_Dp = np.where(sd_Dp > 0, sd_Dp, 1.0)
    print(f"[axes] slope-factor axes from P8 cache: {Dp.shape[0]} cids; "
          f"D-comp1/2 + A-comp3 = eigvecs 1-3 of corr(Dp) (Tier-U only, no leakage)")

    agg = build_motion_user_features(users, cols)

    covered = [u for u in users if u in agg.index]
    n_cov = len(covered)
    med_texts = float(agg.loc[covered, "n_long"].median()) if n_cov else float("nan")
    print(f"[coverage] gated users: {len(users)}; with >=1 long text: {n_cov}; "
          f"median long texts per covered user: {med_texts:.0f}")

    Dbar = agg.loc[covered, [f"D::{c}" for c in cols]].to_numpy(float)
    Dbar_z = Dbar / sd_Dp                      # correlation-space coordinates of the axes
    raw = pd.DataFrame(index=pd.Index(covered, name="user_id"))
    raw["proj_dcomp1"] = Dbar_z @ VDP[:, 0]
    raw["proj_dcomp2"] = Dbar_z @ VDP[:, 1]
    raw["proj_a3"] = Dbar_z @ VDP[:, 2]
    for feat, con in V2_DIFFS.items():
        raw[feat] = Dbar[:, cols.index(con)]
    raw["open_first_person"] = agg.loc[covered, "open_fp"].to_numpy(float)
    raw["log1p_n_long"] = np.log1p(agg.loc[covered, "n_long"].to_numpy(float))
    raw["has_long"] = 1.0

    full = raw.reindex(users)
    cov_means = raw.mean(axis=0)
    full = full.fillna(cov_means)
    full.loc[~full.index.isin(covered), "has_long"] = 0.0
    z = full.copy()
    for c in MOTION_COLS:
        sd = z[c].std()
        z[c] = (z[c] - z[c].mean()) / (sd if sd > 1e-12 else 1.0)
    Xm = z[MOTION_COLS].to_numpy(float)

    # ------------- arms D and M -------------
    arm_d = ridge_arm(np.hstack([Xc, Xm]), Y, f"D union+motion-{Xc.shape[1] + Xm.shape[1]}")
    arm_m = ridge_arm(Xm, Y, "M motion-10")

    delta_mean = round(arm_d["MEAN_BIG5"] - arm_c["MEAN_BIG5"], 4)
    delta_per = {t: round(arm_d[t] - arm_c[t], 4) for t in TRAITS}
    print(f"[delta C->D] mean {delta_mean:+.4f}; per trait "
          + " ".join(f"{t[:1]}={delta_per[t]:+.4f}" for t in TRAITS))

    # ------------- single-feature screen (covered users only) -------------
    print(f"[screen] single-feature Pearson r on covered users (n={n_cov}); flag |r| >= .10:")
    screen = {}
    yc = big5.loc[covered, TRAITS]
    hits = []
    header = "  " + f"{'feature':18s}" + " ".join(f"{t[:5]:>8s}" for t in TRAITS)
    print(header)
    for feat in MOTION_COLS:
        if feat == "has_long":
            screen[feat] = {t: None for t in TRAITS}   # constant 1.0 on covered users
            print(f"  {feat:18s}" + " ".join(f"{'--':>8s}" for _ in TRAITS) + "  (constant on covered)")
            continue
        x = raw[feat].to_numpy(float)
        row = {}
        cells = []
        for t in TRAITS:
            r = float(stats.pearsonr(x, yc[t].to_numpy(float))[0])
            row[t] = round(r, 3)
            flag = "*" if abs(r) >= 0.10 else " "
            if abs(r) >= 0.10:
                hits.append((feat, t, round(r, 3)))
            cells.append(f"{r:+.3f}{flag}")
        screen[feat] = row
        print(f"  {feat:18s}" + " ".join(f"{c:>8s}" for c in cells))
    print(f"[screen] |r| >= .10 hits: {hits if hits else 'none'}")

    # ------------- outputs -------------
    result = {
        "banner": BANNER,
        "custody": {"labels": "PANDORA Big5 Tier-L labels, spent at opening #1 (git cd63d13)",
                    "essays_confirm_half": "untouched",
                    "other_label_sources": "none read",
                    "ledger_row": "EXPL-3"},
        "governance": {"eligibility_n": len(users),
                       "H2_recomputed": r_h2, "H6_recomputed": r_h6,
                       "H2_H6_tolerance": "<1e-9, passed",
                       "arm_C_anchor": "reproduced EXPL-2 stored artifact exactly (mean .1361)"},
        "coverage": {"n_gated": len(users), "n_covered": n_cov,
                     "median_long_texts": med_texts},
        "axes": {"source": "P8 cache (Tier-U), E2 recipe: per-cid last-first -> corr_guarded "
                           "-> top eigvecs 1-3; projections in correlation-space "
                           "(Dbar / sd(Dp))", "n_cids": int(Dp.shape[0])},
        "arm_C_anchor": arm_c,
        "arm_D_union_plus_motion": arm_d,
        "arm_M_motion_only": arm_m,
        "delta_C_to_D": {"mean": delta_mean, **delta_per},
        "single_feature_screen_covered_only": screen,
        "screen_hits_abs_r_ge_010": [{"feature": f, "trait": t, "r": r} for f, t, r in hits],
        "registered_leans": {"delta_mean": "[+.005, +.02]",
                             "one_surprise": "|r|>=.10 in A or O",
                             "M_alone": "[.03, .07]",
                             "kill": "delta <= 0"},
    }
    (OUT_DIR / "EXPL3_MOTION_WEIGHTFIT.json").write_text(json.dumps(result, indent=2))

    md = ["# EXPL-3 — motion-layer weight-fit (EXPLORATORY, spent labels)", "",
          f"> {BANNER}", ">",
          "> Labels spent at opening #1; reuse here is exploratory (F13, operator-ordered).",
          "> Gate, H2/H6, and the EXPL-2 arm-C anchor all reproduced before fitting.", "",
          f"Coverage: {n_cov} of {len(users)} gated users have >= 1 long (m>=2) text; "
          f"median {med_texts:.0f} texts. 1,500-char cap: only the slope/position layer is "
          f"computable (registration feasibility note).", "",
          "| arm | E | N | A | C | O | mean |", "|---|---|---|---|---|---|---|"]
    for name, arm in [("C: EXPL-2 union (anchor)", arm_c),
                      ("D: C + motion-10", arm_d),
                      ("M: motion-10 alone", arm_m)]:
        md.append("| " + name + " | " + " | ".join(f"{arm[t]:+.3f}" for t in TRAITS)
                  + f" | {arm['MEAN_BIG5']:+.4f} |")
    md += ["",
           f"Delta(C->D): mean {delta_mean:+.4f}; per trait "
           + ", ".join(f"{t} {delta_per[t]:+.4f}" for t in TRAITS) + ".",
           "",
           "Single-feature screen (covered users; |r| >= .10 flagged): "
           + (", ".join(f"{f}->{t} r={r:+.3f}" for f, t, r in hits) if hits else "no hits"),
           "",
           "Registered leans (36293aa): Delta mean in [+.005, +.02]; one |r|>=.10 surprise "
           "in A or O; M in [.03, .07]. KILL: Delta <= 0."]
    (OUT_DIR / "EXPL3_MOTION_WEIGHTFIT.md").write_text("\n".join(md) + "\n")
    print("written:", OUT_DIR / "EXPL3_MOTION_WEIGHTFIT.json")
    print("written:", OUT_DIR / "EXPL3_MOTION_WEIGHTFIT.md")


if __name__ == "__main__":
    main()
