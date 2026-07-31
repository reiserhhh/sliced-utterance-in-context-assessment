# SUICA M4-C.3 Physical-Edge Composition Audit

## Decision

`M4_C3_NO_GO_ERROR_ATTRIBUTION`

M4-C.2 established strong atomic action transport but failed its composite
loop and repetition gates. M4-C.3 does not reopen that result. It maps each
estimated edge into the shared physical condition space and constructs all
eight products

\[
L_{ijk}=A_iR_jD_k,\qquad i,j,k\in\{O,D\}.
\]

A Shapley decomposition attributes oracle-to-discovered loop loss to the
creation, response, and choice edges and their order-independent interactions.
Path-conditioned error budgets are evaluated only on the registered query
bank. A finite nonlinear intervention is compared against the Jacobian
product so estimator error is not confused with linearization error.

## Frozen design

- version: `suica-m4-c3-physical-edge-composition-v1`
- repetitions: `8`
- worlds: `endogenous_source_partition_matched, endogenous_creation_expansion, source_rotated_feedback, history_gated_ecology, selection_creation_compensation`
- primary rank: `12`
- rank diagnostic arms: `[4, 8, 12]`
- fault strength: `0.35`

## Diagnostics

- `fault_localization_accuracy`: 1.0
- `fault_attribution_margin_lcb`: 0.029274380888817734
- `null_false_attribution_rate`: 0.0
- `error_budget_loss_spearman`: 0.7264181903422411
- `oracle_jacobian_finite_geometry`: 0.9984527569628712
- `discovered_jacobian_finite_geometry`: 0.9982854046461409
- `finite_loop_transport_geometry`: 0.6266549527979203
- `jacobian_loop_transport_geometry`: 0.6278067176863532
- `maximum_projection_error`: 6.641848843487047e-15
- `maximum_reconstruction_error`: 9.857920392548963e-15
- `basis_invariance_max_difference`: 4.668143857577967e-10
- `passing_repetitions`: 4
- `required_passing_repetitions`: 6
- `rank_loop_geometry`: {"12": 0.5700132767925146, "4": 0.3816441523812397, "8": 0.6320543369596765}
- `mean_shapley_loss`: {"choice": 0.07690504694443315, "creation": 0.243227435790537, "response": 0.052060799578676695}

## Gates

- PASS: `fault_localization`
- PASS: `fault_margin`
- PASS: `null_attribution`
- FAIL: `error_budget`
- PASS: `linearization_control`
- PASS: `physical_reconstruction`
- PASS: `basis_invariance`
- FAIL: `repetition_stability`

## Boundary

Finite synthetic decomposition of physical choice, response, and creation edges only. It explains or localizes composite loop loss; it does not convert M4-C.2 to a pass, identify personality, validate natural text, or authorize M4-D.

This audit can localize why the M4-C.2 plug-in loop failed. It cannot turn the
frozen V2 NO-GO into a pass. M4-D remains blocked.
