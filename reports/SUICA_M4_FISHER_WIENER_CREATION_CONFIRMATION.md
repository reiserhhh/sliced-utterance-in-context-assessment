# SUICA M4-C.3.2 Fisher-Wiener Creation Confirmation

## Decision

`M4_C32_NO_GO_FISHER_WIENER_CREATION`

The discovered condition chart, physical response edge, physical choice edge,
and author-relation endpoint were frozen. Calibration occasions supplied two
technical creation estimates. A leave-one-author-out Fisher-Wiener operator
retained only their cross-half stable author covariance:

\[
\widehat L_u^{FW}=
\widehat A_u^{FW}R_u^DD_u^D.
\]

No oracle edge or final relation geometry was available to the estimator.

## Frozen design

- repetitions: `8`
- main worlds: `endogenous_source_partition_matched, endogenous_creation_expansion, source_rotated_feedback, history_gated_ecology, selection_creation_compensation`
- no-creation controls: `linear_null_ecology, linear_exogenous_selection, fast_return_equal_marginal`
- refusal controls: `condition_alias_ecology, hidden_opportunity_source_alias, evaluation_support_shift, author_leakage, response_leakage_circular`
- hazard family: `gate`
- epsilon scale: `1e-06`

## Main-world results

| world                               |   baseline_geometry |   fisher_geometry |   fisher_gain |   creation_headroom |   hazard_relative_degradation |
|:------------------------------------|--------------------:|------------------:|--------------:|--------------------:|------------------------------:|
| endogenous_creation_expansion       |              0.7745 |            0.8153 |        0.0407 |              0.1869 |                        0.0128 |
| endogenous_source_partition_matched |              0.5894 |            0.6732 |        0.0838 |              0.3514 |                        0.0097 |
| history_gated_ecology               |              0.9612 |            0.9322 |       -0.0290 |              0.0296 |                        0.0074 |
| selection_creation_compensation     |              0.5951 |            0.6226 |        0.0275 |              0.1513 |                        0.0309 |
| source_rotated_feedback             |              0.6788 |            0.8062 |        0.1274 |              0.2678 |                        0.0038 |

## Diagnostics

- `baseline_geometry`: 0.7198060405130348
- `oracle_swap_geometry`: 0.9172274678767088
- `creation_headroom`: 0.19742142736367393
- `creation_headroom_lcb`: 0.13586540923240906
- `fisher_geometry`: 0.7698948533391337
- `fisher_gain`: 0.050088812826098894
- `fisher_gain_lcb`: 0.005123357708534053
- `recovered_headroom`: 0.2537151792233236
- `positive_repetitions`: 5
- `permutation_gain`: -0.43629502311294743
- `null_false_success_rate`: 0.0
- `hazard_relative_degradation`: 0.012987190815336058
- `gauge_max_difference`: 1.1322002363423067e-11
- `refusal_rate`: 0.8
- `selected_physical_replay_max_difference`: 0.0
- `common_creation_shift_geometry_error`: 1.0
- `baseline_creation_geometry`: 0.7347195720209945
- `fisher_creation_geometry`: 0.805421381565019

## Gates

- PASS: `oracle_headroom`
- PASS: `fisher_gain`
- PASS: `absolute_geometry`
- FAIL: `headroom_recovery`
- FAIL: `repetition_stability`
- PASS: `hazard_noninferiority`
- PASS: `permutation_null`
- PASS: `no_creation_specificity`
- PASS: `gauge_invariance`
- FAIL: `refusal_control`
- PASS: `implementation_replay`
- FAIL: `common_shift_invariance`

## Boundary

Finite synthetic, response-safe creation-estimator intervention only. A pass would identify recoverable stable author derivative structure under the registered opportunity budget. It would not identify personality, validate natural text, reopen M4-C.2, or authorize M4-D.

M4-D remains blocked independently of this result.
