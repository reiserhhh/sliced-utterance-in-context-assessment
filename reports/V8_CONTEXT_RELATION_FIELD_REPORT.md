# V8-HJIC-1C Context-Fibered Relation Field Report

Status: `V8_HJIC1C_CONTEXT_RELATION_FIELD_PASS`

This experiment estimates context-indexed technical relation fields from two replicated readout families. It computes every aggregate in covariance space before one calibration-frozen whitening map, so the within/between/total decomposition is directly auditable.

## World summary

| world                          |   context_reliability |   relation_license_rate |   global_license_rate |   local_atlas_rate |   mode_license_rate |   context_refusal_rate |   misspecification_rate |
|:-------------------------------|----------------------:|------------------------:|----------------------:|-------------------:|--------------------:|-----------------------:|------------------------:|
| BALANCED_SIGN_REVERSAL         |                1.0000 |                  1.0000 |                0.0000 |             1.0000 |              0.9833 |                 0.0000 |                  0.0000 |
| COLLIDER_OR_DESCENDANT_Z       |                1.0000 |                  0.0000 |                0.0000 |             0.0000 |              0.0000 |                 0.0000 |                  0.0000 |
| COMPOSITION_REWEIGHT           |                1.0000 |                  1.0000 |                0.0000 |             1.0000 |              0.0500 |                 0.0000 |                  0.0000 |
| ECOLOGICAL_ONLY                |                1.0000 |                  0.0000 |                0.0000 |             0.0000 |              0.0000 |                 0.0000 |                  0.0000 |
| GLOBAL_INVARIANT               |                1.0000 |                  1.0000 |                1.0000 |             0.0000 |              1.0000 |                 0.0000 |                  0.0000 |
| LOCAL_LOW_SINGULAR_GAP         |                1.0000 |                  1.0000 |                1.0000 |             0.0000 |              0.0000 |                 0.0000 |                  0.0000 |
| LOCAL_NULL_MULTIPLE_STRATA     |                1.0000 |                  0.0000 |                0.0000 |             0.0000 |              0.0000 |                 0.0000 |                  0.0000 |
| NOISY_CONTEXT_FRONTIER         |                0.2000 |                  0.0000 |                0.0000 |             0.0000 |              0.0000 |                 1.0000 |                  0.0000 |
| NOISY_CONTEXT_FRONTIER         |                0.4000 |                  0.0000 |                0.0000 |             0.0000 |              0.0000 |                 1.0000 |                  0.0000 |
| NOISY_CONTEXT_FRONTIER         |                0.6000 |                  0.0000 |                0.0000 |             0.0000 |              0.0000 |                 1.0000 |                  0.0000 |
| NOISY_CONTEXT_FRONTIER         |                0.8000 |                  1.0000 |                0.0000 |             1.0000 |              0.8833 |                 0.0000 |                  0.0000 |
| NOISY_CONTEXT_FRONTIER         |                1.0000 |                  1.0000 |                0.0000 |             1.0000 |              0.9667 |                 0.0000 |                  0.0000 |
| NONLINEAR_SIMPSON_IN_SIEVE     |                1.0000 |                  0.0000 |                0.0000 |             0.0000 |              0.0000 |                 0.0000 |                  0.0000 |
| NONLINEAR_SIMPSON_OUT_OF_SIEVE |                1.0000 |                  0.0000 |                0.0000 |             0.0000 |              0.0000 |                 0.0000 |                  1.0000 |
| TRUE_CONTEXT_MODERATION        |                1.0000 |                  1.0000 |                0.0167 |             0.9833 |              0.8333 |                 0.0000 |                  0.0000 |

## Headline diagnostics

- Covariance-decomposition q95 error: 1.94111e-15.
- Pooled cell-wise 95% coverage: 0.9427 (18100/19200).
- Global-invariant license/heterogeneity false alarm: 1.0000 / 0.0000.
- Sign-reversal local/cancellation/global license: 1.0000 / 1.0000 / 0.0000.
- Ecological-only between detection/individual false license: 1.0000 / 0.0000.
- Composition attribution: 0.9833.
- Out-of-sieve misspecification detection/final false relation: 1.0000 / 0.0000.
- Low-gap relation/mode license: 1.0000 / 0.0000.
- High-reliability relation / low-reliability refusal: 1.0000 / 1.0000.

## Gates

- `covariance_decomposition`: PASS
- `uncertainty_coverage`: PASS
- `global_invariant`: PASS
- `balanced_sign_reversal`: PASS
- `true_context_moderation`: PASS
- `ecological_only`: PASS
- `composition_reweight`: PASS
- `residualizer_specification`: PASS
- `local_familywise_null`: PASS
- `relation_without_unique_mode`: PASS
- `context_reliability_frontier`: PASS
- `collider_role_refusal`: PASS
- `truth_isolation`: PASS

## Ruling

A total relation is not an average of context correlations. The licensed object is a context-indexed technical field plus separate within-context, between-context, and composition components. A between-context relation cannot be promoted to an individual relation, and a local mode is withheld when its singular direction is underresolved.

Claim boundary: Passing licenses only a synthetic procedure that estimates preregistered context-indexed technical relation fields from replicated mesoscopic readouts, decomposes total covariance into within-context and between-context components, attributes composition shifts, and refuses under context, residualizer, or causal-role underresolution. It does not establish personality, causal deconfounding, human prevalence, language invariance, or clinical validity.
