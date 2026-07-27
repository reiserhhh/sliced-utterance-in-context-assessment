# V8 V3.7H.4D R2E.1 Corrected Injection Discovery

Status: prospective corrected protocol; no R2E.1 outcome inspected at
registration.

R2E.1 retains every estimand, magnitude, threshold, crossover rule, sample
size, detector setting, and bootstrap rule from R2E. Its only scientific
change is correction and direct verification of the all-author core RNG
path.

## Correction

The frozen builder selects halo-author support before drawing the core.
Therefore, both the baseline and zero-halo core reconstruction use:

```text
halo_author_support = 64
geometry_seed = identical
```

even when `halo_lambda=0`. This ensures the same support-selection RNG path
and hence the same core \(C\).

For every baseline and normal geometry, R2E.1 also calls the frozen builder
directly at the theoretical halo share:

\[
\lambda_{z,\tau}=\sin^2(\theta+z\tau),
\]

normalizes both test-author tensors, and requires:

\[
\left\|
\frac{Q^{constructed}}{\|Q^{constructed}\|}
-
\frac{Q^{builder}}{\|Q^{builder}\|}
\right\|_F
\le 10^{-10}.
\]

Failure makes the protocol invalid before scientific interpretation.

Before generating formal outcomes, all 80 formal-seed parents run a
geometry-only preflight. It additionally requires:

- raw baseline reconstruction and pre/post-orthogonalization axis drift
  below `1e-12`;
- information-matched normal tensors below `1e-10` relative error;
- matching-scale error below `1e-12`;
- every registered operator coordinate below `1e-10` relative error;
- endpoint mean whitened leakage at least `.025`, endpoint-minus-opposite
  leakage at least `.015`, and endpoint leakage inside the frozen R2C
  reference range `[.030,.065]` in both noise families.

Formal outcome generation is prohibited unless this preflight passes.

## Frozen experiment

- 40 fresh parents per noise family;
- Gaussian and heteroskedastic \(t_5\);
- 13 geometries per parent;
- 32 outcomes per geometry;
- 33,280 detector outcomes;
- normal `tau={.03,.06,.09}`;
- tangent `phi={.1,.2,.4}`;
- primary endpoints `.09` and `.4`;
- identical \(J\), \(\Delta V\), simultaneous intervals, and decision gates
  defined in
  `docs/V8_CONDITIONAL_HETEROGENEITY_INJECTION_V37H4D_R2E_PLAN.md`;
- new root seeds and a new output directory;
- no reuse of R2E outcomes for tuning.

## Interpretation

The original R2E output is retained as
`INVALID_POSITIVE_CONTROL_CORE_RNG_MISMATCH`. Only R2E.1 may test detector
sensitivity to the intended normal and tangent geometries.

All claims remain limited to the registered synthetic detector mechanism.
