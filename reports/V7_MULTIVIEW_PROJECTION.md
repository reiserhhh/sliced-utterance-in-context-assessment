# SUICA V7.1 Fresh-Cohort Multiview Projection

## Scope

This is a label-free, fresh-author follow-up to the V7.1 boundary audit. The
E0 author cohort was explicitly excluded. Big Five, MBTI, clinical labels, and
external criteria were not loaded. Different slicing rules are treated as
parallel observation views rather than competing claims about one true cut.

## Selection

- Selected shared rank: `23`
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
|             0 |         0.100 |                                 -0.110 |                                0.023 |              0.499 | False           | False                |
|             0 |         1.000 |                                 -0.110 |                                0.019 |              0.499 | False           | False                |
|             0 |        10.000 |                                 -0.110 |                                0.020 |              0.499 | False           | False                |
|             1 |         0.100 |                                 -0.054 |                                0.044 |              0.499 | False           | False                |
|             1 |         1.000 |                                 -0.053 |                                0.042 |              0.499 | False           | False                |
|             1 |        10.000 |                                 -0.052 |                                0.040 |              0.499 | False           | False                |
|             2 |         0.100 |                                 -0.004 |                                0.040 |              0.499 | False           | False                |
|             2 |         1.000 |                                 -0.003 |                                0.040 |              0.499 | False           | False                |
|             2 |        10.000 |                                 -0.002 |                                0.045 |              0.499 | False           | False                |
|             3 |         0.100 |                                  0.060 |                                0.039 |              0.499 | False           | False                |
|             3 |         1.000 |                                  0.061 |                                0.040 |              0.499 | False           | False                |
|             3 |        10.000 |                                  0.063 |                                0.041 |              0.499 | False           | False                |
|             4 |         0.100 |                                  0.103 |                                0.038 |              0.499 | False           | False                |
|             4 |         1.000 |                                  0.104 |                                0.036 |              0.499 | False           | False                |
|             4 |        10.000 |                                  0.107 |                                0.039 |              0.499 | False           | False                |
|             5 |         0.100 |                                  0.132 |                                0.040 |              0.499 | False           | False                |
|             5 |         1.000 |                                  0.133 |                                0.034 |              0.499 | False           | False                |
|             5 |        10.000 |                                  0.136 |                                0.038 |              0.499 | False           | False                |
|             6 |         0.100 |                                  0.171 |                                0.035 |              0.499 | False           | False                |
|             6 |         1.000 |                                  0.172 |                                0.035 |              0.499 | False           | False                |
|             6 |        10.000 |                                  0.176 |                                0.028 |              0.499 | False           | False                |
|             7 |         0.100 |                                  0.202 |                                0.035 |              0.499 | False           | False                |
|             7 |         1.000 |                                  0.203 |                                0.036 |              0.499 | False           | False                |
|             7 |        10.000 |                                  0.207 |                                0.034 |              0.499 | False           | False                |
|             8 |         0.100 |                                  0.225 |                                0.032 |              0.499 | False           | False                |
|             8 |         1.000 |                                  0.227 |                                0.033 |              0.499 | False           | False                |
|             8 |        10.000 |                                  0.231 |                                0.032 |              0.499 | False           | False                |
|             9 |         0.100 |                                  0.270 |                                0.035 |              0.499 | False           | False                |
|             9 |         1.000 |                                  0.272 |                                0.034 |              0.499 | False           | False                |
|             9 |        10.000 |                                  0.276 |                                0.034 |              0.499 | False           | False                |
|            10 |         0.100 |                                  0.297 |                                0.036 |              0.499 | False           | False                |
|            10 |         1.000 |                                  0.299 |                                0.037 |              0.499 | False           | False                |
|            10 |        10.000 |                                  0.304 |                                0.038 |              0.499 | False           | False                |
|            11 |         0.100 |                                  0.315 |                                0.031 |              0.499 | False           | False                |
|            11 |         1.000 |                                  0.317 |                                0.030 |              0.499 | False           | False                |
|            11 |        10.000 |                                  0.323 |                                0.034 |              0.499 | False           | False                |
|            12 |         0.100 |                                  0.334 |                                0.029 |              0.499 | False           | False                |
|            12 |         1.000 |                                  0.337 |                                0.031 |              0.499 | False           | False                |
|            12 |        10.000 |                                  0.344 |                                0.030 |              0.499 | False           | False                |
|            13 |         0.100 |                                  0.349 |                                0.032 |              0.499 | False           | False                |
|            13 |         1.000 |                                  0.352 |                                0.027 |              0.499 | False           | False                |
|            13 |        10.000 |                                  0.360 |                                0.029 |              0.499 | False           | False                |
|            14 |         0.100 |                                  0.364 |                                0.025 |              0.499 | False           | False                |
|            14 |         1.000 |                                  0.367 |                                0.030 |              0.499 | False           | False                |
|            14 |        10.000 |                                  0.377 |                                0.033 |              0.499 | False           | False                |
|            15 |         0.100 |                                  0.373 |                                0.026 |              0.499 | False           | False                |
|            15 |         1.000 |                                  0.376 |                                0.029 |              0.499 | False           | False                |
|            15 |        10.000 |                                  0.386 |                                0.033 |              0.499 | False           | False                |
|            16 |         0.100 |                                  0.390 |                                0.031 |              0.499 | False           | False                |
|            16 |         1.000 |                                  0.393 |                                0.026 |              0.499 | False           | False                |
|            16 |        10.000 |                                  0.403 |                                0.029 |              0.499 | False           | False                |
|            17 |         0.100 |                                  0.405 |                                0.025 |              0.499 | False           | False                |
|            17 |         1.000 |                                  0.409 |                                0.026 |              0.499 | False           | False                |
|            17 |        10.000 |                                  0.420 |                                0.026 |              0.499 | False           | False                |
|            18 |         0.100 |                                  0.417 |                                0.025 |              0.499 | False           | False                |
|            18 |         1.000 |                                  0.421 |                                0.026 |              0.499 | False           | False                |
|            18 |        10.000 |                                  0.433 |                                0.028 |              0.499 | False           | False                |
|            19 |         0.100 |                                  0.432 |                                0.021 |              0.499 | False           | False                |
|            19 |         1.000 |                                  0.436 |                                0.025 |              0.499 | False           | False                |
|            19 |        10.000 |                                  0.449 |                                0.027 |              0.499 | False           | False                |
|            20 |         0.100 |                                  0.452 |                                0.020 |              0.499 | False           | False                |
|            20 |         1.000 |                                  0.456 |                                0.018 |              0.499 | False           | False                |
|            20 |        10.000 |                                  0.470 |                                0.022 |              0.499 | False           | False                |
|            21 |         0.100 |                                  0.468 |                                0.020 |              0.499 | False           | False                |
|            21 |         1.000 |                                  0.473 |                                0.021 |              0.499 | False           | False                |
|            21 |        10.000 |                                  0.488 |                                0.022 |              0.499 | False           | False                |
|            22 |         0.100 |                                  0.479 |                                0.019 |              0.499 | False           | False                |
|            22 |         1.000 |                                  0.484 |                                0.020 |              0.499 | False           | False                |
|            22 |        10.000 |                                  0.499 |                                0.023 |              0.499 | False           | False                |
|            23 |         0.100 |                                  0.488 |                                0.018 |              0.499 | False           | False                |
|            23 |         1.000 |                                  0.493 |                                0.020 |              0.499 | False           | False                |
|            23 |        10.000 |                                  0.509 |                                0.023 |              0.499 | True            | True                 |
|            24 |         0.100 |                                  0.499 |                                0.019 |              0.499 | True            | False                |
|            24 |         1.000 |                                  0.504 |                                0.020 |              0.499 | True            | False                |
|            24 |        10.000 |                                  0.521 |                                0.022 |              0.499 | True            | False                |

