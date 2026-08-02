# SUICA M4-D Leg 12 — Two-Stage Retrofit of the M4-C.3 Attribution NO-GO

**EXPLORATORY** (open-exploration phase, operator directive 2026-08-01).
Registered before run in `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md`
"Leg 12" (2026-08-02, loop cycle 7 — first standing-queue item after the closed
M4-D arc). Script: `scripts/run_suica_m4_d_c3_retrofit_leg12.py`. Results:
`results/m4_d_c3_retrofit/`.

## Verdict

**ALL THREE LEANS MISS; PIVOT DOES NOT FIRE; THE RETROFIT HYPOTHESIS IS DEAD IN
AN UNANTICIPATED DIRECTION.** The two-stage construction does on the C.3
battery exactly what the M4-D arc established — D-zero route flips drop
149 → 57 and every loop statistic improves (pooled loop transport geometry
.6278 → .7421) — and the attribution ordering gets WORSE, not better: pooled
budget Spearman **.7264 → .6677** (movement −.0588), passing repetitions
**4 → 2**. The original NO-GO's error-budget Spearman was partially CARRIED by
route-flip contamination: flipped rows put extreme values into budget and
realized loss simultaneously and co-ranked them. Removing the contamination
compresses realized loop loss while the first-order budget barely moves: on
the 68 touched view-rows the median total budget shifts .825 → .776 (−6%)
while the median realized loop loss collapses .449 → .200 (−55%) and the
median creation Shapley loss halves (.213 → .110). The attribution deficit is NOT independent
of route contamination — it was positively fed by it. `M4_C3_NO_GO_ERROR_ATTRIBUTION`
stands under both constructions.

## Registered design (bounded retrofit)

Rerun the EXACT C.3 attribution battery (same config
`configs/m4_physical_edge_audit.json`, same 5 worlds x 8 repetitions, same
seeds, same Shapley/error-budget formulas, same decision function, same
Spearman target .75) changing ONLY the discovered-side loop/leg production to
the two-stage construction reused from `scripts/run_suica_m4_d_two_stage_leg5.py`:

- **Stage 1** — route selection by the arm-2 penalized hazard candidate flow at
  the route-accuracy-selected ridge lambda = .125 (`leg3._fit_hazard_penalized`,
  extra ridge on `feedback_*`/`gate_*` coordinates, calibration-only
  candidates, C.3's own selection rule; `base`/`return` reuse the V2 candidate
  scores — the penalty is vacuous on them).
- **Stage 2** — C.3's own V2 unpenalized final refit (`_fit_hazard_candidate`
  on combined calibration+selection, hazard ridge .005, 30 IRLS iterations) at
  the FIXED stage-1 route; no selection in stage 2.

The oracle reference route is frozen V2 semantics shared bit-for-bit between
arms (M4-D arm discipline). The fault-injection sub-battery consumes the
oracle route only, so it is IDENTICAL between arms by construction — fault
accuracy 1.0 and margin LCB .0293 carry over.

## Reproduction certificate (before the retrofit arm)

Per world-rep, freshly computed original-arm rows were asserted against
`results/m4_physical_edge_audit_v1_no_go/` BEFORE the retrofit arm ran on that
world-rep; the reassembled original decision was asserted against the
persisted `decision.json` before adjudication.

| check | value |
|---|---|
| metrics rows max abs difference (80 rows) | 1.11e-16 |
| fault rows max abs difference (320 rows) | 9.89e-17 |
| rank rows max abs difference (120 rows) | 1.11e-16 |
| decision diagnostics max abs difference | 0.0 |
| decision string / gate booleans | equal |

Internal bit-identity gates on the retrofit arm (asserted per author, all
1,280 author-view rows): recomputed V2 route selection == original view's;
shared response/choice legs exactly equal; unchanged-route stage-2 creation
legs exactly equal to the V2 final fit. The 12 view-rows containing no route
change are bit-identical between arms across every float diagnostic (max
difference 0.0).

## Headline comparison

