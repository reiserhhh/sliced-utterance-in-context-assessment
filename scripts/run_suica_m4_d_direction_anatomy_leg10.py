#!/usr/bin/env python3
"""M4-D Leg 10: direction-content anatomy of the discovery step.

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md,
"Leg 10 -- direction-content anatomy of the discovery step", 2026-08-02 loop
cycle 5, commit 3ed9f18, BEFORE this run). Machinery is IMPORTED from the
validated legs -- Leg 4's context build + forced-route derivative, Leg 8's
flexible-penalty lever fits + conditioning-row construction, Leg 9's gap
semantics and persisted swap rows as the bit-anchor -- nothing is
reimplemented.

THE QUESTION. Leg 9's content swap pinned the residual paired gap (~.136
pooled; .21-.26 in the three high-gap worlds) to PER-CATEGORY ROW-DIRECTION
CONTENT of the discovered chart: oracle row directions + discovered row norms
eliminate the gap (basis_content_share 1.06-1.11), support weights ~0. WHERE
does discovery lose the directions, and is the loss attributable?

THE DISCOVERY STEP under anatomy (the M4-C.2/V2 response-safe chart path):
`fit_m4_condition_chart` selects a chart family on the REFERENCE panels using
only declared pre-response variables (the response-safe discipline: the
contract stores `response` separately, "unavailable to the chart-fitting
functions"); `freeze_m4_condition_transform` refits the winning candidate,
computes landmark-RBF features of the reference-calibration prototypes, and
WHITENS them (covariance eigendecomposition, hard rank cut at
rank_tolerance=1e-6 relative, cap 12, then 1/sqrt(eig)). The discovered basis
rows = [1, whitened chart features of each category prototype]. Two structural
suspects live in this path: (i) the whitening is an UNREGULARIZED inverse --
retained directions with eigenvalues down to 1e-6 of the top are amplified by
up to 1e3, so reference-panel sampling noise enters every category row at
unit scale (the discovery-stage analog of the estimator legs' penalty
pathology, with the sign reversed: the hazard was over-penalized, the
whitening is un-penalized); (ii) the response-safe constraint denies the
chart exactly the signal (responses are linear readouts of the true condition
features) that would anchor the retained subspace.

ARMS (registered; 3 high-gap worlds x 8 reps: endogenous_creation_expansion,
selection_creation_compensation, source_rotated_feedback):

A (de-biased discovery; registered lever = lambda~1/n at the discovery
  stage): rebuild the frozen transform's whitening with Tikhonov shrinkage,
  whitening = V_retained / sqrt(eig_retained + lambda_chart),
  lambda_chart = (trace(cov)/p) / n_ref  (mean eigenvalue over n_ref=96
  reference-calibration prototype rows -- the vanishing-with-n choice, the
  faithful transplant of Leg 8's `A_lam1n` "penalty divided by n" semantics
  to the chart's only inverse-covariance operation). The retained eigenvector
  set is EXACTLY V2's (same rank rule, same cap), so width and columns are
  unchanged and the ONLY difference is the amplification law. Chart family
  selection is NOT re-run (it happens before whitening and contains no
  lambda); the lever isolates the freeze/whitening stage. Measurements:
  (i) per-category row-direction alignment to oracle, (ii) the paired gap
  (forced-route V2 refit semantics on both sides -- Leg 9 showed the paired
  metric demands shared estimation conventions, so the registered gap column
  keeps the V2 estimator and moves ONLY the chart).
  UNREGISTERED-SECONDARY companions (clearly separated, no adjudication
  weight): A_x10 (lambda_chart scaled 10x -- guards the transplant's scale
  constant), and gap_A_lam1nboth (lam1n hazard on BOTH sides at the A chart
  -- covers the "chart/hazard" reading of the registered text with
  conventions still shared; its oracle side is bit-anchored to Leg 8's
  persisted A_lam1n lever rows).

B (response-safe relaxation; DIAGNOSTIC ONLY -- THIS VIOLATES AN OPERATIONAL
  DESIGN CONSTRAINT; every emitted row carries diagnostic_only=True and every
  table is labeled): fit discovery WITHOUT the response-safe projection.
  Implementation: on the SAME reference-calibration panel the V2 chart uses,
  regress each reference author's occasion-centered responses (the panel
  field the safety contract withholds) on the source-fused robust-standardized
  pre-context prototype features (intercept discarded), stack the per-author
  coefficient columns, SVD -> top-q response-relevant directions (q = rank at
  1e-8 relative, cap 6 = oracle raw width). Features = fused standardized
  prototypes @ U_q; then the UNCHANGED V2 freeze semantics (center + whiten
  + rank rule) on those features; mechanism-panel category rows transformed
  with the frozen reference centers/scales/U_q/whitening. Same two
  measurements. Attribution: how much of the direction deficit is the safety
  constraint's price.

C (conditioning elevation; the twice-registered hand-off): extend Leg 8's
  persisted conditioning profile (results/m4_d_bias_anatomy/
  conditioning_rows.csv; information operator I = X'WX/n of the final V2
  oracle-basis hazard fit at the forced route) to PER-CATEGORY resolution.
  Registered phrase "conditioning/rank of the information operator restricted
  to each category's direction subspace" is implemented as: restrict I to
  span(J_k) where J_k = the category's estimand Jacobian rows (Leg 8's probe
  machinery -- the parameter directions along which D[k] varies);
  cond_eff_k = lam_max(Q_k'IQ_k) / lam_min_eff(Q_k'IQ_k) with the near-null
  cut at Leg 8's NULL_RELATIVE_TOLERANCE=1e-8 RELATIVE TO THE FULL OPERATOR's
  lam_max. Companions (no adjudication weight): per-category CR sd ratio
  sqrt(J_k I^+ J_k' / n^2)/|D_true[k]|, per-category Jacobian near-null mass,
  and a design-pattern-span variant (span of the category's calibration/
  selection design patterns). Correlate per-category conditioning with the
  per-category V2 direction deficit across the 3 worlds x 16 categories
  (median over reps; conditioning additionally median over authors x views).

ALIGNMENT STATISTIC (registered choice, stated): per-category row-direction
alignment = cosine between the off-diagonal rows of the two bases' cosine-gram
matrices, per role, averaged over the three roles for the headline number:
  g[k,l] = <b_k, b_l> / (||b_k|| ||b_l||)   (full rows, Leg 9's direction
  convention: direction = full row up to norm),
  align[role,k] = cos( g_disc[k, l != k], g_orc[k, l != k] ),
  deficit[role,k] = 1 - align[role,k].
Rationale: ridge/IRLS fits consume the basis only through row inner products
(gram) and event-category incidence, so the normalized gram IS the
direction content; the statistic is invariant to orthogonal gauge and to row
norms, needs NO fitted cross-space map (widths 13 vs 7 differ), and cannot be
saturated by a near-interpolating linear identification. Companion columns:
align on non-constant columns only, and a subspace-level principal-angle
affinity (mean cos^2 principal angles between top-q eigenspaces of the two
cosine kernels in shared category space, q = oracle kernel rank at 1e-8
relative).

GAP SEMANTICS (Leg 9's, unchanged): per author-view at the oracle-forced
route, 1x r=0 panels, V2 estimator semantics:
  gap_arm = e_arm_true - e_orc_true,
world level = median over author-level (view-mean) rows; closure_arm =
1 - gap_arm_world / gap_v2_world.

REGISTERED LEANS (adjudication statistics pre-coded here):
- (a) de-biased discovery closes >= half the paired gap in >= 2 of the 3
  high-gap worlds: closure_A_world >= .5.
- (b) BAND, honest uncertainty: safety relaxation closes [10%, 60%] of the
  DIRECTION DEFICIT, pooled: closure_dir_B = 1 - sum_w(deficit_B_w) /
  sum_w(deficit_v2_w) in [.10, .60] (point-lean recorded separately:
  closure_dir_B < .5 -- the safety constraint is not the main price).
- (c) conditioning predicts deficit: Spearman(median log10 cond_eff_k,
  median deficit_k) >= .6 pooled over the 3 worlds x 16 categories
  (48 pairs).
PIVOT-IF (registered): none of A/B/C attributes >= half the gap -- A fails
lean (a), B's pooled closures (gap AND direction) both < .5, and C fails
lean (c) -- then the direction-deficit source is recorded as
DIRECTION_DEFICIT_SOURCE_UNIDENTIFIED; next instrument = perturbation
analysis of the discovery objective (gradient of direction estimates w.r.t.
panel composition) -- REGISTERED HAND-OFF ONLY, not run here.

FAITHFULNESS GATES (refused, not warned):
1. context build asserts V2 replay geometries vs archived
   results/m4_chart_ecology/metrics.csv (Leg 4 machinery);
2. whitening rebuild at lambda=0 must equal the frozen transform's
   whitening matrix/center and reproduce v2_basis (<= 1e-9);
3. per author-view: my forced-route V2 refit columns e_d_true_v2 /
   e_orc_true / gap_v2 (e_orc_true read from the oracle stack, whose
   identity to the forced refit Leg 9 gated at 1e-9) must match Leg 9's
   persisted gap_swap_rows.csv (<= 1e-9, degenerate flags equal);
4. per author-view: the recomputed Leg 8 aggregate conditioning row
   (lambda_max, condition_number_effective, cr_sd_over_d_true, ...) must
   match persisted conditioning_rows.csv (<= 1e-9 relative on numeric
   columns, flags equal);
5. unregistered lam1nboth oracle side must match Leg 8's persisted A_lam1n
   natural 1x lever rows (<= 1e-9).

Chunked execution (this arc's standard workaround): --chunk-start/--chunk-stop
[--worlds] run repetition ranges in the foreground writing partial CSVs;
--assemble concatenates all partials, REFUSES missing or duplicate cells, and
adjudicates from the concatenated rows only.
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_suica_m4_d_dleg_floor_leg4 as leg4  # noqa: E402  bit-exact reuse
import run_suica_m4_d_overspan_control_leg3 as leg3  # noqa: E402
import run_suica_m4_d_bias_anatomy_leg8 as leg8  # noqa: E402

from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
    _fit_hazard_candidate,
    _feedback_derivative,
    _hazard_design,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
)
from suica_core.m4_condition_manifold_estimator import (  # noqa: E402
    _candidate_features,
    _panel_prototypes,
    _robust_scale,
)

HIGH_GAP_WORLDS = (
    "endogenous_creation_expansion",
    "selection_creation_compensation",
    "source_rotated_feedback",
)
ARM_NAMES = ("v2", "A_debias", "A_debias_x10", "B_unsafe")
REGISTERED_ARMS = ("v2", "A_debias", "B_unsafe")  # A_x10 is secondary
ROLES = ("calibration", "selection", "evaluation")
ROW_TOLERANCE = 1e-9
IDENTITY_TOLERANCE = 1e-9
GRAM_RANK_TOLERANCE = 1e-8
B_SV_TOLERANCE = 1e-8
B_MAX_DIRECTIONS = 6  # oracle raw condition width
LEAN_A_CLOSURE_BAR = 0.5
LEAN_A_MIN_WORLDS = 2
LEAN_B_BAND = (0.10, 0.60)
LEAN_C_BAR = 0.6
NULL_RELATIVE_TOLERANCE = leg8.NULL_RELATIVE_TOLERANCE  # 1e-8
RANK_RELATIVE_TOLERANCE = leg8.RANK_RELATIVE_TOLERANCE  # 1e-10
CONDITIONING_GATE_COLUMNS = (
    "lambda_max",
    "lambda_min_raw",
    "lambda_min_effective",
    "condition_number_raw",
    "condition_number_effective",
    "near_null_count",
    "numerical_rank",
    "cr_sd_over_d_true",
    "jacobian_null_fraction",
)


# ---------------------------------------------------------------------------
# persisted references (refused if absent -- registered comparators)
# ---------------------------------------------------------------------------


def _load_leg9_swap_reference() -> pd.DataFrame:
    path = ROOT / "results" / "m4_d_bias_variance" / "gap_swap_rows.csv"
    if not path.exists():
        raise RuntimeError(
            f"Leg 9 persisted gap swap rows are a required anchor: {path}"
        )
    return pd.read_csv(path)


def _load_leg8_conditioning_reference() -> pd.DataFrame:
    path = ROOT / "results" / "m4_d_bias_anatomy" / "conditioning_rows.csv"
    if not path.exists():
        raise RuntimeError(
            f"Leg 8 persisted conditioning rows are a required anchor: {path}"
        )
    return pd.read_csv(path)


def _load_leg8_lam1n_reference() -> pd.DataFrame:
    path = ROOT / "results" / "m4_d_bias_anatomy" / "lever_rows.csv"
    if not path.exists():
        raise RuntimeError(
            f"Leg 8 persisted lever rows are a required anchor: {path}"
        )
    stored = pd.read_csv(path)
    return stored[
        (stored["panel"] == "natural")
        & (stored["arm"] == "A_lam1n")
        & (stored["budget"] == 1.0)
    ].copy()


def _load_leg8_decision() -> dict[str, Any]:
    path = ROOT / "results" / "m4_d_bias_anatomy" / "decision.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_leg9_decision() -> dict[str, Any]:
    path = ROOT / "results" / "m4_d_bias_variance" / "decision.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


# ---------------------------------------------------------------------------
# Arm A -- de-biased discovery: Tikhonov whitening at the freeze stage
# ---------------------------------------------------------------------------


def _freeze_ingredients(context: dict[str, Any]) -> dict[str, Any]:
    """Recompute the frozen transform's raw features / eigenstructure.

    Follows `freeze_m4_condition_transform` line by line on the candidate the
    frozen transform itself carries, so the lambda=0 rebuild can be gated
    bit-near-exactly against the persisted whitening.
    """
    transform = context["v2_transform"]
    candidate = transform._candidate
    condition = context["observed"].condition
    prototypes = _panel_prototypes(condition.reference_calibration)
    raw = np.mean(_candidate_features(candidate, prototypes), axis=0)
    center = np.mean(raw, axis=0)
    centered = raw - center
    covariance = centered.T @ centered / max(len(centered) - 1, 1)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    rank_tolerance = 1e-6  # config value used by every loop-leg context
    threshold = rank_tolerance * max(float(eigenvalues[0]), 1e-12)
    retained = np.flatnonzero(eigenvalues > threshold)
    maximum_rank = 12
    retained = retained[: max(int(maximum_rank), 1)]
    if len(retained) == 0:
        retained = np.asarray([0])
    n_reference_rows = int(raw.shape[0])
    p_features = int(covariance.shape[0])
    lambda_chart = (
        float(np.trace(covariance)) / p_features / n_reference_rows
    )
    return {
        "candidate": candidate,
        "center": center,
        "eigenvalues": eigenvalues,
        "eigenvectors": eigenvectors,
        "retained": retained,
        "n_reference_rows": n_reference_rows,
        "p_features": p_features,
        "lambda_chart": lambda_chart,
        "transform": transform,
    }


def _whitening_with_lambda(
    ingredients: dict[str, Any],
    lam: float,
) -> np.ndarray:
    eigenvalues = ingredients["eigenvalues"]
    eigenvectors = ingredients["eigenvectors"]
    retained = ingredients["retained"]
    return (
        eigenvectors[:, retained]
        / np.sqrt(np.maximum(eigenvalues[retained] + lam, 1e-12))[None]
    )


def _bases_from_whitening(
    context: dict[str, Any],
    ingredients: dict[str, Any],
    whitening: np.ndarray,
) -> dict[str, np.ndarray]:
    """transform_prototypes semantics with a supplied whitening matrix."""
    condition = context["observed"].condition
    candidate = ingredients["candidate"]
    center = ingredients["center"]
    bases: dict[str, np.ndarray] = {}
    for role in ROLES:
        values = np.asarray(
            getattr(condition, f"mechanism_{role}").pre_context, dtype=float
        )
        if values.ndim == 4:
            values = np.mean(values, axis=1)
        raw = np.mean(_candidate_features(candidate, values), axis=0)
        whitened = (raw - center) @ whitening
        bases[role] = np.column_stack([np.ones(len(raw)), whitened])
    return bases


def _debias_gate(
    context: dict[str, Any],
    ingredients: dict[str, Any],
) -> dict[str, float]:
    """Gate 2: lambda=0 rebuild must reproduce the frozen V2 transform."""
    transform = ingredients["transform"]
    whitening0 = _whitening_with_lambda(ingredients, 0.0)
    whitening_gap = float(
        np.max(np.abs(whitening0 - transform.whitening_matrix))
    )
    center_gap = float(
        np.max(np.abs(ingredients["center"] - transform.whitening_center))
    )
    bases0 = _bases_from_whitening(context, ingredients, whitening0)
    basis_gap = max(
        float(np.max(np.abs(bases0[role] - context["v2_basis"][role])))
        for role in ROLES
    )
    if max(whitening_gap, center_gap, basis_gap) > IDENTITY_TOLERANCE:
        raise RuntimeError(
            "de-biased-whitening rebuild fails the lambda=0 identity gate on "
            f"{context['world']} rep {context['repetition']}: whitening "
            f"{whitening_gap:.3e} center {center_gap:.3e} basis "
            f"{basis_gap:.3e}"
        )
    return {
        "whitening_gap": whitening_gap,
        "center_gap": center_gap,
        "basis_gap": basis_gap,
    }


# ---------------------------------------------------------------------------
# Arm B -- response-informed chart (DIAGNOSTIC ONLY, operationally forbidden)
# ---------------------------------------------------------------------------


def _response_informed_bases(
    context: dict[str, Any],
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    condition = context["observed"].condition
    panel = condition.reference_calibration
    prototypes = _panel_prototypes(panel)  # (sources, points, features)
    sources = prototypes.shape[0]
    standardized = []
    centers = []
    scales = []
    for source in range(sources):
        values, center, scale = _robust_scale(prototypes[source])
        standardized.append(values)
        centers.append(center)
        scales.append(scale)
    fused = np.mean(np.stack(standardized), axis=0)  # (points, features)
    response = np.asarray(panel.response, dtype=float)  # (authors, pts, dims)
    centered = response - response.mean(axis=1, keepdims=True)
    design = np.column_stack([np.ones(len(fused)), fused])
    coefficient_columns = []
    for author in range(response.shape[0]):
        coefficient, _, _, _ = np.linalg.lstsq(
            design, centered[author], rcond=None
        )
        coefficient_columns.append(coefficient[1:, :])  # intercept discarded
    stacked = np.concatenate(coefficient_columns, axis=1)  # (features, a*d)
    left, singular, _ = np.linalg.svd(stacked, full_matrices=False)
    keep = singular > B_SV_TOLERANCE * max(float(singular[0]), 1e-300)
    directions = left[:, keep][:, :B_MAX_DIRECTIONS]
    q = int(directions.shape[1])

    def _features_for(panel_values: np.ndarray) -> np.ndarray:
        values = np.asarray(panel_values, dtype=float)
        if values.ndim == 4:
            values = np.mean(values, axis=1)
        per_source = []
        for source in range(sources):
            standardized_source, _, _ = _robust_scale(
                values[source], center=centers[source], scale=scales[source]
            )
            per_source.append(standardized_source)
        return np.mean(np.stack(per_source), axis=0) @ directions

    reference_features = _features_for(panel.pre_context)
    center_b = np.mean(reference_features, axis=0)
    centered_b = reference_features - center_b
    covariance = centered_b.T @ centered_b / max(len(centered_b) - 1, 1)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    threshold = 1e-6 * max(float(eigenvalues[0]), 1e-12)
    retained = np.flatnonzero(eigenvalues > threshold)[:12]
    if len(retained) == 0:
        retained = np.asarray([0])
    whitening = (
        eigenvectors[:, retained]
        / np.sqrt(np.maximum(eigenvalues[retained], 1e-12))[None]
    )
    bases: dict[str, np.ndarray] = {}
    for role in ROLES:
        features = _features_for(
            getattr(condition, f"mechanism_{role}").pre_context
        )
        bases[role] = np.column_stack(
            [np.ones(len(features)), (features - center_b) @ whitening]
        )
    metadata = {
        "supervised_rank_q": q,
        "retained_after_whitening": int(len(retained)),
        "singular_values_top6": [
            float(value) for value in singular[:6]
        ],
        "width": int(bases["calibration"].shape[1]),
    }
    return bases, metadata


# ---------------------------------------------------------------------------
# direction alignment (cosine-gram rows) + subspace affinity
# ---------------------------------------------------------------------------


def _cosine_gram(basis: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(basis, axis=1)
    safe = np.where(norms > 1e-12, norms, 1.0)
    unit = basis / safe[:, None]
    return unit @ unit.T


def _profile_alignment(
    gram_first: np.ndarray,
    gram_second: np.ndarray,
    category: int,
) -> float:
    mask = np.ones(len(gram_first), dtype=bool)
    mask[category] = False
    first = gram_first[category][mask]
    second = gram_second[category][mask]
    denominator = np.linalg.norm(first) * np.linalg.norm(second)
    if denominator <= 1e-300:
        return float("nan")
    return float(np.dot(first, second) / denominator)


def _subspace_affinity(
    gram_disc: np.ndarray,
    gram_orc: np.ndarray,
) -> tuple[float, int]:
    """Mean cos^2 principal angles between top-q cosine-kernel eigenspaces."""
    eig_orc, vec_orc = np.linalg.eigh(gram_orc)
    order = np.argsort(eig_orc)[::-1]
    eig_orc = eig_orc[order]
    vec_orc = vec_orc[:, order]
    q = int(
        np.sum(eig_orc > GRAM_RANK_TOLERANCE * max(float(eig_orc[0]), 1e-300))
    )
    q = max(q, 1)
    eig_disc, vec_disc = np.linalg.eigh(gram_disc)
    order_disc = np.argsort(eig_disc)[::-1]
    vec_disc = vec_disc[:, order_disc]
    overlap = vec_orc[:, :q].T @ vec_disc[:, :q]
    singular = np.linalg.svd(overlap, compute_uv=False)
    return float(np.mean(singular**2)), q


def _alignment_rows_for_arm(
    keys: dict[str, Any],
    arm: str,
    basis: dict[str, np.ndarray],
    oracle_basis: dict[str, np.ndarray],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    alignment_rows = []
    subspace_rows = []
    diagnostic_only = arm == "B_unsafe"
    for role in ROLES:
        disc = basis[role]
        orc = oracle_basis[role]
        gram_disc = _cosine_gram(disc)
        gram_orc = _cosine_gram(orc)
        gram_disc_nc = _cosine_gram(disc[:, 1:])
        gram_orc_nc = _cosine_gram(orc[:, 1:])
        affinity, q = _subspace_affinity(gram_disc, gram_orc)
        subspace_rows.append(
            {
                **keys,
                "arm": arm,
                "diagnostic_only": diagnostic_only,
                "role": role,
                "subspace_affinity": affinity,
                "oracle_kernel_rank": q,
                "width": int(disc.shape[1]),
            }
        )
        for category in range(len(disc)):
            align_full = _profile_alignment(gram_disc, gram_orc, category)
            align_nc = _profile_alignment(
                gram_disc_nc, gram_orc_nc, category
            )
            alignment_rows.append(
                {
                    **keys,
                    "arm": arm,
                    "diagnostic_only": diagnostic_only,
                    "role": role,
                    "category": category,
                    "align_fullrow": align_full,
                    "deficit_fullrow": 1.0 - align_full,
                    "align_nonconst": align_nc,
                    "row_norm_arm": float(
                        np.linalg.norm(disc[category])
                    ),
                    "row_norm_oracle": float(
                        np.linalg.norm(orc[category])
                    ),
                }
            )
    return alignment_rows, subspace_rows


# ---------------------------------------------------------------------------
# per-category conditioning (Arm C)
# ---------------------------------------------------------------------------


def _category_pattern_vectors(
    names: tuple[str, ...],
    basis_cal_row: np.ndarray,
    basis_sel_row: np.ndarray,
    dimensions: int,
) -> np.ndarray:
    """Span of category k's calibration/selection design patterns."""
    p = len(names)
    width = len(basis_cal_row)
    vectors = []
    for row in (basis_cal_row, basis_sel_row):
        fixed = np.zeros(p)
        fixed[0] = 1.0
        fixed[1 : 1 + width] = row
        vectors.append(fixed)
    name_index = {name: i for i, name in enumerate(names)}
    for extra in ("generated_current", "duration"):
        if extra in name_index:
            unit = np.zeros(p)
            unit[name_index[extra]] = 1.0
            vectors.append(unit)
    for block in ("feedback", "gate"):
        if f"{block}_0_0" not in name_index:
            continue
        for dimension in range(dimensions):
            for row in (basis_cal_row, basis_sel_row):
                pattern = np.zeros(p)
                for condition in range(width):
                    pattern[
                        name_index[f"{block}_{condition}_{dimension}"]
                    ] = row[condition]
                vectors.append(pattern)
    return np.stack(vectors)


