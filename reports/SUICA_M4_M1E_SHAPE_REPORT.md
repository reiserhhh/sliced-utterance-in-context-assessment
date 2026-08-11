# M4-M1e — the shape: additive or r-mediated

**Leg:** M4-M1e · **Registered** 2026-08-11 in
`docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md` (section "M4-M1e — the shape: additive
or r-mediated"), commit `af4a335`, BEFORE this run.
**Executor:** dispatched agent (implementation and execution only; the
registration text is binding).
**Harness:** `scripts/run_suica_m4_m1e_shape.py`.
**Artifacts:** `results/m4_m1e_shape/` (gitignored).
**Banner:** artifact-space shape tournament on M1c's persisted 3840-world
corpus; no new worlds, exploratory, label-free.

**Verdict: `IDENTIFIED_INSUFFICIENTLY` (rule-16 cell 6), modifier `TAX_SHIFT`.**
L-1e **MISS (r-mediated wins)**, L-2e **MISS**, L-3e **quiet**. Rule-27 budgets met:
**False**. Sealable: **False**.

Four results, and the order matters because the last one overturns the most
comfortable thing the line believed.

**One: the field does not separate.** The best additive form (`E-add`,
LOO `0.002706675155983591`) loses to the best r-mediated form
(`E-rq`, `0.0024079360107794926`). **L-1e MISSES**; r-mediation is not dead
at level, it is the better account. The winner is **`E-rq`** —
`field = alpha_s + lambda*r^q` — at LOO `0.0024079360107794926`, ahead of the runner-up
`E-rlin` by 11.89129978102812%, well outside the tie band.

**Two: the shape probe finally goes quiet.** Under the winner the within-share
r² residual is `-0.007427848773582237`, CI `[-0.03672898793443594, 0.018353437794254]` — **containing zero**. The probe
that fired in M1c (−0.199) and again in M1d (−0.126) is silent once the model
carries free share margins *and* a power in r. **L-3e: quiet.** The shape
question, as the registration posed it, is answered.

**Three: and the answer is still not sealable.** Rule 27 — the rule this leg's
predecessor bought — blocks it. The winner's exponent is `q = 3.863625377453229` with CI
`[2.0529339475688055, 5.921369905297595]`, **width `3.86843595772879` against a `1.0` budget**, missing it
by a factor of 3.86843595772879. Selection is not identification, and here the
two come apart cleanly: the model that predicts best carries an exponent the
corpus cannot pin. Routing is cell 6, **`IDENTIFIED_INSUFFICIENTLY`** — the
scoped-M2 route, not a seal.

**Four, and this is the one to carry: κ is representation-dependent.** Forcing
the share margin through the linear tax — `E-tax-add` — costs 32.229399557283564%
of LOO and makes it **the worst of the five models**. And the κ it reports is
`0.6761549415814`, CI `[0.6619291032569563, 0.6901486195533926]` — **disjoint below** M1d's
`[0.7482226203832176, 0.8064115044591174]`. **L-2e MISSES on both clauses**, and the **`TAX_SHIFT`
modifier fires to M3**. The five prior appearances ([0.715, 0.722, 0.75, 0.76, 0.777]) were
appearances *within one family of representations*; change the representation
and κ moves off the band. That is M3's question, arriving earlier and sharper
than expected.

---

## Part 0 — written before any fit

### 0.1 Rule 9 / rule 12 — conventions pinned in writing

| note | pinned reading |
|---|---|
| RN-M1E-1 | sum-to-zero pinning on g_phi in BOTH additive models (E-tax-add carries the same c/g redundancy as E-add; without pinning rule 27's own c and g budgets are unmeetable by construction); identifiable counts E-add 8, E-tax-add 6, raw counts 9 and 7 -- the registration's '7 params' is the raw count |
| RN-M1E-2 | start grids the registration did not pin: alpha_s at its own share's mean field, g_phi at 0; E-tax-add adds c x kappa grids; E-rlin adds an s grid; F0 keeps M1d's 162-start grid verbatim as the frozen incumbent |
| RN-M1E-3 | the three LINEAR models are also solved in closed form by lstsq and the two solutions compared (agreement to 1e-10 required and reported) -- no optimizer risk on the models whose budgets decide the routing |
| RN-M1E-4 | L-2e's 'within 5% LOO of E-add' read one-sided: LOO(E-tax-add) <= 1.05 x LOO(E-add) |
| RN-M1E-5 | rule-16 precedence pinned (cell 1 > REPRESENTATION_TIE > 4 > 5 > 6 > 2/3) because the registered table overlaps; immaterial to consequence since cells 4/5/6 share the scoped-M2 route and only 2/3 seal |
| RN-M1E-6 | L-3e's probe inherits the M1c/M1d estimator unchanged so the number is comparable across legs; computed identically regardless of winner |
| RN-M1E-7 | share margins alpha_s are consumed by any seal but carry NO declared budget; their widths are reported beside the budgeted ones and gate nothing |

### 0.2 The five models, and the identifiability bookkeeping

| model | expression | kind | raw params | identifiable | linear | starts |
|---|---|---|---|---|---|---|
| E-add | field = alpha_s + g_phi  (sum-to-zero on g_phi) | additive | 9 | 8 | True | 2 |
| E-tax-add | field = c - kappa*V + g_phi  (sum-to-zero on g_phi) | additive | 7 | 6 | True | 9 |
| E-rlin | field = alpha_s + s*r | r-mediated | 5 | 5 | True | 4 |
| E-rq | field = alpha_s + lambda*r^q | r-mediated | 6 | 6 | False | 20 |
| F0 | field = c + lambda*r^q - kappa*V | r-mediated (M1d's frozen incumbent baseline) | 4 | 4 | False | 162 |

### 0.3 The model-free monotonicity table — the Part-0 object

Computed before any model was fitted: the within-share extreme contrast
`field(φ=0.98) − field(φ=0.05)` with the pooled SE of the two cell means. This
is appendix Y's surviving invariant in its rawest form, and it is what the shape
question must explain.

| share | V | r span | field at phi=0.05 | field at phi=0.98 | contrast | pooled SE | contrast / SE | > 2 SE |
|---|---|---|---|---|---|---|---|---|
| 0.1 | 0.03000000000000001 | 0.04714885082631204 | 0.1585891652101896 | 0.15987119532439534 | 0.0012820301142057455 | 0.002662818947918231 | 0.4814559830318264 | False |
| 0.25 | 0.07500000000000002 | 0.10864636443860598 | 0.12162744485545209 | 0.13201888792665142 | 0.010391443071199338 | 0.0025394961062406947 | 4.091931090448552 | True |
| 0.4 | 0.12000000000000004 | 0.15863752656482977 | 0.09025343262511598 | 0.10169041646048367 | 0.01143698383536769 | 0.0024676318457931964 | 4.634801522303819 | True |
| 0.6 | 0.18000000000000005 | 0.20320393707216905 | 0.05410832013119198 | 0.063796931786496 | 0.009688611655304012 | 0.002401953516046843 | 4.03363828257993 | True |

All 4 contrasts are positive; 3 of 4 exceed 2 SE. The
exception is decisive for the leg: at share 0.10 the contrast is
**0.4814559830318264 SE** — essentially flat — against a minimum of
4.03363828257993 SE at the other three shares, and share 0.10 is exactly
where the r-span is smallest (0.04714885082631204 against spans [0.04714885082631204, 0.10864636443860598, 0.15863752656482977, 0.20320393707216905]). **A strictly additive
field predicts the same contrast at every share. The data do not.** The
tournament below is that observation, formalised.

### 0.4 G0e — the citations, and the frozen incumbent

| clause | adjudication | persisted | bit-exact |
|---|---|---|---|
| F0 c | 0.2234421078663232 | 0.2234421078663232 | True |
| F0 c CI hi | 1.6803368132111625 | 1.6803368132111625 | True |
| F0 c CI lo | 0.20818746052333 | 0.20818746052333 | True |
| F0 kappa | 0.7766770259880144 | 0.7766770259880144 | True |
| F0 kappa CI hi | 0.8064115044591174 | 0.8064115044591174 | True |
| F0 kappa CI lo | 0.7482226203832176 | 0.7482226203832176 | True |
| F0 lambda | -0.055190882521519 | -0.055190882521519 | True |
| F0 lambda CI hi | -0.04256154549067277 | -0.04256154549067277 | True |
| F0 lambda CI lo | -1.5059828481846496 | -1.5059828481846496 | True |
| F0 q | 1.372031438858951 | 1.372031438858951 | True |
| F0 q CI hi | 2.6445200496694605 | 2.6445200496694605 | True |
| F0 q CI lo | 0.021913588793404413 | 0.021913588793404413 | True |
| F0 vs Fphi separation pct | 5.916868553169516 | 5.916868553169516 | True |
| LOO F0 | 0.0030682764618814033 | 0.0030682764618814033 | True |
| LOO F1 | 0.003198131708377386 | 0.003198131708377386 | True |
| LOO F1e | 0.0031856515917748638 | 0.0031856515917748638 | True |
| LOO F2 | 0.0034019365713125944 | 0.0034019365713125944 | True |
| LOO F3 | 0.003877604046883495 | 0.003877604046883495 | True |
| LOO Fphi | 0.0032498223469787663 | 0.0032498223469787663 | True |
| legacy k2f refit LOO | 0.0061559195350209 | 0.0061559195350209 | True |
| legacy ratio | 18.914542176909535 | 18.914542176909535 | True |
| legacy sealed RMSE | 0.11259090547752257 | 0.11259090547752257 | True |
| legacy winner RMSE | 0.0059526106645589934 | 0.0059526106645589934 | True |
| q_shadow | 2.24488769944643 | 2.24488769944643 | True |
| q_shadow CI hi | 2.318980336007031 | 2.318980336007031 | True |
| q_shadow CI lo | 2.1768337883424214 | 2.1768337883424214 | True |
| r2 CI hi B2000 | -0.07219090437007022 | -0.07219090437007022 | True |
| r2 CI hi B20000 | -0.07097803090981235 | -0.07097803090981235 | True |
| r2 CI lo B2000 | -0.1772060912696028 | -0.1772060912696028 | True |
| r2 CI lo B20000 | -0.17935555262608965 | -0.17935555262608965 | True |
| r2 coef | -0.12563681892698172 | -0.12563681892698172 | True |
| tie margin F0 vs F1e | 0.00011737512989346043 | 0.00011737512989346043 | True |
| all 20 cell means and SEMs vs M1c's persisted values | bit-exact | True | True |
| theory band `[1.71, 1.98]` | [1.71, 1.98] | lines [805, 841, 1386] | True |

| quantity | this leg | M1d | bit-exact |
|---|---|---|---|
| F0 theta | [0.2234421078663232, -0.055190882521519, 1.372031438858951, 0.7766770259880144] | [0.2234421078663232, -0.055190882521519, 1.372031438858951, 0.7766770259880144] | True |
| F0 SSE | 0.000125542913673357 | 0.000125542913673357 | True |

---

## The tournament

| model | expression | kind | parameters | in-sample RMSE | LOO-RMSE | R^2 vs mean | distinct optima | lstsq witness diff | bootstrapped |
|---|---|---|---|---|---|---|---|---|---|
| E-add | `field = alpha_s + g_phi  (sum-to-zero on g_phi)` | additive | alpha_s0.10 = 0.16110015711420475, alpha_s0.25 = 0.12715920641561385, alpha_s0.40 = 0.09611838124372614, alpha_s0.60 = 0.059488406754928294, g_phi0.05 = -0.00482194717663085, g_phi0.30 = -0.002949742497307577, g_phi0.60 = 0.0008027742599145105, g_phi0.85 = 0.0035910954216355657, g_phi0.98 = 0.003377819992388351 | 0.0016240050935901606 | 0.002706675155983591 | 0.9981498861294329 | 1 | 5.55e-17 | no |
| E-tax-add | `field = c - kappa*V + g_phi  (sum-to-zero on g_phi)` | additive | c = 0.17942722572114997, kappa = 0.6761549415814, g_phi0.05 = -0.0048219471766308515, g_phi0.30 = -0.0029497424973075753, g_phi0.60 = 0.0008027742599145088, g_phi0.85 = 0.003591095421635563, g_phi0.98 = 0.0033778199923883553 | 0.0024821194127422233 | 0.003579020306723271 | 0.9956781565890349 | 1 | 3.31e-10 | yes |
| E-rlin | `field = alpha_s + s*r` | r-mediated | alpha_s0.10 = 0.20898849705947717, alpha_s0.25 = 0.17152603250762263, alpha_s0.40 = 0.1365481232580123, alpha_s0.60 = 0.09356471191224446, s = -0.059789716308364924 | 0.002017281473009283 | 0.0026942709003566117 | 0.9971453249133202 | 1 | 5.59e-11 | no |
| **E-rq (winner)** | `field = alpha_s + lambda*r^q` | r-mediated | alpha_s0.10 = 0.18560847593788873, alpha_s0.25 = 0.1456494891347315, alpha_s0.40 = 0.10934916761257428, alpha_s0.60 = 0.06667603971206824, lambda = -0.057625974791364554, q = 3.863625377453229 | 0.001659062336203629 | 0.0024079360107794926 | 0.9980691475243493 | 4 | n/a (nonlinear) | yes |
| F0 | `field = c + lambda*r^q - kappa*V` | r-mediated (M1d's frozen incumbent baseline) | c = 0.2234421078663232, lambda = -0.055190882521519, q = 1.372031438858951, kappa = 0.7766770259880144 | 0.0025054232543959215 | 0.0030682764618814033 | 0.9955966227616307 | 109 | n/a (nonlinear) | no |

| quantity | value |
|---|---|
| LOO ranking | E-rq < E-rlin < E-add < F0 < E-tax-add |
| winner | E-rq (r-mediated) |
| runner-up | E-rlin (r-mediated) |
| separation | 0.00028633488957711907 |
| … as a fraction of the winner's LOO | 0.11891299781028121 |
| tie rule active (< 5%) | False |
| REPRESENTATION_TIE (tie ACROSS the additive / r-mediated divide) | False |
| best additive | E-add at 0.002706675155983591 |
| best r-mediated | E-rq at 0.0024079360107794926 |
| F0 (frozen incumbent) | 0.0030682764618814033 |
| additive beats ALL r-mediated and F0 (L-1e) | False |

Three of the five models are linear in their parameters and were therefore also
solved in closed form; the largest disagreement between the optimizer and
`lstsq` across all three is `3.311532159600006e-10` (RN-M1E-3), so no routing decision
here rests on optimizer behaviour.

A quiet internal check worth recording: `E-add` and `E-tax-add` return
**identical** `g_φ` margins (True) — expected, because the design is
balanced (every φ appears exactly once per share) so the sum-to-zero φ margins
are orthogonal to both the share margins and to V. The two models differ only in
how they represent the share direction, and that is precisely what their LOO gap
measures.

### The φ margin, for the record

`E-add`'s margin is `[-0.00482194717663085, -0.002949742497307577, 0.0008027742599145105, 0.0035910954216355657, 0.003377819992388351]` across φ = [0.05, 0.3, 0.6, 0.85, 0.98], a span of
`0.008413042598266415` — monotone rising and then flattening. It is a perfectly
reasonable curve. It simply cannot be right at every share simultaneously, which
is what the monotonicity table already said and what the LOO ranking confirms.

---

## Verdicts

| lean | clause | sided | prior | measured | verdict |
|---|---|---|---|---|---|
| L-1e | an ADDITIVE form (E-add or E-tax-add) wins LOO outright over all r-mediated forms AND F0 | one-sided | additive .45 / r-mediated .35 / F0 stands .20 | best additive 0.002706675155983591 vs best r-mediated 0.0024079360107794926 vs F0 0.0030682764618814033 | **MISS (r-mediated wins)** |
| L-2e | the share margin IS the tax: LOO(E-tax-add) <= 1.05 x LOO(E-add) AND E-tax-add's kappa CI overlaps M1d's [0.7482226203832176, 0.8064115044591174] (the sixth appearance) | conjunction; the overlap clause two-sided | 0.60 | LOO 0.003579020306723271 vs bar 0.002842008913782771 (False); kappa CI [0.6619291032569563, 0.6901486195533926] vs M1d [0.7482226203832176, 0.8064115044591174] (disjoint-low) | **MISS** |
| L-3e | the winner's within-share r^2 probe -- quiet => SHAPE settled; fires => shape remains open | reading that ROUTES | — | r^2 -0.007427848773582237 CI [-0.03672898793443594, 0.018353437794254] | **quiet** |
| rule 27 | kappa width <= 0.15; c width <= 0.05; each g_phi width <= 0.01; s width <= 50% of abs(point); E-rq q width <= 1.0 | one-sided per parameter | — | 1 budgeted parameters on the winner | **UNMET** |

### L-1e — the field does not separate

Best additive `0.002706675155983591` vs best r-mediated `0.0024079360107794926` vs
F0 `0.0030682764618814033`. The additive family does not beat the r-mediated family, so
**L-1e MISSES** against its .45 prior; the .35 complement (r-mediated wins) is
what paid. Note that `E-add` and `E-rlin` are nearly level
(`0.002706675155983591` vs `0.0026942709003566117`) — the additive
representation is not *bad*, it is simply beaten, and beaten decisively only by
the model that has both free share margins and an r-power.

### L-2e — the share margin is NOT the tax

Two clauses, both failed. The LOO clause: `E-tax-add` at `0.003579020306723271`
against the bar `0.002842008913782771` (= 1.05 × `0.002706675155983591`) — a
32.229399557283564% cost, not a 5% one. Forcing the four share margins onto a
straight line in V is expensive, because they are not on one: the field's share
margins carry curvature that `−κ·V` cannot represent.

The κ clause: `[0.6619291032569563, 0.6901486195533926]` against M1d's `[0.7482226203832176, 0.8064115044591174]` —
**disjoint-low**. There is **no sixth appearance** (False); there is a
shift. **Modifier `TAX_SHIFT` fires to M3.**

**The honest qualification, stated because it changes how M3 should read this.**
The κ that shifted belongs to `E-tax-add`, and `E-tax-add` is the model this
same leg ranks LAST. So the finding is not "κ is 0.676"; it is
**"κ's value depends on the representation it is embedded in, and the
dependence is larger than any of its five prior confidence intervals."** The
winning model does not contain a κ at all — its share direction is four free
margins, and the tax is implicit in them. A constant that changes when you
change the surrounding form is not yet an instrument constant.

### L-3e — quiet, and that is real progress

| quantity | value | 95% CI |
|---|---|---|
| kind | r-mediated | — |
| lambda | -0.057625974791364554 | [-0.0843564122153383, -0.042724477794351616] |
| exponent q | 3.863625377453229 | [2.0529339475688055, 5.921369905297595] |

The winner's r-coefficient is `-0.057625974791364554`, CI `[-0.0843564122153383, -0.042724477794351616]` — **negative and
identified**, which is appendix Y's invariant reappearing in a third
parameterisation. The exponent riding on it is not: `q = 3.863625377453229`, CI
`[2.0529339475688055, 5.921369905297595]`.

---

## Rule 27 — the budgets, and why nothing is sealed

| parameter | point | 95% CI width | budget | budget rule | met |
|---|---|---|---|---|---|
| alpha_s0.10 | 0.18560847593788873 | 0.015203974958038241 | — | no budget declared (RN-M1E-7) | — |
| alpha_s0.25 | 0.1456494891347315 | 0.015209021910085607 | — | no budget declared (RN-M1E-7) | — |
| alpha_s0.40 | 0.10934916761257428 | 0.01511553251962218 | — | no budget declared (RN-M1E-7) | — |
| alpha_s0.60 | 0.06667603971206824 | 0.012928411315645191 | — | no budget declared (RN-M1E-7) | — |
| lambda | -0.057625974791364554 | 0.04163193442098668 | — | no budget declared (RN-M1E-7) | — |
| q | 3.863625377453229 | 3.86843595772879 | 1.0 | width <= 1.0 | False |

1 parameter(s) on the winner carry a declared budget and
5 do not (RN-M1E-7, reported and gating nothing). The budgeted
one **fails**: `q`'s width `3.86843595772879` against `1.0`.

This is rule 27 doing exactly the job defect #45 bought it for. Under the
pre-rule-27 routing this leg would have read "r-mediated wins, probe quiet →
`R_MEDIATED_SETTLED`, M2 seals it" and handed M2 an exponent spanning
`[2.0529339475688055, 5.921369905297595]`. The rule intercepts that. The interesting detail is that the
*other* parameters are fine — the share margins run
`[0.015203974958038241, 0.015209021910085607, 0.01511553251962218, 0.012928411315645191]` wide and λ is `0.04163193442098668` — so the object is not
uniformly vague; it has one bad coordinate, and the budget catches precisely
that one.

For contrast, `E-tax-add` — the rejected model — **meets every budget it has**.
Being identifiable and being right are independent properties, and this leg
exhibits both directions of that independence in a single table.

---

## Routing — the rule-16 table, reproduced verbatim

| # | condition | outcome |
|---|---|---|
| 1 | any G0e mismatch | STOP (citation defect) |
| 2 | additive wins AND winner's probe quiet AND budgets met | ADDITIVE_SHAPE_SETTLED -- r-mediation dead at level on this family; the arguments are (V, phi); M2 seals the winner at exterior-share x interior-phi cells |
| 3 | r-mediated wins AND probe quiet AND budgets met | R_MEDIATED_SETTLED -- M2 seals it |
| 4 | F0 stands (nothing beats it) | NO_BETTER_SHAPE -- the M1-series closes at its measured limit: identified = level band + negative slope + tax; shape = named open; M2 re-charters on the SCOPED object (kappa-channel + model-free cell predictions) |
| 5 | any winner AND probe fires | SHAPE_OPEN_NAMED -- same scoped-M2 route as cell 4 |
| 6 | routing would seal but budgets unmet | **IDENTIFIED_INSUFFICIENTLY -- scoped-M2 route**  <-- THIS LEG |
| -- | tie (<5% LOO) between an additive and an r-mediated form | REPRESENTATION_TIE -- both reported, verdicts co-adjudicated, disagreement SPLIT; routing takes the SCOPED route (a tie on representation is not a settled shape) |
| -- | L-2e kappa disjoint | modifier TAX_SHIFT -> M3 |

Precedence was pinned in Part 0 (RN-M1E-5) because the registered table
overlaps. It did not bite here: with the probe quiet and budgets unmet, only
cell 6 matched. The overlap is recorded as a defect candidate below.

| quantity | value | bar | scale | within 5% |
|---|---|---|---|---|
| E-tax-add: kappa_hi vs M1d ci95 lo | 0.6901486195533926 | 0.7482226203832176 | 0.7482226203832176 | False |
| E-tax-add: kappa_lo vs M1d ci95 hi | 0.6619291032569563 | 0.8064115044591174 | 0.8064115044591174 | False |
| LOO separation winner vs runner-up | 0.00028633488957711907 | 0.0 | 0.0024079360107794926 | False |
| L-2e: LOO(E-tax-add) - 1.05*LOO(E-add) | 0.0007370113929405001 | 0.0 | 0.002842008913782771 | False |

| model | max abs(param) | presses numeric limit | distinct optima |
|---|---|---|---|
| E-add | 0.16110015711420475 | False | 1 |
| E-tax-add | 0.6761549415814 | False | 1 |
| E-rlin | 0.20898849705947717 | False | 1 |
| E-rq | 3.863625377453229 | False | 4 |
| F0 | 1.372031438858951 | False | 109 |

Rule 13 did not trigger (False) — no verdict quantity sat within
5% of its bar. Rule 26's bound trigger cannot fire in this leg (no model
declares bounds) and the numerical-limit surveillance was clean
(False).

## Gates

| gate | PASS | detail |
|---|---|---|
| G0e | True | (i) all 20 cell means and SEMs bit-exact from the rawest artifacts; (ii) 32 M1d adjudication citations; (iii) the theory band |
| F0 frozen | True | the incumbent baseline reproduces M1d's fit bit-exactly on the same means |
| rule 27 | False | 1 budgeted parameters on the winner; 5 reported without a declared budget (RN-M1E-7) |

## Sides declared in Part 0 (rule 22)

| clause | statement | sided | improvement side |
|---|---|---|---|
| L-1e | an ADDITIVE form (E-add or E-tax-add) wins LOO outright over all r-mediated forms AND F0 | one-sided | the additive form wins |
| L-2e | the share margin IS the tax: LOO(E-tax-add) <= 1.05 x LOO(E-add) AND E-tax-add's kappa CI overlaps M1d's [0.7482226203832176, 0.8064115044591174] (the sixth appearance) | conjunction; the overlap clause two-sided | neither |
| L-3e | the winner's within-share r^2 probe -- quiet => SHAPE settled; fires => shape remains open | reading that ROUTES | quiet is settled |
| rule 27 budgets | kappa width <= 0.15; c width <= 0.05; each g_phi width <= 0.01; s width <= 50% of abs(point); E-rq q width <= 1.0 | one-sided per parameter | narrower is better |

## The cells and the winner's residuals

| cell | share | phi | r_pred | V_person | mean field | SEM | residual (winner) |
|---|---|---|---|---|---|---|---|
| s0.10_p0.05 | 0.1 | 0.05 | 0.8189581462487876 | 0.03000000000000001 | 0.1585891652101896 | 0.0018743992250782693 | -0.00038177680566145455 |
| s0.10_p0.30 | 0.1 | 0.3 | 0.8155586799827954 | 0.03000000000000001 | 0.16035538669822857 | 0.0020066026535869932 | 0.000959770503694668 |
| s0.10_p0.60 | 0.1 | 0.6 | 0.8075174172340943 | 0.03000000000000001 | 0.16156034289722412 | 0.0019744651453781504 | 0.0011801679107609764 |
| s0.10_p0.85 | 0.1 | 0.85 | 0.7908869485651705 | 0.03000000000000001 | 0.16512469544098618 | 0.001983741777975856 | 0.0027955523011653494 |
| s0.10_p0.98 | 0.1 | 0.98 | 0.7718092954224756 | 0.03000000000000001 | 0.15987119532439534 | 0.0018913572625018093 | -0.004553713909961399 |
| s0.25_p0.05 | 0.25 | 0.05 | 0.785015540293945 | 0.07500000000000002 | 0.12162744485545209 | 0.0017778785791358425 | -0.001403365128814421 |
| s0.25_p0.30 | 0.25 | 0.3 | 0.7761302864207245 | 0.07500000000000002 | 0.12295515685269942 | 0.001799144985921348 | -0.0010488666898157417 |
| s0.25_p0.60 | 0.25 | 0.6 | 0.7558507450373838 | 0.07500000000000002 | 0.12714790436588774 | 0.0017053615065044834 | 0.001039141689870432 |
| s0.25_p0.85 | 0.25 | 0.85 | 0.7168731389294273 | 0.07500000000000002 | 0.13204663807737851 | 0.0018782693723257374 | 0.0023229584507261647 |
| s0.25_p0.98 | 0.25 | 0.98 | 0.6763691758553391 | 0.07500000000000002 | 0.13201888792665142 | 0.0018133362157806163 | -0.0009098683219689319 |
| s0.40_p0.05 | 0.4 | 0.05 | 0.7411873080384952 | 0.12000000000000004 | 0.09025343262511598 | 0.0017452922267459832 | -0.0009794683489100092 |
| s0.40_p0.30 | 0.4 | 0.3 | 0.726425348215848 | 0.12000000000000004 | 0.09132685344495504 | 0.0016796177194939308 | -0.0012608376789230713 |
| s0.40_p0.60 | 0.4 | 0.6 | 0.6941115392115328 | 0.12000000000000004 | 0.0980498887620882 | 0.0015916871722070262 | 0.0027599132999791415 |
| s0.40_p0.85 | 0.4 | 0.85 | 0.6367206581308248 | 0.12000000000000004 | 0.0992713149259878 | 0.0017741240206580028 | -5.047454491105552e-06 |
| s0.40_p0.98 | 0.4 | 0.98 | 0.5825497814736654 | 0.12000000000000004 | 0.10169041646048367 | 0.0017444660987341613 | -0.000514559817657731 |
| s0.60_p0.05 | 0.6 | 0.05 | 0.6573448847694047 | 0.18000000000000005 | 0.05410832013119198 | 0.001773830076330116 | -0.0011746747177380154 |
| s0.60_p0.30 | 0.6 | 0.3 | 0.6346912945232521 | 0.18000000000000005 | 0.057429784543359674 | 0.0015865768513429728 | 0.0007030765294009714 |
| s0.60_p0.60 | 0.6 | 0.6 | 0.5883719155687073 | 0.18000000000000005 | 0.06031911254293101 | 0.0016085232676605703 | 0.0010671017310586728 |
| s0.60_p0.85 | 0.6 | 0.85 | 0.5151304058057474 | 0.18000000000000005 | 0.061787884770662806 | 0.0015046764572937737 | -0.00044619937082480965 |
| s0.60_p0.98 | 0.6 | 0.98 | 0.4541409476972356 | 0.18000000000000005 | 0.063796931786496 | 0.0016195393028748909 | -0.0001493041718992616 |

---

## Anomaly log — every anomaly, with pre/post-hypothesis timing

No worlds were drawn; Part 0 is verification plus the model-free table, and
every RN note was pinned there before any model was fitted.

- **A-1 — the interpreter (before Part 0).** The environment pinned in M4-M1 and
  reused since: CPython 3.12.12 from `requirements-lock-main.txt` (numpy
  `2.4.4`, pandas `3.0.2`, scipy `1.17.1`), platform `macOS-26.4.1-arm64-arm-64bit`.
- **A-2 — `timeout(1)` absent on this platform (before Part 0).** Every stage ran
  as its own foreground command under an explicit harness-level timeout.
- **A-3 — the registration's parameter counts are inconsistent (Part 0, before
  any fit).** "8 identifiable" for `E-add` is the post-pinning count; "7 params"
  for `E-tax-add` is its raw count, and that model's identifiable count under the
  same pinning is 6. Resolved by RN-M1E-1 before any fit, and reported both ways
  in the model table. Non-blocking.
- **A-4 — κ shifts on a rejected representation (at the fit).** The `TAX_SHIFT`
  modifier fires on `E-tax-add`'s κ while `E-tax-add` is the leg's worst model.
  Reported as registered and qualified above rather than suppressed or
  amplified.
- **A-5 — the winner misses its only budget (at the fit).** `q` width
  3.86843595772879× over. This is the routing-determining number and it is
  reported in full.
- **A-6 — no stage approached its 2× stop-and-report threshold.** Part 0
  `4.6163530349731445` s against 120 s; the fit inside its estimate; rule 13 not
  triggered.

| stage | registration estimate (s) | executor estimate (s) | measured (s) |
|---|---|---|---|
| part0 | 120 | 120 | 4.616 |
| fit | 240 | 300 | 98.269 |
| rule13 | -- | 300 | 0.000 |
| finalize | 60 | 60 | 0.025 |

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

**The shape question is answered, and the answer is r-mediated with free share
margins.** `field ≈ α_s + λ·r^q` with λ negative and identified. The additive
separation hypothesis is rejected — not narrowly, and the model-free
monotonicity table rejected it before any model was fitted: an additive field
predicts one contrast per φ-pair everywhere, and share 0.10's contrast is
0.4814559830318264 SE against a minimum of 4.03363828257993 SE elsewhere, in
exact correspondence with its r-span being the smallest of the four.

**The probe is quiet for the first time in three legs.** M1c −0.199, M1d −0.126,
M1e `-0.007427848773582237` `[-0.03672898793443594, 0.018353437794254]`. Whatever the leftover curvature was, free share
margins plus an r-power absorb it. The M1-series' shape question closes.

**Nothing is sealable, and rule 27 is why.** The winner's exponent is
`[2.0529339475688055, 5.921369905297595]`. M2 must take the scoped route: the κ-channel and model-free cell
predictions, not a shape. Note that this is the *second consecutive leg* whose
winner carries a non-identified exponent while its slope is identified — appendix
Y's reading is now supported by three independent parameterisations, and a
successor should consider registering the SLOPE (∂field/∂r at fixed V, or the
within-share contrast itself) as the sealable object rather than any exponent.

**κ is the finding M3 must absorb.** Five prior routes gave [0.715, 0.722, 0.75, 0.76, 0.777];
this leg's taxed representation gives `0.6761549415814` `[0.6619291032569563, 0.6901486195533926]`,
disjoint below all of them, while the winning representation contains no κ at
all. M3 was chartered to ask whether κ is one instrument constant. This leg
supplies a sharp prior answer: **κ's point value is representation-dependent at
a magnitude exceeding its own intervals**, so M3's design must vary the
surrounding form deliberately rather than accumulate more appearances within one
family.

**Registration-defect candidates: four, all non-blocking.**
1. **The rule-16 table overlaps** (RN-M1E-5): (F0 stands AND probe fires) matches
   cells 4 and 5; (winner AND probe fires AND budgets unmet) matches cells 5 and
   6. Immaterial to consequence — cells 4/5/6 share the scoped-M2 route — but it
   is a rule-15/16 partition failure and a successor should enumerate.
2. **Rule 27's budget list is incomplete** (RN-M1E-7): the share margins α_s and
   `E-rq`'s λ are consumed by any seal and carry no declared budget. They happen
   to be well identified here, so nothing turned on it — the same "nothing turned
   on it" that preceded defect #45.
3. **The `TAX_SHIFT` modifier is not conditioned on its host model being
   competitive.** It fires on `E-tax-add`'s κ regardless of `E-tax-add` ranking
   last. That may well be intended, but the registration does not say, and the
   evidentiary weight of a shift measured on a rejected representation is
   materially different from one measured on a winner. A successor should state
   which it means.
4. **The parameter-count wording** (A-3 above).
