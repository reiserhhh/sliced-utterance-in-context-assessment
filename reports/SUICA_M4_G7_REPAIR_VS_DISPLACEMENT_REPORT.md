# SUICA M4-G7 — Does the Certified Repair Reach the Displacement, or Is It Orthogonal to It?

Tier: **EXPLORATORY** (open-exploration phase, operator directive 2026-08-01).
Registered before run: `docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md`, "M4-G7
registration" (2026-08-03, BEFORE run, commit `e2ee102`); ledger row M4-G7.
Script: `scripts/run_suica_m4_g7_repair_vs_displacement.py`. Artifacts:
`results/m4_g7_repair_vs_displacement/`.

## Headline, stated up front, with the same prominence a success would get

**The PIVOT FIRES. Scale-invariance and recovery are ORTHOGONAL to the
displacement.** M4-G6's certified repair (`column_standardized` at
`alpha=0.10 x deployed ridge`) does not reduce Leg 14's frame displacement —
not partially, not within noise, but by **exactly 0.0** at every one of the
24 (world, repetition) pairs and every one of the 3 worlds' GPA-consensus
offsets. Both leans built to detect a reduction, lean (a) on M4-G2's
registered scale-normalized offset (paired-by-world, n=3) and lean (b) on
Leg 14's own `disp_v2` (paired-by-repetition, n=24), return a CI that is not
merely inside the materiality margin but a **degenerate point exactly at
zero** — the strongest, least ambiguous form "no reduction" can take. This is
not a power failure: G0 shows both comparisons are NOT underpowered against
their registered bars (half-width 0.0 in both cases), and G1's five
independent anchors (M4-E2, Leg 14 twice, M4-G6 twice) all reproduce to
machine precision. **Leg 14's displacement gap is closed by exactly 0% of
its own magnitude.** The reason is mechanical, not statistical, and is
proved in Part 0.1 before any number was computed: the repair varies a
ridge penalty applied INSIDE the truth-recovery estimator, strictly
downstream of and structurally disconnected from `context["v2_basis"]`, the
object metrics 1 and 2 are exclusively computed from. Lean (c) HOLDS
cleanly at both budgets (repaired does not worsen recovery — if anything it
is numerically slightly better, mean diff −0.0002/−0.0079 at 4x/8x, both
CIs comfortably inside the ±0.02 margin). **The repair stands, exactly as
M4-G6 certified it, as a real and useful improvement to the discovery
objective's conditioning — scale-free at no cost to recovery — and the
frame displacement M4-D Leg 14 found and M4-E2 decomposed is confirmed here
as a separate, still-open defect that six legs of ridge/whitening-scale
engineering never touched.** The M4-G line closes on a partial win, labeled
exactly as such.

## Part 0 — the structural-identity argument, world/grain choices, and registered-ambiguity resolutions (written before compute)

### 0.1 Why metrics 1 and 2 cannot move between `deployed` and `repaired`

The repair under test, `g5._forced_route_derivative_columnwise` with
`treatment="column_standardized"`, takes a fixed `basis` argument and
returns a derivative estimate computed FROM it (`scripts/
run_suica_m4_g5_per_column_ridge.py:557-602`); nowhere does it construct,
modify, or return a basis. The basis it consumes, `context["v2_basis"]`, is
built once per (world, repetition) by `leg4._build_context`, entirely before
either of this leg's two arms exist as a concept — it is a function of
`(world, repetition, seed, config)` only, and `config`'s `hazard_ridge`
(0.005) never varies between `deployed` and `repaired`; only the ridge value
handed to the EVALUATION-TIME forced-route refit differs. Metric 1
(`offset_norm` / its M4-G2 scale-normalized form) and metric 2 (Leg 14's
`disp_v2 = quotient_distance(swap_rep, v2_rep)`) are both pure functions of
`context["v2_basis"]` and `context["truth"].oracle_basis` alone
(`leg9._row_norm_swap`, `leg11._stack_frame`, `leg14._quotient_distance` /
`_frechet_mean_multistart`) — neither function's signature takes a ridge,
alpha, or treatment argument. **Consequence, stated as a provable prediction
before compute:** metrics 1 and 2 must be identical between `deployed` and
`repaired` to floating-point exactness, at every world and every repetition.
This was verified, not merely assumed: the `structural_identity_check` cell
in `decision.json` recomputes the labeling and confirms `0.0` max absolute
difference at both metrics (`pass_exactly_zero: true`).

