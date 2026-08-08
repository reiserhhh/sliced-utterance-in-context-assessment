# SUICA M4-G4 — Covariant Ridge: Does a Post-Whitening Ridge Deliver c-Invariant Recovery Without Losing the Gain?

Tier: **EXPLORATORY** (open-exploration phase, operator directive 2026-08-01).
Registered before run: `docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md`, "M4-G4
registration" (2026-08-03, BEFORE run); ledger row M4-G4. Script:
`scripts/run_suica_m4_g4_covariant_ridge.py`. Artifacts:
`results/m4_g4_covariant_ridge/`. Machinery imported and reused unchanged
from M4-G1/G2/G3 (`g1`/`g2`/`g3` in the script): world set (`g3.D1_WORLDS`,
identical to `g2.D1_WORLDS`), valid-6-world truth-recovery subset (M4-G2's
own adopted rule, reused verbatim), context builder (`g1._build_world_contexts`),
c-ladder whitening construction (`g2._whitening_for_c`), unchanged basis
construction (`leg10._bases_from_whitening`), CI helpers
(`g1._paired_world_ci`, `g1._paired_author_ci`) — and, most centrally, M4-G3's
own generic truth-row builder `g3._truth_rows_for_context`, called here with
this leg's own five arm names/bases/params exactly as it is generic over
`arms`. No estimator internals are copied without disclosure; the only new
functions are the post-whitening statistics, their alpha calibration, a small
arm-parameter dispatcher, and this leg's own gate/lean bookkeeping.

## Headline, stated up front

**The PIVOT FIRES. Neither covariant ridge candidate achieves c-invariance at the registered ±0.02 margin, at the registered AUTHOR grain (n=745), well-powered (not underpowered) on the decisive comparison.** Both `covariant_var` and `covariant_msq` — numerically near-identical throughout — cut the raw c-dependence across c ∈ {0.25, 1.0, 4.0} by **89.1%** relative to doing nothing to `hazard_ridge` (the specificity control's own c=0.25-to-c=4.0 swing, 0.2892 @4x / 0.3010 @8x, is this leg's own measurement of that raw swing, and matches `baseline`'s own behavior since floor is inert) — a large, real, mechanistically-attributable effect, not noise. But the **residual** swing (0.0316 @4x, 0.0328 @8x, from c=0.25 to c=4.0) is itself decisively outside the ±0.02 equivalence band (CI [0.0261, 0.0372] @4x, half-width 0.0056 — barely over half the 0.01 power bar, not a marginal call on power, even though it is the widest of the three c-pairs tested for these arms). **Lean (a) MISSES cleanly for both arms** (not underpowered — every one of the 12 comparisons feeding lean (a) has a half-width at most 0.0056, well inside the 0.01 bar). **Lean (c) SPECIFICITY is decisively CONFIRMED** (the same covariant rule applied to `weight_floor`, an M4-G3-inert constant, produces even larger non-invariance — 3.2–17.4× larger on the same c-pairs — matching baseline's own established direction, all six checks OUTSIDE the margin) — the reduction achieved by `covariant_var`/`covariant_msq` is real and specific to touching `hazard_ridge`, not a generic artifact of "any constant made to vary with c." **Lean (b) (disclosed companion, not officially reached since lean (a) never HOLDS) also MISSES decisively** — at c=1, the covariant arms sit at baseline's own (worse) level, not `g3_raw_scale`'s (better) one, exactly as the pre-registered mechanistic prediction below anticipated. G0, G1, G2, G3 all pass or report cleanly (G1 anchor 0.0, G3 truth-path invariance 0.0, G2 ridge/floor-vs-c ratios exactly 16.0/0.0625 as designed). **Per the registration's own consequence: the localization M4-G3 found is confirmed real but incomplete — a simple `ridge = alpha·stat` functional form, under either tested post-whitening statistic, cannot close the residual gap — and the redesign target now moves to the objective's FUNCTIONAL FORM**, specifically the mixed c-scaled/non-c-scaled column structure the mechanistic analysis below identifies as the likely remaining channel.

## Part 0 — registered candidate statistics, calibration rule, specificity control (written before compute; transcribed here)

### What "the whitened quantity the ridge is actually added to" is

`_bases_from_whitening(context, ingredients, whitening)` builds, per role,
`whitened = (raw - center) @ whitening`, then column-stacks an intercept.
`whitening = c · whitening0` (`g2._whitening_for_c`) is a **scalar** multiple
of the deployed (c=1) whitening matrix, so algebraically, for fixed
`(raw, center, whitening0)`:

```
whitened_c = (raw - center) @ (c · whitening0) = c · whitened_1        (*)
```

— an exact identity, not an approximation: going from c=1 to c=c′ is a
literal uniform scalar rescale of every non-intercept basis column.
`hazard_ridge` enters as `penalty = ridge·n·I`, added directly to
`design.T @ diag(weight) @ design`, whose `condition_*`/`feedback_*` blocks
are built from these same whitened columns
(`estimator._hazard_design`, `suica_core/m4_chart_ecology_estimator.py:287-330`).
A statistic "computed on the whitened quantity the ridge is actually added
to" is therefore a statistic of `whitened_c` itself — not of the raw,
pre-whitening eigenvalues M4-G3's `RAW_SCALE` used.

