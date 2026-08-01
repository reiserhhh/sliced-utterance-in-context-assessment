# SUICA M4-D Leg 6 — Excitation vs the D Floor: the Registered Pivot Fires

Date: 2026-08-02
Tier: EXPLORATORY (open-exploration phase; operator directive 2026-08-01:
defensive machinery deferred; design and leans registered in
`docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md` ("Leg 6",
2026-08-02, commit 14441f6) before this run; no prospective seal, no
independent verification pass)

## Decision

```text
PIVOT_C33_INFORMATION_LIMIT_EXTENDS_TO_OBJECT_LEVEL_
NEXT_LEVER_PAIRED_INTERVENTIONAL_OCCASIONS
```

**The registered pivot fires.** Per-event orthogonal excitation (C3.3's
balanced signed probes, reused bit-frozen at generation time) moves the
pooled oracle-forced D-leg floor by only **.0125** (passive `.3902` →
excitation `.3777`, mean of pooled `e_d_paired` medians at {2x, 4x}) —
below the registered `.02` pivot bar and far from the `.34` lean target.
Every world stays `STRUCTURAL_FLOOR` under excitation (all five tail
slopes flat, max |tail| `.078`), so the scaling reading is **(b1) level
shift with flat tail**, not restored budget scaling. Stacking excitation
into the Leg-5 two-stage construction does not help either: pooled loop
geometry **.7387**, *below* Leg 5's persisted `.7605`, with losses in all
five worlds. The registered declaration therefore stands: **the C3.3
information limit extends to the OBJECT level — excitation buys Fisher
information (both truth-referenced error legs drop, route flips drop) but
not D-resolution (the paired disc-vs-oracle gap that bounds loop transport
is pinned by realization variance it cannot reach).** The next design
lever is **paired/interventional occasions**, which becomes the next
registered leg. This is the outcome the registration called honorable, and
it is a theory deliverable: the floor's budget-invariance (Leg 4b) now has
an excitation-invariance clause.

## Registered design and leans (verbatim intent from the plan)

- **Floor arms:** {passive, orthogonal excitation} x budget {1x, 2x, 4x}
  under the Leg-4b protocol (oracle-forced route, per-world floors), same
  5 worlds x 8 reps. Passive must REPRODUCE Leg 4b's persisted values.
  Excitation = C3.3's probe design applied at path generation, evaluation
  natural, exactly as C3.3 did.
- **Stacking arm:** two-stage (Leg 5 construction) + excitation
  calibration at 1x, full battery; compare against Leg 5's persisted
  `.7605`.
- **Leans:** (a) pooled excitation floor <= `.34` at matched budget
  (passive `.39`); (b) record WHICH scaling reading holds — (b1) level
  shift with flat tail (|slope| < `.15`) vs (b2) restored budget scaling
  (tail <= `-.35`); (c) two-stage+excitation pooled >= `.78` with gains
  concentrated in partition (`.6527`) and compensation (`.6209`).
- **Pivot-if:** pooled floor moves < `.02` → the C3.3 information limit
  extends to the OBJECT level; next lever = paired/interventional
  occasions.

