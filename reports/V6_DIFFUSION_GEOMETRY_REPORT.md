# SUICA V6 Diffusion-Geometry Audit

## Scope

This is a numeric-only nonlinear alternative to the rejected stable-axis story.
For each fixed `(k, m)` pair, a self-tuning kNN diffusion map is independently
built for early and late residual clouds, then compared under a row-linkage
permutation null. The grid is fixed before inspecting outcomes; no text,
vocabulary, author ID, scale label, or qualitative interpretation is used.

## Frozen settings

- fixed diffusion grid `(neighbours, dimensions)`: `((10, 3), (25, 3), (50, 3), (25, 5))`
- numeric rows per object: at most `384`
- linkage permutations per grid cell: `999`
- familywise correction: Bonferroni across `32` tests
- density normalization: alpha = 0.5; diffusion time = 1

## Results

| object           |   diffusion_neighbours |   diffusion_dimensions |   n_users | status                         |   linear_cka |   linear_cka_bonferroni_p |   rbf_cka |   rbf_cka_bonferroni_p |   distance_spearman |   distance_spearman_bonferroni_p |   neighbour_jaccard |   neighbour_jaccard_bonferroni_p |   early_connected_components |   late_connected_components |   early_eigengap |   late_eigengap |
|:-----------------|-----------------------:|-----------------------:|----------:|:-------------------------------|-------------:|--------------------------:|----------:|-----------------------:|--------------------:|---------------------------------:|--------------------:|---------------------------------:|-----------------------------:|----------------------------:|-----------------:|----------------:|
| static_residual  |                10.0000 |                 3.0000 |       384 | NO_NONLINEAR_GEOMETRY_DETECTED |       0.0063 |                    1.0000 |    0.0149 |                 1.0000 |              0.0072 |                           1.0000 |              0.0138 |                           1.0000 |                       1.0000 |                      1.0000 |           0.0289 |          0.0331 |
| static_residual  |                25.0000 |                 3.0000 |       384 | NO_NONLINEAR_GEOMETRY_DETECTED |       0.0075 |                    1.0000 |    0.0155 |                 1.0000 |              0.0024 |                           1.0000 |              0.0146 |                           1.0000 |                       1.0000 |                      1.0000 |           0.0126 |          0.0071 |
| static_residual  |                50.0000 |                 3.0000 |       384 | NO_NONLINEAR_GEOMETRY_DETECTED |       0.0138 |                    1.0000 |    0.0277 |                 0.1600 |              0.0080 |                           1.0000 |              0.0151 |                           1.0000 |                       1.0000 |                      1.0000 |           0.0197 |          0.0136 |
| static_residual  |                25.0000 |                 5.0000 |       384 | NO_NONLINEAR_GEOMETRY_DETECTED |       0.0202 |                    0.9600 |    0.0306 |                 0.5120 |              0.0348 |                           1.0000 |              0.0161 |                           1.0000 |                       1.0000 |                      1.0000 |           0.0124 |          0.0063 |
| dynamic_residual |                10.0000 |                 3.0000 |       384 | NO_NONLINEAR_GEOMETRY_DETECTED |       0.0209 |                    0.0640 |    0.0250 |                 0.0960 |              0.0153 |                           1.0000 |              0.0158 |                           1.0000 |                       1.0000 |                      1.0000 |           0.0281 |          0.0236 |
| dynamic_residual |                25.0000 |                 3.0000 |       384 | NO_NONLINEAR_GEOMETRY_DETECTED |       0.0199 |                    0.4160 |    0.0228 |                 0.4480 |              0.0185 |                           1.0000 |              0.0162 |                           1.0000 |                       1.0000 |                      1.0000 |           0.0523 |          0.0403 |
| dynamic_residual |                50.0000 |                 3.0000 |       384 | NO_NONLINEAR_GEOMETRY_DETECTED |       0.0210 |                    0.0960 |    0.0235 |                 0.1280 |              0.0201 |                           1.0000 |              0.0143 |                           1.0000 |                       1.0000 |                      1.0000 |           0.0539 |          0.0508 |
| dynamic_residual |                25.0000 |                 5.0000 |       384 | NO_NONLINEAR_GEOMETRY_DETECTED |       0.0236 |                    0.2560 |    0.0273 |                 0.4160 |              0.0099 |                           1.0000 |              0.0155 |                           1.0000 |                       1.0000 |                      1.0000 |           0.0046 |          0.0318 |

## Reading rule

A passing row means only that the corresponding **pre-specified nonlinear
geometry** reproduces above a linkage-permutation null. It is not evidence for
a named dynamic axis, personality, causal response operator, or general
manifold. A failed grid does not prove no nonlinear structure exists; it rules
out recovery by this fixed, local diffusion construction at the available
sample and two-half design.
