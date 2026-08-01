# SUICA M4-D Leg 4 — D-Leg Floor: Lambda-Grid Extension and Resolution Scaling

Date: 2026-08-01
Tier: EXPLORATORY (open-exploration phase; operator directive 2026-08-01:
defensive machinery deferred; design, leans, and the 4b fork registered in
`docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md` ("Leg 4") before this
run; no prospective seal, no independent verification pass)

## Decision

```text
M4_D_LEG4_LAMBDA_INTERIOR_ROUTE_STABILIZATION_SATURATES_BELOW_GATE_AND_DLEG_FLOOR_IS_RESOLUTION_LIMIT
```

Two results, one battery. **4a:** the registered selection-rule change works
exactly as intended — route-identification accuracy is non-monotone in lambda
and selects INTERIOR lambda = .125 (Leg 3's boundary-bind was the likelihood
criterion, not the ridge mechanism; the mechanism is NOT saturated). At .125
the battery flip count collapses 196 -> 73 and lean (a4a) HOLDS with room
(73 <= 120), but pooled loop geometry reaches only .6901 and lean (b4a)
MISSES by .0099 — and the near-miss is not innocent: the ridge buys route
stability by DISTORTING the creation estimator itself (battery median e_d
.487 -> .783, pooled creation geometry .774 -> .580, non-flip loops worse in
76.7% of rows). Halving the remaining flips relative to Leg 3 (148 -> 73)
bought +.0015 pooled geometry — an independent confirmation that the flip
channel is exhausted and the third layer (D-leg estimation at the correct
route) dominates the wall. **4b:** the registered fork adjudicates
RESOLUTION_LIMIT, unanimously — 5/5 worlds and the pool are STRUCTURAL_FLOOR
on both the primary (paired) and truth-referenced metrics. Pooled median
e_d at the oracle-forced route moves .459 / .418 / .391 / .389 across
{0.5x, 1x, 2x, 4x}; the overall log-log slope is -.081 (nowhere near the
-1/2 estimator-noise signature), the tail slope is -.051, and the power-law
extrapolation says e_d <= .25 would cost ~721x the V2 event budget pooled
(4.0e3x–5.5e6x in the four failing worlds; ~2.7e15x against the generative
law). More events do not buy creation-derivative resolution here; the
closing sections state what does and does not grow with events, and the
exploratory reading of why.

## Registered design and leans (verbatim intent from the plan)

- **4a** — extend the arm-2 ridge grid to {.005, .025, .125, .625, 3.125};
  select lambda by out-of-fold ROUTE-IDENTIFICATION ACCURACY on discovery
  reps {0, 1} (registered change from Leg 3's OOF-likelihood rule, which was
  monotone and bound at the boundary); rerun the full 5-world x 8-rep
  battery at the selected lambda. Leans: (a4a) total flips <= 120;
  (b4a) pooled loop geometry >= .70. Soft outcome: if route-accuracy
  selection also binds at a boundary, report the lambda-response curve and
  declare the mechanism saturated.
- **4b** — at the oracle-forced route (no selection anywhere), re-estimate
  the creation derivative D at event budgets {0.5x, 1x, 2x, 4x} of the V2
  default and fit log(median e_d) vs log(budget). Fork: slope consistent
  with -1/2 (in [-.65, -.35], plateau test failing) => ESTIMATOR/BUDGET-
  LIMITED, report projected budget to e_d <= .25; plateau by 2x
  (|tail slope| < .15) => STRUCTURAL RESOLUTION LIMIT, state the floor per
  world in T4-economics style. Mixed outcomes across worlds allowed. No
  kill (mapping experiment).

