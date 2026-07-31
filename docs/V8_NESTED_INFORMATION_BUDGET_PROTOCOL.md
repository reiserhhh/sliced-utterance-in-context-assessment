# V8 Nested Information-Budget Protocol

Status: opened-panel development protocol.

## Question

The earlier eight- and twelve-event runs used the same eligible author cohort
but changed both the sampled event composition and the fitted estimator. They
therefore could not identify whether the larger relation excess came from
additional text or from estimator adaptation.

This protocol fixes one twelve-event source pool for every author and context,
then reveals literal nested subsets:

\[
E_{u,c}(4)\subset E_{u,c}(6)\subset E_{u,c}(8)
\subset E_{u,c}(10)\subset E_{u,c}(12).
\]

Adjacent event pairs are revealed together. Each increment therefore adds one
event to each alternating technical replicate and preserves source inclusion
inside both replicate streams.

## Two estimator arms

1. `fixed_12_operator`: conditional background, whitening, nuisance
   residualizer and RBF bandwidth are fitted on D0 at twelve events and
   applied unchanged at every lower budget.
2. `budget_refit`: the same objects are fitted on D0 separately at every
   budget.

Only improvement in the fixed arm can be read as evidence that additional
input information improves this frozen measurement operator. Improvement
restricted to the refit arm is estimator adaptation.

## Statistics

For context \(c\), split \(s\), budget \(b\), and estimator arm \(a\), let
\(K^{a}_{c,s,b,0}\) and \(K^{a}_{c,s,b,1}\) be the two U-centered RBF relation
matrices. Relation correspondence is

\[
W^{a}_{c,s}(b)
=
\operatorname{KRC}\!\left(K^{a}_{c,s,b,0},
                          K^{a}_{c,s,b,1}\right)
-
\mathbb E_\pi\operatorname{KRC}\!\left(
K^{a}_{c,s,b,0},
\pi K^{a}_{c,s,b,1}\pi^\top
\right).
\]

Technical disagreement is

\[
Q^{a}_{c,s}(b)
=
\frac{\lVert K^{a}_{c,s,b,0}-K^{a}_{c,s,b,1}\rVert_F^2}
{\lVert K^{a}_{c,s,b,0}\rVert_F^2+
 \lVert K^{a}_{c,s,b,1}\rVert_F^2}.
\]

The primary contrast is twelve minus eight events:

\[
\Delta W=W(12)-W(8),\qquad
\Delta Q=Q(8)-Q(12).
\]

Positive values favor the larger information budget. The full 4/6/8/10/12
curve and the `budget_refit` arm are mechanism diagnostics.

Because one deterministic ladder can privilege a particular part of the
twelve-event pool, a secondary content-sampling audit evaluates all
\(\binom{6}{4}=15\) ways to form an eight-event budget from the six adjacent
event pairs. It uses the same frozen twelve-event operator and reports the
fraction and range of positive twelve-minus-eight contrasts. The schedules
are dependent sensitivity conditions, not independent replications.

## Inference

- The same author permutation is used at every budget within each null draw.
- The same author bootstrap sample is used at every budget and context.
- Relation and disagreement families receive separate studentized
  simultaneous 95% bootstrap bands.
- \(W\) and \(Q\) are computed from the same relation matrices. They are
  complementary diagnostics, not independent evidence or replications.
- Budget labels are not exchangeable; no budget-label permutation p-value is
  reported.
- `0.03` is an interpretive material reference, not a universal psychometric
  standard.

## Evidence boundary

The D1/D2 panels were already opened by the RGC and context-transport chain.
This run can clarify that chain but cannot confirm itself. A future D3 must be
authors or observations that were not inspected while selecting the context
pair, RBF scale, budgets, reveal design, or operator. Renaming or repartitioning
the current authors does not create D3.
