# SUICA V8 Behavior C2 Planted-World Report

## Decision

`V8_BEHAVIOR_C2_PLANTED_WORLD_PASS`

The behavior-v2.1 C2 method passed its final independent planted-world
technical validation. This establishes that a stable author response score
and an interpretable condition-response operator can be estimated as two
separate objects when conditions are shared, randomized, sufficiently
supported, and expressed in a common coordinate system.

It does not establish a personality, emotion, diagnosis, clinical, or
human-construct result.

## Registered Design

- 500 independent planted worlds from a previously unused seed block;
- 60 discovery, 20 calibration, and 80 confirmation authors;
- eight crossed conditions from a three-dimensional factorial basis;
- five behavior families and two independent halves;
- exactly six primary observations per author, condition, half, and family;
- 999 paired permutations with a fixed plus-one p-value rule;
- discovery-only baselines and scaling;
- calibration-only ridge selection;
- confirmation used once for the registered decision.

The planted response model is

\[
\Delta_{u,h,g}(c)=a_{u,h,g}+b_{u,h,g}^{\mathsf T}z_c,
\]

where \(z_c\) is the shared condition basis, \(a\) is an author-half
intercept, and \(b\) is the condition-response operator.

## Two Separate Tracks

### Stable Score

The scoring track uses the raw fixed-quota link-response surface. Ridge is
selected on calibration same-author AUC, while centering and scaling are
frozen from cross-fitted discovery estimates. Author-specific standard error
is not a score coordinate.

The score supports only this claim:

> Under a fixed shared-condition design, the same author's response
> configuration is more similar across independent halves than another
> author's configuration.

### Operator Inference

The inference track uses an unpenalized Firth binomial link estimator with
discovery-fitted condition offsets, analytic Schur covariance, information
condition checks, and fail-closed confidence intervals.

It supports only this claim:

> In the registered logistic planted world, the author-specific link-scale
> response operator can be recovered with calibrated uncertainty.

The probability-incidence surface remains a separate descriptive estimand.
It cannot replace the link-scale operator.

## Final Results

| Metric at SNR 0.50 | Soft | Binary |
| --- | ---: | ---: |
| Same-author score AUC | 0.9998 | 0.9513 |
| Pairing power | 1.000 | 1.000 |
| Median operator cosine | 0.9721 | 0.8426 |
| Author-distance Spearman | 0.9342 | 0.6596 |
| Recovery slope | 0.9996 | 0.9927 |
| Analytic CI coverage | 0.9501 | 0.9684 |
| Bootstrap-t CI coverage | not applicable | 0.9044 |
| Inference refusal rate | not applicable | 0.0244 |

The independent moment sensitivity estimator agreed with the binary primary
analysis: AUC 0.9381 and median operator cosine 0.8321. The descriptive
probability-incidence AUC was 0.9515.

## Falsification Battery

All 70 registered checks passed.

- C1 selection was strongly recoverable by its own score
  (binary AUC 0.9918), while the C2 score remained null (0.4991).
- Null, intercept-only, and unstable-operator mean AUC intervals contained
  0.50, and their one-sided type-I upper bounds were at most 0.03.
- Fixed-quota scoring remained null under C1-driven information imbalance
  (AUC 0.5007).
- SE-only coordinates were author-identifying, confirming that uncertainty
  cannot be included in the score.
- Numerator shuffling returned the score to chance.
- Private, unique, insufficient-overlap, and half-shuffled condition
  coordinates refused numeric C2 output.
- Extreme prevalence retained a stable score (AUC 0.9434) while correctly
  refusing 99.26% of operator inferences.
- Full covariance whitening was non-inferior as a diagnostic but was not
  promoted over the simpler fixed-quota score.

## Interpretation

This result closes the mathematical planted-world question that remained
after Reddit exact-condition support failed. It demonstrates that the C2
object is recoverable under an identified design and that C1 choice,
author-specific precision, and condition-coordinate artifacts do not explain
the registered primary score.

The result does not solve the empirical behavior-v2.1 gate. Blind human
observer accuracy remains unmeasured, Reddit supports joint/C1 but not exact
C2, and the available MEPS material is only a procedure pilot. A future
fixed-condition human design must independently validate the behavior
ontology, repeatability, missingness process, and psychological meaning.

## Artifacts

- `results/v8_behavior_c2_planted_world/v2_final_20260725/decision.json`
- `results/v8_behavior_c2_planted_world/v2_final_20260725/world_summary.csv`
- `results/v8_behavior_c2_planted_world/v2_final_20260725/seed_metrics.csv`
- `results/v8_behavior_c2_planted_world/v2_final_20260725/report.md`
- `results/v8_behavior_c2_planted_world/v2_final_20260725/run_manifest.json`
