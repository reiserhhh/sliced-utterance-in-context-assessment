# SUICA V7 Identification Calibration Matrix

## Scope

This is a synthetic calibration. It tests when V7-style subspace, linear-map, residual, and own-vs-stranger statistics recover or fail under known data-generating worlds. It contains no human text or psychological labels.

## Results

| world                                            | metric                               |   n |    mean |    q025 |    q975 |
|:-------------------------------------------------|:-------------------------------------|----:|--------:|--------:|--------:|
| axis_rotation_equivalence                        | alignment_auc                        | 160 |  1.0000 |  1.0000 |  1.0000 |
| axis_rotation_equivalence                        | relative_distance_spearman           | 160 |  1.0000 |  1.0000 |  1.0000 |
| axis_rotation_equivalence                        | linear_transport_r2                  | 160 |  0.9998 |  0.9998 |  0.9999 |
| axis_rotation_equivalence                        | residual_alignment_auc               | 160 |  1.0000 |  1.0000 |  1.0000 |
| axis_rotation_equivalence                        | raw_subspace_congruence              | 160 |  0.8757 |  0.7848 |  0.9411 |
| axis_rotation_equivalence                        | context_adjusted_subspace_congruence | 160 |  0.8757 |  0.7848 |  0.9411 |
| axis_rotation_equivalence                        | rotation_max_abs_error               | 160 |  0.0000 |  0.0000 |  0.0000 |
| endogenous_context_overadjustment_counterexample | alignment_auc                        | 160 |  0.9627 |  0.9449 |  0.9766 |
| endogenous_context_overadjustment_counterexample | relative_distance_spearman           | 160 |  0.8674 |  0.8232 |  0.9011 |
| endogenous_context_overadjustment_counterexample | linear_transport_r2                  | 160 |  0.7287 |  0.6618 |  0.7869 |
| endogenous_context_overadjustment_counterexample | residual_alignment_auc               | 160 |  0.8361 |  0.7743 |  0.9092 |
| endogenous_context_overadjustment_counterexample | raw_subspace_congruence              | 160 |  0.9967 |  0.9936 |  0.9984 |
| endogenous_context_overadjustment_counterexample | context_adjusted_subspace_congruence | 160 |  0.7412 |  0.5088 |  0.9756 |
| measurement_error_context_counterexample         | alignment_auc                        | 160 |  0.9789 |  0.9579 |  0.9921 |
| measurement_error_context_counterexample         | relative_distance_spearman           | 160 |  0.9759 |  0.9513 |  0.9901 |
| measurement_error_context_counterexample         | linear_transport_r2                  | 160 |  0.9306 |  0.8656 |  0.9712 |
| measurement_error_context_counterexample         | residual_alignment_auc               | 160 |  0.9739 |  0.9454 |  0.9906 |
| nonlinear_metric_without_linear_coordinate       | alignment_auc                        | 160 |  0.6737 |  0.6296 |  0.7136 |
| nonlinear_metric_without_linear_coordinate       | relative_distance_spearman           | 160 |  0.3926 |  0.3253 |  0.4585 |
| nonlinear_metric_without_linear_coordinate       | linear_transport_r2                  | 160 |  0.0682 | -0.0748 |  0.1656 |
| nonlinear_metric_without_linear_coordinate       | residual_alignment_auc               | 160 |  0.6743 |  0.6278 |  0.7139 |
| null                                             | alignment_auc                        | 160 |  0.4991 |  0.4716 |  0.5286 |
| null                                             | relative_distance_spearman           | 160 |  0.0031 | -0.0584 |  0.0627 |
| null                                             | linear_transport_r2                  | 160 | -0.1201 | -0.1717 | -0.0807 |
| null                                             | residual_alignment_auc               | 160 |  0.4991 |  0.4696 |  0.5292 |
| omitted_context_counterexample                   | alignment_auc                        | 160 |  0.9998 |  0.9991 |  1.0000 |
| omitted_context_counterexample                   | relative_distance_spearman           | 160 |  0.9885 |  0.9795 |  0.9945 |
| omitted_context_counterexample                   | linear_transport_r2                  | 160 |  0.9731 |  0.9528 |  0.9839 |
| omitted_context_counterexample                   | residual_alignment_auc               | 160 |  0.9985 |  0.9964 |  0.9995 |
| shared_linear                                    | alignment_auc                        | 160 |  0.9964 |  0.9906 |  0.9987 |
| shared_linear                                    | relative_distance_spearman           | 160 |  0.9254 |  0.8928 |  0.9494 |
| shared_linear                                    | linear_transport_r2                  | 160 |  0.8612 |  0.7951 |  0.9009 |
| shared_linear                                    | residual_alignment_auc               | 160 |  0.9694 |  0.9438 |  0.9806 |
| shared_linear                                    | raw_subspace_congruence              | 160 |  0.5845 |  0.3897 |  0.8178 |
| shared_linear                                    | context_adjusted_subspace_congruence | 160 |  0.9973 |  0.9952 |  0.9986 |
| view_private_structure_sensitivity               | alignment_auc                        | 160 |  0.8115 |  0.7780 |  0.8448 |
| view_private_structure_sensitivity               | relative_distance_spearman           | 160 |  0.3824 |  0.2832 |  0.4624 |
| view_private_structure_sensitivity               | linear_transport_r2                  | 160 |  0.3822 |  0.2894 |  0.4702 |
| view_private_structure_sensitivity               | residual_alignment_auc               | 160 |  0.8113 |  0.7780 |  0.8426 |
| view_private_structure_sensitivity               | raw_subspace_congruence              | 160 |  0.9837 |  0.9625 |  0.9935 |
| view_private_structure_sensitivity               | context_adjusted_subspace_congruence | 160 |  0.9836 |  0.9627 |  0.9932 |

## Gates

Status: `IDENTIFICATION_CALIBRATION_PASS`

- `rotation_equivalence_exact`: `True`
- `shared_context_adjusted_subspace_recovery`: `True`
- `null_alignment_control`: `True`
- `nonlinear_relative_geometry_linear_separation`: `True`
- `omitted_context_counterexample`: `True`
- `endogenous_context_overadjustment_counterexample`: `True`
- `measurement_error_context_counterexample`: `True`

## Interpretation

Exact rotation equivalence is a mathematical non-identifiability certificate: stable subspaces do not identify named axes. Recovery truth is transformed into the same standardized feature coordinates used by the estimator. The raw cross-view subspace is reported separately because shared observed context can displace the true shared subspace; the train-fitted context-adjusted estimate only recovers it in the declared exogenous-context world. Omitted, noisy, and endogenous context worlds demonstrate why residual author alignment is not sufficient to identify an author core and why there is no unconditional residualization rule. The nonlinear world demonstrates that pairwise relative geometry and fixed linear coordinate transport are separate estimands.

Artifacts: `results/v7_identification/w2_corrected_full_20260715`
