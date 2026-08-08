#!/usr/bin/env python3
"""M4-J1: do the two certified repairs generalize beyond the three worlds
that produced them?

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, "M4-J1
registration" (2026-08-03, BEFORE run); ledger row M4-J1). Machinery is
IMPORTED and REUSED wherever an existing seam exists -- this leg adds NO new
basis-construction or estimator code. It calls, literally and unchanged:
h3._basis_for_h3_arm (deployed, basis_shrinkage_0.20), h4._basis_for_h4_arm
(basis_shrinkage_1.00), g6._resolve_all_params / g6._forced_route_derivative_
for_arm (colstd_alpha_0.10, M4-G6's certified per-column-standardized ridge
repair at alpha=0.10x deployed), g2._whitening_for_c (the c-ladder), and h2's
context/regen caching + `_arm_truth_rows` machinery. The deployed estimator
and basis-construction paths (`suica_core/m4_condition_manifold_estimator.py`,
`suica_core/m4_chart_ecology_estimator.py`) are READ-ONLY throughout.

===========================================================================
WHY THIS LEG EXISTS
===========================================================================
Two repairs are certified but deliberately UNADOPTED:
  - M4-G6: per-column standardization of the hazard design at
    alpha = 0.10 x deployed ridge -- exactly c-invariant (lean a HELD EXACTLY,
    0.0 paired diff), recovery tied-or-better vs the best point fix, scale-free
    interior optimum. Certified only against M4-G3/G4/G5's own D1_WORLDS
    (8 worlds) for TRUTH RECOVERY and C-INVARIANCE, and against M4-G7's
    HIGH_GAP_WORLDS (3 worlds) for DISPLACEMENT (where it was proven, by an
    exact structural identity, to move the discovery objective's frame
    displacement by exactly 0% -- the ridge never enters `context["v2_basis"]`).
  - M4-H3/H4: basis-whitening shrinkage -- safe (recovery does not worsen) to
    ratio 1.0 (45.79% displacement reduction), actively good (recovery
    genuinely improves) to ratio 0.20 (34.66% reduction). Certified ONLY on
    M4-E2's three HIGH_GAP_WORLDS, for both displacement AND recovery.

Adopting either changes a frozen operator, which under F16 creates a NEW
operator needing its own study ID and seal. Before that decision is worth
making, this leg tests whether the repairs generalize to five FRESH worlds
neither repair has ever touched for the metric in question.

===========================================================================
PART 0 -- WORLD SET, ARMS, METRICS (registered)
===========================================================================
World set: `D1_WORLDS` (8 total) = M4-G2's own definition, reused verbatim
(`g2.D1_WORLDS`) -- HIGH_GAP_WORLDS (3: endogenous_creation_expansion,
selection_creation_compensation, source_rotated_feedback) + 5 FRESH_COMPANION_
WORLDS (linear_null_ecology, topology_mismatch, fast_return_equal_marginal,
history_gated_ecology, condition_alias_ecology). The three HIGH_GAP_WORLDS
carry inside as G1 anchors; the five companions are genuinely new territory
for the BASIS-SHRINKAGE repair (H3/H4 never touched them, for either metric)
and for the DISPLACEMENT metric of the G6 repair (G7 only tested 3 worlds
there) -- NOT new territory for the G6 repair's truth-recovery/c-invariance
per se (M4-G3 already extended those to D1_WORLDS as its own working set),
but this leg independently RECOMPUTES them end-to-end rather than reading
G6's file, and is the first place they are decomposed PER WORLD (G6 only ever
reported pooled-across-worlds statistics) and reported jointly with the
basis-shrinkage results under one set of gates.

Arms (4): `deployed` (anchor); `colstd_alpha_0.10` (the G6 repair, literal
reuse of g6's own dispatcher); `basis_shrinkage_0.20` (H3's own actively-good
arm, literal reuse of h3's dispatcher); `basis_shrinkage_1.00` (H4's own
harmless-ceiling arm, literal reuse of h4's dispatcher).

Metrics (registered, exactly three):
 1. Leg 14's displacement gap, `disp_v2` (H2/H3/H4's own PRIMARY definition:
    `quotient_distance(row_norm_swap(oracle_basis, arm_basis), arm_basis)`),
    per (world, repetition, arm). Computed fresh for the three BASIS arms
    (`deployed`, `basis_shrinkage_0.20`, `basis_shrinkage_1.00`) via literal
    calls into h3/h4's own dispatch. For `colstd_alpha_0.10`: NOT
    independently recomputed via a second construction path -- M4-G7 proved,
    structurally, before any compute (Part 0 there), that `disp_v2` is a pure
    function of `context["v2_basis"]` alone and that the ridge never enters
    it; this leg reuses that proof rather than re-deriving it, and verifies
    it operationally each world (one spot check per world: the basis
    `g6._resolve_all_params(context, ingredients, c=1.0)` returns is
    identical to the `deployed`-arm basis to machine precision) rather than
    re-running the full GPA/quotient-distance pipeline a second time on an
    object proven identical. `colstd_alpha_0.10`'s disp_v2 is therefore
    ASSIGNED from `deployed`'s own disp_v2 per (world, repetition) -- disclosed
    plainly, not hidden, and anchored on the 3 HIGH_GAP_WORLDS against M4-G7's
    own persisted `repaired`-arm displacement (which used the identical
    structural argument to reach the identical numbers).
 2. Truth-referenced recovery, M4-F5-style, both TRUTH_BUDGETS = (4.0, 8.0)
    (`e_arm_true`, `leg3._relative_error(d_arm_b, d_true)`). For the three
    BASIS arms: deployed `hazard_ridge`, the arm's own basis, via
    `leg4._forced_route_derivative` (literally `h2._arm_truth_rows`, reused
    unchanged) -- this line's own established convention ("this leg varies
    the basis only, never the estimator's regularization"). For
    `colstd_alpha_0.10`: the DEPLOYED basis (at whichever c is requested) with
    M4-G6's own `treatment="column_standardized"` ridge repair, via
    `g5._forced_route_derivative_columnwise` (literally
    `g6._forced_route_derivative_for_arm`, reused unchanged).
 3. c-invariance of the G6 repair ONLY (`colstd_alpha_0.10`), across
    c in {0.25, 1.0, 4.0} -- the SAME metric-2 truth-recovery machinery,
    evaluated at each c via `g2._whitening_for_c`. The basis-shrinkage arms
    have no registered c-lever in this leg (H3/H4 never varied c; that
    territory is the closed M4-G line's) and are evaluated only at their own
    deployed-scale construction.

--- Registered ambiguity resolution: analysis grain (disclosed, resolved
    BEFORE adjudicating any number) ------------------------------------
The registration's own leans are stated PER WORLD ("in >=75% of the wider
world set", "in ANY world", "in every world") -- a materially DIFFERENT
grain from every prior leg in this line, which pooled reps/authors ACROSS
worlds into one CI per arm. This leg's own grain is therefore forced by its
own leans' wording, not chosen freely: lean (a) is a PAIRED-BY-REPETITION CI
COMPUTED SEPARATELY WITHIN EACH WORLD (n=8 reps per world -- the finest grain
at which a per-world verdict is even defined for a quantity, disp_v2, that
is already per-repetition); leans (b)/(c) are PAIRED-BY-AUTHOR CIs COMPUTED
SEPARATELY WITHIN EACH WORLD (n up to 8 reps x 2 views x 16 authors = 256 per
world, matching this line's own author-grain convention but now partitioned
by world instead of pooled across worlds). This is honestly disclosed as
LESS powerful, per-comparison, than every prior leg's pooled grain -- G0
below states the realized MDE at this grain explicitly, per the second
standing rule, rather than silently inheriting a pooled convention the
registration's own wording does not support.

--- Registered restriction: truth-recovery world set for leans (b)/(c) -----
M4-G2 found (and every leg since, G3-G6, has reused verbatim) that TWO of
the 8 D1_WORLDS (`linear_null_ecology`, `fast_return_equal_marginal`) carry a
pre-existing, world-intrinsic `_relative_error` near-zero-denominator
fragility in their regenerated-truth D_true at these budgets -- unrelated to
any arm or repair, and discovered before this leg existed. `VALID_TRUTH_
WORLDS` (g3.VALID_TRUTH_WORLDS, the SAME 6-world subset, reused verbatim, NOT
re-derived here) is the world set for leans (b)/(c) and their G0 statement.
Lean (a) (displacement, a geometric quotient distance with no such fragility)
uses all 8 D1_WORLDS. This restriction is inherited precedent, not a finding
of this leg -- disclosed prominently rather than silently applied.

===========================================================================
GATES (registered)
===========================================================================
G0 POWER: grain justified above; MDE stated per lean from the prior legs'
own persisted effect levels, before adjudicating.
G1 ANCHOR: on the 3 HIGH_GAP_WORLDS, every arm's every metric reproduces its
persisted source to <=1e-12 -- `deployed`/`basis_shrinkage_0.20` disp_v2 and
truth vs H3's own persisted CSVs (`basis_shrinkage_0.20`) and Leg 14's
persisted `displacement_rows.csv` (`deployed`); `basis_shrinkage_1.00` disp_v2
and truth vs H4's own persisted CSVs; `colstd_alpha_0.10` disp_v2 vs M4-G7's
persisted `repaired`-arm displacement; `colstd_alpha_0.10` truth (all 3 c's)
vs M4-G6's own persisted `truth_recovery_rows.csv`. This is what makes the
five new worlds an EXTENSION rather than a re-derivation.
G2 REPAIR LIVENESS per arm per world: basis arms via h2's own
G2_MATERIALITY_RATIO=0.10 basis-distance-vs-deployed convention (reused
unchanged); `colstd_alpha_0.10` via (i) the realized ridge exactly matching
alpha*deployed_ridge at every world/rep/c (arithmetic identity) and (ii) the
whitening's Frobenius norm scaling exactly linearly with c (the same
algebraic identity M4-G2/M4-G4 already proved and this leg re-verifies per
world rather than assuming).
G3 TRUTH-PATH INVARIANCE: degenerate equality check (h2/h3/h4/g6's own
`_g3_spot_check` pattern), one non-degenerate (rep,view,author) per world,
all 4 logical variants (deployed, shrink_0.20, shrink_1.00) plus all 3 c's of
colstd_alpha_0.10 = 6 checks per world.
G4 MATERIALITY FORM: every gate/lean below is an equivalence or fraction-of-
worlds bound; none is a nil-significance test on a known-nonzero quantity;
compliance stated per gate/lean in the report.
G5 DUAL-WINNER reporting: this leg's arms are pre-registered fixed points,
not a ladder search, so there is no new "winner" to select -- but wherever
the report characterizes "which repair generalizes best" it reports BOTH a
harmless-best and an actively-good-best reading per world, per the seventh
standing rule's spirit, rather than collapsing to one pick.

Chunked execution (process rule -- FOREGROUND, explicit long timeouts, no
background jobs, no monitors): `--world W --stage prep` builds+caches 8
contexts and both budgets' arm-invariant regeneration; `--world W --arm A`
computes disp_v2 (basis arms)/G2 rows/truth rows for one arm in one world;
`--world W --stage colstd` computes `colstd_alpha_0.10`'s truth rows (all 3
c's) and ridge/whitening liveness rows for one world; `--world W --stage g3`
computes the one G3 spot check per world; `--assemble` combines every
partial into gates.json/decision.json. `--smoke` runs a 1-world, 1-rep
correctness+timing check before the full sweep. Every stage is idempotent
(skips if its partial already exists).
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
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_suica_m4_d_dleg_floor_leg4 as leg4  # noqa: E402  bit-exact reuse
import run_suica_m4_d_overspan_control_leg3 as leg3  # noqa: E402
import run_suica_m4_d_direction_anatomy_leg10 as leg10  # noqa: E402
import run_suica_m4_d_perturbation_leg11 as leg11  # noqa: E402
import run_suica_m4_d_displacement_leg14 as leg14  # noqa: E402
import run_suica_m4_g1_whitening_intervention as g1  # noqa: E402  paired-CI helpers
import run_suica_m4_g2_metric_units as g2  # noqa: E402  D1_WORLDS, _whitening_for_c
import run_suica_m4_g3_scale_adaptive as g3  # noqa: E402  VALID_TRUTH_WORLDS
import run_suica_m4_g4_covariant_ridge as g4  # noqa: E402  author/world CI + classify
import run_suica_m4_g6_shape_and_strength as g6  # noqa: E402  the certified G6 repair
import run_suica_m4_h2_basis_normalization as h2  # noqa: E402  context/regen/truth machinery
import run_suica_m4_h3_safe_lever_ladder as h3  # noqa: E402  basis_shrinkage_0.20 dispatch
import run_suica_m4_h4_safe_ceiling as h4  # noqa: E402  basis_shrinkage_1.00 dispatch

from suica_core.m4_chart_ecology_generator import M4ChartEcologySpec  # noqa: E402

# ---------------------------------------------------------------------------
# registered world sets, arms, constants
# ---------------------------------------------------------------------------

D1_WORLDS: tuple[str, ...] = g2.D1_WORLDS                      # 8, registered "wider world set"
HIGH_GAP_WORLDS: tuple[str, ...] = leg11.HIGH_GAP_WORLDS        # 3, G1 anchor worlds (subset of D1_WORLDS)
FRESH_COMPANION_WORLDS: tuple[str, ...] = tuple(w for w in D1_WORLDS if w not in HIGH_GAP_WORLDS)  # 5, genuinely new
assert len(D1_WORLDS) == 8 and len(HIGH_GAP_WORLDS) == 3 and len(FRESH_COMPANION_WORLDS) == 5
assert set(HIGH_GAP_WORLDS) <= set(D1_WORLDS)
VALID_TRUTH_WORLDS: tuple[str, ...] = g3.VALID_TRUTH_WORLDS     # 6, inherited precedent (M4-G2), NOT re-derived
assert set(VALID_TRUTH_WORLDS) <= set(D1_WORLDS) and len(VALID_TRUTH_WORLDS) == 6
EXCLUDED_TRUTH_WORLDS: tuple[str, ...] = tuple(w for w in D1_WORLDS if w not in VALID_TRUTH_WORLDS)
assert len(EXCLUDED_TRUTH_WORLDS) == 2

DEPLOYED_ARM = "deployed"
COLSTD_ARM = "colstd_alpha_0.10"
SHRINK20_ARM = "basis_shrinkage_0.20"
SHRINK100_ARM = "basis_shrinkage_1.00"
BASIS_ARMS: tuple[str, ...] = (DEPLOYED_ARM, SHRINK20_ARM, SHRINK100_ARM)
ARMS: tuple[str, ...] = BASIS_ARMS + (COLSTD_ARM,)
BASIS_REPAIR_ARMS: tuple[str, ...] = (SHRINK20_ARM, SHRINK100_ARM)   # non-deployed basis arms
ALL_REPAIR_ARMS: tuple[str, ...] = (SHRINK20_ARM, SHRINK100_ARM, COLSTD_ARM)  # for lean (b)

ALPHA = 0.10
assert f"colstd_alpha_{ALPHA:.2f}" == COLSTD_ARM
assert COLSTD_ARM in g6.ALPHA_ARM_NAMES

C_LADDER: tuple[float, ...] = (0.25, 1.0, 4.0)
assert C_LADDER == g4.C_LADDER == g6.C_LADDER

TRUTH_BUDGETS: tuple[float, ...] = h2.TRUTH_BUDGETS
assert TRUTH_BUDGETS == (4.0, 8.0)

G1_ANCHOR_TOLERANCE = 1e-12
G3_TOLERANCE = 1e-12
LEAN_A_BAR = 0.25                       # >=25% displacement reduction, this line's own registered bar
LEAN_A_WORLD_FRACTION_BAR = 0.75        # >=75% of the wider world set, THIS leg's own registered bar
RECOVERY_NO_WORSEN_MARGIN = h2.LEAN_C_MARGIN   # 0.02, one-sided "does not worsen"
C_INVARIANCE_MARGIN = g4.LEAN_A_MARGIN         # 0.02, two-sided "c-invariant", G4's own convention
G0_FRACTION_BAR = g4.G0_FRACTION_BAR            # 0.01, half of the 0.02 margins, this line's own convention
G2_MATERIALITY_RATIO = h2.G2_MATERIALITY_RATIO  # 0.10, basis-distance liveness bound

# ---- persisted anchor sources -----------------------------------------------
LEG14_DISPLACEMENT_ROWS_PATH = h2.LEG14_DISPLACEMENT_ROWS_PATH
H3_RESULTS = ROOT / "results" / "m4_h3_safe_lever_ladder"
H3_DISP_ROWS_PATH = H3_RESULTS / "disp_rows.csv"
H3_TRUTH_ROWS_PATH = H3_RESULTS / "truth_recovery_rows.csv"
H4_RESULTS = ROOT / "results" / "m4_h4_safe_ceiling"
H4_DISP_ROWS_PATH = H4_RESULTS / "disp_rows.csv"
H4_TRUTH_ROWS_PATH = H4_RESULTS / "truth_recovery_rows.csv"
G6_RESULTS = ROOT / "results" / "m4_g6_shape_and_strength"
G6_TRUTH_ROWS_PATH = G6_RESULTS / "truth_recovery_rows.csv"
G7_RESULTS = ROOT / "results" / "m4_g7_repair_vs_displacement"
G7_DISPLACEMENT_BY_REP_PATH = G7_RESULTS / "displacement_by_rep.csv"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"required persisted anchor is missing: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


# ---------------------------------------------------------------------------
# basis-arm dispatch: literal reuse of h3/h4's own already-anchored dispatch
# ---------------------------------------------------------------------------


def _basis_for_j1_arm(context: dict[str, Any], arm: str) -> tuple[dict[str, np.ndarray], dict[str, Any], dict[str, Any]]:
    if arm == DEPLOYED_ARM:
        return h3._basis_for_h3_arm(context, h3.DEPLOYED_ARM)
    if arm == SHRINK20_ARM:
        assert SHRINK20_ARM in h3.RATIO_BY_ARM
        return h3._basis_for_h3_arm(context, SHRINK20_ARM)
    if arm == SHRINK100_ARM:
        assert SHRINK100_ARM in h4.RATIO_BY_ARM
        return h4._basis_for_h4_arm(context, SHRINK100_ARM)
    raise ValueError(f"not a registered M4-J1 basis arm: {arm}")


# ---------------------------------------------------------------------------
# stage: prep (contexts + arm-invariant regen cache, per world)
# ---------------------------------------------------------------------------


def _run_prep(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    contexts = h2._contexts_for_world(world, config, spec, output)
    for context in contexts:
        for budget in TRUTH_BUDGETS:
            t0 = time.time()
            h2._regen_for_budget_cached(context, spec, budget, output)
            print(f"[m4j1] prep regen b={budget:g} {world} rep={context['repetition']} ({time.time() - t0:.1f}s)", flush=True)
    print(f"[m4j1] prep stage done: {world} ({time.time() - started:.1f}s total)", flush=True)


# ---------------------------------------------------------------------------
# stage: basis arm (disp_v2 + G2 liveness + truth, one basis arm, one world)
# ---------------------------------------------------------------------------


def _run_basis_arm(world: str, arm: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    partial_path = output / f"partial_disp_{world}_{arm}.csv"
    if partial_path.exists():
        print(f"[m4j1] SKIP (partial exists): {world} {arm}", flush=True)
        return
    contexts = h2._contexts_for_world(world, config, spec, output)

    disp_rows: list[dict[str, Any]] = []
    g2_rows: list[dict[str, Any]] = []
    for context in contexts:
        basis, _, meta = _basis_for_j1_arm(context, arm)
        swap_basis = h2.leg9._row_norm_swap(context["truth"].oracle_basis, basis)
        v2_frame = h2.leg11._stack_frame(basis)
        swap_frame = h2.leg11._stack_frame(swap_basis)
        disp = h2.leg14._quotient_distance(swap_frame, v2_frame)
        disp_rows.append({
            "world": world, "arm": arm, "repetition": context["repetition"],
            "disp_v2": disp, "width": int(basis["calibration"].shape[1]), "meta": json.dumps(meta),
        })
        if arm != DEPLOYED_ARM:
            deployed_basis, _, _ = _basis_for_j1_arm(context, DEPLOYED_ARM)
            deployed_frame = h2.leg11._stack_frame(deployed_basis)
            distance = h2.leg14._quotient_distance(deployed_frame, v2_frame)
            g2_rows.append({"world": world, "arm": arm, "repetition": context["repetition"], "basis_distance_vs_deployed": distance})

    truth_rows: list[dict[str, Any]] = []
    for context in contexts:
        for budget in TRUTH_BUDGETS:
            t0 = time.time()
            regen = h2._regen_for_budget_cached(context, spec, budget, output)
            basis, _, _ = _basis_for_j1_arm(context, arm)
            rows = h2._arm_truth_rows(context, regen, budget, arm, basis)
            truth_rows.extend(rows)
            print(f"[m4j1] truth b={budget:g} {world} {arm} rep={context['repetition']} ({time.time() - t0:.1f}s)", flush=True)

    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(disp_rows).to_csv(partial_path, index=False)
    if g2_rows:
        pd.DataFrame(g2_rows).to_csv(output / f"partial_g2_{world}_{arm}.csv", index=False)
    pd.DataFrame(truth_rows).to_csv(output / f"partial_truth_{world}_{arm}.csv", index=False)
    print(f"[m4j1] basis-arm stage done: {world} {arm} ({time.time() - started:.1f}s total)", flush=True)


# ---------------------------------------------------------------------------
# stage: colstd (colstd_alpha_0.10's own truth rows across the c ladder, one world)
# ---------------------------------------------------------------------------


def _colstd_truth_rows_for_basis(
    context: dict[str, Any], regen: dict[str, Any], budget: float, c: float,
    basis: dict[str, np.ndarray], params: dict[str, Any],
) -> list[dict[str, Any]]:
    """Disclosed near-duplicate of h2._arm_truth_rows, dispatching through
    g6's own column-standardized-ridge machinery (g6._forced_route_derivative_
    for_arm) instead of leg4._forced_route_derivative. Structurally identical
    degenerate-reference handling."""
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
                "arm": COLSTD_ARM, "c": c, "budget": budget, "events": regen["events"], "degenerate_reference": degenerate,
            }
            if degenerate:
                rows.append({**keys, "e_arm_true": np.nan})
                continue
            route = stack["selected_model"]
            calibration_b, selection_b = regen["per_view"][view][author]
            d_true = leg4._true_derivative(truth, author)
            d_arm_b = g6._forced_route_derivative_for_arm(
                calibration_b, selection_b, basis, arm=COLSTD_ARM, model=route,
                params=params, fit_kwargs=fit_kwargs, dims=dims,
            )
            e_arm_true = leg3._relative_error(d_arm_b, d_true)
            rows.append({**keys, "e_arm_true": e_arm_true})
    return rows


def _run_colstd(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    partial_path = output / f"partial_truth_{world}_{COLSTD_ARM}.csv"
    if partial_path.exists():
        print(f"[m4j1] SKIP (partial exists): {world} {COLSTD_ARM}", flush=True)
        return
    contexts = h2._contexts_for_world(world, config, spec, output)

    truth_rows: list[dict[str, Any]] = []
    ridge_rows: list[dict[str, Any]] = []
    disp_identity_rows: list[dict[str, Any]] = []
    for context in contexts:
        ingredients = leg10._freeze_ingredients(context)
        deployed_ridge = float(context["fit_kwargs"]["hazard_ridge"])
        deployed_basis, _, _ = _basis_for_j1_arm(context, DEPLOYED_ARM)
        for c in C_LADDER:
            t0 = time.time()
            resolved, basis, raw_scale, _ = g6._resolve_all_params(context, ingredients, c)
            params = resolved[COLSTD_ARM]
            whitening_c = g2._whitening_for_c(ingredients, c)
            ridge_rows.append({
                "world": world, "repetition": context["repetition"], "c": c,
                "deployed_ridge": deployed_ridge, "alpha": ALPHA,
                "realized_ridge_deployed": float(params["ridge_deployed"]),
                "expected_ridge_deployed": float(ALPHA * deployed_ridge),
                "whitening_fro_norm": float(np.linalg.norm(whitening_c)),
            })
            if c == 1.0:
                gap = max(float(np.max(np.abs(basis[role] - deployed_basis[role]))) for role in h2.ROLES)
                disp_identity_rows.append({"world": world, "repetition": context["repetition"], "basis_vs_deployed_max_abs_diff": gap})
            for budget in TRUTH_BUDGETS:
                regen = h2._regen_for_budget_cached(context, spec, budget, output)
                rows = _colstd_truth_rows_for_basis(context, regen, budget, c, basis, params)
                truth_rows.extend(rows)
            print(f"[m4j1] colstd c={c} {world} rep={context['repetition']} ({time.time() - t0:.1f}s)", flush=True)

    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(truth_rows).to_csv(partial_path, index=False)
    pd.DataFrame(ridge_rows).to_csv(output / f"partial_ridge_{world}.csv", index=False)
    pd.DataFrame(disp_identity_rows).to_csv(output / f"partial_colstd_basis_identity_{world}.csv", index=False)
    print(f"[m4j1] colstd stage done: {world} ({time.time() - started:.1f}s total)", flush=True)


# ---------------------------------------------------------------------------
# stage: g3 (truth-path invariance spot check, one world, all 6 variants)
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
    regen = h2._regen_for_budget(context, spec, 1.0)
    calibration_g, selection_g = regen["per_view"][view][author]

    rows: list[dict[str, Any]] = []
    for arm in BASIS_ARMS:
        basis, _, _ = _basis_for_j1_arm(context, arm)
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
            "world": world, "arm": arm, "c": 1.0, "repetition": rep_idx, "view": view, "author": author,
            "e_arm_true_flatstyle": e_flatstyle, "e_arm_true_regen_budget1": e_regen, "abs_diff": abs(e_flatstyle - e_regen),
        })

    ingredients = leg10._freeze_ingredients(context)
    for c in C_LADDER:
        resolved, basis, _, _ = g6._resolve_all_params(context, ingredients, c)
        params = resolved[COLSTD_ARM]
        d_flatstyle = g6._forced_route_derivative_for_arm(
            calibration_flat, selection_flat, basis, arm=COLSTD_ARM, model=route, params=params, fit_kwargs=fit_kwargs, dims=dims,
        )
        d_regen = g6._forced_route_derivative_for_arm(
            calibration_g, selection_g, basis, arm=COLSTD_ARM, model=route, params=params, fit_kwargs=fit_kwargs, dims=dims,
        )
        e_flatstyle = leg3._relative_error(d_flatstyle, d_true)
        e_regen = leg3._relative_error(d_regen, d_true)
        rows.append({
            "world": world, "arm": COLSTD_ARM, "c": c, "repetition": rep_idx, "view": view, "author": author,
            "e_arm_true_flatstyle": e_flatstyle, "e_arm_true_regen_budget1": e_regen, "abs_diff": abs(e_flatstyle - e_regen),
        })
    return rows


def _run_g3(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    partial_path = output / f"partial_g3_{world}.csv"
    if partial_path.exists():
        print(f"[m4j1] SKIP (partial exists): g3 {world}", flush=True)
        return
    contexts = h2._contexts_for_world(world, config, spec, output)
    rows = _g3_spot_check(world, contexts, spec)
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(partial_path, index=False)
    print(f"[m4j1] g3 stage done: {world} ({time.time() - started:.1f}s total)", flush=True)


# ---------------------------------------------------------------------------
# smoke stage
# ---------------------------------------------------------------------------


def _run_smoke(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    t0 = time.time()
    world_index = {name: index for index, name in enumerate(config["worlds"])}[world]
    expected_for = h2.leg8._expected_geometries_lookup(config)
    seed = h2.leg3._world_seed(int(config["seed"]), 0, world, world_index)
    context = h2.leg4._build_context(world, 0, seed, spec=spec, config=config, expected_geometries=expected_for(world, 0, seed))
    print(f"[m4j1 smoke] context built ({time.time() - t0:.1f}s)", flush=True)

    for arm in BASIS_ARMS:
        t1 = time.time()
        basis, _, meta = _basis_for_j1_arm(context, arm)
        if arm == DEPLOYED_ARM:
            gap = max(float(np.max(np.abs(basis[role] - context["v2_basis"][role]))) for role in h2.ROLES)
            print(f"[m4j1 smoke] deployed basis vs context v2_basis max|diff|={gap:.3e}", flush=True)
            assert gap <= G1_ANCHOR_TOLERANCE, f"deployed basis reconstruction fails G1 anchor: {gap:.3e}"
        print(f"[m4j1 smoke] arm={arm} width={basis['calibration'].shape[1]} meta={meta} ({time.time() - t1:.1f}s)", flush=True)

    t2 = time.time()
    ingredients = leg10._freeze_ingredients(context)
    deployed_basis, _, _ = _basis_for_j1_arm(context, DEPLOYED_ARM)
    for c in C_LADDER:
        resolved, basis, raw_scale, deployed_ridge = g6._resolve_all_params(context, ingredients, c)
        params = resolved[COLSTD_ARM]
        expected_ridge = ALPHA * deployed_ridge
        print(
            f"[m4j1 smoke] colstd c={c} ridge_deployed={params['ridge_deployed']:.6g} expected={expected_ridge:.6g} "
            f"diff={abs(params['ridge_deployed'] - expected_ridge):.3e} whitening_fro={np.linalg.norm(g2._whitening_for_c(ingredients, c)):.4f}",
            flush=True,
        )
        if c == 1.0:
            gap = max(float(np.max(np.abs(basis[role] - deployed_basis[role]))) for role in h2.ROLES)
            print(f"[m4j1 smoke] colstd basis@c=1.0 vs deployed basis max|diff|={gap:.3e}", flush=True)
            assert gap <= G1_ANCHOR_TOLERANCE, f"colstd basis@c=1 fails structural-identity check: {gap:.3e}"
    print(f"[m4j1 smoke] colstd param resolution ({time.time() - t2:.1f}s)", flush=True)

    t3 = time.time()
    regen = h2._regen_for_budget(context, spec, 4.0)
    print(f"[m4j1 smoke] regen budget=4x ({time.time() - t3:.1f}s)", flush=True)

    t4 = time.time()
    basis, _, _ = _basis_for_j1_arm(context, SHRINK20_ARM)
    arm_rows = h2._arm_truth_rows(context, regen, 4.0, SHRINK20_ARM, basis)
    print(f"[m4j1 smoke] basis-arm truth rows n={len(arm_rows)} ({time.time() - t4:.1f}s)", flush=True)

    t5 = time.time()
    resolved, basis_c1, _, _ = g6._resolve_all_params(context, ingredients, 1.0)
    colstd_rows = _colstd_truth_rows_for_basis(context, regen, 4.0, 1.0, basis_c1, resolved[COLSTD_ARM])
    print(f"[m4j1 smoke] colstd truth rows n={len(colstd_rows)} ({time.time() - t5:.1f}s)", flush=True)
    print(f"[m4j1 smoke] TOTAL ({time.time() - t0:.1f}s)", flush=True)


# ---------------------------------------------------------------------------
# CI / classification helpers (paired-by-world-and-grain, per single world)
# ---------------------------------------------------------------------------


def _paired_ci(diffs: np.ndarray) -> dict[str, float]:
    """Generic paired t-CI, identical shape to g1._paired_world_ci /
    g1._paired_author_ci -- reused as a bare function so it can be called on
    ANY grain's difference vector, including a single world's own reps or a
    single world's own authors."""
    diffs = np.asarray(diffs, dtype=float)
    diffs = diffs[np.isfinite(diffs)]
    n = len(diffs)
    mean = float(np.mean(diffs)) if n else float("nan")
    if n < 2:
        return {"n": n, "mean": mean, "se": float("nan"), "ci_lo": float("nan"), "ci_hi": float("nan"), "half_width": float("nan")}
    se = float(np.std(diffs, ddof=1) / np.sqrt(n))
    t_crit = float(stats.t.ppf(0.975, df=n - 1))
    half_width = t_crit * se
    return {"n": n, "mean": mean, "se": se, "ci_lo": mean - half_width, "ci_hi": mean + half_width, "half_width": half_width}


