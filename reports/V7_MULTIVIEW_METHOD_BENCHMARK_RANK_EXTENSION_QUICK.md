# SUICA V7 Multiview Method Benchmark

## Scope

A fresh author cohort, excluding E0--E4 and W3, compares mathematical multiview methods. Rank selection uses calibration authors only; confirmation remains held out. No psychological labels are loaded.

### Method Availability

| method               | status                             | detail                                                 |
|:---------------------|:-----------------------------------|:-------------------------------------------------------|
| CONSENSUS_COVARIANCE | AVAILABLE_BUILTIN                  | Implemented and compared in this run.                  |
| CONCAT_PCA           | AVAILABLE_BUILTIN                  | Implemented and compared in this run.                  |
| RGCCA_SUMCOR         | AVAILABLE_BUILTIN                  | Implemented and compared in this run.                  |
| JIVE_AJIVE           | REFUSE_OPTIONAL_DEPENDENCY_MISSING | Not substituted by a differently named implementation. |

### Calibration Rank Selection

| method               |   rank |   calibration_mean_r2 |   calibration_author_bootstrap_se |   one_se_threshold | selected_by_one_se   | representation     |
|:---------------------|-------:|----------------------:|----------------------------------:|-------------------:|:---------------------|:-------------------|
| CONSENSUS_COVARIANCE |      1 |                -0.161 |                             0.052 |              0.392 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      2 |                -0.105 |                             0.070 |              0.392 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      3 |                -0.078 |                             0.049 |              0.392 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      4 |                -0.017 |                             0.081 |              0.392 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      6 |                 0.053 |                             0.062 |              0.392 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      8 |                 0.222 |                             0.045 |              0.392 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |     10 |                 0.276 |                             0.060 |              0.392 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |     12 |                 0.356 |                             0.039 |              0.392 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |     16 |                 0.441 |                             0.049 |              0.392 | True                 | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      1 |                -0.164 |                             0.090 |              0.365 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      2 |                -0.107 |                             0.085 |              0.365 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      3 |                -0.080 |                             0.087 |              0.365 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      4 |                -0.015 |                             0.069 |              0.365 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      6 |                 0.052 |                             0.070 |              0.365 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      8 |                 0.198 |                             0.059 |              0.365 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |     10 |                 0.271 |                             0.052 |              0.365 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |     12 |                 0.324 |                             0.053 |              0.365 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |     16 |                 0.413 |                             0.048 |              0.365 | True                 | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      1 |                -0.159 |                             0.087 |              0.321 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      2 |                -0.129 |                             0.085 |              0.321 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      3 |                -0.117 |                             0.079 |              0.321 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      4 |                -0.076 |                             0.107 |              0.321 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      6 |                 0.022 |                             0.085 |              0.321 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      8 |                 0.121 |                             0.056 |              0.321 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |     10 |                 0.176 |                             0.058 |              0.321 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |     12 |                 0.247 |                             0.075 |              0.321 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |     16 |                 0.358 |                             0.037 |              0.321 | True                 | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      1 |                -0.099 |                             0.081 |              0.460 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      2 |                -0.046 |                             0.077 |              0.460 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      3 |                 0.058 |                             0.064 |              0.460 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      4 |                 0.106 |                             0.060 |              0.460 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      6 |                 0.160 |                             0.062 |              0.460 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      8 |                 0.220 |                             0.062 |              0.460 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |     10 |                 0.311 |                             0.065 |              0.460 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |     12 |                 0.409 |                             0.038 |              0.460 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |     16 |                 0.494 |                             0.034 |              0.460 | True                 | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      1 |                -0.109 |                             0.060 |              0.428 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      2 |                -0.030 |                             0.071 |              0.428 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      3 |                 0.065 |                             0.053 |              0.428 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      4 |                 0.103 |                             0.063 |              0.428 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      6 |                 0.151 |                             0.052 |              0.428 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      8 |                 0.212 |                             0.048 |              0.428 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |     10 |                 0.289 |                             0.067 |              0.428 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |     12 |                 0.368 |                             0.032 |              0.428 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |     16 |                 0.468 |                             0.040 |              0.428 | True                 | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      1 |                -0.098 |                             0.070 |              0.348 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      2 |                -0.031 |                             0.059 |              0.348 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      3 |                 0.012 |                             0.051 |              0.348 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      4 |                 0.043 |                             0.086 |              0.348 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      6 |                 0.088 |                             0.049 |              0.348 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      8 |                 0.163 |                             0.058 |              0.348 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |     10 |                 0.200 |                             0.075 |              0.348 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |     12 |                 0.306 |                             0.073 |              0.348 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |     16 |                 0.396 |                             0.047 |              0.348 | True                 | CHAR35_TFIDF_SVD24 |

