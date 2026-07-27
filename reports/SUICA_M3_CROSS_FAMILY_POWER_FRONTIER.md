# SUICA M3 Cross-Family Event-Power Frontier

Decision: `M3_CROSS_FAMILY_POWER_FRONTIER_PARTIAL`

## Selected minimum events

```json
{
  "cf_d_copula": 1024,
  "cf_d_multimodal": 256,
  "cf_kp_arch": 2048,
  "cf_kp_hsmm": null
}
```

## Frontier

| family       | world           |   events |   seeds |    power |   expected_auc |   cheap_auc |   expected_geometry |   delta_auc |   second_order_max_range |
|:-------------|:----------------|---------:|--------:|---------:|---------------:|------------:|--------------------:|------------:|-------------------------:|
| distribution | cf_d_copula     |      256 |       6 | 0        |       0.538781 |    0.480287 |            0.127038 |   0.0584943 |              0           |
| distribution | cf_d_copula     |      512 |       6 | 0.333333 |       0.605567 |    0.516914 |            0.285383 |   0.0886528 |              0           |
| distribution | cf_d_copula     |     1024 |       6 | 1        |       0.706863 |    0.496091 |            0.468682 |   0.210773  |              0           |
| distribution | cf_d_multimodal |      256 |       6 | 0.833333 |       0.678958 |    0.493627 |            0.452004 |   0.185331  |              0           |
| distribution | cf_d_multimodal |      512 |       6 | 1        |       0.765788 |    0.483294 |            0.619189 |   0.282493  |              0           |
| distribution | cf_d_multimodal |     1024 |       6 | 1        |       0.877701 |    0.489799 |            0.868542 |   0.387902  |              0           |
| path         | cf_kp_arch      |      512 |       6 | 0        |       0.575237 |    0.5      |            0.321028 |   0.0752366 |              2.22045e-16 |
| path         | cf_kp_arch      |     1024 |       6 | 0.666667 |       0.623126 |    0.5      |            0.423879 |   0.123126  |              4.44089e-16 |
| path         | cf_kp_arch      |     2048 |       6 | 1        |       0.637214 |    0.5      |            0.457315 |   0.137214  |              3.33067e-16 |
| path         | cf_kp_hsmm      |      512 |       6 | 0.166667 |       0.588255 |    0.514517 |            0.280244 |   0.0737379 |              1.11022e-16 |
| path         | cf_kp_hsmm      |     1024 |       6 | 0        |       0.599328 |    0.537841 |            0.271528 |   0.0614869 |              1.11022e-16 |
| path         | cf_kp_hsmm      |     2048 |       6 | 0.166667 |       0.600997 |    0.510456 |            0.280062 |   0.0905413 |              1.11022e-16 |

## Boundary

These are public development seeds used only to select a prospective event
budget. They cannot appear in the fresh confirmation.
