#!/usr/bin/env python3
"""M4-J3: can the two candidate deployment gates be told apart?

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, "M4-J3
registration" (2026-08-03, BEFORE run); ledger row M4-J3). Machinery is
IMPORTED and REUSED wherever an existing seam exists. This leg writes NO new
basis-construction or estimator code: every basis, every truth row, every
disp_v2 computation is a literal, unchanged call into `j1._basis_for_j1_arm`
(-> `h3._basis_for_h3_arm` / `h4._basis_for_h4_arm` -> `h2._basis_for_arm`),
`h2._arm_truth_rows`, `h2._regen_for_budget`, `leg9._row_norm_swap`,
`leg11._stack_frame`, `leg14._quotient_distance`, `leg4._build_context`,
`leg4._true_derivative_unit_check`, `leg3._world_seed`, `leg3._relative_error`.
The only NEW code this leg writes is: (1) a context-builder that separates
"which mechanism generates this world's dynamics" from "which world's seed
this repetition draws," a disclosed near-duplicate of
`h2._contexts_for_world` that takes the two as independent arguments instead
of coupling them through a single `world` string (Part 0.2 below); (2) a
disclosed near-duplicate of `j1._g3_spot_check` trimmed to the 3 `BASIS_ARMS`
this leg actually uses (this leg never touches `colstd_alpha_0.10`, so
running M4-J1's own colstd G3 branch would be pure waste, not merely reuse);
and (3) the rank-dissociation / threshold-classification bookkeeping this
leg's own leans require, a grain no earlier leg in this line needed because
no earlier leg asked whether two world-level scalars could be pried apart.
The deployed estimator and basis-construction paths
(`suica_core/m4_condition_manifold_estimator.py`,
`suica_core/m4_chart_ecology_estimator.py`) are READ-ONLY throughout.

===========================================================================
WHY THIS LEG EXISTS
===========================================================================
M4-J2 found the basis-shrinkage repair's harm boundary IS predictable from a
pre-application world property, but by TWO discriminators confounded across
the 8 `D1_WORLDS`: baseline recovery competence (Spearman rho=.886 vs benefit,
CI [.185,1.000]) and baseline displacement (rank-separates by an even LARGER
relative gap, 28.4% vs error's 20.5%, though its correlation CI merely
touches zero) both rank-separate the identical two harm worlds. At n=6
neither can be credited over the other. This leg asks directly: can the two
be DISSOCIATED, and if so, which one actually predicts harm?

===========================================================================
PART 0.1 -- WHY MECHANISM/SEED SEPARATION IS THE CHOSEN LEVER (registered,
before any new compute)
===========================================================================
`generate_m4_chart_ecology_world(world=w, spec=spec, seed=s)`
(`suica_core/m4_chart_ecology_generator.py:931-939`) takes `world` (which
dispatch branch of `_condition_panels`/`_mechanism_parameters`/`_path_panel`
runs -- the DYNAMICS) and `seed` (the RNG draw within that branch) as two
INDEPENDENT parameters. `leg3._world_seed(base, repetition, world,
world_index)` is a convenience the calling scripts use to derive one from the
other by a fixed, already-existing formula (`base + repetition*1_000_003 +
offset`, `offset` keyed by `world` name); it is not a constraint the
generator itself imposes. `leg3._world_seed`'s own `matched_groups` table
(pre-existing, used unchanged by every prior leg: `{linear_exogenous_
selection: 101, endogenous_source_partition_matched: 101,
fast_return_equal_marginal: 211, slow_hysteresis_equal_marginal: 211}`)
already demonstrates this split is a live, registered, non-novel feature of
this program's own machinery -- two mechanistically DIFFERENT worlds sharing
one seed family. M4-G2 found (for a DIFFERENT quantity, `offset_norm`) that a
seed-matched pair produces BIT-IDENTICAL values despite differing dynamics,
because that quantity is built only from the reference-calibration
chart-fit. `disp_v2` (this leg's displacement discriminator) is NOT
guaranteed to inherit that property: `oracle_basis` -- half of `disp_v2`'s
own comparison -- is returned directly from `_condition_panels(world=world,
...)`, which DOES branch on `world`, not merely on `seed`. So "does swapping
a world's seed-donor move displacement while leaving its own mechanism's
error-generating behavior intact" is an empirical question this leg answers,
not an assumption it makes -- exactly what G2 DISSOCIATION LIVENESS exists to
check, honestly, before any harm outcome is read.

Fidelity of the construction: `leg4._build_context(world, repetition, seed,
spec=spec, config=config, expected_geometries=EG)`'s `expected_geometries`
argument gates ONLY a post-hoc validation raise (`if expected_geometries is
not None: ... raise if too different`) -- it is read nowhere else in the
function and does not alter the returned context's contents. Passing `None`
(as this leg does for every new world, since no archived V2 battery ran these
exact (mechanism, seed) combinations) is therefore not a fidelity
compromise, only a skipped REDUNDANT cross-check -- confirmed by code
inspection here and, additionally, by a cheap one-repetition self-validation
(Part 0.4 below) that recomputes an EXISTING anchor world through this leg's
own new plumbing and checks it against M4-J1's persisted value.
`_ingredients_for_arm`, `_basis_for_h3_arm`/`_basis_for_h4_arm`,
`_bases_from_whitening`, `_freeze_ingredients`, `_true_derivative`,
`_row_norm_swap`, `_stack_frame`, `_quotient_distance` were all read before
writing this leg and confirmed to operate purely on `context` CONTENTS --
`context["world"]` appears in that call graph only inside labels and error
messages, never as a dispatch key -- so a context whose `world` field names
one catalog mechanism and whose `seed` field was drawn from a different
catalog world's seed family flows through every one of them unmodified.

===========================================================================
PART 0.2 -- REGISTERED WORLD CONSTRUCTION (decided from ALREADY-PERSISTED
M4-J1/M4-J2 numbers alone, before any new compute for this leg ran)
===========================================================================
Two avenues, both used, neither novel machinery:

(A) SEARCH the existing 15-world catalog (`config["worlds"]`) for chart-usable
    worlds outside `D1_WORLDS` (8 of 15 already used). Of the remaining 7:
    `author_leakage`, `evaluation_support_shift`, `hidden_opportunity_source_
    alias`, `response_leakage_circular` are HARD BLOCKED (`chart_refused=True`
    on all 8 archived reps each -- `leg4._build_context` raises unconditionally
    on `chart.refused`, a hard compatibility requirement, not a favorable-
    result exclusion). `linear_exogenous_selection` is HARD BLOCKED for
    baseline-error measurement specifically (degenerate D_true -- `norm(stack
    ["D"]) < FLIP_TOLERANCE` -- on ALL 256 archived (rep,view,author)
    combinations, per M4-G2's own prior finding, confirmed here from the
    archive's `loop_action_geometry` column reading EXACTLY 0.000000 on every
    one of its 8 reps, the identical signature). The two REMAINING chart-usable,
    non-fully-degenerate candidates are BOTH included as found companions:
    `endogenous_source_partition_matched` (seed-matched to
    `linear_exogenous_selection`, offset 101; but its OWN mechanism has
    `truth_creation=1.0` on all 8 archived reps -- creation loop genuinely
    active, unlike its seed partner) and `slow_hysteresis_equal_marginal`
    (seed-matched to `fast_return_equal_marginal`, offset 211; `truth_
    creation=0.0` and `loop_action_geometry` near zero -- even crossing zero on
    2 of 8 archived reps, -0.067 to -0.137 -- on all 8 reps, an a priori
    ANTICIPATED risk of the identical near-zero-denominator `_relative_error`
    pathology M4-G2 found in its seed partner, stated here BEFORE compute and
    checked empirically at Part 0.3/the smoke stage, not assumed either way).

(B) CONSTRUCT two hybrid worlds by crossing MECHANISM and SEED-DONOR across
    the extremes of the two discriminators, read directly from M4-J1's own
    persisted `disp_rows.csv` / `author_level_truth_rows.csv`
    (`deployed` arm, `VALID_TRUTH_WORLDS`, budget=4.0, full precision):
      baseline error:        min = topology_mismatch       (0.3087223...)
                              max = condition_alias_ecology (0.9472805...)
      baseline displacement: min = history_gated_ecology    (7.007661...)
                              max = condition_alias_ecology (22.730981...)
    `hybrid_hi_error_lo_disp`  = mechanism(condition_alias_ecology)
                                 @ seed(history_gated_ecology)
    `hybrid_lo_error_hi_disp`  = mechanism(topology_mismatch)
                                 @ seed(condition_alias_ecology)
    This rule is a parameter-free extremum selection over data that already
    existed before this leg's own registration was written -- no new compute
    informed the choice of which two worlds donate which half of each hybrid.

===========================================================================
PART 0.3 -- REGISTERED THRESHOLD RULE FOR LEAN (c) (fixed now, computed ONLY
from the original eight; the RULE is fixed before any new-world outcome
exists, though which of its two candidate readings is scored is decided by
lean (b)'s own empirical result, not by this leg's authors)
===========================================================================
For whichever discriminator lean (b) crowns the winner, the classification
threshold is the MIDPOINT between the harm-world MAXIMUM and the safe-world
MINIMUM, both read from `VALID_TRUTH_WORLDS` only (the population M4-J2's own
leans (b)/(c) used):
    threshold_error = (harm_max_error + safe_min_error) / 2
    threshold_disp  = (harm_max_disp  + safe_min_disp)  / 2
Classification rule: a world is HARM-predicted if its value on the winning
discriminator is BELOW the threshold (both discriminators' registered harm
direction is "low value -> harm", per M4-J2's own lean (a) direction and the
rank tables). Both thresholds are computed by code that reads ONLY the
`VALID_TRUTH_WORLDS` columns of M4-J1's persisted anchor files -- never the
new worlds' data -- so their NUMERIC VALUE cannot depend on anything this leg
newly computed, regardless of which one lean (b) ends up crowning.

===========================================================================
PART 0.4 -- ORDER OF OPERATIONS (registered, and enforced operationally)
===========================================================================
The dissociation check (G2 + lean a) uses ONLY the `deployed` arm (baseline
error, baseline displacement) on the new worlds. The harm outcome uses the
`basis_shrinkage_0.20`/`basis_shrinkage_1.00` arms. This script's stages are
split so the two cannot be computed out of order by construction:
`--stage deployed_only` never touches a shrinkage arm; `--assemble-
dissociation` reads ONLY anchor files + `deployed_only` partials and writes a
timestamped `dissociation_evidence.json` BEFORE `--stage harm_arms` is ever
invoked in this leg's own execution transcript (verified in the report by
comparing file mtimes). `--stage harm_arms` is a separate, later invocation,
issued only after the dissociation verdict was read.

===========================================================================
GATES (registered)
===========================================================================
G0 POWER: the dissociating-world count is small by construction (this leg
targets exactly 2 purpose-built worlds plus up to 2 found companions); state
plainly what is DETERMINISTIC (a pairwise rank inversion, once both worlds'
deployed-arm values are measured, has no sampling uncertainty) vs SAMPLED (the
harm read on a dissociating world is a paired-by-author CI, exactly as
M4-J1/M4-J2's own per-world grain).
G1 ANCHOR: the eight existing `D1_WORLDS` reproduce M4-J1/M4-J2's persisted
values to <=1e-12 -- read directly (identity by construction, matching
M4-J2's own precedent for these same two discriminators) from M4-J1's
`disp_rows.csv`/`author_level_truth_rows.csv`/`lean_b_safety_rows.csv`, PLUS
a one-repetition self-validation of this leg's own new context-builder
against M4-J1's persisted `history_gated_ecology` repetition-0 value.
G2 DISSOCIATION LIVENESS: the constructed/found worlds' two discriminators
must genuinely rank OPPOSITELY, demonstrated (Part 0.4) before any harm
outcome is read.
G3 TRUTH-PATH INVARIANCE: degenerate equality check, `j1._g3_spot_check`'s
own method, trimmed to `BASIS_ARMS`.
G4 MATERIALITY FORM: every gate/lean below is an equivalence, exactness,
rank-gap, or CI-exclusion bound; compliance stated per gate in the report.
G6 MOTIVATING-FACT VERIFICATION: every factual claim this registration cites
(including the eight-world displacement table `18.22/16.93/18.61/22.73/
18.33/7.01/18.69/13.18`) is re-derived from the persisted artifacts at full
precision and reported, per the eighth standing rule.

Chunked execution (process rule -- FOREGROUND, explicit long timeouts, no
background jobs, no monitors; internal concurrency INSIDE one foreground call
via shell `&`/`wait`, matching M4-J1's own established precedent, is used for
the expensive `prep` stage only): `--stage smoke_new --label {L,all}` builds
repetition 0 only, for a cheap feasibility+degeneracy check; `--stage prep
--label {L,all}` builds all 8 repetitions + both truth-budget regenerations;
`--stage deployed_only --label {L,all}` computes ONLY the `deployed` arm's
disp_v2 + truth rows; `--stage g1_selfcheck` runs the one-repetition
new-plumbing self-validation; `--assemble-dissociation` computes G2/lean(a)
from anchor files + `deployed_only` partials ONLY and halts the leg there if
dissociation is not achieved; `--stage harm_arms --label {L,all}` computes the
two shrinkage arms' disp_v2 + truth rows (only invoked after the dissociation
verdict is read); `--stage g3 --label {L,all}` runs the trimmed G3 spot check;
`--assemble` combines everything and adjudicates. Every stage is idempotent
(skips if its partial already exists).
"""
from __future__ import annotations

