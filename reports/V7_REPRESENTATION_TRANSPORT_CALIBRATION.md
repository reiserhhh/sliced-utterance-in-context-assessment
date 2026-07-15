# SUICA V7 Representation Transport Calibration

## Scope

This synthetic matrix distinguishes reuse of a frozen geometry procedure from identification of a source-to-target coordinate map. It contains no language, market, personality or clinical labels.

## Results

| world                                    | metric                                 |   n |    mean |    q025 |    q975 |
|:-----------------------------------------|:---------------------------------------|----:|--------:|--------:|--------:|
| common_coordinate                        | paired_relative_distance_spearman      | 120 |  0.9919 |  0.9903 |  0.9933 |
| common_coordinate                        | naive_coordinate_r2                    | 120 |  0.9927 |  0.9920 |  0.9934 |
| common_coordinate                        | naive_retrieval_accuracy               | 120 |  1.0000 |  1.0000 |  1.0000 |
| common_coordinate                        | procrustes_coordinate_r2               | 120 |  0.9923 |  0.9916 |  0.9931 |
| common_coordinate                        | procrustes_retrieval_accuracy          | 120 |  1.0000 |  1.0000 |  1.0000 |
| common_coordinate                        | affine_coordinate_r2                   | 120 |  0.9918 |  0.9910 |  0.9926 |
| common_coordinate                        | affine_retrieval_accuracy              | 120 |  1.0000 |  1.0000 |  1.0000 |
| common_coordinate                        | separate_whitened_distance_spearman    | 120 |  0.9910 |  0.9890 |  0.9928 |
| common_coordinate                        | source_target_covariance_frobenius_gap | 120 |  0.0951 |  0.0790 |  0.1140 |
| unknown_affine                           | paired_relative_distance_spearman      | 120 |  0.8195 |  0.7812 |  0.8521 |
| unknown_affine                           | naive_coordinate_r2                    | 120 | -1.8783 | -2.3012 | -1.3959 |
| unknown_affine                           | naive_retrieval_accuracy               | 120 |  0.0152 |  0.0000 |  0.0502 |
| unknown_affine                           | procrustes_coordinate_r2               | 120 |  0.6919 |  0.6649 |  0.7201 |
| unknown_affine                           | procrustes_retrieval_accuracy          | 120 |  0.9991 |  0.9917 |  1.0000 |
| unknown_affine                           | affine_coordinate_r2                   | 120 |  0.9908 |  0.9898 |  0.9918 |
| unknown_affine                           | affine_retrieval_accuracy              | 120 |  1.0000 |  1.0000 |  1.0000 |
| unknown_affine                           | separate_whitened_distance_spearman    | 120 |  0.9899 |  0.9873 |  0.9917 |
| unknown_affine                           | source_target_covariance_frobenius_gap | 120 |  5.1286 |  4.5980 |  5.7541 |
| unknown_rotation                         | paired_relative_distance_spearman      | 120 |  0.9920 |  0.9903 |  0.9932 |
| unknown_rotation                         | naive_coordinate_r2                    | 120 | -1.3590 | -1.6020 | -1.0732 |
| unknown_rotation                         | naive_retrieval_accuracy               | 120 |  0.0018 |  0.0000 |  0.0085 |
| unknown_rotation                         | procrustes_coordinate_r2               | 120 |  0.9923 |  0.9916 |  0.9931 |
| unknown_rotation                         | procrustes_retrieval_accuracy          | 120 |  1.0000 |  1.0000 |  1.0000 |
| unknown_rotation                         | affine_coordinate_r2                   | 120 |  0.9918 |  0.9911 |  0.9927 |
| unknown_rotation                         | affine_retrieval_accuracy              | 120 |  1.0000 |  1.0000 |  1.0000 |
| unknown_rotation                         | separate_whitened_distance_spearman    | 120 |  0.9910 |  0.9886 |  0.9928 |
| unknown_rotation                         | source_target_covariance_frobenius_gap | 120 |  1.1215 |  0.8499 |  1.3641 |
| unpaired_isotropic_orientation_ambiguity | source_target_covariance_frobenius_gap | 120 |  1.1220 |  0.8814 |  1.4171 |

## Gates

Status: REPRESENTATION_TRANSPORT_CALIBRATION_PASS

- common_coordinate_naive_retrieval: True
- rotation_requires_paired_alignment: True
- affine_requires_paired_alignment: True
- unpaired_orientation_refusal_declared: True

## Interpretation

Pairwise within-domain geometry can survive an unknown rotation while naive source-coordinate retrieval fails. Paired anchors recover an orthogonal or affine map only in the world where those anchors are supplied. An unpaired isotropic target can have the same distribution under multiple rotations, so no numerical source-coordinate comparison is identified from unpaired target text alone. This fixes the later market/language boundary: reuse the V7 procedure with a target-local reference, or collect a declared bridge and test it on held-out anchors.

Artifacts: results/v7_representation_transport/w7_full_20260715
