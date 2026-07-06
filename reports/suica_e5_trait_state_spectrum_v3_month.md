# SUICA E5 Trait-State Spectrum (rind-fixed: top subreddit; occasions: quarters)

> **AUDIT NOTICE (2026-07-05, round 4).** Same estimator caveats as the quarter report:
> MoM under-detects small state shares; use the MixedLM-corrected values in
> docs/SUICA_CLAIMS_LEDGER.md (E5 rows). Ordering conclusions unchanged.


| construct             |   trait_share | trait_ci      |   era_share |   state_share | state_ci      |   slice_noise_share |   state_trait_ratio |
|:----------------------|--------------:|:--------------|------------:|--------------:|:--------------|--------------------:|--------------------:|
| novelty_play_v2       |        0.1821 | [0.166,0.199] |      0      |        0.0395 | [0.027,0.050] |              0.7784 |              0.2168 |
| directive_action_v2   |        0.1636 | [0.151,0.176] |      0      |        0.0109 | [0.002,0.019] |              0.8255 |              0.0669 |
| adversity_recovery_v2 |        0.0822 | [0.060,0.110] |      0      |        0.0149 | [0.000,0.032] |              0.9029 |              0.1813 |
| first_person_usage_v2 |        0.3551 | [0.342,0.366] |      0.0008 |        0.0588 | [0.052,0.064] |              0.5853 |              0.1657 |
| tension_core_v2       |        0.0962 | [0.089,0.103] |      0      |        0.0098 | [0.000,0.018] |              0.8941 |              0.1017 |

## Per-occasion state precision (trait removed)

| construct             |   n_user_quarters |   state_split_half_r |   state_sb_full |
|:----------------------|------------------:|---------------------:|----------------:|
| novelty_play_v2       |             10628 |               0.1029 |          0.1866 |
| directive_action_v2   |             10628 |               0.222  |          0.3633 |
| adversity_recovery_v2 |             10628 |               0.0917 |          0.168  |
| first_person_usage_v2 |             10628 |               0.3905 |          0.5616 |
| tension_core_v2       |             10628 |               0.0997 |          0.1813 |

```json
{
  "P_E5a_firstperson_trait_gt_state": true,
  "P_E5b_tension_stateratio_gt_firstperson": false,
  "P_E5c_tension_state_split_half": 0.09967782369269905
}
```
