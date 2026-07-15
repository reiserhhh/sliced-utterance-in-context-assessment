# SUICA V7 Time-Separated Geometry Baselines

## Design

Each new author contributes an earliest and latest source-comment panel before any vectorization. The panels are source-disjoint and selected from a fresh cohort excluding E0--E4. TF-IDF/SVD representations are fit on discovery authors only; scaling, opportunity sensitivity surfaces, and linear transport maps are fit without confirmation authors.

Subreddit/topic choice is retained as part of the text process. The opportunity-only and opportunity-adjusted arms concern text amount and format only; they are sensitivity controls, not a claim that selection is noise.

### Time-Panel Support

| split        | variable              |   n |       mean |    median |    q025 |        q975 |
|:-------------|:----------------------|----:|-----------:|----------:|--------:|------------:|
| calibration  | early_source_comments |  30 |     12.000 |    12.000 |  12.000 |      12.000 |
| calibration  | late_source_comments  |  30 |     12.000 |    12.000 |  12.000 |      12.000 |
| calibration  | early_tokens          |  30 |    689.867 |   581.500 | 270.575 |    1462.000 |
| calibration  | late_tokens           |  30 |    655.500 |   578.500 | 240.150 |    1307.200 |
| calibration  | temporal_gap          |  30 | 170183.467 | 32840.500 | 161.600 |  911980.050 |
| calibration  | source_overlap_count  |  30 |      0.000 |     0.000 |   0.000 |       0.000 |
| confirmation | early_source_comments |  23 |     12.000 |    12.000 |  12.000 |      12.000 |
| confirmation | late_source_comments  |  23 |     12.000 |    12.000 |  12.000 |      12.000 |
| confirmation | early_tokens          |  23 |    617.826 |   569.000 | 285.750 |    1249.500 |
| confirmation | late_tokens           |  23 |    580.609 |   527.000 | 283.000 |    1069.450 |
| confirmation | temporal_gap          |  23 | 844686.609 | 90728.000 | 304.000 | 5596611.000 |
| confirmation | source_overlap_count  |  23 |      0.000 |     0.000 |   0.000 |       0.000 |
| discovery    | early_source_comments |  67 |     12.000 |    12.000 |  12.000 |      12.000 |
| discovery    | late_source_comments  |  67 |     12.000 |    12.000 |  12.000 |      12.000 |
| discovery    | early_tokens          |  67 |    709.478 |   639.000 | 313.850 |    1568.450 |
| discovery    | late_tokens           |  67 |    723.731 |   660.000 | 305.900 |    1605.500 |
| discovery    | temporal_gap          |  67 | 343502.507 | 85362.000 |  70.750 |  982965.850 |
| discovery    | source_overlap_count  |  67 |      0.000 |     0.000 |   0.000 |       0.000 |

### Condition-Selection Descriptives (Not Residualized)

| split        | variable              |   n |   mean |   median |   q025 |   q975 |
|:-------------|:----------------------|----:|-------:|---------:|-------:|-------:|
| calibration  | early_condition_count |  30 |  6.600 |    7.000 |  2.000 | 11.000 |
| calibration  | late_condition_count  |  30 |  6.533 |    6.000 |  1.000 | 11.000 |
| calibration  | condition_jaccard     |  30 |  0.233 |    0.211 |  0.056 |  0.512 |
| confirmation | early_condition_count |  23 |  7.522 |    8.000 |  4.100 | 11.450 |
| confirmation | late_condition_count  |  23 |  7.217 |    8.000 |  2.650 | 10.450 |
| confirmation | condition_jaccard     |  23 |  0.166 |    0.167 |  0.000 |  0.369 |
| discovery    | early_condition_count |  67 |  7.194 |    7.000 |  2.650 | 11.000 |
| discovery    | late_condition_count  |  67 |  7.313 |    7.000 |  3.000 | 12.000 |
| discovery    | condition_jaccard     |  67 |  0.232 |    0.167 |  0.034 |  0.837 |

### Confirmation Endpoints

