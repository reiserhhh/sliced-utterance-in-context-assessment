# V8 Spacetime Junction-Flow V3.6.1 Scope Correction

## Decision

`V8_SPACETIME_JUNCTION_FLOW_V361_SCOPE_CORRECTION_COMPLETE`

This is a post-seal audit. It does not alter V3.6's frozen estimator, gates,
or decision. It fills the omitted whole-path diagnostic and quantifies two
known biases: static-marginal classification uncertainty and sparse
high-cardinality path mutual information.

## Static-marginal audit

The same group-blocked classifier used in V3.6 had:

- accuracy 0.316;
- repetition-cluster bootstrap 95% CI [0.293, 0.337];
- 999-permutation null mean 0.334;
- one-sided `p=0.903` for above-null accuracy.

The registered 15 static summaries therefore do not distinguish the routing
worlds. This does not prove that every possible static statistic is
uninformative.

## Whole-path audit

Metrics were recomputed for 200 deterministic regenerations per world using
the frozen confirmation seed block. The path estimator operated on branch
labels recovered from the first observer view.

| World | normalized path entropy | raw conditional cue MI | null MI | bias-adjusted MI | held-out transition | held-out exact path |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cue-guided | 1.000 | 0.667 | 0.216 | 0.451 | 1.000 | 1.000 |
| pass-through | 0.333 | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 |
| random-branch | 0.995 | 0.411 | 0.411 | -0.0001 | 0.354 | 0.0445 |

Conditional MI was tested by permuting complete cue paths within
`initial-branch x group` strata 99 times per population. Mean permutation
`p` was 0.01 for cue-guided, 1.00 for pass-through, and 0.524 for random.

The raw random-world MI of 0.411 was entirely finite-sample plug-in bias:
27-class cue paths and 27-class output paths are too sparse for an uncorrected
conditional-MI interpretation. This is an important negative result for
future real-text path work.

The held-out test split used unseen cue-sequence combinations. A hierarchical
local table learned shared `incoming x cue -> outgoing` rules, rather than
memorizing complete paths. Both deterministic generators generalized
perfectly; random exact-path accuracy was near \(1/27\).

## Corrected interpretation

V3.6 supports a registered **local transition-operator** result:

- pass-through is predictable from incoming direction;
- cue-guided continuation is predictable from the cue and composes over an
  unseen three-stage cue sequence;
- random continuation covers the tree but remains non-addressable.

This still does not establish planning or intelligence. The local rules are
hard-coded and noiseless at the mechanism level, all cue symbols are known,
and there is no task reward, cost, adaptive search, or out-of-vocabulary cue.
The next intelligence-relevant simulator must distinguish memorized routing
from reward-efficient generalization to new cue semantics and changed tree
topology.

Canonical artifacts:

- `results/v8_spacetime_junction_flow/v361_posthoc_scope_audit_r2_20260726/decision.json`
- `results/v8_spacetime_junction_flow/v361_posthoc_scope_audit_r2_20260726/path_metrics.csv`