### 0.2 Two-arm dispatcher

`deployed` routes through `g3._forced_route_derivative_adaptive` at
`hazard_ridge = deployed_ridge` (the same `baseline` semantics M4-G1/G4/G5/G6
use). `repaired` routes through `g5._forced_route_derivative_columnwise`
with `treatment="column_standardized"`, `ridge_deployed = 0.10 x
deployed_ridge` — M4-G6's headline, hardcoded and registered here, not
re-derived. Both branches share the identical `basis` (`context["v2_basis"]`)
and the identical deployed defaults for `weight_floor`/`clip_bound`/
`tol_mode`/`tol_value`/`probe_epsilon`.

### 0.3 World and grain choices (fifth standing rule: justify, don't inherit)

**Worlds**: `HIGH_GAP_WORLDS` (3: `endogenous_creation_expansion`,
`selection_creation_compensation`, `source_rotated_feedback`) — Leg 14's and
M4-E2's own worlds, per the outer registration's explicit instruction, not
M4-G1..G6's expanded 8-world `D1_WORLDS`. All three are members of
`VALID_TRUTH_WORLDS` (asserted at import time), so metric 3 needs no world
exclusion.

**Grain, per metric, chosen for power against that metric's own bar:**

- **Metric 1** (offset / scale-normalized offset): **world grain, n=3.**
  This is the metric's own native grain, not an inherited default —
  `offset_norm` is a GPA-consensus statistic pooling all 8 repetitions into
  one number per (world, arm); there is no finer sampling unit available
  without changing what the metric measures.
- **Metric 2** (Leg 14's `disp_v2`): **repetition grain, n=24 (3 worlds x 8
  reps), PRIMARY** — chosen because `disp_v2` is already a per-rep quantity
  in Leg 14's own construction; pairing at rep grain uses the metric at its
  finest available resolution and gives 8x the naive world-grain (n=3)
  sample size. World grain (n=3, on `median_disp_v2`) is reported as a
  disclosed companion for comparability with Leg 14's own reporting.
- **Metric 3** (truth-referenced recovery): **author grain (view-mean, n up
  to 384), PRIMARY** — M4-G3's own hand-off, after finding world grain
  underpowered by >4x, explicitly recommended author grain, and G4/G5/G6
  have used it successfully ever since. World grain (n=3) reported as a
  disclosed companion.

### 0.4 Registered-ambiguity resolution: the `deployed` arm's metric-3 anchor

The outer registration states `deployed`'s anchor as "reproduce M4-E2's
persisted values to <=1e-12." M4-E2 persists `offset_norm` per world (metric
1's anchor, used as registered) and, via its own faithfulness gates,
re-confirms Leg 14's rows to <=1e-9 (metric 2's anchor, sourced directly from
Leg 14 per the outer registration's own metric-2 wording). **M4-E2 computes
no budget=4x/8x truth-referenced recovery at all** — its Task 4 diagnostic
operates at the deployed budget (1x) only, reusing Leg 14's persisted
`gap_rows.csv`. There is therefore no M4-E2 artifact metric 3's
`deployed`-arm anchor could literally target. **Reading A (ADOPTED):**
anchor `deployed`'s metric-3 rows to M4-G6's own persisted `baseline` rows
(`c=1.0`) on these 3 worlds — the nearest available persisted
"deployed-baseline, budget=4x/8x" artifact, and the same file this leg's
`repaired`-arm anchor already depends on. **Reading B (disclosed companion,
computed, not primary):** M4-G1's own original persisted `baseline` rows on
the same 3 worlds. Both readings were computed; they agree to **0.0** (both
`max_abs_diff: 0.0` in `gates.json`), so the disagreement this disclosure
anticipated did not materialize.

### Design summary

Two arms (`deployed`, `repaired`) x 3 worlds x 8 repetitions. Three mandatory
metrics: (1) M4-G2's registered scale-normalized offset, world grain; (2)
Leg 14's `disp_v2`, rep grain primary / world grain companion; (3)
truth-referenced recovery at budgets {4.0x, 8.0x}, author grain primary /
world grain companion. Chunked execution: one foreground call per world
(offset/displacement + G3 spot check + truth rows at both budgets + G2
per-column ridge evidence), then one `--assemble` call.

