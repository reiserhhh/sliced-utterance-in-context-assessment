# SUICA M4-D Leg 1 — Composition-Curvature Conjecture

Date: 2026-08-01
Tier: EXPLORATORY (open-exploration phase; operator directive 2026-08-01:
defensive machinery deferred; leans recorded in
`docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md` before this run; no
prospective seal, no independent verification pass)

## Decision

```text
M4_D_LEG1_CURVATURE_NOT_SUPPORTED_WALL_IS_ESTIMATOR_SIDE
```

All three registered leans MISS. The `M4_C2_NO_GO_CHART_TRANSPORT` wall
(atoms .77–.98, composite loop .6519) is not a holonomy/curvature phenomenon.
It is composition-amplified estimator error concentrated in the creation
feedback leg, plus a discrete hazard model-selection instability induced by
chart overspan. A clean negative: the registered conjecture was testable, was
tested on the exact V2 worlds, and the data refuse it.

## Registered conjecture and leans (verbatim from the plan)

Conjecture: per-atom transports T_i are chart-consistent up to gauge; a
composed loop accumulates a holonomy defect. Law: per-loop transport failure
is an increasing function of accumulated atom-pair non-commutation
sum_ij ||[T_i, T_j]||_F along the loop; near-zero-commutator loops transport
at atom-level rates.

- Lean (a): Spearman(commutator, per-loop error) >= .7 across worlds /
  replicates; pivot signal if < .3.
- Lean (b): path-ordered correction (estimate a connection, parallel-transport
  before composing) reduces loop error where (a) holds.
- Lean (c): in the world family where atoms genuinely commute, loops pass at
  atom-level rates.

## Machinery and faithfulness

Exact replay of the M4-C.2 V2 confirmation (config
`configs/m4_chart_ecology.json`, seed 271828183, same seed rule, same
generator, same chart fit, same per-author fitting flow copied verbatim from
`suica_core/m4_chart_ecology_estimator._one_author`) on the five
creation-active identifiable loop worlds x 8 repetitions x 16 authors x
{train,test} views. Faithfulness gate: recomputed per-world-rep
loop/choice/creation action geometries match
`results/m4_chart_ecology/metrics.csv` with maximum absolute difference
**1.1e-16** (`results/m4_d_curvature/v2_validation.csv`); the pooled
uncorrected loop geometry reproduces the wall at **.6519**.

The V2 loop kernel is L = D @ G @ C with exactly one chart-gauged seam:

- C: choice delta (chart x categories; chart-indexed rows);
- G: response-choice operator (response x chart; chart-indexed columns);
- D: creation feedback derivative (categories x response; **chart-free**).

Per-atom transports (oracle frame -> discovered frame, gauge group
diag(1, O), mass axis fixed): T_C by orthogonal Procrustes on C's whitened
rows; T_G by rank-restricted Procrustes on G's whitened columns; T_D = I
because D carries no chart index. Two of the three registered pair terms
(||[T_C,T_D]||, ||[T_G,T_D]||) are therefore **identically zero**, and the
accumulated sum reduces to the single C–G term, computed as the alternation
norm kappa := ||T_C T_G' − T_G T_C'||_F (the computable form for rectangular
partial isometries; zero iff the relative discovered-frame gauge is
symmetric). Note the structural constraint: G has only 2 response rows, so
T_G's identified plane is always rank 2 (all 1,280 view-rows), and discovered
widths overspan the oracle frame (12–13 vs 7; the loop-passing world
`history_gated_ecology` sits at 8).

Data: 1,280 view-level loops; 206 view-rows excluded from the primary as
degenerate (196 hazard model-selection flips where exactly one route has a
zero D leg — see profile — and 10 rows where both routes select `return`, so
both loops are structurally zero); primary unit = author-level loop
(train/test mean, matching the V2 audit convention), n = **562**.

## Lean (a) — MISS (knife-edge magnitude, wrong mechanism; no pivot trigger)

