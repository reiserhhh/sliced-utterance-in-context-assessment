# V8 V3.7H.4D R2F Local Response Operator

Status: prospective synthetic discovery. No R2F geometry or outcome has
been inspected at registration.

## Objective

R2E.2 confirmed a large detector response along one known halo-normal
direction and practical null response along one registered tangent family.
R2F tests a broader local chart. It estimates which constrained geometry
directions alter the frozen detector at first order, only through curvature,
or approximately not at all.

For parent \(i\):

\[
p_i(Q)=P\{D_i(Q)=1\mid Q,\psi_i\}.
\]

The target is the local response of \(p_i\), not a psychological factor.

## Ambient and constrained spaces

The double-centered test-author geometry has dimension:

\[
(64-1)(16-1)6=5670.
\]

At:

\[
Q_{i0}=\cos\theta C_i+\sin\theta H_i,
\qquad
\theta=\arcsin\sqrt{.01},
\]

24 shared-seed orthonormal probes are projected away from \(C_i,H_i\).

Nine nonconstant R2B macro coordinates define a standardized numerical
Jacobian at epsilon `.01`. Coordinate scales are frozen sample standard
deviations of the 160 R2E.2 baseline geometries. Total information is
matched exactly and sign coherence is constant, so neither enters the
Jacobian.

The deterministic coefficient projector is:

\[
P_i=I-J_i^+J_i.
\]

The first four usable projected canonical probe vectors are orthogonalized
to create \(U_{i1},\ldots,U_{i4}\). Probe seeds define corresponding local
axes across parents without requiring ambient coordinate equality.

Hard geometry gates require:

\[
\|J_iU_i\|_{\mathrm{op}}\le10^{-6},
\]

and finite-step standardized macro drift at most `.05` for every axis,
corner, and registered-null geometry.

## Geodesic chart

For coefficient vector \(x\in\mathbb R^4\):

\[
Q_i(x)=
\cos\theta C_i+
\sin\theta
\left[
\cos\|x\|H_i+
\sin\|x\|
\frac{U_ix}{\|x\|}
\right].
\]

This preserves unit norm and halo share `.01`. Existing information matching
then restores parent-specific scalar residual information exactly.

## Frozen discovery

- 40 fresh parents per noise family;
- Gaussian and heteroskedastic \(t_5\);
- 32 independent detector outcomes per geometry;
- frozen 99-sign CRC/low-rank/HC/Holm detector;
- common random numbers across all geometries in a parent replicate;
- 20,000 stratified parent-block bootstrap draws.

Each parent has 45 geometries:

- one baseline;
- each of four axes at `+/- .10` and `+/- .20`: 16;
- six axis pairs at four `(+/- .10, +/- .10)` corners: 24;
- normal `.09 +/-`: two;
- R2E.2-style registered-null tangent `.4 +/-`: two.

Total formal detector outcomes:

\[
2\cdot40\cdot45\cdot32=115{,}200.
\]

Formal outcomes are prohibited until the geometry-only preflight passes.
The formal run must reproduce every preflight basis and interaction hash.

## Derivatives and sampling-noise correction

The 32 outcomes are frozen into A/B halves of 16. Gradient and Hessian are
estimated independently in each half with symmetric finite differences and
Richardson correction on the axes.

The cross-fitted operators are:

\[
\widehat{\mathcal A}_g=
\frac1{2n}\sum_i
\left(g_i^Ag_i^{B\top}+g_i^Bg_i^{A\top}\right),
\]

\[
\widehat{\mathcal A}_H=
\frac1{2n}\sum_i
\left(H_i^{A\top}H_i^B+H_i^{B\top}H_i^A\right).
\]

Conditional independence of A/B removes additive Bernoulli measurement
variance in expectation. Negative eigenvalues are retained.

The leading first-order strength is:

\[
S_g=(.2)^2\gamma_1.
\]

For the leading curvature direction \(w_1\):

\[
S_H=
\frac{(.2)^4}{4}
E[(w_1^\top H_i^Aw_1)(w_1^\top H_i^Bw_1)].
\]

Quadratic adequacy fits each axis at `0,+/- .10` and predicts `+/- .20`.
Its latent mean squared error is estimated by the A/B residual cross-product.

## Discovery gates

All integrity, manifest, inventory, preflight-hash, normal-control, and
registered-null checks must pass.

A `G1` or `H1` discovery candidate requires:

- point strength above `.005`;
- bootstrap lower bound above zero;
- bootstrap 90% principal-angle upper at most 45 degrees;
- quadratic-adequacy upper MSE at most `.0004`;
- a deterministic sign and coefficient hash.

Candidates within 30 degrees are merged. At most two candidates can be
frozen. No unselected direction may be promoted later.

If no candidate passes, the protocol stops rather than increasing chart
dimension, rotating probes, changing step size, or reusing the same outcomes.
Any candidate requires 80 entirely fresh parents per noise family before a
scientific confirmation claim.

## Interpretation boundary

R2F may support a local detector decomposition into normal response,
first-order tangent response, curvature-only response, and approximate
kernel. It cannot establish:

- that four axes span the 5,670-dimensional tangent space;
- that a local kernel is global;
- that a candidate exists in real text;
- that any direction is personality, cognition, intelligence, diagnosis, or
  a clinical construct.

The plan and source hashes provide a local prospective freeze. Because the
worktree is not committed or externally timestamped, this is not claimed as
third-party preregistration.
