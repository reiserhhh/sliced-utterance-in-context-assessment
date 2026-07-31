# V8-M3-HJIC-SEAM-1 Event-to-Relation Protocol

Status:
`V8_M3_HJIC_SEAM1_PARTIAL`

This protocol tests the remaining synthetic seam between raw event paths and
the already confirmed HJIC-1C context relation field. A 12-repetition
development preflight used 99 null draws and 199 bootstrap draws. The frozen
formal battery then used 60 independent repetitions, 999 null draws, and 999
bootstrap draws without changing gates. Nine of ten gate families passed;
ecological detection reached `.850` rather than `.950`. The result is retained
as partial and motivated the separately frozen SEAM-1A correction.

## 1. Typed arrow

\[
\mathcal N^{f,r}_{u,s}
\xrightarrow{\Phi_{\mathrm{M3}}}
\widehat A^{f,r}_{u,s}
\xrightarrow{\mathcal R_s}
(\widehat J_s,\widehat J_W,\widehat J_B,\widehat J_T,H,\kappa)
\xrightarrow{\mathcal L}
\{\text{license},\text{refusal}\}.
\]

\(\mathcal N^{f,r}_{u,s}\) is an event path for author \(u\), context \(s\),
family \(f\), and replicate \(r\). \(\widehat A\) is a technical replicated
quotient coordinate, not a psychological score. \(\mathcal L\) reads only
observable diagnostics. Synthetic truth is opened only by the audit.

## 2. Frozen M3 event operator

Each 128-event path is split into eight contiguous 16-event blocks. For a
block \(B\), the generator-blind feature map is

\[
\Phi(B)=
\left[
\bar x,\operatorname{Var}(x),
\operatorname{LagCov}_1(x),
\Re\widehat\varphi_x(\omega),
\Im\widehat\varphi_x(\omega),
\Re\widehat\varphi_{(x_t,x_{t+1})}(\nu),
\Im\widehat\varphi_{(x_t,x_{t+1})}(\nu)
\right].
\]

The characteristic-function frequencies are random but frozen on `D0`; they
do not read the world generator. Marginal and transition features are centered
within block so they cannot inherit the planted author mean by construction.

For family \(f\), `D0` identifies the positive replicated support

\[
S_f=\frac12[
\operatorname{Cov}(\bar\Phi_f^{(1)},\bar\Phi_f^{(2)})
+
\operatorname{Cov}(\bar\Phi_f^{(2)},\bar\Phi_f^{(1)})^\top].
\]

The leading two positive eigenvectors \(Q_f\), center \(c_f\), and
cross-replicate whitener \(W_f\) are frozen. Confirmation coordinates are

\[
\widehat A_f^{(r)}=(\bar\Phi_f^{(r)}-c_f)Q_f.
\]

No cross-family truth or external label participates in this calibration.

## 3. Relation and aggregation

Within context \(s\), the relation operator is

\[
\widehat J_s
=W_L\frac12[
\operatorname{Cov}(\widehat A_L^{(1)},\widehat A_R^{(2)}\mid s)
+
\operatorname{Cov}(\widehat A_L^{(2)},\widehat A_R^{(1)}\mid s)
]W_R.
\]

The HJIC-1C covariance-first decomposition is retained:

\[
\widehat J_T=\widehat J_W+\widehat J_B.
\]

\(\widehat J_W\) is the weighted within-context field and
\(\widehat J_B\) is the ecological between-context component. Heterogeneity
\(H\) and cancellation \(\kappa\) retain their HJIC-1C definitions.

## 4. Calibrated refusal layers

- The local relation threshold is the greater of the material floor and the
  `D0` family-wise max-context q99 null.
- The omitted-polynomial nuisance diagnostic is also calibrated on `D0`.
  Every null draw reruns the complete cross-fitted residualizer with an
  independent nuisance design. This retains fitting-induced finite-sample
  correlations that row permutation would erase.
- Mesoscopic reliability below `.25` refuses the event-to-relation seam.
- A registered periodic diagnostic may reveal stable information outside the
  frozen M3 family. If its reliability is at least `.75` while M3 reliability
  is at most `.25`, the system reports mechanism-family mismatch and refuses
  rather than claiming no signal exists.

## 5. Identifiability boundaries

`MICRO_GAUGE_ALIAS` applies an orthogonal hidden-coordinate change followed by
inverse reconstruction. Identical observed event paths must produce identical
M3 outputs, while micro-mechanism identity remains unlicensed. Thus the
observable relation may be identifiable even when its hidden parameterization
is not.

`ESTIMATION_ATTENUATION` adds a same-occasion cross-family author shock that is
independent across repetitions. A same-view covariance retains this shock;
the registered symmetric cross-replicate estimator removes it. Both estimators
are compared with the same analytic population relation.

## 6. Registered worlds

1. `GLOBAL_INVARIANT`
2. `MICRO_GAUGE_ALIAS`
3. `ESTIMATION_ATTENUATION`
4. `BALANCED_CONTEXT_CANCELLATION`
5. `ECOLOGICAL_ONLY`
6. `MECHANISM_FAMILY_MISMATCH`

## 7. Two distinct truth audits

Sample-latent fidelity compares the estimated field with the latent relation
of the same generated authors. It measures direction and shape recovery.

Coverage instead targets the analytic population relation implied by the
generator. A context-stratified author-cluster bootstrap is the primary 95%
interval. A nested author-plus-block bootstrap is retained only as a
conservative sensitivity diagnostic. These estimands must not be mixed.

## 8. Frozen gates

- Clean seam license at least `57/60`.
- Clean relation-fidelity q05 at least `.80`.
- Clean relative-Frobenius-error q95 at most `.25`.
- Covariance-decomposition error q95 at most `.02`.
- Pooled primary 95% cell coverage in `[.90,.98]`.
- Gauge-alias output difference q95 at most `.02`, mechanism-identity licenses
  exactly zero, and seam license at least `57/60`.
- Attenuation correction wins at least `54/60` and reduces median relative
  error by at least `25%`.
- Cancellation detection at least `57/60`; false global license at most
  `3/60`.
- Ecological-only classification at least `57/60`; false individual relation
  at most `3/60`.
- Mechanism-family mismatch detection at least `57/60`; final seam license at
  most `3/60`.
- Independent confirmation decision agreement at least `54/60` after pooling
  registered worlds.
- Observable truth usage is exactly zero.

## 9. Boundary

Passing closes a synthetic engineering and mathematical seam: registered event
paths can be converted by a frozen replicated M3 operator into a correctly
licensed or refused context relation field.

It does not prove that the quotient is personality, that the synthetic worlds
occur in humans, that the relation is causal, or that the hidden micro
mechanism is unique. Psychological interpretation still requires independent
human and external-validity experiments.