## Confirmation Cross-View Results

`consensus_global_r2` predicts target-view features through only the fitted
shared subspace. `direct_global_r2` is a flexible direct Ridge reference.
`permuted_direct_global_r2` trains on broken discovery author correspondence.
The quantities assess author-aligned text structure, not personality.

| source_view              | target_view              |   n_authors |   consensus_global_r2 |   direct_global_r2 |   permuted_direct_global_r2 |   linear_cka |   permuted_linear_cka |
|:-------------------------|:-------------------------|------------:|----------------------:|-------------------:|----------------------------:|-------------:|----------------------:|
| whole                    | native                   |          48 |                 0.221 |              0.270 |                      -0.248 |        0.654 |                 0.239 |
| whole                    | sentence_pack_160        |          48 |                 0.260 |              0.309 |                      -0.253 |        0.682 |                 0.338 |
| whole                    | fixed_128_cross          |          48 |                 0.391 |              0.421 |                      -0.174 |        0.791 |                 0.287 |
| whole                    | fixed_128_within_comment |          48 |                 0.267 |              0.316 |                      -0.233 |        0.692 |                 0.304 |
| native                   | whole                    |          48 |                 0.644 |              0.698 |                      -0.336 |        0.654 |                 0.260 |
| native                   | sentence_pack_160        |          48 |                 0.657 |              0.954 |                      -0.535 |        0.983 |                 0.308 |
| native                   | fixed_128_cross          |          48 |                 0.353 |              0.398 |                      -0.345 |        0.693 |                 0.419 |
| native                   | fixed_128_within_comment |          48 |                 0.653 |              0.939 |                      -0.458 |        0.976 |                 0.365 |
| sentence_pack_160        | whole                    |          48 |                 0.681 |              0.739 |                      -0.327 |        0.682 |                 0.266 |
| sentence_pack_160        | native                   |          48 |                 0.661 |              0.953 |                      -0.384 |        0.983 |                 0.306 |
| sentence_pack_160        | fixed_128_cross          |          48 |                 0.390 |              0.453 |                      -0.275 |        0.736 |                 0.341 |
| sentence_pack_160        | fixed_128_within_comment |          48 |                 0.667 |              0.966 |                      -0.410 |        0.992 |                 0.310 |
| fixed_128_cross          | whole                    |          48 |                 0.781 |              0.851 |                      -0.441 |        0.791 |                 0.312 |
| fixed_128_cross          | native                   |          48 |                 0.289 |              0.327 |                      -0.506 |        0.693 |                 0.339 |
| fixed_128_cross          | sentence_pack_160        |          48 |                 0.341 |              0.399 |                      -0.498 |        0.736 |                 0.347 |
| fixed_128_cross          | fixed_128_within_comment |          48 |                 0.349 |              0.411 |                      -0.365 |        0.750 |                 0.349 |
| fixed_128_within_comment | whole                    |          48 |                 0.694 |              0.749 |                      -0.350 |        0.692 |                 0.249 |
| fixed_128_within_comment | native                   |          48 |                 0.656 |              0.940 |                      -0.414 |        0.976 |                 0.302 |
| fixed_128_within_comment | sentence_pack_160        |          48 |                 0.667 |              0.967 |                      -0.402 |        0.992 |                 0.299 |
| fixed_128_within_comment | fixed_128_cross          |          48 |                 0.400 |              0.464 |                      -0.345 |        0.750 |                 0.342 |

