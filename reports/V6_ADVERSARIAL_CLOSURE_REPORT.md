# V6 Adversarial Simulation Closure

Date: 2026-07-13. Profile: full, 500 Monte Carlo repetitions. Verdict:
**12/12 gates pass within the registered synthetic families**.

## A. Irregular sampling and missingness

The continuous-time, elapsed-time-aware estimator recovered decay with relative bias
`.017`, mean relative error `.121`, and 95% coverage `.946`. Treating irregular samples
as a regular AR process increased error to `.380`. Under MNAR, non-ignorability was not
reliably detectable from observed outcomes (`alarm=.304`); the correct action is
`REFUSE` or sensitivity analysis, not correction from observed data alone.

## B. Opportunity measurement error

With duplicated opportunity proxies, estimated reliability tracked the planted curve.
Operator recovery declined from `.999` at reliability 1.0 to `.910` at reliability
about `.55`; the low-reliability world was refused 100% of the time. A single unknown
proxy has exact scale equivalence:

```text
O exp(w) = (cO) exp(w - log(c)).
```

The simulated equivalence error was `3.6e-15`, AUC `.5`; absolute level and
opportunity-corrected response are therefore refused without calibration data.

## C. Nonlinear and time-varying response

A preregistered quadratic plus phase-interaction basis improved independent-occasion
held-out MSE by `.266`. The static linear slope bias was `.148`; the full model bias was
`.019`, and the time-change term was recovered in `99.6%` of repetitions. This licenses
only the frozen basis projection, not arbitrary nonparametric response or support
extrapolation.

## D. Multiparty and role structure

Omitting partner input biased the apparent self coefficient by `.133`; including it
reduced coefficient error to `.053` and improved held-out MSE by `.061`. In the crossed
actor-partner-role design, actor-operator recovery was `.984`; unseen-dyad
own-vs-stranger standardized delta was `.629`, MC CI `[.018,.068]` on the raw delta.
The structured null FPR was `0/500`; graph and role support passed. Single-partner,
unseen-actor, and unseen-role individual parameters are explicitly refused.

## E. High-dimensional sparse coupling

Threshold selection used validation prediction loss, never true support. At
`p=12`, 12 planted off-diagonal edges and `N=1800`, support F1 was `.968`, relative
Frobenius error `.107`, off-diagonal FPR `.007`, and held-out gain was positive. The
registered effective-sample requirement was about `298`; a 100-observation individual
graph is refused rather than interpreted as zero coupling.

## Scope of closure

This closes the named adversarial simulation program: irregular time, MAR/MNAR,
opportunity measurement error, nonlinear/time-varying response, multiparty/role
confounding, and high-dimensional sparse predictive coupling. It does not prove that
these finite DGP families exhaust natural language. It establishes estimator behavior
and refusal rules before human data, not psychological validity.

Artifact: `results/v6_adversarial_closure/v6_adversarial_closure_full.json`.
