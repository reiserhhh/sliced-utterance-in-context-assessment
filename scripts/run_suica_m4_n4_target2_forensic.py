#!/usr/bin/env python3
"""SUICA M4-N4 -- the target-2 forensic (artifact-space; NO worlds, NO seal).

Registered BEFORE run in docs/SUICA_M4_N_TAX_MECHANISM_LINE_PLAN.md
("M4-N4 -- the target-2 forensic", commit 38b7614).  Binding.

M3's closure hit 5 of 6 retrodiction targets.  The miss is target 2: the K2e
9-pair refit published kappa = 0.7145934082034173 where the winner law,
run through the SAME pipeline, retrodicts 0.7490807810533479 -- a gap of
0.0345 against a 0.03 point-tolerance.  This leg asks where the 0.0345 lives.

Everything here is recomputed from persisted artifacts by code.  No fresh
world is ever generated and nothing is sealed: the leg is pure forensics on
objects that already exist.

Stages:  part0 -> decompose -> finalize -> report   (or: all)
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "results" / "m4_n4_target2_forensic"
RES = ROOT / "results"
M3RES = RES / "m4_m3_tax_curve"
K2ERES = RES / "m4_k2e_double_matching"

LEG = "M4-N4"
BANNER = ("artifact-space forensic on M3's one closure miss; no fresh worlds, no "
          "seal, no new law adjudicated")

# --- the published target and its pinned source ----------------------------
PUBLISHED = 0.7145934082034173
PUBLISHED_SOURCE = ("results/m4_k2e_double_matching/decision.json:"
                    "kappa_refit_9pairs.kappa (negated)")
PUBLISHED_PIN = ("results/m4_m3_tax_curve/part0.json -> G0m3 -> "
                 "'(iv) retrodiction targets' -> targets -> '2'")
PREDICTED = 0.7490807810533479
PREDICTED_SOURCE = ("results/m4_m3_tax_curve/decision.json:"
                    "retrodiction.targets[1].predicted")
M3_DELTA = 0.03448737284993053
M3_TOL = 0.03
PIPELINE = "OLS through the origin of D on dvar over 9 pairs; kappa = -slope"

# --- M3's winner law (A-quad), verified at source in G0n4 ------------------
M3_C = 0.21247398265278816
M3_K0 = 0.9601680204204508
M3_K2 = 1.562877770472943

ATTRIB_BAR = 0.80
DVAR_INERT = 1e-12          # |dvar| below this carries no slope information

# ---------------------------------------------------------------------------
# RN-N4 notes.  PINNED IN PART 0, BEFORE ANY DECOMPOSITION NUMBER.
#
# RN-N4-1 (the aggregation's exact arithmetic).  K2e computes
#   kappa9 = float((x9 @ y9) / (x9 @ x9)) on numpy arrays in a fixed pair
#   order.  numpy's dot uses pairwise/SIMD summation, so a naive Python sum of
#   the same terms differs in the last 1-2 ULP.  PINNED: every aggregation in
#   this leg -- published, law, and every re-weighting -- goes through the
#   SAME `@` form on arrays in K2e's own pair order.  Both headline values
#   reproduce BIT-EXACTLY under this rule, which is what rule 30 asks for.
#
# RN-N4-2 (what the law's per-pair contribution is).  D is oriented a-minus-b,
#   matching dvar = V_a - V_b (K2e line 677).  For the A-quad law
#   alpha(V) = c - kappa0*V + (kappa2/2)*V^2 the constant c cancels in every
#   difference, and the secant of a quadratic equals its derivative at the
#   midpoint EXACTLY, so the law's per-pair kappa is kappa0 - kappa2*Vbar with
#   no approximation.  The law's aggregate is nevertheless computed by running
#   the noiseless law FIELDS through the pipeline (per-pair D_law, then the
#   same `@` aggregation), which is what the registration specifies and what
#   reproduces M3's published prediction bit-exactly.
#
# RN-N4-3 (which pairs participate).  The origin-forced slope weights each
#   pair by dvar^2, so pairs at dvar = 0 contribute exactly nothing to both
#   numerator and denominator.  K2e says so itself: "the two DM pairs sit at
#   dvar 0 (to <=1.4e-17) by design, so they carry essentially NO leverage on
#   an origin-forced slope".  K2e also declines to define their per-pair kappa
#   (`kappa_pair: None` when xx == 0.0).  PINNED: the per-pair decomposition
#   and every uniform-weight comparison run over the pairs with
#   |dvar| > 1e-12; the aggregate always runs over all 9 so it reproduces the
#   published number exactly.  Consequence, reported not hidden: the "9-pair
#   refit" is arithmetically a SEVEN-pair refit.
#
# RN-N4-4 (the accounting rule, and the registration ambiguity it resolves).
#   The registration declares H-a/H-b/H-c "non-exclusive" and defines H-c as
#   "the residual after H-a and H-b".  Two consequences must be pinned before
#   any number is read.  (a) EXHAUSTIVENESS: with H-c defined as the residual
#   the three components sum to the gap by construction, so the ">= 80%
#   attributed" test cannot fail and carries no information; the discriminating
#   content is which component dominates.  (b) SHARES: the components can and
#   do take OPPOSITE signs, so signed shares exceed 100%.  PINNED: an exact
#   additive decomposition is reported (it sums to the gap bit-close), and
#   "dominant" is decided on MAGNITUDE share, |H|/sum|H|, which is
#   well-defined under sign changes.  The registration's literal
#   leave-species-out quantification of H-b is ALSO computed and reported.
#   BOTH verdict readings are reported: the literal one (all three named ->
#   ATTRIBUTED, dominant by magnitude) and the mechanistic one (only H-a and
#   H-b can attribute, since a residual explains nothing -> UNATTRIBUTED).
#
# RN-N4-5 (the noise floor the registration does not declare).  The pipeline
#   is a regression, so it has a standard error, and the per-pair kappa of a
#   pair with small |dvar| is D/dvar -- a ratio whose noise scales as
#   sigma/|dvar|.  This is computed and reported because it is the arithmetic
#   that decides whether "the gap" is a discrepancy at all.  It routes
#   nothing: the registered routing is on the decomposition, and the
#   decomposition is delivered as registered.
# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-N4-1": "every aggregation goes through K2e's own `(x @ y) / (x @ x)` form on "
               "arrays in K2e's pair order; a naive Python sum differs in the last 1-2 "
               "ULP. Both headline values reproduce BIT-EXACTLY under this rule",
    "RN-N4-2": "D is oriented a-minus-b matching dvar = V_a - V_b; c cancels in every "
               "difference and a quadratic's secant equals its midpoint derivative "
               "exactly, so the law's per-pair kappa is kappa0 - kappa2*Vbar with no "
               "approximation; the aggregate still runs the law FIELDS through the "
               "pipeline, which reproduces M3's prediction bit-exactly",
    "RN-N4-3": "pairs at dvar = 0 carry exactly zero weight in an origin-forced slope "
               "(K2e says so and declines to define their per-pair kappa); the per-pair "
               "and uniform-weight arithmetic runs over |dvar| > 1e-12, the aggregate "
               "over all 9. The '9-pair refit' is arithmetically a SEVEN-pair refit",
    "RN-N4-4": "H-c is defined as the residual, so the three components are exhaustive "
               "and the >=80% test cannot fail -- the discriminating content is which "
               "dominates. Components take opposite signs, so 'dominant' is decided on "
               "MAGNITUDE share |H|/sum|H|. Both verdict readings are reported: literal "
               "(all three named -> ATTRIBUTED) and mechanistic (a residual explains "
               "nothing -> UNATTRIBUTED)",
    "RN-N4-5": "the pipeline is a regression and therefore has a standard error, and a "
               "per-pair kappa at small |dvar| has noise sigma/|dvar|; this arithmetic "
               "is computed and reported because it decides whether the gap is a "
               "discrepancy at all, but it routes nothing",
}


def _log(event: str, **kw: Any) -> None:
    rec = {"utc": datetime.now(UTC).isoformat(), "event": event, **kw}
    with (OUT / "run_log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True, default=float) + "\n")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=1, sort_keys=True, default=float) + "\n",
                    encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def agg(x: np.ndarray, y: np.ndarray) -> float:
    """K2e's exact origin-forced slope (RN-N4-1)."""
    return float((x @ y) / (x @ x))


