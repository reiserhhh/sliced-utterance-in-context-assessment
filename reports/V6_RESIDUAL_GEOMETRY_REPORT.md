# SUICA V6 Residual Geometry Audit

## Scope

This is a numeric-only audit. A discovery-fitted representation maps source text
to coordinates once; immediately after that transformation, all analysis uses
only paired author-by-feature matrices. No token, term, raw text, author ID,
questionnaire, or psychological construct name is read or exported.

For author `u`, let `R_u^(E)` and `R_u^(L)` be early and late opportunity-
conditioned residual coordinates. The audit asks whether their **relational
geometry** reproduces:

\[
K^{(h)} = H R^{(h)}R^{(h)\top}H,
\qquad
\operatorname{CKA}(E,L)=
\frac{\langle K^{(E)},K^{(L)}\rangle_F}
{\lVert K^{(E)}\rVert_F\lVert K^{(L)}\rVert_F}.
\]

It also compares rank order of pairwise distances, top-`k` neighbourhood overlap,
covariance-spectrum similarity, and local intrinsic dimension. The null retains
both point clouds but permutes the early-to-late author linkage. Thus a positive
result says that author relations reproduce more than arbitrary linkage; it does
not establish personality, causality, or a named factor.

## Frozen settings

- representation dimensions: `24`
- dynamic residual coordinates: `2`
- permutation draws: `999`
- subsample draws: `128`
- familywise correction: Bonferroni across `18` object-metric tests
- neighbourhood size: `10`
- no factor naming, lexical export, or external labels

## Results

| object           |   n_users |   n_features | status                                       |   linear_cka |   linear_cka_bonferroni_p |   distance_spearman |   distance_spearman_bonferroni_p |   neighbour_jaccard |   neighbour_jaccard_bonferroni_p |   effective_rank_early |   effective_rank_late |   intrinsic_dimension_early |   intrinsic_dimension_late |   spectrum_cosine |
|:-----------------|----------:|-------------:|:---------------------------------------------|-------------:|--------------------------:|--------------------:|---------------------------------:|--------------------:|---------------------------------:|-----------------------:|----------------------:|----------------------------:|---------------------------:|------------------:|
| static_full      |      1640 |           24 | LINKAGE_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN |       0.0935 |                    0.0180 |              0.3172 |                           0.0180 |              0.0130 |                           0.0180 |                22.9246 |               22.9017 |                     17.1753 |                    16.9267 |            0.9999 |
| static_factor    |      1640 |            7 | LINKAGE_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN |       0.1605 |                    0.0180 |              0.2644 |                           0.0180 |              0.0142 |                           0.0180 |                 6.8870 |                6.8695 |                      7.0000 |                     7.0000 |            0.9992 |
| static_residual  |      1640 |           24 | LINKAGE_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN |       0.0396 |                    0.0180 |              0.2597 |                           0.0180 |              0.0084 |                           0.0180 |                16.4866 |               16.5484 |                     14.4130 |                    14.2091 |            0.9995 |
| dynamic_full     |       635 |           10 | PARTIAL_LINKAGE_GEOMETRY_ONLY                |       0.0116 |                    1.0000 |              0.0912 |                           0.0180 |              0.0165 |                           1.0000 |                 6.8665 |                6.9186 |                      8.1814 |                     7.7734 |            0.9966 |
| dynamic_factor   |       635 |            3 | NO_LINKAGE_GEOMETRY_DETECTED                 |       0.0078 |                    1.0000 |              0.0412 |                           0.3960 |              0.0154 |                           1.0000 |                 2.8633 |                2.8644 |                      3.0000 |                     3.0000 |            0.9922 |
| dynamic_residual |       635 |           10 | PARTIAL_LINKAGE_GEOMETRY_ONLY                |       0.0105 |                    1.0000 |              0.0985 |                           0.0360 |              0.0140 |                           1.0000 |                 5.6786 |                5.6700 |                      6.8830 |                     6.7873 |            0.9969 |

## Reading rule

`LINKAGE_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN` requires all three paired-linkage
permutation tests (CKA, distance-rank concordance, and neighbourhood overlap) to
have Bonferroni-adjusted `p < .05`. It is a detection result, not a practical-strength acceptance:
this analysis did not preregister a material effect-size margin.
`PARTIAL_LINKAGE_GEOMETRY_ONLY` is descriptive and cannot support a construct claim. A positive
linkage geometry can still arise from idiolect, social niche, latent topic,
unobserved opportunity, or persistent state; these are not resolved by a linkage
permutation.

The static and dynamic objects remain subject to the V6 identification rule:
without repeated common conditions and independent technical replicas, a dynamic
configuration cannot be promoted to a stable author operator or personality
dimension.
