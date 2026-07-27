# V8 H4D-R2F.1 Independent Mathematical Audit

Date: 2026-07-27

Ruling:
`PASS / ACCEPT_STOP_NO_LOCAL_TANGENT_CANDIDATE`

## Estimator audit

The 32 detector outcomes were divided into two disjoint halves with 16
independent outcome streams each. Common random numbers across geometries
within a half preserve the paired crossover but do not violate A/B
conditional independence.

The implementation correctly uses:

- centered finite differences plus Richardson correction for gradients;
- centered second differences plus Richardson correction for diagonal
  Hessian entries;
- the standard four-corner mixed derivative for off-diagonal entries;
- A/B cross-products for both response operators.

Thus additive Bernoulli measurement variance is removed in expectation.

## Bootstrap and selection audit

Parents, not outcomes, are the bootstrap unit. Resampling is stratified by
Gaussian and \(t_5\), preserves A/B pairing, and recomputes eigendirections
on each of 20,000 draws.

The frozen candidate rule required:

- point strength greater than `.005`;
- bootstrap lower bound greater than zero;
- 90% principal-angle upper at most 45 degrees;
- quadratic upper MSE at most `.0004`.

There is no evidence of post-outcome threshold or direction changes.
R2F.1's correction was made before formal outcomes and appropriately
separated the legacy registered-null control from the new constrained chart.

## Decision audit

First-order:

- strength `.000284`, only 5.7% of threshold;
- angle upper `67.5 degrees`;
- candidate fails materiality and stability.

Second-order:

- strength `-.000304`;
- lower bound negative;
- angle upper `59.9 degrees`;
- candidate fails all three signal requirements.

Quadratic adequacy passed, the normal positive control remained near `.19`,
and the registered-null upper bounds remained below `.00030`. The no-
candidate result is therefore not explained by a broken detector or an
invalid local approximation.

## Negative curvature estimate

The reported curvature strength is a cross-product estimator of latent
curvature energy, not signed geometric curvature. Its population target is
nonnegative, but finite-sample cross-fit operators may have negative
eigenvalues. The estimate means no positive stable curvature energy was
resolved. It cannot be interpreted as global concavity, inhibition, or a
negative psychological mechanism.

The curvature operator maximizes an estimate of \(E\|Hv\|^2\), while the
final scalar uses \(E(v^\top Hv)^2\). These are not equivalent. Therefore
the audit accepts the registered candidate STOP, not an exhaustive absence
of all second-order structure.

## Accepted boundary

Supported:

> Within the frozen `m=4`, `lambda=.01`, `support=64` synthetic detector,
> the registered four-dimensional Jacobian-kernel chart, and the
> `|x|<=.2` neighborhood, no first- or second-order tangent response was
> both materially larger than `.005` and directionally stable.

Not supported:

- absence of signal in the complete 5,670-dimensional tangent space;
- absence of high-order, nonlocal, dynamic, or individual geometry;
- transfer to real text;
- personality, psychology, diagnosis, causality, or clinical meaning.

## Route ruling

Freeze the current synthetic detector tangent-search line. Do not reuse the
115,200 outcomes to expand dimension, rotate directions, alter step size, or
lower thresholds. No candidate exists, so no fresh confirmation is run.
The next evidence should come from an independent or real-text observable,
not further mining of this generator.
