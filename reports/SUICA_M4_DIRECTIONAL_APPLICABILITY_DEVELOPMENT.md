> **Audit correction.** The sealed analyzer parsed the literal world type `null` as pandas NA and therefore reported zero null cells. This report changes only CSV parsing to `keep_default_na=False`; all frozen models, features, thresholds, cells, outcomes, and gates are unchanged. The raw parser-stop report is preserved separately.

# SUICA M4 Fixed-Coverage Directional Applicability

## Decision

`M4_C35_PRE_RESPONSE_DOMAIN_NOT_IDENTIFIED`

This fresh development experiment holds exact support amount fixed while
changing only the pre-response direction of departure. It compares the
historical scalar threshold (`S0`), a fold-local scalar learner (`S1`), and
the preregistered vector signature (`Q`).

## Diagnostics

- `integrity`: {"main_cells": 360, "maximum_basis_replay_error": 0.0, "maximum_null_absolute_gain": 0.0, "maximum_response_identity_error": 0.0, "maximum_signature_replay_error": 0.0, "null_cells": 72, "sealed_cells": 432}
- `leave_one_world_out`: {"Q": {"harm_auc": 0.532933160285529, "harm_auc_bootstrap_valid_rate": 1.0, "harm_auc_lcb": 0.4644183627989898, "harm_auc_ucb": 0.6561566443198404, "mae": 0.22157235166370254, "policy_value_lcb": 0.017336515344783268, "policy_value_over_b0": 0.06783550283619232, "policy_value_ucb": 0.11193082605841366, "r2": -1.616017216833927, "routing_value_lcb": -0.04171121065506091, "routing_value_over_forced_r": -0.024326940142448156, "routing_value_ucb": -0.005258520074696589, "spearman_rho": 0.1613971201930879, "use_r_rate": 0.6666666666666666}, "Q_minus_S1": {"harm_auc_delta": -0.002778228423101825, "policy_value_delta": -0.024326940142448156, "policy_value_delta_lcb": -0.042469653563904884, "policy_value_delta_ucb": -0.0059672435778719305, "routing_value_delta": -0.024326940142448156, "routing_value_delta_lcb": -0.041927795429466536, "routing_value_delta_ucb": -0.005617315245657489}, "S0_historical": {"policy_value_lcb": 0.011627151025057167, "policy_value_over_b0": 0.04181686970370982, "policy_value_ucb": 0.06911791331516534, "routing_value_lcb": -0.07312474887415461, "routing_value_over_forced_r": -0.05034557327493064, "routing_value_ucb": -0.026055223930042247, "use_r_rate": 0.5555555555555556}, "S1": {"harm_auc": 0.5357113887086308, "harm_auc_bootstrap_valid_rate": 1.0, "harm_auc_lcb": 0.5022198987542277, "harm_auc_ucb": 0.5613881496007844, "mae": 0.14407127326483732, "policy_value_lcb": 0.037149609468886145, "policy_value_over_b0": 0.09216244297864046, "policy_value_ucb": 0.13948298281130006, "r2": -0.021421880295406703, "routing_value_lcb": 0.0, "routing_value_over_forced_r": 0.0, "routing_value_ucb": 0.0, "spearman_rho": -0.10717285539153605, "use_r_rate": 1.0}}
- `leave_one_repetition_out`: {"Q": {"harm_auc": 0.5120051914341337, "harm_auc_bootstrap_valid_rate": 1.0, "harm_auc_lcb": 0.4769547325102881, "harm_auc_ucb": 0.5878555658294671, "mae": 0.15637118317695156, "policy_value_lcb": 0.0346505742217963, "policy_value_over_b0": 0.07872341171875359, "policy_value_ucb": 0.12181798924958571, "r2": -0.19544917537661943, "routing_value_lcb": -0.03138321237585942, "routing_value_over_forced_r": -0.01343903125988687, "routing_value_ucb": 0.00018969199249947548, "spearman_rho": 0.026862354097987918, "use_r_rate": 0.85}, "Q_minus_S1": {"harm_auc_delta": 0.025997728747566562, "policy_value_delta": -0.01343903125988687, "policy_value_delta_lcb": -0.032452822244600305, "policy_value_delta_ucb": 9.559305815990218e-05, "routing_value_delta": -0.01343903125988687, "routing_value_delta_lcb": -0.030736128955714506, "routing_value_delta_ucb": 0.0003005571374555367}, "S0_historical": {"policy_value_lcb": 0.012087764162445818, "policy_value_over_b0": 0.04181686970370982, "policy_value_ucb": 0.06818457428478376, "routing_value_lcb": -0.07336490719094987, "routing_value_over_forced_r": -0.05034557327493064, "routing_value_ucb": -0.026323104344155836, "use_r_rate": 0.5555555555555556}, "S1": {"harm_auc": 0.48600746268656714, "harm_auc_bootstrap_valid_rate": 1.0, "harm_auc_lcb": 0.45772784928270666, "harm_auc_ucb": 0.5343578079214194, "mae": 0.14542932069151815, "policy_value_lcb": 0.037233547540910523, "policy_value_over_b0": 0.09216244297864046, "policy_value_ucb": 0.1400909582729062, "r2": -0.05119324270757164, "routing_value_lcb": 0.0, "routing_value_over_forced_r": 0.0, "routing_value_ucb": 0.0, "spearman_rho": -0.25687503396865774, "use_r_rate": 1.0}}
- `feature_count`: 24
- `feature_names`: ["canonical_spectral_entropy", "heldout_source_cka", "maximum_asymmetric_mass", "maximum_condition_number", "maximum_negative_spectral_mass", "minimum_support_stability_lcb", "panel_centroid_shift", "panel_covariance_drift", "rb_distance_correlation_evaluation", "rb_gram_calibration", "rb_gram_evaluation", "rb_gram_selection", "shared_rank", "source_centroid_distance", "source_linear_cka", "source_procrustes_residual", "support_eval_distance_maximum", "support_eval_distance_median", "support_eval_distance_p90", "support_eval_mean_excess", "support_minimum_coverage", "tail_fraction", "tail_leverage_concentration", "tail_leverage_mean"]
- `lowo_pass`: false
- `loro_pass`: false

