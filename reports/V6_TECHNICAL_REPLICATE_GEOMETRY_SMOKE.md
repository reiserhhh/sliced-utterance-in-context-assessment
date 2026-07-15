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
- confirmation rows per comparison: at most `128`
- linkage permutations: `99`
- descriptive subsamples: `16`
- familywise correction: Bonferroni across `12` object-metric tests
- text, terms, author IDs, and external labels: not exported or inspected after mapping

## Coverage

| scheme      | half   |   n_discovery_paired |   n_confirmation_paired_before_subsample |   n_confirmation_used |
|:------------|:-------|---------------------:|-----------------------------------------:|----------------------:|
| interleaved | early  |                 1573 |                                     1640 |                   128 |
| interleaved | late   |                 1573 |                                     1640 |                   128 |
| blocked     | early  |                 1573 |                                     1640 |                   128 |
| blocked     | late   |                 1573 |                                     1640 |                   128 |

## Results

| scheme      | half   |   n_users | status                       |   linear_cka |   linear_cka_bonferroni_p |   distance_spearman |   distance_spearman_bonferroni_p |   neighbour_jaccard |   neighbour_jaccard_bonferroni_p |   effective_rank_early |   effective_rank_late |   intrinsic_dimension_early |   intrinsic_dimension_late |   spectrum_cosine |
|:------------|:-------|----------:|:-----------------------------|-------------:|--------------------------:|--------------------:|---------------------------------:|--------------------:|---------------------------------:|-----------------------:|----------------------:|----------------------------:|---------------------------:|------------------:|
| interleaved | early  |       128 | NO_LINKAGE_GEOMETRY_DETECTED |       0.2163 |                    0.1200 |              0.3721 |                           0.1200 |              0.1164 |                           0.1200 |                20.8506 |               20.6127 |                     13.3517 |                    13.8875 |            0.9978 |
| interleaved | late   |       128 | NO_LINKAGE_GEOMETRY_DETECTED |       0.2405 |                    0.1200 |              0.3856 |                           0.1200 |              0.1398 |                           0.1200 |                20.9079 |               20.7658 |                     13.7842 |                    14.3257 |            0.9989 |
| blocked     | early  |       128 | NO_LINKAGE_GEOMETRY_DETECTED |       0.2128 |                    0.1200 |              0.4102 |                           0.1200 |              0.1375 |                           0.1200 |                20.4995 |               20.6480 |                     13.2299 |                    13.7147 |            0.9987 |
| blocked     | late   |       128 | NO_LINKAGE_GEOMETRY_DETECTED |       0.2231 |                    0.1200 |              0.3741 |                           0.1200 |              0.1281 |                           0.1200 |                20.8285 |               20.1789 |                     13.8641 |                    13.7242 |            0.9960 |

## Reading rule

A passing row means that the relational geometry of opportunity-conditioned
static configurations survives that particular within-condition slice boundary.
It says nothing about whether the configuration is stable across days, tasks,
or people. A blocked failure with an interleaved pass would indicate sensitivity
to short-run temporal state; neither outcome may be promoted to personality.
