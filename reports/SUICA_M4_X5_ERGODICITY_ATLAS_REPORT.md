# SUICA M4-X5 — the ergodicity atlas

**Verdict: `ATLAS_HETEROGENEOUS`**

Registered BEFORE the run in `docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md` (section "X5 — the ergodicity atlas", commit de09409). Five metadata relations, each measured at all three of the owner's measurement series, with the #89 estimability floor as the pool clause, the #90 precision ceilings on every routing recovery clause, and the #91 ladder-coherence check on every priced region set. Bridge build-out item 2. EXPLORATORY, corpus-level, label-free, metadata-only.

## Gates

| gate | status |
|---|---|
| Census / blocking anchors (#78, 22 predicates) | `PASS` |
| Part 0 gate, R1 (commonness x volume) | `PASS` |
| Part 0 gate, R2 (gap x volume) | `PASS` |
| Part 0 gate, R3 (volume x score) | `PASS` |
| Part 0 gate, R4 (commonness x score) | `PASS` |
| Part 0 gate, R5 (commonness x gap) | `PASS` |
| #88a pricing order (every relation priced before the first real number) | `PASS` |
| ID-leak scan (0 NEW hits of 10,296 author names over the committed files; 4 pre-existing dictionary collisions carried unchanged from HEAD) | `PASS` |

## THE ATLAS

Five relations x three measurement series x two cohorts. `beta_b` is level 1 (between-person), `beta_w` is level 2 (average within-person), `Delta` is their difference under the paired author-cluster bootstrap, and `rho_own` is the level-3 ownership correlation of the FLOORED per-author slopes. R1's levels 1-2 are IMPORTED from X4's committed artifacts; its ownership is recomputed here under the floor.

### PRIMARY — disjoint pool

| relation | authors | beta_b | beta_w | Delta [95% CI] | Delta cell | rho_own [95% CI] | ownership |
|---|---|---|---|---|---|---|---|
| **R1** commonness x volume | 7,986 | 0.069062 | -0.007316 | 0.076377 [0.055630, 0.097254] | `NONERGODIC_SIGN_FLIP` | 0.2768 [0.2441, 0.3092] | `WEAKLY_OWNED` |
| **R2** gap x volume | 7,989 | 0.078450 | 0.059092 | 0.019358 [-0.001034, 0.037833] | `LEVELS_INDISTINGUISHABLE` | 0.4151 [0.3925, 0.4372] | `WEAKLY_OWNED` |
| **R3** volume x score | 8,008 | 0.006501 | 0.005172 | 0.001329 [-0.010809, 0.013378] | `LEVELS_INDISTINGUISHABLE` | 0.3585 [0.3320, 0.3847] | `WEAKLY_OWNED` |
| **R4** commonness x score | 7,986 | -0.022737 | 0.001884 | -0.024622 [-0.035282, -0.013686] | `NONERGODIC_SIGN_UNRESOLVED` | 0.2863 [0.2435, 0.3319] | `WEAKLY_OWNED` |
| **R5** commonness x gap | 7,966 | -0.256325 | -0.073531 | -0.182794 [-0.205119, -0.158719] | `NONERGODIC_SAME_SIGN` | 0.2164 [0.1849, 0.2480] | `WEAKLY_OWNED` |

### REPLICATION — Big5 pool (#73)

| relation | authors | beta_b | beta_w | Delta [95% CI] | Delta cell | rho_own [95% CI] | ownership |
|---|---|---|---|---|---|---|---|
| **R1** commonness x volume | 1,096 | 0.051346 | -0.009454 | 0.060799 [0.002037, 0.116844] | `NONERGODIC_SIGN_UNRESOLVED` | 0.3338 [0.2681, 0.4199] | `WEAKLY_OWNED` |
| **R2** gap x volume | 1,100 | 0.125773 | 0.083492 | 0.042281 [-0.014043, 0.093462] | `LEVELS_INDISTINGUISHABLE` | 0.5380 [0.4800, 0.5916] | `STRONGLY_OWNED` |
| **R3** volume x score | 1,116 | 0.000506 | 0.014898 | -0.014392 [-0.044014, 0.015019] | `LEVELS_INDISTINGUISHABLE` | 0.4356 [0.3536, 0.5175] | `WEAKLY_OWNED` |
| **R4** commonness x score | 1,096 | 0.004780 | 0.007481 | -0.002702 [-0.030359, 0.027177] | `LEVELS_INDISTINGUISHABLE` | 0.3396 [0.2674, 0.4108] | `WEAKLY_OWNED` |
| **R5** commonness x gap | 1,081 | -0.347683 | -0.084064 | -0.263619 [-0.322152, -0.206946] | `NONERGODIC_SAME_SIGN` | 0.2398 [0.0788, 0.3885] | `WEAKLY_OWNED` |

R1's author count is its FLOORED level-3 pool (7,986 disjoint, 1,096 Big5); its levels 1-2 and Delta are X4's, measured on X4's pool (8,004 / 1,112) and imported unchanged.

**Atlas route (disjoint): `ATLAS_HETEROGENEOUS`** — 4 distinct Delta cell(s) across the five relations (`LEVELS_INDISTINGUISHABLE`, `NONERGODIC_SAME_SIGN`, `NONERGODIC_SIGN_FLIP`, `NONERGODIC_SIGN_UNRESOLVED`). All five LEVELS_INDISTINGUISHABLE: no; all five in nonergodic cells: no; all five in ONE nonergodic cell: no.

**Atlas route (Big5 replication, #73): `ATLAS_HETEROGENEOUS`.**

## What the #89 estimability floor bought

X4 measured R1 with the same estimator MINUS the floor and recorded three pathologies. Both columns are artifact values.

| object | X4, no floor | X5, floored |
|---|---|---|
| cross-half Var(beta), R1 disjoint | -0.009728 | 0.007987 |
| owned-world rho replicate sd (the #90 object) | 0.1649 | 0.0090–0.0172 over the relations |
| priced rho half-width at 0.50 (the #91 object) | 0.1837 | 0.0211–0.0306 |
| ladders coherent | 0 of 1 (WEAKLY_OWNED was empty) | 5 of 5 |

## The level-3 plateau, as a PREDICTION

Registered criterion: the point estimate lies in [0.25, 0.3] for >= 2 of the four new relations, disjoint cohort. Band provenance: bridge section 7: X1c response-profile persistence 0.279, X2 rhythm ownership 0.259, X4 floored slope ownership 0.277.

| relation | rho_own | 95% CI | point in band | CI overlaps band |
|---|---|---|---|---|
| R2 | 0.4151 | [0.3925, 0.4372] | no | no |
| R3 | 0.3585 | [0.3320, 0.3847] | no | no |
| R4 | 0.2863 | [0.2435, 0.3319] | yes | yes |
| R5 | 0.2164 | [0.1849, 0.2480] | no | no |

**Outcome: `BROKEN`** — 1 of 4 new relations put their point estimate in the band (1 of 4 overlap it with the interval).

## Census (#78 blocking anchors)

| predicate | registered | observed | status |
|---|---|---|---|
| rows parseable (author+subreddit+created_utc+wcq) | 17,640,062 | 17,640,062 | `PASS` |
| authors | 10,296 | 10,296 | `PASS` |
| Big5 cohort authors seen | 1,401 | 1,401 | `PASS` |
| disjoint authors | 8,895 | 8,895 | `PASS` |
| communities | 46,214 | 46,214 | `PASS` |
| score missing (of parseable) | 147 | 147 | `PASS` |
| x = log10(share), min (2 dp) | -7.25 | -7.25 | `PASS` |
| x = log10(share), max (2 dp) | -1.14 | -1.14 | `PASS` |
| R1 pool, X4's sd(x) > 0 path, disjoint | 8,004 | 8,004 | `PASS` |
| R1 pool, X4's sd(x) > 0 path, Big5 | 1,112 | 1,112 | `PASS` |
| R2 pool, disjoint | 7,989 | 7,989 | `PASS` |
| R2 pool, Big5 | 1,100 | 1,100 | `PASS` |
| R2 within-sd(x) median, disjoint (3 dp) | 1.138 | 1.138 | `PASS` |
| R3 pool, disjoint | 8,008 | 8,008 | `PASS` |
| R3 pool, Big5 | 1,116 | 1,116 | `PASS` |
| R3 within-sd(x) median, disjoint (3 dp) | 1.031 | 1.031 | `PASS` |
| R4 pool, disjoint | 7,986 | 7,986 | `PASS` |
| R4 pool, Big5 | 1,096 | 1,096 | `PASS` |
| R4 within-sd(x) median, disjoint (3 dp) | 0.966 | 0.966 | `PASS` |
| R5 pool, disjoint | 7,966 | 7,966 | `PASS` |
| R5 pool, Big5 | 1,081 | 1,081 | `PASS` |
| R5 within-sd(x) median, disjoint (3 dp) | 0.966 | 0.966 | `PASS` |

Per-relation pool arithmetic (x-only, #57: no x-y quantity is evaluated in the census):

| relation | x | y | usable events | disjoint pool | Big5 pool | dropped by the count floor | dropped by the #89 den floor | within-sd(x) med (disjoint) |
|---|---|---|---|---|---|---|---|---|
| **R1** commonness x volume | log10(community share of all parseable events) | log1p(word_count_quoteless) | 17,577,863 | 7,986 | 1,096 | 0 | 42 | 0.966 |
| **R2** gap x volume | log10(seconds since the author's previous comment, full stream) | log1p(word_count_quoteless) | 17,134,912 | 7,989 | 1,100 | 35 | 0 | 1.138 |
| **R3** volume x score | log1p(word_count_quoteless) | slog(score) = sign(score) * log1p(abs(score)) | 17,577,716 | 8,008 | 1,116 | 0 | 0 | 1.031 |
| **R4** commonness x score | log10(community share of all parseable events) | slog(score) = sign(score) * log1p(abs(score)) | 17,577,716 | 7,986 | 1,096 | 0 | 42 | 0.966 |
| **R5** commonness x gap | log10(community share of all parseable events) | log10(seconds since the author's previous comment, full stream) | 17,134,912 | 7,966 | 1,081 | 35 | 42 | 0.966 |

## The R1 import (bit-check)

| object | X4 committed | X5 here | status |
|---|---|---|---|
| Delta_erg (disjoint) | 0.076377 | imported, not recomputed | `IMPORTED` |
| Delta_erg (Big5) | 0.060799 | imported, not recomputed | `IMPORTED` |
| floored rho_own (disjoint) | 0.276816343318 | 0.276816343318 | `PASS` |
| floored pool authors (disjoint) | 7,986 | 7,986 | `PASS` |

The floored ownership point is recomputed from THIS leg's fresh five-column cache and must reproduce X4's committed value to 1e-12: same events, same order, same pinned two-pass path. The observed difference is 0.

## Part 0 — the per-relation gate

Each relation's battery runs on ITS OWN realized skeleton (real x sequences, real halves, real cell sizes; wholly synthetic y). R1 inherits X4's passed gate. The OWNED-slopes recovery ROUTES once, on R2's skeleton, as registered; the owned worlds still run on every relation because #88a prices each relation's rho regions from its own matched worlds.

### R1 — commonness x volume (`PASS`)

| clause | requirement | observed | status |
|---|---|---|---|
| **X4** R1 inherits X4's Part 0 gate (6 ROUTING clauses, all PASS) unchanged | the inherited gate PASSED | X4 gate status PASS; priced 2026-08-21T00:57:16.852676Z | `PASS` |

| descriptive | observed | status |
|---|---|---|
| **D1** X4's ergodic-world honesty check (the instrument does not manufacture non-ergodicity) | mean Delta +0.002027, 8/8 CIs cover 0 | `ANNOTATED` |
| **D2** X4's FLOORED ownership recovery (D6 there): the worlds matched to X5's estimator | planted 0.50 -> +0.5051 (half-width 0.0293); planted 0.15 -> +0.1468 (half-width 0.0357) | `ANNOTATED` |

Priced regions (#88a, pinned 2026-08-21T00:57:16.852676Z): Delta +-0.021532 from the `null` world; rho at 0.15 +-0.0357; rho at 0.50 +-0.0293. **#91 ladder: `COHERENT`** — edges [0.1143, 0.1857] and [0.4707, 0.5293]. the priced regions are disjoint with non-empty interior cells, so the registered ownership ladder resolves at this design's own precision.

### R2 — gap x volume (`PASS`)

| clause | requirement | observed | status |
|---|---|---|---|
| **i** ERGODIC world (one beta for all, person intercepts UNCORRELATED with xbar_u): Delta_erg must read 0 | abs(mean) <= max(0.02, 3 x rep sd) = 0.046291 AND >= 6/8 CIs cover 0 | mean Delta -0.001043 over 8 replicates (sd 0.015430); 6/8 bootstrap CIs cover 0 | `PASS` |
| **ii** NON-ERGODIC world, a_u = gamma * xbar_u + noise: the DERIVED Delta is exactly gamma (within-centering annihilates a_u so level 2 reads beta, while level 1 reads beta + gamma), planted gamma = +0.2500 | abs(gap) <= max(0.02, 3 x rep sd) = 0.042385 | mean Delta +0.252026 (sd 0.014128), gap +0.002026 = 0.14 replicate sd | `PASS` |
| **ii-ceiling** #90 PRECISION CEILING on clause (ii): the replicate spread of the recovery must itself be inside the registered tolerance floor (0.02 in Delta units), else the clause certifies nothing | rep sd <= the tolerance floor (else UNINFORMATIVE) | replicate sd 0.014128 against the ceiling 0.02 | `PASS` |
| **iii-owned** OWNED-SLOPES world at the #76 operating point (the across-author slope dispersion DERIVED so the true ownership correlation is 0.50), FLOORED estimator: rho_own recovery — the registration routes this clause ONCE, on R2's skeleton | abs(gap) <= max(0.02, 3 x rep sd) = 0.0303 | mean rho_own +0.5042 (sd 0.0101), gap +0.0042 = 0.41 replicate sd | `PASS` |
| **iii-owned-ceiling** #90 PRECISION CEILING on the ownership recovery — the clause X4's defect #90 was purchased from: it passed there on a replicate spread of 0.165 | rep sd <= the tolerance floor (else UNINFORMATIVE) | replicate sd 0.0101 against the ceiling 0.02 | `PASS` |
| **iii** NULL world (beta = 0 everywhere, intercepts unrelated to x): ALL FOUR objects must read 0 within their own band or interval | >= 6/8 on each of the five coverage counts | beta_between -0.000973 (8/8 CIs cover 0); beta_within -0.000032 (8/8); Delta -0.000941 (8/8); rho_own +0.0054 (8/8 CIs cover 0, 7/8 points inside the pairing band) | `PASS` |
| **iv** #85b bootstrap-zero on the NULL world: every interval must cover 0 AND cover its own point | >= 6/8 on both counts | Delta CIs covering 0: 8/8; rho_own CIs covering their own point: 8/8 | `PASS` |
| **v** #88a REGION PRICING executed in-leg on THIS relation's skeleton: the boundary half-widths for both routed objects are the realized bootstrap half-widths on the matched planted worlds, pinned BEFORE any real number | all three finite and positive, artifact written before the first real number | Delta region +-0.019237 (null world); rho region at 0.15 +-0.0284; at 0.50 +-0.0211; pinned 2026-08-21T01:56:52.122323Z | `PASS` |
| **vi** #91 LADDER COHERENCE on the priced regions: disjoint regions with non-empty interior cells, ELSE the ownership classification collapses EXPLICITLY to the binary | the check is ASSERTED and its outcome RECORDED; a collapse is a legitimate outcome and never stops the leg (the coarser partition is stated) | edges [0.1216, 0.1784] around 0.15 and [0.4789, 0.5211] around 0.50 -> COHERENT | `PASS` |

| descriptive | observed | status |
|---|---|---|
| **D1** LEVEL VALUE recovery, ergodic world (both levels must read the planted beta = -0.10) | beta_between -0.1010, beta_within -0.1000 | `ANNOTATED` |
| **D2** LEVEL VALUE recovery, non-ergodic world (beta_within = -0.10, beta_between = +0.15) | beta_between +0.1519, beta_within -0.1002 | `ANNOTATED` |
| **D3** the #89 den distribution the ownership mapping rides on — with the floor in the POOL, A_h = sigma^2 E[1/den] can no longer be dominated by a near-degenerate half | A_early 0.0035044 (median-based 0.0021764), A_late 0.00317272 (median-based 0.00201419); min den 24.54 / 34.44, median den 459.5 / 496.5; V = 0.003337, sd(beta_u) = 0.05776 | `ANNOTATED` |
| **D4** OWNERSHIP RECOVERY on this relation's skeleton (ROUTES only on R2; here it prices the rho regions and annotates) | planted 0.50 -> +0.5042 (sd 0.0101, half-width 0.0211); planted 0.15 -> +0.1464 (sd 0.0094, half-width 0.0284) | `ANNOTATED` |

Priced regions (#88a, pinned 2026-08-21T01:56:52.122323Z): Delta +-0.019237 from the `null` world; rho at 0.15 +-0.0284; rho at 0.50 +-0.0211. **#91 ladder: `COHERENT`** — edges [0.1216, 0.1784] and [0.4789, 0.5211]. the priced regions are disjoint with non-empty interior cells, so the registered ownership ladder resolves at this design's own precision.

| #90 ceiling | replicate sd | ceiling | status |
|---|---|---|---|
| Delta recovery (non-ergodic world) | 0.014128 | 0.020000 | `INFORMATIVE` |
| rho_own recovery (owned-slopes world) | 0.010107 | 0.020000 | `INFORMATIVE` |

### R3 — volume x score (`PASS`)

| clause | requirement | observed | status |
|---|---|---|---|
| **i** ERGODIC world (one beta for all, person intercepts UNCORRELATED with xbar_u): Delta_erg must read 0 | abs(mean) <= max(0.02, 3 x rep sd) = 0.057875 AND >= 6/8 CIs cover 0 | mean Delta +0.003458 over 8 replicates (sd 0.019292); 7/8 bootstrap CIs cover 0 | `PASS` |
| **ii** NON-ERGODIC world, a_u = gamma * xbar_u + noise: the DERIVED Delta is exactly gamma (within-centering annihilates a_u so level 2 reads beta, while level 1 reads beta + gamma), planted gamma = +0.2500 | abs(gap) <= max(0.02, 3 x rep sd) = 0.026025 | mean Delta +0.255285 (sd 0.008675), gap +0.005285 = 0.61 replicate sd | `PASS` |
| **ii-ceiling** #90 PRECISION CEILING on clause (ii): the replicate spread of the recovery must itself be inside the registered tolerance floor (0.02 in Delta units), else the clause certifies nothing | rep sd <= the tolerance floor (else UNINFORMATIVE) | replicate sd 0.008675 against the ceiling 0.02 | `PASS` |
| **iii** NULL world (beta = 0 everywhere, intercepts unrelated to x): ALL FOUR objects must read 0 within their own band or interval | >= 6/8 on each of the five coverage counts | beta_between +0.008025 (7/8 CIs cover 0); beta_within +0.000187 (6/8); Delta +0.007838 (7/8); rho_own +0.0045 (8/8 CIs cover 0, 8/8 points inside the pairing band) | `PASS` |
| **iv** #85b bootstrap-zero on the NULL world: every interval must cover 0 AND cover its own point | >= 6/8 on both counts | Delta CIs covering 0: 7/8; rho_own CIs covering their own point: 8/8 | `PASS` |
| **v** #88a REGION PRICING executed in-leg on THIS relation's skeleton: the boundary half-widths for both routed objects are the realized bootstrap half-widths on the matched planted worlds, pinned BEFORE any real number | all three finite and positive, artifact written before the first real number | Delta region +-0.022525 (null world); rho region at 0.15 +-0.0290; at 0.50 +-0.0218; pinned 2026-08-21T01:57:05.638040Z | `PASS` |
| **vi** #91 LADDER COHERENCE on the priced regions: disjoint regions with non-empty interior cells, ELSE the ownership classification collapses EXPLICITLY to the binary | the check is ASSERTED and its outcome RECORDED; a collapse is a legitimate outcome and never stops the leg (the coarser partition is stated) | edges [0.1210, 0.1790] around 0.15 and [0.4782, 0.5218] around 0.50 -> COHERENT | `PASS` |

| descriptive | observed | status |
|---|---|---|
| **D1** LEVEL VALUE recovery, ergodic world (both levels must read the planted beta = -0.10) | beta_between -0.0965, beta_within -0.1000 | `ANNOTATED` |
| **D2** LEVEL VALUE recovery, non-ergodic world (beta_within = -0.10, beta_between = +0.15) | beta_between +0.1551, beta_within -0.1002 | `ANNOTATED` |
| **D3** the #89 den distribution the ownership mapping rides on — with the floor in the POOL, A_h = sigma^2 E[1/den] can no longer be dominated by a near-degenerate half | A_early 0.00439895 (median-based 0.00265947), A_late 0.00440969 (median-based 0.00268672); min den 20.7 / 12.83, median den 376 / 372.2; V = 0.004404, sd(beta_u) = 0.06637 | `ANNOTATED` |
| **D4** OWNERSHIP RECOVERY on this relation's skeleton (ROUTES only on R2; here it prices the rho regions and annotates) | planted 0.50 -> +0.5013 (sd 0.0126, half-width 0.0218); planted 0.15 -> +0.1458 (sd 0.0134, half-width 0.0290) | `ANNOTATED` |

Priced regions (#88a, pinned 2026-08-21T01:57:05.638040Z): Delta +-0.022525 from the `null` world; rho at 0.15 +-0.0290; rho at 0.50 +-0.0218. **#91 ladder: `COHERENT`** — edges [0.1210, 0.1790] and [0.4782, 0.5218]. the priced regions are disjoint with non-empty interior cells, so the registered ownership ladder resolves at this design's own precision.

| #90 ceiling | replicate sd | ceiling | status |
|---|---|---|---|
| Delta recovery (non-ergodic world) | 0.008675 | 0.020000 | `INFORMATIVE` |
| rho_own recovery (owned-slopes world) | 0.012580 | 0.020000 | `INFORMATIVE` |

### R4 — commonness x score (`PASS`)

| clause | requirement | observed | status |
|---|---|---|---|
| **i** ERGODIC world (one beta for all, person intercepts UNCORRELATED with xbar_u): Delta_erg must read 0 | abs(mean) <= max(0.02, 3 x rep sd) = 0.035820 AND >= 6/8 CIs cover 0 | mean Delta -0.001790 over 8 replicates (sd 0.011940); 8/8 bootstrap CIs cover 0 | `PASS` |
| **ii** NON-ERGODIC world, a_u = gamma * xbar_u + noise: the DERIVED Delta is exactly gamma (within-centering annihilates a_u so level 2 reads beta, while level 1 reads beta + gamma), planted gamma = +0.2500 | abs(gap) <= max(0.02, 3 x rep sd) = 0.054182 | mean Delta +0.248453 (sd 0.018061), gap -0.001547 = 0.09 replicate sd | `PASS` |
| **ii-ceiling** #90 PRECISION CEILING on clause (ii): the replicate spread of the recovery must itself be inside the registered tolerance floor (0.02 in Delta units), else the clause certifies nothing | rep sd <= the tolerance floor (else UNINFORMATIVE) | replicate sd 0.018061 against the ceiling 0.02 | `PASS` |
| **iii** NULL world (beta = 0 everywhere, intercepts unrelated to x): ALL FOUR objects must read 0 within their own band or interval | >= 6/8 on each of the five coverage counts | beta_between +0.003926 (8/8 CIs cover 0); beta_within +0.000095 (7/8); Delta +0.003831 (8/8); rho_own +0.0001 (8/8 CIs cover 0, 7/8 points inside the pairing band) | `PASS` |
| **iv** #85b bootstrap-zero on the NULL world: every interval must cover 0 AND cover its own point | >= 6/8 on both counts | Delta CIs covering 0: 8/8; rho_own CIs covering their own point: 8/8 | `PASS` |
| **v** #88a REGION PRICING executed in-leg on THIS relation's skeleton: the boundary half-widths for both routed objects are the realized bootstrap half-widths on the matched planted worlds, pinned BEFORE any real number | all three finite and positive, artifact written before the first real number | Delta region +-0.021514 (null world); rho region at 0.15 +-0.0388; at 0.50 +-0.0306; pinned 2026-08-21T01:57:19.166902Z | `PASS` |
| **vi** #91 LADDER COHERENCE on the priced regions: disjoint regions with non-empty interior cells, ELSE the ownership classification collapses EXPLICITLY to the binary | the check is ASSERTED and its outcome RECORDED; a collapse is a legitimate outcome and never stops the leg (the coarser partition is stated) | edges [0.1112, 0.1888] around 0.15 and [0.4694, 0.5306] around 0.50 -> COHERENT | `PASS` |

| descriptive | observed | status |
|---|---|---|
| **D1** LEVEL VALUE recovery, ergodic world (both levels must read the planted beta = -0.10) | beta_between -0.1016, beta_within -0.0998 | `ANNOTATED` |
| **D2** LEVEL VALUE recovery, non-ergodic world (beta_within = -0.10, beta_between = +0.15) | beta_between +0.1486, beta_within -0.0999 | `ANNOTATED` |
| **D3** the #89 den distribution the ownership mapping rides on — with the floor in the POOL, A_h = sigma^2 E[1/den] can no longer be dominated by a near-degenerate half | A_early 0.00776004 (median-based 0.00323512), A_late 0.00740677 (median-based 0.00308146); min den 1.148 / 1.248, median den 309.1 / 324.5; V = 0.007582, sd(beta_u) = 0.08708 | `ANNOTATED` |
| **D4** OWNERSHIP RECOVERY on this relation's skeleton (ROUTES only on R2; here it prices the rho regions and annotates) | planted 0.50 -> +0.4994 (sd 0.0090, half-width 0.0306); planted 0.15 -> +0.1490 (sd 0.0102, half-width 0.0388) | `ANNOTATED` |

Priced regions (#88a, pinned 2026-08-21T01:57:19.166902Z): Delta +-0.021514 from the `null` world; rho at 0.15 +-0.0388; rho at 0.50 +-0.0306. **#91 ladder: `COHERENT`** — edges [0.1112, 0.1888] and [0.4694, 0.5306]. the priced regions are disjoint with non-empty interior cells, so the registered ownership ladder resolves at this design's own precision.

| #90 ceiling | replicate sd | ceiling | status |
|---|---|---|---|
| Delta recovery (non-ergodic world) | 0.018061 | 0.020000 | `INFORMATIVE` |
| rho_own recovery (owned-slopes world) | 0.008986 | 0.020000 | `INFORMATIVE` |

### R5 — commonness x gap (`PASS`)

| clause | requirement | observed | status |
|---|---|---|---|
| **i** ERGODIC world (one beta for all, person intercepts UNCORRELATED with xbar_u): Delta_erg must read 0 | abs(mean) <= max(0.02, 3 x rep sd) = 0.049026 AND >= 6/8 CIs cover 0 | mean Delta -0.006324 over 8 replicates (sd 0.016342); 6/8 bootstrap CIs cover 0 | `PASS` |
| **ii** NON-ERGODIC world, a_u = gamma * xbar_u + noise: the DERIVED Delta is exactly gamma (within-centering annihilates a_u so level 2 reads beta, while level 1 reads beta + gamma), planted gamma = +0.2500 | abs(gap) <= max(0.02, 3 x rep sd) = 0.038729 | mean Delta +0.250591 (sd 0.012910), gap +0.000591 = 0.05 replicate sd | `PASS` |
| **ii-ceiling** #90 PRECISION CEILING on clause (ii): the replicate spread of the recovery must itself be inside the registered tolerance floor (0.02 in Delta units), else the clause certifies nothing | rep sd <= the tolerance floor (else UNINFORMATIVE) | replicate sd 0.012910 against the ceiling 0.02 | `PASS` |
| **iii** NULL world (beta = 0 everywhere, intercepts unrelated to x): ALL FOUR objects must read 0 within their own band or interval | >= 6/8 on each of the five coverage counts | beta_between +0.003801 (8/8 CIs cover 0); beta_within +0.000031 (8/8); Delta +0.003770 (8/8); rho_own -0.0025 (8/8 CIs cover 0, 7/8 points inside the pairing band) | `PASS` |
| **iv** #85b bootstrap-zero on the NULL world: every interval must cover 0 AND cover its own point | >= 6/8 on both counts | Delta CIs covering 0: 8/8; rho_own CIs covering their own point: 8/8 | `PASS` |
| **v** #88a REGION PRICING executed in-leg on THIS relation's skeleton: the boundary half-widths for both routed objects are the realized bootstrap half-widths on the matched planted worlds, pinned BEFORE any real number | all three finite and positive, artifact written before the first real number | Delta region +-0.021404 (null world); rho region at 0.15 +-0.0377; at 0.50 +-0.0292; pinned 2026-08-21T01:57:32.568410Z | `PASS` |
| **vi** #91 LADDER COHERENCE on the priced regions: disjoint regions with non-empty interior cells, ELSE the ownership classification collapses EXPLICITLY to the binary | the check is ASSERTED and its outcome RECORDED; a collapse is a legitimate outcome and never stops the leg (the coarser partition is stated) | edges [0.1123, 0.1877] around 0.15 and [0.4708, 0.5292] around 0.50 -> COHERENT | `PASS` |

| descriptive | observed | status |
|---|---|---|
| **D1** LEVEL VALUE recovery, ergodic world (both levels must read the planted beta = -0.10) | beta_between -0.1064, beta_within -0.1001 | `ANNOTATED` |
| **D2** LEVEL VALUE recovery, non-ergodic world (beta_within = -0.10, beta_between = +0.15) | beta_between +0.1507, beta_within -0.0999 | `ANNOTATED` |
| **D3** the #89 den distribution the ownership mapping rides on — with the floor in the POOL, A_h = sigma^2 E[1/den] can no longer be dominated by a near-degenerate half | A_early 0.00777354 (median-based 0.00325717), A_late 0.00740111 (median-based 0.003082); min den 1.148 / 1.248, median den 307 / 324.5; V = 0.007586, sd(beta_u) = 0.0871 | `ANNOTATED` |
| **D4** OWNERSHIP RECOVERY on this relation's skeleton (ROUTES only on R2; here it prices the rho regions and annotates) | planted 0.50 -> +0.5047 (sd 0.0172, half-width 0.0292); planted 0.15 -> +0.1500 (sd 0.0216, half-width 0.0377) | `ANNOTATED` |

Priced regions (#88a, pinned 2026-08-21T01:57:32.568410Z): Delta +-0.021404 from the `null` world; rho at 0.15 +-0.0377; rho at 0.50 +-0.0292. **#91 ladder: `COHERENT`** — edges [0.1123, 0.1877] and [0.4708, 0.5292]. the priced regions are disjoint with non-empty interior cells, so the registered ownership ladder resolves at this design's own precision.

| #90 ceiling | replicate sd | ceiling | status |
|---|---|---|---|
| Delta recovery (non-ergodic world) | 0.012910 | 0.020000 | `INFORMATIVE` |
| rho_own recovery (owned-slopes world) | 0.017152 | 0.020000 | `INFORMATIVE` |

## The three levels in full (disjoint cohort)

| relation | level 1 beta_between [CI] | level 2 beta_within [CI] | level 2 early / late | level 3 mean beta | Var(beta) cross-half | rho_own pairing band |
|---|---|---|---|---|---|---|
| **R1** | 0.069062 [0.048843, 0.090518] | -0.007316 [-0.011278, -0.003048] | -0.014776 / 0.000144 | 0.007039 | 0.007987 | [-0.0218, 0.0205] |
| **R2** | 0.078450 [0.059120, 0.096287] | 0.059092 [0.055225, 0.063252] | 0.063847 / 0.054338 | 0.034809 | 0.004709 | [-0.0232, 0.0185] |
| **R3** | 0.006501 [-0.005425, 0.018710] | 0.005172 [0.002502, 0.007958] | 0.003101 / 0.007242 | 0.008035 | 0.002423 | [-0.0232, 0.0218] |
| **R4** | -0.022737 [-0.032957, -0.012321] | 0.001884 [-0.001381, 0.005120] | 0.005064 / -0.001295 | 0.013785 | 0.004483 | [-0.0229, 0.0225] |
| **R5** | -0.256325 [-0.278905, -0.232293] | -0.073531 [-0.076915, -0.070407] | -0.075749 / -0.071313 | -0.069682 | 0.007731 | [-0.0237, 0.0225] |

## Registered leans

| lean | registered | observed | status |
|---|---|---|---|
| R2 (gap x volume): beta_within > 0 — rest precedes longer comments | `directional, weakly held` | +0.059092 | `HELD` |
| R2: Delta cell NONERGODIC_SAME_SIGN | `NONERGODIC_SAME_SIGN` | LEVELS_INDISTINGUISHABLE | `BROKEN` |
| R3 (volume x score): both slopes positive and small | `both positive` | beta_between +0.006501, beta_within +0.005172 | `HELD` |
| R3: Delta cell SAME_SIGN or LEVELS_INDISTINGUISHABLE | `NONERGODIC_SAME_SIGN | LEVELS_INDISTINGUISHABLE` | LEVELS_INDISTINGUISHABLE | `HELD` |
| R4 (commonness x score): beta_within > 0 — bigger venue, more eyes, more score | `directional, weakly held` | +0.001884 | `HELD` |
| R4: Delta cell NONERGODIC_SAME_SIGN | `NONERGODIC_SAME_SIGN` | NONERGODIC_SIGN_UNRESOLVED | `BROKEN` |
| R5 (commonness x gap): REGISTERED UNLEANED (no defensible prior) | `unleaned` | beta_between -0.256325, beta_within -0.073531, cell NONERGODIC_SAME_SIGN | `N/A — REGISTERED UNLEANED` |
| the atlas summary is ATLAS_HETEROGENEOUS | `ATLAS_HETEROGENEOUS` | ATLAS_HETEROGENEOUS | `HELD` |
| the ~0.27 level-3 plateau appears for >= 2 of the four new relations (disjoint) — the plateau's first PREDICTION | `>= 2 points in [0.25, 0.3]` | 1 of 4 in band; R2 +0.4151, R3 +0.3585, R4 +0.2863, R5 +0.2164 | `BROKEN` |

**5 held, 3 broken**, one registered unleaned.

## Cohort divergences (#73) and priced-region straddles (#87)

| relation | object | note | detail |
|---|---|---|---|
| R1 | Delta_erg | #73 divergence; the disjoint cohort routes | disjoint 0.0764 vs Big5 0.0608 |
| R1 | Delta_erg | #87 straddle: the CI crosses the priced region edge(s) 0.0215 | big5 |
| R2 | rho_own | #73 divergence; the disjoint cohort routes | disjoint 0.4151 vs Big5 0.5380 |
| R2 | Delta_erg | #87 straddle: the CI crosses the priced region edge(s) 0.0192 | disjoint |
| R2 | Delta_erg | #87 straddle: the CI crosses the priced region edge(s) 0.0192 | big5 |
| R2 | rho_own | #87 straddle: the CI crosses the priced region edge(s) 0.5211 | big5 |
| R3 | Delta_erg | #87 straddle: the CI crosses the priced region edge(s) -0.0225 | big5 |
| R3 | rho_own | #87 straddle: the CI crosses the priced region edge(s) 0.4782 | big5 |
| R4 | Delta_erg | #73 divergence; the disjoint cohort routes | disjoint -0.0246 vs Big5 -0.0027 |
| R4 | Delta_erg | #87 straddle: the CI crosses the priced region edge(s) -0.0215 | disjoint |
| R4 | Delta_erg | #87 straddle: the CI crosses the priced region edge(s) -0.0215, 0.0215 | big5 |
| R5 | rho_own | #87 straddle: the CI crosses the priced region edge(s) 0.1877 | disjoint |
| R5 | rho_own | #87 straddle: the CI crosses the priced region edge(s) 0.1123, 0.1877 | big5 |

## Honest anomalies

- **the atlas's five relations are NOT five separate measurements.** three of the five share the commonness channel (R1, R4, R5), two share the volume channel as y (R1, R2) and two share the score channel as y (R3, R4). The relations are five PROJECTIONS of one event stream, so agreement between two of them is partly shared measurement and never a fresh replication. The atlas reports the map, not five verdicts.
- **slog(score) is PLATFORM FEEDBACK, not quality.** `score` is the net of other users' votes as PANDORA recorded it: it moves with visibility, timing, subreddit size and vote dynamics. R3 and R4 measure how much feedback an utterance attracts, never whether it deserved it, and the sign transform slog(s) = sign(s) log1p(|s|) is used because the counter is signed. 147 of 17,640,062 parseable rows carry no score and are dropped from R3 and R4 only.
- **the gap channel drops events, and the drops are not random.** the relations that use it (R2, R5) lose the first event of every author's stream and every event whose created_utc ties its predecessor's — a tie is a burst of same-second comments, so the drop is concentrated in exactly the fastest activity. The cache records 433,827 nonpositive gaps against 9,124 first events over the candidate stream's predecessors.
- **R1: level 2 is a two-number average whose two numbers disagree.** the within-person slope reads -0.014776 on the early half and +0.000144 on the late half against the registered estimand -0.007316. The registration pins the average and that is what routes, but level 2 is not a stationary quantity here, and nothing in this leg separates calendar drift from a composition change or from the half split itself.
- **R4: level 2 is a two-number average whose two numbers disagree.** the within-person slope reads +0.005064 on the early half and -0.001295 on the late half against the registered estimand +0.001884. The registration pins the average and that is what routes, but level 2 is not a stationary quantity here, and nothing in this leg separates calendar drift from a composition change or from the half split itself.
- **R4: a #90 ceiling passed with little room.** Delta recovery (non-ergodic world) has replicate sd 0.018061 against the ceiling 0.0200 — 90% of it. The clause is INFORMATIVE as registered, but a design with a little less precision would have stopped the leg here, and the reader should know the margin was thin.
- **R5: a #90 ceiling passed with little room.** rho_own recovery (owned-slopes world) has replicate sd 0.017152 against the ceiling 0.0200 — 86% of it. The clause is INFORMATIVE as registered, but a design with a little less precision would have stopped the leg here, and the reader should know the margin was thin.
- **R2 / disjoint: the LEVELS_INDISTINGUISHABLE cell is decided by a hair.** Delta = +0.019358 with CI [-0.001034, +0.037833]: the interval covers zero by 0.001034, which is 2.7% of its own width. NULL-first routing calls this cell and the call stands, but it is a power-limited null and not an equivalence claim — the scoped reading in the boundaries applies with full force here.

## The reading, in the bridge's vocabulary

This leg is item 2 of the measurement-series bridge's build-out (`docs/SUICA_MEASUREMENT_SERIES_BRIDGE.md`, section 5): *the map of the ergodicity contrast* — not one relation but several, so the question becomes WHICH KINDS of relation carry a large level-conflation error. The vocabulary is the owner's conference input and its source paper: 三枝高大・下司忠大 (2025). 個人差研究における個人間関係の解釈の誤り——測定系列の混同に対する警鐘. パーソナリティ研究, 34(2), 119–134 (Saegusa & Geshi 2025, JJP 34(2) 119–134). Its three measurement series map onto this leg exactly: measuring a group once gives the BETWEEN-person relation (level 1, beta_between); measuring many people repeatedly gives the AVERAGE WITHIN-person relation (level 2, beta_within); measuring one person repeatedly gives THAT person's relation (level 3, beta_{u,h}), whose reliability as a personal attribute is rho_own.

On the disjoint cohort the atlas reads **ATLAS_HETEROGENEOUS**: R1 (commonness x volume) NONERGODIC_SIGN_FLIP; R2 (gap x volume) LEVELS_INDISTINGUISHABLE; R3 (volume x score) LEVELS_INDISTINGUISHABLE; R4 (commonness x score) NONERGODIC_SIGN_UNRESOLVED; R5 (commonness x gap) NONERGODIC_SAME_SIGN. Where the cell is nonergodic, reading the within-person relation off the between-person one is an error of the size Delta_erg names — and where the signs differ it is an error of DIRECTION, not of magnitude. Where the cell is LEVELS_INDISTINGUISHABLE the two series agree at this resolution, which is a scoped null and not an equivalence claim.

The largest conflation error in the atlas is **R5** (commonness x gap): level 1 reads -0.2563 against level 2's -0.0735, a difference of -0.1828 [-0.2051, -0.1587] — 2.5 times the within-person slope itself. Reading the within-person relation off the between-person one would overstate it by that factor.

For the level-3 reliability catalogue (build-out item 3) the atlas contributes 4 new ownership correlations, of which 1 falls in the [0.25, 0.3] band that X1c's 0.279, X2's 0.259 and X4's floored 0.277 already occupy. The plateau was registered here as a PREDICTION rather than an observation, and its outcome is **BROKEN**: the five values run from +0.2164 (R5) to +0.4151 (R2), a spread of 0.1987 on one cohort at one span. Level-3 reliability is therefore a property of the RELATION and not a constant of the corpus — which is what a catalogue is for, and it is the atlas's most useful negative result for the owner's manuscript.

## Boundaries

- **Metadata only; VOLUME, TIMING and PLATFORM FEEDBACK, never content (permanent).** The text-derived quantity in this leg is `word_count_quoteless`, the author's own-word count per comment. No body was read, no topic, no style, no sentiment. The other channels are a community's share of the whole event stream, the seconds between one comment and the next, and the recorded `score`. Every claim is about HOW MUCH is written, WHEN, WHERE and WITH WHAT RESPONSE — never about WHAT is written.
- **`slog(score)` is platform feedback, not quality.** The score column is the net of other users' votes as the corpus recorded it. It moves with visibility, timing, community size and vote dynamics. R3 and R4 measure how much feedback an utterance attracts; nothing here says an utterance deserved its score, and no evaluative reading is licensed.
- **The projection caution.** beta_between, beta_within and beta_{u,h} are STATIC projections of much richer dynamic objects. Five scalar relations measured at three levels say nothing about lags, about how a relation moves within a half, or about any coordinate not projected. A level difference is a statement about these projections at this resolution; a null is not an equivalence claim.
- **No psychological naming.** Expression volume, its community gradient, its rhythm and its feedback are technical objects. Nothing here is a trait, a state, a disposition or a preference, and the leg is label-free: `author_profiles.csv` was never opened.
- **EXPLORATORY, corpus-level.** No person-level claim is licensed. The per-author slopes exist only as the population of a mean, a covariance and one correlation; no individual's beta is a measurement of that individual.
- **The cohort-selection caveat (carried from X2/X4).** A Big5/disjoint difference cannot be separated from HOW the 1,401 Big5 authors were selected. The disjoint cohort is also TYPOLOGY-ENRICHED by construction (PANDORA's non-Big5 authors are MBTI-labelled users), so both cohorts are platform samples with a selection, not population samples.
- **Pool selection, per relation.** Each relation floors at 50 USABLE events in EACH half AND at the #89 estimability floor, so each speaks for authors who are ACTIVE ON BOTH SIDES of their own median AND whose x actually varies within each half. Nothing here speaks for short-lived, low-volume or single-community accounts, and the five pools are not the same set of people.
- **The owner's three-level schema, cited and not claimed.** The between / average-within / single-person trichotomy is the program OWNER's conference input (relayed 2026-08-19) and the framework of Saegusa & Geshi (2025). This leg supplies a corpus instance of the schema on metadata; it does not supply the schema.

## Configuration

| key | value |
|---|---|
| `atlas_route_2_refinement` | `route 2 fires only when all five relations sit in the SAME nonergodic cell; five relations in two different nonergodic cells is route 3, and both predicates are recorded` |
| `author_profiles_csv` | `NEVER OPENED (label-free)` |
| `b_boot` | `1000` |
| `b_perm` | `499` |
| `boundary_centres` | `{"delta": 0.0, "rho_low": 0.15, "rho_high": 0.5}` |
| `boundary_half_widths` | `PRICED IN-LEG (#88a) per relation from that relation's matched planted worlds` |
| `cohort` | `/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/results/m4_sr0_recon/cohort_authors.csv` |
| `columns_read` | `["author", "subreddit", "created_utc", "word_count_quoteless", "score"]` |
| `comments` | `/Volumes/mobile3/projects/project persona/data_sets/PANDORA_official/all_comments_since_2015.csv` |
| `ergodic_cover_floor` | `6` |
| `estimability_floor_den` | `1.0` |
| `estimability_floor_path` | `PINNED two-pass float64: cell mean by bincount sum / bincount count, then bincount of the squared deviations` |
| `gap_rule` | `log10 seconds since the author's previous comment over the full stream; the first event of an author is dropped and so is any nonpositive gap` |
| `halves` | `full-stream median of the author's created_utc, <= early` |
| `leg` | `M4-X5` |
| `level_3_estimator` | `the FLOORED per-author slope throughout; the pool's own floor makes every scored cell estimable, and authors failing the floor are excluded and counted` |
| `n_synth_replicates` | `8` |
| `order` | `per-author stable sort by created_utc (ties keep stream order)` |
| `ownership_recovery_routes_on` | `R2` |
| `planted_beta` | `-0.1` |
| `planted_gamma` | `0.25` |
| `planted_sd_intercept` | `0.5` |
| `planted_sd_noise` | `1.0` |
| `plateau_band` | `[0.25, 0.3]` |
| `plateau_min_relations` | `2` |
| `pool` | `>= 50 USABLE events in EACH half AND the #89 estimability floor den >= 1 in EACH half` |
| `pool_floor_events` | `50` |
| `question_provenance` | `the program OWNER's conference input (relayed 2026-08-19) and the measurement-series bridge, build-out item 2` |
| `registration` | `docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md, section X5, commit de09409` |
| `relations` | `{"R1": {"title": "commonness x volume", "x": "log10(community share of all parseable events)", "y": "log1p(word_count_quoteless)", "imported": true}, "R2": {"title": "gap x volume", "x": "log10(seconds since the author's previous comment, full stream)", "y": "log1p(word_count_quoteless)", "imported": false}, "R3": {"title": "volume x score", "x": "log1p(word_count_quoteless)", "y": "slog(score) = sign(score) * log1p(abs(score))", "imported": false}, "R4": {"title": "commonness x score", "x": "log10(community share of all parseable events)", "y": "slog(score) = sign(score) * log1p(abs(score))", "imported": false}, "R5": {"title": "commonness x gap", "x": "log10(community share of all parseable events)", "y": "log10(seconds since the author's previous comment, full stream)", "imported": false}}` |
| `rho_price_low` | `0.15` |
| `rho_true_target` | `0.5` |
| `score_rule` | `slog(score) = sign(score) * log1p(abs(score)); rows with a missing score are dropped from the relations that use it` |
| `seed` | `20260819` |
| `seed_boot` | `20260822` |
| `seed_part0` | `20260820` |
| `seed_perm` | `20260821` |
| `tol_floor_delta` | `0.02` |
| `tol_floor_rho` | `0.02` |
| `tol_rule` | `max(floor, 3.0 x replicate sd), with the #90 CEILING replicate sd <= floor asserted on every routing recovery clause` |

Config SHA-256 `3b32bf9087d7ad36f7cd5de0057c6124abcd0f3fe80f9d826231c22c12835912`. Run finished 2026-08-21T01:57:35.227442Z in 58.7 s.

