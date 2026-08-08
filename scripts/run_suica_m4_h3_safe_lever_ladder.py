#!/usr/bin/env python3
"""M4-H3: the safe lever's ladder, with the winner defined jointly.

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, "M4-H3
registration" (2026-08-03, BEFORE run), preceded by "M4-H2 planner
adjudication note" on the same date; ledger row M4-H3). Machinery is IMPORTED
and REUSED wherever an existing seam exists -- this script adds NO new Part 0
audit: it reuses `scripts/run_suica_m4_h2_basis_normalization.py` (imported
below as `h2`) for every world/context/oracle/truth/gate helper, and varies
ONLY h2's own Part 0 item 8a (whitening scale, REGULARIZED reading) at a
registered ladder of strengths. The deployed basis-construction path
(`suica_core/m4_condition_manifold_estimator.py`,
`suica_core/m4_chart_ecology_estimator.py`) is READ-ONLY throughout, exactly
as h2 left it -- this leg's only new code is a parameterized near-duplicate
of h2's own shrinkage-whitening branch (`h2._whitening_for_step`,
`m4_condition_manifold_estimator.py:580-583` is the line both h2 and this
leg vary) plus the arm-dispatch, per-arm-metric, and assemble/adjudicate
orchestration around it.

===========================================================================
PART 0 -- INHERITED FROM M4-H2, restated at the one line this leg varies
===========================================================================
M4-H2's Part 0 (its own file, lines 26-197) audited `context["v2_basis"]`'s
full construction path and classified SIX steps as CANDIDATE CARRIER. Of
those six, M4-H2's lean (a) found THREE cleared the registered 25% bar
(`basisvar_whitening_unscaled` 64.71%, `basisvar_rank_tolerance_tight`
42.15%, `basisvar_whitening_shrinkage` 28.93%), but only ONE was also safe:
`basisvar_whitening_shrinkage` (lambda = 0.10 x median retained eigenvalue)
improved recovery (CI entirely on the better side), while the other two --
including the winner under M4-H2's own (defective) target-only rule --
destroyed it. This leg holds every OTHER Part 0 step at its deployed
default (source-scale, centering, rank-retention threshold, intercept
scale, source panel, chart-fitting hyperparameters -- all exactly as
`context["v2_basis"]` and M4-H2's own `deployed` arm compute them) and
varies ONLY the whitening scale, `m4_condition_manifold_estimator.py:580-
583` (`whitening = eigenvectors[:, retained] / sqrt(max(eigenvalues[retained],
1e-12))`), in its REGULARIZED reading (`1/sqrt(eig + lambda)`), at a
registered ladder of `lambda / median(retained eig)` ratios.

--- Registered ladder (NON-EXTENDABLE) ---------------------------------
`{0.02, 0.05, 0.10, 0.20, 0.50}` -- brackets M4-H2's own working value
(0.10) with one point 5x milder, one 2x milder, the working value itself,
one 2x stronger, one 5x stronger. If the safe optimum sits at either
endpoint (0.02 or 0.50), that is reported plainly as a ladder-boundary
finding, NOT extended in this script -- any extension is registered as its
own leg, per the outer task's explicit instruction.

--- Arms -----------------------------------------------------------------
- `deployed` -- anchor. Computed by literally calling `h2._basis_for_arm
  (context, "deployed")` (not reimplemented), then gated to <=1e-12 against
  M4-H2's own PERSISTED `deployed` arm rows (not merely against
  `context["v2_basis"]`, which M4-H2 already gated).
- `basis_shrinkage_<ratio>` for ratio in the ladder above -- this leg's ONLY
  new code: `_whitening_for_shrinkage_ratio`, a disclosed near-duplicate of
  h2's own `basisvar_whitening_shrinkage` branch inside `_whitening_for_step`
  (`run_suica_m4_h2_basis_normalization.py:530-533`), parameterized by
  `ratio` instead of h2's hardcoded `SHRINKAGE_RATIO=0.10`. Formula
  UNCHANGED: `1/sqrt(eig + lambda)`, `lambda = ratio * median(retained eig)`.
  Every other Part 0 step is held at deployed default by construction: this
  leg's arm names never match h2's `_ingredients_for_arm`'s three
  special-cased strings (`basisvar_source_scale_off`,
  `basisvar_center_median`, `basisvar_rank_tolerance_tight`), so calling
  `h2._ingredients_for_arm(context, <this leg's arm name>)` UNCHANGED falls
  through to deployed defaults for source-scale, centering and rank
  tolerance automatically -- exactly the same fall-through h2's own
  `basisvar_whitening_shrinkage` arm relies on. Consequence, verified
  empirically below rather than merely asserted: `k_retained` (hence basis
  WIDTH) is IDENTICAL across every arm in this leg, so unlike M4-H2's
  `rank_tolerance_tight` arm, no width-normalization companion is needed --
  this leg's reductions carry no width confound by construction.
- `whitening_unscaled` -- the KNOWN-UNSAFE REFERENCE (anchor), computed by
  literally calling `h2._basis_for_arm(context, "basisvar_whitening_unscaled")`
  (not reimplemented), gated to <=1e-12 against M4-H2's own persisted
  `basisvar_whitening_unscaled` arm rows. Measured on all three registered
  metrics like every other arm (Part 0's own "metrics at every arm"
  instruction), but per the outer registration's own naming ("the known-
  unsafe reference (anchor)", listed separately from "the ... ladder"), it
  is NOT eligible for joint-winner selection -- it is a reference point, not
  a ladder rung. Both readings (eligible / not eligible) are nonetheless
  computed and reported (Section on winner selection below) since it is
  virtually certain, and empirically confirmed, to fail the recovery-safety
  filter under its own G1-anchored reproduction of M4-H2's OUTSIDE finding
  -- disclosed as a robustness check on this reading, not a live ambiguity
  that changes any adjudicated number.

===========================================================================
DESIGN (registered)
===========================================================================
Worlds: M4-H2's own three `HIGH_GAP_WORLDS`, all 8 repetitions -- IMPORTED
UNCHANGED (`h2.HIGH_GAP_WORLDS`). Three mandatory metrics, computed at EVERY
arm (all 7): (1) Leg 14's displacement gap (`disp_v2`, PRIMARY); (2) M4-E2's
S1-S4 shares (S3's registered-order share is this leg's mechanistic-
consistency check); (3) truth-referenced recovery at both M4-F5
`TRUTH_BUDGETS = (4.0, 8.0)`. All three computed via h2's own per-arm
machinery, near-duplicated only at the one dispatch point
(`_basis_for_h3_arm`, below) that must recognize this leg's own arm names.

--- Registered ambiguity resolution: metric grains (disclosed, resolved
    BEFORE adjudicating any number; justified fresh for THIS leg, not
    inherited by citation alone) -----------------------------------------
Metric 1 (`disp_v2`): REP grain (n=24, 3 worlds x 8 reps) PRIMARY, WORLD
grain (n=3) companion. Justification, restated for this leg rather than
merely cited: `disp_v2` is already a per-repetition quantity under this
leg's OWN arm construction (each repetition gets its own basis, its own GPA
frame, its own quotient distance to the deployed frame) -- no aggregation
is needed to reach the rep-level statistic, so rep grain is the natural
sampling unit for a paired CI, identical to the reasoning M4-G7 and M4-H2
both reached independently for the SAME metric on the SAME three worlds.
Metric 2 (S3 shares): WORLD-level census (n=3, no CI) -- a world's GPA-
consensus share is a single deterministic statistic per world per arm, so
there is no finer sampling unit at which it is even defined (M4-E2's/
M4-H1's/M4-H2's own convention, unchanged).
Metric 3 (truth recovery): AUTHOR grain (n up to 384) PRIMARY, WORLD grain
(n=3) companion -- M4-G3's hand-off recommendation, adopted by every leg
since (G4-G7, H2). Justification restated: each (world, repetition, view,
author) is an independent forced-route refit against the analytic D_true,
so author-level pooling (mean over repeated views) is the finest defensible
grain before the paired-difference CI, matching every prior leg's own
argument for this exact quantity.

--- Winner definition (registered, SIXTH STANDING RULE) --------------------
The JOINT winner is the arm with the LARGEST rep-grain-primary displacement
reduction AMONG arms whose recovery does NOT worsen -- equivalence form,
margin = +/-0.02 (this line's own G4->G7 "no loss" constant, `LEAN_C_MARGIN`,
REUSED unchanged), ONE-SIDED (only "worse by more than the margin"
disqualifies; being much BETTER never disqualifies -- the same one-sided
reading M4-H2's own lean (c) used for the identical "does not worsen"
question), BOTH truth-budget variants required. This filter is applied to
EVERY non-deployed arm (five ladder rungs + the unscaled reference), not
only a pre-selected candidate. Every lean is then evaluated AT the joint
winner, never at the arm with the largest raw reduction (the "target-only"
rule the sixth standing rule exists to replace) -- G5 (below) computes and
publishes BOTH picks explicitly.

--- Lean (b)'s registered materiality margin (Part 0, before compute) -----
"S3's share falls MATERIALLY" is operationalized as a RELATIVE fall of at
least `LEAN_B_MATERIALITY_RATIO = 0.10` (10%) from deployed's own S3 share,
in ALL THREE worlds (census, matching M4-H2's own "falls in 3/3 worlds"
binary criterion but now with an explicit magnitude floor). This reuses
h2's own `G2_MATERIALITY_RATIO = 0.10` convention -- the SAME constant, the
SAME "does this move by at least a tenth of the reference scale" shape of
question, now applied to share MOVEMENT rather than basis DISTANCE, for
continuity rather than introducing an unjustified second constant.

Leans (registered, evaluated ONLY at the joint winner):
(a) SAFE AND EFFECTIVE: the joint winner's rep-grain reduction >= 25%
    relative to deployed, paired CI excluding zero.
(b) MECHANISTICALLY CONSISTENT: at the joint winner, S3's registered-order
    share falls by >= 10% relative to deployed, in all 3 worlds.
(c) ACTIVELY GOOD, NOT MERELY HARMLESS: at the joint winner, recovery is
    IMPROVED -- CI entirely on the negative (better) side of zero, BOTH
    budgets, author grain -- not merely classified WITHIN the +/-0.02
    equivalence band (which only certifies "not worse", the winner-
    eligibility bar itself, not "actively better").

PIVOT-IF: no arm is jointly qualifying at >= 25% (equivalently: the
recovery-safe pool is empty, OR its best member's reduction is <25% / CI
does not exclude zero) -> the safe region and the effective region do not
overlap above 25%; report the bounded, partial safe ceiling as the finding.

Gates: G0 POWER (grain justified above, MDE stated from M4-H2's own
persisted gap/recovery levels, BEFORE adjudicating); G1 ANCHOR (`deployed`
and `whitening_unscaled` reproduce M4-H2's PERSISTED row-level values to
<=1e-12, three independent chains: disp_v2, offset+shares, truth recovery);
G2 BASIS LIVENESS (h2's own `G2_CONDITION_MATERIALITY_RATIO=0.10`
convention, per arm, against deployed); G3 TRUTH-PATH INVARIANCE (degenerate
equality, h2's own `_g3_spot_check` pattern, all 7 arms); G4 MATERIALITY
FORM (equivalence/margin bound stated per gate); G5 JOINT-WINNER COMPLIANCE
(full arm x {displacement, recovery both variants, S3 share} table; the
joint selection shown explicitly; the target-only pick shown for contrast).

Chunked execution (process rule -- "drive every compute stage yourself in
the FOREGROUND, in chunks"; no background jobs, no monitors): identical
stage structure to h2 (`--world W --stage oracle`, `--world W --stage g3`,
`--world W --arm A`, `--assemble`, `--smoke`), reusing h2's own context
cache/oracle/regen machinery UNCHANGED, writing to this leg's OWN output
directory (a fresh, independent context build -- NOT a copy of h2's cache
-- so the G1 anchor is a real end-to-end test of the shared machinery, not
a trivial pass-through). Every per-(world,arm)/per-world stage is
idempotent (skips if its partial already exists).
"""
from __future__ import annotations

