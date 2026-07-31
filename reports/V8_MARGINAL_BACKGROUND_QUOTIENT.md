# V8 Marginal-Background Quotient

Status: `MULTI_CORPUS_SIGNED_CONCORDANCE_DETECTED`

Natural four-event author sets are compared with conditional pseudo-author orbits that preserve corpus, D-split, context, event slot, local length rank, and every 64-dimensional event vector. D0 pseudo worlds freeze blockwise centers and covariance whitening; D1/D2 are untouched audit panels. The signed replicated operator is never projected to a positive part.

## Omnibus M result

| corpus   | split   | view   |   observed_frobenius |   observed_operator_norm |   observed_effective_rank |   observed_link |   observed_same_author_auc |   pseudo_mean_frobenius |   pseudo_mean_operator_norm |   pseudo_mean_effective_rank |   pseudo_mean_link |   pseudo_mean_same_author_auc |   frobenius_delta |   link_delta |   frobenius_raw_p |   link_raw_p |   auc_raw_p |   frobenius_max_t_p |   link_max_t_p |   frobenius_bootstrap_lcb |   frobenius_bootstrap_mean |   link_bootstrap_lcb |   link_bootstrap_mean |
|:---------|:--------|:-------|---------------------:|-------------------------:|--------------------------:|----------------:|---------------------------:|------------------------:|----------------------------:|-----------------------------:|-------------------:|------------------------------:|------------------:|-------------:|------------------:|-------------:|------------:|--------------------:|---------------:|--------------------------:|---------------------------:|---------------------:|----------------------:|
| pandora  | D1      | M_all  |              9.23179 |                  2.13507 |                  18.696   |       0.020599  |                   0.560977 |                 9.12117 |                     1.93419 |                     22.3072  |         0.00384208 |                           nan |         0.110618  |    0.0167569 |            0.044  |       0.001  |         nan |              0.244  |         0.005  |                -0.268389  |                  0.0991287 |          0.000280433 |             0.0166065 |
| pandora  | D2      | M_all  |              9.61108 |                  2.1329  |                  20.3051  |       0.020128  |                   0.559485 |                 9.54213 |                     2.05985 |                     21.5373  |         0.00466583 |                           nan |         0.0689481 |    0.0154622 |            0.1605 |       0.001  |         nan |              0.6375 |         0.011  |                -0.313005  |                  0.06155   |         -6.7435e-05  |             0.0160967 |
| essays   | D1      | M_all  |              8.19809 |                  1.8452  |                  19.7397  |       0.0684262 |                   0.690495 |                 7.97337 |                     1.61485 |                     24.4265  |         0.00580309 |                           nan |         0.224728  |    0.0626232 |            0.0005 |       0.0005 |         nan |              0.001  |         0.0005 |                -0.0658577 |                  0.228791  |          0.0497117   |             0.061803  |
| essays   | D2      | M_all  |              8.5433  |                  2.11078 |                  16.3819  |       0.0772778 |                   0.709708 |                 8.02471 |                     1.62124 |                     24.549   |         0.00493636 |                           nan |         0.518597  |    0.0723414 |            0.0005 |       0.0005 |         nan |              0.0005 |         0.0005 |                 0.182228  |                  0.496626  |          0.0577501   |             0.0721924 |
| x_market | D1      | M_all  |             31.6293  |                 12.2629  |                   6.65264 |       0.244117  |                   0.787167 |                27.9119  |                     9.43939 |                      8.77538 |         0.0361398  |                           nan |         3.71741   |    0.207977  |            0.0005 |       0.0005 |         nan |              0.0005 |         0.0005 |                -1.04199   |                  4.48168   |          0.131359    |             0.204642  |
| x_market | D2      | M_all  |             37.3946  |                 15.3068  |                   5.96829 |       0.263855  |                   0.783654 |                31.3972  |                    10.9441  |                      8.25925 |         0.0396299  |                           nan |         5.99735   |    0.224225  |            0.0005 |       0.0005 |         nan |              0.0005 |         0.0005 |                -0.503456  |                  7.24148   |          0.128326    |             0.22537   |

## Location/shape diagnostics

