# V8 V3.7H.4C W0 Calibration Report

Date: 2026-07-26

Decision:
`V8_MISSPECIFICATION_W0_CALIBRATION_V37H4C_CALIBRATED`

Status: prospective internal calibration; not a sealed confirmation.

## Purpose

V3.7H.4 observed 2/100 false refusals in each additive control. Those point
estimates were below .05, but their one-sided upper bounds were .06162 and
failed the frozen certification gate.

H.4C tested a single question with fresh simulations:

> Is the unchanged H.4 detector's familywise false-refusal probability below
> .05 under each registered additive noise generator?

The 200 prior H.4 W0 trials were not reused.

## Frozen detector

The source lock passed for:

- the H.4 config;
- the multiscale generator dependency;
- the misspecification module;
- the H.4 runner containing `_evaluate_cell`;
- 99 permutations;
- Holm familywise alpha .05.

H.4C directly imported the locked H.4 cell evaluator. No diagnostic,
threshold, rank candidate, panel split, or generator parameter was optimized.

## Design

- 1,000 repetitions per noise mode;
- Gaussian and heteroskedastic standardized \(t_5\) noise;
- 2,000 additive control cells;
- 4,000/4,000 unique world and diagnostic seeds;
- one-sided exact-binomial tail alpha .025 per noise mode;
- simultaneous target: both upper bounds below .05.

The frozen count rule for \(n=1000\) was:

- 0-36 refusals: `CALIBRATED`;
- 37-64: `INCONCLUSIVE`;
- 65 or more: `MISCALIBRATED`.

## Results

| Noise | False refusals | Rate | Simultaneous one-sided interval | CRC triggers | Low-rank triggers | Gain triggers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Gaussian | 16/1000 | .016 | [.00917, .02585] | 9 | 7 | 0 |
| Heteroskedastic \(t_5\) | 30/1000 | .030 | [.02033, .04255] | 22 | 8 | 0 |

Both upper bounds were below .05. All integrity and provenance checks passed:

- detector source lock;
- row count;
- seed uniqueness;
- numeric integrity;
- frozen count boundaries;
- run manifest;
- artifact inventory.

The heavier-tailed world produced more CRC-triggered false refusals. This
shows that calibration depends on the registered noise family. The held-out
gain diagnostic was conservative in W0, but zero triggers do not separately
establish its power or universal calibration.

## Combined H.4/H.4C conclusion

The H.4 frozen machine decision remains
`REFUTED_OVERCONFIDENT_ADDITIVE`. It cannot be rewritten after the fact.

H.4C resolves the scientific uncertainty that caused that STOP:

> The unchanged 99-permutation detector is calibrated below a 5% familywise
> false-refusal rate under the two registered additive synthetic generators.
> Combined with H.4, it has high sensitivity to the registered planted
> cross-panel low-rank residual structures while controlling false refusal in
> the registered additive controls.

This is a combination of H.4 discovery sensitivity and H.4C independent
specificity calibration, not a retroactive H.4 PASS.

## Boundaries

The result does not establish:

- calibration under arbitrary noise, missingness, imbalance, sample size, or
  reference-condition distribution;
- calibration of a detector with more permutations or different diagnostics;
- general nonlinear or full-rank misspecification awareness;
- zero-shot transport to an entirely unseen condition;
- causal localization;
- personality, psychological, diagnostic, clinical, or real-text validity.

The repository was dirty and the protocol was not sealed in git before
execution. The run manifest preserves exact hashes, but this remains an
internal prospective calibration rather than a third-party-verifiable
confirmation seal.

## Next question

The highest-value next adversary is a nonorthogonal interaction and reference-
measure frontier. H.4 double-centered every planted interaction, so it could
not test whether author scores change when the sampled condition distribution
changes.

The next study must distinguish:

\[
A_u^{(\pi)}
=
E_{\pi(c)}[Y_{uc}]
-E_{\pi(u),\pi(c)}[Y]
\]

under different condition reference measures \(\pi\), and must refuse
transport when positivity is absent or the author/interaction decomposition
is observationally aliased.

## Artifacts

- `docs/V8_W0_CALIBRATION_V37H4C_PLAN.md`
- `configs/v8_w0_calibration_v37h4c.json`
- `scripts/run_suica_v8_w0_calibration_v37h4c.py`
- `tests/test_v8_w0_calibration_v37h4c.py`
- `results/v8_misspecification_w0_calibration/v37h4c_calibration_1000rep_20260726/`
