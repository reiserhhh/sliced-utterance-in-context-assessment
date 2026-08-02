# SUICA M4-E2 — Anatomy of the Common Offset: Which Objective Structure Carries It?

Tier: **EXPLORATORY** (open-exploration phase, operator directive 2026-08-01).
Registered before run: docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md,
"M4-E2 — anatomy of the common offset" (2026-08-02, loop cycle 11, commit
dc97d59); ledger row M4-E2. Script:
`scripts/run_suica_m4_e2_offset_anatomy.py`. Artifacts:
`results/m4_e2_offset_anatomy/`. Machinery imported from Legs 3/4/9/10/11/14;
anchors: Leg 14 `decision.json` (persisted cloud offsets + GPA objectives) and
`gap_rows.csv`, Leg 11 `partial_gates_*.json` (per-rep displacement), archived
V2 `metrics.csv`.

**Question.** Leg 14 closed the M4-D arc with one rep-invariant object: the
discovered-frame cloud center sits 12.0–13.8 quotient units from the
oracle-anchor cloud center (~3/4 of the median per-rep displacement),
unremovable by consensus averaging or split-half agreement. WHICH structure of
the discovery objective carries it — the response-safety constraint's
complement (S1), the supervision-target span (S2), or the normalization/scale
modes (S3)?

## Outcome in one paragraph

**0/3 leans; THE REGISTERED PIVOT FIRES: the offset SPREADS — no single
objective term is responsible.** Under the registered sequential order
(S1 → S2 → S3) no subspace reaches 40% in any world, let alone the 60%
concentration bar: S1 (safety complement, the registered point-lean) carries
only .20–.23, S2 (supervision span) is near-irrelevant at .01–.03 — the
supervised block is NOT where the bias lives — S3 (norm/scale modes) peaks at
.30–.38, and the residual .40–.45 is everywhere the largest single piece.
Cross-world direction stability fails decisively: the pairwise Procrustes
cosines of the offset vectors (.416–.452) are statistically indistinguishable
from the within-role permutation null (median ~.43) and the matched-shape
random null (median .424) — the offsets are world-specific directions, NOT one
mechanism. And the practical tie-back inverts: projecting the dominant
component (S3 in all three worlds) out of each rep's discovered frame DOUBLES
the paired gap (pooled .215 → .480, closure −1.23; per-world closures −1.28 /
−1.13 / −1.11) while pushing every rep's frame slightly FARTHER from its
oracle anchor (alpha_dom ≈ 1.05–1.12 in 24/24 reps) — surgical excision breaks
the jointly-adapted frame, exactly the all-or-nothing regime Legs 10/11/14
mapped. The one positive structural residue (companion, no adjudication
weight): the largest identifiable carrier is the scale family — 39–48% of the
offset's squared norm is a column-rescaling of the discovered consensus along
its own principal directions (n2 modes, 19–23x their 13-dim null share),
pointing at the freeze whitening's unregularized amplification (Leg 10's
suspect (i)) — but it tops out at half the mass, its fine direction is
world-specific, and it is not surgically removable. The M4-D/E line closes
with the open problem properly characterized: objective redesign will be
neither a one-term fix nor a shared-direction fix.

## The offset object (task 1 — reused and asserted, not re-derived)

Per world, Leg 14's clouds were rebuilt bit-continuously (same contexts, same
stacked frames, same multi-start GPA rule) and the offset vector taken as the
aligned matrix difference Delta = pad(v2 consensus) − align(pad(swap
consensus)), in the consensus gauge:

| world | ||Delta|| (this run) | Leg 14 persisted | abs diff |
|---|---|---|---|
| endogenous_creation_expansion | 13.754107 | 13.754107 | 0.0 |
| selection_creation_compensation | 11.956016 | 11.956016 | 0.0 |
| source_rotated_feedback | 13.288138 | 13.288138 | 0.0 |

