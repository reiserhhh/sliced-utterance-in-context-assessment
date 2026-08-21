# SUICA M4-X4 — the three-level decomposition and the ergodicity contrast

**Outcome: `NONERGODIC_SIGN_FLIP`** (co-primary ownership: `NOT_OWNED`). One relation — how common a venue is against how much is written there — measured at the owner's three levels on 8,004 disjoint-cohort authors and 14,581,265 events. Level 1 (between-person) **beta_between = 0.069062** [0.048843, 0.090518]; level 2 (average within-person) **beta_within = -0.007316** [-0.011278, -0.003048]; the ergodicity contrast **Delta_erg = 0.076377** [0.055630, 0.097254] on the paired author-cluster bootstrap. Level 3's ownership of the per-person slope reads rho_own = -0.0052 [-0.0156, 0.2740] against a pairing-permutation band [-0.0220, 0.0216].

Registration: `docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md`, section "X4 — the three-level decomposition and the ergodicity contrast (registered BEFORE run, 2026-08-19)", commit 42f0625. Question provenance: the program OWNER's conference input, relayed 2026-08-19. Run 2026-08-21T00:57:17.953162Z, 31 s.

## Verdict and cells

| field | value |
|---|---|
| Delta cell (PRIMARY, routes) | `NONERGODIC_SIGN_FLIP` |
| rho_own cell (co-primary) | `NOT_OWNED` |
| routes on | Delta_erg, PRIMARY arm (disjoint pool) |
| Part 0 gate | `PASS` |
| Delta_erg | 0.076377 |
| Delta_erg CI (paired cluster bootstrap, B = 1000) | [0.055630, 0.097254] |
| #87 Delta straddle | none |
| rho_own | -0.0052 |
| rho_own CI (author cluster bootstrap, B = 1000) | [-0.0156, 0.2740] |
| #87 rho straddle | none |

Registered cells on Delta_erg (NULL-first): `LEVELS_INDISTINGUISHABLE` = the CI includes 0 (scoped by the realized width; NOT an equivalence claim); `NONERGODIC_SAME_SIGN` = the CI excludes 0 and the two slopes share sign; `NONERGODIC_SIGN_FLIP` = the CI excludes 0, the signs differ AND both slopes are detected against their own intervals; `NONERGODIC_SIGN_UNRESOLVED` = a completeness fallback (registration silent) for a Delta that excludes 0 with differing point signs but a slope whose own CI covers 0.

Ownership ladder with the #88a PRICED regions, applied in this order: `NOT_OWNED` = the CI includes 0, or the point is below -0.2327; then `AT_BOUNDARY(0.15)` up to 0.5327; then `WEAKLY_OWNED` up to 0.3163; then `AT_BOUNDARY(0.50)` up to 0.6837; then `STRONGLY_OWNED`. The Delta_erg region around 0 has half-width 0.021532.

**The priced ownership ladder is `DEGENERATE_OVERLAP`.** The 0.15 region reaches to 0.5327 while the 0.50 region starts at 0.3163, so `WEAKLY_OWNED` is an EMPTY interval at this pricing and no point could have landed in it. This is what #87 is for: the regions are the estimator's own realized widths, and here they say the ownership ladder does not resolve on the registered level-3 object. The co-primary cell `NOT_OWNED` is NOT affected by the collapse — it is decided NULL-first, by whether the interval covers 0, and never by a region edge.

## Census and the blocking anchors (#78)

