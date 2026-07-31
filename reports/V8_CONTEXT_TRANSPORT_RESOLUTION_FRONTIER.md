# V8 Context-Transport Resolution Frontier

Status:
`INFORMATION_BUDGET_FRONTIER__TRANSPORT_UNDERRESOLVED`

## Result

The corpus-level residual-geometry audit finds axis-free relation
correspondence in a context-stratified PANDORA block aggregate at the
registered short RBF scale. That aggregate contains only within-context
author pairs and weights them by retained Frobenius pair mass. An opened-panel
disaggregation then shows that none of the four PANDORA contexts closes the
same gate alone. The same-author cross-context experiment consequently cannot
assume that either context arm is measured precisely enough for transport.

At eight events per context, three PANDORA pairs retain at least 24 authors in
both held panels, but each technical replicate contains only four comments.
All three return `WITHIN_CONTEXT_GEOMETRY_UNDERRESOLVED`. X-market has no
context pair meeting the same overlap gate.

The support frontier is:

| Events/context | Admissible PANDORA pairs | Interpretation |
| ---: | ---: | --- |
| 8 | 3 | Enough authors, low within-author information |
| 12 | 1 | Only AskReddit--AskWomen remains admissible |
| 16 | 0 | No pair has both held panels at n >= 24 |
| 24 | 0 | No pair has both held panels at n >= 24 |

## Matched-support diagnostic

The only 12-event admissible pair contains 120 authors
(D0/D1/D2=60/28/32). Replaying eight and twelve events on this identical
author support yields:

| Split | Component | 8-event excess | 12-event excess |
| --- | --- | ---: | ---: |
| D1 | within AskReddit | .0029 | .0637 |
| D1 | within AskWomen | .0765 | .1603 |
| D1 | cross | .0544 | .1355 |
| D2 | within AskReddit | -.0303 | .1225 |
| D2 | within AskWomen | .0485 | .1645 |
| D2 | cross | .0494 | .1489 |

At twelve events, D2 cross correspondence has Holm-adjusted
\(p=.0030\), bootstrap LCB \(=.0269\), and normalized-cross-excess LCB
\(=.310\). D1 cross also has Holm-adjusted \(p=.0030\), but its bootstrap
LCB remains negative
(\(-.0359\)). The within-context bootstrap lower bounds also remain below
zero. The diagnostic is therefore consistent with an information-budget
explanation, but it does not independently confirm that mechanism and does
not close transport. In particular, no paired confidence interval for the
twelve-minus-eight event contrast was registered or computed. The two budgets
also use different spread-sampled events and refit the background,
residualizer, and bandwidth, so event composition and estimator refitting
remain competing explanations.

## Theory update

As a working observation model, the current real-text result can be represented
as

\[
\widehat{\mathcal G}_{S,c,b}
=
\mathcal O_{c,b,S}\!\left(\mathcal R_{S,c}\right)
+
\varepsilon_{S,c,b},
\]

where \(S\) is the matched author set, \(\mathcal R_{S,c}\) is a
context-specific author-relation object, \(\mathcal O_{c,b,S}\) is the
complete sampling and estimation operator, and \(\varepsilon_{S,c,b}\) is a
remainder. This decomposition is not identified by the current experiment:
none of its terms is separately recovered, and
\(\mathcal R_{S,A}=\mathcal R_{S,B}\) has not been established. The data
establish a support-information frontier in PANDORA and show that the observed
relation estimates strengthen when \(b\) increases on one matched author
support, while the number of matched authors rapidly decreases.

This is a formal refusal boundary, not a null-personality result. A future
transport study needs more same-author texts in several contexts, not another
global factor search.

## Boundary

All panels are opened and all objects remain anonymous technical author
relations. The result cannot establish personality, emotion, cognition,
causal situation response, construct invariance, diagnosis, or clinical
validity.
