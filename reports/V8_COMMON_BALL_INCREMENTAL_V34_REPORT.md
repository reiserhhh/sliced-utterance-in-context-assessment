# V8 Common-Ball Incremental V3.4 Report

Decision: `V8_COMMON_BALL_INCREMENTAL_V34_PASS`

## Question

Does a recurring multi-author common intersection contain information that
is absent from the complete thresholded author-pair adjacency tensor?

This is a technical planted-world question. It does not ask whether an
intersection is a personality trait or interpersonal compatibility.

## Registered contrast

Every author response point receives a radius-\(R\) uncertainty ball. The
paired worlds keep all pairwise ball intersections identical in every
condition, radius, and observer view.

- Positive: six points lie on a circle of radius \(0.90R\), so one ball of
  radius \(R\) contains the full set.
- Negative: two points occupy each vertex of an equilateral triangle with
  circumradius \(1.10R\). The largest pair distance is
  \(\sqrt3(1.10R)=1.905R<2R\), so every pair remains adjacent, but no
  registered common ball contains all six.

The frozen radii were \(1.00R,1.03R,1.06R\), with four active conditions of
65 and four independent observer views.

## Main result

| Quantity | Result |
| --- | ---: |
| Fresh paired populations | 500 |
| Per-view adjacency mismatches | 0 |
| View-intersected adjacency mismatches | 0 |
| Pairwise comparator output matches | 500/500 |
| Feasible six-author claims | 500/500 |
| Feasible median F1 / ARI | 1.000 / 1.000 |
| Infeasible six-author claims | 0/500 |
| Infeasible claim one-sided 95% upper | 0.00597 |
| Infeasible overlap refusals | 500/500 |
| Paired decision delta | 1.000, bootstrap 95% CI [1.000, 1.000] |
| Enumeration/candidate cap failures | 0 |

The negative world consistently retained overlapping four-author
common-ball subsets. It therefore did not become “nothing”; it was rejected
specifically because pairwise completeness did not assemble into one stable
six-author joint relation.

## Controls

Each control used 200 fresh populations.

- both feasible: 200/200 decisions agreed;
- both infeasible: 200/200 decisions agreed;
- near registered-radius boundary: 200/200 margin refusals;
- intentional pair-adjacency mismatch: 200/200 runs stopped before the paired
  claim.

Rigid transformations, author permutations, and label permutation preserve
the structural decisions in unit tests.

## Mathematical interpretation

Pairwise adjacency asks whether every two author balls overlap. Common-ball
feasibility asks whether all \(k\) balls share one point:

\[
\bigcap_{u\in G} \mathcal B(x_u,\epsilon R)\ne\varnothing.
\]

The number \(k\) is the intersection multiplicity, or the order of the
relation. It is not evidence strength by itself. A global condition anchor
can produce \(k=24\) without a group-specific relation.

The information-bearing candidate is:

> recurrence of the same author subset inside one common uncertainty ball,
> under the same condition and scale, across independent views.

## Accepted claim

> In the registered finite-margin two-dimensional simulator, complete
> thresholded pairwise adjacency does not determine whether a multi-author
> set lies in one common ball; exact minimum-enclosing-ball geometry retains
> that higher-order feasibility information.

## Boundary and next gate

A complete continuous Euclidean distance matrix already determines the
minimum enclosing ball. V3.4 therefore establishes information beyond a
finite binary threshold tensor, not beyond continuous distance geometry.

No personality, compatibility, type, clinical, or real-text claim follows.
The next scientific gate is to test frozen common-ball recurrence on
condition/opportunity-matched real-text representations, then ask whether it
replicates across held-out text and relates to external psychological or
behavioral evidence.
