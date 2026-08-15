# SUICA M4-SR1 — the selection-geometry test on PANDORA

**Outcome: `SELECTION_TRAIT_COUPLING_DETECTED`** (rule-16 cell 2). Modifiers: BELOW_SR0_MDR, AXIS_SPACE_NOT_RUN.

Registered before the run in `docs/SUICA_M4_S_SELECTION_LINE_PLAN.md` ("M4-SR1",
commit 5d5569d). **EXPLORATORY, corpus-level. No person claims. Aggregates only.
Quotable only with the tier label.**

## 1. The question, and the rule that binds how the answer may be read

The owner's conjecture: the gauge reads frames, but *which* frames a person
chooses is person-owned, so selection-proximity should imply
personality-proximity. That decomposes into **(a)** selection is a person-stable
signature and **(b)** selection-similarity implies trait-similarity. SR0
established (a) on this corpus, strongly. **(a) is not evidence for (b)** —
S1's γ = 0 arm is the standing physical counterexample, a perfectly stable
selection signature carrying zero trait information. This leg tests (b)
directly, and its verdict rests on one primary statistic.

**Decomposition (b) holds on this corpus.** Mantel r = 0.048987613136188025 with one-sided permutation p = 0.001 over 852,165 pairs. Selection-similarity does carry trait-similarity here.

## 2. G0sr1 — SR0's numbers bit-verified

| SR0 quantity | persisted in SR0 | registration states | matches |
|---|---|---|---|
| MDR | 0.07755299626311207 | 0.0776 | True |
| N | 1306 | 1306 | True |
| ceiling | 0.7332349793835083 | 0.7332 | True |
| coverage | 0.7813909148987143 | 0.7814 | True |
| pairs | 852165 | 852165 | True |
| vocab | 1191 | 1191 | True |

## 3. The seal: config before joint

| ordering evidence | value |
|---|---|
| config sha256 | 11b36622c2099acae3d72b54b6c8502b5cc2a913831fce1bd1f64eb6efc11876 |
| config stamped at | 2026-08-15T17:13:13.916769+00:00 |
| first joint selection × trait quantity at | 2026-08-15T17:14:45.493576+00:00 |
| **stamp precedes first join** | **True** |
| seconds between | 91.576807 |
| joint quantities before the stamp | 0 |
| selection stage opened the label table | False |

No worlds exist to seal here, so the discipline is CONFIG-BEFORE-JOINT. Part 0
builds, hashes and stamps the full analysis config — estimand definitions,
transforms, permutation seed, leans, routing — and opens no label column. The
selection stage is selection-side only. The **first joint selection × trait
quantity in the entire harness** is computed in the join stage, which logs its
own event immediately beforehand; the gate reads the run log and proves the
order.

## 4. The primary result

| quantity | value |
|---|---|
| users joined | 1306 |
| pairs | 852,165 (SR0 match True) |
| **Mantel r (Hellinger cosine × neg-sq-Euclidean)** | **0.048987613136188025** |
| permutations | 999 |
| permutations ≥ observed | 0 |
| **p (one-sided positive)** | **0.001** |
| null mean / sd | -0.00010562885372651673 / 0.009064019613144935 |
| null 95th pct / max | 0.01540180833500572 / 0.029409823942762026 |
| z vs null | 5.416277113822429 |
| SR0 minimum detectable r | 0.0776 |
| r / MDR | 0.6312836744354127 |
| exceeds MDR | False |
| disattenuated r (UNBUDGETED, routes nothing) | 0.06396318159111603 |

The observed r sits 5.416277113822429 null standard deviations above the permutation mean, and only 0 of 999 permutations reached it.

**A correction to SR0's power analysis — which this same executor produced — belongs here, because it cuts in this leg's favour.** The observed r is 0.6312836744354127× SR0's declared minimum detectable r of 0.0776, i.e. BELOW it. That declared MDR used the standard 1/√(N−1) heuristic for the Mantel permutation sd (0.027681826617913324). The EMPIRICAL permutation null sd is 0.009064019613144935 — the heuristic overstates the null spread by 3.0540342805269574×. The corrected empirical MDR is 0.025393623364872876, and the observed r is 1.929130492025523× that. The registered test is the permutation null and always was, so the routing is unaffected; but SR0's power table was wrong, and it was wrong in the direction that makes this leg look better.

