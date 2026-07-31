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
  and observed event means; planted truth is accessed only after each region
  is frozen.
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

| world                      | noise_mode         | metric                           |     mean |   lower95 |   upper95 |   n |
|:---------------------------|:-------------------|:---------------------------------|---------:|----------:|----------:|----:|
| aq_gauge_alias             | gaussian           | score_correlation                |   0.9861 |    0.9850 |    0.9873 |   2 |
| aq_gauge_alias             | gaussian           | normalized_score_error           |   0.1705 |    0.1630 |    0.1780 |   2 |
| aq_gauge_alias             | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |   2 |
| aq_gauge_alias             | gaussian           | reference_correction_gain        |  -0.0000 |   -0.0000 |    0.0000 |   2 |
| aq_gauge_alias             | gaussian           | mdd_null_false_positive          |   0.0625 |    0.0625 |    0.0625 |   2 |
| aq_gauge_alias             | gaussian           | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |   2 |
| aq_gauge_alias             | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| aq_gauge_alias             | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| aq_gauge_alias             | heteroskedastic_t5 | score_correlation                |   0.9857 |    0.9850 |    0.9864 |   2 |
| aq_gauge_alias             | heteroskedastic_t5 | normalized_score_error           |   0.1719 |    0.1670 |    0.1769 |   2 |
| aq_gauge_alias             | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |   2 |
| aq_gauge_alias             | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |   -0.0000 |    0.0000 |   2 |
| aq_gauge_alias             | heteroskedastic_t5 | mdd_null_false_positive          |   0.0625 |    0.0000 |    0.1250 |   2 |
| aq_gauge_alias             | heteroskedastic_t5 | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |   2 |
| aq_gauge_alias             | heteroskedastic_t5 | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| aq_gauge_alias             | heteroskedastic_t5 | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| choice_response_alias      | gaussian           | score_correlation                | nan      |  nan      |  nan      |   0 |
| choice_response_alias      | gaussian           | normalized_score_error           | nan      |  nan      |  nan      |   0 |
| choice_response_alias      | gaussian           | composition_correction_gain      | nan      |  nan      |  nan      |   0 |
| choice_response_alias      | gaussian           | reference_correction_gain        | nan      |  nan      |  nan      |   0 |
| choice_response_alias      | gaussian           | mdd_null_false_positive          | nan      |  nan      |  nan      |   0 |
| choice_response_alias      | gaussian           | mdd_two_mdd_power                | nan      |  nan      |  nan      |   0 |
| choice_response_alias      | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| choice_response_alias      | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| choice_response_alias      | heteroskedastic_t5 | score_correlation                | nan      |  nan      |  nan      |   0 |
| choice_response_alias      | heteroskedastic_t5 | normalized_score_error           | nan      |  nan      |  nan      |   0 |
| choice_response_alias      | heteroskedastic_t5 | composition_correction_gain      | nan      |  nan      |  nan      |   0 |
| choice_response_alias      | heteroskedastic_t5 | reference_correction_gain        | nan      |  nan      |  nan      |   0 |
| choice_response_alias      | heteroskedastic_t5 | mdd_null_false_positive          | nan      |  nan      |  nan      |   0 |
| choice_response_alias      | heteroskedastic_t5 | mdd_two_mdd_power                | nan      |  nan      |  nan      |   0 |
| choice_response_alias      | heteroskedastic_t5 | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| choice_response_alias      | heteroskedastic_t5 | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| clean                      | gaussian           | score_correlation                |   0.9875 |    0.9865 |    0.9884 |   2 |
| clean                      | gaussian           | normalized_score_error           |   0.1600 |    0.1544 |    0.1656 |   2 |
| clean                      | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |   2 |
| clean                      | gaussian           | reference_correction_gain        |  -0.0000 |   -0.0000 |    0.0000 |   2 |
| clean                      | gaussian           | mdd_null_false_positive          |   0.1250 |    0.0000 |    0.2500 |   2 |
| clean                      | gaussian           | mdd_two_mdd_power                |   0.9688 |    0.9375 |    1.0000 |   2 |
| clean                      | gaussian           | uncertainty_coverage             |   1.0000 |    1.0000 |    1.0000 |   2 |
| clean                      | gaussian           | uncertainty_successful_draw_rate |   1.0000 |    1.0000 |    1.0000 |   2 |
| clean                      | heteroskedastic_t5 | score_correlation                |   0.9882 |    0.9873 |    0.9891 |   2 |
| clean                      | heteroskedastic_t5 | normalized_score_error           |   0.1526 |    0.1463 |    0.1590 |   2 |
| clean                      | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |   2 |
| clean                      | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |   2 |
| clean                      | heteroskedastic_t5 | mdd_null_false_positive          |   0.0625 |    0.0625 |    0.0625 |   2 |
| clean                      | heteroskedastic_t5 | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |   2 |
| clean                      | heteroskedastic_t5 | uncertainty_coverage             |   0.9375 |    0.8750 |    1.0000 |   2 |
| clean                      | heteroskedastic_t5 | uncertainty_successful_draw_rate |   1.0000 |    1.0000 |    1.0000 |   2 |
| composition_shift          | gaussian           | score_correlation                |   0.9814 |    0.9806 |    0.9822 |   2 |
| composition_shift          | gaussian           | normalized_score_error           |   0.1930 |    0.1885 |    0.1976 |   2 |
| composition_shift          | gaussian           | composition_correction_gain      |   0.3596 |    0.3561 |    0.3631 |   2 |
| composition_shift          | gaussian           | reference_correction_gain        |  -0.0000 |   -0.0000 |    0.0000 |   2 |
| composition_shift          | gaussian           | mdd_null_false_positive          |   0.0938 |    0.0625 |    0.1250 |   2 |
| composition_shift          | gaussian           | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |   2 |
| composition_shift          | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| composition_shift          | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| composition_shift          | heteroskedastic_t5 | score_correlation                |   0.9821 |    0.9790 |    0.9852 |   2 |
| composition_shift          | heteroskedastic_t5 | normalized_score_error           |   0.1882 |    0.1701 |    0.2063 |   2 |
| composition_shift          | heteroskedastic_t5 | composition_correction_gain      |   0.3728 |    0.3692 |    0.3763 |   2 |
| composition_shift          | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |   2 |
| composition_shift          | heteroskedastic_t5 | mdd_null_false_positive          |   0.0625 |    0.0625 |    0.0625 |   2 |
| composition_shift          | heteroskedastic_t5 | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |   2 |
| composition_shift          | heteroskedastic_t5 | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| composition_shift          | heteroskedastic_t5 | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | gaussian           | score_correlation                | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | gaussian           | normalized_score_error           | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |   2 |
| correlated_replicate_shock | gaussian           | reference_correction_gain        |  -0.0000 |   -0.0000 |   -0.0000 |   2 |
| correlated_replicate_shock | gaussian           | mdd_null_false_positive          | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | gaussian           | mdd_two_mdd_power                | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | heteroskedastic_t5 | score_correlation                | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | heteroskedastic_t5 | normalized_score_error           | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |   2 |
| correlated_replicate_shock | heteroskedastic_t5 | reference_correction_gain        |  -0.0000 |   -0.0000 |    0.0000 |   2 |
| correlated_replicate_shock | heteroskedastic_t5 | mdd_null_false_positive          | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | heteroskedastic_t5 | mdd_two_mdd_power                | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | heteroskedastic_t5 | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | heteroskedastic_t5 | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| informative_precision      | gaussian           | score_correlation                |   0.9835 |    0.9835 |    0.9835 |   2 |
| informative_precision      | gaussian           | normalized_score_error           |   0.1821 |    0.1806 |    0.1836 |   2 |
| informative_precision      | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |   2 |
| informative_precision      | gaussian           | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |   2 |
| informative_precision      | gaussian           | mdd_null_false_positive          |   0.0312 |    0.0000 |    0.0625 |   2 |
| informative_precision      | gaussian           | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |   2 |
| informative_precision      | gaussian           | uncertainty_coverage             |   0.9375 |    0.8750 |    1.0000 |   2 |
| informative_precision      | gaussian           | uncertainty_successful_draw_rate |   1.0000 |    1.0000 |    1.0000 |   2 |
| informative_precision      | heteroskedastic_t5 | score_correlation                |   0.9836 |    0.9810 |    0.9862 |   2 |
| informative_precision      | heteroskedastic_t5 | normalized_score_error           |   0.1821 |    0.1663 |    0.1979 |   2 |
| informative_precision      | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |   2 |
| informative_precision      | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |   2 |
| informative_precision      | heteroskedastic_t5 | mdd_null_false_positive          |   0.1250 |    0.0625 |    0.1875 |   2 |
| informative_precision      | heteroskedastic_t5 | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |   2 |
| informative_precision      | heteroskedastic_t5 | uncertainty_coverage             |   1.0000 |    1.0000 |    1.0000 |   2 |
| informative_precision      | heteroskedastic_t5 | uncertainty_successful_draw_rate |   1.0000 |    1.0000 |    1.0000 |   2 |
| operator_kernel            | gaussian           | score_correlation                |   0.9868 |    0.9863 |    0.9872 |   2 |
| operator_kernel            | gaussian           | normalized_score_error           |   0.1664 |    0.1630 |    0.1698 |   2 |
| operator_kernel            | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |   2 |
| operator_kernel            | gaussian           | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |   2 |
| operator_kernel            | gaussian           | mdd_null_false_positive          |   0.0625 |    0.0625 |    0.0625 |   2 |
| operator_kernel            | gaussian           | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |   2 |
| operator_kernel            | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| operator_kernel            | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| operator_kernel            | heteroskedastic_t5 | score_correlation                |   0.9842 |    0.9815 |    0.9869 |   2 |
| operator_kernel            | heteroskedastic_t5 | normalized_score_error           |   0.1763 |    0.1613 |    0.1912 |   2 |
| operator_kernel            | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |   2 |
| operator_kernel            | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |   2 |
| operator_kernel            | heteroskedastic_t5 | mdd_null_false_positive          |   0.2188 |    0.0625 |    0.3750 |   2 |
| operator_kernel            | heteroskedastic_t5 | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |   2 |
| operator_kernel            | heteroskedastic_t5 | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| operator_kernel            | heteroskedastic_t5 | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | gaussian           | score_correlation                | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | gaussian           | normalized_score_error           | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |   2 |
| person_occasion_alias      | gaussian           | reference_correction_gain        |  -0.0000 |   -0.0000 |    0.0000 |   2 |
| person_occasion_alias      | gaussian           | mdd_null_false_positive          | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | gaussian           | mdd_two_mdd_power                | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | heteroskedastic_t5 | score_correlation                | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | heteroskedastic_t5 | normalized_score_error           | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |   2 |
| person_occasion_alias      | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |   2 |
| person_occasion_alias      | heteroskedastic_t5 | mdd_null_false_positive          | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | heteroskedastic_t5 | mdd_two_mdd_power                | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | heteroskedastic_t5 | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | heteroskedastic_t5 | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| reference_mixture          | gaussian           | score_correlation                |   0.9837 |    0.9815 |    0.9859 |   2 |
| reference_mixture          | gaussian           | normalized_score_error           |   0.1826 |    0.1732 |    0.1919 |   2 |
| reference_mixture          | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |   2 |
| reference_mixture          | gaussian           | reference_correction_gain        |   0.4215 |    0.3985 |    0.4444 |   2 |
| reference_mixture          | gaussian           | mdd_null_false_positive          |   0.0312 |    0.0000 |    0.0625 |   2 |
| reference_mixture          | gaussian           | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |   2 |
| reference_mixture          | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| reference_mixture          | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| reference_mixture          | heteroskedastic_t5 | score_correlation                |   0.9854 |    0.9853 |    0.9855 |   2 |
| reference_mixture          | heteroskedastic_t5 | normalized_score_error           |   0.1750 |    0.1740 |    0.1759 |   2 |
| reference_mixture          | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |   2 |
| reference_mixture          | heteroskedastic_t5 | reference_correction_gain        |   0.4239 |    0.3329 |    0.5149 |   2 |
| reference_mixture          | heteroskedastic_t5 | mdd_null_false_positive          |   0.1250 |    0.0625 |    0.1875 |   2 |
| reference_mixture          | heteroskedastic_t5 | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |   2 |
| reference_mixture          | heteroskedastic_t5 | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| reference_mixture          | heteroskedastic_t5 | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| support_hole               | gaussian           | score_correlation                | nan      |  nan      |  nan      |   0 |
| support_hole               | gaussian           | normalized_score_error           | nan      |  nan      |  nan      |   0 |
| support_hole               | gaussian           | composition_correction_gain      | nan      |  nan      |  nan      |   0 |
| support_hole               | gaussian           | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |   2 |
| support_hole               | gaussian           | mdd_null_false_positive          | nan      |  nan      |  nan      |   0 |
| support_hole               | gaussian           | mdd_two_mdd_power                | nan      |  nan      |  nan      |   0 |
| support_hole               | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| support_hole               | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| support_hole               | heteroskedastic_t5 | score_correlation                | nan      |  nan      |  nan      |   0 |
| support_hole               | heteroskedastic_t5 | normalized_score_error           | nan      |  nan      |  nan      |   0 |
| support_hole               | heteroskedastic_t5 | composition_correction_gain      | nan      |  nan      |  nan      |   0 |
| support_hole               | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |   2 |
| support_hole               | heteroskedastic_t5 | mdd_null_false_positive          | nan      |  nan      |  nan      |   0 |
| support_hole               | heteroskedastic_t5 | mdd_two_mdd_power                | nan      |  nan      |  nan      |   0 |
| support_hole               | heteroskedastic_t5 | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| support_hole               | heteroskedastic_t5 | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |

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
  "minimum_clean_score_correlation_lower": 0.9865364714322479,
  "maximum_clean_normalized_error_upper": 0.165564118205655,
  "minimum_composition_gain_lower": 0.35612640772962323,
  "minimum_reference_gain_lower": 0.3329024805181898,
  "maximum_truth_isolation_error": 0.0,
  "maximum_alias_identity_error": 0.0,
  "maximum_valid_operator_defect": 8.038961053955023e-16,
  "minimum_uncertainty_coverage": 0.96875,
  "minimum_uncertainty_success_rate": 1.0,
  "maximum_clean_mdd_false_positive_upper": 0.25,
  "minimum_clean_two_mdd_power_lower": 0.9375
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

Smoke-test only. No L5 promotion, human-text score, psychological construct, personality, state, or use claim.
