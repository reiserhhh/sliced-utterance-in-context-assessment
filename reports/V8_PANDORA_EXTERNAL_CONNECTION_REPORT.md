# SUICA V8 Full PANDORA External Connection

Status: `OPENED_PANDORA_EXPLORATORY_EXTERNAL_CONNECTION`

## Design

The frozen V8 canonical scale-residual geometry was scored before labels were joined. Big5-only authors were used for Big Five heads, MBTI-only authors for four binary axis heads, and strict both-label authors only for the held-out Big5↔MBTI structural bridge. Official repeat-0 folds were used for source-task CV. Every head was fitted inside its training fold; the V8 geometry and representation were never refitted.

Claim boundary: This is an exploratory external connection on previously opened PANDORA labels. It applies the frozen V8 native operator (12-token minimum, 32 temporally spread source comments, 4096-token budget) after personality-leakage cleaning, then tests frozen text geometry against external Big Five and MBTI anchors. It cannot confirm, name, rotate, or select a psychological construct.

## Coverage

- Frozen score authors: 10090
- Geometry-ready authors: 7523
- Big5-only ready: 660
- Big5-only minimum-support sensitivity: 1003
- MBTI-only ready (minimum across axes): 6599
- MBTI-only minimum-support sensitivity (minimum across axes): 8677
- Strict bridge ready: 264
- Strict bridge minimum-support sensitivity: 361

## Primary official-fold results

| View | Big5 mean r | MBTI mean AUC | MBTI mean balanced accuracy | Bridge element r | Bridge permutation p |
|---|---:|---:|---:|---:|---:|
| v8_canonical | -0.005 | 0.544 | 0.531 | 0.498 | 0.0086 |
| nuisance_only | 0.054 | 0.559 | 0.542 | 0.209 | 0.1482 |
| v8_plus_nuisance | 0.032 | 0.572 | 0.550 | 0.353 | 0.0514 |
| v7_author48_upper_bound | 0.062 | 0.608 | 0.577 | 0.497 | 0.0068 |

The 48-coordinate V7 row is an upstream representation upper bound, not the invariant SUICA score. Nuisance-only uses text amount and format opportunity variables. V8+nuisance tests incremental complementarity.

## Minimum-support sensitivity

| View | Big5 mean r | MBTI mean AUC | Bridge element r | Bridge permutation p |
|---|---:|---:|---:|---:|
| v8_canonical | 0.007 | 0.549 | 0.517 | 0.0038 |
| nuisance_only | 0.034 | 0.564 | 0.264 | 0.0728 |
| v8_plus_nuisance | 0.035 | 0.576 | 0.503 | 0.0104 |
| v7_author48_upper_bound | 0.086 | 0.609 | 0.628 | 0.0006 |

## Paired uncertainty

- Big5 V8 minus nuisance: delta=-0.059, 95% paired-bootstrap CI [-0.109, -0.017].
- MBTI V8 minus nuisance: delta=-0.015, 95% paired-bootstrap CI [-0.026, -0.003].
- MBTI V8+nuisance minus nuisance: delta=0.013, 95% paired-bootstrap CI [0.006, 0.020].
- Bridge V8 element r: 0.498, author-bootstrap CI [0.383, 0.582].
- Bridge V8 minus nuisance: delta=0.289, author-bootstrap CI [0.125, 0.430].

## Decision

- Direct Big Five connection is not supported for the invariant V8 canonical score in this run.
- Direct MBTI connection is weak: V8 is above chance but below the nuisance comparator. V8 contributes a small complementary gain only when combined with nuisance variables.
- Cross-scale structure is the positive result: V8 recovers the held-out Big5-to-MBTI relation matrix and adds structure beyond nuisance despite weak individual Big Five prediction.
- The upstream 48-coordinate representation remains stronger for direct prediction. Canonical invariance therefore trades away criterion signal and should not replace the upstream representation in a prediction head.

## Coordinate screen

- Ready-cohort V8/nuisance tests passing within-target-view BH-FDR: 39.
- `Openness` × `v8_csr_09`: r=-0.142, q=0.0040 (n=660).
- `Openness` × `nuisance_chars_per_approx_token`: r=0.139, q=0.0030 (n=660).
- `TF_cont` × `nuisance_chars_per_approx_token`: r=-0.124, q=0.0000 (n=6599).
- `Openness` × `nuisance_std_unit_tokens`: r=0.123, q=0.0073 (n=660).
- `Extraversion` × `nuisance_chars_per_approx_token`: r=0.110, q=0.0406 (n=660).
- `Openness` × `nuisance_log_approx_tokens`: r=0.110, q=0.0141 (n=660).
- `TF_cont` × `v8_csr_15`: r=0.101, q=0.0000 (n=6599).
- `Openness` × `nuisance_mean_unit_tokens`: r=0.096, q=0.0312 (n=660).
- `TF_cont` × `v8_csr_08`: r=-0.090, q=0.0000 (n=6599).
- `JP_cont` × `nuisance_median_unit_tokens`: r=0.075, q=0.0000 (n=6599).
- `JP_cont` × `nuisance_mean_unit_tokens`: r=0.071, q=0.0000 (n=6599).
- `SN_cont` × `nuisance_chars_per_approx_token`: r=0.070, q=0.0000 (n=6599).

## Interpretation boundary

- A nonzero result is an association between a frozen text-geometry coordinate system and an external questionnaire anchor. It does not make the coordinate a named personality construct.
- PANDORA labels were used in earlier project phases. This run is therefore exploratory and cannot replenish the spent lockbox.
- Raw PANDORA contains subreddit metadata, but the frozen native scorer and this external connection do not model it. The nuisance comparator controls text volume and format, not full community/topic selection.
- The V8 representation and geometry were fitted label-free on a subset of MBTI-only authors. MBTI head CV is therefore unsupervised-transductive at the representation level, although no MBTI label entered the scorer.
- Bridge author-bootstrap intervals resample held-out bridge authors while conditioning on the fitted source heads. They do not include uncertainty from refitting Big5-only and MBTI-only heads.
- `support_eligible` rows are a declared sensitivity analysis that ignores the frozen radial-envelope refusal while retaining the minimum-unit rule.

## Reproduction

```bash
python scripts/run_suica_v8_pandora_external_connection.py --stage all
```

Detailed trait/axis rows, fold predictions, relation matrices, and the hash-bound score manifest are stored beside this report.
