# V8 V3.7H.4D R2 Minority Information Frontier

Status: prospective internal discovery plan; R1 detector frozen.

## Question

H4D-R1 detected minority-local structure inconsistently because the random
10% allocation placed between roughly two and ten active authors in the
64-author test split. R2 asks whether failure is explained by the amount of
observable local information rather than by failure of the reference-contrast
core.

The registered information coordinate is

\[
\mathcal I_M
=
\sum_{p\in\{2,3\}}
\sum_{u\in M\cap T}
\sum_{c\in C_M}
\frac{n_{puc}\lVert Q_{uc}\rVert^2}{\sigma_{uc}^2}.
\]

A panel-aware sensitivity coordinate additionally uses
\(\sigma_{uc}^2/n_{puc}+\sigma_{\mathrm{panel}}^2\).
These are descriptive coordinates, not likelihood-ratio statistics.

## Frozen design

- same 256-author, 16-condition, 6-dimension, 4-panel world as H4D-R1;
- same 128/64/64 train/calibration/test split;
- fixed-support active test authors \(m\in\{2,4,8,16\}\);
- fixed-support active train/calibration authors \(2m/m\);
- a random-support validation arm draws \(4m\) authors from all 256, so
  realized test support follows a hypergeometric distribution;
- four active conditions, one drawn from each propensity/reference quartile;
- Gaussian and standardized heteroskedastic \(t_5\) noise;
- K=128 primary opportunity budget;
- unchanged R1 detector: shared author wild signs, 99 permutations, CRC,
  cross-panel rank-three ratio, Higher Criticism, Holm alpha .05.

The primary interaction is an RMS-standardized iid sparse block. The detector
then applies its frozen complete author/condition centering. R2 records:

\[
A_R=\frac{\lVert P_{64}Q_TP_{16}\rVert_F^2}{\lVert Q_T\rVert_F^2}
\]

and the share of centered energy that leaks outside the intended active block.
An `intrinsic_zero_sum` counterexample at \(m=4/8\) double-centers only inside
the active block and therefore does not leak under the detector projection.

## Two scaling arms

1. `global_share`: global interaction energy remains 20% of
   additive-plus-interaction energy. Local amplitude therefore changes with
   support size. This reproduces the ambiguity in the R1 gate.
2. `active_snr`: active-cell RMS is fixed at 15.0 times the **expected**
   registered panel-mean noise RMS at K=128. The constant approximates the R1
   nominal minority amplitude and is frozen before discovery. Realized counts
   are never used to scale the planted signal.

The two arms answer different questions and must not be pooled as if their
effect sizes were equivalent.

## Discovery and confirmation

Discovery uses 300 repetitions per support/arm/m/noise cell, 200 repetitions
per intrinsic-zero-sum counterexample cell, and 300 W0 repetitions per noise.
It estimates:

- omnibus detector power;
- CRC-or-HC power (historically named `non_low_rank_detected`);
- channel-specific power;
- power against \(\log(1+\mathcal I_M)\);
- the smallest \(m\) for which point power remains at least .93 for that and
  every larger support value in both noise modes.

The `CRC-or-HC` label is operational. It does not prove that the planted
geometry is non-low-rank.

Fresh confirmation is not run until the discovery result and independent
audit freeze `confirmation_active_test_authors`. Confirmation uses 1,000
fresh repetitions per noise/cell and requires:

- simultaneous W0 false-refusal upper bound below .05;
- simultaneous power lower bound above .90;
- the `active-SNR + fixed-support + iid-block + m=8` power lower bound to
  exceed .90 in both noise modes.

Discovery independently checks whether random-support power is predicted
within .05 by the fixed iid information curve. This check is not folded into
the narrow fresh confirmation.

If no \(m\) reaches the discovery criterion, R2 reports an unresolved
information frontier rather than tuning the R1 detector.

The intrinsic-zero-sum counterexample is not part of the \(m=8\)
confirmation claim. If comparable scalar information produces different
power under that geometry, the next experiment must replace a scalar
threshold with a geometry-aware information operator.

## Claim boundary

R2 can quantify the observation budget needed by the frozen detector in
registered synthetic worlds. It cannot show that a detected residual is a
personality trait, identify its semantic content, or guarantee sensitivity
to arbitrary local structures.
