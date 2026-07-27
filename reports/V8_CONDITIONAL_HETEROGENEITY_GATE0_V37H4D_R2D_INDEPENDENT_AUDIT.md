# V8 H4D-R2D Gate-0 Independent Mathematical Audit

Date: 2026-07-27

Ruling:
`ACCEPT_STOP / REJECT_FULL_R2D_FOR_REGISTERED_DGP`

## Decision audit

The sole scientific STOP condition was:

\[
U_{95}\!\left[
E_c\{\operatorname{Var}(p_i\mid c)\}
\right]\le .005.
\]

The result was:

\[
\widehat V_{\mathrm{pooled}}=.002925,
\qquad 95\%\ CI=[.001456,.004114].
\]

The upper bound is `.000886` below the frozen threshold, so STOP follows
without reference to the A/B prediction result.

## Estimator audit

For \(S_i\sim\operatorname{Binomial}(R,p_i)\), the registered estimator

\[
\widehat V_c=
\operatorname{Var}_i(S_i/R)
-
\frac1{n_c}\sum_i
\frac{S_i(R-S_i)}{R^2(R-1)}
\]

correctly subtracts expected binomial measurement variance. The first term
uses `ddof=1`, and negative estimates are retained.

The base is the statistical cluster. Each A/B pair shares a latent base but
uses independent outcome noise. Cells use independent bases. The
cell-stratified base-block bootstrap therefore matches the generated
hierarchy. No outcome row is treated as an independent base.

The eight-cell one-sided max-deviation interval and pooled percentile
interval match their respective estimands. Source streams were unique,
replicates complete, and the latent interaction fixed within each base.

Remaining numerical caveats are 50 bases per cell and an unstudentized
bootstrap. These affect fine threshold coverage but do not authorize
changing the frozen decision.

## Interpretation boundary

R2C estimated stable design-cell power:

\[
P(D=1\mid \mathrm{noise},m,\lambda,\mathrm{support}).
\]

Gate-0 estimates residual base-level variation after those conditions are
fixed:

\[
\operatorname{Var}\{
P(D=1\mid Q_i,c)
\mid c
\}.
\]

The latter is too small on average to justify full posterior-predictive R2D
under the registered resource criterion. This supports a group/design-level
interpretation of the current simulator. It does not show that real people
lack stable individual differences or that SUICA cannot measure them.

The `lambda=.01/all64` cells are the bounded exception with the largest
local variance. They motivate a fresh mechanism experiment but cannot
retroactively alter the pooled STOP.

## Next mathematical object

The next test should inject controlled within-cell geometry:

\[
Q_i(\tau)=s_\tau(\bar Q_c+\tau U_i),
\]

while fixing total residual information.

A normal perturbation along a known detector-margin direction tests whether
the detector can transmit deliberately planted individual heterogeneity. A
tangent perturbation orthogonal to registered scalar and broad geometry
coordinates tests whether hidden geometry can create conditional variation
without changing the cell label.

This separates:

1. no individual variation was planted;
2. variation was planted but the detector is insensitive;
3. only detector-margin distance matters;
4. hidden within-cell geometry creates reproducible individual structure.

No personality or psychological interpretation follows without later
real-text and external-construct evidence.
