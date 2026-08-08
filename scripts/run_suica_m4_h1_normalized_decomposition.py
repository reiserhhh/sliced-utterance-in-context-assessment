#!/usr/bin/env python3
"""M4-H1: re-decompose the rep-invariant common offset in VALID units.

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, "M4-H1
registration" (2026-08-03, BEFORE run); ledger row M4-H1). Machinery is
IMPORTED VERBATIM, not re-derived: M4-E2's own module-level subspace-
construction and decomposition helpers (`_response_direction_machinery`,
`_arm_b_gate`, `_s1_patterns`, `_s2_patterns`, `_common_core`,
`_pattern_basis_to_matrix_basis`, `_orthonormal_matrix_basis`, `_project`,
`_sequential_shares`, `_procrustes_cosine`, `_within_role_permutation`, and
its own persisted-reference loaders `_load_leg14_decision`/
`_leg14_world_gates`), Leg 9's row-norm swap, Leg 10's freeze-ingredients
rebuild + `_debias_gate`, Leg 11's stacked-frame quotient machinery, Leg 14's
multi-start GPA + quotient distance + displacement-anchor loader, Leg 4's
context build, Leg 3's world seed, Leg 8's V2-replay lookup, M4-G1's
`_build_world_contexts`, and M4-G2's own registered scale-factor formula
(`_scale_factors_for_c`, evaluated at c=1.0 -- M4-G2's own G1-anchor-verified
equivalent of the deployed baseline whitening's per-direction scale). The
only NEW code is the orchestration that calls M4-E2's own functions TWICE
against the SAME S1-S4 bases (once on the raw Delta, once on the scale-
normalized Delta) and the world-level scale-normalization bookkeeping this
leg's own leans require.

THE DEBT. M4-E2 attributed the displacement's mass across S1 (supervised
core), S2 (supervision span), S3 (normalization/scale modes) and S4
(residual) -- scale family the largest identifiable carrier (~1/3 sequential,
~1/2 standalone), residual the largest single piece (.40-.45) -- computed
entirely on the RAW `offset_norm`, which M4-G2 proved unit-dependent (log-log
slope .8796 [.8386,.9206] under a manipulation whose eigenvectors, relative
spectrum, condition number and width were all invariant at exactly 0.0).
Does the attribution survive once the raw offset is replaced by M4-G2's own
registered scale-normalized offset?

================================================================================
PART 0.0 -- WHICH OBJECT DOES "SUBSTITUTE THE TARGET QUANTITY" MEAN
================================================================================
Disclosed ambiguity, resolved BEFORE compute, per the outer task's own
instruction to give numbers under both readings when a registered rule is
ambiguous. Here the two readings provably COINCIDE, which is this leg's
finding, not an evasion of the ambiguity -- both are stated so that
convergence is visible rather than assumed.

M4-G2's own registered definition (verbatim, `scripts/run_suica_m4_g2_metric_units.py`
Part 0.1): for an arm with per-retained-direction scale factors s_1..s_k,
    scale_normalized_offset(arm) := offset_norm(arm) / GM(s_1..s_k),
    GM(s) = exp(mean(log(s))).
This is a SCALAR division of the ALREADY-COMPUTED scalar `offset_norm` by a
scalar summary of that SAME arm's OWN whitening -- not a redefinition of the
whitening, not a rebuild of the discovered basis. M4-E2 has exactly one "arm"
(the deployed baseline whitening, unchanged throughout -- G1 ANCHOR requires
bit-exact reproduction, which would be impossible if the basis construction
itself were touched) and one offset OBJECT per world: the matrix
Delta = pad(v2 consensus) - align(pad(swap consensus)), offset_norm := ||Delta||_F.

  READING A (adopted as the primary manipulation): decompose
  Delta_normalized := Delta / GM_world instead of Delta, where GM_world is
  M4-G2's own GM(s) formula evaluated on the world's own deployed-baseline
  scale factors (aggregation registered in Part 0.1 below). This is the more
  substantive reading, directly tied to "the target quantity" being the
  object the decomposition actually operates on.

  READING B (reported as a correctness cross-check, not a second branch):
  treat `scale_normalized_offset` as a pure relabeling of the scalar summary
  `offset_norm` for reporting -- the decomposition (already a set of
  UNITLESS ratios computed on Delta) is untouched by construction under this
  reading.

================================================================================
PART 0.1 -- WHY THE TWO READINGS ARE FORCED TO COINCIDE (proved here BEFORE
compute; the numeric run below CONFIRMS this proof, it does not discover it)
================================================================================
Every M4-E2 decomposition statistic this leg's leans touch -- registered /
reverse / standalone sequential shares, the within-S3 family shares, the
width-mismatch share, the dominant share, the top-1 singular share, and the
cross-world Procrustes cosines (raw values AND both disclosed nulls) -- is a
RATIO of squared (or nuclear) norms of LINEAR IMAGES of Delta under FIXED,
Delta-INDEPENDENT bases: S1 is built from Leg 10 arm-B response-supervised
feature patterns, S2 from author-mean observed response patterns, S3 from
per-role constant patterns and the CONSENSUS POSITION `a_center` (the v2 GPA
mean itself, a separate object from the offset Delta = a_center - b_aligned)
-- never from Delta. Projection onto a fixed basis is LINEAR, so
Delta -> Delta/k (any positive scalar k) sends every component -> component/k;
every share below is therefore HOMOGENEOUS OF DEGREE 0 in k:

    share(Delta/k) = ||proj(Delta/k)||^2 / ||Delta/k||^2
                    = (1/k^2)||proj(Delta)||^2 / (1/k^2)||Delta||^2
                    = share(Delta)                                    EXACTLY.

Cross-world Procrustes cosine is bilinear-homogeneous-degree-0 in EACH
argument independently (nuclear_norm(D1/k1)^T(D2/k2) = nuclear_norm(D1'D2)/(k1 k2);
||D1/k1|| ||D2/k2|| = ||D1|| ||D2||/(k1 k2)): invariant even if the two
worlds' own k's differ, which they do here (GM_world varies by world).
Permutation commutes with scalar multiplication (it only reorders rows), so
the permutation-null draws are ALSO invariant; the matched-shape random null
does not touch Delta at all and is trivially shared.

READING A (k = GM_world, one scalar per world) and READING B (k = 1, no-op)
are consequently forced to the SAME share/cosine numbers for every world --
an algebraic identity, not an empirical coincidence to be discovered. G2
METRIC SUBSTITUTION LIVENESS is scoped, by the outer task's own text, to the
SCALAR targets (`offset_norm` vs `scale_normalized_offset`) actually
differing -- which they do, GM_world != 1 (M4-G1/M4-G2's own persisted
`scale_norm_rows.csv` baseline-arm values on these 3 worlds already run
27.5-38.6) -- not to the shares differing; this docstring states in advance
why the shares will not move, so the near-zero empirical diffs reported below
are a CHECK on this proof, not a surprise the proof is retrofitted to explain.

Refit-based statistics (M4-E2's task 4: dominant-component REMOVAL and its
gap closure) are invariant for a SEPARATE, simpler reason and are NOT one of
this leg's three registered leans, so they are not re-run here (disclosed,
not silently skipped): the removal direction u_dom is the dominant component
normalized BY ITS OWN NORM, already unitless in Delta's scale, and the refit
acts on each rep's actual frame (never rescaled) -- not on Delta.

================================================================================
PART 0.1 (continued) -- REGISTERED WORLD-LEVEL AGGREGATION OF GM(s)
================================================================================
The one genuine researcher degree of freedom this leg introduces: M4-G2's
formula is stated per (world, repetition, arm); M4-E2's Delta is a
WORLD-level, post-GPA-consensus object with no per-repetition analogue (the
consensus already collapses all 8 reps before Delta exists). Adopted:

    GM_world := mean over the world's 8 repetitions of GM(s_rep),
    s_rep = M4-G2's own `_scale_factors_for_c(ingredients, c=1.0)`
          = 1/sqrt(max(eig_i, 1e-12)) on the RETAINED eigenvalues,
    ingredients = `leg10._freeze_ingredients(context)` on that rep's context,

reusing M4-G2's own already-anchored formula UNCHANGED -- no new formula
invented. This mirrors M4-G2's OWN aggregation convention exactly: its lean
(c) collapsed `geometric_mean_scale` over repetitions via a plain per-
(world,arm) mean before any further reduction (`scripts/run_suica_m4_g2_metric_units.py`
line ~1308, `.groupby(["world","arm"])[...].mean()`). Cross-anchored below
against M4-G2's own persisted `scale_norm_rows.csv` (arm=="baseline") at
<=1e-9 -- M4-G2's own `SCALENORM_ANCHOR_TOLERANCE` -- and each rep's
`leg10._debias_gate` (that lambda=0 rebuild reproduces `context["v2_basis"]`
exactly) is additionally run as a live gate, confirming the scale factors
used correspond exactly to the SAME whitening that built the basis Delta is
computed from, at <=1e-9 (Leg 10's own `IDENTITY_TOLERANCE`).

================================================================================
GATES
================================================================================
G0 POWER: this leg's comparisons are DETERMINISTIC recomputations on 3 fixed,
finite worlds (a census, not a sample) -- there is no sampling distribution to
power against in the usual CI sense, and M4-E2's own leans/pivot were
themselves plain per-world point comparisons, never CI-based, at this same
n=3 grain (there is no finer grain: GPA consensus collapses 8 reps into ONE
world-level Delta before any decomposition happens, unlike the author-level
truth-recovery statistics used elsewhere in the M4-G line). World is
therefore the grain because it is the ONLY grain at which "a world's own
decomposition share" is even defined -- inherited from M4-E2 because the
target itself forces it, not passively (the fifth standing rule's concern).
Target level cited from M4-E2's persisted `decision.json`: registered-order
S3 share range .2953-.3830 (lean a's subject), S4 residual range .4015-.4464
(lean b's subject), offset cosines .4159-.4523 against permutation-null q95
.4666-.4752 (lean c's subject). The applicable "power" question is numerical,
not statistical: can this design resolve a difference far below the
registered 10-percentage-point (0.10) bar? Part 0.1's proof guarantees yes,
to floating-point precision (~1e-12 to 1e-16) -- ten-plus orders of magnitude
below the bar -- confirmed empirically per world, not merely asserted.

G1 ANCHOR: the RAW-metric re-run reproduces M4-E2's persisted shares
(registered/reverse/standalone/S3-family/width-mismatch/dominant/top-1-
singular) to <=1e-12, PLUS the upstream Leg-14-style offset/GPA-objective/
Leg-11-displacement/Leg-10-arm-B anchors M4-E2 itself gates on (so a failure
anywhere in the rebuild chain is caught at its source, not only at the final
share comparison), PLUS the GM_world computation anchored against M4-G2's own
persisted `scale_norm_rows.csv` at <=1e-9. This is what proves the metric is
the ONLY thing changed.

G2 METRIC SUBSTITUTION LIVENESS: `scale_normalized_offset != offset_norm` per
world (GM_world reported explicitly, must differ materially from 1.0).

G3 TRUTH-PATH INVARIANCE: NOT APPLICABLE. This leg constructs no truth-
referenced regeneration path (no budget/events regeneration, no D_true
comparison at any budget) -- its adjudicated quantities are pure functions of
the already-validated offset object Delta and M4-E2/Leg 14's own persisted
anchors, which G1 ANCHOR re-verifies. Stated explicitly per the registration's
own "where applicable" hedge, not silently skipped.

G4 MATERIALITY FORM: G1 is an equivalence/margin bound (<=1e-12 / <=1e-9).
G2 is a "must differ" liveness form (the SAME polarity convention M4-G1/
M4-G4/M4-G5's own G2 gates used for "the operator/constant/column-scale must
have moved"). Lean (a)/(pivot) use the registered 10-percentage-point margin
directly on point differences (M4-E2's own leans were unhedged point
comparisons at this grain; no CI form applies to a deterministic
recomputation). Lean (c) is registered here (Part 0.2, since the outer
registration names the null but not the exact statistic) as: SURVIVES iff,
for all 3 world pairs, the observed cosine lies at or below the within-role
permutation null's 95th percentile (q95) -- "not detectably above the null",
the operational meaning of M4-E2's own prose ("statistically indistinguishable
from ... the within-role permutation null").

Execution: chunked per-world (`--world` computes one world's partial;
`--assemble` combines, anchors, and adjudicates), following M4-G1/M4-G2/
M4-G7's own established convention -- three foreground chunks, each
rebuilding its own 8 contexts from scratch exactly as every prior leg here
does, plus one foreground assemble call.
"""
from __future__ import annotations

