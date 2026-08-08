#!/usr/bin/env python3
"""M4-H2: is the displacement in the basis's own normalization?

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, "M4-H2
registration" (2026-08-03, BEFORE run); ledger row M4-H2). Machinery is
IMPORTED and REUSED wherever an existing seam exists: Leg 4's context build +
canonical forced-route derivative + analytic D_true, Leg 3's world seed +
relative error, Leg 8's expected-geometries lookup, Leg 9's row-norm swap,
Leg 10's freeze-ingredients rebuild + `_bases_from_whitening` (used UNCHANGED
for every arm's final basis-assembly step), Leg 11's stacked-frame quotient
machinery, Leg 14's GPA Frechet mean + quotient distance (the SAME functions
Leg 14/M4-E2/M4-G1..G7 used), M4-E2's S1/S2 common-core machinery
(`_response_direction_machinery`, `_arm_b_gate`, `_s1_patterns`,
`_s2_patterns`, `_common_core`, `_pattern_basis_to_matrix_basis`,
`_sequential_shares`, `_project`, `_orthonormal_matrix_basis` -- all called
UNCHANGED), M4-G1's paired-CI helpers, M4-G3's `VALID_TRUTH_WORLDS`, M4-G4's
generic author/world-grain CI + classification machinery. No estimator
internals are copied and the deployed basis-construction path
(`suica_core/m4_condition_manifold_estimator.py`,
`suica_core/m4_chart_ecology_estimator.py`) is READ-ONLY throughout -- every
variant lives in this script as a disclosed near-duplicate of the exact lines
it varies.

===========================================================================
PART 0 -- INVENTORY OF `context["v2_basis"]`'s CONSTRUCTION (gated, before
any compute). This inventory IS the leg's hypothesis space; anything found
later may be reported but not scored.
===========================================================================

`context["v2_basis"]` is built by `leg4._build_context` calling
`build_m4_discovered_basis` (`suica_core/m4_chart_ecology_estimator.py:1078-
1103`), which calls `freeze_m4_condition_transform`
(`suica_core/m4_condition_manifold_estimator.py:545-608`) once to fit a
`FrozenConditionTransform` on `observed.condition.reference_calibration`, then
applies `transform.transform_prototypes` (`m4_condition_manifold_estimator.py
:76-96`) to each of the three MECHANISM role panels. Every normalization,
scaling, centering and reference choice on that path, in call order, with
file:line, classification and stated reason:

 1. Per-source robust standardization, `m4_condition_manifold_estimator.py
    :165` (`standardized, center, scale = _robust_scale(values)`, inside
    `_fit_source`, lines 158-210) -- median-center + IQR-scale each source's
    raw pre-context features BEFORE the chart representation (PCA / Isomap /
    landmark-atlas) is fit; re-applied with the FROZEN center/scale at
    `_transform_representation`, lines 217-221, for every later panel
    (reference AND all three mechanism roles) via `_candidate_features`
    (line 270-287) -> `freeze_m4_condition_transform`'s own `raw` (line 564)
    and `build_m4_discovered_basis`'s per-role calls.
    CLASSIFICATION: CANDIDATE CARRIER. This is a genuine, textbook
    normalization step (median/IQR), applied upstream of everything else on
    this path, and "skip it" (identity: center=0, scale=1) is a clean,
    well-posed "unnormalized" reading. -> arm `basisvar_source_scale_off`.
 2. Chart representation family fit (PCA / Isomap / landmark-atlas), kernel
    bandwidth (`m4_condition_manifold_estimator.py:325-328`, applied at
    line 286: `np.exp(-0.5 * (distance / bandwidth) ** 2)`), landmark count
    and selection (`_fit_candidate`, lines 294-339).
    CLASSIFICATION: NOT a candidate carrier. These are representation-fitting
    HYPERPARAMETERS (which family, how many landmarks, how wide the kernel)
    shared with, and already fixed by, the CLOSED chart-selection line
    (M4-F) -- `chart.selected_family`/`selected_parameters` are part of the
    M4-E2/Leg14 anchor this leg is registered to reuse verbatim. Varying them
    would silently re-derive a DIFFERENT chart than the one already anchored,
    not normalize an already-fixed representation. Reported, not scored.
 3. Source-averaging, `m4_condition_manifold_estimator.py:564`
    (`raw = np.mean(_candidate_features(candidate, prototypes), axis=0)`) --
    mean across the `sources` axis.
    CLASSIFICATION: NOT a candidate carrier. This is a feature-FUSION choice
    (which sources contribute, and how), not a scale/center/normalization
    choice in the registration's sense; there is no natural "unnormalized /
    regularized / alternatively centered" reading of "which sources to
    combine". Reported, not scored.
 4. Centering, `m4_condition_manifold_estimator.py:565`
    (`center = np.mean(raw, axis=0)`) -- MEAN centering of the (points x
    features) reference representation, over the points axis.
    CLASSIFICATION: CANDIDATE CARRIER. Directly the registration's own
    "alternatively centered" case: this codebase's OWN convention elsewhere
    (`_robust_scale`, line 108-130, and every S1/S2 extraction) uses MEDIAN
    centering; mean-vs-median at this exact step is a clean, single-axis
    variant. -> arm `basisvar_center_median`.
 5. Covariance denominator, `m4_condition_manifold_estimator.py:567-569`
    (`covariance = centered.T @ centered / max(len(centered) - 1, 1)`) --
    Bessel's correction (N-1) vs population (N), N = 96 reference-calibration
    points (verified empirically below, Part 0 preflight).
    CLASSIFICATION: NOT a candidate carrier, by a priori bound stated BEFORE
    compute. This denominator choice is a PURE GLOBAL SCALAR MULTIPLIER on
    every retained eigenvalue (ratio 96/95 = 1.0105), hence, after
    1/sqrt(.), a UNIFORM ~0.52% multiplier on the whole whitening matrix --
    over 47x smaller than M4-G2's own smallest tested c-ladder step (0.25x/
    4x) and, by M4-G2's own measured log-log slope (0.8796, sub-linear) on
    an axis THIS is a micro-instance of, mechanically incapable of moving
    Leg 14's ~18-unit displacement gap by anywhere near the 25% actionable
    bar. Degenerate with an already-characterized, already-disqualified
    (as a raw-magnitude units effect) axis. Reported, not scored.
 6. Eigenvalue rank-retention threshold, `m4_condition_manifold_estimator.py
    :574-577` (`threshold = rank_tolerance * max(eigenvalues[0], 1e-12);
    retained = flatnonzero(eigenvalues > threshold); retained =
    retained[:maximum_rank]`) -- deployed `rank_tolerance=1e-6`,
    `maximum_rank=12` (from `configs/m4_chart_ecology.json`); verified
    empirically (Part 0 preflight) that `maximum_rank` is the BINDING
    constraint in all 3 worlds at rep 0 (12 of the top eigenvalues always
    clear the 1e-6-relative floor).
    CLASSIFICATION: CANDIDATE CARRIER. This is the "how much of the spectral
    mass survives" reference choice E2 itself frames S3 around ("normal
    -ization/scale modes"); a materially stricter threshold is the
    registration's "unnormalized"-adjacent reading (retain less, so less of
    the amplification survives). -> arm `basisvar_rank_tolerance_tight`
    (`rank_tolerance=1e-3`, 1000x stricter; preflight below shows this cuts
    retained rank from 12 to {7,5,7} across the three worlds' rep 0 -- a
    real, materially different width, not a cosmetic change). A width
    companion (`disp_v2 / sqrt(width)`) is reported alongside this arm's raw
    numbers, per this line's own established practice (M4-G1/M4-G2's D2), to
    separate a width confound from a genuine reduction.
 7. Numerical floor inside the whitening denominator,
    `m4_condition_manifold_estimator.py:582`
    (`np.sqrt(np.maximum(eigenvalues[retained], 1e-12))`).
    CLASSIFICATION: NOT a candidate carrier, by a priori argument VERIFIED in
    the Part 0 preflight (below) rather than merely asserted: this floor only
    binds when a retained eigenvalue is itself <=1e-12 in absolute terms, but
    `rank_tolerance=1e-6` (relative to the top eigenvalue, itself O(0.1)-
    O(0.5) in all three worlds) already excludes anything that small --
    empirically, the smallest RETAINED eigenvalue in every world's rep 0 is
    6.7e-7 to 3.0e-6, i.e. 6.7e5 to 3.0e6 times the floor. Never binds.
    Reported, not scored.
 8. Whitening scale, `m4_condition_manifold_estimator.py:580-583`
    (`whitening = eigenvectors[:, retained] / sqrt(max(eigenvalues[retained],
    1e-12))`) -- the UNREGULARIZED 1/sqrt(eig) amplification M4-E2 named as
    the largest identifiable carrier (n2 family, .74-.79 of standalone S3).
    CLASSIFICATION: CANDIDATE CARRIER, in BOTH of the registration's suggested
    variant forms, since this step is a scaling step with two natural,
    qualitatively different readings:
    (a) REGULARIZED: `basisvar_whitening_shrinkage`, 1/sqrt(eig + lambda),
        lambda = 0.10 * median(retained eigenvalues) -- M4-G1's own Reading-A
        convention and its OWN middle rung (`shrinkage_0.1`), reused for
        continuity rather than re-derived, but now applied to the basis that
        actually builds `context["v2_basis"]` rather than to M4-G1's
        downstream, structurally-disconnected copy.
    (b) UNNORMALIZED: `basisvar_whitening_unscaled`, drop the 1/sqrt(eig)
        term entirely (whitening = raw retained eigenvectors) -- M4-G1's own
        "identity" extreme control, again re-run one level up.
 9. Constant mass ("intercept") column, `m4_condition_manifold_estimator.py
    :96` (`return np.column_stack([np.ones(len(raw)), whitened])`, inside
    `transform_prototypes`; reproduced identically inside
    `leg10._bases_from_whitening`, line 356) -- a literal, UNSCALED column of
    ones prepended to every role's basis, magnitude exactly 1.0/entry
    regardless of the whitened block's own scale.
    CLASSIFICATION: CANDIDATE CARRIER. A genuine reference choice (the mass
    column's scale relative to the block it is concatenated with), already
    named by M4-E2's OWN S3-n1 family definition as one of n1's three
    contributing normalization steps ("the appended constant mass column").
    Deployed IS the "unnormalized" reading (fixed at 1.0, ignoring the
    whitened block's own scale); the natural variant is "matched": rescale
    it to the whitened block's own typical column norm. ->
    arm `basisvar_intercept_matched_scale`.
10. Reference panel choice (`observed.reference_calibration`, never
    `observed.reference_selection`, `m4_condition_manifold_estimator.py
    :556-563`).
    CLASSIFICATION: NOT a candidate carrier -- a distinct DATA-SOURCE choice
    (which panel the chart is fit on), not a normalization/scaling/centering
    step, and varying it would break the "reuse M4-E2/Leg14's own anchors"
    contract (the chart itself was already fit, and validated, on
    `reference_calibration`). Reported, not scored.

SIX steps classified CANDIDATE CARRIER -> six `basisvar_<k>` arms (mirrors
M4-G3's own six-Category-A-constant inventory discipline). Four steps
classified NOT a candidate carrier, each with a stated a priori reason (two
by scope boundary vs the closed chart-selection line, two by a priori/
preflight-verified materiality bound) -- reported, never scored.

--- Part 0 preflight (verified numerically, BEFORE any hypothesis-relevant
    compute; see `_PREFLIGHT_NOTES` below and the smoke stage) ------------
Chart families actually in force on the three registered worlds (rep 0):
`endogenous_creation_expansion`=linear_pca, `selection_creation_compensation`
=global_isomap, `source_rotated_feedback`=global_isomap -- both families
exercised by `basisvar_source_scale_off`'s near-duplicate fit. Reference
panel size: 96 points (2 sources x 32 authors averaged), NOT the 16-category
mechanism-role width -- resolves the N used in item 5's a priori bound.
`retained` = 12 in all three worlds' rep 0 (the `maximum_rank=12` cap binds,
not the 1e-6 relative threshold) -- resolves item 6's "which constraint
binds" and sizes the `rank_tolerance_tight` cut. Smallest retained eigenvalue
6.7e-7 to 3.0e-6 vs the 1e-12 floor -- resolves item 7.

--- Registered mechanistic prediction (Part 0, for lean (b)) --------------
ALL SIX candidate steps are, by construction, normalization/scaling/centering
choices on the SAME path E2 names S3 ("normalization/scale modes") -- Part 0
of THIS leg is exactly an enumeration of that subspace's own generating
mechanism. The registered, uniform mechanistic prediction for every arm is
therefore: **S3's registered-order share falls** at the winning arm. A finer,
NON-ADJUDICATING companion prediction is disclosed per arm (which within-S3
family, n1/n2/n3, the step most directly touches): `whitening_shrinkage`,
`whitening_unscaled`, `rank_tolerance_tight` -> n2 (column-scale modes);
`center_median`, `intercept_matched_scale` -> n1 (centering/mass modes,
matching E2's own n1 definition verbatim for the intercept case);
`source_scale_off` -> no specific family (it is upstream of, and touches,
every family at once; disclosed as the least mechanically specific of the
six, reported but not used to sharpen its own lean-(b) test beyond the
uniform S3 prediction every arm shares).

===========================================================================
DESIGN (registered)
===========================================================================
Arms: `deployed` (anchor) + six `basisvar_<k>` (above). Worlds: Leg 14's/
M4-E2's own `HIGH_GAP_WORLDS` (3), all reps (8). `deployed`'s basis is NOT
read off `context["v2_basis"]` directly for METRIC 1/2 purposes -- it is
INDEPENDENTLY RECOMPUTED via this leg's own `_ingredients_for_arm`/
`_whitening_for_step`/`_basis_for_arm` machinery falling through to every
step's deployed default, then gated to <=1e-12 against `context["v2_basis"]`
itself. This makes the G1 anchor a real test of the shared machinery every
`basisvar_<k>` arm also depends on, not a trivial pass-through.

Three mandatory metrics, computed per arm:
 1. Leg 14's displacement gap on its own persisted definition (`disp_v2 =
    quotient_distance(row_norm_swap(oracle_basis, arm_basis), arm_basis)`,
    Leg 14's OWN formula with the arm's own basis substituted for the
    deployed one) -- PRIMARY.
 2. M4-E2's S1-S4 shares -- S1/S2 bases are ARM-INVARIANT (built from raw
    response/feature panels via Leg 10's arm-B machinery, never from
    `context["v2_basis"]`) and computed ONCE per world, reused for every arm;
    S3 (and hence Delta, and hence every share) IS arm-dependent, since S3's
    n2 family and the offset consensus `a_center` are built from the arm's
    OWN discovered frame -- recomputed per arm via a disclosed, line-for-line
    near-duplicate of M4-E2's own inline S3 construction, gated at `deployed`
    to <=1e-12 against M4-E2's persisted shares.
 3. Truth-referenced recovery, M4-F5-style, both TRUTH_BUDGETS = (4.0, 8.0)
    -- the arm's own basis substituted into `leg4._forced_route_derivative`
    at the DEPLOYED `hazard_ridge` (this leg varies the basis only, never the
    estimator's regularization -- that territory is the closed M4-G line's).

--- Registered ambiguity resolution: metric-1 grain (disclosed, resolved
    BEFORE adjudicating any number) -----------------------------------
The outer registration's lean (a) reads "paired-by-world CI excluding zero"
literally (n=3). But G0 separately instructs "the grain justified... not
inherited" (the fifth standing rule), and M4-G7 -- the immediately preceding
leg, testing the SAME metric (`disp_v2`) against the SAME deployed baseline
on the SAME three worlds -- already resolved this exact tension: REP grain
(n=24, 3 worlds x 8 reps) as PRIMARY, because `disp_v2` is already a per-rep
quantity (no aggregation is needed to reach it), with WORLD grain (n=3) as a
disclosed companion for literal-text fidelity. This leg ADOPTS the identical
resolution, for the identical reason, on the identical metric -- not a fresh
tie-break but an inheritance of the line's own most recent precedent for
this exact ambiguity. Both grains are computed and reported; REP grain
adjudicates lean (a) and the pivot.

--- Metric 3 grain --------------------------------------------------------
AUTHOR grain (view-mean, n up to 3*8*16=384), per M4-G3's own hand-off
recommendation and every leg since (G4-G7). WORLD grain (n=3) reported as a
disclosed companion, per the same established convention.

--- Metric 2 grain ---------------------------------------------------------
WORLD-level point comparison (n=3, a census of the registered worlds, not a
sample) -- M4-E2's and M4-H1's own convention: a world's decomposition share
is a single deterministic GPA-consensus statistic, so there is no finer
sampling unit at which it is even defined.

Leans (registered, unchanged from the outer task):
(a) A CARRIER EXISTS: some `basisvar_<k>` reduces Leg 14's gap by >=25%
    relative to deployed, paired CI excluding zero (rep grain primary).
(b) MECHANISTICALLY CONSISTENT: at the winning arm (largest rep-grain point
    reduction among arms clearing lean (a)), S3's registered-order share
    falls relative to deployed.
(c) NOT COSMETIC: truth-referenced recovery does not worsen at the winning
    arm, either budget, equivalence form, margin = 0.02 (this line's own
    G4->G5->G6->G7 "no loss" convention, reused unchanged).

PIVOT-IF: no arm clears the 25% bar with a CI excluding zero -> the
displacement is NOT in the basis's normalization either; the remaining
candidate is the CONSENSUS/ALIGNMENT step, registered as the next question.

Gates: G0 POWER (grain justified above, MDE stated from Leg 14's persisted
~18-unit gap level before adjudicating); G1 ANCHOR (<=1e-12, both M4-E2 and
Leg 14 persisted values, on `deployed`); G2 BASIS LIVENESS (chordal quotient
distance of each arm's own stacked frame against deployed's, per rep,
materiality margin = 10% of deployed's own median `disp_v2` -- this line's
own `G2_CONDITION_MATERIALITY_RATIO` convention, reused); G3 TRUTH-PATH
INVARIANCE (dual-computation degenerate equality: `context["flat"]`-sourced
vs freshly re-flattened budget=1.0 panels, every arm, one spot-check
(rep,view,author) per world, mirroring M4-G7's own `_g3_spot_check`); G4
MATERIALITY FORM (stated per gate in the report).

Chunked execution (process rule -- "drive every compute stage yourself in
the FOREGROUND, in chunks"; no background jobs, no monitors): `--world W
--stage oracle` computes the arm-invariant oracle truth-recovery rows once
per world (cached); `--world W --stage g3` computes the one-spot-check,
all-arms G3 dual-computation check once per world; `--world W --arm A`
computes one arm's full pass for one world (basis/offset/shares/disp/truth),
reusing the oracle cache and a pickled per-world context cache so context
build (the expensive step) is paid ONCE per world, not once per (world,
arm); `--assemble` combines every partial into gates.json/decision.json.
`--smoke` runs a 1-rep, several-arm, 1-budget correctness+timing check
before the full sweep. Every per-(world,arm)/per-world stage is idempotent
(skips if its partial already exists), so a stage can be re-invoked freely
to resume after a timeout.
"""
from __future__ import annotations

