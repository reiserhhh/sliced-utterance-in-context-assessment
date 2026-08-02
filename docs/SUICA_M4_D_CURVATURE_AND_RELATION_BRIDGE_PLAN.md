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
