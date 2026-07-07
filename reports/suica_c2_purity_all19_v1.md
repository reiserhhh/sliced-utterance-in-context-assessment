# C2 purity decomposition — ALL 19 constructs (v4 gate classification)

| construct             |   rho_raw |   rho_shared_matched |   rho_cond_disjoint |   rho_class_disjoint |   c1_share |   ci_lo |   ci_hi |   mediated_total_upper | v4_family                  |
|:----------------------|----------:|---------------------:|--------------------:|---------------------:|-----------:|--------:|--------:|-----------------------:|:---------------------------|
| first_person_usage_v2 |     0.683 |                0.48  |               0.346 |                0.268 |      0.279 |   0.209 |   0.345 |                  0.398 | F-family (flesh trait)     |
| directive_action_v2   |     0.409 |                0.212 |               0.112 |                0.1   |      0.471 |   0.226 |   0.663 |                  0.209 | C-family (venue signature) |
| tension_core_v2       |     0.316 |                0.09  |               0.081 |                0.053 |    nan     | nan     | nan     |                  0     | undetermined               |
| novelty_play_v2       |     0.382 |                0.261 |               0.108 |                0.033 |      0.587 |   0.411 |   0.72  |                  0.628 | C-family (venue signature) |
| wcl_60                |     0.463 |                0.329 |               0.134 |                0.077 |      0.594 |   0.295 |   0.762 |                  0.575 | C-family (venue signature) |
| wcl_03                |     0.387 |                0.346 |               0.16  |                0.103 |      0.537 |   0.357 |   0.711 |                  0.496 | composite                  |
| wcl_36                |     0.528 |                0.27  |               0.171 |                0.124 |      0.364 |   0.204 |   0.497 |                  0.267 | composite                  |
| wcl_11                |     0.502 |                0.226 |               0.147 |                0.109 |      0.351 |   0.145 |   0.495 |                  0.526 | composite                  |
| wcl_45                |     0.345 |                0.101 |               0.073 |                0.057 |      0.28  |   0.089 |   0.64  |                  0.091 | composite                  |
| wcl_25                |     0.4   |                0.129 |               0.098 |                0.058 |      0.244 |   0     |   0.555 |                  0.211 | composite                  |
| wcl_02                |     0.313 |                0.13  |               0.072 |                0.028 |      0.45  |   0.126 |   0.769 |                  0.405 | C-family (venue signature) |
| wcl_07                |     0.403 |                0.16  |               0.087 |                0.07  |      0.458 |   0.175 |   0.661 |                  0.354 | C-family (venue signature) |
| wcl_54                |     0.311 |                0.106 |               0.087 |                0.058 |      0.183 |   0     |   0.522 |                  0.24  | composite                  |
| wcl_22                |     0.389 |                0.226 |               0.082 |                0.059 |      0.638 |   0.384 |   0.83  |                  0.519 | C-family (venue signature) |
| wcl_13                |     0.322 |                0.093 |               0.057 |                0.044 |    nan     |   0.252 |   0.801 |                  0.121 | undetermined               |
| wcl_35                |     0.591 |                0.293 |               0.231 |                0.206 |      0.212 |   0.058 |   0.341 |                  0.262 | F-family (flesh trait)     |
| wcl_15                |     0.315 |                0.11  |               0.105 |                0.082 |      0.042 |   0     |   0.386 |                  0.165 | composite                  |
| wcl_23                |     0.343 |                0.146 |               0.063 |                0.029 |      0.566 |   0.302 |   0.807 |                  0.62  | C-family (venue signature) |
| wcl_20                |     0.176 |                0.045 |               0.015 |                0.028 |    nan     | nan     | nan     |                  0     | undetermined               |

```json
{
  "n_F_family": 2,
  "n_C_family": 7,
  "n_composite": 7,
  "n_undetermined": 3
}
```

Gate (provisional, THEORY 7.2): F-family iff class-disjoint >= 0.15 AND share < 0.30. Estimators licensed by W-B/W-B2/W-B2c/W-B3; mediated_total = upper bound under coupling; shares are bands per the F6.3 alarm.
