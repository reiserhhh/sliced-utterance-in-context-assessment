# SUICA M4-G5 — Per-Column Ridge: Does the Named Defect Have the Obvious Fix?

Tier: **EXPLORATORY** (open-exploration phase, operator directive 2026-08-01).
Registered before run: `docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md`, "M4-G5
registration" (2026-08-03, BEFORE run); ledger row M4-G5. Script:
`scripts/run_suica_m4_g5_per_column_ridge.py`. Artifacts:
`results/m4_g5_per_column_ridge/`.

## Headline, stated up front

**The PIVOT DOES NOT FIRE — lean (a) COMPLETION holds decisively, for BOTH per-column arms, at the registered ±0.02 margin, at the registered AUTHOR grain (n=745), well-powered.** `column_standardized`'s recovery is EXACTLY (bit-for-bit, 0.0 paired difference, all 745 authors, both budgets, all three c-pairs) invariant across c ∈ {0.25, 1.0, 4.0}. `diagonal_ridge`'s is invariant to 1–4×10⁻¹⁴ (floating-point noise), also on all six checks. Both are not merely inside the margin but seven-plus orders of magnitude inside it — the residual c-dependence the scalar covariant ridge left (M4-G4: 10.9% of the raw swing) is closed to **0.0% (`column_standardized`, exact) and ~3–8×10⁻¹⁴ relative (`diagonal_ridge`, floating-point zero)** — both decisively beat M4-G4's 10.9% residual on the identical statistic. **Lean (c) SPECIFICITY is decisively CONFIRMED** (`specificity_weight_floor` shows large, non-invariant swings, 0.06–0.30, all six checks OUTSIDE the margin — the same covariant/diagonal machinery applied to an M4-G3-inert constant does nothing). G2 shows both mechanisms are unambiguously LIVE (design-variance spread collapses from 38.8×–908.1× to exactly 1.0× for `column_standardized`; the realized ridge spread for `diagonal_ridge` exactly tracks that same 38.8×–908.1× heterogeneity, up from a deployed-uniform 1.0×). G1 anchor and G3 truth-path invariance both pass at exactly 0.0 (32,768 and 112 checks respectively).

**But lean (b) NO LOSS MISSES decisively for both arms** — at c=1, `column_standardized`'s recovery is *worse* than `g3_raw_scale`'s by 0.051–0.061 (both budgets, CI entirely on the worse side), `diagonal_ridge`'s by 0.053–0.062 — almost exactly the size of M4-G4's own persisted c=4 gain (0.059/0.068), because both arms' calibration rule (registered, not tunable) targets the *deployed* ridge (0.005) in the homogeneous-column limit, not `g3_raw_scale`'s own much weaker, specially-tuned value — the identical mechanism M4-G4 itself predicted and found for its own covariant arms, now inherited one level deeper by the (successfully) fixed structural mechanism. **This outcome satisfies neither of the registration's two named branches** ("repair CERTIFIED" requires lean (a) HOLD *and* no loss; "PIVOT FIRES" requires lean (a) to MISS for every arm) — stated plainly, per the outer task's own instruction, rather than softened: **the named structural defect — heterogeneous column scaling inside `_hazard_design` — is now fully, completely, and specifically confirmed as the ENTIRE explanation for M4-G4's residual c-dependence (closed to floating-point zero, both mechanisms, both independently), but achieving invariance and matching `g3_raw_scale`'s recovery level are demonstrably separate, orthogonal questions — the former is solved; the latter is an open, distinct calibration-anchor choice.**

## Part 0 — registered column inventory, statistic, calibration rule, specificity-control reading (written before compute)

### 0.1 The full `_hazard_design` column inventory, from the code

