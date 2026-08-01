# SUICA M4-D Leg 2 — Relation-to-Individual Bridge (rigidity index)

## Decision

`M4_D_LEG2_R_TO_V_BRIDGE_PARTIAL`

Leans (b) and (c) HOLD; lean (a) MISSES its registered .90 bar at pooled
AUC .8691. The miss is structural and localized (conservative refusal band
plus one knife-edge label cell), not a failure of the designed-null refusal:
zero false licenses in 200 group-only worlds. Tier: OPEN-EXPLORATION
(operator directive 2026-08-01); nothing here may be cited above EXPLORATORY.

## Question

The program-wide pattern is that signal lives in `R` and dies in `V`
(E4/P6 author alignment; F18: motion structure real, person parameters not
licensed). The V8 type system forbids silent `R -> V` conversion but never
built the licensed version. This leg asks: under what conditions, computable
from an observed relation field `R_uv` alone, does `R` determine individual
coordinates `V_u` up to gauge — and can that criterion refuse the
vanishing-individuality trap (high author AUC, zero individual structure)?

Formal frame: Euclidean distance geometry / Gram completion. `R` is treated
as a noisy squared-distance (or similarity) field; identifiability =
rank + noise + anchoring; rigidity gives the obstruction language.

## The index (definition, from observed R alone)

Let `B = -1/2 J R J` (doubly centered Gram candidate), eigenvalues
`lambda_1 >= ... >= lambda_n`.

1. **Noise floor / rank condition**: `lambda_floor = |most negative
   eigenvalue|` (a Euclidean configuration has PSD centered Gram; the
   negative spectrum is a noise-scale estimate). Selected rank
   `r = #{lambda_i > 2 * lambda_floor}`, capped at 8. No qualifying
   eigenvalue -> `NO_STABLE_RANK`, index 0.
2. **Spectral margin (gap condition)**:
   `margin = (lambda_r - lambda_{r+1}) / (lambda_r + lambda_{r+1})`
   in [0,1]; Davis–Kahan: the rank-r subspace is stable only while the
   perturbation is small against the gap.
3. **Stress-stability probe (coordinate condition)**: embed by classical
   MDS at rank r; estimate the residual noise scale of `R` against the
   rank-r model (floored at 2% of the field RMS); 12 times: re-measure
   `R + noise-matched symmetric perturbation`, re-embed, gauge-align
   (similarity Procrustes) to the unperturbed embedding, and score the
   fraction of authors whose perturbed coordinate is still nearest to
   their own original coordinate. `stability` = mean identity-preservation
   rate. This is the computable stand-in for local rigidity: group-only
   fields fail it because same-group coordinates are interchangeable.
4. **Rigidity index** = `margin * stability`. License `R -> V^(r)` iff
   index >= tau = 0.5; refuse otherwise (`LOW_RIGIDITY`).

Gauge: any licensed `V` is defined only up to rotation, reflection,
translation, and isotropic scale. Anchoring can never come from the field
itself; a downstream consumer must be gauge-covariant or supply an external
reference frame.

## Frozen design

- module: `suica_core/m4_relation_bridge.py`; script:
  `scripts/run_suica_m4_d_relation_bridge_leg2.py`; seed `20260801`;
  20 replicates per cell; 600 worlds total; runtime ~11 s.
- Pre-fixed before the battery: label margin ratio `0.5` (a world is
  reconstructable only if the gauge-aligned MDS error at the ORACLE rank
  beats the median within-block permuted-truth error by a factor of two);
  license threshold `tau = 0.5`; floor multiplier `2.0`; probe replicates
  `12`; probe floor `2%`; permutation draws `24`; gap-close margin for
  lean (c) `0.25`; rank cap `8`.
- Disclosed pilot contact: a 3-seed placement pilot was run before
  freezing. It informed (i) the noise-grid extension to 2.5 so the
  battery straddles the label flip, and (ii) the composition rule
  `margin * stability` instead of `sqrt(margin * stability)` after the
  sqrt form left the group-only refusal margin thin at the easiest null
  cell (.469 vs tau .5). The two forms order identically (monotone
  transform), so lean (a)'s AUC is unaffected by that choice; only the
  tau operating point moves. Lean margins themselves were not touched.
