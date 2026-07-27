# V8 V3.7H.4D-R2G.2 Hierarchical Society-Limit Frontier

Status: prospective protocol frozen before the numerical run.

R2G.1 varied authors inside one planted group. Its fixed term is therefore a
within-group floor, not a universal society floor. R2G.2 varies both the
number of groups \(G\) and the number of authors per group \(n\).

## Primary estimand

For two independent views of the same planted hierarchy:

\[
\bar R_{s,G,n}^{v}
=
\frac{1}{Gn}
\sum_{g=1}^{G}
\sum_{i=1}^{n}
R_{sgi}^{v},
\qquad
M_\times(G,n)
=
E\langle\bar R_{s,G,n}^{A},\bar R_{s,G,n}^{B}\rangle .
\]

Under nested conditional-expectation projections and independent groups and
authors:

\[
M_\times(G,n)
=
b_S+\frac{b_G}{G}+\frac{b_A}{Gn}.
\]

The components are Hilbert-space martingale differences:

\[
D_S=E[R\mid\mathcal F_S]-E[R\mid\mathcal F_0],
\]

\[
D_G=E[R\mid\mathcal F_G]-E[R\mid\mathcal F_S],
\]

\[
D_A=E[R\mid\mathcal F_A]-E[R\mid\mathcal F_G].
\]

This is projection orthogonality, not independence, causality, or a
psychological ontology.

## Dependent groups

Without independence, the exact finite-design identity is:

\[
M_\times(G,n)
=
\frac{1}{G^2n^2}
\sum_{g,h=1}^{G}
\sum_{i,j=1}^{n}
\Gamma_{AB}\{(g,i),(h,j)\}.
\]

For stationary AR(1) group structure:

\[
M_\times(G,n)
=
b_S+
\frac{b_G}{G^2}
\left[
G+2\sum_{h=1}^{G-1}(G-h)\rho^h
\right]
+\frac{b_A}{Gn}.
\]

A local-to-unity sequence \(\rho_G=1-c/G\) has a positive group limit:

\[
\lim_{G\rightarrow\infty}
\frac{1}{G^2}
\left[
G+2\sum_{h=1}^{G-1}(G-h)\rho_G^h
\right]
=
\frac{2(c-1+e^{-c})}{c^2}.
\]

It can imitate a society floor even when no society component exists.

## Registered worlds

1. `pure_iid`: view-private residual only.
2. `author_iid`: author term only.
3. `group_iid`: independent group and author terms.
4. `society_completable`: score-visible society term.
5. `group_ar1`: group correlation at \(\rho=.5\) and \(.9\).
6. `correlated_hierarchy`: raw levels share lower-level latents.
7. `unavailable_society_shock`: target-common term absent from score.
8. `local_to_unity`: dependent group process with no society term.
9. `correlated_view_noise`: shared technical noise observationally equivalent
   to a stable society term at second order.

Gaussian and standardized \(t_5\) private noise are both registered.
Private-view noise energy is fixed at `.25`, matching four independent target
opportunities in R2G/R2G.1.

## Controls

- Checkerboard cells in the \(G\times n\) surface are held out from fitting.
- Raw, admissible, structural-oracle, and omniscient-oracle residuals are
  separated.
- Per-society confirmation centering is recorded as a deliberate false-zero
  attack.
- Correlated raw hierarchy accounting is compared with its exact martingale
  projection.
- Root-level summaries use Bonferroni-adjusted t intervals. Nested \(G,n\)
  cells are not treated as independent samples.

## Decision boundary

`PASS_HIERARCHICAL_LIMIT_IDENTIFICATION` requires:

- null and oracle surfaces remain inside the practical-zero interval;
- independent author/group coefficients are recovered;
- score-visible and unavailable society terms separate;
- the AR covariance-sum model recovers registered \(\rho\);
- conditional projection removes planted cross-level covariance;
- local-to-unity dependence is not named a society factor;
- common technical noise is marked non-identifiable, not psychological.

Any result is a synthetic mathematical identification result only. It cannot
establish that real-text residuals are complete, that an observed component
is personality, or that society-level error is exactly zero.
