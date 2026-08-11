# M4-M1b — r-at-level, feasibility restated in the estimand's quantity

**Leg:** M4-M1b · **Registered** 2026-08-11 in
`docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md` (section "M4-M1b — r-at-level,
feasibility restated in the estimand's quantity"), commit `2e4e404`, BEFORE this
run. Re-registration of M4-M1 after its cell-1 STOP.
**Executor:** dispatched agent (implementation and execution only; the
registration text is binding).
**Harness:** `scripts/run_suica_m4_m1b_r_at_level.py`.
**Artifacts:** `results/m4_m1b_r_at_level/` (gitignored).
**Banner:** synthetic worlds on K2b's frozen instrument, exploratory, label-free;
a share × φ factorial whose ONLY feasibility gate is the estimand's own
projected identification width (rule 25).

**Verdict: `NON_PROJECTABLE` (rule-16 cell 1).** G3m′(b) — the feasibility gate,
and under rule 25 the only one — failed at 0.5 under the binding truth
at 32 worlds/cell **and again** after the pre-declared once-only escalation to
64. **16 pilot worlds ran; 0 main worlds were
generated and no fit was run.**

Rule 25 worked exactly as enacted, and this leg is its first two-sided test.
**It cleared the leg past M1's false death:** the marginal `corr(r, V)` on this
design is `-0.8495063312353189` — far above the 0.30 bar that killed M1, and now
correctly REPORTED rather than gating. **And it stopped the leg on a real one:**
the same design, carried to the quantity the estimand actually consumes, cannot
resolve `q` to the registered width at the registered budget. M1 died on a
number the estimand does not consume; M1b dies on the number it does. Those are
different failures, and only the second is information.

---

## Part 0 — written before any world

### 0.1 Rule 9 / rule 12 — open conventions, pinned in writing

| note | pinned reading |
|---|---|
| RN-M1B-1 | machinery COPIED into this file, then PROVEN faithful in Part 0 against the imported M1 harness (start grid, OPT, form expressions/names, and fit_form bit-exact on a fixed synthetic probe) |
| RN-M1B-2 | seed string pinned: v8.stable_bucket(f'{MASTER_SEED}-{share!r}-{phi!r}-{world}', salt=<m4m1b-world\|m4m1b-pilot>, modulus=2**31-1); streams disjoint from M1's and from each other by salt |
| RN-M1B-3 | G2m'(ii) gates on the k2b-side realized card attenuation r_card_b_raw at world grain (k2b:392-503 + :505-509 + :486; k2b's own G2 uses it at :944-963); the map-arithmetic certification is also recorded, so either reading of 'persists one' is satisfied. The pilot FIELD contrast is descriptive only and gates NOTHING -- a flat field is cell-2 evidence, not channel death (the registration's own correction of M1) |
| RN-M1B-4 | the `power` stage persists the DECIDED worlds-per-cell; every downstream stage reads it from that artifact, never from a constant |
| RN-M1B-5 | L-4 monotonicity read BOTH ways (sign agreement; and \|rho\|==1 plus sign agreement); L-4 adjudicates nothing so neither is adopted |
| RN-M1B-6 | lambda-vs-zero boundary: adjacent iff min(\|lo\|,\|hi\|) <= 0.05*\|lambda_hat\| |
| RN-M1B-7 | stage chunking: G3m'(b) is its own permit-gated stage `power` between `pilot` and `worlds_a`; the >=10xB re-run is its own stage `rule13` |
| RN-M1B-8 | the NON_PROJECTABLE handoff (added AFTER sigma_w existed, disclosed): on the registered STOP the `diagnose` stage MEASURES the smallest worlds/cell at which the binding truth would clear the bar, on a declared geometric ladder, instead of extrapolating -- the planner's own rule-11 convention that defect #43 bought. It consumes only sigma_w and the pinned design maps; NO field-outcome quantity bearing on L-1/L-2/L-3 enters it, and it adopts nothing |

RN-M1B-8 was added AFTER `σ_w` existed and is disclosed as such. It consumes only
`σ_w` and the pinned design maps — no field-outcome quantity bearing on
L-1/L-2/L-3 enters it — and it adopts nothing.

### 0.2 RN-M1B-1 — the copied machinery, proven faithful

The coordinator left "copy or import" open. The machinery is COPIED (so this
leg's pins cannot drift when a later leg edits M1's file) and Part 0 then
IMPORTS the M1 harness and proves the copy bit-exact: the start grid, the
optimizer dict, every inherited bar, and `fit_form` itself run on a fixed
synthetic probe in both modules.

| form | theta (this leg) | theta (M1 harness) | starts | expr match | bit-exact |
|---|---|---|---|---|---|
| F1 | [0.18884067245802816, 3.036413265466886, -0.2420494705823905] | [0.18884067245802816, 3.036413265466886, -0.2420494705823905] | 54 / 54 | True | True |
| F1e | [0.18884066941042968, 3.0364131856165906, -0.24204946537018907, 6.1848088665522316e-27] | [0.18884066941042968, 3.0364131856165906, -0.24204946537018907, 6.1848088665522316e-27] | 162 / 162 | True | True |
| F2 | [0.14073315413179824, 1.0536587416037417, 0.47099355447613456, 6.628209507787988] | [0.14073315413179824, 1.0536587416037417, 0.47099355447613456, 6.628209507787988] | 162 / 162 | True | True |
| F3 | [0.13208971979701528, 0.860593442595773, 0.06335713416929252] | [0.13208971979701528, 0.860593442595773, 0.06335713416929252] | 54 / 54 | True | True |

### 0.3 G0m′ — anchors bit-exact, including the two new clauses

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
| corr(r, V) over the 26 K2f rows (Pearson) | -0.9643543785903034 | -0.9643543785903034 | True |
| r(0.30, 0.90) | 0.6758917867864564 | 0.6758917867864564 | True |
| r(0.30, 0.98) | 0.645057248597175 | 0.645057248597175 | True |
| r(0.50, 0.90) | 0.558364277337817 | 0.558364277337817 | True |
| r(0.50, 0.98) | 0.5193517935368367 | 0.5193517935368367 | True |
| share envelope hi | 0.6634207990183637 | 0.6634207990183637 | True |
| share envelope lo | 0.02 | 0.02 | True |
| (v) Dopen:M-4 level, mean of the raw per-world CSV | 0.09350089316336324 | 0.09350089316336324 | True |
| (vi) `[1.71, 1.98]` verbatim in `docs/SUICA_IDENTITY_THEORY_V1.md` | [1.71, 1.98] | found on lines [805, 841] | True |
| (vii) ALT corr(r, V) | -0.8915685583022667 | -0.8915685583022667 | True |
| (vii) ALT corr(r^q, V) | -0.9029258027968385 | -0.9029258027968385 | True |
| (vii) MAIN corr(r, V) | -0.8495063312353189 | -0.8495063312353189 | True |
| (vii) MAIN corr(r^q, V) | -0.8649603255864755 | -0.8649603255864755 | True |
| (viii) M1 freed-shares bound | 0.5208187741410987 | 0.5208187741410987 | True |
| (viii) M1 full-interval r span at share 0.1 | 0.05159009087311539 | 0.05159009087311539 | True |
| (viii) M1 full-interval r span at share 0.25 | 0.11784317303319514 | 0.11784317303319514 | True |
| (viii) M1 full-interval r span at share 0.4 | 0.17083747134975158 | 0.17083747134975158 | True |
| (viii) M1 full-interval r span at share 0.6 | 0.21722718146551878 | 0.21722718146551878 | True |
| (viii) M1 infimum \|corr(r,V)\| at registered shares | 0.748768093111513 | 0.748768093111513 | True |

**(vii)** reproduces BOTH of the planner's embedded design tables bit-exactly —
the planner ran its own arithmetic at registration time, which is the
convention defect #43 bought, and it is correct to the last bit:

| share | V_person | r(phi=0.05) | r(phi=0.3) | r(phi=0.6) | r(phi=0.85) | r(phi=0.98) | span | bit-exact |
|---|---|---|---|---|---|---|---|---|
| 0.1 | 0.03000000000000001 | 0.8189581462487876 | 0.8155586799827954 | 0.8075174172340943 | 0.7908869485651705 | 0.7718092954224756 | 0.04714885082631204 | True |
| 0.25 | 0.07500000000000002 | 0.785015540293945 | 0.7761302864207245 | 0.7558507450373838 | 0.7168731389294273 | 0.6763691758553391 | 0.10864636443860598 | True |
| 0.4 | 0.12000000000000004 | 0.7411873080384952 | 0.726425348215848 | 0.6941115392115328 | 0.6367206581308248 | 0.5825497814736654 | 0.15863752656482977 | True |
| 0.6 | 0.18000000000000005 | 0.6573448847694047 | 0.6346912945232521 | 0.5883719155687073 | 0.5151304058057474 | 0.4541409476972356 | 0.20320393707216905 | True |

| share | ALT span (registration) | ALT span (re-derived) | bit-exact |
|---|---|---|---|
| 0.1 | 0.04374938456031985 | 0.04374938456031985 | True |
| 0.25 | 0.09976111056538539 | 0.09976111056538539 | True |
| 0.4 | 0.1438755667421826 | 0.1438755667421826 | True |
| 0.6 | 0.1805503468260165 | 0.1805503468260165 | True |

**(viii)** verifies the M1-STOP numbers the adjudication cites against this
executor's own `results/m4_m1_r_at_level/` artifacts — the infimum
`0.748768093111513`, the freed-shares bound `0.5208187741410987` and all four
full-interval spans re-read from `stop_diagnostic.json`. All bit-exact.

### 0.4 G1m′ — four gates, no proxy gate

| gate | bar | realized | PASS |
|---|---|---|---|
| (a) shares inside the trained envelope | [0.02, 0.6634207990183637] | [0.1, 0.25, 0.4, 0.6] | True |
| (b) V max/min | >= 2.0 | 6.0 | True |
| (c') within-share r SPAN at shares [0.4, 0.6] | >= 0.12 | [0.15863752656482977, 0.20320393707216905] | True |
| (e) duplicate (r, V) design points | 0 | 0 | True |
| *(no marginal-correlation gate -- rule 25)* | n/a | corr(r, V) = -0.8495063312353189, REPORTED only | n/a |

The (c′) bar is an ABSOLUTE span, not M1's ratio — the repair for defect #44's
second half, where the ratio bar was reachable at only two of four share levels
for any ladder. Realized spans at the two gated shares: `[0.15863752656482977, 0.20320393707216905]`
against a `0.12` bar.

| share | V_person | r min | r max | span | ratio | in (c') gate | span >= 0.12 |
|---|---|---|---|---|---|---|---|
| 0.1 | 0.03000000000000001 | 0.7718092954224756 | 0.8189581462487876 | 0.04714885082631204 | 1.0610887315117183 | False | False |
| 0.25 | 0.07500000000000002 | 0.6763691758553391 | 0.785015540293945 | 0.10864636443860598 | 1.160631750110746 | False | False |
| 0.4 | 0.12000000000000004 | 0.5825497814736654 | 0.7411873080384952 | 0.15863752656482977 | 1.2723158288095608 | True | True |
| 0.6 | 0.18000000000000005 | 0.4541409476972356 | 0.6573448847694047 | 0.20320393707216905 | 1.4474468512529728 | True | True |

### 0.5 The collinearity, REPORTED and gating nothing (rule 25)

| quantity (REPORTED, gates nothing -- rule 25) | value |
|---|---|
| corr(r, V) on M1b's 20-point design | -0.8495063312353189 |
| corr(r^1.8528700746510731, V) on M1b's design | -0.8649603255864755 |
| corr(r, V) on K2f's 26 rows | -0.9643543785903034 |
| M1's failed marginal bar (WITHDRAWN by rule 25) | <= 0.30 |

This is the rule-25 exemplar in one line: `-0.8495063312353189` would have failed M1's
withdrawn 0.30 bar by a factor of nearly three, and it is irrelevant, because
identification lives in the within-share φ sweeps at exactly fixed `V`.

---

## G2m′ — the pilot, and a vindication of the registration's own correction

| corner | phi-extension? | n | mean | sd | min | max | finite | inside (0,1) | nonzero var | PASS |
|---|---|---|---|---|---|---|---|---|---|---|
| s0.10_p0.05 | True | 4 | 0.1512477584584036 | 0.02578853225279018 | 0.12201975197145519 | 0.1839818634540913 | True | True | True | True |
| s0.10_p0.98 | False | 4 | 0.16780850113538825 | 0.021970259723813244 | 0.14322024604665107 | 0.1865514428385202 | True | True | True | True |
| s0.60_p0.05 | True | 4 | 0.04736597835735297 | 0.014181264775426325 | 0.032980259309520595 | 0.06667314417811425 | True | True | True | True |
| s0.60_p0.98 | False | 4 | 0.05463551492563269 | 0.013055799519999387 | 0.040344407177444 | 0.06853205905675834 | True | True | True | True |

| reading | role | mean at phi lo | mean at phi hi | contrast | pooled SE | abs(contrast)/SE | > 2.0x SE |
|---|---|---|---|---|---|---|---|
| realized card attenuation `r_card_b_raw` | **THE GATE** (RN-M1B-3) | 0.6594638199680429 | 0.45620831949245705 | 0.20325550047558588 | 0.002141887661159543 | 94.8954999654606 | True |
| field `recovery_b_only` | descriptive only -- gates NOTHING (rule 25) | 0.04736597835735297 | 0.05463551492563269 | -0.007269536568279722 | 0.009637974005686617 | 0.7542598230697173 | False (not a verdict) |
| pinned-map arithmetic certification | alternative route, also satisfied | -- | -- | 0.20320393707216905 | -- | -- | bit-exact vs registration: True |

**This is the finding of the pilot, and it is not a small one.** The φ→r channel
is alive beyond any doubt: the realized card attenuation moves
`0.20325550047558588` between φ = 0.05 and φ = 0.98 at share 0.60, which is
**94.8954999654606× its pooled SE**, and it lands `5.156340341683219e-05` from the
pinned map's PREDICTED `Δr = 0.20320393707216905` — the map's own value being the one
that reproduces the registration's span bit-exactly, not the measurement. The FIELD, at the same corner, moves
`-0.007269536568279722` — **0.7542598230697173× its pooled SE**, i.e. flat
within noise.

M1's registration would have gated on that second number as its declared
fallback. It is below 2× SE, so M1's liveness clause would have FAILED and M1
would have died a second false death — on evidence that the field does not
respond to φ, which is precisely what this leg exists to measure. M1b's
registration says so in advance: "an OUTCOME-side field contrast is NOT a
liveness gate here, because a flat field is cell-2 EVIDENCE, not channel death."
The correction was written before the number existed and the number vindicates
it.

That flat field is also, read honestly, weak *evidence* pointing at truth-table
cell 2 (`R_TERM_ABSENT_AT_LEVEL`). It is four worlds against four at one share.
**It adjudicates nothing here** — no lean is scored in this leg — and it is
recorded as an observation, not a result.

| cell | world | world seed | recovery_b_only | realized r_card_b_raw |
|---|---|---|---|---|
| s0.10_p0.05 | 0 | 581407630 | 0.14387328452636985 | 0.8187539096250657 |
| s0.10_p0.05 | 1 | 329361081 | 0.12201975197145519 | 0.819262125102087 |
| s0.10_p0.05 | 2 | 939169188 | 0.1551161338816981 | 0.8212787159762766 |
| s0.10_p0.05 | 3 | 1494896614 | 0.1839818634540913 | 0.8191158759522705 |
| s0.10_p0.98 | 0 | 662497333 | 0.1865514428385202 | 0.7726755994312857 |
| s0.10_p0.98 | 1 | 440427584 | 0.18614402486699405 | 0.7661858403989144 |
| s0.10_p0.98 | 2 | 1924571184 | 0.15531829078938772 | 0.7722457128513355 |
| s0.10_p0.98 | 3 | 453006784 | 0.14322024604665107 | 0.772786145739586 |
| s0.60_p0.05 | 0 | 660040360 | 0.04250745095790952 | 0.6555092615741597 |
| s0.60_p0.05 | 1 | 723137441 | 0.04730305898386751 | 0.656460891850261 |
| s0.60_p0.05 | 2 | 118273738 | 0.06667314417811425 | 0.663358102383875 |
| s0.60_p0.05 | 3 | 555648020 | 0.032980259309520595 | 0.6625270240638758 |
| s0.60_p0.98 | 0 | 190060613 | 0.062380450794752594 | 0.45655092054359425 |
| s0.60_p0.98 | 1 | 1538940406 | 0.04728514267357585 | 0.4579713952982407 |
| s0.60_p0.98 | 2 | 1434514948 | 0.040344407177444 | 0.4556053029776915 |
| s0.60_p0.98 | 3 | 1487178822 | 0.06853205905675834 | 0.45470565915030187 |

---

## G3m′(b) — the feasibility gate, and the stop

σ_w is the pooled per-world sd across the 16 pilot worlds, df-inflated as
registered.

| quantity | value |
|---|---|
| pooled per-world sd across the 16 pilot worlds (df 12) | 0.019489117988137468 |
| chi2_{0.1, df=12} | 6.3037960595843225 |
| df-aware inflation sqrt(12 / chi2) | 1.3797155080850578 |
| **sigma_w** (inflated) | **0.026889438327132725** |
| base n=32: cell-mean sd | 0.004753426045853251 |
| base n=32: projected q width at q_truth = 1.0 | 0.6446327208199195  **FAIL** |
| base n=32: projected q width at q_truth = 1.8528700746510731 | 1.1702741415331803  **FAIL** |
| base n=32: PASS (both truths <= 0.5) | False |
| escalated n=64: cell-mean sd | 0.0033611797908915907 |
| escalated n=64: projected q width at q_truth = 1.0 | 0.45036131116284384  PASS |
| escalated n=64: projected q width at q_truth = 1.8528700746510731 | 0.8082914682805795  **FAIL** |
| escalated n=64: PASS (both truths <= 0.5) | False |
| escalation fired | True |
| MC cross-check: the same n=64, q_truth=1.8528700746510731 cell re-drawn on a fresh stream | 0.7859406063487944 vs the gate's 0.8082914682805795 (abs diff 0.02235086193178515; both above the bar) |
| **gate verdict** | **FAIL -> NON_PROJECTABLE** |

At 32 worlds/cell the projected 95% width of `q̂` is `0.6446327208199195` under
q_truth = 1.0 and `1.1702741415331803` under q_truth = 1.8528700746510731, against a
`0.5` bar. The pre-declared escalation fired. At 64 worlds/cell the
widths are `0.45036131116284384` and `0.8082914682805795`: the first CLEARS the bar, the second
does not. The registration requires BOTH. **Gate FAIL → `NON_PROJECTABLE`.**

**The failure is precision, not pathology.** Median `q̂` tracks its truth at
every configuration (1.0: 1.0021891019795262, 1.8528700746510731: 1.8442504925087377 at n = 32) and not one replicate failed to
converge:

| q_truth | median q_hat at n=32 | replicates failed to converge |
|---|---|---|
| 1.0 | 1.0021891019795262 | 0 |
| 1.8528700746510731 | 1.8442504925087377 | 0 |

**The asymmetry, stated because it matters to the successor.** The gate is failed by ONE of its two registered truths. At q_truth = 1.0 the escalated design CLEARS the bar; at q_truth = 1.8528700746510731 it does not. Larger q means smaller r^q on r < 1, so the signal the exponent rides on shrinks and its interval widens -- the design is projected adequate under the truth the registered L-2 lean deems LIKELY (below the response band) and inadequate under the one it deems unlikely (prior .10 above / .35 overlap). The registration says BOTH, and BOTH is what was scored; this note reports the asymmetry, it does not relax the gate.

### What n would suffice — measured, not extrapolated

Defect #43 was an extrapolation where arithmetic was available. This leg does
not repeat it in its handoff: the smallest sufficient budget is MEASURED on a
declared geometric ladder `[64, 128, 192, 256, 384, 512]`, running the binding truth until it
clears and then confirming the other truth at the same n.

| worlds/cell | q_truth | cell-mean sd | projected q width | <= 0.5 |
|---|---|---|---|---|
| 64 | 1.8528700746510731 | 0.0033611797908915907 | 0.7859406063487944 | False |
| 128 | 1.8528700746510731 | 0.0023767130229266254 | 0.5516920936367253 | False |
| 192 | 1.8528700746510731 | 0.00194057805706599 | 0.45033528452170346 | True |
| 192 | 1.0 (confirm) | 0.00194057805706599 | 0.2531601642892628 | True |

**192 worlds/cell** is the smallest rung at which the binding truth clears
(`[0.7859406063487944, 0.5516920936367253, 0.45033528452170346]` at `[64, 128, 192]`), and the non-binding truth confirms
there at `0.2531601642892628`. That is **3840 worlds**, 6.0×
the registered base budget. Nothing here is adopted — the leg's verdict is the
registered STOP — but the successor no longer has to guess.

A caution on that number's own precision: the ladder re-drew the n = 64 binding
cell on a fresh stream and got `0.7859406063487944` where the gate got
`0.8082914682805795`, an absolute difference of `0.02235086193178515`. So the width proxy
itself carries roughly 0.027651982989911467 relative Monte-Carlo error at
B_proj = 500, and the ladder's rungs are coarse; n = 192 clears with margin,
the rung below misses at `0.5516920936367253`, and a successor wanting a tight budget
should re-run the ladder finely rather than read 192 as exact.

---

## Routing — the inherited truth table, reproduced verbatim

| # | condition | outcome |
|---|---|---|
| 1 | any G0m'/G1m'/G2m'/G3m' clause fails after its declared ladder | **STOP (planner defect; no fit is run) -- STOP_DESIGN_INFEASIBLE, or NON_PROJECTABLE where G3m'(b) fails after its once-only escalation**  <-- THIS LEG |
| 2 | L-1 MISS AND winner lambda CI contains 0 | R_TERM_ABSENT_AT_LEVEL -- the tax-only level law is the COMPLETE level story on this family; level-response dissociation named; q-at-level closes as structurally unposed; M2 proceeds on the tax-only form |
| 3 | L-1 MISS AND winner lambda CI excludes 0 | NON_IDENTIFIED_UNDERPOWERED -- CI reported, no q claim; M2 blocked; leverage redesign named |
| 4 | L-1 HOLD AND L-2 below | LEVEL_RESPONSE_DISSOCIATION -- q measured at level, below the response band; new named phenomenon; M2 seals the measured law |
| 5 | L-1 HOLD AND L-2 overlap | SINGLE_EXPONENT_RESTORED -- T4's level form completed with the response exponent; M2 seals |
| 6 | L-1 HOLD AND L-2 above | ABOVE_BAND_ANOMALY -- named; M2 seals the measured law; theory note required |
| -- | L-3 disjoint (either side), any cell 2-6 | modifier TAX_SHIFT_AT_LEVEL -- pre-registered anomaly fed into M3's charter |
| -- | L-3 overlap, any cell 2-6 | modifier: kappa's fourth independent appearance is counted |

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
| G1m'(a) | all shares inside [0.02, 0.6634207990183637] | two-sided containment | neither |
| G1m'(b) | V max/min >= 2.0 | one-sided | UP |
| G1m'(c') | within-share r SPAN >= 0.12 at BOTH shares [0.4, 0.6] | one-sided | UP |
| G1m'(e) | no duplicate (r, V) design points | exact | n/a |
| G2m'(i) | per-world fields finite, non-saturated, and nonzero within-corner variance | two-sided containment plus a nonzero-variance floor | neither |
| G2m'(ii) | realized card-attenuation contrast between phi .05 and .98 at share .60 exceeds 2.0x its pooled SE | one-sided | UP |
| G3m'(b) | projected q width proxy <= 0.5 under BOTH q truths -- THE feasibility gate, in the estimand's own quantity (rule 25) | one-sided | DOWN |
| descriptive (NOT a gate, rule 25) | marginal corr(r, V) and corr(r^q, V) across cells | reported only | n/a |

## Gates

| gate | PASS | detail |
|---|---|---|
| G0m' | True | (i)-(vi) M1's anchors re-verified; (vii) BOTH planner design tables reproduced bit-exactly; (viii) the M1-STOP numbers verified against results/m4_m1_r_at_level/ |
| G1m' | True | (a)(b)(c')(e) all pass; no marginal gate (rule 25) |
| G2m' | True | regime guard passed at all 4 corners; phi->r liveness on the realized card statistic passed decisively |
| G3m' | False | THE feasibility gate FAILED at n=32 and again after the pre-declared once-only escalation to n=64 |
| G4m' | True | inherited truth table reproduced verbatim; every report table generated from artifacts |

The four pre-declared forms and the optimizer pins were fixed in Part 0 before
the stop and are persisted, so a successor inherits them unchanged:

| form | expression | params | starts | bounded |
|---|---|---|---|---|
| F1 | field = lambda*r^q - kappa*V | ['lambda', 'q', 'kappa'] | 54 | False |
| F1e | field = lambda*r^q - kappa*V - epsilon, epsilon in [0, 0.05] | ['lambda', 'q', 'kappa', 'epsilon'] | 162 | True |
| F2 | field = lambda*r^q - kappa*V*r^p | ['lambda', 'q', 'kappa', 'p'] | 162 | False |
| F3 | field = (lambda - kappa*V)*r^q | ['lambda', 'q', 'kappa'] | 54 | False |

---

## Anomaly log — every anomaly, with pre/post-hypothesis timing

The hypothesis-relevant boundary in this leg is the PILOT: before it, no
outcome-side number existed; after it, the pilot field contrast and `σ_w` did.
No lean was ever scored.

- **A-1 — the interpreter (before Part 0, before any number).** The environment
  pinned in M4-M1 is reused verbatim: a CPython 3.12.12 virtual environment
  outside the repository, populated from `requirements-lock-main.txt`
  (numpy `2.4.4`, pandas `3.0.2`, scipy `1.17.1`), platform
  `macOS-26.4.1-arm64-arm-64bit`. The machine's only pandas still belongs to CPython 3.9.6,
  which cannot import the published machinery (`datetime.UTC` is 3.11+).
- **A-2 — `timeout(1)` absent on this platform (before Part 0).** Every stage
  ran as its own foreground command under an explicit harness-level timeout,
  all under the 600 s ceiling.
- **A-3 — the pilot's outcome-side flatness (AT the pilot, i.e. the first
  hypothesis-relevant number).** `0.7542598230697173×` SE on the field against
  `94.8954999654606×` SE on the card channel. Reported above. It changed no
  gate, because M1b's registration had already removed the field from the
  liveness clause BEFORE the number existed. Had the executor been free to
  choose after seeing it, the choice would have been contaminated; it was not
  free, and that is the point.
