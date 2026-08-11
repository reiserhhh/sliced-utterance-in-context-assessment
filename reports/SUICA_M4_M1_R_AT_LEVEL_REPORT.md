# M4-M1 — r-at-level on a decollinearized factorial

**Leg:** M4-M1 · **Registered** 2026-08-11 in
`docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md` (section "M4-M1 — r-at-level on a
decollinearized factorial"), commit `140e927`, BEFORE this run.
**Executor:** dispatched agent (implementation and execution only; the
registration text is binding).
**Harness:** `scripts/run_suica_m4_m1_r_at_level.py`.
**Artifacts:** `results/m4_m1_r_at_level/` (gitignored).
**Banner:** synthetic worlds on K2b's frozen instrument, exploratory, label-free;
a share × φ factorial that sets out to break K2f's −0.964 r/V collinearity.

**Verdict: `STOP_DESIGN_INFEASIBLE` (rule-16 cell 1).** STOP_DESIGN_INFEASIBLE (planner defect; no fit is run)

**0 worlds were generated.** The leg stopped inside Part 0,
before the pilot, on the registration's own pre-declared ladder.

K2f left one question: the level law's intercept might hide `λ·r^q`, but its 26
rows could not say, because `corr(r, V) = -0.9643543785903034`. M1's design answer
was a share × φ factorial — φ moves `r` at exactly fixed `V`, since
`person_share_design` has no φ argument. That premise is **true and verified
here**. What fails is its magnitude. On the registered grid the factorial moves
the collinearity only from `-0.9643543785903034` to `-0.9407871367652862`; after the
pre-declared one-step φ extension it reaches `-0.9107365249638539`. Gate G1m(d)
demands `|corr(r, V)| ≤ 0.3`. The realized value is
**3.03578841654618× the bar**, and the diagnostic below shows the bar is not
merely missed but **unreachable**: over *every* 5-point φ ladder at the
registered shares the infimum of `|corr(r, V)|` is `0.748768093111513` —
**2.4958936437050436× the bar**. No φ schedule exists that satisfies the gate the
registration wrote.

Per the registration, that routes to cell 1 and the planner owns the defect.
No pilot ran; no fit ran; no lean was evaluated.

---

## Part 0 — written before any world

Part 0 was computed and persisted (`results/m4_m1_r_at_level/part0.json`,
`part0_tables.md`) before a single world could exist; the world-building entry
points are wrapped by a permit gate that Part 0 never opened.

### 0.1 Rule 9 / rule 12 — open conventions, pinned in writing

| note | pinned reading |
|---|---|
| RN-M1-1 | carrier inheritance: int_share 0, w_int_arm 'zero', K2b panel pins, recovery_b_only, cell level = mean over worlds; M1's OWN master_seed and salts control; no K2d dispatcher needed (no int: carrier) |
| RN-M1-2 | seed string pinned: v8.stable_bucket(f'{MASTER_SEED}-{share!r}-{phi!r}-{world}', salt=<m4m1-world\|m4m1-pilot>, modulus=2**31-1); streams disjoint by salt |
| RN-M1-3 | G2m liveness gates on the k2b-side realized card attenuation r_card_b_raw at world grain (k2b:392-503 + :505-509 + :486, the object k2b's own G2 uses at :944-963); it is not written into any persisted per-world field CSV (k2b:633-646), so the declared field-contrast fallback is ALSO computed and reported; the card statistic controls |
| RN-M1-4 | corr = Pearson, verified by reproducing K2f's -0.9643543785903034 from compiled_rows.csv before any M1 number is used |
| RN-M1-5 | stage chunking: G3m(b) runs as its own foreground stage `power` between `pilot` and `worlds_a`; the >=10xB rule-13 re-run as its own stage `rule13`; ordering unchanged and permit-gated |
| RN-M1-6 | lambda-vs-zero boundary: adjacent iff min(\|lo\|,\|hi\|) <= 0.05*\|lambda_hat\| |
| RN-M1-7 | L-4 monotonicity read BOTH ways (sign-agreement; and \|rho\|==1 plus sign agreement); L-4 adjudicates nothing so neither is adopted |
| RN-M1-8 | the STOP diagnostic: on truth-table cell 1 the `diagnose` stage measures HOW unsatisfiable gate (d) is (the infimum of \|corr(r,V)\| over all 5-point phi ladders at the registered shares, and the best reachable value with shares also freed inside gate (a) subject to gate (b)); pure design arithmetic, deterministic, adopted as NOTHING -- the verdict is the registered STOP |

RN-M1-8 was added **after** G1m failed and **before** any world existed — zero
worlds were generated in this leg, so no hypothesis-relevant number existed at
any point in its authorship. It adopts nothing; it measures the defect.

### 0.2 G0m — the anchors, bit-exact

Every anchor and **every K2f, D-open and theory-document number the
registration quotes** re-derives bit-exactly. There is no citation defect: the
registration's facts are accurate, and the design premise they support is real.

| clause | registration / expected | re-derived / persisted | bit-exact |
|---|---|---|---|
| (i) predicted_attenuation(0.40, 0.90) | 0.6185853753498524 | 0.6185853753498524 | True |
| (ii-a) predicted_attenuation(0.45, 0.90) | 0.5889058864943755 | 0.5889058864943755 | True |
| (ii-b) person_share_design(0.45, 0.0) | 0.13500000000000004 | 0.13500000000000004 | True |
| (iii) person_share_design(0.40, 0.0) | 0.12000000000000004 | 0.12000000000000004 | True |
| F2 LOO-RMSE (fits.json:L-1.best_loo_rmse) | 0.0061559195350209 | 0.0061559195350209 | True |
| F2 LOO-RMSE (loo.json:loo.F2.loo_rmse) | 0.0061559195350209 | 0.0061559195350209 | True |
| F2 kappa' | 0.750086268225045 | 0.750086268225045 | True |
| F2 kappa' ci95 hi | 0.8612166024267973 | 0.8612166024267973 | True |
| F2 kappa' ci95 lo | 0.5202855978239498 | 0.5202855978239498 | True |
| F2 lambda' | 0.18021628978547316 | 0.18021628978547316 | True |
| F2 p | 0.2064406330042716 | 0.2064406330042716 | True |
| F2 q' | -0.009622064624441264 | -0.009622064624441264 | True |
| F2 q' ci95 hi | 0.5313115708778163 | 0.5313115708778163 | True |
| F2 q' ci95 lo | -0.3792124136721057 | -0.3792124136721057 | True |
| K2f n_rows | 26.0 | 26.0 | True |
| corr(r, V) over the 26 K2f rows (Pearson, RN-M1-4) | -0.9643543785903034 | -0.9643543785903034 | True |
| r(0.30, 0.90) | 0.6758917867864564 | 0.6758917867864564 | True |
| r(0.30, 0.98) | 0.645057248597175 | 0.645057248597175 | True |
| r(0.50, 0.90) | 0.558364277337817 | 0.558364277337817 | True |
| r(0.50, 0.98) | 0.5193517935368367 | 0.5193517935368367 | True |
| share envelope hi | 0.6634207990183637 | 0.6634207990183637 | True |
| share envelope lo | 0.02 | 0.02 | True |
| (v) Dopen:M-4 level, mean of the raw per-world CSV | 0.09350089316336324 | 0.09350089316336324 | True |
| (vi) `[1.71, 1.98]` verbatim in `docs/SUICA_IDENTITY_THEORY_V1.md` | [1.71, 1.98] | found on lines [805, 841] | True |

The correlation convention is pinned by this table, not asserted: Pearson
reproduces K2f's quoted `-0.9643543785903034` from `compiled_rows.csv` bit-exactly
(RN-M1-4), which is what licenses reading gate (d)'s "corr" as Pearson.

### 0.3 G1m — the realized 20-point design

Shares `[0.1, 0.25, 0.4, 0.6]` × φ `[0.45, 0.6, 0.75, 0.9, 0.98]` (the ladder after the pre-declared
extension). `r` from `predicted_attenuation`
(`scripts/run_suica_m4_k2c_matched_pairs.py:186-191` → `k2b:533-583`);
`V_person` from `person_share_design`
(`scripts/run_suica_m4_k2e_double_matching.py:234-241` → `k2b.arm_shares`),
never assumed linear.

| cell | share | phi | r_pred | V_person |
|---|---|---|---|---|
| s0.10_p0.45 | 0.1 | 0.45 | 0.8123639923140352 | 0.03000000000000001 |
| s0.10_p0.60 | 0.1 | 0.6 | 0.8075174172340943 | 0.03000000000000001 |
| s0.10_p0.75 | 0.1 | 0.75 | 0.7995275310963105 | 0.03000000000000001 |
| s0.10_p0.90 | 0.1 | 0.9 | 0.7849057220233866 | 0.03000000000000001 |
| s0.10_p0.98 | 0.1 | 0.98 | 0.7718092954224756 | 0.03000000000000001 |
| s0.25_p0.45 | 0.25 | 0.45 | 0.7679524387198792 | 0.07500000000000002 |
| s0.25_p0.60 | 0.25 | 0.6 | 0.7558507450373838 | 0.07500000000000002 |
| s0.25_p0.75 | 0.25 | 0.75 | 0.7366550589077502 | 0.07500000000000002 |
| s0.25_p0.90 | 0.25 | 0.9 | 0.7037278906663471 | 0.07500000000000002 |
| s0.25_p0.98 | 0.25 | 0.98 | 0.6763691758553391 | 0.07500000000000002 |
| s0.40_p0.45 | 0.4 | 0.45 | 0.7131718346406168 | 0.12000000000000004 |
| s0.40_p0.60 | 0.4 | 0.6 | 0.6941115392115328 | 0.12000000000000004 |
| s0.40_p0.75 | 0.4 | 0.75 | 0.6651298285270342 | 0.12000000000000004 |
| s0.40_p0.90 | 0.4 | 0.9 | 0.6185853753498524 | 0.12000000000000004 |
| s0.40_p0.98 | 0.4 | 0.98 | 0.5825497814736654 | 0.12000000000000004 |
| s0.60_p0.45 | 0.6 | 0.45 | 0.6151816160755695 | 0.18000000000000005 |
| s0.60_p0.60 | 0.6 | 0.6 | 0.5883719155687073 | 0.18000000000000005 |
| s0.60_p0.75 | 0.6 | 0.75 | 0.5501066652075185 | 0.18000000000000005 |
| s0.60_p0.90 | 0.6 | 0.9 | 0.49394543808531227 | 0.18000000000000005 |
| s0.60_p0.98 | 0.6 | 0.98 | 0.4541409476972356 | 0.18000000000000005 |

### 0.4 The gates — four pass, one fails

| gate | bar | realized (fallback ladder) | PASS |
|---|---|---|---|
| (a) shares inside the trained envelope | [0.02, 0.6634207990183637] | [0.1, 0.25, 0.4, 0.6] | True |
| (b) V max/min | >= 2.0 | 6.0 | True |
| (c) within-share r max/min | >= 1.2 in >= 2 share levels | 2/4 levels | True |
| **(d) cross-cell abs(corr(r, V))** | **<= 0.3** | **0.9107365249638539** | **False** |
| (e) duplicate (r, V) design points | 0 | 0 | True |

Gate (c) is the near miss that the ladder repaired. On the **registered base**
ladder only **1** of 4 share levels reached the
`1.2` within-share `r` ratio, against a requirement of
**2**; the pre-declared extension to `[0.45, 0.6, 0.75, 0.9, 0.98]`
lifted that to **2**, realized ratios
`[1.0525449708005403, 1.13540425278654, 1.2242247054603972, 1.3546050387988702]`. So the fallback ladder did exactly the job it was
written for — and gate (d) still fails behind it.

| share | V_person | r min (at the ladder's phi MAX) | r max (at the ladder's phi MIN) | max/min | meets (c)'s 1.2 |
|---|---|---|---|---|---|
| 0.1 | 0.03000000000000001 | 0.7718092954224756 | 0.8123639923140352 | 1.0525449708005403 | False |
| 0.25 | 0.07500000000000002 | 0.6763691758553391 | 0.7679524387198792 | 1.13540425278654 | False |
| 0.4 | 0.12000000000000004 | 0.5825497814736654 | 0.7131718346406168 | 1.2242247054603972 | True |
| 0.6 | 0.18000000000000005 | 0.4541409476972356 | 0.6151816160755695 | 1.3546050387988702 | True |

### 0.5 Gate (d) — the failure, under both correlation conventions

| phi ladder | values | Pearson corr(r, V) | Spearman corr(r, V) | Pearson corr(r^1.8528700746510731, V) | passes (d) (<= 0.3) |
|---|---|---|---|---|---|
| registered base ladder | [0.6, 0.7, 0.8, 0.9, 0.98] | -0.9407871367652862 | -0.953947083225262 | -0.9486310889025732 | False |
| pre-declared fallback ladder | [0.45, 0.6, 0.75, 0.9, 0.98] | -0.9107365249638539 | -0.9306800811953776 | -0.9213071767159029 | False |
| G2m liveness fallback ladder | [0.9, 0.92, 0.94, 0.96, 0.98] | -0.99515544292931 | -0.9694584179118516 | -0.9949002231553672 | False |
| K2f's 26 published rows (the object M1 set out to break) | -- | -0.9643543785903034 | -- | -- | -- |

Pearson `-0.9107365249638539`, Spearman `-0.9306800811953776`, and
`corr(r^q, V)` at the sealed response exponent `-0.9213071767159029`: the
failure is not an artifact of the convention. The registration's own headline
comparison — M1's number "against K2f's `-0.9643543785903034`" — is the right
comparison, and it shows the factorial buying a reduction of
`-0.9643543785903034` → `-0.9107365249638539` where the gate needed
`0.3`.

---

## The satisfiability diagnostic (RN-M1-8) — how far from satisfiable

Cell 1 obliges a STOP, not a repair. To make the handoff actionable, the
`diagnose` stage measures *how* unsatisfiable gate (d) is. This is pure design
arithmetic on the pinned deterministic maps: no world, no field, no fit.

| search | best abs(corr(r, V)) reachable | bar | multiple of the bar | gate (d) satisfiable? |
|---|---|---|---|---|
| all 5-point distinct phi ladders, shares PINNED as registered | 0.748768093111513 | 0.3 | 2.50x | False |
| shares ALSO freed inside gate (a), subject to gate (b)'s V max/min >= 2 | 0.5208187741410987 | 0.3 | 1.74x | False |
| as registered (base ladder) | 0.9407871367652862 | 0.3 | 3.14x | False |
| after the pre-declared fallback ladder | 0.9107365249638539 | 0.3 | 3.04x | False |

**At the registered shares, gate (d) is unsatisfiable by construction.** The
infimum of `|corr(r, V)|` over every 5-point distinct φ ladder in
`(0.001, 0.999)` is `0.748768093111513` = **2.4958936437050436× the bar**, attained at the
degenerate ladder `[0.001, 0.011081, 0.021162, 0.988919, 0.999]` — three points crushed against one end of the φ
interval and two against the other, i.e. the most extreme φ leverage the family
can produce. Freeing the shares as well, inside gate (a)'s envelope and subject
to gate (b)'s `V max/min ≥ 2.0`, the best of
4000 seeded draws (474 rejected by gate (b)) is
`0.5208187741410987` = **1.736062580470329× the bar** — an upper bound on that infimum,
already above it.

### Why: φ's ceiling against share's floor

| share | V_person | r at phi=0.001 | r at phi=0.999 | max r span over the FULL open phi interval | max r ratio | can EVER meet (c)'s 1.2 |
|---|---|---|---|---|---|---|
| 0.1 | 0.03000000000000001 | 0.8194500377620684 | 0.767859946888953 | 0.05159009087311539 | 1.06718684974016 | False |
| 0.25 | 0.07500000000000002 | 0.7863172924207741 | 0.668474119387579 | 0.11784317303319514 | 1.1762868144261993 | False |
| 0.4 | 0.12000000000000004 | 0.7433829153532475 | 0.5725454440034959 | 0.17083747134975158 | 1.2983823784452444 | True |
| 0.6 | 0.18000000000000005 | 0.6608028701723697 | 0.44357568870685093 | 0.21722718146551878 | 1.4897184110761292 | True |

V is EXACTLY a linear function of share (V/share = 0.3 at every share tested), and r is monotone decreasing in share, so share alone drives r and V in lockstep. phi is the only knob orthogonal to V, and its TOTAL leverage over the full open interval (0.001, 0.999) is at most 0.21722718146551878 in r (at share 0.6) against a between-share r span of 0.2909602839380743 at fixed phi. Gate (b) REQUIRES V max/min >= 2, i.e. a share range wide enough to make the between-share r spread dominate; gate (d) requires the within-share (phi-driven) spread to dominate instead. In this world family both cannot hold at once.

Two consequences worth naming separately. First, gate (c)'s `1.2` bar is
reachable in only **2 of the 4 registered share
levels for any φ ladder whatsoever** — at shares
`[0.1, 0.25]` the full open φ interval cannot produce a
`1.2` ratio — so the registration's "at least
2 share levels" was, unknowingly, demanding *all* of the
levels that can ever comply. Second, gate (b) and gate (d) pull on the same
knob in opposite directions: (b) needs a wide share range so `V` varies, and a
wide share range is exactly what makes `r` track `V`.

| search | argmin phi ladder | argmin shares | V max/min |
|---|---|---|---|
| shares PINNED | [0.001, 0.011081, 0.021162, 0.988919, 0.999] | [0.1, 0.25, 0.4, 0.6] | 6.0 |
| shares freed | [0.031242, 0.12197, 0.293343, 0.434475, 0.958677] | [0.151984, 0.217976, 0.250972, 0.333461] | 2.1940533214022526 |

---

## What was not run, and why

The registration's cell 1 reads "no fit is run", and the ordering discipline
puts the pilot after the Part-0 gates. Accordingly:

- **G2m (the 16-world pilot): not reached.** No liveness measurement, no
  `σ_w`, no per-world field value exists for this leg.
- **G3m(b) (the power projection): not reached** — it needs pilot `σ_w`.
- **The 640 main worlds: not generated.** The permit gate was
  never opened; `ordering_log.jsonl` records the refusal path unused because
  the leg stopped before arming.
- **The fit: not run.** No winner form, no bootstrap CI, no LOO-RMSE.

The report therefore carries **no per-cell results table, no fit table, no
bootstrap CIs and no L-4 residual pattern** — those tables have no artifact to
be generated from, and rule 24 forbids typing them. The four pre-declared forms
and the optimizer pins were nevertheless fixed in Part 0 before the stop, and
are recorded here so the next registration inherits them unchanged:

| form | expression | params | starts | bounded |
|---|---|---|---|---|
| F1 | field = lambda*r^q - kappa*V | ['lambda', 'q', 'kappa'] | 54 | False |
| F1e | field = lambda*r^q - kappa*V - epsilon, epsilon in [0, 0.05] | ['lambda', 'q', 'kappa', 'epsilon'] | 162 | True |
| F2 | field = lambda*r^q - kappa*V*r^p | ['lambda', 'q', 'kappa', 'p'] | 162 | False |
| F3 | field = (lambda - kappa*V)*r^q | ['lambda', 'q', 'kappa'] | 54 | False |

| pin | value |
|---|---|
| bounds | unbounded, x_scale=1.0, EXCEPT F1e's epsilon in [0, 0.05] |
| epsilon_bounds | [0.0, 0.05] |
| ftol | 1e-14 |
| gtol | 1e-14 |
| jac | 2-point (numerical) |
| loo_starts | the same grid PLUS the full-data optimum |
| loss | linear (plain least squares) |
| max_nfev | 20000 |
| method | trf |
| n_starts | {'F1': 54, 'F1e': 162, 'F2': 162, 'F3': 54} |
| routine | scipy.optimize.least_squares |
| same_optimum_sse_tol | 1e-12 |
| scipy_version | 1.17.1 |
| selection | leave-one-CELL-out RMSE (20 refits per form, full grid + full-data optimum) |
| xtol | 1e-14 |
| start grid | {'epsilon': [0.0, 0.01, 0.03], 'kappa': [0.0, 0.7220359963712748, 2.0], 'lambda': [0.05, 0.17417497661611914, 0.5], 'p': [0.0, 1.0, 1.8528700746510731], 'q': [-0.5, 0.0, 0.5, 1.0, 1.8528700746510731, 3.0]} |

---

## Routing — the rule-16 truth table, reproduced verbatim

| # | condition | outcome |
|---|---|---|
| 1 | any Part-0/pilot gate fails after its declared ladder | **STOP_DESIGN_INFEASIBLE (planner defect; no fit is run)**  <-- THIS LEG |
| 2 | L-1 MISS AND winner lambda CI contains 0 | R_TERM_ABSENT_AT_LEVEL -- the tax-only level law is the COMPLETE level story on this family; level-response dissociation named; q-at-level closes as structurally unposed; M2 proceeds on the tax-only form |
| 3 | L-1 MISS AND winner lambda CI excludes 0 | NON_IDENTIFIED_UNDERPOWERED -- CI reported, no q claim; M2 blocked; leverage redesign named |
| 4 | L-1 HOLD AND L-2 below | LEVEL_RESPONSE_DISSOCIATION -- q measured at level, below the response band; new named phenomenon; M2 seals the measured law |
| 5 | L-1 HOLD AND L-2 overlap | SINGLE_EXPONENT_RESTORED -- T4's level form completed with the response exponent; M2 seals |
| 6 | L-1 HOLD AND L-2 above | ABOVE_BAND_ANOMALY -- named; M2 seals the measured law; theory note required |
| -- | L-3 disjoint (either side), any cell 2-6 | modifier TAX_SHIFT_AT_LEVEL -- pre-registered anomaly fed into M3's charter |
| -- | L-3 overlap, any cell 2-6 | modifier: kappa's fourth independent appearance is counted |

The L-3 modifier row is defined only for cells 2-6 and therefore does not
apply. The enumeration is the registration's own; cell 1 is the cell this leg
lands in, and it is reached through the gate ladder rather than through any
lean.

## Leans

| lean | clause | sided | prior | verdict | why |
|---|---|---|---|---|---|
| L-1 | winner's q 95% bootstrap CI width <= 0.6 | one-sided | 0.55 | **NOT EVALUATED** | cell 1: no fit is run |
| L-2 | winner's q CI against the response band [1.71, 1.98]: entirely below / overlap / entirely above | two-sided | below .55 / overlap .35 / above .10 | **NOT EVALUATED** | conditional on L-1; no fit is run |
| L-3 | winner's kappa CI overlaps K2f F2's kappa' ci95 [0.5202855978239498, 0.8612166024267973] | two-sided overlap; disjoint-low and disjoint-high both named | 0.7 | **NOT EVALUATED** | defined in cells 2-6 only; no fit is run |
| L-4 | within each share level, Spearman(residual, phi) across the 5 phi cells; monotone same-sign in >=3/4 share levels is the named finding 'phi leaks past (r, V)' | reading only, NO gate | -- | **NOT EVALUATED** | a reading on the winner's residuals; there is no winner |

## Sides declared in Part 0 (rule 22)

| clause | statement | sided | improvement side |
|---|---|---|---|
| L-1 | winner's q 95% bootstrap CI width <= 0.6 | one-sided | DOWN (smaller width is better) |
| L-2 | winner's q CI against the response band [1.71, 1.98]: entirely below / overlap / entirely above | two-sided | neither -- all three outcomes are informative and named |
| L-3 | winner's kappa CI overlaps K2f F2's kappa' ci95 [0.5202855978239498, 0.8612166024267973] | two-sided overlap; disjoint-low and disjoint-high both named | neither -- containment/overlap |
| L-4 | within each share level, Spearman(residual, phi) across the 5 phi cells; monotone same-sign in >=3/4 share levels is the named finding 'phi leaks past (r, V)' | reading only, NO gate | n/a |
| G1m(a) | all shares inside [0.02, 0.6634207990183637] | two-sided containment | neither |
| G1m(b) | V max/min >= 2.0 | one-sided | UP |
| G1m(c) | within-share r max/min >= 1.2 in at least 2 share levels | one-sided | UP |
| G1m(d) | cross-cell \|corr(r, V)\| <= 0.3 | one-sided on the absolute value | DOWN |
| G1m(e) | no duplicate (r, V) design points | exact | n/a |
| G2m(i) | all per-world fields finite and strictly inside (0, 1) | two-sided containment | neither |
| G2m(ii) | at share 0.60, \|realized card-attenuation contrast between the corner phis\| > 2.0x its pooled SE | one-sided | UP |
| G3m(b) | projected q width proxy <= 0.5 under BOTH q truths (stricter than L-1's 0.60 to absorb proxy slack) | one-sided | DOWN |

## Gates

| gate | PASS | detail |
|---|---|---|
| G0m | True | every anchor and every K2f / D-open number quoted in the registration re-derived bit-exactly; no citation defect |
| G1m | False | gates (a), (b), (c) and (e) pass on the fallback ladder; gate (d) FAILS on the base ladder and again after the pre-declared one-step extension |
| G2m | None | not reached -- the pilot runs only after G0m/G1m (registration ordering) |
| G3m | None | (a) sides and (c) stage estimates written in Part 0; (b) the power projection needs pilot sigma_w and was not reached |
| G4m | True | rule-16 truth table reproduced verbatim; every report table generated from artifacts |

---

## Anomaly log — every anomaly, with pre/post-hypothesis timing

**No hypothesis-relevant number ever existed in this leg: 0
worlds were generated and no fit was run.** Every anomaly below is therefore
*pre-hypothesis* by construction, and each is stated with the point in the run
at which it was resolved.

- **A-1 — the interpreter did not exist (resolved BEFORE Part 0, i.e. before
  any number of any kind).** The dispatch said a working interpreter with
  pandas/scipy/numpy/pytest was present. It was not: the only pandas on this
  machine belongs to `/usr/bin/python3` (CPython 3.9.6), and the published
  machinery imports `datetime.UTC`, which is 3.11+. `k2b`, `k2c`, `k2d`, `k2e`
  and the K2f harness all fail to import there. A CPython 3.12.12 virtual
  environment was built outside the repository and populated from
  `requirements-lock-main.txt` verbatim, reproducing the lock exactly
  (numpy `2.4.4`, pandas `3.0.2`, scipy `1.17.1` — the same pins the
  lock records for the environment that passed the 970-test suite). Platform
  `macOS-26.4.1-arm64-arm-64bit`. The suite was run on it BEFORE any leg code was written, as a
  baseline.
- **A-2 — `timeout(1)` is absent on this platform (resolved before Part 0).**
  The execution convention requires explicit per-stage timeouts. macOS ships no
  `timeout`; every stage was instead run as its own foreground command under an
  explicit harness-level timeout, all well under the 600 s ceiling.
- **A-3 — G1m failed on the base ladder (Part 0, before the pilot).** Gates (c)
  and (d) both failed; the pre-declared rule-17 ladder fired automatically
  inside `part0`, repaired (c), and left (d) failing. This is the leg's outcome,
  not an incident, and it is recorded here because the ladder firing is itself a
  reportable event.
- **A-4 — Part 0 was executed more than once (every run before any world).**
  The first run produced the STOP; the `diagnose` stage and RN-M1-8 were then
  added to the harness, and `part0` was re-run so the persisted artifact matches
  the committed script. `ordering_log.jsonl` was reset once before the final
  clean pass so the log it carries is the run that produced the committed
  artifacts, end to end; the earlier runs are therefore not in it, and this note
  is the record of them. The arithmetic is deterministic and identical across
  every run — `corr(r, V)` was `-0.9107365249638539` each time — and no world
  existed during any of them.
- **A-5 — an exploratory diagnostic overran and was killed (before the
  `diagnose` stage was written).** A first, unbatched search called
  `predicted_attenuation` inside an optimizer loop and exceeded its foreground
  timeout; it was killed and rewritten to precompute `r` on a fixed
  100-point φ grid, which runs in `2.0728750228881836` s. No number
  from the killed run appears anywhere in this leg; the committed `diagnose`
  stage is deterministic and reproduces the reported values from scratch.
- **A-6 — rule 24 caught two of this leg's own errors before commit.** (i) The
  diagnostic's prose originally described the registration's cited φ leverage
  at share 0.30 as "a 4.6% move"; recomputed from the anchors it is
  `4.780124284524867`%. The string is now generated from the anchor values rather
  than typed. (ii) The within-share leverage table's column headers read "r at
  phi min" / "r at phi max" while the cells carry `r.min()` / `r.max()` — and
  because `r` is monotone DECREASING in φ these are the opposite φ endpoints,
  so the headers were mislabelled (the numbers were right). Both were caught by
  reading the generated table back against the artifact, which is exactly the
  K2f convention doing its job on the executor. A third, `V max/min ≥ 6.0`,
  where 6.0 is the design's REALIZED ratio and the gate's bar is
  `2.0`, was caught the same way and is now a generated
  placeholder.
- **A-7 — no stage approached its 2× stop-and-report threshold.** Part 0 ran in
  `0.042912960052490234` s against a 60 s estimate; `diagnose` in
  `2.0728750228881836` s against a 120 s executor estimate.

| stage | registration estimate (s) | executor estimate (s) | measured (s) |
|---|---|---|---|
| part0 | 60 | 60 | 0.043 |
| diagnose | -- | 120 | 2.073 |
| pilot | 30 | 30 | -- (not reached) |
| power | -- | 120 | -- (not reached) |
| worlds_a | 120 | 120 | -- (not reached) |
| worlds_b | 120 | 120 | -- (not reached) |
| worlds_c | 120 | 120 | -- (not reached) |
| worlds_d | 120 | 120 | -- (not reached) |
| fit | 300 | 300 | -- (not reached) |
| rule13 | -- | 180 | -- (not reached) |
| finalize | 60 | 60 | -- (not reached) |

| component | value |
|---|---|
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| platform | macOS-26.4.1-arm64-arm-64bit |
| python | 3.12.12 |
| python_executable | /private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python |
| scipy | 1.17.1 |

---

## What the planner should carry forward

**The defect.** Rule-11 satisfiability, and rule-18 JOINT satisfiability across clauses sharing generative knobs: gate (b) and gate (d) share `share`, and the registration checked neither jointly nor arithmetically against the bar it wrote. The registration's own cited facts already contained the warning -- it quotes r(0.30, 0.90) = 0.6758917867864564 vs r(0.30, 0.98) = 0.645057248597175, a 4.78% move, and never asked what correlation a knob that small can buy against a share axis that moves r by 0.2910 at fixed phi.

**What the registration got right, and it matters.** The DIRECTION is real and verified: phi does move r at exactly fixed V (gate (c) passes in 2 of 4 share levels on the fallback ladder), and the factorial does reduce the collinearity -- from K2f's -0.9643543785903034 to -0.9407871367652862 (base) and -0.9107365249638539 (fallback ladder). What fails is MAGNITUDE, not sign. The M1
mechanism section is not wrong about the physics of the design — φ really does
move `r` at exactly fixed `V`, and G0m confirms every number it cites. The
registration's error is that it never converted its own cited φ leverage into
the correlation the gate would see.

**What this rules out.** Any share × φ factorial in this world family, at the
registered shares, cannot decollinearize `r` from `V` to `0.3` — the
floor is `0.748768093111513`. Widening φ does not help: the infimum above already
uses the whole open interval. Re-choosing shares inside the trained envelope
does not rescue it either while gate (b) stands, since the best reachable value
found is `0.5208187741410987`.

**Where the leverage would have to come from.** `V` is an exact linear function
of share in this family (`V/share = 0.3`), so as long as the only
two knobs are share and φ, `V` is share and the design has one effective axis
plus a weak second. Decollinearizing `r` from `V` at level needs a knob that
moves `r` *without* moving share — or a `V` that is not a function of share
alone. The `int_share` carrier that M1 pinned to zero (inheriting K2F-FRESH) is
the obvious candidate: `person_share_design(share, int_share)` sums the slow and
interaction shares, so a non-zero interaction carrier moves `V` at fixed share,
which is a second axis in exactly the place the current design has none. That is
a re-registration question, not an executor's choice, and nothing here adopts
it.

**Also worth re-registering with the bar.** Gate (c)'s
`1.2` within-share ratio is reachable in only
2 of the 4 registered share levels for any φ
whatsoever, and gate (d)'s bar is unreachable at any. Both bars want a
generator-derived feasibility argument (rule 17) or an arithmetic satisfiability
check (rule 11) computed jointly (rule 18) before the next registration is
committed — which is precisely the arithmetic this leg's Part 0 performs in
`0.042912960052490234` s.
