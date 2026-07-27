# SUICA M3 Two-Phase Microkernel Discovery

Decision: `M3_TWO_PHASE_MICROKERNEL_DISCOVERY_PARTIAL`

## What changed from V1

The free phase produces an event-level joint state-choice chain. The fixed
phase samples vector responses from the same conditional emission family under
assigned conditions and occasion-level states. Hidden discrete codes and
random-Fourier features are not exposed to the estimator. The estimator uses
ordered counts, training-occasion-selected hierarchical shrinkage, and a
cross-validated RBF surface on public condition coordinates.

This is basis-blinded but not fully out-of-family: random Fourier functions and
Gaussian RBF regression are members of the same kernel family. Shared sequence
information and author-specific transition information are scored separately.
Response metrics use unseen conditions and independent test occasions.

## Discovery checks

- PASS: `input_contract_isolation`
- PASS: `positive_protocol_identification`
- PASS: `occupancy_recovery`
- PASS: `ordered_transition_information`
- PASS: `personal_transition_information`
- PASS: `shared_transition_information`
- PASS: `unseen_condition_field_recovery`
- PASS: `public_projection_recovery`
- PASS: `nonlinear_remainder_recovery`
- FAIL: `nonlinear_predictive_increment`
- PASS: `relative_occasion_state_recovery`
- PASS: `same_author_response_reidentification`
- PASS: `null_author_calibration`
- PASS: `null_personal_transition_calibration`
- PASS: `design_refusals`
- PASS: `response_space_invariance`
- PASS: `occupancy_transition_nonidentification`
- PASS: `stable_state_nonidentification`

## World-by-world estimates

