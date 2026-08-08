# SUICA M4-H2 — Is the displacement in the basis's own normalization?

Tier: **EXPLORATORY, label-free, synthetic.** Registered in
`docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md`, "M4-H2 registration
(2026-08-03, BEFORE run)". Ledger row `M4-H2`. Script:
`scripts/run_suica_m4_h2_basis_normalization.py`. Artifacts:
`results/m4_h2_basis_normalization/{decision.json, gates.json,
disp_rows.csv, g2_liveness_rows.csv, truth_recovery_rows.csv,
author_level_truth_rows.csv, g3check_rows.csv, offset_shares_by_arm.csv}`.

## 0. Where this leg picks up

M4-G7 proved, structurally and empirically at exactly 0.0, that the certified
M4-G-line repair (per-column ridge standardization) never touches
`context["v2_basis"]` — the object Leg 14's displacement is measured on — so
six legs of ridge/whitening-scale engineering could never have moved the
displacement they were opened to attack. M4-H1 then confirmed M4-E2's own
map of that displacement is valid as written (an algebraic identity: its
subspace shares are homogeneous of degree 0 in any global per-world scalar,
so M4-G2's units disqualification of the raw offset LEVEL never touched
M4-E2's SHARES). That map points at S3 (normalization/scale modes,
.2953-.3830 registered order, .4459-.5288 standalone) with the n2
column-scale family dominating inside it (.74-.79 of standalone S3), and S4
(residual) as the largest single piece. This leg asks the question M4-G7's
hand-off posed directly: does the SAME audit-then-intervene treatment,
applied one level up — to the normalization inside BASIS CONSTRUCTION rather
than the estimator's regularization — reduce the displacement itself?

## 1. Part 0 — inventory of `context["v2_basis"]`'s construction

`context["v2_basis"]` is built by `leg4._build_context` calling
`build_m4_discovered_basis` (`suica_core/m4_chart_ecology_estimator.py
:1078-1103`), which calls `freeze_m4_condition_transform`
(`suica_core/m4_condition_manifold_estimator.py:545-608`) once on
`observed.condition.reference_calibration` and then applies
`transform.transform_prototypes` (`m4_condition_manifold_estimator.py
:76-96`) to each of the three mechanism-role panels. Every normalization,
scaling, centering and reference choice on that path, in call order:

