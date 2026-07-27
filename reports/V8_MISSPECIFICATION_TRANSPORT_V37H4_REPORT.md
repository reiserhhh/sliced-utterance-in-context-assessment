# V8 V3.7H.4 Misspecification and Transport Report

Date: 2026-07-26

Frozen machine decision:
`V8_MISSPECIFICATION_TRANSPORT_V37H4_REFUTED_OVERCONFIDENT_ADDITIVE`

Scientific decision:
`PARTIAL_DETECTS_NOT_LOCALIZES_CALIBRATION_UNRESOLVED`

Confirmation status: not sealed and not run.

## Research question

V3.7H.4 deliberately fitted the additive V3.7H.3 coordinate system to
synthetic worlds containing omitted nonlinear, latent-hierarchical, or
persistent opportunity structure. The valid question was:

> Can observation-only diagnostics refuse the additive interpretation before
> a saturated observed-cell decomposition is mistaken for a transportable
> author response?

The experiment did not test a personality construct or a real-text system.

## Design

Four registered worlds were used:

1. W0 additive positive control;
2. W1 nonlinear author-by-condition interaction;
3. W2 author-correlated non-ergodic opportunity process;
4. W3 unobserved subgroup-by-condition hierarchy.

The frozen design used 256 authors, 16 conditions split into 8 train, 4
calibration, and 4 test conditions, 4 opportunity panels, nested
\(K=2,4,8\) prefixes, 6 score dimensions, and Gaussian or
heteroskedastic \(t_5\) noise.

Rank was selected on panels 1-2. Panels 3-4 supplied the final residual
replication and anchored held-out author-by-condition cell transport test.
The three diagnostics were:

- cross-panel residual correlation (CRC);
- low-rank residual concentration;
- held-out structured-predictor gain.

Their permutation p-values were Holm-adjusted at familywise alpha .05.
Any rejection returned `MODEL_INADEQUATE_CAUSE_UNIDENTIFIED`.

Integrity:

- 100 repetitions per registered cell;
- 1,400 total world/noise/effect cells;
- 16,800 component-recovery rows;
- 4,200 residual-prefix rows;
- 7,000 rank-selection rows;
- 2,800/2,800 unique RNG seeds;
- run manifest and artifact inventory passed;
- maximum operation gap \(7.27\times10^{-16}\);
- maximum response/opportunity alias identity error 0;
- full repository regression: 565 tests passed.

## Additive positive control

Main-component recovery and split-panel stability were strong. The minimum
simultaneous lower bounds were:

- K=4 recovery \(R^2=.9933\);
- K=4 split-panel correlation \(r=.9868\).

CRC and held-out gain were correctly centered near zero:

| Noise | Mean CRC | 90% CRC interval | Mean normalized gain |
| --- | ---: | ---: | ---: |
| Gaussian | -.00221 | [-.00444, .00002] | -.00071 |
| Heteroskedastic \(t_5\) | -.00290 | [-.00574, -.00005] | -.00056 |

Nevertheless, each noise mode produced 2 false refusals in 100 repetitions.
The registered one-sided 95% binomial upper bound was .06162, above the
required .05. Three false refusals came from the low-rank test and one from
CRC. The gain test caused none.

The frozen W0 gate therefore failed.

This failure means:

\[
\text{the experiment did not prove }
p_{\mathrm{false-refusal}}<.05.
\]

It does not mean:

\[
\text{the experiment proved }
p_{\mathrm{false-refusal}}>.05.
\]

The observed point estimate was 2%. If the true rate were 5%, observing at
most two refusals in 100 trials would still have probability .1183. The
registered 100-repetition design was therefore too weak to certify a strict
upper bound below .05 reliably.

The result cannot be rescued post hoc by pooling noise modes, changing the
interval, or relaxing the gate.

## Planted misspecification sensitivity

All W1, W2, and W3 cells were refused in 100/100 repetitions at both the 5%
and 20% planted effect shares under both noise modes.

At the registered strong effect share of .20:

- minimum detection lower bound: .97049;
- minimum recoverable-gap closure lower bound: .93252;
- minimum mean CRC: .88189.

Mean gap closure at .20 ranged from .9360 to .9874. This establishes high
sensitivity to the registered stable residual structures.

The result is narrower than a general misspecification theorem:

- W1 is a low-dimensional bilinear-tanh generator;
- W3 is planted rank two and rank two is in the candidate set;
- both align substantially with the SVD-based structured alternative;
- double centering prevents the planted interaction from contaminating the
  registered main effects.

The experiment therefore shows that a deliberately omitted, cross-panel
replicating low-rank structure can be detected. It does not show that every
unknown nonlinear or hierarchical structure can be detected.

## Persistent opportunity structure

W2 was refused in every repetition. Its K=8/K=2 cross-panel residual-energy
ratio remained approximately one:

- minimum registered ratio: .99863.

Additional opportunities therefore did not remove the planted persistent
component. This is a valid counterexample to the idea that opportunity
replication automatically eliminates every non-author source.

However, the same observations can be labeled either persistent opportunity
structure or stable author response. Their maximum identity error was zero.
The data cannot identify which label is causal.

The `specific_causal_attribution=False` field is a governance rule encoded in
the implementation. Its zero attribution rate is not an independently learned
causal classifier.

## Transport boundary

The final test conditions were held out for target authors, but anchor authors
provided information for those conditions. The supported object is therefore:

> anchored held-out author-by-condition cell transport.

It is not zero-shot transport to an entirely unseen condition.

## Decision

The frozen machine status remains
`REFUTED_OVERCONFIDENT_ADDITIVE` because the preregistered W0 false-refusal
gate failed.

The scientific interpretation is narrower:

> V3.7H.4 detects the registered planted cross-panel residual structures and
> refuses causal localization, but it has not yet certified false-refusal
> probability below 5%. Sensitivity is supported; general calibration and
> general misspecification awareness remain unresolved.

No personality, psychological, diagnostic, clinical, or real-text claim is
opened.

## Next registered step

Run an independent W0-only calibration study with new seeds. Do not reuse the
200 W0 trials in this discovery.

The calibration protocol should:

- keep the current 99-permutation detector, three diagnostics, Holm alpha
  .05, rank-selection process, and strict `<.05` target unchanged;
- use 1,000 repetitions per noise mode;
- apply simultaneous one-sided 97.5% binomial bounds across the two noise
  modes;
- return `CALIBRATED`, `MISCALIBRATED`, or `INCONCLUSIVE`;
- freeze an exact-binomial power table before execution;
- leave all diagnostic-specific rates descriptive only.

Changing permutation count or diagnostic thresholds would define a new
detector and require a new calibration.

## Post-run calibration update

The prospective H.4C study subsequently ran 1,000 fresh W0 repetitions per
noise mode with the unchanged detector:

- Gaussian: 16/1000, simultaneous upper .02585;
- heteroskedastic \(t_5\): 30/1000, simultaneous upper .04255.

H.4C passed its independent calibration gate. This resolves the scientific
calibration uncertainty but does not rewrite the frozen H.4 machine STOP.
See `reports/V8_W0_CALIBRATION_V37H4C_REPORT.md`.

## Artifacts

- `docs/V8_MISSPECIFICATION_TRANSPORT_V37H4_PLAN.md`
- `configs/v8_misspecification_transport_v37h4.json`
- `suica_core/v8_misspecification_transport.py`
- `scripts/run_suica_v8_misspecification_transport_v37h4.py`
- `tests/test_v8_misspecification_transport_v37h4.py`
- `results/v8_misspecification_transport/v37h4_discovery_100rep_20260726/`
