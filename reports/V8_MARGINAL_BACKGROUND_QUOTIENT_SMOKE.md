# V8 Marginal-Background Quotient

Status: `MULTI_CORPUS_SIGNED_CONCORDANCE_DETECTED`

Natural four-event author sets are compared with conditional pseudo-author orbits that preserve corpus, D-split, context, event slot, local length rank, and every 64-dimensional event vector. D0 pseudo worlds freeze blockwise centers and covariance whitening; D1/D2 are untouched audit panels. The signed replicated operator is never projected to a positive part.

## Omnibus M result

| corpus   | split   | view   |   observed_frobenius |   observed_operator_norm |   observed_effective_rank |   observed_link |   observed_same_author_auc |   pseudo_mean_frobenius |   pseudo_mean_operator_norm |   pseudo_mean_effective_rank |   pseudo_mean_link |   pseudo_mean_same_author_auc |   frobenius_delta |   link_delta |   frobenius_raw_p |   link_raw_p |   auc_raw_p |   frobenius_max_t_p |   link_max_t_p |   frobenius_bootstrap_lcb |   frobenius_bootstrap_mean |   link_bootstrap_lcb |   link_bootstrap_mean |
|:---------|:--------|:-------|---------------------:|-------------------------:|--------------------------:|----------------:|---------------------------:|------------------------:|----------------------------:|-----------------------------:|-------------------:|------------------------------:|------------------:|-------------:|------------------:|-------------:|------------:|--------------------:|---------------:|--------------------------:|---------------------------:|---------------------:|----------------------:|
| pandora  | D1      | M_all  |              22.126  |                  6.40451 |                  11.9353  |      0.0184975  |                   0.557332 |                 22.0542 |                     6.30562 |                     12.2793  |         0.00100199 |                           nan |         0.0717943 |    0.0174955 |              0.34 |         0.08 |         nan |                0.92 |           0.36 |                  -1.93276 |                   0.249936 |           -0.020059  |            0.0187553  |
| pandora  | D2      | M_all  |              26.4047 |                  8.0569  |                  10.7405  |      0.00888348 |                   0.514141 |                 26.1275 |                     7.53454 |                     12.0677  |         0.00354627 |                           nan |         0.277189  |    0.0053372 |              0.21 |         0.39 |         nan |                0.66 |           0.94 |                  -2.0354  |                   0.313976 |           -0.0312296 |            0.00597005 |
| essays   | D1      | M_all  |              24.0071 |                  6.87679 |                  12.1874  |      0.0496585  |                   0.6393   |                 23.411  |                     6.53356 |                     12.8993  |         0.00563693 |                           nan |         0.596158  |    0.0440215 |              0.02 |         0.01 |         nan |                0.09 |           0.01 |                  -1.58236 |                   0.758998 |            0.0097549 |            0.0423168  |
| essays   | D2      | M_all  |              24.7743 |                  7.24519 |                  11.6924  |      0.110218   |                   0.791894 |                 24.358  |                     6.80423 |                     12.8754  |        -0.0025917  |                           nan |         0.416382  |    0.11281   |              0.13 |         0.01 |         nan |                0.53 |           0.01 |                  -1.57909 |                   0.520665 |            0.0773635 |            0.112252   |
| x_market | D1      | M_all  |              37.9049 |                 15.0426  |                   6.34955 |      0.267549   |                   0.820305 |                 33.6848 |                    12.4367  |                      7.35874 |         0.0469681  |                           nan |         4.22011   |    0.220581  |              0.01 |         0.01 |         nan |                0.01 |           0.01 |                  -2.25693 |                   5.55967  |            0.137431  |            0.211514   |
| x_market | D2      | M_all  |              46.4092 |                 18.3631  |                   6.3873  |      0.294006   |                   0.822754 |                 39.5298 |                    15.0945  |                      6.88505 |         0.0378293  |                           nan |         6.87945   |    0.256176  |              0.01 |         0.01 |         nan |                0.01 |           0.01 |                  -1.72051 |                   9.20503  |            0.161989  |            0.253341   |

## Location/shape diagnostics

