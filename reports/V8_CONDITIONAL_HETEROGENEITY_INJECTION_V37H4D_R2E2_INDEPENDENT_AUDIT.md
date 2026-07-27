# V8 H4D-R2E.2 Independent Mathematical Audit

Date: 2026-07-27

Ruling:
`PASS / ACCEPT_V8_R2E2_CONFIRMED_NORMAL_ONLY`

## Familywise decision audit

The prospective protocol separated two necessary claims:

1. two noise-specific normal \(J_N\) endpoints must exceed `.005`;
2. five tangent \(J_T/\Delta V_T\) endpoints must not exceed `.005`.

The normal family used one-sided family alpha `.05` and Bonferroni endpoint
alpha `.025`. The tangent family used one-sided family alpha `.05` and
Bonferroni endpoint alpha `.01`.

This is a valid intersection-union decision: `NORMAL_ONLY` requires both
necessary subclaims. Each subclaim controls its own familywise error at
`.05`. The result must not be described as one joint 95% confidence set
across all seven endpoints.

## Bootstrap audit

The implementation resamples the 80 parents within each noise family. A
sampled parent retains:

- its baseline;
- normal plus/minus;
- tangent plus/minus;
- all 32 outcome replicates.

The same bootstrap parent indices are used for baseline and paired arms
within a noise family, preserving common-random-number and crossover
dependence. Gaussian and \(t_5\) use independent streams. The pooled
\(\Delta V_T\) endpoint averages the two noise-family bootstrap draws,
which is a valid product-bootstrap construction. Dependence among pooled
and noise-specific endpoints does not invalidate Bonferroni control.

## Numerical decision

Normal positive controls:

\[
J_N^G=.19689,\quad LCB=.19153,
\]

\[
J_N^{t5}=.18546,\quad LCB=.17972.
\]

Both are far above `.005`.

The maximum official tangent Bonferroni upper bound was:

\[
\max UCB_T=.0017404<.005.
\]

Studentized max-t sensitivity bounds gave the same decision. The result is
not threshold-fragile.

The supported statement is:

> The registered normal direction has strong frozen-detector sensitivity,
> while an effect greater than `.005` is excluded for the registered tangent
> family.

This is practical-null evidence, not proof that the tangent effect is
exactly zero.

## Scope restrictions

The result is local to:

\[
m=4,\quad \lambda=.01,\quad support=64,\quad
\tau=.09,\quad \phi=.4,
\]

the frozen synthetic detector, the registered tangent construction, and the
Gaussian/\(t_5\) noise families.

It cannot establish:

- that every tangent direction is a detector kernel;
- that all individual fine geometry is irrelevant;
- that the current macro coordinates are universally sufficient;
- that R2D lacks a target in other generators or real text;
- personality, semantics, intelligence, diagnosis, causality, or clinical
  validity.

## Metadata caveat

Both immutable R2E.2 `seed_audit.json` files retain the legacy key
`common_random_numbers_across_13_geometries`. The actual protocol contains
five geometries, and the formal integrity check verifies exactly five
geometry IDs and 800 geometry rows. This is a stale field name, not a seed
or row-count failure. The generated artifacts were not edited after the
run, preserving their passing manifests and inventories.

