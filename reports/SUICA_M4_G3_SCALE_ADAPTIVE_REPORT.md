# SUICA M4-G3 — Scale-Adaptive Constants: Can M4-G2's Units Artifact Be Turned Into a Repair?

Tier: **EXPLORATORY** (open-exploration phase, operator directive 2026-08-01).
Registered before run: `docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md`, "M4-G3
registration" (2026-08-03, BEFORE run), plus the "M4-G2 planner adjudication
note" that raised the question this leg answers; ledger row M4-G3. Script:
`scripts/run_suica_m4_g3_scale_adaptive.py`. Artifacts:
`results/m4_g3_scale_adaptive/`. Machinery imported and reused unchanged from
M4-G1/M4-G2 (`g1`/`g2` in the script): world set (`g2.D1_WORLDS`), valid-6-
world truth-recovery subset (M4-G2's own lean (b) adopted rule, reused
verbatim), context builder, c-ladder whitening construction
(`g2._whitening_for_c`), CI helpers (`g1._paired_world_ci`,
`g1._paired_author_ci`), aggregation helpers (`g1._author_level_truth`) — and,
transitively, Leg 3/4/9/10/11/14's own machinery. No estimator internals are
copied without disclosure; every new function is a PARAMETERIZED
near-duplicate of an unchanged original, cited by file and line at its
definition.

## Headline, stated up front

**This outcome lands outside every registered branch, and is reported as such.** Of six inventoried constants, one — `hazard_ridge` — is real, large, and dominant: its own author-level companion (n≈745, the same well-powered grain lean (b) uses) recovers 69–72% of the c=4 gain with a paired CI decisively excluding zero ([0.0399, 0.0628] @4x, [0.0488, 0.0727] @8x), and the ridge value it computes (0.00023–0.00089 across all 64 contexts, always 4.6–18% of the deployed 0.005) is consistent and never crosses zero or flips sign. The other five constants (`tolerance`, `weight_floor`, `clip_bound`, `probe_epsilon`, `intercept`) are cleanly INERT or, for `intercept`, a small real *worsening* — matching the Part 0 a priori ranking derived before any compute ran. **But the leg's own registered test at its own registered grain (paired-by-world, n=6) is severely underpowered — not a subtle effect, a >4x gap between the realized half-width and the pre-stated bar, disclosed in G0 from M4-G2's persisted numbers *before* any adaptive arm was computed** — so lean (a) cannot be scored HOLD or a clean MISS for `hazard_ridge`/`adaptive_all` at the registered grain, and the PIVOT itself is **UNDERPOWERED**, not "fires" and not "does not fire." Separately, and decisively (well-powered, n=745, all three pairwise c-comparisons, both budgets, every CI outside the ±0.02 margin): **lean (b) MISSES.** The adaptive-ridge formula does not deliver invariant recovery across the c-ladder — it produces an inverted-U, worse at c=0.25, best at c=1 (its own calibration point), slightly worse again at c=4. **Verdict: `hazard_ridge` is confirmed as the (or the dominant) localized channel of M4-G2's scale dependence, but no tested formula here is certified as a genuine, general repair — this specific adaptive form is a partial, context-calibrated fix, not the reparameterization-invariant one lean (b) was built to certify.**

## Part 0 — registered constant inventory (written into the script BEFORE compute; transcribed here)

Every function reachable from an arm's basis was enumerated by walking the
exact call graph M4-G1/M4-G2 use for a c-arm's basis:

```
g2._whitening_for_c -> leg10._bases_from_whitening -> {
    OFFSET path:  leg9._row_norm_swap -> leg11._stack_frame ->
                   leg14._frechet_mean_multistart/_gpa_mean/_quotient_distance
    TRUTH path:   leg4._forced_route_derivative ->
                   estimator._fit_hazard_candidate -> estimator._hazard_design /
                   estimator._fit_logistic -> estimator._feedback_derivative ->
                   estimator._hazard_probability -> estimator._hazard_design
}
```
plus `leg3._relative_error` on both paths (compares the arm's output to the
world's fixed analytic `D_true`, itself never touched by c or by any arm).

### Category A — constants on the TRUTH-RECOVERY call graph (scored; each gets its own `adaptive_<k>` arm)

| # | constant | file : line | deployed value | role |
|---|---|---|---|---|
| A1 | `hazard_ridge` | `suica_core/m4_chart_ecology_estimator.py:341-342` | 0.005 (`configs/m4_chart_ecology.json` → `route_estimator.hazard_ridge`) | regularizer, `penalty = ridge*n*I` added to the IRLS Gram matrix |
| A2 | IRLS convergence tolerance | `suica_core/m4_chart_ecology_estimator.py:357` | `1e-10` (absolute) | convergence tolerance on `‖updated − coefficient‖` |
| A3 | IRLS weight floor | `suica_core/m4_chart_ecology_estimator.py:348` | `1e-4` | floor on `fitted·(1−fitted)` |
| A4 | logit clip bound | `suica_core/m4_chart_ecology_estimator.py:347,438` | `±20.0` | clip on `design @ coefficient` before `expit` (two call sites, one constant) |
| A5 | finite-difference probe epsilon | `suica_core/m4_chart_ecology_estimator.py:531`, consumed via `scripts/run_suica_m4_d_dleg_floor_leg4.py:441-447` | `0.05` | step size for the arm's estimated derivative (`_feedback_derivative`'s own default; `_forced_route_derivative` never overrides it) |
| A6 | basis intercept constant | `scripts/run_suica_m4_d_direction_anatomy_leg10.py:356` | `1.0` | literal `1` column-stacked beside the whitened (c-scaled) basis columns |

