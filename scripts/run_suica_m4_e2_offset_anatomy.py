#!/usr/bin/env python3
"""M4-E2: anatomy of the rep-invariant common offset (Leg 14's final object).

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md,
"M4-E2 -- anatomy of the common offset", 2026-08-02 loop cycle 11, commit
dc97d59, BEFORE this run; ledger row M4-E2). Machinery is IMPORTED from the
validated legs -- Leg 4's context build + canonical forced-route refit, Leg 9's
row-norm swap, Leg 11's stacked-frame quotient machinery, Leg 14's multi-start
GPA Frechet mean and refit wrapper (bit-continuity with the object under
anatomy), Leg 10's arm-B response-supervision extraction (gated against its
own function output). No estimator internals are copied.

THE OBJECT. Leg 14's companion decomposition isolated a REP-INVARIANT COMMON
OFFSET between the discovered-frame cloud center and the oracle-anchor cloud
center (quotient distance 12.0/13.8 across the three high-gap worlds, ~3/4 of
the median per-rep displacement), unremovable by consensus averaging or
split-half agreement. THE QUESTION: which structure of the discovery
objective carries it?

THE OFFSET VECTOR (task 1; reuse + assert). Per world, rebuild Leg 14's
clouds exactly: v2 frames = stacked role bases S = [B_cal; B_sel; B_eval]
(48 x W), swap frames = Leg 9's row-norm swap (oracle directions + the rep's
own norms), consensus of each cloud = Leg 14's multi-start GPA chordal
Frechet mean (argmin objective over the 8 rep inits). The offset vector is
the aligned matrix difference

    Delta = A - align(B_pad -> A),   A = pad(v2 consensus, W),
                                     B_pad = pad(swap consensus, W),

so ||Delta||_F equals Leg 14's persisted `v2_consensus_to_swap_consensus`
(ASSERTED <= 1e-9 against decision.json, plus GPA objectives and the Leg 11
per-rep displacement anchors). Delta is the canonical representative of the
offset in the consensus gauge; every decomposition statistic below is
invariant (or equivariant) under a global right-O(W) change of that gauge.

REGISTERED SUBSPACES (task 2; constructions stated precisely -- the
registration delegates the operational definitions to this script and
requires them stated). All are realized in the 48 x W stacked-frame MATRIX
space (dim 48*W = 624). Pattern subspaces act on the CATEGORY-PATTERN space
R^48 (rows = 3 roles x 16 category slots) as left projectors P (x) full
column space -- left action commutes with the right gauge, so shares are
gauge-invariant. S3 additionally uses gauge-EQUIVARIANT matrix modes built
from the consensus representative itself (their span transforms with the
gauge, so projections of Delta are gauge-invariant numbers).

- S1 (response-safety projection's complement -- the directions the safety
  constraint removes; REGISTERED POINT-LEAN). Realization = the span of the
  RESPONSE-SUPERVISED feature patterns the safe chart is denied, via Leg
  10's arm-B construction VERBATIM (gated): per rep, per-author OLS of
  occasion-centered reference-calibration responses on source-fused
  robust-standardized pre-context prototypes, SVD of stacked coefficient
  columns -> top-q directions U_q (q = rank at 1e-8 relative, cap 6; q = 6
  in 24/24 world-reps per Leg 10); the rep's category patterns = the arm-B
  features of the three mechanism roles, Z_role @ U_q (16 x q per role,
  stacked 48 x q). World-level S1 = the common core of the 8 reps' pattern
  spans: pool the unit-normalized pattern columns of all reps (48 x sum q_r),
  SVD, retain the top d1 = median_r q_r left singular vectors (captured
  pooled-mass fraction RECORDED -- if the rep-level spans share no core this
  number is small and the report says so). Matrix-space dim = d1 * W.
  NOT chosen (stated): subtracting the safe chart's own representable span
  would make S1 depend on the discovered object itself (circular).
- S2 (span of supervision-target directions -- the supervised block). The
  supervision targets the safety discipline withholds are the RESPONSES.
  Per rep, per role: author-mean observed response of the role's condition
  panel (16 x 2), one 48-pattern per response dimension (2 per rep,
  UNCENTERED -- the raw targets as an estimator would see them, choice
  stated; the intercept/constant interaction with S3 is exactly what the
  ordering sensitivity discloses). World-level S2 = common core as in S1
  with d2 = 2. Matrix-space dim = d2 * W.
- S3 (normalization/scale modes -- directions moved by the estimator's
  normalization steps; operational construction from the code, stated).
  Three families, one per normalization step class in the freeze path:
  (n1) CENTERING/MASS modes: robust-scale median subtraction, whitening
       center subtraction, and the appended constant mass column all move
       every category row of a role equally -> span{1_role (x) R^W} for the
       three roles (39 matrix dims);
  (n2) PRINCIPAL COLUMN-SCALE modes: the whitening rescales retained
       directions by 1/sqrt(eig) (V2's unregularized inverse amplifies the
       weakest retained direction ~300x, Leg 10) -> first-order motion under
       re-scaling the consensus's principal column directions:
       {A v_i v_i^T, i = 1..W}, v_i = right singular vectors of A (13 dims;
       basis-canonical, hence gauge-equivariant -- raw column axes e_j would
       depend on the arbitrary GPA gauge and are NOT used);
  (n3) PER-ROLE SIZE modes: output_scale / row-norm-family global size per
       role block {P_role A} (3 dims; contains the global scale mode A).
  S3 = orthonormalized union (rank recorded, ~54). Within-S3 family split
  n1 -> n2 -> n3 reported as a companion.
- S4 = residual.

DECOMPOSITION (registered order): sequential orthogonal projection of Delta,
S1 -> S2 -> S3, shares = ||component||^2 / ||Delta||^2 (nested Pythagorean;
shares sum to 1 with S4). Ordering sensitivity DISCLOSED: reverse order
S3 -> S2 -> S1, plus standalone (non-sequential) shares as the overlap
diagnostic. Null reference per subspace: dim/624 (expected share of an
isotropic random matrix direction; all subspaces are low-dim so the 60% bar
is far above null). COMPANION (no adjudication weight): the right-side
column-space split -- Delta * Q_perp = A * Q_perp is the part of the offset
forced by the width mismatch (the discovered chart's 6 extra whitened
directions; swap width 7 vs consensus width 13), reported as
width_mismatch_share.

CROSS-WORLD DIRECTION STABILITY (task 3). Category slots are world- and
rep-specific draws, so slot-index correspondence across worlds is
structural-only; the registered statistic is computed as registered and its
nulls are disclosed: pairwise PROCRUSTES COSINE over the right gauge,
cos_P(D1, D2) = nuclear_norm(D1^T D2) / (||D1||_F ||D2||_F), for the three
world pairs, on (i) the raw offsets and (ii) their dominant sequential
components. NULLS: (a) within-role row-permutation null (200 draws; destroys
slot correspondence, preserves role-block structure -- high raw cosines that
survive this null are carried by slot-free structure such as the constant
patterns); (b) matched-shape random-matrix null (200 pairs).

DIAGNOSTIC REFIT (task 4; the one registered battery). Per world: the
dominant component = the registered-order sequential component with the
largest share among S1/S2/S3 (pre-coded tie-break: first of S1,S2,S3).
U_dom = component/||component||. Per rep: align the rep's discovered frame
to the consensus (Leg 14's GPA alignment), PROJECT OUT the single matrix
direction U_dom (F' = F_al - <F_al, U_dom> U_dom), slice back into roles,
refit D at the canonical forced route (V2 semantics, 1x r=0 panels, Leg 9
gap semantics), and measure paired-gap closure vs gap_v2. The frames are not
column-orthonormal by design, so the registered "re-orthonormalize" step is
realized as the applicable well-posedness checks: column rank unchanged
(REFUSED otherwise) + Leg 11's rotation gate on the modified frame
(refit at F' vs F' @ R_random, <= 1e-6). Companion: displacement
alpha_dom = d(swap_rep, F') / d(swap_rep, v2_rep).

GAP SEMANTICS (Leg 9's, unchanged): per author-view at the oracle-forced
route, gap_dom = e_dom_true - e_orc_true; author level = view mean; rep
level = median over authors; world/pooled level = median over pooled
author-level rows. gap_v2 and e_orc_true are READ from Leg 14's persisted
gap_rows.csv and my recomputed e_orc is ASSERTED against it (<= 1e-9,
degenerate flags equal) -- the same rows Leg 14 bit-anchored to Leg 9.

REGISTERED LEANS (adjudication statistics pre-coded here, BEFORE the run):
- (a) the offset concentrates >= 60% of squared norm in ONE subspace
  consistently across the 3 worlds: held iff there exists i in {S1,S2,S3}
  with registered-order share_i >= .60 in ALL 3 worlds (same i). The
  registered point-lean is i = S1; whether the point-lean specifically holds
  is recorded separately.
- (b) the concentrated/dominant direction is stable across worlds: held iff
  ALL 3 pairwise Procrustes cosines of the raw offset vectors are >= .70
  (dominant-component cosines reported alongside; permutation null
  disclosed).
- (c) removing the dominant component closes >= half the paired gap:
  held iff pooled closure = 1 - pooled_gap_dom / pooled_gap_v2 >= .50
  (pooled = median over all usable author-level rows of the 3 worlds).
PIVOT-IF (registered): the offset spreads -- share < .40 for EVERY subspace
in EVERY world (registered order) -> no single objective term is
responsible; the open problem stands exactly as Leg 14 registered it and the
loop moves outside the M4-D/E line. If neither the lean-(a) bar nor the
pivot clause fires, the honest in-between is recorded.

FAITHFULNESS GATES (refused, not warned):
1. context build asserts V2 replay geometries vs archived metrics.csv;
2. analytic D_true unit check (Leg 4) at 1e-10;
3. per rep, d(swap_rep, v2_rep) must match Leg 11's persisted
   procrustes_residual at <= 1e-9;
4. the rebuilt GPA consensuses must reproduce Leg 14's persisted
   v2_consensus_to_swap_consensus at <= 1e-9 AND the persisted GPA
   objectives (v2 + swap clouds) at <= 1e-9 -- the offset object is
   bit-continuous with Leg 14;
5. ||Delta||_F must equal the quotient distance at <= 1e-10
   (representative self-consistency);
6. my arm-B rebuild must equal Leg 10's `_response_informed_bases`
   output at <= 1e-12 per role (certifies the S1 extraction sits on Leg
   10's exact code path);
7. per author-view, my e_orc must match Leg 14's persisted e_orc_true at
   <= 1e-9 with equal degenerate flags (certifies the refit path);
8. rotation gate on every modified frame (<= 1e-6) + column-rank
   preservation;
9. share bookkeeping: sequential shares must sum to 1 at <= 1e-9.

Execution: one foreground run, all three worlds (~6 min; the only battery is
one refit arm). --worlds/--output permit debug subsets; adjudication and
decision.json REFUSE to finalize unless all three registered worlds are
present.
"""
from __future__ import annotations