import argparse
import json
import pickle
import sys
import time
from datetime import datetime, timezone
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

import run_suica_m4_d_overspan_control_leg3 as leg3  # noqa: E402  world seed, relative error
import run_suica_m4_d_dleg_floor_leg4 as leg4  # noqa: E402  context build, true derivative
import run_suica_m4_d_bias_variance_leg9 as leg9  # noqa: E402  row-norm swap
import run_suica_m4_d_direction_anatomy_leg10 as leg10  # noqa: E402  freeze ingredients (unused directly, kept for parity/debug)
import run_suica_m4_d_perturbation_leg11 as leg11  # noqa: E402  stacked-frame quotient machinery
import run_suica_m4_d_displacement_leg14 as leg14  # noqa: E402  GPA quotient distance
import run_suica_m4_h2_basis_normalization as h2  # noqa: E402  regen + truth-rows machinery
import run_suica_m4_h3_safe_lever_ladder as h3  # noqa: E402  basis_shrinkage dispatch
import run_suica_m4_h4_safe_ceiling as h4  # noqa: E402  basis_shrinkage_1.00 dispatch
import run_suica_m4_j1_repair_generalization as j1  # noqa: E402  arms, world sets, CI helpers
import run_suica_m4_j2_harm_boundary as j2  # noqa: E402  HARM_WORLDS / SAFE_WORLDS

from suica_core.m4_chart_ecology_generator import M4ChartEcologySpec  # noqa: E402

_ = h3, h4, leg10  # imported for dispatch-chain completeness / debug parity; referenced via j1/h2 wrappers below

# ---------------------------------------------------------------------------
# registered constants -- literal reuse of M4-J1/M4-J2's own definitions
# ---------------------------------------------------------------------------

ROLES = leg11.ROLES
D1_WORLDS: tuple[str, ...] = j1.D1_WORLDS                          # 8, anchor
HIGH_GAP_WORLDS: tuple[str, ...] = j1.HIGH_GAP_WORLDS               # 3
FRESH_COMPANION_WORLDS: tuple[str, ...] = j1.FRESH_COMPANION_WORLDS  # 5
VALID_TRUTH_WORLDS: tuple[str, ...] = j1.VALID_TRUTH_WORLDS         # 6
EXCLUDED_TRUTH_WORLDS: tuple[str, ...] = j1.EXCLUDED_TRUTH_WORLDS   # 2
HARM_WORLDS: tuple[str, ...] = j2.HARM_WORLDS                       # 2
SAFE_WORLDS: tuple[str, ...] = j2.SAFE_WORLDS                       # 4

DEPLOYED_ARM = j1.DEPLOYED_ARM
SHRINK20_ARM = j1.SHRINK20_ARM
SHRINK100_ARM = j1.SHRINK100_ARM
BASIS_ARMS: tuple[str, ...] = j1.BASIS_ARMS                        # (deployed, shrink20, shrink100)
TRUTH_BUDGETS: tuple[float, ...] = j1.TRUTH_BUDGETS                 # (4.0, 8.0)
PRIMARY_BUDGET = 4.0
COMPANION_BUDGET = 8.0
PRIMARY_SHRINK_ARM = SHRINK100_ARM
COMPANION_SHRINK_ARM = SHRINK20_ARM

G1_ANCHOR_TOLERANCE = 1e-12
G3_TOLERANCE = 1e-12
RECOVERY_NO_WORSEN_MARGIN = j1.RECOVERY_NO_WORSEN_MARGIN            # 0.02
G0_FRACTION_BAR = j1.G0_FRACTION_BAR                                # 0.01

J1_RESULTS = ROOT / "results" / "m4_j1_repair_generalization"
J1_DISP_ROWS_PATH = J1_RESULTS / "disp_rows.csv"
J1_AUTHOR_TRUTH_PATH = J1_RESULTS / "author_level_truth_rows.csv"
J1_LEAN_B_PATH = J1_RESULTS / "lean_b_safety_rows.csv"

# ---------------------------------------------------------------------------
# Part 0.2 -- registered new-world construction (see docstring)
# ---------------------------------------------------------------------------

NEW_WORLDS: dict[str, dict[str, str]] = {
    "hybrid_hi_error_lo_disp": {
        "mechanism_world": "condition_alias_ecology",
        "seed_world": "history_gated_ecology",
        "kind": "constructed",
        "predicted": "HIGH baseline error, LOW baseline displacement",
    },
    "hybrid_lo_error_hi_disp": {
        "mechanism_world": "topology_mismatch",
        "seed_world": "condition_alias_ecology",
        "kind": "constructed",
        "predicted": "LOW baseline error, HIGH baseline displacement",
    },
    "found_endogenous_source_partition_matched": {
        "mechanism_world": "endogenous_source_partition_matched",
        "seed_world": "endogenous_source_partition_matched",
        "kind": "found",
        "predicted": "unknown a priori -- searched, not constructed",
    },
    "found_slow_hysteresis_equal_marginal": {
        "mechanism_world": "slow_hysteresis_equal_marginal",
        "seed_world": "slow_hysteresis_equal_marginal",
        "kind": "found",
        "predicted": "unknown a priori; ANTICIPATED risk of near-zero-denominator truth pathology (loop_action_geometry near/crossing zero on all 8 archived reps, matching its seed-partner fast_return_equal_marginal's own known pathology)",
    },
}
NEW_WORLD_LABELS: tuple[str, ...] = tuple(NEW_WORLDS.keys())
CONSTRUCTED_LABELS: tuple[str, ...] = tuple(k for k, v in NEW_WORLDS.items() if v["kind"] == "constructed")
FOUND_LABELS: tuple[str, ...] = tuple(k for k, v in NEW_WORLDS.items() if v["kind"] == "found")

SELFCHECK_WORLD = "history_gated_ecology"
SELFCHECK_REP = 0


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"required persisted anchor is missing: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Part 0.1 -- context builder that separates mechanism from seed-donor
# (disclosed near-duplicate of h2._contexts_for_world, cache-keyed by LABEL
# rather than by world name, precisely so a hybrid whose mechanism_world
# equals an existing catalog world's name never collides in the cache with
# that world's own native (mechanism==seed) entry)
# ---------------------------------------------------------------------------


def _cache_dir(output: Path) -> Path:
    path = output / "_context_cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _world_index_map(config: dict[str, Any]) -> dict[str, int]:
    return {name: index for index, name in enumerate(config["worlds"])}


def _hybrid_seed(config: dict[str, Any], seed_world: str, repetition: int) -> int:
    idx = _world_index_map(config)[seed_world]
    return leg3._world_seed(int(config["seed"]), repetition, seed_world, idx)


def _build_labeled_context(
    label: str, mechanism_world: str, seed_world: str, repetition: int,
    config: dict[str, Any], spec: M4ChartEcologySpec,
) -> dict[str, Any]:
    seed = _hybrid_seed(config, seed_world, repetition)
    context = leg4._build_context(
        mechanism_world, repetition, seed, spec=spec, config=config, expected_geometries=None,
    )
    unit_gap = leg4._true_derivative_unit_check(
        context["truth"], context["flat"][("train", 0)][0]["response_next"].shape[1],
    )
    if unit_gap > 1e-10:
        raise RuntimeError(f"analytic D_true fails the unit check on {label} ({mechanism_world}@seed({seed_world})) rep {repetition}: {unit_gap:.3e}")
    context["unit_gap"] = unit_gap
    context["label"] = label
    context["seed_world"] = seed_world
    context["mechanism_world"] = mechanism_world
    return context


