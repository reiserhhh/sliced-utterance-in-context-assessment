# SUICA M4-U2c — the decay-rate contrast

**Outcome: `SIGN_UNRESOLVED`.**

**Λ = λ_distinct − λ_common = 0.0741/y [-0.0558, 0.1854]** at the registered primary configuration q = 0.5 / m = 5 (179,107 self pairs and 424 contributing authors in the 2–3y bin).

**THE VERDICT IS THE INTERVAL STATEMENT.** The registration named `SIGN_UNRESOLVED` a live cell before the run and projected a borderline half-width of 0.08–0.10/y; the realized half-width is 0.1206/y and the interval straddles zero. The sign evidence is carried as registered — this CI TOGETHER WITH U2b's quarantined sign unanimity (Δfloor negative at all five of its configurations) — and the tier is unchanged at EXPLORATORY. No layer is declared the standing one.

**Both registered arms put the point on the same side of zero** — primary Λ 0.0741/y, confirmatory 0.0861/y — and in both arms λ_distinct (0.3276 and 0.3176) exceeds λ_common (0.2535 and 0.2315). That is a POINT-level agreement with U2b's five quarantined configurations, not an interval that excludes zero, and it is reported as the former.

Executed from the registration committed at `6a4a5bb` in `docs/SUICA_M4_U_WHEN_ORDER_PLAN.md` (section "U2c — the decay-rate contrast (completion of U2b; registered BEFORE run, 2026-08-18)"). Run window 2026-08-17T22:53:29.632693Z to 2026-08-17T22:55:04.435166Z; report generated 2026-08-17T22:55:04.435168Z. Every number in this report is produced from the run's artifacts by `scripts/run_suica_m4_u2c_decay_rate_contrast.py` (rule 24).

## Gates

