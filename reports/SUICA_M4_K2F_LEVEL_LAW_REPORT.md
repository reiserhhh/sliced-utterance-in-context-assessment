# M4-K2f — The level law

**Leg:** M4-K2f · **Registered** 2026-08-10 in `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md`
(section "M4-K2f — The level law"), commit `598fb78`, BEFORE this run.
**Executor:** dispatched agent (implementation and execution only).
**Harness:** `scripts/run_suica_m4_k2f_level_law.py`.
**Artifacts:** `results/m4_k2f_level_law/` (gitignored).
**Banner:** synthetic worlds calibrated to an opened-panel regime, exploratory;
Stage 1 is artifact-space refitting on 26 persisted arms.

**Verdict: `LEVEL_LAW_RESTORED` (rule-16 cell 2 — L-1 HOLD, L-2 HOLD).**

D-open withdrew the T4 composite's use as an absolute LEVEL formula: the sealed
`field ≈ λ·r^q − κ·V_person` missed its new arm by 5.09 band widths while every
input re-derived bit-exactly. This leg asked whether there is a level law at
all. There is. Refit on 26 persisted arms, the best of three pre-declared forms
reaches a leave-one-out RMSE of `0.0061559195350209` against the sealed form's
`0.11259090547752257` — **18.29× better** — and its prediction for a fresh arm,
**hashed 14.586 s before the first fresh-arm world existed**, landed inside its
own band at 25.3% of the half-width.

The substantive finding is *where* the sealed law was wrong. The refit's
variance-tax coefficient κ′ ≈ 0.75 sits essentially on the sealed κ = 0.7220;
what collapses is the exponent, from a sealed `q = 1.8529` to a refitted
`q′ = −0.0096` whose 95% interval straddles zero in all three forms. **The tax
was right; the attenuation power law was the error.**

---

## Part 0 — written before any fit

Part 0 was persisted (`results/m4_k2f_level_law/part0.json`,
`part0_tables.md`) before a single parameter was estimated. Its contents: the
row rule, the compilation with per-row provenance, the anchors, the candidate
forms, the optimizer pins, the satisfiability check, the realizability floor,
the gate stages and the rule-16 enumeration.

### 0.1 Rule 9 — open conventions, pinned in writing BEFORE compiling

| pin | content | alternative reading, reported not adopted |
|---|---|---|
| **RN-K2F-1** (the row rule) | one row per persisted PRIMARY design arm; **both sides of every matched pair are separate rows**, because a pair's two arms are two distinct `(r, V)` design points and the object being fitted is a LEVEL law, not a difference law — the difference reading is exactly what D-open convicted. K2b contributes its six primary arms; **C1 is excluded** because K2b's own machinery excludes it (`scripts/run_suica_m4_k2b_t4_branch.py:94-105`, `PRIMARY_ARMS`; C1 is the "descriptive companion cell, no gate" with an equal-share `w_int` carrier). | a-side only → **17 rows**; pair MEANS as rows (K2d's `post_hoc_descriptive.json` `level` currency) → **17 rows**; RN-K2F-1 plus C1 → **27 rows** |
| **RN-K2F-2** (weighting) | unweighted nonlinear least squares — the registration says "nonlinear least squares on the compiled level rows" with no weights, and the rows are design points, not replicates | inverse-variance weights from each arm's per-world SEM (which would up-weight the 32-world arms over K2b's 8-world arms); computed and reported in §3.4, does not select the winner |
| **RN-K2F-3** (fresh-arm seeds) | K2f's OWN lineage, salt `m4k2f-world`, master_seed `20260826` — the registration names a master seed for this arm, and a genuinely fresh panel draw is the stricter test | reuse `k2b.world_seed_for` (the very panels every training row was measured on, as D-open's M-4 did); ALSO run, reported in §5.3, does not adjudicate L-2 |
| **RN-K2F-4** (ordering vs the pilot) | the registration's ordering clause is absolute, so the **rule-17 fresh-arm pilot runs AFTER the prediction stamp**. A pilot is a measurement of the fresh arm; publishing a prediction early costs nothing, reading the arm early costs the leg | running the pilot in Part 0 (D-open's order, where the protected object was a seal rather than a self-authored prediction) |
| **RN-K2F-5** (machinery note) | the published legs load their dependencies through private importlib loaders that do **not** consult `sys.modules`, so `k2e.k2d()` is a *different* k2d object owning a *different* k2b object. K2d's `int:` weight dispatcher must be installed on **both**, or `person_share_design` raises on the four interaction-carrier rows; both installers are run and both verifications persisted (`int_zero_route_equals_zero_arm_bit_exact: true`, equal-arm deviation `2.7755575615628914e-17`). The same fact forced the ordering guard onto **4** k2b instances rather than 1. | — |