## Part 1 — Outcome

### G0 POWER (reported first, per instruction)

| Metric | Grain | n | Bar (absolute) | Target level cited | Realized half-width | Underpowered vs. bar? |
|---|---|---|---|---|---|---|
| 1: scale-normalized offset | world | 3 | 0.050864 (12.5% of deployed's own 3-world mean, 0.406909) | M4-E2 persisted `offset_norm`: 13.754/11.956/13.288; M4-G2 persisted baseline scale-norm (3-world mean): 0.398426 | **0.0** | No |
| 2: Leg 14 displacement (`disp_v2`) | repetition (primary) | 24 | 1.805893 (10% of deployed's own mean disp, Leg 14's OWN `PIVOT_REDUCTION_BAR`) | Leg 14 persisted `median_disp_v2`: 18.224/16.930/18.613 | **0.0** | No |
| 2 (companion) | world | 3 | 1.792229 | (same) | **0.0** | No |
| 3: truth recovery, 4x | author (primary) | 384 | 0.01 (`G0_FRACTION_BAR`, half the 0.02 adjudication margin) | M4-G6 persisted headline (repaired, pooled 6-world): 0.5083 | 0.015868 | **Yes** |
| 3: truth recovery, 8x | author (primary) | 384 | 0.01 | M4-G6 persisted headline: 0.4946 | 0.016302 | **Yes** |

Metrics 1 and 2's zero half-widths are **not a sampling-precision
achievement** — they are degenerate points because the paired difference is
identically 0.0 at every unit, a direct empirical confirmation of Part
0.1's structural argument, not evidence of an unusually powerful design.
Metric 3's author-grain test is technically underpowered against the
stricter `G0_FRACTION_BAR` (0.01, half of the actual adjudication margin) —
the same relationship G4/G5/G6 report routinely — but this does **not**
compromise lean (c)'s own classification, which uses the registered 0.02
margin directly and is decisively WITHIN it at both budgets (upper CI bounds
0.0156 and 0.0084, both well inside 0.02).

### G2 REPAIR LIVENESS

The repaired arm differs from deployed in the applied regularization on
**both** axes the outer task asks for:

- **Scalar level**: `deployed_ridge = 0.005` (constant across all 24
  contexts, verified), `repaired_scalar = alpha x deployed_ridge = 0.0005`.
  The realized ratio, cross-checked against M4-G6's own persisted G2
  evidence for `colstd_alpha_0.10`, is **0.1** exactly (`abs_diff` vs. the
  registered alpha: 0.0).
- **Per-column shape**: computed fresh on this leg's own 24 representative
  (world, repetition) design matrices via `g5._standardize_design` (the
  SAME degenerate-column-floor logic — `DESIGN_VAR_FLOOR=1e-12`,
  `DEGENERATE_STD_FALLBACK=1.0` — the real `column_standardized` fit already
  applies, so this reports the mechanism's own realized profile, not a
  reconstruction). The per-column ridge profile's own spread (max/min across
  non-intercept design columns) ranges **20.5x to 281.8x** across the 24
  sampled contexts — deployed's own profile is exactly flat (spread == 1.0,
  a single scalar times `n*I`) by construction. Realized ratio of the
  repaired per-column ridge to deployed's flat scalar spans **0.0028x to
  1.79x** across columns and contexts.

**G2 verdict: LIVE** (`shape_live: true`, `scalar_live: true`,
`live: true`). Both the level and the shape of the regularization genuinely
differ — this is the same mechanism M4-G5/G6 certified, applied unchanged.

### G1 ANCHOR

Five independent persisted sources, all reproduced to **<=1e-12** (realized
max: `1.78e-15`, floating-point noise):

