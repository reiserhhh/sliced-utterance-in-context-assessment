# SUICA V7 E2: Condition/Opportunity Contribution Accounting

## Scope

E2 tests an operator-indexed text-geometry accounting relation, not a
psychological scale:

\[
y_{ui}=\Phi_D(x_{ui}),\qquad
\widehat m(d)=\widehat E_D[y\mid d],
\]
\[
T_{uh}=\bar y_{uh}-\bar y_D,
\quad K_{uh}=\overline{\widehat m(d)}_{uh}-\overline{\widehat m(d)}_D,
\quad A_{uh}=\overline{y-\widehat m(d)}_{uh}-\overline{y-\widehat m(d)}_D,
\quad \boxed{T=K+A}.
\]

`d` consists of recorded subreddit/time context in the primary arm; the
format-enriched arm adds visible length/format opportunity.  Reddit selection
is explicitly retained as an observed author-conditioned process rather than
subtracted as nuisance.

## Design

- Fresh selected authors: `600` after excluding E0/E1 cohorts.
- Declared source panel: exactly `48` chronologically spaced comments per author, then alternating source-disjoint A/B halves.
- Split counts: discovery `379`, calibration `112`, confirmation `109`.
- Representation, context vocabulary, length deciles and surfaces: discovery only. Ridge alpha: calibration only. Confirmation: evaluation only.
- External labels / Big Five / MBTI / clinical values: `not read`.
- Raw text, subreddit names, and author IDs: `not exported`.

## Calibration selection

|   ridge_alpha |   calibration_context_r2 | operator        | arm             |
|--------------:|-------------------------:|:----------------|:----------------|
|         0.100 |                    0.007 | native          | primary         |
|         1.000 |                    0.007 | native          | primary         |
|        10.000 |                    0.007 | native          | primary         |
|       100.000 |                    0.007 | native          | primary         |
|         0.100 |                    0.153 | native          | format_enriched |
|         1.000 |                    0.153 | native          | format_enriched |
|        10.000 |                    0.153 | native          | format_enriched |
|       100.000 |                    0.153 | native          | format_enriched |
|         0.100 |                    0.002 | fixed_128_cross | primary         |
|         1.000 |                    0.002 | fixed_128_cross | primary         |
|        10.000 |                    0.002 | fixed_128_cross | primary         |
|       100.000 |                    0.003 | fixed_128_cross | primary         |
|         0.100 |                    0.059 | fixed_128_cross | format_enriched |
|         1.000 |                    0.059 | fixed_128_cross | format_enriched |
|        10.000 |                    0.059 | fixed_128_cross | format_enriched |
|       100.000 |                    0.058 | fixed_128_cross | format_enriched |

## Condition-surface and selection metrics

`context_r2` is comment-level confirmation R2 from the frozen surface; its
permutation breaks context-to-text pairing within year-quarter/length-decile
strata. `selection_logscore_gain` compares each author's A-half subreddit
profile predicting B against the discovery population profile, symmetrized
over A/B. `K_to_T_r2` maps context-carried A-half structure to total B-half
structure. Only the native/primary row licenses the decision below; other rows
are sensitivity descriptions and cannot rescue a failed primary test.

| operator        | arm             |   ridge_alpha |   n_discovery_units |   n_calibration_units |   n_confirmation_units |   context_r2 |   context_r2_ci_low |   context_r2_ci_high |   context_permutation_p | artifact_sha256                                                  |   author_map_ridge_alpha |   k_to_t_r2 |   k_to_t_ci_low |   k_to_t_ci_high |   k_to_t_permutation_p |   n_train |   n_confirmation |   selection_logscore_gain |   selection_logscore_ci_low |   selection_logscore_ci_high |   selection_permutation_p |   selection_shrinkage |   n_confirmation_authors |
|:----------------|:----------------|--------------:|--------------------:|----------------------:|-----------------------:|-------------:|--------------------:|---------------------:|------------------------:|:-----------------------------------------------------------------|-------------------------:|------------:|----------------:|-----------------:|-----------------------:|----------:|-----------------:|--------------------------:|----------------------------:|-----------------------------:|--------------------------:|----------------------:|-------------------------:|
| native          | primary         |       100.000 |           18192.000 |              5376.000 |               5232.000 |        0.005 |               0.000 |                0.008 |                   0.001 | abfb19e6a50cfd0260470387ebf2de52510904a4d176f5fb71093158cd05a85d |                    0.100 |       0.021 |          -0.014 |            0.034 |                  0.001 |   379.000 |          109.000 |                   nan     |                     nan     |                      nan     |                   nan     |               nan     |                  nan     |
| native          | format_enriched |        10.000 |           18192.000 |              5376.000 |               5232.000 |        0.159 |             nan     |              nan     |                 nan     | 3e754ab7491a43b4013f02fdfd56902253e6d62e7c38333e27f55a86239f39e2 |                  nan     |     nan     |         nan     |          nan     |                nan     |   nan     |          nan     |                   nan     |                     nan     |                      nan     |                   nan     |               nan     |                  nan     |
| fixed_128_cross | primary         |       100.000 |            8299.000 |              2588.000 |               2659.000 |        0.003 |             nan     |              nan     |                 nan     | 0c06f5970232cfb1c9e598bb459a8da922b4cd53efc15d4306df9d2448676d74 |                  nan     |     nan     |         nan     |          nan     |                nan     |   nan     |          nan     |                   nan     |                     nan     |                      nan     |                   nan     |               nan     |                  nan     |
| fixed_128_cross | format_enriched |        10.000 |            8299.000 |              2588.000 |               2659.000 |        0.076 |             nan     |              nan     |                 nan     | 520aeba63b7f8b1e36bedf4b2d7132623e5d1a07898509a0ca2f2ad3658fd5a3 |                  nan     |     nan     |         nan     |          nan     |                nan     |   nan     |          nan     |                   nan     |                     nan     |                      nan     |                   nan     |               nan     |                  nan     |
| native          | primary         |       nan     |             nan     |               nan     |                nan     |      nan     |             nan     |              nan     |                 nan     | nan                                                              |                  nan     |     nan     |         nan     |          nan     |                nan     |   nan     |          nan     |                     0.894 |                       0.741 |                        1.042 |                     0.001 |                 5.000 |                  109.000 |

