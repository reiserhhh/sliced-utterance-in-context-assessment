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

## Addendum 2 (2026-08-02): Legs 6-7 — the floor's interpretation changes from
## VARIANCE to BIAS; the variance-reduction fork of the design-change track is pruned

Leg 6 (pivot fired): per-event orthogonal excitation moves the pooled floor only
.0125 (.3902 -> .3777) — the C3.3 information limit extends to the OBJECT level;
excitation buys LAW information (e_orc_true .376 -> .292; flips 196 -> 167 / 73 -> 54)
but not disc-oracle resolution, and it does NOT stack with two-stage (.7387 < .7605,
negative in all five worlds).

Leg 7 (pivot fired; the planner's registered interpretation DIES): independent-
realization averaging leaves the floor R-invariant (.418/.400/.387/.381 at
R={1,2,4,8}; slope -.045 vs the predicted -.5; R=8 observed .381 vs .148 predicted).
The pivot profile decomposes the floor into TWO R-INVARIANT BIAS COMPONENTS:
law-level bias ~.37 (oracle-own-error, shared by both bases, flat in R — but
EXCITATION-RESPONSIVE per Leg 6) and basis-mismatch bias ~.13 (estimator-minus-
oracle gap, flat under everything tested). Leg 4b's oracle self-drift evidence
(.16-.26) reproduces but is COMMON-MODE — both bases wobble together while their
difference stays fixed; per-realization variance is only ~19.5% of the paired error
scale.

REVISED limit statement: the ~.39 floor is invariant to gauge correction, route
repair, event budget, per-event excitation, AND independent-realization averaging —
because it is BIAS, not variance. Candidate mechanisms, now separable by experiment:
(1) the V2 ridge penalty's non-vanishing regularization bias (noted at Leg 4:
the penalty scales with n by design; it is used in BOTH bases — consistent with the
shared law-level component); (2) hazard-family misspecification; (3) discovered-
frame subspace mismatch (the Leg-3 "span must match" thread) for the ~.13 gap.
Next levers, in registered order: de-biased derivative estimation + family
enlargement (law-level), subspace alignment (gap), paired/interventional occasions
(only if the bias levers fail).

## Addendum 3 (2026-08-02): Legs 8-9 — the floor's final anatomy: ridge
## self-infliction, common-mode cancellation, and the metric's true meaning

**Leg 8 (1/4 leans; pivot not triggered).** The law-level component ~.376 is largely
the V2 ridge's own non-vanishing penalty bias: lambda~1/n de-biasing cuts it to .261
at 1x (4/5 worlds <= .25) and — decisively — RESTORES textbook budget scaling
(log-log slope -.005 under V2 -> -.521 de-biased; 4x pooled .127).
**RETROACTIVE CORRECTION TO LEG 4b:** its "RESOLUTION_LIMIT / budget cannot buy
resolution" verdict was an artifact of the V2 penalty growing with n; under a
de-biased estimator, budget buys resolution at the textbook rate. The 4b
MEASUREMENT stands; its interpretation is corrected here (dated note; the 4b ledger
row remains as recorded per append-only discipline, with this addendum controlling).
Also: one-step family enlargement worsens (.480; unstable at 3.06 combined),
alignment INVERTS the basis gap (.136 -> .155 — not orientation), and de-biased D
DAMAGES paired transport (.625) — the third stacking failure.

**Leg 9 (1/3 leans; the registered pivot fires — the bias-variance account of the
paired floor is DEAD, informatively).** No ranking inversion at 4x (ts_lam1n .6488 <
ts_v2 .7538 registered column; .6862 < .7003 on the unregistered lam1n-referenced
secondary — no reference-bias rescue of the SIGN, though reference bias sets the
MARGIN: .1357 -> .0220). The signature's bias half INVERTED: paired bias of
de-biased estimators (.462/.642) EXCEEDS V2's (.381) because ridge shrinkage is
COMMON-MODE in the pairing and cancels — while against the LAW the same estimators
are exactly low-bias/high-variance (lam1n .2605 -> .0891 at R=8). The account was
right about the estimators and wrong about the metric.

**What the paired transport metric actually measures (consolidated).** Agreement
with the oracle-BASIS fit under shared estimation conventions: it rewards
common-mode shrinkage, punishes unilateral de-biasing, and its residual gap (.136)
is pinned by Leg 9's content swap to PER-CATEGORY ROW-DIRECTION CONTENT of the
discovered chart (basis-content share ~1.06-1.11; support-weighting ~0; oracle
directions + discovered norms eliminate the gap). Partition's resistance is 30.2%
reference-envelope artifact (.592 -> .413 corrected; residual real attenuation
c* ~ .43).

