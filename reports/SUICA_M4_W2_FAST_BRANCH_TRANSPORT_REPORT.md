# SUICA M4-W2 — fast-time and branch-code transport

**VERDICT: `ORDER_SHIFTS` (cell 2 of 3).** The order channel re-instantiates IN CELL but at a different level — same law, different magnitude.

The order family routes: the size-matched primary rho is 0.2207 [0.2023, 0.2401] on 984 authors who share nobody with the source cohort, against U1's sealed 0.2893 [0.2695, 0.3114] on 984. Both points sit in U1's `ORDER_CHANNEL` cell; the intervals are disjoint, so the row classifies **SHIFTS**.

The branch family is co-primary and carries #73 flags without routing: 5 divergence flag(s) are raised below. Generated 2026-08-18T15:11:48.335648Z from `results/m4_w2_fast_branch_transport`.

## 1. Anchor gates (#78) — blocking, re-executed on the W1 cache

| anchor | registered | observed | status |
|---|---|---|---|
| disjoint_events | 14634702 | 14634702 | PASS |
| authors_seen | 8895 | 8895 | PASS |
| vocab_floor_users | 89 | 89 | PASS |
| law_vocabulary | 1443 | 1443 | PASS |
| order_pool | 7247 | 7247 | PASS |
| branch_pool | 8625 | 8625 | PASS |
| tie_rate_in_law_vocab | 0.00882 | 0.00882 | PASS |
| session_share_in_law_vocab | 0.56147 | 0.56147 | PASS |
| cross_thread_share_all_events | 0.73174 | 0.73174 | PASS |
| law vocabulary identical to the cache's list | True | True | PASS |

All 10 anchors reproduce (PASS). The law vocabulary was recomputed from the cache by SR0's rule — distinct cohort users per subreddit, floor ceil(0.01 × 8895) = 89 — and the resulting 1443-community list is identical to the one W1 carried, not merely the same length.

## 2. The size-matched draws (the W1 adjudication's binding correction)

Pooled same-vs-different AUC is a function of GALLERY SIZE: a larger gallery offers more impostors and drives the pooled AUC down. U1's and T1's sealed values were measured at N = 984 and N = 1,304, so a full-pool comparison would confound transport with gallery size. The primary arms therefore run at exactly the source sizes.

| draw | order | source pool (censused) | N drawn | digest |
|---|---|---|---|---|
| order subpool | 1st | 7247 | 984 | `e44097a2b36ad6ea` |
| branch subpool | 2nd | 8625 | 1304 | `b76122f923db8740` |

One stream: `numpy.random.default_rng(20260818), one stream, two draws`. The order draw is taken FIRST and the branch draw continues the same stream, so the draw ORDER is part of the pin — swapping them changes both subpools. Both draws are uniform without replacement and are sorted ascending before use. 138 authors appear in both draws, which is expected and harmless: the two families are separate instruments, not a joint test.

## 3. Order family — the verdict router

| arm | gallery N | size-matched | rho (target) | 95% CI | rho (source) | source CI | delta | class |
|---|---|---|---|---|---|---|---|---|
| rho, raw-adjacency primary arm | 984 | yes | 0.2207 | [0.2023, 0.2401] | 0.2893 | [0.2695, 0.3114] | -0.0686 | **SHIFTS** |
| rho, stay-rate scalar arm | 984 | yes | 0.1778 | [0.1344, 0.2191] | 0.1803 | [0.1375, 0.2234] | -0.0025 | **REPRODUCES** |
| rho, cross-thread-only arm | 984 | yes | 0.1383 | [0.1192, 0.1593] | 0.1626 | [0.1373, 0.1895] | -0.0243 | **REPRODUCES** |

Every AUC row above is size-matched: the target gallery is 984 authors and the source gallery was 984, so the rho comparison is a like-for-like comparison of gallery-matched pooled AUCs. Nothing in this table compares a 984-author AUC with a 7247-author AUC.

