# V8 Conditional Background-Quotient Concordance Spectrum

Status:
`EXPLORATORY_REAL_TEXT_TECHNICAL_STRUCTURE__PSYCHOLOGICAL_MAPPING_CLOSED`

Date: 2026-07-30

## 1. Why this layer is needed

An observed author aggregate is not automatically an author property. The
measurement operator, corpus, context, event slot, and local text-length
distribution can create reproducible geometry before natural utterances are
grouped by author. V8 therefore separates:

\[
\text{conditional event marginals}
\longrightarrow
\text{measurement background}
\longrightarrow
\text{background quotient}
\longrightarrow
\text{replicated author concordance}.
\]

This is not denoising by subtraction. The background is a conditional
reference orbit. The retained object is the natural author's position and
replicate relation relative to that orbit.

## 2. Background quotient

For corpus \(c\), author \(u\), technical replicate \(r\), and event set
\(\mathcal X_{cur}\), the order-free M representation is

\[
m(\mathcal X_{cur})
=
[\operatorname{mean}_{64},
\operatorname{variance}_{64},
\operatorname{RFF}_{16},
\operatorname{quantiles}_{24}]
\in\mathbb R^{168}.
\]

Pseudo authors are constructed by bijective event reallocation within corpus,
split, context, slot, and local length-rank blocks. They preserve complete
event vectors and declared event marginals while perturbing natural
author-event grouping and cross-replicate author correspondence. The corrected
operator samples uniformly from the complete within-block symmetric group;
fixed points and the observed identity assignment are in its support. D0
pseudo worlds define blockwise centers and covariance:

\[
q_{curb}
=
\Omega_{cb,\lambda}^{-1/2}
\{m_b(\mathcal X_{cur})-E_{\mathbb B_c}[m_b\mid Z]\}.
\]

The resulting \(q\) is a coordinate in a conditional background quotient. It
is corpus-local: centers, covariance, axes, and coefficients are never
transported between corpora.

## 3. Why signed concordance replaced raw operator energy

The symmetric cross-replicate operator is

\[
B_c
=
\frac{1}{2n}
(Q_{c0}^{\mathsf T}Q_{c1}+Q_{c1}^{\mathsf T}Q_{c0}),
\]

and the complete within-replicate energy is

\[
W_c
=
\frac12(C_{c00}+C_{c11}).
\]

The Frobenius statistic \(\|B_c\|_F\) accumulates coherent, anti-coherent, and
finite-sample directional energy. It therefore did not yield a complete
three-corpus grouping result. The normalized signed trace

\[
T_{\mathrm{link},c}
=
\frac{\operatorname{tr}(B_c)}
{\sqrt{\operatorname{tr}(C_{c00})\operatorname{tr}(C_{c11})}}
\]

cancels incoherent directions and directly tests same-coordinate
cross-replicate concordance.

The original audit used a nonzero cyclic shift. It was a valid generative
knockout, but its support excluded fixed points, the observed identity, and
most permutations. Its tail areas are therefore Monte Carlo tail areas under
that knockout, not exact permutation p-values.

The full exchangeability-corrected rerun found:

- PANDORA: link excess \(+.01650/+.01533\) in D1/D2, maxT
  \(p=.0060/.0165\), paired lower bounds \(+.00180/+.00037\);
- Essays: \(+.06299/+.07299\), maxT \(p=.0005/.0005\), lower bounds
  \(+.04954/+.05974\);
- X-market: \(+.20973/+.22887\), maxT \(p=.0005/.0005\), lower bounds
  \(+.13096/+.14060\).

Signed concordance is therefore detected in all three corpora under the
corrected null. This is a technical grouping result, not a personality result.

## 4. Conditional background-quotient concordance spectrum

Signed trace is only the first spectral moment. The Conditional
Background-Quotient Concordance Spectrum (CBQ-CS) asks whether that moment is
carried by reproducible low-dimensional directions. With additive ridge

\[
W_{c,\gamma}
=
W_c+\gamma\frac{\operatorname{tr}(W_c)}{d}I,
\]

the generalized problem is

\[
B_cv_{cj}
=
\lambda_{cj}W_{c,\gamma}v_{cj}.
\]

Because \(W_{c,\gamma}\succeq W_c\), Cauchy-Schwarz bounds the signed
generalized spectrum in \([-1,1]\). Positive and negative eigenvalues are
retained separately; no positive-part projection or post-hoc sign flipping is
allowed.

D0 pseudo worlds set extreme-eigenvalue thresholds. A candidate subspace must
also exceed pseudo A/B subspace affinity and preserve the expected sign under
A-to-B and B-to-A held-out projection. Only then are frozen directions scored
on D1 and D2.

## 5. Exchangeability-corrected opened-panel findings

