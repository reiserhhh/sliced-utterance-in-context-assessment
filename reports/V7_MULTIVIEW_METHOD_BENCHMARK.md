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
| CONSENSUS_COVARIANCE |      1 |                -0.042 |                             0.034 |              0.190 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      2 |                 0.037 |                             0.035 |              0.190 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      3 |                 0.076 |                             0.031 |              0.190 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      4 |                 0.103 |                             0.027 |              0.190 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      6 |                 0.175 |                             0.026 |              0.190 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      8 |                 0.216 |                             0.026 |              0.190 | True                 | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      1 |                -0.042 |                             0.033 |              0.187 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      2 |                 0.045 |                             0.028 |              0.187 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      3 |                 0.077 |                             0.028 |              0.187 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      4 |                 0.095 |                             0.027 |              0.187 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      6 |                 0.177 |                             0.025 |              0.187 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      8 |                 0.211 |                             0.025 |              0.187 | True                 | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      1 |                -0.059 |                             0.034 |              0.133 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      2 |                -0.017 |                             0.032 |              0.133 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      3 |                 0.023 |                             0.034 |              0.133 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      4 |                 0.062 |                             0.031 |              0.133 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      6 |                 0.104 |                             0.030 |              0.133 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      8 |                 0.162 |                             0.029 |              0.133 | True                 | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      1 |                 0.015 |                             0.020 |              0.216 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      2 |                 0.076 |                             0.025 |              0.216 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      3 |                 0.098 |                             0.025 |              0.216 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      4 |                 0.121 |                             0.026 |              0.216 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      6 |                 0.191 |                             0.023 |              0.216 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      8 |                 0.239 |                             0.023 |              0.216 | True                 | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      1 |                 0.012 |                             0.020 |              0.215 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      2 |                 0.072 |                             0.023 |              0.215 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      3 |                 0.093 |                             0.025 |              0.215 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      4 |                 0.125 |                             0.024 |              0.215 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      6 |                 0.195 |                             0.023 |              0.215 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      8 |                 0.236 |                             0.021 |              0.215 | True                 | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      1 |                -0.000 |                             0.022 |              0.183 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      2 |                 0.063 |                             0.024 |              0.183 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      3 |                 0.083 |                             0.023 |              0.183 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      4 |                 0.123 |                             0.025 |              0.183 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      6 |                 0.157 |                             0.022 |              0.183 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      8 |                 0.207 |                             0.023 |              0.183 | True                 | CHAR35_TFIDF_SVD24 |

### Confirmation Shared-Method Summary

| representation     | method               |   selected_rank |   confirmation_mean_r2 |   observed_z |   max_t_fwer_p | status                  |
|:-------------------|:---------------------|----------------:|-----------------------:|-------------:|---------------:|:------------------------|
| WORD12_TFIDF_SVD24 | CONSENSUS_COVARIANCE |               8 |                  0.257 |       31.888 |          0.010 | FWER_POSITIVE_SUPPORTED |
| WORD12_TFIDF_SVD24 | CONCAT_PCA           |               8 |                  0.267 |       41.664 |          0.010 | FWER_POSITIVE_SUPPORTED |
| WORD12_TFIDF_SVD24 | RGCCA_SUMCOR         |               8 |                  0.232 |       40.606 |          0.010 | FWER_POSITIVE_SUPPORTED |
| CHAR35_TFIDF_SVD24 | CONSENSUS_COVARIANCE |               8 |                  0.225 |       29.801 |          0.010 | FWER_POSITIVE_SUPPORTED |
| CHAR35_TFIDF_SVD24 | CONCAT_PCA           |               8 |                  0.237 |       34.376 |          0.010 | FWER_POSITIVE_SUPPORTED |
| CHAR35_TFIDF_SVD24 | RGCCA_SUMCOR         |               8 |                  0.232 |       42.040 |          0.010 | FWER_POSITIVE_SUPPORTED |

### Direct Ridge Comparator

| representation     | method       |   mean_directed_r2 |
|:-------------------|:-------------|-------------------:|
| CHAR35_TFIDF_SVD24 | DIRECT_RIDGE |              0.655 |
| WORD12_TFIDF_SVD24 | DIRECT_RIDGE |              0.661 |

## Decision

```json
{
  "status": "SUBSPACE_COMPARISON_SUPPORTED",
  "best_supported_method": {
    "representation": "WORD12_TFIDF_SVD24",
    "method": "CONCAT_PCA",
    "confirmation_mean_r2": 0.2668707153351155
  },
  "direct_ridge_is_comparator_not_shared_subspace": true,
  "claim_boundary": "Mathematical multiview comparison only; no factor naming, personality, causal, or clinical claim."
}
```

## Boundary

This is a comparison of anonymous shared-text representations. A method outperforming broken correspondence does not identify an axis, author core, psychological construct, or clinical score. `JIVE_AJIVE` is explicitly unavailable unless its actual optional dependency is present; no surrogate is renamed as JIVE.

Artifacts: `results/v7_multiview_benchmark/w4_full_20260715`
