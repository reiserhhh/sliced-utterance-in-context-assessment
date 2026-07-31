# V8 Exchangeable Background Audit

Status: `EXCHANGEABLE_NULL_AUDIT_COMPLETED`

The historical no-self cyclic knockout is rerun with uniform within-block permutations. Fixed points and the natural identity assignment belong to the corrected null support.

## Decision

```json
{
  "status": "EXCHANGEABLE_NULL_AUDIT_COMPLETED",
  "marginal_status": "MULTI_CORPUS_SIGNED_CONCORDANCE_DETECTED",
  "marginal_corpus_status": {
    "pandora": "SIGNED_CONCORDANCE_RESIDUAL_DETECTED",
    "essays": "SIGNED_CONCORDANCE_RESIDUAL_DETECTED",
    "x_market": "SIGNED_CONCORDANCE_RESIDUAL_DETECTED"
  },
  "spectrum_status": "ONE_CORPUS_LOCAL_POSITIVE_SPECTRUM_REPLICATED",
  "spectrum_corpus_status": {
    "pandora": "POSITIVE_SPECTRUM_UNDERRESOLVED",
    "essays": "POSITIVE_SPECTRUM_UNDERRESOLVED",
    "x_market": "FROZEN_POSITIVE_SPECTRUM_REPLICATED"
  },
  "mean_fixed_point_fraction": 0.05939106401200066,
  "identity_blocks_observed": 0,
  "version": "v8-exchangeable-background-audit-1",
  "timestamp_utc": "2026-07-29T18:13:29.750186+00:00",
  "claim_boundary": "Opened-panel exchangeability correction. It compares the historical no-self cyclic knockout with a uniform within-block permutation distribution whose support includes fixed points and the natural identity assignment. It can correct the technical null interpretation but cannot confirm a personality, emotion, cognition, causal, cross-corpus, diagnostic, or clinical claim."
}
```

## Historical comparison

| corpus   | split   |   link_delta_cyclic |   link_max_t_p_cyclic |   link_bootstrap_lcb_cyclic |   link_delta_exchangeable |   link_max_t_p_exchangeable |   link_bootstrap_lcb_exchangeable | family            |   delta_cyclic |   max_t_p_cyclic |   bootstrap_lcb_cyclic |   delta_exchangeable |   max_t_p_exchangeable |   bootstrap_lcb_exchangeable |
|:---------|:--------|--------------------:|----------------------:|----------------------------:|--------------------------:|----------------------------:|----------------------------------:|:------------------|---------------:|-----------------:|-----------------------:|---------------------:|-----------------------:|-----------------------------:|
| pandora  | D1      |           0.0167569 |                0.005  |                 0.000280433 |                 0.0165011 |                      0.006  |                        0.00179754 | signed_link       |     nan        |         nan      |             nan        |           nan        |               nan      |                   nan        |
| pandora  | D2      |           0.0154622 |                0.011  |                -6.7435e-05  |                 0.0153313 |                      0.0165 |                        0.00037289 | signed_link       |     nan        |         nan      |             nan        |           nan        |               nan      |                   nan        |
| essays   | D1      |           0.0626232 |                0.0005 |                 0.0497117   |                 0.0629856 |                      0.0005 |                        0.0495406  | signed_link       |     nan        |         nan      |             nan        |           nan        |               nan      |                   nan        |
| essays   | D2      |           0.0723414 |                0.0005 |                 0.0577501   |                 0.0729869 |                      0.0005 |                        0.0597409  | signed_link       |     nan        |         nan      |             nan        |           nan        |               nan      |                   nan        |
| x_market | D1      |           0.207977  |                0.0005 |                 0.131359    |                 0.209734  |                      0.0005 |                        0.130956   | signed_link       |     nan        |         nan      |             nan        |           nan        |               nan      |                   nan        |
| x_market | D2      |           0.224225  |                0.0005 |                 0.128326    |                 0.228872  |                      0.0005 |                        0.140598   | signed_link       |     nan        |         nan      |             nan        |           nan        |               nan      |                   nan        |
| x_market | D1      |         nan         |              nan      |               nan           |               nan         |                    nan      |                      nan          | positive_spectrum |       0.589601 |           0.0005 |               0.219009 |             0.599052 |                 0.0005 |                     0.244953 |
| x_market | D2      |         nan         |              nan      |               nan           |               nan         |                    nan      |                      nan          | positive_spectrum |       0.455929 |           0.0005 |               0.15208  |             0.463702 |                 0.0005 |                     0.171744 |

