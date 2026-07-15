# SUICA V7.1 Operator Atlas

## Scope

This atlas uses only frozen author-feature artifacts from the fresh E1 cohort.
It fits directed Ridge maps on E1 discovery+calibration authors and evaluates
them on E1 confirmation authors. It contains no raw text, Big Five, MBTI, or
external labels.  Its evidence status is `HOLDOUT_REUSED_EXPLORATORY`: E1 already used
this confirmation cohort for its own cross-view endpoint, so this atlas is a
descriptive follow-up rather than an independent confirmation family.

It does not prove that views are coordinate charts, that maps are invertible,
or that any arrow represents a psychological hierarchy. It quantifies which
operator-conditioned feature spaces preserve information under a declared
linear transport.

- Ridge alpha inherited from E1 calibration: `10.0`

## Held-Out Directed Edges

| source_view              | target_view              |   n_authors |   direct_global_r2 |   permuted_direct_global_r2 |   r2_above_permuted |   linear_cka |   heldout_cca_mean_correlation |
|:-------------------------|:-------------------------|------------:|-------------------:|----------------------------:|--------------------:|-------------:|-------------------------------:|
| whole                    | native                   |          48 |              0.270 |                      -0.224 |               0.494 |        0.654 |                          0.885 |
| whole                    | sentence_pack_160        |          48 |              0.309 |                      -0.224 |               0.533 |        0.682 |                          0.891 |
| whole                    | fixed_128_cross          |          48 |              0.421 |                      -0.185 |               0.606 |        0.791 |                          0.956 |
| whole                    | fixed_128_within_comment |          48 |              0.316 |                      -0.208 |               0.525 |        0.692 |                          0.893 |
| native                   | whole                    |          48 |              0.698 |                      -0.269 |               0.967 |        0.654 |                          0.885 |
| native                   | sentence_pack_160        |          48 |              0.954 |                      -0.318 |               1.272 |        0.983 |                          0.992 |
| native                   | fixed_128_cross          |          48 |              0.398 |                      -0.302 |               0.700 |        0.693 |                          0.893 |
| native                   | fixed_128_within_comment |          48 |              0.939 |                      -0.467 |               1.407 |        0.976 |                          0.988 |
| sentence_pack_160        | whole                    |          48 |              0.739 |                      -0.506 |               1.245 |        0.682 |                          0.891 |
| sentence_pack_160        | native                   |          48 |              0.953 |                      -0.535 |               1.488 |        0.983 |                          0.990 |
| sentence_pack_160        | fixed_128_cross          |          48 |              0.453 |                      -0.330 |               0.783 |        0.736 |                          0.906 |
| sentence_pack_160        | fixed_128_within_comment |          48 |              0.966 |                      -0.426 |               1.392 |        0.992 |                          0.994 |
| fixed_128_cross          | whole                    |          48 |              0.851 |                      -0.452 |               1.303 |        0.791 |                          0.955 |
| fixed_128_cross          | native                   |          48 |              0.327 |                      -0.393 |               0.720 |        0.693 |                          0.894 |
| fixed_128_cross          | sentence_pack_160        |          48 |              0.399 |                      -0.402 |               0.801 |        0.736 |                          0.907 |
| fixed_128_cross          | fixed_128_within_comment |          48 |              0.411 |                      -0.385 |               0.796 |        0.750 |                          0.923 |
| fixed_128_within_comment | whole                    |          48 |              0.749 |                      -0.377 |               1.127 |        0.692 |                          0.891 |
| fixed_128_within_comment | native                   |          48 |              0.940 |                      -0.380 |               1.320 |        0.976 |                          0.988 |
| fixed_128_within_comment | sentence_pack_160        |          48 |              0.967 |                      -0.350 |               1.317 |        0.992 |                          0.994 |
| fixed_128_within_comment | fixed_128_cross          |          48 |              0.464 |                      -0.324 |               0.787 |        0.750 |                          0.926 |

## Directional Asymmetry

| view_a                   | view_b                   |   a_to_b_r2 |   b_to_a_r2 |   r2_asymmetry_a_to_b_minus_b_to_a |   mean_heldout_cca |
|:-------------------------|:-------------------------|------------:|------------:|-----------------------------------:|-------------------:|
| fixed_128_cross          | fixed_128_within_comment |       0.411 |       0.464 |                             -0.052 |              0.925 |
| fixed_128_cross          | native                   |       0.327 |       0.398 |                             -0.071 |              0.893 |
| fixed_128_cross          | sentence_pack_160        |       0.399 |       0.453 |                             -0.054 |              0.906 |
| fixed_128_cross          | whole                    |       0.851 |       0.421 |                              0.430 |              0.956 |
| fixed_128_within_comment | native                   |       0.940 |       0.939 |                              0.000 |              0.988 |
| fixed_128_within_comment | sentence_pack_160        |       0.967 |       0.966 |                              0.001 |              0.994 |
| fixed_128_within_comment | whole                    |       0.749 |       0.316 |                              0.433 |              0.892 |
| native                   | sentence_pack_160        |       0.954 |       0.953 |                              0.001 |              0.991 |
| native                   | whole                    |       0.698 |       0.270 |                              0.428 |              0.885 |
| sentence_pack_160        | whole                    |       0.739 |       0.309 |                              0.430 |              0.891 |

## Cycle Diagnostics

Cycle results are deliberately stringent: three separately fitted maps must
return to their starting standardized feature space. Low cycle performance
means the views are not interchangeable coordinate systems under this map
family; it does not mean that the source author structure is absent.

| source_view              |   mean_cycle_r2 |   mean_cycle_rmse |
|:-------------------------|----------------:|------------------:|
| fixed_128_cross          |           0.559 |             0.615 |
| fixed_128_within_comment |           0.591 |             0.557 |
| native                   |           0.570 |             0.566 |
| sentence_pack_160        |           0.590 |             0.554 |
| whole                    |           0.895 |             0.190 |

## Interpretation Boundary

An edge above its broken-correspondence null establishes only that two
operator-indexed, author-aligned text representations share recoverable
structure in this corpus. Directional differences can arise from aggregation,
lossiness, opportunity structure, or model linearity. They are not named
constructs and do not establish personality, clinical, or cross-language
validity.

## Artifacts

- Edge table: `results/v7_operator_atlas/e3_v72_full_20260715/atlas_edges.csv`
- R2 matrix: `results/v7_operator_atlas/e3_v72_full_20260715/directed_r2_matrix.csv`
- Asymmetry table: `results/v7_operator_atlas/e3_v72_full_20260715/atlas_asymmetry.csv`
- Cycle table: `results/v7_operator_atlas/e3_v72_full_20260715/cycle_errors.csv`