def _contexts_for_label(label: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> list[dict[str, Any]]:
    """Builds up to `repetitions` contexts for a label. MECHANICAL FINDING,
    disclosed here and in the report (discovered during Part 0.2 world
    construction, BEFORE any dissociation check or harm read ran): a
    mechanism/seed-donor combination can hit `chart.refused` at a SPECIFIC
    repetition even when neither donor world ever refuses across its own 8
    native repetitions (topology_mismatch's mechanism @ condition_alias_
    ecology's seed family refuses at repetition 4 specifically). This was an
    ANTICIPATED possibility (Part 0.1 states the construction's fidelity is
    empirical, not assumed) but its SPECIFIC location was not predictable in
    advance. Per-repetition refusal is caught and the repetition is SKIPPED
    (not the whole label) -- a deterministic, outcome-blind response to a
    hard compatibility constraint the generator itself imposes, exactly
    analogous to M4-G2's own precedent of excluding a specific degenerate
    world rather than silently forcing a fit. The skip is persisted to
    `skipped_repetitions_<label>.json` for full disclosure; every downstream
    computation operates on however many contexts were actually built (never
    hardcodes 8), so this degrades gracefully to n=7 (or fewer) reps for the
    affected label alone."""
    cache_path = _cache_dir(output) / f"contexts_{label}.pkl"
    if cache_path.exists():
        with cache_path.open("rb") as handle:
            return pickle.load(handle)
    spec_info = NEW_WORLDS[label]
    mechanism_world = spec_info["mechanism_world"]
    seed_world = spec_info["seed_world"]
    repetitions = int(config["repetitions"])
    contexts = []
    skipped: list[dict[str, Any]] = []
    for repetition in range(repetitions):
        started = time.time()
        try:
            context = _build_labeled_context(label, mechanism_world, seed_world, repetition, config, spec)
        except RuntimeError as exc:
            if "chart refused" not in str(exc):
                raise
            print(f"[m4j3] CHART REFUSED, SKIPPING rep: {label} (mech={mechanism_world} seed<-{seed_world}) rep={repetition}: {exc}", flush=True)
            skipped.append({"label": label, "mechanism_world": mechanism_world, "seed_world": seed_world, "repetition": repetition, "reason": str(exc)})
            continue
        contexts.append(context)
        print(f"[m4j3] context {label} (mech={mechanism_world} seed<-{seed_world}) rep={repetition} ({time.time() - started:.1f}s)", flush=True)
    if not contexts:
        raise RuntimeError(f"_contexts_for_label({label}): every repetition refused; this label is INFEASIBLE, not merely reduced-n")
    if skipped:
        with (_cache_dir(output) / f"skipped_repetitions_{label}.json").open("w", encoding="utf-8") as handle:
            json.dump(skipped, handle, indent=2, sort_keys=True, default=str)
            handle.write("\n")
    with cache_path.open("wb") as handle:
        pickle.dump(contexts, handle)
    return contexts


def _regen_for_budget_cached_label(context: dict[str, Any], spec: M4ChartEcologySpec, budget: float, output: Path, label: str) -> dict[str, Any]:
    cache_dir = _cache_dir(output)
    cache_path = cache_dir / f"regen_{label}_r{context['repetition']}_b{budget:g}.pkl"
    if cache_path.exists():
        with cache_path.open("rb") as handle:
            return pickle.load(handle)
    regen = h2._regen_for_budget(context, spec, budget)  # pure compute, reused unchanged
    with cache_path.open("wb") as handle:
        pickle.dump(regen, handle)
    return regen


def _disp_v2_for_context(context: dict[str, Any], arm: str) -> tuple[float, int, dict[str, Any]]:
    """Literal reuse of j1._basis_for_j1_arm's dispatch plus the identical
    row-norm-swap / stacked-frame / quotient-distance sequence j1._run_basis_arm
    uses (run_suica_m4_j1_repair_generalization.py:321-325) -- disclosed
    near-duplicate because that logic lives inside a per-world loop there,
    not exposed as a standalone function."""
    basis, _, meta = j1._basis_for_j1_arm(context, arm)
    swap_basis = leg9._row_norm_swap(context["truth"].oracle_basis, basis)
    v2_frame = leg11._stack_frame(basis)
    swap_frame = leg11._stack_frame(swap_basis)
    disp = leg14._quotient_distance(swap_frame, v2_frame)
    width = int(basis["calibration"].shape[1])
    return float(disp), width, meta


# ---------------------------------------------------------------------------
# stage: smoke_new (repetition 0 only, feasibility + degeneracy check)
# ---------------------------------------------------------------------------


def _run_smoke_new(label: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    spec_info = NEW_WORLDS[label]
    t0 = time.time()
    context = _build_labeled_context(label, spec_info["mechanism_world"], spec_info["seed_world"], 0, config, spec)
    print(f"[m4j3 smoke] {label}: context built OK ({time.time() - t0:.1f}s), chart NOT refused (else this would have raised)", flush=True)

    d_true_norms = []
    n_degenerate = 0
    n_total = 0
    for view in ("train", "test"):
        for author in range(context["authors"]):
            stack = context["oracle_stacks"][view][author]
            n_total += 1
            norm = float(np.linalg.norm(stack["D"]))
            if norm < leg4.FLIP_TOLERANCE:
                n_degenerate += 1
            d_true_norms.append(norm)
    arr = np.array(d_true_norms)
    print(
        f"[m4j3 smoke] {label}: D_true norm over {n_total} (view,author) combos: "
        f"min={arr.min():.6g} median={np.median(arr):.6g} max={arr.max():.6g} "
        f"n_degenerate(<{leg4.FLIP_TOLERANCE:g})={n_degenerate}/{n_total}",
        flush=True,
    )
    disp, width, _ = _disp_v2_for_context(context, DEPLOYED_ARM)
    print(f"[m4j3 smoke] {label}: rep0 deployed disp_v2={disp:.6f} width={width}", flush=True)
    print(f"[m4j3 smoke] {label}: TOTAL ({time.time() - t0:.1f}s)", flush=True)


# ---------------------------------------------------------------------------
# stage: g1_selfcheck (new plumbing, trivial hybrid == an existing anchor world)
# ---------------------------------------------------------------------------


def _run_g1_selfcheck(config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    t0 = time.time()
    context = _build_labeled_context(f"selfcheck_{SELFCHECK_WORLD}", SELFCHECK_WORLD, SELFCHECK_WORLD, SELFCHECK_REP, config, spec)
    disp, width, _ = _disp_v2_for_context(context, DEPLOYED_ARM)

    j1_disp = pd.read_csv(J1_DISP_ROWS_PATH)
    row = j1_disp[(j1_disp["arm"] == DEPLOYED_ARM) & (j1_disp["world"] == SELFCHECK_WORLD) & (j1_disp["repetition"] == SELFCHECK_REP)]
    if len(row) != 1:
        raise RuntimeError(f"g1_selfcheck: expected exactly 1 M4-J1 row for {SELFCHECK_WORLD} rep {SELFCHECK_REP}, got {len(row)}")
    j1_value = float(row["disp_v2"].iloc[0])
    j1_width = int(row["width"].iloc[0])
    abs_diff = abs(disp - j1_value)

    regen = h2._regen_for_budget(context, spec, PRIMARY_BUDGET)
    truth_rows = h2._arm_truth_rows(context, regen, PRIMARY_BUDGET, DEPLOYED_ARM, j1._basis_for_j1_arm(context, DEPLOYED_ARM)[0])
    my_truth = pd.DataFrame(truth_rows)

    j1_truth = pd.read_csv(J1_AUTHOR_TRUTH_PATH)  # this is author-MEAN; need row-level for an exact per-row anchor -> use disp-only as the primary selfcheck, truth as a companion mean check
    j1_truth_scoped = j1_truth[
        (j1_truth["world"] == SELFCHECK_WORLD) & (j1_truth["repetition"] == SELFCHECK_REP)
        & (j1_truth["arm"] == DEPLOYED_ARM) & (j1_truth["c"] == 1.0) & (j1_truth["budget"] == PRIMARY_BUDGET)
    ]
    my_truth_mean_by_author = my_truth.groupby("author")["e_arm_true"].mean()
    j1_truth_mean_by_author = j1_truth_scoped.set_index("author")["e_arm_true"]
    joined = pd.concat([my_truth_mean_by_author.rename("mine"), j1_truth_mean_by_author.rename("theirs")], axis=1, join="inner")
    truth_abs_diff = (joined["mine"] - joined["theirs"]).abs()
    truth_max_abs_diff = float(truth_abs_diff.max()) if len(truth_abs_diff) else float("nan")

    result = {
        "statement": "this leg's OWN new context-builder (_build_labeled_context), invoked with mechanism_world==seed_world==an EXISTING D1_WORLDS anchor world, must reproduce M4-J1's persisted value for that exact (world, repetition) -- validates that passing expected_geometries=None does not compromise fidelity and that the mechanism/seed-donor split correctly degenerates to the ordinary case when the two arguments coincide",
        "world": SELFCHECK_WORLD, "repetition": SELFCHECK_REP,
        "disp_v2_mine": disp, "disp_v2_j1_persisted": j1_value, "disp_v2_abs_diff": abs_diff,
        "width_mine": width, "width_j1_persisted": j1_width, "width_match": bool(width == j1_width),
        "disp_v2_tolerance": G1_ANCHOR_TOLERANCE, "disp_v2_pass": bool(abs_diff <= G1_ANCHOR_TOLERANCE),
        "truth_e_arm_true_max_abs_diff_by_author": truth_max_abs_diff, "truth_n_authors_checked": int(len(joined)),
        "truth_tolerance": G1_ANCHOR_TOLERANCE, "truth_pass": bool(truth_max_abs_diff <= G1_ANCHOR_TOLERANCE),
        "seconds": time.time() - t0,
    }
    output.mkdir(parents=True, exist_ok=True)
    with (output / "g1_selfcheck.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    print(f"[m4j3] g1_selfcheck: disp_v2 abs_diff={abs_diff:.3e} truth max_abs_diff={truth_max_abs_diff:.3e} ({time.time() - t0:.1f}s)", flush=True)


# ---------------------------------------------------------------------------
# stage: prep (8 contexts + both-budget regen, one label)
# ---------------------------------------------------------------------------


def _run_prep(label: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    contexts = _contexts_for_label(label, config, spec, output)
    for context in contexts:
        for budget in TRUTH_BUDGETS:
            t0 = time.time()
            _regen_for_budget_cached_label(context, spec, budget, output, label)
            print(f"[m4j3] prep regen b={budget:g} {label} rep={context['repetition']} ({time.time() - t0:.1f}s)", flush=True)
    print(f"[m4j3] prep stage done: {label} ({time.time() - started:.1f}s total)", flush=True)


# ---------------------------------------------------------------------------
# stage: deployed_only (disp_v2 + truth rows, deployed arm ONLY -- this is the
# dissociation-relevant compute; it never touches a shrinkage arm)
# ---------------------------------------------------------------------------


def _run_deployed_only(label: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    disp_path = output / f"partial_deployed_disp_{label}.csv"
    truth_path = output / f"partial_deployed_truth_{label}.csv"
    if disp_path.exists() and truth_path.exists():
        print(f"[m4j3] SKIP (partials exist): deployed_only {label}", flush=True)
        return
    contexts = _contexts_for_label(label, config, spec, output)

    disp_rows: list[dict[str, Any]] = []
    for context in contexts:
        disp, width, meta = _disp_v2_for_context(context, DEPLOYED_ARM)
        disp_rows.append({
            "label": label, "world": context["mechanism_world"], "seed_world": context["seed_world"],
            "arm": DEPLOYED_ARM, "repetition": context["repetition"], "disp_v2": disp, "width": width, "meta": json.dumps(meta),
        })

    truth_rows: list[dict[str, Any]] = []
    for context in contexts:
        basis, _, _ = j1._basis_for_j1_arm(context, DEPLOYED_ARM)
        for budget in TRUTH_BUDGETS:
            t0 = time.time()
            regen = _regen_for_budget_cached_label(context, spec, budget, output, label)
            rows = h2._arm_truth_rows(context, regen, budget, DEPLOYED_ARM, basis)
            for row in rows:
                row["label"] = label
                row["world"] = context["mechanism_world"]
                row["seed_world"] = context["seed_world"]
            truth_rows.extend(rows)
            print(f"[m4j3] deployed_only truth b={budget:g} {label} rep={context['repetition']} ({time.time() - t0:.1f}s)", flush=True)

    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(disp_rows).to_csv(disp_path, index=False)
    pd.DataFrame(truth_rows).to_csv(truth_path, index=False)
    print(f"[m4j3] deployed_only stage done: {label} ({time.time() - started:.1f}s total)", flush=True)


# ---------------------------------------------------------------------------
# stage: harm_arms (basis_shrinkage_0.20 / 1.00 -- disp_v2 + truth rows)
# ---------------------------------------------------------------------------


def _run_harm_arms(label: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    contexts = _contexts_for_label(label, config, spec, output)
    for arm in (SHRINK20_ARM, SHRINK100_ARM):
        disp_path = output / f"partial_harm_disp_{label}_{arm}.csv"
        truth_path = output / f"partial_harm_truth_{label}_{arm}.csv"
        if disp_path.exists() and truth_path.exists():
            print(f"[m4j3] SKIP (partials exist): harm_arms {label} {arm}", flush=True)
            continue
        disp_rows: list[dict[str, Any]] = []
        for context in contexts:
            disp, width, meta = _disp_v2_for_context(context, arm)
            disp_rows.append({
                "label": label, "world": context["mechanism_world"], "seed_world": context["seed_world"],
                "arm": arm, "repetition": context["repetition"], "disp_v2": disp, "width": width, "meta": json.dumps(meta),
            })
        truth_rows: list[dict[str, Any]] = []
        for context in contexts:
            basis, _, _ = j1._basis_for_j1_arm(context, arm)
            for budget in TRUTH_BUDGETS:
                t0 = time.time()
                regen = _regen_for_budget_cached_label(context, spec, budget, output, label)
                rows = h2._arm_truth_rows(context, regen, budget, arm, basis)
                for row in rows:
                    row["label"] = label
                    row["world"] = context["mechanism_world"]
                    row["seed_world"] = context["seed_world"]
                truth_rows.extend(rows)
                print(f"[m4j3] harm_arms truth b={budget:g} {label} {arm} rep={context['repetition']} ({time.time() - t0:.1f}s)", flush=True)
        output.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(disp_rows).to_csv(disp_path, index=False)
        pd.DataFrame(truth_rows).to_csv(truth_path, index=False)
    print(f"[m4j3] harm_arms stage done: {label} ({time.time() - started:.1f}s total)", flush=True)


# ---------------------------------------------------------------------------
# stage: g3 (trimmed spot check, BASIS_ARMS only -- disclosed near-duplicate
# of j1._g3_spot_check; `world` there is only ever used for labeling output
# rows and a not-found error message, never for dispatch, so this trim is
# purely a waste-avoidance measure (skips M4-J1's own colstd/g6 branch, which
# this leg never uses), not a fidelity change)
# ---------------------------------------------------------------------------


def _g3_spot_check_basis(label: str, contexts: list[dict[str, Any]], spec: M4ChartEcologySpec) -> list[dict[str, Any]]:
    dims = contexts[0]["flat"][("train", 0)][0]["response_next"].shape[1]
    found_context = found_view = found_author = found_stack = None
    for candidate_context in contexts:
        found = False
        for candidate_view in ("train", "test"):
            for candidate_author in range(candidate_context["authors"]):
                candidate_stack = candidate_context["oracle_stacks"][candidate_view][candidate_author]
                if float(np.linalg.norm(candidate_stack["D"])) >= leg4.FLIP_TOLERANCE:
                    found_context, found_view, found_author, found_stack = candidate_context, candidate_view, candidate_author, candidate_stack
                    found = True
                    break
            if found:
                break
        if found:
            break
    if found_context is None:
        raise RuntimeError(f"G3 spot check found NO non-degenerate (rep,view,author) on {label}")

    context, view, author, stack = found_context, found_view, found_author, found_stack
    route = stack["selected_model"]
    fit_kwargs = context["fit_kwargs"]
    calibration_flat, selection_flat, _ = context["flat"][(view, author)]
    d_true = leg4._true_derivative(context["truth"], author)
    regen = h2._regen_for_budget(context, spec, 1.0)
    calibration_g, selection_g = regen["per_view"][view][author]

    rows: list[dict[str, Any]] = []
    for arm in BASIS_ARMS:
        basis, _, _ = j1._basis_for_j1_arm(context, arm)
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
            "label": label, "world": context["mechanism_world"], "arm": arm, "c": 1.0,
            "repetition": context["repetition"], "view": view, "author": author,
            "e_arm_true_flatstyle": e_flatstyle, "e_arm_true_regen_budget1": e_regen, "abs_diff": abs(e_flatstyle - e_regen),
        })
    return rows


def _run_g3(label: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    partial_path = output / f"partial_g3_{label}.csv"
    if partial_path.exists():
        print(f"[m4j3] SKIP (partial exists): g3 {label}", flush=True)
        return
    contexts = _contexts_for_label(label, config, spec, output)
    rows = _g3_spot_check_basis(label, contexts, spec)
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(partial_path, index=False)
    print(f"[m4j3] g3 stage done: {label} ({time.time() - started:.1f}s total)", flush=True)


# ---------------------------------------------------------------------------
# CI helpers (literal reuse of j1's own bare functions)
# ---------------------------------------------------------------------------

_paired_ci = j1._paired_ci
_classify_one_sided = j1._classify_one_sided


# ---------------------------------------------------------------------------
# anchor readers -- direct reads of M4-J1's persisted files, identity by
# construction (the same G1 approach M4-J2 used for these same two
# discriminators)
# ---------------------------------------------------------------------------


def _read_anchor_deployed() -> pd.DataFrame:
    disp = pd.read_csv(J1_DISP_ROWS_PATH)
    dep_disp = disp[disp["arm"] == DEPLOYED_ARM]
    disp_by_world = dep_disp.groupby("world")["disp_v2"].median().rename("baseline_displacement")

    truth = pd.read_csv(J1_AUTHOR_TRUTH_PATH)
    scoped = truth[(truth["arm"] == DEPLOYED_ARM) & (truth["c"] == 1.0)]
    err4 = scoped[scoped["budget"] == PRIMARY_BUDGET].groupby("world")["e_arm_true"].mean().rename("baseline_error_b4")
    err8 = scoped[scoped["budget"] == COMPANION_BUDGET].groupby("world")["e_arm_true"].mean().rename("baseline_error_b8")

    out = pd.concat([disp_by_world, err4, err8], axis=1)
    out.index.name = "world"
    out = out.reset_index()
    out["is_harm_world"] = out["world"].isin(HARM_WORLDS)
    out["is_excluded_truth_world"] = out["world"].isin(EXCLUDED_TRUTH_WORLDS)
    out["is_valid_truth_world"] = out["world"].isin(VALID_TRUTH_WORLDS)
    out["kind"] = "anchor"
    out["label"] = out["world"]
    return out


def _read_anchor_harm() -> pd.DataFrame:
    """Direct read of M4-J1's own lean (b) safety rows -- VALID_TRUTH_WORLDS
    only (6 of 8), every (arm, budget) combination, identity by construction."""
    lb = pd.read_csv(J1_LEAN_B_PATH)
    scoped = lb[lb["arm"].isin([SHRINK20_ARM, SHRINK100_ARM])].copy()
    return scoped


# ---------------------------------------------------------------------------
# new-world readers
# ---------------------------------------------------------------------------

PATHOLOGY_ERROR_BAR = 100.0  # anchor's own valid worlds top out at 0.947; this is >100x that -- the identical order-of-magnitude signature M4-G2 used to identify EXCLUDED_TRUTH_WORLDS (~1e9 there)


def _read_new_deployed(labels: list[str], output: Path) -> pd.DataFrame:
    rows = []
    for label in labels:
        disp_df = pd.read_csv(output / f"partial_deployed_disp_{label}.csv")
        truth_df = pd.read_csv(output / f"partial_deployed_truth_{label}.csv")
        disp_med = float(disp_df["disp_v2"].median())
        usable = truth_df[~truth_df["degenerate_reference"]]
        err4 = usable[usable["budget"] == PRIMARY_BUDGET]["e_arm_true"]
        err8 = usable[usable["budget"] == COMPANION_BUDGET]["e_arm_true"]
        n_degen_b4 = int(truth_df[truth_df["budget"] == PRIMARY_BUDGET]["degenerate_reference"].sum())
        n_total_b4 = int(len(truth_df[truth_df["budget"] == PRIMARY_BUDGET]))
        err4_mean = float(err4.mean()) if len(err4) else float("nan")
        err8_mean = float(err8.mean()) if len(err8) else float("nan")
        rows.append({
            "label": label, "world": NEW_WORLDS[label]["mechanism_world"], "seed_world": NEW_WORLDS[label]["seed_world"],
            "kind": NEW_WORLDS[label]["kind"], "predicted": NEW_WORLDS[label]["predicted"],
            "baseline_displacement": disp_med, "baseline_error_b4": err4_mean, "baseline_error_b8": err8_mean,
            "n_degenerate_b4": n_degen_b4, "n_total_b4": n_total_b4,
            "degenerate_fraction_b4": (n_degen_b4 / n_total_b4) if n_total_b4 else float("nan"),
            "pathological_b4": bool(np.isfinite(err4_mean) and err4_mean > PATHOLOGY_ERROR_BAR),
        })
    return pd.DataFrame(rows)


DISSOCIATION_MATERIALITY_RATIO = 0.10  # reused unchanged from this program's own G2_MATERIALITY_RATIO / H2/J1 convention (10% relative gap)


def _pairwise_dissociation(disc: dict[str, dict[str, float]]) -> pd.DataFrame:
    labels = list(disc.keys())
    rows = []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            a, b = labels[i], labels[j]
            da, db = disc[a], disc[b]
            a_higher_error = bool(da["error"] > db["error"])
            a_higher_disp = bool(da["disp"] > db["disp"])
            dissociates = a_higher_error != a_higher_disp
            error_hi, error_lo = max(da["error"], db["error"]), min(da["error"], db["error"])
            disp_hi, disp_lo = max(da["disp"], db["disp"]), min(da["disp"], db["disp"])
            error_gap_ratio = (error_hi / error_lo - 1.0) if error_lo > 0 else float("inf")
            disp_gap_ratio = (disp_hi / disp_lo - 1.0) if disp_lo > 0 else float("inf")
            materially_dissociates = bool(dissociates and error_gap_ratio >= DISSOCIATION_MATERIALITY_RATIO and disp_gap_ratio >= DISSOCIATION_MATERIALITY_RATIO)
            rows.append({
                "world_a": a, "world_b": b,
                "error_a": da["error"], "error_b": db["error"],
                "disp_a": da["disp"], "disp_b": db["disp"],
                "a_higher_error": a_higher_error, "a_higher_disp": a_higher_disp,
                "lower_error_world": a if not a_higher_error else b,
                "lower_disp_world": a if not a_higher_disp else b,
                "dissociates": bool(dissociates),
                "error_gap_ratio": error_gap_ratio, "disp_gap_ratio": disp_gap_ratio,
                "materiality_bar": DISSOCIATION_MATERIALITY_RATIO,
                "materially_dissociates": materially_dissociates,
            })
    return pd.DataFrame(rows)


def _full_population_dissociation_check(anchor: pd.DataFrame, usable_new: pd.DataFrame) -> pd.DataFrame:
    """Companion, non-primary evidence strengthening G2: checks EVERY pair
    across the full population (8 anchor D1_WORLDS + usable new worlds) for a
    rank inversion, not merely among the new worlds themselves. Still strictly
    deployed-arm data -- no harm outcome is touched. Reported to show how
    thoroughly 'not separable with the machinery available' was checked
    before concluding it, per the registration's own standard for that branch.
    EXCLUDED_TRUTH_WORLDS (the 2 anchor worlds with M4-G2's own known
    near-zero-denominator ~1e9 baseline-error pathology) are dropped from the
    anchor population first -- the SAME pathology screen this leg already
    applies to new worlds via `pathological_b4`, here applied to the anchor
    side too. MECHANICAL FINDING, caught and fixed in this same assembly
    step, before this check's own result was used to adjudicate anything:
    the first draft of this function omitted that exclusion and reported 11
    'dissociating' pairs, 6 of which involved fast_return_equal_marginal or
    linear_null_ecology on one side -- spurious rank inversions driven
    entirely by their ~1e9 pathological error value, not by any genuine
    competence signal."""
    anchor_valid = anchor[~anchor["world"].isin(EXCLUDED_TRUTH_WORLDS)]
    disc = {row["world"]: {"error": row["baseline_error_b4"], "disp": row["baseline_displacement"]} for _, row in anchor_valid.iterrows()}
    disc.update({row["label"]: {"error": row["baseline_error_b4"], "disp": row["baseline_displacement"]} for _, row in usable_new.iterrows()})
    return _pairwise_dissociation(disc)


# ---------------------------------------------------------------------------
# stage: assemble-dissociation -- G2/lean(a) ONLY, computed strictly before
# any harm outcome exists in this leg's own execution transcript
# ---------------------------------------------------------------------------


def _assemble_dissociation(output: Path) -> None:
    started_iso = _now_iso()
    anchor = _read_anchor_deployed()

    labels_present = [label for label in NEW_WORLD_LABELS if (output / f"partial_deployed_disp_{label}.csv").exists()]
    missing = [label for label in NEW_WORLD_LABELS if label not in labels_present]
    if missing:
        raise RuntimeError(f"assemble-dissociation: missing deployed_only partials for {missing}; run --stage deployed_only --label <L> first")

    new_df = _read_new_deployed(labels_present, output)
    usable_new = new_df[~new_df["pathological_b4"]].copy()
    excluded_new = new_df[new_df["pathological_b4"]].copy()

    disc = {row["label"]: {"error": row["baseline_error_b4"], "disp": row["baseline_displacement"]} for _, row in usable_new.iterrows()}
    pairwise = _pairwise_dissociation(disc)
    any_dissociates = bool(pairwise["dissociates"].any()) if len(pairwise) else False
    any_materially_dissociates = bool(pairwise["materially_dissociates"].any()) if len(pairwise) else False
    dissociating_pairs = pairwise[pairwise["dissociates"]] if len(pairwise) else pairwise
    materially_dissociating_pairs = pairwise[pairwise["materially_dissociates"]] if len(pairwise) else pairwise

    full_pop_pairwise = _full_population_dissociation_check(anchor, usable_new)
    full_pop_any_dissociates = bool(full_pop_pairwise["dissociates"].any())
    full_pop_any_materially_dissociates = bool(full_pop_pairwise["materially_dissociates"].any())
    full_pop_dissociating = full_pop_pairwise[full_pop_pairwise["dissociates"]]
    full_pop_materially_dissociating = full_pop_pairwise[full_pop_pairwise["materially_dissociates"]]

    selfcheck_path = output / "g1_selfcheck.json"
    selfcheck = _load_json(selfcheck_path) if selfcheck_path.exists() else None

    g0 = {
        "statement": (
            "the dissociating-world count is small by construction: this leg targets exactly 2 PURPOSE-BUILT worlds "
            "(hybrid_hi_error_lo_disp, hybrid_lo_error_hi_disp) plus up to 2 FOUND companions. A PAIRWISE RANK "
            "INVERSION between two worlds' deployed-arm values, once both are measured, is a DETERMINISTIC fact -- no "
            "sampling uncertainty, exactly like M4-J2's own G0 treatment of its rank-2 separation. But a BARE rank "
            "inversion can be noise-level (a fraction of a percent on either axis); this leg additionally requires "
            "BOTH axes' relative gap to clear a 10% materiality bar (DISSOCIATION_MATERIALITY_RATIO, reused unchanged "
            "from this program's own G2_MATERIALITY_RATIO convention) before calling a pair a genuine dissociation, "
            "reported alongside the bare/unfiltered count for transparency. The HARM read on a dissociating world "
            "(lean b, computed only AFTER this dissociation check) is a paired-by-author CI at the identical "
            "per-world grain M4-J1/M4-J2 used, and inherits the identical power characterization from those legs."
        ),
        "n_new_worlds_attempted": len(NEW_WORLD_LABELS),
        "n_new_worlds_usable_for_dissociation": int(len(usable_new)),
        "n_new_worlds_pathological_excluded": int(len(excluded_new)),
        "pathological_excluded_labels": excluded_new["label"].tolist(),
        "n_pairwise_comparisons": int(len(pairwise)),
        "n_pairs_dissociating_bare": int(pairwise["dissociates"].sum()) if len(pairwise) else 0,
        "n_pairs_materially_dissociating": int(pairwise["materially_dissociates"].sum()) if len(pairwise) else 0,
    }

    g2 = {
        "statement": (
            "the constructed/found worlds' two discriminators (deployed-arm baseline error, deployed-arm baseline "
            "displacement) must genuinely rank OPPOSITELY -- checked PAIRWISE among the new worlds (the literal, "
            "reference-frame-free reading, adopted and disclosed here since 'rank oppositely' requires a reference "
            "frame the registration text does not itself pin down), demonstrated BEFORE any harm outcome "
            "(basis_shrinkage_0.20/1.00) is computed or read anywhere in this leg's own execution transcript -- "
            "verifiable from this file's own mtime preceding every partial_harm_*.csv's mtime. PRIMARY criterion is "
            "MATERIAL dissociation (both axes' relative gap >=10%); the bare/unfiltered rank inversion is reported "
            "as a companion since it is easily satisfied by noise."
        ),
        "reading_adopted": "pairwise rank inversion between two NEW worlds' (error, displacement) pairs, PRIMARY = materially_dissociates",
        "pairwise_table": pairwise.to_dict(orient="records"),
        "any_pair_dissociates_bare": any_dissociates,
        "any_pair_materially_dissociates": any_materially_dissociates,
        "dissociating_pairs_bare": dissociating_pairs.to_dict(orient="records") if len(pairwise) else [],
        "materially_dissociating_pairs": materially_dissociating_pairs.to_dict(orient="records") if len(pairwise) else [],
        "companion_full_population_check": {
            "statement": "non-primary, disclosed companion strengthening the 'not separable with the machinery available' conclusion where it applies: EVERY pair across the full population (8 anchor D1_WORLDS, EXCLUDED_TRUTH_WORLDS' 2 pathological members dropped first, + usable new worlds) checked for a rank inversion, not merely among the new worlds. Still strictly deployed-arm data.",
            "n_population_worlds": int(len(anchor) - len(EXCLUDED_TRUTH_WORLDS) + len(usable_new)),
            "n_pairwise_comparisons": int(len(full_pop_pairwise)),
            "n_pairs_dissociating_bare": int(full_pop_pairwise["dissociates"].sum()),
            "n_pairs_materially_dissociating": int(full_pop_pairwise["materially_dissociates"].sum()),
            "any_pair_dissociates_bare": full_pop_any_dissociates,
            "any_pair_materially_dissociates": full_pop_any_materially_dissociates,
            "dissociating_pairs_bare": full_pop_dissociating.to_dict(orient="records"),
            "materially_dissociating_pairs": full_pop_materially_dissociating.to_dict(orient="records"),
        },
    }

    lean_a = {
        "statement": "DISSOCIATION ACHIEVED -- at least two worlds exist or are constructible in which the two discriminators rank OPPOSITELY, verified before the harm outcome is computed. If dissociation cannot be achieved, this leg adjudicates nothing further and the gate stays provisional.",
        "held": any_materially_dissociates,
        "held_bare_criterion_no_materiality_bar": any_dissociates,
        "held_under_full_population_companion_check_material": full_pop_any_materially_dissociates,
        "held_under_full_population_companion_check_bare": full_pop_any_dissociates,
    }

    evidence = {
        "leg": "M4-J3", "stage": "assemble-dissociation",
        "computed_before_any_harm_outcome": True,
        "timestamp_utc": started_iso,
        "anchor_deployed_table": anchor.to_dict(orient="records"),
        "new_world_deployed_table": new_df.to_dict(orient="records"),
        "g0_power": g0, "g2_dissociation_liveness": g2, "lean_a_dissociation_achieved": lean_a,
        "g1_selfcheck": selfcheck,
    }
    output.mkdir(parents=True, exist_ok=True)
    with (output / "dissociation_evidence.json").open("w", encoding="utf-8") as handle:
        json.dump(evidence, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    new_df.to_csv(output / "dissociation_table.csv", index=False)
    pairwise.to_csv(output / "dissociation_pairwise.csv", index=False)
    full_pop_pairwise.to_csv(output / "dissociation_pairwise_full_population.csv", index=False)

    print(f"[m4j3] ASSEMBLE-DISSOCIATION done at {started_iso}", flush=True)
    print(f"[m4j3] lean_a (DISSOCIATION ACHIEVED, PRIMARY=material) held={any_materially_dissociates} (bare-criterion held={any_dissociates})", flush=True)
    print(f"[m4j3] full-population companion: material held={full_pop_any_materially_dissociates}, bare held={full_pop_any_dissociates}", flush=True)
    print(new_df[["label", "world", "kind", "baseline_error_b4", "baseline_displacement", "pathological_b4"]].to_string(index=False), flush=True)
    if len(pairwise):
        print(pairwise[["world_a", "world_b", "error_a", "error_b", "disp_a", "disp_b", "dissociates", "materially_dissociates"]].to_string(index=False), flush=True)
    print(f"[m4j3] full-population pairwise: {int(len(full_pop_pairwise))} comparisons, {int(full_pop_pairwise['dissociates'].sum())} bare-dissociate, {int(full_pop_pairwise['materially_dissociates'].sum())} materially dissociate", flush=True)
    if full_pop_any_materially_dissociates:
        print(full_pop_materially_dissociating[["world_a", "world_b", "error_a", "error_b", "disp_a", "disp_b", "error_gap_ratio", "disp_gap_ratio"]].to_string(index=False), flush=True)
    if not any_materially_dissociates:
        print("[m4j3] DISSOCIATION NOT ACHIEVED (primary, new-worlds-only, material criterion) -- per the registration, this leg's primary reading adjudicates nothing further; the gate stays provisional under that reading. See the full-population companion for whether any pre-existing pair happens to dissociate.", flush=True)


# ---------------------------------------------------------------------------
# harm outcome for a new world (mirrors j1's own lean-b methodology exactly:
# paired-by-author CI, one-sided +/-0.02 "does not worsen", both budgets)
# ---------------------------------------------------------------------------


def _harm_outcome_for_new_world(label: str, output: Path) -> list[dict[str, Any]]:
    deployed_truth = pd.read_csv(output / f"partial_deployed_truth_{label}.csv")
    deployed_usable = deployed_truth[~deployed_truth["degenerate_reference"]]
    deployed_author = deployed_usable.groupby(["repetition", "author", "budget"])["e_arm_true"].mean()

    rows: list[dict[str, Any]] = []
    for arm in (SHRINK20_ARM, SHRINK100_ARM):
        truth_path = output / f"partial_harm_truth_{label}_{arm}.csv"
        if not truth_path.exists():
            continue
        arm_truth = pd.read_csv(truth_path)
        arm_usable = arm_truth[~arm_truth["degenerate_reference"]]
        arm_author = arm_usable.groupby(["repetition", "author", "budget"])["e_arm_true"].mean()
        for budget in TRUTH_BUDGETS:
            dep_b = deployed_author.xs(budget, level="budget")
            arm_b = arm_author.xs(budget, level="budget")
            joined = pd.concat([arm_b.rename("arm_val"), dep_b.rename("deployed_val")], axis=1, join="inner")
            diffs = (joined["arm_val"] - joined["deployed_val"]).to_numpy()
            ci = _paired_ci(diffs)
            cls = _classify_one_sided(ci, RECOVERY_NO_WORSEN_MARGIN)
            rows.append({
                "label": label, "arm": arm, "budget": budget, "n_authors": ci["n"],
                "mean_diff_arm_minus_deployed": ci["mean"], "ci_lo": ci["ci_lo"], "ci_hi": ci["ci_hi"],
                "half_width": ci["half_width"], "margin": RECOVERY_NO_WORSEN_MARGIN,
                "underpowered_vs_g0_bar": bool(np.isfinite(ci["half_width"]) and ci["half_width"] > G0_FRACTION_BAR),
                "classification": cls, "worsens": bool(cls == "OUTSIDE"),
            })
    return rows


# ---------------------------------------------------------------------------
# G6 motivating-fact verification
# ---------------------------------------------------------------------------


def _g6_motivating_fact_verification(anchor: pd.DataFrame) -> dict[str, Any]:
    cited_disp_values = [18.22, 16.93, 18.61, 22.73, 18.33, 7.01, 18.69, 13.18]
    persisted = anchor.set_index("world")["baseline_displacement"].to_dict()
    persisted_rounded = {w: round(float(v), 2) for w, v in persisted.items()}

    matched = []
    remaining_worlds = dict(persisted_rounded)
    unmatched_cited = []
    for cv in cited_disp_values:
        hit = None
        for w, rv in list(remaining_worlds.items()):
            if abs(rv - cv) < 1e-9:
                hit = w
                break
        if hit is not None:
            matched.append({"cited_value": cv, "matched_world": hit, "full_precision_value": float(persisted[hit])})
            del remaining_worlds[hit]
        else:
            unmatched_cited.append(cv)
    all_matched = (len(unmatched_cited) == 0) and (len(remaining_worlds) == 0)

    valid = anchor[anchor["world"].isin(VALID_TRUTH_WORLDS)]
    harm = valid[valid["world"].isin(HARM_WORLDS)]
    safe = valid[valid["world"].isin(SAFE_WORLDS)]

    err_harm_max = float(harm["baseline_error_b4"].max())
    err_safe_min = float(safe["baseline_error_b4"].min())
    err_gap = err_safe_min - err_harm_max
    err_ratio_pct = (err_safe_min / err_harm_max - 1.0) * 100.0

    disp_harm_max = float(harm["baseline_displacement"].max())
    disp_safe_min = float(safe["baseline_displacement"].min())
    disp_gap = disp_safe_min - disp_harm_max
    disp_ratio_pct = (disp_safe_min / disp_harm_max - 1.0) * 100.0

    return {
        "statement": "re-derivation, from this leg's own direct read of M4-J1's persisted disp_rows.csv/author_level_truth_rows.csv, of every factual claim the M4-J3 registration and the M4-J2 planner adjudication note it inherits cite.",
        "eight_world_displacement_table": {
            "cited_values_as_written_in_registration": cited_disp_values,
            "cited_values_matched_to_persisted_worlds": matched,
            "cited_values_unmatched": unmatched_cited,
            "persisted_worlds_unmatched_to_any_cited_value": list(remaining_worlds.keys()),
            "all_eight_values_verified_correct": bool(all_matched),
            "full_precision_table_by_world": {w: float(v) for w, v in persisted.items()},
        },
        "baseline_error_rank_separation_rederivation": {
            "harm_world_max": err_harm_max, "safe_world_min": err_safe_min,
            "gap_absolute": float(err_gap), "gap_ratio_pct": float(err_ratio_pct),
            "cited_in_registration_pct": 20.5,
            "matches_cited": bool(abs(err_ratio_pct - 20.5) < 0.1),
        },
        "baseline_displacement_rank_separation_rederivation": {
            "harm_world_max": disp_harm_max, "safe_world_min": disp_safe_min,
            "gap_absolute": float(disp_gap), "gap_ratio_pct": float(disp_ratio_pct),
            "cited_in_registration_pct": 28.4,
            "matches_cited": bool(abs(disp_ratio_pct - 28.4) < 0.1),
        },
        "any_cited_fact_found_wrong": bool(not all_matched),
    }


# ---------------------------------------------------------------------------
# stage: assemble -- full adjudication (G0/G1/G2/G3/G4/G6, leans a/b/c, pivot)
# ---------------------------------------------------------------------------


def _assemble(output: Path) -> None:
    evidence_path = output / "dissociation_evidence.json"
    if not evidence_path.exists():
        raise RuntimeError("assemble: dissociation_evidence.json is missing -- run --assemble-dissociation BEFORE --stage harm_arms and this final --assemble")
    evidence = _load_json(evidence_path)
    evidence_mtime = evidence_path.stat().st_mtime

    anchor = _read_anchor_deployed()
    anchor_harm = _read_anchor_harm()

    labels_present = [label for label in NEW_WORLD_LABELS if (output / f"partial_deployed_disp_{label}.csv").exists()]
    new_df = _read_new_deployed(labels_present, output)
    usable_new = new_df[~new_df["pathological_b4"]].copy()
    excluded_new = new_df[new_df["pathological_b4"]].copy()

    disc = {row["label"]: {"error": row["baseline_error_b4"], "disp": row["baseline_displacement"]} for _, row in usable_new.iterrows()}
    pairwise = _pairwise_dissociation(disc)
    any_dissociates_bare = bool(pairwise["dissociates"].any()) if len(pairwise) else False
    any_dissociates = bool(pairwise["materially_dissociates"].any()) if len(pairwise) else False  # PRIMARY criterion
    dissociating_pairs = pairwise[pairwise["materially_dissociates"]].copy() if len(pairwise) else pairwise

    full_pop_pairwise = _full_population_dissociation_check(anchor, usable_new)
    full_pop_material = full_pop_pairwise[full_pop_pairwise["materially_dissociates"]].copy()

    lean_a = {
        "statement": "DISSOCIATION ACHIEVED -- at least two worlds exist or are constructible in which the two discriminators rank OPPOSITELY, verified before the harm outcome is computed. PRIMARY reading: pairwise among the newly searched/constructed worlds only, material criterion (>=10% relative gap on both axes).",
        "held": any_dissociates,
        "held_bare_criterion": any_dissociates_bare,
        "n_dissociating_pairs": int(len(dissociating_pairs)),
        "companion_full_population_material_pairs": full_pop_material.to_dict(orient="records"),
    }

    # ============================ order-of-operations proof ============================
    harm_disp_files = sorted(output.glob("partial_harm_disp_*.csv"))
    harm_truth_files = sorted(output.glob("partial_harm_truth_*.csv"))
    harm_mtimes = [p.stat().st_mtime for p in harm_disp_files] + [p.stat().st_mtime for p in harm_truth_files]
    order_proof = {
        "statement": "the dissociation_evidence.json file (G2/lean(a), computed from ONLY the deployed arm) must predate every partial_harm_*.csv file (the shrinkage-arm harm outcome) on disk -- direct, file-timestamp evidence that the dissociation check ran, and was read, before this leg's own execution ever invoked --stage harm_arms",
        "dissociation_evidence_mtime": evidence_mtime, "dissociation_evidence_mtime_iso": datetime.fromtimestamp(evidence_mtime, tz=timezone.utc).isoformat(),
        "n_harm_partial_files": len(harm_mtimes),
        "earliest_harm_partial_mtime": min(harm_mtimes) if harm_mtimes else None,
        "earliest_harm_partial_mtime_iso": datetime.fromtimestamp(min(harm_mtimes), tz=timezone.utc).isoformat() if harm_mtimes else None,
        "evidence_predates_every_harm_partial": bool(harm_mtimes and all(evidence_mtime < m for m in harm_mtimes)),
    }

    # ============================ G0 (full, restated) ============================
    g0 = dict(evidence["g0_power"])
    g0["harm_read_grain"] = "paired-by-author CI, per (label, arm, budget) -- identical grain to M4-J1's own lean (b) / M4-J2's own benefit read"
    g0["harm_power_bar_half_width"] = G0_FRACTION_BAR

    # ============================ G1 ANCHOR (full) ============================
    selfcheck_path = output / "g1_selfcheck.json"
    selfcheck = _load_json(selfcheck_path) if selfcheck_path.exists() else None
    g1_anchor = {
        "statement": "the eight existing D1_WORLDS reproduce M4-J1/M4-J2's persisted values to <=1e-12 -- READ DIRECTLY (identity by construction, 0.0 diff, exceeding the 1e-12 bar) from M4-J1's disp_rows.csv/author_level_truth_rows.csv/lean_b_safety_rows.csv, per M4-J2's own established precedent for these same two discriminators; PLUS an independent one-repetition self-validation of this leg's OWN new context-builder plumbing.",
        "anchor_read_max_abs_diff": 0.0, "anchor_read_tolerance": G1_ANCHOR_TOLERANCE,
        "anchor_read_pass": True,
        "new_plumbing_selfcheck": selfcheck,
        "new_plumbing_selfcheck_pass": bool(selfcheck is not None and selfcheck.get("disp_v2_pass") and selfcheck.get("truth_pass")),
        "pass": bool(selfcheck is not None and selfcheck.get("disp_v2_pass") and selfcheck.get("truth_pass")),
    }

    # ============================ G2 (restate from evidence + full pairwise incl. excluded) ============================
    g2 = dict(evidence["g2_dissociation_liveness"])
    g2["pathological_new_worlds_excluded_from_dissociation_test"] = excluded_new["label"].tolist()

    # ============================ G3 TRUTH-PATH INVARIANCE ============================
    g3_frames = []
    for label in labels_present:
        p = output / f"partial_g3_{label}.csv"
        if p.exists():
            g3_frames.append(pd.read_csv(p))
    g3_df = pd.concat(g3_frames, ignore_index=True) if g3_frames else pd.DataFrame(columns=["abs_diff"])
    g3_max = float(g3_df["abs_diff"].max()) if len(g3_df) else float("nan")
    g3_gate = {
        "statement": "budget=1.0 freshly-regenerated panels reproduce context['flat']-sourced refits exactly, one spot-check (rep,view,author) per new world, all 3 BASIS_ARMS -- disclosed near-duplicate of j1._g3_spot_check trimmed to skip the colstd/g6 branch this leg never uses.",
        "max_abs_diff": g3_max, "n_checks": int(len(g3_df)), "tolerance": G3_TOLERANCE,
        "pass": bool(np.isfinite(g3_max) and g3_max <= G3_TOLERANCE),
    }

    # ============================ G6 MOTIVATING-FACT VERIFICATION ============================
    g6 = _g6_motivating_fact_verification(anchor)

    # ============================ harm outcomes for usable new worlds ============================
    harm_rows_all: list[dict[str, Any]] = []
    for label in usable_new["label"].tolist():
        harm_rows_all.extend(_harm_outcome_for_new_world(label, output))
    harm_df = pd.DataFrame(harm_rows_all)

    def _harms_at(label: str, arm: str, budget: float) -> bool | None:
        if not len(harm_df):
            return None
        scoped = harm_df[(harm_df["label"] == label) & (harm_df["arm"] == arm) & (harm_df["budget"] == budget)]
        if not len(scoped):
            return None
        return bool(scoped["worsens"].iloc[0])

    harm_by_label = {}
    for label in usable_new["label"].tolist():
        harm_by_label[label] = {
            "harms_primary": _harms_at(label, PRIMARY_SHRINK_ARM, PRIMARY_BUDGET),
            "harms_companion_budget8": _harms_at(label, PRIMARY_SHRINK_ARM, COMPANION_BUDGET),
            "harms_companion_ratio020_b4": _harms_at(label, COMPANION_SHRINK_ARM, PRIMARY_BUDGET),
            "harms_companion_ratio020_b8": _harms_at(label, COMPANION_SHRINK_ARM, COMPANION_BUDGET),
        }

    # ============================ unified harm lookup (anchor worlds via M4-J1's own file + new worlds via this leg's fresh compute) ============================
    def _anchor_harm_lookup(world: str) -> dict[str, bool | None]:
        rows100 = anchor_harm[(anchor_harm["world"] == world) & (anchor_harm["arm"] == SHRINK100_ARM)]
        rows020 = anchor_harm[(anchor_harm["world"] == world) & (anchor_harm["arm"] == SHRINK20_ARM)]

        def _get(rows: pd.DataFrame, budget: float) -> bool | None:
            r = rows[rows["budget"] == budget]
            return bool(r["worsens"].iloc[0]) if len(r) else None

        return {
            "harms_primary": _get(rows100, PRIMARY_BUDGET), "harms_companion_budget8": _get(rows100, COMPANION_BUDGET),
            "harms_companion_ratio020_b4": _get(rows020, PRIMARY_BUDGET), "harms_companion_ratio020_b8": _get(rows020, COMPANION_BUDGET),
        }

    unified_harm_lookup: dict[str, dict[str, bool | None]] = {w: _anchor_harm_lookup(w) for w in anchor["world"]}
    unified_harm_lookup.update(harm_by_label)

    def _classify_pair_harm(a: str, b: str, lower_error_world: str, lower_disp_world: str) -> dict[str, str]:
        result: dict[str, str] = {}
        for combo_name in ("harms_primary", "harms_companion_budget8", "harms_companion_ratio020_b4", "harms_companion_ratio020_b8"):
            harm_a = unified_harm_lookup.get(a, {}).get(combo_name)
            harm_b = unified_harm_lookup.get(b, {}).get(combo_name)
            if harm_a is None or harm_b is None:
                verdict = "UNDETERMINED"
            elif harm_a and not harm_b:
                harmed = a
                verdict = "COMPETENCE_CONSISTENT" if harmed == lower_error_world else ("DISPLACEMENT_CONSISTENT" if harmed == lower_disp_world else "NEITHER_MATCHES")
            elif harm_b and not harm_a:
                harmed = b
                verdict = "COMPETENCE_CONSISTENT" if harmed == lower_error_world else ("DISPLACEMENT_CONSISTENT" if harmed == lower_disp_world else "NEITHER_MATCHES")
            elif harm_a and harm_b:
                verdict = "BOTH_HARMED"
            else:
                verdict = "NEITHER_HARMED"
            result[combo_name] = verdict
        return result

    # ============================ LEAN (b): COMPETENCE WINS (PRIMARY population: new-worlds-only material pairs) ============================
    lean_b_rows = []
    for _, pair in dissociating_pairs.iterrows():
        a, b = pair["world_a"], pair["world_b"]
        row_result: dict[str, Any] = {
            "world_a": a, "world_b": b, "lower_error_world": pair["lower_error_world"], "lower_disp_world": pair["lower_disp_world"],
        }
        row_result.update(_classify_pair_harm(a, b, pair["lower_error_world"], pair["lower_disp_world"]))
        lean_b_rows.append(row_result)
    lean_b_df = pd.DataFrame(lean_b_rows)

    primary_verdicts = lean_b_df["harms_primary"].tolist() if len(lean_b_df) else []
    competence_wins_primary = bool(len(primary_verdicts) > 0 and all(v == "COMPETENCE_CONSISTENT" for v in primary_verdicts))
    displacement_wins_primary = bool(len(primary_verdicts) > 0 and all(v == "DISPLACEMENT_CONSISTENT" for v in primary_verdicts))
    all_combo_cols = ["harms_primary", "harms_companion_budget8", "harms_companion_ratio020_b4", "harms_companion_ratio020_b8"]
    competence_wins_all_combos = bool(len(lean_b_df) > 0 and all((lean_b_df[c] == "COMPETENCE_CONSISTENT").all() for c in all_combo_cols))
    displacement_wins_all_combos = bool(len(lean_b_df) > 0 and all((lean_b_df[c] == "DISPLACEMENT_CONSISTENT").all() for c in all_combo_cols))

    # ============================ disclosed, NON-ADJUDICATING companion: the full-population material pairs ============================
    # Two pairs materially dissociate once EXCLUDED_TRUTH_WORLDS' pathology is screened out of the anchor side:
    # history_gated_ecology vs topology_mismatch (both anchor, both ALREADY KNOWN from M4-J1 to be HARM_WORLDS), and
    # history_gated_ecology vs hybrid_lo_error_hi_disp (the latter a NEW world sharing topology_mismatch's mechanism).
    # Neither pair belongs to the PRIMARY (new-worlds-only) population this leg's lean (b)/(c) adjudicate on; both are
    # reported here purely as disclosure, computed AFTER lean (a) had already and independently missed under the
    # primary reading -- this companion NEVER overrides that verdict.
    companion_pair_rows = []
    for _, pair in full_pop_material.iterrows():
        a, b = pair["world_a"], pair["world_b"]
        row_result = {
            "world_a": a, "world_b": b, "lower_error_world": pair["lower_error_world"], "lower_disp_world": pair["lower_disp_world"],
            "error_gap_ratio": pair["error_gap_ratio"], "disp_gap_ratio": pair["disp_gap_ratio"],
        }
        row_result.update(_classify_pair_harm(a, b, pair["lower_error_world"], pair["lower_disp_world"]))
        companion_pair_rows.append(row_result)
    companion_pairs_df = pd.DataFrame(companion_pair_rows)

    lean_b = {
        "statement": "COMPETENCE WINS -- in the dissociating worlds, harm follows baseline recovery error rather than baseline displacement.",
        "population": "PRIMARY: dissociating pairs among newly searched/constructed worlds only (n=%d)" % len(dissociating_pairs),
        "not_adjudicated": bool(len(dissociating_pairs) == 0),
        "not_adjudicated_reason": "lean (a) MISSED under the primary reading (no pair among the newly searched/constructed worlds materially dissociates) -- per the registration, this leg adjudicates nothing further; lean (b) is NOT scored" if len(dissociating_pairs) == 0 else None,
        "rows": lean_b_rows,
        "competence_wins_at_primary_combination": competence_wins_primary,
        "displacement_wins_at_primary_combination": displacement_wins_primary,
        "competence_wins_at_all_4_combinations": competence_wins_all_combos,
        "displacement_wins_at_all_4_combinations": displacement_wins_all_combos,
        "held": bool(competence_wins_primary and len(dissociating_pairs) > 0),
        "disclosed_non_adjudicating_companion__full_population_material_pairs": {
            "statement": "the ONLY pairs in the full population (anchor + new, pathology-screened) that materially dissociate, computed AFTER lean (a)'s primary MISS was already final -- reported for transparency, NEVER used to adjudicate lean (b)/(c) or override lean (a).",
            "rows": companion_pair_rows,
            "interpretation": (
                "history_gated_ecology vs topology_mismatch: BOTH are M4-J1's own HARM_WORLDS -- harm is identical "
                "(harmed) on both sides regardless of which one ranks lower on error vs displacement, so this pair "
                "carries ZERO discriminating power between the two candidate mechanisms even though it IS a genuine, "
                "material, non-spurious dissociation. history_gated_ecology vs hybrid_lo_error_hi_disp: the hybrid "
                "shares topology_mismatch's mechanism almost exactly (error/displacement within ~1-5% of topology's "
                "own native values), so its harm outcome, computed fresh here, is reported but should not be read as "
                "independent evidence beyond what topology_mismatch's own already-known status already established."
            ),
        },
    }

    # ============================ LEAN (c): THE GATE IS USABLE ============================
    winning_discriminator = "baseline_error_b4" if competence_wins_primary else ("baseline_displacement" if displacement_wins_primary else None)

    valid_anchor = anchor[anchor["world"].isin(VALID_TRUTH_WORLDS)]
    harm_anchor_rows = valid_anchor[valid_anchor["world"].isin(HARM_WORLDS)]
    safe_anchor_rows = valid_anchor[valid_anchor["world"].isin(SAFE_WORLDS)]

    threshold_error = (float(harm_anchor_rows["baseline_error_b4"].max()) + float(safe_anchor_rows["baseline_error_b4"].min())) / 2.0
    threshold_disp = (float(harm_anchor_rows["baseline_displacement"].max()) + float(safe_anchor_rows["baseline_displacement"].min())) / 2.0

    anchor_harm_primary = anchor_harm[(anchor_harm["arm"] == PRIMARY_SHRINK_ARM) & (anchor_harm["budget"] == PRIMARY_BUDGET)].set_index("world")["worsens"].to_dict()

    classification_rows = []
    for _, row in valid_anchor.iterrows():
        w = row["world"]
        actual = bool(anchor_harm_primary.get(w))
        pred_error = bool(row["baseline_error_b4"] < threshold_error)
        pred_disp = bool(row["baseline_displacement"] < threshold_disp)
        classification_rows.append({
            "world": w, "kind": "anchor", "baseline_error_b4": row["baseline_error_b4"], "baseline_displacement": row["baseline_displacement"],
            "actual_harms": actual, "predicted_harms_by_error_threshold": pred_error, "error_threshold_correct": bool(pred_error == actual),
            "predicted_harms_by_disp_threshold": pred_disp, "disp_threshold_correct": bool(pred_disp == actual),
        })
    for label in usable_new["label"].tolist():
        actual = harm_by_label.get(label, {}).get("harms_primary")
        if actual is None:
            continue
        row = usable_new[usable_new["label"] == label].iloc[0]
        pred_error = bool(row["baseline_error_b4"] < threshold_error)
        pred_disp = bool(row["baseline_displacement"] < threshold_disp)
        classification_rows.append({
            "world": row["world"], "kind": f"new:{label}", "baseline_error_b4": row["baseline_error_b4"], "baseline_displacement": row["baseline_displacement"],
            "actual_harms": bool(actual), "predicted_harms_by_error_threshold": pred_error, "error_threshold_correct": bool(pred_error == actual),
            "predicted_harms_by_disp_threshold": pred_disp, "disp_threshold_correct": bool(pred_disp == actual),
        })
    classification_df = pd.DataFrame(classification_rows)
    error_threshold_all_correct = bool(len(classification_df) and classification_df["error_threshold_correct"].all())
    disp_threshold_all_correct = bool(len(classification_df) and classification_df["disp_threshold_correct"].all())

    lean_c = {
        "statement": "THE GATE IS USABLE -- a single threshold on the winning discriminator classifies every world (the original VALID_TRUTH_WORLDS six plus the new usable ones with a determined harm outcome) correctly, with the threshold registered from the original eight (restricted to the 6 with a known harm label) BEFORE the new worlds' outcomes were computed (Part 0.3).",
        "not_adjudicated": bool(winning_discriminator is None),
        "not_adjudicated_reason": "lean (b) never crowned a winner (lean (a) missed, so there is no dissociating pair for lean (b) to score) -- lean (c) has no discriminator to build a certified threshold around; the classification table below is still computed and reported for transparency (against BOTH candidate thresholds), but 'held' cannot be TRUE by construction when there is no winning_discriminator" if winning_discriminator is None else None,
        "threshold_rule": "midpoint(harm-world MAX, safe-world MIN) on VALID_TRUTH_WORLDS only; a world is HARM-predicted if its value is BELOW the threshold",
        "threshold_error_b4": threshold_error, "threshold_displacement": threshold_disp,
        "winning_discriminator": winning_discriminator,
        "classification_table": classification_rows,
        "error_threshold_classifies_all_correctly": error_threshold_all_correct,
        "displacement_threshold_classifies_all_correctly": disp_threshold_all_correct,
        "held": bool(
            winning_discriminator is not None and (
                (winning_discriminator == "baseline_error_b4" and error_threshold_all_correct)
                or (winning_discriminator == "baseline_displacement" and disp_threshold_all_correct)
            )
        ),
    }

    # ============================ G4 MATERIALITY FORM ============================
    g4 = {
        "statement": "G1 is exact identity-by-construction (0.0) plus a <=1e-12 self-check; G2 is an exact pairwise rank-sign comparison (no CI); G3 is a <=1e-12 exact-equality check; lean (a) is an existence claim on a deterministic rank fact; lean (b) is a classification over paired-by-author CI-derived one-sided equivalence outcomes (identical margin/grain to M4-J1's own lean b); lean (c) is an exact classification-accuracy check against a pre-registered threshold. None is a nil-significance test on a known-nonzero quantity.",
        "g1_form": "exact identity + <=1e-12 self-check", "g2_form": "exact rank-sign comparison",
        "g3_form": "<=1e-12 exact equality", "lean_a_form": "deterministic existence claim",
        "lean_b_form": "classification over one-sided equivalence (+/-0.02) CI outcomes",
        "lean_c_form": "exact classification-accuracy check against a pre-registered threshold",
    }

    # ============================ PIVOT ============================
    pivot_condition_met = displacement_wins_primary or (not competence_wins_primary and not displacement_wins_primary)
    pivot = {
        "registered": "harm follows DISPLACEMENT rather than competence, or neither predicts in the dissociating worlds -> the provisional gate's stated basis is wrong. Either the correct gate is displacement (in which case say so and re-specify), or the boundary is not a single scalar at all and no gate can be certified from this design.",
        "fires": bool(any_dissociates and pivot_condition_met),
        "not_applicable_dissociation_not_achieved": bool(not any_dissociates),
        "note": "the pivot's OWN precondition is 'in the dissociating worlds' -- with zero dissociating worlds under the primary reading, the pivot's antecedent is unsatisfied, so it is NOT APPLICABLE (neither fires nor cleanly does-not-fire), exactly the shape M4-G3's own pivot took when its own leg was underpowered rather than a clean miss." if not any_dissociates else None,
    }

    # ============================ VERDICT ============================
    if not any_dissociates:
        verdict = "DISSOCIATION_NOT_ACHIEVED__GATE_STAYS_PROVISIONAL"
    elif competence_wins_primary and lean_c["held"]:
        verdict = "DISSOCIATION_ACHIEVED__COMPETENCE_WINS__GATE_CERTIFIED_ON_ERROR_THRESHOLD"
    elif competence_wins_primary and not lean_c["held"]:
        verdict = "DISSOCIATION_ACHIEVED__COMPETENCE_WINS__THRESHOLD_NOT_CERTIFIED"
    elif displacement_wins_primary and lean_c["held"]:
        verdict = "DISSOCIATION_ACHIEVED__DISPLACEMENT_WINS__PIVOT_FIRES__GATE_MUST_BE_RESPECIFIED_ON_DISPLACEMENT"
    elif displacement_wins_primary and not lean_c["held"]:
        verdict = "DISSOCIATION_ACHIEVED__DISPLACEMENT_WINS__PIVOT_FIRES__THRESHOLD_NOT_EVEN_ON_DISPLACEMENT"
    else:
        verdict = "DISSOCIATION_ACHIEVED__NEITHER_PREDICTS__PIVOT_FIRES__NO_SCALAR_GATE_CERTIFIABLE"

    # ============================ full world x discriminator x harm table ============================
    full_table_rows = []
    for _, row in anchor.iterrows():
        w = row["world"]
        h100_b4 = anchor_harm[(anchor_harm["world"] == w) & (anchor_harm["arm"] == SHRINK100_ARM) & (anchor_harm["budget"] == PRIMARY_BUDGET)]
        h020_b4 = anchor_harm[(anchor_harm["world"] == w) & (anchor_harm["arm"] == SHRINK20_ARM) & (anchor_harm["budget"] == PRIMARY_BUDGET)]
        full_table_rows.append({
            "label": w, "world": w, "kind": "anchor", "is_harm_world": bool(row["is_harm_world"]), "is_valid_truth_world": bool(row["is_valid_truth_world"]),
            "baseline_error_b4": row["baseline_error_b4"], "baseline_displacement": row["baseline_displacement"],
            "shrink100_worsens_b4": bool(h100_b4["worsens"].iloc[0]) if len(h100_b4) else None,
            "shrink100_mean_diff_b4": float(h100_b4["mean_diff_arm_minus_deployed"].iloc[0]) if len(h100_b4) else None,
            "shrink020_worsens_b4": bool(h020_b4["worsens"].iloc[0]) if len(h020_b4) else None,
            "shrink020_mean_diff_b4": float(h020_b4["mean_diff_arm_minus_deployed"].iloc[0]) if len(h020_b4) else None,
        })
    for _, row in new_df.iterrows():
        label = row["label"]
        hb = harm_by_label.get(label, {})
        hd4 = harm_df[(harm_df["label"] == label) & (harm_df["arm"] == SHRINK100_ARM) & (harm_df["budget"] == PRIMARY_BUDGET)]
        hd020 = harm_df[(harm_df["label"] == label) & (harm_df["arm"] == SHRINK20_ARM) & (harm_df["budget"] == PRIMARY_BUDGET)]
        full_table_rows.append({
            "label": label, "world": row["world"], "kind": row["kind"], "is_harm_world": None, "is_valid_truth_world": None,
            "baseline_error_b4": row["baseline_error_b4"], "baseline_displacement": row["baseline_displacement"],
            "shrink100_worsens_b4": hb.get("harms_primary"),
            "shrink100_mean_diff_b4": float(hd4["mean_diff_arm_minus_deployed"].iloc[0]) if len(hd4) else None,
            "shrink020_worsens_b4": hb.get("harms_companion_ratio020_b4"),
            "shrink020_mean_diff_b4": float(hd020["mean_diff_arm_minus_deployed"].iloc[0]) if len(hd020) else None,
            "pathological_b4": bool(row["pathological_b4"]),
        })
    full_table_df = pd.DataFrame(full_table_rows)

    decision = {
        "estimand_id": "M4-J3",
        "tier": "EXPLORATORY",
        "registered_in": "docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, M4-J3 registration (2026-08-03, BEFORE run)",
        "anchor_worlds": D1_WORLDS, "harm_worlds": HARM_WORLDS, "safe_worlds": SAFE_WORLDS, "valid_truth_worlds": VALID_TRUTH_WORLDS,
        "new_worlds": NEW_WORLDS, "new_worlds_usable": usable_new["label"].tolist(), "new_worlds_pathological_excluded": excluded_new["label"].tolist(),
        "order_of_operations_proof": order_proof,
        "gates": {"g0_power": g0, "g1_anchor": g1_anchor, "g2_dissociation_liveness": g2, "g3_truth_path_invariance": g3_gate, "g4_materiality_form": g4, "g6_motivating_fact_verification": g6},
        "lean_a_dissociation_achieved": lean_a,
        "lean_b_competence_wins": lean_b,
        "lean_c_gate_is_usable": lean_c,
        "pivot": pivot,
        "verdict": verdict,
        "claim_boundary": "EXPLORATORY, synthetic, label-free. Tests whether baseline recovery competence and baseline displacement can be dissociated, and if so which predicts the basis-shrinkage repair's harm, on a synthetic world set constructed/found by registered parameter variation. Licenses no claim about any real corpus, construct, person, or diagnosis, and no deployment decision by itself.",
    }
    gates_out = {"g0_power": g0, "g1_anchor": g1_anchor, "g2_dissociation_liveness": g2, "g3_truth_path_invariance": g3_gate, "g4_materiality_form": g4, "g6_motivating_fact_verification": g6}

    output.mkdir(parents=True, exist_ok=True)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    with (output / "gates.json").open("w", encoding="utf-8") as handle:
        json.dump(gates_out, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")

    anchor.to_csv(output / "anchor_deployed_table.csv", index=False)
    anchor_harm.to_csv(output / "anchor_harm_table.csv", index=False)
    new_df.to_csv(output / "new_world_deployed_table.csv", index=False)
    pairwise.to_csv(output / "dissociation_pairwise_final.csv", index=False)
    full_pop_pairwise.to_csv(output / "dissociation_pairwise_full_population_final.csv", index=False)
    if len(harm_df):
        harm_df.to_csv(output / "new_world_harm_rows.csv", index=False)
    lean_b_df.to_csv(output / "lean_b_competence_rows.csv", index=False)
    companion_pairs_df.to_csv(output / "lean_b_companion_full_population_rows.csv", index=False)
    classification_df.to_csv(output / "lean_c_threshold_classification_rows.csv", index=False)
    full_table_df.to_csv(output / "world_discriminator_harm_table.csv", index=False)
    g3_df.to_csv(output / "g3_check_rows.csv", index=False)

    print(f"[m4j3] ASSEMBLE done. verdict={verdict}", flush=True)
    print(f"[m4j3] lean_a held={any_dissociates} (bare={any_dissociates_bare}) lean_b held={lean_b['held']} (not_adjudicated={lean_b['not_adjudicated']}) lean_c held={lean_c['held']} (not_adjudicated={lean_c['not_adjudicated']}) pivot_fires={pivot['fires']}", flush=True)
    print(f"[m4j3] order-of-operations: evidence predates every harm partial = {order_proof['evidence_predates_every_harm_partial']}", flush=True)
    print(full_table_df.to_string(index=False), flush=True)
    if len(companion_pairs_df):
        print("[m4j3] disclosed non-adjudicating companion (full-population material pairs):", flush=True)
        print(companion_pairs_df.to_string(index=False), flush=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "m4_chart_ecology.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "m4_j3_gate_dissociation")
    parser.add_argument("--label", type=str, default=None, help="one of NEW_WORLDS' keys, or 'all'")
    parser.add_argument("--stage", type=str, default=None, choices=["smoke_new", "g1_selfcheck", "prep", "deployed_only", "harm_arms", "g3"])
    parser.add_argument("--assemble-dissociation", action="store_true")
    parser.add_argument("--assemble", action="store_true")
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    spec = M4ChartEcologySpec(**config["base_spec"])

    if args.assemble_dissociation:
        _assemble_dissociation(args.output)
        return
    if args.assemble:
        _assemble(args.output)
        return
    if args.stage == "g1_selfcheck":
        _run_g1_selfcheck(config, spec, args.output)
        return

    if args.label is None:
        raise SystemExit("--label is required unless --assemble/--assemble-dissociation/--stage g1_selfcheck")
    labels = list(NEW_WORLD_LABELS) if args.label == "all" else [args.label]
    for label in labels:
        if label not in NEW_WORLDS:
            raise SystemExit(f"not a registered M4-J3 new-world label: {label}")

    for label in labels:
        if args.stage == "smoke_new":
            _run_smoke_new(label, config, spec, args.output)
        elif args.stage == "prep":
            _run_prep(label, config, spec, args.output)
        elif args.stage == "deployed_only":
            _run_deployed_only(label, config, spec, args.output)
        elif args.stage == "harm_arms":
            _run_harm_arms(label, config, spec, args.output)
        elif args.stage == "g3":
            _run_g3(label, config, spec, args.output)
        else:
            raise SystemExit(f"--stage is required: {args.stage!r} not recognized")


if __name__ == "__main__":
    main()

