# V8 V3.7H.4D R1 Reference-Contrast Frontier Plan

Status: prospective repair protocol, frozen before full execution.

## Core correction

The absolute decomposition of total author score into \(A\) and the
author-constant projection of \(Q\) is not observation-only identifiable.
R1 does not attempt it.

R1 estimates a gauge-invariant reference contrast:

\[
\delta\pi=\pi^{(1)}-\pi^{(0)},
\qquad
\sum_c\delta\pi_c=0,
\]

\[
\Delta_u
=
C_{\delta\pi}(M)_u
=
\sum_c\delta\pi_c
\left(M_{uc}-\bar M_{\cdot c}\right).
\]

For the A/Q transformation \(Q'_{uc}=Q_{uc}-r_u\):

\[
C_{\delta\pi}(Q')=C_{\delta\pi}(Q).
\]

This identifies whether author position changes across two registered
condition references. It does not identify whether an absolute score
component should be named author trait or interaction.

## Independent-panel contrast

Two full-support reference measures are frozen at JSD .05 or .15.
Independent test panels produce:

\[
\widehat\Delta^{(a)}_u
=
\widehat\theta^{(a)}_u(\pi^{(1)})
-\widehat\theta^{(a)}_u(\pi^{(0)}),
\]

\[
\widehat\Delta^{(b)}_u
=
\widehat\theta^{(b)}_u(\pi^{(1)})
-\widehat\theta^{(b)}_u(\pi^{(0)}).
\]

The observation-only normalized contrast magnitude is estimated from
cross-panel energy:

\[
D_C
=
\frac{
\sqrt{
\max\left(
E_u\langle
\widehat\Delta^{(a)}_u,
\widehat\Delta^{(b)}_u
\rangle,
0
\right)
}
}{
SD_u(\widehat\theta^\star_u)
}.
\]

Author bootstrap intervals provide:

- near-contrast-kernel when one-sided 90% upper \(D_C<.10\);
- reference-sensitive when one-sided 95% lower \(D_C>.20\);
- unresolved between the two.

Oracle contrast is evaluation-only.

## Worlds

1. `additive`: new-detector and reference-contrast zero control.
2. `reference_shift`: common-reference score transport under acquisition
   shift.
3. `contrast_sensitive`: interaction aligned with \(\delta\pi\).
4. `contrast_kernel`: interaction projected into the registered contrast
   kernel.
5. `support_violation`: structural zero reference support.
6. `full_rank`: diffuse residual spectrum.
7. `minority_local`: sparse author-condition residual.
8. `aq_alias`: identical observations under alternative A/Q decomposition.

All score-relevance worlds use nonzero reference contrast. No classification
is attempted when \(\delta\pi=0\).

## Geometry-preserving detector null

R1 retains CRC, cross-panel low-rank concentration, and Higher Criticism, but
uses one shared wild-sign null:

1. retain each complete author-by-condition residual vector;
2. multiply the right-panel vector by an author-level Rademacher sign;
3. re-run the same row/column residualization after every draw;
4. preserve condition mask, condition covariance, and heteroskedastic
   geometry;
5. derive all three null statistics from the same 99 frozen draws;
6. Holm-adjust the three p-values at alpha .05.

This is a new detector and receives 1,000 additive controls per noise mode.

## Frozen decisions

Cell outputs:

- `NO_STRUCTURE_REFERENCE_STABLE`;
- `STRUCTURE_DETECTED_REFERENCE_CONTRAST_NEAR_KERNEL`;
- `STRUCTURE_DETECTED_REFERENCE_SENSITIVE`;
- `STRUCTURE_DETECTED_REFERENCE_EFFECT_UNRESOLVED`;
- `REFUSE_NONOVERLAP`;
- `CAUSE_UNIDENTIFIED_AQ`.

Primary gates:

- W0 simultaneous false-refusal upper below .05;
- W0 false reference-sensitive classification upper below .05;
- reference-shift RCG lower above .50, \(D^\star\) upper below .20, and score
  correlation lower above .90;
- support-violation refusal lower above .90 and invalid score output upper
  below .05;
- contrast-sensitive detection and sensitive-classification lower above .90;
- contrast-kernel detection and near-kernel classification lower above .90;
- contrast-kernel false-sensitive upper below .05;
- full-rank and minority-local non-low-rank detection lower above .90;
- A/Q alias `CAUSE_UNIDENTIFIED_AQ` lower above .95, specific attribution
  upper below .05, and identity error at most \(10^{-12}\).

Weak effect, JSD .05, and coverage .90 cells are sensitivity boundaries.

## Claim boundary

A pass would establish:

\[
\boxed{
\text{absolute A/Q allocation is not identifiable,
but cross-reference author response is identifiable under support}
}
\]

It would not establish a personality construct, real-text calibration,
diagnosis, clinical usefulness, or causal attribution.
