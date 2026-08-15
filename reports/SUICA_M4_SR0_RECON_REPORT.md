# SUICA M4-SR0 — the real-data reconnaissance

**Outcome: `SR1_READY`**

Registered before the run in `docs/SUICA_M4_S_SELECTION_LINE_PLAN.md` ("M4-SR0",
commit 21149bb). **The first real-data leg of the identity era.** The
REAL-DATA GOVERNANCE block (R-G1..R-G8) is binding law for this leg and was
treated as such.

**This leg computed no statistic linking selection to any label.** That is
enforced by the code's structure and verified by enumeration in §7, not asserted.

## 1. Source manifest

| source | path | size (MiB) | columns | rows | exists |
|---|---|---|---|---|---|
| comments | /Volumes/mobile3/projects/project persona/data_sets/PANDORA_official/all_comments_since_2015.csv | 5389.8 | 17 | '-' | True |
| profiles | /Volumes/mobile3/projects/project persona/data_sets/PANDORA_official/author_profiles.csv | 1.2 | 38 | 10295 | True |
| prepared_big5 | /Volumes/mobile3/projects/project persona/data_sets/prepared/pandora_official/pandora_official_big5_prepared.csv | 12.3 | 19 | 1401 | True |
| v2lib | /Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/scripts/suica_v2_lib.py | 0.0 | '-' | '-' | True |

