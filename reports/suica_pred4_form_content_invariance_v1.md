# PRED-4 form/content structure invariance across rind regimes

| pair                |   transport_FORM |   transport_CONTENT |    diff |   ci_lo |   ci_hi | form_gt_content   | ci_excludes_0   |
|:--------------------|-----------------:|--------------------:|--------:|--------:|--------:|:------------------|:----------------|
| pandora_vs_essays   |           0.5968 |              0.7481 | -0.1513 | -0.2136 | -0.0418 | False             | False           |
| pandora_vs_x_market |           0.7114 |              0.6448 |  0.0666 | -0.0082 |  0.1621 | True              | False           |
| essays_vs_x_market  |           0.521  |              0.7395 | -0.2185 | -0.3004 | -0.0633 | False             | False           |

**verdict: fail** (criterion: FORM > CONTENT in 3/3 pairs AND CI excludes 0 in >= 2/3)

Implication if pass: cross-regime deployment rides on FORM coordinates
+ regime-relative norms (route c); document type is NOT a legitimate
covariate when self-selected (F4).
