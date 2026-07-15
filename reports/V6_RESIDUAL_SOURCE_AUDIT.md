# SUICA V6 Residual Source Audit

## Registered question

Can same-author signal survive stranger controls matched on measured opportunity
and community exposure? This audit uses no personality labels. It holds the raw
factor-discovery representation and author split fixed, then compares early text
objects with late stranger objects matched on available metadata and subreddit-set
overlap.

## Result table

| object           | control                      |   n_users |   auc |   auc_ci_lo |   auc_ci_hi | metadata                                                       |   matched_condition_jaccard |   matched_numeric_opportunity_distance |   candidate_pool_max |   minimum_condition_jaccard |   condition_caliper_coverage |   condition_weight |
|:-----------------|:-----------------------------|----------:|------:|------------:|------------:|:---------------------------------------------------------------|----------------------------:|---------------------------------------:|---------------------:|----------------------------:|-----------------------------:|-------------------:|
| static_full      | unmatched_deranged           |      1640 | 0.667 |       0.655 |       0.677 | meta_comments;meta_conditions;meta_opportunity_choice          |                     nan     |                                nan     |              nan     |                     nan     |                      nan     |            nan     |
| static_full      | matched_condition_weight_0   |      1640 | 0.646 |       0.637 |       0.656 | meta_comments;meta_conditions;meta_opportunity_choice          |                       0.029 |                                  0.232 |               25.000 |                     nan     |                        1.000 |              0.000 |
| static_full      | matched_condition_weight_0.5 |      1640 | 0.644 |       0.634 |       0.652 | meta_comments;meta_conditions;meta_opportunity_choice          |                       0.033 |                                  0.233 |               25.000 |                     nan     |                        1.000 |              0.500 |
| static_full      | matched_condition_weight_1   |      1640 | 0.645 |       0.636 |       0.654 | meta_comments;meta_conditions;meta_opportunity_choice          |                       0.037 |                                  0.235 |               25.000 |                     nan     |                        1.000 |              1.000 |
| static_full      | matched_condition_weight_2   |      1640 | 0.641 |       0.631 |       0.650 | meta_comments;meta_conditions;meta_opportunity_choice          |                       0.045 |                                  0.247 |               25.000 |                     nan     |                        1.000 |              2.000 |
| static_full      | condition_caliper_0.05       |      1637 | 0.635 |       0.626 |       0.645 | meta_comments;meta_conditions;meta_opportunity_choice          |                       0.072 |                                  0.501 |               25.000 |                       0.050 |                        0.998 |              1.000 |
| static_full      | condition_caliper_0.10       |      1303 | 0.643 |       0.632 |       0.655 | meta_comments;meta_conditions;meta_opportunity_choice          |                       0.117 |                                  0.757 |               25.000 |                       0.100 |                        0.795 |              1.000 |
| static_factor    | unmatched_deranged           |      1640 | 0.694 |       0.680 |       0.706 | meta_comments;meta_conditions;meta_opportunity_choice          |                     nan     |                                nan     |              nan     |                     nan     |                      nan     |            nan     |
| static_factor    | matched_condition_weight_0   |      1640 | 0.679 |       0.667 |       0.689 | meta_comments;meta_conditions;meta_opportunity_choice          |                       0.030 |                                  0.232 |               25.000 |                     nan     |                        1.000 |              0.000 |
| static_factor    | matched_condition_weight_0.5 |      1640 | 0.676 |       0.663 |       0.687 | meta_comments;meta_conditions;meta_opportunity_choice          |                       0.033 |                                  0.233 |               25.000 |                     nan     |                        1.000 |              0.500 |
| static_factor    | matched_condition_weight_1   |      1640 | 0.675 |       0.664 |       0.687 | meta_comments;meta_conditions;meta_opportunity_choice          |                       0.037 |                                  0.235 |               25.000 |                     nan     |                        1.000 |              1.000 |
| static_factor    | matched_condition_weight_2   |      1640 | 0.673 |       0.662 |       0.684 | meta_comments;meta_conditions;meta_opportunity_choice          |                       0.045 |                                  0.247 |               25.000 |                     nan     |                        1.000 |              2.000 |
| static_factor    | condition_caliper_0.05       |      1637 | 0.667 |       0.656 |       0.678 | meta_comments;meta_conditions;meta_opportunity_choice          |                       0.072 |                                  0.502 |               25.000 |                       0.050 |                        0.998 |              1.000 |
| static_factor    | condition_caliper_0.10       |      1303 | 0.673 |       0.661 |       0.687 | meta_comments;meta_conditions;meta_opportunity_choice          |                       0.117 |                                  0.758 |               25.000 |                       0.100 |                        0.795 |              1.000 |
| static_residual  | unmatched_deranged           |      1640 | 0.613 |       0.604 |       0.626 | meta_comments;meta_conditions;meta_opportunity_choice          |                     nan     |                                nan     |              nan     |                     nan     |                      nan     |            nan     |
| static_residual  | matched_condition_weight_0   |      1640 | 0.595 |       0.583 |       0.604 | meta_comments;meta_conditions;meta_opportunity_choice          |                       0.029 |                                  0.232 |               25.000 |                     nan     |                        1.000 |              0.000 |
| static_residual  | matched_condition_weight_0.5 |      1640 | 0.596 |       0.588 |       0.607 | meta_comments;meta_conditions;meta_opportunity_choice          |                       0.033 |                                  0.231 |               25.000 |                     nan     |                        1.000 |              0.500 |
| static_residual  | matched_condition_weight_1   |      1640 | 0.594 |       0.585 |       0.605 | meta_comments;meta_conditions;meta_opportunity_choice          |                       0.037 |                                  0.235 |               25.000 |                     nan     |                        1.000 |              1.000 |
| static_residual  | matched_condition_weight_2   |      1640 | 0.593 |       0.582 |       0.602 | meta_comments;meta_conditions;meta_opportunity_choice          |                       0.045 |                                  0.247 |               25.000 |                     nan     |                        1.000 |              2.000 |
| static_residual  | condition_caliper_0.05       |      1637 | 0.592 |       0.580 |       0.603 | meta_comments;meta_conditions;meta_opportunity_choice          |                       0.072 |                                  0.499 |               25.000 |                       0.050 |                        0.998 |              1.000 |
| static_residual  | condition_caliper_0.10       |      1303 | 0.600 |       0.587 |       0.611 | meta_comments;meta_conditions;meta_opportunity_choice          |                       0.116 |                                  0.756 |               25.000 |                       0.100 |                        0.795 |              1.000 |
| dynamic_full     | unmatched_deranged           |       635 | 0.529 |       0.510 |       0.547 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                     nan     |                                nan     |              nan     |                     nan     |                      nan     |            nan     |
| dynamic_full     | matched_condition_weight_0   |       635 | 0.528 |       0.507 |       0.547 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                       0.027 |                                  0.337 |               25.000 |                     nan     |                        1.000 |              0.000 |
| dynamic_full     | matched_condition_weight_0.5 |       635 | 0.529 |       0.512 |       0.549 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                       0.029 |                                  0.337 |               25.000 |                     nan     |                        1.000 |              0.500 |
| dynamic_full     | matched_condition_weight_1   |       635 | 0.530 |       0.508 |       0.549 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                       0.032 |                                  0.339 |               25.000 |                     nan     |                        1.000 |              1.000 |
| dynamic_full     | matched_condition_weight_2   |       635 | 0.531 |       0.513 |       0.548 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                       0.038 |                                  0.348 |               25.000 |                     nan     |                        1.000 |              2.000 |
| dynamic_full     | condition_caliper_0.05       |       631 | 0.532 |       0.513 |       0.551 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                       0.070 |                                  0.689 |               25.000 |                       0.050 |                        0.994 |              1.000 |
| dynamic_full     | condition_caliper_0.10       |       465 | 0.526 |       0.504 |       0.552 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                       0.116 |                                  0.976 |               25.000 |                       0.100 |                        0.732 |              1.000 |
| dynamic_factor   | unmatched_deranged           |       635 | 0.511 |       0.492 |       0.530 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                     nan     |                                nan     |              nan     |                     nan     |                      nan     |            nan     |
| dynamic_factor   | matched_condition_weight_0   |       635 | 0.512 |       0.491 |       0.531 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                       0.027 |                                  0.337 |               25.000 |                     nan     |                        1.000 |              0.000 |
| dynamic_factor   | matched_condition_weight_0.5 |       635 | 0.514 |       0.497 |       0.534 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                       0.030 |                                  0.339 |               25.000 |                     nan     |                        1.000 |              0.500 |
| dynamic_factor   | matched_condition_weight_1   |       635 | 0.510 |       0.492 |       0.530 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                       0.032 |                                  0.339 |               25.000 |                     nan     |                        1.000 |              1.000 |
| dynamic_factor   | matched_condition_weight_2   |       635 | 0.514 |       0.493 |       0.531 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                       0.038 |                                  0.347 |               25.000 |                     nan     |                        1.000 |              2.000 |
| dynamic_factor   | condition_caliper_0.05       |       631 | 0.509 |       0.490 |       0.534 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                       0.070 |                                  0.684 |               25.000 |                       0.050 |                        0.994 |              1.000 |
| dynamic_factor   | condition_caliper_0.10       |       465 | 0.507 |       0.482 |       0.532 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                       0.117 |                                  0.976 |               25.000 |                       0.100 |                        0.732 |              1.000 |
| dynamic_residual | unmatched_deranged           |       635 | 0.532 |       0.514 |       0.549 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                     nan     |                                nan     |              nan     |                     nan     |                      nan     |            nan     |
| dynamic_residual | matched_condition_weight_0   |       635 | 0.531 |       0.512 |       0.551 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                       0.027 |                                  0.336 |               25.000 |                     nan     |                        1.000 |              0.000 |
| dynamic_residual | matched_condition_weight_0.5 |       635 | 0.532 |       0.513 |       0.547 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                       0.029 |                                  0.339 |               25.000 |                     nan     |                        1.000 |              0.500 |
| dynamic_residual | matched_condition_weight_1   |       635 | 0.532 |       0.514 |       0.550 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                       0.032 |                                  0.339 |               25.000 |                     nan     |                        1.000 |              1.000 |
| dynamic_residual | matched_condition_weight_2   |       635 | 0.536 |       0.519 |       0.553 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                       0.038 |                                  0.347 |               25.000 |                     nan     |                        1.000 |              2.000 |
| dynamic_residual | condition_caliper_0.05       |       631 | 0.542 |       0.520 |       0.563 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                       0.070 |                                  0.692 |               25.000 |                       0.050 |                        0.994 |              1.000 |
| dynamic_residual | condition_caliper_0.10       |       465 | 0.539 |       0.509 |       0.566 | meta_comments;meta_conditions;dynamic_runs;dynamic_transitions |                       0.117 |                                  0.979 |               25.000 |                       0.100 |                        0.732 |              1.000 |

