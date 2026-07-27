# V8 V3.7H.4D R2C Permutation-Orbit Frontier

Date: 2026-07-27

Machine decision:
`V8_PERMUTATION_ORBIT_FRONTIER_V37H4D_R2C_REFUTED_PERMUTATION_ORBIT_EXPLANATION`

Scientific decision:
`GROUP_CELL_CALIBRATION_PASS / INDIVIDUAL_CONDITIONAL_PREDICTION_REFUTED`

Status: fresh-seed synthetic mechanism study. This is not a real-text or
psychological validation.

## Question

R2B showed that geometry predicts frozen-detector power beyond scalar
precision energy, but its finite coordinate model failed on a diffuse halo.
R2C asked whether the detector's finite author-level wild-sign orbit,
estimated on independent mechanism panels, was itself sufficient to predict
the detector outcome on a fresh panel pair.

Panels 0/1 estimated:

\[
\Omega_M=
P\left[
p^{Holm}_{CRC}<.05
\lor
p^{Holm}_{HC}<.05
\mid R_0,R_1
\right].
\]

Panels 2/3 supplied one independent 99-draw CRC/low-rank/HC/Holm outcome.
The frozen R2B six-coordinate model was sealed before R2C outcomes at
SHA-256
`46c2329d697bbfe170f7e73387ff1ba6a2d44e23ff563d4bff942a9a831d4b6a`.

## Pre-outcome audit corrections

The first smoke used 19 permutations. Under three-test Holm and strict
`p < .05`, that resolution cannot reject; smoke was therefore changed to the
same 99 draws as the formal detector.

The first formal process was interrupted before it returned or wrote any
outcomes because the proposed support-spectrum reliability pooled large
between-cell differences. The gate was corrected prospectively to correlate
mechanism and outcome spectra only after centering each registered
`noise x m x lambda x halo-support` cell. The same preregistered formal seed
was then rerun from the beginning.

## Design and integrity

- 1,200 independent base worlds;
- nine paired halo geometries per base;
- 10,800 rows;
- \(m=4,8\);
- Gaussian and heteroskedastic \(t_5\);
- \(\lambda=0,.003,.01,.03,.10\);
- nonzero diffuse author support of 8 or all 64 test authors;
- 999 sign draws for the mechanism orbit;
- 2,000 reconstructions of the exact 99-draw Holm path;
- 99 independent outcome draws.

All source locks, row count, base pairing, seed uniqueness, scalar-information
matching, numeric integrity, and probability bounds passed.

The registered halo discontinuity replicated:

| Noise | m=4 lambda .03 all-author minus lambda 0 | 95% CI |
| --- | ---: | ---: |
| Gaussian | .910 | [.877, .940] |
| \(t_5\) | .897 | [.863, .930] |

## Primary refutation

Against the frozen R2B comparator:

- orbit log-loss gain: **-.6630**, 95% CI [-.7910, -.5365];
- orbit Brier gain: **-.00339**, 95% CI [-.00888, .00196].

Thus the mechanism-panel orbit did not improve row-level prediction of an
independent outcome. It often returned exact probabilities of one:
4,397/10,800 rows had \(\Omega_M=1\), while their fresh-panel outcome rate
was .9350. These relatively rare misses incur very large proper-scoring
penalties.

At threshold .5:

| Predictor | Accuracy | Balanced accuracy |
| --- | ---: | ---: |
| permutation orbit | .8242 | .7442 |
| frozen R2B operator | .8244 | .7934 |

The orbit therefore did not improve individual/base-level discrimination.

## Aggregate calibration

At the 36 registered design-cell means, the orbit was highly calibrated:

- maximum absolute cell error: .0481;
- maximum bootstrap upper bound: .1091;
- mean absolute cell error: .0154;
- frozen R2B mean absolute cell error: .1120.

This is a valid group-level calibration result but not a new individual
mechanism theorem. Because mechanism and outcome panel pairs are exchangeable
within a registered cell, the tower property predicts:

\[
E[\Omega(R_{01})\mid c]
=
P\{D(R_{23})=1\mid c\}.
\]

The cell result verifies the exchangeability and implementation assumptions.
It does not imply:

\[
\Omega(R_{01})
\approx
P\{D(R_{23})=1\mid R_{01}\}
\]

for a particular base world.

## Support-spectrum reliability

The apparent pooled mechanism/outcome correlations were very high:

- \(N_1=.9955\);
- \(N_2=.9939\);
- \(N_\infty=.9602\).

After removing registered cell means:

- \(N_1=.6279\);
- \(N_2=.7753\);
- \(N_\infty=.7901\).

All missed the .80 gate. Most pooled stability came from known experimental
cell differences, not reproducible base-specific geometry.

## Interpretation

R2C separates three levels:

1. total scalar information is insufficient;
2. geometry and finite randomization resolution explain group-level power
   differences;
3. a plug-in orbit from one noisy panel pair is not a calibrated conditional
   predictor for a second panel pair.

The missing operation is not probability clipping. It is integration over
measurement uncertainty in the latent interaction:

\[
P\{D(R_{\mathrm{new}})=1\mid R_{\mathrm{observed}}\}
=
\int P\{D(R_{\mathrm{new}})=1\mid Q\}
\,p(Q\mid R_{\mathrm{observed}})\,dQ.
\]

Any next experiment must estimate this posterior-predictive quantity on
fresh data. A post-hoc sigmoid calibration of \(\Omega_M\) would hide the
mechanism failure and is not an acceptable correction.

## Claim boundary

Supported:

- the registered halo changes the finite detector orbit;
- group-cell detector power is reproduced under exchangeable panels;
- panel-level support geometry has moderate but sub-threshold repeatability.

Refuted:

- the plug-in randomization orbit as a sufficient individual conditional
  predictor;
- the claim that near-perfect pooled support-spectrum correlations imply
  within-cell reliability.

Still closed:

- observable real-text estimation of planted support or \(Q\);
- personality or psychological constructs;
- diagnosis, causality, or clinical use.

## Artifacts

- `docs/V8_PERMUTATION_ORBIT_FRONTIER_V37H4D_R2C_PLAN.md`
- `configs/v8_permutation_orbit_frontier_v37h4d_r2c.json`
- `suica_core/v8_permutation_orbit_frontier.py`
- `scripts/run_suica_v8_permutation_orbit_frontier_v37h4d_r2c.py`
- `results/v8_permutation_orbit_frontier/v37h4d_r2c_discovery_10800rows_20260727/`
