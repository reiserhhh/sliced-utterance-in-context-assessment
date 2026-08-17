# SUICA M4-U2b — the persistence budget by carrier

**Outcome: `POOL_GATE_UNMET`.**

**THE LEG STOPS AT THE REGISTERED POOL GATE (#69). NO CLASSIFICATION CELL IS ASSIGNED AND NO VERDICT IS CLAIMED.** The registration pins that the intersection pair set at q = 0.5 / m = 10 must retain ≥ 100,000 pairs and ≥ 400 contributing authors in the 2–3y bin, and that the leg STOPS and reports if that is unmet with no silent re-split. It is unmet on BOTH clauses: **99,714 pairs** (0.997× the target) and **348 authors** (0.870× the target). Everything below the gate section is computed and reported so the planner can adjudicate once, and every quantity in it is **PROVISIONAL and non-verdict-carrying**.

Executed from the registration committed at `96f7e40` in `docs/SUICA_M4_U_WHEN_ORDER_PLAN.md` (section "U2b — the persistence budget by carrier (registered BEFORE run, 2026-08-18)"). Run window 2026-08-17T22:25:22.373510Z to 2026-08-17T22:27:14.220465Z; report generated 2026-08-17T22:27:14.220467Z. Every number in this report is produced from the run's artifacts by `scripts/run_suica_m4_u2b_persistence_budget.py` (rule 24).

## Gates

| gate | status |
|---|---|
| cache anchor gate (3,005,360 events / 1401 authors / 1191 vocabulary) | PASS |
| split census — blocking pins (universe, Common(0.5) size and share, pool authors and blocks) | PASS |
| split census — all registered pins | PASS |
| G0 — U2 primary arm bit-comparison (#56) | PASS |
| registered pool gate #69 (intersection, 2-3y) | UNMET |
| taste-row fold purity (mass identity, zero test mass) | PASS |
| sub-vocabulary counts integral (max deviation 1.05e-05) | PASS |
| no synthetic gate required (R layer, no world simulated) | N/A |
| ID-leak scan (0 of 1401 cohort IDs in committed files) | PASS |

## The vocabulary split (census, #77 computations pinned)

Universe: the in-vocabulary cohort events of the U1 cache. Communities are ranked by descending event count over that universe (descending event count, ties broken by ascending vocab index); Common(q) is the smallest rank prefix with cumulative share ≥ q; Distinctive(q) is its complement within the 1,191-community vocabulary.

| registered census quantity | registered | observed | status |
|---|---|---|---|
| `universe_in_vocab_events` *(blocking)* | 2348361 | 2348361 | PASS |
| `common_size_q30` | 8 | 8 | PASS |
| `common_share_q30` | 0.3077 | 0.3077 | PASS |
| `common_size_q50` *(blocking)* | 32 | 32 | PASS |
| `common_share_q50` *(blocking)* | 0.5036 | 0.5036 | PASS |
| `common_size_q70` | 104 | 104 | PASS |
| `common_share_q70` | 0.7008 | 0.7008 | PASS |
| `pool_authors` *(blocking)* | 849 | 849 | PASS |
| `pool_blocks` *(blocking)* | 45731 | 45731 | PASS |
| `block_common_q05_q25_q50` | [0, 8, 25] | [0, 8, 25] | PASS |
| `block_distinct_q05_q25_q50` | [0, 6, 25] | [0, 6, 25] | PASS |
| `eligible_pairs_common_m10_2_3y` | 253946 | 253946 | PASS |
| `eligible_pairs_distinct_m10_2_3y` | 230661 | 230661 | PASS |
| `eligible_authors_distinct_m10_2_3y` | 506 | 506 | PASS |

## The registered pool gate (#69) — the leg's decision point

Because a block carries exactly K = 50 in-vocabulary events, the eligibility predicate is a per-BLOCK property (common ≥ m AND K − common ≥ m), so the intersection PAIR set is exactly the same-author pair set of the eligible BLOCK subset. All four rows therefore share identical pair indices, an identical cross reservoir, identical permutation plans and identical bootstrap author draws (#72 satisfied by construction, not by alignment).

| set at q=0.5, m=10 | 2–3y pairs | 2–3y authors | eligible blocks |
|---|---|---|---|
| common (marginal) | 253,946 | 408 | 33,352 |
| distinct (marginal) | 230,661 | 506 | 32,426 |
| intersection | 99,714 | 348 | 20,047 |

**Gate: UNMET.** Required ≥ 100,000 pairs (realized 99,714, 0.9971× target) and ≥ 400 authors (realized 348, 0.8700× target).

The registration's own per-row eligible-pair census reproduces EXACTLY — common 253,946 and distinct 230,661 pairs, 506 distinct-eligible authors — so the construction here IS the planner's construction. What the census did not carry is the INTERSECTION of the two eligibilities, which is far smaller than either marginal: requiring ≥ 10 events in BOTH halves of a 50-event block excludes lopsided blocks, and lopsidedness is author-persistent. The intersection keeps 39.3% of the common row's 2–3y pairs and 61.7% of U2's 564 2–3y contributors.

## The four rows — PROVISIONAL (the pool gate is unmet)

**Binding comparison rule:** LEVEL differences across rows are never interpreted — a restricted row carries its own, block-varying attenuation, so E_common and E_distinct are not on a common scale. Only within-row floor shares and their contrasts transport.

| row | 0-90d | 90-180d | 180-365d | 1-2y | 2-3y | 3y+ |
|---|---|---|---|---|---|---|
| full | 0.5218 | 0.4691 | 0.4262 | 0.3430 | 0.2672 | 0.2441 |
| common (q=0.5, 32 communities) | 0.5879 | 0.5511 | 0.5152 | 0.4296 | 0.3405 | 0.3182 |
| distinct (q=0.5, 1159 communities) | 0.4440 | 0.3753 | 0.3323 | 0.2578 | 0.2055 | 0.2012 |
| taste (d=64, out-of-fold) | 0.4278 | 0.4071 | 0.3810 | 0.3264 | 0.2956 | 0.2636 |

E(b) with 95% cluster-bootstrap CI and the within-quarter permutation band, at the two verdict-relevant bins:

| row | blocks | self pairs (2–3y) | E(0–90d) [CI] | null band | E(2–3y) [CI] | null band |
|---|---|---|---|---|---|---|
| full | 20,047 | 99,714 | 0.5218 [0.4549, 0.5984] | [-0.00196, 0.00209] | 0.2672 [0.1787, 0.3556] | [-0.00298, 0.00360] |
| common (q=0.5, 32 communities) | 20,047 | 99,714 | 0.5879 [0.5391, 0.6439] | [-0.00383, 0.00451] | 0.3405 [0.2075, 0.4428] | [-0.00686, 0.00740] |
| distinct (q=0.5, 1159 communities) | 20,047 | 99,714 | 0.4440 [0.3606, 0.5473] | [-0.00064, 0.00067] | 0.2055 [0.1410, 0.2933] | [-0.00071, 0.00070] |
| taste (d=64, out-of-fold) | 20,047 | 99,714 | 0.4278 [0.4057, 0.4585] | [-0.00386, 0.00370] | 0.2956 [0.2396, 0.3529] | [-0.00738, 0.00788] |

Self and epoch-matched cross means behind those excesses:

| row | self mean (0–90d) | cross (0–90d) | self mean (2–3y) | cross (2–3y) | perm p (existence) | perm p (decay) |
|---|---|---|---|---|---|---|
| full | 0.6122 | 0.0903 | 0.3499 | 0.0827 | 0.0020 | 0.0020 |
| common (q=0.5, 32 communities) | 0.7651 | 0.1771 | 0.5125 | 0.1720 | 0.0020 | 0.0020 |
| distinct (q=0.5, 1159 communities) | 0.4627 | 0.0186 | 0.2186 | 0.0131 | 0.0020 | 0.0020 |
| taste (d=64, out-of-fold) | 0.8859 | 0.4628 | 0.7379 | 0.4525 | 0.0020 | 0.0020 |

### Floor shares

| row | D = E(0–90d) − E(2–3y) [CI] | F = E(2–3y)/E(0–90d) [CI] |
|---|---|---|
| full | 0.2546 [0.1564, 0.3600] | **0.5120** [0.3441, 0.6793] |
| common (q=0.5, 32 communities) | 0.2474 [0.1258, 0.3858] | **0.5792** [0.3603, 0.7760] |
| distinct (q=0.5, 1159 communities) | 0.2385 [0.1329, 0.3481] | **0.4628** [0.3000, 0.6655] |
| taste (d=64, out-of-fold) | 0.1322 [0.0754, 0.1943] | **0.6909** [0.5530, 0.8210] |

### The verdict contrast Δfloor = F_distinct − F_common

| contrast | point | 95% CI | CI half-width | null center | null IQR | cell |
|---|---|---|---|---|---|---|
| Δfloor = F_distinct − F_common | **-0.1163** | [-0.2620, 0.0299] | 0.1459 | 0.04479 | [-2.346, 2.651] | `UNRESOLVED_SPLIT` |
| F_taste − F_full | **0.1789** | [-0.0373, 0.3749] | 0.2061 | -0.13905 | [-3.510, 4.181] | `UNRESOLVED_SPLIT` |

**The floor-share null is a ratio of two quantities the permutation drives to zero, so its permutation distribution is heavy-tailed by construction and its 95% band is not an informative bound.** The registration's claim is about the null's LOCATION, and that is what is checked: Δfloor's realized permutation center is 0.04479 with IQR [-2.346, 2.651] (100.0% of replicates finite). The informative nulls of this leg are the per-bin E(b) bands in the table above, which sit three to four orders of magnitude inside their effects, exactly as in U2.

### Equivalence-band projection (#71)

The `NO_LAYER_SPLIT` equivalence band is |Δfloor| < 0.1. The realized half-width of Δfloor's 95% CI is 0.1459 (1.459× the band). The design could NOT have declared a null split at this power: the achievable interval is WIDER than the equivalence band, so `NO_LAYER_SPLIT` was not reachable and a near-zero Δfloor would have read `UNRESOLVED_SPLIT` rather than equivalence.

## Sensitivity grid (q × m)

Registered as one-at-a-time variations on the primary contrast: q ∈ {0.3, 0.7} at m = 10, and m ∈ {5, 15} at q = 0.5. Each row reports its OWN intersection pool realization against the registered #69 targets.

| q | m | Common(q) | 2–3y pairs | 2–3y authors | #69 | F_common | F_distinct | Δfloor [CI] | cell | #73 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 10 | 32 | 99,714 | 348 | UNMET | 0.5792 | 0.4628 | -0.1163 [-0.2620, 0.0299] | `UNRESOLVED_SPLIT` | — |
| 0.3 | 10 | 8 | 48,862 | 199 | UNMET | 0.8109 | 0.3703 | -0.4406 [-0.5648, -0.2011] | `COMMON_STANDING` | #73 |
| 0.7 | 10 | 104 | 108,716 | 401 | PASS | 0.5792 | 0.4583 | -0.1209 [-0.2256, -0.0007] | `COMMON_STANDING` | #73 |
| 0.5 | 5 | 32 | 179,107 | 424 | PASS | 0.5625 | 0.4646 | -0.0980 [-0.2144, 0.0424] | `NO_LAYER_SPLIT` | #73 |
| 0.5 | 15 | 32 | 42,230 | 259 | UNMET | 0.5899 | 0.4817 | -0.1083 [-0.2789, 0.0378] | `UNRESOLVED_SPLIT` | — |

- **#73 flag** — q=0.3/m=10 lands in `COMMON_STANDING` while the primary configuration lands in `UNRESOLVED_SPLIT`
- **#73 flag** — q=0.7/m=10 lands in `COMMON_STANDING` while the primary configuration lands in `UNRESOLVED_SPLIT`
- **#73 flag** — q=0.5/m=5 lands in `NO_LAYER_SPLIT` while the primary configuration lands in `UNRESOLVED_SPLIT`

**Registered configurations that DO clear the #69 targets:** q=0.7/m=10 (108,716 pairs, 401 authors), q=0.5/m=5 (179,107 pairs, 424 authors). This is reported as adjudication data only. Promoting one of them to primary is a re-split and belongs to the planner, not to this executor.

## G0 — U2 anchor bit-comparison (#56: inheritance is not exemption)

U2's primary arm was RECOMPUTED here from the same cache through the same imported estimator and compared field-by-field against its committed artifacts (`/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/results/m4_u2_persistence_curve/arms.json`). Status **PASS**; maximum absolute difference across 20 compared fields: 0.000e+00; bitwise identical: yes.

| field | bitwise identical | max abs difference |
|---|---|---|
| `curve` | yes | 0.000e+00 |
| `curve_ci` | yes | 0.000e+00 |
| `curve_null_band` | yes | 0.000e+00 |
| `curve_null_center` | yes | 0.000e+00 |
| `curve_null_mean` | yes | 0.000e+00 |
| `self_mean` | yes | 0.000e+00 |
| `cross_mean_matched` | yes | 0.000e+00 |
| `mean_gap_days` | yes | 0.000e+00 |
| `d` | yes | 0.000e+00 |
| `d_ci` | yes | 0.000e+00 |
| `d_null_band` | yes | 0.000e+00 |
| `d_null_center` | yes | 0.000e+00 |
| `floor_share` | yes | 0.000e+00 |
| `floor_share_ci` | yes | 0.000e+00 |
| `perm_p_existence` | yes | 0.000e+00 |
| `perm_p_decay` | yes | 0.000e+00 |
| `self_pairs` | yes | 0.000e+00 |
| `n_blocks` | yes | 0.000e+00 |
| `n_authors` | yes | 0.000e+00 |
| `n_quarters` | yes | 0.000e+00 |

## Taste row — fold purity (blocking gate)

Embeddings are fitted on TRAINING authors' first-half events only (per author, the median of that author's in-vocabulary event timestamps; first half = created_utc <= median (SR1/T2's early/late rule without SR1's 4000-timestamp cap, which existed only to reproduce SR1's frozen halves)); curves are read on TEST authors' pairs and pooled by unweighted mean over folds (U1 convention). Purity is the mass identity: the fitted count matrix's total must equal the training authors' first-half in-vocabulary mass EXACTLY, and the test authors' mass must be entirely absent from it.

| fold | train authors | test authors | overlap | fitted mass | train first-half mass | test mass excluded | test blocks |
|---|---|---|---|---|---|---|---|
| 0 | 679 | 170 | 0 | 869,475 | 869,475 | 284,246 | 5,081 |
| 1 | 679 | 170 | 0 | 926,685 | 926,685 | 227,036 | 4,073 |
| 2 | 679 | 170 | 0 | 938,266 | 938,266 | 215,455 | 4,187 |
| 3 | 679 | 170 | 0 | 928,374 | 928,374 | 225,347 | 3,353 |
| 4 | 680 | 169 | 0 | 952,084 | 952,084 | 201,637 | 3,353 |

Per-fold floor shares: 0.5547, 0.4806, 0.8310, 0.7938, 0.7992.

## Registered descriptive — the mix-shift trajectory (non-verdict-moving)

Mean common-share of a block (calendar year of the block midpoint), over all 45,731 pool blocks at q = 0.5:

| era | blocks | mean common share | sd |
|---|---|---|---|
| 2015 | 6,830 | 0.4517 | 0.3375 |
| 2016 | 11,435 | 0.4886 | 0.3594 |
| 2017 | 14,427 | 0.5407 | 0.3628 |
| 2018 | 10,938 | 0.5295 | 0.3532 |
| 2019 | 2,101 | 0.4393 | 0.3492 |

The same quantity by the block's position in its author's own tenure (quintile of within-author block index), which separates a platform-level mix shift from a personal one:

| tenure quintile | blocks | mean common share | sd |
|---|---|---|---|
| Q1 | 9,133 | 0.4987 | 0.3590 |
| Q2 | 9,175 | 0.5056 | 0.3558 |
| Q3 | 9,115 | 0.5223 | 0.3550 |
| Q4 | 9,175 | 0.5211 | 0.3566 |
| Q5 | 9,133 | 0.4875 | 0.3577 |

## Registered leans

- **L1** (DISTINCTIVE_STANDING with point Δfloor in (0.05, 0.25]): **MISSED (PROVISIONAL: the pool gate is unmet)** — realized cell `UNRESOLVED_SPLIT`, point Δfloor -0.1163 [-0.2620, 0.0299]
- **L2** (the taste row posts the highest floor share of all four rows (F_taste ≥ F_full)): **HELD (PROVISIONAL: the pool gate is unmet)** — F_taste 0.6909, F_full 0.5120, highest row `taste (d=64, out-of-fold)` at 0.6909

## Boundaries

- **NO VERDICT IS CLAIMED.** The registered #69 pool gate is unmet at the primary configuration, so this leg assigns no classification cell. Every estimate below the gate section is PROVISIONAL and exists so the planner can adjudicate the re-split it now owns; none of it may be cited as a U2b result.
- **The eq-12 projection caution, carried into the outcome as registered:** this leg reads ONE slow-time projection of the transition kernel K_u (eq 12) onto the marginal selection distribution π_u over the 1191-community vocabulary, now split by carrier. A layer split here would be a statement about π_u on the Hellinger unigram sphere over calendar time, never about a psychological attribute (§5.4), and 'common' and 'distinctive' are EVENT-MASS strata of a subreddit vocabulary, not the T-line's personality/identity constructs — the T-line proposition is what motivates the test, not what the strata mean.
- **U2's three-year scoping binds every floor share here.** A floor share is E(2-3y)/E(0-90d): what survives THREE YEARS, not a demonstrated permanent floor. U2's curve had not flattened by its verdict endpoint (E(3y+) below E(2-3y), the exponential asymptote weakly identified below both), so 'permanent floor' and 'permanent core' are forbidden prose here as they are in U2; 'three-year core' is the licensed phrase, and no floor share in this report may be extrapolated past the observed span.
- **LEVEL differences across rows are never interpreted** (registered comparison rule): a restricted row is a lower-dimensional, differently attenuated view of the same block, and the attenuation varies block by block with how much mass falls in that sub-vocabulary. Only within-row floor shares and their contrasts transport across rows.
- The eligibility floor is not neutral. Requiring >= m events in BOTH sub-vocabularies keeps only BALANCED blocks, so the intersection set over-represents authors who mix common and distinctive communities within a 50-event window and under-represents specialists of either kind. That selection is the price of the shared pair set (#72) and it is why the pool gate exists.
- The taste row's cross baseline is fold-local while the other three rows share one pool-level reservoir, so the taste row's LEVEL is not on the other rows' scale even before attenuation is considered. Its floor share still transports under the comparison rule; its E(b) values do not.
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
  "descriptive_bin": "3y+",
  "epoch_origin_utc": "2014-12-31T23:54:39Z",
  "equivalence_band": 0.1,
  "inherited_from_u2": [
    "build_blocks (exact-K disjoint blocks, Hellinger features)",
    "assign_quarters / gap_bin (epoch cells and gap bins)",
    "compute_arm (epoch-matched EXACT stratified cross baseline, RD-U2-1 form; within-quarter permutation scaffold; author cluster bootstrap)",
    "scan_for_cohort_ids (ID-leak gate)"
  ],
  "k": 50,
  "lean_delta": [
    0.05,
    0.25
  ],
  "m_primary": 10,
  "m_sensitivities": [
    5,
    15
  ],
  "pool_gate_min_authors_2_3y": 400,
  "pool_gate_min_pairs_2_3y": 100000,
  "pool_min_blocks": 4,
  "q_primary": 0.5,
  "q_sensitivities": [
    0.3,
    0.7
  ],
  "quarter_days": 91.3,
  "recorded_choices": {
    "bootstrap_cross_baseline": "inherited from U2 unchanged: cell cross means are held at their full-row values inside the cluster bootstrap; only the self side and the epoch-matching weights are resampled",
    "bootstrap_pairing": "compute_arm draws its author multinomial from seed + 11 with the same author count for every row on the shared block set, so \u0394floor's bootstrap is PAIRED replicate by replicate; the secondary contrast F_taste \u2212 F_full is NOT paired (fold-stratified against pool-level draws) and its interval is correspondingly conservative",
    "community_ranking_tie_break": "descending event count, ties broken by ascending vocab index",
    "eligibility_is_a_block_property": "a block holds exactly K in-vocabulary events, so 'both blocks hold >= m events in BOTH sub-vocabularies' reduces to the per-block predicate (common >= m AND K - common >= m); the intersection PAIR set is therefore exactly the same-author pair set of the eligible BLOCK subset, and all rows share pair indices, cross reservoir, permutation plans and bootstrap draws EXACTLY (#72)",
    "floor_share_null": "the permutation null of a RATIO whose numerator and denominator are both driven to zero is heavy-tailed by construction; the registration's claim is about the null's LOCATION, so the center and IQR are the reported checks and the 95% band is reported but not read as a bound",
    "mix_shift_eras": "calendar year of the block midpoint; a within-author tenure-quintile variant is reported beside it because 'account era' admits both readings and the descriptive is non-verdict-moving",
    "pool_gate_stop_semantics": "RD-U2B-1 (disclosed): the registered #69 STOP is implemented as a STOP AT THE VERDICT, not a STOP AT THE COMPUTATION \u2014 no cell is assigned and every estimate is labelled PROVISIONAL, while the rows, contrasts and the registered sensitivity grid are still computed so the planner can adjudicate from numbers rather than from an empty report. No re-split is performed and no configuration is promoted",
    "pool_rule_not_recomputed": "the U2 pool (>= 4 blocks at K = 50, 849 authors) is inherited unchanged; eligibility filters BLOCKS inside it and is never used to re-derive a pool, so an author with fewer than two eligible blocks contributes no self pair but still serves as a cross partner",
    "renormalization": "the full Hellinger vector's sub-vocabulary columns, L2-renormalized \u2014 identical to sqrt(counts) over the sub-vocabulary, L2-normalized",
    "sub_vocabulary_counts": "recovered from the Hellinger feature as K * f^2 and asserted integral to 1e-3 before use (the feature is sqrt(count / K) and already unit-norm because a block's counts sum to K)",
    "taste_block_vector": "features @ embedding (the Hellinger-weighted mean of the block's communities' embeddings), L2-normalized",
    "taste_cross_reservoir": "fold-local: a fold's cross baseline uses that fold's test authors only, because two folds' embeddings are different coordinate systems and a cross-fold cosine is not defined; the SELF pair set is still exactly the intersection set, partitioned by fold",
    "taste_embedding": "PPMI + truncated SVD, d = 64, of the training authors' first-half count matrix; the recipe is reproduced verbatim from scripts/run_suica_m4_t2_matched_residual.py:587-601 and asserted bit-identical to it in the contract tests",
    "taste_first_half_rule": "per author, the median of that author's in-vocabulary event timestamps; first half = created_utc <= median (SR1/T2's early/late rule without SR1's 4000-timestamp cap, which existed only to reproduce SR1's frozen halves)",
    "taste_pooling": "per-fold curves on TEST authors' pairs, pooled by unweighted mean over folds (U1 convention); the bootstrap and permutation replicate matrices are pooled the same way, so the pooled interval is a fold-stratified cluster bootstrap"
  },
  "registration_commit": "96f7e40",
  "script_sha256": "8153d299f76ceca4a5a5fcbec74a2f140463f71844482ee2960c5b51c6b6ec46",
  "seed": 20260818,
  "taste_dim": 64,
  "taste_folds": 5,
  "u2_artifacts": "/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/results/m4_u2_persistence_curve",
  "u2_machinery": "/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/scripts/run_suica_m4_u2_persistence_curve.py",
  "u2_machinery_sha256": "09dda64dffeaaa5e38f7a0008540474bf25fb1ddef9b927cde0dd568d8572ef3",
  "verdict_endpoint_bin": "2-3y"
}
```

Artifacts (gitignored): `results/m4_u2b_persistence_budget/` — `config.json`, `config.sha256.json`, `anchors.json`, `census.json`, `pool_gate.json`, `g0_anchor_comparison.json`, `rows.json`, `contrasts.json`, `sensitivities.json`, `taste_purity.json`, `mix_shift.json`, `verdict.json`, `id_leak_scan.json`, `report_payload.json`, `run_log.jsonl`.

