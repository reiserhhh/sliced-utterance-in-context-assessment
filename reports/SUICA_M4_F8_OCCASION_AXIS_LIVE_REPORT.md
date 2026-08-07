# SUICA M4-F8 -- The Decisive Occasion Cell: Live Channel, Adequate Power (Authors x16, Kappa=0.5)

> **BANNER: synthetic worlds calibrated to an opened-panel regime, exploratory.**
> This leg consumes NO new real-text evidence. It repeats M4-F7's occasion-
> spread sweep at kappa=0.5 instead of kappa=1.0, reusing M4-F7's own
> generalized (author_mult-parametrized), already kappa-parametrized
> per-world engine VERBATIM, by direct call into F7's own module. No label
> columns anywhere; no claim about the real relation field's content,
> personality, emotion, diagnosis, or any individual.

Registered spec: `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md`
section "M4-F8 registration (2026-08-03, BEFORE run) -- the decisive cell:
live channel, adequate power", together with the preceding "M4-F7 planner
adjudication note -- the closure is NOT earned" (the standing rule this leg
exists to satisfy). Script:
`scripts/run_suica_m4_f8_occasion_axis_live.py`. Artifacts:
`results/m4_f8_occasion_axis_live/`.

**Headline, stated up front so it is not buried: this leg VOIDS on a
mechanical gate (G5, decorrelation) that every prior leg in this line has
passed. G0 (power) and G6 (channel liveness, new) both PASS -- the first
M4-F leg to be both adequately powered and causally live -- but per the
pre-existing, verbatim-reused G5 rule, a mechanical gate failure voids the
leg regardless. The decisive test the registration sought remains formally
unresolved. Full numbers under a disclosed alternate reading are given below
and are NOT adopted.**

## Part 0 -- REGISTERED ADJUDICATIONS AND OPERATIONALIZATIONS (written before the run)

The registration fixes the design as "identical to M4-F7 in every respect
except kappa": shared-occasion design, kappa=0.5, authors x16, common-budget
construction, block count B in {1,2,4,8}, M4-F6's own verified 40-step gap,
8 worlds x 20 draws, both M4-F5 truth variants at every cell. It mandates a
NEW gate, G6 CHANNEL LIVENESS, alongside the now-standard G0 POWER, and
requires both to be reported first. Every implementation choice below was
fixed in the script BEFORE any of the six `--stage` calls (`g6`, `anchor`,
`construction-check`, `sweep`, `gates`, `finalize`) was run.

### 0.1 Reuse boundary

Directly imported/called, never reimplemented: `f1().knob_tag` (main() only
-- every other F1 call this leg needs happens inside F7's own already-loaded
functions); `f2().run_gate_g1`, `f2().shock_vector` (from
`scripts/run_suica_m4_f2_composition.py`); `f3().run_gate_g3` (from
`scripts/run_suica_m4_f3_composition_scaling.py`); `f4().build_live_tasks`
(from `scripts/run_suica_m4_f4_author_axis.py`); `f5().run_truth_sweep_world`,
`f5().G4_TOLERANCE` (from `scripts/run_suica_m4_f5_gauge_validity.py`);
`f6().GAP`, `f6().M_COMMON`, `f6()._paired_ci`, `f6().spread_world_seed_for`,
`f6().g5_world_correlation`, `f6().block_layout`,
`f6().block_occasion_labels`, `f6()._draw_common_state`,
`f6()._draw_ar1_span`, `f6().generate_world_spread` (from
`scripts/run_suica_m4_f6_occasion_spread.py`) -- ALL called directly,
unchanged. **`f7().common_layout_scaled`, `f7().run_spread_sweep_world`**
(from `scripts/run_suica_m4_f7_occasion_axis_powered.py`) -- called
DIRECTLY, UNCHANGED, for EVERY per-world computation. This is the leg's
central reuse commitment and the reason this script needed NO new per-world
engine at all: F7's own `run_spread_sweep_world` already reads
`task["kappa"]` and `task["author_mult"]` dynamically from the task dict,
not from any module constant, so it was already kappa- and
scale-parametrized before this leg touched it.

