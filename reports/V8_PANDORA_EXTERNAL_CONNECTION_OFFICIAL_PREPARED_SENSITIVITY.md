# SUICA V8 Full PANDORA External Connection

Status: `OPENED_PANDORA_EXPLORATORY_EXTERNAL_CONNECTION`

## Design

The frozen V8 canonical scale-residual geometry was scored before labels were joined. Big5-only authors were used for Big Five heads, MBTI-only authors for four binary axis heads, and strict both-label authors only for the held-out Big5↔MBTI structural bridge. Official repeat-0 folds were used for source-task CV. Every head was fitted inside its training fold; the V8 geometry and representation were never refitted.

Claim boundary: This is an exploratory external connection on previously opened PANDORA labels. It tests frozen V8 text geometry against external Big Five and MBTI anchors; it cannot confirm, name, rotate, or select a psychological construct.

## Coverage

- Frozen score authors: 10090
- Geometry-ready authors: 3813
- Big5-only ready: 315
- MBTI-only ready (minimum across axes): 3420
- Strict bridge ready: 78

## Primary official-fold results

| View | Big5 mean r | MBTI mean AUC | MBTI mean balanced accuracy | Bridge element r | Bridge permutation p |
|---|---:|---:|---:|---:|---:|
| v8_canonical | 0.023 | 0.526 | 0.521 | -0.103 | 0.6731 |
| nuisance_only | 0.061 | 0.563 | 0.545 | 0.384 | 0.0280 |
| v8_plus_nuisance | 0.059 | 0.560 | 0.539 | 0.463 | 0.0090 |
| v7_author48_upper_bound | 0.033 | 0.592 | 0.567 | 0.438 | 0.0074 |

The 48-coordinate V7 row is an upstream representation upper bound, not the invariant SUICA score. Nuisance-only uses text amount and format opportunity variables. V8+nuisance tests incremental complementarity.

## Coordinate screen

- Ready-cohort V8/nuisance tests passing within-target-view BH-FDR: 14.
- `Openness` × `nuisance_chars_per_approx_token`: r=0.216, q=0.0010 (n=315).
- `Agreeableness` × `nuisance_punctuation_ratio`: r=0.167, q=0.0269 (n=315).
- `TF_cont` × `nuisance_chars_per_approx_token`: r=-0.134, q=0.0000 (n=3420).
- `TF_cont` × `v8_csr_15`: r=0.092, q=0.0000 (n=3420).
- `JP_cont` × `nuisance_log_sampled_comments`: r=-0.085, q=0.0000 (n=3420).
- `TF_cont` × `v8_csr_08`: r=-0.077, q=0.0001 (n=3420).
- `JP_cont` × `nuisance_mean_unit_tokens`: r=0.069, q=0.0003 (n=3420).
- `SN_cont` × `nuisance_mean_unit_tokens`: r=0.058, q=0.0066 (n=3420).
- `SN_cont` × `nuisance_std_unit_tokens`: r=0.053, q=0.0088 (n=3420).
- `JP_cont` × `nuisance_median_unit_tokens`: r=0.051, q=0.0080 (n=3420).
- `EI_cont` × `nuisance_chars_per_approx_token`: r=-0.049, q=0.0391 (n=3420).
- `JP_cont` × `nuisance_std_unit_tokens`: r=0.043, q=0.0274 (n=3420).

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
