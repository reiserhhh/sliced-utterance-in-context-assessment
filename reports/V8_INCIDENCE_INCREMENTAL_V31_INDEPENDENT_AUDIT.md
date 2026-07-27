# V8 Incremental Incidence V3.1 Independent Audit

Decision: `PASS_TECHNICAL_PLANTED_ONLY`

V3.1 closes the two estimator defects identified in the V3 audit. It supports
a technical planted-world claim for condition-aligned persistent subsets. It
does not support a personality or real-text claim.

## Confirmed

- Thresholded Apriori search is complete. For \(A\subseteq B\), the set of
  hyperedges that can support \(B\) is a subset of those that can support
  \(A\). The multiplicity-specific weight, cross-view minimum, and cell
  average preserve \(P(B)\le P(A)\).
- An independent exhaustive comparison over 250 random weighted multiview
  grids found no omitted threshold-passing subset and no score discrepancy.
- A stable subset embedded in different maximal hyperedges is now recovered.
- Cross-view support is minimized within the same condition-radius cell
  before averaging, so shifted-condition support is rejected.
- All 600 confirmation pair rows and 400 null rows are estimate-ready; no
  exact-enumeration or candidate-search cap fired.
- Whole-map AUC remains chance with all 90% intervals in [0.45, 0.55].
- Incidence AUC is 1.0 in every positive world; positive claims are 600/600.
- Counterfactual, chaining, and null group claims are all 0/200 per world,
  with one-sided 95% upper bound 0.01487.
- Eleven artifact hashes verify, summaries recompute from raw rows, and
  discovery/confirmation seeds are disjoint.

## Interpretation boundary

Minimum same-condition distance and a soft local kernel also achieve
approximately AUC 1.0 in the positive worlds. V3.1 therefore establishes
local condition-aligned information beyond integrated whole-map distance, not
the unique necessity or superiority of exact hyperedges.

CF2 preserves a possible independent value: overlapping triplets yield
pairwise local and incidence AUC near 0.80, while the no-chaining rule does not
declare one six-author core. That is a set-level decision-safety property, not
a higher pairwise AUC. The current triplets are individually below the frozen
persistence threshold, so a stronger attack remains necessary.

Raw intersection multiplicity has no accepted psychological interpretation.
The measured quantity is the recurrence of the same author subset inside a
common uncertainty ball at aligned condition-radius cells across views.
Shared prompts, opportunity structure, or observer effects can create the
same geometry.

## Accepted claim

> In the registered low-noise simulator, condition-aligned persistent subset
> cores carry planted co-membership information after integrated whole-map
> Euclidean distance is algebraically neutralized, and the corrected
> threshold-complete estimator recovers those cores while rejecting the
> registered asynchronous, chain, rotating-membership, and null worlds.

The audit rejects extensions to hypergraph uniqueness, real-text prevalence,
personality similarity, interpersonal compatibility, psychological types,
clinical meaning, or diagnostic validity.

## Remaining gate

Run a frozen strong-chain challenge in which every overlapping triplet passes
the persistence threshold but no six-author common ball exists. Compare the
unchanged hypergraph estimator with single-link, complete-link, and spectral
clustering built from the simple local scores. The primary contrast is false
six-core rate and group-structure recovery, not pairwise AUC.

The manifest remains dirty and unsealed. The result is reproducible technical
evidence, not an immutable preregistration.