### Registered candidate statistics (S1, S2)

Both computed from `basis = leg10._bases_from_whitening(context, ingredients,
g2._whitening_for_c(ingredients, c))` (unchanged; deployed intercept — this
leg's arms never touch A6), dropping the intercept column:

| | formula | interpretation |
|---|---|---|
| S1 "var" | mean, over 3 roles × all non-intercept columns, of `Var_over_categories(whitened_c[:,j])` (ddof=1) | direct post-whitening analogue of `RAW_SCALE` (which was the mean *eigenvalue*, i.e. mean per-direction *variance*, of the raw centered features) |
| S2 "msq" | mean, same scope, of `Mean_over_categories(whitened_c[:,j]^2)` (uncentered) | the more literal reading of "the quantity summed into the Gram matrix diagonal ridge is added to" — that diagonal entry is literally `Σ_i weight_i · design[i,j]²`, an uncentered second moment; `center` is built once from a separate prototypes panel, so a role's own `raw − center` need not be zero-mean, so S1/S2 can genuinely differ |

By identity (*), both are **exact**, algebraic, homogeneous-degree-2
functions of c: `POST_SCALE_k(context, c) = c² · POST_SCALE_k(context, 1)`
for k ∈ {var, msq}, for every context — this is what makes them genuinely
**covariant** (move with c by construction), in direct contrast to
`RAW_SCALE`, which is identical at every c by construction (computed
upstream of whitening entirely).

### Alpha calibration rule (registered; not tuned on outcomes)

```
ridge_covariant_k(context, c) := alpha_k · POST_SCALE_k(context, c)
alpha_k := hazard_ridge_deployed / MEAN_across_64_(world,rep)_contexts( POST_SCALE_k(context, c=1.0) )
```

— a single **global** scalar `alpha_k` (not per-context), computed once from
a dedicated `--stage calibrate` pass over all 64 contexts at c=1 (no IRLS
fit, no truth-recovery number touched), mirroring M4-G3's own A1 structure
(one global multiplier × a per-context statistic). This literally implements
the registration's own named example ("matching the deployed ridge at c=1"):
by construction, `MEAN_across_contexts(ridge_covariant_k(context, 1.0)) ==
hazard_ridge_deployed` exactly.

**Registered ambiguity, both readings disclosed.** "Matching the deployed
ridge at c=1" could instead mean **per-context** exact matching
(`alpha_context := hazard_ridge_deployed / POST_SCALE_k(context, 1)`). By
identity (*) this collapses, algebraically and exactly, to
`ridge_covariant(context, c) = hazard_ridge_deployed · c²` — a universal,
context-free, **statistic-free** formula, identical for S1 and S2 alike
(confirmed in `calibration.json`'s `per_context_calibration_limit`: 0.0003125
/ 0.005 / 0.08 at c=0.25/1/4, matching M4-G3's own independently-derived
toy-model plausibility target of 0.0003125 at c=1 for reproducing c=4's
effective ridge). This is a clean, disclosed mathematical fact worth
recording in its own right, but it would make testing "candidate statistics"
(plural, as registered) vacuous — S1 and S2 would be identical. The **global**
reading is adopted for exactly this reason (preserves genuine, testable
cross-context variation between S1 and S2) and because it is the literal
structural analogue of M4-G3's own A1.

### Pre-registered mechanistic prediction (disclosed before compute)

For the `model=="base"` route (intercept + `condition_*` columns only, no
feedback/gate cross-terms), identity (*) plus global alpha calibration means
a diagonal covariate rescale by c, compensated by a ridge exactly
proportional to c², reproduces the *same* fitted coefficients (mapped
through `beta_c = beta_1/c`) at every c — a provable mechanism, not a hope.
Two disclosed limits on how far this reaches, both stated **before** compute:
**(i)** alpha is calibrated globally, not per-context, so exact invariance
holds only up to how much `POST_SCALE_k(context,1)` itself varies
context-to-context around the global mean; **(ii)** for `return`/`feedback`/
`gate` routes, `_hazard_design` also builds columns from `rows["generated"]`/
`rows["duration"]` (raw world data, never touched by c) and from
`basis[:,0]` (the unscaled intercept sub-column) crossed with
`response_next` (the `feedback_0_d`/`gate_0_d` sub-block) — these do **not**
satisfy identity (*) and are not compensated by a c²-ridge, so exact
invariance is a base-route-only guarantee; other routes were registered as
an **open empirical question**, not a foregone conclusion. Because alpha is
calibrated to reproduce `hazard_ridge_deployed` (0.005) at c=1 — not
`g3_raw_scale`'s own much weaker c=1 value (0.00023–0.00089) — the
a priori expectation registered here was: **lean (a) plausibly HOLDS**
(mechanistically grounded), **lean (b) at material risk of MISSING** because
the invariant level this construction settles on resembles baseline's own
(worse) c=1 performance, not `g3_raw_scale`'s (better) one.

**What actually happened (Part 1, below) confirms half of this prediction
decisively (lean (b) MISSES, exactly as anticipated and for the anticipated
reason) and refutes the other half in a mechanistically legible way: lean
(a) also MISSES, because limits (i)/(ii) together are larger than the
prediction allowed for — not absent, but not small enough to fit inside
±0.02 at n=745 precision.** This is exactly the kind of registered,
falsifiable prediction whose failure is informative rather than embarrassing:
the residual (10.9% of the raw swing) is direct, quantitative evidence of
how much of M4-G3's scale dependence lives *outside* the pure-ridge,
diagonal-rescale story.

### Specificity control: `weight_floor`, and why not `clip_bound`/`probe_epsilon`

Of M4-G3's four cleanly-INERT-at-both-grains constants (`tolerance`,
`weight_floor`, `clip_bound`, `probe_epsilon`): `tolerance`'s adaptive form
was a mode switch, not multiplicative — excluded. `clip_bound` (deployed
20.0) and `probe_epsilon` (deployed 0.05) were **rejected** for this leg's
control despite being valid M4-G3 nulls: a covariant clip at c=0.25 could
plausibly tighten to O(1) on the logit scale (no longer obviously a no-op);
a covariant epsilon at c=4 could grow to O(1), threatening the
finite-difference small-step approximation itself — both plausible *genuine*
channels, which would confound the specificity story. `weight_floor`
(deployed 1e-4) was adopted: `fitted·(1−fitted) ∈ [0, 0.25]` regardless of
design scale (the sigmoid saturates any c), so covariant floor values across
the *whole* tested ladder (realized: 6.25e-6 to 1.6e-3, see G2 below) stay
far below where the floor could plausibly bind in either direction.
`floor_covariant = alpha_floor · POST_SCALE_VAR(c)` (reuses S1);
`hazard_ridge` and every other constant stay at deployed values in this arm.

