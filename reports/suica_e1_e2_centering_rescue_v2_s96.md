# SUICA E1/E2 Centering Rescue (exploration)

> **AUDIT NOTICE (2026-07-05, round 3 — the FE-rescue result below is OVERTURNED).**
> Same self-estimation leak as the s128 run; out-of-sample deltas are negative. The s96
> "replication" replicates the artifact, not a real effect. Authoritative record:
> docs/SUICA_CLAIMS_LEDGER.md (E1-R1 rows, OVERTURNED).


## E1 lexicon arms

| construct             |   n_users |   r_raw |   r_naive |   r_fe |   delta_fe_vs_raw |   fe_ci_lo |   fe_ci_hi |   delta_naive_vs_raw |   naive_ci_lo |   naive_ci_hi |
|:----------------------|----------:|--------:|----------:|-------:|------------------:|-----------:|-----------:|---------------------:|--------------:|--------------:|
| novelty_play_v2       |      4080 |  0.3053 |    0.0773 | 0.1699 |           -0.1354 |    -0.1641 |    -0.1045 |              -0.228  |       -0.2604 |       -0.1919 |
| directive_action_v2   |      4080 |  0.3488 |    0.2777 | 0.3828 |            0.0341 |     0.0153 |     0.0544 |              -0.0711 |       -0.0945 |       -0.05   |
| adversity_recovery_v2 |      4080 |  0.0994 |    0.0685 | 0.1441 |            0.0447 |     0.0279 |     0.0629 |              -0.0309 |       -0.0472 |       -0.0166 |
| first_person_usage_v2 |      4080 |  0.6232 |    0.5193 | 0.6501 |            0.0269 |     0.013  |     0.0406 |              -0.1039 |       -0.1219 |       -0.0846 |
| tension_core_v2       |      4080 |  0.2814 |    0.2475 | 0.3351 |            0.0537 |     0.0413 |     0.0679 |              -0.0339 |       -0.0478 |       -0.019  |

## E2 lambda curve

| construct             |    0.0 |   0.25 |    0.5 |   0.75 |    1.0 |
|:----------------------|-------:|-------:|-------:|-------:|-------:|
| adversity_recovery_v2 | 0.0994 | 0.0914 | 0.0833 | 0.0755 | 0.0685 |
| directive_action_v2   | 0.3488 | 0.3389 | 0.3231 | 0.3021 | 0.2777 |
| first_person_usage_v2 | 0.6232 | 0.6196 | 0.6024 | 0.5687 | 0.5193 |
| novelty_play_v2       | 0.3053 | 0.2528 | 0.1896 | 0.1259 | 0.0773 |
| tension_core_v2       | 0.2814 | 0.2773 | 0.27   | 0.2599 | 0.2475 |

## E1 occupancy arms

```json
{
  "n_users": 4080,
  "mean_node_r": {
    "raw": 0.13913096336494635,
    "naive": 0.0973872268156019,
    "fe": 0.19796542428572197
  },
  "delta_fe_vs_raw": 0.05883446092077563,
  "fe_ci": [
    0.05394230871902214,
    0.06368377082631772
  ],
  "delta_naive_vs_raw": -0.04174373654934445,
  "naive_ci": [
    -0.0460462412902427,
    -0.03738966212912073
  ]
}
```

## P1 temporal retest, FE vs raw

| construct             |   p1_r_raw |   p1_r_fe |
|:----------------------|-----------:|----------:|
| novelty_play_v2       |     0.4266 |    0.108  |
| directive_action_v2   |     0.4022 |    0.2514 |
| adversity_recovery_v2 |     0.1062 |    0.0255 |
| first_person_usage_v2 |     0.6918 |    0.5217 |
| tension_core_v2       |     0.24   |    0.1637 |