| Anchor | Source | Rows/cells checked | Max abs diff |
|---|---|---|---|
| Metric 1, offset_norm (deployed) | M4-E2 `offset_table` | 3 worlds | 0.0 |
| Metric 2, `disp_v2` per rep (deployed) | Leg 14 `displacement_rows.csv` | 24 | 1.78e-15 |
| Metric 2, `median_disp_v2` per world (deployed) | Leg 14 `decision.json` `displacement_table` | 3 worlds | 0.0 |
| Metric 3 (deployed), PRIMARY | M4-G6 persisted `baseline`, c=1.0 | 1,536 rows | 0.0 |
| Metric 3 (deployed), SECONDARY DISCLOSED | M4-G1 persisted `baseline` (independent original source) | 1,536 rows | 0.0 |
| Metric 3 (repaired), PRIMARY | M4-G6 persisted `colstd_alpha_0.10`, c=1.0 | 1,536 rows | 0.0 |
| Internal: `v2_basis` reproduces `g1._whitening_for_arm("baseline")` + `_bases_from_whitening` | (structural, not external) | 24 reps x 3 roles | 0.0 |

**G1 verdict: PASS.**

### G3 TRUTH-PATH INVARIANCE

Degenerate equality check: the truth path's own budget=1.0 short-circuit
reproduces gap-stage-style `e_arm_true` exactly, one spot-check
(repetition, view, author) per world, both arms (6 checks total).
**Max abs diff: 0.0. PASS.**

### G4 MATERIALITY FORM — explicit compliance

- **G0**: CI-half-width-vs-bar equivalence bound, per metric; underpowered
  comparisons flagged explicitly (`underpowered_vs_bar`/
  `underpowered_vs_g0_bar`), never silently read as nulls.
- **G1**: degenerate exact-equality checks (tolerance 1e-12) against five
  independent persisted sources, not significance tests.
- **G2**: dual liveness check — scalar ratio equals the registered alpha to
  <=1e-9, AND per-column profile spread exceeds 1.0 (deployed's own profile
  is exactly flat by construction) — not a binary did-anything-change test.
- **G3**: degenerate exact-equality check (tolerance 1e-12) between two
  independently-computed derivations of the same quantity, both arms.
- **lean (a)**: paired-by-world CI-excludes-zero test (directional
  materiality claim, not nil-significance).
- **lean (b)**: paired-by-repetition CI-excludes-zero test (directional
  materiality claim, not nil-significance); world-grain companion reported
  alongside, not substituted.
- **lean (c)**: one-sided WITHIN/OUTSIDE/AMBIGUOUS classification on paired
  author-level CI against the fixed +/-0.02 (upper-only) margin, both
  budgets, never nil-significance.

## Per-arm x per-world summary — all three metrics

| World | Arm | Offset_norm | Scale-norm offset (metric 1) | Median disp_v2 (metric 2) | Mean e_arm_true 4x (metric 3) | Mean e_arm_true 8x |
|---|---|---|---|---|---|---|
| endogenous_creation_expansion | deployed | 13.754107 | 0.500850 | 18.224166 | (author-level, see below) | |
| endogenous_creation_expansion | repaired | 13.754107 | 0.500850 | 18.224166 | | |
| selection_creation_compensation | deployed | 11.956016 | 0.375241 | 16.929591 | | |
| selection_creation_compensation | repaired | 11.956016 | 0.375241 | 16.929591 | | |
| source_rotated_feedback | deployed | 13.288138 | 0.344636 | 18.613126 | | |
| source_rotated_feedback | repaired | 13.288138 | 0.344636 | 18.613126 | | |

Metrics 1 and 2 are bit-identical between `deployed` and `repaired` **by
row**, not only in aggregate — every one of the 6 (world x arm) offset rows
and all 48 (world x rep x arm) displacement rows shows `abs_diff == 0.0`.

Metric 3, pooled across the 3 worlds (author grain, n=384 per budget/arm):

| Budget | Arm | Mean `e_arm_true` | Median `e_arm_true` |
|---|---|---|---|
| 4x | deployed | 0.5667 | 0.5562 |
| 4x | repaired | 0.5665 | 0.5149 |
| 8x | deployed | 0.5634 | 0.5581 |
| 8x | repaired | 0.5555 | 0.5058 |

(`e_orc_true`, arm-invariant by construction, pools to 0.3095/0.3084 at
4x/8x — an internal consistency check, not an adjudicated quantity.) Means
are statistically tied (see lean (c) below); medians favor `repaired`
sharply, consistent with M4-G6's own disclosed median-based robustness
reading.

## Lean adjudication

### Lean (a) — DISPLACEMENT FALLS: **MISS**

