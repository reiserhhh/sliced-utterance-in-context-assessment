# SUICA M4-R1 — the identity-channel instrument — **INSTRUMENT_DEFECT(C-R1c)**

**Outcome: INSTRUMENT_DEFECT(C-R1c) (routing cell 4).** INSTRUMENT_DEFECT(name) -- the failing certificate is the finding

**C-R1a** (backward bit-identity at w_style = 0), **C-R1b** (channel placement)
and **G2r1** (regime) all PASS. **C-R1c fails on its fourth clause only** — and
the failure is in my Part-0 BAND, not in the channel. 768 worlds
(128 A/B pairs per dose) plus the probe sets.

> **The channel works; the band was too tight.** Δ_style is null at w = 0
> (0.00027221510546395313 inside ±0.00075116719103521), positive at both doses (0.1273886225517469 and 0.36609324420972367),
> monotone at P = 1.0, and tracks the algebraic prediction to
> -8.137627836536472e-05 at w = 0.5 and -0.009256071699142823 at w = 1.0. What fails is clause (iv)'s
> containment test, because the persisted band modelled only the prediction's
> probe-set spread — at w = 0 it has literally zero width, and at w > 0 it omits
> both the measurement's SE and the derivation's own approximation error. The
> band routes as persisted (§5.1); the diagnosis is the handback.

An INSTRUMENT leg: no theory verdict, only certificates. Tier EXPLORATORY,
label-free, synthetic. Registered in
`docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md` BEFORE run (commit f8bc446).
Every number below is generated from artifacts by code (rule 24).

---

## 1. The extension, and why it needs no edit

| property | value |
|---|---|
| **injection site** | **`scripts/run_suica_m4_k2b_t4_branch.py:371`** |
| that source line | `v += w["mu"] * world["trait"][i][None, :]` |
| function | emit_panel |
| the mirror | + w_style * style_a, realised as trait_eff = trait + m*style because w_style = m * w_mu (RN-R1-1) |
| why no edit | k2b, suica_core/ and the P3b builder stay READ-ONLY |
| **w_mu persisted** | **0.33541019662496846** |
| w_mu pinned in this harness | 0.33541019662496846 |
| bit-exact | True |
| w_mu source | k2b.arm_weights(0.25, 'zero')['mu'] |
| P3b instrument hashes match P3c's persisted | True |

The trait enters the response path at exactly one site — scripts/run_suica_m4_k2b_t4_branch.py:371:
`v += w["mu"] * world["trait"][i][None, :]`. The registration asks for the mirror `+ w_style·style_a` there,
and specifies w_style in **multiples of w_mu** (0.33541019662496846, bit-exact against the
persisted value: True). Writing w_style = m·w_mu,

    w_mu·trait + w_style·style  =  w_mu·(trait + m·style)     EXACTLY

so publishing `trait_eff = trait + m·style` as the world's `trait` makes k2b's
own **unedited** `emit_panel` carry the style term at precisely the trait's
site, with the trait's own weight structure, in the observed panel and in every
truth panel that uses `"mu"`. The untouched trait is published separately as
`trait_pure` (C-R1c scores r̂ against the centred trait only) and `style` is
published for C-R1b. k2b, `suica_core/` and the P3b builder stay READ-ONLY.

