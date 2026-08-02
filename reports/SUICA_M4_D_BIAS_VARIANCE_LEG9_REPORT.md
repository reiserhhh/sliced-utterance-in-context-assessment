# M4-D Leg 9 — The Bias-Variance Account of the Paired Floor: PIVOT FIRES (the account DIES on the registered column); the gap is basis CONTENT; partition is only partly artifact

Tier: **EXPLORATORY** (open-exploration phase, operator directive 2026-08-01).
Registered BEFORE run in `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md`
"Leg 9" (commit 0f3ada7, 2026-08-02, loop cycle 4). Script:
`scripts/run_suica_m4_d_bias_variance_leg9.py`; adjudication:
`results/m4_d_bias_variance/decision.json`. All machinery imported bit-exact
from Legs 3/4/5/6/7/8; faithfulness chain below.

## Verdict

**The registered pivot FIRES: the two-stage ranking does NOT invert at 4x**
(two-stage+lam1n **.6488** < two-stage+V2 **.7538**), and the registered
bias-variance signature fails at 1x in the direction that explains why: on
the PAIRED metric the de-biased estimators have **higher** bias than the V2
ridge (.4621/.6418 vs .3808), not lower — the ridge's shrinkage is
**common-mode in the pairing and cancels**; removing it *uncovers* basis
disagreement instead of removing error. The bias-variance account of the
paired floor is **DEAD** as registered (leans 1/3; recorded plainly).

The dissection that survives it: against the **law** (truth reference) the
de-biased estimators are exactly the low-bias/high-variance objects the
hypothesis imagined — lam1n's R=8-averaged oracle-side law error is
**.0891** (from .2605 per-panel) while the V2 ridge stays bias-pinned at
**.3662** (from .3756). The account was right about the *estimators* and
wrong about the *metric*: the paired floor is anchored to basis
disagreement, not to law accuracy, and (Arm B) that disagreement is
**entirely basis CONTENT** — content share **1.11 / 1.06 / 1.09** in the
three high-gap worlds (lean b HOLDS above 100%: giving the discovered
parameterization the oracle's row *directions* matches or beats the oracle
refit itself; giving the oracle's row *norms* to discovered directions
leaves the gap intact). Partition's resistance is only **partly** reference
artifact: the envelope correction removes 30% of the level
(.5922 → **.4134**, bar .30 — lean c MISSES).

Registered hand-off (per the pivot clause): the next instrument is the
**information-operator conditioning profile** already persisted at
`results/m4_d_bias_anatomy/conditioning_rows.csv`, elevated to a full leg.

## Registered arms and leans (plan, commit 0f3ada7)

- **Arm A**: {V2 ridge, lam1n, unpen} x {1x, 4x}, R=8 fresh panels per
  world-rep (Leg 7 mechanism); per-cell paired error split into bias^2 +
  variance; then the FULL two-stage 5x8 battery with each estimator as the
  stage-2 refit at both budgets (6 batteries).
- **Arm B**: gap content-swap in the 3 high-gap worlds — (i) oracle basis +
  discovered support-weights, (ii) discovered basis + oracle support-weights.
- **Arm C**: partition law-level bias under the envelope-corrected reference.
- **Leans**: (a) lower-bias/higher-variance signature at 1x AND ranking
  inversion at 4x; (b) basis-content >= 70% in >= 2/3 worlds; (c) partition
  .592 -> <= .30. **Pivot-if**: no inversion at 4x -> account dies; next
  instrument = the persisted conditioning profile.

Operational definitions fixed here (stated in the script docstring before
assembly): pairing per estimator against ITS OWN oracle-basis twin (Leg-4b
semantics); bias_rel = ||mean_r delta_r|| / ||mean_r D_orc_r||, var_rel =
mean_r ||delta_r - mean delta||^2 / ||mean_r D_orc_r||^2, total = bias^2 +
var exactly (identity asserted per cell, 7,680 cells, 72 degenerate
excluded); "support-weights" = per-category basis row norms, "content" =
row directions (the factorization left after Leg 8 killed orientation);
attribution = symmetric two-factor main effects, content + weights = gap_v2
exactly; p_env measured per world-rep as mean menu occupancy (menu ==
envelope in partition; measured range .6190-.6213 vs analytic .62).

## Arm A — bias-variance decomposition (registered pairing)

Pooled author-level medians:

