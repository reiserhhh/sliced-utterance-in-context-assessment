#!/usr/bin/env python3
"""M4-G2: metric units -- does offset_norm inherit the whitening's units?

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, "M4-G2
registration" (2026-08-03, BEFORE run); ledger row M4-G2). Machinery is
IMPORTED and REUSED, not reimplemented: M4-G1's own world/context builder
(`_build_world_contexts`), whitening-arm dispatch for its own 8 arms
(`_whitening_for_arm`, `_scale_factors`, `_condition_number`), CI helpers
(`_paired_world_ci`, `_paired_author_ci`), aggregation helpers
(`_author_level_truth`), and persisted anchors (M4-E2's decision, M4-G1's own
decision/offset/truth/g2 CSVs) -- imported as `g1` below. Leg 10's
freeze-ingredients + Tikhonov whitening rebuild, Leg 9's row-norm swap,
Leg 11's stacked-frame quotient machinery, Leg 14's GPA Frechet mean +
quotient distance, Leg 4's context build / forced-route derivative /
generator regeneration, Leg 3's relative error -- ALL the SAME functions
M4-G1 and M4-E2 used, imported directly, never copied. The only new code is
(i) the pure-scale c-ladder arm construction (Part 0.2), (ii) two disclosed
structural near-duplicates of M4-G1's own `_arm_bases_and_meta` and
`_truth_rows_for_context` parameterized over the c-ladder's 5 arm names
instead of M4-G1's module-level 8-arm `ARM_NAMES` (mirroring M4-G1's OWN
Part 0.3 precedent of writing a disclosed near-duplicate when the original
does not expose what a leg needs), and (iii) the scale-normalization/G2
invariance/regression bookkeeping this leg's own leans require.

THE QUESTION (M4-G1's own hand-off / planner adjudication note). M4-G1 found
the discovery objective's offset_norm falls MONOTONICALLY as the whitening is
weakened, with identity (no whitening) showing the single lowest offset of
all eight arms tried while its truth error is 56% worse than baseline
(Spearman(offset, recovery error) = -.786 across the 7 non-baseline arms).
Two mechanisms could produce that: (1) UNITS -- offset_norm is a norm in a
space whose metric the whitening itself sets, so weakening the whitening
shrinks every distance in that space without anything improving, in which
case the metric cannot be compared across arms with different whitening
scales, and M4-E2's attribution of the offset's mass to the scale family may
itself be a units statement; or (2) a REAL TRADE-OFF -- displacement
genuinely trades against recovery. This leg separates them with a pure
change-of-units manipulation (D1) plus a width-controlled diagnostic (D2).

PART 0.0 -- REGISTERED WORLD SELECTION (disclosed; PARTIALLY resolved BEFORE
compute, CORRECTED DURING compute -- both readings given, per the standing
"never silently pick the favorable reading" rule, since this is a discovery
about the DESIGN, not about any hypothesis-relevant outcome). G0 requires
the c-ladder (D1) to run on MORE worlds than M4-E2/M4-G1's 3-world anchor
ceiling -- "target 8" -- while G1 ANCHOR requires the SAME 3 worlds M4-G1
used (HIGH_GAP_WORLDS) so its persisted baseline offset/truth numbers remain
a valid bit-exact anchor.

ORIGINAL rule (written before any compute): D1_WORLDS = HIGH_GAP_WORLDS (3,
E2-anchored) + 5 FRESH_COMPANION_WORLDS, the config's own `worlds` list, in
its declared order, excluding HIGH_GAP_WORLDS and excluding the 4 worlds
whose archived M4-C.2 battery (`results/m4_chart_ecology/metrics.csv`) shows
`chart_refused=True` on every one of their 8 reps -- author_leakage,
evaluation_support_shift, hidden_opportunity_source_alias,
response_leakage_circular -- since Leg 4's `_build_context` raises
unconditionally on `chart.refused` (a hard compatibility requirement, not a
favorable-result cherry-pick), taking the first 5 remaining in config order:
linear_null_ecology, linear_exogenous_selection,
endogenous_source_partition_matched, fast_return_equal_marginal,
slow_hysteresis_equal_marginal.

DISCOVERY (mid-compute, BEFORE any slope/truth-recovery/lean number was
computed -- only offset_gap's own G1/G2 bookkeeping had run): the ORIGINAL
rule did not check `leg3._world_seed`'s own `matched_groups` table, which
deliberately shares one seed offset across two named worlds each --
{linear_exogenous_selection, endogenous_source_partition_matched} share
offset 101; {fast_return_equal_marginal, slow_hysteresis_equal_marginal}
share offset 211 (pre-existing in Leg 3, used unchanged by every prior leg
in this program; not introduced here). Empirically, for EVERY (world, rep,
c) triple, `offset_norm`, `geometric_mean_scale`, and `condition_number` are
BIT-IDENTICAL (0.0 max abs diff) within each matched pair, even though the
worlds' DYNAMIC mechanisms genuinely differ (archived
`classification_accuracy`/`active_mechanisms` differ sharply, e.g.
`endogenous_source_partition_matched` is 0.0/"creation" against
`linear_exogenous_selection`'s 1.0/"selection"). Mechanism: this leg's
offset/G2 pipeline is built entirely from Leg 10's reference-calibration
chart-fitting + eigendecomposition, which depends only on `seed` (not on
which dynamic mechanism `world` switches on) -- so seed-matched worlds are
DETERMINISTIC DUPLICATES for offset_norm specifically, a fact the ORIGINAL
rule's config-order selection did not anticipate. Two of the 5 originally-
selected fresh companions are therefore zero-information duplicates of their
partners for the offset/slope test (though NOT necessarily for
truth-recovery, which touches the mechanism-dependent calibration/selection
panels -- disclosed separately in the report).

CORRECTED rule, round 1 (adopted; a deterministic, outcome-blind EXTENSION of
the original rule, decided before any slope/truth/lean number existed): same
config-order walk, same chart-refusal exclusion, PLUS skip the second-seen
member of any `matched_groups` pair once its partner is already selected,
continuing to the next worlds in config order to still reach 5. Applied:
linear_null_ecology (independent seed, kept), linear_exogenous_selection
(first of the 101-pair, kept), endogenous_source_partition_matched (second
of the 101-pair, SKIPPED), fast_return_equal_marginal (first of the
211-pair, kept), slow_hysteresis_equal_marginal (second of the 211-pair,
SKIPPED), history_gated_ecology (independent seed, kept),
condition_alias_ecology (independent seed, kept), reaching 5:
{linear_null_ecology, linear_exogenous_selection, fast_return_equal_marginal,
history_gated_ecology, condition_alias_ecology}.

SECOND DISCOVERY (mid-compute, still BEFORE any slope/truth-equivalence/lean
number was computed -- only the G3 spot-check's search loop, added to fix
the empty-file bug the first discovery's replacement worlds triggered, had
run): `linear_exogenous_selection` is degenerate
(`norm(stack["D"]) < FLIP_TOLERANCE`) for EVERY (repetition, view, author) --
all 8x2x16=256 combinations -- so G3's degenerate-equality check cannot run
on it AT ALL, and (since `g1._author_level_truth`/`_author_level_gap`
explicitly drop `degenerate_reference` rows) it would also contribute ZERO
usable rows to lean (b)'s truth-recovery equivalence test. Consistent with
its archived `active_mechanisms="selection"` / `creation_action_geometry`
uniformly 0.0 (no creation loop active at all, and this line's D_true is a
creation/loop-mechanism derivative -- see M4-D Leg 4). This is a hard
blocker, not a power/precision concern: a mandatory gate (G3) is simply
inapplicable on this world.

CORRECTED rule, round 2 (adopted; same outcome-blind principle): replace
`linear_exogenous_selection` with the NEXT candidate in the SAME config-order
walk (continuing past `condition_alias_ecology`, through the 4 chart-refusing
exclusions, to the last remaining safe+independent world in the 15-world
catalog): `topology_mismatch` (archived `active_mechanisms="creation"`,
`creation_action_geometry` .79-.99 across all 8 reps -- a materially active
creation loop, checked from the archive BEFORE running it, precisely to
avoid repeating the same blocker a third time). FRESH_COMPANION_WORLDS =
{linear_null_ecology, topology_mismatch, fast_return_equal_marginal,
history_gated_ecology, condition_alias_ecology}, five independent seeds, G3
non-degenerate on all five (verified below). D1_WORLDS is this twice-
corrected 8. The three excluded worlds' partials remain on disk
(`partial_*_endogenous_source_partition_matched.csv`,
`partial_*_slow_hysteresis_equal_marginal.csv`,
`partial_*_linear_exogenous_selection.csv`) as disclosed evidence; they are
not read by `--assemble`.

PART 0.1 -- REGISTERED SCALE-NORMALIZED OFFSET DEFINITION FOR LEAN (c)
(disclosed, resolved BEFORE compute). D1's own c-ladder shows offset scales
with c "uniformly across every retained direction" BY CONSTRUCTION (c
multiplies the WHOLE baseline whitening operator). Lean (c) needs a
normalization that undoes this SAME kind of "typical per-direction scale"
effect for M4-G1's own eight (differently-shaped) arms, so that arms whose
displayed offset differs mainly because their whitening's OVERALL scale
differs (rather than because their DISCOVERED STRUCTURE differs) are put on
a common footing -- while explicitly NOT also correcting for the retained
WIDTH (that is D2's separate, non-adjudicating diagnostic).

Registered definition: for an arm with per-retained-direction scale factors
s_1..s_k (`1/sqrt(eig_i+lambda)` for baseline/shrinkage/truncated, `1` for
identity -- EXACTLY `g1._scale_factors`'s own output, reused unchanged),

    scale_normalized_offset(arm) := offset_norm(arm) / GM(s_1..s_k),
    GM(s) = exp(mean(log(s)))  -- the GEOMETRIC MEAN of the per-direction
    scale factors (equivalently det(diag(s))^(1/k), the standard "typical
    linear scale" of a diagonal map, invariant to WHICH directions carry
    more or less amplification).

Justification: (i) it is EXACT under D1's own manipulation -- GM(c*s_base) =
c*GM(s_base), so dividing by it recovers exactly "c" when an arm truly is a
uniform rescaling of another, the same relationship D1 tests directly; (ii)
it generalizes cleanly to arms whose scale is NOT uniform across directions
(shrinkage's eig-dependent law, truncation's survivor-only law) by using the
one aggregate statistic that is invariant to reordering which directions get
more or less amplification, matching offset_norm's own basis-invariant
(GPA/quotient) construction; (iii) `identity`'s own GM = 1 exactly (every
s_i=1), so `scale_normalized_offset(identity) = offset_norm(identity)`
unchanged -- identity is untouched by this normalization, a clean property
for a lean whose OWN registered question is whether identity stops being the
minimum. GM(s) is recomputed here (NOT read from M4-G1's persisted CSVs,
which store only scale_min/scale_max/condition_number, not the full vector)
via a light re-run of `leg10._freeze_ingredients` + `g1._whitening_for_arm` +
`g1._scale_factors` on M4-G1's own 3 worlds x 8 reps x 8 arms -- REUSED
unchanged, no GPA, no truth-regeneration -- cross-anchored below (recomputed
scale_min/scale_max reproduce M4-G1's persisted `g2_spectrum_evidence.csv`
exactly) so this recompute is verified consistent with M4-G1's own numbers
before being used for anything.

PART 0.2 -- D1 ARM CONSTRUCTION (registered; do not add or drop). Arms
`c_0.25, c_0.5, c_1.0, c_2.0, c_4.0` for c in {0.25, 0.5, 1.0, 2.0, 4.0}, each
built as `c * whitening_baseline` where `whitening_baseline =
leg10._whitening_with_lambda(ingredients, 0.0)` -- Leg 10's OWN lambda=0
rebuild, i.e. M4-G1's `baseline` arm's own whitening operator, UNCHANGED,
scaled by the scalar c. `c_1.0` IS `baseline` (mathematically identical),
retained under its own name for G1 ANCHOR and G0's log-log fit (c=1 must be
one of the five ladder points). This changes NOTHING structural: SAME
`ingredients["eigenvectors"][:, retained]` (never touched by c at all -- by
construction, not merely by empirical closeness), SAME retained width
(k_retained+1, unchanged across c), and a per-direction scale vector
`c/sqrt(eig+0)` whose RATIOS to each other (relative spectrum) and whose
MAX/MIN ratio (condition number) are exactly c-invariant algebraically. G2
below reports this as an explicit invariance check, not merely an assertion.

PART 0.3 -- STATISTICAL OPERATIONALIZATIONS, DISCLOSED.
- D1's decisive test (lean a / PIVOT): for each of the 8 worlds, an OLS fit
  of log(offset_norm) on log(c) over the 5 ladder points gives ONE slope per
  world; the 8 per-world slopes are then the sampling units for a
  paired-by-world t-interval (`g1._paired_world_ci`, REUSED unchanged, now
  n=8/df=7 rather than M4-G1's n=3/df=2 -- the SAME function, a bigger
  sample). This mirrors the established "paired-by-world" convention of
  every prior leg in this line rather than a naive pooled OLS across all 40
  (world,c) points (which would treat highly-correlated within-world points
  as independent). A pooled OLS across all 40 points is ALSO reported as a
  disclosed, non-gating companion.
- G0's MDE bar for the slope CI: 0.5 -- half the gap between the two
  substantively distinct hypotheses this test discriminates (slope=0,
  scale-invariant, vs slope=1, offset scales exactly linearly with the
  operator's units), the SAME "half of the discriminating gap" convention
  M4-G1's own G0 used (its bar was half of lean (a)'s 25% actionability
  threshold). A secondary, non-primary disclosure reports a paired-by-world
  (n=8) CI on the raw offset difference between the ladder's two extremes
  (c=4.0 minus c=0.25), using M4-G1's OWN materiality convention (12.5% of a
  baseline offset) for direct comparability, with TWO baselines reported
  side by side: M4-E2's persisted 3-world mean (12.999, M4-G1's own number)
  and this leg's own fresh 8-world c=1.0 mean -- explicitly labeled which is
  E2-anchored (3 worlds) and which is fresh (8 worlds), per G0's own
  instruction.
- Lean (b)'s equivalence check: ALL C(5,2)=10 pairwise c-comparisons, at BOTH
  truth budgets (4x, 8x, unchanged from M4-G1), on author-level (view-mean)
  paired differences (`g1._paired_author_ci`, REUSED unchanged) across the 8
  fresh worlds; HELD iff EVERY one of the 20 pairwise CIs lies entirely
  inside +/-0.02 (an equivalence bound on the CI, not the point estimate,
  per G4).
- Lean (c)'s aggregation: registered text says "across M4-G1's eight arms" --
  ALL EIGHT (baseline included), unlike M4-G1's OWN disclosed companion
  (which excluded baseline, n=7); that n=7 reading is ALSO reported here,
  bit-anchored to reproduce M4-G1's disclosed -0.786 as a correctness check
  on this leg's own data plumbing before it is used for anything new. HELD
  iff, at BOTH truth budgets, the scale-normalized Spearman is >= 0 (not
  negative) AND `identity` is not the arm with the minimum scale-normalized
  offset; if the two budgets disagree the lean is reported MISS with the
  disagreement disclosed, never resolved by picking the favorable budget.

GATES: mechanics only here (compliance stated in the report). G0: per-world
log-log OLS slope -> paired-by-world CI (n=8, fresh) vs the 0.5 bar; states
explicitly which numbers are E2-anchored (3 worlds) vs fresh (8 worlds); if
underpowered (half-width > bar), lean (a) and the pivot are BOTH reported
UNDERPOWERED, adjudicating neither branch. G1: `c_1.0` reproduces M4-G1's
persisted `baseline` offset AND both truth-recovery variants to <=1e-12 on
the 3 HIGH_GAP_WORLDS, identical world seeds (`leg3._world_seed`, inside
`g1._build_world_contexts`, is a pure function of config + world +
repetition, unaffected by which OTHER worlds this run also processes). G2:
per (world, rep, c), report width / condition number / relative-spectrum /
eigenvector invariance vs the `c_1.0` case in the SAME context, plus the
Frobenius-norm RATIO (which must equal c, proving the channel is live) --
tolerance 1e-9 relative, far tighter than M4-G1's 10% materiality bar
because THIS leg's claim is EXACT algebraic invariance, not "not too
different." G3: degenerate equality check as in M4-G1 (gap-stage-style
e_arm_true at a spot-check subset vs the truth-path's own budget=1.0
short-circuit). G4: compliance restated per gate in the report; G0/G2 are
margin/equivalence bounds, G3 is a degenerate exact-equality check, lean
(a)'s CI-excludes-zero test is a directional/materiality claim (M4-G1's own
G4 precedent), not a nil-test on a known-nonzero quantity, since the slope's
true value is PRECISELY this leg's open question.

Chunked execution (this arc's standard workaround, UNCHANGED convention):
`--world` + `--stage {offset_gap, truth}` (+ `--budget`) computes ONE
(world, stage) partial; `--assemble` reads every partial, cross-checks
completeness, and adjudicates. Each stage call rebuilds its 8 contexts from
scratch, exactly as M4-G1 does.
"""
from __future__ import annotations