import argparse
import json
import pickle
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA
from sklearn.manifold import Isomap

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_suica_m4_d_dleg_floor_leg4 as leg4  # noqa: E402  bit-exact reuse
import run_suica_m4_d_overspan_control_leg3 as leg3  # noqa: E402
import run_suica_m4_d_bias_anatomy_leg8 as leg8  # noqa: E402
import run_suica_m4_d_bias_variance_leg9 as leg9  # noqa: E402
import run_suica_m4_d_direction_anatomy_leg10 as leg10  # noqa: E402
import run_suica_m4_d_perturbation_leg11 as leg11  # noqa: E402
import run_suica_m4_d_displacement_leg14 as leg14  # noqa: E402
import run_suica_m4_e2_offset_anatomy as e2  # noqa: E402  S1/S2/shares machinery
import run_suica_m4_g1_whitening_intervention as g1  # noqa: E402  paired-CI helpers
import run_suica_m4_g3_scale_adaptive as g3  # noqa: E402  VALID_TRUTH_WORLDS
import run_suica_m4_g4_covariant_ridge as g4  # noqa: E402  author/world CI + classify

from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_condition_manifold_estimator import (  # noqa: E402
    _Candidate,
    _SourceRepresentation,
    _candidate_features,
    _farthest_landmarks,
    _knn_graph_distances,
    _panel_prototypes,
    _representation_distance,
    _robust_scale,
)