Newly written, because F7 hardcodes `KAPPA_TAG="k10"`/`KAPPA=1.0` as
MODULE-LEVEL constants inside its own task/cell-name builders (not as
task-dict parameters): `cell_name_spread_x16`, `build_spread_tasks`,
`build_construction_check_task`, `build_anchor_task` -- disclosed thin
near-duplicates of F7's own same-named functions, re-pointed at
`KAPPA_TAG="k05"`. `cell_summary` and gates G1 (thin direct-call
wrapper)/G2/G3 (thin direct-call wrapper)/G4/G5, OUT-scoped to this script's
own artifact tree (every leg's `cell_summary`/gates has been OUT-scoped even
when the underlying rule is reused verbatim). The G0 POWER gate, re-targeted
at M4-F5's `authors_x16_shared_k05` and the registration's own `.0407` bar.
**The G6 CHANNEL LIVENESS gate, wholly new** (0.4 below). The adjudication
code (leans a/b/c, the pivot, now gated on BOTH G0 and G6).

### 0.2 G2's disclosed ambiguity resolution

The registration's own text: "the raw `authors_x16_shared_k05` anchor must
reproduce M4-F5's persisted cell (agreement + BOTH truth variants) to
<=1e-12; **the B=1 sweep cell must reproduce M4-F7's construction where
comparable**." The first clause is unambiguous and is G2(b) below. The
second is genuinely ambiguous: F7 itself computed NO kappa=0.5 cells
anywhere (its own registration explicitly scoped it out), so there is no F7
NUMBER to reproduce at kappa=0.5.