| statistic | original (V2) | retrofit (two-stage) |
|---|---|---|
| decision | `M4_C3_NO_GO_ERROR_ATTRIBUTION` | `M4_C3_NO_GO_ERROR_ATTRIBUTION` |
| pooled budget Spearman (bar .75) | **.7264** | **.6677** |
| passing repetitions (bar 6) | **4** (reps 0,2,4,5) | **2** (reps 0,7) |
| fault localization accuracy | 1.0 | 1.0 (identical by construction) |
| pooled loop transport geometry (DDD) | .6278 | .7421 |
| mean Shapley loss: creation / response / choice | .243 / .052 / .077 | .131 / .051 / .076 |
| D-zero flips (1,280 author-view rows) | 149 | 57 (109 corrected, 17 broken) |
| route-name mismatches vs oracle | 455 | 513 |
| rank-arm loop geometry 4 / 8 / 12 | .382 / .632 / .570 | .431 / .711 / .711 |
| basis invariance max difference | 4.668e-10 | 4.668e-10 (binding on shared legs) |

The failing gates are the same two in both arms: `error_budget` and
`repetition_stability`. All six others pass in both.

## Per-repetition comparison (the registered split table)

| rep | Spearman orig | Spearman retro | delta | pass orig | pass retro | flips corrected | flips broken | routes changed |
|---|---|---|---|---|---|---|---|---|
| 0 | .9273 | .7939 | −.1333 | yes | yes | 7 | 3 | 59 |
| 1 | .7091 | .2848 | −.4242 | no | no | 7 | 2 | 75 |
| 2 | .7576 | .5273 | −.2303 | yes | no | 13 | 0 | 75 |
| 3 | −.0061 | .0061 | +.0121 | no | no | 31 | 3 | 93 |
| 4 | .8303 | .6606 | −.1697 | yes | no | 17 | 4 | 91 |
| 5 | .8061 | .6848 | −.1212 | yes | no | 14 | 2 | 75 |
| 6 | .6727 | .6000 | −.0727 | no | no | 6 | 2 | 95 |
| 7 | .6970 | .7818 | +.0848 | no | yes | 14 | 1 | 73 |

Every repetition contains corrected flips, so the registered flip-corrected vs
untouched REP split is degenerate (8 vs 0) and the pre-coded fallback applies:
graded Spearman between per-rep corrected-flip count and per-rep
delta-Spearman = **+.313** (< the pre-coded .5 bar) on the primary flip
variable; **−.217** on the name-level route-correction secondary. Six of eight
reps degrade; the only meaningful gain (rep 7, +.085) sits at a middling
correction count, and the heaviest-corrected rep (rep 3, 31 corrections) stays
at ~zero (−.006 → +.006) — its ordering was never flip-driven to begin with.

## Within-world budget-vs-loss Spearman (16 view-rows each)

| world | original | retrofit | routes changed | flips corrected |
|---|---|---|---|---|
| endogenous_creation_expansion | +.041 | −.365 | 165 | 27 |
| endogenous_source_partition_matched | +.441 | +.338 | 167 | 32 |
| history_gated_ecology | +.897 | +.915 | 13 | 3 |
| selection_creation_compensation | +.232 | +.529 | 131 | 32 |
| source_rotated_feedback | +.762 | +.468 | 160 | 15 |

The one world where the registered mechanism story holds is compensation
(+.23 → +.53, 32 corrections). The near-untouched world (gated) keeps its high
ordering. The three other route-heavy worlds all LOSE ordering — expansion
inverts outright.

## Original-vs-retrofit table per rep per world (train/test mean)

budget = `path_error_total`; loop loss = 1 − DDD geometry.

