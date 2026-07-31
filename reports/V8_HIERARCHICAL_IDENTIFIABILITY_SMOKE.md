# V8-HJIC-1 Hierarchical Identifiability Report

Status: `V8_HJIC1_SYNTHETIC_TYPED_GRAPH_PASS`

## Scope

This synthetic battery tests the typed SUICA graph without reading human text or external personality labels. Latent author-process objects, measurement estimates, uncertainty/refusal, population lifts, and external readouts remain separate object types.

Repetitions: 5.

## Component recovery

| component         |   mean_correlation |   q05_correlation |
|:------------------|-------------------:|------------------:|
| coupling          |             0.9963 |            0.9958 |
| persistence       |             0.8695 |            0.8585 |
| preference        |             0.9678 |            0.9616 |
| response_operator |             0.9993 |            0.9992 |
| stable            |             0.9997 |            0.9996 |
| state             |             0.9822 |            0.9810 |

## Commutation

| component               |   mean_defect |   q95_defect |
|:------------------------|--------------:|-------------:|
| coupling                |        0.0000 |       0.0000 |
| linear_observation_mean |        0.0000 |       0.0000 |
| persistence             |        0.0000 |       0.0000 |
| preference              |        0.0000 |       0.0000 |
| response_operator       |        0.0000 |       0.0000 |
| stable                  |        0.0000 |       0.0000 |
| state                   |        0.0000 |       0.0000 |

## Alias refusal

| world        | component                  |   refusal_rate |   false_point_rate |   mean_auc |   minimum_auc |   maximum_auc |   minimum_latent_separation |   maximum_observed_difference |
|:-------------|:---------------------------|---------------:|-------------------:|-----------:|--------------:|--------------:|----------------------------:|------------------------------:|
| KERNEL_ALIAS | full_response_operator     |         1.0000 |             0.0000 |     0.5000 |        0.5000 |        0.5000 |                      1.1825 |                        0.0000 |
| MENU_ALIAS   | preference_vs_availability |         1.0000 |             0.0000 |     0.5000 |        0.5000 |        0.5000 |                      4.0504 |                        0.0000 |
| ORDER_ALIAS  | ordered_transition         |         1.0000 |             0.0000 |     0.5000 |        0.5000 |        0.5000 |                      0.7326 |                        0.0000 |
| STATE_ALIAS  | stable_vs_state            |         1.0000 |             0.0000 |     0.5000 |        0.5000 |        0.5000 |                      1.3997 |                        0.0000 |

## Key diagnostics

- Pooled nominal-95% coverage: 0.9547.
- Naive route-heterogeneity rate: 0.8000; licensed false-ontology rate: 0.0000.
- Shared-latent relation-pattern q05: 0.8309; individual-correlation q95: 0.4420.
- Shared-latent license rate: 1.0000; common-nuisance license rate: 0.0000.
- Maximum frozen-map DPI violation: 0 bits.
- Reference-shift cosine q05: 0.9942; amplitude-error q95: 0.0539.

## Gates

- `component_recovery`: PASS
- `commutation`: PASS
- `coverage`: PASS
- `alias_refusal`: PASS
- `information_order`: PASS
- `route_nonontology`: PASS
- `shared_relational_lift`: PASS
- `confound_refusal`: PASS
- `reference_specificity`: PASS

## Ruling

Passing this battery licenses only a synthetic typed-graph implementation. It shows recovery in an identifiable design, refusal under observational equivalence, correct frozen-map information ordering, and separation of route behavior from ontology. It does not establish that any technical component is personality or that the graph transports to human language.

Claim boundary: Synthetic identifiability, commutation, information-order, refusal, route-nonontology, and population-lift evidence only. Passing does not establish that human text follows the generator, that a technical component is personality, or that SUICA is clinically valid.