GPA objectives (v2 and swap clouds) also reproduce at 0.0; v2 basin counts
8/7/8 match Leg 14's gates; ||Delta||_F equals the quotient distance at
<= 1e-10. Every decomposition statistic below is invariant under the global
right-O(W) gauge of that representative.

## Subspace constructions (stated, as the registration requires)

All subspaces live in the 48 x 13 stacked-frame matrix space (dim 624).
Pattern subspaces act on category-pattern space R^48 as left projectors
(x) full column space (gauge-invariant); S3 additionally uses
gauge-equivariant matrix modes built from the consensus itself.

- **S1 — safety complement** (dim 78 = 6 x 13; null share .125): common core
  (top-6 left singular vectors of the pooled unit-normalized per-rep
  patterns) of Leg 10 arm-B's response-supervised feature patterns
  Z_role @ U_q — the exact code path that relaxes the response-safety
  constraint, gated at 0.0 against `leg10._response_informed_bases`.
  Supervised rank q = 6 in 24/24 reps; pooled-core capture .55–.57.
- **S2 — supervision span** (dim 26 = 2 x 13; null .0417): common core of the
  author-mean observed mechanism-panel responses (uncentered), d2 = 2;
  pooled-core capture .48–.53.
- **S3 — normalization/scale modes** (rank 54; null .0865): orthonormalized
  union of (n1) per-role constant patterns (x) R^13 — every centering step
  and the mass column move rows along these (39); (n2) principal
  column-scale modes {A v_i v_i^T} of the consensus A — first-order motion
  under re-scaling its principal column directions, the whitening's
  amplification family (13); (n3) per-role size modes {P_role A} (3).
- **S4 — residual.**

## Decomposition (task 2): registered order, reverse order, standalone

Registered sequential order S1 → S2 → S3 (adjudicated):

| world | S1 | S2 | S3 | S4 residual | max |
|---|---|---|---|---|---|
| expansion | .2285 | .0122 | .3323 | .4269 | .3323 |
| compensation | .2002 | .0154 | .3830 | .4015 | **.3830** |
| rotated | .2319 | .0264 | .2953 | .4464 | .2953 |

Lean (a) bar: >= .60 in one subspace in all 3 worlds — **MISS 0/3** (no
subspace reaches .40 anywhere under this order; the S1 point-lean is also
wrong). Pivot bar: max share < .40 in every world — **FIRES 3/3**.

Ordering sensitivity (disclosed; reverse order S3 → S2 → S1, plus standalone
projections of Delta):

| world | S3 rev. | S2 rev. | S1 rev. | resid rev. | S1 alone | S2 alone | S3 alone |
|---|---|---|---|---|---|---|---|
| expansion | .4459 | .0261 | .1632 | .3649 | .2285 | .0618 | .4459 |
| compensation | .5288 | .0112 | .1232 | .3369 | .2002 | .0697 | .5288 |
| rotated | .4984 | .0119 | .1225 | .3672 | .2319 | .0723 | .4984 |

The S1/S3 overlap is real (S1 first steals .07–.15 from S3), and the pivot's
sub-40% clause is ORDER-SENSITIVE: under S3-first ordering S3 holds .45–.53
everywhere (>= .40). The pre-coded rule is evaluated on the registered order
and fires; the concentration conclusion is ordering-robust the other way — no
subspace approaches .60 under ANY ordering (max anywhere .529), so "no single
term carries the offset" stands regardless.

Within-S3 family structure and the scale finding (companions):

| world | n1 alone (null .0625) | n2 alone (null .0208) | n3 alone (null .0048) | n2 share of standalone-S3 component |
|---|---|---|---|---|
| expansion | .0937 | **.3946** | .1846 | .7398 |
| compensation | .1136 | **.4772** | .1510 | .7082 |
| rotated | .0882 | **.4569** | .1582 | .7901 |

