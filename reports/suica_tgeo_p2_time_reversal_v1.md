# T-GEO-P2 — time-reversal (drift) null on PANDORA (label-free)

Per-user OLS slope of block-mean construct value on block time (K=4
equal-count blocks, span >= 180 days); sign-flip null (2000 draws).
Arm 'pooled' confounds style drift with venue-mix drift; arm 'top1'
holds the venue constant.

| arm | construct | n | mean slope /yr | frac>0 | p (sign-flip) |
|---|---|---|---|---|---|
| pooled | tension_core_v2 | 4454 | -0.0163 | 0.47 | 0.0000 |
| pooled | directive_action_v2 | 4454 | -0.0362 | 0.46 | 0.0000 |
| pooled | first_person_usage_v2 | 4454 | -0.2244 | 0.40 | 0.0000 |
| pooled | novelty_play_v2 | 4454 | -0.0061 | 0.48 | 0.1620 |
| top1 | tension_core_v2 | 3278 | -0.0097 | 0.48 | 0.1585 |
| top1 | directive_action_v2 | 3278 | +0.0118 | 0.49 | 0.3725 |
| top1 | first_person_usage_v2 | 3278 | -0.2467 | 0.43 | 0.0000 |
| top1 | novelty_play_v2 | 3278 | +0.0145 | 0.48 | 0.0490 |
