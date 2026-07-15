# SUICA V6 Cross-Block Geometry Audit

## Scope

This audit tests **undirected** relational correspondence between numeric V6
object families. It uses only internally aligned arrays from the ID-free cache.
For point clouds `A^(h)` and `B^(h')`, it asks whether their row-to-row kernels,
distance order, and local neighbour graphs correspond more than after permuting
the linkage of `B`. It cannot identify whether one object leads, inhibits, or
causes another; the present two-half design does not support such a claim.

## Frozen settings

- numeric rows per comparison: at most `384`
- linkage permutations: `999`
- familywise correction: Bonferroni across `48` tests
- source text, terms, author IDs, and external labels: not read

## Results

| pair            | comparison              |   n_users | status                                           |   linear_cka |   linear_cka_bonferroni_p |   rbf_cka |   rbf_cka_bonferroni_p |   distance_spearman |   distance_spearman_bonferroni_p |   neighbour_jaccard |   neighbour_jaccard_bonferroni_p |
|:----------------|:------------------------|----------:|:-------------------------------------------------|-------------:|--------------------------:|----------:|-----------------------:|--------------------:|---------------------------------:|--------------------:|---------------------------------:|
| static__hybrid  | left_early__right_early |       384 | CROSS_BLOCK_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN |       0.0931 |                    0.0480 |    0.1406 |                 0.0480 |              0.2724 |                           0.0480 |              0.0223 |                           0.0480 |
| static__hybrid  | left_late__right_late   |       384 | CROSS_BLOCK_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN |       0.0797 |                    0.0480 |    0.1437 |                 0.0480 |              0.3214 |                           0.0480 |              0.0251 |                           0.0480 |
| static__hybrid  | left_early__right_late  |       384 | PARTIAL_CROSS_BLOCK_GEOMETRY_ONLY                |       0.0560 |                    1.0000 |    0.1146 |                 0.0960 |              0.1156 |                           0.0480 |              0.0162 |                           1.0000 |
| static__hybrid  | left_late__right_early  |       384 | PARTIAL_CROSS_BLOCK_GEOMETRY_ONLY                |       0.0644 |                    0.4320 |    0.1186 |                 0.0480 |              0.1837 |                           0.0480 |              0.0126 |                           1.0000 |
| static__dynamic | left_early__right_early |       384 | NO_CROSS_BLOCK_GEOMETRY_DETECTED                 |       0.0327 |                    1.0000 |    0.0619 |                 1.0000 |              0.0400 |                           1.0000 |              0.0134 |                           1.0000 |
| static__dynamic | left_late__right_late   |       384 | NO_CROSS_BLOCK_GEOMETRY_DETECTED                 |       0.0343 |                    1.0000 |    0.0624 |                 1.0000 |              0.0002 |                           1.0000 |              0.0125 |                           1.0000 |
| static__dynamic | left_early__right_late  |       384 | NO_CROSS_BLOCK_GEOMETRY_DETECTED                 |       0.0270 |                    1.0000 |    0.0584 |                 1.0000 |             -0.0196 |                           1.0000 |              0.0166 |                           1.0000 |
| static__dynamic | left_late__right_early  |       384 | NO_CROSS_BLOCK_GEOMETRY_DETECTED                 |       0.0381 |                    0.1920 |    0.0639 |                 0.8640 |              0.0440 |                           1.0000 |              0.0147 |                           1.0000 |
| hybrid__dynamic | left_early__right_early |       384 | PARTIAL_CROSS_BLOCK_GEOMETRY_ONLY                |       0.0464 |                    0.0480 |    0.0690 |                 0.5760 |              0.0283 |                           1.0000 |              0.0141 |                           1.0000 |
| hybrid__dynamic | left_late__right_late   |       384 | NO_CROSS_BLOCK_GEOMETRY_DETECTED                 |       0.0311 |                    1.0000 |    0.0644 |                 1.0000 |             -0.0100 |                           1.0000 |              0.0125 |                           1.0000 |
| hybrid__dynamic | left_early__right_late  |       384 | NO_CROSS_BLOCK_GEOMETRY_DETECTED                 |       0.0265 |                    1.0000 |    0.0585 |                 1.0000 |              0.0273 |                           1.0000 |              0.0121 |                           1.0000 |
| hybrid__dynamic | left_late__right_early  |       384 | NO_CROSS_BLOCK_GEOMETRY_DETECTED                 |       0.0293 |                    1.0000 |    0.0637 |                 1.0000 |              0.0414 |                           1.0000 |              0.0140 |                           1.0000 |

## Reading rule

All-four-metric support is labelled
`CROSS_BLOCK_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN`; partial support remains
descriptive. Same-half coupling can be mechanically induced because these
objects originate from the same underlying text-path coordinates. Cross-half
coupling is therefore the stronger result, but still not evidence of a causal
or psychological relation.
