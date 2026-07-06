# SUICA E11 shuffled-score-fit null geometry (round-7 closure)

## trait mode (n_targets=19, n_perm=200)

| axis | old thr (random dir) | new thr (shuffled fit) | ratio | FPR of old bar |
|---|---|---|---|---|
| E | 0.0759 | 0.0534 | 0.70 | 0.0003 |
| A | 0.0777 | 0.0462 | 0.59 | 0.0000 |
| C | 0.0717 | 0.0464 | 0.65 | 0.0000 |
| N | 0.0652 | 0.0534 | 0.82 | 0.0013 |
| O | 0.0762 | 0.0517 | 0.68 | 0.0003 |

- old bar defective by D1: **False**
- V2-2 significant targets: old 1 -> fitted-null 7

Recount changes:
- tension_core_v2: 0 -> 1 (C-0.050)
- novelty_play_v2: 0 -> 2 (E+0.068;O+0.069)
- wcl_03: 0 -> 2 (E+0.057;O+0.072)
- wcl_11: 0 -> 1 (O-0.061)
- wcl_02: 0 -> 3 (A+0.051;C+0.064;N-0.061)
- wcl_13: 1 -> 3 (E-0.056;C-0.068;O-0.094)
- wcl_23: 0 -> 2 (A-0.057;C-0.047)

## state mode (n_targets=3, n_perm=200)

| axis | old thr (random dir) | new thr (shuffled fit) | ratio | FPR of old bar |
|---|---|---|---|---|
| E | 0.0759 | 0.0254 | 0.33 | 0.0000 |
| A | 0.0777 | 0.0213 | 0.27 | 0.0000 |
| C | 0.0717 | 0.0237 | 0.33 | 0.0000 |
| N | 0.0652 | 0.0257 | 0.39 | 0.0000 |
| O | 0.0762 | 0.0264 | 0.35 | 0.0000 |

- old bar defective by D1: **False**
- V2-2 significant targets: old 0 -> fitted-null 1

Recount changes:
- state_f5: 0 -> 2 (A-0.023;C-0.032)

