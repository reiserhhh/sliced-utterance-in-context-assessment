# V8 R2G.2A Heavy-Tail Precision Extension

Status: prospective protocol frozen after R2G.2 and before any R2G.2A root
was generated.

R2G.2 passed 19 of 20 mechanism-by-noise gates. Its only failure was the
standardized-\(t_5\) local-to-unity equivalence endpoint:

\[
\hat b_S=-.003987,\qquad
CI_{\mathrm{sim}}=[-.010884,.002910].
\]

The lower endpoint exceeded the registered \(-.01\) boundary by `.000884`.
This is an equivalence-precision failure, not evidence of a non-zero society
component. The original R2G.2 decision remains `PARTIAL_INDEPENDENT_ONLY`.

## Frozen extension

- 80 entirely fresh roots from seed `87243119`.
- No old root is pooled into inference.
- Standardized \(t_5\) noise only.
- The same \(G,n,c\), dimensionality, estimator, checkerboard split,
  practical margin, and 36-endpoint Bonferroni critical value.
- One terminal analysis. No sequential extension.

Primary TOST:

\[
H_0:b_S\le-.01\ \text{or}\ b_S\ge.01,
\qquad
H_1:|b_S|<.01.
\]

Guardrails:

\[
\operatorname{NRMSE}_{test}\le.20,
\]

\[
|\hat b_G-.06|\le.02,\qquad
|\hat b_A-.08|\le.02,
\]

and the misspecified independent model must retain:

\[
LCB(\hat b_S^{naive})>.03.
\]

## Weak-identification diagnostic

Because \(b_S\) and \(b_G\) are nearly collinear on a finite \(G\) grid, the
extension also reports:

\[
\theta_\infty
=
b_S+q_\infty(c)b_G,
\qquad
q_\infty(c)
=
\frac{2(c-1+e^{-c})}{c^2}.
\]

\(\theta_\infty\) is the total asymptotic floor. A successful \(b_S=0\)
equivalence test does not imply \(\theta_\infty=0\): the local-to-unity group
process retains \(q_\infty(1.5)\approx.6428\), so the planted total floor is
approximately `.0386`.

The extension is a synthetic precision resolution only. It does not identify
society and persistent group dependence from unknown real data without
additional dependence assumptions.
