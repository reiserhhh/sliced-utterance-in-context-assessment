# SUICA M3 Micro-to-Meso Mechanism Atlas

Decision: `M3_ATLAS_V1_LOW_ORDER_PARAMETER_RECOVERY_PASS`

## Question

This discovery does not assume that microscopic event vectors connect directly
to one mesoscopic author axis. It tests whether several distinct intermediate
mechanisms can be recovered selectively from independent event panels.

## Mechanism families

1. state-density distribution beyond the mean;
2. condition-to-response operator (an operational if-then signature);
3. metastable/Koopman slow mode;
4. interactional alignment or susceptibility operator;
5. higher-order path memory beyond a first-order Markov approximation;
6. opportunity profile as a declared non-response confound;
7. a union summary for mixed worlds.

## Discovery checks

- PASS: `density_state_distribution_auc`
- PASS: `density_state_distribution_geometry`
- PASS: `density_state_distribution_selectivity`
- PASS: `conditional_response_operator_auc`
- PASS: `conditional_response_operator_geometry`
- PASS: `conditional_response_operator_selectivity`
- PASS: `metastable_slow_mode_auc`
- PASS: `metastable_slow_mode_geometry`
- PASS: `metastable_slow_mode_selectivity`
- PASS: `interactional_alignment_auc`
- PASS: `interactional_alignment_geometry`
- PASS: `interactional_alignment_selectivity`
- PASS: `higher_order_path_auc`
- PASS: `higher_order_path_geometry`
- PASS: `higher_order_path_selectivity`
- PASS: `null_calibration`
- PASS: `opportunity_detection`
- PASS: `opportunity_residual_control`

## Expected-family results at 96 events per occasion

| world                         | family               |     mean |   lower95_seed_quantile |   upper95_seed_quantile |
|:------------------------------|:---------------------|---------:|------------------------:|------------------------:|
| conditional_response_operator | conditional_operator | 0.940366 |                0.923425 |                0.954108 |
| density_state_distribution    | distribution_kme     | 0.759067 |                0.710179 |                0.797551 |
| higher_order_path             | higher_order_path    | 0.679473 |                0.652531 |                0.699177 |
| interactional_alignment       | interaction_coupling | 0.938155 |                0.92435  |                0.950592 |
| metastable_slow_mode          | koopman_spectrum     | 0.632022 |                0.570291 |                0.660335 |
| mixed_superposition           | union                | 0.800194 |                0.755455 |                0.829335 |
| opportunity_only              | opportunity_profile  | 0.839486 |                0.801933 |                0.880627 |

## Sample-information frontier

|   events | world                         |   expected_auc |   expected_geometry |   expected_win_fraction |
|---------:|:------------------------------|---------------:|--------------------:|------------------------:|
|       24 | conditional_response_operator |       0.931003 |            0.828355 |                     1   |
|       24 | density_state_distribution    |       0.692196 |            0.642373 |                     1   |
|       24 | higher_order_path             |       0.592176 |            0.36989  |                     0.9 |
|       24 | interactional_alignment       |       0.929072 |            0.825405 |                     1   |
|       24 | metastable_slow_mode          |       0.622692 |            0.394679 |                     1   |
|       48 | conditional_response_operator |       0.932881 |            0.829677 |                     1   |
|       48 | density_state_distribution    |       0.732674 |            0.714355 |                     1   |
|       48 | higher_order_path             |       0.655556 |            0.532717 |                     1   |
|       48 | interactional_alignment       |       0.93804  |            0.828099 |                     1   |
|       48 | metastable_slow_mode          |       0.62006  |            0.414232 |                     1   |
|       96 | conditional_response_operator |       0.940366 |            0.830494 |                     1   |
|       96 | density_state_distribution    |       0.759067 |            0.788657 |                     1   |
|       96 | higher_order_path             |       0.679473 |            0.616321 |                     1   |
|       96 | interactional_alignment       |       0.938155 |            0.831224 |                     1   |
|       96 | metastable_slow_mode          |       0.632022 |            0.460519 |                     0.9 |

## Diagnostics

```json
{
  "density_state_distribution": {
    "expected_family": "distribution_kme",
    "mean_auc": 0.7590674603174603,
    "mean_geometry": 0.7886568660062963,
    "win_fraction": 1.0
  },
  "conditional_response_operator": {
    "expected_family": "conditional_operator",
    "mean_auc": 0.9403659611992945,
    "mean_geometry": 0.8304943221597944,
    "win_fraction": 1.0
  },
  "metastable_slow_mode": {
    "expected_family": "koopman_spectrum",
    "mean_auc": 0.6320216049382715,
    "mean_geometry": 0.4605191488843663,
    "win_fraction": 0.9
  },
  "interactional_alignment": {
    "expected_family": "interaction_coupling",
    "mean_auc": 0.938154761904762,
    "mean_geometry": 0.831224465758049,
    "win_fraction": 1.0
  },
  "higher_order_path": {
    "expected_family": "higher_order_path",
    "mean_auc": 0.6794731040564375,
    "mean_geometry": 0.6163206236231572,
    "win_fraction": 1.0
  },
  "null_max_auc": 0.5064329805996473,
  "opportunity_auc": 0.8394863315696648,
  "opportunity_residual_max_auc": 0.5156812169312169
}
```

## Interpretation

Passing a world means that the registered summary recovers independent-view
author geometry generated by that mechanism and is not merely a mean score.
It does not establish that the mechanism exists in human text or that it is a
personality construct. Failure is informative: it identifies a mechanism that
cannot yet be distinguished at the tested event budget.

The opportunity-only world is especially important. Stable author
reidentification caused only by differing condition exposure must be assigned
to the opportunity profile, while response-residual mechanisms remain near
chance. This separates a measurable author environment from an author
response law.
