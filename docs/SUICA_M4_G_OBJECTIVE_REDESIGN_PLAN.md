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