Pre-coded operationalizations (stated in the script header before the run):
lambda picked by fewest discovery D-zero flips (Leg 1's flip definition),
ties by fewer route-name mismatches then smaller lambda; 4b primary metric
e_d_paired = ||D_disc(b) - D_orc(b)|| / ||D_orc(b)|| (both legs refit at
budget b at the forced route; coincides with the program-standard e_d at
1x), companions e_d_true / e_orc_true (analytic generator-law derivative at
the estimator's own probe) and e_d_frozen; plateau bar |tail slope| < .15
over {1x, 2x, 4x}; verdict BUDGET_LIMITED only if overall slope in
[-.65, -.35] without plateau.

## Machinery and faithfulness

Bit-exact reuse: the V2 replay and arm-2 ridge machinery are IMPORTED from
`scripts/run_suica_m4_d_overspan_control_leg3.py` (nothing reimplemented).
Battery: 5 creation-active loop worlds x 8 repetitions x 16 authors x
{train, test}, seed rule and config identical to V2/Leg 1/Leg 3.

| gate | value |
| --- | ---: |
| arm-0 geometries vs archived `metrics.csv` (per world-rep, before treatment) | **1.11e-16** |
| arm-0 per-row e_loop / e_d vs Leg 1 `per_loop_metrics.csv` (1,280 rows) | **2.22e-16** |
| arm-0 per-row vs Leg 3 persisted rows (1,280 rows, flags equal) | **2.22e-16** |
| discovery arm-2 @ lambda=.005 vs Leg 3 persisted arm-2 rows (320 rows, flags equal) | **8.33e-17** |
| arm-0 flips / pooled loop geometry | **196** / **.6519** (exact) |
| 4b oracle-side refit at 1x vs oracle-stack D (all nondegenerate rows) | **0.0** (bit-exact) |
| 4b forced discovered refit at 1x vs arm-0 D (781 route-matching rows) | **0.0** (bit-exact) |
| analytic D_true vs `_feedback_derivative` on exact generator coefficients | **1.67e-15** |

## Part 4a — lambda-response curve and the interior selection

Discovery evaluation (reps {0, 1} x 5 worlds x 32 author-views = 320 rows
per lambda; route-identification accuracy = 1 - flip rate vs oracle route):

| lambda | discovery flips | route-id accuracy | name mismatches | mean discovery loop geometry | median discovery e_d |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.005 | 38 | .881 | 120 | .633 | .482 |
| 0.025 | 27 | .916 | 114 | **.693** | .573 |
| **0.125** | **21** | **.934** | 112 | .650 | .791 |
| 0.625 | 26 | .919 | 106 | .563 | .931 |
| 3.125 | 58 | .819 | 124 | .519 | .983 |

The curve is non-monotone with an interior optimum: **lambda* = .125**, not
a boundary. Leg 3's binding constraint was therefore the LIKELIHOOD rule,
not the ridge mechanism — the registered rule change closes that question,
and the unregistered lambda=.125 smoke lead from Leg 3 is now licensed and
confirmed. The registered saturation declaration does NOT fire. Two honest
reads of the same table: (i) route-name accuracy barely moves (.61–.67
across the grid; battery mismatches 489 -> 474) — the ridge fixes D-ZERO
flips, not name-level route identity (feedback-vs-gate confusions share a
nonzero D leg and never count as flips); (ii) discovery loop geometry peaks
at .025, one grid point BELOW the flip optimum — the registered rule
optimizes route identification and pays elsewhere, which is exactly what
the battery shows next.

## Part 4a — battery at lambda* = .125 and lean adjudication

| arm | flips | pooled loop geometry | worlds >= .75 | pooled creation geometry | median e_d | median e_loop | non-flip mean e_loop |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| arm0_v2 | 196 | .6519 | 1/5 | .7736 | .4869 | .7128 | .6565 |
| arm2_penalized @ .125 | **73** | **.6901** | 2/5 | **.5800** | **.7830** | .8224 | .8069 |

Flips by world: 53 -> 21 (partition), 72 -> 20 (expansion), 38 -> 16
(rotated), 5 -> 2 (gated), 28 -> 14 (compensation); 141 fixed, 18 newly
broken. Per-world loop geometry: partition .577 -> .598, expansion
.516 -> .720, rotated .684 -> .763, gated .915 -> **.753**, compensation
.567 -> .617.

- **Lean (a4a) — HOLD.** 73 <= 120 (196 -> 73, -62.8%; nearly the "halving"
  Leg 3's lean (a) wanted, twice over).
- **Lean (b4a) — MISS by .0099.** Pooled .6901 < .70. Context: Leg 3's
  lambda=.005 arm scored 148 flips / .6886 — cutting the remaining flips in
  half again bought **+.0015** pooled geometry.

**Disclosed trade-off (the substantive 4a finding): the ridge buys route
stability by distorting the creation estimator itself.**

- Battery median e_d rises .487 -> **.783**; pooled creation-action
  geometry falls .774 -> **.580** (gated .969 -> .670, compensation
  .765 -> .429, rotated .706 -> .472).
- On rows that are non-flip under BOTH arms, median e_loop worsens
  .617 -> .811 (median e_d .414 -> .772) and 76.7% of those rows get worse.
- The 141 un-flipped rows land at median e_loop **.839** (Leg 3 @ .005:
  .78) — route recovery without a usable D estimate, again.
- The one world that passed the V2 gate (gated, .915) is DAMAGED to .753 —
  the treatment that rescues failing worlds' selection erodes the passing
  world's derivative.

Flip elimination alone still lifts the pooled statistic (flips force
e_loop = 1 rows), which is why geometry rises at all; but the bulk error
underneath moves the WRONG way. Route stabilization via feedback shrinkage
is now saturated below the gate: at the flip-optimal lambda the geometry
lean still misses, independently confirming Leg 3's third-layer conclusion
that D-LEG ESTIMATION AT THE CORRECT ROUTE, not selection, is the wall.

## Part 4b — design actually run

Budgets {0.5x, 1x, 2x, 4x} = events {60, 120, 240, 480} per occasion (the
generator parameterizes event count as `spec.events`; 4x is possible, so
the registered fallback grid was not needed). Frozen world semantics:
condition panels, mechanism parameters, and the oracle basis are
bit-identical across budgets (asserted per budget); the chart and both
bases stay frozen at their V2 (1x) estimates; the generator consumes RNG
per event, so non-1x panels are fresh path realizations of the identical
law, while 1x reuses the exact battery panels. Route forced per author-view
to the oracle stack's V2-selected model on both sides; no selection
anywhere; V2 estimator semantics unchanged (no extra ridge in 4b).
48 / 5,120 rows (36 partition, 8 gated, 4 compensation) have a D-zero
forced route (oracle picked base/return) and are excluded as
degenerate-reference rows.

## Part 4b — scaling table and the fork verdict

Primary e_d_paired, author-level medians per budget, log-log slopes:

| world | 0.5x | 1x | 2x | 4x | overall slope | tail slope | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| endogenous_creation_expansion | .536 | .495 | .475 | .456 | -.076 | -.060 | STRUCTURAL_FLOOR |
| endogenous_source_partition_matched | .577 | .520 | .499 | .474 | -.091 | -.067 | STRUCTURAL_FLOOR |
| history_gated_ecology | .159 | .151 | .143 | .138 | -.071 | -.066 | STRUCTURAL_FLOOR |
| selection_creation_compensation | .483 | .459 | .447 | .445 | -.040 | -.023 | STRUCTURAL_FLOOR |
| source_rotated_feedback | .495 | .466 | .461 | .442 | -.051 | -.039 | STRUCTURAL_FLOOR |
| **POOLED** | **.459** | **.418** | **.391** | **.389** | **-.081** | **-.051** | **STRUCTURAL_FLOOR** |

Truth-referenced companion e_d_true (pooled): .613 / .592 / .589 / .580,
overall slope -.025, tail -.015 — STRUCTURAL_FLOOR in all 5 worlds there
too. **The fork verdict is RESOLUTION_LIMIT, unanimous on both metrics**
(no mixed outcome). Every slope is an order of magnitude away from the
-1/2 estimator-noise band [-.65, -.35]; the 2x -> 4x pooled segment is
-.005 — flat.

Projected budget multiples to reach e_d <= .25 (power-law extrapolation,
reported for completeness even though the verdict is not budget-limited):
pooled **721x**; expansion 1.0e4x, partition 4.0e3x, compensation 5.5e6x,
rotated 2.6e5x. Against the generative law (e_d_true): ~2.7e15x pooled.
history_gated_ecology is ALREADY below the target at every budget
(.138–.159) — its floor is flat but sits under .25, consistent with it
being the one world that passes the loop gate; the four failing worlds
floor at .442–.474.

## The resolution-limit statement (T4-economics style)

**What grows with events:** route identification (4a: flips 196 -> 73 at
fixed data via regularization; and within 4b the first doubling of data
still buys a little paired agreement, .459 -> .418). **What does not grow:**
the creation derivative's resolution at the correct route. From 1x to 4x
the pooled paired error moves .418 -> .389 (tail slope -.051, final segment
-.005); the oracle frame's own distance from the generative law is
budget-flat (.376 -> .373 pooled, tail -.005); and the fitted D wobbles
.16–.26 (median relative drift) between fresh realizations of the SAME law
even in the oracle frame at 2x–4x budgets. At this observation design the
creation derivative is resolution-limited at ~.39 pooled (per-world floors
.138 gated / .442–.474 elsewhere), and the projected cost of buying the .25
target with events alone (721x pooled, >= 4.0e3x per failing world) is not
a budget any design would pay. The M4-C.3.x creation-estimator wall is a
RESOLUTION LIMIT of this estimator-plus-observation-design, not a resource
shortfall.

**Exploratory reading of why (companion-curve decomposition, stated as
interpretation, not a sealed claim):** at 4x the discovered-side estimator
(.389 pooled) sits essentially AT the oracle frame's own error scale
against the law (e_orc_true .367–.373), while the oracle-frame fit's
distance from the law never decays with budget. Two mechanisms in the
numbers: (i) the V2 hazard ridge scales its penalty with sample size
(penalty = ridge x n x I), so the shrinkage fraction is budget-invariant by
design — a non-vanishing regularization bias; (ii) the fitted D is a
high-variance PER-REALIZATION object — oracle-frame refits on fresh
realizations of the identical law drift .16–.26 in relative norm. The
floor, on this reading, is not "estimator failure on too little data": it
is the realization-to-realization variance of the creation derivative plus
fixed regularization/misspecification bias under this observation design.
Only design changes can plausibly move it — richer per-event excitation
(the C3.3 information-frontier lead), paired or interventional occasions,
or a de-biased derivative estimator — not more events of the same kind.

## Honest anomalies and caveats

- **Partition-world truth reference is level-offset.** The generator masks
  `generated_next` by the envelope in `endogenous_source_partition_matched`,
  so the analytic latent-law derivative overstates the OBSERVABLE hazard
  derivative there: its reference gap is .645 vs .270–.389 in the other
  worlds, and its e_d_true floor (.716) carries that offset. e_*_true
  LEVELS are therefore not comparable across worlds (slopes still are);
  the primary paired metric is unaffected (both sides fit the same
  observable process).
- **The frozen-reference curve shows why it is not the primary:**
  e_d_frozen dips at 1x (.418) then bounces (.445 at 2x) — only the 1x
  panels share the realization with the frozen reference, so realization
  wobble (~.17–.26) enters at every other budget. Persisted for
  completeness.
- **Discovery loop geometry peaks at lambda=.025**, one grid point below
  the flip-optimal .125 (.693 vs .650). A geometry-based selection rule
  would have chosen differently; only the registered route-accuracy rule
  was licensed, and its battery outcome is reported as adjudicated. No
  battery run at .025 exists (not licensed here).
- The discovery pre-pass consumes reps {0, 1}, which remain in the
  evaluation battery (same disclosure as Leg 3; registration fixed the
  battery to the exact V2 40 world-reps).
- 4b's non-1x panels are fresh realizations, not extensions of the 1x
  paths (the generator consumes RNG per event); budgets are therefore
  compared law-to-law, not path-to-path, and the paired metric absorbs the
  shared realization at each budget.
- e_loop can exceed 1 where a zero-D route is replaced by a badly oriented
  nonzero D; medians quoted alongside means where it matters.

## Scope and claim boundary

Finite synthetic M4-C.2 worlds only. Truth-referenced estimator
diagnostics throughout (oracle-basis fits and generator-law derivatives
are consumed as references), so nothing here is an operational rescue of
chart transport, a repaired gate, or a reopening of the V1/V2 NO-GO
decisions, which stand unchanged. The 4b curves map the resolution
economics of the V2 creation-derivative estimator at the correct route;
they license no deployable estimator. No natural-text, personality,
emotion, diagnosis, or clinical claim. EXPLORATORY tier; nothing here may
be cited above it.

## Artifacts

- script: `scripts/run_suica_m4_d_dleg_floor_leg4.py`
- adjudication: `results/m4_d_dleg_floor/decision.json`
- battery rows (2,560 = 2 arms x 1,280): `results/m4_d_dleg_floor/per_loop_metrics.csv`
- world-rep rows (80): `results/m4_d_dleg_floor/world_rep_metrics.csv`
- arm-0 faithfulness: `results/m4_d_dleg_floor/v2_validation.csv`
- lambda discovery rows (1,600 = 5 lambdas x 320): `results/m4_d_dleg_floor/lambda_discovery_rows.csv`
- lambda-response curve (50 world-rep cells): `results/m4_d_dleg_floor/lambda_response_curve.csv`
- 4b budget rows (5,120): `results/m4_d_dleg_floor/dleg_budget_rows.csv`
- 4b scaling summary: `results/m4_d_dleg_floor/dleg_scaling_summary.csv`