### Design summary

Five arms, `baseline` (c=1 only, anchor), `g3_raw_scale` (M4-G3's own
`adaptive_hazard_ridge` formula, computed fresh at c=1 only — anchor + lean
(b) reference point; its own c=0.25/4.0 values are **not** recomputed here,
sourced directly from M4-G3's persisted winner-ladder files for the
descriptive table only, disclosed as unverified-by-this-leg at those two
c-values, see the G1 anomaly below), `covariant_var`/`covariant_msq`/
`specificity_weight_floor` (full new compute, c ∈ {0.25, 1.0, 4.0}). **The
registered analysis grain is the AUTHOR grain** (n up to 745, M4-G2's valid
6-world subset, degenerate-reference exclusion, reused verbatim) per the
fifth standing rule; world-grain numbers are a disclosed companion only. No
offset/GPA stage: this leg's own lean (c) is specificity, not a cosmetic-trade
check, and M4-G3 already established structurally that neither `hazard_ridge`
nor `weight_floor` reach `_bases_from_whitening` at all.

## Part 1 — Outcome

*(Everything below was computed after the run; Part 0 above was frozen
before compute began.)*

### G0 POWER (reported first, per instruction)

Pre-registered bar: half of this leg's own ±0.02 leaning margin = **±0.01**
absolute half-width (this line's "half of my own leaning bar" convention —
G1: half of 25%, G2: half the slope 0-vs-1 gap, G3: half of 50%), adopted
because this leg's own leans (a)/(b)/(c) are stated in absolute (not
%-of-gain) terms, unlike M4-G3's lean (a). The registration's literal
"against the c=4 gain" framing is also reported: M4-G3's own persisted
author-level c=4 gain is 0.0591 (@4x) / 0.0683 (@8x).

| | value |
|---|---|
| Comparisons run at author grain | 22 (lean (a): 2 arms × 3 c-pairs × 2 budgets = 12; lean (b) companion: 2 arms × 2 budgets = 4; lean (c): 1 arm × 3 c-pairs × 2 budgets = 6) |
| Half-width range | 0.00205 – 0.01892 (median 0.00556) |
| Underpowered vs ±0.01 bar | 10 of 22 |
| Half-width as fraction of M4-G3's own c=4 gain | 0.030 – 0.314 |

**The 10 underpowered-by-bar comparisons are exactly the 6 lean (c) rows and
4 lean (b) companion rows — the ones with the LARGEST effects (0.05–0.31),
where a half-width of 0.011–0.019 is still 4.6–20.4× smaller than the
observed effect itself.** None of them are ambiguous: every one is
classified OUTSIDE its margin (see below), because "underpowered vs the
±0.01 bar" only matters for resolving effects *near* the ±0.02 knife-edge —
it does not, and under the registered equivalence-form logic must not,
block a MISS conclusion on an effect that is itself 2.7–15.0× the margin.
**The 12 lean (a)
rows — the ones that decide the PIVOT — are all adequately powered** (every
half-width ≤ 0.0056, barely more than half the 0.01 bar); the decisive
comparison (`covariant_var`/`msq`, c=0.25 vs c=4.0) has a half-width of
0.0056 — the widest of the three pairs tested for these two arms, but still
comfortably inside the power bar, not a borderline call. **The PIVOT firing
here is not an underpowered non-adjudication — the opposite of M4-G3's own
outcome.**

### G1 ANCHOR

