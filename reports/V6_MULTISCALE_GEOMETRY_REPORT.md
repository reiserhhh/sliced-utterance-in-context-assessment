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
- report output contains no text or author identifiers

## Results

| object           |         k |   neighbour_jaccard |   null_mean |   absolute_excess |   normalized_excess |   bonferroni_p | status                                    |
|:-----------------|----------:|--------------------:|------------:|------------------:|--------------------:|---------------:|:------------------------------------------|
| static_residual  |   5.00000 |             0.00176 |     0.00170 |           0.00007 |             0.00007 |        1.00000 | NO_SCALE_LINKAGE_DETECTED                 |
| static_residual  |  10.00000 |             0.00445 |     0.00322 |           0.00122 |             0.00123 |        0.01800 | SCALE_LINKAGE_DETECTED_NO_MATERIAL_MARGIN |
| static_residual  |  25.00000 |             0.01106 |     0.00784 |           0.00322 |             0.00324 |        0.00600 | SCALE_LINKAGE_DETECTED_NO_MATERIAL_MARGIN |
| static_residual  |  50.00000 |             0.02303 |     0.01564 |           0.00739 |             0.00751 |        0.00600 | SCALE_LINKAGE_DETECTED_NO_MATERIAL_MARGIN |
| static_residual  | 100.00000 |             0.04516 |     0.03164 |           0.01352 |             0.01397 |        0.00600 | SCALE_LINKAGE_DETECTED_NO_MATERIAL_MARGIN |
| static_residual  | 200.00000 |             0.08972 |     0.06516 |           0.02456 |             0.02628 |        0.00600 | SCALE_LINKAGE_DETECTED_NO_MATERIAL_MARGIN |
| dynamic_residual |   5.00000 |             0.00350 |     0.00441 |          -0.00091 |            -0.00092 |        1.00000 | NO_SCALE_LINKAGE_DETECTED                 |
| dynamic_residual |  10.00000 |             0.00747 |     0.00837 |          -0.00090 |            -0.00091 |        1.00000 | NO_SCALE_LINKAGE_DETECTED                 |
| dynamic_residual |  25.00000 |             0.02068 |     0.02055 |           0.00013 |             0.00013 |        1.00000 | NO_SCALE_LINKAGE_DETECTED                 |
| dynamic_residual |  50.00000 |             0.04419 |     0.04145 |           0.00274 |             0.00286 |        0.07800 | NO_SCALE_LINKAGE_DETECTED                 |
| dynamic_residual | 100.00000 |             0.09305 |     0.08598 |           0.00707 |             0.00773 |        0.00600 | SCALE_LINKAGE_DETECTED_NO_MATERIAL_MARGIN |
| dynamic_residual | 200.00000 |             0.20312 |     0.18762 |           0.01550 |             0.01909 |        0.00600 | SCALE_LINKAGE_DETECTED_NO_MATERIAL_MARGIN |

## Reading rule

`SCALE_LINKAGE_DETECTED_NO_MATERIAL_MARGIN` requires adjusted `p < .05` only;
it has no preregistered practical-effect threshold. The `absolute_excess` and
`normalized_excess` columns must be read alongside p-values. A signal only at
large `k` is broad relational ordering, not a stable local group. A signal at
small `k` still requires opportunity, representation, and repeated-occasion
controls before it can be treated as an author property.
