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
- confirmation authors per comparison: at most `384` (fixed hash subset)
- linkage permutations: `999`
- familywise correction: Bonferroni across `32` tests
- examined views: complete static configuration and static residual configuration
- examined comparisons: same-half and cross-half word/character geometry

## Results

| object          | comparison             |   n_users | status                                                    |   linear_cka |   linear_cka_bonferroni_p |   rbf_cka |   rbf_cka_bonferroni_p |   distance_spearman |   distance_spearman_bonferroni_p |   neighbour_jaccard |   neighbour_jaccard_bonferroni_p |
|:----------------|:-----------------------|----------:|:----------------------------------------------------------|-------------:|--------------------------:|----------:|-----------------------:|--------------------:|---------------------------------:|--------------------:|---------------------------------:|
| static_full     | word_early__char_early |       384 | CROSS_REPRESENTATION_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN |       0.5312 |                    0.0320 |    0.5199 |                 0.0320 |              0.6523 |                           0.0320 |              0.1087 |                           0.0320 |
| static_full     | word_late__char_late   |       384 | CROSS_REPRESENTATION_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN |       0.5088 |                    0.0320 |    0.5172 |                 0.0320 |              0.6598 |                           0.0320 |              0.1006 |                           0.0320 |
| static_full     | word_early__char_late  |       384 | CROSS_REPRESENTATION_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN |       0.1135 |                    0.0320 |    0.1778 |                 0.0320 |              0.3338 |                           0.0320 |              0.0209 |                           0.0320 |
| static_full     | word_late__char_early  |       384 | CROSS_REPRESENTATION_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN |       0.1245 |                    0.0320 |    0.1854 |                 0.0320 |              0.3407 |                           0.0320 |              0.0278 |                           0.0320 |
| static_residual | word_early__char_early |       384 | CROSS_REPRESENTATION_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN |       0.4235 |                    0.0320 |    0.3446 |                 0.0320 |              0.5682 |                           0.0320 |              0.0621 |                           0.0320 |
| static_residual | word_late__char_late   |       384 | CROSS_REPRESENTATION_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN |       0.2829 |                    0.0320 |    0.3040 |                 0.0320 |              0.4838 |                           0.0320 |              0.0511 |                           0.0320 |
| static_residual | word_early__char_late  |       384 | PARTIAL_CROSS_REPRESENTATION_GEOMETRY_ONLY                |       0.0507 |                    0.1920 |    0.0967 |                 0.0320 |              0.2274 |                           0.0320 |              0.0156 |                           1.0000 |
| static_residual | word_late__char_early  |       384 | PARTIAL_CROSS_REPRESENTATION_GEOMETRY_ONLY                |       0.0499 |                    0.2560 |    0.0961 |                 0.0320 |              0.2324 |                           0.0320 |              0.0218 |                           0.0320 |

## Reading rule

`CROSS_REPRESENTATION_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN` means that all four
numeric correspondence tests survive the stated familywise correction. It shows
only that a relational configuration is not tied to one coordinate basis. It
does not establish semantic invariance, causal source, stable author trait,
personality, or a usable score. Same-half results alone demonstrate mapping
correspondence; cross-half results are needed before calling the result a
representation-transport property.
