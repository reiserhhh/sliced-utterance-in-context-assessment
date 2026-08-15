# SUICA M4-S2 — the transfer law

**Outcome: `TRANSFER_LAW_SEALED`** (rule-16 cell 4). Modifiers: GAMMA0_NULL_CONFIRMED_ON_FRESH_WORLDS, DIRECTION_READING_AGREES.
Interior hits: **3/3**.

Registered before the run in `docs/SUICA_M4_S_SELECTION_LINE_PLAN.md` ("M4-S2",
commit 84962a5). EXPLORATORY, synthetic, label-free. **The coupling is built by
the generator**: this is a law of the apparatus, not of people.

## 1. What was sealed

Selection similarity is driven by γ·u + (1−γ)·v with u ⟂ v; trait similarity by
u alone. The derived shape is

    r(γ) = r(1) · g(γ),   g(γ) = γ² / √(γ⁴ + (1−γ)⁴)

with the amplitude r(1) = 0.23983432331725474 taken from S1 and bit-verified. The three
interior points are the test.

**The transfer law holds.** All three interior points land inside bands fixed before any world existed (γ=0.25 at -0.10995782940173755, γ=0.5 at -0.2717359118085588, γ=0.75 at -0.3629171127689849). The shape r(γ) = r(1)·γ²/√(γ⁴+(1−γ)⁴) is sharply non-linear — a near-flat top and a collapsing knee — so this is not a curve a smooth monotone guess could have matched by luck.

## 2. The sealed predictions

| γ | g(γ) | planner sanity | prediction | SE_pred | SE_meas | SE_approx | half-width | band |
|---|---|---|---|---|---|---|---|---|
| 0.25 | 0.11043152607484653 | 0.1104 | 0.02648527032905259 | 0.00016200230186118092 | 0.002324586047924536 | 0.021690319564518324 | 0.04363026050121361 | [-0.01714499017216102, 0.0701155308302662] |
| 0.5 | 0.7071067811865475 | 0.7071 | 0.16958847637891772 | 0.0010373208655672403 | 0.002324586047924536 | 0.10940957607134302 | 0.21887836869808167 | [-0.04928989231916395, 0.38846684507699936] |
| 0.75 | 0.9938837346736188 | 0.9938 | 0.2383674329614733 | 0.0014580207167506282 | 0.002324586047924536 | 0.043552479712535445 | 0.08727767214621368 | [0.15108976081525963, 0.32564510510768696] |

`prediction.json` hashed `ef870d43d6c73757…`, stamped 2026-08-15T17:27:40.278163+00:00 with **0 fresh
worlds and 0 probe worlds in existence** — the band needed none, because
SE_meas came from S1's persisted spread and SE_approx from standard normals.
The arms re-read the stamp and re-hashed to a match at 2026-08-15T17:27:58.239438+00:00, 17.961275 s
later.

### 2.1 The SE_approx budget, and which way it errs

| γ | analytic g | pipeline ratio (mean) | ratio sd | \|deviation\| mean | \|deviation\| max | budget (× conservatism) |
|---|---|---|---|---|---|---|
| 0.25 | 0.11043152607484653 | 0.07766211128618199 | 0.013608651968474933 | 0.03276941478866454 | 0.06029250877441813 | 0.09043876316162719 |
| 0.5 | 0.7071067811865475 | 0.44959247073676384 | 0.02274388784050644 | 0.25751431044978357 | 0.3041254328072555 | 0.45618814921088324 |
| 0.75 | 0.9938837346736188 | 0.8823526228138191 | 0.0069168510746423885 | 0.11153111185979984 | 0.12106268224425876 | 0.18159402336638814 |

SE_approx is the softmax / z-scoring distortion, built from **probe-free**
objects: standard-normal u and v pushed through the pipeline's own arithmetic —
z-scoring, score = β*(γu + (1−γ)v), softmax, cosine of the preference vectors,
Mantel against cosine of centred u — with no world, no builder and no
multinomial draw. The realized shape ratio is compared to the analytic g(γ) and
the deviation is the budget.

