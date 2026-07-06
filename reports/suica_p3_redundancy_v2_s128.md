# SUICA P3 Redundancy vs Empath (v2)

| target                          |   n_users |   empath_cv_r2 |
|:--------------------------------|----------:|---------------:|
| raw_base::first_person_usage_v2 |      4980 |         0.4278 |
| choice::choice_ax_05            |      3204 |         0.3581 |
| fe_base::first_person_usage_v2  |      4980 |         0.3428 |
| choice::choice_ax_11            |      3204 |         0.2722 |
| raw_base::novelty_play_v2       |      4980 |         0.2662 |
| choice::choice_ax_03            |      3204 |         0.2621 |
| choice::choice_ax_02            |      3204 |         0.2568 |
| choice::choice_ax_06            |      3204 |         0.2091 |
| choice::choice_ax_08            |      3204 |         0.1939 |
| choice::choice_ax_00            |      3204 |         0.1843 |
| choice::choice_ax_04            |      3204 |         0.1215 |
| raw_base::directive_action_v2   |      4980 |         0.1159 |
| raw_base::tension_core_v2       |      4980 |         0.0811 |
| choice::choice_ax_01            |      3204 |         0.0732 |
| raw_base::adversity_recovery_v2 |      4980 |         0.0732 |
| fe_base::directive_action_v2    |      4980 |         0.064  |
| choice::choice_ax_10            |      3204 |         0.0599 |
| fe_base::tension_core_v2        |      4980 |         0.0592 |
| fe_base::adversity_recovery_v2  |      4980 |         0.0407 |
| fe_base::novelty_play_v2        |      4980 |         0.032  |
| choice::choice_ax_07            |      3204 |         0.0258 |
| choice::choice_ax_12            |      3204 |         0.0117 |
| choice::choice_ax_09            |      3204 |         0.0089 |

```json
{
  "n_targets": 23,
  "fraction_r2_le_075": 1.0,
  "max_r2": 0.42784146926186084,
  "P3_verdict": "pass"
}
```