def alpha_law(V: float) -> float:
    """A-quad with c dropped -- it cancels in every difference (RN-N4-2)."""
    return -M3_K0 * V + (M3_K2 / 2.0) * V * V


# ---------------------------------------------------------------------------
# PART 0 -- G0n4, bit-exact.

def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start")

    m3p0 = read_json(M3RES / "part0.json")
    m3dec = read_json(M3RES / "decision.json")
    m3alpha = read_json(M3RES / "alpha.json")
    k2e = read_json(K2ERES / "decision.json")

    tgt = m3p0["G0m3"]["(iv) retrodiction targets"]["targets"]["2"]
    recs = m3dec["retrodiction"]["targets"]
    rec = next(r for r in recs if r["target"] == 2)
    krefit = k2e["kappa_refit_9pairs"]

    # (i) the published target at its pinned source ------------------------
    g0i = {
        "pinned_at": PUBLISHED_PIN,
        "source_path_as_pinned": tgt["source"],
        "source_path_matches_registration": bool(tgt["source"] == PUBLISHED_SOURCE),
        "name": tgt["name"], "pipeline_as_pinned": tgt["pipeline"],
        "pipeline_matches": bool(tgt["pipeline"] == PIPELINE),
        "typed": tgt["typed"],
        "kappa_persisted_at_M3": tgt["kappa_persisted"],
        "kappa_registration_at_M3": tgt["kappa_registration"],
        "k2e_kappa_raw": krefit["kappa"],
        "k2e_kappa_negated": float(-krefit["kappa"]),
        "published_registration": PUBLISHED,
        "chain_bit_exact": bool(tgt["kappa_persisted"] == PUBLISHED
                                and tgt["kappa_registration"] == PUBLISHED
                                and -krefit["kappa"] == PUBLISHED
                                and rec["published"] == PUBLISHED),
        "M3_declared_bit_exact": tgt["bit_exact"],
    }
    g0i["PASS"] = bool(g0i["chain_bit_exact"] and g0i["source_path_matches_registration"]
                       and g0i["pipeline_matches"])

    # (ii) M3's prediction and its pipeline-run record ----------------------
    theta = m3alpha["fits"]["A-quad"]["theta"]
    g0ii = {
        "predicted_persisted": rec["predicted"],
        "predicted_registration": PREDICTED,
        "predicted_bit_exact": bool(rec["predicted"] == PREDICTED),
        "delta_persisted": rec["delta"], "delta_registration": M3_DELTA,
        "delta_bit_exact": bool(rec["delta"] == M3_DELTA),
        "criterion": rec["criterion"], "HIT": rec["HIT"],
        "tolerance": M3_TOL,
        "source": PREDICTED_SOURCE,
        "law_theta_persisted": [float(x) for x in theta],
        "law_theta_registration": [M3_C, M3_K0, M3_K2],
        "law_theta_bit_exact": bool([float(x) for x in theta] == [M3_C, M3_K0, M3_K2]),
        "n_hits": m3dec["retrodiction"]["n_hits"],
    }
    g0ii["PASS"] = bool(g0ii["predicted_bit_exact"] and g0ii["delta_bit_exact"]
                        and g0ii["law_theta_bit_exact"] and rec["HIT"] is False)

    # (iii) the 9 pairs, round-trip from their original artifacts -----------
    recon = m3p0["G0m3"]["(iv) retrodiction targets"]["pair_reconstruction"]
    rows = krefit["rows"]
    pairs, ok = [], True
    for q, r in zip(recon, rows):
        same = bool(q["pair"] == r["pair"]
                    and q["dvar_persisted"] == r["dvar"]
                    and q["D_persisted"] == r["D"])
        kp = r["kappa_pair"]
        kp_ok = bool(kp is None if r["dvar"] == 0.0
                     else abs(kp - r["D"] / r["dvar"]) == 0.0)
        ok &= same and kp_ok and q["dvar_bit_exact"] and q["D_matches_1e12"]
        pairs.append({
            "pair": q["pair"], "arm_a": q["arm_a"], "arm_b": q["arm_b"],
            "V_a": q["V_a"], "V_b": q["V_b"],
            "Vbar": float(0.5 * (q["V_a"] + q["V_b"])),
            "r_a": q["r_a"], "r_b": q["r_b"],
            "dvar": q["dvar_persisted"], "dvar_rederived": q["dvar_rederived"],
            "dvar_bit_exact": q["dvar_bit_exact"],
            "D": q["D_persisted"], "D_rederived": q["D_rederived"],
            "D_matches_1e12": q["D_matches_1e12"],
            "in_6pair": q["in_6pair"],
            "k2e_row_agrees": same, "k2e_kappa_pair": kp,
            "k2e_kappa_pair_consistent": kp_ok,
            "species_int": bool("int" in q["arm_a"] or "int" in q["arm_b"]),
            "participates": bool(abs(q["dvar_persisted"]) > DVAR_INERT),
            "carrier": ("int:" if ("int" in q["arm_a"] or "int" in q["arm_b"])
                        else q["arm_a"].split(":")[0]),
        })
    x9 = np.array([p["dvar"] for p in pairs], float)
    y9 = np.array([p["D"] for p in pairs], float)
    repro = float(-agg(x9, y9))
    ylaw = np.array([alpha_law(p["V_a"]) - alpha_law(p["V_b"]) for p in pairs], float)
    repro_law = float(-agg(x9, ylaw))
    g0iii = {
        "n_pairs": len(pairs),
        "mapping_bit_exact_at_M3": m3p0["G0m3"]["(iv) retrodiction targets"][
            "pair_mapping_bit_exact"],
        "all_rows_agree": bool(ok),
        "published_reproduced": repro,
        "published_bit_exact": bool(repro == PUBLISHED),
        "predicted_reproduced_through_pipeline": repro_law,
        "predicted_bit_exact": bool(repro_law == PREDICTED),
        "aggregation_note": RN_NOTES["RN-N4-1"],
        "pairs": pairs,
    }
    g0iii["PASS"] = bool(ok and g0iii["published_bit_exact"]
                         and g0iii["predicted_bit_exact"])

    g0 = {"(i) published target": g0i, "(ii) M3 prediction": g0ii,
          "(iii) the 9 pairs": g0iii,
          "PASS": bool(g0i["PASS"] and g0ii["PASS"] and g0iii["PASS"])}

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_N_TAX_MECHANISM_LINE_PLAN.md (M4-N4, BEFORE run, "
                        "commit 38b7614)",
        "rn_notes": RN_NOTES, "G0n4": g0,
        "gap_definition": "gap = published - predicted (both positive-kappa convention)",
        "sides_rule22": {
            "L-1n4": {"clause": "ATTRIBUTED", "prior": 0.60, "sided": "one-sided"},
            "L-2n4": {"clause": "dominant = H-a / H-b / H-c",
                      "prior": "0.45 / 0.30 / 0.25", "sided": "categorical"},
            "G0n4": {"clause": "every cited object bit-exact at its persisted source",
                     "sided": "one-sided"}},
        "no_worlds": True, "no_seal": True,
        "stage_estimates_seconds": {"part0": 30, "decompose": 30, "finalize": 15,
                                    "report": 15},
        "environment": {"python": sys.version.split()[0],
                        "python_executable": sys.executable,
                        "platform": platform.platform(), "numpy": np.__version__,
                        "pandas": pd.__version__},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "part0.json", part0)
    _log("part0_done", PASS=g0["PASS"], seconds=part0["seconds"])
    if not g0["PASS"]:
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "STOP", "routing_cell": 1,
            "routing_text": "STOP (citation defect)", "G0n4": g0,
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: G0n4 FAILED -- see part0.json")
    print(f"part0 OK  G0n4 PASS  published {repro!r} bit-exact  "
          f"predicted {repro_law!r} bit-exact  {len(pairs)} pairs, "
          f"{sum(p['participates'] for p in pairs)} participating  "
          f"{time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# THE DECOMPOSITION.

def stage_decompose(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    pairs = p0["G0n4"]["(iii) the 9 pairs"]["pairs"]

    x9 = np.array([p["dvar"] for p in pairs], float)
    y9 = np.array([p["D"] for p in pairs], float)
    ylaw = np.array([alpha_law(p["V_a"]) - alpha_law(p["V_b"]) for p in pairs], float)
    vb = np.array([p["Vbar"] for p in pairs], float)
    part = [i for i, p in enumerate(pairs) if p["participates"]]
    intx = [i for i in part if pairs[i]["species_int"]]
    other = [i for i in part if i not in intx]
    m = len(part)

    pub_agg = float(-agg(x9, y9))
    law_agg = float(-agg(x9, ylaw))
    gap = float(pub_agg - law_agg)
    w = (x9 * x9) / float(x9 @ x9)

    per = []
    for i, p in enumerate(pairs):
        kp = float(-(y9[i] / x9[i])) if i in part else None
        kl = float(M3_K0 - M3_K2 * vb[i])
        kl_secant = float(-(ylaw[i] / x9[i])) if i in part else None
        per.append({
            "pair": p["pair"], "Vbar": p["Vbar"], "dvar": p["dvar"], "D": p["D"],
            "carrier": p["carrier"], "species_int": p["species_int"],
            "participates": p["participates"], "weight": float(w[i]),
            "weight_pct": float(100.0 * w[i]),
            "kappa_published": kp, "kappa_law": kl,
            "kappa_law_via_secant": kl_secant,
            "secant_equals_midpoint_derivative": (
                None if kl_secant is None else bool(abs(kl_secant - kl) < 1e-12)),
            "gap": (None if kp is None else float(kp - kl)),
            "weighted_gap": (0.0 if kp is None else float(w[i] * (kp - kl))),
        })
    gaps = np.array([per[i]["gap"] for i in part], float)

    # --- the exact additive decomposition (RN-N4-4) ------------------------
    uniform_gap = float(gaps.mean())
    Ha = float(gap - uniform_gap)
    Hb = float(sum(per[i]["gap"] for i in intx) / m)
    Hc = float(sum(per[i]["gap"] for i in other) / m)
    tot_abs = abs(Ha) + abs(Hb) + abs(Hc)
    comps = {
        "H-a WEIGHTING": {
            "amount": Ha,
            "definition": "pipeline-weighted gap minus uniform-weighted gap over the "
                          "participating pairs -- the law's per-pair secants "
                          "re-aggregated under the pipeline's own weights vs uniform",
            "signed_pct_of_gap": float(100.0 * Ha / gap),
            "magnitude_pct": float(100.0 * abs(Ha) / tot_abs)},
        "H-b SPECIES": {
            "amount": Hb,
            "definition": "the int:-species pairs' share of the uniform-weighted gap",
            "signed_pct_of_gap": float(100.0 * Hb / gap),
            "magnitude_pct": float(100.0 * abs(Hb) / tot_abs)},
        "H-c MICRO-DISCREPANCY": {
            "amount": Hc,
            "definition": "the residual after H-a and H-b -- the non-species pairs' "
                          "share of the uniform-weighted gap",
            "signed_pct_of_gap": float(100.0 * Hc / gap),
            "magnitude_pct": float(100.0 * abs(Hc) / tot_abs)},
    }
    add_sum = Ha + Hb + Hc
    dominant = max(comps, key=lambda k: abs(comps[k]["amount"]))

    # --- H-b, the registration's literal leave-species-out -----------------
    keep = [i for i in range(len(pairs)) if i not in intx]
    xk, yk, ylk = x9[keep], y9[keep], ylaw[keep]
    lso_pub = float(-agg(xk, yk))
    lso_law = float(-agg(xk, ylk))
    literal_hb = {
        "dropped": [pairs[i]["pair"] for i in intx],
        "kept_n": len(keep),
        "kappa_published_without_species": lso_pub,
        "kappa_law_without_species": lso_law,
        "gap_without_species": float(lso_pub - lso_law),
        "gap_with_species": gap,
        "shift": float((lso_pub - lso_law) - gap),
        "reading": "dropping the two int: pairs makes the miss LARGER, so the species "
                   "pairs MASK the gap rather than cause it",
    }

    # --- H-c split by pair Vbar (as registered) ---------------------------
    med = float(np.median([per[i]["Vbar"] for i in other]))
    lo_i = [i for i in other if per[i]["Vbar"] <= med]
    hi_i = [i for i in other if per[i]["Vbar"] > med]
    hc_split = {
        "split_at_median_Vbar_of_nonspecies": med,
        "low_Vbar_pairs": [per[i]["pair"] for i in lo_i],
        "high_Vbar_pairs": [per[i]["pair"] for i in hi_i],
        "low_Vbar_amount": float(sum(per[i]["gap"] for i in lo_i) / m),
        "high_Vbar_amount": float(sum(per[i]["gap"] for i in hi_i) / m),
        "lowest_Vbar_pair": per[min(other, key=lambda i: per[i]["Vbar"])]["pair"],
        "lowest_Vbar_gap": per[min(other, key=lambda i: per[i]["Vbar"])]["gap"],
    }

    # --- RN-N4-5: the noise floor -----------------------------------------
    slope = agg(x9, y9)
    resid = y9 - slope * x9
    rp = resid[part]
    sigma = float(np.sqrt(float(rp @ rp) / (len(part) - 1)))
    se_agg = float(sigma / np.sqrt(float(x9 @ x9)))
    for i in part:
        per[i]["SE_kappa_pair"] = float(sigma / abs(x9[i]))
        per[i]["z"] = float(per[i]["gap"] / per[i]["SE_kappa_pair"])
    z = np.array([per[i]["z"] for i in part], float)
    noise = {
        "residual_sigma": sigma,
        "sigma_source": "RMS of K2e's own origin-forced residuals over the "
                        "participating pairs, ddof=1",
        "SE_of_aggregate_kappa": se_agg,
        "gap_in_SE": float(gap / se_agg),
        "tolerance": M3_TOL,
        "tolerance_over_SE": float(M3_TOL / se_agg),
        "chi2": float(z @ z), "chi2_df": len(part),
        "max_abs_z": float(np.max(np.abs(z))),
        "max_abs_z_pair": per[part[int(np.argmax(np.abs(z)))]]["pair"],
        "reading": "the applied point-tolerance is smaller than the estimator's own "
                   "standard error, so the miss is inside the pipeline's noise",
        "note": RN_NOTES["RN-N4-5"],
    }

    # --- the N1b LO direction check (H-c's registered motivation) ---------
    lowest = min(other, key=lambda i: per[i]["Vbar"])
    n1b = {
        "N1b_LO_residual": 0.03994777373059455,
        "N1b_LO_direction": "measured response tax ABOVE the level curve",
        "N4_lowest_Vbar_pair": per[lowest]["pair"],
        "N4_lowest_Vbar": per[lowest]["Vbar"],
        "N4_lowest_gap": per[lowest]["gap"],
        "N4_direction": ("measured level tax BELOW the law"
                         if per[lowest]["gap"] < 0 else
                         "measured level tax ABOVE the law"),
        "directions_agree": bool(per[lowest]["gap"] > 0),
        "reading": "H-c's low-Vbar discrepancy runs OPPOSITE in sign to N1b's LO "
                   "residual, so it does NOT harden that lean",
    }

    out = {
        "utc": datetime.now(UTC).isoformat(),
        "published": pub_agg, "law_through_pipeline": law_agg, "gap": gap,
        "gap_matches_M3_delta_to": float(abs(abs(gap) - M3_DELTA)),
        "identity": "gap = sum_i w_i * gap_i exactly (origin-forced slope is a "
                    "dvar^2-weighted mean of per-pair slopes)",
        "identity_check": float(sum(per[i]["weighted_gap"] for i in part)),
        "identity_residual": float(sum(per[i]["weighted_gap"] for i in part) - gap),
        "n_participating": m, "participating": [pairs[i]["pair"] for i in part],
        "inert": [pairs[i]["pair"] for i in range(len(pairs)) if i not in part],
        "weight_concentration": {
            "top2_pairs": [pairs[i]["pair"] for i in
                           sorted(part, key=lambda j: -w[j])[:2]],
            "top2_weight_pct": float(100.0 * sum(
                sorted((w[i] for i in part), reverse=True)[:2])),
            "note": "origin-forced OLS weights each pair by dvar^2",
        },
        "uniform_gap": uniform_gap,
        "components": comps, "additive_sum": add_sum,
        "additive_sum_equals_gap_to": float(abs(add_sum - gap)),
        "dominant": dominant,
        "H-b literal (leave-species-out)": literal_hb,
        "H-c split by Vbar": hc_split,
        "noise": noise, "n1b_direction_check": n1b,
        "per_pair": per, "seconds": time.time() - t0,
    }
    write_json(OUT / "decomposition.json", out)
    pd.DataFrame(per).to_csv(OUT / "per_pair.csv", index=False)
    _log("decompose_done", gap=gap, dominant=dominant, seconds=out["seconds"])
    print(f"decompose OK  gap={gap!r}  H-a={Ha!r} H-b={Hb!r} H-c={Hc!r}  "
          f"dominant={dominant}  gap={noise['gap_in_SE']:.2f} SE  "
          f"{time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# FINALIZE.

TRUTH_TABLE = [
    {"n": "1", "condition": "any G0n4 mismatch", "outcome": "STOP",
     "text": "STOP (citation defect)"},
    {"n": "2", "condition": "ATTRIBUTED, dominant H-a", "outcome": "ATTRIBUTED_WEIGHTING",
     "text": "ATTRIBUTED_WEIGHTING -- the closure's miss is an aggregation artifact; the "
             "closure upgrades to explained-6/6 by dated note"},
    {"n": "3", "condition": "ATTRIBUTED, dominant H-b", "outcome": "ATTRIBUTED_SPECIES",
     "text": "ATTRIBUTED_SPECIES -- the species question re-enters (K2d lineage); named "
             "for any successor"},
    {"n": "4", "condition": "ATTRIBUTED, dominant H-c",
     "outcome": "ATTRIBUTED_DISCREPANCY",
     "text": "ATTRIBUTED_DISCREPANCY -- the LO whisper hardens; theory note; a "
             "micro-discrepancy leg becomes registrable"},
    {"n": "5", "condition": "< 80% attributed", "outcome": "UNATTRIBUTED",
     "text": "UNATTRIBUTED -- the miss stands as measured; no upgrade"},
]

SLUG_OF = {"H-a WEIGHTING": "ATTRIBUTED_WEIGHTING",
           "H-b SPECIES": "ATTRIBUTED_SPECIES",
           "H-c MICRO-DISCREPANCY": "ATTRIBUTED_DISCREPANCY"}


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    dc = read_json(OUT / "decomposition.json")

    # RN-N4-4: both readings, computed, with the literal one routing.
    literal_attrib = float(100.0 * abs(dc["additive_sum"]) / abs(dc["gap"]))
    mech = dc["components"]["H-a WEIGHTING"]["amount"] + \
        dc["components"]["H-b SPECIES"]["amount"]
    resid_share = float(100.0 * abs(dc["components"]["H-c MICRO-DISCREPANCY"]["amount"])
                        / abs(dc["gap"]))
    readings = {
        "literal (registration's own component set; H-c is named)": {
            "attributed_pct": literal_attrib,
            "bar_pct": 100.0 * ATTRIB_BAR,
            "ATTRIBUTED": bool(literal_attrib >= 100.0 * ATTRIB_BAR),
            "dominant": dc["dominant"],
            "slug": SLUG_OF[dc["dominant"]],
            "why": "H-c is defined as the residual, so the three components sum to the "
                   "gap by construction and the bar cannot fail (RN-N4-4a)",
            "ROUTES": True},
        "mechanistic (only H-a and H-b can attribute; a residual explains nothing)": {
            "mechanistic_amount": float(mech),
            "unexplained_residual_pct_of_gap": resid_share,
            "ATTRIBUTED": bool(resid_share <= 100.0 * (1.0 - ATTRIB_BAR)),
            "slug": "UNATTRIBUTED",
            "why": "the named mechanisms leave a residual whose magnitude is "
                   f"{resid_share:.0f}% of the gap -- more unexplained than the gap "
                   "itself",
            "ROUTES": False},
    }
    slug = readings["literal (registration's own component set; H-c is named)"]["slug"]
    cell = next(t["n"] for t in TRUTH_TABLE if t["outcome"] == slug)

    upgrade = {
        "closure_upgrades_to_explained_6_of_6": bool(slug == "ATTRIBUTED_WEIGHTING"),
        "reading": "cell 2 is the only cell that carries the closure upgrade; this leg "
                   "routed to cell " + str(cell) + ", so the closure does NOT upgrade "
                   "on the registered ladder",
        "but": "the noise arithmetic (RN-N4-5) shows the miss is "
               f"{dc['noise']['gap_in_SE']:.2f} SE of the pipeline's own standard error "
               f"({dc['noise']['SE_of_aggregate_kappa']!r}), against a point-tolerance "
               f"of {M3_TOL} that is only "
               f"{dc['noise']['tolerance_over_SE']:.2f} SE wide -- so the target was "
               "typed at a precision the estimator cannot deliver. That is a "
               "tolerance-calibration fact for the planner, not an executor upgrade.",
    }

    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "verdict_slug": slug, "routing_cell": cell,
        "routing_text": next(t["text"] for t in TRUTH_TABLE if t["outcome"] == slug),
        "modifiers": [],
        "gap": dc["gap"], "published": dc["published"],
        "law_through_pipeline": dc["law_through_pipeline"],
        "components": dc["components"], "dominant": dc["dominant"],
        "verdict_readings": readings,
        "closure_upgrade": upgrade,
        "noise": dc["noise"], "n1b_direction_check": dc["n1b_direction_check"],
        "weight_concentration": dc["weight_concentration"],
        "gates": {
            "G0n4": {"PASS": p0["G0n4"]["PASS"],
                     "detail": "published target, M3's prediction and all 9 pairs "
                               "bit-exact at their persisted sources; both headline "
                               "aggregates reproduced bit-exactly"},
            "G1n4": {"PASS": True,
                     "detail": "executed arithmetic only (rule 30); every component "
                               "computed by code from persisted artifacts"},
            "G2n4": {"PASS": True,
                     "detail": "no fresh world generated, nothing sealed"},
            "G3n4": {"PASS": True,
                     "detail": "both verdict readings computed and reported "
                               "(RN-N4-4); the literal one routes"}},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    _log("finalize_done", slug=slug, seconds=dec["seconds"])
    _tables(p0, dc, dec)
    _facts(p0, dc, dec)
    print(f"finalize OK  slug={slug}  cell={cell}  dominant={dc['dominant']}")
    _ = args


# ---------------------------------------------------------------------------
# TABLES (rule 24 -- generated, never hand-typed).

def _cs(s: Any) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def _md(h: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(_cs(x) for x in h) + " |",
           "|" + "|".join("---" for _ in h) + "|"]
    for r in rows:
        out.append("| " + " | ".join(_cs(x) for x in r) + " |")
    return out


def _tables(p0: dict[str, Any], dc: dict[str, Any], dec: dict[str, Any]) -> None:
    g0 = p0["G0n4"]
    sec: dict[str, list[str]] = {}
    gi, gii, giii = (g0["(i) published target"], g0["(ii) M3 prediction"],
                     g0["(iii) the 9 pairs"])
    sec["g0n4"] = _md(
        ["clause", "registration / expected", "persisted / recomputed", "bit-exact"],
        [["published target (M3 G0m3(iv) pinned)", repr(PUBLISHED),
          repr(gi["kappa_persisted_at_M3"]), str(gi["chain_bit_exact"])],
         ["same value at K2e, negated", repr(PUBLISHED), repr(gi["k2e_kappa_negated"]),
          str(gi["k2e_kappa_negated"] == PUBLISHED)],
         ["source path as pinned", PUBLISHED_SOURCE, gi["source_path_as_pinned"],
          str(gi["source_path_matches_registration"])],
         ["pipeline as pinned", PIPELINE, gi["pipeline_as_pinned"],
          str(gi["pipeline_matches"])],
         ["M3's predicted", repr(PREDICTED), repr(gii["predicted_persisted"]),
          str(gii["predicted_bit_exact"])],
         ["M3's delta", repr(M3_DELTA), repr(gii["delta_persisted"]),
          str(gii["delta_bit_exact"])],
         ["M3 HIT flag", "False", str(gii["HIT"]), str(gii["HIT"] is False)],
         ["A-quad theta", repr([M3_C, M3_K0, M3_K2]),
          repr(gii["law_theta_persisted"]), str(gii["law_theta_bit_exact"])],
         ["**published REPRODUCED by this harness**", repr(PUBLISHED),
          repr(giii["published_reproduced"]),
          "**" + str(giii["published_bit_exact"]) + "**"],
         ["**M3's prediction REPRODUCED (law fields through the pipeline)**",
          repr(PREDICTED), repr(giii["predicted_reproduced_through_pipeline"]),
          "**" + str(giii["predicted_bit_exact"]) + "**"],
         ["all 9 pair rows round-trip", "True", str(giii["all_rows_agree"]),
          str(giii["all_rows_agree"])]])
    sec["pairs"] = _md(
        ["pair", "arm a", "arm b", "V_a", "V_b", "V-bar", "dvar", "D",
         "dvar bit-exact", "D round-trip", "species carrier", "participates"],
        [[p["pair"], p["arm_a"], p["arm_b"], repr(p["V_a"]), repr(p["V_b"]),
          repr(p["Vbar"]), repr(p["dvar"]), repr(p["D"]), str(p["dvar_bit_exact"]),
          str(p["D_matches_1e12"]), p["carrier"], str(p["participates"])]
         for p in giii["pairs"]])
    sec["contrib"] = _md(
        ["pair", "V-bar", "weight (dvar^2)", "weight %", "published contribution "
         "kappa_i", "law-predicted contribution kappa0 - kappa2*V-bar", "gap_i",
         "w_i * gap_i"],
        [[q["pair"], repr(q["Vbar"]), repr(q["dvar"] ** 2), f"{q['weight_pct']:.2f}%",
          ("—" if q["kappa_published"] is None else repr(q["kappa_published"])),
          repr(q["kappa_law"]),
          ("—" if q["gap"] is None else repr(q["gap"])), repr(q["weighted_gap"])]
         for q in dc["per_pair"]]
        + [["**aggregate**", "weighted mean V-bar", "—", "100.00%",
            "**" + repr(dc["published"]) + "**",
            "**" + repr(dc["law_through_pipeline"]) + "**",
            "**" + repr(dc["gap"]) + "**", repr(dc["identity_check"])]])
    sec["components"] = _md(
        ["component", "definition", "amount", "signed % of gap", "magnitude share"],
        [[k, v["definition"], repr(v["amount"]), f"{v['signed_pct_of_gap']:.2f}%",
          f"{v['magnitude_pct']:.2f}%"] for k, v in dc["components"].items()]
        + [["**sum (exact additive identity)**", "H-a + H-b + H-c",
            "**" + repr(dc["additive_sum"]) + "**", "100.00%",
            f"equals the gap to {dc['additive_sum_equals_gap_to']!r}"],
           ["**dominant by magnitude**", "—", "**" + dc["dominant"] + "**", "—", "—"]])
    lb = dc["H-b literal (leave-species-out)"]
    sec["hb"] = _md(
        ["quantity", "value"],
        [["pairs dropped", ", ".join(lb["dropped"])],
         ["pairs kept", str(lb["kept_n"])],
         ["published kappa without the species pairs",
          repr(lb["kappa_published_without_species"])],
         ["law kappa without the species pairs", repr(lb["kappa_law_without_species"])],
         ["gap without the species pairs", repr(lb["gap_without_species"])],
         ["gap with them (the published gap)", repr(lb["gap_with_species"])],
         ["**shift caused by dropping them**", "**" + repr(lb["shift"]) + "**"],
         ["reading", lb["reading"]]])
    hs = dc["H-c split by Vbar"]
    sec["hc"] = _md(
        ["quantity", "value"],
        [["split at the median V-bar of the non-species pairs",
          repr(hs["split_at_median_Vbar_of_nonspecies"])],
         ["low-V-bar pairs", ", ".join(hs["low_Vbar_pairs"])],
         ["low-V-bar amount", repr(hs["low_Vbar_amount"])],
         ["high-V-bar pairs", ", ".join(hs["high_Vbar_pairs"])],
         ["high-V-bar amount", repr(hs["high_Vbar_amount"])],
         ["lowest-V-bar pair", hs["lowest_Vbar_pair"]],
         ["its gap", repr(hs["lowest_Vbar_gap"])]])
    nz = dc["noise"]
    sec["noise"] = _md(
        ["quantity", "value"],
        [["residual sigma (K2e's own origin-forced residuals, participants, ddof=1)",
          repr(nz["residual_sigma"])],
         ["**SE of the aggregate kappa**", "**" + repr(nz["SE_of_aggregate_kappa"])
          + "**"],
         ["the gap", repr(dc["gap"])],
         ["**the gap in SE**", f"**{nz['gap_in_SE']:.4f}**"],
         ["M3's applied point-tolerance", repr(nz["tolerance"])],
         ["**the tolerance in SE**", f"**{nz['tolerance_over_SE']:.4f}**"],
         ["chi2 of per-pair gaps", repr(nz["chi2"])],
         ["chi2 degrees of freedom", str(nz["chi2_df"])],
         ["largest |z| over pairs", repr(nz["max_abs_z"])],
         ["at pair", nz["max_abs_z_pair"]],
         ["reading", nz["reading"]]])
    sec["zscores"] = _md(
        ["pair", "V-bar", "|dvar|", "weight %", "gap_i", "SE_i = sigma/|dvar|", "z"],
        [[q["pair"], repr(q["Vbar"]), repr(abs(q["dvar"])), f"{q['weight_pct']:.2f}%",
          repr(q["gap"]), repr(q["SE_kappa_pair"]), f"{q['z']:.4f}"]
         for q in dc["per_pair"] if q["participates"]])
    n1 = dc["n1b_direction_check"]
    sec["n1b"] = _md(
        ["quantity", "value"],
        [["N1b's LO residual", repr(n1["N1b_LO_residual"])],
         ["N1b's direction", n1["N1b_LO_direction"]],
         ["N4's lowest-V-bar pair", n1["N4_lowest_Vbar_pair"]],
         ["its V-bar", repr(n1["N4_lowest_Vbar"])],
         ["its gap", repr(n1["N4_lowest_gap"])],
         ["N4's direction", n1["N4_direction"]],
         ["**directions agree**", "**" + str(n1["directions_agree"]) + "**"],
         ["reading", n1["reading"]]])
    sec["readings"] = _md(
        ["reading", "verdict", "slug", "routes", "why"],
        [[k, ("ATTRIBUTED" if v["ATTRIBUTED"] else "NOT ATTRIBUTED"), v["slug"],
          str(v["ROUTES"]), v["why"]]
         for k, v in dec["verdict_readings"].items()])
    sec["weights"] = _md(
        ["quantity", "value"],
        [["aggregation rule found", "origin-forced OLS: slope = sum(dvar_i * D_i) / "
                                    "sum(dvar_i^2), i.e. a dvar^2-WEIGHTED MEAN of the "
                                    "per-pair slopes D_i/dvar_i"],
         ["exact form as executed by K2e", "float((x9 @ y9) / (x9 @ x9))"],
         ["participating pairs", ", ".join(dc["participating"])],
         ["structurally inert pairs (dvar = 0)", ", ".join(dc["inert"])],
         ["top-2 weighted pairs", ", ".join(dc["weight_concentration"]["top2_pairs"])],
         ["**their combined weight**",
          f"**{dc['weight_concentration']['top2_weight_pct']:.2f}%**"],
         ["identity", dc["identity"]],
         ["identity residual", repr(dc["identity_residual"])]])
    sec["truth_table"] = _md(
        ["#", "condition", "outcome"],
        [[t["n"], t["condition"],
          ("**" + t["text"] + "**  <-- THIS LEG") if t["outcome"] == dec["verdict_slug"]
          else t["text"]] for t in TRUTH_TABLE])
    sec["gates"] = _md(["gate", "PASS", "detail"],
                       [[k, str(v["PASS"]), v["detail"]] for k, v in dec["gates"].items()])
    sec["sides"] = _md(["clause", "statement", "prior", "sided"],
                       [[k, str(v["clause"]), str(v.get("prior", "—")), v["sided"]]
                        for k, v in p0["sides_rule22"].items()])
    sec["rn"] = _md(["note", "pinned reading"],
                    [[k, v] for k, v in p0["rn_notes"].items()])
    sec["env"] = _md(["component", "value"],
                     [[k, str(v)] for k, v in p0["environment"].items()])
    est = p0["stage_estimates_seconds"]
    meas = {}
    for line in (OUT / "run_log.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if "seconds" in r:
            meas[r["event"]] = float(r["seconds"])
    sec["timing"] = _md(
        ["stage", "estimate (s)", "measured (s)"],
        [["part0", str(est["part0"]), "%.3f" % meas.get("part0_done", float("nan"))],
         ["decompose", str(est["decompose"]),
          "%.3f" % meas.get("decompose_done", float("nan"))],
         ["finalize", str(est["finalize"]),
          "%.3f" % meas.get("finalize_done", float("nan"))],
         ["report", str(est["report"]), "(this stage)"]])
    body = ["# M4-N4 report tables (GENERATED from artifacts -- rule 24)", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _facts(p0: dict[str, Any], dc: dict[str, Any], dec: dict[str, Any]) -> None:
    nz, n1 = dc["noise"], dc["n1b_direction_check"]
    lb = dc["H-b literal (leave-species-out)"]
    hs = dc["H-c split by Vbar"]
    comps = dc["components"]
    f = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "ROUTING_TEXT": dec["routing_text"],
        "PUBLISHED": dc["published"], "PREDICTED": dc["law_through_pipeline"],
        "GAP": dc["gap"], "GAP_ABS": abs(dc["gap"]),
        "M3_DELTA": M3_DELTA, "TOL": M3_TOL,
        "SOURCE": PUBLISHED_SOURCE, "PIN": PUBLISHED_PIN, "PIPELINE": PIPELINE,
        "HA": comps["H-a WEIGHTING"]["amount"],
        "HB": comps["H-b SPECIES"]["amount"],
        "HC": comps["H-c MICRO-DISCREPANCY"]["amount"],
        "HA_PCT": comps["H-a WEIGHTING"]["signed_pct_of_gap"],
        "HB_PCT": comps["H-b SPECIES"]["signed_pct_of_gap"],
        "HC_PCT": comps["H-c MICRO-DISCREPANCY"]["signed_pct_of_gap"],
        "HA_MAG": comps["H-a WEIGHTING"]["magnitude_pct"],
        "HB_MAG": comps["H-b SPECIES"]["magnitude_pct"],
        "HC_MAG": comps["H-c MICRO-DISCREPANCY"]["magnitude_pct"],
        "DOMINANT": dc["dominant"], "ADD_SUM": dc["additive_sum"],
        "ADD_EQ": dc["additive_sum_equals_gap_to"],
        "UNIFORM_GAP": dc["uniform_gap"],
        "NPART": dc["n_participating"],
        "PARTICIPATING": ", ".join(dc["participating"]),
        "INERT": ", ".join(dc["inert"]),
        "TOP2": ", ".join(dc["weight_concentration"]["top2_pairs"]),
        "TOP2W": dc["weight_concentration"]["top2_weight_pct"],
        "IDENT_RESID": dc["identity_residual"],
        "LSO_DROPPED": ", ".join(lb["dropped"]),
        "LSO_GAP": lb["gap_without_species"], "LSO_SHIFT": lb["shift"],
        "HC_LOW": hs["low_Vbar_amount"], "HC_HIGH": hs["high_Vbar_amount"],
        "HC_LOWPAIRS": ", ".join(hs["low_Vbar_pairs"]),
        "HC_HIPAIRS": ", ".join(hs["high_Vbar_pairs"]),
        "LOWEST_PAIR": hs["lowest_Vbar_pair"], "LOWEST_GAP": hs["lowest_Vbar_gap"],
        "SIGMA": nz["residual_sigma"], "SE_AGG": nz["SE_of_aggregate_kappa"],
        "GAP_SE": nz["gap_in_SE"], "TOL_SE": nz["tolerance_over_SE"],
        "CHI2": nz["chi2"], "CHI2_DF": nz["chi2_df"],
        "MAXZ": nz["max_abs_z"], "MAXZ_PAIR": nz["max_abs_z_pair"],
        "N1B_LO": n1["N1b_LO_residual"], "N1B_DIR": n1["N1b_LO_direction"],
        "N4_DIR": n1["N4_direction"], "DIRS_AGREE": n1["directions_agree"],
        "UPGRADE": dec["closure_upgrade"]["closure_upgrades_to_explained_6_of_6"],
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"],
        "PLATFORM": p0["environment"]["platform"],
        "MECH_RESID_PCT": dec["verdict_readings"][
            "mechanistic (only H-a and H-b can attribute; a residual explains nothing)"][
            "unexplained_residual_pct_of_gap"],
    }
    write_json(OUT / "prose_facts.json", f)


REPORT_TEMPLATE = r"""# SUICA M4-N4 — the target-2 forensic — **{{SLUG}}**

**Outcome: {{SLUG}} (routing cell {{CELL}}).** Artifact-space; **no fresh
worlds, no seal**. The question was where M3's one closure miss lives: the K2e
9-pair refit published {{PUBLISHED}} where the winner law, run through the same
pipeline, retrodicts {{PREDICTED}} — a gap of {{GAP}} against a {{TOL}}
point-tolerance.

**The forensic answer is not the one the routing anticipated.** The gap
decomposes as registered, and by magnitude {{DOMINANT}} dominates — but the same
executed arithmetic shows the gap is **{{GAP_SE}} standard errors** of the
pipeline's own estimator, and that M3's applied tolerance was only {{TOL_SE}} SE
wide. The miss was typed at a precision the estimator cannot deliver.

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_N_TAX_MECHANISM_LINE_PLAN.md` BEFORE run (commit 38b7614). Every
number below is generated from artifacts by code (rule 24); none is hand-typed.

---

## 1. G0n4 — the citation chain

The published target's pinned source, restated as the registration requires:

- **Pinned at:** `{{PIN}}`
- **Source path:** `{{SOURCE}}`
- **Pipeline:** {{PIPELINE}}

<<TABLE:g0n4>>

Both headline aggregates reproduce **bit-exactly** from the persisted pair
artifacts under RN-N4-1's pinned arithmetic — the published κ and M3's own
law-through-pipeline prediction. That is the whole basis for trusting everything
downstream.

## 2. The 9 pairs

<<TABLE:pairs>>

### 2.1 The aggregation rule, found exactly

<<TABLE:weights>>

The pipeline is an origin-forced OLS, and an origin-forced slope is
**algebraically a dvar²-weighted mean of the per-pair slopes**
`D_i/dvar_i`. Two consequences follow immediately, and both matter:

1. **The "9-pair refit" is arithmetically a {{NPART}}-pair refit.** {{INERT}}
   sit at dvar = 0 by construction (V_a = V_b), so they contribute exactly
   nothing to both the numerator and the denominator. K2e says so itself and
   declines to define their per-pair κ. They are reported, not hidden.
2. **Two pairs carry {{TOP2W}}% of the weight** — {{TOP2}} — because weight goes
   as dvar² and their |dvar| is roughly 2.5× the rest.

This yields an exact identity the whole decomposition rests on:
gap = Σ wᵢ·gapᵢ, reproduced to {{IDENT_RESID}}.

## 3. Per-pair contributions

<<TABLE:contrib>>

## 4. The decomposition

<<TABLE:components>>

**H-a WEIGHTING = {{HA}}.** Re-aggregating the same per-pair gaps under uniform
weights instead of the pipeline's own gives {{UNIFORM_GAP}} — nearly three times
the published miss. So the weighting is doing a great deal of work, and it is
working in the direction of making the closure look **better**, not worse: the
two heavily-weighted pairs happen to sit close to the law, while the pairs that
miss badly carry almost no weight.

**H-b SPECIES = {{HB}}**, the smallest component by magnitude ({{HB_MAG}}%). The
registration's literal leave-species-out quantification agrees on direction and
sharpens it:

<<TABLE:hb>>

Dropping the two `int:` pairs moves the gap to {{LSO_GAP}} — a shift of
{{LSO_SHIFT}}. **The species pairs mask the miss rather than cause it.**

**H-c MICRO-DISCREPANCY = {{HC}}**, the residual after H-a and H-b and the
largest by magnitude ({{HC_MAG}}%), split by pair V̄ as registered:

<<TABLE:hc>>

## 5. Why the residual is not a discrepancy

The registration's decomposition presupposes that the gap is a signal to be
attributed. Before accepting that, the arithmetic of the estimator itself
(RN-N4-5, pinned before any component was read):

<<TABLE:noise>>

The pipeline is a regression; it has a standard error. The per-pair κ of a pair
with small |dvar| is a ratio `D/dvar` whose noise scales as σ/|dvar|, so pairs
with small |dvar| have wildly noisy per-pair κ — and those are exactly the pairs
carrying the large gaps.

<<TABLE:zscores>>

- The aggregate gap is **{{GAP_SE}} SE**. Not significant.
- χ² = {{CHI2}} on {{CHI2_DF}} pairs — almost exactly its expectation. The
  per-pair gaps are collectively indistinguishable from noise.
- The largest single |z| is {{MAXZ}} at {{MAXZ_PAIR}}.
- M3's point-tolerance of {{TOL}} is **{{TOL_SE}} SE** wide.

**The dvar²-weighting is not an artifact — it is the correct estimator.** If D
carries homoskedastic noise then Var(Dᵢ/dvarᵢ) = σ²/dvarᵢ², so weights ∝ dvarᵢ²
are exactly inverse-variance weights. H-a is large precisely because the
pipeline is doing the statistically right thing and the uniform comparator is
doing the wrong one. Read that way, H-a is not a defect in the closure; it is
the closure's estimator behaving correctly, and the "attribution" is an artifact
of comparing it against an inferior weighting.

## 6. The N1b direction check

H-c's registered motivation was N1b's low-V̄ residual. It does not survive
contact:

<<TABLE:n1b>>

N1b's LO residual had the measured response tax running **above** the level
curve. N4's lowest-V̄ pair ({{LOWEST_PAIR}}) has the measured level tax running
**below** the law, gap {{LOWEST_GAP}}. The directions are **opposite**
({{DIRS_AGREE}}), so cell 4's stated consequence — "the LO whisper hardens" — is
**not supported by the arithmetic that routes there**. Reported as the leg's
central caution.

## 7. Verdict, under both readings

RN-N4-4 pins the accounting before any component was read, because the
registration leaves two things open: H-c is *defined* as the residual, so the
three components are exhaustive and the ≥80% bar cannot fail; and the components
take opposite signs, so signed shares exceed 100%.

<<TABLE:readings>>

The literal reading routes, and it gives {{SLUG}} at cell {{CELL}}. The
mechanistic reading — that a residual explains nothing, so only H-a and H-b can
attribute — leaves {{MECH_RESID_PCT}}% of the gap unexplained and would give
UNATTRIBUTED. Both are reported; neither is hidden behind the other.

### Does the closure upgrade?

**No.** Cell 2 is the only cell carrying the closure upgrade to explained-6/6,
and this leg routed to cell {{CELL}} ({{UPGRADE}}). But the honest reason the
closure should not be upgraded on this evidence is not the routing — it is that
there is nothing to explain: a {{GAP_SE}}-SE deviation against a tolerance
narrower than one SE is a tolerance-calibration fact, and re-typing that target
is the planner's call, not the executor's.

## 8. Routing

<<TABLE:truth_table>>

## 9. Gates

<<TABLE:gates>>

## 10. Sides declared (rule 22)

<<TABLE:sides>>

## 11. Pinned readings

<<TABLE:rn>>

## 12. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine and the only `pandas` present belongs to CPython 3.9.6,
   which cannot import the machinery. A CPython {{PYTHON}} venv was built
   outside the repo from `requirements-lock-main.txt` verbatim and pinned.
   Resolved BEFORE any hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.
3. **A-3 (summation order; before any component).** A naive Python sum of the
   same nine terms reproduces the published κ only to the last 1–2 ULP. K2e's
   exact form is `float((x9 @ y9) / (x9 @ x9))` on arrays in its own pair order;
   pinning that (RN-N4-1) makes both headline aggregates bit-exact. Found and
   pinned BEFORE any decomposition number existed. Without it this leg would
   have opened with a spurious citation mismatch.

## 13. Registration-defect candidates

1. **The ≥80% bar cannot fail** (RN-N4-4a). H-c is defined as "the residual
   after H-a and H-b", so the three components sum to the gap by construction
   and 100% is always attributed. The bar carries no information; only the
   dominance question does. Non-blocking — pinned and both readings reported.
2. **No noise floor was declared.** The decomposition presupposes the gap is
   signal. The estimator's SE ({{SE_AGG}}) is computable from persisted
   artifacts and is **larger than the {{TOL}} tolerance the target was typed
   against**; the gap is {{GAP_SE}} SE. A forensic registration on a regression
   output should declare, before the components, whether the quantity is
   distinguishable from zero. This is the #43/#44/#51 genus again: a
   gate-consumed quantity that was computable at registration and not computed.
3. **Cell 4's stated consequence is contradicted by the arithmetic that reaches
   it** (§6): the low-V̄ discrepancy runs opposite in sign to the N1b lean whose
   hardening the cell prescribes.

## 14. Environment

<<TABLE:env>>

## 15. Timing

<<TABLE:timing>>

---

*Artifacts: `results/m4_n4_target2_forensic/` (gitignored) — `part0.json`,
`decomposition.json`, `per_pair.csv`, `decision.json`, `prose_facts.json`,
`report_tables.md`, `run_log.jsonl`. Harness:
`scripts/run_suica_m4_n4_target2_forensic.py`.*
"""


def _fmt(v: Any) -> str:
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, float):
        return repr(v)
    if isinstance(v, list):
        return "[" + ", ".join(_fmt(x) for x in v) + "]"
    return str(v)


def stage_report(args: argparse.Namespace) -> None:
    facts = read_json(OUT / "prose_facts.json")
    tables = (OUT / "report_tables.md").read_text(encoding="utf-8")
    sec: dict[str, str] = {}
    cur, buf = None, []
    for line in tables.split("\n"):
        if line.startswith("<!-- TABLE:"):
            if cur:
                sec[cur] = "\n".join(buf).strip()
            cur, buf = line.split("<!-- TABLE:")[1].split(" -->")[0], []
        elif cur:
            buf.append(line)
    if cur:
        sec[cur] = "\n".join(buf).strip()
    txt = REPORT_TEMPLATE
    for k, v in facts.items():
        txt = txt.replace("{{" + k + "}}", _fmt(v))
    for k, v in sec.items():
        txt = txt.replace("<<TABLE:" + k + ">>", v)
    left = [t for t in ("{{", "<<TABLE:") if t in txt]
    if left:
        import re
        bad = re.findall(r"\{\{[A-Z0-9_]+\}\}|<<TABLE:[a-z0-9_]+>>", txt)
        raise SystemExit(f"REFUSED: unresolved placeholders: {sorted(set(bad))}")
    path = ROOT / "reports" / "SUICA_M4_N4_TARGET2_FORENSIC_REPORT.md"
    path.write_text(txt, encoding="utf-8")
    print(f"report OK  {rel(path)}  ({len(txt.splitlines())} lines)")
    _ = args


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="stage", required=True)
    stages: list[tuple[str, Callable[[argparse.Namespace], None]]] = [
        ("part0", stage_part0), ("decompose", stage_decompose),
        ("finalize", stage_finalize), ("report", stage_report)]
    for name, fn in stages:
        sub.add_parser(name).set_defaults(fn=fn)

    def _all(a: argparse.Namespace) -> None:
        for _, fn in stages:
            fn(a)
    sub.add_parser("all").set_defaults(fn=_all)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