| world                           | metric                            |       mean |    lower95 |    upper95 |   n |
|:--------------------------------|:----------------------------------|-----------:|-----------:|-----------:|----:|
| N10_null_authors                | occupancy_correlation             |     0.5571 |     0.5491 |     0.5670 |  12 |
| N10_null_authors                | transition_order_gain             |     0.0717 |     0.0704 |     0.0729 |  12 |
| N10_null_authors                | heldout_personal_transition_skill |    -0.0000 |    -0.0000 |     0.0000 |  12 |
| N10_null_authors                | heldout_shared_transition_skill   |     0.0303 |     0.0296 |     0.0312 |  12 |
| N10_null_authors                | transition_prior_strength         | 10000.0000 | 10000.0000 | 10000.0000 |  12 |
| N10_null_authors                | heldout_field_r2                  |    -0.2358 |    -0.2989 |    -0.1736 |  12 |
| N10_null_authors                | heldout_nonlinear_increment       |     0.0608 |     0.0513 |     0.0704 |  12 |
| N10_null_authors                | projection_correlation            |   nan      |   nan      |   nan      |   0 |
| N10_null_authors                | nonlinear_heldout_correlation     |   nan      |   nan      |   nan      |   0 |
| N10_null_authors                | same_author_response_auc          |     0.5049 |     0.4925 |     0.5181 |  12 |
| N10_null_authors                | state_relative_correlation        |     0.7759 |     0.7223 |     0.8213 |  12 |
| N1_no_common_support            | occupancy_correlation             |     0.9282 |     0.9223 |     0.9340 |  12 |
| N1_no_common_support            | transition_order_gain             |     0.0816 |     0.0730 |     0.0900 |  12 |
| N1_no_common_support            | heldout_personal_transition_skill |     0.0182 |     0.0155 |     0.0209 |  12 |
| N1_no_common_support            | heldout_shared_transition_skill   |     0.1090 |     0.0982 |     0.1188 |  12 |
| N1_no_common_support            | transition_prior_strength         |    93.3333 |    80.0000 |   100.0000 |  12 |
| N1_no_common_support            | heldout_field_r2                  |   nan      |   nan      |   nan      |   0 |
| N1_no_common_support            | heldout_nonlinear_increment       |   nan      |   nan      |   nan      |   0 |
| N1_no_common_support            | projection_correlation            |   nan      |   nan      |   nan      |   0 |
| N1_no_common_support            | nonlinear_heldout_correlation     |   nan      |   nan      |   nan      |   0 |
| N1_no_common_support            | same_author_response_auc          |   nan      |   nan      |   nan      |   0 |
| N1_no_common_support            | state_relative_correlation        |   nan      |   nan      |   nan      |   0 |
| N2_single_occasion              | occupancy_correlation             |     0.7904 |     0.7672 |     0.8139 |  12 |
| N2_single_occasion              | transition_order_gain             |     0.0840 |     0.0779 |     0.0922 |  12 |
| N2_single_occasion              | heldout_personal_transition_skill |     0.0001 |     0.0001 |     0.0001 |  12 |
| N2_single_occasion              | heldout_shared_transition_skill   |     0.0206 |     0.0036 |     0.0368 |  12 |
| N2_single_occasion              | transition_prior_strength         | 10000.0000 | 10000.0000 | 10000.0000 |  12 |
| N2_single_occasion              | heldout_field_r2                  |    -0.3389 |    -0.4263 |    -0.2646 |  12 |
| N2_single_occasion              | heldout_nonlinear_increment       |     0.1762 |     0.1518 |     0.2024 |  12 |
| N2_single_occasion              | projection_correlation            |     0.1702 |     0.1422 |     0.2036 |  12 |
| N2_single_occasion              | nonlinear_heldout_correlation     |    -0.0056 |    -0.0670 |     0.0544 |  12 |
| N2_single_occasion              | same_author_response_auc          |     0.5639 |     0.5451 |     0.5797 |  12 |
| N2_single_occasion              | state_relative_correlation        |   nan      |   nan      |   nan      |   0 |
| N3_fixed_not_randomized         | occupancy_correlation             |     0.9336 |     0.9265 |     0.9399 |  12 |
| N3_fixed_not_randomized         | transition_order_gain             |     0.0863 |     0.0782 |     0.0942 |  12 |
| N3_fixed_not_randomized         | heldout_personal_transition_skill |     0.0204 |     0.0165 |     0.0241 |  12 |
| N3_fixed_not_randomized         | heldout_shared_transition_skill   |     0.1196 |     0.1037 |     0.1351 |  12 |
| N3_fixed_not_randomized         | transition_prior_strength         |    80.0000 |    60.0000 |   100.0000 |  12 |
| N3_fixed_not_randomized         | heldout_field_r2                  |    -0.0916 |    -0.1294 |    -0.0529 |  12 |
| N3_fixed_not_randomized         | heldout_nonlinear_increment       |     0.0480 |     0.0385 |     0.0600 |  12 |
| N3_fixed_not_randomized         | projection_correlation            |     0.2392 |     0.2046 |     0.2753 |  12 |
| N3_fixed_not_randomized         | nonlinear_heldout_correlation     |     0.0209 |    -0.0273 |     0.0651 |  12 |
| N3_fixed_not_randomized         | same_author_response_auc          |     0.5846 |     0.5671 |     0.6043 |  12 |
| N3_fixed_not_randomized         | state_relative_correlation        |     0.5612 |     0.4949 |     0.6301 |  12 |
| N4_rank_deficient               | occupancy_correlation             |     0.9069 |     0.8924 |     0.9189 |  12 |
| N4_rank_deficient               | transition_order_gain             |     0.1172 |     0.1091 |     0.1259 |  12 |
| N4_rank_deficient               | heldout_personal_transition_skill |     0.0059 |     0.0043 |     0.0076 |  12 |
| N4_rank_deficient               | heldout_shared_transition_skill   |     0.1379 |     0.1204 |     0.1534 |  12 |
| N4_rank_deficient               | transition_prior_strength         |   133.3333 |   100.0000 |   200.0000 |  12 |
| N4_rank_deficient               | heldout_field_r2                  |   nan      |   nan      |   nan      |   0 |
| N4_rank_deficient               | heldout_nonlinear_increment       |   nan      |   nan      |   nan      |   0 |
| N4_rank_deficient               | projection_correlation            |   nan      |   nan      |   nan      |   0 |
| N4_rank_deficient               | nonlinear_heldout_correlation     |   nan      |   nan      |   nan      |   0 |
| N4_rank_deficient               | same_author_response_auc          |   nan      |   nan      |   nan      |   0 |
| N4_rank_deficient               | state_relative_correlation        |   nan      |   nan      |   nan      |   0 |
| N5_representation_drift         | occupancy_correlation             |     0.9300 |     0.9209 |     0.9382 |  12 |
| N5_representation_drift         | transition_order_gain             |     0.0927 |     0.0845 |     0.1012 |  12 |
| N5_representation_drift         | heldout_personal_transition_skill |     0.0218 |     0.0191 |     0.0244 |  12 |
| N5_representation_drift         | heldout_shared_transition_skill   |     0.1178 |     0.1000 |     0.1354 |  12 |
| N5_representation_drift         | transition_prior_strength         |    80.0000 |    60.0000 |   100.0000 |  12 |
| N5_representation_drift         | heldout_field_r2                  |   nan      |   nan      |   nan      |   0 |
| N5_representation_drift         | heldout_nonlinear_increment       |   nan      |   nan      |   nan      |   0 |
| N5_representation_drift         | projection_correlation            |   nan      |   nan      |   nan      |   0 |
| N5_representation_drift         | nonlinear_heldout_correlation     |   nan      |   nan      |   nan      |   0 |
| N5_representation_drift         | same_author_response_auc          |   nan      |   nan      |   nan      |   0 |
| N5_representation_drift         | state_relative_correlation        |   nan      |   nan      |   nan      |   0 |
| N6_unknown_missingness          | occupancy_correlation             |     0.9334 |     0.9259 |     0.9400 |  12 |
| N6_unknown_missingness          | transition_order_gain             |     0.0916 |     0.0826 |     0.1005 |  12 |
| N6_unknown_missingness          | heldout_personal_transition_skill |     0.0194 |     0.0166 |     0.0224 |  12 |
| N6_unknown_missingness          | heldout_shared_transition_skill   |     0.1186 |     0.1033 |     0.1362 |  12 |
| N6_unknown_missingness          | transition_prior_strength         |    73.3333 |    53.3333 |    93.3333 |  12 |
| N6_unknown_missingness          | heldout_field_r2                  |   nan      |   nan      |   nan      |   0 |
| N6_unknown_missingness          | heldout_nonlinear_increment       |   nan      |   nan      |   nan      |   0 |
| N6_unknown_missingness          | projection_correlation            |   nan      |   nan      |   nan      |   0 |
| N6_unknown_missingness          | nonlinear_heldout_correlation     |   nan      |   nan      |   nan      |   0 |
| N6_unknown_missingness          | same_author_response_auc          |   nan      |   nan      |   nan      |   0 |
| N6_unknown_missingness          | state_relative_correlation        |   nan      |   nan      |   nan      |   0 |
| N7_dependent_technical_streams  | occupancy_correlation             |     0.9319 |     0.9216 |     0.9406 |  12 |
| N7_dependent_technical_streams  | transition_order_gain             |     0.0851 |     0.0797 |     0.0900 |  12 |
| N7_dependent_technical_streams  | heldout_personal_transition_skill |     0.0188 |     0.0169 |     0.0209 |  12 |
| N7_dependent_technical_streams  | heldout_shared_transition_skill   |     0.1068 |     0.0907 |     0.1232 |  12 |
| N7_dependent_technical_streams  | transition_prior_strength         |    86.6667 |    66.6667 |   100.0000 |  12 |
| N7_dependent_technical_streams  | heldout_field_r2                  |    -0.0568 |    -0.0975 |    -0.0145 |  12 |
| N7_dependent_technical_streams  | heldout_nonlinear_increment       |     0.0491 |     0.0359 |     0.0613 |  12 |
| N7_dependent_technical_streams  | projection_correlation            |     0.2418 |     0.1867 |     0.2914 |  12 |
| N7_dependent_technical_streams  | nonlinear_heldout_correlation     |     0.0851 |     0.0286 |     0.1388 |  12 |
| N7_dependent_technical_streams  | same_author_response_auc          |     0.6192 |     0.6020 |     0.6381 |  12 |
| N7_dependent_technical_streams  | state_relative_correlation        |     0.5035 |     0.4454 |     0.5570 |  12 |
| N8_mixed_coarse_blocks          | occupancy_correlation             |     0.9313 |     0.9264 |     0.9363 |  12 |
| N8_mixed_coarse_blocks          | transition_order_gain             |     0.0913 |     0.0846 |     0.0980 |  12 |
| N8_mixed_coarse_blocks          | heldout_personal_transition_skill |     0.0221 |     0.0194 |     0.0250 |  12 |
| N8_mixed_coarse_blocks          | heldout_shared_transition_skill   |     0.1198 |     0.1057 |     0.1339 |  12 |
| N8_mixed_coarse_blocks          | transition_prior_strength         |    66.6667 |    46.6667 |    86.6667 |  12 |
| N8_mixed_coarse_blocks          | heldout_field_r2                  |    -0.0816 |    -0.1348 |    -0.0316 |  12 |
| N8_mixed_coarse_blocks          | heldout_nonlinear_increment       |     0.0500 |     0.0403 |     0.0595 |  12 |
| N8_mixed_coarse_blocks          | projection_correlation            |     0.2122 |     0.1736 |     0.2467 |  12 |
| N8_mixed_coarse_blocks          | nonlinear_heldout_correlation     |     0.1028 |     0.0233 |     0.1759 |  12 |
| N8_mixed_coarse_blocks          | same_author_response_auc          |     0.6065 |     0.5821 |     0.6344 |  12 |
| N8_mixed_coarse_blocks          | state_relative_correlation        |     0.5234 |     0.4620 |     0.5853 |  12 |
| N9_reference_mismatch           | occupancy_correlation             |     0.9332 |     0.9239 |     0.9416 |  12 |
| N9_reference_mismatch           | transition_order_gain             |     0.0938 |     0.0884 |     0.1001 |  12 |
| N9_reference_mismatch           | heldout_personal_transition_skill |     0.0215 |     0.0168 |     0.0266 |  12 |
| N9_reference_mismatch           | heldout_shared_transition_skill   |     0.1300 |     0.1136 |     0.1478 |  12 |
| N9_reference_mismatch           | transition_prior_strength         |    80.0000 |    60.0000 |   100.0000 |  12 |
| N9_reference_mismatch           | heldout_field_r2                  |   nan      |   nan      |   nan      |   0 |
| N9_reference_mismatch           | heldout_nonlinear_increment       |   nan      |   nan      |   nan      |   0 |
| N9_reference_mismatch           | projection_correlation            |   nan      |   nan      |   nan      |   0 |
| N9_reference_mismatch           | nonlinear_heldout_correlation     |   nan      |   nan      |   nan      |   0 |
| N9_reference_mismatch           | same_author_response_auc          |   nan      |   nan      |   nan      |   0 |
| N9_reference_mismatch           | state_relative_correlation        |   nan      |   nan      |   nan      |   0 |
| P2_smooth_event_kernel          | occupancy_correlation             |     0.9807 |     0.9791 |     0.9822 |  12 |
| P2_smooth_event_kernel          | transition_order_gain             |     0.0985 |     0.0964 |     0.1005 |  12 |
| P2_smooth_event_kernel          | heldout_personal_transition_skill |     0.0405 |     0.0378 |     0.0432 |  12 |
| P2_smooth_event_kernel          | heldout_shared_transition_skill   |     0.1496 |     0.1420 |     0.1571 |  12 |
| P2_smooth_event_kernel          | transition_prior_strength         |   100.0000 |   100.0000 |   100.0000 |  12 |
| P2_smooth_event_kernel          | heldout_field_r2                  |     0.1302 |     0.0135 |     0.2240 |  12 |
| P2_smooth_event_kernel          | heldout_nonlinear_increment       |    -0.0097 |    -0.0333 |     0.0069 |  12 |
| P2_smooth_event_kernel          | projection_correlation            |     0.7465 |     0.7005 |     0.7913 |  12 |
| P2_smooth_event_kernel          | nonlinear_heldout_correlation     |     0.3880 |     0.3092 |     0.4623 |  12 |
| P2_smooth_event_kernel          | same_author_response_auc          |     0.8382 |     0.7974 |     0.8767 |  12 |
| P2_smooth_event_kernel          | state_relative_correlation        |     0.8531 |     0.8111 |     0.8918 |  12 |
| P3_nonlinear_t5                 | occupancy_correlation             |     0.9819 |     0.9807 |     0.9833 |  12 |
| P3_nonlinear_t5                 | transition_order_gain             |     0.0958 |     0.0942 |     0.0975 |  12 |
| P3_nonlinear_t5                 | heldout_personal_transition_skill |     0.0428 |     0.0392 |     0.0465 |  12 |
| P3_nonlinear_t5                 | heldout_shared_transition_skill   |     0.1571 |     0.1472 |     0.1680 |  12 |
| P3_nonlinear_t5                 | transition_prior_strength         |   100.0000 |   100.0000 |   100.0000 |  12 |
| P3_nonlinear_t5                 | heldout_field_r2                  |     0.2051 |     0.1409 |     0.2653 |  12 |
| P3_nonlinear_t5                 | heldout_nonlinear_increment       |     0.0348 |     0.0148 |     0.0574 |  12 |
| P3_nonlinear_t5                 | projection_correlation            |     0.8320 |     0.8087 |     0.8484 |  12 |
| P3_nonlinear_t5                 | nonlinear_heldout_correlation     |     0.5310 |     0.4694 |     0.5871 |  12 |
| P3_nonlinear_t5                 | same_author_response_auc          |     0.9178 |     0.8930 |     0.9426 |  12 |
| P3_nonlinear_t5                 | state_relative_correlation        |     0.8098 |     0.7585 |     0.8575 |  12 |
| P4_state_choice_heteroskedastic | occupancy_correlation             |     0.9814 |     0.9797 |     0.9827 |  12 |
| P4_state_choice_heteroskedastic | transition_order_gain             |     0.0952 |     0.0926 |     0.0976 |  12 |
| P4_state_choice_heteroskedastic | heldout_personal_transition_skill |     0.0408 |     0.0376 |     0.0433 |  12 |
| P4_state_choice_heteroskedastic | heldout_shared_transition_skill   |     0.1529 |     0.1432 |     0.1610 |  12 |
| P4_state_choice_heteroskedastic | transition_prior_strength         |   100.0000 |   100.0000 |   100.0000 |  12 |
| P4_state_choice_heteroskedastic | heldout_field_r2                  |     0.2408 |     0.1793 |     0.3003 |  12 |
| P4_state_choice_heteroskedastic | heldout_nonlinear_increment       |    -0.0032 |    -0.0140 |     0.0084 |  12 |
| P4_state_choice_heteroskedastic | projection_correlation            |     0.8153 |     0.7908 |     0.8372 |  12 |
| P4_state_choice_heteroskedastic | nonlinear_heldout_correlation     |     0.4872 |     0.4377 |     0.5338 |  12 |
| P4_state_choice_heteroskedastic | same_author_response_auc          |     0.8899 |     0.8578 |     0.9222 |  12 |
| P4_state_choice_heteroskedastic | state_relative_correlation        |     0.8279 |     0.7919 |     0.8640 |  12 |