*"The repaired objective's scale-normalized offset is lower than deployed's,
paired-by-world CI excluding zero."*

Per-world reduction (`deployed - repaired`): **0.0, 0.0, 0.0** (all three
worlds). Paired-by-world CI (n=3, df=2): **[0.0, 0.0]**, mean 0.0, half-width
0.0. The CI does not exclude zero — it does not merely fail to exclude zero,
it **is** zero. **MISS**, and not narrowly: there is no reduction to speak
of, at any world, at any magnitude.

### Lean (b) — THE ORIGINAL GAP FALLS: **MISS**

*"Leg 14's displacement gap is lower under the repair, paired CI excluding
zero."*

Rep-grain (primary, n=24): reduction is 0.0 at every one of the 24 (world,
repetition) pairs. Paired CI (df=23): **[0.0, 0.0]**. World-grain companion
(n=3, on `median_disp_v2`): identical result, **[0.0, 0.0]**. **MISS**, at
both grains, unanimously.

**Quantifying how much of Leg 14's gap the repair closes, as instructed:
exactly 0%.** Not "a small, statistically insignificant amount" — the
`disp_v2` value under `repaired` is the SAME FLOATING-POINT NUMBER as under
`deployed`, row for row. Leg 14's own consensus arm (a genuinely different,
GPA-averaging construction) reduced displacement by single-digit percentages
at best and still tripped its own 10% pivot bar in all three worlds
(`results/m4_d_discovery_displacement/decision.json`,
`pivot_if.worlds_below_pivot_bar`); this leg's ridge-based repair does not
move the needle at all, because it was never mechanically connected to the
object being measured.

### Lean (c) — NOT COSMETIC: **HOLD**

*"Truth-referenced recovery does not worsen under either variant (equivalence
form, margin registered in Part 0)."* Margin: **0.02**
(`g4.LEAN_B_MARGIN`, reused unchanged G4->G5->G6->this leg — "the margin
registered in Part 0" per the outer task's own wording, exactly as G6 itself
registered its reuse).

| Budget | Mean diff (repaired − deployed) | CI | Classification |
|---|---|---|---|
| 4x | −0.000243 | [−0.016111, 0.015625] | **WITHIN** |
| 8x | −0.007886 | [−0.024188, 0.008416] | **WITHIN** |

Both budgets classify WITHIN the one-sided equivalence margin (upper CI
bound below +0.02 in both cases) — recovery does **not** worsen; if
anything, the point estimate favors `repaired` at both budgets (negative
mean diff), consistent with M4-G6's own certified finding that `alpha=0.10`
ties or slightly beats deployed-style recovery. World-grain companion
(n=3) is directionally consistent (mean diff −0.0279/−0.0418 at 4x/8x) but,
as expected at n=3, is not itself adjudicated. **HOLD**, cleanly, at both
budgets.

## The PIVOT

**Registered condition**: neither (a) nor (b) shows a reduction with a CI
excluding zero. **Both (a) and (b) missed, unanimously, at every grain
tested. The PIVOT FIRES.**

Per the outer task's own instruction for exactly this branch: **scale-
invariance and recovery are ORTHOGONAL to the displacement.** M4-G6's
`column_standardized`-at-`alpha=0.10` repair remains a **real, certified
improvement to the discovery objective's conditioning** — it makes the
objective exactly c-invariant (M4-G6's own finding, re-anchored here to
0.0) at no cost to truth-referenced recovery (confirmed independently here,
lean (c) HOLD). But it is a repair to a DIFFERENT property of the objective
than the one M4-D Leg 14 found and M4-E2 decomposed. **Leg 14's frame
displacement — distributed across S1/S2/S3, world-specific in direction,
not removable by any single term — is confirmed here as a separate,
still-open defect**, unmoved by six legs of whitening-scale and ridge-based
objective engineering (M4-G1 through M4-G6), because none of that engineering
ever reaches `context["v2_basis"]`, the object the displacement is measured
on.

## Verdict

**`PIVOT_SCALE_INVARIANCE_AND_RECOVERY_ORTHOGONAL_TO_DISPLACEMENT`.**

