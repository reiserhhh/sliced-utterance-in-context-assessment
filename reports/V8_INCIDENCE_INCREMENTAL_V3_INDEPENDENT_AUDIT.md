# V8 Incremental Incidence V3 Independent Audit

Decision: `PARTIAL`

The implemented V3 code gate passes and its numbers reproduce. It establishes
a constructive planted-world result for condition-local information beyond
integrated Euclidean distance. It does not yet establish a complete
persistent-core method.

## Confirmed

- Gram reservoir compensation produces the same centered row Gram matrix in
  each positive/counterfactual pair.
- Orthogonal Procrustes noise transport preserves the fitted distance
  matrices to approximately \(10^{-15}\). Isotropic Gaussian noise retains
  its marginal distribution under the orthogonal map.
- Population-level bootstrap treats each simulated population as one unit
  and does not treat 276 author pairs as independent.
- The three whole-map AUC means are 0.5041, 0.5007, and 0.5036; their
  bootstrap 90% intervals all lie inside [0.45, 0.55].
- Incidence AUC is 1.0 and median incremental AUC is 0.493-0.502 in all
  three positive worlds.
- Positive group claims are 200/200; counterfactual, chaining, and both null
  claims are 0/200.
- Exact maximal-hyperedge enumeration agrees with exhaustive truth in the
  repository tests and in an additional independent panel of 320 random,
  collinear, repeated-point, 2D, 3D, and 4D small sets.
- Artifact hashes and reproduced first-seed outputs agree with the canonical
  run.

## Why the code gate is not a general method PASS

### The local contrast is deliberately easy

Approximately 89%-93% of total path energy is placed in reservoir
coordinates outside the event region. At event conditions, planted core MEB
radii are approximately 0.69-2.51 uncertainty radii, while the closest
outside authors are about 217-285 radii away. The threshold 0.04 also lies in
the analytic gap between fixed-six recurrence (0.0755), chain-triplet
recurrence (0.0294), and rotating-six recurrence (0.0126).

This is legitimate for a constructive proof, but not evidence of realistic
measurement difficulty.

### Exact maximal hyperedges do not imply complete persistent cores

Candidate cores are drawn only from sets that appear at least once as a
maximal hyperedge. A stable subset such as `{0,1,2}` can be embedded in
`{0,1,2,3}` in one view and `{0,1,2,4}` in another. The stable intersection
never appears as a maximal edge and is omitted. Persistent subset closure is
therefore incomplete even though maximal hyperedge enumeration is exact.

### Cross-view persistence is not condition-aligned

V3 computes recurrence separately in each view and then takes the minimum of
the view-average scores. A core can occur only at condition A in one view and
only at condition B in another and still pass. The current code supports
“recurs in every view,” not “recurs at the same condition in every view.”

### Incidence is not uniquely necessary

Independent simple local baselines based on minimum same-condition distance,
near-neighbor recurrence, and a soft local kernel also obtain AUC 1.0 in the
positive worlds. CF2 pairwise local AUC is about 0.80, while the no-chaining
core rule correctly refuses a six-author merge. The supported distinction is
therefore:

- local condition-aligned information adds to integrated global distance;
- persistent no-chaining cores add a population-structure decision;
- exact hyperedges have not been shown to be the only useful local statistic.

## Additional limits

- The noise matching is an exact design identity that uses paired author
  correspondence; it is not an empirical robustness result.
- Null safety is mainly fail-closed: global-anchor and reservoir-only refusal
  rates are 94.0% and 99.5%.
- The worktree is dirty and untracked, so the internal freeze is not an
  immutable Git-sealed preregistration.

## Accepted claim

> In the registered low-noise, 24-author, two-dimensional simulator, there
> exists planted co-membership that integrated whole-map Euclidean distance
> cannot identify but condition-local recurrence can identify; the current
> estimator recovers the fixed cores and rejects the registered asynchronous,
> chain, rotating-membership, and null worlds.

The audit does not accept general incidence superiority, complete persistent
core recovery, real-text existence, personality meaning, or clinical
interpretation.

## Required V3.1 correction

1. Build candidate cores from the intersection closure of maximal hyperedges,
   not only from maximal sets themselves.
2. Score recurrence jointly at the same condition and radius across all
   independent views.
3. Add direct counterexamples for hidden stable subsets and view-shifted
   conditions.
4. Report simple local baselines and state clearly that the target is
   conditional-local information, not uniqueness of exact hyperedges.
