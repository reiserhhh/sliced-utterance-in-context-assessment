# SUICA M4-G — Objective Redesign Line: registrations and outcomes

Opened 2026-08-03, immediately after the M4-F panel design line closed
(`docs/SUICA_M4_F_PANEL_DESIGN_SYNTHESIS.md`). This document holds every
registration and outcome of the line, in order, append-only. The claims ledger
controls; nothing here may exceed its tier.

## Why this line exists

Two independent arcs converged on the same remaining problem.

- **M4-D Leg 14 → M4-E2**: the discovery objective carries a systematic frame
  displacement whose common offset is DISTRIBUTED (largest single piece is the
  residual at .40–.45), world-specific in direction at the permutation null,
  and not removable by any single term — removing the dominant term DOUBLES
  the gap. Verdict `OFFSET_SPREAD_NO_SINGLE_OBJECTIVE_TERM`. Its registered
  hand-off named the **scale family** as the largest IDENTIFIABLE carrier
  (~1/3 of mass in the registered sequential order, ~1/2 standalone,
  dominated by the `n2` component: the principal column-scale modes
  `{A v_i v_i^T}` — first-order motion of the consensus under re-scaling its
  principal column directions, i.e. **the freeze whitening's unregularized
  1/sqrt(eig) amplification**). The supervised block is irrelevant. M4-E2 also
  disclosed that its own sub-40% clause is knife-edged and order-sensitive:
  the honest reading is "no term above ~half the mass under any ordering".
- **M4-F1..F9**: the panel side is closed. A finite panel can be made
  self-consistent and cannot be made trait-certifying. If a trait-level object
  is reachable at all, the remaining lever is the objective, not the data.

M4-E2 DECOMPOSED the offset. This line INTERVENES on it.

## Standing rules inherited from M4-F (all four apply to every leg here)

1. Designed-null and decorrelation-style gates state their aggregation rule
   and multiplicity treatment BEFORE the run.
2. Every leg pre-states the scale at which its target is measurably non-zero
   (citing the prior leg's persisted numbers) and the minimum detectable
   effect its design affords; a null at the target's noise floor is reported
   UNDERPOWERED, never as a null.
3. Every leg verifies from the generator/operator that its manipulation has a
   NON-ZERO causal channel at every tested parameter value; a null on an inert
   knob is reported VACUOUS, never as a null.
4. Every gate bounds MATERIALITY through an equivalence form — the confidence
   interval must lie inside a margin justified from the generator or the
   effect size — never nil significance on a known-nonzero quantity.

---

## M4-G1 registration (2026-08-03, BEFORE run) — is the scale family an actionable lever, or only a carrier?

**Question.** M4-E2 showed the whitening's amplification family carries the
largest identifiable share of the offset. Carrying mass is not the same as
being fixable. Does REGULARIZING that amplification actually reduce the
discovery objective's frame displacement — and if it does, does the reduction
transfer to truth, or does it merely improve the objective's self-consistency
while leaving (or worsening) what the objective recovers?

The second half is not optional. This program has twice measured
self-consistency and truth moving in opposite directions: Leg 12 (a cleaning
intervention improved every loop statistic while lowering truth-referenced
attribution .7264 → .6677) and M4-F5 (the gauge rose 63x while trait-like
recovery plateaued). An offset reduction that does not transfer is a cosmetic
result and must be reported as one.

**Design.** Reuse Leg 14 / M4-E2's persisted world and objective path exactly;
the ONLY thing that varies is the whitening applied inside the discovery
objective:

- `baseline` — the deployed unregularized whitening (1/sqrt(eig)). Must
  reproduce the persisted offset and gap (gate G1).
- `shrinkage` — 1/sqrt(eig + lambda) over a registered ladder
  lambda / median(eig) in {0.01, 0.1, 1.0}.
- `truncated` — drop the smallest-eigenvalue directions (precisely those the
  1/sqrt(eig) map amplifies most) over a registered ladder retaining
  {90%, 75%, 50%} of spectral mass.
- `identity` — no whitening at all: the extreme control that distinguishes
  "regularize the amplification" from "whitening is the problem".

Same worlds, same repetitions, and the same paired-by-world statistics M4-E2
used, so arms are compared within world.

**Metrics, both mandatory at every arm.**
1. OFFSET/GAP — M4-E2's own persisted objective metric, unchanged.
2. TRUTH-REFERENCED RECOVERY — computed by the identical path on the world's
   known structure, in the M4-F5 style (register the operationalization in
   Part 0 before compute; report at least two variants with their sensitivity,
   since this is the leg's main researcher degree of freedom).

**Leans.**
(a) ACTIONABLE: at least one shrinkage or truncation setting reduces the
    offset by >= 25% relative to baseline, paired-by-world CI excluding zero.
(b) IT TRANSFERS: at the setting that minimizes the offset, truth-referenced
    recovery IMPROVES over baseline, paired CI excluding zero — under BOTH
    truth variants, or the lean MISSES.
(c) NOT SIMPLY "WHITENING BAD": the `identity` arm is worse than the best
    regularized arm on the offset metric.

**PIVOT-IF:** no arm reduces the offset by >= 25% with a paired CI excluding
zero -> THE SCALE FAMILY IS EXONERATED AS A LEVER. It carries mass without
being actionable, the redesign target moves to the residual block (.40–.45 of
the mass, the largest single piece), and the next registered question becomes
the objective's FUNCTIONAL FORM rather than its scaling.

A second, separately recorded outcome: if (a) HOLDS but (b) MISSES, the
finding is that the scale family is a **cosmetic** lever — offset reduction
without truth transfer — which is a result about the objective metric itself
and must be reported as prominently as a success would have been.

**Gates.**
- **G0 POWER** — pre-state the baseline offset/gap level from M4-E2's
  persisted artifacts and the minimum detectable paired difference this design
  affords. If the realized paired CI half-width exceeds 12.5% of the baseline
  offset (half of lean (a)'s 25% bar), the leg is UNDERPOWERED and adjudicates
  nothing.
- **G1 ANCHOR** — the `baseline` arm reproduces M4-E2 / Leg 14's persisted
  offset and gap to <= 1e-12 on identical world seeds.
- **G2 CHANNEL LIVENESS** — for every non-baseline arm, demonstrate the
  whitening operator actually moved: report the spectrum or condition number
  of the applied whitening beside baseline's, with an equivalence-form
  statement of what counts as "materially different". An arm that does not
  move the operator is INERT and its result is reported VACUOUS, not as a null.
- **G3 TRUTH-PATH INVARIANCE** — the truth-referenced path must be the
  identical objective path differing only in its input; demonstrate with a
  degenerate equality check (M4-F5 and M4-F9 both achieved exactly 0.0).
- **G4 MATERIALITY FORM** — every gate in this leg is stated as an
  equivalence/margin bound; no gate may be a nil-significance test on a
  known-nonzero quantity. State this compliance explicitly.

Tier: EXPLORATORY, label-free, synthetic. Artifacts:
`results/m4_g1_whitening_intervention/`; report
`reports/SUICA_M4_G1_WHITENING_INTERVENTION_REPORT.md`.

## M4-G1 outcome (2026-08-03, appended)

**PIVOT DOES NOT FIRE. Lean (a) HOLDS, lean (b) MISSES decisively under both
truth variants, lean (c) MISSES. Verdict:
`COSMETIC_LEVER_OFFSET_WITHOUT_TRANSFER`.** G0 and G2 first, as the standing
rules require: G0 POWER is a mixed picture (3 of 6 candidate arms
underpowered at the n=3-world replication ceiling) but lean (a)'s HOLD rests
on `truncated_90` alone, which IS adequately powered (half-width 98.1% of
the 12.5%-of-baseline-offset bar, 52.8% reduction, paired 95% CI [5.28,
8.46]) — not on underpowered noise. G2 CHANNEL LIVENESS passes for every one
of the seven non-baseline arms by a wide margin (smallest relative
condition-number change 43.3%, vs a 10% materiality bar). G1 ANCHOR and G3
TRUTH-PATH INVARIANCE both pass at floating-point-epsilon / exact 0.0.

At the arm the registration's own rule selects for lean (b) — `truncated_50`,
the candidate with the single lowest mean offset (5.19, a 59.9% reduction) —
truth-referenced recovery does not transfer, it collapses: `e_arm_true` rises
from baseline's ~0.567 to ~0.928 at BOTH truth-recovery budgets (4x and 8x
events, regenerated from the frozen world law per Leg 4 Part 4b's own
machinery), paired 95% CI entirely on the "worse" side at both
(n=384 author-reps each). Lean (c) MISSES outright: `identity` (zero
amplification) has the single LOWEST offset of all eight arms tested,
including every regularized candidate — not merely "not worse," an
inversion of the registered expectation.

A disclosed, non-gating companion computed identically for every arm
(paired, author-level, both budgets) sharpens the finding into a
dose-response: `shrinkage_0.01` and `shrinkage_0.1` — the two mildest
settings, offset reductions 10.9% and 24.9% — show small but statistically
real truth-recovery IMPROVEMENTS (CIs entirely positive at both budgets).
`shrinkage_0.1` misses the registered 25% actionable bar by 0.14 percentage
points (24.86%), a knife-edge disclosure in the same spirit as M4-E2's own
sub-40% clause. `shrinkage_1.0` (42.1% reduction) is ambiguous (CI includes
zero). Every arm at or past 50%+ reduction (the three truncated arms,
identity) shows large, decisive worsening. Spearman(offset, recovery error)
across the 7 non-baseline arms = −0.786 (descriptive, n=7, not a registered
test): lower offset associates with WORSE recovery, not better. **The scale
family carries mass and is a real, adequately-powered lever on the offset
metric — but only its mildest, sub-actionable settings preserve or help
truth; every setting that clears the registered "actionable" bar makes
recovery worse, and the setting with the single lowest offset (identity) is
the second-worst for recovery of all eight arms tried.**

Full numbers, gates, per-arm table, and the dose-response table:
`reports/SUICA_M4_G1_WHITENING_INTERVENTION_REPORT.md`. Artifacts:
`results/m4_g1_whitening_intervention/{decision.json, gates.json,
offset_rows.csv, gap_rows.csv, truth_recovery_rows.csv,
g2_spectrum_evidence.csv, g3_check_rows.csv}`.

**Hand-off.** Neither the PIVOT's clean exoneration nor a usable estimator
fix is licensed: the scale family plainly IS an offset-metric lever (lean a),
and is plainly NOT a truth-transferring one past its mildest settings (lean
b). The open question this leaves for the next registration in this line is
sharply framed by the dose-response table: whether a NARROWER shrinkage
ladder concentrated between this leg's "real but sub-bar" (~0.01–0.1) and
"ambiguous" (~1.0) points can find a setting that is both actionable (>=25%
offset reduction) and truth-transferring, or whether — as the monotone
Spearman pattern suggests — those two properties are in this objective's
structure fundamentally in tension, in which case the redesign target moves,
as the PIVOT branch would have directed, to the residual block or the
objective's functional form.

## M4-G1 planner adjudication note (2026-08-03, appended) — the target metric is now the suspect

The leg is adjudicated as the agent reported it: lean (a) HOLD on
`truncated_90` (the one arm that clears 25% AND is adequately powered,
52.8% reduction, paired CI [5.28, 8.46]), lean (b) MISS decisively under both
truth variants, lean (c) MISS by inversion, pivot does not fire, verdict
`COSMETIC_LEVER_OFFSET_WITHOUT_TRANSFER`.

**But the arm table says something sharper than "cosmetic", and it points at
the metric rather than at the lever:**

| arm | offset | width | truth error @4x |
|---|---|---|---|
| baseline | 12.999 | 13 | 0.5562 |
| shrinkage_0.01 | 11.571 | 13 | 0.5512 |
| shrinkage_0.1 | 9.755 | 13 | 0.5539 |
| shrinkage_1.0 | 7.503 | 13 | 0.5751 |
| truncated_90 | 6.129 | 4 | 0.8801 |
| truncated_75 | 5.572 | 3 | 0.9085 |
| truncated_50 | 5.190 | 2 | 0.9574 |
| **identity** | **4.352** | 13 | 0.8656 |

The offset falls MONOTONICALLY as the whitening is weakened, and the single
lowest offset in the whole table belongs to `identity` — no whitening at all —
whose truth error is 56% worse than baseline's. Across the seven non-baseline
arms the offset and the recovery error are anti-correlated at Spearman −.786.
**Minimizing the registered target makes the objective worse at its job.**

Two mechanisms could produce that, and they have very different consequences:

1. **Units.** `offset_norm` is a norm in a space whose metric the whitening
   itself sets. Weakening the whitening shrinks every distance in that space,
   so the measured offset falls without anything improving. If so, the metric
   cannot be compared across arms with different whitening scales — and
   M4-E2's attribution of ~1/3–1/2 of the offset mass to the scale family may
   itself be a units statement rather than a structural one.
2. **A real trade-off.** The displacement genuinely trades against recovery,
   and the objective cannot have both.

There is also a plain **width confound** sitting on top of either: the
truncated arms carry width 4/3/2 against baseline's 13, and a norm over fewer
dimensions is mechanically smaller.

The two mechanisms are cheaply separable and the next leg separates them. Note
what is at stake: under mechanism 1, this line's stated target — and part of
the prior leg's decomposition — is disqualified as an optimization objective.

One more thing the leg found that the registered leans could not score, and
which survives either mechanism: the two MILDEST arms (shrinkage .01 and .1)
are the only ones whose truth recovery genuinely IMPROVES, both with CIs
entirely on the better side — and shrinkage_0.1 misses the registered 25%
actionable bar by 0.14 points (24.86%). The bar selected exactly the arms that
hurt. That is recorded here as a registration critique, not as a rescue: no
lean is re-scored on it.

## M4-G2 registration (2026-08-03, BEFORE run) — is the offset metric measuring the world or its own units?

**Question.** Does `offset_norm` inherit the whitening's units (and the
retained width), or is it scale-invariant? The answer decides whether M4-G1's
anti-correlation — and part of M4-E2's decomposition — is an artifact or a
finding.

**Design, in two registered diagnostics.**

- **D1, the pure-scale ladder (decisive).** Take the deployed baseline
  whitening W and form arms `c*W` for c in {0.25, 0.5, 1.0, 2.0, 4.0}. This
  changes NOTHING structural: identical eigenvectors, identical relative
  spectrum, identical condition number, identical width. It is a pure change
  of units. Measure `offset_norm` and the truth-referenced recovery at every
  c, on the M4-G1 world/objective path, unchanged.
- **D2, the width companion.** Report `offset_norm / sqrt(width)` alongside
  the raw value for all eight M4-G1 arms, to separate the dimension-count
  effect from the scale effect. Declared as a diagnostic, not a new target.

**Leans.**
(a) UNITS: the log-log slope of `offset_norm` against c has a CI excluding 0
    (report the point estimate and state plainly whether the CI contains 1).
(b) TRUTH IS SCALE-FREE: truth-referenced recovery is invariant across the c
    ladder — equivalence form, all pairwise differences inside +/- 0.02,
    a margin justified as ~4% of baseline truth error (.556).
(c) NORMALIZATION REPAIRS THE ORDERING: under a scale-normalized offset
    (registered in Part 0 before compute, together with its justification),
    the Spearman correlation between offset and truth error across M4-G1's
    eight arms is no longer negative, and `identity` is no longer the minimum.

**PIVOT-IF:** the log-log slope CI includes 0 -> THE METRIC IS SCALE-INVARIANT.
M4-G1's anti-correlation is then a real property of the objective: reducing
displacement genuinely costs recovery, M4-E2's scale-family attribution stands
as structural, and the redesign faces a true trade-off rather than a units bug
— which becomes the line's next registered question and a substantially harder
one.

**Gates.**
- **G0 POWER** — M4-E2's anchored world count is only 3 (M4-G1 reported 3 of
  6 candidate arms underpowered at that ceiling). Run the c ladder on MORE
  worlds (target 8) since it is a fresh measurement, and state explicitly
  which comparisons are E2-anchored (3 worlds) and which are fresh (8). Report
  the realized MDE; underpowered comparisons adjudicate nothing.
