# SUICA V7.1 Fresh-Cohort Multiview Projection

## Scope

This is a label-free, fresh-author follow-up to the V7.1 boundary audit. The
E0 author cohort was explicitly excluded. Big Five, MBTI, clinical labels, and
external criteria were not loaded. Different slicing rules are treated as
parallel observation views rather than competing claims about one true cut.

## Selection

- Selected shared rank: `21`
- Selected encoder Ridge alpha: `10.0`
- Selection metric: calibration-author bootstrap mean cross-view global R2,
  with the common source-comment representation fit on discovery authors only.
- Selection rule: the smallest rank within one bootstrap standard error of the
  calibration optimum.
- Rank status: `RANK_SELECTED_BY_CALIBRATION_ONE_SE`. A boundary status is a lower bound within the
  admissible grid, not evidence that the true shared dimension is exactly the
  selected rank.

|   shared_rank |   ridge_alpha |   calibration_mean_consensus_global_r2 |   calibration_consensus_global_r2_se |   one_se_threshold | within_one_se   | selected_by_one_se   |
|--------------:|--------------:|---------------------------------------:|-------------------------------------:|-------------------:|:----------------|:---------------------|
|             0 |         0.100 |                                 -0.731 |                                0.112 |             -0.108 | False           | False                |
|             0 |         1.000 |                                 -0.731 |                                0.068 |             -0.108 | False           | False                |
|             0 |        10.000 |                                 -0.731 |                                0.077 |             -0.108 | False           | False                |
|             1 |         0.100 |                                 -0.673 |                                0.095 |             -0.108 | False           | False                |
|             1 |         1.000 |                                 -0.671 |                                0.068 |             -0.108 | False           | False                |
|             1 |        10.000 |                                 -0.667 |                                0.077 |             -0.108 | False           | False                |
|             2 |         0.100 |                                 -0.639 |                                0.073 |             -0.108 | False           | False                |
|             2 |         1.000 |                                 -0.636 |                                0.087 |             -0.108 | False           | False                |
|             2 |        10.000 |                                 -0.632 |                                0.075 |             -0.108 | False           | False                |
|             3 |         0.100 |                                 -0.584 |                                0.071 |             -0.108 | False           | False                |
|             3 |         1.000 |                                 -0.579 |                                0.064 |             -0.108 | False           | False                |
|             3 |        10.000 |                                 -0.572 |                                0.087 |             -0.108 | False           | False                |
|             4 |         0.100 |                                 -0.497 |                                0.083 |             -0.108 | False           | False                |
|             4 |         1.000 |                                 -0.491 |                                0.050 |             -0.108 | False           | False                |
|             4 |        10.000 |                                 -0.480 |                                0.054 |             -0.108 | False           | False                |
|             5 |         0.100 |                                 -0.469 |                                0.062 |             -0.108 | False           | False                |
|             5 |         1.000 |                                 -0.462 |                                0.052 |             -0.108 | False           | False                |
|             5 |        10.000 |                                 -0.448 |                                0.044 |             -0.108 | False           | False                |
|             6 |         0.100 |                                 -0.454 |                                0.066 |             -0.108 | False           | False                |
|             6 |         1.000 |                                 -0.446 |                                0.053 |             -0.108 | False           | False                |
|             6 |        10.000 |                                 -0.431 |                                0.067 |             -0.108 | False           | False                |
|             7 |         0.100 |                                 -0.441 |                                0.068 |             -0.108 | False           | False                |
|             7 |         1.000 |                                 -0.430 |                                0.074 |             -0.108 | False           | False                |
|             7 |        10.000 |                                 -0.410 |                                0.080 |             -0.108 | False           | False                |
|             8 |         0.100 |                                 -0.411 |                                0.070 |             -0.108 | False           | False                |
|             8 |         1.000 |                                 -0.399 |                                0.044 |             -0.108 | False           | False                |
|             8 |        10.000 |                                 -0.377 |                                0.074 |             -0.108 | False           | False                |
|             9 |         0.100 |                                 -0.396 |                                0.053 |             -0.108 | False           | False                |
|             9 |         1.000 |                                 -0.382 |                                0.064 |             -0.108 | False           | False                |
|             9 |        10.000 |                                 -0.356 |                                0.038 |             -0.108 | False           | False                |
|            10 |         0.100 |                                 -0.376 |                                0.063 |             -0.108 | False           | False                |
|            10 |         1.000 |                                 -0.360 |                                0.087 |             -0.108 | False           | False                |
|            10 |        10.000 |                                 -0.332 |                                0.057 |             -0.108 | False           | False                |
|            11 |         0.100 |                                 -0.357 |                                0.067 |             -0.108 | False           | False                |
|            11 |         1.000 |                                 -0.339 |                                0.052 |             -0.108 | False           | False                |
|            11 |        10.000 |                                 -0.306 |                                0.087 |             -0.108 | False           | False                |
|            12 |         0.100 |                                 -0.337 |                                0.073 |             -0.108 | False           | False                |
|            12 |         1.000 |                                 -0.317 |                                0.055 |             -0.108 | False           | False                |
|            12 |        10.000 |                                 -0.283 |                                0.041 |             -0.108 | False           | False                |
|            13 |         0.100 |                                 -0.308 |                                0.070 |             -0.108 | False           | False                |
|            13 |         1.000 |                                 -0.282 |                                0.052 |             -0.108 | False           | False                |
|            13 |        10.000 |                                 -0.238 |                                0.066 |             -0.108 | False           | False                |
|            14 |         0.100 |                                 -0.303 |                                0.060 |             -0.108 | False           | False                |
|            14 |         1.000 |                                 -0.275 |                                0.046 |             -0.108 | False           | False                |
|            14 |        10.000 |                                 -0.228 |                                0.052 |             -0.108 | False           | False                |
|            15 |         0.100 |                                 -0.289 |                                0.038 |             -0.108 | False           | False                |
|            15 |         1.000 |                                 -0.259 |                                0.075 |             -0.108 | False           | False                |
|            15 |        10.000 |                                 -0.210 |                                0.049 |             -0.108 | False           | False                |
|            16 |         0.100 |                                 -0.273 |                                0.084 |             -0.108 | False           | False                |
|            16 |         1.000 |                                 -0.241 |                                0.062 |             -0.108 | False           | False                |
|            16 |        10.000 |                                 -0.186 |                                0.060 |             -0.108 | False           | False                |
|            17 |         0.100 |                                 -0.267 |                                0.048 |             -0.108 | False           | False                |
|            17 |         1.000 |                                 -0.232 |                                0.039 |             -0.108 | False           | False                |
|            17 |        10.000 |                                 -0.172 |                                0.083 |             -0.108 | False           | False                |
|            18 |         0.100 |                                 -0.264 |                                0.059 |             -0.108 | False           | False                |
|            18 |         1.000 |                                 -0.226 |                                0.087 |             -0.108 | False           | False                |
|            18 |        10.000 |                                 -0.162 |                                0.068 |             -0.108 | False           | False                |
|            19 |         0.100 |                                 -0.252 |                                0.080 |             -0.108 | False           | False                |
|            19 |         1.000 |                                 -0.211 |                                0.070 |             -0.108 | False           | False                |
|            19 |        10.000 |                                 -0.143 |                                0.065 |             -0.108 | False           | False                |
|            20 |         0.100 |                                 -0.226 |                                0.056 |             -0.108 | False           | False                |
|            20 |         1.000 |                                 -0.184 |                                0.067 |             -0.108 | False           | False                |
|            20 |        10.000 |                                 -0.112 |                                0.063 |             -0.108 | False           | False                |
|            21 |         0.100 |                                 -0.220 |                                0.065 |             -0.108 | False           | False                |
|            21 |         1.000 |                                 -0.175 |                                0.059 |             -0.108 | False           | False                |
|            21 |        10.000 |                                 -0.099 |                                0.064 |             -0.108 | True            | True                 |
|            22 |         0.100 |                                 -0.212 |                                0.054 |             -0.108 | False           | False                |
|            22 |         1.000 |                                 -0.165 |                                0.034 |             -0.108 | False           | False                |
|            22 |        10.000 |                                 -0.081 |                                0.067 |             -0.108 | True            | False                |
|            23 |         0.100 |                                 -0.213 |                                0.048 |             -0.108 | False           | False                |
|            23 |         1.000 |                                 -0.166 |                                0.039 |             -0.108 | False           | False                |
|            23 |        10.000 |                                 -0.079 |                                0.039 |             -0.108 | True            | False                |
|            24 |         0.100 |                                 -0.198 |                                0.070 |             -0.108 | False           | False                |
|            24 |         1.000 |                                 -0.146 |                                0.050 |             -0.108 | False           | False                |
|            24 |        10.000 |                                 -0.056 |                                0.051 |             -0.108 | True            | False                |