| gate | status |
|---|---|
| cache anchor gate (3,005,360 events / 1401 authors / 1191 vocabulary) | PASS |
| pool reproduction (849 authors / 45,731 blocks) | PASS |
| split census (universe 2,348,361; Common(0.5) = 32; Common(0.7) = 104) | PASS |
| GATE ANCHORS #78 (U2b's realized intersection quantities at both run configurations, recomputed and compared exactly) | PASS |
| G0 — U2b four-row E(b) table bit-comparison (#56) | PASS |
| taste-row fold purity (mass identity, zero test mass) | PASS |
| sub-vocabulary counts integral (max deviation 1.06e-05) | PASS |
| no synthetic gate required (R layer, no world simulated) | N/A |
| ID-leak scan (0 of 1401 cohort IDs in committed files) | PASS |

## The gate's executed predicate (#78), recomputed as a blocking anchor

U2b's #78 defect was a gate governed by a quantity no census computed. U2c's gate quantities are U2b's REALIZED intersection numbers — the predicate already executed on census data — and this runner re-executes the same predicate and compares EXACTLY before any row is read. A mismatch stops the leg.

| configuration | registered pairs (2–3y) | observed | registered authors | observed | eligible blocks | meets #69 | status |
|---|---|---|---|---|---|---|---|
| primary q=0.5/m=5 | 179,107 | 179,107 | 424 | 424 | 27,485 | yes | PASS |
| confirmatory q=0.7/m=10 | 108,716 | 108,716 | 401 | 401 | 19,571 | yes | PASS |

Both configurations clear the registered #69 targets (≥ 100,000 pairs and ≥ 400 authors in the 2–3y bin), which is why U2c can issue a verdict where U2b could not.

## The estimand (#79: ratio-free)

Per carrier row, OLS over the FIVE verdict bins 0-90d / 90-180d / 180-365d / 1-2y / 2-3y:

```
log E_row(b) = log E0_row − λ_row · gap_years(b)
```

where `gap_years(b)` is the row's realized per-bin mean self-pair gap on the intersection set (days / 365.25) and `E_row(b)` is the epoch-matched personal excess — the self mean minus the EXACT stratified cross mean — computed by U2's estimator, imported by file. λ is in 1/year and is LEVEL-FREE by construction: a gap-independent attenuation moves log E0, not λ. The verdict contrast is **Λ = λ_distinct − λ_common**, positive when the distinctive decays faster. The 3y+ bin is descriptive and NEVER enters the fit.

Realized gap grid at the primary configuration (years): 0-90d = 0.1182, 90-180d = 0.3650, 180-365d = 0.7300, 1-2y = 1.4171, 2-3y = 2.3961; the descriptive 3y+ bin sits at 3.3955 years and is excluded.

## The four decay rates (primary: q = 0.5, m = 5)

| row | λ (1/y) | 95% CI | CI half-width | R² (log-linear) | E0 | F = E(2–3y)/E(0–90d) |
|---|---|---|---|---|---|---|
| full vocabulary | **0.2943** | [0.1895, 0.4405] | 0.1255 | 0.9939 | 0.5403 | 0.5094 |
| common (q=0.5, 32 communities) | **0.2535** | [0.1408, 0.4244] | 0.1418 | 0.9992 | 0.6122 | 0.5625 |
| distinctive (q=0.5, 1159 communities) | **0.3276** | [0.1854, 0.4970] | 0.1558 | 0.9747 | 0.4280 | 0.4646 |
| taste (per-fold PPMI+SVD d=64, out-of-fold) | **0.1736** | [0.0970, 0.2737] | 0.0883 | 0.9670 | 0.4419 | 0.6803 |

R² is descriptive only: it says how well a single exponential describes the five-bin window, not whether the decay is exponential.

Per-row per-bin personal excess E(b) with its realized mean gap:

| row | 0-90d | 90-180d | 180-365d | 1-2y | 2-3y | 3y+ |
|---|---|---|---|---|---|---|
| full vocabulary | 0.5340 | 0.4820 | 0.4330 | 0.3459 | 0.2720 | 0.2434 |
| common (q=0.5, 32 communities) | 0.5925 | 0.5554 | 0.5148 | 0.4259 | 0.3333 | 0.2962 |
| distinctive (q=0.5, 1159 communities) | 0.4376 | 0.3729 | 0.3272 | 0.2551 | 0.2033 | 0.2026 |
| taste (per-fold PPMI+SVD d=64, out-of-fold) | 0.4407 | 0.4183 | 0.3866 | 0.3295 | 0.2998 | 0.2756 |
| *realized mean gap (days)* | 43.18 | 133.31 | 266.62 | 517.59 | 875.16 | 1240.19 |
| *realized mean gap (years)* | 0.1182 | 0.3650 | 0.7300 | 1.4171 | 2.3961 | 3.3955 |
| *self pairs* | 453,665 | 356,709 | 538,528 | 541,856 | 179,107 | 49,230 |

Every E(b) in the fitted window is strictly positive, so the log-linear fit is defined on the point estimate of every row:

| row | min E(b) over the five fitted bins | positive |
|---|---|---|
| full vocabulary | 0.2720 | yes |
| common (q=0.5, 32 communities) | 0.3333 | yes |
| distinctive (q=0.5, 1159 communities) | 0.2033 | yes |
| taste (per-fold PPMI+SVD d=64, out-of-fold) | 0.2998 | yes |

Descriptive 3y+ bin (never fitted): full vocabulary 0.2434, common (q=0.5, 32 communities) 0.2962, distinctive (q=0.5, 1159 communities) 0.2026, taste (per-fold PPMI+SVD d=64, out-of-fold) 0.2756.

## The verdict contrast Λ = λ_distinct − λ_common

| quantity | point | 95% CI | half-width | bootstrap replicates | dropped (non-positive E) |
|---|---|---|---|---|---|
| Λ = λ_distinct − λ_common | **0.0741** | [-0.0558, 0.1854] | 0.1206 | 1,000 | 0 |
| λ_taste − λ_full | **-0.1207** | [-0.2771, 0.0205] | 0.1488 | 1,000 | 0 |

The bootstrap is PAIRED BY CONSTRUCTION for Λ: all rows sit on one block set, so `compute_arm` draws the identical author multinomial for each of them and the contrast is differenced replicate by replicate. The secondary contrast λ_taste − λ_full is NOT paired (fold-stratified draws against pool-level draws) and its interval is correspondingly conservative.

Per-row bootstrap drops (replicates with any non-positive E(b) in the fitted window): full vocabulary 0, common (q=0.5, 32 communities) 0, distinctive (q=0.5, 1159 communities) 0, taste (per-fold PPMI+SVD d=64, out-of-fold) 0 of 1,000.

### The permutation null on Λ, and what it can say

| null | replicates | retained | center | 95% band |
|---|---|---|---|---|
| Λ, registered log-slope form | 499 | 7 | 0.04464 | [-0.4276, 2.0061] |
| Λ, positivity-free linear-slope companion | 499 | 499 | 0.000061 | [-0.00289, 0.00264] |

**RD-U2C-1 (disclosed re-posing).** The registration poses the null directly on Λ on the ground that a slope contrast is well behaved where a ratio is not. That is true of the SLOPE; it is not true of the LOGARITHM the registered slope is taken on. A within-quarter relabelling drives E(b) to within a few 1e−4 of zero, its sign then flips freely across bins, and `log E(b)` is undefined for any replicate with a non-positive bin — so the registered null is computed with the same positivity rule and retains 7 of 499 replicates. Beside it the runner reports the positivity-free LINEAR slope contrast (OLS of E(b) on gap_years, no logarithm), defined on 100.0% of replicates, whose realized center is 0.000061 against a realized value of -0.0162 on that same scale. The linear contrast is NOT level-free — a lower-level row has a shallower absolute slope whatever its rate — which is exactly why it is not the estimand and why its realized value need not share Λ's sign; it is read ONLY as the null's location, where both rows are driven to zero and no level confound survives. **No verdict rests on either null**: the verdict is the bootstrap interval on Λ, and the nulls are location checks.

The informative nulls of this leg are the per-row per-bin E(b) permutation centers, which reproduce U2's result on every carrier:

| row | largest absolute E(b) null center (any bin) | smallest E(b) over the fitted bins | ratio |
|---|---|---|---|
| full vocabulary | 5.815e-05 | 0.2720 | 4,678× |
| common (q=0.5, 32 communities) | 8.353e-05 | 0.3333 | 3,991× |
| distinctive (q=0.5, 1159 communities) | 4.326e-05 | 0.2033 | 4,699× |
| taste (per-fold PPMI+SVD d=64, out-of-fold) | 3.664e-04 | 0.2998 | 818× |

### Registration-time projection against the realized width (#71/#79, executed form)

| quantity | projected at registration | realized |
|---|---|---|
| Λ point | +0.10/y | 0.0741/y |
| Λ CI half-width | 0.08–0.10/y | 0.1206/y |
| λ_common | 0.239/y | 0.2535/y |
| λ_distinct | 0.338/y | 0.3276/y |
| λ_taste | 0.16/y | 0.1736/y |

The projection was made from U2b's realized dispersion BEFORE this run and is reported here whether it flattered the design or not: the realized half-width is 1.206× the top of the projected range. This is the #71 convention executed at registration time rather than discovered afterwards, which is the whole point of defect #79's convention.

**Honest anomaly — the bigger pool bought a WIDER interval.** The projection's shrink argument was that the m = 5 pool adds 21.8% authors over U2b's failed primary (424 against 348) and 79.6% pairs (179,107 against 99,714). It did add them, and the interval still came out wider than the confirmatory arm's, which runs on a SMALLER pool (108,716 pairs, 401 authors): the primary's half-width is 0.1206/y against the confirmatory arm's 0.0859/y, a ratio of 1.404×. The mechanism is visible in the per-row half-widths below: lowering the floor admits blocks with as few as m events in a sub-vocabulary, and a carrier-restricted vector built from five events is a far noisier point on the sphere than one built from ten. Pool size and per-block precision trade against each other here, and the registration priced only the first. The projection convention (#71/#79) held — the number was stated before the run and is reported against — but the model behind the number did not.

| row | primary (q=0.5, m=5) λ half-width | confirmatory (q=0.7, m=10) λ half-width | ratio |
|---|---|---|---|
| full | 0.1255 | 0.1178 | 1.065× |
| common | 0.1418 | 0.1408 | 1.007× |
| distinct | 0.1558 | 0.1153 | 1.352× |
| taste | 0.0883 | 0.0834 | 1.059× |

## Confirmatory arm (q = 0.7, m = 10)

Registered as the one sensitivity that also clears both #69 targets (108,716 pairs, 401 authors). Divergence in cell carries a #73 flag; the PRIMARY routes.

| row | λ (1/y) | 95% CI | CI half-width | R² (log-linear) | E0 | F = E(2–3y)/E(0–90d) |
|---|---|---|---|---|---|---|
| full vocabulary | **0.2751** | [0.1797, 0.4153] | 0.1178 | 0.9724 | 0.4296 | 0.5181 |
| common (q=0.7, 104 communities) | **0.2315** | [0.1222, 0.4039] | 0.1408 | 0.9895 | 0.5006 | 0.5792 |
| distinctive (q=0.7, 1087 communities) | **0.3176** | [0.2210, 0.4515] | 0.1153 | 0.9129 | 0.3220 | 0.4583 |
| taste (per-fold PPMI+SVD d=64, out-of-fold) | **0.1515** | [0.0955, 0.2622] | 0.0834 | 0.9619 | 0.3750 | 0.7054 |

| quantity | point | 95% CI | half-width | cell |
|---|---|---|---|---|
| Λ (confirmatory) | **0.0861** | [-0.0109, 0.1609] | 0.0859 | `SIGN_UNRESOLVED` |
| λ_taste − λ_full (confirmatory) | **-0.1236** | [-0.2798, 0.0300] | 0.1549 | — |

No #73 flag: the confirmatory arm lands in the same cell (`SIGN_UNRESOLVED`) as the primary.

## G0 — U2b four-row bit-comparison (#56: inheritance is not exemption)

U2b's primary configuration (q = 0.5, m = 10) was recomputed here from the same cache through the same imported estimator — all four rows, including the five taste folds — and compared field by field against its committed artifacts (`/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/results/m4_u2b_persistence_budget/rows.json`). Status **PASS**; maximum absolute difference across all 60 compared fields: 0.000e+00; bitwise identical: yes.

| row | committed key | fields | bitwise identical | max abs difference |
|---|---|---|---|---|
| full | `full` | 15 | yes | 0.000e+00 |
| common | `common (q=0.5, 32 communities)` | 15 | yes | 0.000e+00 |
| distinct | `distinct (q=0.5, 1159 communities)` | 15 | yes | 0.000e+00 |
| taste | `taste (d=64, out-of-fold)` | 15 | yes | 0.000e+00 |

## Taste row — fold purity (blocking gate)

Embeddings are fitted on TRAINING authors' first-half events only; curves are read on TEST authors' pairs and pooled by unweighted mean over folds (U1 convention). Purity is a mass identity, asserted inside the run for every fold of every configuration.

| configuration | fold | train | test | overlap | fitted mass | train first-half mass | test mass excluded | test blocks |
|---|---|---|---|---|---|---|---|---|
| G0 (q=0.5, m=10) | 0 | 679 | 170 | 0 | 869,475 | 869,475 | 284,246 | 5,081 |
| G0 (q=0.5, m=10) | 1 | 679 | 170 | 0 | 926,685 | 926,685 | 227,036 | 4,073 |
| G0 (q=0.5, m=10) | 2 | 679 | 170 | 0 | 938,266 | 938,266 | 215,455 | 4,187 |
| G0 (q=0.5, m=10) | 3 | 679 | 170 | 0 | 928,374 | 928,374 | 225,347 | 3,353 |
| G0 (q=0.5, m=10) | 4 | 680 | 169 | 0 | 952,084 | 952,084 | 201,637 | 3,353 |
| primary (q=0.5, m=5) | 0 | 679 | 170 | 0 | 869,475 | 869,475 | 284,246 | 6,873 |
| primary (q=0.5, m=5) | 1 | 679 | 170 | 0 | 926,685 | 926,685 | 227,036 | 5,693 |
| primary (q=0.5, m=5) | 2 | 679 | 170 | 0 | 938,266 | 938,266 | 215,455 | 5,554 |
| primary (q=0.5, m=5) | 3 | 679 | 170 | 0 | 928,374 | 928,374 | 225,347 | 4,796 |
| primary (q=0.5, m=5) | 4 | 680 | 169 | 0 | 952,084 | 952,084 | 201,637 | 4,569 |
| confirmatory (q=0.7, m=10) | 0 | 679 | 170 | 0 | 869,475 | 869,475 | 284,246 | 4,316 |
| confirmatory (q=0.7, m=10) | 1 | 679 | 170 | 0 | 926,685 | 926,685 | 227,036 | 4,205 |
| confirmatory (q=0.7, m=10) | 2 | 679 | 170 | 0 | 938,266 | 938,266 | 215,455 | 4,080 |
| confirmatory (q=0.7, m=10) | 3 | 679 | 170 | 0 | 928,374 | 928,374 | 225,347 | 3,506 |
| confirmatory (q=0.7, m=10) | 4 | 680 | 169 | 0 | 952,084 | 952,084 | 201,637 | 3,464 |

Per-fold floor shares at the primary configuration: 0.5145, 0.5476, 0.8129, 0.7867, 0.7404.

## Registered leans (disclosed knowledge, not predictions)

- **L1** (Λ > 0 with point ≈ +0.10/y (disclosed knowledge, not a prediction)): **SIGN HELD IN POINT, UNRESOLVED IN INTERVAL** — realized Λ 0.0741/y [-0.0558, 0.1854], cell `SIGN_UNRESOLVED`.
- **L2** (λ_taste is the SMALLEST rate of the four rows (projected ≈ 0.16/y)): **HELD** — λ_taste 0.1736/y against λ_full 0.2943, λ_common 0.2535, λ_distinct 0.3276; slowest row `taste`.

## Boundaries

- **The eq-12 projection caution, carried into the verdict as registered:** this leg reads ONE slow-time projection of the transition kernel K_u (eq 12) onto the marginal selection distribution π_u over the 1191-community vocabulary, split by carrier. A decay-rate contrast here is a statement about π_u on the Hellinger unigram sphere over calendar time, never about a psychological attribute (§5.4), and 'common' and 'distinctive' are EVENT-MASS strata of a subreddit vocabulary, not the T-line's personality/identity constructs — the T-line proposition is what motivates the test, not what the strata mean.
- **U2's three-year scoping binds every rate here.** λ is estimated over a window that ends at the 2–3y bin (realized mean gap 2.396 years), so it is a THREE-YEAR CORE rate and nothing else. U2's curve had not flattened at its verdict endpoint, the log-linear form is a local description of the observed window rather than a demonstrated law, and no rate in this report licenses a half-life, an asymptote or any permanent-rate language. Extrapolating λ past the observed span is forbidden prose.
- **The provisional sign was KNOWN at registration and is disclosed.** U2b's Δfloor point was negative in all five of its configurations (COMMON_STANDING direction) when U2c was registered. U2c is a verdict-issuing completion under corrected gate arithmetic (#78) and a ratio-free estimand (#79), not an independent prediction, and its leans are disclosures rather than forecasts. The registration also stated BEFORE the run that detection is borderline at the projected half-width 0.08–0.10/y — realized 0.1206/y.
- **LEVEL differences across rows are never interpreted** (U2b's comparison rule, inherited): a restricted row is a lower-dimensional, differently attenuated view of the same block. The decay RATE is the level-free quantity this leg exists to compare — a gap-independent attenuation moves log E0, not λ — but the E(b) levels tabulated beside it do not transport across rows.
- **No equivalence cell exists in this leg, by registration.** At the projected width no |Λ| band was reachable, so posing one would have repeated #79a. A near-zero Λ therefore reads SIGN_UNRESOLVED and is reported as an interval, never as a demonstration of equal rates.
- The eligibility floor is not neutral. Requiring ≥ m events in BOTH sub-vocabularies keeps only BALANCED blocks, so the intersection set over-represents authors who mix common and distinctive communities within a 50-event window. Lowering the floor from m = 10 to m = 5 enlarges the pool by admitting more lopsided blocks, which is a different sample, not a bigger draw from the same one.
- The taste row's cross baseline is fold-local while the other three rows share one pool-level reservoir, and its bootstrap draws are fold-stratified rather than pool-level, so the secondary contrast λ_taste − λ_full is NOT paired and its interval is conservative.
- Label-free and corpus-level throughout: no Big5 or MBTI value is read anywhere in this leg, and no per-author quantity is reported or committed.

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
  "cache": "/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/results/m4_u1_order_identity/events_cache.npz",
  "cells": [
    "SIGN_UNRESOLVED",
    "COMMON_STANDING",
    "DISTINCT_SLOWER"
  ],
  "days_per_year": 365.25,
  "descriptive_bin_excluded_from_the_fit": "3y+",
  "epoch_origin_utc": "2014-12-31T23:54:39Z",
  "equivalence_cell": null,
  "fit_bins": [
    "0-90d",
    "90-180d",
    "180-365d",
    "1-2y",
    "2-3y"
  ],
  "g0_configuration": {
    "m": 10,
    "q": 0.5
  },
  "gate_anchors": {
    "confirmatory q=0.7/m=10": {
      "authors_2_3y": 401,
      "m": 10,
      "pairs_2_3y": 108716,
      "q_milli": 700
    },
    "primary q=0.5/m=5": {
      "authors_2_3y": 424,
      "m": 5,
      "pairs_2_3y": 179107,
      "q_milli": 500
    }
  },
  "inherited_from_u2": [
    "build_blocks (exact-K disjoint blocks, Hellinger features)",
    "assign_quarters / gap_bin (epoch cells and gap bins)",
    "compute_arm (epoch-matched EXACT stratified cross baseline, RD-U2-1 form; within-quarter permutation scaffold; author cluster bootstrap)",
    "scan_for_cohort_ids (ID-leak gate)"
  ],
  "inherited_from_u2b": [
    "community_ranking / common_prefix (the vocabulary split)",
    "block_counts_over (exact sub-vocabulary counts as K*f^2)",
    "renormalize (the carrier restriction)",
    "self_pair_census (the gate's exact predicate)",
    "ppmi_svd / first_half_counts / taste_folds / pool_fold_results",
    "summarize_row and percentile_ci"
  ],
  "k": 50,
  "m_confirmatory": 10,
  "m_primary": 5,
  "pool_gate_min_authors_2_3y": 400,
  "pool_gate_min_pairs_2_3y": 100000,
  "pool_min_blocks": 4,
  "projected_half_width": [
    0.08,
    0.1
  ],
  "projected_lambda_common": 0.239,
  "projected_lambda_distinct": 0.338,
  "projected_lambda_point": 0.1,
  "projected_lambda_taste": 0.16,
  "q_confirmatory": 0.7,
  "q_primary": 0.5,
  "quarter_days": 91.3,
  "recorded_choices": {
    "bootstrap_pairing": "compute_arm draws its author multinomial from seed + 11 with the same author count for every row on the shared block set, so Lambda's bootstrap is PAIRED replicate by replicate; the secondary contrast lambda_taste - lambda_full is NOT paired (fold-stratified draws against pool-level draws) and its interval is correspondingly conservative",
    "fit_window": "OLS over the FIVE verdict bins 0-90d / 90-180d / 180-365d / 1-2y / 2-3y; the 3y+ bin is reported descriptively and NEVER enters the fit (registration, inherited from U2)",
    "gap_years": "the row's REALIZED per-bin mean self-pair gap in days on the intersection set, divided by 365.25 days per year; the gaps are held at their realized values inside the bootstrap and the permutation, because the resampling machinery inherited from U2 resamples the excess, not the gap grid",
    "gate_anchor_semantics": "#78: the gate quantities are U2b's REALIZED intersection numbers, i.e. the gate predicate already executed on census data; this runner re-executes the same predicate and compares EXACTLY, and any mismatch stops the leg before any row is read",
    "lambda_sign": "lambda = -slope of log E(b) on gap_years, so a positive lambda is decay; Lambda = lambda_distinct - lambda_common is positive when the DISTINCTIVE decays faster",
    "permutation_null_on_lambda": "RD-U2C-1 (disclosed): the registration poses the null DIRECTLY on Lambda as a slope contrast. The LOG form of that slope is undefined on most permutation replicates, because a within-quarter relabelling drives E(b) to zero and its sign then flips freely, so the registered null is computed with the same positivity rule and its RETAINED count is reported as the honest measure of how much it can say; beside it the positivity-free LINEAR slope contrast (OLS of E(b) on gap_years, no logarithm) is reported on all 499 replicates as the location check the registration's argument actually needs. No verdict rests on either null; the verdict is the bootstrap interval on Lambda",
    "positivity_rule": "a replicate whose five fitted bins contain any non-positive E(b) has no logarithm and is DROPPED, with the count reported; for Lambda a replicate is dropped when EITHER row is non-positive",
    "row_order": "full / common / distinct / taste, matching U2b's committed rows.json order for the G0 bit-comparison",
    "taste_cross_reservoir": "fold-local, inherited from U2b unchanged: a fold's cross baseline uses that fold's test authors only, because two folds' embeddings are different coordinate systems"
  },
  "registration_commit": "6a4a5bb",
  "script_sha256": "3003bbbac3f7ba67e426d93ee609cd11adca46df6ae85643164829fa69f77276",
  "seed": 20260818,
  "taste_dim": 64,
  "taste_folds": 5,
  "u2_machinery": "/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/scripts/run_suica_m4_u2_persistence_curve.py",
  "u2_machinery_sha256": "09dda64dffeaaa5e38f7a0008540474bf25fb1ddef9b927cde0dd568d8572ef3",
  "u2b_artifacts": "/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/results/m4_u2b_persistence_budget",
  "u2b_machinery": "/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/scripts/run_suica_m4_u2b_persistence_budget.py",
  "u2b_machinery_sha256": "8153d299f76ceca4a5a5fcbec74a2f140463f71844482ee2960c5b51c6b6ec46"
}
```

Artifacts (gitignored): `results/m4_u2c_decay_rate_contrast/` — `config.json`, `config.sha256.json`, `anchors.json`, `split_census.json`, `gate_anchor.json`, `g0_anchor_comparison.json`, `arms.json`, `taste_purity.json`, `verdict.json`, `id_leak_scan.json`, `report_payload.json`, `run_log.jsonl`.