`_hazard_design(rows, basis, *, model, misalign_gate=False)`
(`suica_core/m4_chart_ecology_estimator.py:287-330`) builds, for
`categories, width = basis.shape` (`basis` from `leg10._bases_from_whitening`,
itself `column_stack([ones, whitened])` — `scripts/run_suica_m4_d_direction_anatomy_leg10.py:356`
— so `basis[:,0]` is always a literal-1 column and `basis[:,1:]` is
`whitened_c = c·whitened_1`, identity (*) from M4-G4's own Part 0):

| block | design columns | source line(s) | value | provenance |
|---|---|---|---|---|
| `intercept` | 1 (index 0) | estimator.py:297 `np.ones((events,categories,1))` | literal 1 | **c-invariant** |
| `condition_0..width-1` | `width` (indices 1..width) | estimator.py:298-301, names estimator.py:269 | `basis[None]` broadcast | `condition_0` = `basis[:,0]` = literal 1 → **c-invariant**; `condition_1..width-1` = `basis[:,1:]` = `c·whitened_1` → **c-scaled, exactly linear in c** |
| `generated_current` | 1 (return/feedback/gate) | estimator.py:306 | raw world data | **c-invariant** |
| `duration` | 1 (return/feedback/gate) | estimator.py:307 | raw world data (`tanh(duration/4)`) | **c-invariant** |
| `feedback_{p}_{d}` | `width·dimensions` (feedback/gate) | estimator.py:311-315, `einsum("kp,nd->nkpd", basis, response_next)` | `basis[:,p]·response_next[:,d]` | `p=0` → **c-invariant** (crosses the unscaled intercept sub-column with raw `response_next`); `p=1..width-1` → **c-scaled, exactly linear in c** |
| `gate_{p}_{d}` | `width·dimensions` (gate only) | estimator.py:317-321, `feedback·gate_row` | same split as `feedback_{p}_{d}`, multiplied by a raw 0/1 row factor | `p=0` → **c-invariant**; `p=1..width-1` → **c-scaled, exactly linear in c** |

Column counts by `model` (`width = 1+k_retained`, `k_retained ∈ [6,12]`
empirically across this line's 64 (world,rep) contexts —
`results/m4_g4_covariant_ridge/calibration_context_rows.csv`; `dimensions =
response_dimensions = 2`, fixed by `configs/m4_chart_ecology.json`): `base`:
`1+width`. `return`: `1+width+2`. `feedback`: `1+width+2+width·dimensions`.
`gate`: `1+width+2+2·width·dimensions`. **Every column, in every model, is
exactly one of two kinds: literally constant in c (degree 0), or exactly
linear in c (degree 1)** — proved directly from the code, confirmed
empirically (`results/m4_g5_per_column_ridge/column_inventory.csv`, all
1,050 inventoried columns across 8 worlds × 4 models classified `c_invariant`
or `c_scaled_degree1`, zero `UNEXPECTED`/`AMBIGUOUS_DEGENERATE_ZERO`).

### 0.2 Registered column-scale statistic

Per-column **variance (ddof=1)**, computed on the assembled, unweighted
`_hazard_design` output — the same stacked (calibration+selection) design
`_fit_logistic`'s Gram matrix is built from — computed once, before any IRLS
iteration, fresh for whatever `(context, route, rows, c)` a given fit call
uses:

```
var_j(context, route, rows, c) := Var_ddof1( design(rows, c)[:, j] )
```

A genuine extension of M4-G4's own S1 "var" statistic (computed on `basis`
alone) to the *full* assembled hazard design, since this leg's target is
the full `_hazard_design` column inventory, not merely the basis.
Degenerate-column floor: `DESIGN_VAR_FLOOR = 1e-12` (reused, not invented —
the same value appears pervasively in this codebase, e.g.
`leg10._whitening_with_lambda`'s `np.maximum(eigenvalues[retained]+lam,
1e-12)`).

### 0.3 `column_standardized` (registered formula)

For column `j≠0` (`intercept`, index 0, is already ridge-exempt via
`penalty[0,0]=0.0`, estimator.py:342, under every arm — left untouched,
never rescaled): if `var_j(context,route,rows,c) ≥ DESIGN_VAR_FLOOR`,
`scale_j := sqrt(var_j)`; else `scale_j := 1.0` (no rescale). This
"leave a near-zero-variance column unscaled" rule is not invented for this
leg — it is the exact convention already present in this same estimator
file for the identical purpose (`fit_m4_chart_ecology_route`,
estimator.py:1009-1010: `scale = np.where(scale > 1e-8, scale, 1.0)`), reused
here (floor tightened to `1e-12` for column-level *variance*, matching this
leg's own inventory floor, rather than the `1e-8` std-level floor of that
unrelated call site — a disclosed, deliberate choice).

```
design_std[:, j] = design[:, j] / scale_j
beta_std          = g3._fit_logistic_adaptive(design_std, target, ridge=ridge_deployed, ...)   # UNCHANGED, reused
beta              = beta_std / scale                                                            # un-rescale
```

"The single ridge acts in common units": `ridge_deployed` (0.005) is used
unmodified — no new calibration constant. Downstream (`_hazard_probability`,
`_feedback_derivative`) are called on `beta` against the original,
un-standardized basis/design — byte-identical to every other arm's own
downstream code.

### 0.4 `diagonal_ridge` (registered formula)

Design is left **completely untouched**; only the penalty matrix changes,
from `ridge·n·I` (estimator.py:341-342) to `n·diag(0, ridge_1(c), ...,
ridge_{p-1}(c))` (index 0 stays exempt):

```
K(context,route,rows)          := ridge_deployed / MEAN_{j≠0, var_j(c=1)≥FLOOR}( var_j(context,route,rows,c=1) )
ridge_j(context,route,rows,c)  := K(context,route,rows) · var_j(context,route,rows,c)     for j≠0, var_j(c=1) ≥ FLOOR
ridge_j(context,route,rows,c)  := ridge_deployed                                          for j≠0, var_j(c=1) < FLOOR  (degenerate fallback)
ridge_0                        := 0
```

**Degenerate-column fallback, caught by a smoke test and fixed BEFORE any
hypothesis-relevant truth-recovery number existed.** `condition_0` (design
index 1, `basis[:,0]`) is always a literal-1 column, structurally identical
to the ridge-exempt `intercept` (index 0) — its `var_j(c=1)` is exactly 0.
The naive formula (no fallback) gives it `ridge_j = K·0 = 0` exactly, which
reintroduces the `intercept`/`condition_0` collinearity the deployed scalar
ridge's own uniform nonzero value was incidentally preventing, and
`_fit_logistic_diagonal`'s `np.linalg.solve` raised `LinAlgError: Singular
matrix` on the `feedback`/`gate` routes in the smoke test. Fix: any
non-exempt but degenerate column keeps its ridge at the plain deployed
value — exactly mirroring `column_standardized`'s own "leave a degenerate
column unscaled" rule, making the two arms' degenerate-column treatment
consistent by construction.

**Registered ambiguity, both readings disclosed.** `K` could be calibrated
(i) **globally** — a single scalar across all 64 (world,rep) contexts,
mirroring M4-G4's own `alpha_var` exactly — or (ii) **per-call** — frozen
fresh from that same (context, route, rows) call's own design at c=1, reused
at whatever c that call needs. Both satisfy the registration's literal
requirement (homogeneous-column limit reproduces `ridge_deployed` exactly,
at c=1, under either reading). **ADOPTED: (ii), per-call.** Reasons, stated
before compute: (a) M4-G4's own hand-off explicitly named GLOBAL
calibration as a source of its own 10.9% residual ("alpha is calibrated
globally, not per-context, so some residual is contributed by cross-context
variation... around its population mean"). Since this leg tests whether a
more targeted, per-column mechanism can close that residual, keeping the
same global-calibration limitation would confound the test. Per-call
calibration removes this specific, already-identified confound. (b)
"Proportional to each column's own scale statistic" is most literally read
as within that same column's own realized context. **Reading (i) is
disclosed, not scored as a second arm** (mirroring M4-G4's own precedent):
the global value that (i) would have used is recorded in
`calibration_source.json`, computed for free from the same per-context
`var_j(c=1)` statistics this leg already gathers — no extra compute stage.

### 0.5 Pre-registered mechanistic prediction (a provable, not merely hoped-for, argument — exceeding M4-G4's own "base-route-only" guarantee)

Every column of `_hazard_design`, in every route, is exactly degree-0 or
exactly degree-1 in c (0.1). Write `D(c) := diag(scale_j(c))`, where for
`column_standardized`, `scale_j(c) = sqrt(var_j(c))`, and for
`diagonal_ridge`'s reparameterization argument, `scale_j(c) := c` for
c-scaled `j`, `:= 1` for c-invariant `j` — both are, up to the
degenerate-column floor, the same diagonal reparameterization applied on
opposite sides of the optimization problem (`column_standardized` applies
`D(c)^{-1}` to the data and fits with a scalar ridge; `diagonal_ridge`
applies `D(c)⊙D(c)` to the penalty and fits on the untouched data).
Substituting `beta = D(c)^{-1} gamma`: for `column_standardized`,
`design(c) = design(1) D(c)` exactly, so `design(c) beta = design(1) gamma`
regardless of c. For `diagonal_ridge`, `D(c)^{-1} penalty(c) D(c)^{-1} = n ·
diag(K·var_j(1))`, independent of c. **In both cases the reparameterized
IRLS objective — deviance plus penalty, as a function of `gamma` — is
exactly c-independent, and so is the reparameterized initial point.**
Newton's method / IRLS is covariant under invertible linear
reparameterization, so the entire iterate sequence in `gamma`-coordinates is
identical at every c. Consequence: `design(rows,c) @ beta(c) =
design(rows,1) @ beta(1)` exactly, for any rows (training or evaluation/probe
alike) — hence `e_arm_true` should be c-invariant up to floating point, for
every route, not merely `base` as in M4-G4's own guarantee.

One disclosed, non-exact channel: the IRLS convergence check is evaluated in
`beta`-space, not `gamma`-space, so the *iteration count* at which IRLS
stops can differ slightly by c — exactly M4-G3's own Category A2 ("IRLS
convergence tolerance"), already found cleanly, adequately-powered INERT at
both grains in M4-G3's own test. **Prediction: lean (a) should HOLD for
both arms, likely far inside the ±0.02 margin — a stronger result than
M4-G4's own 89.1%.**

**Pre-compute validation (a smoke test, not the registered leans
themselves).** `results/m4_g5_per_column_ridge/provable_invariance_spot_check.csv`
verifies this directly on one representative context/route (`feedback`,
`endogenous_creation_expansion` rep 0): the reparameterized coefficient
`gamma` differs by ≤1.5e-14 across all three c-pairs for `diagonal_ridge`,
and exactly 0.0 for `column_standardized`; `e_arm_true` itself differs by
≤1.4e-15. An early diagnostic draft mis-labeled `beta` (the un-rescaled,
original-units coefficient, expected to vary with c) as `gamma` and
appeared to show a large discrepancy for `column_standardized` — caught and
corrected before any hypothesis-relevant truth-recovery number existed
(disclosed in "Honest anomalies," below).

### 0.6 Specificity control: reading adopted, and why

**Registered ambiguity, disclosed.** "A specificity control carried over
from M4-G4: the same per-column rule applied where it should do nothing."
Of M4-G3's four cleanly-inert constants, `weight_floor` is the only
multiplicative survivor after M4-G4's own exclusions (`tolerance` is a mode
switch; `clip_bound`/`probe_epsilon` rejected by M4-G4's own Part 0 for
plausible-live-channel risk at the c-ladder's extremes). `weight_floor` is
clipped **per-observation** (`fitted·(1−fitted)`, estimator.py:348) — it has
no design-column index at all, so there is no literal "per-column"
decomposition of it to construct; that reading is **rejected as VACUOUS by
construction** — no such object exists in the codebase (every M4-G3/M4-G4
inert constant is scalar; only `hazard_ridge`, added as `ridge·n·I` to a
per-column Gram structure, ever had a column-indexed form). **ADOPTED
reading**: "carried over from M4-G4" reuses M4-G4's own control — same
target (`weight_floor`), same mechanism
(`floor_covariant(context,c)=alpha_floor·POST_SCALE_VAR(context,c)`, `alpha_floor`
read from M4-G4's own persisted `calibration.json`) — as this leg's
specificity control, verified to reproduce M4-G4's persisted values at all
three c to ≤1e-12 (an additional disclosed anchor beyond the task's three
named ones).

### Design summary

Six arms: `baseline`, `g3_raw_scale` (c=1 only, anchors); `covariant_var`,
`specificity_weight_floor` (c ∈ {0.25,1,4}, full new compute, both anchored
to M4-G4's persisted values at all three c); `column_standardized`,
`diagonal_ridge` (c ∈ {0.25,1,4}, full new compute, this leg's own
mechanisms). No offset/GPA stage: neither new arm ever calls
`_bases_from_whitening` — both operate strictly downstream of it.

---

## Part 1 — Outcome

*(Everything below is computed after the run; Part 0 above was frozen
before compute began.)*

### G0 POWER (reported first, per instruction)

Bar: ±0.01 absolute half-width, reused verbatim from `g4.G0_FRACTION_BAR`
(this line's own "half of the ±0.02 leaning margin" convention). Also
reported against M4-G3's own persisted author-level c=4 gain (0.0591@4x /
0.0683@8x, the same reference M4-G4 used).

| | value |
|---|---|
| Comparisons run at author grain | 22 (lean (a): 2 arms × 3 c-pairs × 2 budgets = 12; lean (b) companion: 2 arms × 2 budgets = 4; lean (c): 1 arm × 3 c-pairs × 2 budgets = 6) |
| Half-width range | 0.0 – 0.0189 (median 3.7×10⁻¹⁴) |
| Underpowered vs ±0.01 bar | 10 of 22 |

**The 12 lean (a) rows — the ones that decide the PIVOT — have half-widths of essentially exactly 0.0** (paired differences across c are deterministically ~0 for both arms, so the standard error itself is ~0 — not "small," but the strongest possible form of "not underpowered": there is no meaningful uncertainty left to resolve). **The 10 "underpowered"-by-the-±0.01-bar rows are exactly the 4 lean (b) and 6 lean (c) rows — the ones with the LARGEST effects (0.052–0.301)**, where a half-width of 0.011–0.019 is still 4.4–20.4× smaller than the observed effect itself; every one is classified OUTSIDE its margin, not AMBIGUOUS — "underpowered vs the ±0.01 bar" does not, and under the registered equivalence-form logic must not, block a decisive MISS/OUTSIDE conclusion on an effect that large. **The PIVOT-deciding comparisons are not merely adequately powered — they carry essentially zero residual uncertainty.**

### G1 ANCHOR

| check | n compared | max abs diff | tolerance | pass |
|---|---|---|---|---|
| `baseline`@c=1 vs M4-G4 persisted | 4,096 | **0.0** | 1e-12 | YES |
| `g3_raw_scale`@c=1 vs M4-G4 persisted | 4,096 | **0.0** | 1e-12 | YES |
| `covariant_var`@{0.25,1,4} vs M4-G4 persisted | 12,288 | **0.0** | 1e-12 | YES |
| `specificity_weight_floor`@{0.25,1,4} vs M4-G4 persisted | 12,288 | **0.0** | 1e-12 | YES |

**PASS**, exact to the bit, across all 32,768 anchor-checked rows. `baseline`/`g3_raw_scale` anchored at c=1 only (M4-G4's own compute-scope reduction, carried over verbatim — see Part 0 Design summary). `covariant_var` and `specificity_weight_floor` are anchored at **all three** c, a stronger check than the registration's literal minimum, since M4-G4 itself fully computed both at all three c; the `specificity_weight_floor` anchor is an *additional* disclosed check beyond the task's three named ones, required by this leg's adopted reading of "carried over from M4-G4" (Part 0.6) — if the carry-over claim were false, this anchor would have failed.

### G2 COLUMN-SCALE LIVENESS

Design column-variance spread (max/min ratio across non-degenerate, non-exempt columns) BEFORE and AFTER, averaged across 8 worlds × 4 hazard models, at each c:

| c | mean spread BEFORE | `column_standardized` spread AFTER | reduction ratio | status | `diagonal_ridge` ridge spread AFTER (deployed uniform BEFORE = 1.0) | status |
|---|---|---|---|---|---|---|
| 0.25 | 38.79× | **1.0000000000002×** | 0.0258 (2.58% of BEFORE) | **LIVE** | 38.79× | **LIVE** |
| 1.00 | 59.55× | **1.0000000000002×** | 0.0168 (1.68% of BEFORE) | **LIVE** | 59.55× | **LIVE** |
| 4.00 | 908.14× | **1.0000000000002×** | 0.0011 (0.11% of BEFORE) | **LIVE** | 908.14× | **LIVE** |

Materiality margin (registered): `column_standardized` is LIVE iff the AFTER/BEFORE ratio ≤ 10%; `diagonal_ridge` is LIVE iff its ridge-value spread departs from the deployed-uniform 1.0 by more than 10% (reusing this line's own established "ratio departs from 1.0 by >10%" convention, e.g. M4-G4's own G2 rule). **Both mechanisms are decisively LIVE at every c, by a wide margin — not a knife-edge call.** `column_standardized` collapses the design's own column-scale spread to *exactly* unit variance (the definition of standardization succeeding); `diagonal_ridge`'s realized ridge spread *exactly* equals the design's own BEFORE spread at every c (an algebraic consequence of `ridge_j ∝ var_j` with a single shared proportionality constant — the ridge now tracks the design's own heterogeneity precisely, up from the deployed scalar's perfectly uniform 1.0×). Neither arm is INERT or VACUOUS at any c. Raw evidence: `results/m4_g5_per_column_ridge/g2_column_scale_spread_evidence.csv` (96 rows: 8 worlds × 4 models × 3 c).

**Column inventory** (`results/m4_g5_per_column_ridge/column_inventory.csv`, 1,050 rows: 8 worlds × 4 models × (columns per model)): every column classified `c_invariant` or `c_scaled_degree1` by direct empirical comparison of designs built at c=1 vs c=2 on identical rows — **zero** `UNEXPECTED` or `AMBIGUOUS_DEGENERATE_ZERO` classifications. Per-model counts: `base` 16 c-invariant / 89 c-scaled; `return` 32 / 89; `feedback` 48 / 267; `gate` 64 / 445 — confirming the Part 0.1 analytical derivation (every column is exactly degree-0 or degree-1 in c, no exceptions, across every route this line's 64 contexts realize) as an empirical fact, not merely a code-reading claim.

### G3 TRUTH-PATH INVARIANCE

Gap-stage-style `e_arm_true` vs. the truth-path's own budget=1.0 short-circuit, at a searched non-degenerate `(rep, view, author)` per world, for every `(arm, c)` combination actually computed (14 per world: 6 at c=1, 4 at c=0.25, 4 at c=4) × 8 worlds = **112 checks: max abs diff 0.0. PASS.**

### G4 MATERIALITY FORM — explicit compliance

- **G0** is a CI-half-width-vs-bar equivalence bound (±0.01), reused from M4-G4; underpowered comparisons are explicitly flagged, never silently read as nulls — and in this leg the PIVOT-deciding comparisons carry essentially zero half-width, the strongest possible non-underpowered case.
- **G1** is a degenerate exact-equality check (0.0 achieved on all four anchors, 32,768 rows), not a significance test.
- **G2** is a ratio-vs-materiality-margin equivalence check (LIVE iff the AFTER/BEFORE reduction ratio ≤ 10% for `column_standardized`, or the ridge-spread departs from 1.0 by >10% for `diagonal_ridge`) — decisively satisfied (2.6%, 1.7%, 0.1% reduction; 38.8×–908.1× ridge spread), not a binary "did anything change" test.
- **Leans (a)/(b)/(c)** are three-way WITHIN/OUTSIDE/AMBIGUOUS classifications on paired-author CIs against fixed margins — never nil-significance; the 10 "underpowered vs ±0.01" rows above are all large, decisive OUTSIDE effects, reported as such, not as ambiguous. **Compliant throughout.**

## Per-arm × per-c summary table

Pooled author-level mean `e_arm_true` (n=745, 6 valid worlds, degenerate excluded), both budgets:

| arm | c | @4x mean | @8x mean |
|---|---|---|---|
| `baseline` | 1.00 | 0.5582 | 0.5556 |
| `g3_raw_scale` | 1.00 | 0.5068 | 0.4949 |
| `covariant_var` | 0.25 | 0.5736 | 0.5711 |
| `covariant_var` | 1.00 | 0.5602 | 0.5577 |
| `covariant_var` | 4.00 | 0.5420 | 0.5383 |
| `specificity_weight_floor` | 0.25 | 0.7882 | 0.7882 |
| `specificity_weight_floor` | 1.00 | 0.5582 (=`baseline`, exact) | 0.5556 (=`baseline`, exact) |
| `specificity_weight_floor` | 4.00 | 0.4990 | 0.4872 |
| `column_standardized` | 0.25 | **0.558329** | **0.555418** |
| `column_standardized` | 1.00 | **0.558329** | **0.555418** |
| `column_standardized` | 4.00 | **0.558329** | **0.555418** |
| `diagonal_ridge` | 0.25 | **0.560096** | **0.557118** |
| `diagonal_ridge` | 1.00 | **0.560096** | **0.557118** |
| `diagonal_ridge` | 4.00 | **0.560096** | **0.557118** |

`covariant_var`/`specificity_weight_floor`/`baseline`/`g3_raw_scale` rows reproduce M4-G4's own persisted table exactly (G1 anchor, above). **`column_standardized` and `diagonal_ridge` are identical to six decimal places across the entire c-ladder** — the row-level gate check (lean (a), below) confirms this holds per-author, not merely in the pooled mean. Both sit close to `baseline`'s own c=1 level (0.5582/0.5601 vs 0.5582), not `g3_raw_scale`'s lower one (0.5068) — this is the mechanistic signature lean (b) below quantifies.

## Lean adjudication

### Lean (a) — COMPLETION: at least one per-column arm is c-invariant within ±0.02, author grain

**HOLDS decisively for BOTH arms — not a knife-edge, not merely "inside the margin," but floating-point exact.**

| arm | budget | c-pair | mean diff | 95% author CI | class |
|---|---|---|---|---|---|
| `column_standardized` | 4x | 0.25 vs 1.0 | 0.0 | [0.0, 0.0] | WITHIN |
| `column_standardized` | 4x | 0.25 vs 4.0 | 0.0 | [0.0, 0.0] | WITHIN |
| `column_standardized` | 4x | 1.0 vs 4.0 | 0.0 | [0.0, 0.0] | WITHIN |
| `column_standardized` | 8x | (all 3 pairs) | 0.0 | [0.0, 0.0] | WITHIN |
| `diagonal_ridge` | 4x | 0.25 vs 1.0 | −9.3×10⁻¹⁵ | [−2.0×10⁻¹⁴, 1.2×10⁻¹⁵] | WITHIN |
| `diagonal_ridge` | 4x | 0.25 vs 4.0 | −9.5×10⁻¹⁵ | [−4.9×10⁻¹⁴, 3.0×10⁻¹⁴] | WITHIN |
| `diagonal_ridge` | 4x | 1.0 vs 4.0 | −1.9×10⁻¹⁶ | [−3.6×10⁻¹⁴, 3.5×10⁻¹⁴] | WITHIN |
| `diagonal_ridge` | 8x | 0.25 vs 1.0 | −1.1×10⁻¹⁴ | [−2.4×10⁻¹⁴, 1.6×10⁻¹⁵] | WITHIN |
| `diagonal_ridge` | 8x | 0.25 vs 4.0 | −2.3×10⁻¹⁴ | [−5.2×10⁻¹⁴, 5.9×10⁻¹⁵] | WITHIN |
| `diagonal_ridge` | 8x | 1.0 vs 4.0 | −1.2×10⁻¹⁴ | [−3.6×10⁻¹⁴, 1.2×10⁻¹⁴] | WITHIN |

`column_standardized`'s per-author, per-budget `e_arm_true` is bit-identical (0.0 paired difference, all 745 authors) at every one of the three c values — a direct empirical confirmation of the Part 0.5 provable-invariance argument, not merely a lucky aggregate. `diagonal_ridge`'s is invariant to 10⁻¹⁴–10⁻¹⁵, consistent with the same argument up to ordinary floating-point roundoff accumulated over the IRLS iterations and the two extra `_hazard_design` builds (at c and at c=1) its own mechanism requires. **`column_standardized` status: HOLD. `diagonal_ridge` status: HOLD. Both arms HOLD. Lean (a) HOLDS — the PIVOT does not fire.**

### Lean (b) — NO LOSS: winning arm's recovery at c=1 not worse than `g3_raw_scale`'s (disclosed companion, computed for both arms since both HOLD lean (a))

**MISSES, decisively, for both arms:**

| arm | budget | mean diff (candidate − `g3_raw_scale`) | 95% author CI | class |
|---|---|---|---|---|
| `column_standardized` | 4x | +0.0515 | [0.0399, 0.0631] | OUTSIDE (worse) |
| `column_standardized` | 8x | +0.0605 | [0.0485, 0.0726] | OUTSIDE (worse) |
| `diagonal_ridge` | 4x | +0.0533 | [0.0419, 0.0646] | OUTSIDE (worse) |
| `diagonal_ridge` | 8x | +0.0622 | [0.0506, 0.0739] | OUTSIDE (worse) |

Both arms' c=1 error is worse than `g3_raw_scale`'s by 0.051–0.062 — almost exactly M4-G4's own persisted c=4 gain (0.0591/0.0683), i.e. the per-column treatments give back essentially the *entire* gain `g3_raw_scale` found, landing within 0.0002–0.0019 of `baseline`'s own c=1 level (0.558329 vs 0.558152 for `column_standardized`; 0.560096 vs 0.558152 for `diagonal_ridge` — see the summary table). **The mechanism is fully traceable to a Part 0 design choice, disclosed there though its lean (b) consequence was not explicitly forecast**: both `column_standardized`'s scalar ridge (`ridge_deployed`, unmodified — Part 0.3) and `diagonal_ridge`'s calibration constant `K` (fixed so the homogeneous-column limit reproduces `ridge_deployed` exactly — Part 0.4) are anchored to the *deployed* value, never to `g3_raw_scale`'s much weaker, specially-fit one — the identical pattern M4-G4 itself explicitly predicted and confirmed for its own (scalar) covariant arms, now found to recur, unprompted, in this leg's per-column arms once the numbers came in. So achieving invariance was never, by this construction, also going to recover `g3_raw_scale`'s gain. **Had a `g3_raw_scale`-calibrated anchor been registered instead, lean (b) might have HELD — but that anchor was not the registered one, and substituting it now would be exactly the post-hoc rescue the outer task prohibits.**

### Lean (c) — QUANTITATIVE IMPROVEMENT: residual c-dependence smaller than the scalar covariant's 10.9%, same statistic M4-G4 used

**Specificity control confirmation — CONFIRMED, decisively (all six checks OUTSIDE the margin):**

| budget | c-pair | mean diff | 95% author CI | class |
|---|---|---|---|---|
| 4x | 0.25 vs 1.0 | +0.2300 | [0.2186, 0.2414] | OUTSIDE |
| 4x | 0.25 vs 4.0 | +0.2892 | [0.2707, 0.3078] | OUTSIDE |
| 4x | 1.0 vs 4.0 | +0.0592 | [0.0480, 0.0703] | OUTSIDE |
| 8x | 0.25 vs 1.0 | +0.2326 | [0.2212, 0.2440] | OUTSIDE |
| 8x | 0.25 vs 4.0 | +0.3010 | [0.2820, 0.3199] | OUTSIDE |
| 8x | 1.0 vs 4.0 | +0.0684 | [0.0568, 0.0800] | OUTSIDE |

`specificity_weight_floor`'s own swings reproduce M4-G4's persisted specificity-control numbers exactly (G1 anchor) — an M4-G3-inert constant given the identical covariant/per-column-style treatment does nothing to fix the c-dependence; the reduction the two new arms achieve is specific to `hazard_ridge`, not a generic side-effect.

**Residual-vs-M4-G4 comparison, on the identical statistic (|mean diff, c=0.25 vs c=4.0| ÷ `specificity_weight_floor`'s own swing on the same pair):**

| arm | budget | my swing (0.25 vs 4.0) | control swing | my residual fraction | M4-G4's residual fraction | improves on M4-G4? |
|---|---|---|---|---|---|---|
| `column_standardized` | 4x | **0.0 (exact)** | 0.2892 | **0.0%** | 10.93% | **YES** |
| `column_standardized` | 8x | **0.0 (exact)** | 0.3010 | **0.0%** | 10.89% | **YES** |
| `diagonal_ridge` | 4x | 9.5×10⁻¹⁵ | 0.2892 | **3.3×10⁻¹²%** | 10.93% | **YES** |
| `diagonal_ridge` | 8x | 2.3×10⁻¹⁴ | 0.3010 | **7.6×10⁻¹²%** | 10.89% | **YES** |

**Lean (c) HOLDS decisively for both arms, at both budgets — not merely "smaller than 10.9%" but 11–12 orders of magnitude smaller.** The scalar covariant ridge M4-G4 tested closed 89.1% of the raw c-dependence and left 10.9% as a structural residual attributed to the design's mixed c-scaled/c-invariant columns; making the SAME family of treatment genuinely per-column closes what remained, completely, on both independently-derived mechanisms.

### Pivot — no per-column arm achieves c-invariance

**DOES NOT FIRE.** Both `column_standardized` and `diagonal_ridge` HOLD lean (a) decisively (not underpowered — the deciding comparisons carry essentially zero residual uncertainty). Per the registration, the PIVOT requires every arm to MISS; neither does.

## Verdict

**Stated plainly, per the outer task's own instruction, with no post-hoc rescue and no softening of the miss:**

1. **The named structural defect is fully, completely, and specifically confirmed as the entire explanation for M4-G4's residual c-dependence.** M4-G4 named the mechanism — `_hazard_design` mixes c-scaled columns (built from the whitened basis) with c-invariant ones (`generated_current`/`duration`, raw data; `feedback_0_d`/`gate_0_d`, crossed with the unscaled intercept) — and showed a single scalar ridge could close only 89.1% of the raw c-dependence. **Two independent per-column mechanisms — one reshaping the design (`column_standardized`), one reshaping the penalty (`diagonal_ridge`) — each close the remaining 10.9% to floating-point zero** (exactly 0.0 for `column_standardized`; ~10⁻¹⁴ absolute, ~10⁻¹² % relative, for `diagonal_ridge`), verified at the row level (745 authors, not merely in aggregate) and confirmed specific to `hazard_ridge` by a decisively-non-invariant control on an M4-G3-inert constant. This is not "smaller than 10.9%" — it is complete closure, on two independently-derived, mechanistically-different constructions that agree with each other and with the pre-registered Part 0.5 mathematical argument.
2. **But neither arm is a CERTIFIED repair in the registration's full sense, because lean (b) MISSES decisively for both.** At c=1, both arms recover *worse* than `g3_raw_scale` by almost exactly M4-G4's own c=4 gain — because their calibration (registered, not tunable after the fact) targets the *deployed* ridge value, not `g3_raw_scale`'s weaker, specially-fit one. **This is not a flaw in the invariance mechanism** — G2 and lean (a) show the mechanism itself works exactly as derived — **it is a separate, orthogonal fact about which absolute regularization strength the per-column rule was registered to reproduce.**
3. **This outcome satisfies neither of the outer task's two named branches and is reported as such, not forced into either.** "Repair CERTIFIED" requires lean (a) HOLD *and* no loss — lean (b) fails that. "PIVOT FIRES" requires every arm to MISS lean (a) — neither does, decisively. The honest, load-bearing finding is a clean separation this leg's design was not built to prevent from happening: **invariance (the property this whole `M4-G` line has chased since M4-G1) is now fully solved, by two independent constructions, closing 100% of what M4-G4 left open; recovering `g3_raw_scale`'s specific gain is a distinct, still-open calibration question, not a further symptom of column heterogeneity.**
4. **Consequence for the line.** M4-E2 handed over "a distributed, world-specific frame displacement, no single term removable." Four legs later M4-G4 converted that into "the discovery objective regularizes a heterogeneous-scale design matrix with one scalar constant, so its behaviour inherits the whitening's units." This leg closes that chapter completely: **a per-column-aware regularizer, keyed either to the design or to the penalty, eliminates the scale-dependence entirely** — the c-invariance property this whole line was built to recover is achieved, exactly, not approximately. The open question moving forward is narrower and different in kind from anything this line has asked before: not "is there a scale-dependence and where does it live" (answered, completely), but "what absolute regularization *strength* should a scale-consistent estimator target" — a calibration-selection question, not a structural-defect question, and outside this leg's own registered scope to answer.

## Honest anomalies and disclosures

- **A `LinAlgError: Singular matrix` was caught and fixed during the smoke-test stage, before any hypothesis-relevant truth-recovery number existed.** `diagonal_ridge`'s naive formula (`ridge_j = K·var_j`, no fallback) gives `condition_0` (a literal-1 column, structurally identical to the ridge-exempt `intercept`) a ridge of exactly 0, reintroducing the `intercept`/`condition_0` collinearity the deployed scalar ridge's own uniform nonzero value was incidentally preventing. Caught on the `feedback` route during `--stage inventory`'s provable-invariance spot check (before any `--stage truth` compute had run for any world). Fixed by falling back to the plain deployed ridge value for any non-exempt, degenerate column — mirroring `column_standardized`'s own "leave a degenerate column unscaled" rule, Part 0.3 — making the two arms' degenerate-column treatment consistent by construction. Disclosed in Part 0.4 with the fix, not silently patched.
- **A diagnostic mis-labeling was caught and fixed in the same pre-compute smoke-testing pass.** An early version of the provable-invariance spot check captured `_fit_logistic_columnstd`'s first return value (`beta = coefficient_std / scale`, the un-rescaled coefficient in *original* units, which is expected to vary with c since `scale` itself varies with c) under a variable named `coeff_std` and compared it as if it were `gamma` (`coefficient_std` itself, the standardized-space fit Part 0.5 predicts is c-invariant) — producing an apparently large "gamma difference" (up to 3.1) that contradicted the (independently, separately verified) fact that the *standardized design* `design_std` was bit-identical across c. Traced to the mislabeling, not a mechanism defect, by directly re-deriving `design_std` equality (confirmed exactly 0.0 diff) before touching the comparison code. Fixed by adding an explicit `coefficient_std` return value to `_fit_logistic_columnstd` and correcting the spot-check driver to compare that value. Caught and fixed entirely within `--stage inventory` (no IRLS-heavy truth-recovery compute had run yet); the corrected check is the one reported in Part 0.5 and confirms exact invariance (0.0 gamma diff for `column_standardized`).
- **Compute cost.** `--stage inventory` (8 worlds, column inventory + G2 spread evidence + provable-invariance spot check; no IRLS-heavy fits beyond the 6 small ones the spot check itself runs): under 5 minutes. Truth stage: `endogenous_creation_expansion` was launched first, joined within about a minute by 3 more (4 concurrent) and shortly after by 2 more (6 concurrent, matching M4-G4's own established ceiling); once a slot freed the remaining 2 worlds (`topology_mismatch`, `fast_return_equal_marginal`) were launched, briefly reaching 8 concurrent against 10 available cores. Driven in the foreground in explicit chunks per this arc's standard workaround, with periodic health/progress polling (slice counts, process CPU time, error-signature greps) rather than blind waiting. Completion order and wall-clock from each world's own launch: `linear_null_ecology` first (launched 14:44:46 JST, done 14:57:43, ≈13.0 min), `fast_return_equal_marginal` second (launched ≈14:52, done 15:06:20, ≈14 min, benefiting from `linear_null_ecology`'s freed slot), then `condition_alias_ecology` (launched 14:45:06, done 15:12:58, ≈27.9 min), `endogenous_creation_expansion` (launched 14:44:30, done 15:13:18, ≈28.8 min), `source_rotated_feedback` (launched 14:44:43, done 15:13:35, ≈28.9 min), `selection_creation_compensation` (launched 14:44:40, done 15:13:39, ≈29.0 min), `history_gated_ecology` (launched 14:45:03, done 15:13:57, ≈28.9 min), `topology_mismatch` last (launched ≈14:52, done 15:16:15, ≈24 min, speeding up markedly once it had the machine largely to itself). Total wall-clock from the first launch to the last completion: ≈31.75 minutes. No world showed a Traceback, RuntimeError, LinAlgError, or Killed signal in its own log at any point during the actual `--stage truth` runs (the one `LinAlgError` encountered was during pre-compute smoke-testing, fixed before any world's truth stage was launched).

## Faithfulness chain (all green)

| gate | value |
|---|---|
| G1 anchor: `baseline`@c=1 vs M4-G4 persisted (4,096 rows) | **0.0** |
| G1 anchor: `g3_raw_scale`@c=1 vs M4-G4 persisted (4,096 rows) | **0.0** |
| G1 anchor: `covariant_var`@{.25,1,4} vs M4-G4 persisted (12,288 rows) | **0.0** |
| G1 anchor: `specificity_weight_floor`@{.25,1,4} vs M4-G4 persisted (12,288 rows) | **0.0** |
| G2: `column_standardized` design-variance spread after standardization, every c | **exactly 1.0×** |
| G2: `diagonal_ridge` ridge spread vs design's own BEFORE spread, every c | **exactly equal** |
| G3 truth-path invariance (112 checks: 14 (arm,c) combos × 8 worlds) | **0.0** |
| row-count completeness (truth: 57,344 = Σ_c 8 worlds×2 budgets×8 reps×2 views×16 authors×n_arms(c); author: 22,596) | exact match, every partial |
| valid-6-world subset, recomputed from this leg's own arm-invariant `e_orc_true` | reproduces M4-G2/M4-G3/M4-G4's own adopted set exactly |
| `specificity_weight_floor`@c=1 vs `baseline`@c=1 (structural, ridge/floor's only-difference check) | **0.0**, both budgets |
| Lean (a): `column_standardized` paired-author diff, all 745 authors, all c-pairs, both budgets | **exactly 0.0** |
| Lean (a): `diagonal_ridge` paired-author diff, all 745 authors, all c-pairs, both budgets | **1–4×10⁻¹⁴** |
| Column inventory empirical provenance check (1,050 columns, 8 worlds × 4 models) | **0 UNEXPECTED, 0 AMBIGUOUS** |

## Boundaries

Finite synthetic M4-C.2 worlds only. 8 D1 worlds (reused verbatim from
M4-G2/G3/G4); truth-recovery statistics restricted to M4-G2's own valid
6-world subset (excludes `linear_null_ecology`, `fast_return_equal_marginal`
— the pre-existing `_relative_error` near-zero-denominator fragility,
unrelated to any manipulation in this leg, reused verbatim rather than
re-derived). Truth-referenced recovery via budget-regenerated (4x/8x events)
finite panels from the frozen world law, compared to the analytic `D_true`,
exactly M4-G1/G2/G3/G4's own construction, reused unchanged. No
natural-text, personality, or clinical claim; no seal, no independent
verification (operator directive 2026-08-01). This leg answers the question
M4-G4's planner adjudication note posed (does per-column regularization
complete the repair scalar covariance took to 89.1%); it does not re-open
M4-G1's, M4-G2's, M4-G3's, or M4-G4's own leans, and it does not test any
functional-form repair beyond the two per-column mechanisms and the one
specificity control registered in Part 0. **The open question for any
future leg in this line: since invariance is now fully achieved (this leg)
and the residual is purely a calibration-anchor choice (lean (b)'s clean,
mechanistically-understood miss), whether a per-column rule calibrated to
`g3_raw_scale`'s own (better, but non-c-covariant) level — rather than to
the deployed ridge's homogeneous-limit value — can be both invariant AND at
least as good, or whether matching `g3_raw_scale`'s specific gain is itself
an artifact of that arm's own single-point calibration (M4-G3's own
diagnosed flaw) that a principled, non-tuned per-column rule should not
be expected to reproduce.**
