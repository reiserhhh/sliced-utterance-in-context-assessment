# SUICA V6 Opportunity-Profile Source Audit

## Question

The raw V6 static residualizer already models individual-comment surface features
linearly. This frozen follow-up asks whether its residual same-author signal
survives stranger matching on progressively richer **observable opportunity
profiles**: text amount, format means, format dispersion, sampling cadence, and
finally observed-community overlap. It is a label-free source audit, not a
personality, causal, or denoising result.

## Data and boundaries

- technical raw units after the existing explicit personality-report guard: `597,933`
- confirmation authors represented in the static object: `1,640`
- external labels read: `False`
- raw text, author identifiers, embeddings, and profile rows persisted: `False`
- source path is local and is not included in this release.

Subreddit selection is not subtracted as nuisance. It appears only as a late-target
matched-control constraint, because selection is part of an author's natural text
process. The audit cannot control exact topic semantics, social role, identity,
editing behavior, or unrecorded opportunity.

## Frozen nested controls

1. `coarse`: selected comment count and selected condition count.
2. `surface_mean`: coarse controls plus the mean of ten observed format variables.
3. `surface_distribution`: mean controls plus within-view format dispersion.
4. `surface_time`: distribution controls plus span, median/max gap, and long-run support.
5. `surface_time_plus_community`: the preceding numeric profile plus soft community-set matching.
6. `surface_time_plus_community_caliper`: the same, requiring subreddit-set Jaccard
   `>= 0.10`. This is the primary row.

## Results

| object          | stage                               |   n_matched_users |   matched_auc |   matched_auc_ci_lo |   matched_auc_ci_hi |   condition_caliper_coverage |   matched_condition_jaccard |   matched_numeric_opportunity_distance |   matched_to_random_profile_distance |   matched_community_jaccard_lift |   n_profile_features |
|:----------------|:------------------------------------|------------------:|--------------:|--------------------:|--------------------:|-----------------------------:|----------------------------:|---------------------------------------:|-------------------------------------:|---------------------------------:|---------------------:|
| static_full     | coarse                              |              1640 |         0.648 |               0.638 |               0.658 |                        1.000 |                       0.026 |                                  0.108 |                                0.097 |                            0.004 |                    2 |
| static_full     | surface_mean                        |              1640 |         0.630 |               0.620 |               0.640 |                        1.000 |                       0.028 |                                  0.503 |                                0.419 |                            0.006 |                   12 |
| static_full     | surface_distribution                |              1640 |         0.630 |               0.619 |               0.641 |                        1.000 |                       0.027 |                                  0.591 |                                0.477 |                            0.005 |                   22 |
| static_full     | surface_time                        |              1640 |         0.628 |               0.618 |               0.639 |                        1.000 |                       0.027 |                                  0.657 |                                0.523 |                            0.005 |                   26 |
| static_full     | surface_time_plus_community         |              1640 |         0.623 |               0.612 |               0.634 |                        1.000 |                       0.036 |                                  0.660 |                                0.526 |                            0.014 |                   26 |
| static_full     | surface_time_plus_community_caliper |              1303 |         0.643 |               0.631 |               0.656 |                        0.795 |                       0.117 |                                  1.061 |                                0.843 |                            0.091 |                   26 |
| static_factor   | coarse                              |              1640 |         0.682 |               0.672 |               0.693 |                        1.000 |                       0.026 |                                  0.108 |                                0.097 |                            0.004 |                    2 |
| static_factor   | surface_mean                        |              1640 |         0.663 |               0.653 |               0.675 |                        1.000 |                       0.028 |                                  0.504 |                                0.421 |                            0.005 |                   12 |
| static_factor   | surface_distribution                |              1640 |         0.663 |               0.650 |               0.673 |                        1.000 |                       0.027 |                                  0.592 |                                0.479 |                            0.005 |                   22 |
| static_factor   | surface_time                        |              1640 |         0.663 |               0.653 |               0.674 |                        1.000 |                       0.027 |                                  0.656 |                                0.520 |                            0.005 |                   26 |
| static_factor   | surface_time_plus_community         |              1640 |         0.659 |               0.648 |               0.671 |                        1.000 |                       0.036 |                                  0.658 |                                0.525 |                            0.014 |                   26 |
| static_factor   | surface_time_plus_community_caliper |              1303 |         0.672 |               0.661 |               0.687 |                        0.795 |                       0.116 |                                  1.058 |                                0.844 |                            0.091 |                   26 |
| static_residual | coarse                              |              1640 |         0.597 |               0.587 |               0.606 |                        1.000 |                       0.026 |                                  0.108 |                                0.097 |                            0.004 |                    2 |
| static_residual | surface_mean                        |              1640 |         0.583 |               0.573 |               0.594 |                        1.000 |                       0.028 |                                  0.502 |                                0.417 |                            0.006 |                   12 |
| static_residual | surface_distribution                |              1640 |         0.579 |               0.570 |               0.591 |                        1.000 |                       0.027 |                                  0.592 |                                0.480 |                            0.005 |                   22 |
| static_residual | surface_time                        |              1640 |         0.580 |               0.568 |               0.589 |                        1.000 |                       0.027 |                                  0.655 |                                0.522 |                            0.005 |                   26 |
| static_residual | surface_time_plus_community         |              1640 |         0.577 |               0.567 |               0.588 |                        1.000 |                       0.036 |                                  0.660 |                                0.524 |                            0.013 |                   26 |
| static_residual | surface_time_plus_community_caliper |              1303 |         0.599 |               0.589 |               0.612 |                        0.795 |                       0.117 |                                  1.060 |                                0.843 |                            0.091 |                   26 |

## Registered decision

**SURVIVES_OBSERVED_OPPORTUNITY_PROFILE_SCREEN** — The residual is still above chance after all observed profile and community controls.

The decision applies only to `static_residual`. It is accepted only
when the strict caliper retains at least `75%`
of the eligible confirmation authors and its bootstrap lower bound exceeds `.50`.
It does not establish that the remaining signal is a trait, a psychological
construct, a causal response parameter, or an independent occasion effect.

## Post-run matching-quality QA

`matched_to_random_profile_distance` and
`matched_community_jaccard_lift` are post-run quality diagnostics added after
the primary endpoint was fixed. They do not change the decision rule. A profile
distance ratio below `1` means that the nearest-pool procedure found surface
profiles closer than random non-self late-author pairings; a positive Jaccard
lift means it also increased community overlap relative to random pairings.

## Interpretation rule

- A collapse is compatible with an **observed opportunity proxy**; it is not proof
  that one profile variable caused the earlier signal.
- Survival is an **unknown stable author configuration after this observed screen**;
  it remains confounded with unmeasured topic, role, identity, and long-term writing
  habit.
- Dynamic objects are deliberately absent: the current PANDORA corpus cannot meet
  the registered epoch-by-technical-replica design needed to attribute dynamic
  differences to an author parameter rather than persistent state.
