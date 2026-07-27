# V8 Blind Junction Localization V3.7B Independent Audit

Decision: `PASS_WITH_CAVEATS`

## Integrity

- All five V3.7B sealed implementation files matched their SHA-256 hashes.
- The pre-seal evidence, effective config, seven canonical artifacts, run
  manifest, and artifact inventory verified.
- Canonical base seeds did not overlap the exclusion ledger.
- No confirmation tuning was found.
- The locator API read only trajectory, window, and threshold.

The V3.7B seal records the parent V3.7A seal by path but not by hash. The
current parent hash verifies, but the provenance chain should freeze that hash
explicitly in the next version.

## Accepted

Within the registered two-dimensional pause-cusp path family, the blind
geometry-and-order locator recovered junctions and branches and preserved the
same-source V3.7A routing structure:

- localization F1 0.99963;
- blind-versus-oracle operator correlation 0.95891;
- blind truth correlation 0.86432;
- split-session reliability 0.65193;
- unseen-context reliability 0.82680;
- within-group AUC 0.96266;
- author claim 195/200;
- cue-leak author claim 0/200.

## Caveats

### Generator-locator isomorphism

The positive generator plants a local speed dip and a perpendicular cusp.
The locator scores the product of a speed dip and a perpendicular cusp.
Registered negatives contain isolated bend, pause, cue-bend, near-crossing,
and speed-wave mechanisms, but not enough joint pause-plus-cusp non-junction
counterexamples. The result is a matched-family procedural upper bound, not
general blind localization.

### Shared-event inflation

Blind counts are constructed by expanding and relocalizing the exact events
that generated oracle counts. Direct oracle/blind profile correlation
therefore contains shared sampling noise. The reported 0.959 is same-event
retention, not independent-panel recovery. Likewise, gain retention 1.001
compares each estimator on its own corresponding event counts rather than
scoring blind-fit and oracle-fit predictions against one independent truth
panel.

### Mask stress was negligible

Detection was 0.99932 and mean opportunity availability was 0.999999. About
20,000 of roughly 29.5 million events were lost, but almost no complete
packet-cell-context was unavailable. The available-case estimator does not
fabricate events, yet it can be biased when missingness depends on author,
context, branch, outcome, or difficulty because different authors are then
averaged over different effective reference designs.

### Circular location-error gate

An event is first counted as correct only when location error is at most two.
P95 error is then calculated only among those correct events. Consequently
P95 cannot exceed the registered maximum of two whenever any correct event
exists. Recall remains informative; the conditional P95 gate does not add an
independent falsification.

### Selection and RNG limitations

The implementation selected thresholds by false-positive eligibility,
followed by F1, recall, and threshold. It did not include location error in
selection as the frozen prose implied. Thresholds 0.25 and 0.30 were nearly
tied, so 0.30 has no unique theoretical meaning.

The top-level canonical seeds were disjoint from pre-seal seeds, but fixed
integer offsets across repetitions and components created 398 repeated seed
IDs among 4,200 derived RNG uses. This weakens the strict independence
assumption behind the population bootstrap.

### Inherited group oracle

The locator itself is metadata-blind. The downstream routing denoiser is
told \(K=4\), and the scorer uses true groups for centering, reliability, and
the author claim. This inherits the V3.7A group-oracle limitation. V3.7A's
invalid variance-share and empirical-interval gates were not used by V3.7B.

## Narrow final ruling

V3.7B proves that a metadata-blind locator can recover the registered
pause-cusp synthetic signature and retain the same-event low-rank routing
structure. It does not establish open-world localization, independent-panel
operator recovery, robustness to nonrandom missingness, group-free
measurement, real-text junctions, thought nodes, intelligence, personality,
or clinical meaning.

## Required new-version work

1. Use independent oracle events for blind-fit evaluation.
2. Add out-of-family positives, matched joint hard negatives, random affine
   distortions, unknown branch dictionaries, multiple junctions, and higher
   noise.
3. Add MAR/MNAR mask arms with 50%-95% opportunity coverage and compare
   available-case, common-support, and IPW estimators.
4. Use `SeedSequence.spawn()` for non-overlapping component streams.
5. Compute unconditional localization-error distributions with misses
   represented explicitly.
6. Discover \(K\) on discovery data and report group-free primary metrics;
   true-group centering becomes sensitivity analysis only.
7. Freeze the parent seal hash and exact threshold selection rule.
