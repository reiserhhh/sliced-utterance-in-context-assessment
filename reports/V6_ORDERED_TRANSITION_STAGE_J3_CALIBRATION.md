# SUICA V6 Ordered-Transition J3: Synthetic Calibration

This calibration contains no human text or endpoint label. It asks whether the
centred ordered-transition operator can distinguish a stable author-specific
autoregressive signature from its within-block order null at each support level.

## Decision

`REFUSE_NO_CALIBRATED_ORDER_SUPPORT`. Selected per-view support: `None`.

## Grid

|   events_per_view |   total_events_for_disjoint_views |   simulations |   n_authors |   weak_delta_auc_median |   weak_delta_auc_q05 |   moderate_delta_auc_median |   moderate_delta_auc_q05 |   null_delta_auc_median |   null_delta_auc_q95 |   weak_delta_over_null_median |   moderate_q05_over_null_q95 | qualified   |
|------------------:|----------------------------------:|--------------:|------------:|------------------------:|---------------------:|----------------------------:|-------------------------:|------------------------:|---------------------:|------------------------------:|-----------------------------:|:------------|
|                24 |                                48 |            60 |         300 |                  0.0003 |              -0.0295 |                      0.0129 |                  -0.0066 |                  0.0001 |               0.0236 |                        0.0002 |                      -0.0302 | False       |
|                48 |                                96 |            60 |         300 |                  0.0071 |              -0.0224 |                      0.0219 |                   0.0004 |                  0.0027 |               0.027  |                        0.0045 |                      -0.0265 | False       |
|                72 |                               144 |            60 |         300 |                  0.0062 |              -0.0189 |                      0.0268 |                   0.0055 |                  0.0027 |               0.0278 |                        0.0035 |                      -0.0222 | False       |
|                96 |                               192 |            60 |         300 |                  0.0084 |              -0.018  |                      0.0284 |                   0.0098 |                 -0.0023 |               0.0222 |                        0.0107 |                      -0.0124 | False       |
|               120 |                               240 |            60 |         300 |                  0.0097 |              -0.0129 |                      0.0267 |                   0.0116 |                  0.0028 |               0.0312 |                        0.007  |                      -0.0196 | False       |
|               144 |                               288 |            60 |         300 |                  0.0059 |              -0.0166 |                      0.0288 |                   0.013  |                  0      |               0.0234 |                        0.0059 |                      -0.0104 | False       |

## Boundary

The synthetic author transition deviations are a declared estimator stress test,
not a model of a person or proof that PANDORA contains the same mechanism.
