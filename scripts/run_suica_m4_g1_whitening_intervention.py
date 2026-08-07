#!/usr/bin/env python3
"""M4-G1: whitening intervention -- is the scale family an actionable lever?

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, "M4-G1
registration" (2026-08-03, BEFORE run); ledger row M4-G1). Machinery is
IMPORTED from the validated legs -- Leg 4's context build + forced-route
refit + analytic D_true, Leg 3's world seed + relative error, Leg 9's
row-norm swap, Leg 10's freeze-ingredients rebuild + Tikhonov whitening
(`_whitening_with_lambda`, `_bases_from_whitening`), Leg 11's stacked-frame
quotient machinery, Leg 14's GPA Frechet mean + quotient distance (the SAME
functions M4-E2 used). No estimator internals are copied; the ONLY new code
here is (i) the whitening-arm constructions this leg registers (shrinkage /
truncation / identity), built on top of Leg 10's `ingredients` dict, and
(ii) the truth-referenced recovery construction (Part 0.3 below).

THE QUESTION (M4-E2's hand-off). M4-E2 decomposed Leg 14's rep-invariant
common offset and named the whitening's unregularized 1/sqrt(eig) scale
family (its n2 principal column-scale modes) the largest IDENTIFIABLE
carrier (~1/3 sequential, ~1/2 standalone). Carrying mass is not the same as
being fixable. Does REGULARIZING that scale family reduce the discovery
objective's frame displacement -- and if it does, does the reduction
transfer to truth, or is it cosmetic (M4-F5/Leg-12 precedent: self-
consistency and truth have moved in opposite directions twice already)?

ARMS (registered; do not add or drop): `baseline` (deployed 1/sqrt(eig));
`shrinkage_{0.01,0.1,1.0}` (1/sqrt(eig+lambda), lambda = ratio*median(eig));
`truncated_{90,75,50}` (drop the smallest-eigenvalue retained directions,
keep the top-k covering >= that fraction of retained spectral mass, SAME
1/sqrt(eig) law on survivors); `identity` (eigenvector rotation only, scale
= 1, no amplification at all). All eight act on Leg 10's OWN freeze
ingredients (the reference-calibration covariance eigendecomposition Leg 10
already validated bit-near-exactly against the frozen V2 transform) -- the
retained EIGENVECTOR SET is always V2's own top-12 (identical rank rule,
identical cap; empirically the rank-tolerance cut never removes any of the
top 12 on these three worlds, verified per-context below), so for
`baseline`/`shrinkage`/`identity` the ARM'S BASIS WIDTH is unchanged (13);
`truncated` changes width by construction (fewer retained columns).

PART 0.1 -- REGISTERED AMBIGUITY: "lambda / median(eig)" (disclosed, resolved
BEFORE compute). The registration's shrinkage ladder is stated as
"lambda / median(eig) in {0.01, 0.1, 1.0}" using the SAME symbol "eig" the
formula "1/sqrt(eig + lambda)" already uses. Two readings are possible:
  Reading A (ADOPTED): median over the RETAINED eigenvalues only (the same
    12 values that appear as "eig" in "eig + lambda" -- the values the
    whitening actually inverts). Same-symbol consistency within one
    sentence; also the more scientifically apt reading, since it scales
    lambda to the OPERATIVE spectrum's own typical size, not a spectrum that
    includes discarded, never-inverted directions.
  Reading B (NOT ADOPTED, computed and reported for disclosure): median over
    ALL raw candidate features' eigenvalues (16 on every probed context here
    -- the full covariance before the rank-tolerance retain-12 cut).
  Both medians are computed and printed per context (see `_g0_ambiguity_
  probe` output folded into g2_rows); Reading A is used for every registered
  lambda in this run. On the three probed contexts (one rep per world) the
  two readings differ by 5-10x (e.g. expansion rep 0: retained-median
  1.215e-3 vs all-16-median 1.62e-4), so this is not a cosmetic choice.

PART 0.2 -- REGISTERED AMBIGUITY: "identity ... no whitening at all"
(disclosed, resolved BEFORE compute). Two readings:
  Reading A (ADOPTED): scale = 1 in the SAME retained eigenbasis (whitening
    = eigenvectors[:, retained], no division at all -- the eigenvectors are
    already orthonormal, so this is a pure rotation/embedding, zero
    per-direction amplification). This keeps width, rotation, and retained
    columns IDENTICAL to baseline; the only thing that varies across all
    eight arms is then, uniformly, the per-direction SCALE LAW -- matching
    the registration's own framing ("the ONLY thing that varies is the
    whitening applied") and giving lean (c) ("identity worse than best
    regularized arm") a clean, apples-to-apples reading: if a completely
    UNSCALED chart does worse than a MODERATELY regularized one, that is
    direct evidence that some anisotropic rescaling is informative and the
    lesson is "regularize the amplification," not "delete whitening."
  Reading B (NOT adopted, disclosed): skip the freeze-stage PCA transform
    entirely and use the raw centered candidate features directly (width =
    p_features = 16 here, not 13; also drops the eigenbasis ROTATION, not
    only the scale). Rejected because (i) it changes TWO things at once
    (rotation AND scale), confounding lean (c)'s "not simply whitening bad"
    reading with "not simply rotation-into-PCA-space bad"; (ii) it is a
    materially larger, differently-shaped implementation (a new feature
    pipeline, not a one-line change to Leg 10's `ingredients` machinery),
    raising both effort and bit-exactness risk for a leg whose registered
    scope is the SCALE family specifically ("intervene on the whitening
    SCALE family" -- M4-G plan doc, "Why this line exists"). Reading A is
    adopted; Reading B is not implemented.

PART 0.3 -- TRUTH-REFERENCED RECOVERY OPERATIONALIZATION (registered BEFORE
compute; this leg's main researcher degree of freedom, per the
registration). "Computed by the identical path on the world's known
structure, in the M4-F5 style" -- M4-F5's defining move was: SAME deployed
path, input varied between the finite noisy realization and a noise-free
construction, with >= 2 truth variants and a degenerate G4 (here G3)
equality check that the truth path, fed the finite input, reproduces the
finite result exactly. This leg's six deliverables do NOT include the
generator/estimator files, so any truth construction must be built ONLY
from functions those files already expose unchanged -- ruling out a
hand-derived "soft-label" reconstruction of the generator's own stochastic
target (which would need new formulas transcribed independently of the
generator's private code, a materially higher-risk undertaking than reusing
an already-validated call).

Leg 4's OWN Part 4b ("D-leg resolution scaling") already contains exactly
the needed reusable primitive: regenerate the world's dynamic event panels
at a DIFFERENT `spec.events` budget via `generate_m4_chart_ecology_world`
UNCHANGED (frozen-world law: identical oracle_basis/author_parameters
verified bit-exact across budgets, only the finite event panels are a fresh
realization), refit via the IDENTICAL `_forced_route_derivative` path, and
compare to the analytic D_true. `_budget_rows_for_world_rep` itself hardcodes
`context["v2_basis"]`, so (mirroring M4-F5's own precedent of writing a
"disclosed structural near-duplicate" when the original does not expose what
a leg needs) this script's `_truth_rows_for_context` is a near-duplicate
parameterized over an ARBITRARY arm basis, calling the SAME three primitives
Leg 4 Part 4b calls (`generate_m4_chart_ecology_world`, `_flatten_events`,
`_forced_route_derivative`) in the SAME order with the SAME frozen-world
assertions.

TWO REGISTERED VARIANTS (both mandatory, sensitivity disclosed):
  Variant 1: budget = 4.0x events (480; the SAME ceiling Leg 4 Part 4b itself
    validated as "possible" without a fallback grid -- reusing an
    already-proven multiplier rather than inventing a new one).
  Variant 2: budget = 8.0x events (960; a further doubling, the genuine
    second, independent finite-sample point this leg needs -- mirroring
    M4-F5's own sensitivity-check convention of probing a multiple of the
    primary rather than trusting one point).
  Budget = 1.0x (the exact deployed finite panel, i.e. e_arm_true itself) is
  DELIBERATELY NOT used as one of the two adjudicated variants: it is
  mechanically a fixed affine function of "gap" (gap_arm = e_arm_true -
  e_orc_true, e_orc_true arm-invariant), so a within-author-view, across-arm
  paired comparison on it is statistically IDENTICAL to gap's own paired
  comparison -- it could never diverge from "gap," defeating the entire
  point of a SEPARATE truth-referenced metric (the motivating precedent:
  Leg 12 and M4-F5 both found self-consistency and truth-recovery moving in
  OPPOSITE directions). Budget = 1.0x is used ONLY for gate G3 (the
  degenerate equality check).

GAP SEMANTICS (Leg 9's / Leg 14's, unchanged): per author-view at the
oracle-forced route, 1x panels, gap_arm = e_arm_true - e_orc_true; author
level = view mean; world level = median over pooled author-reps.
e_orc_true is READ from Leg 14's persisted `gap_rows.csv` (bit-anchored) and
independently recomputed here (both must agree, gate below).

GATES (all four M4-F standing rules; explicit compliance stated in the
report, not here -- this docstring states the MECHANICS only):
- G0 POWER: paired-by-world (n=3) CI on the raw offset difference
  (baseline - arm) for each of the six candidate (shrinkage/truncation)
  arms; t-interval, df=2. UNDERPOWERED if the half-width exceeds 12.5% of
  the mean M4-E2 baseline offset (~12.999) = ~1.625 absolute units.
- G1 ANCHOR: `baseline` arm's basis bit-reproduces `context["v2_basis"]`
  (<=1e-12), its GPA offset bit-reproduces M4-E2's persisted `offset_norm`
  (<=1e-12), and its gap_v2/e_d_true_v2 bit-reproduces Leg 14's persisted
  `gap_rows.csv` (<=1e-12).
- G2 CHANNEL LIVENESS: per arm, the whitening's per-direction scale-factor
  spectrum (1/sqrt(eig+lambda), or 1 for identity) and its condition number
  are reported beside baseline's; "materially different" is pre-declared as
  >= 10% relative change in condition number OR any change in retained
  width -- given the expected swings (baseline condition number ~300+,
  shrinkage_1.0 ~15x smaller, identity exactly 1, truncated changes width
  outright), this bar is not expected to be close.
- G3 TRUTH-PATH INVARIANCE: the truth-recovery code path, evaluated at
  budget=1.0 (its own frozen-world short-circuit, reusing
  `context["observed"]` with no regeneration, mirroring Leg 4 Part 4b's own
  `if budget == 1.0: observed_b = context["observed"]`), reproduces the gap
  stage's own e_arm_true for the same (world, rep, view, author, arm)
  EXACTLY (<=1e-12) -- a spot-check subset, not merely a trivial
  self-identity.
- G4 MATERIALITY FORM: G0 and G2 are equivalence/margin bounds by
  construction (a CI-vs-margin bound; a magnitude-of-change-vs-margin
  bound); G3 is a degenerate exact-equality check, not a significance test;
  none of G0-G3 is a nil-significance test on a known-nonzero quantity.

Chunked execution (this arc's standard workaround): `--world` + `--stage
{offset_gap, truth}` (+ `--budget` for the truth stage) computes ONE
(world, stage) partial and writes it to disk; `--assemble` reads every
partial, cross-checks completeness, and adjudicates. Each stage call rebuilds
its 8 contexts from scratch (idempotent, ~35-45s overhead) rather than
threading python objects across process boundaries.
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_suica_m4_d_dleg_floor_leg4 as leg4  # noqa: E402  bit-exact reuse
import run_suica_m4_d_overspan_control_leg3 as leg3  # noqa: E402
import run_suica_m4_d_bias_anatomy_leg8 as leg8  # noqa: E402
import run_suica_m4_d_direction_anatomy_leg10 as leg10  # noqa: E402
import run_suica_m4_d_bias_variance_leg9 as leg9  # noqa: E402
import run_suica_m4_d_perturbation_leg11 as leg11  # noqa: E402
import run_suica_m4_d_displacement_leg14 as leg14  # noqa: E402

from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)

HIGH_GAP_WORLDS = leg11.HIGH_GAP_WORLDS
ROLES = leg11.ROLES
FLIP_TOLERANCE = leg4.FLIP_TOLERANCE

SHRINKAGE_RATIOS = {
    "shrinkage_0.01": 0.01,
    "shrinkage_0.1": 0.1,
    "shrinkage_1.0": 1.0,
}
TRUNCATION_FRACTIONS = {
    "truncated_90": 0.90,
    "truncated_75": 0.75,
    "truncated_50": 0.50,
}
ARM_NAMES = (
    "baseline",
    "shrinkage_0.01",
    "shrinkage_0.1",
    "shrinkage_1.0",
    "truncated_90",
    "truncated_75",
    "truncated_50",
    "identity",
)
CANDIDATE_ARMS = (
    "shrinkage_0.01",
    "shrinkage_0.1",
    "shrinkage_1.0",
    "truncated_90",
    "truncated_75",
    "truncated_50",
)  # lean (a)/(b)/(c) pool -- registered "shrinkage or truncation"

TRUTH_BUDGETS = (4.0, 8.0)
G1_OFFSET_TOLERANCE = 1e-12
G1_BASIS_TOLERANCE = 1e-12
G1_GAP_TOLERANCE = 1e-12
G3_TOLERANCE = 1e-12
ROW_ANCHOR_TOLERANCE = 1e-9  # leg14 persisted e_orc_true anchor (own recompute)
LEAN_A_REDUCTION_BAR = 0.25
G0_POWER_FRACTION = 0.125
G2_CONDITION_MATERIALITY_RATIO = 0.10
EPS = 1e-300


# ---------------------------------------------------------------------------
# persisted references
# ---------------------------------------------------------------------------


def _load_leg14_gap_rows() -> pd.DataFrame:
    path = ROOT / "results" / "m4_d_discovery_displacement" / "gap_rows.csv"
    if not path.exists():
        raise RuntimeError(f"Leg 14 persisted gap rows are a required anchor: {path}")
    return pd.read_csv(path)


def _load_m4e2_decision() -> dict[str, Any]:
    path = ROOT / "results" / "m4_e2_offset_anatomy" / "decision.json"
    if not path.exists():
        raise RuntimeError(f"M4-E2 persisted decision is a required anchor: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


# ---------------------------------------------------------------------------
# whitening arms (built on Leg 10's freeze-ingredients machinery, unchanged)
# ---------------------------------------------------------------------------


def _whitening_for_arm(
    ingredients: dict[str, Any], arm: str
) -> tuple[np.ndarray, dict[str, Any]]:
    eigenvalues_all = ingredients["eigenvalues"]
    eigenvectors = ingredients["eigenvectors"]
    retained = ingredients["retained"]
    eig_retained = eigenvalues_all[retained]  # already descending (leg10 sorts)
    if arm == "baseline":
        whitening = leg10._whitening_with_lambda(ingredients, 0.0)
        return whitening, {
            "lambda": 0.0,
            "k_retained": int(len(retained)),
            "median_eig_retained": float(np.median(eig_retained)),
            "median_eig_all": float(np.median(eigenvalues_all)),
        }
    if arm in SHRINKAGE_RATIOS:
        ratio = SHRINKAGE_RATIOS[arm]
        median_retained = float(np.median(eig_retained))
        median_all = float(np.median(eigenvalues_all))
        lam = ratio * median_retained  # Reading A, adopted (Part 0.1)
        lam_reading_b = ratio * median_all  # Reading B, disclosed only
        whitening = leg10._whitening_with_lambda(ingredients, lam)
        return whitening, {
            "ratio": ratio,
            "lambda": lam,
            "lambda_reading_b_not_adopted": lam_reading_b,
            "k_retained": int(len(retained)),
            "median_eig_retained": median_retained,
            "median_eig_all": median_all,
        }
    if arm in TRUNCATION_FRACTIONS:
        frac = TRUNCATION_FRACTIONS[arm]
        cummass = np.cumsum(eig_retained) / np.sum(eig_retained)
        k = int(np.searchsorted(cummass, frac) + 1)
        k = int(min(k, len(retained)))
        kept = retained[:k]
        whitening = (
            eigenvectors[:, kept]
            / np.sqrt(np.maximum(eigenvalues_all[kept], 1e-12))[None]
        )
        return whitening, {
            "mass_fraction_target": frac,
            "k_retained": k,
            "cummass_at_k": float(cummass[k - 1]),
            "dropped": int(len(retained) - k),
        }
    if arm == "identity":
        whitening = eigenvectors[:, retained]  # Reading A, adopted (Part 0.2)
        return whitening, {"k_retained": int(len(retained))}
    raise ValueError(f"unknown arm: {arm}")


def _scale_factors(ingredients: dict[str, Any], arm: str, meta: dict[str, Any]) -> np.ndarray:
    eigenvalues_all = ingredients["eigenvalues"]
    retained = ingredients["retained"]
    if arm == "identity":
        return np.ones(meta["k_retained"])
    if arm in TRUNCATION_FRACTIONS:
        kept = retained[: meta["k_retained"]]
        return 1.0 / np.sqrt(np.maximum(eigenvalues_all[kept], 1e-12))
    lam = float(meta.get("lambda", 0.0))
    eig = eigenvalues_all[retained]
    return 1.0 / np.sqrt(np.maximum(eig + lam, 1e-12))


def _condition_number(scale: np.ndarray) -> float:
    if len(scale) < 2:
        return float("nan")
    return float(np.max(scale) / np.min(scale))


# ---------------------------------------------------------------------------
# context + per-arm basis/frame construction (rebuilt fresh each invocation)
# ---------------------------------------------------------------------------


def _build_world_contexts(
    world: str, config: dict[str, Any], spec: M4ChartEcologySpec
) -> list[dict[str, Any]]:
    repetitions = int(config["repetitions"])
    world_index = {name: index for index, name in enumerate(config["worlds"])}[world]
    expected_for = leg8._expected_geometries_lookup(config)
    contexts = []
    for repetition in range(repetitions):
        seed = leg3._world_seed(int(config["seed"]), repetition, world, world_index)
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
            context["truth"], context["flat"][("train", 0)][0]["response_next"].shape[1]
        )
        if unit_gap > 1e-10:
            raise RuntimeError(
                f"analytic D_true fails the unit check on {world} rep {repetition}: "
                f"{unit_gap:.3e}"
            )
        context["unit_gap"] = unit_gap
        contexts.append(context)
        print(
            f"[m4g1] context {world} rep={repetition} ({time.time() - started:.1f}s)",
            flush=True,
        )
    return contexts


def _arm_bases_and_meta(
    contexts: list[dict[str, Any]],
) -> tuple[dict[str, list[dict[str, np.ndarray]]], dict[str, list[dict[str, Any]]]]:
    arm_bases: dict[str, list[dict[str, np.ndarray]]] = {arm: [] for arm in ARM_NAMES}
    arm_meta: dict[str, list[dict[str, Any]]] = {arm: [] for arm in ARM_NAMES}
    for context in contexts:
        ingredients = leg10._freeze_ingredients(context)
        for arm in ARM_NAMES:
            whitening, meta = _whitening_for_arm(ingredients, arm)
            basis = leg10._bases_from_whitening(context, ingredients, whitening)
            arm_bases[arm].append(basis)
            scale = _scale_factors(ingredients, arm, meta)
            meta = {
                **meta,
                "width": int(basis["calibration"].shape[1]),
                "scale_min": float(np.min(scale)),
                "scale_max": float(np.max(scale)),
                "condition_number": _condition_number(scale),
            }
            arm_meta[arm].append(meta)
    return arm_bases, arm_meta


# ---------------------------------------------------------------------------
# stage 1: offset (GPA, per arm) + gap (budget=1x, per arm) + G1/G2/G3
# ---------------------------------------------------------------------------


def _run_offset_gap_stage(
    world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path
) -> None:
    contexts = _build_world_contexts(world, config, spec)
    arm_bases, arm_meta = _arm_bases_and_meta(contexts)

    # ---- G1 anchor (basis) ---------------------------------------------------
    basis_gap_max = 0.0
    for rep_idx, context in enumerate(contexts):
        for role in ROLES:
            diff = float(
                np.max(np.abs(arm_bases["baseline"][rep_idx][role] - context["v2_basis"][role]))
            )
            basis_gap_max = max(basis_gap_max, diff)
    if basis_gap_max > G1_BASIS_TOLERANCE:
        raise RuntimeError(
            f"G1 basis anchor fails on {world}: baseline arm diverges from "
            f"context v2_basis by {basis_gap_max:.3e}"
        )

    # ---- offset (GPA) per arm -------------------------------------------------
    offset_rows = []
    g2_rows = []
    for arm in ARM_NAMES:
        v2_frames = []
        swap_frames = []
        for rep_idx, context in enumerate(contexts):
            basis = arm_bases[arm][rep_idx]
            swap_basis = leg9._row_norm_swap(context["truth"].oracle_basis, basis)
            v2_frames.append(leg11._stack_frame(basis))
            swap_frames.append(leg11._stack_frame(swap_basis))
            meta = arm_meta[arm][rep_idx]
            g2_rows.append(
                {
                    "world": world,
                    "arm": arm,
                    "repetition": rep_idx,
                    **{
                        key: value
                        for key, value in meta.items()
                        if key
                        in (
                            "width",
                            "k_retained",
                            "lambda",
                            "ratio",
                            "mass_fraction_target",
                            "cummass_at_k",
                            "dropped",
                            "scale_min",
                            "scale_max",
                            "condition_number",
                        )
                    },
                }
            )
        gpa_v2 = leg14._frechet_mean_multistart(v2_frames)
        gpa_swap = leg14._frechet_mean_multistart(swap_frames)
        offset = leg14._quotient_distance(gpa_v2["mean"], gpa_swap["mean"])
        offset_rows.append(
            {
                "world": world,
                "arm": arm,
                "offset_norm": offset,
                "width": int(v2_frames[0].shape[1]),
                "gpa_v2_basins": int(gpa_v2["n_distinct_basins"]),
                "gpa_swap_basins": int(gpa_swap["n_distinct_basins"]),
                "gpa_v2_objective": gpa_v2["objective_mean_squared_distance"],
                "gpa_swap_objective": gpa_swap["objective_mean_squared_distance"],
            }
        )
        print(
            f"[m4g1] offset {world} arm={arm} width={v2_frames[0].shape[1]} "
            f"offset={offset:.6f}",
            flush=True,
        )

    # ---- G1 anchor (offset) ----------------------------------------------------
    m4e2 = _load_m4e2_decision()
    persisted_offset = float(m4e2["offset_table"][world]["offset_norm"])
    baseline_offset = next(r for r in offset_rows if r["arm"] == "baseline")["offset_norm"]
    offset_anchor_gap = abs(baseline_offset - persisted_offset)
    if offset_anchor_gap > G1_OFFSET_TOLERANCE:
        raise RuntimeError(
            f"G1 offset anchor fails on {world}: {baseline_offset:.12f} vs "
            f"M4-E2 persisted {persisted_offset:.12f} (|diff|={offset_anchor_gap:.3e})"
        )

    # ---- gap rows at budget=1x, all arms ---------------------------------------
    leg14_rows_ref = _load_leg14_gap_rows()
    leg14_world_rows = leg14_rows_ref[leg14_rows_ref["world"] == world]
    dims = contexts[0]["flat"][("train", 0)][0]["response_next"].shape[1]
    gap_rows = []
    row_anchor_max = 0.0
    g1_gap_anchor_max = 0.0
    g3_check_rows = []
    for rep_idx, context in enumerate(contexts):
        reference = leg14_world_rows[leg14_world_rows["repetition"] == rep_idx]
        fit_kwargs = context["fit_kwargs"]
        for view in ("train", "test"):
            for author in range(context["authors"]):
                stack = context["oracle_stacks"][view][author]
                degenerate = bool(float(np.linalg.norm(stack["D"])) < FLIP_TOLERANCE)
                stored_row = reference[
                    (reference["author"] == author) & (reference["view"] == view)
                ]
                if len(stored_row) != 1:
                    raise RuntimeError(
                        f"Leg 14 gap-row reference missing {world} r{rep_idx} {view} "
                        f"a{author}"
                    )
                stored_row = stored_row.iloc[0]
                if bool(stored_row["degenerate_reference"]) != degenerate:
                    raise RuntimeError(
                        f"degenerate flag mismatch vs Leg 14 on {world} r{rep_idx} "
                        f"{view} a{author}"
                    )
                route = stack["selected_model"]
                keys = {
                    "world": world,
                    "repetition": rep_idx,
                    "view": view,
                    "author": author,
                    "forced_route": route,
                    "degenerate_reference": degenerate,
                }
                if degenerate:
                    for arm in ARM_NAMES:
                        gap_rows.append(
                            {**keys, "arm": arm, "e_arm_true": np.nan, "e_orc_true": np.nan, "gap": np.nan}
                        )
                    continue
                calibration, selection, _ = context["flat"][(view, author)]
                d_true = leg4._true_derivative(context["truth"], author)
                d_orc = leg4._forced_route_derivative(
                    calibration,
                    selection,
                    context["truth"].oracle_basis,
                    model=route,
                    hazard_ridge=fit_kwargs["hazard_ridge"],
                    logistic_iterations=fit_kwargs["logistic_iterations"],
                    dimensions=dims,
                )
                e_orc_true = leg3._relative_error(d_orc, d_true)
                anchor_gap = abs(e_orc_true - float(stored_row["e_orc_true"]))
                row_anchor_max = max(row_anchor_max, anchor_gap)
                if anchor_gap > ROW_ANCHOR_TOLERANCE:
                    raise RuntimeError(
                        f"e_orc_true diverges from Leg 14 persisted rows on {world} "
                        f"r{rep_idx} {view} a{author}: {anchor_gap:.3e}"
                    )
                for arm in ARM_NAMES:
                    basis = arm_bases[arm][rep_idx]
                    d_arm = leg4._forced_route_derivative(
                        calibration,
                        selection,
                        basis,
                        model=route,
                        hazard_ridge=fit_kwargs["hazard_ridge"],
                        logistic_iterations=fit_kwargs["logistic_iterations"],
                        dimensions=dims,
                    )
                    e_arm_true = leg3._relative_error(d_arm, d_true)
                    gap_rows.append(
                        {
                            **keys,
                            "arm": arm,
                            "e_arm_true": e_arm_true,
                            "e_orc_true": e_orc_true,
                            "gap": e_arm_true - e_orc_true,
                        }
                    )
                    if arm == "baseline":
                        g1_gap_diff = abs(e_arm_true - float(stored_row["e_v2_true"]))
                        g1_gap_anchor_max = max(g1_gap_anchor_max, g1_gap_diff)
                        if g1_gap_diff > G1_GAP_TOLERANCE:
                            raise RuntimeError(
                                f"G1 gap anchor fails on {world} r{rep_idx} {view} "
                                f"a{author}: {g1_gap_diff:.3e}"
                            )
                # ---- G3 spot-check: truth path at budget=1.0 reproduces this
                # exactly, via the SAME regeneration-style code the truth
                # stage uses (observed_b = context["observed"], no new draw).
                if rep_idx == 0 and view == "train" and author == 0:
                    for arm in ("baseline", "identity"):
                        basis = arm_bases[arm][rep_idx]
                        calibration_g3 = leg4._flatten_events(
                            context["observed"].ecology.train_calibration, author
                        )
                        selection_g3 = leg4._flatten_events(
                            context["observed"].ecology.train_selection, author
                        )
                        d_arm_g3 = leg4._forced_route_derivative(
                            calibration_g3,
                            selection_g3,
                            basis,
                            model=route,
                            hazard_ridge=fit_kwargs["hazard_ridge"],
                            logistic_iterations=fit_kwargs["logistic_iterations"],
                            dimensions=dims,
                        )
                        e_arm_g3 = leg3._relative_error(d_arm_g3, d_true)
                        reference_e = next(
                            row["e_arm_true"]
                            for row in gap_rows
                            if row["arm"] == arm
                            and row["repetition"] == 0
                            and row["view"] == "train"
                            and row["author"] == 0
                        )
                        g3_check_rows.append(
                            {
                                "world": world,
                                "arm": arm,
                                "repetition": 0,
                                "view": "train",
                                "author": 0,
                                "e_arm_true_gap_stage": reference_e,
                                "e_arm_true_truthpath_budget1": e_arm_g3,
                                "abs_diff": abs(e_arm_g3 - reference_e),
                            }
                        )
    g3_max = max((row["abs_diff"] for row in g3_check_rows), default=float("nan"))
    if g3_max > G3_TOLERANCE:
        raise RuntimeError(f"G3 truth-path invariance fails on {world}: {g3_max:.3e}")

    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(offset_rows).to_csv(output / f"partial_offset_{world}.csv", index=False)
    pd.DataFrame(g2_rows).to_csv(output / f"partial_g2_{world}.csv", index=False)
    pd.DataFrame(gap_rows).to_csv(output / f"partial_gap_{world}.csv", index=False)
    pd.DataFrame(g3_check_rows).to_csv(output / f"partial_g3check_{world}.csv", index=False)
    gates = {
        "world": world,
        "basis_anchor_max_abs_diff": basis_gap_max,
        "offset_anchor_abs_diff": offset_anchor_gap,
        "gap_anchor_max_abs_diff": g1_gap_anchor_max,
        "leg14_e_orc_true_anchor_max_abs_diff": row_anchor_max,
        "g3_truthpath_max_abs_diff": g3_max,
        "unit_check_max": max(c["unit_gap"] for c in contexts),
    }
    with (output / f"partial_gates_offset_gap_{world}.json").open("w", encoding="utf-8") as handle:
        json.dump(gates, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    print(f"[m4g1] offset_gap stage done: {world} ({json.dumps(gates)})", flush=True)


# ---------------------------------------------------------------------------
# stage 2: truth-referenced recovery at a regenerated budget
# ---------------------------------------------------------------------------


def _truth_rows_for_context(
    context: dict[str, Any],
    arm_bases_rep: dict[str, dict[str, np.ndarray]],
    spec: M4ChartEcologySpec,
    budget: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    world = context["world"]
    repetition = context["repetition"]
    seed = context["seed"]
    truth = context["truth"]
    fit_kwargs = context["fit_kwargs"]
    dims = context["flat"][("train", 0)][0]["response_next"].shape[1]
    events_b = int(round(spec.events * budget))
    if budget == 1.0:
        observed_b = context["observed"]
        truth_b = truth
    else:
        spec_b = replace(spec, events=events_b)
        observed_b, truth_b = generate_m4_chart_ecology_world(
            world=world, spec=spec_b, seed=seed
        )
        for role in ROLES:
            if not np.array_equal(truth_b.oracle_basis[role], truth.oracle_basis[role]):
                raise RuntimeError(
                    f"frozen-world violation at budget {budget}: oracle basis[{role}] "
                    f"changed on {world} rep {repetition}"
                )
        for name in ("creation", "gate", "generated_base", "selection"):
            if not np.array_equal(
                truth_b.author_parameters[name], truth.author_parameters[name]
            ):
                raise RuntimeError(
                    f"frozen-world violation at budget {budget}: author parameter "
                    f"{name} changed on {world} rep {repetition}"
                )
    rows: list[dict[str, Any]] = []
    n_cal_rows = n_sel_rows = 0
    for view in ("train", "test"):
        calibration_panel = getattr(observed_b.ecology, f"{view}_calibration")
        selection_panel = getattr(observed_b.ecology, f"{view}_selection")
        for author in range(context["authors"]):
            stack = context["oracle_stacks"][view][author]
            degenerate = bool(float(np.linalg.norm(stack["D"])) < FLIP_TOLERANCE)
            keys = {
                "world": world,
                "repetition": repetition,
                "view": view,
                "author": author,
                "budget": budget,
                "events": events_b,
                "degenerate_reference": degenerate,
            }
            if degenerate:
                for arm in ARM_NAMES:
                    rows.append(
                        {**keys, "arm": arm, "e_arm_true": np.nan, "e_orc_true": np.nan}
                    )
                continue
            route = stack["selected_model"]
            calibration_b = leg4._flatten_events(calibration_panel, author)
            selection_b = leg4._flatten_events(selection_panel, author)
            n_cal_rows = len(calibration_b["choice"])
            n_sel_rows = len(selection_b["choice"])
            d_true = leg4._true_derivative(truth, author)
            d_orc_b = leg4._forced_route_derivative(
                calibration_b,
                selection_b,
                truth.oracle_basis,
                model=route,
                hazard_ridge=fit_kwargs["hazard_ridge"],
                logistic_iterations=fit_kwargs["logistic_iterations"],
                dimensions=dims,
            )
            e_orc_true = leg3._relative_error(d_orc_b, d_true)
            for arm in ARM_NAMES:
                basis = arm_bases_rep[arm]
                d_arm_b = leg4._forced_route_derivative(
                    calibration_b,
                    selection_b,
                    basis,
                    model=route,
                    hazard_ridge=fit_kwargs["hazard_ridge"],
                    logistic_iterations=fit_kwargs["logistic_iterations"],
                    dimensions=dims,
                )
                e_arm_true = leg3._relative_error(d_arm_b, d_true)
                rows.append(
                    {**keys, "arm": arm, "e_arm_true": e_arm_true, "e_orc_true": e_orc_true}
                )
    gate = {
        "world": world,
        "repetition": repetition,
        "budget": budget,
        "events": events_b,
        "n_cal_rows_last": n_cal_rows,
        "n_sel_rows_last": n_sel_rows,
    }
    return rows, gate


def _run_truth_stage(
    world: str,
    config: dict[str, Any],
    spec: M4ChartEcologySpec,
    budget: float,
    output: Path,
) -> None:
    contexts = _build_world_contexts(world, config, spec)
    arm_bases, _ = _arm_bases_and_meta(contexts)
    all_rows: list[dict[str, Any]] = []
    gates: list[dict[str, Any]] = []
    for rep_idx, context in enumerate(contexts):
        started = time.time()
        arm_bases_rep = {arm: arm_bases[arm][rep_idx] for arm in ARM_NAMES}
        rows, gate = _truth_rows_for_context(context, arm_bases_rep, spec, budget)
        all_rows.extend(rows)
        gates.append(gate)
        print(
            f"[m4g1] truth b={budget} {world} rep={rep_idx} "
            f"({time.time() - started:.1f}s, events={gate['events']})",
            flush=True,
        )
    output.mkdir(parents=True, exist_ok=True)
    budget_tag = f"{budget:g}"
    pd.DataFrame(all_rows).to_csv(
        output / f"partial_truth_{world}_b{budget_tag}.csv", index=False
    )
    with (output / f"partial_gates_truth_{world}_b{budget_tag}.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump({"gates": gates}, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    print(f"[m4g1] truth stage done: {world} budget={budget}", flush=True)


# ---------------------------------------------------------------------------
# assemble + adjudicate
# ---------------------------------------------------------------------------


def _author_level_gap(gap_rows: pd.DataFrame) -> pd.DataFrame:
    usable = gap_rows[~gap_rows["degenerate_reference"]]
    return (
        usable.groupby(["world", "repetition", "author", "arm"])[["e_arm_true", "e_orc_true", "gap"]]
        .mean()
        .reset_index()
    )


def _author_level_truth(truth_rows: pd.DataFrame) -> pd.DataFrame:
    usable = truth_rows[~truth_rows["degenerate_reference"]]
    return (
        usable.groupby(["world", "repetition", "author", "arm", "budget"])[
            ["e_arm_true", "e_orc_true"]
        ]
        .mean()
        .reset_index()
    )


def _paired_world_ci(diffs: np.ndarray) -> dict[str, float]:
    n = len(diffs)
    mean = float(np.mean(diffs))
    if n < 2:
        return {"n": n, "mean": mean, "se": float("nan"), "ci_lo": float("nan"), "ci_hi": float("nan"), "half_width": float("nan")}
    se = float(np.std(diffs, ddof=1) / np.sqrt(n))
    t_crit = float(stats.t.ppf(0.975, df=n - 1))
    half_width = t_crit * se
    return {
        "n": n,
        "mean": mean,
        "se": se,
        "t_crit_df": n - 1,
        "ci_lo": mean - half_width,
        "ci_hi": mean + half_width,
        "half_width": half_width,
    }


def _paired_author_ci(diffs: np.ndarray) -> dict[str, float]:
    n = len(diffs)
    mean = float(np.mean(diffs))
    se = float(np.std(diffs, ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    t_crit = float(stats.t.ppf(0.975, df=max(n - 1, 1))) if n > 1 else float("nan")
    half_width = t_crit * se if n > 1 else float("nan")
    return {
        "n": n,
        "mean": mean,
        "se": se,
        "ci_lo": mean - half_width if n > 1 else float("nan"),
        "ci_hi": mean + half_width if n > 1 else float("nan"),
        "half_width": half_width,
    }


def _assemble(output: Path) -> None:
    worlds = list(HIGH_GAP_WORLDS)

    offset_frames = [pd.read_csv(output / f"partial_offset_{w}.csv") for w in worlds]
    offset_rows = pd.concat(offset_frames, ignore_index=True)
    g2_frames = [pd.read_csv(output / f"partial_g2_{w}.csv") for w in worlds]
    g2_rows = pd.concat(g2_frames, ignore_index=True)
    gap_frames = [pd.read_csv(output / f"partial_gap_{w}.csv") for w in worlds]
    gap_rows = pd.concat(gap_frames, ignore_index=True)
    g3_frames = [pd.read_csv(output / f"partial_g3check_{w}.csv") for w in worlds]
    g3_rows = pd.concat(g3_frames, ignore_index=True)
    offset_gate_payloads = []
    for w in worlds:
        with (output / f"partial_gates_offset_gap_{w}.json").open("r", encoding="utf-8") as handle:
            offset_gate_payloads.append(json.load(handle))

    truth_frames = []
    truth_gate_payloads = []
    for w in worlds:
        for budget in TRUTH_BUDGETS:
            budget_tag = f"{budget:g}"
            path = output / f"partial_truth_{w}_b{budget_tag}.csv"
            if not path.exists():
                raise RuntimeError(f"missing truth partial: {path}")
            truth_frames.append(pd.read_csv(path))
            with (output / f"partial_gates_truth_{w}_b{budget_tag}.json").open(
                "r", encoding="utf-8"
            ) as handle:
                truth_gate_payloads.append(json.load(handle))
    truth_rows = pd.concat(truth_frames, ignore_index=True)

    # ---- completeness checks --------------------------------------------------
    expected_offset_rows = len(worlds) * len(ARM_NAMES)
    if len(offset_rows) != expected_offset_rows:
        raise RuntimeError(f"offset rows {len(offset_rows)} != expected {expected_offset_rows}")
    expected_gap_rows = len(worlds) * 8 * 2 * 16 * len(ARM_NAMES)
    if len(gap_rows) != expected_gap_rows:
        raise RuntimeError(f"gap rows {len(gap_rows)} != expected {expected_gap_rows}")
    expected_truth_rows = len(worlds) * len(TRUTH_BUDGETS) * 8 * 2 * 16 * len(ARM_NAMES)
    if len(truth_rows) != expected_truth_rows:
        raise RuntimeError(f"truth rows {len(truth_rows)} != expected {expected_truth_rows}")

    # =========================================================================
    # G0 POWER (offset, paired-by-world, n=3)
    # =========================================================================
    m4e2 = _load_m4e2_decision()
    baseline_offsets_m4e2 = {
        w: float(m4e2["offset_table"][w]["offset_norm"]) for w in worlds
    }
    mean_baseline_offset = float(np.mean(list(baseline_offsets_m4e2.values())))
    g0_bar = G0_POWER_FRACTION * mean_baseline_offset

    offset_wide = offset_rows.pivot(index="world", columns="arm", values="offset_norm")
    g0_rows = []
    for arm in CANDIDATE_ARMS:
        diffs = (offset_wide["baseline"] - offset_wide[arm]).to_numpy()
        ci = _paired_world_ci(diffs)
        underpowered = bool(ci["half_width"] > g0_bar)
        g0_rows.append(
            {
                "arm": arm,
                "mean_diff_baseline_minus_arm": ci["mean"],
                "half_width": ci["half_width"],
                "bar_12_5pct_of_mean_baseline": g0_bar,
                "underpowered": underpowered,
            }
        )
    g0_any_underpowered = any(row["underpowered"] for row in g0_rows)
    g0 = {
        "statement": (
            "paired-by-world (n=3) CI half-width on the raw offset difference "
            "(baseline - arm) vs 12.5% of the mean M4-E2 baseline offset"
        ),
        "baseline_offsets_m4e2": baseline_offsets_m4e2,
        "mean_baseline_offset": mean_baseline_offset,
        "bar": g0_bar,
        "per_arm": g0_rows,
        "any_underpowered": g0_any_underpowered,
        "equivalence_form": True,
    }

    # =========================================================================
    # G2 CHANNEL LIVENESS
    # =========================================================================
    g2_summary = (
        g2_rows.groupby("arm")[["width", "condition_number"]]
        .agg(["mean", "min", "max"])
    )
    baseline_condition = float(
        g2_rows[g2_rows["arm"] == "baseline"]["condition_number"].mean()
    )
    baseline_width = int(g2_rows[g2_rows["arm"] == "baseline"]["width"].iloc[0])
    g2_arm_rows = []
    for arm in ARM_NAMES:
        if arm == "baseline":
            continue
        scoped = g2_rows[g2_rows["arm"] == arm]
        width = int(scoped["width"].iloc[0])
        cond = float(scoped["condition_number"].mean())
        width_changed = width != baseline_width
        if np.isnan(cond) or np.isnan(baseline_condition):
            cond_rel_change = float("nan")
        else:
            cond_rel_change = abs(cond - baseline_condition) / max(baseline_condition, EPS)
        material = bool(
            width_changed
            or (not np.isnan(cond_rel_change) and cond_rel_change >= G2_CONDITION_MATERIALITY_RATIO)
        )
        g2_arm_rows.append(
            {
                "arm": arm,
                "width": width,
                "baseline_width": baseline_width,
                "width_changed": width_changed,
                "condition_number_mean": cond,
                "baseline_condition_number": baseline_condition,
                "condition_number_relative_change": cond_rel_change,
                "materially_different": material,
            }
        )
    g2 = {
        "statement": (
            "materially different pre-declared as width change OR >=10% relative "
            "change in condition number vs baseline"
        ),
        "per_arm": g2_arm_rows,
        "all_material": bool(all(row["materially_different"] for row in g2_arm_rows)),
        "equivalence_form": True,
    }

    # =========================================================================
    # G3 (already gated per-world at compute time; assemble the summary)
    # =========================================================================
    g3 = {
        "statement": "truth path at budget=1.0 reproduces the gap stage's e_arm_true exactly",
        "max_abs_diff": float(g3_rows["abs_diff"].max()),
        "n_checks": int(len(g3_rows)),
        "tolerance": G3_TOLERANCE,
        "pass": bool(g3_rows["abs_diff"].max() <= G3_TOLERANCE),
    }

    # =========================================================================
    # G1 anchor summary
    # =========================================================================
    g1 = {
        "basis_anchor_max_abs_diff": max(g["basis_anchor_max_abs_diff"] for g in offset_gate_payloads),
        "offset_anchor_max_abs_diff": max(g["offset_anchor_abs_diff"] for g in offset_gate_payloads),
        "gap_anchor_max_abs_diff": max(g["gap_anchor_max_abs_diff"] for g in offset_gate_payloads),
        "leg14_e_orc_true_anchor_max_abs_diff": max(
            g["leg14_e_orc_true_anchor_max_abs_diff"] for g in offset_gate_payloads
        ),
        "tolerance": G1_OFFSET_TOLERANCE,
        "pass": bool(
            max(g["basis_anchor_max_abs_diff"] for g in offset_gate_payloads) <= G1_BASIS_TOLERANCE
            and max(g["offset_anchor_abs_diff"] for g in offset_gate_payloads) <= G1_OFFSET_TOLERANCE
            and max(g["gap_anchor_max_abs_diff"] for g in offset_gate_payloads) <= G1_GAP_TOLERANCE
        ),
    }

    # =========================================================================
    # LEAN (a): offset reduction >= 25%, paired CI excluding zero
    # =========================================================================
    lean_a_rows = []
    for arm in CANDIDATE_ARMS:
        per_world_reduction = {
            w: 1.0 - float(offset_wide.loc[w, arm]) / float(offset_wide.loc[w, "baseline"])
            for w in worlds
        }
        mean_reduction = float(np.mean(list(per_world_reduction.values())))
        diffs = (offset_wide["baseline"] - offset_wide[arm]).to_numpy()
        ci = _paired_world_ci(diffs)
        ci_excludes_zero = bool(ci["ci_lo"] > 0.0)
        held = bool(mean_reduction >= LEAN_A_REDUCTION_BAR and ci_excludes_zero)
        lean_a_rows.append(
            {
                "arm": arm,
                "per_world_reduction": per_world_reduction,
                "mean_reduction": mean_reduction,
                "paired_diff_ci": ci,
                "ci_excludes_zero": ci_excludes_zero,
                "held": held,
            }
        )
    lean_a_any_held = any(row["held"] for row in lean_a_rows)
    lean_a = {
        "statement": (
            ">= 25% offset reduction vs baseline, paired-by-world (n=3) CI "
            "excluding zero, at least one shrinkage or truncation arm"
        ),
        "per_arm": lean_a_rows,
        "held": lean_a_any_held,
    }
    pivot_fires = not lean_a_any_held
    pivot = {
        "registered": (
            "no arm reduces the offset by >=25% with paired CI excluding zero -> "
            "THE SCALE FAMILY IS EXONERATED AS A LEVER"
        ),
        "fires": bool(pivot_fires),
    }

    # =========================================================================
    # LEAN (b): at the offset-minimizing arm, truth recovery improves, BOTH variants
    # =========================================================================
    mean_offset_by_arm = {
        arm: float(offset_wide[arm].mean()) for arm in CANDIDATE_ARMS
    }
    argmin_arm = min(mean_offset_by_arm, key=mean_offset_by_arm.get)

    author_truth = _author_level_truth(truth_rows)
    lean_b_variants = []
    for budget in TRUTH_BUDGETS:
        scoped = author_truth[author_truth["budget"] == budget]
        base_rows = scoped[scoped["arm"] == "baseline"].set_index(["world", "repetition", "author"])
        arm_rows = scoped[scoped["arm"] == argmin_arm].set_index(["world", "repetition", "author"])
        joined = base_rows.join(arm_rows, lsuffix="_baseline", rsuffix="_arm", how="inner")
        diffs = (joined["e_arm_true_baseline"] - joined["e_arm_true_arm"]).to_numpy()
        ci = _paired_author_ci(diffs)
        improves = bool(ci["n"] > 1 and ci["ci_lo"] > 0.0)
        lean_b_variants.append(
            {
                "budget": budget,
                "n_author_reps": int(len(joined)),
                "mean_recovery_error_baseline": float(joined["e_arm_true_baseline"].mean()),
                "mean_recovery_error_arm": float(joined["e_arm_true_arm"].mean()),
                "paired_diff_ci": ci,
                "improves": improves,
            }
        )
    lean_b_held = bool(lean_a_any_held and all(v["improves"] for v in lean_b_variants))
    lean_b = {
        "statement": (
            "at the offset-minimizing candidate arm, truth-referenced recovery "
            "improves over baseline (paired CI excluding zero) under BOTH truth "
            "variants, else MISS"
        ),
        "argmin_offset_arm": argmin_arm,
        "mean_offset_by_arm": mean_offset_by_arm,
        "variants": lean_b_variants,
        "held": lean_b_held,
    }
    cosmetic = bool(lean_a_any_held and not lean_b_held)

    # =========================================================================
    # LEAN (c): identity worse than best regularized arm on offset, every world
    # =========================================================================
    best_arm = argmin_arm
    per_world_c = {}
    for w in worlds:
        identity_offset = float(offset_wide.loc[w, "identity"])
        best_offset = float(offset_wide.loc[w, best_arm])
        per_world_c[w] = {
            "identity_offset": identity_offset,
            "best_regularized_offset": best_offset,
            "identity_worse": bool(identity_offset > best_offset),
        }
    lean_c_held_every_world = bool(all(v["identity_worse"] for v in per_world_c.values()))
    lean_c_held_mean = bool(
        float(offset_wide["identity"].mean()) > float(offset_wide[best_arm].mean())
    )
    lean_c = {
        "statement": (
            "the identity arm is worse than the best regularized (candidate) arm "
            "on the offset metric"
        ),
        "best_regularized_arm": best_arm,
        "per_world": per_world_c,
        "held_every_world_reading": lean_c_held_every_world,
        "held_mean_reading": lean_c_held_mean,
        "held": lean_c_held_every_world,
    }

    verdict = (
        "PIVOT_SCALE_FAMILY_EXONERATED"
        if pivot_fires
        else ("COSMETIC_LEVER_OFFSET_WITHOUT_TRANSFER" if cosmetic else "ACTIONABLE_AND_TRANSFERS" if lean_b_held else "PARTIAL_LEAN_A_ONLY")
    )

    # ---- per-arm summary table --------------------------------------------------
    author_gap = _author_level_gap(gap_rows)
    per_arm_table = []
    for arm in ARM_NAMES:
        offset_by_world = {w: float(offset_wide.loc[w, arm]) for w in worlds}
        gap_scoped = author_gap[author_gap["arm"] == arm]
        truth4 = author_truth[(author_truth["arm"] == arm) & (author_truth["budget"] == 4.0)]
        truth8 = author_truth[(author_truth["arm"] == arm) & (author_truth["budget"] == 8.0)]
        per_arm_table.append(
            {
                "arm": arm,
                "offset_by_world": offset_by_world,
                "offset_mean": float(np.mean(list(offset_by_world.values()))),
                "gap_median": float(gap_scoped["gap"].median()),
                "e_arm_true_1x_median": float(gap_scoped["e_arm_true"].median()),
                "truth_recovery_error_budget4_median": float(truth4["e_arm_true"].median()),
                "truth_recovery_error_budget8_median": float(truth8["e_arm_true"].median()),
            }
        )

    decision = {
        "estimand_id": "SUICA_M4_G1_WHITENING_INTERVENTION",
        "tier": "EXPLORATORY (open-exploration phase)",
        "registered_in": (
            "docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md M4-G1 registration "
            "(2026-08-03, BEFORE run); ledger row M4-G1"
        ),
        "arms": list(ARM_NAMES),
        "candidate_arms_lean_pool": list(CANDIDATE_ARMS),
        "truth_budgets": list(TRUTH_BUDGETS),
        "gates": {"G0": g0, "G1": g1, "G2": g2, "G3": g3},
        "lean_a": lean_a,
        "lean_b": lean_b,
        "lean_c": lean_c,
        "pivot": pivot,
        "cosmetic_finding": cosmetic,
        "verdict": verdict,
        "per_arm_table": per_arm_table,
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only; truth-referenced recovery via "
            "budget-regenerated (4x/8x events) finite panels from the frozen "
            "world law, compared to the analytic D_true; no natural-text, "
            "personality, or clinical claim; no seal, no independent "
            "verification (operator directive 2026-08-01)."
        ),
    }

    output.mkdir(parents=True, exist_ok=True)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    with (output / "gates.json").open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "G0_power": g0,
                "G1_anchor": g1,
                "G2_channel_liveness": g2,
                "G3_truth_path_invariance": g3,
                "offset_gates_per_world": offset_gate_payloads,
                "truth_gates_per_world_budget": truth_gate_payloads,
            },
            handle,
            indent=2,
            sort_keys=True,
            default=str,
        )
        handle.write("\n")
    offset_rows.to_csv(output / "offset_rows.csv", index=False)
    gap_rows.to_csv(output / "gap_rows.csv", index=False)
    truth_rows.to_csv(output / "truth_recovery_rows.csv", index=False)
    g2_rows.to_csv(output / "g2_spectrum_evidence.csv", index=False)
    g3_rows.to_csv(output / "g3_check_rows.csv", index=False)

    print(
        json.dumps(
            {
                "verdict": verdict,
                "g0_any_underpowered": g0_any_underpowered,
                "g1_pass": g1["pass"],
                "g2_all_material": g2["all_material"],
                "g3_pass": g3["pass"],
                "lean_a_held": lean_a_any_held,
                "lean_b_held": lean_b_held,
                "lean_c_held": lean_c_held_every_world,
                "pivot_fires": pivot_fires,
                "cosmetic": cosmetic,
                "argmin_offset_arm": argmin_arm,
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
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "m4_g1_whitening_intervention")
    parser.add_argument("--world", type=str, default=None)
    parser.add_argument("--stage", type=str, choices=("offset_gap", "truth"), default=None)
    parser.add_argument("--budget", type=float, default=None)
    parser.add_argument("--assemble", action="store_true")
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    spec = M4ChartEcologySpec(**config["base_spec"])

    if args.assemble:
        _assemble(args.output)
        return

    if args.world is None or args.stage is None:
        raise SystemExit("--world and --stage are required unless --assemble")
    if args.world not in HIGH_GAP_WORLDS:
        raise SystemExit(f"not a registered high-gap world: {args.world}")

    if args.stage == "offset_gap":
        _run_offset_gap_stage(args.world, config, spec, args.output)
    else:
        if args.budget is None:
            raise SystemExit("--budget is required for --stage truth")
        if args.budget not in TRUTH_BUDGETS:
            raise SystemExit(f"not a registered truth budget: {args.budget}")
        _run_truth_stage(args.world, config, spec, args.budget, args.output)


if __name__ == "__main__":
    main()
