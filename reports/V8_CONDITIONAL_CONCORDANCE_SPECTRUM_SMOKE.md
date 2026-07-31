# V8 Conditional Concordance Spectrum

Status: `ONE_CORPUS_LOCAL_POSITIVE_SPECTRUM_REPLICATED`

This opened-panel follow-up asks whether the signed M concordance found by the background quotient is low-dimensionally compressible. Positive and negative generalized spectra are retained separately; no positive-part operator is used.

## D0 spectrum resolution

| corpus   | view         | status                                      |   gamma |   positive_threshold |   negative_threshold |   positive_rank |   negative_rank | positive_stable   | negative_stable   |   natural_condition_a |   natural_condition_b |   positive_affinity |   positive_affinity_threshold |   negative_affinity |   negative_affinity_threshold |   positive_held_ab |   positive_held_ba |   negative_held_ab |   negative_held_ba |   positive_mass |   negative_mass |     trace |   frobenius |
|:---------|:-------------|:--------------------------------------------|--------:|---------------------:|---------------------:|----------------:|----------------:|:------------------|:------------------|----------------------:|----------------------:|--------------------:|------------------------------:|--------------------:|------------------------------:|-------------------:|-------------------:|-------------------:|-------------------:|----------------:|----------------:|----------:|------------:|
| pandora  | M_all        | POSITIVE_CONCORDANCE_SUBSPACE_UNDERRESOLVED |     0.1 |             0.957769 |             0.957164 |               0 |               0 | False             | False             |               75.6327 |               61.0378 |           0         |                   nan         |                   0 |                           nan |        nan         |        nan         |                nan |                nan |        0        |              -0 |  0.249237 |     8.91357 |
| pandora  | strict_shape | POSITIVE_CONCORDANCE_SUBSPACE_UNDERRESOLVED |     0.1 |             0.906875 |             0.906124 |               0 |               0 | False             | False             |               43.3897 |               35.0136 |           0         |                   nan         |                   0 |                           nan |        nan         |        nan         |                nan |                nan |        0        |              -0 | -0.598928 |     5.24946 |
| essays   | M_all        | POSITIVE_CONCORDANCE_SUBSPACE_RESOLVED      |     0.1 |             0.966732 |             0.966555 |               1 |               0 | True              | False             |               92.8503 |               73.876  |           0.0222676 |                     0.0181504 |                   0 |                           nan |          0.0519027 |          0.0986518 |                nan |                nan |        0.967271 |              -0 |  0.824063 |     8.95224 |
| essays   | strict_shape | POSITIVE_CONCORDANCE_SUBSPACE_UNDERRESOLVED |     0.1 |             0.931153 |             0.932069 |               0 |               0 | False             | False             |               53.1956 |               41.2856 |           0         |                   nan         |                   0 |                           nan |        nan         |        nan         |                nan |                nan |        0        |              -0 | -0.886928 |     5.6965  |
| x_market | M_all        | POSITIVE_CONCORDANCE_SUBSPACE_RESOLVED      |     0.3 |             0.920042 |             0.917748 |               3 |               0 | True              | False             |               66.9759 |               41.099  |           0.117376  |                     0.0394826 |                   0 |                           nan |          0.56225   |          0.684979  |                nan |                nan |        2.80777  |              -0 |  5.61746  |     7.21996 |
| x_market | strict_shape | POSITIVE_CONCORDANCE_SUBSPACE_RESOLVED      |     0.3 |             0.856943 |             0.860015 |               1 |               0 | True              | False             |               57.1408 |               29.9335 |           0.638201  |                     0.0480357 |                   0 |                           nan |          0.726132  |          0.828372  |                nan |                nan |        0.928776 |              -0 |  2.27024  |     4.70798 |

## Frozen D1/D2 projections

| corpus   | split   | view         |   observed |   pseudo_mean |    delta |   raw_p |   bootstrap_mean |   bootstrap_lcb |   max_t_p |
|:---------|:--------|:-------------|-----------:|--------------:|---------:|--------:|-----------------:|----------------:|----------:|
| essays   | D1      | M_all        |  0.0838344 |   -0.0451082  | 0.128943 |    0.2  |         0.167555 |       -0.370613 |      0.51 |
| essays   | D2      | M_all        |  0.227566  |    0.0309676  | 0.196598 |    0.07 |         0.215889 |       -0.219581 |      0.22 |
| x_market | D1      | M_all        |  0.571272  |   -0.00413662 | 0.575409 |    0.01 |         0.58384  |        0.237405 |      0.01 |
| x_market | D2      | M_all        |  0.507759  |    0.0797534  | 0.428005 |    0.01 |         0.396641 |        0.133903 |      0.01 |
| x_market | D1      | strict_shape |  0.781823  |    0.00712081 | 0.774702 |    0.01 |         0.771153 |        0.38113  |    nan    |
| x_market | D2      | strict_shape |  0.628277  |    0.025598   | 0.602679 |    0.01 |         0.517823 |        0.148017 |    nan    |

## Block attribution

| corpus   | view         |   axis |   block |   attribution |
|:---------|:-------------|-------:|--------:|--------------:|
| essays   | M_all        |      0 |       0 |     0.513539  |
| essays   | M_all        |      0 |       1 |     0.235564  |
| essays   | M_all        |      0 |       2 |     0.0673031 |
| essays   | M_all        |      0 |       3 |     0.183594  |
| x_market | M_all        |      0 |       0 |     0.201134  |
| x_market | M_all        |      0 |       1 |     0.684877  |
| x_market | M_all        |      0 |       2 |     0.0375369 |
| x_market | M_all        |      0 |       3 |     0.0764529 |
| x_market | M_all        |      1 |       0 |     0.604831  |
| x_market | M_all        |      1 |       1 |     0.142196  |
| x_market | M_all        |      1 |       2 |     0.0200595 |
| x_market | M_all        |      1 |       3 |     0.232914  |
| x_market | M_all        |      2 |       0 |     0.636652  |
| x_market | M_all        |      2 |       1 |     0.100054  |
| x_market | M_all        |      2 |       2 |     0.0142853 |
| x_market | M_all        |      2 |       3 |     0.249008  |
| x_market | strict_shape |      0 |       0 |     0.957232  |
| x_market | strict_shape |      0 |       1 |     0.0427679 |

## Claim boundary

Exploratory opened-panel compression audit following the marginal-background quotient result. It asks whether corpus-local signed concordance is carried by a D0-resolved low-dimensional positive or negative generalized spectrum and whether the frozen positive spectrum repeats in D1/D2. It cannot confirm PANDORA after the prior knife-edge result, cannot align spectra across corpora, and cannot name personality, emotion, cognition, diagnosis, causality, or clinical validity. Formal confirmation requires a fresh author panel.
