# V8 Response-Set Incidence Geometry Report

Status:

- executable affine gate:
  `V8_RESPONSE_SET_INCIDENCE_PLANTED_PASS`;
- independent methodological audit: `PARTIAL`;
- psychological, interpersonal, and real-text interpretation: `CLOSED`.

Canonical audited artifacts:
`results/v8_response_set_incidence/v1_final_audited_20260726/`.

## 1. Research question

The experiment asks whether an author can be represented as a
condition-indexed geometric object rather than one point, and whether
relations between two such objects can be estimated without confusing a
shared condition with an author-specific relation.

For author \(u\),

\[
f_u(z)=a_u+B_uz,\qquad S_u=f_u(\mathcal Z),
\]

\[
\Gamma_u=\{(z,f_u(z)):z\in\mathcal Z\}.
\]

Depending on the rank of \(B_u\), \(S_u\) is a bounded line, surface, or
volume. The lifted graph \(\Gamma_u\) retains condition identity.

Three quantities are kept separate:

\[
d_{uv}^{=}
=
\inf_z\|f_u(z)-f_v(z)\|,
\]

\[
d_{uv}^{\mathrm{free}}
=
\inf_{z,z'}\|f_u(z)-f_v(z')\|,
\]

and whole-map proximity,

\[
d_{uv}^{\mathrm{map}}
=
\left(
\|a_u-a_v\|_2^2+\|B_u-B_v\|_F^2
\right)^{1/2}.
\]

The first is a same-condition incidence. The second may be only a
cross-condition coincidence. In this affine V1, the third detects
near-equivalent response maps; it is not yet a population-calibrated
excess-incidence statistic.

## 2. Registered battery

The battery contains 21 pair worlds:

- same-condition crossing and coincident overlap;
- cross-condition-only crossing;
- parallel, near-miss, and three-dimensional skew relations;
- line, plane, and volume response images;
- private conditions, condition permutation, half shuffle, and
  observer-specific displacement;
- paired equal maps, a common-anchor line pencil, and nonintersecting
  direction-rich tangent segments.

Discovery, calibration, and confirmation use disjoint seed blocks. The run
contains 1,680 discovery, 3,360 calibration, 8,400 confirmation, and 12,600
noise-sensitivity pair simulations, plus 96 finite-scale dimension runs and
480 population-graph runs.

The first smoke exposed an estimand mismatch: graph F1 used pair-specific
map equivalence while cross-view stability used the raw common-condition
graph. This was corrected before confirmation so both graph gates refer to
the pair-specific map-equivalence graph. After the first full run, an audit
found that `private_conditions` relied on implicit `NaN` boolean conversion
for its expected-label columns. Labels were made explicit and the full
audited package was rerun without changing geometry, thresholds, or
classification rules.

## 3. Audited results

| Metric | Result | Frozen gate |
| --- | ---: | ---: |
| Same-condition incidence AUC | 1.000 | at least 0.90 |
| Free-image incidence AUC | 1.000 | at least 0.90 |
| Relation balanced accuracy | 0.9657 | at least 0.85 |
| Median finite-scale dimension error | 0.0863 | at most 0.25 |
| Median principal-angle error | 0.2147 degrees | at most 10 degrees |
| Paired map-equivalence graph F1 | 1.000 | at least 0.85 |
| Cross-view map-equivalence Jaccard | 0.9979 | at least 0.80 |
| False same-edge one-sided 95% upper bound | 0.000535 | at most 0.03 |
| Attack refusal rate | 1.000 | at least 0.90 |
| Rigid-distance invariance | 1.000 | at least 0.95 |
| Shared-anchor false excess run rate | 0.000 | at most 0.03 |

The least accurate clear confirmation templates were a 2D endpoint near miss
(0.890) and 3D skew lines (0.8975). These failures were refusals, not false
same-condition edges.

The finite-scale estimator returned medians of 0.961 for a 2D line, 0.960
for a 3D line, 1.862 for a plane, and 2.779 for a volume. These are
engineering checks under correctly specified affine maps, not evidence that
real author sets have those dimensions.

The population examples expose why raw intersection cannot be called
pair-specific connection:

| World | Oracle raw edges | Predicted raw edges | Predicted map-equivalence edges |
| --- | ---: | ---: | ---: |
| Paired equal maps | 8 | 7.994 | 8 |
| Common condition anchor | 120 | 119.969 | 0 |
| Direction-rich tangent segments | 0 | 0 | 0 |

Every author in the common-anchor world passes through the same response at
the same condition. That produces a complete raw incidence graph but no
pair-specific map equivalence.

## 4. Identified operating boundary

At noise standard deviation 0.01, clear-world correctness was 0.986; at the
registered 0.03 it was 0.964. From 0.06 onward, all ordinary worlds crossed
the residual/stability boundary and were refused.

This is a successful fail-closed result, but it also shows that the current
identified domain is narrow: dense shared conditions, correctly specified
affine maps, independent isotropic noise, and a low-noise regime. The AUC of
1.0 reflects a large separation between the fixed positive and negative
templates, not cross-template geometric generalization.

## 5. Theoretical upgrade supported

The experiment supports four changes to the SUICA mathematical object.

1. A person may be represented by a response set \(S_u\), and more safely by
   a lifted condition-response graph \(\Gamma_u\), rather than only a point.
2. Same-condition incidence, cross-condition coincidence, and whole-map
   similarity are different relations and must not share one score.
3. Relations are naturally population graphs or condition-indexed
   hypergraphs. A common condition can create many raw edges without creating
   pair-specific affinity.
4. Under noise, exact intersection should be replaced by an uncertainty tube
   and a refusal region.

Kakeya geometry is only a motivation: a zero-area set may still carry rich
direction and incidence structure. The finite affine battery does not test a
Kakeya set, a continuum of directions, zero-measure full dimension, or any
Kakeya theorem.

## 6. Independent-audit limits

The independent audit does not promote the executable `PASS` to a general
scientific pass:

- persistence across tube radii was not estimated;
- transversality rank, full principal-angle spectra, tangency order, and
  intersection dimension were not implemented;
- the current graph statistic is map equivalence and depends on the chosen
  condition-coordinate parameterization;
- graph and dimension worlds are deliberately easy planted templates;
- nonlinear paths, partial condition overlap, correlated or heteroscedastic
  noise, missing conditions, and consistent condition misregistration remain
  untested;
- the dirty repository manifest binds outputs to code hashes but is not a
  cryptographic preregistration seal;
- no real text, psychological label, compatibility outcome, or clinical
  variable was used.

## 7. Next mathematical gate

The next registered V2 should replace coordinate-dependent map distance with

\[
d_{\mathrm{map}}^2(u,v)
=
\mathbb E_{z\sim P_Z}
\left[
\{f_u(z)-f_v(z)\}^{\mathsf T}
\Sigma_\Delta(z)^{-1}
\{f_u(z)-f_v(z)\}
\right].
\]

For radius \(\epsilon\), define

\[
R_{uv}(z,\epsilon)
=
\mathbf 1
\left[
\|f_u(z)-f_v(z)\|_{\Sigma_\Delta(z)^{-1}}
\le \epsilon
\right].
\]

The pair-specific object should be persistence of \(R_{uv}\) across
independent views and radii, minus a condition-matched random-pair baseline.
V2 must add nonlinear curves and sheets, Jacobian-based transversality,
intersection dimension, partial overlap, correlated noise, condition
reparameterization attacks, and fresh geometric templates. Real-text or
psychological interpretation remains closed until that technical gate is
passed and an appropriate shared-condition dataset is available.
