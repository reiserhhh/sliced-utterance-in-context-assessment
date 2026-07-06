# SUICA Rind Regime Test v3

> **AUDIT NOTICE (2026-07-05, round 3 — values below are the ORIGINAL run and are partially SUPERSEDED).**
> PRED-1 "4/4" was demoted to **3/4**: the tension delta (+0.150) is a temporal-clustering
> artifact (span-matched delta -0.033). PRED-3 values here (0.677/0.587/0.691) include a
> 24th derived feature by mistake; corrected 23-feature values are **0.620/0.530/0.572**.
> Authoritative record: docs/SUICA_CLAIMS_LEDGER.md ("Rind theory base v3 regime test").


## PRED-1 paired fixed vs mixed rind (PANDORA, same users)

| construct             |   n_users |   r_fixed_rind |   r_mixed_rind |   delta |   ci_lo |   ci_hi |
|:----------------------|----------:|---------------:|---------------:|--------:|--------:|--------:|
| first_person_usage_v2 |       918 |         0.8822 |         0.8161 |  0.0661 |  0.0423 |  0.0891 |
| directive_action_v2   |       918 |         0.7008 |         0.5548 |  0.1459 |  0.0869 |  0.2092 |
| tension_core_v2       |       918 |         0.3842 |         0.2345 |  0.1497 |  0.0665 |  0.2254 |
| novelty_play_v2       |       918 |         0.6478 |         0.3888 |  0.2589 |  0.1762 |  0.3393 |

## PRED-1b cross-corpus split-half at matched budget

| construct             |   essays_fixed_prompt |   pandora_mixed |   pandora_top_subreddit |   x_domain_fixed |
|:----------------------|----------------------:|----------------:|------------------------:|-----------------:|
| directive_action_v2   |                 0.404 |           0.386 |                   0.498 |            0.431 |
| first_person_usage_v2 |                 0.626 |           0.627 |                   0.729 |            0.728 |
| novelty_play_v2       |                 0.205 |           0.234 |                   0.413 |            0.643 |
| tension_core_v2       |                 0.221 |           0.124 |                   0.194 |            0.357 |

## PRED-2 / PRED-3

```json
{
  "PRED1_pass_count": 4,
  "PRED1_verdict": "pass",
  "PRED2": {
    "n_users": 31,
    "same_median_cos": 0.7462025072446364,
    "random_median_cos": 0.4982728791224397,
    "symbol_choice_auc": 0.809573361082206,
    "verdict": "pass"
  },
  "PRED3": {
    "pandora_vs_essays": 0.6765369689679199,
    "pandora_vs_x_market": 0.5866721924588455,
    "essays_vs_x_market": 0.6907979267175243,
    "verdict": "partial"
  }
}
```