import argparse
import json
import sys
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

import run_suica_m4_d_dleg_floor_leg4 as leg4  # noqa: E402  bit-exact reuse
import run_suica_m4_d_overspan_control_leg3 as leg3  # noqa: E402
import run_suica_m4_d_bias_variance_leg9 as leg9  # noqa: E402
import run_suica_m4_d_direction_anatomy_leg10 as leg10  # noqa: E402
import run_suica_m4_d_perturbation_leg11 as leg11  # noqa: E402
import run_suica_m4_d_displacement_leg14 as leg14  # noqa: E402
import run_suica_m4_e2_offset_anatomy as e2  # noqa: E402  the leg being re-decomposed
import run_suica_m4_g1_whitening_intervention as g1mod  # noqa: E402  _build_world_contexts
import run_suica_m4_g2_metric_units as g2mod  # noqa: E402  registered scale-normalized offset formula

from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
)

HIGH_GAP_WORLDS = e2.HIGH_GAP_WORLDS
ROLES = e2.ROLES
SUBSPACE_NAMES = e2.SUBSPACE_NAMES
EPS = e2.EPS

# ---- reused-unchanged tolerances (identical checks to M4-E2's own chain) --
OFFSET_ANCHOR_TOLERANCE = e2.OFFSET_ANCHOR_TOLERANCE  # 1e-9
DISPLACEMENT_ANCHOR_TOLERANCE = e2.DISPLACEMENT_ANCHOR_TOLERANCE  # 1e-9
ARM_B_GATE_TOLERANCE = e2.ARM_B_GATE_TOLERANCE  # 1e-12
SELF_CONSISTENCY_TOLERANCE = e2.SELF_CONSISTENCY_TOLERANCE  # 1e-10
DEBIAS_TOLERANCE = leg10.IDENTITY_TOLERANCE  # 1e-9, leg10._debias_gate's own bar

