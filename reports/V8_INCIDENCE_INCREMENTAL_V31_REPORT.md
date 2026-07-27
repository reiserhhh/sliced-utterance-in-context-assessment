# V8 Incremental Incidence V3.1 Report

Code-gate decision: `V8_INCIDENCE_INCREMENTAL_PLANTED_PASS`

Independent methodology audit: `PASS_TECHNICAL_PLANTED_ONLY`

Canonical run:
`results/v8_incidence_incremental/v31_final_20260726/`

## Question

Can V3 recover a stable author subset when it is hidden inside different
maximal hyperedges, while requiring its recurrence to occur at the same
condition and radius in every independent view?

V3.1 also asks whether exact hyperedges are uniquely responsible for the
local signal by reporting three simpler condition-local baselines.

## Estimator correction

For candidate author subset \(A\), the view-specific support at one
condition-radius cell is

\[
q_v(A;z,\epsilon)
=
\max_{\substack{G\in\mathcal H^{\max}_{v,z,\epsilon}\\A\subseteq G}}
\frac{n-|G|}{n-2}.
\]

V3.1 aligns the views before aggregation:

\[
P_\cap(A)
=
\frac1{|Z||E|}
\sum_{z,\epsilon}\min_v q_v(A;z,\epsilon).
\]

Thus support at condition \(z_1\) in one view and only at \(z_2\) in another
does not count as replicated support.

Candidate discovery uses threshold-complete Apriori expansion from all
triples. If \(A\subseteq B\), every maximal hyperedge containing \(B\) also
contains \(A\), so

\[
P_\cap(B)\le P_\cap(A).
\]

Every subset that can pass the frozen threshold 0.04 is therefore generated;
the zero-support intersection lattice need not be materialized. The search
refuses above 5,000 evaluated candidates.

Direct tests cover:

- a stable triple hidden in different four-author maximal edges;
- a triple appearing at different conditions in separate views;
- the CF2 overlap-chain counterfactual.

## Confirmation result

Each counterfactual pair had 200 untouched confirmation populations.

| Metric | CF1 | CF2 | CF3 |
| --- | ---: | ---: | ---: |
| Maximum fitted distance relative error | \(1.37\times10^{-15}\) | \(1.48\times10^{-15}\) | \(1.34\times10^{-15}\) |
| Whole-map AUC mean | 0.5041 | 0.5009 | 0.5034 |
| Whole-map AUC 90% CI | [0.5003, 0.5082] | [0.4973, 0.5046] | [0.4992, 0.5078] |
| Incidence AUC median | 1.000 | 1.000 | 1.000 |
| Incremental AUC median | 0.4927 | 0.5019 | 0.4977 |
| F1 / ARI median | 1.000 / 1.000 | 1.000 / 1.000 | 1.000 / 1.000 |
| Positive group claims | 200/200 | 200/200 | 200/200 |
| Counterfactual group claims | 0/200 | 0/200 | 0/200 |
| Cross-view core Jaccard median | 1.000 | 1.000 | 1.000 |
| Permutation AUC mean | 0.4921 | 0.4999 | 0.4991 |

Every positive, distance-equivalence, incremental-AUC, cross-view,
counterfactual, chaining, null, and permutation gate passed. The one-sided
95% upper bound for each 0/200 false group-claim rate is 0.01487.

Global-anchor and reservoir-only nulls had 0/200 group claims. Their refusal
rates were 2.5% and 20.0%, respectively, compared with 94.0% and 99.5% in
V3. The corrected candidate search therefore reduced fail-closed behavior
without introducing false group claims. The rotating-membership CF3
counterfactual still refused all populations rather than issuing a negative
group estimate.

Positive worlds evaluated exactly 2,112 threshold-search candidates. Negative
worlds evaluated 2,024-2,027. No exact-enumeration or candidate-cap refusal
occurred in the 1,000 confirmation populations.

Discovery and confirmation seeds are disjoint. Eleven inventoried artifacts
verify. The run manifest records all code, configuration, environment, and
hashes.

## Simpler local baselines

| Positive-world median AUC | CF1 | CF2 | CF3 |
| --- | ---: | ---: | ---: |
| Minimum same-condition distance | 1.000 | 1.000 | 1.000 |
| Soft local kernel | 1.000 | 1.000 | 1.000 |
| Mutual 5-neighbor recurrence | 0.803 | 0.813 | 0.808 |

V3.1 therefore does not establish that exact hyperedges uniquely extract the
local information. The supported distinction is:

- condition-local observations contain information that integrated whole-map
  Euclidean distance loses;
- a persistent no-chaining hypergraph can express a simultaneous multi-author
  core and refuse a transitive merge;
- ordinary local pairwise scores can be equally discriminative in the current
  strongly separated positive worlds.

In the CF2 chain counterfactual, incidence and the soft local baseline both
retain pairwise AUC near 0.80, but the hypergraph estimator makes no six-author
group claim. This suggests a set-level safety value, not a pairwise prediction
advantage. Because each planted triplet in CF2 remains below the persistence
threshold, this is not yet the strongest possible no-chaining attack.

## What an intersection means

The relevant object is not one exact coordinate and not the raw number of
paths passing through it. At a declared condition and tolerance, it is a set
of authors whose response points share a common uncertainty ball. Its
information comes from:

1. membership identity;
2. same-condition alignment;
3. recurrence across conditions and scales;
4. replication across independent views;
5. specificity relative to the reference population;
6. non-overlapping population coverage.

A global common anchor can connect all 24 paths and contain no group-specific
information. Hence raw multiplicity is not monotone evidence of similarity.

The strict current interpretation is a **shared conditional response
mechanism candidate**. It can become evidence of psychological similarity
only after comparable structures survive opportunity controls in human text,
replicate across text samples, and relate to external psychological or
behavioral criteria.

## Independent audit

The audit reproduced the summaries, hashes, first confirmation seeds, and
confidence bounds. It also compared the Apriori result with full subset
enumeration on 250 random weighted multiview grids; every threshold-passing
set and score matched.

The audit accepts mathematical completeness of the thresholded search and
closure of both V3 estimator gaps. It does not accept hypergraph uniqueness,
real-text existence, personality meaning, compatibility, psychological
types, or clinical use.

## Limits

- The planted convergence remains strongly separated from outsiders.
- The Gram-reservoir construction is an ideal algebraic counterfactual.
- Simple local distances solve the current positive discrimination task.
- CF2 does not make every overlapping triplet independently pass threshold.
- The design fixes 24 authors, balanced six-author groups, two dimensions,
  low noise, and a known finite condition grid.
- The rotating counterfactual remains fail-closed.
- No real text or external psychological/behavioral labels are used.
- The manifest records `dirty=true`; this is reproducible internal evidence,
  not an immutable Git-sealed preregistration.

## Next gate

The next registered test is a strong-chain counterfactual:

1. every overlapping triplet must independently exceed persistence 0.04;
2. no six-author set may share a common ball at any condition;
3. simple local scores must be passed to frozen single-link, complete-link,
   and spectral clustering baselines;
4. false six-core rate, F1/ARI, refusal, and pairwise AUC must be compared
   directly with the unchanged hypergraph estimator.

Only that test can establish whether no-chaining supplies an independent
population-structure advantage over ordinary local graph methods.
