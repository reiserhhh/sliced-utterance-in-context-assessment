# SUICA M4-C.3.5-R2 Response-Safe Chart Replacement

## Decision

`M4_C35_R2B_PARTIAL_CONDITIONAL_EFFECT`

This paired experiment holds the C3.4 gate-zero estimand, physical anchor,
current observation law, and Fisher-Wiener pooling fixed. It compares the old
response-safe chart (`B0`), its top-variance rank match (`Br_var`), its
repeatability-selected rank match (`Br_rep`), the frozen RCCA spectral-block
chart (`R`), and the truth-open oracle chart with the same estimator (`Oest`).
The oracle creation swap remains only the scoring denominator.

## Main-world means

| world                               |   geometry_B0 |   geometry_Br_var |   geometry_Br_rep |   geometry_R |   geometry_Oest |   headroom |   gain_R_B0 |   gain_R_Br_var |   gain_R_Br_rep |   gain_R_Oest |   cka_gain_R_B0 |
|:------------------------------------|--------------:|------------------:|------------------:|-------------:|----------------:|-----------:|------------:|----------------:|----------------:|--------------:|----------------:|
| endogenous_creation_expansion       |        0.7094 |            0.7640 |            0.6766 |       0.9200 |          0.9192 |     0.2122 |      0.2106 |          0.1560 |          0.2434 |        0.0008 |          0.2630 |
| endogenous_source_partition_matched |        0.8295 |            0.8113 |            0.7627 |       0.9665 |          0.9668 |     0.1492 |      0.1369 |          0.1552 |          0.2038 |       -0.0003 |          0.2553 |
| history_gated_ecology               |        0.9565 |            0.9230 |            0.9295 |       0.9564 |          0.9563 |     0.0117 |     -0.0001 |          0.0334 |          0.0268 |        0.0001 |          0.1134 |
| selection_creation_compensation     |        0.8001 |            0.8084 |            0.5350 |       0.8525 |          0.8445 |     0.0831 |      0.0524 |          0.0441 |          0.3175 |        0.0080 |          0.3606 |
| source_rotated_feedback             |        0.8700 |            0.8376 |            0.7565 |       0.8841 |          0.8831 |     0.0399 |      0.0141 |          0.0466 |          0.1277 |        0.0011 |          0.2521 |

## Diagnostics

- `global_oracle_headroom`: 0.0992298076255296
- `eligible_oracle_headroom`: 0.13378012361969585
- `oracle_headroom_lcb`: 0.07950783619232826
- `oracle_estimator_gain`: 0.12004537352130935
- `oracle_estimator_gain_lcb`: 0.06594902423779432
- `oracle_estimator_recovered_headroom`: 0.8973334025506582
- `global_rcca_gain`: 0.08279602750190986
- `rcca_gain`: 0.12055119568488554
- `rcca_gain_lcb`: 0.06875708961270459
- `rcca_variance_rank_gain`: 0.08703868324189176
- `rcca_variance_rank_gain_lcb`: 0.07952635599694424
- `rcca_repeatability_rank_gain`: 0.18384818390165977
- `rcca_repeatability_rank_gain_lcb`: 0.16215014931592464
- `rcca_recovered_headroom`: 0.901114398934053
- `rcca_recovered_headroom_lcb`: 0.8647838113262474
- `rcca_recovery_ratio_valid_bootstrap_rate`: 1.0
- `rcca_accessible_efficiency`: 1.00421359148411
- `rcca_accessible_efficiency_lcb`: 0.9896841433585029
- `rcca_accessible_ratio_valid_bootstrap_rate`: 1.0
- `rcca_oracle_noninferiority_lcb`: -0.0017964210477579012
- `positive_repetitions`: 2
- `positive_worlds`: 3
- `minimum_world_gain`: -9.028404750327512e-05
- `eligible_worlds`: {"endogenous_creation_expansion": {"gain": 0.21060490311827218, "headroom": 0.2122230710466006, "headroom_lcb": 0.03538440169456236, "positive_repetitions": 2, "ratio_valid_bootstrap_rate": 1.0, "recovery": 0.9923751554421097, "recovery_lcb": 0.9812570286142697}, "endogenous_source_partition_matched": {"gain": 0.13694006528231117, "headroom": 0.14919091603583573, "headroom_lcb": 0.1413848183901658, "positive_repetitions": 2, "ratio_valid_bootstrap_rate": 1.0, "recovery": 0.9178847407131551, "recovery_lcb": 0.9034777483053348}, "source_rotated_feedback": {"gain": 0.014108618654073257, "headroom": 0.03992638377665125, "headroom_lcb": 0.03371067435238573, "positive_repetitions": 2, "ratio_valid_bootstrap_rate": 1.0, "recovery": 0.35336580274830465, "recovery_lcb": 0.22332097239390514}}
- `sentinel_worlds`: {"history_gated_ecology": {"gain": -9.028404750327512e-05, "gain_lcb": -0.0032363358566567246}}
- `boundary_worlds`: {"selection_creation_compensation": {"oracle_fidelity": 0.008045697617890035, "oracle_fidelity_lcb": 0.001423709979859522}}
- `cka_gain_rcca_baseline`: 0.248874946933547
- `cka_gain_rcca_baseline_lcb`: 0.24260225327001045
- `cka_gain_rcca_variance_rank`: 0.1458112110688619
- `cka_gain_rcca_variance_rank_lcb`: 0.14211853002320457
- `cka_gain_rcca_repeatability_rank`: 0.3031821101976643
- `cka_gain_rcca_repeatability_rank_lcb`: 0.2773563730092496
- `cka_permutation_p_maximum`: 0.005
- `hazard_relative_degradation`: -0.053341015446552675
- `hazard_relative_degradation_ucb`: -0.033051955905976316
- `author_permutation_gain`: -0.6174435724703103
- `null_false_successes`: 0
- `null_trials`: 6
- `null_false_success_rate`: 0.0
- `null_false_success_wilson_upper`: 0.39033428790216534
- `native_rcca_refusal_rate`: 0.0
- `same_rank_control_coverage`: 1.0
- `basis_contract_pass_rate`: 1.0
- `source_shuffle_zero_rank_or_refusal_rate`: 1.0
- `support_shift_refusal_rate`: 1.0
- `alias_false_recovery_rate`: 0.0
- `downstream_gauge_max_error`: 1.2078879563226508e-14
- `downstream_common_shift_max_error`: 8.066464163292153e-15

## Gates

- PASS: `oracle_headroom`
- PASS: `oracle_estimator_ceiling`
- PASS: `rcca_absolute_gain`
- PASS: `same_rank_superiority`
- PASS: `headroom_recovery`
- PASS: `accessible_efficiency`
- PASS: `repetition_consistency`
- FAIL: `world_consistency`
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

Finite-synthetic conditional paired chart effect only. RCCA saw pre-response condition tensors only; response and oracle truth were opened only after every chart arm was frozen for scoring. No personality, natural-text, clinical, or M4-D claim follows.
