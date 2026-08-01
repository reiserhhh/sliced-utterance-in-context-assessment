# SUICA M4-D Leg 5 — Two-Stage Route-Then-Refit: the Trade-Off Dilemma Killed by Construction

Date: 2026-08-02
Tier: EXPLORATORY (open-exploration phase; operator directive 2026-08-01:
defensive machinery deferred; design and leans registered in
`docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md` ("Leg 5",
2026-08-02) before this run; no prospective seal, no independent
verification pass)

## Decision

```text
M4_D_LEG5_ALL_LEANS_HOLD_TRADE_OFF_DILEMMA_KILLED_BY_CONSTRUCTION
```

**All three registered leans HOLD — the first full-hold leg of the M4-D
arc.** The synthesis's trade-off law said route fidelity and creation
fidelity compete at any single lambda; the two-stage construction shows
they are SEPARABLE OBJECTIVES: stage 1 buys Leg 4a's route stability
exactly (73 flips, asserted bit-tight against the persisted Leg-4 rows),
and stage 2's unpenalized refit at the stage-1-selected routes buys
creation fidelity BETTER than the V2 baseline itself (battery median e_d
.4481 vs arm0's .4869 — refitting at stabilized routes beats the baseline
D fit at sometimes-wrong routes). Pooled loop geometry lands at **.7605**,
clearing the twice-missed .70 bar by .06 rather than missing it by a hair,
with 3/5 worlds at or above the original .75 mark. The registered pivot
(construction exhausted, wall passes to design change) does NOT fire. What
the dilemma's death does not change: the remaining gap between .7605 and
1.0 sits where Leg 4b located it — the structural D-leg floor (two-stage
e_d .448 is already near the .418 achievable at the oracle-forced route at
1x and approaching the ~.39 realization-variance floor), and the two
still-failing worlds are exactly the two with the highest 4b floors. This
is a truth-referenced estimator diagnostic, not an operational rescue: the
V1/V2 NO-GO decisions still stand.

## Registered design and leans (verbatim intent from the plan)

- **Primary arm (two_stage).** STAGE 1 = Leg 4a's winning configuration
  exactly (arm-2 ridge lambda=.125 on hazard feedback/gate, route selected
  by the V2 rule over penalized candidates); flips must equal 73 by
  construction and are ASSERTED against the Leg-4 persisted rows before
  proceeding. STAGE 2 = at each author-view's stage-1-selected route,
  refit the creation derivative with the V2 BASELINE (unpenalized)
  estimator; recompute loop transport from stage-2 fits.
- **Secondary arm (single_stage_025).** Full 5-world x 8-rep battery at
  single-stage lambda=.025 (the Leg-4a discovery-loop-geometry peak; one
  grid point; licenses the discovery observation Leg 4 left unlicensed).
- **Leans:** (a) stage-2 median e_d <= .55 (from .783 under the
  flip-optimal ridge; baseline .487); (b) pooled loop geometry >= .70 —
  THE DECISIVE TEST, missed twice by ~.01 (.6886 Leg 3, .6901 Leg 4a);
  (c) worlds >= .75 in 2-3 of 5 (band; 2/5 under 4a).
- **Pivot-if:** (a) holds but (b) misses -> D-quality-at-fixed-route was
  not the binding path; declare the two-stage construction EXHAUSTED and
  pass the wall fully to the design-change track (C3.3 excitation).

Pre-coded operationalizations (stated in the script header before the
run): stage-2 refit = V2 final-refit semantics (`_fit_hazard_candidate` on
combined calibration+selection panels, hazard ridge .005, 30 IRLS
iterations) at the FIXED stage-1 route, no selection anywhere in stage 2;
rows whose stage-1 route equals arm 0's V2-selected route reuse arm 0's
final hazard fit (bit-identical by construction). Coupling note: this
estimator fits the choice/response (GC) legs independently of the hazard,
so the registered "(and GC legs where the estimator couples them)" clause
is vacuous — stage 2 refits exactly the D leg, and C/G are the V2
baseline legs on every arm. Lean statistics: median e_d = author-level
(train/test-mean) e_d_atom on oracle-nondegenerate rows, battery median;
pooled geometry = mean loop_action_geometry over the 40 world-reps;
worlds >= .75 on 8-rep world means.

## Machinery and faithfulness

Bit-exact reuse: V2 replay, arm-2 ridge machinery, and context building
are IMPORTED from `scripts/run_suica_m4_d_overspan_control_leg3.py` and
`scripts/run_suica_m4_d_dleg_floor_leg4.py` (nothing reimplemented).
Battery: 5 creation-active loop worlds x 8 repetitions x 16 authors x
{train, test}; seed rule and config identical to V2/Legs 1/3/4. Runtime
289 s.