| corpus   | split   | view                |   frobenius_delta |   frobenius_raw_p |   observed_link |   link_raw_p |   observed_same_author_auc |   auc_raw_p |
|:---------|:--------|:--------------------|------------------:|------------------:|----------------:|-------------:|---------------------------:|------------:|
| pandora  | D1      | M_all               |        0.110618   |            0.044  |      0.020599   |       0.001  |                   0.560977 |         nan |
| pandora  | D1      | location_mean       |        0.160924   |            0.005  |      0.0290105  |       0.01   |                   0.570398 |         nan |
| pandora  | D1      | strict_shape        |       -0.058952   |            0.89   |      0.00886214 |       0.165  |                   0.519907 |         nan |
| pandora  | D1      | dispersion_variance |       -0.0724019  |            0.94   |      0.0112626  |       0.11   |                   0.522055 |         nan |
| pandora  | D1      | higher_shape        |       -0.0211529  |            0.67   |     -0.00644512 |       0.675  |                   0.494356 |         nan |
| pandora  | D2      | M_all               |        0.0689481  |            0.1605 |      0.020128   |       0.001  |                   0.559485 |         nan |
| pandora  | D2      | location_mean       |        0.184781   |            0.005  |      0.0341418  |       0.005  |                   0.573093 |         nan |
| pandora  | D2      | strict_shape        |       -0.00424159 |            0.525  |      0.0055887  |       0.46   |                   0.509765 |         nan |
| pandora  | D2      | dispersion_variance |       -0.00180667 |            0.515  |      0.0061796  |       0.475  |                   0.504085 |         nan |
| pandora  | D2      | higher_shape        |       -0.0381657  |            0.765  |      0.00158283 |       0.515  |                   0.495597 |         nan |
| essays   | D1      | M_all               |        0.224728   |            0.0005 |      0.0684262  |       0.0005 |                   0.690495 |         nan |
| essays   | D1      | location_mean       |        0.506697   |            0.005  |      0.121708   |       0.005  |                   0.730796 |         nan |
| essays   | D1      | strict_shape        |       -0.17027    |            1      |      0.0143407  |       0.01   |                   0.535425 |         nan |
| essays   | D1      | dispersion_variance |       -0.136956   |            1      |      0.015577   |       0.01   |                   0.529296 |         nan |
| essays   | D1      | higher_shape        |       -0.0399265  |            0.835  |      0.00534465 |       0.44   |                   0.507613 |         nan |
| essays   | D2      | M_all               |        0.518597   |            0.0005 |      0.0772778  |       0.0005 |                   0.709708 |         nan |
| essays   | D2      | location_mean       |        0.667087   |            0.005  |      0.133061   |       0.005  |                   0.754935 |         nan |
| essays   | D2      | strict_shape        |       -0.0981957  |            0.975  |      0.0196609  |       0.005  |                   0.534418 |         nan |
| essays   | D2      | dispersion_variance |       -0.0707688  |            0.925  |      0.0218863  |       0.005  |                   0.535055 |         nan |
| essays   | D2      | higher_shape        |       -0.0483593  |            0.905  |      0.00375793 |       0.545  |                   0.496834 |         nan |
| x_market | D1      | M_all               |        3.71741    |            0.0005 |      0.244117   |       0.0005 |                   0.787167 |         nan |
| x_market | D1      | location_mean       |        3.86668    |            0.005  |      0.337263   |       0.005  |                   0.812151 |         nan |
| x_market | D1      | strict_shape        |        1.05574    |            0.01   |      0.127832   |       0.005  |                   0.617013 |         nan |
| x_market | D1      | dispersion_variance |        1.12587    |            0.005  |      0.138809   |       0.005  |                   0.628061 |         nan |
| x_market | D1      | higher_shape        |       -0.0112415  |            0.495  |      0.0517592  |       0.44   |                   0.518378 |         nan |
| x_market | D2      | M_all               |        5.99735    |            0.0005 |      0.263855   |       0.0005 |                   0.783654 |         nan |
| x_market | D2      | location_mean       |        5.53956    |            0.005  |      0.362616   |       0.005  |                   0.793955 |         nan |
| x_market | D2      | strict_shape        |        1.99678    |            0.01   |      0.135633   |       0.005  |                   0.661357 |         nan |
| x_market | D2      | dispersion_variance |        2.20658    |            0.01   |      0.142577   |       0.005  |                   0.646535 |         nan |
| x_market | D2      | higher_shape        |        0.040334   |            0.385  |      0.0669866  |       0.155  |                   0.562815 |         nan |

The `strict_shape` view excludes raw quantiles because those quantiles retain location information; it contains variance and centered RFF blocks only. Diagnostic views do not promote a claim when the omnibus M gate fails.

## Background diagnostics

| corpus   | block     |   dimension |   condition_number |   coverage |
|:---------|:----------|------------:|-------------------:|-----------:|
| pandora  | mean      |          64 |            4.23841 |          1 |
| pandora  | variance  |          64 |            5.89088 |          1 |
| pandora  | rff       |          16 |           21.1644  |          1 |
| pandora  | quantiles |          24 |           30.8343  |          1 |
| essays   | mean      |          64 |            3.91218 |          1 |
| essays   | variance  |          64 |            5.38883 |          1 |
| essays   | rff       |          16 |           21.7955  |          1 |
| essays   | quantiles |          24 |           32.6569  |          1 |
| x_market | mean      |          64 |            6.89839 |          1 |
| x_market | variance  |          64 |            8.93011 |          1 |
| x_market | rff       |          16 |           24.1097  |          1 |
| x_market | quantiles |          24 |           32.5777  |          1 |

## Claim boundary

Prospective label-free measurement-background audit on opened real-text authors. A pass licenses only a corpus-local, source-disjoint natural grouping residual beyond corpus/context/slot/local-length-matched event marginals. It does not license cross-corpus coordinate transport, personality, emotion, cognition, diagnosis, language invariance, causal interpretation, or clinical validity. A failure rejects this M operator and design, not the existence of all author information.
