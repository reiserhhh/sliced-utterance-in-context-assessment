# V8 V3.7H.4C Independent Calibration Audit

Date: 2026-07-26

Ruling: `CALIBRATED_WITH_REGISTERED_WORLD_BOUNDARY`

This is a post-run independent audit, not a sealed confirmation.

## Accepted

- The detector source and H.4 config hashes match the frozen discovery
  implementation.
- The H.4C runner calls the same `_evaluate_cell`.
- The prior H.4 W0 trials were not pooled into calibration.
- Both registered noise modes used 1,000 fresh repetitions.
- One-sided alpha .025 per noise mode provides Bonferroni simultaneous
  coverage of at least .95.
- Both registered upper bounds are below .05.
- The `CALIBRATED` decision follows the prospective count rule.

## Interpretation

H.4's 2/100 result reflected insufficient certification resolution, not
demonstrated detector inflation. H.4C supplies the missing specificity
calibration for the exact detector.

The combined evidence is:

1. H.4 detects all registered planted cross-panel structured alternatives;
2. H.4C controls false refusal below .05 in the two registered additive
   controls.

H.4 itself remains a frozen STOP. H.4C is a new calibration result and does
not retroactively change that machine decision.

## Important limits

- The 99-permutation p-values are discrete. Holm rejection effectively
  requires a minimum raw p-value of .01.
- Heavy-tail false refusals were driven mainly by CRC, so noise-family
  dependence remains material.
- The H.4 alternatives are structurally favorable to low-rank diagnostics.
- Source locking checks the H.4 run manifest's existence rather than its hash;
  direct config and detector code hashes still lock the actual evaluator.
- The dirty repository and absence of a pre-run git seal prevent a formal
  confirmation claim.

## Allowed claim

> The unchanged V3.7H.4 99-permutation detector is calibrated below a 5%
> familywise false-refusal rate under the registered balanced additive
> Gaussian and heteroskedastic standardized \(t_5\) synthetic generators.

## Prohibited claims

- arbitrary-distribution calibration;
- general misspecification detection;
- zero-shot unseen-condition transport;
- causal, personality, psychological, diagnostic, or clinical inference;
- real-text validity;
- a retroactive H.4 PASS.

## Next audit target

Test non-double-centered and out-of-family interactions under changing
condition reference measures, positivity violations, full-rank diffuse
effects, minority-local effects, and near-kernel effects. The system must
separate score transport from cause attribution and must return refusal when
reference support is insufficient.
