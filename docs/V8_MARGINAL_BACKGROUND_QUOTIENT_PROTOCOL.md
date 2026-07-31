# V8 Marginal-Background Quotient Protocol

## Question

Does the order-free V8 `M` family contain a replicated natural-author grouping
residual after accounting for the geometry that the measurement operator
inevitably creates from corpus-, context-, slot-, and local-length-matched
single-event marginals?

This is not a denoising experiment. It estimates the position of a natural
event set relative to its conditional pseudo-author orbit.

## Frozen object

For corpus \(c\), author \(u\), and technical replicate \(r\), let

\[
m(\mathcal X_{cur}) =
[\operatorname{mean}_{64},\operatorname{variance}_{64},
\operatorname{RFF}_{16},\operatorname{quantiles}_{24}]
\in\mathbb R^{168}.
\]

Pseudo authors are bijective slot-wise reallocations within corpus, D-split,
context, and local length-rank blocks. They preserve every complete
64-dimensional event vector and every slot marginal while breaking natural
author-event correspondence, natural within-author co-occurrence, and the
cross-replicate author link.

D0 pseudo worlds freeze a conditional center \(b_{crZ}\) and one shrinkage
covariance \(\Omega_{cb}\) per M block:

\[
q_{curb} =
\Omega_{cb,\lambda}^{-1/2}
\{m_b(\mathcal X_{cur})-b_{crZ,b}\}.
\]

PANDORA, Essays, and X-market are calibrated independently. No axes,
whiteners, or coefficients are transported between corpora.

## Primary statistic

\[
C_{cs} =
\frac{1}{2}\left[
\operatorname{Cov}(Q_0,Q_1)+
\operatorname{Cov}(Q_1,Q_0)^\top
\right],
\qquad
T_F=\|C_{cs}\|_F .
\]

No positive-part projection, eigenvalue clipping of the signed replicated
operator, or trace-one normalization is allowed. Numerical flooring is used
only for the positive D0 background covariance that defines whitening.

The primary test compares natural \(T_F\) with 1,999 independently generated
pseudo-author worlds. MaxT controls the six PANDORA/Essays/X-market by D1/D2
omnibus cells. A paired-world author-cluster bootstrap resamples both technical
replicates together and applies the same author indices to a frozen bank of
pseudo worlds. Its centered lower bound is computed on the natural-minus-pseudo
contrast. A natural-only percentile bootstrap is forbidden because duplicate
authors upward-bias covariance norms.

Location/shape diagnostics use the first 199 frozen pseudo worlds. They cannot
promote a claim independently of the 1,999-world omnibus test.

## Secondary diagnostics

- Signed concordance `link`
- Natural-data same-author cosine AUC (descriptive; not recomputed in every
  pseudo world because it is not a promotion statistic)
- Operator norm and effective rank
- `location_mean`
- `strict_shape = variance + centered RFF`
- `dispersion_variance`
- `higher_shape = centered RFF`

Raw quantiles are excluded from `strict_shape` because they retain location.
Block and leave-one-block interpretations are diagnostic until omnibus `M_all`
passes.

For centered quotient rows, signed concordance is the normalized trace of the
cross-replicate operator:

\[
T_{\mathrm{link}}
\simeq
\frac{n}{n-1}
\frac{\operatorname{tr}(C_{01})}
{\sqrt{\operatorname{tr}(C_{00})\operatorname{tr}(C_{11})}}.
\]

Unlike the Frobenius norm, it cancels incoherent high-dimensional directions
and tests same-coordinate concordance. It receives its own six-cell maxT and
paired-world cluster-bootstrap bound. A link-only pass is reported separately
as `SIGNED_CONCORDANCE_RESIDUAL_DETECTED`; it does not retroactively satisfy
the omnibus arbitrary-operator gate.

## Promotion and refusal

A corpus-local pass requires D1 and D2 to have:

- positive natural-minus-pseudo Frobenius excess;
- maxT \(p\le .05\);
- author-bootstrap lower 95% bound above zero;
- positive signed concordance.

Coverage below 90% is `BACKGROUND_QUOTIENT_UNDERRESOLVED`. A pass licenses only
a corpus-local natural grouping residual. It does not identify personality,
emotion, cognition, language invariance, diagnosis, causality, or cross-corpus
common coordinates.

Even after a pass, lexical fingerprinting, duplicated text, unmeasured thread
or time structure, formatting, language, community membership, and
pseudo-text unnaturalness remain alternative explanations.