- **A-4 — the gate failed and the escalation fired (AFTER `σ_w` existed).**
  Pre-declared, once only, applied exactly as written; no second escalation was
  attempted.
- **A-5 — RN-M1B-8 was added after `σ_w` existed (disclosed).** The n-ladder
  diagnostic consumes only `σ_w` and the pinned design maps; no field-outcome
  quantity bearing on any lean enters it, and it adopts nothing.
- **A-6 — a Monte-Carlo discrepancy at the one overlapping configuration
  (after the gate).** `0.7859406063487944` vs `0.8082914682805795` at the same
  (n = 64, q_truth = 1.8528700746510731); the gate stage draws both truths from
  one seeded stream while the ladder re-seeds per cell, so the two consume
  different stretches. Both are above the bar and the GATE value is the power
  stage's — the registered one. Disclosed rather than smoothed, and it doubles
  as a measurement of the proxy's own MC error.
- **A-6b — rule 24 caught a claim in this leg's own prose (before commit).** The
  liveness paragraph first said the realized card contrast "agrees bit-exactly"
  with the pinned map's `Δr`. It does not, and could not: one is a measurement
  over 8 worlds, the other is deterministic algebra. They differ by
  `5.156340341683219e-05`. What IS bit-exact is the map against the
  registration's stated span. The sentence is now generated from both values.
