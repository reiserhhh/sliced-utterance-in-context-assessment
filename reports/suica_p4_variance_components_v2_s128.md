# SUICA P4 Variance Components & React Signatures (v2)

> **AUDIT NOTICE (2026-07-04, round 2 — partially SUPERSEDED).** The MixedLM tension row in
> this report (condition share 45.3%) is a DEGENERATE fit (empirical condition eta^2 = 0.97%)
> and was struck from the record. Corrected reading: tension is ~95% slice-level residual,
> person ~2-5%. Authoritative record: docs/SUICA_CLAIMS_LEDGER.md (P4 row).


## MoM shares (grid)

| construct             |   person_share |   condition_share |   interaction_share |   residual_share |   person_share_ci_lo |   person_share_ci_hi |   interaction_share_ci_lo |   interaction_share_ci_hi |
|:----------------------|---------------:|------------------:|--------------------:|-----------------:|---------------------:|---------------------:|--------------------------:|--------------------------:|
| novelty_play_v2       |         0.013  |            0.0002 |              0      |           0.9868 |               0      |               0.0265 |                    0      |                    0      |
| directive_action_v2   |         0.0629 |            0.0143 |              0.0386 |           0.8843 |               0.0445 |               0.0846 |                    0.006  |                    0.0655 |
| adversity_recovery_v2 |         0.0146 |            0.0063 |              0      |           0.9791 |               0      |               0.0233 |                    0      |                    0.0646 |
| first_person_usage_v2 |         0.1715 |            0.0514 |              0.051  |           0.7261 |               0.1268 |               0.2158 |                    0.0191 |                    0.0751 |
| tension_core_v2       |         0.0457 |            0.0036 |              0      |           0.9508 |               0.0186 |               0.0662 |                    0      |                    0.0149 |

## React signatures (early vs late, shared conditions)

| construct             |   n_users |   median_signature_r |   mean_signature_r |   null_median_signature_r |
|:----------------------|----------:|---------------------:|-------------------:|--------------------------:|
| novelty_play_v2       |      1482 |               0.0091 |             0.0354 |                   -0.013  |
| directive_action_v2   |      1482 |               0.1042 |             0.0867 |                   -0.0016 |
| adversity_recovery_v2 |      1480 |               0.0604 |             0.0683 |                   -0.0134 |
| first_person_usage_v2 |      1482 |               0.1872 |             0.1475 |                   -0.0052 |
| tension_core_v2       |      1482 |               0.0164 |             0.01   |                   -0.0301 |

```json
{
  "interaction_ci_positive_count": 2,
  "react_median_ge_030_count": 0,
  "P4_verdict": "partial",
  "grid_fill": 0.4417910447761194,
  "mixedlm": {
    "first_person_usage_v2": {
      "person_share": 0.16165005098490018,
      "condition_share": 0.054819104209986744,
      "interaction_share": 0.10079788166908595,
      "residual_share": 0.6827329631360272,
      "n_rows": 3863
    },
    "tension_core_v2": {
      "person_share": 0.021343548347163826,
      "condition_share": 0.45329654316689993,
      "interaction_share": 0.0064197459171628285,
      "residual_share": 0.5189401625687735,
      "n_rows": 3863
    }
  }
}
```

> **Audit note (2026-07-04):** the MixedLM tension row in this report was found to be a degenerate fit by the independent audit (empirical condition eta^2 = 0.97% vs the fitted 45.3%). See docs/SUICA_CLAIMS_LEDGER.md P4 row for the corrected reading: tension is ~95% slice-level residual; person share ~2-5%.
