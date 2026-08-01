# SUICA M4-D Leg 3 — Overspan-Controlled Route Identification

Date: 2026-08-01
Tier: EXPLORATORY (open-exploration phase; operator directive 2026-08-01:
defensive machinery deferred; design and leans registered in
`docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md` ("Leg 3") before this
run; no prospective seal, no independent verification pass)

## Decision

```text
M4_D_LEG3_PARTIAL_ROUTE_STABILIZATION_WITHOUT_TRANSPORT_RECOVERY_THIRD_LAYER_IS_D_LEG_ESTIMATION
```

The best single arm (arm 2, ridge on the hazard feedback parameterization)
moves both registered quantities in the predicted direction — flips 196 ->
148, pooled loop geometry .6519 -> .6886, with strong D-leg mediation (.7355)
— but leans (a) and (b) MISS: flips fall 24.5%, not the registered half, and
no arm adds a single world above the .75 bar (1/5 throughout). Lean (c)
HOLDS under both registered readings. The registered pivot condition is
adjudicated PARTIALLY TRIGGERED (both readings below), and the third-layer
profile shows why the leans could not hold: un-flipping the route recovers
almost none of the loop — flip-fixed rows land at median e_loop .78, and the
non-flip loop error barely moves (.6705 -> .6634). Selection instability is
real but shallow; underneath it is D-leg ESTIMATION error at the correct
route, which no amount of route stabilization removes. Separately, the
width-control arm produced the sharpest negative of the battery: shrinking
the chart frame toward oracle width made everything worse (flips 228, pooled
.5641), because the negative-spectrum rule UNDER-spans where source
disagreement is structural, and because rank-matching does not subspace-match.

## Registered design and leans (verbatim intent from the plan)

Arms, independent (never stacked), all modifying the DISCOVERED-side
estimation only — oracle fits are frozen V2 semantics, shared bit-for-bit
across arms:

- Arm 0 `arm0_v2`: exact V2 replay; must reproduce the archived wall.
- Arm 1 `arm1_width`: chart-frame rank by the Leg-2 bridge negative-spectrum
  noise-floor rule (eigenvalue > 2x |most negative|), applied to the chart
  estimation step.
- Arm 2 `arm2_penalized`: V2 charts; extra ridge (single global lambda) on
  hazard `feedback_*`/`gate_*` coefficients; lambda by out-of-fold likelihood
  on discovery repetitions only.
- Arm 3 `arm3_oof`: V2 charts and fits; route selected by symmetric two-fold
  out-of-fold predictive score instead of the V2 rule.

Leans: (a) flips halved in the best single arm (196 -> <= 98); (b) per-world
mean loop geometry >= .75 in >= 3 of 5 worlds (currently 1/5); (c) mediation:
within-(world x rep) rho between D-leg error improvement and loop improvement
>= .5 (the plan wording registers (c) on the width arm; the orchestrator
restatement says winning arm; both were computed). Pivot-if: flips drop but
pooled geometry stays < .70 — then the D-leg error is not selection-driven;
profile the third layer.

## Machinery and faithfulness

Exact replay of the M4-C.2 V2 confirmation (config
`configs/m4_chart_ecology.json`, seed 271828183, same seed rule, generator,
chart fit, and per-author fitting flow as Leg 1, which validated to 1.1e-16)
on the five creation-active loop worlds x 8 repetitions x 16 authors x
{train, test}. Faithfulness gates, all enforced before/against the arms:

| gate | value |
| --- | ---: |
| arm-0 loop/choice/creation geometry vs archived `metrics.csv`, max abs difference (in-task, before arms run per world-rep) | **1.11e-16** |
| arm-0 per-row e_loop / e_d vs Leg 1 `per_loop_metrics.csv`, max abs difference (1,280 rows) | **2.22e-16** |
| arm-0 selected models and flip flags vs Leg 1 | identical |
| arm-0 flips total / by world | **196** = 53/72/38/5/28 |
| arm-0 pooled loop geometry | **.6519** |

Flip definition is Leg 1's (D-zero flips: exactly one of the discovered/
oracle pair has a zero D leg); route-name mismatches are recorded separately.
Loop geometry is V2's own statistic (Spearman-of-pdist on author-mean
kernels, train/test averaged). Primary per-loop unit: author-level
(train/test mean) on oracle-nondegenerate rows.

## Arm battery (40 world-reps, 1,280 view-rows per arm)

| arm | flips | pooled loop geometry | worlds >= .75 | mean width by world (part/exp/rot/gated/comp; oracle 7) |
| --- | ---: | ---: | ---: | --- |
| arm0_v2 | 196 | .6519 | 1/5 | 13.0 / 12.9 / 13.0 / 8.6 / 12.8 |
| arm1_width | **228** | **.5641** | 1/5 | 8.6 / 9.0 / **5.0** / 8.5 / 7.5 |
| arm2_penalized (winner) | **148** | **.6886** | 1/5 | = arm 0 |
| arm3_oof | 195 | .6753 | 1/5 | = arm 0 |

Per-world loop geometry (mean over 8 reps):

