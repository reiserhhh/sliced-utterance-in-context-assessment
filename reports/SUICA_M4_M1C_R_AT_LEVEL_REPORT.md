# M4-M1c — r-at-level at the measured budget

**Leg:** M4-M1c · **Registered** 2026-08-11 in
`docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md` (section "M4-M1c — r-at-level at the
measured budget"), commit `dd1a38f`, BEFORE this run.
**Executor:** dispatched agent (implementation and execution only; the
registration text is binding).
**Harness:** `scripts/run_suica_m4_m1c_r_at_level.py`.
**Artifacts:** `results/m4_m1c_r_at_level/` (gitignored).
**Banner:** synthetic worlds on K2b's frozen instrument, exploratory,
label-free; the M1b design at the budget M1b's own diagnostic measured.

**Verdict: `LEVEL_RESPONSE_DISSOCIATION` (rule-16 cell 4), modifier `KAPPA_FOURTH_APPEARANCE`.**
L-1 **HOLD**, L-2 **below**, L-3 **overlap**. 3840 worlds
(20 cells × 192).

Three legs asked one question. M1 died on a proxy; M1b died on the estimand and
priced the answer at 192 worlds/cell; the planner funded it.
**The exponent is now identified at level, and it is not the response
exponent.** The winning form's `q = -0.15040108849226472`, 95% interval `[-0.18322395953281184, -0.11871900002844447]`, width
`0.06450495950436737` against L-1's `0.6` bar — an interval **entirely below** the
response band `[1.71, 1.98]`, and entirely below zero. The variance tax
lands at `κ = 0.7601952008701406`, `[0.7356727662590873, 0.7846243216827854]` — inside K2f's
`[0.5202855978239498, 0.8612166024267973]`, **κ's fourth independent appearance**.

The sign is the finding. At **exactly fixed** `V = 0.18000000000000005` (share
0.6), pushing φ from [0.05, 0.3, 0.6, 0.85, 0.98]'s low end to its high end drops
predicted attenuation `r` from `0.6573448847694047` to `0.4541409476972356` —
and the measured b-only field recovery **rises** from `0.05410832013119198`
to `0.063796931786496`, a gain of 4.03363828257993 pooled SEM. Less
predicted card attenuation, more field recovery, person-variance held exactly
constant. At response grade q sits in `[1.71, 1.98]`; at level `q = -0.15040108849226472`. That is the
dissociation, measured rather than inferred.

---

## Part 0 — written before any world

### 0.1 Rule 9 / rule 12 — conventions pinned in writing

| note | pinned reading |
|---|---|
| RN-M1C-1 | machinery COPIED into this file, then PROVEN faithful in Part 0 against BOTH the M1 and M1b harnesses (start grid, OPT, form expressions/names, inherited bars, and fit_form bit-exact on a fixed synthetic probe) |
| RN-M1C-2 | seed string pinned: v8.stable_bucket(f'{MASTER_SEED}-{share!r}-{phi!r}-{world}', salt='m4m1c-world', modulus=2**31-1), indices 0..191; index 0 is the SMOKE world and is RETAINED, so chunks cover 1..191 and the union is exactly 0..191 |
| RN-M1C-3 | smoke.json records BOOLEANS ONLY -- no mean/min/max/sd/level anywhere; the retained per-world CSV holds the levels but nothing reads or aggregates them before the `fit` stage |
| RN-M1C-4 | chunk k takes Part-0 design indices [4k, 4k+4) (share-major, phi ascending); chunks are RESUMABLE (a complete cell artifact is skipped); seeds depend only on (share, phi, index), never on chunk membership |
| RN-M1C-5 | bootstrap draws are generated in batches from ONE master-seeded rng in draw order -- identical stream to the unbatched form; memory management only |
| RN-M1C-6 | L-4 as registered (both monotonicity readings) PLUS appendix W's discriminator: OLS of the winner's cell residuals on [1, r, r^2] with share fixed effects (primary) and without (secondary); 'fires' = the r^2 coefficient's 95% world-block bootstrap CI excludes 0. A reading; adjudicates nothing |
| RN-M1C-7 | the >=10xB rule-13 re-run is its own foreground stage `rule13` |

### 0.2 RN-M1C-1 — the copied machinery, proven against BOTH predecessors

| witness | forms bit-exact | start grids | optimizer | inherited bars | PASS |
|---|---|---|---|---|---|
| M1 | True | True | True | True | True |
| M1b | True | True | True | True | True |

### 0.3 G0m″ — anchors bit-exact, nine clauses

Every anchor, every K2f number, the D-open level, the theory band, the planner's
design table, the M1-STOP numbers, and **every M1b number the planner's
adjudication cites** re-derive bit-exactly from the persisted artifacts.

| clause | registration / adjudication | re-derived / persisted | bit-exact |
|---|---|---|---|
| (i) predicted_attenuation(0.40, 0.90) | 0.6185853753498524 | 0.6185853753498524 | True |
| (ii-a) predicted_attenuation(0.45, 0.90) | 0.5889058864943755 | 0.5889058864943755 | True |
| (ii-b) person_share_design(0.45, 0.0) | 0.13500000000000004 | 0.13500000000000004 | True |
| (iii) person_share_design(0.40, 0.0) | 0.12000000000000004 | 0.12000000000000004 | True |
| F2 LOO-RMSE (fits.json) | 0.0061559195350209 | 0.0061559195350209 | True |
| F2 LOO-RMSE (loo.json) | 0.0061559195350209 | 0.0061559195350209 | True |
| F2 kappa' | 0.750086268225045 | 0.750086268225045 | True |
| F2 kappa' ci95 hi | 0.8612166024267973 | 0.8612166024267973 | True |
| F2 kappa' ci95 lo | 0.5202855978239498 | 0.5202855978239498 | True |
| F2 lambda' | 0.18021628978547316 | 0.18021628978547316 | True |
| F2 p | 0.2064406330042716 | 0.2064406330042716 | True |
| F2 q' | -0.009622064624441264 | -0.009622064624441264 | True |
| F2 q' ci95 hi | 0.5313115708778163 | 0.5313115708778163 | True |
| F2 q' ci95 lo | -0.3792124136721057 | -0.3792124136721057 | True |
| corr(r, V) over the 26 K2f rows | -0.9643543785903034 | -0.9643543785903034 | True |
| r(0.30, 0.90) | 0.6758917867864564 | 0.6758917867864564 | True |
| r(0.30, 0.98) | 0.645057248597175 | 0.645057248597175 | True |
| r(0.50, 0.90) | 0.558364277337817 | 0.558364277337817 | True |
| r(0.50, 0.98) | 0.5193517935368367 | 0.5193517935368367 | True |
| share envelope hi | 0.6634207990183637 | 0.6634207990183637 | True |
| share envelope lo | 0.02 | 0.02 | True |
| (v) Dopen:M-4 level from the raw CSV | 0.09350089316336324 | 0.09350089316336324 | True |
| (vi) `[1.71, 1.98]` verbatim in `docs/SUICA_IDENTITY_THEORY_V1.md` | [1.71, 1.98] | lines [805, 841] | True |
| (vii) MAIN corr(r, V) | -0.8495063312353189 | -0.8495063312353189 | True |
| (vii) MAIN corr(r^q, V) | -0.8649603255864755 | -0.8649603255864755 | True |
| (viii) M1 freed-shares bound | 0.5208187741410987 | 0.5208187741410987 | True |
| (viii) M1 full-interval r span at share 0.1 | 0.05159009087311539 | 0.05159009087311539 | True |
| (viii) M1 full-interval r span at share 0.25 | 0.11784317303319514 | 0.11784317303319514 | True |
| (viii) M1 full-interval r span at share 0.4 | 0.17083747134975158 | 0.17083747134975158 | True |
| (viii) M1 full-interval r span at share 0.6 | 0.21722718146551878 | 0.21722718146551878 | True |
| (viii) M1 infimum \|corr(r,V)\| | 0.748768093111513 | 0.748768093111513 | True |
| (ix) M1b cell-mean sd at n=32 | 0.004753426045853251 | 0.004753426045853251 | True |
| (ix) M1b ladder confirmation n=192 q_truth 1.0 | 0.2531601642892628 | 0.2531601642892628 | True |
| (ix) M1b ladder width n=192 q_truth 1.8528700746510731 | 0.45033528452170346 | 0.45033528452170346 | True |
| (ix) M1b pilot card SE multiple | 94.8954999654606 | 94.8954999654606 | True |
| (ix) M1b pilot card contrast | 0.20325550047558588 | 0.20325550047558588 | True |
| (ix) M1b pilot field SE multiple | 0.7542598230697173 | 0.7542598230697173 | True |
| (ix) M1b pilot field contrast | -0.007269536568279722 | -0.007269536568279722 | True |
| (ix) M1b q-width n=32 q_truth 1.0 | 0.6446327208199195 | 0.6446327208199195 | True |
| (ix) M1b q-width n=32 q_truth 1.8528700746510731 | 1.1702741415331803 | 1.1702741415331803 | True |
| (ix) M1b q-width n=64 q_truth 1.0 | 0.45036131116284384 | 0.45036131116284384 | True |
| (ix) M1b q-width n=64 q_truth 1.8528700746510731 | 0.8082914682805795 | 0.8082914682805795 | True |
| (ix) M1b sigma_w (df-inflated) | 0.026889438327132725 | 0.026889438327132725 | True |

| share | V_person | r(phi=0.05) | r(phi=0.3) | r(phi=0.6) | r(phi=0.85) | r(phi=0.98) | span | bit-exact |
|---|---|---|---|---|---|---|---|---|
| 0.1 | 0.03000000000000001 | 0.8189581462487876 | 0.8155586799827954 | 0.8075174172340943 | 0.7908869485651705 | 0.7718092954224756 | 0.04714885082631204 | True |
| 0.25 | 0.07500000000000002 | 0.785015540293945 | 0.7761302864207245 | 0.7558507450373838 | 0.7168731389294273 | 0.6763691758553391 | 0.10864636443860598 | True |
| 0.4 | 0.12000000000000004 | 0.7411873080384952 | 0.726425348215848 | 0.6941115392115328 | 0.6367206581308248 | 0.5825497814736654 | 0.15863752656482977 | True |
| 0.6 | 0.18000000000000005 | 0.6573448847694047 | 0.6346912945232521 | 0.5883719155687073 | 0.5151304058057474 | 0.4541409476972356 | 0.20320393707216905 | True |

### 0.4 G1m″ — the design gates

| gate | bar | realized | PASS |
|---|---|---|---|
| (a) shares inside the trained envelope | [0.02, 0.6634207990183637] | [0.1, 0.25, 0.4, 0.6] | True |
| (b) V max/min | >= 2.0 | 6.0 | True |
| (c') within-share r SPAN at shares [0.4, 0.6] | >= 0.12 | [0.15863752656482977, 0.20320393707216905] | True |
| (e) duplicate (r, V) design points | 0 | 0 | True |
| *(no marginal-correlation gate -- rule 25)* | n/a | corr(r, V) = -0.8495063312353189, REPORTED only | n/a |

Marginal `corr(r, V) = -0.8495063312353189` (`corr(r^q, V) = -0.8649603255864755`) is
REPORTED and gates nothing — rule 25, whose exemplar this design is.

### 0.5 G2m″ — no new pilot

M1b's persisted pilot IS this leg's regime, liveness and noise source: same
instrument, same corners, same 16 worlds. `σ_w = 0.026889438327132725` is read from
`results/m4_m1b_r_at_level/g3mb_power.json` and verified bit-exactly, along with
M1b's regime and liveness pass records.

### 0.6 G3m″ — the feasibility gate, CONFIRMED before any world

| quantity | value |
|---|---|
| sigma_w (from M1b's persisted pilot) | 0.026889438327132725 |
| source | results/m4_m1b_r_at_level/g3mb_power.json |
| confirmation n=192: B_proj | 2000 |
| confirmation n=192: cell-mean sd | 0.00194057805706599 |
| confirmation n=192: q width at q_truth = 1.0 | 0.24923889216646022  PASS |
| confirmation n=192: q width at q_truth = 1.8528700746510731 | 0.46602037304504784  PASS |
| confirmation n=192: PASS (both truths <= 0.5) | True |
| rule-13 re-decide | not run |
| escalated n=256 | not run |
| boundary rule fired | False |
| escalation fired | False |
| M1b's B_proj=500 ladder at n=192, for comparison | 0.45033528452170346 / 0.2531601642892628 |
| **worlds/cell decided** | **192** |

At n = 192 with B_proj = 2000 the projected 95% widths of
`q̂` are 1.0: 0.24923889216646022, 1.8528700746510731: 0.46602037304504784, both under the `0.5` bar. Boundary rule fired:
**False**; escalation fired: **False**. M1b's B_proj = 500
ladder had put the same configuration at [0.45033528452170346, 0.2531601642892628]; the honest re-run at
four times the draws agrees to within its own Monte-Carlo error. Worth stating
plainly: the binding width sits close to — but below — the `[0.47, 0.53]`
re-decide band, so the confirmation is comfortable against the bar without being
far from the band that would have demanded 10000 draws.

---

## The smoke stage

World index 0 of every cell, **booleans only** — no aggregation, no level read
(RN-M1C-3). These 20 worlds are retained in the main sample, so the chunks cover
indices 1..192 minus one and the union is exactly the registered
0..191.

| cell | world | all finite | strictly inside (0,1) | PASS |
|---|---|---|---|---|
| s0.10_p0.05 | 0 | True | True | True |
| s0.10_p0.30 | 0 | True | True | True |
| s0.10_p0.60 | 0 | True | True | True |
| s0.10_p0.85 | 0 | True | True | True |
| s0.10_p0.98 | 0 | True | True | True |
| s0.25_p0.05 | 0 | True | True | True |
| s0.25_p0.30 | 0 | True | True | True |
| s0.25_p0.60 | 0 | True | True | True |
| s0.25_p0.85 | 0 | True | True | True |
| s0.25_p0.98 | 0 | True | True | True |
| s0.40_p0.05 | 0 | True | True | True |
| s0.40_p0.30 | 0 | True | True | True |
| s0.40_p0.60 | 0 | True | True | True |
| s0.40_p0.85 | 0 | True | True | True |
| s0.40_p0.98 | 0 | True | True | True |
| s0.60_p0.05 | 0 | True | True | True |
| s0.60_p0.30 | 0 | True | True | True |
| s0.60_p0.60 | 0 | True | True | True |
| s0.60_p0.85 | 0 | True | True | True |
| s0.60_p0.98 | 0 | True | True | True |

---

## The grid

| cell | share | phi | r_pred | V_person | mean field | SEM | sd | n |
|---|---|---|---|---|---|---|---|---|
| s0.10_p0.05 | 0.1 | 0.05 | 0.8189581462487876 | 0.03000000000000001 | 0.1585891652101896 | 0.0018743992250782693 | 0.02597243753202635 | 192 |
| s0.10_p0.30 | 0.1 | 0.3 | 0.8155586799827954 | 0.03000000000000001 | 0.16035538669822857 | 0.0020066026535869932 | 0.02780430197292163 | 192 |
| s0.10_p0.60 | 0.1 | 0.6 | 0.8075174172340943 | 0.03000000000000001 | 0.16156034289722412 | 0.0019744651453781504 | 0.027358991596550607 | 192 |
| s0.10_p0.85 | 0.1 | 0.85 | 0.7908869485651705 | 0.03000000000000001 | 0.16512469544098618 | 0.001983741777975856 | 0.027487532388409612 | 192 |
| s0.10_p0.98 | 0.1 | 0.98 | 0.7718092954224756 | 0.03000000000000001 | 0.15987119532439534 | 0.0018913572625018093 | 0.026207414991340158 | 192 |
| s0.25_p0.05 | 0.25 | 0.05 | 0.785015540293945 | 0.07500000000000002 | 0.12162744485545209 | 0.0017778785791358425 | 0.02463500823001315 | 192 |
| s0.25_p0.30 | 0.25 | 0.3 | 0.7761302864207245 | 0.07500000000000002 | 0.12295515685269942 | 0.001799144985921348 | 0.024929684206388535 | 192 |
| s0.25_p0.60 | 0.25 | 0.6 | 0.7558507450373838 | 0.07500000000000002 | 0.12714790436588774 | 0.0017053615065044834 | 0.02363018219630374 | 192 |
| s0.25_p0.85 | 0.25 | 0.85 | 0.7168731389294273 | 0.07500000000000002 | 0.13204663807737851 | 0.0018782693723257374 | 0.026026063865349454 | 192 |
| s0.25_p0.98 | 0.25 | 0.98 | 0.6763691758553391 | 0.07500000000000002 | 0.13201888792665142 | 0.0018133362157806163 | 0.025126323655493665 | 192 |
| s0.40_p0.05 | 0.4 | 0.05 | 0.7411873080384952 | 0.12000000000000004 | 0.09025343262511598 | 0.0017452922267459832 | 0.024183478486232514 | 192 |
| s0.40_p0.30 | 0.4 | 0.3 | 0.726425348215848 | 0.12000000000000004 | 0.09132685344495504 | 0.0016796177194939308 | 0.02327346581965167 | 192 |
| s0.40_p0.60 | 0.4 | 0.6 | 0.6941115392115328 | 0.12000000000000004 | 0.0980498887620882 | 0.0015916871722070262 | 0.022055064416145617 | 192 |
| s0.40_p0.85 | 0.4 | 0.85 | 0.6367206581308248 | 0.12000000000000004 | 0.0992713149259878 | 0.0017741240206580028 | 0.024582983541664296 | 192 |
| s0.40_p0.98 | 0.4 | 0.98 | 0.5825497814736654 | 0.12000000000000004 | 0.10169041646048367 | 0.0017444660987341613 | 0.024172031320712262 | 192 |
| s0.60_p0.05 | 0.6 | 0.05 | 0.6573448847694047 | 0.18000000000000005 | 0.05410832013119198 | 0.001773830076330116 | 0.024578910529580323 | 192 |
| s0.60_p0.30 | 0.6 | 0.3 | 0.6346912945232521 | 0.18000000000000005 | 0.057429784543359674 | 0.0015865768513429728 | 0.02198425373310946 | 192 |
| s0.60_p0.60 | 0.6 | 0.6 | 0.5883719155687073 | 0.18000000000000005 | 0.06031911254293101 | 0.0016085232676605703 | 0.02228835219795856 | 192 |
| s0.60_p0.85 | 0.6 | 0.85 | 0.5151304058057474 | 0.18000000000000005 | 0.061787884770662806 | 0.0015046764572937737 | 0.020849408583884465 | 192 |
| s0.60_p0.98 | 0.6 | 0.98 | 0.4541409476972356 | 0.18000000000000005 | 0.063796931786496 | 0.0016195393028748909 | 0.02244099485947193 | 192 |

Per-cell SEM ranges from `0.0015046764572937737` to `0.0020066026535869932`; cell mean field from
`0.05410832013119198` to `0.16512469544098618` (range `0.11101637530979419`).

---

## The fits

| form | expression | lambda | lambda ci95 | q | q ci95 | q width | kappa | kappa ci95 | 4th param | in-sample RMSE | LOO-RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F1 | `field = lambda*r^q - kappa*V` | 0.17505204234174737 | [0.17322592761078637, 0.17688885617490216] | -0.1888182542137735 | [-0.22686946646111852, -0.14900957557344477] | 0.07785989088767375 | 0.7596295789070726 | [0.735240940068321, 0.7838667424719438] | -- | 0.0026264051166751978 | 0.003198131708377386 |
| **F1e (winner)** | `field = lambda*r^q - kappa*V - epsilon, epsilon in [0, 0.05]` | 0.2249206339499495 | [0.2226976852269149, 0.2267740781729326] | -0.15040108849226472 | [-0.18322395953281184, -0.11871900002844447] | 0.06450495950436737 | 0.7601952008701406 | [0.7356727662590873, 0.7846243216827854] | epsilon = 0.049999999999999996 ci95 [0.049999999999909624, 0.049999999999999996] | 0.002621078709438027 | 0.0031856515917748638 |
| F2 | `field = lambda*r^q - kappa*V*r^p` | 0.17810271708703745 | [0.1719071338546651, 0.18474536451408446] | -0.12421609491451265 | [-0.2544030218404508, 0.011573105680058435] | 0.26597612752050925 | 0.7831856742623807 | [0.7324014642909888, 0.8433277666605047] | p = 0.10816742886000663 ci95 [-0.09622170477518216, 0.3288578132562438] | 0.002591249722764473 | 0.0034019365713125944 |
| F3 | `field = (lambda - kappa*V)*r^q` | 0.1675744937183866 | [0.16396480039778022, 0.17139093637680697] | -0.3141204190367959 | [-0.40469459727192797, -0.21832280189980452] | 0.18637179537212345 | 0.6658456569673928 | [0.6525777952905363, 0.6791081161546143] | -- | 0.0033903747201612703 | 0.003877604046883495 |

| form | B | draws used | discarded | n starts | converged | at global SSE | distinct optima | R^2 vs mean |
|---|---|---|---|---|---|---|---|---|
| F1 | 2000 | 2000 | 0 | 54 | 54 | 54 | 1 | 0.9951610947688201 |
| F1e | 2000 | 2000 | 0 | 162 | 162 | 162 | 1 | 0.9951807016791032 |
| F2 | 2000 | 2000 | 0 | 162 | 162 | 162 | 1 | 0.9952897688274347 |
| F3 | 2000 | 2000 | 0 | 54 | 54 | 54 | 1 | 0.9919365836062832 |

**All four forms agree on the qualitative picture** — `q` negative and small in
magnitude, `κ` near 0.76, `λ` near 0.18–0.22 — which is why the verdicts are
robust to the form tie described next.

### The winner sits on a declared bound, and this is disclosed

`F1e` wins by LOO, and its `ε` is **pinned at its registered upper bound**:
point estimate `0.049999999999999996` against the bound `0.05` (gap
`6.938893903907228e-18`), with a bootstrap interval `[0.049999999999909624, 0.049999999999999996]` whose *lower*
endpoint is `9.037909309839165e-14` from the bound — i.e. essentially every draw sat
on the constraint. `F1e` therefore contributes no effective free fourth
parameter here; it is `F1` with a fixed −0.05 offset and a λ
re-scaled to compensate (`0.2249206339499495` against `F1`'s `0.17505204234174737`).

Two things keep this from mattering to the verdict, and both were pre-declared.
First, the **tie rule fired**: `F1e` beats `F1` by `1.2480116602522386e-05` =
0.003917602488214719 of the winner's LOO, well inside the 5% band, so every verdict
had to agree across both forms — and every verdict does. Second, `F1` is
**unbounded** and gives the same three verdicts from `q = -0.1888182542137735`,
`[-0.22686946646111852, -0.14900957557344477]`, `κ = 0.7596295789070726`, `λ = 0.17505204234174737`. The negative-`q`,
`κ ≈ 0.76` picture is not an artifact of a clipped parameter.

---

## Verdicts

| lean | clause | sided | prior | measured | verdict |
|---|---|---|---|---|---|
| L-1 | winner's q 95% CI width <= 0.6 | one-sided (DOWN) | 0.55 | width 0.06450495950436737 on [-0.18322395953281184, -0.11871900002844447] | **HOLD** |
| L-2 | winner's q CI vs [1.71, 1.98] | two-sided (below / overlap / above) | below .55 / overlap .35 / above .10 | [-0.18322395953281184, -0.11871900002844447] | **below** |
| L-3 | winner's kappa CI overlaps [0.5202855978239498, 0.8612166024267973] | two-sided overlap | 0.70 | [0.7356727662590873, 0.7846243216827854] | **overlap** |
| (routing input) | winner's lambda CI contains 0 | two-sided | -- | [0.2226976852269149, 0.2267740781729326] | False |
| L-4 | Spearman(residual, phi) within shares + appendix W's quadratic | reading, NO gate | -- | A 2/4, B 0/4 | reading only |

**L-1 HOLDS with room to spare:** the q interval is `0.06450495950436737` wide against a
`0.6` bar. The budget bought what the projection said it would buy.

**L-2 is BELOW, and the registered lean called it.** The lean was BELOW at prior
.55; the interval `[-0.18322395953281184, -0.11871900002844447]` does not merely fall below `[1.71, 1.98]`, it
falls below zero. This is cell 4's `LEVEL_RESPONSE_DISSOCIATION`.

**L-3 OVERLAPS**, so the modifier is `KAPPA_FOURTH_APPEARANCE`: modifier: kappa's fourth independent appearance is counted. κ has now
appeared at ≈0.72–0.76 in four independent fitting routes, and this leg's
interval `[0.7356727662590873, 0.7846243216827854]` is the tightest of them and sits inside K2f's.

### Rule 13 and the tie rule

| quantity | value | bar | scale | within 5% |
|---|---|---|---|---|
| F1e: q CI width vs L-1 bar | 0.06450495950436737 | 0.6 | 0.6 | False |
| F1e: q_lo vs response band 1.71 | -0.18322395953281184 | 1.71 | 1.71 | False |
| F1e: q_lo vs response band 1.98 | -0.18322395953281184 | 1.98 | 1.98 | False |
| F1e: q_hi vs response band 1.71 | -0.11871900002844447 | 1.71 | 1.71 | False |
| F1e: q_hi vs response band 1.98 | -0.11871900002844447 | 1.98 | 1.98 | False |
| F1e: kappa_hi vs K2f ci95 lo | 0.7846243216827854 | 0.5202855978239498 | 0.5202855978239498 | False |
| F1e: kappa_lo vs K2f ci95 hi | 0.7356727662590873 | 0.8612166024267973 | 0.8612166024267973 | False |
| F1e: lambda CI nearest endpoint vs 0 | 0.2226976852269149 | 0.0 | 0.2249206339499495 | False |
| F1: q CI width vs L-1 bar | 0.07785989088767375 | 0.6 | 0.6 | False |
| F1: q_lo vs response band 1.71 | -0.22686946646111852 | 1.71 | 1.71 | False |
| F1: q_lo vs response band 1.98 | -0.22686946646111852 | 1.98 | 1.98 | False |
| F1: q_hi vs response band 1.71 | -0.14900957557344477 | 1.71 | 1.71 | False |
| F1: q_hi vs response band 1.98 | -0.14900957557344477 | 1.98 | 1.98 | False |
| F1: kappa_hi vs K2f ci95 lo | 0.7838667424719438 | 0.5202855978239498 | 0.5202855978239498 | False |
| F1: kappa_lo vs K2f ci95 hi | 0.735240940068321 | 0.8612166024267973 | 0.8612166024267973 | False |
| F1: lambda CI nearest endpoint vs 0 | 0.17322592761078637 | 0.0 | 0.17505204234174737 | False |
| LOO separation winner vs runner-up | 1.2480116602522386e-05 | 0.0 | 0.0031856515917748638 | True |

| form | verdict | B=2000 | B=20000 | unchanged | max endpoint shift |
|---|---|---|---|---|---|
| F1e | L-1 | HOLD | HOLD | True | 0.0009586407472494674 |
| F1e | L-2 | below | below | True | 0.0009586407472494674 |
| F1e | L-3 | overlap | overlap | True | 0.0009586407472494674 |
| F1e | lambda_ci_contains_zero | False | False | True | 0.0009586407472494674 |
| F1 | L-1 | HOLD | HOLD | True | 0.0006440703575815165 |
| F1 | L-2 | below | below | True | 0.0006440703575815165 |
| F1 | L-3 | overlap | overlap | True | 0.0006440703575815165 |
| F1 | lambda_ci_contains_zero | False | False | True | 0.0006440703575815165 |

Rule 13 fired (**True**) on the near-tie and the re-run at
B = 20000 left every verdict unchanged (**all stable: True**).

---

## L-4 — the reading, and appendix W's discriminator

| share | Spearman(residual, phi) | sign | perfectly monotone | mean resid at r-extremes | mean resid mid-r | U-shape sign (ends - mid) | residuals in phi order |
|---|---|---|---|---|---|---|---|
| 0.1 | 0.0 | 0 | False | -0.0007815016105517381 | 0.0027549238990342193 | -0.0035364255095859574 | -0.0003843778458274827, 0.0012367950125088678, 0.0020958595581342387, 0.004932117126459551, -0.0011786253752759934 |
| 0.25 | 0.8999999999999998 | 1 | False | -0.002064415035092561 | -0.0005082313540028435 | -0.0015561836810897172 | -0.004617621082872933, -0.003689599353178863, -0.0004291596503367967, 0.0025940649415071293, 0.0004887910126878114 |
| 0.4 | 0.6 | 1 | False | -0.002427977783141237 | -0.0006726757172726416 | -0.0017553020658685956 | -0.0038070773585779927, -0.003446637047581705, 0.00165576479879731, -0.00022715490303353014, -0.0010488782077044817 |
| 0.6 | -0.6 | -1 | False | -0.0006337974339542737 | 0.002362974586882336 | -0.0029967720208366098 | 0.0013729300877863837, 0.0034274222569794024, 0.003556147525710013, 0.00010535397795759238, -0.002640524955694931 |

**L-4 itself is QUIET.** Per-share Spearman(residual, φ) = [0.0, 0.8999999999999998, 0.6, -0.6];
sign-agreement reading A reaches 2/4 against a 3/4 bar
(False), and the stricter reading B reaches 0/4
(False). There is no φ-leak signature.

| reading | r^2 coefficient | 95% world-block bootstrap CI | fires? |
|---|---|---|---|
| with share fixed effects (PRIMARY -- appendix W's 'within share strata') | -0.19911194958208703 | [-0.2879978718649799, -0.10706476050455438] | True |
| pooled, no fixed effects (secondary) | -0.04921007645583713 | [-0.10592459329331352, 0.007421060164540356] | False |
| **appendix W reading** | FORM_GAP (quadratic-in-r fires, L-4 Spearman quiet) -- appendix W.1's span-gap signature | -- | -- |

**The quadratic-in-r discriminator FIRES.** Appendix W.1, written before any M1
world existed, states the rule: "an L-4 monotone fire is φ-leak evidence; a
quadratic fire with quiet Spearman is FORM-GAP evidence, and the follow-up is a
registered form extension … not a φ-channel claim." That is exactly the
configuration observed — quiet Spearman, r² coefficient `-0.19911194958208703` with
interval `[-0.2879978718649799, -0.10706476050455438]` excluding zero on the within-share (fixed-effects)
reading, the pooled reading `-0.04921007645583713` `[-0.10592459329331352, 0.007421060164540356]` not firing.
Verdict of the discriminator: **FORM_GAP (quadratic-in-r fires, L-4 Spearman quiet) -- appendix W.1's span-gap signature**.

**One honest correction to appendix W, stated because the sign matters.** W.1
predicted the span gap would show as a *U*-shape — "residuals positive at both
r-extremes, negative mid-range" — which is a POSITIVE r² coefficient. The
measured coefficient is **negative**: the residuals are low at both r-extremes
and high in the middle, an inverted-U. So the discriminator fires *in kind*
exactly as W.1 specified, and the follow-up it prescribes (a registered form
extension, not a φ-channel claim) stands — but the missing shape is on the
opposite side of the family's span from the "positive floor plus positive power"
W.1 hypothesised. The ε-at-bound finding above points the same way and is
independent of it: the fit wants a *more negative* constant than the box allows,
not a positive floor. Two separate signals, one conclusion — the registered
four-form family does not span this truth.

None of this touches the outcome slug: L-4 and the discriminator are readings,
and cell 4 is decided by L-1, L-2 and λ's interval alone.

---

## Routing — the inherited truth table, reproduced verbatim

| # | condition | outcome |
|---|---|---|
| 1 | any G0m''/G1m''/G3m''/smoke clause fails after its declared ladder | STOP (no fit is run) -- NON_PROJECTABLE_AT_CEILING where G3m'' fails after the once-only escalation to 256; SMOKE_REGIME_BREAK where the smoke fails (no ALT ladder is available: it would need a fresh projection) |
| 2 | L-1 MISS AND winner lambda CI contains 0 | R_TERM_ABSENT_AT_LEVEL -- the tax-only level law is the COMPLETE level story on this family; level-response dissociation named; q-at-level closes as structurally unposed; M2 proceeds on the tax-only form |
| 3 | L-1 MISS AND winner lambda CI excludes 0 | NON_IDENTIFIED_UNDERPOWERED -- CI reported, no q claim; M2 blocked; leverage redesign named |
| 4 | L-1 HOLD AND L-2 below | **LEVEL_RESPONSE_DISSOCIATION -- q measured at level, below the response band; new named phenomenon; M2 seals the measured law**  <-- THIS LEG |
| 5 | L-1 HOLD AND L-2 overlap | SINGLE_EXPONENT_RESTORED -- T4's level form completed with the response exponent; M2 seals |
| 6 | L-1 HOLD AND L-2 above | ABOVE_BAND_ANOMALY -- named; M2 seals the measured law; theory note required |
| -- | L-3 disjoint (either side), any cell 2-6 | modifier TAX_SHIFT_AT_LEVEL -- pre-registered anomaly fed into M3's charter |
| -- | L-3 overlap, any cell 2-6 | **modifier: kappa's fourth independent appearance is counted**  <-- THIS LEG |

## Gates

| gate | PASS | detail |
|---|---|---|
| G0m'' | True | (i)-(vi) M1's anchors; (vii) planner design table; (viii) the M1-STOP numbers; (ix) EVERY M1b number the adjudication cites -- all bit-exact |
| G1m'' | True | (a)(b)(c')(e) pass; no marginal gate (rule 25) |
| G2m'' | True | no new pilot -- M1b's persisted pilot is the pinned regime, liveness and noise source, verified bit-exactly |
| G3m'' | True | projection CONFIRMED before any world at n=192, B_proj=2000 |
| smoke | True | world 0 of all 20 cells finite and non-saturated; booleans only; worlds retained |
| G4m'' | True | inherited truth table reproduced verbatim; every report table generated from artifacts |

## Sides declared in Part 0 (rule 22)

| clause | statement | sided | improvement side |
|---|---|---|---|
| L-1 | winner's q 95% bootstrap CI width <= 0.6 | one-sided | DOWN (smaller width is better) |
| L-2 | winner's q CI against the response band [1.71, 1.98]: entirely below / overlap / entirely above | two-sided | neither -- all three outcomes are informative and named |
| L-3 | winner's kappa CI overlaps K2f F2's kappa' ci95 [0.5202855978239498, 0.8612166024267973] | two-sided overlap; disjoint-low and disjoint-high both named | neither -- containment/overlap |
| L-4 | within each share level, Spearman(residual, phi) across the 5 phi cells; monotone same-sign in >=3/4 share levels is the named finding 'phi leaks past (r, V)'. Appendix W's quadratic-in-r discriminator is reported beside it (RN-M1C-6) | reading only, NO gate | n/a |
| G1m''(a) | all shares inside [0.02, 0.6634207990183637] | two-sided containment | neither |
| G1m''(b) | V max/min >= 2.0 | one-sided | UP |
| G1m''(c') | within-share r SPAN >= 0.12 at BOTH shares [0.4, 0.6] | one-sided | UP |
| G1m''(e) | no duplicate (r, V) design points | exact | n/a |
| smoke | world index 0 of every cell finite and strictly inside (0, 1) -- booleans only, no aggregation | two-sided containment | neither -- failure is a STOP with no ALT ladder |
| G3m'' | projected q width proxy <= 0.5 under BOTH q truths at n=192, B_proj=2000, recomputed from M1b's persisted sigma_w -- THE feasibility gate (rule 25) | one-sided | DOWN |
| descriptive (NOT a gate, rule 25) | marginal corr(r, V) and corr(r^q, V) across cells | reported only | n/a |

| form | expression | params | starts | bounded |
|---|---|---|---|---|
| F1 | field = lambda*r^q - kappa*V | ['lambda', 'q', 'kappa'] | 54 | False |
| F1e | field = lambda*r^q - kappa*V - epsilon, epsilon in [0, 0.05] | ['lambda', 'q', 'kappa', 'epsilon'] | 162 | True |
| F2 | field = lambda*r^q - kappa*V*r^p | ['lambda', 'q', 'kappa', 'p'] | 162 | False |
| F3 | field = (lambda - kappa*V)*r^q | ['lambda', 'q', 'kappa'] | 54 | False |

---

## Anomaly log — every anomaly, with pre/post-hypothesis timing

The hypothesis-relevant boundary in this leg is the `fit` stage: Part 0, the
smoke booleans and the world CSVs all precede any level being read or
aggregated. Every RN note was pinned in Part 0, before the first world.

- **A-1 — the interpreter (before Part 0, before any number).** The environment
  pinned in M4-M1 and reused in M1b is reused again verbatim: a CPython
  3.12.12 virtual environment outside the repository, populated from
  `requirements-lock-main.txt` (numpy `2.4.4`, pandas `3.0.2`, scipy
  `1.17.1`), platform `macOS-26.4.1-arm64-arm-64bit`. The machine's only pandas still belongs
  to CPython 3.9.6, which cannot import the published machinery.
- **A-2 — `timeout(1)` absent on this platform (before Part 0).** Every stage
  ran as its own foreground command under an explicit harness-level timeout.
- **A-3 — the projection landed near the re-decide band (Part 0, before any
  world).** The binding width sits just below `[0.47, 0.53]`, so the rule-13
  10000-draw re-decide did not fire. Disclosed because a slightly noisier draw
  would have triggered it; the decision was made by the registered rule, not by
  preference.
- **A-4 — the form tie (at the fit, the first hypothesis-relevant moment).**
  `F1e` over `F1` by 0.003917602488214719 of the winner's LOO. The pre-declared tie
  rule fired and required agreement across both forms; agreement was obtained on
  all three leans, so no verdict reports SPLIT.
- **A-5 — the winner's ε is pinned at its declared upper bound (at the fit).**
  Reported in full above rather than smoothed. It does not move the verdict —
  the unbounded runner-up gives the same three — but it is real evidence about
  the form family and is carried forward as such.
- **A-6 — appendix W's discriminator fires with the opposite sign to W.1's
  prediction (at finalize).** Reported above with both readings and the
  correction stated plainly. The discriminator's *rule* is unaffected; its
  hypothesised *shape* is.
- **A-7 — no stage approached its 2× stop-and-report threshold.** Every world
  chunk landed inside its 480 s estimate and Part 0 inside its 240 s estimate.

| stage | registration estimate (s) | executor estimate (s) | measured (s) |
|---|---|---|---|
| part0 | 240 | 240 | 155.426 |
| smoke | 30 | 30 | 11.640 |
| worlds_1 | 480 | 480 | 435.876 |
| worlds_2 | 480 | 480 | 438.260 |
| worlds_3 | 480 | 480 | 434.700 |
| worlds_4 | 480 | 480 | 436.020 |
| worlds_5 | 480 | 480 | 436.085 |
| fit | 420 | 420 | 18.261 |
| rule13 | -- | 300 | 27.112 |
| finalize | 60 | 60 | 0.004 |

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

**The level law, as measured on this family and scoped to this grid:**

    field ≈ λ·r^q − κ·V_person − ε      λ ≈ 0.2249206339499495, q ≈ -0.15040108849226472, κ ≈ 0.7601952008701406

with `q` **negative** and its interval excluding both zero and the response
band. The tax coefficient is confirmed a fourth time. The exponent does not
transfer between grades: it is inside `[1.71, 1.98]` at response and `-0.15040108849226472` at level, and the
two are not merely different in magnitude but **opposite in sign**.

**What is now settled that was not.** K2f could not tell an intercept from
`λ·r^q` and reported `q′` straddling zero at `[-0.3792124136721057, 0.5313115708778163]`. M1c's interval is `[-0.18322395953281184, -0.11871900002844447]` — `0.06450495950436737` wide against K2f's
`0.910523984549922` — and excludes zero. The r-term at level is present, small, and negative.
λ's interval `[0.2226976852269149, 0.2267740781729326]` excludes zero, which is what keeps this in cell 4
rather than cell 2.

**What is not settled, and should not be claimed.** (i) The form family does not
span the truth: two independent signals say so (ε at its bound in essentially
every bootstrap draw; the quadratic-in-r residual firing at
`-0.19911194958208703`, `[-0.2879978718649799, -0.10706476050455438]`), so `q = -0.15040108849226472` is the best exponent *within a
family that is demonstrably too small*, not the exponent of the world. The
honest next step is appendix W's own prescription — a registered form
extension — before any exponent is sealed. (ii) The claim is scoped to the
tested grid: shares [0.1, 0.25, 0.4, 0.6], φ [0.05, 0.3, 0.6, 0.85, 0.98], this instrument, this carrier.
(iii) φ at {0.05, 0.30, 0.60, 0.85} remains a regime extension beyond the
exercised {0.90, 0.98}; the smoke and M1b's regime guard cover finiteness and
non-saturation, not physical realism.

**For M2.** The line charter says M2 seals the measured law at ≥3 extrapolated
configurations with bands from M1's LOO-RMSE. The winner's LOO-RMSE is
`0.0031856515917748638`, so a ±2×LOO band is ±`0.0063713031835497275`. Two cautions the
planner should weigh before registering it: sealing `F1e` seals a form whose
fourth parameter is a boundary artifact, and sealing any of the four seals a
family the residuals say is incomplete. Sealing `F1` — unbounded, 0.39176024882147187% behind,
same verdicts — may be the more honest object; that is a registration decision
and the executor takes no position beyond reporting that the two are
statistically indistinguishable here.

**Registration-defect candidates: one, non-blocking.** The registration selects
by LOO across four forms, one of which has a bounded parameter, and it does not
say what happens when a bounded form wins **with its bound active** — whether
the boundary parameter's CI is interpretable, whether the form should be demoted
to its effective dimension, or whether the boundary itself should be reported as
a finding (as it is here). Nothing turned on it this time, because the tie rule
independently forced agreement with the unbounded `F1`. It is flagged so a
successor registration can settle it in advance rather than in the report.
