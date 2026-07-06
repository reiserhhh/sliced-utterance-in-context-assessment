#!/usr/bin/env python
"""E11 shuffled-score-fit null geometry (round-7 INCOMPLETE closure).

The v2 permutation calibration (F2) drew 200 RANDOM UNIT DIRECTIONS in the
raw 1024-dim embedding space as the null for marker-axis |cos|. But the
licensed statistic is computed on a FITTED direction (ridge coefficients),
which is confined to the data subspace of the user-embedding matrix — a
subspace that overlaps the semantic marker axes far more than the uniform
sphere does. The geometrically correct null is therefore:

    shuffle construct scores across units -> REFIT the direction with the
    frozen fit_direction machinery -> |cos| with each marker axis.

This script builds that null for both E11 v2 modes (trait: 19 constructs;
state: f1/f3/f5) using a closed-form ridge identical to the frozen
fit_direction (equivalence asserted at cos > 0.999 on real targets before
any null is trusted).

PRE-COMMITTED DECISION RULE (fixed before execution):
  D1 The v2 random-direction bar is DEFECTIVE if (a) the fitted-null 99th
     percentile exceeds the random-direction 99th percentile by > 20% on any
     axis, OR (b) the empirical FPR of the old bar under the fitted null
     exceeds 0.02 per axis-draw (nominal 0.01).
  D2 If defective, the corrected licensing bar is the pooled fitted-null
     99th percentile per axis; V2-2 is recounted with it (CI rule unchanged).
  D3 Standing ruling is unaffected in either outcome: adjective profiles
     remain DESCRIPTIVE aids; this check can only confirm or further
     tighten the licensing bar (G11 family).

Permutation scheme: trait mode rows are one-per-user -> plain permutation is
exact. State mode rows are user-month cells with within-person centering ->
scores are permuted WITHIN user (preserves the user block structure the
centering induces).
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

import scripts.run_suica_e11v2_adjective_projection as e11  # noqa: E402

OUT_DIR = ROOT / "results" / "suica_e11_shuffled_fit_null_v1"
REPORT = ROOT / "reports" / "suica_e11_shuffled_fit_null_v1.md"
V2_TRAIT = ROOT / "results" / "suica_e11v2_adjective_trait"
V2_STATE = ROOT / "results" / "suica_e11v2_adjective_state"
N_PERM = 200
ALPHA = 100.0
SEED = 42


def closed_form_operator(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (Z, A) with Z the frozen standardization of x and A the ridge
    operator so that w = A @ (y - y.mean()) equals fit_direction's Ridge coef."""
    mu, sd = x.mean(axis=0), x.std(axis=0)
    sd = np.where(sd < 1e-12, 1.0, sd)
    z = (x - mu) / sd
    gram = z.T @ z + ALPHA * np.eye(z.shape[1])
    a = np.linalg.solve(gram, z.T)
    return z, a, sd


def assert_equivalence(x, targets, a):
    checked = []
    for name, yv in list(targets.items())[:3]:
        w_frozen = e11.fit_direction(x, yv, np.arange(len(x)), alpha=ALPHA)
        w_closed = a @ (yv - yv.mean())
        w_closed = w_closed / max(1e-12, np.linalg.norm(w_closed))
        cos = float(abs(w_frozen @ w_closed))
        checked.append({"target": name, "cos_frozen_vs_closed": cos})
        if cos <= 0.999:
            raise AssertionError(f"closed-form ridge != frozen fit_direction for {name}: cos={cos}")
    return checked


def parse_axis_cell(cell: str) -> tuple[float, float, float]:
    """'+0.094[-0.11,-0.06]*' style -> (val, lo, hi)."""
    val = float(cell.split("[")[0])
    lo, hi = cell.split("[")[1].split("]")[0].split(",")
    return val, float(lo), float(hi)