| statistic | value |
| --- | ---: |
| primary Spearman(kappa, e_loop), author-level loops pooled | **.6977** (bar .70) |
| view-level sensitivity | .7020 |
| sensitivity including flip rows | .6066 |
| per-world Spearman (expansion/partition/gated/compensation/rotated) | .431 / .567 / .248 / .265 / .391 |
| within-(world x rep) median Spearman (40 cells) | **.1030** (IQR −.054 to .269) |
| partial rank correlation given atom errors | .4222 |
| companion seam-defect Spearman | .5845 |
| companion joint-gauge-excess Spearman | .6092 |
| world-rep level: mean kappa vs mean e_loop | .6488 |
| world-rep level: mean kappa vs loop geometry | −.3036 |

The registered primary lands **.0023 below the bar** and the view-level
aggregation crosses it — a knife-edge on aggregation choice, adjudicated as a
MISS on the registered primary. The decisive fact is not the pooled number
but its decomposition: **within a fixed world-repetition the commutator does
not rank which authors' loops fail (median rho .10)**. The pooled .6977 is a
between-cell (ecological) correlation: worlds/reps with more gauge scatter
are also the ones with harder estimation (kappa vs D-leg error at world-rep
level: rho = .658). Between .3 and .7, so the registered pivot trigger
(< .3) is not fired either — but leans (b) and (c) below independently
discriminate the mechanism, and both refuse the curvature reading.

## Lean (b) — MISS (the connection correction does not help; it hurts)

Path-ordered correction: insert Omega = T_G T_C' at the single gauged seam,
L_corr = D @ G @ Omega @ C, per author per view (truth-open Procrustes
connection, diagnostic only).

| statistic | value |
| --- | ---: |
| median relative reduction of e_loop | **−.2815** (negative = worse) |
| Wilcoxon one-sided p (reduction > 0) | 1.0000 |
| pooled loop geometry, uncorrected -> corrected | .6519 -> .6470 |
| per-world corrected vs uncorrected | expansion .504/.516, partition .552/.577, gated .907/.915, compensation **.619/.567**, rotated .653/.684 |

No world where (a) holds at .7 exists, so the fallback (all worlds) is
reported. If the loop failure were seam holonomy, parallel transport across
the seam would recover oracle composition; instead the corrected loops are on
net slightly worse (only `selection_creation_compensation` improves, +.052).
The discovered C and G legs agree with each other in the discovered frame
better than each aligns to the oracle frame separately — the opposite of the
holonomy picture.

## Lean (c) — MISS (the intervention cannot move the commutator, yet loops improve anyway)

The generator has no commuting parameter, so a minimal variant was built on
`endogenous_creation_expansion` (reps 0–3): interpolate the planted creation
loading from the registered rank-1 outer(direction, [1, −.72]) (lambda = 0,
bit-identical to the registered world) to a norm-matched full-rank loading
(lambda = 1), per-author Frobenius norm preserved. Marginals held: generated
menu rate .283 -> .273, union rate .606 -> .601.

| lambda | mean kappa | loop geometry | creation geometry | flips (of 128) | mean e_loop |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.0 | 1.3772 | .5227 | .7993 | 36 | .7782 |
| 0.5 | 1.3737 | .5479 | .7683 | 29 | .7985 |
| 1.0 | 1.3825 | .6828 | .8074 | 22 | .7849 |

kappa is **flat** (drop −.005): full-rank creation loading does not make the
estimated transports commute, because the seam transports (T_C, T_G) are
determined by the choice and response legs, not by the creation loading —
the registered "commuting-atom family" is **not constructible** by the only
atom-level knob the loop offers (an honest construction failure, recorded as
such). What the intervention did move is the estimator: model-selection flips
fell 36 -> 22 and loop geometry rose .523 -> .683 at **constant commutator**
— a direct dissociation: loop transport improves while the registered
predictor does not change. Within the commuting family,
Spearman(kappa, e_loop) = .148.

## Where the loop error actually lives (the honest pivot profile)

