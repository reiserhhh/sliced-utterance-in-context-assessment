# V8 Exchangeable Background Audit

Status: `EXCHANGEABLE_NULL_AUDIT_COMPLETED`

The historical no-self cyclic knockout is rerun with uniform within-block permutations. Fixed points and the natural identity assignment belong to the corrected null support.

## Decision

```json
{
  "status": "EXCHANGEABLE_NULL_AUDIT_COMPLETED",
  "marginal_status": "MULTI_CORPUS_SIGNED_CONCORDANCE_DETECTED",
  "marginal_corpus_status": {
    "pandora": "GROUPING_RESIDUAL_NOT_DETECTED",
    "essays": "SIGNED_CONCORDANCE_RESIDUAL_DETECTED",
    "x_market": "SIGNED_CONCORDANCE_RESIDUAL_DETECTED"
  },
  "spectrum_status": "SIGNED_CONCORDANCE_NOT_LOW_DIMENSIONALLY_RESOLVED",
  "spectrum_corpus_status": {
    "pandora": "POSITIVE_SPECTRUM_UNDERRESOLVED",
    "essays": "POSITIVE_SPECTRUM_UNDERRESOLVED",
    "x_market": "POSITIVE_SPECTRUM_UNDERRESOLVED"
  },
  "mean_fixed_point_fraction": 0.0644331022833178,
  "identity_blocks_observed": 0,
  "version": "v8-exchangeable-background-audit-1",
  "timestamp_utc": "2026-07-29T18:06:24.796592+00:00",
  "claim_boundary": "Opened-panel exchangeability correction. It compares the historical no-self cyclic knockout with a uniform within-block permutation distribution whose support includes fixed points and the natural identity assignment. It can correct the technical null interpretation but cannot confirm a personality, emotion, cognition, causal, cross-corpus, diagnostic, or clinical claim."
}
```

## Historical comparison

| corpus   | split   |   link_delta_cyclic |   link_max_t_p_cyclic |   link_bootstrap_lcb_cyclic |   link_delta_exchangeable |   link_max_t_p_exchangeable |   link_bootstrap_lcb_exchangeable | family      |
|:---------|:--------|--------------------:|----------------------:|----------------------------:|--------------------------:|----------------------------:|----------------------------------:|:------------|
| pandora  | D1      |           0.0167569 |                0.005  |                 0.000280433 |                0.0182814  |                        0.23 |                       -0.0116257  | signed_link |
| pandora  | D2      |           0.0154622 |                0.011  |                -6.7435e-05  |                0.00813281 |                        0.9  |                       -0.0269779  | signed_link |
| essays   | D1      |           0.0626232 |                0.0005 |                 0.0497117   |                0.0444452  |                        0.02 |                        0.00683002 | signed_link |
| essays   | D2      |           0.0723414 |                0.0005 |                 0.0577501   |                0.109715   |                        0.01 |                        0.0738885  | signed_link |
| x_market | D1      |           0.207977  |                0.0005 |                 0.131359    |                0.2225     |                        0.01 |                        0.137195   | signed_link |
| x_market | D2      |           0.224225  |                0.0005 |                 0.128326    |                0.256747   |                        0.01 |                        0.167364   | signed_link |

## Corrected marginal cells

