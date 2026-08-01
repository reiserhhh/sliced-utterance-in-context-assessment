# M4-D Synthesis — The Composite-Loop Transport Wall: Decomposition and Limit

Tier: EXPLORATORY (open-exploration phase, 2026-08-01/02). Synthesizes the four
registered M4-D legs (plan + outcomes: docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md;
reports/SUICA_M4_D_CURVATURE_LEG1_REPORT.md, ..._RELATION_BRIDGE_LEG2_REPORT.md,
..._OVERSPAN_CONTROL_LEG3_REPORT.md, ..._DLEG_FLOOR_LEG4_REPORT.md; ledger rows
M4-D.1..M4-D.4). Finite synthetic M4-C.2 worlds only; V1/V2 NO-GOs stand; no
natural-text, personality, or clinical claim.

## 1. The wall, fully decomposed

The M4-C arc left a four-NO-GO wall: atomic actions transport (.77-.98) while the
composite loop fails (.6519 pooled), and four repair families (RBF, Fisher-Wiener,
information frontier, attribution cube) all failed. M4-D dissects the wall into
exactly three layers plus one dead hypothesis:

**Dead: curvature/holonomy (Leg 1).** The gauge-seam commutator is causally inert:
within-cell rho(kappa, loop error) = .103; path-ordered seam correction WORSENS loops
(-.2815); a commutator-flat intervention still lifts loop geometry .523 -> .683.
The pooled Spearman .6977 was ecological. The wall is estimator-side.

**Layer 1 — route-selection flips under chart overspan (repairable).** Discovered
charts overspan the oracle frame (widths 12-13 vs 7), inflating the hazard feedback
parameterization; selection flips to `return` (D = 0, loop error 1) in 15.3% of
author-loops; flip count predicts world-rep loop geometry at rho = -.8044. Ridge on
the hazard feedback/gate coefficients with lambda selected by OUT-OF-FOLD
ROUTE-IDENTIFICATION ACCURACY (non-monotone in lambda; interior optimum lambda=.125)
cuts flips 196 -> 73 (-62.8%). Two structural sub-findings: (i) span must MATCH, not
merely shrink — naive width reduction under-spans and hurts (flips 228, geometry
.5641), and rank-matching is not subspace-matching (width-7 truncation still drops
mechanism directions, flips 1 -> 12); (ii) likelihood-based lambda selection is
monotone and binds at the grid boundary — the selection TARGET, not the penalty, was
Leg 3's binding constraint.

**Layer 2 — the D-leg mediates (confirmed twice).** Where any arm moves loop error at
all, it moves through creation-derivative error: within-cell rho(D-leg improvement,
loop improvement) = .61-.74; within cells D-leg error ranks remaining loop error
(rho .69) over the GC composite (.44).

**Layer 3 — the D-leg floor is structural (Leg 4b; the limit).** At the oracle-forced
route, D-leg error is budget-flat: pooled medians .459/.418/.391/.389 at event
budgets {0.5x, 1x, 2x, 4x}; overall log-log slope -.081 (an order of magnitude off
the estimator-limited -1/2); projected budget to reach e_d <= .25 is 721x pooled
(4.0e3x-5.5e6x in the failing worlds). Verdict unanimous 5/5 worlds on both primary
and true-referenced metrics: RESOLUTION_LIMIT. At 4x the discovered estimator (.389)
sits at the oracle frame's own finite-sample error scale (.367-.373, itself
budget-flat, with oracle self-drift .16-.26 across realizations): the floor is the
creation derivative's PER-REALIZATION VARIANCE plus non-vanishing regularization
bias — a property of the OBJECT under this observation design, not of the estimator.

## 2. The limit statement (T4-economics style, exploratory tier)

Under the current observation design (passive occasion streams, V2 event structure),
composite-loop transport geometry is bounded above by the intrinsic realization noise
of the creation derivative (~.39 paired-error scale in these worlds), and this bound
is invariant to: gauge/seam correction (Leg 1), route-selection repair (Leg 3/4a,
flips -63% buys +.0015-.038 geometry), and event budget (Leg 4b, slope -.08).
What events buy is route identification, not creation resolution. Only DESIGN change
can move the floor: richer per-event excitation (the C3.3 frontier), paired or
interventional occasions, or de-biased derivative estimators (the V2 ridge penalty's
bias does not vanish with n by design).