## Direction summary

|   target_count | direction_mode      |   forced_r_gain |   oracle_error |   harmful |
|---------------:|:--------------------|----------------:|---------------:|----------:|
|                |                     |          0.0762 |         0.0013 |    0.0250 |
|        12.0000 | radial_concentrated |          0.1377 |         0.1310 |    0.2750 |
|        12.0000 | radial_dispersed    |          0.1254 |         0.1408 |    0.2500 |
|        12.0000 | source_asymmetric   |          0.0975 |         0.2276 |    0.2750 |
|        12.0000 | tangential_rotation |          0.0925 |         0.1631 |    0.2250 |
|        13.0000 | radial_concentrated |          0.1144 |         0.1333 |    0.2500 |
|        13.0000 | radial_dispersed    |          0.1003 |         0.1471 |    0.3000 |
|        13.0000 | source_asymmetric   |          0.0325 |         0.2126 |    0.4250 |
|        13.0000 | tangential_rotation |          0.0529 |         0.1781 |    0.2750 |

## World summary

| world                               |   forced_r_gain |   harmful |
|:------------------------------------|----------------:|----------:|
| endogenous_creation_expansion       |          0.1091 |    0.2222 |
| endogenous_source_partition_matched |          0.0783 |    0.3056 |
| history_gated_ecology               |          0.0422 |    0.3056 |
| selection_creation_compensation     |          0.1534 |    0.1528 |
| source_rotated_feedback             |          0.0778 |    0.2917 |

## Interpretation

The present pre-response signature does not identify a safe, positive-utility R/B0 routing domain. Stop threshold tuning and retain direction as descriptive applicability metadata.

## Boundary

Finite-synthetic fixed-coverage development only. No natural-text, personality, behavioral, diagnostic, clinical, or M4-D claim.
