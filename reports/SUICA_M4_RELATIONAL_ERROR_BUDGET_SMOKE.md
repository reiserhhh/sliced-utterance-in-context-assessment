# SUICA M4-C.3.1 Relational Error Budget

## Decision

`M4_C31_RELATIONAL_THIRD_ORDER_INTERACTION`

The M4-C.3 author-wise Frobenius budget did not share the estimand of the
author-relation loop gate. M4-C.3.1 first quotients common author mode, then
works on the upper-triangle distance vector of all eight mixed physical loops.

For midrank vectors \(z_S\), the registered loss has the exact form

\\[
1-\\rho_S(d_O,d_S)=\\frac12\\|z_O-z_S\\|_2^2.
\\]

Single-edge and pairwise Harsanyi terms predict the DDD distance vector without
using DDD. The residual is the irreducible three-edge interaction.

## Frozen design

- version: `suica-m4-c31-relational-error-budget-smoke-v1`
- repetitions: `1`
- worlds: `endogenous_source_partition_matched, endogenous_creation_expansion, source_rotated_feedback, history_gated_ecology, selection_creation_compensation`
- common-mode quotient: author centering
- primary endpoint: pairwise-distance midrank loss
- secondary endpoint: normalized centered Gram/CKA

## Diagnostics

- `pooled_second_order_loss_spearman`: 0.9030303030303028
- `cluster_bootstrap_spearman_lcb`: 0.45828025477707013
- `leave_one_repetition_out_min_spearman`: 0.0
- `normalized_loss_mae`: 0.3949194929750524
- `maximum_spearman_identity_error`: 2.220446049250313e-16
- `maximum_mobius_reconstruction_error`: 1.3877787807814457e-17
- `maximum_shapley_efficiency_error`: 3.3306690738754696e-16
- `maximum_similarity_invariance_error`: 0.0
- `fault_localization_accuracy`: 1.0
- `fault_attribution_margin_lcb`: 0.026554004743659678
- `null_false_attribution_rate`: 0.0
- `median_third_order_relative_norm`: 0.15985093534266898
- `fault_third_order_95pct`: 0.0
- `third_order_excess`: 0.15985093534266898
- `mean_actual_loss`: 0.4739831557809874
- `mean_predicted_second_order_loss`: 0.3798576902025178
- `mean_gram_cka`: 0.7401219969121591
- `mean_shapley_loss`: {"choice": 0.09370878461793833, "creation": 0.31714690615879065, "response": 0.06312746500425813}

## Gates

- PASS: `spearman_identity`
- PASS: `mobius_reconstruction`
- PASS: `similarity_invariance`
- PASS: `shapley_efficiency`
- PASS: `pooled_prediction`
- FAIL: `cluster_stability`
- FAIL: `leave_one_out_stability`
- FAIL: `prediction_error`
- PASS: `fault_localization`
- PASS: `fault_margin`
- PASS: `null_attribution`

## Boundary

Finite synthetic relation-space accounting only. It can coordinate M4-C.2 loop loss in the same author-relation geometry, but cannot change prior NO-GO decisions, establish causality, identify personality, validate natural text, or authorize M4-D.

M4-C.2 and M4-C.3 remain frozen NO-GO results. M4-D remains blocked.
