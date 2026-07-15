# SUICA V7.1 Operator Boundary Audit

## Scope

This is a label-free engineering audit on the reused V7 reference cohort. It
does not read Big Five, MBTI, clinical labels, or other external criteria. It
does not identify a personality factor. It asks only whether fixed slicing has
a technically robust source-text sampling precision advantage after provenance
corrections.

All operators used the same capped source-comment panel and source-token budget
with one discovery-fitted TF-IDF/SVD representation. Factor bundles were fit
without confirmation authors and were scored with frozen calibration norms.

## Verdict

- Result: **FIXED_ADVANTAGE_NOT_ROBUST**
- Reason: The observed fixed-window precision pattern did not survive every required boundary control.

### Required Controls

- `fixed_128_within_comment`: `does_not_support_precision`
- `fixed_128_boundary_marker`: `does_not_support_precision`
- `fixed_128_offset64`: `does_not_support_precision`
- `fixed_128_hash_offset`: `does_not_support_precision`

## Operator Summary

| operator                  | kind     |   confirmation_authors |   confirmation_scoreable_coverage |   mean_bootstrap_z_sem |   mean_error_to_between_variance_ratio |   mean_source_disjoint_correlation |   mean_permutation_p |   frozen_replay_max_abs_diff | bundle_path                                                   | source_boundary_mode   | offset_strategy   |   offset_tokens |   n_users |   n_units |   median_unit_tokens |   median_units_per_user |   median_operator_tokens_per_user |   median_source_rows_per_unit |   boundary_crossing_rate |   median_unique_source_coverage |   boundary_marker_unit_rate |   frozen_replay_max_abs_diff_qc |
|:--------------------------|:---------|-----------------------:|----------------------------------:|-----------------------:|---------------------------------------:|-----------------------------------:|---------------------:|-----------------------------:|:--------------------------------------------------------------|:-----------------------|:------------------|----------------:|----------:|----------:|---------------------:|------------------------:|----------------------------------:|------------------------------:|-------------------------:|--------------------------------:|----------------------------:|--------------------------------:|
| whole                     | whole    |                     50 |                             1.000 |                  0.538 |                                  0.288 |                              0.449 |                0.034 |                        0.000 | operator_bundles/whole_factor_bundle.json                     | not_applicable         | not_applicable    |               0 |       180 |       180 |             1645.000 |                   1.000 |                          1645.000 |                        32.000 |                    1.000 |                           1.000 |                       0.000 |                           0.000 |
| native                    | native   |                     50 |                             1.000 |                  0.559 |                                  0.379 |                              0.402 |                0.018 |                        0.000 | operator_bundles/native_factor_bundle.json                    | not_applicable         | not_applicable    |               0 |       180 |      5712 |               34.000 |                  32.000 |                          1645.000 |                         1.000 |                    0.000 |                           1.000 |                       0.000 |                           0.000 |
| sentence_pack_160         | semantic |                     50 |                             1.000 |                  0.592 |                                  0.377 |                              0.351 |                0.014 |                        0.000 | operator_bundles/sentence_pack_160_factor_bundle.json         | not_applicable         | not_applicable    |               0 |       180 |      6174 |               36.000 |                  33.000 |                          1645.000 |                         1.000 |                    0.000 |                           1.000 |                       0.000 |                           0.000 |
| fixed_128_cross           | fixed    |                     50 |                             1.000 |                  0.580 |                                  0.301 |                              0.424 |                0.007 |                        0.000 | operator_bundles/fixed_128_cross_factor_bundle.json           | cross                  | fixed             |               0 |       180 |      2629 |              128.000 |                  13.000 |                          1645.000 |                         3.000 |                    0.842 |                           1.000 |                       0.000 |                           0.000 |
| fixed_128_within_comment  | fixed    |                     50 |                             1.000 |                  0.562 |                                  0.344 |                              0.362 |                0.024 |                        0.000 | operator_bundles/fixed_128_within_comment_factor_bundle.json  | within                 | fixed             |               0 |       180 |      6382 |               36.000 |                  34.000 |                          1644.000 |                         1.000 |                    0.000 |                           1.000 |                       0.000 |                           0.000 |
| fixed_128_boundary_marker | fixed    |                     50 |                             1.000 |                  0.592 |                                  0.374 |                              0.359 |                0.006 |                        0.000 | operator_bundles/fixed_128_boundary_marker_factor_bundle.json | cross_marker           | fixed             |               0 |       180 |      2681 |              128.000 |                  13.500 |                          1674.500 |                         3.000 |                    0.832 |                           1.000 |                       0.836 |                           0.000 |
| fixed_128_offset64        | fixed    |                     50 |                             1.000 |                  0.556 |                                  0.391 |                              0.381 |                0.102 |                        0.000 | operator_bundles/fixed_128_offset64_factor_bundle.json        | cross                  | fixed             |              64 |       180 |      2726 |              128.000 |                  14.000 |                          1645.000 |                         3.000 |                    0.828 |                           1.000 |                       0.000 |                           0.000 |
| fixed_128_hash_offset     | fixed    |                     50 |                             1.000 |                  0.618 |                                  0.363 |                              0.423 |                0.006 |                        0.000 | operator_bundles/fixed_128_hash_offset_factor_bundle.json     | cross                  | author_hash       |               0 |       180 |      2714 |              128.000 |                  14.000 |                          1645.000 |                         3.000 |                    0.824 |                           1.000 |                       0.000 |                           0.000 |
| fixed_64_cross            | fixed    |                     50 |                             1.000 |                  0.529 |                                  0.331 |                              0.428 |                0.154 |                        0.000 | operator_bundles/fixed_64_cross_factor_bundle.json            | cross                  | fixed             |               0 |       180 |      5175 |               64.000 |                  26.000 |                          1645.000 |                         2.000 |                    0.653 |                           1.000 |                       0.000 |                           0.000 |
| fixed_256_cross           | fixed    |                     50 |                             1.000 |                  0.650 |                                  0.333 |                              0.332 |                0.250 |                        0.000 | operator_bundles/fixed_256_cross_factor_bundle.json           | cross                  | fixed             |               0 |       180 |      1363 |              256.000 |                   7.000 |                          1645.000 |                         5.000 |                    0.952 |                           1.000 |                       0.000 |                           0.000 |

