#!/usr/bin/env python3
"""M4-H6: is the S4 residual attackable at all -- reproducible, or repetition-specific?

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, "M4-H6
registration" (2026-08-03, BEFORE run), preceded by the "M4-H5 planner
adjudication note -- the survivor has a name, and no handle" on the same
date; ledger row M4-H6). Machinery is IMPORTED and REUSED wherever an
existing seam exists: h2 (basis construction, context cache, S3 bases,
generic paired-CI helper via g1), h3/h4 (per-arm dispatch and per-arm
offset+shares, both disclosed near-duplicates of h2's own machinery), h5
(the 2-way arm router `_basis_for_h5_arm`, the G3 world-build spot check
`_g3_spot_check_h5`, the arm name constants), and e2 (S1-S4 sequential
projection, `_procrustes_cosine`, the disclosed random-matrix-null pattern
this leg is explicitly told to avoid using as ITS OWN deciding null). This
leg performs NO new Part 0 audit and touches NO basis-construction formula --
`deployed` and `basis_shrinkage_1.00` are LITERAL calls into h4's own
already-anchored `_basis_for_h4_arm` (via h5's own router), exactly as H5
used them.

===========================================================================
WHAT IS GENUINELY NEW IN THIS LEG (stated precisely, since the registration
delegates "extract the S4 component per (world, repetition)" to this script)
===========================================================================
Every predecessor leg's "Delta" is a WORLD-level object: one offset vector
per (world, arm), built from the GPA (GENERALIZED PROCRUSTES) chordal
Frechet-mean CONSENSUS of that world's 8 repetitions' own frames --
`a_center = pad(consensus_v2, W)`, `delta = a_center - align(pad(consensus_
swap, W), a_center)`. No predecessor leg ever needed a PER-REPETITION analog
of that offset, because no predecessor leg's leans were about cross-
repetition agreement. This leg's entire new-construction surface is that one
per-repetition object, built to be DIRECTLY comparable (i) to the world's own
S1/S2/S3 bases (all three anchored in `a_center`'s own gauge -- S1/S2/n1 are
provably right-O(W)-gauge INVARIANT by construction (pattern (x) full-column-
space span), but S3's n2/n3 families are gauge-EQUIVARIANT, built from
`a_center`'s own realized right-singular-vectors and row-blocks -- so a
per-rep delta expressed in an uncontrolled, rep-native gauge would corrupt
exactly the S3/S4 boundary this leg exists to measure) and (ii) across
repetitions within and between worlds (so the SAME common gauge must be used
for every repetition compared).

Construction (`_delta_rep_in_consensus_gauge`, below), per (world, arm, rep):
  1. NATIVE-GAUGE delta (existing functions only, `leg14._pad`/`leg14._align`,
     the SAME calls every predecessor leg already uses for `disp_v2`):
       delta_native = pad(v2_frame_r) - align(pad(swap_frame_r), pad(v2_frame_r))
     `||delta_native||` is PROVABLY equal to the already-anchored, already-
     gated Leg-11 `disp_v2` value for that (world, rep, arm) -- the optimal
     Procrustes alignment distance `min_R ||A - BR||_F` is SYMMETRIC in (A,B)
     (both equal `sqrt(||A||^2+||B||^2-2*nuclear_norm(A^T B))`), so this is
     algebraically the SAME scalar `leg14._quotient_distance(swap_frame,
     v2_frame)` already persists in every predecessor's `disp_rows.csv`, via
     a differently-ordered (but exactly equal) computation -- gated below at
     `e2.DISPLACEMENT_ANCHOR_TOLERANCE` (1e-9, E2's own tolerance for this
     exact class of check: two independently-derived computations of the same
     symmetric quantity).
  2. GAUGE ROTATION: `R_r`, the SAME orthogonal matrix `leg14._align` uses to
     bring `pad(v2_frame_r)` onto `a_center` (extracted explicitly via
     `_procrustes_rotation`, a disclosed 3-line near-duplicate of `leg14.
     _align`'s own SVD body -- `_align` does not expose `R` itself, only
     `frame @ R`). Gated: `pad(v2_frame_r) @ R_r` must equal `leg14._align
     (pad(v2_frame_r), a_center)` (the EXISTING function, called independently)
     to <=1e-12 -- this is not two different computations of a symmetric
     quantity, it is the SAME SVD evaluated twice, so exact (floating-point)
     equality is the correct, tight bar.
  3. `delta_rep = delta_native @ R_r`. This is NOT an approximation or a
     second, independent alignment of swap onto `a_center` (which would
     silently corrupt the rep's own v2-vs-swap relative geometry, since
     independently aligning v2 and swap to a THIRD reference in general uses
     TWO DIFFERENT rotations). It is the ALGEBRAIC IDENTITY
       align(B @ R, A @ R) = align(B, A) @ R      for any orthogonal R,
     applied with `A = pad(v2_frame_r)`, `B = pad(swap_frame_r)`, `R = R_r`:
     because orthogonal Procrustes alignment commutes with a SHARED right-
     orthogonal transform (proof: for orthogonal R, `||AR - BR@Q||_F =
     ||A - B@(R Q R^T)||_F` for every Q in O(W), and conjugation by R is a
     bijection on O(W), so the argmin over Q corresponds exactly to the
     argmin over the original problem, conjugated), `delta_rep` is EXACTLY
     "rigidly rotate the (v2_frame_r, swap_frame_r) PAIR together into
     `a_center`'s gauge, preserving their mutual geometry" -- not two
     independent, geometry-corrupting alignments. `||delta_rep||` therefore
     equals `||delta_native||` exactly (rotation preserves the Frobenius
     norm) -- gated at <=1e-12 as a cheap internal consistency check.
This is a disclosed EXTENSION of the exact pattern M4-E2's own "diagnostic
refit" task (task 4 of that leg) already uses -- `frame_aligned = leg14.
_align(leg14._pad(v2_frames[repetition], width), a_center)` -- BEFORE
computing anything relative to an `a_center`-anchored quantity (there:
`u_dom`, one single direction; here: the FULL S1-S4 decomposition of the
rep's own v2-vs-swap DIFFERENCE, not just its v2 frame alone).

Once `delta_rep` is in `a_center`'s gauge, `e2._sequential_shares(delta_rep,
bases, e2.SUBSPACE_NAMES)` -- the SAME function, SAME `bases` dict (built
once per (world, arm) exactly as every predecessor leg builds it), called on
a DIFFERENT vector -- is REUSED VERBATIM to extract `S4_residual`'s own
component vector for that repetition. No new decomposition machinery exists
anywhere in this file; the only new code is the per-rep DELTA CONSTRUCTION
above (a coordinate-frame bookkeeping step), never the S1/S2/S3/S4 math.

--- Scope decision (disclosed, BEFORE compute): registered order only ------
Unlike M4-H5, this leg's own registration never mentions ordering
sensitivity (no "both orderings" instruction in the M4-H6 Design/Leans/
Gates), and the leans/pivot are stated purely in terms of "S4's ... direction"
without a reverse-order companion requested. This leg therefore computes and
adjudicates REGISTERED order only (S1->S2->S3->S4, this line's own primary
convention since M4-E2). Reverse order is NOT computed here -- a scope
decision made explicitly before compute, not an oversight, and not a
retreat from a finding: nothing in this leg's own results depends on it.

--- Scope decision (disclosed, BEFORE compute): no truth-recovery machinery
Directly citing M4-H5's own identical, already-adjudicated precedent: this
leg's registered Design/Leans/Gates never mention `TRUTH_BUDGETS` or
truth-referenced recovery. Reading A (ADOPTED, same as H5): out of scope,
oracle-stage regeneration loop skipped entirely. G3 "truth-path invariance
where applicable" is satisfied, as in H5, by a lightweight world-build
faithfulness spot-check (`h5._g3_spot_check_h5`, called UNCHANGED, filtered
to this leg's 2 arms) that does not gate any lean.

===========================================================================
THE REGISTERED NULL (Part 0, before compute) -- "repetition-shuffled",
never a synthetic-random-matrix null and never zero
===========================================================================
M4-E2 disclosed that `_procrustes_cosine(first, second) = nuclear_norm(first^T
second) / (||first|| ||second||)` is a SUM OF SINGULAR VALUES divided by a
norm product -- ALWAYS >= 0 by construction (singular values are
non-negative), and INFLATED even for two INDEPENDENT random Gaussian
matrices of this shape (E2's own `random_null`, reused below as a disclosed,
non-deciding companion). Comparing a real agreement number to a raw "0" or to
a synthetic-random-matrix null would therefore either overstate or
mischaracterize any real finding. The task's registration requires the
DECIDING comparator to be a REPETITION-SHUFFLED null instead, registered
here as follows.

Pool, per arm, the 24 real, already-computed `S4_residual` component vectors
(3 `HIGH_GAP_WORLDS` x 8 repetitions), in a FIXED order `k = world_index*8 +
repetition` (`world_index` per `WORLDS` below). Draw `NULL_DRAWS=200`
independent random permutations of `{0..23}` (SHARED across both arms -- the
SAME 200 permutations are applied to each arm's own 24 REAL vectors, so
arm-to-arm comparisons are not muddied by independent permutation noise).
For each permutation, chunk into 3 groups of 8 (matching the true world
sizes) -- this randomly REASSIGNS which repetition's REAL, already-computed
S4 vector sits in which pseudo-world, destroying any TRUE within-world
correspondence while using only REAL empirical vectors (so whatever
"inflation" the statistic carries from S4's own realized rank/shape is
IDENTICALLY present in both the real statistic and this null -- exactly the
apples-to-apples comparison M4-E2's disclosure demands, and exactly why a
synthetic-random-matrix comparator would NOT do this validly). Within each
pseudo-group, compute all C(8,2)=28 pairwise `|_procrustes_cosine|` values
(already non-negative, so "absolute value" in the registration's own words
is automatically satisfied -- no extra `abs()` is applied or needed);
pool all 3*28=84 values for that draw and take their mean -- ONE null value
per draw, 200 per arm. This SAME null distribution (median, q95) is the
comparator for EVERY agreement number this leg reports -- within-world
(lean a) and across-world (lean b) alike, per the registration's explicit
instruction ("It must be the comparison for every agreement number").

G2 NULL LIVENESS (registered as its own gate, kept deliberately separate
from the leans themselves so it is not circular with them): report the null
distribution's own spread (min/q05/median/q95/max/std across its 200 draws)
and confirm it is non-degenerate (std bounded away from 0 -- "a null that
does not move is not a null") and sits comfortably below the trivial ceiling
of 1.0 (self-identical cosine) -- i.e. that random re-grouping of REAL
vectors produces a genuine, varying, sub-maximal distribution rather than a
frozen or trivial one. The disclosed random-matrix-null companion (E2's own
construction, reused verbatim on the same (48, width) shape) is reported
alongside as context for the magnitude of M4-E2's disclosed inflation, and
is explicitly labelled NOT the deciding comparator anywhere in this report.

===========================================================================
DESIGN (registered)
===========================================================================
Worlds: h2's own three `HIGH_GAP_WORLDS` (unchanged). Arms: `deployed`
(reference) and `basis_shrinkage_1.00` (M4-H4's HARMLESS winner, cited by
name, unchanged) -- both literal calls into h5's own `_basis_for_h5_arm`
router, itself a literal call into h4's own `_basis_for_h4_arm`. Per
(world, arm): world-level offset/shares (disclosed near-duplicate of h3's/
h4's own `_arm_offset_and_shares_h{3,4}`, the ONLY change being the extra
per-repetition extraction appended after the existing, UNCHANGED world-level
computation) and 8 per-repetition `S4_residual` component vectors.

--- Grain (fifth standing rule: justify, don't inherit) --------------------
The agreement statistic (Procrustes cosine of TWO S4 vectors) is inherently
defined PER PAIR of repetitions, not per single repetition -- mirroring this
line's own established principle of adopting the metric's own natural finest
unit (H2's own adoption of REP grain for `disp_v2` because "disp_v2 is
already a per-rep quantity"; here, the natural finest unit is the PAIR).
WITHIN-WORLD grain: n=28 pairs (C(8,2), one world, one arm). ACROSS-WORLD
grain: n=64 pairs per world-pair (8x8), n=192 pooled over the 3 world-pairs
(PRIMARY, since the registration states the lean as a single "sits at or
below" test); per-world-pair breakdown reported as a disclosed companion,
mirroring E2's own task-3 per-pair convention. CI: `g1._paired_world_ci`
(this line's own generic one-sample t-CI helper, reused unchanged -- it is
a plain t-CI on whatever array it is given, "paired" in name only from its
original call site, not in mechanism) applied directly to the pair-level
array at each grain -- the SAME simplicity convention this entire line uses
throughout (rep grain n=24 pools 3 worlds' reps as i.i.d. for an ordinary
t-CI; author grain n up to 384 pools views x authors x worlds the same way).
No new statistical machinery is introduced for the CI itself.

Leans (registered; evaluated at `basis_shrinkage_1.00`; `deployed` reported
as a disclosed, non-adjudicating reference/companion throughout).
(a) REPRODUCIBLE WITHIN WORLD: per world, HELD iff the within-world CI's
    lower bound exceeds the null's q95 (`ci_lo > null_q95`); lean (a) HOLDS
    iff >=2 of 3 worlds are HELD.
(b) NOT ACROSS WORLDS (the control): HELD iff the POOLED across-world CI's
    upper bound sits at/below the null's q95 (`ci_hi <= null_q95`) --
    applying the SAME CI-based equivalence logic as lean (a) rather than a
    bare point-estimate comparison, per G4 MATERIALITY FORM's own requirement
    that every gate be an equivalence/margin bound; the raw point-estimate
    reading is reported alongside as a disclosed cross-check.
(c) MATERIAL ENOUGH TO CAPTURE: for every world where lean (a) HELD, HELD
    iff that world's own point-estimate mean >= 0.5 (ADOPTED reading: ALL
    qualifying worlds must clear the bar, not merely one -- disclosed,
    since the registration does not itself state a count rule here).

PIVOT-IF lean (a) MISSES (< 2 of 3 worlds HELD) -> S4 IS REPETITION-SPECIFIC
AND NOT ATTACKABLE BY ANY BASIS CONSTRUCTION -- written with the prominence
of a discovery per the outer task's explicit instruction, not as a shortfall.

Gates: G0 POWER (null spread + MDE stated from the null's own pair-level
variance, BEFORE the real within/across comparisons are adjudicated -- see
`_assemble`'s ordering); G1 ANCHOR (world-level shares/displacement to
<=1e-12 against E2's/H4's own persisted values, registered-literal +
disclosed superset, mirroring H5's own pattern exactly; PLUS a new,
additional per-repetition delta-construction consistency check, described
above, tying this leg's own new machinery to already-anchored `disp_v2`
values); G2 NULL LIVENESS (above); G3 world-build faithfulness (scope-reduced,
non-gating, citing H5's own precedent); G4 MATERIALITY FORM (equivalence/
margin form stated per gate, in the report).

Chunked execution (process rule -- foreground, explicit long timeouts, no
background jobs, no monitors): `--world W --stage g3`, `--world W --arm A`,
`--assemble`, `--smoke`. Every per-(world,arm)/per-world stage is idempotent
(skips if its partial already exists). Contexts are built FRESH in this
leg's own output directory (not a copy of h2's/h3's/h4's/h5's cache), so G1
is a real end-to-end test, exactly as every predecessor leg's own docstring
states for itself.
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
from scipy import stats as scipy_stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_suica_m4_h2_basis_normalization as h2  # noqa: E402  bit-exact reuse of every seam
import run_suica_m4_h3_safe_lever_ladder as h3  # noqa: E402  bit-exact reuse (h3.h2 is the SAME object as h2 above)
import run_suica_m4_h4_safe_ceiling as h4  # noqa: E402  bit-exact reuse (h4.h3/h4.h2 are the SAME objects)
import run_suica_m4_h5_residual_carrier as h5  # noqa: E402  arm router + G3 spot check, reused verbatim
import run_suica_m4_g1_whitening_intervention as g1  # noqa: E402  generic paired-CI helper

from suica_core.m4_chart_ecology_generator import M4ChartEcologySpec  # noqa: E402

# ---------------------------------------------------------------------------
# registered arms, worlds and parameters (Part 0, above)
# ---------------------------------------------------------------------------

DEPLOYED_ARM = h5.DEPLOYED_ARM              # "deployed" (reference, disclosed companion)
HARMLESS_ARM = h5.HARMLESS_ARM              # "basis_shrinkage_1.00" -- M4-H4's HARMLESS winner; leans evaluated here
ARMS: tuple[str, ...] = (DEPLOYED_ARM, HARMLESS_ARM)
assert HARMLESS_ARM in h4.RATIO_BY_ARM, "HARMLESS_ARM must be one of H4's own new ratios"

WORLDS: tuple[str, ...] = tuple(h2.HIGH_GAP_WORLDS)
REPETITIONS = 8  # asserted against config in main()
N_GROUPS = len(WORLDS)
GROUP_SIZE = REPETITIONS
N_POOLED = N_GROUPS * GROUP_SIZE  # 24

G1_ANCHOR_TOLERANCE = h2.G1_ANCHOR_TOLERANCE          # 1e-12 -- same-computation exactness
DISPLACEMENT_ANCHOR_TOLERANCE = h2.e2.DISPLACEMENT_ANCHOR_TOLERANCE  # 1e-9 -- E2's own tolerance for two
                                                       # independently-ordered computations of the same
                                                       # symmetric Procrustes distance
G3_TOLERANCE = h2.G3_TOLERANCE                        # 1e-12

NULL_DRAWS = h2.e2.NULL_DRAWS                         # 200, E2's own convention, reused unchanged
REP_SHUFFLE_NULL_SEED_TAG = 1611                       # this leg's own tag (distinct from E2's 1409/1410)
RANDOM_MATRIX_NULL_SEED_TAG = 1612                     # disclosed companion only, never the decider

PIVOT_MIN_WORLDS_HELD = 2       # registered: ">= 2 of 3 worlds"
LEAN_C_MATERIALITY_BAR = 0.5    # registered

SUBSPACE_NAMES = h2.e2.SUBSPACE_NAMES  # (S1_safety_complement, S2_supervision_span, S3_norm_scale_modes)

H4_DISP_ROWS_PATH = h5.H4_DISP_ROWS_PATH
H4_OFFSET_SHARES_PATH = h5.H4_OFFSET_SHARES_PATH
H4_DECISION_PATH = h5.H4_DECISION_PATH
H3_DISP_ROWS_PATH = h5.H3_DISP_ROWS_PATH
E2_DECISION_PATH = h2.E2_DECISION_PATH


# ---------------------------------------------------------------------------
# this leg's ONLY new construction: per-repetition delta in the world's own
# consensus gauge (see docstring for the full derivation and justification)
# ---------------------------------------------------------------------------


def _procrustes_rotation(frame: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Disclosed near-duplicate of leg14._align's 3-line SVD body
    (scripts/run_suica_m4_d_displacement_leg14.py:310-314), returning the
    rotation matrix R itself (frame @ R == leg14._align(frame, target)) so
    the SAME rotation can be applied to a second, paired matrix -- leg14.
    _align only returns the rotated frame, never R on its own."""
    left, _, right_t = np.linalg.svd(frame.T @ target)
    return left @ right_t


