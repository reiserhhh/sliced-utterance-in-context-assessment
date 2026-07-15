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
| whole                     | whole    |                     26 |                             1.000 |                  0.659 |                                  0.391 |                              0.323 |                0.387 |                        0.000 | operator_bundles/whole_factor_bundle.json                     | not_applicable         | not_applicable    |               0 |        90 |        90 |              822.500 |                   1.000 |                           822.500 |                        16.000 |                    1.000 |                           1.000 |                       0.000 |                           0.000 |
| native                    | native   |                     26 |                             1.000 |                  0.611 |                                  0.520 |                              0.280 |                0.240 |                        0.000 | operator_bundles/native_factor_bundle.json                    | not_applicable         | not_applicable    |               0 |        90 |      1435 |               33.000 |                  16.000 |                           822.500 |                         1.000 |                    0.000 |                           1.000 |                       0.000 |                           0.000 |
| sentence_pack_160         | semantic |                     26 |                             1.000 |                  0.678 |                                  0.585 |                              0.136 |                0.294 |                        0.000 | operator_bundles/sentence_pack_160_factor_bundle.json         | not_applicable         | not_applicable    |               0 |        90 |      1564 |               35.000 |                  17.000 |                           822.500 |                         1.000 |                    0.000 |                           1.000 |                       0.000 |                           0.000 |
| fixed_128_cross           | fixed    |                     26 |                             1.000 |                  0.716 |                                  0.510 |                              0.048 |                0.559 |                        0.000 | operator_bundles/fixed_128_cross_factor_bundle.json           | cross                  | fixed             |               0 |        90 |       691 |              128.000 |                   7.000 |                           822.500 |                         3.000 |                    0.792 |                           1.000 |                       0.000 |                           0.000 |
| fixed_128_within_comment  | fixed    |                     26 |                             1.000 |                  0.677 |                                  0.482 |                              0.180 |                0.353 |                        0.000 | operator_bundles/fixed_128_within_comment_factor_bundle.json  | within                 | fixed             |               0 |        90 |      1608 |               37.000 |                  17.500 |                           822.500 |                         1.000 |                    0.000 |                           1.000 |                       0.000 |                           0.000 |
| fixed_128_boundary_marker | fixed    |                     26 |                             1.000 |                  0.611 |                                  0.546 |                              0.166 |                0.255 |                        0.000 | operator_bundles/fixed_128_boundary_marker_factor_bundle.json | cross_marker           | fixed             |               0 |        90 |       702 |              128.000 |                   7.000 |                           837.500 |                         3.000 |                    0.801 |                           1.000 |                       0.806 |                           0.000 |
| fixed_128_offset64        | fixed    |                     26 |                             1.000 |                  0.602 |                                  0.503 |                              0.171 |                0.353 |                        0.000 | operator_bundles/fixed_128_offset64_factor_bundle.json        | cross                  | fixed             |              64 |        90 |       737 |              128.000 |                   7.000 |                           822.500 |                         3.000 |                    0.805 |                           1.000 |                       0.000 |                           0.000 |
| fixed_128_hash_offset     | fixed    |                     26 |                             1.000 |                  0.594 |                                  0.564 |                              0.048 |                0.338 |                        0.000 | operator_bundles/fixed_128_hash_offset_factor_bundle.json     | cross                  | author_hash       |               0 |        90 |       726 |              128.000 |                   7.000 |                           822.500 |                         3.000 |                    0.777 |                           1.000 |                       0.000 |                           0.000 |
| fixed_64_cross            | fixed    |                     26 |                             1.000 |                  0.599 |                                  0.541 |                              0.054 |                0.441 |                        0.000 | operator_bundles/fixed_64_cross_factor_bundle.json            | cross                  | fixed             |               0 |        90 |      1338 |               64.000 |                  13.000 |                           822.500 |                         2.000 |                    0.632 |                           1.000 |                       0.000 |                           0.000 |
| fixed_256_cross           | fixed    |                     26 |                             1.000 |                  0.591 |                                  0.544 |                              0.137 |                0.343 |                        0.000 | operator_bundles/fixed_256_cross_factor_bundle.json           | cross                  | fixed             |               0 |        90 |       367 |              256.000 |                   4.000 |                           822.500 |                         4.000 |                    0.916 |                           1.000 |                       0.000 |                           0.000 |

## Precision vs Native

`delta_mean = native mean calibration-z SEM - operator mean calibration-z SEM`.
A positive value indicates lower aggregate source-sampling uncertainty, but it
does not equate factor axes across separately fitted operators.

| operator                  | comparison                       |   delta_mean |   delta_ci_low |   delta_ci_high |   n_paired_authors | interpretation                                                        |
|:--------------------------|:---------------------------------|-------------:|---------------:|----------------:|-------------------:|:----------------------------------------------------------------------|
| fixed_128_boundary_marker | native_mean_z_sem_minus_operator |        0.001 |         -0.078 |           0.081 |                 26 | positive means lower aggregate calibration-z sampling SEM than native |
| fixed_128_cross           | native_mean_z_sem_minus_operator |       -0.104 |         -0.203 |          -0.007 |                 26 | positive means lower aggregate calibration-z sampling SEM than native |
| fixed_128_hash_offset     | native_mean_z_sem_minus_operator |        0.017 |         -0.048 |           0.096 |                 26 | positive means lower aggregate calibration-z sampling SEM than native |
| fixed_128_offset64        | native_mean_z_sem_minus_operator |        0.009 |         -0.101 |           0.126 |                 26 | positive means lower aggregate calibration-z sampling SEM than native |
| fixed_128_within_comment  | native_mean_z_sem_minus_operator |       -0.066 |         -0.157 |           0.027 |                 26 | positive means lower aggregate calibration-z sampling SEM than native |
| fixed_256_cross           | native_mean_z_sem_minus_operator |        0.020 |         -0.073 |           0.123 |                 26 | positive means lower aggregate calibration-z sampling SEM than native |
| fixed_64_cross            | native_mean_z_sem_minus_operator |        0.012 |         -0.078 |           0.086 |                 26 | positive means lower aggregate calibration-z sampling SEM than native |
| sentence_pack_160         | native_mean_z_sem_minus_operator |       -0.067 |         -0.147 |          -0.005 |                 26 | positive means lower aggregate calibration-z sampling SEM than native |
| whole                     | native_mean_z_sem_minus_operator |       -0.048 |         -0.136 |           0.041 |                 26 | positive means lower aggregate calibration-z sampling SEM than native |

## Interpretation Boundary

- Source-cluster bootstrap SEM estimates finite observed-text sampling error.
- Source-disjoint correlations are technical within-corpus agreement, not
  cross-day or psychological trait reliability.
- Factor IDs are anonymous operational coordinates. Their rotations are not
  treated as aligned between operators.
- Any result here is an engineering result on a reused cohort. E1 must use a
  fresh author cohort or be labelled exploratory.

## Artifacts

- Config and cohort manifest: `results/v7_operator_boundary_audit/e0_quick_20260714/run_manifest.json`
- Boundary decision: `results/v7_operator_boundary_audit/e0_quick_20260714/boundary_audit.json`
- Normalized precision: `results/v7_operator_boundary_audit/e0_quick_20260714/normalized_precision.csv`
- Source-disjoint agreement: `results/v7_operator_boundary_audit/e0_quick_20260714/source_disjoint_consistency.csv`
- Provenance QC: `results/v7_operator_boundary_audit/e0_quick_20260714/provenance_qc.csv`
- Operator bundles: `results/v7_operator_boundary_audit/e0_quick_20260714/operator_bundles`
