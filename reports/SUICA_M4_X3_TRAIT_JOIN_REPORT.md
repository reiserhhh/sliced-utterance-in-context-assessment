# SUICA M4-X3 -- the trait join of expression coordinates

**VERDICT: `EXPRESSION_TRAIT_SILENT` (cell 1).**  Tier EXPLORATORY, corpus-level, layer P.  Registered before the run in `docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md` at commit `8823b60`.

4 of 4 coordinates were admitted by the label-free reliability gate; 0 of them detect raw coupling to Big5 similarity at the registered two-sided band.

**Scoped statement (attached to the realized-band width table, and only there): silent beyond r ~ 0.019 on the coordinates admitted here, with the realized band widths below.**  No equivalence cell is claimed beyond this sentence, and the cohort caveat below rides it.

**The reading is not a dead harness.**  On the SAME pairs, with the SAME trait matrix and the SAME Mantel machinery, the Where channel is live: Mantel(bag-distance, trait-distance) ranges over 0.0449 to 0.0528 across the admitted coordinates' pools, against SR1's independently established 0.049 on a different pool of 1,306.  A within-harness point estimate, DESCRIPTIVE and routing nothing -- no null was run on it -- but it is the reading under which the expression rows' bands mean what they say.

## 1. The label event

The label event.  This leg opens the PANDORA Big5 columns of author_profiles.csv ONCE, under the stamp, for the Big5-cohort analysis pool -- the SR1/U3 class of re-join.  No per-author trait value is written to any committed file; only aggregate statistics leave stage E.

