# SUICA E7 Within-Person State Discovery (deep PANDORA, rind-fixed, month cells)

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

## Within factors: congruence + lag structure

| factor   |   congruence_ab |   lag1_r |   lag1_ci_lo |   lag1_ci_hi |   lag2_r |   lag3_r |   lag1_shuffle_null | top_features                                                                                  |
|:---------|----------------:|---------:|-------------:|-------------:|---------:|---------:|--------------------:|:----------------------------------------------------------------------------------------------|
| state_f1 |           0.988 |   -0.008 |       -0.044 |        0.041 |   -0.068 |   -0.057 |              -0.092 | redemption_growth_rate, social_evaluation_rate, positive_affect_rate, contamination_loss_rate |
| state_f2 |           0.978 |   -0.038 |       -0.061 |       -0.014 |   -0.066 |   -0.049 |              -0.082 | temporal_sequence_rate, past_temporal_rate, self_focus_rate, third_person_rate                |
| state_f3 |           0.964 |    0.026 |        0.002 |        0.052 |   -0.01  |   -0.052 |              -0.084 | mentalization_rate, directive_rate, certainty_rate, self_focus_rate                           |
| state_f4 |           0.963 |   -0.049 |       -0.073 |       -0.025 |   -0.055 |   -0.027 |              -0.075 | contamination_loss_rate, negative_affect_rate, conflict_threat_rate, causal_meaning_rate      |
| state_f5 |           0.931 |   -0.001 |       -0.024 |        0.023 |   -0.005 |   -0.016 |              -0.063 | second_person_rate, self_focus_rate, agency_rate, future_temporal_rate                        |

## E7d within-vs-between best-match congruence

[0.876, 0.775, 0.713, 0.704, 0.545]

```json
{
  "E7a_features_ge_010": 3,
  "E7a_pass": false,
  "E7b_stable_factors": 5,
  "E7b_pass": true,
  "E7c_persistent_state_factors": 1,
  "E7c_pass": true,
  "E7d_within_between_matches": [
    0.876,
    0.775,
    0.713,
    0.704,
    0.545
  ],
  "E7d_distinct_structure": true
}
```