| # | step | file:line | classification | reason |
|---|---|---|---|---|
| 1 | per-source robust standardization (median-center + IQR-scale, re-applied to every later panel via the frozen center/scale) | `m4_condition_manifold_estimator.py:165` (`_fit_source`, lines 158-210); re-applied `:217-221` (`_transform_representation`) | **CANDIDATE** | genuine textbook normalization upstream of everything else; "skip it" (identity) is a clean unnormalized reading |
| 2 | chart representation family / dimensions / neighbors / landmarks / kernel bandwidth | `:294-339` (`_fit_candidate`), bandwidth applied `:286` | excluded | representation-fitting hyperparameters shared with, and fixed by, the CLOSED chart-selection line (M4-F); varying them re-derives a different chart than the one M4-E2/Leg14 anchored on |
| 3 | source-averaging (mean across the `sources` axis) | `:564` | excluded | a feature-fusion choice, not a scale/center/normalization step; no natural "unnormalized" reading |
| 4 | centering (mean over the reference panel's points) | `:565` | **CANDIDATE** | this codebase's own convention elsewhere (`_robust_scale`, every S1/S2 extraction) is MEDIAN; mean-vs-median is a clean single-axis variant |
| 5 | covariance denominator (N-1 vs N, N=96 reference points, verified below) | `:567-569` | excluded, a priori bound | a pure global scalar multiplier on every eigenvalue (96/95=1.0105, ~0.52% whitening effect after 1/sqrt) — over 47x smaller than M4-G2's smallest c-ladder step and, by M4-G2's own measured sub-linear slope (.8796) on an axis this is a micro-instance of, mechanically incapable of reaching the 25% bar; degenerate with an already-disqualified units axis |
| 6 | eigenvalue rank-retention threshold (`rank_tolerance`, `maximum_rank`) | `:574-577` | **CANDIDATE** | E2's own S3 framing ("how much spectral mass survives"); deployed `rank_tolerance=1e-6`/`maximum_rank=12` (from `configs/m4_chart_ecology.json`) |
| 7 | numerical floor inside the whitening denominator | `:582` (inner `np.maximum(eigenvalues[retained], 1e-12)`) | excluded, preflight-verified | never binds: smallest retained eigenvalue 6.7e-7 to 3.0e-6 across all 3 worlds' rep 0, i.e. 6.7e5-3.0e6x the floor |
| 8 | whitening scale (1/sqrt(eig), the unregularized amplification M4-E2 named as the largest identifiable carrier) | `:580-583` | **CANDIDATE (two variant forms)** | (a) REGULARIZED: 1/sqrt(eig+lambda); (b) UNNORMALIZED: drop the term entirely |
| 9 | constant mass ("intercept") column, literal unscaled 1.0/entry | `m4_condition_manifold_estimator.py:96`; reproduced `leg10.py:356` | **CANDIDATE** | named verbatim by M4-E2's own S3-n1 family definition ("the appended constant mass column"); deployed IS the unnormalized reading, natural variant is matched-scale |
|10 | reference panel choice (`reference_calibration`, never `reference_selection`) | `:556-563` | excluded | a data-source choice, not normalization; would break the Leg14/M4-E2 anchor contract |

**Preflight (verified numerically before any hypothesis-relevant compute).**
Chart families in force on the three registered worlds (rep 0):
`endogenous_creation_expansion` = `linear_pca`,
`selection_creation_compensation` = `global_isomap`,
`source_rotated_feedback` = `global_isomap` — both families are exercised by
the `basisvar_source_scale_off` near-duplicate fit. Reference-calibration
panel size: 96 points (2 sources x 32 authors averaged), not the 16-category
mechanism-role width — this resolves item 5's N. `retained`=12 in all three
worlds' rep 0 (the `maximum_rank=12` cap binds, not the 1e-6 relative
threshold), resolving item 6's "which constraint binds" and sizing the
`rank_tolerance=1e-3` cut (verified: retains 7/5/7 directions at rep 0,
6-10 across all 8 reps per world — a real, materially different width, not
cosmetic). Smallest retained eigenvalue 6.7e-7 to 3.0e-6 vs the 1e-12 floor,
resolving item 7.

**Six candidate steps -> six `basisvar_<k>` arms** (mirrors M4-G3's own
six-Category-A-constant inventory discipline):

- `basisvar_source_scale_off` — skip the per-source robust-scale (item 1)
- `basisvar_center_median` — median instead of mean centering (item 4)
- `basisvar_rank_tolerance_tight` — `rank_tolerance` 1e-6 -> 1e-3 (item 6)
- `basisvar_whitening_shrinkage` — 1/sqrt(eig+lambda), lambda = 0.10 x
  median(retained eig) — M4-G1's own Reading-A convention and middle rung,
  reused for continuity (item 8a)
- `basisvar_whitening_unscaled` — drop 1/sqrt(eig) entirely, M4-G1's own
  "identity" extreme control, re-run one level up (item 8b)
- `basisvar_intercept_matched_scale` — rescale the constant column to the
  whitened block's own median column-L2-norm, pooled across all 3 roles
  (item 9)

**Registered mechanistic prediction for lean (b).** All six candidate steps
are, by construction, normalization/scaling/centering choices on the exact
subspace E2 names S3 — Part 0 of this leg IS an enumeration of S3's own
generating mechanism. The registered, uniform prediction is therefore: **S3's
registered-order share falls** at the winning arm. A finer, non-adjudicating
companion (which within-S3 family the step most directly touches) is
disclosed per arm: `whitening_shrinkage`/`whitening_unscaled`/
`rank_tolerance_tight` -> n2 (column-scale); `center_median`/
`intercept_matched_scale` -> n1 (centering/mass, matching E2's own n1
definition verbatim for the intercept case); `source_scale_off` -> no
specific family (upstream of all three, least mechanically specific).

