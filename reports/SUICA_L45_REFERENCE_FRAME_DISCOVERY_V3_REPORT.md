# SUICA L4-to-L5 Reference-Frame Discovery

Decision: `L45_OPENED_DISCOVERY_CANDIDATE`

## Question

Can an anonymous facet-indexed technical vector become a comparable
reference-relative measurement candidate when the reference population,
target facet measure, chart/operator, support rule, occasion universe, and
uncertainty procedure are frozen?

## Design

- Reference, calibration, and scored panels are generated independently.
- Scores standardize event composition to a frozen facet measure before
  applying a frozen population chart.
- Stable-subspace selection uses calibration occasions only.
- Confidence regions jointly resample reference authors, calibration authors,
  within-author occasions, and observed event means; planted truth is accessed
  only after each region is frozen.
- Ten synthetic worlds include heavy tails, support holes, reference-mixture
  shift, A/Q gauge aliases, choice/response aliases, person/occasion aliases,
  correlated repeat shocks, operator kernels, and informative precision.

## Gates

- PASS: `clean_score_recovery`
- PASS: `clean_normalized_error`
- PASS: `composition_standardization`
- PASS: `reference_mixture_correction`
- PASS: `truth_isolation`
- PASS: `required_refusals`
- PASS: `aq_gauge_alias`
- PASS: `operator_transport`
- PASS: `observable_uncertainty`
- PASS: `mdd_false_positive`
- PASS: `mdd_power`

## Selected summaries

| world                 | noise_mode         | metric                           |   mean |   lower95 |   upper95 |   n |
|:----------------------|:-------------------|:---------------------------------|-------:|----------:|----------:|----:|
| clean                 | gaussian           | score_correlation                | 0.9879 |    0.9876 |    0.9882 |  30 |
| clean                 | gaussian           | normalized_score_error           | 0.1573 |    0.1556 |    0.1591 |  30 |
| clean                 | gaussian           | mdd_null_false_positive          | 0.0802 |    0.0604 |    0.1021 |  30 |
| clean                 | gaussian           | mdd_two_mdd_power                | 1.0000 |    1.0000 |    1.0000 |  30 |
| clean                 | gaussian           | uncertainty_coverage             | 0.9563 |    0.9375 |    0.9750 |  10 |
| clean                 | gaussian           | uncertainty_successful_draw_rate | 1.0000 |    1.0000 |    1.0000 |  10 |
| clean                 | heteroskedastic_t5 | score_correlation                | 0.9878 |    0.9876 |    0.9881 |  30 |
| clean                 | heteroskedastic_t5 | normalized_score_error           | 0.1576 |    0.1560 |    0.1592 |  30 |
| clean                 | heteroskedastic_t5 | mdd_null_false_positive          | 0.0854 |    0.0604 |    0.1125 |  30 |
| clean                 | heteroskedastic_t5 | mdd_two_mdd_power                | 1.0000 |    1.0000 |    1.0000 |  30 |
| clean                 | heteroskedastic_t5 | uncertainty_coverage             | 0.9563 |    0.9250 |    0.9875 |  10 |
| clean                 | heteroskedastic_t5 | uncertainty_successful_draw_rate | 1.0000 |    1.0000 |    1.0000 |  10 |
| composition_shift     | gaussian           | composition_correction_gain      | 0.2488 |    0.2264 |    0.2714 |  30 |
| composition_shift     | heteroskedastic_t5 | composition_correction_gain      | 0.2457 |    0.2247 |    0.2667 |  30 |
| informative_precision | gaussian           | uncertainty_coverage             | 0.9563 |    0.9250 |    0.9875 |  10 |
| informative_precision | gaussian           | uncertainty_successful_draw_rate | 1.0000 |    1.0000 |    1.0000 |  10 |
| informative_precision | heteroskedastic_t5 | uncertainty_coverage             | 0.9875 |    0.9688 |    1.0000 |  10 |
| informative_precision | heteroskedastic_t5 | uncertainty_successful_draw_rate | 1.0000 |    1.0000 |    1.0000 |  10 |
| reference_mixture     | gaussian           | reference_correction_gain        | 0.6971 |    0.6616 |    0.7309 |  30 |
| reference_mixture     | heteroskedastic_t5 | reference_correction_gain        | 0.6908 |    0.6449 |    0.7300 |  30 |

## Refusal rates

```json
{
  "support_hole": 1.0,
  "choice_response_alias": 1.0,
  "person_occasion_alias": 1.0,
  "correlated_replicate_shock": 1.0,
  "operator_kernel": 1.0
}
```

## Extrema

```json
{
  "minimum_clean_score_correlation_lower": 0.9875655428884242,
  "maximum_clean_normalized_error_upper": 0.15924637598358563,
  "minimum_composition_gain_lower": 0.22469034916127695,
  "minimum_reference_gain_lower": 0.6449288073732788,
  "maximum_truth_isolation_error": 0.0,
  "maximum_alias_identity_error": 0.0,
  "maximum_valid_operator_defect": 7.825215271862575e-16,
  "minimum_uncertainty_coverage_lower": 0.925,
  "maximum_uncertainty_coverage_mean": 0.9875,
  "minimum_uncertainty_success_rate": 1.0,
  "maximum_clean_mdd_false_positive_upper": 0.1125,
  "minimum_clean_two_mdd_power_lower": 1.0
}
```

## Interpretation

Passing this opened discovery battery would show only that a declared
reference-frame construction can recover a planted technical score and refuse
registered nonidentified worlds. It would not establish an L5 score on human
text, a psychological construct, a personality trait, or an application.
Formal promotion requires a separately sealed fresh-seed confirmation and a
real study-specific generalizability design.

## Claim boundary

Opened synthetic discovery of the E45 reference-scoring edge only. V1 failed because occasion uncertainty was omitted; V2 repaired it; V3 uses group-specific coverage bounds. Maximum licensed layer remains L4 pending sealed confirmation and a real study-specific G/D design.
