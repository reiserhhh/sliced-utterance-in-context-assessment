# SUICA V6 Technical-Replicate Geometry Audit

## Scope

This audit measures robustness to slice boundaries inside the same author,
half, and condition cell. Each cell with at least two observations is split by
two predeclared procedures: alternating (interleaved) comments and temporal
blocks. The source map and nuisance residualization are discovery-fitted. After
that boundary, all tests operate on numeric residual matrices only.

This is a **technical-replica** result: it measures scoring sensitivity to
which comments land in a slice. It does not establish independent occasions,
cross-context transfer, individual response operators, or a personality trait.

## Frozen settings

- technical split schemes: interleaved, blocked
- confirmation rows per comparison: at most `384`
- linkage permutations: `999`
- descriptive subsamples: `128` of at most `256` authors
- familywise correction: Bonferroni across `12` object-metric tests
- text, terms, author IDs, and external labels: not exported or inspected after mapping

## Coverage

| scheme      | half   |   n_discovery_paired |   n_confirmation_paired_before_subsample |   n_confirmation_used |
|:------------|:-------|---------------------:|-----------------------------------------:|----------------------:|
| interleaved | early  |                 1573 |                                     1640 |                   384 |
| interleaved | late   |                 1573 |                                     1640 |                   384 |
| blocked     | early  |                 1573 |                                     1640 |                   384 |
| blocked     | late   |                 1573 |                                     1640 |                   384 |

## Results

| scheme      | half   |   n_users | status                                       |   linear_cka |   linear_cka_bonferroni_p |   distance_spearman |   distance_spearman_bonferroni_p |   neighbour_jaccard |   neighbour_jaccard_bonferroni_p |   effective_rank_early |   effective_rank_late |   intrinsic_dimension_early |   intrinsic_dimension_late |   spectrum_cosine |
|:------------|:-------|----------:|:---------------------------------------------|-------------:|--------------------------:|--------------------:|---------------------------------:|--------------------:|---------------------------------:|-----------------------:|----------------------:|----------------------------:|---------------------------:|------------------:|
| interleaved | early  |       384 | LINKAGE_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN |       0.1264 |                    0.0120 |              0.3498 |                           0.0120 |              0.0497 |                           0.0120 |                21.4072 |               22.5346 |                     15.0717 |                    15.9145 |            0.9735 |
| interleaved | late   |       384 | LINKAGE_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN |       0.1379 |                    0.0120 |              0.4039 |                           0.0120 |              0.0573 |                           0.0120 |                22.2192 |               22.2685 |                     14.9626 |                    15.1185 |            0.9986 |
| blocked     | early  |       384 | LINKAGE_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN |       0.1276 |                    0.0120 |              0.3676 |                           0.0120 |              0.0523 |                           0.0120 |                21.5925 |               22.6110 |                     14.8946 |                    15.9222 |            0.9779 |
| blocked     | late   |       384 | LINKAGE_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN |       0.1347 |                    0.0120 |              0.3842 |                           0.0120 |              0.0563 |                           0.0120 |                22.0503 |               22.2783 |                     14.7854 |                    15.2923 |            0.9972 |

## Reading rule

A passing row means that the relational geometry of opportunity-conditioned
static configurations survives that particular within-condition slice boundary.
It says nothing about whether the configuration is stable across days, tasks,
or people. A blocked failure with an interleaved pass would indicate sensitivity
to short-run temporal state; neither outcome may be promoted to personality.