| check | n compared | max abs diff | tolerance | pass |
|---|---|---|---|---|
| `baseline`@c=1 vs M4-G3 persisted `baseline`@c=1 | 4,096 | **0.0** | 1e-12 | YES |
| `g3_raw_scale`@c=1 vs M4-G3 persisted `adaptive_hazard_ridge`@c=1 | 4,096 | **0.0** | 1e-12 | YES |

**PASS**, exact to the bit, for the two independently-recomputed anchor
points. **Disclosed scope note**: `g3_raw_scale` is anchored only at c=1.0
— its own c=0.25/4.0 values (used solely in the descriptive per-arm table)
are read directly from M4-G3's already-gated
`partial_winner_ladder_*_adaptive_hazard_ridge.csv` files, not
independently re-verified at those two c-values by this leg (see "Honest
anomalies," below, for the mechanical bug this caught).

### G2 COVARIANCE LIVENESS

Realized ridge/floor value (mean across all 64 contexts) at each c, and the
ratio against c=1 — the test of whether the manipulation actually moved:

| arm | parameter | mean @c=0.25 | mean @c=1 | mean @c=4 | ratio c4/c1 | ratio c0.25/c1 | theoretical | status |
|---|---|---|---|---|---|---|---|---|
| `covariant_var` | ridge | 0.0003125 | 0.0050000 | 0.0800000 | **16.0000** | **0.0625** | 16.0 / 0.0625 | **LIVE** |
| `covariant_msq` | ridge | 0.0003125 | 0.0050000 | 0.0800000 | **16.0000** | **0.0625** | 16.0 / 0.0625 | **LIVE** |
| `specificity_weight_floor` | weight_floor | 0.00000625 | 0.00010000 | 0.00160000 | **16.0000** | **0.0625** | 16.0 / 0.0625 | **LIVE** |
| `g3_raw_scale` (contrast) | ridge | 0.0003817 | 0.0003817 | 0.0003817 | 1.0000 | 1.0000 | 1.0 / 1.0 | INERT (analytic, c-independent by construction — M4-G3's own finding) |

**Every ratio matches its theoretical value to 10+ significant figures**
(16.000000000000142 / 0.062499999999991215 and similarly for the other two —
floating-point exact, not merely "close"), confirming identity (*)
empirically at the full pooled scale, not just the single-context spot check
performed before pooling (Part 0's independent verification, reproduced
here: ratios exactly 16.0/0.0625 on a freshly-rebuilt context, `condition_alias_ecology`
rep 0, computed before any of the 8-world compute was used for this specific
check). **`g3_raw_scale`'s own ridge is, by contrast, exactly c-invariant —
the flaw M4-G3 identified, reproduced here as a clean numerical fact, not
merely asserted.** All three of this leg's own manipulated constants are
unambiguously LIVE (moved by construction); none is VACUOUS.

### G3 TRUTH-PATH INVARIANCE

Gap-stage-style `e_arm_true` (via `context["flat"]`) vs. the truth-path's own
budget=1.0 short-circuit, at a searched non-degenerate `(rep, view, author)`
per world, for every `(arm, c)` combination actually computed (11 per world:
5 at c=1, 3 at c=0.25, 3 at c=4) × 8 worlds = **88 checks: max abs diff 0.0.**
**PASS.**

### G4 MATERIALITY FORM — explicit compliance

- **G0** is a CI-half-width-vs-bar equivalence bound (±0.01, half of the
  ±0.02 leaning margin), reported both in absolute terms and as a fraction
  of M4-G3's own persisted c=4 gain; underpowered comparisons are flagged
  and excluded from being read as nulls, never silently passed.
- **G1** is a degenerate exact-equality check (0.0 achieved on both
  independently-recomputed anchors), not a significance test.
- **G2** is a ratio-vs-theoretical-value equivalence check (LIVE iff the
  realized ratio departs from 1.0 by more than 10% in both directions,
  decisively satisfied at 16.0/0.0625 vs the trivial 10% bar) rather than a
  binary "did it change" test.
- **Leans (a)/(b)/(c)** are three-way WITHIN/OUTSIDE/AMBIGUOUS classifications
  on paired-author CIs against fixed margins (±0.02 two-sided for (a)/(c),
  one-sided for (b)) — never a nil-significance test; a wide CI that is
  still entirely outside the margin is decisive evidence of a real effect,
  not a power failure, and is reported as such (the 10 "underpowered" rows
  above are exactly this case). **Compliant throughout.**

## Per-arm × per-c summary table

Pooled author-level mean `e_arm_true` (n=745, 6 valid worlds, degenerate
excluded), both budgets:

| arm | c | @4x mean | @8x mean |
|---|---|---|---|
| `baseline` | 1.00 | 0.5582 | 0.5556 |
| `g3_raw_scale` | 1.00 | 0.5068 | 0.4949 |
| `covariant_var` | 0.25 | 0.5736 | 0.5711 |
| `covariant_var` | 1.00 | 0.5602 | 0.5577 |
| `covariant_var` | 4.00 | 0.5420 | 0.5383 |
| `covariant_msq` | 0.25 | 0.5738 | 0.5713 |
| `covariant_msq` | 1.00 | 0.5605 | 0.5579 |
| `covariant_msq` | 4.00 | 0.5422 | 0.5385 |
| `specificity_weight_floor` | 0.25 | 0.7882 | 0.7882 |
| `specificity_weight_floor` | 1.00 | 0.5582 (=`baseline`, exact) | 0.5556 (=`baseline`, exact) |
| `specificity_weight_floor` | 4.00 | 0.4990 | 0.4872 |

Three things visible at a glance, all load-bearing for the adjudication
below: **(1)** `covariant_var`/`covariant_msq` are numerically indistinguishable
throughout (differ only in the 3rd–4th decimal) — S1 and S2 turned out to
carry almost identical information in this data, a real finding, not an
implementation error (confirmed via G2's own independent per-arm ridge
values, which also match to 4 decimals). **(2)** `specificity_weight_floor`
is bit-identical to `baseline` at c=1 (ridge is the only thing that moves
recovery; floor genuinely does not, even measured this way) and moves in
`baseline`'s own established direction elsewhere (worse at c=0.25, better at
c=4 — the same monotonic pattern M4-G2 first documented). **(3)**
`covariant_var`/`msq` sit at c=1 within 0.002–0.003 of `baseline` (0.560 vs
0.558) and nowhere near `g3_raw_scale` (0.507) — the pre-registered
mechanistic prediction confirmed directly.

## Lean adjudication

### Lean (a) — C-COVARIANCE: at least one covariant arm is c-invariant within ±0.02, author grain

**MISS for both arms, cleanly (not underpowered).**

| arm | budget | c-pair | mean diff | 95% author CI | half-width | class |
|---|---|---|---|---|---|---|
| `covariant_var` | 4x | 0.25 vs 1.0 | +0.0133 | [0.0113, 0.0154] | 0.0021 | WITHIN |
| `covariant_var` | 4x | 0.25 vs 4.0 | +0.0316 | [0.0260, 0.0372] | 0.0056 | **OUTSIDE** |
| `covariant_var` | 4x | 1.0 vs 4.0 | +0.0183 | [0.0140, 0.0226] | 0.0043 | AMBIGUOUS |
| `covariant_var` | 8x | 0.25 vs 1.0 | +0.0134 | [0.0113, 0.0155] | 0.0021 | WITHIN |
| `covariant_var` | 8x | 0.25 vs 4.0 | +0.0328 | [0.0273, 0.0383] | 0.0055 | **OUTSIDE** |
| `covariant_var` | 8x | 1.0 vs 4.0 | +0.0194 | [0.0151, 0.0236] | 0.0043 | AMBIGUOUS |
| `covariant_msq` | 4x | 0.25 vs 1.0 | +0.0133 | [0.0113, 0.0154] | 0.0021 | WITHIN |
| `covariant_msq` | 4x | 0.25 vs 4.0 | +0.0316 | [0.0261, 0.0372] | 0.0056 | **OUTSIDE** |
| `covariant_msq` | 4x | 1.0 vs 4.0 | +0.0183 | [0.0140, 0.0226] | 0.0043 | AMBIGUOUS |
| `covariant_msq` | 8x | 0.25 vs 1.0 | +0.0134 | [0.0113, 0.0155] | 0.0021 | WITHIN |
| `covariant_msq` | 8x | 0.25 vs 4.0 | +0.0328 | [0.0273, 0.0383] | 0.0056 | **OUTSIDE** |
| `covariant_msq` | 8x | 1.0 vs 4.0 | +0.0194 | [0.0151, 0.0236] | 0.0043 | AMBIGUOUS |

Both arms are decided by the **same** pair (c=0.25 vs c=4.0, both budgets):
its half-width (0.0055–0.0056) is the widest of the three pairs tested for
these two arms, yet still barely over half the 0.01 power bar — comfortably
adequate, not a power failure — and its CI clears the ±0.02 margin by
30.2–36.4% of the margin's own width (30.2%/30.4% at 4x, 36.3%/36.4% at 8x
for `covariant_var`/`covariant_msq` respectively) — not a knife-edge. Per
`_arm_status_from_pairs`, one OUTSIDE pair is sufficient for a clean MISS
regardless of the other pairs' AMBIGUOUS status (a genuinely unresolved
1.0-vs-4.0 comparison does not rescue a decided 0.25-vs-4.0 one).
**`covariant_var` status: MISS. `covariant_msq`
status: MISS. Neither arm HOLDS. Lean (a) MISSES.**

