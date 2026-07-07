#!/usr/bin/env python
"""OP-32 pilot: individuality as the DISTINCTIVE RESIDUAL (Furr 2008 frame).

User thesis being operationalized: personality is fingerprint-like — no
factor set exhausts a person, but the person is CODABLE; what remains after
subtracting the group is the individuality. Formal frame: Furr (2008,
J Pers 76:1267) — any profile = normative component (population profile)
+ distinctive component; raw profile similarity is inflated by
normativeness. SUICA already met this lesson twice (E6 stranger null,
E9b random-neighbor null); this pilot applies it to the whole 19-construct
battery profile.

Estimands (pre-committed; T1 exploratory, Tier-U, label-free):
  D1 distinctive-signature stability: per-construct z-scoring within half
     removes the normative profile; per-user Pearson r between the early
     and late 19-dim DEVIATION profiles; median across users.
  D2 stranger null: median r between user u's early profile and user v's
     late profile over 200 derangement draws (normative already removed, so
     this should sit ~0; the same-user excess over it = distinctive
     stability, the residual-individuality signal).
  D3 distinctiveness magnitude ||d_u|| (L2 of the z-profile): is HOW
     distinctive a person is itself stable? r(||d_early||, ||d_late||).
  D4 dimensionality-of-residual context (cited, not recomputed): OP-9 M3 —
     the 19-score battery leaves ~32% of embedding-space person signal
     unsubsumed (median CV R^2 0.684) while identification parity holds
     (AUC 0.887 vs 0.891) — the "codable but not exhaustively factorable"
     quantification.

Eligibility: users with >= 6 slices in both halves (the standard OP-5/E9
half-eligible pool). No pass/fail bar: this is a measurement pilot; the
pre-committed reading rule is only directional — D1 must exceed the D2
null band for the residual-individuality claim to survive at T1.
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

from scripts.run_suica_op9_embedding_baseline_v3 import rederive_op5_scores, OP5_KEPT, V3_BATTERY  # noqa: E402
from scripts.suica_v2_lib import score_slices_v2  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
OUT_DIR = ROOT / "results" / "suica_op32_distinctive_residual_pilot_v1"
REPORT = ROOT / "reports" / "suica_op32_distinctive_residual_pilot_v1.md"
SEED = 42
N_DRAWS = 200
CONSTRUCTS = V3_BATTERY + OP5_KEPT


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = pd.read_parquet(TIER_DIR / "op9_half_slices.parquet")
    v3 = score_slices_v2(frame[["user_id", "slice_text"]].assign(half=frame["half"]))
    prof = (v3.groupby(["user_id", "half"])[V3_BATTERY].mean()
            .join(rederive_op5_scores(frame).groupby(["user_id", "half"]).mean()))
    early = prof.xs("early", level="half")
    late = prof.xs("late", level="half")
    common = early.index.intersection(late.index)
    E, L = early.loc[common, CONSTRUCTS], late.loc[common, CONSTRUCTS]
    # remove the normative profile: z per construct within half (Furr)
    Ez = (E - E.mean()) / E.std()
    Lz = (L - L.mean()) / L.std()
    A, B = Ez.to_numpy(), Lz.to_numpy()
    n = len(common)

    def rowcorr(a, b):
        a = a - a.mean(axis=1, keepdims=True)
        b = b - b.mean(axis=1, keepdims=True)
        num = (a * b).sum(1)
        den = np.sqrt((a**2).sum(1) * (b**2).sum(1))
        return np.where(den > 0, num / den, np.nan)

    same = rowcorr(A, B)
    d1 = float(np.nanmedian(same))
    null_meds = []
    for _ in range(N_DRAWS):
        perm = rng.permutation(n)
        perm = np.where(perm == np.arange(n), (perm + 1) % n, perm)
        null_meds.append(float(np.nanmedian(rowcorr(A, B[perm]))))
    d2_med = float(np.median(null_meds))
    d2_hi = float(np.percentile(null_meds, 97.5))
    mag_e = np.sqrt((A**2).sum(1)); mag_l = np.sqrt((B**2).sum(1))
    d3 = float(np.corrcoef(mag_e, mag_l)[0, 1])
    frac_above_null = float(np.mean(same > d2_hi))

    res = {"n_users": int(n), "n_constructs": len(CONSTRUCTS),
           "D1_distinctive_stability_median_r": round(d1, 4),
           "D2_stranger_null_median": round(d2_med, 4),
           "D2_null_97_5pct_of_medians": round(d2_hi, 4),
           "same_minus_null_excess": round(d1 - d2_med, 4),
           "fraction_users_above_null_97_5": round(frac_above_null, 4),
           "D3_distinctiveness_magnitude_retest_r": round(d3, 4),
           "D4_cited_context": {"battery_id_auc": 0.887, "embedding_id_auc": 0.891,
                                "M3_median_cv_r2_embedding_from_battery": 0.684,
                                "unfactored_person_signal_share": "~32% (OP-9 M3)"},
           "reading_rule": "T1 survives iff D1 > D2 null band",
           "verdict_T1": bool(d1 > d2_hi)}
    (OUT_DIR / "op32_pilot_results.json").write_text(json.dumps(res, indent=2) + "\n")
    per_user = pd.DataFrame({"user_id": common, "distinctive_stability_r": same,
                             "magnitude_early": mag_e, "magnitude_late": mag_l})
    per_user.to_csv(OUT_DIR / "op32_per_user.csv", index=False)
    REPORT.write_text("# OP-32 pilot — individuality as the distinctive residual (T1)\n\n"
                      "```json\n" + json.dumps(res, indent=2) + "\n```\n\n"
                      "Frame: Furr (2008) profile = normative + distinctive; z-scoring per\n"
                      "construct removes the normative component, the stranger null guards\n"
                      "against structural inflation (E6/E9b lesson). D1 vs D2 excess is the\n"
                      "measured stability of what remains of a person AFTER the group is\n"
                      "subtracted — the operational form of the fingerprint thesis.\n")
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