## Training Shared/Private Decomposition

Shared variance is an in-sample structural fraction after fitting the frozen
rank. Private effective rank is calculated on the remaining operator residual.
They describe operator-indexed text geometry and require confirmation
cross-view prediction above for any generalization interpretation.

| operator                 |   shared_variance_ratio_training |   private_effective_rank_training |   selected_shared_rank |
|:-------------------------|---------------------------------:|----------------------------------:|-----------------------:|
| whole                    |                            0.863 |                            19.386 |                     23 |
| native                   |                            0.774 |                            28.166 |                     23 |
| sentence_pack_160        |                            0.789 |                            26.010 |                     23 |
| fixed_128_cross          |                            0.660 |                            29.749 |                     23 |
| fixed_128_within_comment |                            0.790 |                            25.753 |                     23 |

## Bootstrap Loading-Subspace Audit

Loading subspaces are compared in feature space under discovery-author
bootstrap resampling. `subspace_congruence_lower` must exceed the random
subspace null upper bound before a shared *subspace* is called recurrent.
Axis matching is deliberately stricter and remains anonymous; an axis that
does not survive the alignment margin is recorded as
`FACTOR_AXES_NOT_IDENTIFIED_SUBSPACE_ONLY`, not renamed or discarded.

| operator                 |   subspace_congruence_lower |   subspace_congruence_median |   random_subspace_null_upper |   axis_mean_cosine_lower |   axis_min_assignment_margin_median | subspace_status   | axis_status                              |
|:-------------------------|----------------------------:|-----------------------------:|-----------------------------:|-------------------------:|------------------------------------:|:------------------|:-----------------------------------------|
| fixed_128_cross          |                       0.790 |                        0.828 |                        0.508 |                    0.463 |                              -0.220 | SUBSPACE_RECURS   | FACTOR_AXES_NOT_IDENTIFIED_SUBSPACE_ONLY |
| fixed_128_within_comment |                       0.813 |                        0.850 |                        0.511 |                    0.484 |                              -0.217 | SUBSPACE_RECURS   | FACTOR_AXES_NOT_IDENTIFIED_SUBSPACE_ONLY |
| native                   |                       0.811 |                        0.850 |                        0.515 |                    0.483 |                              -0.213 | SUBSPACE_RECURS   | FACTOR_AXES_NOT_IDENTIFIED_SUBSPACE_ONLY |
| sentence_pack_160        |                       0.814 |                        0.851 |                        0.506 |                    0.484 |                              -0.212 | SUBSPACE_RECURS   | FACTOR_AXES_NOT_IDENTIFIED_SUBSPACE_ONLY |
| whole                    |                       0.957 |                        0.971 |                        0.503 |                    0.525 |                              -0.201 | SUBSPACE_RECURS   | FACTOR_AXES_NOT_IDENTIFIED_SUBSPACE_ONLY |