- **G1 ANCHOR** — c=1.0 reproduces M4-G1's persisted `baseline` offset and
  truth recovery to <= 1e-12 on identical world seeds.
- **G2 CHANNEL LIVENESS** — show that each c actually changes the applied
  whitening operator while leaving eigenvectors, relative spectrum, condition
  number and width unchanged; this is what makes D1 a pure-units manipulation
  rather than a structural one. Report all four invariances explicitly.
- **G3 TRUTH-PATH INVARIANCE** — degenerate equality check, as in M4-G1.
- **G4 MATERIALITY FORM** — every gate an equivalence/margin bound; state
  compliance per gate.

Tier: EXPLORATORY, label-free, synthetic. Artifacts:
`results/m4_g2_metric_units/`; report
`reports/SUICA_M4_G2_METRIC_UNITS_REPORT.md`.

## M4-G2 outcome (2026-08-03, appended)

**PIVOT DOES NOT FIRE. The log-log slope of `offset_norm` against a pure
whitening-scale multiplier c is 0.8796, paired-by-world (n=8, fresh) 95% CI
[0.8386, 0.9206] — materially nonzero, adequately powered (half-width 8.2%
of the 0.5 bar), and sub-linear (the CI excludes both 0 AND 1). Per the
registration's own branch: `offset_norm` is DISQUALIFIED as an optimization
target in its raw form.** Lean (a) HOLDS. Lean (b) MISSES decisively — truth
recovery is not scale-free; it improves monotonically and precisely as c
rises (error .786→.422 at budget=4x across the ladder on the 6 numerically-
valid worlds, 18 of 20 pairwise checks decisively outside the ±0.02
equivalence margin, up to 15x). Lean (c) HOLDS decisively: under the
registered scale-normalized offset (offset divided by the geometric mean of
an arm's own per-direction scale factors), the Spearman correlation between
offset and M4-G1's truth error flips from M4-G1's disclosed −0.786 to
**+0.833** (identical at both truth budgets, no disagreement), and
`identity` — M4-G1's spuriously "best" arm on raw offset — becomes the
single WORST-scoring arm once normalized, now consistent with its actual
poor truth-recovery. G0 primary (the slope CI, the decisive test) is
emphatically not underpowered. G1 ANCHOR and G3 TRUTH-PATH INVARIANCE both
pass at 0.0. G2 shows all four registered invariances (eigenvectors,
relative spectrum, condition number, width) hold to floating-point
exactness within every context while the whitening operator's Frobenius
norm scales with c exactly — D1 is confirmed pure units, not structure.
Verdict: **`METRIC_UNITS_DISQUALIFIED`.**

**Two world-selection corrections and one statistical-validity correction
were made mid-compute, all disclosed in full with both readings given, none
altering lean (a)/pivot's already-finalized numbers.** (1) `leg3._world_seed`'s
own pre-existing `matched_groups` table shares seeds across
`{linear_exogenous_selection, endogenous_source_partition_matched}` and
`{fast_return_equal_marginal, slow_hysteresis_equal_marginal}`; both pairs
produced bit-identical (0.0 diff) `offset_norm`/G2 evidence despite genuinely
different dynamic mechanisms — a deterministic, outcome-blind exclusion of
each pair's second member was applied BEFORE any hypothesis-relevant number
existed. (2) The replacement `linear_exogenous_selection` was then found
degenerate (`D_true` below `FLIP_TOLERANCE`) on all 256 of its
(rep,view,author) combinations — G3 inapplicable — and was replaced by
`topology_mismatch` (checked non-degenerate from the archive before running
it), again before any hypothesis-relevant number existed for the world in
question. (3) AFTER lean (a)/pivot were finalized, lean (b)'s naive
all-8-world computation produced nonsense means (10^8-10^9 scale); the
arm-invariant diagnostic `e_orc_true` showed two worlds
(`linear_null_ecology`, `fast_return_equal_marginal`) with median ~5e9 vs
0.18-0.74 in the other six — a pre-existing `_relative_error`
near-zero-denominator fragility on these two low/null-signal worlds' small
`D_true` at the regenerated truth budgets, unrelated to the c-ladder (their
OFFSET data remained sane throughout). Lean (b) was recomputed on the valid
6-world subset (adopted) with both readings persisted; the MISS verdict
holds under both.

**Consequence for M4-E2's scale-family attribution, stated precisely as the
registration requires**: M4-E2's decomposition was computed once, at a
single fixed operator's own units, and never compared offset magnitudes
across operators of different intrinsic scale — as a description of which
displacement directions dominate AT that one fixed operator, it is not
directly tested or overturned here. What IS undermined — demonstrated
directly by lean (c)'s sign flip from −0.786 to +0.833 — is treating raw
`offset_norm` as comparable, scale-free evidence ACROSS operators whose own
intrinsic scale differs, which is exactly the cross-arm design M4-G1 used
(arms whose geometric-mean-scale spans 32.6x to 1.0x): M4-G1's own headline
"identity has the lowest offset" finding is shown here to be substantially a
units artifact of that specific comparison, not evidence about the arms'
relative structural quality.

Full numbers, gates, the c-ladder table (offset and both truth variants per
c), the per-world log-log regression table, the D2 width-companion table,
and the full lean (b)/(c) tables (both naive and adopted readings):
`reports/SUICA_M4_G2_METRIC_UNITS_REPORT.md`. Artifacts:
`results/m4_g2_metric_units/{decision.json, gates.json, offset_rows.csv,
truth_recovery_rows.csv, g2_invariance_evidence.csv, g3_check_rows.csv,
scale_norm_rows.csv, d1_loglog_per_world_slopes.csv, d2_width_companion.csv,
lean_b_pairwise_equivalence.csv,
lean_b_pairwise_equivalence_naive_all8_worlds.csv,
lean_b_truth_validity_diagnostic.csv}`.

**Hand-off.** The raw discovery objective (`offset_norm`) is disqualified as
an optimization target — M4-G1's own cross-arm comparisons built on it
(including its central "identity is best" finding) inherit this
disqualification. A scale-normalized version (Part 0.1 of this leg) is
demonstrated, on M4-G1's own 8 arms, to repair the ordering into one
directionally consistent with actual truth-recovery quality. The open
question for the next registration in this line is whether that
normalized metric (or a refinement of it) is viable as a REPLACEMENT
optimization target in its own right — checked here only on the 8-arm,
3-world setting M4-G1 already ran, not on a fresh design of its own — and,
separately, whether the genuine (non-units) scale-vs-recovery relationship
this leg found on the pure c-ladder (bigger c: worse raw offset, but BETTER
truth recovery, opposite-signed to M4-G1's own non-uniform-regularization
finding) reflects something about this objective's functional form that a
normalized-offset redesign would need to reconcile.

## M4-G2 planner adjudication note (2026-08-03, appended) — one artifact killed, one lever uncovered

The verdict stands as adjudicated: slope .8796 [.8386, .9206] on a manipulation
whose four invariances were confirmed at exactly 0.0, so **`offset_norm` is
DISQUALIFIED as an optimization target in its raw form**. Lean (c) shows the
repair works: under the pre-registered scale-normalized offset, Spearman with
truth error flips from M4-G1's −.786 to **+.833**, and `identity` moves from
raw-offset minimum to normalized-offset maximum. The width companion rules out
the dimension-count explanation (identity's offset/sqrt(width) = 1.207 is
still the minimum). M4-E2's own decomposition is NOT overturned — it never
varied c — but M4-G1's cross-arm raw-offset comparisons, including its
"identity is best" reading, inherit the disqualification.

**Lean (b)'s MISS is the more interesting half, and it is a finding, not a
failure.** Truth recovery was registered as scale-free and is not: it improves
MONOTONICALLY along the ladder, .786 → .646 → .525 → .451 → .422, with 18 of
20 pairwise CIs outside the ±.02 equivalence band. Since c is provably a pure
change of units — eigenvectors, relative spectrum, condition number and width
all identical to 0.0 — recovery cannot depend on it unless something
DOWNSTREAM of the whitening compares a scale-carrying quantity against a FIXED
ABSOLUTE CONSTANT. Multiplying the whitening by 4 then effectively weakens
that constant, and recovery improves by 20% of its own magnitude.

That is a third instrument finding in this line's short life, and unlike the
first two it points at a repair rather than a retraction: if a fixed constant
is being compared against a quantity whose scale is arbitrary, making it
RELATIVE should deliver the c=4 improvement at c=1 — a real gain rather than a
units trick. The next leg tests exactly that, and is registered to fail loudly
if the scale dependence is not localizable in identifiable constants.

Process note, recorded because it is the standard here: the executing agent
hit three mechanical problems (two colliding world seeds; a degenerate
replacement world; a near-zero-denominator blowup in two worlds' relative
error) and disclosed each with its resolution — the first two fixed before any
hypothesis-relevant number existed, the third found only AFTER lean (a) and
the pivot were finalized, recomputed on the valid 6-world subset with both
readings persisted and the MISS holding under each.

## M4-G3 registration (2026-08-03, BEFORE run) — turn the units artifact into a repair

**Question.** M4-G2 proved something downstream of the whitening compares a
scale-carrying quantity against a fixed absolute constant, because a pure unit
change moved truth recovery .786 → .422. Can that dependence be localized in
identifiable constants, and does making them SCALE-ADAPTIVE deliver the c=4
recovery at c=1?

**Part 0 audit (before any compute, and gated).** Enumerate every constant in
the objective path that is compared against, added to, or thresholds a
scale-carrying quantity — regularizers, convergence tolerances, rank or
support thresholds, floors, clip bounds. Publish the inventory in the report
with file and line references. This inventory IS the leg's hypothesis space;
constants discovered later may be reported but may not be scored.

**Design.** Reuse M4-G2's world set (8 worlds, the valid-subset rule from its
lean (b) carried over verbatim) and objective path.

