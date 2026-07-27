# V8 V3.7H.4D R2E Conditional-Heterogeneity Injection

Status: prospective discovery protocol; no R2E outcomes inspected at
registration.

## Objective

R2D Gate-0 found too little pooled within-cell probability variance to
justify a posterior model. R2E distinguishes two explanations:

1. the generator did not plant meaningful within-cell individuality;
2. the registered detector cannot transmit individual geometry.

R2E deliberately injects paired geometry differences while holding the
parent world and scalar residual information fixed.

## Orthonormal frame

In the double-centered test-author-by-condition Frobenius space:

\[
\|C\|=\|H\|=\|H_1\|=1,\qquad
\langle C,H\rangle=
\langle C,H_1\rangle=
\langle H,H_1\rangle=0.
\]

Here \(C\) is the four-author core, \(H\) is an all-64-author halo, and
\(H_1\) is an independently drawn all-author tangent direction. Let:

\[
\theta=\arcsin\sqrt{.01}=.1001674.
\]

The baseline is:

\[
Q_0=\cos\theta C+\sin\theta H.
\]

## Paired injections

Every parent receives both signs at every nonzero magnitude.

Normal positive control:

\[
Q^N_{\tau,z}
=
\cos(\theta+z\tau)C+\sin(\theta+z\tau)H,
\quad
\tau\in\{.03,.06,.09\},\ z\in\{-1,+1\}.
\]

At \(\tau=.09\), the two halo shares are approximately `.00010` and
`.03573`, crossing the known R2C halo frontier.

Tangent hidden-geometry test:

\[
Q^T_{\phi,z}
=
\cos\theta C+
\sin\theta\{\cos\phi H+z\sin\phi H_1\},
\quad
\phi\in\{.1,.2,.4\}.
\]

It holds halo share `.01`, all-author support, and unit norm exactly. Every
candidate is subsequently scaled to the same parent-specific residual
information target. Each parent therefore has 13 geometries: one baseline
plus six normal and six tangent states.

## Fresh design

- Gaussian and heteroskedastic \(t_5\);
- 40 fresh parents per noise, 80 total;
- 13 geometries per parent;
- 32 independent outcome-panel pairs per geometry;
- 33,280 detector outcomes;
- unchanged 99-sign CRC/low-rank/HC/Holm detector;
- the same opportunity/noise/sign streams across all 13 geometries within
  one `parent x replicate` as common random numbers;
- independent streams across parents and replicates;
- 20,000 parent-block bootstrap draws.

This is discovery. Any GO requires an independently seeded confirmation with
80 parents per noise.

## Estimands

For paired outcomes \(Y_{i+r},Y_{i-r}\), define
\(D_{ir}=Y_{i+r}-Y_{i-r}\). Direction sensitivity is:

\[
J_a=\frac14E_i[(p_{ia+}-p_{ia-})^2],
\]

estimated without truncation by:

\[
\widehat J_a
=
\frac1{4n}\sum_i
\left[
\bar D_{ia}^{\,2}
-
\frac{s^2_{D,ia}}R
\right].
\]

The side-mixture variance decomposes as:

\[
V_a
=
\operatorname{Var}_i\left(
\frac{p_{ia+}+p_{ia-}}2
\right)
+J_a.
\]

The midpoint component is corrected for replicate measurement variance.
The second estimand is \(\Delta V_a=V_a-V_0\). Thus \(J\) measures detector
sensitivity to a direction, while \(\Delta V\) asks whether that direction
creates useful base-level heterogeneity.

## Integrity gates

- frozen source hashes;
- complete parent, geometry, and outcome blocks;
- unique source streams and exact common-random-number pairing;
- frame norms and inner products within `1e-10`;
- author and condition marginals within `1e-10`;
- theoretical versus measured halo share within `1e-10`;
- all-author nonzero energy support;
- information matching relative error at most `1e-6`;
- finite registered geometry coordinates.

Information-matching scale ratios outside `[.9,1.1]` do not invalidate the
run, but prevent a pure-angle interpretation.

## Frozen endpoints and decisions

Primary endpoints are normal `tau=.09` and tangent `phi=.4`. Smaller
magnitudes describe dose shape only and cannot be selected post hoc.

Nine endpoint bounds share one one-sided simultaneous max-deviation family:
normal/tangent \(J\) and \(\Delta V\) in both noises, plus pooled tangent
\(\Delta V\).

`DISCOVERY_GO_HIDDEN_TANGENT_GEOMETRY` requires:

1. normal \(J\) lower bound above `.005` in both noises;
2. tangent \(J\) lower bound above `.005` in both noises;
3. pooled tangent \(\Delta V\) lower bound above `.005`;
4. positive tangent \(J\) and \(\Delta V\) points in both noises;
5. all information-scale ratios inside `[.9,1.1]`.

`NORMAL_ONLY_KNOWN_MARGIN` requires the normal positive control and tangent
\(J\)/\(\Delta V\) upper bounds at most `.005`.

`PARTIAL_TANGENT_SUBTHRESHOLD` records normal passage plus positive but
sub-threshold tangent evidence. `PARTIAL_TANGENT_AMPLITUDE_COUPLED` records
a tangent GO whose information-matching scale leaves `[.9,1.1]`.

If both normal endpoint upper bounds are at most `.005`, the positive control
fails and hidden-geometry interpretation stops. All remaining valid patterns
are `INCONCLUSIVE_NO_TUNING`.

## Claim boundary

R2E can establish sensitivity of the registered synthetic detector to
controlled geometry. It cannot name a psychological factor, establish
personality, validate real text, or support diagnostic or clinical use.