| representation             | variant                   | metric                     |   statistic |   n_features |   n_confirmation_authors |   observed_z |   raw_permutation_p |   max_t_fwer_p | positive_direction   | status                      |
|:---------------------------|:--------------------------|:---------------------------|------------:|-------------:|-------------------------:|-------------:|--------------------:|---------------:|:---------------------|:----------------------------|
| WORD12_TFIDF_SVD24         | raw_text                  | alignment_auc              |       0.719 |           12 |                       23 |        4.022 |               0.033 |          0.033 | True                 | FWER_POSITIVE_SUPPORTED     |
| WORD12_TFIDF_SVD24         | raw_text                  | relative_distance_spearman |       0.231 |           12 |                       23 |        1.405 |               0.067 |          0.733 | True                 | UNRESOLVED                  |
| WORD12_TFIDF_SVD24         | raw_text                  | linear_transport_r2        |      -0.016 |           12 |                       23 |        2.433 |               0.033 |          0.200 | False                | UNRESOLVED                  |
| WORD12_TFIDF_SVD24         | opportunity_adjusted_text | alignment_auc              |       0.634 |           12 |                       23 |        2.045 |               0.033 |          0.233 | True                 | UNRESOLVED                  |
| WORD12_TFIDF_SVD24         | opportunity_adjusted_text | relative_distance_spearman |      -0.029 |           12 |                       23 |       -0.226 |               0.533 |          1.000 | False                | UNRESOLVED                  |
| WORD12_TFIDF_SVD24         | opportunity_adjusted_text | linear_transport_r2        |      -0.196 |           12 |                       23 |       -0.408 |               0.733 |          1.000 | False                | UNRESOLVED                  |
| CHAR35_TFIDF_SVD24         | raw_text                  | alignment_auc              |       0.749 |           12 |                       23 |        4.713 |               0.033 |          0.033 | True                 | FWER_POSITIVE_SUPPORTED     |
| CHAR35_TFIDF_SVD24         | raw_text                  | relative_distance_spearman |       0.385 |           12 |                       23 |        2.355 |               0.033 |          0.200 | True                 | UNRESOLVED                  |
| CHAR35_TFIDF_SVD24         | raw_text                  | linear_transport_r2        |      -0.008 |           12 |                       23 |        3.857 |               0.033 |          0.033 | False                | FWER_NONPOSITIVE_DIFFERENCE |
| CHAR35_TFIDF_SVD24         | opportunity_adjusted_text | alignment_auc              |       0.674 |           12 |                       23 |        3.388 |               0.033 |          0.033 | True                 | FWER_POSITIVE_SUPPORTED     |
| CHAR35_TFIDF_SVD24         | opportunity_adjusted_text | relative_distance_spearman |       0.125 |           12 |                       23 |        0.809 |               0.267 |          0.900 | True                 | UNRESOLVED                  |
| CHAR35_TFIDF_SVD24         | opportunity_adjusted_text | linear_transport_r2        |      -0.141 |           12 |                       23 |        1.324 |               0.133 |          0.733 | False                | UNRESOLVED                  |
| WORD1_TFIDF_SVD24          | raw_text                  | alignment_auc              |       0.727 |           12 |                       23 |        4.745 |               0.033 |          0.033 | True                 | FWER_POSITIVE_SUPPORTED     |
| WORD1_TFIDF_SVD24          | raw_text                  | relative_distance_spearman |       0.228 |           12 |                       23 |        1.430 |               0.100 |          0.700 | True                 | UNRESOLVED                  |
| WORD1_TFIDF_SVD24          | raw_text                  | linear_transport_r2        |      -0.016 |           12 |                       23 |        2.719 |               0.033 |          0.100 | False                | UNRESOLVED                  |
| WORD1_TFIDF_SVD24          | opportunity_adjusted_text | alignment_auc              |       0.717 |           12 |                       23 |        4.483 |               0.033 |          0.033 | True                 | FWER_POSITIVE_SUPPORTED     |
| WORD1_TFIDF_SVD24          | opportunity_adjusted_text | relative_distance_spearman |       0.008 |           12 |                       23 |       -0.061 |               0.633 |          1.000 | True                 | UNRESOLVED                  |
| WORD1_TFIDF_SVD24          | opportunity_adjusted_text | linear_transport_r2        |      -0.150 |           12 |                       23 |        0.480 |               0.333 |          1.000 | False                | UNRESOLVED                  |
| STRUCTURAL_OPPORTUNITY     | opportunity_only          | alignment_auc              |       0.597 |           13 |                       23 |        1.374 |               0.133 |          0.733 | True                 | UNRESOLVED                  |
| STRUCTURAL_OPPORTUNITY     | opportunity_only          | relative_distance_spearman |       0.089 |           13 |                       23 |        0.702 |               0.233 |          0.967 | True                 | UNRESOLVED                  |
| STRUCTURAL_OPPORTUNITY     | opportunity_only          | linear_transport_r2        |      -0.145 |           13 |                       23 |        1.147 |               0.133 |          0.867 | False                | UNRESOLVED                  |
| DETERMINISTIC_SOURCE_NOISE | deterministic_noise       | alignment_auc              |       0.516 |           24 |                       23 |        0.553 |               0.367 |          1.000 | True                 | UNRESOLVED                  |
| DETERMINISTIC_SOURCE_NOISE | deterministic_noise       | relative_distance_spearman |      -0.140 |           24 |                       23 |       -0.854 |               0.800 |          1.000 | False                | UNRESOLVED                  |
| DETERMINISTIC_SOURCE_NOISE | deterministic_noise       | linear_transport_r2        |      -0.396 |           24 |                       23 |        0.258 |               0.433 |          1.000 | False                | UNRESOLVED                  |

## Decision

```json
{
  "status": "TEMPORAL_GEOMETRY_UNRESOLVED",
  "supported_raw_text_representations": [],
  "best_raw_text_alignment_auc": 0.7490118577075099,
  "opportunity_only_alignment_auc": 0.5968379446640316,
  "opportunity_control_competitive": false,
  "deterministic_noise_has_fwer_supported_endpoint": false,
  "claim_boundary": "Within-PANDORA time-separated technical geometry only. The result cannot identify personality, eliminate context/selection, or establish cross-occasion psychological measurement."
}
```

## Interpretation Boundary

`FWER_POSITIVE_SUPPORTED` means only that a registered technical endpoint exceeded its correspondence-permuted family in its meaningful direction under this corpus and time split. `FWER_NONPOSITIVE_DIFFERENCE` is not positive evidence. It does not name a factor, prove an author core, or license personality/clinical interpretation. A competitive opportunity-only arm is a warning that expression opportunity remains an alternative explanation, not a reason to erase selection or language content.

Artifacts: `results/v7_temporal_geometry/w3_quick_v2_20260715`