| rep | world | budget orig | budget retro | loop loss orig | loop loss retro | routes changed | flips corrected | flips broken |
|---|---|---|---|---|---|---|---|---|
| 0 | expansion | 0.454 | 0.449 | 0.099 | 0.096 | 16 | 0 | 0 |
| 0 | partition | 0.869 | 1.726e+09 | 0.451 | 0.303 | 18 | 4 | 1 |
| 0 | gated | 0.159 | 0.159 | 0.012 | 0.012 | 0 | 0 | 0 |
| 0 | compensation | 1.152 | 1.523 | 0.959 | 1.092 | 11 | 3 | 1 |
| 0 | rotated | 0.341 | 0.354 | 0.097 | 0.180 | 14 | 0 | 1 |
| 1 | expansion | 0.688 | 0.660 | 0.163 | 0.167 | 25 | 0 | 0 |
| 1 | partition | 1.134 | 1.203 | 0.533 | 0.130 | 18 | 4 | 0 |
| 1 | gated | 0.185 | 0.185 | 0.016 | 0.016 | 0 | 0 | 0 |
| 1 | compensation | 0.995 | 0.890 | 0.636 | 0.541 | 15 | 2 | 0 |
| 1 | rotated | 1.092 | 1.082 | 0.397 | 0.386 | 17 | 1 | 2 |
| 2 | expansion | 0.508 | 0.447 | 0.379 | 0.242 | 25 | 3 | 0 |
| 2 | partition | 1.155e+09 | 1.155e+09 | 0.379 | 0.168 | 21 | 1 | 0 |
| 2 | gated | 0.341 | 0.341 | 0.030 | 0.030 | 0 | 0 | 0 |
| 2 | compensation | 2.158 | 2.155 | 0.509 | 0.477 | 9 | 1 | 0 |
| 2 | rotated | 0.825 | 0.744 | 0.911 | 0.370 | 20 | 8 | 0 |
| 3 | expansion | 0.756 | 0.652 | 0.501 | 0.092 | 24 | 12 | 0 |
| 3 | partition | 0.784 | 0.706 | 0.700 | 0.217 | 26 | 11 | 0 |
| 3 | gated | 0.595 | 0.623 | 0.884 | 0.840 | 10 | 3 | 3 |
| 3 | compensation | 0.916 | 0.834 | 0.801 | 0.274 | 14 | 5 | 0 |
| 3 | rotated | 0.758 | 0.759 | 0.142 | 0.146 | 19 | 0 | 0 |
| 4 | expansion | 0.695 | 0.657 | 0.081 | 0.094 | 28 | 2 | 0 |
| 4 | partition | 0.577 | 0.458 | 0.436 | 0.173 | 17 | 9 | 1 |
| 4 | gated | 0.194 | 0.194 | 0.015 | 0.015 | 0 | 0 | 0 |
| 4 | compensation | 1.061 | 1.044 | 0.815 | 0.628 | 21 | 6 | 1 |
| 4 | rotated | 0.531 | 0.555 | 0.075 | 0.096 | 25 | 0 | 2 |
| 5 | expansion | 0.786 | 0.774 | 0.075 | 0.068 | 9 | 1 | 0 |
| 5 | partition | 0.669 | 0.656 | 0.153 | 0.143 | 21 | 2 | 2 |
| 5 | gated | 0.131 | 0.131 | 0.006 | 0.006 | 0 | 0 | 0 |
| 5 | compensation | 1.051 | 1.035 | 0.542 | 0.133 | 19 | 6 | 0 |
| 5 | rotated | 1.070 | 1.056 | 0.468 | 0.338 | 26 | 5 | 0 |
| 6 | expansion | 1.001 | 0.950 | 0.178 | 0.059 | 22 | 1 | 0 |
| 6 | partition | 0.687 | 0.695 | 0.272 | 0.280 | 27 | 0 | 0 |
| 6 | gated | 0.262 | 0.285 | 0.014 | 0.016 | 3 | 0 | 0 |
| 6 | compensation | 1.546 | 1.405 | 1.093 | 1.040 | 22 | 5 | 2 |
| 6 | rotated | 0.848 | 0.814 | 0.135 | 0.135 | 21 | 0 | 0 |
| 7 | expansion | 0.875 | 0.812 | 0.844 | 0.487 | 16 | 8 | 0 |
| 7 | partition | 1.290 | 1.275 | 0.402 | 0.419 | 19 | 1 | 0 |
| 7 | gated | 0.476 | 0.476 | 0.049 | 0.049 | 0 | 0 | 0 |
| 7 | compensation | 0.871 | 0.827 | 0.523 | 0.248 | 20 | 4 | 1 |
| 7 | rotated | 0.783 | 0.759 | 0.112 | 0.108 | 18 | 1 | 0 |

## Lean adjudication

- **(a) MISS.** Pooled budget Spearman .6677 < .75, and it moved DOWN from
  .7264 rather than up.
- **(b) MISS.** Passing repetitions 2 < 6, down from 4. Rep 2 (.7576 → .5273),
  rep 4 (.8303 → .6606) and rep 5 (.8061 → .6848) fall below the .75 per-rep
  bar; rep 7 newly crosses it (.6970 → .7818).
- **(c) MISS** under the pre-coded operationalization (fixed in the script
  docstring before any retrofit number was seen; the registration was verbal).
  All 8 reps contain corrected flips, so the degenerate fallback applied:
  graded Spearman(corrected count, delta-Spearman) = +.313 < .5. There is no
  concentration of improvement because there is almost no improvement — the
  sign of the association is weakly positive (heavier-corrected reps degrade
  LESS), which is the residue of the registered mechanism inside an overall
  degradation.