### 3.1 Null locations against the bag ceiling

| arm | AUC real | exact-bag null mean | null 95% band | unigram bag AUC | null − bag | real − bag | shuffle p | bag exact |
|---|---|---|---|---|---|---|---|---|
| primary | 0.9289 | 0.9087 | [0.9083, 0.9092] | 0.9342 | -0.0254 | -0.0053 | 0.002 | True |
| stay_rate | 0.6951 | 0.6292 | [0.6243, 0.6342] | 0.9342 | -0.3050 | -0.2391 | 0.002 | True |
| cross_thread | 0.9127 | 0.8986 | [0.8980, 0.8993] | 0.9342 | -0.0356 | -0.0215 | 0.002 | True |

The exact-bag shuffle destroys ORDER while holding each half's community bag EXACTLY fixed (verified bit-for-bit per fold, the `bag exact` column). The null therefore sits where a pure bag instrument sits, and rho reads the excess that only adjacency carries. The raw-adjacency null lands 0.0254 below the unigram bag ceiling; at source the same gap was -0.0211, i.e. on the same side, and the two differ by 0.0044.

### 3.2 Full-pool sensitivity (registered, NOT size-matched)

| arm | gallery N | rho | 95% CI | AUC real | null mean | cell (with CI support) |
|---|---|---|---|---|---|---|
| primary | 7247 | 0.1762 | [0.1700, 0.1831] | 0.9245 | 0.9083 | ORDER_CHANNEL |

This row is **not** size-matched and must not be read as a transport comparison against U1's 984-author value: the gallery is 7247 authors, 7.36× the source. It answers a different question — whether the channel survives at the cohort's full censused scale — and it lands in cell `ORDER_CHANNEL`, the same as the size-matched arm's `ORDER_CHANNEL`. The rho level itself moves by -0.0445 across the 7.36× gallery change, which is the size effect the W1 adjudication required this leg to hold fixed in the primary arms.

## 4. Branch family — co-primary, #73 flags, never routing

| arm | quantity | gallery N (valid) | size-matched | AUC (target) | 95% CI | AUC (source) | source CI | delta | class |
|---|---|---|---|---|---|---|---|---|---|
| full | flat Hellinger AUC (full arm) | 1301 | yes | 0.9817 | [0.9772, 0.9852] | 0.9837 | absent | -0.0020 | **REPRODUCES** |
| full | frozen-path AUC (full arm) | 1301 | yes | 0.7154 | [0.7028, 0.7425] | 0.7461 | absent | -0.0307 | **SHIFTS** ⚑ |
| full | terminal residual AUC (full arm) | 1301 | yes | 0.9722 | [0.9617, 0.9761] | 0.9552 | absent | +0.0170 | **SHIFTS** ⚑ |
| clean | flat Hellinger AUC (clean arm) | 1293 | yes | 0.9562 | [0.9480, 0.9638] | 0.9661 | absent | -0.0099 | **SHIFTS** ⚑ |
| clean | frozen-path AUC (clean arm) | 1293 | yes | 0.6929 | [0.6918, 0.7273] | 0.7317 | absent | -0.0388 | **SHIFTS** ⚑ |
| clean | terminal residual AUC (clean arm) | 1293 | yes | 0.9486 | [0.9374, 0.9580] | 0.9417 | absent | +0.0069 | **REPRODUCES** |

Size-matching statement for every AUC row above: the branch draw is N = 1304 authors, exactly T1's input size; after the pipeline's own validity filter (both halves must have non-zero norm) the realised gallery is 1301 against T1's 1,304 for the full arm and 1,269 for the clean arm. The residual gallery difference is under half a percent and is stated, not corrected.

**Missing source intervals (registered rule).** T1's committed artifacts carry per-depth gain CIs but no interval for any of the three AUCs, so all 6 branch AUC rows fall to the registered fallback: classify by point-in-TARGET-CI and FLAG the missing interval. The flag stands for every branch AUC row in the table above.