## 2. Design as executed

Arms: `deployed` (anchor, independently RECOMPUTED via this leg's own
machinery falling through to every step's deployed default, then gated to
<=1e-12 against `context["v2_basis"]` itself — not a trivial read-off) + the
six `basisvar_<k>` arms above. Worlds: Leg 14's/M4-E2's own three
`HIGH_GAP_WORLDS`, all 8 repetitions. Three metrics at every arm: (1) Leg
14's displacement gap (`disp_v2`, its own persisted formula with the arm's
basis substituted for the deployed one) — PRIMARY; (2) M4-E2's S1-S4 shares
(S1/S2 bases are ARM-INVARIANT, built once per world from Leg 10's arm-B
machinery on raw response/feature panels, never from the discovered basis;
S3 and the offset Delta ARE arm-dependent, rebuilt per arm via a disclosed
line-for-line near-duplicate of M4-E2's own inline S3 construction); (3)
truth-referenced recovery, both `TRUTH_BUDGETS = (4.0, 8.0)`, the arm's own
basis substituted into `leg4._forced_route_derivative` at the DEPLOYED
`hazard_ridge` (this leg varies the basis only, never the estimator's
regularization — that territory is the closed M4-G line's).

**Registered ambiguity resolution: metric-1 grain (disclosed, resolved
before adjudicating any number).** The outer registration's lean (a) reads
"paired-by-world CI excluding zero" literally (n=3), but G0 separately
instructs the grain be "justified... not inherited" (the fifth standing
rule). M4-G7 — the immediately preceding leg, testing the identical metric
(`disp_v2`) against the identical deployed baseline on the identical three
worlds — already resolved this exact tension: REP grain (n=24) primary,
because `disp_v2` is already a per-rep quantity, WORLD grain (n=3) a
disclosed companion. This leg adopts the identical resolution for the
identical reason on the identical metric. **Both grains were computed; they
agree on every arm's HOLD/MISS classification (Section 5), so the ambiguity
turned out not to matter to the adjudication.**

## 3. Gates

### G0 POWER
Target level cited from Leg 14's own persisted `median_disp_v2`:
18.22/16.93/18.61 across the three worlds (pooled rep-grain mean 18.06).
Metric-1 rep-grain half-widths for all six arms (0.062-0.888) sit
comfortably under the 4.51 bar (25% of the pooled deployed mean) — **no arm
is underpowered for lean (a).** Metric-2 (S1-S4 shares) is a world-level
point comparison (n=3, a census, no CI — M4-E2's/M4-H1's own convention: a
world's decomposition share is a single deterministic GPA-consensus
statistic with no finer sampling unit). Metric-3, at the winning arm, author
grain (n=384): realized half-widths 0.0172/0.0171 (4x/8x), which is
**larger** than this line's own strict `G0_FRACTION_BAR=0.01` (half of the
0.02 margin) — flagged `underpowered_vs_g0_bar: true` by that literal
criterion. Disclosed plainly, and disclosed as not undermining the
classification: the realized CI (0.257-0.291 at 4x) sits 13-14x the
margin's own width away from the ±0.02 boundary, so the OUTSIDE
classification is decisive regardless of the nominal power flag — the
`0.01` bar is a conservative standard tuned to resolve effects NEAR the
margin, and this effect is nowhere near it.

### G1 ANCHOR
`max_abs_diff_overall = 0.0` (exact), against tolerance 1e-12, across three
independent chains: (1) `deployed`'s per-rep `disp_v2` vs Leg 14's persisted
`displacement_rows.csv` — 24/24 checks, 0.0; (2) `deployed`'s `offset_norm`
+ all four share families (registered/reverse/standalone/s3-family) vs
M4-E2's persisted `offset_table` — 3/3 worlds, 0.0; (3) `deployed`'s
`e_v2_true` at budget=1.0 (this leg's own budget-regeneration machinery) vs
Leg 14's persisted `gap_rows.csv` — 3/3 spot-checks, 0.0. This is a
meaningful test, not a pass-through: `deployed`'s basis is independently
RECOMPUTED via the exact ingredients/whitening machinery every
`basisvar_<k>` arm also depends on (falling through to each step's deployed
default), so the 0.0 certifies that shared machinery end-to-end.

### G2 BASIS LIVENESS
Materiality margin: 10% of deployed's median `disp_v2` (this line's own
`G2_CONDITION_MATERIALITY_RATIO` convention). Chordal quotient distance of
each arm's own stacked frame against deployed's, per rep, median over 24
(world, rep) pairs:

| arm | median basis distance vs deployed | ratio to 10% bar | live |
|---|---|---|---|
| `basisvar_intercept_matched_scale` | 5.24 | 2.97x | yes |
| `basisvar_center_median` | 6.84 | 3.88x | yes |
| `basisvar_whitening_shrinkage` | 7.85 | 4.46x | yes |
| `basisvar_source_scale_off` | 13.93 | 7.91x | yes |
| `basisvar_rank_tolerance_tight` | 16.33 | 9.27x | yes |
| `basisvar_whitening_unscaled` | 22.29 | 12.66x | yes |

**All six arms are LIVE, by a wide margin** — smallest 2.97x the bar, none
marginal. No arm's null (if any) would be VACUOUS.

### G3 TRUTH-PATH INVARIANCE
Dual computation: `context["flat"]`-sourced calibration/selection panels vs
this leg's own freshly re-flattened budget=1.0 panels, every one of the 7
arms, one spot-check (rep, view, author) per world. `max_abs_diff = 0.0`
across 21/21 checks, against tolerance 1e-12.

### G4 MATERIALITY FORM
G0: CI-half-width-vs-bar equivalence bound per metric, underpowered
comparisons flagged explicitly (not silently read as nulls — see G0 above).
G1/G3: degenerate exact-equality checks (tolerance 1e-12), not significance
tests. G2: ratio-to-deployed-scale liveness bound (10% materiality margin).
Lean (a): paired CI-excludes-zero test AND a >=25%-of-deployed-mean
point-estimate bar, both required. Lean (b): point comparison across all 3
registered worlds (a census). Lean (c): one-sided WITHIN/OUTSIDE/AMBIGUOUS
classification against a fixed ±0.02 (upper-only) margin. No gate is a
nil-significance test on a known-nonzero quantity.

## 4. Per-arm table (all three metrics, all seven arms)

`disp_v2` = Leg 14's displacement gap, rep-grain median (n=8/world, pooled
median over 24 author-reps shown as "pooled" below is the same statistic
used for lean (a)'s point estimate — the mean, shown here — see Section 5
for the CI). S3 = registered-order share, world-level mean over the 3
worlds. `e_arm_true` = author-grain pooled mean, both budgets.