| corpus   | split   | view   |   observed_frobenius |   observed_operator_norm |   observed_effective_rank |   observed_link |   observed_same_author_auc |   pseudo_mean_frobenius |   pseudo_mean_operator_norm |   pseudo_mean_effective_rank |   pseudo_mean_link |   pseudo_mean_same_author_auc |   frobenius_delta |   link_delta |   frobenius_raw_p |   link_raw_p |   auc_raw_p |   frobenius_max_t_p |   link_max_t_p |   frobenius_bootstrap_lcb |   frobenius_bootstrap_mean |   link_bootstrap_lcb |   link_bootstrap_mean |
|:---------|:--------|:-------|---------------------:|-------------------------:|--------------------------:|----------------:|---------------------------:|------------------------:|----------------------------:|-----------------------------:|-------------------:|------------------------------:|------------------:|-------------:|------------------:|-------------:|------------:|--------------------:|---------------:|--------------------------:|---------------------------:|---------------------:|----------------------:|
| pandora  | D1      | M_all  |              22.1897 |                  6.4285  |                  11.9147  |       0.0189363 |                   0.556908 |                 22.1396 |                     6.29501 |                     12.4071  |        0.000654908 |                           nan |         0.0500613 |   0.0182814  |              0.44 |         0.04 |         nan |                0.94 |           0.23 |                 -1.64643  |                   0.05948  |          -0.0116257  |             0.0149039 |
| pandora  | D2      | M_all  |              26.5271 |                  8.11924 |                  10.6745  |       0.0104817 |                   0.520763 |                 26.0995 |                     7.62986 |                     11.7424  |        0.0023489   |                           nan |         0.427531  |   0.00813281 |              0.09 |         0.33 |         nan |                0.38 |           0.9  |                 -2.31932  |                   0.252613 |          -0.0269779  |             0.0167655 |
| essays   | D1      | M_all  |              23.9819 |                  6.87315 |                  12.1747  |       0.0499326 |                   0.638979 |                 23.3302 |                     6.55288 |                     12.7274  |        0.00548747  |                           nan |         0.651751  |   0.0444452  |              0.02 |         0.01 |         nan |                0.06 |           0.02 |                 -0.960659 |                   0.897209 |           0.00683002 |             0.0459419 |
| essays   | D2      | M_all  |              24.7805 |                  7.2778  |                  11.5936  |       0.109726  |                   0.788441 |                 24.3305 |                     6.74675 |                     13.049   |        1.10997e-05 |                           nan |         0.449922  |   0.109715   |              0.06 |         0.01 |         nan |                0.27 |           0.01 |                 -1.90987  |                   0.414893 |           0.0738885  |             0.11084   |
| x_market | D1      | M_all  |              37.7557 |                 14.8383  |                   6.47437 |       0.266585  |                   0.822226 |                 33.6421 |                    12.4917  |                      7.27509 |        0.0440851   |                           nan |         4.11359   |   0.2225     |              0.01 |         0.01 |         nan |                0.01 |           0.01 |                 -2.12761  |                   5.00713  |           0.137195   |             0.220044  |
| x_market | D2      | M_all  |              46.3105 |                 17.9308  |                   6.67054 |       0.295692  |                   0.827194 |                 39.6024 |                    15.0512  |                      6.94005 |        0.0389456   |                           nan |         6.70809   |   0.256747   |              0.01 |         0.01 |         nan |                0.01 |           0.01 |                 -1.23097  |                   8.13515  |           0.167364   |             0.259552  |

## Corrected spectrum resolution

| corpus   | view         | status                                      |   gamma |   positive_threshold |   negative_threshold |   positive_rank |   negative_rank | positive_stable   | negative_stable   |   natural_condition_a |   natural_condition_b |   positive_affinity |   positive_affinity_threshold |   negative_affinity |   negative_affinity_threshold |   positive_held_ab |   positive_held_ba |   negative_held_ab |   negative_held_ba |   positive_mass |   negative_mass |     trace |   frobenius |
|:---------|:-------------|:--------------------------------------------|--------:|---------------------:|---------------------:|----------------:|----------------:|:------------------|:------------------|----------------------:|----------------------:|--------------------:|------------------------------:|--------------------:|------------------------------:|-------------------:|-------------------:|-------------------:|-------------------:|----------------:|----------------:|----------:|------------:|
| pandora  | M_all        | POSITIVE_CONCORDANCE_SUBSPACE_UNDERRESOLVED |     0.1 |             0.957647 |             0.957322 |               0 |               0 | False             | False             |               64.6751 |               67.9857 |           0         |                   nan         |                   0 |                           nan |         nan        |        nan         |                nan |                nan |        0        |              -0 |  0.27035  |     8.91156 |
| pandora  | strict_shape | POSITIVE_CONCORDANCE_SUBSPACE_UNDERRESOLVED |     0.1 |             0.906318 |             0.904526 |               0 |               0 | False             | False             |               40.7856 |               44.4136 |           0         |                   nan         |                   0 |                           nan |         nan        |        nan         |                nan |                nan |        0        |              -0 | -0.590202 |     5.24814 |
| essays   | M_all        | POSITIVE_CONCORDANCE_SUBSPACE_UNDERRESOLVED |     0.1 |             0.966664 |             0.966743 |               1 |               0 | False             | False             |               79.9933 |               81.8084 |           0.0106187 |                     0.0325691 |                   0 |                           nan |           0.202355 |         -0.0458546 |                nan |                nan |        0.967171 |              -0 |  0.823266 |     8.94982 |
| essays   | strict_shape | POSITIVE_CONCORDANCE_SUBSPACE_UNDERRESOLVED |     0.1 |             0.932942 |             0.934886 |               0 |               0 | False             | False             |               42.8513 |               49.1426 |           0         |                   nan         |                   0 |                           nan |         nan        |        nan         |                nan |                nan |        0        |              -0 | -0.895815 |     5.69296 |

## Corrected frozen spectrum cells

_No resolved spectrum cells._

## Claim boundary

Opened-panel exchangeability correction. It compares the historical no-self cyclic knockout with a uniform within-block permutation distribution whose support includes fixed points and the natural identity assignment. It can correct the technical null interpretation but cannot confirm a personality, emotion, cognition, causal, cross-corpus, diagnostic, or clinical claim.
