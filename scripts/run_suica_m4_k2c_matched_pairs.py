#!/usr/bin/env python3
"""M4-K2c -- matched-attenuation pairs: transform of card algebra, or state
composition?  (link-free)

Registered spec: docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md section "M4-K2c --
Matched-attenuation pairs: is the reader a transform of card algebra, or does it
read state composition? (link-free)" (REGISTERED 2026-08-09, BEFORE RUN, commit
8adb0a9), together with the K2b OUTCOME and planner adjudication immediately
above it (defect #20, standing rule 14, the over-response anchors).  Theory:
docs/SUICA_IDENTITY_THEORY_V1.md T4 (S3), appendices H and I.

Executor standing: implementation and execution only.  Everything labelled
"RN-n" below is a register-note -- an operationalization of something the
registration left open (standing rule 9) -- fixed and written to
reports/SUICA_M4_K2C_MATCHED_PAIRS_REPORT.md Part 0 BEFORE any main arm ran.

Reuse boundary (registration: "REUSE its machinery wholesale"):
  * scripts/run_suica_m4_k2b_t4_branch.py (k2b()) -- the whole expressive-world
    apparatus, imported and CALLED UNMODIFIED: layout (k2b:238-293),
    retained_cell_sizes (k2b:296-300), build_k2b_world (k2b:316-353), emit_panel
    (k2b:359-381), card_channel_frame (k2b:392-457), pooled_card_stats
    (k2b:463-489), bootstrap_card (k2b:505-509), arm_weights/arm_shares
    (k2b:198-213), arm_predictions (k2b:533-584), run_field_world (k2b:607-704),
    field_from_vectors (k2b:592-604), read_csv_rt (k2b:178-180), spearman
    (k2b:710-715), CHANNELS/DIM/NOISE_SHARE/SIGNAL_SHARE.  k2b in turn imports
    k2a (the validated instrument), f2, f1 and e1 unchanged.
  * suica_core/ is READ-ONLY and untouched.
  * NEW in this leg (rule 12): predicted_attenuation, solve_share_for_target,
    solve_matched_pair, world_seed_for (K2c salt), run_field_world (a two-line
    provenance wrapper around k2b's), bootstrap_card_pair, ols_slope,
    l3_pooled_q.

Stages (foreground, chunked, resumable; artifacts under
results/m4_k2c_matched_pairs/):
  --stage part0     the COMPUTED shares, every prediction, and G0c'..G5c' on
                    RESERVED pilot worlds 9701-9702.  Writes gates.json,
                    part0_arms.json, part0_predictions.csv, part0_tables.md.
                    `arms` refuses to run unless every Part-0 gate passes AND
                    the Part-0 report exists on disk.
  --stage arms      the 7 arms x N worlds, chunked by WORLD RANGE
                    (--worlds a-b), all arms per chunk (both phi worlds are
                    built once per world index and shared across arms).
  --stage finalize  G1c' post-arms matching, D_k per pair, L-1/L-2/PARTIAL-C,
                    L-3, rule-13 stability, pivots, decision.json.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import suica_core.v8_realtext_relation_field as v8  # noqa: E402

BANNER = "synthetic worlds calibrated to an opened-panel regime, exploratory"

# --- registration-fixed constants -------------------------------------------
MASTER_SEED = 20260817             # registration: "master_seed 20260817"
WORLDS_PER_ARM = 32                # registration: "32 worlds/arm"
ESCALATION_LADDER = (32, 64)       # registration G2c': "escalate 32->64 once"
PILOT_WORLDS = (9701, 9702)        # RESERVED; disjoint from main indices 0..63
B_BOOT = 2000                      # registration G3c': "B=2000, seed=master"
B_BOOT_HIGH = 20000                # registration G3c': ">=10xB" (rule 13)

# registration: "three matched pairs at target predicted attenuations
# ~ {0.78, 0.68, 0.56}: (s_ka, phi=.90) vs (s_kb, phi=.98)"
PAIR_TARGETS: tuple[tuple[str, float], ...] = (("P1", 0.78), ("P2", 0.68), ("P3", 0.56))
PHI_A, PHI_B = 0.90, 0.98
ANCHOR_ARM = ("A1anc", 0.02, 0.90)   # registration: "A1-anchor (.02, .90)"

# registration G1c': "Part-0 predicted difference <= 1e-12"
MATCH_TOL_PART0 = 1e-12
# registration G1c': "measured within-pair card-attenuation difference pooled CI
# inside +/-0.005"
MATCH_TOL_MEASURED = 0.005
# registration G2c': "MDE(80%, a=.05, paired, n=32) ... <= 0.020"
MDE_TARGET = 0.020
# registration L-1: "m_k = max(0.020, MDE_k)"
#
# RN-3 (rule 9 -- the registration does not say WHICH MDE_k).  PRIMARY: the
# REALIZED-sd MDE at the executed n, i.e. the resolution the leg actually
# achieved on the data it collected; SECOND READING: the Part-0 pilot MDE.  Both
# are computed and reported for every pair.  Fixed before any main arm ran.
EQUIV_FLOOR = 0.020

# RN-4 (rule 9 -- the registered partition is INCOMPLETE).  L-1 (3/3 pairs
# |D_k| CI inside +/-m_k) and L-2 (>=2/3 pairs CI excluding 0, one sign) are NOT
# mutually exclusive: a difference can be statistically resolved and still lie
# strictly inside the materiality margin (e.g. D = 0.012, CI [0.004, 0.019]).
# The registration gives no precedence.  RESOLUTION, fixed before any main arm:
# simultaneous fire is scored as **BOTH_FIRE**, a NAMED NON-REGISTERED outcome
# reported as such (the standing convention for results that fit no registered
# branch), NOT as either branch; T4 is not re-typed on it, both readings are
# reported at full precision, and the substantive reading offered to the planner
# is "composition-sensitivity is real but sub-material at the registered
# margin".  Likewise 0/3 significant WITHOUT 3/3 equivalence is
# NO_REGISTERED_BRANCH (underpowered, rule 2), not L-1.

# RN-6: K2b's arm-independent reader efficiency, used ONLY as L-3's intercept
# scale.  The OLS SLOPE q is invariant to lambda (subtracting log(lambda), a
# constant, from y cannot change a slope), so L-3's verdict does not depend on
# this number at all; finalize verifies the invariance numerically against
# lambda = 1.
K2B_LAMBDA = 0.17417497661611914

# --- t-quantiles (RN-7).  MDE(80%, alpha=.05, paired, n) =
#     (t_{.975,n-1} + t_{.80,n-1}) sd/sqrt(n).  Values from scipy.stats.t.ppf,
#     cross-checked against scipy at Part 0 when importable.  NOTE (anomaly A-1):
#     k2b's hardcoded table carries t_{.80,31} = 0.8534705711311653, which is
#     1.0028e-04 above the correct 0.853370295696944; K2b never exercised n=32
#     (it ran at n=8), so nothing in K2b changes.  K2c uses the correct values.
T_QUANTILES: dict[int, tuple[float, float]] = {
    32: (2.039513446396408, 0.853370295696944),
    64: (1.998340542520741, 0.8473639122756463),
}

OUT = ROOT / "results" / "m4_k2c_matched_pairs"
REPORT = ROOT / "reports" / "SUICA_M4_K2C_MATCHED_PAIRS_REPORT.md"
K2B_OUT = ROOT / "results" / "m4_k2b_t4_branch"
K2A_OUT = ROOT / "results" / "m4_k2a_expressive_world"
K2B_PRIMARY_ARMS = ("A1", "A2", "A3", "A4", "A5", "A6")

_K2B: Any = None


def k2b() -> Any:
    global _K2B
    if _K2B is None:
        path = ROOT / "scripts" / "run_suica_m4_k2b_t4_branch.py"
        spec = importlib.util.spec_from_file_location("run_suica_m4_k2b_t4_branch", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _K2B = module
    return _K2B


def read_csv_rt(path: Path) -> pd.DataFrame:
    """G5c': every artifact re-read with float_precision='round_trip'."""
    return k2b().read_csv_rt(path)


def mde_paired(sd_diff: float, n: int) -> float:
    t_alpha, t_beta = T_QUANTILES[n]
    return (t_alpha + t_beta) * sd_diff / math.sqrt(n)


def world_seed_for(world: int) -> int:
    """RN-1: K2c's OWN seed lineage (master_seed 20260817, salt 'm4k2c-world').
    The seed depends on the WORLD INDEX ONLY, so every arm -- including the two
    arms of a pair, which differ in phi -- shares the trait b, the AR
    innovations, the frame shocks, the interaction loadings and the noise
    bit-for-bit.  The within-pair contrast is therefore exactly paired, which is
    what makes D_k a within-world difference."""
    return int(
        v8.stable_bucket(f"{MASTER_SEED}-{world}", salt="m4k2c-world", modulus=2**31 - 1)
    )


def run_field_world(arm_id: str, world_index: int, world, w, *, verify: bool = False):
    """RN-2 (provenance): k2b.run_field_world is called UNMODIFIED, so the corpus
    tag it builds keeps the literal prefix 'm4k2b-'.  The tag is a hash label
    seeding the deployed transition-null permutation streams
    (f1:199-206); prefixing every K2c arm id with 'K2C-' makes every tag
    DISJOINT from every K2b tag, which is what the fresh lineage requires.  The
    returned row's 'arm' field is rewritten to the clean K2c id."""
    row = k2b().run_field_world(f"K2C-{arm_id}", world_index, world, w, verify=verify)
    row["arm"] = arm_id
    return row


