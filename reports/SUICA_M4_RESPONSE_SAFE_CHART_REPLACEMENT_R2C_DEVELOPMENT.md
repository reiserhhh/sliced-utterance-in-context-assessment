# SUICA M4-C.3.5-R2C Abstention-Aware Policy Development

## Decision

`M4_C35_R2C_DEVELOPMENT_COMPLETE`

The frozen policy uses RCCA (`R`) only when the pre-response applicability
check accepts; otherwise it uses the old chart (`B0`). The primary development
estimand is full-population policy value, not accepted-stratum performance.

## Diagnostics

- `policy_gain`: 0.12055119568488555
- `policy_gain_lcb`: 0.06875708961270462
- `policy_recovery`: 0.9011143989340531
- `policy_recovery_lcb`: 0.8647838113262477
- `policy_recovery_valid_rate`: 1.0
- `policy_accessible_efficiency`: 1.0042135914841097
- `policy_accessible_efficiency_lcb`: 0.9896841433585029
- `policy_efficiency_valid_rate`: 1.0
- `policy_oracle_noninferiority_lcb`: -0.0017964210477579012
- `positive_repetitions`: 2
- `eligible_worlds`: {"endogenous_creation_expansion": {"acceptance_rate": 1.0, "headroom_lcb": 0.03538440169456236, "policy_gain": 0.21060490311827224, "policy_gain_lcb": 0.03944023890547976, "positive_repetitions": 2, "ratio_valid_bootstrap_rate": 1.0, "recovery_lcb": 0.9812570286142697}, "endogenous_source_partition_matched": {"acceptance_rate": 1.0, "headroom_lcb": 0.1413848183901657, "policy_gain": 0.13694006528231117, "policy_gain_lcb": 0.1277380373637057, "positive_repetitions": 2, "ratio_valid_bootstrap_rate": 1.0, "recovery_lcb": 0.9034777483053356}, "source_rotated_feedback": {"acceptance_rate": 1.0, "headroom_lcb": 0.03371067435238584, "policy_gain": 0.014108618654073257, "policy_gain_lcb": 0.007528300576429059, "positive_repetitions": 2, "ratio_valid_bootstrap_rate": 1.0, "recovery_lcb": 0.2233209723939044}}
- `history_policy_gain_lcb`: -0.0032363358566566136
- `boundary_policy_oracle_fidelity_lcb`: 0.001423709979859411
- `hazard_relative_degradation_ucb`: -0.03305195590597643
- `null_false_successes`: 0
- `null_trials`: 6
- `null_false_success_wilson_upper`: 0.39033428790216534
- `acceptance_rate_by_stratum`: {"boundary": 1.0, "eligible": 1.0, "null": 1.0, "sentinel": 1.0}
- `main_acceptance_rate`: 1.0
- `eligible_acceptance_rate`: 1.0
- `eligible_accepted_cells`: 6
- `eligible_refused_cells`: 0
- `forced_r_gain`: 0.12055119568488555
- `routing_gain_over_forced_r`: 0.0
- `accepted_stratum_forced_gain`: 0.12055119568488555
- `refused_stratum_forced_gain`: NaN
- `refused_cells`: []
- `minimum_coverage`: 0.9375
- `minimum_margin`: 0.13749999999999996
- `maximum_basis_replay_error`: 0.0
- `maximum_policy_identity_error`: 0.0

## Candidate gates (not confirmation)

- PASS: `policy_gain`
- PASS: `policy_recovery`
- PASS: `policy_efficiency`
- PASS: `history_safety`
- PASS: `boundary_fidelity`
- PASS: `hazard_safety`
- PASS: `null_specificity`

No abstention budget is registered in this development run. These checks may
design a fresh confirmation but cannot themselves produce GO.

## Boundary

Fresh-seed finite-synthetic R2C development only. This run characterizes a pre-response RCCA/B0 fallback policy and may design, but cannot confirm, an external abstention budget. It licenses no natural-text, personality, clinical, or M4-D claim.
