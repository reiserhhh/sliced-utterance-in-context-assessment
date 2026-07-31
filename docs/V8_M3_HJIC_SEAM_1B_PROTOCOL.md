# V8-M3-HJIC-SEAM-1B Measurement-Support Invariance Protocol

Status:
`V8_M3_HJIC_SEAM1B_SUPPORT_INVARIANCE_PASS`

SEAM-1A isolated the between-null defect while intentionally retaining the
original D0-to-confirmation loading drift. SEAM-1B now tests that drift as a
separate estimand. It does not reinterpret either prior `PARTIAL` run.
The independent 60x999 formal battery passed every registered gate family
without post-run rule changes.

## 1. Measurement-support object

For family \(f\) and independent confirmation split \(d\), raw block features
are aggregated per author before the frozen M3 projection. Their same-family
replicated covariance is

\[
\widehat S_{f,d}
=
\frac12[
\operatorname{Cov}(\bar\Phi_{f,d}^{(1)},\bar\Phi_{f,d}^{(2)})
+
\operatorname{Cov}(\bar\Phi_{f,d}^{(2)},\bar\Phi_{f,d}^{(1)})^\top].
\]

Let \(\widehat Q_{f,d}\) be its leading two positive-eigenvalue directions and
\(Q_{f,0}\) the D0-frozen support. The registered alignment statistic is the
worst principal-angle cosine squared:

\[
A_{f,d}
=
\sigma_{\min}^2(Q_{f,0}^{\top}\widehat Q_{f,d}).
\]

This statistic is invariant to rotation inside the same support. It detects
loss or replacement of a calibrated direction, not a unique hidden loading
matrix.

## 2. Resolution before invariance

Support alignment is meaningful only when the confirmation support is
estimable. Two observable resolution diagnostics are therefore required:

\[
G_{f,d}
=
\frac{\lambda_k-\lambda_{k+1}}
{\max(|\lambda_k|,\epsilon)},
\qquad
E_{f,d}=\lambda_k,
\]

where \(k=2\). Low \(G\) or \(E\) produces `SUPPORT_UNDERRESOLVED`; it is not
called drift.

D0 thresholds are calibrated by repeatedly splitting D0 authors into two
disjoint halves. For every split, the minimum across families and halves is
recorded:

\[
\tau_A=Q_{.01}(A_{\text{half1,half2}}),\quad
\tau_G=Q_{.01}(G),\quad
\tau_E=Q_{.01}(E).
\]

The calibration sees only same-family raw M3 features. It never reads
cross-family truth or hidden loadings.

## 3. Registered worlds

- All original relation, alias, attenuation, cancellation, ecological,
  mismatch, and held-out-null worlds now share one latent-to-event operator
  across D0/D1/D2. Authors, paths, and innovations remain independent.
- `WITHIN_SUPPORT_GAUGE` rotates coordinates inside the same column space and
  must not trigger refusal.
- `MEASUREMENT_SUPPORT_DRIFT_GLOBAL` replaces the confirmation support while
  preserving a latent global relation.
- `MEASUREMENT_SUPPORT_DRIFT_ECOLOGICAL` replaces the support while preserving
  an ecological latent relation.
- `SUPPORT_UNDERRESOLVED` contains no stable author support and must be refused
  as underresolved rather than noninvariant.

Sharing the simulation operator is not estimator leakage. The estimator sees
only D0 events and freezes \(Q_{f,0}\); D1/D2 hidden loadings remain inside the
truth lockbox.

## 4. License

When support auditing is active, a final seam license additionally requires
both independent confirmation splits to be resolved and aligned. Both splits
below \(\tau_A\) license `SUPPORT_NONINVARIANT`. Either split failing
\(\tau_G\) or \(\tau_E\) licenses `SUPPORT_UNDERRESOLVED`. Disagreement is
reported and cannot be silently averaged away.

## 5. Frozen gates

The independent formal run uses seed `20260804`, 60 repetitions, 999 null
draws, and 999 bootstrap draws.

- Aligned global seam and aligned ecological detection each at least `57/60`.
- False support refusal in global, ecological, and within-support-gauge worlds
  each at most `3/60`.
- Global and ecological severe support-drift detection each at least `57/60`;
  final seam license in each at most `3/60`.
- D1/D2 support-decision agreement at least `.90` after pooling registered
  worlds.
- Held-out-null false support-drift classification at most `3/60`.
- Support-underresolution detection at least `57/60`; final seam license at
  most `3/60`.
- All relation, decomposition, coverage, alias, attenuation, cancellation,
  ecological, mismatch, and truth-isolation gates remain unchanged.

## 6. Boundary

Passing proves a synthetic observable distinction among aligned support,
support non-invariance, and support underresolution. It does not identify the
hidden operator that changed, justify comparing scores after refusal, or
construct a transport map. Human measurement invariance and psychological
meaning remain future empirical questions.
