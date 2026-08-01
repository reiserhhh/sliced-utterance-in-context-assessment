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