This is reported with the same prominence a positive result would receive,
per the outer task's explicit instruction, because it is exactly that kind
of result: a clean, well-anchored, mechanically-explained answer to the
question the line was opened to ask. The M4-G line closes on a **partial
win**: the objective's conditioning is repaired and certified
(M4-G5/G6); its systematic frame displacement is not, and is handed off,
named and undiminished, as a defect belonging to the basis-construction
path (`_bases_from_whitening`/`build_m4_discovered_basis`) rather than the
ridge/regularization path this whole line intervened on.

## Honest anomalies and disclosures

**One mechanical problem, found on the first run, fixed before any
hypothesis-relevant number was affected.** The first pass of the G2
per-column ridge-profile diagnostic computed the per-column ridge weight
directly from raw `g5._design_column_stats` variance. Several design
columns are near-degenerate (e.g. `condition_0`, noted in M4-G1's own
docstring), producing raw variances near the floating-point floor; dividing
by them to get a min/max "spread" statistic produced nonsense values near
float overflow (`design_var_spread_max` observed at `1.79e+301` on the
first run). This diagnostic feeds ONLY the G2 REPAIR LIVENESS evidence — it
is never read by any of the three leans or the pivot, so no
hypothesis-relevant number existed at the time the problem was found or
after it was fixed. **Fix**: call `g5._standardize_design(full_design,
var_j)` directly — the exact function `_fit_logistic_columnstd` uses
internally, including its established degenerate-column floor
(`DESIGN_VAR_FLOOR=1e-12`, `DEGENERATE_STD_FALLBACK=1.0`, reused, not
reinvented) — so the reported profile is bit-identical to what the real fit
computes, not a naive reconstruction. All three worlds were then re-run in
full for reproducibility (the fix lives inside the same per-world compute
function); every substantive number (metrics 1, 2, 3, all gates, all leans)
reproduced identically before and after the fix, as expected since the fix
touches only the G2 diagnostic. Post-fix, the per-column spread is a
sensible 20.5x-281.8x.

**No other mechanical problems were encountered.** All five G1 anchors, the
internal basis-identity check, and G3 passed on the first attempt at every
world.

**No post-hoc rescues, no tuning after seeing results, no softening of a
miss.** Leans (a) and (b) MISS as decisively as a result can miss (an exact
zero, not a near-zero); this is reported as the headline, not buried. The
outcome lands squarely inside the PIVOT-IF branch the registration wrote
before this leg ran; nothing here required stepping outside the registered
branches.

## Faithfulness chain (all green)

`v2_basis` (deployed) == `g1._whitening_for_arm("baseline")` +
`leg10._bases_from_whitening` (0.0, 24 reps x 3 roles) == M4-G1's own
`baseline` construction (by the same identity, inherited) -> `offset_norm`
(deployed) == M4-E2 persisted (0.0, 3 worlds) -> `disp_v2` (deployed) ==
Leg 14 persisted, both per-rep and world-median (1.78e-15 / 0.0) ->
`e_arm_true` (deployed) == M4-G6 persisted `baseline` == M4-G1 persisted
`baseline` (0.0, 1,536 rows each) -> `e_arm_true` (repaired) == M4-G6
persisted `colstd_alpha_0.10` (0.0, 1,536 rows) -> G3 truth-path
short-circuit == gap-stage-style computation (0.0, 6 checks, both arms) ->
structural-identity relabeling (metrics 1/2, deployed vs. repaired) == 0.0
by direct recomputation, confirming Part 0.1's a priori argument rather
than merely asserting it.

## Boundaries

Finite synthetic M4-C.2 worlds only (the 3 `HIGH_GAP_WORLDS`, reused
verbatim from M4-E2/Leg 14/M4-G1); truth-recovery via budget-regenerated
(4x/8x events) finite panels from the frozen world law, compared to the
analytic `D_true`; no natural-text, personality, or clinical claim; no seal,
no independent verification (operator directive 2026-08-01). The
"orthogonal" finding is scoped to the ONE repair mechanism this line
certified (`column_standardized` ridge reparameterization) and the ONE
displacement object Leg 14/M4-E2 defined (`quotient_distance` between the
row-norm swap and the discovered v2 frame); it is not a claim that no
possible objective repair could ever move the displacement, only that this
line's entire ridge/whitening-scale engineering effort — six legs of it —
structurally could not, because of where in the discovery pipeline the
displacement lives versus where this line's every intervention landed.
