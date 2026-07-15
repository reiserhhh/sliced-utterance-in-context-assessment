# SUICA V6 Residual Metric Diagnostic

## Status

**POSTHOC_EXPLANATORY_ONLY.** This diagnostic was triggered by the frozen L1
residual AUC result. It does not alter L1, PRED-1, or the centering claims.

## Same data, two metrics

- J1-compatible confirmation authors: `1,195`
- raw/residual multivariate same-author AUC: `0.6002` / `0.6500`
- residual minus raw AUC: `+0.0499`
- interpretation: `AUC_RELIABILITY_DIVERGENCE`

### Per-coordinate split-half reliability

| coordinate            |   first_r |   second_r |   second_minus_first |   ci_lo |   ci_hi |   bootstrap_finite_fraction |
|:----------------------|----------:|-----------:|---------------------:|--------:|--------:|----------------------------:|
| first_person_usage_v2 |    0.6264 |     0.5435 |              -0.0829 | -0.101  | -0.0646 |                           1 |
| directive_action_v2   |    0.3807 |     0.3023 |              -0.0784 | -0.1066 | -0.0505 |                           1 |
| novelty_play_v2       |    0.1223 |     0.0706 |              -0.0516 | -0.0766 | -0.0267 |                           1 |
| tension_core_v2       |    0.1035 |     0.1044 |               0.0009 | -0.0132 |  0.0144 |                           1 |

## Reading

A multivariate AUC uses the geometry of the four-coordinate vector, whereas a
scalar split-half correlation retains one coordinate’s population variance. A
difference between them is an estimand/metric fact, not evidence that either
raw or residual coordinates are personality. The residual transform is fitted
on discovery condition means only; labels and raw-text artifacts are absent.
