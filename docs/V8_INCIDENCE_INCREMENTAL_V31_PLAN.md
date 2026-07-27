# V8 Incremental Incidence V3.1 Plan

Status: `FROZEN_BEFORE_CONFIRMATION`

## 1. Purpose

V3.1 preserves the V3 distance-matched counterfactual design and closes two
estimator gaps identified by independent audit:

1. a persistent subset may be hidden inside different maximal hyperedges;
2. recurrence in separate views must occur at the same condition and radius,
   not merely somewhere in each view.

The estimand remains

\[
I(Y;\text{condition-local persistent structure}
\mid D_{\text{whole-map}})>0.
\]

This is a planted geometric estimand, not a personality estimand.

## 2. Condition-aligned support

For candidate author subset \(A\), view \(v\), condition \(z\), and radius
\(\epsilon\), define

\[
q_v(A;z,\epsilon)
=
\max_{\substack{G\in\mathcal H^{\max}_{v,z,\epsilon}\\A\subseteq G}}
\frac{n-|G|}{n-2},
\]

with zero support when no containing hyperedge exists. Joint support is

\[
q_\cap(A;z,\epsilon)=\min_v q_v(A;z,\epsilon),
\]

and persistence is

\[
P_\cap(A)
=
\frac1{|Z||E|}
\sum_{z,\epsilon}q_\cap(A;z,\epsilon).
\]

The minimum is taken before averaging. Therefore a core at condition \(z_1\)
in one view and only at \(z_2\) in another view receives no joint support.

## 3. Threshold-complete subset search

Directly materializing the full intersection lattice can grow exponentially
under null geometry. V3.1 instead performs an Apriori search from all
three-author subsets.

For \(A\subseteq B\),

\[
q_v(B;z,\epsilon)\le q_v(A;z,\epsilon)
\quad\Longrightarrow\quad
P_\cap(B)\le P_\cap(A).
\]

The support is therefore anti-monotone. A set of size \(k+1\) can pass the
frozen threshold only if every size-\(k\) subset passes. V3.1:

1. evaluates every triple;
2. retains triples with \(P_\cap\ge0.04\);
3. joins retained \(k\)-sets only when every \(k\)-subset of the proposed
   \((k+1)\)-set retained;
4. evaluates the proposal and repeats;
5. refuses if evaluated candidates exceed 5,000.

This is complete for every threshold-passing subset while avoiding the full
zero-support intersection lattice.

## 4. Registered controls

The V3 counterfactuals remain unchanged:

- CF1: synchronous six-author convergence versus asynchronous visits;
- CF2: fixed six-author cores versus overlapping triplet chains;
- CF3: persistent membership versus rotating membership.

The two null worlds remain global common anchor and reservoir-only geometry.
Three simpler condition-local statistics are reported:

- minimum same-condition distance;
- soft same-condition kernel;
- mutual five-nearest-neighbor recurrence.

They test whether local information is already available without exact
hyperedges. V3.1 does not preregister a uniqueness claim for the hypergraph
representation.

## 5. Frozen design and gates

- 24 authors in four anonymous groups of six;
- 65 conditions, four independent views, two response dimensions;
- epsilon grid 2.0, 3.0, 4.0;
- persistence threshold 0.04;
- exact enumeration node cap 25,000;
- thresholded candidate cap 5,000;
- 40 discovery and 200 confirmation populations per world;
- all V3 distance-equivalence, recovery, false-claim, chaining,
  cross-view, and permutation gates retained unchanged.

The only allowed PASS statement is:

> In the registered low-noise simulator, condition-aligned persistent subset
> cores retain planted co-membership after integrated whole-map Euclidean
> distance is neutralized.

PASS does not establish that the exact hypergraph is uniquely necessary, that
the same object exists in real text, or that any recovered core is personality
similarity, compatibility, a psychological type, or a clinical relation.