import argparse
import json
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

import run_suica_m4_d_dleg_floor_leg4 as leg4  # noqa: E402  bit-exact reuse
import run_suica_m4_d_overspan_control_leg3 as leg3  # noqa: E402
import run_suica_m4_d_bias_anatomy_leg8 as leg8  # noqa: E402
import run_suica_m4_d_bias_variance_leg9 as leg9  # noqa: E402
import run_suica_m4_d_direction_anatomy_leg10 as leg10  # noqa: E402
import run_suica_m4_d_perturbation_leg11 as leg11  # noqa: E402
import run_suica_m4_d_displacement_leg14 as leg14  # noqa: E402

from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
)
from suica_core.m4_condition_manifold_estimator import (  # noqa: E402
    _panel_prototypes,
    _robust_scale,
)

HIGH_GAP_WORLDS = leg11.HIGH_GAP_WORLDS
ROLES = leg11.ROLES

OFFSET_ANCHOR_TOLERANCE = 1e-9  # Leg 14 persisted offset + GPA objectives
DISPLACEMENT_ANCHOR_TOLERANCE = 1e-9  # Leg 11 procrustes_residual anchor
ROW_ANCHOR_TOLERANCE = 1e-9  # Leg 14 persisted e_orc rows
ARM_B_GATE_TOLERANCE = 1e-12  # Leg 10 arm-B rebuild identity
SELF_CONSISTENCY_TOLERANCE = 1e-10  # ||Delta|| vs quotient distance
SHARE_SUM_TOLERANCE = 1e-9
ROT_GATE_TOLERANCE = 1e-6
UNIT_CHECK_TOLERANCE = 1e-10
SUBSPACE_RANK_TOLERANCE = 1e-10  # relative, orthonormalization rank cut
B_SV_TOLERANCE = leg10.B_SV_TOLERANCE  # 1e-8 (arm-B direction rank cut)
B_MAX_DIRECTIONS = leg10.B_MAX_DIRECTIONS  # 6

LEAN_A_SHARE_BAR = 0.60
LEAN_B_COSINE_BAR = 0.70
LEAN_C_CLOSURE_BAR = 0.50
PIVOT_SHARE_BAR = 0.40
SUBSPACE_NAMES = ("S1_safety_complement", "S2_supervision_span", "S3_norm_scale_modes")
NULL_DRAWS = 200
PERM_NULL_SEED_TAG = 1409
RANDOM_NULL_SEED_TAG = 1410
ROT_SEED_OFFSET = 2  # leg14 used seed / seed+1; this leg uses seed+2
EPS = 1e-300


# ---------------------------------------------------------------------------
# persisted references (refused if absent -- registered comparators)
# ---------------------------------------------------------------------------


def _load_leg14_decision() -> dict[str, Any]:
    path = ROOT / "results" / "m4_d_discovery_displacement" / "decision.json"
    if not path.exists():
        raise RuntimeError(
            f"Leg 14 persisted decision is a required anchor: {path}"
        )
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_leg14_gap_rows() -> pd.DataFrame:
    path = ROOT / "results" / "m4_d_discovery_displacement" / "gap_rows.csv"
    if not path.exists():
        raise RuntimeError(
            f"Leg 14 persisted gap rows are a required anchor: {path}"
        )
    return pd.read_csv(path)


def _leg14_world_gates(decision: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        gate["world"]: gate
        for gate in decision["faithfulness"]["per_world_gates"]
    }


# ---------------------------------------------------------------------------
# S1 machinery: Leg 10 arm-B extraction (verbatim lines), gated vs leg10
# ---------------------------------------------------------------------------


