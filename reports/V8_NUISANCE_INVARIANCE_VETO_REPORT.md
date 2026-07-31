# V8-HJIC-1B Nuisance-Invariance Veto Report

Status: `V8_HJIC1B_NUISANCE_INVARIANCE_VETO_PASS`

HJIC-1A remains preserved as a partial result. This follow-up tests whether a material, permutation-supported raw-versus-conditioned relation shift can veto an otherwise stable global relation.

## World summary

| world                      |   relation_license_rate |   mode_license_rate |   nuisance_veto_rate |   support_failure_rate |   mean_truth_fidelity |
|:---------------------------|------------------------:|--------------------:|---------------------:|-----------------------:|----------------------:|
| COLLIDER_OR_DESCENDANT_Z   |                  0.0000 |              0.0000 |               1.0000 |                 0.0000 |              nan      |
| COMMON_NUISANCE            |                  0.0000 |              0.0000 |             nan      |                 1.0000 |              nan      |
| CORRELATED_REPLICATE_ERROR |                  0.0000 |              0.0000 |               0.0000 |                 0.0500 |              nan      |
| LOCALIZED_SIMPSON          |                  0.0000 |              0.0000 |               1.0000 |                 0.0000 |                0.9790 |
| LOW_SINGULAR_GAP           |                  1.0000 |              0.0000 |               0.0000 |                 0.0000 |                0.9829 |
| NULL_HIGH_DIM_NUISANCE     |                  1.0000 |              0.6333 |               0.0000 |                 0.0000 |                0.9768 |
| PRIVATE_AXES               |                  0.0000 |              0.0000 |               0.0000 |                 0.0000 |              nan      |
| SHARED_LATENT              |                  0.9833 |              0.8000 |               0.0000 |                 0.0000 |                0.9773 |
| SIMPSON_MIXTURE            |                  0.0000 |              0.0000 |               1.0000 |                 0.0000 |                0.9990 |
| WEAK_RELATION              |                  0.0000 |              0.0000 |               0.0167 |                 0.0000 |                0.1404 |

## Diagnostics

- Shared relation/mode license: 0.9833 / 0.8000.
- High-dimensional-null relation license: 1.0000; positive-world nuisance veto: 0.0000.
- Licensed positive truth fidelity: 1.0000 (n=119).
- Low-gap relation/mode license: 1.0000 / 0.0000.
- Simpson detection/final license: 1.0000 / 0.0000.
- Collider sensitivity/final license: 1.0000 / 0.0000.
- Weak relation final license/nuisance veto: 0.0000 / 0.0167.

## Gates

- `shared_relation`: PASS
- `shared_mode`: PASS
- `high_dim_null_safety`: PASS
- `licensed_truth_fidelity`: PASS
- `basic_negative_refusal`: PASS
- `low_gap_relation_without_mode`: PASS
- `simpson_veto`: PASS
- `collider_sensitivity_veto`: PASS
- `weak_relation_classification`: PASS
- `truth_isolation`: PASS

## Ruling

Condition sensitivity is a veto on a global invariant relation, not evidence that conditioning recovered causal truth. Weak relations, unique-mode failure, and nuisance sensitivity remain distinct refusal types.

Claim boundary: Passing licenses only an observable veto for materially condition-sensitive relation claims under a frozen nuisance definition and residualizer. It does not identify causality, decide whether Z is confounder, mediator, moderator, collider, or construct signal, or establish human personality validity.
