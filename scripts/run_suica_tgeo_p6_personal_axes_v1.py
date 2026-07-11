#!/usr/bin/env python
"""T-GEO-P6 — personal axes: is the factor FRAME itself a personal signature?
Label-free, Tier-U. Instrument for F10.3 (individuality as axes).

Per user per half: leading eigenvector of the WITHIN-person slice correlation
of the 19-construct battery. Tests, per F10.4 registered predictions:

  (1) self vs stranger: |cos(u_early, u_late)| for the same user vs cyclic-shift
      derangement pairings (F7 row 1 group). Conjecture requires self > stranger.
  (2) noise ceiling: within-half odd/even split congruence. If early-late is
      well below the ceiling, personal frames genuinely rotate over time.
  (3) SHARP arm: residualize slices against the population top-4 frame
      (slice-level, early-pooled) first. The conjecture DIES if residualized
      self <= stranger (personal frames = noisy copies of the shared frame).
  (4) nameability dispersion: best |cos| of personal axes against population
      PC1..PC4 vs a random-direction baseline in R^19.

Arms: pooled (all conditions; gate >= 12 slices per half) and top1 (largest
condition only; gate >= 8 per half — pass-A cells cap at 10 slices/half, so
this arm is noisier and reads the style-only frame with venue held constant).
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

OUT_DIR = ROOT / "results" / "suica_tgeo_p6_personal_axes"
SEED = 20260711
N_SHIFT = 300
N_RANDOM = 20000
GATE_POOLED = 12
GATE_TOP1 = 8


def scored_pass_a() -> tuple[pd.DataFrame, list[str]]:
    cache = OUT_DIR / "cache_passA_scored19.parquet"
    cols = list(a19.V3_BATTERY) + list(a19.OP5_KEPT)
    if cache.exists():
        return pd.read_parquet(cache), cols
    frame = a19.rebuild_passA_with_text()
    scored = a19.score_slices_v2(frame[["user_id", "condition", "half", "slice_text"]])
    import scripts.run_suica_dev_anchor_performance_v1 as dav
    _, wcl_transform = dav.pandora_style_fit_and_battery()
    wcl = wcl_transform(frame["slice_text"]).reset_index(drop=True)
    src = pd.concat([frame[["user_id", "condition", "half"]].reset_index(drop=True),
                     scored[a19.V3_BATTERY].reset_index(drop=True),
                     wcl[a19.OP5_KEPT]], axis=1)
    src.to_parquet(cache)
    return src, cols


def corr_guarded(X: np.ndarray) -> np.ndarray:
    mu = X.mean(0)
    sd = X.std(0)
    Z = np.where(sd > 0, (X - mu) / np.where(sd > 0, sd, 1.0), 0.0)
    C = (Z.T @ Z) / max(1, len(Z) - 1)
    np.fill_diagonal(C, 1.0)
    return C


def leading_vec(X: np.ndarray) -> np.ndarray:
    w, V = np.linalg.eigh(corr_guarded(X))
    return V[:, int(np.argmax(w))]


def self_vs_stranger(UE: np.ndarray, UL: np.ndarray, rng) -> dict:
    n = len(UE)
    self_c = np.abs((UE * UL).sum(axis=1))
    obs = float(self_c.mean())
    shifts = rng.choice(np.arange(1, n), size=min(N_SHIFT, n - 1), replace=False)
    null_means = np.array([np.abs((UE * np.roll(UL, k, axis=0)).sum(axis=1)).mean()
                           for k in shifts])
    return {"n_users": int(n),
            "self_mean_abs_cos": round(obs, 4),
            "self_median_abs_cos": round(float(np.median(self_c)), 4),
            "stranger_mean_abs_cos": round(float(null_means.mean()), 4),
            "p_self_gt_stranger": round(float((null_means >= obs).mean()), 4)}


def frames_for(scored: pd.DataFrame, cols: list[str], gate: int,
               resid: np.ndarray | None = None,
               std: tuple[np.ndarray, np.ndarray] | None = None) -> dict:
    """Per-user early/late leading eigenvectors + odd/even ceilings.
    resid = population top-k frame to project out (applied to standardized scores)."""
    counts = scored.groupby(["user_id", "half"]).size().unstack(fill_value=0)
    ok = counts.index[(counts.get("early", 0) >= gate) & (counts.get("late", 0) >= gate)]
    ue, ul, ceil_e, ceil_l = [], [], [], []
    for user in ok:
        halves = {}
        for h in ["early", "late"]:
            X = scored.loc[(scored["user_id"] == user) & (scored["half"] == h),
                           cols].to_numpy(float)
            if resid is not None:
                mu, sd = std
                Z = (X - mu) / sd
                X = Z - Z @ resid @ resid.T
            halves[h] = X
        ue.append(leading_vec(halves["early"]))
        ul.append(leading_vec(halves["late"]))
        idx_e = np.arange(len(halves["early"]))
        idx_l = np.arange(len(halves["late"]))
        ceil_e.append(abs(float(leading_vec(halves["early"][idx_e % 2 == 0])
                                @ leading_vec(halves["early"][idx_e % 2 == 1]))))
        ceil_l.append(abs(float(leading_vec(halves["late"][idx_l % 2 == 0])
                                @ leading_vec(halves["late"][idx_l % 2 == 1]))))
    return {"UE": np.array(ue), "UL": np.array(ul), "users": list(ok),
            "ceiling_early_oddeven": round(float(np.mean(ceil_e)), 4),
            "ceiling_late_oddeven": round(float(np.mean(ceil_l)), 4)}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scored, cols = scored_pass_a()
    rng = np.random.default_rng(SEED)

    # population slice-level top-4 frame from EARLY slices (for residualization + alignment)
    early = scored.loc[scored["half"] == "early", cols].to_numpy(float)
    mu, sd = early.mean(0), np.where(early.std(0) > 0, early.std(0), 1.0)
    w, V = np.linalg.eigh(corr_guarded(early))
    order = np.argsort(w)[::-1]
    V4 = V[:, order[:4]]

    result: dict = {"constructs": cols, "gates": {"pooled": GATE_POOLED, "top1": GATE_TOP1}}
    print(f"pass-A scored: {len(scored)} slices, {scored['user_id'].nunique()} users")

    for arm in ["pooled", "top1"]:
        if arm == "top1":
            top = (scored.groupby(["user_id", "condition"]).size()
                   .sort_values(ascending=False).reset_index()
                   .drop_duplicates("user_id").set_index("user_id")["condition"])
            sub = scored[scored["condition"] == scored["user_id"].map(top)]
            gate = GATE_TOP1
        else:
            sub, gate = scored, GATE_POOLED
        arm_res = {}
        for tag, kw in [("raw", {}), ("residualized", {"resid": V4, "std": (mu, sd)})]:
            fr = frames_for(sub, cols, gate, **kw)
            stats = self_vs_stranger(fr["UE"], fr["UL"], rng)
            stats["ceiling_early_oddeven"] = fr["ceiling_early_oddeven"]
            stats["ceiling_late_oddeven"] = fr["ceiling_late_oddeven"]
            arm_res[tag] = stats
            print(f"[{arm}/{tag}] n={stats['n_users']} self={stats['self_mean_abs_cos']} "
                  f"stranger={stats['stranger_mean_abs_cos']} p={stats['p_self_gt_stranger']} "
                  f"ceil_e={stats['ceiling_early_oddeven']} ceil_l={stats['ceiling_late_oddeven']}")
            if arm == "pooled" and tag == "raw":
                best = np.abs(fr["UE"] @ V4)
                rand = rng.standard_normal((N_RANDOM, len(cols)))
                rand /= np.linalg.norm(rand, axis=1, keepdims=True)
                rbest = np.abs(rand @ V4).max(axis=1)
                bm = best.max(axis=1)
                result["alignment_dispersion"] = {
                    "median_best_abs_cos_vs_pop_pc1_4": round(float(np.median(bm)), 4),
                    "q25": round(float(np.percentile(bm, 25)), 4),
                    "q75": round(float(np.percentile(bm, 75)), 4),
                    "share_best_match_pc": [round(float((best.argmax(1) == k).mean()), 3)
                                            for k in range(4)],
                    "random_baseline_median": round(float(np.median(rbest)), 4),
                    "random_baseline_p95": round(float(np.percentile(rbest, 95)), 4)}
        result[arm] = arm_res

    (OUT_DIR / "TGEO_P6_PERSONAL_AXES.json").write_text(json.dumps(result, indent=2))
    md = ["# T-GEO-P6 — personal axes (F10.3, label-free)", "",
          "Leading eigenvector of within-person slice correlation, per user per half.",
          "Self = |cos(u_early, u_late)|; stranger = cyclic-shift derangement pairing;",
          "ceiling = within-half odd/even split; residualized = population top-4 slice-",
          "level frame projected out first (the sharp F10.3 test).", "",
          "| arm | variant | n | self | stranger | p(self>stranger) | ceil early | ceil late |",
          "|---|---|---|---|---|---|---|---|"]
    for arm in ["pooled", "top1"]:
        for tag in ["raw", "residualized"]:
            s = result[arm][tag]
            md.append(f"| {arm} | {tag} | {s['n_users']} | {s['self_mean_abs_cos']} "
                      f"| {s['stranger_mean_abs_cos']} | {s['p_self_gt_stranger']} "
                      f"| {s['ceiling_early_oddeven']} | {s['ceiling_late_oddeven']} |")
    ad = result["alignment_dispersion"]
    md += ["", f"Alignment dispersion (pooled raw): median best |cos| vs population PC1-4 "
           f"= {ad['median_best_abs_cos_vs_pop_pc1_4']} (IQR {ad['q25']}-{ad['q75']}); "
           f"random-direction baseline median {ad['random_baseline_median']} "
           f"(p95 {ad['random_baseline_p95']}); best-match shares PC1..4 = "
           f"{ad['share_best_match_pc']}."]
    (OUT_DIR / "TGEO_P6_PERSONAL_AXES.md").write_text("\n".join(md) + "\n")
    print("written:", OUT_DIR / "TGEO_P6_PERSONAL_AXES.md")


if __name__ == "__main__":
    main()
