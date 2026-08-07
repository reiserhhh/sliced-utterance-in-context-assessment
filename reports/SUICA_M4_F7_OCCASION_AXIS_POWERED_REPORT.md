# SUICA M4-F7 -- The Occasion Axis, Properly Powered (Authors x16)

> **BANNER: synthetic worlds calibrated to an opened-panel regime, exploratory.**
> This leg consumes NO new real-text evidence. It repeats M4-F6's occasion-
> spread sweep at 16x the author count, reusing M4-F6's own block+gap
> generator, common-budget construction, two truth variants, and G5
> decorrelation check VERBATIM, by direct call into F6's own module. No label
> columns anywhere; no claim about the real relation field's content,
> personality, emotion, diagnosis, or any individual.

Registered spec: `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md`
section "M4-F7 registration (2026-08-03, BEFORE run) -- the occasion axis,
properly powered", together with the preceding "M4-F6 planner adjudication
note" (the standing rule this leg exists to satisfy). Script:
`scripts/run_suica_m4_f7_occasion_axis_powered.py`. Artifacts:
`results/m4_f7_occasion_axis_powered/`.

## Part 0 -- REGISTERED ADJUDICATIONS AND OPERATIONALIZATIONS (written before the run)

The registration fixes the design as "identical to M4-F6 except for scale":
shared-occasion design, kappa=1.0 only, authors x16, common-budget
construction, block count B in {1,2,4,8}, M4-F6's own verified 40-step gap,
8 worlds x 20 draws. It mandates a NEW gate, G0 POWER, as the first thing to
report, and requires G2 continuity to state explicitly which object each
check uses. Every implementation choice below was fixed in the script
BEFORE any of the six `--stage` calls (`anchor`, `construction-check`,
`sweep`, `gates`, `finalize`) was run.

### 0.1 Reuse boundary