- `baseline` — c=1.0 as deployed (anchor).
- `c4_reference` — c=4.0, the improvement to be matched (also an anchor: must
  reproduce M4-G2's persisted c=4 recovery to <=1e-12).
- `adaptive_<k>` — one arm per inventoried constant, with that constant alone
  made relative to a declared data-scale statistic (registered in Part 0),
  everything else at c=1.0.
- `adaptive_all` — every inventoried constant made relative simultaneously.

**Leans.**
(a) LOCALIZABLE: at least one single-constant `adaptive_<k>` arm recovers
    >= 50% of the c=4 truth-recovery gain at c=1 (gain measured as
    baseline_error − c4_error, per budget), paired-by-world CI excluding zero.
(b) DEFINITIONAL CHECK: the winning adaptive arm's truth recovery is invariant
    across the c ladder {0.25, 1.0, 4.0} — equivalence form, all pairwise
    differences inside +/- .02. This is what distinguishes a genuine
    scale-adaptive repair from a lucky reparameterization.
(c) NO NEW COSMETIC TRADE: the scale-normalized offset at the winning arm does
    not worsen relative to baseline (equivalence form, margin registered in
    Part 0).

**PIVOT-IF:** no single-constant arm reaches 50% of the gain AND `adaptive_all`
also fails to -> the scale dependence is NOT localized in identifiable
constants. The redesign target then moves to the objective's FUNCTIONAL FORM,
and this line's remaining hypothesis (that the displacement problem is a
scaling problem at all) is retired.

**Gates.**
- **G0 POWER** — pre-state the c=4 gain from M4-G2's persisted artifacts and
  the design's MDE; underpowered comparisons adjudicate nothing.
- **G1 ANCHOR** — `baseline` and `c4_reference` reproduce M4-G2's persisted
  values to <=1e-12 on identical world seeds.
- **G2 CONSTANT LIVENESS** — for every inventoried constant, demonstrate it
  actually carries scale dependence: perturb it alone at c=1 and show truth
  recovery moves, in equivalence form against a registered margin. A constant
  that does not move recovery is INERT, is reported as such, and its adaptive
  arm's null is VACUOUS rather than a null.
- **G3 TRUTH-PATH INVARIANCE** — degenerate equality check, as in G1/G2.
- **G4 MATERIALITY FORM** — every gate an equivalence/margin bound; state
  compliance per gate.

Tier: EXPLORATORY, label-free, synthetic. Artifacts:
`results/m4_g3_scale_adaptive/`; report
`reports/SUICA_M4_G3_SCALE_ADAPTIVE_REPORT.md`.

## M4-G3 outcome (2026-08-03, appended)

**This outcome lands outside every registered branch, and is reported as
such — neither HOLD, nor a clean MISS, nor PIVOT FIRES.** Part 0's audit
found six Category A constants on the truth-recovery call graph
(`hazard_ridge`, an IRLS convergence tolerance, an IRLS weight floor, a
logit clip bound, a finite-difference probe epsilon, and the basis's own
literal intercept column) plus two Category B constants provably confined
to the offset/GPA path alone (excluded from adaptive arms by call-graph
inspection, not by empirical test). **`hazard_ridge` is confirmed, on
four converging lines of evidence, as the (or the dominant) IDENTIFIABLE,
LOCALIZED source of M4-G2's proven scale dependence**: (i) a provable a
priori argument (an L2 penalty of the form `ridge·n·I` breaks the exact
diagonal-reparameterization invariance unregularized IRLS otherwise has —
textbook reason ridge implementations standardize features first); (ii)
the adaptive ridge value (`hazard_ridge_deployed · mean(raw retained
eigenvalues)`) is consistent and directionally stable across all 64
sampled contexts (0.00023–0.00089, always 4.6–18% of the deployed 0.005,
never crossing zero); (iii) its well-powered author-level companion CI
(n≈745, the SAME grain lean (b) itself uses) decisively excludes zero,
recovering 69–72% of the c=4 gain at both budgets ([0.0399,0.0628]@4x,
[0.0488,0.0727]@8x); (iv) the other five constants are cleanly,
adequately-powered nulls (`tolerance`/`weight_floor`/`clip_bound`/
`probe_epsilon`, CIs within ~1e-4 of exactly [0,0]) or a small real
negative (`intercept`), at the identical grain, ruling out "everything
moves a little" as an alternative story. **But `hazard_ridge`'s own
REGISTERED test — paired-by-world (n=6) — is severely underpowered: half-
width ≈0.08 against a 25%-of-gain bar of ≈0.02, a >4x gap, disclosed in G0
from M4-G2's own persisted numbers BEFORE any adaptive-arm compute ran**
(the same design also leaves M4-G2's own raw c=4 gain barely/not
significant at this grain — not a property invented for this leg). Per
the standing rule that a null at the noise floor is reported UNDERPOWERED,
lean (a) is UNDERPOWERED for `hazard_ridge`/`adaptive_all` (not MISS), and
the **PIVOT is therefore UNDERPOWERED, not FIRES and not DOES-NOT-FIRE** —
FIRES requires every arm to be a *clean* MISS, and an underpowered
comparison cannot supply that. **Separately, and decisively (well-powered,
n=745, all 3 pairwise c-comparisons × 2 budgets, every CI outside ±0.02):
LEAN (b) MISSES.** The adaptive-ridge formula does not deliver invariant
recovery across c∈{0.25,1,4} — it produces an inverted-U, worst at c=0.25,
best at c=1.0 (its own calibration point), worse again at c=4.0 (though
still better than c=0.25): mean diffs +0.084/+0.093 (0.25 vs 1, both
budgets) and −0.034/−0.024 (1 vs 4, both budgets), every CI clear of the
margin by 1.5–5x. Lean (c) HOLDS trivially and exactly: `hazard_ridge`'s
basis is bit-identical to baseline's (0.0 max abs diff, all 8 worlds × 8
reps × 3 roles — verified structurally, not merely argued), so its offset
cannot have moved. G1 ANCHOR passes at exactly 0.0 (8,192 truth rows + 16
offset rows vs M4-G2's persisted `c_1.0`/`c_4.0`). G3 passes at exactly
0.0 (72 checks, all 9 arms × 8 worlds).

**Verdict: `hazard_ridge` is the identified, load-bearing localized
constant, but no formula tested here is CERTIFIED as a genuine, general
repair** — lean (b), the gate explicitly built to distinguish a real
repair from a lucky reparameterization, MISSES decisively and
mechanistically-interpretably (the formula fixes ridge's ABSOLUTE value
from context-level raw eigenvalues alone, not its ratio to each c's own
realized design scale, so it only lands well at its own calibration point,
c=1). The hypothesis that M4-G2's scale dependence is a scaling problem is
**neither retired nor confirmed solved**: `hazard_ridge` is now the
identified target for any future repair attempt, which must register a
c-DEPENDENT (not merely context-dependent) functional form and MUST re-run
lean (b) as its own certification gate — reusing this leg's localization
finding is legitimate; skipping lean (b) would not be.

Full numbers, gates, the Part 0 constant inventory with file/line
references, the per-arm summary table, and the full lean (a)/(b)/(c)
tables: `reports/SUICA_M4_G3_SCALE_ADAPTIVE_REPORT.md`. Artifacts:
`results/m4_g3_scale_adaptive/{decision.json, gates.json,
truth_recovery_rows.csv, author_level_truth_rows.csv, context_meta.csv,
offset_rows.csv, e_orc_true_validity_diagnostic.csv,
lean_a_per_constant.csv, g2_liveness_per_constant.csv,
lean_b_pairwise_equivalence.csv}`.

**Hand-off.** The next registration in this line, if this hypothesis is
pursued further, must do two things this leg deliberately did not do
(doing either after seeing lean (b)'s MISS would be a post-hoc rescue):
(1) register a scale-adaptive ridge formula that is a function of each
ARM's own realized design scale (not only the deployed baseline's raw
eigenvalues), so that it is well-defined and, by construction, testable
for genuine c-invariance rather than single-point calibration; (2)
reconsider the registered statistical grain for truth-recovery gates —
this leg's own G0 and M4-G2's own lean (b) both found the author-level
(n≈745) grain adequately powered where the world-level (n=6) grain was
not, so a future leg's PRIMARY test should either use a finer-grained
pairing (e.g. paired-by-world×repetition) or explicitly register a larger
world set. Absent either, the PIVOT question this leg's own registration
posed remains formally undecided, even though the weight of (non-
adjudicating) evidence leans toward "does not fire."

## M4-G3 planner adjudication note (2026-08-03, appended) — the constant is found; the repair is not certified

**What is established.** The scale dependence M4-G2 proved is localized in ONE
constant: `hazard_ridge` (deployed 0.005,
`suica_core/m4_chart_ecology_estimator.py:341-342`), on four converging lines
of evidence — a priori math, an adaptive value consistent across all 64
contexts at 4.6–18% of deployed, a decisive well-powered author-grain effect
(CI [.040,.063] @4x, [.049,.073] @8x), and clean nulls on the other five
inventoried constants (tolerance, weight floor, clip bound, probe epsilon all
INERT at both grains; intercept small and NEGATIVE). Its adaptive arm recovers
89.5%/95.5% of the c=4 gain at world grain (69.2%/72.3% author grain, CI
excluding zero) at c=1, with the basis bit-identical to baseline — so lean (c)
holds trivially and no cosmetic trade was made.

**Why that is not yet a repair.** Lean (b), the gate registered precisely to
separate a genuine scale-adaptive fix from a lucky reparameterization, MISSES
decisively (n=745, all six pairwise checks outside ±.02). The adaptive arm's
recovery is an inverted-U across c: worst at .25, best at 1.0, worse again at
4.0. The mechanism is visible in the formula: the declared data-scale
statistic is `RAW_SCALE = mean(raw retained eigenvalues)`, which is computed
BEFORE whitening and is therefore c-INVARIANT, while the quantity the ridge
regularizes lives AFTER whitening and scales with c. So the fix is calibrated
at the deployed scale and cannot follow the scale it was built to track. It is
context-adaptive, not scale-adaptive.

**Pivot: outside every registered branch, and correctly reported as such.**
Firing requires every arm to be a clean MISS; `hazard_ridge` and
`adaptive_all` are UNDERPOWERED at the registered world grain, not MISS. The
agent flagged that underpowering from M4-G2's persisted gain BEFORE running
any adaptive arm, and declined to resolve the branch by picking a side.

**Fifth planner registration defect, and its rule.** G0 required a pre-stated
MDE but did not specify the analysis GRAIN, so the line's default (paired by
world, n=6–8) was inherited — and it is structurally underpowered for effects
of this size by more than 4x, while the author grain (n≈745) is adequately
powered and was available all along. **Standing rule (fifth): the analysis
grain must be chosen for power against the registered bar and justified before
the run; inheriting the line's default grain is not a justification.**

