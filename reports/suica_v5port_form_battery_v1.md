# V5PORT — trading-side SUICA v5 form battery scored on PANDORA (v4 conventions)

Label-free Tier-U run; same slices/estimators/gate as the v4 all-19 table.
Formulas ported verbatim from trading-agent-claude (see script docstring).

| construct                   |   rho_raw |   rho_shared_matched |   rho_cond_disjoint |   rho_class_disjoint |   c1_share |   ci_lo |   ci_hi |   mediated_total_upper | v4_family                  |   n_users | verdict   |
|:----------------------------|----------:|---------------------:|--------------------:|---------------------:|-----------:|--------:|--------:|-----------------------:|:---------------------------|----------:|:----------|
| v5_laugh_rate               |     0.295 |                0.162 |               0.112 |                0.074 |      0.312 |   0     |   0.627 |                  0     | C-family (venue signature) |      2941 |           |
| v5_emoji_kaomoji_rate       |     0.15  |                0.032 |               0.013 |                0.003 |    nan     | nan     | nan     |                  0     | undetermined               |      2941 |           |
| v5_exclaim_question_density |     0.524 |                0.365 |               0.181 |                0.152 |      0.506 |   0.32  |   0.612 |                  0.096 | composite                  |      2941 |           |
| v5_ellipsis_rate            |    -0.002 |               -0.001 |              -0.001 |               -0.001 |    nan     | nan     | nan     |                nan     | undetermined               |      2941 |           |
| v5_apostrophe_omission_rate |     0.678 |                0.47  |               0.353 |                0.323 |      0.249 |   0.014 |   0.405 |                  0     | F-family (flesh trait)     |      2941 |           |
| v5_allcaps_rate             |     0.318 |                0.104 |               0.054 |                0.039 |      0.478 |   0.263 |   0.747 |                  0.19  | C-family (venue signature) |      2941 |           |
| v5_elongation_rate          |     0.29  |                0.148 |               0.104 |                0.071 |      0.3   |   0     |   0.629 |                  0     | C-family (venue signature) |      2941 |           |
| v5_punct_density            |     0.577 |                0.445 |               0.33  |                0.283 |      0.259 |   0.151 |   0.357 |                  0.052 | F-family (flesh trait)     |      2941 |           |
| v5_first_person_rate        |     0.688 |                0.486 |               0.354 |                0.276 |      0.271 |   0.204 |   0.33  |                  0.378 | F-family (flesh trait)     |      2941 |           |
| v5_second_person_rate       |     0.454 |                0.322 |               0.162 |                0.112 |      0.496 |   0.384 |   0.602 |                  0.309 | composite                  |      2941 |           |
| v5_third_person_rate        |     0.447 |                0.241 |               0.103 |                0.094 |      0.574 |   0.438 |   0.676 |                  0.346 | C-family (venue signature) |      2941 |           |
| v5_ascii_share              |     0.077 |                0.068 |               0.084 |                0.081 |    nan     | nan     | nan     |                  0     | undetermined               |      2941 |           |
| v5_hiragana_share           |    -0.001 |               -0     |              -0     |               -0.001 |    nan     | nan     | nan     |                nan     | undetermined               |      2941 |           |
| v5hp_tension_core_v2        |     0.282 |                0.083 |               0.063 |                0.049 |    nan     | nan     | nan     |                  0     | undetermined               |      2941 |           |
| v5hp_directive_action_v2    |     0.339 |                0.161 |               0.068 |                0.057 |      0.579 |   0.339 |   0.797 |                  0.083 | C-family (venue signature) |      2941 |           |
| v5hp_first_person_usage_v2  |     0.477 |                0.214 |               0.155 |                0.119 |      0.277 |   0.001 |   0.458 |                  0.225 | composite                  |      2941 |           |
| v5hp_novelty_play_v2        |     0.337 |                0.186 |               0.097 |                0.041 |      0.482 |   0.284 |   0.63  |                  0.535 | C-family (venue signature) |      2941 |           |
| v5hi_tension_core_v2        |     0.144 |                0.067 |               0.042 |                0.028 |    nan     | nan     | nan     |                  0     | undetermined               |      2923 |           |
| v5hi_directive_action_v2    |     0.258 |                0.174 |               0.093 |                0.101 |      0.464 |   0     |   0.778 |                  0.195 | composite                  |      2921 |           |
| v5hi_first_person_usage_v2  |     0.65  |                0.446 |               0.321 |                0.249 |      0.281 |   0.206 |   0.35  |                  0.378 | F-family (flesh trait)     |      2941 |           |
| v5hi_novelty_play_v2        |     0.181 |                0.177 |               0.07  |               -0.001 |      0.604 |   0.205 |   0.854 |                  0.273 | C-family (venue signature) |      2828 |           |
| v5_log_tokens_mean          |     0.751 |                0.656 |               0.505 |                0.463 |      0.23  |   0.185 |   0.27  |                  0.286 | F-family (flesh trait)     |      2942 |           |
| v5_post_len_cv              |     0.356 |                0.219 |               0.093 |                0.057 |      0.577 |   0.418 |   0.727 |                  0     | C-family (venue signature) |      2942 |           |

## v4 reference rows (all19, round-10 audited)

| construct             |   rho_raw |   rho_shared_matched |   rho_cond_disjoint |   rho_class_disjoint |   c1_share |   ci_lo |   ci_hi |   mediated_total_upper | v4_family                  |
|:----------------------|----------:|---------------------:|--------------------:|---------------------:|-----------:|--------:|--------:|-----------------------:|:---------------------------|
| first_person_usage_v2 |     0.684 |                0.48  |               0.346 |                0.268 |      0.279 |   0.21  |   0.345 |                  0.398 | F-family (flesh trait)     |
| directive_action_v2   |     0.409 |                0.212 |               0.112 |                0.1   |      0.471 |   0.226 |   0.663 |                  0.209 | C-family (venue signature) |
| tension_core_v2       |     0.316 |                0.09  |               0.081 |                0.053 |    nan     | nan     | nan     |                  0     | undetermined               |
| novelty_play_v2       |     0.382 |                0.261 |               0.108 |                0.033 |      0.587 |   0.411 |   0.72  |                  0.628 | C-family (venue signature) |
| wcl_60                |     0.709 |                0.43  |               0.407 |                0.365 |      0.053 |   0     |   0.201 |                  0.056 | F-family (flesh trait)     |
| wcl_13                |     0.462 |                0.209 |               0.206 |                0.169 |      0.014 |   0     |   0.235 |                  0.129 | F-family (flesh trait)     |
| wcl_23                |     0.537 |                0.221 |               0.183 |                0.169 |      0.172 |   0     |   0.342 |                  0.275 | F-family (flesh trait)     |

## Notes
- Unit deviation: v5 native unit is post/occasion; here rates are per 128-token slice
  (v4 unit) for comparability; length habits are per comment within the frozen halves.
- laugh_rate counts URL 'www' on Reddit (ported as-is; interpret accordingly).
- JA features on an EN corpus are register-transport probes, expected degenerate.
- Hurdle rows: v5hp_* = P(any signal per slice), v5hi_* = intensity given signal;
  plain-rate references are the v4 rows above (v5 proposal P2, first empirical test).