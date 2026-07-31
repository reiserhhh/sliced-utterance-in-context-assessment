# V8 Conditional Concordance Spectrum

Status: `MULTI_CORPUS_LOCAL_POSITIVE_SPECTRA_REPLICATED`

This opened-panel follow-up asks whether the signed M concordance found by the background quotient is low-dimensionally compressible. Positive and negative generalized spectra are retained separately; no positive-part operator is used.

## D0 spectrum resolution

| corpus   | view         | status                                      |   gamma |   positive_threshold |   negative_threshold |   positive_rank |   negative_rank | positive_stable   | negative_stable   |   natural_condition_a |   natural_condition_b |   positive_affinity |   positive_affinity_threshold |   negative_affinity |   negative_affinity_threshold |   positive_held_ab |   positive_held_ba |   negative_held_ab |   negative_held_ba |   positive_mass |   negative_mass |    trace |   frobenius |
|:---------|:-------------|:--------------------------------------------|--------:|---------------------:|---------------------:|----------------:|----------------:|:------------------|:------------------|----------------------:|----------------------:|--------------------:|------------------------------:|--------------------:|------------------------------:|-------------------:|-------------------:|-------------------:|-------------------:|----------------:|----------------:|---------:|------------:|
| pandora  | M_all        | POSITIVE_CONCORDANCE_SUBSPACE_UNDERRESOLVED |    0.1  |             0.699475 |             0.697556 |               0 |               0 | False             | False             |               38.2571 |               36.4493 |           0         |                   nan         |                   0 |                           nan |         nan        |         nan        |                nan |                nan |        0        |              -0 | 2.16187  |     4.70871 |
| pandora  | strict_shape | POSITIVE_CONCORDANCE_SUBSPACE_UNDERRESOLVED |    0.01 |             0.590926 |             0.587818 |               0 |               0 | False             | False             |               37.8838 |               39.0107 |           0         |                   nan         |                   0 |                           nan |         nan        |         nan        |                nan |                nan |        0        |              -0 | 0.668392 |     2.76479 |
| essays   | M_all        | POSITIVE_CONCORDANCE_SUBSPACE_RESOLVED      |    0.1  |             0.672131 |             0.667857 |               3 |               0 | True              | False             |               39.7478 |               38.0797 |           0.0659305 |                     0.0378216 |                   0 |                           nan |           0.156742 |           0.123697 |                nan |                nan |        2.09223  |              -0 | 6.43464  |     4.52656 |
| essays   | strict_shape | POSITIVE_CONCORDANCE_SUBSPACE_UNDERRESOLVED |    0.01 |             0.562818 |             0.560824 |               0 |               0 | False             | False             |               47.7035 |               50.6789 |           0         |                   nan         |                   0 |                           nan |         nan        |         nan        |                nan |                nan |        0        |              -0 | 0.380944 |     2.54333 |
| x_market | M_all        | POSITIVE_CONCORDANCE_SUBSPACE_RESOLVED      |    0.3  |             0.919839 |             0.919066 |               3 |               0 | True              | False             |               67.6305 |               41.3189 |           0.126581  |                     0.0388131 |                   0 |                           nan |           0.564865 |           0.696503 |                nan |                nan |        2.80672  |              -0 | 5.60458  |     7.22445 |
| x_market | strict_shape | POSITIVE_CONCORDANCE_SUBSPACE_RESOLVED      |    0.3  |             0.857685 |             0.857155 |               1 |               0 | True              | False             |               57.5995 |               30.235  |           0.629247  |                     0.0378934 |                   0 |                           nan |           0.727221 |           0.825072 |                nan |                nan |        0.929501 |              -0 | 2.27901  |     4.71082 |

## Frozen D1/D2 projections

| corpus   | split   | view         |   observed |   pseudo_mean |    delta |   raw_p |   bootstrap_mean |   bootstrap_lcb |   max_t_p |
|:---------|:--------|:-------------|-----------:|--------------:|---------:|--------:|-----------------:|----------------:|----------:|
| essays   | D1      | M_all        |   0.216731 |    0.018758   | 0.197973 |  0.0005 |         0.205562 |       0.109573  |    0.0005 |
| essays   | D2      | M_all        |   0.196505 |    0.00541062 | 0.191095 |  0.0005 |         0.194687 |       0.0878992 |    0.0005 |
| x_market | D1      | M_all        |   0.586082 |   -0.00351877 | 0.589601 |  0.0005 |         0.567283 |       0.219009  |    0.0005 |
| x_market | D2      | M_all        |   0.51622  |    0.0602909  | 0.455929 |  0.0005 |         0.430723 |       0.15208   |    0.0005 |
| x_market | D1      | strict_shape |   0.775509 |    0.00545218 | 0.770057 |  0.0005 |         0.778512 |       0.335998  |  nan      |
| x_market | D2      | strict_shape |   0.62553  |   -0.00251479 | 0.628045 |  0.0005 |         0.580341 |       0.154147  |  nan      |

## Block attribution

| corpus   | view         |   axis |   block |   attribution |
|:---------|:-------------|-------:|--------:|--------------:|
| essays   | M_all        |      0 |       0 |     0.688349  |
| essays   | M_all        |      0 |       1 |     0.228486  |
| essays   | M_all        |      0 |       2 |     0.0130835 |
| essays   | M_all        |      0 |       3 |     0.0700808 |
| essays   | M_all        |      1 |       0 |     0.621898  |
| essays   | M_all        |      1 |       1 |     0.220593  |
| essays   | M_all        |      1 |       2 |     0.0331319 |
| essays   | M_all        |      1 |       3 |     0.124378  |
| essays   | M_all        |      2 |       0 |     0.533141  |
| essays   | M_all        |      2 |       1 |     0.290939  |
| essays   | M_all        |      2 |       2 |     0.0663437 |
| essays   | M_all        |      2 |       3 |     0.109576  |
| x_market | M_all        |      0 |       0 |     0.197987  |
| x_market | M_all        |      0 |       1 |     0.687466  |
| x_market | M_all        |      0 |       2 |     0.0384254 |
| x_market | M_all        |      0 |       3 |     0.0761216 |
| x_market | M_all        |      1 |       0 |     0.61434   |
| x_market | M_all        |      1 |       1 |     0.122538  |
| x_market | M_all        |      1 |       2 |     0.0214662 |
| x_market | M_all        |      1 |       3 |     0.241656  |
| x_market | M_all        |      2 |       0 |     0.625706  |
| x_market | M_all        |      2 |       1 |     0.107597  |
| x_market | M_all        |      2 |       2 |     0.011653  |
| x_market | M_all        |      2 |       3 |     0.255044  |
| x_market | strict_shape |      0 |       0 |     0.955005  |
| x_market | strict_shape |      0 |       1 |     0.044995  |

## Claim boundary

Exploratory opened-panel compression audit following the marginal-background quotient result. It asks whether corpus-local signed concordance is carried by a D0-resolved low-dimensional positive or negative generalized spectrum and whether the frozen positive spectrum repeats in D1/D2. It cannot confirm PANDORA after the prior knife-edge result, cannot align spectra across corpora, and cannot name personality, emotion, cognition, diagnosis, causality, or clinical validity. Formal confirmation requires a fresh author panel.
