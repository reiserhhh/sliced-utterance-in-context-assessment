# SUICA M4-F9 -- The Decisive Occasion Cell, Repaired Gate, Fresh Seeds (Authors x16, Kappa=0.5)

> **BANNER: synthetic worlds calibrated to an opened-panel regime, exploratory.**
> This leg consumes NO new real-text evidence. It repeats M4-F8's occasion-
> spread sweep on FRESH world seeds with G5 repaired from a nil-significance
> test to an equivalence bound, reusing M4-F8's OWN script as a loaded
> module (not merely as a design template). No label columns anywhere; no
> claim about the real relation field's content, personality, emotion,
> diagnosis, or any individual.

Registered spec: `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md`
section "M4-F9 registration (2026-08-03, BEFORE run) -- the decisive cell,
repaired gate, fresh seeds", together with the preceding "M4-F8 planner
adjudication note -- a defective gate, and the standard the agent set" (why
this leg exists). Script:
`scripts/run_suica_m4_f9_occasion_axis_repaired.py`. Artifacts:
`results/m4_f9_occasion_axis_repaired/`.

**Headline, stated up front so it is not buried: this leg does NOT void.**
G0 (power), G1-G4 (mechanical), G5 (decorrelation, repaired equivalence
form), and G6 (channel liveness) **all PASS** on this leg's own fresh
seeds. With every gate clear, the registered pivot condition is evaluated
for real, not merely disclosed-and-declined as in M4-F8: **adequately
powered AND causally live AND long-window recovery does NOT rise with B
(paired B8-B1 95% CI [-0.0559, +0.0233], includes zero)**. **THE PIVOT
FIRES.** Per the registration, **the closure is EARNED**: trait-level
relation structure is not certifiable on any of the three panel axes under
this synthetic instrument, D3 is permanently restricted to occasion-bound
objects, and the M4-E2 objective redesign is the only remaining route. Full
numbers, both G5 pooling readings, and the theoretical-residual coherence
check are given below.

## Part 0 -- REGISTERED ADJUDICATIONS AND OPERATIONALIZATIONS (written before the run)

The registration fixes the design as "identical to M4-F8 in every
scientific respect" -- shared-occasion design, kappa=0.5, authors x16,
common-budget construction, block count B in {1,2,4,8}, the G5-verified
40-step gap, 8 worlds x 20 draws, both M4-F5 truth variants, the SAME G0
POWER target/bar and G6 CHANNEL LIVENESS design M4-F8 introduced -- with
**exactly two registered changes**: (1) fresh world seeds, (2) G5 repaired
to an equivalence form. Leans and pivot are carried over word for word.
Every implementation choice below was fixed in the script BEFORE any of the
six `--stage` calls (`g6`, `anchor`, `construction-check`, `sweep`, `gates`,
`finalize`) was run.

### 0.1 Reuse boundary -- maximal: M4-F8's own script loaded as a module