## Non-orthogonal variance accounting

The traces obey
\[
\operatorname{tr}\Sigma_T=
\operatorname{tr}\Sigma_K+
\operatorname{tr}\Sigma_A+2\operatorname{tr}\Sigma_{KA}.
\]
`trace_K / trace_T` is intentionally not reported as standalone “variance
explained”: the covariance term can be positive or negative.

|   trace_T |   trace_K |   trace_A |   trace_KA |   identity_trace_error |   max_identity_error | operator        | arm             | half   | split        |   n_authors |
|----------:|----------:|----------:|-----------:|-----------------------:|---------------------:|:----------------|:----------------|:-------|:-------------|------------:|
|     0.005 |     0.000 |     0.004 |      0.000 |                  0.000 |                0.000 | native          | primary         | left   | discovery    |         379 |
|     0.005 |     0.000 |     0.005 |      0.000 |                 -0.000 |                0.000 | native          | primary         | left   | calibration  |         112 |
|     0.006 |     0.000 |     0.005 |      0.000 |                  0.000 |                0.000 | native          | primary         | left   | confirmation |         109 |
|     0.005 |     0.002 |     0.003 |      0.000 |                  0.000 |                0.000 | native          | format_enriched | left   | discovery    |         379 |
|     0.005 |     0.001 |     0.004 |      0.000 |                  0.000 |                0.000 | native          | format_enriched | left   | calibration  |         112 |
|     0.006 |     0.002 |     0.004 |      0.000 |                 -0.000 |                0.000 | native          | format_enriched | left   | confirmation |         109 |
|     0.010 |     0.001 |     0.008 |      0.000 |                 -0.000 |                0.000 | fixed_128_cross | primary         | left   | discovery    |         379 |
|     0.009 |     0.001 |     0.008 |     -0.000 |                  0.000 |                0.000 | fixed_128_cross | primary         | left   | calibration  |         112 |
|     0.009 |     0.001 |     0.009 |     -0.000 |                 -0.000 |                0.000 | fixed_128_cross | primary         | left   | confirmation |         109 |
|     0.010 |     0.002 |     0.007 |      0.000 |                 -0.000 |                0.000 | fixed_128_cross | format_enriched | left   | discovery    |         379 |
|     0.009 |     0.002 |     0.008 |     -0.000 |                 -0.000 |                0.000 | fixed_128_cross | format_enriched | left   | calibration  |         112 |
|     0.009 |     0.002 |     0.007 |     -0.000 |                 -0.000 |                0.000 | fixed_128_cross | format_enriched | left   | confirmation |         109 |

## Source-disjoint component retrieval

Each AUC asks whether A-side component vectors are closer to their own B-side
vector than to sampled B-side strangers. These are author-alignment metrics,
not personality validity coefficients.