## Confirmation Cross-View Results

`consensus_global_r2` predicts target-view features through only the fitted
shared subspace. `direct_global_r2` is a flexible direct Ridge reference.
`permuted_direct_global_r2` trains on broken discovery author correspondence.
The quantities assess author-aligned text structure, not personality.

| source_view              | target_view              |   n_authors |   consensus_global_r2 |   direct_global_r2 |   permuted_direct_global_r2 |   linear_cka |   permuted_linear_cka |
|:-------------------------|:-------------------------|------------:|----------------------:|-------------------:|----------------------------:|-------------:|----------------------:|
| whole                    | native                   |          26 |                -0.223 |             -0.132 |                      -0.575 |        0.731 |                 0.427 |
| whole                    | sentence_pack_160        |          26 |                -0.168 |             -0.077 |                      -0.667 |        0.757 |                 0.462 |
| whole                    | fixed_128_cross          |          26 |                 0.138 |              0.206 |                      -0.483 |        0.814 |                 0.470 |
| whole                    | fixed_128_within_comment |          26 |                -0.150 |             -0.063 |                      -0.610 |        0.760 |                 0.460 |
| native                   | whole                    |          26 |                 0.444 |              0.533 |                      -0.717 |        0.731 |                 0.436 |
| native                   | sentence_pack_160        |          26 |                 0.472 |              0.890 |                      -0.879 |        0.982 |                 0.494 |
| native                   | fixed_128_cross          |          26 |                 0.151 |              0.131 |                      -0.522 |        0.798 |                 0.501 |
| native                   | fixed_128_within_comment |          26 |                 0.467 |              0.873 |                      -0.960 |        0.978 |                 0.602 |
| sentence_pack_160        | whole                    |          26 |                 0.497 |              0.619 |                      -0.567 |        0.757 |                 0.466 |
| sentence_pack_160        | native                   |          26 |                 0.478 |              0.888 |                      -1.111 |        0.982 |                 0.486 |
| sentence_pack_160        | fixed_128_cross          |          26 |                 0.200 |              0.224 |                      -0.790 |        0.822 |                 0.608 |
| sentence_pack_160        | fixed_128_within_comment |          26 |                 0.489 |              0.906 |                      -1.363 |        0.989 |                 0.498 |
| fixed_128_cross          | whole                    |          26 |                 0.588 |              0.778 |                      -0.592 |        0.814 |                 0.498 |
| fixed_128_cross          | native                   |          26 |                 0.091 |              0.115 |                      -0.985 |        0.798 |                 0.548 |
| fixed_128_cross          | sentence_pack_160        |          26 |                 0.136 |              0.179 |                      -0.944 |        0.822 |                 0.542 |
| fixed_128_cross          | fixed_128_within_comment |          26 |                 0.153 |              0.202 |                      -1.079 |        0.823 |                 0.503 |
| fixed_128_within_comment | whole                    |          26 |                 0.507 |              0.644 |                      -0.654 |        0.760 |                 0.432 |
| fixed_128_within_comment | native                   |          26 |                 0.475 |              0.869 |                      -1.227 |        0.978 |                 0.508 |
| fixed_128_within_comment | sentence_pack_160        |          26 |                 0.490 |              0.905 |                      -0.873 |        0.989 |                 0.497 |
| fixed_128_within_comment | fixed_128_cross          |          26 |                 0.208 |              0.237 |                      -0.774 |        0.823 |                 0.566 |