# ---------------------------------------------------------------------------
# PART 0, step 1: the COMPUTED shares (the designed identity).

def predicted_attenuation(share: float, phi: float) -> float:
    """r(card -> b) from the K2a-validated attenuation algebra (max relative
    error 0.30% over 12 cells; 0.0975% over K2b's 6 arms), evaluated on THIS
    panel's (context, m) norm cells.  Pure algebra: no world is generated."""
    return float(k2b().arm_predictions(share, phi, "zero")["r_card_b_pred_raw"])


def solve_share_for_target(target: float, phi: float) -> dict[str, float]:
    """Bisection to adjacent doubles.  r(.,phi) is strictly decreasing in share
    on (0,1), so the bracket is unconditional."""
    lo, hi = 0.0, 0.999999
    r_lo, r_hi = predicted_attenuation(lo, phi), predicted_attenuation(hi, phi)
    if not (r_hi <= target <= r_lo):
        raise SystemExit(
            f"REFUSED: target {target!r} outside the attainable range "
            f"[{r_hi!r}, {r_lo!r}] at phi={phi!r}"
        )
    iters = 0
    while iters < 400:
        mid = 0.5 * (lo + hi)
        if mid <= lo or mid >= hi:
            break
        if predicted_attenuation(mid, phi) > target:
            lo = mid
        else:
            hi = mid
        iters += 1
    cand = min((lo, hi), key=lambda s: abs(predicted_attenuation(s, phi) - target))
    return {
        "share": float(cand),
        "attenuation": predicted_attenuation(cand, phi),
        "target": float(target),
        "abs_error_vs_target": abs(predicted_attenuation(cand, phi) - target),
        "bisection_iterations": iters,
        "bracket_width_final": float(hi - lo),
    }


def solve_matched_pair(pair_id: str, target: float) -> dict[str, Any]:
    """Arm a is solved to the nominal target; arm b is then solved to arm a's
    ACHIEVED attenuation, so the within-pair predicted difference is bounded by
    the solver's own resolution, not by the target's representability."""
    a = solve_share_for_target(target, PHI_A)
    b = solve_share_for_target(a["attenuation"], PHI_B)
    diff = a["attenuation"] - b["attenuation"]
    return {
        "pair": pair_id,
        "target_attenuation": float(target),
        "arm_a": {"arm": f"{pair_id}a", "share": a["share"], "phi": PHI_A,
                  "predicted_attenuation": a["attenuation"],
                  "bisection_iterations": a["bisection_iterations"],
                  "bracket_width_final": a["bracket_width_final"]},
        "arm_b": {"arm": f"{pair_id}b", "share": b["share"], "phi": PHI_B,
                  "predicted_attenuation": b["attenuation"],
                  "bisection_iterations": b["bisection_iterations"],
                  "bracket_width_final": b["bracket_width_final"]},
        "share_gap_b_minus_a": b["share"] - a["share"],
        "predicted_attenuation_difference": diff,
        "abs_predicted_difference": abs(diff),
        "matched_part0": bool(abs(diff) <= MATCH_TOL_PART0),
        "arm_a_abs_error_vs_target": a["abs_error_vs_target"],
    }


def arms_spec() -> list[dict[str, Any]]:
    """The 7 arms, read back from the Part-0 artifact (the shares are COMPUTED,
    so no stage after part0 may re-derive them independently)."""
    path = OUT / "part0_arms.json"
    if not path.exists():
        raise SystemExit("REFUSED: results/m4_k2c_matched_pairs/part0_arms.json missing.")
    return json.loads(path.read_text(encoding="utf-8"))["arms"]


# ---------------------------------------------------------------------------
# Paired card bootstrap: the SAME authors-within-world multinomial multipliers
# applied to both arms of a pair (k2a's scheme, unmodified; the pairing is what
# a within-pair difference requires).

def bootstrap_card_pair(
    frame_a: pd.DataFrame, frame_b: pd.DataFrame, b_draws: int, seed: int, chunk: int = 250
) -> tuple[dict[str, float], dict[str, float], dict[str, np.ndarray], dict[str, np.ndarray]]:
    key_cols = ["author", "world_seed", "cell_key", "m"]
    for c in key_cols:
        if not frame_a[c].equals(frame_b[c]):
            raise SystemExit(f"REFUSED: pair frames not row-aligned on {c!r}")
    keep = [c for c in frame_a.columns if c not in key_cols]
    cols = {c: i for i, c in enumerate(keep)}
    data_a = frame_a[keep].to_numpy(float)
    data_b = frame_b[keep].to_numpy(float)
    n_rows = float(len(frame_a))
    pooled = k2b().pooled_card_stats
    point_a = pooled(data_a.sum(axis=0), cols, n_rows)
    point_b = pooled(data_b.sum(axis=0), cols, n_rows)
    worlds = frame_a["world_seed"].to_numpy()
    strata = [np.flatnonzero(worlds == u) for u in np.unique(worlds)]
    rng = np.random.default_rng(seed)
    reps_a: dict[str, list[np.ndarray]] = {}
    reps_b: dict[str, list[np.ndarray]] = {}
    done = 0
    while done < b_draws:
        take = min(chunk, b_draws - done)
        mult = np.zeros((take, len(frame_a)))
        for idx in strata:
            mm = len(idx)
            mult[:, idx] = rng.multinomial(mm, np.full(mm, 1.0 / mm), size=take)
        for reps, data in ((reps_a, data_a), (reps_b, data_b)):
            block = pooled(mult @ data, cols, n_rows)
            for key, value in block.items():
                reps.setdefault(key, []).append(np.atleast_1d(value))
        done += take
    boots_a = {k: np.concatenate(v) for k, v in reps_a.items()}
    boots_b = {k: np.concatenate(v) for k, v in reps_b.items()}
    return point_a, point_b, boots_a, boots_b


# ---------------------------------------------------------------------------
# L-3: the pooled log-log slope q.  DESCRIPTIVE-TO-LEAN, no branch weight.

def ols_slope(x: np.ndarray, y: np.ndarray) -> float:
    xc = x - x.mean()
    return float((xc @ (y - y.mean())) / (xc @ xc))


def l3_pooled_q(
    x_log_att: np.ndarray,
    k2b_field: dict[str, np.ndarray],
    k2c_field: dict[str, np.ndarray],
    order_k2b: tuple[str, ...],
    order_k2c: tuple[str, ...],
    lam: float,
    b_draws: int,
    seed: int,
) -> dict[str, Any]:
    """x is FIXED at the Part-0 predicted attenuation (RN-5); y = log(field/lam)
    per arm.  Worlds are resampled in blocks WITHIN each leg, shared across that
    leg's arms (the arms are world-paired by construction)."""
    def y_of(fb: dict[str, np.ndarray], fc: dict[str, np.ndarray]) -> np.ndarray:
        vals = [np.mean(fb[a]) for a in order_k2b] + [np.mean(fc[a]) for a in order_k2c]
        return np.log(np.asarray(vals, dtype=float) / lam)

    y_point = y_of(k2b_field, k2c_field)
    q_point = ols_slope(x_log_att, y_point)
    n_b = len(next(iter(k2b_field.values())))
    n_c = len(next(iter(k2c_field.values())))
    rng = np.random.default_rng(seed)
    pick_b = rng.integers(0, n_b, size=(b_draws, n_b))
    pick_c = rng.integers(0, n_c, size=(b_draws, n_c))
    mat_b = np.stack([k2b_field[a][pick_b].mean(axis=1) for a in order_k2b], axis=1)
    mat_c = np.stack([k2c_field[a][pick_c].mean(axis=1) for a in order_k2c], axis=1)
    y_boot = np.log(np.concatenate([mat_b, mat_c], axis=1) / lam)
    xc = x_log_att - x_log_att.mean()
    q_boot = ((y_boot - y_boot.mean(axis=1, keepdims=True)) @ xc) / (xc @ xc)
    lo, hi = k2b().k2a().ci_of(q_boot)
    resid = y_point - (y_point.mean() + q_point * (x_log_att - x_log_att.mean()))
    return {
        "q": q_point,
        "q_ci": [lo, hi],
        "q_boot": q_boot,
        "intercept_at_lambda": float(y_point.mean() - q_point * x_log_att.mean()),
        "n_points": int(len(x_log_att)),
        "r2": float(1.0 - (resid @ resid) / ((y_point - y_point.mean()) @ (y_point - y_point.mean()))),
        "clause_q_gt_1": bool(q_point > 1.0),
        "clause_ci_excludes_1": bool(lo > 1.0 or hi < 1.0),
        "lambda": float(lam),
    }


# ---------------------------------------------------------------------------
# Stage: part0

