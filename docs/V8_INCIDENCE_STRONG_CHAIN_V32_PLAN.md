# V8 Incidence Strong-Chain V3.2 Plan

Status: `FROZEN_BEFORE_CONFIRMATION`

## 1. Estimand

V3.2 tests whether the frozen V3.1 no-chaining hypergraph has a set-level
decision advantage over aggregated pairwise local graphs when both observe
the same pair recurrence:

\[
\Delta_m
=
P(C_m=1\mid W_{\mathrm{chain}})
-
P(C_H=1\mid W_{\mathrm{chain}}),
\]

where \(C=1\) is a six-author group claim, \(m\) is a graph method, and \(H\)
is the frozen V3.1 estimator.

It does not test personality, compatibility, real-text prevalence, or
clinical meaning.

## 2. Matched strong-chain construction

Each anonymous group has six authors. The strong-chain world uses the
balanced triplet design

\[
\mathcal B
=
\{012,013,024,035,045,125,134,145,234,235\}.
\]

Every author belongs to five blocks and every author pair belongs to exactly
two blocks.

### Core-six world

- ten conditions: all six authors enter one common ball;
- fifteen conditions: each author makes a separate private excursion;
- twenty-five conditions: baseline response;
- fifteen coordinates: Gram reservoir.

Each author has 25 active response opportunities.
The discovery-registered geometry uses anchor scale 1.75 and private
excursion radius 0.90. These were selected from the declared grid because all
80 discovery populations passed the pair-distribution matching gates; no
psychological or confirmation label informed the choice.

### Strong-chain world

- each triplet in \(\mathcal B\) enters a common ball for five conditions;
- the other three authors remain separated;
- fifteen coordinates: Gram reservoir.

Each author again has 25 active opportunities. Every same-group author pair
is jointly near for \(2\times5=10\) conditions, exactly matching core-six.
No condition contains a six-author common ball.

Theoretical persistence is

\[
P_3
=
\frac5{65}\frac{21}{22}
=0.0734>0.04,
\qquad
P_6
=
\frac{10}{65}\frac{18}{22}
=0.1259.
\]

Gram-reservoir completion and paired Procrustes noise preserve the V3.1
whole-map distance counterfactual.

## 3. Frozen pairwise graph

All graph methods receive only

\[
W_{ij}
=
\frac1{|Z||E|}
\sum_{z,\epsilon}
\min_v
\mathbf1\{
\|x^{(v)}_{i,z}-x^{(v)}_{j,z}\|
\le2\epsilon r_z
\}.
\]

They cannot access condition identity after aggregation.

Registered methods:

- single-link connected components at \(W_{ij}\ge0.04\);
- complete-link clustering at distance \(1-W_{ij}\le0.96\);
- normalized-Laplacian spectral clustering with \(K\in[2,8]\) selected by
  maximum eigengap, deterministic `cluster_qr`, minimum eigengap 0.05, and
  silhouette 0.10.

No method may be given the true number of groups.

## 4. Frozen hypergraph

The V3.1 estimator is unchanged:

- exact maximal common-ball hyperedges;
- same-cell cross-view support;
- threshold-complete Apriori search;
- persistence threshold 0.04;
- inclusion-maximal cores;
- overlapping persistent cores produce `REFUSE_CORE_AMBIGUITY`;
- no transitive closure.

## 5. Matching gates

- exact designed pair recurrence difference at most \(10^{-12}\);
- observed pair-matrix MAE at most 0.02;
- observed pair-matrix correlation at least 0.95;
- absolute core/chain pairwise AUC difference at most 0.03;
- normalized pair-condition Wasserstein-1 at most 0.05;
- degree-strength relative error at most 0.05;
- normalized-Laplacian spectrum relative error at most 0.05;
- V3.1 oracle and fitted whole-map distance matching retained.

Any failed matching gate stops interpretation.

## 6. Runs and gates

- discovery: 80 paired populations;
- confirmation: 500 untouched paired populations;
- attacks/nulls: 500 each for asynchronous, rotating-membership,
  global-anchor, and reservoir-only;
- all uncertainty is aggregated by simulated population.

Primary gates:

- core-six hypergraph claim lower 95% bound at least 0.90;
- core-six median F1 and ARI at least 0.90;
- every registered chain triplet passes threshold in at least 90% of
  populations by lower 95% bound;
- chain hypergraph six-group claim upper 95% bound at most 0.03;
- chain ambiguity-refusal lower 95% bound at least 0.90;
- every graph method recovers core-six and falsely recovers strong-chain at
  rates whose lower 95% bounds are at least 0.90;
- paired graph-minus-hypergraph false-claim difference lower bootstrap 95%
  bound at least 0.75;
- each attack/null false claim upper 95% bound at most 0.03;
- no exact-enumeration or candidate-cap refusal.

## 7. Claim boundary

The only allowed PASS statement is:

> In the registered simulator, aggregated pairwise local graphs cannot
> distinguish persistent simultaneous six-author convergence from a matched
> collection of independently persistent overlapping triplets, while the
> frozen condition-aligned hypergraph refuses the transitive six-author
> interpretation.

This is a higher-order structural-identifiability claim. It does not imply
that an incidence core is personality similarity, compatibility, a
psychological type, or a real human group.
