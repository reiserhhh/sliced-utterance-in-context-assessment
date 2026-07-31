# SUICA M4-C.3.4 Creation Residual Attribution

## Decision

`M4_C34_NO_GO_THREE_FACTOR_INCOMPLETE`

The high-information `K=8 excitation` endpoint was fixed. The diagnostic cube
crossed discovered/oracle chart (`C`), current joint/target-aligned
history-stratified hurdle likelihood (`S`), and Fisher-Wiener
pooled/author-local fit (`P`). Every cell estimates the same gate-zero direct
creation derivative. Oracle chart cells are truth-open attribution controls
and are not deployable.

## Cell means

|      c |      s |      p |   geometry |   geometry_gain |   recovered_headroom |
|-------:|-------:|-------:|-----------:|----------------:|---------------------:|
| 0.0000 | 0.0000 | 0.0000 |     0.7749 |          0.0000 |               0.0000 |
| 0.0000 | 0.0000 | 1.0000 |     0.7948 |          0.0199 |               0.2284 |
| 0.0000 | 1.0000 | 0.0000 |     0.7372 |         -0.0378 |              -1.2412 |
| 0.0000 | 1.0000 | 1.0000 |     0.7572 |         -0.0177 |              -0.8587 |
| 1.0000 | 0.0000 | 0.0000 |     0.8632 |          0.0883 |               0.7065 |
| 1.0000 | 0.0000 | 1.0000 |     0.8632 |          0.0883 |               0.7163 |
| 1.0000 | 1.0000 | 0.0000 |     0.8162 |          0.0413 |              -0.3555 |
| 1.0000 | 1.0000 | 1.0000 |     0.8132 |          0.0383 |              -0.4601 |

## World decomposition

| world                               |   baseline_geometry |   full_geometry |   oracle_headroom |   full_recovered_headroom |   observation_main_effect |   shapley_C |   shapley_S |   shapley_P |
|:------------------------------------|--------------------:|----------------:|------------------:|--------------------------:|--------------------------:|------------:|------------:|------------:|
| endogenous_creation_expansion       |              0.8019 |          0.9183 |            0.1250 |                    0.8276 |                   -0.0032 |      0.1158 |     -0.0040 |      0.0047 |
| endogenous_source_partition_matched |              0.6277 |          0.6881 |            0.2509 |                    0.2825 |                   -0.0824 |      0.1163 |     -0.0814 |      0.0255 |
| history_gated_ecology               |              0.9630 |          0.8945 |            0.0249 |                   -3.0316 |                   -0.0865 |      0.0136 |     -0.0874 |      0.0053 |
| selection_creation_compensation     |              0.6357 |          0.6329 |            0.0643 |                   -1.2043 |                   -0.0323 |      0.0293 |     -0.0318 |     -0.0003 |
| source_rotated_feedback             |              0.8463 |          0.9323 |            0.0972 |                    0.8003 |                   -0.0112 |      0.0885 |     -0.0122 |      0.0097 |

## Diagnostics

- `oracle_headroom`: 0.11243688130272014
- `oracle_headroom_lcb`: 0.07407284360025
- `joint_information_full_rank_coverage`: 1.0
- `source_at_risk_coverage`: 1.0
- `observation_main_effect`: -0.08441376596045991
- `observation_main_effect_lcb`: -0.15813271155224354
- `observation_positive_repetitions`: 0
- `full_recovered_headroom`: 0.340546968395607
- `target_world_recovered_headroom`: {"endogenous_source_partition_matched": 0.24071188326156612, "history_gated_ecology": -2.7524065290178545}
- `other_world_degradation`: 0.06652429566868068
- `shapley_means`: {"C": 0.07267837684855485, "P": 0.008968481044168024, "S": -0.04335681882922486}
- `leading_shapley_factor`: "C"
- `shapley_leading_margin`: 0.06370989580438685
- `shapley_leading_margin_lcb`: 0.039560269011194124
- `hazard_relative_degradation`: -0.07720778709728937
- `permutation_gain`: -0.6180518775879759
- `null_false_success_rate`: 0.0
- `gauge_max_difference`: 7.640020560639726e-11
- `common_shift_distance_error`: 8.881784197001252e-16
- `truth_open_alias_rate`: 0.875

## Gates

- PASS: `oracle_headroom`
- PASS: `joint_information`
- PASS: `source_at_risk`
- FAIL: `observation_main_effect`
- FAIL: `full_recovery`
- FAIL: `target_world_recovery`
- PASS: `other_world_noninferiority`
- PASS: `shapley_identifiability`
- PASS: `hazard_noninferiority`
- PASS: `permutation_null`
- PASS: `no_creation_specificity`
- PASS: `gauge_invariance`
- PASS: `common_shift_invariance`
- FAIL: `truth_open_alias`

## Boundary

Finite synthetic chart/observation/pooling attribution only. Oracle-chart cells are diagnostic and nondeployable. The result cannot identify personality, validate natural text, close M4-C.2, or authorize M4-D.

M4-D remains blocked independently of this result.
