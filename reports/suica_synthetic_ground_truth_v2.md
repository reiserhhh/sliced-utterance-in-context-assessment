# SUICA P0 Synthetic Ground Truth (v2)

Scorer equivalence max diff: 0.00e+00

## Recovery by world

| world          | construct             |   rank_recovery_spearman |   planted_person |   planted_condition |   planted_interaction |   est_person |   est_condition |   est_interaction | dominant_component_match   |   dominant_share_abs_error |   est_residual_share |
|:---------------|:----------------------|-------------------------:|-----------------:|--------------------:|----------------------:|-------------:|----------------:|------------------:|:---------------------------|---------------------------:|---------------------:|
| W1_person      | novelty_play_v2       |                   0.9611 |           0.8863 |              0.0643 |                0.0494 |       0.9207 |          0.061  |            0.0183 | True                       |                     0.0344 |               0.464  |
| W1_person      | directive_action_v2   |                   0.9797 |           0.9375 |              0.0318 |                0.0307 |       0.9457 |          0.0311 |            0.0232 | True                       |                     0.0082 |               0.2999 |
| W1_person      | adversity_recovery_v2 |                   0.9618 |           0.897  |              0.0614 |                0.0416 |       0.9137 |          0.0611 |            0.0252 | True                       |                     0.0167 |               0.4457 |
| W1_person      | first_person_usage_v2 |                   0.9805 |           0.8792 |              0.0722 |                0.0486 |       0.8829 |          0.0744 |            0.0427 | True                       |                     0.0037 |               0.28   |
| W1_person      | tension_core_v2       |                   0.9736 |           0.9219 |              0.0408 |                0.0374 |       0.9352 |          0.0316 |            0.0332 | True                       |                     0.0133 |               0.2889 |
| W2_condition   | novelty_play_v2       |                   0.8155 |           0.0883 |              0.8507 |                0.061  |       0.1007 |          0.8771 |            0.0222 | True                       |                     0.0264 |               0.6132 |
| W2_condition   | directive_action_v2   |                   0.8685 |           0.0907 |              0.8618 |                0.0475 |       0.078  |          0.8829 |            0.039  | True                       |                     0.0212 |               0.3763 |
| W2_condition   | adversity_recovery_v2 |                   0.8312 |           0.0872 |              0.8616 |                0.0511 |       0.0896 |          0.8761 |            0.0343 | True                       |                     0.0145 |               0.5014 |
| W2_condition   | first_person_usage_v2 |                   0.8746 |           0.1011 |              0.8488 |                0.0501 |       0.1051 |          0.8454 |            0.0495 | True                       |                     0.0034 |               0.3712 |
| W2_condition   | tension_core_v2       |                   0.8889 |           0.1368 |              0.8028 |                0.0604 |       0.1382 |          0.8197 |            0.0421 | True                       |                     0.0169 |               0.4043 |
| W3_interaction | novelty_play_v2       |                   0.7213 |           0.2795 |              0.0677 |                0.6528 |       0.2334 |          0.0721 |            0.6944 | True                       |                     0.0416 |               0.4678 |
| W3_interaction | directive_action_v2   |                   0.7454 |           0.3033 |              0.1061 |                0.5906 |       0.2373 |          0.1169 |            0.6458 | True                       |                     0.0552 |               0.3319 |
| W3_interaction | adversity_recovery_v2 |                   0.66   |           0.2296 |              0.2249 |                0.5455 |       0.1833 |          0.2472 |            0.5695 | True                       |                     0.024  |               0.4701 |
| W3_interaction | first_person_usage_v2 |                   0.6806 |           0.2789 |              0.113  |                0.608  |       0.2115 |          0.1256 |            0.6629 | True                       |                     0.0549 |               0.294  |
| W3_interaction | tension_core_v2       |                   0.7056 |           0.3134 |              0.0331 |                0.6535 |       0.2192 |          0.0295 |            0.7514 | True                       |                     0.0979 |               0.3002 |

## Null worlds

mean null person share: 0.0012; false-positive rate: 6/100 = 0.060

## MixedLM vs MoM (tension, W1)

```json
{
  "mixedlm": {
    "person_share": 0.6684961588206744,
    "condition_share": 0.018912687748235676,
    "interaction_share": 0.038115396272575285,
    "residual_share": 0.27447575715851463
  },
  "mom": {
    "person_share": 0.6794889680151533,
    "condition_share": 0.016718814118398376,
    "interaction_share": 0.023841526703464247,
    "residual_share": 0.27995069116298404
  }
}
```

react amplitude recovery r (W3, tension): 0.9490

## Criteria

```json
{
  "scorer_equivalence_pass": true,
  "rank_recovery_pass": true,
  "dominant_component_pass": true,
  "dominant_share_error_pass": true,
  "null_person_share_pass": true,
  "null_false_positive_rate": 0.06,
  "null_false_positive_pass": true,
  "P0_verdict": "pass"
}
```