- World battery (planted n=80 authors, latent rank 3, 4 groups;
  fields = exact squared-distance matrix + `noise * rms_offdiag`
  symmetric Gaussian; two independent fields per world, index computed
  on field one only):
  - `individual`: true low-rank per-author coordinates; noise grid
    {.02, .05, .1, .2, .35, .6, 1.0, 1.5, 2.5} x 20.
  - `group_only`: every author exactly on its group centroid — the
    pairwise analogue of the `v8_vanishing_individuality` designed null;
    same grid x 20.
  - `mixed`: centroids + within-group-centered offsets at epsilon
    {.1, .2, .4} x noise {.05, .2, .6} x 20.
  - `c2_group_only` / `c2_joint` (eps .5, 1.5) x 20: fields built from the
    ACTUAL `simulate_hierarchical_c2_world` machinery (160 authors,
    binomial surfaces -> empirical logits, condition-centered per
    author/half/family to remove intercepts, one field per half).
    Faithful-analogue statement: the C2 simulator emits per-author
    response surfaces, not pairwise fields, so the planted families use a
    direct latent-configuration analogue and the C2 fields are carried as
    a fidelity check, per the plan's instruction to say so.

## Results

Individual-family noise profile (means over 20 replicates):

| noise | margin | sel. rank | stability | E_rec | E_ratio | label rate | licensed |
|---|---|---|---|---|---|---|---|
| .02 | .948 | 3.0 | 1.000 | .009 | .009 | 1.00 | 1.00 |
| .05 | .872 | 3.0 | .999 | .023 | .023 | 1.00 | 1.00 |
| .10 | .776 | 3.0 | .996 | .045 | .046 | 1.00 | 1.00 |
| .20 | .576 | 3.0 | .961 | .092 | .093 | 1.00 | .85 |
| .35 | .413 | 2.8 | .802 | .159 | .161 | 1.00 | .00 |
| .60 | .213 | 1.7 | .275 | .278 | .281 | 1.00 | .00 |
| 1.0 | .042 | 0.2 | .015 | .473 | .479 | .75 | .00 |
| 1.5 | .000 | 0.0 | .000 | .705 | .713 | .00 | .00 |
| 2.5 | .000 | 0.0 | .000 | .875 | .886 | .00 | .00 |

Group-only refusal (the trap):

| family | n | refusal rate | median index | max index | median author-all AUC | median within-group AUC | median E-ratio |
|---|---|---|---|---|---|---|---|
| planted `group_only` | 180 | 1.000 | .0747 | .2680 | .8366 | .4976 | 1.000 |
| `c2_group_only` (v8 machinery) | 20 | 1.000 | .0040 | .0101 | .8963 | .5775 | 1.000 |

(Original v8_vanishing_individuality headline for comparison:
author_all_auc .8644, author_within_auc .5001.)

Mixed family: label rate moves .00 -> 1.00 across (epsilon, noise) exactly
as an epsilon ladder should; within-group author AUC rises .50 -> .93 with
epsilon; the index tracks (cell medians .06–.65).

C2 joint worlds (detection vs estimation): at eps 1.5 the individual share
of the planted response is .832 and within-group author AUC across halves
is .9933 — identity is nearly perfectly detectable — yet the oracle-rank
reconstruction only reaches E-ratio .6575 (fails the 2x margin) and the
index refuses (median .0170). At trials=6 measurement granularity the field
supports author DETECTION but not coordinate ESTIMATION. This is the F18
pattern ("structure real, person parameters not yet licensed") reproduced
in a fully controlled setting.

License confusion at tau = .5 (600 worlds): 116 licensed & reconstructable,
8 licensed & not (all in the knife-edge cell below), 97 refused but
reconstructable, 379 refused & not. Empirical false-license rate
8/387 = .021 overall and 0/200 on group-only worlds; miss rate on
reconstructable worlds 97/213 = .455 — the bridge is refuse-biased, as a
license should be.

## Lean adjudication

- **Lean (a) — MISS.** Registered: rigidity index separates reconstructable
  from non-reconstructable worlds with AUC >= .90 (ground truth = beat the
  within-block permuted-truth baseline by the pre-fixed factor 2). Result:
  pooled AUC **.8691** (individual-family .9439, mixed .8847, planted-only
  pooled .8578). Localization (descriptive, not re-adjudication): among the
  512 worlds where any rank is certifiable from R (selected rank >= 1) the
  AUC is .9055; the shortfall is (i) the hard-zero refusal band — at noise
  1.0, 75% of individual worlds still carry label 1 while the rank test
  already returns 0 (14 label-1 worlds with index exactly 0), ranking them
  below cleanly-refused group-only worlds with nonzero indices — and
  (ii) the mixed eps=.1/noise=.05 cell whose mean E-ratio is .502, i.e.
  sitting exactly on the pre-fixed label margin (cell label rate .55); all
  8 false licenses are that one cell (E-ratios .665–.784). Label-margin
  sensitivity (descriptive only): AUC .929 at margin .40, .869 at the
  registered .50, .787 at .70 — the index encodes a STRICTER notion of
  reconstructability than the registered 2x criterion. The registered lean
  is adjudicated on the registered margin: MISS.
