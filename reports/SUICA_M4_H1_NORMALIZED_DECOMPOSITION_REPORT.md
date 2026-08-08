# SUICA M4-H1 — Re-decomposing the Common Offset in Valid Units

Tier: **EXPLORATORY** (open-exploration phase, operator directive 2026-08-01).
Registered before run: `docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md`, "M4-H1
registration" (2026-08-03); ledger row M4-H1. Script:
`scripts/run_suica_m4_h1_normalized_decomposition.py`. Artifacts:
`results/m4_h1_normalized_decomposition/`. Machinery imported verbatim from
M4-E2 (subspace construction + decomposition), Leg 9/10/11/14 (frames, GPA,
quotient distance, freeze ingredients), M4-G1 (`_build_world_contexts`), and
M4-G2 (`_scale_factors_for_c`, the registered scale-normalized offset
formula).

**Question.** M4-E2 attributed the discovery objective's frame displacement
across S1 (supervised core), S2 (supervision span), S3 (normalization/scale
modes) and S4 (residual) — scale family the largest identifiable carrier
(~1/3 sequential, ~1/2 standalone), residual the largest single piece
(.40–.45) — computed entirely on the raw `offset_norm`, which M4-G2 proved
unit-dependent (log-log slope .8796 under a pure change of the whitening's
units). Does the attribution survive once the raw offset is replaced by
M4-G2's own registered scale-normalized offset?

## Outcome in one paragraph

**PIVOT FIRES — not on a near-miss, but on an exact algebraic identity.**
Every subspace share moves by at most **1.7×10⁻¹⁴ percentage points** between
the raw and the scale-normalized metric (bar: 10 points), across all three
worlds, all three orderings (registered, reverse, standalone), and all
within-S3 family splits — floating-point noise, not a measured effect. Lean
(a) MISSES: the scale family's share does not move (5.6×10⁻¹⁵ to 1.7×10⁻¹⁴
points, nowhere near the 10-point bar). Lean (b) HOLDS: the residual remains
the largest single piece in the registered order, in all three worlds,
unchanged to machine precision. Lean (c) SURVIVES: the cross-world Procrustes
cosines of the offset vectors are bit-identical under both metrics (max diff
1.7×10⁻¹⁶) and remain at-or-below the permutation null's 95th percentile in
all three pairs, exactly reproducing M4-E2's own "world-specific, not one
mechanism" finding. **This is not a coincidence the run happened to land on —
it is proved in Part 0 of the script, before any compute, from the fact that
M4-G2's scale-normalized offset is a per-world SCALAR division of the
already-computed offset object, and every one of M4-E2's decomposition
statistics is a ratio of squared norms of that SAME object under FIXED,
Delta-independent bases, hence homogeneous of degree 0 in that scalar.**
**Verdict: `PIVOT_UNITS_ROBUST_ATTRIBUTION_STANDS`.** M4-E2's picture stands
as structural. The debt the M4-G line's synthesis flagged is paid, and the
M4-H basis-construction line proceeds directly from M4-E2's own numbers —
the `.40–.45` residual and the `~1/3–1/2` scale-family carrier share do not
need to be recomputed for the basis work ahead.

## G0 — POWER

