# SUICA M3 Cross-Family Power Preflight

Decision: `M3_CROSS_FAMILY_V4_SMOKE_DIAGNOSTIC`

## Purpose

This development-seed run asks whether one generator-blind estimator suite has
enough power to justify an artifact-sealed fresh-seed confirmation. Failure is
a power or specification finding, not evidence against human personality.

## Target summary

| world           | target             |   seeds |   validity_fraction |   refusal_max |   expected_auc |   cheap_auc |   expected_geometry |   cheap_geometry |   heldout_increment |   positive_increment_fraction |   off_target_geometry |   knockout_geometry |
|:----------------|:-------------------|--------:|--------------------:|--------------:|---------------:|------------:|--------------------:|-----------------:|--------------------:|------------------------------:|----------------------:|--------------------:|
| cf_d_copula     | distribution       |       2 |                   1 |             0 |       0.589372 |    0.520984 |           0.21278   |        0.0201572 |         0.00450607  |                           1   |           nan         |          0.0344039  |
| cf_d_multimodal | distribution       |       2 |                   1 |             0 |       0.571445 |    0.458975 |           0.355474  |        0.0151636 |         0.000812712 |                           0.5 |           nan         |          0.0590134  |
| cf_d_skew       | distribution       |       2 |                   1 |             0 |       0.69603  |    0.507926 |           0.496573  |       -0.0222899 |         0.0299817   |                           1   |           nan         |          0.107967   |
| cf_d_tail       | distribution       |       2 |                   1 |             0 |       0.512115 |    0.502868 |           0.0407269 |       -0.0523554 |         0.00489602  |                           1   |           nan         |          0.0702741  |
| cf_kp_arch      | nonlinear_dynamics |       2 |                   1 |             0 |       0.687991 |    0.520833 |           0.658846  |        0.0434691 |         3.93559e-06 |                           1   |           nan         |          0.0121225  |
| cf_kp_cycle     | direction          |       2 |                   1 |             0 |       0.752831 |    0.51521  |           0.865212  |       -0.0392368 |         0.0276558   |                           1   |           nan         |          0.00964988 |
| cf_kp_hsmm      | hazard             |       2 |                   1 |             0 |       0.766342 |    0.48547  |           0.825639  |       -0.0481677 |         0.00193947  |                           1   |           nan         |          0.128962   |
| cf_o_neural     | condition          |       2 |                   1 |             0 |       0.999962 |    0.492942 |           0.977174  |       -0.0805511 |         0.324813    |                           1   |             0.0816781 |          0.0440236  |
| cf_o_neural     | partner            |       2 |                   1 |             0 |       0.999962 |    0.4903   |           0.914459  |       -0.0459977 |         0.266718    |                           1   |             0.103815  |          0.0144544  |
| cf_o_spline     | condition          |       2 |                   1 |             0 |       0.999698 |    0.486602 |           0.979414  |        0.0437621 |         0.387292    |                           1   |             0.062581  |          0.0114948  |
| cf_o_spline     | partner            |       2 |                   1 |             0 |       0.999736 |    0.497283 |           0.958948  |       -0.0814828 |         0.365224    |                           1   |             0.0372803 |          0.0166578  |
| cf_o_voronoi    | condition          |       2 |                   1 |             0 |       1        |    0.504227 |           0.91612   |        0.0477588 |         0.19442     |                           1   |             0.179552  |          0.0599143  |
| cf_o_voronoi    | partner            |       2 |                   1 |             0 |       0.999962 |    0.50619  |           0.951091  |       -0.0072861 |         0.222927    |                           1   |             0.123838  |          0.0380779  |

## Gates not yet satisfied

- `cf_d_tail::distribution`

## Boundary

No confirmation truth was sealed or opened. Hyperparameters may still change
only in this preflight branch. Human text, psychological constructs, and
clinical use remain outside scope.