| Corpus | Resolved object | Main result | Boundary |
| --- | --- | --- | --- |
| PANDORA | No positive M or strict-shape axis | rank 0 at the current D0 resolution despite weak signed trace | The detected trace is distributed or below axis resolution; fresh D3 is required. |
| Essays | No stable low-dimensional axis | two D0 M candidates fail the A/B affinity threshold (.0246 versus .0363) | The earlier three-axis result is superseded; within-document coherence remains a design limitation. |
| X-market | Three M axes plus one strict-shape axis | M excess \(+.599/.464\); strict-shape excess \(+.765/.629\), all paired lower bounds positive | Only 141 authors are available; symbol, language, template, time, and market-role alternatives remain. |

No stable negative spectrum was resolved. Therefore the current data do not
support a technical-view complementarity axis.

The correction establishes an important non-implication:

\[
T_{\mathrm{link}}>0
\quad\not\Rightarrow\quad
\operatorname{rank}_{\mathrm{resolved}}>0.
\]

PANDORA and Essays retain same-author concordance without a stable common
low-dimensional chart. Author structure may be diffuse, locally curved,
sample-rotating, or simply below the present resolution. Calling that
remainder a factor would exceed the evidence.

These ranks are not common factor counts. They are corpus-local resolved
ranks under different collection opportunities:

\[
\operatorname{rank}_{\mathrm{resolved}}(c)
=
\operatorname{rank}
\left[
\text{author concordance visible under the design of }c
\right].
\]

The contrast itself is informative: measurement opportunity controls which
author structure can be resolved. It does not imply that one corpus contains
more personality than another.

## 6. Integrated V8 object

The static M route is now:

\[
x
\longrightarrow
m(\mathcal X)
\longrightarrow
q=\Omega_{\mathbb B}^{-1/2}
\{m-E_{\mathbb B}m\}
\longrightarrow
(B,W)
\longrightarrow
\{\lambda_j,V_j\}_{c}^{+/-}.
\]

The transition K route remains separate and terminates at the Conditional
Marginal Orbit-Susceptibility Operator:

\[
(c,o)
\longrightarrow
P_c(x\mid Z)
\longrightarrow
\mathcal T_{K,c}.
\]

Current evidence does not license a natural author-composition increment or
observed-order phase on K. M and K must not be forced into one latent factor
inventory merely because both originate from text.

## 7. What the breakthrough is

The new theoretical contribution is a falsifiable separation between:

1. geometry generated by the measurement operator and conditional event
   marginals;
2. natural same-author concordance beyond that background;
3. the spectral dimensionality of the concordance;
4. later external psychological or behavioral meaning.

This makes “unnameable dynamics” mathematically tractable without naming them
prematurely. An anonymous direction can be characterized by sign, magnitude,
rank, replicate stability, block composition, condition sensitivity, and
transport boundary before any semantic reading or personality label is used.

## 8. Completed falsification and theory refinement

The declared-opportunity filtration and filtered spectrum have now been run.
Signed concordance survives in all three corpora, but no stable filtered
global linear axis remains. The raw X axes are therefore retained as
opportunity-mediated historical directions, not current author factors.

The next estimand was correctly changed from another axis to author-relation
correspondence:

\[
\operatorname{KRC}_{rel}
=
\frac{\langle\widetilde K_0,\widetilde K_1\rangle_F}
{\|\widetilde K_0\|_F\|\widetilde K_1\|_F}.
\]

Within-context U-centering removes diagonal self-similarity. The
context-stratified PANDORA block aggregate resolves short-scale RBF relation
correspondence and the corresponding X aggregate resolves multi-scale
correspondence; Essays remains scalar-only. These aggregates weight retained
within-context author-pair mass and contain no cross-context relation. The
RBF-minus-linear contrast does not close, so this is not a nonlinear claim.

The same-author cross-context audit then returns
`CONTEXT_TRANSPORT_UNDERRESOLVED`. None of the individual PANDORA contexts
passes the complete relation gate, even though the context-stratified block
aggregate does. Increasing the event budget on identical
AskReddit--AskWomen author support raises all within and cross point
estimates, but PANDORA loses matched authors faster than precision closes.
Event composition and estimator refitting remain competing explanations, so
this is only compatible with an information-budget hypothesis.

A non-identifying working observation model is:

\[
\widehat{\mathcal G}_{S,c,b}
=
\mathcal O_{c,b,S}\!\left(\mathcal R_{S,c}\right)
+\varepsilon_{S,c,b}.
\]

The terms are not separately identified, and
\(\mathcal R_{S,A}=\mathcal R_{S,B}\) has not been established. The RGC
scale, context disaggregation, transport audit, and event-budget diagnostics
reuse the same opened D1/D2 panels and form one adaptive exploratory chain.
The next fresh-data falsification must freeze enough events per author and
enough same-author contexts before opening D3. More axis mining on the opened
panels is stopped. All objects remain anonymous until an independently
registered external psychological or behavioral linkage succeeds.

The current result licenses a new technical measurement layer. It does not
license personality, emotion, cognition, intelligence, diagnosis, causality,
cross-language invariance, or clinical use.
