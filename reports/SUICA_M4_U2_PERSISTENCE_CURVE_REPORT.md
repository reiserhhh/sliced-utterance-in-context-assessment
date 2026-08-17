# SUICA M4-U2 — the personal persistence curve

**Outcome: `DRIFT_WITH_CORE`** — E(0-90d) = 0.6573 [0.5973, 0.7228], decay D = 0.3058 [0.2364, 0.3855], floor share E(2-3y)/E(0-90d) = 0.5348 [0.4203, 0.6320].

Executed from the registration committed at `b864dc7` in `docs/SUICA_M4_U_WHEN_ORDER_PLAN.md` (section "U2 — the personal persistence curve (registered BEFORE run, 2026-08-18)"). Run window 2026-08-17T21:48:30.732133Z to 2026-08-17T21:50:40.015368Z; report generated 2026-08-17T21:50:40.015370Z. Every number in this report is produced from the run's artifacts by `scripts/run_suica_m4_u2_persistence_curve.py` (rule 24).

## Outcome and cell

**The personal selection signature is a MOVING WAVE WITH A STANDING CORE — it drifts, and it does not drift away.**

- Existence: E(0-90d) = 0.6573, 95% cluster-bootstrap CI [0.5973, 0.7228], against a within-quarter permutation band [-0.0009, 0.0009] (permutation p = 0.0020, B = 499).
- Decay: D = E(0-90d) − E(2-3y) = 0.3058, CI [0.2364, 0.3855], null band [-0.0017, 0.0016] (permutation p = 0.0020).
- Endpoint level: E(2-3y) = 0.3515 [0.2708, 0.4270] — the registered verdict endpoint (#74). The 3y+ bin is descriptive and never carries the verdict.
- Floor share E(2-3y)/E(0-90d) = 0.5348 [0.4203, 0.6320]; registered lean [0.6, 0.9] — MISSED (below the lean's bottom).

The intervals straddle no cell boundary, so the point and the interval agree on the cell.

**The 4W projection caution, quoted into the verdict as registered:** this is a SLOW-TIME PROJECTION of the transition kernel K_u (eq 12), not K_u itself. `FIXED_POINT` would mean drift is undetected at this span and this power for this projection — never "no dynamics"; and a detected decay is a statement about the marginal selection distribution π_u on the Hellinger unigram sphere over calendar time, not about any psychological attribute (§5.4).

## The null's own location (#68)

E's expected null location is **0 BY CONSTRUCTION**: under a within-quarter relabelling the same-author pair set of a cell is a uniformly random subset of that cell's pair set, so the self mean and the epoch-matched cross mean share an expectation and their difference has expectation zero. That is an argument, not evidence; the realized center is the check.

| bin | null center (median) | null mean | null 95% band | abs(center) ≤ 0.002 |
|---|---|---|---|---|
| 0-90d | -0.000015 | 0.000002 | [-0.00088, 0.00090] | PASS |
| 90-180d | 0.000024 | -0.000004 | [-0.00088, 0.00091] | PASS |
| 180-365d | -0.000037 | -0.000012 | [-0.00089, 0.00095] | PASS |
| 1-2y | -0.000037 | -0.000022 | [-0.00095, 0.00099] | PASS |
| 2-3y | 0.000016 | 0.000036 | [-0.00143, 0.00168] | PASS |
| 3y+ | 0.000081 | 0.000086 | [-0.00272, 0.00299] | PASS |

D's own null: center -0.000019, mean -0.000034, band [-0.00173, 0.00164].

## The curve — primary arm

| bin | self pairs | self mean cos | epoch-matched cross mean | E(b) | 95% CI | null band | mean gap (d) |
|---|---|---|---|---|---|---|---|
| 0-90d | 1,005,742 | 0.7105 | 0.0532 | 0.6573 | [0.5973, 0.7228] | [-0.00088, 0.00090] | 42.8 |
| 90-180d | 783,654 | 0.6487 | 0.0516 | 0.5971 | [0.5318, 0.6665] | [-0.00088, 0.00091] | 133.5 |
| 180-365d | 1,198,561 | 0.5950 | 0.0503 | 0.5447 | [0.4727, 0.6163] | [-0.00089, 0.00095] | 266.4 |
| 1-2y | 1,248,992 | 0.5033 | 0.0479 | 0.4554 | [0.3784, 0.5274] | [-0.00095, 0.00099] | 518.3 |
| 2-3y | 417,963 | 0.3959 | 0.0444 | 0.3515 | [0.2708, 0.4270] | [-0.00143, 0.00168] | 874.1 |
| 3y+ *(descriptive)* | 100,150 | 0.3091 | 0.0453 | 0.2638 | [0.1869, 0.3339] | [-0.00272, 0.00299] | 1234.7 |

Epoch matching feasibility on the primary arm: the minimum cross-candidate ratio is 26.0× the self-pair count over occupied (quarter-pair × bin) strata and 71.4× at quarter-pair resolution (median over strata 203.3×). The registration censused this as 115.4× without naming its denominator; both resolutions clear the 20× the registered sampler needs, so epoch matching is feasible in every stratum as registered. Self pairs dropped for want of any cross partner: 0 of 4,755,062.

## Equivalence-band width projection (#71)

The FIXED_POINT equivalence margin is 0.2 × E(0-90d) = 0.1315. The realized half-width of D's 95% CI is 0.0745 (0.567× the margin). The design could therefore have DECLARED equivalence had D been near zero: the achievable band is narrower than the margin.

## Arms

| arm | role | authors | blocks | E(0-90d) [CI] | E(2-3y) [CI] | D [CI] | floor share [CI] | cell | #73 |
|---|---|---|---|---|---|---|---|---|---|
| full vocab, pool 849, verdict bins | PRIMARY | 849 | 45,731 | 0.6573 [0.5973, 0.7228] | 0.3515 [0.2708, 0.4270] | 0.3058 [0.2364, 0.3855] | 0.5348 [0.4203, 0.6320] | `DRIFT_WITH_CORE` | — |
| balanced panel (564 authors with 2-3y support) | sensitivity — composition control | 564 | 39,076 | 0.6402 [0.5750, 0.7121] | 0.3506 [0.2764, 0.4228] | 0.2896 [0.2251, 0.3623] | 0.5477 [0.4498, 0.6390] | `DRIFT_WITH_CORE` | — |
| activity tercile 1 (302 authors, <= 650 vocab events) | secondary — decay shape by activity | 302 | 2,347 | 0.7073 [0.6773, 0.7397] | 0.2817 [0.2424, 0.3232] | 0.4256 [0.3728, 0.4778] | 0.3982 [0.3387, 0.4603] | `DRIFT_WITH_CORE` | — |
| activity tercile 2 (265 authors, 650-2050 vocab events) | secondary — decay shape by activity | 265 | 6,416 | 0.6981 [0.6731, 0.7237] | 0.3110 [0.2696, 0.3565] | 0.3871 [0.3376, 0.4333] | 0.4455 [0.3866, 0.5107] | `DRIFT_WITH_CORE` | — |
| activity tercile 3 (282 authors, > 2050 vocab events) | secondary — decay shape by activity | 282 | 36,968 | 0.6523 [0.5890, 0.7178] | 0.3501 [0.2675, 0.4211] | 0.3021 [0.2376, 0.3812] | 0.5368 [0.4223, 0.6277] | `DRIFT_WITH_CORE` | — |
| clean_no_explicit_personality (23 communities removed) | governance echo | 779 | 39,634 | 0.6588 [0.5779, 0.7332] | 0.3418 [0.2687, 0.4145] | 0.3170 [0.2431, 0.3922] | 0.5188 [0.4177, 0.6177] | `DRIFT_WITH_CORE` | — |
| K = 100 blocks | sensitivity — block size | 690 | 22,257 | 0.6994 [0.6449, 0.7581] | 0.3854 [0.3081, 0.4588] | 0.3140 [0.2427, 0.3907] | 0.5511 [0.4485, 0.6463] | `DRIFT_WITH_CORE` | — |

Full curves, every arm:

| arm | 0-90d | 90-180d | 180-365d | 1-2y | 2-3y | 3y+ |
|---|---|---|---|---|---|---|
| full vocab, pool 849, verdict bins | 0.6573 | 0.5971 | 0.5447 | 0.4554 | 0.3515 | 0.2638 |
| balanced panel (564 authors with 2-3y support) | 0.6402 | 0.5812 | 0.5353 | 0.4539 | 0.3506 | 0.2640 |
| activity tercile 1 (302 authors, <= 650 vocab events) | 0.7073 | 0.6152 | 0.5148 | 0.3761 | 0.2817 | 0.2321 |
| activity tercile 2 (265 authors, 650-2050 vocab events) | 0.6981 | 0.6016 | 0.5353 | 0.4167 | 0.3110 | 0.2696 |
| activity tercile 3 (282 authors, > 2050 vocab events) | 0.6523 | 0.5934 | 0.5414 | 0.4525 | 0.3501 | 0.2629 |
| clean_no_explicit_personality (23 communities removed) | 0.6588 | 0.5951 | 0.5452 | 0.4637 | 0.3418 | 0.2341 |
| K = 100 blocks | 0.6994 | 0.6382 | 0.5833 | 0.4912 | 0.3854 | 0.3055 |

No arm diverges from the primary in cell; zero #73 flags.

## Registered leans

- **Primary lean — DRIFT_WITH_CORE with floor share in [0.6, 0.9]: the CELL held, the MAGNITUDE did not.** Realized floor share 0.5348 [0.4203, 0.6320] — MISSED (below the lean's bottom). The core survives, but it keeps 53.5% of the near-gap excess rather than the 60-90% the planner leaned on; the interval's top edge (0.6320) only grazes the lean's bottom. Recorded as a prediction miss in the OVERCLAIM direction — the signature moves more than the T-line's early/late AUC and the S-line's split-half implied.
- **Secondary lean — decay concentrated in the low-activity tercile: HELD (largest decay in the low-activity tercile).** Decay by activity tercile: activity tercile 1 D = 0.4256 (floor 0.3982); activity tercile 2 D = 0.3871 (floor 0.4455); activity tercile 3 D = 0.3021 (floor 0.5368). The gradient is monotone in activity: thin signatures both start higher and fall further.

## 3y+ descriptive extension

E(3y+) = 0.2638 [0.1869, 0.3339] over 100,150 self pairs from 332 authors (mean gap 1234.7 d). **Descriptive only — never a verdict endpoint (#74).** The support is thin and composition-shifted: only the corpus's longest-lived authors can contribute a pair at this span.

## Exponential refinement (never verdict-carrying)

Fit of E(Δt) = E_inf + A·exp(−Δt/τ) on the 5 verdict bins at their realized mean gaps (42.8, 133.5, 266.4, 518.3, 874.1 days): E_inf = 0.1310 [-1.0224, 0.3558], A = 0.5439 [0.3130, 1.7268], τ = 976.3 d [415.6, 3650.0] (2.67 y). τ cap 3650 d; cap hit on the point fit: no; cap-hit share across bootstrap replicates 0.115. Residual SSE 0.00012439.

**The fit does NOT carry the verdict, and on this curve it could not have.** Three parameters on five points is weakly identified: the E_inf interval [-1.0224, 0.3558] runs negative at its bottom — an unphysical value for a floor — and 11.5% of bootstrap replicates push tau to the 3650-day cap, i.e. prefer a straight line to a decay-with-floor over this window. The floor the VERDICT rests on is the measured E(2-3y) and its own interval, not this E_inf. Read tau as an order of magnitude (years, not months), nothing finer.

## Reliability descriptive

Adjacent-block same-author cosine (consecutive disjoint K = 50 blocks, the shortest personal gap the design can see): mean 0.7703 over 44,882 pairs from 849 authors; median 0.8090, mean gap 17.4 d. Attenuation is constant across bins by the fixed-K construction, so E is an attenuated LEVEL and only D and the floor share are transportable. Adjacent blocks are the empirical ceiling this estimator can reach at K = 50.

## Census reproduction (blocking gate)

| quantity | registered | reproduced | status |
|---|---|---|---|
| authors_ge_4_blocks | 849 | 849 | PASS |
| authors_ge_2_blocks | 1028 | 1028 | PASS |
| authors_ge_8_blocks | 690 | 690 | PASS |
| total_blocks_all_authors | 46318 | 46318 | PASS |
| n_quarters | 18 | 18 | PASS |
| self_pairs_per_bin | [1005742, 783654, 1198561, 1248992, 417963, 100150] | [1005742, 783654, 1198561, 1248992, 417963, 100150] | PASS |
| authors_2_3y | 564 | 564 | PASS |
| authors_3y_plus | 332 | 332 | PASS |
| tercile_sizes | [302, 265, 282] | [302, 265, 282] | PASS |
| tercile_edges_vocab_events | [650, 2050] | [650, 2050] | PASS |

Cache anchors: events = 3,005,360, authors = 1,401, vocabulary = 1,191 — gate PASS.

## Honesty checks

| check | result |
|---|---|
| cache anchor gate (3,005,360 events / 1401 authors / 1191 vocabulary) | PASS |
| census reproduction (all registered pins) | PASS |
| permutation-null center abs(E) <= 0.002 in every bin | PASS |
| permutation-null center for D | -0.000019 |
| 3y+ excluded from the verdict (#74) | PASS |
| no synthetic gate required (registered: R layer, no world simulated) | N/A |
| cross-sampler equivalence (max abs(sampled − exact)) | 0.000048 |
| ID-leak scan (0 of 1401 cohort IDs in committed files) | PASS |

**Cross-baseline estimator equivalence (disclosed re-posing RD-U2-1).** The registration specifies the epoch-matched cross term as a sample of up to 20 different-author pairs per self pair per cell. This run computes the cell's cross mean EXACTLY (over all its different-author pairs) and weights cells by the same self-pair histogram — the zero-variance limit of the registered sampler, identical in estimand because the censused feasibility (min 26.0× here) makes 20 × self < available in every stratum. The registered sampler was ALSO run on the primary arm as a check: 95094317.0000 cross pairs drawn, per-bin |sampled − exact| max 0.000048.

## Boundaries

- This is ONE slow-time projection of K_u (eq 12) onto the marginal selection distribution over 1191 communities. A flat curve would mean drift is undetected in THIS projection at THIS span and power — never that the process has no dynamics; a decaying one is a statement about π_u on the Hellinger unigram sphere, not about any psychological attribute (§5.4).
- E is an ATTENUATED level: reliability at K = 50 is bounded by the adjacent-block similarity (0.7703), so only D and the floor share are transportable across block sizes; the K = 100 arm is the check that they are.
- THE CURVE HAS NOT FLATTENED BY THE VERDICT ENDPOINT. E(3y+) = 0.2638 sits below E(2-3y) = 0.3515, and the refinement fit's asymptote — weakly identified, see that section — sits below both. `DRIFT_WITH_CORE` is therefore a statement at a THREE-YEAR horizon: the core is what survives three years, not a demonstrated permanent floor. Extrapolating the floor past the observed span is not licensed by this leg.
- The verdict endpoint is 2-3y because that is the last bin with deep support (564 contributing authors, convention #74). The 3y+ bin is reported and never used for a verdict: its 332 authors are a survivorship-selected subpopulation.
- Epoch matching absorbs shared platform drift by construction, so E measures PERSONAL persistence in excess of the epoch. It cannot separate a personal taste change from a personal change of which communities exist for that person; both read as decay.
- Blocks are event-counted, not time-counted: a 50-event block spans days for a heavy user and months for a light one. The activity terciles are the sensitivity that makes that visible; the bins are calendar gaps between block MIDPOINTS.
- The cluster bootstrap resamples authors, so the CIs carry author-level sampling error. They do not carry error in the cross baseline, which is held at its full-arm value (recorded in the configuration block).
- Label-free and corpus-level throughout: no Big5 or MBTI value is read anywhere in this leg, and no per-author quantity is reported or committed.

## Configuration

```json
{
  "b_boot": 1000,
  "b_perm": 499,
  "bin_edges_days": [
    0.0,
    90.0,
    180.0,
    365.0,
    730.0,
    1095.0
  ],
  "bin_interval_convention": "left-closed, right-open on |\u0394t| in days",
  "bin_labels": [
    "0-90d",
    "90-180d",
    "180-365d",
    "1-2y",
    "2-3y",
    "3y+"
  ],
  "cache": "/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/results/m4_u1_order_identity/events_cache.npz",
  "cross_per_self_registered": 20,
  "descriptive_bin": "3y+",
  "epoch_origin": "corpus minimum created_utc over all cached cohort events",
  "epoch_origin_utc": "2014-12-31T23:54:39Z",
  "equivalence_fraction": 0.2,
  "floor_share_lean": [
    0.6,
    0.9
  ],
  "k_primary": 50,
  "k_sensitivity": 100,
  "pool_min_blocks": 4,
  "quarter_days": 91.3,
  "recorded_choices": {
    "bootstrap_cross_baseline": "cell cross means held at their full-arm values inside the cluster bootstrap; only the self side and the epoch-matching weights are resampled (the cross mean is estimated from ~10^9 pairs and carries negligible variance beside the author-clustered self side)",
    "cell_definition": "unordered quarter pair (min, max)",
    "clean_arm_rule": "explicit-typology communities dropped from the vocabulary, their events become OOV, blocks and pool recomputed",
    "cross_baseline_estimator": "EXACT cell-conditional cross mean over all different-author pairs of the (quarter-pair, bin) stratum, weighted by the self-pair histogram \u2014 the zero-variance limit of the registered up-to-20-per-self-pair sampler; the registered sampler is run on the primary arm as an equivalence check (disclosed re-posing RD-U2-1)",
    "empty_stratum_rule": "a (cell, bin) stratum with self pairs but no different-author pair is dropped from both terms and the weights are renormalized; the dropped self-pair mass is reported",
    "fit_abscissa": "mean self-pair gap within the bin (days), from artifacts",
    "fit_solver": "log grid of 1500 tau values in [1, 3650.0] days with the linear least-squares solution for (E_inf, A) at each",
    "k100_pool_rule": ">= 4 blocks recomputed at K = 100 (the same pool rule, not the K = 50 pool)",
    "permutation_scaffold": "within-quarter block->author relabelling implemented as a fixed slot->author map (an exact permutation invariant) with a permuted slot->block-position map; row 0 is the identity",
    "tercile_rule": "quantiles (0.3333333333333333, 0.6666666666666666) of per-author BLOCK counts, assignment x <= lo | lo < x <= hi | x > hi; edges reported in vocabulary events as blocks x K"
  },
  "registration_commit": "b864dc7",
  "script_sha256": "09dda64dffeaaa5e38f7a0008540474bf25fb1ddef9b927cde0dd568d8572ef3",
  "seed": 20260818,
  "tau_cap_days": 3650.0,
  "verdict_bins": 5,
  "verdict_endpoint_bin": "2-3y"
}
```

Artifacts (gitignored): `results/m4_u2_persistence_curve/` — `config.json`, `config.sha256.json`, `census.json`, `anchors.json`, `arms.json`, `curve.json`, `verdict.json`, `fit.json`, `reliability.json`, `cross_sampler_check.json`, `id_leak_scan.json`, `report_payload.json`, `run_log.jsonl`.

