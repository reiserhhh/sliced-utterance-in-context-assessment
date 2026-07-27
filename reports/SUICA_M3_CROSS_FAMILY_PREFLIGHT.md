# SUICA M3 Cross-Family Power Preflight

Decision: `M3_CROSS_FAMILY_PREFLIGHT_POWER_READY`

## Purpose

This development-seed run asks whether one generator-blind estimator suite has
enough power to justify an artifact-sealed fresh-seed confirmation. Failure is
a power or specification finding, not evidence against human personality.

## Target summary

| world           | target       |   seeds |   validity_fraction |   expected_auc |   cheap_auc |   expected_geometry |   cheap_geometry |   heldout_increment |   positive_increment_fraction |   off_target_geometry |   knockout_geometry |
|:----------------|:-------------|--------:|--------------------:|---------------:|------------:|--------------------:|-----------------:|--------------------:|------------------------------:|----------------------:|--------------------:|
| cf_d_copula     | distribution |       6 |                   1 |       0.730173 |    0.502226 |            0.537522 |       0.00502622 |            0.227947 |                             1 |           nan         |           0.0190792 |
| cf_d_multimodal | distribution |       6 |                   1 |       0.669716 |    0.502591 |            0.472975 |      -0.00235151 |            0.167126 |                             1 |           nan         |           0.0142928 |
| cf_d_skew       | distribution |       6 |                   1 |       0.736112 |    0.479827 |            0.523991 |      -0.00774156 |            0.256285 |                             1 |           nan         |           0.0289082 |
| cf_d_tail       | distribution |       6 |                   1 |       0.674661 |    0.498465 |            0.379568 |      -0.00106764 |            0.176196 |                             1 |           nan         |           0.0181864 |
| cf_kp_arch      | path         |       6 |                   1 |       0.640822 |    0.5      |            0.434913 |     nan          |            0.140822 |                             1 |           nan         |           0.0444147 |
| cf_kp_cycle     | path         |       6 |                   1 |       0.729608 |    0.5      |            0.421984 |     nan          |            0.229608 |                             1 |           nan         |           0.0392171 |
| cf_kp_hsmm      | path         |       6 |                   1 |       0.978474 |    0.5      |            0.991828 |     nan          |            0.478474 |                             1 |           nan         |           0.0267482 |
| cf_o_neural     | condition    |       6 |                   1 |       0.968293 |    0.494064 |            0.971538 |      -0.0411136  |            0.205638 |                             1 |             0.0622958 |           0.0370759 |
| cf_o_neural     | partner      |       6 |                   1 |       0.950507 |    0.504401 |            0.982564 |       0.0307256  |            0.212725 |                             1 |             0.0674593 |           0.0631702 |
| cf_o_spline     | condition    |       6 |                   1 |       0.975939 |    0.508469 |            0.986714 |      -0.0435952  |            0.265454 |                             1 |             0.0541258 |           0.0441254 |
| cf_o_spline     | partner      |       6 |                   1 |       0.974691 |    0.504703 |            0.988172 |      -0.0310771  |            0.272545 |                             1 |             0.0436639 |           0.0206967 |
| cf_o_voronoi    | condition    |       6 |                   1 |       0.937974 |    0.505918 |            0.984987 |       0.01537    |            0.15828  |                             1 |             0.106754  |           0.0294771 |
| cf_o_voronoi    | partner      |       6 |                   1 |       0.936583 |    0.496437 |            0.979325 |      -0.0141383  |            0.161874 |                             1 |             0.0896278 |           0.0363397 |

## Gates not yet satisfied

- None

## Boundary

No confirmation truth was sealed or opened. Hyperparameters may still change
only in this preflight branch. Human text, psychological constructs, and
clinical use remain outside scope.
