# V8.3.7G Independent Mathematical Audit

Ruling: `PASS_WITH_CAVEATS`

The canonical PASS is accepted only for the frozen NMSE-based synthetic
profile experiment. No blocking arithmetic error, truth leakage, panel
overlap, or pseudoreplication was found.

## Accepted

- The selector met the registered NMSE gates: exact-rank excess upper bound
  -0.0406, dense reduction lower bound 28.51%, broken reduction lower bound
  20.14%, and worst-world regret upper bound 0.01191.
- Reference, calibration, interval-fit/radius, and evaluation authors were
  disjoint. Evaluation truth was scorer-only.
- Coverage intervals bootstrapped 60 repetition-level proportions rather
  than treating all evaluation authors as independent experiment
  repetitions.
- For 192 radius authors, order 188 gives achieved confidence 0.96554 for a
  one-sided 95% content tolerance radius.
- The strict nonparametric statement concerns only the mapped proxy-error
  radial distribution, conditional on its fitted map.
- Latent-error coverage of 0.957-0.966 is empirical, marginal, and
  model-assisted in four Gaussian planted worlds.
- State-alias and reference-shift refusal worked as a registered
  metadata-driven policy.
- Score plus unresolved reconstructed the input within 1.55e-15.
- Seed uniqueness, row counts, selection/oracle bookkeeping, decision
  arithmetic, and artifact hashes reconciled.

## Major caveats

### NMSE/NRMSE conflict

The implementation computes NMSE without a square root, while two sealed
prose documents say NRMSE. The PASS can be released only as an NMSE result.
On a square-root normalized-error scale, the dense/broken point reductions
are approximately 15.71% and 10.94%, so an NRMSE gate would not pass.

### Local rather than publicly anchored prospectivity

The seal is internally hash-consistent and local chronology places it before
the confirmation output. However, the repository was dirty and the V3.7G
files were untracked. The experiment lacks an independent public timestamp.

### Weak shift transport control

All 60 budget-256 reference-shift cells selected `hard_r48`. The resulting
identity operator makes direction and amplitude equal to one algebraically,
so this check contributes little evidence about nontrivial transport.

### Marginal uncertainty result

The four world-specific coverage intervals are individual 95% intervals, not
a simultaneous family-wise statement. Informative precision overcovered at
0.9981, showing poor efficiency outside the homoskedastic core.

### Scope

Reconstruction is an algebraic reversible decomposition, not proof of
psychological information conservation. Nothing establishes real-text
structure, personality meaning, individual interpretation, clinical
validity, automatic state/shift detection, or cross-budget filtration
coherence.

## Next mathematical question

Using genuinely nested event prefixes
\(m\in\{32,64,128,256,512\}\) for the same authors under frozen
\(P_0,Q_0\), test whether the observable reliability-spectrum estimator has:

1. out-of-sample approximate martingale coherence;
2. monotone risk and uncertainty contraction;
3. reversible unresolved-channel conservation;
4. no use of latent truth for selection.

This should be a separately named, prospectively sealed experiment. It must
use explicit metric equations and must not reuse V3.7G's canonical seed.