- **Lean (b) — HOLD.** In group-only worlds the index refuses 200/200
  (planted max index .268, machinery max .0101, both far under tau .5)
  while author-all AUC stays high (medians .8366 / .8963 >= .80) and
  within-group AUC stays at chance (.4976 / .5775). The index is not fooled
  by the vanishing-individuality trap; the E-ratio is pinned at 1.000 by
  within-block permutation invariance, confirming zero individual
  identifiability in the label sense.
- **Lean (c) — HOLD.** Qualitative EDM-perturbation behavior: the
  reconstruction-error knee (max change of log-log slope) sits at noise
  .35 and the spectral gap closes (mean margin < .25) at noise .60 —
  adjacent grid points (pre-fixed rule: within one step). Reconstruction
  error grows gently while the gap is open and accelerates as it closes,
  with rank collapse (3 -> 2 -> 0) over the same band.

## The typed bridge (what this licenses)

The V8 type system reserved but never built the licensed `R -> V`
conversion. This leg supplies it as an executable gate:

- `R -> V^(r)` is **PERMITTED** only when the rigidity index
  (`margin * stability` at the auto-selected rank) clears tau = .5; the
  output coordinates are licensed **only up to gauge** (rotation,
  reflection, translation, isotropic scale) and only at rank r. Anchoring
  is external by construction: nothing in `R` can fix the frame.
- Otherwise the conversion is **REFUSED** (`NO_STABLE_RANK` /
  `LOW_RIGIDITY`). Group-only fields are the canonical refusal: their `R`
  determines a group configuration (an R/P-level object), and any
  per-author `V` read off them is gauge-fake — the refusal is the type
  law made computable.
- The license is deliberately conservative at tau = .5 (empirical
  operating point tpr .545 / fpr .021; ROC-optimal Youden threshold .230
  with tpr .761 / fpr .054 is recorded for calibration but NOT adopted —
  it is post-hoc). What the license does NOT do: certify psychological
  meaning of the coordinates, fix a reference frame, or transfer to real
  corpora without the deferred defense phase.

## Honest anomalies

1. The lean (a) miss is structural, not sampling noise: the index answers
   "is the rank certifiable and are the coordinates re-measurement-stable"
   while the label answers "does oracle-rank MDS beat permuted truth 2x";
   the two disagree exactly in the band where partial global shape
   survives after the rank becomes invisible from R alone.
2. All 8 false licenses come from one cell whose truth label is itself at
   the margin (mean E-ratio .502 vs margin .50) — a knife-edge artifact of
   the binary label, not a trap failure. Zero false licenses on designed
   nulls.
3. C2-machinery fields: the auto rank hits the cap (8) with near-zero
   margin because the empirical-logit noise is heteroscedastic and the
   negative-spectrum floor underestimates the positive noise tail — the
   refusal is right, but the rank selector is not calibrated for
   heteroscedastic fields. Flagged for the defense phase.
4. `c2_group_only` within-group AUC is .5775 (slightly above chance):
   residual intercept leakage through the finite-trial (n=6) empirical
   logit — an imperfection of the analogue construction, disclosed; it
   does not affect the refusal or the label (E-ratio pinned at 1.0).
5. Pilot contact disclosed in Frozen design: grid placement and the
   product composition were chosen after a 3-seed pilot; the composition
   choice cannot move AUC (monotone), and no lean margin was altered.

## Boundary

EXPLORATORY tier. Synthetic planted worlds only; no natural text, no
personality, no clinical claim; no prospective seal and no independent
verification pass (operator directive). The bridge gate itself
(`rigidity_report`) is ready to be pointed at the program's real relation
fields (E4/P6 alignment matrices, V8 bridge fields), but any such run is a
new registered step, and tau = .5 remains provisional until the defense
phase calibrates it on fresh worlds.

## Artifacts

- `suica_core/m4_relation_bridge.py`
- `scripts/run_suica_m4_d_relation_bridge_leg2.py`
- `results/m4_d_relation_bridge/relation_bridge_worlds.csv` (600 per-world
  rows)
- `results/m4_d_relation_bridge/decision.json`
- `tests/test_m4_relation_bridge.py` (9 tests; suite collection intact,
  959 tests collected)