| world | arm0 | arm1 | arm2 | arm3 |
| --- | ---: | ---: | ---: | ---: |
| endogenous_source_partition_matched | .577 | .547 | .619 | .590 |
| endogenous_creation_expansion | .516 | .503 | .631 | .537 |
| source_rotated_feedback | .684 | .443 | .710 | .663 |
| history_gated_ecology | .915 | .915 | .884 | .932 |
| selection_creation_compensation | .567 | .412 | .599 | .654 |

Winning arm by the pre-coded rule (fewest flips, ties by pooled geometry):
**arm2_penalized**.

## Arm 2 lambda selection (registered criterion, stated here)

Out-of-fold likelihood (fit on calibration, hazard logloss on the selection
panel, penalized feedback/gate candidates, discovered basis) on discovery
repetitions {0, 1} x 5 worlds x 32 author-views:

| lambda | mean OOF logloss |
| ---: | ---: |
| **0.005** | **.45899** |
| 0.025 | .46288 |
| 0.125 | .47701 |
| 0.625 | .49463 |

The criterion is monotone in lambda and picks the GRID BOUNDARY (0.005, one
base-ridge worth of extra shrinkage) — i.e., the registered likelihood
criterion licenses only the weakest available treatment. Even so, arm 2 cut
flips by 48 net (50 fixed, 2 newly broken) and lifted pooled geometry +.037.
Post-hoc, unregistered sensitivity (recorded honestly, not adjudicated): the
pre-run smoke executed the same battery code on two rep-0 cells at
lambda = 0.125 and saw much stronger route stabilization (partition rep 0:
flips 5 -> 0, geometry .565 -> .831 vs .633 at 0.005; expansion rep 0:
14 -> 5, -.101 -> .588 vs .160). The binding constraint on this arm appears
to be the likelihood-based tuning rule, not the ridge mechanism — untested
beyond those two cells and unlicensed here.

## Lean (a) — MISS (flips fall by a quarter, not by half)

Best single arm: arm 2, 196 -> **148** (registered bar <= 98). By world:
53 -> 38 (partition), 72 -> 55 (expansion), 38 -> 30 (rotated), 5 -> 4
(gated), 28 -> 21 (compensation). Remaining flip directions are unchanged in
kind: discovered `return` vs oracle `feedback` 102, vs oracle `gate` 43,
reverse 3. Arm 3 is a wash (195: fixed 62, newly broke 61 — the symmetric
two-fold score reshuffles selection about one-for-one rather than
stabilizing it; its name-level mismatches are actually the battery's worst
at 539). Arm 1 goes the wrong way (228: fixed 80, manufactured 112).

## Lean (b) — MISS (no arm adds a world above .75)

Every arm stays at 1/5 (gated only). Closest approach: arm 2 lifts rotated
to .7096 (from .6841); expansion reaches .6312, still far below the bar.

## Lean (c) — HOLD (both registered readings)

Within-(world x rep) Spearman between D-leg error improvement and loop-error
improvement vs arm 0, author-level:

| reading | arm | median within-cell rho | cells with variation |
| --- | --- | ---: | ---: |
| plan wording (width arm) | arm1_width | **.6118** (IQR .43–.81) | 33/40 (7 gated cells are exact no-ops) |
| task wording (winning arm) | arm2_penalized | **.7355** (IQR .43–.88) | 40/40 |

Both clear .5; the readings agree. Where these arms move the loop at all,
they move it through the D leg — the mechanism channel is exactly the one
Leg 1 identified. What (c) holding alongside (a)/(b) missing means: the
lever is correct but far too short.

## Pivot adjudication — PARTIALLY TRIGGERED (both readings recorded)

- Strict registered letter ("flips drop but pooled geometry stays < .70"):
  flips DID drop (196 -> 148, −24.5%) and the winning arm's pooled geometry
  IS below .70 (.6886). By the letter, the pivot FIRES.
- Pre-coded operationalization in the script (written before the run):
  trigger = lean-(a) hold AND geometry < .70; since flips did not halve, it
  records `triggered: false`.

Both readings are persisted (`decision.json` carries the operationalized
field; this section is the controlling adjudication). The substantive
question the pivot asks — is the D-leg error selection-driven? — is answered
by the profile below: **mostly not**, so the third layer is profiled as
registered.

## Third-layer profile (where the wall lives after route stabilization)

1. **Un-flipping the route does not recover the loop.** The 50 rows arm 2
   un-flipped go from e_loop = 1 (structural) to median **.7803** (mean
   .9659 — a few recovered-but-misoriented D legs exceed 1). Route identity
   is necessary but nearly worthless without a usable D estimate.
2. **The non-flip error floor is flat.** Author-level non-flip mean e_loop:
   .6705 (arm 0) -> .6634 (arm 2); median .6397 -> .6250. The entire pooled
   geometry gain rides on the flip channel plus slight D shrinkage; the bulk
   error does not move.
