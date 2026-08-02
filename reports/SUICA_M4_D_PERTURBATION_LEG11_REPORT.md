# SUICA M4-D Leg 11 — Perturbation Analysis of the Paired Functional at the Oracle Point

Tier: **EXPLORATORY** (open-exploration phase, operator directive 2026-08-01).
Registered before run: docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md,
"Leg 11 — perturbation analysis" (2026-08-02, loop cycle 6, commit 0e81907).
**This is the designated FINAL LEG of the M4-D arc.** Script:
`scripts/run_suica_m4_d_perturbation_leg11.py`. Artifacts:
`results/m4_d_perturbation/`. Machinery imported from Legs 3/4/8/9/10;
anchors: Leg 9 `gap_swap_rows.csv` (t=0), Leg 10 `gap_world_table.csv` (t=1),
archived V2 `metrics.csv`.

**Question.** Leg 9 showed EXACT oracle row directions eliminate the paired
gap; Leg 10 showed partial direction repair buys ~nothing. Is the paired gap
therefore a NON-SMOOTH (all-or-nothing) functional of direction content near
the oracle point — a cliff with an identifiable discrete decision flipping at
its knee — or is it smooth, in which case the all-or-nothing reading is wrong
and the residual is genuinely distributed object-level direction content?

## Outcome in one paragraph

