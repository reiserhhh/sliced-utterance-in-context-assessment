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
| whole                    | native                   |          26 |             -0.132 |                      -0.589 |               0.457 |        0.731 |                          0.740 |
| whole                    | sentence_pack_160        |          26 |             -0.077 |                      -0.619 |               0.541 |        0.757 |                          0.825 |
| whole                    | fixed_128_cross          |          26 |              0.206 |                      -0.329 |               0.535 |        0.814 |                          0.916 |
| whole                    | fixed_128_within_comment |          26 |             -0.063 |                      -0.672 |               0.610 |        0.760 |                          0.836 |
| native                   | whole                    |          26 |              0.533 |                      -0.809 |               1.342 |        0.731 |                          0.742 |
| native                   | sentence_pack_160        |          26 |              0.890 |                      -0.881 |               1.771 |        0.982 |                          0.967 |
| native                   | fixed_128_cross          |          26 |              0.131 |                      -0.736 |               0.868 |        0.798 |                          0.603 |
| native                   | fixed_128_within_comment |          26 |              0.873 |                      -1.223 |               2.096 |        0.978 |                          0.969 |
| sentence_pack_160        | whole                    |          26 |              0.619 |                      -0.631 |               1.250 |        0.757 |                          0.830 |
| sentence_pack_160        | native                   |          26 |              0.888 |                      -0.796 |               1.685 |        0.982 |                          0.970 |
| sentence_pack_160        | fixed_128_cross          |          26 |              0.224 |                      -0.761 |               0.985 |        0.822 |                          0.684 |
| sentence_pack_160        | fixed_128_within_comment |          26 |              0.906 |                      -1.214 |               2.121 |        0.989 |                          0.989 |
| fixed_128_cross          | whole                    |          26 |              0.778 |                      -0.734 |               1.512 |        0.814 |                          0.918 |
| fixed_128_cross          | native                   |          26 |              0.115 |                      -1.040 |               1.155 |        0.798 |                          0.671 |
| fixed_128_cross          | sentence_pack_160        |          26 |              0.179 |                      -0.973 |               1.153 |        0.822 |                          0.692 |
| fixed_128_cross          | fixed_128_within_comment |          26 |              0.202 |                      -1.039 |               1.242 |        0.823 |                          0.697 |
| fixed_128_within_comment | whole                    |          26 |              0.644 |                      -0.578 |               1.222 |        0.760 |                          0.835 |
| fixed_128_within_comment | native                   |          26 |              0.869 |                      -1.148 |               2.018 |        0.978 |                          0.974 |
| fixed_128_within_comment | sentence_pack_160        |          26 |              0.905 |                      -0.809 |               1.715 |        0.989 |                          0.988 |
| fixed_128_within_comment | fixed_128_cross          |          26 |              0.237 |                      -0.696 |               0.933 |        0.823 |                          0.729 |

## Directional Asymmetry

| view_a                   | view_b                   |   a_to_b_r2 |   b_to_a_r2 |   r2_asymmetry_a_to_b_minus_b_to_a |   mean_heldout_cca |
|:-------------------------|:-------------------------|------------:|------------:|-----------------------------------:|-------------------:|
| fixed_128_cross          | fixed_128_within_comment |       0.202 |       0.237 |                             -0.035 |              0.713 |
| fixed_128_cross          | native                   |       0.115 |       0.131 |                             -0.017 |              0.637 |
| fixed_128_cross          | sentence_pack_160        |       0.179 |       0.224 |                             -0.045 |              0.688 |
| fixed_128_cross          | whole                    |       0.778 |       0.206 |                              0.572 |              0.917 |
| fixed_128_within_comment | native                   |       0.869 |       0.873 |                             -0.004 |              0.972 |
| fixed_128_within_comment | sentence_pack_160        |       0.905 |       0.906 |                             -0.001 |              0.989 |
| fixed_128_within_comment | whole                    |       0.644 |      -0.063 |                              0.707 |              0.836 |
| native                   | sentence_pack_160        |       0.890 |       0.888 |                              0.002 |              0.969 |
| native                   | whole                    |       0.533 |      -0.132 |                              0.665 |              0.741 |
| sentence_pack_160        | whole                    |       0.619 |      -0.077 |                              0.696 |              0.827 |

## Cycle Diagnostics

Cycle results are deliberately stringent: three separately fitted maps must
return to their starting standardized feature space. Low cycle performance
means the views are not interchangeable coordinate systems under this map
family; it does not mean that the source author structure is absent.

| source_view              |   mean_cycle_r2 |   mean_cycle_rmse |
|:-------------------------|----------------:|------------------:|
| fixed_128_cross          |           0.419 |             0.595 |
| fixed_128_within_comment |           0.343 |             0.626 |
| native                   |           0.303 |             0.646 |
| sentence_pack_160        |           0.327 |             0.630 |
| whole                    |           0.808 |             0.219 |

## Interpretation Boundary

An edge above its broken-correspondence null establishes only that two
operator-indexed, author-aligned text representations share recoverable
structure in this corpus. Directional differences can arise from aggregation,
lossiness, opportunity structure, or model linearity. They are not named
constructs and do not establish personality, clinical, or cross-language
validity.

## Artifacts

- Edge table: `results/v7_operator_atlas/e3_v72_quick_20260715_r2/atlas_edges.csv`
- R2 matrix: `results/v7_operator_atlas/e3_v72_quick_20260715_r2/directed_r2_matrix.csv`
- Asymmetry table: `results/v7_operator_atlas/e3_v72_quick_20260715_r2/atlas_asymmetry.csv`
- Cycle table: `results/v7_operator_atlas/e3_v72_quick_20260715_r2/cycle_errors.csv`