| arm | mean `disp_v2` (rep grain, n=24) | vs deployed | mean S3 share | `e_arm_true`@4x | `e_arm_true`@8x |
|---|---|---|---|---|---|
| `deployed` | 18.059 | — | 0.3368 | 0.5667 | 0.5634 |
| `basisvar_source_scale_off` | 17.898 | +0.9% | 0.3398 | 0.5463 | 0.5434 |
| `basisvar_intercept_matched_scale` | 18.620 | -3.1% | 0.3177 | 0.5735 | 0.5700 |
| `basisvar_center_median` | 16.761 | +7.2% | 0.3202 | 0.5664 | 0.5640 |
| `basisvar_whitening_shrinkage` | 12.834 | +28.9% | 0.3115 | 0.5556 | 0.5530 |
| `basisvar_rank_tolerance_tight` | 10.446 | +42.2% | 0.1700 | 0.6594 | 0.6579 |
| `basisvar_whitening_unscaled` | 6.372 | +64.7% | 0.0403 | 0.8408 | 0.8408 |

(oracle floor `e_orc_true`, for reference, pooled author grain: 0.3095/0.3084
at 4x/8x — every arm remains far above the oracle floor.)

Full per-arm, per-world numbers (offset_norm, all four share families,
GPA basin counts, width): `results/m4_h2_basis_normalization/
offset_shares_by_arm.csv`. Full per-rep `disp_v2`:
`results/m4_h2_basis_normalization/disp_rows.csv`. Full row-level truth
recovery: `results/m4_h2_basis_normalization/truth_recovery_rows.csv` /
`author_level_truth_rows.csv`.

