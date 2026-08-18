# SUICA M4-W1 — slow-time law transport to the disjoint cohort

**Outcome: `COMMON_STANDING`.**

**Λ = λ_distinct − λ_common = 0.0911/y [0.0628, 0.1490]** on the LAW arm at the registered configuration q = 0.5 / m = 10 (1,211,631 self pairs and 3,241 contributing authors in the 2–3y bin, 125,555 blocks). The verdict criterion is this bootstrap interval and nothing else.

**THE MIDDLE CLOSES.** Λ's bootstrap interval lies strictly above zero on a cohort disjoint from the one that produced the provisional sign: the DISTINCTIVE carrier decays faster than the COMMON carrier, so the common mass is the standing part over the three-year window. The T-line proposition acquires its When clause on fresh authors.

Realized half-width 0.0431/y against the registered projection ±0.044/y (ratio 0.979); 1,000 of 1,000 bootstrap replicates retained (0 dropped for a non-positive E(b) in one of the two rows).

## Gates

| gate | status |
|---|---|
| disjoint cache anchors (14,634,702 events / 8,895 authors / 1,443 vocabulary / coverage 0.7587) | `PASS` |
| W1 census anchors #78 (16 pinned predicates, re-executed exactly) | `PASS` |
| frozen instrument objects (1191 vocabulary / 32 Common) | `PASS` |
| clean-arm removal set (22 typology communities present in the law vocabulary) | `PASS` |
| taste-row fold purity (mass identity, zero test mass) | `PASS` |
| sufficiency targets #69 (>= 100k pairs, >= 400 authors at m=10) | `PASS` |
| cohort disjointness (zero authors shared with the 1401) | `PASS` |
| no synthetic gate required (R layer, no world simulated) | `N/A` |
| ID-leak scan (0 NEW hits of 10,296 author names over the committed files; 3 pre-existing dictionary collisions carried unchanged from HEAD) | `PASS` |

The ID-leak universe is every author name in the comments file — 10,296 candidates, the 1,401 source cohort plus the 8,895 disjoint authors — and the scan list itself is written only into gitignored `results/`. At that size the substring matcher acquires DICTIONARY COLLISIONS: 3 candidate names are ordinary English words or bare digit runs that already occur in prose committed long before this leg. Collisions are separated from leaks mechanically — a hit counts as pre-existing only when the same scanner produces the identical hit, same file and same line, on that file's version at HEAD — and this leg only APPENDS to the two pre-existing documents. Files this leg authors have no HEAD version and therefore zero tolerance. NEW hits: 0.

## Census — the registered predicates, re-executed (#78)

| pinned quantity | registered | observed | status |
|---|---|---|---|
| disjoint_events | 14,634,702 | 14,634,702 | `PASS` |
| authors_seen | 8,895 | 8,895 | `PASS` |
| vocabulary_floor_users | 89 | 89 | `PASS` |
| law_vocabulary | 1,443 | 1,443 | `PASS` |
| law_coverage | 0.7587 | 0.7587 | `PASS` |
| common_q50 | 71 | 71 | `PASS` |
| typology_in_vocabulary | 22 | 22 | `PASS` |
| typology_in_common | 8 | 8 | `PASS` |
| pool_authors | 6,111 | 6,111 | `PASS` |
| pool_blocks | 213,489 | 213,489 | `PASS` |
| quarters | 18 | 18 | `PASS` |
| self_pairs_2_3y | 2,591,663 | 2,591,663 | `PASS` |
| gate_m10_pairs | 1,211,631 | 1,211,631 | `PASS` |
| gate_m10_authors | 3,241 | 3,241 | `PASS` |
| gate_m5_pairs | 1,790,865 | 1,790,865 | `PASS` |
| gate_m5_authors | 3,746 | 3,746 | `PASS` |

Self pairs by bin over the whole pool: 0-90d 2,814,112, 90-180d 2,310,348, 180-365d 3,802,118, 1-2y 4,947,253, 2-3y 2,591,663, 3y+ 1,004,737. The 3y+ bin is descriptive and never enters a fit.

Common(0.5) carries 0.5022 of the in-vocabulary event mass in 71 communities; the distinctive tail is 1,372 communities. The intersection predicate is m ≤ (common events in the block) ≤ K − m at K = 50.

