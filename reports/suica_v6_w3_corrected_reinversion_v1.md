# V6-W3 -- Essays re-inversion with the F12.4 exact centering-bias correction (label-free)

Registered commit: 0a4a97a (F12.4, docs/SUICA_THEORY_FORMAL_NOTES_V3.md)

n_texts=1349 (5<=m<=12), n_windows=8793; excluded m>12: 12; m<5: 948; subsample-gap texts: 0

Pooled F12.4 coefficients: A=5.783604 B_coef=-7.783604 C=-3.934800 D_coef=6.734463 det=8.322542

## Summary

| quantity | naive | corrected |
|---|---|---|
| B_diag_mean | -0.0103 | 0.0303 |
| Gamma0_diag_mean | 0.7273 | 0.8095 |

## Per-construct implied theta (sorted by naive theta, descending)

| construct | naive_theta | corrected_theta | r_naive | r_corrected |
|---|---|---|---|---|
| wcl_60 | 0.4285 | 0.3443 | -0.3620 | -0.3078 |
| wcl_23 | 0.1029 | 0.0482 | -0.1018 | -0.0481 |
| tension_core_v2 | 0.0705 | 0.0171 | -0.0702 | -0.0171 |
| wcl_54 | 0.0567 | 0.0038 | -0.0565 | -0.0038 |
| directive_action_v2 | 0.0435 | 0.0000 | -0.0434 | +0.0090 |
| wcl_22 | 0.0390 | 0.0000 | -0.0389 | +0.0134 |
| wcl_25 | 0.0343 | 0.0000 | -0.0343 | +0.0179 |
| wcl_20 | 0.0311 | 0.0000 | -0.0311 | +0.0210 |
| wcl_45 | 0.0123 | 0.0000 | -0.0123 | +0.0393 |
| wcl_11 | 0.0088 | 0.0000 | -0.0088 | +0.0426 |
| first_person_usage_v2 | 0.0000 | 0.0000 | +0.0328 | +0.0828 |
| novelty_play_v2 | 0.0000 | 0.0000 | +0.0266 | +0.0769 |
| wcl_03 | 0.0000 | 0.0000 | +0.0195 | +0.0700 |
| wcl_36 | 0.0000 | 0.0000 | +0.0424 | +0.0921 |
| wcl_02 | 0.0000 | 0.0000 | +0.0289 | +0.0791 |
| wcl_07 | 0.0000 | 0.0000 | +0.0564 | +0.1055 |
| wcl_13 | 0.0000 | 0.0000 | +0.0291 | +0.0793 |
| wcl_35 | 0.0000 | 0.0000 | +0.0486 | +0.0981 |
| wcl_15 | 0.0000 | 0.0000 | +0.0038 | +0.0548 |

## Bootstrap (500 text-resample draws, seed 20260712)

Each draw redoes the full pipeline (D2, S0/symS1, the draw's own n-composition F12.4 coefficients, both inversions). Percentile CIs.

| quantity | point | CI 2.5% | CI 97.5% | frac draws > 0 |
|---|---|---|---|---|
| B_diag_mean corrected | +0.0303 | +0.0136 | +0.0484 | 1.000 |
| B_diag_mean naive | -0.0103 | -0.0248 | +0.0054 | - |

### Corrected signed r_c, 6 largest |r_c| (both signs eligible)

| construct | r_c | CI 2.5% | CI 97.5% |
|---|---|---|---|
| wcl_60 | -0.3078 | -0.8733 | -0.0348 |
| wcl_07 | +0.1055 | -0.0393 | +0.2142 |
| wcl_35 | +0.0981 | +0.0182 | +0.1654 |
| wcl_36 | +0.0921 | +0.0123 | +0.1552 |
| first_person_usage_v2 | +0.0828 | +0.0186 | +0.1401 |
| wcl_13 | +0.0793 | +0.0101 | +0.1372 |

wcl_60 corrected r_c = -0.3078 CI=[-0.8733, -0.0348]
