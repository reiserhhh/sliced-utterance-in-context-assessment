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
| endogenous_creation_expansion       |        0.8174 |            0.7108 |            0.7329 |       0.9289 |          0.9301 |     0.1247 |      0.1115 |          0.2181 |          0.1960 |       -0.0012 |          0.3180 |
| endogenous_source_partition_matched |        0.7154 |            0.7118 |            0.6447 |       0.8827 |          0.8859 |     0.2292 |      0.1673 |          0.1709 |          0.2380 |       -0.0031 |          0.2765 |
| history_gated_ecology               |        0.8088 |            0.7802 |            0.7512 |       0.8631 |          0.8633 |     0.1412 |      0.0543 |          0.0829 |          0.1119 |       -0.0003 |          0.1508 |
| selection_creation_compensation     |        0.7229 |            0.6425 |            0.7274 |       0.7521 |          0.7514 |     0.0844 |      0.0292 |          0.1096 |          0.0247 |        0.0007 |          0.2760 |
| source_rotated_feedback             |        0.8667 |            0.8329 |            0.7344 |       0.9559 |          0.9562 |     0.0978 |      0.0891 |          0.1230 |          0.2214 |       -0.0004 |          0.2674 |

## Diagnostics

- `global_oracle_headroom`: 0.13545794193625876
- `eligible_oracle_headroom`: 0.15056910223299372
- `oracle_headroom_lcb`: 0.11193125925680121
- `oracle_estimator_gain`: 0.12422583254190449
- `oracle_estimator_gain_lcb`: 0.09481106587420216
- `oracle_estimator_recovered_headroom`: 0.8250419953336434
- `global_rcca_gain`: 0.09029708845096149
- `rcca_gain`: 0.12265988735542449
- `rcca_gain_lcb`: 0.09338350773196259
- `rcca_variance_rank_gain`: 0.14089818594402856
- `rcca_variance_rank_gain_lcb`: 0.10827074956198636
- `rcca_repeatability_rank_gain`: 0.15841794858017968
- `rcca_repeatability_rank_gain_lcb`: 0.12447194956711603
- `rcca_recovered_headroom`: 0.8146418191802596
- `rcca_recovered_headroom_lcb`: 0.6798446097086764
- `rcca_recovery_ratio_valid_bootstrap_rate`: 1.0
- `rcca_accessible_efficiency`: 0.987394367544675
- `rcca_accessible_efficiency_lcb`: 0.9800820922657101
- `rcca_accessible_ratio_valid_bootstrap_rate`: 1.0
- `rcca_oracle_noninferiority_lcb`: -0.0025965387958768716
- `positive_repetitions`: 8
- `positive_worlds`: 3
- `minimum_world_gain`: 0.029225987915827478
- `eligible_worlds`: {"endogenous_creation_expansion": {"gain": 0.11151121605667061, "headroom": 0.12469268699215225, "headroom_lcb": 0.06082297381762616, "positive_repetitions": 8, "ratio_valid_bootstrap_rate": 1.0, "recovery": 0.8942883399704809, "recovery_lcb": 0.7642507729319344}, "endogenous_source_partition_matched": {"gain": 0.16734246503870215, "headroom": 0.22921616148056323, "headroom_lcb": 0.12866975494370708, "positive_repetitions": 7, "ratio_valid_bootstrap_rate": 1.0, "recovery": 0.7300639883234945, "recovery_lcb": 0.43516095468462}, "source_rotated_feedback": {"gain": 0.08912598097090074, "headroom": 0.09779845822626573, "headroom_lcb": 0.05908251007014374, "positive_repetitions": 8, "ratio_valid_bootstrap_rate": 1.0, "recovery": 0.9113229654878565, "recovery_lcb": 0.856888913891554}}
- `sentinel_worlds`: {"history_gated_ecology": {"gain": 0.05427979227270639, "gain_lcb": 0.006538314663888586}}
- `boundary_worlds`: {"selection_creation_compensation": {"oracle_fidelity": 0.000706646294881555, "oracle_fidelity_lcb": -0.00025785210778526827}}
- `cka_gain_rcca_baseline`: 0.25772747324069256
- `cka_gain_rcca_baseline_lcb`: 0.21634326103874765
- `cka_gain_rcca_variance_rank`: 0.1884004191058966
- `cka_gain_rcca_variance_rank_lcb`: 0.16455459235681028
- `cka_gain_rcca_repeatability_rank`: 0.30076557845118945
- `cka_gain_rcca_repeatability_rank_lcb`: 0.25702426195758343
- `cka_permutation_p_maximum`: 0.005
- `hazard_relative_degradation`: -0.26190468971750536
- `hazard_relative_degradation_ucb`: -0.049609836185187876
- `author_permutation_gain`: -0.5120971423898419
- `null_false_successes`: 0
- `null_trials`: 120
- `null_false_success_rate`: 0.0
- `null_false_success_wilson_upper`: 0.031019166418703486
- `native_rcca_refusal_rate`: 0.0125
- `same_rank_control_coverage`: 1.0
- `basis_contract_pass_rate`: 1.0
- `source_shuffle_zero_rank_or_refusal_rate`: 1.0
- `support_shift_refusal_rate`: 1.0
- `alias_false_recovery_rate`: 0.0
- `downstream_gauge_max_error`: 2.307876112439544e-14
- `downstream_common_shift_max_error`: 1.4689638394571602e-14

## Gates

- PASS: `oracle_headroom`
- PASS: `oracle_estimator_ceiling`
- PASS: `rcca_absolute_gain`
- PASS: `same_rank_superiority`
- PASS: `headroom_recovery`
- PASS: `accessible_efficiency`
- PASS: `repetition_consistency`
- PASS: `world_consistency`
- PASS: `oracle_gram_alignment`
- PASS: `hazard_noninferiority`
- PASS: `author_permutation_null`
- PASS: `null_specificity`
- FAIL: `chart_native_acceptance`
- PASS: `source_shuffle`
- PASS: `support_shift`
- PASS: `observable_alias`
- PASS: `downstream_invariance`

## Boundary

Finite-synthetic conditional paired chart effect only. RCCA saw pre-response condition tensors only; response and oracle truth were opened only after every chart arm was frozen for scoring. No personality, natural-text, clinical, or M4-D claim follows.
