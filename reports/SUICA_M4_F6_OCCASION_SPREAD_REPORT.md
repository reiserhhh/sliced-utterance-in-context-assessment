# SUICA M4-F6 -- Can Occasion SPREAD Certify the Trait-Level Object?

> **BANNER: synthetic worlds calibrated to an opened-panel regime, exploratory.**
> This leg consumes NO new real-text evidence. It extends M4-F1/F2/F3/F4/F5's
> generator family with ONE new mechanism (block+gap occasion spreading) and
> reuses their gauge/map/D0/halving/truth-path machinery unchanged. No label
> columns anywhere; no claim about the real relation field's content,
> personality, emotion, diagnosis, or any individual.

Registered spec: `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md`
section "M4-F6 registration (2026-08-03, BEFORE run) -- can occasion SPREAD
certify the trait-level object?" (panel design laws line, loop cycle 15).
Script: `scripts/run_suica_m4_f6_occasion_spread.py`. Artifacts:
`results/m4_f6_occasion_spread/`.

## Part 0 -- REGISTERED ADJUDICATIONS AND OPERATIONALIZATIONS (written before the run)

The registration fixes the design (fixed authors and fixed total events,
sweeping occasion-block count B in {1,2,4,8} with a gap chosen to decorrelate
the AR(1) state), the three leans, the pivot, and gates G1-G4 by direct reuse
of the prior legs' own helpers. It explicitly asks this leg to REGISTER,
BEFORE compute: (i) which M4-F4/M4-F5 cell is the base and why; (ii) the gap
derivation from the world's own phi range; (iii) G5's aggregation rule. All
three, plus every other implementation choice, are fixed here.

### 0.1 Reuse boundary

Directly imported/called, never reimplemented: `f1().load_spec`,
`f1()._directions`, `f1().e1()`, `f1().build_layout`, `f1().featurize_panel`,
`f1().half_indices`, `f1().knob_tag` (from
`scripts/run_suica_m4_f1_panel_sizing.py`); `f2().generate_world_composed`,
`f2().occasion_labels`, `f2().shock_vector`, `f2().run_gate_g1`,
`f2().run_gate_g3` (from `scripts/run_suica_m4_f2_composition.py`);
`f3().world_seed_for`, `f3().run_gate_g3` (from
`scripts/run_suica_m4_f3_composition_scaling.py`); `f4().build_live_tasks`,
`f4().cell_name_live`, `f4().seed_suffix_for_mult` (from
`scripts/run_suica_m4_f4_author_axis.py`); `f5().run_truth_sweep_world`
(called DIRECTLY, unchanged, for the RAW base1x gate-anchor cells --
literally M4-F4's/M4-F5's own computation), `f5().field_from_vectors`,
`f5().generate_truth_vectors_long` (Truth Variant B, reused **completely
unchanged** -- see 0.6), `f5().T_LARGE_PRIMARY`, `f5().G4_TOLERANCE` (from
`scripts/run_suica_m4_f5_gauge_validity.py`).

Newly written, because no prior leg has it: `generate_world_spread` /
`generate_truth_vectors_exact_spread` (the block+gap generator and its
noise-free Truth-Variant-A counterpart, 0.5); `block_layout` /
`block_occasion_labels` / `block_boundary_label_pairs` (0.4); `common_layout`
(0.4); `run_spread_sweep_world` (the per-world engine for the adjudicated
cells, a disclosed structural near-duplicate of `f5().run_truth_sweep_world`
substituting the two new generators and calling every other primitive
unchanged); gates G2 (new comparison target) and G5 (wholly new); the
adjudication code.

### 0.2 Base cell and the two-tier B=1 resolution

**Base cell: `base1x`** (author_mult=1, event_mult=1) -- the smallest,
cheapest, and most heavily-anchored cell in this line (every prior leg's own
G1/G2-style gate ultimately traces back to it), chosen for compute economy
and because the registration only requires picking ONE M4-F4/M4-F5 cell, not
the largest.

**A genuine tension, disclosed and resolved here, BEFORE compute.** The
registration requires BOTH (a) "each swept multiple's total event count is
exactly equal" across B (the task's own "FIXED TOTAL EVENTS" instruction) AND
(b) G2's bit-identical reproduction of M4-F5's own persisted `base1x_shared_k05`/
`k10` cells at B=1. These cannot both be satisfied by a SINGLE B=1
computation: M4-F5's own base1x cells use the panel's RAW, untruncated
per-author counts (`{8,10,12,14,16}`, verified below, total 13,202 events),
while B in {2,4,8} need EXACT per-author divisibility by B (up to 8), which
the raw counts do not have. Mirroring M4-F2's own established precedent for
exactly this situation (a separate raw-layout G1 gate-anchor, distinct from
the six common-budget adjudicated cells), this leg computes **two distinct
B=1-shaped objects**:

