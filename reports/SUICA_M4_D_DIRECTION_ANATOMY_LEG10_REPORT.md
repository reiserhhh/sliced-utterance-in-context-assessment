# SUICA M4-D Leg 10 — Direction-Content Anatomy of the Discovery Step

Tier: **EXPLORATORY** (open-exploration phase, operator directive 2026-08-01).
Registered before run: docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md,
"Leg 10 — direction-content anatomy of the discovery step" (2026-08-02, loop
cycle 5, commit 3ed9f18). Script:
`scripts/run_suica_m4_d_direction_anatomy_leg10.py`. Artifacts:
`results/m4_d_direction_anatomy/`. Machinery imported bit-exactly from Legs
3/4/8/9; anchors: Leg 9 `gap_swap_rows.csv`, Leg 8 `conditioning_rows.csv` +
`lever_rows.csv`, archived V2 `metrics.csv`.

**Question.** Leg 9 pinned the residual paired gap (.215/.210/.228 in the
three high-gap worlds) to per-category ROW-DIRECTION content of the
discovered chart (oracle directions + discovered norms eliminate it; support
weights ~0). WHERE does discovery lose the directions, and is the loss
attributable — to discovery-stage estimation bias (A), to the response-safe
constraint (B), or to per-category information-operator conditioning (C)?

## Outcome in one paragraph

**Leans 1/3 (b only, and dead-center on its knife edge); the registered
pivot does NOT fire under the pre-coded rule, but only by a .0008 margin on
one disjunct — under the stricter gap-only reading it WOULD fire. The
deepest finding is a DECOUPLING: both levers move the discovered chart's row
directions substantially toward oracle (A closes ~1/3 of the direction
deficit, B ~1/2) yet the paired gap does not follow (A: +.11/−.14/−.14
"closure", i.e. worse in 2/3 worlds; B: only ~1/5 pooled). Per-world-rep,
direction improvement and gap improvement are uncorrelated (rho .22 for A,
−.13 for B; mean gap improvement under A is −.003 against a mean direction
improvement of +.132). Combined with Leg 9 (EXACT oracle directions
eliminate the gap), this says the gap is not monotone in direction
alignment: partially repaired directions buy nothing — the paired gap
behaves as an all-or-nothing functional of the direction content, which is
exactly the regime the registered hand-off instrument (perturbation analysis
of the discovery objective) exists to probe. The twice-registered
conditioning instrument arrives DOA as a predictor: the per-category
restricted conditioning profile is nearly FLAT (cond_eff 3.4–7.2 across all
48 world×category cells) and its within-world correlation with the
direction deficit is ~0 (−.21/+.15/+.09); the pooled −.39 is a
between-world Simpson artifact.**

## Design as executed (implementation decisions stated)

- **Alignment statistic (registered choice):** per-category cosine between
  off-diagonal rows of the two bases' cosine-gram matrices (full rows,
  Leg 9's direction convention), per role, averaged over the three roles;
  deficit = 1 − align. Gauge- and norm-invariant, defined across unequal
  widths (13 vs 7), no fitted cross-space map. Companions: non-constant
  columns only; subspace-level principal-angle affinity (mean cos² between
  top-q cosine-kernel eigenspaces, q = oracle kernel rank).
- **Arm A (de-biased discovery):** the lambda~1/n lever transplanted to the
  discovery stage's only inverse-covariance operation — the freeze
  whitening. `W = V_retained / sqrt(eig_retained + lambda_chart)`,
  `lambda_chart = (trace(cov)/p)/n_ref` (3.7e-4–5.7e-4 across world-reps;
  V2's retained set/rank unchanged, rank 11–12, retained eigenvalues span
  ~.29 down to ~2.6e-6 — the V2 whitening amplifies the weakest retained
  direction ~300x relative to the strongest). Chart-family selection is not
  re-run (no lambda lives there); gap refits keep V2 estimator semantics on
  both sides (Leg 9: the paired metric demands shared conventions).
  Unregistered-secondary: `A_x10` (lambda scaled 10x) and `gap_A_lam1nboth`
  (lam1n hazard on both sides at the A chart).
