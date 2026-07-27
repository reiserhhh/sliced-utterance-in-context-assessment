# SUICA M3 Micro-Meso-Macro Foundation V1

Decision: `M3_MATCHED_FAMILY_RECOVERY_WITH_BASIC_REFUSAL_CHECKS`

## Scope

This battery tests a declared synthetic microscopic choice/response process,
its mesoscopic projections, transformation invariants, and required refusals.
It does not read real text or psychological labels.

## Checks

- PASS: `packet_isolation`
- PASS: `positive_response_identified`
- PASS: `positive_state_identified`
- PASS: `choice_js`
- PASS: `choice_heldout_skill`
- PASS: `position_geometry`
- PASS: `position_nrmse`
- PASS: `operator_recovery`
- PASS: `nonlinear_recovery`
- PASS: `nonlinear_heldout_increment`
- PASS: `state_recovery`
- PASS: `refusal_worlds`
- PASS: `affine_and_coarse_invariance`
- PASS: `observational_equivalence`

## Recovery summary

| world                           | metric                           |     mean |   lower95 |   upper95 |   n |
|:--------------------------------|:---------------------------------|---------:|----------:|----------:|----:|
| negative_no_common_support      | choice_js_median                 |   0.0050 |    0.0049 |    0.0051 |  60 |
| negative_no_common_support      | heldout_choice_log_skill         |   0.5255 |    0.5108 |    0.5401 |  60 |
| negative_no_common_support      | heldout_nonlinear_incremental_r2 | nan      |  nan      |  nan      |   0 |
| negative_no_common_support      | position_distance_spearman       | nan      |  nan      |  nan      |   0 |
| negative_no_common_support      | position_nrmse                   | nan      |  nan      |  nan      |   0 |
| negative_no_common_support      | operator_correlation             | nan      |  nan      |  nan      |   0 |
| negative_no_common_support      | nonlinear_correlation            | nan      |  nan      |  nan      |   0 |
| negative_no_common_support      | state_correlation                | nan      |  nan      |  nan      |   0 |
| negative_rank_deficient         | choice_js_median                 |   0.0050 |    0.0049 |    0.0051 |  60 |
| negative_rank_deficient         | heldout_choice_log_skill         |   0.4823 |    0.4688 |    0.4963 |  60 |
| negative_rank_deficient         | heldout_nonlinear_incremental_r2 | nan      |  nan      |  nan      |   0 |
| negative_rank_deficient         | position_distance_spearman       | nan      |  nan      |  nan      |   0 |
| negative_rank_deficient         | position_nrmse                   | nan      |  nan      |  nan      |   0 |
| negative_rank_deficient         | operator_correlation             | nan      |  nan      |  nan      |   0 |
| negative_rank_deficient         | nonlinear_correlation            | nan      |  nan      |  nan      |   0 |
| negative_rank_deficient         | state_correlation                | nan      |  nan      |  nan      |   0 |
| negative_single_occasion        | choice_js_median                 |   0.0050 |    0.0049 |    0.0050 |  60 |
| negative_single_occasion        | heldout_choice_log_skill         |   0.5135 |    0.5013 |    0.5260 |  60 |
| negative_single_occasion        | heldout_nonlinear_incremental_r2 |   0.1266 |    0.1246 |    0.1286 |  60 |
| negative_single_occasion        | position_distance_spearman       |   0.7330 |    0.7230 |    0.7433 |  60 |
| negative_single_occasion        | position_nrmse                   |   0.5870 |    0.5768 |    0.5973 |  60 |
| negative_single_occasion        | operator_correlation             |   0.9810 |    0.9806 |    0.9814 |  60 |
| negative_single_occasion        | nonlinear_correlation            |   0.9346 |    0.9339 |    0.9352 |  60 |
| negative_single_occasion        | state_correlation                | nan      |  nan      |  nan      |   0 |
| positive_linear_gaussian        | choice_js_median                 |   0.0049 |    0.0049 |    0.0050 |  60 |
| positive_linear_gaussian        | heldout_choice_log_skill         |   0.5178 |    0.5065 |    0.5291 |  60 |
| positive_linear_gaussian        | heldout_nonlinear_incremental_r2 |  -0.0072 |   -0.0074 |   -0.0071 |  60 |
| positive_linear_gaussian        | position_distance_spearman       |   0.9938 |    0.9936 |    0.9940 |  60 |
| positive_linear_gaussian        | position_nrmse                   |   0.0760 |    0.0749 |    0.0771 |  60 |
| positive_linear_gaussian        | operator_correlation             |   0.9951 |    0.9950 |    0.9952 |  60 |
| positive_linear_gaussian        | nonlinear_correlation            | nan      |  nan      |  nan      |   0 |
| positive_linear_gaussian        | state_correlation                |   0.9747 |    0.9744 |    0.9749 |  60 |
| positive_nonlinear_t5           | choice_js_median                 |   0.0050 |    0.0049 |    0.0051 |  60 |
| positive_nonlinear_t5           | heldout_choice_log_skill         |   0.5167 |    0.5066 |    0.5274 |  60 |
| positive_nonlinear_t5           | heldout_nonlinear_incremental_r2 |   0.1604 |    0.1581 |    0.1627 |  60 |
| positive_nonlinear_t5           | position_distance_spearman       |   0.9936 |    0.9934 |    0.9938 |  60 |
| positive_nonlinear_t5           | position_nrmse                   |   0.0767 |    0.0757 |    0.0775 |  60 |
| positive_nonlinear_t5           | operator_correlation             |   0.9952 |    0.9951 |    0.9953 |  60 |
| positive_nonlinear_t5           | nonlinear_correlation            |   0.9820 |    0.9818 |    0.9822 |  60 |
| positive_nonlinear_t5           | state_correlation                |   0.9744 |    0.9742 |    0.9747 |  60 |
| positive_shared_heteroskedastic | choice_js_median                 |   0.0049 |    0.0048 |    0.0050 |  60 |
| positive_shared_heteroskedastic | heldout_choice_log_skill         |   0.5251 |    0.5132 |    0.5374 |  60 |
| positive_shared_heteroskedastic | heldout_nonlinear_incremental_r2 |   0.1611 |    0.1584 |    0.1638 |  60 |
| positive_shared_heteroskedastic | position_distance_spearman       |   0.9931 |    0.9928 |    0.9933 |  60 |
| positive_shared_heteroskedastic | position_nrmse                   |   0.0798 |    0.0786 |    0.0810 |  60 |
| positive_shared_heteroskedastic | operator_correlation             |   0.9946 |    0.9944 |    0.9947 |  60 |
| positive_shared_heteroskedastic | nonlinear_correlation            |   0.9803 |    0.9799 |    0.9806 |  60 |
| positive_shared_heteroskedastic | state_correlation                |   0.9720 |    0.9715 |    0.9724 |  60 |