**A visible side effect, not adjudicated by any lean:** at the winning arm,
the offset's mass that leaves S3 does not mainly land in S4 (residual) — it
lands disproportionately in S1 (safety-complement): S1's registered-order
share rises from .200-.232 (deployed) to .497-.554 (`basisvar_whitening
_unscaled`) in all three worlds, while S4 stays roughly flat (.40-.45 in
both). Removing the amplification does not just shrink the offset; it
reveals that S1 was already carrying substantial mass, now dominant once
S3 collapses.

## 5. Lean (a) — A CARRIER EXISTS

Rep grain (n=24, PRIMARY) and world grain (n=3, companion, literal-text
reading) **agree on every arm's classification** — no disagreement the
grain ambiguity of Section 2 needed to resolve.

| arm | reduction (rep grain) | 95% CI | clears 25% | CI excl. 0 | HELD |
|---|---|---|---|---|---|
| `basisvar_whitening_unscaled` | **64.71%** | [10.950, 12.423] | yes | yes | **YES** |
| `basisvar_rank_tolerance_tight` | 42.15% | [6.725, 8.500] | yes | yes | YES |
| `basisvar_whitening_shrinkage` | 28.93% | [4.635, 5.814] | yes | yes | YES |
| `basisvar_center_median` | 7.19% | [0.938, 1.658] | no | yes | no |
| `basisvar_source_scale_off` | 0.89% | [-0.543, 0.865] | no | no | no |
| `basisvar_intercept_matched_scale` | -3.11% | [-0.623, -0.499] | no | no | no (worse) |

World-grain companion reproduces the same three-arm HOLD set almost exactly
(64.54%/42.15%/29.62% at world grain vs 64.71%/42.15%/28.93% at rep grain).

**Lean (a) HOLDS. Three of six arms clear the registered 25% bar with a CI
excluding zero.** Per the registered winner-selection rule (largest
rep-grain point reduction among qualifying arms, fixed BEFORE seeing
results): **winner = `basisvar_whitening_unscaled`.**