### Confirmation Shared-Method Summary

| representation     | method               |   selected_rank |   confirmation_mean_r2 |   observed_z |   max_t_fwer_p | status                  |
|:-------------------|:---------------------|----------------:|-----------------------:|-------------:|---------------:|:------------------------|
| WORD12_TFIDF_SVD24 | CONSENSUS_COVARIANCE |              16 |                  0.426 |       31.556 |          0.033 | FWER_POSITIVE_SUPPORTED |
| WORD12_TFIDF_SVD24 | CONCAT_PCA           |              16 |                  0.411 |       32.612 |          0.033 | FWER_POSITIVE_SUPPORTED |
| WORD12_TFIDF_SVD24 | RGCCA_SUMCOR         |              16 |                  0.393 |       30.242 |          0.033 | FWER_POSITIVE_SUPPORTED |
| CHAR35_TFIDF_SVD24 | CONSENSUS_COVARIANCE |              16 |                  0.544 |       34.584 |          0.033 | FWER_POSITIVE_SUPPORTED |
| CHAR35_TFIDF_SVD24 | CONCAT_PCA           |              16 |                  0.526 |       28.923 |          0.033 | FWER_POSITIVE_SUPPORTED |
| CHAR35_TFIDF_SVD24 | RGCCA_SUMCOR         |              16 |                  0.525 |       29.889 |          0.033 | FWER_POSITIVE_SUPPORTED |

### Direct Ridge Comparator

| representation     | method       |   mean_directed_r2 |
|:-------------------|:-------------|-------------------:|
| CHAR35_TFIDF_SVD24 | DIRECT_RIDGE |              0.590 |
| WORD12_TFIDF_SVD24 | DIRECT_RIDGE |              0.513 |

## Decision

```json
{
  "status": "SUBSPACE_COMPARISON_SUPPORTED",
  "best_supported_method": {
    "representation": "CHAR35_TFIDF_SVD24",
    "method": "CONSENSUS_COVARIANCE",
    "confirmation_mean_r2": 0.5436754173851319
  },
  "direct_ridge_is_comparator_not_shared_subspace": true,
  "rank_status": "RANK_UNRESOLVED_AT_REGISTERED_GRID_BOUNDARY",
  "rank_boundary_requires_fresh_expanded_grid": true,
  "cohort_commitment": {
    "cohort_recipe": {
      "cohort_id": "v7.3-w4b-multiview-rank-extension-1",
      "seed": 20260716,
      "min_comments_per_user": 32,
      "max_users": 120
    },
    "n_authors": 120,
    "membership_sha256": "31be87739444bf6688deb51dcf5a92017b14919fbfe5af91fddc1be64628908c",
    "raw_identifiers_persisted": false
  },
  "claim_boundary": "Mathematical multiview comparison only; no factor naming, personality, causal, or clinical claim."
}
```

## Boundary

This is a comparison of anonymous shared-text representations. A method outperforming broken correspondence does not identify an axis, author core, psychological construct, or clinical score. A selected rank at the registered grid maximum is explicitly unresolved and must be tested on a fresh cohort with an expanded grid. `JIVE_AJIVE` is explicitly unavailable unless its actual optional dependency is present; no surrogate is renamed as JIVE.

Artifacts: `results/v7_multiview_benchmark/w4b_quick_20260715`
