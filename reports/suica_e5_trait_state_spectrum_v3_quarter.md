# SUICA E5 Trait-State Spectrum (rind-fixed: top subreddit; occasions: quarters)

> **AUDIT NOTICE (2026-07-05, round 4 — MoM point estimates below are biased in this regime).**
> The MoM estimator is blind to state shares < ~0.05 on this thin-cell layout and inflates
> trait by ~+0.04; the "state 0.000 (CI upper 0.002)" style precision is NOT supported.
> Corrected MixedLM values (month): first_person trait ~0.33 / state ~0.10; tension state
> <= ~2%. Channel ordering is unchanged. Parity split-half state precisions are ~2.5x
> inflated by same-text adjacency (contiguous first_person SB = 0.27). Authoritative
> record: docs/SUICA_CLAIMS_LEDGER.md (E5 rows).


| construct             |   trait_share | trait_ci      |   era_share |   state_share | state_ci      |   slice_noise_share |   state_trait_ratio |
|:----------------------|--------------:|:--------------|------------:|--------------:|:--------------|--------------------:|--------------------:|
| novelty_play_v2       |        0.1515 | [0.137,0.164] |      0      |        0.0247 | [0.014,0.035] |              0.8238 |              0.1629 |
| directive_action_v2   |        0.1557 | [0.143,0.165] |      0.0002 |        0.0028 | [0.000,0.010] |              0.8414 |              0.0179 |
| adversity_recovery_v2 |        0.0667 | [0.053,0.083] |      0      |        0.0041 | [0.000,0.022] |              0.9292 |              0.062  |
| first_person_usage_v2 |        0.3462 | [0.334,0.359] |      0.0018 |        0.0416 | [0.035,0.046] |              0.6104 |              0.1203 |
| tension_core_v2       |        0.0884 | [0.081,0.098] |      0.0002 |        0      | [0.000,0.002] |              0.9115 |              0      |

## Per-occasion state precision (trait removed)

| construct             |   n_user_quarters |   state_split_half_r |   state_sb_full |
|:----------------------|------------------:|---------------------:|----------------:|
| novelty_play_v2       |              8802 |               0.1206 |          0.2152 |
| directive_action_v2   |              8802 |               0.2275 |          0.3706 |
| adversity_recovery_v2 |              8802 |               0.0922 |          0.1689 |
| first_person_usage_v2 |              8802 |               0.3521 |          0.5208 |
| tension_core_v2       |              8802 |               0.0755 |          0.1404 |

```json
{
  "P_E5a_firstperson_trait_gt_state": true,
  "P_E5b_tension_stateratio_gt_firstperson": false,
  "P_E5c_tension_state_split_half": 0.07550755268554303
}
```
