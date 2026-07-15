# SUICA V6 Joint-Process J1: Synthetic Support Calibration

## Scope

This simulation selects a minimum natural-event support threshold for the
declared kernel-mean joint-process estimator. It checks a null world plus
weak and moderate author-conditioned worlds. It is not evidence about human
personality, clinical state, language equivalence, or PANDORA.

## Frozen decision

`CALIBRATED`. Selected support: `{'min_events': 24, 'min_transitions': 8}`.

## Calibration grid

|   min_events |   min_transitions |   simulations |   n_authors |   weak_auc_median |   weak_auc_q05 |   moderate_auc_median |   moderate_auc_q05 |   null_auc_median |   null_auc_q95 |   null_promotion_rate | qualified   |
|-------------:|------------------:|--------------:|------------:|------------------:|---------------:|----------------------:|-------------------:|------------------:|---------------:|----------------------:|:------------|
|           24 |                 8 |            80 |         300 |            0.5434 |         0.5228 |                0.6513 |             0.6245 |            0.4992 |         0.5165 |                     0 | True        |
|           48 |                16 |            80 |         300 |            0.5865 |         0.5648 |                0.762  |             0.731  |            0.4965 |         0.5176 |                     0 | True        |
|           72 |                24 |            80 |         300 |            0.6301 |         0.5937 |                0.833  |             0.8018 |            0.4993 |         0.52   |                     0 | True        |
|           96 |                32 |            80 |         300 |            0.6556 |         0.632  |                0.8791 |             0.849  |            0.4997 |         0.5206 |                     0 | True        |
|          120 |                40 |            80 |         300 |            0.693  |         0.6572 |                0.9171 |             0.8936 |            0.5014 |         0.5166 |                     0 | True        |

## Interpretation boundary

The synthetic worlds vary only the magnitude of stable author-specific
selection preferences, expression offsets, and transition persistence. The
resulting threshold only rules out clearly under-supported estimators in these
declared worlds. It cannot justify a human interpretation or separate latent
topic from expression in real text.
