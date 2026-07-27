# V8 Reliability Spectrum and Resolution Filtration V3.7G

Canonical decision:
`V8_RELIABILITY_SPECTRUM_V37G_PASS_CORE_OBSERVABLE_SPECTRUM`

Independent ruling: `PASS_WITH_CAVEATS` for the registered **NMSE** synthetic
experiment.

The implementation and frozen config use normalized mean squared error
(NMSE). Two sealed prose documents incorrectly call that quantity NRMSE.
Those sealed files remain unchanged; the post-confirmation correction is
recorded in
`docs/V8_RELIABILITY_SPECTRUM_V37G_POST_CONFIRMATION_ERRATUM.md`.

## Question

V3.7G tested whether an externally normed SUICA profile should delete every
low-energy coordinate, or instead estimate a reliability spectrum while
retaining an auditable unresolved channel. It also tested whether an
observable-only error protocol could provide a bounded measurement-error
region without using evaluation truth during fitting.

No text, psychological labels, or real author identifiers were read. The
result is a synthetic mechanism result, not personality validity.

## Frozen design

The prospective confirmation used one canonical seed and 60 independent
repetitions. Every repetition contained eight 48-dimensional planted worlds
at event budgets 64 and 256, with four disjoint author panels:

- 256 external-reference authors;
- 128 calibration/selection authors;
- 384 interval authors, split 192/192 into map-fit and radius panels;
- 96 evaluation authors.

Hard-rank, Wiener, power, and monotone-spline estimators competed by
calibration-only cross-validation. The primary hard comparator was the
CV-minimum-risk hard estimator. Synthetic truth was scorer-only.

## Canonical results

All 20 frozen decision checks passed.

| Registered result | Confirmation estimate |
| --- | ---: |
| Exact-rank excess NMSE versus hard | -0.0438 [-0.0470, -0.0406] |
| Dense-tail NMSE reduction versus hard | 28.94% [28.51%, 29.36%] |
| Broken-spectrum NMSE reduction versus hard | 20.69% [20.14%, 21.23%] |
| Worst-world oracle regret | 0.00957 [0.00743, 0.01191] |
| Permutation effective df | 0.0227 [0, 0.0682] |
| Permutation residual AUC | 0.4936 [0.4857, 0.5013] |
| Exact-rank latent coverage | 0.9601 [0.9516, 0.9681] |
| Dense-tail latent coverage | 0.9589 [0.9509, 0.9660] |
| Broken-spectrum latent coverage | 0.9571 [0.9509, 0.9635] |
| Slow-decay latent coverage | 0.9661 [0.9587, 0.9731] |
| Core interval availability | 1.000 |
| State-alias interval refusal | 1.000 |
| Reference-shift interval refusal | 1.000 |
| Score + unresolved reconstruction error | 1.55e-15 |

All 3,360 registered RNG streams were unique. The 960 metric rows and 28,800
candidate rows matched the frozen design. The parent and V3.7G prospective
seals passed.

The informative-precision secondary world covered at 0.9981. This is not an
extra success: it is an efficiency failure showing that the current
homoskedastic radial map becomes overly conservative under author-dependent
precision.

On a square-rooted normalized-error scale, the point reductions would be
approximately 15.71% for dense-tail and 10.94% for broken-spectrum. V3.7G
therefore makes no NRMSE-gate claim.

## Mathematical result

At a fixed event budget, the fitted profile is

\[
\widehat G_u
=
\widehat\mu_0
+W_m(X_u-\widehat\mu_0),
\]

where \(W_m\) is selected from reliability-spectrum operators without
evaluation truth. Its complement is retained:

\[
R_u^{(m)}
=
(I-W_m)(X_u-\widehat\mu_0).
\]

The canonical reconstruction verifies

\[
X_u-\widehat\mu_0
=
(\widehat G_u-\widehat\mu_0)+R_u^{(m)}
\]

to machine precision. Therefore a coordinate can be weakly scored at the
current resolution without being declared noise or destroyed.

For uncertainty, sessions 1/2 define the score, sessions 3/4 define an
independent proxy, one interval half estimates a measurement-error radial
map, and the other half supplies an order statistic. With 192 radius authors,
the registered 95% content / 95% confidence order is 188 and its achieved
confidence is 0.96554.

The strict nonparametric guarantee applies only to the mapped proxy-error
radius. Its transfer to latent author error is model-assisted and was
empirically supported only in the four registered Gaussian core worlds. It
is not a per-author conditional confidence interval.

## Theory update

V3.7G supports four narrow upgrades.

1. SUICA should treat reliability as continuous and resolution-dependent,
   not divide the vector space once into signal and disposable noise.
2. Hard truncation is not a universal baseline: smooth operators materially
   reduce risk in dense and broken spectra without harming the exact-rank
   control.
3. The unresolved channel is part of the measurement record. It may contain
   stable low-energy author structure, state, reference error, or event error
   and must be resolved by later designs rather than renamed.
4. When state and stable author structure are aliased, or when the reference
   population is transported without calibration, the correct output is
   refusal rather than an overconfident score region.

The confirmation does not validate the “resolution filtration” claim across
budgets. The 64- and 256-event panels are not nested observations, so
martingale coherence and pathwise uncertainty contraction remain theoretical
requirements for a later experiment.

## Remaining limits

- All successful latent-coverage claims are model-assisted Gaussian planted
  worlds.
- The four world-specific 95% coverage intervals are marginal, not a
  simultaneous family-wise 95% statement.
- Informative precision causes severe overcoverage and needs an
  author-conditional error model.
- Reference and model-selection uncertainty are not fully propagated.
- Refusal is triggered by registered design metadata, not discovered
  automatically from observations.
- The shift-transport check is weak: all budget-256 shift cells selected the
  identity hard-rank-48 operator, making direction and amplitude recovery
  algebraic in this confirmation.
- The seal is hash-consistent and predates the result on the local
  filesystem, but the dirty repository and untracked V3.7G files do not
  provide an independent public timestamp.
- Real-text existence, cross-language behavior, personality meaning,
  clinical validity, and individual interpretation remain untested.

## Reproducibility

Canonical artifacts:
`results/v8_reliability_spectrum/v37g_confirmation_20260726/`

Prospective seal SHA-256:
`c9ca3c4e456e5ef3ffc4ad086fbd577e21b0f3befd5d726694178680ceb28ddb`

The canonical confirmation was run once. It must not be retuned or rerun in
response to this result.