Pre-coded operationalizations (script header, before the run): floor :=
mean of pooled author-level `e_d_paired` medians at {2x, 4x} (Leg 4b's
floor statement); tail slope over {1x, 2x, 4x} (Leg 4b's tail definition);
lean (c) concentration := mean per-world gain over the two pinned worlds
exceeds the mean gain over the other three (gains vs Leg 5's persisted
per-world values); pivot on (passive floor − excitation floor) < `.02`,
which also covers a worsening.

## Faithfulness chain (all gates passed)

| Gate | Result |
|---|---|
| Passive floor rows vs Leg 4 persisted `dleg_budget_rows.csv` | 3,840 rows across 40 world-reps, max abs diff **2.22e-16**, all flags/routes equal — asserted per world-rep BEFORE the excitation arm ran |
| Passive pooled medians + tail slope vs Leg 4 persisted decision | match to < 1e-9 / < 1e-6 |
| Amplitude-0 pipeline identity (per world at rep 0) | excitation generator with probe amplitude 0 reproduces the natural calibration/selection panels **value-exactly on all 8 panel fields** (5/5 worlds) |
| Balanced probe design (zero-mean, orthogonal) | exact (mirrors C3.3's frozen test) |
| V2 replay validation (arm-0 geometries vs archived battery) | max abs diff 1.11e-16 |
| 1x oracle/disc identity gates (Leg-4b) | 0.0 |
| Assembly cell audit | 7,680 floor rows, 3,840 stacking rows, 120 scale cells — no missing, no duplicates |

Pairing note (verified, not assumed): the excitation generator re-seeds
the identical per-panel RNG streams the natural generator uses and draws
no additional randoms, so the excitation arm is a **paired realization**
of the passive arm (same noise streams, probe-only causal delta), not a
resample. No passive regeneration was needed — Leg 4b's persisted floor
IS the passive floor here, and the registered reproduce-first requirement
was met bit-exactly.

## Floor table — passive vs excitation, pooled `e_d_paired` medians

| Budget | Passive | Excitation | Delta (P−E) |
|---|---|---|---|
| 1x | .4182 | .3931 | **.0251** |
| 2x | .3908 | .3797 | .0111 |
| 4x | .3895 | .3756 | .0139 |
| **Floor (2x–4x mean)** | **.3902** | **.3777** | **.0125** |

Tail slope (1x→4x): passive **−.0512** (persisted), excitation
**−.0327**. Excitation verdict: `STRUCTURAL_FLOOR` (pooled and all five
worlds).

Per world (floor = mean of medians at {2x, 4x}; all verdicts
`STRUCTURAL_FLOOR`, all improvements positive but small):

| World | Passive floor | Excitation floor | Improvement | Exc. tail slope |
|---|---|---|---|---|
| expansion | .4656 | .4447 | .0209 | −.0449 |
| partition | .4866 | .4652 | .0213 | −.0777 |
| gated | .1404 | .1365 | .0039 | −.0264 |
| compensation | .4458 | .4040 | **.0418** | −.0055 |
| rotated | .4512 | .4482 | .0030 | −.0430 |
| **POOLED** | **.3902** | **.3777** | **.0125** | −.0327 |

Reading: the excitation delta is a small downward **translation** whose
size *shrinks* from 1x (.0251) to the tail (.011–.014) — the two curves
converge toward nearly the same asymptote. Only compensation moves more
than the pivot bar on its own (.0418), and even there the tail is the
flattest of all five (−.0055): a lower shelf, not restored scaling.

## Where the excitation information actually went (companions)

Truth-referenced legs at the forced route, pooled medians:

| Metric | 1x passive → exc | 4x passive → exc |
|---|---|---|
| `e_d_true` (disc vs generator law) | .5923 → .5516 | .5798 → .5267 |
| `e_orc_true` (oracle vs generator law) | .3756 → .2921 | .3728 → .2800 |

Both sides of the estimator move meaningfully closer to the TRUE creation
derivative under excitation (oracle side by ~.08–.09 — this is C3.3's
positive Fisher channel, alive and well at the object level), and route
identification improves everywhere (battery flips: V2 baseline 196 →
167 excited; penalized stage 1 73 → 54 excited). But the PAIRED gap —
discovered-basis fit vs oracle-basis fit on the SAME excited panels, the
quantity that mediates loop transport (Leg 4/5) — barely moves. That is
the precise sense in which the information limit extends to the object
level: **excitation buys information about the law, but the disc–oracle
resolution gap is dominated by per-realization variance plus basis
mismatch that richer per-event excitation cannot reach.**

## Stacking arm — two-stage + excitation at 1x vs Leg 5

| Arm (1x battery) | Flips | Median e_d | Pooled loop geom | Worlds >= .75 |
|---|---|---|---|---|
| arm0_v2 (natural, persisted) | 196 | .4869 | .6519 | 1 |
| two_stage (natural, Leg 5 persisted) | 73 | .4481 | **.7605** | 3 |
| arm0_excited | 167 | .5003 | .6664 | 1 |
| stage1_excited (lambda=.125) | 54 | .7033 | .6986 | 2 |
| **two_stage_excited** | **54** | **.4595** | **.7387** | **3** |

Per-world gain of two_stage_excited vs Leg 5's two_stage: expansion
−.0058, partition −.0215, gated −.0199, compensation −.0347, rotated
−.0271 — **negative in all five worlds** (pooled −.0218). The pinned
worlds lost MORE (mean −.0281) than the others (−.0176): the opposite of
the registered concentration. Lean (c) misses on both sub-conditions.

Honest reading of the stacking loss: the loop statistic is anchored to
the NATURAL maximum-passive oracle stacks (C3.3's fixed endpoint; the
choice that makes `.7387` directly comparable to `.7605`). Fitting the
discovered legs on excited paths improves route stability (54 flips,
better than the natural construction's 73) but places the refit D's
slightly farther from the natural-oracle D's (median e_d .4595 vs .4481)
— a small cross-distribution penalty that eats more than the
route-stability gain. Excitation and the two-stage construction do NOT
stack; each pays for information the transport statistic cannot spend.

## Per-lean adjudication

| Lean | Registered bar | Value | Verdict |
|---|---|---|---|
| (a) floor drop >= .05 | excitation floor <= .34 (passive .3902) | .3777, improvement .0125 | **MISS** |
| (b) which scaling reading | (b1) \|tail\| < .15 vs (b2) tail <= −.35 | tail −.0327 (all 5 worlds flat) | **(b1) LEVEL SHIFT, FLAT TAIL** |
| (c) stacking >= .78, gains in pinned worlds | pooled >= .78 AND pinned gain > other gain | .7387; pinned −.0281 vs other −.0176 | **MISS** (both sub-conditions) |
| Pivot-if | improvement < .02 | .0125 | **FIRES** |

## What this closes and what it opens

Closed (exploratory tier): the first lever of the design-change track.
Under the current V2 event structure, per-event excitation richness — the
lever C3.3's frontier pointed at — does **not** move the D-leg resolution
floor (< .02 pooled), does not restore budget scaling (flat tails,
unanimous), and does not stack with the two-stage construction (pooled
−.0218). The Leg-4b limit statement gains a clause: the ~.39 floor is
invariant to gauge/seam correction, route repair, event budget, AND
per-event response excitation at the C3.3 design point.

Open (registered next lever, per the pivot): **paired/interventional
OCCASIONS** — designs that intervene at the occasion level (paired
natural/intervened occasions of the same authors, or occasion-level
randomization), attacking the per-realization variance term directly
rather than the per-event information term. That becomes the next
registered leg of the design-change track.

## Honest anomalies and boundaries

- **Excitation helps exactly where C3.3 said it would.** Flips drop at
  both the V2 baseline (196→167) and stage 1 (73→54), and both
  truth-referenced legs improve — "what events buy is route
  identification" extends to "what excitation buys is law information,
  not disc–oracle resolution". No contradiction with C3.3's positive
  slope; the NO-GO's reach is now sharper.
- **The 1x matched-budget delta (.0251) exceeds the tail deltas
  (.011–.014).** Excitation is worth roughly one passive octave at 1x
  (excited 1x .3931 vs passive 2x .3908) but the advantage decays as
  passive budget grows — convergent asymptotes, the signature of a shared
  floor rather than an information deficit.
- **Stacking comparability caveat:** two_stage_excited is scored against
  the natural oracle stacks (the fixed maximum-passive endpoint, required
  for comparability with .7605). A hypothetical excited-oracle reference
  would change the number; it was not registered and is not computed.
- **Response scale is estimated per budget from the natural panels at
  that budget** (C3.3 semantics: the scale of the process being
  replaced). Realized scales are persisted
  (`excitation_scales.csv`); cross-budget drift of the pooled mean scale
  is < .005 SD units, so the arms are amplitude-matched across budgets.
- Degenerate reference rows: 36 per arm (the same 12 author-views x 3
  budgets as Leg 4b's rule), excluded from medians on both arms
  identically.
- Truth-referenced diagnostic throughout (oracle-forced routes,
  oracle-basis fits, generator-law derivatives consumed as references);
  excitation itself is a designed creation-input intervention available
  only because the generator is known. Nothing here reopens any gate: the
  V1/V2 and C3.3 NO-GO decisions stand. Finite synthetic M4-C.2 worlds
  only; no natural-text, personality, emotion, or clinical claim; no
  seal, no independent verification (operator directive 2026-08-01).

## Artifacts

- `scripts/run_suica_m4_d_excitation_floor_leg6.py` (chunked foreground
  battery + refuse-on-missing assembly)
- `results/m4_d_excitation_floor/decision.json`
- `results/m4_d_excitation_floor/floor_budget_rows.csv` (7,680 rows, both
  arms), `floor_scaling_summary.csv`, `excitation_scales.csv`
- `results/m4_d_excitation_floor/stacking_per_loop_metrics.csv` (3,840
  rows), `stacking_world_rep_metrics.csv`
- `results/m4_d_excitation_floor/passive_reproduction_check.csv`,
  `v2_validation.csv`
