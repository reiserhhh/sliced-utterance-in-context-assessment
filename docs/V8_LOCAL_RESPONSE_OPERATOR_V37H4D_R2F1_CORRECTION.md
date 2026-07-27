# V8 V3.7H.4D R2F.1 Geometry-Gate Correction

Status: prospective correction before any formal R2F discovery run.

The R2F smoke stopped before formal execution because the legacy
R2E.2-style tangent-null control exceeded the new `.05 SD` finite-coordinate
gate in one saturated coordinate:

- absolute `operator_rho3` drift: `1.51e-6`;
- frozen baseline SD: `1.63e-5`;
- standardized drift: `.0927`.

The new four-dimensional Jacobian-kernel chart itself passed:

- maximum axis drift: `.00295 SD`;
- maximum mixed-corner drift: `.00139 SD`;
- maximum Jacobian-kernel residual: `2.71e-16`.

No smoke detector outcome was inspected to make this correction.

R2F.1 therefore applies the finite macro-coordinate drift gate only to the
new axis and corner geometries it is designed to validate. The legacy
registered-null arm is not a member of that chart. It remains unchanged as a
separate outcome sanity control and must again have \(J\) upper bounds at
most `.005`.

No step, dimension, coordinate scale, candidate gate, detector, sample size,
or bootstrap rule changes. R2F.1 uses fresh smoke and formal root seeds.

