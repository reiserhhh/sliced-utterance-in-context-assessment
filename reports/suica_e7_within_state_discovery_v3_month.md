# SUICA E7 v2 Within-Person State Discovery (deep, rind-fixed, occasions: month)

cells: 15844, users: 1175

## E7a feature state reliability (contiguous)

| feature                 |   within_state_split_half_r |
|:------------------------|----------------------------:|
| self_focus_rate         |                       0.136 |
| second_person_rate      |                       0.133 |
| moral_norm_rate         |                       0.118 |
| general_people_rate     |                       0.087 |
| third_person_rate       |                       0.085 |
| achievement_order_rate  |                       0.072 |
| future_temporal_rate    |                       0.069 |
| communion_rate          |                       0.064 |
| past_temporal_rate      |                       0.061 |
| novelty_play_rate       |                       0.056 |
| directive_rate          |                       0.055 |
| positive_affect_rate    |                       0.051 |
| mentalization_rate      |                       0.049 |
| uncertainty_rate        |                       0.042 |
| causal_meaning_rate     |                       0.039 |
| agency_rate             |                       0.037 |
| social_evaluation_rate  |                       0.035 |
| conflict_threat_rate    |                       0.033 |
| negative_affect_rate    |                       0.033 |
| contamination_loss_rate |                       0.028 |
| temporal_sequence_rate  |                       0.027 |
| redemption_growth_rate  |                       0.027 |
| certainty_rate          |                       0.016 |

## Factors: cell-state reliability, congruence (with shuffled null), above-null persistence

| factor   |   cell_state_reliability |   congruence_ab |   congruence_null |   lag1_r |   null_mean |   delta1 |   delta1_ci_lo |   delta1_ci_hi |   delta3 |   decay_ci_lo |   decay_ci_hi | top_features                                                                                  |
|:---------|-------------------------:|----------------:|------------------:|---------:|------------:|---------:|---------------:|---------------:|---------:|--------------:|--------------:|:----------------------------------------------------------------------------------------------|
| state_f1 |                    0.036 |           0.988 |             0.99  |   -0.008 |      -0.078 |    0.069 |          0.033 |          0.106 |    0.02  |         0.011 |         0.094 | redemption_growth_rate, social_evaluation_rate, positive_affect_rate, contamination_loss_rate |
| state_f2 |                    0.057 |           0.978 |             0.983 |   -0.038 |      -0.074 |    0.036 |          0.012 |          0.061 |    0.025 |        -0.025 |         0.044 | temporal_sequence_rate, past_temporal_rate, self_focus_rate, third_person_rate                |
| state_f3 |                    0.084 |           0.964 |             0.954 |    0.026 |      -0.074 |    0.1   |          0.079 |          0.128 |    0.022 |         0.046 |         0.109 | mentalization_rate, directive_rate, certainty_rate, self_focus_rate                           |
| state_f4 |                    0.057 |           0.963 |             0.948 |   -0.049 |      -0.076 |    0.027 |          0.002 |          0.05  |    0.048 |        -0.058 |         0.014 | contamination_loss_rate, negative_affect_rate, conflict_threat_rate, causal_meaning_rate      |
| state_f5 |                    0.121 |           0.931 |             0.918 |   -0.001 |      -0.075 |    0.074 |          0.05  |          0.103 |    0.059 |        -0.014 |         0.047 | second_person_rate, self_focus_rate, agency_rate, future_temporal_rate                        |

```json
{
  "occasion": "month",
  "E7a_features_ge_010": 3,
  "E7a_pass": false,
  "E7b_cell_state_reliability_ge_010": 1,
  "E7b_pass": false,
  "E7c_persistent_decaying_factors": 2,
  "median_congruence_null_gap": 0.010138206809889638
}
```