1. **`base1x_shared_k05`/`k10`** (RAW budget, 13,202 events) -- computed via
   a DIRECT, unchanged call to `f5().run_truth_sweep_world` on M4-F4's own
   byte-identical task (`f4().build_live_tasks(..., [1], kappa_tags)`).
   Used **only** as G2's gate-anchor comparison target. Not part of the
   adjudicated B-sweep.
2. **`b1_shared_k05`/`k10`** (COMMON budget, `M_COMMON=8` events/author,
   7,880 events total -- see 0.4) -- the actual **B=1 point of the
   adjudicated sweep**, at the IDENTICAL total-event budget as `b2`/`b4`/`b8`.
   Computed via the SAME `generate_world_spread`/`run_spread_sweep_world`
   machinery used for B in {2,4,8}, with `block_count=1` (a trivial
   single-block case -- see 0.5).

G2 is checked against object 1 (a real, meaningful, bit-exact check of
`run_truth_sweep_world` on identical world seeds). Every registered lean and
the pivot are computed on object 2 (the true fixed-budget family). This
keeps the "FIXED TOTAL EVENTS" comparison uncontaminated by a ~40% budget
gap while still giving G2 the strict, literal reproduction check its own
language ("A mismatch VOIDS the comparison") demands.

### 0.3 The inter-block gap, derived from the world's own phi range

Calibrated knobs (`results/m4_f1_panel_sizing/calibration_record.json`,
read verbatim, no new calibration): `phi_lo=.20`, `phi_hi=.80`. The AR(1)
state `x` is stationary with `corr(x_t, x_{t+h}) = phi^h`; the worst case
(slowest-decorrelating) author has `phi=phi_hi=.80`.
`block_occasion_labels`' own arithmetic (block `b`'s labels =
`[b*(s+GAP), b*(s+GAP)+s-1]`) puts a label-index STEP of `GAP+1` (a
discrete-indexing +1, not tunable away) between the last label of one block
and the first label of the next.

**GAP=40** -> label step 41 -> worst-case theoretical autocorrelation
`0.8**41 = 1.065e-4`. Compared against the smallest per-cell SE measured
anywhere in this line at comparable panel scale (M4-F5's own `base1x`
`agreement_se` ~ .0017-.0026) and against the intrinsic sampling SE of a
SINGLE-WORLD G5 correlation estimate itself (pooling `n*(B-1)*k` (author,
factor) pairs -- at the smallest tested cell, `B=2`, `n=985*1*48=47,280`
pairs, giving an intrinsic SE of order `1/sqrt(47280) ~= .0046`, itself
~43x the theoretical correlation) -- GAP=40 provides roughly three to four
orders of magnitude of margin. GAP is held FIXED across every swept B (one
registered constant, verified by G5 at every cell, never tuned per B or
after seeing any result).

### 0.4 The uniform common-budget layout, `M_COMMON=8`

**Verified before compute** (not merely assumed): the `base1x` panel's
per-author raw event counts, across ALL 985 authors and every split, are
`{8,10,12,14,16}`; the MINIMUM raw count, across D0 AND D1/D2, is exactly
**8** (`min(raw_counts)==8`, checked programmatically before any generator
code was written). `M_COMMON=8` is set to this panel-wide minimum.

