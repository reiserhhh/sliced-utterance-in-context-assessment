# V8 Reliability Spectrum V3.7G Confirmation Plan

## Purpose

Freeze and test the V3.7G reliability-spectrum estimator and its
model-assisted 95% content / 95% confidence measurement-error tolerance
ball on a fresh canonical seed.

This confirmation does not read text, psychological labels, or synthetic
truth during estimator selection or tolerance-radius construction.
Synthetic truth is scorer-only.

## Frozen design

- 60 independent repetitions;
- 48 profile dimensions;
- event budgets 64 and 256;
- 256 external-reference authors;
- 128 calibration authors;
- 384 interval authors, split 192/192 into fit and radius panels;
- 96 evaluation authors;
- four technical sessions;
- CV-minimum-risk hard rank as the primary hard comparator;
- hard, Wiener, power, and monotone-spline candidate families;
- 1,000 fit-author bootstrap replicates for every registered tolerance ball;
- exact-rank, dense-tail, broken-spectrum, author-permutation, state-alias,
  slow-variance-decay, informative-precision, and reference-shift worlds.

Only exact-rank, dense-tail, broken-spectrum, and slow-variance-decay worlds
enter the core latent-coverage gate. Informative precision is a secondary
heteroskedastic efficiency audit. State alias and uncalibrated reference
shift must refuse intervals.

## Frozen primary gates

- exact-rank excess NRMSE upper 95% bound at most 0.01;
- dense-tail reduction lower 95% bound at least 0.20;
- broken-spectrum reduction lower 95% bound at least 0.15;
- worst-world regret upper 95% bound at most 0.015;
- author-permutation effective-df upper 95% bound at most 2;
- author-permutation residual-AUC CI wholly inside [0.47, 0.53];
- every core world's repetition-cluster coverage CI wholly inside
  [0.92, 0.98];
- 100% core tolerance-ball availability;
- 100% state-alias and reference-shift interval refusal;
- planted-shift operator direction lower 95% bound at least 0.98;
- planted-shift operator amplitude CI wholly inside [0.95, 1.05];
- maximum score-plus-unresolved reconstruction error at most 1e-10.

Each publishable tolerance ball independently refuses when the radial map,
fit bootstrap, or pair-swap stability gates fail. No gate may be changed
after the prospective seal.

## Interpretation boundary

A pass supports only an externally normed, calibration-selected,
information-conserving profile estimator in the registered Gaussian
profile worlds, plus model-assisted latent coverage of a tolerance ball in
the four core worlds.

It does not establish:

- real-text existence;
- personality or clinical validity;
- distribution-free latent coverage;
- per-author conditional confidence;
- automatic state/shift detection;
- universal cross-budget filtration coherence;
- that every token contains psychological information.

## Failure rule

Any failed integrity, control, uncertainty, or estimator gate is reported
as the corresponding `STOP` or `REFUTE` status. The canonical seed is run
once. A failed result may motivate a separately named future experiment,
but V3.7G itself is not retuned or rerun.