def _restricted_conditioning(
    information: np.ndarray,
    span_vectors: np.ndarray,
    full_lambda_max: float,
) -> dict[str, float]:
    q_matrix, r_matrix = np.linalg.qr(span_vectors.T)
    keep = np.abs(np.diag(r_matrix)) > 1e-10 * max(
        float(np.max(np.abs(np.diag(r_matrix)))), 1e-300
    )
    q_matrix = q_matrix[:, keep]
    if q_matrix.shape[1] == 0:
        return {
            "lambda_max": float("nan"),
            "lambda_min_effective": float("nan"),
            "condition_number_effective": float("nan"),
            "numerical_rank": 0,
            "subspace_dimension": 0,
        }
    restricted = q_matrix.T @ information @ q_matrix
    eigenvalues = np.linalg.eigvalsh(restricted)
    lam_max = float(eigenvalues[-1])
    near_null = eigenvalues < NULL_RELATIVE_TOLERANCE * full_lambda_max
    positive = eigenvalues[~near_null]
    effective_min = float(positive[0]) if len(positive) else float("nan")
    return {
        "lambda_max": lam_max,
        "lambda_min_effective": effective_min,
        "condition_number_effective": float(
            lam_max / max(effective_min, 1e-300)
        )
        if np.isfinite(effective_min)
        else float("inf"),
        "numerical_rank": int(
            np.sum(eigenvalues > RANK_RELATIVE_TOLERANCE * full_lambda_max)
        ),
        "subspace_dimension": int(q_matrix.shape[1]),
    }


