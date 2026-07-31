# SUICA L4-to-L5 Reference-Frame Discovery

Decision: `REFUSE_L45_PROMOTION`

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
- FAIL: `observable_uncertainty`
- PASS: `mdd_false_positive`
- PASS: `mdd_power`

## Selected summaries

| world                      | noise_mode         | metric                           |     mean |   lower95 |   upper95 |   n |
|:---------------------------|:-------------------|:---------------------------------|---------:|----------:|----------:|----:|
| aq_gauge_alias             | gaussian           | score_correlation                |   0.9880 |    0.9876 |    0.9883 |  30 |
| aq_gauge_alias             | gaussian           | normalized_score_error           |   0.1566 |    0.1544 |    0.1587 |  30 |
| aq_gauge_alias             | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| aq_gauge_alias             | gaussian           | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| aq_gauge_alias             | gaussian           | mdd_null_false_positive          |   0.0865 |    0.0667 |    0.1052 |  30 |
| aq_gauge_alias             | gaussian           | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| aq_gauge_alias             | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| aq_gauge_alias             | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| aq_gauge_alias             | heteroskedastic_t5 | score_correlation                |   0.9876 |    0.9872 |    0.9879 |  30 |
| aq_gauge_alias             | heteroskedastic_t5 | normalized_score_error           |   0.1590 |    0.1566 |    0.1613 |  30 |
| aq_gauge_alias             | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| aq_gauge_alias             | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| aq_gauge_alias             | heteroskedastic_t5 | mdd_null_false_positive          |   0.1104 |    0.0760 |    0.1479 |  30 |
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
| clean                      | gaussian           | score_correlation                |   0.9877 |    0.9873 |    0.9880 |  30 |
| clean                      | gaussian           | normalized_score_error           |   0.1582 |    0.1561 |    0.1603 |  30 |
| clean                      | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| clean                      | gaussian           | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| clean                      | gaussian           | mdd_null_false_positive          |   0.0792 |    0.0563 |    0.1042 |  30 |
| clean                      | gaussian           | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| clean                      | gaussian           | uncertainty_coverage             |   0.6750 |    0.6062 |    0.7312 |  10 |
| clean                      | gaussian           | uncertainty_successful_draw_rate |   1.0000 |    1.0000 |    1.0000 |  10 |
| clean                      | heteroskedastic_t5 | score_correlation                |   0.9877 |    0.9873 |    0.9880 |  30 |
| clean                      | heteroskedastic_t5 | normalized_score_error           |   0.1585 |    0.1562 |    0.1606 |  30 |
| clean                      | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| clean                      | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| clean                      | heteroskedastic_t5 | mdd_null_false_positive          |   0.0708 |    0.0490 |    0.0948 |  30 |
| clean                      | heteroskedastic_t5 | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| clean                      | heteroskedastic_t5 | uncertainty_coverage             |   0.7188 |    0.6687 |    0.7750 |  10 |
| clean                      | heteroskedastic_t5 | uncertainty_successful_draw_rate |   1.0000 |    1.0000 |    1.0000 |  10 |
| composition_shift          | gaussian           | score_correlation                |   0.9866 |    0.9863 |    0.9870 |  30 |
| composition_shift          | gaussian           | normalized_score_error           |   0.1650 |    0.1631 |    0.1670 |  30 |
| composition_shift          | gaussian           | composition_correction_gain      |   0.2490 |    0.2281 |    0.2695 |  30 |
| composition_shift          | gaussian           | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| composition_shift          | gaussian           | mdd_null_false_positive          |   0.0740 |    0.0531 |    0.0959 |  30 |
| composition_shift          | gaussian           | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| composition_shift          | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| composition_shift          | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| composition_shift          | heteroskedastic_t5 | score_correlation                |   0.9867 |    0.9864 |    0.9870 |  30 |
| composition_shift          | heteroskedastic_t5 | normalized_score_error           |   0.1646 |    0.1625 |    0.1668 |  30 |
| composition_shift          | heteroskedastic_t5 | composition_correction_gain      |   0.2259 |    0.2021 |    0.2522 |  30 |
| composition_shift          | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| composition_shift          | heteroskedastic_t5 | mdd_null_false_positive          |   0.0729 |    0.0510 |    0.0969 |  30 |
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
| informative_precision      | gaussian           | score_correlation                |   0.9871 |    0.9867 |    0.9875 |  30 |
| informative_precision      | gaussian           | normalized_score_error           |   0.1622 |    0.1599 |    0.1646 |  30 |
| informative_precision      | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| informative_precision      | gaussian           | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| informative_precision      | gaussian           | mdd_null_false_positive          |   0.0750 |    0.0563 |    0.0948 |  30 |
| informative_precision      | gaussian           | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| informative_precision      | gaussian           | uncertainty_coverage             |   0.6875 |    0.6188 |    0.7625 |  10 |
| informative_precision      | gaussian           | uncertainty_successful_draw_rate |   1.0000 |    1.0000 |    1.0000 |  10 |
| informative_precision      | heteroskedastic_t5 | score_correlation                |   0.9871 |    0.9867 |    0.9874 |  30 |
| informative_precision      | heteroskedastic_t5 | normalized_score_error           |   0.1625 |    0.1603 |    0.1648 |  30 |
| informative_precision      | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| informative_precision      | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| informative_precision      | heteroskedastic_t5 | mdd_null_false_positive          |   0.0708 |    0.0479 |    0.0958 |  30 |
| informative_precision      | heteroskedastic_t5 | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| informative_precision      | heteroskedastic_t5 | uncertainty_coverage             |   0.7750 |    0.7125 |    0.8375 |  10 |
| informative_precision      | heteroskedastic_t5 | uncertainty_successful_draw_rate |   1.0000 |    1.0000 |    1.0000 |  10 |
| operator_kernel            | gaussian           | score_correlation                |   0.9880 |    0.9876 |    0.9884 |  30 |
| operator_kernel            | gaussian           | normalized_score_error           |   0.1566 |    0.1543 |    0.1590 |  30 |
| operator_kernel            | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| operator_kernel            | gaussian           | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| operator_kernel            | gaussian           | mdd_null_false_positive          |   0.0792 |    0.0594 |    0.1010 |  30 |
| operator_kernel            | gaussian           | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| operator_kernel            | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| operator_kernel            | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| operator_kernel            | heteroskedastic_t5 | score_correlation                |   0.9880 |    0.9877 |    0.9884 |  30 |
| operator_kernel            | heteroskedastic_t5 | normalized_score_error           |   0.1561 |    0.1539 |    0.1584 |  30 |
| operator_kernel            | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| operator_kernel            | heteroskedastic_t5 | reference_correction_gain        |   0.0000 |    0.0000 |    0.0000 |  30 |
| operator_kernel            | heteroskedastic_t5 | mdd_null_false_positive          |   0.0667 |    0.0437 |    0.0917 |  30 |
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
| reference_mixture          | gaussian           | score_correlation                |   0.9879 |    0.9876 |    0.9883 |  30 |
| reference_mixture          | gaussian           | normalized_score_error           |   0.1566 |    0.1543 |    0.1587 |  30 |
| reference_mixture          | gaussian           | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| reference_mixture          | gaussian           | reference_correction_gain        |   0.7119 |    0.6817 |    0.7403 |  30 |
| reference_mixture          | gaussian           | mdd_null_false_positive          |   0.0667 |    0.0427 |    0.0948 |  30 |
| reference_mixture          | gaussian           | mdd_two_mdd_power                |   1.0000 |    1.0000 |    1.0000 |  30 |
| reference_mixture          | gaussian           | uncertainty_coverage             | nan      |  nan      |  nan      |   0 |
| reference_mixture          | gaussian           | uncertainty_successful_draw_rate | nan      |  nan      |  nan      |   0 |
| reference_mixture          | heteroskedastic_t5 | score_correlation                |   0.9878 |    0.9874 |    0.9882 |  30 |
| reference_mixture          | heteroskedastic_t5 | normalized_score_error           |   0.1572 |    0.1547 |    0.1596 |  30 |
| reference_mixture          | heteroskedastic_t5 | composition_correction_gain      |   0.0000 |    0.0000 |    0.0000 |  30 |
| reference_mixture          | heteroskedastic_t5 | reference_correction_gain        |   0.7288 |    0.7023 |    0.7567 |  30 |
| reference_mixture          | heteroskedastic_t5 | mdd_null_false_positive          |   0.0740 |    0.0531 |    0.0958 |  30 |
| reference_mixture          | heteroskedastic_t5 | mdd_two_mdd_power                |   0.9990 |    0.9969 |    1.0000 |  30 |
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
  "minimum_clean_score_correlation_lower": 0.987339024711282,
  "maximum_clean_normalized_error_upper": 0.16064079923402141,
  "minimum_composition_gain_lower": 0.20210772047377276,
  "minimum_reference_gain_lower": 0.6816620083500586,
  "maximum_truth_isolation_error": 0.0,
  "maximum_alias_identity_error": 0.0,
  "maximum_valid_operator_defect": 8.883991063504153e-16,
  "minimum_uncertainty_coverage": 0.7140625,
  "minimum_uncertainty_success_rate": 1.0,
  "maximum_clean_mdd_false_positive_upper": 0.10416666666666667,
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

Opened synthetic discovery of the E45 reference-scoring edge only. Maximum licensed layer remains L4 until a separately sealed fresh-seed confirmation and a study-specific real-text G/D design.