n2 — column-rescalings of the discovered consensus along its own principal
directions — is the sharpest relative concentration in the whole anatomy
(19–23x null). n3's high standalone (31–38x null) is almost fully contained
in n2's span-effect (sequential adds <= .012 after n2): the scale structure
is one family, not two. n1 (centering/mass) is weak (1.4–1.8x null).

**Width-mismatch companion, honestly nulled:** the share of the offset
outside the swap consensus's 7-dim column space is .854/.880/.864 — at its
random baseline 1 − 7/48 = .854 (+.000/+.026/+.010). The naive "the offset is
the discovered chart's 6 extra whitened columns" story is RULED OUT: the
offset does not preferentially avoid or occupy the extra directions.

The offset is also not low-rank: top-1 singular share of Delta is .14–.16.

## Cross-world direction stability (task 3) — MISS, decisively

Procrustes cosine over the right gauge (nuclear-norm normalized); nulls
disclosed because O(13)-alignment inflates cosines heavily:

| pair | offset cosine | dominant-comp. cosine | perm-null median (q95) | random-null median (q95) |
|---|---|---|---|---|
| expansion / compensation | .4179 | .3974 | .4316 (.4666) | .4239 (.4603) |
| expansion / rotated | .4523 | .4590 | .4334 (.4752) | .4239 (.4603) |
| compensation / rotated | .4159 | .4165 | .4298 (.4687) | .4239 (.4603) |

Lean (b) bar (>= .70 all pairs): **MISS** — and not marginally: every observed
value sits AT the null medians (two of three below the within-role
permutation median). The offsets are world-specific directions statistically
indistinguishable from unrelated matrices under the alignment gauge. NOT one
mechanism at the vector level; what IS consistent across worlds is only the
structural profile (the share tables above).

## Dominant-component removal refit (task 4) — MISS, sign inverted

Dominant subspace = S3 in all three worlds (pre-coded rule: largest
registered-order share among S1/S2/S3). Per rep: align the discovered frame
to the consensus, project out the single unit matrix direction of the world's
S3 component, slice, canonical forced-route refit (V2 semantics, 1x r=0,
Leg 9 gap semantics; gap_v2 and e_orc bit-anchored to Leg 14's persisted
rows).

| world | gap_v2 | gap_dom | closure | median alpha_dom | median coeff / ||Delta_dom|| |
|---|---|---|---|---|---|
| expansion | .2150 | .4895 | **−1.277** | 1.068 | 14.37 / 7.93 |
| compensation | .2102 | .4487 | **−1.135** | 1.064 | 12.68 / 7.40 |
| rotated | .2283 | .4827 | **−1.115** | 1.064 | 14.05 / 7.22 |
| **pooled** | **.2152** | **.4799** | **−1.230** | — | — |

