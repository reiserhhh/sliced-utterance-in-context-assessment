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
| CONSENSUS_COVARIANCE |      1 |                -0.085 |                             0.028 |              0.319 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      2 |                -0.035 |                             0.030 |              0.319 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      3 |                -0.000 |                             0.031 |              0.319 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      4 |                 0.038 |                             0.033 |              0.319 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      6 |                 0.105 |                             0.031 |              0.319 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      8 |                 0.155 |                             0.025 |              0.319 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |     10 |                 0.206 |                             0.031 |              0.319 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |     12 |                 0.253 |                             0.031 |              0.319 | False                | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |     16 |                 0.346 |                             0.026 |              0.319 | True                 | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      1 |                -0.085 |                             0.025 |              0.310 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      2 |                -0.036 |                             0.034 |              0.310 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      3 |                -0.007 |                             0.029 |              0.310 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      4 |                 0.037 |                             0.034 |              0.310 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      6 |                 0.114 |                             0.031 |              0.310 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |      8 |                 0.177 |                             0.029 |              0.310 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |     10 |                 0.216 |                             0.030 |              0.310 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |     12 |                 0.260 |                             0.025 |              0.310 | False                | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           |     16 |                 0.334 |                             0.025 |              0.310 | True                 | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      1 |                -0.095 |                             0.030 |              0.249 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      2 |                -0.062 |                             0.029 |              0.249 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      3 |                -0.013 |                             0.031 |              0.249 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      4 |                 0.027 |                             0.032 |              0.249 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      6 |                 0.075 |                             0.028 |              0.249 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      8 |                 0.103 |                             0.033 |              0.249 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |     10 |                 0.148 |                             0.029 |              0.249 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |     12 |                 0.208 |                             0.025 |              0.249 | False                | WORD12_TFIDF_SVD24 |
| RGCCA_SUMCOR         |     16 |                 0.279 |                             0.029 |              0.249 | True                 | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      1 |                -0.070 |                             0.036 |              0.319 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      2 |                 0.009 |                             0.043 |              0.319 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      3 |                 0.050 |                             0.038 |              0.319 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      4 |                 0.123 |                             0.044 |              0.319 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      6 |                 0.157 |                             0.043 |              0.319 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |      8 |                 0.196 |                             0.034 |              0.319 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |     10 |                 0.236 |                             0.041 |              0.319 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |     12 |                 0.269 |                             0.041 |              0.319 | False                | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE |     16 |                 0.360 |                             0.041 |              0.319 | True                 | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      1 |                -0.077 |                             0.039 |              0.306 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      2 |                 0.006 |                             0.031 |              0.306 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      3 |                 0.046 |                             0.037 |              0.306 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      4 |                 0.116 |                             0.046 |              0.306 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      6 |                 0.152 |                             0.043 |              0.306 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |      8 |                 0.196 |                             0.041 |              0.306 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |     10 |                 0.232 |                             0.036 |              0.306 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |     12 |                 0.265 |                             0.044 |              0.306 | False                | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           |     16 |                 0.343 |                             0.037 |              0.306 | True                 | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      1 |                -0.084 |                             0.036 |              0.266 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      2 |                -0.027 |                             0.036 |              0.266 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      3 |                 0.035 |                             0.039 |              0.266 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      4 |                 0.083 |                             0.042 |              0.266 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      6 |                 0.124 |                             0.038 |              0.266 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |      8 |                 0.182 |                             0.040 |              0.266 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |     10 |                 0.211 |                             0.038 |              0.266 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |     12 |                 0.230 |                             0.046 |              0.266 | False                | CHAR35_TFIDF_SVD24 |
| RGCCA_SUMCOR         |     16 |                 0.311 |                             0.045 |              0.266 | True                 | CHAR35_TFIDF_SVD24 |

### Confirmation Shared-Method Summary

| representation     | method               |   selected_rank |   confirmation_mean_r2 |   observed_z |   max_t_fwer_p | status                  |
|:-------------------|:---------------------|----------------:|-----------------------:|-------------:|---------------:|:------------------------|
| WORD12_TFIDF_SVD24 | CONSENSUS_COVARIANCE |              16 |                  0.397 |       35.690 |          0.010 | FWER_POSITIVE_SUPPORTED |
| WORD12_TFIDF_SVD24 | CONCAT_PCA           |              16 |                  0.396 |       42.333 |          0.010 | FWER_POSITIVE_SUPPORTED |
| WORD12_TFIDF_SVD24 | RGCCA_SUMCOR         |              16 |                  0.341 |       44.660 |          0.010 | FWER_POSITIVE_SUPPORTED |
| CHAR35_TFIDF_SVD24 | CONSENSUS_COVARIANCE |              16 |                  0.395 |       39.901 |          0.010 | FWER_POSITIVE_SUPPORTED |
| CHAR35_TFIDF_SVD24 | CONCAT_PCA           |              16 |                  0.395 |       49.827 |          0.010 | FWER_POSITIVE_SUPPORTED |
| CHAR35_TFIDF_SVD24 | RGCCA_SUMCOR         |              16 |                  0.353 |       48.964 |          0.010 | FWER_POSITIVE_SUPPORTED |

