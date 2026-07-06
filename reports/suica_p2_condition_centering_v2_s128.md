# SUICA P2 Condition-Centering Value (v2)

## P2a lexicon constructs

| construct             |   n_users |   r_centered |   r_raw |   delta |   delta_ci_lo |   delta_ci_hi |
|:----------------------|----------:|-------------:|--------:|--------:|--------------:|--------------:|
| novelty_play_v2       |      3726 |       0.1005 |  0.3123 | -0.2118 |       -0.2467 |       -0.1721 |
| directive_action_v2   |      3726 |       0.3114 |  0.3766 | -0.0652 |       -0.0896 |       -0.0407 |
| adversity_recovery_v2 |      3726 |       0.0593 |  0.1055 | -0.0462 |       -0.065  |       -0.0271 |
| first_person_usage_v2 |      3726 |       0.5538 |  0.6535 | -0.0996 |       -0.1185 |       -0.0815 |
| tension_core_v2       |      3726 |       0.2733 |  0.3061 | -0.0328 |       -0.0471 |       -0.0168 |

pooled delta = -0.0911, CI [-0.1017, -0.0803]

## P2b node occupancy

{
  "n_users": 3726,
  "mean_node_r_centered": 0.09590337448754867,
  "mean_node_r_raw": 0.1628318986288271,
  "delta": -0.06692852414127844,
  "delta_ci_lo": -0.0747556666568613,
  "delta_ci_hi": -0.059570720329181044
}

```json
{
  "p2a_pooled_delta": -0.0911375503846881,
  "p2a_pooled_ci": [
    -0.10171521936969027,
    -0.08028474781470209
  ],
  "P2a_verdict": "fail",
  "p2b": {
    "n_users": 3726,
    "mean_node_r_centered": 0.09590337448754867,
    "mean_node_r_raw": 0.1628318986288271,
    "delta": -0.06692852414127844,
    "delta_ci_lo": -0.0747556666568613,
    "delta_ci_hi": -0.059570720329181044
  },
  "P2b_verdict": "fail"
}
```
