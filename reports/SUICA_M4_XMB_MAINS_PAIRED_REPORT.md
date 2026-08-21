# SUICA M4-X-Mb — the mains estimator, paired-scored

**VERDICT — MAINS_CERTIFIED.** Every routing clause of the paired-scored mains battery passed on the realized skeleton, so the corpus main budget below is licensed as an instrument reading — the first true main budget of this design.

Run (UTC): `2026-08-21T03:08:49.236780Z` · seed `20260819` · B_boot `1000` · runtime 31.7 s · config sha256 `c89abfb8c888773d…`

## The reading

**The instrument certifies.** All 10 routing clauses pass under paired scoring, so the corpus main budget in this report is licensed as an instrument reading and X3's #87 prerequisite is discharged for both mains.

**What the repair actually did.** X-M's routing family read `FAIL` with 9 of 10 clauses passing; re-scored paired, 1 clause moved (b_only:community). The clause that stopped X-M is the size-weighted community main in `{b-only}`: its NOMINAL replicate sd is 0.0157 against a ceiling of 0.01, while its PAIRED sd is 0.000508 — a factor of 31 between the two, which is the world's draw noise being charged to the instrument and then not being charged to it.

**The estimator was never the problem, and the numbers say so twice.** Paired, the four own-recovery clauses read mean errors of -0.000304, -0.000046, 0.003965, 0.000531 with paired sds of 0.001084, 0.000508, 0.002020, 0.000456 — against ceilings of 0.01 on both. The same worlds, the same seeds, the same estimates: only the thing they are compared to changed.

**And #93b's own worked example needed checking.** The adjudication reasoned that about 60 replicates would have made R02 reliable at nominal scoring. Swept directly on this skeleton, the probability that the nominal clause lands under its ceiling reads 8 → 0.267, 16 → 0.136, 30 → 0.056, 60 → 0.011. It FALLS with the budget, because a sample sd concentrates on the quantity it estimates and that quantity — the target's own draw sd, 0.0172 — is above the ceiling on this skeleton. More replicates would have made the nominal clause more reliably UNINFORMATIVE, not less. The paired repair is not one option among several for this clause; it is the only one that works.

**The paired budget, derived rather than inherited.** With X-M's measured paired sd of 0.002019 on its widest clause, 8 replicates put the sd ceiling 5.0x away and the mean ceiling 14 standard errors away; the chance of breaching the sd ceiling by replicate noise alone is bounded above by 10^-31.

**One paired clause carries a real bias, and paired scoring is what makes it legible.** The author main in `{full}` has a paired mean error of 0.003965 against a standard error of 0.000714 — inside the registered 0.01 resolution, and therefore a PASS, but not noise. It has a name and a measured value elsewhere in this same battery: the interaction's bleed into the author coefficient reads 0.00395 in `{g-only}`, the largest of the six zero-point rows. The two agree to the fifth decimal, which is the df derivation's `popvar(M_a·g)` term appearing twice: once as leakage in a world with no author effect, once as bias in a world that has one. Nominal scoring hid it inside a replicate spread six times its size.

