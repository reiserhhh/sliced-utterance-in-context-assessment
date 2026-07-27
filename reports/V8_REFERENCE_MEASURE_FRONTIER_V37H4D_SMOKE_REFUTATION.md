# V8 V3.7H.4D Smoke Refutation

Date: 2026-07-26

Decision:
`V8_REFERENCE_MEASURE_FRONTIER_V37H4D_SMOKE_REFUTED_IDENTIFIABILITY`

The full discovery was not run.

## What the smoke test found

The original H.4D plan attempted to classify a detected residual as
score-relevant or near-kernel using:

\[
\frac{
E_u\left\|
\sum_c\pi^\star_cR_{uc}
\right\|^2
}{
E_{u,c}\|R_{uc}\|^2
}.
\]

However, the residual operator first removed author and condition means:

\[
R
=
P^\perp_{\mathrm{author}}
P^\perp_{\mathrm{condition}}M.
\]

With the same reference used for author centering:

\[
T_{\pi^\star}(R)=0
\]

by construction. The ratio was therefore near zero for additive,
noncentered, full-rank, minority-local, near-kernel, and reference-shift
worlds. It did not measure an empirical property.

The 99-permutation preflight exposed the failure directly: multiple
non-near-kernel worlds were labeled
`STRUCTURE_DETECTED_SCORE_NEAR_KERNEL`.

## Identifiability theorem

For any author vector \(r_u\):

\[
A'_u=A_u+r_u,
\qquad
Q'_{uc}=Q_{uc}-r_u
\]

produces:

\[
A'_u+Q'_{uc}=A_u+Q_{uc}.
\]

Therefore:

- total author score under a fixed reference can be identified under support;
- the absolute contribution of \(Q\) to that score cannot be separated from
  \(A\) using observations alone;
- oracle interaction score fraction is a generator label, not an estimable
  quantity;
- the original near-kernel gate contradicted the registered A/Q alias world.

## What remains valid from smoke

- reference weighting reduced the JSD=.15 cross-environment discrepancy by
  approximately 79%-85% in the two smoke repetitions;
- W0 nSTE was approximately .09-.11 and score correlation .994-.996;
- structural support zeros were refused;
- full-rank effective rank was approximately 47.5;
- all split, seed, row, and numeric integrity checks passed.

These are engineering diagnostics, not promoted findings.

## Permutation-null warning

The original condition-permutation null can disturb centering constraints,
condition masks, and condition-specific variance. One W0 seed produced
Holm-adjusted .03 in both low-rank and HC channels. A 30-repetition
exploratory audit observed 2/30 familywise refusals in each noise mode. This
does not prove miscalibration, but it requires a geometry-preserving null and
a new 1,000-repetition-per-noise calibration.

## Repair

R1 replaces the unidentifiable absolute interaction projection with the
gauge-invariant reference contrast:

\[
C_{\delta\pi}(M)_u
=
\sum_c\delta\pi_c
\left(M_{uc}-\bar M_{\cdot c}\right),
\qquad
\sum_c\delta\pi_c=0.
\]

Since \(C_{\delta\pi}(r_u)=0\), this contrast is invariant to the A/Q gauge
transformation.

The full H.4D discovery is permanently closed. A separate R1 protocol is
required.