- source: `/Volumes/mobile3/projects/project persona/data_sets/PANDORA_official/author_profiles.csv`
- columns opened: `author`, `agreeableness`, `openness`, `conscientiousness`, `extraversion`, `neuroticism`
- opened: ONCE, in stage E, after `first_join` was logged at `2026-08-21T03:54:09.411707+00:00`
- analysis-pool label completeness: 1,116 of 1,116 (1.0000)
- z-scoring: the 1,116-author Big5 analysis pool (ONE z-scoring, reused by every coordinate row and by the per-trait secondary table)
- reader: inherited verbatim from U3.open_trait_table (#81 pin)
- committed artifacts carry AGGREGATES ONLY; no per-author trait value leaves stage E.

## 2. The stamp chain (G-X3)

| event | artifact | UTC |
|---|---|---|
| `config_stamped` | `config.sha256.json` | `2026-08-21T03:54:08.533578+00:00` |
| `coordinates_frozen` | `coordinate_freeze.json` | `2026-08-21T03:54:09.210158+00:00` |
| `first_join` | `join.json` | `2026-08-21T03:54:09.411707+00:00` |

Gaps: stamp -> freeze `0.7 s`, freeze -> first join `0.2 s`.  Order proven from the artifact timestamps: **yes**; joint quantities before the stamp: 0; labels opened before the stamp: no.  G-X3 PASS = **yes**.

| hash | stamped/frozen | recomputed | matches |
|---|---|---|---|
| `config.json` | `4da77d04c5cb188e` | `4da77d04c5cb188e` | yes |
| `coordinates.npz` | `26f159f06798e98d` | `26f159f06798e98d` | yes |

CONFIG-BEFORE-JOINT.  stage_part0 re-executes every inherited anchor, builds the four coordinates, runs the label-free reliability gate and the four value reproductions, and only then writes, hashes and stamps the config; it never opens a label column.  stage_stageb is label-free, re-executes the coordinates, asserts them bit-identical to the stamped reliabilities and freezes the coordinate table into the stamp chain.  The FIRST joint expression x trait quantity of the harness lives in stage_stagee, which logs a `first_join` event immediately before it.  G-X3 reads the artifacts and proves stamp < coordinate_freeze < first_join.

## 3. Anchors, source agreement and the value reproductions

| anchor | registered | observed | status |
|---|---|---|---|
| Big5 cohort authors seen | 1,401 | 1,401 | PASS |
| X2 pool, Big5 (the analysis pool) | 1,116 | 1,116 | PASS |
| X2 pool, disjoint | 8,008 | 8,008 | PASS |
| X5 R2 pool, Big5 | 1,100 | 1,100 | PASS |
| X5 R2 pool, disjoint | 7,989 | 7,989 | PASS |
| authors | 10,296 | 10,296 | PASS |
| candidate authors (>= 50 events per half) | 9,124 | 9,124 | PASS |
| disjoint authors | 8,895 | 8,895 | PASS |
| law vocabulary (communities) | 1,443 | 1,443 | PASS |
| law vocabulary floor (users) | 89 | 89 | PASS |
| rows parseable (author+subreddit+created_utc+wcq) | 17,640,062 | 17,640,062 | PASS |

Census status **PASS** (BLOCKING under #78).

| source-agreement check | result |
|---|---|
| x2 and x5 big5 masks identical | yes |
| x2 and x5 candidate pools identical | yes |
| x2 author names equal cell cache | yes |
| x5 author names equal cell cache | yes |

Agreement status **PASS**.  The rhythm channel comes from X5's cache, the bag channel from X2's and the chain from X1's; a coordinate table assembled across three caches is only meaningful if the author code space is literally the same object.

| reproduced value | committed | recomputed here | abs delta | status |
|---|---|---|---|---|
| X-Mb certified author main (disjoint s=5 skeleton) | 0.1285873991 | 0.1285873991 | 0.000000000000 | PASS |
| X-Mb disjoint chain census (s=5) | {"authors": 3665, "communities": 1000, "shared_pairs": 31899} | {"authors": 3665, "communities": 1000, "shared_pairs": 31899} | exact | PASS |
| X2 rhythm ownership rho_own (Big5 arm) | 0.6366996180 | 0.6366996180 | 0.000000000000 | PASS |
| X5 R2 mean floored slope (Big5 arm) | 0.0520327970 | 0.0520327970 | 0.000000000000 | PASS |
| X5 R2 slope ownership rho_own (Big5 arm) | 0.5380393024 | 0.5380393024 | 0.000000000000 | PASS |

Reproduction status **PASS** at tolerance 1e-09.  Every coordinate estimator is the committed object of the leg that certified it, called here on this pool; these four numbers are what makes that claim checkable.

## 4. The reliability gate (label-free, before the stamp)

| coordinate | n eligible | share of pool | split-half r | Spearman-Brown | expectation | gate |
|---|---|---|---|---|---|---|
| RAW LEVEL -- person-mean y | 1,116 | 1.000 | 0.8859 | 0.9395 | 0.900 | **ADMIT** |
| ADJUSTED LEVEL -- the X-Mb author-main a_hat_u | 408 | 0.366 | 0.9015 | 0.9482 | 0.900 | **ADMIT** |
| RHYTHM -- X2's r1_u | 1,116 | 1.000 | 0.6367 | 0.7780 | 0.637 | **ADMIT** |
| R2 SLOPE -- the floored gap x volume within-person slope | 1,100 | 0.986 | 0.5380 | 0.6996 | 0.538 | **ADMIT** |

Threshold 0.5.  X3's registered rule: failures are reported and excluded; the leg stops clean only if EVERY coordinate fails, and that stop happens before the stamp.

Stage B re-executed the coordinates from the same label-free sources and the split-half reliabilities came back BIT-IDENTICAL to the ones the stamp pinned (determinism **PASS**); the admitted set was unchanged (yes).

### The adjusted level's chain, censused label-free before the stamp

| support s | authors | communities | shared pairs | LCC author coverage | singleton communities |
|---|---|---|---|---|---|
| 3 | 446 | 431 | 3,889 | 1.000 | 13 |
| 5 (PRIMARY) | 408 | 240 | 3,261 | 1.000 | 4 |
| 8 | 351 | 133 | 2,659 | 1.000 | 0 |

The primary is s = 5, inherited from X-Mb's certified skeleton; the other two supports are the X1c census and route nothing.  The chain is the X1c predicate chain run on the BIG5 mask instead of the disjoint mask, at X-Mb's certified primary support s = 5; no pre-registered census exists for it, so it is censused here, label-free, and pinned into the stamped config before any label is opened.  On the Big5 chain the FE budget reads author main 0.1376, community main 0.0458, interaction 0.0177, residual 0.7989.

## 5. The per-coordinate table

| coordinate | N | pairs | raw Mantel r | band | p | bootstrap CI | partial (bag) | p | partial (bag+act) | detects raw |
|---|---|---|---|---|---|---|---|---|---|---|
| RAW LEVEL -- person-mean y | 1,116 | 622,170 | **0.0006** | [-0.0207, 0.0216] | 0.9480 | [-0.0199, 0.0241] | -0.0020 | 0.8660 | -0.0020 | **no** |
| ADJUSTED LEVEL -- the X-Mb author-main a_hat_u | 408 | 83,028 | **-0.0073** | [-0.0370, 0.0375] | 0.7060 | [-0.0467, 0.0285] | -0.0078 | 0.7000 | -0.0079 | **no** |
| RHYTHM -- X2's r1_u | 1,116 | 622,170 | **0.0023** | [-0.0200, 0.0242] | 0.8410 | [-0.0202, 0.0259] | 0.0008 | 0.9530 | 0.0002 | **no** |
| R2 SLOPE -- the floored gap x volume within-person slope | 1,100 | 604,450 | **-0.0172** | [-0.0293, 0.0238] | 0.1930 | [-0.0395, 0.0059] | -0.0189 | 0.1470 | -0.0197 | **no** |

Nulls: raw = permutation of the AUTHOR ROWS of the trait matrix, B = 999, two-sided at alpha = 0.05; partial = Smouse-Long-Sokal residual permutation on the bag channel, same B.  The bag control is LINEAR (#82 declared).  CIs are the author-cluster bootstrap on the Mantel r, B = 1000, self-pairs excluded.

| coordinate | Mantel(bag, trait) | corr(coord-dist, bag) | corr(coord-dist, activity) | disattenuated raw (secondary) |
|---|---|---|---|---|
| RAW LEVEL -- person-mean y | 0.0454 | 0.0567 | 0.0058 | 0.0007 |
| ADJUSTED LEVEL -- the X-Mb author-main a_hat_u | 0.0528 | 0.0088 | 0.0290 | -0.0084 |
| RHYTHM -- X2's r1_u | 0.0454 | 0.0341 | 0.0737 | 0.0029 |
| R2 SLOPE -- the floored gap x volume within-person slope | 0.0449 | 0.0373 | 0.0850 | -0.0230 |

Disattenuation is a SECONDARY READING ONLY (#57 family).  The coordinate reliabilities are MEASURED here; the label reliability 0.80 is DECLARED, so any disattenuated number illustrates scale and routes nothing.

Bag channel: the 1,443-community SR0-class law vocabulary; 7 pool authors have no in-vocabulary event.  An author with no in-vocabulary event carries the zero signature and therefore bag distance 1 to everyone; the count is reported, the rows are not dropped.

## 6. The level contrast

| row | N | raw Mantel r | band | p | bootstrap CI | detects |
|---|---|---|---|---|---|---|
| RAW LEVEL (own support) | 1,116 | **0.0006** | [-0.0207, 0.0216] | 0.9480 | [-0.0199, 0.0241] | no |
| ADJUSTED LEVEL | 408 | **-0.0073** | [-0.0370, 0.0375] | 0.7060 | [-0.0467, 0.0285] | no |
| RAW LEVEL on the adjusted support (second reading) | 408 | -0.0080 | [-0.0364, 0.0368] | 0.6590 | [-0.0455, 0.0326] | no |

The two rows stand on DIFFERENT supports (1,116 vs 408 authors): the chain's eligibility, not the adjustment, is most of that gap.  The descriptive retention ratio (-11.7637) is NOT read here: its denominator sits inside its own permutation band, so the ratio has no scale.  #79: no ratio null.  The level contrast is read as TWO detection decisions with TWO CIs, never as a null on r_adjusted / r_raw.  The retention ratio is printed as a descriptive and routes nothing.

The second reading is a DISCLOSED executor addition: DISCLOSED SECOND READING, routes nothing: the registered contrast compares two coordinates on two different supports, so this row separates the adjustment from the chain's eligibility loss.

## 7. The per-trait secondary table

| coordinate | AGRE | OPEN | CONS | EXTR | NEUR |
|---|---|---|---|---|---|
| RAW LEVEL -- person-mean y | 0.053 (p=0.075) | 0.086 (p=0.004) | 0.042 (p=0.165) | -0.019 (p=0.518) | -0.060 (p=0.044) |
| ADJUSTED LEVEL -- the X-Mb author-main a_hat_u | 0.141 (p=0.004) | 0.033 (p=0.511) | 0.048 (p=0.336) | 0.002 (p=0.963) | -0.030 (p=0.541) |
| RHYTHM -- X2's r1_u | 0.007 (p=0.821) | 0.057 (p=0.055) | -0.008 (p=0.779) | -0.002 (p=0.953) | -0.087 (p=0.003) |
| R2 SLOPE -- the floored gap x volume within-person slope | 0.048 (p=0.109) | 0.021 (p=0.491) | -0.041 (p=0.174) | -0.014 (p=0.652) | 0.003 (p=0.910) |

Pearson of the coordinate against each z-scored trait, over that coordinate's eligible label-complete authors; two-sided p by Fisher z, declared.  Guard: Bonferroni x (5 x 4), i.e. alpha = 0.00250; a cell that clears it is marked SURVIVES.  **This table routes nothing.**  0 of 20 cells survive.  The five largest |r| cells, survivors or not: adj_level x agreeableness 0.141 (p=0.0042); rhythm x neuroticism -0.087 (p=0.0035); raw_level x openness 0.086 (p=0.0038); raw_level x neuroticism -0.060 (p=0.0436); rhythm x openness 0.057 (p=0.0552).

## 8. Projection against realized power

| coordinate | N | projected minimal detectable r | realized 1.96 x null sd | realized / projected | band half-width |
|---|---|---|---|---|---|
| RAW LEVEL -- person-mean y | 1,116 | 0.0192 | 0.0218 | 1.135 | 0.0212 |
| ADJUSTED LEVEL -- the X-Mb author-main a_hat_u | 408 | 0.0317 | 0.0369 | 1.165 | 0.0372 |
| RHYTHM -- X2's r1_u | 1,116 | 0.0192 | 0.0227 | 1.187 | 0.0221 |
| R2 SLOPE -- the floored gap x volume within-person slope | 1,100 | 0.0193 | 0.0261 | 1.354 | 0.0265 |

The registration projected a minimal detectable r of about 0.019 at N ~ 1,116, from SR1's realized z = 5.42 at r = 0.049 on N = 1,306 under the DECLARED assumption z proportional to r*sqrt(N).

## 9. Leans

| lean | registered | realized | status |
|---|---|---|---|
| primary cell | EXPRESSION_TRAIT_SILENT to LEVEL_ONLY_COMPOSITION | EXPRESSION_TRAIT_SILENT | HELD |
| dynamics point | \|raw r\| <= 0.03 for every dynamics coordinate | r2_slope 0.0172, rhythm 0.0023 | HELD |
| cohort caveat | carried on every claim | carried | HELD |

## 10. Honest anomalies

**A1 -- The adjusted level costs two thirds of the pool.**  The Big5 analog of the X1c chain at s = 5 admits 408 of the 1,116 pool authors (0.366); the chain census at s = 3 admits 446 and at s = 8 351.  Why it matters: the level contrast's two rows do not stand on the same support, so the adjusted row is the least powerful reading in the leg (projected minimal detectable r 0.0317 against the raw level's 0.0192); the disclosed second reading exists precisely to separate the adjustment from the eligibility loss.  REPORTED, routes nothing.  The support is the chain's, and the chain is X-Mb's certified primary; no support was shopped.

**A2 -- Seven pool authors carry the zero bag signature.**  7 of the pool have no event in the 1,443-community law vocabulary, so their Hellinger cosine to everyone is 0 and their bag distance is exactly 1.  Why it matters: those rows enter the SLS partial as constant-1 covariate values; at 7 of 1,116 the effect on the residual is far below the band widths.  REPORTED; the rows are not dropped.

**A3 -- The retention ratio is not interpretable here.**  The ratio r_adjusted / r_raw = -11.7637, from a denominator (+0.0006) that sits inside its own permutation band.  Why it matters: a ratio of two numbers indistinguishable from zero has no scale; #79 already forbids a null on it, and under a SILENT verdict the point value is noise.  PRINTED for completeness and explicitly NOT read; the contrast is the two detection decisions and the two CIs.

**A4 -- The largest per-trait cell, and why it does not route.**  ADJUSTED LEVEL -- the X-Mb author-main a_hat_u x agreeableness: r = +0.1413, p = 0.0042 on n = 408; the Bonferroni threshold is 0.00250 and it does NOT survive it.  Why it matters: the per-trait table is a marginal reading of the SAME coordinate whose distance-matrix Mantel is inside its band; a marginal correlation and a Mantel r answer different questions, and only the Mantel row routes.  SECONDARY, Bonferroni-guarded, ROUTES NOTHING by registration.

**A5 -- The slope row is the closest thing to a signal, and it is still inside.**  Raw r = -0.0172, p = 0.1930, band [-0.0293, +0.0238]; the bag-partial moves it to -0.0189 (p = 0.1470) and the activity control to -0.0197 (p = 0.1230).  Why it matters: controlling the bag and activity moves it AWAY from zero rather than towards it, which is the pattern a real but small coupling would also make; at this p it is not distinguishable from the band.  REPORTED as the leg's strongest non-detection; the registered lean |raw r| <= 0.03 still holds.

**A6 -- The realized bands are wider than the projection said.**  Realized 1.96 x null sd over projected minimal detectable r: adj_level 1.165, r2_slope 1.354, raw_level 1.135, rhythm 1.187.  Why it matters: the registration's z proportional to r*sqrt(N) assumption transports SR1's power to a different coordinate family; the realized bands are 1.1x to 1.4x wider, so the scoped silence is scoped at the REALIZED widths and not at the projected 0.019.  The scoped statement is attached to the realized widths, exactly as #71's executed form requires.

## 11. Boundaries

- The coordinates are TECHNICAL OBJECTS.  Expression volume, its venue-adjusted author main, its event-time rhythm and its gap-volume slope are selection-process statistics of an author's own metadata stream.  NO PSYCHOLOGICAL NAMING is permitted REGARDLESS OF OUTCOME -- not 'talkativeness', not 'expressiveness', not 'impulsivity', not 'consistency'.  A coupling, if one is found, is a coupling of a metadata statistic to a questionnaire score.
- Metadata only.  The word count is HOW MUCH was said, never WHAT was said; no text body is read anywhere in the X line.  Every claim carries that boundary.
- The COHORT CAVEAT rides every claim.  Big5-cohort ownership is higher than the disjoint cohort's on every coordinate the X line measured (X2's rhythm 0.637 vs 0.259, X5's R2 slope 0.538 vs its disjoint value -- the sevenfold Big5-ownership flag), and the cohort's own selection cannot be separated from that.  A reading here is a reading ON THIS COHORT.
- The eq-12 / response-operator projection caution.  Each coordinate is ONE first-order projection of the response operator; a verdict here is a statement about that projection, on this pool, measured this way -- exactly as X1c's and X2's positive results were.
- #79: no ratio null.  The level contrast is read as TWO detection decisions with TWO CIs, never as a null on r_adjusted / r_raw.  The retention ratio is printed as a descriptive and routes nothing.
- EXPLORATORY, corpus-level.  No person claim is made or supportable: every estimand is a corpus-level distance-matrix statistic.
- Governance: aggregates only; no text excerpt; the body column never read; identifier artifacts confined to gitignored `results/`; ID-leak scan over 10,296 names -- 0 NEW hits, 4 pre-existing dictionary collisions carried unchanged from HEAD (baseline 4).

## 12. Config block

```json
{
 "B_boot": 1000,
 "B_perm": 999,
 "alpha": 0.05,
 "analysis_pool": {
  "anchor": 1116,
  "n_authors": 1116,
  "per_coordinate_eligibility": "each coordinate's own machinery",
  "rule": "the Big5 cohort under X2's predicate: >= 50 events in EACH of the author's own halves"
 },
 "cells": {
  "DYNAMICS_COUPLED": "rhythm or slope detects raw (any level pattern)",
  "EXPRESSION_TRAIT_SILENT": "no admitted coordinate detects raw (scoped silence at r ~ 0.019 with the realized band widths)",
  "LEVEL_INTRINSIC": "both levels detect",
  "LEVEL_ONLY_COMPOSITION": "raw level detects, adjusted level does NOT, dynamics silent",
  "precedence": "dynamics first, then the level pattern",
  "suffix": "any detecting cell gains REDUNDANT (every detecting coordinate's bag-partial is inside its band) or INCREMENTAL (at least one is outside)"
 },
 "estimands": {
  "activity_sensitivity": "partial additionally controlling |log n_u - log n_v|, n = pool event count",
  "bag_distance": "1 - Hellinger cosine of the L2-normalised sqrt full-stream in-vocabulary frequency vector over the 1443-community SR0-class law vocabulary, on this pool (U3's construction)",
  "confidence_intervals": "author-cluster bootstrap on the Mantel r, B = 1000; self-pairs excluded",
  "coordinate_geometry": "|c_u - c_v|",
  "disattenuation": "SECONDARY reading only: r / sqrt(rel_SB * 0.8); label reliability DECLARED, not measured (#57)",
  "partial": "partial Mantel r(c-dist, trait-dist | bag-dist), Smouse-Long-Sokal residual permutation, B = 999; the control is LINEAR (#82 declared)",
  "raw": "Mantel r, null = permutation of the AUTHOR ROWS of the trait matrix, B = 999, two-sided band",
  "trait_geometry": "Euclidean distance over five z-scored Big5 (#81 BY FORMULA; one z-scoring over the analysis pool; U3's reader, inherited)"
 },
 "layer": "P (label-bearing)",
 "leans": {
  "cohort_caveat": "the COHORT CAVEAT rides every claim.  Big5-cohort ownership is higher than the disjoint cohort's on every coordinate the X line measured (X2's rhythm 0.637 vs 0.259, X5's R2 slope 0.538 vs its disjoint value -- the sevenfold Big5-ownership flag), and the cohort's own selection cannot be separated from that.  A reading here is a reading ON THIS COHORT.",
  "dynamics_point": "|raw r| <= 0.03 for every dynamics coordinate",
  "primary": "EXPRESSION_TRAIT_SILENT to LEVEL_ONLY_COMPOSITION"
 },
 "leg": "M4-X3",
 "level": "corpus-level",
 "machinery_imported_by_file": [
  "scripts/run_suica_m4_u3_when_trait_join.py (stamp chain, Mantel/SLS, bag signature, reliability rows, THE label reader)",
  "scripts/run_suica_m4_x2_volume_path.py (Arm / arm_layout / masked lag-1 Pearson)",
  "scripts/run_suica_m4_x5_ergodicity_atlas.py (relation_stats with the #89 floor, RelationSkeleton, X4's cell_moments and per_cell_slopes)",
  "scripts/run_suica_m4_xmb_mains_paired.py (chain design, FE coefficients, pinned normalization, full_budget, census and #83 helpers)"
 ],
 "projection": {
  "anchor": {
   "sr1_N": 1306,
   "sr1_r": 0.049,
   "sr1_z": 5.42
  },
  "assumption": "z proportional to r*sqrt(N), declared",
  "recomputed_at_the_analysis_pool": 0.01916868656052559,
  "recomputed_per_coordinate": {
   "adj_level": 0.03170256281827076,
   "r2_slope": 0.019307591903246307,
   "raw_level": 0.01916868656052559,
   "rhythm": 0.01916868656052559
  },
  "registered_minimal_detectable_r": 0.019
 },
 "registration_commit": "8823b60",
 "reliability_gate": {
  "admitted": [
   "raw_level",
   "adj_level",
   "rhythm",
   "r2_slope"
  ],
  "excluded": [],
  "expectations": {
   "adj_level": 0.9,
   "r2_slope": 0.538,
   "raw_level": 0.9,
   "rhythm": 0.637
  },
  "measured_on": "the ACTUAL coordinate objects, label-free, BEFORE the stamp",
  "realized": {
   "adj_level": 0.9015441054463098,
   "r2_slope": 0.538039302428076,
   "raw_level": 0.8859120427927117,
   "rhythm": 0.6366996180212688
  },
  "stop_rule": "X3's registered rule: failures are reported and excluded; the leg stops clean only if EVERY coordinate fails, and that stop happens before the stamp",
  "threshold": 0.5
 },
 "secondary": {
  "guard": "Bonferroni x (5 x n_admitted)",
  "p_transform": "Fisher z, declared; the table routes nothing",
  "per_trait_table": "5 traits x admitted coordinates, Pearson of the coordinate against each z-scored trait"
 },
 "seed": 20260819,
 "seed_boot": 20260822,
 "seed_perm": 20260821,
 "tier": "EXPLORATORY",
 "title": "the trait join of expression coordinates",
 "y": "log1p(word_count_quoteless) (#70 pin)"
}
```

Generated from `results/m4_x3_trait_join/report_payload.json` (rule 24: every number in this report is read from an artifact, never retyped).  Run environment recorded in `part0.json`.
