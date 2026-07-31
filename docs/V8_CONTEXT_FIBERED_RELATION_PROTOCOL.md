# V8-HJIC-1C Context-Fibered Relation and Aggregation Protocol

Status:
`V8_HJIC1C_CONTEXT_RELATION_FIELD_PASS`

This protocol was frozen after a 12-repetition development preflight with 199
null permutations and 199 author bootstraps. The preflight passed all
registered decision categories after increasing the planted relation evidence
budget and calibrating the omitted-polynomial diagnostic. Those development
results are not formal confirmation. The subsequently frozen formal run used
60 repetitions, 999 null permutations, and 999 author bootstraps and passed
all 13 decision gates without further rule changes.

## 1. Open arrow

HJIC-1B can veto a materially condition-sensitive global relation. It cannot
distinguish a reproducible local relation field from ecological composition,
sign cancellation, or context measurement failure. HJIC-1C therefore
implements the next typed arrows:

\[
\widehat A_u
\xrightarrow{\mathcal R_s}
\mathcal J
\xrightarrow{\Gamma_{\rho,w}}
\mathfrak G_{\rho,w},
\]

\[
\mathcal J=\{(p_s,J_s):s=1,\ldots,K\},
\]

\[
\mathfrak G_{\rho,w}
=
(p_s,\{J_s\},J_W,J_B,J_T,H,\kappa,\mathcal U).
\]

\(\widehat A_u\) is a replicated technical readout, not a questionnaire score.
The external psychological map \(\Psi\) remains closed.

## 2. Author-disjoint design

- `D0 calibration` freezes the two marginal whitening maps, four context
  cut-points, and a 99th-percentile max-context null threshold. It never reads
  cross-family truth.
- `D1 confirmation-A` and `D2 confirmation-B` contain independent authors.
- Each readout family has two independent text-replicate views.
- The primary nuisance model is a cross-fitted total-degree-three polynomial
  sieve.
- Fourth- and fifth-degree residual dependence is a registered
  misspecification diagnostic, not a replacement estimator.
- Context labels have two independent measurements in the reliability
  frontier.

The formal run uses 1,200 calibration authors and 1,200 authors in each
confirmation split.

## 3. Covariance-first relation field

For context \(s\), let the symmetric cross-replicate covariance be

\[
C_s
=
\frac12\left[
\operatorname{Cov}(B^{(1)},M^{(2)}\mid s)
+
\operatorname{Cov}(B^{(2)},M^{(1)}\mid s)
\right].
\]

One pair of marginal whitening maps \(W_B,W_M\), frozen on `D0`, defines

\[
J_s=W_BC_sW_M.
\]

The method does not average context correlations. It first applies the total
covariance theorem:

\[
C_T
=
\underbrace{\sum_s p_s C_s}_{C_W}
+
\underbrace{
\sum_s p_s
(\mu_{B,s}-\mu_B)(\mu_{M,s}-\mu_M)^\top
}_{C_B}.
\]

Because the same linear maps are used after decomposition,

\[
J_T=J_W+J_B
\]

must hold up to floating-point error. \(J_W\) is the within-context relation;
\(J_B\) is the between-context or ecological component. A large \(J_B\) does
not license an individual relation.

The registered heterogeneity and cancellation functionals are

\[
H
=
\frac{
\sum_s p_s\|J_s-J_W\|_F^2
}{
\sum_s p_s\|J_s\|_F^2+\epsilon
},
\]

\[
\kappa
=
1-
\frac{\|J_W\|_F}
{\sum_s p_s\|J_s\|_F+\epsilon}.
\]

They describe a technical field. They are not causal effects or personality
scores.

## 4. Observable licenses

A local relation requires:

- both confirmation splits above the `D0` max-context null threshold and the
  fixed material floor;
- cross-confirmation direction cosine at least `.80`;
- at least two licensed contexts for a field-level relation;
- context-assignment agreement at least `.70`;
- context-measurement field agreement at least `.80`;
- no registered residualizer misspecification;
- no declared post-response/collider context role.

A unique local mode is a separate license. Its singular gap must exceed twice
the cross-confirmation operator error plus the fixed `.04` margin. Relation
failure and unique-mode failure are not interchangeable.

Composition reweighting is licensed only when:

