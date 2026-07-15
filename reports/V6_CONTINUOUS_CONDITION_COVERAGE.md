# V6 Continuous Condition-Manifold Coverage Audit

## Question

Does a balanced fixed schedule alone identify a conditional response function
when topic/situation/opportunity occupies a continuous multidimensional space?
This is a planted-world audit only.

The generator is

\[
Y_{ui}=a_u+m(z_{ui})+B_u\phi(z_{ui})+\epsilon_{ui},\qquad z\in\mathbb{R}^2.
\]

All arms have the same author count and the narrow and wide exact arms have the
same per-author fixed-observation budget. `wide_exact` observes a full smooth
condition map across the full grid. `narrow_exact_same_budget` spends that
budget repeatedly in one half of the manifold. `wide_coarse_proxy` covers the
full grid but its estimator sees only the first context coordinate.

## Frozen setup

- profile: `full`
- config SHA-256: `395bb7aba118416d162b067fd950e3d9b33bc42cf1d9b5b96347371544da7f12`
- repetitions per arm: `200`
- no human text, labels, author IDs, or clinical outcomes used

## Results

| scenario | held-out response r | response MSE | level r | coverage radius | fixed observations |
|---|---:|---:|---:|---:|---:|
| wide_exact | 0.928 [0.922, 0.934] | 0.008 [0.008, 0.009] | 0.995 [0.990, 0.998] | 0.255 [0.233, 0.273] | 32.000 [32.000, 32.000] |
| narrow_exact_same_budget | 0.740 [0.693, 0.785] | 0.026 [0.022, 0.030] | 0.981 [0.976, 0.984] | 0.557 [0.468, 0.653] | 32.000 [32.000, 32.000] |
| wide_coarse_proxy | 0.611 [0.566, 0.648] | 0.035 [0.031, 0.039] | 0.995 [0.990, 0.998] | 0.255 [0.227, 0.274] | 32.000 [32.000, 32.000] |

## Gates

```json
{
  "coarse_proxy_materially_harms_response": true,
  "narrow_coverage_materially_harms_response": true,
  "narrow_has_less_context_coverage": true,
  "wide_exact_recovers_response": true
}
```

## Licensed conclusion

Within this planted family, balancing over a *coarse* or *narrowly covered*
condition representation is not equivalent to balancing over the full condition
manifold. Thus future V6 fixed-prompt work must predefine both condition
representation and coverage diagnostics; simply giving every participant the
same number of prompts is insufficient. This does not validate any human
condition ontology, author trait, factor, or clinical assessment.