**The wall's story, three reductions deep:** geometry wall (dead, Leg 1) ->
estimator wall (routes repaired by two-stage, Leg 5; law-bias repaired by
de-biasing, Leg 8) -> METRIC READING (Leg 9): what remains in the paired diagnostic
is (i) direction content of discovery — the one object-level deficit left — and
(ii) the pairing's own common-mode structure, which is a property of the
truth-referenced diagnostic, not of the estimand. Next: direction-content anatomy
(Leg 10) with the conditioning profile elevated per the twice-registered hand-off.

## Final addendum (2026-08-02): the arc closes — the loop wall, fully decomposed
## in eleven legs

Leg 11 (pivot fired, informatively): the paired gap is SMOOTH at the oracle point in
3/3 high-gap worlds — a convex, near-quadratic basin (gap(theta) ~ theta^1.8; early
rise share 4.5-8.4% vs the 50% knee bar; interval slopes rise monotonically). Nothing
discrete flips: the evaluator's hard switches are inert along the entire path
(soft-assignment functional reproduces the hard curves to 1e-12). The all-or-nothing
reading of Leg 10 is WRONG (recorded); its decoupling is reinterpreted as PATH
ANISOTROPY — the scalar direction-deficit statistic is not a path coordinate, and
Legs 8/10's levers moved the frame in unproductive directions. The residual gap is
genuinely distributed direction content, accrued across the whole oracle->discovered
frame displacement (73-79% beyond t=.4).

**THE WALL, FINAL FORM (exploratory tier; truth-referenced diagnostic; V1/V2 NO-GOs
untouched).** The composite-loop paired transport deficit decomposes into exactly
four parts:
(i) ROUTE MISIDENTIFICATION under chart overspan — repairable by construction
    (two-stage route-then-refit; flips 196 -> 73; Legs 3/4a/5);
(ii) ESTIMATOR SELF-INFLICTION — the V2 penalty's non-vanishing bias, which also
    manufactured the illusion of a budget-invariant "structural floor" (Leg 4b,
    retroactively corrected); repairable by lambda ~ 1/n, restoring textbook
    n^(-1/2) budget scaling (slope -.005 -> -.521; .127 at 4x; Leg 8);
(iii) COMMON-MODE METRIC STRUCTURE — the pairing cancels shared shrinkage and
    punishes unilateral convention change; a property of the truth-referenced
    diagnostic, not of the estimand (Legs 6/7/9: three stacking failures explained;
    reference bias sets margins, not signs);
(iv) A SMOOTH, QUADRATIC-BASIN DIRECTION-CONTENT DEFICIT of the discovery step —
    the one genuine object-level residual (~.21-.23 in 3/5 worlds, ~.03-.07 in 2/5),
    not orientation (Leg 8), not norms or support weights (Leg 9), not safety-
    constraint price or conditioning starvation (Leg 10), not a discrete cliff
    (Leg 11): discovery simply lands a finite frame displacement from the oracle,
    and the gap grows near-quadratically along that displacement.

Consequence for future design: the productive lever for (iv) is not post-hoc
alignment polish (path-anisotropic, Leg 10) but reducing frame displacement AT
DISCOVERY — a better discovery objective is the registered future item, deferred
with the arc's closure. Interpretation discipline: (iii) means paired truth-
referenced diagnostics OVERSTATE operational deficits whenever estimation
conventions differ between sides; any future use of such diagnostics must state the
shared-convention assumption explicitly.

Registered-vs-outcome record of the arc (honesty table): 11 legs, 3 full-holds
(Legs 5, 6-lean-b-reading, 9-lean-b), 4 registered pivots fired exactly as
pre-committed (Legs 6, 7, 9, 11), 2 planner interpretations killed by their own
registered tests (per-realization variance, Leg 7; all-or-nothing, Leg 11), 1
retroactive correction of a prior leg's interpretation under append-only discipline
(Leg 4b, corrected in Addendum 3). The instruments decided, not the leans.

The M4-D arc is CLOSED. The loop's standing queue resumes: two-stage retrofit of the
M4-C.3 attribution NO-GO; R->V bridge heteroscedastic calibration.
