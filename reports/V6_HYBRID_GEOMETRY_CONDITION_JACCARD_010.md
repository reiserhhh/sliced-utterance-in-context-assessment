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
- cached sensitivity mask: `condition_jaccard_ge_010`
- raw text, tokens, terms, author IDs, and external labels: not read

## Results

| object          |   n_users |   n_features | status                        |   linear_cka |   linear_cka_bonferroni_p |   distance_spearman |   distance_spearman_bonferroni_p |   neighbour_jaccard |   neighbour_jaccard_bonferroni_p |   effective_rank_early |   effective_rank_late |   intrinsic_dimension_early |   intrinsic_dimension_late |   spectrum_cosine |
|:----------------|----------:|-------------:|:------------------------------|-------------:|--------------------------:|--------------------:|---------------------------------:|--------------------:|---------------------------------:|-----------------------:|----------------------:|----------------------------:|---------------------------:|------------------:|
| hybrid_full     |      1207 |           24 | PARTIAL_LINKAGE_GEOMETRY_ONLY |       0.0194 |                    1.0000 |              0.2578 |                           0.0090 |              0.0134 |                           0.0090 |                23.1098 |               23.1373 |                     18.2437 |                    18.2793 |            0.9990 |
| hybrid_factor   |      1207 |            2 | PARTIAL_LINKAGE_GEOMETRY_ONLY |       0.0023 |                    1.0000 |              0.0533 |                           0.0180 |              0.0087 |                           1.0000 |                 1.9936 |                1.9954 |                      2.0000 |                     2.0000 |            0.9999 |
| hybrid_residual |      1207 |           24 | PARTIAL_LINKAGE_GEOMETRY_ONLY |       0.0180 |                    1.0000 |              0.2528 |                           0.0090 |              0.0135 |                           0.0090 |                21.2744 |               21.2983 |                     17.2768 |                    17.4132 |            0.9990 |

## Reading rule

`LINKAGE_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN` requires all three linkage
metrics to survive the stated familywise correction. It means only that the
numeric relation among rows reproduces above an arbitrary pairing; it does not
identify the source of that relation or promote the object to a psychological
construct. `PARTIAL_LINKAGE_GEOMETRY_ONLY` is descriptive, not confirmatory.
