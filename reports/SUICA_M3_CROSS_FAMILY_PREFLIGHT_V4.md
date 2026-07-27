# SUICA M3 Cross-Family Power Preflight

Decision: `M3_CROSS_FAMILY_V4_READY_FOR_CLEAN_SEAL`

## Purpose

This development-seed run asks whether one generator-blind estimator suite has
enough power to justify an artifact-sealed fresh-seed confirmation. Failure is
a power or specification finding, not evidence against human personality.

## Target summary

| world           | target             |   seeds |   validity_fraction |   refusal_max |   expected_auc |   cheap_auc |   expected_geometry |   cheap_geometry |   heldout_increment |   positive_increment_fraction |   off_target_geometry |   knockout_geometry |
|:----------------|:-------------------|--------:|--------------------:|--------------:|---------------:|------------:|--------------------:|-----------------:|--------------------:|------------------------------:|----------------------:|--------------------:|
| cf_d_copula     | distribution       |      12 |                   1 |             0 |       0.636407 |    0.495905 |            0.331325 |     -0.000761076 |          0.0125961  |                      1        |           nan         |          0.015091   |
| cf_d_multimodal | distribution       |      12 |                   1 |             0 |       0.659845 |    0.498938 |            0.447224 |      0.00026771  |          0.016426   |                      1        |           nan         |          0.00671952 |
| cf_d_skew       | distribution       |      12 |                   1 |             0 |       0.679603 |    0.498383 |            0.468235 |     -0.000967287 |          0.0432161  |                      1        |           nan         |          0.0174014  |
| cf_d_tail       | distribution       |      12 |                   1 |             0 |       0.644567 |    0.496136 |            0.353589 |     -0.00334701  |          0.0164537  |                      1        |           nan         |          0.0108799  |
| cf_kp_arch      | nonlinear_dynamics |      12 |                   1 |             0 |       0.777397 |    0.520491 |            0.829392 |      0.0399927   |          2.2653e-06 |                      0.833333 |           nan         |          0.0298192  |
| cf_kp_cycle     | direction          |      12 |                   1 |             0 |       0.75769  |    0.498585 |            0.865916 |      0.00282385  |          0.0290302  |                      1        |           nan         |          0.00870229 |
| cf_kp_hsmm      | hazard             |      12 |                   1 |             0 |       0.80907  |    0.497994 |            0.875808 |     -0.00291517  |          0.00633295 |                      1        |           nan         |          0.0322345  |
| cf_o_neural     | condition          |      12 |                   1 |             0 |       0.999954 |    0.500992 |            0.981624 |      0.0197657   |          0.417791   |                      1        |             0.0539202 |          0.0411055  |
| cf_o_neural     | partner            |      12 |                   1 |             0 |       0.999958 |    0.500236 |            0.978508 |     -0.0126859   |          0.420525   |                      1        |             0.0499233 |          0.0418303  |
| cf_o_spline     | condition          |      12 |                   1 |             0 |       0.999939 |    0.501174 |            0.988131 |     -1.43204e-05 |          0.48961    |                      1        |             0.0539801 |          0.033657   |
| cf_o_spline     | partner            |      12 |                   1 |             0 |       0.999965 |    0.499632 |            0.988334 |     -0.00937478  |          0.48043    |                      1        |             0.051864  |          0.031212   |
| cf_o_voronoi    | condition          |      12 |                   1 |             0 |       0.999969 |    0.499991 |            0.980129 |     -0.0053192   |          0.335386   |                      1        |             0.0756676 |          0.0253208  |
| cf_o_voronoi    | partner            |      12 |                   1 |             0 |       0.999911 |    0.500598 |            0.976823 |     -0.0270902   |          0.337277   |                      1        |             0.0639209 |          0.0291296  |

## Gates not yet satisfied

- None

## Boundary

No confirmation truth was sealed or opened. Hyperparameters may still change
only in this preflight branch. Human text, psychological constructs, and
clinical use remain outside scope.