**Disattenuation is UNBUDGETED and routes nothing** (RN-SR1-4). The
selection-side reliability 0.7332 is measured (SR0); the label reliability 0.80
is a **declared** parameter, not a measurement. The disattenuated figure is an
illustration of scale only.

## 5. Second readings (adjudicating nothing)

### 5.1 Geometry grid

| selection geometry | trait geometry | Mantel r | sign |
|---|---|---|---|
| hellinger_cosine (PRIMARY) | negative_squared_euclidean (PRIMARY) | 0.048987613136187574 | 1 |
| hellinger_cosine (PRIMARY) | centred_profile_cosine | 0.03207134928723893 | 1 |
| raw_frequency_cosine | negative_squared_euclidean (PRIMARY) | 0.03703374254514458 | 1 |
| raw_frequency_cosine | centred_profile_cosine | 0.025984074919015603 | 1 |
| negative_euclidean_distance | negative_squared_euclidean (PRIMARY) | 0.04789480729045626 | 1 |
| negative_euclidean_distance | centred_profile_cosine | 0.03201520943384964 | 1 |

**GEOMETRY_SPLIT = False.** All geometries agree in sign, so the reading does not depend on the direction convention (the owner's C-4 concern is checked and clear).

### 5.2 Split-half

| reading | value |
|---|---|
| early half × traits | 0.03985813511679325 |
| late half × traits | 0.04498873327209943 |
| mean | 0.042423434194446344 |
| halves agree in sign | True |
| selection self-consistency (early × late selection geometry) | 0.675573251251224 |

### 5.3 Comment-count tertiles

| comment-count tertile | users | pairs | median comments | Mantel r |
|---|---|---|---|---|
| low | 437 | 95,266 | 73.0 | 0.0444626838820253 |
| mid | 434 | 93,961 | 481.5 | 0.03199603525666885 |
| high | 435 | 94,395 | 2884.0 | 0.06391622568311668 |

### 5.4 The 12-axis space — NOT RUN, and why

The axis constructor is live code, but a faithful refit runs TF-IDF over **slice
text** (constructor lines 49–55) and both of its inputs are absent from disk:
`phase2_passB_slicetext_s128.parquet` and `tier_u_comments.parquet`. Refitting
would therefore require reading comment text — which this line has deliberately
never done — and substituting a co-occurrence "axis" would be a different object
that invites exactly the mis-citation the planner barred. Reported as NOT_RUN
with the reason, rather than approximated.

## 6. R-G compliance

| R-G check | result |
|---|---|
| ID-leak scan: cohort IDs checked | 1401 |
| **ID-leak scan: leaks found** | **0** |
| aggregates only | True |
| body column never read | True |
| essays untouched | True |
| identifier artifacts confined to gitignored results | True |
| native corpus untouched | True |
| no cross corpus linkage | True |
| no per user rows in report | True |
| no text excerpts | True |

The `body` column was never read. Sources were read in place from the private
paths. The only identifier-bearing artifact is SR0's cohort file in gitignored
`results/`.

## 7. Anomalies

1. **A-1 (before any number).** Interpreter re-verified as standing practice:
   `/private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv2/bin/python`, Python 3.12.12, numpy 2.4.4, pandas 3.0.2 — matching every
   prior leg.
2. **A-2 (before any number).** `timeout(1)` is absent on macOS; every stage ran
   as its own foreground command under an explicit tool timeout.
3. **A-3 (before any joint quantity).** The 12-axis refit was ruled out on
   evidence — its inputs were checked and found absent — rather than skipped by
   preference.

## 8. Boundary

EXPLORATORY, corpus-level, one corpus, one cohort, one primary geometry.
The coupling is a corpus-level pairwise statistic, not a person-level claim, and its magnitude is small in absolute terms.

## 9. Environment

`/private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv2/bin/python` — Python 3.12.12, numpy 2.4.4, pandas 3.0.2.
