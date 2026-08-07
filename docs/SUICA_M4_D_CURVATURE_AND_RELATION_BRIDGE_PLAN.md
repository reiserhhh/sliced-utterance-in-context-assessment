# M4-D — Composition Curvature and the Relation-to-Individual Bridge (plan, 2026-08-01)

Tier: OPEN-EXPLORATION THEORY DEVELOPMENT (operator-directed: defensive machinery
deferred until theory completion; light leans recorded here before runs; no
adversarial verification pass in this phase). Successor to the M4-C NO-GO wall and
the route index's two unstarted mainline items ("mechanism composition" beyond
grammar, "individual-to-relation bridge").

## Leg 1 — the curvature conjecture (why loops fail when atoms pass)

Observed wall: M4-C.2 V2 atomic-action transport passes (.77-.98) while the
composite loop fails (.652, NO_GO_CHART_TRANSPORT); all four repair attempts
(RBF -.1386, Fisher-Wiener 25.4%, information frontier 44%, attribution cube)
NO-GO. Conjecture: this is not estimator noise but GEOMETRY — per-atom transports
T_i are each chart-consistent only up to gauge, and a composed loop accumulates a
holonomy defect. Prediction (the testable law): per-loop transport failure is an
increasing function of accumulated atom-pair non-commutation
sum_ij ||[T_i, T_j]||_F along the loop, with near-zero-commutator loops
transporting as well as their atoms.

Leans: (a) commutator magnitude explains >= half the variance in per-loop
transport error across the existing M4-C.2 synthetic worlds (Spearman >= .7);
(b) the loop error is reduced by path-ordered correction (estimate a connection,
parallel-transport before composing) in worlds where (a) holds; (c) in the world
family where atoms genuinely commute, loops pass at atom-level rates. If (a)
fails (< .3), the curvature reading is wrong and the wall is estimator-side after
all — record and pivot.

Machinery: reuse m4 chart-ecology generators + the M4-A composition grammar's
non-commutation term; new analysis script only.

## Leg 2 — relation-determined individuality (when does R license V?)

The program-wide pattern: signal lives in R (E4/P6 author alignment; V8 bridge
relation structure — exploratory, post-hoc, on spent labels) and dies in V
(direct trait prediction ~0; X1: motion structure real but not person
parameters). V8's type system forbids silent R->V conversion; the OPEN THEORY
QUESTION is the licensed version: under what conditions does a relation field
R_uv determine individual coordinates V_u up to gauge (isometry/reference choice)?

Formal skeleton: treat R as noisy observations of a Gram/EDM object; reconstruction
identifiability = rank + noise + anchor conditions (Euclidean distance geometry).
The v8_vanishing_individuality group-only worlds are the designed NULL (author AUC
high, individuality zero -> R must NOT license V there). Deliverable: a
reconstruction-identifiability criterion computable from observed R alone
(spectral gap / rigidity index), validated across planted worlds spanning
{individuality present, group-only, mixed}, with the criterion's decision compared
to ground truth reconstructability.

Leans: (a) a spectral-gap-based rigidity index separates reconstructable from
non-reconstructable worlds with AUC >= .9; (b) in group-only worlds the index
correctly refuses (V-reconstruction error at chance) despite high author AUC —
i.e., the index is NOT fooled by the vanishing-individuality trap; (c) noise
threshold behavior matches the EDM perturbation bound qualitatively.

Machinery: v8_vanishing_individuality generators + new EDM/Gram analysis module.

## Recording rule for this phase

Each leg writes one report + one ledger row with actual numbers and lean
adjudication (hold/miss recorded as always); no prospective seal, no independent
verification pass (deferred to the post-theory defense phase); nothing here may be
cited above EXPLORATORY tier.

## Leg outcomes (2026-08-01, appended) and Leg 3 registration

**Leg 1: curvature conjecture NOT SUPPORTED — clean negative, all three leans miss.**
Pooled Spearman(kappa, loop error) .6977 (knife-edge vs .70) but WITHIN world-rep
cells the commutator does not rank failures (median rho .103 — the pooled number is
ecological); path-ordered correction makes loops WORSE (median relative reduction
-.2815); the commuting-knob construction cannot move the commutator (1.377->1.383)
yet loop geometry rises .523->.683 as model-selection flips fall 36->22 — transport
improves at constant commutator, a direct dissociation. The wall is ESTIMATOR-SIDE:
15.3% hazard model-selection flips (discovered route picks `return`, forcing D=0 and
loop error 1, where the oracle picks feedback/gate); flip count predicts world-rep
loop geometry at rho = -.8044 (vs kappa's -.30); within cells the chart-free D-leg
error ranks author loop error (median rho .699); mechanism: discovered charts
OVERSPAN the oracle frame (widths 12-13 vs 7), inflating the hazard feedback
parameterization; the one low-overspan world (history_gated, width 8, 5 flips)
passes at .915. V1/V2 NO-GOs stand; curvature reading closed.

**Leg 2: R->V bridge PARTIAL — (b),(c) hold, (a) misses.** Rigidity index licenses
R->V at tau=.5; group-only refusal 200/200 with zero false licenses (not fooled by
the vanishing-individuality trap; author AUC .84-.90 there while index .004-.075);
knee/gap-closure adjacent grid points. (a) pooled AUC .8691 vs registered .90 —
localized to the hard-refusal noise band + one knife-edge cell; at stricter label
margin .929 (index encodes a stricter standard than the registered 2x criterion);
adjudicated on the registered margin: miss. Bonus controlled reproduction of the
F18 pattern: c2_joint eps=1.5 gives within-group author AUC .9933 with index .017 —
near-perfect detection, zero licensable coordinates, now a PLANTED-WORLD phenomenon.

## Leg 3 — overspan-controlled route identification (attacking where the wall
## actually lives; registered before run)

Target: Leg 1's pivot profile says the composite-loop wall is caused by chart
OVERSPAN inflating the hazard feedback parameterization, flipping route selection
to `return` (D=0). Existence proof that low overspan passes: history_gated
(width 8, 5 flips, .915).

Design: add width/parsimony control to chart estimation (candidate mechanisms, in
registered order: (i) rank/width selection on the chart frame by the same
negative-spectrum floor used in the Leg-2 bridge; (ii) penalized hazard fit;
(iii) route selection by out-of-fold route-specific predictive score instead of
in-fold fit). Rerun the exact V2 loop battery per arm.

Leans: (a) width control cuts model-selection flips by >= half (196 total -> <= 98);
(b) loop transport geometry crosses the original .75 NO-GO bar in >= 3 of 5 worlds
(currently 1 of 5); (c) mediation: the width-arm's loop improvement is carried by
D-leg error reduction (within-cell rho between width-arm D-leg improvement and loop
improvement >= .5). Pivot-if: flips drop but geometry does not follow (< .70 pooled)
— then the D-leg error is not selection-driven and the wall has a third layer;
profile it.

## Leg 3 outcome (2026-08-01, appended) and Leg 4 registration

**Leg 3: PARTIAL — route stabilization without transport recovery; third layer
identified.** Winning arm arm2_penalized (ridge on hazard feedback/gate, lambda .005
by the registered OOF rule): flips 196->148 (-24.5%, lean (a) MISS vs halving), pooled
geometry .6519->.6886, worlds >=.75 still 1/5 (lean (b) MISS), D-leg mediation HOLDS
(rho .61/.74, lean (c)). Pivot PARTIALLY TRIGGERED (strict letter fires: flips drop,
pooled .6886 < .70). Third-layer profile: un-flipped rows recover only to median
e_loop .78; non-flip error floor flat (.6705->.6634); within cells D-leg error ranks
remaining loop error (rho .69) over GC (.44); oracle-D substitution leaves .41 vs
oracle-GC .45. **Route identification is necessary but nowhere near sufficient — the
third layer is D-LEG (creation-derivative) ESTIMATION ERROR AT THE CORRECT ROUTE**,
which reconnects to the four M4-C.3.x creation-estimator NO-GOs as one persistent
bottleneck. Two disclosed leads: (i) span must MATCH, not shrink — rank-matching !=
subspace-matching (width-7 truncation still dropped mechanism directions, flips
1->12); (ii) the OOF-likelihood lambda rule is the binding constraint on arm 2 (rule
is monotone in lambda, picked the grid boundary .005; an unregistered lambda=.125
smoke showed far stronger stabilization — unlicensed, needs registered extension).

## Leg 4 — is the D-leg floor structural or estimator-limited? (registered before run)

Two parts, one script battery, same V2 worlds:

**4a (lambda-grid extension, closes the arm2 question).** Extend the ridge grid to
{.005,.025,.125,.625,3.125} with the SELECTION RULE CHANGED as registered here:
choose lambda by out-of-fold ROUTE-IDENTIFICATION ACCURACY (not raw likelihood, which
Leg 3 showed is monotone and binds at the boundary); rerun the full battery at the
selected lambda. Leans: (a4a) flips <= 120 at the new selection; (b4a) pooled
geometry >= .70. Soft: if route-accuracy selection also binds at a boundary, report
the full lambda-response curve and call the mechanism saturated.

**4b (D-leg resolution scaling — repair path vs limit theorem).** At the correct
(oracle-forced) route, measure achievable D-leg error vs event budget: rerun creation
estimation at event budgets {0.5x, 1x, 2x, 4x} of the V2 default per world-rep, with
the oracle-route fixed, and fit the scaling of median e_d vs budget. Leans: (a4b) if
e_d scales ~ budget^(-1/2) (estimator-limited), the M4-C.3.x wall is a BUDGET
problem — record the projected budget to reach e_d <= .25 and the wall becomes a
resource theorem; (b4b) if e_d plateaus by 2x (structural floor), record a RESOLUTION
LIMIT for creation estimation at this observation design (the T4-style economics
statement for the D leg) — either outcome is a theory deliverable, there is no bad
result here. Kill: none (mapping experiment). Tier: EXPLORATORY, open-exploration
phase rules.

## Leg 5 — two-stage route-then-refit estimation (registered before run, 2026-08-02)

Target: the trade-off law (synthesis section 2). If route selection and creation
estimation are competing objectives at a single lambda, decouple them: STAGE 1
selects the route exactly as Leg 4a's winning configuration (ridge lambda=.125,
route-accuracy-selected — flips 73 by construction, unchanged); STAGE 2 refits the
creation derivative (and the GC legs where the estimator couples them) at the
STAGE-1-selected route with the V2 baseline (unpenalized) estimator. Loop transport
recomputed from stage-2 fits. Secondary arm (cheap, licenses the Leg-4a discovery
observation): single-stage lambda=.025 full battery (the discovery-loop-geometry
peak; one grid point).

