# V8 V3.7H.4D R2E.2 Fresh Endpoint Confirmation

Status: prospective confirmation; no R2E.2 geometry or outcome inspected.

## Purpose

R2E.1 validly confirmed the normal positive control but its frozen
unstudentized nine-endpoint interval was dominated by normal variance. The
tangent point estimates and pointwise intervals were near zero, but the
machine decision correctly remained inconclusive.

R2E.2 confirms the two scientific questions in separate prospective
families:

1. is the known halo-normal direction detectable?
2. is the registered macro-coordinate-matched tangent family practically
   smaller than `.005`?

## Fresh design

- 80 fresh parents per noise family, 160 total;
- only five geometries per parent:
  baseline, normal `.09 +/-`, tangent `.4 +/-`;
- 32 outcomes per geometry;
- 25,600 outcomes total;
- unchanged DGP, 99-sign detector, information matching, CRN crossover,
  and `.005` practical threshold;
- full R2E.1 geometry-only preflight before any outcome;
- fresh root and analysis seeds;
- 20,000 parent-block bootstrap draws.

## Primary intervals

Normal family:

- two \(J_N\) endpoints;
- one-sided Bonferroni family alpha `.05`;
- endpoint lower quantile `.025`.

Tangent family:

- \(J_T\) in Gaussian and \(t_5\);
- \(\Delta V_T\) in Gaussian and \(t_5\);
- pooled \(\Delta V_T\);
- one-sided Bonferroni family alpha `.05`;
- endpoint upper quantile `.99`.

Studentized max-t upper bounds are a sensitivity analysis only.

## Decisions

`CONFIRMED_NORMAL_ONLY` requires:

\[
LCB(J_N)>.005
\]

in both noise families and:

\[
UCB(J_T),\ UCB(\Delta V_T),\
UCB(\Delta V_{T,\mathrm{pooled}})\le .005
\]

for all five tangent endpoints.

`REFUTED_NORMAL_ONLY_TANGENT_CHANNEL` requires the normal positive control
and all tangent lower bounds above `.005`.

Failure to reconfirm normal stops interpretation. All remaining valid
patterns are inconclusive; no threshold, endpoint, or interval method may be
changed after outcome.

## Boundary

Confirmation is local to `m=4`, baseline halo share `.01`, the registered
all-author tangent construction, and the frozen detector. It does not imply
that every fine geometry is null or establish any psychological construct.
