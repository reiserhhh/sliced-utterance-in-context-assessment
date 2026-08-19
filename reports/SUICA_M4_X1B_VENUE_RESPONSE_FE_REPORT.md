# SUICA M4-X1b — the venue response, repaired design and exact estimator

Run 2026-08-19T05:07:59.684924Z · registration `docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md` (X1b, commit 0f8e43e) · seed 20260819 · B_perm 499 · B_boot 1000 · runtime 44.7 s.

**VERDICT — A1_STOP__SYNTHETIC_GATE_FAILED.**

Part 0 passed 8 of its 9 clauses and failed 1 (“recovery — author main within max(0.01, 3 x replicate sd)”), so the A1 stop fired BEFORE any real estimand was computed. No corpus value of R, of the variance budget or of the headroom distribution appears anywhere in this leg. The REGISTERED REPAIR itself succeeded completely: on the identical null world the exact two-way FE reads -0.0000 for the interaction share where X1's double-centering reads 0.0183, with a cluster-bootstrap CI [-0.0003, 0.0002] that covers 0 and R = 0.0078 inside its permutation band [-0.0166, 0.0166]. What fails is the object the registration explicitly did NOT repair: the author main share, estimated PRE-FE from the cross-half covariance of author half-means, recovers 0.3220 for a planted 0.3000 against a tolerance of 0.0179.

## Gates