**Quantified relative to doing nothing** (the specificity control's own
0.25-vs-4.0 swing, 0.2892 @4x / 0.3010 @8x, which reproduces `baseline`'s
raw c-dependence almost exactly): the covariant ridge construction cuts the
full swing by **89.1%** at both budgets (residual 10.9% / 10.9%) — a large,
real, mechanistically-grounded improvement over doing nothing. **Quantified
relative to `g3_raw_scale`'s own swings, pair by pair** (G3's own persisted
pairwise diffs, absolute value, @4x: 0.0836 @0.25-vs-1, 0.0494 @0.25-vs-4,
0.0342 @1-vs-4): `covariant_var`'s own diffs (0.0133/0.0316/0.0183) are
flatter on every pair, but by a very uneven margin — 6.3× flatter on
0.25-vs-1, only 1.6× flatter on 0.25-vs-4 (the pair that actually decides
lean (a)), and 1.9× flatter on 1-vs-4 (8x budget: 7.0×/2.1×/1.2×
respectively). **The pair where the improvement is smallest relative to
`g3_raw_scale` is the same pair that fails the ±0.02 margin** — reporting
only the most favorable ratio (6.3×) would have overstated how flat the
repair actually is; the decisive comparison is barely-to-moderately flatter
than `g3_raw_scale`'s own inverted-U, not dramatically so.

