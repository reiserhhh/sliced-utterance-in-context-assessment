# SUICA V7 Time-Separated Geometry Baselines

## Design

Each new author contributes an earliest and latest source-comment panel before any vectorization. The panels are source-disjoint and selected from a fresh cohort excluding E0--E4. TF-IDF/SVD representations are fit on discovery authors only; scaling, opportunity sensitivity surfaces, and linear transport maps are fit without confirmation authors.

Subreddit/topic choice is retained as part of the text process. The opportunity-only and opportunity-adjusted arms concern text amount and format only; they are sensitivity controls, not a claim that selection is noise.

### Time-Panel Support

| split        | variable              |   n |       mean |    median |    q025 |        q975 |
|:-------------|:----------------------|----:|-----------:|----------:|--------:|------------:|
| calibration  | early_source_comments |  76 |     16.000 |    16.000 |  16.000 |      16.000 |
| calibration  | late_source_comments  |  76 |     16.000 |    16.000 |  16.000 |      16.000 |
| calibration  | early_tokens          |  76 |    938.237 |   826.500 | 364.125 |    2095.625 |
| calibration  | late_tokens           |  76 |    902.145 |   756.000 | 348.625 |    2189.125 |
| calibration  | temporal_gap          |  76 | 357689.342 | 40098.500 | 149.000 | 1492917.375 |
| calibration  | source_overlap_count  |  76 |      0.000 |     0.000 |   0.000 |       0.000 |
| confirmation | early_source_comments |  57 |     16.000 |    16.000 |  16.000 |      16.000 |
| confirmation | late_source_comments  |  57 |     16.000 |    16.000 |  16.000 |      16.000 |
| confirmation | early_tokens          |  57 |    846.526 |   838.000 | 411.800 |    1510.600 |
| confirmation | late_tokens           |  57 |    889.368 |   821.000 | 393.600 |    1816.400 |
| confirmation | temporal_gap          |  57 | 421975.930 | 64973.000 |  67.200 | 3797859.600 |
| confirmation | source_overlap_count  |  57 |      0.000 |     0.000 |   0.000 |       0.000 |
| discovery    | early_source_comments | 167 |     16.000 |    16.000 |  16.000 |      16.000 |
| discovery    | late_source_comments  | 167 |     16.000 |    16.000 |  16.000 |      16.000 |
| discovery    | early_tokens          | 167 |    972.683 |   864.000 | 400.350 |    1841.800 |
| discovery    | late_tokens           | 167 |    934.461 |   809.000 | 404.200 |    2282.350 |
| discovery    | temporal_gap          | 167 | 226915.078 | 38429.000 |  86.000 | 1036493.300 |
| discovery    | source_overlap_count  | 167 |      0.000 |     0.000 |   0.000 |       0.000 |

### Condition-Selection Descriptives (Not Residualized)

| split        | variable              |   n |   mean |   median |   q025 |   q975 |
|:-------------|:----------------------|----:|-------:|---------:|-------:|-------:|
| calibration  | early_condition_count |  76 |  8.053 |    9.000 |  2.875 | 13.125 |
| calibration  | late_condition_count  |  76 |  8.171 |    9.000 |  1.875 | 14.000 |
| calibration  | condition_jaccard     |  76 |  0.254 |    0.231 |  0.054 |  0.608 |
| confirmation | early_condition_count |  57 |  8.877 |    9.000 |  4.000 | 15.000 |
| confirmation | late_condition_count  |  57 |  9.246 |   10.000 |  4.000 | 14.000 |
| confirmation | condition_jaccard     |  57 |  0.186 |    0.158 |  0.062 |  0.431 |
| discovery    | early_condition_count | 167 |  7.970 |    8.000 |  2.000 | 14.850 |
| discovery    | late_condition_count  | 167 |  8.623 |    9.000 |  2.150 | 14.000 |
| discovery    | condition_jaccard     | 167 |  0.225 |    0.190 |  0.034 |  0.650 |

### Confirmation Endpoints

