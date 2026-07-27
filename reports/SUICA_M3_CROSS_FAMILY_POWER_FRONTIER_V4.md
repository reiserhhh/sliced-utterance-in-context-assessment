# SUICA M3 Cross-Family Event-Power Frontier

Decision: `M3_CROSS_FAMILY_POWER_FRONTIER_RESOLVED`

## Selected minimum events

```json
{
  "cf_d_multimodal": 1024,
  "cf_d_tail": 1024,
  "cf_kp_arch": 1024
}
```

## Frontier

| family       | world           |   events |   seeds |    power |   expected_auc |   cheap_auc |   expected_geometry |   delta_auc |   heldout_increment |   positive_increment_fraction |   theoretical_lag02_max_range |
|:-------------|:----------------|---------:|--------:|---------:|---------------:|------------:|--------------------:|------------:|--------------------:|------------------------------:|------------------------------:|
| distribution | cf_d_multimodal |      512 |       6 | 0.166667 |       0.585368 |    0.512819 |            0.278767 |   0.0725498 |         0.0159262   |                      1        |                             0 |
| distribution | cf_d_multimodal |     1024 |       6 | 1        |       0.666478 |    0.485104 |            0.462913 |   0.181375  |         0.0191441   |                      1        |                             0 |
| distribution | cf_d_tail       |      512 |       6 | 0.166667 |       0.598464 |    0.495877 |            0.27759  |   0.102587  |         0.0159497   |                      1        |                             0 |
| distribution | cf_d_tail       |     1024 |       6 | 1        |       0.66077  |    0.480581 |            0.435284 |   0.180189  |         0.018869    |                      1        |                             0 |
| path         | cf_kp_arch      |      512 |       6 | 0.333333 |       0.689275 |    0.50318  |            0.658139 |   0.186095  |         1.2598e-06  |                      0.333333 |                             0 |
| path         | cf_kp_arch      |     1024 |       6 | 0.833333 |       0.75833  |    0.515725 |            0.795635 |   0.242605  |         2.32782e-06 |                      0.833333 |                             0 |

## Boundary

These are public development seeds used only to select a prospective event
budget. They cannot appear in the fresh confirmation.