import argparse
import itertools
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
import run_suica_m4_d_direction_anatomy_leg10 as leg10  # noqa: E402
import run_suica_m4_d_bias_variance_leg9 as leg9  # noqa: E402
import run_suica_m4_d_perturbation_leg11 as leg11  # noqa: E402
import run_suica_m4_d_displacement_leg14 as leg14  # noqa: E402
import run_suica_m4_g1_whitening_intervention as g1  # noqa: E402  the leg this extends

from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)

ROLES = leg11.ROLES
FLIP_TOLERANCE = leg4.FLIP_TOLERANCE
HIGH_GAP_WORLDS = g1.HIGH_GAP_WORLDS  # 3, E2/M4-G1-anchored
ORIGINAL_FRESH_COMPANION_WORLDS = (  # Part 0.0, BEFORE the matched-seed discovery
    "linear_null_ecology",
    "linear_exogenous_selection",
    "endogenous_source_partition_matched",
    "fast_return_equal_marginal",
    "slow_hysteresis_equal_marginal",
)
SEED_MATCHED_DUPLICATES_EXCLUDED = (  # Part 0.0 round 1, disclosed evidence kept on disk, not assembled
    "endogenous_source_partition_matched",  # seed-matches linear_exogenous_selection (offset 101)
    "slow_hysteresis_equal_marginal",  # seed-matches fast_return_equal_marginal (offset 211)
)
DEGENERATE_D_TRUE_EXCLUDED = (  # Part 0.0 round 2, disclosed evidence kept on disk, not assembled
    "linear_exogenous_selection",  # degenerate D_true on ALL 256 (rep,view,author); G3 inapplicable
)
FRESH_COMPANION_WORLDS = (  # Part 0.0 CORRECTED rule (round 2), adopted
    "linear_null_ecology",
    "topology_mismatch",
    "fast_return_equal_marginal",
    "history_gated_ecology",
    "condition_alias_ecology",
)
D1_WORLDS = tuple(HIGH_GAP_WORLDS) + FRESH_COMPANION_WORLDS  # 8 total, all mutually independent seeds
assert len(D1_WORLDS) == 8, f"expected 8 D1 worlds, got {len(D1_WORLDS)}"
assert not set(FRESH_COMPANION_WORLDS) & set(SEED_MATCHED_DUPLICATES_EXCLUDED)
assert not set(FRESH_COMPANION_WORLDS) & set(DEGENERATE_D_TRUE_EXCLUDED)

