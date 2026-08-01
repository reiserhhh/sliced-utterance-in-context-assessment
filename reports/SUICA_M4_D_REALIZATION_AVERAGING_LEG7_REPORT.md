# SUICA M4-D Leg 7 — Realization Averaging: the R^(-1/2) Test Fails, the Interpretation Dies

Date: 2026-08-02
Tier: EXPLORATORY (open-exploration phase; operator directive 2026-08-01:
defensive machinery deferred; design and leans registered in
`docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md` ("Leg 7",
2026-08-02 loop cycle 2, commit 79d35e6) before this run; no prospective
seal, no independent verification pass)

## Decision

```text
PIVOT_PER_REALIZATION_VARIANCE_INTERPRETATION_DIES_
NEXT_ORACLE_VS_ESTIMATOR_BIAS_DECOMPOSITION
```

**The registered pivot fires, and the Leg-4b interpretation is dead.**
Averaging D estimates across R ∈ {1, 2, 4, 8} independent realizations of
the identical law moves the pooled oracle-forced floor from **.4182** to
only **.3808** — a log-log slope of **−.0454**, an order of magnitude off
the registered R^(−1/2) band [−.65, −.35] and above the −.15 pivot bar.
If the floor were the creation derivative's per-realization variance,
R = 8 should have delivered ~.148; the observed floor sits **2.58×** above
that prediction, and all five worlds are individually flat (slopes −.032
to −.068). The "floor = per-realization variance" reading — the planner's
registered interpretation from the synthesis document — **is recorded as
the planner's miss, plainly: averaging independent realizations was the
one intervention that interpretation guaranteed would work, and it does
not.**

