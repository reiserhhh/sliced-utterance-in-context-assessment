# V8 Scale, Null, Transversality, and Manifold V3.5 Plan

Status: `FROZEN_BEFORE_CONFIRMATION`

## 1. Purpose

V3.5 closes four technical gaps left by V2.3-V3.4:

1. replace finite-radius hit counts with exact common-ball birth scale;
2. place a condition-restricted random-author baseline inside the estimator;
3. estimate tangent versus transverse contact from local jets;
4. test two-dimensional nonlinear response sheets.

No psychological labels or real text enter this battery.

## 2. Exact scale statistic

For candidate author set \(H\), condition \(z\), and view \(v\),

\[
b_{H,z,v}
=
\rho_{\mathrm{MEB}}(X_{H,z,v}),
\qquad
b^\cap_{H,z}=\max_v b_{H,z,v}.
\]

On the registered radius interval \([r_0,r_1]=[1.00,1.06]\),

\[
S_{H,z}
=
\frac{[r_1-\max(r_0,b^\cap_{H,z})]_+}{r_1-r_0},
\]

\[
P_H
=
\frac{n-|H|}{n-2}
\frac1{|Z|}
\sum_z S_{H,z}.
\]

This is the normalized survival length after the exact Cech-simplex birth.
Because feasibility is monotone in radius, it is not described as a
birth-death barcode.

## 3. Condition-restricted max-T null

The paired null independently permutes author identities inside each
condition while preserving every condition's point multiset, edge
multiplicity, scale, view noise, and opportunity count.

For each of 999 restricted permutations the complete candidate search is
rerun and its maximum \(P_H\) retained. The familywise p-value is

\[
p_{\mathrm{FWER}}
=
\frac{1+\sum_b
\mathbf 1[P_{\max}^{(b)}\ge P_{\max}^{\mathrm{obs}}]}
{1000}.
\]

A group claim requires the frozen persistence threshold, nonoverlap,
population coverage, and \(p_{\mathrm{FWER}}\le.01\).

## 4. Local geometry

For response map \(f_u:\mathcal Z\to\mathbb R^d\), fit a local quadratic jet
without using relation labels. For a pair,

\[
Dg=J_u-J_v.
\]

For a regular same-condition intersection,

\[
\dim I=\dim\mathcal Z-\operatorname{rank}(Dg).
\]

A singular value above the frozen rank threshold is transverse. First-order
rank deficiency with a stable normal Hessian difference is tangent.
Near-threshold singular values are refused.

The curve battery includes transverse, tangent, coincident, near-miss, and
rank-boundary worlds. The sheet battery uses a \(13\times13\) two-dimensional
condition grid and includes paraboloid, sinusoidal, and RBF sheets,
transverse intersection curves, tangent contact, coincidence, near misses,
correlated noise, and a common condition reparameterization.

## 5. Frozen sizes and gates

- discovery: 80 populations per world;
- confirmation: 200 populations per world;
- restricted permutations: 999 per scale population;
- exact birth error at most \(10^{-5}\) on noiseless registered geometry;
- continuous versus 9/17/33-point decision agreement at least 0.99;
- positive claim one-sided 95% lower at least 0.90;
- matched-null claim one-sided 95% upper at most 0.03;
- matching standardized mean difference at most 0.05;
- curve/surface relation accuracy at least 0.90;
- regular intersection-dimension MAE at most 0.25;
- held-out nonlinear transversality AUC at least 0.85;
- geometry-boundary refusal one-sided 95% lower at least 0.90.

Any label use in estimation, condition-matching failure, cap failure, or
post-confirmation threshold change stops the claim.

## 6. Claim boundary

A PASS validates only the registered synthetic estimators. It does not make
an intersection a personality signal, thought node, intelligence mechanism,
or clinically meaningful relation.