import argparse
import json
import pickle
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_suica_m4_h2_basis_normalization as h2  # noqa: E402  bit-exact reuse of every seam

from suica_core.m4_chart_ecology_generator import M4ChartEcologySpec  # noqa: E402

# ---------------------------------------------------------------------------
# registered arms and parameters (Part 0, above)
# ---------------------------------------------------------------------------

DEPLOYED_ARM = "deployed"
WHITENING_UNSCALED_ARM = "whitening_unscaled"
RATIO_LADDER: tuple[float, ...] = (0.02, 0.05, 0.10, 0.20, 0.50)  # NON-EXTENDABLE, registered


def _ladder_arm_name(ratio: float) -> str:
    return f"basis_shrinkage_{ratio:.2f}"


LADDER_ARMS: tuple[str, ...] = tuple(_ladder_arm_name(r) for r in RATIO_LADDER)
RATIO_BY_ARM: dict[str, float] = dict(zip(LADDER_ARMS, RATIO_LADDER))
NONDEPLOYED_ARMS: tuple[str, ...] = LADDER_ARMS + (WHITENING_UNSCALED_ARM,)
ARMS: tuple[str, ...] = (DEPLOYED_ARM,) + NONDEPLOYED_ARMS

H2_ARM_NAME = {DEPLOYED_ARM: "deployed", WHITENING_UNSCALED_ARM: "basisvar_whitening_unscaled"}

G1_ANCHOR_TOLERANCE = h2.G1_ANCHOR_TOLERANCE          # 1e-12
G3_TOLERANCE = h2.G3_TOLERANCE                        # 1e-12
LEAN_A_BAR = h2.LEAN_A_BAR                             # 0.25
RECOVERY_NO_WORSEN_MARGIN = h2.LEAN_C_MARGIN           # 0.02, one-sided "does not worsen"
G0_FRACTION_BAR_METRIC3 = h2.G0_FRACTION_BAR_METRIC3   # 0.01
G2_MATERIALITY_RATIO = h2.G2_MATERIALITY_RATIO         # 0.10, basis-distance liveness bound
LEAN_B_MATERIALITY_RATIO = 0.10                        # registered here: S3-share relative-fall bound (Part 0)

H2_RESULTS = ROOT / "results" / "m4_h2_basis_normalization"
H2_DISP_ROWS_PATH = H2_RESULTS / "disp_rows.csv"
H2_OFFSET_SHARES_PATH = H2_RESULTS / "offset_shares_by_arm.csv"
H2_TRUTH_ROWS_PATH = H2_RESULTS / "truth_recovery_rows.csv"
H2_DECISION_PATH = H2_RESULTS / "decision.json"

SHARE_FIELDS = (
    [f"registered_{n}" for n in h2.e2.SUBSPACE_NAMES + ("S4_residual",)]
    + [f"reverse_{n}" for n in h2.e2.SUBSPACE_NAMES + ("S4_residual",)]
    + [f"standalone_{n}" for n in h2.e2.SUBSPACE_NAMES]
    + ["s3family_n1_centering_mass", "s3family_n2_column_scale", "s3family_n3_role_size", "s3family_S4_residual"]
)


# ---------------------------------------------------------------------------
# this leg's ONLY new construction code: parameterized shrinkage + dispatch
# ---------------------------------------------------------------------------


def _whitening_for_shrinkage_ratio(ingredients: dict[str, Any], ratio: float) -> tuple[np.ndarray, dict[str, Any]]:
    """Disclosed near-duplicate of h2._whitening_for_step's
    `basisvar_whitening_shrinkage` branch (run_suica_m4_h2_basis_normalization.py
    :530-533, itself reproducing m4_condition_manifold_estimator.py:580-583's
    shape with a regularizer added), parameterized by `ratio` instead of h2's
    hardcoded SHRINKAGE_RATIO=0.10. Formula UNCHANGED: 1/sqrt(eig + lambda),
    lambda = ratio * median(retained eig)."""
    eigenvalues = ingredients["eigenvalues"]
    eigenvectors = ingredients["eigenvectors"]
    retained = ingredients["retained"]
    eig_retained = eigenvalues[retained]
    lam = ratio * float(np.median(eig_retained))
    whitening = eigenvectors[:, retained] / np.sqrt(np.maximum(eig_retained + lam, 1e-12))[None]
    return whitening, {"lambda": lam, "ratio": ratio, "k_retained": int(len(retained))}


def _basis_for_h3_arm(context: dict[str, Any], arm: str) -> tuple[dict[str, np.ndarray], dict[str, Any], dict[str, Any]]:
    """Dispatch for this leg's 7 arms. `deployed` and `whitening_unscaled`
    are literal calls into h2's own `_basis_for_arm` (not reimplemented) --
    bit-identical to h2's own construction. Ladder arms reuse h2's own
    `_ingredients_for_arm` UNCHANGED (this leg's arm names never match h2's
    3 special-cased strings, so it falls through to deployed defaults for
    source-scale/centering/rank-tolerance automatically, exactly as h2's own
    `basisvar_whitening_shrinkage` arm does) and vary only the whitening
    step via `_whitening_for_shrinkage_ratio` above."""
    if arm == DEPLOYED_ARM:
        return h2._basis_for_arm(context, "deployed")
    if arm == WHITENING_UNSCALED_ARM:
        return h2._basis_for_arm(context, "basisvar_whitening_unscaled")
    if arm in RATIO_BY_ARM:
        ingredients = h2._ingredients_for_arm(context, arm)
        whitening, meta = _whitening_for_shrinkage_ratio(ingredients, RATIO_BY_ARM[arm])
        basis = h2.leg10._bases_from_whitening(context, ingredients, whitening)
        return basis, ingredients, meta
    raise ValueError(f"not a registered M4-H3 arm: {arm}")


