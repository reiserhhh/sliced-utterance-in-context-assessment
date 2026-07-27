# H4D-R2 Independent Theory Audit

Date: 2026-07-27

Ruling:
`GO_IID_M8_CONFIRMATION / STOP_CROSS_GEOMETRY_SCALAR_THRESHOLD`

## Accepted

1. Random support must retain \(M_T=0\); favorable re-drawing would bias
   power upward.
2. Sparse \(Q\) remains exactly zero outside its intended block. Only the
   registered detector projection may create a halo.
3. The weighted additive projection used for residual information is
   equivalent to \(q_R'(PDP)^+q_R\) under the registered diagonal
   pre-projection covariance and complete Euclidean centering.
4. The fixed iid discovery legitimately selected \(m=8\).
5. Fresh R2A confirmation passed within that exact family.

## Refutation

Scalar residual information is not sufficient across geometry. The
intrinsic-zero-sum counterexample had at least as much \(\mathcal I_R\) but
far lower detector power.

The likely mechanism is author-level sign randomization. With very few
energy-carrying authors, the sign orbit is coarse; for \(m=4\), the scale
\(2^{-m}=.0625\) is already unfavorable under three-channel Holm correction.
The small iid centering halo distributes energy to additional author rows and
changes the effective randomization geometry.

## Required operator

Let \(W=(\Sigma^R)^{-1/2}Q_R\). The next model must retain at least:

\[
\mathfrak I(Q)=
\left(
\lVert W\rVert_F^2,\,
n_{\mathrm{eff}}^A,\,
s_{\mathrm{eff}}^{cell},\,
\rho_3,\,
L_R
\right),
\]

where:

\[
n_{\mathrm{eff}}^A
=
\frac{(\sum_u e_u)^2}{\sum_u e_u^2},
\qquad
e_u=\lVert W_{u\cdot}\rVert^2,
\]

\[
s_{\mathrm{eff}}^{cell}
=
\frac{(\sum_{uc}e_{uc})^2}{\sum_{uc}e_{uc}^2},
\]

\[
\rho_3
=
\frac{\sum_{k=1}^{3}\sigma_k(W)^2}
{\sum_k\sigma_k(W)^2}.
\]

The richer object is the author Gram operator \(G_A=WW^\top\), including its
spectrum, diagonal leverage, and maximum author-energy share.

## Boundary

R2A confirms an iid operational boundary only. R2B must test whether a
geometry-aware operator predicts held-out detector power across unseen
interaction families without changing the detector.