| verification | result |
|---|---|
| comments: `subreddit` field present | True |
| comments: `created_utc` field present | True |
| comments: `author` field present | True |
| profiles: all five Big5 columns present | True |
| profiles: rows / authors with all five Big5 | 10295 / **1568** |
| canonical SR1 cohort (registration's N) | **1401** — prepared Big5 mainline (N=1401); strict subset of the five-complete set: True |
| prepared Big5: rows | 1401 (registration said 1401 rows: True) |
| prepared Big5: unique `user_id` | **1401** (equals 1401: True) |
| comment timestamp range | 2014-12-31T23:54:39+00:00 → 2019-04-30T23:58:17+00:00 |

The comment table is 5389.8 MiB and was read **streamed**, three columns only
(`author`, `subreddit`, `created_utc`), in chunks of 2,000,000 rows — never
loaded whole, and `body` never read at all.

**On the cohort count.** The registration describes the prepared Big5 CSV as
1401 rows, and it is exactly that: 1,401 rows, 1401 unique
`user_id`. (A naive `wc -l` reports far more, because the `text` column contains
embedded newlines — worth knowing before anyone audits the file that way.)
Counted independently from `author_profiles.csv`, **1568** authors carry all
five Big5 values; the prepared mainline cohort of 1401 is a strict
subset of them (intersection 1401). This leg takes the registration's
1401 as the canonical SR1 cohort and reports the 1568 as the wider
labelled pool — a real headroom fact for SR1, not a discrepancy.

## 2. The selection-signature object for SR1

| item | value |
|---|---|
| declared floor (before the stream) | a subreddit enters iff used by ≥ 0.01 of cohort users = 15 users |
| distinct subreddits seen in cohort | 15863 |
| **vocabulary size at the floor** | **1191** |
| coverage: cohort comments inside the vocabulary | 0.7813909148987143 |
| total cohort comments | 3,005,360 |
| rows streamed / rows in cohort | 17,640,062 / 3,005,360 |
| cohort users with ≥ 1 comment | 1401 |
| users with a signature (≥ 20 comments) | **1306** |
| mean non-zero subreddits per user | 44.50076569678407 |
| sparsity (mean non-zero / vocabulary) | 0.03736420293600678 |

| percentile | p0 | p10 | p100 | p25 | p5 | p50 | p75 | p90 | p95 |
|---|---|---|---|---|---|---|---|---|---|
| comments per cohort user | 1.0 | 47.0 | 52406.0 | 135.0 | 26.0 | 575.0 | 2069.0 | 5705.0 | 9669.0 |

The vocabulary floor was declared before the stream and from counts alone
(RN-SR0-2): a subreddit enters iff at least 1% of cohort users post there. No
floor was chosen after seeing a coverage number.

## 3. Split-half feasibility and the stability ceiling

| item | value |
|---|---|
| users eligible (≥ 40 comments) | 1282 |
| users scored (both halves non-empty) | 1271 |
| self cosine (own early vs own late), mean | **0.6814441717128207** |
| self cosine sd | 0.2882601041061215 |
| other cosine (own early vs a permuted user's late), mean | 0.05115484595892177 |
| discrimination (self − other) | **0.630289325753899** |
| pairwise-similarity reliability, split-half | 0.5788247760635731 |
| **pairwise-similarity reliability, Spearman-Brown (the SR1 ceiling)** | **0.7332349793835083** |
| pairs used for the reliability estimate | 404,550 |

Halves are cut at each user's **own median timestamp** (RN-SR0-3), so they are
disjoint in time. The number that matters for SR1 is the last row: the
reliability of the *pairwise similarity* object, because that — not the raw
frequency vector — is what a Mantel test correlates. The measured ceiling is 0.7332349793835083 (Spearman-Brown). Any Mantel correlation SR1 observes is attenuated by its square root, so the ceiling is the honest cap on what the corpus can show.

## 4. Label-side marginals (computed in a separate stage)

| trait | n | mean | sd | variance | p25 | p50 | p75 |
|---|---|---|---|---|---|---|---|
| agreeableness | 1401 | 42.34939329050678 | 30.906133487248784 | 955.1890871316407 | 14.0 | 40.0 | 70.0 |
| openness | 1401 | 62.09528907922912 | 27.687923217119188 | 766.6210920770877 | 42.0 | 69.0 | 85.0 |
| conscientiousness | 1401 | 40.426481084939326 | 30.1921871108564 | 911.5681625369633 | 13.0 | 35.0 | 65.0 |
| extraversion | 1401 | 36.61670235546038 | 30.146388899654326 | 908.8047636892016 | 10.0 | 28.0 | 59.0 |
| neuroticism | 1401 | 49.64204139900071 | 32.24694596571011 | 1039.8655241154277 | 18.0 | 50.0 | 82.0 |

Marginals only. This stage never opened a selection artifact.

## 5. SR1 power analysis

| item | value |
|---|---|
| N effective (signature ∩ gold) | **1306** |
| pairs | 852,165 |
| permutations planned | 999 |
| α / power target | 0.05 / 0.8 |
| permutation null sd ≈ 1/√(N−1) | 0.027681826617913324 |
| **minimum detectable OBSERVED Mantel r** | **0.07755299626311207** |
| selection-side reliability (measured) | 0.7332349793835083 |

| assumed label reliability | attenuation √(rel_sel·rel_lab) | minimum detectable TRUE Mantel r |
|---|---|---|
| 1.0 | 0.8562914103174856 | 0.09056846224156084 |
| 0.9 | 0.812349359232318 | 0.09546754162076374 |
| 0.8 | 0.765890320807625 | 0.10125861909487652 |
| 0.7 | 0.7164247940771284 | 0.1082500171745353 |
| 0.6 | 0.6632804743320166 | 0.11692338198439348 |
| 0.5 | 0.6054894629072864 | 0.1280831476252909 |

Label reliability is **not** measured here — that is outside this leg's mandate —
so it is carried as a declared parameter and the requirement is read across a
range (RN-SR0-4).

## 6. The 12-axis choice constructor

| item | result |
|---|---|
| 12-axis choice constructor in this repo | **FOUND (constructor); FITTED ARTIFACT ABSENT** |
| searched | scripts/, docs/, reports/, suica_core/ for choice axis / choice_axes / N_CLASSES / 12 axes / holdout |
| what exists instead | a LIVE constructor, not a lost v2 artifact: subreddit centroids from TF-IDF -> TruncatedSVD(64) -> KMeans(12) build the subreddit->axis map, and per-user selection is projected onto the axes as log-ratio shares against the population mean. A second constructor (op6a) refits on cohort A and confirms on cohort B -- the source of the 5/5 holdout. |
| consequence for SR1 | SR1's PRIMARY signature object (per-user subreddit frequency vectors over the declared vocabulary) needs none of this and is fully available. The 12-axis projection is available only by REFITTING, because the fitted class map is not on disk (results/ is gitignored). SR1 must therefore either use the frequency vectors directly or re-fit and artifact-pin the class map first; it must NOT cite the existing 5/5 holdout as though the same fitted axes were in hand. |

## 7. The no-peek gate, by enumeration

| no-peek check | result |
|---|---|
| artifacts produced (enumerated) | axis_finding.json, cohort_authors.csv, gate.json, labels.json, power.json, run_log.jsonl, selection.json, sources.json, vocab_size.npy |
| unexpected artifacts | **none** |
| joint selection × label quantities found | **none** |
| selection stage opened the label table | False |
| labels stage opened a selection artifact | False |
| cohort hand-off file columns | ['author'] → ids only: True |
| **G-SR0** | **PASS = True** |

The separation is structural. `stage_selection` is handed the cohort as a bare
author-id list whose writer asserts it has exactly one column, and it never opens
`author_profiles.csv`. `stage_labels` never opens a selection artifact.
`stage_power` sees both sides only as summary scalars already written. There is
no code path in this harness that joins a selection object to a label value.

## 8. R-G compliance statement

- **R-G: no person claims.** Every number in this report is a corpus-level
  aggregate, a distribution percentile, or a count. No claim about any
  individual is made or supportable from it.
- **No user IDs.** The only artifact containing author identifiers is
  `cohort_authors.csv`, which lives in `results/` (gitignored) and is never
  read into the report. The report contains none.
- **No text.** The `body` column was never read. No excerpt appears anywhere.
- **No per-user rows.** The report carries aggregates only.
- **No cross-corpus linkage.** One corpus was opened. Essays was not touched and
  its confirm-half labels remain sealed; the native corpus remains paused and
  was not read.
- **Sources read in place** from the private data paths; nothing was copied into
  this repository.

## 9. Anomalies

1. **A-1 (before any number).** Interpreter re-verified as standing practice
   after the previous leg's venv loss: `/private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv2/bin/python`, Python 3.12.12, numpy
   2.4.4, pandas 3.0.2 — matching every prior leg.
2. **A-2 (before any number).** `timeout(1)` is absent on macOS; every stage ran
   as its own foreground command under an explicit tool timeout.
3. **A-3 (a reconnaissance finding, not an execution fault).** The 12-axis constructor exists and is live, but its FITTED artifact (`results/suica_e3_e4_choice_class_v2_s128/condition_class_map.csv`) is not on disk — `results/` is gitignored — so the subreddit→axis assignment behind the existing 5/5 holdout cannot currently be reproduced without a refit. Reported here because SR1 would otherwise inherit it silently.

## 10. Routing

All pinned sources exist and verify, the selection-signature object is defined and abundant, split-half is feasible, and the design has power: with N = 1306 and a measured selection-side reliability of 0.7332349793835083, the minimum detectable OBSERVED Mantel r is 0.07755299626311207. **SR1 is registrable.** Two conditions travel with that: the 12-axis projection needs a refit and an artifact pin before it may be used or cited, and SR1 must carry the S1 lesson as a live alternative -- a perfectly stable selection signature can be trait-silent, so stability evidence must not be read as coupling evidence.

## 11. Environment

`/private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv2/bin/python` — Python 3.12.12, numpy 2.4.4, pandas 3.0.2.
