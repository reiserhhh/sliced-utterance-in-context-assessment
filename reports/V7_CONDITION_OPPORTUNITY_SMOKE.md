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

- Fresh selected authors: `120` after excluding E0/E1 cohorts.
- Declared source panel: exactly `24` chronologically spaced comments per author, then alternating source-disjoint A/B halves.
- Split counts: discovery `81`, calibration `17`, confirmation `22`.
- Representation, context vocabulary, length deciles and surfaces: discovery only. Ridge alpha: calibration only. Confirmation: evaluation only.
- External labels / Big Five / MBTI / clinical values: `not read`.
- Raw text, subreddit names, and author IDs: `not exported`.

## Calibration selection

|   ridge_alpha |   calibration_context_r2 | operator        | arm             |
|--------------:|-------------------------:|:----------------|:----------------|
|         0.100 |                   -0.031 | native          | primary         |
|         1.000 |                   -0.031 | native          | primary         |
|        10.000 |                   -0.031 | native          | primary         |
|       100.000 |                   -0.028 | native          | primary         |
|         0.100 |                    0.137 | native          | format_enriched |
|         1.000 |                    0.137 | native          | format_enriched |
|        10.000 |                    0.137 | native          | format_enriched |
|       100.000 |                    0.139 | native          | format_enriched |
|         0.100 |                   -0.051 | fixed_128_cross | primary         |
|         1.000 |                   -0.051 | fixed_128_cross | primary         |
|        10.000 |                   -0.049 | fixed_128_cross | primary         |
|       100.000 |                   -0.037 | fixed_128_cross | primary         |
|         0.100 |                   -0.028 | fixed_128_cross | format_enriched |
|         1.000 |                   -0.028 | fixed_128_cross | format_enriched |
|        10.000 |                   -0.028 | fixed_128_cross | format_enriched |
|       100.000 |                   -0.008 | fixed_128_cross | format_enriched |

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
| native          | primary         |       100.000 |            1944.000 |               408.000 |                528.000 |       -0.053 |              -0.086 |               -0.035 |                   0.040 | 4374b4918ed803dc09ba28a78320b1f3c616b812c15eb0e760c8b6071287e1b0 |                    0.100 |      -0.069 |          -0.216 |           -0.066 |                  0.020 |    81.000 |           22.000 |                   nan     |                     nan     |                      nan     |                   nan     |               nan     |                  nan     |
| native          | format_enriched |       100.000 |            1944.000 |               408.000 |                528.000 |        0.099 |             nan     |              nan     |                 nan     | fec689981bd3ef52437b565b1843eb1f22df22f27b82ce5c82ac935adde51744 |                  nan     |     nan     |         nan     |          nan     |                nan     |   nan     |          nan     |                   nan     |                     nan     |                      nan     |                   nan     |               nan     |                  nan     |
| fixed_128_cross | primary         |       100.000 |             930.000 |               199.000 |                245.000 |       -0.192 |             nan     |              nan     |                 nan     | 66ba3f01e4681ae2de9193b783bbc169586fef457f0ee56769a72a0e834b30a3 |                  nan     |     nan     |         nan     |          nan     |                nan     |   nan     |          nan     |                   nan     |                     nan     |                      nan     |                   nan     |               nan     |                  nan     |
| fixed_128_cross | format_enriched |       100.000 |             930.000 |               199.000 |                245.000 |       -0.145 |             nan     |              nan     |                 nan     | 83f722d5984737d7843aa39c59743c084ad325da45eb9af1f917fe3107e03826 |                  nan     |     nan     |         nan     |          nan     |                nan     |   nan     |          nan     |                   nan     |                     nan     |                      nan     |                   nan     |               nan     |                  nan     |
| native          | primary         |       nan     |             nan     |               nan     |                nan     |      nan     |             nan     |              nan     |                 nan     | nan                                                              |                  nan     |     nan     |         nan     |          nan     |                nan     |   nan     |          nan     |                     0.870 |                       0.604 |                        1.128 |                     0.010 |                 5.000 |                   22.000 |

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
|     0.012 |     0.002 |     0.008 |      0.001 |                 -0.000 |                0.000 | native          | primary         | left   | discovery    |          81 |
|     0.010 |     0.001 |     0.010 |     -0.000 |                  0.000 |                0.000 | native          | primary         | left   | calibration  |          17 |
|     0.012 |     0.001 |     0.012 |     -0.001 |                 -0.000 |                0.000 | native          | primary         | left   | confirmation |          22 |
|     0.012 |     0.004 |     0.006 |      0.000 |                 -0.000 |                0.000 | native          | format_enriched | left   | discovery    |          81 |
|     0.010 |     0.003 |     0.008 |      0.000 |                  0.000 |                0.000 | native          | format_enriched | left   | calibration  |          17 |
|     0.012 |     0.004 |     0.009 |     -0.000 |                 -0.000 |                0.000 | native          | format_enriched | left   | confirmation |          22 |
|     0.022 |     0.006 |     0.013 |      0.001 |                  0.000 |                0.000 | fixed_128_cross | primary         | left   | discovery    |          81 |
|     0.020 |     0.002 |     0.021 |     -0.001 |                  0.000 |                0.000 | fixed_128_cross | primary         | left   | calibration  |          17 |
|     0.020 |     0.005 |     0.025 |     -0.005 |                  0.000 |                0.000 | fixed_128_cross | primary         | left   | confirmation |          22 |
|     0.022 |     0.007 |     0.012 |      0.001 |                  0.000 |                0.000 | fixed_128_cross | format_enriched | left   | discovery    |          81 |
|     0.020 |     0.003 |     0.019 |     -0.001 |                  0.000 |                0.000 | fixed_128_cross | format_enriched | left   | calibration  |          17 |
|     0.020 |     0.006 |     0.024 |     -0.004 |                  0.000 |                0.000 | fixed_128_cross | format_enriched | left   | confirmation |          22 |

