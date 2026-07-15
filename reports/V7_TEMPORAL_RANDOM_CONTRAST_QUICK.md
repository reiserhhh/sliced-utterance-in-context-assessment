# SUICA V7 Temporal vs Random-Half Contrast

## Design

The same fresh authors and the same fixed number of source comments per panel are evaluated twice: chronological earliest-versus-latest and random source halves. TF-IDF/SVD is fitted only on discovery authors. A shared scaler is fitted only on discovery/calibration panels. No external labels are read.

- Time-panel authors: `120`
- Random-panel authors: `120`
- Confirmation authors: `23`

## Results

| representation     |   n_features |   n_confirmation_authors |   temporal_alignment_auc |   temporal_relative_distance_spearman |   temporal_linear_transport_r2 |   random_alignment_auc |   random_relative_distance_spearman |   random_linear_transport_r2 |   temporal_minus_random_alignment_auc |   alignment_delta_ci_low |   alignment_delta_ci_high |   paired_sign_flip_max_t_p |
|:-------------------|-------------:|-------------------------:|-------------------------:|--------------------------------------:|-------------------------------:|-----------------------:|------------------------------------:|-----------------------------:|--------------------------------------:|-------------------------:|--------------------------:|---------------------------:|
| WORD12_TFIDF_SVD24 |           12 |                       23 |                   0.7154 |                                0.3646 |                         0.0055 |                 0.6976 |                              0.0626 |                      -0.1188 |                                0.0178 |                  -0.1426 |                    0.1505 |                     0.9900 |
| CHAR35_TFIDF_SVD24 |           12 |                       23 |                   0.7154 |                                0.2235 |                         0.0257 |                 0.7174 |                              0.0309 |                      -0.1074 |                               -0.0020 |                  -0.1584 |                    0.1424 |                     1.0000 |
| WORD1_TFIDF_SVD24  |           12 |                       23 |                   0.6957 |                                0.2279 |                        -0.0034 |                 0.7253 |                              0.0645 |                      -0.1133 |                               -0.0296 |                  -0.2177 |                    0.1049 |                     0.9550 |

## Boundary

A negative temporal-minus-random AUC means chronological separation made same-author matching harder than ordinary random sampling for this corpus and source budget. It does not prove a personality change, identify a psychological factor, or say that random halves are a clinically meaningful occasion. The paired sign-flip p-value is a descriptive family control over author-level rank contributions.

Artifacts: `results/v7_temporal_geometry/w3_temporal_random_quick_20260715`
