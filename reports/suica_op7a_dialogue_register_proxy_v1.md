# OP-7a dialogue-register proxy (top-level vs reply turns)

| construct             |   within_top |   within_reply |   cross_time_separated |   same_occasion_cross_diagnostic |   level_shift_dz_reply_minus_top | verdict         |
|:----------------------|-------------:|---------------:|-----------------------:|---------------------------------:|---------------------------------:|:----------------|
| first_person_usage_v2 |        0.782 |          0.857 |                  0.739 |                            0.783 |                           -0.099 | register-robust |
| directive_action_v2   |        0.611 |          0.651 |                  0.493 |                            0.547 |                            0.124 | register-robust |
| tension_core_v2       |        0.405 |          0.561 |                  0.43  |                            0.481 |                            0.341 | register-robust |
| novelty_play_v2       |        0.535 |          0.61  |                  0.534 |                            0.624 |                           -0.28  | register-robust |
| wcl_60                |        0.505 |          0.625 |                  0.523 |                            0.577 |                           -0.135 | register-robust |
| wcl_03                |        0.671 |          0.707 |                  0.652 |                            0.759 |                           -0.297 | register-robust |
| wcl_36                |        0.592 |          0.755 |                  0.592 |                            0.656 |                            0.858 | register-robust |
| wcl_11                |        0.54  |          0.559 |                  0.512 |                            0.649 |                           -0.454 | register-robust |
| wcl_45                |        0.608 |          0.676 |                  0.61  |                            0.68  |                           -0.301 | register-robust |
| wcl_25                |        0.676 |          0.736 |                  0.67  |                            0.778 |                           -0.312 | register-robust |
| wcl_02                |        0.716 |          0.79  |                  0.697 |                            0.778 |                            0.555 | register-robust |
| wcl_07                |        0.531 |          0.634 |                  0.539 |                            0.612 |                           -0.27  | register-robust |
| wcl_54                |        0.644 |          0.584 |                  0.461 |                            0.592 |                           -0.323 | register-robust |
| wcl_22                |        0.453 |          0.558 |                  0.459 |                            0.516 |                           -0.032 | register-robust |
| wcl_13                |        0.539 |          0.673 |                  0.569 |                            0.627 |                            0.221 | register-robust |
| wcl_35                |        0.275 |          0.424 |                  0.299 |                            0.346 |                           -0.133 | register-robust |
| wcl_15                |        0.474 |          0.575 |                  0.49  |                            0.564 |                            0.115 | register-robust |
| wcl_23                |        0.493 |          0.599 |                  0.481 |                            0.542 |                           -0.47  | register-robust |
| wcl_20                |        0.549 |          0.651 |                  0.566 |                            0.748 |                            0.227 | register-robust |

```json
{
  "n_users_eligible": 1976,
  "n_constructs": 19,
  "n_assessable": 19,
  "n_register_robust": 19,
  "n_register_bound": 0,
  "n_indeterminate": 0,
  "material_level_shifts_dz_ge_0.5": [
    "wcl_36",
    "wcl_02"
  ],
  "mean_adjacency_inflation": 0.08118713621005609
}
```

Scope note: this is the Reddit-internal register boundary, a PRECURSOR to
OP-7 (AI-dialogue pilot), which remains open pending data collection.