| gate | value |
| --- | ---: |
| arm-0 geometries vs archived `metrics.csv` (per world-rep) | **1.11e-16** |
| arm-0 per-row e_loop / e_d vs Leg 1 `per_loop_metrics.csv` (1,280 rows, flags equal) | **2.22e-16** |
| arm-0 flips / pooled loop geometry | **196** / **.6519** (exact) |
| stage-1 per-row vs Leg 4 persisted arm-2 rows (1,280 rows, 40 world-reps, flags equal, asserted per world-rep BEFORE stage 2) | **2.22e-16** |
| stage-1 battery flips (must equal 73 by construction) | **73** (exact) |
| unchanged-route two-stage rows vs arm-0 rows (668 rows, bit-identity by construction) | **0.0** |

## The comparison table (registered baselines, all arms)

| arm | flips | median e_d | pooled loop geometry | worlds >= .75 | pooled creation geometry | non-flip mean e_loop |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| arm0_v2 (V2 baseline) | 196 | .4869 | .6519 | 1/5 | .7736 | .6565 |
| Leg 3 arm2 @ .005 (persisted) | 148 | .4769 | .6886 | 1/5 | .7844 | .6534 |
| Leg 4a arm2 @ .125 (= stage 1, recomputed + asserted) | 73 | .7830 | .6901 | 2/5 | .5800 | .8069 |
| single_stage_025 (secondary) | 96 | .5791 | .7230 | 1/5 | .7424 | .6927 |
| **two_stage (primary)** | **73** | **.4481** | **.7605** | **3/5** | **.8234** | **.6728** |

**The two-stage arm dominates every other arm on every column.** It keeps
stage 1's best-in-arc flip count (73) while posting the best-in-arc median
e_d (.4481 — below even arm0's .4869), the best pooled loop geometry
(.7605), the most worlds over .75 (3/5), and the best creation geometry
(.8234 — above the baseline .7736 that stage 1 alone had crushed to
.5800). Route selection and creation estimation are separable objectives,
both achievable simultaneously; no single-lambda point on the Leg-3/4
response curves comes close to this corner.

## Lean adjudication

- **Lean (a) — HOLD.** Two-stage median e_d **.4481 <= .55**. The
  registered target was "return toward baseline" from stage 1's .783; the
  result goes PAST baseline (.487). Mechanism: e_d compares the discovered
  D against the oracle stack's D; arm 0 pays wrong-route D's (often zero)
  on its 196 flip rows, while stage 2 refits at routes that are correct
  94.3% of the time in the flip sense (1 - 73/1280) — route stabilization
  plus unpenalized refit removes
  more wrong-route error than the baseline ever had.
- **Lean (b) — HOLD, the decisive one.** Pooled loop geometry **.7605 >=
  .70**. The bar missed twice by ~.01 (.6886, .6901) is cleared by
  **+.0605**. D-quality-at-fixed-route WAS the binding path on
  route-stabilized rows: undoing the ridge's D distortion at unchanged
  selection converts stage 1's .6901 into .7605 (+.0704 from the refit
  alone).
- **Lean (c) — HOLD.** Worlds >= .75: **3/5** (gated .9479, rotated
  .7914, expansion .7894), inside the registered 2-3 band. Partition
  (.6527) and compensation (.6209) stay below — see the floor note.
- **Pivot — NOT TRIGGERED** ((a) and (b) both hold). The two-stage
  construction is NOT exhausted; it is the arc's first fully successful
  construction.

