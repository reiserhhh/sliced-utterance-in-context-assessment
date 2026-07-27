# SUICA M3 Micro-Meso-Macro Foundation V1

Decision: `M3_SMOKE_PASS_SYNTHETIC_MICRO_MESO_CLOSURE`

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
| negative_no_common_support      | choice_js_median                 |   0.0066 |    0.0062 |    0.0071 |   2 |
| negative_no_common_support      | heldout_choice_log_skill         |   0.4705 |    0.4076 |    0.5334 |   2 |
| negative_no_common_support      | heldout_nonlinear_incremental_r2 | nan      |  nan      |  nan      |   0 |
| negative_no_common_support      | position_distance_spearman       | nan      |  nan      |  nan      |   0 |
| negative_no_common_support      | position_nrmse                   | nan      |  nan      |  nan      |   0 |
| negative_no_common_support      | operator_correlation             | nan      |  nan      |  nan      |   0 |
| negative_no_common_support      | nonlinear_correlation            | nan      |  nan      |  nan      |   0 |
| negative_no_common_support      | state_correlation                | nan      |  nan      |  nan      |   0 |
| negative_rank_deficient         | choice_js_median                 |   0.0064 |    0.0063 |    0.0065 |   2 |
| negative_rank_deficient         | heldout_choice_log_skill         |   0.5044 |    0.4871 |    0.5217 |   2 |
| negative_rank_deficient         | heldout_nonlinear_incremental_r2 | nan      |  nan      |  nan      |   0 |
| negative_rank_deficient         | position_distance_spearman       | nan      |  nan      |  nan      |   0 |
| negative_rank_deficient         | position_nrmse                   | nan      |  nan      |  nan      |   0 |
| negative_rank_deficient         | operator_correlation             | nan      |  nan      |  nan      |   0 |
| negative_rank_deficient         | nonlinear_correlation            | nan      |  nan      |  nan      |   0 |
| negative_rank_deficient         | state_correlation                | nan      |  nan      |  nan      |   0 |
| negative_single_occasion        | choice_js_median                 |   0.0062 |    0.0058 |    0.0065 |   2 |
| negative_single_occasion        | heldout_choice_log_skill         |   0.4474 |    0.4325 |    0.4623 |   2 |
| negative_single_occasion        | heldout_nonlinear_incremental_r2 |   0.1244 |    0.1119 |    0.1369 |   2 |
| negative_single_occasion        | position_distance_spearman       |   0.6726 |    0.6425 |    0.7026 |   2 |
| negative_single_occasion        | position_nrmse                   |   0.6236 |    0.5994 |    0.6478 |   2 |
| negative_single_occasion        | operator_correlation             |   0.9815 |    0.9795 |    0.9835 |   2 |
| negative_single_occasion        | nonlinear_correlation            |   0.9341 |    0.9309 |    0.9373 |   2 |
| negative_single_occasion        | state_correlation                | nan      |  nan      |  nan      |   0 |
| positive_linear_gaussian        | choice_js_median                 |   0.0059 |    0.0059 |    0.0060 |   2 |
| positive_linear_gaussian        | heldout_choice_log_skill         |   0.5411 |    0.4861 |    0.5961 |   2 |
| positive_linear_gaussian        | heldout_nonlinear_incremental_r2 |  -0.0075 |   -0.0082 |   -0.0068 |   2 |
| positive_linear_gaussian        | position_distance_spearman       |   0.9939 |    0.9930 |    0.9948 |   2 |
| positive_linear_gaussian        | position_nrmse                   |   0.0753 |    0.0707 |    0.0798 |   2 |
| positive_linear_gaussian        | operator_correlation             |   0.9949 |    0.9948 |    0.9950 |   2 |
| positive_linear_gaussian        | nonlinear_correlation            | nan      |  nan      |  nan      |   0 |
| positive_linear_gaussian        | state_correlation                |   0.9742 |    0.9728 |    0.9756 |   2 |
| positive_nonlinear_t5           | choice_js_median                 |   0.0060 |    0.0059 |    0.0061 |   2 |
| positive_nonlinear_t5           | heldout_choice_log_skill         |   0.4743 |    0.3753 |    0.5734 |   2 |
| positive_nonlinear_t5           | heldout_nonlinear_incremental_r2 |   0.1604 |    0.1473 |    0.1735 |   2 |
| positive_nonlinear_t5           | position_distance_spearman       |   0.9932 |    0.9922 |    0.9941 |   2 |
| positive_nonlinear_t5           | position_nrmse                   |   0.0769 |    0.0737 |    0.0801 |   2 |
| positive_nonlinear_t5           | operator_correlation             |   0.9954 |    0.9950 |    0.9959 |   2 |
| positive_nonlinear_t5           | nonlinear_correlation            |   0.9820 |    0.9813 |    0.9827 |   2 |
| positive_nonlinear_t5           | state_correlation                |   0.9743 |    0.9724 |    0.9762 |   2 |
| positive_shared_heteroskedastic | choice_js_median                 |   0.0071 |    0.0064 |    0.0078 |   2 |
| positive_shared_heteroskedastic | heldout_choice_log_skill         |   0.5184 |    0.5136 |    0.5232 |   2 |
| positive_shared_heteroskedastic | heldout_nonlinear_incremental_r2 |   0.1791 |    0.1698 |    0.1884 |   2 |
| positive_shared_heteroskedastic | position_distance_spearman       |   0.9929 |    0.9925 |    0.9933 |   2 |
| positive_shared_heteroskedastic | position_nrmse                   |   0.0768 |    0.0760 |    0.0775 |   2 |
| positive_shared_heteroskedastic | operator_correlation             |   0.9947 |    0.9936 |    0.9958 |   2 |
| positive_shared_heteroskedastic | nonlinear_correlation            |   0.9822 |    0.9795 |    0.9848 |   2 |
| positive_shared_heteroskedastic | state_correlation                |   0.9718 |    0.9691 |    0.9745 |   2 |

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
  "maximum_invariance_error": 1.0880185641326534e-14,
  "minimum_invariance_geometry": 1.0,
  "maximum_equivalent_observable_error": 1.1102230246251565e-16,
  "minimum_micro_difference": 0.9535199809512349
}
```

## Interpretation

The microscopic generator and mesoscopic estimator are physically separated.
Observed packets contain no truth, world label, planted basis, latent rank, or
systematic component. A positive result licenses only the registered synthetic
micro-to-meso derivation. The stable-position/state alias and the
same-occupancy/different-transition construction demonstrate that identical
mesoscopic observations need not identify one microscopic cause.

## Claim boundary

Smoke-only execution check. No scientific, real-text, personality, causal, construct, diagnostic, or clinical claim.
