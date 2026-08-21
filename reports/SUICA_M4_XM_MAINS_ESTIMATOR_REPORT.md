# SUICA M4-X-M — the mains estimator

**VERDICT — INSTRUMENT_DEFECT.** 1 of 10 routing clauses did not pass, the A1 stop fires, and NO real-data main was computed, reported or stored. The instrument is not certified at the registered resolution.

Run (UTC): `2026-08-21T02:37:55.123290Z` · seed `20260819` · B_boot `1000` · runtime 20.0 s · config sha256 `fdd92bd4ef96ad3e…`

## The reading

**The instrument does NOT certify.** 9 of 10 routing clauses passed and the rest did not: `UNINFORMATIVE` on (R02). The A1 stop fires, the real arm was not run, and no corpus main exists in this leg's record. X3 may not take a main from here.

**The failure is the GATE's resolution, not the estimator's accuracy, and the two must not be confused.** The clause that did not pass is the size-weighted community main's own-recovery clause, and it did not FAIL — its gap is 0.0036, comfortably inside any tolerance. It is UNINFORMATIVE: its replicate sd is 0.0157 against a #90 ceiling of 0.0100, so the tolerance it would have been scored at is 0.0470 — the clause claims a resolution of 0.01 and delivers nothing of the kind. #90 exists precisely to refuse that pass.

**And the spread is the WORLDS, not the estimator.** Scored paired — each replicate against its own realized planted target — the same estimator on the same worlds reads a mean error of -0.000045 with sd 0.000496, while the realized target itself moves with sd 0.0150 — 30 times larger. The estimator tracks each world's truth to about half a thousandth of a variance point; what scatters is which truth got drawn.

**The cause is structural and was visible at registration.** The size-weighted community covariance concentrates its weight on an EFFECTIVE 43.3 communities, not the nominal 1,000, so the realized weighted variance of an iid component moves draw to draw with closed-form sd 0.0172. Over 8 replicates the probability that this clause lands under its own ceiling is 0.267. It was underpowered when it was written, and no seed would have changed that.

**A clause that PASSED must be read with the same eye.** The same estimand in {full}: .30 / .08 / .02 drew a replicate sd of 0.0072 and cleared the ceiling with 0.0028 to spare — at a probability of 0.267 of doing so. The same clause reading INFORMATIVE in one world and UNINFORMATIVE in another, on the same estimand and the same skeleton, is not a finding about the two worlds; it is the sharpest available demonstration that this ceiling is being asked a question it cannot answer at this replicate budget.

**What the battery did establish, and it is not nothing.** The author main recovers its plant in both worlds that carry it (gaps 0.0002 and 0.0012) with replicate sds under the ceiling; every one of the 6 zero-point rows reads below 0.005; the null world's bootstrap covers zero and its own point for both mains; and the interaction echo reproduces X1c's estimand to the fourth decimal, which certifies that this leg's fit IS X1c's fit.

**The zero-point clause is the one worth carrying forward.** Both estimators ran on all five worlds. The FE mains pass all 6 zero-point rows; the marginal mains fail 3 of them. The #87 diagnosis is therefore confirmed by measurement: the marginal rows were not a conservative version of the mains, they were contaminated, and the projection is what removes the contamination.

## Leg lineage

