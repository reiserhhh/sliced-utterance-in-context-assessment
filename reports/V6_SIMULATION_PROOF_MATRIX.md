# V6 simulation proof matrix

Run: full, seed `60712`, 500 Monte Carlo repetitions, 1,000 paths per repetition.
Config hash: `19f9e6b4bbd6ec1219a759975ddc9856187ec2b312a6b4b24bf33a21f64d059f`.
Simulation code hash: `39003065be921eb4391be9ef2b6994946eefaee9ea4d159bf68036aa3bc11d13`.
Starting Git HEAD: `2cc7944af78330ed31cbbddd6814540a7929dbbb`.

## Result

All 76 audit-frozen row-level gates passed in the final run. The gates were iteratively
revised during adversarial development and are not a preregistration. This is a computational
license within the named generators, not human validation.

| Test | Result |
|---|---:|
| Valid short-memory guard FPR, iid / AR(.6) | .000 / .004 |
| Wrong-memory guard detection | .996-1.000 |
| Zero-inflated serial test FPR / power | .052 / .824 |
| m=3 equivalent-world classification AUC | .501 |
| Lag-aware flow bias, m=5 / m=8 | -.0010 / -.0017 |
| Flow 95% CI coverage, m=5 / m=8 | .942 / .948 |
| Hidden-opportunity thinning AUC | .501 |
| VAR coupling test FPR / power | .038 / 1.000 |
| Above-Nyquist equivalent-world AUC | .501 |
| Below-Nyquist frequency recovery | 1.000 |
| Sufficient-excitation response-operator relative error | .0037 |

SIM-W8 recovered easy conditional ranks, guarded innovation eigenvalues `.08/.12/.18`,
and did not turn the guard band into a forced rank. These thresholds are simulation
design constants and require prospective calibration before human use.

## Interpretation boundary

The matrix closes algebraic and estimator-behavior questions for the specified Gaussian,
Poisson, zero-inflated, VAR, and linear-response worlds. It does not establish a human
personality factor, cross-register portability, clinical validity, or incremental
prediction. The next evidence class is prospective same-person, repeated-condition data.
