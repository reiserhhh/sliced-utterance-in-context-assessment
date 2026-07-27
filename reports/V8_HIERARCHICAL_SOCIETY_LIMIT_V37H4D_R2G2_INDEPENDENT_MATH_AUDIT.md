# V8 R2G.2 / R2G.2A Independent Mathematical Audit

Date: 2026-07-27

## Decision

`R2G.2_PARTIAL_PLUS_R2G.2A_PASS`

The original R2G.2 machine result remains partial. R2G.2A is a valid
independent fresh-root precision extension because its 80 roots, seed,
estimator, equivalence margin, multiplicity rule, and single terminal
analysis were fixed before the extension ran. Old and new roots were not
pooled.

## Accepted proposition

In the registered synthetic world with:

\[
\rho_G=1-\frac{1.5}{G},
\]

and standardized \(t_5\) private noise:

\[
M(G,n)
=
b_S+b_Gq_G(1.5)+\frac{b_A}{Gn}.
\]

The known-dependence model recovered:

\[
b_S=-.001284
\quad
[-.005732,.003164],
\]

\[
b_G=.06174,\qquad b_A=.08250,
\]

with held-out NRMSE `.03287`.

The total asymptotic floor was:

\[
\theta_\infty=.03840
\quad
[.03786,.03894],
\]

against truth `.03857`.

The misspecified independent-group model generated a false society
coefficient:

\[
b_S^{naive}=.03385
\quad
[.03313,.03458].
\]

Thus local-to-unity group dependence preserves a non-zero aggregation floor
and is falsely assigned to a society-common component when independence is
assumed.

## Required interpretation

- The result establishes practical equivalence \(|b_S|<.01\), not exact zero.
- It explicitly does not establish a zero total limit:
  \(\theta_\infty\approx.0384\).
- Corrected root estimates of \(b_S\) and \(b_G\) correlate `-.9927`.
  Society and persistent-group allocation is weakly identified; the total
  floor is much more stable.
- Known \(c\) makes the planted synthetic terms separable. Unknown or
  unrestricted real dependence may make them observationally equivalent.
- The intervals are 36-family Bonferroni t intervals, not distribution-free
  exact confidence sets.
- Conditional projection yields statistical orthogonality, not causal or
  psychological levels.
- Shared technical noise remains observationally equivalent to stable common
  structure at second order.

## Governance caveat

The source/config hashes and artifact inventories are valid, and both
inventories pass. The repository was dirty and the prospective documents
were not Git-tracked before execution. The work is reproducible local
evidence, but it must not be described as a third-party preregistration seal
until a clean commit and immutable tag exist.

No formula or machine decision needs post-run modification.
