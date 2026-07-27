# V8 V3.7H.3 Multiscale Zero-Identification Plan

Status: prospective synthetic discovery protocol.

This protocol operationalizes a narrow version of the multiscale intuition:
components are not declared absent because an aggregate is small. Instead, a
component is characterized by how its observable energy changes under a
registered amplitude path, replication depth, and aggregation scale.

No text, external label, psychological construct, diagnosis, or clinical
claim is used in this experiment.

## Observation model

For society \(s\), nested group \(g\), author \(u\), condition \(c\),
opportunity \(k\), and technical stream \(r\):

\[
X_{sguckr}
=
\mu+S_s+G_{g|s}+A_{u|gs}+H_c+B_{u,c}
+U_{sguck}+\varepsilon_{sguckr}.
\]

The planted components obey:

\[
\sum_s S_s=0,\quad
\sum_gG_{g|s}=0,\quad
\sum_uA_{u|gs}=0,\quad
\sum_cH_c=0,
\]

\[
\sum_cB_{u,c}=0,\qquad
\sum_uB_{u,c}=0\text{ within each group}.
\]

The constraints define one balanced reference decomposition. They do not say
that real populations are balanced or that these terms have psychological
meaning.

## Estimands

### Balanced hierarchical projections

The stable score-space surface is decomposed into:

- society position;
- group-within-society position;
- author-within-group position;
- common condition response;
- author-by-condition response.

Two independent opportunity panels estimate stable cross-panel energy. Within
occasion stream contrasts estimate technical variance. Repeated opportunities
estimate transient opportunity variance.

### Symmetric zero path

For component \(j\), hold one planted basis fixed and evaluate:

\[
X_j(\lambda)=X_{\text{background}}+\lambda F_j.
\]

For a quadratic measurement functional \(T_m\), define:

\[
Z_{mj}(\lambda)
=
\frac{T_m(X_j(+\lambda))+T_m(X_j(-\lambda))}{2}
-T_m(X_j(0)).
\]

The symmetric path removes first-order background cross terms. Under correct
separation:

\[
Z_{jj}(\lambda)\propto\lambda^2,\qquad
Z_{mj}(\lambda)\approx0\quad(m\ne j).
\]

The log-log slope and off-diagonal leakage form the component's registered
zero signature.

### Coarse-graining flow

Independent author deviations should contribute to a group mean at order:

\[
E\|\bar A_g\|^2\propto n_g^{-1}.
\]

A group-common component should remain order \(n_g^0\). The same distinction
is tested between independent group deviations and society-common structure.
An intraclass-correlated author world is included to show that aggregation
does not remove shared structure.

### Projection-order assay

Let \(P_G\) and \(P_C\) be empirical group and condition conditional-mean
operators. The registered commutator is:

\[
\mathcal C_{G,C}Y=P_GP_CY-P_CP_GY.
\]

It should be negligible under a balanced product design. It may be nonzero
under author-dependent condition selection. A nonzero commutator is a
dependence/imbalance diagnostic, not a causal or psychological interaction.

### Non-identification assays

1. A persistent author response and a persistent schedule confound are
   generated with identical observations and must return
   `CAUSE_UNIDENTIFIED`.
2. A minority-by-near-kernel response follows:

\[
\eta_{\text{observable}}
\approx p\alpha\eta_{\text{individual}},
\]

where \(p\) is affected-author prevalence and \(\alpha\) is the fraction of
response energy visible to the frozen score operator.

## Frozen synthetic design

- 8 societies;
- 4 groups per society;
- 8 authors per group;
- 6 balanced conditions;
- 4 repeated opportunities;
- 2 technical streams;
- 6 score dimensions;
- 2 independent opportunity panels;
- Gaussian and standardized heteroskedastic \(t_5\) worlds;
- \(K=2,3,4\) recovery surfaces;
- symmetric amplitudes \(0,.125,.25,.5,1\).

## Registered discovery gates

These are method-development gates, not confirmation thresholds:

1. maximum algebraic reconstruction error `<= 1e-10`;
2. minimum K=4 stable-component mean recovery \(R^2\) `>= .80`;
3. minimum K=4 stable split-panel correlation `>= .80`;
4. every diagonal zero-path slope in `[1.8, 2.2]`;
5. maximum absolute off-diagonal zero-path leakage `<= .02`;
6. independent-author group-mean slope in `[-1.15, -.85]`;
7. group-common author-aggregation slope in `[-.15, .15]`;
8. independent-group society-mean slope in `[-1.15, -.85]`;
9. society-common group-aggregation slope in `[-.15, .15]`;
10. selection world reverses the naive author direction in at least 90% of
    repetitions and balanced standardization restores it in at least 90%;
11. balanced projection commutator is at most 10% of the raw selected-design
    commutator;
12. alias identity error `<= 1e-10` and classification is
    `CAUSE_UNIDENTIFIED`;
13. maximum minority-near-kernel identity relative error `<= .02`;
14. all output, seed, reconstruction, manifest, and inventory contracts pass.

Failure of a gate records a boundary. It does not license threshold tuning on
the same random panel.

## Interpretation boundary

A pass would show that the registered synthetic observation model supports a
multiscale component-identification calculus. It would not show:

- that society-scale residuals are literally zero;
- that all behavior is personal;
- that a recovered component is personality;
- that observational response is causal;
- that the same decomposition exists in real text;
- that a saturated author function generalizes to unseen conditions.
