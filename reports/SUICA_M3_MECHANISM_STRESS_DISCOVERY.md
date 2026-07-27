# SUICA M3 Low-Order-Matched Mechanism Stress Test

Decision: `M3_MECHANISM_STRESS_DISCOVERY_PARTIAL`

## Purpose

Atlas V1 recovered deliberately simple author parameters. This attack asks
whether the proposed higher-order summaries still add information after the
corresponding cheap statistic is matched or explicitly included.

## Checks

- FAIL: `equal_covariance_density_shape_absolute`
- FAIL: `equal_covariance_density_shape_incremental`
- PASS: `matched_linear_nonlinear_response_absolute`
- PASS: `matched_linear_nonlinear_response_incremental`
- PASS: `matched_lag1_ar2_slow_mode_absolute`
- PASS: `matched_lag1_ar2_slow_mode_incremental`
- FAIL: `matched_lag12_lag3_path_absolute`
- FAIL: `matched_lag12_lag3_path_incremental`
- PASS: `matched_linear_nonlinear_interaction_absolute`
- PASS: `matched_linear_nonlinear_interaction_incremental`
- PASS: `null_calibration`

## Final-event diagnostics

| world                                | expected            | cheap              |   expected_auc |   cheap_auc |   delta_auc |   expected_geometry |   cheap_geometry |   delta_geometry |
|:-------------------------------------|:--------------------|:-------------------|---------------:|------------:|------------:|--------------------:|-----------------:|-----------------:|
| equal_covariance_density_shape       | distribution_kme    | covariance_profile |       0.533995 |    0.510117 |   0.0238779 |            0.120542 |        0.0517126 |        0.0688296 |
| matched_linear_nonlinear_response    | nonlinear_condition | linear_condition   |       1        |    0.522641 |   0.477359  |            0.998478 |        0.149439  |        0.849039  |
| matched_lag1_ar2_slow_mode           | ar2_slow_spectrum   | lag1_spectrum      |       0.834319 |    0.489722 |   0.344597  |            0.895463 |        0.0358808 |        0.859583  |
| matched_lag12_lag3_path              | lag3_memory         | lag2_memory        |       0.563937 |    0.507908 |   0.0560295 |            0.132235 |        0.0646237 |        0.0676109 |
| matched_linear_nonlinear_interaction | nonlinear_partner   | linear_partner     |       1        |    0.514394 |   0.485606  |            0.998662 |        0.163481  |        0.835181  |

## Information frontier

|   events | world                                | family              | expected   | cheap   |      auc |    geometry |
|---------:|:-------------------------------------|:--------------------|:-----------|:--------|---------:|------------:|
|       48 | equal_covariance_density_shape       | covariance_profile  | False      | True    | 0.506435 |  0.0260414  |
|       48 | equal_covariance_density_shape       | distribution_kme    | True       | False   | 0.533102 |  0.0803546  |
|       48 | matched_lag12_lag3_path              | lag2_memory         | False      | True    | 0.508122 |  0.0464514  |
|       48 | matched_lag12_lag3_path              | lag3_memory         | True       | False   | 0.544905 |  0.0870989  |
|       48 | matched_lag1_ar2_slow_mode           | ar2_slow_spectrum   | True       | False   | 0.766281 |  0.747556   |
|       48 | matched_lag1_ar2_slow_mode           | lag1_spectrum       | False      | True    | 0.50853  | -0.00473738 |
|       48 | matched_linear_nonlinear_interaction | linear_partner      | False      | True    | 0.507403 |  0.133066   |
|       48 | matched_linear_nonlinear_interaction | nonlinear_partner   | True       | False   | 0.997313 |  0.998614   |
|       48 | matched_linear_nonlinear_response    | linear_condition    | False      | True    | 0.50427  |  0.151683   |
|       48 | matched_linear_nonlinear_response    | nonlinear_condition | True       | False   | 0.997507 |  0.998594   |
|       96 | equal_covariance_density_shape       | covariance_profile  | False      | True    | 0.526413 |  0.0151898  |
|       96 | equal_covariance_density_shape       | distribution_kme    | True       | False   | 0.53733  |  0.0659231  |
|       96 | matched_lag12_lag3_path              | lag2_memory         | False      | True    | 0.527917 |  0.0641303  |
|       96 | matched_lag12_lag3_path              | lag3_memory         | True       | False   | 0.534198 |  0.120967   |
|       96 | matched_lag1_ar2_slow_mode           | ar2_slow_spectrum   | True       | False   | 0.808234 |  0.851164   |
|       96 | matched_lag1_ar2_slow_mode           | lag1_spectrum       | False      | True    | 0.513911 |  0.00734455 |
|       96 | matched_linear_nonlinear_interaction | linear_partner      | False      | True    | 0.524885 |  0.139579   |
|       96 | matched_linear_nonlinear_interaction | nonlinear_partner   | True       | False   | 0.999881 |  0.998553   |
|       96 | matched_linear_nonlinear_response    | linear_condition    | False      | True    | 0.523851 |  0.158101   |
|       96 | matched_linear_nonlinear_response    | nonlinear_condition | True       | False   | 0.999861 |  0.998586   |
|      192 | equal_covariance_density_shape       | covariance_profile  | False      | True    | 0.510117 |  0.0517126  |
|      192 | equal_covariance_density_shape       | distribution_kme    | True       | False   | 0.533995 |  0.120542   |
|      192 | matched_lag12_lag3_path              | lag2_memory         | False      | True    | 0.507908 |  0.0646237  |
|      192 | matched_lag12_lag3_path              | lag3_memory         | True       | False   | 0.563937 |  0.132235   |
|      192 | matched_lag1_ar2_slow_mode           | ar2_slow_spectrum   | True       | False   | 0.834319 |  0.895463   |
|      192 | matched_lag1_ar2_slow_mode           | lag1_spectrum       | False      | True    | 0.489722 |  0.0358808  |
|      192 | matched_linear_nonlinear_interaction | linear_partner      | False      | True    | 0.514394 |  0.163481   |
|      192 | matched_linear_nonlinear_interaction | nonlinear_partner   | True       | False   | 1        |  0.998662   |
|      192 | matched_linear_nonlinear_response    | linear_condition    | False      | True    | 0.522641 |  0.149439   |
|      192 | matched_linear_nonlinear_response    | nonlinear_condition | True       | False   | 1        |  0.998478   |

## Boundary

Even a pass licenses only synthetic higher-order parameter recovery. It does
not establish a complete mechanism basis, human-text persistence, personality
meaning, or construct validity.