**Why a single panel-wide constant, not a per-author floor-to-nearest-
multiple-of-B (M4-F2's own precedent for a superficially similar problem).**
A per-author floor (e.g. `8*(m//8)`) would give raw count 16 authors a
DIFFERENT block size (`s=2`) than raw count 8 authors (`s=1`) at `B=8`.
Because block START positions are `b*(s+GAP)`, a different `s` shifts EVERY
block boundary after the first to a DIFFERENT absolute occasion-label value
for different authors -- silently breaking the cross-author occasion-label
ALIGNMENT that the entire "shared" design's cross-author correlation
mechanism depends on (two authors in the same context only share a shock if
they land on the identical `(context, occasion)` pair). A single constant
`M_COMMON`, applied to literally every author regardless of raw count, keeps
block boundaries IDENTICAL for every author at every swept B, preserving
that alignment exactly, at the disclosed cost of truncating higher-count
authors (up to 8 of 16 events, 50%, for the 282-of-565 `m=16` D1/D2
authors). This is the leg's own resolution of an implementation choice the
registration left open; verified NOT to exclude any author (`M_COMMON`
equals the panel MINIMUM, so `event_count=8>=MIN_RETAINED_EVENTS=8` holds
for literally every author).

**Budget cost, disclosed exactly.** Raw `base1x` total = 13,202 events
(985 authors). Common-budget total = `985*8 = 7,880` events. Loss = 5,322
events (40.3%) relative to the raw panel -- substantial but principled, and
IDENTICAL across every one of the four adjudicated B points (verified as an
exact-equality diagnostic in Part 1, not merely asserted).

### 0.5 The block+gap generator (the ONLY new generator mechanism this leg introduces)

**The central technical finding driving this leg's entire construction.**
Every prior generator in this family (`f1().generate_world`,
`f2().generate_world_composed`) draws the AR(1) state `x` over exactly
`t_max = max(counts)` steps, ONE STEP PER OBSERVED EVENT -- there is no
"gap" concept anywhere in the existing code: `x`'s time axis is tied to
observed-event-count, not to occasion (calendar) time. Occasion LABELS in
the existing "shared"/"free" modes are used ONLY to key the shared-shock
lookup (`shock_vector(world_seed, context, occasion, k)`); they never index
into `x`. This means simply reusing `f2().generate_world_composed` with a
different `occasion_labels` function (the naive approach) would NOT
introduce any genuine AR(1) decorrelation at all -- `x` would still evolve
one step per observed event, with no gap ever simulated.

`generate_world_spread` (new) fixes this: `x` is drawn over the FULL
occasion-time axis `t_span = block_count*s + (block_count-1)*GAP` (block
positions AND the unobserved gap positions between them), using the
identical AR(1) recursion (`_draw_ar1_span`, extracted verbatim in form from
`f1().generate_world`'s own loop). Observed events are then read off `x` at
the block positions only (`x[:, labels, :]`), so the state GENUINELY evolves
through, and decorrelates across, the simulated gap -- this is what G5
verifies (0.7). Everything else (`loadings`, `z`, `zeta`, `phi`, `mean_part`,
the shock cache/blend, `noise`) is a direct structural copy, in form, of
`f2().generate_world_composed`'s own kappa>0 branch.
`generate_truth_vectors_exact_spread` (Truth Variant A, new) is the
noise-free counterpart, sharing an IDENTICAL rng draw prefix
(`_draw_common_state` + `_draw_ar1_span`, factored into shared helpers so
the two functions replay bit-identically given the same `world_seed`) --
mirroring M4-F5's own `generate_truth_vectors_exact` discipline exactly,
including drawing a same-shaped but UNUSED noise term for stream-order
symmetry.

`block_count=1` is NOT special-cased: with `s=M_COMMON=8` and
`block_count-1=0` gap terms, `t_span=8` and `block_occasion_labels`
degenerates to plain `arange(8)`, matching "shared" mode's own labels
exactly (mathematically, not merely superficially) -- one generator function
handles the whole B in {1,2,4,8} family.

### 0.6 Why Truth Variant B needs NO change under block+gap spreading

`f5().generate_truth_vectors_long` resamples the AR(1) state over `T_LARGE`
FRESH synthetic occasions (`0..T_LARGE-1`), using the SAME per-author `phi`
and the SAME deterministic `f2().shock_vector` for those occasion indices --
this construction characterizes "this world's long-run signature"
independent of how the FINITE, OBSERVED panel's own occasions happen to be
arranged. It takes `counts` only to read `len(counts)`; nothing about block
or gap structure enters it. It is therefore reused **completely unchanged**
for the spread cells (called on the spread cell's own `world_seed`, so
`loadings`/`z`/`zeta`/`phi`/`mean_part` replay bit-identically to that
cell's own live world by construction).

### 0.7 G5's aggregation rule, registered BEFORE the run (the standing rule from M4-F4's G0 ambiguity)

For each `(block_count, kappa)` combination with `block_count>=2` (6 cells:
`{2,4,8}x{k05,k10}`; `block_count=1` has zero boundary pairs -- nothing to
check), **pool** the realized cross-block-boundary correlation of the RAW
(pre-kappa-blend) AR(1) state `x` across ALL authors (n=985) x ALL factors
(k=48) x ALL adjacent boundary pairs (`block_count-1` pairs) WITHIN each of
the 8 worlds, giving ONE Pearson correlation per world (8 values per cell).
**Aggregate** across the 8 worlds via mean/SE, t-test against 0 (df=7).
**This is a PER-CELL rule, not a trend-across-B rule**: the fixed GAP is
designed to decorrelate at EVERY block_count independently, so there is no
principled reason to expect the residual correlation to trend with B (unlike
M4-F4's G0, whose registered concern was specifically an artifact that
SCALES WITH the swept axis). **G5 PASSES if and only if `|t|<2.0` at EVERY
ONE of the 6 tested cells** -- mirroring this line's own established
"indistinguishable from zero" bar (`f1().cell_summary`'s own `rise`
threshold, `mean/se>=2.0`, applied here in the opposite direction: NOT
crossing the bar, rather than crossing it). `x`'s own autocorrelation does
not depend on `kappa` by construction (`kappa` only enters the SUBSEQUENT
blending step, after `x` is drawn) -- both kappas are expected to agree and
are checked anyway, under this leg's own convention of independent world
draws per `(block_count, kappa)` cell (0.9), for thoroughness rather than
necessity. A `|t|>=2.0` at ANY tested cell VOIDS the leg, per the
registration, with no repair-and-rerun.

### 0.8 Lean and pivot operationalizations

**Lean (a).** Paired-by-world difference, `truth_recovery_long(b8) -
truth_recovery_long(b1)`, matched by world index (0-7, mirroring
`f2()._paired_ci`'s own construction, reused verbatim), at kappa=1.0
(primary). HOLD if the 95% CI excludes zero on the positive side.

**Lean (b).** Registered text: "same-occasion truth recovery does NOT rise
with B by more than half the long-window gain." Operationalized as a
POINT-ESTIMATE comparison of the two paired diffs (the registered language's
plain "does NOT rise ... by more than half" reads as a magnitude comparison,
not itself requiring a further CI, though each diff's own CI is reported for
context): HOLD if `mean(paired_diff_A) <= 0.5 * mean(paired_diff_B)`, where
`paired_diff_B` is lean (a)'s own statistic. Registered caveat, disclosed
here BEFORE seeing the sign of lean (a)'s own result: if lean (a)'s point
estimate is not clearly a positive "gain," this comparison against "half a
gain" loses its intended meaning (there is no gain to be half of) -- the
literal rule is still applied exactly as registered, with this
interpretive caveat attached to the output rather than silently changing
the rule.

**Lean (c).** Registered text: "split-half agreement is approximately
B-invariant (max-to-min across B within +/-20% of the B=1 value)."
Two readings are possible and both are computed (Part 1 discloses which
number was used to gate and reports both): **Reading 1 (adopted for the
gate)**, a per-point band -- every one of the 4 swept B's agreement lies
within `B1_value +/- 0.20*B1_value`. **Reading 2 (stricter, computed
alongside from the same persisted numbers)** -- the max-to-min SPREAD
itself is `<= 0.20*B1_value` (a single-sided reading of "the spread ... is
within 20%", narrower than reading 1's `+/-20%` band, which allows a
spread of up to `0.40*B1_value` in the worst case). Reading 1 is adopted
as the literal parse of "max-to-min ... within +/-20% OF THE B=1 VALUE"
(the "+/-" attaches most naturally to a per-point deviation from the
reference, not to the spread statistic itself), consistent with how this
line has read similar "+/-X%" language elsewhere; Reading 2's number is
reported alongside per this line's own disclosure discipline for
ambiguous rules.

**Kappa scope (0.9).** Leans (a)/(b)/(c) and the pivot are evaluated at
kappa=1.0 (primary), mirroring M4-F3's/M4-F4's own treatment of their
non-decisive kappa. Kappa=0.5 is computed identically (its own independent
8-world sweep, own seed lineage) and reported as context in every table,
gating nothing.

### 0.9 Independent world draws per (block_count, kappa) cell

Every `(block_count, kappa)` combination -- including the two flavors of
B=1 -- gets its OWN `seed_key` (`f"b{block_count}_{kappa_tag}"` for the
adjudicated family, salt `"m4f6-spread-world"`, distinct from every prior
leg's own world salt) and hence its OWN independent 8-world draw, mirroring
this line's established convention (M4-F2/F3/F4/F5 all bake kappa into
`seed_key`, giving independent draws per kappa) rather than sharing one
world draw across B or kappa. "Paired-by-world" throughout this leg (as
throughout the whole line) means paired by ORDINAL world index 0-7 for
statistical blocking, not by identical underlying random substrate.

### 0.10 Budget/gate scope summary

Gates: **G1** (direct call, `f2().run_gate_g1`) -- kappa<=0 free cell
reproduces M4-F1's persisted `base1x`. **G2** (new) -- the RAW
`base1x_shared_k05`/`k10` gate-anchor cells reproduce M4-F5's persisted
agreement AND both truth-variant means to <=1e-12. **G3** (direct call,
`f3().run_gate_g3()`) -- gauge/map/halving invariance. **G4** (new
comparison scope, identical mechanism to M4-F5's own) -- truth-path
invariance across every world of every one of the 10 computed cells (2
anchor + 8 adjudicated). **G5** (wholly new, 0.7) -- the decorrelation
check. `M_COMMON=8` and `GAP=40` are registered constants, not tuned after
seeing any gate or lean number.

---

*(Everything below this line was written after the run. Part 0 above was
not edited after compute began.)*

## Part 1 -- OUTCOME

**0/3 primary leans HOLD except lean (c); PIVOT FIRES. Verdict:
`OCCASION_SPREAD_NOT_THE_LEVER_TRAIT_LEVEL_UNCERTIFIABLE_ON_ALL_THREE_AXES`.**
At kappa=1.0 (primary), long-window truth recovery (Variant B) does NOT rise
from B=1 to B=8 at fixed total budget -- the paired-by-world difference is
**-0.0254** (95% CI **[-0.0699, +0.0192]**, including zero) -- so per the
registration's own pre-committed consequence: **trait-level relation
structure is not certifiable on ANY of the three panel axes (authors,
events, occasions) tested across this M4-F line, and the D3 program is
restricted to occasion-bound objects.** Lean (c) -- the gauge is B-invariant
-- HOLDs cleanly, exactly matching the registration's own prediction that
this would be "the sharpest and most falsifiable of the three... the one
that would explain why four legs of gauge optimization never touched trait
certification."

Run: anchor stage (2 RAW base1x cells x 8 worlds) in 28s; sweep stage (8
adjudicated cells x 8 worlds) in two foreground chunks by kappa, 44s (k10)
+ 46s (k05); gates in 11s; finalize <1s. `--workers 8` throughout. Total
compute **under 2 minutes**. `MASTER_SEED=20260802` (identical to every
prior leg in this line), knobs read verbatim from M4-F1's
`calibration_record.json` (`k=48, rho=.50, w_mu=.15, w_x=.15, w_e=.70, phi
in [.20,.80]`) -- no new calibration search.

## Gates (all five green)

- **G1** (kappa<=0 free cell reproduces M4-F1's persisted `base1x`; direct
  call to `f2().run_gate_g1`): abs diffs 9.9e-17 (agreement_mean), 1.1e-16
  (agreement_se), 0.0 (d0_eff_rank_M_mean), 7.1e-15 (d0_eff_rank_K_mean), 0
  (n_retained) -- identical numbers to every prior leg's own G1 (same
  function, same call). **PASS.**
- **G2** (the RAW `base1x_shared_k05`/`k10` gate-anchor cells reproduce
  M4-F5's persisted agreement AND both truth-variant means): max abs diff
  across both cells x 4 checked fields (`agreement_mean`, `agreement_se`,
  `truth_recovery_exact_mean`, `truth_recovery_long_mean`) is **6.2e-17** --
  floating-point noise, not a substantive mismatch; `d0_eff_rank_M/K_mean`
  and `n_retained` also matched exactly (0.0 / 0 diff). **PASS.**
- **G3** (gauge invariance; direct call to `f3().run_gate_g3()`): batched
  feature map vs. deployed `v8.build_feature_panel` bit-identical; halving
  vs. `e1().split_half_frames` identical. **PASS.**
- **G4** (truth-path invariance, identical mechanism to M4-F5): max diff
  across all 10 computed cells (2 anchor + 8 adjudicated) x 8 worlds = 80
  world-checks = **exactly 0.0** -- matching M4-F5's own "exactly 0.0"
  achievement in full. **PASS.**
- **G5** (decorrelation check, Part 0.7's pre-registered aggregation rule):
  all 6 tested `(block_count, kappa)` cells have `|t|<2.0`. Correlation
  means range **-0.00161 to +0.00069** (all four orders of magnitude below
  any per-cell SE measured elsewhere in this line), t-statistics range
  **-1.976 to +0.795**. **PASS**, but disclosed as a genuinely close call at
  one cell: `b4_shared_k05` landed at `t=-1.976`, immediately under the
  `|t|<2.0` bar (correlation_mean=-0.001606, se=0.000813, n_pairs/world=
  141,840). No cell was repaired, re-run, or had its gap adjusted after
  seeing this number -- the gate is reported exactly as computed on the
  first and only run. Full table:

| block_count | kappa | correlation_mean | correlation_se | t_stat | n_pairs/world | pass |
|---|---|---|---|---|---|---|
| 2 | 0.5 | +0.000492 | 0.001210 | +0.407 | 47,280 | yes |
| 2 | 1.0 | +0.000686 | 0.000863 | +0.795 | 47,280 | yes |
| 4 | 0.5 | -0.001606 | 0.000813 | **-1.976** | 141,840 | yes (closest) |
| 4 | 1.0 | -0.001150 | 0.000838 | -1.373 | 141,840 | yes |
| 8 | 0.5 | -0.000504 | 0.000306 | -1.644 | 330,960 | yes |
| 8 | 1.0 | -0.000258 | 0.000587 | -0.441 | 330,960 | yes |

Pooled grand mean across all 6 cells: -0.00039 (supplementary context only,
per Part 0.7 -- NOT the gating statistic). `results/m4_f6_occasion_spread/
gates.json` carries the full detail for all five gates.

## Budget conservation (diagnostic, not a lettered gate, verified exactly)

Every one of the 8 adjudicated `b{1,2,4,8}_shared_k{05,10}` cells allocates
**exactly 7,880 events** (`985 authors x M_COMMON=8`) -- identical across
every swept B and both kappas, verified as exact integer equality from the
persisted `n_events_total` column, not merely asserted. The two RAW
gate-anchor cells allocate 13,202 events each (M4-F1's own raw `base1x`
total), by design NOT equal to the adjudicated family's budget (Part 0.2).

## The full B-vs-metrics table (both kappas, all three gauges)

| B | kappa | agreement | agreement SE | truth A (same-occasion, exact) | truth A SE | truth B (long-window) | truth B SE |
|---|---|---|---|---|---|---|---|
| 1 | 0.5 | 0.010993 | 0.002865 | 0.148493 | 0.006873 | 0.019555 | 0.007496 |
| 1 | 1.0 | **0.035248** | 0.004649 | **0.114013** | 0.007970 | **0.049185** | 0.010365 |
| 2 | 0.5 | 0.015184 | 0.005394 | 0.152545 | 0.007505 | 0.002014 | 0.008584 |
| 2 | 1.0 | **0.036484** | 0.004204 | **0.116498** | 0.010130 | **0.028907** | 0.012638 |
| 4 | 0.5 | 0.017682 | 0.003616 | 0.155561 | 0.006101 | -0.003316 | 0.006942 |
| 4 | 1.0 | **0.029720** | 0.003051 | **0.122384** | 0.009369 | **0.030441** | 0.007518 |
| 8 | 0.5 | 0.008687 | 0.004176 | 0.149485 | 0.007233 | 0.010438 | 0.004484 |
| 8 | 1.0 | **0.035839** | 0.005313 | **0.108984** | 0.008861 | **0.023824** | 0.011874 |

(kappa=1.0 rows, the primary/decisive line, in **bold**.) The pattern is
directly visible without any statistic: at kappa=1.0, agreement is flat
(0.0297-0.0365) across the entire B sweep, truth A is flat
(0.1090-0.1224), and truth B is HIGHEST at B=1 (0.0492) and LOWER at every
B>=2 (0.0289, 0.0304, 0.0238) with no further monotone trend among
B in {2,4,8} themselves.

## Lean adjudication

- **Lean (a) MISS.** Paired-by-world (`b8 - b1`, truth recovery long,
  kappa=1.0): mean **-0.025362**, SE 0.018825, t=-1.347, 95% CI
  **[-0.069876, +0.019153]** -- includes zero, and the point estimate is
  negative (a decline, not a rise). Context (kappa=0.5, non-gating): mean
  -0.009117, SE 0.006918, 95% CI [-0.025475, +0.007241] -- also includes
  zero, same sign, a weaker but qualitatively identical pattern at the
  kappa where the AR(1) state genuinely enters the observed data (see
  Interpretation below).
- **Lean (b) MISS.** Paired-by-world (`b8 - b1`, truth recovery exact,
  kappa=1.0): mean -0.005028, SE 0.009780, 95% CI [-0.028154, +0.018097] --
  includes zero. Half of lean (a)'s own paired diff = -0.012681. The
  registered rule (`mean(diff_A) <= 0.5*mean(diff_B)`) evaluates to
  `-0.005028 <= -0.012681`, which is **FALSE** (-0.005028 is the LESS
  negative of the two) -- MISS by the literal rule. Disclosed interpretive
  caveat (registered in Part 0.8 before seeing this sign): lean (a)'s own
  "gain" is negative, so "does not rise by more than half the gain" is
  being evaluated against a negative target; read plainly, same-occasion
  truth recovery (Variant A) DECLINED LESS under spreading than long-window
  truth recovery (Variant B) did (-0.0050 vs -0.0254) -- if anything this
  is weak, non-registered evidence in the DIRECTION the underlying idea
  points (spreading changes which object is estimable rather than sharpening
  the state-inclusive one), but the registered rule's literal MISS verdict
  stands as computed, per the task's own instruction to report the letter
  of an ambiguous-context rule plainly rather than rescue it.
- **Lean (c) HOLD** under the adopted Reading 1 (0.8): agreement at B in
  {1,2,4,8}, kappa=1.0: 0.035248 / 0.036484 / 0.029720 / 0.035839. B=1
  reference 0.035248; +/-20% band = +/-0.007050 (range
  [0.028198, 0.042298]). Every one of the four values falls inside the band
  (largest deviation: B=4, `|0.029720-0.035248|=0.005528`, 78.4% of the
  band). **Reading 2 (stricter, computed alongside per Part 0.8's disclosed
  ambiguity)**: max-to-min itself = `0.036484-0.029720=0.006764`; compared
  to `0.20*0.035248=0.007050` -- `0.006764 <= 0.007050` is **also TRUE**,
  but by a much tighter margin (95.9% of the tolerance consumed, vs Reading
  1's 78.4% at its own tightest point). **Lean (c) HOLDs under BOTH
  readings**, though Reading 2's margin is close enough that a reader
  applying the stricter parse should know how little room it left.

## Pivot adjudication

**PIVOT FIRES.** Registered rule: "long-window truth recovery does not rise
with B (paired CI includes 0)." Lean (a)'s own CI, `[-0.069876,
+0.019153]`, includes zero -- the pivot condition is met exactly, with no
ambiguity (unlike lean (c), this rule has only one natural reading and both
components -- CI-includes-zero and the point estimate being negative --
point the same direction). Per the registration's own pre-committed
consequence: **trait-level relation structure is not certifiable on ANY of
the three panel axes tested by this M4-F line (authors: M4-F4's own law was
subsequently shown by M4-F5 to certify only an occasion-bound object; events:
M4-F1/M4-F3 showed scale/composition-rate both fail; occasions: this leg).
The D3 program's claims are permanently restricted to occasion-bound
objects, and the registered next question becomes the M4-E2 objective
redesign (`OFFSET_SPREAD_NO_SINGLE_OBJECTIVE_TERM`) with the panel side
closed on all three axes.**

## Interpretation: a mechanistic reading of WHY the primary kappa shows no effect (a reading, not a registered claim, clearly separated from the adjudication above)

Re-examining the blend formula both the live world and both truth variants
share: `blended_x = sqrt(1-kappa)*x_at_labels + sqrt(kappa)*shock_x`. At
**kappa=1.0 exactly**, `sqrt(1-kappa)=sqrt(0)=0`, so **`blended_x =
shock_x` identically -- the author-private AR(1) state `x` contributes
NOTHING to the observed panel or to EITHER truth variant at the primary
kappa.** `shock_vector` is an independent, freshly-hashed draw per
`(context, occasion)` pair regardless of which occasion-label VALUES are
used -- so whether occasion labels are sequential (`0..7`, B=1) or spread
with gaps (`{0,41,...,287}`, B=8), the cross-author sharing STRUCTURE this
leg's uniform-block design preserves (every author in a context still lands
on the identical set of labels as every other author in that context, at
every B) is statistically UNCHANGED; only the specific hashed vectors
differ, and their distribution does not depend on label spread. Under this
reading, **at kappa=1.0 the entire occasion-spread manipulation has, by the
generator's own algebra, zero causal channel to any of the three adjudicated
quantities** -- the observed B1-vs-B8 differences are attributable to
ordinary independent-world sampling variation between the two cells'
distinct seed draws, not to any effect of spreading itself. This would fully
explain lean (c)'s clean HOLD (nothing CAN move the gauge with B here) and
gives a mechanism-level account of the pivot beyond "no effect was
detected", separate from and not required by the (already sufficient)
statistical pivot rule itself.

This reading is NOT the whole story, however: **kappa=0.5 gives `x` a
genuine, non-zero causal channel** (`sqrt(1-.5)=sqrt(.5)~=.707`, an
equal-variance blend with `shock_x`), yet the kappa=0.5 context row shows
the SAME qualitative pattern -- a negative point estimate, CI including
zero (0.9's independent-draw context, above). If the kappa=1.0 algebraic
degeneracy were the ENTIRE explanation, kappa=0.5 (where spreading DOES
have a real mechanism to act through) might be expected to show at least a
weak positive signal; it does not. **This strengthens, rather than
undermines, the pivot's substantive finding**: even on the one kappa where
occasion spread mechanically CAN matter, no positive effect on long-window
truth recovery appears in this data -- the kappa=1.0 degeneracy is an
additional, deeper reason the PRIMARY condition specifically was guaranteed
to show nothing, layered on top of (not a substitute for) a genuine null on
the causally-live axis too. G5's own PASS is unaffected by any of this --
it correctly verifies the manipulation does what it claims to the state `x`
itself; this reading is about what happens to that decorrelated state
AFTER it enters (or, at kappa=1.0, fails to enter) the blend.

## Honest anomalies and disclosures

1. **The two-tier B=1 resolution (Part 0.2)** is a genuine, disclosed
   accommodation of a tension the registration itself created (bit-identical
   G2 vs. fixed-total-budget), not a hidden convenience -- resolved by
   direct appeal to M4-F2's own established precedent for the identical
   situation.
2. **`M_COMMON=8` costs 40.3% of the raw `base1x` panel's events**
   (13,202 -> 7,880), concentrated in the 282-of-565 `m=16` D1/D2 authors
   (who lose exactly half their own events). This is the price of exact
   cross-author occasion-label alignment (Part 0.4); the alternative
   (per-author floor-to-nearest-multiple-of-B) would have preserved more
   data but silently broken that alignment for every block after the first.
3. **G5's closest cell (`b4_shared_k05`, t=-1.976) is genuinely close to
   the `|t|<2.0` bar** -- reported with its exact number rather than
   folded into a flat "all pass," per this line's own disclosure
   discipline (mirroring M4-F4's own G0 addendum). No repair or re-run
   followed from seeing it.
4. **Lean (c)'s registered "+/-20%" language admits two readings**
   (Part 0.8/Part 1); both are computed from the same persisted numbers and
   both HOLD, but the stricter reading's margin (95.9% of tolerance used)
   is close enough to be worth a reader's own judgment, not just the
   adopted verdict.
5. **Lean (b)'s "half the gain" rule is evaluated against a negative
   "gain"** (lean (a) itself missed) -- the registered caveat anticipating
   exactly this was written in Part 0.8, BEFORE the sign of lean (a)'s
   result was known, and the literal rule's MISS verdict is reported
   without softening, with the caveat attached for interpretation only.
6. **The mechanistic "kappa=1.0 zeroes out x" reading (above) was derived
   AFTER seeing the null result**, not registered in advance -- disclosed
   plainly as a post-hoc reading, consistent with this line's convention of
   clearly separating registered adjudication from interpretive readings
   that follow it.
7. Total main-pipeline compute was under 2 minutes (985-author panels
   throughout, no author-multiple scaling in this leg) -- by far the
   cheapest leg in the M4-F line; no memory-safety revisions were needed
   (contrast M4-F5's own T_LARGE/chunk-size revision at the much larger
   x32-holdout scale).

## Decision boundary

Exploratory, synthetic-calibrated, label-free. This leg tested the third and
final classical panel-design axis (occasion spread) against the trait-like
long-window truth target M4-F5 showed the first two axes (authors, events)
could not reach. It found no rise, at fixed budget, under a spreading
manipulation independently verified (G5) to genuinely decorrelate the
underlying AR(1) state at the chosen gap -- so the null is not attributable
to an ineffective manipulation. Per the registration's own pre-committed
consequence, **trait-level relation structure is not certifiable on any of
the three panel axes in this world; the D3 program's claims are
permanently restricted to occasion-bound objects on this synthetic
instrument**, and the registered next question (M4-E2 objective redesign)
now owns the problem with no panel-side escape route remaining. This
licenses a finding about panel DESIGN under this calibrated synthetic
instrument only -- it makes no claim about the real relation field's actual
content, personality, emotion, diagnosis, or any individual. Artifacts:
`results/m4_f6_occasion_spread/{decision.json, gates.json, cells.csv,
cell_*.csv, draws_*.csv}`.
