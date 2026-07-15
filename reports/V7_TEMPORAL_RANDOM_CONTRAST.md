# SUICA V7 Temporal vs Random-Half Contrast

## Design

The same fresh authors and the same fixed number of source comments per panel are evaluated twice: chronological earliest-versus-latest and random source halves. TF-IDF/SVD is fitted only on discovery authors. A shared scaler is fitted only on discovery/calibration panels. No external labels are read.

- Time-panel authors: `300`
- Random-panel authors: `300`
- Confirmation authors: `57`

## Results

| representation     |   n_features |   n_confirmation_authors |   n_random_partitions |   temporal_alignment_auc |   temporal_relative_distance_spearman |   temporal_linear_transport_r2 |   random_alignment_auc_mean |   random_alignment_auc_q025 |   random_alignment_auc_q975 |   random_relative_distance_spearman_mean |   random_relative_distance_spearman_q025 |   random_relative_distance_spearman_q975 |   random_linear_transport_r2_mean |   random_linear_transport_r2_q025 |   random_linear_transport_r2_q975 |   temporal_minus_random_alignment_auc_mean |   alignment_delta_ci_low |   alignment_delta_ci_high |   pooled_author_sign_flip_max_t_p |
|:-------------------|-------------:|-------------------------:|----------------------:|-------------------------:|--------------------------------------:|-------------------------------:|----------------------------:|----------------------------:|----------------------------:|-----------------------------------------:|-----------------------------------------:|-----------------------------------------:|----------------------------------:|----------------------------------:|----------------------------------:|-------------------------------------------:|-------------------------:|--------------------------:|----------------------------------:|
| WORD12_TFIDF_SVD24 |           24 |                       57 |                    25 |                   0.7556 |                                0.2149 |                        -0.0271 |                      0.8082 |                      0.7612 |                      0.8613 |                                   0.2812 |                                   0.1527 |                                   0.4030 |                            0.0450 |                            0.0115 |                            0.0811 |                                    -0.0525 |                  -0.1142 |                    0.0122 |                            0.2100 |
| CHAR35_TFIDF_SVD24 |           24 |                       57 |                    25 |                   0.7920 |                                0.1513 |                         0.0286 |                      0.8175 |                      0.7746 |                      0.8765 |                                   0.3033 |                                   0.1902 |                                   0.4139 |                            0.0684 |                            0.0253 |                            0.1054 |                                    -0.0255 |                  -0.0819 |                    0.0217 |                            0.7420 |
| WORD1_TFIDF_SVD24  |           24 |                       57 |                    25 |                   0.7619 |                                0.1086 |                        -0.0133 |                      0.8017 |                      0.7615 |                      0.8659 |                                   0.2377 |                                   0.1178 |                                   0.3673 |                            0.0359 |                           -0.0092 |                            0.0788 |                                    -0.0398 |                  -0.1089 |                    0.0277 |                            0.4160 |

## Boundary

A negative temporal-minus-random AUC means chronological separation made same-author matching harder than ordinary random sampling for this corpus and source budget. It does not prove a personality change, identify a psychological factor, or say that random halves are a clinically meaningful occasion. The paired sign-flip p-value is a descriptive family control over author-level rank contributions.

Artifacts: `results/v7_temporal_geometry/w3_temporal_random_corrected_full_20260715`
