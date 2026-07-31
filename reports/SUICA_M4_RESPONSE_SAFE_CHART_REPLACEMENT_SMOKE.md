# SUICA M4-C.3.5-R2 Response-Safe Chart Replacement

## Decision

`M4_C35_R2_SMOKE_COMPLETE`

This paired experiment holds the C3.4 gate-zero estimand, physical anchor,
current observation law, and Fisher-Wiener pooling fixed. It compares the old
response-safe chart (`B0`), its top-variance rank match (`Br_var`), its
repeatability-selected rank match (`Br_rep`), the frozen RCCA spectral-block
chart (`R`), and the truth-open oracle chart with the same estimator (`Oest`).
The oracle creation swap remains only the scoring denominator.

## Main-world means

| world                               |   geometry_B0 |   geometry_Br_var |   geometry_Br_rep |   geometry_R |   geometry_Oest |   headroom |   gain_R_B0 |   gain_R_Br_var |   gain_R_Br_rep |   cka_gain_R_B0 |
|:------------------------------------|--------------:|------------------:|------------------:|-------------:|----------------:|-----------:|------------:|----------------:|----------------:|----------------:|
| endogenous_source_partition_matched |        0.8560 |            0.6393 |            0.7690 |       0.7198 |          0.8161 |     0.0290 |     -0.1363 |          0.0805 |         -0.0493 |          0.5152 |
| history_gated_ecology               |        0.7291 |            0.4083 |            0.6240 |       0.7964 |          0.7871 |     0.1959 |      0.0673 |          0.3881 |          0.1724 |          0.3051 |

## Diagnostics

- `global_oracle_headroom`: 0.1124794745484401
- `eligible_oracle_headroom`: 0.029009304871373875
- `oracle_headroom_lcb`: 0.029009304871373875
- `oracle_estimator_gain`: -0.03995621237000546
- `oracle_estimator_gain_lcb`: -0.03995621237000546
- `oracle_estimator_recovered_headroom`: -1.3773584905660354
- `rcca_gain`: -0.03448275862068956
- `rcca_gain_lcb`: -0.03448275862068956
- `rcca_variance_rank_gain`: 0.23426382047071703
- `rcca_variance_rank_gain_lcb`: 0.23426382047071703
- `rcca_repeatability_rank_gain`: 0.06157635467980299
- `rcca_repeatability_rank_gain_lcb`: 0.06157635467980299
- `rcca_recovered_headroom`: -4.698113207547162
- `rcca_recovered_headroom_lcb`: -4.698113207547162
- `rcca_recovery_ratio_valid_bootstrap_rate`: 1.0
- `rcca_accessible_efficiency`: NaN
- `rcca_accessible_efficiency_lcb`: NaN
- `rcca_accessible_ratio_valid_bootstrap_rate`: 0.0
- `rcca_oracle_noninferiority_lcb`: -0.09633278598795836
- `positive_repetitions`: 0
- `positive_worlds`: 1
- `minimum_world_gain`: -0.13628899835796382
- `eligible_worlds`: {"endogenous_source_partition_matched": {"gain": -0.13628899835796382, "headroom": 0.029009304871373875, "headroom_lcb": 0.029009304871373875, "ratio_valid_bootstrap_rate": 1.0, "recovery": -4.698113207547162, "recovery_lcb": -4.698113207547162}}
- `sentinel_worlds`: {"history_gated_ecology": {"gain": 0.0673234811165847, "gain_lcb": 0.0673234811165847}}
- `cka_gain_rcca_baseline`: 0.41016272128703746
- `cka_gain_rcca_baseline_lcb`: 0.41016272128703746
- `cka_gain_rcca_variance_rank`: 0.21570859113513363
- `cka_gain_rcca_variance_rank_lcb`: 0.21570859113513363
- `cka_gain_rcca_repeatability_rank`: 0.3951013297404567
- `cka_gain_rcca_repeatability_rank_lcb`: 0.3951013297404567
- `cka_permutation_p_maximum`: 0.05
- `hazard_relative_degradation`: 0.18582927653713965
- `author_permutation_gain`: -0.33552271483305973
- `null_false_successes`: 0
- `null_trials`: 1
- `null_false_success_rate`: 0.0
- `null_false_success_wilson_upper`: 0.7934506856227626
- `native_rcca_refusal_rate`: 0.0
- `same_rank_control_coverage`: 1.0
- `basis_contract_pass_rate`: 1.0
- `source_shuffle_zero_rank_or_refusal_rate`: 1.0
- `support_shift_refusal_rate`: 1.0
- `alias_false_recovery_rate`: 0.0
- `downstream_gauge_max_error`: 4.87088971587446e-12
- `downstream_common_shift_max_error`: 5.886404211286056e-12

## Gates

- PASS: `oracle_headroom`
- FAIL: `oracle_estimator_ceiling`
- FAIL: `rcca_absolute_gain`
- PASS: `same_rank_superiority`
- PASS: `headroom_recovery`
- FAIL: `accessible_efficiency`
- PASS: `repetition_consistency`
- PASS: `world_consistency`
- PASS: `oracle_gram_alignment`
- PASS: `hazard_noninferiority`
- PASS: `author_permutation_null`
- PASS: `null_specificity`
- PASS: `chart_native_acceptance`
- PASS: `source_shuffle`
- PASS: `support_shift`
- PASS: `observable_alias`
- PASS: `downstream_invariance`

## Boundary

Finite-synthetic paired chart replacement only. RCCA saw pre-response condition tensors only; response and oracle truth were opened only after every chart arm was frozen for scoring. No personality, natural-text, clinical, or M4-D claim follows.