## Training Shared/Private Decomposition

Shared variance is an in-sample structural fraction after fitting the frozen
rank. Private effective rank is calculated on the remaining operator residual.
They describe operator-indexed text geometry and require confirmation
cross-view prediction above for any generalization interpretation.

| operator                 |   shared_variance_ratio_training |   private_effective_rank_training |   selected_shared_rank |
|:-------------------------|---------------------------------:|----------------------------------:|-----------------------:|
| whole                    |                            0.837 |                            16.564 |                     21 |
| native                   |                            0.773 |                            25.978 |                     21 |
| sentence_pack_160        |                            0.787 |                            24.513 |                     21 |
| fixed_128_cross          |                            0.664 |                            27.748 |                     21 |
| fixed_128_within_comment |                            0.788 |                            24.642 |                     21 |

## Bootstrap Loading-Subspace Audit

Loading subspaces are compared in feature space under discovery-author
bootstrap resampling. `subspace_congruence_lower` must exceed the random
subspace null upper bound before a shared *subspace* is called recurrent.
Axis matching is deliberately stricter and remains anonymous; an axis that
does not survive the alignment margin is recorded as
`FACTOR_AXES_NOT_IDENTIFIED_SUBSPACE_ONLY`, not renamed or discarded.

| operator                 |   subspace_congruence_lower |   subspace_congruence_median |   random_subspace_null_upper |   axis_mean_cosine_lower |   axis_min_assignment_margin_median | subspace_status   | axis_status                              |
|:-------------------------|----------------------------:|-----------------------------:|-----------------------------:|-------------------------:|------------------------------------:|:------------------|:-----------------------------------------|
| fixed_128_cross          |                       0.764 |                        0.799 |                        0.461 |                    0.447 |                              -0.182 | SUBSPACE_RECURS   | FACTOR_AXES_NOT_IDENTIFIED_SUBSPACE_ONLY |
| fixed_128_within_comment |                       0.787 |                        0.818 |                        0.450 |                    0.457 |                              -0.186 | SUBSPACE_RECURS   | FACTOR_AXES_NOT_IDENTIFIED_SUBSPACE_ONLY |
| native                   |                       0.786 |                        0.819 |                        0.456 |                    0.456 |                              -0.207 | SUBSPACE_RECURS   | FACTOR_AXES_NOT_IDENTIFIED_SUBSPACE_ONLY |
| sentence_pack_160        |                       0.790 |                        0.821 |                        0.467 |                    0.459 |                              -0.201 | SUBSPACE_RECURS   | FACTOR_AXES_NOT_IDENTIFIED_SUBSPACE_ONLY |
| whole                    |                       0.896 |                        0.916 |                        0.454 |                    0.498 |                              -0.161 | SUBSPACE_RECURS   | FACTOR_AXES_NOT_IDENTIFIED_SUBSPACE_ONLY |

