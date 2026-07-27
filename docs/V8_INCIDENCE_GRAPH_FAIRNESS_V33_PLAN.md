# V8 Incidence Graph Fairness V3.3 Plan

Status: `FROZEN_BEFORE_RUN`

## Question

Does V3.2 demonstrate a hypergraph-specific advantage, or only that
aggregating away the condition index loses simultaneity information?

V3.3 gives every comparator the complete condition-radius pair adjacency
tensor

\[
A_{ijz\epsilon}
=
\min_v
\mathbf1\{
\|x^{(v)}_{i,z}-x^{(v)}_{j,z}\|
\le2\epsilon r_z
\}.
\]

No comparator receives common-ball or minimum-enclosing-ball information.

## Frozen comparators

1. `persistent_maximal_clique`: enumerate maximal pairwise cliques at every
   condition-radius cell, score exact membership persistence, and refuse
   overlapping persistent groups.
2. `condition_complete_link`: partition every cell by complete linkage on
   binary pair distance, score recurrent groups, and refuse overlap.
3. `aggregate_component_concurrency_gate`: propose groups from the aggregate
   pair graph, but require all within-group edges to co-occur in the same
   cells often enough to pass 0.04.

All methods use the V3.1 specificity weight, persistence threshold 0.04,
coverage 0.75, and no-chaining refusal. They do not receive true group count.

## Data and gates

- Recreate the exact 500 V3.2 confirmation seeds and frozen DGP.
- Verify aggregate pair-matrix matching remains intact.
- Every method must recover the core-six groups with lower 95% rate at least
  0.90 and median F1/ARI at least 0.90.
- Every method must make at most 0.03 strong-chain six-group claims by upper
  95% bound.
- Maximal-clique and complete-link methods must ambiguity-refuse at least 90%
  of strong chains.
- No enumeration/candidate cap may fire.

## Decision rule

If the condition-aware pairwise methods match the hypergraph decision, V3.2
is frozen as an **aggregation information-loss theorem**. It may not be used
as evidence that common-ball hypergraphs are uniquely necessary.

The next possible incremental test must match the full
\(A_{ijz\epsilon}\) tensor while changing joint common-ball feasibility.
