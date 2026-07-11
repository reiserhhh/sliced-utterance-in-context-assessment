#!/usr/bin/env python
"""T-GEO-P1 — phi-linearity of aggregation on PANDORA (label-free, Tier-U).

Imports the v5 T-geometry Layer-II instrument (trading-agent-claude,
docs/SUICA_V5_TGEOMETRY_REFORMULATION_20260711.md) to the upstream corpus.

Theory (phi-linearization theorem, ported): with phi(r) = r/(1-r), the
Spearman-Brown lengthening family is exactly phi(r_W) = W * phi(rho).
Under the parallel-measurement model, phi against designed aggregation
level W is a straight line through 0 with slope phi(1); under clustered
noise (venue shocks shared by slices from the same condition), phi(W) =
a*W / (1 + b*W): concave, asymptote a/b, and the curvature parameter b is
an estimator of the clustered-noise share.

PANDORA prediction (stated before running, directional): F-family
constructs (person-borne form habits) should run near-linear; C-family
constructs (venue signatures) should saturate early, because their
"day-shock" analog is the venue shock that our within-half slice pools
share. tension (undetermined) has no committed prediction.

Design (data-independent):
  - Frozen pass-A slices (count-verified cache), early/late halves.
  - Cohort fixed across W: users with >= 8 slices in BOTH halves.
  - Nested designed subsets: per user-half, permute slice indices with a
    per-(user,half) seeded rng (crc32) and take the first 1/2/4/8 — nested
    so the W-curve is monotone in information, no selection on outcomes.
  - r(W) = Spearman correlation across users of (early_W mean, late_W
    mean), matching the v5 instrument; Pearson reported as sensitivity.
  - phi ratios phi(W)/phi(1) vs the parallel-model prediction W;
    saturating-model fit phi(W) = a*W/(1+b*W) by least squares;
    bootstrap 95% CIs (500 user resamples, seeded).
"""
from __future__ import annotations

import json
import sys
import zlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import curve_fit

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_suica_c2_purity_all19_v1 as a19  # noqa: E402

OUT_DIR = ROOT / "results" / "suica_tgeo_p1_phi_linearity"
WS = [1, 2, 4, 8]
N_BOOT = 500

F_FAMILY = ["first_person_usage_v2", "wcl_60", "wcl_13", "wcl_23"]
C_FAMILY = ["novelty_play_v2", "wcl_02", "wcl_25", "wcl_35"]
UND = ["tension_core_v2"]
CONSTRUCTS = F_FAMILY + C_FAMILY + UND


def phi(r: float) -> float:
    r = float(np.clip(r, -0.999, 0.999))
    return r / (1.0 - r)


def sat_model(w, a, b):
    return a * w / (1.0 + b * w)


