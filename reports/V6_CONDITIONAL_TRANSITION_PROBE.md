# SUICA V6 Conditional Kernel Transition Probe

## Frozen mathematical object

Let `X` be the two-dimensional, discovery-fitted opportunity-conditioned residual
path and let `H_t = (X_t, Q_t, Q_(t+1), progress_t)`. A Gaussian output kernel
embeds the conditional next-state law:

\[
\mu_0(h)=\mathbb{E}[\ell(X_{t+1},\cdot)\mid H_t=h].
\]

The pooled approximation `mu_0` is trained only on discovery authors. For an
unseen confirmation author-half, the measured object is the equal-run-weighted
conditional residual embedding:

\[
\widehat G_{u,h}=
\frac{1}{|R_{u,h}|}\sum_{r\in R_{u,h}}
\frac{1}{m_r-1}\sum_{t=1}^{m_r-1}
\left[\phi(X_{t+1})-\widehat\mu_0(H_t)\right].
\]

Because the Gaussian kernel is characteristic in its infinite-dimensional limit,
this object is sensitive in principle to conditional mean, variance, skewness,
multimodality, and nonlinear switching. The present `output_rff_features=64`
implementation is a finite, regularized approximation.

## Frozen evaluation protocol

- Representation, nuisance residualization, PCA, and pooled transition law fit:
  discovery authors only.
- Identity evaluation: held-out confirmation authors only.
- Runs are complete consecutive same-subreddit sequences; no transition crosses a
  run, condition, or sampling gap.
- Null: shuffle each run's interior observations jointly while preserving endpoints,
  run membership, and observation multiset.
- No Big Five, MBTI, other questionnaire labels, or author identifiers enter model fitting.

## Results

| variant                           | control                |   auc |   ci_lo |   ci_hi |
|:----------------------------------|:-----------------------|------:|--------:|--------:|
| conditional_transition_embedding  | unmatched              | 0.582 |   0.564 |   0.598 |
| endpoint_preserving_order_shuffle | unmatched              | 0.581 |   0.563 |   0.597 |
| conditional_transition_embedding  | weighted_opportunity   | 0.583 |   0.561 |   0.603 |
| endpoint_preserving_order_shuffle | weighted_opportunity   | 0.581 |   0.560 |   0.602 |
| ordered_minus_shuffled            | weighted_opportunity   | 0.001 |  -0.000 |   0.003 |
| conditional_transition_embedding  | condition_caliper_0.05 | 0.585 |   0.563 |   0.606 |
| endpoint_preserving_order_shuffle | condition_caliper_0.05 | 0.584 |   0.563 |   0.605 |
| ordered_minus_shuffled            | condition_caliper_0.05 | 0.001 |  -0.001 |   0.002 |
| conditional_transition_embedding  | condition_caliper_0.10 | 0.571 |   0.546 |   0.597 |
| endpoint_preserving_order_shuffle | condition_caliper_0.10 | 0.570 |   0.546 |   0.596 |
| ordered_minus_shuffled            | condition_caliper_0.10 | 0.001 |  -0.001 |   0.003 |

## Result status

The exploratory order-sensitive screen is not supported by this PANDORA split.

The matched order delta is `0.0011` with bootstrap interval
`[-0.0004, 0.0027]` across
`669` paired confirmation authors.

## Limits that remain non-negotiable

This does **not** identify a stable author operator `G_u`. PANDORA lacks the
registered `epoch x independent technical replica` structure: a stable author
parameter and a persistent state can generate the same observed transition law.
The matched-stranger procedure is a sensitivity analysis, not causal adjustment.
The current bootstrap is an exploratory uncertainty estimate, not the 1,999
stratified permutation/max-T confirmation protocol required before selecting among
kernel families, history lengths, or hyperparameters.
