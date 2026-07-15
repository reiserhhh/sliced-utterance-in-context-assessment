# SUICA V6 Cached Numeric Geometry Audit

## Scope

This is an ID-free numeric audit of already constructed V6 objects. The tested
quantity is relational geometry, not a named factor, trait, or personality
score. The null retains both early and late point clouds but permutes the row
linkage between them.

## Frozen settings

- linkage permutations: `999`
- descriptive subsamples: `128`
- familywise correction: Bonferroni across `9` object-metric tests
- cached sensitivity mask: none
- raw text, tokens, terms, author IDs, and external labels: not read

## Results

| object          |   n_users |   n_features | status                        |   linear_cka |   linear_cka_bonferroni_p |   distance_spearman |   distance_spearman_bonferroni_p |   neighbour_jaccard |   neighbour_jaccard_bonferroni_p |   effective_rank_early |   effective_rank_late |   intrinsic_dimension_early |   intrinsic_dimension_late |   spectrum_cosine |
|:----------------|----------:|-------------:|:------------------------------|-------------:|--------------------------:|--------------------:|---------------------------------:|--------------------:|---------------------------------:|-----------------------:|----------------------:|----------------------------:|---------------------------:|------------------:|
| hybrid_full     |      1381 |           24 | PARTIAL_LINKAGE_GEOMETRY_ONLY |       0.0166 |                    1.0000 |              0.2326 |                           0.0090 |              0.0110 |                           0.0090 |                23.1849 |               23.2090 |                     18.5089 |                    18.4475 |            0.9997 |
| hybrid_factor   |      1381 |            2 | PARTIAL_LINKAGE_GEOMETRY_ONLY |       0.0011 |                    1.0000 |              0.0491 |                           0.0180 |              0.0067 |                           1.0000 |                 1.9963 |                1.9955 |                      2.0000 |                     2.0000 |            1.0000 |
| hybrid_residual |      1381 |           24 | PARTIAL_LINKAGE_GEOMETRY_ONLY |       0.0153 |                    1.0000 |              0.2287 |                           0.0090 |              0.0110 |                           0.0090 |                21.3438 |               21.3649 |                     17.3656 |                    17.6981 |            0.9998 |

## Reading rule

`LINKAGE_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN` requires all three linkage
metrics to survive the stated familywise correction. It means only that the
numeric relation among rows reproduces above an arbitrary pairing; it does not
identify the source of that relation or promote the object to a psychological
construct. `PARTIAL_LINKAGE_GEOMETRY_ONLY` is descriptive, not confirmatory.
