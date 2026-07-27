# V8 External Zero, Nested Uncertainty, and Residual Sufficiency V3.7F

Status: `PROSPECTIVELY_SEALED_BEFORE_CONFIRMATION`

## 1. Question

V3.7F tests a stricter replacement for the old denoising metaphor:

> No text coordinate is called noise before it fails stability, condition
> matching, and negative-control tests. Omitted coordinates are an unresolved
> information channel, not disposable error.

This does not imply that personality prediction error must converge to zero.
For target \(\Theta_u\), text \(X\), and condition \(C\), the Bayes floor is

\[
R^*=
\mathbb E\{\operatorname{tr}\operatorname{Var}(\Theta_u\mid X,C)\}.
\]

Coordinate-wise information \(I(X_j;A_u\mid C)>0\) does not force \(R^*=0\).

## 2. Four planted worlds

- `hard_rank12`: exactly 12 stable author directions.
- `dense_tail48`: all 48 ILR directions carry nonzero stable author energy,
  with \(\lambda_j=(1+j/4)^{-0.75}\).
- `dense_state_alias`: the dense stable structure plus correlated temporary
  state that cannot be separated from one short observation.
- `author_permutation`: session marginals are preserved while author pairing
  is destroyed.

The dense worlds are a mathematical existence test for distributed author
information. They do not assert that every natural-language token contains
personality.

The hard-rank specificity world fixes context and author-by-context
amplitudes to zero so the ILR profile is exactly rank 12. The dense worlds
retain both terms. This prevents nonlinear context integration from planting
unregistered stable residuals in the null control.

## 3. Fully external origin

Four disjoint author panels are used:

- 256 router-reference authors;
- 256 zero/norm-reference authors;
- 128 calibration authors;
- 96 evaluation authors.

The router is fitted only on the first panel. The absolute origin

\[
\hat z_0
=
\frac{1}{2|R_Z|}
\sum_{i\in R_Z}(x_{i1}^{Q_0}+x_{i2}^{Q_0})
\]

is fitted only on the second. Rank and stable basis use calibration authors
but may not redefine the origin. Evaluation authors never affect another
author's score.

## 4. Hard and soft estimators

Hard adaptive scoring uses

\[
\hat D_u
=
\hat z_0+\hat P_{\hat r}(\bar x_u-\hat z_0).
\]

The unresolved channel is

\[
R_{us}
=(I-\hat P_{\hat r})(x_{us}-\hat z_0).
\]

The soft sensitivity keeps every empirically positive stable direction and
uses reliability weights

\[
w_j=
\frac{\max(\hat\lambda_j,0)}
{\max(\hat\lambda_j,0)+\hat\nu_j/2}.
\]

The registered information-conserving rule is conditional but not
truth-selected: if adaptive selection already chooses all 48 coordinates, the
full-space hard score is retained; otherwise the soft all-positive-energy
operator is used. This prevents unnecessary shrinkage from being declared a
universal improvement.

## 5. Nested uncertainty

The balanced resampling tensor is \(T_u(R,K,E)\):

- \(R\): router and norm-reference author resampling;
- \(K\): calibration-pair resampling, rank reselection, and basis refit;
- \(E\): target-author event resampling.

A functional-ANOVA decomposition separates main effects and interactions.
Empirical Mahalanobis regions are calibrated from the joint cloud rather than
assuming a chi-square law. Event-only and full-pipeline MDC are kept
distinct.

Coverage is evaluated by fresh draws from the scorer-known synthetic event
process. This is an oracle Monte Carlo calibration check for the interval
machinery, not a claim that a real deployment knows its event distribution.

## 6. Residual and asymptotic tests

Residual cross-session reliability, hard-neighbor AUC, and incremental
pairing AUC are measured before any omitted coordinate is called noise.
`hard_rank12` is the specificity control; `dense_tail48` is the sensitivity
test; `author_permutation` must return chance.

Across event budgets 32/64/128/256/512:

\[
\operatorname{MSE}(m)=F_\infty+A m^{-\alpha}.
\]

The experiment distinguishes an event-sampling floor from reference,
capacity, state, and unresolved-channel floors.

## 7. Governance

- V3.7E files and seal are read-only.
- Discovery may repair implementation and choose defensible confirmation
  gates.
- Confirmation requires a new content seal over code, tests, plan, and
  confirmation config.
- No personality labels, author identifiers, or human text are read.
- A pass licenses only the registered synthetic mechanism.