ROLES = leg11.ROLES
HIGH_GAP_WORLDS = leg11.HIGH_GAP_WORLDS
VALID_TRUTH_WORLDS = g3.VALID_TRUTH_WORLDS
assert set(HIGH_GAP_WORLDS) <= set(VALID_TRUTH_WORLDS), "M4-H2 needs no world exclusion for metric 3"
TRUTH_BUDGETS = g1.TRUTH_BUDGETS
assert TRUTH_BUDGETS == (4.0, 8.0)

# ---------------------------------------------------------------------------
# registered arms and parameters (Part 0)
# ---------------------------------------------------------------------------

BASISVAR_ARMS = (
    "basisvar_whitening_shrinkage",
    "basisvar_whitening_unscaled",
    "basisvar_rank_tolerance_tight",
    "basisvar_center_median",
    "basisvar_intercept_matched_scale",
    "basisvar_source_scale_off",
)
ARMS = ("deployed",) + BASISVAR_ARMS

SHRINKAGE_RATIO = 0.10          # lambda = ratio * median(retained eig); M4-G1 Reading-A
TIGHT_RANK_TOLERANCE = 1e-3     # vs deployed 1e-6 (1000x stricter)
DEPLOYED_RANK_TOLERANCE = 1e-6
DEPLOYED_MAXIMUM_RANK = 12

ARM_S3_FAMILY_PREDICTION = {  # disclosed companion only; lean (b) itself uses S3 whole
    "basisvar_whitening_shrinkage": "n2_column_scale",
    "basisvar_whitening_unscaled": "n2_column_scale",
    "basisvar_rank_tolerance_tight": "n2_column_scale",
    "basisvar_center_median": "n1_centering_mass",
    "basisvar_intercept_matched_scale": "n1_centering_mass",
    "basisvar_source_scale_off": None,
}

G1_ANCHOR_TOLERANCE = 1e-12
G3_TOLERANCE = 1e-12
LEAN_A_BAR = 0.25                 # >=25% reduction, this leg's own registered bar
LEAN_C_MARGIN = g4.LEAN_B_MARGIN  # 0.02, G4->G5->G6->G7's own "no loss" convention
G0_FRACTION_BAR_METRIC3 = g4.G0_FRACTION_BAR  # 0.01, half of LEAN_C_MARGIN
G2_MATERIALITY_RATIO = 0.10       # G1's own G2_CONDITION_MATERIALITY_RATIO convention

E2_DECISION_PATH = ROOT / "results" / "m4_e2_offset_anatomy" / "decision.json"
LEG14_DECISION_PATH = ROOT / "results" / "m4_d_discovery_displacement" / "decision.json"
LEG14_DISPLACEMENT_ROWS_PATH = ROOT / "results" / "m4_d_discovery_displacement" / "displacement_rows.csv"
LEG14_GAP_ROWS_PATH = ROOT / "results" / "m4_d_discovery_displacement" / "gap_rows.csv"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"required persisted anchor is missing: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


# ---------------------------------------------------------------------------
# Part 0 candidate steps 1/2: disclosed near-duplicates of _fit_source /
# _fit_candidate (m4_condition_manifold_estimator.py:158-210, 294-339), the
# ONLY seam not already exposed by leg10's own near-duplicate machinery.
# ---------------------------------------------------------------------------


def _fit_source_variant(
    values: np.ndarray, *, family: str, dimensions: int, neighbors: int, skip_scale: bool,
) -> _SourceRepresentation:
    if skip_scale:
        matrix = np.asarray(values, dtype=float)
        standardized = matrix
        center = np.zeros(matrix.shape[1])
        scale = np.ones(matrix.shape[1])
    else:
        standardized, center, scale = _robust_scale(values)
    if family == "linear_pca":
        estimator = PCA(n_components=dimensions, svd_solver="full").fit(standardized)
        representation = estimator.transform(standardized)
        graph_distances = None
    elif family == "global_isomap":
        _, components = _knn_graph_distances(standardized, neighbors)
        if components != 1:
            raise ValueError("global Isomap calibration graph is disconnected")
        estimator = Isomap(n_neighbors=neighbors, n_components=dimensions, eigen_solver="dense").fit(standardized)
        representation = estimator.transform(standardized)
        graph_distances = None
    elif family == "landmark_atlas":
        graph_distances, components = _knn_graph_distances(standardized, neighbors)
        if components != 1 or not np.isfinite(graph_distances).all():
            raise ValueError("landmark atlas calibration graph is disconnected")
        estimator = None
        representation = graph_distances
    else:
        raise ValueError(f"unknown chart family: {family}")
    return _SourceRepresentation(
        family=family, center=center, scale=scale,
        calibration_standardized=standardized,
        calibration_representation=np.asarray(representation, dtype=float),
        estimator=estimator, graph_distances=graph_distances, neighbors=neighbors,
    )


def _fit_candidate_variant(
    calibration: Any, *, family: str, dimensions: int, neighbors: int, landmarks: int, skip_scale: bool,
) -> _Candidate:
    prototypes = _panel_prototypes(calibration)
    models = tuple(
        _fit_source_variant(
            prototypes[source], family=family, dimensions=dimensions,
            neighbors=min(neighbors, len(prototypes[source]) - 2), skip_scale=skip_scale,
        )
        for source in range(len(prototypes))
    )
    first = models[0]
    if first.family == "landmark_atlas":
        metric = np.asarray(first.graph_distances, dtype=float)
    else:
        metric = squareform(pdist(first.calibration_representation))
    selected = _farthest_landmarks(metric, landmarks)
    bandwidths = []
    for model in models:
        distance = _representation_distance(model, model.calibration_representation, selected)
        positive = distance[distance > 1e-10]
        bandwidths.append(float(np.median(positive)) if len(positive) else 1.0)
    return _Candidate(
        family=family,
        parameters={"dimensions": int(dimensions), "neighbors": int(neighbors), "landmarks": int(len(selected))},
        models=models, landmarks=selected, bandwidths=np.asarray(bandwidths),
    )


# ---------------------------------------------------------------------------
# Part 0 candidate steps 4/6/8: ingredients + whitening builders, reusing
# leg10._bases_from_whitening UNCHANGED for the final assembly step.
# ---------------------------------------------------------------------------


def _ingredients_for_arm(context: dict[str, Any], arm: str) -> dict[str, Any]:
    """Reproduces freeze_m4_condition_transform's eigendecomposition
    (m4_condition_manifold_estimator.py:556-579) with exactly the named
    arm's registered step varied; every other step at its deployed default."""
    transform = context["v2_transform"]
    condition = context["observed"].condition
    parameters = transform.selected_parameters
    family = transform.selected_family

    if arm == "basisvar_source_scale_off":
        candidate = _fit_candidate_variant(
            condition.reference_calibration, family=family,
            dimensions=int(parameters["dimensions"]), neighbors=int(parameters["neighbors"]),
            landmarks=int(parameters["landmarks"]), skip_scale=True,
        )
    else:
        candidate = transform._candidate  # deployed candidate fit, reused unchanged

    prototypes = _panel_prototypes(condition.reference_calibration)
    raw = np.mean(_candidate_features(candidate, prototypes), axis=0)

    if arm == "basisvar_center_median":
        center = np.median(raw, axis=0)
    else:
        center = np.mean(raw, axis=0)

    centered = raw - center
    covariance = centered.T @ centered / max(len(centered) - 1, 1)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]

    rank_tolerance = TIGHT_RANK_TOLERANCE if arm == "basisvar_rank_tolerance_tight" else DEPLOYED_RANK_TOLERANCE
    threshold = rank_tolerance * max(float(eigenvalues[0]), 1e-12)
    retained = np.flatnonzero(eigenvalues > threshold)
    retained = retained[: max(int(DEPLOYED_MAXIMUM_RANK), 1)]
    if len(retained) == 0:
        retained = np.asarray([0])

    return {
        "candidate": candidate, "center": center,
        "eigenvalues": eigenvalues, "eigenvectors": eigenvectors, "retained": retained,
    }