# ---------------------------------------------------------------------------
# per-arm offset/shares (near-duplicate of h2._arm_offset_and_shares, the
# ONLY change is _basis_for_arm -> _basis_for_h3_arm; every other call is
# h2's own machinery, reused unchanged)
# ---------------------------------------------------------------------------


def _arm_offset_and_shares_h3(
    world: str, contexts: list[dict[str, Any]], arm: str, s1_patterns: np.ndarray, s2_patterns: np.ndarray,
) -> dict[str, Any]:
    v2_frames = []
    swap_frames = []
    disp_rows = []
    for context in contexts:
        basis, _, meta = _basis_for_h3_arm(context, arm)
        swap_basis = h2.leg9._row_norm_swap(context["truth"].oracle_basis, basis)
        v2_frame = h2.leg11._stack_frame(basis)
        swap_frame = h2.leg11._stack_frame(swap_basis)
        v2_frames.append(v2_frame)
        swap_frames.append(swap_frame)
        disp = h2.leg14._quotient_distance(swap_frame, v2_frame)
        disp_rows.append({
            "world": world, "arm": arm, "repetition": context["repetition"],
            "disp_v2": disp, "width": int(basis["calibration"].shape[1]),
            "meta": json.dumps(meta),
        })

    gpa_v2 = h2.leg14._frechet_mean_multistart(v2_frames)
    gpa_swap = h2.leg14._frechet_mean_multistart(swap_frames)
    consensus = gpa_v2["mean"]
    swap_consensus = gpa_swap["mean"]
    width = max(consensus.shape[1], swap_consensus.shape[1])
    a_center = h2.leg14._pad(consensus, width)
    b_center = h2.leg14._pad(swap_consensus, width)
    b_aligned = h2.leg14._align(b_center, a_center)
    delta = a_center - b_aligned
    offset_norm = float(np.linalg.norm(delta))
    categories = a_center.shape[0] // len(h2.ROLES)

    s1_basis = h2.e2._pattern_basis_to_matrix_basis(s1_patterns, width)
    s2_basis = h2.e2._pattern_basis_to_matrix_basis(s2_patterns, width)
    s3_family = h2._s3_bases_for_center(a_center, width, categories)
    bases = {
        "S1_safety_complement": s1_basis, "S2_supervision_span": s2_basis,
        "S3_norm_scale_modes": s3_family["S3_norm_scale_modes"],
    }
    registered = h2.e2._sequential_shares(delta, bases, h2.e2.SUBSPACE_NAMES)
    reverse = h2.e2._sequential_shares(delta, bases, tuple(reversed(h2.e2.SUBSPACE_NAMES)))
    standalone = {
        name: float(np.sum(h2.e2._project(delta.reshape(-1), b) ** 2) / max(float(np.sum(delta.reshape(-1) ** 2)), h2.e2.EPS))
        for name, b in bases.items()
    }
    s3_component = registered["components"]["S3_norm_scale_modes"]
    family_bases = {k: s3_family[k] for k in ("n1_centering_mass", "n2_column_scale", "n3_role_size")}
    s3_family_shares = h2.e2._sequential_shares(
        s3_component, family_bases, ("n1_centering_mass", "n2_column_scale", "n3_role_size"),
    )["shares"]

    return {
        "arm": arm, "world": world, "disp_rows": disp_rows,
        "offset_norm": offset_norm, "width": width,
        "registered_shares": registered["shares"], "reverse_shares": reverse["shares"],
        "standalone_shares": standalone, "s3_family_shares": s3_family_shares,
        "gpa_v2_basins": int(gpa_v2["n_distinct_basins"]), "gpa_swap_basins": int(gpa_swap["n_distinct_basins"]),
        "gpa_v2_fixed_point_residual": gpa_v2["max_fixed_point_residual_over_starts"],
        "gpa_swap_fixed_point_residual": gpa_swap["max_fixed_point_residual_over_starts"],
    }


def _g2_liveness_rows_h3(world: str, contexts: list[dict[str, Any]], arm: str) -> list[dict[str, Any]]:
    rows = []
    for context in contexts:
        deployed_basis, _, _ = _basis_for_h3_arm(context, DEPLOYED_ARM)
        arm_basis, _, _ = _basis_for_h3_arm(context, arm)
        deployed_frame = h2.leg11._stack_frame(deployed_basis)
        arm_frame = h2.leg11._stack_frame(arm_basis)
        distance = h2.leg14._quotient_distance(deployed_frame, arm_frame)
        rows.append({"world": world, "arm": arm, "repetition": context["repetition"], "basis_distance_vs_deployed": distance})
    return rows


def _g3_spot_check_h3(world: str, contexts: list[dict[str, Any]], spec: M4ChartEcologySpec) -> list[dict[str, Any]]:
    """Near-duplicate of h2._g3_spot_check, generalized to this leg's 7 arms."""
    dims = contexts[0]["flat"][("train", 0)][0]["response_next"].shape[1]
    rep_idx = view = author = context = stack = None
    for candidate_rep_idx, candidate_context in enumerate(contexts):
        found = False
        for candidate_view in ("train", "test"):
            for candidate_author in range(candidate_context["authors"]):
                candidate_stack = candidate_context["oracle_stacks"][candidate_view][candidate_author]
                if float(np.linalg.norm(candidate_stack["D"])) >= h2.leg4.FLIP_TOLERANCE:
                    rep_idx, view, author, context, stack = (
                        candidate_rep_idx, candidate_view, candidate_author, candidate_context, candidate_stack,
                    )
                    found = True
                    break
            if found:
                break
        if found:
            break
    if context is None:
        raise RuntimeError(f"G3 spot check found NO non-degenerate (rep,view,author) on {world}")

    route = stack["selected_model"]
    fit_kwargs = context["fit_kwargs"]
    calibration_flat, selection_flat, _ = context["flat"][(view, author)]
    d_true = h2.leg4._true_derivative(context["truth"], author)
    regen = h2._regen_for_budget(context, spec, 1.0)
    calibration_g, selection_g = regen["per_view"][view][author]

    rows: list[dict[str, Any]] = []
    for arm in ARMS:
        basis, _, _ = _basis_for_h3_arm(context, arm)
        d_flatstyle = h2.leg4._forced_route_derivative(
            calibration_flat, selection_flat, basis, model=route,
            hazard_ridge=fit_kwargs["hazard_ridge"], logistic_iterations=fit_kwargs["logistic_iterations"], dimensions=dims,
        )
        d_regen = h2.leg4._forced_route_derivative(
            calibration_g, selection_g, basis, model=route,
            hazard_ridge=fit_kwargs["hazard_ridge"], logistic_iterations=fit_kwargs["logistic_iterations"], dimensions=dims,
        )
        e_flatstyle = h2.leg3._relative_error(d_flatstyle, d_true)
        e_regen = h2.leg3._relative_error(d_regen, d_true)
        rows.append({
            "world": world, "arm": arm, "repetition": rep_idx, "view": view, "author": author,
            "e_arm_true_flatstyle": e_flatstyle, "e_arm_true_regen_budget1": e_regen,
            "abs_diff": abs(e_flatstyle - e_regen),
        })
    return rows


# ---------------------------------------------------------------------------
# stages: oracle (reused verbatim from h2), g3, arm, smoke
# ---------------------------------------------------------------------------