|     auc |   auc_ci_low |   auc_ci_high |   permutation_p |   n_authors | operator        | arm             | component   | split        |
|--------:|-------------:|--------------:|----------------:|------------:|:----------------|:----------------|:------------|:-------------|
| nan     |      nan     |       nan     |         nan     |         379 | native          | primary         | T           | discovery    |
| nan     |      nan     |       nan     |         nan     |         379 | native          | primary         | K           | discovery    |
| nan     |      nan     |       nan     |         nan     |         379 | native          | primary         | A           | discovery    |
| nan     |      nan     |       nan     |         nan     |         112 | native          | primary         | T           | calibration  |
| nan     |      nan     |       nan     |         nan     |         112 | native          | primary         | K           | calibration  |
| nan     |      nan     |       nan     |         nan     |         112 | native          | primary         | A           | calibration  |
|   0.916 |        0.890 |         0.938 |           0.001 |         109 | native          | primary         | T           | confirmation |
|   0.926 |        0.904 |         0.946 |           0.001 |         109 | native          | primary         | K           | confirmation |
|   0.891 |        0.862 |         0.917 |           0.001 |         109 | native          | primary         | A           | confirmation |
| nan     |      nan     |       nan     |         nan     |         379 | native          | format_enriched | T           | discovery    |
| nan     |      nan     |       nan     |         nan     |         379 | native          | format_enriched | K           | discovery    |
| nan     |      nan     |       nan     |         nan     |         379 | native          | format_enriched | A           | discovery    |
| nan     |      nan     |       nan     |         nan     |         112 | native          | format_enriched | T           | calibration  |
| nan     |      nan     |       nan     |         nan     |         112 | native          | format_enriched | K           | calibration  |
| nan     |      nan     |       nan     |         nan     |         112 | native          | format_enriched | A           | calibration  |
|   0.913 |        0.888 |         0.936 |           0.001 |         109 | native          | format_enriched | T           | confirmation |
|   0.871 |        0.836 |         0.904 |           0.001 |         109 | native          | format_enriched | K           | confirmation |
|   0.872 |        0.840 |         0.901 |           0.001 |         109 | native          | format_enriched | A           | confirmation |
| nan     |      nan     |       nan     |         nan     |         379 | fixed_128_cross | primary         | T           | discovery    |
| nan     |      nan     |       nan     |         nan     |         379 | fixed_128_cross | primary         | K           | discovery    |
| nan     |      nan     |       nan     |         nan     |         379 | fixed_128_cross | primary         | A           | discovery    |
| nan     |      nan     |       nan     |         nan     |         112 | fixed_128_cross | primary         | T           | calibration  |
| nan     |      nan     |       nan     |         nan     |         112 | fixed_128_cross | primary         | K           | calibration  |
| nan     |      nan     |       nan     |         nan     |         112 | fixed_128_cross | primary         | A           | calibration  |
|   0.848 |        0.813 |         0.882 |           0.001 |         109 | fixed_128_cross | primary         | T           | confirmation |
|   0.858 |        0.829 |         0.884 |           0.001 |         109 | fixed_128_cross | primary         | K           | confirmation |
|   0.820 |        0.783 |         0.855 |           0.001 |         109 | fixed_128_cross | primary         | A           | confirmation |
| nan     |      nan     |       nan     |         nan     |         379 | fixed_128_cross | format_enriched | T           | discovery    |
| nan     |      nan     |       nan     |         nan     |         379 | fixed_128_cross | format_enriched | K           | discovery    |
| nan     |      nan     |       nan     |         nan     |         379 | fixed_128_cross | format_enriched | A           | discovery    |
| nan     |      nan     |       nan     |         nan     |         112 | fixed_128_cross | format_enriched | T           | calibration  |
| nan     |      nan     |       nan     |         nan     |         112 | fixed_128_cross | format_enriched | K           | calibration  |
| nan     |      nan     |       nan     |         nan     |         112 | fixed_128_cross | format_enriched | A           | calibration  |
|   0.842 |        0.806 |         0.875 |           0.001 |         109 | fixed_128_cross | format_enriched | T           | confirmation |
|   0.843 |        0.801 |         0.883 |           0.001 |         109 | fixed_128_cross | format_enriched | K           | confirmation |
|   0.798 |        0.757 |         0.835 |           0.001 |         109 | fixed_128_cross | format_enriched | A           | confirmation |

## Matched partial screen (native primary only)

The partial screen is deliberately not a generic A/B retrieval test. First,
source-disjoint A/B comment pairs are restricted by the registered exact
condition/time support rule.  On calibration authors only, we select the first
registered pair of condition-overlap and numeric calipers that reaches the
coverage gate.  Numeric distance is computed from the frozen paired selection
profile, frozen context-carried configuration `K`, matched comment count,
matched time span, and matched token count. Exact fields are operator,
representation, source arm, language, and the registered support class.

Confirmation authors are packed into disjoint 4--8-author strata only when
every within-stratum pair satisfies the frozen calipers. The observed statistic
compares each author's A residual to its linked B residual against the other B
residuals *within its own stratum*. Its null permutes B identities independently
within each frozen stratum and recomputes the same rank statistic. This makes
the null conditionally exchangeable under the declared matching surface; it is
not an unrestricted author derangement or an iid candidate-pool draw.