- **Arm B (response-safe relaxation) — RESPONSE-SAFETY RELAXED, DIAGNOSTIC
  ONLY, OPERATIONALLY FORBIDDEN (label carried on every table and every
  emitted row):** on the same reference-calibration panel the V2 chart uses,
  per-author OLS of occasion-centered responses on source-fused
  robust-standardized pre-context prototypes; SVD of the stacked coefficient
  columns → top-q response-relevant directions (q = 6 in 24/24 world-reps;
  width 7 = oracle width); then the UNCHANGED V2 freeze semantics. The only
  change is access to the panel field the safety contract withholds.
- **Arm C (conditioning elevation, the twice-registered hand-off):** Leg 8's
  information operator (final V2 oracle-basis hazard fit, forced route)
  restricted per category to span(J_k), J_k = the category's estimand
  Jacobian rows (probe machinery); cond_eff_k with the near-null cut at
  1e-8 relative to the FULL operator's lambda_max. Companions: per-category
  CR sd ratio, Jacobian near-null mass, design-pattern-span restriction.
- **Gap semantics (Leg 9's, unchanged):** forced-route V2 refits at 1x r=0;
  gap_arm = e_arm_true − e_orc_true; author-level view-mean, world median;
  closure = 1 − gap_arm/gap_v2.

## Faithfulness gates (all REFUSE-on-fail; all passed at float roundoff)

| gate | value |
|---|---|
| V2 replay vs archived metrics (72 rows) | max abs diff 1.1e-16 |
| lambda=0 whitening/basis rebuild vs frozen transform | 0.0 exactly |
| forced-route V2 gap columns vs Leg 9 `gap_swap_rows.csv` | max abs diff 2.2e-16 |
| lam1n oracle side vs Leg 8 `lever_rows.csv` (natural 1x) | max abs diff 2.2e-16 |
| Leg 8 conditioning-row replica vs `conditioning_rows.csv` (767 rows, 9 columns) | max rel diff 3.5e-16 |
| analytic D_true probe unit check | max 1.7e-15 |
| world-level gap_v2 vs Leg 8/9 persisted per-world gaps | .2150/.2102/.2283 exact |

## Gap attribution ledger (world level; author-median; closure = 1 − gap/gap_v2)

| world | gap_v2 | gap_A | closure_A | gap_B (DIAG. ONLY) | closure_B (DIAG. ONLY) | gap_A_x10 (unreg.) | gap_A_lam1nboth (unreg.) |
|---|---|---|---|---|---|---|---|
| endogenous_creation_expansion | .2150 | .1907 | **+.113** | .2077 | +.034 | .1968 | .4993 |
| selection_creation_compensation | .2102 | .2396 | **−.140** | .1501 | +.286 | .3169 | .5536 |
| source_rotated_feedback | .2283 | .2597 | **−.138** | .1771 | +.224 | .3340 | .3992 |
| POOLED (author-median) | .2152 | .2315 | −.076 | .1694 | +.213 | .3029 | .4816 |

Truth-referenced components, pooled: e_orc_true .2966; e_d_true_v2 .5695;
e_A .5840; e_A10 .6495; e_B .5030. Even the safety-relaxed, width-matched,
response-supervised chart (B) recovers only ~30% of the disc−oracle
difference in truth-referenced D error; ~4/5 of the paired gap stands.

## Direction-deficit ledger (mean deficit over roles×categories; rep-mean, world level)

| world | deficit v2 | deficit A | closure_A_dir | deficit B (DIAG. ONLY) | closure_B_dir (DIAG. ONLY) | deficit A_x10 (unreg.) |
|---|---|---|---|---|---|---|
| endogenous_creation_expansion | .4148 | .2608 | .371 | .2260 | .455 | .2423 |
| selection_creation_compensation | .3351 | .2535 | .243 | .1563 | .534 | .2582 |
| source_rotated_feedback | .3969 | .2363 | .405 | .1903 | .521 | .2507 |
| POOLED (ratio of sums) | — | — | **.345** | — | **.5008** | .3449 |

Subspace principal-angle affinity (median, cosine kernels): v2 .757–.800 →
A .812–.828, B .836–.853 — both levers also move the SUBSPACE toward
oracle, in every world.

## The decoupling (descriptive companion, post hoc, no adjudication weight)

Across the 24 world-reps, Spearman between direction-deficit improvement and
gap improvement: **A: rho = .218** (mean direction improvement +.132, mean
gap improvement −.003); **B: rho = −.133** (+.191 direction, +.066 gap).
Direction repair at the discovery stage does not translate into paired-gap
closure at ANY observed magnitude short of Leg 9's exact-oracle swap.

Note one mechanical confound for A's gap column, recorded honestly: Tikhonov
whitening shrinks the scale of weak whitened coordinates, and the V2 hazard
ridge (penalty ∝ n, scale-sensitive) then penalizes those coordinates
harder — the A gap measurement is a joint effect of better directions and a
shifted ridge operating point. The alignment measurement is
scale-invariant and unaffected. A_x10 separates the two effects: alignment
matches A (.345 vs .345 pooled closure) while the gap worsens monotonically
with shrinkage (−.076 → −.407 pooled closure) — the paired gap punishes the
unilateral convention change, not the direction content. This is Leg 9's
common-mode lesson reappearing at the chart stage.

## Per-category alignment tables (deficit = 1 − align, mean over roles, median over reps)

Arm B columns are RESPONSE-SAFETY RELAXED — DIAGNOSTIC ONLY, OPERATIONALLY
FORBIDDEN.

#### endogenous_creation_expansion

| category | deficit v2 | deficit A (de-biased discovery) | deficit A_x10 (unregistered) | deficit B (SAFETY RELAXED, DIAGNOSTIC ONLY) | log10 cond_eff (Jacobian-restricted) |
|---|---|---|---|---|---|
| 0 | 0.323 | 0.196 | 0.196 | 0.200 | 0.643 |
| 1 | 0.305 | 0.176 | 0.141 | 0.195 | 0.714 |
| 2 | 0.476 | 0.312 | 0.268 | 0.231 | 0.674 |
| 3 | 0.331 | 0.221 | 0.175 | 0.237 | 0.752 |
| 4 | 0.346 | 0.265 | 0.259 | 0.229 | 0.575 |
| 5 | 0.516 | 0.258 | 0.259 | 0.237 | 0.588 |
| 6 | 0.386 | 0.316 | 0.266 | 0.285 | 0.722 |
| 7 | 0.624 | 0.276 | 0.260 | 0.207 | 0.658 |
| 8 | 0.352 | 0.228 | 0.243 | 0.240 | 0.661 |
| 9 | 0.325 | 0.244 | 0.208 | 0.150 | 0.767 |
| 10 | 0.378 | 0.234 | 0.265 | 0.178 | 0.605 |
| 11 | 0.268 | 0.166 | 0.192 | 0.252 | 0.575 |
| 12 | 0.431 | 0.207 | 0.162 | 0.200 | 0.588 |
| 13 | 0.343 | 0.247 | 0.238 | 0.161 | 0.685 |
| 14 | 0.371 | 0.229 | 0.192 | 0.171 | 0.703 |
| 15 | 0.409 | 0.201 | 0.158 | 0.169 | 0.634 |

#### selection_creation_compensation

| category | deficit v2 | deficit A (de-biased discovery) | deficit A_x10 (unregistered) | deficit B (SAFETY RELAXED, DIAGNOSTIC ONLY) | log10 cond_eff (Jacobian-restricted) |
|---|---|---|---|---|---|
| 0 | 0.235 | 0.224 | 0.244 | 0.148 | 0.844 |
| 1 | 0.293 | 0.180 | 0.169 | 0.115 | 0.831 |
| 2 | 0.279 | 0.259 | 0.272 | 0.142 | 0.828 |
| 3 | 0.407 | 0.298 | 0.281 | 0.128 | 0.746 |
| 4 | 0.299 | 0.235 | 0.259 | 0.163 | 0.749 |
| 5 | 0.228 | 0.196 | 0.201 | 0.125 | 0.759 |
| 6 | 0.273 | 0.188 | 0.206 | 0.089 | 0.734 |
| 7 | 0.387 | 0.245 | 0.261 | 0.114 | 0.855 |
| 8 | 0.295 | 0.230 | 0.268 | 0.161 | 0.710 |
| 9 | 0.246 | 0.286 | 0.324 | 0.140 | 0.680 |
| 10 | 0.376 | 0.175 | 0.169 | 0.160 | 0.778 |
| 11 | 0.217 | 0.170 | 0.187 | 0.144 | 0.776 |
| 12 | 0.284 | 0.169 | 0.180 | 0.149 | 0.784 |
| 13 | 0.289 | 0.207 | 0.269 | 0.128 | 0.742 |
| 14 | 0.409 | 0.226 | 0.234 | 0.136 | 0.821 |
| 15 | 0.289 | 0.311 | 0.268 | 0.194 | 0.786 |

#### source_rotated_feedback

| category | deficit v2 | deficit A (de-biased discovery) | deficit A_x10 (unregistered) | deficit B (SAFETY RELAXED, DIAGNOSTIC ONLY) | log10 cond_eff (Jacobian-restricted) |
|---|---|---|---|---|---|
| 0 | 0.302 | 0.159 | 0.189 | 0.160 | 0.636 |
| 1 | 0.369 | 0.207 | 0.239 | 0.158 | 0.575 |
| 2 | 0.435 | 0.312 | 0.293 | 0.182 | 0.585 |
| 3 | 0.374 | 0.242 | 0.256 | 0.159 | 0.619 |
| 4 | 0.379 | 0.230 | 0.263 | 0.184 | 0.580 |
| 5 | 0.296 | 0.217 | 0.233 | 0.220 | 0.621 |
| 6 | 0.381 | 0.209 | 0.222 | 0.202 | 0.655 |
| 7 | 0.499 | 0.224 | 0.264 | 0.181 | 0.624 |
| 8 | 0.439 | 0.260 | 0.218 | 0.171 | 0.557 |
| 9 | 0.403 | 0.209 | 0.195 | 0.210 | 0.582 |
| 10 | 0.440 | 0.225 | 0.235 | 0.169 | 0.581 |
| 11 | 0.360 | 0.192 | 0.230 | 0.163 | 0.625 |
| 12 | 0.293 | 0.142 | 0.137 | 0.122 | 0.535 |
| 13 | 0.321 | 0.196 | 0.207 | 0.103 | 0.597 |
| 14 | 0.503 | 0.244 | 0.252 | 0.143 | 0.649 |
| 15 | 0.371 | 0.167 | 0.166 | 0.180 | 0.640 |

## Arm C — conditioning vs deficit (the twice-registered hand-off, adjudicated)

Pooled Spearman(median log10 cond_eff_k, median deficit_v2_k), 48 pairs:
**−.391**. Per world: expansion −.212, compensation +.150, rotated +.091.
Companions: CR-sd ratio +.077, pattern-span restriction +.220, Jacobian
near-null mass −.191. The restricted conditioning profile is nearly FLAT:
log10 cond_eff spans only .535–.855 across all 48 cells (condition numbers
3.4–7.2 — benign everywhere). The negative pooled value is a between-world
composition (Simpson) artifact: compensation has the HIGHEST conditioning
medians (.78) and the LOWEST deficits (.335). **Per-category information
geometry at the estimand level does not predict where the chart loses
directions — the conditioning instrument is dead as a deficit predictor.**

## Registered leans — adjudication

- **(a) MISS (0/3 worlds).** De-biased discovery closes ≥ half the paired
  gap in ≥ 2/3 worlds: closures +.113 / −.140 / −.138 — no world reaches
  .5; two of three go negative.
- **(b) HOLD (band), knife-edge; point-lean MISSES by .0008.** Safety
  relaxation closes [10%, 60%] of the direction deficit: pooled closure
  .5008 ∈ [.10, .60]. The registered point-lean ("below half — the safety
  constraint is not the main price") misses at the fourth decimal: the
  price of safety is almost exactly HALF the direction deficit. Companion:
  the same relaxation closes only .213 of the PAIRED GAP.
- **(c) MISS (sign reversed).** Conditioning-deficit Spearman ≥ .6 pooled:
  observed −.391 pooled, ~0 within worlds.

## Pivot adjudication (recorded with both readings)

Pre-coded rule (this script, before run): A attributes via lean (a); B
attributes if gap-closure ≥ .5 OR direction-closure ≥ .5; C attributes via
lean (c). Result: A no, C no, B **yes by .0008** (direction disjunct .5008;
gap disjunct .213). **The pivot does not fire under the pre-coded rule** —
verdict DIRECTION_DEFICIT_SOURCE_ATTRIBUTED_AT_LEAST_PARTIALLY (the safety
constraint accounts for ~half the DIRECTION deficit). Recorded equally
plainly: under the stricter reading of the registered pivot text ("attributes
>= half the GAP"), no arm reaches half the gap (max closure .286, one world)
and the pivot WOULD fire with verdict DIRECTION_DEFICIT_SOURCE_UNIDENTIFIED.
Either way the registered hand-off is the live next instrument:
**perturbation analysis of the discovery objective (gradient of direction
estimates w.r.t. panel composition) — registered here as the hand-off, NOT
run.** The decoupling result makes it more pointed: the instrument should
test whether the gap is a sharp (non-smooth) functional of direction content
around the oracle point, which would explain why 1/3-to-1/2 direction repair
buys zero gap.

## Honest anomalies and limits

1. **Direction–gap decoupling is the finding, and it cuts against the
   simplest reading of Leg 9.** Leg 9's exact-oracle content swap eliminated
   the gap; Leg 10 shows movement TOWARD oracle directions (by a
   gauge-invariant profile statistic AND by subspace affinity) leaves the
   gap untouched. Either the gap depends on a direction component the
   cosine-gram profile under-weights, or the gap functional is effectively
   discontinuous in direction space. The hand-off instrument distinguishes
   these.
2. **A's gap column carries a scale-ridge confound** (shrunk coordinates
   meet a scale-sensitive n-proportional hazard ridge); A_x10's monotone gap
   worsening at constant alignment shows the paired functional reacting to
   the convention change, not the content change.
3. **Rep-level gap noise is large** (world-rep gap_v2 ranges .083–.472
   within a single world); world-level closures are medians over 8 reps and
   the per-world closure signs for A are not stable rep to rep.
4. **Lean (b) sits exactly on its point-lean boundary** (.5008 vs .5) — the
   "half the direction deficit" statement should be treated as a point
   estimate with real uncertainty, not a threshold crossing (mean-of-world
   closures reads .503; both aggregations are knife-edge).
5. **Arm B is diagnostic only.** It consumes reference-panel responses that
   the operational design forbids the chart to see; nothing in this leg
   licenses a response-informed chart as an estimator.
6. Conditioning rows exclude the one degenerate author-view (767 vs 768);
   flag agreement with Leg 8 is exact.

## Boundary

Finite synthetic M4-C.2 worlds only; truth-referenced diagnostic; V1/V2
NO-GO decisions stand; no natural-text, personality, or clinical claim.
Ledger row M4-D.11 (result), EXPLORATORY tier.
