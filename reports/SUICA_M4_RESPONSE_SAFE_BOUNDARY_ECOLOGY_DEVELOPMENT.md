# SUICA M4-C.3.5-R2C Boundary Ecology Development

## Decision

`M4_C35_R2C_BOUNDARY_ECOLOGY_DEVELOPMENT_COMPLETE`

Mechanism classification:
`FALSE_REFUSAL_RISK`

The same response truth is scored across native and outcome-blind
pre-response support interventions. `Pi` uses `R` above the frozen `.80`
coverage boundary and `B0` below it.

## Eligible worlds by coverage

| variant             |   minimum_coverage | accepted   |   forced_r_gain |   oracle_error |   policy_value |   routing_value |
|:--------------------|-------------------:|:-----------|----------------:|---------------:|---------------:|----------------:|
| evaluation_count_10 |             0.6250 | False      |          0.1318 |         0.1749 |         0.0000 |         -0.1318 |
| evaluation_count_11 |             0.6875 | False      |          0.1165 |         0.1696 |         0.0000 |         -0.1165 |
| evaluation_count_12 |             0.7500 | False      |          0.0156 |         0.2349 |         0.0000 |         -0.0156 |
| evaluation_count_13 |             0.8125 | True       |         -0.0222 |         0.2491 |        -0.0222 |          0.0000 |
| native              |             1.0000 | True       |          0.0472 |        -0.0010 |         0.0472 |          0.0000 |
| native              |             0.9375 | True       |          0.1176 |        -0.0022 |         0.1176 |          0.0000 |

## Eligible worlds by boundary side

| world                               | accepted   |   forced_r_gain |   oracle_error |   routing_value |
|:------------------------------------|:-----------|----------------:|---------------:|----------------:|
| endogenous_creation_expansion       | False      |          0.0356 |         0.1084 |         -0.0356 |
| endogenous_creation_expansion       | True       |          0.0017 |         0.0804 |          0.0000 |
| endogenous_source_partition_matched | False      |          0.3411 |         0.2846 |         -0.3411 |
| endogenous_source_partition_matched | True       |          0.1382 |         0.1967 |          0.0000 |
| source_rotated_feedback             | False      |         -0.1128 |         0.1864 |          0.1128 |
| source_rotated_feedback             | True       |         -0.0497 |         0.0942 |          0.0000 |

## Diagnostics

- `policy_value`: 0.012030465078593422
- `policy_value_lcb`: -0.006098108664953583
- `routing_value_over_forced_r`: -0.05278792508739032
- `routing_value_lcb`: -0.08241914947797299
- `routing_value_ucb`: -0.023156700696807652
- `accepted_forced_r_gain`: 0.03007616269648355
- `refused_forced_r_gain`: 0.08797987514565053
- `harmful_cells`: 13
- `eligible_cells`: 30
- `harm_auc`: 0.5542986425339367
- `harm_auc_lcb`: 0.5535714285714286
- `harm_auc_bootstrap_valid_rate`: 1.0
- `oracle_error_relation`: {"permutation_p": 0.001, "r2": 0.04605823631683259, "slope": 0.30533523062821, "spearman_rho": 0.38290877657416594}
- `acceptance_rate`: 0.4
- `maximum_basis_replay_error`: 0.0
- `null_maximum_absolute_forced_gain`: 0.0

## Boundary

Finite-synthetic support-boundary development only. It identifies neither natural-text transport nor personality, behavioral, clinical, or M4-D validity.
