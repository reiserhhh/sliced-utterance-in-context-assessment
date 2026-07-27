# V8 Adaptive Rank and Fixed Reference V3.7E Methodology Audit

Ruling: `PASS_WITH_CAVEATS`

This is an artifact- and method-level audit, not an external replication.

## Accepted

- The V3.7E content seal and V3.7D parent seal verified without drift.
- Reference, calibration, and evaluation authors were disjoint in all 960
  cells. Evaluation authors and scorer truth were unavailable to rank
  selection.
- The primary comparison paired fixed, adaptive, and oracle estimators on the
  same observations.
- Flat-spectrum rank was selected exactly in all 480 flat cells. Rank 8 was
  unchanged, while rank 12 and 16 closed their fixed-rank truth and NRMSE
  gaps.
- The session-permutation control selected rank 0 and returned AUC .500 in
  every world.
- The decaying-spectrum arm selected smaller effective ranks and never hit
  the rank-24 ceiling. The selector is therefore responding to predictable
  stable energy rather than merely copying the declared latent rank.
- Opportunity standardization, population-shift direction, and projected
  amplitude passed their frozen gates.
- The built-in and external RNG audits passed. The latter covered all
  partition, permutation-order, parent, and replicate streams omitted from
  the compact built-in ledger.

## Caveats

### The flat-spectrum selector problem is clean

The synthetic rank spectrum has an unusually sharp cutoff, 128 calibration
authors, and 48 observed coordinates. Exact rank recovery is a useful
mechanism check, not evidence that unknown rank will be selected exactly in
human text. Smooth spectra appropriately produced effective rank rather than
literal rank.

### The V3.7D reverse example remains valid but is not robust

V3.7E does not retract the mathematical existence of identity without
recovery. It shows that the registered rank-12 example was a controlled
fixed-rank misspecification. A claim that reverse separation is intrinsic to
the population would now be unsupported.

### External reference is incomplete for absolute scores

The context router is fitted only on 256 external-reference authors and then
frozen. However, the stable projection center is estimated on the 128
calibration authors. Difference scores and planted shifts are translation
invariant and therefore valid here, but the absolute score origin is not yet
fully independent of the calibration cohort. V3.7E supports fixed-reference
contrast transport, not a deployable external norm.

### Opportunity transport uses a planted interaction and repeated panels

The \(B_u z_c\) interaction is deliberately constructed so changing
opportunity can bias naive profiles. Eight panels estimate systematic drift;
this does not imply that standardized scoring has lower variance or better
accuracy from one short human session.

### Cohort-refit erasure is algebraic

Explicitly subtracting the target cohort mean must erase its mean shift. The
near-zero result is a construction control. The less tautological
router-only target refit retained `.182` of the projected movement and should
be reported alongside it.

### The population shift is favorable

The shift follows the first planted author direction and is tested in the
rank-8 flat arm. Arbitrary, weak, orthogonal, sparse, nonlinear, or
out-of-support movements were not tested.

### One DGP family and one scale regime

The confirmation uses low-rank linear author and author-by-context operators,
fixed total author RMS, categorical routing, and a common reference
population before the planted shifts. Reference-mixture changes, anisotropic
noise, unknown context support, MNAR opportunity, and nonlinear operators may
alter the result.

### Identity remains a matching metric

Hard-neighbor AUC and top-1 mean cross-session same-author matching inside a
declared candidate set. They do not establish personality, psychological
identity, deanonymization, or clinical validity.

### No single-author error theory

The outputs remain population-level technical metrics. Event uncertainty,
reference-panel uncertainty, rank-selection uncertainty, confidence-region
coverage, and minimum detectable change are deferred to V3.7F.

## Final ruling

The canonical decision is accepted within its registered synthetic boundary.
V3.7E closes the strongest alternative explanation for the V3.7D rank-12
result: fixed estimator capacity. It also demonstrates a bounded
fixed-reference contrast mechanism.

The next mathematical closure should be V3.7F: replace the calibration-cohort
score origin with a fully external zero, then estimate nested uncertainty
from event sampling, reference sampling, and rank selection. Real repeated
text should remain a later existence test, not be mixed into that estimator
calibration experiment.