def _per_category_conditioning_rows(
    keys: dict[str, Any],
    calibration: dict[str, np.ndarray],
    selection: dict[str, np.ndarray],
    oracle_basis: dict[str, np.ndarray],
    final_hazard: tuple[np.ndarray, tuple[str, ...]],
    model: str,
    dimensions: int,
    d_true: np.ndarray,
) -> list[dict[str, Any]]:
    coefficient, names = final_hazard
    designs = [
        _hazard_design(
            calibration, oracle_basis["calibration"], model=model
        )[0],
        _hazard_design(selection, oracle_basis["selection"], model=model)[0],
    ]
    design = np.vstack(designs)
    n_rows = design.shape[0]
    probability = expit(np.clip(design @ coefficient, -20.0, 20.0))
    weight = probability * (1.0 - probability)
    information = (design.T @ (weight[:, None] * design)) / n_rows
    eigenvalues, eigenvectors = np.linalg.eigh(information)
    full_lambda_max = float(eigenvalues[-1])
    near_null = eigenvalues < NULL_RELATIVE_TOLERANCE * full_lambda_max
    null_vectors = eigenvectors[:, near_null]
    pseudo = np.linalg.pinv(information, rcond=1e-12)

    basis_eval = oracle_basis["evaluation"]
    categories = len(basis_eval)
    jacobian_blocks = []
    for dimension in range(dimensions):
        response_pos = np.zeros((1, dimensions))
        response_neg = np.zeros((1, dimensions))
        response_pos[0, dimension] = leg4.PROBE_EPSILON
        response_neg[0, dimension] = -leg4.PROBE_EPSILON
        design_pos, _ = _hazard_design(
            leg8._probe_rows(basis_eval, response_pos, np.zeros(1)),
            basis_eval,
            model=model,
        )
        design_neg, _ = _hazard_design(
            leg8._probe_rows(basis_eval, response_neg, np.zeros(1)),
            basis_eval,
            model=model,
        )
        prob_pos = expit(np.clip(design_pos @ coefficient, -20.0, 20.0))
        prob_neg = expit(np.clip(design_neg @ coefficient, -20.0, 20.0))
        weight_pos = (prob_pos * (1.0 - prob_pos))[:, None]
        weight_neg = (prob_neg * (1.0 - prob_neg))[:, None]
        jacobian_blocks.append(
            (weight_pos * design_pos - weight_neg * design_neg)
            / (2.0 * leg4.PROBE_EPSILON)
        )
    rows = []
    for category in range(categories):
        jacobian_k = np.stack(
            [block[category] for block in jacobian_blocks]
        )  # (dims, p)
        restricted = _restricted_conditioning(
            information, jacobian_k, full_lambda_max
        )
        pattern = _category_pattern_vectors(
            names,
            oracle_basis["calibration"][category],
            oracle_basis["selection"][category],
            dimensions,
        )
        restricted_pattern = _restricted_conditioning(
            information, pattern, full_lambda_max
        )
        variance_k = float(
            np.einsum("ip,pq,iq->", jacobian_k, pseudo, jacobian_k) / n_rows
        )
        variance_k = max(variance_k, 0.0)
        d_true_k = float(np.abs(d_true[category])) if d_true.ndim == 1 else (
            float(np.linalg.norm(d_true[category]))
        )
        jacobian_norm_sq = float(np.sum(jacobian_k**2))
        if null_vectors.shape[1]:
            null_fraction_k = float(
                np.sum((jacobian_k @ null_vectors) ** 2)
                / max(jacobian_norm_sq, 1e-300)
            )
        else:
            null_fraction_k = 0.0
        rows.append(
            {
                **keys,
                "category": category,
                "model": model,
                "cond_eff_jacobian": restricted[
                    "condition_number_effective"
                ],
                "lambda_max_jacobian": restricted["lambda_max"],
                "lambda_min_eff_jacobian": restricted[
                    "lambda_min_effective"
                ],
                "rank_jacobian": restricted["numerical_rank"],
                "dim_jacobian": restricted["subspace_dimension"],
                "cond_eff_pattern": restricted_pattern[
                    "condition_number_effective"
                ],
                "rank_pattern": restricted_pattern["numerical_rank"],
                "dim_pattern": restricted_pattern["subspace_dimension"],
                "cr_sd_over_d_true_k": float(
                    np.sqrt(variance_k / n_rows) / max(d_true_k, 1e-300)
                ),
                "jacobian_null_fraction_k": null_fraction_k,
                "d_true_k_norm": d_true_k,
            }
        )
    return rows


