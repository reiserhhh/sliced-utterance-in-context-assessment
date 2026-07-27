# SUICA M3 Independent Pairwise Mechanism Decomposition

Decision: `M3_MECHANISM_PAIR_DECOMPOSITION_DISCOVERY_PASS`

## Mechanism summary

| mechanism   |   pair_pass_fraction |   mean_own_partial_geometry |   mean_cross_partial_geometry |   mean_knockout_geometry |   mean_same_author_auc |
|:------------|---------------------:|----------------------------:|------------------------------:|-------------------------:|-----------------------:|
| ar2         |                    1 |                    0.841312 |                     0.0192519 |              0.0080082   |               0.80087  |
| condition   |                    1 |                    0.995952 |                     0.0206489 |             -0.000376073 |               0.965952 |
| density     |                    1 |                    0.8819   |                     0.0721142 |             -0.00100182  |               0.91097  |
| interaction |                    1 |                    0.994774 |                     0.0105384 |              0.00837536  |               0.963361 |
| lag3        |                    1 |                    0.886068 |                     0.0562452 |             -0.0190571   |               0.863577 |

## Pairwise detail

| pair                  | mechanism   | family                          |   own_partial_geometry |   cross_partial_geometry |   knockout_geometry |   same_author_auc |   own_over_crosstalk | pass   |
|:----------------------|:------------|:--------------------------------|-----------------------:|-------------------------:|--------------------:|------------------:|---------------------:|:-------|
| ar2+interaction       | ar2         | ar2_slow_spectrum               |               0.841829 |              -0.00121061 |          0.00723591 |          0.816947 |             0.84304  | True   |
| ar2+interaction       | interaction | nonlinear_partner               |               0.996802 |              -0.00979435 |          0.013694   |          0.962929 |             1.0066   | True   |
| ar2+lag3              | ar2         | ar2_slow_spectrum               |               0.828056 |               0.037771   |         -0.016419   |          0.78649  |             0.790285 | True   |
| ar2+lag3              | lag3        | lag3_partial_operator           |               0.909872 |               0.0148493  |         -0.0216744  |          0.839698 |             0.895023 | True   |
| condition+ar2         | ar2         | ar2_slow_spectrum               |               0.85211  |               0.0269385  |          0.0295273  |          0.810204 |             0.825171 | True   |
| condition+ar2         | condition   | nonlinear_condition             |               0.995403 |               0.0158927  |         -0.00599028 |          0.965174 |             0.979511 | True   |
| condition+interaction | condition   | nonlinear_condition             |               0.998234 |               0.0955621  |          0.0133509  |          0.978253 |             0.902672 | True   |
| condition+interaction | interaction | nonlinear_partner               |               0.998436 |               0.0624873  |          0.0240854  |          0.979261 |             0.935949 | True   |
| condition+lag3        | condition   | nonlinear_condition             |               0.995136 |              -0.0187988  |         -0.00123325 |          0.959046 |             1.01393  | True   |
| condition+lag3        | lag3        | lag3_partial_operator           |               0.912483 |               0.080681   |         -0.0398731  |          0.87376  |             0.831802 | True   |
| density+ar2           | ar2         | ar2_slow_spectrum               |               0.843252 |               0.0135086  |          0.0116886  |          0.789838 |             0.829743 | True   |
| density+ar2           | density     | standardized_distribution_shape |               0.96668  |               0.0162623  |          0.00371379 |          0.938109 |             0.950418 | True   |
| density+condition     | condition   | nonlinear_condition             |               0.995033 |              -0.0100605  |         -0.00763162 |          0.961334 |             1.00509  | True   |
| density+condition     | density     | standardized_distribution_shape |               0.896096 |               0.0639161  |         -0.00611056 |          0.945118 |             0.83218  | True   |
| density+interaction   | density     | standardized_distribution_shape |               0.823037 |               0.133246   |         -0.0130297  |          0.940124 |             0.689791 | True   |
| density+interaction   | interaction | nonlinear_partner               |               0.993072 |               0.00227248 |         -0.0131348  |          0.954754 |             0.9908   | True   |
| density+lag3          | density     | standardized_distribution_shape |               0.841785 |               0.0750326  |          0.0114192  |          0.820529 |             0.766752 | True   |
| density+lag3          | lag3        | lag3_partial_operator           |               0.907502 |              -0.0171907  |          0.00297931 |          0.841769 |             0.924692 | True   |
| interaction+lag3      | interaction | nonlinear_partner               |               0.990785 |              -0.0128119  |          0.00885685 |          0.956502 |             1.0036   | True   |
| interaction+lag3      | lag3        | lag3_partial_operator           |               0.814415 |               0.146641   |         -0.0176604  |          0.899081 |             0.667774 | True   |

## Interpretation boundary

Independent author parameters, partial pairwise geometry, and counterfactual
knockout test whether an estimator tracks its own mechanism rather than merely
reidentifying authors from a correlated composite code. A pass remains a
synthetic decomposition result, not evidence of completeness, human-text
persistence, or personality meaning.
