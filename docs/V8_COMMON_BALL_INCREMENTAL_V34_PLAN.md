# V8 Common-Ball Incremental V3.4 Plan

Status: `FROZEN_BEFORE_CONFIRMATION`

## 1. Estimand

V3.4 tests

\[
I(Y;\text{common-ball feasibility}\mid A_{ijz\epsilon v})>0,
\]

where the complete author-pair, condition, radius, and observer-view
adjacency tensor \(A_{ijz\epsilon v}\) is held identical between paired
worlds. The view-intersected tensor \(A_{ijz\epsilon}\) must therefore also
be identical.

It does not test information beyond complete continuous Euclidean distances:
a full distance matrix already determines minimum-enclosing-ball geometry.

## 2. Registered geometry

Use fixed uncertainty radius \(R=1\) and
\(\epsilon\in\{1.00,1.03,1.06\}\).

In each active group-condition:

- `MEB+`: six points lie on a circle of radius \(0.90R\);
- `MEB-`: two points occupy each vertex of an equilateral triangle whose
  circumradius is \(1.10R\).

For `MEB-`, the maximum pair distance is

\[
\sqrt3(1.10R)=1.905R<2R.
\]

Thus every within-group pair is adjacent at every registered epsilon in both
worlds, but

\[
\rho_{\mathrm{MEB+}}=0.90R\le R,
\qquad
\rho_{\mathrm{MEB-}}=1.10R>1.06R.
\]

Four active conditions give

\[
P_6
=
\frac4{65}\frac{18}{22}
=0.0503>0.04.
\]

All nonactive author pairs remain beyond the largest pair threshold. Four
small independent observer perturbations are paired across worlds and must
preserve exact tensor equality. Any tensor mismatch stops the paired claim.

## 3. Frozen methods

- Exact MEB maximal hyperedges;
- same-condition, same-radius cross-view support;
- V3.1 threshold-complete subset search;
- persistence threshold 0.04;
- overlap ambiguity refusal;
- fixed geometric margin refusal when a candidate MEB lies within \(0.02R\)
  of a registered radius boundary.

The three V3.3 pairwise comparators receive only the identical tensor. Their
paired outputs must be exactly equal.

## 4. Confirmation and controls

- main fresh confirmation pairs: 500;
- both-feasible control: 200;
- both-infeasible control: 200;
- near-boundary refusal: 200;
- intentional adjacency mismatch: 200;
- rigid transformation, author permutation, and label-blindness are unit
  invariance tests.

Primary gates:

- exact per-view and view-intersected tensor mismatch: 0/500;
- pairwise comparator output mismatch: 0/500;
- `MEB+` six-core claim lower 95% at least 0.90;
- `MEB-` six-core claim upper 95% at most 0.03;
- paired decision delta bootstrap 95% lower at least 0.75;
- both-feasible agreement lower 95% at least 0.90;
- both-infeasible agreement lower 95% at least 0.90;
- boundary refusal lower 95% at least 0.90;
- intentional mismatch stop lower 95% at least 0.90;
- cap failure rate zero.

## 5. Claim boundary

The only allowed PASS statement is:

> In the registered finite-margin two-dimensional simulator, complete
> thresholded pairwise adjacency does not determine whether a multi-author
> set lies in one common ball; exact MEB geometry retains that higher-order
> feasibility information.

PASS does not establish information beyond complete continuous pairwise
distance geometry, real-text existence, personality similarity,
compatibility, psychological types, or clinical meaning.
