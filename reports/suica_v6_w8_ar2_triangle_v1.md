# V6-W8 -- AR(2) texture-triangle fit of the three hybrid functionals (Essays, label-free)

Registered commit: e04d5e0 (F12.9, docs/SUICA_THEORY_FORMAL_NOTES_V3.md)

n_texts=1349 (5<=m<=12), n_windows=8793; excluded m>12: 12; m<5: 948; subsample-gap: 0.

Grid: 6564 stationarity-triangle points (91x91, step 0.02), Yule-Walker ladders to lag 11, exact-on-composition expected functionals; cache 0.002s. Fit: weighted grid LS on (r_c, rho_pihalf, rho_pi); weights = 300-draw bootstrap sds; 3 moments, 2 parameters, 1 dof.

## Fits (sorted by overidentification residual, worst first)

| construct | a1 | CI | a2 | CI | resid | CI | drops |
|---|---|---|---|---|---|---|---|
| wcl_03 | +0.06 | [-0.14, +0.38] | +0.00 | [-0.10, +0.12] | 0.830 | [0.046, 3.721] | 0 |
| first_person_usage_v2 | +0.08 | [-0.14, +0.33] | +0.00 | [-0.12, +0.12] | 0.524 | [0.022, 3.399] | 0 |
| tension_core_v2 | +0.08 | [-0.14, +0.36] | +0.06 | [-0.06, +0.20] | 0.293 | [0.017, 1.521] | 0 |
| wcl_13 | +0.08 | [-0.10, +0.34] | +0.00 | [-0.10, +0.13] | 0.154 | [0.016, 1.715] | 0 |
| wcl_36 | +0.18 | [-0.06, +0.54] | +0.04 | [-0.08, +0.18] | 0.125 | [0.016, 1.422] | 0 |
| wcl_07 | -0.14 | [-0.36, +0.17] | -0.16 | [-0.28, -0.02] | 0.089 | [0.006, 1.468] | 0 |
| wcl_20 | +0.68 | [+0.04, +0.72] | +0.30 | [+0.04, +0.32] | 0.084 | [0.010, 4.114] | 0 |
| wcl_60 | -0.56 | [-0.76, -0.18] | -0.26 | [-0.39, -0.02] | 0.080 | [0.003, 1.759] | 29 |
| wcl_15 | +0.06 | [-0.23, +0.42] | +0.00 | [-0.16, +0.15] | 0.072 | [0.011, 1.463] | 0 |
| wcl_35 | +0.28 | [-0.04, +0.76] | +0.08 | [-0.08, +0.24] | 0.067 | [0.007, 1.253] | 0 |
| wcl_11 | +0.32 | [-0.07, +0.74] | +0.14 | [-0.04, +0.29] | 0.052 | [0.005, 1.728] | 0 |
| wcl_02 | +0.02 | [-0.27, +0.48] | -0.04 | [-0.18, +0.15] | 0.046 | [0.009, 1.471] | 0 |
| wcl_45 | +0.00 | [-0.20, +0.30] | -0.02 | [-0.14, +0.13] | 0.044 | [0.011, 0.877] | 0 |
| wcl_25 | +0.12 | [-0.21, +0.70] | +0.06 | [-0.12, +0.30] | 0.040 | [0.006, 0.837] | 0 |
| novelty_play_v2 | +0.08 | [-0.18, +0.47] | +0.00 | [-0.14, +0.14] | 0.039 | [0.005, 0.550] | 0 |
| wcl_54 | +0.14 | [-0.10, +0.63] | +0.08 | [-0.04, +0.27] | 0.017 | [0.011, 1.233] | 0 |
| directive_action_v2 | +0.04 | [-0.26, +0.41] | +0.02 | [-0.14, +0.18] | 0.013 | [0.008, 0.872] | 0 |
| wcl_23 | +0.10 | [-0.28, +0.64] | +0.08 | [-0.12, +0.34] | 0.012 | [0.004, 1.035] | 0 |
| wcl_22 | +0.24 | [+0.02, +0.68] | +0.12 | [+0.00, +0.30] | 0.006 | [0.006, 1.739] | 0 |

Median residual = 0.067; wcl_60 residual = 0.080 (rank 8/19, 1 = worst; ratio to median = 1.18).

Registered leans: (a) carry-over a1~+0.1/a2~0 small resid; (b) wcl_20 a2~+0.15, wcl_07 a2~-0.15..-0.2, small resids; (c) wcl_60 worst resid (sharp MA test); (d) one-step echoes resid > carry-over set. KILL: wcl_60 resid ~ median.