The target intervals are this leg's own instrument (RD-W2-2): an author-level cluster bootstrap, B = 300, re-running the SAME pinned function on each resample. A with-replacement author draw seeds the gallery with duplicated authors, and a duplicate scores as high as the true match while being labelled 'different', which perturbs the pooled AUC. The measured bias runs from -0.0024 to +0.0159 across the six rows; it is reported per row rather than assumed, and the bias-corrected ('basic') interval is carried alongside so the class can be checked under both:

| arm | quantity | percentile CI | bootstrap bias | basic (recentred) CI | class under the basic CI |
|---|---|---|---|---|---|
| full | flat Hellinger AUC (full arm) | [0.9772, 0.9852] | -0.0004 | [0.9782, 0.9862] | REPRODUCES |
| full | frozen-path AUC (full arm) | [0.7028, 0.7425] | +0.0066 | [0.6883, 0.7280] | SHIFTS |
| full | terminal residual AUC (full arm) | [0.9617, 0.9761] | -0.0024 | [0.9683, 0.9826] | SHIFTS |
| clean | flat Hellinger AUC (clean arm) | [0.9480, 0.9638] | -0.0002 | [0.9487, 0.9645] | SHIFTS |
| clean | frozen-path AUC (clean arm) | [0.6918, 0.7273] | +0.0159 | [0.6585, 0.6940] | SHIFTS |
| clean | terminal residual AUC (clean arm) | [0.9374, 0.9580] | -0.0003 | [0.9391, 0.9598] | REPRODUCES |

### 4.1 Depth-by-depth gains and the triple gate

| arm | depth | n | centroid gain | 95% CI | gain p | branch excess | branch p | excess bits | bits p | stable |
|---|---|---|---|---|---|---|---|---|---|---|
| full | 1 | 1301 | 0.03512 | [0.02647, 0.04313] | 0.002 | 0.2338 | 0.002 | 0.1992 | 0.002 | yes |
| full | 2 | 1301 | 0.04474 | [0.03787, 0.05148] | 0.002 | 0.2872 | 0.002 | 0.3027 | 0.002 | yes |
| full | 3 | 1301 | 0.01928 | [0.01356, 0.02563] | 0.002 | 0.2034 | 0.002 | 0.1982 | 0.002 | yes |
| full | 4 | 1057 | 0.02149 | [0.01523, 0.02846] | 0.002 | 0.1925 | 0.002 | 0.1904 | 0.002 | yes |
| full | 5 | 621 | 0.02161 | [0.01409, 0.02966] | 0.002 | 0.2481 | 0.002 | 0.2509 | 0.002 | yes |
| full | 6 | 257 | 0.01863 | [0.00865, 0.02902] | 0.002 | 0.2630 | 0.002 | 0.2988 | 0.002 | yes |
| clean_no_explicit_personality | 1 | 1293 | 0.01278 | [0.00711, 0.01830] | 0.002 | 0.2396 | 0.002 | 0.1773 | 0.002 | yes |
| clean_no_explicit_personality | 2 | 1293 | 0.00955 | [0.00416, 0.01492] | 0.002 | 0.2102 | 0.002 | 0.2033 | 0.002 | yes |
| clean_no_explicit_personality | 3 | 1160 | 0.01157 | [0.00779, 0.01570] | 0.002 | 0.1952 | 0.002 | 0.1666 | 0.002 | yes |
| clean_no_explicit_personality | 4 | 893 | 0.00514 | [0.00152, 0.00907] | 0.002 | 0.2038 | 0.002 | 0.1667 | 0.002 | yes |
| clean_no_explicit_personality | 5 | 622 | -0.00019 | [-0.00343, 0.00369] | 0.002 | 0.1774 | 0.002 | 0.1426 | 0.002 | no |

