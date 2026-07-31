# SUICA M4-C.3.5-R1 Response-Safe RCCA Chart

## Decision

`M4_C35_R1_CONFIRMATION_GO`

This gate sees only replicated pre-response condition tensors. It estimates
within-source repeatable supports from four fixed author blocks, freezes
regularized whiteners, identifies cross-source spectral blocks, and evaluates
projector/Gram objects rather than named canonical axes.

## World diagnostics

| world                               |   support_rank_source_1 |   support_rank_source_2 |   shared_rank |   projector_affinity_minimum |   heldout_source_cka |   condition_number_maximum |   coverage |
|:------------------------------------|------------------------:|------------------------:|--------------:|-----------------------------:|---------------------:|---------------------------:|-----------:|
| endogenous_creation_expansion       |                  6.0000 |                  6.0000 |        6.0000 |                       0.9987 |               0.9984 |                    36.7100 |     0.9629 |
| endogenous_source_partition_matched |                  6.0000 |                  6.0000 |        6.0000 |                       0.9981 |               0.9985 |                    34.6822 |     0.9531 |
| history_gated_ecology               |                  6.0000 |                  6.0000 |        6.0000 |                       0.9999 |               0.9997 |                     3.6813 |     0.9707 |
| selection_creation_compensation     |                  6.0000 |                  6.0000 |        6.0000 |                       0.9987 |               0.9985 |                    33.0706 |     0.9141 |
| source_rotated_feedback             |                  6.0000 |                  6.0000 |        6.0000 |                       0.9986 |               0.9984 |                    37.1951 |     0.9375 |

## Controls

| control          | world                               |    value |   pass_rate |
|:-----------------|:------------------------------------|---------:|------------:|
| common_shift     | invariance                          | 0.000000 |    1.000000 |
| orthogonal_gauge | invariance                          | 0.000000 |    1.000000 |
| refusal          | author_leakage                      | 1.000000 |    1.000000 |
| refusal          | evaluation_support_shift            | 1.000000 |    1.000000 |
| refusal          | response_leakage_circular           | 1.000000 |    1.000000 |
| refusal          | topology_mismatch                   | 0.500000 |    0.500000 |
| response_hash    | invariance                          | 0.000000 |    1.000000 |
| source_shuffle   | endogenous_creation_expansion       | 0.000000 |    1.000000 |
| source_shuffle   | endogenous_source_partition_matched | 0.000000 |    1.000000 |
| source_shuffle   | history_gated_ecology               | 0.000000 |    1.000000 |
| source_shuffle   | selection_creation_compensation     | 0.000000 |    1.000000 |
| source_shuffle   | source_rotated_feedback             | 0.000000 |    1.000000 |

## Diagnostics

- `projector_affinity_mean`: 0.9988001402574597
- `projector_affinity_lcb`: 0.9986169664782639
- `heldout_source_cka_mean`: 0.9987191586199111
- `heldout_source_cka_lcb`: 0.9986780516523324
- `rank_resolved_rate`: 1.0
- `rank_pattern_frequency`: 1.0
- `support_stability_minimum`: 0.9224622763023556
- `support_stability_lcb_minimum`: 0.8518756767217547
- `consensus_concentration_minimum`: 0.9231150826337253
- `consensus_minimum_eigenvalue`: 0.727350532280987
- `consensus_eigengap_lcb_minimum`: 0.4443004514783422
- `rank_boundary_lcb_minimum`: 0.5776328227763093
- `next_boundary_ucb_maximum`: -0.13696107349579126
- `native_consensus_affinity_minimum`: 0.998544786656996
- `condition_number_maximum`: 59.03032084057318
- `canonical_singular_maximum`: 0.9996704938431962
- `negative_spectral_mass_maximum`: 1.4119745041638813e-05
- `asymmetric_mass_maximum`: 0.007309649004266263
- `coverage_minimum`: 0.8125
- `native_refusal_rate`: 0.0
- `null_false_positives`: 7
- `null_trials`: 1000
- `null_fpr_upper`: 0.014378315465766588
- `source_shuffle_zero_rank_rate`: 1.0
- `response_hash_failures`: 0
- `gauge_max_error`: 2.220446049250313e-14
- `common_shift_max_error`: 4.263256414560601e-14
- `alias_false_recovery_rate`: 0.0
- `forbidden_refusal_rate`: 1.0
- `support_shift_refusal_rate`: 1.0
- `topology_refusal_rate`: 0.5

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

Pure finite-synthetic pre-response chart evidence only. No response, mechanism endpoint, truth, personality label, or downstream headroom selected this chart. CONFIRMATION_GO licenses the frozen chart only as a candidate observable replacement in a separate downstream experiment; it does not establish mechanism recovery or personality meaning.