| corpus   | split   | view                |   frobenius_delta |   frobenius_raw_p |   observed_link |   link_raw_p |   observed_same_author_auc |   auc_raw_p |
|:---------|:--------|:--------------------|------------------:|------------------:|----------------:|-------------:|---------------------------:|------------:|
| pandora  | D1      | M_all               |        0.0717943  |              0.34 |     0.0184975   |         0.08 |                   0.557332 |         nan |
| pandora  | D1      | location_mean       |        0.118832   |              0.26 |     0.0119692   |         0.27 |                   0.530896 |         nan |
| pandora  | D1      | strict_shape        |        0.158616   |              0.24 |     0.0191595   |         0.13 |                   0.542315 |         nan |
| pandora  | D1      | dispersion_variance |        0.0645433  |              0.38 |     0.0340555   |         0.03 |                   0.575627 |         nan |
| pandora  | D1      | higher_shape        |        0.0697229  |              0.26 |    -0.0723646   |         0.99 |                   0.42936  |         nan |
| pandora  | D2      | M_all               |        0.277189   |              0.21 |     0.00888348  |         0.39 |                   0.514141 |         nan |
| pandora  | D2      | location_mean       |        0.45808    |              0.01 |     0.0234567   |         0.19 |                   0.512525 |         nan |
| pandora  | D2      | strict_shape        |        0.0992522  |              0.39 |    -0.000649199 |         0.58 |                   0.485836 |         nan |
| pandora  | D2      | dispersion_variance |       -0.0568643  |              0.58 |    -0.00908852  |         0.7  |                   0.470236 |         nan |
| pandora  | D2      | higher_shape        |        0.0857191  |              0.26 |     0.0545004   |         0.18 |                   0.551223 |         nan |
| essays   | D1      | M_all               |        0.596158   |              0.02 |     0.0496585   |         0.01 |                   0.6393   |         nan |
| essays   | D1      | location_mean       |        1.34415    |              0.01 |     0.114718    |         0.01 |                   0.722138 |         nan |
| essays   | D1      | strict_shape        |       -0.846193   |              1    |    -0.0249818   |         0.95 |                   0.434342 |         nan |
| essays   | D1      | dispersion_variance |       -0.586719   |              0.98 |    -0.0238376   |         0.96 |                   0.442758 |         nan |
| essays   | D1      | higher_shape        |       -0.119475   |              0.81 |    -0.0339012   |         0.79 |                   0.474854 |         nan |
| essays   | D2      | M_all               |        0.416382   |              0.13 |     0.110218    |         0.01 |                   0.791894 |         nan |
| essays   | D2      | location_mean       |        0.863181   |              0.01 |     0.16772     |         0.01 |                   0.784424 |         nan |
| essays   | D2      | strict_shape        |       -0.441787   |              0.97 |     0.0549555   |         0.01 |                   0.629722 |         nan |
| essays   | D2      | dispersion_variance |       -0.361161   |              0.93 |     0.0552915   |         0.01 |                   0.61262  |         nan |
| essays   | D2      | higher_shape        |       -0.00420659 |              0.46 |     0.0525198   |         0.2  |                   0.568751 |         nan |
| x_market | D1      | M_all               |        4.22011    |              0.01 |     0.267549    |         0.01 |                   0.820305 |         nan |
| x_market | D1      | location_mean       |        4.66401    |              0.01 |     0.353834    |         0.01 |                   0.833126 |         nan |
| x_market | D1      | strict_shape        |        0.985307   |              0.06 |     0.156818    |         0.01 |                   0.673691 |         nan |
| x_market | D1      | dispersion_variance |        0.958622   |              0.06 |     0.166439    |         0.01 |                   0.677497 |         nan |
| x_market | D1      | higher_shape        |        0.0981943  |              0.33 |     0.0900833   |         0.4  |                   0.546282 |         nan |
| x_market | D2      | M_all               |        6.87945    |              0.01 |     0.294006    |         0.01 |                   0.822754 |         nan |
| x_market | D2      | location_mean       |        6.99182    |              0.01 |     0.386859    |         0.01 |                   0.826431 |         nan |
| x_market | D2      | strict_shape        |        1.77765    |              0.03 |     0.160195    |         0.01 |                   0.678356 |         nan |
| x_market | D2      | dispersion_variance |        1.81277    |              0.03 |     0.164964    |         0.01 |                   0.659417 |         nan |
| x_market | D2      | higher_shape        |        0.270902   |              0.11 |     0.114151    |         0.04 |                   0.604162 |         nan |

The `strict_shape` view excludes raw quantiles because those quantiles retain location information; it contains variance and centered RFF blocks only. Diagnostic views do not promote a claim when the omnibus M gate fails.

## Background diagnostics

| corpus   | block     |   dimension |   condition_number |   coverage |
|:---------|:----------|------------:|-------------------:|-----------:|
| pandora  | mean      |          64 |            5.68429 |          1 |
| pandora  | variance  |          64 |            6.48841 |          1 |
| pandora  | rff       |          16 |           22.9542  |          1 |
| pandora  | quantiles |          24 |           31.0892  |          1 |
| essays   | mean      |          64 |            6.71484 |          1 |
| essays   | variance  |          64 |            5.78373 |          1 |
| essays   | rff       |          16 |           23.9818  |          1 |
| essays   | quantiles |          24 |           34.876   |          1 |
| x_market | mean      |          64 |            9.78028 |          1 |
| x_market | variance  |          64 |            9.92723 |          1 |
| x_market | rff       |          16 |           22.0444  |          1 |
| x_market | quantiles |          24 |           34.0117  |          1 |

## Claim boundary

Prospective label-free measurement-background audit on opened real-text authors. A pass licenses only a corpus-local, source-disjoint natural grouping residual beyond corpus/context/slot/local-length-matched event marginals. It does not license cross-corpus coordinate transport, personality, emotion, cognition, diagnosis, language invariance, causal interpretation, or clinical validity. A failure rejects this M operator and design, not the existence of all author information.