## Refusal audit

```json
{
  "N1_no_common_support": 1.0,
  "N2_single_occasion": 1.0,
  "N3_fixed_not_randomized": 1.0,
  "N4_rank_deficient": 1.0,
  "N5_representation_drift": 1.0,
  "N6_unknown_missingness": 1.0,
  "N7_dependent_technical_streams": 1.0,
  "N8_mixed_coarse_blocks": 1.0,
  "N9_reference_mismatch": 1.0
}
```

## Diagnostic extrema

```json
{
  "minimum_positive_occupancy_correlation": 0.9807099387244594,
  "minimum_positive_transition_order_gain": 0.09516106962543396,
  "minimum_positive_personal_transition_skill": 0.04050968124242513,
  "minimum_positive_shared_transition_skill": 0.14959071974758129,
  "minimum_positive_heldout_field_r2": 0.13021327268515184,
  "minimum_positive_projection_correlation": 0.7465301977623846,
  "minimum_positive_nonlinear_correlation": 0.38804776937935803,
  "minimum_nonlinear_increment_lower95": -0.03328364501504281,
  "minimum_nonlinear_positive_seed_fraction": 0.4166666666666667,
  "minimum_positive_state_correlation": 0.8098243765461577,
  "minimum_positive_same_author_auc": 0.8381637286324787,
  "null_same_author_auc": 0.5048889689223799,
  "null_personal_transition_skill": -1.8821075582571624e-06,
  "maximum_invariance_error": 4.052314039881821e-15,
  "minimum_invariance_geometry": 1.0,
  "alias_occupancy_accuracy": 0.5499999999999999,
  "alias_transition_accuracy": 1.0,
  "maximum_state_alias_observable_error": 3.3306690738754696e-16,
  "minimum_state_alias_truth_difference": 0.988733426773778
}
```

## Interpretation boundary

This is a discovery run, not a frozen confirmation. A partial result may
support specific components even when the conjunction fails. The recovered
axes are public-coordinate projections, not generator coefficients and not
psychological traits. Correlation with a planted nonlinear remainder is not
enough to claim nonlinear predictive benefit; that requires positive held-out
incremental R2 across worlds and seeds.

Discovery only. The current generator and estimator are basis-blinded but near-family because random Fourier response functions and Gaussian RBF regression share a kernel family. A partial result may support two-phase synthetic recovery of occupancy, shared and author-specific transition information, public-coordinate response projection, and within-author relative occasion state under explicit design conditions. General nonlinear recovery, human text, personality meaning, psychological constructs, clinical use, and sealed confirmation remain unlicensed.
