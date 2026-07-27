# V8 Incidence Graph Fairness V3.3 Independent Audit

Decision: `PASS`

- All three comparators make structural decisions only from
  \(A_{ijz\epsilon}\); coordinates are used only to construct the tensor.
- Labels affect only F1/ARI. Label permutation leaves selected groups,
  refusals, and claims unchanged.
- The 500 seeds are identical to V3.2 confirmation seeds.
- Every method recovered 500/500 true cores and made 0/500 strong-chain
  claims.
- Maximal-clique and complete-link methods ambiguity-refused 500/500 chains.
- Decision summaries, hashes, and the first seed reproduce.

Accepted claim:

> Condition-aware pairwise adjacency is sufficient for the registered
> core-six versus strong-chain distinction; the failure of aggregate graph
> methods in V3.2 is caused by aggregation over conditions.

Rejected extensions include common-ball uniqueness, generic hypergraph
superiority, personality meaning, and real-text validity.

The next valid experiment must hold the complete pair adjacency tensor fixed
and vary only common-ball feasibility.