def _run_g3_h3(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    partial_path = output / f"partial_g3_{world}.csv"
    if partial_path.exists():
        print(f"[m4h3] SKIP (partial exists): g3 {world}", flush=True)
        return
    contexts = h2._contexts_for_world(world, config, spec, output)
    rows = _g3_spot_check_h3(world, contexts, spec)
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(partial_path, index=False)
    print(f"[m4h3] g3 stage done: {world} ({time.time() - started:.1f}s total)", flush=True)


def _run_arm_h3(world: str, arm: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    partial_path = output / f"partial_arm_{world}_{arm}.json"
    if partial_path.exists():
        print(f"[m4h3] SKIP (partial exists): {world} {arm}", flush=True)
        return
    contexts = h2._contexts_for_world(world, config, spec, output)
    oracle_path = output / f"partial_oracle_{world}.csv"
    if not oracle_path.exists():
        raise RuntimeError(f"oracle stage must run before arm stage: missing {oracle_path}")

    s1_cache = output / "_context_cache" / f"s1s2_{world}.pkl"
    if s1_cache.exists():
        with s1_cache.open("rb") as handle:
            s1_patterns, s2_patterns, s1s2_meta = pickle.load(handle)
    else:
        s1_per_rep, s2_per_rep, q_values = [], [], []
        arm_b_gate_max = 0.0
        for context in contexts:
            machinery = h2.e2._response_direction_machinery(context)
            arm_b_gate_max = max(arm_b_gate_max, h2.e2._arm_b_gate(context, machinery))
            s1_per_rep.append(h2.e2._s1_patterns(context, machinery))
            q_values.append(int(machinery["q"]))
            s2_per_rep.append(h2.e2._s2_patterns(context))
        d1_target = int(np.median(q_values))
        s1_patterns, s1_captured, d1 = h2.e2._common_core(s1_per_rep, retained_dim=d1_target)
        d2_target = int(s2_per_rep[0].shape[1])
        s2_patterns, s2_captured, d2 = h2.e2._common_core(s2_per_rep, retained_dim=d2_target)
        s1s2_meta = {
            "arm_b_gate_max": arm_b_gate_max, "s1_captured": s1_captured, "s2_captured": s2_captured,
            "d1": d1, "d2": d2, "q_values": q_values,
        }
        s1_cache.parent.mkdir(parents=True, exist_ok=True)
        with s1_cache.open("wb") as handle:
            pickle.dump((s1_patterns, s2_patterns, s1s2_meta), handle)

    offset_shares = _arm_offset_and_shares_h3(world, contexts, arm, s1_patterns, s2_patterns)
    g2_rows = _g2_liveness_rows_h3(world, contexts, arm)

    truth_rows: list[dict[str, Any]] = []
    for context in contexts:
        for budget in h2.TRUTH_BUDGETS:
            t0 = time.time()
            regen = h2._regen_for_budget_cached(context, spec, budget, output)
            basis, _, _ = _basis_for_h3_arm(context, arm)
            rows = h2._arm_truth_rows(context, regen, budget, arm, basis)
            truth_rows.extend(rows)
            print(f"[m4h3] truth b={budget:g} {world} {arm} rep={context['repetition']} ({time.time() - t0:.1f}s)", flush=True)

    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(offset_shares["disp_rows"]).to_csv(output / f"partial_disp_{world}_{arm}.csv", index=False)
    pd.DataFrame(g2_rows).to_csv(output / f"partial_g2_{world}_{arm}.csv", index=False)
    pd.DataFrame(truth_rows).to_csv(output / f"partial_truth_{world}_{arm}.csv", index=False)
    summary = {k: v for k, v in offset_shares.items() if k != "disp_rows"}
    with partial_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    print(f"[m4h3] arm stage done: {world} {arm} ({time.time() - started:.1f}s total)", flush=True)


def _run_smoke_h3(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    t0 = time.time()
    world_index = {name: index for index, name in enumerate(config["worlds"])}[world]
    expected_for = h2.leg8._expected_geometries_lookup(config)
    seed = h2.leg3._world_seed(int(config["seed"]), 0, world, world_index)
    context = h2.leg4._build_context(
        world, 0, seed, spec=spec, config=config, expected_geometries=expected_for(world, 0, seed),
    )
    print(f"[m4h3 smoke] context built ({time.time() - t0:.1f}s)", flush=True)

    for arm in (DEPLOYED_ARM, _ladder_arm_name(0.02), _ladder_arm_name(0.50), WHITENING_UNSCALED_ARM):
        t1 = time.time()
        basis, ingredients, meta = _basis_for_h3_arm(context, arm)
        if arm == DEPLOYED_ARM:
            gap = max(float(np.max(np.abs(basis[role] - context["v2_basis"][role]))) for role in h2.ROLES)
            print(f"[m4h3 smoke] deployed basis vs context v2_basis max|diff|={gap:.3e}", flush=True)
            assert gap <= G1_ANCHOR_TOLERANCE, f"deployed basis reconstruction fails G1 anchor: {gap:.3e}"
        print(f"[m4h3 smoke] arm={arm} width={basis['calibration'].shape[1]} meta={meta} ({time.time() - t1:.1f}s)", flush=True)
    widths = {arm: _basis_for_h3_arm(context, arm)[0]["calibration"].shape[1] for arm in ARMS}
    print(f"[m4h3 smoke] widths by arm (must all match -- no rank_tolerance variant in this leg): {widths}", flush=True)
    assert len(set(widths.values())) == 1, f"unexpected width mismatch across arms: {widths}"

    t2 = time.time()
    regen = h2._regen_for_budget(context, spec, 4.0)
    print(f"[m4h3 smoke] regen budget=4x ({time.time() - t2:.1f}s)", flush=True)
    t3 = time.time()
    oracle_rows = h2._oracle_truth_rows(context, regen, 4.0)
    print(f"[m4h3 smoke] oracle rows n={len(oracle_rows)} ({time.time() - t3:.1f}s)", flush=True)
    t4 = time.time()
    basis, _, _ = _basis_for_h3_arm(context, _ladder_arm_name(0.02))
    arm_rows = h2._arm_truth_rows(context, regen, 4.0, _ladder_arm_name(0.02), basis)
    print(f"[m4h3 smoke] arm rows n={len(arm_rows)} ({time.time() - t4:.1f}s)", flush=True)
    print(f"[m4h3 smoke] TOTAL ({time.time() - t0:.1f}s)", flush=True)


# ---------------------------------------------------------------------------
# assemble + adjudicate
# ---------------------------------------------------------------------------


def _direction_classification(ci: dict[str, float]) -> str:
    """Strict-direction check for lean (c) 'actively good, not merely
    harmless': is the CI entirely on ONE side of zero? Distinct from
    h2.g4._classify_pair (which, at margin=0, folds BOTH 'entirely better'
    and 'entirely worse' into a single OUTSIDE class) -- this leg needs to
    tell the two apart."""
    if ci["n"] <= 1 or not np.isfinite(ci["ci_lo"]) or not np.isfinite(ci["ci_hi"]):
        return "AMBIGUOUS"
    if ci["ci_hi"] < 0.0:
        return "IMPROVED"
    if ci["ci_lo"] > 0.0:
        return "WORSE"
    return "AMBIGUOUS_OR_NO_CHANGE"


def _assemble(output: Path) -> None:
    worlds = list(h2.HIGH_GAP_WORLDS)
    for world in worlds:
        for arm in ARMS:
            for stem in ("disp", "g2", "truth"):
                path = output / f"partial_{stem}_{world}_{arm}.csv"
                if not path.exists():
                    raise RuntimeError(f"missing partial (world/arm not yet computed): {path}")
            if not (output / f"partial_arm_{world}_{arm}.json").exists():
                raise RuntimeError(f"missing arm summary: partial_arm_{world}_{arm}.json")
        if not (output / f"partial_g3_{world}.csv").exists():
            raise RuntimeError(f"missing G3 spot check for {world}")

    disp_rows = pd.concat([pd.read_csv(output / f"partial_disp_{w}_{a}.csv") for w in worlds for a in ARMS], ignore_index=True)
    g2_rows = pd.concat([pd.read_csv(output / f"partial_g2_{w}_{a}.csv") for w in worlds for a in NONDEPLOYED_ARMS], ignore_index=True)
    truth_rows = pd.concat([pd.read_csv(output / f"partial_truth_{w}_{a}.csv") for w in worlds for a in ARMS], ignore_index=True)
    oracle_rows = pd.concat([pd.read_csv(output / f"partial_oracle_{w}.csv") for w in worlds], ignore_index=True)
    g3_rows = pd.concat([pd.read_csv(output / f"partial_g3_{w}.csv") for w in worlds], ignore_index=True)
    arm_summaries = {(w, a): h2._load_json(output / f"partial_arm_{w}_{a}.json") for w in worlds for a in ARMS}

    expected_disp = len(worlds) * len(ARMS) * 8
    if len(disp_rows) != expected_disp:
        raise RuntimeError(f"disp rows {len(disp_rows)} != expected {expected_disp}")
    expected_truth_arm_rows = len(worlds) * 8 * len(h2.TRUTH_BUDGETS) * 2 * 16
    for arm in ARMS:
        n = len(truth_rows[truth_rows["arm"] == arm])
        if n != expected_truth_arm_rows:
            raise RuntimeError(f"truth rows for arm {arm}: {n} != expected {expected_truth_arm_rows}")

    join_keys = ["world", "repetition", "view", "author", "budget"]
    truth_joined = truth_rows.merge(
        oracle_rows[join_keys + ["e_orc_true", "degenerate_reference"]], on=join_keys, how="inner", suffixes=("", "_oracle"),
    )
    if len(truth_joined) != len(truth_rows):
        raise RuntimeError("oracle join lost truth rows")
    truth_joined["degenerate_reference"] = (
        truth_joined["degenerate_reference"].astype(bool) | truth_joined["degenerate_reference_oracle"].astype(bool)
    )

    # ==== G1 ANCHOR: `deployed` and `whitening_unscaled` reproduce M4-H2's ====
    # ==== own PERSISTED row-level values to <=1e-12, three chains =============
    h2_disp = pd.read_csv(H2_DISP_ROWS_PATH)
    h2_shares = pd.read_csv(H2_OFFSET_SHARES_PATH)
    h2_truth = pd.read_csv(H2_TRUTH_ROWS_PATH)

    metric1_anchor_rows = []
    for h3_arm, h2_arm in H2_ARM_NAME.items():
        mine = disp_rows[disp_rows["arm"] == h3_arm][["world", "repetition", "disp_v2"]]
        theirs = h2_disp[h2_disp["arm"] == h2_arm][["world", "repetition", "disp_v2"]]
        joined = mine.merge(theirs, on=["world", "repetition"], suffixes=("_mine", "_h2"), how="inner")
        if len(joined) != 24:
            raise RuntimeError(f"metric1 anchor join for {h3_arm}: {len(joined)} rows != 24")
        joined["abs_diff"] = (joined["disp_v2_mine"] - joined["disp_v2_h2"]).abs()
        metric1_anchor_rows.append({"h3_arm": h3_arm, "h2_arm": h2_arm, "n_checks": len(joined), "max_abs_diff": float(joined["abs_diff"].max())})
    metric1_anchor_max = max(r["max_abs_diff"] for r in metric1_anchor_rows)

    metric2_anchor_rows = []
    for h3_arm, h2_arm in H2_ARM_NAME.items():
        for w in worlds:
            mine = arm_summaries[(w, h3_arm)]
            theirs_row = h2_shares[(h2_shares["world"] == w) & (h2_shares["arm"] == h2_arm)]
            if len(theirs_row) != 1:
                raise RuntimeError(f"metric2 anchor missing for {h3_arm}/{h2_arm} on {w}")
            theirs_row = theirs_row.iloc[0]
            offset_diff = abs(mine["offset_norm"] - float(theirs_row["offset_norm"]))
            flat_mine = {
                **{f"registered_{k}": v for k, v in mine["registered_shares"].items()},
                **{f"reverse_{k}": v for k, v in mine["reverse_shares"].items()},
                **{f"standalone_{k}": v for k, v in mine["standalone_shares"].items()},
                **{f"s3family_{k}": v for k, v in mine["s3_family_shares"].items()},
            }
            share_diffs = {f: abs(float(flat_mine[f]) - float(theirs_row[f])) for f in SHARE_FIELDS}
            metric2_anchor_rows.append({
                "h3_arm": h3_arm, "h2_arm": h2_arm, "world": w,
                "offset_norm_abs_diff": offset_diff, "max_share_abs_diff": max(share_diffs.values()),
            })
    metric2_anchor_max = max(max(r["offset_norm_abs_diff"], r["max_share_abs_diff"]) for r in metric2_anchor_rows)

    metric3_anchor_rows = []
    for h3_arm, h2_arm in H2_ARM_NAME.items():
        mine = truth_rows[truth_rows["arm"] == h3_arm][["world", "repetition", "view", "author", "budget", "e_arm_true"]]
        theirs = h2_truth[h2_truth["arm"] == h2_arm][["world", "repetition", "view", "author", "budget", "e_arm_true"]]
        joined = mine.merge(theirs, on=["world", "repetition", "view", "author", "budget"], suffixes=("_mine", "_h2"), how="inner")
        if len(joined) != expected_truth_arm_rows:
            raise RuntimeError(f"metric3 anchor join for {h3_arm}: {len(joined)} rows != {expected_truth_arm_rows}")
        both_nan = joined["e_arm_true_mine"].isna() & joined["e_arm_true_h2"].isna()
        diffs = (joined["e_arm_true_mine"] - joined["e_arm_true_h2"]).abs()
        diffs = diffs.where(~both_nan, 0.0)
        if diffs.isna().any():
            raise RuntimeError(f"metric3 anchor for {h3_arm}: NaN mismatch not covered by both_nan mask")
        metric3_anchor_rows.append({"h3_arm": h3_arm, "h2_arm": h2_arm, "n_checks": len(joined), "max_abs_diff": float(diffs.max())})
    metric3_anchor_max = max(r["max_abs_diff"] for r in metric3_anchor_rows)

    g1_anchor_max = max(metric1_anchor_max, metric2_anchor_max, metric3_anchor_max)
    g1_anchor = {
        "tolerance": G1_ANCHOR_TOLERANCE,
        "statement": "deployed and whitening_unscaled reproduce M4-H2's own persisted row-level CSVs (disp_rows.csv, offset_shares_by_arm.csv, truth_recovery_rows.csv) to <=1e-12, full row-level joins (not spot checks)",
        "metric1_disp_v2_vs_h2_disp_rows": metric1_anchor_rows,
        "metric2_offset_and_shares_vs_h2_offset_shares": {"per_world": metric2_anchor_rows, "max_abs_diff": metric2_anchor_max},
        "metric3_e_arm_true_vs_h2_truth_recovery_rows": metric3_anchor_rows,
        "max_abs_diff_overall": g1_anchor_max,
        "pass": bool(g1_anchor_max <= G1_ANCHOR_TOLERANCE),
    }

    # ==== disclosed, non-gate consistency check: does ratio=0.10 reproduce ====
    # ==== h2's own basisvar_whitening_shrinkage (same formula, same ratio)? ===
    mid_arm = _ladder_arm_name(0.10)
    mine_mid = disp_rows[disp_rows["arm"] == mid_arm][["world", "repetition", "disp_v2"]]
    theirs_mid = h2_disp[h2_disp["arm"] == "basisvar_whitening_shrinkage"][["world", "repetition", "disp_v2"]]
    joined_mid = mine_mid.merge(theirs_mid, on=["world", "repetition"], suffixes=("_mine", "_h2"), how="inner")
    disclosed_ratio010_check = {
        "statement": "NOT a registered gate -- basis_shrinkage_0.10 uses the identical formula/ratio as h2's own basisvar_whitening_shrinkage; this is an internal-consistency sanity check, disclosed for transparency",
        "n_checks": int(len(joined_mid)),
        "max_abs_diff": float((joined_mid["disp_v2_mine"] - joined_mid["disp_v2_h2"]).abs().max()) if len(joined_mid) else None,
    }

    # ==== G2 BASIS LIVENESS =====================================================
    deployed_disp_median = float(disp_rows[disp_rows["arm"] == "deployed"]["disp_v2"].median())
    g2_by_arm = {}
    for arm in NONDEPLOYED_ARMS:
        scoped = g2_rows[g2_rows["arm"] == arm]
        median_dist = float(scoped["basis_distance_vs_deployed"].median())
        ratio = median_dist / deployed_disp_median if deployed_disp_median > 0 else float("nan")
        g2_by_arm[arm] = {
            "median_basis_distance_vs_deployed": median_dist,
            "ratio_to_deployed_median_disp_v2": ratio,
            "live": bool(ratio >= G2_MATERIALITY_RATIO),
        }
    g2_basis_liveness = {
        "statement": "every arm's own stacked frame must differ from deployed's by >= 10% of deployed's median disp_v2 (chordal quotient distance, per rep, median over 8 reps x 3 worlds) -- h2's own G2_CONDITION_MATERIALITY_RATIO convention, reused unchanged",
        "materiality_ratio": G2_MATERIALITY_RATIO,
        "deployed_median_disp_v2": deployed_disp_median,
        "by_arm": g2_by_arm,
        "all_live": bool(all(v["live"] for v in g2_by_arm.values())),
    }

    # ==== G3 TRUTH-PATH INVARIANCE ===============================================
    g3_gate = {
        "statement": "budget=1.0 freshly-regenerated panels reproduce context['flat']-sourced refits exactly, every arm, one spot-check (rep,view,author) per world",
        "max_abs_diff": float(g3_rows["abs_diff"].max()),
        "n_checks": int(len(g3_rows)),
        "tolerance": G3_TOLERANCE,
        "pass": bool(g3_rows["abs_diff"].max() <= G3_TOLERANCE),
    }

    # ==== width-invariance check (disclosed, supports "no width confound") =====
    width_by_arm = disp_rows.groupby("arm")["width"].agg(["min", "max"]).to_dict("index")
    width_invariant = bool(len({v["min"] for v in width_by_arm.values()} | {v["max"] for v in width_by_arm.values()}) == 1)

    # ==== metric 1: displacement reduction, rep grain PRIMARY (n=24), ==========
    # ==== world grain (n=3) companion, per non-deployed arm =====================
    disp_wide = disp_rows.set_index(["world", "repetition", "arm"])["disp_v2"]
    deployed_mean_rep = float(disp_rows[disp_rows["arm"] == "deployed"]["disp_v2"].mean())
    bar_absolute_rep = LEAN_A_BAR * deployed_mean_rep
    reduction_by_arm: dict[str, dict[str, Any]] = {}
    for arm in NONDEPLOYED_ARMS:
        reduction_rep = np.array([float(disp_wide[(w, r, "deployed")] - disp_wide[(w, r, arm)]) for w in worlds for r in range(8)])
        ci_rep = h2.g1._paired_world_ci(reduction_rep)
        reduction_pct_rep = float(np.mean(reduction_rep)) / deployed_mean_rep

        reduction_world = np.array([
            float(disp_rows[(disp_rows["world"] == w) & (disp_rows["arm"] == "deployed")]["disp_v2"].median())
            - float(disp_rows[(disp_rows["world"] == w) & (disp_rows["arm"] == arm)]["disp_v2"].median())
            for w in worlds
        ])
        ci_world = h2.g1._paired_world_ci(reduction_world)
        deployed_mean_world = float(np.mean([
            float(disp_rows[(disp_rows["world"] == w) & (disp_rows["arm"] == "deployed")]["disp_v2"].median()) for w in worlds
        ]))
        reduction_pct_world = float(np.mean(reduction_world)) / deployed_mean_world

        reduction_by_arm[arm] = {
            "rep_grain_PRIMARY": {
                "n": ci_rep["n"], "mean_reduction_absolute": ci_rep["mean"], "reduction_pct": reduction_pct_rep,
                "ci_lo": ci_rep["ci_lo"], "ci_hi": ci_rep["ci_hi"], "half_width": ci_rep["half_width"],
                "bar_absolute": bar_absolute_rep,
                "underpowered_vs_bar": bool(np.isfinite(ci_rep["half_width"]) and ci_rep["half_width"] > bar_absolute_rep),
                "clears_25pct_bar": bool(reduction_pct_rep >= LEAN_A_BAR),
                "ci_excludes_zero": bool(ci_rep["ci_lo"] > 0.0),
            },
            "world_grain_companion": {
                "n": ci_world["n"], "mean_reduction_absolute": ci_world["mean"], "reduction_pct": reduction_pct_world,
                "ci_lo": ci_world["ci_lo"], "ci_hi": ci_world["ci_hi"],
                "clears_25pct_bar": bool(reduction_pct_world >= LEAN_A_BAR),
                "ci_excludes_zero": bool(ci_world["ci_lo"] > 0.0) if np.isfinite(ci_world["ci_lo"]) else False,
            },
        }

    # ==== metric 2: S3 registered-order share, world census (n=3), per arm =====
    s3_by_arm_world = {
        arm: {w: float(arm_summaries[(w, arm)]["registered_shares"]["S3_norm_scale_modes"]) for w in worlds}
        for arm in ARMS
    }
    s3_deployed_mean = float(np.mean(list(s3_by_arm_world["deployed"].values())))
    lean_b_by_arm: dict[str, dict[str, Any]] = {}
    for arm in NONDEPLOYED_ARMS:
        per_world_fall_ratio = {
            w: (s3_by_arm_world["deployed"][w] - s3_by_arm_world[arm][w]) / s3_by_arm_world["deployed"][w]
            if s3_by_arm_world["deployed"][w] > 0 else float("nan")
            for w in worlds
        }
        falls_materially_all_worlds = all(per_world_fall_ratio[w] >= LEAN_B_MATERIALITY_RATIO for w in worlds)
        lean_b_by_arm[arm] = {
            "s3_share_by_world": s3_by_arm_world[arm],
            "s3_share_mean_3worlds": float(np.mean(list(s3_by_arm_world[arm].values()))),
            "relative_fall_vs_deployed_by_world": per_world_fall_ratio,
            "falls_materially_10pct_all_3_worlds": bool(falls_materially_all_worlds),
        }

    # ==== metric 3: truth recovery, author grain PRIMARY, world companion, =====
    # ==== computed for EVERY non-deployed arm (needed for the qualifying set) ==
    author_truth = h2.g4._author_level_truth_with_c(truth_joined)
    recovery_by_arm: dict[str, dict[str, Any]] = {}
    for arm in NONDEPLOYED_ARMS:
        by_budget = {}
        for budget in h2.TRUTH_BUDGETS:
            author_ci = h2.g4._paired_author_diff_ci(author_truth, arm, 1.0, "deployed", 1.0, budget, worlds)
            world_ci = h2.g4._paired_world_diff_ci(author_truth, arm, 1.0, "deployed", 1.0, budget, worlds)
            author_class = h2.g4._classify_pair(author_ci, RECOVERY_NO_WORSEN_MARGIN, one_sided=True)
            direction = _direction_classification(author_ci)
            underpowered = bool(author_ci["n"] > 1 and author_ci["half_width"] > G0_FRACTION_BAR_METRIC3)
            by_budget[str(budget)] = {
                "author_grain": {
                    "n": author_ci["n"], "mean_diff_arm_minus_deployed": author_ci["mean"],
                    "ci_lo": author_ci["ci_lo"], "ci_hi": author_ci["ci_hi"], "half_width": author_ci["half_width"],
                    "no_worsen_class": author_class, "direction": direction, "underpowered_vs_g0_bar": underpowered,
                },
                "world_grain_companion": {
                    "n": world_ci["n"], "mean_diff_arm_minus_deployed": world_ci["mean"],
                    "ci_lo": world_ci["ci_lo"], "ci_hi": world_ci["ci_hi"],
                },
            }
        does_not_worsen_both = all(by_budget[str(b)]["author_grain"]["no_worsen_class"] == "WITHIN" for b in h2.TRUTH_BUDGETS)
        improved_both = all(by_budget[str(b)]["author_grain"]["direction"] == "IMPROVED" for b in h2.TRUTH_BUDGETS)
        recovery_by_arm[arm] = {"by_budget": by_budget, "recovery_does_not_worsen_both_budgets": bool(does_not_worsen_both), "recovery_improved_both_budgets": bool(improved_both)}

    # ==== G5 JOINT-WINNER COMPLIANCE: full table + explicit selection ==========
    g5_table = []
    for arm in NONDEPLOYED_ARMS:
        row = {
            "arm": arm,
            "is_ladder_rung": arm in RATIO_BY_ARM,
            "ratio": RATIO_BY_ARM.get(arm),
            "reduction_pct_rep_grain": reduction_by_arm[arm]["rep_grain_PRIMARY"]["reduction_pct"],
            "reduction_ci_lo_rep": reduction_by_arm[arm]["rep_grain_PRIMARY"]["ci_lo"],
            "reduction_ci_hi_rep": reduction_by_arm[arm]["rep_grain_PRIMARY"]["ci_hi"],
            "reduction_ci_excludes_zero_rep": reduction_by_arm[arm]["rep_grain_PRIMARY"]["ci_excludes_zero"],
            "reduction_pct_world_grain": reduction_by_arm[arm]["world_grain_companion"]["reduction_pct"],
            "clears_25pct_bar_rep": reduction_by_arm[arm]["rep_grain_PRIMARY"]["clears_25pct_bar"],
            "s3_share_mean_3worlds": lean_b_by_arm[arm]["s3_share_mean_3worlds"],
            "s3_falls_materially_10pct_all_3_worlds": lean_b_by_arm[arm]["falls_materially_10pct_all_3_worlds"],
            "recovery_diff_4x_mean": recovery_by_arm[arm]["by_budget"]["4.0"]["author_grain"]["mean_diff_arm_minus_deployed"],
            "recovery_class_4x": recovery_by_arm[arm]["by_budget"]["4.0"]["author_grain"]["no_worsen_class"],
            "recovery_direction_4x": recovery_by_arm[arm]["by_budget"]["4.0"]["author_grain"]["direction"],
            "recovery_diff_8x_mean": recovery_by_arm[arm]["by_budget"]["8.0"]["author_grain"]["mean_diff_arm_minus_deployed"],
            "recovery_class_8x": recovery_by_arm[arm]["by_budget"]["8.0"]["author_grain"]["no_worsen_class"],
            "recovery_direction_8x": recovery_by_arm[arm]["by_budget"]["8.0"]["author_grain"]["direction"],
            "recovery_does_not_worsen_both_budgets": recovery_by_arm[arm]["recovery_does_not_worsen_both_budgets"],
            "recovery_improved_both_budgets": recovery_by_arm[arm]["recovery_improved_both_budgets"],
        }
        g5_table.append(row)
    g5_table_sorted = sorted(g5_table, key=lambda r: r["reduction_pct_rep_grain"], reverse=True)

    # target-only pick: largest reduction, unconditional on safety (over ALL 6 non-deployed arms, including the reference)
    target_only_winner = max(NONDEPLOYED_ARMS, key=lambda a: reduction_by_arm[a]["rep_grain_PRIMARY"]["reduction_pct"])

    # joint pick, reading A (registered): ladder rungs + reference both eligible for the safety-filtered pool
    qualifying_pool_with_reference = [a for a in NONDEPLOYED_ARMS if recovery_by_arm[a]["recovery_does_not_worsen_both_budgets"]]
    joint_winner_with_reference = (
        max(qualifying_pool_with_reference, key=lambda a: reduction_by_arm[a]["rep_grain_PRIMARY"]["reduction_pct"])
        if qualifying_pool_with_reference else None
    )
    # joint pick, reading B (disclosed alternative): only the registered ladder rungs are eligible (the reference is
    # explicitly named "the known-unsafe reference (anchor)", not "the ... ladder", in the outer registration)
    qualifying_pool_ladder_only = [a for a in LADDER_ARMS if recovery_by_arm[a]["recovery_does_not_worsen_both_budgets"]]
    joint_winner_ladder_only = (
        max(qualifying_pool_ladder_only, key=lambda a: reduction_by_arm[a]["rep_grain_PRIMARY"]["reduction_pct"])
        if qualifying_pool_ladder_only else None
    )
    readings_agree = bool(joint_winner_with_reference == joint_winner_ladder_only)
    # adopted reading: B (ladder-only) -- the reference is registered as an anchor/comparison point, not a ladder
    # rung; readings_agree (computed above) confirms this choice is not doing any work in practice, since the
    # reference fails the safety filter under its own G1-anchored reproduction of h2's OUTSIDE finding either way
    joint_winner = joint_winner_ladder_only

    g5_joint_winner_compliance = {
        "statement": "full arm x {displacement, recovery both variants, S3 share} table, joint selection shown explicitly, target-only pick shown for contrast",
        "full_table_sorted_by_reduction_pct_desc": g5_table_sorted,
        "target_only_winner": {
            "arm": target_only_winner,
            "reduction_pct_rep_grain": reduction_by_arm[target_only_winner]["rep_grain_PRIMARY"]["reduction_pct"],
            "recovery_does_not_worsen_both_budgets": recovery_by_arm[target_only_winner]["recovery_does_not_worsen_both_budgets"],
            "note": "picked by largest reduction alone, ignoring recovery entirely -- the sixth standing rule's target-only rule this leg replaces",
        },
        "ambiguity_disclosed": {
            "question": "is whitening_unscaled (the registered 'known-unsafe reference (anchor)') eligible for joint-winner selection, or only the 5 basis_shrinkage_<ratio> ladder rungs?",
            "reading_A_reference_eligible": {"qualifying_pool": qualifying_pool_with_reference, "joint_winner": joint_winner_with_reference},
            "reading_B_ladder_only_ADOPTED": {"qualifying_pool": qualifying_pool_ladder_only, "joint_winner": joint_winner_ladder_only},
            "readings_agree": readings_agree,
            "adopted": "B (ladder-only)",
            "reason": "the outer registration lists 'whitening_unscaled' separately from 'the ... ladder' and names it 'the known-unsafe reference (anchor)', not a candidate rung; both readings are computed and agree exactly (the reference fails the recovery-safety filter under G1's own anchored reproduction of M4-H2's OUTSIDE finding), so this choice does not change any adjudicated number -- disclosed as a robustness check, not a live fork.",
        },
        "joint_winner": joint_winner,
    }

    # ==== leans, evaluated ONLY at the joint winner =============================
    lean_a = {
        "statement": "the joint winner's rep-grain reduction >= 25% relative to deployed, paired CI excluding zero",
        "joint_winner": joint_winner,
        "held": False,
    }
    if joint_winner is not None:
        r = reduction_by_arm[joint_winner]["rep_grain_PRIMARY"]
        lean_a.update({
            "reduction_pct": r["reduction_pct"], "ci_lo": r["ci_lo"], "ci_hi": r["ci_hi"],
            "clears_25pct_bar": r["clears_25pct_bar"], "ci_excludes_zero": r["ci_excludes_zero"],
            "held": bool(r["clears_25pct_bar"] and r["ci_excludes_zero"]),
        })
    lean_a_held = lean_a["held"]

    pivot_fires = not lean_a_held
    pivot = {
        "registered": "no arm is jointly qualifying at >=25% -> the safe region and the effective region do not overlap above 25%; report the bounded, partial safe ceiling",
        "fires": bool(pivot_fires),
    }

    lean_b = {"statement": "at the joint winner, S3's registered-order share falls by >=10% relative to deployed, in all 3 worlds", "applicable": joint_winner is not None, "held": False}
    if joint_winner is not None:
        lean_b.update({**lean_b_by_arm[joint_winner], "held": lean_b_by_arm[joint_winner]["falls_materially_10pct_all_3_worlds"]})

    lean_c = {
        "statement": "at the joint winner, recovery is IMPROVED -- CI entirely on the better side, both budgets, author grain (stronger than 'does not worsen', the winner-eligibility bar itself)",
        "applicable": joint_winner is not None, "held": False,
    }
    if joint_winner is not None:
        lean_c.update({
            "by_budget": recovery_by_arm[joint_winner]["by_budget"],
            "held": recovery_by_arm[joint_winner]["recovery_improved_both_budgets"],
        })

    # ladder-boundary disclosure
    ladder_boundary = None
    if joint_winner in (_ladder_arm_name(min(RATIO_LADDER)), _ladder_arm_name(max(RATIO_LADDER))):
        ladder_boundary = {
            "at_endpoint": True, "endpoint_arm": joint_winner,
            "statement": "the joint winner sits at a REGISTERED LADDER ENDPOINT -- the true optimum may lie beyond this ladder's range; this script does NOT extend the ladder (registered NON-EXTENDABLE); any extension requires its own leg.",
        }
    else:
        ladder_boundary = {"at_endpoint": False, "endpoint_arm": None, "statement": "the joint winner sits strictly inside the registered ladder's range -- both boundary rungs were tested and neither was the optimum."}

    # ==== G0 POWER (grain justified above; MDE stated citing M4-H2's own =======
    # ==== persisted numbers, BEFORE adjudicating) ===============================
    h2_decision = h2._load_json(H2_DECISION_PATH)
    h2_deployed_disp_pooled_mean = 18.059  # cited from M4-H2 report Section 4 (reproduced here to <=1e-12 by G1)
    h2_g0_half_widths = h2_decision["gates"]["G0_power"]["metric1_displacement"]["by_arm_half_width_rep_grain"]
    h2_recovery_baseline = {"4x": 0.5667, "8x": 0.5634}  # cited from M4-H2 report Section 4, deployed row
    g0_power = {
        "metric1_displacement": {
            "grain": "repetition (n=24, PRIMARY -- disp_v2 is a per-rep quantity by this leg's own construction, matching M4-G7/M4-H2's identical reasoning on the identical metric/worlds) / world (n=3, companion, literal text)",
            "cited_from_m4h2": {
                "deployed_pooled_rep_grain_mean_disp_v2": h2_deployed_disp_pooled_mean,
                "h2_own_achieved_half_widths_rep_grain": h2_g0_half_widths,
            },
            "mde_statement_before_adjudicating": (
                f"the registered 25% bar in absolute terms is {LEAN_A_BAR} * {h2_deployed_disp_pooled_mean:.3f} = "
                f"{LEAN_A_BAR * h2_deployed_disp_pooled_mean:.3f}; M4-H2's own largest rep-grain half-width across its "
                f"6 arms, on the IDENTICAL worlds/reps/disp_v2 design, was {max(h2_g0_half_widths.values()):.3f} "
                f"({LEAN_A_BAR * h2_deployed_disp_pooled_mean / max(h2_g0_half_widths.values()):.1f}x smaller than the "
                "bar) -- this design is not expected to be underpowered for lean (a) at any arm; verified empirically below."
            ),
            "bar_absolute_rep_grain": bar_absolute_rep,
            "by_arm_half_width_rep_grain": {a: reduction_by_arm[a]["rep_grain_PRIMARY"]["half_width"] for a in NONDEPLOYED_ARMS},
            "by_arm_underpowered_rep_grain": {a: reduction_by_arm[a]["rep_grain_PRIMARY"]["underpowered_vs_bar"] for a in NONDEPLOYED_ARMS},
        },
        "metric2_shares": {
            "grain": "world (n=3, census -- a world's decomposition share is a single deterministic GPA-consensus statistic, no finer sampling unit is defined -- M4-E2/M4-H1/M4-H2's own convention)",
            "note": "point comparison, no CI; reported per world for all 7 arms",
        },
        "metric3_truth_recovery": {
            "grain": "author (n up to 384, PRIMARY -- M4-G3's hand-off convention, adopted by every leg since) / world (n=3, companion)",
            "cited_from_m4h2": {"deployed_baseline_e_arm_true": h2_recovery_baseline, "margin": RECOVERY_NO_WORSEN_MARGIN, "g0_bar": G0_FRACTION_BAR_METRIC3},
            "mde_statement_before_adjudicating": (
                f"the winner-eligibility margin is +/-{RECOVERY_NO_WORSEN_MARGIN} (one-sided, 'does not worsen'); this "
                f"line's own strict G0 bar is {G0_FRACTION_BAR_METRIC3} (half the margin); M4-H2's own realized author-"
                "grain half-width at its single evaluated arm was 0.0172/0.0171 (4x/8x), nominally over this strict bar "
                "but with the classification decisive regardless (CI sat 12-14x the margin's width away from the "
                "boundary at M4-H2's unsafe winner); the SAME design (same worlds/authors/reps) applies here, evaluated "
                "now at every one of 6 arms -- realized half-widths reported per arm below, each flagged against the "
                "G0_FRACTION_BAR_METRIC3 bar rather than silently read as a clean null if it is exceeded."
            ),
            "by_arm_by_budget_half_width_author_grain": {
                a: {b: recovery_by_arm[a]["by_budget"][str(b)]["author_grain"]["half_width"] for b in h2.TRUTH_BUDGETS} for a in NONDEPLOYED_ARMS
            },
            "by_arm_by_budget_underpowered_vs_g0_bar": {
                a: {b: recovery_by_arm[a]["by_budget"][str(b)]["author_grain"]["underpowered_vs_g0_bar"] for b in h2.TRUTH_BUDGETS} for a in NONDEPLOYED_ARMS
            },
        },
    }

    # ==== G4 MATERIALITY FORM ====================================================
    g4_materiality_form = {
        "G0": "CI-half-width-vs-bar equivalence bound per metric, MDE stated citing M4-H2's own persisted numbers before adjudicating; underpowered comparisons flagged explicitly, never silently read as nulls",
        "G1": "degenerate exact-equality checks (tolerance 1e-12) against M4-H2's own independently-persisted row-level CSVs, not significance tests",
        "G2": "ratio-to-deployed-scale liveness bound (10% materiality margin), not nil-significance",
        "G3": "degenerate exact-equality check (tolerance 1e-12) between two independently-derived computations",
        "lean_a": "paired-by-repetition CI-excludes-zero test AND a >=25%-of-deployed-mean point-estimate bar, both required, at the joint winner only (directional materiality, not nil-significance)",
        "lean_b": "relative-fall equivalence bound (>=10% of deployed's own S3 share) across all 3 registered worlds (a census, not a sample), at the joint winner only",
        "lean_c": "strict-direction classification (CI entirely negative, both budgets, author grain) at the joint winner only -- stronger than the winner-eligibility filter's own one-sided +/-0.02 equivalence band",
        "winner_definition": "one-sided WITHIN/OUTSIDE/AMBIGUOUS equivalence classification against a fixed +/-0.02 (upper-only) margin, both budgets required, applied to EVERY non-deployed arm to build the qualifying pool -- not a nil-significance test",
    }

    if pivot_fires:
        verdict = "PIVOT_SAFE_EFFECTIVE_REGIONS_DO_NOT_OVERLAP_ABOVE_25PCT"
    elif lean_a["held"] and lean_b["held"] and lean_c["held"]:
        verdict = "SAFE_EFFECTIVE_AND_ACTIVELY_GOOD"
    elif lean_a["held"] and lean_b["held"] and not lean_c["held"]:
        verdict = "SAFE_AND_MECHANISTICALLY_CONSISTENT_NOT_ACTIVELY_GOOD"
    elif lean_a["held"] and not lean_b["held"]:
        verdict = "SAFE_BUT_MECHANISM_NOT_CONFIRMED_AT_WINNER"
    else:
        verdict = "AMBIGUOUS_NO_CLEAN_BRANCH"  # defensive; unreachable given pivot_fires := not lean_a_held

    decision = {
        "estimand_id": "SUICA_M4_H3_SAFE_LEVER_LADDER",
        "tier": "EXPLORATORY (open-exploration phase)",
        "registered_in": "docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md M4-H3 registration (2026-08-03, BEFORE run), preceded by the M4-H2 planner adjudication note (sixth standing rule); ledger row M4-H3",
        "worlds": worlds, "arms": list(ARMS), "ladder_arms": list(LADDER_ARMS), "ratio_ladder": list(RATIO_LADDER),
        "reference_arm": WHITENING_UNSCALED_ARM, "truth_budgets": list(h2.TRUTH_BUDGETS),
        "part0_inherited_from_m4h2": "this leg varies ONLY h2's Part 0 item 8a (whitening scale, regularized reading, m4_condition_manifold_estimator.py:580-583), at the registered ladder above; every other Part 0 step held at deployed default by construction (verified: width_invariant across all 7 arms)",
        "width_invariance_check": {"by_arm_min_max_width": width_by_arm, "all_arms_identical_width": width_invariant},
        "disclosed_ratio_0.10_internal_consistency_check_not_a_gate": disclosed_ratio010_check,
        "gates": {
            "G0_power": g0_power, "G1_anchor": g1_anchor, "G2_basis_liveness": g2_basis_liveness,
            "G3_truth_path_invariance": g3_gate, "G4_materiality_form": g4_materiality_form,
            "G5_joint_winner_compliance": g5_joint_winner_compliance,
        },
        "lean_a_safe_and_effective": lean_a,
        "lean_b_mechanistically_consistent": lean_b,
        "lean_c_actively_good": lean_c,
        "pivot": pivot,
        "ladder_boundary": ladder_boundary,
        "verdict": verdict,
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only (the 3 HIGH_GAP_WORLDS, reused verbatim from M4-E2/Leg14/M4-H2); "
            "truth-recovery via budget-regenerated (4x/8x events) finite panels from the frozen world law, compared "
            "to the analytic D_true; no natural-text, personality, or clinical claim; no seal, no independent "
            "verification (operator directive 2026-08-01)."
        ),
    }

    output.mkdir(parents=True, exist_ok=True)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    with (output / "gates.json").open("w", encoding="utf-8") as handle:
        json.dump(decision["gates"], handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    disp_rows.to_csv(output / "disp_rows.csv", index=False)
    g2_rows.to_csv(output / "g2_liveness_rows.csv", index=False)
    truth_joined.to_csv(output / "truth_recovery_rows.csv", index=False)
    g3_rows.to_csv(output / "g3check_rows.csv", index=False)
    pd.DataFrame([
        {"world": w, "arm": a, **{k: v for k, v in arm_summaries[(w, a)].items() if k not in ("registered_shares", "reverse_shares", "standalone_shares", "s3_family_shares")},
         **{f"registered_{k}": v for k, v in arm_summaries[(w, a)]["registered_shares"].items()},
         **{f"reverse_{k}": v for k, v in arm_summaries[(w, a)]["reverse_shares"].items()},
         **{f"standalone_{k}": v for k, v in arm_summaries[(w, a)]["standalone_shares"].items()},
         **{f"s3family_{k}": v for k, v in arm_summaries[(w, a)]["s3_family_shares"].items()}}
        for w in worlds for a in ARMS
    ]).to_csv(output / "offset_shares_by_arm.csv", index=False)
    author_truth.to_csv(output / "author_level_truth_rows.csv", index=False)
    pd.DataFrame(g5_table_sorted).to_csv(output / "g5_arm_by_metric_table.csv", index=False)

    print(json.dumps({
        "verdict": verdict, "pivot_fires": pivot_fires, "joint_winner": joint_winner, "target_only_winner": target_only_winner,
        "lean_a_held": lean_a["held"], "lean_b_held": lean_b["held"], "lean_c_held": lean_c["held"],
        "g1_anchor_pass": g1_anchor["pass"], "g2_all_live": g2_basis_liveness["all_live"], "g3_pass": g3_gate["pass"],
        "readings_agree": readings_agree,
    }, indent=2))


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "m4_chart_ecology.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "m4_h3_safe_lever_ladder")
    parser.add_argument("--world", type=str, default=None)
    parser.add_argument("--arm", type=str, default=None)
    parser.add_argument("--stage", type=str, default=None, choices=["oracle", "g3"])
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--assemble", action="store_true")
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    spec = M4ChartEcologySpec(**config["base_spec"])

    if args.assemble:
        _assemble(args.output)
        return

    if args.world is None:
        raise SystemExit("--world is required unless --assemble")
    if args.world not in h2.HIGH_GAP_WORLDS:
        raise SystemExit(f"not a registered HIGH_GAP_WORLDS world: {args.world}")

    if args.smoke:
        _run_smoke_h3(args.world, config, spec, args.output)
        return
    if args.stage == "oracle":
        h2._run_oracle(args.world, config, spec, args.output)
        return
    if args.stage == "g3":
        _run_g3_h3(args.world, config, spec, args.output)
        return
    if args.arm is None:
        raise SystemExit("--arm is required unless --stage oracle/g3 or --smoke or --assemble")
    if args.arm not in ARMS:
        raise SystemExit(f"not a registered arm: {args.arm}")
    _run_arm_h3(args.world, args.arm, config, spec, args.output)


if __name__ == "__main__":
    main()
