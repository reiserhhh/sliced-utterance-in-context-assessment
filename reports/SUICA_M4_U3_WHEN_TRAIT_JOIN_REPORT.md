# SUICA M4-U3 -- the Who x When trait join

**VERDICT: `WHEN_TRAIT_SILENT` (cell 1).**  Tier EXPLORATORY, corpus-level.  The verdict keys on the PRIMARY coordinate `stay_ct` alone; `tight` and `drift_pa` are secondary rows carrying a Bonferroni x3 guard and never route.

Primary row: raw Mantel r = **-0.0036** [band -0.0231, 0.0213], p = 0.7430; partial (bag-controlled) r = **-0.0125** [band -0.0216, 0.0202], p = 0.2570, over 847 authors and 358,281 pairs.

**Scoped statement (attached to the realized-band width report, and only there): silent beyond r ~ 0.022.**  The realized two-sided band half-width is 0.0222 and the realized minimal detectable r (1.96 x null sd) is 0.0220 against the registration's projected 0.0220 -- a ratio of 1.000.  No equivalence cell is claimed beyond this sentence.

**The silence is not a dead harness.**  On the SAME pairs, with the SAME trait matrix and the SAME Mantel machinery, the Where channel is live: Mantel(bag-distance, trait-distance) = **0.0490** on `stay_ct`'s pool, against SR1's independently established 0.049 on a different pool of 1,306.  A within-harness point estimate, DESCRIPTIVE and routing nothing -- no null was run on it, because it is not a registered estimand of this leg -- but it is the reading under which the When rows' bands mean what they say: the machinery finds the coupling it is known to find, in these very pairs, and finds none through the When coordinates.

## 1. The label event

The label event.  This leg opens the PANDORA Big5 columns of author_profiles.csv once, under the stamp, for the 849-author analysis pool -- the SR1/SR2 class of re-join.  No per-author trait value is written to any committed file; only aggregate statistics leave stage E.

- source: `/Volumes/mobile3/projects/project persona/data_sets/PANDORA_official/author_profiles.csv`
- columns opened: `author`, `agreeableness`, `openness`, `conscientiousness`, `extraversion`, `neuroticism`
- opened: ONCE, in stage E, after `first_join` was logged at 2026-08-18T06:56:16.267746+00:00
- analysis pool label completeness: 849 of 849 (1.0000) -- the registration's 100% census reproduces
- z-scoring: the 849-author analysis pool (one z-scoring, reused by every coordinate row)
- no per-author trait value appears in any committed file; only the aggregate statistics below left stage E.

## 2. The stamp chain (G-U3)

| event | utc | artifact | sha256 (16) |
|---|---|---|---|
| config stamped | 2026-08-18T06:56:01.975215+00:00 | `config.json` | `8c399494dfbba293` |
| coordinate table frozen | 2026-08-18T06:56:16.189523+00:00 | `coordinates.npz` | `4a4aa07100c8c473` |
| FIRST JOIN | 2026-08-18T06:56:16.267746+00:00 | `join.json` | -- |

**`stamp_utc < coordinate_freeze_utc < first_join_utc` = yes** (+14.2 s, then +0.1 s).  Joint quantities before the stamp: 0.  Labels opened before the stamp: no.  Both hashes re-verify: config yes, coordinates yes.  G-U3 PASS = yes; ID-leak scan 0 hits over 1,398 cohort names in 5 committed files.

## 3. Part 0 anchors (no label opened)

| anchor | registered | observed | match |
|---|---|---|---|
| cache events | 3,005,360 | 3,005,360 | yes |
| cache authors | 1,401 | 1,401 | yes |
| cache vocabulary | 1,191 | 1,191 | yes |
| block_pool_ge4_blocks | 849 | 849 | yes |
| drift_eligible | 652 | 652 | yes |
| stay_eligible | 847 | 847 | yes |
| tight_eligible | 763 | 763 | yes |

**RD-U3-1 (disclosed re-posing, decided label-free in part 0, before the stamp).**  The registered prose predicate `>= 30 per half` admits 848 authors from this cache while the registered census names 847; exactly 1 author sits at min(early, late) = 30.  U3 adopts the STRICTLY TIGHTER `> 30 per half`, which reproduces the registered pool exactly (847).  The looser pool routes nothing.