C_VALUES = (0.25, 0.5, 1.0, 2.0, 4.0)
C_ARM_NAMES = ("c_0.25", "c_0.5", "c_1.0", "c_2.0", "c_4.0")
C_OF_ARM = dict(zip(C_ARM_NAMES, C_VALUES))
ARM_OF_C = {c: arm for arm, c in C_OF_ARM.items()}

TRUTH_BUDGETS = g1.TRUTH_BUDGETS  # (4.0, 8.0), reused unchanged

G1_ANCHOR_TOLERANCE = 1e-12
G3_TOLERANCE = 1e-12
G2_INVARIANCE_TOLERANCE = 1e-9  # relative; algebraic identity, expect ~1e-15
SCALENORM_ANCHOR_TOLERANCE = 1e-9  # vs M4-G1 persisted scale_min/scale_max
G0_SLOPE_HALF_WIDTH_BAR = 0.5  # half the slope=0-vs-slope=1 discriminating gap
G0_SECONDARY_POWER_FRACTION = 0.125  # M4-G1's own convention, for comparability
LEAN_B_MARGIN = 0.02
LEAN_B_MARGIN_JUSTIFICATION = "~4% of M4-G1 baseline truth error (.5562 @4x)"
EPS = 1e-300


# ---------------------------------------------------------------------------
# persisted M4-G1 references
# ---------------------------------------------------------------------------


def _load_m4g1_csv(name: str) -> pd.DataFrame:
    path = ROOT / "results" / "m4_g1_whitening_intervention" / name
    if not path.exists():
        raise RuntimeError(f"M4-G1 persisted artifact is a required anchor: {path}")
    return pd.read_csv(path)