## Precision vs Native

`delta_mean = native mean calibration-z SEM - operator mean calibration-z SEM`.
A positive value indicates lower aggregate source-sampling uncertainty, but it
does not equate factor axes across separately fitted operators.

| operator                  | comparison                       |   delta_mean |   delta_ci_low |   delta_ci_high |   n_paired_authors | interpretation                                                        |
|:--------------------------|:---------------------------------|-------------:|---------------:|----------------:|-------------------:|:----------------------------------------------------------------------|
| fixed_128_boundary_marker | native_mean_z_sem_minus_operator |       -0.033 |         -0.077 |           0.017 |                 50 | positive means lower aggregate calibration-z sampling SEM than native |
| fixed_128_cross           | native_mean_z_sem_minus_operator |       -0.021 |         -0.064 |           0.034 |                 50 | positive means lower aggregate calibration-z sampling SEM than native |
| fixed_128_hash_offset     | native_mean_z_sem_minus_operator |       -0.060 |         -0.115 |          -0.010 |                 50 | positive means lower aggregate calibration-z sampling SEM than native |
| fixed_128_offset64        | native_mean_z_sem_minus_operator |        0.002 |         -0.051 |           0.054 |                 50 | positive means lower aggregate calibration-z sampling SEM than native |
| fixed_128_within_comment  | native_mean_z_sem_minus_operator |       -0.004 |         -0.039 |           0.029 |                 50 | positive means lower aggregate calibration-z sampling SEM than native |
| fixed_256_cross           | native_mean_z_sem_minus_operator |       -0.091 |         -0.155 |          -0.021 |                 50 | positive means lower aggregate calibration-z sampling SEM than native |
| fixed_64_cross            | native_mean_z_sem_minus_operator |        0.030 |         -0.017 |           0.081 |                 50 | positive means lower aggregate calibration-z sampling SEM than native |
| sentence_pack_160         | native_mean_z_sem_minus_operator |       -0.033 |         -0.060 |           0.001 |                 50 | positive means lower aggregate calibration-z sampling SEM than native |
| whole                     | native_mean_z_sem_minus_operator |        0.020 |         -0.042 |           0.093 |                 50 | positive means lower aggregate calibration-z sampling SEM than native |

## Interpretation Boundary

- Source-cluster bootstrap SEM estimates finite observed-text sampling error.
- Source-disjoint correlations are technical within-corpus agreement, not
  cross-day or psychological trait reliability.
- Factor IDs are anonymous operational coordinates. Their rotations are not
  treated as aligned between operators.
- Any result here is an engineering result on a reused cohort. E1 must use a
  fresh author cohort or be labelled exploratory.

## Artifacts

- Config and cohort manifest: `results/v7_operator_boundary_audit/e0_full_20260714/run_manifest.json`
- Boundary decision: `results/v7_operator_boundary_audit/e0_full_20260714/boundary_audit.json`
- Normalized precision: `results/v7_operator_boundary_audit/e0_full_20260714/normalized_precision.csv`
- Source-disjoint agreement: `results/v7_operator_boundary_audit/e0_full_20260714/source_disjoint_consistency.csv`
- Provenance QC: `results/v7_operator_boundary_audit/e0_full_20260714/provenance_qc.csv`
- Operator bundles: `results/v7_operator_boundary_audit/e0_full_20260714/operator_bundles`