This leg's three adjudicated comparisons are **deterministic recomputations
on M4-E2's own 3 registered worlds** — a census, not a sample. WORLD is the
grain because it is the *only* one at which "a world's own decomposition
share" is even defined: the GPA consensus already collapses each world's 8
repetitions into one Delta before any share exists, so there is no available
resampling unit finer than the world itself (unlike the author-level
truth-recovery statistics the rest of the M4-G line uses). This matches
M4-E2's own design exactly — its own lean (a)/(b)/(c)/pivot were themselves
plain, unhedged point comparisons at n=3, never CI-based — so inheriting the
world grain here is forced by the target's own definition, not a passive
default (the fifth standing rule's concern).

Target level, cited from M4-E2's persisted `decision.json`:

| quantity | M4-E2 persisted range |
|---|---|
| S3 (scale family) registered-order share | .2953 – .3830 |
| S4 (residual) registered-order share | .4015 – .4464 |
| offset cosines (world pairs) | .4159 – .4523 |
| permutation-null q95 | .4666 – .4752 |

The applicable "power" question is numerical, not statistical: can this
design resolve a difference far below the registered 10-percentage-point
(0.10) bar? Part 0.1's proof guarantees yes, to floating-point precision.
**Realized:** max share identity diff **2.22×10⁻¹⁶** (machine epsilon), max
cosine identity diff **1.67×10⁻¹⁶** — a margin of **4.5×10¹⁴×** the 10-point
bar. Not underpowered by any reading; the opposite — the design resolves
effects fifteen orders of magnitude smaller than the bar requires.

## G1 — ANCHOR

Two independent anchor chains, both required by the registration.

**(1) The RAW re-run reproduces M4-E2's persisted numbers.** Every
registered-order, reverse-order, standalone, within-S3-family, and scalar
companion field (`width_mismatch_share`, `width_mismatch_baseline`,
`rank_b_aligned`, `dominant_share`, `delta_singular_top1_share`,
`dominant_subspace` identity) compared against
`results/m4_e2_offset_anatomy/decision.json`: 66 share-field checks (3 worlds
× 22 subspace/family entries across the 6 order variants) + 18 scalar
companion checks (3 worlds × 6 scalars) = **84 checks total
(`g1_share_anchor_rows.csv`), max abs diff = 0.0** (exact).

`offset_norm` itself: 3/3 worlds exact 0.0 against M4-E2's persisted
13.754107 / 11.956016 / 13.288138. The cross-world Procrustes cosines (raw)
against M4-E2's persisted `cosine_rows.csv`: max abs diff **5.55×10⁻¹⁷**
(3 pairs × 2 fields). The upstream rebuild chain (Leg-14-style offset/GPA-
objective anchor, Leg-11 displacement anchor, Leg-10 arm-B gate, Leg-10
`_debias_gate`, the unit check) all pass at exactly 0.0 except the routine
`unit_check_max` (1.67×10⁻¹⁵, the same floating-point-scale value M4-E2 itself
reports). **This is what proves the metric substitution is the ONLY thing
that changed** — every piece of machinery upstream of it reproduces M4-E2
bit-for-bit.

**(2) GM_world's own per-repetition inputs reproduce M4-G2's persisted
numbers.** 24 rows (3 worlds × 8 reps) of `_scale_factors_for_c(ingredients,
1.0)`'s geometric mean, joined against M4-G2's persisted
`scale_norm_rows.csv` (arm=="baseline"): max abs diff **0.0** (exact),
tolerance 1e-9. Each rep's `leg10._debias_gate` (confirms the lambda=0
whitening rebuild reproduces `context["v2_basis"]` exactly, so the scale
factors used correspond to the SAME whitening the basis — and hence Delta —
was built from) also passes at exactly 0.0 across all 24 reps.

**G1 = PASS** on both chains.

## G2 — METRIC SUBSTITUTION LIVENESS

`scale_normalized_offset` differs from `offset_norm` by 96.4% – 97.4%
(relative) in every world — `GM_world` runs 27.5–38.6, nowhere near 1.0:

| world | offset_norm (raw) | GM_world | scale_normalized_offset |
|---|---|---|---|
| endogenous_creation_expansion | 13.754107 | 27.461514 | 0.500850 |
| selection_creation_compensation | 11.956016 | 31.862204 | 0.375241 |
| source_rotated_feedback | 13.288138 | 38.557064 | 0.344636 |

**G2 = LIVE.** The substitution changes the reported magnitude by roughly
two-thirds to three-quarters of an order of magnitude — this is not a
substitution that "changes nothing." What it does not change, and is proved
in Part 0 not to be able to change, is the decomposition's internal
proportions (see below).

## G3 — TRUTH-PATH INVARIANCE