| registered predicate | registered | observed | status |
|---|---|---|---|
| rows parseable (author+subreddit+created_utc+wcq) | 17,640,062 | 17,640,062 | `PASS` |
| authors | 10,296 | 10,296 | `PASS` |
| Big5 cohort authors seen | 1,401 | 1,401 | `PASS` |
| disjoint authors | 8,895 | 8,895 | `PASS` |
| communities | 46,214 | 46,214 | `PASS` |
| x = log10(share), min (2 dp) | -7.25 | -7.25 | `PASS` |
| x = log10(share), max (2 dp) | -1.14 | -1.14 | `PASS` |
| pool (>= 50 each half AND sd(x) > 0 each half), disjoint | 8,004 | 8,004 | `PASS` |
| pool (>= 50 each half AND sd(x) > 0 each half), Big5 | 1,112 | 1,112 | `PASS` |
| within-author sd(x) q25, disjoint (3 dp) | 0.805 | 0.805 | `PASS` |
| within-author sd(x) median, disjoint (3 dp) | 0.965 | 0.965 | `PASS` |
| within-author sd(x) q75, disjoint (3 dp) | 1.111 | 1.111 | `PASS` |
| within-author sd(x) q25, Big5 (3 dp) | 0.66 | 0.66 | `PASS` |
| within-author sd(x) median, Big5 (3 dp) | 0.856 | 0.856 | `PASS` |
| within-author sd(x) q75, Big5 (3 dp) | 1.013 | 1.013 | `PASS` |
| distinct communities per author, median, disjoint | 64 | 64 | `PASS` |
| distinct communities per author, median, Big5 | 55 | 55 | `PASS` |
| top-1 community share, median, disjoint (3 dp) | 0.259 | 0.259 | `PASS` |
| top-1 community share, q90, disjoint (3 dp) | 0.577 | 0.577 | `PASS` |
| top-1 community share, median, Big5 (3 dp) | 0.329 | 0.329 | `PASS` |
| top-1 community share, q90, Big5 (3 dp) | 0.743 | 0.743 | `PASS` |

## Part 0 — the gate on the REALIZED skeleton (wholly synthetic y)

Real per-author x sequences, real half splits, real cell sizes; every y in this section is planted. No corpus y value enters Part 0, and the region pricing below was written to disk BEFORE the first real-arm number existed.

### ROUTING clauses (A1-stopping)

| # | clause | observed | required | status |
|---|---|---|---|---|
| i | ERGODIC world (one beta for all, person intercepts UNCORRELATED with xbar_u): Delta_erg must read 0 | mean Delta +0.002027 over 8 replicates (sd 0.008991); 8/8 bootstrap CIs cover 0 | abs(mean) <= max(0.0050, 3 x rep sd) = 0.026973 AND >= 6/8 CIs cover 0 | `PASS` |
| ii | NON-ERGODIC world, a_u = gamma * xbar_u + noise: the DERIVED Delta is exactly gamma (beta_within is blind to a_u, beta_between reads beta + gamma), planted gamma = +0.2500 | mean Delta +0.256506 (sd 0.009369), gap +0.006506 | abs(gap) <= max(2% x 0.2500, 3 x rep sd) = 0.028108 | `PASS` |
| iii | OWNED-SLOPES world at the #76 operating point (the across-author slope dispersion DERIVED so the true ownership correlation is 0.50): rho_own recovery | mean rho_own +0.7790 (sd 0.1649), gap +0.2790 = 1.69 replicate sd — THE TOLERANCE IS CARRIED BY THE REPLICATE SPREAD, NOT BY THE POINT (see D6) | abs(gap) <= max(0.02, 3 x rep sd) = 0.4948 | `PASS` |
| iv | NULL world (beta = 0 everywhere, intercepts unrelated to x): ALL FOUR objects must read 0 within their own band or interval | beta_between +0.002927 (8/8 CIs cover 0); beta_within +0.000141 (8/8); Delta +0.002786 (8/8); rho_own +0.0024 (6/8 CIs cover 0, 7/8 points inside the pairing band) | >= 6/8 on each of the four coverage counts | `PASS` |
| v | #85b bootstrap-zero on the NULL world: every interval must cover 0 AND cover its own point | Delta CIs covering 0: 8/8; rho_own CIs covering their own point: 8/8 | >= 6/8 on both counts | `PASS` |
| vi | #88a REGION PRICING executed in-leg: the boundary-region half-widths for BOTH routed objects are Part 0's REALIZED bootstrap half-widths on the matched planted worlds, pinned BEFORE any real-arm number | Delta region +-0.021532 (null world); rho region at 0.15 +-0.3827; at 0.50 +-0.1837; pinned 2026-08-21T00:57:16.852676Z | all three finite and positive, artifact written before the first real-arm number | `PASS` |

### DESCRIPTIVE clauses (annotate, never stop)