- the local field is independently reproduced;
- context-weight L1 shift is at least `.40`;
- at least `.70` of the aggregate within-relation shift is explained by
  applying the observed weight change to the cross-confirmed local field.

Every license records `truth_used_by_license=false`.

## 5. Registered worlds

1. `GLOBAL_INVARIANT`
2. `BALANCED_SIGN_REVERSAL`
3. `TRUE_CONTEXT_MODERATION`
4. `ECOLOGICAL_ONLY`
5. `COMPOSITION_REWEIGHT`
6. `NONLINEAR_SIMPSON_IN_SIEVE`
7. `NONLINEAR_SIMPSON_OUT_OF_SIEVE`
8. `NOISY_CONTEXT_FRONTIER` at
   \(\rho_Z\in\{1,.8,.6,.4,.2\}\)
9. `LOCAL_NULL_MULTIPLE_STRATA`
10. `LOCAL_LOW_SINGULAR_GAP`
11. `COLLIDER_OR_DESCENDANT_Z`

The observable taxonomy is:

\[
\begin{aligned}
&\texttt{GLOBAL_INVARIANT},\\
&\texttt{LOCAL_RELATION_ATLAS},\\
&\texttt{GLOBAL_CANCELLATION},\\
&\texttt{ECOLOGICAL_ONLY},\\
&\texttt{COMPOSITION_REWEIGHT},\\
&\texttt{MODE_UNDERRESOLVED},\\
&\texttt{RESIDUALIZER_MISSPECIFIED},\\
&\texttt{CONTEXT_UNDERRESOLVED},\\
&\texttt{CONTEXT_ROLE_UNSUPPORTED},\\
&\texttt{NO_SUPPORTED_RELATION}.
\end{aligned}
\]

## 6. Frozen formal gates

The formal battery uses 60 repetitions, 999 max-context null permutations,
and 999 author-block bootstraps per registered coverage world.

- Total-covariance decomposition standardized-error q95 at most `.02`.
- Pooled nominal 95% cell-wise coverage in `[.90,.98]`.
- `GLOBAL_INVARIANT`: correct global license at least `.95`;
  heterogeneity false alarm at most `.05`.
- `BALANCED_SIGN_REVERSAL`: local atlas, heterogeneity, and cancellation
  detection each at least `.95`; global license at most `.05`.
- `TRUE_CONTEXT_MODERATION`: local atlas and heterogeneity each at least
  `.95`; global license at most `.05`.
- `ECOLOGICAL_ONLY`: between-context detection at least `.95`; individual
  relation license at most `.05`.
- `COMPOSITION_REWEIGHT`: correct composition attribution at least `.95`;
  attribution failure at most `.05`.
- In-sieve Simpson false relation at most `.05`.
- Out-of-sieve misspecification detection at least `.95`; final relation
  license at most `.05`.
- `LOCAL_NULL_MULTIPLE_STRATA`: family-wise any-field license at most `.05`.
- `LOCAL_LOW_SINGULAR_GAP`: relation license at least `.95`; unique-mode
  license at most `.05`.
- At \(\rho_Z\ge.8\), relation recovery at least `.95`; at
  \(\rho_Z\le.4\), explicit underresolution at least `.95`.
- Collider/descendant role refusal at least `.95`; final relation license at
  most `.05`.
- Truth usage by every observable license is zero.

## 7. Required outputs

- `context_relation_field.csv`
- `within_between_covariance.csv`
- `aggregation_commutation.csv`
- `heterogeneity_cancellation.csv`
- `ecological_failure_modes.csv`
- `context_reliability_frontier.csv`
- `uncertainty_coverage.csv`
- `licenses.csv`
- `truth_audit.csv`
- `decision.json`
- `run_manifest.json`
- `artifact_inventory.json`

## 8. Boundary

Passing licenses a synthetic procedure for identifying a preregistered
context-indexed technical relation field, separating within-context,
between-context, and composition components, and refusing when context,
residualizer, or causal-role support is inadequate.

It does not establish causal deconfounding, exhaustive context coverage,
human prevalence, personality meaning, language invariance, diagnosis, or
clinical validity. It also does not yet close the M3-to-HJIC seam from raw
event paths; that is the next experiment after this relation-field layer.
