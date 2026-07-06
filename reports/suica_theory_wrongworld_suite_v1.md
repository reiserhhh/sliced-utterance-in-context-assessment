# Wrong-world suite v1 (no-lock theory falsification)

## W_A_choice_null

```json
{
  "sparse": {
    "choice_auc_strict_frozen": 0.0392546875,
    "choice_auc_mid_tie": 0.50005625,
    "axis_retest_median_abs": 0.03887928707982191,
    "pass": true
  },
  "moderate": {
    "choice_auc_strict_frozen": 0.4974984375,
    "choice_auc_mid_tie": 0.49753203125,
    "axis_retest_median_abs": 0.028072791060526736,
    "pass": true
  },
  "criterion": "mid-tie AUC in [0.45,0.55] AND frozen strict AUC <= 0.55 AND axis median |r| < 0.10, at both sparsity levels",
  "pass": true
}
```

## W_B_flesh_null

```json
{
  "rho_raw": 0.6365530277602254,
  "rho_shared_set": 0.4300727434934874,
  "rho_disjoint_set": -0.07115134910056323,
  "cov_raw": 0.3501811317537633,
  "cov_mix": 0.35978236210238207,
  "cov_flesh_hat": 0.00391232461694472,
  "mix_share": 1.0,
  "mediated_total": 0.9888277115407356,
  "criterion": "EXPECT rho_raw AND rho_shared inflated (>0.15) while rho_disjoint <= 0.10 and mix_share >= 0.80",
  "pass": true
}
```

## W_B2_recovery_grid

```json
{
  "grid": [
    {
      "flesh_sd": 0.5,
      "conc": 0.8,
      "target_mix_share": 0.645,
      "estimated_mix_share": 0.697,
      "abs_err": 0.052
    },
    {
      "flesh_sd": 0.5,
      "conc": 1.5,
      "target_mix_share": 0.612,
      "estimated_mix_share": 0.66,
      "abs_err": 0.049
    },
    {
      "flesh_sd": 0.5,
      "conc": 3.0,
      "target_mix_share": 0.477,
      "estimated_mix_share": 0.465,
      "abs_err": 0.012
    },
    {
      "flesh_sd": 1.0,
      "conc": 0.8,
      "target_mix_share": 0.384,
      "estimated_mix_share": 0.423,
      "abs_err": 0.039
    },
    {
      "flesh_sd": 1.0,
      "conc": 1.5,
      "target_mix_share": 0.3,
      "estimated_mix_share": 0.337,
      "abs_err": 0.037
    },
    {
      "flesh_sd": 1.0,
      "conc": 3.0,
      "target_mix_share": 0.179,
      "estimated_mix_share": 0.187,
      "abs_err": 0.008
    },
    {
      "flesh_sd": 1.5,
      "conc": 0.8,
      "target_mix_share": 0.191,
      "estimated_mix_share": 0.217,
      "abs_err": 0.026
    },
    {
      "flesh_sd": 1.5,
      "conc": 1.5,
      "target_mix_share": 0.148,
      "estimated_mix_share": 0.158,
      "abs_err": 0.01
    },
    {
      "flesh_sd": 1.5,
      "conc": 3.0,
      "target_mix_share": 0.064,
      "estimated_mix_share": 0.064,
      "abs_err": 0.001
    }
  ],
  "max_abs_err": 0.052,
  "criterion": "max |est - target| <= 0.10 over 3x3 grid",
  "pass": true
}
```

## W_B2c_class_correlated

```json
{
  "planted_var_f": 1.005,
  "cov_cond_disjoint": 0.996,
  "cov_class_disjoint": 0.89,
  "class_mediation_bias_removed": 0.106,
  "criterion": "|cov_class_disjoint - Var(f)| <= 0.15 AND cov_cond >= cov_class + 0.05",
  "pass": true
}
```

## W_B3_flesh_coupled_choice

```json
{
  "planted": {
    "var_f": 0.879,
    "var_m": 0.191,
    "cov_fm": 0.231,
    "mediated_total_target": 0.426
  },
  "estimated_mediated_total": 0.541,
  "abs_err": 0.115,
  "rho_cond_disjoint_observed": 0.546,
  "note_F3_bias": "disjoint-set retains the 2Cov(f,m) cross-term -> expected to exceed the pure-flesh share 0.574 of stable variance",
  "criterion": "|estimated - target| <= 0.10 under Cov(f,m) != 0",
  "pass": false
}
```

## W_PHASE_centering_boundary

```json
{
  "cells": [
    {
      "regime": "exogenous",
      "delta_cov_centered_minus_raw": 0.01,
      "predicted_delta": 0.0,
      "ok": true
    },
    {
      "regime": "person_k0",
      "delta_cov_centered_minus_raw": -0.316,
      "predicted_delta": -0.304,
      "ok": true
    },
    {
      "regime": "person_k07",
      "delta_cov_centered_minus_raw": -1.583,
      "predicted_delta": -1.294,
      "ok": false
    }
  ],
  "criterion": "sign and magnitude (+/-0.10) match -(Var(m)+2Cov(f,m)) per regime; ~0 under exogenous",
  "pass": false
}
```

## W_C_timescale_alias

```json
{
  "observed_month_lag1": -0.054,
  "analytic_aliased_lag1": 0.161,
  "band": 0.12,
  "criterion": "observed <= analytic + band (no fabrication of month-native persistence)",
  "pass": true
}
```

## W_D_react_norm_only

```json
{
  "fpr_increment_ci_above_zero": 0.01,
  "n_cohorts": 100,
  "criterion": "FPR <= 0.05",
  "pass": true
}
```

## W_E_leak_mask

```json
{
  "slice_leak_detection_rate": 0.5761700336700336,
  "n_surviving_users": 108,
  "recovery_unmasked_maxr": 0.578,
  "recovery_after_mask_maxr": 0.115,
  "null95_at_n_surv": 0.192,
  "criterion": "positive control unmasked > 0.30; after mask <= null95 among surviving users (the production estimand: masked slices are dropped)",
  "pass": true
}
```


**ALL_PASS = False**
