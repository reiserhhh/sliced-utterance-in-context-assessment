# SUICA E9 Embedding Interpretive Channel

## E9a anchor projection (stability + MTMM)

| construct             | kind      |   stability_r |   convergent_r |   max_discriminant_r | mtmm_ok   |
|:----------------------|:----------|--------------:|---------------:|---------------------:|:----------|
| first_person_usage_v2 | real      |         0.597 |          0.565 |                0.505 | True      |
| directive_action_v2   | real      |         0.578 |          0.276 |                0.382 | False     |
| tension_core_v2       | real      |         0.57  |          0.134 |                0.461 | False     |
| novelty_play_v2       | real      |         0.517 |          0.258 |                0.325 | False     |
| wcl_60                | real      |         0.512 |          0.222 |                0.265 | False     |
| wcl_03                | real      |         0.63  |          0.602 |                0.484 | True      |
| wcl_36                | real      |         0.68  |          0.659 |                0.435 | True      |
| wcl_11                | real      |         0.601 |          0.782 |                0.375 | True      |
| wcl_45                | real      |         0.683 |          0.622 |                0.643 | False     |
| wcl_25                | real      |         0.604 |          0.622 |                0.353 | True      |
| wcl_02                | real      |         0.634 |          0.722 |                0.438 | True      |
| wcl_07                | real      |         0.646 |          0.755 |                0.652 | True      |
| wcl_54                | real      |         0.633 |          0.53  |                0.581 | False     |
| wcl_22                | real      |         0.404 |          0.297 |                0.206 | True      |
| wcl_13                | real      |         0.625 |          0.229 |                0.582 | False     |
| wcl_35                | real      |         0.609 |          0.619 |                0.412 | True      |
| wcl_15                | real      |         0.562 |          0.407 |                0.472 | False     |
| wcl_23                | real      |         0.58  |          0.591 |                0.3   | True      |
| wcl_20                | real      |         0.586 |          0.815 |                0.545 | True      |
| scr_1                 | scrambled |         0.488 |        nan     |                0.552 | False     |
| scr_2                 | scrambled |         0.546 |        nan     |                0.484 | False     |
| scr_3                 | scrambled |         0.504 |        nan     |                0.509 | False     |

## E9b neighbor reading (k=50, vs random-neighbor null)

| construct             |   neighbor_read_r |   random_neighbor_r |   delta |   delta_ci_lo |   delta_ci_hi | e9b_ok   |
|:----------------------|------------------:|--------------------:|--------:|--------------:|--------------:|:---------|
| first_person_usage_v2 |             0.577 |               0.009 |   0.568 |         0.518 |         0.612 | True     |
| directive_action_v2   |             0.286 |              -0.018 |   0.304 |         0.258 |         0.352 | True     |
| tension_core_v2       |             0.121 |              -0.009 |   0.13  |         0.081 |         0.178 | False    |
| novelty_play_v2       |             0.41  |               0.017 |   0.393 |         0.345 |         0.437 | True     |
| wcl_60                |             0.293 |              -0.02  |   0.313 |         0.26  |         0.364 | True     |
| wcl_03                |             0.531 |              -0.004 |   0.535 |         0.485 |         0.583 | True     |
| wcl_36                |             0.573 |              -0.017 |   0.589 |         0.545 |         0.632 | True     |
| wcl_11                |             0.53  |               0.027 |   0.503 |         0.449 |         0.551 | True     |
| wcl_45                |             0.456 |               0.018 |   0.438 |         0.394 |         0.483 | True     |
| wcl_25                |             0.481 |               0.01  |   0.471 |         0.418 |         0.527 | True     |
| wcl_02                |             0.497 |              -0.01  |   0.507 |         0.444 |         0.563 | True     |
| wcl_07                |             0.534 |               0     |   0.534 |         0.492 |         0.582 | True     |
| wcl_54                |             0.42  |               0.008 |   0.412 |         0.372 |         0.461 | True     |
| wcl_22                |             0.414 |              -0.001 |   0.415 |         0.369 |         0.46  | True     |
| wcl_13                |             0.337 |               0.001 |   0.336 |         0.29  |         0.377 | True     |
| wcl_35                |             0.401 |              -0.027 |   0.427 |         0.36  |         0.487 | True     |
| wcl_15                |             0.377 |              -0.005 |   0.382 |         0.322 |         0.461 | True     |
| wcl_23                |             0.418 |              -0.003 |   0.421 |         0.313 |         0.532 | True     |
| wcl_20                |             0.421 |               0.021 |   0.4   |         0.337 |         0.456 | True     |

```json
{
  "n_users": 3183,
  "E9a_pass_count": 11,
  "E9a_pass": true,
  "E9a_scrambled_max_stability": 0.546396478290154,
  "E9b_pass_count": 18,
  "E9b_pass": true,
  "k_neighbors": 50,
  "model": "BAAI/bge-large-en-v1.5"
}
```