## Source-disjoint component retrieval

Each AUC asks whether A-side component vectors are closer to their own B-side
vector than to sampled B-side strangers. These are author-alignment metrics,
not personality validity coefficients.

|     auc |   auc_ci_low |   auc_ci_high |   permutation_p |   n_authors | operator        | arm             | component   | split        |
|--------:|-------------:|--------------:|----------------:|------------:|:----------------|:----------------|:------------|:-------------|
| nan     |      nan     |       nan     |         nan     |          81 | native          | primary         | T           | discovery    |
| nan     |      nan     |       nan     |         nan     |          81 | native          | primary         | K           | discovery    |
| nan     |      nan     |       nan     |         nan     |          81 | native          | primary         | A           | discovery    |
| nan     |      nan     |       nan     |         nan     |          17 | native          | primary         | T           | calibration  |
| nan     |      nan     |       nan     |         nan     |          17 | native          | primary         | K           | calibration  |
| nan     |      nan     |       nan     |         nan     |          17 | native          | primary         | A           | calibration  |
|   0.756 |        0.623 |         0.846 |           0.010 |          22 | native          | primary         | T           | confirmation |
|   0.868 |        0.813 |         0.925 |           0.010 |          22 | native          | primary         | K           | confirmation |
|   0.756 |        0.659 |         0.862 |           0.010 |          22 | native          | primary         | A           | confirmation |
| nan     |      nan     |       nan     |         nan     |          81 | native          | format_enriched | T           | discovery    |
| nan     |      nan     |       nan     |         nan     |          81 | native          | format_enriched | K           | discovery    |
| nan     |      nan     |       nan     |         nan     |          81 | native          | format_enriched | A           | discovery    |
| nan     |      nan     |       nan     |         nan     |          17 | native          | format_enriched | T           | calibration  |
| nan     |      nan     |       nan     |         nan     |          17 | native          | format_enriched | K           | calibration  |
| nan     |      nan     |       nan     |         nan     |          17 | native          | format_enriched | A           | calibration  |
|   0.764 |        0.634 |         0.856 |           0.010 |          22 | native          | format_enriched | T           | confirmation |
|   0.828 |        0.718 |         0.912 |           0.010 |          22 | native          | format_enriched | K           | confirmation |
|   0.756 |        0.661 |         0.856 |           0.010 |          22 | native          | format_enriched | A           | confirmation |
| nan     |      nan     |       nan     |         nan     |          81 | fixed_128_cross | primary         | T           | discovery    |
| nan     |      nan     |       nan     |         nan     |          81 | fixed_128_cross | primary         | K           | discovery    |
| nan     |      nan     |       nan     |         nan     |          81 | fixed_128_cross | primary         | A           | discovery    |
| nan     |      nan     |       nan     |         nan     |          17 | fixed_128_cross | primary         | T           | calibration  |
| nan     |      nan     |       nan     |         nan     |          17 | fixed_128_cross | primary         | K           | calibration  |
| nan     |      nan     |       nan     |         nan     |          17 | fixed_128_cross | primary         | A           | calibration  |
|   0.724 |        0.641 |         0.815 |           0.010 |          22 | fixed_128_cross | primary         | T           | confirmation |
|   0.734 |        0.632 |         0.811 |           0.010 |          22 | fixed_128_cross | primary         | K           | confirmation |
|   0.696 |        0.610 |         0.780 |           0.010 |          22 | fixed_128_cross | primary         | A           | confirmation |
| nan     |      nan     |       nan     |         nan     |          81 | fixed_128_cross | format_enriched | T           | discovery    |
| nan     |      nan     |       nan     |         nan     |          81 | fixed_128_cross | format_enriched | K           | discovery    |
| nan     |      nan     |       nan     |         nan     |          81 | fixed_128_cross | format_enriched | A           | discovery    |
| nan     |      nan     |       nan     |         nan     |          17 | fixed_128_cross | format_enriched | T           | calibration  |
| nan     |      nan     |       nan     |         nan     |          17 | fixed_128_cross | format_enriched | K           | calibration  |
| nan     |      nan     |       nan     |         nan     |          17 | fixed_128_cross | format_enriched | A           | calibration  |
|   0.709 |        0.630 |         0.789 |           0.010 |          22 | fixed_128_cross | format_enriched | T           | confirmation |
|   0.767 |        0.663 |         0.855 |           0.010 |          22 | fixed_128_cross | format_enriched | K           | confirmation |
|   0.715 |        0.649 |         0.797 |           0.010 |          22 | fixed_128_cross | format_enriched | A           | confirmation |