| arm | stable depths (target) | stable depths (source) | symmetric difference | class |
|---|---|---|---|---|
| full | [1, 2, 3, 4, 5, 6] | [1, 2, 3, 4, 5] | [6] | **DEPTHS_SHIFT** |
| clean | [1, 2, 3, 4] | [1, 2, 3, 4] | ∅ | **DEPTHS_REPRODUCE** |

### 4.2 Clean arm (governance echo)

The clean arm removes the 22 explicitly named typology communities present in the law vocabulary and rebuilds the author vectors (the removed columns are zeroed and the Hellinger normalisation is re-applied inside the pinned function — T1's exact pattern). Its rows appear in the tables above. The removed set is in `arms.json`; the names are community names, never author names.

## 5. Cohort-instrument notes

| instrument quantity | this cohort | source cohort | note |
|---|---|---|---|
| timestamp tie rate (in-law-vocab spliced adjacency) | 0.00882 | 0.11522 | an attenuation source present at source and essentially ABSENT here (13.1× lower) |
| session share (gap ≤ 1 h, same denominator) | 0.56147 | 0.67000 | denominators differ (whole-cohort splice here, pooled test folds at source) |
| cross-thread share (all adjacencies) | 0.73174 | 0.62213 | same caveat |
| same-state adjacency share (dwell dominance) | 0.6141 | 0.7122 | descriptive, pooled over test folds in both cohorts |
| OOV state occupancy | 0.2801 | 0.2071 | descriptive |

The tie rate is the registration's named cohort-instrument difference. Tied timestamps are order-free events that the shuffle cannot move informatively, so they attenuate the REAL adjacency signal at source and barely exist here. The registered lean read that as a reason to expect rho HIGH of source. The realised direction is the opposite (-0.0686), which is recorded as an honest anomaly rather than explained away.

## 6. Projection versus lean

| lean | statement | observed | outcome |
|---|---|---|---|
| L1 | ORDER_TRANSPORTS with target rho in [0.25, 0.4]; the absent tie attenuation (0.9% here vs 11.5% at source) leans rho HIGH of source | verdict ORDER_SHIFTS, rho 0.2207 (source 0.2893, delta -0.0686) | **MISSED** |
| L2 | dwell dominance transports — the stay-rate arm keeps a detected rho and same-state adjacency stays the majority share | stay-arm rho 0.1778 [0.13440753579784115, 0.21914126167463271], dwell share 0.6141 (source 0.7122) | **HELD** |
| L3 | branch flat and residual REPRODUCE; path SHIFTS plausibly | full.flat_auc REPRODUCES; full.hierarchical_path_auc SHIFTS; full.terminal_residual_auc SHIFTS | **PARTIAL** |
| L4 | stable depths REPRODUCE or SHIFT by one | full [1, 2, 3, 4, 5, 6] vs [1, 2, 3, 4, 5] -> DEPTHS_SHIFT; clean [1, 2, 3, 4] vs [1, 2, 3, 4] -> DEPTHS_REPRODUCE | **HELD** |
| L5 | clean arm transports in the same cell as the full arm (the U/W identity-robust pattern) | clean.flat_auc ABOVE_CHANCE; clean.hierarchical_path_auc ABOVE_CHANCE; clean.terminal_residual_auc ABOVE_CHANCE | **HELD** |

- **L1**: rho landed BELOW source, not above: the direction of the lean is wrong as well as its cell.

## 7. Boundaries

- **EXPLORATORY, corpus-level.** Both families are measured over a single Reddit comment corpus with one splitting rule. Nothing here licenses a claim about persons outside this corpus, and nothing here is preregistered in the confirmatory sense — the sealed predictions were fixed before the run, but the source values were themselves produced by exploratory legs.
- **Typology-enriched cohort.** The disjoint cohort was recovered from the same comments file as the source cohort, whose recruitment ran through typology forums. The law vocabulary contains 22 explicitly named typology communities, and the clean arm exists precisely because that enrichment is a live confound for any 'community selection' reading.
- **Size-matching is a correction, not a cure.** Matching the gallery removes the gallery-size confound from the AUC comparison; it does not make the two cohorts exchangeable in any other respect. Event volume, tie structure, session structure and community mix all differ, and each of them can move a pooled AUC.
- **The eq-12 projection caution stands.** Width projections and level projections are different objects. This leg projected LEVELS (sealed points and their cells) and made no width projection; the #79b/#80b width machinery is not exercised here, and its two consecutive hits at W1 must not be read as licensing level projection.
- **rho is a ratio against a moving null.** rho = (AUC_real − null)/(1 − null) is measured against an exact-bag null that is itself cohort-specific (here 0.9087, at source 0.9396). A rho difference can come from the numerator, the denominator, or both; this leg reports the raw AUCs and the null locations so the decomposition stays visible.
- **Branch AUC intervals are executor-supplied.** The registration pinned no interval instrument for T1's three AUCs because T1 produced none. The cluster bootstrap used here is the house instrument, but it is NOT the sealed source's instrument, and a REPRODUCES verdict on those rows rests on an interval that the source leg never had.
- **Label-free.** No personality label of any kind was read. `author_profiles.csv` was never opened. Nothing in this leg speaks to what any author is like — only to whether two halves of the same author's stream can be matched, and by what channel.

## 8. Gates

| gate | status |
|---|---|
| anchor gates (#78), 10 of them | PASS |
| fold purity (no test-author mass in any state map) | PASS |
| exact-bag invariance, every order arm | PASS |
| size matching, order gallery == 984 | PASS |
| size matching, branch draw == 1304 | PASS |
| ID-leak scan (0 NEW hits of 10,296 author names) | PASS |

The ID-leak universe is every author name in the comments file — 10,296 candidates, the 4-hit HEAD baseline separated mechanically under #83. Raw hits on the committed files: 4; pre-existing (identical file and line at HEAD): 4; **NEW: 0**. Only NEW hits block.

## 9. Configuration

```json
{
  "branch": {
    "auc_bootstrap": 300,
    "bootstrap": 1000,
    "input": "sqrt frequency / Hellinger unit sphere (inside suica_core)",
    "max_depth": 6,
    "min_events": 40,
    "min_leaf": 30,
    "permutations": 499,
    "subpool_n": 1304
  },
  "label_free": true,
  "leg": "M4-W2",
  "machinery": {
    "branch": "suica_core.hierarchical_selection_identity.cross_fitted_hierarchical_identity",
    "cache": "results/m4_w1_slow_transport/disjoint_events_cache.npz",
    "order": "scripts/run_suica_m4_u1_order_identity.py (imported by file)"
  },
  "n_folds": 5,
  "order": {
    "alpha": 0.5,
    "arms": [
      "primary",
      "cross_thread",
      "stay_rate"
    ],
    "b_boot_shuffle_full_pool": 10,
    "b_boot_shuffle_matched": 100,
    "b_bootstrap": 1000,
    "b_shuffle": 499,
    "c_states": 24,
    "cluster_seed": "SEED + 1000 * fold",
    "kmeans_n_init": 10,
    "lens": "hellinger_joint (bigram joint next-state counts)",
    "pool_min_per_half": 50,
    "subpool_n": 984
  },
  "output_dir": "results/m4_w2_fast_branch_transport",
  "registration": "docs/SUICA_M4_W_DISJOINT_TRANSPORT_PLAN.md :: ## W2 \u2014 fast-time and branch-code transport (registered BEFORE run, 2026-08-18)",
  "seed": 20260818,
  "vocabulary": {
    "floor_fraction": 0.01,
    "floor_users": 89,
    "rule": "SR0 distinct-user floor",
    "size": 1443
  }
}
```

Wall clock: order size-matched 358.1 s, order full-pool 2312.5 s, branch arms 52.0 s, branch AUC bootstrap 1139.0 s.

