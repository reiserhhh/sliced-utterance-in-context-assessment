# V8 Conditional Concordance Spectrum

## Purpose

The marginal-background quotient found that normalized signed concordance is
replicated in Essays and X-market while PANDORA is borderline and fails its
conjunction gate. This follow-up asks whether that concordance is carried by a
small, D0-reproducible subspace or by many weak directions.

This is an opened-panel exploratory compression audit. It cannot promote the
existing PANDORA result.

## Signed generalized operator

For background-quotient replicate matrices \(Q_0,Q_1\):

\[
B=\frac{1}{2n}(Q_0^\top Q_1+Q_1^\top Q_0),
\qquad
W=\frac12(C_{00}+C_{11}).
\]

For the smallest frozen \(\gamma\) whose pseudo-world condition-number 95th
percentile is at most 100:

\[
W_\gamma=W+
\gamma\frac{\operatorname{tr}W}{d}I,
\qquad
R=W_\gamma^{-1/2}BW_\gamma^{-1/2}.
\]

The generalized eigenproblem is:

\[
Bv_j=\lambda_jW_\gamma v_j.
\]

The M blocks have already been standardized separately by the D0 pseudo
background. Retaining the complete within covariance here is necessary:
\(W_\gamma\succeq W\) and Cauchy-Schwarz then bound the signed spectrum in
\([-1,1]\). A block-diagonal denominator is forbidden because cross-block
covariance can otherwise create pseudo-concordance values above one. Blocks
are used only for frozen-loading attribution.

Positive and negative eigenvalues are retained separately. No positive-part
projection is applied to \(B\) or \(R\).

## D0 resolution

D0 is deterministically divided into A/B author halves. Pseudo-author worlds
freeze 95th-percentile thresholds for the largest positive and negative
eigenvalues. Candidate ranks count natural D0 eigenvalues beyond those
thresholds, capped at 12.

A side is resolved only if:

- its A/B subspace affinity exceeds the full pseudo-pipeline 95th percentile;
- A-fitted directions have the expected signed concordance in B;
- B-fitted directions have the expected signed concordance in A.

The full D0 spectrum is refit only after rank and stability pass.

## D1/D2 audit

The frozen positive generalized vectors are scored without refitting:

\[
T_{+,s}
=
\frac{\operatorname{tr}(V_+^\top B_sV_+)}
{\operatorname{tr}(V_+^\top W_sV_+)}.
\]

The same vectors score 1,999 pseudo-author worlds. The primary design declares
six `M_all` corpus-by-split cells. A corpus whose D0 spectrum is unresolved is
an automatic non-pass and has no numerical D1/D2 score. MaxT is therefore
computed only over the numerically resolved `M_all` cells; unresolved cells
cannot be rescued by that smaller family. Both D1 and D2 of a corpus must have
positive excess, maxT \(p\le .05\), and a paired-world author-cluster lower
bound above zero.

`strict_shape = variance + centered RFF` is a secondary family. Raw quantiles
are excluded because they retain location and would not form a strict
mean-free shape test.

## Interpretation

- A resolved and replicated positive spectrum is a corpus-local, low-dimensional
  same-coordinate author concordance subspace.
- A signed-link pass without a resolved spectrum means concordance is diffuse
  or the D0 panel cannot identify stable axes.
- A negative spectrum is technical-view complementarity, not noise and not a
  score that may be sign-flipped after inspection.
- No outcome identifies personality or a cross-corpus common construct.