## Exact-condition matched partial screen (native primary only)

Calibration chooses the smallest time caliper that retains enough authors with
at least 8 exact-subreddit A/B pairs over at least 3 subreddits.  Confirmation
residual vectors are then contrasted with B strangers from an A-to-B candidate
pool matched on recorded selection profile, context-carried K, span, and
subreddit overlap.  The partial-screen null draws one pseudo-own and all
pseudo-strangers iid from that *same* frozen row-wise candidate distribution;
it is therefore conditional on the declared matching variables rather than an
unrestricted author derangement.

| operator   | arm     | status                              |   calibration_coverage |   confirmation_coverage |
|:-----------|:--------|:------------------------------------|-----------------------:|------------------------:|
| native     | primary | REFUSE_INSUFFICIENT_MATCHED_SUPPORT |                  0.000 |                     nan |

## Registered primary-native summary

```json
{
  "context_r2": -0.05295270460572388,
  "context_r2_ci_high": -0.03534273720870658,
  "context_r2_ci_low": -0.08576456247063033,
  "context_r2_p": 0.04,
  "context_r2_q": 0.08,
  "k_to_t_ci_high": -0.06636499228879592,
  "k_to_t_ci_low": -0.21598796114859914,
  "k_to_t_permutation_p": 0.02,
  "k_to_t_q": 0.06,
  "k_to_t_r2": -0.0690630153752021,
  "n_confirmation": 22,
  "n_train": 81,
  "partial_auc": NaN,
  "partial_auc_ci_high": NaN,
  "partial_auc_ci_low": NaN,
  "partial_auc_p": 1.0,
  "partial_auc_q": 1.0,
  "partial_null_exchangeable": false,
  "selection_gain": 0.8699820500522469,
  "selection_gain_ci_high": 1.1283713810766351,
  "selection_gain_ci_low": 0.6037954424889722,
  "selection_gain_p": 0.01,
  "selection_gain_q": 0.05,
  "total_auc": 0.756095041322314,
  "total_auc_ci_high": 0.846482438016529,
  "total_auc_ci_low": 0.6232128099173554,
  "total_auc_p": 0.01,
  "total_auc_q": 0.05
}
```

**REFUSE_INSUFFICIENT_MATCHED_SUPPORT** — The calibration-selected exact-subreddit time caliper did not retain enough confirmation authors for E2-B.

## Claim boundary

E2 may establish observed-selection recurrence, held-out context predictability,
exact algebraic component accounting, and survival/collapse under a declared
matched partial screen. It does **not** identify exposure opportunity, causal
context effects, a fixed-condition response operator, temporal personality,
external validity, a clinical score, or a human psychological construct.

## Artifacts

- `results/v7_condition_opportunity/e2_stratified_quick_20260715/run_manifest.json`
- `results/v7_condition_opportunity/e2_stratified_quick_20260715/condition_model_metrics.csv`
- `results/v7_condition_opportunity/e2_stratified_quick_20260715/author_map_selection.csv`
- `results/v7_condition_opportunity/e2_stratified_quick_20260715/selection_profile_selection.csv`
- `results/v7_condition_opportunity/e2_stratified_quick_20260715/selection_metrics.csv`
- `results/v7_condition_opportunity/e2_stratified_quick_20260715/variance_accounting.csv`
- `results/v7_condition_opportunity/e2_stratified_quick_20260715/component_retrieval_metrics.csv`
- `results/v7_condition_opportunity/e2_stratified_quick_20260715/matched_partial_metrics.csv`
- `results/v7_condition_opportunity/e2_stratified_quick_20260715/permutation_null.csv`