## Pivot adjudication

**NOT triggered.** The registered pivot ("Spearman moves < .01 → the
attribution deficit is independent of route contamination; return the item to
the M4-C queue unchanged") required near-zero movement; the observed movement
is −.0588. The outcome falls OUTSIDE both registered branches: the leans
anticipated improvement, the pivot anticipated indifference, and the
instrument returned a third state — significant movement DOWNWARD. Recorded
plainly, no post-hoc rescue: the attribution deficit is not independent of
route contamination; the contamination was a positive INPUT to the ordering
statistic. The C.3 item stays in the M4-C track as a NO-GO; what returns to
that track's queue is sharper knowledge, not a live retrofit thread — any
budget-formula redesign is out of this leg's registered scope.

## Mechanism (what the numbers show)

1. **The two-stage construction transfers.** Its arc-established effect
   reproduces on a battery it was never tuned on: D-zero flips 149 → 57
   (`return` selections 151 → 57), loop transport geometry up in all 5 worlds
   (partition .584 → .771, compensation .265 → .446, expansion .710 → .837,
   rotated .708 → .780, gated .872 → .877), creation Shapley share of loop
   loss nearly halves (.243 → .131), rank-arm geometries rise at every rank.
2. **The ordering statistic was flip-subsidized.** A D-zero flip puts an
   extreme value into BOTH the budget (creation numerator ≈ the full oracle
   path) and the realized loss, at the same row — automatic rank agreement.
   With flips removed, realized loss compresses (std .321 → .269; e.g.
   partition rep 1 loss .533 → .130, rotated rep 2 .911 → .370) while the
   linearized budget hardly moves (touched-row medians: total budget
   .825 → .776 as realized loss collapses .449 → .200 and creation Shapley
   halves .213 → .110). The remaining, cleaner regime is one the first-order
   budget ranks WORSE (expansion +.04 → −.36 within-world).
3. **Stage 1 fixes the D-zero channel, not name agreement.** Route-name
   mismatches RISE 455 → 513: the penalized selection swings mass to `gate`
   (461 feedback→gate transitions; `gate` count 452 → 902 vs oracle's 598),
   overshooting oracle name agreement while killing the `return` collapse.
   Same lesson as the arc: the flip channel and the route-name channel are
   different objects.

## Honest anomalies

- **Budget denominator pathology, pre-existing and now exposed.** The
  per-author budget denominator (norm of the oracle path response) is
  near-zero for isolated authors in partition: the original battery already
  contained a 2.31e9 view-row (rep 2 test, identical in both arms). Under the
  retrofit a SECOND such row appears (rep 0 partition: budget 0.869 →
  1.73e9) — a corrected author whose V2 route was D-zero (budget ratio ≈ 1 by
  construction: the numerator collapses to the oracle path itself) acquires a
  nonzero creation estimate whose deviation is huge relative to its tiny
  denominator, even as that world-rep's realized loss IMPROVES (.451 → .303).
  Spearman is rank-based, so the magnitude does not blow up the statistic,
  but the rank inversion it creates is real damage and is the mechanism in
  miniature.
- **17 broken flips.** The construction breaks 17 rows that V2 had right
  (worst single cell: gated rep 3, 3 corrected vs 3 broken) — the two-stage
  correction rate is 109:17, not clean-sheet.
- **Basis invariance identical to 15 digits between arms** (4.668e-10): the
  binding edge is a shared (choice/response) leg, so the check certifies the
  shared legs, not the two-staged creation leg specifically.
- **Compensation world improves** (+.23 → +.53) — the registered story is
  locally true in exactly one world, the one with the highest flip density
  per changed route; reported to keep the kill honest rather than absolute.

## Boundary

Finite synthetic decomposition on the frozen C.3 battery only. The retrofit
changes the discovered-side estimator construction, not the attribution
formula, targets, or worlds. `M4_C3_NO_GO_ERROR_ATTRIBUTION` remains the
decision of record under both constructions; this leg does not convert
M4-C.2 to a pass, identify personality, validate natural text, or reopen
M4-D. EXPLORATORY tier; no seal, no independent verification (operator
directive 2026-08-01).
