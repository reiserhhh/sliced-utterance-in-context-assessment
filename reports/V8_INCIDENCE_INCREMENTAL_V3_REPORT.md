# V8 Incremental Incidence V3 Report

Code-gate decision: `V8_INCIDENCE_INCREMENTAL_PLANTED_PASS`

Independent methodology audit: `PARTIAL`

Canonical run:
`results/v8_incidence_incremental/v3_final_20260726/`

## Question

Does persistent same-condition intersection contain information that is not
already present in ordinary whole-trajectory distance?

V2.3 could not answer this because fitted whole-map distance separated every
clear simulator perfectly. V3 constructs positive and counterfactual
populations whose whole-map distance geometry is algebraically identical,
then changes only their local incidence organization.

## Counterfactual construction

For each pair, local event paths \(L^+\) and \(L^-\) are completed by
orthogonal reservoir coordinates so that

\[
HF^+F^{+\mathsf T}H
=
HF^-F^{-\mathsf T}H
=
\gamma H.
\]

Consequently every oracle author-pair whole-map distance is equal and the
positive and counterfactual distance matrices are identical. View noise is
transported through an orthogonal Procrustes map, preserving distance
matching after observation noise.

The three counterfactuals isolate different aspects of incidence:

- CF1: same-condition six-author convergence versus the same anchor visited
  asynchronously;
- CF2: persistent six-author cores versus overlapping persistent triplets
  that form a transitive chain;
- CF3: persistent six-author membership versus multiplicity six whose
  members rotate at every condition.

## Exact estimator

At each condition, uncertainty radius, and independent view, V3 enumerates
all inclusion-maximal common-ball hyperedges. It uses a pair graph,
Bron-Kerbosch maximal cliques, exact minimum-enclosing-ball verification, and
Helly-witness recursion. Tests against exhaustive enumeration pass for random
2D sets with \(n=8,10,12\), random 3D sets, and an overlapping-hyperedge
counterexample that the old complete-link partition misses.

Persistent cores are scored by exact-member recurrence over the frozen
condition-radius grid. Selected cores must be inclusion-maximal, disjoint,
and present in all four views. V3 never takes a transitive closure over
overlapping cores.

The threshold 0.04 was fixed from the planted support separation before
confirmation:

\[
P_{\mathrm{fixed\ 6}}
\approx\frac6{65}\frac{18}{22}=0.0755,
\]

\[
P_{\mathrm{chain\ 3}}
\le\frac2{65}\frac{21}{22}=0.0294,
\qquad
P_{\mathrm{rotating\ 6}}
\le\frac1{65}\frac{18}{22}=0.0126.
\]

## Confirmation result

Each counterfactual pair had 200 untouched confirmation populations.

| Metric | CF1 | CF2 | CF3 |
| --- | ---: | ---: | ---: |
| Maximum fitted distance relative error | \(1.37\times10^{-15}\) | \(1.48\times10^{-15}\) | \(1.28\times10^{-15}\) |
| Whole-map AUC mean | 0.5041 | 0.5007 | 0.5036 |
| Whole-map AUC 90% CI | [0.5001, 0.5080] | [0.4972, 0.5043] | [0.4994, 0.5080] |
| Incidence AUC median | 1.000 | 1.000 | 1.000 |
| Incremental AUC median | 0.4927 | 0.5020 | 0.4977 |
| F1 / ARI median | 1.000 / 1.000 | 1.000 / 1.000 | 1.000 / 1.000 |
| Positive group claims | 200/200 | 200/200 | 200/200 |
| Counterfactual group claims | 0/200 | 0/200 | 0/200 |
| Cross-view core Jaccard median | 1.000 | 1.000 | 1.000 |
| Permutation AUC mean | 0.4926 | 0.4999 | 0.4988 |

The one-sided 95% upper bound for every 0/200 counterfactual claim rate is
0.01487. CF2 had 0/200 chaining errors. Global-anchor and reservoir-only
nulls also had 0/200 claims.

All confirmation, null, distance-equivalence, incremental-AUC,
cross-view, chaining, and label-permutation gates passed. Discovery and
confirmation seeds are disjoint. Ten inventoried artifacts verify, and the
full repository test suite passes 447 tests.

## What an intersection means after V3

The result rejects three simpler interpretations:

1. An intersection is not merely two paths visiting the same place; condition
   synchronization matters.
2. A chain of overlapping local relations is not one common author group.
3. High multiplicity is not sufficient; stable membership matters.

The information-bearing candidate is therefore a persistent conditional
incidence core:

\[
\mathcal C
=
\left(
H,\;
\text{same condition},\;
\text{scale recurrence},\;
\text{view replication},\;
\text{membership persistence}
\right).
\]

In the registered simulator, this object retains planted co-membership after
all information available to integrated whole-map Euclidean distance has
been neutralized. This establishes a distinct conditional-geometric signal,
not a personality signal.

If a corresponding structure survives in human text, it could represent
authors who instantiate a similar response mechanism under comparable
conditions. Calling it personality similarity would additionally require
cross-text stability and external psychological or behavioral validation.

## Approximation result

The old complete-link estimator had median precision approximately 0.990 and
median recall approximately 0.969 in the positive worlds. It is useful as a
fast proposal mechanism but not mathematically exact. V3 decisions use only
the exact estimator.

## Limits

- Gram compensation and paired orthogonal noise deliberately construct an
  ideal distance-matched counterfactual. This proves mathematical
  non-equivalence to integrated distance, not natural prevalence.
- The planted local convergence is strong and sharply separated from noise.
  Softer graded convergence has not been tested.
- The design fixes 24 authors, four balanced groups of six, 65 scalar
  conditions, two dimensions, and noise SD 0.01.
- Whole-map Euclidean distance is only one competing path model. Dynamic
  time warping, conditional kernels, operator distance, and learned sequence
  baselines remain untested.
- The two null worlds mostly fail closed through core ambiguity; independent
  calibration of useful real-text refusal rates is open.
- Exact enumeration is bounded by a node cap and has not been scaled beyond
  this registered design.
- The configuration was frozen before the V3 confirmation run, but the
  worktree is dirty and untracked. This is an internal frozen confirmation,
  not an immutable third-party-verifiable preregistration.
- No real text, external psychological labels, behavioral outcomes, or
  clinical criteria were used.

## Subsequent correction

V3.1 closed the two estimator gaps through threshold-complete persistent
subset search and same-cell cross-view support. Its full confirmation and
independent audit passed at the technical planted-world tier. See
`reports/V8_INCIDENCE_INCREMENTAL_V31_REPORT.md`.
