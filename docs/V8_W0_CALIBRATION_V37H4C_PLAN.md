# V8 V3.7H.4C W0 Calibration Plan

Status: prospective calibration protocol, frozen before execution.

V3.7H.4 observed 2 false refusals in each 100-repetition additive control
cell. The point estimate was 2%, but the registered one-sided upper bound was
.06162 and did not certify a rate below .05.

H.4C does not alter or re-optimize the detector. It asks only whether the
unchanged detector's additive-world familywise false-refusal probability can
be calibrated with adequate Monte Carlo resolution.

## Detector lock

H.4C must use the exact H.4 detector:

- 99 permutations per diagnostic;
- CRC, low-rank residual concentration, and held-out gain;
- Holm familywise alpha .05;
- the same rank candidates and panel split;
- the same additive generator and two registered noise modes.

The H.4 config and three detector source hashes are frozen in
`configs/v8_w0_calibration_v37h4c.json`. Any mismatch stops the run.

The 200 prior H.4 W0 trials are not pooled into H.4C.

## Design

- 1,000 fresh repetitions per noise mode;
- Gaussian and heteroskedastic standardized \(t_5\) noise;
- 2,000 total additive control cells;
- independent world and diagnostic seeds for every cell;
- no nonadditive world and no effect-size tuning.

For noise mode \(m\), let \(X_m\) be the number of familywise
`MODEL_INADEQUATE` refusals among \(n=1000\) trials.

The exact one-sided bounds use tail alpha .025 per noise mode. This provides
Bonferroni simultaneous coverage of at least .95 across the two modes:

\[
L_m=\operatorname{Beta}^{-1}
(.025;X_m,n-X_m+1),
\]

\[
U_m=\operatorname{Beta}^{-1}
(.975;X_m+1,n-X_m).
\]

## Frozen count boundaries

For \(n=1000\):

- `CALIBRATED` is possible only when \(X_m\le36\) for both modes;
- `MISCALIBRATED` is declared when \(X_m\ge65\) for either mode;
- counts 37-64 are `INCONCLUSIVE`.

At the boundaries:

\[
U(36,1000)=.049493<.05,
\]

\[
L(65,1000)=.050520\ge.05.
\]

## Frozen operating characteristics

For one noise mode:

| True refusal rate | P(CALIBRATED) | P(INCONCLUSIVE) | P(MISCALIBRATED) |
| ---: | ---: | ---: | ---: |
| .01 | 1.000000 | 0.000000 | 0.000000 |
| .02 | .999635 | .000365 | 0.000000 |
| .03 | .883823 | .116177 | 0.000000 |
| .04 | .291924 | .707952 | .000124 |
| .05 | .021155 | .958095 | .020750 |
| .06 | .000419 | .729213 | .270368 |
| .08 | 0.000000 | .032308 | .967693 |

The design has greater than 99.9% probability of certification if the true
per-noise rate is .02. It deliberately leaves a broad uncertainty region near
the .05 boundary.

## Decision

- `CALIBRATED`: both \(U_m<.05\);
- `MISCALIBRATED`: any \(L_m\ge.05\);
- `INCONCLUSIVE`: neither condition;
- `STOP_INTEGRITY`: source lock, seed uniqueness, row count, or numeric
  integrity fails.

Diagnostic-specific trigger counts are descriptive only. No individual
diagnostic threshold may be changed after the run.

## Claim boundary

A `CALIBRATED` result would certify the synthetic additive-control
false-refusal rate for this exact 99-permutation detector under the two
registered noise generators. It would not validate real-text calibration,
general misspecification detection, causal localization, personality meaning,
diagnosis, or clinical use.
