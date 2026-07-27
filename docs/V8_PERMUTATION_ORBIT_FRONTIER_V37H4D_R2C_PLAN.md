# V8 V3.7H.4D R2C Resolution-Indexed Permutation-Orbit Frontier

Status: prospective fresh-seed synthetic mechanism experiment.

## Motivation

R2B established that total precision energy is not sufficient, while its
finite geometry vector improved but did not fully calibrate unseen geometry.
The largest failure was a discontinuity in the halo family: a small diffuse
component changed the attainable author-level wild-sign orbit far more than
it changed second-order effective support.

R2C does not tune the detector or add geometry labels. It estimates the
finite randomization orbit on panels independent of the final outcome.

## Frozen comparator

The R2B scalar-plus-six-coordinate logistic operator was fitted and frozen
before any R2C outcomes:

`results/v8_geometry_information_operator/v37h4d_r2b_frozen_operator_20260727/frozen_operator.json`

Artifact SHA-256:
`46c2329d697bbfe170f7e73387ff1ba6a2d44e23ff563d4bff942a9a831d4b6a`.

No R2C outcome may change its scaler, coefficients, feature order, or ridge
strength.

## Orbit object

For mechanism-panel residuals:

\[
z_u=\langle R_{0u},R_{1u}\rangle,\qquad
p_u=\frac{|z_u|}{\sum_v |z_v|},
\]

\[
N_1=\exp\left(-\sum_u p_u\log p_u\right),\quad
N_2=\left(\sum_u p_u^2\right)^{-1},\quad
N_\infty=(\max_u p_u)^{-1}.
\]

The mechanism panel uses 999 independently generated author sign vectors to
form the joint three-channel null reservoir. From that reservoir, 2,000
independent groups of 99 draws reproduce the exact CRC, low-rank, HC, and
Holm decision path. The resulting quantity is:

\[
\Omega_M=
P\left[
p^{Holm}_{CRC}<.05
\ \lor\
p^{Holm}_{HC}<.05
\mid R_0,R_1
\right].
\]

The final binary endpoint is computed once from panels 2/3 using independent
noise and an independent 99-draw wild-sign stream.

## Fresh paired frontier

- \(m\in\{4,8\}\);
- Gaussian and heteroskedastic \(t_5\);
- K=128, 16 conditions, four active conditions;
- \(\lambda\in\{0,.003,.01,.03,.10\}\);
- at \(\lambda=0\), the core author support is \(m\);
- at nonzero lambda, the diffuse component has author support 8 or 64;
- 300 base worlds per `m x noise` cell;
- nine paired geometries per base;
- 10,800 total rows.

Every geometry is matched to its paired iid anchor's scalar residual
information within \(10^{-6}\). World, anchor, orbit-sign, and outcome-sign
streams are paired within base; geometry-generation streams are independent.

## Gates

1. Source hashes, frozen comparator, row count, base pairing, seed
   uniqueness, numeric integrity, and information matching pass.
2. At \(m=4\), the all-author \(\lambda=.03\) minus \(\lambda=0\) power-gap
   lower bound exceeds .30 under both noise modes.
3. Orbit-minus-frozen-R2B log-loss gain lower bound exceeds .02.
4. Orbit-minus-frozen-R2B Brier gain lower bound exceeds .01.
5. Every registered cell has calibration error point estimate at most .10
   and bootstrap upper bound at most .15.
6. The \(m=4,\lambda=.03\), all-author calibration error is at most .10 in
   both noise modes.
7. After centering each registered
   `noise x m x lambda x halo-support` cell, mechanism/outcome
   \(N_1,N_2,N_\infty\) correlations are all at least .80. Overall
   correlations are descriptive only and cannot satisfy this gate.

## Decisions

- `PASS`: all gates pass.
- `PARTIAL_ORBIT_ORDER_ONLY`: predictive gains pass but full cell
  calibration does not.
- `PARTIAL_ORBIT_CALIBRATED_SPECTRUM_UNSTABLE`: calibration passes but
  cross-panel support-spectrum reliability does not.
- `REFUTED_PERMUTATION_ORBIT_EXPLANATION`: orbit gains fail.
- `STOP_INVALID_FRONTIER`: integrity or the registered halo discontinuity
  fails.

Passing establishes only a mathematical mechanism for the frozen synthetic
detector. It does not make the oracle R2B coordinates or planted support
observable in real text.