**A1 is the strongest a priori candidate, on a provable basis, not merely a
suspicion.** For a DIAGONAL rescaling of covariates — exactly what c does to
the design (M4-G2's own G2: eigenvectors, relative spectrum, condition
number, width all invariant at 0.0) — unregularized weighted least squares
is EXACTLY invariant (the coefficient compensates 1:1: `X' = X·diag(t)` ⟹
`coefficient' = diag(t)⁻¹·coefficient` reproduces identical fitted values).
An L2 penalty of the form `ridge·n·I` is **not** invariant under this
substitution, because the penalty term becomes `0.5·ridge·n·Σ(coefficient_j/t_j)²`
— unequal across differently-scaled coefficient blocks — which is the
textbook reason ridge/lasso implementations standardize features first. A4
(clip) and A3 (floor) are, by the same argument, only SECOND-ORDER effects
in the idealized ridge=0 limit (the fitted logit and probabilities would be
exactly c-invariant, so nothing would bind differently); A2 (tolerance) acts
on the coefficient scale directly, which A1's own mechanism already shows is
not c-invariant; A5 (epsilon) is a probe on a structurally different axis
(response, not condition) with only an indirect multiplicative channel
(disclosed in full in the script docstring). A6 is disclosed with a
**pre-registered doubt on record**: unregularized IRLS is invariant to ANY
diagonal rescaling, including one that leaves a single column fixed — so
A6's causal channel to truth recovery is expected, on that argument, to be
weaker than A1's; it is tested, not asserted inert, because the argument's
premise (ridge=0) does not hold here.

### Category B — constants on the OFFSET/GPA call graph ONLY (inventoried, provably excluded from the scored hypothesis space)

| # | constant | file : line | why excluded |
|---|---|---|---|
| B1 | `GPA_TOLERANCE = 1e-11` | `scripts/run_suica_m4_d_displacement_leg14.py:204`, used in `_gpa_mean` (~line 335) | `_run_truth_stage`/`_truth_rows_for_context` never call `_frechet_mean_multistart`/`_gpa_mean`/`_quotient_distance`/`leg9._row_norm_swap`/`leg11._stack_frame` at all — zero causal channel to truth recovery is a call-graph FACT, stronger than an empirical G2 check could supply |
| B2 | `BASIN_RESOLUTION = 1e-6` | `scripts/run_suica_m4_d_displacement_leg14.py:206`, used in `_frechet_mean_multistart` (~line 375) | same exclusion as B1; additionally does not even affect the adopted GPA mean/offset, only the disclosed basin-count diagnostic |

No adaptive arm is built for B1/B2: an arm testing them would necessarily
reproduce baseline's truth-recovery rows bit-for-bit, since nothing on the
truth-recovery path would change — spending compute to empirically confirm
a call-graph certainty would itself be the "vacuous null on an inert knob"
the standing rules warn against, just arrived at more expensively.

### Considered and excluded (not scale-carrying w.r.t. c, or not a magnitude-bearing comparator, or outside the reused call graph)

- `rank_tolerance=1e-6`, `maximum_rank=12` (`leg10._freeze_ingredients`,
  ~lines 300-304): determine `retained` from the RAW covariance
  eigenvalues, upstream of c entirely.