def run_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    m = k2b()
    lay = m.layout()
    gates: dict[str, Any] = {
        "leg": "M4-K2c",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "pilot_worlds": list(PILOT_WORLDS),
        "worlds_per_arm_registered": WORLDS_PER_ARM,
        "noise_share": m.NOISE_SHARE,
        "signal_share": m.SIGNAL_SHARE,
        "rule14_compliance": (
            "NO GATE AND NO BRANCH LEAN IN THIS LEG COMPARES QUANTITIES ACROSS "
            "SCALES.  G0c' re-derives K2b numbers against themselves; G1c' "
            "compares card attenuation to card attenuation; G2c'/G4c'/L-1/L-2/"
            "PARTIAL-C compare field agreement to field agreement.  L-3 is the "
            "single cross-scale object; the registration declares it "
            "descriptive-to-lean with NO BRANCH WEIGHT, and it pins its own link "
            "(a log-log power law whose exponent q IS the estimand), so rule 14's "
            "first clause is satisfied for it and its second clause (link-free "
            "redesign) is satisfied for everything that adjudicates T4."
        ),
    }

    # ---- step 1: the COMPUTED shares (pure algebra, before any world exists)
    t_shares = time.time()
    pairs = [solve_matched_pair(pid, tgt) for pid, tgt in PAIR_TARGETS]
    arms: list[dict[str, Any]] = []
    for pr in pairs:
        for side in ("arm_a", "arm_b"):
            arms.append({
                "arm": pr[side]["arm"], "pair": pr["pair"], "side": side[-1],
                "share": pr[side]["share"], "phi": pr[side]["phi"],
                "w_int_arm": "zero", "role": "pair",
                "target_attenuation": pr["target_attenuation"],
            })
    arms.append({"arm": ANCHOR_ARM[0], "pair": None, "side": None,
                 "share": ANCHOR_ARM[1], "phi": ANCHOR_ARM[2],
                 "w_int_arm": "zero", "role": "anchor", "target_attenuation": None})
    shares_seconds = time.time() - t_shares

    pred_rows = []
    for a in arms:
        pred = m.arm_predictions(a["share"], a["phi"], a["w_int_arm"])
        pred_rows.append({"arm": a["arm"], "pair": a["pair"], "side": a["side"],
                          "role": a["role"], "target_attenuation": a["target_attenuation"],
                          **pred})
    preds = pd.DataFrame(pred_rows)
    preds.to_csv(OUT / "part0_predictions.csv", index=False)
    pred_by_arm = {r["arm"]: r for _, r in preds.iterrows()}
    arm_ids = tuple(a["arm"] for a in arms)

    # ---- G0c': anchors, bit-exact
    g0: dict[str, Any] = {}
    k2b_dec = json.loads((K2B_OUT / "decision.json").read_text(encoding="utf-8"))
    k2b_gates = json.loads((K2B_OUT / "gates.json").read_text(encoding="utf-8"))
    k2b_pred = read_csv_rt(K2B_OUT / "part0_predictions.csv").set_index("arm")
    k2b_field = {
        a: read_csv_rt(K2B_OUT / f"arm_{a}_field.csv").sort_values("world")[
            "recovery_b_only"].to_numpy(float)
        for a in K2B_PRIMARY_ARMS
    }
    rec_a1 = float(np.mean(k2b_field["A1"]))
    rec_a4 = float(np.mean(k2b_field["A4"]))
    s_re = rec_a1 - rec_a4
    p_re = float(k2b_gates["G1b"]["P_identity"])
    sp_re = s_re / p_re
    meas_rec = np.array([float(np.mean(k2b_field[a])) for a in K2B_PRIMARY_ARMS])
    pred_att_k2b = np.array(
        [float(k2b_pred.loc[a, "r_card_b_pred_raw"]) for a in K2B_PRIMARY_ARMS]
    )
    lam_re = float(np.mean(meas_rec) / np.mean(pred_att_k2b))
    slp_re = float(s_re / (lam_re * p_re))
    persisted = {
        "A1_field_recovery": k2b_dec["second_readings"]["per_arm_field_recovery"]["A1"]["b_only_mean"],
        "A4_field_recovery": k2b_dec["second_readings"]["per_arm_field_recovery"]["A4"]["b_only_mean"],
        "S_over_P": k2b_dec["leans"]["L-B"]["S_over_P"],
        "S": k2b_dec["leans"]["L-B"]["S"],
        "lambda": k2b_dec["second_readings"]["efficiency_normalized_descriptive"]["lambda"],
        "S_over_lambda_P": k2b_dec["second_readings"]["efficiency_normalized_descriptive"]["S_over_lambda_P"],
    }
    rederived = {
        "A1_field_recovery": rec_a1, "A4_field_recovery": rec_a4,
        "S_over_P": sp_re, "S": s_re, "lambda": lam_re, "S_over_lambda_P": slp_re,
    }
    g0["k2b_anchors"] = {
        "persisted": persisted, "rederived": rederived,
        "residual": {k: rederived[k] - persisted[k] for k in persisted},
        "bit_exact": {k: bool(rederived[k] == persisted[k]) for k in persisted},
        "all_bit_exact": bool(all(rederived[k] == persisted[k] for k in persisted)),
        "route": "round-trip re-read of results/m4_k2b_t4_branch/arm_A*_field.csv and "
                 "part0_predictions.csv; P_identity from gates.json G1b",
    }
    # K2a anchor cell, exactly as K2b's G0b did it
    a_cid, a_phi, a_occ, a_arm = "phi0.9_occ8_intzero", 0.9, 8, "zero"
    k2a = m.k2a()
    k2a_persisted = read_csv_rt(K2A_OUT / f"cell_{a_cid}.csv")
    k2a_re = pd.concat(
        [k2a.suff_stats_for_world(k2a.world_seed_for(a_phi, a_occ, w), a_phi, a_occ,
                                  a_arm, k2a.N_AUTHORS)
         for w in range(k2a.WORLDS_PER_CELL)],
        ignore_index=True,
    )
    shared = [c for c in k2a_persisted.columns if c in k2a_re.columns]
    diffs = {c: float(np.max(np.abs(k2a_persisted[c].to_numpy(float) - k2a_re[c].to_numpy(float))))
             for c in shared}
    g0["k2a_anchor"] = {
        "cell": a_cid, "rows": int(len(k2a_persisted)), "columns_compared": len(shared),
        "max_abs_residual": float(max(diffs.values())),
        "bit_exact": bool(max(diffs.values()) == 0.0),
    }
    g0["panel"] = {
        "authors_per_world": int(len(lay["author_ids"])),
        "retained_authors": int(len(lay["retained_idx"])),
        "events_total": int(lay["counts"].sum()),
        "m_multiset": {int(k): int(v) for k, v in
                       sorted(pd.Series(lay["counts"]).value_counts().items())},
        "contexts": sorted(set(lay["contexts"])),
        "retained_cell_sizes": m.retained_cell_sizes(),
    }
    # t-quantile cross-check (RN-7 / anomaly A-1)
    tq: dict[str, Any] = {"table": {str(k): list(v) for k, v in T_QUANTILES.items()}}
    try:
        from scipy import stats as _st  # noqa: PLC0415
        tq["scipy_version"] = __import__("scipy").__version__
        tq["max_abs_deviation_vs_scipy"] = float(max(
            max(abs(T_QUANTILES[n][0] - float(_st.t.ppf(0.975, n - 1))),
                abs(T_QUANTILES[n][1] - float(_st.t.ppf(0.80, n - 1))))
            for n in T_QUANTILES
        ))
    except Exception as exc:                                  # pragma: no cover
        tq["scipy_version"] = f"unavailable: {exc}"
        tq["max_abs_deviation_vs_scipy"] = None
    tq["k2b_table_n32_t80"] = 0.8534705711311653
    tq["k2b_table_n32_t80_error"] = 0.8534705711311653 - T_QUANTILES[32][1]
    tq["k2b_impact"] = "none: K2b selected n=8 and never evaluated its n=32 entry"
    g0["t_quantiles"] = tq
    g0["criterion"] = (
        "all six K2b anchors (A1/A4 field recovery, S, S/P, lambda, S/(lambda P)) "
        "re-derived from persisted artifacts EQUAL bit-exactly, AND the K2a anchor "
        "cell re-derives with residual == 0.0"
    )
    g0["pass"] = bool(g0["k2b_anchors"]["all_bit_exact"] and g0["k2a_anchor"]["bit_exact"])
    gates["G0c_prime"] = g0

    # ---- G1c' (Part-0 half): the designed identity
    g1: dict[str, Any] = {
        "pairs": pairs,
        "tolerance_part0": MATCH_TOL_PART0,
        "tolerance_measured_post_arms": MATCH_TOL_MEASURED,
        "max_abs_predicted_difference": float(max(p["abs_predicted_difference"] for p in pairs)),
        "criterion_part0": "within-pair PREDICTED attenuation difference <= 1e-12 for 3/3 pairs",
        "criterion_post_arms": (
            "within-pair MEASURED card attenuation difference pooled 95% CI inside "
            "+/-0.005 (5x K2a's max attenuation error 0.00065); a pair failing the "
            "match is VOID for composition claims"
        ),
        "part0_pass": bool(all(p["matched_part0"] for p in pairs)),
    }
    g1["pass"] = g1["part0_pass"]
    gates["G1c_prime"] = g1

    # ---- pilot: both channels, all 7 arms, on the RESERVED worlds
    t_pilot = time.time()
    build_times: list[float] = []
    pilot_worlds: dict[tuple[int, float], Any] = {}
    for w_idx in PILOT_WORLDS:
        for phi in (PHI_A, PHI_B):
            tb = time.time()
            pilot_worlds[(w_idx, phi)] = m.build_k2b_world(world_seed_for(w_idx), phi)
            build_times.append(time.time() - tb)
    pilot_card: dict[str, pd.DataFrame] = {}
    pilot_field: dict[str, list[dict[str, Any]]] = {}
    pilot_panels: dict[str, list[np.ndarray]] = {}
    realized: dict[str, dict[str, float]] = {}
    frame_residual_max = 0.0
    for a in arms:
        w = m.arm_weights(a["share"], a["w_int_arm"])
        frames, rows = [], []
        for w_idx in PILOT_WORLDS:
            world = pilot_worlds[(w_idx, a["phi"])]
            frame, cres = m.card_channel_frame(world, w, world_seed_for(w_idx))
            frame_residual_max = max(frame_residual_max, cres)
            frames.append(frame)
            rows.append(run_field_world(a["arm"], w_idx, world, w,
                                        verify=(w_idx == PILOT_WORLDS[0])))
        pilot_card[a["arm"]] = pd.concat(frames, ignore_index=True)
        pilot_field[a["arm"]] = rows
        pilot_panels[a["arm"]] = m.emit_panel(pilot_worlds[(PILOT_WORLDS[0], a["phi"])], w)
        realized[a["arm"]] = rows[0]["realized_shares"]
    pilot_seconds = time.time() - t_pilot
    pilot_work_seconds = pilot_seconds - float(np.sum(build_times))

    # ---- G4c': liveness (rule 3) + within-pair non-degeneracy (rule 10)
    g4: dict[str, Any] = {"within_pair": [], "across_target": {}}
    pilot_card_point = {}
    for a in arms:
        pt, _ = m.bootstrap_card(pilot_card[a["arm"]], 1, MASTER_SEED)
        pilot_card_point[a["arm"]] = {"gap": float(pt["gap"]),
                                      "attenuation": float(pt["r_card_b_raw"])}
    for pr in pairs:
        ida, idb = pr["arm_a"]["arm"], pr["arm_b"]["arm"]
        pa, pb = pilot_panels[ida], pilot_panels[idb]
        rms = math.sqrt(float(np.mean(np.concatenate(
            [(pa[i] - pb[i]).ravel() for i in range(len(pa))]) ** 2)))
        g4["within_pair"].append({
            "pair": pr["pair"], "rms_panel_change": rms,
            "share_gap": pr["share_gap_b_minus_a"],
            "phi_gap": PHI_B - PHI_A,
            "realized_state_share_a": realized[ida]["slow"],
            "realized_state_share_b": realized[idb]["slow"],
            "realized_state_share_gap": realized[idb]["slow"] - realized[ida]["slow"],
            "pilot_field_a": float(np.mean([r["recovery_b_only"] for r in pilot_field[ida]])),
            "pilot_field_b": float(np.mean([r["recovery_b_only"] for r in pilot_field[idb]])),
            "non_degenerate": bool(rms > 1e-6 and abs(pr["share_gap_b_minus_a"]) > 1e-6),
        })
    tgt_levels = [t for _, t in PAIR_TARGETS]
    by_target_card, by_target_field = [], []
    for pr in pairs:
        ida, idb = pr["arm_a"]["arm"], pr["arm_b"]["arm"]
        by_target_card.append(0.5 * (pilot_card_point[ida]["attenuation"]
                                     + pilot_card_point[idb]["attenuation"]))
        by_target_field.append(0.5 * (
            float(np.mean([r["recovery_b_only"] for r in pilot_field[ida]]))
            + float(np.mean([r["recovery_b_only"] for r in pilot_field[idb]]))))
    anchor_card = pilot_card_point[ANCHOR_ARM[0]]["attenuation"]
    anchor_field = float(np.mean([r["recovery_b_only"] for r in pilot_field[ANCHOR_ARM[0]]]))
    card_levels = [anchor_card] + by_target_card
    field_levels = [anchor_field] + by_target_field
    g4["across_target"] = {
        "levels_desc_by_design": ["A1anc(pred .8272)"] + [f"{t:g}" for t in tgt_levels],
        "pilot_card_attenuation": card_levels,
        "pilot_field_recovery": field_levels,
        "card_strictly_decreasing": bool(all(card_levels[i] > card_levels[i + 1]
                                             for i in range(len(card_levels) - 1))),
        "field_strictly_decreasing": bool(all(field_levels[i] > field_levels[i + 1]
                                              for i in range(len(field_levels) - 1))),
    }
    g4["frame_channel_centred_residual_max"] = frame_residual_max
    g4["realized_share_dev_abs_max"] = float(max(
        max(abs(realized[a["arm"]][k] - m.arm_shares(a["share"], a["w_int_arm"])[k])
            for k in m.arm_shares(a["share"], a["w_int_arm"]))
        for a in arms
    ))
    g4["criterion"] = (
        "across the four designed attenuation levels the pilot card attenuation AND "
        "the pilot field recovery are both STRICTLY DECREASING (the lever is live on "
        "both channels, per prediction); within every pair the emitted panels differ "
        "(RMS > 1e-6) and the composition contrast is non-degenerate (share gap > 0); "
        "realized variance shares within 0.01 absolute of design"
    )
    g4["pass"] = bool(
        g4["across_target"]["card_strictly_decreasing"]
        and g4["across_target"]["field_strictly_decreasing"]
        and all(r["non_degenerate"] for r in g4["within_pair"])
        and g4["realized_share_dev_abs_max"] <= 0.01
    )
    gates["G4c_prime"] = g4

    # ---- G2c': power (rule 2)
    g2: dict[str, Any] = {"per_pair": [], "ladder": []}
    pilot_d: dict[str, np.ndarray] = {}
    for pr in pairs:
        ida, idb = pr["arm_a"]["arm"], pr["arm_b"]["arm"]
        fa = np.array([r["recovery_b_only"] for r in pilot_field[ida]])
        fb = np.array([r["recovery_b_only"] for r in pilot_field[idb]])
        pilot_d[pr["pair"]] = fa - fb
    for n_worlds in ESCALATION_LADDER:
        rows = []
        for pr in pairs:
            sd = float(np.std(pilot_d[pr["pair"]], ddof=1))
            rows.append({"pair": pr["pair"], "pilot_paired_sd": sd,
                         "mde": mde_paired(sd, n_worlds),
                         "meets": bool(mde_paired(sd, n_worlds) <= MDE_TARGET)})
        g2["ladder"].append({"n_worlds": n_worlds, "per_pair": rows,
                             "max_mde": float(max(r["mde"] for r in rows)),
                             "all_meet": bool(all(r["meets"] for r in rows))})
    chosen = next((lv["n_worlds"] for lv in g2["ladder"] if lv["all_meet"]), None)
    g2["worlds_selected"] = int(chosen if chosen is not None else ESCALATION_LADDER[-1])
    g2["escalated"] = bool(chosen is not None and chosen != ESCALATION_LADDER[0])
    g2["short_at_max"] = bool(chosen is None)
    g2["per_pair"] = [
        {"pair": pr["pair"],
         "pilot_paired_diffs": [float(x) for x in pilot_d[pr["pair"]]],
         "pilot_paired_sd": float(np.std(pilot_d[pr["pair"]], ddof=1)),
         "mde_at_selected": mde_paired(float(np.std(pilot_d[pr["pair"]], ddof=1)),
                                       g2["worlds_selected"]),
         "equivalence_margin_m_k_pilot": max(EQUIV_FLOOR, mde_paired(
             float(np.std(pilot_d[pr["pair"]], ddof=1)), g2["worlds_selected"]))}
        for pr in pairs
    ]
    g2["criterion"] = (
        "MDE(80%, alpha=.05, paired, n) for the within-pair field difference <= 0.020 "
        "in ALL THREE pairs; escalate 32->64 once; still short at 64 -> RUN and TIER "
        "the claims (registered)"
    )
    g2["pass"] = True   # registered: shortfall does not block the run, it tiers claims
    g2["power_met"] = bool(not g2["short_at_max"])
    gates["G2c_prime"] = g2

    # ---- G3c': rule 11 satisfiability with directions + rule 13 spec
    n_sel = g2["worlds_selected"]
    g3: dict[str, Any] = {"b_draws": B_BOOT, "seed": MASTER_SEED,
                          "b_draws_stability": B_BOOT_HIGH, "clauses": []}
    card_se = {}
    for a in arms:
        _, bt = m.bootstrap_card(pilot_card[a["arm"]], 400, MASTER_SEED)
        card_se[a["arm"]] = float(np.std(bt["r_card_b_raw"], ddof=1))
    # projected half-width of a within-pair MEASURED attenuation difference at n_sel
    proj_pair_hw = {}
    for pr in pairs:
        ida, idb = pr["arm_a"]["arm"], pr["arm_b"]["arm"]
        se_pair = math.sqrt(card_se[ida] ** 2 + card_se[idb] ** 2)   # conservative: unpaired
        proj_pair_hw[pr["pair"]] = 1.96 * se_pair * math.sqrt(len(PILOT_WORLDS) / n_sel)
    d_se_proj = {pr["pair"]: float(np.std(pilot_d[pr["pair"]], ddof=1)) / math.sqrt(n_sel)
                 for pr in pairs}
    g3["projected_pair_attenuation_halfwidth"] = proj_pair_hw
    g3["projected_D_k_se"] = d_se_proj
    g3["clauses"] = [
        {"lean": "G1c'", "clause": "within-pair MEASURED card attenuation difference "
                                   "95% CI inside +/-0.005",
         "direction": "two-sided (equivalence)",
         "satisfiable": bool(max(proj_pair_hw.values()) < MATCH_TOL_MEASURED),
         "note": "projected (conservative, unpaired) half-widths " + ", ".join(
             f"{k}={v:.8f}" for k, v in proj_pair_hw.items()) +
             f" against the +/-{MATCH_TOL_MEASURED} margin; the paired bootstrap "
             "actually used is strictly tighter"},
        {"lean": "L-1", "clause": "|D_k| 95% CI inside +/-m_k, m_k = max(0.020, MDE_k), "
                                  "3/3 pairs",
         "direction": "two-sided (equivalence, rule 4)",
         "satisfiable": bool(all(1.96 * v < max(EQUIV_FLOOR, mde_paired(
             float(np.std(pilot_d[p["pair"]], ddof=1)), n_sel))
             for p, v in zip(pairs, d_se_proj.values()))),
         "note": "projected 1.96*se(D_k) " + ", ".join(
             f"{k}={1.96 * v:.8f}" for k, v in d_se_proj.items()) +
             "; margins " + ", ".join(
             f"{p['pair']}={max(EQUIV_FLOOR, mde_paired(float(np.std(pilot_d[p['pair']], ddof=1)), n_sel)):.8f}"
             for p in pairs)},
        {"lean": "L-2", "clause": "D_k 95% CI excludes 0 in >=2/3 pairs AND all "
                                  "significant D_k share one sign",
         "direction": "two-sided per pair (exclusion); sign consistency is "
                      "deterministic given the significant set",
         "satisfiable": True,
         "note": "an exclusion clause is satisfiable for any non-degenerate CI; "
                 "pilot |D_k| means " + ", ".join(
                     f"{p['pair']}={float(np.mean(pilot_d[p['pair']])):+.8f}" for p in pairs)},
        {"lean": "PARTIAL-C", "clause": "exactly 1/3 significant, OR significant D_k "
                                        "with MIXED signs",
         "direction": "deterministic given L-2's significant set", "satisfiable": True,
         "note": "partition complement of L-1/L-2 as registered; RN-4 fixes the "
                 "L-1/L-2 simultaneous-fire reading BEFORE any hypothesis number"},
        {"lean": "L-3", "clause": "pooled q from log(field/lambda) on log(attenuation) "
                                  "over 6 K2b + 7 K2c arms: q > 1 with CI excluding 1",
         "direction": "one-sided in content (q > 1); evaluated on the two-sided 95% "
                      "CI as registered ('CI excluding 1'), with the one-sided 5th "
                      "percentile reported alongside",
         "satisfiable": True,
         "note": "13 points spanning predicted attenuation "
                 f"{min(list(pred_att_k2b) + [float(pred_by_arm[a]['r_card_b_pred_raw']) for a in arm_ids]):.6f}"
                 f"..{max(list(pred_att_k2b) + [float(pred_by_arm[a]['r_card_b_pred_raw']) for a in arm_ids]):.6f}; "
                 "K2b's own two-point reading already gives q ~ 2.4, far from 1"},
    ]
    g3["pass"] = bool(all(c["satisfiable"] for c in g3["clauses"]))
    gates["G3c_prime"] = g3

    # ---- G5c': hygiene
    build_mean = float(np.mean(build_times))
    per_arm_world = pilot_work_seconds / (len(arms) * len(PILOT_WORLDS))
    est_per_world_all_arms = build_mean * 2 + per_arm_world * len(arms)
    gates["G5c_prime"] = {
        "pass": True,
        "round_trip_parsing_everywhere": True,
        "float_precision": "round_trip",
        "stages_chunked": ["part0", "arms --worlds a-b (all 7 arms per chunk)", "finalize"],
        "background_jobs": 0,
        "monitors": 0,
        "world_build_seconds_mean": build_mean,
        "pilot_seconds": pilot_seconds,
        "shares_solve_seconds": shares_seconds,
        "stage_estimate_seconds": {
            "arms_per_world_index_all_7_arms": est_per_world_all_arms,
            "arms_total_at_selected_n": est_per_world_all_arms * n_sel,
            "recommended_chunk_worlds": 16,
            "stop_and_report_at": 2.0 * est_per_world_all_arms * n_sel,
        },
        "predicted_attenuation_desc": list(
            preds.sort_values("r_card_b_pred_raw", ascending=False)["arm"]
        ),
    }

    gates["part0_all_pass"] = bool(
        gates["G0c_prime"]["pass"] and gates["G1c_prime"]["pass"]
        and gates["G2c_prime"]["pass"] and gates["G3c_prime"]["pass"]
        and gates["G4c_prime"]["pass"] and gates["G5c_prime"]["pass"]
    )
    gates["stage_seconds"] = time.time() - t0
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2, default=str) + "\n",
                                    encoding="utf-8")
    (OUT / "part0_arms.json").write_text(
        json.dumps({"master_seed": MASTER_SEED, "worlds_selected": n_sel, "arms": arms,
                    "pairs": pairs}, indent=2, default=str) + "\n", encoding="utf-8")
    pd.DataFrame([{k: v for k, v in r.items() if k != "realized_shares"}
                  for a in arms for r in pilot_field[a["arm"]]]).to_csv(
        OUT / "part0_pilot_field.csv", index=False)
    write_part0_tables(gates, preds, pairs)
    write_manifest({"part0": time.time() - t0})
    print(json.dumps({
        "stage": "part0", "seconds": round(time.time() - t0, 3),
        "part0_all_pass": gates["part0_all_pass"],
        **{g: gates[g]["pass"] for g in ("G0c_prime", "G1c_prime", "G2c_prime",
                                         "G3c_prime", "G4c_prime", "G5c_prime")},
        "computed_shares": {p["pair"]: {"s_a": p["arm_a"]["share"], "s_b": p["arm_b"]["share"],
                                        "r_a": p["arm_a"]["predicted_attenuation"],
                                        "r_b": p["arm_b"]["predicted_attenuation"],
                                        "abs_diff": p["abs_predicted_difference"]}
                            for p in pairs},
        "worlds_selected": n_sel,
        "power_met": gates["G2c_prime"]["power_met"],
        "k2b_anchors_bit_exact": gates["G0c_prime"]["k2b_anchors"]["bit_exact"],
        "k2a_anchor_residual": gates["G0c_prime"]["k2a_anchor"]["max_abs_residual"],
        "stage_estimate": gates["G5c_prime"]["stage_estimate_seconds"],
    }, indent=2, default=str))


