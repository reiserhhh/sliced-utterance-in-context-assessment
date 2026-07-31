# SUICA M4-C.3.5-R1 Response-Safe RCCA Chart

## Decision

`M4_C35_R1_SMOKE_COMPLETE`

This gate sees only replicated pre-response condition tensors. It estimates
within-source repeatable supports from four fixed author blocks, freezes
regularized whiteners, identifies cross-source spectral blocks, and evaluates
projector/Gram objects rather than named canonical axes.

## World diagnostics

| world                               |   support_rank_source_1 |   support_rank_source_2 |   shared_rank |   projector_affinity_minimum |   heldout_source_cka |   condition_number_maximum |   coverage |
|:------------------------------------|------------------------:|------------------------:|--------------:|-----------------------------:|---------------------:|---------------------------:|-----------:|
| endogenous_source_partition_matched |                  6.0000 |                  6.0000 |        6.0000 |                       0.9934 |               0.9966 |                    55.1855 |     0.9375 |
| history_gated_ecology               |                  6.0000 |                  6.0000 |        6.0000 |                       0.9993 |               0.9994 |                     3.7808 |     1.0000 |
| source_rotated_feedback             |                  6.0000 |                  6.0000 |        6.0000 |                       0.9921 |               0.9959 |                    59.6727 |     0.9375 |

## Controls

| control          | world                               |    value |   pass_rate |
|:-----------------|:------------------------------------|---------:|------------:|
| common_shift     | invariance                          | 0.000000 |    1.000000 |
| orthogonal_gauge | invariance                          | 0.000000 |    1.000000 |
| refusal          | author_leakage                      | 1.000000 |    1.000000 |
| refusal          | evaluation_support_shift            | 1.000000 |    1.000000 |
| refusal          | response_leakage_circular           | 1.000000 |    1.000000 |
| refusal          | topology_mismatch                   | 1.000000 |    1.000000 |
| response_hash    | invariance                          | 0.000000 |    1.000000 |
| source_shuffle   | endogenous_source_partition_matched | 1.000000 |    0.000000 |
| source_shuffle   | history_gated_ecology               | 0.000000 |    1.000000 |
| source_shuffle   | source_rotated_feedback             | 0.000000 |    1.000000 |

## Diagnostics

- `projector_affinity_mean`: 0.9949406212928258
- `projector_affinity_lcb`: 0.9949406212928258
- `heldout_source_cka_mean`: 0.9972828044136494
- `heldout_source_cka_lcb`: 0.9972828044136494
- `rank_resolved_rate`: 1.0
- `rank_pattern_frequency`: 1.0
- `support_stability_minimum`: 0.9475346217445886
- `support_stability_lcb_minimum`: 0.8955614793423795
- `consensus_concentration_minimum`: 0.9495396083396926
- `consensus_minimum_eigenvalue`: 0.8107998624135113
- `consensus_eigengap_lcb_minimum`: 0.5202712098565966
- `rank_boundary_lcb_minimum`: 0.39344922100161417
- `next_boundary_ucb_maximum`: -0.22410263310727585
- `native_consensus_affinity_minimum`: 0.9967843465350307
- `condition_number_maximum`: 59.67273879600799
- `canonical_singular_maximum`: 0.9996085162518834
- `negative_spectral_mass_maximum`: 3.318570216109024e-05
- `asymmetric_mass_maximum`: 0.01422573760517853
- `coverage_minimum`: 0.9375
- `native_refusal_rate`: 0.0
- `null_false_positives`: 1
- `null_trials`: 30
- `null_fpr_upper`: 0.16670390991409173
- `source_shuffle_zero_rank_rate`: 0.6666666666666666
- `response_hash_failures`: 0
- `gauge_max_error`: 2.042810365310288e-14
- `common_shift_max_error`: 1.865174681370263e-14
- `alias_false_recovery_rate`: 0.0
- `forbidden_refusal_rate`: 1.0
- `support_shift_refusal_rate`: 1.0
- `topology_refusal_rate`: 1.0

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