def _load_m4g1_decision() -> dict[str, Any]:
    path = ROOT / "results" / "m4_g1_whitening_intervention" / "decision.json"
    if not path.exists():
        raise RuntimeError(f"M4-G1 persisted decision is a required anchor: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


# ---------------------------------------------------------------------------
# D1: pure-scale c-ladder arm construction (Part 0.2)
# ---------------------------------------------------------------------------


def _whitening_for_c(ingredients: dict[str, Any], c: float) -> np.ndarray:
    whitening0 = leg10._whitening_with_lambda(ingredients, 0.0)  # M4-G1 baseline, unchanged
    return c * whitening0


def _scale_factors_for_c(ingredients: dict[str, Any], c: float) -> np.ndarray:
    eig_retained = ingredients["eigenvalues"][ingredients["retained"]]
    return c / np.sqrt(np.maximum(eig_retained, 1e-12))


def _c_arm_bases_and_g2(
    contexts: list[dict[str, Any]], world: str
) -> tuple[dict[str, list[dict[str, np.ndarray]]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Build the 5 c-arm bases per rep, plus G2 invariance evidence rows and
    (for HIGH_GAP_WORLDS only) the lean-(c) scale-normalization rows over
    M4-G1's own 8 arms (Part 0.1), reusing `g1._whitening_for_arm` /
    `g1._scale_factors` directly -- both take `arm` as an explicit argument
    and do not depend on g1's module-level ARM_NAMES, so this is genuine
    reuse, not a duplicate dispatch table."""
    arm_bases: dict[str, list[dict[str, np.ndarray]]] = {name: [] for name in C_ARM_NAMES}
    g2_rows: list[dict[str, Any]] = []
    scalenorm_rows: list[dict[str, Any]] = []
    for rep_idx, context in enumerate(contexts):
        ingredients = leg10._freeze_ingredients(context)
        scale_c1 = _scale_factors_for_c(ingredients, 1.0)
        whitening_c1 = _whitening_for_c(ingredients, 1.0)
        frob_c1 = float(np.linalg.norm(whitening_c1))
        relative_spectrum_c1 = scale_c1 / np.max(scale_c1)
        eigenvectors_used_c1 = ingredients["eigenvectors"][:, ingredients["retained"]]
        for name in C_ARM_NAMES:
            c = C_OF_ARM[name]
            whitening = _whitening_for_c(ingredients, c)
            basis = leg10._bases_from_whitening(context, ingredients, whitening)
            arm_bases[name].append(basis)

            scale = _scale_factors_for_c(ingredients, c)
            width = int(basis["calibration"].shape[1])
            relative_spectrum = scale / np.max(scale)
            frob = float(np.linalg.norm(whitening))
            eigenvectors_used = ingredients["eigenvectors"][:, ingredients["retained"]]
            g2_rows.append(
                {
                    "world": world,
                    "repetition": rep_idx,
                    "arm": name,
                    "c": c,
                    "width": width,
                    "k_retained": int(len(ingredients["retained"])),
                    "condition_number": g1._condition_number(scale),
                    "condition_number_c1": g1._condition_number(scale_c1),
                    "condition_number_abs_diff_vs_c1": abs(
                        g1._condition_number(scale) - g1._condition_number(scale_c1)
                    ),
                    "relative_spectrum_max_abs_diff_vs_c1": float(
                        np.max(np.abs(relative_spectrum - relative_spectrum_c1))
                    ),
                    "eigenvectors_identical_array_vs_c1": bool(
                        np.array_equal(eigenvectors_used, eigenvectors_used_c1)
                    ),
                    "eigenvectors_is_same_object_vs_c1": bool(
                        eigenvectors_used is eigenvectors_used_c1
                    ),
                    "geometric_mean_scale": float(np.exp(np.mean(np.log(scale)))),
                    "frobenius_norm": frob,
                    "frobenius_norm_c1": frob_c1,
                    "frobenius_norm_ratio_vs_c1": (frob / frob_c1) if frob_c1 else float("nan"),
                    "c_recovered_from_frobenius_ratio_abs_diff": (
                        abs((frob / frob_c1) - c) if frob_c1 else float("nan")
                    ),
                }
            )
        if world in HIGH_GAP_WORLDS:
            for arm in g1.ARM_NAMES:
                whitening_g1, meta_g1 = g1._whitening_for_arm(ingredients, arm)
                scale_g1 = g1._scale_factors(ingredients, arm, meta_g1)
                scalenorm_rows.append(
                    {
                        "world": world,
                        "repetition": rep_idx,
                        "arm": arm,
                        "geometric_mean_scale": float(np.exp(np.mean(np.log(scale_g1)))),
                        "scale_min": float(np.min(scale_g1)),
                        "scale_max": float(np.max(scale_g1)),
                        "condition_number": g1._condition_number(scale_g1),
                    }
                )
    return arm_bases, g2_rows, scalenorm_rows


# ---------------------------------------------------------------------------
# stage 1: offset (GPA, per c-arm) + G1/G2/G3 gates
# ---------------------------------------------------------------------------


def _run_offset_gap_stage(
    world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path
) -> None:
    contexts = g1._build_world_contexts(world, config, spec)  # reused, unmodified
    arm_bases, g2_rows, scalenorm_rows = _c_arm_bases_and_g2(contexts, world)

    # ---- G1 anchor (basis): c_1.0 must reproduce context v2_basis exactly ----
    basis_gap_max = 0.0
    for rep_idx, context in enumerate(contexts):
        for role in ROLES:
            diff = float(
                np.max(np.abs(arm_bases["c_1.0"][rep_idx][role] - context["v2_basis"][role]))
            )
            basis_gap_max = max(basis_gap_max, diff)
    if basis_gap_max > G1_ANCHOR_TOLERANCE:
        raise RuntimeError(
            f"G1 basis anchor fails on {world}: c_1.0 arm diverges from "
            f"context v2_basis by {basis_gap_max:.3e}"
        )

    # ---- offset (GPA) per c-arm ------------------------------------------------
    offset_rows = []
    for name in C_ARM_NAMES:
        c = C_OF_ARM[name]
        v2_frames = []
        swap_frames = []
        for rep_idx, context in enumerate(contexts):
            basis = arm_bases[name][rep_idx]
            swap_basis = leg9._row_norm_swap(context["truth"].oracle_basis, basis)
            v2_frames.append(leg11._stack_frame(basis))
            swap_frames.append(leg11._stack_frame(swap_basis))
        gpa_v2 = leg14._frechet_mean_multistart(v2_frames)
        gpa_swap = leg14._frechet_mean_multistart(swap_frames)
        offset = leg14._quotient_distance(gpa_v2["mean"], gpa_swap["mean"])
        offset_rows.append(
            {
                "world": world,
                "arm": name,
                "c": c,
                "offset_norm": offset,
                "width": int(v2_frames[0].shape[1]),
                "gpa_v2_basins": int(gpa_v2["n_distinct_basins"]),
                "gpa_swap_basins": int(gpa_swap["n_distinct_basins"]),
                "gpa_v2_objective": gpa_v2["objective_mean_squared_distance"],
                "gpa_swap_objective": gpa_swap["objective_mean_squared_distance"],
            }
        )
        print(
            f"[m4g2] offset {world} arm={name} c={c} offset={offset:.6f}",
            flush=True,
        )

    # ---- G1 anchor (offset): only meaningful on HIGH_GAP_WORLDS ----------------
    offset_anchor_gap = None
    if world in HIGH_GAP_WORLDS:
        m4g1_offset = _load_m4g1_csv("offset_rows.csv")
        persisted_baseline = float(
            m4g1_offset[
                (m4g1_offset["world"] == world) & (m4g1_offset["arm"] == "baseline")
            ]["offset_norm"].iloc[0]
        )
        my_c1_offset = next(r["offset_norm"] for r in offset_rows if r["arm"] == "c_1.0")
        offset_anchor_gap = abs(my_c1_offset - persisted_baseline)
        if offset_anchor_gap > G1_ANCHOR_TOLERANCE:
            raise RuntimeError(
                f"G1 offset anchor fails on {world}: {my_c1_offset:.12f} vs "
                f"M4-G1 persisted {persisted_baseline:.12f} "
                f"(|diff|={offset_anchor_gap:.3e})"
            )

    # ---- scale-norm anchor (only HIGH_GAP_WORLDS): vs M4-G1's own g2 CSV -------
    scalenorm_anchor_max = None
    if world in HIGH_GAP_WORLDS:
        m4g1_g2 = _load_m4g1_csv("g2_spectrum_evidence.csv")
        scalenorm_anchor_max = 0.0
        for row in scalenorm_rows:
            ref = m4g1_g2[
                (m4g1_g2["world"] == row["world"])
                & (m4g1_g2["arm"] == row["arm"])
                & (m4g1_g2["repetition"] == row["repetition"])
            ]
            if len(ref) != 1:
                raise RuntimeError(
                    f"scale-norm anchor: missing M4-G1 g2 row for {row['world']} "
                    f"{row['arm']} rep{row['repetition']}"
                )
            ref = ref.iloc[0]
            diff = max(
                abs(row["scale_min"] - float(ref["scale_min"])),
                abs(row["scale_max"] - float(ref["scale_max"])),
            )
            scalenorm_anchor_max = max(scalenorm_anchor_max, diff)
        if scalenorm_anchor_max > SCALENORM_ANCHOR_TOLERANCE:
            raise RuntimeError(
                f"scale-norm anchor fails on {world}: max abs diff "
                f"{scalenorm_anchor_max:.3e} vs M4-G1 persisted g2 CSV"
            )

    # ---- G3 spot check: gap-stage-style e_arm_true vs truth-path budget=1.0 ----
    # Search for the first non-degenerate (rep, view, author) rather than
    # hardcoding rep0/train/author0 -- 4 of the 8 D1 worlds have a degenerate
    # oracle reference there (discovered when this search was added), which
    # would otherwise leave g3_rows empty for those worlds.
    g3_rows: list[dict[str, Any]] = []
    dims = contexts[0]["flat"][("train", 0)][0]["response_next"].shape[1]
    rep_idx = view = author = context = stack = None
    for candidate_rep_idx, candidate_context in enumerate(contexts):
        found = False
        for candidate_view in ("train", "test"):
            for candidate_author in range(candidate_context["authors"]):
                candidate_stack = candidate_context["oracle_stacks"][candidate_view][candidate_author]
                if float(np.linalg.norm(candidate_stack["D"])) >= FLIP_TOLERANCE:
                    rep_idx, view, author, context, stack = (
                        candidate_rep_idx,
                        candidate_view,
                        candidate_author,
                        candidate_context,
                        candidate_stack,
                    )
                    found = True
                    break
            if found:
                break
        if found:
            break
    degenerate = context is None
    if not degenerate:
        route = stack["selected_model"]
        fit_kwargs = context["fit_kwargs"]
        calibration, selection, _ = context["flat"][(view, author)]
        d_true = leg4._true_derivative(context["truth"], author)
        for name in ("c_1.0", "c_4.0"):
            basis = arm_bases[name][rep_idx]
            d_gapstyle = leg4._forced_route_derivative(
                calibration,
                selection,
                basis,
                model=route,
                hazard_ridge=fit_kwargs["hazard_ridge"],
                logistic_iterations=fit_kwargs["logistic_iterations"],
                dimensions=dims,
            )
            e_gapstyle = leg3._relative_error(d_gapstyle, d_true)
            calibration_g3 = leg4._flatten_events(
                context["observed"].ecology.train_calibration, author
            )
            selection_g3 = leg4._flatten_events(
                context["observed"].ecology.train_selection, author
            )
            d_truthpath = leg4._forced_route_derivative(
                calibration_g3,
                selection_g3,
                basis,
                model=route,
                hazard_ridge=fit_kwargs["hazard_ridge"],
                logistic_iterations=fit_kwargs["logistic_iterations"],
                dimensions=dims,
            )
            e_truthpath = leg3._relative_error(d_truthpath, d_true)
            g3_rows.append(
                {
                    "world": world,
                    "arm": name,
                    "repetition": rep_idx,
                    "view": view,
                    "author": author,
                    "e_arm_true_gapstyle": e_gapstyle,
                    "e_arm_true_truthpath_budget1": e_truthpath,
                    "abs_diff": abs(e_gapstyle - e_truthpath),
                }
            )
    if degenerate:
        raise RuntimeError(
            f"G3 spot check found NO non-degenerate (rep, view, author) on "
            f"{world} across all {len(contexts)} reps -- cannot run the "
            f"degenerate equality check at all on this world"
        )
    g3_max = max((row["abs_diff"] for row in g3_rows), default=float("nan"))
    if g3_max > G3_TOLERANCE:
        raise RuntimeError(f"G3 truth-path invariance fails on {world}: {g3_max:.3e}")

    G3_COLUMNS = [
        "world",
        "arm",
        "repetition",
        "view",
        "author",
        "e_arm_true_gapstyle",
        "e_arm_true_truthpath_budget1",
        "abs_diff",
    ]

    # ---- persist -----------------------------------------------------------
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(offset_rows).to_csv(output / f"partial_offset_{world}.csv", index=False)
    pd.DataFrame(g2_rows).to_csv(output / f"partial_g2_{world}.csv", index=False)
    pd.DataFrame(g3_rows, columns=G3_COLUMNS).to_csv(
        output / f"partial_g3check_{world}.csv", index=False
    )
    if world in HIGH_GAP_WORLDS:
        pd.DataFrame(scalenorm_rows).to_csv(
            output / f"partial_scalenorm_{world}.csv", index=False
        )
    gates = {
        "world": world,
        "is_high_gap_e2_anchored": world in HIGH_GAP_WORLDS,
        "basis_anchor_max_abs_diff": basis_gap_max,
        "offset_anchor_abs_diff": offset_anchor_gap,
        "scalenorm_anchor_max_abs_diff": scalenorm_anchor_max,
        "g3_truthpath_max_abs_diff": g3_max,
        "unit_check_max": max(c_["unit_gap"] for c_ in contexts),
    }
    with (output / f"partial_gates_offset_gap_{world}.json").open("w", encoding="utf-8") as handle:
        json.dump(gates, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    print(f"[m4g2] offset_gap stage done: {world} ({json.dumps(gates, default=str)})", flush=True)


# ---------------------------------------------------------------------------
# stage 2: truth-referenced recovery at a regenerated budget (near-duplicate
# of g1._truth_rows_for_context, parameterized over the c-ladder's 5 arm
# names instead of g1's module-level ARM_NAMES -- see module docstring)
# ---------------------------------------------------------------------------


def _truth_rows_for_context_c(
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
                for arm in C_ARM_NAMES:
                    rows.append(
                        {**keys, "arm": arm, "c": C_OF_ARM[arm], "e_arm_true": np.nan, "e_orc_true": np.nan}
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
            for arm in C_ARM_NAMES:
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
                    {
                        **keys,
                        "arm": arm,
                        "c": C_OF_ARM[arm],
                        "e_arm_true": e_arm_true,
                        "e_orc_true": e_orc_true,
                    }
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
    contexts = g1._build_world_contexts(world, config, spec)
    arm_bases, _, _ = _c_arm_bases_and_g2(contexts, world)
    all_rows: list[dict[str, Any]] = []
    gates: list[dict[str, Any]] = []
    for rep_idx, context in enumerate(contexts):
        started = time.time()
        arm_bases_rep = {name: arm_bases[name][rep_idx] for name in C_ARM_NAMES}
        rows, gate = _truth_rows_for_context_c(context, arm_bases_rep, spec, budget)
        all_rows.extend(rows)
        gates.append(gate)
        print(
            f"[m4g2] truth b={budget} {world} rep={rep_idx} "
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
    print(f"[m4g2] truth stage done: {world} budget={budget}", flush=True)


# ---------------------------------------------------------------------------
# assemble + adjudicate
# ---------------------------------------------------------------------------


def _slope_ci_excludes_zero(ci: dict[str, float]) -> bool:
    return bool(ci["ci_lo"] > 0.0 or ci["ci_hi"] < 0.0)


def _assemble(output: Path) -> None:
    worlds = list(D1_WORLDS)

    offset_frames = [pd.read_csv(output / f"partial_offset_{w}.csv") for w in worlds]
    offset_rows = pd.concat(offset_frames, ignore_index=True)
    g2_frames = [pd.read_csv(output / f"partial_g2_{w}.csv") for w in worlds]
    g2_rows = pd.concat(g2_frames, ignore_index=True)
    g3_frames = [pd.read_csv(output / f"partial_g3check_{w}.csv") for w in worlds]
    g3_rows = pd.concat(g3_frames, ignore_index=True)
    scalenorm_frames = [pd.read_csv(output / f"partial_scalenorm_{w}.csv") for w in HIGH_GAP_WORLDS]
    scalenorm_rows = pd.concat(scalenorm_frames, ignore_index=True)

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
    expected_offset_rows = len(worlds) * len(C_ARM_NAMES)
    if len(offset_rows) != expected_offset_rows:
        raise RuntimeError(f"offset rows {len(offset_rows)} != expected {expected_offset_rows}")
    expected_truth_rows = len(worlds) * len(TRUTH_BUDGETS) * 8 * 2 * 16 * len(C_ARM_NAMES)
    if len(truth_rows) != expected_truth_rows:
        raise RuntimeError(f"truth rows {len(truth_rows)} != expected {expected_truth_rows}")
    expected_scalenorm_rows = len(HIGH_GAP_WORLDS) * 8 * len(g1.ARM_NAMES)
    if len(scalenorm_rows) != expected_scalenorm_rows:
        raise RuntimeError(
            f"scalenorm rows {len(scalenorm_rows)} != expected {expected_scalenorm_rows}"
        )

    # =========================================================================
    # Part 0.0 world-selection disclosure: reproduce the seed-matched-duplicate
    # evidence from the EXCLUDED worlds' partials (kept on disk, not assembled
    # into any adjudicated table) -- proves the correction from the ORIGINAL
    # 5-fresh-world rule to the CORRECTED 5-fresh-world rule was warranted.
    # =========================================================================
    world_selection_disclosure = {
        "original_fresh_companion_worlds": list(ORIGINAL_FRESH_COMPANION_WORLDS),
        "corrected_fresh_companion_worlds": list(FRESH_COMPANION_WORLDS),
        "seed_matched_duplicates_excluded": list(SEED_MATCHED_DUPLICATES_EXCLUDED),
        "degenerate_d_true_excluded": list(DEGENERATE_D_TRUE_EXCLUDED),
        "degenerate_d_true_excluded_replacement": "topology_mismatch",
        "pairs": [],
    }
    matched_pairs = (
        ("linear_exogenous_selection", "endogenous_source_partition_matched", 101),
        ("fast_return_equal_marginal", "slow_hysteresis_equal_marginal", 211),
    )
    for kept, excluded, seed_offset in matched_pairs:
        kept_offset = pd.read_csv(output / f"partial_offset_{kept}.csv")
        excluded_path = output / f"partial_offset_{excluded}.csv"
        excluded_offset = pd.read_csv(excluded_path) if excluded_path.exists() else None
        kept_g2 = pd.read_csv(output / f"partial_g2_{kept}.csv")
        excluded_g2_path = output / f"partial_g2_{excluded}.csv"
        excluded_g2 = pd.read_csv(excluded_g2_path) if excluded_g2_path.exists() else None
        row = {
            "kept": kept,
            "excluded": excluded,
            "shared_seed_offset": seed_offset,
            "excluded_partial_available": excluded_offset is not None,
        }
        if excluded_offset is not None:
            row["offset_norm_max_abs_diff"] = float(
                (kept_offset["offset_norm"].to_numpy() - excluded_offset["offset_norm"].to_numpy())
            .__abs__().max()
            )
            row["geometric_mean_scale_max_abs_diff"] = float(
                (kept_g2["geometric_mean_scale"].to_numpy() - excluded_g2["geometric_mean_scale"].to_numpy())
                .__abs__()
                .max()
            )
            row["condition_number_max_abs_diff"] = float(
                (kept_g2["condition_number"].to_numpy() - excluded_g2["condition_number"].to_numpy())
                .__abs__()
                .max()
            )
        world_selection_disclosure["pairs"].append(row)

    # =========================================================================
    # G1 ANCHOR summary (c_1.0 vs M4-G1 persisted baseline, 3 HIGH_GAP_WORLDS)
    # =========================================================================
    high_gap_payloads = [g for g in offset_gate_payloads if g["is_high_gap_e2_anchored"]]
    m4g1_truth = _load_m4g1_csv("truth_recovery_rows.csv")
    my_c1_truth = truth_rows[
        (truth_rows["arm"] == "c_1.0") & (truth_rows["world"].isin(HIGH_GAP_WORLDS))
    ]
    baseline_truth = m4g1_truth[m4g1_truth["arm"] == "baseline"]
    truth_join = my_c1_truth.merge(
        baseline_truth,
        on=["world", "repetition", "view", "author", "budget"],
        suffixes=("_mine", "_g1"),
        how="inner",
    )
    expected_truth_join = len(HIGH_GAP_WORLDS) * len(TRUTH_BUDGETS) * 8 * 2 * 16
    if len(truth_join) != expected_truth_join:
        raise RuntimeError(
            f"G1 truth anchor join size {len(truth_join)} != expected {expected_truth_join}"
        )
    truth_anchor_diff = (truth_join["e_arm_true_mine"] - truth_join["e_arm_true_g1"]).abs()
    truth_anchor_max = float(truth_anchor_diff.max(skipna=True))

    g1_anchor = {
        "basis_anchor_max_abs_diff": max(g["basis_anchor_max_abs_diff"] for g in high_gap_payloads),
        "offset_anchor_max_abs_diff": max(
            g["offset_anchor_abs_diff"] for g in high_gap_payloads
        ),
        "scalenorm_anchor_max_abs_diff": max(
            g["scalenorm_anchor_max_abs_diff"] for g in high_gap_payloads
        ),
        "truth_recovery_anchor_max_abs_diff": truth_anchor_max,
        "truth_recovery_anchor_n_rows_compared": int(len(truth_join)),
        "tolerance": G1_ANCHOR_TOLERANCE,
        "worlds": list(HIGH_GAP_WORLDS),
        "pass": bool(
            max(g["basis_anchor_max_abs_diff"] for g in high_gap_payloads) <= G1_ANCHOR_TOLERANCE
            and max(g["offset_anchor_abs_diff"] for g in high_gap_payloads) <= G1_ANCHOR_TOLERANCE
            and (np.isnan(truth_anchor_max) or truth_anchor_max <= G1_ANCHOR_TOLERANCE)
        ),
    }

    # =========================================================================
    # G2 CHANNEL LIVENESS / INVARIANCE (all 8 worlds x 8 reps x 5 c's)
    # =========================================================================
    # Width invariance is a WITHIN-(world,repetition)-CONTEXT claim across the
    # 5 c's (the actual G2 claim: c does not change retained width) -- NOT a
    # claim that width is the same GLOBALLY across different contexts. Width
    # legitimately varies ACROSS contexts (k_retained follows Leg 10's own
    # rank-tolerance cut per (world,rep), exactly the "retained rank is not
    # rigidly 12" variability M4-G1 itself disclosed) -- that is expected and
    # orthogonal to this leg's claim, disclosed separately below, not folded
    # into the invariance gate.
    width_nunique_within_context = g2_rows.groupby(["world", "repetition"])["width"].nunique()
    width_invariant_within_context = bool((width_nunique_within_context == 1).all())
    width_varies_across_contexts = bool(g2_rows["width"].nunique() > 1)

    cond_diff_max = float(g2_rows["condition_number_abs_diff_vs_c1"].max())
    cond_rel_diff_max = float(
        (g2_rows["condition_number_abs_diff_vs_c1"] / g2_rows["condition_number_c1"]).max()
    )
    rel_spectrum_diff_max = float(g2_rows["relative_spectrum_max_abs_diff_vs_c1"].max())
    eigenvectors_all_identical = bool(g2_rows["eigenvectors_identical_array_vs_c1"].all())
    # NOTE: "same object" is FALSE by construction, not a failure -- numpy
    # fancy indexing (`array[:, idx_array]`) always returns a fresh copy, so
    # re-slicing `ingredients["eigenvectors"][:, retained]` per c yields a
    # NEW array object every call even though `ingredients["eigenvectors"]`
    # itself (the unsliced source) is never touched by c at all. The
    # meaningful, actually-claimed invariance is VALUE identity
    # (`eigenvectors_identical_array_vs_c1`, via np.array_equal), which holds
    # exactly; object identity is reported only as a disclosed diagnostic,
    # not part of the gate.
    eigenvectors_all_same_object = bool(g2_rows["eigenvectors_is_same_object_vs_c1"].all())
    frob_ratio_diff_max = float(g2_rows["c_recovered_from_frobenius_ratio_abs_diff"].max())

    g2 = {
        "statement": (
            "for every (world, rep, c), width / condition number / relative "
            "spectrum / eigenvectors are invariant vs the c_1.0 case in the "
            "SAME (world, repetition) context (tolerance 1e-9 relative -- "
            "exact algebraic identity, not a materiality bar), while the "
            "Frobenius norm of the applied whitening operator scales exactly "
            "with c (channel liveness)"
        ),
        "tolerance": G2_INVARIANCE_TOLERANCE,
        "width_invariant_within_context": width_invariant_within_context,
        "width_varies_across_contexts_disclosed_not_gated": width_varies_across_contexts,
        "width_distinct_values_across_all_contexts": sorted(
            int(w) for w in g2_rows["width"].unique()
        ),
        "condition_number_max_abs_diff_vs_c1": cond_diff_max,
        "condition_number_max_relative_diff_vs_c1": cond_rel_diff_max,
        "relative_spectrum_max_abs_diff_vs_c1": rel_spectrum_diff_max,
        "eigenvectors_identical_every_row": eigenvectors_all_identical,
        "eigenvectors_same_object_every_row_diagnostic_only": eigenvectors_all_same_object,
        "channel_live_max_abs_diff_c_recovered_from_frobenius_ratio": frob_ratio_diff_max,
        "all_four_invariances_hold": bool(
            width_invariant_within_context
            and cond_rel_diff_max <= G2_INVARIANCE_TOLERANCE
            and rel_spectrum_diff_max <= G2_INVARIANCE_TOLERANCE
            and eigenvectors_all_identical
        ),
        "channel_is_live": bool(frob_ratio_diff_max <= G2_INVARIANCE_TOLERANCE),
    }

    # =========================================================================
    # G3 (already gated per-world at compute time; assemble the summary)
    # =========================================================================
    g3 = {
        "statement": "truth path at budget=1.0 reproduces the gap-stage-style e_arm_true exactly",
        "max_abs_diff": float(g3_rows["abs_diff"].max()),
        "n_checks": int(len(g3_rows)),
        "tolerance": G3_TOLERANCE,
        "pass": bool(g3_rows["abs_diff"].max() <= G3_TOLERANCE),
    }

    # =========================================================================
    # D1: log-log regression (offset vs c), per world + paired-by-world CI
    # =========================================================================
    offset_wide = offset_rows.pivot(index="world", columns="c", values="offset_norm")
    log_c = np.log(np.array(C_VALUES))
    per_world_fit = []
    for w in worlds:
        y = np.log(offset_wide.loc[w, list(C_VALUES)].to_numpy(dtype=float))
        slope, intercept = np.polyfit(log_c, y, deg=1)
        yhat = slope * log_c + intercept
        ss_res = float(np.sum((y - yhat) ** 2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
        per_world_fit.append(
            {"world": w, "slope": float(slope), "intercept": float(intercept), "r2": r2}
        )
    slope_array = np.array([row["slope"] for row in per_world_fit])
    slope_ci = g1._paired_world_ci(slope_array)  # reused unchanged, n=8/df=7 here
    slope_ci_excludes_zero = _slope_ci_excludes_zero(slope_ci)
    slope_ci_contains_one = bool(slope_ci["ci_lo"] <= 1.0 <= slope_ci["ci_hi"])
    slope_underpowered = bool(slope_ci["half_width"] > G0_SLOPE_HALF_WIDTH_BAR)

    # pooled OLS across all 40 (world, c) points -- disclosed, non-gating companion
    log_c_pooled = np.tile(log_c, len(worlds))
    log_offset_pooled = np.log(
        np.concatenate([offset_wide.loc[w, list(C_VALUES)].to_numpy(dtype=float) for w in worlds])
    )
    pooled = stats.linregress(log_c_pooled, log_offset_pooled)
    pooled_n = len(log_c_pooled)
    pooled_t = float(stats.t.ppf(0.975, df=pooled_n - 2))
    pooled_ci_lo = float(pooled.slope - pooled_t * pooled.stderr)
    pooled_ci_hi = float(pooled.slope + pooled_t * pooled.stderr)

    d1_regression = {
        "statement": (
            "primary: per-world OLS log(offset) ~ log(c) (5 points each), "
            "then a paired-by-world t-interval on the 8 per-world slopes "
            "(g1._paired_world_ci, reused unchanged, n=8/df=7); secondary "
            "(disclosed, non-gating): pooled OLS across all 40 (world,c) "
            "points, ignoring world blocks"
        ),
        "per_world_fit": per_world_fit,
        "primary_paired_by_world": {
            **slope_ci,
            "ci_excludes_zero": slope_ci_excludes_zero,
            "ci_contains_one": slope_ci_contains_one,
            "underpowered": slope_underpowered,
            "bar_half_width": G0_SLOPE_HALF_WIDTH_BAR,
        },
        "secondary_pooled_ols": {
            "n": pooled_n,
            "slope": float(pooled.slope),
            "intercept": float(pooled.intercept),
            "stderr": float(pooled.stderr),
            "rvalue": float(pooled.rvalue),
            "r2": float(pooled.rvalue**2),
            "ci_lo": pooled_ci_lo,
            "ci_hi": pooled_ci_hi,
            "ci_excludes_zero": bool(pooled_ci_lo > 0.0 or pooled_ci_hi < 0.0),
            "ci_contains_one": bool(pooled_ci_lo <= 1.0 <= pooled_ci_hi),
        },
    }

    # =========================================================================
    # G0 POWER -- primary (slope CI) + secondary (endpoint paired CI, disclosed)
    # =========================================================================
    m4e2 = g1._load_m4e2_decision()
    e2_baseline_offsets = {w: float(m4e2["offset_table"][w]["offset_norm"]) for w in HIGH_GAP_WORLDS}
    e2_mean_baseline_offset = float(np.mean(list(e2_baseline_offsets.values())))
    fresh_c1_offsets = {w: float(offset_wide.loc[w, 1.0]) for w in worlds}
    fresh_mean_c1_offset = float(np.mean(list(fresh_c1_offsets.values())))

    endpoint_diffs = (offset_wide[4.0] - offset_wide[0.25]).to_numpy()  # n=8, fresh
    endpoint_ci = g1._paired_world_ci(endpoint_diffs)
    endpoint_bar_e2 = G0_SECONDARY_POWER_FRACTION * e2_mean_baseline_offset
    endpoint_bar_fresh = G0_SECONDARY_POWER_FRACTION * fresh_mean_c1_offset

    g0 = {
        "statement": (
            "PRIMARY (decisive, gates lean a / pivot): paired-by-world (n=8, "
            "FRESH) CI half-width on the mean per-world log-log slope vs a "
            "0.5 bar (half the slope=0-vs-slope=1 discriminating gap). "
            "SECONDARY (disclosed, non-gating, for comparability with "
            "M4-G1's own G0 convention): paired-by-world (n=8, FRESH) CI on "
            "the raw offset difference between the ladder's extremes "
            "(c=4.0 minus c=0.25) vs 12.5% of a baseline offset, reported "
            "against BOTH an E2-ANCHORED baseline (M4-E2's persisted 3-world "
            "mean, 12.999) and this leg's own FRESH 8-world c=1.0 mean"
        ),
        "worlds_fresh_n": 8,
        "worlds_e2_anchored_n": 3,
        "primary_slope_mde": {
            "half_width": slope_ci["half_width"],
            "bar": G0_SLOPE_HALF_WIDTH_BAR,
            "pct_of_bar": (
                100.0 * slope_ci["half_width"] / G0_SLOPE_HALF_WIDTH_BAR
                if not np.isnan(slope_ci["half_width"])
                else float("nan")
            ),
            "underpowered": slope_underpowered,
        },
        "secondary_endpoint_disclosure": {
            "mean_diff_c4_minus_c025": endpoint_ci["mean"],
            "half_width": endpoint_ci["half_width"],
            "ci_lo": endpoint_ci["ci_lo"],
            "ci_hi": endpoint_ci["ci_hi"],
            "e2_anchored_baseline_offsets_3world": e2_baseline_offsets,
            "e2_anchored_mean_baseline_offset": e2_mean_baseline_offset,
            "e2_anchored_bar_12_5pct": endpoint_bar_e2,
            "underpowered_vs_e2_anchored_bar": bool(endpoint_ci["half_width"] > endpoint_bar_e2),
            "fresh_c1_offsets_8world": fresh_c1_offsets,
            "fresh_mean_c1_offset": fresh_mean_c1_offset,
            "fresh_bar_12_5pct": endpoint_bar_fresh,
            "underpowered_vs_fresh_bar": bool(endpoint_ci["half_width"] > endpoint_bar_fresh),
        },
        "equivalence_form": True,
    }

    # =========================================================================
    # LEAN (a) / PIVOT -- UNITS: slope CI excludes 0 (fresh, 8 worlds)
    # =========================================================================
    if slope_underpowered:
        lean_a_status = "UNDERPOWERED"
        pivot_status = "UNDERPOWERED"
    elif slope_ci_excludes_zero:
        lean_a_status = "HOLD"
        pivot_status = "DOES_NOT_FIRE"
    else:
        lean_a_status = "MISS"
        pivot_status = "FIRES"
    lean_a = {
        "statement": "log-log slope of offset_norm against c has a CI excluding 0",
        "slope_point_estimate": slope_ci["mean"],
        "ci_lo": slope_ci["ci_lo"],
        "ci_hi": slope_ci["ci_hi"],
        "ci_contains_one": slope_ci_contains_one,
        "status": lean_a_status,
        "held": bool(lean_a_status == "HOLD"),
    }
    pivot = {
        "registered": "log-log slope CI includes 0 -> THE METRIC IS SCALE-INVARIANT",
        "status": pivot_status,
        "fires": bool(pivot_status == "FIRES"),
    }

    # =========================================================================
    # LEAN (b) -- TRUTH IS SCALE-FREE: all 10 pairwise c-comparisons, both budgets
    #
    # DISCOVERED POST-HOC (after lean (a)/G0/pivot were already finalized above
    # -- this correction touches ONLY lean (b), never revisits lean (a)'s
    # already-computed numbers): `e_orc_true` (the ORACLE-basis reference
    # error -- ARM-INVARIANT by construction, computed identically for every
    # c, so it cannot be biased favorably or unfavorably by anything this leg
    # manipulates) has median ~1e9-1e10 in TWO of the 8 D1 worlds
    # (linear_null_ecology, fast_return_equal_marginal) at BOTH budgets, a
    # 9-10 ORDER-OF-MAGNITUDE jump from the other six worlds' 0.18-0.74 --
    # proof this is a pre-existing near-zero-denominator fragility of
    # `_relative_error` on these two mechanistically low/null-signal worlds'
    # small `D_true` at the regenerated 4x/8x truth budgets, not a property
    # of the c-ladder (their OFFSET data, computed by a completely different
    # code path, was and remains sane -- lean (a) is untouched). M4-G1 never
    # met this because it used only the 3 HIGH_GAP (high-signal, by
    # construction) worlds. Both readings are computed and reported; the
    # NAIVE all-8-world reading is kept only as diagnostic evidence of the
    # pathology, and the VALID-subset reading (median e_orc_true <= 10 at
    # BOTH budgets -- a threshold with 9 orders of magnitude of headroom on
    # both sides, not a close call) is ADOPTED for the held/miss verdict.
    # =========================================================================
    TRUTH_VALIDITY_THRESHOLD = 10.0  # generous; actual gap is ~1e9, see report
    orc_diag_rows = []
    for budget in TRUTH_BUDGETS:
        scoped = truth_rows[
            (truth_rows["budget"] == budget)
            & (~truth_rows["degenerate_reference"])
            & (truth_rows["arm"] == "c_1.0")  # e_orc_true is arm-invariant; any arm works
        ]
        for w in worlds:
            median_e_orc = float(scoped[scoped["world"] == w]["e_orc_true"].median())
            orc_diag_rows.append({"world": w, "budget": budget, "median_e_orc_true": median_e_orc})
    orc_diag = pd.DataFrame(orc_diag_rows)
    worst_per_world = orc_diag.groupby("world")["median_e_orc_true"].max()
    truth_valid_worlds = sorted(worst_per_world[worst_per_world <= TRUTH_VALIDITY_THRESHOLD].index.tolist())
    truth_invalid_worlds = sorted(worst_per_world[worst_per_world > TRUTH_VALIDITY_THRESHOLD].index.tolist())

    author_truth = g1._author_level_truth(truth_rows)  # reused unchanged, generic over "arm"

    def _lean_b_rows_for_worlds(world_subset: list[str]) -> list[dict[str, Any]]:
        rows_out = []
        for budget in TRUTH_BUDGETS:
            scoped = author_truth[
                (author_truth["budget"] == budget) & (author_truth["world"].isin(world_subset))
            ]
            for c_lo, c_hi in itertools.combinations(C_VALUES, 2):
                a_lo, a_hi = ARM_OF_C[c_lo], ARM_OF_C[c_hi]
                r_lo = scoped[scoped["arm"] == a_lo].set_index(["world", "repetition", "author"])
                r_hi = scoped[scoped["arm"] == a_hi].set_index(["world", "repetition", "author"])
                joined = r_lo.join(r_hi, lsuffix="_lo", rsuffix="_hi", how="inner")
                diffs = (joined["e_arm_true_lo"] - joined["e_arm_true_hi"]).to_numpy()
                ci = g1._paired_author_ci(diffs)  # reused unchanged
                within_margin = bool(
                    ci["n"] > 1
                    and ci["ci_lo"] >= -LEAN_B_MARGIN
                    and ci["ci_hi"] <= LEAN_B_MARGIN
                )
                rows_out.append(
                    {
                        "budget": budget,
                        "c_lo": c_lo,
                        "c_hi": c_hi,
                        "n": ci["n"],
                        "mean_diff": ci["mean"],
                        "ci_lo": ci["ci_lo"],
                        "ci_hi": ci["ci_hi"],
                        "half_width": ci["half_width"],
                        "within_margin": within_margin,
                    }
                )
        return rows_out

    lean_b_rows_naive_all8 = _lean_b_rows_for_worlds(list(worlds))
    lean_b_rows_valid_subset = _lean_b_rows_for_worlds(truth_valid_worlds)
    lean_b_held_naive = bool(all(row["within_margin"] for row in lean_b_rows_naive_all8))
    lean_b_held = bool(all(row["within_margin"] for row in lean_b_rows_valid_subset))
    lean_b_rows = lean_b_rows_valid_subset  # adopted reading persisted as the primary CSV

    lean_b = {
        "statement": (
            f"all C(5,2)=10 pairwise c-comparisons, both truth budgets, CI "
            f"entirely inside +/-{LEAN_B_MARGIN} "
            f"(margin justified as {LEAN_B_MARGIN_JUSTIFICATION})"
        ),
        "numerical_validity_diagnostic": {
            "statement": (
                "arm-invariant e_orc_true median per world/budget; worlds "
                f"with max-over-budget median > {TRUTH_VALIDITY_THRESHOLD} "
                "are excluded from the ADOPTED reading (pre-existing "
                "_relative_error near-zero-denominator fragility, unrelated "
                "to the c-ladder -- see module docstring / report)"
            ),
            "threshold": TRUTH_VALIDITY_THRESHOLD,
            "median_e_orc_true_by_world_budget": orc_diag_rows,
            "valid_worlds": truth_valid_worlds,
            "invalid_worlds_excluded": truth_invalid_worlds,
        },
        "naive_all_8_worlds": {
            "n_checks": len(lean_b_rows_naive_all8),
            "per_pair": lean_b_rows_naive_all8,
            "max_abs_half_width": float(max(row["half_width"] for row in lean_b_rows_naive_all8)),
            "held": lean_b_held_naive,
        },
        "adopted_valid_subset": {
            "worlds_used": truth_valid_worlds,
            "n_worlds": len(truth_valid_worlds),
            "n_checks": len(lean_b_rows_valid_subset),
            "per_pair": lean_b_rows_valid_subset,
            "max_abs_half_width": float(
                max(row["half_width"] for row in lean_b_rows_valid_subset)
            ),
            "held": lean_b_held,
        },
        "held": lean_b_held,
    }

    # =========================================================================
    # LEAN (c) -- NORMALIZATION REPAIRS THE ORDERING (M4-G1's 8 arms, 3 worlds)
    # =========================================================================
    scalenorm_by_world_arm = (
        scalenorm_rows.groupby(["world", "arm"])["geometric_mean_scale"].mean().reset_index()
    )
    scalenorm_by_arm = scalenorm_by_world_arm.groupby("arm")["geometric_mean_scale"].mean()

    m4g1_decision = _load_m4g1_decision()
    per_arm = {row["arm"]: row for row in m4g1_decision["per_arm_table"]}
    arms8 = list(g1.ARM_NAMES)
    raw_offset_by_arm = {a: float(per_arm[a]["offset_mean"]) for a in arms8}
    truth4_by_arm = {a: float(per_arm[a]["truth_recovery_error_budget4_median"]) for a in arms8}
    truth8_by_arm = {a: float(per_arm[a]["truth_recovery_error_budget8_median"]) for a in arms8}
    normalized_offset_by_arm = {
        a: raw_offset_by_arm[a] / float(scalenorm_by_arm[a]) for a in arms8
    }

    raw_vec8 = [raw_offset_by_arm[a] for a in arms8]
    norm_vec8 = [normalized_offset_by_arm[a] for a in arms8]
    truth4_vec8 = [truth4_by_arm[a] for a in arms8]
    truth8_vec8 = [truth8_by_arm[a] for a in arms8]

    spearman_raw_8_b4 = stats.spearmanr(raw_vec8, truth4_vec8)
    spearman_raw_8_b8 = stats.spearmanr(raw_vec8, truth8_vec8)
    spearman_norm_8_b4 = stats.spearmanr(norm_vec8, truth4_vec8)
    spearman_norm_8_b8 = stats.spearmanr(norm_vec8, truth8_vec8)

    # n=7 cross-check: reproduce M4-G1's own disclosed -0.786 (raw offset, budget=4x)
    arms7 = [a for a in arms8 if a != "baseline"]
    raw_vec7 = [raw_offset_by_arm[a] for a in arms7]
    truth4_vec7 = [truth4_by_arm[a] for a in arms7]
    spearman_raw_7_b4 = stats.spearmanr(raw_vec7, truth4_vec7)
    m4g1_disclosed_spearman = -0.786
    spearman_anchor_abs_diff = abs(float(spearman_raw_7_b4.statistic) - m4g1_disclosed_spearman)

    argmin_raw = arms8[int(np.argmin(raw_vec8))]
    argmin_norm = arms8[int(np.argmin(norm_vec8))]

    budget4_not_negative = bool(spearman_norm_8_b4.statistic >= 0)
    budget8_not_negative = bool(spearman_norm_8_b8.statistic >= 0)
    identity_is_argmin_norm = bool(argmin_norm == "identity")
    both_budgets_agree = bool(budget4_not_negative == budget8_not_negative)
    lean_c_held = bool(
        budget4_not_negative
        and budget8_not_negative
        and not identity_is_argmin_norm
    )
    lean_c = {
        "statement": (
            "under the Part 0.1 scale-normalized offset, across M4-G1's "
            "eight arms (n=8, baseline included, as registered), the "
            "Spearman correlation with truth error is no longer negative "
            "AND identity is no longer the minimum -- held only if both "
            "hold at BOTH truth budgets"
        ),
        "correctness_anchor_n7_raw_spearman_budget4x": float(spearman_raw_7_b4.statistic),
        "m4g1_disclosed_value": m4g1_disclosed_spearman,
        "correctness_anchor_abs_diff": spearman_anchor_abs_diff,
        "raw_offset_by_arm": raw_offset_by_arm,
        "geometric_mean_scale_by_arm": {a: float(scalenorm_by_arm[a]) for a in arms8},
        "scale_normalized_offset_by_arm": normalized_offset_by_arm,
        "truth_error_budget4_by_arm": truth4_by_arm,
        "truth_error_budget8_by_arm": truth8_by_arm,
        "spearman_raw_n8_budget4": float(spearman_raw_8_b4.statistic),
        "spearman_raw_n8_budget8": float(spearman_raw_8_b8.statistic),
        "spearman_normalized_n8_budget4": float(spearman_norm_8_b4.statistic),
        "spearman_normalized_n8_budget8": float(spearman_norm_8_b8.statistic),
        "argmin_raw_offset_arm": argmin_raw,
        "argmin_normalized_offset_arm": argmin_norm,
        "budget4_not_negative": budget4_not_negative,
        "budget8_not_negative": budget8_not_negative,
        "both_budgets_agree": both_budgets_agree,
        "identity_is_argmin_normalized": identity_is_argmin_norm,
        "held": lean_c_held,
    }

    # =========================================================================
    # D2: width companion (all eight M4-G1 arms, purely derived, no new compute)
    # =========================================================================
    m4g1_offset_full = _load_m4g1_csv("offset_rows.csv")
    d2_rows = []
    for arm in arms8:
        scoped = m4g1_offset_full[m4g1_offset_full["arm"] == arm]
        offset_mean = float(scoped["offset_norm"].mean())
        width = int(scoped["width"].iloc[0])
        d2_rows.append(
            {
                "arm": arm,
                "offset_mean": offset_mean,
                "width": width,
                "offset_over_sqrt_width": offset_mean / np.sqrt(width),
            }
        )

    # =========================================================================
    # verdict
    # =========================================================================
    if pivot_status == "UNDERPOWERED":
        verdict = "UNDERPOWERED_NO_ADJUDICATION"
    elif pivot_status == "FIRES":
        verdict = "PIVOT_METRIC_SCALE_INVARIANT"
    else:
        verdict = "METRIC_UNITS_DISQUALIFIED"

    decision = {
        "estimand_id": "SUICA_M4_G2_METRIC_UNITS",
        "tier": "EXPLORATORY (open-exploration phase)",
        "registered_in": (
            "docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md M4-G2 registration "
            "(2026-08-03, BEFORE run); ledger row M4-G2"
        ),
        "d1_worlds_fresh": list(worlds),
        "d1_worlds_e2_anchored_subset": list(HIGH_GAP_WORLDS),
        "d1_worlds_fresh_companion": list(FRESH_COMPANION_WORLDS),
        "world_selection_disclosure": world_selection_disclosure,
        "c_values": list(C_VALUES),
        "c_arm_names": list(C_ARM_NAMES),
        "truth_budgets": list(TRUTH_BUDGETS),
        "gates": {"G0": g0, "G1": g1_anchor, "G2": g2, "G3": g3},
        "d1_regression": d1_regression,
        "d2_width_companion": d2_rows,
        "lean_a": lean_a,
        "lean_b": lean_b,
        "lean_c": lean_c,
        "pivot": pivot,
        "verdict": verdict,
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only (8 for D1: 3 E2-anchored + "
            "5 fresh companions; 3 for lean (c), M4-G1's own set); "
            "truth-referenced recovery via budget-regenerated (4x/8x events) "
            "finite panels from the frozen world law, compared to the "
            "analytic D_true; no natural-text, personality, or clinical "
            "claim; no seal, no independent verification (operator "
            "directive 2026-08-01)."
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
                "G1_anchor": g1_anchor,
                "G2_channel_liveness_invariance": g2,
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
    truth_rows.to_csv(output / "truth_recovery_rows.csv", index=False)
    g2_rows.to_csv(output / "g2_invariance_evidence.csv", index=False)
    g3_rows.to_csv(output / "g3_check_rows.csv", index=False)
    scalenorm_rows.to_csv(output / "scale_norm_rows.csv", index=False)
    pd.DataFrame(per_world_fit).to_csv(output / "d1_loglog_per_world_slopes.csv", index=False)
    pd.DataFrame(d2_rows).to_csv(output / "d2_width_companion.csv", index=False)
    pd.DataFrame(lean_b_rows_valid_subset).to_csv(
        output / "lean_b_pairwise_equivalence.csv", index=False
    )
    pd.DataFrame(lean_b_rows_naive_all8).to_csv(
        output / "lean_b_pairwise_equivalence_naive_all8_worlds.csv", index=False
    )
    orc_diag.to_csv(output / "lean_b_truth_validity_diagnostic.csv", index=False)

    print(
        json.dumps(
            {
                "verdict": verdict,
                "g0_slope_underpowered": slope_underpowered,
                "g1_pass": g1_anchor["pass"],
                "g2_all_invariances_hold": g2["all_four_invariances_hold"],
                "g2_channel_is_live": g2["channel_is_live"],
                "g3_pass": g3["pass"],
                "lean_a_status": lean_a_status,
                "lean_b_held": lean_b_held,
                "lean_c_held": lean_c_held,
                "pivot_status": pivot_status,
                "slope_mean": slope_ci["mean"],
                "slope_ci": [slope_ci["ci_lo"], slope_ci["ci_hi"]],
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
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "m4_g2_metric_units")
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
    if args.world not in D1_WORLDS:
        raise SystemExit(f"not a registered D1 world: {args.world}")

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