## Corrected marginal cells

| corpus   | split   | view   |   observed_frobenius |   observed_operator_norm |   observed_effective_rank |   observed_link |   observed_same_author_auc |   pseudo_mean_frobenius |   pseudo_mean_operator_norm |   pseudo_mean_effective_rank |   pseudo_mean_link |   pseudo_mean_same_author_auc |   frobenius_delta |   link_delta |   frobenius_raw_p |   link_raw_p |   auc_raw_p |   frobenius_max_t_p |   link_max_t_p |   frobenius_bootstrap_lcb |   frobenius_bootstrap_mean |   link_bootstrap_lcb |   link_bootstrap_mean |
|:---------|:--------|:-------|---------------------:|-------------------------:|--------------------------:|----------------:|---------------------------:|------------------------:|----------------------------:|-----------------------------:|-------------------:|------------------------------:|------------------:|-------------:|------------------:|-------------:|------------:|--------------------:|---------------:|--------------------------:|---------------------------:|---------------------:|----------------------:|
| pandora  | D1      | M_all  |              9.22981 |                  2.13537 |                  18.6828  |       0.0205194 |                   0.560757 |                 9.12346 |                     1.93599 |                     22.2851  |         0.00401833 |                           nan |         0.106352  |    0.0165011 |            0.0565 |       0.0005 |         nan |              0.294  |         0.006  |                -0.305045  |                  0.0973751 |           0.00179754 |             0.0164898 |
| pandora  | D2      | M_all  |              9.61071 |                  2.13391 |                  20.2842  |       0.0200525 |                   0.559307 |                 9.54268 |                     2.06086 |                     21.5166  |         0.00472117 |                           nan |         0.0680246 |    0.0153313 |            0.1555 |       0.002  |         nan |              0.6305 |         0.0165 |                -0.315926  |                  0.0790279 |           0.00037289 |             0.0145878 |
| essays   | D1      | M_all  |              8.20211 |                  1.84923 |                  19.6729  |       0.068542  |                   0.690632 |                 7.97613 |                     1.61745 |                     24.3653  |         0.00555632 |                           nan |         0.225987  |    0.0629856 |            0.0005 |       0.0005 |         nan |              0.0015 |         0.0005 |                -0.0727091 |                  0.235282  |           0.0495406  |             0.0633929 |
| essays   | D2      | M_all  |              8.54739 |                  2.11536 |                  16.3267  |       0.0773929 |                   0.709871 |                 8.02519 |                     1.62252 |                     24.5104  |         0.00440603 |                           nan |         0.522205  |    0.0729869 |            0.0005 |       0.0005 |         nan |              0.0005 |         0.0005 |                 0.197528  |                  0.487057  |           0.0597409  |             0.0734009 |
| x_market | D1      | M_all  |             31.7172  |                 12.3493  |                   6.59635 |       0.244302  |                   0.787828 |                27.9257  |                     9.46569 |                      8.7381  |         0.0345682  |                           nan |         3.7915    |    0.209734  |            0.0005 |       0.0005 |         nan |              0.0005 |         0.0005 |                -0.770524  |                  4.99189   |           0.130956   |             0.209894  |
| x_market | D2      | M_all  |             37.5266  |                 15.487   |                   5.87147 |       0.265347  |                   0.786184 |                31.4353  |                    10.9688  |                      8.24065 |         0.0364756  |                           nan |         6.09137   |    0.228872  |            0.0005 |       0.0005 |         nan |              0.0005 |         0.0005 |                -0.288437  |                  7.26523   |           0.140598   |             0.228878  |

## Corrected spectrum resolution