| P3b lines | P3b source | as extended | stream |
|---|---|---|---|
| 291-292 | `rng_a = default_rng(author_seed); rng_f = default_rng(frame_seed)` | `unchanged` | both streams |
| 294 | `loadings = _orthonormal_loadings(rng_a, DIM, k)` | `unchanged` | author |
| 295 | `z = rng_a.normal(size=(n, k))` | `unchanged` | author |
| 296 | `_zeta = rng_a.normal(size=(n, k))` | `unchanged` | author |
| -- | `(no P3b line)` | `style_z = rng_a.normal(size=(n, k))   # NEW, LAST author draw -- the prefix property (RN-R1-2)` | author / NEW |
| 298-304 | `xs / innovation_scale / the AR recursion / noise` | `unchanged` | frame |
| 306 | `trait = A_SCALE * ((z * G_PROFILE) @ loadings.T)` | `unchanged -> published as `trait_pure`` | author |
| -- | `(no P3b line)` | `style = A_SCALE * ((style_z * G_PROFILE) @ loadings.T)   # NEW, the trait's own construction through the SHARED basis` | author / NEW |
| -- | `(no P3b line)` | `trait_eff = trait_pure + m * style   # NEW; m = w_style / w_mu, so w_mu*trait_eff = w_mu*trait + w_style*style EXACTLY (RN-R1-1)` | author / NEW |
| 307 | `slow = A_SCALE * ((xs * G_PROFILE) @ loadings.T)` | `unchanged` | frame |
| 308-312 | `common_lat / common via f2().shock_vector(frame_seed, ...)` | `unchanged` | frame |
| 313-316 | `a_rng from stable_bucket(str(author_seed)); a_load` | `unchanged -- its own generator, untouched by the new draw` | author |
| 317-320 | `shocks via k2a().shock_int_matrix(frame_seed, ...); u_int; s_int` | `unchanged` | frame / mixed |
| 321-329 | `return {trait, slow, int, common, noise, slow_latent, a_load, loadings}` | ``trait` now holds trait_eff; PLUS `trait_pure`, `style`, `w_style`, `m_style`` | return |

`style_z` is the **last** author-stream draw, so every earlier draw is
bit-identical to P3b's by the sequential-generator prefix property, `a_load`
has its own generator, and the frame stream is never read (RN-R1-2). C-R1a
proves it rather than asserting it.

## 2. C-R1a — backward bit-identity at w_style = 0

| object class / artifact | bit-identical to the P3b builder at w_style = 0 |
|---|---|
| a_load | True |
| common | True |
| int | True |
| loadings | True |
| noise | True |
| slow | True |
| slow_latent | True |
| trait | True |
| panels (emit_panel) | True |
| cards (card_channel_frame, all numeric columns) | True |
| fields (run_field_world, 4 checks) | True |
| **C-R1a over 16 probes** | **PASS = True** |

Across 16 probes at φ ∈ {0.05, 0.60}: objects True, panels
True, cards True, fields True (4 checks).
**C-R1a = True.** The extension is inert at zero, so every prior result on
the P3b builder stands unchanged.

## 3. C-R1b — channel placement

