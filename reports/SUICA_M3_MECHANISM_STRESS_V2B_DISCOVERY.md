# SUICA M3 Low-Order-Matched Mechanism Stress Test

Decision: `M3_MECHANISM_STRESS_DISCOVERY_PASS`

## Purpose

Atlas V1 recovered deliberately simple author parameters. This attack asks
whether the proposed higher-order summaries still add information after the
corresponding cheap statistic is matched or explicitly included.

## Checks

- PASS: `equal_covariance_density_shape_absolute`
- PASS: `equal_covariance_density_shape_incremental`
- PASS: `matched_linear_nonlinear_response_absolute`
- PASS: `matched_linear_nonlinear_response_incremental`
- PASS: `matched_lag1_ar2_slow_mode_absolute`
- PASS: `matched_lag1_ar2_slow_mode_incremental`
- PASS: `matched_lag12_lag3_path_absolute`
- PASS: `matched_lag12_lag3_path_incremental`
- PASS: `matched_linear_nonlinear_interaction_absolute`
- PASS: `matched_linear_nonlinear_interaction_incremental`
- PASS: `null_calibration`

## Final-event diagnostics

| world                                | expected                        | cheap              |   expected_auc |   cheap_auc |   delta_auc |   expected_geometry |   cheap_geometry |   delta_geometry |
|:-------------------------------------|:--------------------------------|:-------------------|---------------:|------------:|------------:|--------------------:|-----------------:|-----------------:|
| equal_covariance_density_shape       | standardized_distribution_shape | covariance_profile |       0.938611 |    0.507077 |    0.431534 |            0.96333  |        0.0259561 |         0.937374 |
| matched_linear_nonlinear_response    | nonlinear_condition             | linear_condition   |       1        |    0.499777 |    0.500223 |            0.998512 |        0.155921  |         0.84259  |
| matched_lag1_ar2_slow_mode           | ar2_slow_spectrum               | lag1_spectrum      |       0.833547 |    0.503805 |    0.329742 |            0.886761 |        0.0308691 |         0.855892 |
| matched_lag12_lag3_path              | lag3_partial_operator           | lag2_memory        |       0.934766 |    0.506336 |    0.42843  |            0.978591 |        0.0306038 |         0.947987 |
| matched_linear_nonlinear_interaction | nonlinear_partner               | linear_partner     |       1        |    0.520882 |    0.479118 |            0.998507 |        0.173229  |         0.825278 |

## Information frontier

|   events | world                                | family              | expected   | cheap   |      auc |    geometry |
|---------:|:-------------------------------------|:--------------------|:-----------|:--------|---------:|------------:|
|       48 | equal_covariance_density_shape       | covariance_profile  | False      | True    | 0.497141 | -0.0137172  |
|       48 | equal_covariance_density_shape       | distribution_kme    | True       | False   | 0.522687 |  0.0555915  |
|       48 | matched_lag12_lag3_path              | lag2_memory         | False      | True    | 0.510902 |  0.0426895  |
|       48 | matched_lag12_lag3_path              | lag3_memory         | True       | False   | 0.523507 |  0.0973042  |
|       48 | matched_lag1_ar2_slow_mode           | ar2_slow_spectrum   | True       | False   | 0.759861 |  0.740594   |
|       48 | matched_lag1_ar2_slow_mode           | lag1_spectrum       | False      | True    | 0.518779 |  0.0299865  |
|       48 | matched_linear_nonlinear_interaction | linear_partner      | False      | True    | 0.519577 |  0.172666   |
|       48 | matched_linear_nonlinear_interaction | nonlinear_partner   | True       | False   | 0.996951 |  0.998558   |
|       48 | matched_linear_nonlinear_response    | linear_condition    | False      | True    | 0.514486 |  0.155159   |
|       48 | matched_linear_nonlinear_response    | nonlinear_condition | True       | False   | 0.997083 |  0.998569   |
|       96 | equal_covariance_density_shape       | covariance_profile  | False      | True    | 0.503269 |  0.00507939 |
|       96 | equal_covariance_density_shape       | distribution_kme    | True       | False   | 0.520595 |  0.0622043  |
|       96 | matched_lag12_lag3_path              | lag2_memory         | False      | True    | 0.515778 |  0.100161   |
|       96 | matched_lag12_lag3_path              | lag3_memory         | True       | False   | 0.538607 |  0.1406     |
|       96 | matched_lag1_ar2_slow_mode           | ar2_slow_spectrum   | True       | False   | 0.802429 |  0.823052   |
|       96 | matched_lag1_ar2_slow_mode           | lag1_spectrum       | False      | True    | 0.49162  |  0.00115498 |
|       96 | matched_linear_nonlinear_interaction | linear_partner      | False      | True    | 0.49239  |  0.151004   |
|       96 | matched_linear_nonlinear_interaction | nonlinear_partner   | True       | False   | 0.999974 |  0.998758   |
|       96 | matched_linear_nonlinear_response    | linear_condition    | False      | True    | 0.528728 |  0.146665   |
|       96 | matched_linear_nonlinear_response    | nonlinear_condition | True       | False   | 0.999936 |  0.998668   |
|      192 | equal_covariance_density_shape       | covariance_profile  | False      | True    | 0.507077 |  0.0259561  |
|      192 | equal_covariance_density_shape       | distribution_kme    | True       | False   | 0.523763 |  0.0805562  |
|      192 | matched_lag12_lag3_path              | lag2_memory         | False      | True    | 0.506336 |  0.0306038  |
|      192 | matched_lag12_lag3_path              | lag3_memory         | True       | False   | 0.5495   |  0.135028   |
|      192 | matched_lag1_ar2_slow_mode           | ar2_slow_spectrum   | True       | False   | 0.833547 |  0.886761   |
|      192 | matched_lag1_ar2_slow_mode           | lag1_spectrum       | False      | True    | 0.503805 |  0.0308691  |
|      192 | matched_linear_nonlinear_interaction | linear_partner      | False      | True    | 0.520882 |  0.173229   |
|      192 | matched_linear_nonlinear_interaction | nonlinear_partner   | True       | False   | 1        |  0.998507   |
|      192 | matched_linear_nonlinear_response    | linear_condition    | False      | True    | 0.499777 |  0.155921   |
|      192 | matched_linear_nonlinear_response    | nonlinear_condition | True       | False   | 1        |  0.998512   |

## Boundary

Even a pass licenses only synthetic higher-order parameter recovery. It does
not establish a complete mechanism basis, human-text persistence, personality
meaning, or construct validity.