### Lean (b) — NO LOSS: winning arm's recovery at c=1 not worse than `g3_raw_scale`'s (disclosed companion; officially unreached since lean (a) never HOLDS)

**MISS, decisively, for both arms — reported as a non-gating companion per
the registration ("that arm's recovery," referring to an arm lean (a)
selects; none was selected here), computed anyway because it costs zero
marginal compute and confirms the pre-registered mechanistic prediction
directly:**

| arm | budget | mean diff (candidate − `g3_raw_scale`) | 95% author CI | class |
|---|---|---|---|---|
| `covariant_var` | 4x | +0.0534 | [0.0417, 0.0651] | OUTSIDE (worse) |
| `covariant_var` | 8x | +0.0628 | [0.0506, 0.0750] | OUTSIDE (worse) |
| `covariant_msq` | 4x | +0.0536 | [0.0419, 0.0653] | OUTSIDE (worse) |
| `covariant_msq` | 8x | +0.0630 | [0.0508, 0.0752] | OUTSIDE (worse) |

The candidate arms' c=1 error is **worse** than `g3_raw_scale`'s by
0.053–0.063 — roughly the *entire* size of M4-G3's own persisted c=4 gain
(0.059/0.068). This is exactly the pre-registered mechanism: calibrating
alpha to reproduce `hazard_ridge_deployed` at c=1 pins the covariant arms to
baseline's own (weaker-regularization-free but not better-fitting) c=1
level, not `g3_raw_scale`'s deliberately-weakened one. **Had lean (a) HELD
for either arm, lean (b) would still have MISSED.**

### Lean (c) — SPECIFICITY: the same covariant rule on an M4-G3-inert constant does not produce c-invariance

**CONFIRMED, decisively — all six checks OUTSIDE the margin, at BOTH
budgets, with room to spare:**

| budget | c-pair | mean diff | 95% author CI | class |
|---|---|---|---|---|
| 4x | 0.25 vs 1.0 | +0.2300 | [0.2186, 0.2414] | **OUTSIDE** |
| 4x | 0.25 vs 4.0 | +0.2892 | [0.2707, 0.3078] | **OUTSIDE** |
| 4x | 1.0 vs 4.0 | +0.0592 | [0.0480, 0.0703] | **OUTSIDE** |
| 8x | 0.25 vs 1.0 | +0.2326 | [0.2212, 0.2440] | **OUTSIDE** |
| 8x | 0.25 vs 4.0 | +0.3010 | [0.2820, 0.3199] | **OUTSIDE** |
| 8x | 1.0 vs 4.0 | +0.0684 | [0.0568, 0.0800] | **OUTSIDE** |

`specificity_weight_floor`'s own non-invariance is **3.2–17.4× larger**
(smallest ratio on the 1.0-vs-4.0 pair, largest on 0.25-vs-1.0, both budgets)
than `covariant_var`/`msq`'s on the same c-pairs, decisively confirming that
touching `weight_floor` (already known INERT for truth recovery from M4-G3)
does nothing to fix the c-dependence — the reduction the ridge-covariant
arms achieve is specific to `hazard_ridge`, not a generic side-effect of
"making some constant vary with c." **A striking, unregistered-but-load-bearing
cross-check**: `specificity_weight_floor`'s own 1.0-vs-4.0 diff (0.0592 @4x,
0.0684 @8x) matches M4-G3's own persisted author-level c=4 gain (0.0591 @4x,
0.0683 @8x) to three decimal places — because with `hazard_ridge` untouched,
`specificity_weight_floor` mechanically reproduces `baseline`'s own c-ladder
behavior exactly (its c=1 value already matched `baseline`'s bit-for-bit,
see the summary table), and `baseline`'s own c=1-to-c=4 move *is* M4-G3's c=4
gain. This is an emergent, structural confirmation that both legs' machinery
is measuring the same quantity, not a coincidence.

### Pivot — no covariant candidate achieves c-invariance

**FIRES.** Both `covariant_var` and `covariant_msq` are clean MISSes — not
underpowered, on a comparison whose half-width (0.0056) is still comfortably
under the 0.01 power bar even though it is the least precise of the three
pairs tested for these arms. Per the registration: **the dependence is not a
simple ridge-scaling issue, M4-G3's
localization is incomplete, and the redesign target moves to the objective's
FUNCTIONAL FORM.**

## Verdict

**Stated plainly, per the outer task's own instruction: the PIVOT fires, and
the localization is real but incomplete — this is delivered cleanly, which
is the one thing M4-G3's own underpowered pivot could not do.**

