# V8 Incidence Strong-Chain V3.2 Independent Audit

Decision: `PARTIAL`

The registered simulation, statistics, and artifacts pass. The broad
hypergraph-versus-graph interpretation does not.

## Confirmed

- The triplet schedule is a valid \(2-(6,3,2)\) design.
- Author opportunity counts and aggregate author-pair recurrence are matched.
- The 500 paired confirmation populations and four sets of 500 attacks use
  disjoint seeds.
- The hypergraph recovered 500/500 true cores and made 0/500 strong-chain
  six-author claims; every chain was ambiguity-refused.
- Single-link, complete-link, and spectral methods returned the same
  six-author aggregate groups in both worlds for 500/500 populations.
- Four attacks each produced 0/500 group claims.
- Confidence bounds, summaries, manifest hashes, artifact hashes, and
  prospective-seal hashes recompute.

## Why the methodology decision is partial

The graph methods receive only aggregate \(W_{ij}\). The hypergraph receives
the full condition-indexed views. Since \(W_{ij}\) is deliberately identical
between worlds, equal graph outputs are an information-theoretic consequence,
not evidence that graph algorithms are inferior.

A direct audit using condition-indexed pair adjacency found maximum clique
size six in the true-core world and three in the strong-chain world for all
ten checked seeds. The current DGP therefore requires condition information,
not necessarily a hypergraph.

Calling the aggregate graph output a false claim also depends on changing its
estimand. It correctly identifies a pair-recurrence cluster; it would only be
false to reinterpret that cluster as simultaneous six-author convergence.

## Accepted claim

> In the registered simulator, aggregating condition-indexed pair recurrence
> into a single matrix loses the concurrency information needed to
> distinguish a simultaneous six-author common core from matched overlapping
> persistent triplets.

The audit rejects general hypergraph superiority, unique common-ball
necessity, personality similarity, compatibility, psychological types,
real-text prevalence, and clinical interpretation.

## Required fairness gate

Give the comparator the full \(A_{ijz\epsilon}\) tensor and evaluate
persistent maximal-clique, condition-aware complete-link, and explicit
overlap-refusal rules. If they match the hypergraph, freeze V3.2 as an
aggregation theorem.

To establish an incremental common-ball result after that, construct a
counterfactual with the same condition-indexed pair adjacency tensor but
different joint common-ball feasibility.
