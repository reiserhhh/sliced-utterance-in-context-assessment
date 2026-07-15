# SUICA V7 Identification Calibration Matrix

## Scope

This is a synthetic calibration. It tests when V7-style subspace, linear-map, residual, and own-vs-stranger statistics recover or fail under known data-generating worlds. It contains no human text or psychological labels.

## Results

| world                                      | metric                               |   n |    mean |    q025 |    q975 |
|:-------------------------------------------|:-------------------------------------|----:|--------:|--------:|--------:|
| axis_rotation_equivalence                  | alignment_auc                        |  16 |  1.0000 |  1.0000 |  1.0000 |
| axis_rotation_equivalence                  | relative_distance_spearman           |  16 |  1.0000 |  1.0000 |  1.0000 |
| axis_rotation_equivalence                  | linear_transport_r2                  |  16 |  0.9984 |  0.9973 |  0.9990 |
| axis_rotation_equivalence                  | residual_alignment_auc               |  16 |  1.0000 |  1.0000 |  1.0000 |
| axis_rotation_equivalence                  | raw_subspace_congruence              |  16 |  0.8804 |  0.8297 |  0.9474 |
| axis_rotation_equivalence                  | context_adjusted_subspace_congruence |  16 |  0.8804 |  0.8297 |  0.9474 |
| axis_rotation_equivalence                  | rotation_max_abs_error               |  16 |  0.0000 |  0.0000 |  0.0000 |
| nonlinear_metric_without_linear_coordinate | alignment_auc                        |  16 |  0.7098 |  0.6699 |  0.7562 |
| nonlinear_metric_without_linear_coordinate | relative_distance_spearman           |  16 |  0.4505 |  0.3760 |  0.5049 |
| nonlinear_metric_without_linear_coordinate | linear_transport_r2                  |  16 |  0.0694 | -0.4424 |  0.2242 |
| nonlinear_metric_without_linear_coordinate | residual_alignment_auc               |  16 |  0.7104 |  0.6684 |  0.7573 |
| nonlinear_metric_without_linear_coordinate | raw_subspace_congruence              |  16 |  0.9405 |  0.8980 |  0.9719 |
| nonlinear_metric_without_linear_coordinate | context_adjusted_subspace_congruence |  16 |  0.9401 |  0.8977 |  0.9728 |
| null                                       | alignment_auc                        |  16 |  0.4996 |  0.4465 |  0.5334 |
| null                                       | relative_distance_spearman           |  16 |  0.0040 | -0.0514 |  0.0553 |
| null                                       | linear_transport_r2                  |  16 | -0.1852 | -0.2571 | -0.1365 |
| null                                       | residual_alignment_auc               |  16 |  0.4998 |  0.4486 |  0.5346 |
| omitted_context_counterexample             | alignment_auc                        |  16 |  0.9994 |  0.9961 |  1.0000 |
| omitted_context_counterexample             | relative_distance_spearman           |  16 |  0.9818 |  0.9505 |  0.9931 |
| omitted_context_counterexample             | linear_transport_r2                  |  16 |  0.9617 |  0.9257 |  0.9794 |
| omitted_context_counterexample             | residual_alignment_auc               |  16 |  0.9969 |  0.9861 |  0.9996 |
| shared_linear                              | alignment_auc                        |  16 |  0.9957 |  0.9903 |  0.9988 |
| shared_linear                              | relative_distance_spearman           |  16 |  0.9109 |  0.8492 |  0.9439 |
| shared_linear                              | linear_transport_r2                  |  16 |  0.8514 |  0.7984 |  0.9000 |
| shared_linear                              | residual_alignment_auc               |  16 |  0.9722 |  0.9533 |  0.9828 |
| shared_linear                              | raw_subspace_congruence              |  16 |  0.6779 |  0.4955 |  0.8323 |
| shared_linear                              | context_adjusted_subspace_congruence |  16 |  0.9402 |  0.9100 |  0.9776 |

## Gates

Status: `IDENTIFICATION_CALIBRATION_PASS`

- `rotation_equivalence_exact`: `True`
- `shared_context_adjusted_subspace_recovery`: `True`
- `null_alignment_control`: `True`
- `nonlinear_relative_geometry_linear_separation`: `True`
- `omitted_context_counterexample`: `True`

## Interpretation

Exact rotation equivalence is a mathematical non-identifiability certificate: stable subspaces do not identify named axes. The raw cross-view subspace is reported separately because shared observed context can displace the true shared subspace; only the train-fitted context-adjusted estimate is used for the recovery gate. The omitted-context world demonstrates why residual author alignment is not sufficient to identify an author core. The nonlinear world demonstrates that pairwise relative geometry and fixed linear coordinate transport are separate estimands.

Artifacts: `results/v7_identification/w2_quick_v2_20260715`
