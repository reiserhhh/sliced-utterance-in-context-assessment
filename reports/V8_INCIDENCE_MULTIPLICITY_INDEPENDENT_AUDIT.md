# V8 Incidence Multiplicity Independent Audit

Decision: `PARTIAL`

The V2.3 numerical code gate is reproducible and passes its implemented
registered criteria. The independent methodology decision remains partial
because the experiment does not establish incremental value over ordinary
whole-trajectory distance and does not implement a complete persistent
hypergraph estimator.

## Confirmed

- Calibration, confirmation, challenge, discovery, and sensitivity seed
  blocks do not overlap.
- Manifest code/config hashes and all 17 inventoried artifacts verify.
- All five null worlds have 0/160 group claims separately. Each one-sided
  95% Clopper-Pearson upper bound is 0.01855.
- Calibration has 0/120 claims per null world; each marginal upper bound is
  0.02466.
- Clear-world F1, ARI, group-claim, component multiplicity, and the decision
  gates independently reproduce. Serialization ties change recomputed AUC by
  at most 0.00093 and do not affect any gate.
- A population-wide anchor is effectively suppressed: raw multiplicity is
  24 while group-claim rate is 0.
- Observer-only, half-only, condition-permuted, and partial-support attacks
  refuse output.

## Methodological findings

1. The reported null intervals are separate marginal 95% intervals, not a
   simultaneous familywise interval. Confirmation would still pass a
   Bonferroni-adjusted five-null upper bound (approximately 0.0284), but the
   120-repetition calibration would not (approximately 0.0377).
2. The implemented uncertainty set is a pooled isotropic residual-scaled
   ball. It is not an author-specific covariance tube or a calibrated
   confidence region.
3. Complete-link clustering proposes one disjoint candidate partition at
   each condition and radius. Common-ball verification is correct for each
   proposed set, but legal overlapping hyperedges are not exhaustively
   enumerated.
4. Components are formed by transitive closure over selected hyperedges from
   different conditions and radii. This can create a component larger than
   every constituent hyperedge. The current null panel did not convert this
   into a false population claim, but a dedicated hyperedge-chain attack is
   missing.
5. Persistence is exact-member recurrence on a finite
   condition-by-radius grid, not continuous topological persistence.
6. The pair score is centered and standardized across all author pairs after
   aggregation. It is not a condition-local random-pair normalization.
7. Tangent scores are exported but do not enter the frozen group decision.
   The result therefore does not establish a tangent/transverse classifier.
8. Multiplicity and localization gates are aggregated across clear worlds
   rather than implemented as explicit worst-world gates. All V2.3 clear
   worlds happen to pass individually, so this does not change its numeric
   result.

## Strongest alternative explanation

A simple fitted whole-map integrated-distance baseline obtains AUC 1.0 in
all four clear worlds and both challenge worlds. The planted generators are
therefore strongly separated before incidence analysis. V2.3 proves that
the incidence detector can recover those groups; it does not prove that
incidence, multiplicity, or tangent geometry adds information beyond an
ordinary trajectory-distance model.

V2 through V2.3 also form an adaptive development sequence over the same
broad simulator family. New seeds avoid reusing observations, but the
so-called fresh challenge families were repeatedly observed across versions.
The untracked dirty worktree and post-run documentation prevent treating the
sequence as a formal immutable preregistration.

## Accepted claim

> Under the fixed V2.3 simulated design with 24 authors, four balanced
> six-author groups, 65 shared scalar conditions, pooled-isotropic
> normalization, a fixed radius grid, and noise SD 0.03, the implemented
> complete-link common-ball recurrence detector recovered anonymous planted
> co-membership on independent confirmation seeds while making no population
> group claims in the five registered null worlds.

The audit does not accept claims of personality similarity, compatibility,
psychological types, clinical meaning, complete multiplicity recovery,
tangent identification, real-text validity, or superiority over whole-map
distance.

## Required next gate

The next planted experiment must match or neutralize whole-map distance while
changing only local incidence topology. It must also include an overlapping
hyperedge enumeration check and a cross-condition hyperedge-chain null.
Only incremental discrimination over the frozen whole-map baseline would
show that incidence contributes a distinct geometric signal.
