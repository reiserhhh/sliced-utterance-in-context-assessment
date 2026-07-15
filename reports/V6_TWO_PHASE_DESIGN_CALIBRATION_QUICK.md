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

- profile: `quick`
- config SHA-256: `0b203d3fcdad6a46271ea85088d555cf377a21da6d77083bb0566b941b6c1e83`
- repetitions per grid point: `20`
- planted free-choice strength: `1.8`
- no labels, raw text, human identifiers, or clinical outcomes used

## Fixed-phase grid

| conditions | repeats/condition | total observations | level r | response r | support | qualified |
|---:|---:|---:|---:|---:|---:|:---:|
| 2 | 1 | 2 | 0.952 [0.942, 0.959] | 0.679 [0.657, 0.709] | 1.000 [1.000, 1.000] | no |
| 2 | 2 | 4 | 0.973 [0.968, 0.977] | 0.794 [0.774, 0.818] | 1.000 [1.000, 1.000] | yes |
| 2 | 4 | 8 | 0.983 [0.978, 0.987] | 0.874 [0.859, 0.884] | 1.000 [1.000, 1.000] | yes |
| 4 | 1 | 4 | 0.973 [0.965, 0.978] | 0.678 [0.661, 0.696] | 1.000 [1.000, 1.000] | no |
| 4 | 2 | 8 | 0.984 [0.978, 0.989] | 0.787 [0.770, 0.801] | 1.000 [1.000, 1.000] | yes |
| 4 | 4 | 16 | 0.990 [0.988, 0.992] | 0.876 [0.866, 0.885] | 1.000 [1.000, 1.000] | yes |

## Free-phase grid

| conditions | free trials | selection-profile r | held-out log-score gain | accidental B support | qualified |
|---:|---:|---:|---:|---:|:---:|
| 4 | 8 | 0.772 [0.703, 0.820] | 0.210 [0.151, 0.265] | 0.199 [0.122, 0.267] | no |
| 4 | 16 | 0.877 [0.847, 0.901] | 0.289 [0.235, 0.339] | 0.390 [0.326, 0.472] | yes |
| 4 | 24 | 0.909 [0.889, 0.932] | 0.315 [0.251, 0.384] | 0.551 [0.494, 0.650] | yes |

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