## M4-G4 registration (2026-08-03, BEFORE run) — the c-covariant ridge, at a grain that can see it

**Question.** M4-G3 localized the scale dependence in `hazard_ridge` but its
adaptive formula keyed off a pre-whitening statistic and so could not follow
c. Does a ridge keyed off a POST-whitening scale statistic — one that scales
with c by construction — deliver c-invariant recovery without losing the gain?

**Design.** Reuse M4-G3's world set, objective path, arms plumbing and truth
variants. **The registered analysis grain is the AUTHOR grain (n≈745)**, per
the fifth standing rule; world-grain numbers are reported as a companion and
adjudicate nothing.

- `baseline` — deployed ridge at c=1 (anchor to M4-G3's persisted value).
- `g3_raw_scale` — M4-G3's adaptive arm, the known point fix (anchor).
- `covariant_<k>` — one arm per registered post-whitening scale statistic,
  ridge = alpha * stat, with the statistic computed on the whitened quantity
  the ridge is actually added to. Register the candidate statistics AND the
  alpha calibration rule in Part 0 before compute; alpha must be fixed by a
  rule (e.g. matching the deployed ridge at c=1), never tuned on outcomes.
- Each arm evaluated across c in {0.25, 1.0, 4.0}.

**Leans.**
(a) C-COVARIANCE: at least one `covariant_<k>` arm is c-invariant at the
    author grain — all pairwise differences across c inside ±.02.
(b) NO LOSS: that arm's recovery at c=1 is not worse than `g3_raw_scale`'s
    (equivalence form, margin registered in Part 0).
(c) SPECIFICITY: the same covariant rule applied to one of M4-G3's INERT
    constants does NOT produce c-invariance — the control that shows the ridge
    is the mechanism rather than the rescaling being cosmetic anywhere.

**PIVOT-IF:** no covariant candidate achieves c-invariance -> the dependence
is not a simple ridge-scaling issue, M4-G3's localization is incomplete, and
the redesign target moves to the objective's FUNCTIONAL FORM. That is the
consequence M4-G3's own pivot could not deliver, and this leg is registered to
deliver it either way.

**Gates.**
- **G0 POWER** — at the AUTHOR grain, against the c=4 gain persisted by
  M4-G3; state the MDE and the bar before adjudicating. World-grain companion
  numbers may not be used to adjudicate anything.
- **G1 ANCHOR** — `baseline` and `g3_raw_scale` reproduce M4-G3's persisted
  values to <=1e-12 on identical world seeds.
- **G2 COVARIANCE LIVENESS** — for every `covariant_<k>`, demonstrate the
  realized ridge value actually scales with c (report ridge(c=.25),
  ridge(c=1), ridge(c=4) and their ratios). A candidate whose ridge does not
  move with c is by definition not covariant: report it as INERT and its
  result as VACUOUS, not as a null.
- **G3 TRUTH-PATH INVARIANCE** — degenerate equality check.
- **G4 MATERIALITY FORM** — every gate an equivalence/margin bound; state
  compliance per gate.

Tier: EXPLORATORY, label-free, synthetic. Artifacts:
`results/m4_g4_covariant_ridge/`; report
`reports/SUICA_M4_G4_COVARIANT_RIDGE_REPORT.md`.

## M4-G4 outcome (2026-08-03, appended)

**The PIVOT FIRES, cleanly — the one thing M4-G3's own pivot attempt could
not do.** Two post-whitening statistics were registered (`covariant_var`,
the direct post-whitening analogue of `RAW_SCALE`; `covariant_msq`, the more
literal uncentered-second-moment reading of "the quantity the ridge is
added to"), both provably homogeneous-degree-2 in c
(`POST_SCALE_k(context,c) = c²·POST_SCALE_k(context,1)`, an exact algebraic
identity from `whitening = c·whitening0`, confirmed empirically to 10+
significant figures in the pooled G2 gate: realized ridge ratios exactly
16.0/0.0625 at c=4/c=0.25 vs c=1, in direct contrast to `g3_raw_scale`'s own
exactly-1.0 ratio, M4-G3's own flaw reproduced as a clean number). At the
registered AUTHOR grain (n=745, well-powered — the decisive comparison's
half-width, 0.0056, is barely over half the 0.01 power bar, not a marginal
call), **both candidates cut the raw c-dependence by 89.1% relative to doing
nothing to `hazard_ridge`** (the specificity control, `weight_floor` treated
by the identical rule, reproduces `baseline`'s own raw swing almost exactly
and is decisively confirmed NOT c-invariant on all six checks — the
reduction is specific to `hazard_ridge`, not a generic artifact) **— but the
residual 10.9% is itself decisively outside the registered ±0.02 margin**
(CI [0.026, 0.037] @4x on the deciding c=0.25-vs-c=4.0 pair, clearing the
margin by 30–36% of its own width, both arms, both budgets). Lean (a)
MISSES cleanly for both arms; lean (c) SPECIFICITY is decisively CONFIRMED;
lean (b) (disclosed companion, officially unreached since lean (a) never
HOLDS) also MISSES decisively — at c=1 the covariant arms sit at
`baseline`'s own worse level, not `g3_raw_scale`'s better one, exactly the
pre-registered mechanistic prediction (alpha calibrated to match deployed
ridge at c=1, not `g3_raw_scale`'s much weaker value). G1 anchor and G3
truth-path invariance both pass at exactly 0.0.

**Per the registration's own consequence for a firing pivot: the dependence
is not a simple ridge-scaling issue, M4-G3's localization is incomplete, and
the redesign target moves to the objective's FUNCTIONAL FORM.** The
mechanism was registered, not discovered post-hoc: Part 0 disclosed, before
compute, that `_hazard_design` mixes columns built from the whitened basis
(which does satisfy the c-scaling identity, and which a covariant ridge can
compensate) with columns built from raw world data
(`generated_current`/`duration`) and from the *unscaled* intercept
sub-column crossed with `response_next` (`feedback_0_d`/`gate_0_d`) — these
do not scale with c and are not compensated by any scalar ridge, however it
is keyed. G2's own numbers make this concrete: the ridge itself is exactly
covariant (16.0/0.0625, floating-point exact) while only 89.1% of the
recovery swing it was meant to fix actually closes — the gap lives
downstream of the ridge's value, in how the design is assembled from
mismatched column types.

**Two mechanical items, both caught and disclosed before any
hypothesis-relevant number was compromised.** (1) An early G1-anchor draft
attempted to independently re-verify `g3_raw_scale`'s c=0.25/4.0 values
against M4-G3's own persisted winner-ladder files — but `g3_raw_scale` is,
by this leg's own registered compute-scope reduction, never computed away
from c=1 in this leg's new compute, so the join correctly found 0 rows and
raised the assembly's own `expected != len(joined)` assertion; fixed by
removing the invalid anchor attempt (this arm's c=1 anchor, the only point
this leg newly computes for it, remains independently verified at exactly
0.0) — caught after all 8 worlds' truth-stage compute had already completed
and persisted, but before it affected any lean, gate, or truth-recovery row.
(2) `covariant_var` and `covariant_msq` turned out numerically
near-indistinguishable throughout (differ in the 3rd–4th decimal) — a
registered open question in Part 0 (whether a role's raw features are
zero-mean relative to `center`), resolved empirically rather than by
assumption, and reported as a real finding rather than suppressed.

Full numbers, gates, the Part 0 statistic/calibration/specificity-control
registration, the per-arm × per-c table, and the full lean (a)/(b)/(c)
tables: `reports/SUICA_M4_G4_COVARIANT_RIDGE_REPORT.md`. Artifacts:
`results/m4_g4_covariant_ridge/{decision.json, gates.json, calibration.json,
truth_recovery_rows.csv, author_level_truth_rows.csv, context_meta.csv,
e_orc_true_validity_diagnostic.csv, g2_ridge_vs_c.csv,
g0_and_lean_pairwise_rows.csv}`.

**Hand-off.** This line's original hypothesis — that M4-G2's scale
dependence is a pure scaling problem, fixable by making one absolute
constant relative to a data-scale statistic — is now closed out at the
functional-form boundary it was always going to meet: `hazard_ridge` is
confirmed, on two independent legs and four converging lines of evidence
(M4-G3) plus a fifth (this leg's specificity control), as the dominant
identifiable channel, and a genuinely covariant ridge closes the large
majority (89.1%) of it — but not all, and the shortfall is structural, not
a matter of finding a better statistic or a better alpha. The next
registration in this line, if pursued, should not test a third
`ridge = alpha · stat` variant (a fourth instance of a functional form this
leg and M4-G3 together have now closed out) but should examine whether a
column-type-aware treatment of the hazard design itself — separately
regularizing or rescaling the `generated_current`/`duration`/
`feedback_0_d`/`gate_0_d` blocks that do not share the whitened basis's own
c-scaling — can close the remaining 10.9%. Absent that, the line's own
honest position is that M4-G2's scale-dependence finding is majority-
explained and majority-repairable by a single constant, with a real,
quantified, structurally-located remainder.

## M4-G4 planner adjudication note (2026-08-03, appended) — the opaque problem now has a named mechanism

The pivot fires cleanly, and unlike M4-G3 it fires on adequately powered
evidence: the twelve comparisons deciding lean (a) all carry half-widths
<= .0056 against a .01 bar. Lean (a) MISSES on the c=.25-vs-4.0 pair
(CI [.026,.037] @4x, clearing the ±.02 margin by 30–36%), lean (b) MISSES,
lean (c) SPECIFICITY is CONFIRMED decisively (the inert-constant control shows
3.2–17.4x larger non-invariance on the same pairs). G2 is exact: the covariant
ridges realize c-ratios of exactly 16.0 and 0.0625 in floating point, matching
the algebra, while `g3_raw_scale`'s ridge ratio is exactly 1.0 — M4-G3's
diagnosed flaw reproduced as a measured number rather than an inference.

**No repair is certified, and the registered consequence stands: the target
moves to the objective's FUNCTIONAL FORM.** But the leg did far more than fire
a pivot. A scalar covariant ridge closes **89.1%** of the raw c-dependence,
and the residual 10.9% has an identified structural cause:

> `_hazard_design` mixes columns of different scale provenance — c-scaled
> columns built from the whitened basis alongside c-invariant ones
> (`generated_current` / `duration`, taken from raw data;
> `feedback_0_d` / `gate_0_d`, crossed with the unscaled intercept).
> **No single scalar ridge can be scale-consistent across a design matrix
> whose columns do not share a scale.**

That is worth stating plainly against where this line started. M4-E2 handed
over "a distributed, world-specific frame displacement, largest single piece
the residual at .40–.45, no single term removable". Four legs later the same
phenomenon reads: the discovery objective regularizes a design matrix with
heterogeneous column scaling using one scalar constant, so its behaviour
inherits the whitening's units and no scalar fix — adaptive or covariant — can
be scale-consistent. The problem moved from a statistical mystery to a named
structural defect with an obvious candidate remedy.

M4-G3's localization is sharpened rather than overturned: `hazard_ridge`
remains the dominant channel; it is simply the wrong SHAPE of knob.

## M4-G5 registration (2026-08-03, BEFORE run) — per-column scaling: does the named defect have the obvious fix?

**Question.** M4-G4 named the mechanism: one scalar regularizer applied to a
design matrix whose columns do not share a scale. Does making the
regularization PER-COLUMN — so each column is regularized in its own units —
complete the repair that scalar covariance could only take to 89.1%?

**Design.** Reuse M4-G4's worlds, objective path, arms plumbing, truth
variants and gate helpers. **Registered analysis grain: AUTHOR (n≈745)**, per
the fifth standing rule; world-grain numbers are companions and adjudicate
nothing. Every arm evaluated across c in {0.25, 1.0, 4.0}.

- `baseline` (anchor), `g3_raw_scale` (anchor: the best point fix at c=1),
  `covariant_var` (anchor: M4-G4's best scalar covariant, 89.1% closed).
- `column_standardized` — standardize each `_hazard_design` column to unit
  scale before the ridge is applied, so the single ridge acts in common units.
- `diagonal_ridge` — a per-column ridge proportional to each column's own
  scale statistic (registered in Part 0), leaving the design untouched.
- A specificity control carried over from M4-G4: the same per-column rule
  applied where it should do nothing.

Register in Part 0, before compute: the column-scale statistic, the
calibration rule fixing overall strength (it must reproduce the deployed ridge
at c=1 in the homogeneous-column limit), and the exact column inventory of
`_hazard_design` with each column's scale provenance (c-scaled vs c-invariant)
stated from the code, with file:line references.

**Leans.**
(a) COMPLETION: at least one per-column arm is c-invariant at the author grain
    — all pairwise differences across c inside ±.02, i.e. it clears the bar
    M4-G4's scalar covariant missed by 30–36%.
(b) NO LOSS: that arm's recovery at c=1 is not worse than `g3_raw_scale`'s
    (equivalence form, margin registered in Part 0).
(c) QUANTITATIVE IMPROVEMENT: the residual c-dependence it leaves is smaller
    than the scalar covariant's 10.9%, reported on the same statistic M4-G4
    used so the two numbers are comparable.

**PIVOT-IF:** no per-column arm achieves c-invariance -> the scale
heterogeneity is NOT confined to the design matrix's columns. The defect is
then deeper than column scaling — in the hazard model's structure rather than
its parameterization — and the line's next question becomes whether the
displacement is IRREDUCIBLE at this level of the objective, which would be a
result about the objective's construction rather than about any knob in it.

**Gates.**
- **G0 POWER** at the AUTHOR grain against M4-G4's persisted effects; state
  the MDE and bar before adjudicating; world-grain companions adjudicate
  nothing.
- **G1 ANCHOR** — `baseline`, `g3_raw_scale` and `covariant_var` reproduce
  M4-G4's persisted values to <=1e-12 on identical world seeds.
- **G2 COLUMN-SCALE LIVENESS** — report the spread of column scales BEFORE
  and AFTER each per-column treatment (e.g. max/min ratio across columns), at
  every c. A treatment that does not materially reduce the spread is not the
  registered manipulation: report it INERT and its result VACUOUS.
- **G3 TRUTH-PATH INVARIANCE** — degenerate equality check.
- **G4 MATERIALITY FORM** — every gate an equivalence/margin bound; state
  compliance per gate.

Tier: EXPLORATORY, label-free, synthetic. Artifacts:
`results/m4_g5_per_column_ridge/`; report
`reports/SUICA_M4_G5_PER_COLUMN_RIDGE_REPORT.md`.

## M4-G5 outcome (2026-08-03, appended)

**The PIVOT DOES NOT FIRE. Lean (a) COMPLETION HOLDS decisively for BOTH
per-column arms — not a knife-edge, but floating-point exact.**
`column_standardized`'s recovery is bit-identical (0.0 paired difference,
all 745 authors, both budgets, all three c-pairs) across c ∈ {0.25, 1.0,
4.0}; `diagonal_ridge`'s is invariant to 1–4×10⁻¹⁴ (ordinary floating-point
roundoff). Both are seven-plus orders of magnitude inside the registered
±0.02 margin, at the registered AUTHOR grain (n=745), on comparisons that
carry essentially zero residual uncertainty (paired differences ≈0, so the
standard error itself is ≈0 — the strongest possible non-underpowered case,
not merely an adequately-powered one). **Lean (c) QUANTITATIVE IMPROVEMENT
HOLDS decisively for both arms, at both budgets: the residual c-dependence
M4-G4 left at 10.9% of the raw swing is closed to 0.0% (`column_standardized`,
exact) and ~3–8×10⁻¹² % (`diagonal_ridge`, floating-point zero) — 11–12
orders of magnitude smaller than M4-G4's own residual, on the identical
statistic.** Lean (c) SPECIFICITY is separately, decisively CONFIRMED: the
identical mechanism applied to `weight_floor` (M4-G3-inert) produces large,
non-invariant swings (0.06–0.30, all six checks OUTSIDE the margin,
reproducing M4-G4's own persisted specificity-control numbers exactly) — the
repair is specific to `hazard_ridge`, not a generic artifact. G2 shows both
mechanisms unambiguously LIVE: `column_standardized` collapses the design's
own column-variance spread from 38.8×–908.1× (growing with c, as the c² vs
c⁰ column split predicts) to *exactly* 1.0× at every c; `diagonal_ridge`'s
realized ridge spread exactly tracks that same 38.8×–908.1× heterogeneity,
up from the deployed scalar's perfectly uniform 1.0×. G1 anchor (32,768
rows across 4 anchor arms, including `specificity_weight_floor` at all
three c — an additional disclosed anchor beyond the registration's three
named arms, required by this leg's adopted reading of "carried over from
M4-G4") and G3 truth-path invariance (112 checks) both pass at exactly 0.0.
The column inventory (1,050 columns, 8 worlds × 4 hazard models, classified
by direct empirical comparison of designs built at c=1 vs c=2) confirms the
Part 0.1 analytical claim with zero exceptions: every column of
`_hazard_design` is exactly degree-0 or exactly degree-1 in c, no column
ever mixes both.

**But lean (b) NO LOSS MISSES decisively for both arms.** At c=1, both
arms' recovery is *worse* than `g3_raw_scale`'s by 0.051–0.062 (both
budgets, CI entirely on the worse side) — almost exactly M4-G4's own
persisted c=4 gain (0.059/0.068) — landing within 0.0002–0.0019 of
`baseline`'s own (worse) c=1 level, not `g3_raw_scale`'s (better) one.
**The mechanism is traceable directly to a Part 0 design choice, disclosed
there though its lean (b) consequence was not explicitly forecast**: both
`column_standardized`'s ridge (`ridge_deployed`, unmodified) and
`diagonal_ridge`'s calibration constant (fixed so the homogeneous-column
limit reproduces `ridge_deployed` exactly) are anchored to the *deployed*
value, never to `g3_raw_scale`'s much weaker, specially-fit one — the
identical pattern M4-G4 itself predicted and confirmed for its own scalar
covariant arms, now found, unprompted, to recur in this leg's per-column
arms. Achieving invariance was therefore never, by this registered
construction, also going to recover `g3_raw_scale`'s specific gain.

**This outcome satisfies neither of the registration's two named branches,
stated plainly rather than forced or softened.** "Repair CERTIFIED" requires
lean (a) HOLD *and* no loss — lean (b)'s decisive MISS fails that. "PIVOT
FIRES" requires every arm to MISS lean (a) — neither does, and lean (a)'s
HOLD is not a marginal or underpowered one. The honest, load-bearing
finding: **invariance — the property this whole `M4-G` line has chased
since M4-G1 — is now fully and completely solved, by two independently-derived
mechanisms that agree with each other and with a provable, pre-registered
mathematical argument (Part 0.5) exceeding M4-G4's own base-route-only
guarantee; recovering `g3_raw_scale`'s specific numerical gain is a
distinct, separable, still-open calibration-anchor question, not a further
symptom of the column-heterogeneity defect.** G2's own evidence makes the
separation mechanistic, not merely observed: the ridge/design manipulation
is unambiguously LIVE and the resulting fit is unambiguously invariant,
while the *level* that invariant fit settles at is a direct, provable
consequence of which absolute constant (`ridge_deployed`) the per-column
rule was registered to reproduce in the homogeneous limit.

**Two mechanical items, both caught and fixed during the pre-compute
`--stage inventory` smoke-testing pass, before any hypothesis-relevant
truth-recovery number existed.** (1) `diagonal_ridge`'s naive formula
(`ridge_j = K·var_j`, no fallback) gave `condition_0` — a literal-1 column
structurally identical to the ridge-exempt `intercept` — a ridge of exactly
0, reintroducing the `intercept`/`condition_0` collinearity the deployed
scalar ridge's own uniform nonzero value was incidentally preventing;
`np.linalg.solve` raised `LinAlgError: Singular matrix` on the
`feedback`/`gate` routes. Fixed by falling back to the plain deployed ridge
for any non-exempt, degenerate column, mirroring `column_standardized`'s own
"leave a degenerate column unscaled" rule — making the two arms'
degenerate-column treatment consistent by construction, not by coincidence.
(2) An early diagnostic mis-labeled `_fit_logistic_columnstd`'s first return
value (`beta`, the un-rescaled coefficient in original units, expected to
vary with c) as `gamma` (the standardized-space fit Part 0.5 predicts is
c-invariant), producing an apparently large discrepancy that contradicted
the independently-verified fact that the standardized design itself was
bit-identical across c. Traced to the mislabeling by directly re-deriving
`design_std` equality (0.0 diff) before touching the comparison code; fixed
by adding an explicit `coefficient_std` return value. Neither item touched
any world's actual `--stage truth` compute; all 8 worlds' truth-stage runs
completed with zero Tracebacks, RuntimeErrors, LinAlgErrors, or Killed
signals.

Full numbers, gates, the Part 0 column inventory/statistic/calibration-rule
registration (including the two-mechanism provable-invariance argument),
the per-arm × per-c table, and the full lean (a)/(b)/(c) tables:
`reports/SUICA_M4_G5_PER_COLUMN_RIDGE_REPORT.md`. Artifacts:
`results/m4_g5_per_column_ridge/{decision.json, gates.json,
calibration_source.json, column_inventory.csv,
g2_column_scale_spread_evidence.csv, provable_invariance_spot_check.csv,
truth_recovery_rows.csv, author_level_truth_rows.csv, context_meta.csv,
e_orc_true_validity_diagnostic.csv, g0_and_lean_pairwise_rows.csv}`.

**Hand-off.** This line's central question — is M4-G2's proven scale
dependence a scaling problem at all, and if so, where does it live — is now
closed with a complete, mechanistically-verified answer: it lived entirely
in `_hazard_design`'s mixture of c-scaled and c-invariant columns under one
shared scalar regularizer, and a genuinely per-column treatment (either of
two independently-derived constructions) removes it completely, to
floating-point exactness, confirmed at the row level across 745 authors and
specific to the named constant by a decisive control. What remains open is
narrower and different in kind from anything this line has asked before:
not a structural-defect question but a calibration-selection one — whether
a per-column rule anchored to `g3_raw_scale`'s own (better, but itself only
context-adaptive, not c-covariant, per M4-G3's own diagnosed flaw) level,
rather than to the deployed ridge's homogeneous-limit value, can be both
invariant and at least as good, or whether `g3_raw_scale`'s specific gain
was itself an artifact of its own single-point calibration that a
principled, non-tuned per-column rule has no obligation to reproduce. If
pursued, the next leg in this line should register that calibration
question directly rather than testing a third structural variant of the
per-column family this leg has now closed out.

## M4-G5 planner adjudication note (2026-08-03, appended) — invariance solved exactly; strength is the remaining variable

**Two decisive HOLDs and one decisive MISS, none of them ambiguous.**

Lean (a) HOLDS to machine precision: `column_standardized` is BIT-IDENTICAL
across c (0.0), `diagonal_ridge` invariant to 1–4e-14, both backed by the
pre-registered provable linear-reparameterization argument and both
route-general rather than base-route-limited. Lean (c) HOLDS: M4-G4's residual
10.9% closes to 0.0% and ~1e-12% respectively — eleven to twelve orders of
magnitude. G2 shows the mechanisms are live and enormous (column-scale spread
38.8x/59.6x/908.1x before standardization, 1.0000000000002x after).

The column inventory is itself a result worth keeping: across 1,050 columns,
8 worlds and 4 models, **every column of `_hazard_design` is exactly degree-0
or exactly degree-1 in c — never mixed, zero ambiguous cases.** The
heterogeneity M4-G4 named is therefore exactly binary, which is precisely why
a per-column treatment can remove it exactly rather than approximately.

**So the scale problem this line has chased since M4-G2 is SOLVED, provably
and exactly. And it did not buy the recovery.** Lean (b) MISSES decisively:
both invariant arms sit at BASELINE's recovery level (.5583) rather than
`g3_raw_scale`'s better one (.5068), a gap of .051–.062 that is about the size
of M4-G4's whole c=4 gain.

The reason is visible and was predicted by M4-G4 for its own arms: the
registered calibration for both per-column arms anchors overall strength to
the DEPLOYED ridge, while `g3_raw_scale`'s advantage came from being WEAKER
than deployed (M4-G3 measured its adaptive value at 4.6–18% of deployed). So
the per-column arms inherited deployed's strength — and with it deployed's
recovery — while gaining exact invariance.

**That separates two things this line had been treating as one.** Scale
invariance is a property of the ridge's SHAPE (per-column vs scalar) and is
now solved. Recovery quality is a property of its STRENGTH, and remains
untouched. The registration's two named branches both assumed the repair
would arrive as a single package; it did not, and neither branch applies
cleanly. Recorded as an outside-every-branch outcome, exactly as reported.

## M4-G6 registration (2026-08-03, BEFORE run) — shape and strength together, or a real trade-off

**Question.** M4-G5 solved invariance with the ridge's SHAPE at deployed
STRENGTH. M4-G3 found the recovery gain at a WEAKER strength with the wrong
shape. Does the combination — per-column shape at the weaker strength — give
both, or do invariance and recovery genuinely trade off?

**Design.** Reuse M4-G5's worlds, objective path, arms plumbing, column
inventory, truth variants and gate helpers. **Registered analysis grain:
AUTHOR (n≈745).** Every arm evaluated across c in {0.25, 1.0, 4.0}.

- Anchors: `baseline`, `g3_raw_scale`, `column_standardized` at deployed
  strength (all must reproduce M4-G5's persisted values to <=1e-12).
- `colstd_alpha_<k>` — `column_standardized` at an overall-strength ladder
  alpha/deployed in {0.05, 0.10, 0.20, 0.50, 1.00}, chosen to bracket the
  4.6–18% band M4-G3 measured. The ladder is registered here and may not be
  extended after seeing results; if the optimum sits at an endpoint, say so
  and register any extension as a separate leg.

**Leans.**
(a) INVARIANCE IS STRENGTH-FREE: every `colstd_alpha_<k>` arm remains
    c-invariant within ±.02 (expected to be exact by M4-G5's
    reparameterization argument — this lean tests that the argument does not
    depend on strength).
(b) RECOVERY RECOVERED: at some alpha, recovery is not worse than
    `g3_raw_scale`'s at c=1 (equivalence form, margin registered in Part 0),
    paired CI at the author grain.
(c) TUNING IS ALSO SCALE-FREE: the alpha that minimizes recovery error is the
    SAME at c=0.25, 1.0 and 4.0. This is the sharpest of the three — if the
    best alpha itself moves with c, then invariance of the OUTPUT was not
    enough and the objective's TUNING remains scale-bound.

**PIVOT-IF:** no alpha in the registered ladder is both c-invariant and at
least as good as `g3_raw_scale` -> INVARIANCE AND RECOVERY GENUINELY TRADE
OFF at this objective. That is a structural limit of the current construction,
not a tuning failure, and the line's next question becomes whether a different
regularization FAMILY (not strength, not per-column shape) can hold both — or
whether the displacement is irreducible here, which is the question M4-G5's
pivot branch pointed at.

**Gates.** G0 POWER at the author grain against M4-G5's persisted gap
(.051–.062); G1 triple anchor to <=1e-12; G2 STRENGTH LIVENESS (report the
realized ridge magnitude per alpha and confirm it moves as registered; an
alpha whose realized ridge does not move is INERT and VACUOUS); G3 truth-path
invariance; G4 materiality-form compliance stated per gate.

Tier: EXPLORATORY, label-free, synthetic. Artifacts:
`results/m4_g6_shape_and_strength/`; report
`reports/SUICA_M4_G6_SHAPE_AND_STRENGTH_REPORT.md`.

## M4-G6 outcome (2026-08-03, appended)

Same design as the registration above, executed: eight arms (`baseline`,
`g3_raw_scale` at c=1 only; `column_standardized` at deployed strength plus
`colstd_alpha_<k>` for k in {0.05,0.10,0.20,0.50,1.00}, all at c in
{0.25,1,4}), reusing `g5._forced_route_derivative_columnwise` completely
UNCHANGED for every `column_standardized`-family arm -- the only new
quantity is the scalar `ridge_used(alpha) = alpha * deployed_ridge` passed
into it. A cheap `--stage smoke` pre-flight (one representative context
per world, no full sweep) verified the alpha-ridge arithmetic and the
`colstd_alpha_1.00`/`column_standardized` identity BEFORE the full 8-world
truth sweep launched, and passed cleanly on its first run; the full sweep
then completed on all 8 worlds with zero Tracebacks, RuntimeErrors,
LinAlgErrors, or Killed signals (~40.6 minutes wall-clock, 8 concurrent
against 10 cores, ~1.28x M4-G5's own ~31.75 minutes despite a ~1.43x
larger per-world (arm,c) count, since this leg's single mechanism needs
only one `_hazard_design` build per call, unlike `diagonal_ridge`'s two).

**PIVOT DOES NOT FIRE. Lean (a) HOLDS EXACTLY for all five registered
alphas, without exception** (0.0 paired difference, all 745 authors, every
c-pair, both budgets) -- directly confirming, empirically, the leg's own
pre-registered Part 0.1 argument that the reparameterized penalized
objective is c-independent for ANY fixed scalar ridge, not merely the
deployed one. **Lean (b) HOLDS for three of five alphas** (0.05, 0.10,
0.20 -- all comfortably WITHIN the +/-0.02 margin at both budgets) and
**MISSES for the remaining two** (0.50 AMBIGUOUS/OUTSIDE; 1.00 OUTSIDE
both budgets, reproducing M4-G5's own persisted 0.0515/0.0605 MISS
bit-for-bit, since `colstd_alpha_1.00` is bit-identical to
`column_standardized` by construction -- confirmed to 0.0 by an
assembly-time structural check, 12,288 rows). **Three alphas hold BOTH
leans jointly**, decisively defeating the PIVOT-IF condition. The
headline alpha -- lowest pooled error among the three -- is
`colstd_alpha_0.10` (10% of deployed, near the midpoint of M4-G3's own
measured 4.6-18% band): mean `e_arm_true` 0.5083/0.4946 (4x/8x) against
`g3_raw_scale`'s own persisted 0.5068/0.4949, statistically tied and
numerically ahead at 8x. **Lean (c), the sharpest lean, HOLDS under the
adopted (mean, per-budget) reading**: the error-minimizing alpha is 0.10
at c=0.25, 1.0, AND 4.0, for both budgets separately and pooled -- an
INTERIOR optimum (error rises to both sides), so no ladder-endpoint
question arises under this reading. A disclosed median-based robustness
check names a DIFFERENT best alpha (0.05) -- also perfectly scale-free in
its own right, six-for-six across (c,budget) -- but this reading's own
optimum sits exactly at the ladder's lower endpoint, so per the outer
task's own instruction this is disclosed plainly: any exploration below
alpha=0.05 would need a separately-registered leg, not an extension of
this one. G0 shows the deciding comparisons carry essentially zero (lean
a) or comfortably small (lean b, half-widths 2.8-3.9x smaller than the
+/-0.02 margin) residual uncertainty. G1 anchor (three anchors plus one
bonus internal-consistency check, 45,056 rows total) and G3 truth-path
invariance (160 checks) both pass at exactly 0.0. G2 confirms the alpha
multiplier is genuinely live at all 15 (alpha,c) cells, matching the
registered alpha to 0.0 absolute difference and spanning exactly the
registered 20x ladder ratio.

**Verdict: shape (M4-G5's per-column standardization) and strength (this
leg's weaker-than-deployed alpha) together DELIVER the repair.** The
scale-dependence chased since M4-G2, localized to `hazard_ridge` by M4-G3,
decomposed into shape (solved exactly by M4-G4/M4-G5) and strength
(untouched by M4-G5, since its calibration anchored to the deployed
value) is now closed on BOTH axes at once: a band of alphas (roughly the
lower fifth of the registered ladder) achieves exact c-invariance AND
recovery matching `g3_raw_scale`'s own best level, and the
error-minimizing member of that band is the SAME member at every c
tested, under the reading methodologically consistent with every other
lean in this line. Full artifacts: `scripts/run_suica_m4_g6_shape_and_strength.py`;
`results/m4_g6_shape_and_strength/` (decision.json, gates.json,
error_surface_alpha_x_c_x_budget.csv, argmin_by_c_and_budget.csv,
truth_recovery_rows.csv, author_level_truth_rows.csv, context_meta.csv,
smoke_check.csv, and partials); `reports/SUICA_M4_G6_SHAPE_AND_STRENGTH_REPORT.md`.

## M4-G6 planner adjudication note (2026-08-03, appended) — the repair is delivered

**All three leans HOLD; the pivot does not fire; the verdict is
`SHAPE_AND_STRENGTH_HOLD_AT_SOME_ALPHA`.** This is the first fully
constructive result of the line.

The alpha x c author-grain error surface (n=745, pooled) makes both halves
visible at once:

| alpha | c=0.25 (4x/8x) | c=1.0 (4x/8x) | c=4.0 (4x/8x) |
|---|---|---|---|
| 0.05 | .5123/.4963 | .5123/.4963 | .5123/.4963 |
| **0.10** | **.5083/.4946** | **.5083/.4946** | **.5083/.4946** |
| 0.20 | .5122/.5019 | .5122/.5019 | .5122/.5019 |
| 0.50 | .5314/.5258 | .5314/.5258 | .5314/.5258 |
| 1.00 | .5583/.5554 | .5583/.5554 | .5583/.5554 |

Every row is identical across c — lean (a) holds EXACTLY at all five strengths
(0.0 paired difference, no exceptions), confirming empirically that M4-G5's
reparameterization argument does not depend on strength. Lean (b) holds at
alpha .05/.10/.20 and misses at .50/1.00, the latter reproducing M4-G5's own
miss bit-for-bit. Lean (c) — the sharp one — HOLDS: alpha = .10 minimizes
error at every c, at both budgets, and pooled, and it is an INTERIOR optimum
rather than a ladder endpoint. G2 is exact (realized ridge matches the
registered alpha to 0.0 at all 15 cells), G1 anchors reproduce M4-G5 at
exactly 0.0 over 32,768 rows, G3 is 0.0 over 160 checks.

**Headline: `column_standardized` at alpha = 0.10 x deployed ridge is exactly
c-invariant AND ties `g3_raw_scale`'s recovery (.5083/.4946 vs .5068/.4949,
numerically ahead at 8x) — so the objective can be made scale-free without
paying for it.** Disclosed qualification, stated rather than papered over: a
median-based reading names alpha = .05 instead, which sits at the ladder's
lower endpoint; the ladder was registered as non-extendable, so any test below
.05 requires its own leg.

Process note, also carried into the report: the leg's original monitor was a
`tail -F` pipeline that by construction can never signal completion, which is
why the agent had to be woken. It was killed and not rebuilt. All eight worlds
computed correctly and independently, verified after the fact from each log's
completion marker and partial-file presence.

## M4-G7 registration (2026-08-03, BEFORE run) — take the repair back to the problem that opened the line

**Question.** M4-G6 delivered a repair judged on truth-referenced recovery and
c-invariance. But this line was opened to attack something else: the discovery
objective's systematic FRAME DISPLACEMENT — Leg 14's finding, characterized by
M4-E2 as distributed, world-specific, and not removable by any single term.
Does the certified repair actually reduce THAT?

This is the line's closing question, and it is registered to be able to end in
an honest partial win: scale-invariance and recovery could both be real gains
that are simply ORTHOGONAL to the displacement.

**Design.** Reuse M4-E2 / Leg 14's own worlds, objective path and persisted
anchors — the same ground the displacement was originally measured on.

- `deployed` — the baseline objective as shipped (anchor: must reproduce
  M4-E2's persisted values to <=1e-12).
- `repaired` — `column_standardized` at alpha = 0.10 x deployed ridge, the
  M4-G6 headline (anchor: must reproduce M4-G6's persisted recovery to
  <=1e-12 where the paths coincide).

**Metrics (all three mandatory).**
1. The SCALE-NORMALIZED offset registered in M4-G2 — the raw `offset_norm` is
   disqualified and may not be used as the primary.
2. Leg 14's displacement gap, on its own persisted definition.
3. Truth-referenced recovery, both M4-F5-style variants, to confirm the
   reduction is not bought at recovery's expense.

**Leans.**
(a) DISPLACEMENT FALLS: the repaired objective's scale-normalized offset is
    lower than deployed's, paired-by-world CI excluding zero.
(b) THE ORIGINAL GAP FALLS: Leg 14's displacement gap is lower under the
    repair, paired CI excluding zero.
(c) NOT COSMETIC: truth-referenced recovery does not worsen under either
    variant (equivalence form, margin registered in Part 0).

**PIVOT-IF:** neither (a) nor (b) shows a reduction with a CI excluding zero
-> SCALE-INVARIANCE AND RECOVERY ARE ORTHOGONAL TO THE DISPLACEMENT. The
repair stands as a real and certified improvement to the objective's
conditioning, the displacement is confirmed as a separate still-open defect,
and the line closes with a partial win labeled exactly as such — not as a
solution to the problem it was opened for.

**Gates.** G0 POWER at the registered grain, stated with the target level from
M4-E2's persisted artifacts and the MDE, with the grain justified rather than
inherited (fifth standing rule); G1 dual anchor to <=1e-12; G2 REPAIR LIVENESS
(the repaired arm must differ from deployed in the applied regularization —
report the realized per-column ridge profile beside deployed's scalar); G3
truth-path invariance; G4 materiality-form compliance per gate.

Tier: EXPLORATORY, label-free, synthetic. Artifacts:
`results/m4_g7_repair_vs_displacement/`; report
`reports/SUICA_M4_G7_REPAIR_VS_DISPLACEMENT_REPORT.md`.

## M4-G7 outcome (2026-08-03, appended)

Same design as the registration above, executed: two arms (`deployed`;
`repaired` = `g5._forced_route_derivative_columnwise` with
`treatment="column_standardized"` at `ridge_deployed = 0.10 x
deployed_ridge`, M4-G6's headline, called UNCHANGED) x the 3
`HIGH_GAP_WORLDS` (Leg 14's/M4-E2's own worlds, not the G-line's expanded
8-world `D1_WORLDS`) x 8 repetitions. Part 0 proved, before any compute,
that metrics 1 and 2 (`offset_norm`/its M4-G2 scale-normalized form, Leg
14's `disp_v2`) are pure functions of `context["v2_basis"]` alone --
`_forced_route_derivative_columnwise`'s signature takes a fixed basis and
never returns one, and `context["v2_basis"]` is built once, before either
arm exists as a concept, from a config whose `hazard_ridge` never varies
between arms. All three foreground world passes and the assemble stage
completed with zero Tracebacks or RuntimeErrors, all on the first attempt
except one non-hypothesis-relevant diagnostic (below).

**PIVOT FIRES. Lean (a) MISSES and lean (b) MISSES, both at an EXACT 0.0
paired difference, not a near-miss.** Lean (a) (M4-G2's registered
scale-normalized offset, paired-by-world, n=3 -- the metric's own native
grain): per-world reduction 0.0/0.0/0.0, CI exactly [0.0, 0.0]. Lean (b)
(Leg 14's own `disp_v2`, paired-by-repetition, n=24 -- chosen over the
naive world-grain default per the fifth standing rule, since `disp_v2` is
already a per-rep quantity; world-grain companion, n=3, agrees): reduction
0.0 at all 24 (world, repetition) pairs, CI exactly [0.0, 0.0] at both
grains. **Leg 14's displacement gap closes by exactly 0% of its own
magnitude.** This is not a power failure: G0 shows neither comparison is
underpowered against its own registered bar (12.5% of deployed's own mean
scale-normalized offset for lean (a); Leg 14's own 10% `PIVOT_REDUCTION_BAR`
for lean (b)) -- the realized half-widths are exactly 0.0 because the
underlying per-unit difference is exactly 0.0, a direct, verified
confirmation of Part 0.1's structural argument (`structural_identity_check`
in `decision.json`: `pass_exactly_zero: true`), not sampling luck. **Lean
(c) HOLDS at both budgets**: author-grain (n=384/budget) mean diff
(repaired minus deployed) is -0.000243 (4x) and -0.007886 (8x), both CIs
comfortably inside the registered +/-0.02 margin (upper bounds 0.0156 and
0.0084) -- one-sided WITHIN at both budgets, if anything favoring
`repaired`. G1 anchor (five independent persisted sources: M4-E2's
`offset_table`; Leg 14's `displacement_rows.csv` and `displacement_table`;
M4-G6's persisted `baseline` and `colstd_alpha_0.10` truth rows; M4-G1's own
independent `baseline` rows as a disclosed secondary reading, since M4-E2
itself persists no budget=4x/8x recovery for the `deployed` arm's metric-3
anchor to literally target) passes at 1.78e-15 -- floating-point noise,
comfortably inside 1e-12. G2 REPAIR LIVENESS confirms the repair genuinely
differs from deployed on BOTH axes the outer task asked for: the scalar
ratio is exactly 0.10 (cross-checked against M4-G6's own persisted G2
evidence for `colstd_alpha_0.10`), and the per-column ridge profile --
computed via `g5._standardize_design`, the exact floor-protected mechanism
(`DESIGN_VAR_FLOOR=1e-12`, `DEGENERATE_STD_FALLBACK=1.0`) the real fit uses
internally -- spreads 20.5x-281.8x across 24 sampled contexts against
deployed's exactly-flat 1.0x profile. G3 truth-path invariance passes at
0.0 (6 checks, both arms).

**Verdict: `PIVOT_SCALE_INVARIANCE_AND_RECOVERY_ORTHOGONAL_TO_DISPLACEMENT`.**
Per the registration's own consequence for this branch: M4-G6's certified
repair stands, unmodified, as a real and useful improvement to the
discovery objective's conditioning -- exactly c-invariant, at no cost to
truth-referenced recovery, independently reconfirmed here. But it does not
touch, at all, in any world or repetition, the frame displacement M4-D Leg
14 found and M4-E2 decomposed. The mechanical reason is now proven, not
merely inferred: every one of this line's six legs (M4-G1 through M4-G6)
intervened on the whitening scale or the estimator's ridge penalty, both of
which act strictly downstream of `context["v2_basis"]` -- the object Leg
14's displacement is measured on -- so no repair built entirely within that
downstream space could ever have moved it, regardless of how well-tuned.
**The M4-G line closes here on a partial win, labeled exactly as such**:
the objective's conditioning is repaired and certified; its systematic
frame displacement is confirmed real, unmoved, and handed off as belonging
to the basis-construction path (`_bases_from_whitening`/
`build_m4_discovered_basis`), not the regularization path this entire line
worked in.

**One mechanical problem, found on the first run, fixed before any
hypothesis-relevant number was affected.** The first G2 per-column
ridge-profile pass used raw, unfloored design-column variance; several
near-degenerate columns (e.g. `condition_0`) drove the reported spread
toward float overflow (`~1e+301`, observed). This diagnostic feeds only G2
REPAIR LIVENESS evidence, never a lean or the pivot, so nothing
hypothesis-relevant existed yet. Fixed by calling `g5._standardize_design`
directly (the real fit's own degenerate-column floor); all three worlds
were then re-run in full, and every substantive number -- metrics 1/2/3,
all gates, all leans -- reproduced identically before and after, as
expected since the fix touched only that one diagnostic.

Full numbers, gates, per-world/per-arm tables for all three metrics, and
the complete faithfulness chain: `reports/
SUICA_M4_G7_REPAIR_VS_DISPLACEMENT_REPORT.md`. Artifacts:
`scripts/run_suica_m4_g7_repair_vs_displacement.py`;
`results/m4_g7_repair_vs_displacement/{decision.json, gates.json,
offset_displacement_by_world.csv, displacement_by_rep.csv,
truth_recovery_rows.csv, author_level_truth_rows.csv,
g2_ridge_profile_rows.csv, g3check_rows.csv, context_meta.csv, and
partials}`.

## M4-H1 registration (2026-08-03, BEFORE run) — re-decompose the displacement in valid units

**The line that opened here closes with `docs/SUICA_M4_G_OBJECTIVE_LINE_SYNTHESIS.md`.**
M4-G7 proved the displacement lives in basis construction (`context["v2_basis"]`),
not in the ridge/whitening territory the M4-G line worked in. Before any work
starts there, one debt must be paid.

**Question.** M4-E2 decomposed the displacement into subspaces S1 (supervised
core), S2 (supervision span), S3 (normalization/scale modes) and S4 (residual),
and reported the scale family as the largest identifiable carrier (~1/3
sequential, ~1/2 standalone) with the residual the largest single piece
(.40–.45). It computed all of that on the RAW `offset_norm`, which M4-G2
disqualified as unit-dependent (log-log slope .8796 under a pure change of
units). **Does the attribution survive in valid units?**

**Design.** Re-run M4-E2's decomposition unchanged in every respect — same
worlds, same anchors, same S1–S4 construction, same registered sequential
order, same reverse order, same standalone variants — with ONE substitution:
the target quantity is M4-G2's registered scale-normalized offset instead of
the raw one. Report the raw-metric shares alongside as the disqualified
comparison, so the change (or its absence) is visible rather than asserted.

**Leans.**
(a) THE ATTRIBUTION MOVES: the scale family's share under the normalized
    metric differs from its raw-metric share by more than 10 percentage
    points, in either direction, in the registered sequential order.
(b) THE RESIDUAL SURVIVES: the residual block remains the largest single piece
    under the normalized metric (M4-E2's most consequential finding, tested
    for unit-robustness).
(c) WORLD-SPECIFICITY SURVIVES: the offset direction remains world-specific at
    the permutation null. This is a units-INDEPENDENT property, so it doubles
    as a control on the re-analysis: if it changes, the re-implementation
    differs from M4-E2's in some way not registered here.

**PIVOT-IF:** every subspace share moves by <= 10 points -> M4-E2's
decomposition was units-robust after all. Its picture stands as structural,
the debt is paid, and the basis line proceeds directly from it.

**Gates.** G0 POWER with the grain justified and the target level cited from
M4-E2's persisted artifacts; G1 ANCHOR — the RAW-metric re-run must reproduce
M4-E2's persisted shares to <=1e-12, which is what proves the only change is
the metric; G2 METRIC SUBSTITUTION LIVENESS — show the normalized and raw
targets actually differ per world (they must, by M4-G2); G3 truth-path
invariance where applicable; G4 materiality-form compliance per gate.

Tier: EXPLORATORY, label-free, synthetic. Artifacts:
`results/m4_h1_normalized_decomposition/`; report
`reports/SUICA_M4_H1_NORMALIZED_DECOMPOSITION_REPORT.md`. This leg opens the
**M4-H basis-construction line**; subsequent M4-H registrations continue in
this document until it warrants its own.

## M4-H1 outcome (2026-08-03, appended)

**PIVOT FIRES -- not on a near-miss but on an exact algebraic identity,
proved in Part 0 before compute and confirmed empirically to floating-point
precision. Every subspace share moves by at most 1.67e-14 percentage points
between the raw and the scale-normalized metric (bar: 10 points), across all
3 worlds, all 3 registered orderings (registered/reverse/standalone), and
every within-S3 family split. Verdict:
`PIVOT_UNITS_ROBUST_ATTRIBUTION_STANDS`.** Lean (a) THE ATTRIBUTION MOVES
MISSES (max observed move 1.7e-14 points, nowhere near the 10-point bar).
Lean (b) THE RESIDUAL SURVIVES HOLDS (S4 remains the largest single piece,
registered order, all 3 worlds, unchanged to machine precision: .426948/
.401458/.446432). Lean (c) WORLD-SPECIFICITY SURVIVES holds under this leg's
own Part 0.2 operationalization (offset cosines at-or-below the permutation
null's 95th percentile in all 3 pairs, both metrics, cosine identity vs. raw
1.67e-16).

**Why this is a proof, not a coincidence (Part 0.1).** M4-G2's registered
`scale_normalized_offset(arm) := offset_norm(arm) / GM(s)` is a SCALAR
division of the already-computed scalar offset_norm by a scalar summary of
that arm's own whitening -- it does not touch the whitening, the discovered
basis, or the offset's direction. Applied to the offset MATRIX
(`Delta_normalized := Delta / GM_world`, GM_world = M4-G2's own formula
averaged over the world's 8 reps, the one registered aggregation choice this
leg introduces), every one of M4-E2's decomposition statistics -- sequential/
reverse/standalone shares, within-S3 family shares, width-mismatch share,
dominant share, top-1 singular share, and cross-world Procrustes cosines
(raw values and both disclosed nulls) -- is a ratio of squared or nuclear
norms of LINEAR IMAGES of Delta under FIXED, Delta-independent bases (S1/S2/
S3 are built from Leg 10 arm-B directions, response-target patterns, and the
consensus position `a_center` -- never from Delta itself). Projection onto a
fixed basis is linear, so every such statistic is HOMOGENEOUS OF DEGREE 0 in
any global per-world scalar applied to Delta -- an algebraic identity, not an
empirical finding to be discovered. The two candidate readings of "substitute
the target quantity" this leg disclosed (rescale the decomposed object vs.
treat the substitution as a pure relabeling of the reported scalar) are
consequently forced to the SAME numbers; this is the ambiguity's resolution,
not an evasion of it. Refit-based statistics (M4-E2's task-4 diagnostic,
dominant-component removal) are invariant for a separate, simpler reason
(the removal direction is a component normalized by its own norm, already
unitless) and are not one of this leg's three registered leans, so task 4 is
not re-run -- disclosed, not silently skipped.

**G0 POWER**: the three comparisons are deterministic recomputations on
M4-E2's 3 registered worlds (a census, not a sample) -- WORLD is the grain
because it is the only one at which a world's own decomposition share is
defined (GPA consensus collapses 8 reps into one Delta before any share
exists), matching M4-E2's own non-CI, world-level point-comparison design at
this identical grain. Realized margin: 4.5e14x the registered 10-point bar
(max share identity diff 2.22e-16, machine epsilon) -- not underpowered by
any reading. **G1 ANCHOR** passes on two independent chains: (1) the RAW
re-run reproduces M4-E2's persisted `decision.json` at 84/84 checks (every
registered/reverse/standalone/S3-family share field plus 6 scalar
companions, 3 worlds), offset_norm at 3/3 worlds, and cross-world cosines
against M4-E2's persisted `cosine_rows.csv`, ALL at exactly 0.0 (or
5.55e-17-scale floating-point noise for the cosines) -- proving the metric
substitution is the ONLY thing that changed; (2) GM_world's own 24 per-rep
inputs reproduce M4-G2's persisted `scale_norm_rows.csv` (arm=="baseline")
at exactly 0.0, with Leg 10's own `_debias_gate` (confirms the lambda=0
whitening rebuild reproduces `context["v2_basis"]` exactly) passing at 0.0
across all 24 reps -- proving the scale factors used correspond exactly to
the SAME whitening the offset was built from. **G2 METRIC SUBSTITUTION
LIVENESS** holds decisively: `scale_normalized_offset` differs from
`offset_norm` by 96.4-97.4% (relative) in every world, GM_world running
27.5-38.6 -- the substitution changes the reported magnitude by roughly
two-thirds to three-quarters of an order of magnitude while (per Part 0.1)
being unable to move a single share. **G3** is NOT APPLICABLE, stated
explicitly (no truth-referenced regeneration path in this leg). **G4**
materiality-form compliance stated per gate in the report.

The full registered/reverse/standalone share table under both metrics
reproduces M4-E2's own numbers, including its disclosed order-sensitivity
knife-edge (`selection_creation_compensation`'s registered-order S3 at
.3830, .017 under the .40 pivot-share bar, while reverse-order S3 exceeds
.40 in all 3 worlds at .446/.529/.498) exactly unit for unit under the
normalized metric -- the order-sensitivity is a property of the
decomposition's structure, not of the raw offset's units, and normalizing
was never going to resolve it. The within-S3 family split (n2 = principal
column-scale modes, the whitening's amplification family) reproduces at all
three granularities M4-E2 reported (n2 alone: .3946/.4772/.4569; n2 within
standalone S3: .7398/.7082/.7901; n2 within the registered-order sequential
S3 component: .8227/.8132/.8714), identically between raw and normalized to
<=2.2e-16 at every cell.

**The consequence for the M4-G line's own synthesis, stated precisely, as
that document required**: the debt flagged there -- "M4-E2's decomposition
attributed ~1/3-1/2 of the identifiable carrier mass to the scale family
using the RAW offset, which G2 disqualified... now a units statement of
unknown structural content" -- is paid. M4-G2's units disqualification was
about comparing the MAGNITUDE offset_norm ACROSS DIFFERENT WHITENING
OPERATORS (M4-G1's 8 arms, the pure c-ladder) -- a cross-object comparison.
M4-E2's attribution is a decomposition of ONE FIXED object into subspace
fractions -- a within-object proportion, already unitless by construction.
The two were never the same kind of quantity; this leg is what proves that
formally, rather than merely arguing it. M4-E2's numbers stand exactly as
originally reported: scale family ~1/3 of the mass in the registered order
(~1/2 standalone, n2-dominated), residual .40-.45 the largest single piece,
offset direction world-specific at the permutation null.

No mechanical problems: all three foreground world computations (~35-60s
each, 8 contexts per world) and the assemble step completed cleanly on the
first attempt, zero Tracebacks or RuntimeErrors.

Full numbers, gates, the complete subspace x ordering share table under
both metrics, and the permutation-null evidence:
`reports/SUICA_M4_H1_NORMALIZED_DECOMPOSITION_REPORT.md`. Artifacts:
`scripts/run_suica_m4_h1_normalized_decomposition.py`;
`results/m4_h1_normalized_decomposition/{decision.json, gates.json,
decomposition_rows_both_metrics.csv, subspace_rows_both_metrics.csv,
cosine_rows_both_metrics.csv, cosine_rows_raw.csv, cosine_rows_normalized.csv,
g1_share_anchor_rows.csv, g1_offset_anchor_rows.csv, g1_cosine_anchor_rows.csv,
gm_rows_with_g2_anchor.csv, share_identity_check.csv, lean_a_rows.csv,
pivot_rows.csv, and per-world partials}`.

**Hand-off.** M4-E2's map -- scale family the largest identifiable carrier at
~1/3-1/2 of the mass, residual .40-.45 the largest single piece, offset
direction world-specific, order-sensitive knife-edge at .3830 -- is now
confirmed structural rather than a units artifact, closing the one debt the
M4-G line's synthesis owed the record before the basis-construction line
could build on it. The M4-H basis-construction line (`context["v2_basis"]` /
`_bases_from_whitening` / `build_m4_discovered_basis`, per M4-G7's own
hand-off) proceeds directly from M4-E2's own numbers without needing to
recompute them.

## M4-H2 registration (2026-08-03, BEFORE run) — is the displacement in the basis's own normalization?

**Where the search now stands.** M4-G7 proved the displacement lives in basis
construction (`context["v2_basis"]`), not in the estimator's ridge or the
whitening scale the M4-G line worked in. M4-H1 then confirmed that M4-E2's map
of that displacement is valid as written — its shares are units-invariant by
an identity — so the search can use M4-E2's own numbers, which point at S3
(normalization/scale modes; .2953–.3830 registered, .4459–.5288 standalone)
with the n2 scale family dominating inside it (.74–.79 of standalone S3), and
S4 (residual) as the largest single piece.

**Question.** The M4-G line applied audit-then-intervene to the ESTIMATOR's
regularization and repaired it exactly. Does the same treatment applied one
level up — to the normalization inside BASIS CONSTRUCTION — reduce the
displacement itself?

**Part 0 audit (gated, before any compute).** Enumerate every normalization,
scaling, centering and reference choice inside the construction of
`context["v2_basis"]`, with file and line references, and classify each as a
candidate carrier or not with a stated reason. **This inventory is the leg's
hypothesis space**; steps discovered later may be reported but not scored.
This mirrors M4-G3's inventory discipline, which is what made that leg's
localization decisive.

**Design.** Reuse M4-E2 / Leg 14's worlds and anchors.
- `deployed` — the basis as shipped (anchor: reproduce M4-E2 and Leg 14's
  persisted values to <=1e-12).
- `basisvar_<k>` — one arm per inventoried step, that step alone varied
  (regularized, unnormalized, or alternatively centered as the step's nature
  dictates; the variant form for each step is registered in Part 0).

**Metrics (all three mandatory at every arm).**
1. Leg 14's displacement gap on its own persisted definition — PRIMARY.
2. M4-E2's S1–S4 shares, to test whether a reduction shows up as mass leaving
   the subspace the mechanism predicts rather than as a number moving for
   unexplained reasons.
3. Truth-referenced recovery, both M4-F5 variants — because this program has
   three times measured a target improving while truth worsened (Leg 12,
   M4-F5, M4-G1) and no reduction is accepted here without checking.

**Leans.**
(a) A CARRIER EXISTS: at least one `basisvar_<k>` reduces Leg 14's gap by
    >= 25% relative to deployed, paired-by-world CI excluding zero.
(b) MECHANISTICALLY CONSISTENT: at the winning arm, S3's share falls (or, if
    the winner is not an S3-type step, the share of the subspace its own
    mechanism predicts falls) — a number moving for the registered reason.
(c) NOT COSMETIC: truth-referenced recovery does not worsen under either
    variant (equivalence form, margin registered in Part 0).

**PIVOT-IF:** no arm reduces the gap by >= 25% with a CI excluding zero ->
the displacement is NOT in the basis's normalization either. The remaining
candidate inside basis construction is the CONSENSUS/ALIGNMENT step itself,
and that becomes the line's next registered question.

**Gates.** G0 POWER with the grain justified not inherited, citing Leg 14's
persisted gap level and stating the MDE; G1 ANCHOR to <=1e-12 on both M4-E2
and Leg 14 persisted values; G2 BASIS LIVENESS — every arm must actually
change the basis, reported as a subspace angle or basis distance against
deployed, with a materiality margin registered in Part 0 (an arm that does not
move the basis is INERT and its result VACUOUS); G3 truth-path invariance;
G4 materiality-form compliance stated per gate.

Tier: EXPLORATORY, label-free, synthetic. Artifacts:
`results/m4_h2_basis_normalization/`; report
`reports/SUICA_M4_H2_BASIS_NORMALIZATION_REPORT.md`.