1. **M4-G3's finding that `hazard_ridge` is the dominant localized channel
   of M4-G2's scale dependence is not overturned — it is *sharpened*.** A
   ridge keyed to a genuinely covariant post-whitening statistic (verified
   LIVE at exactly the theoretical 16.0/0.0625 ratios, in contrast to
   `g3_raw_scale`'s own exactly-1.0 ratio) removes **89.1%** of the raw
   c=0.25-to-c=4.0 swing, well-powered (half-width 0.0056, comfortably inside
   the 0.01 bar) at both budgets. Touching an M4-G3-inert constant with the
   identical mechanical rule removes **0%** of that swing (if anything,
   `specificity_weight_floor` is a hair *more* variable than `baseline`
   itself, and its own swings on the same pairs are 3.2–17.4× larger than
   the ridge-covariant arms'). `hazard_ridge` is confirmed, again, as the
   dominant, specific channel.
2. **But no tested functional form — `ridge = alpha · POST_SCALE_VAR(c)` or
   `ridge = alpha · POST_SCALE_MSQ(c)`, either one — is CERTIFIED as a
   general repair.** The residual 10.9% is not noise: on the pair that
   decides it (c=0.25 vs c=4.0), the CI clears the registered ±0.02 margin by
   30–36% of the margin's own width (both arms, both budgets), at n=745, with
   a half-width (0.0056) barely over half the 0.01 power bar — a decisive, not
   marginal, MISS. **What this means concretely, following the two limits
   registered in Part 0 before compute:** (i) the alpha calibration is
   global, not per-context, so some residual is contributed
   by cross-context variation in `POST_SCALE_k(context, 1)` around its
   population mean (disclosed as unavoidable under the adopted, and
   necessary-for-testing-two-candidates, calibration reading); (ii) more
   importantly, **the `return`/`feedback`/`gate` routes' own design columns
   mix c-scaled blocks (built from `basis`, which does satisfy identity (*))
   with c-invariant blocks (`generated_current`/`duration`, raw world data;
   and the `feedback_0_d`/`gate_0_d` sub-block, which crosses the *unscaled*
   intercept column with `response_next`)** — no single scalar ridge,
   however cleverly keyed to the *whitened design's own scale*, can
   compensate a diagonal rescale that only touches *part* of the design.
   This is not a new finding invented after seeing the MISS: it was the
   specific, disclosed reason lean (a) was registered as an "open empirical
   question" rather than a foregone conclusion in Part 0, before compute.
3. **The redesign target moves to the objective's FUNCTIONAL FORM.** Per the
   registration's own consequence for a firing pivot: the next leg in this
   line, if pursued, should not test a third `ridge = alpha · stat`
   candidate (a variant of the same functional form already shown
   insufficient) but should instead examine whether the *mixed* column
   structure itself — specifically, whether `generated_current`/`duration`/
   `feedback_0_d`/`gate_0_d` should themselves be whitened, rescaled, or
   separately regularized — is the load-bearing remainder. This leg's own
   G2 evidence (exact 16.0/0.0625 ratios on the *ridge*, yet only 89.1%
   of the raw swing removed on *recovery*) is direct, quantitative
   confirmation that the gap lives downstream of the ridge's own value, in
   how the design is assembled from the basis.

Consequence for the line: M4-G2's original hypothesis — that the scale
dependence is a scaling problem fixable by a single relative constant — is
**substantially, quantitatively refuted as a *complete* account** (a single
ridge closes at most 89% of it) while being **confirmed as the *dominant*
partial account** (nothing else tested, including a mechanically-identical
treatment of an inert constant, closes any of it). Both halves are true
simultaneously and are reported together, as M4-G3's own outcome format
anticipated for a result that does not fit one branch cleanly — except this
time the branch it lands in (PIVOT FIRES, cleanly) is itself one of the two
registered branches, not a third "outside every branch" outcome.

## Honest anomalies and disclosures

- **A mechanical bug was caught and fixed at assembly time, before any
  hypothesis-relevant number from this leg's own truth-recovery data had
  been read.** An earlier draft of the G1 ANCHOR block attempted to
  independently re-verify `g3_raw_scale`'s c=0.25/4.0 values against M4-G3's
  own persisted winner-ladder files via a join — but `g3_raw_scale` is, by
  this leg's own registered, disclosed compute-scope reduction (Part 0,
  Design), never computed away from c=1 in this leg's new compute (only
  `covariant_var`/`covariant_msq`/`specificity_weight_floor` are swept
  across the full c-ladder). The join therefore correctly found 0 matching
  rows and raised `RuntimeError` — a **correct** consequence of the scope
  reduction, not a data or compute error, caught by the very
  `expected != len(joined)` assertion the anchor block itself carries. Fixed
  by removing the invalid 0.25/4.0 anchor attempt and disclosing plainly
  that `g3_raw_scale`'s c=0.25/4.0 descriptive-table values are read
  directly from M4-G3's own already-gated files, unverified by this leg at
  those two points (the c=1.0 anchor — the only point this leg newly
  computes for that arm — remains independently verified at exactly 0.0).
  This was caught by re-running `--assemble` after the truth-stage compute
  for all 8 worlds had already completed and persisted; it affected no
  truth-recovery row, no lean, and no gate — only the G1 anchor's own
  bookkeeping for one non-adjudicating descriptive-table arm.
