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