**The effective-sample disclosure (#93c) is where the whole episode came from.** The size-weighted community main runs on an effective 43.3 communities of a nominal 1,000 — 4.3% — and every table in this report that prints the nominal count now prints the effective one beside it.

**The first true main budget of this design.** The author main reads 0.1286 [0.1230, 0.1357] and the size-weighted community main 0.0552 [0.0523, 0.0596], as shares of comment-level Var(y) on the eligible shared grid. X1c's 2x2-inversion annotations, promoted to predictions by the X-M registration, score author MISS (predicted 0.150, read 0.1286); community MISS (predicted 0.077, read 0.0552).

**Both predictions miss, and they miss by almost exactly the same amount.** The author gap is -0.0214 and the community gap -0.0218 — a difference between the two of 0.00041. X1c's 2x2 inversion was an algebraic annotation on contaminated rows, and it over-corrected both mains by about two variance points in the same direction. That is a property of the inversion, not of either main, and it is reported here rather than smoothed: a prediction that breaks the same way twice is more informative than one that breaks once.

**And the weighting choice is doing the work on the community side.** The registered PRIMARY community main is size-weighted and reads 0.0552; the UNWEIGHTED secondary reads 0.0786, which lands 0.0016 from the predicted 0.077. The registration named the size-weighted reading as primary before the run and that is what routes and what is scored; the coincidence on the secondary is recorded as an observation about the weighting, with no claim attached. On a design whose size-weighted community side has an effective sample of 43.3, the two weightings are not estimating a common number, and which one a downstream leg wants is a question that has to be asked deliberately.

## Leg lineage

- M4-X1 (`A1_STOP__SYNTHETIC_GATE_FAILED`, commit ebe4f5b) — the venue response, first registration; double-centering's zero was not zero on an incomplete grid (defect #85).
- M4-X1b (`A1_STOP__SYNTHETIC_GATE_FAILED`, commit e8c9040) — design and estimator repaired (law vocabulary + support floor; exact two-way FE by alternating projections); routing machinery certified, stopped again on a descriptive whose bias was design-predicted (defect #86).
- M4-X1c (`RESPONSE_TRACE`, adjudicated) — the corpus reading, with the two main rows correctly renamed MARGINAL and #87 purchased: any leg wanting the mains as OBJECTS must first build main ESTIMATORS under their own gate.
- M4-X-M (`INSTRUMENT_DEFECT`, commit 3ee385d) — the estimator built and 9/10 routing clauses passed; R02 read UNINFORMATIVE because a #90 ceiling on a world-limited clause charges the instrument for the world's own draw noise (P(informative) = 0.267 for ANY correct estimator). Defect #93 purchased.
- M4-X-Mb (this leg) — the same estimator, the same worlds, the same seeds, the same six inherited routing clauses and the same three descriptives. GATE ARITHMETIC ONLY: #93a paired scoring, #93c effective samples, #93b a derived replicate budget, and the #93 dev-prototype note enforced by a stamp the real arm cannot bypass.

## Preconditions

| gate | status |
| --- | --- |
| Inherited census anchors (#78: 17,640,062 parseable rows / 10,296 authors / 1,443 law communities and three more) | **PASS** |
| Predicate-chain census (#78: s = 3/5/8 exact; 0 singleton communities and LCC 1.000 at s = 5) | **PASS** |
| LCC assertion (the alternating projection is exact, and the coefficient gauge is one-dimensional, only on a connected design) | **PASS** |
| Mains gate — ROUTING clauses, PAIRED (#93a; A1 stop on any failure; the real arm is forbidden unless every one passes) | **PASS** |
| Mains gate — DESCRIPTIVE clauses (the X1c interaction echo; annotate, never stop) | **PASS** |
| Certification precedes the real arm (#93 dev-prototype note; asserted from the artifacts' own timestamps) | **PASS** |
| ID-leak scan (0 NEW hits of 10,296 author names over the committed files; 4 pre-existing dictionary collisions carried unchanged from HEAD) | **PASS** |

### The predicate-chain census (#78, BLOCKING)

| support floor s | authors | communities | shared pairs | singleton communities | LCC author coverage |
| --- | --- | --- | --- | --- | --- |
| s = 3 | 3,686 | 1,145 | 32,415 | 1 | 1.000 |
| s = 5 | 3,665 | 1,000 | 31,899 | 0 | 1.000 |
| s = 8 | 3,595 | 780 | 30,561 | 0 | 1.000 |

The primary skeleton is the `s = 5` row, at `n_min = 10` cells; every number in this report is a function of it and of X1's committed cell cache. The skeleton, the estimator, the normalization, the worlds and the seeds are X-M's, unchanged.

## What X-Mb changes, and what it does not

| element | X-M | X-Mb |
| --- | --- | --- |
| skeleton, estimator, pinned normalization | the certified ones | **identical** (imported by file, contract-tested) |
| worlds, seeds, replicate count | 5 worlds, offsets 13/19/23/7/0, 8 replicates | **identical** |
| own-recovery scoring (R01–R04) | replicate mean vs the NOMINAL planted share | **PAIRED**: each replicate vs ITS OWN realized planted component (#93a) |
| own-recovery ceilings | replicate sd ≤ 0.01, gap ≤ max(0.01, 3×sd) | paired sd ≤ 0.01 AND \|paired mean error\| ≤ 0.01 |
| cross-leakage, bootstrap-zero, bootstrap-stability (R05–R10) | 6 clauses | **inherited verbatim** |
| interaction echo (D01–D03) | 3 descriptive clauses | **inherited verbatim** |
| effective samples | named in the diagnosis | **published beside every nominal count** (#93c) |
| replicate budget | inherited from X1b | **derived and printed** (#93b) |
| real-arm access | source order | **a certification stamp the real arm cannot bypass**, order asserted from artifacts (#93 note) |

| clause | X-M (nominal) | X-Mb (paired) | moved | nominal replicate sd | paired replicate sd | ratio |
| --- | --- | --- | --- | --- | --- | --- |
| a_only:author | **PASS** | **PASS** | no | 0.0036 | 0.001084 | 3.4x |
| b_only:community | **UNINFORMATIVE** | **PASS** | yes | 0.0157 | 0.000508 | 30.9x |
| full:author | **PASS** | **PASS** | no | 0.0061 | 0.002020 | 3.0x |
| full:community | **PASS** | **PASS** | no | 0.0072 | 0.000456 | 15.7x |

THE OBJECT.  X1's world builder draws the component vectors first and in a fixed order -- a (authors), then b (communities), then g (cells) -- and skips the draw entirely when a share is zero, so the stream is reproducible from the replicate's seed alone.  The REALIZED planted component of a replicate is then the ESTIMATOR'S OWN FUNCTIONAL applied to the vector that was actually drawn: the unweighted population variance of a for the author main, the W-weighted population variance of b for the size-weighted community main, each divided by the same realized comment-level Var(y) the estimator divides by, and each carrying the same mean-removal factor the estimator carries.  Scoring against it asks 'did the estimator find the world it was given', which is the question a #90 ceiling is entitled to ask; scoring against the NOMINAL share asks 'was the world it was given the world we asked for', which is a property of the draw and not of the instrument.

## The gate — PAIRED and NOMINAL, side by side

#93a PAIRED: every own-recovery clause is scored replicate by replicate against ITS OWN realized planted component (the estimator's functional applied to the drawn vector, over the same realized Var(y)); ROUTING requires paired |mean error| <= 0.01 AND paired replicate sd <= 0.01. The NOMINAL reading X-M routed on is co-reported with its derived P(informative). Clauses R05-R10 and D01-D03 are X-M's, unchanged.

### ROUTING clauses (A1-stopping)

| clause | status |
| --- | --- |
| (R01) recovery, PAIRED (#93a) in {a-only}: author .30 — the author main tracks each replicate's OWN realized planted component: paired |mean error| <= 0.01 AND paired replicate sd <= 0.01, share units (#92 resolution, #90 ceiling — now on the ESTIMATOR) | **PASS** |
| (R02) recovery, PAIRED (#93a) in {b-only}: community .08 — the community main tracks each replicate's OWN realized planted component: paired |mean error| <= 0.01 AND paired replicate sd <= 0.01, share units (#92 resolution, #90 ceiling — now on the ESTIMATOR) | **PASS** |
| (R03) recovery, PAIRED (#93a) in {full}: .30 / .08 / .02 — the author main tracks each replicate's OWN realized planted component: paired |mean error| <= 0.01 AND paired replicate sd <= 0.01, share units (#92 resolution, #90 ceiling — now on the ESTIMATOR) | **PASS** |
| (R04) recovery, PAIRED (#93a) in {full}: .30 / .08 / .02 — the community main tracks each replicate's OWN realized planted component: paired |mean error| <= 0.01 AND paired replicate sd <= 0.01, share units (#92 resolution, #90 ceiling — now on the ESTIMATOR) | **PASS** |
| (R05) cross-leakage — in {a-only}: author .30 every zero-planted component (community, interaction) reads < 0.005 absolute (#85 zero-point family, mains) | **PASS** |
| (R06) cross-leakage — in {b-only}: community .08 every zero-planted component (author, interaction) reads < 0.005 absolute (#85 zero-point family, mains) | **PASS** |
| (R07) cross-leakage — in {g-only}: interaction .02 every zero-planted component (author, community) reads < 0.005 absolute (#85 zero-point family, mains) | **PASS** |
| (R08) cross-leakage — in {null}: nothing every zero-planted component (author, community, interaction) reads < 0.005 absolute (#85 zero-point family, mains) | **PASS** |
| (R09) #85b bootstrap-zero — in {null}: nothing the cluster-bootstrap CI covers 0 for BOTH mains | **PASS** |
| (R10) bootstrap-stability — the author-resampled bootstrap does not move the zero: the CI covers 0 AND its own point, both mains | **PASS** |

**10 of 10 routing clauses passed → routing status `PASS`.**

### Own-component recovery — the two scorings on the same replicates

| clause | world | component | PAIRED mean error | PAIRED sd | PAIRED status | NOMINAL gap | NOMINAL sd | NOMINAL status | NOMINAL P(informative) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R01 | {a-only}: author .30 | author | -0.000304 | 0.001084 | **PASS** | 0.0002 | 0.0036 | **PASS** | 0.954 |
| R02 | {b-only}: community .08 | community | -0.000046 | 0.000508 | **PASS** | 0.0036 | 0.0157 | **UNINFORMATIVE** | 0.267 |
| R03 | {full}: .30 / .08 / .02 | author | 0.003965 | 0.002020 | **PASS** | 0.0012 | 0.0061 | **PASS** | 0.954 |
| R04 | {full}: .30 / .08 / .02 | community | 0.000531 | 0.000456 | **PASS** | -0.0084 | 0.0072 | **PASS** | 0.267 |

`P(informative)` is the closed-form reliability of the NOMINAL reading, computed from the design alone: the realized weighted population variance of an iid component moves draw to draw with `sd ≈ V·sqrt(2·Σ p_i²)`, and the column reports how often a sample sd formed from 8 replicates of that quantity lands under the ceiling. It is a property of the WORLDS and of the weights — no estimator appears in it.

| clause | realized target, mean | realized target, sd | nominal target | max abs paired error | se of paired mean |
| --- | --- | --- | --- | --- | --- |
| a_only:author | 0.3005 | 0.0036 | 0.3000 | 0.002010 | 0.000383 |
| b_only:community | 0.0836 | 0.0154 | 0.0800 | 0.000822 | 0.000180 |
| full:author | 0.2973 | 0.0070 | 0.3000 | 0.007182 | 0.000714 |
| full:community | 0.0711 | 0.0069 | 0.0800 | 0.000962 | 0.000161 |

Corrected scale routes; the raw scale is co-reported (#67). Both the estimate and the realized target carry the SAME constant mean-removal factor on a fixed skeleton, so the paired error on the corrected scale is exactly the raw paired error times that factor — the routing decision is scale-invariant here, which is a property worth stating rather than a coincidence worth hiding:

| clause | paired mean error, RAW | paired sd, RAW | realized target, RAW |
| --- | --- | --- | --- |
| a_only:author | -0.000304 | 0.001084 | 0.3004 |
| b_only:community | -0.000045 | 0.000496 | 0.0817 |
| full:author | 0.003964 | 0.002019 | 0.2972 |
| full:community | 0.000519 | 0.000445 | 0.0695 |

## Effective samples (#93c)

#93c.  A covariance over 1,000 communities whose weights concentrate on a few dozen is not a covariance over 1,000 anything.  The effective sample of a weighted estimand is 1 / sum_i p_i^2 with p the NORMALIZED weights — the same sum_i p_i^2 that sets the mean-removal factor, so the two columns below are one quantity read twice.  Every weighted row this leg reports publishes it beside its nominal count.

| estimand row | weighting | nominal members | `Σ p²` | EFFECTIVE members | effective / nominal | mean-removal factor |
| --- | --- | --- | --- | --- | --- | --- |
| R02 / R04 — community main, size-weighted (PRIMARY) | analysis-pool comment counts (X1c's convention) | 1,000 | 0.023120 | 43.3 | 0.0433 | 1.023667 |
| R01 / R03 — author main | unweighted over the component's authors | 3,665 | 0.000273 | 3665.0 | 1.0000 | 1.000273 |
| secondary — community main, unweighted | unweighted over the component's communities | 1,000 | 0.001000 | 1000.0 | 1.0000 | 1.001001 |
| (contrast) X1c's interaction — residual df, not a weighting | cells of the shared grid | 31,899 | — | 27235.0 | 0.8538 | 1.171250 |

On the REAL skeleton, the same disclosure for the corpus reading:

| side | nominal | effective |
| --- | --- | --- |
| authors | 3,665 | 3665.0 |
| communities (size-weighted) | 1,000 | 43.3 |

## The replicate budget, derived (#93b)

#93b: the budget is DERIVED from the design and from X-M's measured paired sd before the gate is read, and printed here rather than asserted.

**Prior.** X-M's committed artifact results/m4_xm_mains_estimator/part0_mains_gate.json, diagnostics.paired_error.b_only.community.sd_error -- the clause whose NOMINAL scoring stopped X-M. The measured paired sds are `a_only:author` 0.001084, `b_only:community` 0.000496, `full:author` 0.002019, `full:community` 0.000445; the registration's pin of 0.000496 agrees with the stopping clause's measured value.

**Paired side, closed form.** With `R` replicates and a paired error sd of `σ`, the sample sd obeys `(R−1)·s²/σ² ~ χ²_{R−1}`, so the clause breaches its ceiling only if that chi-square exceeds `(R−1)·(ceiling/σ)²`.

| quantity | value |
| --- | --- |
| replicates R | 8 |
| paired sd σ (worst X-M clause) | 0.002019 |
| ceiling / σ | 5.0x |
| χ² threshold at df = 7 | 171.7 |
| log10 upper bound on P(sd ceiling breached) | -30.9 |
| se of the paired mean | 0.000714 |
| mean ceiling, in standard errors | 14 |

**Conclusion.** 8 replicates suffice: the paired sd would have to exceed its expectation by 5.0x for the sd ceiling to bind, and the mean ceiling sits 14 standard errors from zero.

**Nominal side, simulated — and this is where #93b's worked example does not survive contact with the design.**

| replicates | mean replicate sd | P(replicate sd ≤ ceiling) |
| --- | --- | --- |
| 8 | 0.0141 | 0.267 |
| 16 | 0.0147 | 0.136 |
| 30 | 0.0150 | 0.056 |
| 60 | 0.0152 | 0.011 |

MORE replicates do not rescue the NOMINAL clause. A sample sd concentrates on the quantity it estimates, and that quantity is the target's own draw sd, which is above the ceiling on this skeleton; so P(informative) falls toward 0 as the budget grows instead of rising. #93b's worked example (about 60 replicates would have made R02 reliable at nominal scoring) does not hold for a ceiling read on the replicate SD — it would hold for a ceiling read on the standard ERROR of the replicate mean, which shrinks as 1/sqrt(R). The paired repair is not one option among several here; for this clause it is the only one that works.

## The inherited clauses (X-M verbatim)

### Cross-leakage — the #85 zero-point family, for mains

| world | zero-planted component | reading | maximum | status |
| --- | --- | --- | --- | --- |
| {a-only}: author .30 | community | -0.00002 | 0.005 | **PASS** |
| {a-only}: author .30 | interaction | -0.00008 | 0.005 | **PASS** |
| {b-only}: community .08 | author | 0.00004 | 0.005 | **PASS** |
| {b-only}: community .08 | interaction | 0.00010 | 0.005 | **PASS** |
| {g-only}: interaction .02 | author | 0.00395 | 0.005 | **PASS** |
| {g-only}: interaction .02 | community | 0.00065 | 0.005 | **PASS** |
| {null}: nothing | author | -0.00002 | 0.005 | **PASS** |
| {null}: nothing | community | 0.00000 | 0.005 | **PASS** |
| {null}: nothing | interaction | 0.00005 | 0.005 | **PASS** |
| {full}: .30 / .08 / .02 | — | — | — | **N/A** (every component is planted in this world, so the zero-point clause has no zero to test) |

Scored against the same 0.005 bound, the FE mains pass all 6 zero-point rows and X1c's MARGINAL estimators fail 3 of them (a_only:community, b_only:author, g_only:author) — #87's diagnosis as a measurement, carried forward unchanged.

### The null world's bootstrap

| main | point | CI (corrected) | CI (raw, #67) | covers 0 | covers own point |
| --- | --- | --- | --- | --- | --- |
| author | 0.00016 | [-0.00011, 0.00044] | [-0.00011, 0.00044] | yes | yes |
| community | -0.00001 | [-0.00017, 0.00011] | [-0.00016, 0.00011] | yes | yes |

### DESCRIPTIVE clauses (annotate, never stop)

| clause | status |
| --- | --- |
| (D01) interaction echo — X1c's df-corrected estimator recovers 0.0200 in {g-only}: interaction .02 | **PASS** |
| (D02) interaction echo — X1c's df-corrected estimator recovers 0.0200 in {full}: .30 / .08 / .02 | **PASS** |
| (D03) interaction echo — X1c's estimator reads < 0.005 in the three worlds with no planted interaction | **PASS** |

| world | interaction target | recovered mean (df-corrected) | gap | replicate sd |
| --- | --- | --- | --- | --- |
| {g-only}: interaction .02 | 0.0200 | 0.0199 | -0.0001 | 0.0004 |
| {full}: .30 / .08 / .02 | 0.0200 | 0.0199 | -0.0001 | 0.0005 |
| {a-only}: author .30 | 0.0000 | -0.00008 | -0.00008 | — |
| {b-only}: community .08 | 0.0000 | 0.00010 | 0.00010 | — |
| {null}: nothing | 0.0000 | 0.00005 | 0.00005 | — |

### The gauge factors on the realized skeleton

| reading | members | `Σ p²` | effective members | factor |
| --- | --- | --- | --- | --- |
| author main | 3,665 | 0.000273 | 3665.0 | 1.000273 |
| community main, size-weighted (PRIMARY) | 1,000 | 0.023120 | 43.3 | 1.023667 |
| community main, unweighted (secondary) | 1,000 | 0.001000 | 1000.0 | 1.001001 |
| *(contrast)* X1c's INTERACTION factor `P/(P − A − C + 1)` | P = 31,899 | — | 27,235 | 1.171250 |

The mains carry NO residual-df shrinkage — X-M derived it, printed it and contract-tested it, and this leg inherits the derivation with the estimator.

## The certification stamp and the gated real arm (#93 note)

#93 note, enforced in code rather than by restraint: a development prototype never touches the real arm before certification. In this leg the real arm is unreachable except through ``run_real_arm``, which refuses any certificate whose cell is not MAINS_CERTIFIED and whose stamp is not already on disk; the stamp carries both a UTC instant and a monotonic counter, the real arm records its own, and ``certification_order.json`` asserts the order from the artifacts.

| field | value |
| --- | --- |
| certificate cell | **MAINS_CERTIFIED** |
| certified | yes |
| stamped (UTC) | `2026-08-21T03:09:00.868231Z` |
| real arm started (UTC) | `2026-08-21T03:09:00.868796Z` |
| monotonic delta (ns) | 561,375 |
| order assertion | **PASS** |

the certification stamp was written to disk before the real arm formed its first corpus estimand; the order is asserted from the artifacts, not from the order the source happens to read in.

## The corpus main budget

Every routing clause passed, the certificate was stamped, and the real arm ran ONCE through the gated path — the first TRUE main budget of this design, superseding X1c's marginal-annotated reading as the interpretable one (X1c's rows remain valid under their marginal name).

| component | share (corrected) | CI | share (raw, #67) | CI (raw) | gauge factor |
| --- | --- | --- | --- | --- | --- |
| author main `Var_hat(a)` | 0.1286 | [0.1230, 0.1357] | 0.1286 | [0.1229, 0.1356] | 1.000273 |
| community main `Var_hat(b)`, size-weighted | 0.0552 | [0.0523, 0.0596] | 0.0539 | [0.0510, 0.0582] | 1.023667 |
| community main, unweighted (secondary) | 0.0786 | [0.0772, 0.0854] | 0.0786 | [0.0771, 0.0853] | 1.001001 |
| interaction (X1c's estimand, df-corrected) | 0.0190 | — | 0.0162 | — | 1.171250 |
| residual | 0.7972 | — | — | — | — |

Bootstrap: cluster over authors, `B = 1,000`, the FE refitted and the coefficients re-normalized inside every replicate, and the gauge factor recomputed from each replicate's own weights (#87(b) treatment one — the factor is RECOMPUTED from each bootstrap replicate's own weights, not pinned at the realized design).

For contrast, X1c's MARGINAL rows on the same skeleton read author 0.1804 and community 0.0928 — the difference between them and the mains above is the contamination the projection removes, which the zero-point battery measured on synthetic worlds and which appears here at corpus scale.

### The registered predictions, scored

| prediction | value | realized point | realized CI | result |
| --- | --- | --- | --- | --- |
| author main | 0.1500 | 0.1286 | [0.1230, 0.1357] | **MISS** |
| community main | 0.0770 | 0.0552 | [0.0523, 0.0596] | **MISS** |

Source of the predictions: X1c's 2x2-inversion ANNOTATION on the marginal rows (implied author main 0.1526, implied community main 0.0767), promoted to a testable prediction by the X-M registration.

## Registered leans

| lean | registered | observed | status |
| --- | --- | --- | --- |
| certification PASSES | PASS | PASS | **HELD** |
| real author main in [0.1, 0.2] | [0.1, 0.2] | 0.1286 | **HELD** |
| real community main in [0.05, 0.11] | [0.05, 0.11] | 0.0552 | **HELD** |

## Deviations and anomalies, all recorded

- **No permutation null was run.** `B_perm = 499` is registered 'where applicable'; every X-Mb clause is a recovery, a leakage bound or a bootstrap statement.
- **The paired block reuses the gate's own per-replicate estimates.** X-M's diagnostic paired block re-drew each world and recomputed the estimator; this leg reads the per-replicate values the scored block already stored and computes only the realized target, so the pairing is bit-exact against the replicates the nominal clause read rather than a re-derivation of them. The realized-component reconstruction is contract-tested against a noiseless world where the cell means ARE the drawn components.
- **Paired errors route on the corrected scale, raw co-reported (#67).** On a fixed skeleton the estimate and the realized target carry the same constant mean-removal factor, so the corrected paired error is exactly the raw one times that factor and the routing decision is scale-invariant; the identity is contract-tested.
- **#93b's worked example is corrected in-leg.** The adjudication's 'about 60 replicates' would not have rescued the nominal clause: swept on this skeleton, P(informative) FALLS with the replicate budget. The correction is reported as a measurement, and the paired budget is derived separately and holds.
- **The {full} author clause passes with a bias, not with noise.** Its paired mean error is several standard errors from zero and matches the interaction's measured bleed into the author coefficient; the clause passes because that bias is inside the registered resolution, and the agreement is reported in the reading above rather than left as a rounding coincidence.
- **Both registered predictions MISS, in the same direction and by nearly the same amount**, and the unweighted community secondary sits close to the community prediction while the registered size-weighted primary does not. The primary was named before the run and is what routes; the secondary's proximity is recorded as an observation with no claim attached.
- **No development prototype touched the real arm.** The #93 note is enforced in code: the real arm is reachable only through `run_real_arm`, which refuses an uncertified or unstamped certificate, and `certification_order.json` asserts from the artifacts that the stamp preceded the first corpus estimand.

## Defect candidates for the planner (nothing below was run)

- **A gate ceiling should declare which VARIANCE it is bounding.** #93a fixed own-recovery clauses by pairing, but the general shape of the mistake is a clause whose statistic mixes estimator error with design-side draw noise. A registration convention could require every ceiling to name the variance component it constrains (estimator / world / both) so the arithmetic is checkable before the run rather than after the stop.
- **A worked example inside an adopted defect deserves the same pre-registration arithmetic as a clause.** #93b's own illustration ('about 60 replicates') was not derived, and it does not hold for the ceiling it illustrates. Convention to consider: an illustrative number in a defect note is either derived in the note or marked explicitly as an unchecked sketch.
- **An own-recovery clause could report its realized target's spread as a routing DIAGNOSTIC.** Paired scoring hides the world variation that made the nominal reading unreliable; publishing the realized target sd beside the paired sd (as this leg's table does) keeps the design's own instability visible rather than differenced away.

## Boundaries

- **Metadata only, expression VOLUME and not content (permanent).** The only text-derived quantity in this leg is `word_count_quoteless`, the author's own-word count per comment. No body was read, no topic, no style, no sentiment; `author_profiles.csv` was never opened.
- **INSTRUMENT LEG, R1-class.** Everything certified here is a property of an ESTIMATOR on a design, not a finding about people or venues. The leg issues certificates, not theory verdicts, and no downstream leg may cite it as evidence for anything about the corpus.
- **No psychological naming.** An author coefficient is a fitted offset in log-words on this eligible grid. It is not a trait, a state, a disposition or a style, and the leg is label-free.
- **EXPLORATORY, corpus-level.** No person-level claim is licensed. The author coefficients exist only as the population a covariance runs over.
- **The mains are estimands OF THIS DESIGN.** Var_hat(a) and Var_hat(b) are defined on the eligible shared grid (well-shared venues, authors with at least three surviving shared communities). They are not population quantities of Reddit, of PANDORA, or of the disjoint cohort.
- **Incomplete design.** The grid is sparse and the community side is size-skewed; the size-weighted community estimand has an EFFECTIVE number of communities far below its nominal count, which is a property of the corpus and is reported rather than repaired.
- **Cohort composition.** The disjoint cohort is TYPOLOGY-ENRICHED by construction, so it is a platform sample with a selection, not a population sample.
- **A certified instrument is still only an instrument.** MAINS_CERTIFIED says the estimator recovers a planted main on this skeleton to the registered resolution. It does not say the corpus main means anything about anybody, and the real budget below is a description of variance on an eligible grid, not a statement about persons or venues.
- **The gate was repaired, not relaxed.** Paired scoring makes the ceiling STRICTER on the estimator (the world's draw noise no longer inflates the spread the clause is compared against) while removing a term the clause was never entitled to charge the instrument for. A clause that passes here would also have passed X-M's nominal ceiling had the worlds been drawn quietly enough.

## Configuration

```json
{
  "author_profiles_opened": false,
  "b_boot": 1000,
  "b_perm_not_used": "B_perm = 499 is registered 'where applicable'; no X-Mb clause is defined against a permutation band",
  "bodies_read": false,
  "ceiling_paired_mean_error": 0.01,
  "ceiling_paired_sd": 0.01,
  "ceiling_replicate_sd_nominal": 0.01,
  "cells": {
    "certified": "MAINS_CERTIFIED",
    "defect": "INSTRUMENT_DEFECT",
    "rule": "MAINS_CERTIFIED iff EVERY routing clause passes; any failure is INSTRUMENT_DEFECT + A1, and the real arm is not run"
  },
  "changed_from_xm": [
    "#93a own-recovery clauses are scored PAIRED against each replicate's own realized planted component; ROUTING ceilings are paired |mean error| <= 0.01 AND paired sd <= 0.01",
    "#93a the NOMINAL reading is co-reported with its derived P(informative) from the closed-form target sd",
    "#93c every weighted estimand row publishes its effective sample beside its nominal one",
    "#93b the replicate budget is derived and printed, on both scorings",
    "#93 note: the real arm is reachable only through a certification stamp written to disk first, and the order is asserted from the artifacts"
  ],
  "class": "R1 (instrument leg; certificates only, no theory verdict)",
  "columns_read": [
    "author",
    "subreddit",
    "created_utc",
    "word_count_quoteless",
    "word_count"
  ],
  "data_source": "X1's committed cell cache results/m4_x1_venue_response/cell_cache.npz (sufficient statistics); the 17.6M-row comments CSV is re-streamed ONLY if the cache is absent",
  "dev_prototype_rule": "#93 note, enforced in code rather than by restraint: a development prototype never touches the real arm before certification. In this leg the real arm is unreachable except through ``run_real_arm``, which refuses any certificate whose cell is not MAINS_CERTIFIED and whose stamp is not already on disk; the stamp carries both a UTC instant and a monotonic counter, the real arm records its own, and ``certification_order.json`` asserts the order from the artifacts.",
  "effective_sample_rule": "#93c.  A covariance over 1,000 communities whose weights concentrate on a few dozen is not a covariance over 1,000 anything.  The effective sample of a weighted estimand is 1 / sum_i p_i^2 with p the NORMALIZED weights \u2014 the same sum_i p_i^2 that sets the mean-removal factor, so the two columns below are one quantity read twice.  Every weighted row this leg reports publishes it beside its nominal count.",
  "fe_tolerance": 1e-10,
  "halves": "author's FULL-STREAM median created_utc, <= to early",
  "k_min": 3,
  "leakage_maximum": 0.005,
  "leans": {
    "certification": "PASS",
    "real_author_main": [
      0.1,
      0.2
    ],
    "real_community_main": [
      0.05,
      0.11
    ]
  },
  "leg": "M4-X-Mb",
  "machinery_imported_by_file": [
    "scripts/run_suica_m4_xm_mains_estimator.py (the mains estimator, the pinned normalization, the df derivation, the five-world gate, the leakage battery, the bootstrap, the descriptive echo)",
    "scripts/run_suica_m4_x1c_venue_response.py (df correction, clause-separated gate status)",
    "scripts/run_suica_m4_x1b_venue_response_fe.py (predicate chain, exact-FE alternating projections, synthetic world builder, cell cache, law vocabulary)",
    "scripts/run_suica_m4_x1_venue_response.py (Design, variance_budget, weighted_cov, #83 helpers)"
  ],
  "n_min_primary": 10,
  "normalization": [
    "1. FIT: alternating projections accumulate (a_acc, c_acc) with y_cell = a_acc[author] + c_acc[community] + v (exact to machine precision; the split is gauge-dependent, the sum is not).",
    "2. CENTRE THE AUTHOR COEFFICIENTS: abar = mean over the connected component's authors of a_acc; a_hat = a_acc - abar; ABSORB the shift, mu <- mu + abar.",
    "3. CENTRE THE COMMUNITY COEFFICIENTS: bbar = mean over the component's communities of c_acc; b_hat = c_acc - bbar; ABSORB the shift, mu <- mu + bbar.",
    "RESULT: y_cell = mu + a_hat[author] + b_hat[community] + v with mean(a_hat) = mean(b_hat) = 0, and (mu, a_hat, b_hat) unchanged by which side the sweep started from."
  ],
  "paired_scoring": "THE OBJECT.  X1's world builder draws the component vectors first and in a fixed order -- a (authors), then b (communities), then g (cells) -- and skips the draw entirely when a share is zero, so the stream is reproducible from the replicate's seed alone.  The REALIZED planted component of a replicate is then the ESTIMATOR'S OWN FUNCTIONAL applied to the vector that was actually drawn: the unweighted population variance of a for the author main, the W-weighted population variance of b for the size-weighted community main, each divided by the same realized comment-level Var(y) the estimator divides by, and each carrying the same mean-removal factor the estimator carries.  Scoring against it asks 'did the estimator find the world it was given', which is the question a #90 ceiling is entitled to ask; scoring against the NOMINAL share asks 'was the world it was given the world we asked for', which is a property of the draw and not of the instrument.",
  "predecessors": [
    "M4-X1 (A1_STOP__SYNTHETIC_GATE_FAILED, commit ebe4f5b)",
    "M4-X1b (A1_STOP__SYNTHETIC_GATE_FAILED, commit e8c9040)",
    "M4-X1c (RESPONSE_TRACE, adjudicated; defect #87)",
    "M4-X-M (INSTRUMENT_DEFECT, commit 3ee385d; defect #93)"
  ],
  "predictions": {
    "author_main": 0.15,
    "community_main": 0.077,
    "source": "X1c's 2x2-inversion ANNOTATION on the marginal rows (implied author main 0.1526, implied community main 0.0767), promoted to a testable prediction by the X-M registration"
  },
  "registration": "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md@e421072 (X-Mb)",
  "replicate_budget_sweep": [
    8,
    16,
    30,
    60
  ],
  "replicate_budget_sweep_trials": 2000,
  "resolution_floor_share": 0.01,
  "role": "the completion of X-M under defect #93: GATE ARITHMETIC ONLY. The estimator, the skeleton, the normalization, the worlds and the seeds are X-M's committed ones",
  "run_utc": "2026-08-21T03:08:49.236780Z",
  "seed": 20260819,
  "seed_boot": 20260822,
  "seed_part0": 20260820,
  "skeleton": "X1c's primary design: law vocabulary (floor 89 users -> 1,443 communities), support floor s = 5, n_min = 10 cells, k_min = 3, largest connected component",
  "support_censused": [
    3,
    5,
    8
  ],
  "support_primary": 5,
  "synthetic_replicates": 8,
  "title": "the mains estimator, paired-scored gate",
  "tolerance_sd_multiple_nominal": 3.0,
  "unchanged_from_xm": [
    "the skeleton and its #78 census",
    "the two-way FE estimator and the pinned normalization",
    "the five worlds, their planted shares and their seed offsets",
    "the 8-replicate budget (now derived rather than inherited)",
    "routing clauses R05-R10 (cross-leakage, bootstrap-zero, bootstrap-stability) and descriptives D01-D03",
    "the df derivation and the gauge factors",
    "the cells, the leans, the predictions and the boundaries"
  ],
  "vocabulary_floor_fraction": 0.01,
  "world_seed_offsets": {
    "a_only": 13,
    "b_only": 19,
    "full": 0,
    "g_only": 23,
    "null": 7
  },
  "worlds": {
    "a_only": {
      "author": 0.3,
      "community": 0.0,
      "interaction": 0.0
    },
    "b_only": {
      "author": 0.0,
      "community": 0.08,
      "interaction": 0.0
    },
    "full": {
      "author": 0.3,
      "community": 0.08,
      "interaction": 0.02
    },
    "g_only": {
      "author": 0.0,
      "community": 0.0,
      "interaction": 0.02
    },
    "null": {
      "author": 0.0,
      "community": 0.0,
      "interaction": 0.0
    }
  },
  "xm_prior_paired_sd": 0.000496,
  "xm_prior_paired_sd_source": "X-M's committed artifact results/m4_xm_mains_estimator/part0_mains_gate.json, diagnostics.paired_error.b_only.community.sd_error -- the clause whose NOMINAL scoring stopped X-M",
  "y": "log(1 + word_count_quoteless)"
}
```

