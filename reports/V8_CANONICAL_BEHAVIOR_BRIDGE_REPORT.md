# SUICA V8 Canonical Geometry-to-Behavior Bridge Report

Status: `CANONICAL_GEOMETRY_CONFIRMED__CURRENT_BEHAVIOR_OBJECT_STOP`

Run:
`results/v8_canonical_behavior_bridge/pandora_20260725`

## Purpose

This bounded diagnostic replaced the failed sorted-distance geometry with the
internally confirmed canonical scale-residual representation. It kept the
existing PANDORA observer cache, six event codes, three segments per half,
source-disjoint author halves, cohort splits, feature filters, ridge search,
and confirmation gates unchanged.

No new LLM calls or external labels were used.

## Result

Calibration selected repeated event rates plus event pairs. On the frozen
20-author confirmation partition:

| Endpoint | Result |
| --- | ---: |
| Cross-modal author AUC | 0.547 |
| Author-cluster 95% interval | [0.447, 0.616] |
| Cross-modal cosine AUC | 0.623 |
| Geometry self-author AUC | 0.735 |
| Behavior self-author AUC | 0.556 |
| Element Spearman | 0.152 |
| Distance Spearman | 0.143, p=0.073 |
| Evidence-supported profile rate | 0.650 |
| Stable registered links | 0 |
| Distinct behavior targets | 0 |

Relative to the old selected bridge, geometry self-AUC increased by 0.269 and
cross-modal AUC increased by 0.053, while behavior self-AUC changed by only
0.006.

## Decision

`V8_CANONICAL_GEOMETRY_PASS_BEHAVIOR_VIEW_STOP`

The earlier bridge failure had two bottlenecks. Canonical structural identity
closed the geometry bottleneck, but the current behavior object remains
under-resolved. Three segments and six broad event codes do not preserve
enough source-disjoint author information to support stable registered links.

Do not tune the renderer or spend additional calls on the current prompt. The
next behavior experiment must change the measured object:

1. collect or reuse more segments per author half;
2. expand the observable event ontology before opening outcomes;
3. separate event rate, sequencing, response, repair, and state-transition
   objects;
4. include an independently coded subset to estimate observer accuracy rather
   than only observer agreement;
5. require behavior self-author AUC at least 0.60 before fitting a
   geometry-to-behavior bridge.

This result concerns author-relative geometry and an explicit behavior
codebook. It does not validate personality, diagnosis, clinical utility, or
direct LLM psychological scoring.
