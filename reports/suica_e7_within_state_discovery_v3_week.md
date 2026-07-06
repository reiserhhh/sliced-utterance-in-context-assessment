# SUICA E7 v2 Within-Person State Discovery (deep, rind-fixed, occasions: week)

cells: 15465, users: 864

## E7a feature state reliability (contiguous)

| feature                 |   within_state_split_half_r |
|:------------------------|----------------------------:|
| second_person_rate      |                       0.217 |
| self_focus_rate         |                       0.184 |
| third_person_rate       |                       0.136 |
| moral_norm_rate         |                       0.1   |
| past_temporal_rate      |                       0.099 |
| novelty_play_rate       |                       0.095 |
| communion_rate          |                       0.093 |
| general_people_rate     |                       0.093 |
| positive_affect_rate    |                       0.083 |
| achievement_order_rate  |                       0.081 |
| contamination_loss_rate |                       0.079 |
| future_temporal_rate    |                       0.07  |
| mentalization_rate      |                       0.065 |
| directive_rate          |                       0.059 |
| temporal_sequence_rate  |                       0.055 |
| social_evaluation_rate  |                       0.052 |
| agency_rate             |                       0.051 |
| conflict_threat_rate    |                       0.047 |
| uncertainty_rate        |                       0.047 |
| causal_meaning_rate     |                       0.046 |
| negative_affect_rate    |                       0.037 |
| redemption_growth_rate  |                       0.036 |
| certainty_rate          |                       0.034 |

## Factors: cell-state reliability, congruence (with shuffled null), above-null persistence

| factor   |   cell_state_reliability |   congruence_ab |   congruence_null |   lag1_r |   null_mean |   delta1 |   delta1_ci_lo |   delta1_ci_hi |   delta3 |   decay_ci_lo |   decay_ci_hi | top_features                                                                                 |
|:---------|-------------------------:|----------------:|------------------:|---------:|------------:|---------:|---------------:|---------------:|---------:|--------------:|--------------:|:---------------------------------------------------------------------------------------------|
| state_f1 |                    0.058 |           0.991 |             0.984 |   -0.011 |      -0.053 |    0.042 |          0.012 |          0.069 |    0.018 |        -0.012 |         0.061 | redemption_growth_rate, social_evaluation_rate, positive_affect_rate, achievement_order_rate |
| state_f2 |                    0.114 |           0.987 |             0.981 |   -0.009 |      -0.049 |    0.04  |          0.008 |          0.079 |    0.057 |        -0.063 |         0.024 | past_temporal_rate, temporal_sequence_rate, self_focus_rate, general_people_rate             |
| state_f3 |                    0.105 |           0.979 |             0.971 |    0.049 |      -0.05  |    0.099 |          0.041 |          0.17  |    0.085 |        -0.015 |         0.042 | mentalization_rate, certainty_rate, directive_rate, self_focus_rate                          |
| state_f4 |                    0.067 |           0.967 |             0.964 |   -0     |      -0.054 |    0.054 |          0.02  |          0.087 |    0.01  |        -0.007 |         0.095 | contamination_loss_rate, negative_affect_rate, conflict_threat_rate, general_people_rate     |
| state_f5 |                    0.134 |           0.952 |             0.863 |    0.041 |      -0.049 |    0.09  |          0.062 |          0.119 |    0.044 |         0.011 |         0.082 | second_person_rate, agency_rate, future_temporal_rate, self_focus_rate                       |

```json
{
  "occasion": "week",
  "E7a_features_ge_010": 3,
  "E7a_pass": false,
  "E7b_cell_state_reliability_ge_010": 3,
  "E7b_pass": true,
  "E7c_persistent_decaying_factors": 1,
  "median_congruence_null_gap": 0.0072851339904602685
}
```