- `1e-12` floor inside `leg10._whitening_with_lambda` (line 334): protects
  the RAW eigenvalues (`lam=0` always on this leg's arms), upstream of c.
- `1e-12` floor(s) inside `leg9._row_norm_swap` (line 1106): protects the
  ORACLE basis's row norm (c-invariant), not the arm's own; also
  offset-path-only.
- `logistic_iterations=30` (config): an iteration COUNT, not itself a
  comparator against a scale-carrying quantity.
- `penalty[0, 0] = 0.0` (estimator.py:342): a structural exemption, not a
  magnitude with a "relative" form.
- Laplace-smoothing constants `0.5`, `1.0` in `_fit_logistic`'s intercept
  init (estimator.py:344): operate on the binary target `y`, never touched
  by c or by any arm.
- `np.tanh(duration/4.0)`'s `4.0`, and the `history[:,0] > 0.0` gate
  threshold (estimator.py:307, 318): operate on RAW world data.
- `GPA_MAX_ITERATIONS = 50000` (leg14.py:205): an iteration cap, not a
  comparator; also offset-path-only.
- `EXPONENT_ANCHOR_TOLERANCE = 5e-4` (leg14.py:207): belongs to a different
  leg-14 function, never imported or called by g1.py/g2.py's reused call
  graph.

### Analytical aside and the declared data-scale statistic (registered before compute)

Empirical check on one sample context (world=`endogenous_creation_expansion`,
rep=0, k_retained=12): raw retained eigenvalues range 2.6e-6 to 0.295,
mean = 0.0486, geometric-mean SCALE FACTOR (`1/sqrt(eig)`, M4-G2's own
`geometric_mean_scale` statistic) = 28.43 — but the WHITENED design columns
this scale factor produces have empirical variance ≈0.79–2.48 per column
(overall ≈0.84–1.48 across the three roles), i.e. close to the UNIT variance
whitening is mathematically defined to produce (`variance = eigenvalue ·
(1/√eigenvalue)² = 1`, exactly, up to finite-sample/out-of-distribution
noise). **The whitening's own scale factor is the reciprocal normalization
that PRODUCES unit magnitude — it is not a measure of the resulting
feature's magnitude, and is the wrong denominator for "how far the deployed
constants' implicit unit-variance assumption is from true."** The RAW,
PRE-WHITENING eigenvalue scale is the right one. This is not a new idea in
this codebase: `leg10._freeze_ingredients`'s own Arm A (Leg 10's "de-biased
discovery" Tikhonov lever, `scripts/run_suica_m4_d_direction_anatomy_leg10.py:309-311`)
already computes `lambda_chart = trace(covariance)/p_features/n_reference_rows`,
a closely related raw-covariance-scale statistic, as the reference for a
DIFFERENT regularizer in this exact pipeline — precedent, not invention.

**Declared data-scale statistic** (used by every Category A arm):
```
RAW_SCALE(context) := mean(ingredients["eigenvalues"][ingredients["retained"]])
```
computed once per (world, repetition) from the unchanged
`leg10._freeze_ingredients` output — identical regardless of c, and
identical regardless of which Category A constant is being adapted.

**Adopted adaptive formulas** (each holds every OTHER Category A constant,
and c, at its deployed/baseline value):

| constant | adaptive formula | direction at RAW_SCALE≈0.05–0.13 (this leg's observed range) |
|---|---|---|
| A1 ridge | `ridge_deployed · RAW_SCALE` | weakens (RAW_SCALE < 1) |
| A2 tolerance | switch absolute → relative: `‖Δcoef‖∞ < 1e-10·max(1,‖coef‖∞)` | self-normalizing, no RAW_SCALE needed |
| A3 weight floor | `1e-4 · RAW_SCALE` | shrinks |
| A4 clip bound | `20.0 / RAW_SCALE` | grows |
| A5 probe epsilon | `0.05 · RAW_SCALE` | shrinks |
| A6 intercept | `1.0 / sqrt(RAW_SCALE)` | grows |

`adaptive_all` applies all six simultaneously. Every arm otherwise stays at
`c=1.0` — the manipulation is entirely in the constants, never in the
whitening scale itself.

**Pre-registered plausibility check** (computed from a toy one-coefficient
ridge model and M4-G2's own persisted c=4 anchor, BEFORE any adaptive-arm
compute; not tuned to it): reproducing c=4's effective ridge-to-information
ratio EXACTLY at c=1 requires `ridge_deployed/4² = 0.0003125`
(`ridge_effective(c) = ridge_used(c)/c²` for a diagonal rescaling by c, so
matching c=4's naturally-weaker effective ridge at c=1 means setting
`ridge_used(1) = ridge_deployed/16`). A1's formula, evaluated on the sampled
context above, gives `0.005·0.0486 ≈ 0.000243` — same order of magnitude as
0.0003125, computed from RAW_SCALE alone (the formula never references "4"
or "c=4" anywhere).

### Design (registered)

Reuse M4-G2's 8 worlds and objective path verbatim. Arms: `baseline` (c=1,
all six deployed — anchor), `c4_reference` (c=4, all six deployed — anchor,
must reproduce M4-G2's persisted c=4 recovery ≤1e-12), `adaptive_<A1..A6>`
(one arm per Category A constant, c=1, that constant alone adaptive),
`adaptive_all` (all six adaptive, c=1). 9 arms total, both truth budgets
(4x, 8x). M4-G2's valid-6-world subset is reused verbatim for every
truth-recovery statistic; this leg's own arm-invariant `e_orc_true`
diagnostic (identical construction, deployed constants, never touches any
arm's basis or any Category A constant) is recomputed and cross-checked
against the same threshold to confirm the same two worlds are invalid here
too (a structural certainty, verified not merely assumed — see Part 1).

OFFSET (GPA) is computed for exactly 4 arms: `baseline`, `c4_reference`
(both needed for G1 ANCHOR), `adaptive_intercept`, `adaptive_all` (the only
two arms whose basis — hence whose GPA offset — can possibly differ from
baseline's, since A1–A5 never touch `_bases_from_whitening`; verified
structurally, not merely assumed, by a bit-exact basis comparison for every
A1–A5 arm during the truth stage). The other five single-constant arms'
offset is IDENTICAL to baseline's by construction (zero marginal GPA
compute).

**Lean (c) margin** (registered here, Part 0): offset lives on baseline's
own O(5–15) native scale (M4-G1/M4-G2's own tables), not truth error's
[0,1] scale, so lean (b)'s absolute ±0.02 band would be a units mismatch if
reused for offset. The registered margin is instead ±10% of baseline's own
mean offset, reusing M4-G1's own G2 "10% relative change" materiality
convention (`scripts/run_suica_m4_g1_whitening_intervention.py:253`,
`G2_CONDITION_MATERIALITY_RATIO`) rather than inventing a new number.

**G0 bar**: half of lean (a)'s 50% bar (25% of the c=4 gain), matching this
line's own "half of the actionability threshold" convention (M4-G1: half of
25%; M4-G2: half the slope 0-vs-1 gap).

**Lean (a)/G2-liveness budget-aggregation rule** (registered here,
resolving a genuine ambiguity — the registered text says "per budget" for
lean (a) without restating M4-G1's own "both variants, or MISS" convention
explicitly): both numbers computed under EITHER reading are reported; the
adopted rule requires the criterion to hold at BOTH budgets (4x AND 8x)
before a constant/arm is credited as HOLD/LIVE — the same "both mandatory"
convention every truth-recovery lean in this line (M4-G1's lean (b), M4-G2's
lean (b)) has used, adopted for consistency rather than invented fresh.

## Part 1 — Outcome

*(Everything below this line was computed after the run; Part 0 above was
frozen before compute began.)*

### G0 POWER (reported first, per instruction)

Pre-stated (Part 0, before any adaptive-arm compute) from M4-G2's persisted
`truth_recovery_rows.csv`, and reproduced bit-for-bit here from this leg's
own `baseline`/`c4_reference` rows (G1 anchor, below, confirms these are the
same numbers):

| budget | grain | gain (baseline − c4) | CI | half-width | 25%-of-gain bar | underpowered? |
|---|---|---|---|---|---|---|
| 4x | world-level (n=6, **registered**) | 0.0741 | [−0.0007, 0.1489] | 0.0748 | 0.0185 | **YES** |
| 4x | author-level (n≈745, disclosed) | 0.0591 | half-width 0.0112 | 0.0112 | 0.0148 | NO |
| 8x | world-level (n=6, **registered**) | 0.0840 | [0.0038, 0.1643] | 0.0803 | 0.0210 | **YES** |
| 8x | author-level (n≈745, disclosed) | 0.0683 | half-width 0.0116 | 0.0116 | 0.0171 | NO |

**The registered (world-level, n=6) grain is severely underpowered — not
marginally.** The half-width (≈0.075–0.080) is 4–4.3× the 25%-of-gain bar,
and at budget 4x the CI does not even exclude zero for the raw c=4 gain
itself (the thing this whole leg is trying to recover a fraction of). This
was flagged here, from M4-G2's own persisted numbers, **before any
adaptive-arm compute ran** — not a discovery made after seeing a
disappointing result. The author-level companion (same reduction grain
lean (b) itself already uses) is comfortably powered at both budgets. Per
the standing rule ("a null at the target's noise floor is reported
UNDERPOWERED, never as a null"), every world-level MISS below is
re-examined against this bar before being scored.

### G1 ANCHOR

`baseline` and `c4_reference` reproduce M4-G2's persisted `c_1.0`/`c_4.0`
rows exactly, on identical world seeds:

| check | n compared | max abs diff | tolerance | pass |
|---|---|---|---|---|
| truth recovery (`e_arm_true`), both arms, both budgets, all 8 worlds × 8 reps × 2 views × 16 authors | 8,192 (4,096 per arm) | **0.0** | 1e-12 | YES |
| offset (`offset_norm`), both arms, all 8 worlds | 16 (8 per arm) | **0.0** | 1e-12 | YES |

**PASS**, exact to the bit.

### G2 CONSTANT LIVENESS

Three-way classification per constant (not a binary live/inert): **LIVE**
(world-level CI entirely outside ±0.02 at both budgets), **INERT** (CI
entirely inside ±0.02 at both budgets — a genuine equivalence-form null),
or **AMBIGUOUS** (CI straddles the margin — neither confirmed, the same
underpowering G0 already flagged). A disclosed author-level companion
(same grain as lean (b)) is computed for every row.

| constant | world-level status | world CI @4x | author CI @4x | author status @4x |
|---|---|---|---|---|
| `hazard_ridge` | **AMBIGUOUS** | [−0.0162, 0.1489] | [0.0399, 0.0628] | LIVE |
| `tolerance` | INERT | [0.0000, 0.0000] | [−0.0000, 0.0000] | INERT |
| `weight_floor` | INERT | [−0.0000, 0.0000] | [−0.0000, 0.0000] | INERT |
| `clip_bound` | INERT | [−0.0000, 0.0000] | [−0.0000, 0.0000] | INERT |
| `probe_epsilon` | INERT | [−0.0005, 0.0002] | [−0.0000, −0.0000] | INERT |
| `intercept` | INERT | [−0.0163, 0.0050] | [−0.0103, −0.0066] | LIVE (small, negative) |

Five of six Category A constants are **cleanly, decisively INERT** at both
grains — `tolerance`, `weight_floor`, `clip_bound`, `probe_epsilon` move
truth recovery by an amount indistinguishable from exactly zero (CIs at or
within 1e-4 of [0,0] in most cases), confirming the a priori ranking in
Part 0 (these were flagged as second-order/weak-channel candidates on
mathematical grounds, before any compute ran). `intercept` is INERT at the
world-level grain but the well-powered author-level companion shows a
small, real, **negative** effect (worsens recovery slightly, opposite the
needed direction — also consistent with the Part 0 prediction that its
channel, if any, was expected to be weak and its direction unclear).
`hazard_ridge` alone cannot be classified LIVE or INERT at the registered
world-level grain (the same underpowering as G0), but its author-level
companion is decisively LIVE — CI entirely positive and well clear of the
margin at both budgets (author CI @8x: [0.0488, 0.0727]).

### G3 TRUTH-PATH INVARIANCE

Gap-stage-style `e_arm_true` (from `context["flat"]`, deployed-and-adapted
parameters threaded through identically) vs. the truth-path's own
budget=1.0 short-circuit, at a searched non-degenerate (rep, view, author)
per world, **all 9 arms × 8 worlds = 72 checks: max abs diff 0.0.** **PASS.**

A companion structural check (not itself a registered gate, but load-bearing
for the offset-stage compute-savings claimed in the Design section):
`adaptive_hazard_ridge`, `adaptive_tolerance`, `adaptive_weight_floor`,
`adaptive_clip_bound`, `adaptive_probe_epsilon`'s bases are bit-identical to
`baseline`'s at every (world, repetition, role) — **max abs diff 0.0** across
all 8 worlds × 8 reps × 3 roles — confirming these five arms' offset is
identical to baseline's by construction, not by assumption.

### G4 MATERIALITY FORM — explicit compliance

- **G0** is a CI-half-width-vs-bar equivalence bound (25% of the gain,
  half of lean (a)'s 50% actionability bar), computed at two grains; the
  world-level (registered) reading is explicitly reported as failing this
  bound (underpowered), not treated as passing by default.
- **G1** is a degenerate exact-equality check (0.0 achieved), not a
  significance test.
- **G2** is now a three-way equivalence classification (LIVE / INERT /
  AMBIGUOUS) rather than a binary pass/fail, precisely so that an
  underpowered world-level read is never silently folded into either LIVE
  or INERT — it is reported AMBIGUOUS and the well-powered author-level
  companion is shown alongside it.
- **Lean (a)**'s status is HOLD / MISS / **UNDERPOWERED**, not a binary —
  an arm whose world-level CI does not exclude zero is only scored MISS if
  its own comparison is adequately powered (half-width ≤ the G0 bar);
  otherwise it is UNDERPOWERED, per the standing rule, and this determines
  the PIVOT's own status symmetrically (FIRES requires every arm to be a
  clean MISS, not merely non-HOLD). **Compliant throughout.**

## Per-arm summary table

Truth error = world-level median (over repetition × author) then mean
across the 6 valid worlds; "recovered" = baseline − arm, "% of c=4 gain" =
recovered / (baseline − c4_reference). Offset = mean raw `offset_norm`
across all 8 D1 worlds (arm's own GPA run, or bit-identical-to-baseline by
construction where noted).

| arm | truth error @4x | % of c=4 gain @4x | truth error @8x | % of c=4 gain @8x | offset (mean, 8 worlds) |
|---|---|---|---|---|---|
| `baseline` | 0.5547 | — | 0.5566 | — | 12.003 |
| `c4_reference` | 0.4805 | 100% | 0.4726 | 100% | 51.922 |
| `adaptive_hazard_ridge` | 0.4883* | 89.5% (world) / 69.2% (author) | 0.4763* | 95.5% (world) / 72.3% (author) | 12.003 (=baseline, by construction) |
| `adaptive_tolerance` | 0.5547 | 0.0% | 0.5566 | −0.0% | 12.003 (=baseline) |
| `adaptive_weight_floor` | 0.5547 | −0.0% | 0.5566 | −0.0% | 12.003 (=baseline) |
| `adaptive_clip_bound` | 0.5547 | 0.0% | 0.5566 | 0.0% | 12.003 (=baseline) |
| `adaptive_probe_epsilon` | 0.5548 | −0.2% | 0.5566 | −0.0% | 12.003 (=baseline) |
| `adaptive_intercept` | 0.5603 | −7.6% | 0.5611 | −5.3% | 18.307 |
| `adaptive_all` | 0.4900* | 87.2% (world) / 63.4% (author) | 0.4768* | 94.9% (world) / 67.9% (author) | 18.307 (=`adaptive_intercept`, by construction) |

\* world-level point estimate; the world-level CI does not exclude zero
(G0/lean (a) underpowering, see above) — the author-level companion CI
does, decisively, for both `adaptive_hazard_ridge` and `adaptive_all`.

## Lean adjudication

### Lean (a) — LOCALIZABLE: at least one single-constant arm recovers ≥50% of the c=4 gain, paired-world CI excluding zero

**UNDERPOWERED for `hazard_ridge` (and for `adaptive_all`'s own analogous check); clean MISS for the other five.**

| constant | fraction of gain @4x | fraction @8x | world CI excludes 0? | status |
|---|---|---|---|---|
| `hazard_ridge` | 89.5% | 95.5% | NO (world) / **YES (author)** | **UNDERPOWERED** |
| `tolerance` | 0.0% | −0.0% | NO | MISS |
| `weight_floor` | −0.0% | −0.0% | NO | MISS |
| `clip_bound` | 0.0% | 0.0% | NO | MISS |
| `probe_epsilon` | −0.2% | −0.0% | NO | MISS |
| `intercept` | −7.6% | −5.3% | NO (world) / YES-negative (author) | MISS |
| `adaptive_all` (feeds PIVOT only) | 87.2% | 94.9% | NO (world) / **YES (author)** | **UNDERPOWERED** |

`hazard_ridge`'s point estimate clears the 50% bar by a wide margin at
*both* budgets (89.5%, 95.5%) — nowhere close to a knife-edge — but its
own paired-by-world (n=6) CI is [−0.0162, 0.1489] @4x and [−0.0059, 0.1664]
@8x, both including zero, with a half-width (~0.08) that is itself ~4× the
G0 bar. This is not scored MISS: per G4, an arm whose own comparison fails
the pre-registered power bar cannot be scored a clean null. `hazard_ridge`
is the ONLY constant for which this distinction matters — every other
constant's world-level CI is either tight-and-zero (genuinely inert, no
power issue: half-widths are 0.0002–0.006, far inside the bar) or (for
`intercept`) tight-and-small-negative. **Four of six constants (`tolerance`,
`weight_floor`, `clip_bound`, `probe_epsilon`) are decisively, adequately-
powered nulls — this is a real finding, not an artifact of underpowering.**

### Lean (b) — DEFINITIONAL CHECK: the winning arm's recovery is invariant across c ∈ {0.25, 1.0, 4.0}

**MISS, decisively.** All C(3,2)=3 pairwise comparisons, both budgets,
author-level paired CI (n=745, adequately powered — this is the same grain
that gave lean (a)'s decisive author-level companion, so this MISS is not
itself a power artifact):

| budget | c pair | mean diff (lo − hi) | 95% CI | inside ±0.02? |
|---|---|---|---|---|
| 4x | 0.25 vs 1.00 | +0.0836 | [0.0708, 0.0965] | NO |
| 4x | 0.25 vs 4.00 | +0.0494 | [0.0299, 0.0688] | NO |
| 4x | 1.00 vs 4.00 | −0.0342 | [−0.0447, −0.0238] | NO |
| 8x | 0.25 vs 1.00 | +0.0933 | [0.0799, 0.1066] | NO |
| 8x | 0.25 vs 4.00 | +0.0692 | [0.0485, 0.0899] | NO |
| 8x | 1.00 vs 4.00 | −0.0241 | [−0.0353, −0.0129] | NO |

Every one of the 6 checks falls decisively outside the margin — not a
knife-edge, and not ambiguous. The SIGN pattern is informative: error at
c=0.25 is highest, error at c=1.0 (the SAME calibration point the adaptive
ridge formula's own deployed anchor sits at) is lowest, and error at c=4.0
is higher again than at c=1.0 (though still lower than at c=0.25). **The
adaptive-ridge formula produces an inverted-U in recovery quality across
the ladder, peaking at c=1, not a flat/invariant line.** Mechanically: the
formula (`ridge_deployed · RAW_SCALE`, computed once from context-level raw
eigenvalues, identical in absolute value at every c by construction) fixes
the ABSOLUTE ridge value rather than the ridge-to-design-scale RATIO at each
c; per the toy-model relation in Part 0 (`ridge_effective(c) ≈
ridge_used/c²` for the raw, unadapted whitening scale), a FIXED `ridge_used`
becomes progressively WEAKER, not appropriately weaker-in-proportion, as c
grows past 1 — at c=4 the already-20×-weakened ridge is weakened by another
16× in effective terms, past whatever point was optimal, while the OTHER
five constants (still at their DEPLOYED, unadapted values in this test, by
the registration's own "everything else held" design) may also bind
differently at c=4's larger raw design scale than they did at c=1 where
they tested cleanly inert. Both are plausible, disclosed, NOT
re-adjudicated mechanisms — no further compute was spent chasing which one
dominates, since doing so after seeing this MISS would be exactly the
post-hoc rescue the standing rules prohibit.

### Lean (c) — NO NEW COSMETIC TRADE: the winning arm's offset does not worsen relative to baseline

**HOLD, trivially and exactly.** `adaptive_hazard_ridge`'s basis is
bit-identical to `baseline`'s at every (world, repetition, role) — G3's
companion structural check above confirms this at 0.0 max abs diff, not
merely by the a priori argument that A1–A5 never touch
`_bases_from_whitening`. Its offset is therefore IDENTICAL to baseline's,
world by world (paired-world CI mean = 0.0, exactly, n=8) — a fortiori
inside the registered ±10%-of-baseline-mean-offset margin (±1.2003). No new
cosmetic trade is possible for this specific winner, by construction.

### Pivot — no single-constant arm AND no all-constants arm reaches 50% of the gain

**UNDERPOWERED, not FIRES, not DOES-NOT-FIRE — reported exactly as such.**
FIRES requires every arm's comparison to be a clean MISS; `hazard_ridge`
and `adaptive_all` are UNDERPOWERED, not MISS, at the registered
paired-by-world grain (G0's own pre-registered finding, not a surprise).
The registered condition therefore cannot be evaluated as written at this
leg's registered statistical grain. **This is disclosed as a genuine
"outside every registered branch" outcome, not resolved by picking either
branch:** the well-powered author-level companion evidence (decisive for
`hazard_ridge`/`adaptive_all`, decisively null for the other four) makes it
implausible that the pivot would fire if the design had been adequately
powered at the registered grain — but that is a informed expectation, not
an adjudicated result, and is reported as such.

## Verdict

**No single verdict word from the registration's own vocabulary
(HOLD/MISS/FIRES/DOES-NOT-FIRE) cleanly covers this outcome; both
components below are simultaneously true and are reported together, exactly
as the outer task's own adjudication instructions anticipate for an
outside-every-branch result:**

1. **`hazard_ridge` is confirmed, on converging evidence, as the (or the
   dominant) IDENTIFIABLE, LOCALIZED source of M4-G2's proven scale
   dependence.** Four independent lines agree: (i) the a priori,
   provable-not-merely-suspected mathematical argument in Part 0 (an L2
   penalty breaks the diagonal-reparameterization invariance that
   unregularized IRLS otherwise has exactly); (ii) the adaptive ridge value
   itself is consistent and directionally stable across all 64 contexts
   (0.00023–0.00089, always 4.6–18% of deployed, never crossing zero or
   flipping sign); (iii) the well-powered author-level companion to lean
   (a) shows a decisive, large, positive effect at both budgets; (iv) the
   five OTHER constants are cleanly, adequately-powered nulls (or a small
   real negative, for `intercept`) at the SAME grain, ruling out "everything
   moves a little" as an alternative explanation.
2. **No tested formula here is CERTIFIED as a genuine, general repair.**
   Lean (b) — the gate explicitly built to distinguish a genuine repair
   from a lucky reparameterization — MISSES decisively, well-powered, in a
   mechanistically interpretable way (an inverted-U peaking exactly at the
   adaptive formula's own calibration point, c=1). The formula tested
   (`ridge_deployed · RAW_SCALE`, c-independent in absolute value) is real
   and large but not reparameterization-invariant; whether a DIFFERENT
   functional form (e.g. one that scales with the ARM's own realized design
   scale rather than only the context's raw eigenvalues) would pass lean
   (b) is an open question this leg does not answer — testing one would be
   exactly the post-hoc rescue the standing rules prohibit.
3. **The PIVOT itself is UNDERPOWERED at the registered grain, not FIRES.**
   This is disclosed as a genuine power failure of the registered design
   (flagged in G0 before compute, using only M4-G2's own persisted
   numbers), not softened into either a HOLD or a MISS.

Consequence for the line: the hypothesis that M4-G2's scale dependence is a
SCALING problem — fixable by making an absolute constant relative to a
data-scale statistic — is **neither retired nor confirmed as solved**.
`hazard_ridge` is now the identified, load-bearing constant for any future
attempt; a future leg attempting a repair should register a c-DEPENDENT
(not merely context-dependent) functional form and MUST re-run lean (b) as
its own certification gate before claiming success — reusing this leg's
localization finding is legitimate reuse of a result, not a rescue of this
leg's own MISS.

## Honest anomalies and disclosures

- **The world-level (n=6) grain, exactly as registered ("paired-by-world"),
  turned out to be severely underpowered** — not merely for the adaptive
  arms but for M4-G2's OWN persisted c=4 gain itself (computed from
  M4-G2's persisted CSV, before any new compute ran here). This was
  disclosed in G0 BEFORE any adaptive-arm compute, per the standing rules,
  and the whole leg's design (`_paired_world_ci` on world-level medians,
  n=6 after M4-G2's own valid-subset exclusion) is unchanged from what
  M4-G1/M4-G2 themselves used for the OFFSET metric — the difference here
  is that TRUTH RECOVERY's own world-to-world variance is evidently larger
  relative to its effect sizes than offset's was, a property of the metric
  and the world set, not a design choice made for this leg.
- **A units-mismatch bug was caught and fixed before any adaptive-arm
  compute was run**: an early draft of lean (c)'s margin literally reused
  lean (b)'s absolute ±0.02 (calibrated for truth error's [0,1] scale) for
  OFFSET (which lives on baseline's own O(5–15) scale) — a margin that
  would have been meaninglessly strict. Fixed to ±10% of baseline's own
  mean offset (reusing M4-G1's own G2 materiality convention) before the
  truth-stage compute that would have made this consequential was run.
- **A signature bug in `_run_winner_ladder_stage` was caught and fixed
  before the truth stage completed** (hence before it could affect any
  number): the first draft passed a single-arm basis/constants lookup into
  `_truth_rows_for_context` while that function still iterated the full
  9-arm `ARM_NAMES` internally, which would have raised `KeyError` the
  first time it ran. Fixed by adding an explicit `arms` parameter.
- **An earlier (superseded) draft of Part 0's adaptive-ridge formula used
  the WRONG statistic** — the whitening's own geometric-mean SCALE FACTOR
  (`1/√eigenvalue`) rather than the RAW eigenvalue itself — reasoning
  (before any compute) that a big scale factor meant a big design. A direct
  empirical check on one sampled context (reported in Part 0) showed this
  is backwards: whitened features have ~unit variance BY THE DEFINITION of
  whitening, regardless of how large the scale factor was; the scale factor
  measures the AMPLIFICATION APPLIED, not the RESULT. The corrected
  statistic (mean raw retained eigenvalue) was adopted before any
  adaptive-arm truth-recovery compute ran, with the reasoning and the
  empirical check both disclosed in Part 0 rather than silently fixed.
- **`topology_mismatch` is visibly the most computationally heterogeneous
  world**: its 8 repetitions retain between 6 and 12 eigendirections (every
  other world retains 11 or 12 on all 8 reps), and its raw_scale ranges
  0.051–0.178 versus every other world's tighter 0.045–0.114 band. This did
  not require any special handling — the same code path ran unmodified —
  but is disclosed since it is visibly the outlier in `context_meta.csv`.
- **Compute cost**: 8 chunked world-level truth-stage runs, each
  context-build ≈4–6s/rep (8 reps) + ≈14–38s per (repetition, budget) across
  all 9 arms together (budget=8x consistently ≈2× budget=4x's cost); run
  first sequentially (one world ≈6–7 minutes solo) then increasingly in
  parallel (up to 4 concurrent, given 10 available cores) for the remaining
  worlds, ≈25 minutes wall-clock total for all 8 (`topology_mismatch` was
  consistently the slowest, both here and in the offset/winner-ladder
  stages, tracing to its own wide per-repetition retained-rank spread,
  6–12 vs every other world's 11–12). The offset stage (4 arms × 8 worlds,
  GPA-only, no per-author/view sweep) was far cheaper, under 2 minutes per
  world run individually. The 8-world winner-ladder stage (1 arm × 2 extra
  c's × 2 budgets × 8 worlds) took ≈2–8 minutes per world (partial
  concurrency again); `--assemble` itself is sub-second. All compute was
  driven in the foreground in explicit per-world/per-stage chunks,
  consistent with this
  arc's standard chunked-execution workaround.

## Faithfulness chain (all green)

| gate | value |
|---|---|
| G1 anchor: truth recovery vs M4-G2 persisted (`baseline`/`c4_reference` vs `c_1.0`/`c_4.0`, 8,192 rows) | **0.0** |
| G1 anchor: offset vs M4-G2 persisted (16 rows) | **0.0** |
| G3 degenerate equality (searched non-degenerate spot, 9 arms × 8 worlds = 72 checks) | **0.0** |
| structural basis-identity check (5 single-constant arms vs baseline, 8 worlds × 8 reps × 3 roles) | **0.0** |
| row-count completeness (truth: 36,864 = 8 worlds×8 reps×2 budgets×2 views×16 authors×9 arms; offset: 32 = 8 worlds×4 arms; winner-ladder: 8,192 = 8 worlds×8 reps×2 c's×2 budgets×2 views×16 authors) | exact match, every partial |
| valid-6-world subset, recomputed from this leg's own arm-invariant `e_orc_true` vs re-derived from scratch | reproduces M4-G2's own adopted set exactly |
| `DEPLOYED_PROBE_EPSILON == leg4.PROBE_EPSILON` (module-load-time assertion) | passes (both 0.05) |

## Boundaries

Finite synthetic M4-C.2 worlds only. 8 D1 worlds (reused verbatim from
M4-G2); truth-recovery statistics restricted to M4-G2's own valid 6-world
subset (excludes `linear_null_ecology`, `fast_return_equal_marginal` — the
pre-existing `_relative_error` near-zero-denominator fragility, unrelated to
any manipulation in this leg). Truth-referenced recovery via
budget-regenerated (4x/8x events) finite panels from the frozen world law,
compared to the analytic `D_true`, exactly M4-G1/M4-G2's own construction,
reused unchanged. No natural-text, personality, or clinical claim; no seal,
no independent verification (operator directive 2026-08-01). This leg
answers the question M4-G2's planner adjudication note posed (can the
proven scale dependence be localized in identifiable constants, and does
making them relative deliver c=4's gain at c=1); it does not re-open M4-G1's
or M4-G2's own leans, and it does not test any functional-form repair beyond
the six-constant, `RAW_SCALE`-relative family registered in Part 0. The open
question for any future leg: whether a c-dependent (not merely
context-dependent) adaptive-ridge form can pass lean (b)'s own invariance
certification, and whether the registered world-level grain should be
redesigned (e.g. paired-by-(world×repetition) rather than paired-by-world)
for adequate power on truth-recovery statistics specifically, given this
leg's and M4-G2's own lean (b) both found the author-level grain
comfortably powered where the world-level grain was not.
