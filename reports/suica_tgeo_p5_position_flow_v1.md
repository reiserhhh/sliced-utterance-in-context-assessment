# T-GEO-P5 — position-in-text flow: open vs close 128 tokens (label-free)

Comments >= 288 tokens: n = 21496; user-level gate >= 3 for mean shifts, >= 5 for frames (n = 1380 users).

## Mean-level shift (close - open), user level, sign-flip null

| construct | n users | user mean diff | frac > 0 | p |
|---|---|---|---|---|
| first_person_usage_v2 | 2169 | -0.6871 | 0.30 | 0.0000 |
| tension_core_v2 | 2169 | +0.0547 | 0.55 | 0.0000 |
| wcl_36 | 2169 | -0.0971 | 0.46 | 0.0000 |
| wcl_54 | 2169 | -0.1160 | 0.43 | 0.0000 |
| wcl_15 | 2169 | -0.0364 | 0.38 | 0.0000 |
| wcl_25 | 2169 | -0.0314 | 0.43 | 0.0015 |
| wcl_22 | 2169 | -0.0928 | 0.47 | 0.0040 |
| wcl_02 | 2169 | +0.0295 | 0.50 | 0.0045 |
| wcl_20 | 2169 | +0.0255 | 0.48 | 0.0525 |
| directive_action_v2 | 2169 | +0.0259 | 0.49 | 0.1040 |
| wcl_07 | 2169 | -0.0167 | 0.40 | 0.1785 |
| novelty_play_v2 | 2169 | -0.0102 | 0.44 | 0.2230 |
| wcl_23 | 2169 | -0.0073 | 0.48 | 0.5415 |
| wcl_03 | 2169 | +0.0068 | 0.49 | 0.6900 |
| wcl_11 | 2169 | -0.0044 | 0.47 | 0.7100 |
| wcl_35 | 2169 | -0.0056 | 0.44 | 0.7120 |
| wcl_13 | 2169 | +0.0067 | 0.51 | 0.8335 |
| wcl_45 | 2169 | +0.0016 | 0.51 | 0.9425 |
| wcl_60 | 2169 | +0.0001 | 0.28 | 0.9860 |

## Frame flow (top-4 subspace, open vs close)

Chordal distance 0.4919 vs swap-null mean 0.2789 (p95 0.3475), p = 0.0. Per-PC best congruence [0.965, 0.94, 0.732, 0.78].