| representation             | variant                   | metric                     |   statistic |   n_features |   n_confirmation_authors |   observed_z |   raw_permutation_p |   max_t_fwer_p | positive_direction   | status                      |
|:---------------------------|:--------------------------|:---------------------------|------------:|-------------:|-------------------------:|-------------:|--------------------:|---------------:|:---------------------|:----------------------------|
| WORD12_TFIDF_SVD24         | raw_text                  | alignment_auc              |       0.776 |           24 |                       57 |       10.337 |               0.005 |          0.005 | True                 | FWER_POSITIVE_SUPPORTED     |
| WORD12_TFIDF_SVD24         | raw_text                  | relative_distance_spearman |       0.274 |           24 |                       57 |        2.893 |               0.005 |          0.040 | True                 | FWER_POSITIVE_SUPPORTED     |
| WORD12_TFIDF_SVD24         | raw_text                  | linear_transport_r2        |      -0.031 |           24 |                       57 |        4.838 |               0.005 |          0.005 | False                | FWER_NONPOSITIVE_DIFFERENCE |
| WORD12_TFIDF_SVD24         | opportunity_adjusted_text | alignment_auc              |       0.729 |           24 |                       57 |        8.614 |               0.005 |          0.005 | True                 | FWER_POSITIVE_SUPPORTED     |
| WORD12_TFIDF_SVD24         | opportunity_adjusted_text | relative_distance_spearman |       0.160 |           24 |                       57 |        1.677 |               0.040 |          0.525 | True                 | UNRESOLVED                  |
| WORD12_TFIDF_SVD24         | opportunity_adjusted_text | linear_transport_r2        |      -0.078 |           24 |                       57 |        2.701 |               0.005 |          0.055 | False                | UNRESOLVED                  |
| CHAR35_TFIDF_SVD24         | raw_text                  | alignment_auc              |       0.821 |           24 |                       57 |        9.885 |               0.005 |          0.005 | True                 | FWER_POSITIVE_SUPPORTED     |
| CHAR35_TFIDF_SVD24         | raw_text                  | relative_distance_spearman |       0.217 |           24 |                       57 |        2.642 |               0.010 |          0.060 | True                 | UNRESOLVED                  |
| CHAR35_TFIDF_SVD24         | raw_text                  | linear_transport_r2        |       0.024 |           24 |                       57 |        6.272 |               0.005 |          0.005 | True                 | FWER_POSITIVE_SUPPORTED     |
| CHAR35_TFIDF_SVD24         | opportunity_adjusted_text | alignment_auc              |       0.759 |           24 |                       57 |        7.477 |               0.005 |          0.005 | True                 | FWER_POSITIVE_SUPPORTED     |
| CHAR35_TFIDF_SVD24         | opportunity_adjusted_text | relative_distance_spearman |       0.138 |           24 |                       57 |        1.666 |               0.050 |          0.525 | True                 | UNRESOLVED                  |
| CHAR35_TFIDF_SVD24         | opportunity_adjusted_text | linear_transport_r2        |      -0.008 |           24 |                       57 |        5.079 |               0.005 |          0.005 | False                | FWER_NONPOSITIVE_DIFFERENCE |
| WORD1_TFIDF_SVD24          | raw_text                  | alignment_auc              |       0.738 |           24 |                       57 |        8.182 |               0.005 |          0.005 | True                 | FWER_POSITIVE_SUPPORTED     |
| WORD1_TFIDF_SVD24          | raw_text                  | relative_distance_spearman |       0.233 |           24 |                       57 |        2.624 |               0.010 |          0.070 | True                 | UNRESOLVED                  |
| WORD1_TFIDF_SVD24          | raw_text                  | linear_transport_r2        |      -0.003 |           24 |                       57 |        5.762 |               0.005 |          0.005 | False                | FWER_NONPOSITIVE_DIFFERENCE |
| WORD1_TFIDF_SVD24          | opportunity_adjusted_text | alignment_auc              |       0.685 |           24 |                       57 |        6.074 |               0.005 |          0.005 | True                 | FWER_POSITIVE_SUPPORTED     |
| WORD1_TFIDF_SVD24          | opportunity_adjusted_text | relative_distance_spearman |       0.131 |           24 |                       57 |        1.589 |               0.060 |          0.580 | True                 | UNRESOLVED                  |
| WORD1_TFIDF_SVD24          | opportunity_adjusted_text | linear_transport_r2        |      -0.045 |           24 |                       57 |        3.931 |               0.005 |          0.005 | False                | FWER_NONPOSITIVE_DIFFERENCE |
| STRUCTURAL_OPPORTUNITY     | opportunity_only          | alignment_auc              |       0.625 |           13 |                       57 |        3.787 |               0.005 |          0.005 | True                 | FWER_POSITIVE_SUPPORTED     |
| STRUCTURAL_OPPORTUNITY     | opportunity_only          | relative_distance_spearman |       0.199 |           13 |                       57 |        4.714 |               0.005 |          0.005 | True                 | FWER_POSITIVE_SUPPORTED     |
| STRUCTURAL_OPPORTUNITY     | opportunity_only          | linear_transport_r2        |       0.235 |           13 |                       57 |        4.093 |               0.005 |          0.005 | True                 | FWER_POSITIVE_SUPPORTED     |
| DETERMINISTIC_SOURCE_NOISE | deterministic_noise       | alignment_auc              |       0.495 |           24 |                       57 |       -0.072 |               0.495 |          1.000 | False                | UNRESOLVED                  |
| DETERMINISTIC_SOURCE_NOISE | deterministic_noise       | relative_distance_spearman |       0.079 |           24 |                       57 |        1.229 |               0.120 |          0.830 | True                 | UNRESOLVED                  |
| DETERMINISTIC_SOURCE_NOISE | deterministic_noise       | linear_transport_r2        |      -0.082 |           24 |                       57 |        1.130 |               0.120 |          0.885 | False                | UNRESOLVED                  |

## Decision

```json
{
  "status": "TECHNICAL_TEMPORAL_GEOMETRY_SUPPORTED",
  "supported_raw_text_representations": [
    "WORD12_TFIDF_SVD24"
  ],
  "best_raw_text_alignment_auc": 0.8214285714285714,
  "opportunity_only_alignment_auc": 0.6246867167919798,
  "opportunity_control_competitive": false,
  "deterministic_noise_has_fwer_supported_endpoint": false,
  "claim_boundary": "Within-PANDORA time-separated technical geometry only. The result cannot identify personality, eliminate context/selection, or establish cross-occasion psychological measurement."
}
```

## Interpretation Boundary

`FWER_POSITIVE_SUPPORTED` means only that a registered technical endpoint exceeded its correspondence-permuted family in its meaningful direction under this corpus and time split. `FWER_NONPOSITIVE_DIFFERENCE` is not positive evidence. It does not name a factor, prove an author core, or license personality/clinical interpretation. A competitive opportunity-only arm is a warning that expression opportunity remains an alternative explanation, not a reason to erase selection or language content.

Artifacts: `results/v7_temporal_geometry/w3_full_20260715`