**Reading 1 (adopted):** "M4-F7's construction" means F7's own generalized,
`author_mult`-parametrized ORCHESTRATION (the code path, reused here via
direct calls into `f7().common_layout_scaled`/`f7().run_spread_sweep_world`)
applied at kappa=0.5, checked against the one persisted object that IS
numerically comparable at this kappa: M4-F6's own `b1_shared_k05` (exactly
mirroring what F7 itself did for k10 against F6's `b1_shared_k10`). Adopted
because it is the only reading that admits an actual `<=1e-12` numeric
check, and it directly parallels F7's own G2(a) structure, which the
registration explicitly invokes ("state which object each check uses, as
M4-F7 did").

**Reading 2 (not adopted):** "the B=1 sweep cell" refers to the actual
adjudicated `b1_x16_shared_k05` cell itself (not a separate construction-
check cell), and "reproduce M4-F7's construction" is read as a pure
code-reuse requirement with no numeric comparison at all (since F7 has no
k05 numbers to diff against). This reading is not rejected as wrong, but
Reading 1 is adopted because it is strictly more informative (it adds a real
numeric check where Reading 2 would add none) and follows the established
G2(a)/G2(b) two-sub-check pattern F7 itself used.

Implemented as G2(a) CONSTRUCTION (`construction_check_mult1_b1_k05`, mult=1/
block_count=1/kappa=0.5, via F7's own generalized orchestration using F6's
own seed_key `"b1_k05"`/corpus-prefix `"m4f6-"`/budget_label `"f6.0"`, vs.
M4-F6's persisted `b1_shared_k05`) and G2(b) ANCHOR (the RAW
`authors_x16_shared_k05` cell, `f5().run_truth_sweep_world` unchanged on
`f4()`'s own byte-identical mult=16/k05 task, vs. M4-F5's persisted
`authors_x16_shared_k05` -- the same row G0 reads, for a different purpose).

### 0.3 G0 POWER, operationalized

Identical construction to F7's own G0: report the target's measured level at
this scale, read verbatim from `results/m4_f5_gauge_validity/cells.csv` row
`authors_x16_shared_k05` (never retyped), and the minimum detectable paired
difference this design's REALIZED SEs afford, computed as the 95% CI
half-width of the paired-by-world `b8_x16 - b1_x16` difference on
`truth_recovery_long`, using `f6()._paired_ci` verbatim. **FAILS
(UNDERPOWERED) if that half-width exceeds `G0_HALF_WIDTH_BAR=0.0407`**
(half of the target's `.081307` level, per the registration).

### 0.4 G6 CHANNEL LIVENESS, operationalized (the leg's central new gate)

**(i) Analytic.** The AR(1) state's own blend coefficient,
`math.sqrt(max(0.0, 1.0 - kappa))`, computed via the IDENTICAL expression
`f6().generate_world_spread` uses internally (not retyped-and-hoped), at
kappa=0.5: `0.7071067811865476` -- non-zero by construction.

**(ii) Empirical.** `_g6_state_ablation_events` is a disclosed structural
near-duplicate of `f6().generate_world_spread`'s own draw sequence
(identical prefix -- `f6()._draw_common_state`, `f6()._draw_ar1_span`, the
noise draw, `mean_part`, `f6().block_occasion_labels`, the
`f2().shock_vector` cache loop, all in the same order with the same
`world_seed`), assembling TWO events arrays per world instead of one:
**INTACT** (mean_part + state_part computed from the real kappa-blend,
bit-identical to the real generator's own output -- verified, not merely
asserted, 0.7 below) and **STATE_ZEROED** (identical except `x_at_labels`'s
own contribution to the blend is dropped; `shock_x`, `mean_part`, and the
noise draw are UNCHANGED and IDENTICAL across both variants, isolating
exactly what the AR(1) state ITSELF -- not `shock_x`, not `mean_part` --
contributes). "Between-author variance of the assembled events" is
operationalized as the trace of the between-author covariance matrix of each
author's own mean event vector (averaged over that author's `m_common`
observed occasions, summed across the 64 raw event dimensions) -- computed
over ALL authors in the `author_mult=16` layout, not the retained/resolved
D1/D2 subset downstream of D0 calibration, since this is disclosed here as a
property of the GENERATOR's own output, not the deployed pipeline.

G6 is computed at kappa=0.5, `block_count` in `{1, 8}` (the two endpoints
the pivot itself compares -- not all four block counts, since G6's purpose
is to certify the channel for the SAME B8-vs-B1 comparison the leans use,
and this keeps compute minimal), using the SAME `seed_key`
(`"b1_x16_k05"`/`"b8_x16_k05"`) the actual adjudicated sweep cells use --
hence bit-identical world draws to the b1/b8 cells the leans are computed
on, not a separately-seeded proxy. A non-gating context row at kappa=1.0,
`block_count=1`, reuses F7's OWN seed_key (`"b1_x16_k10"`), hence F7's own
bit-identical world draws -- expected to read a ratio of 1.0 exactly, since
M4-F6's/M4-F7's own algebra established the channel is EXACTLY inert at
kappa=1.0.

**Aggregation and pass rule (disclosed ambiguity resolution).** The
registration gives no numeric "materiality" bar beyond "indistinguishable
from zero" -- no magnitude cutoff is specified. Two readings were available:
(a) a pure significance test (does the ratio differ from 1.0 at all,
statistically), or (b) a significance test PLUS an invented minimum-magnitude
bar (e.g., ratio >= 1.10). **Reading (a) is adopted**: per-world log-ratio
(`log(v_intact/v_zeroed)`), aggregated across the 8 worlds via
`f6()._paired_ci` (identical construction to every paired statistic in this
line), with G6 PASSING (channel LIVE) iff the CI excludes 0 on the positive
side at BOTH `block_count in {1, 8}`. This mirrors this line's own
established "indistinguishable from zero" idiom in the opposite direction --
exactly as F7's own Part 0.7 did for G5 relative to F1's threshold -- and
avoids inventing an arbitrary magnitude bar the registration never specified.
The raw point-estimate ratios ARE prominently reported (Part 1) so a reader
can independently judge magnitude/materiality; see the Honest disclosures
section for why that magnitude turns out to matter a great deal to how this
leg's finding should be read regardless of adjudication.

**Internal-consistency safeguard (not itself a registered gate).** A
one-time check (kappa=0.5, `block_count=1`, world 0) that the ablation
helper's own INTACT reconstruction is bit-identical to
`f6().generate_world_spread`'s real output for identical inputs. A failure
here would indicate a code defect in the ablation helper, not a scientific
finding about channel liveness, so it is treated like G1-G5 (raises in
`run_gates`, voids the leg as a mechanical defect) rather than folded into
G6's own "channel_live" pass/fail.

### 0.5 Lean and pivot operationalizations

Unchanged from F7 in every respect (same three leans, same lean-(b)
inapplicable-on-non-positive-gain rule, same lean-(c) two-reading
disclosure), with the pivot's `adequately_powered` clause now conjoined with
a `causally_live` clause (`g0["pass"] and g6["pass"]`), per the
registration's own explicit "adequately powered (G0) AND causally live (G6)
AND ... " pivot text.

### 0.6 M_COMMON and GAP -- reused verbatim, not re-derived

`M_COMMON=8` and `GAP=40` are read directly as `f6().M_COMMON`/`f6().GAP`,
identical to F6's and F7's own values, never redefined -- including after
observing G5's failure (0.9 below); the registration's own explicit
instruction ("Do NOT increase the gap and re-run silently") is honored.

### 0.7 Budget/gate scope summary

Six cells computed: the RAW gate-anchor (`authors_x16_shared_k05`, 211,232
events, G0's target AND G2(b)'s target), the gate-only construction-check
(`construction_check_mult1_b1_k05`, 7,880 events, G2(a)'s target), and the
four adjudicated common-budget cells (`b{1,2,4,8}_x16_shared_k05`, 126,080
events each, identical across every swept B). Gates: **G0** (0.3) POWER.
**G1** (direct call, `f2().run_gate_g1`). **G2** (0.2) -- construction +
anchor, both to <=1e-12. **G3** (direct call, `f3().run_gate_g3()`). **G4**
(identical mechanism to M4-F5/M4-F6/M4-F7) -- truth-path invariance across
all 6 computed cells. **G5** (F6's own per-cell `|t|<2.0` rule, reused
verbatim, 3 cells). **G6** (0.4, new) -- channel liveness.

### 0.8 Timing pilot (before the full sweep, per the task's own instruction)

A single-world pilot, run in-process before any `--stage sweep` call:
`b1_x16_k05` world 0 took 56.57s, `b8_x16_k05` world 0 took 59.45s --
matching F7's own pilot numbers (56.6s/59.6s) almost exactly, confirming
kappa does not change per-world compute cost. Extrapolated total: G6 ~15s,
anchor ~200s, construction-check ~10s, sweep ~4 cells x 130-155s
(8-way parallel), gates+finalize under 2 minutes -- consistent with what was
observed (0.11 below).

### 0.9 Self-reported script addition, made AFTER observing G5's failure (disclosed, not a rescue)

The ORIGINAL script (mirroring F7's own structure) assumed `run_finalize()`
would never be reached after a G1-G5 gate failure, because `run_gates()`
raises and halts the pipeline before `finalize` runs, in the SAME invocation
-- exactly F6's and F7's own discipline, and exactly what happened here: G5
failed, `--stage gates` raised, execution stopped. Running each stage as a
SEPARATE foreground call (required by this task's own 120-second-per-call
chunking constraint, since a single `--stage all` invocation exceeds it at
this scale) meant `--stage finalize` had to be invoked independently
afterward, and the original `run_finalize()` had no code path for "gates.json
already shows a mechanical failure." **A branch was added to
`run_finalize()` AFTER this failure was observed** that checks
`gates["mechanical_gates_pass"]` first and, if false, writes a complete
`VOID_MECHANICAL_GATE_FAILURE` decision (full G0/G6 statements, the failing
gate's own detail, and a disclosed "Reading 2" side computation using the
UNMODIFIED `adjudicate()` function, explicitly labeled NOT ADOPTED) instead
of proceeding to adjudicate. This addition does not touch GAP, the `|t|<2.0`
threshold, kappa, block counts, the lean rules, the pivot rule, or any other
scientific/design parameter -- it only prevents silent adjudication past a
gate whose own established consequence is to void the leg. Full self-report,
including the addition's exact diff intent, is repeated in Honest
disclosures below.

---

*(Everything below this line was written after the run. Part 0 above -- and
the script that implements it, except for the disclosed 0.9 addition, made
for reporting completeness after observing a gate failure, not to change any
scientific parameter -- was not edited after compute began.)*

## Part 1 -- OUTCOME

### G0 POWER -- reported first, as mandated

**ADEQUATELY POWERED.** Target level, read verbatim from M4-F5's own
persisted `authors_x16_shared_k05` row: long-window truth recovery
**0.081307 +/- 0.010920** (matches the registration's cited number exactly).
This leg's own realized paired-by-world `b8_x16 - b1_x16` difference on
`truth_recovery_long`: mean **-0.036177**, SD 0.037991, SE 0.013432 (n=8,
df=7), t=-2.693, 95% CI **[-0.067938, -0.004416]**. **Minimum detectable
paired difference (95% CI half-width): 0.031761** -- inside the registered
`.0407` bar (78.0% of it). **G0 PASSES.**

### G6 CHANNEL LIVENESS -- reported first, as mandated, and the leg's most valuable byproduct

**Analytic:** `sqrt(1 - 0.5) = 0.7071067811865476`, non-zero.
**Internal-consistency check:** max abs diff between the ablation helper's
own INTACT reconstruction and `f6().generate_world_spread`'s real output,
same inputs: **exactly 0.0**. **PASS.**

**Kappa=1.0 context row (non-gating validation, F7's own world draws).**
Between-author variance with the state intact vs. state-zeroed is
**bit-identical at all 8 of 8 worlds** (e.g. world 0: 0.503271 vs 0.503271;
world 5: 0.510021 vs 0.510021) -- ratio **exactly 1.000000** everywhere,
log-ratio exactly 0.0. This is not merely consistent with M4-F6's/M4-F7's
own algebraic finding that `blended_x = shock_x` at kappa=1.0 -- it
**converts that code-reading argument into a directly measured empirical
fact**: with `x`'s own contribution multiplied by `sqrt(1-1)=0` exactly,
zeroing it changes NOTHING, to full floating-point precision, regardless of
the specific random draw. The planner's own inference in the M4-F7
adjudication note is independently confirmed, not merely re-asserted.

**Kappa=0.5 gating rows (this leg's own kappa).**

| block_count | v_intact (mean) | v_state_zeroed (mean) | ratio (mean) | log-ratio 95% CI | live |
|---|---|---|---|---|---|
| 1 | 0.538667 | 0.489913 | **1.0995** | [0.09435, 0.09540] | YES |
| 8 | 0.507451 | 0.488762 | **1.0382** | [0.03719, 0.03786] | YES |

Both CIs exclude 0 on the positive side by a wide margin (t=428.7 and
t=266.5 respectively -- unsurprising given each world pools variance
estimates over 15,760 authors x 64 dimensions, so world-to-world sampling
noise is tiny relative to a real, reproducible effect; per-world ratios are
tightly clustered: 1.0984-1.1005 at B=1, 1.0377-1.0390 at B=8, across all 8
independently-seeded worlds). **CHANNEL LIVE at both tested block counts.
G6 PASSES.**

**The magnitude matters and is stated plainly here, not buried.** The state
accounts for only **~9-10% of between-author variance at B=1**
(`(0.538667-0.489913)/0.489913 = 9.95%` relative to the zeroed baseline) and
**~4% at B=8** (`(0.507451-0.488762)/0.488762 = 3.82%`). The channel is
REAL and STATISTICALLY UNAMBIGUOUS -- not a rounding artifact, not sampling
noise -- but it is a MINORITY contributor to between-author heterogeneity in
the assembled events at this kappa; `mean_part` (the fixed, per-author trait
term, equally weighted at `w_mu=w_x=0.15`) and the noise floor
(`w_e=0.7`, dominant) together account for the remaining ~90-96%. **This is
a genuine limitation on what any null (or non-null) found on this channel
can conclude, independent of how the adjudication below resolves**: a
finding here bears on whether spreading occasions helps THROUGH a channel
that is real but modest, not through a channel that dominates the panel's
own between-author signal. It belongs in this leg's limitations regardless
of which way the pivot would have gone.

### Gates G1-G5

- **G1** (direct call, `f2().run_gate_g1`): diffs ~1e-16/1e-17 range,
  `n_retained` exact (565). **PASS.**
- **G2(a) CONSTRUCTION**: `construction_check_mult1_b1_k05` (computed
  through F7's own generalized orchestration) vs. M4-F6's persisted
  `b1_shared_k05`: max abs diff **5.55e-17**; `n_retained` exact (565).
  **PASS.**
- **G2(b) ANCHOR**: the RAW `authors_x16_shared_k05` cell vs. M4-F5's
  persisted `authors_x16_shared_k05`: max abs diff **4.86e-17**;
  `n_retained` exact (9040). **PASS.**
- **G3** (direct call, `f3().run_gate_g3()`): batched feature map bit-
  identical (`max_abs_diff_M`/`K` = 0.0); halving identical (120/120
  checked). **PASS.**
- **G4** (truth-path invariance): max diff across all 6 computed cells is
  **exactly 0.0** on every single cell. **PASS.**
- **G5** (decorrelation, F6's own rule reused verbatim): **FAILS.**

| block_count | correlation_mean | correlation_se | t_stat | n_pairs/world | pass |
|---|---|---|---|---|---|
| 2 | -0.000177 | 0.000613 | -0.289 | 756,480 | yes |
| 4 | **+0.000552** | 0.000158 | **+3.497** | 2,269,440 | **NO** |
| 8 | -0.000219 | 0.000159 | -1.383 | 5,295,360 | yes |

`b4_x16_shared_k05` has `|t|=3.497 >= 2.0`. Per F6's own Part 0.7 rule,
reused verbatim by F7 and by this leg (required reading for this task): **a
`|t|>=2.0` at ANY tested cell VOIDS the leg.**

## THE VOID DETERMINATION

**This leg VOIDS on G5.** Both G0 and G6 -- the two gates the task's own
registration summary flags as leg-voiding -- PASS cleanly. But G5, a
pre-existing gate this task's required reading explicitly directs be reused
"VERBATIM" (including its established consequence, not merely its
correlation arithmetic), FAILS. This produces a genuine ambiguity, disclosed
here with numbers under both readings, per this task's own process rules.

**The question:** does a G1-G5 mechanical-gate failure void the leg even
though G0 and G6 both pass, or does the task prompt's summary line ("Gates
(six; G0 and G6 are the ones that can void the leg)") mean only G0/G6 govern
voidability for this specific registration, so adjudication should proceed
despite the G5 failure?

**Reading 1 (ADOPTED): the leg is VOID.** G5 retains its pre-existing,
verbatim-reused consequence (M4-F6's own Part 0.7 rule, explicitly required
reading for this task: "A `|t|>=2.0` at ANY tested cell VOIDS the leg per
the registration," unchanged through M4-F7 and this leg). Adopted for two
reasons. First, weakening an established, explicitly-required-reading
safeguard specifically because it produced an inconvenient result here is
exactly the kind of post-hoc softening this task's own process rules forbid
("no post-hoc rescues... no softening a miss"). Second, the task's own
summary line is better read as flagging the two NEW standing-rule gates this
registration introduces (the ones needing fresh "valid scientific outcome,
not a code defect" semantics) rather than as silently overruling G5's own
pre-existing, three-legs-deep, unqualified rule. Under this reading: **no
lean, no pivot, no closure claim is licensed by this leg.**

**Reading 2 (NOT ADOPTED, given in full for transparency).** If the task's
summary parenthetical is instead read as an exhaustive, leg-specific
override making G5 non-voiding for M4-F8 specifically, adjudication would
proceed on the already-collected data, with the G5 failure disclosed as a
caveat rather than a trigger. Under this reading, using the SAME
`adjudicate()` function unmodified:

- **Lean (a)**: paired-by-world `b8_x16-b1_x16` truth-recovery-long diff
  mean **-0.036177**, SE 0.013432, 95% CI **[-0.067938, -0.004416]** --
  excludes zero on the NEGATIVE side. **MISS** (same statistic as G0's own
  power computation, since both use the identical paired construction).
- **Lean (b)**: **INAPPLICABLE** (`ci_long["mean"]=-0.036177 <= 0`, the
  long-window "gain" is not positive).
- **Lean (c)**: agreement at B in {1,2,4,8}: 0.19279/0.19160/0.17856/0.17330
  -- B=1 reference 0.19279, +/-20% band [0.15423, 0.23135]; every value
  falls inside. **HOLD.**
- **Pivot**: `adequately_powered=true` (G0), `causally_live=true` (G6),
  `no_rise_condition=true` (CI excludes zero, negative side) ->
  **FIRES.** Would-be verdict:
  `CLOSURE_EARNED_TRAIT_LEVEL_UNCERTIFIABLE_ON_ALL_THREE_PANEL_AXES`.

This is NOT adopted as this leg's finding. It is reported in full so a
reader who disagrees with Reading 1's adoption has everything needed to
reach their own conclusion, and because it shows the substantive numbers are
NOT the reason for the void -- the void is purely a gate-discipline
question, not an ambiguous or borderline substantive result.

## Budget conservation (diagnostic, verified exactly)

Every one of the 4 adjudicated `b{1,2,4,8}_x16_shared_k05` cells allocates
**exactly 126,080 events** (`15,760 authors x M_COMMON=8`), identical across
every swept B -- matching M4-F7's own identical-budget cells exactly. The
RAW gate-anchor allocates 211,232 events, matching M4-F7's own
`authors_x16_shared_k10` total exactly (author replication does not depend
on kappa). The construction-check allocates 7,880 events (`985 x 8`),
matching M4-F6's own `b1_shared_k05` total exactly.

## The full B-vs-metrics table (kappa=0.5, reported regardless of the void, per this line's own full-disclosure convention)

| B | agreement | agreement SE | truth A (same-occasion, exact) | truth A SE | truth B (long-window) | truth B SE |
|---|---|---|---|---|---|---|
| 1 | 0.192791 | 0.008508 | 0.347591 | 0.010525 | **0.070522** | 0.009431 |
| 2 | 0.191597 | 0.011996 | 0.344104 | 0.006592 | **0.064198** | 0.009042 |
| 4 | 0.178556 | 0.010736 | 0.335649 | 0.006671 | **0.071580** | 0.010945 |
| 8 | 0.173299 | 0.010809 | 0.314659 | 0.005780 | **0.034345** | 0.009704 |

Context rows: RAW gate-anchor `authors_x16_shared_k05` -- agreement
0.095219, truth A 0.323159, truth B 0.081307 (matches M4-F5's persisted
value to <=1e-12, per G2(b)). Construction-check
`construction_check_mult1_b1_k05` (mult=1) -- agreement 0.010993, truth A
0.148493, truth B 0.019555 (matches M4-F6's persisted `b1_shared_k05` to
<=1e-12, per G2(a)).

Truth B is again **non-monotonic** across B in {1,2,4}: essentially flat
from B=1 (0.0705) to B=2 (0.0642) to B=4 (0.0716), then drops at B=8
(0.0343) -- the same qualitative pattern M4-F7 found at kappa=1.0 (a rise
or plateau through B=4, a sharp drop at B=8), now also present at kappa=0.5.

**Per-world detail (kappa=0.5, `truth_recovery_long`, paired by world index):**

| world | B=1 | B=8 | B8-B1 |
|---|---|---|---|
| 0 | 0.074891 | 0.031825 | -0.043067 |
| 1 | 0.083817 | 0.045602 | -0.038215 |
| 2 | 0.105992 | 0.033390 | -0.072602 |
| 3 | 0.096480 | 0.003697 | -0.092783 |
| 4 | 0.040334 | 0.066507 | +0.026173 |
| 5 | 0.052342 | 0.053614 | +0.001272 |
| 6 | 0.079026 | 0.054608 | -0.024418 |
| 7 | 0.031297 | -0.014482 | -0.045779 |

**6 of 8 world-index pairs are negative** (less unanimous than M4-F7's own
8-of-8 at kappa=1.0, but still the clear majority driving the significant
paired mean).

## Interpretation: two post-hoc readings, clearly separated from the VOID adjudication above (not registered claims)

**On G6's own magnitude pattern.** The live channel's own share of
between-author variance SHRINKS as block_count rises (9.95% at B=1 -> 3.82%
at B=8) -- G6 was computed only at the two endpoints, but the direction is
suggestive. A plausible mechanism (post-hoc, not tested by any registered
gate here): as occasions spread further apart, each author's own `m_common`
observed values of the AR(1) state `x` become less mutually correlated (that
is precisely G5's own decorrelation target), so their average moves closer
to `x`'s own stationary mean -- which is IDENTICAL (zero) for every author
by construction. Spreading, in other words, may not just decorrelate
observations; it may also wash out exactly the kind of per-author
persistence that gives `x` ANY between-author signal to contribute in the
first place, independent of whether the panel/gauge machinery downstream can
recover it. This would be a mechanistically coherent reason for why
long-window recovery might fail to rise with B even on a causally live
channel -- but it is offered as interpretation only; it is not what the
(voided) adjudication above turns on.

**On G5's own failure pattern.** F7's own report (Honest disclosures, item
5) already flagged that "G5 becoming, if anything, a MORE sensitive test at
this scale" as author count grows -- its own closest call, `b2_x16_shared_k10`
at `t=+1.871`, sat at 93.6% of the `2.0` bar. This leg's closest call,
`b4_x16_shared_k05` at `t=+3.497`, tips over. The correlation MAGNITUDES
involved are consistent across both legs and with F6's own (F6:
-0.00161 to +0.00069; F7: -0.0000651 to +0.000860; this leg: -0.000219 to
+0.000552) -- none of these is qualitatively different from the others; what
differs is the pooled pair count (F6: tens/hundreds of thousands; F7 and
this leg: 756,480 to 5,295,360), which shrinks the standard error and
inflates `t` for a FIXED tiny residual correlation. This reads as a
methodological finding about the G5 rule itself, not about this leg's
world-generation being newly broken: a fixed `|t|<2.0` significance
threshold does not hold its meaning as pooled sample size grows, because it
conflates "detectable" with "practically nonzero." A future registration
revisiting this line's decorrelation check should consider an
equivalence-style test (a fixed magnitude bound, e.g. `|correlation|<1e-3`,
independent of `n`) rather than a fixed-`t` significance bar -- disclosed
here as a candidate standing-rule addition, not adopted unilaterally by the
executing agent.

## Honest anomalies and disclosures

1. **G5 FAILS at `b4_x16_shared_k05`** (`t=+3.497`, correlation `+0.000552`,
   `n_pairs/world=2,269,440`) while `b2`/`b8` pass comfortably
   (`t=-0.289`/`-1.383`). This is the headline finding of this leg and is
   NOT softened: the leg is reported VOID under the adopted reading.
2. **A disclosed, self-reported script addition** (Part 0.9): a branch was
   added to `run_finalize()` AFTER observing G5's failure, to check
   `gates["mechanical_gates_pass"]` and write a complete
   `VOID_MECHANICAL_GATE_FAILURE` decision rather than silently adjudicating.
   No scientific/design parameter (GAP, the `|t|<2.0` bar, kappa, block
   counts, the lean/pivot rules) was touched. This was necessitated by
   running each stage as a separate foreground call under this task's own
   120-second-per-call constraint, which exposed a code path (`--stage
   finalize` invoked independently after a gate failure) that F6's and F7's
   own single-invocation `--stage all` runs never had to handle because
   their own G5 never failed.
3. **A disclosed ambiguity between two readings of leg-voidability** (the
   VOID DETERMINATION section above): Reading 1 (G5 retains its
   pre-existing void-on-failure consequence) is adopted; Reading 2 (only
   G0/G6 govern voidability for this registration) is fully computed and
   reported but not adopted. Under Reading 2 the pivot would FIRE with the
   SAME closure verdict M4-F7 itself reached
   (`CLOSURE_EARNED_TRAIT_LEVEL_UNCERTIFIABLE_ON_ALL_THREE_PANEL_AXES`) --
   this is disclosed plainly, not to smuggle the conclusion in by the back
   door, but because withholding it would make this report less complete,
   not more rigorous.
4. **G6's own channel magnitude is modest** (~9-10% of between-author
   variance at B=1, ~4% at B=8) even though it is statistically unambiguous
   -- stated as a limitation that applies REGARDLESS of how the void
   question above is read, per the task's own explicit instruction.
5. **Truth B is again non-monotonic** across B in {1,2,4,8} (flat-to-rising
   through B=4, sharp drop at B=8) -- the same qualitative pattern M4-F7
   found at kappa=1.0, now also present at kappa=0.5, reported plainly
   rather than smoothed.
6. **6 of 8 world-index pairs are negative** on the B8-B1 truth-B diff (vs.
   M4-F7's own 8-of-8 at kappa=1.0) -- a less unanimous but still
   majority-consistent direction.
7. **Total main-pipeline compute was approximately 9 minutes**: G6 ~14s
   (standalone, before the sweep); anchor 195s; construction-check 9s; sweep
   135s (`--block-counts 4`) + 154s (`--block-counts 8`) + prior batch
   (`--block-counts 1,2`, ~294s, matching F7's own timing for the same pair)
   run as three separate foreground chunks per the 120-second constraint;
   gates ~11s; finalize <1s (after the disclosed 0.9 addition).
   `--workers 8` throughout. A single-world timing pilot (56.57s/59.45s) was
   run in-process before the full sweep, per the task's own instruction.

## Decision boundary

Exploratory, synthetic-calibrated, label-free. This leg was designed to be
the decisive occasion-axis test: the one cell in the M4-F line that is both
adequately powered (G0, confirmed: minimum detectable paired difference
0.0318, comfortably inside the 0.0407 bar) and causally live (G6, confirmed
and independently validated by an exact-1.0 kappa=1.0 control: the state
contributes a real, statistically unambiguous, but modest 4-10% of
between-author variance at kappa=0.5). Neither of those two gates blocks
adjudication. **A third, pre-existing, verbatim-reused gate (G5,
decorrelation) does: one of the three tested block-count cells
(`b4_x16_shared_k05`) shows a residual cross-block correlation
indistinguishable in magnitude from every prior leg's own closest calls, but
statistically significant at this leg's much larger pooled sample size.**
Per the registration's own explicit instruction, the gap was not increased
and the leg was not re-run; the void is written as observed. **The decisive
test the M4-F line has been building toward across four legs
(M4-F5/F6/F7/F8) remains formally unresolved**: the raw numbers, reported in
full above under an explicitly-labeled, non-adopted alternate reading, point
in the same direction M4-F7 already found (decline, not rise), but this leg
cannot certify that finding past its own gate discipline. This licenses no
finding about panel DESIGN, and makes no claim about the real relation
field's actual content, personality, emotion, diagnosis, or any individual.
Artifacts: `results/m4_f8_occasion_axis_live/{decision.json, gates.json,
cells.csv, cell_*.csv, draws_*.csv, g6_gate.json, g6_worlds.csv}`.