| estimator | budget | bias_rel | var_rel | total | bias share | mean per-panel paired |
|---|---|---|---|---|---|---|
| v2ridge | 1x | **.3808** | .0251 | .1847 | .848 | .4181 |
| v2ridge | 4x | **.3773** | .0059 | .1501 | .958 | .3853 |
| lam1n | 1x | **.4621** | .1253 | .4213 | .562 | .6088 |
| lam1n | 4x | **.4390** | .0317 | .2592 | .823 | .4973 |
| unpen | 1x | **.6418** | .2527 | .7689 | .427 | .8123 |
| unpen | 4x | **.6247** | .0624 | .5037 | .717 | .6808 |

- The V2 ridge's paired error is already **84.8% bias^2 at 1x and 95.8% at
  4x** — the paired floor is nearly pure pair-bias for the production
  estimator (Leg 7's R-invariance, now quantified from inside).
- The **variance half of the signature held** (lam1n .1253 > v2 .0251;
  unpen .2527 > .0251) and variance does collapse with budget (lam1n .125
  -> .032); the **bias half failed** — de-biased estimators show MORE
  paired bias, at every budget. Signature: MISS (both estimators, both
  halves required).
- Law-reference companions (same cells): e_orc_true per-panel -> R=8-avg:
  v2ridge .3756 -> .3662 (bias-pinned); lam1n .2605 -> **.0891**; unpen
  .3181 -> .1201. Against truth, de-biasing works exactly as hypothesized;
  against the pairing, it backfires. The two references now measurably
  disagree about which estimator is "better" — the paired metric rewards
  shared ridge behavior (Leg 8's mechanism, now decomposed).

## Arm A — the six-battery ranking (the decisive numbers)

Stage 1 = Leg 5 stage 1 bit-exact in all six (flips 73 asserted); stage-2
refit per cell on the canonical realization-0 panels of the stated budget.

| battery | stage-2 | pooled loop | creation | median e_d | flips | [2nd: lam1n-ref loop] |
|---|---|---|---|---|---|---|
| two_stage | v2ridge @ 1x | **.7605** | .8234 | .4481 | 73 | .6811 |
| ts_lam1n_1x | lam1n @ 1x | **.6248** | .7063 | .8778 | 73 | .6592 |
| ts_unpen_1x | unpen @ 1x | **.4072** | .4011 | 1.0000 | 194 | .4369 |
| ts_v2ridge_4x | v2ridge @ 4x | **.7538** | .8195 | .4496 | 73 | .7003 |
| ts_lam1n_4x | lam1n @ 4x | **.6488** | .7469 | .7441 | 73 | .6862 |
| ts_unpen_4x | unpen @ 4x | **.4115** | .4192 | .9014 | 207 | .4319 |

- **Inversion test**: below at 1x — yes (.6248 < .7605); inverts at 4x —
  **NO** (.6488 < .7538). The 4x budget moves lam1n +.0240 and v2ridge
  -.0067 (gap .1357 -> .1050, 23% closed): the direction the equilibrium
  account predicted, an order of magnitude short of the crossing it
  required. **PIVOT FIRES.**
- two_stage reproduces Leg 5's .76048 and ts_lam1n_1x reproduces Leg 8's
  two_stage_lever .62476 (both asserted per row at 2.2e-16 scaled).
- unpen as a stage-2 refit is not a viable estimator here: 190/207 rows
  collapse to exactly D=0 (separation on singular unpenalized systems;
  the Leg-8 guard ladder fired 257,963 times in the floor pass + 17,262 in
  the battery, essentially all on unpen/lam1n fits), flips explode 73 ->
  194/207.

**UNREGISTERED-SECONDARY column (no adjudication weight; the "missing
arm" Leg 8 flagged):** every statistic recomputed against a lam1n-fitted
oracle reference (same realizations/budgets; reference loops D_orc_lam1n @
G_orc @ C_orc; reference itself sits .898/.905 loop geometry from the V2
oracle at 1x/4x). Result: **no reference-bias rescue** — the inversion is
absent on this column too (ts_lam1n_4x .6862 < ts_v2ridge_4x .7003). But
the column does localize most of the 1x MARGIN: against the de-biased
reference, two_stage falls .7605 -> .6811 and the lam1n-vs-v2 gap at 1x
shrinks from .1357 to **.0220** — i.e. most of the margin by which
de-biased D "damages transport" is the V2-fitted endpoint rewarding its
own ridge bias; what reference choice does NOT change is the ordering.
Recorded as qualification, not rescue; leans adjudicated on the registered
column only.

## Arm B — the gap is basis CONTENT (lean b HOLDS, above 100%)

Row-norm swaps at the oracle-forced route, V2 semantics, 1x panels;
world-level author-median gaps (gap_* = e_*_true − e_orc_true):

| world | gap_v2 | gap_i (orc content + disc weights) | gap_ii (disc content + orc weights) | content | weights | content share |
|---|---|---|---|---|---|---|
| expansion | .2150 | **−.0199** | .2439 | .2394 | −.0245 | **1.114** |
| compensation | .2102 | **+.0052** | .2391 | .2220 | −.0119 | **1.056** |
| rotated | .2283 | **−.0096** | .2590 | .2484 | −.0202 | **1.088** |

Attribution formula (registered in-script): 2x2 factorial corners
{(disc,disc)=gap_v2, (orc,disc)=gap_i, (disc,orc)=gap_ii, (orc,orc)=0};
content = .5·((gap_v2−gap_i)+gap_ii), weights = .5·((gap_v2−gap_ii)+gap_i);
content+weights = gap_v2 exactly. Reading: swap in the oracle's row
DIRECTIONS and the discovered-width refit **matches or slightly beats the
oracle refit itself** (gap_i ≈ 0, twice negative); swap only the row NORMS
and the gap is fully intact (gap_ii ≥ gap_v2). After Leg 3 (span must
match), Leg 8 (not orientation — alignment inverts), this pins the
basis-mismatch bias to the **direction content of the basis rows per
category**; support-weighting contributes ~0 (slightly negative). 3/3
worlds ≥ .70 — lean b HOLDS with margin.

## Arm C — partition: partly artifact, mostly real (lean c MISSES)

Envelope mechanics verified: menu == envelope in this world; measured
p_env .6190–.6213 across 8 world-reps (analytic stationary .62 exact).
Author-median law-level bias, oracle basis, natural panels:

| estimator | latent 1x | env-corrected 1x | latent 4x | env-corrected 4x | scale c* (1x) |
|---|---|---|---|---|---|
| v2ridge | .6447 | **.4480** | .6426 | .4436 | .3634 |
| lam1n | .5922 | **.4134** | .5657 | **.3450** | .4341 |
| unpen | .6011 | .4226 | .5772 | .3679 | .4291 |

The correction removes **30.2%** of lam1n's 1x level (.5922 → .4134), not
the ≥ half the lean required (bar .30) — **MISS**. The reference gap
itself drops .6447 → .4480. The scale diagnostic explains the residual:
the fitted D sits at c* ≈ .43·D_true, well below the envelope's .62 — a
genuine world-specific attenuation beyond the masking artifact. Partition
remains the worst world under every estimator and both references (best
reachable here: lam1n @ 4x corrected .3450). Leg 4's caveat stands
upgraded: e_*_true LEVELS in partition carry a ~.62 multiplicative
reference offset (now measured, not just flagged), but correcting it does
not dissolve the world's resistance.

## Leans and pivot (registered column)

- **Lean (a): MISS.** Signature failed (bias half inverted: lam1n .4621 >
  v2 .3808, unpen .6418 > .3808 at 1x; variance half held) AND no ranking
  inversion at 4x (.6488 < .7538).
- **Lean (b): HOLD.** Content share 1.114/1.056/1.088 — 3/3 worlds ≥ .70.
- **Lean (c): MISS.** .5922 → .4134 corrected (bar .30); 30% artifact,
  70% real.
- **PIVOT FIRES** (registered): the bias-variance account of the paired
  floor is DEAD. Qualification from the unregistered-secondary column: no
  reference-bias rescue (inversion absent on both columns), but most of
  the 1x de-biasing penalty (.1357 of margin → .0220) is the V2-fitted
  endpoint rewarding shared ridge bias. Next instrument (registered):
  the information-operator conditioning profile persisted at
  `results/m4_d_bias_anatomy/conditioning_rows.csv`, elevated to a full
  leg.

## What this kills, what stands

Killed: the floor-as-bias-variance-equilibrium reading — budget does shift
the equilibrium exactly as predicted (variance terms collapse, lam1n gains,
v2 flat) but the crossing never comes because de-biasing RAISES pair-bias;
no budget rescues a de-biased stage-2 refit under the paired transport
metric. Also killed: support-weighting as a gap mechanism (Arm B) and the
strong form of the partition-artifact hypothesis (Arm C).

Stands, sharpened: the paired floor's last layer is the **basis-content
gap** — the discovered chart's per-category row directions — which is (i)
~100% of the estimator-minus-oracle gap in the three high-gap worlds, (ii)
untouched by budget, realization averaging, excitation, de-biasing, and
row-norm correction, and (iii) invisible to law-accuracy improvements
because the paired metric scores basis agreement. The Leg-8 reference-bias
mechanism is now quantified: it accounts for most of the de-biasing
penalty's size but not its sign.

## Honest anomalies and caveats

- The lever r=0 crosscheck vs Leg 8's persisted rows shows max diff
  1.42e-14 (vs 2.2e-16 elsewhere): the unpen/lam1n fallback path
  (lstsq/gelsy under BLAS threading, this run executed 4 chunks in
  parallel) is not bit-stable at the last ULP scale. Within the 1e-9
  tolerance; flags all equal; no adjudicated statistic is near that scale.
- unpen's battery rows include 190/207 exact-zero D collapses
  (separation); its "flips" statistic counts these, so its battery numbers
  measure estimator failure, not transport structure. Guard-ladder
  fallbacks: 257,963 (floor) + 17,262 (battery), zero on v2ridge fits.
- The signature lean was registered on the PAIRED decomposition; this
  report also shows the law-reference decomposition where the same
  estimators DO show the low-bias/high-variance pattern. The lean is
  adjudicated as registered (MISS); the law-side pattern is reported as
  context, not as a hold.
- 4x fresh realizations are law-identical but path-independent draws;
  budgets compare law-to-law (Leg 4b's convention), and realization-0 at
  each budget is the canonical battery panel set, gated bit-exactly.
- The lam1n-referenced column consumes lam1n oracle-side fits (r=0) for
  the battery endpoints; its creation-geometry variant was not computed
  (loop geometry only) — stated scope of the secondary column.

## Faithfulness chain (all asserted, RuntimeError on any breach)

- V2 replay vs archived battery: max 1.11e-16 (40/40 world-reps).
- v2ridge r=0 rows vs Leg 4 persisted floor rows at 1x AND 4x: max
  2.22e-16, flags equal (the 4x side also gates the offset-realization
  bridge: offset-0 `_path_panel` panels reproduce the full generator's 4x
  panels value-exactly on all 8 fields x 4 panels, 40/40).
- Law identity (oracle basis + all 8 author-parameter arrays) bit-identical
  40/40; realization-0 1x panel identity 40/40; analytic D_true unit check
  max 1.67e-15; v2ridge oracle refit identity vs context stacks exactly 0.
- lam1n/unpen oracle-side r=0 rows vs Leg 8 persisted lever rows: max
  1.42e-14 (disclosed above), flags equal, 40/40.
- Stage-1 vs Leg 4 arm-2 rows: 2.19e-16 scaled, flips exactly 73;
  two_stage vs Leg 5 rows: 2.21e-16, pooled .76048 reproduced;
  ts_lam1n_1x vs Leg 8 two_stage_lever rows: 2.19e-16, pooled .62476
  reproduced.
- Assembly refused missing/duplicate cells: 7,680 decomposition cells
  (72 degenerate), 60,864 per-panel rows, 768 swap rows, 768 partition
  rows, 8,960 battery rows, 8,960 secondary rows, 360 secondary world
  rows, 40 gate payloads.

## Scope and claim boundary

Finite synthetic M4-C.2 worlds only. Truth-referenced estimator
diagnostics throughout (oracle basis, oracle-forced routes, generator-law
derivatives, generator-privileged fresh realizations of the frozen law,
and the generator's envelope constant are consumed as references); the
lam1n-referenced pairing column is UNREGISTERED-SECONDARY with no
adjudication weight; nothing here is an operational rescue of chart
transport or a reopened gate; the V1/V2 and C3.3 NO-GO decisions stand.
No natural-text, personality, emotion, diagnosis, or clinical claim.
EXPLORATORY tier; nothing here may be cited above it. No seal, no
independent verification (operator directive 2026-08-01).

## Artifacts

- script: `scripts/run_suica_m4_d_bias_variance_leg9.py`
- adjudication: `results/m4_d_bias_variance/decision.json`
- decomposition cells / per-panel rows / summary:
  `results/m4_d_bias_variance/bv_cells.csv`, `bv_panel_rows.csv`,
  `bv_summary.csv`
- battery: `battery_world_rep_metrics.csv`, `battery_per_loop_metrics.csv`;
  secondary column: `battery_secondary_lam1nref_world.csv`,
  `battery_secondary_lam1nref_rows.csv`
- gap swap: `gap_swap_rows.csv`, `gap_attribution.csv`
- partition: `partition_reference_rows.csv`
- crosschecks: `check_1x/check_4x/lever_check/stage1_check/`
  `two_stage_check/lam1n_1x_check_crosscheck.csv`, `v2_validation.csv`