def write_part0_tables(gates: dict[str, Any], preds: pd.DataFrame,
                       pairs: list[dict[str, Any]]) -> None:
    lines: list[str] = []
    lines.append("### G1c' -- the COMPUTED shares and the designed identity\n")
    lines.append("| pair | target r | s_ka (phi .90) | r(P_ka) | s_kb (phi .98) | r(P_kb) | "
                 "|r(P_ka) - r(P_kb)| | matched (<=1e-12) | share gap |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for p in pairs:
        lines.append(
            f"| `{p['pair']}` | {p['target_attenuation']:g} | "
            f"{p['arm_a']['share']!r} | {p['arm_a']['predicted_attenuation']!r} | "
            f"{p['arm_b']['share']!r} | {p['arm_b']['predicted_attenuation']!r} | "
            f"{p['abs_predicted_difference']:.6e} | {p['matched_part0']} | "
            f"{p['share_gap_b_minus_a']:+.10f} |"
        )
    lines.append("\n### Part-0 point predictions (all 7 arms, computed before any world)\n")
    lines.append("| arm | role | share | phi | A (mu) | B (slow) | Cc (frame) | E (noise) | "
                 "rho_int pred | rho_cont pred | GAP pred | r(card->b) pred |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for _, r in preds.iterrows():
        lines.append(
            f"| `{r['arm']}` | {r['role']} | {r['share_design']:.12g} | {r['phi_slow']:g} | "
            f"{r['A_mu']:.8f} | {r['B_slow']:.8f} | {r['Cc_common']:.8f} | {r['E_noise']:.8f} | "
            f"{r['rho_interleaved_pred']:.10f} | {r['rho_contiguous_pred']:.10f} | "
            f"{r['gap_pred']:.10f} | {r['r_card_b_pred_raw']:.12f} |"
        )
    lines.append("\n### G4c' liveness (pilot worlds 9701-9702)\n")
    lines.append("| pair | panel RMS a vs b | share gap | realized state share a | b | "
                 "pilot field a | pilot field b | non-degenerate |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in gates["G4c_prime"]["within_pair"]:
        lines.append(
            f"| `{r['pair']}` | {r['rms_panel_change']:.8f} | {r['share_gap']:+.8f} | "
            f"{r['realized_state_share_a']:.8f} | {r['realized_state_share_b']:.8f} | "
            f"{r['pilot_field_a']:.8f} | {r['pilot_field_b']:.8f} | {r['non_degenerate']} |"
        )
    at = gates["G4c_prime"]["across_target"]
    lines.append("\n| designed level | pilot card attenuation | pilot field recovery |")
    lines.append("|---|---|---|")
    for lvl, c, f in zip(at["levels_desc_by_design"], at["pilot_card_attenuation"],
                         at["pilot_field_recovery"]):
        lines.append(f"| {lvl} | {c:.8f} | {f:.8f} |")
    lines.append("\n### G2c' power ladder (2-world pilot)\n")
    lines.append("| n worlds | pair | pilot paired sd | MDE(80%, .05, paired) | <= 0.020 |")
    lines.append("|---|---|---|---|---|")
    for lv in gates["G2c_prime"]["ladder"]:
        for r in lv["per_pair"]:
            lines.append(f"| {lv['n_worlds']} | `{r['pair']}` | {r['pilot_paired_sd']:.8f} | "
                         f"{r['mde']:.8f} | {r['meets']} |")
    lines.append("\n### G3c' clause satisfiability with DIRECTIONS (rule 11)\n")
    lines.append("| lean | clause | direction | satisfiable | note |")
    lines.append("|---|---|---|---|---|")
    for c in gates["G3c_prime"]["clauses"]:
        lines.append(f"| {c['lean']} | {c['clause']} | {c['direction']} | {c['satisfiable']} | "
                     f"{c['note']} |")
    (OUT / "part0_tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Stage: arms

def require_part0() -> dict[str, Any]:
    path = OUT / "gates.json"
    if not path.exists():
        raise SystemExit("REFUSED: Part 0 has not run (results/.../gates.json missing).")
    gates = json.loads(path.read_text(encoding="utf-8"))
    if not gates.get("part0_all_pass"):
        raise SystemExit("REFUSED: a Part-0 gate failed; no arms may run.")
    if not REPORT.exists():
        raise SystemExit("REFUSED: the Part-0 report has not been written to disk.")
    return gates


def run_arms(args: argparse.Namespace) -> None:
    gates = require_part0()
    m = k2b()
    n_worlds = int(gates["G2c_prime"]["worlds_selected"])
    lo, hi = (0, n_worlds - 1)
    if args.worlds:
        a, _, b = args.worlds.partition("-")
        lo, hi = int(a), int(b or a)
    if hi >= n_worlds:
        raise SystemExit(f"REFUSED: world range {lo}-{hi} exceeds n={n_worlds}")
    arms = arms_spec()
    t0 = time.time()
    card_acc: dict[str, list[pd.DataFrame]] = {a["arm"]: [] for a in arms}
    field_acc: dict[str, list[dict[str, Any]]] = {a["arm"]: [] for a in arms}
    weights = {a["arm"]: m.arm_weights(a["share"], a["w_int_arm"]) for a in arms}
    for world_index in range(lo, hi + 1):
        seed = world_seed_for(world_index)
        worlds = {phi: m.build_k2b_world(seed, phi) for phi in (PHI_A, PHI_B)}
        for a in arms:
            world = worlds[a["phi"]]
            frame, _ = m.card_channel_frame(world, weights[a["arm"]], seed)
            card_acc[a["arm"]].append(frame)
            field_acc[a["arm"]].append(
                run_field_world(a["arm"], world_index, world, weights[a["arm"]]))
        del worlds
        print(f"  world {world_index}: 7 arms  ({time.time() - t0:.1f}s)")
    tag = f"w{lo:03d}_{hi:03d}"
    for a in arms:
        aid = a["arm"]
        pd.concat(card_acc[aid], ignore_index=True).to_csv(
            OUT / f"arm_{aid}_card_{tag}.csv", index=False)
        pd.DataFrame(field_acc[aid]).to_csv(OUT / f"arm_{aid}_field_{tag}.csv", index=False)
    write_manifest({f"arms[{tag}]": time.time() - t0})
    print(json.dumps({"stage": "arms", "worlds": [lo, hi], "arms": [a["arm"] for a in arms],
                      "seconds": round(time.time() - t0, 3)}, indent=2))


def load_arm(aid: str, n_worlds: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    card = pd.concat([read_csv_rt(p) for p in sorted(OUT.glob(f"arm_{aid}_card_w*.csv"))],
                     ignore_index=True)
    field = pd.concat([read_csv_rt(p) for p in sorted(OUT.glob(f"arm_{aid}_field_w*.csv"))],
                      ignore_index=True).sort_values("world").reset_index(drop=True)
    if len(field) != n_worlds:
        raise SystemExit(f"REFUSED: arm {aid} has {len(field)} worlds, expected {n_worlds}")
    return card, field


# ---------------------------------------------------------------------------
# Stage: finalize

def run_finalize(args: argparse.Namespace) -> None:
    gates = require_part0()
    m = k2b()
    k2a = m.k2a()
    t0 = time.time()
    n_worlds = int(gates["G2c_prime"]["worlds_selected"])
    arms = arms_spec()
    pairs = json.loads((OUT / "part0_arms.json").read_text(encoding="utf-8"))["pairs"]
    preds = read_csv_rt(OUT / "part0_predictions.csv").set_index("arm")

    card_by_arm: dict[str, pd.DataFrame] = {}
    field_by_arm: dict[str, np.ndarray] = {}
    mixed_by_arm: dict[str, np.ndarray] = {}
    cells: list[dict[str, Any]] = []
    stability: list[dict[str, Any]] = []
    for a in arms:
        aid = a["arm"]
        card, field = load_arm(aid, n_worlds)
        card_by_arm[aid] = card
        field_by_arm[aid] = field["recovery_b_only"].to_numpy(float)
        mixed_by_arm[aid] = field["recovery_mixed"].to_numpy(float)
        point, boots = m.bootstrap_card(card, B_BOOT, MASTER_SEED)
        row: dict[str, Any] = {"arm": aid, "pair": a["pair"], "side": a["side"],
                               "role": a["role"], "share": a["share"], "phi": a["phi"],
                               "n_authors_pooled": int(len(card)), "n_worlds": int(len(field))}
        for key, pkey in (("gap", "gap_pred"), ("r_card_b_raw", "r_card_b_pred_raw")):
            lo, hi = k2a.ci_of(boots[key])
            row[key] = float(point[key])
            row[f"{key}_lo"], row[f"{key}_hi"] = lo, hi
            row[f"{key}_se"] = float(np.std(boots[key], ddof=1))
            row[f"{key}_pred"] = float(preds.loc[aid, pkey])
            row[f"{key}_err"] = float(point[key]) - float(preds.loc[aid, pkey])
            row[f"{key}_rel_err"] = row[f"{key}_err"] / float(preds.loc[aid, pkey])
            row[f"{key}_contains_pred"] = bool(lo <= float(preds.loc[aid, pkey]) <= hi)
        row["recovery_b_only_mean"] = float(np.mean(field_by_arm[aid]))
        row["recovery_b_only_sd"] = float(np.std(field_by_arm[aid], ddof=1))
        row["recovery_mixed_mean"] = float(np.mean(mixed_by_arm[aid]))
        row["recovery_mixed_sd"] = float(np.std(mixed_by_arm[aid], ddof=1))
        cells.append(row)
        print(f"  finalized {aid} ({time.time() - t0:.1f}s)")
    pd.DataFrame(cells).to_csv(OUT / "cells.csv", index=False)
    cell_by_arm = {r["arm"]: r for r in cells}

    # ---- world-block paired bootstrap over the field channel (SHARED picks)
    rng = np.random.default_rng(MASTER_SEED)
    pick = rng.integers(0, n_worlds, size=(B_BOOT, n_worlds))
    pick_hi = np.random.default_rng(MASTER_SEED).integers(
        0, n_worlds, size=(B_BOOT_HIGH, n_worlds))
    boot_field = {a["arm"]: field_by_arm[a["arm"]][pick].mean(axis=1) for a in arms}
    boot_mixed = {a["arm"]: mixed_by_arm[a["arm"]][pick].mean(axis=1) for a in arms}

    # ---- G1c' post-arms: the MEASURED matching
    g1_post: list[dict[str, Any]] = []
    for pr in pairs:
        ida, idb = pr["arm_a"]["arm"], pr["arm_b"]["arm"]
        pa, pb, ba, bb = bootstrap_card_pair(card_by_arm[ida], card_by_arm[idb],
                                             B_BOOT, MASTER_SEED)
        d_boot = ba["r_card_b_raw"] - bb["r_card_b_raw"]
        d_point = float(pa["r_card_b_raw"] - pb["r_card_b_raw"])
        lo, hi = k2a.ci_of(d_boot)
        inside = bool(-MATCH_TOL_MEASURED <= lo and hi <= MATCH_TOL_MEASURED)
        rec = {"pair": pr["pair"], "arm_a": ida, "arm_b": idb,
               "measured_attenuation_a": float(pa["r_card_b_raw"]),
               "measured_attenuation_b": float(pb["r_card_b_raw"]),
               "predicted_attenuation": pr["arm_a"]["predicted_attenuation"],
               "measured_difference": d_point, "ci": [lo, hi],
               "se": float(np.std(d_boot, ddof=1)),
               "margin": MATCH_TOL_MEASURED, "inside_margin": inside,
               "VOID": bool(not inside)}
        g1_post.append(rec)
        mc = k2a.mc_sd_of_endpoint(d_boot, B_BOOT, 0.025)
        dist = min(abs(MATCH_TOL_MEASURED - hi), abs(-MATCH_TOL_MEASURED - lo))
        if dist <= 2.0 * mc:
            _, _, ba2, bb2 = bootstrap_card_pair(card_by_arm[ida], card_by_arm[idb],
                                                 B_BOOT_HIGH, MASTER_SEED)
            d2 = ba2["r_card_b_raw"] - bb2["r_card_b_raw"]
            lo2, hi2 = k2a.ci_of(d2)
            v2 = bool(-MATCH_TOL_MEASURED <= lo2 and hi2 <= MATCH_TOL_MEASURED)
            stability.append({"scope": f"G1c'[{pr['pair']}]",
                              "clause": "measured within-pair attenuation diff CI inside +/-0.005",
                              "direction": "two-sided (equivalence)",
                              "boundary": MATCH_TOL_MEASURED,
                              "mc_sd_endpoint_B2000": mc, "distance_to_boundary": dist,
                              "verdict_B2000": inside, "verdict_B20000": v2,
                              "endpoints_B20000": [lo2, hi2],
                              "status": "STABLE" if inside == v2 else "BOUNDARY"})
    n_void = sum(r["VOID"] for r in g1_post)

    # ---- D_k, the link-free adjudication quantity
    d_rows: list[dict[str, Any]] = []
    for pr in pairs:
        ida, idb = pr["arm_a"]["arm"], pr["arm_b"]["arm"]
        d = field_by_arm[ida] - field_by_arm[idb]
        db = boot_field[ida] - boot_field[idb]
        lo, hi = k2a.ci_of(db)
        sd_real = float(np.std(d, ddof=1))
        mde_real = mde_paired(sd_real, n_worlds)
        mde_pilot = float(next(r["mde_at_selected"] for r in gates["G2c_prime"]["per_pair"]
                               if r["pair"] == pr["pair"]))
        m_k = max(EQUIV_FLOOR, mde_real)
        rec = {
            "pair": pr["pair"], "arm_a": ida, "arm_b": idb,
            "field_a": float(np.mean(field_by_arm[ida])),
            "field_b": float(np.mean(field_by_arm[idb])),
            "D_k": float(np.mean(d)), "ci": [lo, hi],
            "se": float(np.std(db, ddof=1)),
            "sd_paired_realized": sd_real,
            "mde_realized": mde_real, "mde_pilot": mde_pilot,
            "m_k_primary_realized": m_k,
            "m_k_second_pilot": max(EQUIV_FLOOR, mde_pilot),
            "abs_ci_inside_m_k": bool(-m_k <= lo and hi <= m_k),
            "abs_ci_inside_m_k_pilot_margin": bool(
                -max(EQUIV_FLOOR, mde_pilot) <= lo and hi <= max(EQUIV_FLOOR, mde_pilot)),
            "ci_excludes_zero": bool(lo > 0.0 or hi < 0.0),
            "sign": int(np.sign(np.mean(d))),
            "per_world_positive": int(np.sum(d > 0.0)),
            "paired_t_ci": [float(np.mean(d) - T_QUANTILES[n_worlds][0] * sd_real / math.sqrt(n_worlds)),
                            float(np.mean(d) + T_QUANTILES[n_worlds][0] * sd_real / math.sqrt(n_worlds))],
            "VOID": bool(next(r["VOID"] for r in g1_post if r["pair"] == pr["pair"])),
        }
        d_rows.append(rec)
        # rule 13 on both gated field clauses per pair
        db_hi = (field_by_arm[ida][pick_hi].mean(axis=1)
                 - field_by_arm[idb][pick_hi].mean(axis=1))
        mc = k2a.mc_sd_of_endpoint(db, B_BOOT, 0.025)
        dist_eq = min(abs(m_k - hi), abs(-m_k - lo))
        if dist_eq <= 2.0 * mc:
            lo2, hi2 = k2a.ci_of(db_hi)
            v2 = bool(-m_k <= lo2 and hi2 <= m_k)
            stability.append({"scope": f"L-1[{pr['pair']}]",
                              "clause": "|D_k| CI inside +/-m_k", "direction": "two-sided",
                              "boundary": m_k, "mc_sd_endpoint_B2000": mc,
                              "distance_to_boundary": dist_eq,
                              "verdict_B2000": rec["abs_ci_inside_m_k"],
                              "verdict_B20000": v2, "endpoints_B20000": [lo2, hi2],
                              "status": "STABLE" if rec["abs_ci_inside_m_k"] == v2 else "BOUNDARY"})
        dist_z = min(abs(lo), abs(hi))
        if dist_z <= 2.0 * mc:
            lo2, hi2 = k2a.ci_of(db_hi)
            v2 = bool(lo2 > 0.0 or hi2 < 0.0)
            stability.append({"scope": f"L-2[{pr['pair']}]",
                              "clause": "D_k CI excludes 0", "direction": "two-sided",
                              "boundary": 0.0, "mc_sd_endpoint_B2000": mc,
                              "distance_to_boundary": dist_z,
                              "verdict_B2000": rec["ci_excludes_zero"],
                              "verdict_B20000": v2, "endpoints_B20000": [lo2, hi2],
                              "status": "STABLE" if rec["ci_excludes_zero"] == v2 else "BOUNDARY"})
    pd.DataFrame(d_rows).to_csv(OUT / "pair_differences.csv", index=False)

    valid = [r for r in d_rows if not r["VOID"]]
    n_sig = sum(r["ci_excludes_zero"] for r in valid)
    sig_signs = sorted({r["sign"] for r in valid if r["ci_excludes_zero"]})
    l1 = {
        "prior": 0.40,
        "pairs_valid": len(valid), "pairs_void": n_void,
        "pairs_inside_margin": sum(r["abs_ci_inside_m_k"] for r in valid),
        "clause": "3/3 pairs |D_k| CI inside +/-m_k",
        "fires": bool(len(valid) == 3 and all(r["abs_ci_inside_m_k"] for r in valid)),
        "fires_pilot_margin_reading": bool(
            len(valid) == 3 and all(r["abs_ci_inside_m_k_pilot_margin"] for r in valid)),
    }
    l2 = {
        "prior": 0.45,
        "pairs_significant": n_sig, "signs_of_significant": sig_signs,
        "clause": ">=2/3 pairs D_k CI excludes 0 AND all significant D_k share one sign",
        "fires": bool(n_sig >= 2 and len(sig_signs) == 1 and len(valid) == 3),
        "direction": ("positive (phi .90 arm recovers MORE)" if sig_signs == [1]
                      else "negative (phi .98 arm recovers MORE)" if sig_signs == [-1]
                      else "mixed/none"),
    }
    partial_c = {
        "clause": "exactly 1/3 significant, OR significant D_k with MIXED signs",
        "fires": bool(len(valid) == 3 and (n_sig == 1 or (n_sig >= 2 and len(sig_signs) > 1))),
    }

    # ---- L-3: the pooled log-log slope (DESCRIPTIVE-TO-LEAN, no branch weight)
    k2b_pred = read_csv_rt(K2B_OUT / "part0_predictions.csv").set_index("arm")
    k2b_cells = read_csv_rt(K2B_OUT / "cells.csv").set_index("arm")
    k2b_field = {a: read_csv_rt(K2B_OUT / f"arm_{a}_field.csv").sort_values("world")[
        "recovery_b_only"].to_numpy(float) for a in K2B_PRIMARY_ARMS}
    order_c = tuple(a["arm"] for a in arms)
    x_pred = np.log(np.array(
        [float(k2b_pred.loc[a, "r_card_b_pred_raw"]) for a in K2B_PRIMARY_ARMS]
        + [float(preds.loc[a, "r_card_b_pred_raw"]) for a in order_c]))
    x_meas = np.log(np.array(
        [float(k2b_cells.loc[a, "r_card_b_raw"]) for a in K2B_PRIMARY_ARMS]
        + [float(cell_by_arm[a]["r_card_b_raw"]) for a in order_c]))
    l3 = l3_pooled_q(x_pred, k2b_field, field_by_arm, K2B_PRIMARY_ARMS, order_c,
                     K2B_LAMBDA, B_BOOT, MASTER_SEED)
    l3["prior"] = 0.70
    l3["x_convention"] = ("PRIMARY: Part-0 PREDICTED attenuation (deterministic x, no "
                          "errors-in-variables dilution). SECOND READING: measured card "
                          "attenuation, x fixed at its point value.")
    l3_meas = l3_pooled_q(x_meas, k2b_field, field_by_arm, K2B_PRIMARY_ARMS, order_c,
                          K2B_LAMBDA, B_BOOT, MASTER_SEED)
    l3["second_reading_measured_x"] = {k: v for k, v in l3_meas.items() if k != "q_boot"}
    l3_lam1 = l3_pooled_q(x_pred, k2b_field, field_by_arm, K2B_PRIMARY_ARMS, order_c,
                          1.0, B_BOOT, MASTER_SEED)
    l3["lambda_invariance_check"] = {
        "q_at_lambda_k2b": l3["q"], "q_at_lambda_1": l3_lam1["q"],
        "abs_difference": abs(l3["q"] - l3_lam1["q"]),
        "note": "the OLS slope cannot depend on lambda (it shifts y by a constant); "
                "verified numerically",
    }
    l3["one_sided_lower95"] = float(np.percentile(l3["q_boot"], 5.0))
    l3["fires"] = bool(l3["clause_q_gt_1"] and l3["clause_ci_excludes_1"] and l3["q_ci"][0] > 1.0)
    q_boot = l3.pop("q_boot")
    mc_q = k2a.mc_sd_of_endpoint(q_boot, B_BOOT, 0.025)
    if min(abs(1.0 - l3["q_ci"][0]), abs(1.0 - l3["q_ci"][1])) <= 2.0 * mc_q:
        l3_hi = l3_pooled_q(x_pred, k2b_field, field_by_arm, K2B_PRIMARY_ARMS, order_c,
                            K2B_LAMBDA, B_BOOT_HIGH, MASTER_SEED)
        v2 = bool(l3_hi["q"] > 1.0 and l3_hi["q_ci"][0] > 1.0)
        stability.append({"scope": "L-3", "clause": "q > 1 with CI excluding 1",
                          "direction": "one-sided in content, two-sided CI",
                          "boundary": 1.0, "mc_sd_endpoint_B2000": mc_q,
                          "distance_to_boundary": min(abs(1.0 - l3["q_ci"][0]),
                                                      abs(1.0 - l3["q_ci"][1])),
                          "verdict_B2000": l3["fires"], "verdict_B20000": v2,
                          "endpoints_B20000": l3_hi["q_ci"],
                          "status": "STABLE" if l3["fires"] == v2 else "BOUNDARY"})

    if stability:
        pd.DataFrame(stability).to_csv(OUT / "rule13_stability.csv", index=False)
    boundary = [s for s in stability if s["status"] == "BOUNDARY"]

    # ---- verdict (RN-4's partition, fixed in Part 0)
    both_fire = bool(l1["fires"] and l2["fires"])
    if n_void >= 2:
        branch = "P1c_PRIME__MATCHING_FAILS__INSTRUMENT_QUESTION"
    elif both_fire:
        branch = "BOTH_FIRE__NO_REGISTERED_BRANCH"
    elif l1["fires"]:
        branch = "L-1"
    elif l2["fires"]:
        branch = "L-2"
    elif partial_c["fires"]:
        branch = "PARTIAL-C"
    else:
        branch = "NO_REGISTERED_BRANCH"

    pivots = {
        "P1c_prime": {"fires": bool(n_void >= 2),
                      "consequence": "attenuation algebra does not transfer at matched-pair "
                                     "precision -> instrument question returns to K2a'; no "
                                     "theory adjudication"},
        "P2c_prime": {"fires": bool(branch == "L-1"),
                      "consequence": "T4-simple-with-link registered in IDT; appendix G's "
                                     "slope claim REVISED to link curvature (planner)"},
        "P3c_prime": {"fires": bool(branch == "L-2"),
                      "consequence": "T4-reader-mediated (composition form) registered; "
                                     "constructive repair test is the next registration"},
        "P4c_prime": {"fires": bool(branch == "PARTIAL-C"),
                      "consequence": "K2d localization"},
    }

    slug_map = {
        "P1c_PRIME__MATCHING_FAILS__INSTRUMENT_QUESTION": "MATCHING_FAILS__INSTRUMENT_QUESTION",
        "BOTH_FIRE__NO_REGISTERED_BRANCH": "BOTH_FIRE__SIGNIFICANT_BUT_SUB_MATERIAL",
        "L-1": "L1__FIELD_IS_A_FUNCTION_OF_ATTENUATION__T4_SIMPLE_WITH_LINK",
        "L-2": "L2__COMPOSITION_SENSITIVE__T4_READER_MEDIATED",
        "PARTIAL-C": "PARTIAL_C__COMPOSITION_SENSITIVITY_NON_UNIFORM",
        "NO_REGISTERED_BRANCH": "NO_REGISTERED_BRANCH__REPORTED_AS_SUCH",
    }
    slug = slug_map[branch]
    slug += "__MATCH_" + ("EXACT" if n_void == 0 else f"VOID{n_void}")
    slug += "__L3_" + ("HOLD" if l3["fires"] else "MISS")

    # ---- descriptive companions
    descriptive = {
        "per_arm": {
            a["arm"]: {
                "share": a["share"], "phi": a["phi"], "role": a["role"],
                "predicted_attenuation": float(preds.loc[a["arm"], "r_card_b_pred_raw"]),
                "measured_attenuation": cell_by_arm[a["arm"]]["r_card_b_raw"],
                "measured_attenuation_ci": [cell_by_arm[a["arm"]]["r_card_b_raw_lo"],
                                            cell_by_arm[a["arm"]]["r_card_b_raw_hi"]],
                "attenuation_rel_err": cell_by_arm[a["arm"]]["r_card_b_raw_rel_err"],
                "attenuation_contains_pred": cell_by_arm[a["arm"]]["r_card_b_raw_contains_pred"],
                "card_gap": cell_by_arm[a["arm"]]["gap"],
                "card_gap_pred": cell_by_arm[a["arm"]]["gap_pred"],
                "card_gap_contains_pred": cell_by_arm[a["arm"]]["gap_contains_pred"],
                "field_b_only": float(np.mean(field_by_arm[a["arm"]])),
                "field_b_only_ci": list(k2a.ci_of(boot_field[a["arm"]])),
                "field_mixed": float(np.mean(mixed_by_arm[a["arm"]])),
                "field_mixed_ci": list(k2a.ci_of(boot_mixed[a["arm"]])),
                "mixed_minus_b": float(np.mean(mixed_by_arm[a["arm"]] - field_by_arm[a["arm"]])),
                "mixed_minus_b_ci": list(k2a.ci_of(boot_mixed[a["arm"]] - boot_field[a["arm"]])),
            } for a in arms
        },
        "anchor_continuity": {
            "K2c_A1anc_field_b_only": float(np.mean(field_by_arm[ANCHOR_ARM[0]])),
            "K2c_A1anc_field_ci": list(k2a.ci_of(boot_field[ANCHOR_ARM[0]])),
            "K2b_A1_field_b_only": float(np.mean(k2b_field["A1"])),
            "difference": float(np.mean(field_by_arm[ANCHOR_ARM[0]]) - np.mean(k2b_field["A1"])),
            "note": "same design cell (.02, .90), DIFFERENT seed lineage (20260817/"
                    "m4k2c-world vs 20260816/m4k2b-world); a continuity reading only, "
                    "no gate",
        },
        "card_positive_control": {
            "arms_attenuation_containing_prediction": int(sum(
                cell_by_arm[a["arm"]]["r_card_b_raw_contains_pred"] for a in arms)),
            "arms_gap_containing_prediction": int(sum(
                cell_by_arm[a["arm"]]["gap_contains_pred"] for a in arms)),
            "n_arms": len(arms),
            "max_abs_attenuation_rel_err": float(max(
                abs(cell_by_arm[a["arm"]]["r_card_b_raw_rel_err"]) for a in arms)),
            "note": "not a registered gate in K2c (K2a/K2b certified the instrument); "
                    "reported for continuity",
        },
    }

    decision = {
        "leg": "M4-K2c",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "banner": BANNER,
        "master_seed": MASTER_SEED,
        "worlds_per_arm": n_worlds,
        "n_authors_per_world": int(len(m.layout()["author_ids"])),
        "n_retained": int(len(m.layout()["retained_idx"])),
        "arms": arms,
        "G1c_prime_post_arms": {"per_pair": g1_post, "pairs_void": n_void,
                                "pass": bool(n_void == 0)},
        "pair_differences": d_rows,
        "leans": {"L-1": l1, "L-2": l2, "PARTIAL-C": partial_c, "L-3": l3},
        "branch": branch,
        "pivots": pivots,
        "rule13": {"triggered": len(stability), "boundary": len(boundary),
                   "records": stability},
        "descriptive": descriptive,
        "verdict_slug": slug,
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2, default=str) + "\n",
                                       encoding="utf-8")
    write_manifest({"finalize": time.time() - t0})
    print(json.dumps({k: v for k, v in decision.items()
                      if k not in ("rule13", "descriptive", "arms")}, indent=2, default=str))
    print(f"rule13 triggered={len(stability)} boundary={len(boundary)}")


def write_manifest(stage_times: dict[str, float]) -> None:
    path = OUT / "manifest.json"
    prior = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    prior.setdefault("leg", "M4-K2c")
    prior.setdefault("banner", BANNER)
    prior.setdefault("script", "scripts/run_suica_m4_k2c_matched_pairs.py")
    prior.setdefault("master_seed", MASTER_SEED)
    prior.setdefault("worlds_per_arm_registered", WORLDS_PER_ARM)
    prior.setdefault("pilot_worlds", list(PILOT_WORLDS))
    prior.setdefault("pair_targets", [list(p) for p in PAIR_TARGETS])
    prior.setdefault("phi_a", PHI_A)
    prior.setdefault("phi_b", PHI_B)
    prior.setdefault("anchor_arm", list(ANCHOR_ARM))
    prior.setdefault("b_boot", B_BOOT)
    prior.setdefault("b_boot_high", B_BOOT_HIGH)
    prior.setdefault("python", sys.version)
    prior.setdefault("numpy", np.__version__)
    prior.setdefault("pandas", pd.__version__)
    prior.setdefault("stage_seconds", {})
    prior["stage_seconds"].update(stage_times)
    prior["updated_utc"] = datetime.now(UTC).isoformat()
    path.write_text(json.dumps(prior, indent=2, default=str) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, choices=("part0", "arms", "finalize"))
    parser.add_argument("--worlds", default=None, help="world range 'a-b' (chunking)")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.stage == "part0":
        run_part0(args)
    elif args.stage == "arms":
        run_arms(args)
    else:
        run_finalize(args)


if __name__ == "__main__":
    main()
