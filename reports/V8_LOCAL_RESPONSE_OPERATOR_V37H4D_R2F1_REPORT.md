# V8 V3.7H.4D R2F.1 Local Response Operator

Date: 2026-07-27

Machine decision:
`V8_R2F_STOP_NO_LOCAL_TANGENT_CANDIDATE`

Scientific decision:
`VALID_LOCAL_SEARCH / NO_MATERIAL_STABLE_CANDIDATE / FREEZE_ROUTE`

Status: fresh-seed synthetic detector-geometry discovery. No fresh
confirmation is authorized because no candidate passed.

## Question

R2E.2 showed that the frozen detector responds strongly to one known
halo-normal direction and is practically insensitive to one random tangent
family. R2F.1 asked whether a broader, macro-coordinate-constrained local
chart contains:

- a stable first-order tangent response;
- a curvature-only response;
- or only an approximate local kernel.

This is a detector-mechanism question. It is not a search for a named
personality factor.

## Geometry

The double-centered ambient space has:

\[
(64-1)(16-1)6=5670
\]

dimensions. Each parent received 24 shared-seed random probes. The probes
were projected into the kernel of a standardized nine-coordinate numerical
Jacobian. Four deterministic orthogonal axes were retained.

For local coordinates \(x\in\mathbb R^4\):

\[
Q_i(x)=
\cos\theta C_i+
\sin\theta
\left[
\cos\|x\|H_i+
\sin\|x\|
\frac{U_ix}{\|x\|}
\right].
\]

The chart exactly preserves unit norm and halo share `.01`; parent-specific
residual information is subsequently matched exactly.

Formal geometry-only preflight:

- 80 parents;
- 3,600 geometries;
- zero detector outcomes;
- maximum Jacobian-kernel residual `1.74e-15`;
- maximum finite-step macro drift `.03637 SD < .05`;
- every basis and interaction hash later reproduced in the formal run.

## Formal discovery

- 40 parents in each of Gaussian and heteroskedastic \(t_5\);
- 45 geometries per parent;
- 32 independent outcomes per geometry;
- 115,200 frozen 99-sign/Holm detector evaluations;
- A/B halves of 16 outcomes;
- 20,000 noise-stratified parent-block bootstrap draws.

All generation, source-lock, seed, CRN, row, geometry, information,
preflight-equivalence, numeric, manifest, and inventory checks passed.

## Controls

| Arm | Noise | \(J\) | interval lower | interval upper |
| --- | --- | ---: | ---: | ---: |
| normal `.09` | Gaussian | .192767 | .184866 | .200668 |
| normal `.09` | \(t_5\) | .188256 | .179120 | .196913 |
| registered null `.4` | Gaussian | -.0000378 | -.000252 | .000214 |
| registered null `.4` | \(t_5\) | .0000252 | -.000202 | .000290 |

The detector remained highly sensitive to the known normal direction and
again practically null for the unchanged registered tangent control.
Failure to find a new candidate therefore cannot be reduced to general
detector failure.

## First-order operator

The A/B cross-fitted gradient operator had eigenvalues:

\[
.007104,\quad +.004046,\quad -.007302,\quad -.010290.
\]

At the registered `.2` endpoint:

\[
S_g=.2^2\lambda_{\max}=.000284.
\]

Its bootstrap lower bound was `.000140`, but materiality failed:

\[
.000284 < .005.
\]

The 90% bootstrap principal-angle upper was `67.5 degrees`, also failing the
registered `45 degrees` stability gate. A weak nonzero finite-sample
direction is therefore not a promotable response axis.

For scale, the observed strength is only 5.7% of the practical candidate
threshold. The descriptive 97.5% bootstrap quantile was `.000723`, still
well below `.005`, but no prospective practical-null claim was registered
for the entire selected chart.

## Curvature operator

The A/B cross-fitted curvature-operator eigenvalues were all negative:

\[
-.0703,\quad -.7730,\quad -1.9416,\quad -3.1965.
\]

The registered curvature strength was:

\[
S_H=-.000304,
\]

with lower bound `-.000707` and 90% principal-angle upper
`59.9 degrees`.

This is not negative physical curvature. \(S_H\) is a cross-product estimate
of nonnegative latent curvature energy; finite-sample A/B disagreement may
produce negative eigenvalues. The correct interpretation is that no
positive stable curvature energy was resolved.

The operator direction maximizes an estimate of
\(E\|H_iv\|^2\), while the final scalar strength uses
\(E(v^\top H_iv)^2\). They are related but not identical. The result tests
the frozen candidate rule, not every conceivable second-order functional.

## Local quadratic adequacy

The A/B residual cross-product MSE estimate was `-.000269`; its one-sided
upper bound was `.0000488`, below the `.0004` gate.

The negative point is retained as an unbiased cross-product fluctuation. It
does not mean negative prediction error. The supported statement is only
that the data did not reveal material failure of the local quadratic
approximation over `|x|<=.2`.

## Decision and theory update

No candidate simultaneously met:

- strength above `.005`;
- lower bound above zero;
- principal-angle upper at most 45 degrees;
- quadratic adequacy.

Therefore:

`V8_R2F_STOP_NO_LOCAL_TANGENT_CANDIDATE`.

R2E.2 and R2F.1 together support the following local decomposition for the
registered synthetic detector:

\[
\text{response}
=
\text{strong known normal channel}
+
\text{registered tangent practical kernel}
+
\text{no material stable mode in the tested 4D constrained chart}.
\]

This sharpens the R2D resource STOP. The current simulator's detector power
is largely organized by movement across its known geometry margin rather
than by arbitrary within-shell rotation.

## Mandatory boundary

The result does not show:

- that all 5,670 tangent dimensions are null;
- that unknown high-dimensional or dynamic variables do not exist;
- that higher-order, nonlocal, or differently constrained responses vanish;
- that the current detector is a sufficient representation of SUICA;
- anything about personality, semantics, real text, psychology, diagnosis,
  causality, intelligence, or clinical use.

The current synthetic tangent-search route is frozen. The same outcomes may
not be reused to increase dimension, rotate probes, change step size, or
lower candidate gates. Since no direction was frozen, fresh confirmation is
not run.

## Next admissible direction

Do not continue mining this detector. The next high-value test must change
the evidence source rather than the search parameters:

- apply the already frozen geometric observables to independent real-text
  or fixed-condition data;
- test whether reproducible author/condition response structure exists
  before assigning psychological meaning;
- if a real observable is found, construct a new synthetic world that plants
  that mechanism explicitly and then test identifiability.

## Artifacts

- `docs/V8_LOCAL_RESPONSE_OPERATOR_V37H4D_R2F_PLAN.md`
- `docs/V8_LOCAL_RESPONSE_OPERATOR_V37H4D_R2F1_CORRECTION.md`
- `configs/v8_local_response_operator_v37h4d_r2f1_discovery.json`
- `suica_core/v8_local_response_operator.py`
- `scripts/run_suica_v8_local_response_operator_v37h4d_r2f.py`
- `scripts/analyze_suica_v8_local_response_operator_v37h4d_r2f.py`
- `results/v8_local_response_operator/r2f1_geometry_preflight_3600geometries_20260727/`
- `results/v8_local_response_operator/r2f1_discovery_115200outcomes_20260727/`
- `results/v8_local_response_operator/r2f1_discovery_analysis_20260727/`