# ---- new tolerances this leg's own gates need -----------------------------
G1_SHARE_ANCHOR_TOLERANCE = 1e-12  # vs M4-E2 persisted decision.json shares (registered bar)
GM_ANCHOR_TOLERANCE = 1e-9  # vs M4-G2 persisted scale_norm_rows.csv (its own SCALENORM_ANCHOR_TOLERANCE)
NORMALIZED_IDENTITY_REPORT_FLOOR = 1e-9  # any diff above this is investigated, not merely noted

LEAN_A_MOVE_BAR = 0.10  # percentage points (share units), either direction, registered order
LEAN_C_NULL_PERCENTILE = 0.95  # Part 0.2's own adopted operationalization

SHARE_KEYS = (
    "registered_shares",
    "reverse_shares",
    "standalone_shares",
    "s3_family_shares",
    "s3_family_shares_standalone_component",
    "family_standalone_shares",
)
ORDER_LABEL = {
    "registered_shares": "registered_S1_S2_S3",
    "reverse_shares": "reverse_S3_S2_S1",
    "standalone_shares": "standalone",
    "s3_family_shares": "within_S3_component",
    "s3_family_shares_standalone_component": "within_S3_standalone_component",
    "family_standalone_shares": "standalone_family_of_delta",
}


# ---------------------------------------------------------------------------
# persisted references
# ---------------------------------------------------------------------------