## Source-Disjoint Technical Control

The matched cosine compares raw source-comment halves before slicing. It is a
technical positive control, not a trait-reliability estimate.

| operator                 |   n_authors |   matched_mean_cosine |   permuted_mean_cosine |   source_overlap_count |
|:-------------------------|------------:|----------------------:|-----------------------:|-----------------------:|
| whole                    |          26 |                 0.209 |                  0.172 |                      0 |
| native                   |          26 |                 0.486 |                  0.403 |                      0 |
| sentence_pack_160        |          26 |                 0.469 |                  0.370 |                      0 |
| fixed_128_cross          |          26 |                 0.250 |                  0.249 |                      0 |
| fixed_128_within_comment |          26 |                 0.458 |                  0.366 |                      0 |

## Claim Boundary

The experiment may identify shared and operator-private **anonymous
author-relative text structure**. It does not identify psychological factors,
show a human trait, establish cross-language transport, or justify a clinical
score. The next step is operator-atlas mapping only if the confirmation and
permutation results show a nontrivial shared component.

## Artifacts

- Manifest: `results/v7_multiview_projection/e1_v72_quick_20260715_r2/run_manifest.json`
- Rank selection: `results/v7_multiview_projection/e1_v72_quick_20260715_r2/rank_selection.csv`
- Confirmation cross-view results: `results/v7_multiview_projection/e1_v72_quick_20260715_r2/cross_view_confirmation.csv`
- Shared/private summary: `results/v7_multiview_projection/e1_v72_quick_20260715_r2/shared_private_training_summary.csv`
- Source-disjoint control: `results/v7_multiview_projection/e1_v72_quick_20260715_r2/source_disjoint_feature_control.csv`
- Bootstrap alignment detail: `results/v7_multiview_projection/e1_v72_quick_20260715_r2/bootstrap_alignment.csv`
- Bootstrap alignment summary: `results/v7_multiview_projection/e1_v72_quick_20260715_r2/bootstrap_alignment_summary.csv`
- Frozen runtime: `results/v7_multiview_projection/e1_v72_quick_20260715_r2/artifacts/multiview_runtime.joblib`
- Replay fixture: `results/v7_multiview_projection/e1_v72_quick_20260715_r2/replay_fixture.json`
- Replay expected values: `results/v7_multiview_projection/e1_v72_quick_20260715_r2/replay_expected.npz`
- Artifact hash inventory: `results/v7_multiview_projection/e1_v72_quick_20260715_r2/artifact_inventory.json`
