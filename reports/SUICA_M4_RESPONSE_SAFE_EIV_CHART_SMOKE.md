# SUICA M4-C.3.5 Response-Safe Cross-View EIV Chart

## Decision

`M4_C35_NO_GO_RESPONSE_SAFE_CHART_IDENTIFICATION`

The C3.4 gate-zero direct-creation estimand, `K=8` excitation, discovered
`C0` response/choice anchor, and truth-open oracle ceiling were held fixed.
Only the condition basis supplied to the Fisher-Wiener creation estimator was
changed. The EIV chart was fitted from replicated pre-response condition
tensors and compared with same-rank source-1 PCA and a source-shuffled null.

## Chart comparison

| chart       |   geometry |   geometry_gain |   recovered_headroom |   evaluation_loss |
|:------------|-----------:|----------------:|---------------------:|------------------:|
| c0          |     0.8522 |          0.0000 |               0.0000 |            0.4318 |
| eiv         |     0.5293 |         -0.3229 |             -37.6559 |            0.4787 |
| pca         |     0.5142 |         -0.3380 |             -38.6781 |            0.4751 |
| shuffle_eiv |     0.3758 |         -0.4765 |             -30.4205 |            0.4910 |

## Main-world recovered headroom

| world                               |     c0 |      eiv |      pca |
|:------------------------------------|-------:|---------:|---------:|
| endogenous_source_partition_matched | 0.0000 |   0.5117 |   0.4085 |
| history_gated_ecology               | 0.0000 | -75.8235 | -77.7647 |

## Controls

| world_type   | control                  |     value |   pass_rate |
|:-------------|:-------------------------|----------:|------------:|
| invariance   | common_shift             |  0.000000 |    1.000000 |
| invariance   | orthogonal_gauge         |  0.000000 |    1.000000 |
| invariance   | response_bytes           |  0.000000 |    1.000000 |
| main         | source_condition_shuffle | -0.259168 |    1.000000 |
| null         | source_condition_shuffle | -0.126774 |    1.000000 |
| refusal      | chart_refusal            |  0.500000 |    0.500000 |

## Diagnostics

- `mean_recovered_headroom`: -37.65589616128116
- `recovered_headroom_lcb`: -37.65589616128116
- `positive_repetitions`: 0
- `mean_advantage_over_same_rank_pca`: 1.0222314277823714
- `pca_advantage_lcb`: 1.0222314277823714
- `oracle_headroom`: 0.06294471811713193
- `oracle_headroom_lcb`: 0.06294471811713193
- `target_world_recovered_headroom`: {"endogenous_source_partition_matched": 0.5117370892018778, "history_gated_ecology": -75.8235294117642}
- `other_world_gain`: 0.0
- `hazard_relative_degradation`: 0.10862308247671826
- `shuffle_gain`: -0.4764641488779419
- `null_false_success_rate`: 0.0
- `selected_rank_mean`: 3.5
- `principal_angle_maximum`: 83.11731919896788
- `coverage_minimum`: 0.984375
- `singular_margin_minimum`: -4.0226752531907
- `target_chart_refusal_rate`: 0.5
- `gauge_max_error`: 4.440892098500626e-15
- `common_shift_max_error`: 2.3092638912203256e-14
- `response_hash_failures`: 0
- `alias_false_recovery_rate`: 0.0
- `forbidden_refusal_rate`: 1.0
- `support_refusal_rate`: 0.0
- `topology_refusal_rate`: 0.0

## Gates

- FAIL: `recovered_headroom`
- PASS: `same_rank_pca_advantage`
- PASS: `oracle_headroom`
- FAIL: `target_world_recovery`
- PASS: `other_world_noninferiority`
- PASS: `hazard_noninferiority`
- PASS: `source_shuffle_null`
- PASS: `no_creation_specificity`
- FAIL: `chart_stability`
- PASS: `gauge_invariance`
- PASS: `common_shift_invariance`
- PASS: `response_safety`
- PASS: `alias_safety`
- PASS: `forbidden_provenance_refusal`
- PASS: `support_shift_refusal`

## Boundary

Finite synthetic response-safe condition-chart evidence only. The chart uses no response, author identity, mechanism label, synthetic truth, Big Five, or MBTI during fitting. A pass would still require a separately frozen C2 transport confirmation; it cannot identify personality, validate natural text, or authorize M4-D.

M4-D remains blocked independently of this result.