Directly imported/called, never reimplemented: `f1().load_spec`,
`f1()._directions`, `f1().e1()`, `f1().build_layout`, `f1().featurize_panel`,
`f1().half_indices`, `f1().knob_tag` (from
`scripts/run_suica_m4_f1_panel_sizing.py`); `f2().run_gate_g1` (from
`scripts/run_suica_m4_f2_composition.py`); `f3().run_gate_g3` (from
`scripts/run_suica_m4_f3_composition_scaling.py`); `f4().build_live_tasks`
(from `scripts/run_suica_m4_f4_author_axis.py`); `f5().run_truth_sweep_world`
(called DIRECTLY, unchanged, for the RAW authors-x16 gate-anchor cell --
literally M4-F5's own computation, repeated), `f5().field_from_vectors`,
`f5().generate_truth_vectors_long`, `f5().T_LARGE_PRIMARY`,
`f5().G4_TOLERANCE` (from `scripts/run_suica_m4_f5_gauge_validity.py`);
**`f6().generate_world_spread`, `f6().generate_truth_vectors_exact_spread`,
`f6().g5_world_correlation`, `f6().spread_world_seed_for`, `f6().GAP`,
`f6().M_COMMON`, `f6()._paired_ci`** (from
`scripts/run_suica_m4_f6_occasion_spread.py`) -- ALL called directly,
unchanged. This last group is the leg's central reuse commitment: the
occasion-spread MECHANISM itself (the block+gap generator, its noise-free
truth counterpart, the decorrelation diagnostic, the paired-CI construction)
is not re-derived at all, only re-scaled.

Newly written, because nothing prior exposes an author-scale parameter:
`common_layout_scaled` (0.2, F6's own `common_layout` generalized to accept
`author_mult`); `_prepare_spread_world` / `run_spread_sweep_world` (a
disclosed structural near-duplicate of F6's own same-named functions,
necessary ONLY because the world-building step calls
`common_layout_scaled(reference, task["author_mult"])` instead of F6's
hardcoded `common_layout(reference)` -- every downstream primitive is called
exactly as F6 itself calls it); the G0 POWER gate (0.3, wholly new); the
construction-check cell/task builder and gate G2(a) (0.2); `cell_summary`
and gates G1/G2/G3/G4/G5, OUT-scoped to this script's own artifact tree
(each leg's `cell_summary`/gates has always been OUT-scoped even when the
underlying rule is reused verbatim -- see F5's/F6's own `cell_summary`, each
a disclosed near-duplicate of the previous one for exactly this reason); the
adjudication code (leans a/b/c with the registered lean-(b)
inapplicable-on-non-positive-gain rule, the pivot, and the G0-gated finalize
branch).

### 0.2 The construction-check cell -- a THIRD tier beyond F6's own two-tier B=1 resolution

M4-F6's own report (Part 0.2) resolved a tension between "fixed total events
across the B sweep" and G2's bit-identical reproduction requirement by
computing two distinct B=1-shaped objects: a RAW gate-anchor
(`base1x_shared_k05`/`k10`) and the actual COMMON-budget adjudicated B=1
point (`b1_shared_k05`/`k10`). This leg inherits that exact same tension at
the new scale (RAW `authors_x16_shared_k10`, 211,232 events, vs. COMMON
`b1_x16_shared_k10`, 126,080 events) and resolves it identically -- that is
tier 1/2, unchanged in kind from F6.

This leg's registration adds a THIRD, genuinely new requirement beyond F6's
own: G2 must show "the B=1 cell reproduces M4-F6's own construction at the
same author scale where comparable." Since M4-F6 never computed anything at
authors x16, the only scale where a byte-exact F6 reference exists is
authors x1 (mult=1) -- so this leg computes one extra, GATE-ONLY cell,
`construction_check_mult1_b1_k10`: `author_mult=1`, `block_count=1`,
`kappa=1.0`, using F6's OWN exact `seed_key` (`"b1_k10"`), corpus prefix
(`"m4f6-"`), and `budget_label` (`"f6.0"`) -- run through THIS leg's
generalized, `author_mult`-parametrized orchestration. If the generalization
introduced no bug, this cell must reproduce F6's persisted `b1_shared_k10`
cell to <=1e-12 (G2(a)). This is a code-correctness check on the
generalization itself, not a scientific/adjudicated cell -- it never enters
`BLOCK_COUNTS`, the sweep, or any lean.

G2 therefore has two required sub-checks, stated explicitly per the
registration's own instruction: **G2(a) CONSTRUCTION** (the
`construction_check_mult1_b1_k10` cell vs. M4-F6's persisted
`b1_shared_k10`) and **G2(b) ANCHOR** (the RAW `authors_x16_shared_k10` cell,
computed via a direct unchanged call to `f5().run_truth_sweep_world` on
`f4()`'s own byte-identical mult=16 task, vs. M4-F5's persisted
`authors_x16_shared_k10` -- the direct scale-up of M4-F6's own G2, which
checked the same object at mult=1 against M4-F5's `base1x_shared_k05`/`k10`).

### 0.3 G0 POWER, operationalized

Per the M4-F6 planner note (verbatim standing rule) and the task's own
instruction: before adjudicating anything, report (i) the target's measured
level at this scale, read verbatim from
`results/m4_f5_gauge_validity/cells.csv` row `authors_x16_shared_k10`
(never retyped -- the gate reads the CSV directly), and (ii) the minimum
detectable paired difference this design's REALIZED SEs afford, computed as
the 95% CI half-width of the paired-by-world `b8_x16 - b1_x16` difference on
`truth_recovery_long`, using `f6()._paired_ci` verbatim (the identical
construction used for lean (a) itself, so the power statement and the lean
share one code path by design). **If that half-width exceeds
`G0_HALF_WIDTH_BAR=0.066`, G0 FAILS (declared UNDERPOWERED).**

### 0.4 M_COMMON and GAP -- reused verbatim, not re-derived

`M_COMMON=8` and `GAP=40` are read directly as `f6().M_COMMON` /
`f6().GAP` -- never redefined. `M_COMMON=8` remains valid at author_mult=16
because author replication (`f1().build_layout`'s own multiset-repetition
construction) does not alter any individual author's own raw event count --
it is still exactly the panel-wide minimum verified by F6, and
`common_layout_scaled` re-checks this (not merely assumes it) against the
actual x16 layout before use. `GAP=40`'s derivation (worst-case
`phi_hi=.80` giving `0.8**41=1.065e-4`) is a property of the world's
calibrated phi RANGE, which does not depend on author count either --
reusing the identical constant is the registration's own explicit
instruction ("M4-F6's verified gap of 40 steps"), and G5 (0.7 below)
empirically reverifies decorrelation held at the new scale rather than
assuming F6's own verification transfers automatically.

