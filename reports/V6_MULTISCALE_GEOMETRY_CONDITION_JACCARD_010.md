# SUICA V6 Multiscale Residual Geometry

## Numeric object

This analysis reads only an ID-free `.npz` cache of paired numeric residual
matrices. It never opens source text, feature names, token lists, labels, or
author identifiers.

For each neighbourhood scale `k`, let `N_k^E(u)` and `N_k^L(u)` be the `k`
nearest numerical neighbours of author `u` in the early and late clouds. The
profile statistic is

\[
J_k=\frac{1}{n}\sum_u
\frac{|N_k^E(u)\cap N_k^L(u)|}{|N_k^E(u)\cup N_k^L(u)|}.
\]

The linkage null fixes both clouds and permutes only early-to-late author
correspondence. Small `k` tests local neighbourhoods; larger `k` tests broader,
mesoscopic affiliation. This is not evidence for a discrete cluster, a factor,
or a psychological construct.

## Frozen controls

- linkage permutations per object-scale: `1999`
- Bonferroni family: `12` object-scale tests
- condition-overlap mask: `condition_jaccard_ge_010`
- report output contains no text or author identifiers

## Results

| object           |         k |   neighbour_jaccard |   null_mean |   absolute_excess |   normalized_excess |   bonferroni_p | status                                    |
|:-----------------|----------:|--------------------:|------------:|------------------:|--------------------:|---------------:|:------------------------------------------|
| static_residual  |   5.00000 |             0.00223 |     0.00200 |           0.00023 |             0.00023 |        1.00000 | NO_SCALE_LINKAGE_DETECTED                 |
| static_residual  |  10.00000 |             0.00553 |     0.00381 |           0.00173 |             0.00173 |        0.00600 | SCALE_LINKAGE_DETECTED_NO_MATERIAL_MARGIN |
| static_residual  |  25.00000 |             0.01344 |     0.00925 |           0.00419 |             0.00423 |        0.00600 | SCALE_LINKAGE_DETECTED_NO_MATERIAL_MARGIN |
| static_residual  |  50.00000 |             0.02719 |     0.01846 |           0.00873 |             0.00890 |        0.00600 | SCALE_LINKAGE_DETECTED_NO_MATERIAL_MARGIN |
| static_residual  | 100.00000 |             0.05345 |     0.03742 |           0.01603 |             0.01666 |        0.00600 | SCALE_LINKAGE_DETECTED_NO_MATERIAL_MARGIN |
| static_residual  | 200.00000 |             0.10583 |     0.07754 |           0.02829 |             0.03067 |        0.00600 | SCALE_LINKAGE_DETECTED_NO_MATERIAL_MARGIN |
| dynamic_residual |   5.00000 |             0.00490 |     0.00513 |          -0.00023 |            -0.00023 |        1.00000 | NO_SCALE_LINKAGE_DETECTED                 |
| dynamic_residual |  10.00000 |             0.00883 |     0.00977 |          -0.00094 |            -0.00095 |        1.00000 | NO_SCALE_LINKAGE_DETECTED                 |
| dynamic_residual |  25.00000 |             0.02447 |     0.02400 |           0.00047 |             0.00048 |        1.00000 | NO_SCALE_LINKAGE_DETECTED                 |
| dynamic_residual |  50.00000 |             0.05174 |     0.04864 |           0.00310 |             0.00326 |        0.11400 | NO_SCALE_LINKAGE_DETECTED                 |
| dynamic_residual | 100.00000 |             0.11014 |     0.10180 |           0.00834 |             0.00928 |        0.00600 | SCALE_LINKAGE_DETECTED_NO_MATERIAL_MARGIN |
| dynamic_residual | 200.00000 |             0.24516 |     0.22605 |           0.01910 |             0.02468 |        0.00600 | SCALE_LINKAGE_DETECTED_NO_MATERIAL_MARGIN |

## Reading rule

`SCALE_LINKAGE_DETECTED_NO_MATERIAL_MARGIN` requires adjusted `p < .05` only;
it has no preregistered practical-effect threshold. The `absolute_excess` and
`normalized_excess` columns must be read alongside p-values. A signal only at
large `k` is broad relational ordering, not a stable local group. A signal at
small `k` still requires opportunity, representation, and repeated-occasion
controls before it can be treated as an author property.
