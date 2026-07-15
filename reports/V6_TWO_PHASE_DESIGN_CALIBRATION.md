# V6 Two-Phase Design Calibration

## Question

What information budget is required by the two distinct V6 estimands in the
registered endogenous-selection world? This is a synthetic calibration, not a
human participant power calculation.

The free phase estimates a selection profile \(\pi_u\); the balanced fixed
phase estimates response contrasts \(B_u\):

\[
R_\pi=\operatorname{corr}(\operatorname{vec}\hat{\pi}_u,
                              \operatorname{vec}\pi_u),\qquad
R_B=\operatorname{corr}(\operatorname{vec}\hat B_u,
                            \operatorname{vec}B_u).
\]

The frozen criterion uses lower 2.5% simulation quantiles, not observed human
effect sizes.

## Frozen setup

- profile: `full`
- config SHA-256: `babd64683631d02b720de800b727a6eb4e64fd94de295913a597a3e76e6ad8c1`
- repetitions per grid point: `200`
- planted free-choice strength: `1.8`
- no labels, raw text, human identifiers, or clinical outcomes used

## Fixed-phase grid

| conditions | repeats/condition | total observations | level r | response r | support | qualified |
|---:|---:|---:|---:|---:|---:|:---:|
| 2 | 1 | 2 | 0.953 [0.946, 0.960] | 0.679 [0.647, 0.711] | 1.000 [1.000, 1.000] | no |
| 2 | 2 | 4 | 0.974 [0.969, 0.978] | 0.793 [0.772, 0.812] | 1.000 [1.000, 1.000] | yes |
| 2 | 3 | 6 | 0.981 [0.977, 0.985] | 0.846 [0.828, 0.865] | 1.000 [1.000, 1.000] | yes |
| 2 | 4 | 8 | 0.985 [0.980, 0.988] | 0.876 [0.860, 0.891] | 1.000 [1.000, 1.000] | yes |
| 2 | 6 | 12 | 0.989 [0.984, 0.992] | 0.912 [0.902, 0.921] | 1.000 [1.000, 1.000] | yes |
| 4 | 1 | 4 | 0.974 [0.968, 0.978] | 0.679 [0.659, 0.698] | 1.000 [1.000, 1.000] | no |
| 4 | 2 | 8 | 0.985 [0.979, 0.988] | 0.792 [0.778, 0.806] | 1.000 [1.000, 1.000] | yes |
| 4 | 3 | 12 | 0.989 [0.985, 0.992] | 0.846 [0.836, 0.856] | 1.000 [1.000, 1.000] | yes |
| 4 | 4 | 16 | 0.991 [0.986, 0.994] | 0.877 [0.869, 0.884] | 1.000 [1.000, 1.000] | yes |
| 4 | 6 | 24 | 0.992 [0.988, 0.995] | 0.912 [0.905, 0.918] | 1.000 [1.000, 1.000] | yes |
| 6 | 1 | 6 | 0.981 [0.976, 0.985] | 0.677 [0.664, 0.692] | 1.000 [1.000, 1.000] | no |
| 6 | 2 | 12 | 0.989 [0.985, 0.992] | 0.792 [0.783, 0.802] | 1.000 [1.000, 1.000] | yes |
| 6 | 3 | 18 | 0.991 [0.987, 0.994] | 0.845 [0.836, 0.853] | 1.000 [1.000, 1.000] | yes |
| 6 | 4 | 24 | 0.993 [0.988, 0.995] | 0.877 [0.870, 0.883] | 1.000 [1.000, 1.000] | yes |
| 6 | 6 | 36 | 0.994 [0.989, 0.996] | 0.911 [0.907, 0.916] | 1.000 [1.000, 1.000] | yes |

## Free-phase grid

| conditions | free trials | selection-profile r | held-out log-score gain | accidental B support | qualified |
|---:|---:|---:|---:|---:|:---:|
| 4 | 8 | 0.779 [0.725, 0.831] | 0.225 [0.161, 0.283] | 0.170 [0.100, 0.250] | no |
| 4 | 16 | 0.869 [0.825, 0.898] | 0.290 [0.222, 0.344] | 0.401 [0.325, 0.492] | yes |
| 4 | 24 | 0.907 [0.884, 0.928] | 0.315 [0.265, 0.366] | 0.544 [0.458, 0.642] | yes |
| 4 | 48 | 0.950 [0.935, 0.961] | 0.352 [0.293, 0.402] | 0.731 [0.650, 0.800] | yes |

## Frozen synthetic selections

- fixed numeric minimum: 2 conditions x 2 repeats = 4 fixed observations.
- fixed breadth recommendation: 4 conditions x 2 repeats = 8 fixed observations.
- free selection minimum: 16 free observations across 4 conditions.

The first fixed selection minimizes numerical observations. The breadth
recommendation additionally requires the predeclared condition breadth and is
therefore the appropriate architecture when one wants to estimate more than a
binary response contrast.

## Gates

```json
{
  "at_least_one_breadth_qualified_fixed_design": true,
  "at_least_one_fixed_design_qualified": true,
  "at_least_one_free_design_qualified": true
}
```

## Licensed conclusion

Inside this planted generator, free and fixed phases need separate budgets:
free observations improve recovery of a choice distribution but provide only
accidental and incomplete support for response contrasts; balanced fixed
conditions make contrast support complete and improve precision by repeated
within-condition observations. The report supplies a reproducible design
calibration for future protocol construction only. It does not give a required
human sample size, establish a SUICA factor, validate a psychological construct,
or license clinical use.
