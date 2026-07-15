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

- profile: `quick`
- config SHA-256: `6a1388c7639da75a147dc7cd5b6b53c50d684d9c0e0d84511b2ab2ca4d201c22`
- repetitions per arm: `20`
- no human text, labels, author IDs, or clinical outcomes used

## Results

| scenario | held-out response r | response MSE | level r | coverage radius | fixed observations |
|---|---:|---:|---:|---:|---:|
| wide_exact | 0.925 [0.918, 0.930] | 0.009 [0.008, 0.009] | 0.992 [0.982, 0.997] | 0.254 [0.231, 0.278] | 32.000 [32.000, 32.000] |
| narrow_exact_same_budget | 0.733 [0.680, 0.781] | 0.027 [0.022, 0.032] | 0.978 [0.971, 0.982] | 0.561 [0.450, 0.638] | 32.000 [32.000, 32.000] |
| wide_coarse_proxy | 0.610 [0.570, 0.651] | 0.034 [0.030, 0.039] | 0.993 [0.986, 0.996] | 0.254 [0.227, 0.273] | 32.000 [32.000, 32.000] |

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