- M4-X1 (`A1_STOP__SYNTHETIC_GATE_FAILED`, commit ebe4f5b) — the venue response, first registration; double-centering's zero was not zero on an incomplete grid (defect #85).
- M4-X1b (`A1_STOP__SYNTHETIC_GATE_FAILED`, commit e8c9040) — design and estimator repaired (law vocabulary + support floor; exact two-way FE by alternating projections); routing machinery certified, stopped again on a descriptive whose bias was design-predicted (defect #86).
- M4-X1c (`RESPONSE_TRACE`, adjudicated) — the corpus reading, with the two main rows correctly renamed MARGINAL and #87 purchased: any leg wanting the mains as OBJECTS must first build main ESTIMATORS under their own gate.
- M4-X-M (this leg) — that gate. R1-class, certificates only; the #87 prerequisite for X3's stage-E trait join.

## Preconditions

| gate | status |
| --- | --- |
| Inherited census anchors (#78: 17,640,062 parseable rows / 10,296 authors / 1,443 law communities and three more) | **PASS** |
| Predicate-chain census (#78: s = 3/5/8 exact; 0 singleton communities and LCC 1.000 at s = 5) | **PASS** |
| LCC assertion (the alternating projection is exact, and the coefficient gauge is one-dimensional, only on a connected design) | **PASS** |
| Mains gate — ROUTING clauses (A1 stop on any failure; the real arm is forbidden unless every one passes) | **FAIL** |
| Mains gate — DESCRIPTIVE clauses (the X1c interaction echo; annotate, never stop) | **PASS** |
| ID-leak scan (0 NEW hits of 10,296 author names over the committed files; 4 pre-existing dictionary collisions carried unchanged from HEAD) | **PASS** |

### The predicate-chain census (#78, BLOCKING)

| support floor s | authors | communities | shared pairs | singleton communities | LCC author coverage |
| --- | --- | --- | --- | --- | --- |
| s = 3 | 3,686 | 1,145 | 32,415 | 1 | 1.000 |
| s = 5 | 3,665 | 1,000 | 31,899 | 0 | 1.000 |
| s = 8 | 3,595 | 780 | 30,561 | 0 | 1.000 |

The primary skeleton is the `s = 5` row, at `n_min = 10` cells; every number in this report is a function of it and of X1's committed cell cache.

## The estimator, and the normalization that identifies it

Per half, on the eligible shared cells of the primary skeleton, the exact two-way fixed-effect fit by alternating projections (X1b's machinery, imported by file; X1b's tightened stopping rule: BOTH residual group means at most `1e-10` on exit). The fit is a projection, so its coefficients are identified only up to the gauge `a -> a + t`, `b -> b - t`. The registration pins the normalization; the pinned sequence, as executed:

1. FIT: alternating projections accumulate (a_acc, c_acc) with y_cell = a_acc[author] + c_acc[community] + v (exact to machine precision; the split is gauge-dependent, the sum is not).
2. CENTRE THE AUTHOR COEFFICIENTS: abar = mean over the connected component's authors of a_acc; a_hat = a_acc - abar; ABSORB the shift, mu <- mu + abar.
3. CENTRE THE COMMUNITY COEFFICIENTS: bbar = mean over the component's communities of c_acc; b_hat = c_acc - bbar; ABSORB the shift, mu <- mu + bbar.

RESULT: y_cell = mu + a_hat[author] + b_hat[community] + v with mean(a_hat) = mean(b_hat) = 0, and (mu, a_hat, b_hat) unchanged by which side the sweep started from.

The two centrings act on disjoint vectors and both dump their shift into the same scalar intercept, so the sequence is confluent: step 3 cannot undo step 2, and the normalized coefficients do not depend on which side the sweep started from. That invariance is a contract test, not a remark — a normalization whose answer depended on its own order would identify nothing.

The two estimands are then CROSS-HALF covariances of the normalized coefficient vectors, reported as shares of comment-level `Var(y)` over the analysis pool:

| estimand | definition | weighting |
| --- | --- | --- |
| `Var_hat(a)` | covariance over the component's authors of `(a_hat_early, a_hat_late)` | unweighted (real sample); author multiplicity inside a bootstrap replicate |
| `Var_hat(b)` PRIMARY | covariance over the component's communities of `(b_hat_early, b_hat_late)` | size-weighted, weights = analysis-pool comment counts (X1c's convention) |
| `Var_hat(b)` secondary | the same covariance | unweighted |

The cross-half form is what makes these ESTIMATORS rather than variance decompositions. The two halves' estimation errors are unlinked given the design, so the coefficients' own sampling noise cancels in expectation instead of inflating the reading — the same property that lets X1c's interaction share be attenuation-free, now applied one level up.

## The df / joint-estimation derivation (derived, printed, contract-tested)

THE QUESTION.  X1c's routing statistic needed the factor P/(P - A - C + 1): the two-way projection removes a rank-(A + C - 1) dummy space from the P cell observations of a half, so a white interaction keeps only (P - A - C + 1)/P of itself IN THE RESIDUAL.  Does the same shrinkage hit the mains?

THE ANSWER: NO, and for a structural reason.  The mains are the projection's COORDINATES, not its residual.  Writing the fit as the linear map a_hat_h = M_a y_h with the SAME M_a in both halves (the design is shared -- a slot is eligible in both halves by construction), and the model as y = mu + a[u] + b[c] + g + e_h with e_h unlinked across halves: M_a is unbiased on the fitted part, so a_hat_h = (a - abar) + M_a g + M_a e_h.  The cross-half covariance kills every term that is not shared: E[cov(a_hat_e, a_hat_l)] = popvar(a - abar) + popvar(M_a g).  No noise inflation (the two halves' estimation errors are unlinked), and no residual-df shrinkage (the estimand never enters the residual).  The second term is not a df effect at all -- it is the interaction LEAKAGE that routing clause (2) measures and bounds.

WHAT REMAINS: the MEAN-REMOVAL (gauge) loss, one dimension per side.  Every reading here is a weighted POPULATION covariance with normalized weights p, and such a covariance subtracts its own weighted mean, so for an iid component of variance V it targets V * (1 - sum_i p_i^2).  The correction is therefore ONE formula for all three readings:

    factor(p) = 1 / (1 - sum_i p_i^2),   share_corr = share_raw * factor(p).

  * author main, real sample: p_u = 1/A     -> factor = A/(A - 1);

  * author main, bootstrap:   p_u = m_u / sum m  (author multiplicities);

  * community main, size-weighted (PRIMARY): p_c = W_c = (n_{c,early} + n_{c,late}) / sum_c(...);

  * community main, unweighted (secondary):  p_c = 1/C -> C/(C - 1).

The factor is a positive scalar, so the corrected CI is the affine image of the raw CI and 'the CI covers 0' is invariant -- the bootstrap-zero clauses are untouched by the correction.  Per #87(b) the factor is RECOMPUTED INSIDE every bootstrap replicate from that replicate's own weights, not pinned at the realized design; the raw reading is co-reported everywhere (#67).

A CONSEQUENCE WORTH NAMING.  sum_c W_c^2 is the inverse of the size-weighted design's EFFECTIVE NUMBER OF COMMUNITIES.  A small effective number makes the correction large AND makes the estimand's own draw-to-draw variability large -- which is what routing clause (1) runs into on this skeleton.

On the realized skeleton:

| reading | members | `sum p^2` | effective members | retained | factor |
| --- | --- | --- | --- | --- | --- |
| author main | 3,665 | 0.000273 | 3665.0 | 0.999727 | 1.000273 |
| community main, size-weighted (PRIMARY) | 1,000 | 0.023120 | 43.3 | 0.976880 | 1.023667 |
| community main, unweighted (secondary) | 1,000 | 0.001000 | 1000.0 | 0.999000 | 1.001001 |
| *(contrast)* X1c's INTERACTION factor `P/(P - A - C + 1)` | P = 31,899 | — | — | 0.853789 | 1.171250 |

The contrast is the point of the derivation: the interaction loses 0.1462 of itself to the projection because it lives IN the residual, while the author main loses only 0.000273 to its own mean removal. The size-weighted community main loses 0.023120 — over 85x the author side — because its effective number of communities is 43.3, not 1,000.

## The gate — the leg IS the battery

Five wholly synthetic worlds on the REALIZED skeleton, 8 replicates each, cell sufficient statistics drawn exactly (cell mean `~ N(mu, sigma^2/n)`, within-cell SS `~ sigma^2 chi^2_{n-1}`). floor = 0.01 in SHARE units (#92: a resolution statement in the estimand's own units, not a fraction of a freely chosen planted scale); tolerance = max(floor, 3 x replicate sd) over 8 replicates; #90 ceiling = the same 0.01 read as an upper bound on that replicate sd, above which the clause is UNINFORMATIVE and stops the leg

### ROUTING clauses (A1-stopping)

| clause | status |
| --- | --- |
| (R01) recovery — author main in {a-only}: author .30 within max(0.01, 3 x replicate sd) of 0.3000, replicate sd <= 0.01 (#90 ceiling / #92 resolution) | **PASS** |
| (R02) recovery — community main in {b-only}: community .08 within max(0.01, 3 x replicate sd) of 0.0800, replicate sd <= 0.01 (#90 ceiling / #92 resolution) | **UNINFORMATIVE** |
| (R03) recovery — author main in {full}: .30 / .08 / .02 within max(0.01, 3 x replicate sd) of 0.3000, replicate sd <= 0.01 (#90 ceiling / #92 resolution) | **PASS** |
| (R04) recovery — community main in {full}: .30 / .08 / .02 within max(0.01, 3 x replicate sd) of 0.0800, replicate sd <= 0.01 (#90 ceiling / #92 resolution) | **PASS** |
| (R05) cross-leakage — in {a-only}: author .30 every zero-planted component (community, interaction) reads < 0.005 absolute (#85 zero-point family, mains) | **PASS** |
| (R06) cross-leakage — in {b-only}: community .08 every zero-planted component (author, interaction) reads < 0.005 absolute (#85 zero-point family, mains) | **PASS** |
| (R07) cross-leakage — in {g-only}: interaction .02 every zero-planted component (author, community) reads < 0.005 absolute (#85 zero-point family, mains) | **PASS** |
| (R08) cross-leakage — in {null}: nothing every zero-planted component (author, community, interaction) reads < 0.005 absolute (#85 zero-point family, mains) | **PASS** |
| (R09) #85b bootstrap-zero — in {null}: nothing the cluster-bootstrap CI covers 0 for BOTH mains | **PASS** |
| (R10) bootstrap-stability — the author-resampled bootstrap does not move the zero: the CI covers 0 AND its own point, both mains | **PASS** |

**9 of 10 routing clauses passed → routing status `FAIL`.**

### Own-component recovery, scored

| world | component | target | recovered mean | gap | replicate sd | tolerance | #90 ceiling headroom | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {a-only}: author .30 | author | 0.3000 | 0.3002 | 0.0002 | 0.0036 | 0.0109 | 0.0064 | **PASS** |
| {b-only}: community .08 | community | 0.0800 | 0.0836 | 0.0036 | 0.0157 | 0.0470 | -0.0057 | **UNINFORMATIVE** |
| {full}: .30 / .08 / .02 | author | 0.3000 | 0.3012 | 0.0012 | 0.0061 | 0.0183 | 0.0039 | **PASS** |
| {full}: .30 / .08 / .02 | community | 0.0800 | 0.0716 | -0.0084 | 0.0072 | 0.0215 | 0.0028 | **PASS** |

Corrected scale routes; the raw scale is co-reported (#67):

| world | component | recovered mean, RAW | gap, RAW | replicate sd, RAW |
| --- | --- | --- | --- | --- |
| {a-only}: author .30 | author | 0.3001 | 0.0001 | 0.0036 |
| {b-only}: community .08 | community | 0.0817 | 0.0017 | 0.0153 |
| {full}: .30 / .08 / .02 | author | 0.3011 | 0.0011 | 0.0061 |
| {full}: .30 / .08 / .02 | community | 0.0700 | -0.0100 | 0.0070 |

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

**This is the clause X1's marginal estimators would have failed.** An author's half-mean carries that author's own composition average of the community main and of the interaction, identically in both halves, and a cross-half covariance is defenceless against anything shared. Both estimators were run on every one of these worlds, so the contrast is measured rather than argued:

| world | author: FE main | author: X1c MARGINAL | community: FE main | community: X1c MARGINAL |
| --- | --- | --- | --- | --- |
| {a-only}: author .30 | 0.30019 | 0.30015 | -0.00002 | 0.02628 |
| {b-only}: community .08 | 0.00004 | 0.02247 | 0.08360 | 0.08170 |
| {g-only}: interaction .02 | 0.00395 | 0.00567 | 0.00065 | 0.00186 |
| {null}: nothing | -0.00002 | 0.00001 | 0.00000 | 0.00000 |
| {full}: .30 / .08 / .02 | 0.30122 | 0.32197 | 0.07164 | 0.10716 |

Scored against the same 0.005 bound, the FE mains pass all 6 zero-point rows and the marginal mains fail 3 of them (a_only:community, b_only:author, g_only:author). The projection removes the community effects before the author coefficient is formed, and the author effects before the community coefficient is formed; the half-mean does neither.

### The null world's bootstrap

Cluster bootstrap over authors, `B = 1,000`, the FE REFITTED and the coefficients RE-NORMALIZED inside every replicate, and (per #87b) the mean-removal factor recomputed from each replicate's own weights.

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

The echo is a consistency check on the WHOLE fit: the same alternating projection that produces the coefficients produces the residual X1c reads, so an interaction that stopped reproducing here would mean this leg's fit is not X1c's fit.

## Diagnostics (non-routing)

### Is the replicate spread the ESTIMATOR, or the WORLDS?

`score_recovery` compares the replicate MEAN to the NOMINAL planted share, so its replicate spread mixes two different questions: how far the estimator is from the truth, and how far each drawn world's realized truth is from its nominal parameter. The paired block below separates them — same worlds, same seeds, each replicate scored against ITS OWN realized target (the same functional of the drawn component vector that the estimator targets), on the raw scale.

| world | main | mean paired error | sd of paired error | max abs error | sd of the realized target |
| --- | --- | --- | --- | --- | --- |
| {a-only}: author .30 | author | -0.000304 | 0.001084 | 0.002010 | 0.003636 |
| {a-only}: author .30 | community | -0.000018 | 0.000019 | 0.000060 | 0.000000 |
| {b-only}: community .08 | author | 0.000041 | 0.000144 | 0.000293 | 0.000000 |
| {b-only}: community .08 | community | -0.000045 | 0.000496 | 0.000803 | 0.015041 |
| {full}: .30 / .08 / .02 | author | 0.003964 | 0.002019 | 0.007180 | 0.007016 |
| {full}: .30 / .08 / .02 | community | 0.000519 | 0.000445 | 0.000939 | 0.006755 |

### Could the recovery clauses have been INFORMATIVE at all?

The world-draw variability of a weighted population variance of an iid component has a closed form, `sd ≈ V * sqrt(2 * sum_i p_i^2)` — governed by the EFFECTIVE number of members, not the nominal one. This block draws the component vector directly (no estimator, no `y`, no corpus), forms the same replicate-sized sd the gate forms, and reports how often it lands under the #90 ceiling.

| clause | effective members | closed-form draw sd | mean replicate sd | P(replicate sd <= ceiling) |
| --- | --- | --- | --- | --- |
| b_only:community (size-weighted) | 43.3 | 0.0172 | 0.0141 | 0.267 |
| b_only:community (unweighted) | 1000.0 | 0.0036 | 0.0035 | 1.000 |
| a_only:author | 3665.0 | 0.0070 | 0.0068 | 0.954 |

### The projection on the realized incidence

Sweeps: 23 early / 23 late; exit change 8.615e-11 / 8.192e-11; maximum residual group mean 5.847e-11 over all four (author, community) x (early, late) checks.

## The corpus main budget

**NOT COMPUTED.** The A1 stop fired: at least one routing clause did not pass, so the registration forbids the real arm and no corpus main was computed, reported or stored. The failing clauses are:

- `UNINFORMATIVE` — (R02) recovery — community main in {b-only}: community .08 within max(0.01, 3 x replicate sd) of 0.0800, replicate sd <= 0.01 (#90 ceiling / #92 resolution)

The registered PREDICTIONS from X1c's 2x2 inversion (author main ≈ 0.15, community main ≈ 0.077) are therefore **UNSCORED**. They remain open, and the leg that certifies the instrument inherits them unchanged.

## Registered leans

| lean | registered | observed | status |
| --- | --- | --- | --- |
| certification PASSES | PASS | FAIL | **BROKE** |
| real author main in [0.1, 0.2] | [0.1, 0.2] | — | **UNSCORED — the A1 stop forbids the real arm** |
| real community main in [0.05, 0.11] | [0.05, 0.11] | — | **UNSCORED — the A1 stop forbids the real arm** |

## Deviations and anomalies, all recorded

- **No permutation null was run.** `B_perm = 499` is registered 'where applicable'; every X-M clause is a recovery, a leakage bound or a bootstrap statement, and none is defined against a permutation band. Running one would have produced a number no clause reads.
- **The {g-only} world's seed offset is new.** X1b fixed offsets for the author-only (13), community-only (19), null (7) and planted (0) worlds; {g-only} does not exist in X1b, so it takes the next unused offset (23) in the same series, chosen before the run and pinned in the config. No seed was re-chosen after seeing a result (#76).
- **The mean-removal factor is recomputed inside every bootstrap replicate**, rather than pinned at the realized design. This is the FIRST of #87(b)'s two permitted treatments, and it is available here only because the mains' correction is a function of the resample's own weights and costs nothing to recompute — X1c's interaction factor was pinned and its interval declared one-sidedly conservative, which is the second treatment.
- **A development prototype touched the real arm.** While the estimator was being written, a scratchpad script (never committed, never an artifact of this leg) evaluated the mains on the real skeleton to size the compute. The registration forbids REPORTING a real-data number when the gate fails, and that is honoured absolutely: no real main appears in this report, in `results/m4_xm_mains_estimator/`, in the ledger row, or in the outcome appended to the registration. The fact is recorded because concealing it would be the worse failure.

## Defect candidates for the planner (nothing below was run)

- **A #90 ceiling on a WORLD-LIMITED clause cannot distinguish a bad estimator from a bad gate.** The ceiling asks whether the replicate spread is smaller than the claimed resolution, but the replicate spread of an own-recovery clause is the sum of estimator error and world-draw variability, and on a size-skewed design the second term dominates by two orders of magnitude. Convention to consider: an own-recovery clause is scored PAIRED — each replicate against its own realized target — so that the ceiling constrains the estimator, with the nominal-target reading co-reported.
- **Registered replicate counts should be derived from the estimand's effective sample, not inherited.** The closed form `sd ≈ V * sqrt(2 * sum_i p_i^2)` is computable from the DESIGN ALONE, before any world is drawn, so a registration can state the replicate budget that makes each clause informative and refuse to register one that cannot be.
- **A size-weighted estimand needs its effective sample published next to its nominal one.** A covariance over 1,000 communities whose weights concentrate on a few dozen is not a covariance over 1,000 anything, and every table that prints the nominal count invites the wrong reading of its precision.

## Boundaries

- **Metadata only, expression VOLUME and not content (permanent).** The only text-derived quantity in this leg is `word_count_quoteless`, the author's own-word count per comment. No body was read, no topic, no style, no sentiment; `author_profiles.csv` was never opened.
- **INSTRUMENT LEG, R1-class.** Everything certified here is a property of an ESTIMATOR on a design, not a finding about people or venues. The leg issues certificates, not theory verdicts, and no downstream leg may cite it as evidence for anything about the corpus.
- **No psychological naming.** An author coefficient is a fitted offset in log-words on this eligible grid. It is not a trait, a state, a disposition or a style, and the leg is label-free.
- **EXPLORATORY, corpus-level.** No person-level claim is licensed. The author coefficients exist only as the population a covariance runs over.
- **The mains are estimands OF THIS DESIGN.** Var_hat(a) and Var_hat(b) are defined on the eligible shared grid (well-shared venues, authors with at least three surviving shared communities). They are not population quantities of Reddit, of PANDORA, or of the disjoint cohort.
- **Incomplete design.** The grid is sparse and the community side is size-skewed; the size-weighted community estimand has an EFFECTIVE number of communities far below its nominal count, which is a property of the corpus and is reported rather than repaired.
- **Cohort composition.** The disjoint cohort is TYPOLOGY-ENRICHED by construction, so it is a platform sample with a selection, not a population sample.

## Configuration

```json
{
  "author_profiles_opened": false,
  "b_boot": 1000,
  "b_perm_not_used": "B_perm = 499 is registered 'where applicable'; no X-M routing or descriptive clause is defined against a permutation band, so no permutation null was run",
  "bodies_read": false,
  "ceiling_replicate_sd": 0.01,
  "cells": {
    "certified": "MAINS_CERTIFIED",
    "defect": "INSTRUMENT_DEFECT",
    "rule": "MAINS_CERTIFIED iff EVERY routing clause passes; any failure is INSTRUMENT_DEFECT + A1, and the real arm is not run"
  },
  "class": "R1 (instrument leg; certificates only, no theory verdict)",
  "columns_read": [
    "author",
    "subreddit",
    "created_utc",
    "word_count_quoteless",
    "word_count"
  ],
  "data_source": "X1's committed cell cache results/m4_x1_venue_response/cell_cache.npz (sufficient statistics); the 17.6M-row comments CSV is re-streamed ONLY if the cache is absent",
  "df_treatment": "DERIVED in-leg: the mains carry NO residual-df shrinkage (they are the projection's coordinates, not its residual, and the cross-half form is attenuation-free); the only correction is the mean-removal/gauge loss, factor 1/(1 - sum_i p_i^2) with p the normalized covariance weights. Corrected routes, raw co-reported (#67); the factor is RECOMPUTED inside every bootstrap replicate (#87b)",
  "estimators": {
    "author_main": "cov over the connected component's authors of (a_hat_early, a_hat_late), unweighted",
    "community_main_primary": "cov over the component's communities of (b_hat_early, b_hat_late), size-weighted by analysis-pool comment counts (X1c's convention)",
    "community_main_secondary": "the same covariance, unweighted",
    "scale": "shares of comment-level Var(y) over the analysis pool (X1c's population-variance convention)"
  },
  "fe_stopping_rule": "X1b's tightened rule: BOTH residual group means at most the tolerance in absolute value on exit",
  "fe_tolerance": 1e-10,
  "halves": "author's FULL-STREAM median created_utc, <= to early",
  "k_min": 3,
  "leakage_maximum": 0.005,
  "leakage_reading": "the #85 zero-point family, extended to mains: in every world, every component planted at ZERO must read < 0.005 absolute. {full} plants all three, so the clause is vacuous there and is recorded N/A rather than silently passed",
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
  "leg": "M4-X-M",
  "machinery_imported_by_file": [
    "scripts/run_suica_m4_x1c_venue_response.py (df correction, clause-separated gate status)",
    "scripts/run_suica_m4_x1b_venue_response_fe.py (predicate chain, exact-FE alternating projections, synthetic world builder, bootstrap-FE pattern, cell cache, law vocabulary)",
    "scripts/run_suica_m4_x1_venue_response.py (Design, variance_budget, weighted_cov, #83 helpers)"
  ],
  "n_min_primary": 10,
  "normalization": [
    "1. FIT: alternating projections accumulate (a_acc, c_acc) with y_cell = a_acc[author] + c_acc[community] + v (exact to machine precision; the split is gauge-dependent, the sum is not).",
    "2. CENTRE THE AUTHOR COEFFICIENTS: abar = mean over the connected component's authors of a_acc; a_hat = a_acc - abar; ABSORB the shift, mu <- mu + abar.",
    "3. CENTRE THE COMMUNITY COEFFICIENTS: bbar = mean over the component's communities of c_acc; b_hat = c_acc - bbar; ABSORB the shift, mu <- mu + bbar.",
    "RESULT: y_cell = mu + a_hat[author] + b_hat[community] + v with mean(a_hat) = mean(b_hat) = 0, and (mu, a_hat, b_hat) unchanged by which side the sweep started from."
  ],
  "predecessors": [
    "M4-X1 (A1_STOP__SYNTHETIC_GATE_FAILED, commit ebe4f5b)",
    "M4-X1b (A1_STOP__SYNTHETIC_GATE_FAILED, commit e8c9040)",
    "M4-X1c (RESPONSE_TRACE, adjudicated; defect #87)"
  ],
  "predictions": {
    "author_main": 0.15,
    "community_main": 0.077,
    "source": "X1c's 2x2-inversion ANNOTATION on the marginal rows (implied author main 0.1526, implied community main 0.0767), promoted to a testable prediction by the X-M registration"
  },
  "registration": "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md@d65e818 (X-M)",
  "resolution_floor_share": 0.01,
  "role": "X3's #87 prerequisite: X3's stage-E trait join needs Var(a)/Var(b) as ESTIMATED objects, and X1c's rows are MARGINAL by their own admission",
  "run_utc": "2026-08-21T02:37:55.123290Z",
  "seed": 20260819,
  "seed_boot": 20260822,
  "seed_part0": 20260820,
  "seeds_inherited": "the X1/X1b derivation, NOT re-chosen (#76); the {g-only} world is new to this leg and takes the next unused offset in the same series",
  "skeleton": "X1c's primary design: law vocabulary (floor 89 users -> 1,443 communities), support floor s = 5, n_min = 10 cells, k_min = 3, largest connected component",
  "support_censused": [
    3,
    5,
    8
  ],
  "support_primary": 5,
  "synthetic_replicates": 8,
  "title": "the mains estimator",
  "tolerance_sd_multiple": 3.0,
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
  "y": "log(1 + word_count_quoteless)"
}
```

