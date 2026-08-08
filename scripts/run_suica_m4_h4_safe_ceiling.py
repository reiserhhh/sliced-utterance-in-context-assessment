#!/usr/bin/env python3
"""M4-H4: where does the safe region end, and does the lever generalize?

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, "M4-H4
registration" (2026-08-03, BEFORE run), preceded by "M4-H3 planner
adjudication note" on the same date (seventh standing rule); ledger row
M4-H4). Machinery is IMPORTED and REUSED wherever an existing seam exists --
this script adds NO new Part 0 audit and NO new construction mechanism: it
reuses `scripts/run_suica_m4_h3_safe_lever_ladder.py` (imported below as
`h3`, which itself imports `scripts/run_suica_m4_h2_basis_normalization.py`
as `h2`) for every world/context/oracle/truth/gate helper, AND for the one
formula this line varies (`h3._whitening_for_shrinkage_ratio`, itself a
disclosed near-duplicate of `h2._whitening_for_step`'s
`basisvar_whitening_shrinkage` branch, formula UNCHANGED:
`1/sqrt(eig + lambda)`, `lambda = ratio * median(retained eig)`). The
deployed basis-construction path (`suica_core/m4_condition_manifold_
estimator.py`, `suica_core/m4_chart_ecology_estimator.py`) is READ-ONLY
throughout, exactly as h2/h3 left it. This leg's only new code is (1) arm-
dispatch plumbing for the four genuinely NEW ratios (1.0/2.0/4.0/8.0 --
`0.50` is the registered bridge/anchor point and is computed by a LITERAL
call into h3's own dispatch, not re-derived) and (2) the dual-winner
selection/adjudication orchestration the seventh standing rule requires.

===========================================================================
PART 0 -- INHERITED FROM H2 VIA H3, UNCHANGED. No new normalization,
scaling, centering or reference choice is introduced anywhere in this leg.
===========================================================================
H2's own Part 0 (its file, lines 26-197) audited `context["v2_basis"]`'s full
construction path and classified SIX steps as CANDIDATE CARRIER; H3 varied
ONLY one of them (item 8a, whitening scale, regularized reading) at a
registered ladder {0.02,0.05,0.10,0.20,0.50}, holding every other step at
deployed default. H4 varies the IDENTICAL, single step, by the IDENTICAL
formula, at a registered ladder EXTENSION upward: {0.50, 1.0, 2.0, 4.0, 8.0}.
Every other Part 0 step remains at deployed default by construction --
verified empirically, not merely asserted, exactly as H3 verified it: since
none of this leg's arm names match H2's `_ingredients_for_arm`'s three
special-cased strings, every ladder rung (old or new) falls through to
deployed defaults for source-scale/centering/rank-tolerance automatically
(the width-invariance check below re-confirms this for the four new rungs).

--- Registered ladder EXTENSION (arms) --------------------------------
`{0.50, 1.0, 2.0, 4.0, 8.0}` -- 0.50 is the shared BRIDGE POINT with H3's own
ladder (H3's own upper endpoint) and is carried here as an ANCHOR: computed
by a literal call into `h3._basis_for_h3_arm(context, "basis_shrinkage_0.50")`
(not re-derived), gated to <=1e-12 against H3's own PERSISTED
`basis_shrinkage_0.50` rows. The four new rungs (1.0, 2.0, 4.0, 8.0) are this
leg's only new compute, at ratios 2x/4x/8x/16x H3's own working value of
0.10 and 2x/4x/8x/16x the registered ladder's OWN prior top (0.50).
`whitening_unscaled` is retained UNCHANGED as the known-unsafe reference
(anchor): a literal call into `h3._basis_for_h3_arm(context,
"whitening_unscaled")`, gated to <=1e-12 against H3's own persisted
`whitening_unscaled` rows.

--- Disclosed superset on G1 (ambiguity, resolved, does not change the
    result either way) --------------------------------------------------
The outer registration's own G1 clause names only `basis_shrinkage_0.50` and
`whitening_unscaled` as anchors. This script ALSO anchors `deployed` against
H3's own persisted `deployed` rows (a THIRD chain beyond the registered two),
because (a) the Design paragraph says "reuse M4-H3's worlds, ANCHORS, arms
plumbing" (plural; H3 itself anchored `deployed` alongside `whitening_
unscaled`, and every leg in this line since M4-H2 has anchored `deployed`),
(b) `deployed` is the mandatory reference point for every metric this leg
computes (reduction, S3 fall, recovery diff are all defined AGAINST it), so
verifying it costs nothing and only STRENGTHENS G1 -- it cannot change which
arms pass or fail, since it adds a check rather than removing or loosening
one. Both readings (registered-literal: 2 chains; disclosed-superset: 3
chains) are reported; they necessarily agree on pass/fail (Section G1).

--- Winner definition (seventh standing rule) --------------------------
TWO winners are reported explicitly, both restricted to the five registered
ladder rungs (NOT `whitening_unscaled`, named separately as "the known-unsafe
reference" in both the H3 and H4 registrations -- the same eligibility
question H3 raised is raised again here, both readings computed, Section G5):
- HARMLESS winner: largest rep-grain reduction among ladder rungs whose
  recovery does NOT worsen (one-sided equivalence, margin +/-0.02, BOTH
  budgets) -- IDENTICAL filter to H3's own "joint winner" (sixth standing
  rule), now relabeled per the seventh standing rule's own vocabulary.
- ACTIVELY GOOD winner: largest rep-grain reduction among ladder rungs whose
  recovery IS improved (CI entirely on the better side, BOTH budgets) -- a
  STRICT SUBSET filter (algebraically: ci_hi<0 implies ci_hi<=0.02, so every
  actively-good arm is also harmless; verified, not merely asserted, in
  Section G5, on this leg's own data).
Every lean below states explicitly which winner it is evaluated at.

===========================================================================
DESIGN (registered)
===========================================================================
Worlds: H3's own three `HIGH_GAP_WORLDS` (imported transitively via h2), all
8 repetitions -- UNCHANGED. Three mandatory metrics, computed at EVERY arm
(all 7: deployed + 5 ladder rungs + reference): (1) Leg 14's displacement gap
(`disp_v2`, PRIMARY); (2) M4-E2's S1-S4 shares, reported PER WORLD (not only
the 3-world mean), since world heterogeneity -- specifically
`source_rotated_feedback`'s total non-response at every H3 rung -- is now
itself a registered question (lean b); (3) truth-referenced recovery at both
M4-F5 `TRUTH_BUDGETS`.

--- Metric grains (restated fresh, per the fifth standing rule -- inheriting
    a grain by citation alone is not a justification) -------------------
IDENTICAL worlds, repetitions, authors and budgets to H2/H3 -- the SAME
justification applies with no modification: Metric 1, REP grain (n=24)
PRIMARY / world grain (n=3) companion (`disp_v2` is already a per-repetition
quantity by this leg's own arm construction). Metric 2, WORLD-level census
(n=3, no CI -- a world's GPA-consensus share is a single deterministic
statistic, no finer sampling unit is defined). Metric 3, AUTHOR grain (n up
to 384) PRIMARY / world grain (n=3) companion (each (world, repetition, view,
author) is an independent forced-route refit against the analytic D_true).

--- Lean (b)'s materiality margin (carried forward from H3's own Part 0,
    unchanged) ------------------------------------------------------------
"S3's share falls MATERIALLY" is, as in H3, a RELATIVE fall of at least
`LEAN_B_MATERIALITY_RATIO = 0.10` from deployed's own S3 share, in ALL THREE
worlds (census). A companion, no-floor "falls at all" (ratio > 0) reading is
also computed and reported, mirroring H3's own disclosed practice.

Leans (registered; each states its own winner).
(a) CEILING LOCATED: at least one of the five ladder rungs is UNSAFE (author-
    grain OUTSIDE the +/-0.02 one-sided margin at either budget) -- so the
    harmless region's upper bound is interior to this ladder, not an
    endpoint again. A property of the whole ladder, not "at" a winner.
(b) GENERALIZES OR NOT: AT THE HARMLESS WINNER, does S3's share fall
    materially (>=10%, inherited floor) in all 3 worlds? A registered
    EITHER-WAY test: a miss confirms `source_rotated_feedback`'s
    non-response is STRUCTURAL rather than a strength effect -- itself the
    finding, not a failure.
(c) THE LEVELS SEPARATE: the ACTIVELY GOOD winner's ratio is STRICTLY BELOW
    the HARMLESS winner's ratio. Two readings disclosed: Reading A restricts
    both winners to this leg's own newly-tested ladder (0.50-8.0) alone;
    Reading B (ADOPTED) uses the full registered ladder to date -- H3's own
    already-G1-anchored 0.02/0.05/0.10/0.20 (cited from its persisted,
    already-adjudicated artifacts, not recomputed) PLUS this leg's own
    0.50-8.0. Reading B is adopted because "the actively-good ceiling" is a
    property of the whole lever this line has been building, not an
    artifact of where any one leg's own ladder happens to start; the
    comparison is valid across legs because `deployed` (the shared zero
    point both reduction-percentages are computed against) is G1-anchored
    bit-identical throughout the whole chain (H2->H3->H4).

**PIVOT-IF** no rung in the extended ladder is unsafe (lean (a) MISSES): the
safe region extends beyond 8x median-eigenvalue shrinkage with no ceiling
located in this design -- surprising enough that it demands a separate
explanation of why the deployed (unshrunk) value sits where it does, which
becomes the line's next registered question rather than a footnote.

Gates: G0 POWER (grain justified above, MDE stated from H3's own persisted
gap/recovery levels, BEFORE adjudicating); G1 ANCHOR (registered-literal:
`basis_shrinkage_0.50` and `whitening_unscaled` to <=1e-12 against H3's
persisted rows; disclosed superset: `deployed` also checked); G2 BASIS
LIVENESS (H2's own `G2_CONDITION_MATERIALITY_RATIO=0.10` convention, per
arm); G3 TRUTH-PATH INVARIANCE (degenerate equality, all 7 arms); G4
MATERIALITY FORM (equivalence/margin bound stated per gate); G5 DUAL-WINNER
COMPLIANCE (full arm x {reduction, S3 PER WORLD, recovery both variants}
table; both winners shown explicitly; what a SINGLE-winner rule -- H3's own
sixth-standing-rule "joint winner", reporting the harmless pick alone -- would
have chosen instead, and what it would have hidden).

Chunked execution (process rule -- foreground, explicit long timeouts, no
background jobs, no monitors): identical stage structure to h2/h3
(`--world W --stage oracle`, `--world W --stage g3`, `--world W --arm A`,
`--assemble`, `--smoke`), reusing h2's own context cache/oracle/regen
machinery UNCHANGED, writing to this leg's OWN output directory (a fresh,
independent context build -- NOT a copy of H3's cache -- so the G1 anchor is
a real end-to-end test). Every per-(world,arm)/per-world stage is idempotent.
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
import run_suica_m4_h3_safe_lever_ladder as h3  # noqa: E402  bit-exact reuse (h3.h2 is the SAME object as h2 above)

from suica_core.m4_chart_ecology_generator import M4ChartEcologySpec  # noqa: E402

# ---------------------------------------------------------------------------
# registered arms and parameters (Part 0, above)
# ---------------------------------------------------------------------------

DEPLOYED_ARM = "deployed"
WHITENING_UNSCALED_ARM = "whitening_unscaled"
RATIO_LADDER: tuple[float, ...] = (0.50, 1.0, 2.0, 4.0, 8.0)  # ladder EXTENSION upward, registered
_ladder_arm_name = h3._ladder_arm_name  # reused unchanged (":.2f" format -- "basis_shrinkage_<ratio>")

LADDER_ARMS: tuple[str, ...] = tuple(_ladder_arm_name(r) for r in RATIO_LADDER)
RATIO_BY_ARM: dict[str, float] = dict(zip(LADDER_ARMS, RATIO_LADDER))
NONDEPLOYED_ARMS: tuple[str, ...] = LADDER_ARMS + (WHITENING_UNSCALED_ARM,)
ARMS: tuple[str, ...] = (DEPLOYED_ARM,) + NONDEPLOYED_ARMS

ANCHOR_ARM = _ladder_arm_name(0.50)  # == "basis_shrinkage_0.50"
assert ANCHOR_ARM in h3.RATIO_BY_ARM, "ladder-bridge assumption violated: 0.50 must match H3's own rung name"
NEW_RATIO_ARMS: tuple[str, ...] = tuple(a for a in LADDER_ARMS if a != ANCHOR_ARM)  # this leg's only new compute

# identical strings on both sides: H4 keeps H3's own arm-naming convention.
H3_ARM_NAME = {DEPLOYED_ARM: "deployed", ANCHOR_ARM: "basis_shrinkage_0.50", WHITENING_UNSCALED_ARM: "whitening_unscaled"}
# the registered G1 clause names only these two; `deployed` is a disclosed superset check (see docstring).
H3_ARM_NAME_REGISTERED_ONLY = {ANCHOR_ARM: "basis_shrinkage_0.50", WHITENING_UNSCALED_ARM: "whitening_unscaled"}

G1_ANCHOR_TOLERANCE = h2.G1_ANCHOR_TOLERANCE          # 1e-12
G3_TOLERANCE = h2.G3_TOLERANCE                        # 1e-12
LEAN_A_BAR = h2.LEAN_A_BAR                             # 0.25 (informational/citational only -- H4's own leans do not gate on it)
RECOVERY_NO_WORSEN_MARGIN = h2.LEAN_C_MARGIN           # 0.02, one-sided "does not worsen" / harmless-eligibility margin
G0_FRACTION_BAR_METRIC3 = h2.G0_FRACTION_BAR_METRIC3   # 0.01
G2_MATERIALITY_RATIO = h2.G2_MATERIALITY_RATIO         # 0.10, basis-distance liveness bound
LEAN_B_MATERIALITY_RATIO = h3.LEAN_B_MATERIALITY_RATIO  # 0.10, S3-share relative-fall bound, carried forward from H3's Part 0 unchanged

H3_RESULTS = ROOT / "results" / "m4_h3_safe_lever_ladder"
H3_DISP_ROWS_PATH = H3_RESULTS / "disp_rows.csv"
H3_OFFSET_SHARES_PATH = H3_RESULTS / "offset_shares_by_arm.csv"
H3_TRUTH_ROWS_PATH = H3_RESULTS / "truth_recovery_rows.csv"
H3_DECISION_PATH = H3_RESULTS / "decision.json"

SHARE_FIELDS = h3.SHARE_FIELDS  # reused unchanged

WORLD_S3_COLUMN = {
    "endogenous_creation_expansion": "s3_endogenous_creation_expansion",
    "selection_creation_compensation": "s3_selection_creation_compensation",
    "source_rotated_feedback": "s3_source_rotated_feedback",
}


# ---------------------------------------------------------------------------
# this leg's ONLY new construction code: arm dispatch (0.50/reference are
# literal calls into h3's own dispatch; the 4 new ratios reuse h3's own
# shrinkage formula on h2's own ingredients)
# ---------------------------------------------------------------------------


def _basis_for_h4_arm(context: dict[str, Any], arm: str) -> tuple[dict[str, np.ndarray], dict[str, Any], dict[str, Any]]:
    """Dispatch for this leg's 7 arms. `deployed`, `whitening_unscaled` and
    the bridge rung `basis_shrinkage_0.50` are LITERAL calls into H3's own
    dispatch (`h3._basis_for_h3_arm`) -- not reimplemented, bit-identical to
    H3's construction by construction, not merely by formula equivalence.
    The four genuinely NEW rungs (1.0/2.0/4.0/8.0) reuse H3's own
    `_whitening_for_shrinkage_ratio` (unchanged formula) on H2's own
    `_ingredients_for_arm`, which falls through to deployed defaults for
    source-scale/centering/rank-tolerance automatically (this leg's arm
    names never match H2's 3 special-cased strings), exactly as every
    ladder rung in H2 and H3 already relies on."""
    if arm == DEPLOYED_ARM:
        return h3._basis_for_h3_arm(context, h3.DEPLOYED_ARM)
    if arm == WHITENING_UNSCALED_ARM:
        return h3._basis_for_h3_arm(context, h3.WHITENING_UNSCALED_ARM)
    if arm in RATIO_BY_ARM:
        ratio = RATIO_BY_ARM[arm]
        if arm in h3.RATIO_BY_ARM:  # ratio 0.50: the bridge point, H3's own rung name, literal reuse
            return h3._basis_for_h3_arm(context, arm)
        ingredients = h2._ingredients_for_arm(context, arm)
        whitening, meta = h3._whitening_for_shrinkage_ratio(ingredients, ratio)
        basis = h2.leg10._bases_from_whitening(context, ingredients, whitening)
        return basis, ingredients, meta
    raise ValueError(f"not a registered M4-H4 arm: {arm}")


# ---------------------------------------------------------------------------
# per-arm offset/shares (disclosed near-duplicate of h3._arm_offset_and_shares_h3,
# the ONLY change is _basis_for_h3_arm -> _basis_for_h4_arm; every other call
# is h2's own machinery, reused unchanged)
# ---------------------------------------------------------------------------


def _arm_offset_and_shares_h4(
    world: str, contexts: list[dict[str, Any]], arm: str, s1_patterns: np.ndarray, s2_patterns: np.ndarray,
) -> dict[str, Any]:
    v2_frames = []
    swap_frames = []
    disp_rows = []
    for context in contexts:
        basis, _, meta = _basis_for_h4_arm(context, arm)
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


def _g2_liveness_rows_h4(world: str, contexts: list[dict[str, Any]], arm: str) -> list[dict[str, Any]]:
    rows = []
    for context in contexts:
        deployed_basis, _, _ = _basis_for_h4_arm(context, DEPLOYED_ARM)
        arm_basis, _, _ = _basis_for_h4_arm(context, arm)
        deployed_frame = h2.leg11._stack_frame(deployed_basis)
        arm_frame = h2.leg11._stack_frame(arm_basis)
        distance = h2.leg14._quotient_distance(deployed_frame, arm_frame)
        rows.append({"world": world, "arm": arm, "repetition": context["repetition"], "basis_distance_vs_deployed": distance})
    return rows


def _g3_spot_check_h4(world: str, contexts: list[dict[str, Any]], spec: M4ChartEcologySpec) -> list[dict[str, Any]]:
    """Near-duplicate of h3._g3_spot_check_h3, generalized to this leg's 7 arms."""
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
        basis, _, _ = _basis_for_h4_arm(context, arm)
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


def _run_g3_h4(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    partial_path = output / f"partial_g3_{world}.csv"
    if partial_path.exists():
        print(f"[m4h4] SKIP (partial exists): g3 {world}", flush=True)
        return
    contexts = h2._contexts_for_world(world, config, spec, output)
    rows = _g3_spot_check_h4(world, contexts, spec)
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(partial_path, index=False)
    print(f"[m4h4] g3 stage done: {world} ({time.time() - started:.1f}s total)", flush=True)


def _run_arm_h4(world: str, arm: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    partial_path = output / f"partial_arm_{world}_{arm}.json"
    if partial_path.exists():
        print(f"[m4h4] SKIP (partial exists): {world} {arm}", flush=True)
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

    offset_shares = _arm_offset_and_shares_h4(world, contexts, arm, s1_patterns, s2_patterns)
    g2_rows = _g2_liveness_rows_h4(world, contexts, arm)

    truth_rows: list[dict[str, Any]] = []
    for context in contexts:
        for budget in h2.TRUTH_BUDGETS:
            t0 = time.time()
            regen = h2._regen_for_budget_cached(context, spec, budget, output)
            basis, _, _ = _basis_for_h4_arm(context, arm)
            rows = h2._arm_truth_rows(context, regen, budget, arm, basis)
            truth_rows.extend(rows)
            print(f"[m4h4] truth b={budget:g} {world} {arm} rep={context['repetition']} ({time.time() - t0:.1f}s)", flush=True)

    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(offset_shares["disp_rows"]).to_csv(output / f"partial_disp_{world}_{arm}.csv", index=False)
    pd.DataFrame(g2_rows).to_csv(output / f"partial_g2_{world}_{arm}.csv", index=False)
    pd.DataFrame(truth_rows).to_csv(output / f"partial_truth_{world}_{arm}.csv", index=False)
    summary = {k: v for k, v in offset_shares.items() if k != "disp_rows"}
    with partial_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    print(f"[m4h4] arm stage done: {world} {arm} ({time.time() - started:.1f}s total)", flush=True)


def _run_smoke_h4(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    t0 = time.time()
    world_index = {name: index for index, name in enumerate(config["worlds"])}[world]
    expected_for = h2.leg8._expected_geometries_lookup(config)
    seed = h2.leg3._world_seed(int(config["seed"]), 0, world, world_index)
    context = h2.leg4._build_context(
        world, 0, seed, spec=spec, config=config, expected_geometries=expected_for(world, 0, seed),
    )
    print(f"[m4h4 smoke] context built ({time.time() - t0:.1f}s)", flush=True)

    for arm in (DEPLOYED_ARM, _ladder_arm_name(0.50), _ladder_arm_name(8.0), WHITENING_UNSCALED_ARM):
        t1 = time.time()
        basis, ingredients, meta = _basis_for_h4_arm(context, arm)
        if arm == DEPLOYED_ARM:
            gap = max(float(np.max(np.abs(basis[role] - context["v2_basis"][role]))) for role in h2.ROLES)
            print(f"[m4h4 smoke] deployed basis vs context v2_basis max|diff|={gap:.3e}", flush=True)
            assert gap <= G1_ANCHOR_TOLERANCE, f"deployed basis reconstruction fails G1 anchor: {gap:.3e}"
        print(f"[m4h4 smoke] arm={arm} width={basis['calibration'].shape[1]} meta={meta} ({time.time() - t1:.1f}s)", flush=True)
    widths = {arm: _basis_for_h4_arm(context, arm)[0]["calibration"].shape[1] for arm in ARMS}
    print(f"[m4h4 smoke] widths by arm (must all match -- no rank_tolerance variant in this leg): {widths}", flush=True)
    assert len(set(widths.values())) == 1, f"unexpected width mismatch across arms: {widths}"

    # extra smoke-only check: the bridge rung reproduces H3's own dispatch bit-for-bit (not merely close)
    basis_bridge, _, _ = _basis_for_h4_arm(context, ANCHOR_ARM)
    basis_h3, _, _ = h3._basis_for_h3_arm(context, ANCHOR_ARM)
    bridge_gap = max(float(np.max(np.abs(basis_bridge[role] - basis_h3[role]))) for role in h2.ROLES)
    print(f"[m4h4 smoke] {ANCHOR_ARM} (this leg's dispatch) vs h3's own dispatch max|diff|={bridge_gap:.3e}", flush=True)
    assert bridge_gap == 0.0, f"bridge-rung reconstruction is not bit-identical to h3's own dispatch: {bridge_gap:.3e}"

    t2 = time.time()
    regen = h2._regen_for_budget(context, spec, 4.0)
    print(f"[m4h4 smoke] regen budget=4x ({time.time() - t2:.1f}s)", flush=True)
    t3 = time.time()
    oracle_rows = h2._oracle_truth_rows(context, regen, 4.0)
    print(f"[m4h4 smoke] oracle rows n={len(oracle_rows)} ({time.time() - t3:.1f}s)", flush=True)
    t4 = time.time()
    basis, _, _ = _basis_for_h4_arm(context, _ladder_arm_name(8.0))
    arm_rows = h2._arm_truth_rows(context, regen, 4.0, _ladder_arm_name(8.0), basis)
    print(f"[m4h4 smoke] arm rows n={len(arm_rows)} ({time.time() - t4:.1f}s)", flush=True)
    print(f"[m4h4 smoke] TOTAL ({time.time() - t0:.1f}s)", flush=True)


# ---------------------------------------------------------------------------
# G1 anchor-chain computation, parameterized by an {h4_arm: h3_arm} map so it
# can be called once for the outer registration's literal 2-arm clause and
# once for this script's own disclosed 3-arm superset (docstring).
# ---------------------------------------------------------------------------


def _g1_anchor_chains(
    arm_map: dict[str, str], disp_rows: pd.DataFrame, arm_summaries: dict[tuple[str, str], dict[str, Any]],
    truth_rows: pd.DataFrame, h3_disp: pd.DataFrame, h3_shares: pd.DataFrame, h3_truth: pd.DataFrame,
    worlds: list[str], expected_truth_arm_rows: int,
) -> dict[str, Any]:
    metric1_rows = []
    for h4_arm, h3_arm in arm_map.items():
        mine = disp_rows[disp_rows["arm"] == h4_arm][["world", "repetition", "disp_v2"]]
        theirs = h3_disp[h3_disp["arm"] == h3_arm][["world", "repetition", "disp_v2"]]
        joined = mine.merge(theirs, on=["world", "repetition"], suffixes=("_mine", "_h3"), how="inner")
        if len(joined) != 24:
            raise RuntimeError(f"metric1 anchor join for {h4_arm}: {len(joined)} rows != 24")
        joined["abs_diff"] = (joined["disp_v2_mine"] - joined["disp_v2_h3"]).abs()
        metric1_rows.append({"h4_arm": h4_arm, "h3_arm": h3_arm, "n_checks": len(joined), "max_abs_diff": float(joined["abs_diff"].max())})
    metric1_max = max(r["max_abs_diff"] for r in metric1_rows)

    metric2_rows = []
    for h4_arm, h3_arm in arm_map.items():
        for w in worlds:
            mine = arm_summaries[(w, h4_arm)]
            theirs_row = h3_shares[(h3_shares["world"] == w) & (h3_shares["arm"] == h3_arm)]
            if len(theirs_row) != 1:
                raise RuntimeError(f"metric2 anchor missing for {h4_arm}/{h3_arm} on {w}")
            theirs_row = theirs_row.iloc[0]
            offset_diff = abs(mine["offset_norm"] - float(theirs_row["offset_norm"]))
            flat_mine = {
                **{f"registered_{k}": v for k, v in mine["registered_shares"].items()},
                **{f"reverse_{k}": v for k, v in mine["reverse_shares"].items()},
                **{f"standalone_{k}": v for k, v in mine["standalone_shares"].items()},
                **{f"s3family_{k}": v for k, v in mine["s3_family_shares"].items()},
            }
            share_diffs = {f: abs(float(flat_mine[f]) - float(theirs_row[f])) for f in SHARE_FIELDS}
            metric2_rows.append({
                "h4_arm": h4_arm, "h3_arm": h3_arm, "world": w,
                "offset_norm_abs_diff": offset_diff, "max_share_abs_diff": max(share_diffs.values()),
            })
    metric2_max = max(max(r["offset_norm_abs_diff"], r["max_share_abs_diff"]) for r in metric2_rows)

    metric3_rows = []
    for h4_arm, h3_arm in arm_map.items():
        mine = truth_rows[truth_rows["arm"] == h4_arm][["world", "repetition", "view", "author", "budget", "e_arm_true"]]
        theirs = h3_truth[h3_truth["arm"] == h3_arm][["world", "repetition", "view", "author", "budget", "e_arm_true"]]
        joined = mine.merge(theirs, on=["world", "repetition", "view", "author", "budget"], suffixes=("_mine", "_h3"), how="inner")
        if len(joined) != expected_truth_arm_rows:
            raise RuntimeError(f"metric3 anchor join for {h4_arm}: {len(joined)} rows != {expected_truth_arm_rows}")
        both_nan = joined["e_arm_true_mine"].isna() & joined["e_arm_true_h3"].isna()
        diffs = (joined["e_arm_true_mine"] - joined["e_arm_true_h3"]).abs()
        diffs = diffs.where(~both_nan, 0.0)
        if diffs.isna().any():
            raise RuntimeError(f"metric3 anchor for {h4_arm}: NaN mismatch not covered by both_nan mask")
        metric3_rows.append({"h4_arm": h4_arm, "h3_arm": h3_arm, "n_checks": len(joined), "max_abs_diff": float(diffs.max())})
    metric3_max = max(r["max_abs_diff"] for r in metric3_rows)

    overall_max = max(metric1_max, metric2_max, metric3_max)
    return {
        "metric1_disp_v2_vs_h3_disp_rows": metric1_rows, "metric1_max_abs_diff": metric1_max,
        "metric2_offset_and_shares_vs_h3_offset_shares": {"per_world": metric2_rows, "max_abs_diff": metric2_max},
        "metric3_e_arm_true_vs_h3_truth_recovery_rows": metric3_rows, "metric3_max_abs_diff": metric3_max,
        "max_abs_diff_overall": overall_max, "pass": bool(overall_max <= G1_ANCHOR_TOLERANCE),
    }


# ---------------------------------------------------------------------------
# assemble + adjudicate
# ---------------------------------------------------------------------------


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

    # ==== load H3's own persisted artifacts (three CSVs + decision.json), once ==
    h3_disp = pd.read_csv(H3_DISP_ROWS_PATH)
    h3_shares = pd.read_csv(H3_OFFSET_SHARES_PATH)
    h3_truth = pd.read_csv(H3_TRUTH_ROWS_PATH)
    with H3_DECISION_PATH.open("r", encoding="utf-8") as handle:
        h3_decision = json.load(handle)

    # ==== G1 ANCHOR: registered-literal (2 arms) + disclosed superset (3 arms) ==
    g1_registered_literal = _g1_anchor_chains(
        H3_ARM_NAME_REGISTERED_ONLY, disp_rows, arm_summaries, truth_rows, h3_disp, h3_shares, h3_truth, worlds, expected_truth_arm_rows,
    )
    g1_disclosed_superset = _g1_anchor_chains(
        H3_ARM_NAME, disp_rows, arm_summaries, truth_rows, h3_disp, h3_shares, h3_truth, worlds, expected_truth_arm_rows,
    )
    g1_anchor = {
        "tolerance": G1_ANCHOR_TOLERANCE,
        "statement": (
            "basis_shrinkage_0.50 and whitening_unscaled reproduce H3's own persisted row-level CSVs "
            "(disp_rows.csv, offset_shares_by_arm.csv, truth_recovery_rows.csv) to <=1e-12, full row-level "
            "joins (not spot checks) -- the outer registration's own literal G1 clause. This script ALSO "
            "anchors `deployed` against H3's own persisted rows as a disclosed SUPERSET check (docstring); "
            "both readings are reported and necessarily agree on pass/fail since the superset only adds a "
            "check, never removes or loosens one."
        ),
        "registered_literal_2chain": g1_registered_literal,
        "disclosed_superset_3chain_incl_deployed": g1_disclosed_superset,
        "max_abs_diff_overall": g1_disclosed_superset["max_abs_diff_overall"],
        "pass": bool(g1_registered_literal["pass"] and g1_disclosed_superset["pass"]),
    }

    # ==== G2 BASIS LIVENESS ======================================================
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

    # ==== width-invariance check (disclosed companion) ==========================
    width_by_arm = disp_rows.groupby("arm")["width"].agg(["min", "max"]).to_dict("index")
    width_invariant = bool(len({v["min"] for v in width_by_arm.values()} | {v["max"] for v in width_by_arm.values()}) == 1)

    # ==== metric 1: displacement reduction, rep grain PRIMARY (n=24), ===========
    # ==== world grain (n=3) companion, per non-deployed arm =====================
    disp_wide = disp_rows.set_index(["world", "repetition", "arm"])["disp_v2"]
    deployed_mean_rep = float(disp_rows[disp_rows["arm"] == "deployed"]["disp_v2"].mean())
    bar_absolute_rep = LEAN_A_BAR * deployed_mean_rep  # informational/citational only -- H4's own leans gate on safety, not this 25% bar
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

    # ==== metric 2: S1-S4 shares, world census (n=3), per arm, PER WORLD ========
    # (world heterogeneity is itself a registered question -- report all shares
    # per world, not only S3's 3-world mean)
    shares_by_arm_world: dict[str, dict[str, dict[str, float]]] = {
        arm: {w: dict(arm_summaries[(w, arm)]["registered_shares"]) for w in worlds}
        for arm in ARMS
    }
    s3_by_arm_world = {arm: {w: float(shares_by_arm_world[arm][w]["S3_norm_scale_modes"]) for w in worlds} for arm in ARMS}
    lean_b_by_arm: dict[str, dict[str, Any]] = {}
    for arm in NONDEPLOYED_ARMS:
        per_world_fall_ratio = {
            w: (s3_by_arm_world["deployed"][w] - s3_by_arm_world[arm][w]) / s3_by_arm_world["deployed"][w]
            if s3_by_arm_world["deployed"][w] > 0 else float("nan")
            for w in worlds
        }
        falls_materially_all_worlds = all(per_world_fall_ratio[w] >= LEAN_B_MATERIALITY_RATIO for w in worlds)
        falls_at_all_all_worlds = all(per_world_fall_ratio[w] > 0.0 for w in worlds)
        lean_b_by_arm[arm] = {
            "s3_share_by_world": s3_by_arm_world[arm],
            "s3_share_mean_3worlds": float(np.mean(list(s3_by_arm_world[arm].values()))),
            "all_shares_by_world": shares_by_arm_world[arm],
            "relative_fall_vs_deployed_by_world": per_world_fall_ratio,
            "falls_materially_10pct_all_3_worlds": bool(falls_materially_all_worlds),
            "falls_at_all_all_3_worlds_no_floor_companion": bool(falls_at_all_all_worlds),
        }

    # ==== metric 3: truth recovery, author grain PRIMARY, world companion, =====
    # ==== computed for EVERY non-deployed arm (needed to build both pools) =====
    author_truth = h2.g4._author_level_truth_with_c(truth_joined)
    recovery_by_arm: dict[str, dict[str, Any]] = {}
    for arm in NONDEPLOYED_ARMS:
        by_budget = {}
        for budget in h2.TRUTH_BUDGETS:
            author_ci = h2.g4._paired_author_diff_ci(author_truth, arm, 1.0, "deployed", 1.0, budget, worlds)
            world_ci = h2.g4._paired_world_diff_ci(author_truth, arm, 1.0, "deployed", 1.0, budget, worlds)
            class_one_sided = h2.g4._classify_pair(author_ci, RECOVERY_NO_WORSEN_MARGIN, one_sided=True)
            class_two_sided = h2.g4._classify_pair(author_ci, RECOVERY_NO_WORSEN_MARGIN, one_sided=False)
            direction = h3._direction_classification(author_ci)
            underpowered = bool(author_ci["n"] > 1 and author_ci["half_width"] > G0_FRACTION_BAR_METRIC3)
            by_budget[str(budget)] = {
                "author_grain": {
                    "n": author_ci["n"], "mean_diff_arm_minus_deployed": author_ci["mean"],
                    "ci_lo": author_ci["ci_lo"], "ci_hi": author_ci["ci_hi"], "half_width": author_ci["half_width"],
                    "no_worsen_class_one_sided_ADOPTED": class_one_sided,
                    "no_worsen_class_two_sided_disclosed_check": class_two_sided,
                    "direction": direction, "underpowered_vs_g0_bar": underpowered,
                },
                "world_grain_companion": {
                    "n": world_ci["n"], "mean_diff_arm_minus_deployed": world_ci["mean"],
                    "ci_lo": world_ci["ci_lo"], "ci_hi": world_ci["ci_hi"],
                },
            }
        does_not_worsen_both = all(by_budget[str(b)]["author_grain"]["no_worsen_class_one_sided_ADOPTED"] == "WITHIN" for b in h2.TRUTH_BUDGETS)
        unsafe_either_budget = any(by_budget[str(b)]["author_grain"]["no_worsen_class_one_sided_ADOPTED"] == "OUTSIDE" for b in h2.TRUTH_BUDGETS)
        improved_both = all(by_budget[str(b)]["author_grain"]["direction"] == "IMPROVED" for b in h2.TRUTH_BUDGETS)
        two_sided_agrees = all(
            by_budget[str(b)]["author_grain"]["no_worsen_class_two_sided_disclosed_check"]
            == by_budget[str(b)]["author_grain"]["no_worsen_class_one_sided_ADOPTED"]
            for b in h2.TRUTH_BUDGETS
        )
        recovery_by_arm[arm] = {
            "by_budget": by_budget,
            "recovery_does_not_worsen_both_budgets_HARMLESS": bool(does_not_worsen_both),
            "recovery_unsafe_at_least_one_budget_OUTSIDE": bool(unsafe_either_budget),
            "recovery_improved_both_budgets_ACTIVELY_GOOD": bool(improved_both),
            "one_sided_vs_two_sided_margin_reading_agree_both_budgets": bool(two_sided_agrees),
        }

    # ==== G5 table: full arm x {reduction, S3 PER WORLD, recovery both variants} =
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
            "clears_25pct_bar_rep_informational": reduction_by_arm[arm]["rep_grain_PRIMARY"]["clears_25pct_bar"],
            **{WORLD_S3_COLUMN[w]: lean_b_by_arm[arm]["s3_share_by_world"][w] for w in worlds},
            "s3_share_mean_3worlds": lean_b_by_arm[arm]["s3_share_mean_3worlds"],
            "s3_falls_materially_10pct_all_3_worlds": lean_b_by_arm[arm]["falls_materially_10pct_all_3_worlds"],
            "s3_falls_at_all_all_3_worlds_no_floor": lean_b_by_arm[arm]["falls_at_all_all_3_worlds_no_floor_companion"],
            "recovery_diff_4x_mean": recovery_by_arm[arm]["by_budget"]["4.0"]["author_grain"]["mean_diff_arm_minus_deployed"],
            "recovery_class_4x": recovery_by_arm[arm]["by_budget"]["4.0"]["author_grain"]["no_worsen_class_one_sided_ADOPTED"],
            "recovery_direction_4x": recovery_by_arm[arm]["by_budget"]["4.0"]["author_grain"]["direction"],
            "recovery_diff_8x_mean": recovery_by_arm[arm]["by_budget"]["8.0"]["author_grain"]["mean_diff_arm_minus_deployed"],
            "recovery_class_8x": recovery_by_arm[arm]["by_budget"]["8.0"]["author_grain"]["no_worsen_class_one_sided_ADOPTED"],
            "recovery_direction_8x": recovery_by_arm[arm]["by_budget"]["8.0"]["author_grain"]["direction"],
            "recovery_does_not_worsen_both_budgets_HARMLESS": recovery_by_arm[arm]["recovery_does_not_worsen_both_budgets_HARMLESS"],
            "recovery_unsafe_at_least_one_budget_OUTSIDE": recovery_by_arm[arm]["recovery_unsafe_at_least_one_budget_OUTSIDE"],
            "recovery_improved_both_budgets_ACTIVELY_GOOD": recovery_by_arm[arm]["recovery_improved_both_budgets_ACTIVELY_GOOD"],
        }
        g5_table.append(row)
    g5_table_sorted = sorted(g5_table, key=lambda r: r["reduction_pct_rep_grain"], reverse=True)

    # ==== dual-winner selection (seventh standing rule) ==========================
    target_only_winner = max(NONDEPLOYED_ARMS, key=lambda a: reduction_by_arm[a]["rep_grain_PRIMARY"]["reduction_pct"])

    def _winner(pool: list[str]) -> str | None:
        return max(pool, key=lambda a: reduction_by_arm[a]["rep_grain_PRIMARY"]["reduction_pct"]) if pool else None

    harmless_pool_with_reference = [a for a in NONDEPLOYED_ARMS if recovery_by_arm[a]["recovery_does_not_worsen_both_budgets_HARMLESS"]]
    harmless_pool_ladder_only = [a for a in LADDER_ARMS if recovery_by_arm[a]["recovery_does_not_worsen_both_budgets_HARMLESS"]]
    harmless_winner_with_reference = _winner(harmless_pool_with_reference)
    harmless_winner_ladder_only = _winner(harmless_pool_ladder_only)
    harmless_readings_agree = bool(harmless_winner_with_reference == harmless_winner_ladder_only)
    harmless_winner = harmless_winner_ladder_only  # ADOPTED (matches H3's own adopted reading)

    actively_good_pool_with_reference = [a for a in NONDEPLOYED_ARMS if recovery_by_arm[a]["recovery_improved_both_budgets_ACTIVELY_GOOD"]]
    actively_good_pool_ladder_only = [a for a in LADDER_ARMS if recovery_by_arm[a]["recovery_improved_both_budgets_ACTIVELY_GOOD"]]
    actively_good_winner_with_reference = _winner(actively_good_pool_with_reference)
    actively_good_winner_ladder_only = _winner(actively_good_pool_ladder_only)
    actively_good_readings_agree = bool(actively_good_winner_with_reference == actively_good_winner_ladder_only)
    actively_good_winner = actively_good_winner_ladder_only  # ADOPTED

    actively_good_subset_of_harmless = all(a in harmless_pool_ladder_only for a in actively_good_pool_ladder_only)

    g5_dual_winner_compliance = {
        "statement": "full arm x {reduction, S3 per world, recovery both variants} table; BOTH winners (harmless, actively good) shown explicitly; what a SINGLE-winner rule (H3's own sixth-standing-rule 'joint winner', i.e. the harmless pick alone) would have chosen and hidden; the historical target-only pick shown for completeness",
        "full_table_sorted_by_reduction_pct_desc": g5_table_sorted,
        "target_only_winner_historical_pre_sixth_rule_defect": {
            "arm": target_only_winner,
            "reduction_pct_rep_grain": reduction_by_arm[target_only_winner]["rep_grain_PRIMARY"]["reduction_pct"],
            "recovery_does_not_worsen_both_budgets": recovery_by_arm[target_only_winner]["recovery_does_not_worsen_both_budgets_HARMLESS"],
            "note": "picked by largest reduction alone, ignoring recovery entirely -- the ORIGINAL (pre-sixth-standing-rule) defect; shown for continuity with every prior leg's own disclosure, not itself a registered pick",
        },
        "single_winner_rule_h3_sixth_standing_rule_harmless_only": {
            "arm": harmless_winner,
            "note": "H3's own registered 'joint winner' rule (sixth standing rule): largest reduction among the recovery-does-not-worsen pool, reported ALONE. This is exactly what a single-winner rule would choose here -- and, reported alone, it hides whether the pick is merely harmless or also actively good, which is precisely the gap the seventh standing rule exists to close.",
        },
        "dual_winner_seventh_standing_rule": {
            "harmless_winner": {
                "arm": harmless_winner, "pool": harmless_pool_ladder_only,
                "reduction_pct_rep_grain": reduction_by_arm[harmless_winner]["rep_grain_PRIMARY"]["reduction_pct"] if harmless_winner else None,
                "ratio": RATIO_BY_ARM.get(harmless_winner) if harmless_winner else None,
            },
            "actively_good_winner": {
                "arm": actively_good_winner, "pool": actively_good_pool_ladder_only,
                "reduction_pct_rep_grain": reduction_by_arm[actively_good_winner]["rep_grain_PRIMARY"]["reduction_pct"] if actively_good_winner else None,
                "ratio": RATIO_BY_ARM.get(actively_good_winner) if actively_good_winner else None,
            },
            "actively_good_pool_is_strict_subset_of_harmless_pool_verified": bool(actively_good_subset_of_harmless),
        },
        "ambiguity_disclosed_reference_eligibility": {
            "question": "is whitening_unscaled (the registered 'known-unsafe reference') eligible for HARMLESS/ACTIVELY-GOOD winner selection, or only the 5 basis_shrinkage_<ratio> ladder rungs? (the same question H3 raised for its own single joint winner)",
            "harmless_reading_A_reference_eligible": {"pool": harmless_pool_with_reference, "winner": harmless_winner_with_reference},
            "harmless_reading_B_ladder_only_ADOPTED": {"pool": harmless_pool_ladder_only, "winner": harmless_winner_ladder_only},
            "harmless_readings_agree": harmless_readings_agree,
            "actively_good_reading_A_reference_eligible": {"pool": actively_good_pool_with_reference, "winner": actively_good_winner_with_reference},
            "actively_good_reading_B_ladder_only_ADOPTED": {"pool": actively_good_pool_ladder_only, "winner": actively_good_winner_ladder_only},
            "actively_good_readings_agree": actively_good_readings_agree,
            "adopted": "B (ladder-only), matching H3's own adopted reading and the registration's naming of the reference separately from 'the...ladder'",
            "reason": "whitening_unscaled is G1-anchored bit-identical to H3's own known-unsafe reference, so it fails both pools under either reading regardless; disclosed as a robustness check, not a live fork.",
        },
    }

    # ==== lean (a): CEILING LOCATED -- a property of the WHOLE ladder ===========
    unsafe_ladder_rungs = [a for a in LADDER_ARMS if recovery_by_arm[a]["recovery_unsafe_at_least_one_budget_OUTSIDE"]]
    ambiguous_ladder_rungs = [
        a for a in LADDER_ARMS
        if not recovery_by_arm[a]["recovery_does_not_worsen_both_budgets_HARMLESS"]
        and not recovery_by_arm[a]["recovery_unsafe_at_least_one_budget_OUTSIDE"]
    ]
    lean_a = {
        "statement": "at least one of the five ladder rungs is UNSAFE (author-grain OUTSIDE the +/-0.02 one-sided margin at either budget) -- so the harmless region's upper bound is interior to this ladder, not an endpoint again",
        "unsafe_rungs": unsafe_ladder_rungs,
        "ambiguous_rungs_neither_within_nor_outside": ambiguous_ladder_rungs,
        "held": bool(len(unsafe_ladder_rungs) > 0),
    }
    lean_a_held = lean_a["held"]

    pivot_fires = not lean_a_held
    pivot = {
        "registered": "no rung in the extended ladder is unsafe -> the safe region extends beyond 8x median-eigenvalue shrinkage with no ceiling located in this design",
        "fires": bool(pivot_fires),
    }

    # ==== lean (b): GENERALIZES OR NOT -- AT THE HARMLESS WINNER ================
    lean_b = {
        "statement": "at the HARMLESS winner, does S3's registered-order share fall materially (>=10%, inherited from H3's Part 0) in all 3 worlds?",
        "evaluated_at_winner": "HARMLESS", "winner_arm": harmless_winner,
        "applicable": harmless_winner is not None, "held": False,
    }
    if harmless_winner is not None:
        lean_b.update({
            "s3_share_by_world": lean_b_by_arm[harmless_winner]["s3_share_by_world"],
            "s3_share_mean_3worlds": lean_b_by_arm[harmless_winner]["s3_share_mean_3worlds"],
            "relative_fall_vs_deployed_by_world": lean_b_by_arm[harmless_winner]["relative_fall_vs_deployed_by_world"],
            "falls_materially_10pct_all_3_worlds": lean_b_by_arm[harmless_winner]["falls_materially_10pct_all_3_worlds"],
            "falls_at_all_all_3_worlds_no_floor_companion": lean_b_by_arm[harmless_winner]["falls_at_all_all_3_worlds_no_floor_companion"],
            "held": lean_b_by_arm[harmless_winner]["falls_materially_10pct_all_3_worlds"],
        })
        if actively_good_winner is not None and actively_good_winner != harmless_winner:
            lean_b["disclosed_companion_at_actively_good_winner_not_adjudicating"] = {
                "winner_arm": actively_good_winner,
                "relative_fall_vs_deployed_by_world": lean_b_by_arm[actively_good_winner]["relative_fall_vs_deployed_by_world"],
                "falls_materially_10pct_all_3_worlds": lean_b_by_arm[actively_good_winner]["falls_materially_10pct_all_3_worlds"],
            }

    # ==== lean (c): THE LEVELS SEPARATE ==========================================
    # Reading A: restricted to THIS leg's own newly-tested ladder (0.50-8.0) alone
    reading_a_harmless_ratio = RATIO_BY_ARM.get(harmless_winner_ladder_only) if harmless_winner_ladder_only else None
    reading_a_actively_good_ratio = RATIO_BY_ARM.get(actively_good_winner_ladder_only) if actively_good_winner_ladder_only else None
    reading_a_computable = reading_a_harmless_ratio is not None and reading_a_actively_good_ratio is not None
    reading_a_held = bool(reading_a_computable and reading_a_actively_good_ratio < reading_a_harmless_ratio)

    # Reading B (ADOPTED): combined ladder -- H3's own persisted 0.02/0.05/0.10/0.20
    # (cited, NOT recomputed) + this leg's own 0.50/1.0/2.0/4.0/8.0
    h3_g5_rows = h3_decision["gates"]["G5_joint_winner_compliance"]["full_table_sorted_by_reduction_pct_desc"]
    h3_lower_rungs = [r for r in h3_g5_rows if r["is_ladder_rung"] and r["arm"] != ANCHOR_ARM]
    if len(h3_lower_rungs) != 4:
        raise RuntimeError(f"expected 4 H3-only lower rungs (0.02/0.05/0.10/0.20), got {len(h3_lower_rungs)}")
    combined_pool_rows = (
        [{"arm": r["arm"], "ratio": r["ratio"], "reduction_pct_rep_grain": r["reduction_pct_rep_grain"],
          "does_not_worsen": r["recovery_does_not_worsen_both_budgets"], "improved": r["recovery_improved_both_budgets"],
          "source": "H3_CITED_NOT_RECOMPUTED"} for r in h3_lower_rungs]
        + [{"arm": a, "ratio": RATIO_BY_ARM[a], "reduction_pct_rep_grain": reduction_by_arm[a]["rep_grain_PRIMARY"]["reduction_pct"],
            "does_not_worsen": recovery_by_arm[a]["recovery_does_not_worsen_both_budgets_HARMLESS"],
            "improved": recovery_by_arm[a]["recovery_improved_both_budgets_ACTIVELY_GOOD"],
            "source": "THIS_LEG"} for a in LADDER_ARMS]
    )
    combined_pool_rows_sorted = sorted(combined_pool_rows, key=lambda r: r["ratio"])
    combined_reduction_monotonic = all(
        combined_pool_rows_sorted[i]["reduction_pct_rep_grain"] <= combined_pool_rows_sorted[i + 1]["reduction_pct_rep_grain"]
        for i in range(len(combined_pool_rows_sorted) - 1)
    )
    combined_harmless_pool = [r for r in combined_pool_rows if r["does_not_worsen"]]
    combined_actively_good_pool = [r for r in combined_pool_rows if r["improved"]]
    combined_harmless_winner = max(combined_harmless_pool, key=lambda r: r["reduction_pct_rep_grain"]) if combined_harmless_pool else None
    combined_actively_good_winner = max(combined_actively_good_pool, key=lambda r: r["reduction_pct_rep_grain"]) if combined_actively_good_pool else None
    reading_b_computable = combined_harmless_winner is not None and combined_actively_good_winner is not None
    reading_b_held = bool(reading_b_computable and combined_actively_good_winner["ratio"] < combined_harmless_winner["ratio"])

    lean_c = {
        "statement": "the ACTIVELY GOOD winner's ratio is STRICTLY BELOW the HARMLESS winner's ratio -- quantifying what pushing harder costs",
        "reading_A_this_legs_own_ladder_only": {
            "harmless_winner": harmless_winner_ladder_only, "harmless_ratio": reading_a_harmless_ratio,
            "actively_good_winner": actively_good_winner_ladder_only, "actively_good_ratio": reading_a_actively_good_ratio,
            "computable": reading_a_computable, "held": reading_a_held,
            "note": "if actively_good_winner is None, there is no actively-good arm within THIS leg's own newly-tested range (0.50-8.0) to compare -- not a clean HOLD/MISS, reported as not computable here",
        },
        "reading_B_combined_ladder_ADOPTED": {
            "combined_pool_ratio_ordered": combined_pool_rows_sorted,
            "combined_reduction_monotonic_in_ratio": combined_reduction_monotonic,
            "harmless_winner": combined_harmless_winner, "actively_good_winner": combined_actively_good_winner,
            "computable": reading_b_computable, "held": reading_b_held,
        },
        "adopted": "B",
        "reason": "the actively-good ceiling is a property of the whole registered shrinkage lever, not an artifact of where any one leg's own ladder happens to start; H3's own 0.02-0.20 rows are G1-anchored, already-adjudicated, cited not recomputed; the comparison is valid across legs because `deployed` (the shared zero point) is G1-anchored bit-identical throughout H2->H3->H4.",
        "held": reading_b_held,
    }

    # ==== ceiling disclosure ======================================================
    if not lean_a_held:
        ceiling_disclosure = {
            "ceiling_located_in_this_ladder": False,
            "statement": "no rung in {0.50,...,8.0} is unsafe -- the PIVOT fires; see pivot section",
        }
    else:
        largest_harmless_ratio_ladder_only = max((RATIO_BY_ARM[a] for a in harmless_pool_ladder_only), default=None)
        smallest_unsafe_ratio = min((RATIO_BY_ARM[a] for a in unsafe_ladder_rungs), default=None)
        safety_is_contiguous = bool(
            largest_harmless_ratio_ladder_only is not None and smallest_unsafe_ratio is not None
            and largest_harmless_ratio_ladder_only < smallest_unsafe_ratio
            and all(RATIO_BY_ARM[a] < smallest_unsafe_ratio for a in harmless_pool_ladder_only)
            and all(RATIO_BY_ARM[a] >= smallest_unsafe_ratio for a in unsafe_ladder_rungs)
        )
        ceiling_disclosure = {
            "ceiling_located_in_this_ladder": True,
            "unsafe_rungs": unsafe_ladder_rungs,
            "largest_harmless_ratio_this_ladder": largest_harmless_ratio_ladder_only,
            "smallest_unsafe_ratio_this_ladder": smallest_unsafe_ratio,
            "safety_region_contiguous_below_smallest_unsafe_ratio": safety_is_contiguous,
            "statement": (
                "at least one rung is unsafe; the harmless region's upper bound is interior to this ladder"
                if safety_is_contiguous else
                "at least one rung is unsafe, but the safe/unsafe pattern across {0.50,...,8.0} is NOT a simple "
                "single threshold -- reported exactly, not smoothed into a 'ceiling' narrative"
            ),
        }

    # ==== G0 POWER (grain justified in the docstring; MDE stated citing H3's own =
    # ==== persisted numbers, BEFORE adjudicating) ================================
    h3_deployed_disp_pooled_mean = float(h3_disp[h3_disp["arm"] == "deployed"]["disp_v2"].mean())
    h3_g0 = h3_decision["gates"]["G0_power"]
    h3_metric1_half_widths = h3_g0["metric1_displacement"]["by_arm_half_width_rep_grain"]
    h3_metric3_half_widths = h3_g0["metric3_truth_recovery"]["by_arm_by_budget_half_width_author_grain"]
    h3_deployed_truth = h3_truth[(h3_truth["arm"] == "deployed") & (h3_truth["c"] == 1.0)]
    h3_recovery_baseline_own = {
        str(b): float(h3_deployed_truth[h3_deployed_truth["budget"] == b]["e_arm_true"].mean()) for b in h2.TRUTH_BUDGETS
    }
    metric3_hw_min = min(min(v.values()) for v in h3_metric3_half_widths.values())
    metric3_hw_max = max(max(v.values()) for v in h3_metric3_half_widths.values())

    g0_power = {
        "metric1_displacement": {
            "grain": "repetition (n=24, PRIMARY) / world (n=3, companion) -- IDENTICAL design to H2/H3 on the identical metric/worlds",
            "cited_from_m4h3": {
                "deployed_pooled_rep_grain_mean_disp_v2": h3_deployed_disp_pooled_mean,
                "h3_own_achieved_half_widths_rep_grain_across_its_6_arms": h3_metric1_half_widths,
            },
            "mde_statement_before_adjudicating": (
                f"H3's own largest rep-grain half-width across its 6 arms, on the IDENTICAL worlds/reps/disp_v2 "
                f"design, was {max(h3_metric1_half_widths.values()):.3f} -- this design is not expected to be "
                "underpowered for any arm; verified empirically below (H4's own half-widths, metric-1 section)."
            ),
            "by_arm_half_width_rep_grain": {a: reduction_by_arm[a]["rep_grain_PRIMARY"]["half_width"] for a in NONDEPLOYED_ARMS},
        },
        "metric2_shares": {
            "grain": "world (n=3, census)", "note": "point comparison, no CI; reported per world for all 7 arms",
        },
        "metric3_truth_recovery": {
            "grain": "author (n up to 384, PRIMARY) / world (n=3, companion)",
            "cited_from_m4h3": {
                "deployed_baseline_e_arm_true_recomputed_from_h3_own_csv": h3_recovery_baseline_own,
                "margin": RECOVERY_NO_WORSEN_MARGIN, "g0_bar": G0_FRACTION_BAR_METRIC3,
                "h3_own_achieved_half_widths_author_grain_across_its_6_arms": h3_metric3_half_widths,
            },
            "mde_statement_before_adjudicating": (
                f"the winner-eligibility (harmless) margin is +/-{RECOVERY_NO_WORSEN_MARGIN} (one-sided); this "
                f"line's own strict G0 bar is {G0_FRACTION_BAR_METRIC3} (half the margin); H3's own realized "
                f"author-grain half-widths across its 6 arms on the IDENTICAL design ranged "
                f"{metric3_hw_min:.4f}-{metric3_hw_max:.4f} -- this design is not expected to be underpowered "
                "for lean (a)/(c) at any safe-region arm; realized half-widths reported per arm below, each "
                "flagged against the G0_FRACTION_BAR_METRIC3 bar rather than silently read as a clean null if "
                "exceeded."
            ),
            "by_arm_by_budget_half_width_author_grain": {
                a: {str(b): recovery_by_arm[a]["by_budget"][str(b)]["author_grain"]["half_width"] for b in h2.TRUTH_BUDGETS} for a in NONDEPLOYED_ARMS
            },
            "by_arm_by_budget_underpowered_vs_g0_bar": {
                a: {str(b): recovery_by_arm[a]["by_budget"][str(b)]["author_grain"]["underpowered_vs_g0_bar"] for b in h2.TRUTH_BUDGETS} for a in NONDEPLOYED_ARMS
            },
        },
    }

    # ==== G4 MATERIALITY FORM ====================================================
    g4_materiality_form = {
        "G0": "CI-half-width-vs-bar equivalence bound per metric, MDE stated citing H3's own persisted numbers before adjudicating; underpowered comparisons flagged explicitly, never silently read as nulls",
        "G1": "degenerate exact-equality checks (tolerance 1e-12) against H3's own independently-persisted row-level CSVs, not significance tests (registered-literal 2-chain AND disclosed-superset 3-chain both reported)",
        "G2": "ratio-to-deployed-scale liveness bound (10% materiality margin), not nil-significance",
        "G3": "degenerate exact-equality check (tolerance 1e-12) between two independently-derived computations",
        "lean_a": "per-rung one-sided WITHIN/OUTSIDE equivalence classification at +/-0.02 (harmless-eligibility margin) -- a property of the WHOLE ladder (any rung), not a nil-significance test",
        "lean_b": "relative-fall equivalence bound (>=10% of deployed's own S3 share, inherited unchanged from H3's Part 0) across a 3-world census, at the HARMLESS winner only",
        "lean_c": "ordinal ratio comparison (actively-good winner's ratio strictly below harmless winner's ratio), built from the SAME one-sided WITHIN/IMPROVED equivalence classifications used to build each pool -- not a nil-significance test",
        "winner_definitions": "harmless: one-sided WITHIN/OUTSIDE/AMBIGUOUS equivalence at +/-0.02, both budgets, applied to every ladder rung. actively-good: strict-direction classification (CI entirely negative), both budgets, applied to every ladder rung -- a stricter, nested filter, verified a subset of the harmless filter on this leg's own data (G5).",
    }

    # ==== verdict =================================================================
    if pivot_fires:
        verdict = "PIVOT_SAFE_REGION_EXTENDS_BEYOND_8X_NO_CEILING_LOCATED"
    else:
        mech = "MECHANISM_GENERALIZES_3_OF_3_WORLDS" if lean_b["held"] else "MECHANISM_STILL_STRUCTURALLY_WORLD_HETEROGENEOUS"
        lvl = "LEVELS_SEPARATE" if lean_c["held"] else "LEVELS_DO_NOT_SEPARATE"
        verdict = f"CEILING_LOCATED__{mech}__{lvl}"

    decision = {
        "estimand_id": "SUICA_M4_H4_SAFE_CEILING",
        "tier": "EXPLORATORY (open-exploration phase)",
        "registered_in": "docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md M4-H4 registration (2026-08-03, BEFORE run), preceded by the M4-H3 planner adjudication note (seventh standing rule); ledger row M4-H4",
        "worlds": worlds, "arms": list(ARMS), "ladder_arms": list(LADDER_ARMS), "ratio_ladder": list(RATIO_LADDER),
        "anchor_bridge_arm": ANCHOR_ARM, "reference_arm": WHITENING_UNSCALED_ARM, "truth_budgets": list(h2.TRUTH_BUDGETS),
        "part0_inherited_from_h2_via_h3": (
            "this leg varies ONLY the same single step H3 varied (whitening scale, regularized reading), at an "
            "extended ratio range; zero new normalization/scaling/centering choices; every other Part 0 step held "
            "at deployed default by construction (verified: width_invariant across all 7 arms)"
        ),
        "width_invariance_check": {"by_arm_min_max_width": width_by_arm, "all_arms_identical_width": width_invariant},
        "gates": {
            "G0_power": g0_power, "G1_anchor": g1_anchor, "G2_basis_liveness": g2_basis_liveness,
            "G3_truth_path_invariance": g3_gate, "G4_materiality_form": g4_materiality_form,
            "G5_dual_winner_compliance": g5_dual_winner_compliance,
        },
        "lean_a_ceiling_located": lean_a,
        "lean_b_generalizes_at_harmless_winner": lean_b,
        "lean_c_levels_separate": lean_c,
        "pivot": pivot,
        "ceiling_disclosure": ceiling_disclosure,
        "verdict": verdict,
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only (the 3 HIGH_GAP_WORLDS, reused verbatim from M4-E2/Leg14/H2/H3); "
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
        "verdict": verdict, "pivot_fires": pivot_fires,
        "harmless_winner": harmless_winner, "actively_good_winner": actively_good_winner, "target_only_winner": target_only_winner,
        "lean_a_held": lean_a["held"], "lean_b_held": lean_b["held"], "lean_c_held": lean_c["held"],
        "g1_anchor_pass": g1_anchor["pass"], "g2_all_live": g2_basis_liveness["all_live"], "g3_pass": g3_gate["pass"],
    }, indent=2))


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "m4_chart_ecology.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "m4_h4_safe_ceiling")
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
        _run_smoke_h4(args.world, config, spec, args.output)
        return
    if args.stage == "oracle":
        h2._run_oracle(args.world, config, spec, args.output)
        return
    if args.stage == "g3":
        _run_g3_h4(args.world, config, spec, args.output)
        return
    if args.arm is None:
        raise SystemExit("--arm is required unless --stage oracle/g3 or --smoke or --assemble")
    if args.arm not in ARMS:
        raise SystemExit(f"not a registered arm: {args.arm}")
    _run_arm_h4(args.world, args.arm, config, spec, args.output)


if __name__ == "__main__":
    main()
