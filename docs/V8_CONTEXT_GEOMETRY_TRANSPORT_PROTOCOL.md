# V8 Same-Author Context Geometry Transport

Status:
`OPENED_PANEL_CONTEXT_TRANSPORT_FALSIFICATION`

## Question

V8-CBQ-RGC-1 found reproducible author-relation correspondence without a
stable global axis. This experiment asks whether that correspondence is only
technical repeatability inside one observed context, or whether it survives
when the same authors write in two different contexts.

For registered contexts \(A,B\) and technical replicates \(r=0,1\), let
\(\widetilde K_{Ar}\) and \(\widetilde K_{Br}\) be the opportunity-filtered,
nuisance-conditioned, within-context U-centered relation matrices. The
cross-context estimand is

\[
\theta_{A\leftrightarrow B}
=
\frac12\left[
\operatorname{KRC}_{rel}(\widetilde K_{A0},\widetilde K_{B1})
+
\operatorname{KRC}_{rel}(\widetilde K_{A1},\widetilde K_{B0})
\right].
\]

The design separately requires positive within-context correspondence
\(\theta_A\) and \(\theta_B\). A normalized cross-excess diagnostic is
reported as

\[
\eta_{A\leftrightarrow B}
=
\frac{\theta^{excess}_{A\leftrightarrow B}}
{\sqrt{
\theta^{excess}_{A}
\theta^{excess}_{B}
}}.
\]

Because null-mean subtraction precedes normalization,
\(\eta_{A\leftrightarrow B}\) is not bounded by one and is not a retention
percentage. It is interpreted only after both within-context gates close.
This is relation transport, not coordinate transport and not a factor score.

## Frozen design

- PANDORA uses six registered pairwise combinations of AskReddit, politics,
  worldnews, and AskWomen.
- Each author contributes eight source-disjoint comments in each context,
  split into odd/even technical replicates.
- The same author hash defines D0/D1/D2 in both contexts.
- D0 fits a separate exchangeable M background, declared-opportunity
  residualizer, nuisance relation operator, and median-distance bandwidth for
  each context arm.
- Only the RBF multiplier that survived V8-CBQ-RGC-1 is read: 0.5 for
  PANDORA. No D1/D2 scale search is allowed.
- A held split with fewer than 24 matched authors returns `NO_OVERLAP`.
- Essays has no second observed context and is not eligible.
- X-market is audited at the same eight-post budget. Its current overlap is
  below the frozen held-panel minimum, so it must refuse rather than lower the
  gate.

An orthogonal support audit enumerates 8, 12, 16, and 24 events per context.
It reports only retained D0/D1/D2 author counts and never chooses an outcome
after reading held-panel metrics. Here event count is an information budget,
not a model hyperparameter and not the transition-family symbol \(K\).

If a higher-budget diagnostic changes the result, the lower budget must be
replayed on the identical higher-budget-eligible author support before any
change is attributed to information amount. This matched-support replay is
descriptive and cannot promote the opened result. It fixes author support but
changes the spread-sampled events and refits the background, residualizer, and
bandwidth. Event composition and estimator refitting therefore remain
alternatives to a pure information-budget explanation.

## Null, interval, and multiplicity

The cross null synchronously permutes both B relation matrices. This preserves
all within-B relations and breaks only the same-author A-to-B correspondence.
Within-A and within-B nulls independently permute the second technical
replicate. Fixed points and the identity assignment remain in support.

Each eligible cell has an exact cellwise permutation \(p\)-value. One Holm
step-down family spans every eligible pair, split, scale, and component cell.
Holm is used because context pairs overlap in authors and contexts; aligning
independently generated pairwise null draws by draw index would not define a
valid joint maximum-\(T\) randomization distribution.
The paired-author bootstrap resamples the four relation matrices together and
re-U-centers each sampled matrix. Its uncertainty is conditional on D0-fitted
backgrounds, residualizers, nuisance relation operators, and bandwidths; it
does not represent full-pipeline refit uncertainty.

## Decision rule

A registered scale is `CONTEXT_TRANSPORTABLE_RELATION_GEOMETRY` only when:

1. within-A and within-B excess are positive in D1 and D2;
2. their Holm-adjusted \(p\leq .05\) and bootstrap lower bounds are positive;
3. cross-context excess satisfies the same gates in D1 and D2;
4. \(\eta_{A\leftrightarrow B}\geq .25\) in both panels and its conditional
   bootstrap lower bound is positive.

Passing within-context but not cross-context gates yields
`CROSS_CONTEXT_UNDERRESOLVED`. It does not establish context binding. Such a
claim would require a separately powered equivalence/refutation design whose
simultaneous upper bound lies below a preregistered minimum transport effect.
Failure to resolve both within-context arms yields
`WITHIN_CONTEXT_GEOMETRY_UNDERRESOLVED`.

The current panels are opened. A positive result is exploratory and requires
fresh authors before promotion. The RGC scale, context disaggregation,
transport audit, twelve-event diagnostic, and matched-support replay reuse
the same opened D1/D2 author panels. They form one adaptive evidence chain,
not independent replications; every downstream \(p\)-value is exploratory.

## Boundary

This experiment may establish a stable same-author relation geometry across
specific observed contexts. It cannot identify personality, emotion,
cognition, causal response to situation, a named latent factor, diagnosis, or
clinical validity. Query groups and subreddits are observed collection strata,
not randomized situations.
