# V8 Spacetime Junction-Flow V3.6 Plan

Status: `FROZEN_BEFORE_CONFIRMATION`

## 1. Research object

V3.6 tests whether a geometric common intersection can be augmented with
time-directed transition information. It uses the product space

\[
d_\lambda((x,t),(y,s))^2
=
d_X(x,y)^2+\lambda^2(t-s)^2
\]

while preserving the causal order \(t_{\mathrm{in}}<t_j<t_{\mathrm{out}}\).
The technical object is a **spacetime routing junction**, not a thought node.

At each junction, incoming branch \(B^-\), outgoing branch \(B^+\), cue
\(C\), group \(G\), and stage \(J\) define:

\[
G_C
=
\frac{I(B^+;C\mid B^-,G,J)}{\log K},
\qquad
G_T
=
\frac{I(B^+;B^-\mid C,G,J)}{\log K},
\]

\[
H_{\mathrm{res}}
=
\frac{H(B^+\mid B^-,C,G,J)}{\log K}.
\]

\(G_C\) is cue-sensitive routing, \(G_T\) is pass-through dependence, and
\(H_{\mathrm{res}}\) is unexplained branching. High branch entropy alone is
not controlled routing.

## 2. Matched policy worlds

Use \(K=3\) branches, depth \(L=3\), 24 authors, 27 balanced cue-sequence
episodes per author, and four independent views.

| World | Rule | Registered signature |
| --- | --- | --- |
| pass-through | \(B^+=B^-\) | \(G_T\) high, \(G_C\) and residual low |
| random-branch | balanced random \(B^+\) | residual high, both information channels low |
| cue-guided | \(B^+=C\) | \(G_C\) high, \(G_T\) and residual low |

The worlds share authors, group nodes, cue marginals, incoming/outgoing
branch marginals, stage visits, speed, curvature, noise, and static point
distributions. Only event-level transition correspondence changes.

The same representation-space node recurs at all three stages. Spatial
\(X\)-only analysis should collapse stage identity; \(X\times T\) should
recover the ordered stages.

## 3. Tree unrolling

The estimated transition kernel is unrolled over three stages. Report:

- observed path entropy and effective leaf fraction;
- cue-conditioned path entropy;
- cue-channel capacity;
- probability of following the cue-defined goal path;
- number of cue-addressable leaves with path probability at least 0.80.

Geometry describes possible paths, the kernel describes selection, and an
external task reward would describe effectiveness. V3.6 contains no reward.

## 4. Counterfactual controls

- `cue_shuffle`: preserves geometry and branch marginals but removes cue
  correspondence;
- `time_shuffle`: preserves spatial nodes but destroys common temporal order;
- `tangent_view_shuffle`: preserves per-view branch marginals but destroys
  cross-view tangent identity;
- `guided_near_miss`: preserves cue routing but removes the common ball.

The last two logical contrasts are mandatory:

- a common intersection with random/pass-through routing shows that an
  intersection is not sufficient for cue-sensitive routing;
- cue-guided routing in a near miss shows that a common intersection is not
  mathematically necessary for routing.

## 5. Frozen gates

- 500 confirmation populations per primary world;
- 200 populations per control;
- junction F1 one-sided 95% lower at least 0.95;
- time-order Kendall tau at least 0.95;
- tangent cross-view ARI at least 0.90;
- three-world classification lower at least 0.90;
- target information lower at least 0.80;
- non-target information upper at most 0.10;
- unconditional branch entropy at least 0.95 in every primary world;
- cue/time decisive attack upper at most 0.03;
- tangent attack refusal lower at least 0.90;
- guided-near-miss refusal lower at least 0.90;
- \(X\)-only stage accuracy at most 0.50;
- \(X\times T\) stage accuracy at least 0.95;
- primary world prediction from frozen static marginals at most 0.55.

Any cue leakage into node coordinates, failed marginal matching, label use in
the estimator, hash mismatch, or confirmation-driven threshold change stops
the claim.

## 6. Interpretation boundary

A PASS can say only that simulated spacetime response paths contain
identifiable routing regimes at common junctions. Intelligence requires an
external goal, reward, efficiency, and novel-cue generalization. Personality
requires author-specific kernels stable across contexts and linked to
independent psychological or behavioral evidence.