## Refusal rates

```json
{
  "negative_no_common_support": 1.0,
  "negative_single_occasion": 1.0,
  "negative_rank_deficient": 1.0
}
```

## Invariance and equivalence extrema

```json
{
  "maximum_invariance_error": 1.1213252548714081e-14,
  "minimum_invariance_geometry": 1.0,
  "maximum_equivalent_observable_error": 2.220446049250313e-16,
  "minimum_micro_difference": 0.8867824135144834
}
```

## Interpretation

The generator and estimator are separated at the Python-module and packet
interface, and observed packets contain no explicit truth or world label.
However, the public design manifest exposes the condition basis used by this
matched additive generator. Nonlinear recovery uses saturated observed
condition means, and state recovery uses the same additive zero-sum gauge as
the generator. The result is therefore an engineering baseline for known-basis
projection, simple refusals, and algebraic invariants, not a micro-to-meso
theory closure. The equivalence constructions are algebraic demonstrations;
they do not yet pass through the estimator as blinded classification tests.

## Claim boundary

This is an internal 60-seed matched-family repetition, not a sealed confirmation. A pass licenses known-basis additive projection, simple refusal guards, and algebraic invariants only. It does not establish recovery from a microscopic kernel, nonlinear out-of-family generalization, human-text existence, personality meaning, causality, construct validity, cross-language invariance, diagnosis, or clinical use.