**The headline is the pivot profile.** The floor decomposes into **two
R-invariant BIAS components, not variance**: (1) a **law-level bias**
~.37 — the oracle's own refit error vs the generator law, .376 → .366
across R (slope −.013, flat), shared by both bases; (2) a
**basis-mismatch bias** ~.13 — the estimator-minus-oracle gap,
.136 → .132 (slope −.014, flat). Only a small averageable component
(~20% of the paired error's squared scale) sits on top. Cross-referenced
with Leg 6, the two components are **experimentally separable**: the
law-level term responds to excitation (e_orc_true .376 → .292, persisted)
while the paired disc-vs-oracle resolution does not (floor moved .0125),
and both are averaging-invariant here. The limit statement's
interpretation changes from VARIANCE to BIAS: averaging cannot fix it —
family enlargement / de-biasing (law-level term) and subspace alignment
(basis-mismatch term) become the next levers. The registered next
instrument — the oracle-vs-estimator bias decomposition at increasing R —
was pre-coded into this leg and is delivered below ("Pivot profile").

## Registered design and leans (verbatim intent from the plan)

- **Floor arms:** R ∈ {1, 2, 4, 8} independent path realizations per
  world-rep under the IDENTICAL law (frozen condition panels / mechanism
  parameters / oracle basis, fresh realization randomness only), event
  budget fixed at 1x (120 events) per realization. D per realization at
  the oracle-forced route (4b protocol), then realization-averaged:
  primary = simple mean of the R D-estimates; secondary = pooled joint
  fit over the R panels. `e_d_paired` of the averaged estimate, per world
  per R, persisted per row.
- **Stacking arm:** two-stage (Leg 5) + realization-averaged D at R = 4,
  full 5-world × 8-rep battery, vs Leg 5's persisted `.7605`.
- **Leans:** (a) THE CONFIRMATION TEST — pooled log-log slope of floor vs
  R in [−.65, −.35] (at R = 8, .39 → ~.14 if exact); (b) R = 8 pooled
  floor ≤ .20; (c) stacking pooled ≥ .82 with partition and compensation
  both crossing .70.
- **Pivot-if:** slope > −.15 (R-invariant floor) → the per-realization-
  variance interpretation DIES — record it as the planner's registered
  miss; next instrument = oracle-vs-estimator bias decomposition at
  increasing R.

Pre-coded operationalizations (script header, before the run): floor(R) =
pooled author-level median `e_d_paired` of the 'avg' method; slope = OLS
of log(median) on log(R) over all four R; realization mechanism = path-
panel seed offset r·1_000_000_007 under bit-asserted law identity;
realization 0 = the exact battery panels; nested realization prefixes
across the R grid (standard Monte-Carlo convergence-curve construction).

## Faithfulness chain (all gates passed)

| Gate | Result |
|---|---|
| Law identity (reassembled oracle basis, 3 roles + all 8 author-parameter arrays vs battery truth) | bit-equal on all 40 world-reps |
| Realization-0 reassembly identity (offset-0 path panels vs battery panels, 8 fields × 4 panels) | value-exact on all 40 world-reps |
| R=1 floor rows vs Leg 4 persisted `dleg_budget_rows.csv` (1x rows) | 1,280 rows, max abs diff **2.22e-16**, all flags/routes equal — asserted per world-rep BEFORE any R > 1 work |
| Pooled R=1 median vs Leg 4 persisted 1x pooled median | equal (.4181517…, < 1e-9) |
| Realization-0 fit identity (oracle refit vs oracle stack D; forced disc refit vs arm-0 D at matching routes) | 0.0 / 0.0 |
| Analytic D_true unit check vs probe machinery | 1.67e-15 |
| Stage-1 rows vs Leg 4 persisted arm-2 rows | 40 world-reps, scaled max **2.19e-16**, non-amplified strict max 2.22e-16, flips exactly 73 |
| two_stage rows vs Leg 5 persisted rows | 40 world-reps, scaled max **2.21e-16**, non-amplified strict max 4.44e-16, all flags equal |
| V2 replay validation (arm-0 geometries vs archived battery) | 1.11e-16 |
| Assembly cell audit | 10,240 averaged rows + 10,240 single rows + 3,840 stacking rows + 3×40 check rows — no missing, no duplicates |

Tolerance disclosure (in-run instrument correction, made before any
battery row was persisted): on the 12 oracle-degenerate author-views
(oracle route `base`/`return`, oracle loop exactly zero) Leg 1's `e_loop`
statistic is the 1e-12-clamped amplification ‖loop_disc‖/1e-12 ≈ 1e+11,
and one ULP of BLAS wobble (1.5e-05 absolute = **1.2e-16 relative**, on
`selection_creation_compensation` rep 0 author 13 test) reproduces in a
fresh minimal process running only context → stage 1 → two_stage — it is
float noise on the clamp, not a replay divergence (`e_d_atom` on the same
row matches to 8.3e-17; every flag and route equal). The stage-1/two_stage
row asserts therefore use |diff| ≤ 1e-9·max(1, |reference|): strict
absolute on every regular row, one-ULP-relative on the amplified rows;
both maxima are persisted per world-rep. No adjudicated statistic consumes
the amplified ratios (medians exclude oracle-degenerate rows; geometries
consume loop matrices, not clamped ratios).

## Floor vs R — pooled `e_d_paired` medians (method 'avg', primary)

| R | Observed | R^(−1/2) prediction | Segment slope |
|---|---|---|---|
| 1 | .4182 (= Leg 4b 1x, bit-exact) | .4182 | — |
| 2 | .4002 | .2957 | −.063 |
| 4 | .3869 | .2091 | −.049 |
| 8 | **.3808** | **.1478** | −.023 |

Overall log-log slope **−.0454** (registered band [−.65, −.35]; pivot bar
−.15); tail slope (R ≥ 2) −.036. The segments *decay* (−.063 → −.023):
the curve is converging to an asymptote just below .38, not following a
power law. Lean (a) **MISS** — the pivot condition (> −.15) fires
instead. Lean (b) **MISS**: .3808 > .20 (and 2.58× the R^(−1/2)
prediction).

Per world (all five individually flat — no world shows scaling):

| World | R=1 | R=2 | R=4 | R=8 | Overall slope |
|---|---|---|---|---|---|
| endogenous_creation_expansion | .4954 | .4652 | .4685 | .4593 | −.032 |
| endogenous_source_partition_matched | .5203 | .4792 | .4673 | .4681 | −.049 |
| history_gated_ecology | .1510 | .1420 | .1346 | .1314 | −.068 |
| selection_creation_compensation | .4590 | .4339 | .4267 | .4287 | −.032 |
| source_rotated_feedback | .4664 | .4662 | .4427 | .4358 | −.037 |

R=1 values coincide bit-exactly with Leg 4b's persisted 1x medians (the
registered reproduce-first requirement). Single-realization medians are
exchangeable across realizations (.4143–.4231 over the 8 draws, battery
realization .4182 inside the band) — no realization-mechanism artifact.

