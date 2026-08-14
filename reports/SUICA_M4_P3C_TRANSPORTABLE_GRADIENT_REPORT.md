# SUICA M4-P3c — the transportable gradient, by differences — **UNDERPOWERED**

**Outcome: UNDERPOWERED (routing cell 8); modifiers: none.**
UNDERPOWERED (levels and bands reported)

**V-A (frame-owned component) D_grad = 0.00852887414363202 [0.005277986571389943, 0.011952276850539912] → POSITIVE.
V-B (transportable component) range_ref = 0.0011121987595310255 [-0.001020386706397168, 0.003228730521677211] →
UNDERPOWERED.** Against range_nat = 0.009641072903163045 [0.00715774671522028, 0.01223467530439654]. 3456 worlds
(768 A/B pairs at each endpoint + 192 at the shape reading).

**Read plainly: the frame-owned component is real and large, and the
transportable component cannot be certified either way.** D_grad is
0.00852887414363202 — most of range_nat — with a CI comfortably clear of zero. range_ref
is 0.0011121987595310255, straddling zero, and its CI is *slightly* too wide to sit
inside the ±0.001993500543087015 equivalence band, so it classifies UNDERPOWERED rather
than NULL. The registered routing sends any UNDERPOWERED verdict to cell 8, and
that is where this leg lands — one notch short of GRADIENT_FULLY_FRAME, which
would have required V-B to be certifiable as NULL.