def _classify_one_sided(ci: dict[str, float], margin: float) -> str:
    """WITHIN = does not worsen beyond margin; OUTSIDE = worsens beyond
    margin; matches h2/h3/h4's own one-sided 'does not worsen' convention."""
    if ci["n"] <= 1 or not np.isfinite(ci["ci_lo"]) or not np.isfinite(ci["ci_hi"]):
        return "AMBIGUOUS"
    if ci["ci_hi"] <= margin:
        return "WITHIN"
    if ci["ci_lo"] > margin:
        return "OUTSIDE"
    return "AMBIGUOUS"


def _classify_two_sided(ci: dict[str, float], margin: float) -> str:
    if ci["n"] <= 1 or not np.isfinite(ci["ci_lo"]) or not np.isfinite(ci["ci_hi"]):
        return "AMBIGUOUS"
    if ci["ci_lo"] >= -margin and ci["ci_hi"] <= margin:
        return "WITHIN"
    if ci["ci_lo"] > margin or ci["ci_hi"] < -margin:
        return "OUTSIDE"
    return "AMBIGUOUS"


# ---------------------------------------------------------------------------
# assemble + adjudicate
# ---------------------------------------------------------------------------


def _assemble(output: Path) -> None:
    worlds = list(D1_WORLDS)
    valid_worlds = list(VALID_TRUTH_WORLDS)

    for world in worlds:
        for arm in BASIS_ARMS:
            for stem in ("disp", "truth"):
                path = output / f"partial_{stem}_{world}_{arm}.csv"
                if not path.exists():
                    raise RuntimeError(f"missing partial (world/arm not yet computed): {path}")
        if not (output / f"partial_truth_{world}_{COLSTD_ARM}.csv").exists():
            raise RuntimeError(f"missing colstd truth partial for {world}")
        if not (output / f"partial_ridge_{world}.csv").exists():
            raise RuntimeError(f"missing colstd ridge/liveness partial for {world}")
        if not (output / f"partial_colstd_basis_identity_{world}.csv").exists():
            raise RuntimeError(f"missing colstd basis-identity partial for {world}")
        if not (output / f"partial_g3_{world}.csv").exists():
            raise RuntimeError(f"missing G3 spot check for {world}")

    disp_rows = pd.concat([pd.read_csv(output / f"partial_disp_{w}_{a}.csv") for w in worlds for a in BASIS_ARMS], ignore_index=True)
    g2_rows = pd.concat([pd.read_csv(output / f"partial_g2_{w}_{a}.csv") for w in worlds for a in BASIS_REPAIR_ARMS], ignore_index=True)
    basis_truth_rows = pd.concat([pd.read_csv(output / f"partial_truth_{w}_{a}.csv") for w in worlds for a in BASIS_ARMS], ignore_index=True)
    colstd_truth_rows = pd.concat([pd.read_csv(output / f"partial_truth_{w}_{COLSTD_ARM}.csv") for w in worlds], ignore_index=True)
    ridge_rows = pd.concat([pd.read_csv(output / f"partial_ridge_{w}.csv") for w in worlds], ignore_index=True)
    basis_identity_rows = pd.concat([pd.read_csv(output / f"partial_colstd_basis_identity_{w}.csv") for w in worlds], ignore_index=True)
    g3_rows = pd.concat([pd.read_csv(output / f"partial_g3_{w}.csv") for w in worlds], ignore_index=True)

    expected_disp = len(worlds) * len(BASIS_ARMS) * 8
    if len(disp_rows) != expected_disp:
        raise RuntimeError(f"disp rows {len(disp_rows)} != expected {expected_disp}")
    expected_basis_truth_arm_rows = len(worlds) * 8 * len(TRUTH_BUDGETS) * 2 * 16
    for arm in BASIS_ARMS:
        n = len(basis_truth_rows[basis_truth_rows["arm"] == arm])
        if n != expected_basis_truth_arm_rows:
            raise RuntimeError(f"basis truth rows for {arm}: {n} != expected {expected_basis_truth_arm_rows}")
    expected_colstd_rows = len(worlds) * len(C_LADDER) * len(TRUTH_BUDGETS) * 8 * 2 * 16
    if len(colstd_truth_rows) != expected_colstd_rows:
        raise RuntimeError(f"colstd truth rows {len(colstd_truth_rows)} != expected {expected_colstd_rows}")

    # combine colstd_alpha_0.10's displacement: ASSIGNED from deployed's own
    # disp_v2 (G7's structural-identity proof, reused verbatim), per
    # (world, repetition). Verified live above per world by
    # partial_colstd_basis_identity (basis@c=1.0 == deployed basis).
    deployed_disp = disp_rows[disp_rows["arm"] == DEPLOYED_ARM][["world", "repetition", "disp_v2"]].copy()
    colstd_disp = deployed_disp.copy()
    colstd_disp["arm"] = COLSTD_ARM
    colstd_disp["width"] = disp_rows[disp_rows["arm"] == DEPLOYED_ARM]["width"].to_numpy()
    colstd_disp["meta"] = json.dumps({"assigned_from": "deployed", "justification": "M4-G7 Part 0 structural identity: ridge never enters context['v2_basis']"})
    disp_rows_full = pd.concat([disp_rows, colstd_disp[disp_rows.columns]], ignore_index=True)

    all_truth_rows = pd.concat([basis_truth_rows, colstd_truth_rows], ignore_index=True)

    # ==== structural identity check (colstd_alpha_0.10 basis@c=1.0 == deployed basis) ====
    basis_identity_max = float(basis_identity_rows["basis_vs_deployed_max_abs_diff"].max())
    basis_identity_check = {
        "statement": "colstd_alpha_0.10's basis at c=1.0 (via g6._resolve_all_params) is bit-identical to the deployed basis -- the structural fact (M4-G7 Part 0) that licenses assigning colstd_alpha_0.10's disp_v2 from deployed's own, rather than recomputing a second GPA/quotient-distance pipeline on a provably identical object",
        "n_checks": int(len(basis_identity_rows)), "max_abs_diff": basis_identity_max,
        "tolerance": G1_ANCHOR_TOLERANCE, "pass": bool(basis_identity_max <= G1_ANCHOR_TOLERANCE),
    }

    # ==== G1 ANCHOR (on the 3 HIGH_GAP_WORLDS only) ============================
    anchor_rows_disp: list[dict[str, Any]] = []

    # deployed / basis_shrinkage_0.20 disp_v2 vs Leg14 / H3
    leg14_disp = pd.read_csv(LEG14_DISPLACEMENT_ROWS_PATH)
    h3_disp = pd.read_csv(H3_DISP_ROWS_PATH)
    h4_disp = pd.read_csv(H4_DISP_ROWS_PATH)
    g7_disp = pd.read_csv(G7_DISPLACEMENT_BY_REP_PATH)

    def _anchor_disp(my_arm: str, their_frame: pd.DataFrame, their_arm_col_value: str | None, disp_col: str, source_name: str) -> None:
        mine = disp_rows_full[(disp_rows_full["arm"] == my_arm) & (disp_rows_full["world"].isin(HIGH_GAP_WORLDS))][["world", "repetition", "disp_v2"]]
        theirs = their_frame
        if their_arm_col_value is not None and "arm" in theirs.columns:
            theirs = theirs[theirs["arm"] == their_arm_col_value]
        theirs = theirs[theirs["world"].isin(HIGH_GAP_WORLDS)][["world", "repetition", disp_col]].rename(columns={disp_col: "disp_v2_theirs"})
        joined = mine.merge(theirs, on=["world", "repetition"], how="inner")
        if len(joined) != len(HIGH_GAP_WORLDS) * 8:
            raise RuntimeError(f"G1 disp anchor join for {my_arm} vs {source_name}: {len(joined)} rows != {len(HIGH_GAP_WORLDS) * 8}")
        diff = (joined["disp_v2"] - joined["disp_v2_theirs"]).abs()
        anchor_rows_disp.append({"arm": my_arm, "source": source_name, "n_checks": int(len(joined)), "max_abs_diff": float(diff.max())})

    _anchor_disp(DEPLOYED_ARM, leg14_disp, None, "disp_v2", "leg14_displacement_rows")
    _anchor_disp(SHRINK20_ARM, h3_disp, SHRINK20_ARM, "disp_v2", "h3_disp_rows")
    _anchor_disp(SHRINK100_ARM, h4_disp, SHRINK100_ARM, "disp_v2", "h4_disp_rows")
    _anchor_disp(COLSTD_ARM, g7_disp, "repaired", "disp_v2_leg14_definition", "g7_displacement_by_rep")

    anchor_disp_max = max(r["max_abs_diff"] for r in anchor_rows_disp)

    # truth anchors
    anchor_rows_truth: list[dict[str, Any]] = []

    def _anchor_truth(my_arm: str, their_path: Path, their_arm: str, c_values: tuple[float, ...], source_name: str) -> None:
        their_frame = pd.read_csv(their_path)
        mine = all_truth_rows[(all_truth_rows["arm"] == my_arm) & (all_truth_rows["world"].isin(HIGH_GAP_WORLDS)) & (all_truth_rows["c"].isin(c_values))]
        theirs = their_frame[(their_frame["arm"] == their_arm) & (their_frame["world"].isin(HIGH_GAP_WORLDS)) & (their_frame["c"].isin(c_values))]
        join_keys = ["world", "repetition", "view", "author", "budget", "c"]
        joined = mine.merge(theirs, on=join_keys, suffixes=("_mine", "_theirs"), how="inner")
        expected = len(HIGH_GAP_WORLDS) * 8 * len(TRUTH_BUDGETS) * 2 * 16 * len(c_values)
        if len(joined) != expected:
            raise RuntimeError(f"G1 truth anchor join for {my_arm} vs {source_name}: {len(joined)} rows != {expected}")
        both_nan = joined["e_arm_true_mine"].isna() & joined["e_arm_true_theirs"].isna()
        diff = (joined["e_arm_true_mine"] - joined["e_arm_true_theirs"]).abs()
        diff = diff.where(~both_nan, 0.0)
        if diff.isna().any():
            raise RuntimeError(f"G1 truth anchor for {my_arm} vs {source_name}: NaN mismatch not covered by both_nan mask")
        anchor_rows_truth.append({"arm": my_arm, "source": source_name, "c_values": list(c_values), "n_checks": int(len(joined)), "max_abs_diff": float(diff.max())})

    _anchor_truth(DEPLOYED_ARM, H4_TRUTH_ROWS_PATH, "deployed", (1.0,), "h4_truth_recovery_rows")
    _anchor_truth(SHRINK20_ARM, H3_TRUTH_ROWS_PATH, SHRINK20_ARM, (1.0,), "h3_truth_recovery_rows")
    _anchor_truth(SHRINK100_ARM, H4_TRUTH_ROWS_PATH, SHRINK100_ARM, (1.0,), "h4_truth_recovery_rows")
    _anchor_truth(COLSTD_ARM, G6_TRUTH_ROWS_PATH, COLSTD_ARM, C_LADDER, "g6_truth_recovery_rows")

    anchor_truth_max = max(r["max_abs_diff"] for r in anchor_rows_truth)

    g1_anchor_max = max(anchor_disp_max, anchor_truth_max, basis_identity_max)
    g1_anchor = {
        "statement": "on the 3 HIGH_GAP_WORLDS, every arm's every metric reproduces its persisted source to <=1e-12 -- what makes the 5 FRESH_COMPANION_WORLDS an EXTENSION rather than a re-derivation",
        "tolerance": G1_ANCHOR_TOLERANCE,
        "displacement_anchors": anchor_rows_disp,
        "truth_anchors": anchor_rows_truth,
        "basis_identity_check": basis_identity_check,
        "max_abs_diff_overall": g1_anchor_max,
        "pass": bool(g1_anchor_max <= G1_ANCHOR_TOLERANCE),
    }

    # ==== G2 REPAIR LIVENESS per arm per world ==================================
    deployed_disp_median_by_world = disp_rows_full[disp_rows_full["arm"] == DEPLOYED_ARM].groupby("world")["disp_v2"].median()
    deployed_disp_median_overall = float(disp_rows_full[disp_rows_full["arm"] == DEPLOYED_ARM]["disp_v2"].median())
    g2_basis_by_arm_world: dict[str, dict[str, Any]] = {}
    for arm in BASIS_REPAIR_ARMS:
        for w in worlds:
            scoped = g2_rows[(g2_rows["arm"] == arm) & (g2_rows["world"] == w)]
            median_dist = float(scoped["basis_distance_vs_deployed"].median())
            ref = float(deployed_disp_median_by_world.get(w, deployed_disp_median_overall))
            ratio = median_dist / ref if ref > 0 else float("nan")
            g2_basis_by_arm_world[f"{arm}__{w}"] = {
                "arm": arm, "world": w, "median_basis_distance_vs_deployed": median_dist,
                "ratio_to_deployed_median_disp_v2_this_world": ratio, "live": bool(ratio >= G2_MATERIALITY_RATIO),
            }
    g2_basis_all_live = bool(all(v["live"] for v in g2_basis_by_arm_world.values()))

    ridge_rows["ridge_arith_abs_diff"] = (ridge_rows["realized_ridge_deployed"] - ridge_rows["expected_ridge_deployed"]).abs()
    ridge_arith_max = float(ridge_rows["ridge_arith_abs_diff"].max())
    fro_at_1 = ridge_rows[ridge_rows["c"] == 1.0].set_index(["world", "repetition"])["whitening_fro_norm"]
    fro_ratio_rows = []
    for c in C_LADDER:
        scoped = ridge_rows[ridge_rows["c"] == c].set_index(["world", "repetition"])["whitening_fro_norm"]
        ratio = (scoped / fro_at_1).reset_index()
        ratio["c"] = c
        ratio["expected_ratio"] = c
        ratio["abs_diff_from_c"] = (ratio["whitening_fro_norm"] - c).abs()
        fro_ratio_rows.append(ratio)
    fro_ratio_df = pd.concat(fro_ratio_rows, ignore_index=True)
    fro_ratio_max_diff = float(fro_ratio_df["abs_diff_from_c"].max())
    g2_colstd_liveness = {
        "statement": "colstd_alpha_0.10's realized ridge_deployed matches alpha*deployed_ridge exactly at every (world,rep,c), and the applied whitening's Frobenius norm scales exactly linearly with c relative to c=1.0 (both algebraic identities, re-verified per world rather than assumed)",
        "ridge_arithmetic_max_abs_diff": ridge_arith_max, "ridge_arithmetic_tolerance": G1_ANCHOR_TOLERANCE,
        "ridge_arithmetic_pass": bool(ridge_arith_max <= G1_ANCHOR_TOLERANCE),
        "whitening_fro_norm_ratio_max_abs_diff_from_c": fro_ratio_max_diff, "whitening_fro_norm_tolerance": 1e-8,
        "whitening_fro_norm_pass": bool(fro_ratio_max_diff <= 1e-8),
        "live": bool(ridge_arith_max <= G1_ANCHOR_TOLERANCE and fro_ratio_max_diff <= 1e-8),
    }
    g2_repair_liveness = {
        "basis_arms_statement": "h2's own G2_CONDITION_MATERIALITY_RATIO=0.10 convention, per arm per world: basis distance vs deployed >= 10% of THAT world's own deployed median disp_v2",
        "materiality_ratio": G2_MATERIALITY_RATIO,
        "basis_arms_by_arm_world": g2_basis_by_arm_world,
        "basis_arms_all_live": g2_basis_all_live,
        "colstd_liveness": g2_colstd_liveness,
        "all_live": bool(g2_basis_all_live and g2_colstd_liveness["live"]),
    }

    # ==== G3 TRUTH-PATH INVARIANCE ==============================================
    g3_max = float(g3_rows["abs_diff"].max())
    g3_gate = {
        "statement": "budget=1.0 freshly-regenerated panels reproduce context['flat']-sourced refits exactly, one spot-check (rep,view,author) per world, all 3 basis arms + all 3 c's of colstd_alpha_0.10 (6 variants/world)",
        "max_abs_diff": g3_max, "n_checks": int(len(g3_rows)), "tolerance": G3_TOLERANCE,
        "pass": bool(g3_max <= G3_TOLERANCE),
    }

    # ==== per-world author-grain truth table (for leans b/c) ====================
    usable_truth = all_truth_rows[~all_truth_rows["degenerate_reference"]]
    author_truth = (
        usable_truth.groupby(["world", "repetition", "author", "arm", "c", "budget"])["e_arm_true"].mean().reset_index()
    )

    # ==== LEAN (a): THE REDUCTION GENERALIZES (basis_shrinkage_1.00, all 8 worlds, rep grain) ====
    disp_wide = disp_rows_full.set_index(["world", "repetition", "arm"])["disp_v2"]
    lean_a_by_world: dict[str, Any] = {}
    for w in worlds:
        deployed_vals = np.array([float(disp_wide[(w, r, DEPLOYED_ARM)]) for r in range(8)])
        arm_vals = np.array([float(disp_wide[(w, r, SHRINK100_ARM)]) for r in range(8)])
        reduction = deployed_vals - arm_vals
        ci = _paired_ci(reduction)
        deployed_mean = float(np.mean(deployed_vals))
        reduction_pct = float(np.mean(reduction)) / deployed_mean if deployed_mean else float("nan")
        bar_absolute = LEAN_A_BAR * deployed_mean
        held = bool(reduction_pct >= LEAN_A_BAR and np.isfinite(ci["ci_lo"]) and ci["ci_lo"] > 0.0)
        lean_a_by_world[w] = {
            "world": w, "n_reps": ci["n"], "deployed_mean_disp_v2": deployed_mean,
            "mean_reduction_absolute": ci["mean"], "reduction_pct": reduction_pct,
            "ci_lo": ci["ci_lo"], "ci_hi": ci["ci_hi"], "half_width": ci["half_width"],
            "bar_absolute": bar_absolute,
            "underpowered_vs_bar": bool(np.isfinite(ci["half_width"]) and ci["half_width"] > bar_absolute),
            "clears_25pct_bar": bool(reduction_pct >= LEAN_A_BAR),
            "ci_excludes_zero": bool(np.isfinite(ci["ci_lo"]) and ci["ci_lo"] > 0.0),
            "is_high_gap_anchor_world": w in HIGH_GAP_WORLDS,
            "is_fresh_companion_world": w in FRESH_COMPANION_WORLDS,
            "held": held,
        }
    n_worlds_held = sum(1 for v in lean_a_by_world.values() if v["held"])
    world_fraction_held = n_worlds_held / len(worlds)
    lean_a = {
        "statement": "the ratio-1.0 (basis_shrinkage_1.00) repair achieves >=25% displacement reduction in >=75% of the wider (8-world) set, paired-by-repetition CI (n=8, within each world) excluding zero",
        "grain": "paired-by-repetition, computed separately within each world (n=8 per world)",
        "bar_per_world": LEAN_A_BAR, "world_fraction_bar": LEAN_A_WORLD_FRACTION_BAR,
        "by_world": lean_a_by_world,
        "n_worlds_held": n_worlds_held, "n_worlds_total": len(worlds), "world_fraction_held": world_fraction_held,
        "held": bool(world_fraction_held >= LEAN_A_WORLD_FRACTION_BAR),
    }

    pivot_fires = not lean_a["held"]
    pivot = {
        "registered": "the reduction fails to reach 25% in >=75% of the wider set -> the repairs are WORLD-SET-SPECIFIC; the M4-E2 three-world results stand as scope-limited, no deployment decision arises, and the finding is that the repair's generality was the untested assumption all along",
        "fires": bool(pivot_fires),
    }

    # ==== LEAN (b): SAFETY GENERALIZES (does not worsen in ANY VALID_TRUTH_WORLDS world, either repair) ====
    lean_b_rows: list[dict[str, Any]] = []
    worst_case_by_arm: dict[str, list[str]] = {a: [] for a in ALL_REPAIR_ARMS}
    for arm in ALL_REPAIR_ARMS:
        c_for_arm = 1.0
        for w in valid_worlds:
            for budget in TRUTH_BUDGETS:
                scoped_deployed = author_truth[
                    (author_truth["arm"] == DEPLOYED_ARM) & (author_truth["c"] == 1.0)
                    & (author_truth["budget"] == budget) & (author_truth["world"] == w)
                ].set_index(["repetition", "author"])["e_arm_true"]
                scoped_arm = author_truth[
                    (author_truth["arm"] == arm) & (author_truth["c"] == c_for_arm)
                    & (author_truth["budget"] == budget) & (author_truth["world"] == w)
                ].set_index(["repetition", "author"])["e_arm_true"]
                joined = pd.concat([scoped_arm.rename("arm_val"), scoped_deployed.rename("deployed_val")], axis=1, join="inner")
                diffs = (joined["arm_val"] - joined["deployed_val"]).to_numpy()
                ci = _paired_ci(diffs)
                cls = _classify_one_sided(ci, RECOVERY_NO_WORSEN_MARGIN)
                worsens = cls == "OUTSIDE"
                if worsens:
                    worst_case_by_arm[arm].append(f"{w}@budget={budget:g}")
                lean_b_rows.append({
                    "arm": arm, "world": w, "budget": budget, "n_authors": ci["n"],
                    "mean_diff_arm_minus_deployed": ci["mean"], "ci_lo": ci["ci_lo"], "ci_hi": ci["ci_hi"],
                    "half_width": ci["half_width"], "margin": RECOVERY_NO_WORSEN_MARGIN,
                    "underpowered_vs_g0_bar": bool(np.isfinite(ci["half_width"]) and ci["half_width"] > G0_FRACTION_BAR),
                    "classification": cls, "worsens": bool(worsens),
                })
    lean_b_df = pd.DataFrame(lean_b_rows)
    any_worsening = bool(lean_b_df["worsens"].any())
    worsening_named = {a: v for a, v in worst_case_by_arm.items() if v}
    lean_b = {
        "statement": "recovery does not worsen (equivalence, +/-0.02, one-sided 'does not worsen') in ANY of the 6 VALID_TRUTH_WORLDS, either repair (basis_shrinkage_0.20, basis_shrinkage_1.00, colstd_alpha_0.10), both truth-budget variants -- a single worsening world is named explicitly as a material deployment-risk finding, not averaged away",
        "grain": "paired-by-author, computed separately within each world (n up to 256 per world per budget)",
        "world_scope": "VALID_TRUTH_WORLDS (6 of 8) -- linear_null_ecology and fast_return_equal_marginal excluded, inherited precedent from M4-G2 (pre-existing, world-intrinsic e_relative_error near-zero-denominator fragility, unrelated to any arm or this leg)",
        "excluded_worlds": list(EXCLUDED_TRUTH_WORLDS),
        "margin": RECOVERY_NO_WORSEN_MARGIN,
        "rows": lean_b_rows,
        "any_world_worsens": any_worsening,
        "worsening_worlds_by_arm": worsening_named,
        "held": bool(not any_worsening),
    }

    # ==== LEAN (c): INVARIANCE IS WORLD-INDEPENDENT (colstd_alpha_0.10, per world, c-pairs) ====
    import itertools as _itertools
    lean_c_rows: list[dict[str, Any]] = []
    for w in valid_worlds:
        for budget in TRUTH_BUDGETS:
            for c_lo, c_hi in _itertools.combinations(C_LADDER, 2):
                lo = author_truth[
                    (author_truth["arm"] == COLSTD_ARM) & (author_truth["c"] == c_lo)
                    & (author_truth["budget"] == budget) & (author_truth["world"] == w)
                ].set_index(["repetition", "author"])["e_arm_true"]
                hi = author_truth[
                    (author_truth["arm"] == COLSTD_ARM) & (author_truth["c"] == c_hi)
                    & (author_truth["budget"] == budget) & (author_truth["world"] == w)
                ].set_index(["repetition", "author"])["e_arm_true"]
                joined = pd.concat([lo.rename("lo"), hi.rename("hi")], axis=1, join="inner")
                diffs = (joined["lo"] - joined["hi"]).to_numpy()
                ci = _paired_ci(diffs)
                cls = _classify_two_sided(ci, C_INVARIANCE_MARGIN)
                lean_c_rows.append({
                    "world": w, "budget": budget, "c_lo": c_lo, "c_hi": c_hi, "n_authors": ci["n"],
                    "mean_diff": ci["mean"], "ci_lo": ci["ci_lo"], "ci_hi": ci["ci_hi"], "half_width": ci["half_width"],
                    "margin": C_INVARIANCE_MARGIN,
                    "underpowered_vs_g0_bar": bool(np.isfinite(ci["half_width"]) and ci["half_width"] > G0_FRACTION_BAR),
                    "classification": cls, "exactly_zero": bool(abs(ci["mean"]) < 1e-9),
                })
    lean_c_df = pd.DataFrame(lean_c_rows)
    n_world_checks = lean_c_df.groupby("world").apply(lambda d: bool((d["classification"] == "WITHIN").all())).to_dict()
    n_worlds_hold = sum(1 for v in n_world_checks.values() if v)
    any_outside = bool((lean_c_df["classification"] == "OUTSIDE").any())
    max_abs_mean_diff = float(lean_c_df["mean_diff"].abs().max())
    lean_c = {
        "statement": "the G6 repair's c-invariance (colstd_alpha_0.10, c in {0.25,1.0,4.0}) holds exactly (two-sided equivalence +/-0.02) in EVERY one of the 6 VALID_TRUTH_WORLDS -- testing whether M4-G5's reparameterization argument is a property of the construction (world-independent) or of the three worlds it was demonstrated on",
        "grain": "paired-by-author, computed separately within each world (n up to 256 per world per budget per c-pair)",
        "world_scope": "VALID_TRUTH_WORLDS (6 of 8), same restriction and reason as lean (b)",
        "margin": C_INVARIANCE_MARGIN,
        "rows": lean_c_rows,
        "by_world_all_pairs_within": n_world_checks,
        "n_worlds_hold": n_worlds_hold, "n_worlds_total": len(valid_worlds),
        "any_pair_outside_margin": any_outside,
        "max_abs_mean_diff_across_all_checks": max_abs_mean_diff,
        "held": bool(n_worlds_hold == len(valid_worlds) and not any_outside),
    }

    # ==== G0 POWER (stated per lean, from the prior legs' own persisted effect levels) ====
    g0 = {
        "lean_a": {
            "statement": "target level cited from H4's own persisted harmless-ceiling finding (basis_shrinkage_1.00: 45.79% reduction on a deployed disp_v2 level of ~15-24 units, rep grain n=24 pooled across 3 worlds, CI [7.515,9.025]). This leg's own grain is forced by its leans' PER-WORLD wording to n=8 reps per world -- materially less powerful than H4's pooled n=24. Realized per-world half-widths are reported in lean (a)'s own table; per the second standing rule, any world whose half-width exceeds LEAN_A_BAR*deployed_mean (its own bar_absolute) is UNDERPOWERED at that world, not a clean miss, and is flagged as such rather than silently counted against the 75% bar.",
            "target_reduction_pct": 0.4579, "target_source": "H4 basis_shrinkage_1.00 harmless-ceiling reduction",
            "per_world_n": 8,
        },
        "lean_b": {
            "statement": "target level cited from H3/H4's own established margin (+/-0.02, half-width bar 0.01 = G0_FRACTION_BAR, this line's own convention since M4-G4) at this leg's own per-world author grain (n up to 256 per world per budget, vs the pooled n up to 384-768 every prior leg in this line used). Realized per-(arm,world,budget) half-widths are reported in lean (b)'s own row table; any comparison whose half-width exceeds G0_FRACTION_BAR is flagged UNDERPOWERED there rather than silently adjudicated as a clean WITHIN.",
            "margin": RECOVERY_NO_WORSEN_MARGIN, "power_bar_half_width": G0_FRACTION_BAR, "per_world_author_n_max": 256,
        },
        "lean_c": {
            "statement": "target level cited from M4-G6's own persisted finding: lean (a) HELD EXACTLY (0.0 paired difference, n=745 pooled across all 8 D1_WORLDS, every c-pair, both budgets) -- an algebraic identity, not a statistical result, so this leg expects near-zero mean diffs and correspondingly tight per-world CIs. Realized per-world half-widths reported in lean (c)'s own row table; any exceeding G0_FRACTION_BAR is flagged UNDERPOWERED there.",
            "margin": C_INVARIANCE_MARGIN, "power_bar_half_width": G0_FRACTION_BAR, "per_world_author_n_max": 256,
        },
        "g4_materiality_form_compliance": "every gate above (G1 <=1e-12 exact reproduction; G2 >=10% materiality ratio / exact arithmetic identity; G3 <=1e-12 exact reproduction) and every lean (a: fraction-of-worlds bound on a paired CI; b: one-sided equivalence, +/-0.02; c: two-sided equivalence, +/-0.02) is an equivalence, margin, exactness, or fraction bound -- none is a nil-significance test on a known-nonzero quantity",
    }

    # ==== G5 DUAL-WINNER reporting (per world: harmless-best vs actively-good-best) ====
    dual_winner_by_world: dict[str, Any] = {}
    for w in valid_worlds:
        harmless_arms = []
        actively_good_arms = []
        for arm in ALL_REPAIR_ARMS:
            rows_here = [r for r in lean_b_rows if r["arm"] == arm and r["world"] == w]
            if not rows_here:
                continue
            all_within = all(r["classification"] == "WITHIN" for r in rows_here)
            all_improved = all(r["ci_hi"] < 0.0 for r in rows_here if np.isfinite(r["ci_hi"]))
            if all_within:
                harmless_arms.append(arm)
            if all_improved and len(rows_here) == len(TRUTH_BUDGETS):
                actively_good_arms.append(arm)
        dual_winner_by_world[w] = {"world": w, "harmless_arms": harmless_arms, "actively_good_arms": actively_good_arms}
    g5_dual_winner = {
        "statement": "this leg's 4 arms are pre-registered fixed points, not a ladder search -- there is no new 'winner' to select. Per the seventh standing rule's spirit, wherever this leg characterizes which repair does best per world, it reports BOTH a harmless reading and an actively-good reading rather than collapsing to one pick.",
        "by_world": dual_winner_by_world,
    }

    verdict = "PIVOT_FIRES_WORLD_SET_SPECIFIC" if pivot_fires else "REDUCTION_GENERALIZES"
    if not pivot_fires:
        if lean_b["held"] and lean_c["held"]:
            verdict = "REDUCTION_GENERALIZES__SAFETY_HOLDS__INVARIANCE_WORLD_INDEPENDENT"
        elif not lean_b["held"] and lean_c["held"]:
            verdict = "REDUCTION_GENERALIZES__SAFETY_FAILS_IN_NAMED_WORLD__INVARIANCE_WORLD_INDEPENDENT"
        elif lean_b["held"] and not lean_c["held"]:
            verdict = "REDUCTION_GENERALIZES__SAFETY_HOLDS__INVARIANCE_NOT_WORLD_INDEPENDENT"
        else:
            verdict = "REDUCTION_GENERALIZES__SAFETY_FAILS_IN_NAMED_WORLD__INVARIANCE_NOT_WORLD_INDEPENDENT"

    decision = {
        "estimand_id": "M4-J1",
        "tier": "EXPLORATORY",
        "registered_in": "docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, M4-J1 registration (2026-08-03, BEFORE run)",
        "worlds": worlds, "high_gap_anchor_worlds": list(HIGH_GAP_WORLDS), "fresh_companion_worlds": list(FRESH_COMPANION_WORLDS),
        "valid_truth_worlds": valid_worlds, "excluded_truth_worlds": list(EXCLUDED_TRUTH_WORLDS),
        "arms": list(ARMS), "alpha": ALPHA, "c_ladder": list(C_LADDER), "truth_budgets": list(TRUTH_BUDGETS),
        "gates": {
            "g0_power": g0,
            "g1_anchor": g1_anchor,
            "g2_repair_liveness": g2_repair_liveness,
            "g3_truth_path_invariance": g3_gate,
            "g5_dual_winner": g5_dual_winner,
        },
        "lean_a_reduction_generalizes": lean_a,
        "lean_b_safety_generalizes": lean_b,
        "lean_c_invariance_world_independent": lean_c,
        "pivot": pivot,
        "verdict": verdict,
        "claim_boundary": "EXPLORATORY, synthetic, label-free. Tests generalization of two certified objective-conditioning repairs across a wider synthetic world set. Licenses no claim about any real corpus, construct, person, or diagnosis.",
    }

    gates_out = {
        "g0_power": g0, "g1_anchor": g1_anchor, "g2_repair_liveness": g2_repair_liveness,
        "g3_truth_path_invariance": g3_gate, "g4_materiality_form": g0["g4_materiality_form_compliance"],
        "g5_dual_winner": g5_dual_winner,
    }

    output.mkdir(parents=True, exist_ok=True)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    with (output / "gates.json").open("w", encoding="utf-8") as handle:
        json.dump(gates_out, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")

    disp_rows_full.to_csv(output / "disp_rows.csv", index=False)
    all_truth_rows.to_csv(output / "truth_recovery_rows.csv", index=False)
    author_truth.to_csv(output / "author_level_truth_rows.csv", index=False)
    g2_rows.to_csv(output / "g2_liveness_rows.csv", index=False)
    ridge_rows.to_csv(output / "colstd_ridge_liveness_rows.csv", index=False)
    g3_rows.to_csv(output / "g3_check_rows.csv", index=False)
    lean_b_df.to_csv(output / "lean_b_safety_rows.csv", index=False)
    lean_c_df.to_csv(output / "lean_c_invariance_rows.csv", index=False)
    pd.DataFrame(list(lean_a_by_world.values())).to_csv(output / "lean_a_reduction_rows.csv", index=False)

    print(f"[m4j1] ASSEMBLE done. verdict={verdict} pivot_fires={pivot_fires}", flush=True)
    print(f"[m4j1] lean_a: {n_worlds_held}/{len(worlds)} worlds held (bar {LEAN_A_WORLD_FRACTION_BAR:.0%})", flush=True)
    print(f"[m4j1] lean_b: any_world_worsens={any_worsening} worsening={worsening_named}", flush=True)
    print(f"[m4j1] lean_c: {n_worlds_hold}/{len(valid_worlds)} worlds hold exactly", flush=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "m4_chart_ecology.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "m4_j1_repair_generalization")
    parser.add_argument("--world", type=str, default=None)
    parser.add_argument("--arm", type=str, default=None)
    parser.add_argument("--stage", type=str, default=None, choices=["prep", "colstd", "g3"])
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
    if args.world not in D1_WORLDS:
        raise SystemExit(f"not a registered D1_WORLDS world: {args.world}")

    if args.smoke:
        _run_smoke(args.world, config, spec, args.output)
        return
    if args.stage == "prep":
        _run_prep(args.world, config, spec, args.output)
        return
    if args.stage == "colstd":
        _run_colstd(args.world, config, spec, args.output)
        return
    if args.stage == "g3":
        _run_g3(args.world, config, spec, args.output)
        return
    if args.arm is None:
        raise SystemExit("--arm is required unless --stage prep/colstd/g3 or --smoke or --assemble")
    if args.arm not in BASIS_ARMS:
        raise SystemExit(f"not a registered basis arm: {args.arm} (colstd_alpha_0.10 uses --stage colstd)")
    _run_basis_arm(args.world, args.arm, config, spec, args.output)


if __name__ == "__main__":
    main()