## Source-Disjoint Technical Control

The matched cosine compares raw source-comment halves before slicing. It is a
technical positive control, not a trait-reliability estimate.

| operator                 |   n_authors |   matched_mean_cosine |   permuted_mean_cosine |   source_overlap_count |
|:-------------------------|------------:|----------------------:|-----------------------:|-----------------------:|
| whole                    |          48 |                 0.333 |                  0.066 |                      0 |
| native                   |          48 |                 0.320 |                  0.173 |                      0 |
| sentence_pack_160        |          48 |                 0.309 |                  0.140 |                      0 |
| fixed_128_cross          |          48 |                 0.228 |                  0.143 |                      0 |
| fixed_128_within_comment |          48 |                 0.306 |                  0.166 |                      0 |

## Claim Boundary

The experiment may identify shared and operator-private **anonymous
author-relative text structure**. It does not identify psychological factors,
show a human trait, establish cross-language transport, or justify a clinical
score. The next step is operator-atlas mapping only if the confirmation and
permutation results show a nontrivial shared component.

## Artifacts

- Manifest: `results/v7_multiview_projection/e1_v72_full_20260715/run_manifest.json`
- Rank selection: `results/v7_multiview_projection/e1_v72_full_20260715/rank_selection.csv`
- Confirmation cross-view results: `results/v7_multiview_projection/e1_v72_full_20260715/cross_view_confirmation.csv`
- Shared/private summary: `results/v7_multiview_projection/e1_v72_full_20260715/shared_private_training_summary.csv`
- Source-disjoint control: `results/v7_multiview_projection/e1_v72_full_20260715/source_disjoint_feature_control.csv`
- Bootstrap alignment detail: `results/v7_multiview_projection/e1_v72_full_20260715/bootstrap_alignment.csv`
- Bootstrap alignment summary: `results/v7_multiview_projection/e1_v72_full_20260715/bootstrap_alignment_summary.csv`
- Frozen runtime: `results/v7_multiview_projection/e1_v72_full_20260715/artifacts/multiview_runtime.joblib`
- Replay fixture: `results/v7_multiview_projection/e1_v72_full_20260715/replay_fixture.json`
- Replay expected values: `results/v7_multiview_projection/e1_v72_full_20260715/replay_expected.npz`
- Artifact hash inventory: `results/v7_multiview_projection/e1_v72_full_20260715/artifact_inventory.json`