Lean (c) bar (pooled closure >= .50): **MISS, sign inverted** — removal
DOUBLES the gap and moves every rep's frame slightly farther from its oracle
anchor (alpha_dom > 1 in 24/24 reps). The mechanism is visible in the
coefficients: the frames' shared content along the removal direction
(c_r = 12.7–14.4, all positive) is ~1.8x the offset component itself
(7.2–7.9) — the projection excises about twice the offset and lands the frame
on the far side, while also deleting load-bearing scale structure that the
removal direction (built from the consensus's own principal modes) inevitably
overlaps. This is the same regime Leg 10 measured as direction/gap DECOUPLING
and Leg 14 as the consensus blow-up: the discovered frame is a jointly
adapted local optimum; amputating one matrix direction breaks the joint fit.

## Adjudication summary

| lean | bar | outcome |
|---|---|---|
| (a) >= 60% in ONE subspace, all 3 worlds (point-lean S1) | max share .3323/.3830/.2953 (S3); S1 .20–.23 | **MISS** |
| (b) cross-world pairwise cosine >= .7 | .4179/.4523/.4159, at null medians | **MISS** |
| (c) dominant-removal closes >= half the gap | pooled closure −1.230 | **MISS (sign inverted)** |
| PIVOT: < 40% in every subspace, every world | fires per pre-coded rule (registered order) | **FIRES** |

Verdict: **OFFSET_SPREAD_NO_SINGLE_OBJECTIVE_TERM**. Registered hand-off
executed: the Leg 14 open problem stands exactly as registered — now with the
added characterization that the redesign target is DISTRIBUTED (largest
single piece is the residual, .40–.45), the scale family is the largest
identifiable carrier (~1/3 sequential, ~1/2 standalone, n2-dominated), the
supervised block is irrelevant, and the offset direction is world-specific.
The loop moves outside the M4-D/E line to fresh mining.

## Honest anomalies

- **The pivot's sub-40% clause is knife-edged and order-sensitive.**
  Compensation's registered-order S3 share is .3830 — .017 under the bar —
  and under reverse ordering S3 exceeds .40 in all three worlds (.446/.529/
  .498). The pre-coded rule (registered order) fires cleanly, but the honest
  reading is "no term above ~half the mass under any ordering", not "every
  term below 40% in every reading".
- **Procrustes-cosine null inflation.** Two independent random 48x13 matrices
  already cosine at .424 (median) under the O(13) alignment; the registered
  .7 bar is effectively a vector-cosine bar. The miss is decisive (observed
  at null), but the bar itself was generous to the lean.
- **Width-mismatch share sits exactly at its random baseline** (.854 vs
  .854/.880/.864) — reported because the "6 extra whitened columns" reading
  of the offset was a live hypothesis from Leg 10's amplification suspect; it
  is ruled out, while the RESCALING of retained directions (n2) is the
  carrier that survives.
- **One rep gains a column direction from the removal.** Expansion rep 6
  (native width 12) has frame rank 12 → 13 after projection: the removal
  direction has support outside that rep's native column space. No refusal
  (well-posedness preserved, rotation gate 1.6e-13); noted because it shows
  the world-level removal direction is not even representable inside every
  rep's discovered chart.
- **S2's sequential share (.012–.026) is BELOW its null (.0417)** — S1 and S3
  absorb what little response-target mass exists; even standalone S2 is only
  1.5–1.7x null. The supervision-target span is the one clean exoneration of
  this anatomy.
- **The common cores behind S1/S2 are only moderate** (pooled-mass capture
  .55/.48–.57/.53), as expected with rep-specific category draws; their
  patterns are rep-pooled constructions, so S1/S2 shares partly reflect that
  weakness — disclosed rather than repaired, since inflating the pooled rank
  would push S1/S2 toward trivial full-space projectors.

## Faithfulness chain (all green, refused-not-warned)

| gate | value |
|---|---|
| V2 replay geometries (72 rows) | max 1.1e-16 |
| analytic D_true unit check | 1.7e-15 |
| Leg 11 displacement anchor (24 reps) | 0.0 |
| Leg 14 offset anchor (3 worlds) | 0.0 |
| Leg 14 GPA objectives (v2 + swap clouds) | 0.0 |
| Leg 10 arm-B rebuild gate | 0.0 |
| Leg 14 e_orc row anchor (768 cells) | 9.7e-17 |
| rotation gate on dominant-removed frames | 1.6e-13 |
| sequential shares sum to 1 | enforced at 1e-9 |
| frame rank preservation under removal | 24/24 (one rank gain, disclosed) |

## Boundaries

Finite synthetic M4-C.2 worlds only; truth-referenced diagnostic on Leg 14's
persisted cloud objects; the dominant-removed frames are DIAGNOSTIC
constructions (the removal direction consumes all 8 reps and the oracle-anchor
cloud), not deployable estimator semantics; S1 uses the response panel field
the safety contract withholds (diagnostic-only, Leg 10 arm-B precedent); the
subspace realizations are this leg's stated operational constructions of the
registered terms, not unique; no natural-text, personality, or clinical
claim; no seal, no independent verification (operator directive 2026-08-01).