**The levels say more than the verdict does.** R_refresh is essentially zero at
every φ — -0.0009178005907745429, -0.0014144445255356564, 0.00019439816875648275 — against an R_nat of
0.12141191457796047 … 0.1310529874811235. The gauge scored against a *different frame's*
truth agrees with it barely at all. That is the substance; the verdict is
UNDERPOWERED only because certifying "indistinguishable from zero" is a
stronger demand than observing "near zero".

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md` BEFORE run (commit 11f42d6).
Every number below is generated from artifacts by code (rule 24).

---

## 1. The instrument, imported

| property | value |
|---|---|
| imported from | `scripts/run_suica_m4_p3b_refresh_gradient.py:279` |
| signature | `build_split_world(author_seed: 'int', frame_seed: 'int', phi_slow: 'float') -> 'dict[str, np.ndarray]'` |
| function sha256 | a7618a321752fc502d804745f2e83b7dd75af7e3f8a88868575c3afa632ed9bc |
| file sha256 | b06c36bc3ff5a757d73e25c42bd19491d300e117de4b2f1b45085a2f1fe1cd4a |
| file bytes | 92033 |
| P3b provenance entries behind it | 18 |
| ultimate source span | run_suica_m4_k2b_t4_branch.py:321-349 |
| k2b edited | False |
| suica_core edited | False |
| why imported, not re-extracted | build_split_world is IMPORTED from P3b by file path with the file's and the function's sha256 recorded, and P3b's C2 battery re-run on fresh probe pairs; re-extracting would create a second copy to drift |

P3b's certified `build_split_world` is **imported by file**, not re-extracted —
one certified builder in the programme, with nothing to drift. Its C2 battery is
re-run here on 4 **fresh** probe pairs:

| check | objects | result |
|---|---|---|
| C2a author identical | trait, a_load, loadings | True |
| C2a frame differs | slow, slow_latent, noise, common, int | True |
| C2a norm delta: slow | frame | [250.75964053278514, 251.1014000990286] |
| C2a norm delta: slow_latent | frame | [1228.6504177280797, 1230.5535422818334] |
| C2a norm delta: noise | frame | [250.855111144242, 250.99681302686716] |
| C2a norm delta: common | frame | [15.456355013034589, 15.926464179341583] |
| C2a norm delta: int | frame | [250.07083342882402, 252.17926376965457] |
| C2b determinism | 8 objects | True |
| C2c shared basis | loadings | True |
| **C2 (fresh probe pairs: 4)** | — | **PASS = True** |

C2 = True: author objects bit-identical, every frame object differing
(`common` by a norm delta in [15.456355013034589, 15.926464179341583]), determinism
holding, basis shared. k2b and `suica_core/` untouched.

## 2. G0 — the citations, and the sign convention

| clause | expected | found | OK |
|---|---|---|---|
| M1c range (phi .98 - phi .05) | 0.010391443071199338 | 0.010391443071199338 | True |
| P3b verdict | NON_PROJECTABLE | NON_PROJECTABLE | True |
| P3b instrument certified | True | True | True |
| P3b SE(range_ref) at 192 | — | 0.0047600770920988265 | — |
| P3b sigma R_nat | — | 0.032930580570026624 | — |
| P3b sigma R_refresh | — | 0.04663904004781301 | — |
| ladder r at phi=0.05 | 0.785015540293945 | 0.785015540293945 | True |
| ladder r at phi=0.3 | 0.7761302864207245 | 0.7761302864207245 | True |
| ladder r at phi=0.6 | 0.7558507450373838 | 0.7558507450373838 | True |
| ladder r at phi=0.85 | 0.7168731389294273 | 0.7168731389294273 | True |
| ladder r at phi=0.98 | 0.6763691758553391 | 0.6763691758553391 | True |

**The side-signing reverses from P3b, deliberately** (RN-P3C-2). P3b reported
range_nat = R(.05) − R(.98) = −0.0104; this registration defines
range = value(.98) − value(.05), so range_nat is **+0.010391443071199338** — the same
quantity with the opposite sign, and the sign the registration's own truths use.
Every range in this leg is HI minus LO. Stated because a silent sign flip
between sibling legs is exactly what survives review and then poisons a
comparison.

## 3. Bands and the correlation that pays for this design

| quantity | value |
|---|---|
| sd R_nat (raw / df-inflated) | 0.025745674905011007 / 0.04247772399511441 |
| sd R_refresh (raw / df-inflated) | 0.011838454714040339 / 0.019532236530097353 |
| pooled df / inflation | 6 / 1.6498974741130894 |
| **within-phi correlation of R_nat and R_refresh** | **0.761471882823515** |
| SE(range_nat) at 768 | 0.002167682275475159 |
| SE(range_ref) | 0.0009967502715435075 |
| **SE(D_grad), joint** | **0.0015497830611512617** |
| SE(D_grad) if independent | 0.002385866205643397 |
| correlation benefit factor | 0.6495683024829683 |
| **epsilon_D (V-A NULL band)** | **0.0030995661223025234** |
| **epsilon_r (V-B NULL band)** | **0.001993500543087015** |
| band definition | eps = 2 * SE of the estimand at the decided pairs/phi, from pilot noise df-inflated on the chi2(0.10) convention; a NULL verdict is a CI lying inside +/- eps |

R_nat and R_refresh are computed from the **same** A-world — one gauge pass,
two truth panels — so they are correlated within a pair (ρ = 0.761471882823515). The
bootstrap is therefore JOINT (RN-P3C-3): one resample of pair indices drives
both ranges, so D_grad inherits the cancellation. SE(D_grad) = 0.0015497830611512617 against
0.002385866205643397 had they been independent — a factor of 0.6495683024829683. **This is
what makes the difference estimand feasible where P3b's ratio was not.**

ε_D = 0.0030995661223025234 and ε_r = 0.001993500543087015, computed from pilot noise df-inflated
(df 6, factor 1.6498974741130894) and written before the arms.

## 4. The projection

| pairs/phi | truth | detected | power at 2 SE | bar | null quantity | false fire | bar | PASS |
|---|---|---|---|---|---|---|---|---|
| 768 (registered) | FULLY_FRAME | D_grad | 1.0 | 0.8 | range_ref | 0.05 | 0.1 | True |
| 768 (registered) | TRANSPORTS | range_ref | 1.0 | 0.8 | D_grad | 0.0445 | 0.1 | True |

At the registered 768 pairs/φ: FULLY_FRAME detects D_grad with power 1.0
(bar 0.8) while range_ref false-fires at 0.05 (bar 0.1); TRANSPORTS detects
range_ref with power 1.0 while D_grad false-fires at 0.0445. All four
clear. Escalation did not fire (False).

## 5. C1′ — the anchor

| phi | role | P3c R_nat | P3c SEM | M1c mean | M1c SEM | difference | tolerance | inside | pooled z |
|---|---|---|---|---|---|---|---|---|---|
| 0.05 | endpoint | 0.12141191457796047 | 0.0009692408241353337 | 0.12162744485545209 | 0.0017778785791358425 | -0.00021553027749161846 | 0.005028599997733033 | True | -0.10643918235484917 |
| 0.6 | shape reading | 0.127054822864402 | 0.0019654438197426417 | 0.12714790436588774 | 0.0017053615065044834 | -9.308150148573668e-05 | 0.004823490742495307 | True | -0.035770884964947285 |
| 0.98 | endpoint | 0.1310529874811235 | 0.0009013957608274527 | 0.13201888792665142 | 0.0018133362157806163 | -0.0009659004455279119 | 0.005128889338998506 | True | -0.4769833641131134 |
| **C1'** | — | — | — | — | — | — | — | **3/3** | PASS = True |

3/3 levels inside 2·√2·SEM of M1c's row (largest |pooled z| =
0.4769833641131134); C1′ = True. The extracted two-stream instrument reproduces
M1c's measured levels, so a failure downstream would have been a finding, not a
plumbing artefact. range_nat also co-measures M1c's range to
-0.0007503701680362934.

## 6. The result

| phi | role | r_pred | n | R_nat mean | R_nat SEM | R_refresh mean | R_refresh SEM | R_deframe mean | R_deframe SEM | within-pair corr |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | endpoint | 0.785015540293945 | 768 | 0.12141191457796047 | 0.0009692408241353337 | -0.0009178005907745429 | 0.0007756226258312586 | -0.0006611068355035473 | 0.0007884988374526054 | 0.007142710928294203 |
| 0.6 | shape reading | 0.7558507450373838 | 192 | 0.127054822864402 | 0.0019654438197426417 | -0.0014144445255356564 | 0.0015808013006755244 | 0.0006918693173260006 | 0.001508768943295481 | -0.0027490284889659074 |
| 0.98 | endpoint | 0.6763691758553391 | 768 | 0.1310529874811235 | 0.0009013957608274527 | 0.00019439816875648275 | 0.0008406974743652825 | -0.0005750845212524437 | 0.0007569982629817279 | 0.0036923299323797887 |

| estimand | definition | point | 95% CI | epsilon | classification |
|---|---|---|---|---|---|
| range_nat | R_nat(.98) - R_nat(.05) | 0.009641072903163045 | [0.00715774671522028, 0.01223467530439654] | — | — (not a verdict) |
| **range_ref (V-B)** | R_refresh(.98) - R_refresh(.05) | **0.0011121987595310255** | [-0.001020386706397168, 0.003228730521677211] | 0.001993500543087015 | **UNDERPOWERED** |
| **D_grad (V-A)** | range_nat - range_ref | **0.00852887414363202** | [0.005277986571389943, 0.011952276850539912] | 0.0030995661223025234 | **POSITIVE** |
| M1c's realized range | the anchor | 0.010391443071199338 | — | — | — |
| range_nat - M1c's | co-measurement check | -0.0007503701680362934 | — | — | — |

| verdict | quantity | NULL-first (routes) | sign-first | agree |
|---|---|---|---|---|
| V-A | D_grad | POSITIVE | POSITIVE | True |
| V-B | range_ref | UNDERPOWERED | UNDERPOWERED | True |

Both verdicts read the same under the NULL-first order that routes and under the
sign-first order (True / True).

### 6.1 The joint bootstrap, and what it bought

| quantity | value |
|---|---|
| **bootstrap correlation, range_nat vs range_ref** | **0.017673408969719043** |
| realized SE(D_grad) from the joint bootstrap | 0.0017252853220331757 |
| SE(D_grad) had they been independent | 0.0017405070975400247 |
| why joint | the bootstrap resamples PAIR INDICES once per replicate and recomputes both ranges from the same indices, because R_nat and R_refresh share the A-world; treating them as independent would inflate SE(D_grad) by up to sqrt(2). The realized correlation is reported |
| bootstrap B | 2000 |

Realized bootstrap correlation between range_nat and range_ref: **0.017673408969719043**.
Realized SE(D_grad) 0.0017252853220331757 against 0.0017405070975400247 under an
independence assumption.

### 6.2 The fraction — quoted, and labelled

| quantity | value |
|---|---|
| range_ref / range_nat | 0.115360476028154 |
| 95% CI | [-0.10768346212929444, 0.3468040491435675] |
| CI width | 0.4544875112728619 |
| **label** | **UNBUDGETED -- descriptive only, gates nothing, routes nothing** |
| why it is shown | range_ref/range_nat is the ratio that failed P3b's budget; quoted here as a point with an honest CI, labelled UNBUDGETED, gating and routing nothing |

range_ref/range_nat = 0.115360476028154 [-0.10768346212929444, 0.3468040491435675], width 0.4544875112728619. **UNBUDGETED.**
This is the P3b ratio that failed its budget; it is shown because a reader will
compute it anyway, and showing its width is the P3b lesson made visible. It
gates nothing and routes nothing.

### 6.3 The bands, and the pilot's luck

| quantity | pilot (Part 0, routes) | realized (reported) |
|---|---|---|
| within-pair correlation rho | 0.761471882823515 | 0.0054175204303369955 |
| sd R_refresh | 0.019532236530097353 | 0.022396388278681817 |
| SE(range_ref) | 0.0009967502715435075 | 0.0011438368332526896 |
| SE(D_grad) | 0.0015497830611512617 | 0.0017252853220331757 |
| epsilon_D | 0.0030995661223025234 | 0.0034505706440663515 |
| epsilon_r | 0.001993500543087015 | 0.002287673666505379 |
| V-A | POSITIVE | POSITIVE |
| V-B | UNDERPOWERED | UNDERPOWERED |
| **verdicts robust to the band source** | — | **True** |

The Part-0 bands route, as registered. They are recomputed here from the
realized arms because the pilot is only 4 pairs per endpoint, and an n = 4
correlation carries a standard error of roughly 0.5 (RN-P3C-9). It shows: the
pilot's ρ = 0.761 against a realized 0.0054175204303369955, a miss of 0.756054362393178. The
projection used the optimistic ρ and so understated SE(D_grad) — which did not
matter, because D_grad is far from its band either way.

**Both verdicts are unchanged under the realized-noise bands (True):**
V-A POSITIVE and V-B UNDERPOWERED under ε_D = 0.0030995661223025234 / 0.0034505706440663515 and
ε_r = 0.001993500543087015 / 0.002287673666505379. The pilot's sampling luck is visible and
audited, and it changed nothing.

## 7. Routing

| # | condition | outcome |
|---|---|---|
| 1 | G0 / C2 battery / citation failure | STOP / INSTRUMENT_DEFECT |
| 2 | projection fails after escalation | NON_PROJECTABLE |
| 3 | C1' anchor fails | INSTRUMENT_DEFECT (never a world finding) |
| 4 | V-A POSITIVE and V-B NULL | GRADIENT_FULLY_FRAME -- the natural phi-gradient is frame-owned; the M-line law stands as a law of the statistic; the mechanism section re-types (the r-channel reads frame-agreement) |
| 5 | V-A POSITIVE and V-B POSITIVE | GRADIENT_MIXED -- both components real; the split is quoted descriptively |
| 6 | V-A NULL and V-B POSITIVE | GRADIENT_TRANSPORTS -- the reading crosses frames; the scaffold-gradient strengthens |
| 7 | V-B NEGATIVE | INVERSION_NAMED -- refreshment reverses the gradient; new phenomenon, theory note |
| 8 | any UNDERPOWERED among V-A/V-B (no higher cell fires) | **UNDERPOWERED (levels and bands reported)**  <-- THIS LEG |
| 9 | V-A NEGATIVE (and V-B not NEGATIVE) | FRAME_COMPONENT_NEGATIVE -- refreshed gradient exceeds natural; named, theory note |

## 8. Gates

| gate | PASS | detail |
|---|---|---|
| G0 | True | M1c's row and range, P3b's persisted SEs and certification, the ladder r values -- all verified |
| C2 | True | re-run on 4 FRESH probe pairs: author objects bit-identical, every frame object differs, determinism, shared basis |
| C3 | True | rule-29 predicate on BOTH scorings at both endpoints; bands computed df-inflated before the arms |
| G3p3c | True | both truths discriminated at 2*SE; escalation fired: False |
| C1' | True | 3/3 levels within 2.8284271247461903*SEM of M1c's row |

## 9. Sides declared (rule 22)

| clause | statement | prior | sided |
|---|---|---|---|
| C1' | R_nat levels within 2.8284271247461903*SEM of M1c's row | — | two-sided |
| G3p3c | both powers >= 0.8 at 2*SE and both null false-fires <= 0.1 | — | one-sided each |
| L-1p3c | FULLY_FRAME / MIXED / TRANSPORTS / INVERSION / underpowered | 0.50 / 0.25 / 0.10 / 0.05 / 0.10 | categorical |
| V-A | D_grad vs 0, NULL-first | — | two-sided |
| V-B | range_ref vs 0, NULL-first | — | two-sided |

## 10. Pinned readings

| note | pinned reading |
|---|---|
| RN-P3C-1 | build_split_world is IMPORTED from P3b by file path with the file's and the function's sha256 recorded, and P3b's C2 battery re-run on fresh probe pairs; re-extracting would create a second copy to drift |
| RN-P3C-2 | the side-signing REVERSES from P3b deliberately: this registration defines range = value(.98) - value(.05), so range_nat is +0.010391443071199338 and matches the registration's own truths; stated because a silent sign flip between sibling legs poisons comparisons |
| RN-P3C-3 | the bootstrap resamples PAIR INDICES once per replicate and recomputes both ranges from the same indices, because R_nat and R_refresh share the A-world; treating them as independent would inflate SE(D_grad) by up to sqrt(2). The realized correlation is reported |
| RN-P3C-4 | the projection simulates both registered truths from the pilot's realized (sd_nat, sd_ref, rho_within); PASS is the conjunction of both powers >= 0.8 at 2*SE and both null false-fires <= 0.1 |
| RN-P3C-5 | range_ref/range_nat is the ratio that failed P3b's budget; quoted here as a point with an honest CI, labelled UNBUDGETED, gating and routing nothing |
| RN-P3C-6 | eps_D and eps_r come from the pilot's realized noise, df-inflated on the chi2(0.10) convention at the DECIDED pairs/phi, written before the arms; NULL is tested first (#55) |
| RN-P3C-7 | the phi = 0.60 arm enters C1' and the shape table and NO estimand -- the three estimands are endpoint differences by registration |
| RN-P3C-8 | R_nat, R_refresh and R_deframe at a pair index share one corpus string, so label noise cannot enter a within-pair contrast; across phi the tag differs, which is why C1' is distributional |

## 11. Rule events

- **Rule 13:** 0 boundary event(s); bootstrap B = 2000.
- **Rule 25:** the projection gate passed at the registered size; no escalation.
  Its correlation input was badly estimated by the 4-pair pilot (§6.3) — a
  power calculation, not a verdict, and the verdicts are robust to it.
- **Rule 26:** no bounded winner.
- **Rule 27:** the only budgeted quantities are the verdict CIs against their
  Part-0 bands; the fraction is explicitly UNBUDGETED and carries the label.
- **Rule 29:** the domain-pinned predicate ran on BOTH scorings at every arm.
- **Rule 30:** every cited constant read from its persisted source; the
  instrument carries file, line and two sha256s.

## 12. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine; a CPython 3.12.12 venv was built outside the repo
   from `requirements-lock-main.txt` verbatim and pinned. Resolved BEFORE any
   hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.

## 13. Environment

| component | value |
|---|---|
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| platform | macOS-26.4.1-arm64-arm-64bit |
| python | 3.12.12 |
| python_executable | /private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python |
| scipy | 1.17.1 |

## 14. Timing

| stage | estimate (s) | measured (s) |
|---|---|---|
| part0 | 180 | 0.239 |
| pilot | 60 | 8.267 |
| project | 30 | 0.000 |
| arm p0.05_0_384 | 350 | 387.621 |
| arm p0.05_384_768 | 350 | 382.150 |
| arm p0.98_0_384 | 350 | 381.528 |
| arm p0.98_384_768 | 350 | 384.403 |
| arm p0.6_0_192 | 350 | 191.794 |
| fit | 240 | 0.090 |
| finalize | 60 | 0.000 |

---

*Artifacts: `results/m4_p3c_transportable_gradient/` (gitignored) —
`part0.json`, `pilot.json`, `pilot_field.csv`, `projection.json`, `arms/`,
`fit.json`, `decision.json`, `prose_facts.json`, `report_tables.md`,
`run_log.jsonl`. Harness:
`scripts/run_suica_m4_p3c_transportable_gradient.py`.*
