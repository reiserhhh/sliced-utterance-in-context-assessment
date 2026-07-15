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
| CONSENSUS_COVARIANCE |      1 |                -0.195 |                             0.104 |              0.137 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      2 |                -0.111 |                             0.110 |              0.137 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      3 |                -0.056 |                             0.073 |              0.137 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      4 |                -0.004 |                             0.092 |              0.137 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      6 |                 0.061 |                             0.111 |              0.137 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      8 |                 0.194 |                             0.057 |              0.137 | True                 | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      1 |                -0.195 |                             0.124 |              0.120 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      2 |                -0.114 |                             0.113 |              0.120 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      3 |                -0.075 |                             0.113 |              0.120 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      4 |                -0.004 |                             0.113 |              0.120 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      6 |                 0.064 |                             0.085 |              0.120 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      8 |                 0.179 |                             0.060 |              0.120 | True                 | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      1 |                -0.205 |                             0.086 |              0.048 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      2 |                -0.137 |                             0.102 |              0.048 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      3 |                -0.108 |                             0.079 |              0.048 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      4 |                -0.059 |                             0.098 |              0.048 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      6 |                 0.027 |                             0.109 |              0.048 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      8 |                 0.128 |                             0.080 |              0.048 | True                 | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      1 |                -0.093 |                             0.066 |              0.188 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      2 |                -0.021 |                             0.053 |              0.188 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      3 |                 0.020 |                             0.042 |              0.188 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      4 |                 0.083 |                             0.059 |              0.188 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      6 |                 0.144 |                             0.040 |              0.188 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      8 |                 0.255 |                             0.067 |              0.188 | True                 | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      1 |                -0.098 |                             0.069 |              0.161 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      2 |                -0.023 |                             0.058 |              0.161 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      3 |                 0.013 |                             0.063 |              0.161 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      4 |                 0.070 |                             0.051 |              0.161 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      6 |                 0.131 |                             0.029 |              0.161 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      8 |                 0.206 |                             0.045 |              0.161 | True                 | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      1 |                -0.096 |                             0.064 |              0.176 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      2 |                -0.037 |                             0.050 |              0.176 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      3 |                 0.006 |                             0.047 |              0.176 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      4 |                 0.078 |                             0.042 |              0.176 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      6 |                 0.136 |                             0.056 |              0.176 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      8 |                 0.226 |                             0.049 |              0.176 | True                 | CHAR35_TFIDF_SVD24 |

### Confirmation Shared-Method Summary

| representation     | method               |   selected_rank |   confirmation_mean_r2 |   observed_z |   max_t_fwer_p | status                  |
|:-------------------|:---------------------|----------------:|-----------------------:|-------------:|---------------:|:------------------------|
| WORD12_TFIDF_SVD24 | CONSENSUS_COVARIANCE |               8 |                  0.358 |       16.867 |          0.033 | FWER_POSITIVE_SUPPORTED |
| WORD12_TFIDF_SVD24 | CONCAT_PCA           |               8 |                  0.362 |       28.804 |          0.033 | FWER_POSITIVE_SUPPORTED |
| WORD12_TFIDF_SVD24 | RGCCA_SUMCOR         |               8 |                  0.344 |       24.259 |          0.033 | FWER_POSITIVE_SUPPORTED |
| CHAR35_TFIDF_SVD24 | CONSENSUS_COVARIANCE |               8 |                  0.346 |       23.803 |          0.033 | FWER_POSITIVE_SUPPORTED |
| CHAR35_TFIDF_SVD24 | CONCAT_PCA           |               8 |                  0.353 |       21.170 |          0.033 | FWER_POSITIVE_SUPPORTED |
| CHAR35_TFIDF_SVD24 | RGCCA_SUMCOR         |               8 |                  0.348 |       25.827 |          0.033 | FWER_POSITIVE_SUPPORTED |

### Direct Ridge Comparator

| representation     | method       |   mean_directed_r2 |
|:-------------------|:-------------|-------------------:|
| CHAR35_TFIDF_SVD24 | DIRECT_RIDGE |              0.646 |
| WORD12_TFIDF_SVD24 | DIRECT_RIDGE |              0.617 |

## Decision

```json
{
  "status": "SUBSPACE_COMPARISON_SUPPORTED",
  "best_supported_method": {
    "representation": "WORD12_TFIDF_SVD24",
    "method": "CONCAT_PCA",
    "confirmation_mean_r2": 0.3621674603489099
  },
  "direct_ridge_is_comparator_not_shared_subspace": true,
  "claim_boundary": "Mathematical multiview comparison only; no factor naming, personality, causal, or clinical claim."
}
```

## Boundary

This is a comparison of anonymous shared-text representations. A method outperforming broken correspondence does not identify an axis, author core, psychological construct, or clinical score. `JIVE_AJIVE` is explicitly unavailable unless its actual optional dependency is present; no surrogate is renamed as JIVE.

Artifacts: `results/v7_multiview_benchmark/w4_quick_v2_20260715`