### 0.5 Kappa scope: k10 only

Per the registration ("kappa=1.0 only... M4-F6 established the kappa=0.5
behaviour is qualitatively the same and it is not worth the compute"), this
leg computes NO kappa=0.5 cells anywhere -- not for the sweep, not for the
anchor, not for the construction-check. Every lean, gate, and the pivot are
therefore evaluated on a single kappa. Where this report's Interpretation
section (Part 1) needs kappa=0.5 context, it cites M4-F6's own
already-registered, already-adjudicated kappa=0.5 finding rather than
recomputing it.

### 0.6 Lean and pivot operationalizations

**Lean (a).** Paired-by-world difference,
`truth_recovery_long(b8_x16) - truth_recovery_long(b1_x16)`, matched by
world index 0-7 (statistical blocking, not shared randomness -- each
`(block_count)` cell has its own independent `seed_key`/world draw, exactly
mirroring F6's own Part 0.9 convention), via `f6()._paired_ci` unchanged.
HOLD if the 95% CI excludes zero on the positive side.

**Lean (b).** Registered text: "same-occasion recovery rises by less than
half of any long-window gain (if the long-window gain is negative or null,
state that this lean is inapplicable rather than scoring it)." Unlike M4-F6
(which discovered this ambiguity mid-report and attached a disclosed
caveat), M4-F7's own registration resolves it in advance: operationalized
here as `gain_is_positive = ci_long["mean"] > 0`; if NOT positive, the lean's
verdict is written as `"INAPPLICABLE"` (a third value, not folded into MISS)
and the point-estimate rule is not evaluated at all. This was fixed in the
script before the run, before either paired diff's sign was known.

**Lean (c).** Identical rule and BOTH readings to M4-F6 (Reading 1, adopted:
a per-point +/-20%-of-B1 band; Reading 2, stricter: max-to-min <=20% of B1,
reported alongside).

**Pivot.** "The leg is adequately powered by its own pre-run standard
(G0 PASS) AND long-window recovery does not rise with B (paired CI includes
0)." Operationalized identically to F6's own pivot condition
(`ci_includes_zero OR NOT ci_excludes_zero_positive` -- the second disjunct
alone already covers both "CI straddles zero" and "CI lies entirely below
zero," so the two clauses are logically overlapping by construction, exactly
as they were in F6's own code, reused verbatim), conjoined with `G0["pass"]`.

### 0.7 G5's aggregation rule -- reused verbatim, scope halved

`f6().g5_world_correlation` and F6's own pre-registered per-cell `|t|<2.0`
rule (its Part 0.7) are applied exactly as written, with NO new aggregation
logic. The only change is scope: 3 cells here (`b2_x16`, `b4_x16`, `b8_x16`,
block_count>=2, kappa=1.0 only) instead of F6's own 6 (the same 3
block-counts x 2 kappas) -- half, because this leg drops kappa=0.5 (0.5
above). `b1_x16` (block_count=1) is `applicable=false`, mirroring F6's own
treatment of its own B=1 cell (zero boundary pairs, nothing to decorrelate).

### 0.8 G0 vs. G5: two different kinds of gate failure, disclosed as a genuine design choice

G1-G5 failing has always meant, in this line, "the mechanism is broken; VOID
the leg and do not repair-and-rerun" (F6's own explicit language for G5).
**G0 is different in kind, and this is a deliberate, disclosed departure**:
the registration's own text for G0 is "adjudicate NOTHING, and do not report
a null" -- i.e. an anticipated, VALID scientific outcome this leg must still
document in full (a complete report, plan-doc outcome, and ledger row), not
a mechanical defect. Accordingly, `run_gates` in this script raises
(halting the pipeline) if G5 fails, exactly as F6's own code does, but does
**NOT** raise if G0 alone fails -- it prints a plain warning and lets
`run_finalize` run, where the G0-fail branch writes a complete
`UNDERPOWERED_NO_ADJUDICATION` decision with the full power statement and
explicitly skips leans/pivot. This choice was fixed in the script before
compute; it did not need to be exercised (0.11 below), but is disclosed
here as a registered ambiguity-resolution regardless, per this line's own
convention of writing down non-obvious rule readings before seeing whether
they matter.

### 0.9 Budget/gate scope summary

Six cells computed in total: the RAW gate-anchor (`authors_x16_shared_k10`,
211,232 events, G2(b)'s target), the gate-only construction-check
(`construction_check_mult1_b1_k10`, 7,880 events, G2(a)'s target), and the
four adjudicated common-budget cells (`b{1,2,4,8}_x16_shared_k10`, 126,080
events each, identical across every swept B -- verified as exact integer
equality in Part 1). Gates: **G0** (new, 0.3) POWER. **G1** (direct call,
`f2().run_gate_g1`) -- kappa<=0 free cell reproduces M4-F1's persisted
`base1x`. **G2** (new target objects, 0.2) -- construction + anchor, both
to <=1e-12. **G3** (direct call, `f3().run_gate_g3()`) -- gauge/map/halving
invariance. **G4** (identical mechanism to M4-F5/M4-F6) -- truth-path
invariance across all 6 computed cells. **G5** (0.7) -- decorrelation,
3 cells. `M_COMMON=8` and `GAP=40` are reused constants, never tuned.

---

*(Everything below this line was written after the run. Part 0 above -- and
the script that implements it -- was not edited after compute began.)*

## Part 1 -- OUTCOME

### G0 POWER -- reported first, as mandated

**ADEQUATELY POWERED.** Target level, read verbatim from M4-F5's own
persisted `authors_x16_shared_k10` row: long-window truth recovery
**0.132169 +/- 0.008453** (matches the registration's cited "authors x16,
kappa=1.0: long-window recovery .1322 +/- .0085" exactly). This leg's own
realized paired-by-world `b8_x16 - b1_x16` difference on
`truth_recovery_long`: mean **-0.084972**, SD 0.057909, SE 0.020474 (n=8,
df=7), t=-4.150, 95% CI **[-0.133386, -0.036559]**. **Minimum detectable
paired difference (95% CI half-width): 0.048413** -- well inside the
registered `.066` bar (73.4% of it), not a close call. **G0 PASSES.**

### Gates (all six green)

- **G0** (above): PASS, half-width 0.0484 <= 0.066.
- **G1** (kappa<=0 free cell reproduces M4-F1's persisted `base1x`; direct
  call to `f2().run_gate_g1`): abs diffs ~1e-16 range across
  `agreement_mean`/`agreement_se`, 0.0 on `d0_eff_rank_M_mean`, `n_retained`
  exact -- identical machinery to every prior leg's own G1. **PASS.**
- **G2(a) CONSTRUCTION**: the `construction_check_mult1_b1_k10` cell
  (computed through this leg's generalized, `author_mult`-parametrized
  orchestration) vs. M4-F6's persisted `b1_shared_k10`: max abs diff across
  `agreement_mean`, `agreement_se`, `truth_recovery_exact_mean`,
  `truth_recovery_long_mean`, `d0_eff_rank_M_mean`, `d0_eff_rank_K_mean` is
  **7.63e-17**; `n_retained` exact (565=565). **PASS.**
- **G2(b) ANCHOR**: the RAW `authors_x16_shared_k10` cell (a direct,
  unchanged call to `f5().run_truth_sweep_world`) vs. M4-F5's persisted
  `authors_x16_shared_k10`: max abs diff **5.55e-17**; `n_retained` exact
  (9040=9040). **PASS.** (Both G2 sub-checks pass at floating-point noise
  levels, five orders of magnitude inside the registered 1e-12 bar.)
- **G3** (gauge invariance; direct call to `f3().run_gate_g3()`): batched
  feature map vs. deployed `v8.build_feature_panel` bit-identical
  (`max_abs_diff_M`/`max_abs_diff_K` = 0.0); halving vs.
  `e1().split_half_frames` identical (120/120 checked, 0 mismatches).
  **PASS.**
- **G4** (truth-path invariance, identical mechanism to M4-F5/M4-F6): max
  diff across all 6 computed cells (construction-check + anchor + 4
  adjudicated) is **exactly 0.0** on every single cell -- matching M4-F5's
  and M4-F6's own "exactly 0.0" achievement in full, at 16x the author
  count. **PASS.**
- **G5** (decorrelation, F6's own rule reused verbatim): all 3 tested
  `block_count>=2` cells (kappa=1.0 only) have `|t|<2.0`. Full table:

| block_count | correlation_mean | correlation_se | t_stat | n_pairs/world | pass |
|---|---|---|---|---|---|
| 2 | +0.000860 | 0.000460 | +1.871 | 756,480 | yes (closest) |
| 4 | -0.0000469 | 0.000192 | -0.244 | 2,269,440 | yes |
| 8 | -0.0000651 | 0.000175 | -0.373 | 5,295,360 | yes |

  **PASS.** Closest call is `b2_x16_shared_k10` at t=+1.871 (comfortably
  under 2.0, disclosed exactly per this line's own convention -- compare
  F6's own closest call, `b4_shared_k05` at t=-1.976, an even tighter
  margin). Pooled grand mean across the 3 cells: +0.000249 (supplementary
  context only, not the gating statistic, per F6's own Part 0.7 rule).
  Correlation magnitudes are 3-4 orders of magnitude below the smallest SE
  measured anywhere in this leg, and `n_pairs/world` is 16-126x larger than
  M4-F6's own corresponding cells (985 authors -> 15,760), giving this
  leg's own G5 an intrinsically tighter statistical test than F6's.

All six gates green: `gates.json` -> `{"G0": true, "G1": true, "G2": true,
"G3": true, "G4": true, "G5": true}`.

## Budget conservation (diagnostic, verified exactly)

Every one of the 4 adjudicated `b{1,2,4,8}_x16_shared_k10` cells allocates
**exactly 126,080 events** (`15,760 authors x M_COMMON=8`) -- identical
across every swept B, verified as exact integer equality from the persisted
`n_events_total` column. The RAW gate-anchor allocates 211,232 events
(`15,760 x` the panel's own raw per-author range, matching M4-F5's own
`authors_x16_shared_k10` total exactly); the construction-check allocates
7,880 events (`985 x 8`, matching M4-F6's own `b1_shared_k10` total
exactly).

## The full B-vs-metrics table (kappa=1.0 only)

| B | agreement | agreement SE | truth A (same-occasion, exact) | truth A SE | truth B (long-window) | truth B SE |
|---|---|---|---|---|---|---|
| 1 | 0.447114 | 0.017333 | 0.410250 | 0.011111 | **0.141480** | 0.011484 |
| 2 | 0.452479 | 0.013543 | 0.419243 | 0.007776 | **0.148860** | 0.016876 |
| 4 | 0.439351 | 0.019159 | 0.398986 | 0.010321 | **0.160104** | 0.010170 |
| 8 | 0.426154 | 0.018389 | 0.406428 | 0.008755 | **0.056507** | 0.016094 |

Context rows (not adjudicated, reported for completeness): RAW gate-anchor
`authors_x16_shared_k10` -- agreement 0.229053, truth A 0.500941, truth B
0.132169. Construction-check `construction_check_mult1_b1_k10` (mult=1) --
agreement 0.035248, truth A 0.114013, truth B 0.049185.

The pattern is directly visible: agreement and truth A are both essentially
flat across the whole B sweep (agreement 0.4262-0.4525, truth A
0.3990-0.4192). Truth B (long-window) is **non-monotonic** across
B in {1,2,4}: it actually RISES from B=1 (0.1415) to B=2 (0.1489) to B=4
(0.1601), then **drops sharply** at B=8 (0.0565) -- a decline of roughly
65% relative to B=4 and 60% relative to B=1. The registered lean/pivot
machinery is a B8-vs-B1 comparison, not a monotonicity test, so this
non-monotonicity does not affect the adjudication below, but it is reported
plainly rather than smoothed into "truth B declines with B," which the raw
numbers do not uniformly show.

**Per-world detail (kappa=1.0, `truth_recovery_long`, paired by world
index):**

| world | B=1 | B=8 | B8-B1 |
|---|---|---|---|
| 0 | 0.133213 | 0.079350 | -0.053863 |
| 1 | 0.142965 | 0.039379 | -0.103587 |
| 2 | 0.149888 | 0.082076 | -0.067812 |
| 3 | 0.139227 | 0.121849 | -0.017378 |
| 4 | 0.153840 | 0.024834 | -0.129005 |
| 5 | 0.199842 | 0.057425 | -0.142417 |
| 6 | 0.131166 | -0.029310 | -0.160476 |
| 7 | 0.081696 | 0.076454 | -0.005242 |

**All 8 of 8 world-index pairs are negative** -- not merely a negative
mean driven by a few outliers.

## Lean adjudication

- **Lean (a) MISS.** Paired-by-world (`b8_x16 - b1_x16`, truth recovery
  long, kappa=1.0): mean **-0.084972**, SE 0.020474, t=-4.150, 95% CI
  **[-0.133386, -0.036559]** -- excludes zero, but on the NEGATIVE side (a
  significant DECLINE), not the registered positive-rise side lean (a)
  requires. `ci_excludes_zero_positive=false`.
- **Lean (b) INAPPLICABLE**, per the registered rule fixed in Part 0.6
  before this run: `ci_long["mean"]=-0.084972 <= 0`, so the long-window
  "gain" is not positive and the half-gain comparison is not scored. For
  context only: paired-by-world (`b8_x16 - b1_x16`, truth recovery exact,
  kappa=1.0) mean -0.003822, SE 0.016479, 95% CI [-0.042788, +0.035143] --
  includes zero, a much smaller and non-significant movement than truth B's
  own decline (truth A moved by 4.5% of truth B's magnitude), consistent
  with same-occasion recovery being far more stable under spreading than
  the long-window target is.
- **Lean (c) HOLD** under Reading 1 (adopted): agreement at B in
  {1,2,4,8}: 0.447114 / 0.452479 / 0.439351 / 0.426154. B=1 reference
  0.447114; +/-20% band = +/-0.089423 (range [0.357691, 0.536537]). Every
  value falls inside the band (largest deviation: B=8,
  `|0.426154-0.447114|=0.020960`, 23.4% of the band). **Reading 2**
  (stricter): max-to-min = `0.452479-0.426154=0.026325`; compared to
  `0.20*0.447114=0.089423` -- `0.026325<=0.089423` is **also TRUE**, and by
  a much wider margin than M4-F6's own Reading-2 call (F6 consumed 95.9% of
  its tolerance at B=4; this leg consumes only 29.4%). **Lean (c) HOLDs
  cleanly under both readings, more comfortably than M4-F6's own B=1 call.**

## Pivot adjudication

**PIVOT FIRES.** Registered rule: "adequately powered (G0 PASS) AND
long-window truth recovery does not rise with B (paired CI includes 0)."
G0 PASSES (above). Lean (a)'s own CI, `[-0.133386, -0.036559]`, does not
exclude zero on the positive side -- the `NOT ci_excludes_zero_positive`
disjunct of the pivot condition is satisfied (as is, redundantly,
`ci_includes_zero=false` being false is irrelevant since the OR's other arm
already fires; this is the same logically-overlapping construction F6's own
code used, reused verbatim). **Per the registration's own pre-committed
consequence: the closure is EARNED.** Trait-level relation structure is not
certifiable on ANY of the three panel axes tested across this M4-F line
(authors: M4-F4's own law was subsequently shown by M4-F5 to certify only an
occasion-bound object; events: M4-F1/M4-F3 showed scale/composition-rate
both fail; occasions: M4-F6's own null, now confirmed at a properly-powered
scale by this leg, with the properly-powered result landing as a
*significant decline*, not merely a non-significant null). **The D3
program's claims are permanently restricted to occasion-bound objects, and
the M4-E2 objective redesign (`OFFSET_SPREAD_NO_SINGLE_OBJECTIVE_TERM`) is
the only remaining route, with the panel side closed on all three axes.**
This closure is stronger than M4-F6's own suspended attempt at it: F6's own
paired CI, `[-0.069876, +0.019153]`, straddled zero at a scale where the
target itself was barely distinguishable from its own noise floor; this
leg's CI, `[-0.133386, -0.036559]`, sits entirely below zero at a scale
where the target is measured at 15.6 SEs above zero (M4-F5's own
`0.132169/0.008453`).

## Interpretation: a mechanistic reading extending M4-F6's own (a reading, not a registered claim, clearly separated from the adjudication above)

M4-F6's own report identified that at **kappa=1.0 exactly**, the shared
blend formula `blended_x = sqrt(1-kappa)*x_at_labels + sqrt(kappa)*shock_x`
reduces algebraically to `blended_x = shock_x` -- the author-private AR(1)
state contributes NOTHING to the observed panel or to either truth variant
at this kappa. This is a property of the generator's own algebra, not of
scale, so it applies to this leg identically: **at kappa=1.0, the
occasion-spread manipulation has zero causal channel to any of this leg's
adjudicated quantities here too.** `shock_vector` draws are i.i.d. across
`(context, occasion)` pairs regardless of the specific occasion-label
VALUE used, and `block_occasion_labels` gives every author in a context the
identical set of labels at every swept B -- so the cross-author SHARING
STRUCTURE (which authors receive which shared vector) is unchanged between
B=1 and B=8; only the specific realized vectors differ, because each
`(block_count)` cell draws from its own independent `seed_key` (F6's own
Part 0.9 convention). Under this reading, the four adjudicated cells are,
in population, statistically exchangeable draws under kappa=1.0 -- and the
large, consistently-signed, 8-of-8 decline observed here is best read as
an unusually large instance of ordinary between-independent-draw sampling
variability (the kind of variability F6 itself could only speculate about
at a scale where it was statistically invisible), not as mechanistic
evidence that spreading occasions itself degrades long-window recovery.

This reading does **not** soften or contest the adjudication above --
the registered pivot rule is a property of the REALIZED paired CI, computed
exactly as specified, and it fires exactly as computed regardless of why.
What it does is scope the closure's ROBUSTNESS claim correctly: this leg,
by the registration's own explicit economization (0.5), tested ONLY the one
kappa where spreading is algebraically guaranteed to be inert. The claim
that the closure also holds where spreading COULD mechanically matter rests
entirely on M4-F6's own separately-registered, already-adjudicated kappa=0.5
finding (paired diff -0.009117, SE 0.006918, 95% CI [-0.025475, +0.007241],
same sign, same qualitative null) -- not on any new evidence this leg
produced. F6's own report drew the identical conclusion from the identical
structure: "even on the one kappa where spreading mechanically CAN matter,
no positive long-window effect appears in this data." This leg adds a
properly-powered kappa=1.0 result to that picture; it does not re-test
kappa=0.5 at x16 (the registration explicitly declined that expense), so the
"robust across the causally-live kappa" component of the full argument is
inherited from F6, not independently reconfirmed here.

## Honest anomalies and disclosures

1. **The three-tier B=1 resolution (Part 0.2)** adds a genuinely new,
   gate-only construction-check cell beyond M4-F6's own two-tier RAW/COMMON
   split -- disclosed as a leg-specific addition required by this
   registration's own "reproduces M4-F6's own construction at the same
   author scale" instruction, which M4-F6's own registration never needed
   to satisfy (there was no prior leg for F6 to reproduce at a matching
   scale).
2. **Truth B is non-monotonic across B in {1,2,4,8}** (rises to a peak at
   B=4, then drops sharply at B=8) -- reported exactly as measured, not
   smoothed into a monotone-decline narrative the raw numbers do not
   support. The registered pivot is a B8-vs-B1 comparison and is unaffected
   by this, but a reader should not infer a smooth dose-response from this
   leg's own data.
3. **All 8 of 8 world-index pairs show a negative B8-B1 diff** on truth B --
   a notably consistent direction for what the mechanistic reading (above)
   argues is, at this kappa, sampling variability rather than a caused
   effect. This tension (a large, consistent, significant difference
   between cells the generator's own algebra says should be
   distributionally exchangeable) is disclosed plainly rather than
   resolved; the registered adjudication does not depend on resolving it.
4. **G0's "does not raise/void the run" design choice (Part 0.8)** departs
   from G5's own established "VOID on failure" discipline -- a genuine,
   disclosed departure from precedent, made necessary by the registration's
   own text ("adjudicate NOTHING" implies a report must still exist) and
   fixed in the script before compute. It was not exercised in this run
   (G0 passed), so it remains an untested code path; disclosed as such.
5. **G5's closest call moved from F6's own b4/k05 (t=-1.976) to this leg's
   b2 (t=+1.871)** -- both comfortably under the |t|<2.0 bar, and this
   leg's own margin is slightly larger despite (or perhaps aided by) a much
   larger `n_pairs_per_world` (756,480 vs. F6's comparable cells' tens of
   thousands), consistent with G5 becoming, if anything, a MORE sensitive
   test at this scale, not a weaker one.
6. **Total main-pipeline compute was approximately 15 minutes** (anchor
   205s single batch of 8 worlds; construction-check 9s; sweep 294s
   (`--block-counts 1,2`) + 290s (`--block-counts 4,8`) in two foreground
   chunks; gates ~64s; finalize ~21s; `--workers 8` throughout, run
   entirely in the foreground with no backgrounded compute), a single-world
   timing pilot (56.6s for `b1_x16` world 0, 59.6s for `b8_x16` world 0, run
   in-process before the full sweep was launched) having already indicated
   this scale was computationally tractable to drive interactively. This is
   roughly 7-8x M4-F6's own <2-minute total, consistent with a 16x author
   multiple at sub-linear per-author cost (the same sub-linear pattern
   M4-F5 itself measured going from its own base1x to authors x16, ~10x
   time for 16x authors).

## Decision boundary

Exploratory, synthetic-calibrated, label-free. This leg re-tested the
occasion-spread axis at the one scale (authors x16) where M4-F5 established
the long-window target is measurably non-zero, closing the power gap the
M4-F6 planner note identified as that leg's own registration defect. G0
confirms the design is adequately powered (minimum detectable paired
difference 0.048, well inside the registered 0.066 bar), and the
properly-powered result is not an ambiguous null but a **statistically
significant decline** in long-window truth recovery from B=1 to B=8. Per
the registration's own pre-committed consequence, **the closure is EARNED**:
trait-level relation structure is not certifiable on any of the three panel
axes (authors, events, occasions) tested across this M4-F line under this
synthetic instrument; the D3 program's claims are permanently restricted to
occasion-bound objects; and the M4-E2 objective redesign
(`OFFSET_SPREAD_NO_SINGLE_OBJECTIVE_TERM`) is the only remaining route, with
the panel side closed on all three axes. This licenses a finding about panel
DESIGN under this calibrated synthetic instrument only -- it makes no claim
about the real relation field's actual content, personality, emotion,
diagnosis, or any individual. Artifacts:
`results/m4_f7_occasion_axis_powered/{decision.json, gates.json, cells.csv,
cell_*.csv, draws_*.csv}`.
