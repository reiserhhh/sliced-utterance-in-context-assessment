# SUICA M4-X1 — the venue response of expression volume

Run 2026-08-19T04:25:55.591911Z · registration `docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md` (commit 0bdb638) · seed 20260819 · B_perm 499 · B_boot 1000.

**VERDICT — A1_STOP__SYNTHETIC_GATE_FAILED.**

Part 0 failed on both of its clauses — recovery and null-world honesty — so the A1 stop fired BEFORE any real estimand was computed. No corpus value of R, of the variance budget or of the headroom distribution appears anywhere in this leg. On the primary arm's own realized design the registered interaction estimator returns 0.0613 for a planted 0.0200 (tolerance 0.0100), and in a world with NO interaction planted it returns 0.0482 with a bootstrap CI [0.0566, 0.0738] that excludes 0 and R = 0.4524 against a band [0.2184, 0.2439]. The artifact is three times the effect the leg was registered to detect.

## Gates

| gate | status |
|---|---|
| Census anchors (#78: every registered predicate exact) | **PASS** |
| Part 0 synthetic recovery gate (#76; A1 stop on failure) | **FAIL** |
| ID-leak scan (0 NEW hits of 10,296 author names over the committed files; 3 pre-existing dictionary collisions carried unchanged from HEAD) | **PASS** |

## Census — the registered predicates, re-executed (#78)

| quantity (exact predicate) | registered | observed | status |
|---|---|---|---|
| rows parseable (author+subreddit+created_utc+wcq) | 17,640,062 | 17,640,062 | PASS |
| wcq = 0 share (4 dp) | 0.0000 | 0.0000 | PASS |
| authors | 10,296 | 10,296 | PASS |
| Big5 cohort authors seen | 1,401 | 1,401 | PASS |
| disjoint authors | 8,895 | 8,895 | PASS |
| pool, disjoint, n=10/k=3 (PRIMARY) | 4,342 | 4,342 | PASS |
| pool, disjoint, n=5/k=3 | 5,842 | 5,842 | PASS |
| pool, Big5, n=10/k=3 | 615 | 615 | PASS |
| law vocabulary floor (users) | 89 | 89 | PASS |
| law vocabulary (communities) | 1,443 | 1,443 | PASS |

Non-gating cross-checks (published by the registration or inherited from the W/U lines). These do not route and did not gate: the ten pins above are what #78 blocks on, and the three pool counts are the sharp test of the eligibility predicate.

| cross-check | expected | observed | agrees |
|---|---|---|---|
| disjoint events (W1 cache size) | 14,634,702 | 14,634,702 | yes |
| Big5 events (U2 ANCHOR_EVENTS) | 3,005,360 | 3,005,360 | yes |
| within-cell sd of y (median, n=5 early cells) | 0.9070 | 0.9035 | NO |
| median shared eligible communities (n=5, disjoint; authors with >= 1 shared pair / eligible authors) | 4 | 5.0 / 7.0 | NO |
| median shared eligible communities (n=5, Big5; authors with >= 1 shared pair / eligible authors) | 3 | 4.0 / 8.0 | NO |

## Part 0 — the synthetic recovery gate (#76; A1 stop on failure)

The estimator is required to recover planted variance shares on a synthetic two-way world built at the PRIMARY ARM'S REALIZED DESIGN DENSITY — the real skeleton (which authors, which communities per author, how many comments per cell) carrying entirely synthetic y — and is required NOT to detect an interaction where none was planted. No real y enters Part 0.

Tolerance rule: max(0.01, 3.0 x replicate sd) over 8 replicates. The floor of 0.01 of total variance is half the width of the registration's own RESPONSE_TRACE / IDIOSYNCRATIC_RESPONSE boundary at 0.02: a bias larger than that re-routes the cell, so it is the loosest tolerance the verdict can survive.

| planted share | planted | recovered (mean of 8) | replicate sd | tolerance | bias | status |
|---|---|---|---|---|---|---|
| author | 0.3000 | 0.3261 | 0.0072 | 0.0217 | 0.0261 | FAIL |
| community | 0.0800 | 0.1351 | 0.0089 | 0.0268 | 0.0551 | FAIL |
| interaction | 0.0200 | 0.0613 | 0.0019 | 0.0100 | 0.0413 | FAIL |

| null-world honesty check (nothing planted in the interaction) | value |
|---|---|
| interaction share (planted 0.0000) | 0.0482 |
| cluster-bootstrap CI | [0.0566, 0.0738] |
| CI covers 0 (the registered routing clause) | **NO** |
| CI covers its own point estimate | **NO** |
| permutation band for the share | [0.0423, 0.0440] |
| share inside its own permutation band | **NO** |
| R | 0.4524 |
| permutation band for R | [0.2184, 0.2439] |
| R inside band | **NO** |
| author main recovered (planted 0.3000) | 0.3217 |
| community main recovered (planted 0.0800) | 0.1225 |
| honesty status | **FAIL** |

### What Part 0 localizes

- **The design is sparse.** 4,342 authors x 5,369 communities give 42,141 occupied (author, community) slots — a fill of 0.001808. The median author holds 6.0 shared communities and the median community holds 2.0 eligible authors; 0.0577 of slots sit in a community with exactly one eligible author.
- **Double-centering on an incomplete grid does not remove the mains.** With ONLY an author main planted (0.3000, nothing else) the interaction share reads 0.0383; with ONLY a community main planted (0.0800, nothing else) it reads 0.0078. Both leaks are cross-half PERSISTENT by construction — a main effect is the same in both halves — so the cross-half covariance trick, which is attenuation-free for noise, is defenceless against them.
- **The null world is detected.** With the interaction planted at exactly 0.0000 the estimator returns 0.0458 (8 replicates) and, on the scored replicate, a bootstrap CI [0.0566, 0.0738] that excludes 0, with R = 0.4524 against a band [0.2184, 0.2439]. The planted world reads 0.0613 for a planted 0.0200: the signal and the artifact are the same size.
- **The mechanism-coordinate null is anti-conservative here.** The permutation band for the share, [0.0423, 0.0440], sits below the null-world value 0.0482: permuting community labels within (author, half) moves the community MAIN along with the interaction, injecting within-author variance the real data does not carry, so the band under-states the artifact instead of absorbing it.
- **The cluster bootstrap is not centred on its own estimate.** In the null world the CI is [0.0566, 0.0738] around a point estimate of 0.0482 (does NOT cover it): resampling authors with replacement makes the grid MORE incomplete (about 63% of authors distinct per replicate), and the leak grows with incompleteness. A zero-reference CI clause cannot route a statistic whose zero moves with the resample.

| synthetic world | planted interaction | recovered interaction (mean ± sd) | recovered author | recovered community | R |
|---|---|---|---|---|---|
| planted | 0.0200 | 0.0613 ± 0.0019 | 0.3261 | 0.1351 | 0.6320 |
| null | 0.0000 | 0.0458 ± 0.0014 | 0.3214 | 0.1389 | 0.4464 |
| author_only | 0.0000 | 0.0383 ± 0.0012 | 0.2979 | 0.0572 | 0.4244 |
| community_only | 0.0000 | 0.0078 ± 0.0008 | 0.0207 | 0.0761 | 0.0006 |

Part 0 status: **FAIL** (recovery FAIL, honesty FAIL).

### Headroom (#84) on the Part 0 worlds — SYNTHETIC, not a corpus reading

The registration's headroom claim is that within-cell noise bounds every per-author correlation away from 1, so the estimator cannot saturate. On the planted world, at the primary arm's own design and cell sizes, the realized distribution is:

| quantile | per-author correlation (planted world) |
|---|---|
| q00 | -1.0000 |
| q05 | -0.2540 |
| q10 | 0.1504 |
| q25 | 0.5167 |
| q50 | 0.7411 |
| q75 | 0.8884 |
| q90 | 0.9682 |
| q95 | 0.9886 |
| q100 | 1.0000 |

4,340 authors scored, 2 undefined (a flat profile in one half); mean 0.6264, sd 0.3906; 0.0470 above 0.99, with both extreme quantiles rounding to 1.0000 and -1.0000 at four decimals.

Two things follow, and neither is what the registration expected. First, the per-author statistic is NOT bounded away from 1: at k_min = 3 shared communities a Pearson correlation over three points reaches the ceiling whenever the three points happen to line up, so 'headroom exists by construction' holds for the MEAN over thousands of authors, not for the per-author correlation the sentence is about. Second, the ceiling was never the binding problem: in the NULL world, where nothing was planted, 0.0362 of authors still sit above 0.99 and the mean is 0.4524. It is the FLOOR that Part 0 falsified.

## No real arm was run

Part 0 did not pass, so the A1 stop fired BEFORE any real estimand was computed. No corpus value of R, of the variance budget or of the headroom distribution exists in this leg's artifacts, and none is reported here. The census above is design arithmetic that the registration had already published; it is not an estimand.

The registered cells and leans are therefore UNSCORED. NO_REPRODUCIBLE_RESPONSE is not the outcome either: the leg reached no reading of the crossing at all, in either direction.

| registered object | value | outcome |
|---|---|---|
| cell 1 NO_REPRODUCIBLE_RESPONSE | R inside band AND interaction share CI includes 0 | UNSCORED |
| cell 2 RESPONSE_TRACE | detected, share < 0.02 | UNSCORED |
| cell 3 IDIOSYNCRATIC_RESPONSE | share in [0.02, 0.1] | UNSCORED |
| cell 4 RESPONSE_MAJOR | share > 0.1 | UNSCORED |
| lean: R | (0.05, 0.3] | UNSCORED |
| lean: interaction share | (0.005, 0.05] | UNSCORED |
| lean: author main | [0.15, 0.45] | UNSCORED |
| lean: community main | [0.02, 0.15] | UNSCORED |
| lean: Big5 replication in the primary cell | same cell | UNSCORED (no cell was reached, so no #73 flag exists) |

### The arm designs that were built and not scored

| arm | eligible authors | communities | slots | comments | median shared communities | median eligible authors per community | singleton-community slot share |
|---|---|---|---|---|---|---|---|
| primary | 4,342 | 5,369 | 42,141 | 8,974,599 | 6.0 | 2.0 | 0.0577 |
| sens_n5 | 5,842 | 7,450 | 73,421 | 10,144,456 | 7.0 | 2.0 | 0.0437 |
| replication_big5 | 615 | 1,973 | 6,240 | 2,011,642 | 6.0 | 1.0 | 0.1910 |
| sens_lawvocab | 3,694 | 1,338 | 32,714 | 6,904,131 | 6.0 | 9.0 | 0.0032 |
| sens_word_count | 4,342 | 5,369 | 42,141 | 8,974,599 | 6.0 | 2.0 | 0.0577 |

Design counts only — no y was read into any estimand. They are reported because the leak Part 0 measured scales with exactly these numbers.

### Defect candidates recorded for the planner

Executor candidates, not registered content, and nothing below was run:

- **The antecedent verification (#84) checked the wrong antecedent.** The registration verified that the per-author correlation has HEADROOM (it cannot saturate) and that the null lives in the mechanism's own coordinate, and it asserted that 'the estimand needs no cross-author support floor'. It never asked whether the estimator's ZERO is zero on the realized design. It is not: with nothing planted the interaction share reads 0.0482 and R reads 0.4524.
- **The routing statistic is zero-referenced but its zero moves.** Cell 1 asks whether the interaction share's CI includes 0. That presumes 0 is the no-response value; on an incomplete grid the no-response value is the leak, and the cluster bootstrap tracks the leak rather than the estimand (in the null world the CI is [0.0566, 0.0738] around a point of 0.0482). A band-referenced or design-calibrated contrast — not a zero-referenced CI — is what this family of estimands needs.
- **The permutation null is not a clean mechanism coordinate for this estimand.** Permuting community labels within (author, half) moves the community MAIN together with the interaction, so the band ([0.0423, 0.0440]) sits below the artifact it is supposed to calibrate (0.0482). A null that resamples the interaction while HOLDING both mains fixed would be the matching coordinate.
- **The headroom clause is stated about the wrong object.** The registration argues that within-cell noise 'bounds every per-author correlation away from 1'. On the planted world at the primary design, 0.0470 of authors read above 0.99 and the extremes round to +-1.0000: with k_min = 3 the per-author correlation has no such bound. What is bounded is the MEAN over thousands of authors. The clause should be restated about the estimand, not about its summands.
- **The leak is carried by the AUTHOR main through thin communities, and it is a support problem after all.** With only an author main planted the interaction share reads 0.0383 and R reads 0.4244; with only a community main planted they read 0.0078 and 0.0006. The primary design has a median of 2.0 eligible authors per community and 0.0577 of slots in single-author communities; the law-vocabulary arm the registration demoted to a sensitivity has 9.0 and 0.0032. A cross-author support floor is a candidate PRIMARY, not a sensitivity — the opposite of what the registration reasoned.

## Boundaries

- **Metadata only, expression VOLUME and not content (permanent).** The only text-derived quantity in this leg is `word_count_quoteless`, the author's own-word count per comment. No body was read, no topic, no style, no sentiment. Every claim here is about HOW MUCH is written in a venue, never about WHAT is written.
- **The response-operator projection caution.** Profile persistence is ONE static projection of crossing #2's condition-response operator R_v. A null is a statement about this projection at this resolution, not about the operator; a detection is a lower bound on it.
- **No psychological naming.** Verbosity is a technical expression-volume object. Nothing here is a trait, a state, a disposition or a preference, and the leg is label-free: `author_profiles.csv` was never opened.
- **EXPLORATORY, corpus-level.** No person-level claim is licensed. The per-author correlations exist only as the population of a mean.
- **Cohort composition.** The disjoint cohort is TYPOLOGY-ENRICHED by construction (PANDORA's non-Big5 authors are MBTI-labelled users), so it is a platform sample with a selection, not a population sample.
- **Incomplete design.** The eligible grid is sparse: most authors occupy a handful of communities and most communities carry few eligible authors. Double-centering on an incomplete grid does not separate mains from the interaction exactly — that is why Part 0 is a gate and not a formality.

## Configuration

```json
{
  "author_profiles_opened": false,
  "b_boot": 1000,
  "b_perm": 499,
  "bodies_read": false,
  "bootstrap_semantics": "R resamples per-author correlations; the budget recomputes every component, including the double-centering, from the resampled author multiset",
  "cells": {
    "idiosyncratic_max": 0.1,
    "trace_max": 0.02
  },
  "chunk_size": 2000000,
  "columns_read": [
    "author",
    "subreddit",
    "created_utc",
    "word_count_quoteless",
    "word_count"
  ],
  "halves": "author's FULL-STREAM median created_utc, <= to early",
  "k_min": 3,
  "leg": "M4-X1",
  "min_cell_keep": 5,
  "n_min_primary": 10,
  "n_min_sensitivity": 5,
  "null_shares": {
    "author": 0.3,
    "community": 0.08,
    "interaction": 0.0
  },
  "planted_shares": {
    "author": 0.3,
    "community": 0.08,
    "interaction": 0.02
  },
  "registration": "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md@0bdb638",
  "run_utc": "2026-08-19T04:25:55.591911Z",
  "seed": 20260819,
  "seed_boot": 20260822,
  "seed_part0": 20260820,
  "seed_perm": 20260821,
  "synthetic_replicates": 8,
  "title": "the venue response of expression volume",
  "tolerance_floor": 0.01,
  "tolerance_sd_multiple": 3.0,
  "var_y_denominator": "comment-level population variance of y over the analysis pool = the comments inside eligible cells",
  "y": "log(1 + word_count_quoteless)",
  "y_sensitivity": "log(1 + word_count)"
}
```

