# SUICA V7 Representation Transport Calibration

## Scope

This synthetic matrix distinguishes reuse of a frozen geometry procedure from identification of a source-to-target coordinate map. It contains no language, market, personality or clinical labels.

## Results

| world                                    | metric                                 |   n |    mean |    q025 |    q975 |
|:-----------------------------------------|:---------------------------------------|----:|--------:|--------:|--------:|
| common_coordinate                        | paired_relative_distance_spearman      |  16 |  0.9916 |  0.9896 |  0.9936 |
| common_coordinate                        | naive_coordinate_r2                    |  16 |  0.9926 |  0.9914 |  0.9937 |
| common_coordinate                        | naive_retrieval_accuracy               |  16 |  1.0000 |  1.0000 |  1.0000 |
| common_coordinate                        | procrustes_coordinate_r2               |  16 |  0.9920 |  0.9910 |  0.9931 |
| common_coordinate                        | procrustes_retrieval_accuracy          |  16 |  1.0000 |  1.0000 |  1.0000 |
| common_coordinate                        | affine_coordinate_r2                   |  16 |  0.9913 |  0.9896 |  0.9925 |
| common_coordinate                        | affine_retrieval_accuracy              |  16 |  1.0000 |  1.0000 |  1.0000 |
| common_coordinate                        | separate_whitened_distance_spearman    |  16 |  0.9903 |  0.9879 |  0.9928 |
| common_coordinate                        | source_target_covariance_frobenius_gap |  16 |  0.0984 |  0.0815 |  0.1158 |
| unknown_affine                           | paired_relative_distance_spearman      |  16 |  0.8214 |  0.7680 |  0.8507 |
| unknown_affine                           | naive_coordinate_r2                    |  16 | -1.8201 | -2.5822 | -1.2161 |
| unknown_affine                           | naive_retrieval_accuracy               |  16 |  0.0312 |  0.0000 |  0.0938 |
| unknown_affine                           | procrustes_coordinate_r2               |  16 |  0.6573 |  0.6133 |  0.6957 |
| unknown_affine                           | procrustes_retrieval_accuracy          |  16 |  0.9740 |  0.9500 |  1.0000 |
| unknown_affine                           | affine_coordinate_r2                   |  16 |  0.9903 |  0.9875 |  0.9917 |
| unknown_affine                           | affine_retrieval_accuracy              |  16 |  1.0000 |  1.0000 |  1.0000 |
| unknown_affine                           | separate_whitened_distance_spearman    |  16 |  0.9896 |  0.9866 |  0.9920 |
| unknown_affine                           | source_target_covariance_frobenius_gap |  16 |  4.5547 |  3.6551 |  5.0956 |
| unknown_rotation                         | paired_relative_distance_spearman      |  16 |  0.9910 |  0.9890 |  0.9925 |
| unknown_rotation                         | naive_coordinate_r2                    |  16 | -1.3840 | -1.6657 | -0.9509 |
| unknown_rotation                         | naive_retrieval_accuracy               |  16 |  0.0031 |  0.0000 |  0.0271 |
| unknown_rotation                         | procrustes_coordinate_r2               |  16 |  0.9919 |  0.9911 |  0.9928 |
| unknown_rotation                         | procrustes_retrieval_accuracy          |  16 |  1.0000 |  1.0000 |  1.0000 |
| unknown_rotation                         | affine_coordinate_r2                   |  16 |  0.9912 |  0.9902 |  0.9923 |
| unknown_rotation                         | affine_retrieval_accuracy              |  16 |  1.0000 |  1.0000 |  1.0000 |
| unknown_rotation                         | separate_whitened_distance_spearman    |  16 |  0.9897 |  0.9875 |  0.9917 |
| unknown_rotation                         | source_target_covariance_frobenius_gap |  16 |  1.0564 |  0.8249 |  1.1884 |
| unpaired_isotropic_orientation_ambiguity | source_target_covariance_frobenius_gap |  16 |  1.0476 |  0.6937 |  1.2818 |

## Gates

Status: REPRESENTATION_TRANSPORT_CALIBRATION_PASS

- common_coordinate_naive_retrieval: True
- rotation_requires_paired_alignment: True
- affine_requires_paired_alignment: True
- unpaired_orientation_refusal_declared: True

## Interpretation

Pairwise within-domain geometry can survive an unknown rotation while naive source-coordinate retrieval fails. Paired anchors recover an orthogonal or affine map only in the world where those anchors are supplied. An unpaired isotropic target can have the same distribution under multiple rotations, so no numerical source-coordinate comparison is identified from unpaired target text alone. This fixes the later market/language boundary: reuse the V7 procedure with a target-local reference, or collect a declared bridge and test it on held-out anchors.

Artifacts: results/v7_representation_transport/w7_quick_20260715