RN-K2F-1's counts reproduce the registration's own per-leg statement ("K2b's 6,
K2c's 7, K2d's 6, K2e's 6, D-open's M-4 arm") and G0f's "26-row compilation".

### 0.2 The compilation — 26 rows, every level and covariate re-derived

Levels are the mean of `recovery_b_only` over an arm's worlds, recomputed from
the rawest persisted file with round-trip float parsing
(`float_precision="round_trip"`), then compared bit-for-bit against the leg's
own published value. Covariates come from the published machinery, never from
field values: `r` from `predicted_attenuation`
(`scripts/run_suica_m4_k2c_matched_pairs.py:186-191`, and
`scripts/run_suica_m4_k2d_frontier_carrier.py:273-279` for the four rows with a
non-zero interaction carrier), `V_person` from `person_share_design`
(`scripts/run_suica_m4_k2e_double_matching.py:234-241`).

| row | leg | arm | share | int | φ | worlds | r_pred | V_person | level |
|---|---|---|---|---|---|---|---|---|---|
| K2b:A1 | K2b | A1 | `0.02` | `0.0` | `0.9` | 8 | `0.8271784593117322` | `0.006` | `0.177888649457317` |
| K2b:A2 | K2b | A2 | `0.1` | `0.0` | `0.9` | 8 | `0.7849057220233866` | `0.03000000000000001` | `0.1506896317900927` |
| K2b:A3 | K2b | A3 | `0.3` | `0.0` | `0.9` | 8 | `0.6758917867864564` | `0.09000000000000002` | `0.10962256916514518` |
| K2b:A4 | K2b | A4 | `0.5` | `0.0` | `0.9` | 8 | `0.558364277337817` | `0.15000000000000002` | `0.07543949574114414` |
| K2b:A5 | K2b | A5 | `0.3` | `0.0` | `0.98` | 8 | `0.645057248597175` | `0.09000000000000002` | `0.11574817692039557` |
| K2b:A6 | K2b | A6 | `0.5` | `0.0` | `0.98` | 8 | `0.5193517935368367` | `0.15000000000000002` | `0.06918364030560309` |
| K2c:P1a | K2c | P1a | `0.10921276830855525` | `0.0` | `0.9` | 32 | `0.78` | `0.03276383049256658` | `0.15871254618530495` |
| K2c:P1b | K2c | P1b | `0.0873786568216755` | `0.0` | `0.98` | 32 | `0.7800000000000001` | `0.026213597046502654` | `0.1620474716206881` |
| K2c:P2a | K2c | P2a | `0.29267462506992153` | `0.0` | `0.9` | 32 | `0.68` | `0.0878023875209765` | `0.11995446641787935` |
| K2c:P2b | K2c | P2b | `0.24421800730418725` | `0.0` | `0.98` | 32 | `0.68` | `0.0732654021912562` | `0.13212198302374079` |
| K2c:P3a | K2c | P3a | `0.4973617623232523` | `0.0` | `0.9` | 32 | `0.5600000000000002` | `0.1492085286969757` | `0.08225066394872052` |
| K2c:P3b | K2c | P3b | `0.4359007987784457` | `0.0` | `0.98` | 32 | `0.5600000000000002` | `0.13077023963353374` | `0.09580994783492192` |
| K2c:A1anc | K2c | A1anc | `0.02` | `0.0` | `0.9` | 32 | `0.8271784593117322` | `0.006` | `0.1785831487097378` |
| K2d:FR45a | K2d | FR45a | `0.6634207990183637` | `0.0` | `0.9` | 32 | `0.45000000000000007` | `0.19902623970550914` | `0.05705094660907048` |
| K2d:FR45b | K2d | FR45b | `0.6061873016248464` | `0.0` | `0.98` | 32 | `0.45000000000000007` | `0.1818561904874539` | `0.06693033221632827` |
| K2d:SP68slow | K2d | SP68slow | `0.29267462506992153` | `0.0` | `0.9` | 32 | `0.68` | `0.0878023875209765` | `0.12039037534592587` |
| K2d:SP68int | K2d | SP68int | `0.14633731253496077` | `0.2806659454238726` | `0.9` | 32 | `0.6800000000000002` | `0.12810097738765003` | `0.0900394657375559` |
| K2d:SP56slow | K2d | SP56slow | `0.4973617623232523` | `0.0` | `0.9` | 32 | `0.5600000000000002` | `0.1492085286969757` | `0.08225219735962576` |
| K2d:SP56int | K2d | SP56int | `0.24868088116162615` | `0.37685012551875713` | `0.9` | 32 | `0.5600000000000002` | `0.18765930200411501` | `0.0551914191846241` |
| K2e:DM68a | K2e | DM68a | `0.29267462506992153` | `0.0` | `0.9` | 32 | `0.68` | `0.0878023875209765` | `0.12696018020695515` |
| K2e:DM68b | K2e | DM68b | `0.20690025098519338` | `0.08577437408472816` | `0.98` | 32 | `0.68` | `0.08780238752097648` | `0.1205360563958062` |
| K2e:DM56a | K2e | DM56a | `0.4973617623232523` | `0.0` | `0.9` | 32 | `0.5600000000000002` | `0.1492085286969757` | `0.09267656776408613` |
| K2e:DM56b | K2e | DM56b | `0.3515995738630727` | `0.14576218846017958` | `0.98` | 32 | `0.5600000000000002` | `0.1492085286969757` | `0.08375868094687854` |
| K2e:VS62a | K2e | VS62a | `0.39758432365362883` | `0.0` | `0.9` | 32 | `0.6200000000000001` | `0.11927529709608865` | `0.10924229469593509` |
| K2e:VS62b | K2e | VS62b | `0.3401102295271236` | `0.0` | `0.98` | 32 | `0.62` | `0.10203306885813711` | `0.1198405729656353` |
| Dopen:M-4 | Dopen | DOPEN-S4 | `0.4` | `0.0` | `0.9` | 32 | `0.6185853753498524` | `0.12000000000000004` | `0.09350089316336324` |

Full per-row provenance (rawest file, design source, persisted `r`, persisted
`V`) is in `results/m4_k2f_level_law/part0_tables.md` and as columns of
`compiled_rows.csv`. Sources by leg:

- **K2b** levels from `results/m4_k2b_t4_branch/arm_{A1..A6}_field.csv` (8 worlds each), cross-checked against `decision.json:leans.L-D.per_arm[].b_only_mean`; design from `manifest.json:arms[]`; persisted `r` from `part0_predictions.csv:r_card_b_pred_raw`.
- **K2c / K2d / K2e** levels from `arm_{ID}_field_w000_015.csv` + `arm_{ID}_field_w016_031.csv` (32 worlds each), cross-checked against `decision.json:descriptive.per_arm.<arm>.field_b_only`; design and persisted `r` (and, for K2e, persisted `V`) from `part0_arms.json`.
- **D-open M-4** level from `results/dopen_seal_opening/m4_field_rows.csv`, cross-checked against `stage1_m4.json:measured_recovery_b_only.mean`; persisted `r` and `V` from `stage1_m4.json:law_inputs`.

**Round-trip result:** levels **26/26 bit-exact** against the published values
(max abs diff `0.0`); `r` **25/25 bit-exact** (max abs diff `0.0`; K2c's A1anc
anchor has no persisted `r`); `V_person` **7/7 bit-exact** (max abs diff `0.0`;
only K2e and D-open persist it, so the other 19 rows are derived, not checked —
disclosed).

**Disclosed structure of the design (found in Part 0, before any fit).** Three
clusters of rows sit at *identical* `(r, V)`:

| r | V | rows | level spread |
|---|---|---|---|
| `0.5600000000000002` | `0.1492085286969757` | K2c:P3a, K2d:SP56slow, K2e:DM56a, K2e:DM56b | `0.010425903815365609` |
| `0.68` | `0.0878023875209765` | K2c:P2a, K2d:SP68slow, K2e:DM68a, K2e:DM68b | `0.0070057137890758014` |
| `0.8271784593117322` | `0.006` | K2b:A1, K2c:A1anc | `0.0006944992524207938` |

K2e's double-matched b-sides sit on their a-sides' covariates **by design** —
that is what the H-VAR test is. Also, `r` and `V` are near-collinear across the
26 rows (`corr = −0.9643543785903034`): both are driven by the state share.
Two consequences, both stated before fitting: (i) no function of `(r, V)` can
separate a tied cluster, so the within-tie spread is an irreducible floor; (ii)
the split between the `r^q` term and the `V` term is weakly identified, so wide
intervals on `q` are expected and must not be read as a defect of the fit.

### 0.3 The three candidate forms — pre-declared, no others

| form | expression |
|---|---|
| **F1** | `field = λ′·r^q′ − κ′·V` |
| **F2** | `field = λ′·r^q′ − κ′·V·r^p` |
| **F3** | `field = (λ′ − κ′·V)·r^q′` |

**F2 nests both**: F1 is F2 at `p = 0`, F3 is F2 at `p = q′`. So F2 cannot fit
worse in sample than either, and leave-one-out is precisely what makes it pay
for its fourth parameter.

### 0.4 Optimizer pins

| pin | value |
|---|---|
| routine | `scipy.optimize.least_squares`, scipy `1.17.1` |
| method / jacobian / bounds | `trf` / `2-point` numerical / unbounded, `x_scale=1.0` |
| tolerances | `ftol = xtol = gtol = 1e-14`, `max_nfev = 20000`, plain (linear) loss |
| multi-start grid | λ ∈ {0.05, 0.17417497661611914, 0.5} × q ∈ {0.5, 1.0, 1.8528700746510731, 3.0} × κ ∈ {0.0, 0.7220359963712748, 2.0}, and for F2 × p ∈ {0.0, 1.0, 1.8528700746510731} |
| starts | **36** (F1), **108** (F2), **36** (F3) |
| "same optimum" tolerance | relative SSE agreement `1e-12` |
| LOO starts | the same grid **plus** the full-data optimum (37 / 109 / 37 per held-out row) |
| parameter CIs | nonparametric bootstrap over rows, `B = 2000`, `seed = 20260826`, started at the full-data optimum; resamples with fewer than 3 distinct `r` values or any \|param\| ≥ 1e6 discarded and counted |

### 0.5 The baseline — the SEALED form, frozen, stated plainly

The baseline is the sealed T4 composite at its **published constants, not
refitted**: `λ = 0.17417497661611914`, `q = 1.8528700746510731`,
`κ_hat = −0.7220359963712748` (D1 bundle, opened in D-open;
`results/dopen_seal_opening/opened_bundle_view.json:predictions[S-4].constants`).
Because it is frozen it has no leave-one-out variability: **its "LOO"-RMSE
is simply its residual RMSE on the same 26 rows**, and it is reported under
that name throughout.

| baseline quantity | value |
|---|---|
| residual RMSE on the 26 rows | **`0.11259090547752257`** |
| mean signed residual (law − measured) | `-0.10906524853261387` |
| residual range | `[-0.1610876677874571, -0.05967241765543682]` |

Every one of the 26 residuals is negative: the sealed law under-predicts the
level at *every* persisted arm, extending D-open's six-arm observation
(−0.060 to −0.126) to the full corpus.

### 0.6 Rule 11 — satisfiability, and rule 22 — sides

| clause | sided | improvement side | bar |
|---|---|---|---|
| L-1 (i) best LOO-RMSE ≤ 0.010 | one-sided | **DOWN** | `0.01` |
| L-1 (ii) best LOO-RMSE ≤ baseline/2 | one-sided | **DOWN** | `0.056295452738761284` |
| L-2 measured inside prediction ± 2×LOO-RMSE | **two-sided** | neither — containment; a miss on either side falsifies | set at Stage 2 |

Joint binding bar `min(0.01, 0.056295452738761284) = 0.01`; **clause (i)
binds**, and the pair is jointly satisfiable (any value in `(0, 0.01]` satisfies
both). The baseline is arithmetic at frozen constants — no fitting — which is
what makes this check real in Part 0 rather than nominal.

### 0.7 Rule 17 — realizability of Stage 1

The tied clusters put a floor under every candidate form. Computed before any
fit: irreducible **in-sample** RMSE floor `0.0020486044913194325`; irreducible
**LOO** RMSE floor `0.002735243174745005` (a held-out row's cluster-mates
number `m−1`, so its LOO error is inflated by `m/(m−1)`). Both are below the
`0.010` bar, so **L-1 is realizable**; a floor above the bar would have made the
lean unsatisfiable by construction and stopped the leg.

### 0.8 Rule 23 — the stage at which each gate's inputs exist

| gate | inputs exist at |
|---|---|
| G0f | Part 0 (persisted D-open artifacts + the 26 rows) |
| G1f | the predict/arm boundary (the stamp, the counter, the permit) |
| G2f | **after** the prediction stamp (RN-K2F-4), before the 32 scored worlds |
| G3f | Stage 1 (satisfiability, sides) and Stage 2 (B, boundaries) |
| G4f | finalize (all persisted values, and the prose) |

### 0.9 Rule 16 — the three cells, enumerated, no gaps

| cell | L-1 | L-2 | route | slug |
|---|---|---|---|---|
| 1 | MISS | not adjudicated (arm still run, for the record) | T4 scoped PERMANENTLY to response form; the level question closes answered-in-the-negative | `NO_LEVEL_LAW` |
| 2 | HOLD | HOLD | the level law is RESTORED in the winning form; inherits the fragility-annex quoting rules; a D1-style seal is the named follow-up | `LEVEL_LAW_RESTORED` |
| 3 | HOLD | MISS | OVERFIT — the refit describes, does not predict; T4 scoped to response form; the winning form recorded descriptive-only | `LEVEL_LAW_OVERFIT` |

L-1 ∈ {HOLD, MISS} and, when L-1 holds, L-2 ∈ {HOLD, MISS}: total, no overlap.
The registration named `UNRESOLVABLE` only through the rule-17 fallback (a
non-finite or saturated pilot), which did not fire.

### 0.10 G0f — D-open's S-4 anchors, bit-exact

| anchor | expected | re-derived / persisted | bit-exact |
|---|---|---|---|
| sealed prediction | `-0.015116265289181696` | `-0.015116265289181696` | ✓ |
| measured b-only recovery | `0.09350089316336324` | `0.09350089316336324` | ✓ |
| CI lo | `0.08624502054643839` | `0.08624502054643839` | ✓ |
| CI hi | `0.10103687186109606` | `0.10103687186109606` | ✓ |
| `r` | `0.6185853753498524` | `0.6185853753498524` | ✓ |
| `V_person` | `0.12000000000000004` | `0.12000000000000004` | ✓ |

Plus the compilation audit of §0.2. **G0f PASS.**

---

## 1. Stage 1 — the fits

| form | λ′ | q′ | κ′ | p | in-sample RMSE | R² vs mean |
|---|---|---|---|---|---|---|
| **F1** | `0.17346136414455723` | `-0.15864657750225272` | `0.7247210056790004` | — | `0.005579849467280071` | `0.974047967552096` |
| **F2** | `0.18021628978547316` | `-0.009622064624441264` | `0.750086268225045` | `0.2064406330042716` | `0.005474614013402661` | `0.9750176424605855` |
| **F3** | `0.18009724674725458` | `0.06164248438626035` | `0.6360902393932114` | — | `0.005763865953705927` | `0.9723080107466112` |

Bootstrap 95% intervals (`B = 2000`, seed `20260826`; **2000/2000 resamples used
for every form**, 0 discarded), with the rule-13 `B = 20000` re-run beside them:

| form | parameter | 95% CI (B=2000) | 95% CI (B=20000) |
|---|---|---|---|
| F1 | λ′ | `[0.16690752512621174, 0.18502304366750907]` | `[0.1672132016274437, 0.18561317711131875]` |
| F1 | q′ | `[-0.34396054438575774, 0.1907267583818416]` | `[-0.3356463659118309, 0.210155181138263]` |
| F1 | κ′ | `[0.559974196707491, 0.833473222660496]` | `[0.5495045854913163, 0.8296955728891077]` |
| **F2** | λ′ | `[0.16314877137031103, 0.20134544738508586]` | `[0.16395220842547362, 0.20113293448674938]` |
| **F2** | q′ | `[-0.3792124136721057, 0.5313115708778163]` | `[-0.359641900748643, 0.5749000586407423]` |
| **F2** | κ′ | `[0.5202855978239498, 0.8612166024267973]` | `[0.5034052451994765, 0.860882393706231]` |
| **F2** | p | `[-0.274576360541506, 0.6783179586975702]` | `[-0.26509717839094277, 0.6804665164063352]` |
| F3 | λ′ | `[0.16312042543602734, 0.2009168323132954]` | `[0.16338954648280904, 0.20097023645352408]` |
| F3 | q′ | `[-0.2832814573439836, 0.5823389412995601]` | `[-0.2882491460479585, 0.5816306774261398]` |
| F3 | κ′ | `[0.5611134180374822, 0.6773729794353077]` | `[0.5558259199721106, 0.6765500885034547]` |

**Multi-start audit.** Every start converged and every start reached the same
optimum: F1 36/36 starts at the global SSE, F2 108/108, F3 36/36; **1 distinct
optimum per form** at the `1e-12` relative tolerance. Local minima are not a
live risk here.

**Reading the parameters.** κ′ lands at `0.72–0.75` across all three forms —
statistically indistinguishable from the sealed κ = `0.7220359963712748`. q′
collapses to ≈ 0 with an interval straddling zero in all three. F2's extra
parameter `p` is likewise indistinguishable from 0. So the fitted surface is,
to the resolution these 26 rows support, **`field ≈ 0.18 − 0.75·V_person`**:
an intercept minus the same variance tax. Given `corr(r, V) = −0.9643543785903034`
this leg cannot claim that `r` is *irrelevant* — only that, once `V` is in the
model, no power of `r` earns its keep. That is a statement about
identifiability on this corpus, and it is the honest one.

## 2. The LOO table and the selection

| form | **LOO-RMSE** | LOO MAE | LOO max abs | failed refits |
|---|---|---|---|---|
| **F2 (winner)** | **`0.0061559195350209`** | `0.004472780414938132` | `0.016200819149920512` | 0 |
| F1 | `0.0061727757182724885` | `0.004559841574781416` | `0.016724611732529898` | 0 |
| F3 | `0.006453886460034428` | `0.005273197547844569` | `0.013620476795316971` | 0 |
| — sealed baseline (frozen; residual RMSE, not a LOO) | `0.11259090547752257` | — | `0.1610876677874571` | n/a |

**The F1/F2 selection is a near-tie and must not be over-read.** The separation
is `1.6856183251588372e-05`, i.e. **0.27%** of the winner's LOO-RMSE. Rule 13
flagged it as boundary-adjacent and the `B = 20000` re-run was executed (§1).
The tie is immaterial to Stage 2 for a checkable reason recorded *inside the
hashed prediction file*: all three forms predict the fresh arm within
`0.00084` of one another, and all three fall inside the band (§4).

The worst-fit rows under F2 (held-out errors): K2b:A6 `+0.016200819149920512`,
K2e:DM56a `-0.01147863107280822`, K2e:VS62a `-0.009896650831525008`,
K2b:A2 `+0.009865923347981337`, K2b:A3 `+0.009681551292381976`. Four of the
five worst are 8-world K2b arms or tied-cluster members — the two places the
data are noisiest and the covariates least able to discriminate.

## 3. L-1 — the verdict

| clause | value | bar | met |
|---|---|---|---|
| (i) best LOO-RMSE ≤ 0.010 | `0.0061559195350209` | `0.01` | **yes** (38.4% below) |
| (ii) best LOO-RMSE ≤ baseline / 2 | `0.0061559195350209` | `0.056295452738761284` | **yes** (89.1% below) |

Improvement factor over the sealed baseline: **`18.28985983929699`×** — against
a required 2×. **L-1 [prior .55] HOLDS.**

### 3.4 Second reading (RN-K2F-2): inverse-variance weighting

Re-fitting with weights `1/SEM²` (up-weighting the 32-world arms) moves nothing
material: F1 → `(0.17263022263050648, -0.20178942431307947, 0.7428780965853438)`,
F2 → `(0.1773289654128293, -0.09545226472843876, 0.7577627233602068, 0.136747978143475)`,
F3 → `(0.17775402259112336, 0.004573463889709892, 0.6288295938431131)`. Their
unweighted RMSEs on the same rows are `0.005690341932417579`,
`0.005570007093536646`, `0.005892150420516888` — the same ordering, the same
picture, and q′ still ≈ 0.

---

## 4. The Stage-2 prediction — written and hashed BEFORE the arm existed

**This section records the prediction. The measured value appears only in §5.**

```
winning form  F2 :  field = λ′·r^q′ − κ′·V·r^p
θ             λ′ = 0.18021628978547316   q′ = -0.009622064624441264
              κ′ = 0.750086268225045      p  = 0.2064406330042716
fresh arm     share .45, φ .90, w_int zero, 32 worlds, master_seed 20260826
              (K2f lineage, salt m4k2f-world)
inputs        r_pred    = 0.5889058864943755
              V_person  = 0.13500000000000004
PREDICTION    0.09036036155829047
band          ±2 × LOO-RMSE = ±0.0123118390700418
              [0.07804852248824867, 0.10267220062833227]
```

Also recorded inside the hashed file, before any world existed:

| quantity | value |
|---|---|
| F1 would predict | `0.09082455783734975` |
| F2 (the winner) predicts | `0.09036036155829047` |
| F3 would predict | `0.09119929913183332` |
| the **sealed** form would predict | `-0.03217523530690303` |

### 4.1 Ordering attestation (G1f) — enforced, not asserted

| item | value |
|---|---|
| `prediction.json` sha256 | **`48dcabe6b813305a712e87e78eba05d03765a513c050e68073bd3dfc4184c420`** (1169 bytes) |
| stamp written | `2026-08-09T19:55:18.139607+00:00` |
| permit issued (arm process) | `2026-08-09T19:55:32.725509+00:00` |
| **gap** | **`+14.586 s` after the stamp** |
| fresh-arm generations before the stamp | **`0`** |
| k2b instances guarded | **4** (RN-K2F-5) |
| entry points wrapped | **12** = 3 × 4 (`build_k2b_world`, `run_field_world`, `emit_panel`) |
| permit mechanism | `prediction.json` re-read from disk and re-hashed; permit granted only on a match against the stamped digest, and only with the counter at 0 |
| cross-process leg | `predict` refuses to run if any fresh-arm artifact (`fresh_arm_field.csv`, `fresh_arm_field_k2b_lineage.csv`, `fresh_arm.json`, `pilot_field.csv`, `g2f_pilot.json`) already exists |
| append-only log | `results/m4_k2f_level_law/ordering_log.jsonl` |

A guard on one k2b instance would have been nominal: RN-K2F-5's private-loader
fact means three other reachable instances could have generated a world without
tripping it. All four are wrapped.

---

## 5. Stage 2 — the measurement

### 5.1 G2f — the rule-17 pilot (after the stamp, per RN-K2F-4)

Pilot worlds `9601`, `9602` (reserved, disjoint from the scored `0..31`):
`recovery_b_only` = `0.1122568775501732`, `0.09868106447957786` — finite,
strictly inside `(0, 1)`, k2b's own G4b route residuals `0.0` max-abs.
**G2f PASS.** The declared fallback (non-finite or saturated → STOP, L-2
UNRESOLVABLE, prediction stands on the record) did not fire.

### 5.2 The scored arm

| quantity | value |
|---|---|
| **measured b-only field recovery, 32 worlds** | **`0.09348041524223985`** |
| world-block bootstrap CI (`B = 2000`, seed `20260826`, 32 blocks) | `[0.0840861788911068, 0.10345598492352123]` |
| bootstrap sd | `0.0050103590231738715` |
| rule-13 re-run at `B = 20000` | `[0.0838367750797846, 0.10322088456338437]`, max endpoint shift `0.00024940381132219913`, containment unchanged |
| mixed-route recovery (companion) | `0.1938412673446392` |
| realized arm shares | `slow 0.13500000000000004`, `mu 0.08250000000000002`, `common 0.08250000000000002`, `int 0.0`, `noise 0.7000000000000001` |

### 5.3 Second reading (RN-K2F-3): the k2b world lineage

Running the same arm on **k2b's** world seeds — the panels every training row
was measured on — gives `0.08709612152185398`, CI
`[0.07961683287469572, 0.09477197120184305]`. **Also inside the band.** The two
lineages differ by `0.006384293720385875` against a difference SE of
`0.006348549054442376` — `1.01` SE, i.e. world-draw noise. Reported; it does
not adjudicate L-2.

## 6. L-2 — the verdict

| quantity | value |
|---|---|
| predicted (hashed before the arm) | `0.09036036155829047` |
| band | `[0.07804852248824867, 0.10267220062833227]`, half-width `0.0123118390700418` |
| **measured** | **`0.09348041524223985`** |
| signed error (measured − predicted) | `+0.003120053683949381` |
| as a fraction of the half-width | **`0.2534`** |
| as a multiple of the LOO-RMSE | `0.5068379575463031` |
| inside the band | **yes** |
| distance outside | `0.0` |

**L-2 [prior .60, conditional on L-1] HOLDS.**

For contrast, on this same arm the **sealed** form's prediction
(`-0.03217523530690303`) misses the measurement by `0.12565565054914288` —
`20.41 ×` the winning form's LOO-RMSE, and squarely inside the −0.060..−0.126
under-prediction family D-open documented.

**One caveat, volunteered.** The fresh arm's share `.45` lies *between* training
rows at `.40` (D-open's M-4) and `.4974/.50` (P3a, SP56slow, DM56a, A4), so L-2
is an **interpolation** test, not extrapolation. This was written into Part 0
before the fit, and it bounds what the HOLD buys: the restored law is shown to
predict *inside* the corpus's design envelope. Extrapolation is untested. A
coincidence worth naming rather than hiding: the measured `0.09348041524223985`
sits `0.0000205` from D-open's M-4 measurement at share `.40` — that is a
sampling coincidence across two independent 32-world draws (the k2b-lineage
reading of the same `.45` arm gives `0.08709612152185398`), not evidence that
the arm failed to move.

---

## 7. Routing (rule 16) and scorecard

**Cell 2 — L-1 HOLD, L-2 HOLD → `LEVEL_LAW_RESTORED`.** The level law is
restored in the winning form F2. It inherits the D2 fragility annex's quoting
rules, and a D1-style prospective seal is the named follow-up.

| item | value |
|---|---|
| rows compiled | **26** (K2b 6, K2c 7, K2d 6, K2e 6, D-open 1) |
| levels bit-exact vs published | **26/26** |
| `r` bit-exact vs persisted | **25/25** |
| `V` bit-exact vs persisted | **7/7** |
| winner | **F2**, `field = λ′·r^q′ − κ′·V·r^p` |
| winner LOO-RMSE | `0.0061559195350209` |
| sealed baseline residual RMSE | `0.11259090547752257` |
| improvement factor | `18.28985983929699`× |
| **L-1 [.55]** | **HOLD** |
| prediction (hashed first) | `0.09036036155829047`, band `[0.07804852248824867, 0.10267220062833227]` |
| measured | `0.09348041524223985`, CI `[0.0840861788911068, 0.10345598492352123]` |
| **L-2 [.60]** | **HOLD** |
| **verdict slug** | **`LEVEL_LAW_RESTORED`** |

### Gates

| gate | status | detail |
|---|---|---|
| **G0f** | **PASS** | D-open's six S-4 anchors bit-exact; 26-row compilation audited with per-row provenance; 26/26 levels, 25/25 `r`, 7/7 `V` bit-exact |
| **G1f** | **PASS** | stamp `19:55:18.139607Z` → permit `19:55:32.725509Z` (`+14.586 s`); `0` fresh-arm generations before the stamp; 12 entry points wrapped over 4 k2b instances; hash re-read from disk |
| **G2f** | **PASS** | rule-17 fresh-arm pilot finite, strictly inside `(0,1)`, G4b route residuals `0.0` |
| **G3f** | **PASS** | rule 11 satisfiability computed in Part 0 (binding bar `0.01`); rule 22 sides declared for all three clauses; rule 23 gate stages named; rule 13 at `B=2000` seed `20260826` with the `B=20000` re-run at both flagged boundaries; rule 18 not applicable (L-1 and L-2 share no generative knob — L-1 is artifact-space arithmetic, L-2 is a fresh arm) |
| **G4f** | **PASS** | hygiene; rule-16 three-cell enumeration total and non-overlapping; rule 24 applied to this document (§8) |

### Rule 13 record

| stage | quantity | value | bar | boundary? | action |
|---|---|---|---|---|---|
| 1 | best LOO vs `0.010` | `0.0061559195350209` | `0.01` | no (−38.4%) | — |
| 1 | best LOO vs baseline/2 | `0.0061559195350209` | `0.056295452738761284` | no (−89.1%) | — |
| 1 | **LOO separation, winner vs runner-up** | `1.6856183251588372e-05` | `0` | **yes** (+0.27%) | all parameter CIs re-run at `B=20000` |
| 2 | measured vs band lo | `0.09348041524223985` | `0.07804852248824867` | no (gap `0.015431892753991178`) | — |
| 2 | measured vs band hi | `0.09348041524223985` | `0.10267220062833227` | no | — |
| 2 | containment at `B=20000` | — | — | — | unchanged; max endpoint shift `0.00024940381132219913` |

---

## 8. Rule 24 — prose verification, and anomalies

Every number in this document was re-read from the persisted artifacts
(`part0.json`, `compiled_rows.csv`, `fits.json`, `loo.json`, `prediction.json`,
`prediction.sha256.json`, `fresh_arm.json`, `decision.json`) before commit;
derived quantities (the 18.29× factor, the `0.2534` band fraction, the
`20.41 ×` sealed miss, the `14.586 s` gap, the `1.01` SE lineage difference)
were recomputed from those values rather than copied from a run log.

**Anomalies, with timing.**

- **A-1 (≈ 8 min in, during Part 0 implementation, before any fit or level number was produced).** `k2b.arm_weights` (k2b:198-210) refuses the `int:t` carrier string that four compiled rows carry, so covariate derivation crashed. Cause: K2d's disclosed dispatcher (k2d:206-237) was not installed. Fixed by installing it and persisting K2d's own bit-exactness verification.
- **A-2 (≈ 10 min in, immediately after A-1, still before any fit).** The same crash reappeared one call later on the `person_share_design` path. Cause is RN-K2F-5: the published legs' private importlib loaders bypass `sys.modules`, so `k2e.k2d()` is a *different* k2d object owning a *different* k2b object, and patching one leaves the other untouched. Both installers are now run. This is a real property of the published machinery, not of this leg, and it is why the G1f guard was subsequently widened from 1 k2b instance to 4 — had it stayed at 1, the ordering gate would have been enforceable in name only.
- **A-3 (during Part 0, before any fit).** The compilation surfaced three tied-covariate clusters (10 of 26 rows) and `corr(r, V) = −0.9643543785903034`. Rather than merge or drop rows, the irreducible RMSE floors were computed and added to Part 0 as a rule-17 realizability argument, and Part 0 was re-persisted — still before the first fit.
- **A-4 (Stage 1, after the LOO table existed).** The F1/F2 selection separates by 0.27%. Disclosed rather than smoothed; rule 13 fired and the high-B re-run was executed. Because all three forms' fresh-arm predictions were written *inside the hashed file*, the reader can verify that the near-tie could not have changed L-2's outcome.
- **A-5 (Stage 2, after the measurement).** The measured value sits `0.0000205` from D-open's M-4 measurement at a *different* share. Named in §6 as a sampling coincidence, with the k2b-lineage reading (`0.08709612152185398`) as the check.

**Timing.** Compute: Part 0 `0.3 s`, Stage 1 `54.2 s` (of which `45.0 s` was the
rule-13 `B=20000` re-run), predict `< 1 s`, arm `38.6 s` (66 worlds: 2 pilot +
32 scored + 32 second-reading), finalize `< 1 s` — every stage inside its Part-0
estimate (`120 / 300 / 5 / 120 / 60 s`). No stage came near the 2× stop-and-report
threshold. No background jobs; all stages foreground and chunked.

## 9. What this leg does and does not establish

**Establishes.** (i) A level law exists on this instrument: a three- or
four-parameter function of `(r, V_person)` predicts b-only field recovery across
26 arms spanning four legs with a held-out RMSE of `0.0062` — 18× better than
the sealed composite. (ii) It *predicts*: a value fixed and hashed before the
arm existed landed at a quarter of its own band. (iii) The sealed law's failure
is localized — κ survives essentially unchanged; the `r^q` exponent does not.

**Does not establish.** (i) That `r` is irrelevant — `r` and `V` are collinear
at `−0.964` here by design, so this corpus cannot separate them; a decisive test
needs arms that break the collinearity. (ii) Extrapolation — L-2 was an
interpolation at share `.45`. (iii) That F2 is the right form — its margin over
F1 is 0.27%, and its extra parameter's interval contains 0; F1 is the more
parsimonious reading of the same surface and is not excluded. The honest
one-line summary of the fitted object is **an intercept minus a variance tax**,
with the attenuation exponent unresolved at this corpus's resolution.