## 4. Coordinates: reliability, gate, and the joined estimands

| coordinate | role | split-half r | SB | gate (>= 0.5) | pool | mean (sd) | raw r [band] p | partial r [band] p | + activity r [band] p | disatt. raw (SECONDARY) |
|---|---|---|---|---|---|---|---|---|---|---|
| `stay_ct` | PRIMARY | 0.7685 | 0.8691 | **ADMIT** | 847 (358,281 pairs) | 0.5413 (0.2037) | -0.0036 [-0.0231, 0.0213] p=0.7430 | -0.0125 [-0.0216, 0.0202] p=0.2570 | -0.0124 [-0.0200, 0.0219] p=0.2490 | -0.0043 |
| `tight` | secondary | 0.8872 | 0.9402 | **ADMIT** | 763 (290,703 pairs) | 0.7718 (0.1427) | -0.0087 [-0.0251, 0.0254] p=0.4930 | -0.0132 [-0.0252, 0.0237] p=0.2950 | -0.0131 [-0.0258, 0.0266] p=0.3280 | -0.0100 |
| `drift_pa` | secondary | 0.9383 | 0.9681 | **ADMIT** | 652 (212,226 pairs) | 0.2565 (0.1831) | -0.0042 [-0.0313, 0.0313] p=0.7780 | -0.0111 [-0.0283, 0.0304] p=0.4560 | -0.0110 [-0.0284, 0.0297] p=0.4670 | -0.0048 |

