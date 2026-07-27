# V8 Blind Junction Localization V3.7B Report

Canonical engine decision: `V8_BLIND_JUNCTION_LOCALIZATION_V37B_PASS`

Scientific status:
`SYNTHETIC_REGISTERED_SIGNATURE_LOCALIZATION_PASS__OPEN_WORLD_CLOSED`

Independent methodology decision: `PASS_WITH_CAVEATS`

## Question

V3.7B removed the oracle junction window used by V3.7A. A locator received
only a two-dimensional trajectory in its observed order. Its public API did
not receive cue, author, group, context, session, outcome, or psychological
metadata.

The registered positive family contained a localized conjunction:

- reduced speed near the transition;
- a cusp component perpendicular to the incoming tangent;
- variable junction position, speed, cusp amplitude, pause depth, and branch
  angle;
- smooth drift, measurement noise, and cue-aligned distractor bends.

Registered negatives contained smooth paths, bend-only, pause-only,
cue-bend, near-crossing, and speed-wave attacks.

## Canonical evidence

The canonical seed was `20330919`; discovery selected threshold 0.30 before
200 confirmation populations were scored.

| Metric | Mean | 95% interval |
| --- | ---: | ---: |
| Precision | 0.999995 | [0.999985, 1.000000] |
| Recall | 0.999265 | [0.999150, 0.999380] |
| F1 | 0.999630 | [0.999570, 0.999685] |
| Median location error | 0 | [0, 0] |
| P95 location error | 1 | [1, 1] |
| False junctions / 1000 negatives | 0.0025 | [0.0000, 0.0075] |
| Blind-versus-oracle operator correlation | 0.9589 | [0.9555, 0.9621] |
| Predictive gain retention | 1.0012 | [0.9980, 1.0043] |
| Blind truth correlation | 0.8643 | [0.8622, 0.8666] |
| Blind split-session reliability | 0.6519 | [0.6484, 0.6556] |
| Blind unseen-context reliability | 0.8268 | [0.8246, 0.8291] |
| Blind within-group AUC | 0.9627 | [0.9611, 0.9642] |
| Blind author claim | 195/200 | lower bound 0.9482 |
| Cue-leak author claim | 0/200 | upper bound 0.0149 |

The mean observed opportunity fraction was 0.999999. The mask-aware profile
estimator therefore had almost no missingness burden in this registered
world, although its refusal behavior was unit-tested for complete cell
non-overlap.

## Interpretation

The result shows that a geometry-and-order-only detector can recover the
registered pause-plus-perpendicular-cusp event family accurately enough to
preserve the V3.7A routing operator. It closes the narrow procedural gap
between an oracle event window and a blind locator in this planted world.

It does not establish open-world event discovery. The positive generator and
locator share the same mechanistic hypothesis: a junction contains a speed
dip and a perpendicular cusp. Their near-perfect separation is therefore a
family-specific upper bound. The result must not be described as discovery
of arbitrary trajectory junctions.

## Inherited limitations

V3.7B reuses the V3.7A routing estimator and scorer. It therefore inherits:

- known four-component mixture count during denoiser fitting;
- true-group centering in scorer-only correlations and reliability;
- no accepted variance-component decomposition;
- no formal single-author confidence interval;
- no personality, thought, intelligence, clinical, or real-text meaning.

The mask-aware estimator omits unavailable cells rather than fabricating
events. Because missingness was almost absent here, the experiment does not
yet validate robustness to outcome-dependent or context-dependent
localization failure.

## Independent audit corrections

The independent audit accepted the narrow registered-family result and found
six limits that constrain its use:

1. The positive generator and locator share the same speed-dip plus
   perpendicular-cusp mechanism. The controls do not include enough
   pause-plus-cusp joint false positives.
2. Blind counts are relocalized from the exact events used for oracle counts.
   The 0.959 operator correlation therefore contains shared sampling noise,
   and gain retention 1.001 is not independent-panel predictive superiority.
3. Canonical opportunity availability was 0.999999. The mask-aware estimator
   was not meaningfully tested under random or nonrandom missingness.
4. P95 location error was computed only after defining correct events as
   error at most two, making that gate partly circular.
5. Fixed seed offsets caused 398 duplicate derived RNG seed IDs among 4,200
   component uses, weakening strict population independence.
6. The locator firewall is valid, but downstream scoring still inherits
   V3.7A's known-\(K\) and true-group-centering limitation.

See `reports/V8_BLIND_JUNCTION_LOCALIZATION_V37B_INDEPENDENT_AUDIT.md`.

## Next gates

1. Score blind-fit operators against an independent oracle event panel.
2. Hold the frozen locator fixed and test out-of-family positive mechanisms:
   gradual branching, loops, pauses without cusps, cusps without pauses,
   asymmetric multi-stage transitions, and higher-dimensional trajectories.
3. Test hard negatives matched on the locator's score components rather than
   only hand-named path types.
4. Increase trajectory noise and reduce signal amplitude until calibrated
   refusal replaces forced localization.
5. Evaluate MAR/MNAR localization masks and compare available-case,
   common-support, and inverse-probability-weighted profiles.
6. Replace derived integer offsets with spawned RNG streams and make
   localization-error gates unconditional.
7. Only after those tests, map a frozen numerical event representation into
   real text without opening psychological labels.