| corpus   | view         | status                                      |   gamma |   positive_threshold |   negative_threshold |   positive_rank |   negative_rank | positive_stable   | negative_stable   |   natural_condition_a |   natural_condition_b |   positive_affinity |   positive_affinity_threshold |   negative_affinity |   negative_affinity_threshold |   positive_held_ab |   positive_held_ba |   negative_held_ab |   negative_held_ba |   positive_mass |   negative_mass |    trace |   frobenius |
|:---------|:-------------|:--------------------------------------------|--------:|---------------------:|---------------------:|----------------:|----------------:|:------------------|:------------------|----------------------:|----------------------:|--------------------:|------------------------------:|--------------------:|------------------------------:|-------------------:|-------------------:|-------------------:|-------------------:|----------------:|----------------:|---------:|------------:|
| pandora  | M_all        | POSITIVE_CONCORDANCE_SUBSPACE_UNDERRESOLVED |    0.1  |             0.697874 |             0.698854 |               0 |               0 | False             | False             |               37.4105 |               39.2964 |           0         |                   nan         |                   0 |                           nan |        nan         |         nan        |                nan |                nan |        0        |              -0 | 2.16177  |     4.70877 |
| pandora  | strict_shape | POSITIVE_CONCORDANCE_SUBSPACE_UNDERRESOLVED |    0.01 |             0.587249 |             0.586584 |               0 |               0 | False             | False             |               35.0064 |               48.6571 |           0         |                   nan         |                   0 |                           nan |        nan         |         nan        |                nan |                nan |        0        |              -0 | 0.6671   |     2.76484 |
| essays   | M_all        | POSITIVE_CONCORDANCE_SUBSPACE_UNDERRESOLVED |    0.1  |             0.675331 |             0.666951 |               2 |               0 | False             | False             |               37.7505 |               41.679  |           0.0246137 |                     0.0362897 |                   0 |                           nan |          0.0986161 |           0.109595 |                nan |                nan |        1.41849  |              -0 | 6.43593  |     4.52628 |
| essays   | strict_shape | POSITIVE_CONCORDANCE_SUBSPACE_UNDERRESOLVED |    0.01 |             0.562862 |             0.559294 |               0 |               0 | False             | False             |               46.5066 |               44.6968 |           0         |                   nan         |                   0 |                           nan |        nan         |         nan        |                nan |                nan |        0        |              -0 | 0.380869 |     2.54328 |
| x_market | M_all        | POSITIVE_CONCORDANCE_SUBSPACE_RESOLVED      |    0.3  |             0.919802 |             0.919663 |               3 |               0 | True              | False             |               44.3401 |               71.363  |           0.0877998 |                     0.0394726 |                   0 |                           nan |          0.605829  |           0.34247  |                nan |                nan |        2.80712  |              -0 | 5.61285  |     7.22111 |
| x_market | strict_shape | POSITIVE_CONCORDANCE_SUBSPACE_RESOLVED      |    0.3  |             0.855663 |             0.856757 |               1 |               0 | True              | False             |               34.1653 |               53.7724 |           0.592257  |                     0.0401446 |                   0 |                           nan |          0.805323  |           0.713824 |                nan |                nan |        0.930236 |              -0 | 2.28032  |     4.7074  |

## Corrected frozen spectrum cells

| corpus   | split   | view         |   observed |   pseudo_mean |    delta |   raw_p |   bootstrap_mean |   bootstrap_lcb |   max_t_p |
|:---------|:--------|:-------------|-----------:|--------------:|---------:|--------:|-----------------:|----------------:|----------:|
| x_market | D1      | M_all        |   0.587359 |  -0.0116926   | 0.599052 |  0.0005 |         0.580532 |        0.244953 |    0.0005 |
| x_market | D2      | M_all        |   0.517934 |   0.0542321   | 0.463702 |  0.0005 |         0.444471 |        0.171744 |    0.0005 |
| x_market | D1      | strict_shape |   0.770315 |   0.0056597   | 0.764655 |  0.0005 |         0.755978 |        0.371644 |  nan      |
| x_market | D2      | strict_shape |   0.629171 |  -0.000104776 | 0.629276 |  0.0005 |         0.593653 |        0.115903 |  nan      |

## Claim boundary

Opened-panel exchangeability correction. It compares the historical no-self cyclic knockout with a uniform within-block permutation distribution whose support includes fixed points and the natural identity assignment. It can correct the technical null interpretation but cannot confirm a personality, emotion, cognition, causal, cross-corpus, diagnostic, or clinical claim.