# ---------------------------------------------------------------------------
# per-world-rep pass
# ---------------------------------------------------------------------------


def _forced_v2_derivative(
    context: dict[str, Any],
    view: str,
    author: int,
    basis: dict[str, np.ndarray],
) -> np.ndarray:
    calibration, selection, _ = context["flat"][(view, author)]
    route = context["oracle_stacks"][view][author]["selected_model"]
    dimensions = context["flat"][("train", 0)][0]["response_next"].shape[1]
    return leg4._forced_route_derivative(
        calibration,
        selection,
        basis,
        model=route,
        hazard_ridge=context["fit_kwargs"]["hazard_ridge"],
        logistic_iterations=context["fit_kwargs"]["logistic_iterations"],
        dimensions=dimensions,
    )


def _lam1n_derivative(
    context: dict[str, Any],
    view: str,
    author: int,
    basis: dict[str, np.ndarray],
) -> np.ndarray:
    calibration, selection, _ = context["flat"][(view, author)]
    route = context["oracle_stacks"][view][author]["selected_model"]
    dimensions = context["flat"][("train", 0)][0]["response_next"].shape[1]
    coefficient, names, family, _ = leg8._lever_fit(
        calibration,
        selection,
        basis,
        model=route,
        arm="A_lam1n",
        hazard_ridge=context["fit_kwargs"]["hazard_ridge"],
        iterations=context["fit_kwargs"]["logistic_iterations"],
    )
    if family != "base":
        raise RuntimeError(
            f"lam1n lever resolved to family {family}; base only"
        )
    return _feedback_derivative(
        coefficient, names, basis["evaluation"], dimensions
    )