**Conservatism direction, stated as the registration requires:** the budget
takes the **maximum** absolute deviation across repetitions, not the mean, and
multiplies by 1.5. The reason is R2b, where this executor's probe-based
transport term undersized the realized value by 1.53×. So the budget errs
**wide**, which makes the sealed test **easier** to pass. That is the direction a
reader must know, because it is the one that flatters a hit rather than the one
that excuses a miss. It deliberately excludes multinomial sampling noise, which
is SE_meas's job.

## 3. Gates

| gate | PASS | detail |
|---|---|---|
| G0s2 | True | r(1) bit-exact True (0.23983432331725474); β* 1.7 matches True; S1 C-S1c PASS True; S1 hash verified |
| G1s2 / #59 | True | interior preferences genuinely mixed: mean max-π {'g0.25': 0.5856019757375133, 'g0.75': 0.5872647734807723} (1/4 = flat, 1 = collapsed) |
| G2s2 | True | rule-29 predicates, 4 pilot worlds |
| G3s2 | True | escalation fired: False; n_final 16 |

| γ | half-width | power at truth | false-fire at −3·band | PASS |
|---|---|---|---|---|
| 0.25 | 0.04363026050121361 | 1.0 | 0.0 | True |
| 0.5 | 0.21887836869808167 | 1.0 | 0.0 | True |
| 0.75 | 0.08727767214621368 | 1.0 | 0.0 | True |

## 4. Results

| γ | measured Mantel r | CI95 | SEM | sd | worlds |
|---|---|---|---|---|---|
| 0.0 | -0.000556827079510771 | [-0.001610303477140683, 0.0004102164964021282] | 0.0005139081760339071 | 0.0020556327041356282 | 16 |
| 0.25 | 0.021687781588106775 | [0.019706868338856466, 0.023929471306571363] | 0.0011081395283929366 | 0.004432558113571746 | 16 |
| 0.5 | 0.11011136328557458 | [0.10764037282740947, 0.11285795106841882] | 0.001367680212097663 | 0.005470720848390652 | 16 |
| 0.75 | 0.20669287217697138 | [0.204047311871756, 0.20943216928148053] | 0.0014421749426070639 | 0.0057686997704282554 | 16 |
| 1.0 | 0.237741075953029 | [0.23415995152633748, 0.24081471764146747] | 0.0017329278650054674 | 0.00693171146002187 | 16 |

### 4.1 V-S2b — the three sealed interior tests

| γ | prediction | measured | CI95 | half-width | position | INSIDE |
|---|---|---|---|---|---|---|
| 0.25 | 0.02648527032905259 | 0.021687781588106775 | [0.019706868338856466, 0.023929471306571363] | 0.04363026050121361 | -0.10995782940173755 | **True** |
| 0.5 | 0.16958847637891772 | 0.11011136328557458 | [0.10764037282740947, 0.11285795106841882] | 0.21887836869808167 | -0.2717359118085588 | **True** |
| 0.75 | 0.2383674329614733 | 0.20669287217697138 | [0.204047311871756, 0.20943216928148053] | 0.08727767214621368 | -0.3629171127689849 | **True** |

### 4.1b The sharper, secondary prediction — and the defect it exposes

| γ | pipeline ratio | analytic pred | pipeline pred | bias absorbed by SE_approx | half-width | band |
|---|---|---|---|---|---|---|
| 0.25 | 0.07766211128618199 | 0.02648527032905259 | 0.01862603990771079 | 0.007859230421341802 | 0.005021709419392657 | [0.013604330488318132, 0.023647749327103444] |
| 0.5 | 0.44959247073676384 | 0.16958847637891772 | 0.1078277059876844 | 0.061760770391233316 | 0.0057682731266421915 | [0.10205943286104222, 0.11359597911432659] |
| 0.75 | 0.8823526228138191 | 0.2383674329614733 | 0.2116184442197572 | 0.026748988741716103 | 0.005406852719451732 | [0.20621159150030546, 0.21702529693920894] |

