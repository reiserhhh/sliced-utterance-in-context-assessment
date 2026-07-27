# V8 H4D-R2E Construction Erratum

Date: 2026-07-27

Original machine output:
`V8_R2E_STOP_POSITIVE_CONTROL_FAILED`

Post-run scientific ruling:
`INVALID_POSITIVE_CONTROL_CORE_RNG_MISMATCH`

The original output remains immutable and auditable. It must not be used as
evidence that the detector is insensitive to normal or tangent geometry.

## Failure

The intended all-author halo construction was:

\[
Q_\lambda=\sqrt{1-\lambda}\,C+\sqrt{\lambda}\,H.
\]

The runner attempted to recover \(C\) by calling the frozen controlled-halo
builder with the same seed at `lambda=0, support=4`, then subtracting it from
a `lambda=.01, support=64` geometry.

That assumption was false. The builder samples the additional halo-author
support before drawing the core. At `support=64`, selecting 60 inactive
authors advances the random-number generator; at `support=4`, it does not.
The two calls therefore generated different core matrices:

\[
C_{s=4}\ne C_{s=64}.
\]

Consequently:

\[
\widetilde H=
\frac{Q_{.01,s=64}-\cos\theta C_{s=4}}{\sin\theta}
\]

contained a large difference between two unrelated cores. Orthonormalizing
\(\widetilde H\) made it numerically valid but did not restore the intended
diffuse halo.

## Observable evidence

The frozen R2C normal frontier had:

- `lambda=0, core`: detection approximately `.09/.103`;
- `lambda=.03, all64`: detection `1.00/1.00`;
- operator whitened leakage approximately `.0108` versus `.0402`.

The invalid R2E endpoint had nominal `lambda=.03573` but:

- detection only `.124/.138`;
- operator whitened leakage only `.0103/.0110`.

It therefore remained core-like despite passing norm, marginal, support,
halo-share, information, and seed checks. Those checks were necessary but
not sufficient because they did not verify equivalence to the frozen
builder's actual core/halo path.

## Correction

The correct core reconstruction uses:

`lambda=0, support=64, same geometry seed`.

This consumes the identical support-selection RNG path before drawing the
core. A corrected protocol must also directly compare every baseline/normal
geometry with a fresh call to the frozen builder at the same theoretical
lambda and require Frobenius error below `1e-10` before outcome
interpretation.

The corrected run must use a new protocol ID, new root seed, and new output
directory. No original outcomes or thresholds may be reused for tuning.

## Boundary

This erratum invalidates the original positive-control interpretation, not
the broader R2C result and not the R2D Gate-0 pooled STOP. It provides no
evidence about personality, psychology, real text, diagnosis, causality, or
clinical use.