1. **Hazard model-selection flip channel (dominant at the metric level).**
   196/1,280 view-rows (15.3%) select `return` under the discovered chart
   where the oracle route selects `feedback` (132) or `gate` (62); reverse
   direction 2. A flipped row has D = 0, hence a structurally zero loop and
   e_loop = 1 by construction. Flips per world: expansion 72, partition 53,
   rotated 38, compensation 28, **gated 5** — exactly the world ordering of
   the V2 loop wall (.516/.577/.684/.567/**.915**). At world-rep level,
   flip count predicts loop geometry at Spearman **−.8044**, far above kappa
   (−.3036), D-leg error (−.3114), or transform rank (−.3142).
2. **D-leg estimation error (dominant at the per-loop level).** Within
   world-rep cells, author loop error is ranked by the chart-free D leg's
   error (median rho **.6985**) and by the GC composite (.4059), not by the
   commutator (.1030). Pooled author-level: e_gc .8215, e_d .8031 vs kappa
   .6977. Median atom errors: e_C .847, e_D .425, e_G .131; median GC
   composite .437.
3. **Overspan mechanism (coherent with both).** Discovered charts overspan
   the oracle frame (widths 12–13 vs 7) in the four failing worlds; the
   hazard feedback block scales as width x response-dims, so overspan
   inflates the feedback parameterization, diluting the feedback signal —
   degrading D where feedback is kept and flipping selection to `return`
   where it is not. The one low-overspan world (gated, width 8, rank 7.6) has
   5 flips and passes at .915.
4. **Leg-swap attribution (medians, seam-corrected frames).** Uncorrected
   .640; seam-only correction .807 (worse); oracle-C swap .468; oracle-D swap
   .597; oracle-G swap .817. No single-leg substitution recovers atom-level
   transport; the seam itself is the least helpful place to intervene.

Alternative reading now on record: **the wall is estimator-side** — a
composition of (i) a discrete model-selection instability across charts and
(ii) variance amplification of the weakest leg under chart overspan, not a
gauge-geometric obstruction. Constructive (untested, unlicensed) implication
for a future defended phase: stabilize hazard model selection across charts
(select on physical actions rather than penalized logloss) and control chart
rank before composing; the lambda = 1 and gated-world contrasts predict both
would move the loop gate, the commutator law predicts neither would.

## Anomalies and honest notes

- The registered primary is knife-edge: .6977 (author-level) vs .7020
  (view-level) straddle the .70 bar; adjudication follows the registered
  per-loop unit (author-level, the V2 audit's train/test-mean convention).
  Neither reading survives the (b)/(c) mechanism tests.
- Two reverse flips (discovered `gate` vs oracle `return`) produce near-zero
  oracle loops and exploding relative errors; they are in the degenerate
  exclusion (their inclusion would only add kappa-independent noise).
- `sum_ij ||[T_i,T_j]||_F` degenerates to one term because D is chart-free;
  the law as registered was only ever testable on the C–G seam here.
- Procrustes transports are UV' estimators (approximate for the unbalanced
  G-side problem); reflections (det = −1 blocks) are not separated from
  rotations in kappa. Both caveats apply equally across all rows and cannot
  manufacture the within-cell null.
- Commuting-family rep 0 stays pathological at lambda <= .5 (geometry −.15)
  and only partially recovers at lambda = 1 (.431); the family means above
  include it.
- `choice_geometry` in the commuting family (~.23–.36) is noise by design —
  selection is inactive in `endogenous_creation_expansion`, so the V2 choice
  gate never read that world; it is reported only because the lean-(c)
  "atom floor" formula consumed it (the meaningful atom there is creation,
  .81 at lambda = 1, loop .68).

## Scope and claim boundary

Finite synthetic M4-C.2 worlds only. The transports consume oracle legs, so
everything here is a truth-open diagnostic — not an operational rescue of
chart transport, not a repair of the V2 NO-GO, and not a new gate. The V1 and
V2 NO-GO decisions stand unchanged. No natural-text, personality, emotion,
diagnosis, or clinical claim. EXPLORATORY tier; nothing here may be cited
above it.

## Artifacts

- script: `scripts/run_suica_m4_d_curvature_leg1.py`
- per-loop rows (1,664: 1,280 main + 384 commuting family): `results/m4_d_curvature/per_loop_metrics.csv`
- world-rep rows: `results/m4_d_curvature/world_rep_metrics.csv`
- V2 faithfulness check: `results/m4_d_curvature/v2_validation.csv`
- adjudication: `results/m4_d_curvature/decision.json`
