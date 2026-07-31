# V8 Exchangeable Background Audit

Status:
`OPENED_PANEL_METHOD_CORRECTION`

## Question

Do the M-family marginal-background and CBQ-CS conclusions survive when the
pseudo-author distribution is changed from a forced no-self cyclic knockout
to a uniform within-block permutation distribution?

## Why this correction is necessary

The historical knockout used a non-zero cyclic shift in every
split/context/slot/local-length block. It preserved event marginals and
guaranteed that natural author grouping was destroyed, but it excluded every
fixed point, the natural identity assignment, and most non-cyclic
permutations. It is therefore a useful generative knockout distribution, not
an exact exchangeability randomization distribution. Its Monte Carlo tail
areas must not be described as exact permutation p-values.

## Corrected operator

For each frozen block \(h\), sample

\[
\pi_h\sim\operatorname{Uniform}(\mathfrak S(h)).
\]

The complete operator is

\[
\Pi_{\mathrm{ex}}
=
\prod_h\mathfrak S(h).
\]

The identity permutation belongs to every \(\mathfrak S(h)\). Fixed points
are allowed and their observed rate is audited. Complete 64-dimensional event
vectors, event-slot marginals, split, context, and local length blocks remain
preserved exactly.

## Analysis

The existing M background quotient and CBQ-CS estimators are rerun without
changing feature maps, block definitions, regularization grids, rank rules,
or D0/D1/D2 assignments. The only changed object is the pseudo-author
reallocation distribution.

The result is an opened-panel method correction. Agreement strengthens the
technical conclusion. Disagreement supersedes the affected tail-area claim
but does not erase the descriptive natural-author statistic.

No result licenses personality, emotion, cognition, causality, cross-corpus
common factors, diagnosis, or clinical use.