- **A-7 — no stage approached its 2× stop-and-report threshold.** Part 0
  `1.920362949371338` s against 60 s; pilot `9.817700862884521` s against 40 s;
  power `82.54143500328064` s against a 120 s executor estimate; diagnose
  `79.65195512771606` s against 300 s.

| stage | registration estimate (s) | executor estimate (s) | measured (s) |
|---|---|---|---|
| part0 | 60 | 60 | 1.920 |
| pilot | 40 | 40 | 9.818 |
| power | -- | 120 | 82.541 |
| diagnose | -- | 300 | 79.652 |
| worlds_a | 150 | 150 | -- (not reached) |
| worlds_b | 150 | 150 | -- (not reached) |
| worlds_c | 150 | 150 | -- (not reached) |
| worlds_d | 150 | 150 | -- (not reached) |
| fit | 300 | 300 | -- (not reached) |
| rule13 | -- | 240 | -- (not reached) |
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

**Rule 25 is validated in both directions by one leg.** It let M1b past a
marginal correlation of `-0.8495063312353189` that M1's withdrawn bar would have
rejected, and — at the pilot — it prevented a second false death when the
outcome-side field contrast came in at `0.7542598230697173×` SE. A proxy gate
would have killed this design twice, on two different proxies, for two
different wrong reasons. The estimand-side gate killed it once, for the right
one.