## Decision rule

The `condition_caliper_*` rows match the observed late target to strangers whose
late subreddit set has at least the stated Jaccard overlap. They are sensitivity
analyses, not causal adjustment: coverage and actual overlap are reported. The
weighted nearest-neighbour rows are a screening control. Neither analysis alone
licenses an author-level or personality claim, because the current corpus lacks
within-occasion technical replicates and fixed discovery-calibrated calipers.

The immediate inference is narrower: a signal that collapses under metadata
matching is compatible with an expression-opportunity proxy. A signal that
survives is an **unidentified stable author-path feature** requiring the next,
epoch-and-replicate audit; it is not personality.

### Current classifications

- Survives strongest matching: none.
- Undecided after strongest matching: dynamic_factor.
- This is not a causal adjustment: unmeasured topic semantics, social role,
  identity, and latent opportunity may still explain any surviving signal.

## Outcome and dynamic-variable interpretation

Static full, factor, and residual spaces remain above chance under every reported
screen. The dynamic **factor projection** is chance-like, but the dynamic
**residual** remains weakly above chance under the weighted screen (.536
[.519,.553]) and the near-universal Jaccard >=.05 sensitivity analysis (.542
[.520,.563], 99.4% coverage). This is evidence against the claim that the
dynamic residual is explained only by the currently measured opportunity fields.

It is not an author-level dynamic finding. A separate whole-run feasibility audit
shows that only 9 authors can supply the required epoch x technical-replica design
at the registered 2-run/12-transition resolution. The correct status is
`UNIDENTIFIABLE_WITH_CURRENT_PANDORA_CORPUS`: persistent state, stable author
path parameter, topic semantics, and systematic scorer behavior remain
observationally entangled.

Dynamic descriptors represent a candidate unknown variable only if their signal
survives matched strangers. It should then be described mechanically (stable
trajectory configuration, persistence, roughness, variance, or change-point
pattern) until a preregistered repeated-condition human study establishes its
psychological meaning. The audit cannot name it; it can rule out a class of
opportunity explanations.