### Paired Confirmation Method Differences

| first_method         | second_method        |   mean_r2_difference_first_minus_second |   ci_low |   ci_high |   material_threshold | status                                  | representation     |
|:---------------------|:---------------------|----------------------------------------:|---------:|----------:|---------------------:|:----------------------------------------|:-------------------|
| CONCAT_PCA           | CONSENSUS_COVARIANCE |                                  -0.001 |   -0.009 |     0.006 |                0.020 | NO_MATERIAL_PAIRED_DIFFERENCE_SUPPORTED | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           | RGCCA_SUMCOR         |                                   0.054 |    0.036 |     0.078 |                0.020 | MATERIAL_FIRST_OVER_SECOND_SUPPORTED    | WORD12_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE | RGCCA_SUMCOR         |                                   0.056 |    0.039 |     0.078 |                0.020 | MATERIAL_FIRST_OVER_SECOND_SUPPORTED    | WORD12_TFIDF_SVD24 |
| CONCAT_PCA           | CONSENSUS_COVARIANCE |                                   0.000 |   -0.008 |     0.008 |                0.020 | NO_MATERIAL_PAIRED_DIFFERENCE_SUPPORTED | CHAR35_TFIDF_SVD24 |
| CONCAT_PCA           | RGCCA_SUMCOR         |                                   0.042 |    0.023 |     0.066 |                0.020 | MATERIAL_FIRST_OVER_SECOND_SUPPORTED    | CHAR35_TFIDF_SVD24 |
| CONSENSUS_COVARIANCE | RGCCA_SUMCOR         |                                   0.042 |    0.020 |     0.067 |                0.020 | NO_MATERIAL_PAIRED_DIFFERENCE_SUPPORTED | CHAR35_TFIDF_SVD24 |

### Direct Ridge Comparator

| representation     | method       |   mean_directed_r2 |
|:-------------------|:-------------|-------------------:|
| CHAR35_TFIDF_SVD24 | DIRECT_RIDGE |              0.630 |
| WORD12_TFIDF_SVD24 | DIRECT_RIDGE |              0.621 |

## Decision

```json
{
  "status": "SUBSPACE_COMPARISON_SUPPORTED",
  "highest_supported_endpoint_descriptive_only": {
    "representation": "WORD12_TFIDF_SVD24",
    "method": "CONSENSUS_COVARIANCE",
    "confirmation_mean_r2": 0.397016584941594
  },
  "method_superiority_status": "WITHIN_COHORT_MATERIAL_DIFFERENCE_SUPPORTED",
  "direct_ridge_is_comparator_not_shared_subspace": true,
  "rank_status": "RANK_UNRESOLVED_AT_REGISTERED_GRID_BOUNDARY",
  "rank_boundary_action": "REFUSE_FACTOR_COUNT_USE_EFFECTIVE_RANK_DIAGNOSTIC",
  "rank_selection_role": "TRANSPORT_CAPACITY_PARAMETER_NOT_FACTOR_COUNT",
  "cohort_commitment": {
    "cohort_recipe": {
      "cohort_id": "v7.3-w4b-multiview-rank-extension-1",
      "seed": 20260716,
      "min_comments_per_user": 32,
      "max_users": 200
    },
    "n_authors": 200,
    "membership_sha256": "89c33105707a549d7d5ac2dfe77d5160c0d330e306904c920a620bff0384a677",
    "raw_identifiers_persisted": false
  },
  "claim_boundary": "Mathematical multiview comparison only; no factor naming, personality, causal, or clinical claim."
}
```

## Boundary

This is a comparison of anonymous shared-text representations. A method outperforming broken correspondence does not identify an axis, author core, psychological construct, or clinical score. A selected rank at the registered grid maximum is explicitly unresolved: a transport criterion must not be extended indefinitely and reinterpreted as a factor count. The declared boundary action determines whether a fresh capacity check or a separate effective-rank diagnostic is appropriate. `JIVE_AJIVE` is explicitly unavailable unless its actual optional dependency is present; no surrogate is renamed as JIVE.

Artifacts: `results/v7_multiview_benchmark/w4b_corrected_full_20260715`