def _response_direction_machinery(context: dict[str, Any]) -> dict[str, Any]:
    """First half of leg10._response_informed_bases, verbatim, returning the
    intermediate objects (directions U_q, per-source robust centers/scales,
    the feature builder) that the leg10 function does not expose."""
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

    def features_for(panel_values: np.ndarray) -> np.ndarray:
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

    return {
        "directions": directions,
        "q": q,
        "singular": singular,
        "features_for": features_for,
        "condition": condition,
    }


def _arm_b_gate(context: dict[str, Any], machinery: dict[str, Any]) -> float:
    """Rebuild Leg 10's arm-B bases from the extracted machinery (second half
    of leg10._response_informed_bases, verbatim) and assert identity against
    the leg10 function called directly on the same context."""
    condition = machinery["condition"]
    features_for = machinery["features_for"]
    reference_features = features_for(
        condition.reference_calibration.pre_context
    )
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
    rebuilt: dict[str, np.ndarray] = {}
    for role in ROLES:
        features = features_for(
            getattr(condition, f"mechanism_{role}").pre_context
        )
        rebuilt[role] = np.column_stack(
            [np.ones(len(features)), (features - center_b) @ whitening]
        )
    reference_bases, metadata = leg10._response_informed_bases(context)
    gate = max(
        float(np.max(np.abs(rebuilt[role] - reference_bases[role])))
        for role in ROLES
    )
    if gate > ARM_B_GATE_TOLERANCE:
        raise RuntimeError(
            "arm-B rebuild diverges from leg10._response_informed_bases on "
            f"{context['world']} rep {context['repetition']}: {gate:.3e}"
        )
    if int(metadata["supervised_rank_q"]) != int(machinery["q"]):
        raise RuntimeError(
            "arm-B supervised rank mismatch vs leg10 metadata on "
            f"{context['world']} rep {context['repetition']}"
        )
    return gate


def _s1_patterns(context: dict[str, Any], machinery: dict[str, Any]) -> np.ndarray:
    """Stacked category patterns of the response-supervised features:
    [Z_cal; Z_sel; Z_eval] @ U_q, shape (48, q)."""
    features_for = machinery["features_for"]
    condition = machinery["condition"]
    blocks = [
        features_for(getattr(condition, f"mechanism_{role}").pre_context)
        for role in ROLES
    ]
    return np.vstack(blocks)


def _s2_patterns(context: dict[str, Any]) -> np.ndarray:
    """Stacked supervision-target patterns: author-mean observed responses of
    the three mechanism condition panels, shape (48, response_dims)."""
    condition = context["observed"].condition
    blocks = [
        np.mean(
            np.asarray(
                getattr(condition, f"mechanism_{role}").response, dtype=float
            ),
            axis=0,
        )
        for role in ROLES
    ]
    return np.vstack(blocks)


def _common_core(
    per_rep_patterns: list[np.ndarray],
    *,
    retained_dim: int,
) -> tuple[np.ndarray, float, int]:
    """Unit-normalize pattern columns, pool over reps, SVD; return the top-d
    left singular vectors, the captured pooled squared-mass fraction, and the
    effective retained dimension (min(d, numerical rank))."""
    columns = []
    for patterns in per_rep_patterns:
        for column in np.asarray(patterns, dtype=float).T:
            norm = float(np.linalg.norm(column))
            if norm > 1e-12:
                columns.append(column / norm)
    pooled = np.column_stack(columns)
    left, singular, _ = np.linalg.svd(pooled, full_matrices=False)
    rank = int(
        np.sum(singular > SUBSPACE_RANK_TOLERANCE * max(float(singular[0]), EPS))
    )
    d = int(min(retained_dim, rank))
    captured = float(
        np.sum(singular[:d] ** 2) / max(np.sum(singular**2), EPS)
    )
    return left[:, :d], captured, d


# ---------------------------------------------------------------------------
# matrix-space subspaces and sequential projection
# ---------------------------------------------------------------------------


def _orthonormal_matrix_basis(mats: list[np.ndarray]) -> np.ndarray:
    """Orthonormal basis (columns, vectorized) of the span of the given
    48 x W matrices, rank-cut at SUBSPACE_RANK_TOLERANCE relative."""
    stacked = np.column_stack([mat.reshape(-1) for mat in mats])
    left, singular, _ = np.linalg.svd(stacked, full_matrices=False)
    rank = int(
        np.sum(singular > SUBSPACE_RANK_TOLERANCE * max(float(singular[0]), EPS))
    )
    return left[:, :rank]


def _pattern_basis_to_matrix_basis(
    patterns: np.ndarray, width: int
) -> np.ndarray:
    """Orthonormal pattern columns (48 x d) -> orthonormal matrix basis of
    span{pattern (x) e_w} (624 x d*width)."""
    total = patterns.shape[0] * width
    columns = []
    for pattern in patterns.T:
        for w in range(width):
            mat = np.zeros((patterns.shape[0], width))
            mat[:, w] = pattern
            columns.append(mat.reshape(-1))
    basis = np.column_stack(columns)
    if basis.shape[0] != total:
        raise RuntimeError("pattern basis vectorization shape error")
    return basis


def _project(vec: np.ndarray, basis: np.ndarray) -> np.ndarray:
    if basis.shape[1] == 0:
        return np.zeros_like(vec)
    return basis @ (basis.T @ vec)


def _sequential_shares(
    delta: np.ndarray,
    bases: dict[str, np.ndarray],
    order: tuple[str, ...],
) -> dict[str, Any]:
    vec = delta.reshape(-1)
    total = float(vec @ vec)
    remaining = vec.copy()
    shares: dict[str, float] = {}
    components: dict[str, np.ndarray] = {}
    for name in order:
        component = _project(remaining, bases[name])
        shares[name] = float(component @ component) / max(total, EPS)
        components[name] = component.reshape(delta.shape)
        remaining = remaining - component
    shares["S4_residual"] = float(remaining @ remaining) / max(total, EPS)
    components["S4_residual"] = remaining.reshape(delta.shape)
    checksum = float(sum(shares.values()))
    if abs(checksum - 1.0) > SHARE_SUM_TOLERANCE:
        raise RuntimeError(
            f"sequential shares do not sum to 1: {checksum:.12f}"
        )
    return {"shares": shares, "components": components, "order": order}


def _procrustes_cosine(first: np.ndarray, second: np.ndarray) -> float:
    """max_{R in O(W)} <first, second R>_F / (||first|| ||second||)
    = nuclear norm of first^T second over the norm product."""
    denominator = float(
        np.linalg.norm(first) * np.linalg.norm(second)
    )
    if denominator <= 1e-300:
        return float("nan")
    singular = np.linalg.svd(first.T @ second, compute_uv=False)
    return float(np.sum(singular) / denominator)


def _within_role_permutation(
    mat: np.ndarray, rng: np.random.Generator
) -> np.ndarray:
    categories = mat.shape[0] // len(ROLES)
    out = mat.copy()
    for index in range(len(ROLES)):
        block = slice(index * categories, (index + 1) * categories)
        out[block] = mat[block][rng.permutation(categories)]
    return out


# ---------------------------------------------------------------------------
# per-world pass
# ---------------------------------------------------------------------------