Per-world loop geometry (arm0 -> stage1 -> two_stage): expansion .5161 ->
.7200 -> **.7894**; partition .5769 -> .5982 -> **.6527**; gated .9152 ->
.7527 -> **.9479**; compensation .5671 -> .6170 -> **.6209**; rotated
.6841 -> .7627 -> **.7914**. The gated world — DAMAGED by stage 1's ridge
(.9152 -> .7527, the trade-off law's sharpest exhibit) — is not merely
repaired but finishes ABOVE its V2 baseline (.9479): stage 2 keeps the two
flips the ridge fixed there and gives back the underlying V2-quality
derivative.

## Where the gain lives (structure decomposition)

The two-stage arm differs from arm 0 on exactly the rows where stage 1
changed the route: **612 changed rows** (fresh stage-2 refits) vs **668
unchanged rows** that reuse arm 0's final hazard fit and are bit-identical
to arm 0 (max |e_loop diff| = 0.0, by construction and verified). All
pooled-geometry gain over arm 0 comes from the changed 612: their median
e_loop falls .7695 -> .7027 and 59.0% of them improve; arm 0 had 141 of
its 196 flips there (fixed by stage 1's selection), and two-stage carries
the 18 flips stage 1 newly broke (73 = 55 inherited on unchanged rows +
18 on changed rows; stage-2 flips = stage-1 flips = 73 exactly, as the
route class fixes the D-zero pattern).

Against stage 1 at IDENTICAL routes (1,207 both-nonflip rows): median e_d
.7741 -> **.4270**, median e_loop .8141 -> **.6284**, better in 76.6% of
rows — the ridge's creation distortion undone wholesale at fixed
selection. Against arm 0 on both-nonflip rows (1,066): medians essentially
tie (.6174 vs .6168, e_d .4136 vs .4094; the "better" fraction .2364 is
dominated by the 613 bit-identical ties) — i.e., two-stage = arm 0
wherever arm 0's route already agreed, exactly as designed.

Mediation (within-cell rho of D-improvement vs loop-improvement):
two_stage vs stage1 median rho = **.7763** (40/40 cells; IQR [.474,
.869]); two_stage vs arm0 = .7238 (36/40 varying cells); consistent with
Legs 3/4 — the D leg is the channel through which everything moves.

## Secondary arm — the lambda=.025 discovery observation, now licensed

The Leg-4a discovery table showed loop geometry peaking at .025 (one grid
point below the flip-optimal .125); Leg 4's report explicitly declined to
claim it without a battery run. The battery verdict: single_stage_025
posts 96 flips / pooled **.7230** / median e_d .5791 / 1 world >= .75. So
(i) the discovery observation was real — .025 is the best SINGLE-stage
lambda in the arc, beating both .005 (.6886) and .125 (.6901) on pooled
geometry; (ii) it still sits on the trade-off curve — its D is degraded
(.579 vs baseline .487; on both-nonflip rows vs arm 0 it is WORSE in
63.7%), its flip count is worse than .125's (96 vs 73), and it loses to
two-stage on every column. The trade-off law governs every single-lambda
point; only the two-stage construction escapes the curve.

## What is killed, what survives

- **KILLED: the trade-off law's dilemma.** "No single lambda serves both"
  survives as stated (the .025 battery confirms it), but the dilemma —
  that route fidelity must be PAID FOR with creation fidelity — is dead:
  a two-stage design achieves the flip-optimal route stability AND
  better-than-baseline creation fidelity simultaneously. Layers 1 (route
  selection under overspan) and the D-DISTORTION side of layer 2 are now
  repaired by construction.
- **SURVIVES: the Leg-4b structural floor.** Two-stage battery median e_d
  .4481 sits ~.03 above the 1x oracle-forced-route value (.418) and
  approaches the ~.39 pooled realization-variance floor; the two worlds
  still under .75 are exactly the two with the highest 4b per-world floors
  (partition .474, compensation .445 at 4x) plus partition's envelope
  masking. The remaining gap between .7605 and full transport is the
  floor's territory: further lambda tuning or refit variants have nothing
  left to buy; movement requires the design-change track (C3.3 excitation
  richness, paired/interventional occasions, de-biased derivative
  estimators), exactly as the synthesis ordered.

## Honest anomalies and caveats

- **Lean (a) over-delivers, and the reading matters.** .4481 < .4869
  (baseline) is NOT "stage 2 estimates D better than V2 can": on
  route-matched rows stage-2 fits ARE V2 fits (bit-identical). The gain is
  entirely compositional — fewer wrong-route D's in the median. The
  registered lean text anticipated a return toward .487, not past it; the
  overshoot is a route-mix effect, not an estimator improvement.
- **18 broken-route rows persist by construction.** Stage 1's ridge broke
  18 rows arm 0 had right (Leg 4's disclosed 141-fixed/18-broken split);
  stage 2 inherits their routes and cannot repair them. A stage-1 variant
  that only ACCEPTS route changes when they fix a D-zero disagreement is
  an obvious refinement — unregistered, left open.
- **Pooled .7605 also crosses the original .75 pooled NO-GO bar, and 3/5
  worlds satisfy Leg 3's old lean (b) target — neither reopens any gate.**
  The statistic consumes oracle-basis fits on the reference side; it is a
  truth-referenced diagnostic of estimator structure, not the operational
  V2 transport gate, and the V1/V2 NO-GO decisions stand unchanged.
- **Compensation barely moves** (.5671 -> .6209 across the whole arc,
  worst in every arm). Its 4b floor (.445) plus lowest flip leverage (28
  baseline flips) leave route repair little to work with; it is the
  clearest exhibit that the residual wall is not selection.
- **Route-name mismatches stay at 474** (feedback-vs-gate confusions with
  nonzero D on both sides) — unchanged from stage 1 by construction, still
  untouched by any arm in the arc, and evidently not binding at .7605.
- The stage-1 lambda (.125) and the secondary lambda (.025) were fixed by
  Leg 4's registered selection and discovery table respectively; no lambda
  search was run in this leg.

## Scope and claim boundary

Finite synthetic M4-C.2 worlds only. The loop-transport statistic compares
against oracle-basis fits, so this is a truth-referenced diagnostic of the
estimator — NOT an operational rescue of chart transport, not a repaired
or reopened gate: the V1/V2 NO-GO decisions stand unchanged. No
natural-text, personality, emotion, diagnosis, or clinical claim.
EXPLORATORY tier under the 2026-08-01 open-exploration directive; nothing
here may be cited above it.

## Artifacts

- script: `scripts/run_suica_m4_d_two_stage_leg5.py`
- adjudication: `results/m4_d_two_stage/decision.json`
- battery rows (5,120 = 4 arms x 1,280): `results/m4_d_two_stage/per_loop_metrics.csv`
- world-rep rows (160): `results/m4_d_two_stage/world_rep_metrics.csv`
- arm-0 faithfulness: `results/m4_d_two_stage/v2_validation.csv`
- stage-1 vs Leg-4 per-world-rep assert log (40): `results/m4_d_two_stage/stage1_leg4_crosscheck.csv`
