# V8 Real-Text Support and Relation-Field Protocol

Status: `OBSERVED_TECHNICAL_SOFT_SUPPORT__RELATION_UNRESOLVED`

Date: 2026-07-29

## 1. Question and boundary

This experiment asks whether the synthetic V8 event-to-support-to-relation
seam has observable technical counterparts in PANDORA, Essays, and X market
text. It is label-free: no Big Five, MBTI, emotion, diagnosis, or behavioral
target enters the event map, calibration, or decision.

The strongest admissible object is an anonymous replicated text-support
operator. A positive result is not a personality factor.

## 2. Data roles

- PANDORA: author-disjoint Reddit comments in four non-personality
  subreddits; subreddit is self-selected observational context.
- Essays: one fixed-prompt document per writer, divided into within-document
  pseudo-replicates; it cannot establish longitudinal author stability.
- X: collector-selected market posts grouped by query group; query group is
  an observed collection stratum, not author choice or causal context.

Authors are assigned deterministically to D0/D1/D2 in a 40/30/30 ratio. D0
fits all maps and nulls. D1 and D2 are independent confirmation panels.

## 3. Frozen event map

Each raw text event is mapped without labels to a deterministic signed-hash
vector using word uni/bigrams and character 3--5 grams. Two non-equivalent
families are computed from each ordered event path.

The marginal family \(M\) contains order-free means, variances, projected
quantiles, and random Fourier moments. The transition family first computes
lag products, delta variance, transition Fourier moments, and antisymmetric
probability currents. Its order-insensitive expectation is then removed:

\[
K^\circ
=
K-\mathbb E_{\pi}
\left[K\mid\text{same event multiset}\right].
\]

Thus \(K^\circ\) asks what remains after randomizing order while preserving
the author's observed event set. It is not assumed to be psychological
dynamics.

## 4. Replicated support

For family \(f\), source-disjoint technical replicates define

\[
S_f^\times
=
\frac12
\left[
\operatorname{Cov}(X_f^{(1)},X_f^{(2)})
+
\operatorname{Cov}(X_f^{(2)},X_f^{(1)})^\top
\right].
\]

Hard support uses leading eigenvectors and principal-angle recurrence. The
real-text hard axes were not identifiable. The registered fallback is the
trace-one positive support density

\[
\rho_f
=
\frac{(S_f^\times)_+}
{\operatorname{tr}(S_f^\times)_+}.
\]

It is compared by Hilbert--Schmidt alignment, density fidelity, Bures
distance, and a full-spectrum Haar-rotation null. The technical coordinate
filter is \(G_f=\rho_f^{1/2}\), which does not select a unique axis.

## 5. Relation and macro layer

Within a resolved context \(s\), the soft cross-family operator is the
trace-normalized cross-replicate covariance

\[
J_s
=
\frac{
\frac12[
\operatorname{Cov}(M^{(1)},K^{\circ(2)})
+
\operatorname{Cov}(M^{(2)},K^{\circ(1)})
]
}{
\sqrt{
\operatorname{tr}(S_M^+)
\operatorname{tr}(S_{K^\circ}^+)
}
}.
\]

A license requires:

1. both family supports resolved;
2. a within-context author permutation test;
3. D1 and D2 confirmation in the same context;
4. replicated operator or null-excess spectrum agreement;
5. an alias audit showing \(K^\circ\) is not predicted away by \(M\).

Raw singular-spectrum similarity is not sufficient because random
cross-covariance matrices share a generic spectral shape.

For multi-context corpora, covariance is decomposed before normalization:

\[
C_T=C_W+C_B,
\qquad
J_T=J_W+J_B.
\]

The numerical identity is an implementation audit. \(J_B\) is ecological
between-context structure and cannot issue an individual relation license.

## 6. Observed result

All twelve D1/D2 corpus-family support checks passed the soft-density
rotation null while every hard-axis comparison failed. Effective ranks were
diffuse, approximately 29--44 rather than a small factor inventory.

No context obtained the required D1+D2 relation confirmation:

- PANDORA: one isolated D2 `worldnews` endpoint passed locally, but no
  context repeated in D1;
- Essays: neither pseudo-replicate panel passed;
- X: no collector stratum passed.

The relation-field decision is therefore
`REALTEXT_SOFT_SUPPORT_ONLY_RELATION_UNRESOLVED`.

The macro covariance identity closed to numerical error below
\(7\times10^{-16}\), but PANDORA and X heterogeneity/cancellation values
remain descriptive because the local \(M\leftrightarrow K^\circ\) relation
was not licensed.

The first frozen-source transport screen accepted PANDORA to Essays and
PANDORA to X only when both M and \(K^\circ\) were required. However,
\(K^\circ\) passed all six directions; the apparent direction was produced by
M and a source-specific retained-energy threshold. This is a candidate
mechanism, not a containment result.

## 7. Theory update

Real text currently supports the typed chain

\[
\text{frozen event procedure}
\longrightarrow
\text{high-dimensional replicated support density}
\longrightarrow
\text{corpus-local author geometry}.
\]

It does not yet support

\[
M\longleftrightarrow K^\circ
\]

as a stable context relation. Support existence, cross-family relation,
cross-corpus transport, and psychological interpretation are separate
licenses. The next audit must test capacity-conditioned support coverage
under equal event budgets, pair/global metrics, and full-spectrum controls.