| # | clause | observed | required | status |
|---|---|---|---|---|
| D1 | LEVEL VALUE recovery, ergodic world (both levels must read the planted beta = -0.10) | beta_between -0.0981, beta_within -0.1002 | annotate only, never stops | `ANNOTATED` |
| D2 | LEVEL VALUE recovery, non-ergodic world (beta_within = -0.10, beta_between = beta + gamma = +0.15) — this world also plants a SIGN FLIP between the levels | beta_between +0.1565, beta_within -0.1000 | annotate only, never stops | `ANNOTATED` |
| D3 | LEVEL VALUE recovery, null world (both levels read 0) | beta_between +0.002927, beta_within +0.000141 | annotate only, never stops | `ANNOTATED` |
| D4 | the DEN DISTRIBUTION the ownership mapping rides on — den = sum (x - xbar_cell)^2 is unbounded below in this pool, so A_h = sigma^2 E[1/den] can be dominated by a handful of near-degenerate halves | A_early 0.0174469 (median-based 0.00324483), A_late 27.9454 (median-based 0.00308668); min den 0.02221 / 4.664e-06, median den 308.2 / 324 | annotate only, never stops | `ANNOTATED` |
| D5 | the x-only PRECISION FLOOR the real arms also carry as a non-routing sensitivity (den >= 1.0, i.e. the per-half slope's sampling sd does not exceed the event-noise sd) | 7,986 of 8,000 level-3 authors clear the floor (14 excluded); the floored mapping reads A_early 0.00776003 / A_late 0.00740677 against the routed 0.0174469 / 27.9454 | annotate only, never stops | `ANNOTATED` |
| D6 | OWNERSHIP RECOVERY ON THE FLOORED OBJECT — the same planted question with the near-degenerate halves out; this is what clause (iii)'s replicate spread is made of | planted 0.50 -> +0.5051 (sd 0.0138, half-width 0.0293) against the ROUTED object's +0.7790 (sd 0.1649, half-width 0.1837); planted 0.15 -> +0.1468 (half-width 0.0357) against +0.2951 (half-width 0.3827) | annotate only, never stops | `ANNOTATED` |

### The derived non-ergodic Delta (clause ii, analytic)

```
y_{u,i} = a_u + beta * x_{u,i} + e_{u,i},   a_u = gamma * xbar_u + w_u
  level 2:  within-(u,h) centering annihilates a_u  =>  E[beta_within] = beta
  level 1:  ybar_u = (beta + gamma) xbar_u + w_u + ebar_u
            =>  E[beta_between] = beta + gamma   (w_u uncorrelated with xbar_u)
  =>  Delta_erg = beta_between - beta_within = gamma   EXACTLY, with no free parameter
```
Planted gamma = +0.2500; the clause requires recovery of that number and nothing else.

### The ownership mapping (#76 operating point, derived here)

```
rho = V / sqrt((V + A_e)(V + A_l)), A_h = sigma^2 * E_u[1 / den_{u,h}]
```
| quantity | rho target 0.50 | rho target 0.15 | 0.50, precision-floored (annotation) |
|---|---|---|---|
| authors in the mapping | 8,000 | 8,000 | 7,986 |
| A_early = sigma^2 E[1/den_early] | 0.01744691 | 0.01744691 | 0.00776003 |
| A_late = sigma^2 E[1/den_late] | 27.94537166 | 27.94537166 | 0.00740677 |
| V = Var_u(beta_u) solving the target | 9.33834305 | 0.66063311 | 0.00758237 |
| sd(beta_u) planted | 3.055870 | 0.812793 | 0.087077 |
| rho implied by the solution | 0.500000 | 0.150000 | 0.500000 |

### #88a region pricing — PINNED BEFORE ANY REAL-ARM NUMBER

| region | centre | matched planted world | realized bootstrap half-width | planted / realized rho |
|---|---|---|---|---|
| Delta_erg | 0.0000 | `null` | 0.021532 | 0 / n.a. |
| rho_own low | 0.15 | `owned_slopes_at_0.15` | 0.3827 | 0.15 / 0.2951 |
| rho_own high | 0.50 | `owned_slopes` | 0.1837 | 0.50 / 0.7790 |

ANNOTATION (routes nothing): the same pricing on the level-3 object read through the x-only precision floor den >= 1.0 — half-width 0.0357 at 0.15 (realized rho 0.1468) and 0.0293 at 0.50 (realized rho 0.5051).

Pricing artifact written 2026-08-21T00:57:16.852676Z; first real-arm number computed 2026-08-21T00:57:16.859920Z (`PASS`).

## The three levels, per arm

| arm | authors | events | level 1 beta_between (CI) | r_between | level 2 beta_within (CI) | Delta_erg (CI) | cell |
|---|---|---|---|---|---|---|---|
| PRIMARY — disjoint pool | 8,004 | 14,581,265 | 0.069062 [0.048843, 0.090518] | 0.0734 | -0.007316 [-0.011278, -0.003048] | 0.076377 [0.055630, 0.097254] | `NONERGODIC_SIGN_FLIP` |
| REPLICATION — Big5 pool | 1,112 | 2,984,569 | 0.051346 [-0.005921, 0.107078] | 0.0540 | -0.009454 [-0.021970, 0.001675] | 0.060799 [0.002037, 0.116844] | `NONERGODIC_SIGN_UNRESOLVED` |
| sensitivity — floor 100 events/half, disjoint pool | 6,859 | 14,411,014 | 0.063888 [0.039694, 0.087040] | 0.0681 | -0.007804 [-0.011817, -0.003275] | 0.071692 [0.046891, 0.094870] | `NONERGODIC_SIGN_FLIP` |

Level 2 is the mean of the two half slopes; both halves are printed so the average is not a black box:

| arm | beta_within (early half) | beta_within (late half) | mean = level 2 |
|---|---|---|---|
| PRIMARY — disjoint pool | -0.014776 | 0.000144 | -0.007316 |
| REPLICATION — Big5 pool | -0.022666 | 0.003759 | -0.009454 |
| sensitivity — floor 100 events/half, disjoint pool | -0.015400 | -0.000209 | -0.007804 |

## Level 3 — the per-person slope, its ownership and its true dispersion

| arm | authors scored | dropped (constant half) | rho_own | CI (B = 1000) | pairing band (B = 499) | cell | mean beta | Var(beta) cross-half | sd_true | headroom about the mean |
|---|---|---|---|---|---|---|---|---|---|---|
| PRIMARY — disjoint pool | 8,000 | 4 | -0.0052 | [-0.0156, 0.2740] | [-0.0220, 0.0216] | `NOT_OWNED` | 0.067040 | -0.00972847 | n/a | [n/a, n/a] |
| REPLICATION — Big5 pool | 1,103 | 9 | -0.0016 | [-0.0806, 0.3235] | [-0.0485, 0.0492] | `NOT_OWNED` | 0.021257 | -0.00047770 | n/a | [n/a, n/a] |
| sensitivity — floor 100 events/half, disjoint pool | 6,858 | 1 | 0.0952 | [0.0718, 0.3368] | [-0.0249, 0.0201] | `AT_BOUNDARY(0.15)` | 0.007106 | 0.00932276 | 0.096554 | [-0.1821, 0.1964] |

`Var(beta)` is the CROSS-HALF COVARIANCE of the two per-half slope estimates — the across-author variance with the per-half estimation noise removed. `headroom` (recorded definition) is the +-1.96 sd_true interval about the mean slope: what the owned dispersion buys around the average person, an annotation and not a measurement of any individual.

NON-ROUTING sensitivity — the same level-3 object through the x-only precision floor den >= 1.0:

| arm | authors above the floor | excluded | rho_own | CI | Var(beta) cross-half |
|---|---|---|---|---|---|
| PRIMARY — disjoint pool | 7,986 | 14 | 0.2768 | [0.2416, 0.3103] | 0.00798683 |
| REPLICATION — Big5 pool | 1,096 | 7 | 0.3338 | [0.2590, 0.4184] | 0.01745042 |
| sensitivity — floor 100 events/half, disjoint pool | 6,851 | 7 | 0.3246 | [0.2941, 0.3554] | 0.00778750 |

## The owner's schema, mapped onto what was measured

| the owner's design | what it yields | this leg's object | reading |
|---|---|---|---|
| one-shot measurement of a GROUP | the BETWEEN-person relation | `beta_between`, the OLS slope of person-mean y on person-mean x over 8,004 authors | 0.069062 [0.048843, 0.090518], r = 0.0734 |
| repeated measurement of MANY | the AVERAGE WITHIN-person relation | `beta_within`, the within-(author, half)-centered pooled slope, averaged over the two halves | -0.007316 [-0.011278, -0.003048] |
| repeated measurement of ONE | THAT person's relation | `beta_{u,h}`, one slope per author per half; its ownership `rho_own` and its noise-free dispersion `Var(beta)` | rho_own -0.0052 [-0.0156, 0.2740], Var(beta) = -0.00972847 |
| **the comparison** | **whether level 1 = level 2** | **`Delta_erg`**, paired author-cluster bootstrap | **0.076377 [0.055630, 0.097254]** -> `NONERGODIC_SIGN_FLIP` |

## Registered leans (report against; they never route)

| lean | registered | observed | status |
|---|---|---|---|
| beta_within < 0 (a commoner venue -> shorter comments) | held moderately | -0.007316 [-0.011278, -0.003048] | `HELD` |
| beta_between < 0 | held moderately | +0.069062 [0.048843, 0.090518] | `BROKEN` |
| Delta_erg NONERGODIC_SAME_SIGN with abs(beta_between) > abs(beta_within) | held weakly | cell `NONERGODIC_SIGN_FLIP`, abs(between) 0.069062 vs abs(within) 0.007316 | `BROKEN` |
| rho_own(beta) WEAKLY_OWNED | WEAKLY_OWNED | `NOT_OWNED` at rho_own -0.0052 [-0.0156, 0.2740]; NOTE: at this pricing WEAKLY_OWNED is an EMPTY interval, so the lean could not have held whatever the data said | `BROKEN` |
| the Big5 replication lands in the SAME Delta cell | NONERGODIC_SIGN_FLIP | NONERGODIC_SIGN_UNRESOLVED | `BROKEN` |
| Big5 ownership possibly HIGHER than the primary's | co-reported, either way is a #73 flag | Big5 -0.0016 vs primary -0.0052; through the x-only precision floor (routes nothing) Big5 +0.3338 [0.2590, 0.4184] vs primary +0.2768 [0.2416, 0.3103] | `HELD` |

## #73 flags and #87 straddles

| arm | object | primary cell | arm cell | value | CI | note |
|---|---|---|---|---|---|---|
| big5 | Delta_erg | `NONERGODIC_SIGN_FLIP` | `NONERGODIC_SIGN_UNRESOLVED` | 0.060799 | [0.002037, 0.116844] | #73 divergence; the primary routes |
| floor100 | rho_own | `NOT_OWNED` | `AT_BOUNDARY(0.15)` | 0.095166 | [0.071768, 0.336775] | #73 divergence; the primary routes |
| big5 | Delta_erg | `NONERGODIC_SIGN_FLIP` | `NONERGODIC_SIGN_UNRESOLVED` | 0.060799 | [0.002037, 0.116844] | #87 straddle: the CI crosses the priced region edge(s) 0.0215 |
| big5 | rho_own | `NOT_OWNED` | `NOT_OWNED` | -0.001564 | [-0.080609, 0.323478] | #87 straddle: the CI crosses the priced region edge(s) 0.3163 |
| floor100 | rho_own | `NOT_OWNED` | `AT_BOUNDARY(0.15)` | 0.095166 | [0.071768, 0.336775] | #87 straddle: the CI crosses the priced region edge(s) 0.3163 |

## Honest anomalies

- **the pool predicate is reproduced through the CENSUS's own floating-point path, and that path admits mathematically constant halves.** `sd(x) > 0 in EACH half` has three defensible implementations and they do not agree on this corpus: numpy's per-slice two-pass sd (pairwise summation) gives 8,004 / 1,112 — the REGISTERED anchors, reproduced here exactly; a grouped sequential accumulation gives 8,008 / 1,114; the mathematically exact test min(x) == max(x) gives 8,000 / 1,103. The anchored path therefore admits 13 halves whose x is mathematically constant. They are not swept under the rug: their exact contribution to the level-1 and level-2 pooled sums is zero and is set to zero, and the level-3 estimator returns NaN for them and counts them (4 authors dropped on the primary arm). No estimand value depends on which of the three paths is used beyond those 13 cells.
- **the level-3 object is ONE-AUTHOR FRAGILE, and the priced ownership regions say so.** `den = sum (x - xbar_cell)^2` is unbounded below in this pool: the median half has den ~ 324 but the smallest non-degenerate late half has den = 4.66e-06, so that one author's per-half slope carries a sampling variance of 214,404 — about 96% of the whole arm's A_late = 27.95. The #76 mapping therefore lands on a pathological operating point (V = 9.338, sd(beta_u) = 3.06) and the cluster bootstrap correctly reports that rho_own on this skeleton can be moved by a single author: the priced half-widths are +-0.184 at 0.50 and +-0.383 at 0.15, which is wide enough that the registered ownership LADDER cannot be resolved at this design's own precision. This is a true statement about the registered estimator, not a bug: with the x-only precision floor (den >= 1.0, 7,986 of 8,000 authors) the same worlds price at +-0.029 and +-0.036. The routed number is the registered one; the floored arm is co-reported and routes nothing.
- **Part 0's ownership clause (iii) passes on its REPLICATE SPREAD, not on its point.** The planted world's realized rho_own is +0.7790 against the derived 0.50 — a gap of +0.2790 that clears the registered tolerance only because the replicate sd is 0.1649 and the tolerance is 3 x that. The clause is recorded as PASSED and simultaneously as UNINFORMATIVE, which is the honest reading of a max(floor, 3 x sd) tolerance whose second term has run away. D6 shows the same recovery on the floored object: +0.5051 (sd 0.0138) against the same planted 0.50, so the level-3 machinery itself is sound and it is the pool's den tail that is not.
- **A_early and A_late differ by three orders of magnitude on the same authors.** A_early = 0.01745 against A_late = 27.95, while the MEDIAN-based versions agree to a few percent (0.003245 vs 0.003087). The two halves are statistically alike; the asymmetry is one late half in the extreme tail. The floored mapping removes it entirely (0.00776 vs 0.007407).
- **the PRICED ownership ladder collapsed: `WEAKLY_OWNED` is an empty interval.** The priced regions run [-0.2327, 0.5327] around 0.15 and [0.3163, 0.6837] around 0.50, which overlap, so no rho_own value could have been called `WEAKLY_OWNED` at this pricing — the exact cell the registration LEANED toward. The lean is therefore recorded as BROKEN against a ladder that could not have produced it, which is a weaker statement than a broken lean usually is and is flagged as such. The routed cell `NOT_OWNED` is decided NULL-first and does not depend on any region edge.
- **Var(beta) by cross-half covariance comes out NEGATIVE on the routed level-3 object.** Cov(beta_early, beta_late) = -0.00972847 on the primary arm, so sd_true and the headroom are undefined and are printed as n/a. A variance estimate cannot be negative in truth; this is the same one-author tail read through the covariance instead of the correlation. Through the x-only precision floor the same arm reads Var(beta) = +0.00798683 with rho_own +0.2768 [0.2416, 0.3103]. The routed number is the registered one; the floored one is co-reported and routes nothing.
- **level 2 is carried almost entirely by the EARLY half.** The within-person slope reads -0.014776 on the early half and +0.000144 on the late half; the registered estimand is their mean, -0.007316. The registration pins the average of the two halves and that is what routes, but a reader should not take level 2 as a stationary quantity: on this corpus it is a two-number average whose two numbers disagree in magnitude and nearly in sign. Nothing in this leg can say whether that is calendar drift, a cohort composition change, or the half split itself.
- **an arm disagrees with the primary on the Delta cell (#73).** Arms `big5` -> `NONERGODIC_SIGN_UNRESOLVED` (Delta +0.060799 [0.002037, 0.116844]) against the primary's `NONERGODIC_SIGN_FLIP` (Delta +0.076377 [0.055630, 0.097254]). The primary routes; the divergence is reported and not resolved.

## Boundaries

- **Metadata only; expression VOLUME and not content (permanent).** The only text-derived quantity in this leg is `word_count_quoteless`, the author's own-word count per comment. No body was read, no topic, no style, no sentiment. The other variable, `x`, is a community's share of the whole event stream — a pure activity statistic. Every claim here is about HOW MUCH is written where, never about WHAT is written.
- **The owner's three-level schema, with its provenance.** The between/average-within/single-person trichotomy this leg measures is the program OWNER's conference input, relayed 2026-08-19: a one-shot group measurement yields a BETWEEN-person relation; repeated measurement of many yields the AVERAGE WITHIN-person relation; repeated measurement of one yields THAT person's relation. X4 supplies a corpus instance of the schema on metadata; it does not supply the schema, and the schema is cited, not claimed.
- **The projection caution.** beta_between, beta_within and beta_{u,h} are STATIC projections of a much richer dynamic object. One scalar relation measured at three levels says nothing about lags, about how the relation moves within a half, or about any other coordinate. A level difference is a statement about these three projections at this resolution; a null is not an equivalence claim.
- **No psychological naming.** Expression volume and its community gradient are technical objects. Nothing here is a trait, a state, a disposition or a preference, and the leg is label-free: `author_profiles.csv` was never opened.
- **EXPLORATORY, corpus-level.** No person-level claim is licensed. The per-author slopes exist only as the population of a mean, a covariance and one correlation; no individual's beta is a measurement of that individual.
- **The cohort-selection caveat (carried from X2).** A Big5/disjoint difference cannot be separated from HOW the 1,401 Big5 authors were selected. The disjoint cohort is also TYPOLOGY-ENRICHED by construction (PANDORA's non-Big5 authors are MBTI-labelled users), so both cohorts are platform samples with a selection, not population samples.
- **Pool selection.** The pool floors at 50 events in EACH half and requires within-half x spread, so the leg speaks for authors who are ACTIVE ON BOTH SIDES of their own median AND who move between communities. Nothing here speaks for short-lived, low-volume or single-community accounts.

## Governance

| gate | status |
|---|---|
| Census / blocking anchors (#78, 21 predicates) | `PASS` |
| Part 0 realized-skeleton gate (6 ROUTING clauses) | `PASS` |
| #88a pricing order (regions pinned before the first real number) | `PASS` |
| ID-leak scan (0 NEW hits of 10,296 author names over the committed files; 4 pre-existing dictionary collisions carried unchanged from HEAD) | `PASS` |

## Configuration

```json
{
  "author_profiles_csv": "NEVER OPENED (label-free)",
  "b_boot": 1000,
  "b_perm": 499,
  "boundary_centres": {
    "delta": 0.0,
    "rho_high": 0.5,
    "rho_low": 0.15
  },
  "boundary_half_widths": "PRICED IN-LEG (#88a) from Part 0's realized bootstrap half-widths on the matched planted worlds",
  "cohort": "/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/results/m4_sr0_recon/cohort_authors.csv",
  "columns_read": [
    "author",
    "subreddit",
    "created_utc",
    "word_count_quoteless"
  ],
  "comments": "/Volumes/mobile3/projects/project persona/data_sets/PANDORA_official/all_comments_since_2015.csv",
  "ergodic_cover_floor": 6,
  "halves": "full-stream median of the author's created_utc, <= early",
  "leg": "M4-X4",
  "level_3_degeneracy_rule": "a cell whose x is exactly constant (min == max) yields NaN and is counted; its contribution to the level-1 and level-2 pooled sums is exactly zero",
  "n_synth_replicates": 8,
  "order": "per-author stable sort by created_utc (ties keep stream order)",
  "planted_beta": -0.1,
  "planted_gamma": 0.25,
  "planted_sd_intercept": 0.5,
  "planted_sd_noise": 1.0,
  "pool": ">= 50 events in EACH half AND within-author sd(x) > 0 in EACH half (np.std per half slice, the census's own path)",
  "pool_floor_primary": 50,
  "pool_floor_sensitivity": 100,
  "precision_floor_den": 1.0,
  "precision_floor_role": "x-only NON-ROUTING sensitivity, pinned before any real number",
  "question_provenance": "the program OWNER's conference input, relayed 2026-08-19",
  "registration": "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md, section X4, commit 42f0625",
  "rho_price_low": 0.15,
  "rho_true_target": 0.5,
  "seed": 20260819,
  "seed_boot": 20260822,
  "seed_part0": 20260820,
  "seed_perm": 20260821,
  "tol_delta": "max(0.02 x |planted Delta scale|, 3.0 x replicate sd)",
  "tol_rho": "max(0.02, 3.0 x replicate sd)",
  "x": "log10(community share of all parseable events) \u2014 a GLOBAL fixed community attribute over the full stream",
  "y": "log1p(word_count_quoteless)"
}
```

Config SHA-256: `e896dc166dd619c9cc934209d070350013b60a392ecae3442f91565872de0577`. Artifacts: `results/m4_x4_three_levels/` (gitignored). Every table above is generated from those artifacts (rule 24).

