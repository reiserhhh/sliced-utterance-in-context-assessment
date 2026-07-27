# V8 Incidence Graph Fairness V3.3 Report

Decision: `V8_INCIDENCE_GRAPH_FAIRNESS_PASS`

Independent audit: `PASS`

Canonical run:
`results/v8_incidence_graph_fairness/v33_final_20260726/`

## Question

Does V3.2 require common-ball hypergraphs, or does it only require preserving
the condition index in pairwise relations?

V3.3 gives all comparators the full condition-radius adjacency tensor
\(A_{ijz\epsilon}\), without coordinates or MEB information.

## Result

The exact 500 V3.2 confirmation seeds were replayed.

| Condition-aware pairwise method | Core-six claim | Strong-chain claim | Chain ambiguity refusal | Positive F1 / ARI |
| --- | ---: | ---: | ---: | ---: |
| Persistent maximal clique | 500/500 | 0/500 | 500/500 | 1.0 / 1.0 |
| Condition complete-link | 500/500 | 0/500 | 500/500 | 1.0 / 1.0 |
| Aggregate component + concurrency gate | 500/500 | 0/500 | 0/500 | 1.0 / 1.0 |

For maximal-clique and complete-link methods, median maximum persistent group
size was six in the true-core world and three in the strong chain. The
concurrency gate retained size six in the positive world and no passing group
in the chain.

Every 500/500 success has one-sided 95% lower bound 0.9940. Every 0/500
strong-chain claim has one-sided upper bound 0.00597.

The aggregate pair-matrix MAE exactly reproduces V3.2 row by row. All result,
manifest, configuration, and prospective-seal hashes verify.

## Theoretical decision

V3.2 is frozen as an **aggregation information-loss theorem**:

> Aggregating \(A_{ijz\epsilon}\) into \(W_{ij}\) removes the concurrency
> information needed to distinguish simultaneous six-author convergence from
> time-distributed overlapping triplets. Ordinary pairwise methods are
> sufficient once the condition index is retained.

V3.2/V3.3 do not establish common-ball hypergraph uniqueness or superiority.
They also do not establish personality similarity, compatibility, real-text
groups, or clinical meaning.

## Next gate

V3.4 must match the full binary adjacency tensor
\(A_{ijz\epsilon}\) while changing joint common-ball feasibility. Only this
can test whether MEB/common-ball geometry adds information beyond
condition-aware thresholded pair relations.

Even a V3.4 pass would not exceed complete continuous pairwise distance
geometry, because a full Euclidean distance matrix determines the MEB.
