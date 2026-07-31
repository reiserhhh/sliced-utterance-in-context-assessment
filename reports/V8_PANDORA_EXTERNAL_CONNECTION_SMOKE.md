# SUICA V8 Full PANDORA External Connection

Status: `OPENED_PANDORA_EXPLORATORY_EXTERNAL_CONNECTION`

## Design

The frozen V8 canonical scale-residual geometry was scored before labels were joined. Big5-only authors were used for Big Five heads, MBTI-only authors for four binary axis heads, and strict both-label authors only for the held-out Big5↔MBTI structural bridge. Official repeat-0 folds were used for source-task CV. Every head was fitted inside its training fold; the V8 geometry and representation were never refitted.

Claim boundary: This is an exploratory external connection on previously opened PANDORA labels. It tests frozen V8 text geometry against external Big Five and MBTI anchors; it cannot confirm, name, rotate, or select a psychological construct.

## Coverage

- Frozen score authors: 812
- Geometry-ready authors: 251
- Big5-only ready: 64
- MBTI-only ready (minimum across axes): 119
- Strict bridge ready: 68

## Primary official-fold results

| View | Big5 mean r | MBTI mean AUC | MBTI mean balanced accuracy | Bridge element r | Bridge permutation p |
|---|---:|---:|---:|---:|---:|
| v8_canonical | -0.048 | 0.499 | 0.501 | 0.223 | 0.2300 |
| nuisance_only | 0.016 | 0.564 | 0.535 | 0.038 | 0.4300 |
| v8_plus_nuisance | -0.063 | 0.571 | 0.545 | -0.142 | 0.7200 |
| v7_author48_upper_bound | -0.024 | 0.546 | 0.554 | 0.077 | 0.4200 |

The 48-coordinate V7 row is an upstream representation upper bound, not the invariant SUICA score. Nuisance-only uses text amount and format opportunity variables. V8+nuisance tests incremental complementarity.

## Coordinate screen

- Ready-cohort V8/nuisance tests passing within-target-view BH-FDR: 1.
- `JP_cont` × `nuisance_log_sampled_comments`: r=-0.279, q=0.0193 (n=119).

## Interpretation boundary

- A nonzero result is an association between a frozen text-geometry coordinate system and an external questionnaire anchor. It does not make the coordinate a named personality construct.
- PANDORA labels were used in earlier project phases. This run is therefore exploratory and cannot replenish the spent lockbox.
- The prepared official files preserve sampled, leakage-cleaned comments but do not retain subreddit/topic metadata. The nuisance comparator controls text volume and format, not full community/topic selection.
- `support_eligible` rows are a declared sensitivity analysis that ignores the frozen radial-envelope refusal while retaining the minimum-unit rule.

## Reproduction

```bash
python scripts/run_suica_v8_pandora_external_connection.py --stage all
```

Detailed trait/axis rows, fold predictions, relation matrices, and the hash-bound score manifest are stored beside this report.
