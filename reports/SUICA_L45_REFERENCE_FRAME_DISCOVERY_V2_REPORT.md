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
| aq_gauge_alias             | gaussian           | score_correlation                |   0.9879 |    0.9876 |    0.9882 |  30 |
| aq_gauge_alias             | gaussian           | normalized_score_error           |   0.1574 |    0.1553 |    0.1594 |  30 |
| aq_gauge_alias             | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| aq_gauge_alias             | gaussian           | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| aq_gauge_alias             | gaussian           | mdd_null_false_positive          |   0.0865 |    0.0667 |    0.1052 |  30 |
| aq_gauge_alias             | gaussian           | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| aq_gauge_alias             | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| aq_gauge_alias             | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| aq_gauge_alias             | heteroskedastic_t5 | score_correlation                |   0.9880 |    0.9878 |    0.9882 |  30 |
| aq_gauge_alias             | heteroskedastic_t5 | normalized_score_error           |   0.1563 |    0.1548 |    0.1578 |  30 |
| aq_gauge_alias             | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| aq_gauge_alias             | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| aq_gauge_alias             | heteroskedastic_t5 | mdd_null_false_positive          |   0.0802 |    0.0531 |    0.1083 |  30 |
| aq_gauge_alias             | heteroskedastic_t5 | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
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
| clean                      | gaussian           | score_correlation                |   0.9878 |    0.9874 |    0.9882 |  30 |
| clean                      | gaussian           | normalized_score_error           |   0.1578 |    0.1556 |    0.1603 |  30 |
| clean                      | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| clean                      | gaussian           | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| clean                      | gaussian           | mdd_null_false_positive          |   0.0677 |    0.0500 |    0.0896 |  30 |
| clean                      | gaussian           | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| clean                      | gaussian           | uncertainty_coverage             |   0.9750 |    0.9563 |    0.9938 |  10 |
| clean                      | gaussian           | uncertainty_successful_draw_rate |   1.0000 |    1.0000 |    1.0000 |  10 |
| clean                      | heteroskedastic_t5 | score_correlation                |   0.9878 |    0.9874 |    0.9883 |  30 |
| clean                      | heteroskedastic_t5 | normalized_score_error           |   0.1573 |    0.1547 |    0.1599 |  30 |
| clean                      | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| clean                      | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| clean                      | heteroskedastic_t5 | mdd_null_false_positive          |   0.0771 |    0.0552 |    0.1000 |  30 |
| clean                      | heteroskedastic_t5 | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| clean                      | heteroskedastic_t5 | uncertainty_coverage             |   0.9500 |    0.9375 |    0.9688 |  10 |
| clean                      | heteroskedastic_t5 | uncertainty_successful_draw_rate |   1.0000 |    1.0000 |    1.0000 |  10 |
| composition_shift          | gaussian           | score_correlation                |   0.9865 |    0.9862 |    0.9869 |  30 |
| composition_shift          | gaussian           | normalized_score_error           |   0.1658 |    0.1637 |    0.1679 |  30 |
| composition_shift          | gaussian           | composition_correction_gain      |   0.2250 |    0.2023 |    0.2479 |  30 |
| composition_shift          | gaussian           | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| composition_shift          | gaussian           | mdd_null_false_positive          |   0.0771 |    0.0542 |    0.1042 |  30 |
| composition_shift          | gaussian           | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| composition_shift          | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| composition_shift          | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| composition_shift          | heteroskedastic_t5 | score_correlation                |   0.9864 |    0.9861 |    0.9868 |  30 |
| composition_shift          | heteroskedastic_t5 | normalized_score_error           |   0.1664 |    0.1645 |    0.1684 |  30 |
| composition_shift          | heteroskedastic_t5 | composition_correction_gain      |   0.2151 |    0.1918 |    0.2370 |  30 |
| composition_shift          | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| composition_shift          | heteroskedastic_t5 | mdd_null_false_positive          |   0.0760 |    0.0573 |    0.0958 |  30 |
| composition_shift          | heteroskedastic_t5 | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| composition_shift          | heteroskedastic_t5 | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| composition_shift          | heteroskedastic_t5 | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | gaussian           | score_correlation                | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | gaussian           | normalized_score_error           | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| correlated_replicate_shock | gaussian           | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| correlated_replicate_shock | gaussian           | mdd_null_false_positive          | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | gaussian           | mdd_two_mdd_power                | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | heteroskedastic_t5 | score_correlation                | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | heteroskedastic_t5 | normalized_score_error           | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| correlated_replicate_shock | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| correlated_replicate_shock | heteroskedastic_t5 | mdd_null_false_positive          | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | heteroskedastic_t5 | mdd_two_mdd_power                | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | heteroskedastic_t5 | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| correlated_replicate_shock | heteroskedastic_t5 | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| informative_precision      | gaussian           | score_correlation                |   0.9869 |    0.9866 |    0.9873 |  30 |
| informative_precision      | gaussian           | normalized_score_error           |   0.1631 |    0.1608 |    0.1654 |  30 |
| informative_precision      | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| informative_precision      | gaussian           | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| informative_precision      | gaussian           | mdd_null_false_positive          |   0.0740 |    0.0552 |    0.0927 |  30 |
| informative_precision      | gaussian           | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| informative_precision      | gaussian           | uncertainty_coverage             |   0.9750 |    0.9500 |    1.0000 |  10 |
| informative_precision      | gaussian           | uncertainty_successful_draw_rate |   1.0000 |    1.0000 |    1.0000 |  10 |
| informative_precision      | heteroskedastic_t5 | score_correlation                |   0.9870 |    0.9867 |    0.9874 |  30 |
| informative_precision      | heteroskedastic_t5 | normalized_score_error           |   0.1630 |    0.1609 |    0.1651 |  30 |
| informative_precision      | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| informative_precision      | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| informative_precision      | heteroskedastic_t5 | mdd_null_false_positive          |   0.0688 |    0.0469 |    0.0927 |  30 |
| informative_precision      | heteroskedastic_t5 | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| informative_precision      | heteroskedastic_t5 | uncertainty_coverage             |   0.9313 |    0.9062 |    0.9563 |  10 |
| informative_precision      | heteroskedastic_t5 | uncertainty_successful_draw_rate |   1.0000 |    1.0000 |    1.0000 |  10 |
| operator_kernel            | gaussian           | score_correlation                |   0.9875 |    0.9872 |    0.9878 |  30 |
| operator_kernel            | gaussian           | normalized_score_error           |   0.1596 |    0.1576 |    0.1616 |  30 |
| operator_kernel            | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| operator_kernel            | gaussian           | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| operator_kernel            | gaussian           | mdd_null_false_positive          |   0.1177 |    0.0917 |    0.1448 |  30 |
| operator_kernel            | gaussian           | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| operator_kernel            | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| operator_kernel            | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| operator_kernel            | heteroskedastic_t5 | score_correlation                |   0.9879 |    0.9876 |    0.9882 |  30 |
| operator_kernel            | heteroskedastic_t5 | normalized_score_error           |   0.1570 |    0.1553 |    0.1587 |  30 |
| operator_kernel            | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| operator_kernel            | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| operator_kernel            | heteroskedastic_t5 | mdd_null_false_positive          |   0.0625 |    0.0417 |    0.0844 |  30 |
| operator_kernel            | heteroskedastic_t5 | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| operator_kernel            | heteroskedastic_t5 | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| operator_kernel            | heteroskedastic_t5 | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | gaussian           | score_correlation                | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | gaussian           | normalized_score_error           | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| person_occasion_alias      | gaussian           | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| person_occasion_alias      | gaussian           | mdd_null_false_positive          | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | gaussian           | mdd_two_mdd_power                | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | heteroskedastic_t5 | score_correlation                | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | heteroskedastic_t5 | normalized_score_error           | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| person_occasion_alias      | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| person_occasion_alias      | heteroskedastic_t5 | mdd_null_false_positive          | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | heteroskedastic_t5 | mdd_two_mdd_power                | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | heteroskedastic_t5 | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| person_occasion_alias      | heteroskedastic_t5 | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| reference_mixture          | gaussian           | score_correlation                |   0.9877 |    0.9873 |    0.9880 |  30 |
| reference_mixture          | gaussian           | normalized_score_error           |   0.1585 |    0.1563 |    0.1609 |  30 |
| reference_mixture          | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| reference_mixture          | gaussian           | reference_correction_gain        |   0.7151 |    0.6854 |    0.7427 |  30 |
| reference_mixture          | gaussian           | mdd_null_false_positive          |   0.0708 |    0.0510 |    0.0917 |  30 |
| reference_mixture          | gaussian           | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| reference_mixture          | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| reference_mixture          | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| reference_mixture          | heteroskedastic_t5 | score_correlation                |   0.9879 |    0.9876 |    0.9882 |  30 |
| reference_mixture          | heteroskedastic_t5 | normalized_score_error           |   0.1571 |    0.1551 |    0.1592 |  30 |
| reference_mixture          | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| reference_mixture          | heteroskedastic_t5 | reference_correction_gain        |   0.7312 |    0.7018 |    0.7601 |  30 |
| reference_mixture          | heteroskedastic_t5 | mdd_null_false_positive          |   0.0521 |    0.0344 |    0.0719 |  30 |
| reference_mixture          | heteroskedastic_t5 | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| reference_mixture          | heteroskedastic_t5 | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| reference_mixture          | heteroskedastic_t5 | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| support_hole               | gaussian           | score_correlation                | nan      |  nan      |  nan      |   0 |
| support_hole               | gaussian           | normalized_score_error           | nan      |  nan      |  nan      |   0 |
| support_hole               | gaussian           | composition_correction_gain      | nan      |  nan      |  nan      |   0 |
| support_hole               | gaussian           | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| support_hole               | gaussian           | mdd_null_false_positive          | nan      |  nan      |  nan      |   0 |
| support_hole               | gaussian           | mdd_two_mdd_power                | nan      |  nan      |  nan      |   0 |
| support_hole               | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| support_hole               | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| support_hole               | heteroskedastic_t5 | score_correlation                | nan      |  nan      |  nan      |   0 |
| support_hole               | heteroskedastic_t5 | normalized_score_error           | nan      |  nan      |  nan      |   0 |
| support_hole               | heteroskedastic_t5 | composition_correction_gain      | nan      |  nan      |  nan      |   0 |
| support_hole               | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
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
  "minimum_clean_score_correlation_lower": 0.9874001364977048,
  "maximum_clean_normalized_error_upper": 0.16031869099747525,
  "minimum_composition_gain_lower": 0.191760586512048,
  "minimum_reference_gain_lower": 0.6854152094421652,
  "maximum_truth_isolation_error": 0.0,
  "maximum_alias_identity_error": 0.0,
  "maximum_valid_operator_defect": 8.665078851565433e-16,
  "minimum_uncertainty_coverage": 0.9578125,
  "minimum_uncertainty_success_rate": 1.0,
  "maximum_clean_mdd_false_positive_upper": 0.1,
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

Opened synthetic discovery of the E45 reference-scoring edge only. V1 failed observable coverage; V2 changes only the uncertainty resampling model. Maximum licensed layer remains L4 pending sealed confirmation and a real study-specific G/D design.
