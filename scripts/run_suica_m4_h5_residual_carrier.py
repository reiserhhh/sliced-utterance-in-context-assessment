#!/usr/bin/env python3
"""M4-H5: under the safe lever, what carries the surviving ~54%?

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, "M4-H5
registration" (2026-08-03, BEFORE run), preceded by the "M4-H4 planner
adjudication note" on the same date; ledger row M4-H5). Machinery is IMPORTED
and REUSED wherever an existing seam exists -- this script performs NO new
Part 0 audit, NO new basis-construction mechanism, and NO new S1-S4
decomposition machinery: it imports `run_suica_m4_h2_basis_normalization`
(as `h2`), `run_suica_m4_h3_safe_lever_ladder` (as `h3`, whose own `h2` is the
SAME object) and `run_suica_m4_h4_safe_ceiling` (as `h4`, whose own `h3`/`h2`
are the SAME objects) and dispatches every one of this leg's 3 arms to a
LITERAL call into h3's or h4's own, already-anchored, already-adjudicated
`_basis_for_h{3,4}_arm` / `_arm_offset_and_shares_h{3,4}` functions. The only
new code in this file is (1) a 6-line arm router (below) that picks which
predecessor's dispatch function to call, (2) the G1 anchor-chain assembly
against three independently-persisted comparators (M4-E2's decision.json,
M4-H3's disp_rows.csv, M4-H4's disp_rows.csv), (3) the G2 DECOMPOSITION
LIVENESS computation (new to this leg -- see below), and (4) the lean
(a)/(b)/(c) qualifying-subspace adjudication logic the registration asks for.

===========================================================================
WHAT "DECOMPOSE THE RESIDUAL DISPLACEMENT" MEANS HERE (stated precisely,
since the registration delegates the operational definition to this script)
===========================================================================
Throughout this line, an arm's "shares" (`registered_shares`, `reverse_
shares`) are ALREADY the S1-S4 sequential decomposition of THAT ARM's OWN
offset vector Delta_arm = a_center(arm) - align(swap_consensus(arm)) --
i.e. `share_i(arm) = ||component_i||^2 / ||Delta_arm||^2`, a property of the
arm's OWN surviving displacement, not of deployed's. At a repaired arm
(`basis_shrinkage_1.00` or `basis_shrinkage_0.20`), `||Delta_arm||` IS "the
surviving displacement" M4-H4 measured as ~54%/~65% of deployed's own
magnitude (45.79%/34.66% reduction respectively), and `share_i(arm)` IS
"what fraction of that surviving displacement subspace i carries." H2/H3/H4
already compute this decomposition for every arm they touch (that is what
`_arm_offset_and_shares_h{2,3,4}` returns) -- so "decompose the residual
displacement under deployed / basis_shrinkage_1.00 / basis_shrinkage_0.20" is
answered by gathering those three arms' own already-defined share
decompositions, freshly recomputed here (fresh context build, this leg's own
output directory, per the process rule that every G1 anchor be a real
end-to-end test) and anchored to <=1e-12 against the three independently-
persisted comparators named in the registration.

===========================================================================
PART 0 -- INHERITED FROM H2 VIA H3/H4, UNCHANGED. Zero new normalization,
scaling, centering, whitening, or reference choice anywhere in this leg.
===========================================================================
This leg does not vary Part 0 at all -- it re-derives THREE ALREADY-
REGISTERED arms (`deployed`, H4's own `basis_shrinkage_1.00`, H3's own
`basis_shrinkage_0.20`) via literal calls into h3's/h4's own dispatch
functions, and decomposes each arm's own offset. No basis-construction
formula is touched.

--- Arm router (this leg's only new construction code) --------------------
- `deployed` and `basis_shrinkage_1.00` (H4's HARMLESS winner) -> literal
  calls into `h4._basis_for_h4_arm` / `h4._arm_offset_and_shares_h4`.
- `basis_shrinkage_0.20` (H3's ACTIVELY-GOOD winner) -> literal calls into
  `h3._basis_for_h3_arm` / `h3._arm_offset_and_shares_h3` (h4's own ladder
  starts at 0.50 and does not know this ratio).

--- Scope reduction, disclosed (ambiguity, resolved, stated before compute) -
The outer registration's Design/Metrics/Leans sections for THIS leg name
only displacement (`disp_v2`) and S1-S4 shares -- unlike every G/H2/H3/H4
Design section, there is no mention of `TRUTH_BUDGETS` or truth-referenced
recovery anywhere in the M4-H5 registration. Reading A (ADOPTED): Metric 3
(truth recovery) is out of THIS leg's scope -- it was already adjudicated at
both repaired arms by H3 (lean c) and H4 (lean b/c), is not one of this
leg's own registered leans, and recomputing it here would not change any
adjudicated quantity. This leg therefore skips the "oracle" stage and the
`TRUTH_BUDGETS` regeneration loop entirely (a genuine compute-scope
reduction, not a shortcut on what IS in scope). Reading B (disclosed,
NOT adopted): "G3 truth-path invariance where applicable" could be read as
requiring the full truth machinery regardless. Resolution: G3 is honored
under Reading A's own reduced scope -- a lightweight world-build
faithfulness spot-check (budget=1.0 regen vs flat-style refit, h2's own
`_g3_spot_check` pattern, restricted to this leg's 3 arms) is still run and
gated (see G3 below), so "where applicable" is satisfied by re-certifying
the shared context-build machinery this leg still depends on, without
resurrecting a metric this leg does not adjudicate on. This costs one
regen(budget=1.0) call per world (~6s, per h2's own docstring), not the full
oracle-stage TRUTH_BUDGETS=(4.0,8.0) loop H2/H3/H4 each paid for.

--- G2, redefined for this leg (registered as "DECOMPOSITION LIVENESS", a
    different gate from H2/H3/H4's own "G2 BASIS LIVENESS") ---------------
H2/H3/H4's G2 asked "does the arm's BASIS differ materially from deployed's
basis" (a chordal-distance-of-frames ratio bound). This leg's G2 asks "does
the arm's own SHARE DECOMPOSITION differ materially from deployed's" --
answered directly from the shares this leg already computes, no basis-
distance computation needed. Materiality bound: REUSES
`LEAN_B_MATERIALITY_RATIO = 0.10` (H3's own Part 0 constant, itself citing
H2's `G2_MATERIALITY_RATIO = 0.10`) -- the same "moves by >=1/10 of the
reference scale" convention this line has used twice already for exactly
this shape of question, generalized here from "S3's share alone" to "at
least one of the four subspace shares," so as not to presuppose which
subspace will turn out to move (that presupposition is this leg's actual
question, not something Part 0 should assume).

===========================================================================
DESIGN (registered)
===========================================================================
Worlds: H4's own three `HIGH_GAP_WORLDS` (imported transitively, unchanged).
Arms: `deployed`, `basis_shrinkage_1.00` (HARMLESS winner, cited from H4),
`basis_shrinkage_0.20` (ACTIVELY-GOOD winner, cited from H3). One metric
family, computed at every arm: M4-E2's S1-S4 shares (registered order AND
reverse order, both persisted and reported -- M4-E2 disclosed ordering
sensitivity, M4-H1 reproduced it exactly, this leg keeps the comparison
live per the outer task's explicit instruction), plus `disp_v2` (needed for,
and gated by, the G1 anchor).

--- Metric grain (restated fresh, fifth standing rule) ---------------------
Shares: WORLD-level census (n=3), NO CI -- a world's GPA-consensus share is
a single deterministic statistic per (world, arm, subspace, ordering),
identical convention to M4-E2/H2/H3/H4's own Metric-2 treatment (cited, not
re-derived, since the object is literally the same kind of quantity).
Displacement (`disp_v2`, ANCHOR-ONLY, not adjudicating): rep grain (n=24),
identical justification to every predecessor leg on the identical
worlds/reps/metric, cited here only to support the G1 anchor, not recomputed
as its own CI in this leg since reduction-CIs are not one of this leg's
registered leans (already adjudicated by H3/H4 themselves).

--- Winner definition (inherited, cited, not re-derived) -------------------
HARMLESS winner = `basis_shrinkage_1.00` (H4's own G5 dual-winner
compliance, 45.79% reduction, CI [7.515,9.025] rep grain). ACTIVELY-GOOD
winner = `basis_shrinkage_0.20` (H3's own G5 joint-winner compliance,
34.66% reduction, CI [5.613,6.905] rep grain, recovery CI entirely on the
better side both budgets). Both are REGISTERED literally by name in the
outer M4-H5 registration -- no winner-selection computation happens in this
leg; these two arms are simply the two comparators the registration names.

Leans (registered; evaluated at the arms named above; ADOPTED ordering =
registered sequential S1->S2->S3->S4, per every predecessor leg's own
convention of treating "registered order" as primary and "reverse order" as
the disclosed ordering-sensitivity companion; BOTH orderings computed and
reported for every lean, per the outer task's explicit instruction).
(a) A NEW DOMINANT CARRIER EXISTS: at the HARMLESS winner, some subspace i
    in {S1,S2,S3,S4} has share_i >= 0.40 in >= 2 of 3 worlds (same i).
(b) IT IS S4: the subspace identified by (a) (the "primary carrier" -- see
    `_qualifying_subspaces` below for the tie-break rule, disclosed, used
    only if (a) ever finds more than one qualifying subspace) is
    `S4_residual`.
(c) STRENGTH-INVARIANT: the SAME subspace identified by (a)/(b) at the
    HARMLESS winner is ALSO a qualifying carrier (>=0.40 share in >=2/3
    worlds, independently re-tested) at the ACTIVELY-GOOD winner.

PIVOT-IF: lean (a) misses (no subspace clears 0.40 in >=2/3 worlds at the
HARMLESS winner, registered order) -> THE SURVIVING DISPLACEMENT IS
GENUINELY DISTRIBUTED; to be written with the prominence of a discovery,
per the outer task's explicit instruction, not as a shortfall.

Gates: G0 POWER (grain justified above; Metric-shares MDE is N/A in the
usual CI sense -- see docstring above and the G0 section below for what IS
stated instead, citing H3's/H4's own persisted numbers); G1 ANCHOR (shares
vs M4-E2 for `deployed`, registered-literal; displacement vs M4-H4 for
`basis_shrinkage_1.00` and vs M4-H3 for `basis_shrinkage_0.20`, registered-
literal; shares for both repaired arms vs H3's/H4's own persisted CSVs, and
displacement for `deployed` vs H3's/H4's own persisted CSVs, DISCLOSED
SUPERSET -- strictly stronger, cannot change pass/fail, all <=1e-12); G2
DECOMPOSITION LIVENESS (>=10% relative share movement in >=1 of the 4
subspaces, every world, reused `LEAN_B_MATERIALITY_RATIO`); G3 TRUTH-PATH
INVARIANCE (lightweight world-build spot-check, scope-reduced per the
disclosed reading above, not gating any lean); G4 MATERIALITY FORM
(equivalence/margin bound stated per gate, below).

Chunked execution (process rule -- foreground, explicit long timeouts, no
background jobs, no monitors): `--world W --stage g3`, `--world W --arm A`,
`--assemble`, `--smoke`. Every per-(world,arm)/per-world stage is
idempotent (skips if its partial already exists). Contexts are built FRESH
in this leg's own output directory (not a copy of H3's/H4's cache), so the
G1 anchor is a real end-to-end test, exactly as every predecessor leg's own
docstring states for itself.
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
import run_suica_m4_h4_safe_ceiling as h4  # noqa: E402  bit-exact reuse (h4.h3 is h3, h4.h2 is h2, all same objects)

from suica_core.m4_chart_ecology_generator import M4ChartEcologySpec  # noqa: E402

# ---------------------------------------------------------------------------
# registered arms and parameters (Part 0, above)
# ---------------------------------------------------------------------------

DEPLOYED_ARM = "deployed"
HARMLESS_ARM = "basis_shrinkage_1.00"       # M4-H4's HARMLESS winner (cited, registered by name)
ACTIVELY_GOOD_ARM = "basis_shrinkage_0.20"  # M4-H3's ACTIVELY-GOOD winner (cited, registered by name)
REPAIRED_ARMS: tuple[str, ...] = (HARMLESS_ARM, ACTIVELY_GOOD_ARM)
ARMS: tuple[str, ...] = (DEPLOYED_ARM, HARMLESS_ARM, ACTIVELY_GOOD_ARM)

assert HARMLESS_ARM in h4.RATIO_BY_ARM, "HARMLESS_ARM must be one of H4's own new ratios"
assert ACTIVELY_GOOD_ARM in h3.RATIO_BY_ARM, "ACTIVELY_GOOD_ARM must be one of H3's own ladder rungs"
assert ACTIVELY_GOOD_ARM not in h4.RATIO_BY_ARM, "H4's own ladder starts at 0.50; 0.20 must route through h3"

G1_ANCHOR_TOLERANCE = h2.G1_ANCHOR_TOLERANCE  # 1e-12
G3_TOLERANCE = h2.G3_TOLERANCE                # 1e-12
G2_DECOMPOSITION_LIVENESS_RATIO = h3.LEAN_B_MATERIALITY_RATIO  # 0.10, reused unchanged (see docstring)
PIVOT_SHARE_BAR = 0.40           # registered
MIN_WORLDS_FOR_DOMINANCE = 2     # registered: ">= 2 of 3 worlds"
KNIFE_EDGE_GAP_FLOOR = 0.02      # disclosed, informational-only: top1-vs-top2 gap below this is flagged as close

SUBSPACE_ORDER_REGISTERED: tuple[str, ...] = h2.e2.SUBSPACE_NAMES + ("S4_residual",)  # (S1,S2,S3,S4)

SHARE_FIELDS = h3.SHARE_FIELDS  # reused unchanged -- identical flattened share-column-name list H2/H3/H4 all use

H3_RESULTS = ROOT / "results" / "m4_h3_safe_lever_ladder"
H3_DISP_ROWS_PATH = H3_RESULTS / "disp_rows.csv"
H3_OFFSET_SHARES_PATH = H3_RESULTS / "offset_shares_by_arm.csv"
H3_DECISION_PATH = H3_RESULTS / "decision.json"

H4_RESULTS = ROOT / "results" / "m4_h4_safe_ceiling"
H4_DISP_ROWS_PATH = H4_RESULTS / "disp_rows.csv"
H4_OFFSET_SHARES_PATH = H4_RESULTS / "offset_shares_by_arm.csv"
H4_DECISION_PATH = H4_RESULTS / "decision.json"


# ---------------------------------------------------------------------------
# this leg's ONLY new construction code: a 2-way arm router into h3's/h4's
# own, already-anchored dispatch functions. No basis formula is touched here.
# ---------------------------------------------------------------------------


def _basis_for_h5_arm(context: dict[str, Any], arm: str) -> tuple[dict[str, np.ndarray], dict[str, Any], dict[str, Any]]:
    if arm == ACTIVELY_GOOD_ARM:
        return h3._basis_for_h3_arm(context, arm)
    if arm in (DEPLOYED_ARM, HARMLESS_ARM):
        return h4._basis_for_h4_arm(context, arm)
    raise ValueError(f"not a registered M4-H5 arm: {arm}")


def _offset_and_shares_for_h5_arm(
    world: str, contexts: list[dict[str, Any]], arm: str, s1_patterns: np.ndarray, s2_patterns: np.ndarray,
) -> dict[str, Any]:
    """Literal dispatch into h3's/h4's own COMPLETE offset+shares machinery
    (which is itself h2.e2's S1-S4 sequential-decomposition machinery,
    applied to the arm's own basis/frame/GPA-consensus) -- not reimplemented
    at any level."""
    if arm == ACTIVELY_GOOD_ARM:
        return h3._arm_offset_and_shares_h3(world, contexts, arm, s1_patterns, s2_patterns)
    return h4._arm_offset_and_shares_h4(world, contexts, arm, s1_patterns, s2_patterns)  # deployed, harmless


def _g3_spot_check_h5(world: str, contexts: list[dict[str, Any]], spec: M4ChartEcologySpec) -> list[dict[str, Any]]:
    """Near-duplicate of h3._g3_spot_check_h3 / h4._g3_spot_check_h4,
    restricted to this leg's 3 arms and routed through `_basis_for_h5_arm`.
    World-build faithfulness only (see docstring, scope-reduction note) --
    does not gate any lean."""
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
        basis, _, _ = _basis_for_h5_arm(context, arm)
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
# stages: g3, arm, smoke (no "oracle" stage -- scope reduction, docstring)
# ---------------------------------------------------------------------------


def _run_g3_h5(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    partial_path = output / f"partial_g3_{world}.csv"
    if partial_path.exists():
        print(f"[m4h5] SKIP (partial exists): g3 {world}", flush=True)
        return
    contexts = h2._contexts_for_world(world, config, spec, output)
    rows = _g3_spot_check_h5(world, contexts, spec)
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(partial_path, index=False)
    print(f"[m4h5] g3 stage done: {world} ({time.time() - started:.1f}s total)", flush=True)


def _run_arm_h5(world: str, arm: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    partial_path = output / f"partial_arm_{world}_{arm}.json"
    if partial_path.exists():
        print(f"[m4h5] SKIP (partial exists): {world} {arm}", flush=True)
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

    offset_shares = _offset_and_shares_for_h5_arm(world, contexts, arm, s1_patterns, s2_patterns)

    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(offset_shares["disp_rows"]).to_csv(output / f"partial_disp_{world}_{arm}.csv", index=False)
    summary = {k: v for k, v in offset_shares.items() if k != "disp_rows"}
    with partial_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    print(f"[m4h5] arm stage done: {world} {arm} ({time.time() - started:.1f}s total)", flush=True)


def _run_smoke_h5(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    t0 = time.time()
    world_index = {name: index for index, name in enumerate(config["worlds"])}[world]
    expected_for = h2.leg8._expected_geometries_lookup(config)
    seed = h2.leg3._world_seed(int(config["seed"]), 0, world, world_index)
    context = h2.leg4._build_context(
        world, 0, seed, spec=spec, config=config, expected_geometries=expected_for(world, 0, seed),
    )
    print(f"[m4h5 smoke] context built ({time.time() - t0:.1f}s)", flush=True)

    widths: dict[str, int] = {}
    for arm in ARMS:
        t1 = time.time()
        basis, ingredients, meta = _basis_for_h5_arm(context, arm)
        widths[arm] = int(basis["calibration"].shape[1])
        if arm == DEPLOYED_ARM:
            gap = max(float(np.max(np.abs(basis[role] - context["v2_basis"][role]))) for role in h2.ROLES)
            print(f"[m4h5 smoke] deployed basis vs context v2_basis max|diff|={gap:.3e}", flush=True)
            assert gap <= G1_ANCHOR_TOLERANCE, f"deployed basis reconstruction fails G1 anchor: {gap:.3e}"
        print(f"[m4h5 smoke] arm={arm} width={widths[arm]} meta={meta} ({time.time() - t1:.1f}s)", flush=True)
    print(f"[m4h5 smoke] widths by arm (must all match -- no rank_tolerance variant in this leg): {widths}", flush=True)
    assert len(set(widths.values())) == 1, f"unexpected width mismatch across arms: {widths}"

    t2 = time.time()
    rows = _g3_spot_check_h5(world, [context], spec)
    max_diff = max(r["abs_diff"] for r in rows)
    print(f"[m4h5 smoke] g3-style spot check (all {len(ARMS)} arms) rows n={len(rows)} max_abs_diff={max_diff:.3e} ({time.time() - t2:.1f}s)", flush=True)
    print(f"[m4h5 smoke] TOTAL ({time.time() - t0:.1f}s)", flush=True)


# ---------------------------------------------------------------------------
# lean-adjudication helper: which subspace(s) clear the registered pivot bar
# in enough worlds, and which is the "primary carrier" if more than one does
# ---------------------------------------------------------------------------


def _qualifying_subspaces(
    share_by_world: dict[str, dict[str, float]], worlds: list[str], bar: float, min_worlds: int,
) -> dict[str, Any]:
    by_subspace: dict[str, Any] = {}
    for subspace in SUBSPACE_ORDER_REGISTERED:
        share_vals = {w: float(share_by_world[w][subspace]) for w in worlds}
        clears = {w: bool(share_vals[w] >= bar) for w in worlds}
        n_clear = int(sum(clears.values()))
        by_subspace[subspace] = {
            "share_by_world": share_vals, "clears_bar_by_world": clears,
            "n_worlds_clearing": n_clear, "qualifies_ge_min_worlds": bool(n_clear >= min_worlds),
        }
    qualifying = [s for s in SUBSPACE_ORDER_REGISTERED if by_subspace[s]["qualifies_ge_min_worlds"]]
    primary = (
        max(qualifying, key=lambda s: float(np.mean(list(by_subspace[s]["share_by_world"].values()))))
        if qualifying else None
    )
    return {
        "bar": bar, "min_worlds": min_worlds, "by_subspace": by_subspace,
        "qualifying_subspaces": qualifying,
        "primary_carrier_tiebreak_rule": "largest mean share across all 3 worlds among qualifying subspaces (disclosed; only matters if >1 subspace qualifies)",
        "primary_carrier": primary,
    }


def _knife_edge_rows(share_by_world: dict[str, dict[str, float]], worlds: list[str], arm: str, ordering: str) -> list[dict[str, Any]]:
    rows = []
    for w in worlds:
        vals = {s: float(share_by_world[w][s]) for s in SUBSPACE_ORDER_REGISTERED}
        ranked = sorted(vals.items(), key=lambda kv: kv[1], reverse=True)
        top1_name, top1_val = ranked[0]
        top2_name, top2_val = ranked[1]
        gap = top1_val - top2_val
        rows.append({
            "arm": arm, "world": w, "ordering": ordering,
            "top1_subspace": top1_name, "top1_share": top1_val,
            "top2_subspace": top2_name, "top2_share": top2_val,
            "gap": gap, f"knife_edge_lt_{KNIFE_EDGE_GAP_FLOOR}": bool(gap < KNIFE_EDGE_GAP_FLOOR),
        })
    return rows


# ---------------------------------------------------------------------------
# assemble + adjudicate
# ---------------------------------------------------------------------------


def _assemble(output: Path) -> None:
    worlds = list(h2.HIGH_GAP_WORLDS)
    for world in worlds:
        for arm in ARMS:
            path = output / f"partial_disp_{world}_{arm}.csv"
            if not path.exists():
                raise RuntimeError(f"missing partial (world/arm not yet computed): {path}")
            if not (output / f"partial_arm_{world}_{arm}.json").exists():
                raise RuntimeError(f"missing arm summary: partial_arm_{world}_{arm}.json")
        if not (output / f"partial_g3_{world}.csv").exists():
            raise RuntimeError(f"missing G3 spot check for {world}")

    disp_rows = pd.concat([pd.read_csv(output / f"partial_disp_{w}_{a}.csv") for w in worlds for a in ARMS], ignore_index=True)
    g3_rows = pd.concat([pd.read_csv(output / f"partial_g3_{w}.csv") for w in worlds], ignore_index=True)
    arm_summaries = {(w, a): h2._load_json(output / f"partial_arm_{w}_{a}.json") for w in worlds for a in ARMS}

    expected_disp = len(worlds) * len(ARMS) * 8
    if len(disp_rows) != expected_disp:
        raise RuntimeError(f"disp rows {len(disp_rows)} != expected {expected_disp}")
    expected_g3 = len(worlds) * len(ARMS)
    if len(g3_rows) != expected_g3:
        raise RuntimeError(f"g3 rows {len(g3_rows)} != expected {expected_g3}")

    # ==== load the three independently-persisted comparators ====================
    e2_decision = h2._load_json(h2.E2_DECISION_PATH)
    h3_disp = pd.read_csv(H3_DISP_ROWS_PATH)
    h3_shares = pd.read_csv(H3_OFFSET_SHARES_PATH)
    h3_decision = h2._load_json(H3_DECISION_PATH)
    h4_disp = pd.read_csv(H4_DISP_ROWS_PATH)
    h4_shares = pd.read_csv(H4_OFFSET_SHARES_PATH)
    h4_decision = h2._load_json(H4_DECISION_PATH)

    # ==== G1 ANCHOR ==============================================================
    # --- registered-literal chain 1: `deployed` shares vs M4-E2's own decision.json
    e2_share_rows = []
    for w in worlds:
        mine = arm_summaries[(w, DEPLOYED_ARM)]
        theirs = e2_decision["offset_table"][w]
        offset_diff = abs(mine["offset_norm"] - float(theirs["offset_norm"]))
        share_diffs = {name: abs(float(mine["registered_shares"][name]) - float(theirs["registered_shares"][name])) for name in SUBSPACE_ORDER_REGISTERED}
        reverse_diffs = {name: abs(float(mine["reverse_shares"][name]) - float(theirs["reverse_shares"][name])) for name in SUBSPACE_ORDER_REGISTERED}
        standalone_diffs = {name: abs(float(mine["standalone_shares"][name]) - float(theirs["standalone_shares"][name])) for name in h2.e2.SUBSPACE_NAMES}
        family_diffs = {name: abs(float(mine["s3_family_shares"][name]) - float(theirs["s3_family_shares"][name])) for name in mine["s3_family_shares"]}
        e2_share_rows.append({
            "world": w, "offset_norm_abs_diff": offset_diff,
            "max_share_abs_diff": max(list(share_diffs.values()) + list(reverse_diffs.values()) + list(standalone_diffs.values()) + list(family_diffs.values())),
        })
    e2_share_max = max(max(r["offset_norm_abs_diff"], r["max_share_abs_diff"]) for r in e2_share_rows)

    # --- registered-literal chain 2: `basis_shrinkage_1.00` displacement vs M4-H4
    def _disp_anchor(mine_arm: str, theirs_df: pd.DataFrame, theirs_arm: str) -> dict[str, Any]:
        mine = disp_rows[disp_rows["arm"] == mine_arm][["world", "repetition", "disp_v2"]]
        theirs = theirs_df[theirs_df["arm"] == theirs_arm][["world", "repetition", "disp_v2"]]
        joined = mine.merge(theirs, on=["world", "repetition"], suffixes=("_mine", "_theirs"), how="inner")
        if len(joined) != 24:
            raise RuntimeError(f"displacement anchor join for {mine_arm} vs {theirs_arm}: {len(joined)} rows != 24")
        joined["abs_diff"] = (joined["disp_v2_mine"] - joined["disp_v2_theirs"]).abs()
        return {"n_checks": int(len(joined)), "max_abs_diff": float(joined["abs_diff"].max())}

    harmless_disp_anchor = _disp_anchor(HARMLESS_ARM, h4_disp, HARMLESS_ARM)
    # --- registered-literal chain 3: `basis_shrinkage_0.20` displacement vs M4-H3
    actively_good_disp_anchor = _disp_anchor(ACTIVELY_GOOD_ARM, h3_disp, ACTIVELY_GOOD_ARM)

    registered_literal_max = max(e2_share_max, harmless_disp_anchor["max_abs_diff"], actively_good_disp_anchor["max_abs_diff"])
    registered_literal = {
        "deployed_shares_vs_m4e2_decision_json": {"per_world": e2_share_rows, "max_abs_diff": e2_share_max},
        "basis_shrinkage_1.00_displacement_vs_h4_disp_rows": harmless_disp_anchor,
        "basis_shrinkage_0.20_displacement_vs_h3_disp_rows": actively_good_disp_anchor,
        "max_abs_diff": registered_literal_max,
        "pass": bool(registered_literal_max <= G1_ANCHOR_TOLERANCE),
    }

    # --- disclosed superset: shares for both repaired arms vs H3's/H4's own CSVs,
    # --- and deployed displacement vs H3's/H4's own persisted deployed rows -----
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
        share_diffs = {f: abs(float(flat_mine[f]) - float(theirs_row[f])) for f in SHARE_FIELDS}
        return {"world": world, "offset_norm_abs_diff": offset_diff, "max_share_abs_diff": max(share_diffs.values())}

    harmless_share_superset_rows = [_share_anchor_vs_csv(HARMLESS_ARM, w, h4_shares, HARMLESS_ARM) for w in worlds]
    actively_good_share_superset_rows = [_share_anchor_vs_csv(ACTIVELY_GOOD_ARM, w, h3_shares, ACTIVELY_GOOD_ARM) for w in worlds]
    deployed_disp_vs_h3 = _disp_anchor(DEPLOYED_ARM, h3_disp, DEPLOYED_ARM)
    deployed_disp_vs_h4 = _disp_anchor(DEPLOYED_ARM, h4_disp, DEPLOYED_ARM)

    superset_max = max(
        [r["offset_norm_abs_diff"] for r in harmless_share_superset_rows] + [r["max_share_abs_diff"] for r in harmless_share_superset_rows]
        + [r["offset_norm_abs_diff"] for r in actively_good_share_superset_rows] + [r["max_share_abs_diff"] for r in actively_good_share_superset_rows]
        + [deployed_disp_vs_h3["max_abs_diff"], deployed_disp_vs_h4["max_abs_diff"]],
    )
    disclosed_superset = {
        "statement": (
            "NOT required by the registered G1 clause -- strictly additional checks that can only strengthen G1, "
            "never loosen it: (i) full share decomposition for both repaired arms against H3's/H4's own persisted "
            "offset_shares_by_arm.csv (the registered clause names displacement only for these arms); "
            "(ii) deployed's own displacement against H3's AND H4's persisted disp_rows.csv (the registered clause "
            "names shares only for deployed)."
        ),
        "basis_shrinkage_1.00_shares_vs_h4_offset_shares": {"per_world": harmless_share_superset_rows},
        "basis_shrinkage_0.20_shares_vs_h3_offset_shares": {"per_world": actively_good_share_superset_rows},
        "deployed_displacement_vs_h3_disp_rows": deployed_disp_vs_h3,
        "deployed_displacement_vs_h4_disp_rows": deployed_disp_vs_h4,
        "max_abs_diff": float(superset_max),
        "pass": bool(superset_max <= G1_ANCHOR_TOLERANCE),
    }

    g1_anchor = {
        "tolerance": G1_ANCHOR_TOLERANCE,
        "statement": (
            "registered-literal: deployed's shares reproduce M4-E2's own persisted decision.json['offset_table'] "
            "to <=1e-12 (per world); basis_shrinkage_1.00's displacement reproduces M4-H4's own persisted "
            "disp_rows.csv to <=1e-12 (24 row-level checks); basis_shrinkage_0.20's displacement reproduces "
            "M4-H3's own persisted disp_rows.csv to <=1e-12 (24 row-level checks). Disclosed superset (below) "
            "additionally checks full shares for both repaired arms and deployed's displacement against both "
            "predecessors, strengthening but never substituting for the registered-literal chain."
        ),
        "registered_literal": registered_literal,
        "disclosed_superset": disclosed_superset,
        "max_abs_diff_overall": max(registered_literal_max, superset_max),
        "pass": bool(registered_literal["pass"] and disclosed_superset["pass"]),
    }

    # ==== G3 (world-build faithfulness, scope-reduced, not gating any lean) =====
    g3_gate = {
        "statement": (
            "budget=1.0 freshly-regenerated panels reproduce context['flat']-sourced refits exactly, all 3 arms, "
            "one spot-check (rep,view,author) per world -- world-build faithfulness only; this leg does not "
            "adjudicate on truth-recovery (docstring, scope-reduction note), so this gate does not feed any lean."
        ),
        "max_abs_diff": float(g3_rows["abs_diff"].max()),
        "n_checks": int(len(g3_rows)),
        "tolerance": G3_TOLERANCE,
        "pass": bool(g3_rows["abs_diff"].max() <= G3_TOLERANCE),
    }

    # ==== share table (registered order + reverse order), full arm x subspace x world
    shares_registered = {arm: {w: dict(arm_summaries[(w, arm)]["registered_shares"]) for w in worlds} for arm in ARMS}
    shares_reverse = {arm: {w: dict(arm_summaries[(w, arm)]["reverse_shares"]) for w in worlds} for arm in ARMS}

    share_table_rows = []
    for arm in ARMS:
        for world in worlds:
            for ordering, shares_by_arm in (("registered_S1_S2_S3", shares_registered), ("reverse_S3_S2_S1", shares_reverse)):
                shares = shares_by_arm[arm][world]
                for subspace in SUBSPACE_ORDER_REGISTERED:
                    share_table_rows.append({
                        "arm": arm, "world": world, "ordering": ordering, "subspace": subspace,
                        "share": float(shares[subspace]), "clears_pivot_bar_0.40": bool(float(shares[subspace]) >= PIVOT_SHARE_BAR),
                    })
    share_table = pd.DataFrame(share_table_rows)

    # ==== G2 DECOMPOSITION LIVENESS ==============================================
    deployed_reg = shares_registered[DEPLOYED_ARM]
    deployed_rev = shares_reverse[DEPLOYED_ARM]
    g2_by_arm: dict[str, Any] = {}
    for arm in REPAIRED_ARMS:
        arm_reg = shares_registered[arm]
        arm_rev = shares_reverse[arm]
        deltas_registered = {w: {s: float(arm_reg[w][s] - deployed_reg[w][s]) for s in SUBSPACE_ORDER_REGISTERED} for w in worlds}
        deltas_reverse = {w: {s: float(arm_rev[w][s] - deployed_rev[w][s]) for s in SUBSPACE_ORDER_REGISTERED} for w in worlds}
        rel_deltas_registered = {
            w: {s: float(deltas_registered[w][s]) / max(float(deployed_reg[w][s]), h2.e2.EPS) for s in SUBSPACE_ORDER_REGISTERED}
            for w in worlds
        }
        max_abs_rel_by_world = {w: float(max(abs(v) for v in rel_deltas_registered[w].values())) for w in worlds}
        argmax_subspace_by_world = {
            w: max(SUBSPACE_ORDER_REGISTERED, key=lambda s: abs(rel_deltas_registered[w][s])) for w in worlds
        }
        live_every_world = all(max_abs_rel_by_world[w] >= G2_DECOMPOSITION_LIVENESS_RATIO for w in worlds)
        g2_by_arm[arm] = {
            "share_deltas_registered_order_vs_deployed": deltas_registered,
            "share_deltas_reverse_order_vs_deployed": deltas_reverse,
            "relative_share_deltas_registered_order_vs_deployed": rel_deltas_registered,
            "max_abs_relative_delta_by_world": max_abs_rel_by_world,
            "subspace_with_largest_relative_move_by_world": argmax_subspace_by_world,
            "live_every_world": bool(live_every_world),
        }
    g2_decomposition_liveness = {
        "statement": (
            f"the residual decomposition must actually differ from deployed's: at least one of the four registered-"
            f"order subspace shares must move by >={G2_DECOMPOSITION_LIVENESS_RATIO} relative to deployed's own share "
            f"for that subspace, in EVERY world, reusing LEAN_B_MATERIALITY_RATIO's own established convention "
            f"(docstring). Per-world share deltas reported explicitly (not assumed) for both repaired arms, both "
            f"orderings."
        ),
        "materiality_ratio": G2_DECOMPOSITION_LIVENESS_RATIO,
        "by_arm": g2_by_arm,
        "all_live": bool(all(v["live_every_world"] for v in g2_by_arm.values())),
    }

    # ==== knife-edge / order-sensitivity disclosure (informational, all arms) ===
    knife_edge_rows: list[dict[str, Any]] = []
    for arm in ARMS:
        knife_edge_rows.extend(_knife_edge_rows(shares_registered[arm], worlds, arm, "registered_S1_S2_S3"))
        knife_edge_rows.extend(_knife_edge_rows(shares_reverse[arm], worlds, arm, "reverse_S3_S2_S1"))
    knife_edge_df = pd.DataFrame(knife_edge_rows)

    # ==== G0 POWER (justified grain; MDE statement citing H3's/H4's own numbers,
    # ==== stated before the lean adjudication below reads any qualifying number) =
    all_share_values = [row["share"] for row in share_table_rows]
    observed_min, observed_max = float(min(all_share_values)), float(max(all_share_values))
    e2_deployed_s4 = {w: float(e2_decision["offset_table"][w]["registered_shares"]["S4_residual"]) for w in worlds}

    h4_m1_hw = h4_decision["gates"]["G0_power"]["metric1_displacement"]["by_arm_half_width_rep_grain"][HARMLESS_ARM]
    h4_g5_row = next(r for r in h4_decision["gates"]["G5_dual_winner_compliance"]["full_table_sorted_by_reduction_pct_desc"] if r["arm"] == HARMLESS_ARM)
    h3_g5_row = next(r for r in h3_decision["gates"]["G5_joint_winner_compliance"]["full_table_sorted_by_reduction_pct_desc"] if r["arm"] == ACTIVELY_GOOD_ARM)
    h4_g2_bar = h4_decision["gates"]["G2_basis_liveness"]["materiality_ratio"]
    h3_g2_bar = h3_decision["gates"]["G2_basis_liveness"]["materiality_ratio"]
    h4_g2_ratio_x_bar = h4_decision["gates"]["G2_basis_liveness"]["by_arm"][HARMLESS_ARM]["ratio_to_deployed_median_disp_v2"] / h4_g2_bar
    h3_g2_ratio_x_bar = h3_decision["gates"]["G2_basis_liveness"]["by_arm"][ACTIVELY_GOOD_ARM]["ratio_to_deployed_median_disp_v2"] / h3_g2_bar

    g0_power = {
        "metric_shares_grain": (
            "world census (n=3), NO CI -- a deterministic per-(world,arm,subspace,ordering) statistic; identical "
            "convention first stated at M4-E2's own Metric 2 and reused unchanged by H2/H3/H4 (cited, not re-derived, "
            "since this leg's shares are the SAME kind of quantity, only now compared against a fixed absolute bar "
            "(0.40) rather than against deployed's own value)."
        ),
        "mde_statement_before_adjudicating": (
            f"no half-width/MDE is computable for the shares metric in the usual CI sense (no finer sampling unit "
            f"is defined at the world level; standing rule 2's 'measurably non-zero' scale is established instead "
            f"as follows). (i) This leg's OWN freshly computed shares (all 3 arms x 3 worlds x 2 orderings x 4 "
            f"subspaces, n={len(all_share_values)}) range [{observed_min:.4f}, {observed_max:.4f}] -- the 0.40 pivot "
            f"bar sits well inside this demonstrated dynamic range, not at a floor or ceiling. (ii) This leg's "
            f"actual empirical target (S4_residual) is cited from M4-E2's own persisted, already-adjudicated "
            f"deployed-arm numbers as ALREADY measurably non-zero and already near the pivot bar BEFORE any repair: "
            f"registered-order S4 share at deployed = {e2_deployed_s4} (all 3 worlds already >=0.40, per the "
            f"M4-G registration's own 'largest single piece is the residual at .40-.45' framing) -- so this leg's "
            f"question (does repair push it further, or does something else take over) is not being asked at a "
            f"noise floor. (iii) The finest resolution of the '>=2/3 of 3 worlds' count is 1/3, 2/3 or 3/3 -- no "
            f"intermediate value is possible; order-sensitivity (registered vs reverse) and any near-tie against "
            f"the 0.40 bar or between the top-2 subspaces are computed for every (arm,world,ordering) and disclosed "
            f"explicitly (knife_edge_rows.csv) as this design's own substitute for a half-width."
        ),
        "metric1_displacement_anchor_context_not_adjudicating": {
            "note": "displacement reduction is NOT an adjudicating metric in this leg (leans are share-based); cited only to support that the two repaired arms are non-degenerately different from deployed, already independently established by H3's/H4's own G1/G2 gates",
            "h4_basis_shrinkage_1.00_rep_grain_half_width_cited": h4_m1_hw,
            "h4_basis_shrinkage_1.00_reduction_pct_and_ci_cited": {
                "reduction_pct_rep_grain": h4_g5_row["reduction_pct_rep_grain"],
                "ci_lo": h4_g5_row["reduction_ci_lo_rep"], "ci_hi": h4_g5_row["reduction_ci_hi_rep"],
            },
            "h3_basis_shrinkage_0.20_reduction_pct_and_ci_cited": {
                "reduction_pct_rep_grain": h3_g5_row["reduction_pct_rep_grain"],
                "ci_lo": h3_g5_row["reduction_ci_lo_rep"], "ci_hi": h3_g5_row["reduction_ci_hi_rep"],
            },
        },
        "rule3_vacuous_check": (
            f"the repaired arms are not an inert knob: H4's own G2 BASIS LIVENESS certified basis_shrinkage_1.00 "
            f"live at {h4_g2_ratio_x_bar:.2f}x its own 10% bar; H3's own G2 certified basis_shrinkage_0.20 live at "
            f"{h3_g2_ratio_x_bar:.2f}x. This leg's OWN G2 (decomposition liveness, above) independently re-verifies the "
            f"SHARE decomposition itself (not merely the basis) moves materially."
        ),
    }

    # ==== G4 MATERIALITY FORM ====================================================
    g4_materiality_form = {
        "G0": "no CI-based bar for the shares metric (world-census, no sampling unit, per M4-E2/H2/H3/H4's own established convention); Metric-1 numbers cited from H3/H4 as anchor context only, not an equivalence test of this leg's own",
        "G1": "degenerate exact-equality (<=1e-12) against three independently-persisted comparators (M4-E2's decision.json, M4-H3's disp_rows.csv, M4-H4's disp_rows.csv), registered-literal AND disclosed-superset both reported, not significance tests",
        "G2": f"relative-share-delta materiality bound (>={G2_DECOMPOSITION_LIVENESS_RATIO} relative move in >=1 of 4 subspaces, every world), reusing LEAN_B_MATERIALITY_RATIO's own established convention, not nil-significance",
        "G3": "degenerate exact-equality (<=1e-12) between two independently-derived computations; world-build faithfulness only, does not gate any lean (scope-reduction disclosed in the docstring)",
        "lean_a": "per-subspace, per-world ABSOLUTE threshold classification (share >= 0.40, registered order ADOPTED, reverse order disclosed companion), aggregated to a >=2-of-3-worlds count against a fixed registered bar -- not a nil-significance test",
        "lean_b": "categorical identity check: is lean (a)'s identified primary carrier exactly S4_residual",
        "lean_c": "set-membership check: is lean (a)/(b)'s identified carrier (from the harmless winner) ALSO a qualifying carrier (independently re-tested, same absolute threshold) at the actively-good winner",
    }

    # ==== lean (a): A NEW DOMINANT CARRIER EXISTS, AT THE HARMLESS WINNER ========
    lean_a_registered = _qualifying_subspaces(shares_registered[HARMLESS_ARM], worlds, PIVOT_SHARE_BAR, MIN_WORLDS_FOR_DOMINANCE)
    lean_a_reverse = _qualifying_subspaces(shares_reverse[HARMLESS_ARM], worlds, PIVOT_SHARE_BAR, MIN_WORLDS_FOR_DOMINANCE)
    lean_a_held = bool(len(lean_a_registered["qualifying_subspaces"]) > 0)  # ADOPTED: registered order
    lean_a_reverse_held = bool(len(lean_a_reverse["qualifying_subspaces"]) > 0)
    lean_a_orderings_agree_on_held = bool(lean_a_held == lean_a_reverse_held)

    pivot_fires = not lean_a_held
    pivot = {
        "registered": "no subspace carries >=0.40 share in >=2/3 worlds at the HARMLESS winner (registered order, ADOPTED) -> THE SURVIVING DISPLACEMENT IS GENUINELY DISTRIBUTED",
        "fires": bool(pivot_fires),
        "would_fire_under_reverse_order_companion": bool(not lean_a_reverse_held),
        "orderings_agree_on_pivot_decision": lean_a_orderings_agree_on_held,
    }

    lean_a = {
        "statement": "at the HARMLESS winner, some subspace i in {S1,S2,S3,S4} has share_i >= 0.40 in >= 2 of 3 worlds (same i)",
        "evaluated_at_arm": HARMLESS_ARM,
        "registered_order_ADOPTED": lean_a_registered,
        "reverse_order_disclosed_companion": lean_a_reverse,
        "held": lean_a_held,
    }

    # ==== lean (b): IT IS S4 =======================================================
    carrier_registered = lean_a_registered["primary_carrier"]
    carrier_reverse = lean_a_reverse["primary_carrier"]
    lean_b_held = bool(lean_a_held and carrier_registered == "S4_residual")
    lean_b = {
        "statement": "the subspace identified by lean (a) at the HARMLESS winner is S4_residual",
        "primary_carrier_registered_order_ADOPTED": carrier_registered,
        "primary_carrier_reverse_order_disclosed_companion": carrier_reverse,
        "orderings_agree_on_primary_carrier": bool(carrier_registered == carrier_reverse),
        "held": lean_b_held,
    }

    # ==== lean (c): STRENGTH-INVARIANT ============================================
    lean_a_at_actively_good_registered = _qualifying_subspaces(shares_registered[ACTIVELY_GOOD_ARM], worlds, PIVOT_SHARE_BAR, MIN_WORLDS_FOR_DOMINANCE)
    lean_a_at_actively_good_reverse = _qualifying_subspaces(shares_reverse[ACTIVELY_GOOD_ARM], worlds, PIVOT_SHARE_BAR, MIN_WORLDS_FOR_DOMINANCE)

    lean_c_registered_held = bool(carrier_registered is not None and carrier_registered in lean_a_at_actively_good_registered["qualifying_subspaces"])
    lean_c_reverse_held = bool(carrier_reverse is not None and carrier_reverse in lean_a_at_actively_good_reverse["qualifying_subspaces"])
    lean_c_strict_registered_held = bool(carrier_registered is not None and carrier_registered == lean_a_at_actively_good_registered["primary_carrier"])
    lean_c_orderings_agree = bool(lean_c_registered_held == lean_c_reverse_held)

    lean_c = {
        "statement": "the subspace identified by lean (a)/(b) at the HARMLESS winner is ALSO a qualifying carrier (independently re-tested, same >=0.40-in->=2/3-worlds test) at the ACTIVELY-GOOD winner",
        "carrier_from_harmless_winner_registered_order": carrier_registered,
        "qualifying_subspaces_at_actively_good_registered_order": lean_a_at_actively_good_registered["qualifying_subspaces"],
        "primary_carrier_at_actively_good_registered_order": lean_a_at_actively_good_registered["primary_carrier"],
        "held_membership_reading_registered_order_ADOPTED": lean_c_registered_held,
        "held_strict_primary_reading_registered_order_disclosed": lean_c_strict_registered_held,
        "carrier_from_harmless_winner_reverse_order": carrier_reverse,
        "qualifying_subspaces_at_actively_good_reverse_order": lean_a_at_actively_good_reverse["qualifying_subspaces"],
        "primary_carrier_at_actively_good_reverse_order": lean_a_at_actively_good_reverse["primary_carrier"],
        "held_membership_reading_reverse_order_disclosed_companion": lean_c_reverse_held,
        "orderings_agree": lean_c_orderings_agree,
        "held": lean_c_registered_held,  # ADOPTED: registered order, membership reading
    }

    # ==== verdict ===================================================================
    if pivot_fires:
        verdict = "PIVOT_SURVIVING_DISPLACEMENT_GENUINELY_DISTRIBUTED_NO_DOMINANT_CARRIER"
    else:
        b_tag = "IS_S4" if lean_b_held else f"NOT_S4_IS_{carrier_registered}"
        c_tag = "STRENGTH_INVARIANT" if lean_c_registered_held else "STRENGTH_DEPENDENT"
        order_tag = "" if lean_c_orderings_agree else "__ORDER_SENSITIVE_AT_ACTIVELY_GOOD_ARM"
        verdict = f"NEW_DOMINANT_CARRIER_FOUND__{b_tag}__{c_tag}{order_tag}"

    decision = {
        "estimand_id": "SUICA_M4_H5_RESIDUAL_CARRIER",
        "tier": "EXPLORATORY (open-exploration phase)",
        "registered_in": "docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md M4-H5 registration (2026-08-03, BEFORE run), preceded by the M4-H4 planner adjudication note; ledger row M4-H5",
        "worlds": worlds, "arms": list(ARMS),
        "harmless_winner_arm": HARMLESS_ARM, "actively_good_winner_arm": ACTIVELY_GOOD_ARM,
        "part0_inherited": (
            "this leg performs no Part 0 audit and touches no basis-construction formula; every arm is a literal "
            "call into h3's own (basis_shrinkage_0.20) or h4's own (deployed, basis_shrinkage_1.00) already-"
            "anchored dispatch functions"
        ),
        "scope_reduction_disclosed": (
            "Metric 3 (truth-referenced recovery) is out of this leg's registered scope (no TRUTH_BUDGETS mention "
            "in the M4-H5 Design/Metrics/Leans sections); already adjudicated at both repaired arms by H3/H4 "
            "themselves. G3 here is a lightweight world-build faithfulness spot-check only, not a lean-gating test "
            "(docstring, 'scope reduction' section)."
        ),
        "gates": {
            "G0_power": g0_power, "G1_anchor": g1_anchor, "G2_decomposition_liveness": g2_decomposition_liveness,
            "G3_world_build_faithfulness_not_lean_gating": g3_gate, "G4_materiality_form": g4_materiality_form,
        },
        "lean_a_new_dominant_carrier": lean_a,
        "lean_b_it_is_s4": lean_b,
        "lean_c_strength_invariant": lean_c,
        "pivot": pivot,
        "verdict": verdict,
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only (the 3 HIGH_GAP_WORLDS, reused verbatim from M4-E2/Leg14/H2/H3/H4); "
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
    share_table.to_csv(output / "share_table.csv", index=False)
    knife_edge_df.to_csv(output / "knife_edge_rows.csv", index=False)
    pd.DataFrame([
        {"world": w, "arm": a, "offset_norm": arm_summaries[(w, a)]["offset_norm"], "width": arm_summaries[(w, a)]["width"],
         **{f"registered_{k}": v for k, v in arm_summaries[(w, a)]["registered_shares"].items()},
         **{f"reverse_{k}": v for k, v in arm_summaries[(w, a)]["reverse_shares"].items()},
         **{f"standalone_{k}": v for k, v in arm_summaries[(w, a)]["standalone_shares"].items()},
         **{f"s3family_{k}": v for k, v in arm_summaries[(w, a)]["s3_family_shares"].items()}}
        for w in worlds for a in ARMS
    ]).to_csv(output / "offset_shares_by_arm.csv", index=False)

    print(json.dumps({
        "verdict": verdict, "pivot_fires": pivot_fires,
        "lean_a_held": lean_a_held, "lean_b_held": lean_b_held, "lean_c_held": lean_c_registered_held,
        "carrier_registered_order": carrier_registered, "carrier_reverse_order": carrier_reverse,
        "lean_c_orderings_agree": lean_c_orderings_agree,
        "g1_anchor_pass": g1_anchor["pass"], "g2_all_live": g2_decomposition_liveness["all_live"], "g3_pass": g3_gate["pass"],
    }, indent=2))


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "m4_chart_ecology.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "m4_h5_residual_carrier")
    parser.add_argument("--world", type=str, default=None)
    parser.add_argument("--arm", type=str, default=None)
    parser.add_argument("--stage", type=str, default=None, choices=["g3"])
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
        _run_smoke_h5(args.world, config, spec, args.output)
        return
    if args.stage == "g3":
        _run_g3_h5(args.world, config, spec, args.output)
        return
    if args.arm is None:
        raise SystemExit("--arm is required unless --stage g3 or --smoke or --assemble")
    if args.arm not in ARMS:
        raise SystemExit(f"not a registered arm: {args.arm}")
    _run_arm_h5(args.world, args.arm, config, spec, args.output)


if __name__ == "__main__":
    main()
