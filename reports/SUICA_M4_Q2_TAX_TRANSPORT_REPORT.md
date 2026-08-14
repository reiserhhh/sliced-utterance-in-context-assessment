# SUICA M4-Q2 — is the tax frame-borne? — **TAX_FRAME_BORNE**

**Outcome: TAX_FRAME_BORNE (routing cell 4); modifiers: none.**
TAX_FRAME_BORNE -- the V-response is frame-agreement; the N-line curve is re-typed as the frame channel's V-response; appendix II completes

**D_ref = -0.0022020717726400894 [-0.005350034376011563, 0.0010185625621798886] → NULL** (ε = 0.007413654845687905), against a natural
tax swing **D_nat = 0.1196454983533797 [0.11590855681080722, 0.1232498969832857]** which the M-line law predicted at
0.11801642901308901. 1536 worlds (384 A/B pairs per share).

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_Q_TRANSPORT_LINE_PLAN.md` BEFORE run (commit d030914). Every
number below is generated from artifacts by code (rule 24).

---

## 1. The levels first

RN-Q2-5, pinned in Part 0: a NULL D_ref is largely **confirmatory** given that
P3c already found R_ref near zero — a difference of two near-zero levels is near
zero for an uninteresting reason. So the levels are stated before the
difference.

| share | V | n | R_nat mean | R_nat SEM | R_ref mean | R_ref SEM | \|\|T-nat - T-ref\|\| mean |
|---|---|---|---|---|---|---|---|
| 0.1 | 0.03 | 384 | 0.16306830159907398 | 0.0014179003281448192 | -0.0007786103879736543 | 0.0011820408887000167 | 62.6612044103199 |
| 0.7 | 0.21 | 384 | 0.04342280324569429 | 0.0011174156760681603 | 0.001423461384666435 | 0.0010773169597756112 | 36.158337017254745 |

R_nat falls from 0.16306830159907398 at V = 0.03 to 0.04342280324569429 at V = 0.21 —
the tax, plainly visible. R_ref sits at -0.0007786103879736543 and 0.001423461384666435: **the
frame-refreshed reading has essentially no level to lose at either V**, which is
what makes its difference small.

## 2. The anchor — V-Q2a

The M-line law's prediction is recomputed from two persisted cells on different
legs:

| quantity | value |
|---|---|
| low-V cell | s0.10_p0.60 (share 0.1, phi 0.6, V 0.03, n 192) |
| its source | `results/m4_m1c_r_at_level/cell_means.csv` |
| its mean / SEM | 0.16156034289722412 / 0.0019744651453781504 |
| high-V cell | M2 C2 (share 0.7, phi 0.6, V 0.21, n 192) |
| its source | `results/m4_m2_scoped_seal/decision.json:per_cell.C2` |
| its mean / SEM | 0.04354391388413511 / 0.001616665195874819 |
| **predicted D_nat** | **0.11801642901308901** |
| SEM of the prediction | 0.002551885374750623 |
| planner sanity value (expressly approximate) | 0.117 |
| recomputed minus sanity | 0.0010164290130890014 |
| matches to 3 dp | False |
| does the divergence gate? | False -- rule 30 licenses an expressly-approximate quote; the RECOMPUTED value controls (RN-Q2-6) |
| band rule (pinned) | the anchor band is PINNED as 2*sqrt(2)*sqrt(SEM_pred^2 + SEM_meas^2), matching the programme's V-P3a/C1' convention; the plain 2-SE reading is reported beside it. The prediction's two cells come from DIFFERENT legs on different salts, so the band is distributional by necessity |
| cross-leg note | the two cells come from DIFFERENT legs on different salts (M1c and M2), so the comparison is distributional by necessity |

| quantity | value |
|---|---|
| predicted D_nat | 0.11801642901308901 |
| **measured D_nat** | **0.1196454983533797** |
| measured 95% CI | [0.11590855681080722, 0.1232498969832857] |
| difference | 0.0016290693402906953 |
| pooled SEM | 0.0031258883696546457 |
| z | 0.5211540361150766 |
| pinned band (2*sqrt(2)*pooled SEM) | 0.008841347453659845 |
| **inside the pinned band** | **True** |
| plain 2-SE band (reported) | 0.006251776739309291 |
| inside the 2-SE band | True |
| D_nat POSITIVE | True |
| **V-Q2a PASS** | **True** |

Predicted **0.11801642901308901** by recomputation. The registration's quoted sanity value
is 0.117, expressly approximate with "executor recomputes" — the
recomputation is 0.0010164290130890014 above it and rounds to 0.118 rather than 0.117
(matches to 3 dp: False). Rule 30 licenses an expressly-approximate
quote, so this does **not** gate and the recomputed value controls (RN-Q2-6);
for scale the divergence is about a seventh of the anchor band. Measured
**0.1196454983533797** [0.11590855681080722, 0.1232498969832857]; difference 0.0016290693402906953, z = 0.5211540361150766,
inside the pinned band 0.008841347453659845 (True) and inside the plain
2-SE band 0.006251776739309291 (True). **V-Q2a = True** — the
instrument reproduces the M-line law, so D_ref can be interpreted.

The band was pinned before any measurement (RN-Q2-1): the registration says
"distributional band" without fixing k, and the two source cells come from
different legs on different salts, so the comparison is distributional by
necessity. Both the pinned 2√2 reading and the plain 2-SE reading are reported;
they agree here.

## 3. The result — V-Q2b

| estimand | definition | point | 95% CI | epsilon | classification |
|---|---|---|---|---|---|
| D_nat | R_nat(V=0.03) - R_nat(V=0.21) | 0.1196454983533797 | [0.11590855681080722, 0.1232498969832857] | — | anchor gate: PASS |
| **D_ref** | R_ref(V=0.03) - R_ref(V=0.21) | **-0.0022020717726400894** | [-0.005350034376011563, 0.0010185625621798886] | 0.007413654845687905 | **NULL** |
| V-Q2b sign-first reading | — | — | — | — | NULL |
| readings agree | — | — | — | — | True |

D_ref = **-0.0022020717726400894** [-0.005350034376011563, 0.0010185625621798886] against ε = 0.007413654845687905 → **NULL**. The
sign-first reading agrees (True).

| quantity | value |
|---|---|
| D_ref / D_nat | -0.0184049697058902 |
| 95% CI | [-0.044787633515569504, 0.008345157757188915] |
| CI width | 0.05313279127275842 |
| **label** | **UNBUDGETED -- descriptive only, gates nothing, routes nothing** |
| margin note | the RATIO's band only -- D_nat and D_ref each difference two INDEPENDENT shares, so their own SEs need no covariance term (RN-Q2-3) |

The ratio is quoted **UNBUDGETED** — it gates nothing and routes nothing (the
P3b lesson kept visible), and it is the only place the 1.25 independence margin
touches anything.

## 4. Bands and projection

| quantity | value |
|---|---|
| sd R_nat raw / df-inflated | 0.024427540860045137 / 0.04030293796378275 |
| sd R_ref raw / df-inflated | 0.031131211639470645 / 0.051363307450042625 |
| pooled df / inflation | 6 / 1.6498974741130894 |
| SE(D_nat) at 384 | 0.002908614010315345 |
| SE(D_ref) at 384 | 0.0037068274228439523 |
| **epsilon_D_ref** | **0.007413654845687905** |
| independence margin (#57) | 1.25 |
| margin applied to | the RATIO's band only -- D_nat and D_ref each difference two INDEPENDENT shares, so their own SEs need no covariance term (RN-Q2-3) |

No pilot correlation is consumed (#57). D_nat and D_ref each difference two
**independent** shares, so their SEs need no covariance term; the margin is
applied only to the ratio's band, and stated (RN-Q2-3). The within-pair
R_nat/R_ref correlation is handled by resampling pair indices jointly, never by
estimating a correlation.

| pairs/share | truth | role | SE(D_ref) | fires at 2 SE | bar | PASS |
|---|---|---|---|---|---|---|
| 384 (registered) | D_ref = 0 | false-fire | 0.0037068274228439523 | 0.043 | 0.1 | True |
| 384 (registered) | D_ref = 0.013614431430092793 (partial transport) | power | 0.0037068274228439523 | 0.9485 | 0.8 | True |
| derivation of the partial truth | the Part-0 anchor prediction times P3c's transportable share point 0.115360476028154 | registered sanity | 0.0134 | — | — | — |

False-fire 0.043 at D_ref = 0 (bar 0.1) and power 0.9485 at the partial-
transport truth 0.013614431430092793 (bar 0.8, derived as the anchor prediction times
P3c's transportable share point). Escalation did not fire (False).

## 5. Instrument and C2

| property | value |
|---|---|
| instrument | `scripts/run_suica_m4_p3b_refresh_gradient.py:279` |
| function sha256 | a7618a321752fc502d804745f2e83b7dd75af7e3f8a88868575c3afa632ed9bc |
| P3c persisted function sha256 | a7618a321752fc502d804745f2e83b7dd75af7e3f8a88868575c3afa632ed9bc |
| file sha256 | b06c36bc3ff5a757d73e25c42bd19491d300e117de4b2f1b45085a2f1fe1cd4a |
| **hashes match** | **True** |

Hashes match P3c's persisted values (True).

| check | objects | result |
|---|---|---|
| author objects bit-identical | trait, a_load, loadings | True |
| frame norm delta: slow | frame | [250.23708655061483, 251.4164630870388] |
| frame norm delta: slow_latent | frame | [1226.1131886987466, 1231.2810075007005] |
| frame norm delta: noise | frame | [250.68179181160156, 251.24006792712092] |
| frame norm delta: common | frame | [15.77944446020057, 16.094877939114077] |
| frame norm delta: int | frame | [250.81410154188313, 252.51446727791924] |
| determinism | all objects | True |
| shared basis | loadings | True |
| #60 shared-component check | stated | #60's shared-component check, stated: both scorings use each world's OWN truth panel from k2b's emit_panel and the contrast is between two SHARES, not two reference objects -- nothing is scored against an object it does not contain |
| **C2** | — | **PASS = True** |

C2 = True on 4 fresh probe pairs. The #60 shared-component check
is stated, not merely satisfied (RN-Q2-4): both scorings use each world's **own**
truth panel from k2b's `emit_panel`, and the contrast is between two SHARES, not
two reference objects — so nothing is scored against an object it does not
contain, which was Q1b's failure mode.

## 6. Routing

| # | condition | outcome |
|---|---|---|
| 1 | G0/G1 failure | STOP / INSTRUMENT_DEFECT |
| 2 | projection fails after escalation | NON_PROJECTABLE |
| 3 | V-Q2a not POSITIVE | INSTRUMENT_DEFECT (the anchor is the M-line law) |
| 4 | V-Q2b NULL | **TAX_FRAME_BORNE -- the V-response is frame-agreement; the N-line curve is re-typed as the frame channel's V-response; appendix II completes**  <-- THIS LEG |
| 5 | V-Q2b POSITIVE | TAX_PARTIALLY_TRANSPORTS -- a person-borne tax component exists; quantified descriptively |
| 6 | V-Q2b NEGATIVE | TAX_INVERSION_NAMED -- theory note |
| 7 | any UNDERPOWERED (no higher cell) | UNDERPOWERED |

## 7. Gates

| gate | PASS | detail |
|---|---|---|
| G0q2 | True | instrument hashes vs P3c's persisted; the anchor cells at full precision; P3c's and Q1b's verdicts |
| C2 | True | 4 fresh probe pairs; shared-component check stated (#60) |
| G2q2 | True | rule-29 predicate on BOTH scorings at both shares; bands from variances only with the margin stated |
| G3q2 | True | escalation fired: False |
| V-Q2a | True | D_nat POSITIVE and within the anchor band |

## 8. Sides declared (rule 22)

| clause | statement | prior | sided |
|---|---|---|---|
| G3q2 | power >= 0.8 at the partial-transport truth and false-fire <= 0.1 at 0 | — | one-sided each |
| L-1q2 | TAX_FRAME_BORNE / TAX_PARTIALLY_TRANSPORTS / other | 0.55 / 0.25 / 0.20 | categorical |
| V-Q2a | D_nat POSITIVE and within the anchor band | — | instrument gate |
| V-Q2b | D_ref vs 0, NULL-first | — | two-sided |

## 9. Pinned readings

| note | pinned reading |
|---|---|
| RN-Q2-1 | the anchor band is PINNED as 2*sqrt(2)*sqrt(SEM_pred^2 + SEM_meas^2), matching the programme's V-P3a/C1' convention; the plain 2-SE reading is reported beside it. The prediction's two cells come from DIFFERENT legs on different salts, so the band is distributional by necessity |
| RN-Q2-2 | V-Q2a is an instrument gate: a D_nat that misses the M-line prediction routes INSTRUMENT_DEFECT and is never read as news about the world |
| RN-Q2-3 | no pilot correlation is consumed (#57); D_nat and D_ref difference two INDEPENDENT shares so their variances add with no covariance; the 1.25 margin is applied only to the ratio's band and stated there; the within-pair R_nat/R_ref correlation is handled by joint index resampling, never by estimating a correlation |
| RN-Q2-4 | #60's shared-component check, stated: both scorings use each world's OWN truth panel from k2b's emit_panel and the contrast is between two SHARES, not two reference objects -- nothing is scored against an object it does not contain |
| RN-Q2-5 | a NULL D_ref is largely CONFIRMATORY given P3c's near-zero R_ref levels: a difference of two near-zero levels is near zero for an uninteresting reason. The report states the LEVELS first and reads the difference only alongside them |
| RN-Q2-6 | the registration labels 0.117 a 'planner sanity value, executor recomputes'; the recomputation gives 0.11801642901308901 (0.00102 above, rounding to 0.118). Rule 30 licenses an expressly-approximate quote, so this is NOT a defect and does not gate -- the recomputed value controls and both are recorded |

## 10. Rule events

- **Rule 13:** 0 boundary event(s); bootstrap B = 2000.
- **Rule 25:** the projection gate passed at the registered size.
- **Rule 26:** no bounded winner.
- **Rule 27:** the ratio is explicitly UNBUDGETED and carries the label.
- **Rule 29:** the domain-pinned predicate ran on BOTH scorings at every arm.
- **Rule 30:** every cited constant read from its persisted source; the anchor
  prediction is recomputed rather than quoted.
- **#57:** no pilot correlation consumed; the margin applied only to the ratio.
- **#60:** the shared-component check stated explicitly.

## 11. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine; a CPython 3.12.12 venv was built outside the repo
   from `requirements-lock-main.txt` verbatim and pinned. Resolved BEFORE any
   hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.

## 12. Environment

| component | value |
|---|---|
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| platform | macOS-26.4.1-arm64-arm-64bit |
| python | 3.12.12 |
| python_executable | /private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python |
| scipy | 1.17.1 |

## 13. Timing

| stage | estimate (s) | measured (s) |
|---|---|---|
| part0 | 150 | 0.221 |
| pilot | 60 | 4.707 |
| project | 30 | 0.000 |
| arm s0.1_0_192 | 150 | 116.972 |
| arm s0.1_192_384 | 150 | 113.865 |
| arm s0.7_0_192 | 150 | 113.934 |
| arm s0.7_192_384 | 150 | 113.746 |
| fit | 180 | 0.038 |
| finalize | 60 | 0.000 |

---

*Artifacts: `results/m4_q2_tax_transport/` (gitignored) — `part0.json`,
`pilot.json`, `pilot_field.csv`, `projection.json`, `arms/`, `fit.json`,
`decision.json`, `prose_facts.json`, `report_tables.md`, `run_log.jsonl`.
Harness: `scripts/run_suica_m4_q2_tax_transport.py`.*