## The four-row rate table — LAW arm (PRIMARY)

| row | λ (1/y) | 95% CI | half-width | R² (log-linear) | E₀ | F = E(2–3y)/E(0–90d) | D |
|---|---|---|---|---|---|---|---|
| full vocabulary | **0.1236** | [0.0591, 0.2520] | 0.0964 | 0.9251 | 0.5174 | 0.7360 | 0.1408 |
| common (q=0.5, 71 communities) | **0.0901** | [0.0362, 0.2069] | 0.0853 | 0.9421 | 0.5526 | 0.8014 | 0.1117 |
| distinctive (q=0.5, 1372 communities) | **0.1812** | [0.1045, 0.3223] | 0.1089 | 0.9225 | 0.4599 | 0.6392 | 0.1734 |
| taste (per-fold PPMI+SVD d=64, out-of-fold) | **0.1010** | [0.0854, 0.1345] | 0.0245 | 0.9815 | 0.2804 | 0.7838 | 0.0610 |

Fitted on the five verdict bins at realized mean gaps 0.121y, 0.366y, 0.736y, 1.452y, 2.434y; the 3y+ bin (3.423y) is descriptive only: full E = 0.3890, common E = 0.4459, distinct E = 0.3024, taste E = 0.2048.

### Λ and its nulls