def _load_e2_decision() -> dict[str, Any]:
    path = ROOT / "results" / "m4_e2_offset_anatomy" / "decision.json"
    if not path.exists():
        raise RuntimeError(f"M4-E2 persisted decision is a required anchor: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_e2_cosine_rows() -> pd.DataFrame:
    path = ROOT / "results" / "m4_e2_offset_anatomy" / "cosine_rows.csv"
    if not path.exists():
        raise RuntimeError(f"M4-E2 persisted cosine rows are a required anchor: {path}")
    return pd.read_csv(path)


def _load_g2_scalenorm_baseline() -> pd.DataFrame:
    path = ROOT / "results" / "m4_g2_metric_units" / "scale_norm_rows.csv"
    if not path.exists():
        raise RuntimeError(f"M4-G2 persisted scale-norm rows are a required anchor: {path}")
    frame = pd.read_csv(path)
    return frame[frame["arm"] == "baseline"].reset_index(drop=True)


# ---------------------------------------------------------------------------
# per-world pass: RAW decomposition (near-duplicate orchestration of
# e2._world_pass, disclosed -- that function does not expose its local
# `bases`/`delta`, and drops M4-E2's task-4 diagnostic refit, not needed by
# any of this leg's three registered leans, per Part 0.1's own argument for
# why it would only reproduce M4-E2 bit-for-bit if re-run) + the NEW scale-
# normalized decomposition on the IDENTICAL bases.
# ---------------------------------------------------------------------------


def _decompose(
    target: np.ndarray,
    bases: dict[str, np.ndarray],
    family_bases: dict[str, np.ndarray],
    family_order: tuple[str, ...],
    b_aligned: np.ndarray,
) -> dict[str, Any]:
    registered = e2._sequential_shares(target, bases, SUBSPACE_NAMES)
    reverse = e2._sequential_shares(target, bases, tuple(reversed(SUBSPACE_NAMES)))
    standalone = {
        name: float(
            np.sum(e2._project(target.reshape(-1), basis) ** 2)
            / max(float(np.sum(target.reshape(-1) ** 2)), EPS)
        )
        for name, basis in bases.items()
    }
    s3_component = registered["components"]["S3_norm_scale_modes"]
    s3_families = e2._sequential_shares(s3_component, family_bases, family_order)["shares"]
    s3_standalone_component = e2._project(target.reshape(-1), bases["S3_norm_scale_modes"]).reshape(
        target.shape
    )
    s3_families_standalone_component = e2._sequential_shares(
        s3_standalone_component, family_bases, family_order
    )["shares"]
    family_standalone_shares = {
        name: float(
            np.sum(e2._project(target.reshape(-1), basis) ** 2)
            / max(float(np.sum(target.reshape(-1) ** 2)), EPS)
        )
        for name, basis in family_bases.items()
    }

    q_b, _ = np.linalg.qr(b_aligned)
    rank_b = int(np.linalg.matrix_rank(b_aligned, tol=1e-10))
    q_b = q_b[:, :rank_b]
    target_in_b_col = q_b @ (q_b.T @ target)
    width_mismatch_share = float(
        np.sum((target - target_in_b_col) ** 2) / max(np.sum(target**2), EPS)
    )
    width_mismatch_baseline = 1.0 - rank_b / target.shape[0]

    target_singular = np.linalg.svd(target, compute_uv=False)
    ordered_shares = [registered["shares"][name] for name in SUBSPACE_NAMES]
    dominant_name = SUBSPACE_NAMES[int(np.argmax(ordered_shares))]

    return {
        "norm": float(np.linalg.norm(target)),
        "registered_shares": registered["shares"],
        "reverse_shares": reverse["shares"],
        "standalone_shares": standalone,
        "s3_family_shares": s3_families,
        "s3_family_shares_standalone_component": s3_families_standalone_component,
        "family_standalone_shares": family_standalone_shares,
        "width_mismatch_share": width_mismatch_share,
        "width_mismatch_baseline": width_mismatch_baseline,
        "rank_b_aligned": rank_b,
        "delta_top3_singular": [float(v) for v in target_singular[:3]],
        "delta_singular_top1_share": float(
            target_singular[0] ** 2 / max(np.sum(target_singular**2), EPS)
        ),
        "dominant_subspace": dominant_name,
        "dominant_share": registered["shares"][dominant_name],
    }


def _world_pass_h1(
    world: str,
    config: dict[str, Any],
    spec: M4ChartEcologySpec,
    displacement_anchors: dict[tuple[str, int], float],
    leg14_gates: dict[str, dict[str, Any]],
    leg14_companions: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    contexts = g1mod._build_world_contexts(world, config, spec)  # unit-check + V2-replay gates included

    # ---- frames + Leg 11 displacement anchor (same gate M4-E2 runs) --------
    v2_frames: list[np.ndarray] = []
    swap_frames: list[np.ndarray] = []
    disp_anchor_max = 0.0
    for context in contexts:
        v2_basis = context["v2_basis"]
        swap_basis = leg9._row_norm_swap(context["truth"].oracle_basis, v2_basis)
        v2_frames.append(leg11._stack_frame(v2_basis))
        swap_frames.append(leg11._stack_frame(swap_basis))
        value = leg14._quotient_distance(swap_frames[-1], v2_frames[-1])
        anchor = displacement_anchors.get((world, context["repetition"]))
        if anchor is None:
            raise RuntimeError(
                f"no Leg 11 displacement anchor for {world} rep {context['repetition']}"
            )
        difference = abs(value - anchor)
        disp_anchor_max = max(disp_anchor_max, difference)
        if difference > DISPLACEMENT_ANCHOR_TOLERANCE:
            raise RuntimeError(
                f"displacement metric diverges from Leg 11 on {world} rep "
                f"{context['repetition']}: {value:.12f} vs {anchor:.12f}"
            )

    # ---- Leg 14 GPA consensus + offset (same rebuild M4-E2 runs) -----------
    gpa_v2 = leg14._frechet_mean_multistart(v2_frames)
    gpa_swap = leg14._frechet_mean_multistart(swap_frames)
    consensus = gpa_v2["mean"]
    swap_consensus = gpa_swap["mean"]
    offset_norm = leg14._quotient_distance(consensus, swap_consensus)

    persisted_gate = leg14_gates[world]
    persisted_companion = leg14_companions[world]
    persisted_offset = float(persisted_companion["v2_consensus_to_swap_consensus"])
    persisted_v2_objective = float(persisted_gate["gpa_objective_mean_squared_distance"])
    persisted_swap_objective = float(persisted_companion["swap_cloud_rms_spread"]) ** 2
    offset_anchor_gaps = {
        "offset": abs(offset_norm - persisted_offset),
        "v2_objective": abs(gpa_v2["objective_mean_squared_distance"] - persisted_v2_objective),
        "swap_objective": abs(gpa_swap["objective_mean_squared_distance"] - persisted_swap_objective),
    }
    if max(offset_anchor_gaps.values()) > OFFSET_ANCHOR_TOLERANCE:
        raise RuntimeError(f"Leg 14 cloud rebuild diverges on {world}: {offset_anchor_gaps}")

    width = max(consensus.shape[1], swap_consensus.shape[1])
    a_center = leg14._pad(consensus, width)
    b_center = leg14._pad(swap_consensus, width)
    b_aligned = leg14._align(b_center, a_center)
    delta = a_center - b_aligned
    if abs(float(np.linalg.norm(delta)) - offset_norm) > SELF_CONSISTENCY_TOLERANCE:
        raise RuntimeError(f"offset representative inconsistent with quotient distance on {world}")

    # ---- S1/S2/S3 bases: VERBATIM reuse of M4-E2's own functions -----------
    arm_b_gate_max = 0.0
    s1_per_rep: list[np.ndarray] = []
    s2_per_rep: list[np.ndarray] = []
    q_values: list[int] = []
    for context in contexts:
        machinery = e2._response_direction_machinery(context)
        arm_b_gate_max = max(arm_b_gate_max, e2._arm_b_gate(context, machinery))
        s1_per_rep.append(e2._s1_patterns(context, machinery))
        q_values.append(int(machinery["q"]))
        s2_per_rep.append(e2._s2_patterns(context))
    d1_target = int(np.median(q_values))
    s1_patterns, s1_captured, d1 = e2._common_core(s1_per_rep, retained_dim=d1_target)
    d2_target = int(s2_per_rep[0].shape[1])
    s2_patterns, s2_captured, d2 = e2._common_core(s2_per_rep, retained_dim=d2_target)
    s1_basis = e2._pattern_basis_to_matrix_basis(s1_patterns, width)
    s2_basis = e2._pattern_basis_to_matrix_basis(s2_patterns, width)

    categories = a_center.shape[0] // len(ROLES)
    constant_patterns = np.zeros((a_center.shape[0], len(ROLES)))
    for index in range(len(ROLES)):
        constant_patterns[index * categories : (index + 1) * categories, index] = 1.0 / np.sqrt(
            categories
        )
    n1_mats = [
        np.outer(constant_patterns[:, index], np.eye(width)[w])
        for index in range(len(ROLES))
        for w in range(width)
    ]
    _, _, right_vectors_t = np.linalg.svd(a_center, full_matrices=False)
    n2_mats = [
        a_center @ np.outer(right_vectors_t[i], right_vectors_t[i]) for i in range(right_vectors_t.shape[0])
    ]
    n3_mats = []
    for index in range(len(ROLES)):
        block = np.zeros_like(a_center)
        block[index * categories : (index + 1) * categories] = a_center[
            index * categories : (index + 1) * categories
        ]
        n3_mats.append(block)
    s3_basis = e2._orthonormal_matrix_basis(n1_mats + n2_mats + n3_mats)
    n1_basis = e2._orthonormal_matrix_basis(n1_mats)
    n2_basis = e2._orthonormal_matrix_basis(n2_mats)
    n3_basis = e2._orthonormal_matrix_basis(n3_mats)

    bases = {
        "S1_safety_complement": s1_basis,
        "S2_supervision_span": s2_basis,
        "S3_norm_scale_modes": s3_basis,
    }
    dims = {name: int(basis.shape[1]) for name, basis in bases.items()}
    total_dim = a_center.size
    null_shares = {name: dims[name] / total_dim for name in bases}
    family_bases = {"n1_centering_mass": n1_basis, "n2_column_scale": n2_basis, "n3_role_size": n3_basis}
    family_order = ("n1_centering_mass", "n2_column_scale", "n3_role_size")
    family_dims = {name: int(basis.shape[1]) for name, basis in family_bases.items()}

    raw_result = _decompose(delta, bases, family_bases, family_order, b_aligned)

    # ==== NEW: scale normalization (Part 0.1) ===============================
    gm_per_rep: list[float] = []
    gm_rows: list[dict[str, Any]] = []
    debias_gate_max = 0.0
    for context in contexts:
        ingredients = leg10._freeze_ingredients(context)
        debias = leg10._debias_gate(context, ingredients)  # raises if lambda=0 whitening != v2_basis
        debias_gate_max = max(debias_gate_max, max(debias.values()))
        scale = g2mod._scale_factors_for_c(ingredients, 1.0)
        gm = float(np.exp(np.mean(np.log(scale))))
        gm_per_rep.append(gm)
        gm_rows.append(
            {
                "world": world,
                "repetition": context["repetition"],
                "geometric_mean_scale": gm,
                "debias_whitening_gap": debias["whitening_gap"],
                "debias_center_gap": debias["center_gap"],
                "debias_basis_gap": debias["basis_gap"],
            }
        )
    world_gm = float(np.mean(gm_per_rep))
    delta_normalized = delta / world_gm
    offset_norm_normalized = offset_norm / world_gm

    normalized_result = _decompose(delta_normalized, bases, family_bases, family_order, b_aligned)

    # empirical confirmation of Part 0.1: shares must match to floating-point noise
    share_diffs: dict[str, dict[str, float]] = {}
    for key in SHARE_KEYS:
        raw_map = raw_result[key]
        norm_map = normalized_result[key]
        share_diffs[key] = {name: abs(raw_map[name] - norm_map[name]) for name in raw_map}
    identity_max_abs_diff = max(v for mapping in share_diffs.values() for v in mapping.values())
    identity_max_abs_diff = max(
        identity_max_abs_diff,
        abs(raw_result["width_mismatch_share"] - normalized_result["width_mismatch_share"]),
        abs(raw_result["delta_singular_top1_share"] - normalized_result["delta_singular_top1_share"]),
    )

    gates = {
        "world": world,
        "unit_check_max": max(float(c_["unit_gap"]) for c_ in contexts),
        "displacement_anchor_max_abs_diff": disp_anchor_max,
        "offset_anchor_abs_diff": offset_anchor_gaps["offset"],
        "gpa_v2_objective_abs_diff": offset_anchor_gaps["v2_objective"],
        "gpa_swap_objective_abs_diff": offset_anchor_gaps["swap_objective"],
        "arm_b_gate_max": arm_b_gate_max,
        "debias_gate_max": debias_gate_max,
        "gpa_v2_best_init": int(gpa_v2["best_init_index"]),
        "gpa_v2_n_distinct_basins": int(gpa_v2["n_distinct_basins"]),
        "gpa_swap_n_distinct_basins": int(gpa_swap["n_distinct_basins"]),
        "normalized_vs_raw_share_identity_max_abs_diff": identity_max_abs_diff,
    }

    return {
        "world": world,
        "delta": delta,
        "delta_normalized": delta_normalized,
        "offset_norm": offset_norm,
        "offset_norm_normalized": offset_norm_normalized,
        "world_gm": world_gm,
        "gm_rows": gm_rows,
        "width": width,
        "bases_dims": dims,
        "null_shares": null_shares,
        "family_dims": family_dims,
        "s1_captured": s1_captured,
        "s2_captured": s2_captured,
        "d1": d1,
        "d2": d2,
        "raw": raw_result,
        "normalized": normalized_result,
        "share_diffs": share_diffs,
        "identity_max_abs_diff": identity_max_abs_diff,
        "gates": gates,
    }


# ---------------------------------------------------------------------------
# stage: --world (compute one world's partial)
# ---------------------------------------------------------------------------


def _run_world(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    if world not in HIGH_GAP_WORLDS:
        raise SystemExit(f"not a registered high-gap world: {world}")
    displacement_anchors = leg14._load_leg11_displacement_anchors()
    leg14_decision = e2._load_leg14_decision()
    leg14_gates = e2._leg14_world_gates(leg14_decision)
    leg14_companions = leg14_decision["companions_target_motion_and_basins"]

    result = _world_pass_h1(world, config, spec, displacement_anchors, leg14_gates, leg14_companions)

    output.mkdir(parents=True, exist_ok=True)
    np.save(output / f"partial_delta_{world}.npy", result["delta"])
    np.save(output / f"partial_delta_normalized_{world}.npy", result["delta_normalized"])
    pd.DataFrame(result["gm_rows"]).to_csv(output / f"partial_gm_rows_{world}.csv", index=False)

    payload = {
        "world": world,
        "offset_norm": result["offset_norm"],
        "offset_norm_normalized": result["offset_norm_normalized"],
        "world_gm": result["world_gm"],
        "width": result["width"],
        "bases_dims": result["bases_dims"],
        "null_shares": result["null_shares"],
        "family_dims": result["family_dims"],
        "s1_captured_pooled_fraction": result["s1_captured"],
        "s2_captured_pooled_fraction": result["s2_captured"],
        "d1_retained": result["d1"],
        "d2_retained": result["d2"],
        "raw": result["raw"],
        "normalized": result["normalized"],
        "share_diffs": result["share_diffs"],
        "identity_max_abs_diff": result["identity_max_abs_diff"],
        "gates": result["gates"],
    }
    with (output / f"partial_shares_{world}.json").open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    print(
        f"[m4h1] {world} done: offset={result['offset_norm']:.6f} "
        f"normalized={result['offset_norm_normalized']:.6f} world_gm={result['world_gm']:.6f} "
        f"identity_max_abs_diff={result['identity_max_abs_diff']:.3e}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# assemble: anchors + cross-world cosines (both metrics) + adjudication
# ---------------------------------------------------------------------------


def _cross_world_cosines(
    worlds: list[str],
    deltas: dict[str, np.ndarray],
    seed: int,
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    """Reproduces e2's own task-3 cosine loop exactly (same seed tags, same
    world order, same draw sequence), parameterized over an arbitrary
    per-world delta dict so it can be called once for raw and once for
    normalized deltas with IDENTICAL random draws (Part 0.1: this is what
    lets the two calls empirically confirm, not merely assert, invariance)."""
    pairs = [(worlds[i], worlds[j]) for i in range(len(worlds)) for j in range(i + 1, len(worlds))]
    rng_perm = np.random.default_rng([seed, e2.PERM_NULL_SEED_TAG])
    rng_rand = np.random.default_rng([seed, e2.RANDOM_NULL_SEED_TAG])
    shape = deltas[worlds[0]].shape
    random_null = []
    for _ in range(e2.NULL_DRAWS):
        first = rng_rand.standard_normal(shape)
        second = rng_rand.standard_normal(shape)
        random_null.append(e2._procrustes_cosine(first, second))
    random_null = np.asarray(random_null)

    cosine_offsets: dict[str, float] = {}
    rows: list[dict[str, Any]] = []
    for first, second in pairs:
        pair_name = f"{first}|{second}"
        delta_first = deltas[first]
        delta_second = deltas[second]
        raw = e2._procrustes_cosine(delta_first, delta_second)
        cosine_offsets[pair_name] = raw
        perm_values = np.asarray(
            [
                e2._procrustes_cosine(delta_first, e2._within_role_permutation(delta_second, rng_perm))
                for _ in range(e2.NULL_DRAWS)
            ]
        )
        rows.append(
            {
                "pair": pair_name,
                "cosine_offset": raw,
                "perm_null_median": float(np.median(perm_values)),
                "perm_null_q95": float(np.quantile(perm_values, LEAN_C_NULL_PERCENTILE)),
                "random_null_median": float(np.median(random_null)),
                "random_null_q95": float(np.quantile(random_null, LEAN_C_NULL_PERCENTILE)),
                "at_or_below_perm_q95": bool(raw <= float(np.quantile(perm_values, LEAN_C_NULL_PERCENTILE))),
            }
        )
    return cosine_offsets, rows


def _assemble(output: Path, config: dict[str, Any]) -> None:
    worlds = list(HIGH_GAP_WORLDS)
    seed = int(config["seed"])

    partials = {}
    deltas_raw: dict[str, np.ndarray] = {}
    deltas_norm: dict[str, np.ndarray] = {}
    gm_frames = []
    for world in worlds:
        with (output / f"partial_shares_{world}.json").open("r", encoding="utf-8") as handle:
            partials[world] = json.load(handle)
        deltas_raw[world] = np.load(output / f"partial_delta_{world}.npy")
        deltas_norm[world] = np.load(output / f"partial_delta_normalized_{world}.npy")
        gm_frames.append(pd.read_csv(output / f"partial_gm_rows_{world}.csv"))
    gm_rows = pd.concat(gm_frames, ignore_index=True)

    # =========================================================================
    # G1 ANCHOR -- upstream rebuild chain (already gated per-world at compute
    # time; assemble the summary) + shares/offset vs M4-E2's PERSISTED decision.json
    # + GM_world's own per-rep values vs M4-G2's PERSISTED scale_norm_rows.csv
    # =========================================================================
    upstream_gate_max = {
        key: max(partials[w]["gates"][key] for w in worlds)
        for key in (
            "unit_check_max",
            "displacement_anchor_max_abs_diff",
            "offset_anchor_abs_diff",
            "gpa_v2_objective_abs_diff",
            "gpa_swap_objective_abs_diff",
            "arm_b_gate_max",
            "debias_gate_max",
        )
    }

    e2_decision = _load_e2_decision()
    share_anchor_rows = []
    offset_anchor_rows = []
    for world in worlds:
        e2_world = e2_decision["offset_table"][world]
        mine = partials[world]["raw"]
        offset_anchor_rows.append(
            {
                "world": world,
                "mine_offset_norm": partials[world]["offset_norm"],
                "e2_offset_norm": e2_world["offset_norm"],
                "abs_diff": abs(partials[world]["offset_norm"] - e2_world["offset_norm"]),
            }
        )
        for key, e2_key in (
            ("registered_shares", "registered_shares"),
            ("reverse_shares", "reverse_shares"),
            ("standalone_shares", "standalone_shares"),
            ("s3_family_shares", "s3_family_shares"),
            (
                "s3_family_shares_standalone_component",
                "s3_family_shares_standalone_component",
            ),
            ("family_standalone_shares", "family_standalone_shares"),
        ):
            e2_map = e2_world[e2_key]
            mine_map = mine[key]
            for name in e2_map:
                share_anchor_rows.append(
                    {
                        "world": world,
                        "field": key,
                        "subspace": name,
                        "mine": mine_map[name],
                        "e2_persisted": e2_map[name],
                        "abs_diff": abs(mine_map[name] - e2_map[name]),
                    }
                )
        for scalar_key in (
            "width_mismatch_share",
            "width_mismatch_baseline",
            "rank_b_aligned",
            "dominant_share",
            "delta_singular_top1_share",
        ):
            share_anchor_rows.append(
                {
                    "world": world,
                    "field": "scalar_companion",
                    "subspace": scalar_key,
                    "mine": mine[scalar_key],
                    "e2_persisted": e2_world[scalar_key],
                    "abs_diff": abs(float(mine[scalar_key]) - float(e2_world[scalar_key])),
                }
            )
        share_anchor_rows.append(
            {
                "world": world,
                "field": "scalar_companion",
                "subspace": "dominant_subspace_matches",
                "mine": mine["dominant_subspace"],
                "e2_persisted": e2_world["dominant_subspace"],
                "abs_diff": 0.0 if mine["dominant_subspace"] == e2_world["dominant_subspace"] else 1.0,
            }
        )
    share_anchor_frame = pd.DataFrame(share_anchor_rows)
    offset_anchor_frame = pd.DataFrame(offset_anchor_rows)
    share_anchor_max = float(share_anchor_frame["abs_diff"].max())
    offset_anchor_max = float(offset_anchor_frame["abs_diff"].max())

    # G1 cosine anchor: my RAW cosines vs M4-E2's persisted cosine_rows.csv
    cosine_offsets_raw, cosine_rows_raw = _cross_world_cosines(worlds, deltas_raw, seed)
    e2_cosine_rows = _load_e2_cosine_rows()
    cosine_anchor_rows = []
    for row in cosine_rows_raw:
        e2_row = e2_cosine_rows[e2_cosine_rows["pair"] == row["pair"]].iloc[0]
        cosine_anchor_rows.append(
            {
                "pair": row["pair"],
                "mine_cosine_offset": row["cosine_offset"],
                "e2_cosine_offset": float(e2_row["cosine_offset"]),
                "abs_diff_cosine": abs(row["cosine_offset"] - float(e2_row["cosine_offset"])),
                "mine_perm_null_median": row["perm_null_median"],
                "e2_perm_null_median": float(e2_row["perm_null_median"]),
                "abs_diff_perm_null_median": abs(row["perm_null_median"] - float(e2_row["perm_null_median"])),
            }
        )
    cosine_anchor_frame = pd.DataFrame(cosine_anchor_rows)
    cosine_anchor_max = float(
        max(cosine_anchor_frame["abs_diff_cosine"].max(), cosine_anchor_frame["abs_diff_perm_null_median"].max())
    )

    # GM_world per-rep anchor vs M4-G2's persisted scale_norm_rows.csv (baseline arm)
    g2_scalenorm = _load_g2_scalenorm_baseline()
    gm_joined = gm_rows.merge(
        g2_scalenorm[["world", "repetition", "geometric_mean_scale"]],
        on=["world", "repetition"],
        suffixes=("_mine", "_g2"),
        how="inner",
    )
    if len(gm_joined) != len(gm_rows):
        raise RuntimeError(
            f"GM anchor join incomplete: {len(gm_joined)} matched vs {len(gm_rows)} computed rows"
        )
    gm_joined["abs_diff"] = (gm_joined["geometric_mean_scale_mine"] - gm_joined["geometric_mean_scale_g2"]).abs()
    gm_anchor_max = float(gm_joined["abs_diff"].max())

    g1_anchor = {
        "upstream_gate_max": upstream_gate_max,
        "share_anchor_max_abs_diff": share_anchor_max,
        "offset_anchor_max_abs_diff": offset_anchor_max,
        "cosine_anchor_max_abs_diff": cosine_anchor_max,
        "gm_anchor_max_abs_diff_vs_m4g2": gm_anchor_max,
        "gm_anchor_n_rows": int(len(gm_joined)),
        "tolerance_shares_offset_cosine": G1_SHARE_ANCHOR_TOLERANCE,
        "tolerance_gm": GM_ANCHOR_TOLERANCE,
        "pass": bool(
            share_anchor_max <= G1_SHARE_ANCHOR_TOLERANCE
            and offset_anchor_max <= G1_SHARE_ANCHOR_TOLERANCE
            and cosine_anchor_max <= G1_SHARE_ANCHOR_TOLERANCE
            and gm_anchor_max <= GM_ANCHOR_TOLERANCE
            and max(upstream_gate_max.values()) <= 1e-6
        ),
    }

    # =========================================================================
    # G2 METRIC SUBSTITUTION LIVENESS
    # =========================================================================
    g2_rows = [
        {
            "world": w,
            "offset_norm": partials[w]["offset_norm"],
            "offset_norm_normalized": partials[w]["offset_norm_normalized"],
            "world_gm": partials[w]["world_gm"],
            "abs_diff": abs(partials[w]["offset_norm"] - partials[w]["offset_norm_normalized"]),
            "relative_diff": abs(partials[w]["offset_norm"] - partials[w]["offset_norm_normalized"])
            / max(partials[w]["offset_norm"], EPS),
        }
        for w in worlds
    ]
    g2_min_relative_diff = min(row["relative_diff"] for row in g2_rows)
    g2 = {
        "statement": (
            "offset_norm and scale_normalized_offset must differ per world "
            "(GM_world != 1); this is the ONLY thing the metric substitution "
            "changes -- Part 0.1 proves in advance that the decomposition "
            "shares below will not move despite this"
        ),
        "rows": g2_rows,
        "min_relative_diff": g2_min_relative_diff,
        "live": bool(g2_min_relative_diff > 0.01),  # world_gm would need to be within 1% of 1.0 to be inert
    }

    # =========================================================================
    # normalized-vs-raw identity confirmation (Part 0.1's proof, empirically)
    # =========================================================================
    identity_max = max(partials[w]["identity_max_abs_diff"] for w in worlds)
    identity_rows = []
    for w in worlds:
        for field, diffs in partials[w]["share_diffs"].items():
            for subspace, diff in diffs.items():
                identity_rows.append(
                    {
                        "world": w,
                        "field": field,
                        "subspace": subspace,
                        "raw_share": partials[w]["raw"][field][subspace],
                        "normalized_share": partials[w]["normalized"][field][subspace],
                        "abs_diff": diff,
                    }
                )
    identity_frame = pd.DataFrame(identity_rows)

    # =========================================================================
    # cross-world cosines, NORMALIZED metric (identical machinery/seeds/order)
    # =========================================================================
    cosine_offsets_norm, cosine_rows_norm = _cross_world_cosines(worlds, deltas_norm, seed)
    cosine_identity_max = max(
        abs(cosine_offsets_raw[pair] - cosine_offsets_norm[pair]) for pair in cosine_offsets_raw
    )
    for pair in cosine_offsets_raw:
        raw_row = next(r for r in cosine_rows_raw if r["pair"] == pair)
        norm_row = next(r for r in cosine_rows_norm if r["pair"] == pair)
        cosine_identity_max = max(
            cosine_identity_max,
            abs(raw_row["perm_null_median"] - norm_row["perm_null_median"]),
            abs(raw_row["perm_null_q95"] - norm_row["perm_null_q95"]),
        )

    # =========================================================================
    # decomposition_rows_both_metrics.csv -- the full share table, both metrics
    # =========================================================================
    decomposition_rows = []
    for w in worlds:
        for metric_name, source in (("raw", partials[w]["raw"]), ("normalized", partials[w]["normalized"])):
            offset_val = partials[w]["offset_norm"] if metric_name == "raw" else partials[w]["offset_norm_normalized"]
            for key in SHARE_KEYS:
                for subspace, share in source[key].items():
                    decomposition_rows.append(
                        {
                            "world": w,
                            "metric": metric_name,
                            "order": ORDER_LABEL[key],
                            "subspace": subspace,
                            "share": share,
                            "offset_norm": offset_val,
                            "squared_norm": share * offset_val**2,
                        }
                    )
    decomposition_frame = pd.DataFrame(decomposition_rows)

    # =========================================================================
    # LEAN (a) -- THE ATTRIBUTION MOVES (S3 scale family, registered order)
    # =========================================================================
    lean_a_rows = []
    for w in worlds:
        raw_share = partials[w]["raw"]["registered_shares"]["S3_norm_scale_modes"]
        norm_share = partials[w]["normalized"]["registered_shares"]["S3_norm_scale_modes"]
        lean_a_rows.append(
            {
                "world": w,
                "raw_share": raw_share,
                "normalized_share": norm_share,
                "abs_diff_points": abs(raw_share - norm_share) * 100.0,
                "moved": bool(abs(raw_share - norm_share) > LEAN_A_MOVE_BAR),
            }
        )
    lean_a_held = any(row["moved"] for row in lean_a_rows)
    lean_a = {
        "statement": (
            "the scale family's (S3) share under the normalized metric differs "
            "from its raw-metric share by more than 10 percentage points, "
            "either direction, in the registered sequential order, in at "
            "least one world"
        ),
        "bar_points": LEAN_A_MOVE_BAR * 100.0,
        "rows": lean_a_rows,
        "held": bool(lean_a_held),
    }

    # =========================================================================
    # LEAN (b) -- THE RESIDUAL SURVIVES (largest single piece, registered order)
    # =========================================================================
    lean_b_rows = []
    for w in worlds:
        norm_shares = partials[w]["normalized"]["registered_shares"]
        largest = max(norm_shares, key=norm_shares.get)
        lean_b_rows.append(
            {
                "world": w,
                "shares_normalized": norm_shares,
                "largest_subspace": largest,
                "residual_is_largest": bool(largest == "S4_residual"),
            }
        )
    lean_b_held = all(row["residual_is_largest"] for row in lean_b_rows)
    lean_b = {
        "statement": (
            "the residual (S4) remains the largest single piece under the "
            "normalized metric, registered order, in all 3 worlds"
        ),
        "rows": lean_b_rows,
        "held": bool(lean_b_held),
    }

    # =========================================================================
    # LEAN (c) -- WORLD-SPECIFICITY SURVIVES (permutation null, Part 0.2 rule)
    # =========================================================================
    lean_c_rows = []
    for row in cosine_rows_norm:
        lean_c_rows.append(
            {
                "pair": row["pair"],
                "cosine_offset_normalized": row["cosine_offset"],
                "perm_null_median": row["perm_null_median"],
                "perm_null_q95": row["perm_null_q95"],
                "at_or_below_perm_q95": row["at_or_below_perm_q95"],
            }
        )
    lean_c_held = all(row["at_or_below_perm_q95"] for row in lean_c_rows)
    lean_c = {
        "statement": (
            "SURVIVES iff, for all 3 world pairs, the normalized-metric "
            "offset cosine lies at or below the within-role permutation "
            "null's 95th percentile (Part 0.2's adopted operationalization "
            "of 'world-specific at the permutation null')"
        ),
        "rows": lean_c_rows,
        "held": bool(lean_c_held),
        "cosine_identity_vs_raw_max_abs_diff": cosine_identity_max,
    }

    # =========================================================================
    # PIVOT -- every subspace share moves <=10 points, registered order, every world
    # =========================================================================
    pivot_rows = []
    for w in worlds:
        raw_shares = partials[w]["raw"]["registered_shares"]
        norm_shares = partials[w]["normalized"]["registered_shares"]
        for name in raw_shares:
            pivot_rows.append(
                {
                    "world": w,
                    "subspace": name,
                    "raw_share": raw_shares[name],
                    "normalized_share": norm_shares[name],
                    "abs_diff_points": abs(raw_shares[name] - norm_shares[name]) * 100.0,
                }
            )
    pivot_max_move_points = max(row["abs_diff_points"] for row in pivot_rows)
    pivot_fires = bool(pivot_max_move_points <= LEAN_A_MOVE_BAR * 100.0)
    pivot = {
        "registered": (
            "every subspace share moves by <= 10 points -> M4-E2's "
            "decomposition was units-robust after all; its picture stands "
            "as structural, the debt is paid, and the basis line proceeds "
            "directly from it"
        ),
        "rows": pivot_rows,
        "max_move_points": pivot_max_move_points,
        "bar_points": LEAN_A_MOVE_BAR * 100.0,
        "fires": pivot_fires,
    }

    if pivot_fires:
        verdict = "PIVOT_UNITS_ROBUST_ATTRIBUTION_STANDS"
    elif lean_a_held:
        verdict = "ATTRIBUTION_MOVES_UNDER_VALID_UNITS"
    else:
        verdict = "PARTIAL_NEITHER_LEAN_A_NOR_PIVOT"

    # =========================================================================
    # G0 POWER (stated with the target level cited from M4-E2's persisted
    # artifacts and the MDE, per the fifth standing rule -- see module
    # docstring for the full justification of why WORLD is the grain and why
    # "power" here is a numerical-precision statement, not a sampling one)
    # =========================================================================
    g0 = {
        "statement": (
            "deterministic recomputation on M4-E2's 3 registered worlds (a "
            "census, not a sample); WORLD is the grain because it is the "
            "only one at which a world's own decomposition share is defined "
            "(GPA consensus collapses 8 reps into one Delta before any "
            "share exists) -- matching M4-E2's own non-CI, world-level "
            "point-comparison design for the identical leans/pivot"
        ),
        "target_level_from_e2_persisted": {
            "S3_registered_order_share_range": [0.2953, 0.3830],
            "S4_residual_registered_order_share_range": [0.4015, 0.4464],
            "offset_cosine_range": [0.4159, 0.4523],
            "perm_null_q95_range": [0.4666, 0.4752],
        },
        "bar_points": LEAN_A_MOVE_BAR * 100.0,
        "realized_max_share_identity_abs_diff": identity_max,
        "realized_max_cosine_identity_abs_diff": cosine_identity_max,
        "margin_vs_bar": (
            f"{LEAN_A_MOVE_BAR / max(identity_max, EPS):.3e}x the registered "
            "10-point bar, from the Part 0.1 algebraic proof confirmed "
            "empirically -- not sampling luck"
        ),
        "underpowered": False,
    }

    # =========================================================================
    # G3 -- not applicable (stated explicitly)
    # =========================================================================
    g3 = {
        "statement": (
            "NOT APPLICABLE: this leg constructs no truth-referenced "
            "regeneration path (no budget/events regeneration, no D_true "
            "comparison); its adjudicated quantities are pure functions of "
            "the already-validated Delta object, re-verified by G1 ANCHOR"
        ),
        "applicable": False,
    }

    g4 = {
        "statement": "materiality-form compliance stated per gate",
        "G0": "numerical-precision margin statement (deterministic recomputation, no sampling distribution)",
        "G1": "equivalence/margin bound, <=1e-12 (shares/offset/cosines) and <=1e-9 (GM_world)",
        "G2": "liveness ('must differ') form, same polarity as M4-G1/M4-G4/M4-G5's own G2 gates",
        "G3": "not applicable, stated explicitly",
        "lean_a_pivot": "point-difference against a registered 10-percentage-point margin (M4-E2's own leans used the identical unhedged point-comparison form at this grain)",
        "lean_b": "categorical (largest-piece identity), matching M4-E2's own registered-order finding",
        "lean_c": "at-or-below-null-q95 form, Part 0.2's own registered operationalization",
    }

    # ---- outputs -------------------------------------------------------------
    decision = {
        "estimand_id": "SUICA_M4_H1_NORMALIZED_DECOMPOSITION",
        "tier": "EXPLORATORY (open-exploration phase)",
        "registered_in": (
            "docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md M4-H1 registration "
            "(2026-08-03, BEFORE run); ledger row M4-H1"
        ),
        "worlds": worlds,
        "part_0_1_proof": (
            "every adjudicated statistic is a ratio of squared/nuclear norms "
            "of linear images of Delta under FIXED, Delta-independent bases, "
            "hence homogeneous of degree 0 in any global per-world scalar "
            "applied to Delta -- READING A (Delta/GM_world) and READING B "
            "(no-op) are algebraically forced to the same shares/cosines; "
            "see module docstring Part 0.1 for the full derivation"
        ),
        "gates": {"G0": g0, "G1": g1_anchor, "G2": g2, "G3": g3, "G4": g4},
        "lean_a": lean_a,
        "lean_b": lean_b,
        "lean_c": lean_c,
        "pivot": pivot,
        "verdict": verdict,
        "world_gm_by_world": {w: partials[w]["world_gm"] for w in worlds},
        "offset_norm_by_world": {
            w: {"raw": partials[w]["offset_norm"], "normalized": partials[w]["offset_norm_normalized"]}
            for w in worlds
        },
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only (M4-E2's own 3 HIGH_GAP_WORLDS); "
            "no truth-referenced diagnostic in this leg (see G3); no natural-text, "
            "personality, or clinical claim; no seal, no independent verification "
            "(operator directive 2026-08-01)."
        ),
    }

    output.mkdir(parents=True, exist_ok=True)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    with (output / "gates.json").open("w", encoding="utf-8") as handle:
        json.dump(
            {"G0": g0, "G1": g1_anchor, "G2": g2, "G3": g3, "G4": g4},
            handle,
            indent=2,
            sort_keys=True,
            default=str,
        )
        handle.write("\n")

    decomposition_frame.to_csv(output / "decomposition_rows_both_metrics.csv", index=False)
    share_anchor_frame.to_csv(output / "g1_share_anchor_rows.csv", index=False)
    offset_anchor_frame.to_csv(output / "g1_offset_anchor_rows.csv", index=False)
    cosine_anchor_frame.to_csv(output / "g1_cosine_anchor_rows.csv", index=False)
    gm_joined.to_csv(output / "gm_rows_with_g2_anchor.csv", index=False)
    identity_frame.to_csv(output / "share_identity_check.csv", index=False)
    pd.DataFrame(cosine_rows_raw).assign(metric="raw").to_csv(
        output / "cosine_rows_raw.csv", index=False
    )
    pd.DataFrame(cosine_rows_norm).assign(metric="normalized").to_csv(
        output / "cosine_rows_normalized.csv", index=False
    )
    pd.concat(
        [
            pd.DataFrame(cosine_rows_raw).assign(metric="raw"),
            pd.DataFrame(cosine_rows_norm).assign(metric="normalized"),
        ],
        ignore_index=True,
    ).to_csv(output / "cosine_rows_both_metrics.csv", index=False)
    pd.DataFrame(lean_a_rows).to_csv(output / "lean_a_rows.csv", index=False)
    pd.DataFrame(pivot_rows).to_csv(output / "pivot_rows.csv", index=False)

    subspace_summary_rows = []
    for w in worlds:
        for metric_name in ("raw", "normalized"):
            source = partials[w][metric_name]
            offset_val = partials[w]["offset_norm"] if metric_name == "raw" else partials[w]["offset_norm_normalized"]
            subspace_summary_rows.append(
                {
                    "world": w,
                    "metric": metric_name,
                    "offset_norm": offset_val,
                    "width": partials[w]["width"],
                    "dominant_subspace": source["dominant_subspace"],
                    "dominant_share": source["dominant_share"],
                    "S1_registered": source["registered_shares"]["S1_safety_complement"],
                    "S2_registered": source["registered_shares"]["S2_supervision_span"],
                    "S3_registered": source["registered_shares"]["S3_norm_scale_modes"],
                    "S4_residual_registered": source["registered_shares"]["S4_residual"],
                    "S3_reverse": source["reverse_shares"]["S3_norm_scale_modes"],
                    "delta_singular_top1_share": source["delta_singular_top1_share"],
                    "width_mismatch_share": source["width_mismatch_share"],
                }
            )
    pd.DataFrame(subspace_summary_rows).to_csv(output / "subspace_rows_both_metrics.csv", index=False)

    print(
        json.dumps(
            {
                "verdict": verdict,
                "g1_pass": g1_anchor["pass"],
                "g1_share_anchor_max_abs_diff": share_anchor_max,
                "g1_offset_anchor_max_abs_diff": offset_anchor_max,
                "g1_cosine_anchor_max_abs_diff": cosine_anchor_max,
                "g1_gm_anchor_max_abs_diff": gm_anchor_max,
                "g2_live": g2["live"],
                "g2_min_relative_diff": g2_min_relative_diff,
                "identity_max_abs_diff": identity_max,
                "cosine_identity_max_abs_diff": cosine_identity_max,
                "lean_a_held": lean_a_held,
                "lean_b_held": lean_b_held,
                "lean_c_held": lean_c_held,
                "pivot_fires": pivot_fires,
                "pivot_max_move_points": pivot_max_move_points,
            },
            indent=2,
        )
    )


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "m4_chart_ecology.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "m4_h1_normalized_decomposition")
    parser.add_argument("--world", type=str, default=None)
    parser.add_argument("--assemble", action="store_true")
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    spec = M4ChartEcologySpec(**config["base_spec"])

    if args.assemble:
        _assemble(args.output, config)
        return

    if args.world is None:
        raise SystemExit("--world is required unless --assemble")
    _run_world(args.world, config, spec, args.output)


if __name__ == "__main__":
    main()
