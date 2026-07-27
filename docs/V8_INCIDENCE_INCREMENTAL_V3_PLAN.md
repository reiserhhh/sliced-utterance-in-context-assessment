# V8 Incremental Incidence V3 Plan

Status: `FROZEN_BEFORE_CONFIRMATION`

## 1. Estimand

V3 tests only

\[
I(Y;\text{local persistent incidence}\mid D_{\text{whole-map}})>0.
\]

It does not test personality, compatibility, psychological types, clinical
meaning, or real-text validity.

## 2. Distance-matched counterfactuals

For each repetition, a positive and counterfactual path population share the
same authors and anonymous labels. Local event coordinates are constructed
first. If \(L^\pm\) are the centered local path matrices, choose

\[
\gamma>\max\{\lambda_{\max}(L^+L^{+\mathsf T}),
\lambda_{\max}(L^-L^{-\mathsf T})\}
\]

and add reservoir coordinates satisfying

\[
R^\pm R^{\pm\mathsf T}
=
\gamma H-L^\pm L^{\pm\mathsf T},
\qquad
H=I-\frac1n\mathbf1\mathbf1^\mathsf T.
\]

The complete flattened paths \(F^\pm=L^\pm\oplus R^\pm\) then obey

\[
HF^+F^{+\mathsf T}H
=
HF^-F^{-\mathsf T}H
=
\gamma H.
\]

Every oracle whole-map author distance is therefore identical in the
positive and counterfactual populations and non-discriminative for the
anonymous labels. View noise is paired by an orthogonal Procrustes map, so
the fitted positive and counterfactual distance matrices also match.

| Pair | Positive | Counterfactual |
| --- | --- | --- |
| CF1 | fixed six-author groups converge under the same condition | the same authors visit the same anchor at different conditions |
| CF2 | fixed six-author common-ball cores | overlapping three-author cores form a cross-condition chain but never a six-author core |
| CF3 | fixed six-author sets recur | each condition has multiplicity six but membership rotates |

## 3. Exact hyperedges

At each condition \(z\), radius \(\epsilon r(z)\), and independent view,
V3 enumerates all inclusion-maximal sets

\[
\mathcal H^{\max}_{z,\epsilon}
=
\max_{\subseteq}
\left\{
H:
|H|\ge3,\;
R_{\mathrm{MEB}}(X_H(z))
\le\epsilon r(z)
\right\}.
\]

The algorithm:

1. builds the pair graph at distance \(2\epsilon r(z)\);
2. enumerates maximal cliques by Bron-Kerbosch;
3. verifies each clique by its minimum enclosing ball;
4. when infeasible, finds a Helly witness of size at most \(d+1\) and
   recursively removes witness members;
5. removes duplicate and nonmaximal feasible sets.

Small \(n\) results must match exhaustive subset enumeration exactly.
Node-cap exhaustion refuses output.

## 4. Persistent cores without chaining

For candidate set \(H\), V3 records finite-grid recurrence:

\[
P_H^{(v)}
=
\frac1{|Z||E|}
\sum_{z,\epsilon}
\max_{G\supseteq H}
\frac{n-|G|}{n-2}
\mathbf1\{G\in\mathcal H^{\max}_{z,\epsilon,v}\}.
\]

The cross-view score is

\[
P_H=\min_v P_H^{(v)}.
\]

Selected cores must be inclusion-maximal, mutually disjoint, independently
present in all views, and individually persistent. V3 never unions
overlapping hyperedges across conditions. Any overlap among selected closed
cores returns `REFUSE_CORE_AMBIGUITY`.

## 5. Frozen design and gates

- authors: 24;
- anonymous groups: four balanced groups of six;
- conditions: 65;
- views: four (two halves by two observers);
- ambient response dimension: two;
- event conditions: 24;
- epsilon grid: 2.0, 3.0, 4.0;
- fixed core-persistence threshold: 0.04;
- nominal view-noise SD: 0.01.

Confirmation gates:

- oracle positive/counterfactual distance relative error at most \(10^{-10}\);
- fitted positive/counterfactual distance relative error at most 0.02;
- whole-map AUC bootstrap 90% interval contained in [0.45, 0.55];
- each positive incidence AUC at least 0.85;
- each positive \(\Delta\)AUC over whole-map distance at least 0.30;
- each positive median F1 at least 0.80 and median ARI at least 0.70;
- minimum positive group-claim rate at least 0.90;
- minimum cross-view core Jaccard at least 0.80;
- every counterfactual false group-claim rate at most 0.03;
- CF2 chaining error rate at most 0.03;
- label-permutation incidence AUC bootstrap 90% interval in [0.45, 0.55].

Metrics aggregate by simulated population. Author pairs are not treated as
independent observations.

## 6. Stop rules

- distance mismatch: `REFUSE_DISTANCE_NOT_MATCHED`;
- exact enumeration disagrees with exhaustive small-n truth:
  `STOP_IMPLEMENTATION`;
- node cap: `REFUSE_ENUMERATION_CAP`;
- any counterfactual or chaining gate failure: `STOP_FALSE_STRUCTURE`;
- incidence fails to improve over whole-map distance:
  `STOP_NO_INCREMENTAL_INFORMATION`;
- view-specific cores do not replicate:
  `STOP_AGGREGATION_ARTIFACT`.

The only allowed PASS statement is that exact, same-condition,
cross-scale, cross-view persistent incidence adds planted co-membership
information after whole-map integrated distance has been neutralized in the
registered simulator. A PASS is not a personality claim.