Disattenuation is a SECONDARY reading only: r / sqrt(rel_SB x 0.8) with the label reliability 0.8 **DECLARED, not measured** (#57).  It illustrates scale and routes nothing.

Reliability provenance: the registration's census echoes are tight 0.8872, drift_pa 0.9383 (both exact predicates, both reproduced here) and stay 0.7828 as a DECLARED PROXY on subreddit-level states; the measured C = 24 value is the one gated on.

## 5. The bag channel and the increment question

| coordinate | Mantel(bag-dist, trait-dist) | corr(coord-dist, bag-dist) | corr(coord-dist, activity-dist) | raw -> partial shift | partial + bag^2 (2nd reading) | raw on SQUARED Euclidean (2nd reading) |
|---|---|---|---|---|---|---|
| `stay_ct` | 0.0490 | 0.1768 | 0.0081 | -0.0036 -> -0.0125 | -0.0127 p=0.2380 | -0.0036 p=0.7710 |
| `tight` | 0.0494 | 0.0902 | 0.0347 | -0.0087 -> -0.0132 | -0.0132 p=0.2910 | -0.0087 p=0.5220 |
| `drift_pa` | 0.0559 | 0.1205 | 0.0031 | -0.0042 -> -0.0111 | -0.0116 p=0.4500 | -0.0034 p=0.8150 |

SR1's corpus-level selection x trait coupling (r = 0.049) is the declared effect-scale anchor for every row above.

SECOND READINGS, ROUTING NOTHING.  (a) The registered SLS partial controls the bag channel LINEARLY, so a shared NON-LINEAR dependence of both distances on the bag would survive it; the quadratic row adds bag^2 to the control.  (b) SR1's trait geometry was negative SQUARED Euclidean while U3's registration says Euclidean distance; the squared row shows what that choice is worth.

## 6. Projection versus realized width

| coordinate | N | registered MDR | MDR recomputed at this N | realized 1.96 x null sd | realized / projected | band half-width |
|---|---|---|---|---|---|---|
| `stay_ct` | 847 | 0.022 | 0.0220 | 0.0220 | 1.000 | 0.0222 |
| `tight` | 763 | 0.022 | 0.0232 | 0.0254 | 1.094 | 0.0252 |
| `drift_pa` | 652 | 0.022 | 0.0251 | 0.0300 | 1.198 | 0.0313 |

The projection assumption is DECLARED: z proportional to r*sqrt(N), scaled from SR1's realized z = 5.42 at r = 0.049, N = 1306.  It is an assumption about how one leg's power transfers to another's pool, not a measurement.

## 7. Secondary rows and their guard

| coordinate | cell | raw detected (uncorrected) | raw detected (Bonferroni x3) | partial detected (Bonferroni) | flag |
|---|---|---|---|---|---|
| `tight` | 1 `WHEN_TRAIT_SILENT` | no | no | no | no detection |
| `drift_pa` | 1 `WHEN_TRAIT_SILENT` | no | no | no | no detection |

## 8. Registered leans against the outcome

| lean | registered | realized | outcome |
|---|---|---|---|
| primary (cell) | SILENT-to-REDUNDANT for stay_ct, point \|raw r\| <= 0.03 | `WHEN_TRAIT_SILENT` | HELD |
| primary (point) | \|raw r\| <= 0.03 | \|raw r\| = 0.0036 | HELD |
| secondary (weak, structural) | if any row detects raw, it is tight or drift_pa (structural only) | -- | NOT_ACTIVATED (no row detects raw) |

## 9. Boundaries

- **Tier EXPLORATORY, corpus-level, one Reddit cohort** (PANDORA, 1,401 authors, 2015-2019).  NO PERSON CLAIMS: nothing here licenses a statement about any individual.
- **Section 5.4.**  The coordinates are TECHNICAL OBJECTS (section 5.4).  stay_ct, tight and drift_pa are selection-process statistics of an author's own event stream.  No psychological naming is permitted regardless of outcome -- not 'inertia as a trait', not 'consistency', not 'openness to change'.
- **Slow time.**  The drift-aware caution.  Slow-time coordinates are MOVING TARGETS: each author's coordinate is measured over that author's own span, so a null or a coupling here is a statement about coordinates measured that way, not about a fixed personal quantity.
- **Equation 12.**  The eq-12 projection caution.  Each coordinate is ONE first-order projection of K_u; a verdict here is a statement about that projection, exactly as U1's positive result was.
- **The label event, named.**  The label event.  This leg opens the PANDORA Big5 columns of author_profiles.csv once, under the stamp, for the 849-author analysis pool -- the SR1/SR2 class of re-join.  No per-author trait value is written to any committed file; only aggregate statistics leave stage E.
- **Disattenuation.**  Disattenuation is a SECONDARY READING ONLY (#57 family).  The coordinate reliability is MEASURED here; the label reliability 0.80 is DECLARED, so the disattenuated number illustrates scale and routes nothing.
- The three coordinates are measured on THREE DIFFERENT POOLS (the eligibility predicates differ), so the rows are not a within-author comparison and must never be read as a ranking.

## 10. Configuration block

```json
{
 "B_perm": 999,
 "C_states_plus_oov": 25,
 "K_block": 50,
 "alpha": 0.05,
 "analysis_pool": {
  "n_authors": 849,
  "rule": ">= 4 disjoint K=50 in-vocabulary blocks"
 },
 "config_sha256": "8c399494dfbba2933038fdfb4a3f734526f676c81dc258a0321374e7667daf10",
 "coordinates_sha256": "4a4aa07100c8c4732afa6e7372875eb424ee5d3a0926968b2aab45767e3dc415",
 "kmeans_n_init": 10,
 "label_reliability_DECLARED": 0.8,
 "leg": "M4-U3",
 "predicates": {
  "drift_pa": ">= 3 pairs in EACH cell",
  "stay": "> 30 cross-thread adjacencies in EACH half (RD-U3-1)",
  "tight": ">= 2 such pairs"
 },
 "registration_commit": "921fe86",
 "reliability_gate": 0.5,
 "seed": 20260818,
 "tier": "EXPLORATORY"
}
```

Artifacts (gitignored): `results/m4_u3_when_trait_join/` -- `config.json`, `config.sha256.json`, `part0.json`, `stageb.json`, `coordinates.npz`, `coordinate_freeze.json`, `join.json`, `gate.json`, `verdict.json`, `id_leak_scan.json`, `report_payload.json`, `run_log.jsonl`.  Every table above is generated from `report_payload.json` (rule 24); the report is never hand-edited.

Generated 2026-08-18T07:04:23.200544+00:00 by `scripts/run_suica_m4_u3_when_trait_join.py` (stage `report`).
