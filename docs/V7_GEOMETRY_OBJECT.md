# V7 Primary Object: Relative Geometry Bundle

## Decision

V7's primary object is not a list of factor scores. W4/W4b found a stable,
distributed cross-view spectrum whose effective rank remains far above a small
factor inventory. A fitted flat factor model may remain a historical technical
probe, but it is not the V7 measurement object and must not supply V7 factor
names or psychological scores.

The frozen object is a relative geometry bundle:

\[
D_u \xrightarrow{O,E,A} x_u \xrightarrow{R,M,L}
\widehat{\mathcal G}_{u;R,O,E,A} =
\left(d_M(x_u,\ell_1),\ldots,d_M(x_u,\ell_m),r_M(x_u)\right),
\]

where `O` is a declared observation operator, `E` a frozen representation,
`A` author aggregation, `R` a reference population, `M` a regularized
Mahalanobis metric fit on `R`, and `L` an identifier-free landmark set chosen
from `R`. The emitted profile contains relative distances, not semantic
coordinates.

\[
d_M(x,y)^2=(x-y)^T(S_R+\lambda I)^{-1}(x-y).
\]

The bundle includes the feature transform, metric regularization, landmarks,
support radius, reference-population commitment, operator and representation
artifacts, and a refusal rule. It contains no raw text and no participant,
author or document identifiers.

The bundle ID is a canonical content hash of every score-defining field
(reference geometry, metric, landmarks, operator, representation, runtime and
support policy). Loading refuses a bundle whose contents no longer match its
ID. When farthest-point landmark selection encounters an unidentified
distance tie, the implementation retains the complete tied orbit and sorts
the emitted distance profile; input row order is never allowed to select one
otherwise indistinguishable reference member.

## What Is Invariant

If the same reference rows and target rows are transformed by a common
translation and orthogonal coordinate transform, the distance profile is
unchanged. The bundle is therefore coordinate-free in the limited sense that
its accepted output does not depend on naming a factor axis.

This does **not** imply invariance to:

- a different embedding model or runtime;
- a different language or domain;
- arbitrary nonlinear representation distortion;
- a changed reference population or opportunity design; or
- an unpaired target coordinate system.

Those cases require the V7 domain-transport protocol. A target corpus can
reuse the procedure, but it may not reuse PANDORA norms, landmarks or numeric
positions as if they were universal.

## Accepted Output and Refusal

`suica_core.v7_geometry.GeometryBundle` emits:

- `SU7-GEO-*` bundle ID;
- a landmark-distance profile;
- nearest/mean landmark distance and reference radius;
- `GEOMETRY_PROFILE_READY` or an explicit support refusal.

It refuses a row below its registered observation support or outside the
frozen reference-radius envelope. This is only a radial envelope check. It
does not estimate local density, detect holes inside a multimodal reference
distribution, or establish domain membership; a future deployment may add a
target-local density or conformal gate. A ready profile is a scoreable,
reference-relative text-geometry observation. It is not yet a personality,
emotion, clinical state, trait, or named factor.

## When a One-Dimensional Factor May Be Added

A future factor projection is permitted only after all of the following are
declared and pass on new data:

1. a symmetry breaker independent of post-hoc labels;
2. frozen reference, representation, operator and support policy;
3. author-disjoint technical replication;
4. repeated condition/occasion error estimation under the G-study/LST gate;
5. external convergence and discriminant evidence under the construct
   validation protocol.

Until then, the right primary object is relative geometry plus its support
conditions, not an arbitrary rotated factor coordinate.