def _world_rep_pass(
    context: dict[str, Any],
    stored_leg9_swaps: pd.DataFrame,
    stored_leg8_conditioning: pd.DataFrame,
    stored_leg8_lam1n: pd.DataFrame,
) -> dict[str, Any]:
    world = context["world"]
    repetition = context["repetition"]
    seed = context["seed"]
    truth = context["truth"]
    oracle_basis = truth.oracle_basis
    dimensions = context["flat"][("train", 0)][0]["response_next"].shape[1]

    unit_gap = leg4._true_derivative_unit_check(truth, dimensions)
    if unit_gap > 1e-10:
        raise RuntimeError(
            f"analytic D_true fails the probe unit check on {world} rep "
            f"{repetition}: {unit_gap:.3e}"
        )
    true_d = {
        author: leg4._true_derivative(truth, author)
        for author in range(context["authors"])
    }

    # ---- arm bases -------------------------------------------------------
    ingredients = _freeze_ingredients(context)
    debias_gate = _debias_gate(context, ingredients)
    lambda_chart = ingredients["lambda_chart"]
    bases_by_arm: dict[str, dict[str, np.ndarray]] = {
        "v2": context["v2_basis"],
        "A_debias": _bases_from_whitening(
            context,
            ingredients,
            _whitening_with_lambda(ingredients, lambda_chart),
        ),
        "A_debias_x10": _bases_from_whitening(
            context,
            ingredients,
            _whitening_with_lambda(ingredients, 10.0 * lambda_chart),
        ),
    }
    bases_by_arm["B_unsafe"], b_metadata = _response_informed_bases(context)

    keys_base = {"world": world, "repetition": repetition, "seed": seed}

    alignment_rows: list[dict[str, Any]] = []
    subspace_rows: list[dict[str, Any]] = []
    for arm in ARM_NAMES:
        arm_alignment, arm_subspace = _alignment_rows_for_arm(
            keys_base, arm, bases_by_arm[arm], oracle_basis
        )
        alignment_rows.extend(arm_alignment)
        subspace_rows.extend(arm_subspace)

    # ---- gap rows (forced-route V2 semantics; Leg 9 anchor) --------------
    row_index = [
        (view, author)
        for view in ("train", "test")
        for author in range(context["authors"])
    ]
    degenerate: dict[tuple[str, int], bool] = {}
    for view, author in row_index:
        stack = context["oracle_stacks"][view][author]
        degenerate[(view, author)] = bool(
            float(np.linalg.norm(stack["D"])) < leg4.FLIP_TOLERANCE
        )
    gap_rows: list[dict[str, Any]] = []
    for view, author in row_index:
        stack = context["oracle_stacks"][view][author]
        keys = {
            **keys_base,
            "author": author,
            "view": view,
            "forced_route": stack["selected_model"],
        }
        if degenerate[(view, author)]:
            gap_rows.append(
                {
                    **keys,
                    "degenerate_reference": True,
                    **{
                        name: np.nan
                        for name in (
                            "e_orc_true",
                            "e_d_true_v2",
                            "e_A_true",
                            "e_A10_true",
                            "e_B_true",
                            "gap_v2",
                            "gap_A",
                            "gap_A10",
                            "gap_B",
                            "e_A_lam1n_true",
                            "e_orc_lam1n_true",
                            "gap_A_lam1nboth",
                        )
                    },
                }
            )
            continue
        d_true = true_d[author]
        e_orc = leg3._relative_error(stack["D"], d_true)
        d_v2 = _forced_v2_derivative(
            context, view, author, bases_by_arm["v2"]
        )
        e_v2 = leg3._relative_error(d_v2, d_true)
        d_a = _forced_v2_derivative(
            context, view, author, bases_by_arm["A_debias"]
        )
        e_a = leg3._relative_error(d_a, d_true)
        d_a10 = _forced_v2_derivative(
            context, view, author, bases_by_arm["A_debias_x10"]
        )
        e_a10 = leg3._relative_error(d_a10, d_true)
        d_b = _forced_v2_derivative(
            context, view, author, bases_by_arm["B_unsafe"]
        )
        e_b = leg3._relative_error(d_b, d_true)
        # unregistered-secondary: lam1n on BOTH sides at the A chart
        d_a_lam1n = _lam1n_derivative(
            context, view, author, bases_by_arm["A_debias"]
        )
        d_orc_lam1n = _lam1n_derivative(context, view, author, oracle_basis)
        e_a_lam1n = leg3._relative_error(d_a_lam1n, d_true)
        e_orc_lam1n = leg3._relative_error(d_orc_lam1n, d_true)
        gap_rows.append(
            {
                **keys,
                "degenerate_reference": False,
                "e_orc_true": e_orc,
                "e_d_true_v2": e_v2,
                "e_A_true": e_a,
                "e_A10_true": e_a10,
                "e_B_true": e_b,
                "gap_v2": e_v2 - e_orc,
                "gap_A": e_a - e_orc,
                "gap_A10": e_a10 - e_orc,
                "gap_B": e_b - e_orc,
                "e_A_lam1n_true": e_a_lam1n,
                "e_orc_lam1n_true": e_orc_lam1n,
                "gap_A_lam1nboth": e_a_lam1n - e_orc_lam1n,
            }
        )

    # ---- gate 3: V2 gap columns vs Leg 9 persisted swap rows -------------
    mine = pd.DataFrame(gap_rows)
    reference = stored_leg9_swaps[
        (stored_leg9_swaps["world"] == world)
        & (stored_leg9_swaps["repetition"] == repetition)
    ]
    merge_keys = ["world", "repetition", "author", "view"]
    merged = reference.merge(
        mine, on=merge_keys, suffixes=("_leg9", "_leg10")
    )
    if len(merged) != len(mine) or len(merged) != len(reference):
        raise RuntimeError(
            f"gap rows misaligned with Leg 9 on {world} rep {repetition}: "
            f"{len(merged)} matches vs mine {len(mine)} / stored "
            f"{len(reference)}"
        )
    flags_equal = bool(
        (
            merged["degenerate_reference_leg9"]
            == merged["degenerate_reference_leg10"]
        ).all()
    )
    usable = merged[~merged["degenerate_reference_leg9"]]
    swap_gate_max = float(
        np.max(
            np.abs(
                np.concatenate(
                    [
                        usable["e_d_true_v2_leg9"].to_numpy()
                        - usable["e_d_true_v2_leg10"].to_numpy(),
                        usable["e_orc_true_leg9"].to_numpy()
                        - usable["e_orc_true_leg10"].to_numpy(),
                        usable["gap_v2_leg9"].to_numpy()
                        - usable["gap_v2_leg10"].to_numpy(),
                    ]
                )
            )
        )
    )
    if swap_gate_max > ROW_TOLERANCE or not flags_equal:
        raise RuntimeError(
            f"V2 gap replay diverges from Leg 9 persisted rows on {world} "
            f"rep {repetition}: max|diff|={swap_gate_max:.3e} "
            f"flags_equal={flags_equal}"
        )

    # ---- gate 5: lam1n oracle side vs Leg 8 persisted lever rows ---------
    lam1n_reference = stored_leg8_lam1n[
        (stored_leg8_lam1n["world"] == world)
        & (stored_leg8_lam1n["repetition"] == repetition)
    ]
    lam1n_merged = lam1n_reference.merge(
        mine, on=merge_keys, suffixes=("_leg8", "_leg10")
    )
    if len(lam1n_merged) != len(mine):
        raise RuntimeError(
            f"lam1n lever rows misaligned with Leg 8 on {world} rep "
            f"{repetition}"
        )
    lam1n_usable = lam1n_merged[~lam1n_merged["degenerate_reference_leg8"]]
    lam1n_gate_max = float(
        np.max(
            np.abs(
                lam1n_usable["e_orc_true_leg8"].to_numpy()
                - lam1n_usable["e_orc_lam1n_true"].to_numpy()
            )
        )
    )
    if lam1n_gate_max > ROW_TOLERANCE:
        raise RuntimeError(
            f"lam1n oracle replay diverges from Leg 8 lever rows on {world} "
            f"rep {repetition}: max|diff|={lam1n_gate_max:.3e}"
        )

    # ---- Arm C: aggregate gate (Leg 8 replica) + per-category rows -------
    conditioning_gate_rows: list[dict[str, Any]] = []
    per_category_rows: list[dict[str, Any]] = []
    reference_conditioning = stored_leg8_conditioning[
        (stored_leg8_conditioning["world"] == world)
        & (stored_leg8_conditioning["repetition"] == repetition)
    ]
    conditioning_gate_max = 0.0
    for view, author in row_index:
        keys = {
            **keys_base,
            "author": author,
            "view": view,
        }
        stored_row = reference_conditioning[
            (reference_conditioning["author"] == author)
            & (reference_conditioning["view"] == view)
        ]
        if len(stored_row) != 1:
            raise RuntimeError(
                f"Leg 8 conditioning reference missing for {world} rep "
                f"{repetition} {view} author {author}"
            )
        stored_row = stored_row.iloc[0]
        if degenerate[(view, author)]:
            if not bool(stored_row["degenerate_reference"]):
                raise RuntimeError(
                    "degenerate flag mismatch vs Leg 8 conditioning on "
                    f"{world} rep {repetition} {view} author {author}"
                )
            per_category_rows.extend(
                {
                    **keys,
                    "degenerate_reference": True,
                    "category": category,
                    "model": context["oracle_stacks"][view][author][
                        "selected_model"
                    ],
                    **{
                        name: np.nan
                        for name in (
                            "cond_eff_jacobian",
                            "lambda_max_jacobian",
                            "lambda_min_eff_jacobian",
                            "rank_jacobian",
                            "dim_jacobian",
                            "cond_eff_pattern",
                            "rank_pattern",
                            "dim_pattern",
                            "cr_sd_over_d_true_k",
                            "jacobian_null_fraction_k",
                            "d_true_k_norm",
                        )
                    },
                }
                for category in range(oracle_basis["evaluation"].shape[0])
            )
            continue
        calibration, selection, _ = context["flat"][(view, author)]
        stack = context["oracle_stacks"][view][author]
        replica = leg8._conditioning_row(
            keys,
            calibration,
            selection,
            oracle_basis,
            stack["final_hazard"],
            stack["selected_model"],
            dimensions,
            true_d[author],
        )
        for column in CONDITIONING_GATE_COLUMNS:
            stored_value = float(stored_row[column])
            recomputed = float(replica[column])
            scale = max(abs(stored_value), 1.0)
            gap = abs(recomputed - stored_value) / scale
            conditioning_gate_max = max(conditioning_gate_max, gap)
            if gap > ROW_TOLERANCE:
                raise RuntimeError(
                    "conditioning replica diverges from Leg 8 persisted "
                    f"rows on {world} rep {repetition} {view} author "
                    f"{author} column {column}: stored {stored_value!r} "
                    f"recomputed {recomputed!r}"
                )
        conditioning_gate_rows.append(
            {
                **keys,
                "model": replica["model"],
                "max_relative_gap_all_columns": conditioning_gate_max,
            }
        )
        category_rows = _per_category_conditioning_rows(
            keys,
            calibration,
            selection,
            oracle_basis,
            stack["final_hazard"],
            stack["selected_model"],
            dimensions,
            true_d[author],
        )
        for row in category_rows:
            row["degenerate_reference"] = False
        per_category_rows.extend(category_rows)

    gates = {
        "world": world,
        "repetition": repetition,
        "true_d_unit_check_max_gap": unit_gap,
        "debias_lambda0_identity": debias_gate,
        "lambda_chart": lambda_chart,
        "retained_rank": int(len(ingredients["retained"])),
        "eig_max": float(ingredients["eigenvalues"][0]),
        "eig_min_retained": float(
            ingredients["eigenvalues"][ingredients["retained"][-1]]
        ),
        "swap_gate_max_abs_diff": swap_gate_max,
        "lam1n_gate_max_abs_diff": lam1n_gate_max,
        "conditioning_gate_max_rel_diff": conditioning_gate_max,
        "b_unsafe_metadata": b_metadata,
    }
    return {
        "alignment_rows": alignment_rows,
        "subspace_rows": subspace_rows,
        "gap_rows": gap_rows,
        "per_category_rows": per_category_rows,
        "conditioning_gate_rows": conditioning_gate_rows,
        "gates": gates,
    }


