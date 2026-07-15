# V6 Continuous Condition-Manifold Coverage Protocol

## Purpose

The two-phase design theorem requires more than a categorical condition label:
topic, situation, role, and expression opportunity may occupy a continuous,
multidimensional condition manifold. This simulation asks whether fixed balance
is enough when the observed condition representation is coarse or its covered
region is narrow.

## Planted object

\[
Y_{ui}=a_u+m(z_{ui})+B_u\phi(z_{ui})+\epsilon_{ui},\qquad z_{ui}\in\mathbb{R}^2.
\]

`a_u` is a numerical author level, `m(z)` a shared condition surface, and
`B_u phi(z)` an author-by-condition response function. These are simulation
truth variables, not psychological labels.

## Competing arms

1. `wide_exact`: a full fixed grid and the complete smooth condition map.
2. `narrow_exact_same_budget`: the same number of fixed observations, but
   repeated within one half of the condition space.
3. `wide_coarse_proxy`: the full fixed grid but a proxy that omits one condition
   coordinate.

The primary outcome is held-out response-function recovery over new continuous
condition points. The protocol also records coverage radius, level recovery,
and response MSE.

## Interpretation boundary

The result can establish only a mathematical design requirement inside this
generator: prompt equality is not sufficient unless the prompt/condition
representation and support coverage are adequate. It cannot say that any
particular psychological topic taxonomy is correct, that a response is a trait,
or that a real corpus has achieved the required coverage.
