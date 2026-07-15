# V6 Nonlinear Path-Geometry Simulation

## Planted world

For author phase `theta_u`, independent runs obey

\[
Z_t\sim Uniform(0,2\pi),\qquad
W_{t+1}=2Z_t+\theta_u+\eta_{t+1}\pmod{2\pi},
\]

with `eta ~ von Mises(0, kappa=8.0)`. Every author has the same marginal
state distribution, mean, covariance, and **linear** lag covariance. The author
signal is only the nonlinear conditional transition phase:

\[
M_u=\mathbb{E}\left[e^{i(W_{t+1}-2Z_t)}\right]
=\frac{I_1(\kappa)}{I_0(\kappa)}e^{i\theta_u}.
\]

This is an explicit counterexample to the claim that mean/covariance/linear-AR
summaries exhaust path information. It is not a model of human language.

## Results across 100 independently generated worlds

| object                        |   mean_auc |   q025 |   q975 |
|:------------------------------|-----------:|-------:|-------:|
| linear_summary_auc            |      0.503 |  0.459 |  0.559 |
| conditional_phase_witness_auc |      0.985 |  0.981 |  0.988 |
| shuffled_phase_witness_auc    |      0.548 |  0.484 |  0.600 |

## Interpretation

The linear family is expected to stay at chance because its population moments do
not contain `theta_u`. The conditional circular-kernel witness is expected to
recover it; endpoint-preserving interior shuffling must destroy that recovery.
The simulation therefore licenses only `SUPPORTED-SYNTHETIC`: a nonlinear
conditional transition object can capture a real, order-dependent author
configuration that linear factor-style summaries provably omit.