def build_matrices(src: pd.DataFrame, cols: list[str]) -> dict:
    """Per user-half nested subsets; returns {W: DataFrame(user x [e_,l_ cols])}."""
    rows = {}
    for (user, half), g in src.groupby(["user_id", "half"], sort=False):
        idx = np.arange(len(g))
        rng = np.random.default_rng(zlib.crc32(f"{user}|{half}".encode()) % (2**31))
        rng.shuffle(idx)
        rows[(user, half)] = g.iloc[idx].reset_index(drop=True)
    users = sorted({u for (u, h) in rows
                    if (u, "early") in rows and (u, "late") in rows
                    and len(rows[(u, "early")]) >= max(WS)
                    and len(rows[(u, "late")]) >= max(WS)})
    print(f"cohort (>= {max(WS)} slices per half): {len(users)} users")
    mats = {}
    for W in WS:
        e = pd.DataFrame({c: [rows[(u, "early")][c].iloc[:W].mean() for u in users]
                          for c in cols}, index=users)
        l = pd.DataFrame({c: [rows[(u, "late")][c].iloc[:W].mean() for u in users]
                          for c in cols}, index=users)
        mats[W] = (e, l)
    return mats, users


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = a19.rebuild_passA_with_text()
    print(f"slices: {len(frame)}")

    scored = a19.score_slices_v2(frame[["user_id", "condition", "half", "slice_text"]])
    import scripts.run_suica_dev_anchor_performance_v1 as dav
    _, wcl_transform = dav.pandora_style_fit_and_battery()
    wcl = wcl_transform(frame["slice_text"]).reset_index(drop=True)
    src = pd.concat([frame[["user_id", "condition", "half"]].reset_index(drop=True),
                     scored[[c for c in CONSTRUCTS if c.endswith("_v2")]].reset_index(drop=True),
                     wcl[[c for c in CONSTRUCTS if c.startswith("wcl_")]]], axis=1)

    mats, users = build_matrices(src, CONSTRUCTS)
    n = len(users)

    results = []
    boot_seed_rng = np.random.default_rng(20260711)
    boot_idx = [boot_seed_rng.integers(0, n, n) for _ in range(N_BOOT)]

    for c in CONSTRUCTS:
        fam = ("F" if c in F_FAMILY else "C" if c in C_FAMILY else "und")
        r_sp, r_pe, phis = {}, {}, {}
        for W in WS:
            e, l = mats[W]
            r_sp[W] = float(stats.spearmanr(e[c], l[c]).statistic)
            r_pe[W] = float(stats.pearsonr(e[c], l[c])[0])
            phis[W] = phi(r_sp[W])
        ratios = {W: (phis[W] / phis[1] if abs(phis[1]) > 1e-12 else np.nan) for W in WS}

        boot_ratios = {W: [] for W in WS[1:]}
        e1, l1 = mats[1]
        arrs = {W: (mats[W][0][c].to_numpy(), mats[W][1][c].to_numpy()) for W in WS}
        for bi in boot_idx:
            p1 = phi(float(stats.spearmanr(arrs[1][0][bi], arrs[1][1][bi]).statistic))
            if abs(p1) < 1e-12:
                continue
            for W in WS[1:]:
                pw = phi(float(stats.spearmanr(arrs[W][0][bi], arrs[W][1][bi]).statistic))
                boot_ratios[W].append(pw / p1)
        ci = {W: (float(np.percentile(boot_ratios[W], 2.5)),
                  float(np.percentile(boot_ratios[W], 97.5)))
              if len(boot_ratios[W]) >= 100 else (np.nan, np.nan) for W in WS[1:]}

        try:
            popt, _ = curve_fit(sat_model, np.array(WS, float),
                                np.array([phis[W] for W in WS]),
                                p0=[max(phis[1], 1e-3), 0.1], maxfev=20000)
            a_fit, b_fit = float(popt[0]), float(popt[1])
            asymptote = a_fit / b_fit if b_fit > 1e-9 else np.inf
        except Exception:
            a_fit = b_fit = asymptote = np.nan

        results.append({
            "construct": c, "family": fam, "n_users": n,
            **{f"r_sp_W{W}": round(r_sp[W], 4) for W in WS},
            **{f"phi_W{W}": round(phis[W], 4) for W in WS},
            **{f"ratio_W{W}": round(ratios[W], 3) for W in WS[1:]},
            **{f"ratio_W{W}_ci": [round(ci[W][0], 3), round(ci[W][1], 3)] for W in WS[1:]},
            "parallel_pred": {f"W{W}": W for W in WS[1:]},
            "sat_a": round(a_fit, 4) if a_fit == a_fit else None,
            "sat_b": round(b_fit, 4) if b_fit == b_fit else None,
            "phi_max_asymptote": (round(asymptote, 3)
                                  if asymptote == asymptote and np.isfinite(asymptote) else None),
            **{f"r_pe_W{W}": round(r_pe[W], 4) for W in WS},
        })
        print(f"  {c} ({fam}): phi ratios "
              + " ".join(f"W{W}={ratios[W]:.2f}/{W}" for W in WS[1:])
              + (f"  phi_max={asymptote:.2f}" if asymptote == asymptote and np.isfinite(asymptote) else ""))

    (OUT_DIR / "TGEO_P1_PHI_LINEARITY.json").write_text(json.dumps(
        {"design": "nested seeded subsets, W in {1,2,4,8}, cohort fixed, Spearman primary",
         "n_users": n, "results": results}, indent=2))

    md = ["# T-GEO-P1 — phi-linearity of aggregation on PANDORA (label-free)", "",
          f"Cohort: {n} Tier-U users with >= 8 slices in both halves; nested designed",
          "subsets; r = Spearman(early_W, late_W); phi = r/(1-r). Parallel model",
          "predicts phi(W)/phi(1) = W; venue-clustered noise predicts saturation.", "",
          "| construct | fam | phi(1) | ratio W2 (pred 2) | ratio W4 (pred 4) | ratio W8 (pred 8) | phi_max |",
          "|---|---|---|---|---|---|---|"]
    for r in results:
        md.append(f"| {r['construct']} | {r['family']} | {r['phi_W1']:.3f} "
                  f"| {r['ratio_W2']:.2f} {r['ratio_W2_ci']} "
                  f"| {r['ratio_W4']:.2f} {r['ratio_W4_ci']} "
                  f"| {r['ratio_W8']:.2f} {r['ratio_W8_ci']} "
                  f"| {r['phi_max_asymptote']} |")
    (OUT_DIR / "TGEO_P1_PHI_LINEARITY.md").write_text("\n".join(md) + "\n")
    print("written:", OUT_DIR / "TGEO_P1_PHI_LINEARITY.md")


if __name__ == "__main__":
    main()