# ---------------------------------------------------------------------------
# chunk driver
# ---------------------------------------------------------------------------


def _world_tag(worlds: list[str]) -> str:
    if list(worlds) == list(HIGH_GAP_WORLDS):
        return ""
    indices = "".join(
        str(list(HIGH_GAP_WORLDS).index(world)) for world in worlds
    )
    return f"_w{indices}"


def _run_chunk(
    args: argparse.Namespace,
    config: dict[str, Any],
    spec: M4ChartEcologySpec,
    repetitions: tuple[int, ...],
    worlds: list[str],
) -> None:
    stored_leg9_swaps = _load_leg9_swap_reference()
    stored_leg8_conditioning = _load_leg8_conditioning_reference()
    stored_leg8_lam1n = _load_leg8_lam1n_reference()
    world_index = {
        world: index for index, world in enumerate(config["worlds"])
    }
    expected_for = leg8._expected_geometries_lookup(config)

    collections: dict[str, list] = {
        name: []
        for name in (
            "alignment_rows",
            "subspace_rows",
            "gap_rows",
            "per_category_rows",
            "conditioning_gate_rows",
            "validation",
        )
    }
    gates: list[dict[str, Any]] = []
    for repetition in repetitions:
        for world in worlds:
            seed = leg3._world_seed(
                int(config["seed"]), repetition, world, world_index[world]
            )
            started = time.time()
            context = leg4._build_context(
                world,
                repetition,
                seed,
                spec=spec,
                config=config,
                expected_geometries=expected_for(world, repetition, seed),
            )
            collections["validation"].extend(context["validation_rows"])
            result = _world_rep_pass(
                context,
                stored_leg9_swaps,
                stored_leg8_conditioning,
                stored_leg8_lam1n,
            )
            for name in (
                "alignment_rows",
                "subspace_rows",
                "gap_rows",
                "per_category_rows",
                "conditioning_gate_rows",
            ):
                collections[name].extend(result[name])
            gates.append(result["gates"])

            frame = pd.DataFrame(
                [
                    row
                    for row in result["gap_rows"]
                    if not row["degenerate_reference"]
                ]
            )
            summary = {
                name: round(float(frame[name].median()), 4)
                for name in ("gap_v2", "gap_A", "gap_A10", "gap_B")
            }
            alignment = pd.DataFrame(result["alignment_rows"])
            deficits = {
                arm: round(
                    float(
                        alignment[alignment["arm"] == arm][
                            "deficit_fullrow"
                        ].mean()
                    ),
                    4,
                )
                for arm in ARM_NAMES
            }
            print(
                f"[leg10] rep={repetition} world={world} "
                f"lambda_chart={result['gates']['lambda_chart']:.3e} "
                f"gaps {summary} deficits {deficits} "
                f"({time.time() - started:.0f}s)",
                flush=True,
            )

    suffix = f"rep{repetitions[0]}-{repetitions[-1]}{_world_tag(worlds)}"
    args.output.mkdir(parents=True, exist_ok=True)
    stems = {
        "alignment_rows": "alignment_rows",
        "subspace_rows": "subspace_rows",
        "gap_rows": "gap_rows",
        "per_category_rows": "conditioning_per_category",
        "conditioning_gate_rows": "conditioning_gate",
        "validation": "v2_validation",
    }
    for name, stem in stems.items():
        pd.DataFrame(collections[name]).to_csv(
            args.output / f"partial_{stem}_{suffix}.csv", index=False
        )
    with (args.output / f"partial_gates_{suffix}.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(
            {
                "gates": gates,
                "repetitions": list(repetitions),
                "worlds": worlds,
            },
            handle,
            indent=2,
            sort_keys=True,
            default=str,
        )
        handle.write("\n")
    print(f"[chunk done] {suffix}", flush=True)


# ---------------------------------------------------------------------------
# assembly + adjudication
# ---------------------------------------------------------------------------


def _concat_partials(output: Path, stem: str) -> pd.DataFrame:
    paths = sorted(glob.glob(str(output / f"partial_{stem}_rep*.csv")))
    if not paths:
        raise RuntimeError(f"no partial CSVs found for {stem} under {output}")
    frames = []
    for path in paths:
        frame = pd.read_csv(path)
        if len(frame):
            frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def _refuse_bad_cells(
    frame: pd.DataFrame,
    keys: list[str],
    expected: int,
    label: str,
) -> None:
    duplicated = int(frame.duplicated(subset=keys).sum())
    if duplicated:
        raise RuntimeError(f"{label}: {duplicated} duplicate cells refused")
    if len(frame) != expected:
        raise RuntimeError(
            f"{label}: {len(frame)} rows != expected {expected}; missing "
            "cells refused"
        )


