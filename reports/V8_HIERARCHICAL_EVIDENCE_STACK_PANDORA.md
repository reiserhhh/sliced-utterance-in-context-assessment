# SUICA V8 Hierarchical Evidence Stack: PANDORA Routing

Status: `LAYER_SPECIALIZATION_PARTIAL_EXPLORATORY`

## Contract

The experiment keeps three frozen evidence objects separate: the information-rich upstream author representation, invariant canonical geometry, and observation/opportunity surface. A task head may read more than one layer, but that design matrix is ephemeral and is not exported as a universal person score.

Every outer-fold route and model parameter was selected by nested source-only official folds. Final bridge routes were selected on Big5-only or MBTI-only official folds, serialized, and hash-frozen. Bridge values were loaded only after that freeze existed.

Claim boundary: This opened-label experiment tests whether source-only nested validation selects different frozen evidence levels for different external tasks. A task route is an ephemeral read path, not a new universal SUICA score. Bridge labels never select a route or model parameter. Results do not name a construct or establish confirmatory or clinical validity.

## Direct source-task results

| Route | Big5 mean r | MBTI mean AUC | Bridge element r | Bridge permutation p |
|---|---:|---:|---:|---:|
| upstream_only | 0.062 | 0.607 | 0.524 | 0.0038 |
| canonical_only | -0.002 | 0.546 | 0.485 | 0.0098 |
| opportunity_only | 0.051 | 0.561 | 0.208 | 0.1550 |
| canonical_opportunity | 0.038 | 0.573 | 0.451 | 0.0186 |
| upstream_canonical | 0.060 | 0.607 | 0.546 | 0.0036 |
| upstream_opportunity | 0.067 | 0.609 | 0.528 | 0.0060 |
| all_declared_layers | 0.069 | 0.608 | 0.546 | 0.0036 |
| source_selected_router | 0.049 | 0.608 | 0.463 | 0.0174 |

## Source-selected routes

| Target | Task | Selected route | Layers | Source CV score |
|---|---|---|---|---:|
| EI_cont | binary | all_declared_layers | upstream48|canonical16|opportunity | 0.572 |
| JP_cont | binary | upstream_opportunity | upstream48|opportunity | 0.582 |
| SN_cont | binary | upstream_opportunity | upstream48|opportunity | 0.590 |
| TF_cont | binary | upstream_opportunity | upstream48|opportunity | 0.694 |
| Agreeableness | continuous | upstream_only | upstream48 | 0.102 |
| Conscientiousness | continuous | opportunity_only | opportunity | 0.070 |
| Extraversion | continuous | upstream_opportunity | upstream48|opportunity | 0.087 |
| Neuroticism | continuous | upstream_opportunity | upstream48|opportunity | 0.064 |
| Openness | continuous | opportunity_only | opportunity | 0.146 |

## Route stability

| Target | Distinct outer routes | Modal route | Modal share | Entropy (bits) | Full-source match |
|---|---:|---|---:|---:|---|
| EI_cont | 3 | upstream_canonical | 0.600 | 1.371 | false |
| JP_cont | 2 | upstream_opportunity | 0.600 | 0.971 | true |
| SN_cont | 2 | upstream_opportunity | 0.600 | 0.971 | true |
| TF_cont | 1 | upstream_opportunity | 1.000 | -0.000 | true |
| Agreeableness | 3 | upstream_canonical | 0.400 | 1.522 | false |
| Conscientiousness | 2 | opportunity_only | 0.800 | 0.722 | true |
| Extraversion | 2 | upstream_opportunity | 0.600 | 0.971 | true |
| Neuroticism | 4 | upstream_only | 0.400 | 1.922 | false |
| Openness | 2 | opportunity_only | 0.600 | 0.971 | true |

Route instability is measurement evidence rather than hidden by a majority vote.

## Uncertainty and decision

- big5_only_ready: router minus upstream -0.013, 95% paired-bootstrap CI [-0.040, 0.018].
- mbti_only_ready: router minus upstream 0.001, 95% paired-bootstrap CI [-0.001, 0.003].
- Bridge structure: router minus upstream -0.061, conditional author-bootstrap CI [-0.139, 0.015].
- Bridge with source-head refit: router absolute 95% CI [0.140, 0.621]; router minus upstream CI [-0.218, 0.112].
- Distinct final source-selected routes: 4.
- Decision: `LAYER_SPECIALIZATION_PARTIAL_EXPLORATORY`.

## Interpretation boundary

- Route heterogeneity supports task-specific access to frozen evidence levels; it does not prove that the levels are psychological stages.
- Concatenation occurs only inside a declared task head. No combined feature vector is promoted as the next SUICA score.
- The upstream representation and canonical geometry are deterministic relatives, so a route comparison is about useful resolution, not independent causal channels.
- PANDORA labels were already opened. This experiment is exploratory.
- The conditional bridge-author bootstrap keeps source heads fixed. The separate 200-draw source-head-refit bootstrap includes source-fit and bridge-author uncertainty, but remains conditional on the frozen routes and model parameters.

## Reproduction

```bash
python scripts/run_suica_v8_hierarchical_evidence_stack.py
```
