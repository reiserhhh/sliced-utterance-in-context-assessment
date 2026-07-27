# SUICA V8 Full Technical Experiment Report

Overall status: `V8_TECHNICAL_CORE_NOT_CLOSED`

| phase           | status                                |
|:----------------|:--------------------------------------|
| v8_1_semantic   | V8_1_DOWNGRADE_RENDERER_ONLY          |
| v8_3_simulation | V8_3_ORACLE_IDENTIFICATION_PASS       |
| v8_2_evidence   | V8_2_EXPLANATION_FIDELITY_PASS        |
| v8_4_realtext   | V8_4_SEMANTIC_CANDIDATE_RENDERER_ONLY |

A completed phase may validly end in `NOT_CLOSED`; this is an empirical gate result, not an execution failure.

### V8.1 Semantic channel

Parse rate: `1.0000`; stability: `{'run_icc_min': 0.9733885068527252, 'prompt_model_cka_min': 0.9991905558296724, 'standardized_drift_max': 0.11955204372790484}`

| phase   | metric                   |   mean |   ci_lower |   n_calls |
|:--------|:-------------------------|-------:|-----------:|----------:|
| V8.1    | macro_f1                 | 0.9981 |     0.9965 |       200 |
| V8.1    | worst_event_f1           | 0.9933 |     0.9881 |       200 |
| V8.1    | span_accuracy            | 1      |     1      |       200 |
| V8.1    | polarity_mae             | 0.0879 |     0.0771 |       200 |
| V8.1    | intensity_mae            | 0.13   |     0.1232 |       200 |
| V8.1    | null_false_positive_rate | 0      |     0      |       200 |

### V8.2 Explanation fidelity

| world   |   evidence_precision_mean |   evidence_precision_ci_lower |   evidence_recall_mean |   evidence_recall_ci_lower |   necessity_advantage_mean |   necessity_advantage_ci_lower |   sufficiency_ratio_median |   mechanism_flip_detection_rate |   uncertainty_refusal_rate |
|:--------|--------------------------:|------------------------------:|-----------------------:|---------------------------:|---------------------------:|-------------------------------:|---------------------------:|--------------------------------:|---------------------------:|
| planted |                         1 |                             1 |                      1 |                          1 |                     0.3684 |                         0.365  |                     0.9962 |                               1 |                     0.02   |
| null    |                         0 |                             0 |                      0 |                          0 |                     0.0405 |                         0.0394 |                     0.6936 |                               0 |                     0.9225 |

### V8.3 Planted-world identification

| metric                |   mean |   ci_lower |   ci_upper |
|:----------------------|-------:|-----------:|-----------:|
| theta_geometry_r      | 0.9969 |     0.9969 |     0.997  |
| theta_same_author_auc | 0.9634 |     0.9628 |     0.9639 |
| state_r               | 0.9755 |     0.9754 |     0.9756 |
| choice_probability_r  | 0.8349 |     0.8335 |     0.8362 |
| choice_logloss_skill  | 0.113  |     0.1118 |     0.1142 |
| response_operator_r   | 0.9795 |     0.9793 |     0.9798 |
| response_heldout_r2   | 0.9599 |     0.9594 |     0.9604 |
| history_operator_r    | 0.9901 |     0.9901 |     0.9902 |
| history_heldout_r2    | 0.9821 |     0.982  |     0.9821 |

### V8.4 Label-free real text

| corpus   | endpoint                                    | status                        |   n_discovery |   n_calibration |   n_confirmation |   baseline_confirmation_auc |   augmented_confirmation_auc |   delta_auc |   delta_auc_ci_lower |   delta_auc_ci_upper |   selected_semantic_weight |   semantic_segment_coverage |   run_cka |
|:---------|:--------------------------------------------|:------------------------------|--------------:|----------------:|-----------------:|----------------------------:|-----------------------------:|------------:|---------------------:|---------------------:|---------------------------:|----------------------------:|----------:|
| pandora  | corpus_local_deterministic_plus_v8_semantic | TECHNICAL_INCREMENT_EVALUATED |           122 |              40 |               39 |                      0.6538 |                       0.5945 |     -0.0594 |              -0.1822 |               0.0628 |                          2 |                           1 |    0.4735 |
| pandora  | frozen_v7_geometry_plus_v8_semantic         | TECHNICAL_INCREMENT_EVALUATED |            76 |              21 |               20 |                      0.5132 |                       0.4763 |     -0.0368 |              -0.1658 |               0.0895 |                          1 |                           1 |    0.4735 |
| essays   | corpus_local_deterministic_plus_v8_semantic | TECHNICAL_INCREMENT_EVALUATED |            37 |              19 |               16 |                      0.9125 |                       0.9    |     -0.0125 |              -0.0542 |               0.0333 |                          1 |                           1 |    0.3271 |
| meps     | corpus_local_deterministic_plus_v8_semantic | TECHNICAL_INCREMENT_EVALUATED |            17 |               8 |               12 |                      0.5758 |                       0.6818 |      0.1061 |               0.0076 |               0.2273 |                          1 |                           1 |    0.5534 |
| x_market | corpus_local_deterministic_plus_v8_semantic | TECHNICAL_INCREMENT_EVALUATED |            40 |              17 |               15 |                      0.9429 |                       0.9333 |     -0.0095 |              -0.0333 |               0.0095 |                          1 |                           1 |    0.3866 |

### V8.4 Formatting perturbation

| corpus   | status                        |   format_cka |
|:---------|:------------------------------|-------------:|
| pandora  | FORMAT_PERTURBATION_EVALUATED |       0.3419 |
| essays   | FORMAT_PERTURBATION_EVALUATED |       0.9437 |
| meps     | FORMAT_PERTURBATION_EVALUATED |       0.9396 |
| x_market | FORMAT_PERTURBATION_EVALUATED |       0.9027 |

## Interpretation

- V8.1 recovered the planted event codebook accurately and safely, but its registered numeric run-drift gate failed. The LLM is therefore not licensed as a measurement channel.
- V8.2 and V8.3 establish that the evidence contract and the theta/state/choice/response/history decomposition work in planted worlds under identified designs. They do not establish human constructs.
- V8.4 found no semantic increment over the frozen PANDORA V7 geometry. MEPS showed a positive corpus-local increment, but real-text run stability failed, so this remains a follow-up signal rather than a promoted result.

## Provenance

Status: `V8_FULL_PROVENANCE_PASS`; checked files: `70`; failed files: `0`.

## Decision boundary

Technical core only. Even a full PASS would not validate personality, emotion, diagnosis, clinical utility, or cross-cultural psychological meaning.

V8.5 repeated-human measurement and external construct validation remain closed and were not simulated or inferred from these experiments.