def _delta_rep_in_consensus_gauge(
    v2_frame_r: np.ndarray, swap_frame_r: np.ndarray, a_center: np.ndarray, width: int,
) -> tuple[np.ndarray, dict[str, float]]:
    """Returns (delta_rep, diagnostics). See module docstring for the full
    derivation: delta_native = pad(v2_r) - align(pad(swap_r), pad(v2_r))
    (||delta_native|| == the already-persisted Leg-11 disp_v2 anchor, by the
    symmetry of the Procrustes alignment distance); R_r = the rotation
    leg14._align uses to bring pad(v2_r) onto a_center; delta_rep =
    delta_native @ R_r (== rigidly rotating the (v2_r, swap_r) PAIR into
    a_center's gauge together, preserving their mutual geometry, by the
    align(B@R,A@R) = align(B,A)@R identity)."""
    v2_padded = h2.leg14._pad(v2_frame_r, width)
    swap_padded = h2.leg14._pad(swap_frame_r, width)

    swap_aligned_native = h2.leg14._align(swap_padded, v2_padded)
    delta_native = v2_padded - swap_aligned_native
    native_norm = float(np.linalg.norm(delta_native))

    rotation = _procrustes_rotation(v2_padded, a_center)
    v2_in_gauge_direct = h2.leg14._align(v2_padded, a_center)   # existing function, independent call
    v2_in_gauge_via_rotation = v2_padded @ rotation
    rotation_extraction_gate = float(np.max(np.abs(v2_in_gauge_direct - v2_in_gauge_via_rotation)))

    delta_rep = delta_native @ rotation
    gauge_norm = float(np.linalg.norm(delta_rep))

    return delta_rep, {
        "native_norm": native_norm,
        "gauge_norm": gauge_norm,
        "rotation_extraction_gate": rotation_extraction_gate,
        "norm_preserved_gate": abs(native_norm - gauge_norm),
    }