**NOT APPLICABLE**, stated explicitly per the registration's own "where
applicable" hedge. This leg constructs no truth-referenced regeneration path
(no budget/events regeneration, no `D_true` comparison at any budget) — its
adjudicated quantities are pure functions of the already-validated offset
object Delta, which G1 ANCHOR re-verifies against M4-E2's own chain.

## G4 — MATERIALITY FORM

| gate | form |
|---|---|
| G0 | numerical-precision margin statement (deterministic recomputation, no sampling distribution to bound) |
| G1 | equivalence/margin bound: <=1e-12 (shares/offset/cosines), <=1e-9 (GM_world) |
| G2 | liveness ("must differ") form — same polarity as M4-G1/M4-G4/M4-G5's own G2 gates |
| G3 | not applicable, stated explicitly |
| lean (a) / pivot | point-difference against a registered 10-percentage-point margin (M4-E2's own leans used the identical unhedged point-comparison form at this grain) |
| lean (b) | categorical (largest-piece identity), matching M4-E2's own registered-order finding |
| lean (c) | at-or-below-null-q95 form, this leg's own Part 0.2 registered operationalization |

All gates comply.

## Why the shares provably cannot move (Part 0.1, stated before compute)

M4-G2's registered definition is a **scalar** operation:
`scale_normalized_offset(arm) := offset_norm(arm) / GM(s)`. It does not touch
the whitening, the discovered basis, or the offset object's *direction* — it
divides the already-computed scalar `offset_norm` by a scalar. Applied to the
matrix object Delta (`Delta_normalized := Delta / GM_world`), every one of
M4-E2's decomposition statistics is a ratio of squared (or nuclear) norms of
**linear images of Delta under bases that do not depend on Delta itself** —
S1 is built from Leg 10 arm-B response-supervised patterns, S2 from
author-mean response patterns, S3 from per-role constant patterns and the
*consensus position* `a_center` (the v2 GPA mean, a separate object from
`Delta = a_center - b_aligned`). Projection onto a fixed basis is linear, so
`Delta -> Delta/k` sends every component to `component/k`, and every share
(`= ||component||² / ||Delta||²`) is **homogeneous of degree 0 in k** —
algebraically exact, not approximately close:

```
share(Delta/k) = (1/k²)||proj(Delta)||² / (1/k²)||Delta||² = share(Delta)
```

Procrustes cosine is bilinear-homogeneous-degree-0 in each argument
independently, so this holds even though the two worlds in a pair carry
*different* `GM_world` values. Permutation commutes with scalar
multiplication, so the permutation-null draws are equally invariant, and the
matched-shape random null never touches Delta at all. **Reading A** (divide
Delta by `GM_world`, the substantive reading adopted here) and **Reading B**
(treat the substitution as a pure relabeling of the reported scalar, leaving
the already-unitless decomposition untouched) are consequently forced to the
identical numbers — this is the disclosed ambiguity's resolution: both
readings converge, and that convergence is proved before compute, then
confirmed empirically below to 2.22×10⁻¹⁶.

**The important, non-obvious point this settles**: M4-G2's units
disqualification was about comparing the *magnitude* `offset_norm` **across
different whitening operators** (M4-G1's 8 arms, or the pure c-ladder) — a
cross-object comparison. M4-E2's attribution is a decomposition of *one fixed
object* into subspace fractions — a within-object proportion, already
unitless by construction. The two were never the same kind of quantity, and
this leg is what proves that formally rather than assuming it.

## Full subspace × ordering share table, both metrics

All three worlds, all three registered orderings, raw vs. scale-normalized
(`abs_diff` in share units — read `1e-16` as floating-point noise):

**Registered order (S1 → S2 → S3 → residual)**

| world | subspace | raw | normalized | abs diff |
|---|---|---|---|---|
| endogenous_creation_expansion | S1 | .228537 | .228537 | 0.0 |
| endogenous_creation_expansion | S2 | .012225 | .012225 | 0.0 |
| endogenous_creation_expansion | S3 | .332289 | .332289 | 1.1e-16 |
| endogenous_creation_expansion | S4 residual | .426948 | .426948 | 0.0 |
| selection_creation_compensation | S1 | .200233 | .200233 | 0.0 |
| selection_creation_compensation | S2 | .015355 | .015355 | 0.0 |
| selection_creation_compensation | S3 | .382954 | .382954 | 0.0 |
| selection_creation_compensation | S4 residual | .401458 | .401458 | 0.0 |
| source_rotated_feedback | S1 | .231916 | .231916 | 8.3e-17 |
| source_rotated_feedback | S2 | .026362 | .026362 | 0.0 |
| source_rotated_feedback | S3 | .295291 | .295291 | 1.1e-16 |
| source_rotated_feedback | S4 residual | .446432 | .446432 | 0.0 |

**Reverse order (S3 → S2 → S1 → residual)** — reproduces M4-E2's own
disclosed order-sensitivity numbers exactly under BOTH metrics:

| world | S3 rev. | S2 rev. | S1 rev. | resid. rev. |
|---|---|---|---|---|
| endogenous_creation_expansion | .445902 | .026082 | .163151 | .364865 |
| selection_creation_compensation | .528776 | .011154 | .123180 | .336889 |
| source_rotated_feedback | .498372 | .011864 | .122549 | .367215 |

(raw and normalized identical to <=2.2e-16 at every cell, both orderings and
standalone — full row-level table: `decomposition_rows_both_metrics.csv`,
144 rows = 3 worlds × 2 metrics × 6 order/family variants × subspaces)

M4-E2's own disclosed knife-edge — registered-order S3 at .3830 in
`selection_creation_compensation` (.017 under the .40 pivot-share bar) while
reverse-order S3 exceeds .40 in all three worlds (.446/.529/.498) — is
**exactly reproduced, unit for unit, under the normalized metric**. The
order-sensitivity is a property of the decomposition's structure, not of the
raw offset's units; normalizing does not resolve it and was never going to,
per Part 0.1.

**Within-S3 family split (n2 = principal column-scale modes, the whitening's
amplification family) also reproduces exactly, at all three granularities
M4-E2 reported, under BOTH metrics:**

| world | n2 alone (share of whole Delta) | n2 within standalone-S3 | n2 within registered-order S3 component |
|---|---|---|---|
| endogenous_creation_expansion | .394558 | .739828 | .822711 |
| selection_creation_compensation | .477190 | .708197 | .813193 |
| source_rotated_feedback | .456860 | .790146 | .871374 |

(first column = `standalone_family_of_delta`/`n2_column_scale`, exactly
M4-E2's own report table's "n2 alone" column .3946/.4772/.4569; second =
`within_S3_standalone_component`, M4-E2's "n2 share of standalone-S3
component" .7398/.7082/.7901; third = `within_S3_component`, n2's share of
the registered-order *sequential* S3 component — all three identical between
raw and normalized to <=2.2e-16, full rows in
`decomposition_rows_both_metrics.csv`), matching M4-E2's own reported
n2-dominance of the scale family exactly.

## Cross-world direction stability (world-specificity), both metrics

| pair | cosine (raw = normalized) | perm-null median | perm-null q95 | at/below q95 |
|---|---|---|---|---|
| expansion / compensation | .417911 | .431639 | .466580 | YES |
| expansion / rotated | .452276 | .433401 | .475216 | YES |
| compensation / rotated | .415898 | .429753 | .468715 | YES |

Max abs diff between raw-metric and normalized-metric cosines across all 3
pairs (cosine value, perm-null median, perm-null q95 — 9 comparisons):
**1.67×10⁻¹⁶.** Exactly M4-E2's own finding, reproduced unit for unit: the
offset directions sit at or below the permutation null in every pair, under
both metrics — the offset is world-specific, not one shared mechanism, and
this property is (as the registration itself predicted) units-independent by
construction, so its exact reproduction here doubles as a re-implementation
control: nothing in this leg's rebuild diverges from M4-E2's own machinery.

## Lean-by-lean adjudication

| lean | statement | result |
|---|---|---|
| (a) THE ATTRIBUTION MOVES | S3 registered-order share differs >10 points, raw vs. normalized, any world | **MISS** — max observed 1.7e-14 points (endogenous_creation_expansion 5.6e-15, selection_creation_compensation 5.6e-15, source_rotated_feedback 1.7e-14) |
| (b) THE RESIDUAL SURVIVES | S4 remains the largest single piece, registered order, normalized metric, all 3 worlds | **HOLD** — S4 largest in 3/3 worlds under the normalized metric (.426948/.401458/.446432, identical to raw), reproducing M4-E2's own most consequential finding |
| (c) WORLD-SPECIFICITY SURVIVES | offset cosines at/below permutation-null q95, all 3 pairs, normalized metric | **SURVIVES** — 3/3 pairs at or below q95, cosine identity vs. raw = 1.7e-16 |

## PIVOT

**FIRES.** Registered rule: every subspace share moves by <=10 points, every
world, registered order. Realized: max move across all 12 (world × subspace)
cells = **1.67×10⁻¹⁴ percentage points** — 15 orders of magnitude inside the
bar (full table: `pivot_rows.csv`). Per the registration's own consequence:
**M4-E2's decomposition was units-robust after all. Its picture stands as
structural, the debt is paid, and the basis line proceeds directly from
it.**

## Faithfulness chain

| check | value |
|---|---|
| Raw shares vs. M4-E2 persisted (84 checks: registered/reverse/standalone/S3-family × 3 worlds + scalar companions) | max abs diff 0.0 |
| Raw offset_norm vs. M4-E2 persisted (3 worlds) | max abs diff 0.0 |
| Raw cosines vs. M4-E2 persisted `cosine_rows.csv` (3 pairs × 2 fields) | max abs diff 5.6e-17 |
| Upstream Leg-14 offset/GPA-objective anchor | 0.0 |
| Upstream Leg-11 displacement anchor | 0.0 |
| Upstream Leg-10 arm-B gate | 0.0 |
| Upstream Leg-10 `_debias_gate` (24 reps) | 0.0 |
| Unit check (analytic D_true) | 1.67e-15 |
| GM_world per-rep inputs vs. M4-G2 persisted `scale_norm_rows.csv` (24 rows) | 0.0 |
| Normalized vs. raw share identity (this leg's own proof-confirmation, all worlds/orders/families) | 2.22e-16 |
| Normalized vs. raw cosine identity (this leg's own proof-confirmation) | 1.67e-16 |

No Tracebacks, RuntimeErrors, or refusals on any of the three foreground
world computations or the assemble step. No mechanical problems encountered.

## Boundaries

Finite synthetic M4-C.2 worlds only (M4-E2's own 3 `HIGH_GAP_WORLDS`); no
truth-referenced diagnostic in this leg (see G3); M4-E2's own task-4
diagnostic refit (dominant-component removal / gap closure) is **not
re-run** here — it is not one of this leg's three registered leans, and Part
0.1's argument shows it would reproduce M4-E2 bit-for-bit for a different,
simpler reason (the removal direction is already unitless, being a component
normalized by its own norm) — disclosed, not silently skipped. No
natural-text, personality, or clinical claim; no seal, no independent
verification (operator directive 2026-08-01).

## Hand-off

M4-E2's own numbers — scale family ~1/3 of the mass in the registered order
(~1/2 standalone), residual .40–.45 the largest single piece, offset
direction world-specific, order-sensitive knife-edge at .3830/.017-under-bar
— are now confirmed to be a **structural** statement, not an artifact of
having been computed in the raw operator's own units. The M4-H
basis-construction line (`context["v2_basis"]` / `_bases_from_whitening` /
`build_m4_discovered_basis`, per M4-G7's own hand-off) can build on M4-E2's
map without first redrawing it — the only correction the record owed is now
recorded: the map was never wrong, and now it is proved, not merely assumed,
to have been valid in the units that matter for a share-based attribution.