**Disclosed, not adjudicating: `basisvar_rank_tolerance_tight` is partly a
width artifact.** This arm changes width (13 -> 6-10 depending on rep/world,
verified per-rep, not assumed uniform). Normalizing by `disp_v2/sqrt(width)`
(this line's own D2 convention, M4-G1/M4-G2): deployed 4.950, tight 3.921 —
a real but smaller **20.8%** width-independent reduction, against the raw
42.15%. The other two qualifying arms (`whitening_shrinkage`,
`whitening_unscaled`) never change width (13 in every rep, both arms), so
their reductions carry no such confound — including the winner's own
64.71%, which is a clean basis-shape effect.

## 6. Lean (b) — MECHANISTICALLY CONSISTENT

At the winner (`basisvar_whitening_unscaled`), S3's registered-order share:

| world | deployed | winner | falls? |
|---|---|---|---|
| `endogenous_creation_expansion` | 0.3323 | 0.0490 | yes |
| `selection_creation_compensation` | 0.3830 | 0.0238 | yes |
| `source_rotated_feedback` | 0.2953 | 0.0482 | yes |

Falls in all 3/3 worlds (mean 0.3368 -> 0.0403). **Lean (b) HOLDS,
decisively** — not a knife-edge, an order-of-magnitude collapse, exactly the
predicted subspace (S3), exactly as Part 0 registered before compute. The
predicted family (n2, column-scale) is the natural interpretation: dropping
1/sqrt(eig) entirely removes the whitening's own amplification directions by
construction.

## 7. Lean (c) — NOT COSMETIC

At the winner, author-grain (n=384) paired CI, one-sided WITHIN/OUTSIDE
classification against ±0.02:

| budget | mean diff (winner - deployed) | 95% CI | class |
|---|---|---|---|
| 4x | +0.2741 | [0.2568, 0.2913] | **OUTSIDE** |
| 8x | +0.2774 | [0.2603, 0.2944] | **OUTSIDE** |

World-grain companion agrees in sign and magnitude: +0.307 [0.212, 0.401]
(4x), +0.303 [0.172, 0.434] (8x). **Lean (c) MISSES, decisively** — the
CI's own width is 0.034/0.034, and it sits entirely 12-14x the ±0.02
margin's width away from the boundary on the WORSE side. This is not a
knife-edge miss.

## 8. Dose-response companion (disclosed, non-adjudicating)

The registration's winner-selection rule (largest reduction) is fixed and
was not revisited after seeing lean (c)'s MISS. But the full truth-recovery
comparison against deployed, computed identically for every arm that
cleared lean (a) (not only the winner), sharpens the finding into a clean
monotone dose-response — structurally identical to M4-G1's own headline
finding, one level up in the pipeline:

| arm | offset reduction | mean diff vs deployed @4x | 95% CI | class |
|---|---|---|---|---|
| `basisvar_whitening_shrinkage` | 28.9% | **-0.0111** | [-0.0169, -0.0054] | **WITHIN** (genuinely better) |
| `basisvar_rank_tolerance_tight` | 42.2% | +0.0927 | [0.0731, 0.1123] | OUTSIDE |
| `basisvar_whitening_unscaled` | 64.7% | +0.2741 | [0.2568, 0.2913] | OUTSIDE |

The MILDEST of the three qualifying arms is the ONLY one whose recovery does
not merely avoid worsening — its CI sits entirely on the BETTER side of
zero, comfortably within the ±0.02 margin. Spearman(reduction_pct,
`e_arm_true`@4x) across all six basisvar arms = **+0.600** (descriptive,
n=6, p=.208, not a registered test) — more reduction associates with worse
recovery, the same-signed finding as M4-G1's own Spearman(offset level,
error) = -0.786 on the downstream copy (a positive correlation between
REDUCTION and ERROR is the same relationship as a negative correlation
between remaining OFFSET LEVEL and error). Smaller n here (6 vs 7) and a
different intervention family, so the magnitude is not directly comparable,
but the direction and the qualitative pattern — minimizing the registered
target past a mild point makes the objective worse at its job — reproduce
exactly.

