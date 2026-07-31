# SUICA M4-C Condition-Manifold Discovery

## Decision

`M4_C_CONDITION_MANIFOLD_DISCOVERY_PASS`

## Question

Can SUICA discover a condition representation from author-independent,
pre-response environment/context variables, transport it across two numeric
sources, and retain conditional-response structure without using the response
to select the chart?

The formal object is an atlas or relation geometry

\[
\widehat{\mathcal M}
=
\{(\mathcal U_a,\zeta_a),T_{ab}\},
\]

not a named topic axis. Chart fitting sees neither response nor external
psychological labels. Response is opened only after chart selection and is
evaluated once on the untouched mechanism-evaluation panel.

## Frozen design

- config version: `suica-m4-c-condition-manifold-v1`
- repetitions: `8`
- worlds: `true_linear_manifold, true_nonlinear_multichart, source_specific_rotations, author_leakage, response_leakage_circular, topology_mismatch, null_no_manifold, condition_alias`
- chart families: linear PCA, global Isomap, landmark geodesic atlas
- role split: reference calibration -> reference selection -> mechanism
  calibration/selection -> untouched mechanism evaluation

## Diagnostics

- `identifiable_resolution_rate`: 0.916667
- `identifiable_geometry`: 0.912634
- `identifiable_neighbor_jaccard`: 0.774208
- `identifiable_response_retention`: 0.924575
- `identifiable_response_geometry`: 0.960241
- `refusal_world_resolution_rate`: 1.000000
- `topology_resolution_rate`: 1.000000
- `alias_refusal_rate`: 1.000000
- `response_perturbation_invariance_rate`: 1.000000
- `identifiable_cross_source_geometry`: 0.963450
- `identifiable_topology_match_rate`: 0.833333

## Gates

- PASS: `identifiable_worlds`
- PASS: `geodesic_geometry`
- PASS: `local_neighborhoods`
- PASS: `cross_source_transport`
- PASS: `refusal_attacks`
- PASS: `condition_alias`
- PASS: `response_safety`
- PASS: `topology_or_refusal`
- PASS: `registered_topology`
- PASS: `conditional_response_retention`
- PASS: `response_operator_geometry`

## Selected families

| world                     | selected_family   |   count |
|:--------------------------|:------------------|--------:|
| author_leakage            | linear_pca        |       8 |
| condition_alias           | global_isomap     |       4 |
| condition_alias           | linear_pca        |       4 |
| null_no_manifold          | global_isomap     |       5 |
| null_no_manifold          | landmark_atlas    |       2 |
| null_no_manifold          | linear_pca        |       1 |
| response_leakage_circular | global_isomap     |       6 |
| response_leakage_circular | linear_pca        |       2 |
| source_specific_rotations | global_isomap     |       7 |
| source_specific_rotations | landmark_atlas    |       1 |
| topology_mismatch         | global_isomap     |       5 |
| topology_mismatch         | linear_pca        |       3 |
| true_linear_manifold      | global_isomap     |       1 |
| true_linear_manifold      | linear_pca        |       7 |
| true_nonlinear_multichart | global_isomap     |       4 |
| true_nonlinear_multichart | landmark_atlas    |       4 |

## Scope correction

This V1 route tests condition-chart recovery and frozen conditional-response
retention. It does **not** yet re-estimate all M4-B opportunity-selection,
opportunity-creation, return, recovery, and history-gate operators in the
discovered atlas. Those ecology operators remain valid M4-B objects and require
a separate chart-covariant adapter rather than being inferred from this
response-only result.

Coordinate axes and individual matrix elements are diagnostics. The licensed
objects are held-out neighborhoods, chart-invariant relation geometry,
response prediction on registered support, and explicit refusal under
leakage, no-manifold, topology conflict, or condition alias.

The condition-alias refusal is operationally triggered by the predeclared
untouched-response rule `conditional_response_r2 < 0.60`. Synthetic oracle
retention is used only in the truth-open audit to verify the cause of the
planted alias; it is not available to the runtime refusal.
Response-permutation invariance is executed once per world (8/8), then
recorded on that world's repetition rows.

## Artifacts

- cell metrics: `results/m4_condition_manifold/metrics.csv`
- world summary: `results/m4_condition_manifold/world_summary.csv`
- decision: `results/m4_condition_manifold/decision.json`

## Claim boundary

Finite response-safe synthetic condition geometry only. A pass may recover registered condition neighborhoods and preserve a frozen conditional-response mechanism. It does not identify topic names, personality, emotion, cognition, diagnosis, or natural-text validity. Full M4-B opportunity selection/creation/return/gate transport remains separate.
