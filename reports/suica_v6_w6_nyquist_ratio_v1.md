# V6-W6a -- Normalized Nyquist ratio rho_pi = f(pi)/gamma0 (Essays, label-free)

Registered commit: ed971f1 (F12.7, docs/SUICA_THEORY_FORMAL_NOTES_V3.md)

n_texts=1349 (5<=m<=12), n_windows=8793; excluded m>12: 12; m<5: 948; subsample-gap: 0. Per-h pairs: h=0: 6095, h=1: 4746, h=2: 3397, h=3: 2048, h=4: 1136.

## Mode decision

HEADLINE = registered FLAGGED lag-2-truncated mode. Trigger: the 5-moment gamma0 left-functional is ill-conditioned (|w_g0| = 70.4 vs |w_fpi| = 4.10; centering near-null projection), giving a negative point gamma0 (wcl_60, wcl_07) and max diff vs W3 Gamma0 of 1.139. Truncated mode: |w_fpi3| = 0.89, |w_g03| = 5.77, cond(M3) = 110; all gamma0 positive; max diff vs W3 = 0.356 (median 0.081).

## Reference lines (rho_pi)

| process | asymptotic | exact 5-mom (this composition) | exact truncated |
|---|---|---|---|
| white | 1.000 | 1.000 | 1.000 |
| ma1_.34 | 1.610 | 1.610 | 1.610 |
| ar1_.1 | 0.818 | 0.818 | 0.821 |
| ar2even_.2 | 1.500 | 1.432 | 1.321 |

## rho_pi per construct (headline truncated mode, sorted descending)

| construct | rho_pi | CI 2.5% | CI 97.5% | f_pi | gamma0 | gamma0 - W3 | drops | 5-mom rho_pi [CI] |
|---|---|---|---|---|---|---|---|---|
| wcl_60 | 2.5128 | 1.2801 | 7.3541 | 0.5573 | 0.2218 | -0.1483 | 40 | -4.271 [0.514, 10.061] |
| wcl_23 | 1.1100 | 0.8447 | 1.6220 | 0.7679 | 0.6918 | -0.0117 | 0 | 0.966 [0.395, 4.854] |
| wcl_45 | 0.9940 | 0.8169 | 1.2612 | 0.7154 | 0.7197 | -0.0807 | 0 | 0.882 [0.447, 5.233] |
| directive_action_v2 | 0.9678 | 0.7566 | 1.3081 | 0.7981 | 0.8246 | +0.0165 | 0 | 0.828 [0.398, 4.918] |
| wcl_54 | 0.9498 | 0.7924 | 1.1773 | 0.8744 | 0.9206 | +0.0725 | 0 | 0.895 [0.443, 4.207] |
| wcl_02 | 0.9345 | 0.6841 | 1.3566 | 0.7619 | 0.8153 | -0.1332 | 0 | 0.628 [0.231, 5.224] |
| tension_core_v2 | 0.9036 | 0.7409 | 1.1099 | 0.9084 | 1.0053 | +0.1728 | 0 | 0.654 [0.425, 1.370] |
| wcl_07 | 0.8922 | 0.5961 | 1.5850 | 0.6538 | 0.7328 | -0.1471 | 0 | -4.163 [0.443, 7.498] |
| wcl_25 | 0.8815 | 0.6743 | 1.2922 | 0.8358 | 0.9482 | +0.1137 | 0 | 0.692 [0.342, 3.793] |
| novelty_play_v2 | 0.8697 | 0.6785 | 1.1424 | 0.8007 | 0.9206 | -0.0378 | 0 | 0.770 [0.372, 4.119] |
| wcl_03 | 0.8633 | 0.7168 | 1.0583 | 0.6443 | 0.7463 | -0.0042 | 0 | 0.468 [0.307, 0.987] |
| wcl_15 | 0.8617 | 0.6663 | 1.2974 | 0.7224 | 0.8383 | +0.0390 | 0 | 1.647 [0.325, 7.403] |
| first_person_usage_v2 | 0.8408 | 0.7136 | 1.0152 | 0.5734 | 0.6819 | -0.0079 | 0 | 0.525 [0.326, 1.429] |
| wcl_11 | 0.8315 | 0.6415 | 1.1197 | 0.9447 | 1.1361 | +0.1477 | 0 | 0.542 [0.280, 2.384] |
| wcl_22 | 0.8081 | 0.6921 | 0.9443 | 0.8280 | 1.0246 | +0.2421 | 0 | 0.868 [0.466, 4.303] |
| wcl_13 | 0.8066 | 0.6886 | 0.9585 | 0.7248 | 0.8987 | +0.0553 | 0 | 0.687 [0.387, 2.363] |
| wcl_20 | 0.7699 | 0.6445 | 0.9673 | 0.9959 | 1.2936 | +0.3560 | 0 | 0.498 [0.286, 1.632] |
| wcl_36 | 0.7683 | 0.6474 | 0.9304 | 0.6522 | 0.8489 | +0.0744 | 0 | 0.619 [0.375, 2.140] |
| wcl_35 | 0.7524 | 0.6071 | 0.9696 | 0.6922 | 0.9201 | +0.0895 | 0 | 0.514 [0.284, 1.818] |

Bootstrap: 500 draws, seed 20260712; drop guard gamma0 <= 0.05 per construct per mode. Total drops: truncated 40, 5-moment 1061.