# ---------------------------------------------------------------------------
# per-arm world-level offset/shares (disclosed near-duplicate of h3's/h4's
# own _arm_offset_and_shares_h{3,4}, the ONLY changes: (1) dispatch via h5's
# own 2-way router; (2) the per-repetition S4 extraction appended AFTER the
# existing, UNCHANGED world-level computation)
# ---------------------------------------------------------------------------


def _arm_offset_shares_and_reps_h6(
    world: str, contexts: list[dict[str, Any]], arm: str, s1_patterns: np.ndarray, s2_patterns: np.ndarray,
) -> dict[str, Any]:
    v2_frames, swap_frames, disp_rows = [], [], []
    for context in contexts:
        basis, _, meta = h5._basis_for_h5_arm(context, arm)
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

    # ---- world-level (UNCHANGED machinery, identical to h3/h4/h5) ---------
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

    # ---- NEW: per-repetition S4 extraction (this leg's only new math input,
    # ---- and even this is only a coordinate-frame step -- the projection
    # ---- itself is e2._sequential_shares, reused verbatim, see docstring) --
    per_rep: list[dict[str, Any]] = []
    for idx, context in enumerate(contexts):
        delta_rep, diag = _delta_rep_in_consensus_gauge(v2_frames[idx], swap_frames[idx], a_center, width)
        rep_shares = h2.e2._sequential_shares(delta_rep, bases, h2.e2.SUBSPACE_NAMES)
        anchor_disp = disp_rows[idx]["disp_v2"]
        per_rep.append({
            "repetition": int(context["repetition"]),
            "S4_component": rep_shares["components"]["S4_residual"],
            "S4_share": float(rep_shares["shares"]["S4_residual"]),
            "delta_rep_norm": diag["gauge_norm"],
            "native_norm_vs_disp_v2_anchor_absdiff": abs(diag["native_norm"] - anchor_disp),
            "gauge_rotation_extraction_gate": diag["rotation_extraction_gate"],
            "delta_rep_norm_preserved_gate": diag["norm_preserved_gate"],
        })
    per_rep.sort(key=lambda row: row["repetition"])

    return {
        "arm": arm, "world": world, "disp_rows": disp_rows,
        "offset_norm": offset_norm, "width": width,
        "registered_shares": registered["shares"], "reverse_shares": reverse["shares"],
        "standalone_shares": standalone, "s3_family_shares": s3_family_shares,
        "gpa_v2_basins": int(gpa_v2["n_distinct_basins"]), "gpa_swap_basins": int(gpa_swap["n_distinct_basins"]),
        "gpa_v2_fixed_point_residual": gpa_v2["max_fixed_point_residual_over_starts"],
        "gpa_swap_fixed_point_residual": gpa_swap["max_fixed_point_residual_over_starts"],
        "per_rep": per_rep,
    }


# ---------------------------------------------------------------------------
# stages: g3, arm, smoke (no "oracle" stage -- scope reduction, docstring)
# ---------------------------------------------------------------------------