**This is not a registration defect, and it should not be recorded as one.**
Every clause was satisfiable, every bar was computed, the ladder fired as
written, the escalation fired as written, and the gate returned a well-defined
verdict on a well-posed quantity. `NON_PROJECTABLE` is a pre-declared outcome of
a sound registration, not a defect in it. The one judgement call worth the
planner's attention is the **two-truth conjunction**: the design is projected
adequate under q_truth = 1.0 and inadequate under
q_truth = 1.8528700746510731, and the registered L-2 lean puts .55 on `q` being
BELOW the response band — i.e. the gate is decided by the truth the leg itself
considers least likely. Whether that conjunction is the intended conservatism or
an over-strict reading is the planner's to settle; the executor scored it as
written.

**Three routes, none adopted here.**

1. **Buy the precision.** `192` worlds/cell — `3840` worlds,
   6.0× the base budget — clears both truths on the measured ladder.
   At the observed ~0.6 s/world this is a wall-clock change, not a feasibility
   change.
2. **Re-state the gate.** If the two-truth conjunction is stricter than intended,
   a lean-weighted or q_truth-anchored variant would pass at 64 today. This is a
   registration decision and the executor takes no position on it beyond
   reporting that the binding arm is the low-prior one.
3. **Add the second axis.** the registration NAMES the int_share second axis for a future registration and forbids adopting it here. It is therefore not probed: exercising it requires installing K2d's `int:` weight dispatcher on every reachable k2b instance (RN-K2F-5), a machinery mutation this leg has no licence to make for a knob it may not adopt. Under the planner-side convention that defect #43 bought, that arithmetic is the PLANNER's to run before registering a successor -- it is deterministic and needs no world.

**What was NOT measured.** `q` at level, `κ` at level, the winner form, and the
(r, V)-sufficiency pattern. L-1, L-2, L-3 and L-4 are all NOT EVALUATED. The
level law's exponent remains exactly where K2f left it — unidentified — and
this leg's contribution is to have priced the identification rather than to have
attempted it under-powered.