def _assemble(args: argparse.Namespace, config: dict[str, Any]) -> None:
    repetitions = int(config["repetitions"])
    authors = 16
    categories = 16
    worlds = list(HIGH_GAP_WORLDS)
    n_world_reps = len(worlds) * repetitions

    alignment = _concat_partials(args.output, "alignment_rows")
    subspace = _concat_partials(args.output, "subspace_rows")
    gap_rows = _concat_partials(args.output, "gap_rows")
    per_category = _concat_partials(args.output, "conditioning_per_category")
    conditioning_gate = _concat_partials(args.output, "conditioning_gate")
    validation = _concat_partials(args.output, "v2_validation")
    gate_payloads = []
    for path in sorted(
        glob.glob(str(args.output / "partial_gates_rep*.json"))
    ):
        with open(path, "r", encoding="utf-8") as handle:
            gate_payloads.append(json.load(handle))
    gates = [gate for chunk in gate_payloads for gate in chunk["gates"]]

    _refuse_bad_cells(
        alignment,
        ["world", "repetition", "arm", "role", "category"],
        n_world_reps * len(ARM_NAMES) * len(ROLES) * categories,
        "alignment rows",
    )
    _refuse_bad_cells(
        subspace,
        ["world", "repetition", "arm", "role"],
        n_world_reps * len(ARM_NAMES) * len(ROLES),
        "subspace rows",
    )
    _refuse_bad_cells(
        gap_rows,
        ["world", "repetition", "author", "view"],
        n_world_reps * 2 * authors,
        "gap rows",
    )
    _refuse_bad_cells(
        per_category,
        ["world", "repetition", "author", "view", "category"],
        n_world_reps * 2 * authors * categories,
        "per-category conditioning rows",
    )
    if len(gates) != n_world_reps:
        raise RuntimeError(
            f"gate payloads cover {len(gates)} world-reps != {n_world_reps}"
        )

    # ---- gap tables (Leg 9 semantics: view-mean per author, world median) -
    usable_gaps = gap_rows[~gap_rows["degenerate_reference"]].copy()
    gap_metrics = [
        "gap_v2",
        "gap_A",
        "gap_A10",
        "gap_B",
        "gap_A_lam1nboth",
        "e_orc_true",
        "e_d_true_v2",
        "e_A_true",
        "e_A10_true",
        "e_B_true",
    ]
    author_level = (
        usable_gaps.groupby(["world", "repetition", "author"])
        .agg(**{name: (name, "mean") for name in gap_metrics})
        .reset_index()
    )
    leg8_decision = _load_leg8_decision()
    leg9_decision = _load_leg9_decision()
    gap_table = []
    for world in worlds:
        scoped = author_level[author_level["world"] == world]
        row: dict[str, Any] = {
            "world": world,
            "n_author_reps": int(len(scoped)),
        }
        for name in gap_metrics:
            row[f"median_{name}"] = float(scoped[name].median())
        gap_v2 = row["median_gap_v2"]
        for arm_label, column in (
            ("A", "median_gap_A"),
            ("A10", "median_gap_A10"),
            ("B", "median_gap_B"),
            ("A_lam1nboth", "median_gap_A_lam1nboth"),
        ):
            row[f"closure_{arm_label}"] = (
                1.0 - row[column] / gap_v2 if gap_v2 > 0 else float("nan")
            )
        row["leg8_persisted_gap_v2"] = float(
            leg8_decision["alignment"]["per_world_gap_v2"][world]
        )
        gap_table.append(row)
    gap_frame = pd.DataFrame(gap_table)

    pooled_gap = {
        name: float(author_level[name].median()) for name in gap_metrics
    }
    pooled_closure_gap = {
        arm: 1.0 - pooled_gap[f"gap_{arm}"] / pooled_gap["gap_v2"]
        for arm in ("A", "A10", "B", "A_lam1nboth")
    }

    # ---- direction-deficit tables -----------------------------------------
    rep_deficit = (
        alignment.groupby(["world", "repetition", "arm"])["deficit_fullrow"]
        .mean()
        .reset_index()
    )
    world_deficit = (
        rep_deficit.groupby(["world", "arm"])["deficit_fullrow"]
        .mean()
        .reset_index()
        .pivot(index="world", columns="arm", values="deficit_fullrow")
    )
    deficit_closures = {}
    for arm in ("A_debias", "A_debias_x10", "B_unsafe"):
        deficit_closures[arm] = {
            world: float(
                1.0
                - world_deficit.loc[world, arm]
                / world_deficit.loc[world, "v2"]
            )
            for world in worlds
        }
    pooled_deficit = {
        arm: float(np.sum([world_deficit.loc[w, arm] for w in worlds]))
        for arm in ARM_NAMES
    }
    pooled_closure_dir = {
        arm: 1.0 - pooled_deficit[arm] / pooled_deficit["v2"]
        for arm in ("A_debias", "A_debias_x10", "B_unsafe")
    }

    per_category_deficit_v2 = (
        alignment[alignment["arm"] == "v2"]
        .groupby(["world", "repetition", "category"])["deficit_fullrow"]
        .mean()
        .reset_index()
        .groupby(["world", "category"])["deficit_fullrow"]
        .median()
        .reset_index()
        .rename(columns={"deficit_fullrow": "deficit_v2"})
    )

    # ---- Arm C correlation -------------------------------------------------
    usable_cond = per_category[~per_category["degenerate_reference"]].copy()
    usable_cond["log10_cond_eff_jacobian"] = np.log10(
        usable_cond["cond_eff_jacobian"].astype(float)
    )
    usable_cond["log10_cond_eff_pattern"] = np.log10(
        usable_cond["cond_eff_pattern"].astype(float)
    )
    cond_world_category = (
        usable_cond.groupby(["world", "category"])
        .agg(
            log10_cond_eff_jacobian=("log10_cond_eff_jacobian", "median"),
            log10_cond_eff_pattern=("log10_cond_eff_pattern", "median"),
            cr_sd_over_d_true_k=("cr_sd_over_d_true_k", "median"),
            jacobian_null_fraction_k=("jacobian_null_fraction_k", "median"),
        )
        .reset_index()
    )
    correlation_frame = per_category_deficit_v2.merge(
        cond_world_category, on=["world", "category"]
    )
    if len(correlation_frame) != len(worlds) * categories:
        raise RuntimeError(
            "conditioning-deficit merge lost cells: "
            f"{len(correlation_frame)} != {len(worlds) * categories}"
        )

    def _spearman(frame: pd.DataFrame, x: str) -> float:
        value = spearmanr(frame[x], frame["deficit_v2"]).statistic
        return float(value) if np.isfinite(value) else float("nan")

    spearman_pooled = _spearman(correlation_frame, "log10_cond_eff_jacobian")
    spearman_by_world = {
        world: _spearman(
            correlation_frame[correlation_frame["world"] == world],
            "log10_cond_eff_jacobian",
        )
        for world in worlds
    }
    spearman_companions = {
        "log10_cond_eff_pattern": _spearman(
            correlation_frame, "log10_cond_eff_pattern"
        ),
        "cr_sd_over_d_true_k": _spearman(
            correlation_frame, "cr_sd_over_d_true_k"
        ),
        "jacobian_null_fraction_k": _spearman(
            correlation_frame, "jacobian_null_fraction_k"
        ),
    }

    # ---- leans --------------------------------------------------------------
    closure_a_by_world = {
        row["world"]: float(row["closure_A"])
        for _, row in gap_frame.iterrows()
    }
    lean_a_worlds = [
        world
        for world in worlds
        if closure_a_by_world[world] >= LEAN_A_CLOSURE_BAR
    ]
    lean_a = {
        "statement": (
            "de-biased discovery closes >= half the paired gap in >= 2/3 "
            "high-gap worlds"
        ),
        "closure_A_by_world": closure_a_by_world,
        "worlds_at_or_above_half": lean_a_worlds,
        "held": len(lean_a_worlds) >= LEAN_A_MIN_WORLDS,
    }
    closure_dir_b = pooled_closure_dir["B_unsafe"]
    lean_b = {
        "statement": (
            "safety relaxation closes [10%, 60%] of the direction deficit "
            "(pooled); point-lean below half"
        ),
        "pooled_direction_deficit_closure_B": closure_dir_b,
        "band": list(LEAN_B_BAND),
        "held": bool(
            LEAN_B_BAND[0] <= closure_dir_b <= LEAN_B_BAND[1]
        ),
        "point_lean_below_half": bool(closure_dir_b < 0.5),
        "companion_gap_closure_B_pooled": pooled_closure_gap["B"],
        "diagnostic_only": True,
        "label": (
            "RESPONSE-SAFETY RELAXED -- DIAGNOSTIC ONLY, OPERATIONALLY "
            "FORBIDDEN"
        ),
    }
    lean_c = {
        "statement": (
            "per-category conditioning-deficit Spearman >= .6 pooled "
            "across the three worlds"
        ),
        "spearman_pooled_log10_cond_eff_jacobian": spearman_pooled,
        "spearman_by_world": spearman_by_world,
        "companions": spearman_companions,
        "held": bool(spearman_pooled >= LEAN_C_BAR),
    }
    leans_held = int(lean_a["held"]) + int(lean_b["held"]) + int(
        lean_c["held"]
    )

    a_attributes = lean_a["held"]
    b_attributes = bool(
        pooled_closure_gap["B"] >= 0.5 or closure_dir_b >= 0.5
    )
    c_attributes = lean_c["held"]
    pivot_fires = not (a_attributes or b_attributes or c_attributes)
    pivot = {
        "registered": (
            "none of A/B/C attributes >= half the gap -> "
            "DIRECTION_DEFICIT_SOURCE_UNIDENTIFIED; next instrument = "
            "perturbation analysis of the discovery objective (gradient of "
            "direction estimates w.r.t. panel composition) -- registered "
            "hand-off, NOT run here"
        ),
        "a_attributes_half": a_attributes,
        "b_attributes_half": b_attributes,
        "c_attributes_half_via_identification": c_attributes,
        "fires": pivot_fires,
        "verdict": (
            "DIRECTION_DEFICIT_SOURCE_UNIDENTIFIED"
            if pivot_fires
            else "DIRECTION_DEFICIT_SOURCE_ATTRIBUTED_AT_LEAST_PARTIALLY"
        ),
    }

    # ---- attribution ledger --------------------------------------------------
    attribution_ledger = []
    for world in worlds:
        row = gap_frame[gap_frame["world"] == world].iloc[0]
        attribution_ledger.append(
            {
                "world": world,
                "gap_v2": float(row["median_gap_v2"]),
                "gap_A_debias": float(row["median_gap_A"]),
                "closure_A_gap": float(row["closure_A"]),
                "gap_B_unsafe_DIAGNOSTIC_ONLY": float(row["median_gap_B"]),
                "closure_B_gap_DIAGNOSTIC_ONLY": float(row["closure_B"]),
                "deficit_v2": float(world_deficit.loc[world, "v2"]),
                "deficit_A_debias": float(
                    world_deficit.loc[world, "A_debias"]
                ),
                "closure_A_direction": deficit_closures["A_debias"][world],
                "deficit_B_unsafe_DIAGNOSTIC_ONLY": float(
                    world_deficit.loc[world, "B_unsafe"]
                ),
                "closure_B_direction_DIAGNOSTIC_ONLY": deficit_closures[
                    "B_unsafe"
                ][world],
                "unregistered_gap_A10": float(row["median_gap_A10"]),
                "unregistered_closure_A10_gap": float(row["closure_A10"]),
                "unregistered_gap_A_lam1nboth": float(
                    row["median_gap_A_lam1nboth"]
                ),
            }
        )

    faithfulness = {
        "v2_replay_rows": int(len(validation)),
        "v2_replay_max_abs_difference": float(
            validation["abs_difference"].max()
        )
        if len(validation)
        else None,
        "leg9_swap_gate_max_abs_diff": max(
            float(gate["swap_gate_max_abs_diff"]) for gate in gates
        ),
        "leg8_lam1n_gate_max_abs_diff": max(
            float(gate["lam1n_gate_max_abs_diff"]) for gate in gates
        ),
        "leg8_conditioning_gate_max_rel_diff": max(
            float(gate["conditioning_gate_max_rel_diff"]) for gate in gates
        ),
        "debias_lambda0_identity_max": max(
            max(
                float(value)
                for value in gate["debias_lambda0_identity"].values()
            )
            for gate in gates
        ),
        "true_d_unit_check_max": max(
            float(gate["true_d_unit_check_max_gap"]) for gate in gates
        ),
        "conditioning_gate_rows": int(len(conditioning_gate)),
    }

    chart_profile = {
        "lambda_chart_by_world_rep": {
            f"{gate['world']}/r{gate['repetition']}": float(
                gate["lambda_chart"]
            )
            for gate in gates
        },
        "retained_rank": sorted(
            {int(gate["retained_rank"]) for gate in gates}
        ),
        "b_unsafe_supervised_rank": sorted(
            {
                int(gate["b_unsafe_metadata"]["supervised_rank_q"])
                for gate in gates
            }
        ),
        "b_unsafe_width": sorted(
            {int(gate["b_unsafe_metadata"]["width"]) for gate in gates}
        ),
    }

    # ---- subspace summary ---------------------------------------------------
    subspace_summary = (
        subspace.groupby(["world", "arm"])["subspace_affinity"]
        .median()
        .reset_index()
        .pivot(index="world", columns="arm", values="subspace_affinity")
        .to_dict(orient="index")
    )

    decision = {
        "estimand_id": "SUICA_M4_D_DIRECTION_ANATOMY_LEG10",
        "tier": "EXPLORATORY (open-exploration phase)",
        "registered_in": (
            "docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md Leg 10 "
            "(2026-08-02, loop cycle 5, commit 3ed9f18, before run)"
        ),
        "design": {
            "worlds": worlds,
            "repetitions": repetitions,
            "arms": {
                "A_debias": (
                    "discovery-stage lambda~1/n: Tikhonov whitening "
                    "V/sqrt(eig + trace(cov)/p/n_ref) with V2's retained "
                    "eigenvector set; gap refits keep V2 estimator "
                    "semantics (shared conventions)"
                ),
                "B_unsafe": (
                    "RESPONSE-SAFETY RELAXED -- DIAGNOSTIC ONLY, "
                    "OPERATIONALLY FORBIDDEN: response-supervised "
                    "reference-panel reduction (per-author OLS coefficient "
                    "span, cap 6) + unchanged V2 freeze semantics"
                ),
                "C_conditioning": (
                    "information operator of the final V2 oracle-basis "
                    "hazard fit restricted to each category's estimand-"
                    "Jacobian subspace; near-null cut 1e-8 relative to the "
                    "full operator"
                ),
                "unregistered_secondary": [
                    "A_debias_x10 (lambda scale sensitivity)",
                    "gap_A_lam1nboth (lam1n both sides at the A chart)",
                ],
            },
            "alignment_statistic": (
                "cosine between off-diagonal cosine-gram rows (full rows), "
                "mean over roles; companions: non-constant columns, "
                "subspace principal-angle affinity"
            ),
            "gap_semantics": (
                "Leg 9: forced-route V2 refits at 1x r=0, gap = e_arm_true "
                "- e_orc_true, author-level view-mean, world median"
            ),
        },
        "faithfulness": faithfulness,
        "chart_profile": chart_profile,
        "gap_table": gap_table,
        "pooled_gap": pooled_gap,
        "pooled_closure_gap": pooled_closure_gap,
        "direction_deficit": {
            "world_level": {
                world: {
                    arm: float(world_deficit.loc[world, arm])
                    for arm in ARM_NAMES
                }
                for world in worlds
            },
            "closures_by_world": deficit_closures,
            "pooled_closure_direction": pooled_closure_dir,
        },
        "subspace_affinity_median": subspace_summary,
        "conditioning_correlation": {
            "spearman_pooled_log10_cond_eff_jacobian": spearman_pooled,
            "spearman_by_world": spearman_by_world,
            "companions": spearman_companions,
            "n_pairs": int(len(correlation_frame)),
        },
        "lean_a": lean_a,
        "lean_b": lean_b,
        "lean_c": lean_c,
        "leans_held": leans_held,
        "pivot_if": pivot,
        "attribution_ledger": attribution_ledger,
        "reference_leg9_gap_attribution": leg9_decision.get(
            "gap_attribution"
        ),
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only; truth-referenced "
            "diagnostic; V1/V2 NO-GO decisions stand; arm B violates the "
            "response-safe operational constraint and is diagnostic only, "
            "never a deployable estimator; no natural-text, personality, "
            "or clinical claim."
        ),
    }

    args.output.mkdir(parents=True, exist_ok=True)
    alignment.sort_values(
        ["world", "repetition", "arm", "role", "category"]
    ).to_csv(args.output / "alignment_rows.csv", index=False)
    subspace.sort_values(["world", "repetition", "arm", "role"]).to_csv(
        args.output / "subspace_rows.csv", index=False
    )
    gap_rows.sort_values(["world", "repetition", "author", "view"]).to_csv(
        args.output / "gap_rows.csv", index=False
    )
    per_category.sort_values(
        ["world", "repetition", "author", "view", "category"]
    ).to_csv(args.output / "conditioning_per_category.csv", index=False)
    conditioning_gate.to_csv(
        args.output / "conditioning_gate_check.csv", index=False
    )
    validation.to_csv(args.output / "v2_validation.csv", index=False)
    gap_frame.to_csv(args.output / "gap_world_table.csv", index=False)
    correlation_frame.to_csv(
        args.output / "conditioning_deficit_pairs.csv", index=False
    )
    pd.DataFrame(attribution_ledger).to_csv(
        args.output / "attribution_ledger.csv", index=False
    )
    with (args.output / "decision.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(decision, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    print(
        json.dumps(
            {
                "lean_a_held": lean_a["held"],
                "lean_b_held": lean_b["held"],
                "lean_c_held": lean_c["held"],
                "pivot_fires": pivot_fires,
                "closure_A_by_world": closure_a_by_world,
                "pooled_closure_dir": pooled_closure_dir,
                "spearman_pooled": spearman_pooled,
            },
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m4_chart_ecology.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results" / "m4_d_direction_anatomy",
    )
    parser.add_argument("--chunk-start", type=int, default=None)
    parser.add_argument("--chunk-stop", type=int, default=None)
    parser.add_argument(
        "--worlds",
        type=str,
        default=None,
        help="comma-separated subset of the three high-gap worlds",
    )
    parser.add_argument("--assemble", action="store_true")
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    spec = M4ChartEcologySpec(**config["base_spec"])

    if args.assemble:
        _assemble(args, config)
        return
    if args.chunk_start is None or args.chunk_stop is None:
        raise SystemExit(
            "either --assemble or both --chunk-start/--chunk-stop required"
        )
    worlds = (
        [w for w in args.worlds.split(",") if w]
        if args.worlds
        else list(HIGH_GAP_WORLDS)
    )
    for world in worlds:
        if world not in HIGH_GAP_WORLDS:
            raise SystemExit(f"not a registered high-gap world: {world}")
    repetitions = tuple(range(args.chunk_start, args.chunk_stop))
    _run_chunk(args, config, spec, repetitions, worlds)


if __name__ == "__main__":
    main()
