# SUICA M4-C.3.5-R2 Response-Safe Chart Replacement

## Decision

`M4_C35_R2_READY_TO_FREEZE`

This paired experiment holds the C3.4 gate-zero estimand, physical anchor,
current observation law, and Fisher-Wiener pooling fixed. It compares the old
response-safe chart (`B0`), its RCCA-rank truncation (`Br`), the frozen RCCA
spectral-block chart (`R`), and the truth-open oracle chart with the same
estimator (`Oest`). The oracle creation swap remains only the scoring
denominator.

## Main-world means

| world                               |   geometry_B0 |   geometry_Br |   geometry_R |   geometry_Oest |   headroom |   gain_R_B0 |   gain_R_Br |   cka_gain_R_B0 |
|:------------------------------------|--------------:|--------------:|-------------:|----------------:|-----------:|------------:|------------:|----------------:|
| endogenous_creation_expansion       |        0.8228 |        0.8045 |       0.9556 |          0.9578 |     0.1500 |      0.1328 |      0.1511 |          0.1841 |
| endogenous_source_partition_matched |        0.6271 |        0.6824 |       0.8818 |          0.8823 |     0.2708 |      0.2547 |      0.1994 |          0.3594 |
| history_gated_ecology               |        0.9713 |        0.9561 |       0.9759 |          0.9767 |     0.0232 |      0.0046 |      0.0198 |          0.0345 |
| selection_creation_compensation     |        0.7842 |        0.7993 |       0.7775 |          0.7796 |    -0.0194 |     -0.0066 |     -0.0218 |          0.3746 |
| source_rotated_feedback             |        0.8847 |        0.8277 |       0.9512 |          0.9516 |     0.0787 |      0.0665 |      0.1235 |          0.3144 |

## Diagnostics

- `oracle_headroom`: 0.10067157441488991
- `oracle_headroom_lcb`: 0.05846933814848254
- `oracle_estimator_gain`: 0.091582054309327
- `oracle_estimator_gain_lcb`: 0.05050628515869156
- `oracle_estimator_recovered_headroom`: 0.9097111557220414
- `rcca_gain`: 0.09040141676505309
- `rcca_gain_lcb`: 0.049696506701854236
- `rcca_same_rank_gain`: 0.09438572123064097
- `rcca_same_rank_gain_lcb`: 0.07209945135078825
- `rcca_recovered_headroom`: 0.8979835399463286
- `rcca_recovered_headroom_lcb`: 0.8499584273666695
- `rcca_accessible_efficiency`: 0.9871084182029134
- `rcca_accessible_efficiency_lcb`: 0.9839667785050319
- `positive_repetitions`: 2
- `positive_worlds`: 4
- `minimum_world_gain`: -0.006621987638030513
- `high_headroom_world_recovery`: {"endogenous_creation_expansion": 0.8857910337161904, "endogenous_source_partition_matched": 0.940535272316906, "source_rotated_feedback": 0.8442102478172675}
- `cka_gain_rcca_baseline`: 0.25338528674365957
- `cka_gain_rcca_baseline_lcb`: 0.24860940144353588
- `cka_gain_rcca_same_rank`: 0.16787273872482208
- `cka_gain_rcca_same_rank_lcb`: 0.1506889543038098
- `hazard_relative_degradation`: -0.044277871882335784
- `author_permutation_gain`: -0.5325501770956316
- `null_false_success_rate`: 0.0
- `native_rcca_refusal_rate`: 0.0
- `same_rank_control_coverage`: 1.0
- `source_shuffle_zero_rank_or_refusal_rate`: 1.0
- `support_shift_refusal_rate`: 1.0
- `alias_false_recovery_rate`: 0.0
- `downstream_gauge_max_error`: 8.87744738831131e-15
- `downstream_common_shift_max_error`: 9.114887664085636e-15

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
- PASS: `chart_native_acceptance`
- PASS: `source_shuffle`
- PASS: `support_shift`
- PASS: `observable_alias`
- PASS: `downstream_invariance`

## Boundary

Finite-synthetic paired chart replacement only. RCCA saw pre-response condition tensors only; response and oracle truth were opened only after every chart arm was frozen for scoring. No personality, natural-text, clinical, or M4-D claim follows.
