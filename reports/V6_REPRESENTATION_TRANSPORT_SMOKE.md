# SUICA V6 Representation-Transport Audit

## Scope

This audit asks a restricted numerical question: after the same registered
opportunity conditioning and author aggregation, do author relations survive a
change from a word/bigram TF-IDF coordinate map to a character 3--5 gram TF-IDF
coordinate map? Raw text is used only to fit discovery-side maps. All tests
below operate on numeric confirmation matrices. No vocabulary, text, author ID,
external label, or construct name is exported or inspected.

For a representation `r` and half `h`, the object is a point cloud
`R^(r,h)`. Cross-representation correspondence is tested through linear and RBF
kernel alignment, pairwise-distance rank concordance, and top-10 neighbour
overlap. The null permutes only the row linkage between the two point clouds.

## Frozen settings

- representation dimensions per map: `24`
- confirmation authors per comparison: at most `128` (fixed hash subset)
- linkage permutations: `99`
- familywise correction: Bonferroni across `32` tests
- examined views: complete static configuration and static residual configuration
- examined comparisons: same-half and cross-half word/character geometry

## Results

| object          | comparison             |   n_users | status                                    |   linear_cka |   linear_cka_bonferroni_p |   rbf_cka |   rbf_cka_bonferroni_p |   distance_spearman |   distance_spearman_bonferroni_p |   neighbour_jaccard |   neighbour_jaccard_bonferroni_p |
|:----------------|:-----------------------|----------:|:------------------------------------------|-------------:|--------------------------:|----------:|-----------------------:|--------------------:|---------------------------------:|--------------------:|---------------------------------:|
| static_full     | word_early__char_early |       128 | NO_CROSS_REPRESENTATION_GEOMETRY_DETECTED |       0.5690 |                    0.3200 |    0.6071 |                 0.3200 |              0.6355 |                           0.3200 |              0.1846 |                           0.3200 |
| static_full     | word_late__char_late   |       128 | NO_CROSS_REPRESENTATION_GEOMETRY_DETECTED |       0.5516 |                    0.3200 |    0.5976 |                 0.3200 |              0.5488 |                           0.3200 |              0.1605 |                           0.3200 |
| static_full     | word_early__char_late  |       128 | NO_CROSS_REPRESENTATION_GEOMETRY_DETECTED |       0.2191 |                    0.3200 |    0.3136 |                 0.3200 |              0.2811 |                           0.3200 |              0.0659 |                           0.3200 |
| static_full     | word_late__char_early  |       128 | NO_CROSS_REPRESENTATION_GEOMETRY_DETECTED |       0.2138 |                    0.3200 |    0.3145 |                 0.3200 |              0.2462 |                           0.3200 |              0.0684 |                           0.3200 |
| static_residual | word_early__char_early |       128 | NO_CROSS_REPRESENTATION_GEOMETRY_DETECTED |       0.4204 |                    0.3200 |    0.4656 |                 0.3200 |              0.6202 |                           0.3200 |              0.1203 |                           0.3200 |
| static_residual | word_late__char_late   |       128 | NO_CROSS_REPRESENTATION_GEOMETRY_DETECTED |       0.4026 |                    0.3200 |    0.4271 |                 0.3200 |              0.5455 |                           0.3200 |              0.1168 |                           0.3200 |
| static_residual | word_early__char_late  |       128 | NO_CROSS_REPRESENTATION_GEOMETRY_DETECTED |       0.1481 |                    0.3200 |    0.2427 |                 0.3200 |              0.2880 |                           0.3200 |              0.0571 |                           1.0000 |
| static_residual | word_late__char_early  |       128 | NO_CROSS_REPRESENTATION_GEOMETRY_DETECTED |       0.1404 |                    0.3200 |    0.2367 |                 0.3200 |              0.2961 |                           0.3200 |              0.0628 |                           0.3200 |

## Reading rule

`CROSS_REPRESENTATION_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN` means that all four
numeric correspondence tests survive the stated familywise correction. It shows
only that a relational configuration is not tied to one coordinate basis. It
does not establish semantic invariance, causal source, stable author trait,
personality, or a usable score. Same-half results alone demonstrate mapping
correspondence; cross-half results are needed before calling the result a
representation-transport property.
