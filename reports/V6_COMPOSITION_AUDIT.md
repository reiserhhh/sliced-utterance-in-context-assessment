# V6 Composition Audit

Date: 2026-07-13. Verdict: **synthetic measurement machinery conditionally passes;
psychological trait interpretation remains unlicensed**.

## Evidence composition

- Core W0-W8 current-hash matrix: 76 rows, all `pass`; code hash
  `39003065be921eb4391be9ef2b6994946eefaee9ea4d159bf68036aa3bc11d13`.
- P0-P6 full falsification: all seven scenarios detected at max-T-adjusted
  `p=.0005`; congruence `.967-.995`. The historical `power=false` was an invalid
  Wilson calculation across seven heterogeneous scenarios. It is replaced by a
  repeated-alternative power assay: 200/200 detections in every scenario, Wilson lower
  bound `.981`.
- P7-P10: P8/P9/P10 pass their synthetic gates. P7 cross-lag coupling fails in the
  default sparse observed world despite oracle recovery; it is not promoted.
- Opportunity/dynamics full: all eight gates pass. Observed opportunity recovers `B_u` at
  `r=.931`; own held-out MSE `.158`, stranger MSE `.310`. Hidden opportunity reduces
  recovery to `.575` and raises own MSE to `1.346`.
- Individual dynamics under repeated excitation: coupling/inertia matrix relative error
  `.080`, recovery half-life relative error `.064`; own held-out prediction beats a
  stranger operator. Single-session author dynamics are refused.
- Measurement-error full: all twelve gates pass after disjoint fit/calibration/focal
  conformal calibration. At 16 occasions, RMSE `.024`, coverage `.967`, MDD `.076`.
- Scorer and window perturbation gates pass: small scorer perturbations preserve the
  subspace; large drift is detected; dynamics are refused below four windows.
- Software suite: 127/127 passed in the terminal regression run.
- Final adversarial closure: 12/12 gates pass over 500 repetitions. Irregular-time,
  opportunity-error, nonlinear/time-varying, crossed-interaction, and sparse-coupling
  worlds are summarized in `V6_ADVERSARIAL_CLOSURE_REPORT.md`.

## What composes

The following procedural chain is supported in planted worlds:

1. freeze a reference distribution and target condition distribution;
2. represent structural opportunity separately from zero response;
3. estimate condition/opportunity baseline outside the focal response;
4. estimate an author response operator only under full-rank repeated excitation;
5. validate on held-out fixed conditions and compare with matched strangers;
6. attach calibrated uncertainty and refuse unsupported dynamics.

## What does not compose

- A stable path coordinate plus a stable author level does not automatically become a
  personality dimension.
- Mean-kernel dimensionality does not establish questionnaire-independent personality.
- Oracle cross-lag recovery does not license sparse-text cross-factor coupling.
- Cross-corpus comparisons of different people do not establish same-person transfer.
- A single long document does not establish an author-level motion style.

## Final missing experiment

Use the same participants in free and fixed conditions on at least three occasions.
Record prompt/turn boundaries, length, quotation/list/code/numeric affordance, and
partner input. Fit `a_u` and `B_u` on discovery occasions; evaluate fixed-condition
prediction, matched-stranger delta, projector invariance, recovery parameters, and
calibrated retest on an untouched occasion. Until then SUICA V6 is a reproducible text
path and author-by-context analysis framework, not a validated personality theory.
