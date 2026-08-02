# SUICA M4-D Leg 14 — Discovery-Objective Displacement Reduction: the Quadratic-Basin Prediction Test

Tier: **EXPLORATORY** (open-exploration phase, operator directive 2026-08-01).
Registered before run: docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md,
"Leg 14 — discovery-objective displacement reduction" (2026-08-02, loop cycle
9, commit 693141d; ledger row M4-D.17). Script:
`scripts/run_suica_m4_d_displacement_leg14.py`. Artifacts:
`results/m4_d_discovery_displacement/`. Machinery imported from Legs 3/4/9/11;
anchors: Leg 9 `gap_swap_rows.csv` (rows), Leg 11 `partial_gates_*.json`
(per-rep displacement) and `gap_theta_rows.csv` (exponents), archived V2
`metrics.csv`.

**Question.** Leg 11 left one genuine object-level residual: discovery lands
a finite frame displacement from the oracle point and the paired gap grows
near-quadratically along it (gap ~ theta^1.8-1.9). If that displacement is
rep-level estimation noise, averaging constructions should shrink it — and
the gap should follow the basin law gap_fraction ~ alpha^exponent. This leg
tests both claims with two one-step constructions (consensus-of-8-frames;
split-half-agreement) and the registered per-point prediction check.

## Outcome in one paragraph

**0/3 leans; THE REGISTERED PIVOT FIRES in 3/3 worlds: the discovery
displacement is SYSTEMATIC OBJECTIVE BIAS, not rep noise.** Lean (a) misses
with the sign inverted — consensus does not merely fail to reduce
displacement, it INCREASES it in all three worlds (reductions
−.256/−.264/−.216; alpha_A ≈ 1.24-1.25 in every rep) and the consensus-refit
gap EXPLODES (pooled .680 vs gap_v2 .215): the 8 per-rep frames share a
COMMON bias direction, so averaging removes noise but not the bias, and the
Frechet mean lands farther from every rep's oracle point than the rep's own
discovery. The companion decomposition makes the mechanism explicit: the
discovered-frame cloud's center sits 12.0-13.8 quotient units from the
oracle-anchor cloud's center (a common offset ≈ 3/4 of the median per-rep
displacement 16.9-18.6 in norm), while the split-half arm certifies that
within-rep estimation noise contributes ~NOTHING — two independent
half-discoveries average to the same displaced point (alpha_B median
.97-1.00; never below .895; the two halves can sit 18 units apart and their
midpoint still lands no closer to the oracle). Lean (b) misses for
INAPPLICABILITY, not for prediction failure: material shrinkage (alpha <=
.90) almost never occurred (1 point in 48), so the basin test was largely
unevaluable; the one material point lands IN band (.63), and the loose
alpha<1 sensitivity puts 24/24 split-half points in the factor-2 band
(median factor .90-1.03) — consistent with the basin law, but in the
weakly-informative alpha≈1 regime. On the unregistered EXPANSION side the
law underpredicts: at alpha ≈ 1.25 the consensus gap runs ~1.8-2.1x above
alpha^exponent — the basin steepens beyond the well Leg 11 fitted (angles
<= 20°), path anisotropy again. Lean (c) misses: the best arm (split-half)
cuts the pooled gap only 4.6% (.2152 -> .2054). Registered hand-off executed:
objective redesign (beyond one-step moves) is DEFERRED as the arc's closing
open problem; the loop moves to fresh question mining.

## The closing open problem (stated crisply)

The discovery objective lands frames at a systematically displaced point in
frame space; the displacement is common across reps and unremovable by
averaging (consensus) or split-half agreement; characterizing WHICH term of
the objective produces the bias is the open item.

## Design as executed (implementation decisions stated)

