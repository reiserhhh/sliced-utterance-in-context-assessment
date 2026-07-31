# V8 Opportunity-Filtered Concordance Spectrum

Status:
`OPENED_PANEL_RESIDUAL_SPECTRUM_FALSIFICATION`

## Purpose

The experiment distinguishes two statements that must not be conflated:

1. the full-dimensional M residual has positive same-author concordance;
2. that concordance can be represented by a small stable linear chart.

The first does not imply the second.

## Residual object

With the D0-frozen declared-profile map,

\[
Q_r=P_r+R_r,
\]

the residual spectrum uses

\[
B_R
=\frac{R_0^\top R_1+R_1^\top R_0}{2n},
\qquad
W_R
=\frac12(C_{00}^R+C_{11}^R),
\]

and solves

\[
B_Rv_j
=\lambda_j
\left(
W_R+\gamma\frac{\operatorname{tr}W_R}{d}I
\right)v_j.
\]

The raw-analysis gamma is frozen per corpus. D0 correspondence permutations
within observed context define a family-wise extreme-eigenvalue threshold.
D0 A/B halves must exceed a permutation affinity threshold and project
positively in both directions. Only then is the complete D0 subspace frozen
and tested in D1/D2.

## Decision taxonomy

- `FILTERED_LOW_DIMENSIONAL_SPECTRUM_REPLICATED`: at least one D0-stable axis
  has positive D1/D2 excess, maxT \(p<.05\), and positive bootstrap lower
  bounds.
- `FILTERED_CONCORDANCE_HIGH_DIMENSIONAL_OR_UNDERRESOLVED`: the omnibus
  residual relation exists, but no low-dimensional chart clears all gates.
- `FILTERED_OMNIBUS_NOT_REPLICATED`: no spectrum search is permitted.

The current panels have been opened. A pass is exploratory; promotion
requires fresh D3 authors. No result licenses a shared cross-corpus factor,
personality, emotion, cognition, causality, diagnosis, or clinical validity.