| gate | status |
|---|---|
| Inherited census anchors (#78: X1's ten pins, six re-checkable from the cache) | **PASS** |
| Predicate-chain census (#78: the planner's s = 3/5/8 table exact, 0 singleton communities and LCC 1.000 at s = 5) | **PASS** |
| LCC assertion (the alternating projection is exact only on a connected design; coverage must be 1.000) | **PASS** |
| Big5 replication #69 floor (300 authors, IN-LEG census; below it the arm is underpowered-descriptive, not #73) | **PASS** |
| Part 0 — the gate that had to pass (#76/#85; A1 stop on any failing clause) | **FAIL** |
| ID-leak scan (0 NEW hits of 10,296 author names over the committed files; 4 pre-existing dictionary collisions carried unchanged from HEAD) | **PASS** |

## Anchors — the inherited census (#78, BLOCKING)

| quantity (exact predicate) | registered | observed | status |
|---|---|---|---|
| rows parseable (author+subreddit+created_utc+wcq) | 17,640,062 | 17,640,062 | PASS |
| authors | 10,296 | 10,296 | PASS |
| Big5 cohort authors seen | 1,401 | 1,401 | PASS |
| disjoint authors | 8,895 | 8,895 | PASS |
| law vocabulary floor (users) | 89 | 89 | PASS |
| law vocabulary (communities) | 1,443 | 1,443 | PASS |

Everything above is read from X1's committed cell cache, whose 17,640,062-row single pass is the only time the comments file was touched in this line. No text body, no label file.

## The predicate chain — reproduced from the planner's census (#78, BLOCKING)

The chain runs ONCE in the pinned order, with no fixed-point iteration: (1) cells at n ≥ 10 comments, disjoint authors, law communities; (2) shared pairs, both halves eligible; (3) the community support floor of s authors holding a shared pair; (4) authors with ≥ 3 surviving shared communities; (5) the largest connected component.

| s | authors | communities | shared pairs | fill | median authors per community | singleton communities | LCC author coverage |
|---|---|---|---|---|---|---|---|
| 3 | 3,686 | 1,145 | 32,415 | 0.0077 | 11.0 | 1 (0.0009) | 1.000 |
| 5 (PRIMARY) | 3,665 | 1,000 | 31,899 | 0.0087 | 12.5 | 0 (0.0000) | 1.000 |
| 8 | 3,595 | 780 | 30,561 | 0.0109 | 16.0 | 0 (0.0000) | 1.000 |

| s | registered authors | registered communities | registered shared pairs | all three exact |
|---|---|---|---|---|
| 3 | 3,686 | 1,145 | 32,415 | PASS |
| 5 | 3,665 | 1,000 | 31,899 | PASS |
| 8 | 3,595 | 780 | 30,561 | PASS |

Attrition through the chain at the primary floor (s = 5): 140,026 eligible cells → 37,414 shared pairs → 36,612 after the support floor → 31,899 after the k ≥ 3 author floor → 31,899 in the largest connected component. The graph was already connected before step 5 (1 component(s), author coverage 1.000), which is what makes the alternating projection's exactness argument valid here.

Non-gating cross-checks that the planner's census table also publishes:

| cross-check | published | observed | agrees |
|---|---|---|---|
| s = 3: fill | 0.0077 | 0.0077 | yes |
| s = 3: authors_per_community_median | 11.0 | 11.0 | yes |
| s = 3: singleton_community_share | 0.0009 | 0.0009 | yes |
| s = 5: fill | 0.0087 | 0.0087 | yes |
| s = 5: authors_per_community_median | 12.5 | 12.5 | yes |
| s = 5: singleton_community_share | 0.0 | 0.0 | yes |
| s = 8: fill | 0.0109 | 0.0109 | yes |
| s = 8: authors_per_community_median | 16.0 | 16.0 | yes |
| s = 8: singleton_community_share | 0.0 | 0.0 | yes |

## Part 0 — the gate that had to pass (#76/#85; A1 stop on failure)

The battery is the one that stopped X1, re-run on the X1b skeleton: the real incidence carries WHOLLY SYNTHETIC y, and no real y enters Part 0 at any point. Every clause below had to pass before a single corpus number could be computed.

Tolerance rule: max(0.01, 3.0 x replicate sd) over 8 replicates. The floor of 0.01 of total variance is half the width of the registration's own RESPONSE_TRACE / IDIOSYNCRATIC_RESPONSE boundary at 0.02.

| # | clause | status |
|---|---|---|
| 1 | recovery — author main within max(0.01, 3 x replicate sd) | **FAIL** |
| 2 | recovery — community main within max(0.01, 3 x replicate sd) | PASS |
| 3 | recovery — interaction within max(0.01, 3 x replicate sd) | PASS |
| 4 | null world — interaction share CI covers 0 | PASS |
| 5 | null world — interaction point inside its permutation band | PASS |
| 6 | null world — R inside its permutation band | PASS |
| 7 | ablation — author-only leakage < 0.005 on the interaction share | PASS |
| 8 | ablation — community-only leakage < 0.005 on the interaction share | PASS |
| 9 | #85b bootstrap-zero — the null world's cluster-bootstrap CI covers 0 | PASS |

Part 0 status: **FAIL** (8 of 9 clauses pass).

### Recovery on the planted world

| planted share | planted | recovered (mean of 8) | replicate sd | tolerance | bias | status |
|---|---|---|---|---|---|---|
| author | 0.3000 | 0.3220 | 0.0060 | 0.0179 | 0.0220 | FAIL |
| community | 0.0800 | 0.1072 | 0.0141 | 0.0424 | 0.0272 | PASS |
| interaction | 0.0200 | 0.0170 | 0.0005 | 0.0100 | -0.0030 | PASS |

### The null world, scored with the full pipeline

| null-world clause (nothing planted in the interaction) | value |
|---|---|
| interaction share (planted 0.0000) | -0.0001 |
| cluster-bootstrap CI (FE recomputed in every replicate) | [-0.0003, 0.0002] |
| CI covers 0 (#85b, the bootstrap-zero clause) | yes |
| CI covers its own point estimate | yes |
| permutation band for the share | [-0.0011, 0.0010] |
| share inside its own permutation band | yes |
| R | 0.0078 |
| R cluster-bootstrap CI | [-0.0131, 0.0246] |
| permutation band for R | [-0.0166, 0.0166] |
| R inside band | yes |
| author main recovered (planted 0.3000) | 0.3223 |
| community main recovered (planted 0.0800) | 0.0967 |

### Every synthetic world, point-wise

| synthetic world | planted interaction | recovered interaction (mean ± sd) | recovered author | recovered community | R |
|---|---|---|---|---|---|
| planted | 0.0200 | 0.0170 ± 0.0005 | 0.3220 | 0.1072 | 0.4550 |
| null | 0.0000 | -0.0000 ± 0.0001 | 0.3220 | 0.1139 | 0.0000 |
| author_only | 0.0000 | -0.0001 ± 0.0002 | 0.3002 | 0.0263 | -0.0038 |
| community_only | 0.0000 | 0.0001 ± 0.0001 | 0.0225 | 0.0817 | 0.0032 |

| ablation clause | leakage on the interaction share | maximum | R leakage | status |
|---|---|---|---|---|
| author_only | 0.0001 | 0.0050 | -0.0038 | PASS |
| community_only | 0.0001 | 0.0050 | 0.0032 | PASS |

### The alternating projection, verified

| quantity | early half | late half |
|---|---|---|
| sweeps to convergence | 28 | 28 |
| final max absolute change | 4.993e-11 | 5.353e-11 |
| max abs residual AUTHOR mean | 3.547e-11 | 3.805e-11 |
| max abs residual COMMUNITY mean | 2.220e-17 | 2.726e-17 |

Both mains are removed to machine tolerance on the realized, incomplete grid — which is precisely what X1's single double-centering could not do.

## The repair, demonstrated: X1 versus X1b on the SAME null world

Every cell below is the NULL world — the interaction planted at exactly 0.0000 — drawn under the same seed on the named skeleton and scored by the named estimator, 8 replicates. A correct estimator reads 0.0000 in all of them.

| skeleton | estimator | authors × communities (slots) | interaction share (mean ± sd) | R (mean ± sd) |
|---|---|---|---|---|
| x1_registered_skeleton | x1_double_centering | 4,342 × 5,369 (42,141) | 0.0458 ± 0.0014 | 0.4464 ± 0.0112 |
| x1_registered_skeleton | x1b_exact_fe | 4,342 × 5,369 (42,141) | 0.0000 ± 0.0001 | 0.0017 ± 0.0111 |
| x1b_repaired_skeleton | x1_double_centering | 3,665 × 1,000 (31,899) | 0.0183 ± 0.0014 | 0.2436 ± 0.0167 |
| x1b_repaired_skeleton | x1b_exact_fe | 3,665 × 1,000 (31,899) | -0.0000 ± 0.0001 | 0.0000 ± 0.0057 |

On the single scored replicate of that null world, with the full inference machinery on both sides:

| quantity | X1 (double-centering) | X1b (exact FE) |
|---|---|---|
| interaction share (planted 0.0000) | 0.0176 | -0.0001 |
| cluster-bootstrap CI | [0.0241, 0.0286] | [-0.0003, 0.0002] |
| CI covers 0 | **NO** | yes |
| CI covers its own point | **NO** | yes |
| permutation band for the share | [0.0095, 0.0117] | [-0.0011, 0.0010] |
| R | 0.2442 | 0.0078 |
| permutation band for R | [0.0636, 0.0965] | [-0.0166, 0.0166] |

## Headroom (#84 as restated by #85) — SYNTHETIC, not a corpus reading

The clause is about the MEAN over thousands of authors, not about the per-author correlation: at k_min = 3 a Pearson correlation over three points reaches ±1 whenever three points happen to line up, so saturation in the per-author distribution is EXPECTED and is not a ceiling on the estimand. The realized distributions on the two Part 0 worlds are reported so the statement is a number and not an assertion.

| quantile | planted world | null world |
|---|---|---|
| q00 | -1.0000 | -1.0000 |
| q05 | -0.4981 | -0.8907 |
| q10 | -0.1577 | -0.7442 |
| q25 | 0.2709 | -0.3596 |
| q50 | 0.5659 | 0.0057 |
| q75 | 0.7878 | 0.3778 |
| q90 | 0.9344 | 0.7520 |
| q95 | 0.9796 | 0.9297 |
| q100 | 1.0000 | 1.0000 |

Planted world: 3,665 authors scored, 0 undefined; mean 0.4643, sd 0.4403; 0.0338 above 0.99. Null world: mean 0.0078, sd 0.5259; 0.0180 above 0.99, 0.5029 positive. The MEAN separates the two worlds cleanly (0.4643 against 0.0078) while the per-author tails do not — which is the whole content of the restatement.

## What Part 0 localizes

- **The estimator repair works, and it is the whole of the registered repair.** On the SAME null world — interaction planted at exactly 0.0000 — X1's double-centering reads 0.0183 and R = 0.2436, while the exact alternating-projection FE reads -0.0000 +- 0.0001 and R = 0.0000. The scored replicate's cluster-bootstrap CI is [-0.0003, 0.0002] — it covers 0 and it covers its own point estimate — against the old estimator's [0.0241, 0.0286] on the identical world.
- **The design repair alone would not have sufficed, and the estimator repair alone would have.** On X1's own registered skeleton the FE already reads 0.0000 where double-centering read 0.0458; moving to the support-conditioned skeleton without changing the estimator only takes double-centering from 0.0458 to 0.0183. Support conditioning is still worth having — it is what makes the mains estimable and the graph connected — but the leak was the projection, not the grid.
- **Both ablations are clean.** With ONLY an author main planted the interaction share reads 0.0001 (R = -0.0038); with ONLY a community main planted it reads 0.0001 (R = 0.0032). Both sit far below the 0.005 clause. The residue that X1 localized — a per-community term of the author main surviving the double centering — is removed exactly by the projection.
- **What still fails is the object the registration did NOT repair.** The author main share is estimated PRE-FE, from the cross-half covariance of author half-means, exactly as in X1. On the planted world it recovers 0.3220 for a planted 0.3000 — a bias of 0.0220 against a tolerance of 0.0179. The community main recovers 0.1072 for 0.0800, inside its (wider) tolerance of 0.0424.
- **The author-main bias is a COMPOSITION term, and it is predictable from the design alone.** An author's half-mean is not a_u: it is a_u plus that author's own average of the community main and of the interaction over the communities they occupy. That average is the SAME in both halves up to cell-size reweighting, so the cross-half covariance keeps it. The realized design has E[1/k_u] = 0.1909 over 3,665 authors, which predicts a bias of 0.0191 against the observed 0.0220. The support floor raised the authors per community from X1's 2.0 to 12.5 and thereby fixed the community main; it does not raise the communities per author, so it cannot fix the author main.

## No real arm was run

Part 0 did not pass, so the A1 stop fired BEFORE any real estimand was computed. No corpus value of R, of the variance budget or of the headroom distribution exists in this leg's artifacts, and none is reported here. The chain census above is design arithmetic that the registration had already published; it is not an estimand.

The registered cells and leans are therefore UNSCORED. `NO_REPRODUCIBLE_RESPONSE` is not the outcome either: the leg reached no reading of crossing #2 at all, in either direction.

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

### The four-share budget, per arm

| arm | author main | community main | interaction | residual | R [CI, band] | cell | #73 |
|---|---|---|---|---|---|---|---|
| PRIMARY — disjoint, law vocab, n=10, s=5, k=3, wcq | UNSCORED | UNSCORED | UNSCORED | UNSCORED | UNSCORED | UNSCORED | none (no cell exists) |
| sensitivity — support floor s=8 | UNSCORED | UNSCORED | UNSCORED | UNSCORED | UNSCORED | UNSCORED | none (no cell exists) |
| sensitivity — n_min=5 (same chain) | UNSCORED | UNSCORED | UNSCORED | UNSCORED | UNSCORED | UNSCORED | none (no cell exists) |
| sensitivity — y = log(1 + word_count) | UNSCORED | UNSCORED | UNSCORED | UNSCORED | UNSCORED | UNSCORED | none (no cell exists) |
| REPLICATION — Big5 cohort, identical chain | UNSCORED | UNSCORED | UNSCORED | UNSCORED | UNSCORED | UNSCORED | none (no cell exists) |

### The arm designs that were built and not scored

| arm | eligible authors | communities | shared pairs | comments | median shared communities | median authors per community | singleton communities | LCC coverage | #73 |
|---|---|---|---|---|---|---|---|---|---|
| PRIMARY — disjoint, law vocab, n=10, s=5, k=3, wcq | 3,665 | 1,000 | 31,899 | 6,811,576 | 5.0 | 12.5 | 0 | 1.000 | none (no cell exists) |
| sensitivity — support floor s=8 | 3,595 | 780 | 30,561 | 6,642,327 | 5.0 | 16.0 | 0 | 1.000 | none (no cell exists) |
| sensitivity — n_min=5 (same chain) | 5,094 | 1,243 | 56,460 | 7,885,024 | 7.0 | 18.0 | 0 | 1.000 | none (no cell exists) |
| sensitivity — y = log(1 + word_count) | 3,665 | 1,000 | 31,899 | 6,811,576 | 5.0 | 12.5 | 0 | 1.000 | none (no cell exists) |
| REPLICATION — Big5 cohort, identical chain | 408 | 240 | 3,261 | 1,206,370 | 5.0 | 7.0 | 4 | 1.000 | none (no cell exists) |

Design counts only — no y was read into any estimand. The Big5 replication arm carries 408 eligible authors under the identical chain, at or above the in-leg #69 floor of 300, so it would have carried a #73 comparison had a cell been reached.

### Defect candidates recorded for the planner

Executor candidates, not registered content, and nothing below was run:

- **The main-share estimators are MARGINAL, not main, and the gate is right to say so.** The cross-half covariance of author half-means estimates Var(a) PLUS the author's own composition average of everything else that is persistent — the community main and the interaction. Its target is therefore not the planted author share, and no amount of support conditioning moves it, because the contaminating divisor is the number of communities per AUTHOR (median 5.0, E[1/k_u] = 0.1909), not the number of authors per community. The obvious candidates are to estimate the mains from the SAME two-way projection that now carries the interaction (author and community effect variances read off the fitted effects with their sampling variance removed), or to re-state the registered clause so that the mains are scored against their own marginal targets rather than against the planted variance components. Neither was run here.
- **The registration repaired the routing statistic and left the co-reported ones under the same gate.** The cells route on the interaction share and R, and BOTH now behave exactly: the null world reads -0.0001 with a CI covering 0 and R = 0.0078 inside its band. The gate nevertheless fails, because the recovery clause covers all three planted shares. That is a defensible clause — a budget that over-reads its largest component is not a budget — but a planner may wish to separate ROUTING clauses from DESCRIPTIVE ones so that a descriptive bias downgrades a co-reported number instead of stopping the leg.
- **The interaction estimator is slightly CONSERVATIVE by construction, and the amount is computable.** The two-way projection removes A + C - 1 dimensions from M cells, so a planted interaction that is white across cells loses that fraction of itself: here 3,665 + 1,000 - 1 of 31,899, i.e. a retained fraction of 0.8538, which predicts 0.0171 for a planted 0.0200 against the observed 0.0170. A future registration can either correct for the projection's degrees of freedom or record the estimand as a LOWER bound. Nothing was corrected here.

## Boundaries

- **Metadata only, expression VOLUME and not content (permanent).** The only text-derived quantity in this leg is `word_count_quoteless`, the author's own-word count per comment. No body was read, no topic, no style, no sentiment. Every claim here would have been about HOW MUCH is written in a venue, never about WHAT is written.
- **The response-operator projection caution.** Profile persistence is ONE static projection of crossing #2's condition-response operator R_v. A null would be a statement about this projection at this resolution, not about the operator; a detection would be a lower bound on it.
- **No psychological naming.** Verbosity is a technical expression-volume object. Nothing here is a trait, a state, a disposition or a preference, and the leg is label-free: `author_profiles.csv` was never opened.
- **EXPLORATORY, corpus-level.** No person-level claim is licensed. The per-author correlations exist only as the population of a mean — which is the #85 restatement of the #84 headroom clause: the bounded object is the MEAN over thousands of authors, never the per-author correlation.
- **Cohort composition.** The disjoint cohort is TYPOLOGY-ENRICHED by construction (PANDORA's non-Big5 authors are MBTI-labelled users), so it is a platform sample with a selection, not a population sample.
- **The analysis universe is WELL-SHARED VENUES by construction (new in X1b).** The community universe is the law vocabulary (1,443 communities at floor 89) and the eligible grid carries a cross-author support floor of five authors per community. Whatever this design licenses, it licenses about venues that many cohort authors share — not about the long tail of small or private communities, which the chain removes by construction. The support conditioning is a PRIMARY design parameter (#85c), not a sensitivity.

## Configuration

```json
{
  "ablation_leak_max": 0.005,
  "ablation_worlds": {
    "author_only": {
      "author": 0.3,
      "community": 0.0,
      "interaction": 0.0
    },
    "community_only": {
      "author": 0.0,
      "community": 0.08,
      "interaction": 0.0
    }
  },
  "author_profiles_opened": false,
  "b_boot": 1000,
  "b_perm": 499,
  "big5_power_floor_69": 300,
  "bodies_read": false,
  "bootstrap_semantics": "cluster bootstrap over authors; the FE is RECOMPUTED inside every replicate (#85b), with author multiplicity as the projection weight",
  "cells": {
    "idiosyncratic_max": 0.1,
    "trace_max": 0.02
  },
  "columns_read": [
    "author",
    "subreddit",
    "created_utc",
    "word_count_quoteless",
    "word_count"
  ],
  "estimator": "two-way fixed effects per half by ALTERNATING PROJECTIONS on the eligible shared cells; v = the FE residual of the cell mean",
  "fe_tolerance": 1e-10,
  "halves": "author's FULL-STREAM median created_utc, <= to early",
  "k_min": 3,
  "leg": "M4-X1b",
  "mains_estimator": "cross-half covariances of author and community half-means, computed PRE-FE on the same pool (X1's definition, unchanged by the registration)",
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
  "predecessor": "M4-X1 (A1_STOP__SYNTHETIC_GATE_FAILED, commit ebe4f5b)",
  "predicate_chain": [
    "1. cells with n >= n_min comments, cohort authors, law vocabulary communities",
    "2. shared pairs: (author, community) with BOTH halves eligible",
    "3. community support floor: >= s authors holding a shared pair",
    "4. authors with >= k_min surviving shared communities",
    "5. largest connected component of the bipartite graph",
    "NO fixed-point iteration: the chain runs once, in this order"
  ],
  "registration": "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md@0f8e43e (X1b)",
  "run_utc": "2026-08-19T05:07:59.684924Z",
  "seed": 20260819,
  "seed_boot": 20260822,
  "seed_part0": 20260820,
  "seed_perm": 20260821,
  "support_censused": [
    3,
    5,
    8
  ],
  "support_primary": 5,
  "support_sensitivity": 8,
  "synthetic_replicates": 8,
  "title": "the venue response, repaired design and exact estimator",
  "tolerance_floor": 0.01,
  "tolerance_sd_multiple": 3.0,
  "var_y_denominator": "comment-level population variance of y over the analysis pool = the comments inside eligible cells",
  "vocabulary_floor_fraction": 0.01,
  "y": "log(1 + word_count_quoteless)",
  "y_sensitivity": "log(1 + word_count)"
}
```