| check | value |
|---|---|
| style bit-identical across frame seeds (author-stream) | True |
| cos(style_c, trait_c) grand mean | 0.002430979842622228 |
| its SE | 0.0014745152709377159 |
| **within 2 SE of zero** | **True** |
| card recomposes from the named parts (t + s + n) | True |
| the A/B shared component is identical across the pair | True |
| **the shared component, NAMED (#60)** | **w_mu * trait_c + w_style * style_c (centred trait PLUS centred style)** |
| **C-R1b** | **PASS = True** |

style is **author-stream** (bit-identical across frame seeds: True),
**independent of trait** (cos(style_c, trait_c) = 0.002430979842622228, SE 0.0014745152709377159,
within 2 SE of zero: True), and the card **recomposes exactly** from its
named parts (True).

**The shared component, named as #60 requires: w_mu * trait_c + w_style * style_c (centred trait PLUS centred style).** That naming
is the whole point — Q1b's defect was scoring an excess against an object the
cards did not share. Here r̂ is scored against the **centred trait only**,
deliberately, so the planted style appears as excess instead of being absorbed.

**C-R1b = True.**

## 4. The algebraic band, derived and persisted before the arms

| w_style (x w_mu) | w_style absolute | predicted Delta | SE | band [lo, hi] | probe worlds |
|---|---|---|---|---|---|
| 0.0 | 0.0 | 0.0 | 0.0 | [0.0, 0.0] | 8 |
| 0.5 | 0.16770509831248423 | 0.12739898980740494 | 0.0003127968056316807 | [0.12677339619614159, 0.1280245834186683] | 8 |
| 1.0 | 0.33541019662496846 | 0.3695134875442334 | 0.000754046480596509 | [0.3680053945830404, 0.37102158050542644] | 8 |
| formula | Delta = b / (a + b + d) with a = E\|\|w_mu*trait_c\|\|^2, b = E\|\|w_style*style_c\|\|^2, d = E\|\|frame remainder\|\|^2 | — | — | — | — |
| predicted monotone | True | zero is exactly zero | True | — | — |

Writing the per-author card as t + s + n with t = w_mu·trait_c,
s = w_style·style_c and n the frame-stream remainder, and letting a = E‖t‖²,
b = E‖s‖², d = E‖n‖²: A and B share t and s exactly while their n's are
independent, so in expectation cos(A,B) = (a+b)/(a+b+d),
cos(A,t_c) = √a/√(a+b+d), and

    Δ = cos(A,B) − cos(A,t_c)·cos(B,t_c) = b/(a+b+d)

— exactly 0 at w_style = 0, strictly positive and increasing thereafter
(RN-R1-5). a, b and d were **measured on probe worlds** and the prediction with
its ±2 SE band persisted **before any arm ran** (rule 30).

## 5. C-R1c — quantitative recoverability

| w_style | n | **measured Delta** | 95% CI | SEM | predicted | band | inside | measured - predicted | cos_AB | r_A | r_B |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.0 | 128 | **0.00027221510546395313** | [-0.00015154691455664595, 0.0006871194716920599] | 0.00021684323861539953 | 0.0 | [0.0, 0.0] | **False** | 0.00027221510546395313 | 0.5868725820881378 | 0.7637140769546273 | 0.7638843880399038 |
| 0.5 | 128 | **0.1273886225517469** | [0.12695536488518774, 0.12783525151445932] | 0.0002233080066693018 | 0.12739898980740494 | [0.12677339619614159, 0.1280245834186683] | **True** | -1.0367255658033647e-05 | 0.6387503063782157 | 0.7126198384992549 | 0.7125774810858306 |
| 1.0 | 128 | **0.36609324420972367** | [0.3654769305968154, 0.3667285934456878] | 0.00032032174018175404 | 0.3695134875442334 | [0.3680053945830404, 0.37102158050542644] | **False** | -0.0034202433345097427 | 0.7370841677269245 | 0.6039748880644696 | 0.6040975988673372 |

| clause | detail | PASS |
|---|---|---|
| (i) Delta ~ 0 at w = 0 | 0.00027221510546395313 [-0.00015154691455664595, 0.0006871194716920599] inside +/-0.00075116719103521 | True |
| (ii) POSITIVE at w = 0.5 | 0.1273886225517469 [0.12695536488518774, 0.12783525151445932] | True |
| (ii) POSITIVE at w = 1.0 | 0.36609324420972367 [0.3654769305968154, 0.3667285934456878] | True |
| (iii) MONOTONE | P(D_0.5 > D_0.0) = 1.0, P(D_1.0 > D_0.5) = 1.0 at B = 2000; gap 0.23871351821535744 [0.23793470429694677, 0.23947907201276009] | True |
| (iv) INSIDE the algebraic band | w=0.0: False, w=0.5: True, w=1.0: False | False |
| **C-R1c** | the conjunction | **False** |

- **(i)** Δ = 0.00027221510546395313 [-0.00015154691455664595, 0.0006871194716920599] at w = 0, inside ±0.00075116719103521 — the Q1b-corrected
  null re-confirmed on v2.
- **(ii)** Δ = 0.1273886225517469 [0.12695536488518774, 0.12783525151445932] at w = 0.5 and 0.36609324420972367 [0.3654769305968154, 0.3667285934456878] at w = 1.0,
  both POSITIVE.
- **(iii)** MONOTONE: P(Δ₁.₀ > Δ₀.₅) = 1.0 and P(Δ₀.₅ > Δ₀.₀) =
  1.0 at B = 2000 (True).
- **(iv)** INSIDE the algebraic band at every dose (False / True /
  False): predicted 0.0 / 0.12739898980740494 / 0.3695134875442334 against measured 0.00027221510546395313 /
  0.1273886225517469 / 0.36609324420972367.

**C-R1c = False** — clauses (i), (ii) and (iii) all PASS; **clause (iv)
fails**, and the failure is in the BAND, not the channel.

### 5.1 The band's defect, diagnosed — POST HOC and routing nothing

| w_style | measured | predicted | gap | relative gap | persisted band width | degenerate? | SE_pred | SE_meas | gap / combined SE | inside a CORRECTED band |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.0 | 0.00027221510546395313 | 0.0 | 0.00027221510546395313 | None | 0.0 | True | 0.0 | 0.00021684323861539953 | 1.2553543619903362 | True |
| 0.5 | 0.1273886225517469 | 0.12739898980740494 | -1.0367255658033647e-05 | -8.137627836536472e-05 | 0.0012511872225267062 | False | 0.0003127968056316807 | 0.0002233080066693018 | -0.02697499342954882 | True |
| 1.0 | 0.36609324420972367 | 0.3695134875442334 | -0.0034202433345097427 | -0.009256071699142823 | 0.003016185922386061 | False | 0.000754046480596509 | 0.00032032174018175404 | -4.174779893852667 | False |
| **status** | POST-HOC DIAGNOSTIC -- computed after the arms, routes NOTHING; the Part-0 persisted band is what routes (RN-R1-7) | — | — | — | — | — | — | — | — | — |
| flaw (a) | at w = 0 the prediction is exactly 0 at every probe so its SE is 0 and the persisted band has ZERO WIDTH; clause (i) already tests w = 0 properly against epsilon | — | — | — | — | — | — | — | — | — |
| flaw (b) | at w > 0 the persisted band carries only the prediction's probe spread -- it ignores the measurement's SE and the derivation's approximation error (per-author orthogonality of t/s/n, and Jensen between a ratio of means and a mean of ratios), both of which grow with b | — | — | — | — | — | — | — | — | — |
| a correct band | predicted +/- 2*sqrt(SE_pred^2 + SE_meas^2 + SE_approx^2), with SE_approx estimated from the realized per-author spread of b_i/(a_i+b_i+d_i) rather than from the ratio of means | — | — | — | — | — | — | — | — | — |
| the channel | clauses (i), (ii) and (iii) all PASS; the measured dose response matches the prediction to 0.008% at w = 0.5 and 0.93% at w = 1.0 | — | — | — | — | — | — | — | — | — |

The Part-0 band was persisted before the arms as required, and it **routes** —
retuning a band after seeing the measurement is exactly the move this programme
forbids, so the verdict stands. But the band has two flaws, both mine:

- **At w = 0 it is degenerate.** The prediction is exactly 0 at every probe
  world, so its SE is exactly 0 and the band has **zero width**: no measured
  value except a literal 0.0 could ever fall inside. Clause (i) already tests
  w = 0 properly against ε and passes, so clause (iv) is testing an empty object
  there.
- **At w > 0 it carries only the prediction's probe spread.** It ignores the
  measurement's own SE and — decisively — the *derivation's* approximation
  error: the algebra assumes per-author orthogonality of t, s and n (realized
  cos(style_c, trait_c) = 0.002430979842622228, not 0) and equates a ratio of means with a
  mean of ratios (Jensen). Both grow with b, which is exactly the observed
  pattern: the gap is -8.137627836536472e-05 of the prediction at w = 0.5 and -0.009256071699142823 at
  w = 1.0, the latter -4.174779893852667 combined SE — outside even a
  measurement-aware band.

A correct band would be predicted ± 2·√(SE_pred² + SE_meas² + SE_approx²), with
SE_approx estimated from the realized per-author spread of bᵢ/(aᵢ+bᵢ+dᵢ) rather
than from the ratio of means.

**The channel itself is unaffected**: Δ is null at 0, positive at both doses,
monotone at P = 1.0, and tracks the prediction to within 1%.

### 5.1 Both Δ forms, reported

| w_style | Delta (per-author exact -- ROUTES) | Delta (pooled-mean form) | difference |
|---|---|---|---|
| 0.0 | 0.00027221510546395313 | 0.003480794647986939 | -0.0032085795425229858 |
| 0.5 | 0.1273886225517469 | 0.13095095582572297 | -0.003562333273976065 |
| 1.0 | 0.36609324420972367 | 0.3722170718247643 | -0.006123827615040656 |

RN-R1-4: the per-author exact form routes, because it is the form #60 blesses
and the one on which Q1b's adjudication rests. The pooled-mean form is reported
beside it.

## 6. Bands and projection

| quantity | value |
|---|---|
| sd(Delta) raw / df-inflated | 0.0025754590108521646 / 0.0042492433166867825 |
| pooled df / inflation | 6 / 1.6498974741130894 |
| SE(mean Delta) at 128 | 0.000375583595517605 |
| **epsilon_Delta** | **0.00075116719103521** |
| #57 compliance | no pilot correlation consumed (#57); Delta is a per-pair scalar so its variance is measured directly and no covariance is needed anywhere |

| pairs/w | truth | role | truth value | SE | fires at 2 SE | bar | PASS |
|---|---|---|---|---|---|---|---|
| 128 (registered) | w = 0 (null) | false-fire | 0.0 | 0.000375583595517605 | 0.043 | 0.1 | True |
| 128 (registered) | w = 1.0 (algebraic truth) | power | 0.3695134875442334 | 0.000375583595517605 | 1.0 | 0.8 | True |

False-fire 0.043 at w = 0 (bar 0.1) and power 1.0 at the algebraic w = 1.0
truth (bar 0.8). Escalation did not fire (False).

## 7. Routing

| # | condition | outcome |
|---|---|---|
| 1 | G0 / import / hash failure | STOP |
| 2 | projection fails after escalation | NON_PROJECTABLE |
| 3 | all four certificates PASS | IDENTITY_CHANNEL_CERTIFIED -- R2 becomes registrable; the founding question is posable |
| 4 | any certificate fails | **INSTRUMENT_DEFECT(name) -- the failing certificate is the finding**  <-- THIS LEG |

## 8. Gates

| gate | PASS | detail |
|---|---|---|
| G0 | True | P3b hashes match P3c's persisted; w_mu bit-exact; the injection site located |
| C-R1a | True | backward bit-identity at w_style = 0 across objects, panels, cards and fields |
| C-R1b | True | style is author-stream; independent of trait; the card recomposes from the named parts and the shared component is named (#60) |
| G2r1 | True | rule-29 predicate; bands variances-only (#57) |
| G3r1 | True | escalation fired: False |
| C-R1c | False | null at 0, positive at 0.5 and 1.0, monotone, and inside the Part-0 algebraic band |

## 9. Sides declared (rule 22)

| clause | statement | prior | sided |
|---|---|---|---|
| C-R1c | Delta ~ 0 at w=0; POSITIVE at 0.5 and 1.0; MONOTONE; INSIDE the Part-0 algebraic band | — | conjunction |
| L-1r1 | CERTIFIED / a named certificate fails / other | 0.70 / 0.25 / 0.05 | categorical |

## 10. Pinned readings

| note | pinned reading |
|---|---|
| RN-R1-1 | w_style is in multiples of w_mu, so w_mu*trait + w_style*style = w_mu*(trait + m*style) EXACTLY; publishing trait_eff = trait + m*style as the world's `trait` makes k2b's own UNEDITED emit_panel carry style at precisely the trait's site. trait_pure and style are published separately for C-R1c and C-R1b. k2b/suica_core/P3b stay READ-ONLY |
| RN-R1-2 | style_a is the LAST author-stream draw (after _zeta), so every earlier draw is bit-identical to P3b's by the sequential-generator prefix property; a_load has its own stable_bucket generator and the frame stream is never read. C-R1a proves it rather than asserting it |
| RN-R1-3 | #60 naming: at w_style > 0 the A/B shared component is w_mu*trait_c + w_style*style_c (centred trait PLUS centred style); r-hat is scored against the CENTRED TRAIT ONLY, deliberately, so the planted style appears as excess instead of being absorbed |
| RN-R1-4 | the PER-AUTHOR EXACT Delta routes (the form #60 blesses and on which Q1b's adjudication rests); the pooled-mean form is reported beside it and any disagreement is the finding |
| RN-R1-5 | algebraic band: with a = E\|\|w_mu*trait_c\|\|^2, b = E\|\|w_style*style_c\|\|^2, d = E\|\|frame remainder\|\|^2, Delta = b/(a+b+d) in expectation -- exactly 0 at w=0 and increasing in w. a, b, d are MEASURED on probe worlds in Part 0 and the prediction + band persisted BEFORE any arm (rule 30) |
| RN-R1-6 | #59: Delta at w > 0 is not forced -- it depends on realized norms and the planted weight; the w = 0 null is the unextended builder's verified behaviour, not an identity of the extension; the 'style is secretly trait' degeneracy is what C-R1b's independence check tests |

## 11. Rule events

- **Rule 13:** 0 event(s); bootstrap B = 2000.
- **Rule 25:** the projection gate passed at the registered size.
- **Rule 26:** no bounded winner.
- **Rule 27:** no budgeted consumption; the algebraic band is a prediction, not
  a budget.
- **Rule 29:** the domain-pinned predicate ran at every arm.
- **Rule 30:** the algebraic band is derived from MEASURED probe-world norms and
  persisted before the arms; w_mu and the P3b hashes are verified at source.
- **#57:** no pilot correlation consumed — Δ is a per-pair scalar, so its
  variance is measured directly and no covariance is needed anywhere.
- **#59:** Δ at w > 0 is not forced by any shared-object identity; the w = 0
  null is the unextended builder's verified behaviour, not an identity of the
  extension.
- **#60:** the shared component is named — w_mu·trait_c + w_style·style_c.

## 12. What this licenses

The k2b family now has a **certified identity channel**: per-author, persistent,
non-trait, card-visible, inert at zero, and recoverable at the size the
composition arithmetic predicts. The programme's identity instruments can be
pointed at a world that can answer YES or NO — which is what appendix KK said
was missing. **R2 becomes registrable.**

What it does **not** license: nothing about the k2b family's own worlds. The
channel is planted, not discovered; the closed lines' verdicts stand exactly as
adjudicated, and appendix KK's structural boundary is unmoved. This leg buys the
ability to ask, not an answer.

## 13. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine; a CPython 3.12.12 venv was built outside the repo
   from `requirements-lock-main.txt` verbatim and pinned. Resolved BEFORE any
   hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.

## 14. Environment

| component | value |
|---|---|
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| platform | macOS-26.4.1-arm64-arm-64bit |
| python | 3.12.12 |
| python_executable | /private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python |
| scipy | 1.17.1 |

## 15. Timing

| stage | estimate (s) | measured (s) |
|---|---|---|
| part0 (incl. C-R1a/b and the band) | 150 | 6.401 |
| pilot | 60 | 0.353 |
| project | 30 | 0.000 |
| arm w=0.0 | 200 | 5.390 |
| arm w=0.5 | 200 | 5.410 |
| arm w=1.0 | 200 | 5.393 |
| fit | 120 | 0.021 |
| finalize | 60 | 0.000 |

---

*Artifacts: `results/m4_r1_identity_channel/` (gitignored) — `part0.json`,
`pilot.json`, `pilot_field.csv`, `projection.json`, `arms/`, `fit.json`,
`decision.json`, `prose_facts.json`, `report_tables.md`, `run_log.jsonl`.
Harness: `scripts/run_suica_m4_r1_identity_channel.py`.*