**Trade-off law (route-fidelity vs creation-fidelity).** At fixed design, route
stabilization and creation fidelity are competing objectives: the flip-optimal ridge
(lambda=.125) distorts D (median e_d .487 -> .783; creation geometry .774 -> .580;
the previously passing world falls .915 -> .753), while the D-optimal grid point
(lambda=.025 by discovery loop geometry) tolerates more flips. No single lambda
serves both; a two-stage design (route by penalized fit, D by unpenalized refit at
the selected route) is the natural next construction — unregistered, open.

## 3. The other M4-D deliverable — the typed R->V bridge (Leg 2)

suica_core/m4_relation_bridge.py implements the licensed conversion the V8 type
system reserved: rigidity index (spectral margin x noise-matched identity-stability)
licenses R -> V at tau = .5, refuses otherwise. Group-only worlds: 200/200 refusals,
zero false licenses, while author AUC stays .84-.90 — the vanishing-individuality
trap does not fool the gate. Controlled reproduction of the F18/X1 pattern: c2_joint
eps=1.5 yields within-group author AUC .9933 with rigidity .017 — near-perfect
DETECTION with zero licensable COORDINATES, now a planted-world phenomenon rather
than an empirical anecdote. Registered separation lean missed (.8691 vs .90; the
index encodes a stricter reconstructability standard than the registered label;
refuse-biased tpr .545 / fpr .021 at tau=.5) — recorded, not repaired, this phase.

## 4. What this closes and what it opens

Closed (exploratory tier): the loop wall's mechanism question — it is a three-layer
estimator/object phenomenon, not geometry; the budget question — events cannot buy
creation resolution at this design; the R->V question — a computable license now
exists with a perfect designed-null refusal record.

Open (next constructions, in registered-order preference): (1) two-stage
route-then-refit estimation (kills the trade-off law's dilemma if it works);
(2) design-change track for the D floor — per-event excitation richness (C3.3
frontier) as the first lever; (3) bridge index calibration for heteroscedastic
fields (Leg 2's C2 rank-cap note); (4) the lambda=.025 D-optimal battery
(one grid point, cheap, licenses the discovery-peak observation).

## Addendum (2026-08-02): Leg 5 closes the repairable half — the two-stage
## construction is registered and CONFIRMED

The "unregistered, open" two-stage construction of section 2 is now registered
(Leg 5, commit 85e1481) and confirmed with ALL THREE leans holding — the arc's first
full-hold leg: flips 73 (stage 1 = Leg 4a exactly, asserted at 1e-16), stage-2
median e_d .4481 (better than baseline .4869 — a route-mix effect, not a better
estimator: 94.3% flip-correct routes remove wrong-route D fits), pooled loop
geometry .7605 (the twice-missed .70 bar cleared by +.06), worlds >= .75: 3/5,
creation geometry .8234 (vs baseline .7736; stage 1 alone had destroyed it to .580).
The stage-1-damaged gated world finishes ABOVE baseline (.9152 -> .7527 -> .9479).

REFINED trade-off law: the DILEMMA is killed (route selection and creation
estimation are separable objectives — penalize for selection, refit unpenalized at
the selected route), while the SINGLE-LAMBDA clause survives (the licensed .025
battery is the best single-stage point, .7230, and still trades D away). What
remains below 1.0 is the Layer-3 structural floor: two-stage e_d .448 sits ~.03
above the 1x oracle-forced value (.418), and the two sub-.75 worlds (partition
.6527, compensation .6209) are exactly the two highest-floor worlds. The repairable
layers are now repaired BY CONSTRUCTION; all remaining movement belongs to the
design-change track (C3.3 per-event excitation, paired/interventional occasions,
de-biased derivative estimators). Boundaries unchanged: truth-referenced diagnostic,
V1/V2 NO-GO decisions stand, EXPLORATORY tier.
