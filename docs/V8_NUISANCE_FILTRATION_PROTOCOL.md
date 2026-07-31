# V8 Opportunity and Content-Sensitivity Filtration

Status:
`OPENED_PANEL_TECHNICAL_SENSITIVITY`

## Question

Does exchangeability-corrected M-family author concordance survive after
declared expression-opportunity predictors are removed by a D0-frozen map?

## Filtration

For corpus \(c\), replicate \(r\), and background-quotient coordinate
\(q_{cur}\), let \(Z^{(g)}_{cur}\) be one cumulative predictor tier. Fit on D0:

\[
\widehat\beta_{cr}^{(g)}
=
\arg\min_\beta
\sum_{u\in D0}
\|q_{cur}-[1,Z^{(g)}_{cur}]\beta\|_2^2
+\lambda\|\beta\|_2^2.
\]

The D1/D2 sensitivity coordinate is

\[
q_{cur}^{(g)}
=q_{cur}-[1,Z^{(g)}_{cur}]\widehat\beta_{cr}^{(g)}.
\]

Writing the frozen fitted component as \(p=q-r\), the observed
cross-replicate trace has the exact expansion

\[
\operatorname{tr}\Sigma_{q_0q_1}
=
\operatorname{tr}\Sigma_{p_0p_1}
+\operatorname{tr}\Sigma_{r_0r_1}
+\operatorname{tr}\Sigma_{p_0r_1}
+\operatorname{tr}\Sigma_{r_0p_1}.
\]

All four terms are reported on the same raw-link denominator. This separates
profile-predictable concordance, residual concordance, and directional
profile-residual coupling without forcing them to be orthogonal or positive.
The decomposition is algebraic; it is not a causal partition.

Two effect scales are deliberately retained:

\[
\Delta T_R^{(R)}
=
T_R^{(R)}-E_\pi T_R^{(R)}
\]

normalizes the filtered residual by its own energy and is the primary
filtration gate, whereas

\[
\Delta T_Q^{(Q)}
=
\Delta T_{PP}^{(Q)}
+\Delta T_{RR}^{(Q)}
+\Delta T_{PR}^{(Q)}
+\Delta T_{RP}^{(Q)}
\]

uses the raw-\(Q\) denominator for every component and reconstructs the raw
link excess exactly. Superscripts identify the denominator. The two scales
answer different questions and must not be subtracted or interpreted as
fractions of one another without an explicit denominator conversion.

The tiers are:

1. raw background quotient;
2. length, formatting, and time opportunity;
3. opportunity plus within-author near-duplicate/template indicators;
4. declared opportunity plus available collection variables such as language
   and market symbol;
5. an aggressive content-proxy tier built from frozen random projections of
   the event vectors.

Tier 5 is not a denoising target. Content may carry the technical author
object itself. Its purpose is to locate dependence, not to justify deletion.

## Null and uncertainty

The signed replicate link is tested by uniformly permuting replicate-two
author correspondence within corpus, split, and observed context. Fixed
points and the identity assignment are in the support. D0 maps remain frozen.
Intervals use context-stratified paired author bootstrap. Maximum-T correction
is applied across corpora and D1/D2 separately for each filtration tier.

## Interpretation

- Survival after tiers 2-4 means the detected relation is not exhausted by
  the registered opportunity surface.
- Attenuation means the relation is sensitive to that surface. It does not
  establish that the removed component was noise, a confounder, or outside
  the construct.
- Survival after tier 5 identifies structure beyond a coarse content proxy;
  failure after tier 5 does not invalidate the author relation.
- Essays remains a within-document coherence stress test rather than an
  independent-occasion author design.

No outcome licenses personality, emotion, cognition, causality, language
invariance, diagnosis, or clinical use.