## Averaged vs joint (primary vs secondary construction)

| R | 'avg' (mean of D's) | 'joint' (pooled fit) |
|---|---|---|
| 1 | .4182 | .4182 (identical by construction) |
| 2 | .4002 | .3991 |
| 4 | .3869 | .3876 |
| 8 | .3808 | .3809 |

Maximum pooled-median difference **.0011**; joint overall slope −.0446.
The two constructions agree everywhere — the flatness is a property of
the object, not of the averaging method. (The joint fit also refutes a
"nonlinearity of the mean" objection: pooling the raw panels into one
likelihood gives the same floor as averaging the derivatives.)

## Pivot profile — the oracle-vs-estimator decomposition (pre-coded)

The registered pivot names the next instrument: decompose oracle-vs-
estimator at increasing R. It was computed in this leg for all cases:

| Quantity (pooled medians) | R=1 | R=2 | R=4 | R=8 | Slope |
|---|---|---|---|---|---|
| `e_orc_true` (oracle's own refit error vs the law) | .3756 | .3733 | .3681 | .3662 | **−.013** |
| `e_d_true` (discovered refit error vs the law) | .5923 | .5828 | .5842 | .5790 | −.009 |
| disc excess (`e_d_true` − `e_orc_true`, author-level) | .1364 | .1339 | .1338 | .1321 | **−.014** |
| `e_d_paired` (disc vs orc, the floor) | .4182 | .4002 | .3869 | .3808 | −.045 |

Answers to the two registered questions: **the ORACLE's own refit error
also stays flat** (−.013 — averaging 8 independent realizations moves it
.3756 → .3662), and **the estimator-minus-oracle gap does not close**
(.1364 → .1321). So the floor is not the estimator family's noise and not
realization scatter on either side: the oracle-basis fit converges, under
unlimited independent realizations of this observation design, to a point
~.37 away from the generator-law derivative (law-level regularization/
misspecification bias — the V2 hazard ridge scales with n and the
shrinkage never decays, as Leg 4b's report already noted for budgets),
and the discovered basis adds a stable ~.13 projection offset
(basis-mismatch bias). **This is a world/design-level identifiability
statement, not an estimator-variance statement.**

**Cross-reference to Leg 6 — the two bias sources are experimentally
separable.** Under per-event excitation (Leg 6, persisted statistics),
the LAW-LEVEL component responds: `e_orc_true` fell .376 → .292 at 1x
(excitation buys law information on the oracle's own leg; `e_d_true`
.592 → .552 likewise), yet the paired disc-vs-oracle floor — the
statistic the basis-mismatch displacement bounds — moved only .0125.
Under realization averaging (this leg) BOTH components are flat. The
factorial picture across the two legs: the law-level bias is
excitation-responsive and averaging-invariant; the basis-mismatch
displacement is invariant to both. The levers therefore split by
component — **family enlargement / de-biasing** (richer hazard model
family or vanishing-ridge derivative estimators) attacks the law-level
term, **subspace alignment** (span-matching beyond rank-matching, Leg 3's
disclosed lead) attacks the basis term. Averaging attacks neither.

Implied-scale arithmetic (heuristic footnote, treating pooled medians as
RMS-like scales, e(R)² = b² + σ²/R): paired error → bias b ≈ .375,
per-realization σ ≈ .185 (variance share **19.5%**); oracle-vs-truth →
b ≈ .365, σ ≈ .089 (share 5.7%); disc-vs-truth → b ≈ .577, σ ≈ .133
(share 5.1%). The bias term dominates everywhere.

**Where Leg 4b's reading went wrong (the sharp part):** the per-
realization oracle DRIFT that motivated the interpretation is real —
median `orc_self_drift` across fresh realizations is **.208** (IQR
.158–.273), squarely reproducing the .16–.26 range Leg 4b cited. But the
drift is **common-mode**: within a realization the discovered and oracle
legs fit the same panels and wobble together, so the paired displacement
that bounds loop transport is nearly constant across realizations. Leg 4b
read a common-mode wobble as if it were the pair's variance. Averaging
kills the wobble (σ ≈ .185 component) and leaves the displacement
(b ≈ .375) — which is the floor.

## Stacking — two-stage + realization-averaged D at R = 4

| Arm | Flips | Median e_d | Pooled loop geometry | Worlds ≥ .75 |
|---|---|---|---|---|
| arm2_stage1_125 (recomputed = Leg 4a) | 73 | .7830 | .6901 | 2 |
| two_stage (recomputed = Leg 5, asserted) | 73 | .4481 | .7605 | 3 |
| **two_stage_ravg_r4** | 73 | .4457 | **.7583** | 3 |

Per-world vs Leg 5's persisted two_stage values (gain = ravg − Leg 5):

| World | Leg 5 | ravg R=4 | Gain |
|---|---|---|---|
| endogenous_creation_expansion | .7894 | .7818 | −.0076 |
| endogenous_source_partition_matched | .6527 | .6534 | +.0007 |
| history_gated_ecology | .9479 | .9469 | −.0010 |
| selection_creation_compensation | .6209 | .6175 | −.0035 |
| source_rotated_feedback | .7914 | .7920 | +.0006 |

Lean (c) **MISS** on both sub-conditions: pooled .7583 < .82 (and −.0022
below Leg 5 itself — a wash), and the pinned worlds stay at .6534 / .6175,
far from .70. Realization-averaged stage-2 D buys a marginal median-e_d
improvement (.4481 → .4457) that does not translate into transport: with
the D displacement being bias, averaging four independent fits at the
same route removes only the small variance component, and the loop
statistic is insensitive at that scale. Consistent with the floor result,
not an independent failure. (Stage-2 refits: 3,840 fresh fits at
realizations 1–3; routes and flips identical to Leg 5 by construction.)

## Per-lean adjudication

| Lean | Registered | Value | Verdict |
|---|---|---|---|
| (a) | pooled log-log slope in [−.65, −.35] | −.0454 | **MISS** |
| (b) | R=8 pooled floor ≤ .20 | .3808 | **MISS** |
| (c) | stacking pooled ≥ .82, pinned worlds ≥ .70 | .7583; .6534/.6175 | **MISS** |
| Pivot | slope > −.15 → interpretation dies | −.0454 > −.15 | **FIRES** |

Verdict on the per-realization-variance interpretation: **DEAD** (0/3
leans; the pivot's own condition satisfied with an order-of-magnitude
margin). This was the planner's registered reading from the synthesis
document; its failure is the leg's headline, not a footnote.

## Honest anomalies and notes

1. **The floor does move a little** (.4182 → .3808, −.037 over 8×
   realizations; every world's R=8 median is its minimum). The
   interpretation is not "averaging does nothing"; it is "the averageable
   component is ~20% of the squared scale, and the remaining ~.375
   displacement is invariant". A hypothetical R → ∞ battery would
   asymptote near .375, still 1.5× the .25 target Leg 4b used.
2. **The Leg-4b drift evidence survives; its reading does not.** Median
   realization-to-realization drift .208 (IQR .158–.273) reproduces the
   .16–.26 claim bit-for-bit in spirit — but it is common-mode between
   the paired legs (see pivot profile). Future floor arguments must
   distinguish drift of estimates from variance of their difference.
3. **The one-ULP wobble on amplified degenerate rows** (see faithfulness
   table) forced a scale-aware tolerance on the stage-1/two_stage row
   asserts, corrected before any battery row was persisted; strict
   absolute bit-tightness holds on every row with a nonzero oracle loop.
4. Stacking at R=4 is a **wash, mildly negative pooled** (−.0022), with
   3/5 worlds slightly down — realization averaging is not a stacking
   lever at this design point, mirroring Leg 6's negative stacking
   result for excitation.
5. The gated world (never floor-pinned, R=1 .151) also declines only
   mildly under averaging (R=8 .1314, slope −.068) — the flatness is not
   a high-floor-world artifact.
6. Nested realization prefixes (R arms share lower-R realizations) were
   pre-declared; the joint-fit agreement and the exchangeability of the
   eight single-realization medians rule out prefix artifacts.

## What this leg closes and what it opens

Closed (exploratory tier): the last estimator-side reading of the D-leg
floor. After Leg 4b (budget-invariant), Leg 6 (excitation-invariant at
the C3.3 design point), and now Leg 7 (realization-averaging-invariant),
the floor's limit statement gains its strongest clause: **the ~.38–.39
paired floor is a fixed displacement — law-level fit bias (~.37, shared
by both bases; the ridge-scaling clause of Leg 4b) plus basis-mismatch
bias (~.13) — that no amount of events, excitation, or independent
realizations of this observation design can average away.** The limit
statement's interpretation changes from VARIANCE to BIAS, and the levers
split by component (see the Leg 6 cross-reference): (i) **family
enlargement / de-biasing** for the law-level term
(de-biased/unpenalized-limit derivative estimators — the ridge-vanishing
experiment the V2 design forbids by construction — or a richer hazard
family; this is the excitation-responsive component); (ii) **subspace
alignment** for the basis-mismatch term (span-matching beyond
rank-matching, Leg 3's disclosed lead; invariant to everything tested so
far); (iii) paired/interventional occasions (Leg 6's registered next
lever), which attack the law-level identifiability term rather than the
variance term. The design-change track continues with the
variance-reduction fork now pruned.

## Claim boundary

Finite synthetic M4-C.2 worlds only; truth-referenced estimator
diagnostics (oracle-basis fits, oracle-forced routes, generator-law
derivatives, and generator-privileged fresh realizations of the frozen
law are consumed as references), so nothing here is an operational rescue
of chart transport or a reopened gate; realization averaging requires R
independent draws of the same law and is not available to any
single-realization observer; the V1/V2 and C3.3 NO-GO decisions stand;
no natural-text, personality, emotion, or clinical claim; EXPLORATORY
tier under the 2026-08-01 open-exploration directive; no prospective
seal, no independent verification pass (deferred to the post-theory
defense phase).

## Artifacts

- `scripts/run_suica_m4_d_realization_averaging_leg7.py` (chunked
  foreground battery + assembly; registered leans pre-coded)
- `results/m4_d_realization_averaging/decision.json` (adjudication)
- `results/m4_d_realization_averaging/floor_avg_rows.csv` (10,240
  averaged rows: world × rep × author × view × R × {avg, joint})
- `results/m4_d_realization_averaging/floor_single_rows.csv` (10,240
  per-realization rows)
- `results/m4_d_realization_averaging/floor_scaling_summary.csv`
- `results/m4_d_realization_averaging/stacking_per_loop_metrics.csv`,
  `stacking_world_rep_metrics.csv` (3,840 + 120 rows)
- `results/m4_d_realization_averaging/r1_reproduction_check.csv`,
  `stage1_leg4_crosscheck.csv`, `two_stage_leg5_crosscheck.csv`,
  `v2_validation.csv` (faithfulness chain)
