# C2 purity decomposition — ALL 19 constructs (v4 gate classification)

| construct             |   rho_raw |   rho_shared_matched |   rho_cond_disjoint |   rho_class_disjoint |   c1_share |   ci_lo |   ci_hi |   mediated_total_upper | v4_family                  |
|:----------------------|----------:|---------------------:|--------------------:|---------------------:|-----------:|--------:|--------:|-----------------------:|:---------------------------|
| first_person_usage_v2 |     0.683 |                0.48  |               0.346 |                0.268 |      0.279 |   0.209 |   0.345 |                  0.398 | F-family (flesh trait)     |
| directive_action_v2   |     0.409 |                0.212 |               0.112 |                0.1   |      0.471 |   0.226 |   0.663 |                  0.209 | C-family (venue signature) |
| tension_core_v2       |     0.316 |                0.09  |               0.081 |                0.053 |    nan     | nan     | nan     |                  0     | undetermined               |
| novelty_play_v2       |     0.382 |                0.261 |               0.108 |                0.033 |      0.587 |   0.411 |   0.72  |                  0.628 | C-family (venue signature) |
| wcl_60                |     0.709 |                0.43  |               0.407 |                0.365 |      0.053 |   0     |   0.201 |                  0.056 | F-family (flesh trait)     |
| wcl_03                |     0.574 |                0.346 |               0.17  |                0.14  |      0.508 |   0.358 |   0.631 |                  0.369 | composite                  |
| wcl_36                |     0.573 |                0.341 |               0.21  |                0.159 |      0.385 |   0.277 |   0.479 |                  0.513 | composite                  |
| wcl_11                |     0.54  |                0.352 |               0.179 |                0.102 |      0.492 |   0.369 |   0.613 |                  0.696 | composite                  |
| wcl_45                |     0.516 |                0.285 |               0.194 |                0.159 |      0.32  |   0.168 |   0.464 |                  0.313 | composite                  |
| wcl_25                |     0.523 |                0.335 |               0.155 |                0.075 |      0.538 |   0.404 |   0.657 |                  0.742 | C-family (venue signature) |
| wcl_02                |     0.55  |                0.389 |               0.158 |                0.041 |      0.592 |   0.445 |   0.717 |                  0.747 | C-family (venue signature) |
| wcl_07                |     0.603 |                0.433 |               0.288 |                0.11  |      0.336 |   0.172 |   0.461 |                  0.783 | composite                  |
| wcl_54                |     0.46  |                0.183 |               0.123 |                0.096 |      0.329 |   0     |   0.564 |                  0.191 | C-family (venue signature) |
| wcl_22                |     0.471 |                0.214 |               0.134 |                0.1   |      0.376 |   0.154 |   0.547 |                  0.399 | C-family (venue signature) |
| wcl_13                |     0.462 |                0.209 |               0.206 |                0.169 |      0.014 |   0     |   0.235 |                  0.129 | F-family (flesh trait)     |
| wcl_35                |     0.449 |                0.347 |               0.135 |                0.074 |      0.611 |   0.419 |   0.779 |                  0.158 | C-family (venue signature) |
| wcl_15                |     0.344 |                0.23  |               0.153 |                0.135 |      0.333 |   0.083 |   0.493 |                  0.115 | composite                  |
| wcl_23                |     0.537 |                0.221 |               0.183 |                0.169 |      0.172 |   0     |   0.342 |                  0.275 | F-family (flesh trait)     |
| wcl_20                |     0.498 |                0.287 |               0.116 |                0.021 |      0.595 |   0.307 |   0.734 |                  0.728 | C-family (venue signature) |

```json
{
  "n_F_family": 4,
  "n_C_family": 8,
  "n_composite": 6,
  "n_undetermined": 1
}
```

Gate (provisional, THEORY 7.2): F-family iff class-disjoint >= 0.15 AND share < 0.30. Estimators licensed by W-B/W-B2/W-B2c/W-B3; mediated_total = upper bound under coupling AND rng-stream sensitive (~+/-0.02); shares are bands per the F6.3 alarm. wcl scores TRANSPORTED from the frozen op9 fit (round-10 rule: constructs are bound to their fit).
