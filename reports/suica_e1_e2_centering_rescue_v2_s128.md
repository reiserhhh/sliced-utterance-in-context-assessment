# SUICA E1/E2 Centering Rescue (exploration)

> **AUDIT NOTICE (2026-07-05, round 3 — the FE-rescue result below is OVERTURNED).**
> The positive delta_fe_vs_raw values in this report are a SELF-ESTIMATION LEAK (condition
> effects were estimated on pooled A+B slices). Out-of-sample estimation (cross-fit /
> user-fold) flips every construct negative (-0.046..-0.074; occupancy -0.071/-0.062).
> No form of condition centering adds stability on this data. Authoritative record:
> docs/SUICA_CLAIMS_LEDGER.md (E1-R1 rows, OVERTURNED).


## E1 lexicon arms

| construct             |   n_users |   r_raw |   r_naive |   r_fe |   delta_fe_vs_raw |   fe_ci_lo |   fe_ci_hi |   delta_naive_vs_raw |   naive_ci_lo |   naive_ci_hi |
|:----------------------|----------:|--------:|----------:|-------:|------------------:|-----------:|-----------:|---------------------:|--------------:|--------------:|
| novelty_play_v2       |      3726 |  0.3123 |    0.1005 | 0.1952 |           -0.1171 |    -0.1509 |    -0.0828 |              -0.2118 |       -0.2464 |       -0.1724 |
| directive_action_v2   |      3726 |  0.3766 |    0.3114 | 0.4244 |            0.0478 |     0.0286 |     0.0703 |              -0.0652 |       -0.0894 |       -0.0404 |
| adversity_recovery_v2 |      3726 |  0.1055 |    0.0593 | 0.1546 |            0.049  |     0.0315 |     0.0659 |              -0.0462 |       -0.065  |       -0.0271 |
| first_person_usage_v2 |      3726 |  0.6535 |    0.5538 | 0.6907 |            0.0372 |     0.025  |     0.0501 |              -0.0996 |       -0.1188 |       -0.0829 |
| tension_core_v2       |      3726 |  0.3061 |    0.2733 | 0.3697 |            0.0636 |     0.0476 |     0.0777 |              -0.0328 |       -0.0465 |       -0.0166 |

## E2 lambda curve

| construct             |    0.0 |   0.25 |    0.5 |   0.75 |    1.0 |
|:----------------------|-------:|-------:|-------:|-------:|-------:|
| adversity_recovery_v2 | 0.1055 | 0.0935 | 0.0812 | 0.0696 | 0.0593 |
| directive_action_v2   | 0.3766 | 0.3696 | 0.356  | 0.3359 | 0.3114 |
| first_person_usage_v2 | 0.6535 | 0.6528 | 0.6377 | 0.6045 | 0.5538 |
| novelty_play_v2       | 0.3123 | 0.2641 | 0.2047 | 0.1445 | 0.1005 |
| tension_core_v2       | 0.3061 | 0.3025 | 0.2957 | 0.2857 | 0.2733 |

## E1 occupancy arms

```json
{
  "n_users": 3726,
  "mean_node_r": {
    "raw": 0.17830980428181512,
    "naive": 0.1167752295481143,
    "fe": 0.23128154822991165
  },
  "delta_fe_vs_raw": 0.052971743948096534,
  "fe_ci": [
    0.047361117081924635,
    0.05845229398384283
  ],
  "delta_naive_vs_raw": -0.06153457473370082,
  "naive_ci": [
    -0.06713055322274653,
    -0.05611185139627459
  ]
}
```

## P1 temporal retest, FE vs raw

| construct             |   p1_r_raw |   p1_r_fe |
|:----------------------|-----------:|----------:|
| novelty_play_v2       |     0.4742 |    0.1505 |
| directive_action_v2   |     0.4584 |    0.3059 |
| adversity_recovery_v2 |     0.1087 |    0.0507 |
| first_person_usage_v2 |     0.7299 |    0.5473 |
| tension_core_v2       |     0.2831 |    0.1993 |