| quantity | value |
|---|---|
| Λ point | **0.0911**/y |
| Λ 95% bootstrap CI (THE VERDICT) | [0.0628, 0.1490] |
| CI half-width | 0.0431 |
| registered projection | ±0.044 (ratio 0.979) |
| log-form permutation null centre | 0.1287 (37 of 499 replicates retained) |
| LINEAR slope contrast (domain-safe, #80a) | 0.0236 |
| LINEAR null centre / band | 0.0001 / [-0.0008, 0.0009] (1.000 finite) |

The log-form null is undefined on most permutation replicates (a within-quarter relabelling drives E(b) to zero and its sign then flips freely), which is why the registration poses the Λ null on the LINEAR slope contrast; both are reported and NEITHER routes.

### E(b) by bin — LAW arm

| row | 0-90d | 90-180d | 180-365d | 1-2y | 2-3y | 3y+ |
|---|---|---|---|---|---|---|
| full E(b) | 0.5332 | 0.4869 | 0.4599 | 0.4208 | 0.3925 | 0.3890 |
| full 95% CI | [0.4686, 0.6023] | [0.4124, 0.5666] | [0.3726, 0.5505] | [0.3159, 0.5266] | [0.2644, 0.5146] | [0.2194, 0.5414] |
| full null centre | -0.0000 | 0.0000 | 0.0001 | 0.0000 | 0.0000 | 0.0000 |
| full self pairs | 1,241,406 | 1,043,746 | 1,751,941 | 2,291,654 | 1,211,631 | 481,502 |
| common E(b) | 0.5625 | 0.5293 | 0.5086 | 0.4765 | 0.4508 | 0.4459 |
| common 95% CI | [0.4964, 0.6349] | [0.4535, 0.6104] | [0.4178, 0.6014] | [0.3649, 0.5832] | [0.3116, 0.5747] | [0.2670, 0.5965] |
| common null centre | -0.0000 | -0.0000 | 0.0000 | 0.0001 | 0.0000 | -0.0000 |
| common self pairs | 1,241,406 | 1,043,746 | 1,751,941 | 2,291,654 | 1,211,631 | 481,502 |
| distinct E(b) | 0.4807 | 0.4213 | 0.3869 | 0.3385 | 0.3072 | 0.3024 |
| distinct 95% CI | [0.4253, 0.5344] | [0.3561, 0.4859] | [0.3115, 0.4625] | [0.2530, 0.4254] | [0.2027, 0.4087] | [0.1564, 0.4322] |
| distinct null centre | -0.0000 | 0.0000 | -0.0000 | 0.0000 | 0.0000 | -0.0000 |
| distinct self pairs | 1,241,406 | 1,043,746 | 1,751,941 | 2,291,654 | 1,211,631 | 481,502 |
| taste E(b) | 0.2823 | 0.2680 | 0.2577 | 0.2400 | 0.2212 | 0.2048 |
| taste 95% CI | [0.2705, 0.2894] | [0.2541, 0.2756] | [0.2417, 0.2661] | [0.2213, 0.2496] | [0.1977, 0.2338] | [0.1768, 0.2215] |
| taste null centre | -0.0000 | -0.0000 | -0.0000 | 0.0000 | -0.0001 | -0.0000 |
| taste self pairs | 1,241,406 | 1,043,746 | 1,751,941 | 2,291,654 | 1,211,631 | 481,502 |

Per-bin permutation null centres are the within-quarter block-to-author reassignment (B = 499), expected ≈ 0 by construction; they are the location check on the epoch-matched excess, not a test.

## The sealed-prediction transport table (SECONDARY — never routes)

| quantity | source (1401 cohort) | target (disjoint cohort) | source cell | target cell | CIs overlap | classification |
|---|---|---|---|---|---|---|
| Λ = λ_distinct − λ_common | 0.0741 [-0.0558, 0.1854] | **0.0911** [0.0628, 0.1490] | `SIGN_UNRESOLVED` | `COMMON_STANDING` | yes | **BREAKS** |
| floor share E(2–3y)/E(0–90d), full row | 0.5348 [0.4203, 0.6320] | **0.7360** [0.5453, 0.8568] | `POSITIVE` | `POSITIVE` | yes | **REPRODUCES** |
| D = E(0–90d) − E(2–3y), full row | 0.3058 [0.2364, 0.3855] | **0.1408** [0.0850, 0.2224] | `POSITIVE` | `POSITIVE` | no | **SHIFTS** |
| λ_full | 0.2943 [0.1895, 0.4405] | **0.1236** [0.0591, 0.2520] | `POSITIVE` | `POSITIVE` | yes | **REPRODUCES** |
| λ_taste is the SMALLEST of the four rows (held in both U2c arms) | `ORDER HOLDS` | slowest row `common` | `ORDER HOLDS` | `ORDER BREAKS` | — | **BREAKS** |

Classification is the registered rule, applied as written: REPRODUCES = the target CI meets the source CI AND the sign/cell agrees; SHIFTS = disjoint CIs with the same sign/cell; BREAKS = a different sign/cell. 2 of 5 quantities BREAK, and both BREAKs need reading rather than reciting.

- **Λ = λ_distinct − λ_common — the BREAK is a PRECISION GAIN, not a contradiction.** The two intervals OVERLAP and the sealed source point 0.0741 lies INSIDE the target interval [0.0628, 0.1490]. What changed is resolution, not direction: the source half-width was 0.1206 and could not exclude zero, the target half-width is 0.0431 and does. The registered rule keys on the CELL, so this lands in BREAKS; the substance is that the disjoint cohort CONFIRMS the source's direction at a width the source never had.

- **The layer ordering BREAKS, but narrowly.** λ_taste is rank 2 of 4, 0.0110/y above the slowest row (`common`), and the taste row's own interval [0.0854, 0.1345] CONTAINS the slowest row's point. Order slowest-first: common 0.0901 < taste 0.1010 < full 0.1236 < distinct 0.1812.

The floor share and D move in opposite classifications for one reason, and it is worth stating plainly: the disjoint cohort's curve is FLATTER at both ends. The sealed source values imply a source curve running 0.6574 → 0.3516 across the window; the target full row runs 0.5332 → 0.3925. The disjoint cohort starts LOWER and ends HIGHER, so the RATIO (floor share) reproduces while the DIFFERENCE (D) shifts down. Part of that gap is the pool-versus-intersection provenance asymmetry disclosed above and part is the cohort; this leg does not separate them.

Source provenance, disclosed because it is heterogeneous: Λ = λ_distinct − λ_common — U2c primary arm (cohort 849 pool / 424 gate authors); floor share E(2–3y)/E(0–90d), full row — U2 primary arm (849-author pool, full vocabulary); D = E(0–90d) − E(2–3y), full row — U2 primary arm (849-author pool, full vocabulary); λ_full — U2c primary arm (cohort 849 pool / 424 gate authors).

## Arms

| arm | role | Λ | 95% CI | cell | blocks | authors (2–3y) |
|---|---|---|---|---|---|---|
| law (q=0.5, m=10) | PRIMARY (verdict + transport table) | 0.0911 | [0.0628, 0.1490] | `COMMON_STANDING` | 125,555 | 3,241 |
| instrument (frozen 1191 / Common 32, m=10) | sensitivity — frozen 1191 / Common 32 | 0.0644 | [0.0168, 0.1107] | `COMMON_STANDING` | 98,684 | 2,694 |
| clean_no_explicit_personality (q=0.5, m=10) | co-reported — typology ablation | 0.0780 | [0.0484, 0.1397] | `COMMON_STANDING` | 111,660 | 2,949 |
| law m=5 (q=0.5, m=5) | sensitivity — eligibility floor m = 5 | 0.0953 | [0.0648, 0.1509] | `COMMON_STANDING` | 161,577 | 3,746 |

### Instrument arm versus law arm

The frozen SR0 vocabulary carries 1,187 of its 1,191 community names into the disjoint stream, and the frozen 32-community Common(0.5) set holds 0.3473 of the disjoint cohort's in-frozen-vocabulary event mass (it held 0.5036 on the source cohort — the instrument does not carry its own mass split). Λ = 0.0644/y [0.0168, 0.1107] → `COMMON_STANDING` (98,684 blocks, 2,694 authors in the 2–3y bin), against the law arm's 0.0911/y [0.0628, 0.1490] → `COMMON_STANDING`.

| row | λ (1/y) | 95% CI | half-width | R² (log-linear) | E₀ | F = E(2–3y)/E(0–90d) | D |
|---|---|---|---|---|---|---|---|
| full vocabulary | **0.1844** | [0.1389, 0.2422] | 0.0517 | 0.9442 | 0.4671 | 0.6391 | 0.1741 |
| common (q=0.5, 32 communities) | **0.1507** | [0.1021, 0.2151] | 0.0565 | 0.9758 | 0.4865 | 0.6981 | 0.1485 |
| distinctive (q=0.5, 1159 communities) | **0.2151** | [0.1747, 0.2697] | 0.0475 | 0.9219 | 0.4334 | 0.5893 | 0.1874 |

| row | 0-90d | 90-180d | 180-365d | 1-2y | 2-3y | 3y+ |
|---|---|---|---|---|---|---|
| full E(b) | 0.4825 | 0.4305 | 0.3943 | 0.3439 | 0.3084 | 0.2523 |
| full 95% CI | [0.4616, 0.5012] | [0.4062, 0.4540] | [0.3647, 0.4223] | [0.3079, 0.3796] | [0.2660, 0.3487] | [0.1975, 0.3039] |
| full null centre | 0.0000 | 0.0000 | -0.0000 | -0.0000 | 0.0000 | 0.0001 |
| full self pairs | 711,831 | 579,541 | 932,921 | 1,154,481 | 576,153 | 200,488 |
| common E(b) | 0.4918 | 0.4569 | 0.4280 | 0.3830 | 0.3433 | 0.2692 |
| common 95% CI | [0.4723, 0.5108] | [0.4307, 0.4809] | [0.3941, 0.4587] | [0.3433, 0.4195] | [0.2910, 0.3895] | [0.2025, 0.3297] |
| common null centre | 0.0001 | 0.0001 | -0.0000 | -0.0001 | 0.0001 | 0.0001 |
| common self pairs | 711,831 | 579,541 | 932,921 | 1,154,481 | 576,153 | 200,488 |
| distinct E(b) | 0.4563 | 0.3924 | 0.3522 | 0.3013 | 0.2689 | 0.2273 |
| distinct 95% CI | [0.4334, 0.4779] | [0.3681, 0.4162] | [0.3252, 0.3786] | [0.2695, 0.3324] | [0.2308, 0.3013] | [0.1854, 0.2627] |
| distinct null centre | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| distinct self pairs | 711,831 | 579,541 | 932,921 | 1,154,481 | 576,153 | 200,488 |

### Clean arm (`clean_no_explicit_personality`)

22 explicit-typology communities were removed from the law vocabulary, leaving 1,421; the blocks were REBUILT over the reduced vocabulary and the mass split re-derived, giving Common(0.5) = 84 communities over a pool of 5,401 authors and 190,496 blocks. Λ = 0.0780/y [0.0484, 0.1397] → `COMMON_STANDING` (111,660 blocks, 2,949 authors in the 2–3y bin).

| row | λ (1/y) | 95% CI | half-width | R² (log-linear) | E₀ | F = E(2–3y)/E(0–90d) | D |
|---|---|---|---|---|---|---|---|
| full vocabulary | **0.1227** | [0.0599, 0.2625] | 0.1013 | 0.9227 | 0.5071 | 0.7377 | 0.1371 |
| common (q=0.5, 84 communities) | **0.0940** | [0.0395, 0.2270] | 0.0938 | 0.9383 | 0.5242 | 0.7935 | 0.1104 |
| distinctive (q=0.5, 1337 communities) | **0.1721** | [0.0979, 0.3246] | 0.1133 | 0.9151 | 0.4662 | 0.6533 | 0.1690 |

| row | 0-90d | 90-180d | 180-365d | 1-2y | 2-3y | 3y+ |
|---|---|---|---|---|---|---|
| full E(b) | 0.5228 | 0.4770 | 0.4516 | 0.4123 | 0.3857 | 0.3840 |
| full 95% CI | [0.4554, 0.5933] | [0.3989, 0.5576] | [0.3597, 0.5420] | [0.3013, 0.5163] | [0.2497, 0.5039] | [0.2094, 0.5301] |
| full null centre | 0.0000 | 0.0000 | 0.0000 | 0.0001 | -0.0000 | -0.0001 |
| full self pairs | 1,121,286 | 940,447 | 1,580,177 | 2,070,691 | 1,095,987 | 447,124 |
| common E(b) | 0.5345 | 0.5008 | 0.4811 | 0.4483 | 0.4242 | 0.4230 |
| common 95% CI | [0.4658, 0.6044] | [0.4204, 0.5781] | [0.3877, 0.5686] | [0.3320, 0.5488] | [0.2775, 0.5417] | [0.2391, 0.5642] |
| common null centre | -0.0000 | 0.0001 | 0.0001 | 0.0001 | -0.0001 | 0.0000 |
| common self pairs | 1,121,286 | 940,447 | 1,580,177 | 2,070,691 | 1,095,987 | 447,124 |
| distinct E(b) | 0.4876 | 0.4287 | 0.3955 | 0.3472 | 0.3185 | 0.3134 |
| distinct 95% CI | [0.4266, 0.5451] | [0.3595, 0.4984] | [0.3157, 0.4745] | [0.2530, 0.4387] | [0.2032, 0.4201] | [0.1579, 0.4451] |
| distinct null centre | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -0.0000 | 0.0000 |
| distinct self pairs | 1,121,286 | 940,447 | 1,580,177 | 2,070,691 | 1,095,987 | 447,124 |

Because the disjoint cohort is typology-enriched, a large clean-arm shift would localize the slow common mass in the typology communities themselves; a small one says the pattern is not a typology-forum artifact.

### m = 5 sensitivity

Λ = 0.0953/y [0.0648, 0.1509] → `COMMON_STANDING` (161,577 blocks, 3,746 authors in the 2–3y bin). Lowering the eligibility floor admits more lopsided blocks, which is a different sample rather than a bigger draw from the same one.

| row | λ (1/y) | 95% CI | half-width | R² (log-linear) | E₀ | F = E(2–3y)/E(0–90d) | D |
|---|---|---|---|---|---|---|---|
| full vocabulary | **0.1505** | [0.0815, 0.2626] | 0.0905 | 0.9447 | 0.5190 | 0.6903 | 0.1655 |
| common (q=0.5, 71 communities) | **0.1118** | [0.0543, 0.2169] | 0.0813 | 0.9603 | 0.5467 | 0.7604 | 0.1331 |
| distinctive (q=0.5, 1372 communities) | **0.2071** | [0.1278, 0.3328] | 0.1025 | 0.9394 | 0.4475 | 0.6013 | 0.1860 |

| row | 0-90d | 90-180d | 180-365d | 1-2y | 2-3y | 3y+ |
|---|---|---|---|---|---|---|
| full E(b) | 0.5342 | 0.4834 | 0.4509 | 0.4064 | 0.3688 | 0.3609 |
| full 95% CI | [0.4817, 0.5937] | [0.4221, 0.5529] | [0.3792, 0.5309] | [0.3205, 0.4993] | [0.2653, 0.4805] | [0.2167, 0.5054] |
| full null centre | -0.0000 | -0.0000 | -0.0000 | -0.0001 | -0.0001 | -0.0001 |
| full self pairs | 1,802,741 | 1,518,988 | 2,546,612 | 3,382,753 | 1,790,865 | 706,685 |
| common E(b) | 0.5558 | 0.5190 | 0.4942 | 0.4579 | 0.4227 | 0.4150 |
| common 95% CI | [0.5000, 0.6207] | [0.4528, 0.5933] | [0.4161, 0.5792] | [0.3651, 0.5554] | [0.3051, 0.5377] | [0.2600, 0.5598] |
| common null centre | -0.0000 | -0.0000 | -0.0000 | -0.0001 | -0.0001 | -0.0002 |
| common self pairs | 1,802,741 | 1,518,988 | 2,546,612 | 3,382,753 | 1,790,865 | 706,685 |
| distinct E(b) | 0.4666 | 0.4061 | 0.3686 | 0.3178 | 0.2805 | 0.2725 |
| distinct 95% CI | [0.4165, 0.5134] | [0.3507, 0.4637] | [0.3059, 0.4345] | [0.2464, 0.3922] | [0.1951, 0.3712] | [0.1538, 0.3954] |
| distinct null centre | -0.0000 | 0.0000 | -0.0000 | -0.0000 | 0.0000 | -0.0000 |
| distinct self pairs | 1,802,741 | 1,518,988 | 2,546,612 | 3,382,753 | 1,790,865 | 706,685 |

## Flags (#73)

- transport BREAK on Λ = λ_distinct − λ_common: source cell `SIGN_UNRESOLVED` against target cell `COMMON_STANDING`
- transport BREAK on the layer ordering: the slowest row is `common`, not `taste`

## Registered leans

| lean | statement | outcome | detail |
|---|---|---|---|
| L1 | Λ > 0 with point ≈ +0.07/y (disclosed knowledge, not a fresh prediction) | **HELD** | realized Λ 0.0911/y [0.0628, 0.1490], cell `COMMON_STANDING` |
| L2 | the floor share and D of the full row REPRODUCE (DRIFT_WITH_CORE is cohort-general) | **PARTIAL** | floor share REPRODUCES (0.7360 [0.5453, 0.8568] against 0.5348 [0.4203, 0.6320]); D SHIFTS (0.1408 [0.0850, 0.2224] against 0.3058 [0.2364, 0.3855]) |
| L3 | λ_taste is the SMALLEST rate of the four law-arm rows (ORDER HOLDS) | **MISSED** | slowest row `common`; λ full 0.1236, common 0.0901, distinct 0.1812, taste 0.1010 |
| L4 | the clean arm (typology ablation) leaves Λ inside its CI class | **HELD** | clean Λ 0.0780/y [0.0484, 0.1397] in cell `COMMON_STANDING` against the law arm's `COMMON_STANDING` |

## Boundaries

- **The disjoint cohort is TYPOLOGY-ENRICHED by construction, and that conditions every transport claim here.** PANDORA's non-Big5 authors are the corpus's MBTI-labelled users, recruited through typology communities: 22 explicit-typology communities sit in the law arm's 1,443-community vocabulary and 8 of them sit inside the 71-community Common(0.5) set — the split's common half is partly a typology-forum half. A law that transports here has been carried to a DIFFERENT KIND of author population on the same platform, not to a fresh sample of the same one, so a REPRODUCES is evidence of robustness across cohort composition and a BREAKS is not automatically evidence against the law. The clean arm is the handle on exactly this.
- **The eq-12 projection caution, carried in as registered:** this leg reads ONE slow-time projection of the transition kernel K_u (eq 12) onto the marginal selection distribution π_u over a subreddit vocabulary, split by carrier. A decay-rate contrast here is a statement about π_u on the Hellinger unigram sphere over calendar time, never about a psychological attribute (§5.4), and 'common' and 'distinctive' are EVENT-MASS strata, not the T-line's personality/identity constructs.
- **Three-year scoping binds every rate in this report.** λ is fitted over a window that ends at the 2–3y bin (realized mean gap 2.434 years), so it is a THREE-YEAR CORE rate and nothing else. The log-linear form is a local description of the observed window, not a demonstrated law; no rate here licenses a half-life, an asymptote, a permanent floor or any extrapolation past the observed span.
- **No equivalence cell exists in this leg, by registration.** A near-zero Λ reads `SIGN_UNRESOLVED` and is reported as an interval, never as a demonstration of equal rates.
- **LEVEL differences across rows are never interpreted** (U2b's inherited comparison rule): a restricted row is a lower-dimensional, differently attenuated view of the same block. The decay RATE is the level-free quantity; the E(b) levels tabulated beside it do not transport across rows.
- **The transport table is SECONDARY and never routes the verdict.** The verdict is the bootstrap CI on Λ in the law arm alone. The sealed source values also differ in provenance — floor share and D come from U2's 849-author POOL arm while Λ and λ_full come from U2c's INTERSECTION set — so the floor-share and D rows compare a pool-level source against an intersection-level target and their classifications carry that asymmetry.
- The eligibility floor is not neutral. Requiring ≥ m events in BOTH sub-vocabularies keeps only BALANCED blocks, so the intersection set over-represents authors who mix common and distinctive communities inside a 50-event window. The m = 5 arm is a different sample, not a bigger draw from the same one.
- The taste row's cross baseline is fold-local while the other three rows share one pool-level reservoir, and its bootstrap draws are fold-stratified, so any contrast involving it is unpaired and its interval is conservative.
- EXPLORATORY and corpus-level. Label-free throughout: `author_profiles.csv` is never opened in this leg, the disjoint authors' MBTI labels stay closed, no per-author quantity is reported or committed, and no person claim is made or licensed.

## Configuration

```json
{
  "b_boot": 1000,
  "b_perm": 499,
  "bin_labels": [
    "0-90d",
    "90-180d",
    "180-365d",
    "1-2y",
    "2-3y",
    "3y+"
  ],
  "cache": "/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/results/m4_w1_slow_transport/disjoint_events_cache.npz",
  "cells": [
    "SIGN_UNRESOLVED",
    "COMMON_STANDING",
    "DISTINCT_SLOWER"
  ],
  "cohort_file": "/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/results/m4_sr0_recon/cohort_authors.csv",
  "comments_file": "/Volumes/mobile3/projects/project persona/data_sets/PANDORA_official/all_comments_since_2015.csv",
  "days_per_year": 365.25,
  "descriptive_bin_excluded_from_the_fit": "3y+",
  "epoch_origin_utc": "2015-01-01T00:00:09Z",
  "equivalence_cell": null,
  "fit_bins": [
    "0-90d",
    "90-180d",
    "180-365d",
    "1-2y",
    "2-3y"
  ],
  "frozen_instrument_cache": "/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/results/m4_u1_order_identity/events_cache.npz",
  "k": 50,
  "m_primary": 10,
  "m_sensitivity": 5,
  "pool_min_blocks": 4,
  "projected_half_width": 0.044,
  "q_primary": 0.5,
  "quarter_days": 91.3,
  "registration_commit": "11aacd7",
  "script_sha256": "090b4fca5093065c31e70e8c8cba8c96d94b0441df940f950e3647496f49bba6",
  "sealed_lambda_point": 0.074,
  "sealed_ordering": "\u03bb_taste is the SMALLEST of the four rows (held in both U2c arms)",
  "seed": 20260818,
  "taste_dim": 64,
  "taste_folds": 5,
  "taste_rows_only_on": "law arm",
  "u2_machinery": "/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/scripts/run_suica_m4_u2_persistence_curve.py",
  "u2_machinery_sha256": "09dda64dffeaaa5e38f7a0008540474bf25fb1ddef9b927cde0dd568d8572ef3",
  "u2b_machinery": "/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/scripts/run_suica_m4_u2b_persistence_budget.py",
  "u2b_machinery_sha256": "8153d299f76ceca4a5a5fcbec74a2f140463f71844482ee2960c5b51c6b6ec46",
  "u2c_machinery": "/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/scripts/run_suica_m4_u2c_decay_rate_contrast.py",
  "u2c_machinery_sha256": "3003bbbac3f7ba67e426d93ee609cd11adca46df6ae85643164829fa69f77276",
  "vocab_floor_fraction": 0.01,
  "vocab_floor_users": 89
}
```

Machinery inherited by import-by-file (#81 — pinned by formula with provenance):

*inherited from u2c*
- log_slope_fit (OLS of log E(b) on realized mean gap in years, five verdict bins, positivity rule)
- linear_slope (the domain-safe companion, #80a)
- summarize_lambda / rate_contrast (paired replicate differencing)
- classify_lambda (the three registered cells)

*inherited from u2b*
- community_ranking / common_prefix (the event-mass split)
- block_counts_over (exact sub-vocabulary counts as K*f^2)
- renormalize (the carrier restriction)
- self_pair_census (the gate's exact predicate)
- ppmi_svd / first_half_counts / taste_folds / pool_fold_results
- floor_share / percentile_ci

*inherited from u2*
- build_blocks (exact-K disjoint blocks, Hellinger features)
- assign_quarters / gap_bin (epoch cells and gap bins)
- compute_arm (epoch-matched EXACT stratified cross baseline, RD-U2-1 form; within-quarter permutation scaffold; author cluster bootstrap)
- is_explicit_personality_community (T1's matcher, lines 37-69)
- scan_for_cohort_ids (ID-leak gate)

Recorded implementation choices (registration silent):

- **cache_builder** — U1's stream_cohort_events under the NEGATED cohort predicate, with per-chunk incremental factorization instead of one whole-frame concat (14.6M rows x 3 string columns does not fit in memory); codes are remapped to sorted-name order at the end, so the cache is identical to U1's construction by design and the equivalence is asserted in tests on a toy stream
- **law_vs_instrument** — LAW = SR0's vocabulary RULE re-instantiated on this cohort (floor ceil(0.01 * 8895) = 89 users) with the mass split re-derived here; INSTRUMENT = the frozen 1191-name vocabulary and the frozen 32-name Common(0.5) set from the 1401 cohort, applied to the disjoint stream as-is
- **clean_arm_rule** — U2's clean-arm convention: the typology names are removed from the vocabulary and the blocks are REBUILT over the reduced vocabulary (so a K=50 block again holds exactly 50 in-vocabulary events), the pool and the mass split are re-derived, and Lambda plus the floor share are rerun
- **taste_rows** — the taste row runs on the LAW arm only: the layer-ordering prediction is a law-arm statement and the instrument, clean and m=5 arms exist to move Lambda and the floor share
- **gap_years** — each row's REALIZED per-bin mean self-pair gap in days on its own block set, divided by 365.25; the gaps are held at their realized values inside the bootstrap and the permutation (U2c's inherited convention)
- **transport_classification** — REPRODUCES = target CI intersects source CI AND same sign/cell; SHIFTS = disjoint CIs, same sign/cell; BREAKS = different sign/cell. For Lambda the cell is the registered three-cell partition; for the scalar quantities the cell is the CI's sign class (POSITIVE / NEGATIVE / SIGN_UNRESOLVED). The table is SECONDARY and never routes
- **sealed_source_heterogeneity** — the registration's sealed floor share and D come from U2's PRIMARY arm (the 849-author pool over the full vocabulary) while Lambda and lambda_full come from U2c's INTERSECTION set (q=0.5/m=5). W1 compares all four against its LAW arm's intersection-set rows, which is the like-for-like object for Lambda and lambda_full and a pool-vs-intersection comparison for floor share and D; the mismatch is the registration's and is disclosed rather than silently re-based
- **id_leak_universe** — the union of the 1401 cohort names and the 8,895 disjoint names = 10,296 candidates; the scan list itself is written only into gitignored results/
- **id_leak_collision_rule** — at 10,296 candidates the substring scan acquires DICTIONARY COLLISIONS -- some disjoint author names are ordinary English words or bare digit runs that already occur in committed prose written long before this leg. Collisions are separated from leaks MECHANICALLY: a hit is PRE-EXISTING iff the same scanner produces the identical hit (same file, same line) on that file's version at HEAD. W1's own outputs do not exist at HEAD, so their tolerance is ZERO, and this leg only APPENDS to the two pre-existing documents, so a pre-existing hit keeps its line number. The blocking gate is zero NEW hits

Run started 2026-08-18T12:58:25.518065Z, finished 2026-08-18T13:22:03.396434Z; registration commit `11aacd7`; script sha256 `090b4fca5093065c…`.