A companion observation on WHY: at the winning arm, GPA basin diversity
often collapses (e.g. `basisvar_rank_tolerance_tight` and `basisvar_center
_median` converge to as few as 1 distinct basin of 8 starts on some worlds,
vs deployed's typical 7-8) — the altered bases sit closer together in the
chordal quotient than the deployed ones do. Reported as a side observation,
not adjudicated by any lean.

## 9. Verdict

**PIVOT DOES NOT FIRE** (lean (a) holds — three of six arms clear the 25%
bar with a CI excluding zero). Per the registration's own framing, this
leg's outcome sits in the "carrier found" branch, and both parts of that
branch's required disclosure are answered plainly:

**The carrier is named:** `basisvar_whitening_unscaled` — dropping the
whitening's 1/sqrt(eig) scale entirely from the SAME code path that builds
`context["v2_basis"]` (`m4_condition_manifold_estimator.py:580-583`).
**It closes 64.71% of Leg 14's gap** (rep grain; 64.54% world grain), the
largest reduction of any arm tested, at exactly the reduction where the
basis stops "amplifying weak directions" and starts equal-weighting them.

**Lean (b) DOES certify it as the registered mechanism, not a number moving
for unknown reasons:** S3's share collapses by an order of magnitude in
3/3 worlds, exactly the subspace Part 0 predicted before compute, exactly
the family (n2) the step's own definition names.

**But lean (c) says this specific carrier is not safe to adopt.** Truth-
referenced recovery at the winning arm does not merely fail to improve — it
collapses (mean error rises from ~.565 to ~.841, both budgets, both grains,
CI 12-14x outside the registered margin). **Verdict:
`CARRIER_FOUND_MECHANISM_OR_TRANSFER_UNCERTIFIED`** — structurally the same
finding this line reached at M4-G1, one level up: the displacement IS
reducible at the basis-construction level, the reduction IS mechanistically
real and exactly where Part 0 predicted it, and it is COSMETIC at the arm
that reduces it most. The dose-response companion (Section 8) shows the
mildest qualifying arm (`basisvar_whitening_shrinkage`, 28.9% reduction)
does not share this problem — its recovery is genuinely, statistically
better than deployed's, WITHIN the no-loss margin — but per the registered
adjudication rule that arm is not "the winner," and no post-hoc rescue
re-scores it as one.

## 10. Mechanical notes

One process note, disclosed as the standing convention requires: the first
`--stage oracle` invocation exceeded the harness's 120s default foreground
timeout and was auto-moved to a background task by the tool layer (not a
choice made by this agent, and not a monitor built to wait on it — the
harness's own completion notification was read once). Every subsequent
compute stage was invoked with an explicit long timeout and completed
synchronously in the foreground, as the process rules require. No other
mechanical problems: all context builds, the arm-invariant oracle stage, the
G3 spot-check stage, all 21 (world, arm) compute stages, and the assemble
stage completed with zero Tracebacks or RuntimeErrors, first attempt.

An efficiency fix made BEFORE any hypothesis-relevant number existed:
`_regen_for_budget` (world-regeneration for the truth-recovery budgets, the
single most expensive per-call operation at ~6-13s) is ARM-INVARIANT but was
initially called once per arm; a disk cache
(`_context_cache/regen_{world}_r{rep}_b{budget}.pkl`) was added so it
computes once per (world, repetition, budget) and is reused by all seven
arms, cutting the arm-stage wall-clock from ~190s to ~15-28s per (world,
arm) after the first arm of each world. This is a pure performance change;
it does not touch any computed number (verified: the `deployed` arm's
numbers, computed both before and via the cache, are bit-identical to
M4-E2's and Leg 14's own persisted values, Section 3's G1 ANCHOR).

## 11. Hand-off

`basisvar_whitening_unscaled` is now a second confirmed instance, at a
different location in the objective (basis construction, not estimator
regularization), of this program's recurring pattern: an intervention that
looks decisive on the discovery objective's own displacement metric and is
destructive to truth-referenced recovery. The dose-response in Section 8
suggests the SAFE direction is mild, not aggressive — `basisvar_whitening
_shrinkage` (28.9% reduction, recovery genuinely improved) is the natural
next candidate for a leg that registers a narrower shrinkage ladder around
this step specifically, mirroring M4-G1 -> M4-G3's own narrowing move, but
this time on the basis-construction path rather than the downstream ridge.
Separately, and per the registration's own framing for a leg where the
PIVOT does not fire: since a carrier WAS found (even if uncertified), the
open question the registration reserved for a firing pivot — whether the
CONSENSUS/ALIGNMENT step is the remaining candidate — is not reached by this
leg's own registered branches and is not claimed here; it remains available
as a next question precisely because THIS leg's own carrier is disqualified
on safety grounds, not because basis normalization was exonerated.
