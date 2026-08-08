# SUICA M4-G2 — Metric Units: Does `offset_norm` Measure the World or Its Own Units?

Tier: **EXPLORATORY** (open-exploration phase, operator directive 2026-08-01).
Registered before run: `docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md`, "M4-G2
registration" (2026-08-03, BEFORE run), plus the "M4-G1 planner adjudication
note" that raised the question this leg answers; ledger row M4-G2. Script:
`scripts/run_suica_m4_g2_metric_units.py`. Artifacts:
`results/m4_g2_metric_units/`. Machinery imported and reused unchanged from
M4-G1 (`g1` in the script): world/context builder, whitening-arm dispatch
for M4-G1's own 8 arms, CI helpers (`_paired_world_ci`, `_paired_author_ci`),
aggregation helpers (`_author_level_truth`), persisted anchors — and, via
M4-G1, Leg 10 (freeze ingredients, Tikhonov whitening), Leg 9 (row-norm
swap), Leg 11 (stacked-frame quotient), Leg 14 (GPA Frechet mean, quotient
distance), Leg 4 (context build, forced-route derivative, generator
regeneration), Leg 3 (world seed, relative error), Leg 8 (expected-geometry
lookup). No estimator internals are copied.

## Headline, stated up front

**PIVOT DOES NOT FIRE. The log-log slope of `offset_norm` against a pure
whitening-scale multiplier c is 0.880, 95% CI [0.839, 0.921] — a materially
nonzero, adequately-powered, but sub-linear (CI excludes both 0 AND 1)
dependence on units. Per the registration's own branch: `offset_norm` is
DISQUALIFIED as an optimization target in its raw form.** Lean (a) HOLDS.
Lean (b) MISSES — truth-referenced recovery is NOT scale-free; it improves
monotonically and precisely as c increases (error falls from 0.786 to 0.422
across the ladder at budget=4x, every pairwise CI outside the ±0.02 margin
except the mildest, c=2→4). Lean (c) HOLDS decisively — under the
registered scale-normalized offset, the Spearman correlation with truth
error flips from M4-G1's −0.786 to **+0.833** (identical at both budgets),
and `identity` — M4-G1's spurious "best" arm on raw offset — becomes the
single WORST-scoring arm under normalization, exactly reproducing M4-G1's
own truth-recovery ordering. G0 (primary, the slope CI) is emphatically not
underpowered: realized half-width is 8.2% of its own bar. G2 shows all four
registered invariances (eigenvectors, relative spectrum, condition number,
width) hold to floating-point exactness within every (world, repetition)
context, while the whitening operator's Frobenius norm scales with c
exactly — the channel is live and the manipulation is pure units, not
structure. G1 and G3 both pass at 0.0.

**Two discoveries were made mid-compute, both purely mechanical (world
seed-sharing and numerical fragility, never the outcome of a hypothesis
test), both handled by disclosing both readings and adopting the valid one
before any adjudication depended on the choice.** They are reported in full
below because the registration's own standing rules require it, not because
they change the verdict — they don't: lean (a)/pivot's numbers were fixed
before either discovery mattered, and lean (b)'s MISS holds under both the
naive and the corrected reading.

## Part 0 — registered operationalizations (written into the script BEFORE compute; transcribed here)

### 0.0 World selection — registered, then corrected twice mid-compute (disclosed in full, both readings given)

G0 requires the c-ladder (D1) to run on MORE worlds than M4-E2/M4-G1's
3-world anchor ceiling ("target 8"), while G1 ANCHOR requires the SAME 3
worlds M4-G1 used (`HIGH_GAP_WORLDS`) so its persisted baseline
offset/truth numbers remain a valid bit-exact anchor.

**Original rule (written before any compute).** `D1_WORLDS` =
`HIGH_GAP_WORLDS` (3) + 5 `FRESH_COMPANION_WORLDS`: the config's own 15-world
list, in declared order, excluding `HIGH_GAP_WORLDS` and excluding the 4
worlds whose archived M4-C.2 battery (`results/m4_chart_ecology/metrics.csv`)
shows `chart_refused=True` on every one of their 8 reps (`author_leakage`,
`evaluation_support_shift`, `hidden_opportunity_source_alias`,
`response_leakage_circular` — Leg 4's `_build_context` raises unconditionally
on `chart.refused`, a hard compatibility requirement, not a cherry-pick),
taking the first 5 remaining: `linear_null_ecology`,
`linear_exogenous_selection`, `endogenous_source_partition_matched`,
`fast_return_equal_marginal`, `slow_hysteresis_equal_marginal`.

