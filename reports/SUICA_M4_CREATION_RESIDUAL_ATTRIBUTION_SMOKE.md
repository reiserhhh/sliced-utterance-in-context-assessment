# SUICA M4-C.3.4 Creation Residual Attribution

## Decision

`M4_C34_NO_GO_OBSERVATION_LAW`

The high-information `K=8 excitation` endpoint was fixed. The diagnostic cube
crossed discovered/oracle chart (`C`), current/operator-complete creation law
(`S`), and Fisher-Wiener pooled/author-local fit (`P`). Oracle chart cells are
truth-open attribution controls and are not deployable.

## Cell means

|      c |      s |      p |   geometry |   geometry_gain |   recovered_headroom |
|-------:|-------:|-------:|-----------:|----------------:|---------------------:|
| 0.0000 | 0.0000 | 0.0000 |     0.7827 |          0.0000 |               0.0000 |
| 0.0000 | 0.0000 | 1.0000 |     0.8484 |          0.0657 |              -0.7844 |
| 0.0000 | 1.0000 | 0.0000 |     0.8112 |          0.0285 |              -1.6791 |
| 0.0000 | 1.0000 | 1.0000 |     0.8125 |          0.0298 |              -1.6463 |
| 1.0000 | 0.0000 | 0.0000 |     0.8166 |          0.0339 |              -0.0291 |
| 1.0000 | 0.0000 | 1.0000 |     0.9357 |          0.1530 |               0.9443 |
| 1.0000 | 1.0000 | 0.0000 |     0.7871 |          0.0044 |              -1.4022 |
| 1.0000 | 1.0000 | 1.0000 |     0.9086 |          0.1259 |               0.6022 |

## World decomposition

| world                               |   baseline_geometry |   full_geometry |   oracle_headroom |   full_recovered_headroom |   observation_main_effect |   shapley_C |   shapley_S |   shapley_P |
|:------------------------------------|--------------------:|----------------:|------------------:|--------------------------:|--------------------------:|------------:|------------:|------------:|
| endogenous_source_partition_matched |              0.6180 |          0.8582 |            0.2589 |                    0.9281 |                    0.0673 |      0.0219 |      0.0788 |      0.1396 |
| history_gated_ecology               |              0.9475 |          0.9589 |            0.0416 |                    0.2763 |                   -0.0993 |      0.0858 |     -0.0997 |      0.0254 |

## Diagnostics

- `oracle_headroom`: 0.1502463054187192
- `oracle_headroom_lcb`: 0.1502463054187192
- `joint_information_full_rank_coverage`: 1.0
- `source_at_risk_coverage`: 1.0
- `observation_main_effect`: -0.01600985221674879
- `observation_main_effect_lcb`: -0.01600985221674879
- `observation_positive_repetitions`: 0
- `full_recovered_headroom`: 0.8378870673952641
- `target_world_recovered_headroom`: {"endogenous_source_partition_matched": 0.9281183932346727, "history_gated_ecology": 0.2763157894736813}
- `other_world_degradation`: 0.0
- `shapley_means`: {"C": 0.05386790731618318, "P": 0.08246670315635832, "S": -0.010445174238277705}
- `leading_shapley_factor`: "P"
- `shapley_leading_margin`: 0.028598795840175134
- `shapley_leading_margin_lcb`: 0.028598795840175134
- `hazard_relative_degradation`: -0.20403026775019428
- `permutation_gain`: -0.5426929392446633
- `null_false_success_rate`: 0.0
- `gauge_max_difference`: 1.0807771344545358e-10
- `common_shift_distance_error`: 4.440892098500626e-16
- `truth_open_alias_rate`: 1.0

## Gates

- PASS: `oracle_headroom`
- PASS: `joint_information`
- PASS: `source_at_risk`
- FAIL: `observation_main_effect`
- PASS: `full_recovery`
- PASS: `target_world_recovery`
- PASS: `other_world_noninferiority`
- PASS: `shapley_identifiability`
- PASS: `hazard_noninferiority`
- PASS: `permutation_null`
- PASS: `no_creation_specificity`
- PASS: `gauge_invariance`
- PASS: `common_shift_invariance`
- PASS: `truth_open_alias`

## Boundary

Finite synthetic chart/observation/pooling attribution only. Oracle-chart cells are diagnostic and nondeployable. The result cannot identify personality, validate natural text, close M4-C.2, or authorize M4-D.

M4-D remains blocked independently of this result.
