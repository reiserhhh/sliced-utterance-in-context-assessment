# V8 V3.7H.4D R2E.1 Corrected Geometry Injection

Date: 2026-07-27

Machine decision:
`V8_R2E1_INCONCLUSIVE_NO_TUNING`

Scientific decision:
`VALID_DISCOVERY / NORMAL_CHANNEL_DETECTED / TANGENT_CHANNEL_UNRESOLVED`

Status: corrected fresh-seed synthetic discovery. This is a detector-mechanism
experiment, not real-text or psychological validation.

## Why R2E.1 was required

The original R2E reconstruction used different halo-support RNG paths for
the baseline and recovered core. It therefore mixed two unrelated core
matrices and invalidated its positive control. R2E.1 corrected the
construction by recovering the zero-halo core with the same support-64 RNG
path and directly checking every normal arm against the frozen builder.

The maximum normalized builder-equivalence error was
`2.57e-16`, well below the registered `1e-10` limit. All 18 geometry,
source-lock, seed, pairing, numeric, and potency checks passed before
scientific interpretation.

## Design

- 40 fresh parents per noise family, 80 total;
- Gaussian and heteroskedastic \(t_5\) noise;
- 13 geometries per parent;
- 32 independent outcomes per geometry;
- 33,280 detector outcomes;
- normal perturbations \(\tau\in\{.03,.06,.09\}\);
- tangent rotations \(\phi\in\{.1,.2,.4\}\);
- 20,000 parent-block bootstrap draws;
- common random numbers for each registered plus/minus crossover.

The paired direction statistic was:

\[
J =
\frac{1}{4n}\sum_i
\left[
(\bar D_{i,+}-\bar D_{i,-})^2
-
\frac{s^2_{D_i}}{R}
\right],
\]

where the second term removes finite-replicate outcome noise. Negative
estimates were retained.

## Discovery results

At the primary normal endpoint \(\tau=.09\):

| Noise | \(J_N\) | \(\Delta V_N\) |
| --- | ---: | ---: |
| Gaussian | .190625 | .183559 |
| \(t_5\) | .189831 | .181466 |

The normal positive control passed in both noise families. Its mean whitened
leakage moved from approximately `.011` on the negative side to `.046` on
the positive side, reproducing the intended detector-margin change.

At the primary tangent endpoint \(\phi=.4\):

| Noise | \(J_T\) | \(\Delta V_T\) |
| --- | ---: | ---: |
| Gaussian | -.000076 | .000283 |
| \(t_5\) | .000151 | .000172 |

The pooled tangent \(\Delta V\) was `.000228`. Point estimates were therefore
near zero while the normal channel was large.

## Why the machine result remained inconclusive

The frozen R2E.1 decision used one unstudentized simultaneous family across
nine heterogeneous endpoints. The resulting common upper radius was
`.010283`, more than twice the `.005` practical threshold. Large normal-arm
variance dominated this family and prevented the near-zero tangent
estimates from being declared practically null.

This is not permission to reinterpret the discovery as confirmation.
R2E.1 correctly remained inconclusive under its registered analysis.
Changing its interval family after seeing the outcomes would be tuning.

The admissible next step was therefore a fresh confirmation with:

- only the registered normal `.09` and tangent `.4` endpoints;
- prospectively separated normal and tangent families;
- 80 new parents per noise family;
- no reuse of R2E.1 outcomes.

## Interpretation

R2E.1 establishes that:

- the corrected synthetic construction is geometrically valid;
- the frozen detector is sensitive to the registered halo-normal direction;
- the registered tangent point estimates are much smaller;
- the discovery analysis alone cannot certify a practical tangent null.

It does not establish that all tangent directions are null, that the finite
macro-coordinate vector is sufficient, or that the detected direction is a
personality construct.

## Artifacts

- `docs/V8_CONDITIONAL_HETEROGENEITY_INJECTION_V37H4D_R2E1_PLAN.md`
- `configs/v8_conditional_heterogeneity_injection_v37h4d_r2e1.json`
- `scripts/run_suica_v8_conditional_heterogeneity_injection_v37h4d_r2e1.py`
- `results/v8_conditional_heterogeneity_injection/v37h4d_r2e1_geometry_preflight2_1040geometries_20260727/`
- `results/v8_conditional_heterogeneity_injection/v37h4d_r2e1_corrected_discovery_33280outcomes_20260727/`