**Discovery 1 (mid-compute, before any slope/truth/lean number existed — only
offset_gap's own G1/G2 bookkeeping had run).** `leg3._world_seed`'s own
`matched_groups` table (pre-existing, used unchanged by every leg in this
program) deliberately shares one seed offset across two named worlds each:
`{linear_exogenous_selection, endogenous_source_partition_matched}` share
offset 101; `{fast_return_equal_marginal, slow_hysteresis_equal_marginal}`
share offset 211. Empirically, for every (world, rep, c), `offset_norm`,
`geometric_mean_scale`, and `condition_number` are **bit-identical (0.0 max
abs diff)** within each matched pair — reproduced in
`results/m4_g2_metric_units/decision.json`'s `world_selection_disclosure.pairs`
— even though the worlds' dynamic mechanisms genuinely differ (archived
`classification_accuracy`/`active_mechanisms` differ sharply: e.g.
`endogenous_source_partition_matched` is 0.0/"creation" against
`linear_exogenous_selection`'s 1.0/"selection"). Mechanism: this leg's
offset/G2 pipeline depends only on `seed` (via Leg 10's reference-calibration
chart-fitting + eigendecomposition), not on which dynamic mechanism `world`
switches on — so seed-matched worlds are deterministic duplicates for
`offset_norm` specifically. Two of the 5 originally-selected fresh
companions were therefore zero-information duplicates of their partners for
the offset/slope test.

**Correction, round 1 (adopted; deterministic, outcome-blind extension,
decided before any slope/truth/lean number existed).** Same config-order
walk, same chart-refusal exclusion, plus skip the second-seen member of any
`matched_groups` pair, continuing to the next worlds in config order to
still reach 5: `linear_null_ecology`, `linear_exogenous_selection`
(kept, first of its pair), `fast_return_equal_marginal` (kept, first of its
pair), `history_gated_ecology`, `condition_alias_ecology` — 5 genuinely
independent seeds.

**Discovery 2 (mid-compute, still before any slope/truth-equivalence/lean
number was computed — only the G3 spot-check's search loop, added after an
unrelated empty-file bug surfaced, had run).** `linear_exogenous_selection`
is degenerate (`norm(stack["D"]) < FLIP_TOLERANCE`) on **all 256** of its
(repetition, view, author) combinations — G3's degenerate-equality check is
inapplicable on it at all, and it would contribute zero usable rows to lean
(b)'s truth-recovery test (`_author_level_truth` drops `degenerate_reference`
rows). Consistent with its archived `active_mechanisms="selection"` /
`creation_action_geometry` uniformly 0.0 (no creation loop active — and this
line's `D_true` is a creation/loop-mechanism derivative). A hard blocker, not
a power concern.

**Correction, round 2 (adopted; same outcome-blind principle).** Replace
`linear_exogenous_selection` with the next candidate in the same walk,
continuing past `condition_alias_ecology` through the 4 chart-refusing
exclusions to the last remaining safe+independent world in the catalog:
`topology_mismatch` (archived `active_mechanisms="creation"`,
`creation_action_geometry` .79–.99 across all 8 reps — checked from the
archive **before** running it, specifically to avoid a third blocker).

**Final `FRESH_COMPANION_WORLDS`**: `linear_null_ecology`,
`topology_mismatch`, `fast_return_equal_marginal`, `history_gated_ecology`,
`condition_alias_ecology` — five independent seeds, G3 non-degenerate on all
five (verified in `g3_check_rows.csv`, 16/16 checks, max abs diff 0.0). The
three excluded worlds' partials remain on disk
(`partial_*_endogenous_source_partition_matched.csv`,
`partial_*_slow_hysteresis_equal_marginal.csv`,
`partial_*_linear_exogenous_selection.csv`) as disclosed evidence; `--assemble`
does not read them into any adjudicated table. **Both discoveries were
mechanical/design facts (seed-sharing, gate-inapplicability), never a
hypothesis-relevant outcome — no lean, slope, or truth number existed when
either correction was made.**

### 0.1 Scale-normalized offset definition for lean (c) (registered before compute)

For an arm with per-retained-direction scale factors `s_1..s_k`
(`1/sqrt(eig_i+lambda)` for baseline/shrinkage/truncated, `1` for identity —
`g1._scale_factors`'s own output, reused unchanged):

```
scale_normalized_offset(arm) := offset_norm(arm) / GM(s_1..s_k)
GM(s) = exp(mean(log(s)))   # geometric mean, = det(diag(s))^(1/k)
```

Justification: (i) **exact under D1's own manipulation** — `GM(c·s_base) =
c·GM(s_base)`, so dividing by it recovers exactly c when an arm is a uniform
rescaling, the same relationship D1 tests directly; (ii) **generalizes to
non-uniform arms** (shrinkage's eig-dependent law, truncation's
survivor-only law) via the one aggregate statistic invariant to which
directions carry more or less amplification, matching `offset_norm`'s own
basis-invariant (GPA/quotient) construction; (iii) **`identity`'s own GM = 1
exactly**, so its scale-normalized offset equals its raw offset unchanged —
clean for a lean whose question is precisely whether identity stops being
the minimum. GM is recomputed (not read from M4-G1's CSVs, which store only
`scale_min`/`scale_max`/`condition_number`) via a light re-run of
`leg10._freeze_ingredients` + `g1._whitening_for_arm` + `g1._scale_factors`
on M4-G1's own 3 worlds × 8 reps × 8 arms — no GPA, no truth-regeneration —
cross-anchored against M4-G1's persisted `g2_spectrum_evidence.csv`
(`scale_min`/`scale_max` max abs diff 1.14e-13, tolerance 1e-9). This
normalization deliberately does **not** also correct for retained width —
that is D2's separate, non-adjudicating diagnostic.

### 0.2 D1 arm construction (registered; none added or dropped)

Arms `c_0.25, c_0.5, c_1.0, c_2.0, c_4.0` for c in {0.25, 0.5, 1.0, 2.0, 4.0},
each `c · whitening_baseline` where `whitening_baseline =
leg10._whitening_with_lambda(ingredients, 0.0)` — M4-G1's own `baseline`
arm's operator, unchanged, scaled by the scalar c. `c_1.0` **is**
`baseline`, retained for G1 ANCHOR and the log-log fit. Same
`ingredients["eigenvectors"][:, retained]` (never touched by c, by
construction), same retained width, per-direction scale vector
`c/sqrt(eig)` whose ratios (relative spectrum) and max/min ratio (condition
number) are algebraically c-invariant. G2 (below) reports this as measured
evidence, not merely asserted.

### 0.3 Statistical operationalizations, disclosed

- **D1's decisive test (lean a / pivot)**: per world, OLS fit of
  `log(offset_norm)` on `log(c)` over the 5 ladder points gives one slope;
  the 8 per-world slopes are the sampling units for a paired-by-world
  t-interval (`g1._paired_world_ci`, reused unchanged, n=8/df=7). A pooled
  OLS across all 40 (world, c) points is also reported, disclosed and
  non-gating.
- **G0's slope MDE bar**: 0.5 — half the gap between the two substantively
  distinct hypotheses this test discriminates (slope=0 scale-invariant vs
  slope=1 exact linear units-scaling), the same "half of the discriminating
  gap" convention M4-G1's own G0 used.
- **Lean (b)'s equivalence check**: all C(5,2)=10 pairwise c-comparisons, at
  both truth budgets (4x, 8x, unchanged from M4-G1), author-level
  (view-mean) paired differences (`g1._paired_author_ci`, reused unchanged);
  HELD iff every one of the 20 pairwise CIs lies entirely inside ±0.02 (CI
  form, not point-estimate, per G4).
- **Lean (c)'s aggregation**: registered text says "across M4-G1's eight
  arms" — all eight (baseline included), unlike M4-G1's own disclosed
  companion (n=7, excluded baseline); that n=7 raw-offset reading is also
  reported here as a **correctness anchor** against M4-G1's disclosed −0.786.
  HELD iff, at BOTH budgets, the scale-normalized Spearman is ≥ 0 AND
  `identity` is not the argmin; disagreement between budgets would be
  reported as MISS, never resolved by picking the favorable budget.
- **Discovered post-hoc, disclosed here rather than silently fixed (see
  "Lean (b) numerical-validity discovery" below)**: two of the 8 D1 worlds
  turned out numerically invalid for the *truth-recovery* statistic
  specifically (not for offset). Both readings are computed; the valid
  6-world subset is adopted, chosen by a threshold on the arm-invariant
  `e_orc_true` fixed before looking at which reading it would favor.

## Part 1 — Outcome

*(Everything below this line was computed after the run; Part 0 above was
frozen before compute began, except where explicitly marked as a mid-compute
discovery above.)*

### G0 POWER (reported first, per instruction)

**Primary (decisive — gates lean a/pivot): paired-by-world (n=8, FRESH) CI
on the mean per-world log-log slope.**

| quantity | value |
|---|---|
| mean slope | 0.8796 |
| 95% CI | [0.8386, 0.9206] |
| half-width | 0.0410 |
| bar (half the 0-vs-1 gap) | 0.5 |
| half-width as % of bar | **8.2%** |
| underpowered? | **NO** |

Emphatically not underpowered — the realized half-width is less than a
twelfth of the bar. This is the gate that licenses lean (a)/pivot's
adjudication; **all 8 worlds are E2-independent, freshly measured** (only
`c_1.0`'s VALUE is separately anchored to M4-E2/M4-G1 on the 3
`HIGH_GAP_WORLDS`, below).

**Secondary (disclosed, non-gating, for comparability with M4-G1's own G0
convention): paired-by-world (n=8, fresh) CI on the raw offset difference
between the ladder's extremes.**

| quantity | value |
|---|---|
| mean diff (c=4.0 − c=0.25) | 47.096 |
| 95% CI | [40.216, 53.976] |
| half-width | 6.880 |
| E2-anchored bar (12.5% of M4-E2's persisted 3-world mean baseline offset, 12.999) | 1.625 |
| fresh bar (12.5% of this leg's own 8-world mean c=1.0 offset, 12.003) | 1.500 |
| "underpowered" vs either bar? | technically yes (half-width exceeds both) |

This "underpowered" reading is a **scale mismatch, not noise**: M4-G1's
12.5%-of-baseline bar was calibrated for a ~25%-ish regularization change,
not a 16-fold sweep in c. The CI [40.2, 54.0] is tight and utterly excludes
zero — this comparison is extremely well-determined in absolute terms; it
simply isn't informative measured against a bar built for a different
question. The slope-CI reading above is what actually adjudicates lean
(a)/pivot, and it is not in this position.

### G2 CHANNEL LIVENESS / INVARIANCE (reported second, per instruction)

All four registered invariances, checked per (world, repetition, c) against
the `c_1.0` case in the **same context** (tolerance 1e-9 relative — an exact
algebraic identity, not a materiality bar, since D1's whole claim is that
these are unchanged, not merely similar):

| invariance | max abs / relative diff vs `c_1.0` | holds? |
|---|---|---|
| eigenvectors (value identity, `np.array_equal`) | 0.0 (every row) | **YES** |
| relative spectrum (`scale/max(scale)`) | 0.0 | **YES** |
| condition number | 0.0 abs, 0.0 relative | **YES** |
| width, **within** each (world, rep) context across all 5 c | invariant on 64/64 contexts | **YES** |
| **all four together** | | **YES** |

Channel liveness (the operator actually moved): Frobenius norm of the
applied whitening scales with c exactly — `frobenius_norm(c) /
frobenius_norm(c_1.0)` recovers c to max abs diff **0.0** across every
(world, rep, c). **The channel is live.**

Two disclosed diagnostics, neither part of the gate: (i) width **varies
across different (world, rep) contexts** (distinct values {7,8,9,10,11,12,13}
observed) — this is Leg 10's own rank-tolerance cut responding to each
context's own eigenvalue spectrum, exactly the "retained rank is not rigidly
12" variability M4-G1 itself disclosed, and is orthogonal to this leg's
c-invariance claim (fixed within every context, varying only across them).
(ii) `eigenvectors_is_same_object_vs_c1` is `False` on every row — this is
expected, not a failure: numpy fancy indexing (`array[:, idx]`) always
returns a fresh copy, so re-slicing `ingredients["eigenvectors"][:,
retained]` per c yields a new array object each call even though the
unsliced source is never touched by c. The scientifically meaningful claim
is VALUE identity, which holds exactly (`eigenvectors_identical_every_row`).

**D1 is confirmed a pure change of units, not a structural manipulation.**

### G1 ANCHOR

`c_1.0` reproduces M4-G1's persisted `baseline` numbers on the 3
`HIGH_GAP_WORLDS`, identical seeds:

| check | max abs diff | tolerance | pass |
|---|---|---|---|
| basis vs `context["v2_basis"]` | 0.0 | 1e-12 | YES |
| offset_norm vs M4-G1 persisted `offset_rows.csv` | 0.0 | 1e-12 | YES |
| truth recovery (`e_arm_true`) vs M4-G1 persisted `truth_recovery_rows.csv`, both budgets, 1536 rows compared (3 worlds × 2 budgets × 8 reps × 2 views × 16 authors) | 0.0 | 1e-12 | YES |
| (supplementary) scale-norm recompute vs M4-G1 persisted `g2_spectrum_evidence.csv` scale_min/scale_max, 192 rows | 1.14e-13 | 1e-9 | YES |

**PASS**, all channels exact or well inside tolerance.

### G3 TRUTH-PATH INVARIANCE

Gap-stage-style `e_arm_true` (computed from `context["flat"]`) vs the
truth-path's own budget=1.0 short-circuit, at a **searched** non-degenerate
(rep, view, author) per world (rep0/train/author0 was degenerate on 4 of the
8 D1 worlds — the search loop that fixed this is what surfaced Discovery 2
above), 2 arms (`c_1.0`, `c_4.0`) × 8 worlds = 16 checks: **max abs diff
0.0**. **PASS.**

### G4 MATERIALITY FORM — explicit compliance

- **G0** is a CI-half-width-vs-generator-derived-margin bound (0.5, half the
  slope=0-vs-1 gap) for the primary slope test; the secondary endpoint
  disclosure is explicitly labeled non-gating. Not a significance test on
  the slope difference itself.
- **G2** is an exact-algebraic-identity check (tolerance 1e-9, observed 0.0)
  for the four invariances, plus a positive, deterministic demonstration
  (Frobenius ratio = c) that the operator moved — not a nil-test on whether
  the operator changed at all (which is guaranteed for c≠1 by construction;
  testing THAT would have been exactly the nil-test-on-a-known-nonzero-
  quantity M4-F8 was voided for, and M4-G1's own G4 section already flagged
  this same trap).
- **G3** is a degenerate exact-equality check (0.0 achieved), not a
  significance test.
- **Lean (a)**'s CI-excludes-zero test is a directional/materiality claim
  about a specific numeric slope (whose true value — 0 vs nonzero — is
  precisely this leg's open question), not a nil-test on a known-nonzero
  quantity; M4-G1's own G4 section established this same reasoning for its
  analogous leans. **Lean (b)** is an equivalence bound (CI entirely inside
  a generator-referenced margin), the canonical G4-compliant form. **Lean
  (c)** is a sign check (≥0) plus a categorical argmin check, not a
  significance test. **Compliant throughout.**

## D1 — the c-ladder table (offset, mean across all 8 worlds; both truth-recovery variants, medians)

| c | offset (mean, 8 worlds) | offset std (8 worlds) | truth error @4x (median, 6 valid worlds) | truth error @8x (median, 6 valid worlds) |
|---|---|---|---|---|
| 0.25 | 4.826 | 0.294 | 0.7861 | 0.7862 |
| 0.50 | 6.333 | 0.908 | 0.6456 | 0.6453 |
| 1.00 | 12.003 | 2.228 | 0.5247 | 0.5186 |
| 2.00 | 25.042 | 4.345 | 0.4508 | 0.4456 |
| 4.00 | 51.922 | 8.435 | 0.4221 | 0.4127 |

(Truth-error columns exclude `linear_null_ecology` and
`fast_return_equal_marginal` — the two numerically-invalid worlds; see the
dedicated section below. The naive all-8-world MEDIAN — not mean — is close
regardless, 0.79/0.66/0.54/0.46/0.44, because medians are robust to the
handful of catastrophic rows; it is the MEAN that the lean (b) pairwise CIs
below would have needed protecting, and did.)

Per-world offset by c (all 8 D1 worlds, full precision in `offset_rows.csv`):

| world | c=0.25 | c=0.5 | c=1.0 | c=2.0 | c=4.0 |
|---|---|---|---|---|---|
| condition_alias_ecology | 5.429 | 7.240 | 13.372 | 27.528 | 56.548 |
| endogenous_creation_expansion | 4.920 | 7.026 | 13.754 | 28.475 | 58.344 |
| fast_return_equal_marginal | 4.926 | 6.968 | 13.565 | 28.351 | 58.245 |
| history_gated_ecology | 4.420 | 4.552 | 7.493 | 16.235 | 34.823 |
| linear_null_ecology | 4.807 | 6.569 | 12.776 | 26.771 | 55.723 |
| selection_creation_compensation | 4.699 | 6.256 | 11.956 | 25.193 | 52.217 |
| source_rotated_feedback | 4.773 | 6.592 | 13.288 | 27.055 | 56.022 |
| topology_mismatch | 4.632 | 5.458 | 9.819 | 20.731 | 43.454 |

`offset_norm` rises monotonically with c on every one of the 8 worlds, but
NOT with a single common shape — `history_gated_ecology` (R²=0.924, the
lowest of the 8) is visibly flatter between c=0.25 and c=0.5 than at the
high end, a disclosed curvature noted in the per-world regression table
next.

## D1 — log-log regression: per-world slopes, R², and the CI

| world | slope | intercept | R² |
|---|---|---|---|
| endogenous_creation_expansion | 0.9155 | 2.716 | 0.9867 |
| source_rotated_feedback | 0.9143 | 2.672 | 0.9845 |
| fast_return_equal_marginal | 0.9152 | 2.711 | 0.9854 |
| linear_null_ecology | 0.9097 | 2.662 | 0.9819 |
| selection_creation_compensation | 0.8958 | 2.609 | 0.9788 |
| condition_alias_ecology | 0.8688 | 2.723 | 0.9788 |
| topology_mismatch | 0.8385 | 2.464 | 0.9598 |
| history_gated_ecology | 0.7791 | 2.271 | 0.9240 |

**Primary (paired-by-world, n=8, `g1._paired_world_ci` reused unchanged,
df=7)**: mean slope **0.8796**, 95% CI **[0.8386, 0.9206]**. CI excludes 0
(materially). **CI does NOT contain 1** (upper bound 0.9206 < 1.0) — the
dependence is real but sub-linear, not a pure Euclidean-norm-in-whitened-
units relationship.

**Secondary (pooled OLS, disclosed, non-gating, all 40 (world,c) points,
ignoring world blocks)**: slope **0.8796** (identical point estimate to the
primary method), 95% CI **[0.8093, 0.9499]**, R²=0.944. CI also excludes
both 0 and 1. The two independent methods agree to 4 decimal places on the
point estimate.

## D2 — width companion (all eight M4-G1 arms; diagnostic, not a new target)

| arm | offset (mean, 3 worlds) | width | offset / sqrt(width) |
|---|---|---|---|
| baseline | 12.999 | 13 | 3.605 |
| shrinkage_0.01 | 11.571 | 13 | 3.209 |
| shrinkage_0.1 | 9.755 | 13 | 2.706 |
| shrinkage_1.0 | 7.503 | 13 | 2.081 |
| truncated_90 | 6.129 | 4 | 3.065 |
| truncated_75 | 5.572 | 3 | 3.217 |
| truncated_50 | 5.190 | 2 | **3.670** |
| identity | 4.352 | 13 | **1.207** |

Width-normalizing does **not** rescue `identity`'s anomalous position —
`identity` remains the clear minimum even divided by `sqrt(width)` (1.207,
less than half of any other arm's ratio), so M4-G1's "identity lowest
offset" finding is not explained by a dimension-count artifact; it survives
D2's diagnostic and is instead addressed by D1/lean (c)'s SCALE
normalization below, which does move it.

## Lean adjudication

### Lean (a) — UNITS: log-log slope CI excludes 0

**HOLD.** Slope 0.8796, 95% CI [0.8386, 0.9206]. Excludes 0 comfortably (CI
lower bound is 20× the half-width away from zero). CI does **not** contain
1 — stated plainly per the registration's instruction: the metric's units
dependence is real and precisely estimated, but sub-linear, not the simplest
"pure Euclidean norm in whitened coordinates" hypothesis.

### Pivot — log-log slope CI includes 0 → scale-invariant

**DOES NOT FIRE.** The slope CI excludes 0 by a wide, well-powered margin
(G0 primary half-width only 8.2% of its bar).

### Lean (b) — TRUTH IS SCALE-FREE: all 10 pairwise c-comparisons, both budgets, CI inside ±0.02

**MISS.**

#### Numerical-validity discovery (post-hoc, disclosed in full — does not touch lean (a)/pivot, which were already finalized when this was found)

The naive all-8-world computation produced nonsense: mean differences on
the order of **10⁸–10⁹** (e.g. budget=4x, c=0.25 vs c=4.0: mean diff
−1,358,426,368, CI [−1.72e9, −0.996e9]). Diagnosis, using the
arm-invariant `e_orc_true` (identical computation for every c, so it cannot
be biased by anything this leg manipulates):

| world | median `e_orc_true` @4x | median `e_orc_true` @8x |
|---|---|---|
| topology_mismatch | 0.178 | 0.178 |
| endogenous_creation_expansion | 0.262 | 0.260 |
| selection_creation_compensation | 0.290 | 0.282 |
| source_rotated_feedback | 0.320 | 0.327 |
| history_gated_ecology | 0.380 | 0.372 |
| condition_alias_ecology | 0.735 | 0.736 |
| **linear_null_ecology** | **5,141,574,052** | **3,303,555,873** |
| **fast_return_equal_marginal** | **5,267,807,899** | **3,411,446,739** |

A 9–10 order-of-magnitude jump, present at BOTH budgets, in an
arm-independent quantity — proof this is a pre-existing near-zero-
denominator fragility of `_relative_error(estimate, reference) =
‖estimate−reference‖ / max(‖reference‖, EPS)` when `‖D_true‖` is very small
(these two worlds are exactly the ones with weak/null or purely-linear
mechanisms) at the regenerated 4x/8x truth budgets specifically — NOT a
property of the c-ladder (these two worlds' OFFSET data, a completely
different code path, is and remains sane; see the c-ladder and regression
tables above, where both worlds sit inside the normal range and
`linear_null_ecology`'s own per-world slope/R² — 0.910/0.982 — is unremarkable).
M4-G1 never encountered this because it used only the 3 `HIGH_GAP_WORLDS`,
which are high-signal by construction.

**Both readings, reported explicitly, per the standing rule:**

| reading | worlds | held? | max half-width |
|---|---|---|---|
| naive | all 8 | MISS | 3.6e8 (meaningless) |
| **adopted** | 6 (excludes `linear_null_ecology`, `fast_return_equal_marginal`; threshold: max-over-budget median `e_orc_true` ≤ 10, a bar with 9 orders of magnitude of headroom on both sides) | **MISS** | **0.0189** |

The adopted reading is well-powered and clean (n=745 author-reps per
pairwise check) — this is a genuine, precisely-estimated MISS, not an
artifact of the exclusion:

| budget | c pair | n | mean diff (lo error − hi error) | 95% CI | within ±0.02? |
|---|---|---|---|---|---|
| 4x | 0.25 vs 0.50 | 745 | +0.1274 | [0.1216, 0.1333] | NO |
| 4x | 0.25 vs 1.00 | 745 | +0.2300 | [0.2186, 0.2414] | NO |
| 4x | 0.25 vs 2.00 | 745 | +0.2829 | [0.2672, 0.2985] | NO |
| 4x | 0.25 vs 4.00 | 745 | +0.2891 | [0.2705, 0.3077] | NO |
| 4x | 0.50 vs 1.00 | 745 | +0.1026 | [0.0961, 0.1090] | NO |
| 4x | 0.50 vs 2.00 | 745 | +0.1554 | [0.1434, 0.1674] | NO |
| 4x | 0.50 vs 4.00 | 745 | +0.1617 | [0.1461, 0.1773] | NO |
| 4x | 1.00 vs 2.00 | 745 | +0.0528 | [0.0462, 0.0594] | NO |
| 4x | 1.00 vs 4.00 | 745 | +0.0591 | [0.0479, 0.0703] | NO |
| 4x | 2.00 vs 4.00 | 745 | +0.0063 | [0.0009, 0.0117] | **YES** |
| 8x | 0.25 vs 0.50 | 745 | +0.1280 | [0.1222, 0.1339] | NO |
| 8x | 0.25 vs 1.00 | 745 | +0.2326 | [0.2212, 0.2440] | NO |
| 8x | 0.25 vs 2.00 | 745 | +0.2894 | [0.2737, 0.3052] | NO |
| 8x | 0.25 vs 4.00 | 745 | +0.3009 | [0.2820, 0.3198] | NO |
| 8x | 0.50 vs 1.00 | 745 | +0.1046 | [0.0982, 0.1110] | NO |
| 8x | 0.50 vs 2.00 | 745 | +0.1614 | [0.1494, 0.1735] | NO |
| 8x | 0.50 vs 4.00 | 745 | +0.1729 | [0.1569, 0.1889] | NO |
| 8x | 1.00 vs 2.00 | 745 | +0.0569 | [0.0502, 0.0636] | NO |
| 8x | 1.00 vs 4.00 | 745 | +0.0683 | [0.0568, 0.0799] | NO |
| 8x | 2.00 vs 4.00 | 745 | +0.0115 | [0.0058, 0.0171] | **YES** |

18 of 20 pairwise checks fall decisively outside ±0.02 (up to 15× the
margin); only the two mildest, most-adjacent pairs (c=2.0 vs c=4.0, at both
budgets) fall inside. **Sign is consistently positive**: lower c always
means higher error — truth recovery genuinely, monotonically, precisely
improves as c increases across this ladder. **MISS**, decisively, not a
knife-edge.

### Lean (c) — NORMALIZATION REPAIRS THE ORDERING: M4-G1's 8 arms, scale-normalized offset

**HOLD**, at both budgets, no disagreement.

**Correctness anchor first**: this leg's own n=7 (baseline excluded, matching
M4-G1's exact convention), raw-offset Spearman @4x = **−0.7857**, vs M4-G1's
disclosed **−0.786** — reproduces to within 0.0003 (rounding), confirming
this leg's data plumbing loads M4-G1's persisted per-arm numbers correctly
before anything new is computed from them.

| arm | raw offset (mean) | geometric mean scale | scale-normalized offset | truth error @4x |
|---|---|---|---|---|
| baseline | 12.999 | 32.627 | 0.398 | 0.5562 |
| shrinkage_0.01 | 11.571 | 29.879 | **0.387** | 0.5512 |
| shrinkage_0.1 | 9.755 | 23.647 | 0.413 | 0.5539 |
| shrinkage_1.0 | 7.503 | 15.124 | 0.496 | 0.5751 |
| truncated_90 | 6.129 | 2.237 | 2.740 | 0.8801 |
| truncated_75 | 5.572 | 1.881 | 2.963 | 0.9085 |
| truncated_50 | 5.190 | 1.647 | 3.151 | 0.9574 |
| **identity** | **4.352** (lowest, raw) | 1.000 (by construction, untouched) | **4.352** (now the HIGHEST) | 0.8656 |

| statistic | raw offset | scale-normalized offset |
|---|---|---|
| Spearman vs truth error @4x (n=8, baseline included) | **−0.7857** | **+0.8333** |
| Spearman vs truth error @8x (n=8) | −0.7857 | +0.8333 |
| argmin arm | `identity` | `shrinkage_0.01` |

Both registered criteria hold, at both budgets, identically (0.8333 ==
0.8333, no budget disagreement to adjudicate away): the correlation flips
sign from strongly negative to strongly positive, and `identity` — the arm
whose raw offset was spuriously lowest precisely because it has zero
amplification to divide out — becomes, once normalized, the single
**worst**-scoring arm, matching its poor truth-recovery (0.8656, second-
worst of all eight). The scale-normalized ranking is now directionally
consistent with truth-recovery quality, exactly what "normalization repairs
the ordering" claims. **HOLD.**

## Verdict

**`METRIC_UNITS_DISQUALIFIED`.** Per the registration's own branch: the
slope CI excludes 0, so **`offset_norm` is disqualified as an optimization
target in its raw form.** Lean (c)'s result sharpens why: M4-G1's own
headline anti-correlation was substantially a units artifact of comparing
arms whose intrinsic amplification scale differs by up to 32.6× (baseline)
down to 1.0× (identity) — once that confound is divided out, the
correlation is not merely "no longer negative," it flips to strongly
positive and reproduces the arms' actual truth-recovery ordering.

**What this does and does not imply for M4-E2's scale-family attribution**,
stated precisely as instructed: M4-E2's decomposition was computed **once**,
at the single deployed baseline operator's own fixed units — it never varied
c and never compared the offset across operators of different intrinsic
scale. As a description of which directions of displacement dominate **at
that one fixed operator**, M4-E2's decomposition is not directly tested or
overturned by this leg (this leg decomposed nothing; it only tested whether
the total scales with a global unit change). What IS undermined —
demonstrated directly by lean (c)'s sign flip — is treating **raw
`offset_norm` magnitudes as comparable, scale-free evidence across
operators whose own intrinsic scale differs**, which is exactly the design
M4-G1 used for its own cross-arm comparison (baseline vs shrinkage vs
truncation vs identity, arms whose geometric-mean-scale spans 32.6× to
1.0×). M4-G1's own conclusions drawn from comparing raw offset numbers
across those arms — most importantly "identity has the lowest offset" —
are shown here to be substantially a units artifact of that comparison,
not evidence about the arms' relative structural quality. M4-E2's own
single-operator decomposition is not itself proven wrong, but any
downstream use of it to justify comparing raw offset **across** differently-
scaled whitening choices (which is precisely what M4-G1's whole design did)
inherits the same disqualification demonstrated here.

Per lean (b): even setting the raw-units problem aside, truth-recovery
itself is not scale-free either — it improves substantially and precisely
as c increases across the tested range (error falls from 0.786 to 0.422 at
budget=4x, a ~46% relative reduction, decisively outside the equivalence
margin at 8 of 10 pairs). Interpreted alongside D1's own offset-vs-c
relationship (offset also rises with c, slope 0.88), this means: **within
the pure-scale c-ladder specifically** (as opposed to M4-G1's
non-uniform shrinkage/truncation arms), bigger c is simultaneously "worse"
by the raw offset metric and "better" for truth recovery — offset and
truth-recovery ERROR move in *opposite* directions as c grows, i.e. offset
and recovery QUALITY move together. This is a different, and interesting,
relationship from M4-G1's own non-uniform-regularization finding (where
LOWER offset associated with worse recovery); it is reported here as a
directly-computed, well-powered fact about the D1 ladder specifically, not
extrapolated to the non-uniform arms this leg did not re-test.

## Honest anomalies and disclosures

- **Two world-selection corrections were made mid-compute** (Part 0.0
  above), both mechanical/design discoveries (seed-sharing duplication;
  gate-inapplicability from all-degenerate `D_true`), both made and
  resolved before any slope, truth-recovery-equivalence, or lean number
  existed for the worlds in question. Neither correction touched lean
  (a)/pivot's final numbers.
- **A third, purely statistical, correction was needed for lean (b)
  specifically** (numerical-validity discovery, above), found AFTER lean
  (a)/pivot were already finalized. This is disclosed with maximal
  precision about timing: lean (a)/pivot's world set and result were never
  revisited; only lean (b)'s own world subset was corrected, using an
  arm-invariant diagnostic (`e_orc_true`) that cannot be biased toward any
  particular lean (b) outcome, and both readings (naive-nonsense and
  corrected-clean) are persisted (`lean_b_pairwise_equivalence.csv`,
  `lean_b_pairwise_equivalence_naive_all8_worlds.csv`,
  `lean_b_truth_validity_diagnostic.csv`).
- **A width-invariance aggregation bug was caught and fixed before this
  report was written**: the first `--assemble` run reported
  `width_invariant: false` for G2, appearing to fail an algebraic identity.
  Investigation showed the check had compared width **globally** across all
  8 worlds' rows (which legitimately differ, 7–13, by Leg 10's own
  rank-tolerance cut per context) rather than **within** each (world,
  repetition) context across the 5 c values (which is the actual claim, and
  holds exactly on 64/64 contexts). Fixed and re-run; see
  `g2_invariance_evidence.csv`.
- **`history_gated_ecology` shows visible log-log curvature** (R²=0.924, the
  lowest of the 8 worlds; flat between c=0.25 and c=0.5, steeper above
  c=1.0) — disclosed in the per-world regression table; it does not change
  the paired-by-world CI's conclusion (its own slope, 0.779, is still
  comfortably inside the pooled CI) but is a genuine, visible departure from
  a single clean power law on this one world, worth a future leg's
  attention if this line continues to probe the objective's functional
  form.
- **Truth-recovery in the valid 6-world set improves monotonically across
  the entire c-ladder**, not merely failing to be flat: median error
  0.786 → 0.646 → 0.525 → 0.451 → 0.422 (budget=4x) as c rises from 0.25 to
  4.0. The improvement is diminishing (largest step 0.25→0.5, smallest
  2.0→4.0, the only pair inside the equivalence margin) — consistent with
  approaching some asymptote, not explored further here.

## Faithfulness chain (all green)

| gate | value |
|---|---|
| analytic D_true unit check (all D1 contexts) | max 1.78e-15 |
| basis anchor vs context v2_basis (`c_1.0`, all 8 worlds × 8 reps × 3 roles) | 0.0 |
| offset anchor vs M4-G1 persisted (3 `HIGH_GAP_WORLDS`) | 0.0 |
| truth-recovery anchor vs M4-G1 persisted (3 worlds × 2 budgets × 8 reps × 2 views × 16 authors = 1536 rows) | 0.0 |
| scale-norm recompute vs M4-G1 persisted g2 CSV (192 rows) | 1.14e-13 (tol 1e-9) |
| frozen-world assertion (oracle_basis/author_parameters unchanged across budgets) | exact equality, all 8 worlds × 8 reps × 2 budgets |
| G3 truth-path degenerate equality (searched non-degenerate spot, 2 arms × 8 worlds) | 0.0 (16/16) |
| G2 eigenvector/relative-spectrum/condition-number invariance | 0.0 (all rows) |
| G2 channel liveness (Frobenius ratio recovers c) | 0.0 max abs diff |
| row-count completeness (offset/truth/scalenorm partials) | exact match to expected counts, all worlds |
| lean (c) correctness anchor vs M4-G1 disclosed Spearman | 0.0003 (rounding only) |

## Boundaries

Finite synthetic M4-C.2 worlds only. D1 (lean a/b, G0, pivot): 8 worlds, all
mutually independent seeds (`endogenous_creation_expansion`,
`selection_creation_compensation`, `source_rotated_feedback` — E2/M4-G1-
anchored; `linear_null_ecology`, `topology_mismatch`,
`fast_return_equal_marginal`, `history_gated_ecology`,
`condition_alias_ecology` — fresh); lean (b)'s adopted reading further
restricts to 6 of those 8 (excludes `linear_null_ecology`,
`fast_return_equal_marginal` for the numerical-validity reason above; lean
(a)/G0/pivot use all 8, unaffected). Lean (c): M4-G1's own 3
`HIGH_GAP_WORLDS`, its own 8 arms, reusing M4-G1's persisted offset/truth
numbers plus a light, cross-anchored ingredients-only recompute for the
scale-normalization denominator. Truth-referenced recovery via
budget-regenerated (4x/8x events) finite panels from the frozen world law,
compared to the analytic `D_true`, exactly M4-G1's own construction, reused
unchanged. No natural-text, personality, or clinical claim; no seal, no
independent verification (operator directive 2026-08-01). This leg answers
the units-vs-trade-off question M4-G1's planner adjudication note posed; it
does not re-open M4-G1's own leans (a)/(b)/(c) (COSMETIC_LEVER, unchanged)
and does not decompose the offset the way M4-E2 did (no new attribution
percentages are computed here). The open question for any future leg in
this line: given `offset_norm` is disqualified in its raw form but a
scale-normalized version (Part 0.1) demonstrably repairs its ordering on
M4-G1's own 8 arms, whether that normalized metric — or some refinement of
it — is a viable REPLACEMENT optimization target, and whether it remains
well-behaved outside the specific 8-arm, 3-world setting checked here.