Unlike a design template that gets re-typed, this leg loads
`scripts/run_suica_m4_f8_occasion_axis_live.py` itself as a seventh frozen
module (`f8()`), exactly as F8 loaded `f1()`..`f7()`. Called UNCHANGED,
byte-for-byte: `f8().cell_name_spread_x16` (cell naming, so this leg's cells
stay directly comparable to F8's own by identity); `f8().build_construction_
check_task`, `f8().build_anchor_task` (both gate-anchor task builders, left
on the ORIGINAL seed lineage -- see 0.2); `f8()._read_f5_persisted_row`,
`f8()._read_f6_persisted_row`, `f8()._diff_row` (G2's read/diff helpers,
which only touch shared, read-only F5/F6 artifacts); `f8().g6_analytic_
coefficient`, `f8()._g6_world_task`, `f8()._g6_sanity_check` (G6's entire
ablation mathematics -- none of these three functions depends on a
module-level seed constant, so passing this leg's own fresh seed_key through
them via the task dict reuses F8's math exactly while drawing fresh draws);
and, most importantly, **`f8().adjudicate`, called as the literal same
function object** for the leans/pivot -- not a re-typed copy, an actual
shared reference, the strongest possible form of "word for word." From
`f1()`/`f2()`/`f3()`/`f5()`/`f6()`/`f7()` (loaded exactly as F8 itself
loaded them): `f1().knob_tag`; `f2().run_gate_g1`; `f3().run_gate_g3`;
`f5().run_truth_sweep_world`, `f5().G4_TOLERANCE`; `f6().GAP`,
`f6().M_COMMON`, `f6()._paired_ci`, `f6().spread_world_seed_for`;
`f7().run_spread_sweep_world`, `f7().common_layout_scaled`.

Newly written: `fresh_seed_key` (0.2); `build_spread_tasks`, a disclosed
near-duplicate of `f8().build_spread_tasks` changing ONLY the seed_key line
and this leg's own budget_label/corpus_prefix ("f9.0"/"m4f9-", cosmetic
namespacing matching every prior leg's own per-leg convention); `run_gate_
g5`, REWRITTEN for the equivalence form (0.3); `run_gate_g6`, a disclosed
near-duplicate of `f8().run_gate_g6` changing ONLY the two kappa=0.5
`gating_specs` seed_key strings; `run_gate_g0`/`run_gate_g2`/`run_gate_g4`/
`cell_summary`/`_write_cell`/`run_anchor`/`run_construction_check`/
`run_sweep`/`run_gates`, OUT-scoped near-duplicates (every leg's own
cell_summary/gates has always been OUT-scoped even when the underlying rule
is reused verbatim); `run_finalize`, with the mechanical-gate-VOID branch
built in from the start (0.6).

### 0.2 Change #1 -- FRESH WORLD SEEDS: mechanism ambiguity, disclosed

The registration text says "a new master-seed offset." `f6().spread_world_
seed_for(seed_key, world, knob_tag)` computes `stable_bucket(f"{MASTER_
SEED}-{seed_key}-w{world}-{knob_tag}", salt="m4f6-spread-world",
modulus=2**63-1)`, where `MASTER_SEED` is a **module-level closure constant
baked inside f6.py itself (20260802), not a parameter** -- every prior leg
(F6/F7/F8) kept this constant fixed and varied only `seed_key` to obtain a
"fresh, clearly-namespaced lineage off the same MASTER_SEED" (f6()'s own
docstring). This creates a genuine implementation-mechanism ambiguity for
"a new master-seed offset," since f6.py cannot be edited (out of scope for
this leg's six deliverables):

**Reading A (ADOPTED):** fold a new, disclosed, fixed-before-compute integer
offset into the `seed_key` STRING fed to the UNCHANGED `f6().spread_world_
seed_for` (`fresh_seed_key(block_count) = f"{FRESH_MASTER_SEED}-b{block_
count}_x16_{KAPPA_TAG}"`, `FRESH_MASTER_SEED = MASTER_SEED +
MASTER_SEED_OFFSET = 20260802 + 90000000 = 110260802`). Since `stable_
bucket` is a cryptographic-style hash, changing ANY part of its input string
-- whether the literal `MASTER_SEED` token or a value folded into `seed_
key` -- produces an equally fresh, uncorrelated, disclosed, reproducible
63-bit output; empirically confirmed before compute (`f6().spread_world_
seed_for('b1_x16_k05', 0, knob_tag)` = 8106115090263736079 vs. `f6().spread_
world_seed_for(fresh_seed_key(1), 0, knob_tag)` = 9021143400372420859 --
different, and reproducible across repeated calls). Adopted because it
achieves an equally fresh lineage with **zero new per-world engine code**:
`f7().run_spread_sweep_world` (and everything it calls) is reused
byte-for-byte, exactly as F8 itself established ("this script needs NO new
per-world engine at all").

**Reading B (NOT adopted, disclosed):** reimplement `_prepare_spread_world`/
`run_spread_sweep_world` as near-duplicates, substituting a literal
numeric-MASTER_SEED-parametrized seed function for F6's own hardcoded call.
This would put the word "MASTER_SEED" itself, not just a folded-in offset,
literally inside the reseeded formula -- but at the cost of duplicating a
~150-line per-world engine (calibration, both truth variants, G4's
independent route, G5's correlation) purely to swap one internal function
call, introducing real risk of a transcription bug in code this leg does
not need to touch at all. Not adopted: higher risk, no scientific
difference in what "fresh" means, and directly against this leg's own
registered "reuse it wholesale" instruction.

`MASTER_SEED_OFFSET=90000000` is arbitrary-but-fixed, disclosed before
compute, not tuned to any observed result.

### 0.3 Change #2 -- G5 REPAIRED TO AN EQUIVALENCE FORM

M4-F8's own G5 (F6's Part 0.7 rule, reused verbatim through F7 and F8) was a
**per-cell nil-significance test** (`|t|<2.0` on each of the 3
block_count>=2 cells independently) on a quantity the M4-F8 planner
adjudication note proved is **nonzero by construction**
(`phi_hi**41 = 1.06e-4`), so its failure probability grows, not shrinks,
with sample size. The registration repairs this to an **equivalence
form**: the 95% CI of "the pooled correlation" must lie entirely inside
+/-0.005.

**Pooling ambiguity, disclosed, both readings computed:**

**Reading 1 (ADOPTED, gating):** pool EVERY G5-applicable per-world
correlation value across ALL THREE block_count>=2 cells (b2/b4/b8, 8 worlds
each) into ONE n=24 sample, and compute a SINGLE 95% CI via
`f6()._paired_ci` (the same one-sample t-CI construction used by every
paired statistic in this line). Adopted for three reasons. First, textual:
the registration says "the 95% CI of **the** pooled correlation" (singular,
definite article), directly promoting the exact quantity M4-F8's own G5
gate already computed and explicitly labeled `pooled_context`/`grand_mean_
across_cells` as supplementary, not-yet-gating context -- this leg's
registration reads as promoting that named quantity to the actual gate, not
inventing a new one. Second, mechanistic: the raw AR(1) state's residual
cross-block correlation at a fixed GAP+1=41-step lag does not depend on
`block_count` (`f6().block_boundary_label_pairs` shows every adjacent
boundary pair is separated by exactly `gap+1` steps regardless of how many
blocks total; kappa/block_count only change how many such pairs exist and
how the SUBSEQUENT blend uses them, not the lag itself) -- so the three
cells' 24 world-level correlations are exchangeable draws of the SAME
underlying quantity, and pooling them is statistically natural, not merely
convenient. Third, and most important given WHY this repair exists: pooling
makes the CI **tighter** as more data is combined, which is exactly the
property an equivalence form should reward (a larger, more precise
experiment should find it EASIER to demonstrate negligibility) -- the
opposite of the nil-significance form the M4-F8 planner note diagnosed as
defective (stricter as the experiment gets bigger).

**Reading 2 (NOT adopted, disclosed, fully computed):** keep the OLD
per-cell structure (an independent equivalence CI at each of the 3 cells,
all three must pass), swapping only the test FORM (equivalence vs.
nil-significance) and not the aggregation. Computed alongside for every
cell (Part 1 below) -- at this leg's own realized numbers, **both readings
reach the same PASS conclusion** (see Part 1), so there is no adjudicated
disagreement between them this time, but both are reported per this line's
disclosure convention.

**Delta justification (registered, fixed before compute):** `delta=0.005`
is derived from the generator, not from any observed value: the theoretical
worst-case residual is `phi_hi**41 = 1.06e-4` at the calibrated `phi_hi=.80`
(and `phi_lo**41 = 2.2e-29` at `phi_lo=.20`; the registration's own
illustrative `0.50**41 = 4.5e-13` reference point is independently
reproduced exactly). `delta` is therefore ~47x the largest theoretical
residual the construction can produce -- close to the registration's own
"~50x" framing. `g5_theoretical_residual(knobs, gap)` reads `phi_lo`/`phi_
hi` from the SAME calibration knobs every world in this leg actually uses
(`k=48, rho=0.5, w_mu=0.15, w_x=0.15, w_e=0.7, phi_lo=0.2, phi_hi=0.8`), not
retyped from the registration text.

**Coherence-check bar, disclosed before compute:** "same order of
magnitude" is operationalized as the measured/theoretical ratio falling
within 10x, calibrated from **M4-F8's own already-published** per-cell
measured/theoretical ratios (approximately 1.7x, 5.2x, 2.1x at its three
cells) -- prior, independently-published data, not this leg's own
soon-to-be-observed numbers. This bar is a narrative coherence statement
only; it does not gate the leg (G5's gating statistic is the equivalence
containment test above).

### 0.4 What is UNCHANGED from M4-F8

G0's target/bar (M4-F5's persisted `authors_x16_shared_k05`, `.0407` half of
`.081307`), G6's entire design (analytic coefficient + empirical
between-author-variance-ratio ablation, non-gating kappa=1.0 context row),
and the three leans plus the pivot rule are unchanged in every respect --
the pivot rule is evaluated by the literal same `f8().adjudicate` function
object, not a re-typed copy, so there is no possibility of a transcription
drift in the leans/pivot logic itself.

### 0.5 Which checks use fresh seeds vs. the ORIGINAL lineage (explicit, per the task's own instruction)

| Check | Seed lineage | Why |
|---|---|---|
| G1 (`f2().run_gate_g1`, base1x anchor) | **ORIGINAL** | reproduces M4-F1's persisted `base1x`; re-seeding would break the check |
| G2(a) construction-check (`construction_check_mult1_b1_k05`) | **ORIGINAL** (F6's own `"b1_k05"` seed_key) | reproduces M4-F6's persisted `b1_shared_k05` bit-for-bit |
| G2(b) anchor (`authors_x16_shared_k05`) | **ORIGINAL** (F4's own `build_live_tasks` lineage) | reproduces M4-F5's persisted `authors_x16_shared_k05` bit-for-bit; also G0's target source |
| G6 context row (kappa=1.0, `"b1_x16_k10"`) | **ORIGINAL** (F7's own seed_key) | non-gating validation against F7's/F8's own historical, bit-identical draws |
| G6 gating rows (kappa=0.5, block_count in {1,8}) | **FRESH** (`fresh_seed_key(1)`/`fresh_seed_key(8)`) | must certify the SAME draws the leans/pivot are computed on |
| 4 adjudicated sweep cells (`b{1,2,4,8}_x16_shared_k05`) | **FRESH** (`fresh_seed_key(block_count)`) | this leg's own new sample -- the entire point of change #1 |

### 0.6 Mechanical-gate-VOID branch built in from the start

M4-F8's own report (Part 0.9) disclosed that running each stage as a
SEPARATE foreground call (this task's own chunking constraint) exposes a
code path -- `--stage finalize` invoked independently after `gates.json`
already shows a mechanical failure -- that F6's/F7's single-invocation
`--stage all` runs never had to handle, because their own G5 never failed.
This leg's `run_finalize` builds that branch in **from the start**, citing
F8's report directly, rather than discovering the gap live. As it happens,
G5 did NOT fail this run (0.2/Part 1), so this branch was not exercised --
it remains disclosed as a foreseen, not-yet-triggered safeguard, consistent
with this leg's own "before compute" discipline.

### 0.7 A pre-compute mechanical verification (disclosed, not a design change)

Before running any compute, this leg's own `_load_script`-plus-`Process
PoolExecutor` reuse pattern (identical to F5's/F6's/F7's/F8's own) was
verified empirically rather than assumed, because an initial isolated test
(a throwaway script located OUTSIDE `scripts/`) failed with `ModuleNotFound
Error` under macOS's default "spawn" multiprocessing start method. Root
cause, confirmed by a second, targeted test: the fix already documented in
F3's/F4's/F5's own `_load_script` docstrings (registering `sys.modules
[mod_name] = module` before `exec_module`) works correctly **specifically
because the running script itself lives in `scripts/`**, which CPython
auto-adds to `sys.path[0]` in both parent and spawned child -- letting the
child's own fresh re-import of a same-named `.py` file resolve correctly.
Re-running the identical test with the loader script placed inside
`scripts/` (matching this leg's actual deployment location) succeeded. **No
code change was made as a result** -- this confirms the established,
already-working pattern applies unmodified once more, and is disclosed here
only because it was a genuine, load-bearing risk investigated before
compute, not because anything needed fixing.

### 0.8 Budget/gate scope summary

Six cells computed, identical structure to F8: the RAW gate-anchor
(`authors_x16_shared_k05`, 211,232 events, ORIGINAL lineage, G0's target AND
G2(b)'s target), the gate-only construction-check
(`construction_check_mult1_b1_k05`, 7,880 events, ORIGINAL lineage, G2(a)'s
target), and the four adjudicated common-budget cells
(`b{1,2,4,8}_x16_shared_k05`, 126,080 events each, FRESH lineage, identical
across every swept B). Gates: **G0** (0.4) POWER. **G1** (direct call,
`f2().run_gate_g1`, ORIGINAL). **G2** (0.5) -- construction + anchor, both
ORIGINAL, both to <=1e-12. **G3** (direct call, `f3().run_gate_g3()`). **G4**
(identical mechanism to M4-F5/M4-F6/M4-F7/M4-F8) -- truth-path invariance
across all 6 computed cells. **G5** (0.3, repaired equivalence form, FRESH).
**G6** (0.4, FRESH gating rows + ORIGINAL context row).

### 0.9 Timing expectation (no separate pilot run)

Unlike M4-F8, this leg's own task text does not request a standalone
single-world timing pilot before the full sweep. Since F8's own report
already established that kappa does not change per-world compute cost
(pilot numbers matching F7's own almost exactly), this leg proceeded
directly to full per-cell stages, using F8's own published per-cell timings
(~130-155s per adjudicated cell, 8-way parallel) as the working expectation
for chunking -- confirmed correct in Part 1's timing disclosure.

---

*(Everything below this line was written after the run. Part 0 above --
and the script that implements it -- was not edited after compute began.)*

## Part 1 -- OUTCOME

### G0 POWER -- reported first, as mandated

**ADEQUATELY POWERED.** Target level, read verbatim from M4-F5's own
persisted `authors_x16_shared_k05` row: long-window truth recovery
**0.081307 +/- 0.010920** (matches the registration's cited number exactly
-- ORIGINAL lineage, G2(b)-verified to <=1e-12 below). This leg's own
realized paired-by-world `b8_x16 - b1_x16` difference on `truth_recovery_
long` (FRESH seeds): mean **-0.016323**, SD 0.047392, SE 0.016755 (n=8,
df=7), t=-0.974, 95% CI **[-0.055943, +0.023298]**. **Minimum detectable
paired difference (95% CI half-width): 0.039620** -- inside the registered
`.0407` bar, but only **97.3% of it** (headroom 0.00108) -- markedly
tighter than M4-F8's own 78.0%. **G0 PASSES**, honestly reported as a close
call: on a different fresh-seed draw this margin could plausibly have
crossed the bar. This does not change the outcome (it passed on the seeds
actually drawn), but it is a real property of this leg's own realized
sample, stated plainly rather than smoothed over.

### G5 DECORRELATION, REPAIRED EQUIVALENCE FORM -- reported first, as mandated

**PASSES under BOTH readings.**

**Reading 1 (ADOPTED, gating): POOLED.** All 24 G5-applicable per-world
correlation values (b2/b4/b8, 8 worlds each) pooled into one sample:

| n | mean | SD | SE | 95% CI |
|---|---|---|---|---|
| 24 | -0.0001871 | 0.0013190 | 0.0002692 | **[-0.0007441, +0.0003699]** |

The entire CI lies inside +/-0.005 by a wide margin (the CI's own half-width,
0.00056, is **~9x tighter** than the 0.005 bar). **G5 PASSES (Reading 1).**

**Reading 2 (disclosed, NOT adopted): per-cell.**

| block_count | correlation_mean | correlation_se | per-cell 95% CI | n_pairs/world | equivalence pass |
|---|---|---|---|---|---|
| 2 | -0.000283 | 0.000818 | [-0.002216, +0.001650] | 756,480 | yes |
| 4 | -0.0000903 | 0.000184 | [-0.000525, +0.000344] | 2,269,440 | yes |
| 8 | -0.000188 | 0.0000988 | [-0.000421, +0.0000460] | 5,295,360 | yes |

All three cells independently pass too -- **at this leg's own realized
numbers, Reading 1 and Reading 2 reach the identical PASS conclusion**, so
there is no adjudicated disagreement between the adopted and not-adopted
readings this run (unlike M4-F8, where the analogous ambiguity -- over
whether G5 voids the leg at all -- was consequential). For context only
(NOT gating under either reading): the OLD nil-significance `|t|<2.0` test
would ALSO have passed at all three cells this run (max `|t|=1.899` at
b8, the closest call, still under 2.0) -- this leg's own fresh draw did not
happen to reproduce M4-F8's specific `b4` near-miss, consistent with the
M4-F8 planner note's own diagnosis that the old test's failures were driven
by sample-size-dependent SE shrinkage on a small nonzero residual, not by
anything wrong with the generator.

**Theoretical-residual coherence check.** Theoretical worst-case residual
`phi_hi**41 = 1.063382e-04` at the calibrated `phi_hi=0.8` (lag = GAP+1 =
41 steps). Measured |pooled correlation mean| = **1.871071e-04**. Ratio
**1.760x** -- well inside the disclosed 10x coherence bar. **Statement:
the measured pooled correlation is CONSISTENT with the theoretical
residual** -- both the sign-unstable, few-times-1e-4 magnitude and the
order of magnitude match what a nonzero-but-tiny residual autocorrelation
at a 41-step AR(1) lag predicts, exactly as designed. This is independent
supporting evidence (not itself a gate) that the repaired G5 is now testing
the quantity it was always meant to test, rather than an artifact of pooled
sample size.

### G6 CHANNEL LIVENESS

**LIVE**, on this leg's own fresh seeds. **Analytic:** `sqrt(1-0.5) =
0.7071067811865476`, non-zero. **Internal-consistency check:** max abs diff
between `f8()`'s own ablation helper's INTACT reconstruction and
`f6().generate_world_spread`'s real output, same inputs (this leg's own
fresh seed_key): **exactly 0.0**. **PASS.**

| block_count | v_intact (mean) | v_state_zeroed (mean) | ratio (mean) | log-ratio 95% CI | live |
|---|---|---|---|---|---|
| 1 | 0.538028 | 0.489280 | **1.0996** | [0.09461, 0.09535] | YES |
| 8 | 0.507580 | 0.488836 | **1.0383** | [0.03713, 0.03813] | YES |

Both CIs exclude 0 on the positive side by a wide margin (t=605.7 and
t=177.0). **Coherence with M4-F8's own independently-drawn numbers**: ratio
at B=1 is 1.0996 here vs. **1.0995** in F8 (diff +0.00013); at B=8, 1.0383
here vs. **1.0382** in F8 (diff +0.00015) -- the channel's magnitude is
essentially IDENTICAL across two independent fresh-seed draws, strong
evidence this is a stable, reproducible property of the generator/design at
this kappa, not a seed-specific artifact. **The magnitude is again modest**
-- ~10.0% of between-author variance at B=1, ~3.8% at B=8 -- the same
disclosed limitation M4-F8 already flagged, unchanged by fresh seeds:
`mean_part` and the noise floor (`w_e=0.7`, dominant) account for the
remaining ~90-96%. **Kappa=1.0 context row (ORIGINAL lineage, F7's own
world draws, unchanged since M4-F7/M4-F8):** ratio exactly **1.000000** at
all 8/8 worlds, log-ratio exactly 0.0 -- reproduces F7's/F8's own numbers
bit-for-bit, as expected since this row is deliberately NOT re-seeded.
**G6 PASSES.**

### Gates G1-G4

- **G1** (direct call, `f2().run_gate_g1`, ORIGINAL lineage): diffs
  ~1e-16/1e-17 range, `n_retained` exact (565). **PASS.**
- **G2(a) CONSTRUCTION** (ORIGINAL lineage): `construction_check_mult1_
  b1_k05` vs. M4-F6's persisted `b1_shared_k05`: max abs diff **5.55e-17**;
  `n_retained` exact (565). **PASS.**
- **G2(b) ANCHOR** (ORIGINAL lineage): the RAW `authors_x16_shared_k05`
  cell vs. M4-F5's persisted `authors_x16_shared_k05`: max abs diff
  **4.86e-17** (agreement/truth-exact diffs exactly 0.0); `n_retained`
  exact (9040). **PASS.**
- **G3** (direct call, `f3().run_gate_g3()`): batched feature map
  bit-identical (`max_abs_diff_M`/`K` = 0.0); halving identical (120/120
  checked). **PASS.**
- **G4** (truth-path invariance): max diff across all 6 computed cells
  (2 ORIGINAL-lineage + 4 FRESH-lineage) is **exactly 0.0** on every single
  cell, regardless of seed lineage. **PASS.**

**All gates pass. `mechanical_gates_pass=True`, `all_pass=True`.** The
mechanical-gate-VOID branch built into `run_finalize` (0.6) was NOT
exercised.

## THE FULL ADJUDICATION

With G0 and G6 both PASS, `run_finalize` calls `f8().adjudicate` -- the
literal same function object M4-F8 itself used -- on this leg's own fresh
summaries.

**Lean (a) -- TRAIT AXIS EXISTS: MISS.** Paired-by-world `b8_x16-b1_x16`
truth-recovery-long diff: mean **-0.016323**, 95% CI **[-0.055943,
+0.023298]** -- includes zero. Long-window recovery does not significantly
rise (or fall) with B on this leg's own fresh sample.

**Lean (b) -- DIFFERENT OBJECT, NOT BETTER ESTIMATE: INAPPLICABLE.** The
long-window gain (lean a's own mean, -0.016323) is not positive, so per the
registered rule this lean is not scored. (For completeness: the same-
occasion Variant-A paired diff is mean -0.031731, 95% CI [-0.052387,
-0.011075] -- excludes zero on the negative side -- but this number does
not feed the verdict, since lean (b) is registered INAPPLICABLE whenever
the long-window gain is non-positive.)

**Lean (c) -- GAUGE BLINDNESS REPLICATES: HOLD.** Agreement by block count:
B=1 0.189684, B=2 0.198003, B=4 0.185674, B=8 0.168122. B=1 reference
0.189684, +/-20% band [0.151747, 0.227621]; every value falls inside
(Reading 1, adopted). Reading 2 (stricter, max-to-min <= band): max-min
= 0.029881 <= band 0.037937 -- **also HOLDS** (no disagreement between
readings here).

**PIVOT.** `adequately_powered=true` (G0) AND `causally_live=true` (G6) AND
`no_rise_condition=true` (paired CI includes zero, on B8-B1 truth-recovery-
long) -> **PIVOT FIRES.**

**VERDICT: `CLOSURE_EARNED_TRAIT_LEVEL_UNCERTIFIABLE_ON_ALL_THREE_PANEL_
AXES`.**

Per the registration, this is stated plainly and without qualification:
**the closure is EARNED.** Trait-level relation structure is not
certifiable on any of the three panel axes (author-axis, events-axis,
occasion-axis) under this synthetic instrument. D3 is permanently
restricted to occasion-bound objects. The M4-E2 objective redesign is the
only remaining route.

## The full B-vs-metrics table (kappa=0.5, fresh seeds)

| B | agreement | agreement SE | truth A (same-occasion, exact) | truth A SE | truth B (long-window) | truth B SE |
|---|---|---|---|---|---|---|
| 1 | 0.189684 | 0.008209 | 0.360226 | 0.007656 | **0.059634** | 0.012148 |
| 2 | 0.198003 | 0.012072 | 0.322967 | 0.009713 | **0.049490** | 0.012254 |
| 4 | 0.185674 | 0.017706 | 0.335292 | 0.005266 | **0.078542** | 0.007715 |
| 8 | 0.168122 | 0.010606 | 0.328495 | 0.008243 | **0.043311** | 0.010453 |

Context rows: RAW gate-anchor `authors_x16_shared_k05` (ORIGINAL lineage)
-- agreement 0.095219, truth A 0.323159, truth B 0.081307 (matches M4-F5's
persisted value to <=1e-12, per G2(b)). Construction-check
`construction_check_mult1_b1_k05` (ORIGINAL lineage, mult=1) -- agreement
0.010993, truth A 0.148493, truth B 0.019555 (matches M4-F6's persisted
`b1_shared_k05` to <=1e-12, per G2(a)).

Truth B is again **non-monotonic** across B in {1,2,4,8}: 0.0596 (B=1) ->
0.0495 (B=2) -> 0.0785 (B=4) -> 0.0433 (B=8) -- broadly the same
flat/wobble-through-B4-then-drop-at-B8 SHAPE M4-F7 (kappa=1.0) and M4-F8
(kappa=0.5, void) both found, though this leg's own B=4 value is a local
peak rather than a plateau. The overall B8-vs-B1 comparison (what the leans
and pivot actually test) is a small, non-significant decline.

**Per-world detail (kappa=0.5, `truth_recovery_long`, paired by world
index, FRESH seeds):**

| world | B=1 | B=8 | B8-B1 |
|---|---|---|---|
| 0 | 0.027603 | 0.069075 | +0.041471 |
| 1 | 0.039448 | 0.076932 | +0.037484 |
| 2 | 0.091416 | 0.026867 | -0.064549 |
| 3 | 0.123885 | 0.065274 | -0.058611 |
| 4 | 0.047822 | 0.042593 | -0.005229 |
| 5 | 0.070811 | -0.013327 | -0.084138 |
| 6 | 0.053788 | 0.052484 | -0.001304 |
| 7 | 0.022298 | 0.026591 | +0.004293 |

**5 of 8 world-index pairs are negative** -- a majority, but the least
unanimous of any leg in this line so far (M4-F7: 8/8 at kappa=1.0; M4-F8:
6/8 at kappa=0.5, void). Combined with 2 world pairs that are clearly
positive (worlds 0 and 1, both +0.037 to +0.041), this is the direct
arithmetic reason the paired CI now includes zero where M4-F8's own
(not-adopted) Reading 2 numbers had excluded it on the negative side --
consistent with M4-F9 being a genuinely independent, fresh sample rather
than a re-adjudication of the same draws.

## Budget conservation (diagnostic, verified exactly)

Every one of the 4 adjudicated `b{1,2,4,8}_x16_shared_k05` cells allocates
**exactly 126,080 events** (`15,760 authors x M_COMMON=8`), identical
across every swept B and identical to M4-F7's/M4-F8's own. The RAW
gate-anchor allocates 211,232 events; the construction-check allocates
7,880 events -- both matching M4-F6's/M4-F7's/M4-F8's own totals exactly.

## F8-vs-F9 coherence summary (both independent, both real)

| Quantity | M4-F8 (voided) | M4-F9 (this leg) |
|---|---|---|
| G0 half-width / bar | 0.0318 / .0407 (78.0%) | 0.0396 / .0407 (**97.3%**) |
| G0 paired B8-B1 mean (truth B) | -0.036177 | -0.016323 |
| G0 paired B8-B1 95% CI | [-0.067938, -0.004416] (excludes 0) | [-0.055943, +0.023298] (**includes 0**) |
| G6 ratio at B=1 / B=8 | 1.0995 / 1.0382 | 1.0996 / 1.0383 |
| G5 per-cell magnitudes (b2/b4/b8) | -1.8e-4 / +5.5e-4 / -2.2e-4 | -2.8e-4 / -0.9e-4 / -1.9e-4 |
| G5 old nil-significance `|t|` (context only both legs) | 0.289 / **3.497 (FAIL)** / 1.383 | 0.347 / 0.491 / 1.899 (all pass) |
| World-index B8-B1 negative count | 6/8 | 5/8 |
| Lean (a) / pivot (under the reading that adjudicates) | MISS (excludes 0, negative) / FIRES | MISS (includes 0) / FIRES |

Both legs' G6 channel-liveness numbers are essentially identical (real,
stable generator property). Both legs' G5 per-cell correlation MAGNITUDES
are the same order as each other and as the theoretical residual -- what
changed between legs is not the underlying phenomenon but (i) which
specific cell happened to cross the old, defective `|t|<2.0` bar by chance,
and (ii) this leg's own G0 statistic landing closer to (but still inside)
its power bar. Both legs' adjudicated substantive finding (no rise, in
fact a decline, in long-window recovery from B=1 to B=8) points the same
direction; M4-F9 is the first leg where this can be CERTIFIED rather than
merely observed-and-disclosed-but-voided.

## Interpretation (post-hoc, clearly separated from the adjudication above, not a registered claim)

**Why G0's margin narrowed.** M4-F8's own paired B8-B1 mean was -0.036,
about 2.2x this leg's -0.016 -- a smaller realized effect on this leg's
fresh sample directly produces a smaller numerator relative to a similar
SE, which is arithmetically why the CI now straddles zero (MISS) rather
than sitting entirely below it. This is exactly the between-world sampling
variability the registered pivot rule is designed to be robust to: G0's
role is to certify that the DESIGN has enough power to detect an effect of
M4-F5's own reference size if one is present, not to guarantee any
particular draw reproduces the prior leg's specific point estimate.

**Why the pivot is the right way to read this, not "inconclusive."** A
naive reading might treat a CI that includes zero as "no information."
The registered pivot rule is more precise: it fires specifically when the
design is independently certified adequate (G0) and the manipulation is
independently certified causally active (G6) and, GIVEN both of those, no
rise is detected. That combination -- power and liveness both confirmed,
rise still absent -- is what licenses a negative finding rather than a
merely underpowered null.

## Honest anomalies and disclosures

1. **G0's power margin is real but tight**: 97.3% of the bar (headroom
   0.00108), vs. M4-F8's own 78.0%. Reported plainly in Part 1, not
   smoothed. The leg still PASSES G0 on the seeds actually drawn.
2. **Both G5 readings (pooled, adopted; per-cell, not adopted) reach the
   same PASS conclusion this run** -- unlike M4-F8, where the analogous
   ambiguity (whether G5 voids the leg at all) was the entire story. This
   leg's own ambiguity disclosure (Part 0.3) therefore does not change the
   outcome, but is reported in full per this line's own convention of
   never silently picking the favorable reading.
3. **The master-seed-offset mechanism ambiguity** (Part 0.2): Reading A
   (seed_key-embedded offset, adopted, zero new per-world engine code) vs.
   Reading B (a literal MASTER_SEED-parametrized reimplementation of the
   per-world engine, not adopted, higher risk). This is an implementation
   choice, not a dual-numeric-outcome ambiguity like G5's -- both readings
   would produce a fresh, valid sample; Reading A was chosen for lower risk
   and stated, disclosed reasoning, not because Reading B was computed and
   found less favorable.
4. **A pre-compute mechanical verification was performed and is disclosed**
   (Part 0.7): an initial isolated test of this line's own established
   `ProcessPoolExecutor` reuse pattern failed when run from OUTSIDE
   `scripts/`, and succeeded when re-tested from inside `scripts/` (this
   leg's actual deployment location). No code changed as a result; this is
   disclosed as due diligence on a load-bearing mechanism, not as a fix.
5. **Truth B is again non-monotonic** across B in {1,2,4,8}, as in every
   prior occasion-axis leg, though this leg's own B=4 reads as a local peak
   rather than a plateau -- reported plainly rather than smoothed to match
   the qualitative shape of prior legs.
6. **5 of 8 world-index B8-B1 pairs are negative** (vs. M4-F7's 8/8 at
   kappa=1.0 and M4-F8's 6/8 at kappa=0.5) -- the least unanimous of the
   three occasion-axis legs at authors x16, consistent with this being a
   genuinely independent fresh sample rather than a re-adjudication.
7. **Total compute**: g6 ~13s (per `g6_gate.json`, standalone before the
   sweep); anchor 208s; construction-check 9s; sweep in three foreground
   chunks per this session's own chunking discipline -- `--block-counts
   1,2` (136s + 144s = 280s combined), `--block-counts 4` (147s),
   `--block-counts 8` (153s); gates and finalize together well under a
   minute. `--workers 8` throughout. No separate single-world timing pilot
   was run this leg (Part 0.9); F8's own published per-cell timings served
   as the working expectation and were confirmed accurate (this leg's own
   per-cell times, 136-153s, sit inside F8's own 130-155s range).

## Decision boundary

Exploratory, synthetic-calibrated, label-free. This leg repeats the one
cell in the M4-F line that M4-F8 showed is both adequately powered and
causally live, on a FRESH sample and a repaired, non-defective decorrelation
gate. **Every gate passes.** The registered pivot fires: powered (G0),
live (G6), and no rise in long-window trait recovery from B=1 to B=8 (paired
95% CI [-0.055943, +0.023298], including zero, point estimate a small
decline). **The closure is EARNED**: trait-level relation structure is not
certifiable on any of the three panel axes (author, events, occasion) under
this synthetic instrument; D3 is permanently restricted to occasion-bound
objects; the M4-E2 objective redesign is the only remaining route. This
licenses no finding about panel DESIGN beyond that scope, and makes no
claim about the real relation field's actual content, personality, emotion,
diagnosis, or any individual. Artifacts:
`results/m4_f9_occasion_axis_repaired/{decision.json, gates.json, cells.csv,
cell_*.csv, draws_*.csv, g6_gate.json, g6_worlds.csv}`.