If the selected Jaccard caliper is zero, the result is conditional on the
numeric matching coordinates but does **not** establish literal matched-topic
or matched-subreddit equivalence. That limitation is recorded rather than
silently converted into a fixed-condition claim.

| operator   | arm     | status                    |   caliper_days |   calibration_coverage |   confirmation_coverage |   stratum_coverage | matched_null_method                      | matched_null_exchangeable   | matching_surface                           |   n_strata |   stratum_size_min |   stratum_size_median |   stratum_size_max |   numeric_caliper |   minimum_jaccard |   calibration_pair_coverage |   confirmation_pair_coverage |   confirmation_stratum_coverage |   auc |   auc_ci_low |   auc_ci_high |   permutation_p |   n_authors |
|:-----------|:--------|:--------------------------|---------------:|-----------------------:|------------------------:|-------------------:|:-----------------------------------------|:----------------------------|:-------------------------------------------|-----------:|-------------------:|----------------------:|-------------------:|------------------:|------------------:|----------------------------:|-----------------------------:|--------------------------------:|------:|-------------:|--------------:|----------------:|------------:|
| native     | primary | MATCHED_PARTIAL_EVALUATED |        365.000 |                  0.768 |                   0.798 |              0.789 | within_stratum_identity_permutation_rank | True                        | paired_A_B_metadata_plus_condition_jaccard |         11 |                  6 |                 8.000 |                  8 |             4.000 |             0.000 |                       0.768 |                        0.798 |                           0.789 | 0.834 |        0.766 |         0.896 |           0.001 |          86 |

## Registered primary-native summary

```json
{
  "context_r2": 0.004509342037292474,
  "context_r2_ci_high": 0.007676109431572189,
  "context_r2_ci_low": 0.00024287318619267147,
  "context_r2_p": 0.001,
  "context_r2_q": 0.005,
  "k_to_t_ci_high": 0.03389010033730968,
  "k_to_t_ci_low": -0.014448125322490962,
  "k_to_t_permutation_p": 0.001,
  "k_to_t_q": 0.005,
  "k_to_t_r2": 0.02091907140983129,
  "n_confirmation": 109,
  "n_train": 379,
  "partial_auc": 0.8342192691029899,
  "partial_auc_ci_high": 0.895691633947448,
  "partial_auc_ci_low": 0.7662307459981876,
  "partial_auc_p": 0.001,
  "partial_auc_q": 0.005,
  "partial_null_exchangeable": true,
  "selection_gain": 0.8939960926606118,
  "selection_gain_ci_high": 1.0421082534286958,
  "selection_gain_ci_low": 0.7412935901945233,
  "selection_gain_p": 0.001,
  "selection_gain_q": 0.005,
  "total_auc": 0.9158656678730748,
  "total_auc_ci_high": 0.9384153269926773,
  "total_auc_ci_low": 0.8900743834694049,
  "total_auc_p": 0.001,
  "total_auc_q": 0.005
}
```

**TOTAL_SELECTION_AND_PARTIAL_STRUCTURE_SUPPORTED_WITH_UNRESOLVED_CONTEXT_TRANSPORT** — Total alignment, observed-selection recurrence, and matched partial structure pass. The recorded primary condition surface and/or its K-to-T transport does not meet the material lower-confidence-bound rule, so condition accounting remains unresolved.

## Claim boundary

E2 may establish observed-selection recurrence, held-out context predictability,
exact algebraic component accounting, and survival/collapse under a declared
matched partial screen. It does **not** identify exposure opportunity, causal
context effects, a fixed-condition response operator, temporal personality,
external validity, a clinical score, or a human psychological construct.

## Artifacts

- `results/v7_condition_opportunity/e2_full_20260715_r7/run_manifest.json`
- `results/v7_condition_opportunity/e2_full_20260715_r7/condition_model_metrics.csv`
- `results/v7_condition_opportunity/e2_full_20260715_r7/author_map_selection.csv`
- `results/v7_condition_opportunity/e2_full_20260715_r7/selection_profile_selection.csv`
- `results/v7_condition_opportunity/e2_full_20260715_r7/selection_metrics.csv`
- `results/v7_condition_opportunity/e2_full_20260715_r7/variance_accounting.csv`
- `results/v7_condition_opportunity/e2_full_20260715_r7/component_retrieval_metrics.csv`
- `results/v7_condition_opportunity/e2_full_20260715_r7/matched_partial_metrics.csv`
- `results/v7_condition_opportunity/e2_full_20260715_r7/matched_caliper_selection.csv`
- `results/v7_condition_opportunity/e2_full_20260715_r7/matched_strata.csv`
- `results/v7_condition_opportunity/e2_full_20260715_r7/matching_balance.csv`
- `results/v7_condition_opportunity/e2_full_20260715_r7/matched_partial_null.parquet` (or CSV fallback)
- `results/v7_condition_opportunity/e2_full_20260715_r7/permutation_null.csv`