3. **The D leg carries the remaining error, within cells and by leg swap.**
   On non-flip author-loops (arm 2): within-cell median rho(e_d, e_loop) =
   **.6926** vs rho(e_gc, e_loop) = .4393; substituting the oracle D leg
   (keeping discovered G@C) leaves median error .4084, substituting the
   oracle G@C (keeping discovered D) leaves **.4542**; the D-side residual
   exceeds the GC-side residual in **60.6%** of author-loops. Both legs are
   substantially wrong; D is the heavier and the better-ranking one.
4. **Where:** remaining non-flip mean e_loop by world (arm 2): compensation
   .842, expansion .779, partition .776, rotated .670, gated .293 — the wall
   ordering survives route stabilization.

Reading: the loop wall has (at least) three layers — (i) hazard
model-selection flips (the visible metric-level channel, partially
repairable by regularization), (ii) D-leg estimation error at the correct
route under chart overspan (the dominant per-loop channel, untouched by any
arm here), and (iii) the GC composite error underneath both (~.41 even with
an oracle D). Route identification alone cannot close the gate.

## Arm 1 honest disclosure — width shrinking UNDER-spans and hurts

The negative-spectrum rule (floor = 2x |most negative eigenvalue| of the
cross-source Gram; the source-averaged covariance the V2 whitening actually
consumes is PSD, so the indefinite object had to be the symmetrized
cross-source relation — stated in the script header) shrank widths from
12-13 to 5.0-9.0 against oracle 7. Outcome: flips 196 -> 228, pooled
geometry .6519 -> .5641. Decomposition:

- **Under-span (11/40 reps below oracle width 7: rotated 8/8 at widths 4-6,
  compensation 3/8 at 6):** flips 53 -> 89, geometry .627 -> .439. The
  rotated world is the designed trap for this rule: its two sources observe
  genuinely different orthogonal pre-context maps (the generator ties
  `source_maps` across sources for every loop world EXCEPT
  `source_rotated_feedback`), so cross-source disagreement there is
  STRUCTURAL rotation, not exchangeable noise — the floor reads signal as
  noise and truncates to rank 4.
- **Matched-or-over reps (22 non-no-op reps at widths 7-11):** flips flat
  (138 -> 134) but geometry still drops (.584 -> .518). Sharpest cases:
  compensation reps 3-4 at EXACTLY width 7 — flips 1 -> 12 and 5 -> 13,
  geometry .772 -> .154 and .617 -> .164. Top-eigenvalue truncation of the
  averaged-feature covariance controls the COUNT of retained directions, not
  WHICH directions: rank-matching does not subspace-matching make.
- The 7 gated no-op reps (bridge rank = V2 rank) are the only unharmed
  cells, and gated was already the passing world.

Finding, stated plainly: **span must MATCH, not merely shrink** — a
Goldilocks/misspecification structure. Overspan dilutes the feedback
parameterization (Leg 1); underspan deletes it; and even count-correct
truncation can drop mechanism directions. A usable width control needs (i) a
noise model that matches the disagreement channel (the cross-source floor is
invalid under structural source rotation) and (ii) subspace identification,
not rank capping.

## Other honest notes

- Winning-arm selection, lean-(b)/(c) attachment to "the winning arm", and
  the pivot operationalization were coded before the run; the plan-vs-task
  wording difference on (c) is moot (both hold).
- Arm 3's two-fold score drops the V2 parameter-count penalty by design; its
  failure is therefore informative: the flip channel is not primarily the
  width-coupled complexity penalty (removing it changes almost nothing
  net) but the diluted feedback signal itself in the small selection panel
  (2 occasions), whose per-author OOF loss is too noisy to stabilize
  selection (fixed 62 / broke 61).
- The lambda pre-pass consumes discovery reps {0, 1}, which remain in the
  evaluation battery (registration fixed the battery to the exact V2 40
  world-reps; the pre-pass choice is stated rather than the reps excluded).
- e_loop can exceed 1 on rows where a zero-D route is replaced by a badly
  oriented nonzero D; medians are quoted alongside means where this matters.
- Arm-1 mediation cells exclude 7 exact no-op (zero-variance) gated cells;
  the 33 remaining cells carry the .6118.

## Scope and claim boundary

Finite synthetic M4-C.2 worlds only. The loop statistic compares
discovered-side fits against oracle-basis fits, so everything here is a
truth-referenced diagnostic of the estimator — not an operational rescue of
chart transport, not a repaired gate, and no reopening of the V1/V2 NO-GO
decisions, which stand unchanged. No natural-text, personality, emotion,
diagnosis, or clinical claim. EXPLORATORY tier; nothing here may be cited
above it.

## Artifacts

- script: `scripts/run_suica_m4_d_overspan_control_leg3.py`
- per-loop rows (5,120 = 4 arms x 1,280): `results/m4_d_overspan_control/per_loop_metrics.csv`
- world-rep rows (160): `results/m4_d_overspan_control/world_rep_metrics.csv`
- arm-0 faithfulness: `results/m4_d_overspan_control/v2_validation.csv`
- lambda pre-pass: `results/m4_d_overspan_control/arm2_lambda_selection.csv`
- adjudication: `results/m4_d_overspan_control/decision.json`