- **Frame space and displacement metric.** Leg 11's Kendall size-and-shape
  quotient of stacked role frames S = [B_cal; B_sel; B_eval] (48 x W) under
  right-O(W); chordal distance d(A,B) = min_R ||A_pad − B_pad·R||_F. Per-rep
  d(swap_rep, v2_rep) reproduces Leg 11's persisted `procrustes_residual`
  with **max |diff| = 0.0** — the displacement coordinate is bit-continuous
  with the basin measurement. swap_rep = Leg 9's row-norm swap (oracle
  directions + the rep's own discovered norms), the t=0 oracle point.
- **Arm A mean algorithm.** Multi-start generalized-Procrustes (chordal
  Frechet) mean: one GPA run from each of the 8 rep frames, consensus =
  lowest Frechet objective (ties: lowest init). Two preflight facts forced
  this form and are recorded: the iteration contracts linearly at
  ~.9954/step (so the naive 1e-12-in-500 control was unreachable; runs use
  1e-11 in <= 50000, observed <= 4215 iterations), and the Frechet objective
  is MULTI-MODAL on these widely spread frames (8/7/8 distinct converged
  basins; two inits landed 4.67 apart). The basins are equal to ~0.3% in
  objective (spread 0.92-1.27 on 366-435) and the lean-(a) statistic is
  basin-insensitive: reduction ranges [−.2594,−.2511] / [−.2644,−.2553] /
  [−.2163,−.2090] across ALL basins per world. Verified on the manifold:
  fixed-point residual <= 1.0e-11; refit at the mean vs mean·R_random equal
  to 3.9e-13 (functional well-definedness, Leg 11's rotation gate).
- **Arm B.** Authors of all five condition panels split first/second half
  (the estimator's own `_author_split_features` unit); FULL discovery
  pipeline per half (8-candidate battery + selection + freeze + prototype
  transform); registered one-step symmetric shrinkage = chordal midpoint
  (both-side construction agrees to 1.4e-13; rotation gate 3.6e-13). Chart
  refusals: **0/48 halves refused**; family agreement 19/24 reps (5
  disagreements, e.g. global_isomap vs landmark_atlas, exactly where the
  half-frame distance is largest, 11.7-19.6).
- **Refits.** Canonical `_fit_hazard_candidate` + `_feedback_derivative`
  only (leg4's forced-route path; no local estimator copies in this leg);
  oracle-forced route, 1x r=0 panels, Leg 9 gap semantics.
- **Exponents.** Recomputed from Leg 11's persisted theta rows under Leg
  11's own aggregation: 1.8418 / 1.7638 / 1.8707, gated vs the registered
  printed 1.842/1.764/1.871.

## Displacement per arm (world medians over 8 reps)

| world | disp_v2 | disp_consensus | alpha_A | disp_split | alpha_B | lean-a reduction |
|---|---|---|---|---|---|---|
| expansion | 18.224 | 22.894 | **1.243** | 18.507 | 0.999 | **−.256** |
| compensation | 16.930 | 21.406 | **1.243** | 16.280 | 0.973 | **−.264** |
| rotated | 18.613 | 22.639 | **1.253** | 17.413 | 0.986 | **−.216** |

Lean (a) bar: reduction >= +.30 in >= 2/3 worlds — **MISS 0/3, sign
inverted**. Pivot bar: reduction < .10 in >= 2/3 worlds — **FIRES 3/3**.

## Paired gap per arm (medians; author-level view-means)

| level | gap_v2 | gap_consensus | gap_split |
|---|---|---|---|
| expansion | .2150 | .6977 | .1792 |
| compensation | .2102 | .7077 | .2087 |
| rotated | .2283 | .6512 | .2082 |
| **pooled (3 worlds)** | **.2152** | **.6803** | **.2054** |

Arm reductions vs gap_v2: consensus **−216.1%** (three times worse),
split-half **+4.6%**. Lean (c) bar >= 25% — **MISS** (best arm split_half,
.0456).

## The basin prediction (Arm C)

Per-point test: gap_fraction vs alpha^exponent, factor band [0.5, 2.0].

| arm | world | n | med alpha | med gap_fraction | med factor band | in band |
|---|---|---|---|---|---|---|
| consensus | expansion | 8 | 1.243 | 2.876 | 2.130 | 3/8 |
| consensus | compensation | 8 | 1.243 | 3.205 | 2.021 | 4/8 |
| consensus | rotated | 8 | 1.253 | 2.618 | 1.837 | 6/8 |
| split_half | expansion | 8 | 0.999 | 0.994 | 1.030 | 8/8 |
| split_half | compensation | 8 | 0.973 | 0.998 | 0.992 | 8/8 |
| split_half | rotated | 8 | 0.986 | 0.925 | 0.897 | 8/8 |

- **Registered lean (b) — MISS, dominated by inapplicability.** Primary
  shrinking points (alpha <= .90, stable denominators): 0 / 1 / 0 per
  world. Only compensation is evaluable (rep 4, alpha .895, gap_fraction
  .518, predicted .822, factor band **.63 — in band**), so exactly one
  world passes (< 2). The test the lean wanted mostly could not run because
  neither one-step construction produced material shrinkage. The single
  pass is one point; it is not evidence of the law by itself.
- **Loose sensitivity (alpha < 1, labeled, not adjudicated):** 4/5/5 points;
  median factor bands 1.030/.984/.902; all 24 split-half points in band.
  Consistent with the basin prediction, but this regime (alpha ≈ .9-1.0) is
  weakly informative — alpha^p ≈ gap_fraction ≈ 1 tolerates the band
  easily. The swap-baselined sensitivity variant tells the same story
  (medians .996/.998/.933).
- **Expansion side (unregistered direction, disclosed):** consensus points
  sit at alpha ≈ 1.19-1.35 — OUTSIDE the well Leg 11 fitted (theta <= 20° ~
  gap .19) — and the observed gap fractions (2.6-3.2) run ~1.8-2.1x ABOVE
  alpha^exponent. Outward from the basin the gap grows FASTER than the
  fitted power law: either the well steepens beyond its fitted radius, or
  the consensus direction is anisotropically expensive (Leg 10/11's path
  anisotropy). Either way, the quadratic-basin law is a local law of the
  well's interior, not an extrapolation license.

## Why consensus fails (companion decomposition, no adjudication weight)

| world | swap-cloud RMS spread | v2-cloud RMS spread | d(cloud centers) | median disp_v2 | target-motion floor alpha |
|---|---|---|---|---|---|
| expansion | 20.66 | 20.17 | 13.75 | 18.22 | 1.142 |
| compensation | 19.52 | 19.14 | 11.96 | 16.93 | 1.137 |
| rotated | 21.17 | 20.86 | 13.29 | 18.61 | 1.157 |

Three facts compose the mechanism:
1. **The targets move.** Each rep's truth is its own draw: the oracle-anchor
   (swap) cloud is as spread (~20 RMS) as the discovered cloud, and the
   median distance from a rep's anchor to the anchor consensus is ~114-116%
   of the rep's own displacement. Consensus-ACROSS-reps was therefore
   structurally incapable of showing a >= 10% reduction even for an
   unbiased discovery — the registered consensus statistic alone could not
   have separated bias from target motion.
2. **Discovery tracks its rep's truth in the moving directions.** Per-rep
   displacement (~17-19) is SMALLER than either cloud's spread (~20), and
   cross-rep v2-v2 distances (~28.6 ≈ sqrt(2)·20) look independent — so the
   rep-varying component of the discovered frame follows the rep-varying
   component of the truth. Averaging destroys exactly this tracking, which
   is why the consensus is FARTHER from every rep's oracle point
   (alpha_A ≈ 1.24) and its refit gap explodes to .65-.71.
3. **A common offset remains.** The two cloud CENTERS sit 12.0-13.8 apart —
   a systematic, rep-invariant displacement component (~3/4 of the median
   per-rep displacement in norm) that no amount of averaging removes. With
   Arm B showing within-rep noise ≈ nil, this is the direct geometric
   witness of the pivot's verdict: the displacement is a property of the
   discovery OBJECTIVE, not of the sample.

So the pivot fires as registered, and the verdict is SUPPORTED FOR THE RIGHT
REASON by the unregistered decomposition: systematic common offset + faithful
rep-tracking + negligible within-rep noise. The confound that the registered
statistic could not see (target motion) is disclosed and does not rescue the
noise hypothesis: split-half agreement is immune to target motion and still
moves nothing (alpha_B ≈ 1, gap −4.6%).

## Honest anomalies

- **Frechet multi-modality.** The chordal Frechet objective on the 8 frames
  has 8/7/8 distinct GPA basins (resolution 1e-6), all within ~0.3% in
  objective; the consensus is defined by the stated argmin rule and every
  adjudicated statistic is basin-insensitive (lean-a spread <= .008). The
  original single-start-plus-invariance-check design was replaced by the
  multi-start rule BEFORE any adjudicated output existed; both preflight
  facts are recorded in the script docstring.
- **alpha_B > 1 in 10/24 reps.** The midpoint of two half-discoveries often
  lands slightly FARTHER than the full fit — half-sample noise inflation
  offsetting the averaging gain; consistent with a noise contribution near
  zero, not merely small.
- **Split-half gap can beat v2 locally** (expansion rep 2: .152 vs .314;
  compensation rep 4: .102 vs .198) while the pooled effect stays 4.6% —
  rep-level scatter, no world-level rescue.
- **Family instability under halving.** 5/24 reps pick different chart
  families on the two halves without a single refusal — the candidate
  score's argmax is fragile exactly where the half-frames are far apart
  (distance 11.7-19.6), yet the midpoint's displacement is still ≈ disp_v2:
  even family-level discovery variance does not move the frame toward the
  oracle.
- **The one degenerate row** (Leg 9's) reproduces identically (flag equal,
  row NaN'd, counted).

## Faithfulness chain (all green, refused-not-warned)

| gate | value |
|---|---|
| V2 replay geometries (72 rows) | max 1.1e-16 |
| analytic D_true unit check | 1.7e-15 |
| full-data discovery rebuild vs context v2_basis | 0.0 |
| Leg 11 displacement anchor (24 reps) | 0.0 |
| Leg 9 swap-row anchor (t=0) | 9.7e-17 |
| Leg 9 v2-row anchor | 2.2e-16 |
| consensus rotation gate | 3.9e-13 |
| midpoint rotation gate | 3.6e-13 |
| GPA fixed-point residual | <= 1.0e-11 |
| exponent recomputation vs registered | 1.8418/1.7638/1.8707 vs 1.842/1.764/1.871 |

## Adjudication summary

| lean | bar | outcome |
|---|---|---|
| (a) consensus cuts displacement >= 30% in >= 2/3 worlds | reductions −.256/−.264/−.216 | **MISS (sign inverted)** |
| (b) basin band [0.5,2.0] where displacement shrinks, >= 2/3 worlds | 0/1/0 evaluable points; 1 world passes | **MISS (largely inapplicable)** |
| (c) best arm cuts pooled gap >= 25% | split_half +4.6% | **MISS** |
| PIVOT: reduction < 10% in >= 2/3 worlds | 3/3 (all negative) | **FIRES** |

Verdict: **DISPLACEMENT_IS_SYSTEMATIC_OBJECTIVE_BIAS**. Registered hand-off:
the objective-redesign item (beyond one-step constructions) is deferred as
the M4-D arc's closing open problem; the loop moves to fresh question
mining.

## Boundaries

Finite synthetic M4-C.2 worlds only; truth-referenced diagnostic; V1/V2
NO-GO decisions stand; the consensus and split-half frames are DIAGNOSTIC
constructions of this leg (the consensus consumes all 8 reps, the midpoint
consumes the full panel twice — neither is deployable estimator semantics);
no natural-text, personality, or clinical claim; no seal, no independent
verification (operator directive 2026-08-01).