def _run_g3_h6(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    partial_path = output / f"partial_g3_{world}.csv"
    if partial_path.exists():
        print(f"[m4h6] SKIP (partial exists): g3 {world}", flush=True)
        return
    contexts = h2._contexts_for_world(world, config, spec, output)
    rows = [row for row in h5._g3_spot_check_h5(world, contexts, spec) if row["arm"] in ARMS]
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(partial_path, index=False)
    print(f"[m4h6] g3 stage done: {world} ({time.time() - started:.1f}s total)", flush=True)


def _run_arm_h6(world: str, arm: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    partial_path = output / f"partial_arm_{world}_{arm}.json"
    components_path = output / f"partial_components_{world}_{arm}.pkl"
    if partial_path.exists() and components_path.exists():
        print(f"[m4h6] SKIP (partial exists): {world} {arm}", flush=True)
        return
    contexts = h2._contexts_for_world(world, config, spec, output)

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

    result = _arm_offset_shares_and_reps_h6(world, contexts, arm, s1_patterns, s2_patterns)

    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(result["disp_rows"]).to_csv(output / f"partial_disp_{world}_{arm}.csv", index=False)
    with components_path.open("wb") as handle:
        pickle.dump(result["per_rep"], handle)
    summary = {k: v for k, v in result.items() if k not in ("disp_rows", "per_rep")}
    with partial_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    print(f"[m4h6] arm stage done: {world} {arm} ({time.time() - started:.1f}s total)", flush=True)


def _run_smoke_h6(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    t0 = time.time()
    world_index = {name: index for index, name in enumerate(config["worlds"])}[world]
    expected_for = h2.leg8._expected_geometries_lookup(config)
    seed = h2.leg3._world_seed(int(config["seed"]), 0, world, world_index)
    context = h2.leg4._build_context(
        world, 0, seed, spec=spec, config=config, expected_geometries=expected_for(world, 0, seed),
    )
    print(f"[m4h6 smoke] context built ({time.time() - t0:.1f}s)", flush=True)

    widths: dict[str, int] = {}
    for arm in ARMS:
        t1 = time.time()
        basis, _, meta = h5._basis_for_h5_arm(context, arm)
        widths[arm] = int(basis["calibration"].shape[1])
        if arm == DEPLOYED_ARM:
            gap = max(float(np.max(np.abs(basis[role] - context["v2_basis"][role]))) for role in h2.ROLES)
            print(f"[m4h6 smoke] deployed basis vs context v2_basis max|diff|={gap:.3e}", flush=True)
            assert gap <= G1_ANCHOR_TOLERANCE, f"deployed basis reconstruction fails G1 anchor: {gap:.3e}"
        print(f"[m4h6 smoke] arm={arm} width={widths[arm]} meta={meta} ({time.time() - t1:.1f}s)", flush=True)
    assert len(set(widths.values())) == 1, f"unexpected width mismatch across arms: {widths}"
    print(f"[m4h6 smoke] widths by arm (must match): {widths}", flush=True)

    # single-rep, per-arm end-to-end check of the NEW per-repetition delta
    # construction (mechanical/plumbing check -- with only 1 repetition, its
    # own "GPA consensus" is trivially itself, so this cannot exercise real
    # cross-rep gauge divergence; that is what the full 8-rep run is for).
    for arm in ARMS:
        t2 = time.time()
        basis, _, _ = h5._basis_for_h5_arm(context, arm)
        swap_basis = h2.leg9._row_norm_swap(context["truth"].oracle_basis, basis)
        v2_frame = h2.leg11._stack_frame(basis)
        swap_frame = h2.leg11._stack_frame(swap_basis)
        width = v2_frame.shape[1]
        a_center = h2.leg14._pad(v2_frame, width)
        delta_rep, diag = _delta_rep_in_consensus_gauge(v2_frame, swap_frame, a_center, width)
        disp_anchor = h2.leg14._quotient_distance(swap_frame, v2_frame)
        native_vs_anchor = abs(diag["native_norm"] - disp_anchor)
        print(
            f"[m4h6 smoke] arm={arm} delta_rep: native_norm={diag['native_norm']:.6f} vs disp_v2 "
            f"anchor={disp_anchor:.6f} (diff={native_vs_anchor:.3e}), "
            f"rotation_gate={diag['rotation_extraction_gate']:.3e}, "
            f"norm_preserved_gate={diag['norm_preserved_gate']:.3e} ({time.time() - t2:.1f}s)",
            flush=True,
        )
        assert native_vs_anchor <= DISPLACEMENT_ANCHOR_TOLERANCE, native_vs_anchor
        assert diag["rotation_extraction_gate"] <= G1_ANCHOR_TOLERANCE, diag["rotation_extraction_gate"]
        assert diag["norm_preserved_gate"] <= G1_ANCHOR_TOLERANCE, diag["norm_preserved_gate"]
        assert delta_rep.shape == (48, width)
    print(f"[m4h6 smoke] TOTAL ({time.time() - t0:.1f}s)", flush=True)


# ---------------------------------------------------------------------------
# null construction + agreement statistics (assemble-time only; no per-
# (world,arm) compute needed, since these operate on already-persisted
# per-repetition components)
# ---------------------------------------------------------------------------


def _all_pairs_cosine(vectors: list[np.ndarray]) -> np.ndarray:
    out = []
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            out.append(h2.e2._procrustes_cosine(vectors[i], vectors[j]))
    return np.asarray(out, dtype=float)


def _generate_null_permutations(n_total: int, n_draws: int, rng: np.random.Generator) -> list[np.ndarray]:
    return [rng.permutation(n_total) for _ in range(n_draws)]


def _repetition_shuffled_null_for_arm(
    pooled_vectors: list[np.ndarray], permutations: list[np.ndarray], group_size: int, n_groups: int,
) -> dict[str, Any]:
    draw_values = []
    all_pairs: list[float] = []
    for perm in permutations:
        draw_pairs: list[float] = []
        for g in range(n_groups):
            idx = perm[g * group_size:(g + 1) * group_size]
            group_vectors = [pooled_vectors[i] for i in idx]
            draw_pairs.extend(_all_pairs_cosine(group_vectors).tolist())
        draw_values.append(float(np.mean(draw_pairs)))
        all_pairs.extend(draw_pairs)
    draw_values = np.asarray(draw_values, dtype=float)
    all_pairs = np.asarray(all_pairs, dtype=float)
    return {
        "n_draws": len(permutations), "draw_values": draw_values,
        "median": float(np.median(draw_values)), "q05": float(np.quantile(draw_values, 0.05)),
        "q95": float(np.quantile(draw_values, 0.95)), "min": float(np.min(draw_values)),
        "max": float(np.max(draw_values)), "std": float(np.std(draw_values, ddof=1)),
        "pair_mean": float(np.mean(all_pairs)), "pair_std": float(np.std(all_pairs, ddof=1)),
        "n_pairs_total": int(all_pairs.size),
    }


def _random_matrix_null(shape: tuple[int, int], n_draws: int, rng: np.random.Generator) -> dict[str, Any]:
    """Disclosed companion ONLY (E2's own construction, `random_null` in
    run_suica_m4_e2_offset_anatomy.py, reused verbatim on this leg's own S4
    component shape) -- NEVER the deciding comparator for any lean here."""
    values = []
    for _ in range(n_draws):
        first = rng.standard_normal(shape)
        second = rng.standard_normal(shape)
        values.append(h2.e2._procrustes_cosine(first, second))
    values = np.asarray(values, dtype=float)
    return {
        "n_draws": n_draws, "median": float(np.median(values)), "q95": float(np.quantile(values, 0.95)),
        "min": float(np.min(values)), "max": float(np.max(values)), "std": float(np.std(values, ddof=1)),
    }


def _achievable_half_width(pair_std: float, n: int) -> float:
    if n < 2 or not np.isfinite(pair_std):
        return float("nan")
    se = pair_std / np.sqrt(n)
    t_crit = float(scipy_stats.t.ppf(0.975, df=n - 1))
    return t_crit * se


def _within_world_agreement(components_by_world: dict[str, list[np.ndarray]]) -> dict[str, dict[str, Any]]:
    out = {}
    for world, vectors in components_by_world.items():
        pairs = _all_pairs_cosine(vectors)
        ci = g1._paired_world_ci(pairs)
        out[world] = {"n_pairs": int(pairs.size), **ci}
    return out


def _across_world_agreement(
    components_by_world: dict[str, list[np.ndarray]], worlds_order: list[str],
) -> dict[str, Any]:
    per_pair_rows = []
    pooled: list[float] = []
    pooled_pair_rows: list[dict[str, Any]] = []
    for i in range(len(worlds_order)):
        for j in range(i + 1, len(worlds_order)):
            w1, w2 = worlds_order[i], worlds_order[j]
            vals: list[float] = []
            for r1, v1 in enumerate(components_by_world[w1]):
                for r2, v2 in enumerate(components_by_world[w2]):
                    cos = float(h2.e2._procrustes_cosine(v1, v2))
                    vals.append(cos)
                    pooled_pair_rows.append({"world_1": w1, "repetition_1": r1, "world_2": w2, "repetition_2": r2, "cosine": cos})
            pooled.extend(vals)
            vals_arr = np.asarray(vals, dtype=float)
            ci = g1._paired_world_ci(vals_arr)
            per_pair_rows.append({"world_pair": f"{w1}|{w2}", "n_pairs": int(vals_arr.size), **ci})
    pooled_arr = np.asarray(pooled, dtype=float)
    pooled_ci = g1._paired_world_ci(pooled_arr)
    return {
        "per_world_pair": per_pair_rows,
        "pooled": {"n_pairs": int(pooled_arr.size), **pooled_ci},
        "pair_rows": pooled_pair_rows,
    }


# ---------------------------------------------------------------------------
# assemble + adjudicate
# ---------------------------------------------------------------------------


def _assemble(output: Path, config: dict[str, Any]) -> None:
    worlds = list(WORLDS)
    for world in worlds:
        for arm in ARMS:
            if not (output / f"partial_disp_{world}_{arm}.csv").exists():
                raise RuntimeError(f"missing partial: partial_disp_{world}_{arm}.csv")
            if not (output / f"partial_arm_{world}_{arm}.json").exists():
                raise RuntimeError(f"missing arm summary: partial_arm_{world}_{arm}.json")
            if not (output / f"partial_components_{world}_{arm}.pkl").exists():
                raise RuntimeError(f"missing components: partial_components_{world}_{arm}.pkl")
        if not (output / f"partial_g3_{world}.csv").exists():
            raise RuntimeError(f"missing G3 spot check for {world}")

    disp_rows = pd.concat([pd.read_csv(output / f"partial_disp_{w}_{a}.csv") for w in worlds for a in ARMS], ignore_index=True)
    g3_rows = pd.concat([pd.read_csv(output / f"partial_g3_{w}.csv") for w in worlds], ignore_index=True)
    arm_summaries = {(w, a): h2._load_json(output / f"partial_arm_{w}_{a}.json") for w in worlds for a in ARMS}
    per_rep_by_world_arm: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for w in worlds:
        for a in ARMS:
            with (output / f"partial_components_{w}_{a}.pkl").open("rb") as handle:
                per_rep_by_world_arm[(w, a)] = pickle.load(handle)

    expected_disp = len(worlds) * len(ARMS) * REPETITIONS
    if len(disp_rows) != expected_disp:
        raise RuntimeError(f"disp rows {len(disp_rows)} != expected {expected_disp}")
    expected_g3 = len(worlds) * len(ARMS)
    if len(g3_rows) != expected_g3:
        raise RuntimeError(f"g3 rows {len(g3_rows)} != expected {expected_g3}")
    for w in worlds:
        for a in ARMS:
            if len(per_rep_by_world_arm[(w, a)]) != REPETITIONS:
                raise RuntimeError(f"per-rep components for ({w},{a}) has {len(per_rep_by_world_arm[(w, a)])} != {REPETITIONS}")
            widths = {row["S4_component"].shape[1] for row in per_rep_by_world_arm[(w, a)]}
            if widths != {13}:
                raise RuntimeError(f"unexpected S4 component width(s) for ({w},{a}): {widths}")

    # ==== load independently-persisted comparators ==============================
    e2_decision = h2._load_json(E2_DECISION_PATH)
    h4_disp = pd.read_csv(H4_DISP_ROWS_PATH)
    h4_shares = pd.read_csv(H4_OFFSET_SHARES_PATH)
    h3_disp = pd.read_csv(H3_DISP_ROWS_PATH)

    # ==== G1 ANCHOR: world-level (registered-literal + disclosed superset,
    # ==== mirroring H5's own pattern exactly, restricted to this leg's 2 arms)
    e2_share_rows = []
    for w in worlds:
        mine = arm_summaries[(w, DEPLOYED_ARM)]
        theirs = e2_decision["offset_table"][w]
        offset_diff = abs(mine["offset_norm"] - float(theirs["offset_norm"]))
        share_diffs = {name: abs(float(mine["registered_shares"][name]) - float(theirs["registered_shares"][name])) for name in h2.e2.SUBSPACE_NAMES + ("S4_residual",)}
        reverse_diffs = {name: abs(float(mine["reverse_shares"][name]) - float(theirs["reverse_shares"][name])) for name in h2.e2.SUBSPACE_NAMES + ("S4_residual",)}
        standalone_diffs = {name: abs(float(mine["standalone_shares"][name]) - float(theirs["standalone_shares"][name])) for name in h2.e2.SUBSPACE_NAMES}
        family_diffs = {name: abs(float(mine["s3_family_shares"][name]) - float(theirs["s3_family_shares"][name])) for name in mine["s3_family_shares"]}
        e2_share_rows.append({
            "world": w, "offset_norm_abs_diff": offset_diff,
            "max_share_abs_diff": max(list(share_diffs.values()) + list(reverse_diffs.values()) + list(standalone_diffs.values()) + list(family_diffs.values())),
        })
    e2_share_max = max(max(r["offset_norm_abs_diff"], r["max_share_abs_diff"]) for r in e2_share_rows)

    def _disp_anchor(mine_arm: str, theirs_df: pd.DataFrame, theirs_arm: str) -> dict[str, Any]:
        mine = disp_rows[disp_rows["arm"] == mine_arm][["world", "repetition", "disp_v2"]]
        theirs = theirs_df[theirs_df["arm"] == theirs_arm][["world", "repetition", "disp_v2"]]
        joined = mine.merge(theirs, on=["world", "repetition"], suffixes=("_mine", "_theirs"), how="inner")
        if len(joined) != len(worlds) * REPETITIONS:
            raise RuntimeError(f"displacement anchor join for {mine_arm} vs {theirs_arm}: {len(joined)} rows != {len(worlds) * REPETITIONS}")
        joined["abs_diff"] = (joined["disp_v2_mine"] - joined["disp_v2_theirs"]).abs()
        return {"n_checks": int(len(joined)), "max_abs_diff": float(joined["abs_diff"].max())}

    harmless_disp_anchor = _disp_anchor(HARMLESS_ARM, h4_disp, HARMLESS_ARM)

    registered_literal_max = max(e2_share_max, harmless_disp_anchor["max_abs_diff"])
    registered_literal = {
        "deployed_shares_vs_m4e2_decision_json": {"per_world": e2_share_rows, "max_abs_diff": e2_share_max},
        "basis_shrinkage_1.00_displacement_vs_h4_disp_rows": harmless_disp_anchor,
        "max_abs_diff": registered_literal_max,
        "pass": bool(registered_literal_max <= G1_ANCHOR_TOLERANCE),
    }

    def _share_anchor_vs_csv(mine_arm: str, world: str, theirs_df: pd.DataFrame, theirs_arm: str) -> dict[str, Any]:
        mine = arm_summaries[(world, mine_arm)]
        theirs_row = theirs_df[(theirs_df["world"] == world) & (theirs_df["arm"] == theirs_arm)]
        if len(theirs_row) != 1:
            raise RuntimeError(f"share anchor missing for {mine_arm}/{theirs_arm} on {world}")
        theirs_row = theirs_row.iloc[0]
        offset_diff = abs(mine["offset_norm"] - float(theirs_row["offset_norm"]))
        flat_mine = {
            **{f"registered_{k}": v for k, v in mine["registered_shares"].items()},
            **{f"reverse_{k}": v for k, v in mine["reverse_shares"].items()},
            **{f"standalone_{k}": v for k, v in mine["standalone_shares"].items()},
            **{f"s3family_{k}": v for k, v in mine["s3_family_shares"].items()},
        }
        share_diffs = {f: abs(float(flat_mine[f]) - float(theirs_row[f])) for f in h3.SHARE_FIELDS}
        return {"world": world, "offset_norm_abs_diff": offset_diff, "max_share_abs_diff": max(share_diffs.values())}

    harmless_share_superset_rows = [_share_anchor_vs_csv(HARMLESS_ARM, w, h4_shares, HARMLESS_ARM) for w in worlds]
    deployed_disp_vs_h4 = _disp_anchor(DEPLOYED_ARM, h4_disp, DEPLOYED_ARM)
    deployed_disp_vs_h3 = _disp_anchor(DEPLOYED_ARM, h3_disp, DEPLOYED_ARM)

    superset_max = max(
        [r["offset_norm_abs_diff"] for r in harmless_share_superset_rows] + [r["max_share_abs_diff"] for r in harmless_share_superset_rows]
        + [deployed_disp_vs_h4["max_abs_diff"], deployed_disp_vs_h3["max_abs_diff"]],
    )
    disclosed_superset = {
        "statement": (
            "NOT required by the registered G1 clause -- strictly additional checks that can only strengthen G1, "
            "never loosen it: (i) full share decomposition for basis_shrinkage_1.00 against H4's own persisted "
            "offset_shares_by_arm.csv; (ii) deployed's own displacement against H4's AND H3's persisted disp_rows.csv."
        ),
        "basis_shrinkage_1.00_shares_vs_h4_offset_shares": {"per_world": harmless_share_superset_rows},
        "deployed_displacement_vs_h4_disp_rows": deployed_disp_vs_h4,
        "deployed_displacement_vs_h3_disp_rows": deployed_disp_vs_h3,
        "max_abs_diff": float(superset_max),
        "pass": bool(superset_max <= G1_ANCHOR_TOLERANCE),
    }

    # ==== G1, additional: per-repetition delta-construction consistency
    # ==== (new to this leg -- see docstring; not a comparison to a PRIOR
    # ==== persisted value, since no predecessor leg computed this, but an
    # ==== internal-consistency tie to the ALREADY-anchored disp_v2 values
    # ==== computed above in the SAME assemble pass) ----------------------
    per_rep_checks = []
    for w in worlds:
        for a in ARMS:
            for row in per_rep_by_world_arm[(w, a)]:
                per_rep_checks.append({
                    "world": w, "arm": a, "repetition": row["repetition"],
                    "native_norm_vs_disp_v2_anchor_absdiff": row["native_norm_vs_disp_v2_anchor_absdiff"],
                    "gauge_rotation_extraction_gate": row["gauge_rotation_extraction_gate"],
                    "delta_rep_norm_preserved_gate": row["delta_rep_norm_preserved_gate"],
                })
    per_rep_checks_df = pd.DataFrame(per_rep_checks)
    per_rep_disp_max = float(per_rep_checks_df["native_norm_vs_disp_v2_anchor_absdiff"].max())
    per_rep_rotation_max = float(per_rep_checks_df["gauge_rotation_extraction_gate"].max())
    per_rep_normpreserve_max = float(per_rep_checks_df["delta_rep_norm_preserved_gate"].max())
    per_rep_delta_construction = {
        "statement": (
            "NEW to this leg (no predecessor computed per-repetition deltas): internal-consistency checks tying "
            "the new per-rep delta construction to already-anchored disp_v2 values computed in this SAME assemble "
            "pass (native_norm_vs_disp_v2_anchor, tolerance = e2.DISPLACEMENT_ANCHOR_TOLERANCE = 1e-9, since these "
            "are two independently-ordered computations of a symmetric Procrustes distance) and to leg14._align "
            "itself (rotation_extraction_gate, norm_preserved_gate, tolerance = 1e-12, since these are the SAME "
            "SVD evaluated twice / a pure floating-point identity)."
        ),
        "n_checks": int(len(per_rep_checks_df)),
        "native_norm_vs_disp_v2_anchor_max_abs_diff": per_rep_disp_max,
        "native_norm_vs_disp_v2_anchor_tolerance": DISPLACEMENT_ANCHOR_TOLERANCE,
        "native_norm_vs_disp_v2_anchor_pass": bool(per_rep_disp_max <= DISPLACEMENT_ANCHOR_TOLERANCE),
        "rotation_extraction_gate_max": per_rep_rotation_max,
        "norm_preserved_gate_max": per_rep_normpreserve_max,
        "rotation_and_norm_tolerance": G1_ANCHOR_TOLERANCE,
        "rotation_and_norm_pass": bool(max(per_rep_rotation_max, per_rep_normpreserve_max) <= G1_ANCHOR_TOLERANCE),
    }
    per_rep_delta_construction["pass"] = bool(
        per_rep_delta_construction["native_norm_vs_disp_v2_anchor_pass"] and per_rep_delta_construction["rotation_and_norm_pass"],
    )

    g1_anchor = {
        "tolerance": G1_ANCHOR_TOLERANCE,
        "statement": (
            "registered: deployed's shares reproduce M4-E2's own persisted decision.json['offset_table'] to "
            "<=1e-12 (per world); basis_shrinkage_1.00's displacement reproduces M4-H4's own persisted "
            "disp_rows.csv to <=1e-12 (24 row-level checks). Disclosed superset additionally checks full shares "
            "for basis_shrinkage_1.00 and deployed's displacement against H4's/H3's own persisted CSVs, "
            "strengthening but never substituting for the registered-literal chain. A third, NEW check (not a "
            "predecessor comparison, since no prior leg computed this) ties this leg's own new per-repetition "
            "delta construction to already-anchored disp_v2 values and to leg14._align itself."
        ),
        "registered_literal": registered_literal,
        "disclosed_superset": disclosed_superset,
        "per_repetition_delta_construction": per_rep_delta_construction,
        "pass": bool(registered_literal["pass"] and disclosed_superset["pass"] and per_rep_delta_construction["pass"]),
    }

    # ==== G3 (world-build faithfulness, scope-reduced, not gating any lean) =====
    g3_gate = {
        "statement": (
            "budget=1.0 freshly-regenerated panels reproduce context['flat']-sourced refits exactly, this leg's 2 "
            "arms, one spot-check (rep,view,author) per world -- world-build faithfulness only (h5._g3_spot_check_h5, "
            "reused unchanged, filtered to this leg's own 2 arms); this leg does not adjudicate on truth-recovery "
            "(docstring, scope-reduction note, citing H5's own identical precedent), so this gate feeds no lean."
        ),
        "max_abs_diff": float(g3_rows["abs_diff"].max()),
        "n_checks": int(len(g3_rows)),
        "tolerance": G3_TOLERANCE,
        "pass": bool(g3_rows["abs_diff"].max() <= G3_TOLERANCE),
    }

    # ==== pooled components, null construction, agreement statistics ============
    components_by_arm_world: dict[str, dict[str, list[np.ndarray]]] = {
        a: {w: [row["S4_component"] for row in per_rep_by_world_arm[(w, a)]] for w in worlds} for a in ARMS
    }
    pooled_by_arm: dict[str, list[np.ndarray]] = {
        a: [components_by_arm_world[a][worlds[k // REPETITIONS]][k % REPETITIONS] for k in range(N_POOLED)] for a in ARMS
    }

    perm_rng = np.random.default_rng([int(config["seed"]), REP_SHUFFLE_NULL_SEED_TAG])
    permutations = _generate_null_permutations(N_POOLED, NULL_DRAWS, perm_rng)
    null_by_arm = {a: _repetition_shuffled_null_for_arm(pooled_by_arm[a], permutations, GROUP_SIZE, N_GROUPS) for a in ARMS}

    random_rng = np.random.default_rng([int(config["seed"]), RANDOM_MATRIX_NULL_SEED_TAG])
    random_null_by_arm = {a: _random_matrix_null((48, 13), NULL_DRAWS, random_rng) for a in ARMS}

    within_world_by_arm = {a: _within_world_agreement(components_by_arm_world[a]) for a in ARMS}
    across_world_by_arm = {a: _across_world_agreement(components_by_arm_world[a], worlds) for a in ARMS}

    # ==== G0 POWER (null spread + MDE stated BEFORE the real vs. null
    # ==== comparison is adjudicated below -- uses only null-side numbers) ==
    g0_power = {}
    for a in ARMS:
        null = null_by_arm[a]
        mde_within = _achievable_half_width(null["pair_std"], 28)
        mde_across = _achievable_half_width(null["pair_std"], 192)
        g0_power[a] = {
            "grain_statement": (
                "PAIR grain (the agreement statistic is inherently a per-PAIR quantity -- this line's own "
                "established principle of adopting the metric's natural finest unit, cf. H2's own REP-grain "
                "adoption for disp_v2). WITHIN-WORLD n=28 (C(8,2), one world); ACROSS-WORLD n=192 pooled "
                "(3 world-pairs x 64), per-world-pair n=64 reported as a disclosed companion."
            ),
            "null_spread_before_adjudicating": {
                "n_draws": null["n_draws"], "median": null["median"], "q05": null["q05"], "q95": null["q95"],
                "min": null["min"], "max": null["max"], "std_of_draw_means": null["std"],
                "pooled_pair_mean": null["pair_mean"], "pooled_pair_std": null["pair_std"],
                "n_pairs_pooled_across_all_draws": null["n_pairs_total"],
            },
            "mde_statement_before_adjudicating": (
                f"using the null's own pooled pair-level std ({null['pair_std']:.4f}, a non-circular, "
                f"pre-adjudication variance proxy) as sigma: at WITHIN-WORLD grain (n=28), the achievable "
                f"t-based CI half-width is {mde_within:.4f}; at ACROSS-WORLD pooled grain (n=192), "
                f"{mde_across:.4f}. Context: the null's own q95 ({null['q95']:.4f}) sits "
                f"{1.0 - null['q95']:.4f} below the trivial ceiling of 1.0, and "
                f"{LEAN_C_MATERIALITY_BAR - null['q95']:.4f} away from lean (c)'s own registered 0.5 "
                f"materiality bar -- both comfortably larger than the within-world MDE, so this design is not "
                f"chasing an effect near its own resolution floor."
            ),
            "mde_within_world_half_width_n28": mde_within,
            "mde_across_world_half_width_n192": mde_across,
            "random_matrix_null_disclosed_companion": random_null_by_arm[a],
        }

    # ==== G2 NULL LIVENESS =========================================================
    g2_null_liveness = {}
    for a in ARMS:
        null = null_by_arm[a]
        non_degenerate = bool(null["std"] > 1e-6 and (null["max"] - null["min"]) > 1e-4)
        below_ceiling = bool(null["median"] < 0.95)
        g2_null_liveness[a] = {
            "statement": (
                "the repetition-shuffled null must actually destroy the structure it is meant to destroy: reported "
                "here is the null's own spread (200 draws) and confirmation it is a genuine, non-degenerate, "
                "sub-maximal distribution -- 'a null that does not move is not a null'."
            ),
            "n_draws": null["n_draws"], "median": null["median"], "q05": null["q05"], "q95": null["q95"],
            "min": null["min"], "max": null["max"], "std": null["std"], "range": null["max"] - null["min"],
            "non_degenerate_spread": non_degenerate,
            "sits_below_trivial_ceiling_1.0": below_ceiling,
            "live": bool(non_degenerate and below_ceiling),
        }
    g2_gate = {"by_arm": g2_null_liveness, "all_live": bool(all(v["live"] for v in g2_null_liveness.values()))}

    # ==== G4 MATERIALITY FORM ====================================================
    g4_materiality_form = {
        "G0": "MDE stated from the null's own pair-level std (pre-adjudication, non-circular); no arbitrary externally-borrowed percentage bar invented -- context given against the null's own q95, the 1.0 ceiling, and lean (c)'s own registered 0.5 bar",
        "G1": "degenerate exact-equality (<=1e-12 world-level; <=1e-9 for the two independently-ordered symmetric-distance checks) against independently-persisted comparators (M4-E2's decision.json, M4-H4's disp_rows.csv/offset_shares_by_arm.csv, M4-H3's disp_rows.csv) plus a new internal-consistency check for this leg's own new machinery",
        "G2": "the null's own spread (std, range) reported and confirmed non-degenerate and sub-ceiling -- not a nil-significance test",
        "G3": "degenerate exact-equality (<=1e-12), faithfulness only, not lean-gating (scope-reduction disclosed, citing H5's own precedent)",
        "lean_a": "per-world CI-vs-null-q95 equivalence/margin test (ci_lo > null_q95), aggregated to a >=2-of-3-worlds count against a fixed registered bar -- not a nil-significance test",
        "lean_b": "pooled-across-world CI-vs-null-q95 equivalence/margin test (ci_hi <= null_q95), the SAME logic as lean (a) applied on the other side, per the registration's own control framing",
        "lean_c": "per-world ABSOLUTE threshold classification (point estimate >= 0.5), applied only to worlds lean (a) already qualified",
    }

    # ==== leans + pivot ===========================================================
    null_q95_harmless = null_by_arm[HARMLESS_ARM]["q95"]
    lean_a_by_world = {}
    for w in worlds:
        stats_w = within_world_by_arm[HARMLESS_ARM][w]
        held = bool(np.isfinite(stats_w["ci_lo"]) and stats_w["ci_lo"] > null_q95_harmless)
        lean_a_by_world[w] = {
            "n_pairs": stats_w["n_pairs"], "mean": stats_w["mean"], "ci_lo": stats_w["ci_lo"], "ci_hi": stats_w["ci_hi"],
            "half_width": stats_w["half_width"], "null_q95": null_q95_harmless, "held": held,
        }
    n_worlds_held = int(sum(v["held"] for v in lean_a_by_world.values()))
    lean_a_held = bool(n_worlds_held >= PIVOT_MIN_WORLDS_HELD)
    pivot_fires = not lean_a_held
    lean_a = {
        "statement": "per world: CI lower bound of within-world mean agreement exceeds the null's q95; HELD overall iff >=2 of 3 worlds qualify",
        "evaluated_at_arm": HARMLESS_ARM, "by_world": lean_a_by_world,
        "n_worlds_held": n_worlds_held, "min_worlds_required": PIVOT_MIN_WORLDS_HELD, "held": lean_a_held,
    }
    pivot = {
        "registered": "within-world agreement does not exceed the null in >=2 of 3 worlds -> S4 IS REPETITION-SPECIFIC AND NOT ATTACKABLE BY ANY BASIS CONSTRUCTION",
        "fires": bool(pivot_fires),
    }

    pooled_across = across_world_by_arm[HARMLESS_ARM]["pooled"]
    lean_b_ci_held = bool(np.isfinite(pooled_across["ci_hi"]) and pooled_across["ci_hi"] <= null_q95_harmless)
    lean_b_point_held = bool(pooled_across["mean"] <= null_q95_harmless)
    lean_b = {
        "statement": "pooled across-world CI upper bound sits at/below the null's q95 (equivalence-form ADOPTED reading); raw point-estimate reading disclosed as a cross-check",
        "evaluated_at_arm": HARMLESS_ARM,
        "pooled": pooled_across, "null_q95": null_q95_harmless,
        "per_world_pair": across_world_by_arm[HARMLESS_ARM]["per_world_pair"],
        "held_ci_form_ADOPTED": lean_b_ci_held, "held_point_estimate_disclosed": lean_b_point_held,
        "readings_agree": bool(lean_b_ci_held == lean_b_point_held),
        "held": lean_b_ci_held,
    }

    qualifying_worlds = [w for w, v in lean_a_by_world.items() if v["held"]]
    lean_c_by_world = {w: {"mean": lean_a_by_world[w]["mean"], "clears_0.5": bool(lean_a_by_world[w]["mean"] >= LEAN_C_MATERIALITY_BAR)} for w in qualifying_worlds}
    lean_c_held = bool(len(qualifying_worlds) > 0 and all(v["clears_0.5"] for v in lean_c_by_world.values()))
    lean_c = {
        "statement": "for every world where lean (a) held, point-estimate mean agreement >= 0.5 (ADOPTED: ALL qualifying worlds must clear, disclosed reading since the registration states no count rule here)",
        "evaluated_at_arm": HARMLESS_ARM, "qualifying_worlds": qualifying_worlds, "by_world": lean_c_by_world,
        "bar": LEAN_C_MATERIALITY_BAR, "applicable": bool(len(qualifying_worlds) > 0), "held": lean_c_held,
    }

    # ==== deployed reference companion (disclosed, non-adjudicating) ============
    null_q95_deployed = null_by_arm[DEPLOYED_ARM]["q95"]
    deployed_lean_a_by_world = {}
    for w in worlds:
        stats_w = within_world_by_arm[DEPLOYED_ARM][w]
        held = bool(np.isfinite(stats_w["ci_lo"]) and stats_w["ci_lo"] > null_q95_deployed)
        deployed_lean_a_by_world[w] = {
            "n_pairs": stats_w["n_pairs"], "mean": stats_w["mean"], "ci_lo": stats_w["ci_lo"], "ci_hi": stats_w["ci_hi"],
            "null_q95": null_q95_deployed, "held_if_this_were_adjudicated": held,
        }
    deployed_companion = {
        "statement": "DISCLOSED REFERENCE ONLY -- the registration evaluates leans at the harmless winner; deployed is reported for context (does reproducibility pre-exist, or does the repair change it?), never adjudicated.",
        "within_world_by_world": deployed_lean_a_by_world,
        "n_worlds_would_hold": int(sum(v["held_if_this_were_adjudicated"] for v in deployed_lean_a_by_world.values())),
        "across_world_pooled": across_world_by_arm[DEPLOYED_ARM]["pooled"],
        "null_q95": null_q95_deployed,
    }

    # ==== verdict ===================================================================
    if pivot_fires:
        verdict = "PIVOT_S4_REPETITION_SPECIFIC_NOT_ATTACKABLE_BY_ANY_BASIS_CONSTRUCTION"
    else:
        b_tag = "NOT_ACROSS_WORLDS" if lean_b_held else "CONTROL_MISS_SHARED_STRUCTURE_ACROSS_WORLDS"
        c_tag = "MATERIAL_GE_0.5" if lean_c_held else "SUBMATERIAL_LT_0.5"
        verdict = f"REPRODUCIBLE_WITHIN_WORLD__{b_tag}__{c_tag}"

    decision = {
        "estimand_id": "SUICA_M4_H6_RESIDUAL_REPRODUCIBILITY",
        "tier": "EXPLORATORY (open-exploration phase)",
        "registered_in": "docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md M4-H6 registration (2026-08-03, BEFORE run), preceded by the M4-H5 planner adjudication note; ledger row M4-H6",
        "worlds": worlds, "arms": list(ARMS),
        "harmless_winner_arm": HARMLESS_ARM, "deployed_arm_disclosed_reference_only": DEPLOYED_ARM,
        "part0_inherited": "no new Part 0 audit, no new basis-construction formula; both arms are literal calls into h5's own router into h4's own already-anchored dispatch functions",
        "scope_reductions_disclosed": [
            "registered order (S1->S2->S3->S4) only -- no reverse-order companion computed (unlike H5, this leg's registration never asks for ordering sensitivity)",
            "no truth-recovery machinery -- citing H5's own identical, already-adjudicated scope reduction; G3 is a lightweight world-build faithfulness spot-check only",
        ],
        "gates": {
            "G0_power": g0_power, "G1_anchor": g1_anchor, "G2_null_liveness": g2_gate,
            "G3_world_build_faithfulness_not_lean_gating": g3_gate, "G4_materiality_form": g4_materiality_form,
        },
        "null_construction": {
            "type": "repetition_shuffled",
            "statement": "pool 24 real S4_residual components per arm (3 worlds x 8 reps); 200 random permutations of {0..23} (SHARED across both arms), chunked into 3 groups of 8; within-pseudo-group mean |Procrustes cosine| pooled over all 84 pairs = one null draw. Used as the comparator for every agreement number (within-world and across-world alike). Random-matrix null (E2's own construction) reported as a disclosed, non-deciding companion only.",
            "n_draws": NULL_DRAWS, "n_pooled": N_POOLED, "group_size": GROUP_SIZE, "n_groups": N_GROUPS,
        },
        "lean_a_reproducible_within_world": lean_a,
        "lean_b_not_across_worlds": lean_b,
        "lean_c_material_enough_to_capture": lean_c,
        "pivot": pivot,
        "verdict": verdict,
        "deployed_reference_companion_disclosed_not_adjudicating": deployed_companion,
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only (the 3 HIGH_GAP_WORLDS, reused verbatim from M4-E2/Leg14/H2/H3/H4/H5); "
            "no natural-text, personality, or clinical claim; no seal, no independent verification (operator "
            "directive 2026-08-01)."
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
    g3_rows.to_csv(output / "g3check_rows.csv", index=False)
    per_rep_checks_df.to_csv(output / "per_rep_delta_construction_checks.csv", index=False)

    pd.DataFrame([
        {"world": w, "arm": a, "offset_norm": arm_summaries[(w, a)]["offset_norm"], "width": arm_summaries[(w, a)]["width"],
         **{f"registered_{k}": v for k, v in arm_summaries[(w, a)]["registered_shares"].items()},
         **{f"reverse_{k}": v for k, v in arm_summaries[(w, a)]["reverse_shares"].items()},
         **{f"standalone_{k}": v for k, v in arm_summaries[(w, a)]["standalone_shares"].items()},
         **{f"s3family_{k}": v for k, v in arm_summaries[(w, a)]["s3_family_shares"].items()}}
        for w in worlds for a in ARMS
    ]).to_csv(output / "offset_shares_by_arm.csv", index=False)

    per_rep_share_rows = [
        {"world": w, "arm": a, "repetition": row["repetition"], "S4_share_registered_order": row["S4_share"], "delta_rep_norm": row["delta_rep_norm"]}
        for w in worlds for a in ARMS for row in per_rep_by_world_arm[(w, a)]
    ]
    pd.DataFrame(per_rep_share_rows).to_csv(output / "per_rep_s4_share_rows.csv", index=False)

    within_pair_rows = []
    for a in ARMS:
        for w in worlds:
            vectors = components_by_arm_world[a][w]
            reps = [row["repetition"] for row in per_rep_by_world_arm[(w, a)]]
            for i in range(len(vectors)):
                for j in range(i + 1, len(vectors)):
                    within_pair_rows.append({
                        "arm": a, "world": w, "repetition_i": reps[i], "repetition_j": reps[j],
                        "cosine": float(h2.e2._procrustes_cosine(vectors[i], vectors[j])),
                    })
    pd.DataFrame(within_pair_rows).to_csv(output / "within_world_pair_rows.csv", index=False)

    across_pair_rows = []
    for a in ARMS:
        for row in across_world_by_arm[a]["pair_rows"]:
            across_pair_rows.append({"arm": a, **row})
    pd.DataFrame(across_pair_rows).to_csv(output / "across_world_pair_rows.csv", index=False)

    null_draw_rows = []
    for a in ARMS:
        for i, value in enumerate(null_by_arm[a]["draw_values"].tolist()):
            null_draw_rows.append({"arm": a, "null_type": "repetition_shuffled", "draw_index": i, "value": value})
    pd.DataFrame(null_draw_rows).to_csv(output / "null_draws.csv", index=False)

    within_summary_rows = [
        {"arm": a, "world": w, **{k: v for k, v in within_world_by_arm[a][w].items()}, "null_q95": null_by_arm[a]["q95"]}
        for a in ARMS for w in worlds
    ]
    pd.DataFrame(within_summary_rows).to_csv(output / "within_world_summary.csv", index=False)

    across_summary_rows = []
    for a in ARMS:
        for row in across_world_by_arm[a]["per_world_pair"]:
            across_summary_rows.append({"arm": a, "grouping": row["world_pair"], **{k: v for k, v in row.items() if k != "world_pair"}, "null_q95": null_by_arm[a]["q95"]})
        pooled_row = across_world_by_arm[a]["pooled"]
        across_summary_rows.append({"arm": a, "grouping": "POOLED_ALL_CROSS_WORLD_PAIRS", **pooled_row, "null_q95": null_by_arm[a]["q95"]})
    pd.DataFrame(across_summary_rows).to_csv(output / "across_world_summary.csv", index=False)

    print(json.dumps({
        "verdict": verdict, "pivot_fires": pivot_fires,
        "lean_a_held": lean_a_held, "n_worlds_held": n_worlds_held,
        "lean_b_held_ci": lean_b_ci_held, "lean_b_held_point": lean_b_point_held,
        "lean_c_held": lean_c_held, "lean_c_applicable": lean_c["applicable"],
        "null_q95_harmless": null_q95_harmless,
        "g1_anchor_pass": g1_anchor["pass"], "g2_all_live": g2_gate["all_live"], "g3_pass": g3_gate["pass"],
    }, indent=2))


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "m4_chart_ecology.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "m4_h6_residual_reproducibility")
    parser.add_argument("--world", type=str, default=None)
    parser.add_argument("--arm", type=str, default=None)
    parser.add_argument("--stage", type=str, default=None, choices=["g3"])
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--assemble", action="store_true")
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    assert int(config["repetitions"]) == REPETITIONS, f"this leg hardcodes REPETITIONS={REPETITIONS}, config says {config['repetitions']}"
    spec = M4ChartEcologySpec(**config["base_spec"])

    if args.assemble:
        _assemble(args.output, config)
        return

    if args.world is None:
        raise SystemExit("--world is required unless --assemble")
    if args.world not in WORLDS:
        raise SystemExit(f"not a registered HIGH_GAP_WORLDS world: {args.world}")

    if args.smoke:
        _run_smoke_h6(args.world, config, spec, args.output)
        return
    if args.stage == "g3":
        _run_g3_h6(args.world, config, spec, args.output)
        return
    if args.arm is None:
        raise SystemExit("--arm is required unless --stage g3 or --smoke or --assemble")
    if args.arm not in ARMS:
        raise SystemExit(f"not a registered M4-H6 arm: {args.arm}")
    _run_arm_h6(args.world, args.arm, config, spec, args.output)


if __name__ == "__main__":
    main()
