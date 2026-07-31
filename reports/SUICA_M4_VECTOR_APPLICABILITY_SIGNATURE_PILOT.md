# SUICA M4 Vector Applicability Signature Pilot

## Decision

`VECTOR_SIGNATURE_NOT_RESOLVED`

This post-seal development pilot compares scalar coverage with a fixed
response-safe vector signature `q`. All preprocessing and model fitting are
inside leave-one-group-out folds.

## Diagnostics

- `leave_one_world_out`: {"historical_threshold": {"policy_value_over_b0": 0.012030465078593426, "routing_value_over_forced_r": -0.05278792508739031, "use_r_rate": 0.4}, "scalar": {"harm_auc": 0.45022624434389136, "mae": 0.21414368054815838, "policy_value_over_b0": -0.02182489524735514, "r2": -0.589671875502576, "routing_value_over_forced_r": -0.08664328541333889, "spearman_rho": -0.6365872270795279, "use_r_rate": 0.6666666666666666}, "vector_minus_scalar": {"harm_auc": 0.1380090497737556, "policy_value_over_b0": 0.025070028011204483, "r2": -0.10096049446901811, "routing_value_over_forced_r": 0.02507002801120449, "spearman_rho": 0.4908697632308071}, "vector_q": {"harm_auc": 0.588235294117647, "mae": 0.24271570923578917, "policy_value_over_b0": 0.003245132763849341, "r2": -0.6906323699715942, "routing_value_over_forced_r": -0.0615732574021344, "spearman_rho": -0.14571746384872078, "use_r_rate": 0.8333333333333334}}
- `leave_one_repetition_out`: {"historical_threshold": {"policy_value_over_b0": 0.012030465078593426, "routing_value_over_forced_r": -0.05278792508739031, "use_r_rate": 0.4}, "scalar": {"harm_auc": 0.5339366515837104, "mae": 0.18135213387132348, "policy_value_over_b0": 0.06481839016598374, "r2": -0.1305706758373042, "routing_value_over_forced_r": 0.0, "spearman_rho": -0.10741479816137788, "use_r_rate": 1.0}, "vector_minus_scalar": {"harm_auc": 0.04524886877828049, "policy_value_over_b0": -0.05083339120772276, "r2": -0.3580895393830563, "routing_value_over_forced_r": -0.05083339120772276, "spearman_rho": -0.06588887258389466}, "vector_q": {"harm_auc": 0.5791855203619909, "mae": 0.19637050083075985, "policy_value_over_b0": 0.013984998958260981, "r2": -0.4886602152203605, "routing_value_over_forced_r": -0.05083339120772276, "spearman_rho": -0.17330367074527253, "use_r_rate": 0.5333333333333333}}
- `feature_count`: 24
- `eligible_cells`: 30
- `feature_names`: ["support_minimum_coverage", "support_eval_distance_median", "support_eval_distance_p90", "support_eval_distance_maximum", "support_eval_mean_excess", "tail_fraction", "tail_leverage_mean", "tail_leverage_concentration", "source_linear_cka", "source_procrustes_residual", "source_centroid_distance", "panel_covariance_drift", "panel_centroid_shift", "rb_gram_calibration", "rb_gram_selection", "rb_gram_evaluation", "rb_distance_correlation_evaluation", "shared_rank", "canonical_spectral_entropy", "minimum_support_stability_lcb", "heldout_source_cka", "maximum_condition_number", "maximum_negative_spectral_mass", "maximum_asymmetric_mass"]

## Boundary

Post-seal finite-synthetic pilot only. It can prioritize a fresh vector-applicability experiment but cannot validate a gate or support natural-text, personality, behavioral, clinical, or M4-D claims.