**THE REGISTERED PIVOT FIRES: gap(·) is SMOOTH — the all-or-nothing reading
is WRONG, and it is recorded plainly as wrong.** Along the frame-manifold
geodesic from the oracle point (Leg 9's swap_i basis, t=0) to the discovered
chart (t=1), the world-median gap rises gently and CONVEXLY: only 4.5–8.4%
of the full rise has happened by t=.2 (lean bar: 50%), 73–79% of it happens
beyond t=.4, and the maximum local slope is 1.29–1.37x the mean slope
(smoothness bar: 3x) — no interval carries a jump. The angular arm sharpens
this at the origin: gap(theta) follows a clean power law ~ theta^1.8
(exponents 1.84/1.76/1.87), i.e. the paired functional is not merely
continuous at the oracle point — it is FLAT there (near-quadratic basin,
vanishing first derivative): 5-degree perturbations of every row direction
cost only 6.7–9.2% of the discovered chart's gap. The discrete-event
instrumentation completes the picture from inside: the paired evaluator's
only hard internal switches (IRLS weight floor, logit clips) are INERT along
the entire path — the soft-assignment functional (floor and clips removed on
both sides) reproduces the hard curves to 1e-12, so NOTHING discrete gates
the gap; the registered families that do flip (the would-be route selection,
the p>=.5 association mask) are shadow decisions that never enter the
functional. Leans 1/3: (a) MISS 0/3 under both readings; (b) HELD under the
pre-coded rule but exposed by its own pre-coded ubiquity companion as
NON-SPECIFIC (the association mask flips in ~100% of row-intervals, so it
"co-occurs" with everything); (c) MISS — removal 7e-15/1.9e-12/-5e-12, the
diagnostic causally REFUTES (b)'s family. Consequence for the arc: Leg 10's
decoupling was PATH ANISOTROPY, not a cliff — the residual ~.21–.23 gap is
genuinely distributed direction content, accrued smoothly along the whole
frame displacement. THE ARC CLOSES.**

## Design as executed (implementation decisions stated)

- **Geodesic (Arm A).** The paired functional consumes the three role bases
  only through the row-Gram kernel of the stacked frame
  S = [B_cal; B_sel; B_eval]: `_hazard_design` is linear in basis rows, the
  IRLS ridge is uniform on every basis-derived column (only the design
  intercept is exempt), and the readout probes are basis-linear — so the
  functional is invariant under right-orthogonal maps and zero-column
  padding, and the frame manifold is the Kendall size-and-shape quotient.
  The geodesic between orbits is the straight segment between optimally
  aligned representatives: S(t) = (1−t)·S0_pad + t·S1·R*, with R* = UV'
  from the SVD of S1'S0 (Procrustes). t=0 is Leg 9's swap_i (oracle
  directions + discovered norms, width 7, zero-padded to 13); t=1 is the
  discovered v2 basis. Both invariances were EMPIRICALLY GATED per
  author-view (padding <= 1.4e-13, rotation <= 7.1e-12 relative D error);
  endpoint curve values were computed at the raw representatives and
  bit-anchored to the persisted rows.
- **Angular perturbations (Arm B).** Pure oracle basis; for every (role,
  category) the FULL row (Leg 9's direction convention) is rotated by
  exactly theta in the plane spanned by the row and a random orthogonal
  direction; norms preserved exactly. 8 draws per world-rep; one plane set
  per draw swept across all five angles (common random numbers). theta=0 is
  the exact oracle point (gap = 0 by the Leg 9-gated refit identity).
- **Discrete-event instrumentation (Arm C).** Enumerated from the evaluator
  code. Registered families (adjudicated): category association (fitted
  p >= .5 cells of the stacked cal+sel design at the final coefficient),
  route agreement (the route the V2 selection rule WOULD pick at basis(t) —
  verbatim `_fit_v2_stack` semantics — vs the forced oracle route),
  support-cell membership (cells with fitted p(1−p) < 1e-4, i.e. floored
  weight). Companions (logged, no adjudication weight): fit/readout logit
  clips at |z| >= 20, IRLS iteration count (early stop 1e-10), readout sign
  pattern, plus the path-invariant gate indicator and degenerate flags.
  **Honesty line drawn in advance:** under the ORACLE-FORCED route, the
  would-be route and the association mask are SHADOW decisions — they do
  not enter the computed functional; the functional's only hard internal
  nonlinearities are the weight floor, the logit clips, and the early stop.
- **Soft-assignment diagnostic (unregistered-secondary, loud label).** Two
  variants along the full path: soft-support (no weight floor, no logit
  clip, fit and readout, BOTH sides) and soft-route (score-softmax mixture
  of per-route derivatives, T = .01, symmetric on both sides; base/return
  contribute D = 0 exactly). DIAGNOSTIC ONLY — not deployable estimator
  semantics.
- **Gap semantics (Leg 9, unchanged):** forced-route refits at 1x r=0;
  gap = e_arm_true − e_orc_true; author level = view mean; world level =
  median over author-reps. 3 high-gap worlds x 8 reps; 5,376 gap(t) rows,
  30,720 gap(theta) rows, 5,376 discrete-event rows, 5,376 soft rows.

## Faithfulness chain (all gates green, refused-not-warned)

| Gate | Value |
|---|---|
| V2 replay vs archived metrics (72 rows) | 1.1e-16 |
| analytic D_true unit check | 1.7e-15 |
| instrumented IRLS copy vs canonical coefficient | 0.0 (bit-equal) |
| instrumented readout vs canonical `_feedback_derivative` | gated <= 1e-15 every call |
| t=0 rows vs Leg 9 persisted swap_i (e_i_true, gap_i) | 9.7e-17 |
| t=1 rows vs Leg 9 persisted v2 (e_d_true_v2, gap_v2, e_orc_true) | 2.2e-16 |
| zero-padding invariance at t=0 (relative D error) | 1.4e-13 |
| rotation invariance at t=1 (relative D error) | 7.1e-12 |
| world medians t=0 vs Leg 9 / t=1 vs Leg 10 table | exact to print precision (−.0199/+.0052/−.0096; .2150/.2102/.2283) |
| degenerate rows | 1 (flag-identical to Leg 9) |

The empirical padding/rotation gates certify the kernel-invariance premise
of the quotient-geodesic construction on every author-view; the persisted-row
anchors simultaneously certify the instrumented IRLS copy end-to-end.

## gap(t): the geodesic curves (world medians)

| t | expansion | compensation | rotated |
|---|---|---|---|
| 0.00 | −.0199 | +.0052 | −.0096 |
| 0.05 | −.0167 | +.0045 | −.0084 |
| 0.10 | −.0125 | +.0061 | −.0026 |
| 0.20 | −.0003 | +.0144 | +.0071 |
| 0.40 | +.0353 | +.0475 | +.0553 |
| 0.70 | +.1259 | +.1307 | +.1303 |
| 1.00 | +.2150 | +.2102 | +.2283 |

| statistic | expansion | compensation | rotated | bar |
|---|---|---|---|---|
| early rise share (t <= .2) | 8.4% | 4.5% | 7.0% | >= 50% (lean a) |
| rise share t <= .4 | 23.5% | 20.6% | 27.3% | — |
| rise share t > .4 | 76.5% | 79.4% | 72.7% | — |
| max interval slope / mean slope | 1.287 | 1.353 | 1.372 | < 3 (smooth) |
| max-slope interval | .4→.7 | .4→.7 | .7→1 | — |
| smooth flag | YES | YES | YES | — |

Interval slopes rise monotonically (expansion: .065/.083/.123/.178/.302/.297)
— a smooth CONVEX ramp, no jump anywhere. The heaviest cost sits in the far
60% of the path.

## gap(theta): the angular curves (world medians, 8 draws/rep)

| theta | expansion | compensation | rotated |
|---|---|---|---|
| 1° | .0008 | .0011 | .0007 |
| 2° | .0033 | .0035 | .0026 |
| 5° | .0183 | .0192 | .0152 |
| 10° | .0655 | .0659 | .0545 |
| 20° | .1941 | .1968 | .1744 |

- theta=5° share of the discovered chart's gap: 8.5% / 9.2% / 6.7%
  (lean-a angular bar: 50%) — MISS by a factor of ~6.
- log-log exponents over 1–20°: **1.842 / 1.764 / 1.871** — gap(theta) ~
  theta^1.8, a near-quadratic basin: the paired functional has ~vanishing
  first derivative at the oracle point. Perturbing EVERY row direction of
  the oracle frame by 2 degrees costs ~.003 of gap (~1.5% of the wall).
- Deficit-matched consonance (companion): at matched direction-deficit
  magnitudes the two perturbation families produce gaps of the same order
  and shape (e.g. deficit ≈ .028/.032: A-path rise .042–.065 vs theta-arm
  .054–.066), so locally the functional responds to deficit magnitude
  comparably under two very different perturbation geometries.

## What the discrete instrumentation found (Arm C)

- **The functional's own hard switches are INERT.** Median floored-cell
  count along the path: 0 (a single 1-cell median at expansion t <= .1);
  readout clips: zero everywhere; fit clips flip in only 1.4–7.5% of
  row-intervals. Decisively: the soft-support functional (floor and clips
  removed on BOTH sides) reproduces the hard gap curves to **1e-12 at every
  t in every world** — no discrete internal decision shapes gap(t) at any
  point on the path, knee or no knee.
- **Shadow decisions drift smoothly, gate nothing.** The would-be route
  agreement with the forced route decays gradually along the path
  (.76→.45 / .83→.64 / .73→.50 from t=0 to t=1) — real drift, no jump, and
  irrelevant to the forced-route functional. Note the t=0 values: even at
  the oracle-directions point the shadow selection already disagrees with
  the oracle-basis route for 17–27% of author-views.
- **Lean (b)'s isolation is a ubiquity artifact, exposed by its pre-coded
  companion.** Co-occurrence shares: category_association ~1.00 in all
  three worlds (route .15–.20, support .36–.48) — "exactly one family
  >= .5" holds, so the pre-coded rule adjudicates HELD, same family, 3/3
  worlds. But the flip-density companion (pre-coded precisely as this
  guard) shows the association mask flips in **99.7–100% of ALL
  row-intervals** — with ~13k cells per fit, some cell crosses p = .5 in
  every interval — so under a smooth rise the co-occurrence numerator
  saturates trivially. The isolation is non-specific: there is no knee
  event to co-occur with.
- **Lean (c) causally refutes (b).** The matching soft variant
  (soft-support: the association mask thresholds exactly the logits the
  floor/clips act on; nearest causal analog, stated in advance) removes
  NOTHING: removal = 7.2e-15 / 1.9e-12 / −5.0e-12 at the max-slope
  intervals. MISS — and this miss is informative: it is the direct
  demonstration that no soft-assignment repair exists because no hard
  assignment was ever binding.
- Companion: the soft-route mixture (T=.01) tracks the hard curves closely
  at small t and WORSENS the endpoint in expansion (t=1: .325 vs .215) —
  wrong-route derivative components contaminate the mixture; consistent
  with Leg 5's route-mix lesson; diagnostic only.

## Per-lean adjudication (pre-coded rules)

| Lean | Statement | Result |
|---|---|---|
| (a) | gap jumps >= half its full value by t <= .2 (geodesic) or theta <= 5° (angular) in >= 2/3 worlds | **MISS 0/3 on BOTH readings** (early shares .045–.084; theta-5° shares .067–.092) |
| (b) | C isolates a single flipping decision family in >= 2/3 worlds (same family) | **HELD as pre-coded** (category_association, 3/3) — **but non-specific**: flip density ~100% saturates the co-occurrence rule under a smooth rise; shadow decision, does not enter the functional |
| (c) | the matching soft variant removes >= half the knee jump where (b) isolated | **MISS** (removal ~1e-12; soft == hard; the hard switches never bind) |

**Leans 1/3.** The held lean is the one whose own companions and diagnostic
refute its causal reading; recorded exactly so.

## PIVOT: FIRES — the verdict per world

Pre-coded rule: lean (a) misses under both readings AND >= 2/3 worlds have
early share < .5 with max/mean slope < 3. All three worlds are SMOOTH
(1.29/1.35/1.37 vs bar 3). **Verdict: SMOOTH_GAP_ALL_OR_NOTHING_READING_WRONG
in 3/3 worlds — no knee anywhere, nothing flips because nothing discrete is
load-bearing.**

What this corrects: Leg 10's "effectively all-or-nothing" reading (adopted
after partial direction repair bought no gap closure while Leg 9's exact
swap eliminated it) is WRONG as a statement about the functional. The
functional is smooth and locally flat at the oracle point; along the
geodesic, partial displacement buys proportionate (and early-discounted)
gap. Leg 10's decoupling is therefore PATH ANISOTROPY: the whitening-lever
and safety-relaxation paths moved the frame in directions whose alignment
gains did not translate into functional gains — the scalar deficit statistic
is not a path coordinate, and different frame paths with equal deficit
closure have very different gap outcomes. The residual ~.21–.23 paired gap
is hereby recorded as **genuinely distributed object-level direction
content**: it accrues smoothly across the whole oracle-to-discovered frame
displacement (73–79% of it beyond t=.4), is gated by no discrete event, and
admits no soft-assignment repair.

## Honest anomalies

- Two worlds dip marginally BELOW their t=0 value early on (compensation
  −.0007 at t=.05; several rep-level dips to ~−.007): the swap point is not
  exactly the path minimum. Magnitude ~.007 max, far below effect scale;
  consistent with Leg 9's finding that swap_i slightly BEATS the oracle
  refit.
- Lean (b) is adjudicated HELD because the pre-coded rule says so, while
  every surrounding measurement says the isolation is vacuous. The rule's
  weakness (co-occurrence saturates for ubiquitous flippers) was
  anticipated and its guard (flip density) pre-coded; both are reported.
- The one degenerate author-view (compensation, forced route `return`) is
  excluded exactly as in Legs 9/10 (flag-identical).
- rot-invariance gate max 7.1e-12 (not bit-zero): the IRLS early-stop
  ell-infinity criterion is not rotation-invariant; documented in the
  script, absorbed by the 1e-6 gate with 5 orders of headroom.

## Arc closure and hand-off

Leg 11 is the arc's designated last leg. Its registered hand-off is:

1. **The arc-final synthesis is the PLANNER's job** — fold this leg's
   correction (smooth, convex, no discrete gate; all-or-nothing DEAD; the
   residual gap = distributed object-level direction content) into
   docs/SUICA_M4_D_LOOP_WALL_SYNTHESIS.md as its closing addendum.
2. **The loop's standing queue** (registered before this run, unchanged):
   two-stage retrofit of the C.3 attribution NO-GO; R->V bridge
   heteroscedastic calibration.

## Boundaries

Finite synthetic M4-C.2 worlds only; truth-referenced diagnostic (oracle
basis, forced routes, analytic D_true); V1/V2 NO-GO decisions stand; soft
variants are diagnostic only, never deployable estimator semantics; no
natural-text, personality, or clinical claim; no seal, no independent
verification (operator directive 2026-08-01).
