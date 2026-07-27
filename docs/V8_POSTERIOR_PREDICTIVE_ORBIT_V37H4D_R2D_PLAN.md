# V8 V3.7H.4D R2D Posterior-Predictive Orbit

Status: prospective design; implementation and outcomes not started.

## Objective

R2C showed that the finite permutation orbit is calibrated for registered
group cells but overconfident for an independent panel from the same base.
R2D tests whether explicitly integrating latent-interaction uncertainty and
future-panel measurement noise recovers individual conditional probability.

No probability clipping, outcome-fitted calibration, detector modification,
or reuse of R2C seeds is allowed.

## Estimand

In the additive-residual subspace:

\[
r_p=P_{\mathcal M}Q+\epsilon_p,\qquad p\in\{0,1\}.
\]

For the Gaussian oracle-noise arm:

\[
V_Q=
\left(
P^\top\Sigma_0^{-1}P+
P^\top\Sigma_1^{-1}P
\right)^+,
\]

\[
\hat Q=
V_QP^\top
\left(
\Sigma_0^{-1}r_0+
\Sigma_1^{-1}r_1
\right),
\qquad
Q\mid M\sim N(\hat Q,V_Q).
\]

The heteroskedastic \(t_5\) arm uses its fixed scale-mixture representation
and draws cell-level latent precision jointly with \(Q\).

For posterior draw \(b\):

1. draw \(Q^{(b)}\) from the mechanism-panel posterior;
2. draw future opportunity counts and masks;
3. draw future Gaussian or \(t_5\) measurement noise and panel shock;
4. rerun the registered residualization;
5. run the unchanged 99-sign, three-channel Holm detector;
6. record \(D^{(b)}\).

The registered finite estimator is:

\[
\widehat\pi(M)=
\frac{\frac12+\sum_{b=1}^{B}D^{(b)}}{B+1},
\]

with \(B=256\). The one-half term is the frozen Jeffreys Monte Carlo
estimator, not post-outcome clipping.

## Fresh design

- 12 cells:
  `m={4,8} x noise={Gaussian,t5} x`
  `{lambda=0 core, lambda=.01 all64, lambda=.03 all64}`;
- 100 fresh mechanism bases per cell, 1,200 total;
- 64 independent outcome replicas per mechanism base;
- 256 posterior-predictive draws per base;
- unchanged 99 wild signs, CRC/low-rank/HC, and Holm .05;
- no R2C seeds, panels, or outcomes.

Two frozen arms:

1. `oracle_noise`: simulator noise and acquisition parameters are known;
2. `estimated_noise`: nuisance parameters are estimated only from 500
   independent W0 calibration worlds per noise family.

Frozen comparators:

- R2B six-coordinate operator;
- R2C plug-in permutation orbit.

## Conditional truth

For base \(i\), the 64 independent outcome replicas estimate
\(\widehat p_i^\star\). Improvement beyond registered cell means is:

\[
R^2_{\mathrm{conditional}}
=
1-
\frac{\sum_i(\widehat\pi_i-\widehat p_i^\star)^2}
{\sum_i(\bar p_{\mathrm{cell}(i)}-\widehat p_i^\star)^2}.
\]

The base seed is the bootstrap unit.

## Hard gates

1. Source locks, seed independence, panel isolation, posterior provenance,
   positivity, and residual-subspace rank pass.
2. Oracle R2D minus R2C log-loss lower bound exceeds .10.
3. Oracle R2D minus frozen R2B log-loss lower bound exceeds .02.
4. Oracle R2D Brier gains over both comparators have lower bounds above .005.
5. Conditional \(R^2\) bootstrap lower bound exceeds .10 in both noise
   families.
6. Simultaneous max-cell calibration point estimate is at most .05 and its
   max-stat 95% upper bound is at most .10.
7. On the frozen `R2C orbit_probability=1` diagnostic subset, calibration
   error is at most .05.
8. Estimated-noise minus oracle log-loss degradation upper bound is at most
   .02.
9. Positivity coverage below .95 or deficient posterior precision rank
   forces `REFUSE`; it cannot be imputed.

## Decisions

- `PASS_POSTERIOR_PREDICTIVE_ORBIT`: all oracle and estimated-noise gates
  pass.
- `PARTIAL_NUISANCE_UNIDENTIFIED`: oracle passes, estimated-noise fails.
- `REFUTED_INDIVIDUAL_CONDITIONAL`: only aggregate cell calibration remains.
- `REFUTED_MEASUREMENT_NOISE_POSTERIOR`: oracle cannot beat frozen R2B or
  conditional \(R^2\le0\).
- `STOP_INVALID_PROTOCOL`: any outcome calibration, probability clipping,
  source drift, seed reuse, or panel leakage occurs.

Passing remains a statement about the registered synthetic detector. It does
not identify personality, psychological constructs, semantics, diagnosis,
causality, or clinical validity.
