# V8 V3.7H.4D R2E.2 Fresh Endpoint Confirmation

Date: 2026-07-27

Machine decision:
`V8_R2E2_CONFIRMED_NORMAL_ONLY`

Scientific decision:
`REGISTERED_NORMAL_DIRECTION_ACTIVE / REGISTERED_TANGENT_FAMILY PRACTICALLY_NULL`

Status: fresh-seed synthetic endpoint confirmation. This is local to the
frozen detector and registered geometry.

## Question

R2D Gate-0 found too little pooled within-cell probability heterogeneity to
justify fitting a full posterior predictor. R2E then asked whether this was
because:

1. individual variation was not planted along a detector-relevant direction;
2. the detector could not transmit planted variation; or
3. a hidden macro-coordinate-matched tangent direction carried additional
   detector information.

R2E.2 prospectively separated two endpoint families:

- a known halo-normal direction as the positive control;
- one all-author tangent rotation that preserves registered macro
  coordinates and total information.

## Integrity and design

- 80 fresh parents per noise family, 160 total;
- five geometries per parent: baseline, normal `.09 +/-`,
  tangent `.4 +/-`;
- 32 outcomes per geometry;
- 25,600 detector outcomes;
- Gaussian and heteroskedastic \(t_5\) noise;
- 20,000 parent-block bootstrap draws;
- fresh root and analysis seeds;
- no R2E.1 outcomes used in estimation.

The geometry-only preflight covered all 800 planned geometries before
outcome interpretation. All source-lock, row-count, unique-seed,
common-random-number, reconstruction, builder-equivalence, information,
frame, centering, halo-share, support, numeric, and positive-control potency
checks passed.

Maximum normalized builder-equivalence error was `2.32e-16`. Normal endpoint
leakage was approximately `.0458` versus `.0107-.0112` on the opposite side.

The preflight, formal run, and confirmation analysis each independently
reverified as:

- `RUN_MANIFEST_PASS`;
- `INVENTORY_PASS`.

An independent mathematical audit returned
`PASS / ACCEPT_V8_R2E2_CONFIRMED_NORMAL_ONLY`.

## Registered familywise analysis

The normal family contained the two noise-specific \(J_N\) endpoints. Its
one-sided family alpha `.05` gave Bonferroni endpoint alpha `.025`.

| Noise | \(J_N\) | one-sided Bonferroni lower |
| --- | ---: | ---: |
| Gaussian | .196888 | .191532 |
| \(t_5\) | .185465 | .179719 |

Both lower bounds are far above the `.005` practical threshold. The frozen
detector therefore clearly transmits variation planted along the registered
normal direction.

The tangent family contained noise-specific \(J_T\), noise-specific
\(\Delta V_T\), and pooled \(\Delta V_T\). Its one-sided family alpha `.05`
gave Bonferroni endpoint alpha `.01`.

| Endpoint | Point | one-sided Bonferroni upper |
| --- | ---: | ---: |
| \(J_T\), Gaussian | -.000164 | -.000044 |
| \(J_T\), \(t_5\) | -.000019 | .000189 |
| \(\Delta V_T\), Gaussian | .000289 | .001740 |
| \(\Delta V_T\), \(t_5\) | .000069 | .001244 |
| pooled \(\Delta V_T\) | .000179 | .001132 |

Every tangent upper bound is at most `.001740`, less than 35% of the `.005`
threshold. Studentized max-t sensitivity bounds agree; their largest upper
bound is `.001727`.

## Decision

The two registered conditions were both met:

\[
\operatorname{LCB}(J_N)>.005
\]

for both normal endpoints, and:

\[
\operatorname{UCB}(J_T),
\operatorname{UCB}(\Delta V_T),
\operatorname{UCB}(\Delta V_{T,\mathrm{pooled}})
\le .005
\]

for all five tangent endpoints.

The correct decision is therefore
`V8_R2E2_CONFIRMED_NORMAL_ONLY`.

## What this changes

The result rules out a simple explanation that the detector is generally
incapable of transmitting planted within-cell heterogeneity. It transmits a
large change when the geometry moves across its registered margin.

For the tested tangent family, changing orientation inside the
macro-coordinate-matched shell does not produce a practically material
change in detector probability. In local geometric language, the tested
detector has:

- a large directional response along the registered normal;
- a practical first-order null along the registered tangent rotation.

This explains the R2D Gate-0 result more precisely: the current generator
does not contain enough variation along detector-relevant directions within
its registered cells. The missing target is not recovered merely by
rotating one hidden halo direction while keeping the measured shell fixed.

## Boundary and next theory step

The confirmation applies only to:

- `m=4`;
- baseline halo share `.01`;
- the all-author support-64 construction;
- normal magnitude `.09`;
- tangent magnitude `.4`;
- the frozen 99-sign/Holm synthetic detector;
- the two registered noise families.

It does not prove that every tangent direction is null. It does not prove
that the finite geometry coordinates are sufficient. It does not identify
personality, semantics, intelligence, diagnosis, causality, or clinical
utility.

The next mathematical object should be the local response form of the
detector probability:

\[
p(Q+\delta)
\approx
p(Q)+\langle g_Q,\delta\rangle
\frac12\langle\delta,H_Q\delta\rangle.
\]

R2E.2 identifies one active normal direction and one practically null
tangent family. A future protocol may estimate a basis of independent
tangent directions and test curvature without reusing these outcomes for
direction selection. Until then, the accepted statement is local and
one-family only.

## Artifacts

- `docs/V8_CONDITIONAL_HETEROGENEITY_INJECTION_V37H4D_R2E2_PLAN.md`
- `configs/v8_conditional_heterogeneity_injection_v37h4d_r2e2.json`
- `scripts/run_suica_v8_conditional_heterogeneity_injection_v37h4d_r2e1.py`
- `scripts/analyze_suica_v8_conditional_heterogeneity_injection_v37h4d_r2e2.py`
- `results/v8_conditional_heterogeneity_injection/v37h4d_r2e2_geometry_preflight_800geometries_20260727/`
- `results/v8_conditional_heterogeneity_injection/v37h4d_r2e2_fresh_endpoint_confirmation_25600outcomes_20260727/`
- `results/v8_conditional_heterogeneity_injection/v37h4d_r2e2_confirmation_analysis_20260727/`
- `reports/V8_CONDITIONAL_HETEROGENEITY_INJECTION_V37H4D_R2E2_INDEPENDENT_AUDIT.md`