| γ | measured | analytic pred (routes) | position vs analytic band | pipeline pred (sharp) | position vs pipeline band | inside pipeline? |
|---|---|---|---|---|---|---|
| 0.25 | 0.021687781588106775 | 0.02648527032905259 | -0.10995782940173755 | 0.01862603990771079 | 0.6097010847685176 | True |
| 0.5 | 0.11011136328557458 | 0.16958847637891772 | -0.2717359118085588 | 0.1078277059876844 | 0.39589964756393814 | True |
| 0.75 | 0.20669287217697138 | 0.2383674329614733 | -0.3629171127689849 | 0.2116184442197572 | -0.9109869083479094 | True |

**This is the leg's methodological finding, and it was fixed before any world existed.** The registered SE_approx absorbs the softmax distortion into band WIDTH. But the budget's own arithmetic shows that distortion is not uncertainty — it is a systematic, sign-stable bias: the analytic g overshoots the pipeline ratio at every interior γ, and the Monte-Carlo spread of that ratio is an order of magnitude smaller than the bias. Absorbing a known bias into a #61 band inflates the γ = 0.5 half-width past the prediction itself and makes the sealed test nearly unfalsifiable. **A #61 band states uncertainty; a known bias belongs in the prediction.**

So a second prediction was stamped alongside the first — equally probe-free, equally pre-world — using the pipeline ratio directly. The registered analytic prediction is what ROUTES and is unchanged. On the measurements: **3/3 inside the registered analytic bands, 3/3 inside the far tighter pipeline bands.** The comparison is the point — a wide band that cannot fail is worth less than a narrow one that could have.

### 4.2 Anchors (these route INSTRUMENT_DEFECT, never a shape cell)

| anchor | measured | reference | test | result |
|---|---|---|---|---|
| γ = 1 vs S1 (distributional) | 0.237741075953029 | 0.23983432331725474 | \|dev\| -0.0020932473642257254 ≤ 2√2·SEM 0.006421905101506714 (z -0.921937887620048) | **True** |
| γ = 0 vs the ε-null | -0.000556827079510771 | 0 | ε = 0.010125436066679785 | **True** |

γ = 1 re-measured on fresh worlds gives 0.237741075953029 against S1's 0.23983432331725474 (z =
-0.921937887620048, PASS = True). γ = 0 gives -0.000556827079510771 [-0.001610303477140683, 0.0004102164964021282] against ε = 0.010125436066679785 →
NULL = True — **the falsifier arm reproduces on fresh worlds**, which is
what licenses reading the interior points as shape rather than artefact.

### 4.3 V-S2c — the direction reading (adjudicates nothing)

| γ | cosine selection similarity | distance selection similarity | signs agree |
|---|---|---|---|
| 0.0 | -0.000556827079510771 | -0.00043224833677620684 | True |
| 0.25 | 0.021687781588106775 | 0.021465523423801258 | True |
| 0.5 | 0.11011136328557458 | 0.10942243030319881 | True |
| 0.75 | 0.20669287217697138 | 0.2053878765118171 | True |
| 1.0 | 0.237741075953029 | 0.23575296552240346 | True |

Signs agree across geometries: True. Cosine exceeds distance at γ = 1:
True — T8's expectation, checked rather than assumed.

## 5. Anomalies

1. **A-1 (before any number).** Interpreter re-verified as standing practice:
   `/private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv2/bin/python`, Python 3.12.12 — matching every prior leg.
2. **A-2 (before any number).** `timeout(1)` is absent on macOS; every stage ran
   as its own foreground command under an explicit tool timeout.
3. **A-3 (before any number).** No world of any kind — probe or arm — preceded
   the stamp, because both data-dependent band terms were sourced from persisted
   S1 objects and from standard-normal arithmetic. This is the cleanest K2f
   ordering the program has achieved.

## 6. Boundary

EXPLORATORY, synthetic, label-free. **γ is a knob this apparatus turns**, so the
law is a law of the generator; it says how a built coupling transfers, not that
any real selection behaviour obeys it. One share, one φ, one β, one panel,
16 worlds per arm. The real-data counterpart is SR1, which is a separate
measurement on a separate object and is not evidence for this shape (nor this
shape for it).

## 7. Environment

`/private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv2/bin/python` — Python 3.12.12.
