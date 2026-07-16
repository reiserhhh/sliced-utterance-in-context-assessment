# V7.5-X2: Joint Nested Conditional Uncertainty of the Frozen G1 Geometry Bundle

Registered before run at release commit `3a6f5b9` (ledger row `V7.5-X2`).
First real-data consumption of `suica_core/v7_uncertainty.py`.

## Scope

The measured object is the conditional score error of the frozen G1
relative-geometry bundle (`SU7-GEO-0c434ce57fb2f974c5ba7eb8`) for the held-out
calibration + confirmation authors that G1 scored. The profile functionals are
`mean_landmark_distance` (primary) and `nearest_landmark_distance`
(secondary). Error decomposition of a technical geometry only; no reliability, MDD, or person-score validity claim.

## Reproduction gates (passed before any draw)

- Recomputed E1 native author features match the frozen table to
  max abs diff `9.97e-17`.
- Frozen-bundle rescoring with real per-author unit counts reproduces the G1
  `support_summary.csv` ready counts exactly (139 / 47 / 38).

## Support handling

Real per-author unit counts (`n_units` from the frozen E1 native feature
table) were passed to `score_geometry_bundle`; `assume_support_verified` was
**not** used, so ready rows carry `GEOMETRY_PROFILE_READY` directly and no
support attestation was needed.

## Design (per the module's own API and the V7 uncertainty protocol)

- `source_cluster` (256 draws/author): Resample the scored author's non-overlapping native source comments (cluster bootstrap, with replacement, same unit count) under the frozen representation and frozen G1 bundle.
- `model_refit` (64 draws): Refit the registered TF-IDF+SVD representation on a within-author resample of the discovery source-comment corpus with a fresh SVD seed, recompute discovery author features from their original units, refit the geometry runtime, and rescore the target author's original units. Reference-population membership is held fixed.
- `reference_norm` (256 draws): Resample the 141 discovery reference authors (feature rows) with replacement under the frozen representation and refit the geometry runtime (center, metric, landmarks, support radius) before rescoring frozen target features.
- `joint_nested` (128 draws): Protocol combination rule: resample discovery reference authors, refit representation and geometry runtime on that draw, resample the scored author's source clusters, and score the profile functional per draw.

The module refuses a naive independence-summed total SEM. That refusal was
demonstrated on real draws
(`REFUSE_TOTAL_GEOMETRY_UNCERTAINTY_DEPENDENCE_UNMODELED`)
and then satisfied through the declared joint-nested path, so every emitted
total SEM comes from `JOINT_NESTED_DRAWS`, not from an independence
assumption. The independence approximation is additionally reported per
author as a labeled diagnostic only.

## Results

- Target authors: 99 (calibration + confirmation).
- Decomposed (baseline `GEOMETRY_PROFILE_READY`): **85**.
- Refused out-of-support (module status
  `REFUSE_GEOMETRY_UNCERTAINTY_OUT_OF_SUPPORT`): 14
  — all are baseline radial-envelope refusals; they receive no precision
  estimate, per protocol.

### Pooled component variance shares (mean_landmark_distance)

- source_cluster: **0.5026**
- model_refit: **0.1737**
- reference_norm: **0.3237**

Registered weak lean (`source_cluster_component >= model_refit_component (weak lean, no kill)`):
**HELD** at the pooled
level; per-author fraction with source >= model:
0.988.

### Population summary