def _world_pass(
    world: str,
    config: dict[str, Any],
    spec: M4ChartEcologySpec,
    displacement_anchors: dict[tuple[str, int], float],
    leg14_gates: dict[str, dict[str, Any]],
    leg14_companions: dict[str, dict[str, Any]],
    leg14_rows: pd.DataFrame,
) -> dict[str, Any]:
    repetitions = int(config["repetitions"])
    world_index = {
        name: index for index, name in enumerate(config["worlds"])
    }[world]
    expected_for = leg8._expected_geometries_lookup(config)

    contexts: list[dict[str, Any]] = []
    for repetition in range(repetitions):
        seed = leg3._world_seed(
            int(config["seed"]), repetition, world, world_index
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
        unit_gap = leg4._true_derivative_unit_check(
            context["truth"],
            context["flat"][("train", 0)][0]["response_next"].shape[1],
        )
        if unit_gap > UNIT_CHECK_TOLERANCE:
            raise RuntimeError(
                f"analytic D_true fails the unit check on {world} rep "
                f"{repetition}: {unit_gap:.3e}"
            )
        context["unit_gap"] = unit_gap
        contexts.append(context)
        print(
            f"[m4e2] context {world} rep={repetition} "
            f"({time.time() - started:.1f}s)",
            flush=True,
        )

    # ---- frames + Leg 11 displacement anchors (gate 3) ----------------------
    v2_frames: list[np.ndarray] = []
    swap_frames: list[np.ndarray] = []
    disp_v2: list[float] = []
    disp_anchor_max = 0.0
    for context in contexts:
        v2_basis = context["v2_basis"]
        swap_basis = leg9._row_norm_swap(
            context["truth"].oracle_basis, v2_basis
        )
        v2_frames.append(leg11._stack_frame(v2_basis))
        swap_frames.append(leg11._stack_frame(swap_basis))
        value = leg14._quotient_distance(swap_frames[-1], v2_frames[-1])
        anchor = displacement_anchors.get((world, context["repetition"]))
        if anchor is None:
            raise RuntimeError(
                f"no Leg 11 displacement anchor for {world} rep "
                f"{context['repetition']}"
            )
        difference = abs(value - anchor)
        disp_anchor_max = max(disp_anchor_max, difference)
        if difference > DISPLACEMENT_ANCHOR_TOLERANCE:
            raise RuntimeError(
                f"displacement metric diverges from Leg 11 on {world} rep "
                f"{context['repetition']}: {value:.12f} vs {anchor:.12f}"
            )
        disp_v2.append(value)

    # ---- Leg 14 clouds + offset (gates 4/5) ----------------------------------
    gpa_v2 = leg14._frechet_mean_multistart(v2_frames)
    gpa_swap = leg14._frechet_mean_multistart(swap_frames)
    consensus = gpa_v2["mean"]
    swap_consensus = gpa_swap["mean"]
    offset_norm = leg14._quotient_distance(consensus, swap_consensus)

    persisted_gate = leg14_gates[world]
    persisted_companion = leg14_companions[world]
    persisted_offset = float(
        persisted_companion["v2_consensus_to_swap_consensus"]
    )
    persisted_v2_objective = float(
        persisted_gate["gpa_objective_mean_squared_distance"]
    )
    persisted_swap_objective = (
        float(persisted_companion["swap_cloud_rms_spread"]) ** 2
    )
    offset_anchor_gaps = {
        "offset": abs(offset_norm - persisted_offset),
        "v2_objective": abs(
            gpa_v2["objective_mean_squared_distance"] - persisted_v2_objective
        ),
        "swap_objective": abs(
            gpa_swap["objective_mean_squared_distance"]
            - persisted_swap_objective
        ),
    }
    if max(offset_anchor_gaps.values()) > OFFSET_ANCHOR_TOLERANCE:
        raise RuntimeError(
            f"Leg 14 cloud rebuild diverges on {world}: {offset_anchor_gaps}"
        )

    width = max(consensus.shape[1], swap_consensus.shape[1])
    a_center = leg14._pad(consensus, width)
    b_center = leg14._pad(swap_consensus, width)
    b_aligned = leg14._align(b_center, a_center)
    delta = a_center - b_aligned
    if abs(float(np.linalg.norm(delta)) - offset_norm) > (
        SELF_CONSISTENCY_TOLERANCE
    ):
        raise RuntimeError(
            f"offset representative inconsistent with quotient distance on "
            f"{world}"
        )
    print(
        f"[m4e2] {world} offset rebuilt: ||Delta||={offset_norm:.6f} "
        f"(persisted {persisted_offset:.6f})",
        flush=True,
    )

    # ---- subspace constructions (gate 6 inside S1) ---------------------------
    arm_b_gate_max = 0.0
    s1_per_rep: list[np.ndarray] = []
    s2_per_rep: list[np.ndarray] = []
    q_values: list[int] = []
    for context in contexts:
        machinery = _response_direction_machinery(context)
        arm_b_gate_max = max(arm_b_gate_max, _arm_b_gate(context, machinery))
        s1_per_rep.append(_s1_patterns(context, machinery))
        q_values.append(int(machinery["q"]))
        s2_per_rep.append(_s2_patterns(context))
    d1_target = int(np.median(q_values))
    s1_patterns, s1_captured, d1 = _common_core(
        s1_per_rep, retained_dim=d1_target
    )
    d2_target = int(s2_per_rep[0].shape[1])
    s2_patterns, s2_captured, d2 = _common_core(
        s2_per_rep, retained_dim=d2_target
    )

    s1_basis = _pattern_basis_to_matrix_basis(s1_patterns, width)
    s2_basis = _pattern_basis_to_matrix_basis(s2_patterns, width)

    categories = a_center.shape[0] // len(ROLES)
    constant_patterns = np.zeros((a_center.shape[0], len(ROLES)))
    for index in range(len(ROLES)):
        constant_patterns[
            index * categories : (index + 1) * categories, index
        ] = 1.0 / np.sqrt(categories)
    n1_mats = [
        np.outer(constant_patterns[:, index], np.eye(width)[w])
        for index in range(len(ROLES))
        for w in range(width)
    ]
    _, _, right_vectors_t = np.linalg.svd(a_center, full_matrices=False)
    n2_mats = [
        a_center @ np.outer(right_vectors_t[i], right_vectors_t[i])
        for i in range(right_vectors_t.shape[0])
    ]
    n3_mats = []
    for index in range(len(ROLES)):
        block = np.zeros_like(a_center)
        block[index * categories : (index + 1) * categories] = a_center[
            index * categories : (index + 1) * categories
        ]
        n3_mats.append(block)
    s3_basis = _orthonormal_matrix_basis(n1_mats + n2_mats + n3_mats)
    n1_basis = _orthonormal_matrix_basis(n1_mats)
    n2_basis = _orthonormal_matrix_basis(n2_mats)
    n3_basis = _orthonormal_matrix_basis(n3_mats)

    bases = {
        "S1_safety_complement": s1_basis,
        "S2_supervision_span": s2_basis,
        "S3_norm_scale_modes": s3_basis,
    }
    dims = {name: int(basis.shape[1]) for name, basis in bases.items()}
    total_dim = a_center.size
    null_shares = {name: dims[name] / total_dim for name in bases}

    registered = _sequential_shares(delta, bases, SUBSPACE_NAMES)
    reverse = _sequential_shares(delta, bases, tuple(reversed(SUBSPACE_NAMES)))
    standalone = {
        name: float(
            np.sum(_project(delta.reshape(-1), basis) ** 2)
            / max(float(np.sum(delta.reshape(-1) ** 2)), EPS)
        )
        for name, basis in bases.items()
    }

    # within-S3 family splits (companions): of the registered-order S3
    # component and of the standalone S3 component, plus the direct
    # standalone family shares of Delta itself (each with null dim/624)
    family_bases = {
        "n1_centering_mass": n1_basis,
        "n2_column_scale": n2_basis,
        "n3_role_size": n3_basis,
    }
    family_order = ("n1_centering_mass", "n2_column_scale", "n3_role_size")
    s3_component = registered["components"]["S3_norm_scale_modes"]
    s3_families = _sequential_shares(
        s3_component, family_bases, family_order
    )["shares"]
    s3_standalone_component = _project(
        delta.reshape(-1), s3_basis
    ).reshape(delta.shape)
    s3_families_standalone_component = _sequential_shares(
        s3_standalone_component, family_bases, family_order
    )["shares"]
    family_standalone_shares = {
        name: float(
            np.sum(_project(delta.reshape(-1), basis) ** 2)
            / max(float(np.sum(delta.reshape(-1) ** 2)), EPS)
        )
        for name, basis in family_bases.items()
    }
    family_dims = {
        name: int(basis.shape[1]) for name, basis in family_bases.items()
    }

    # right-side column-space split (companion): width-mismatch mass, with
    # its random baseline 1 - rank(B)/48 (a random direction set already
    # puts that share outside a rank_b-dim row subspace)
    q_b, _ = np.linalg.qr(b_aligned)
    rank_b = int(np.linalg.matrix_rank(b_aligned, tol=1e-10))
    q_b = q_b[:, :rank_b]
    delta_in_b_col = q_b @ (q_b.T @ delta)
    width_mismatch_share = float(
        np.sum((delta - delta_in_b_col) ** 2) / max(np.sum(delta**2), EPS)
    )
    width_mismatch_baseline = 1.0 - rank_b / delta.shape[0]

    # dominant component (pre-coded: largest registered-order share among
    # S1/S2/S3; ties break to the first of the registered order)
    ordered_shares = [registered["shares"][name] for name in SUBSPACE_NAMES]
    dominant_name = SUBSPACE_NAMES[int(np.argmax(ordered_shares))]
    dominant_component = registered["components"][dominant_name]
    dominant_norm = float(np.linalg.norm(dominant_component))
    u_dom = dominant_component / max(dominant_norm, EPS)

    # offset singular spectrum (companion)
    delta_singular = np.linalg.svd(delta, compute_uv=False)

    # ---- diagnostic refit (task 4; gates 7/8) --------------------------------
    gap_rows: list[dict[str, Any]] = []
    refit_summary: list[dict[str, Any]] = []
    row_anchor_max = 0.0
    rot_gate_max = 0.0
    world_reference = leg14_rows[leg14_rows["world"] == world]
    for repetition, context in enumerate(contexts):
        frame_aligned = leg14._align(
            leg14._pad(v2_frames[repetition], width), a_center
        )
        coefficient = float(np.sum(frame_aligned * u_dom))
        frame_dom = frame_aligned - coefficient * u_dom
        rank_before = int(np.linalg.matrix_rank(frame_aligned, tol=1e-10))
        rank_after = int(np.linalg.matrix_rank(frame_dom, tol=1e-10))
        if rank_after < rank_before:
            raise RuntimeError(
                f"dominant-removal collapses frame rank on {world} rep "
                f"{repetition}: {rank_before} -> {rank_after}"
            )
        basis_dom = leg11._slice_frame(frame_dom, categories)
        disp_dom = leg14._quotient_distance(
            swap_frames[repetition], frame_dom
        )

        seed = context["seed"]
        authors = context["authors"]
        truth = context["truth"]
        true_d = {
            author: leg4._true_derivative(truth, author)
            for author in range(authors)
        }
        reference = world_reference[
            world_reference["repetition"] == repetition
        ]
        if len(reference) != 2 * authors:
            raise RuntimeError(
                f"Leg 14 gap-row reference incomplete for {world} rep "
                f"{repetition}"
            )
        rot_gated = False
        rep_gap_dom: list[float] = []
        for view in ("train", "test"):
            for author in range(authors):
                stack = context["oracle_stacks"][view][author]
                stored_row = reference[
                    (reference["author"] == author)
                    & (reference["view"] == view)
                ]
                if len(stored_row) != 1:
                    raise RuntimeError(
                        f"Leg 14 gap-row reference missing {world} "
                        f"r{repetition} {view} a{author}"
                    )
                stored_row = stored_row.iloc[0]
                degenerate = bool(
                    float(np.linalg.norm(stack["D"])) < leg4.FLIP_TOLERANCE
                )
                if degenerate != bool(stored_row["degenerate_reference"]):
                    raise RuntimeError(
                        f"degenerate flag mismatch vs Leg 14 on {world} "
                        f"r{repetition} {view} a{author}"
                    )
                keys = {
                    "world": world,
                    "repetition": repetition,
                    "seed": seed,
                    "author": author,
                    "view": view,
                    "forced_route": stack["selected_model"],
                    "degenerate_reference": degenerate,
                    "dominant_subspace": dominant_name,
                }
                if degenerate:
                    gap_rows.append(
                        {
                            **keys,
                            "e_orc_true": np.nan,
                            "gap_v2": np.nan,
                            "e_dom_true": np.nan,
                            "gap_dom": np.nan,
                        }
                    )
                    continue
                d_true = true_d[author]
                e_orc = leg3._relative_error(stack["D"], d_true)
                anchor_gap = abs(e_orc - float(stored_row["e_orc_true"]))
                row_anchor_max = max(row_anchor_max, anchor_gap)
                if anchor_gap > ROW_ANCHOR_TOLERANCE:
                    raise RuntimeError(
                        f"e_orc diverges from Leg 14 persisted rows on "
                        f"{world} r{repetition} {view} a{author}: "
                        f"{anchor_gap:.3e}"
                    )
                d_dom = leg14._forced_refit(context, view, author, basis_dom)
                e_dom = leg3._relative_error(d_dom, d_true)
                if not rot_gated:
                    rotation = leg14._random_rotation(
                        width, seed + ROT_SEED_OFFSET
                    )
                    rotated_basis = leg11._slice_frame(
                        frame_dom @ rotation, categories
                    )
                    d_rotated = leg14._forced_refit(
                        context, view, author, rotated_basis
                    )
                    rot_gate = leg3._relative_error(d_rotated, d_dom)
                    rot_gate_max = max(rot_gate_max, rot_gate)
                    if rot_gate > ROT_GATE_TOLERANCE:
                        raise RuntimeError(
                            f"dominant-removed frame is not well-defined on "
                            f"the quotient on {world} r{repetition}: "
                            f"{rot_gate:.3e}"
                        )
                    rot_gated = True
                gap_dom = e_dom - e_orc
                rep_gap_dom.append(gap_dom)
                gap_rows.append(
                    {
                        **keys,
                        "e_orc_true": e_orc,
                        "gap_v2": float(stored_row["gap_v2"]),
                        "e_dom_true": e_dom,
                        "gap_dom": gap_dom,
                    }
                )
        refit_summary.append(
            {
                "world": world,
                "repetition": repetition,
                "seed": seed,
                "dominant_subspace": dominant_name,
                "dominant_coefficient": coefficient,
                "disp_v2": disp_v2[repetition],
                "disp_dom": disp_dom,
                "alpha_dom": disp_dom / disp_v2[repetition],
                "frame_rank_before": rank_before,
                "frame_rank_after": rank_after,
            }
        )
        print(
            f"[m4e2] refit {world} rep={repetition} "
            f"alpha_dom={disp_dom / disp_v2[repetition]:.3f} "
            f"coeff={coefficient:.3f}",
            flush=True,
        )

    gates = {
        "world": world,
        "unit_check_max": max(
            float(context["unit_gap"]) for context in contexts
        ),
        "displacement_anchor_max_abs_diff": disp_anchor_max,
        "offset_anchor_abs_diff": offset_anchor_gaps["offset"],
        "gpa_v2_objective_abs_diff": offset_anchor_gaps["v2_objective"],
        "gpa_swap_objective_abs_diff": offset_anchor_gaps["swap_objective"],
        "arm_b_gate_max": arm_b_gate_max,
        "leg14_e_orc_anchor_max_abs_diff": row_anchor_max,
        "rot_gate_dom_max_rel_error": rot_gate_max,
        "gpa_v2_best_init": int(gpa_v2["best_init_index"]),
        "gpa_v2_n_distinct_basins": int(gpa_v2["n_distinct_basins"]),
        "gpa_swap_n_distinct_basins": int(gpa_swap["n_distinct_basins"]),
    }
    return {
        "delta": delta,
        "offset_norm": offset_norm,
        "width": width,
        "bases_dims": dims,
        "null_shares": null_shares,
        "registered_shares": registered["shares"],
        "reverse_shares": reverse["shares"],
        "standalone_shares": standalone,
        "s3_family_shares": s3_families,
        "s3_family_shares_standalone_component": (
            s3_families_standalone_component
        ),
        "family_standalone_shares": family_standalone_shares,
        "family_dims": family_dims,
        "width_mismatch_share": width_mismatch_share,
        "width_mismatch_baseline": width_mismatch_baseline,
        "rank_b_aligned": rank_b,
        "delta_singular": delta_singular,
        "dominant_name": dominant_name,
        "dominant_component": dominant_component,
        "dominant_norm": dominant_norm,
        "dominant_share": registered["shares"][dominant_name],
        "s1_captured": s1_captured,
        "s2_captured": s2_captured,
        "d1": d1,
        "d2": d2,
        "q_values": q_values,
        "gap_rows": gap_rows,
        "refit_summary": refit_summary,
        "gates": gates,
        "validation_rows": [
            row for context in contexts for row in context["validation_rows"]
        ],
    }


# ---------------------------------------------------------------------------
# adjudication (pre-coded; see docstring)
# ---------------------------------------------------------------------------


def _author_level(gap_rows: pd.DataFrame) -> pd.DataFrame:
    usable = gap_rows[~gap_rows["degenerate_reference"]]
    return (
        usable.groupby(["world", "repetition", "author"])[
            ["gap_v2", "gap_dom"]
        ]
        .mean()
        .reset_index()
    )


def _adjudicate(
    worlds: list[str],
    world_results: dict[str, dict[str, Any]],
    cosine_offsets: dict[str, float],
    gap_rows: pd.DataFrame,
) -> dict[str, Any]:
    # ---- lean (a) + pivot -----------------------------------------------------
    shares_by_world = {
        world: world_results[world]["registered_shares"] for world in worlds
    }
    concentrated: list[str] = []
    for name in SUBSPACE_NAMES:
        if all(
            shares_by_world[world][name] >= LEAN_A_SHARE_BAR
            for world in worlds
        ):
            concentrated.append(name)
    lean_a_held = len(concentrated) >= 1
    point_lean_s1 = "S1_safety_complement" in concentrated
    lean_a = {
        "statement": (
            ">= 60% squared-norm concentration in ONE subspace consistently "
            "across the 3 worlds (registered-order sequential shares; "
            "point-lean S1)"
        ),
        "shares_by_world": shares_by_world,
        "subspaces_at_bar_all_worlds": concentrated,
        "held": bool(lean_a_held),
        "point_lean_S1_held": bool(point_lean_s1),
    }
    pivot_fires = all(
        max(shares_by_world[world][name] for name in SUBSPACE_NAMES)
        < PIVOT_SHARE_BAR
        for world in worlds
    )
    pivot = {
        "registered": (
            "the offset spreads (< 40% in every subspace) -> no single "
            "objective term is responsible; the open problem stays open "
            "exactly as registered at Leg 14, and the loop moves to fresh "
            "mining outside the M4-D/E line"
        ),
        "pre_coded_rule": (
            "fires iff max registered-order share over {S1,S2,S3} < .40 in "
            "EVERY world"
        ),
        "max_share_by_world": {
            world: float(
                max(shares_by_world[world][name] for name in SUBSPACE_NAMES)
            )
            for world in worlds
        },
        "fires": bool(pivot_fires),
    }

    # ---- lean (b) --------------------------------------------------------------
    lean_b_held = all(
        value >= LEAN_B_COSINE_BAR for value in cosine_offsets.values()
    )
    lean_b = {
        "statement": (
            "cross-world pairwise Procrustes cosine of the offset vectors "
            ">= .7 for all 3 pairs (one mechanism)"
        ),
        "pairwise_cosines": cosine_offsets,
        "held": bool(lean_b_held),
    }

    # ---- lean (c) --------------------------------------------------------------
    author = _author_level(gap_rows)
    pooled_v2 = float(author["gap_v2"].median())
    pooled_dom = float(author["gap_dom"].median())
    closure = 1.0 - pooled_dom / max(pooled_v2, EPS)
    world_closures = {}
    for world in worlds:
        scoped = author[author["world"] == world]
        world_closures[world] = {
            "gap_v2": float(scoped["gap_v2"].median()),
            "gap_dom": float(scoped["gap_dom"].median()),
            "closure": float(
                1.0
                - scoped["gap_dom"].median()
                / max(scoped["gap_v2"].median(), EPS)
            ),
        }
    lean_c = {
        "statement": (
            "removing the dominant component closes >= half the paired gap "
            "(pooled closure = 1 - pooled_gap_dom / pooled_gap_v2, median "
            "over usable author-level rows of the 3 worlds)"
        ),
        "pooled_gap_v2": pooled_v2,
        "pooled_gap_dom": pooled_dom,
        "pooled_closure": float(closure),
        "world_closures": world_closures,
        "held": bool(closure >= LEAN_C_CLOSURE_BAR),
    }
    return {
        "lean_a": lean_a,
        "lean_b": lean_b,
        "lean_c": lean_c,
        "pivot": pivot,
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


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
        default=ROOT / "results" / "m4_e2_offset_anatomy",
    )
    parser.add_argument(
        "--worlds",
        type=str,
        default=None,
        help="comma-separated subset (debug only; adjudication needs all 3)",
    )
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    spec = M4ChartEcologySpec(**config["base_spec"])
    worlds = (
        [w for w in args.worlds.split(",") if w]
        if args.worlds
        else list(HIGH_GAP_WORLDS)
    )
    for world in worlds:
        if world not in HIGH_GAP_WORLDS:
            raise SystemExit(f"not a registered high-gap world: {world}")

    displacement_anchors = leg14._load_leg11_displacement_anchors()
    leg14_decision = _load_leg14_decision()
    leg14_gates = _leg14_world_gates(leg14_decision)
    leg14_companions = leg14_decision["companions_target_motion_and_basins"]
    leg14_rows = _load_leg14_gap_rows()

    world_results: dict[str, dict[str, Any]] = {}
    for world in worlds:
        world_results[world] = _world_pass(
            world,
            config,
            spec,
            displacement_anchors,
            leg14_gates,
            leg14_companions,
            leg14_rows,
        )

    if set(worlds) != set(HIGH_GAP_WORLDS):
        print(
            "[m4e2] DEBUG SUBSET RUN: adjudication and outputs refused "
            "(all three registered worlds required)"
        )
        return

    # ---- cross-world cosines (task 3) ----------------------------------------
    pairs = [
        (worlds[i], worlds[j])
        for i in range(len(worlds))
        for j in range(i + 1, len(worlds))
    ]
    cosine_rows: list[dict[str, Any]] = []
    cosine_offsets: dict[str, float] = {}
    cosine_dominant: dict[str, float] = {}
    rng_perm = np.random.default_rng([int(config["seed"]), PERM_NULL_SEED_TAG])
    rng_rand = np.random.default_rng(
        [int(config["seed"]), RANDOM_NULL_SEED_TAG]
    )
    shape = world_results[worlds[0]]["delta"].shape
    random_null = []
    for _ in range(NULL_DRAWS):
        first = rng_rand.standard_normal(shape)
        second = rng_rand.standard_normal(shape)
        random_null.append(_procrustes_cosine(first, second))
    random_null = np.asarray(random_null)
    for first, second in pairs:
        pair_name = f"{first}|{second}"
        delta_first = world_results[first]["delta"]
        delta_second = world_results[second]["delta"]
        raw = _procrustes_cosine(delta_first, delta_second)
        cosine_offsets[pair_name] = raw
        perm_values = np.asarray(
            [
                _procrustes_cosine(
                    delta_first,
                    _within_role_permutation(delta_second, rng_perm),
                )
                for _ in range(NULL_DRAWS)
            ]
        )
        dom = _procrustes_cosine(
            world_results[first]["dominant_component"],
            world_results[second]["dominant_component"],
        )
        cosine_dominant[pair_name] = dom
        cosine_rows.append(
            {
                "pair": pair_name,
                "cosine_offset": raw,
                "cosine_dominant_component": dom,
                "perm_null_median": float(np.median(perm_values)),
                "perm_null_q95": float(np.quantile(perm_values, 0.95)),
                "random_null_median": float(np.median(random_null)),
                "random_null_q95": float(np.quantile(random_null, 0.95)),
                "dominant_first": world_results[first]["dominant_name"],
                "dominant_second": world_results[second]["dominant_name"],
            }
        )

    # ---- adjudication ----------------------------------------------------------
    gap_rows = pd.DataFrame(
        [row for world in worlds for row in world_results[world]["gap_rows"]]
    )
    refit_summary = pd.DataFrame(
        [
            row
            for world in worlds
            for row in world_results[world]["refit_summary"]
        ]
    )
    expected_rows = len(worlds) * int(config["repetitions"]) * 2 * 16
    if len(gap_rows) != expected_rows:
        raise RuntimeError(
            f"gap rows {len(gap_rows)} != expected {expected_rows}"
        )
    adjudication = _adjudicate(worlds, world_results, cosine_offsets, gap_rows)
    lean_a = adjudication["lean_a"]
    lean_b = adjudication["lean_b"]
    lean_c = adjudication["lean_c"]
    pivot = adjudication["pivot"]
    leans_held = int(lean_a["held"]) + int(lean_b["held"]) + int(
        lean_c["held"]
    )
    if lean_a["held"]:
        verdict = (
            "OFFSET_CONCENTRATED_"
            + "_AND_".join(lean_a["subspaces_at_bar_all_worlds"])
        )
    elif pivot["fires"]:
        verdict = "OFFSET_SPREAD_NO_SINGLE_OBJECTIVE_TERM"
    else:
        verdict = "PARTIAL_CONCENTRATION_NEITHER_LEAN_NOR_PIVOT"

    # ---- outputs ----------------------------------------------------------------
    args.output.mkdir(parents=True, exist_ok=True)
    decomposition_rows = []
    for world in worlds:
        result = world_results[world]
        for order_name, shares in (
            ("registered_S1_S2_S3", result["registered_shares"]),
            ("reverse_S3_S2_S1", result["reverse_shares"]),
        ):
            for name, share in shares.items():
                decomposition_rows.append(
                    {
                        "world": world,
                        "order": order_name,
                        "subspace": name,
                        "share": share,
                        "squared_norm": share * result["offset_norm"] ** 2,
                        "dim_matrix_space": result["bases_dims"].get(name),
                        "null_share": result["null_shares"].get(name),
                        "offset_norm": result["offset_norm"],
                    }
                )
        for name, share in result["standalone_shares"].items():
            decomposition_rows.append(
                {
                    "world": world,
                    "order": "standalone",
                    "subspace": name,
                    "share": share,
                    "squared_norm": share * result["offset_norm"] ** 2,
                    "dim_matrix_space": result["bases_dims"].get(name),
                    "null_share": result["null_shares"].get(name),
                    "offset_norm": result["offset_norm"],
                }
            )
        for order_name, family_shares in (
            ("within_S3_component", result["s3_family_shares"]),
            (
                "within_S3_standalone_component",
                result["s3_family_shares_standalone_component"],
            ),
        ):
            for name, share in family_shares.items():
                decomposition_rows.append(
                    {
                        "world": world,
                        "order": order_name,
                        "subspace": name,
                        "share": share,
                        "squared_norm": None,
                        "dim_matrix_space": result["family_dims"].get(name),
                        "null_share": None,
                        "offset_norm": result["offset_norm"],
                    }
                )
        for name, share in result["family_standalone_shares"].items():
            decomposition_rows.append(
                {
                    "world": world,
                    "order": "standalone_family_of_delta",
                    "subspace": name,
                    "share": share,
                    "squared_norm": share * result["offset_norm"] ** 2,
                    "dim_matrix_space": result["family_dims"][name],
                    "null_share": result["family_dims"][name]
                    / (result["delta"].size),
                    "offset_norm": result["offset_norm"],
                }
            )
    pd.DataFrame(decomposition_rows).to_csv(
        args.output / "decomposition_rows.csv", index=False
    )
    pd.DataFrame(cosine_rows).to_csv(
        args.output / "cosine_rows.csv", index=False
    )
    gap_rows.sort_values(["world", "repetition", "author", "view"]).to_csv(
        args.output / "refit_gap_rows.csv", index=False
    )
    refit_summary.sort_values(["world", "repetition"]).to_csv(
        args.output / "refit_summary_rows.csv", index=False
    )
    subspace_rows = []
    for world in worlds:
        result = world_results[world]
        subspace_rows.append(
            {
                "world": world,
                "offset_norm": result["offset_norm"],
                "width": result["width"],
                "d1_retained": result["d1"],
                "s1_captured_pooled_fraction": result["s1_captured"],
                "q_per_rep": ";".join(str(q) for q in result["q_values"]),
                "d2_retained": result["d2"],
                "s2_captured_pooled_fraction": result["s2_captured"],
                "s3_rank": result["bases_dims"]["S3_norm_scale_modes"],
                "width_mismatch_share": result["width_mismatch_share"],
                "width_mismatch_baseline": result["width_mismatch_baseline"],
                "rank_b_aligned": result["rank_b_aligned"],
                "n2_standalone_share_of_delta": result[
                    "family_standalone_shares"
                ]["n2_column_scale"],
                "dominant_subspace": result["dominant_name"],
                "dominant_share": result["dominant_share"],
                "dominant_norm": result["dominant_norm"],
                "delta_top3_singular": ";".join(
                    f"{value:.4f}" for value in result["delta_singular"][:3]
                ),
                "delta_singular_top1_share": float(
                    result["delta_singular"][0] ** 2
                    / max(np.sum(result["delta_singular"] ** 2), EPS)
                ),
            }
        )
    pd.DataFrame(subspace_rows).to_csv(
        args.output / "subspace_rows.csv", index=False
    )

    validation = pd.DataFrame(
        [
            row
            for world in worlds
            for row in world_results[world]["validation_rows"]
        ]
    )
    validation.to_csv(args.output / "v2_validation.csv", index=False)

    faithfulness = {
        "v2_replay_rows": int(len(validation)),
        "v2_replay_max_abs_difference": (
            float(validation["abs_difference"].max())
            if len(validation)
            else None
        ),
        "per_world_gates": [world_results[w]["gates"] for w in worlds],
        "unit_check_max": max(
            world_results[w]["gates"]["unit_check_max"] for w in worlds
        ),
        "leg11_displacement_anchor_max_abs_diff": max(
            world_results[w]["gates"]["displacement_anchor_max_abs_diff"]
            for w in worlds
        ),
        "leg14_offset_anchor_max_abs_diff": max(
            world_results[w]["gates"]["offset_anchor_abs_diff"]
            for w in worlds
        ),
        "leg14_gpa_objective_max_abs_diff": max(
            max(
                world_results[w]["gates"]["gpa_v2_objective_abs_diff"],
                world_results[w]["gates"]["gpa_swap_objective_abs_diff"],
            )
            for w in worlds
        ),
        "leg10_arm_b_gate_max": max(
            world_results[w]["gates"]["arm_b_gate_max"] for w in worlds
        ),
        "leg14_e_orc_anchor_max_abs_diff": max(
            world_results[w]["gates"]["leg14_e_orc_anchor_max_abs_diff"]
            for w in worlds
        ),
        "rot_gate_dom_max_rel_error": max(
            world_results[w]["gates"]["rot_gate_dom_max_rel_error"]
            for w in worlds
        ),
    }
    decision = {
        "estimand_id": "SUICA_M4_E2_OFFSET_ANATOMY",
        "tier": "EXPLORATORY (open-exploration phase)",
        "registered_in": (
            "docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md M4-E2 "
            "(2026-08-02, loop cycle 11, commit dc97d59, before run); "
            "ledger row M4-E2"
        ),
        "design": {
            "worlds": worlds,
            "offset": (
                "Delta = pad(v2 GPA consensus) - align(pad(swap GPA "
                "consensus)), Leg 14 multi-start GPA reproduced and "
                "anchored to persisted v2_consensus_to_swap_consensus"
            ),
            "subspaces": {
                "S1_safety_complement": (
                    "common core (top-median-q left singular vectors of "
                    "unit-normalized pooled per-rep patterns) of Leg 10 "
                    "arm-B response-supervised feature patterns "
                    "Z_role @ U_q, (x) full column space"
                ),
                "S2_supervision_span": (
                    "common core of author-mean observed mechanism-panel "
                    "response patterns (uncentered), (x) full column space"
                ),
                "S3_norm_scale_modes": (
                    "orthonormalized union of per-role constant patterns "
                    "(x) full column space (centering/mass), principal "
                    "column-scale modes A v_i v_i^T, and per-role size "
                    "modes P_role A"
                ),
                "decomposition": (
                    "sequential orthogonal projection, registered order "
                    "S1 -> S2 -> S3 -> residual; reverse order and "
                    "standalone shares disclosed as ordering sensitivity"
                ),
            },
            "cross_world_statistic": (
                "Procrustes cosine over the right gauge (nuclear norm "
                "normalized); within-role row-permutation null + "
                "matched-shape random null disclosed"
            ),
            "diagnostic_refit": (
                "per rep: align discovered frame to consensus, project out "
                "the single unit matrix direction of the world's dominant "
                "sequential component, slice, canonical forced-route refit "
                "(V2 semantics, 1x r=0), Leg 9 gap semantics vs persisted "
                "gap_v2"
            ),
        },
        "offset_table": {
            world: {
                "offset_norm": world_results[world]["offset_norm"],
                "registered_shares": world_results[world][
                    "registered_shares"
                ],
                "reverse_shares": world_results[world]["reverse_shares"],
                "standalone_shares": world_results[world][
                    "standalone_shares"
                ],
                "s3_family_shares": world_results[world]["s3_family_shares"],
                "s3_family_shares_standalone_component": world_results[
                    world
                ]["s3_family_shares_standalone_component"],
                "family_standalone_shares": world_results[world][
                    "family_standalone_shares"
                ],
                "family_dims": world_results[world]["family_dims"],
                "width_mismatch_share": world_results[world][
                    "width_mismatch_share"
                ],
                "width_mismatch_baseline": world_results[world][
                    "width_mismatch_baseline"
                ],
                "rank_b_aligned": world_results[world]["rank_b_aligned"],
                "subspace_dims": world_results[world]["bases_dims"],
                "null_shares": world_results[world]["null_shares"],
                "s1_captured_pooled_fraction": world_results[world][
                    "s1_captured"
                ],
                "s2_captured_pooled_fraction": world_results[world][
                    "s2_captured"
                ],
                "dominant_subspace": world_results[world]["dominant_name"],
                "dominant_share": world_results[world]["dominant_share"],
                "delta_singular_top1_share": float(
                    world_results[world]["delta_singular"][0] ** 2
                    / max(
                        np.sum(world_results[world]["delta_singular"] ** 2),
                        EPS,
                    )
                ),
            }
            for world in worlds
        },
        "cosines": {
            "offsets": cosine_offsets,
            "dominant_components": cosine_dominant,
            "rows": cosine_rows,
        },
        "faithfulness": faithfulness,
        "lean_a": lean_a,
        "lean_b": lean_b,
        "lean_c": lean_c,
        "leans_held": leans_held,
        "pivot_if": pivot,
        "verdict": verdict,
        "hand_off": (
            "if the pivot fires: no single objective term carries the "
            "offset; the Leg 14 open problem stands as registered and the "
            "loop moves to fresh mining outside the M4-D/E line; otherwise "
            "the identified subspace is the named target for any future "
            "objective redesign"
        ),
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only; truth-referenced "
            "diagnostic on Leg 14's persisted cloud objects; the "
            "dominant-removed frames are DIAGNOSTIC constructions (the "
            "removal direction consumes all 8 reps and the oracle-anchor "
            "cloud), not deployable estimator semantics; S1 uses the "
            "response panel field the safety contract withholds "
            "(diagnostic-only, Leg 10 arm-B precedent); no natural-text, "
            "personality, or clinical claim."
        ),
    }
    with (args.output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    print(
        json.dumps(
            {
                "verdict": verdict,
                "lean_a_held": lean_a["held"],
                "point_lean_S1_held": lean_a["point_lean_S1_held"],
                "registered_shares": {
                    world: {
                        name: round(value, 4)
                        for name, value in world_results[world][
                            "registered_shares"
                        ].items()
                    }
                    for world in worlds
                },
                "lean_b_held": lean_b["held"],
                "cosines": {
                    pair: round(value, 4)
                    for pair, value in cosine_offsets.items()
                },
                "lean_c_held": lean_c["held"],
                "pooled_closure": round(lean_c["pooled_closure"], 4),
                "pivot_fires": pivot["fires"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