def _whitening_for_step(ingredients: dict[str, Any], arm: str) -> tuple[np.ndarray, dict[str, Any]]:
    eigenvalues = ingredients["eigenvalues"]
    eigenvectors = ingredients["eigenvectors"]
    retained = ingredients["retained"]
    eig_retained = eigenvalues[retained]
    if arm == "basisvar_whitening_shrinkage":
        lam = SHRINKAGE_RATIO * float(np.median(eig_retained))
        whitening = eigenvectors[:, retained] / np.sqrt(np.maximum(eig_retained + lam, 1e-12))[None]
        return whitening, {"lambda": lam, "k_retained": int(len(retained))}
    if arm == "basisvar_whitening_unscaled":
        return eigenvectors[:, retained], {"k_retained": int(len(retained))}
    whitening = eigenvectors[:, retained] / np.sqrt(np.maximum(eig_retained, 1e-12))[None]
    return whitening, {"k_retained": int(len(retained))}


def _rescale_intercept(basis: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Registered variant for `basisvar_intercept_matched_scale`: rescale the
    constant mass column (m4_condition_manifold_estimator.py:96 /
    leg10.py:356) to the whitened block's own median column-L2-norm, pooled
    across all three roles, instead of the deployed literal 1.0/entry."""
    stacked_whitened = np.vstack([basis[role][:, 1:] for role in ROLES])
    col_norms = np.linalg.norm(stacked_whitened, axis=0)
    target_norm = float(np.median(col_norms)) if col_norms.size else 1.0
    out: dict[str, np.ndarray] = {}
    for role in ROLES:
        matrix = basis[role]
        whitened_block = matrix[:, 1:]
        rows = matrix.shape[0]
        new_col0 = np.full(rows, target_norm / np.sqrt(rows))
        out[role] = np.column_stack([new_col0, whitened_block])
    return out


def _basis_for_arm(context: dict[str, Any], arm: str) -> tuple[dict[str, np.ndarray], dict[str, Any], dict[str, Any]]:
    ingredients = _ingredients_for_arm(context, arm)
    whitening, meta = _whitening_for_step(ingredients, arm)
    basis = leg10._bases_from_whitening(context, ingredients, whitening)
    if arm == "basisvar_intercept_matched_scale":
        basis = _rescale_intercept(basis)
    return basis, ingredients, meta


# ---------------------------------------------------------------------------
# S3 construction, factored out of M4-E2's inline body (disclosed near-
# duplicate of scripts/run_suica_m4_e2_offset_anatomy.py:675-701) so it can
# be rebuilt per arm instead of once for the deployed cloud.
# ---------------------------------------------------------------------------


def _s3_bases_for_center(a_center: np.ndarray, width: int, categories: int) -> dict[str, np.ndarray]:
    constant_patterns = np.zeros((a_center.shape[0], len(ROLES)))
    for index in range(len(ROLES)):
        constant_patterns[index * categories:(index + 1) * categories, index] = 1.0 / np.sqrt(categories)
    n1_mats = [
        np.outer(constant_patterns[:, index], np.eye(width)[w])
        for index in range(len(ROLES)) for w in range(width)
    ]
    _, _, right_vectors_t = np.linalg.svd(a_center, full_matrices=False)
    n2_mats = [a_center @ np.outer(right_vectors_t[i], right_vectors_t[i]) for i in range(right_vectors_t.shape[0])]
    n3_mats = []
    for index in range(len(ROLES)):
        block = np.zeros_like(a_center)
        block[index * categories:(index + 1) * categories] = a_center[index * categories:(index + 1) * categories]
        n3_mats.append(block)
    return {
        "S3_norm_scale_modes": e2._orthonormal_matrix_basis(n1_mats + n2_mats + n3_mats),
        "n1_centering_mass": e2._orthonormal_matrix_basis(n1_mats),
        "n2_column_scale": e2._orthonormal_matrix_basis(n2_mats),
        "n3_role_size": e2._orthonormal_matrix_basis(n3_mats),
    }


def _arm_offset_and_shares(
    world: str, contexts: list[dict[str, Any]], arm: str, s1_patterns: np.ndarray, s2_patterns: np.ndarray,
) -> dict[str, Any]:
    v2_frames = []
    swap_frames = []
    disp_rows = []
    arm_bases = []
    for context in contexts:
        basis, _, meta = _basis_for_arm(context, arm)
        arm_bases.append(basis)
        swap_basis = leg9._row_norm_swap(context["truth"].oracle_basis, basis)
        v2_frame = leg11._stack_frame(basis)
        swap_frame = leg11._stack_frame(swap_basis)
        v2_frames.append(v2_frame)
        swap_frames.append(swap_frame)
        disp = leg14._quotient_distance(swap_frame, v2_frame)
        disp_rows.append({
            "world": world, "arm": arm, "repetition": context["repetition"],
            "disp_v2": disp, "width": int(basis["calibration"].shape[1]),
            "meta": json.dumps(meta),
        })

    gpa_v2 = leg14._frechet_mean_multistart(v2_frames)
    gpa_swap = leg14._frechet_mean_multistart(swap_frames)
    consensus = gpa_v2["mean"]
    swap_consensus = gpa_swap["mean"]
    width = max(consensus.shape[1], swap_consensus.shape[1])
    a_center = leg14._pad(consensus, width)
    b_center = leg14._pad(swap_consensus, width)
    b_aligned = leg14._align(b_center, a_center)
    delta = a_center - b_aligned
    offset_norm = float(np.linalg.norm(delta))
    categories = a_center.shape[0] // len(ROLES)

    s1_basis = e2._pattern_basis_to_matrix_basis(s1_patterns, width)
    s2_basis = e2._pattern_basis_to_matrix_basis(s2_patterns, width)
    s3_family = _s3_bases_for_center(a_center, width, categories)
    bases = {
        "S1_safety_complement": s1_basis, "S2_supervision_span": s2_basis,
        "S3_norm_scale_modes": s3_family["S3_norm_scale_modes"],
    }
    registered = e2._sequential_shares(delta, bases, e2.SUBSPACE_NAMES)
    reverse = e2._sequential_shares(delta, bases, tuple(reversed(e2.SUBSPACE_NAMES)))
    standalone = {
        name: float(np.sum(e2._project(delta.reshape(-1), b) ** 2) / max(float(np.sum(delta.reshape(-1) ** 2)), e2.EPS))
        for name, b in bases.items()
    }
    s3_component = registered["components"]["S3_norm_scale_modes"]
    family_bases = {k: s3_family[k] for k in ("n1_centering_mass", "n2_column_scale", "n3_role_size")}
    s3_family_shares = e2._sequential_shares(
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


# ---------------------------------------------------------------------------
# context build + cache (expensive step, paid once per world)
# ---------------------------------------------------------------------------


def _cache_dir(output: Path) -> Path:
    path = output / "_context_cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _contexts_for_world(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> list[dict[str, Any]]:
    cache_path = _cache_dir(output) / f"contexts_{world}.pkl"
    if cache_path.exists():
        with cache_path.open("rb") as handle:
            return pickle.load(handle)
    repetitions = int(config["repetitions"])
    world_index = {name: index for index, name in enumerate(config["worlds"])}[world]
    expected_for = leg8._expected_geometries_lookup(config)
    contexts = []
    for repetition in range(repetitions):
        seed = leg3._world_seed(int(config["seed"]), repetition, world, world_index)
        started = time.time()
        context = leg4._build_context(
            world, repetition, seed, spec=spec, config=config,
            expected_geometries=expected_for(world, repetition, seed),
        )
        unit_gap = leg4._true_derivative_unit_check(
            context["truth"], context["flat"][("train", 0)][0]["response_next"].shape[1],
        )
        if unit_gap > 1e-10:
            raise RuntimeError(f"analytic D_true fails the unit check on {world} rep {repetition}: {unit_gap:.3e}")
        context["unit_gap"] = unit_gap
        contexts.append(context)
        print(f"[m4h2] context {world} rep={repetition} ({time.time() - started:.1f}s)", flush=True)
    with cache_path.open("wb") as handle:
        pickle.dump(contexts, handle)
    return contexts


# ---------------------------------------------------------------------------
# truth-recovery: oracle rows (arm-invariant, cached) + per-arm rows
# ---------------------------------------------------------------------------


def _regen_for_budget(context: dict[str, Any], spec: M4ChartEcologySpec, budget: float) -> dict[str, Any]:
    world = context["world"]
    repetition = context["repetition"]
    truth = context["truth"]
    events_b = int(round(spec.events * budget))
    if budget == 1.0:
        observed_b = context["observed"]
    else:
        spec_b = replace(spec, events=events_b)
        observed_b, truth_b = generate_m4_chart_ecology_world(world=world, spec=spec_b, seed=context["seed"])
        for role in ROLES:
            if not np.array_equal(truth_b.oracle_basis[role], truth.oracle_basis[role]):
                raise RuntimeError(f"frozen-world violation (oracle_basis) at budget {budget}: {world} rep {repetition}")
        for name in ("creation", "gate", "generated_base", "selection"):
            if not np.array_equal(truth_b.author_parameters[name], truth.author_parameters[name]):
                raise RuntimeError(f"frozen-world violation (author_parameters.{name}) at budget {budget}: {world} rep {repetition}")
    per_view: dict[str, dict[int, tuple[dict, dict]]] = {}
    for view in ("train", "test"):
        calibration_panel = getattr(observed_b.ecology, f"{view}_calibration")
        selection_panel = getattr(observed_b.ecology, f"{view}_selection")
        rows = {}
        for author in range(context["authors"]):
            rows[author] = (
                leg4._flatten_events(calibration_panel, author),
                leg4._flatten_events(selection_panel, author),
            )
        per_view[view] = rows
    return {"events": events_b, "per_view": per_view}


def _regen_for_budget_cached(
    context: dict[str, Any], spec: M4ChartEcologySpec, budget: float, output: Path,
) -> dict[str, Any]:
    """Disk-cached wrapper: regeneration (~6s each, dominated by
    generate_m4_chart_ecology_world) is ARM-INVARIANT -- computed once per
    (world, repetition, budget) during the oracle stage and reused by every
    one of the seven arm stages, instead of being recomputed seven times."""
    cache_dir = _cache_dir(output)
    cache_path = cache_dir / f"regen_{context['world']}_r{context['repetition']}_b{budget:g}.pkl"
    if cache_path.exists():
        with cache_path.open("rb") as handle:
            return pickle.load(handle)
    regen = _regen_for_budget(context, spec, budget)
    with cache_path.open("wb") as handle:
        pickle.dump(regen, handle)
    return regen


def _oracle_truth_rows(context: dict[str, Any], regen: dict[str, Any], budget: float) -> list[dict[str, Any]]:
    world = context["world"]
    repetition = context["repetition"]
    truth = context["truth"]
    dims = context["flat"][("train", 0)][0]["response_next"].shape[1]
    fit_kwargs = context["fit_kwargs"]
    rows = []
    for view in ("train", "test"):
        for author in range(context["authors"]):
            stack = context["oracle_stacks"][view][author]
            degenerate = bool(float(np.linalg.norm(stack["D"])) < leg4.FLIP_TOLERANCE)
            keys = {
                "world": world, "repetition": repetition, "view": view, "author": author,
                "budget": budget, "events": regen["events"], "degenerate_reference": degenerate,
            }
            if degenerate:
                rows.append({**keys, "e_orc_true": np.nan})
                continue
            route = stack["selected_model"]
            calibration_b, selection_b = regen["per_view"][view][author]
            d_true = leg4._true_derivative(truth, author)
            d_orc_b = leg4._forced_route_derivative(
                calibration_b, selection_b, truth.oracle_basis, model=route,
                hazard_ridge=fit_kwargs["hazard_ridge"], logistic_iterations=fit_kwargs["logistic_iterations"],
                dimensions=dims,
            )
            e_orc_true = leg3._relative_error(d_orc_b, d_true)
            rows.append({**keys, "e_orc_true": e_orc_true})
    return rows


def _arm_truth_rows(
    context: dict[str, Any], regen: dict[str, Any], budget: float, arm: str, basis: dict[str, np.ndarray],
) -> list[dict[str, Any]]:
    world = context["world"]
    repetition = context["repetition"]
    truth = context["truth"]
    dims = context["flat"][("train", 0)][0]["response_next"].shape[1]
    fit_kwargs = context["fit_kwargs"]
    rows = []
    for view in ("train", "test"):
        for author in range(context["authors"]):
            stack = context["oracle_stacks"][view][author]
            degenerate = bool(float(np.linalg.norm(stack["D"])) < leg4.FLIP_TOLERANCE)
            keys = {
                "world": world, "repetition": repetition, "view": view, "author": author,
                "arm": arm, "c": 1.0, "budget": budget, "events": regen["events"], "degenerate_reference": degenerate,
            }
            if degenerate:
                rows.append({**keys, "e_arm_true": np.nan})
                continue
            route = stack["selected_model"]
            calibration_b, selection_b = regen["per_view"][view][author]
            d_true = leg4._true_derivative(truth, author)
            d_arm_b = leg4._forced_route_derivative(
                calibration_b, selection_b, basis, model=route,
                hazard_ridge=fit_kwargs["hazard_ridge"], logistic_iterations=fit_kwargs["logistic_iterations"],
                dimensions=dims,
            )
            e_arm_true = leg3._relative_error(d_arm_b, d_true)
            rows.append({**keys, "e_arm_true": e_arm_true})
    return rows


# ---------------------------------------------------------------------------
# G3 spot check (dual computation: context["flat"] vs freshly re-flattened
# budget=1.0 panels), disclosed near-duplicate of M4-G7's own
# `_g3_spot_check`, generalized to this leg's seven arms, no ridge dispatch.
# ---------------------------------------------------------------------------


def _g3_spot_check(world: str, contexts: list[dict[str, Any]], spec: M4ChartEcologySpec) -> list[dict[str, Any]]:
    dims = contexts[0]["flat"][("train", 0)][0]["response_next"].shape[1]
    rep_idx = view = author = context = stack = None
    for candidate_rep_idx, candidate_context in enumerate(contexts):
        found = False
        for candidate_view in ("train", "test"):
            for candidate_author in range(candidate_context["authors"]):
                candidate_stack = candidate_context["oracle_stacks"][candidate_view][candidate_author]
                if float(np.linalg.norm(candidate_stack["D"])) >= leg4.FLIP_TOLERANCE:
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
    d_true = leg4._true_derivative(context["truth"], author)
    regen = _regen_for_budget(context, spec, 1.0)
    calibration_g, selection_g = regen["per_view"][view][author]

    rows: list[dict[str, Any]] = []
    for arm in ARMS:
        basis, _, _ = _basis_for_arm(context, arm)
        d_flatstyle = leg4._forced_route_derivative(
            calibration_flat, selection_flat, basis, model=route,
            hazard_ridge=fit_kwargs["hazard_ridge"], logistic_iterations=fit_kwargs["logistic_iterations"], dimensions=dims,
        )
        d_regen = leg4._forced_route_derivative(
            calibration_g, selection_g, basis, model=route,
            hazard_ridge=fit_kwargs["hazard_ridge"], logistic_iterations=fit_kwargs["logistic_iterations"], dimensions=dims,
        )
        e_flatstyle = leg3._relative_error(d_flatstyle, d_true)
        e_regen = leg3._relative_error(d_regen, d_true)
        rows.append({
            "world": world, "arm": arm, "repetition": rep_idx, "view": view, "author": author,
            "e_arm_true_flatstyle": e_flatstyle, "e_arm_true_regen_budget1": e_regen,
            "abs_diff": abs(e_flatstyle - e_regen),
        })
    return rows


# ---------------------------------------------------------------------------
# G2 basis liveness: chordal quotient distance of each arm's stacked frame
# against deployed's, per rep.
# ---------------------------------------------------------------------------


def _g2_liveness_rows(world: str, contexts: list[dict[str, Any]], arm: str) -> list[dict[str, Any]]:
    rows = []
    for context in contexts:
        deployed_basis, _, _ = _basis_for_arm(context, "deployed")
        arm_basis, _, _ = _basis_for_arm(context, arm)
        deployed_frame = leg11._stack_frame(deployed_basis)
        arm_frame = leg11._stack_frame(arm_basis)
        distance = leg14._quotient_distance(deployed_frame, arm_frame)
        rows.append({"world": world, "arm": arm, "repetition": context["repetition"], "basis_distance_vs_deployed": distance})
    return rows


# ---------------------------------------------------------------------------
# stage: oracle (arm-invariant truth rows, cached per world)
# ---------------------------------------------------------------------------


def _run_oracle(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    contexts = _contexts_for_world(world, config, spec, output)
    all_rows: list[dict[str, Any]] = []
    for context in contexts:
        for budget in TRUTH_BUDGETS:
            t0 = time.time()
            regen = _regen_for_budget_cached(context, spec, budget, output)
            rows = _oracle_truth_rows(context, regen, budget)
            all_rows.extend(rows)
            print(f"[m4h2] oracle b={budget:g} {world} rep={context['repetition']} ({time.time() - t0:.1f}s)", flush=True)
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(all_rows).to_csv(output / f"partial_oracle_{world}.csv", index=False)
    print(f"[m4h2] oracle stage done: {world} ({time.time() - started:.1f}s total)", flush=True)


def _run_g3(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    partial_path = output / f"partial_g3_{world}.csv"
    if partial_path.exists():
        print(f"[m4h2] SKIP (partial exists): g3 {world}", flush=True)
        return
    contexts = _contexts_for_world(world, config, spec, output)
    rows = _g3_spot_check(world, contexts, spec)
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(partial_path, index=False)
    print(f"[m4h2] g3 stage done: {world} ({time.time() - started:.1f}s total)", flush=True)


# ---------------------------------------------------------------------------
# stage: arm (offset/shares/disp/G2/G3/truth for one (world, arm))
# ---------------------------------------------------------------------------


def _run_arm(world: str, arm: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    partial_path = output / f"partial_arm_{world}_{arm}.json"
    if partial_path.exists():
        print(f"[m4h2] SKIP (partial exists): {world} {arm}", flush=True)
        return
    contexts = _contexts_for_world(world, config, spec, output)
    oracle_path = output / f"partial_oracle_{world}.csv"
    if not oracle_path.exists():
        raise RuntimeError(f"oracle stage must run before arm stage: missing {oracle_path}")
    oracle_rows = pd.read_csv(oracle_path)

    s1_cache = output / f"_context_cache/s1s2_{world}.pkl"
    if s1_cache.exists():
        with s1_cache.open("rb") as handle:
            s1_patterns, s2_patterns, s1s2_meta = pickle.load(handle)
    else:
        s1_per_rep = []
        s2_per_rep = []
        q_values = []
        arm_b_gate_max = 0.0
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
        s1s2_meta = {
            "arm_b_gate_max": arm_b_gate_max, "s1_captured": s1_captured, "s2_captured": s2_captured,
            "d1": d1, "d2": d2, "q_values": q_values,
        }
        with s1_cache.open("wb") as handle:
            pickle.dump((s1_patterns, s2_patterns, s1s2_meta), handle)

    offset_shares = _arm_offset_and_shares(world, contexts, arm, s1_patterns, s2_patterns)
    g2_rows = _g2_liveness_rows(world, contexts, arm)

    truth_rows: list[dict[str, Any]] = []
    for context in contexts:
        for budget in TRUTH_BUDGETS:
            t0 = time.time()
            regen = _regen_for_budget_cached(context, spec, budget, output)
            basis, _, _ = _basis_for_arm(context, arm)
            rows = _arm_truth_rows(context, regen, budget, arm, basis)
            truth_rows.extend(rows)
            print(f"[m4h2] truth b={budget:g} {world} {arm} rep={context['repetition']} ({time.time() - t0:.1f}s)", flush=True)

    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(offset_shares["disp_rows"]).to_csv(output / f"partial_disp_{world}_{arm}.csv", index=False)
    pd.DataFrame(g2_rows).to_csv(output / f"partial_g2_{world}_{arm}.csv", index=False)
    pd.DataFrame(truth_rows).to_csv(output / f"partial_truth_{world}_{arm}.csv", index=False)
    summary = {k: v for k, v in offset_shares.items() if k != "disp_rows"}
    with partial_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    print(f"[m4h2] arm stage done: {world} {arm} ({time.time() - started:.1f}s total)", flush=True)


# ---------------------------------------------------------------------------
# smoke stage: 1 rep, 2 arms, 1 budget -- cheap correctness+timing check
# ---------------------------------------------------------------------------


def _run_smoke(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    t0 = time.time()
    repetitions = int(config["repetitions"])
    world_index = {name: index for index, name in enumerate(config["worlds"])}[world]
    expected_for = leg8._expected_geometries_lookup(config)
    seed = leg3._world_seed(int(config["seed"]), 0, world, world_index)
    context = leg4._build_context(
        world, 0, seed, spec=spec, config=config, expected_geometries=expected_for(world, 0, seed),
    )
    print(f"[m4h2 smoke] context built ({time.time() - t0:.1f}s)", flush=True)

    for arm in ("deployed", "basisvar_whitening_unscaled", "basisvar_source_scale_off", "basisvar_rank_tolerance_tight"):
        t1 = time.time()
        basis, ingredients, meta = _basis_for_arm(context, arm)
        if arm == "deployed":
            gap = max(float(np.max(np.abs(basis[role] - context["v2_basis"][role]))) for role in ROLES)
            print(f"[m4h2 smoke] deployed basis vs context v2_basis max|diff|={gap:.3e}", flush=True)
            assert gap <= G1_ANCHOR_TOLERANCE, f"deployed basis reconstruction fails G1 anchor: {gap:.3e}"
        print(
            f"[m4h2 smoke] arm={arm} width={basis['calibration'].shape[1]} meta={meta} ({time.time() - t1:.1f}s)",
            flush=True,
        )

    t2 = time.time()
    regen = _regen_for_budget(context, spec, 4.0)
    print(f"[m4h2 smoke] regen budget=4x ({time.time() - t2:.1f}s)", flush=True)
    t3 = time.time()
    oracle_rows = _oracle_truth_rows(context, regen, 4.0)
    print(f"[m4h2 smoke] oracle rows n={len(oracle_rows)} ({time.time() - t3:.1f}s)", flush=True)
    t4 = time.time()
    basis, _, _ = _basis_for_arm(context, "basisvar_whitening_unscaled")
    arm_rows = _arm_truth_rows(context, regen, 4.0, "basisvar_whitening_unscaled", basis)
    print(f"[m4h2 smoke] arm rows n={len(arm_rows)} ({time.time() - t4:.1f}s)", flush=True)
    print(f"[m4h2 smoke] TOTAL ({time.time() - t0:.1f}s)", flush=True)


# ---------------------------------------------------------------------------
# assemble + adjudicate
# ---------------------------------------------------------------------------


def _assemble(output: Path) -> None:
    worlds = list(HIGH_GAP_WORLDS)
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

    disp_rows = pd.concat(
        [pd.read_csv(output / f"partial_disp_{w}_{a}.csv") for w in worlds for a in ARMS], ignore_index=True,
    )
    g2_rows = pd.concat(
        [pd.read_csv(output / f"partial_g2_{w}_{a}.csv") for w in worlds for a in BASISVAR_ARMS], ignore_index=True,
    )
    truth_rows = pd.concat(
        [pd.read_csv(output / f"partial_truth_{w}_{a}.csv") for w in worlds for a in ARMS], ignore_index=True,
    )
    oracle_rows = pd.concat([pd.read_csv(output / f"partial_oracle_{w}.csv") for w in worlds], ignore_index=True)
    g3_rows = pd.concat([pd.read_csv(output / f"partial_g3_{w}.csv") for w in worlds], ignore_index=True)
    arm_summaries = {
        (w, a): _load_json(output / f"partial_arm_{w}_{a}.json") for w in worlds for a in ARMS
    }

    expected_disp = len(worlds) * len(ARMS) * 8
    if len(disp_rows) != expected_disp:
        raise RuntimeError(f"disp rows {len(disp_rows)} != expected {expected_disp}")
    expected_truth_arm_rows = len(worlds) * 8 * len(TRUTH_BUDGETS) * 2 * 16
    for arm in ARMS:
        n = len(truth_rows[truth_rows["arm"] == arm])
        if n != expected_truth_arm_rows:
            raise RuntimeError(f"truth rows for arm {arm}: {n} != expected {expected_truth_arm_rows}")
    expected_oracle_rows = len(worlds) * 8 * len(TRUTH_BUDGETS) * 2 * 16
    if len(oracle_rows) != expected_oracle_rows:
        raise RuntimeError(f"oracle rows {len(oracle_rows)} != expected {expected_oracle_rows}")

    # join truth (arm) with oracle (arm-invariant) to get combined e_arm_true/e_orc_true rows
    join_keys = ["world", "repetition", "view", "author", "budget"]
    truth_joined = truth_rows.merge(
        oracle_rows[join_keys + ["e_orc_true", "degenerate_reference"]], on=join_keys, how="inner", suffixes=("", "_oracle"),
    )
    if len(truth_joined) != len(truth_rows):
        raise RuntimeError("oracle join lost truth rows")
    truth_joined["degenerate_reference"] = (
        truth_joined["degenerate_reference"].astype(bool) | truth_joined["degenerate_reference_oracle"].astype(bool)
    )

    # ---- G1 ANCHOR ------------------------------------------------------------
    e2_decision = _load_json(E2_DECISION_PATH)
    leg14_decision = _load_json(LEG14_DECISION_PATH)
    leg14_disp_rows = pd.read_csv(LEG14_DISPLACEMENT_ROWS_PATH)
    leg14_gap_rows = pd.read_csv(LEG14_GAP_ROWS_PATH)

    metric1_anchor_rows = []
    for w in worlds:
        mine_scoped = disp_rows[(disp_rows["world"] == w) & (disp_rows["arm"] == "deployed")]
        for _, row in mine_scoped.iterrows():
            ref_row = leg14_disp_rows[(leg14_disp_rows["world"] == w) & (leg14_disp_rows["repetition"] == row["repetition"])]
            if len(ref_row) != 1:
                raise RuntimeError(f"Leg14 displacement anchor missing for {w} rep {row['repetition']}")
            theirs = float(ref_row.iloc[0]["disp_v2"])
            metric1_anchor_rows.append({
                "world": w, "repetition": int(row["repetition"]), "mine": float(row["disp_v2"]), "leg14_persisted": theirs,
                "abs_diff": abs(float(row["disp_v2"]) - theirs),
            })
    metric1_anchor_max = max(r["abs_diff"] for r in metric1_anchor_rows)

    metric2_anchor_rows = []
    for w in worlds:
        mine = arm_summaries[(w, "deployed")]
        theirs = e2_decision["offset_table"][w]
        offset_diff = abs(mine["offset_norm"] - float(theirs["offset_norm"]))
        share_diffs = {name: abs(mine["registered_shares"][name] - float(theirs["registered_shares"][name])) for name in e2.SUBSPACE_NAMES + ("S4_residual",)}
        reverse_diffs = {name: abs(mine["reverse_shares"][name] - float(theirs["reverse_shares"][name])) for name in e2.SUBSPACE_NAMES + ("S4_residual",)}
        standalone_diffs = {name: abs(mine["standalone_shares"][name] - float(theirs["standalone_shares"][name])) for name in e2.SUBSPACE_NAMES}
        family_diffs = {name: abs(mine["s3_family_shares"][name] - float(theirs["s3_family_shares"][name])) for name in mine["s3_family_shares"]}
        metric2_anchor_rows.append({
            "world": w, "offset_norm_abs_diff": offset_diff,
            "max_share_abs_diff": max(list(share_diffs.values()) + list(reverse_diffs.values()) + list(standalone_diffs.values()) + list(family_diffs.values())),
        })
    metric2_anchor_max = max(max(r["offset_norm_abs_diff"], r["max_share_abs_diff"]) for r in metric2_anchor_rows)

    g3_deployed = g3_rows[g3_rows["arm"] == "deployed"]
    metric3_g3_anchor_rows = []
    for _, row in g3_deployed.iterrows():
        w = row["world"]
        ref = leg14_gap_rows[
            (leg14_gap_rows["world"] == w) & (leg14_gap_rows["repetition"] == row["repetition"])
            & (leg14_gap_rows["view"] == row["view"]) & (leg14_gap_rows["author"] == row["author"])
        ]
        if len(ref) != 1:
            raise RuntimeError(f"Leg14 gap_rows anchor missing for {w}")
        ref = ref.iloc[0]
        my_e_v2 = float(row["e_arm_true_regen_budget1"])
        their_e_v2 = float(ref["e_v2_true"])
        metric3_g3_anchor_rows.append({
            "world": w, "mine_e_v2_true_budget1": my_e_v2, "leg14_persisted_e_v2_true": their_e_v2,
            "abs_diff": abs(my_e_v2 - their_e_v2),
        })
    metric3_g3_anchor_max = max(r["abs_diff"] for r in metric3_g3_anchor_rows)

    g1_anchor_max = max(metric1_anchor_max, metric2_anchor_max, metric3_g3_anchor_max)
    g1_anchor = {
        "tolerance": G1_ANCHOR_TOLERANCE,
        "metric1_disp_v2_vs_leg14": {"n_checks": len(metric1_anchor_rows), "max_abs_diff": metric1_anchor_max},
        "metric2_offset_and_shares_vs_m4e2": {"per_world": metric2_anchor_rows, "max_abs_diff": metric2_anchor_max},
        "metric3_e_v2_true_budget1_vs_leg14_gap_rows": {"n_checks": len(metric3_g3_anchor_rows), "max_abs_diff": metric3_g3_anchor_max},
        "max_abs_diff_overall": g1_anchor_max,
        "pass": bool(g1_anchor_max <= G1_ANCHOR_TOLERANCE),
    }

    # ---- G2 BASIS LIVENESS -----------------------------------------------------
    deployed_disp_median = float(disp_rows[disp_rows["arm"] == "deployed"]["disp_v2"].median())
    g2_by_arm = {}
    for arm in BASISVAR_ARMS:
        scoped = g2_rows[g2_rows["arm"] == arm]
        median_dist = float(scoped["basis_distance_vs_deployed"].median())
        ratio = median_dist / deployed_disp_median if deployed_disp_median > 0 else float("nan")
        g2_by_arm[arm] = {
            "median_basis_distance_vs_deployed": median_dist,
            "ratio_to_deployed_median_disp_v2": ratio,
            "live": bool(ratio >= G2_MATERIALITY_RATIO),
        }
    g2_basis_liveness = {
        "statement": "every basisvar arm's own stacked frame must differ from deployed's by >= 10% of deployed's median disp_v2 (chordal quotient distance, per rep, median over 8 reps x 3 worlds)",
        "materiality_ratio": G2_MATERIALITY_RATIO,
        "deployed_median_disp_v2": deployed_disp_median,
        "by_arm": g2_by_arm,
        "all_live": bool(all(v["live"] for v in g2_by_arm.values())),
    }

    # ---- G3 TRUTH-PATH INVARIANCE ----------------------------------------------
    g3_gate = {
        "statement": "budget=1.0 freshly-regenerated panels reproduce context['flat']-sourced refits exactly, every arm, one spot-check (rep,view,author) per world",
        "max_abs_diff": float(g3_rows["abs_diff"].max()),
        "n_checks": int(len(g3_rows)),
        "tolerance": G3_TOLERANCE,
        "pass": bool(g3_rows["abs_diff"].max() <= G3_TOLERANCE),
    }

    # ---- metric 1 (lean a): disp_v2, REP grain primary (n=24), WORLD companion (n=3)
    disp_wide = disp_rows.set_index(["world", "repetition", "arm"])["disp_v2"]
    lean_a_by_arm = {}
    for arm in BASISVAR_ARMS:
        reduction_rep = np.array([
            float(disp_wide[(w, r, "deployed")] - disp_wide[(w, r, arm)]) for w in worlds for r in range(8)
        ])
        ci_rep = g1._paired_world_ci(reduction_rep)  # generic paired t-CI, reused at rep grain
        deployed_mean_rep = float(disp_rows[disp_rows["arm"] == "deployed"]["disp_v2"].mean())
        reduction_pct_rep = float(np.mean(reduction_rep)) / deployed_mean_rep
        bar_absolute_rep = LEAN_A_BAR * deployed_mean_rep

        reduction_world = np.array([
            float(disp_rows[(disp_rows["world"] == w) & (disp_rows["arm"] == "deployed")]["disp_v2"].median())
            - float(disp_rows[(disp_rows["world"] == w) & (disp_rows["arm"] == arm)]["disp_v2"].median())
            for w in worlds
        ])
        ci_world = g1._paired_world_ci(reduction_world)
        deployed_mean_world = float(np.mean([
            float(disp_rows[(disp_rows["world"] == w) & (disp_rows["arm"] == "deployed")]["disp_v2"].median()) for w in worlds
        ]))
        reduction_pct_world = float(np.mean(reduction_world)) / deployed_mean_world

        lean_a_by_arm[arm] = {
            "rep_grain_PRIMARY": {
                "n": ci_rep["n"], "mean_reduction_absolute": ci_rep["mean"], "reduction_pct": reduction_pct_rep,
                "ci_lo": ci_rep["ci_lo"], "ci_hi": ci_rep["ci_hi"], "half_width": ci_rep["half_width"],
                "bar_absolute": bar_absolute_rep,
                "underpowered_vs_bar": bool(np.isfinite(ci_rep["half_width"]) and ci_rep["half_width"] > bar_absolute_rep),
                "clears_25pct_bar": bool(reduction_pct_rep >= LEAN_A_BAR),
                "ci_excludes_zero": bool(ci_rep["ci_lo"] > 0.0),
                "held": bool(reduction_pct_rep >= LEAN_A_BAR and ci_rep["ci_lo"] > 0.0),
            },
            "world_grain_companion_literal_text": {
                "n": ci_world["n"], "mean_reduction_absolute": ci_world["mean"], "reduction_pct": reduction_pct_world,
                "ci_lo": ci_world["ci_lo"], "ci_hi": ci_world["ci_hi"], "half_width": ci_world["half_width"],
                "clears_25pct_bar": bool(reduction_pct_world >= LEAN_A_BAR),
                "ci_excludes_zero": bool(ci_world["ci_lo"] > 0.0) if np.isfinite(ci_world["ci_lo"]) else False,
                "held": bool(reduction_pct_world >= LEAN_A_BAR and np.isfinite(ci_world["ci_lo"]) and ci_world["ci_lo"] > 0.0),
            },
        }
    lean_a_arms_holding_primary = [a for a in BASISVAR_ARMS if lean_a_by_arm[a]["rep_grain_PRIMARY"]["held"]]
    lean_a_held = len(lean_a_arms_holding_primary) >= 1
    winner = None
    if lean_a_arms_holding_primary:
        winner = max(lean_a_arms_holding_primary, key=lambda a: lean_a_by_arm[a]["rep_grain_PRIMARY"]["reduction_pct"])
    lean_a = {
        "statement": "at least one basisvar_<k> reduces Leg 14's gap by >=25% relative to deployed, paired CI excluding zero (rep grain primary, n=24; world grain companion, n=3, literal-text reading)",
        "by_arm": lean_a_by_arm,
        "arms_holding_primary": lean_a_arms_holding_primary,
        "winner": winner,
        "held": bool(lean_a_held),
    }

    pivot_fires = not lean_a_held
    pivot = {
        "registered": "no arm reduces the gap by >=25% with a CI excluding zero -> the displacement is NOT in the basis's normalization either; the remaining candidate is the CONSENSUS/ALIGNMENT step",
        "fires": bool(pivot_fires),
    }

    # ---- lean b: mechanistic consistency (winner's S3 share falls) -----------
    lean_b = {"statement": "at the winning arm, S3's registered-order share falls relative to deployed", "applicable": winner is not None}
    if winner is not None:
        deployed_s3 = float(arm_summaries[(worlds[0], "deployed")]["registered_shares"]["S3_norm_scale_modes"])
        s3_by_world = {
            w: {
                "deployed": float(arm_summaries[(w, "deployed")]["registered_shares"]["S3_norm_scale_modes"]),
                "winner": float(arm_summaries[(w, winner)]["registered_shares"]["S3_norm_scale_modes"]),
            }
            for w in worlds
        }
        falls_all_worlds = all(s3_by_world[w]["winner"] < s3_by_world[w]["deployed"] for w in worlds)
        mean_deployed = float(np.mean([s3_by_world[w]["deployed"] for w in worlds]))
        mean_winner = float(np.mean([s3_by_world[w]["winner"] for w in worlds]))
        lean_b.update({
            "winner": winner,
            "predicted_family_companion_non_adjudicating": ARM_S3_FAMILY_PREDICTION[winner],
            "s3_share_by_world": s3_by_world,
            "mean_s3_share_deployed": mean_deployed, "mean_s3_share_winner": mean_winner,
            "falls_in_all_3_worlds": bool(falls_all_worlds),
            "held": bool(falls_all_worlds),
        })
    else:
        lean_b["held"] = False

    # ---- lean c: truth recovery does not worsen at the winner -----------------
    lean_c = {"statement": "truth-referenced recovery does not worsen at the winning arm vs deployed, both budgets, equivalence form, margin=0.02", "applicable": winner is not None}
    if winner is not None:
        author_truth = g4._author_level_truth_with_c(truth_joined)
        lean_c_by_budget = {}
        for budget in TRUTH_BUDGETS:
            author_ci = g4._paired_author_diff_ci(author_truth, winner, 1.0, "deployed", 1.0, budget, worlds)
            world_ci = g4._paired_world_diff_ci(author_truth, winner, 1.0, "deployed", 1.0, budget, worlds)
            author_class = g4._classify_pair(author_ci, LEAN_C_MARGIN, one_sided=True)
            underpowered = bool(author_ci["n"] > 1 and author_ci["half_width"] > G0_FRACTION_BAR_METRIC3)
            lean_c_by_budget[str(budget)] = {
                "author_grain": {
                    "n": author_ci["n"], "mean_diff_winner_minus_deployed": author_ci["mean"],
                    "ci_lo": author_ci["ci_lo"], "ci_hi": author_ci["ci_hi"], "half_width": author_ci["half_width"],
                    "class": author_class, "underpowered_vs_g0_bar": underpowered,
                },
                "world_grain_companion": {
                    "n": world_ci["n"], "mean_diff_winner_minus_deployed": world_ci["mean"],
                    "ci_lo": world_ci["ci_lo"], "ci_hi": world_ci["ci_hi"],
                },
            }
        lean_c_held = bool(all(lean_c_by_budget[str(b)]["author_grain"]["class"] == "WITHIN" for b in TRUTH_BUDGETS))
        lean_c.update({"winner": winner, "margin": LEAN_C_MARGIN, "by_budget": lean_c_by_budget, "held": lean_c_held})
    else:
        lean_c["held"] = False

    # ---- G0 POWER ---------------------------------------------------------------
    leg14_target_level = {w: float(leg14_decision["displacement_table"][w]["median_disp_v2"]) for w in worlds}
    g0_power = {
        "metric1_displacement": {
            "grain": "repetition (n=24, PRIMARY, per G7 precedent) / world (n=3, companion, literal text)",
            "target_level_leg14_persisted_median_disp_v2_by_world": leg14_target_level,
            "bar_fraction": LEAN_A_BAR,
            "by_arm_half_width_rep_grain": {a: lean_a_by_arm[a]["rep_grain_PRIMARY"]["half_width"] for a in BASISVAR_ARMS},
            "by_arm_bar_absolute_rep_grain": {a: lean_a_by_arm[a]["rep_grain_PRIMARY"]["bar_absolute"] for a in BASISVAR_ARMS},
            "by_arm_underpowered_rep_grain": {a: lean_a_by_arm[a]["rep_grain_PRIMARY"]["underpowered_vs_bar"] for a in BASISVAR_ARMS},
        },
        "metric2_shares": {
            "grain": "world (n=3, census -- M4-E2/M4-H1's own convention, no finer grain is defined)",
            "note": "point comparison, no CI; reported per world for all 7 arms",
        },
        "metric3_truth_recovery": {
            "grain": "author (n up to 384, at the winning arm only, per M4-G3's hand-off recommendation)",
            "bar_absolute": G0_FRACTION_BAR_METRIC3, "margin": LEAN_C_MARGIN,
            "half_width_by_budget": (
                {str(b): lean_c["by_budget"][str(b)]["author_grain"]["half_width"] for b in TRUTH_BUDGETS}
                if winner is not None else None
            ),
        },
    }

    # ---- G4 MATERIALITY FORM ----------------------------------------------------
    g4_materiality_form = {
        "G0": "CI-half-width-vs-bar equivalence bound per metric; underpowered comparisons flagged explicitly",
        "G1": "degenerate exact-equality checks (tolerance 1e-12) against independently persisted M4-E2/Leg14 sources, not significance tests",
        "G2": "ratio-to-deployed-scale liveness bound (10% materiality margin), not nil-significance",
        "G3": "degenerate exact-equality check (tolerance 1e-12) between two independently-derived computations",
        "lean_a": "paired-by-repetition CI-excludes-zero test AND a >=25%-of-deployed-mean point-estimate bar, both required (directional materiality, not nil-significance)",
        "lean_b": "point comparison across all 3 registered worlds (a census, not a sample) -- share must fall in every world",
        "lean_c": "one-sided WITHIN/OUTSIDE/AMBIGUOUS classification on paired-author CI against a fixed +/-0.02 (upper-only) margin, both budgets",
    }

    if pivot_fires:
        verdict = "PIVOT_DISPLACEMENT_NOT_IN_BASIS_NORMALIZATION"
    elif lean_a["held"] and lean_b["held"] and lean_c["held"]:
        verdict = "CARRIER_CERTIFIED"
    elif lean_a["held"] and not (lean_b["held"] and lean_c["held"]):
        verdict = "CARRIER_FOUND_MECHANISM_OR_TRANSFER_UNCERTIFIED"
    else:
        verdict = "AMBIGUOUS_NO_CLEAN_BRANCH"

    decision = {
        "estimand_id": "SUICA_M4_H2_BASIS_NORMALIZATION",
        "tier": "EXPLORATORY (open-exploration phase)",
        "registered_in": "docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md M4-H2 registration (2026-08-03, BEFORE run); ledger row M4-H2",
        "worlds": worlds,
        "arms": list(ARMS),
        "basisvar_arms": list(BASISVAR_ARMS),
        "truth_budgets": list(TRUTH_BUDGETS),
        "part0_inventory": {
            "candidate_carriers": {
                "basisvar_source_scale_off": "per-source robust standardization, m4_condition_manifold_estimator.py:165 (skip -> identity)",
                "basisvar_center_median": "reference-panel centering, m4_condition_manifold_estimator.py:565 (mean -> median)",
                "basisvar_rank_tolerance_tight": "eigenvalue rank-retention threshold, m4_condition_manifold_estimator.py:574-577 (1e-6 -> 1e-3)",
                "basisvar_whitening_shrinkage": "whitening scale, m4_condition_manifold_estimator.py:580-583 (regularized, lambda=0.10*median(retained eig))",
                "basisvar_whitening_unscaled": "whitening scale, m4_condition_manifold_estimator.py:580-583 (unnormalized, drop 1/sqrt(eig))",
                "basisvar_intercept_matched_scale": "constant mass column, m4_condition_manifold_estimator.py:96 (unscaled 1.0 -> matched to whitened block's median column norm)",
            },
            "excluded_not_scored": {
                "chart_family_dimensions_neighbors_landmarks": "representation-fitting hyperparameters shared with, and fixed by, the closed chart-selection line (M4-F); m4_condition_manifold_estimator.py:294-339",
                "kernel_bandwidth": "chart-fitting hyperparameter, same scope boundary; m4_condition_manifold_estimator.py:325-328,286",
                "source_averaging": "feature-fusion choice, not a scale/center/normalization step; m4_condition_manifold_estimator.py:564",
                "covariance_denominator": "a priori bounded far below the 25% actionable bar (N=96 -> ~0.52% whitening effect), degenerate with M4-G2's already-characterized units axis; m4_condition_manifold_estimator.py:567-569",
                "whitening_numerical_floor": "verified never binding (smallest retained eigenvalue 6.7e-7 to 3.0e-6 vs the 1e-12 floor); m4_condition_manifold_estimator.py:582",
                "reference_panel_choice": "distinct data-source choice, would break the Leg14/M4-E2 anchor contract; m4_condition_manifold_estimator.py:556-563",
            },
        },
        "gates": {
            "G0_power": g0_power, "G1_anchor": g1_anchor, "G2_basis_liveness": g2_basis_liveness,
            "G3_truth_path_invariance": g3_gate, "G4_materiality_form": g4_materiality_form,
        },
        "lean_a_carrier_exists": lean_a,
        "lean_b_mechanistically_consistent": lean_b,
        "lean_c_not_cosmetic": lean_c,
        "pivot": pivot,
        "verdict": verdict,
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only (the 3 HIGH_GAP_WORLDS, reused verbatim from M4-E2/Leg14); "
            "truth-recovery via budget-regenerated (4x/8x events) finite panels from the frozen world law, "
            "compared to the analytic D_true; no natural-text, personality, or clinical claim; no seal, no "
            "independent verification (operator directive 2026-08-01)."
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
    if winner is not None:
        author_truth = g4._author_level_truth_with_c(truth_joined)
        author_truth.to_csv(output / "author_level_truth_rows.csv", index=False)

    print(json.dumps({
        "verdict": verdict, "pivot_fires": pivot_fires, "winner": winner,
        "lean_a_held": lean_a["held"], "lean_b_held": lean_b["held"], "lean_c_held": lean_c["held"],
        "g1_anchor_pass": g1_anchor["pass"], "g2_all_live": g2_basis_liveness["all_live"], "g3_pass": g3_gate["pass"],
    }, indent=2))


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "m4_chart_ecology.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "m4_h2_basis_normalization")
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
    if args.world not in HIGH_GAP_WORLDS:
        raise SystemExit(f"not a registered HIGH_GAP_WORLDS world: {args.world}")

    if args.smoke:
        _run_smoke(args.world, config, spec, args.output)
        return
    if args.stage == "oracle":
        _run_oracle(args.world, config, spec, args.output)
        return
    if args.stage == "g3":
        _run_g3(args.world, config, spec, args.output)
        return
    if args.arm is None:
        raise SystemExit("--arm is required unless --stage oracle/g3 or --smoke or --assemble")
    if args.arm not in ARMS:
        raise SystemExit(f"not a registered arm: {args.arm}")
    _run_arm(args.world, args.arm, config, spec, args.output)


if __name__ == "__main__":
    main()