- **`covariant_var` and `covariant_msq` are numerically almost
  indistinguishable throughout** (differ in the 3rd–4th decimal of both
  `e_arm_true` and the realized ridge value). This was registered as an
  open empirical question in Part 0 (S1/S2 "can genuinely differ" if a
  role's raw features are not zero-mean relative to `center`) — the finding
  is that, empirically, they are close enough not to matter for this leg's
  worlds. Reported as a real result, not a bug: both statistics were
  computed independently, from independent code paths, and agree.
- **`condition_alias_ecology`'s single-world data (used only as a pre-pooling
  qualitative sanity check, never for adjudication) showed a *flatter*
  c=0.25-to-c=4.0 swing (≈0.019) than the pooled 6-world figure (0.0316) —
  a reminder, disclosed here, that a single world's point estimate is not
  representative of the pooled, adjudicating statistic**, exactly the
  reason the registration specifies the author grain (pooled across worlds)
  as decisive rather than any one world's own numbers.
- **Compute cost**: calibration stage (all 8 worlds, no IRLS fit): 4m35s
  single foreground pass. Truth stage: one solo timing run
  (`condition_alias_ecology`, 12m40s) established the per-world cost before
  any parallelism; the remaining 7 worlds were then run in overlapping
  batches (4 concurrent, then a 5th added mid-batch once slots freed, then
  the final 2 added once more slots freed — up to 6 concurrent processes
  against 10 available cores at points), driven in the foreground in
  explicit chunks per this arc's standard workaround; total wall-clock for
  all 8 worlds' truth-stage compute ≈ 42 minutes (12:46 first calibration
  start to 13:28 last world done), no single Bash invocation left
  unsupervised for longer than its own explicit polling loop. `--assemble`
  itself: a few seconds (excluding the one caught-and-fixed bug's re-run).
  No world showed a Traceback, RuntimeError, or Killed signal in its log at
  any point.

## Faithfulness chain (all green)

| gate | value |
|---|---|
| G1 anchor: `baseline`@c=1 vs M4-G3 persisted (4,096 rows) | **0.0** |
| G1 anchor: `g3_raw_scale`@c=1 vs M4-G3 persisted (4,096 rows) | **0.0** |
| G2: realized ridge/floor ratio vs c, all 3 manipulated arms | **exactly 16.0 / 0.0625** (vs theoretical 16.0/0.0625) |
| G2: `g3_raw_scale`'s own ridge ratio vs c | **exactly 1.0** (M4-G3's own c-invariance flaw, reproduced) |
| G3 truth-path invariance (88 checks: 11 (arm,c) combos × 8 worlds) | **0.0** |
| row-count completeness (truth: 45,056 = Σ_c 8 worlds×2 budgets×8 reps×2 views×16 authors×n_arms(c); author: 17,754) | exact match, every partial |
| valid-6-world subset, recomputed from this leg's own arm-invariant `e_orc_true` | reproduces M4-G2/M4-G3's own adopted set exactly |
| `specificity_weight_floor`@c=1 vs `baseline`@c=1 (structural, ridge/floor's only-difference check) | **0.0**, both budgets |
| `specificity_weight_floor`'s own 1.0-vs-4.0 diff vs M4-G3's persisted author-level c=4 gain | 0.0592 vs 0.0591 (@4x), 0.0684 vs 0.0683 (@8x) — emergent cross-leg agreement, not a registered gate |

## Boundaries

Finite synthetic M4-C.2 worlds only. 8 D1 worlds (reused verbatim from
M4-G2/M4-G3); truth-recovery statistics restricted to M4-G2's own valid
6-world subset (excludes `linear_null_ecology`, `fast_return_equal_marginal`
— the pre-existing `_relative_error` near-zero-denominator fragility,
unrelated to any manipulation in this leg, reused verbatim rather than
re-derived). Truth-referenced recovery via budget-regenerated (4x/8x events)
finite panels from the frozen world law, compared to the analytic `D_true`,
exactly M4-G1/G2/G3's own construction, reused unchanged. No natural-text,
personality, or clinical claim; no seal, no independent verification
(operator directive 2026-08-01). This leg answers the question M4-G3's
planner adjudication note posed (does a ridge keyed to a genuinely
covariant, post-whitening statistic deliver c-invariant recovery without
losing the gain); it does not re-open M4-G1's, M4-G2's, or M4-G3's own
leans, and it does not test any functional-form repair beyond the two
ridge-statistic candidates and the one specificity control registered in
Part 0. **The open question for any future leg in this line, now that the
PIVOT has fired cleanly: whether the residual, structural, mixed-column-type
mismatch identified in the Verdict above (c-scaled `condition_*`/
`feedback_*`-via-whitened-basis blocks vs. c-invariant `generated_current`/
`duration`/`feedback_0_d`/`gate_0_d` blocks) can be closed by a
column-type-aware treatment of the hazard design itself — a genuinely
different functional-form question, not a fourth ridge-statistic variant of
the same family this leg and M4-G3 together have now closed out.**