Leans: (a) stage-2 median e_d at selected routes returns to <= .55 (from .783 under
the flip-optimal ridge; baseline .487); (b) pooled loop geometry >= .70 (missed
twice by .01 hairs — this is the decisive test of whether the D-distortion was the
binding path on route-stabilized rows); (c) worlds >= .75: 2-3 of 5 (band, honest
uncertainty; currently 2/5 under 4a). Pivot-if: (a) holds but (b) misses again —
then D-quality-at-fixed-route was NOT the binding path and the residual wall on
non-flip rows is the Leg-4b floor already at work at 1x; record that the two-stage
construction is exhausted and the wall passes fully to the design-change track
(C3.3 excitation).

## Leg 6 — does excitation move the D floor? (design-change track, first lever;
## registered before run, 2026-08-02)

Relation to prior work: C3.3 measured a Fisher-information frontier under its OWN
estimator (Fisher-Wiener, single-stage) and ruled NO_GO_INFORMATION_LIMIT against
its headroom target — but its geometry-vs-log-information slope was positive and
CI-solid (.0294, LCB .0222), and excitation arms beat passive at every K. The M4-D
arc since built two new instruments: the Leg-4b floor protocol (oracle-forced route,
e_d_paired, budget grid) and the Leg-5 two-stage construction. Leg 6 asks the
design-change question with the NEW instruments: does per-event orthogonal
excitation (C3.3's balanced signed probes, reused as implemented) move the
STRUCTURAL FLOOR itself, and does it stack with two-stage?

Arms: {passive, orthogonal excitation} x budget {1x, 2x, 4x} under the Leg-4b
protocol (oracle-forced route, per-world floors), plus a two-stage+excitation
full battery at 1x for the stacking question. Same 5 worlds x 8 reps.

Leans: (a) excitation lowers the pooled floor by >= .05 absolute at matched budget
(pooled e_d_paired floor .39 -> <= .34); (b) BOTH readings registered for the
scaling: (b1) excitation shifts the LEVEL but the budget-slope stays flat
(|tail slope| < .15 — a floor translation), vs (b2) excitation RESTORES budget
scaling (tail slope <= -.35 — the stronger, less likely reading; record which);
(c) two-stage+excitation pooled loop geometry >= .78 (beyond Leg 5's .7605) with
the gain concentrated in the two floor-pinned worlds (partition .6527,
compensation .6209). PIVOT-IF: pooled floor moves < .02 under excitation — then
the C3.3 information limit extends to the OBJECT level (excitation buys Fisher
information but not D-resolution), and the design lever must be
paired/interventional OCCASIONS, which becomes the next registered leg.

## Leg 7 — realization averaging: the direct test of the floor's interpretation
## (registered before run, 2026-08-02; loop cycle 2)

Leg 6 outcome (pivot fired): orthogonal per-event excitation moves the pooled floor
only .0125 (< .02) — the C3.3 information limit extends to the OBJECT level; reading
B1 (level shift, flat tail); stacking with two-stage HURT (.7387 < .7605, excitation
cuts flips but adds creation noise). The registered next lever: paired/interventional
OCCASIONS.

The Leg-4b interpretation ("the floor is the creation derivative's PER-REALIZATION
variance") makes a sharp falsifiable prediction: averaging D estimates across
INDEPENDENT REALIZATIONS of the same law must reduce the floor as R^(-1/2), where R
is the number of realizations — this is exactly what "more events within ONE
realization" (4b) and "richer excitation within one realization" (Leg 6) could not
do. The generator supports fresh path realizations under frozen world semantics
(4b's non-1x panels were exactly that).

Design: at fixed 1x event budget, R in {1, 2, 4, 8} independent realizations per
world-rep under identical law; D estimated per realization at the oracle-forced
route (4b protocol), then realization-averaged (simple mean of D estimates;
secondary: pooled joint fit); e_d_paired vs R per world. Stacking arm: two-stage +
realization-averaged D at R = 4, full battery, vs Leg 5's .7605.

Leans: (a) THE CONFIRMATION TEST of the 4b interpretation — pooled floor scales as
R^(-1/2): log-log slope in [-.65, -.35] over R (at R=8, .39 -> ~.14 if exact);
(b) at R=8 the pooled floor <= .20; (c) two-stage + realization-averaged D at R=4:
pooled loop geometry >= .82 with the two floor-pinned worlds (partition,
compensation) crossing .70. PIVOT-IF: the floor is R-INVARIANT too (slope > -.15) —
then the "per-realization variance" interpretation of Leg 4b is WRONG, the floor is
estimator-family bias or a world-identifiability limit, and the next instrument is
an oracle-vs-estimator bias decomposition at increasing R; record the
interpretation's death honestly (it is my registered reading from the synthesis
doc, so its failure must be recorded as my miss, not softened).

## Leg 8 — bias anatomy: de-biasing, family enlargement, subspace alignment
## (registered before run, 2026-08-02; loop cycle 3)

The Leg-7 pivot profile split the floor into law-level bias ~.37 and basis-mismatch
bias ~.13. Three registered levers, one battery:

Arm A (de-biased oracle refit): the V2 ridge penalty's bias does not vanish with n
by design (Leg 4 note) and appears in BOTH bases. Refit D at the oracle basis and
oracle-forced route with (i) penalty -> 0 (unpenalized where numerically stable) and
(ii) a penalty scaled to vanish (lambda ~ 1/n). Measure e_orc_true at 1x and 4x.
Arm B (family enlargement): enlarge the hazard family at the oracle basis
(registered enlargement: add pairwise interaction terms of the existing features;
one step only, no search). e_orc_true at 1x/4x.
Arm C (subspace alignment for the gap): project/align the DISCOVERED chart frame
onto the oracle subspace (orthogonal Procrustes on frames; diagnostic only — the
oracle is unavailable in operation) and refit D at the aligned frame; measure how
much of the ~.13 estimator-minus-oracle gap closes.
Arm D (stack): best-of-A/B + excitation (Leg 6 showed excitation moves the
law-level component .376 -> .292) at the oracle basis; and best-of-A/B/C + two-stage
full battery vs Leg 5's .7605.

Leans: (a) de-biasing (A) alone cuts oracle-own-error from ~.376 to <= .25 at 1x in
>= 3/5 worlds (the ridge-bias reading); (b) A or B combined with excitation reaches
e_orc_true <= .18 pooled at 1x; (c) alignment (C) closes >= half the .136 gap
(to <= .068); (d) the full stack (D) lifts two-stage pooled loop geometry to >= .80.
PIVOT-IF: A and B together move oracle-own-error < .05 — then the law-level bias is
neither regularization nor one-step family enlargement, and the recorded verdict
becomes WORLD-IDENTIFIABILITY LIMIT with the next instrument an information-operator
conditioning analysis of the creation estimand in these worlds.

## Leg 9 — the bias-variance account of the paired floor + gap anatomy
## (registered before run, 2026-08-02; loop cycle 4)

Leg 8 outcome: law-level bias is largely ridge self-infliction (A_lam1n .376 -> .261,
4/5 worlds; +excitation .194), but the THIRD consecutive stacking failure appeared —
de-biased D damages paired transport (.6248 < .7605), after excitation (.7387) and
realization-averaging (.7583) also failed to stack. Emerging hypothesis: the paired
disc-vs-oracle transport metric REWARDS the V2 ridge's variance reduction; the loop
floor is a BIAS-VARIANCE EQUILIBRIUM, not a hard limit. Also: the basis-mismatch gap
(.136) is not orientation (alignment inverts it) and concentrates in three worlds
(expansion/compensation/rotated .21-.26 vs gated/partition .026/.066).

Arms:
A (bias-variance decomposition): reuse Leg 7's R-panel machinery. For D estimators
  {V2 ridge, lam1n, unpen} at budgets {1x, 4x}: decompose per-cell paired error into
  bias^2 and variance across R=8 fresh panels (bias = error of the R-averaged
  estimate; variance = mean squared deviation of per-panel estimates around their
  average). Then run two-stage with each estimator at 1x and 4x (full 5x8 battery
  per cell).
B (gap anatomy swap): in the three high-gap worlds, decompose the .21-.26 gap by
  content swap: (i) oracle basis + discovered support-weights vs (ii) discovered
  basis + oracle support-weights (both refits at the oracle-forced route). Attribute
  the gap to basis-content vs support-weighting.
C (partition reference check): recompute partition's law-level bias under the
  envelope-corrected reference flagged at Leg 7 (reference gap .645); adjudicate how
  much of its .592 resistance is artifact.

Leans: (a) the bias-variance signature appears: unpen/lam1n have lower bias and
higher variance than V2 ridge at 1x, AND the two-stage ranking INVERTS at 4x
(two-stage+lam1n >= two-stage+V2 at 4x while below at 1x) — if held, the paired
floor is a bias-variance equilibrium and the limit statement gains its final clause
(the floor moves with budget ONLY through the variance term of a de-biased
estimator); (b) basis-content dominates the gap (>= 70% attribution) in >= 2 of the
3 high-gap worlds; (c) partition's law-level bias at least halves (.592 -> <= .30)
under the corrected reference. PIVOT-IF: (a)'s inversion does NOT appear at 4x —
the bias-variance account dies; the paired floor's last layer is the gap itself;
next instrument = the in-run conditioning profile already persisted at Leg 8
(results/m4_d_bias_anatomy/conditioning_rows.csv) elevated to a full leg.

## Leg 10 — direction-content anatomy of the discovery step
## (registered before run, 2026-08-02; loop cycle 5)

Leg 9 pinned the residual gap to per-category ROW-DIRECTION content of the
discovered chart (oracle directions + discovered norms eliminate it; support
weights ~0). Question: WHERE does discovery lose the directions, and is the loss
attributable?

Arms:
A (de-biased discovery): refit the DISCOVERY chart/hazard with lambda~1/n (the
  Leg-8 lever applied at the discovery stage, not stage-2); measure per-category
  row-direction alignment to oracle (principal angles / per-category cosine) and
  the paired gap in the 3 high-gap worlds.
B (response-safe relaxation, DIAGNOSTIC ONLY — operationally forbidden, label
  loudly): fit discovery without the response-safe projection; attribute how much
  direction deficit is the safety constraint's price.
C (conditioning elevation, the twice-registered hand-off): per-world/per-category
  information-operator conditioning (extend results/m4_d_bias_anatomy/
  conditioning_rows.csv to per-category resolution) correlated with the
  per-category direction deficit.

Leans: (a) de-biased discovery closes >= half the gap in >= 2/3 high-gap worlds;
(b) BAND, honest uncertainty: safety relaxation alone closes [10%, 60%] of the
deficit (point-lean: below half — the safety constraint is not the main price);
(c) conditioning predicts deficit: per-category Spearman >= .6 pooled across the
three worlds. PIVOT-IF: none of A/B/C attributes >= half the gap -> the direction
deficit source is UNIDENTIFIED; next instrument = perturbation analysis of the
discovery objective (gradient of direction estimates w.r.t. panel composition).

## Leg 11 — perturbation analysis: is the paired gap a non-smooth functional at the
## oracle point? (registered before run, 2026-08-02; loop cycle 6)

Leg 10 outcome (1/3; decoupling headline): de-biased discovery repairs direction
ALIGNMENT (.24-.41 of the deficit) without closing the paired gap (+.113/-.140/-.138);
safety relaxation closes .5008 of the direction deficit but only .213 of the gap;
conditioning is dead as a predictor (within-world flat; pooled -.391 = Simpson
artifact). Combined with Leg 9's exact-oracle swap eliminating the gap entirely, the
gap appears NON-MONOTONE — effectively all-or-nothing — in direction content
(rho(direction improvement, gap improvement) = .218/-.133). Registered hand-off:
perturbation analysis of the discovery objective, sharpened here to the paired
functional itself.

Design (3 high-gap worlds x 8 reps):
A (geodesic interpolation): interpolate chart frames from oracle to discovered along
  the frame-manifold geodesic, t in {0,.05,.1,.2,.4,.7,1.0}; refit D at each t
  (V2 estimator, oracle-forced route); gap(t) per world.
B (controlled random perturbations): perturb ORACLE directions by fixed principal
  angles theta in {1,2,5,10,20 degrees} (random within-category rotations, 8 draws
  each); gap(theta).
C (discrete-event instrumentation): instrument the paired evaluator to log every
  discrete internal decision (category association, route agreement, support-cell
  membership) along A's path; identify WHICH discrete decision flips at the knee,
  if a knee exists.

Leans: (a) NON-SMOOTHNESS: gap(t) jumps by >= half its full value within t <= .2
(equivalently gap(theta) jumps by >= half by theta <= 5 degrees) in >= 2/3 worlds;
(b) the jump co-occurs with an identifiable discrete event (C isolates a single
flipping decision family in >= 2/3 worlds); (c) DIAGNOSTIC (unregistered-secondary
reporting): a soft-assignment variant of the paired functional removes >= half the
jump where (b) identifies the event. PIVOT-IF: gap(t) is SMOOTH (no knee; roughly
proportional growth) -> the all-or-nothing reading is wrong, the deficit is genuinely
distributed direction content, and the arc CLOSES with the residual accepted as
object-level; final synthesis follows either way — Leg 11 is the arc's designated
last leg before the loop moves to the standing queue (two-stage retrofit of the C.3
attribution NO-GO; R->V bridge heteroscedastic calibration).

## Leg 12 — two-stage retrofit of the M4-C.3 physical-edge attribution NO-GO
## (registered before run, 2026-08-02; loop cycle 7 — first standing-queue item;
## the M4-D arc itself is closed)

The C.3 error-budget attribution NO-GO (budget Spearman .7264 < .75, passing reps
4 < 6) was measured with V2 single-stage loops. The M4-D arc since established that
two-stage route-then-refit removes route-flip contamination (196 -> 73) and improves
every loop statistic it touched (pooled .6519 -> .7605). Question: does recomputing
the C.3 attribution over TWO-STAGE loops lift the attribution ordering past its own
registered bar?

Design: rerun the exact C.3 attribution battery (its own protocol, worlds, and
Spearman target) with loops/legs produced by the two-stage construction; no other
change. Report the original NO-GO metrics side by side.

Leans: (a) pooled budget Spearman >= .75 (the original bar; from .7264);
(b) passing reps >= 6 (from 4); (c) the improvement concentrates in reps where
stage-1 corrected flips. PIVOT-IF: Spearman moves < .01 -> the attribution deficit
is independent of route contamination; record and return the item to the M4-C
track's own queue unchanged. This is a bounded retrofit: one battery, no new
estimators, no redesign of the attribution formula.

## Leg 12 outcome (2026-08-02, appended) and Leg 13 registration

**Leg 12: 0/3 leans; pivot non-fire; the outcome lands OUTSIDE both registered
branches and is recorded as such.** Two-stage TRANSFERS cleanly to the C.3 worlds
(flips 149 -> 57, pooled loop geometry .6278 -> .7421, all 5 worlds improve) — yet
the attribution Spearman DROPS (.7264 -> .6677, passing reps 4 -> 2): the original
NO-GO's ordering statistic was partially FLIP-SUBSIDIZED (flips injected extreme
auto-co-ranked values into both budget and realized loss; touched-row medians:
budget .825 -> .776 while realized loss collapses .449 -> .200). A pre-existing
budget-denominator pathology was newly exposed (one corrected author's budget blows
up to 1.73e9). M4_C3_NO_GO stands under BOTH constructions; the item returns to the
M4-C queue as a better-understood NO-GO. Lesson filed with the arc's part (iii):
truth-referenced ordering statistics can be SUBSIDIZED by the very contamination
they sit on — cleaning the estimator can lower the score.

## Leg 13 — R->V bridge: heteroscedastic calibration of the rank selector
## (registered before run, 2026-08-02; loop cycle 8 — last pre-declared queue item)

Leg 2's disclosed limitation: the rigidity index's auto-rank (negative-spectrum
floor, eigenvalue > 2x|most negative|) hits the rank cap with near-zero margin under
heteroscedastic empirical-logit noise (the C2 field family). This is instrument
development (not deferred defense machinery): the bridge must behave on realistic
noise fields.

Design: extend the Leg 2 battery with registered heteroscedastic families
(per-pair noise scaling with relation magnitude; per-author variance heterogeneity;
empirical-logit profiles via the same hierarchical C2 generator Leg 2 used). Arms:
baseline selector vs two calibrated variants (one step each, no search):
(V1) variance-weighted eigen-floor (noise floor from a per-cell variance model);
(V2) permutation floor (row/col residual permutation null spectrum, 199 draws).
Measure: rank recovery, license AUC, group-only refusal (Leg 2's designed-null
battery reused — MUST stay intact), and C2-field behavior (cap-hit rate, margin).

Leans: (a) the problem is real: baseline license AUC <= .80 under the
heteroscedastic families (vs .944 homoscedastic individual-family in Leg 2);
(b) at least one calibrated variant restores AUC >= .88 while keeping group-only
refusal >= 199/200; (c) on C2 fields the winning variant produces non-cap rank with
positive margin in >= 3/4 of cases where baseline capped. PIVOT-IF: no variant
restores AUC without breaking group-only refusal -> record the refusal-safety vs
sensitivity TRADE-OFF FRONTIER as the bridge's documented operating curve (a valid
deliverable, not a failure).

## Leg 13 outcome (2026-08-02, appended) and Leg 14 registration

**Leg 13: 0/3 leans; pivot fired as registered — the tau frontier is the
deliverable.** Baseline hetero AUC .8372 (problem milder than leaned; weak spot
author-lognormal .7764; C2 AUC NaN by construction — single-class family, lean was
correctly registered on rank/margin). V1 variance-weighted DEGRADES (.7268; not
variance misestimation — its worst-row analytic edge zero-ranks 22.6% of
reconstructable worlds); V2 permutation ties baseline (.8316). Refusal batteries
intact everywhere (designed-null 200/200 x3 arms; hetero group-only 360/360 x3;
zero false licenses). Frontier: baseline at tau .275 dominates (sensitivity .708 at
0/200 nulls — prospectively reproducing Leg 2's unadopted Youden point); the
variants buy SPECIFIC repairs (V1: C2 un-cap 60/60 median margin .21; V2:
deep-noise ordering .944 -> .995). Mechanism discovery: C2 fields are exact EDMs ->
Gram PSD -> the negative-spectrum floor collapses (~2e-9); the profile-noise PSD
mean shift is invisible to replicate-difference floors — a debiased cross-half
floor is the queued candidate (NOT registered here).

## Leg 14 — discovery-objective displacement reduction: the quadratic-basin
## prediction test (registered before run, 2026-08-02; loop cycle 9)

The arc's one genuine object-level residual: discovery lands a finite frame
displacement from the oracle and the paired gap grows near-quadratically along it
(Leg 11: gap ~ theta^1.8-1.9). Therefore any method that shrinks displacement by
factor alpha should shrink the gap toward ~alpha^2 — a QUANTITATIVE theory
prediction, not just a repair hope.

Arms (one step each, no search; 3 high-gap worlds x 8 reps):
A (consensus discovery): average per-rep discovered frames within each world
  (Frechet/chordal mean on the frame manifold, all 8 reps), refit D at the
  consensus frame per rep; measures whether displacement is rep-noise-driven.
B (split-half agreement): fit discovery on half the panels with a registered
  one-step shrinkage toward the frame fitted on the other half (symmetric,
  averaged); measures within-rep noise contribution.
C (prediction check): for every arm and rep, place (displacement fraction alpha,
  gap fraction) on the Leg-11 basin curve; test gap_fraction ~ alpha^2 against the
  fitted per-world basin exponents (1.84/1.76/1.87).

Leans: (a) consensus reduces frame displacement by >= 30% in >= 2/3 high-gap
worlds; (b) where displacement shrinks, the gap follows the basin prediction within
a factor-2 band (gap_fraction within [0.5, 2.0] x alpha^exponent) in >= 2/3 worlds
— THE QUANTITATIVE TEST of the quadratic-basin theory; (c) the combined best arm
reduces the pooled high-gap paired gap by >= 25% vs gap_v2. PIVOT-IF: consensus
does NOT reduce displacement (< 10%) — displacement is SYSTEMATIC BIAS of the
discovery objective, not estimation noise; record it, and the objective-redesign
item (beyond one-step) is deferred as the arc's closing open problem; the loop then
moves to fresh question mining.

## Leg 14 outcome (2026-08-02, appended) — the M4-D thread's definitive close

**0/3 leans; pivot fires 3/3 worlds; verdict DISPLACEMENT_IS_SYSTEMATIC_OBJECTIVE_
BIAS.** Consensus averaging INCREASES displacement in all three worlds
(-.256/-.264/-.216) and explodes the gap (.215 -> .680): the eight per-rep
discovered frames share a COMMON bias direction — averaging removes noise, not the
bias. Split-half agreement moves 4.6%. The basin prediction test was largely
inapplicable (displacement never shrank). CLOSING OPEN PROBLEM (deferred): which
term of the discovery objective produces the common displacement — objective
redesign beyond one-step moves. The loop moves to fresh question mining per the
registered hand-off.

## M4-E1 — exporting the arc's core discovery to REAL TEXT: the convention gap
## (registered before run, 2026-08-02; loop cycle 10, fresh thread)

The arc's most consequential finding (Leg 8): the V2 ridge's non-vanishing penalty
bias manufactured an illusory budget-invariant floor on synthetic worlds. QUESTION:
does the same self-infliction operate in the REAL-TEXT V8 relation field?

Real text has no oracle, so bias is invisible to split-half agreement (both halves
share it). The label-free detector is the CONVENTION GAP: fit the relation-field
estimate under the V2 penalty convention and under lambda~1/n on identical panels;
measure (i) each convention's internal split-half agreement as event budget n grows
(subsample fractions {1/4, 1/2, 1}), and (ii) the BETWEEN-convention gap at each n.
Signature of operating self-infliction: internal agreement tightens with n for both
conventions while the between-convention gap PERSISTS or grows — the persistent gap
is the real-text analogue of the arc's disc-oracle law-level bias. Null outcome:
the between-convention gap shrinks with n at the same rate as internal disagreement
(penalty immaterial at real-text scale).

Data: the OPENED D1/D2 real-text panels via the existing label-free loaders
(scripts/run_suica_v8_realtext_relation_field.py machinery; PANDORA tier_u frozen
parquet, Essays text-only read under the V6-E2 precedent). REUSE-DISCLOSURE: these
panels are part of the route's declared adaptive exploratory chain (route index
section 7 item 1); this run extends that chain and must carry the same banner — no
fresh-panel confirmatory claim.

Leans: (a) both conventions' internal split-half agreement improves monotonically
with n on PANDORA (sanity); (b) the between-convention gap at full n exceeds 2x the
internal split-half disagreement of either convention (self-infliction OPERATES) in
the primary PANDORA field; (c) Essays shows the same sign (direction only, no
magnitude lean — different register per T6 discipline). PIVOT-IF: the
between-convention gap tracks internal disagreement (< 1.2x at full n) — penalty
choice is immaterial on real text at current scales; record it and the arc's
self-infliction lesson stays synthetic-scoped.

## M4-E1 outcome (2026-08-02, appended)

**Pivot fires by ~4,900x: penalty choice is immaterial on real text at current
scales — the self-infliction lesson stays synthetic-scoped.** Mechanism pinned: the
two conventions are near-perfectly PROJECTIVELY EQUIVALENT on real text (they clip
the same eigen-block and differ by a near-global rescale — Frobenius ratio 3.3344
vs pure-projective prediction 3.3372, 0.03-0.08% off — and the field's own
comparison gauge, matrix cosine, is scale-invariant; Leg 8's synthetic detection
was oracle-referenced and scale-SENSITIVE). Deeper finding, the SATURATED
YARDSTICK: internal split-half agreement is nil at every measurable budget under
EVERY convention including the deployed penalty-free reference — independently
re-confirming V8's own REALTEXT_SOFT_SUPPORT_ONLY_RELATION_UNRESOLVED from a new
angle: the binding constraint on real text is panel SIGNAL, not estimator
convention. Substituted-knob caveat register-noted before compute (the deployed
estimator is penalty-free; the whitened relation algebra's lambda was the closest
live knob). Lean (c) held (Essays same sign); (a) null-regime artifact; (b) miss in
the pivot direction.

## M4-E2 — anatomy of the common offset (registered before run, 2026-08-02;
## loop cycle 11; analysis-only on persisted artifacts)

Leg 14's companion decomposition isolated the arc's final object: a REP-INVARIANT
COMMON OFFSET (12.0-13.8 frame-distance, ~3/4 of per-rep displacement) between the
discovered-frame cloud center and the oracle-anchor cloud center, unremovable by
averaging. Question: WHICH objective structure carries it?

Design (no new batteries; analysis of persisted Leg 10/14 frames + one cheap
diagnostic refit per world): decompose the common-offset vector per world onto
registered subspaces: (S1) the response-safety projection's complement; (S2) the
span of supervision-target directions; (S3) normalization/scale modes; (S4)
residual. Then a diagnostic projection: remove the offset's dominant component from
each rep's discovered frame and refit D (V2, oracle-forced route) to measure gap
closure.

Leans: (a) the offset concentrates (>= 60% squared norm) in ONE subspace
consistently across the 3 worlds — point-lean S1 (safety complement), given Leg 10
arm B closed ~half the DIRECTION deficit; (b) the concentrated component's
direction is stable across worlds (pairwise cosine >= .7) — one mechanism, not
three; (c) removing the dominant component closes >= half the paired gap (the
practical tie-back). PIVOT-IF: the offset spreads (< 40% in every subspace) — no
single objective term is responsible; the open problem stays open exactly as
registered at Leg 14, and the loop moves to fresh mining outside the M4-D/E line.

## M4-E2 outcome (2026-08-02, appended) — the M4-D/E line closes

**0/3 leans; pivot fires; verdict OFFSET_SPREAD_NO_SINGLE_OBJECTIVE_TERM.** Shares:
S1 safety-complement .20-.23, S2 supervision-span .01-.03 (the supervised block is
NOT where the bias lives), S3 norm/scale .30-.38, S4 residual .40-.45 — nothing
reaches 40% anywhere. Cross-world offset cosines .416-.452 sit AT the permutation
null (~.43): world-specific directions, not one mechanism. Dominant-component
removal DOUBLES the gap (.215 -> .480; closures -1.11 to -1.28) — the discovered
frame is a jointly-adapted local optimum; amputating one direction breaks it
(consistent with the Leg-11 smooth basin). CLOSING CHARACTERIZATION of the open
problem: the discovery objective's common displacement is distributed across
objective structure and world-specific in direction; the redesign will be neither a
one-term fix nor a shared-direction fix. The M4-D/E line is CLOSED (14 legs + E1 +
E2); fresh mining moves outside the line.

## M4-F1 — the D3 panel sizing law (registered before run, 2026-08-02; loop cycle
## 12, new line: panel design laws)

M4-E1's saturated yardstick: real-text internal split-half agreement is nil at
current D1/D2 panel scales under EVERY estimator convention — the binding
constraint is panel signal. The V8 route's own item 1 requires a fresh D3 panel
with event count and composition registered BEFORE opening. This leg supplies the
principled sizing: a label-free, synthetic power law calibrated to the real-text
regime.

Design: use the existing V8/M3 relation-field world generators; calibrate the
noise/support regime to the observed real-text diagnostics (effective rank ~39-42,
internal agreement ~0 at current n, the D0/D1 panel shapes persisted in the
realtext artifacts). Sweep panel scale on two axes SEPARATELY: authors x{1,2,4,8}
at fixed events/author, and events/author x{1,2,4,8} at fixed authors. Measure
internal split-half agreement (the field's own gauge) per cell; fit power laws;
extrapolate the budget where agreement crosses .5; validate the extrapolation at
one held-out large cell (16x on the cheaper axis).

Leans: (a) agreement rises off zero within the swept range in the calibrated
worlds (if it cannot, the calibration itself falsifies size-only rescue);
(b) AUTHOR count dominates: the author-axis scaling exponent exceeds the
events-per-author exponent (relation fields are pairwise objects — doubling
authors quadruples pairs); (c) the .5-agreement budget lands within [4x, 50x] of
current D1/D2 on the dominant axis (wide honest band), and the 16x held-out cell
falls within factor-2 of the fitted law's prediction. PIVOT-IF: agreement stays
~0 even at the largest swept cells in calibrated worlds -> SIZE-ONLY RESCUE
FALSIFIED; the D3 design must change COMPOSITION (shared-context events,
within-author condition pairing), not just scale — which becomes the registered
next design question.

## M4-F1 outcome (2026-08-02, appended)

**1/3 leans (a); pivot does NOT fire — agreement rises off zero on both axes —
but the measured law kills size-only rescue anyway.** Generator adjudication
(register-noted in the report Part 0 before compute): no verbatim V8/M3
generator reaches the registered regime (HJIC has no event axis, so the E1
gauge cannot even be applied to it; M3's scalar-parameter worlds cap at
support effective rank ~1-3 and their multi-dim variants CLT-wash through the
deployed map's projection features) — the registered escape fired and the leg
ran on the disclosed minimal composition `M4F1RelationWorld` (HJIC latent/
loadings/taper lifted to event level, per-factor AR(1) chains as the
order-sensitive carrier, deployed frozen map bit-identically batched, gates
0.0). Calibration CALIBRATED and verified on 8x20: effM 42.61 / effK 39.64 /
agreement +.0047 (t 1.03) vs targets 42.17 / 38.53 / ~0; the real
quarter-budget K collapse reproduces untargeted (7.7-9.1 vs 8.48). Result:
five swept cells rise off zero (lean a HOLD) but the exponents are tiny —
events axis FITTED gamma = .153 (CI [.02, 1.22]), .5-agreement budget 10^14x
with bootstrap lower edge ~155x, still outside the registered [4,50]; author
axis DEGENERATE (1x->2x flat at the floor) with companion slope .404 > .153
pointing lean (b)'s way but below the registered >= 3-cell standard (b MISS);
the events-x16 held-out cell validates the law within factor-2 (obs .0123 vs
pred .0107) yet the budget band fails by ~12 orders (c MISS). Practical D3
corollary, stated as a measured-law consequence and NOT as a fired pivot: no
feasible scale reaches .5 agreement on either axis — the D3 design question
moves to COMPOSITION (shared-context events, within-author condition pairing).
Interpretation (hedged): the author axis shows the spurious-field-to-true-
relation crossover beginning only above ~2x authors; the events axis sharpens
features while dissolving the realized-state heterogeneity the finite panel's
field rides on — signal and noise shrink together. Panel design laws line
continues from the composition question.

## M4-F2 registration (2026-08-03, BEFORE run) — the D3 composition law

M4-F1 measured the sizing law and killed size-only rescue (events exponent
.153; .5-agreement budget 10^14x; bootstrap edge ~155x never inside the
registered [4,50]) and issued a corollary hand-off: the D3 panel must change
COMPOSITION — shared-context events, within-author condition pairing — not
scale. This leg tests that hand-off at FIXED TOTAL EVENT BUDGET, so any gain
is attributable to composition alone and not to size.

**Mechanism this leg targets (from M4-F1's own interpretation).** In the
free-response composition each author's events are their own idiosyncratic
occasions, so part of the between-author difference the field rides on is
occasion-SAMPLING nuisance, independent between halves and therefore pure
noise on the split-half gauge. SUICA's own opportunity theory says the fix is
to control the condition by design. A shared-occasion panel (every author in
a context observed on the same occasion grid) removes that nuisance by
construction at identical budget.

**World.** M4F1RelationWorld with the calibrated knobs (k=48, rho=.50,
w_mu=.15, w_x=.15, w_e=.70, phi in [.20,.80]), extended by a context-occasion
common shock: at occasion t in context c a shock s_{c,t} shared by all authors
of c enters each event with weight kappa, taken out of the author's own state
share so total variance is preserved. kappa=0 recovers M4-F1's world exactly.

**Design axes (all at the base1x total event count).**

- Axis 1, occasion composition x kappa in {0.5, 1.0}:
  - `free_k05`, `free_k10`: each author draws their own occasions (current
    deployed/real-text composition);
  - `shared_k05`, `shared_k10`: all authors of a context are observed on the
    SAME occasion grid.
  The comparison of interest is shared minus free AT THE SAME kappa: the
  world (including how much shared structure exists) is held fixed and only
  the design changes.
- Axis 2, within-author condition pairing at kappa=0: `crossed_q2`,
  `crossed_q4` — each author appears in Q contexts with m/Q events each, total
  events unchanged. Read on the deployed per-context gauge AND on a declared
  companion: the within-author cross-context contrast field's own split-half
  agreement (a DIFFERENT typed object; levels are not comparable to the
  per-context field, only the presence/absence of non-nil agreement is).

**Gauge.** Unchanged from M4-E1/M4-F1: the deployed frozen realtext map,
D0 soft calibration, per-context deployed soft field, weighted field
agreement, seed-compatible event halving; 8 worlds x 20 draws per cell.

**Leans.**
(a) At fixed budget, shared-occasion beats free-response at the same kappa:
    agreement(shared) - agreement(free) > 0 with the paired-world CI
    excluding 0 at kappa=1.0 at minimum.
(b) The gain scales with kappa (gain at 1.0 > gain at 0.5), because the
    removed nuisance IS the occasion-sampling variance whose size kappa sets.
(c) Crossed authors HURT the deployed per-context gauge (monotone decline in
    Q, consistent with M4-F1's events-axis law at m/Q events per
    author-context), WHILE the paired-contrast companion shows non-nil
    agreement at Q>=2 (t>2 against its own zero) — i.e. pairing buys a
    DIFFERENT certifiable object, not a better version of the same one.

**PIVOT-IF:** neither kappa shows a shared-minus-free gain with a CI
excluding 0 -> COMPOSITION-AT-FIXED-BUDGET ALSO FAILS on the deployed gauge.
The D3 problem is then not a panel-design problem but a GAUGE problem, and
this line MERGES with the M4-E2 objective-redesign open problem, which becomes
the registered next question.

**Gates (all must pass before adjudication).**
- G1 anchor: the kappa=0 free cell reproduces M4-F1's persisted `base1x`
  (agreement_mean .004733, se .004591, effM 42.610149, effK 39.637239,
  n_retained 565) to <=1e-12.
- G2 budget conservation: total event count is exactly equal across every
  cell (integer equality, reported per cell).
- G3 gauge invariance: deployed map, D0 path, and halving indices are the
  M4-E1/M4-F1 functions, equality-gated as in M4-F1's gate 2.
- G4 designed null: at kappa=0, `shared` equals `free` cell-for-cell (sharing
  occasions can do nothing when there is no common shock). A G4 failure means
  the manipulation is doing something other than what it claims and the leg
  is void.

Tier: EXPLORATORY, label-free, synthetic-calibrated. Artifacts:
`results/m4_f2_composition/`; report
`reports/SUICA_M4_F2_COMPOSITION_REPORT.md`.

## M4-F2 outcome (2026-08-03, appended)

**Lean (a) HOLD, lean (b) HOLD, pivot does NOT fire -- composition beats
M4-F1's scale wall. Lean (c) PARTIAL -- the companion object holds
decisively (t=20.5 / t=62.3), the main-gauge decline half misses at its one
measurable point.** All four gates green (G4 did not fire; the leg is not
void). Full numbers, tables, and the register-noted operationalizations this
leg had to invent (the registration named the mechanism and axes but left
several implementation choices open) are in
`reports/SUICA_M4_F2_COMPOSITION_REPORT.md`.

Gates: G1 reproduces M4-F1's persisted `base1x` (agreement_mean, agreement_se,
both D0 effective ranks, n_retained) to abs diffs of 9.89e-17 / 1.12e-16 /
0.0 / 7.11e-15 / 0 -- far inside the 1e-12 bar, because kappa<=0 makes the
new generator literally return `f1().generate_world`'s own output, not a
numerically-close reproduction. G2: all six adjudicated cells allocate
exactly 12,784 events (M4-F1's raw base1x total 13,202, minus 418 dropped by
the "largest common budget" resolution -- Q=2 and Q=4 both need each
author's per-author budget to be a multiple of 4, applied uniformly to all
six cells, not just the crossed arms, per the registration's own explicit
fallback instruction). G3 bit-identical to the deployed feature map and
halving. G4: `free_k00` and `shared_k00` match EXACTLY at all 8 worlds
(agreement_mean, both eff ranks, n_retained, and the full 20-draw vector) --
the manipulation only does what it claims.

**Axis 1 (free vs shared x kappa): the clean result.** Paired-by-world
(shared minus free, t-based 95% CI, df=7): kappa=0.5 mean +0.008836
[0.004418, 0.013254] t=4.73; kappa=1.0 mean +0.026163 [0.019536, 0.032791]
t=9.34. Both exclude zero (registered minimum was kappa=1.0 only); gain
scales with kappa (2.96x). Pivot does not fire -- unlike M4-F1's scale axes
(events-axis exponent 0.153, 10^14x budget to reach 0.5 agreement),
composition at the SAME fixed budget moves the gauge by 2-5x its own
base1x reference level. The registered composition hand-off from M4-F1
is empirically supported.

**Axis 2 (crossed Q in {2,4} at kappa=0): two-sided.** `crossed_q4`'s main
per-context gauge is undefined at every one of 8/8 worlds
(`ZERO_RETAINED_PSEUDO_AUTHORS`) -- verified by exact arithmetic before any
compute: dividing an 8-16-event budget by 4 caps every author's slice at 4
events, below the deployed gauge's own >=8 retention floor, for every
author, always, regardless of the budget-truncation choice. `crossed_q2`'s
main gauge IS computable but only on a population-restricted subset (282 of
565 D1+D2 authors -- exactly the richest-budget, `m=16`, subgroup, the only
one clearing the >=8 floor at Q=2); against the kappa=0 reference
(free_k00==shared_k00) this comparison is statistically indistinguishable
(t~0.41, nominally even slightly higher, not lower) -- the registered
"monotone decline in Q" is NOT supported at the one point it could actually
be measured, and is undecidable (structural non-computability, not a
measured extreme) at the other. The companion object (this leg's own
construction -- the registration named it but did not pin its equations)
tells a different story entirely: non-nil split-half agreement at both Q=2
(t=20.47, all 565 eligible authors) and Q=4 (t=62.28, the same 282-author
subpopulation whose main gauge is undefined) -- the clearest possible
instance of "pairing buys a different certifiable object, not a better
version of the same one," exactly as registered, but the specific
main-gauge-hurts mechanism the registration also predicted is not the one
observed to be doing the work.

Honest limitations (full list in the report): the crossed_q2-vs-reference
comparison is population-confounded (richest-budget-only vs everyone), not
corrected for after seeing the result in either direction; the companion's
construction is a disclosed, deliberately-simplified same-primitives reuse,
never level-compared to the main gauge; D0 K-effective-rank collapses to
9.21 under crossed_q4 (independent replication of M4-F1's own quarter-budget
K-collapse mechanism, not a new finding); axis-1's four cells share one
random substrate per world by deliberate design (maximizes the registered
paired statistic's power, disclosed rather than hidden). Training mainline
unaffected; panel design laws line continues -- open question is whether a
composition variant exists that lifts the main-gauge object under crossing
without the population confound, or whether (per this leg's honest reading)
crossing is simply a different-object lever, not a same-object repair.

## M4-F3 registration (2026-08-03, BEFORE run) — level or rate? the decisive fork

M4-F2 established that COMPOSITION works where SCALE did not: at one fixed
budget and inside one world, changing only the design (free-response ->
shared-occasion) moved the deployed field's split-half agreement from nil
(-.0028 at kappa=1.0) to +.0234, paired gain +.0262 [.0195, .0328], t=9.34,
and the gain scaled 2.96x with kappa. But +.0234 is still nowhere near the .5
agreement a certified D3 panel needs. Everything now turns on ONE question:

**Did composition buy a LEVEL (a better intercept on the same hopeless curve),
or a RATE (a steeper exponent, so that feasible scale can finish the job)?**

M4-F1 measured the free-response events exponent gamma_free = .153 (CI
[.02, 1.22]) and a .5-agreement budget of 10^14x. If the shared design merely
shifts the intercept, the budget stays astronomically infeasible and NO
composition can certify a finite panel on this gauge. If the exponent
materially improves, a feasible D3 exists and this leg names its size.

**Design.** Mirror M4-F1's sweep protocol exactly so exponents are comparable,
but run BOTH designs on the SAME world substrate at the SAME kappa, so the
comparison is within-world and within-kappa (never shared-at-kappa-1 versus
free-at-kappa-0, which would confound design with world):

- kappa = 1.0 primary (the regime where the design lever is strongest — a
  failure there is decisive), kappa = 0.5 as the robustness axis.
- events/author x {1, 2, 4, 8} at fixed authors, and authors x {1, 2, 4} at
  fixed events/author, for BOTH designs, on identical world seeds.
- 8 worlds x 20 draws per cell; the M4-E1/M4-F1 gauge, map, D0 path, and
  halving unchanged.
- Held-out validation: events x16 under the shared design at kappa=1.0.
- Fits: log-log OLS as in M4-F1; the PRIMARY statistic is the PAIRED-by-world
  difference delta_gamma = gamma_shared - gamma_free (both fitted on the same
  world substrate), bootstrapped over worlds — deliberately chosen because
  M4-F1's marginal exponent CI was very wide, and a paired bootstrap is the
  powerful test of the question actually being asked.

**Leans.**
(a) RATE CHANGE: delta_gamma > 0 on the events axis at kappa=1.0 with the
    paired bootstrap CI excluding 0. Mechanism: M4-F1 diagnosed that adding
    events sharpens features while DISSOLVING the realized-state heterogeneity
    the field rides on (signal and noise shrink together). Under a shared
    occasion grid the between-author contrast at a common occasion is not
    dissolved by averaging — the common component cancels in the contrast
    instead of averaging into noise — so the rate itself should improve.
(b) The .5-agreement events budget under the shared design at kappa=1.0 falls
    below 10^6x (a wide honest band; M4-F1's free-response value was 10^14x).
(c) The held-out x16 shared cell validates the fitted law within factor 2
    (the same standard M4-F1 met).

**PIVOT-IF:** delta_gamma's paired bootstrap CI includes 0 on the events axis
at kappa=1.0 -> COMPOSITION BUYS A LEVEL, NOT A RATE. Then no composition plus
feasible scale certifies this field at .5, the D3 certification problem is a
GAUGE problem rather than a panel-design problem, and this line MERGES with
the M4-E2 objective-redesign open problem — which becomes the registered next
question. (Note that the M4-F2 pivot pointed at the same destination from the
other side; arriving there twice by independent routes would be a strong
result, not a disappointment.)

**Gates.**
- G1 anchor: the kappa=0 cells reproduce M4-F1's persisted `base1x` to <=1e-12
  (as in M4-F2's G1).
- G2 within-kappa/within-world pairing: for every fitted pair, the shared and
  free cells share the identical world seed and identical event budget;
  reported cell-by-cell as exact equality. A violation voids the comparison.
- G3 gauge invariance: deployed map, D0 path, halving indices unchanged,
  equality-gated as in M4-F1/M4-F2.
- G4 budget conservation across the sweep: each swept multiple's total event
  count is exactly equal between the two designs.

Tier: EXPLORATORY, label-free, synthetic-calibrated. Artifacts:
`results/m4_f3_composition_scaling/`; report
`reports/SUICA_M4_F3_COMPOSITION_SCALING_REPORT.md`.

## M4-F3 outcome (2026-08-03, appended)

**0/3 leans; PIVOT FIRES: `COMPOSITION_BUYS_LEVEL_NOT_RATE_GAUGE_PROBLEM_MERGES_WITH_M4E2`.**
All four gates green (G1 kappa=0 anchor to M4-F1's base1x, abs diffs
9.89e-17/1.12e-16/0.0/7.11e-15, far inside 1e-12; G2 96/96 within-kappa/
within-world seed+budget pairs exact; G3 bit-identical map/halving; G4 all 6
swept multiples' event totals exact across kappa AND design). The decisive
statistic -- delta_gamma's paired-by-world bootstrap CI on the events axis
at kappa=1.0 -- is `[-0.839, +0.039]`, including 0, so the registered pivot
fires by the letter of the rule. But the underlying mechanism is starker
than "same law, different intercept": under kappa>0, NEITHER free nor
shared design's events axis reaches even `DEGENERATE` status reliably (free:
DEGENERATE at kappa=0.5, UNFITTABLE at kappa=1.0; shared: UNFITTABLE at
both) -- M4-F1's own kappa=0 events law (gamma=.153) does not survive ANY
context-occasion shock at all. Cell means at kappa=1.0 are flat-to-negative
by mult=8 on both designs (free -.0011, shared -.0055) and the held-out
16x shared cell stays negative (-.0017); no .5-agreement budget could be
extrapolated (nothing to extrapolate from an UNFITTABLE fit) and the holdout
validated nothing (`EVENTS_AXIS_UNFITTABLE_HOLDOUT_IS_A_PROBE`). Lean (a)
MISS (CI includes 0), lean (b) MISS (status UNFITTABLE, no budget claim
licensed), lean (c) MISS (no fitted law to validate against). The paired
bootstrap's own `n_valid` is 18/2000 on the decisive row -- itself further
evidence the events axis barely produces a well-defined exponent at kappa>0,
not merely a caveat on an otherwise-clean number.

Secondary, non-gating finding (authors axis, restricted by this leg's own
registration to 3 multiples, licenses no lean): under `shared` design
specifically, the authors axis -- DEGENERATE at M4-F1's own kappa=0 -- goes
cleanly `FITTED` at both kappa=0.5 (gamma=0.860) and kappa=1.0 (gamma=1.104),
with bootstrap failure rates of 1/2000 and 0/2000 (the most stable fit in
the leg); `free` design's authors axis stays UNFITTABLE/DEGENERATE at both
kappas. A real rate change from shared-occasion composition WAS measured in
this leg's own data -- just on the axis the registration did not make
decisive, reframing the merged line's open question as "why authors and not
events," not "whether composition can ever buy a rate at all."

Per the registration, the pivot MERGES the panel-design-laws line with the
M4-E2 objective-redesign open problem (closed at
`OFFSET_SPREAD_NO_SINGLE_OBJECTIVE_TERM`), which becomes the registered next
question -- arrived at twice now, by M4-F2's fixed-budget pivot-that-did-not-
fire and this leg's scaling pivot-that-did, from independent routes, exactly
as the registration itself anticipated as a possible "strong result, not a
disappointment." Full numbers, tables, and the register-noted
operationalizations and one mechanical loading fix (Part 0.11, discovered
before any gate number existed, confined to this script's own module loader,
zero edits to M4-F1's or M4-F2's scripts) are in
`reports/SUICA_M4_F3_COMPOSITION_SCALING_REPORT.md`.

## M4-F3 planner adjudication note (2026-08-03, appended)

The M4-F3 pivot FIRED exactly as registered on its decisive axis, and that
stands: on the events axis at kappa=1.0 the paired delta_gamma CI
[-.839, +.039] includes zero, the shared design's events fit is UNFITTABLE,
and the x16 holdout is negative. Composition buys a LEVEL, not a RATE, in
events. The registered consequence — the D3 certification problem is a GAUGE
problem, merging with the M4-E2 objective-redesign line — is recorded and
remains on the books as an open destination.

**One honest correction to the pivot's own consequence, made here rather than
by quietly ignoring it.** That consequence was written as a general statement
("no composition plus feasible scale certifies this field") at a time when the
events axis was believed to be the only fittable axis, because M4-F1's author
axis had been degenerate. M4-F3's own PRE-REGISTERED sweep — the authors axis
was in the registered design, it simply carried no lean because 3 multiples
fall below this line's fit standard — contradicts that generalization: under
the shared-occasion design the authors axis is the leg's MOST stable fit,
FITTED at both kappas (gamma .860 at kappa=.5, 1.104 at kappa=1.0; CI
[.719, 1.454]; 2000/2000 and 1999/2000 qualifying resamples) with cell means
.0061 -> .0332 -> .0586, while the free design stays flat. A rate change was
measured; it was measured on the axis the registration had not made decisive.

Therefore the panel line is NOT closed by this pivot, and saying so requires
declaring the re-opening rather than smuggling it. The next leg (M4-F4) is
registered as a DECLARED RE-OPENING of a line whose pivot fired, with two
disciplines attached: (i) it is designed to KILL the author-axis hope
(saturation pivot), not to confirm it; (ii) it carries a mandatory designed
null, because a statistic computed over more field entries could rise for
instrument reasons rather than world reasons — the exact failure mode that
already cost this line two legs (the ridge self-infliction of Leg 4b and the
common-mode metric of Leg 12). If the null rises, M4-F4 is void and the
gauge-problem consequence stands unqualified.

## M4-F4 registration (2026-08-03, BEFORE run) — the author-axis law, or its artifact

**Declared re-opening.** M4-F3's registered pivot fired and its consequence
(gauge problem) is on the books. This leg re-opens the panel line anyway,
openly, for the reason stated in the planner note above: M4-F3's own
pre-registered authors axis measured a rate change that the pivot's
consequence had generalized away. The re-opening is declared, not smuggled,
and this leg is built to KILL the author-axis hope rather than to confirm it.

**The hope being tested.** Under the shared-occasion design at kappa=1.0, the
deployed field's split-half agreement rose .0061 -> .0332 -> .0586 across
authors x{1,2,4} with a FITTED exponent gamma ~ 1.10 (CI [.719, 1.454]),
while the free design stayed flat. If that law extends, a certified D3 panel
is reachable by RECRUITING MORE AUTHORS ONTO SHARED OCCASIONS — not by
collecting more text per author, which M4-F1/M4-F3 showed is useless and
eventually harmful. If it saturates, the panel line closes for good and the
gauge-problem consequence stands unqualified.

**Design.** Shared-occasion design, kappa=1.0 primary and kappa=0.5
robustness, authors x{1,2,4,8,16} at fixed events/author, 8 worlds x 20 draws,
the M4-E1/M4-F1/M4-F2/M4-F3 gauge/map/D0/halving unchanged, held-out
validation at authors x32 (kappa=1.0, shared).

**MANDATORY DESIGNED NULL (gate, not a lean).** The same author sweep run in a
world with NO true cross-author relation structure (authors independent: the
shared latent that creates the field is switched off while every other
generator draw, the occasion grid, the budgets, and the gauge stay identical).
Measured agreement must remain statistically indistinguishable from zero at
EVERY author multiple. Rationale, stated before the run: the agreement
statistic is computed over more field entries as authors grow, and this line
has twice been burned by instrument structure masquerading as world structure
(Leg 4b ridge self-infliction; Leg 12 common-mode metric). If the null rises
with authors, the measured "author-axis rate" is an artifact of the statistic,
M4-F4 is VOID, and M4-F3's gauge-problem consequence stands unqualified.

**Leans.**
(a) The author-axis law EXTENDS: FITTED status at authors x{1..16} under
    shared/kappa=1.0 with the bootstrap CI lower edge above 0.5 (i.e. still a
    steep rate, not a decaying one), and no monotone decline of the local
    slope across the swept range.
(b) The .5-agreement author budget extrapolates below 100x the current base
    panel (roughly <= 60,000 authors at this line's base of 565) — feasible,
    in contrast with M4-F1's 10^14x event budget.
(c) The held-out authors x32 cell validates the fitted law within factor 2
    (the standard M4-F1 met and M4-F3 could not test).

**PIVOT-IF:** the local slope declines monotonically across the swept range,
OR the x32 holdout falls below half the fitted prediction, OR the fit fails
FITTED status -> SATURATION: the author-axis rise is a small-panel transient,
not a law; the panel line closes, M4-F3's gauge-problem consequence stands
unqualified, and the registered next question becomes the M4-E2 objective
redesign with no panel-side escape remaining.

**Gates.**
- G0 designed null (above) — a rise voids the leg.
- G1 anchor: the kappa=0 free cell reproduces M4-F1's persisted `base1x` to
  <=1e-12 (as in M4-F2/M4-F3).
- G2 continuity: the authors x{1,2,4} shared cells at kappa=1.0 reproduce
  M4-F3's persisted values to <=1e-12 on identical world seeds (this leg
  extends that sweep, it does not re-derive it).
- G3 gauge invariance, equality-gated as in M4-F1 gate 2 / M4-F2 G3 / M4-F3 G3.
- G4 budget accounting: total events per cell reported exactly; the author
  axis necessarily grows total budget, so the leg reports cost per cell and
  makes NO fixed-budget claim (unlike M4-F2, which was a fixed-budget leg).

Tier: EXPLORATORY, label-free, synthetic-calibrated. Artifacts:
`results/m4_f4_author_axis/`; report
`reports/SUICA_M4_F4_AUTHOR_AXIS_REPORT.md`.

## M4-F4 outcome (2026-08-03, appended)

**3/3 leans HOLD; pivot does NOT fire. Verdict:
`AUTHOR_AXIS_LAW_EXTENDS_FEASIBLE_D3_VIA_RECRUITMENT`.** The author-axis law
M4-F3 measured on 3 points (gamma=1.104, CI [.719,1.454], not decisive by
registration) EXTENDS cleanly to 5 points spanning authors x{1,2,4,8,16}:
FITTED (5/5 qualifying), gamma=1.0959, bootstrap CI [0.9843, 1.2177] with
ZERO failed resamples (0/2000, the most stable bootstrap in this line's
history); local slopes 2.480/0.858/1.297/0.958 -- NOT monotonically
declining (the 4->8 step rises above 2->4); .5-agreement budget 46.11x
(~26,052 authors), five orders of magnitude below M4-F1's own free-response
events budget (1.08192e14x) and comfortably inside the registered <100x
bar; the authors-x32 held-out cell (never used in fitting) landed at 0.3861
against a pre-registered prediction of 0.4012 -- log-odds gap -0.0275
against a +/-0.3010 factor-2 band, the FIRST holdout in this line to
validate a FITTED law on its own decisive axis. All gates green.

**G0, the mandatory designed null, required a genuine post-hoc-but-disclosed
adjudication call (full derivation in the report's Part 0 addendum) --
recorded here plainly rather than smoothed over.** The raw per-cell `rise`
flag (the same threshold used throughout this line) fired on 2 of 10
independent null cells (author multiples 1 and 16, BOTH at kappa=0.5, the
non-decisive robustness axis; every kappa=1.0 -- the decisive -- cell showed
`rise=False` at all five multiples). Three supplementary readings, computed
on the already-persisted numbers with no re-run of any compute: (i) the
DECISIVE test -- a per-kappa Spearman trend of agreement vs author_mult,
the literal test of "rises WITH AUTHORS" -- found NO significant positive
trend at either kappa (kappa=1.0 rho=-0.100 p=0.873; kappa=0.5 rho=+0.400
p=0.505, and non-monotonic in the raw numbers); (ii) a multiplicity check
found 2/10 raw flags unremarkable under a true null
(`P(>=2 of 10)=6.56%` against a 4.28% per-cell false-positive rate);
(iii) a pooled grand-mean across all 10 null cells (+0.00246, t=2.99,
p=0.015) detected a small, non-authors-scaling BASELINE offset consistent
in sign and magnitude with M4-F1's own pre-existing base1x reference
(+0.0047, t=1.03, a world with zero cross-author structure of any kind) --
a claim about the gauge's level, not its slope with authors. G0 is
adjudicated PASS on the decisive trend test; the live axis at kappa=1.0
grows 0.006 -> 0.229 (37x, clearly trending) over the identical multiplier
range where the null stays flat and near-zero (including two cells with a
negative mean) -- a 50-80x magnitude gap at the top end, not a knife-edge
call. This determination is disclosed as having been made AFTER seeing G0's
raw numbers (unlike every other registered element of this leg), with every
underlying number reported so a reader can independently disagree.

Gates: G1 (direct reuse of `f2().run_gate_g1`) reproduces M4-F1's persisted
`base1x` identically. G2 (authors x{1,2,4} shared/kappa=1.0 reproduce
M4-F3's persisted cells) matched at EXACTLY 0.0 abs diff on every field
(agreement_mean/se, both D0 eff ranks, n_retained) -- bit-for-bit, since
this leg's live cells call `f3().run_sweep_world` with M4-F3's own identical
seed_key/corpus/budget_label for these three points. G3 (direct reuse of
`f3().run_gate_g3()`) bit-identical map and halving. G4: total allocated
events grow linearly and exactly with author_mult (13,202 / 26,404 / 52,808
/ 105,616 / 211,232 / 422,464 at 1x/2x/4x/8x/16x/32x), identical across
kappa at fixed mult; NO fixed-budget claim is made anywhere in the report,
per the registration's own instruction.

kappa=0.5 (non-gating context, per Part 0.3, mirroring M4-F3's own
treatment of its non-decisive kappa): ALSO cleanly FITTED (5/5, gamma=1.057,
CI [.789,1.225], 0/2000 bootstrap failures), budget 140.08x (~79,146
authors) -- above the primary line's <100x bar but still a finite,
enormously smaller number than any events-axis budget measured anywhere in
this program.

**Practical consequence.** RECRUITING MORE AUTHORS onto a shared-occasion
collection design is, on this synthetic instrument, a FEASIBLE certification
path for a D3 panel. This does NOT repair or reopen M4-F3's own merged
consequence on the EVENTS axis (still a GAUGE problem, connected to the
M4-E2 objective-redesign open problem, `OFFSET_SPREAD_NO_SINGLE_OBJECTIVE_TERM`)
-- that consequence stands unqualified on the axis it was measured on. This
leg's finding is an ADDITIVE escape route on a DIFFERENT axis (authors, not
events), not a repair of the events-axis finding. Full numbers, tables, and
the Part 0/addendum register-notes (including the mandatory G0 null-switch
disclosure, written before compute, and the G0 adjudication addendum,
written upon first seeing the gate's data) are in
`reports/SUICA_M4_F4_AUTHOR_AXIS_REPORT.md`.

## M4-F4 planner adjudication note (2026-08-03, appended)

The result stands as adjudicated (all three leans HOLD; saturation pivot does
not fire; author-axis law FITTED 5/5, gamma 1.096 [.984, 1.218], .5-agreement
budget 46.1x ~ 26,052 authors, x32 holdout predicted .4012 / observed .3861).
Two qualifications belong on the record, both surfaced by the executing agent
rather than found afterwards.

**1. G0 carried an ambiguity that the registration should have resolved in
advance, and the post-hoc resolution favoured the leg.** The registered text
said both "indistinguishable from zero at EVERY author multiple" (a per-cell
rule) and "if the null RISES with authors ... artifact" (a trend rule). Two of
ten null cells cleared t=2 (t=6.01 at x1/kappa=.5; t=3.24 at x16/kappa=.5),
so the per-cell reading fails while the trend reading passes decisively
(Spearman agreement-vs-multiple rho=-.100 p=.873 at the primary kappa=1.0;
+.400 p=.505 at kappa=.5). The agent adopted the trend reading, disclosed the
call as post-hoc, and supplied the multiplicity context (P(>=2 of 10 flagged |
true null) = 6.6%). The planner accepts that reading because the registered
RATIONALE for G0 named the scaling artifact specifically ("computed over more
field entries as authors grow"), and a level offset present at every multiple
is not that artifact. But the ambiguity is the planner's error, and the
finding carries this qualification: **G0 licenses "no authors-scaling
artifact", not "no offset".** Standing rule added for this line: any future
designed-null gate must state its aggregation rule (per-cell vs trend, and
the multiplicity treatment) BEFORE the run.

**2. The null offset is real and bears on the headline number.** The null's
pooled grand mean is +.00246 (t=2.99, p=.015), consistent in sign and size
with M4-F1's own zero-structure reference (+.0047). At x32 (agreement .386)
this is 0.6% of signal and immaterial; at x1 (.0061) it is ~40% of signal.
Since an offset lifts the SMALL-n points, it FLATTENS the log-log slope, so it
biases gamma DOWNWARD and the budget UPWARD -- i.e. 46.1x is conservative
rather than optimistic under this mechanism. That argument is recorded here
BEFORE it is tested; M4-F5 carries the offset-corrected refit as a registered
secondary check, and if the corrected budget instead grows by more than a
factor of 2, this note is wrong and the correction controls.

## M4-F5 registration (2026-08-03, BEFORE run) — is the certificate valid?

Four legs of this line have optimized ONE statistic: the deployed field's
internal split-half agreement. M4-F4 now says a feasible D3 panel exists at
~26,052 authors on shared occasions. Before that number is allowed to inform
any design, the gauge itself must be audited against truth, because this
program has already documented the exact pathology that would invalidate it:
in Leg 12 a cleaning intervention IMPROVED every loop statistic while LOWERING
the truth-referenced attribution correlation (.7264 -> .6677), and Leg 4b
showed an estimator manufacturing an apparent floor. Self-consistency and
correctness have moved in opposite directions in this line before.

**Question.** Does split-half agreement certify the field? Specifically: does
agreement co-move with truth-referenced recovery, and does the .5 target
correspond to a field worth having?

**Design.** Reuse M4-F4's exact swept cells (shared design, authors
x{1,2,4,8,16} plus the x32 cell, kappa in {0.5, 1.0}, 8 worlds x 20 draws,
gauge/map/D0/halving unchanged, identical world seeds). At every cell compute
BOTH:
- the split-half agreement already measured (must reproduce M4-F4's persisted
  values to <=1e-12 — gate G2 below), and
- TRUTH-REFERENCED RECOVERY: the same field-agreement functional evaluated
  between the finite-panel estimated field and the world's TRUE field.
The truth operationalization must be REGISTERED IN PART 0 BEFORE COMPUTE and
must be the identical deployed path applied to noise-free author
representations; report at least two variants (analytic noise-free, and a
large-sample asymptotic approximation) with their sensitivity, because the
choice is the leg's main researcher degree of freedom.

**Leans.**
(a) CO-MOVEMENT: truth recovery rises with agreement across every swept cell
    (Spearman >= .9 pooled), with no cell pair where agreement rises and truth
    recovery falls.
(b) TARGET ADEQUACY: at the .5-agreement point, truth recovery >= .7
    (interpolated on the measured curve; extrapolated with the status stated
    plainly if .5 is not reached in range).
(c) KAPPA STABILITY: at equal agreement, truth recovery at kappa=0.5 and
    kappa=1.0 differ by <= .1 — i.e. the agreement-to-truth mapping is a
    property of the gauge, not of how shared the occasions happen to be.

**PIVOT-IF:** any swept regime shows agreement rising while truth recovery
falls, OR truth recovery at the .5-agreement point is below .5 ->
THE GAUGE IS NOT A VALID CERTIFICATE. The .5 target, the 46.1x budget, and the
~26k-author D3 recommendation are all WITHDRAWN pending respecification of the
target against a truth-referenced criterion, and that respecification becomes
the registered next question. (Recording now, before the run: this outcome
would invalidate the most useful result this line has produced, and that is
precisely why the audit is being run before the number is used rather than
after.)

**Registered secondary check (not a lean).** Refit the M4-F4 author-axis law
after subtracting the per-cell G0 null offset, and report the corrected gamma
and .5-agreement budget. Pre-recorded expectation with its mechanism (see the
M4-F4 planner note): an offset lifts small-n points, flattens the log-log
slope, and therefore biases gamma DOWNWARD and the budget UPWARD, so the
corrected budget should be <= 46.1x. If instead it exceeds 46.1x by more than
a factor of 2, the planner note is wrong and the corrected number controls.

**Gates.**
- G1 anchor: kappa=0 free cell reproduces M4-F1's persisted `base1x` to
  <=1e-12 (as in M4-F2/F3/F4).
- G2 continuity: every reused cell reproduces M4-F4's persisted agreement to
  <=1e-12 on identical world seeds; a mismatch voids the comparison.
- G3 gauge invariance, equality-gated as in the prior legs.
- G4 truth-path invariance: the truth-referenced field must be produced by the
  IDENTICAL deployed featurize -> project -> field path as the estimate,
  differing ONLY in the input being noise-free; demonstrate this by an
  equality check on a degenerate case (truth path fed the finite sample must
  reproduce the finite-sample field exactly).

Tier: EXPLORATORY, label-free, synthetic-calibrated. Artifacts:
`results/m4_f5_gauge_validity/`; report
`reports/SUICA_M4_F5_GAUGE_VALIDITY_REPORT.md`.
