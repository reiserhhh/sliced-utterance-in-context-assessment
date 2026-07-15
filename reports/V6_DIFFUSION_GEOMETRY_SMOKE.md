# SUICA V6 Diffusion-Geometry Audit

## Scope

This is a numeric-only nonlinear alternative to the rejected stable-axis story.
For each fixed `(k, m)` pair, a self-tuning kNN diffusion map is independently
built for early and late residual clouds, then compared under a row-linkage
permutation null. The grid is fixed before inspecting outcomes; no text,
vocabulary, author ID, scale label, or qualitative interpretation is used.

## Frozen settings

- fixed diffusion grid `(neighbours, dimensions)`: `((10, 3), (25, 3), (50, 3), (25, 5))`
- numeric rows per object: at most `128`
- linkage permutations per grid cell: `99`
- familywise correction: Bonferroni across `32` tests
- density normalization: alpha = 0.5; diffusion time = 1

## Results

| object           |   diffusion_neighbours |   diffusion_dimensions |   n_users | status                         |   linear_cka |   linear_cka_bonferroni_p |   rbf_cka |   rbf_cka_bonferroni_p |   distance_spearman |   distance_spearman_bonferroni_p |   neighbour_jaccard |   neighbour_jaccard_bonferroni_p |   early_connected_components |   late_connected_components |   early_eigengap |   late_eigengap |
|:-----------------|-----------------------:|-----------------------:|----------:|:-------------------------------|-------------:|--------------------------:|----------:|-----------------------:|--------------------:|---------------------------------:|--------------------:|---------------------------------:|-----------------------------:|----------------------------:|-----------------:|----------------:|
| static_residual  |                10.0000 |                 3.0000 |       128 | NO_NONLINEAR_GEOMETRY_DETECTED |       0.0266 |                    1.0000 |    0.0411 |                 1.0000 |              0.0228 |                           1.0000 |              0.0435 |                           1.0000 |                       1.0000 |                      1.0000 |           0.0350 |          0.0169 |
| static_residual  |                25.0000 |                 3.0000 |       128 | NO_NONLINEAR_GEOMETRY_DETECTED |       0.0184 |                    1.0000 |    0.0403 |                 1.0000 |             -0.0159 |                           1.0000 |              0.0502 |                           1.0000 |                       1.0000 |                      1.0000 |           0.0279 |          0.0244 |
| static_residual  |                50.0000 |                 3.0000 |       128 | NO_NONLINEAR_GEOMETRY_DETECTED |       0.0282 |                    1.0000 |    0.0490 |                 1.0000 |             -0.0101 |                           1.0000 |              0.0432 |                           1.0000 |                       1.0000 |                      1.0000 |           0.0098 |          0.0188 |
| static_residual  |                25.0000 |                 5.0000 |       128 | NO_NONLINEAR_GEOMETRY_DETECTED |       0.0440 |                    1.0000 |    0.0696 |                 1.0000 |              0.0069 |                           1.0000 |              0.0484 |                           1.0000 |                       1.0000 |                      1.0000 |           0.0283 |          0.0436 |
| dynamic_residual |                10.0000 |                 3.0000 |       128 | NO_NONLINEAR_GEOMETRY_DETECTED |       0.0379 |                    1.0000 |    0.0505 |                 1.0000 |              0.0074 |                           1.0000 |              0.0419 |                           1.0000 |                       1.0000 |                      1.0000 |           0.0252 |          0.0822 |
| dynamic_residual |                25.0000 |                 3.0000 |       128 | NO_NONLINEAR_GEOMETRY_DETECTED |       0.0578 |                    0.6400 |    0.0709 |                 0.3200 |              0.0386 |                           1.0000 |              0.0463 |                           1.0000 |                       1.0000 |                      1.0000 |           0.1077 |          0.0870 |
| dynamic_residual |                50.0000 |                 3.0000 |       128 | NO_NONLINEAR_GEOMETRY_DETECTED |       0.0600 |                    0.6400 |    0.0780 |                 0.3200 |              0.0633 |                           0.6400 |              0.0461 |                           1.0000 |                       1.0000 |                      1.0000 |           0.1044 |          0.0395 |
| dynamic_residual |                25.0000 |                 5.0000 |       128 | NO_NONLINEAR_GEOMETRY_DETECTED |       0.0671 |                    0.6400 |    0.0826 |                 0.6400 |              0.0527 |                           1.0000 |              0.0371 |                           1.0000 |                       1.0000 |                      1.0000 |           0.0424 |          0.0217 |

## Reading rule

A passing row means only that the corresponding **pre-specified nonlinear
geometry** reproduces above a linkage-permutation null. It is not evidence for
a named dynamic axis, personality, causal response operator, or general
manifold. A failed grid does not prove no nonlinear structure exists; it rules
out recovery by this fixed, local diffusion construction at the available
sample and two-half design.
