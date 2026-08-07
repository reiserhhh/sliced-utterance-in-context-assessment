# SUICA M4-F2 -- The D3 Composition Law (shared-occasion vs free-response design x kappa; within-author cross-context pairing Q in {2,4}, at fixed total event budget)

> **BANNER: synthetic worlds calibrated to an opened-panel regime, exploratory.**
> This leg consumes NO new real-text evidence. It extends M4-F1's
> `M4F1RelationWorld` (itself calibrated, not verbatim-reused, from the V8
> HJIC and M3 generator families -- see M4-F1 Part 0.2) by one new mechanism
> and re-measures the deployed field's own split-half agreement gauge under a
> panel-COMPOSITION manipulation at a budget M4-F1 already showed SCALE alone
> cannot rescue. No label columns anywhere; no claim about the real relation
> field's content, personality, emotion, diagnosis, or any individual.

Registered spec: `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md`
section "M4-F2 registration (2026-08-03, BEFORE run)" (loop cycle 13, panel
design laws line, leg 2). Script:
`scripts/run_suica_m4_f2_composition.py`. Artifacts:
`results/m4_f2_composition/`.

## Part 0 -- REGISTERED ADJUDICATIONS AND OPERATIONALIZATIONS (written before the run)

The registration fixes the mechanism (a context-occasion common shock at
weight kappa, variance-preserving), the design axes, the leans, and the
gates. It leaves several implementation-level choices open. Per the process
rule ("if you discover the spec cannot be executed as written... state the
minimal disclosed deviation... and proceed only if the deviation preserves
the registered comparison"), every one of those choices is fixed here, BEFORE
any sweep compute, with the reasoning that forced each choice.

### 0.1 The context-occasion shock: exact construction

At occasion index `t` in context `c`, `s_{c,t} ~ N(0, I_k)` is drawn once per
`(world, context, occasion)` via a seed independent of the module-level `rng`
object that drives `loadings`/`z`/`zeta`/`x`/`noise`
(`v8.stable_bucket(f"{world_seed}-{context}-{occasion}", salt="m4f2-shock")`).
Each author's state contribution at their occasion `t` becomes
`sqrt(w_x) * a * (( (sqrt(1-kappa)*x_t + sqrt(kappa)*s_{c,t}) * g ) @ loadings.T)`
-- algebraically identical to the registered substitution
("`sqrt(kappa)*sqrt(w_x)*a*((s_{c,t}*g)@loadings.T)` substituted for that
fraction of the author's own state contribution, the state term scaled by
`sqrt(1-kappa)`"). Because the shock draw is on an independent RNG stream,
`kappa<=0` makes the new generator return **the literal, unmodified return
value of `f1().generate_world(counts, knobs, world_seed)`** -- not a
numerically-close reproduction but the same function call. This is what
turns gates G1 and G4 into exact-equality checks rather than tolerance
checks, and it is verified directly (not just argued) in Part 1.

### 0.2 What "occasion" means for `free` vs `shared` (register-note; the registration names the two designs but not their exact index construction)

- **`shared`**: occasion label of an author's t-th event = the local
  sequential index `t` (0..count-1). Every author in a context begins at
  occasion 0 and advances in lockstep, so authors observed at the same
  position genuinely share `s_{c,t}`.
- **`free`**: occasion label = a globally unique flat index (a running offset
  over all authors, author-then-t order). This makes cross-author occasion
  collision **exactly zero**, not merely low-probability -- the limit case of
  "each author draws their own idiosyncratic occasions" rather than an
  arbitrary finite occasion-calendar size that would need its own
  (unregistered) collision-rate justification. Because it is a documented
  bijection with the flattened event index, there is nothing else to tune.

Both constructions leave `kappa<=0` behavior untouched (Part 0.1), so this
choice cannot contaminate gate G4; it only governs what happens once
`kappa>0`.

### 0.3 The "largest common budget across cells" (register-note resolving G2's explicit fallback clause)

Registered text: *"each author appears in Q contexts with floor(m/Q) events
each (distribute remainders deterministically and report the exact totals;
G2 requires exact equality of TOTAL events across every cell -- if integer
division makes exact equality impossible, say so explicitly... and use the
largest common budget across cells rather than silently letting cells
differ)."*

Read literally, "floor(m/Q) events **each**" is a strict per-context
uniformity constraint (no context may get one more than another), so any
per-author remainder `m mod Q` cannot be assigned to any context and must be
dropped. Since `crossed_q2` (Q=2) and `crossed_q4` (Q=4) then generally
achieve *different* totals from each other and from the free/shared cells'
raw `m` (M4-F1's base1x per-author counts, `m in {8,10,12,14,16}`), exact
equality across all six cells is impossible under any single Q applied only
to the crossed arms. The escape clause fires exactly as anticipated:

**Resolution adopted: `m^common_i = 4 * floor(m_i / 4)`, the largest
per-author budget simultaneously exact for both Q=2 and Q=4, applied
UNIFORMLY to all six adjudicated cells** (free_k05, free_k10, shared_k05,
shared_k10, crossed_q2, crossed_q4) -- not only the crossed arms. This makes
G2 hold by construction (every cell allocates the identical total), at the
cost of uniformly dropping `m_i mod 4` events per author from the free/shared
arms too (0 events for `m in {8,12,16}`, 2 events for `m in {10,14}`; exact
counts verified in Part 1). **This truncated layout is used for all six
adjudicated cells but NOT for gate G1**, which reproduces M4-F1's base1x on
its own original (raw, untruncated) layout -- G1 and the adjudicated cells
are deliberately different computations answering different questions (gate
correctness vs the registered comparison).

### 0.4 Crossed-context rotation (register-note; the registration names Q but not which Q contexts an author lands in)

Four contexts exist (`AskReddit`, `AskWomen`, `politics`, `worldnews`,
alphabetical). An author's assigned Q contexts are `Q` consecutive contexts
in this fixed cyclic order starting at their own home context (e.g. home
`AskWomen`, Q=2 -> `[AskWomen, politics]`). Deterministic, no randomness, no
search. For Q=4 this trivially means every author appears in all four
contexts.

### 0.5 The `MIN_FEATURIZABLE=4` wall, discovered by arithmetic before any Monte Carlo compute, and its consequence for `crossed_q4`

`f1().featurize_panel` (reused verbatim, per the registration's explicit "do
not reimplement the gauge" instruction) hard-`raise`s if either of a row's
two alternating replicates (`vectors[offset::2]`, offset in {0,1}) has fewer
than 2 events -- i.e. it requires **every row it is given >= 4 events**, not
merely the deployed gauge's own `>=8` retention floor. Given
`m^common in {8, 12, 16}` (Part 0.3) and per-context-slice size
`s = m^common / Q`:

| m^common | n authors | crossed_q2 slice (s=m/2) | crossed_q4 slice (s=m/4) |
|---|---|---|---|
| 8  | 272 | 4 (>= MIN_FEATURIZABLE, usable)  | 2 (< 4, **must be dropped**) |
| 12 | 200 | 6 (usable) | 3 (< 4, **must be dropped**) |
| 16 | 513 | 8 (usable) | 4 (>= MIN_FEATURIZABLE, usable) |

**Resolution adopted**: pseudo-author rows with `slice_size < 4` are excluded
from every call into the deployed featurization machinery (both the D0
calibration input and the eval panel), for both crossed cells uniformly. For
`crossed_q2` this drops nothing (all slices >= 4). For `crossed_q4` this
drops 1,888 of 3,940 intended pseudo-rows (472 of 985 real authors, exactly
the `m^common in {8,12}` group) -- **only the `m^common=16` subpopulation (513
authors) is featurizable under `crossed_q4` at all**, a structural
consequence of dividing an 8-16-event budget by 4 at this event scale, not
an artifact of the truncation choice in 0.3 (no choice of "common budget"
raises the ceiling above `floor(16/4)=4`).

**A second-order, register-noted consequence discovered from this same
arithmetic**: the deployed gauge's own split-half retention floor is `>=8`
events (`MIN_RETAINED_EVENTS`, matching M4-F1/M4-E1). Since `crossed_q4`'s
largest achievable slice is 4 (< 8), **no `crossed_q4` pseudo-author row can
ever be retained for the main per-context split-half gauge, at any world,
by construction** -- this is verified, not merely predicted, in Part 1, and
is reported as a genuine `ZERO_RETAINED_PSEUDO_AUTHORS` status rather than
papered over by relaxing the retention floor (which would violate gate G3's
gauge-invariance requirement). `crossed_q2`'s main gauge remains computable,
but is restricted to the `m^common=16` subpopulation only (slice=8, the only
one meeting the `>=8` retention floor) -- **282 of 565 D1+D2 eval authors**
(confirmed in Part 1), not the full population free/shared/G1 measure. This
is a disclosed, load-bearing limitation on how the crossed_q2 main-gauge
number may be compared to the free/shared cells' (full-population) numbers.

### 0.6 The within-author cross-context contrast field (register-note: this is explicitly "a DIFFERENT typed object," constructed here)

The registration names the companion but does not give it equations (unlike
the main gauge, which the registration ties to specific verbatim functions).
Construction adopted, reusing deployed primitives wherever their shape
permits and disclosing exactly where it departs:

For each D1/D2 author whose all `Q` context-slices have `>=4` events (the
same wall as 0.5): each slice-half (seeded via the verbatim
`f1().half_indices`, budget label `crossedq{Q}`) is fed as a **single path**
(no alternating-replicate sub-split -- `Q in {2,4}` observations per author
cannot support a further 2-way split) to the verbatim
`f1().marginal_features_batch` / `transition_features_batch`, giving one
`(M_q, K_q)` pair per slice-half. The per-author **contrast matrix** is
`v8._cross_covariance(M-stack-over-Q, K-stack-over-Q)` -- i.e. the standard
field's author axis and this field's context axis are swapped: the "authors"
that the cross-covariance pools over are this ONE author's own Q
context-slices. This is intentionally **unnormalized** (no energy/soft
denominator -- `soft_relation_matrix`'s normalization needs the 2-replicate
structure this object does not have); split-half **agreement** between the
two halves' contrast matrices uses the verbatim, scale-invariant
`v8._matrix_cosine`, so the missing normalization does not affect the
agreement reading. Aggregated to one number per world (mean over eligible
authors), then across the 8 worlds for a t-test against 0 -- authors within
one world share a generative substrate and are not independent, so the world
(not the author) is kept as the unit of replication, exactly mirroring the
main gauge's own world-then-cell structure. **This object's level is never
compared to the main gauge's** (registered instruction); only presence/
absence of non-nil agreement is read.

### 0.7 The paired-seed design (register-note: a deliberate choice that strengthens, not weakens, the registered comparisons)

All four Axis-1 cells (`free_k05`, `free_k10`, `shared_k05`, `shared_k10`)
and the G4 gate cells (`free_k00`, `shared_k00`) share **one world_seed per
world index** (`seed_group="axis1"`, independent of kappa/occasion_mode) and
**one corpus string per world index** (governing split-half draw and
transition-null randomization). Consequently `z`, `zeta`, `x`, `noise`,
`loadings` -- and, for a fixed kappa, the shock draws `s_{c,t}` themselves --
are IDENTICAL across all four (plus the two gate) cells at a given world
index; only the kappa/occasion_mode-driven blend differs. This is what
licenses the registration's own required statistic, "paired-by-world
differences ... with a t-based CI," at maximal power: worlds are matched not
just nominally but at the level of the underlying random draws, so any
measured difference is attributable to the design manipulation alone. The
two crossed cells similarly share a world_seed with each other
(`seed_group="axis2"`) but not with axis-1 (a different comparison, not
required to be paired against axis-1 by the registration).

### 0.8 Gate design note

G1 and G4 are computed via the SAME general per-world engine
(`run_axis1_world`), pointed at two different seed scaffolds: G1 uses
M4-F1's own exact recipe (`seed_group="base1x"`, corpus tag `m4f1`, salt
`m4f1-world`, budget label `f1.0`, the RAW/untruncated layout) so that its
output is directly checked against `results/m4_f1_panel_sizing/cells.csv`'s
persisted `base1x` row (read at run time, never retyped, per the
instruction); G4 uses this leg's own scaffold at the common-budget layout.
G3 duplicates M4-F1's gate-1/gate-2 CHECK LOGIC (not by calling
`f1().run_gates()`, which would overwrite `results/m4_f1_panel_sizing/
gates.json`, a prior leg's artifact this leg must not touch) against the
identical underlying functions (`f1()._directions`, `f1().featurize_panel`,
`f1().half_indices`), imported unchanged.

*(Everything below this line was written after the run; nothing above was
edited after compute began.)*

---

## Part 1 -- OUTCOME

**Lean (a) HOLD, lean (b) HOLD, pivot does NOT fire -- shared-occasion design
beats free-response design at fixed total event budget, and the gain grows
with kappa exactly as the mechanism predicts. Lean (c) PARTIAL: the
companion object (0.6) is a clean, strong HOLD (t=20.5 and t=62.3 against
zero); the main-gauge "monotone decline in Q" half of lean (c) MISSES at its
one actually-measurable point (`crossed_q2`, statistically indistinguishable
from the kappa=0 reference, nominally even slightly higher) and is
structurally forced rather than measured at `crossed_q4` (main gauge
undefined by construction, per 0.5).**

Run: gates in 37s (10-core machine, 6 workers); sweep (6 cells x 8 worlds x
20 draws) in 65s; all foreground, single machine, `MASTER_SEED=20260802`
(M4-F1's own), knobs reused verbatim from M4-F1's `calibration_record.json`
(`k=48, rho=.50, w_mu=.15, w_x=.15, w_e=.70, phi in [.20,.80]`) -- **this leg
performs no new calibration search**, exactly as registered ("MASTER_SEED
and knobs exactly as M4-F1").

## Gates (all green; G4 is a stop-condition and did not fire)

- **G1** (kappa<=0 free cell reproduces M4-F1's persisted `base1x` to
  <=1e-12; target read from `results/m4_f1_panel_sizing/cells.csv` at run
  time): `agreement_mean` abs diff **9.89e-17**, `agreement_se` abs diff
  **1.12e-16**, `d0_eff_rank_M_mean` abs diff **0.0**, `d0_eff_rank_K_mean`
  abs diff **7.11e-15**, `n_retained` exact (565=565). All far inside the
  1e-12 bar -- three of the four numeric diffs are nonzero float64 rounding
  noise from summation/dispatch order; the largest (7.11e-15, eff rank K) is
  still ~140x inside the bar, the other two (~1e-16) are ~4 orders of
  magnitude inside it, and eff rank M is exactly 0.0. **PASS.**
- **G2** (exact total ALLOCATED event count across every cell): all six
  cells allocate exactly **12,784** events (`free_k05`, `free_k10`,
  `shared_k05`, `shared_k10`, `crossed_q2`, `crossed_q4`); M4-F1's raw
  base1x total is 13,202, so the common-budget truncation (Part 0.3) drops
  **418 events (3.17%)** uniformly across all six cells. **PASS.**
- **G3** (gauge invariance, M4-F1's own gate style): batched feature map vs
  the deployed `v8.build_feature_panel` -- max abs diff M = 0.0, K = 0.0
  (bit-identical); numpy halving vs `e1().split_half_frames` -- 120/120
  author-draw checks identical. **PASS.**
- **G4** (designed null: kappa=0 `shared` equals `free` cell-for-cell): all
  8 worlds match EXACTLY (`agreement_mean`, `d0_eff_rank_M`,
  `d0_eff_rank_K`, `n_retained`, and the full 20-value `draw_values` vector,
  bit-for-bit) between `free_k00` and `shared_k00`. **PASS** -- the leg is
  live.

`results/m4_f2_composition/gates.json` carries the full detail (all 8 G4
per-world rows, both G1 target and observed dicts).

## The composition-x-kappa results (Axis 1: free vs shared, kappa in {.5, 1.0})

Cell means over 8 worlds (each world's own value is the mean of 20 E1-seed-
compatible split-half draws); `n_retained=565` (all D1+D2 eval authors)
identically across all four cells, confirming the common-budget truncation
does not touch retention at this axis (`m^common>=8` for every author):

| cell | kappa | mode | agreement mean (8 worlds) | d0 eff rank M | d0 eff rank K |
|---|---|---|---|---|---|
| free_k05   | 0.5 | free   | +0.000501 | 43.72 | 39.39 |
| shared_k05 | 0.5 | shared | +0.009337 | 43.25 | 39.40 |
| free_k10   | 1.0 | free   | -0.002773 | 43.98 | 39.14 |
| shared_k10 | 1.0 | shared | +0.023390 | 42.62 | 38.32 |

**Paired-by-world (shared minus free), t-based 95% CI, df=7:**

| kappa | mean diff | sd | se | t | 95% CI | excludes 0 (>0) |
|---|---|---|---|---|---|---|
| 0.5 | **+0.008836** | 0.005284 | 0.001868 | 4.730 | [0.004418, 0.013254] | **yes** |
| 1.0 | **+0.026163** | 0.007927 | 0.002803 | 9.335 | [0.019536, 0.032791] | **yes** |

Every one of the 8 paired world-differences is individually positive at
kappa=1.0 (range +0.0148 to +0.0353); at kappa=0.5, 7 of 8 are positive
(range -0.0005 to +0.0142). Gain at kappa=1.0 is **2.96x** the gain at
kappa=0.5.

## Lean (a) and (b) adjudication

- **Lean (a) HOLD.** Registered rule: "shared - free paired-world CI
  excludes 0 (>0) at kappa=1.0 at minimum." The kappa=1.0 CI is
  [0.019536, 0.032791], entirely positive (t=9.34, nowhere near the df=7
  critical value of 2.365). The kappa=0.5 CI ALSO excludes 0
  ([0.004418, 0.013254], t=4.73) -- the registered minimum bar is cleared
  with a substantial margin at both tested kappa levels, not just the
  required one.
- **Lean (b) HOLD.** Registered rule: "gain at 1.0 > gain at 0.5." Measured
  +0.026163 > +0.008836 (ratio 2.96x). Because both cells at a given kappa
  share their entire random substrate except the kappa/mode blend (Part 0.7),
  this is a low-noise comparison, not two independently-noisy means being
  subtracted.
- **PIVOT does NOT fire.** Registered rule: fires if NEITHER kappa shows a
  CI-excluding-zero gain. Both do. **Composition-at-fixed-budget works on
  this gauge, in contrast to M4-F1's scale axes, where identical worlds
  never rose fast enough to be practically useful** (M4-F1: events-axis
  gamma=0.153, 10^14x budget to reach 0.5 agreement). The registered
  hand-off to a GAUGE-problem / M4-E2 merger is NOT issued.

## The crossed-context results (Axis 2: Q in {2,4}, kappa=0)

### Main per-context gauge

| cell | main gauge status | n retained (of how many possible) | agreement mean (worlds where computable) |
|---|---|---|---|
| kappa=0 reference (`free_k00`==`shared_k00`, G4) | OK | 565 | +0.006611 (se 0.003122, 8 worlds) |
| crossed_q2 | OK, but **restricted population** | 564 (only the `m^common=16` subgroup, 282 of 565 D1+D2 authors x 2 slices) | +0.009213 (se 0.005504, 8 worlds) |
| crossed_q4 | **`ZERO_RETAINED_PSEUDO_AUTHORS`, all 8/8 worlds** | 0 (structurally impossible: max slice=4 < the gauge's own >=8 retention floor) | undefined |

`crossed_q2`'s D0 calibration ran on the full panel (1970/1970 pseudo-rows
usable, nothing dropped, since `m^common/2 in {4,6,8}` all clear the
featurizability wall); its main-gauge EVAL population is nonetheless
restricted to 282 D1+D2 authors (the `m^common=16` subgroup) because only
their slices (`s=8`) clear the gauge's OWN `>=8` retention floor -- **the
crossed_q2 vs reference comparison below is confounded by this population
restriction and is disclosed as such, not corrected for** (correcting it
post hoc would be exactly the kind of rescue the process rules forbid).
`crossed_q4`'s D0 calibration itself succeeds (924 D0 pseudo-rows from the
513 `m^common=16` authors, far above the 24-row floor; effective ranks M
39.72 / K **9.21**, consistent with M4-F1's own quarter-budget K-collapse
mechanism at short paths -- an independent replication of that finding, not
a new one), but eval retention is exactly zero at every world, as predicted
by pure arithmetic in Part 0.5 before any compute ran.

**crossed_q2 vs the kappa=0 reference (unpaired -- these cells do not share
a seed group, Part 0.7):** mean difference +0.002601, combined SE
(independent-cells approximation) 0.006327, t~0.41 -- **not distinguishable
from zero.** If anything the crossed_q2 point estimate is nominally above
the reference, not below it.

### The companion: within-author cross-context contrast field

| cell | n eligible D1/D2 authors | mean (8 worlds) | se | t vs 0 |
|---|---|---|---|---|
| crossed_q2 | 565 (all; every slice >=4) | +0.008195 | 0.000400 | **20.47** |
| crossed_q4 | 282 (only `m^common=16`, matching the featurizability wall) | +0.025114 | 0.000403 | **62.28** |

Both comfortably clear the registered `t>2` non-nil bar, by an order of
magnitude. `crossed_q4`'s companion is measurable and strongly non-nil on
EXACTLY the same 282-author subpopulation whose main gauge is undefined --
the clearest instance of the registration's own framing: *"pairing buys a
DIFFERENT certifiable object, not a better version of the same one."*
Companion levels are never compared to the main-gauge levels (registered
instruction); the `crossed_q4`-over-`crossed_q2` companion ratio (3.06x) is
reported as a same-object internal comparison only.

## Lean (c) adjudication

Registered rule, two parts: **(c1)** "Crossed authors HURT the deployed
per-context gauge (monotone decline in Q ...)"; **(c2)** "the paired-contrast
companion shows non-nil agreement at Q>=2 (t>2 against its own zero)."

- **(c1) MISS at its one measurable point.** `crossed_q2`'s main-gauge mean
  (+0.009213) is NOT below the kappa=0 reference (+0.006611) -- the
  unpaired difference is small and positive (t~0.41), i.e. statistically
  indistinguishable from no change, nominally even slightly higher.
  `crossed_q4` never produces a main-gauge number at all
  (`ZERO_RETAINED_PSEUDO_AUTHORS`, all 8 worlds) -- this is the most extreme
  possible instance of "the gauge cannot use crossed data," but it is a
  STRUCTURAL non-computability forced by event arithmetic (Part 0.5), not a
  measured decline on a numeric curve, so it cannot be used to claim
  "monotone decline" was observed -- only that the crossed_q4 arm never
  reaches the point where decline could even be measured. Read plainly:
  the registered monotone-decline claim is not supported by what was
  actually measurable.
- **(c2) HOLD, decisively.** Both `crossed_q2` (t=20.47) and `crossed_q4`
  (t=62.28) clear `t>2` by more than an order of magnitude.
- **Lean (c) overall: PARTIAL.** The companion half of the claim (a
  different, pairing-specific certifiable object exists and is strongly
  non-nil) is fully supported; the main-gauge-decline half is not supported
  at the one point where it could be measured, and is undecidable (not
  "supported by an extreme case") at the other.

## What the results say (interpretation, hedged)

**Axis 1 is the clean result of this leg.** M4-F1 established that
NO feasible SCALE increase reaches useful split-half agreement on the
deployed gauge (events-axis exponent 0.153, budget 10^14x). This leg shows
that at the EXACT SAME total event budget, changing WHICH occasions are
shared moves the gauge by +0.0088 (kappa=.5) to +0.0262 (kappa=1.0) --
roughly 2-5x the base1x reference level itself (+0.0047, M4-F1's own
persisted number, reproduced here as G1). The mechanism argument
(occasion-sampling nuisance is pure between-half noise under `free`, removed
by construction under `shared`) is directly supported by the fact that the
gain SCALES with kappa (the parameter that literally controls how much
shared-vs-private variance exists) rather than appearing as a fixed offset.
This is the registered hand-off from M4-F1 working as designed: composition,
not scale, is the lever.

**Axis 2 is a genuinely two-sided result, not a clean win.** The
"crossing hurts the SAME OBJECT, buys a DIFFERENT one" story only half
survives contact with this event budget. The companion object's success is
real and large (t in the tens, not a knife-edge) -- there plainly is
non-nil, poolable cross-context structure inside a single author's data,
recoverable at both Q=2 and Q=4, including on the very authors whose main
gauge cannot be computed. But the specific mechanism registered for WHY
crossing should hurt the main gauge (thinner per-context-slice budgets
following M4-F1's own events-axis law) does not show up as a measured
decline where it is actually testable -- most likely because `crossed_q2`'s
main-gauge comparison is not on a matched population (Part 0.5's disclosed
confound: only the richest-budget authors survive its retention floor,
so the comparison is "richest-budget authors, crossed" vs "everyone,
uncrossed," not a clean composition-only contrast). This is a genuine,
disclosed limitation of what this leg can say about the main-gauge half of
lean (c), not a finding that crossing is neutral or beneficial for the main
gauge.

## Honest anomalies and disclosures

1. **The crossed_q2 main-gauge population confound (Part 0.5, 0.6).** The
   564/565 retained pseudo-rows for `crossed_q2` come exclusively from the
   282 authors whose original `m=16` -- the single richest-budget subgroup.
   The kappa=0 reference and every axis-1 cell measure the FULL 565-author
   population. The lean-(c1) MISS above is reported on this
   population-mismatched comparison as computed; no attempt was made to
   restrict the reference to the matching 282-author subpopulation after
   seeing the result (that would be a post-hoc rescue/attack the process
   rules forbid either direction of).
2. **`crossed_q4`'s main gauge is undefined by construction, not by an edge
   case that happened to bite.** Verified by exact pre-compute arithmetic
   (Part 0.5: max slice 4 < the gauge's own retention floor 8, true for
   every one of the 985 authors) before any Monte Carlo run, and then
   confirmed empirically at all 8/8 worlds. No retention-floor relaxation was
   applied (that would break gate G3's gauge-invariance requirement).
3. **G1's three nonzero diffs (7.11e-15 on eff rank K, 1.12e-16 on
   agreement_se, 9.89e-17 on agreement_mean)** are floating-point
   summation-order noise (multi-process dispatch across 6 workers vs however
   M4-F1's own persisted run was dispatched) -- the largest is still ~140x
   inside the 1e-12 bar, the other two ~4 orders of magnitude inside it --
   reported exactly, not rounded away.
4. **The companion object's construction (Part 0.6) is this leg's own,
   not equation-pinned by the registration.** It deliberately reuses
   verbatim low-level primitives (`marginal_features_batch`,
   `transition_features_batch`, `v8._cross_covariance`, `v8._matrix_cosine`)
   but skips the alternating-replicate split and the soft/energy
   normalization the main gauge's `soft_relation_matrix` uses, because `Q in
   {2,4}` cannot support either. Its LEVEL is not comparable to the main
   gauge's level (registered instruction, respected throughout); its
   `crossed_q4`-vs-`crossed_q2` ratio (3.06x) is an internal, same-object
   comparison only.
5. **D0 effective-rank drift under crossing** (`crossed_q4`: M 39.72, K
   **9.21**) reproduces M4-F1's own quarter-budget K-collapse mechanism
   (short paths collapse the K-family's effective rank sharply, PANDORA
   real-text collapse was 38.5 -> 8.48 at a 4-event quarter-budget) as an
   independent, unregistered but consistent replication -- reported as
   context, not as a fourth lean.
6. **No new calibration search was run.** Per the registration
   ("MASTER_SEED and knobs exactly as M4-F1"), the knobs are read verbatim
   from `results/m4_f1_panel_sizing/calibration_record.json`
   (`k48-r0.50-mu0.15-x0.15-e0.70-p0.20_0.80`); this leg's own compute begins
   at the gates.
7. **Axis-1's shared world-seed design (Part 0.7)** is a deliberate choice
   that increases statistical power for the registered paired comparison; it
   also means the four axis-1 cells are not four independent 8-world
   experiments but one shared 8-world random substrate viewed through four
   lenses. This is disclosed rather than hidden because it is exactly what
   the registration's own required statistic ("paired-by-world differences")
   presupposes.

## Decision boundary

Exploratory, synthetic-calibrated, label-free. This leg licenses a D3
panel-COMPOSITION design prior: at a fixed, already-scale-exhausted event
budget, moving from free-response to shared-occasion collection design
measurably improves the deployed field's own split-half agreement gauge
(the composition hand-off from M4-F1 is empirically supported on Axis 1);
within-author cross-context pairing produces a real, strongly non-nil, but
DIFFERENT, object (Axis 2's companion), while its effect on the SAME
main-gauge object the registration hoped to see decline is not established
at this budget (population-confounded where measurable, structurally
undefined otherwise). It makes no claim about the real relation field's
content, about personality, emotion, diagnosis, or any individual, and does
not certify (or refute) any real-text relation structure. Artifacts:
`results/m4_f2_composition/{decision.json, gates.json, axis1_cell_*.csv,
axis1_draws_*.csv, axis2_cell_*.csv}`.