def run_mode(mode_state: bool, rng: np.random.Generator) -> dict:
    e11.MODE_STATE = mode_state
    tag = "state" if mode_state else "trait"
    v2_dir = V2_STATE if mode_state else V2_TRAIT
    old = json.loads((v2_dir / "e11v2_results.json").read_text())
    old_thr = old["axis_thresholds_99pct"]
    profiles = pd.read_csv(v2_dir / "e11v2_profiles.csv")

    _, _, _, axes = e11.embed_lexicon()
    x, targets, units, _ = e11.load_targets()
    unit_ids = np.asarray(units)
    z, a, _ = closed_form_operator(x)
    equiv = assert_equivalence(x, targets, a)

    axis_mat = np.stack([axes[d] for d in "EACNO"])  # 5 x dim
    null_by_axis = {d: [] for d in "EACNO"}
    per_target_null = {}
    for name, yv in targets.items():
        draws = np.empty((N_PERM, 5))
        for p in range(N_PERM):
            if mode_state:
                yp = pd.Series(yv).groupby(unit_ids).transform(
                    lambda s: s.sample(frac=1.0, random_state=int(rng.integers(1 << 31))).to_numpy()
                ).to_numpy()
            else:
                yp = rng.permutation(yv)
            w = a @ (yp - yp.mean())
            n = np.linalg.norm(w)
            if n < 1e-12:
                draws[p] = 0.0
                continue
            draws[p] = np.abs(axis_mat @ (w / n))
        per_target_null[name] = draws
        for j, d in enumerate("EACNO"):
            null_by_axis[d].extend(draws[:, j].tolist())

    new_thr = {d: float(np.percentile(null_by_axis[d], 99)) for d in "EACNO"}
    ratio = {d: new_thr[d] / old_thr[d] for d in "EACNO"}
    fpr_old_bar = {d: float(np.mean(np.array(null_by_axis[d]) > old_thr[d])) for d in "EACNO"}
    defective = bool(max(ratio.values()) > 1.20 or max(fpr_old_bar.values()) > 0.02)

    # recount V2-2 under the fitted-null bar (CI rule unchanged, from stored bootstrap CIs)
    recount_rows = []
    for _, r in profiles.iterrows():
        n_sig_old = int(r["n_sig_axes"])
        n_sig_new = 0
        hits = []
        for d in "EACNO":
            val, lo, hi = parse_axis_cell(str(r[f"axis_{d}"]).rstrip("*"))
            sig = abs(val) > new_thr[d] and (lo > 0 or hi < 0)
            n_sig_new += int(sig)
            if sig:
                hits.append(f"{d}{val:+.3f}")
        recount_rows.append({"target": r["target"], "n_sig_axes_old": n_sig_old,
                             "n_sig_axes_fitted_null": n_sig_new, "fitted_null_hits": ";".join(hits)})
    recount = pd.DataFrame(recount_rows)
    sig_targets_new = int((recount["n_sig_axes_fitted_null"] >= 1).sum())

    return {
        "mode": tag, "n_units": int(len(np.unique(unit_ids))), "n_rows": int(len(x)),
        "n_targets": int(len(targets)), "n_perm_per_target": N_PERM,
        "equivalence_check": equiv,
        "old_random_direction_thr_99pct": old_thr,
        "new_shuffled_fit_thr_99pct": new_thr,
        "thr_ratio_new_over_old": ratio,
        "empirical_fpr_of_old_bar_under_fitted_null": fpr_old_bar,
        "old_bar_defective_by_D1": defective,
        "V2_2_sig_targets_old": int(old["V2_2_targets_with_sig_axis"]),
        "V2_2_sig_targets_under_fitted_null": sig_targets_new,
        "per_target_null_99pct_max_axis": {
            name: float(np.percentile(draws.max(axis=1), 99)) for name, draws in per_target_null.items()
        },
        "recount": recount.to_dict(orient="records"),
    }


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = {"trait": run_mode(False, rng), "state": run_mode(True, rng)}
    (OUT_DIR / "shuffled_fit_null_results.json").write_text(
        json.dumps(results, indent=2, default=float) + "\n")

    lines = ["# SUICA E11 shuffled-score-fit null geometry (round-7 closure)", ""]
    for tag, res in results.items():
        lines += [f"## {tag} mode (n_targets={res['n_targets']}, n_perm={res['n_perm_per_target']})", ""]
        lines += ["| axis | old thr (random dir) | new thr (shuffled fit) | ratio | FPR of old bar |",
                  "|---|---|---|---|---|"]
        for d in "EACNO":
            lines.append(
                f"| {d} | {res['old_random_direction_thr_99pct'][d]:.4f} "
                f"| {res['new_shuffled_fit_thr_99pct'][d]:.4f} "
                f"| {res['thr_ratio_new_over_old'][d]:.2f} "
                f"| {res['empirical_fpr_of_old_bar_under_fitted_null'][d]:.4f} |")
        lines += ["", f"- old bar defective by D1: **{res['old_bar_defective_by_D1']}**",
                  f"- V2-2 significant targets: old {res['V2_2_sig_targets_old']} -> "
                  f"fitted-null {res['V2_2_sig_targets_under_fitted_null']}", ""]
        changed = [r for r in res["recount"] if r["n_sig_axes_old"] != r["n_sig_axes_fitted_null"]]
        if changed:
            lines += ["Recount changes:"] + [
                f"- {r['target']}: {r['n_sig_axes_old']} -> {r['n_sig_axes_fitted_null']} ({r['fitted_null_hits'] or 'none'})"
                for r in changed] + [""]
    REPORT.write_text("\n".join(lines) + "\n")
    for tag, res in results.items():
        print(f"[{tag}] defective={res['old_bar_defective_by_D1']} "
              f"ratios={ {d: round(res['thr_ratio_new_over_old'][d], 2) for d in 'EACNO'} } "
              f"V2-2 {res['V2_2_sig_targets_old']} -> {res['V2_2_sig_targets_under_fitted_null']}")


if __name__ == "__main__":
    main()
