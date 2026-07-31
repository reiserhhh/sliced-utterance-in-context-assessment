# SUICA M4-C.3.5-R1 Response-Safe RCCA Chart

## Decision

`M4_C35_R1_READY_TO_FREEZE`

This gate sees only replicated pre-response condition tensors. It estimates
within-source repeatable supports from four fixed author blocks, freezes
regularized whiteners, identifies cross-source spectral blocks, and evaluates
projector/Gram objects rather than named canonical axes.

## World diagnostics

| world                               |   support_rank_source_1 |   support_rank_source_2 |   shared_rank |   projector_affinity_minimum |   heldout_source_cka |   condition_number_maximum |   coverage |
|:------------------------------------|------------------------:|------------------------:|--------------:|-----------------------------:|---------------------:|---------------------------:|-----------:|
| endogenous_creation_expansion       |                  6.0000 |                  6.0000 |        6.0000 |                       0.9988 |               0.9981 |                    40.3000 |     0.9062 |
| endogenous_source_partition_matched |                  6.0000 |                  6.0000 |        6.0000 |                       0.9988 |               0.9985 |                    31.7843 |     0.9531 |
| history_gated_ecology               |                  6.0000 |                  6.0000 |        6.0000 |                       0.9999 |               0.9997 |                     3.4689 |     1.0000 |
| selection_creation_compensation     |                  6.0000 |                  6.0000 |        6.0000 |                       0.9991 |               0.9987 |                    29.2405 |     0.9375 |
| source_rotated_feedback             |                  6.0000 |                  6.0000 |        6.0000 |                       0.9987 |               0.9985 |                    34.1165 |     0.9609 |

## Controls

| control          | world                               |    value |   pass_rate |
|:-----------------|:------------------------------------|---------:|------------:|
| common_shift     | invariance                          | 0.000000 |    1.000000 |
| orthogonal_gauge | invariance                          | 0.000000 |    1.000000 |
| refusal          | author_leakage                      | 1.000000 |    1.000000 |
| refusal          | evaluation_support_shift            | 1.000000 |    1.000000 |
| refusal          | response_leakage_circular           | 1.000000 |    1.000000 |
| refusal          | topology_mismatch                   | 0.000000 |    0.000000 |
| response_hash    | invariance                          | 0.000000 |    1.000000 |
| source_shuffle   | endogenous_creation_expansion       | 0.000000 |    1.000000 |
| source_shuffle   | endogenous_source_partition_matched | 0.000000 |    1.000000 |
| source_shuffle   | history_gated_ecology               | 0.000000 |    1.000000 |
| source_shuffle   | selection_creation_compensation     | 0.000000 |    1.000000 |
| source_shuffle   | source_rotated_feedback             | 0.000000 |    1.000000 |

## Diagnostics

- `projector_affinity_mean`: 0.9990530884422281
- `projector_affinity_lcb`: 0.998962015322193
- `heldout_source_cka_mean`: 0.9987077774718734
- `heldout_source_cka_lcb`: 0.9986911748702271
- `rank_resolved_rate`: 1.0
- `rank_pattern_frequency`: 1.0
- `support_stability_minimum`: 0.9347860776828102
- `support_stability_lcb_minimum`: 0.8695846701277128
- `consensus_concentration_minimum`: 0.9349261496245228
- `consensus_minimum_eigenvalue`: 0.7838134587220379
- `consensus_eigengap_lcb_minimum`: 0.5385757588205253
- `rank_boundary_lcb_minimum`: 0.6375599445701414
- `next_boundary_ucb_maximum`: -0.14044020601454402
- `native_consensus_affinity_minimum`: 0.9990290385700055
- `condition_number_maximum`: 42.970262704631644
- `canonical_singular_maximum`: 0.9996281869038373
- `negative_spectral_mass_maximum`: 1.3932260723815145e-05
- `asymmetric_mass_maximum`: 0.0065719494965267205
- `coverage_minimum`: 0.875
- `native_refusal_rate`: 0.0
- `null_false_positives`: 4
- `null_trials`: 250
- `null_fpr_upper`: 0.04040980934111917
- `source_shuffle_zero_rank_rate`: 1.0
- `response_hash_failures`: 0
- `gauge_max_error`: 1.7319479184152442e-14
- `common_shift_max_error`: 3.108624468950438e-14
- `alias_false_recovery_rate`: 0.0
- `forbidden_refusal_rate`: 1.0
- `support_shift_refusal_rate`: 1.0
- `topology_refusal_rate`: 0.0

## Gates

- PASS: `projector_stability`
- PASS: `heldout_gram_stability`
- PASS: `rank_identification`
- PASS: `support_consensus`
- PASS: `numerical_contract`
- PASS: `replicate_model`
- PASS: `coverage`
- PASS: `null_specificity`
- PASS: `source_shuffle`
- PASS: `response_safety`
- PASS: `gauge_invariance`
- PASS: `common_shift_invariance`
- PASS: `alias_safety`
- PASS: `forbidden_refusal`
- PASS: `support_shift_refusal`

## Boundary

Pure finite-synthetic pre-response chart evidence only. No response, mechanism endpoint, truth, personality label, or downstream headroom selected this chart. READY_TO_FREEZE means only that a separate confirmation protocol may be sealed.