| functional                | component          |   pooled_variance_share |   mean_author_share |   median_author_share |   median_author_sem |   n_authors |
|:--------------------------|:-------------------|------------------------:|--------------------:|----------------------:|--------------------:|------------:|
| mean_landmark_distance    | source_cluster     |                  0.5026 |              0.4945 |                0.5011 |              0.8586 |          85 |
| mean_landmark_distance    | model_refit        |                  0.1737 |              0.1791 |                0.1727 |              0.5178 |          85 |
| mean_landmark_distance    | reference_norm     |                  0.3237 |              0.3264 |                0.3229 |              0.7247 |          85 |
| mean_landmark_distance    | joint_nested_total |                nan      |            nan      |              nan      |              1.6837 |          85 |
| nearest_landmark_distance | source_cluster     |                  0.4358 |              0.4290 |                0.4241 |              0.9186 |          85 |
| nearest_landmark_distance | model_refit        |                  0.2218 |              0.2264 |                0.2247 |              0.6791 |          85 |
| nearest_landmark_distance | reference_norm     |                  0.3423 |              0.3446 |                0.3461 |              0.8253 |          85 |
| nearest_landmark_distance | joint_nested_total |                nan      |            nan      |              nan      |              1.6844 |          85 |

### Per-author conditional SEM quantiles (mean_landmark_distance, decomposed authors)

|        |   sem_source_cluster |   sem_model_refit |   sem_reference_norm |   total_conditional_sem_joint |   total_sem_independence_approx |
|-------:|---------------------:|------------------:|---------------------:|------------------------------:|--------------------------------:|
| 0.0500 |               0.6579 |            0.4188 |               0.5281 |                        1.3894 |                          1.0210 |
| 0.2500 |               0.7917 |            0.4854 |               0.6350 |                        1.5427 |                          1.1626 |
| 0.5000 |               0.8586 |            0.5178 |               0.7247 |                        1.6837 |                          1.2440 |
| 0.7500 |               0.9721 |            0.5663 |               0.7948 |                        1.8443 |                          1.3366 |
| 0.9500 |               1.1967 |            0.6576 |               0.8903 |                        2.2472 |                          1.5955 |

Median joint total conditional SEM: 1.6837
(median baseline mean_landmark_distance: 11.0535).
Median joint/independence SEM ratio:
1.3682 — a ratio away
from 1 is direct evidence that the component dependence the module refuses to
ignore is real.

### Draw-level radial-envelope diagnostics (decomposed authors)

Draw values enter the component vectors regardless of the draw's own support
status (the frozen bundle is the measurement instrument; draws quantify its
sensitivity), but each draw is also re-checked against the applicable radial
envelope and the per-author ready rate is recorded:

- `source_cluster`: median ready rate 0.188, mean 0.241
- `model_refit`: median ready rate 0.953, mean 0.884
- `reference_norm`: median ready rate 0.492, mean 0.486
- `joint_nested`: median ready rate 0.062, mean 0.075

The low source-cluster and joint ready rates are an honest secondary finding:
a cluster-bootstrap of an author's ~32 source comments adds enough
mean-feature noise in 48 whitened dimensions to push the regularized
Mahalanobis radius past the frozen q99 threshold in most draws. The G1 radial
envelope is therefore tight relative to per-author source-sampling noise —
held-out authors typically sit within about one conditional SEM of the
refusal boundary. This is a support-policy calibration observation, not a
scoring error, and it does not change any baseline status.

## Artifacts

- Decision: `/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/results/v7_uncertainty/x2_g1_joint_20260717/decision.json`
- Per-author table (deidentified, anon ids only): `/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/results/v7_uncertainty/x2_g1_joint_20260717/per_author_uncertainty.csv`
- Population summary: `/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/results/v7_uncertainty/x2_g1_joint_20260717/component_share_summary.csv`
- Deidentified draw matrices: `/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/results/v7_uncertainty/x2_g1_joint_20260717/draw_matrices_deidentified.npz`
- Aggregate snapshot: `/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/results/v7_uncertainty/x2_g1_joint_20260717/aggregate_snapshot.json`
- Manifest: `/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/results/v7_uncertainty/x2_g1_joint_20260717/run_manifest.json`

## Claim boundary

Error decomposition of a technical geometry only; no reliability, MDD, or person-score validity claim. The decomposition conditions on the frozen E1
representation family, the native operator, this Reddit-derived corpus, and
the G1 support policy; it says nothing about trait reliability (G-study/LST
gate), minimum detectable difference, or any person-level interpretation.
