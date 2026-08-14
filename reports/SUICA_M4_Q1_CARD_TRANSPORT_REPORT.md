# SUICA M4-Q1 — card transport under frame refreshment — **INEXPRESSIBLE**

**Outcome: INEXPRESSIBLE (routing cell 1); modifiers: none.**
STOP / INEXPRESSIBLE. Stopped at the registration's own expressibility clause, answered by code in Part 0 + the demonstration. **0 measurement pairs
drawn** (16 demonstration pairs on the pilot salt).

**The card layer's b-truth is frame-free by construction, so truth-side frame
refreshment is a null operation there.** The registration's own expressibility
clause is the right exit, and it is reached by code rather than by argument: the
cross-world path was built, proven bit-exact against k2b at the zero point, and
then shown to return **exactly** C_nat when pointed at the B-world.

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_Q_TRANSPORT_LINE_PLAN.md` BEFORE run (commit 0f3d773). Every
number below is generated from artifacts by code (rule 24).

---

## 1. The card statistic, pinned — and it has two readings

Appendix N says *"card attenuation 0.827 vs field recovery 0.178"*. **Two
persisted objects round to 0.827**, and the registration does not disambiguate,
so both are pinned and both are carried through the expressibility test
(RN-Q1-1).

| property | reading A -- the closed form | reading B -- the measured |
|---|---|---|
| object | `r_card_b_pred_raw` | `r_card_b_raw` |
| function | arm_predictions | card_channel_frame -> pooled_card_stats |
| source pin | `scripts/run_suica_m4_k2b_t4_branch.py:533` | `scripts/run_suica_m4_k2b_t4_branch.py:392-457` |
| computed at | `scripts/run_suica_m4_k2b_t4_branch.py:577` | `scripts/run_suica_m4_k2b_t4_branch.py:486` |
| value at A1 | 0.8271784593117322 | 0.8266850143926395 |
| takes a world | False | True |
| forms author-indexed vectors | False | True |
| **has a truth side to replace** | **False** | **True** |
| expressible as author-indexed card vectors | False | True |
| why | pure algebra over retained cell sizes and the four variance shares; it never touches a world, an author, or a vector, so there is no truth-side panel in it to swap | 64-dim per-author vectors exist inside the function (the card `full` and the truth `trait`) and are contracted row-wise, so a cross-world variant is constructible -- though every RETURNED column is a per-author scalar, so the vectors must be re-derived rather than read off a persisted artifact |
| estimate side | — | the card, scripts/run_suica_m4_k2b_t4_branch.py:423 (w_mu*trait_c + w_slow*slow_c + w_int*int_c + w_noise*noise_c, each centred in the (context, m) cell; the frame channel is EXCLUDED by construction) |
| **truth side** | — | **world['trait'][idx], scripts/run_suica_m4_k2b_t4_branch.py:410 -- the BARE LATENT TRAIT ARRAY, not a card** |

| quantity | registration / expected | persisted | bit-exact |
|---|---|---|---|
| card, closed form (r_card_b_pred_raw, A1) | 0.8271784593117322 | 0.8271784593117322 | True |
| card, measured (r_card_b_raw, A1) | 0.8266850143926395 | 0.8266850143926395 | True |
| field, measured (recovery_b_only_mean, A1) | 0.177888649457317 | 0.177888649457317 | True |
| ratio, closed form / field | ~4.5 | 4.6499788594449205 | prose |
| ratio, measured / field | ~4.5 | 4.6472049617252065 | prose |
| note | appendix N says '~4.5x' with a tilde; neither persisted ratio is 4.5 and no artifact carries a ratio key -- the tilde is doing real work and the number is prose, not a computed object | — | — |

| anchor | located at | verbatim quote (extracted by code, rule 24) |
|---|---|---|
| appendix N instrument-role typing (the 4.5x sentence) | `docs/SUICA_IDENTITY_THEORY_V1.md:894` (para 893-900) | **N.2 — Instrument-role typing (T5's table, closing line).** As a TRAIT instrument at these regimes the plain card reader dominates the deployed relation-field gauge by ~4.5× (card attenuation 0.827 vs field recovery 0.178 at the lowest state share). The gauge is an occasion-bound-object instrument — the F-line's wall, now with its mechanism. Reader licensing: trait questions → card-family readers with frame-refreshed discriminators (T6″); occasion-bound-object questions → the relational gauge; never the converse. |
| the Q-line handoff sentence | `docs/SUICA_IDENTITY_THEORY_V1.md:1886` (para 1875-1887) | **II.2 — The instrument statement.** At this family's regimes, the deployed relation-field gauge reads FRAME-AGREEMENT: its level, its φ-gradient, and its response to frame injection are all predominantly frame-borne; genuine cross-frame person transport is bounded at ≤ about a third (CI) with a point near a ninth. The M-line and N-line laws are untouched AS LAWS OF THE STATISTIC — sealed predictions hit regardless of what the statistic reads. What re-types is the mechanism: the readability penalty (Z.1), the scaffold gradient (FF.3), and the level law's r-channel are frame-agreement phenomena. The instrument-role typing of appendix N (cards ≈ 4.5× the gauge at trait reading) now awaits its … |

The ratio is worth a note: 4.6499788594449205 under the closed-form reading and
4.6472049617252065 under the measured one. Appendix N's "~4.5×" carries a tilde and
no artifact holds a ratio key — the number is prose, not a computed object.

### 1.1 The registration's phrase names an object that does not exist

The registration says C_ref *"replaces only the truth-side card panel with the
B-world's"*. In `card_channel_frame` the truth side is **not a card panel**: it
is world['trait'][idx], scripts/run_suica_m4_k2b_t4_branch.py:410 -- the BARE LATENT TRAIT ARRAY, not a card. The estimate side is a card (a centred channel mixture with
the frame channel excluded by construction); the truth side is the bare latent
trait. This harness replaces exactly the object that can be replaced, and
reports the mismatch rather than papering over it (RN-Q1-2).

## 2. The instrument and the C2 battery

| property | value |
|---|---|
| imported from | `scripts/run_suica_m4_p3b_refresh_gradient.py:279` |
| signature | `build_split_world(author_seed: 'int', frame_seed: 'int', phi_slow: 'float') -> 'dict[str, np.ndarray]'` |
| function sha256 (this leg) | a7618a321752fc502d804745f2e83b7dd75af7e3f8a88868575c3afa632ed9bc |
| function sha256 (P3c persisted) | a7618a321752fc502d804745f2e83b7dd75af7e3f8a88868575c3afa632ed9bc |
| **function sha matches** | **True** |
| file sha256 (this leg) | b06c36bc3ff5a757d73e25c42bd19491d300e117de4b2f1b45085a2f1fe1cd4a |
| file sha256 (P3c persisted) | b06c36bc3ff5a757d73e25c42bd19491d300e117de4b2f1b45085a2f1fe1cd4a |
| **file sha matches** | **True** |

Hashes match P3b's persisted values (True / True).

| check | objects | result |
|---|---|---|
| author objects bit-identical | trait, a_load, loadings | True |
| frame norm delta: slow | frame | [251.02075811919303, 251.2642344969858] |
| frame norm delta: slow_latent | frame | [1229.5739966580375, 1230.678041532583] |
| frame norm delta: noise | frame | [251.12215870305664, 251.61673066141282] |
| frame norm delta: common | frame | [15.760782951513832, 16.263078016415818] |
| frame norm delta: int | frame | [250.58685697006015, 252.69669961573538] |
| determinism | all objects | True |
| shared basis | loadings | True |
| **C2 (4 fresh probes)** | — | **PASS = True** |

C2 = True on 4 fresh probe pairs. **Note what C2a certifies:
the author objects — `trait` among them — are bit-identical between A and B.**
That certification is the whole story of this leg.

## 3. G1q1(b) — the cross-world path is k2b's statistic, not a lookalike

| phi | pair | k2b r_card_b_raw | cross-world path, A vs A | frame bit-identical | statistic bit-identical |
|---|---|---|---|---|---|
| 0.05 | 0 | 0.7856147959429605 | 0.7856147959429605 | True | True |
| 0.05 | 1 | 0.7806106161266513 | 0.7806106161266513 | True | True |
| 0.05 | 2 | 0.783686729307712 | 0.783686729307712 | True | True |
| 0.05 | 3 | 0.7875354457678577 | 0.7875354457678577 | True | True |
| 0.05 | 4 | 0.7838577140773021 | 0.7838577140773021 | True | True |
| 0.05 | 5 | 0.7832582025177404 | 0.7832582025177404 | True | True |
| 0.05 | 6 | 0.7874492994014174 | 0.7874492994014174 | True | True |
| 0.05 | 7 | 0.7853762367328722 | 0.7853762367328722 | True | True |
| 0.98 | 0 | 0.6784358446934362 | 0.6784358446934362 | True | True |
| 0.98 | 1 | 0.674835442994792 | 0.674835442994792 | True | True |
| 0.98 | 2 | 0.6768749395983972 | 0.6768749395983972 | True | True |
| 0.98 | 3 | 0.672084087627381 | 0.672084087627381 | True | True |
| 0.98 | 4 | 0.6764730085935434 | 0.6764730085935434 | True | True |
| 0.98 | 5 | 0.674816850005901 | 0.674816850005901 | True | True |
| 0.98 | 6 | 0.6795863430964846 | 0.6795863430964846 | True | True |
| 0.98 | 7 | 0.6775306261465067 | 0.6775306261465067 | True | True |
| **G1q1(b)** | — | — | — | True | **PASS = True** |

Run with `world_truth = world_est`, the cross-world path reproduces k2b's own
`card_channel_frame` **byte-for-byte** and its pooled `r_card_b_raw` exactly, on
all 16 checks: G1q1(b) = True. The trap was avoided explicitly
(RN-Q1-3): `trait_c` feeds both the card and the centred truth, so only the
truth-side trait is parameterised and the card keeps A's throughout.

## 4. The result: C_ref ≡ C_nat, identically

| phi | n | C_nat mean | C_nat SEM | C_ref mean | C_ref SEM | L_C mean | max \|L_C\| | C_ref == C_nat on every pair |
|---|---|---|---|---|---|---|---|---|
| 0.05 | 8 | 0.7846736299843141 | 0.0008174982320896168 | 0.7846736299843141 | 0.0008174982320896168 | 0.0 | 0.0 | True |
| 0.98 | 8 | 0.6763296428445553 | 0.0008382417866778095 | 0.6763296428445553 | 0.0008382417866778095 | 0.0 | 0.0 | True |

**C_ref equals C_nat on every pair at both φ (True), with
max |L_C| = 0.0.** Not "within noise" — *identically*, to the last bit.

The reason is one line of the generator. The card statistic's truth side is
`world["trait"]`, a pure **author-stream** object; A and B share the author seed
by construction, so B's trait is bit-identical to A's (True) and
swapping the truth side changes nothing.

## 5. The contrast that makes the finding sharp

| phi | card: trait A == B | card: L_C | gauge: common A == B | gauge: R_nat | gauge: R_refresh | gauge: R_nat - R_refresh | gauge truth norm delta |
|---|---|---|---|---|---|---|---|
| 0.05 | True | 0.0 | False | 0.11439067415413948 | 0.0009056149726381045 | 0.1134850591815014 | 57.21695751596421 |
| 0.98 | True | 0.0 | False | 0.1362886208874512 | -0.007950204144913695 | 0.14423882503236488 | 57.362605357119726 |

On the **same pairs**, the gauge behaves completely differently: its b-only
truth is `emit_panel(..., active=("mu","common"))`, which **contains the frame**,
so B's truth panel genuinely differs (True) and R_refresh moves
away from R_nat by 0.12886194210693314 on average. Card layer: 0.7846736299843141 → 0.7846736299843141
at φ = 0.05 (no change at all). Gauge layer: 0.11439067415413948 → 0.0009056149726381045.

**The two layers differ precisely in whether their truth object carries the
frame.** That is the finding.

| aspect | statement |
|---|---|
| **headline** | **the card layer's b-truth is FRAME-FREE BY CONSTRUCTION, so truth-side frame refreshment is a null operation there** |
| reading A (closed form) | under the closed-form reading of appendix N's 0.827 (r_card_b_pred_raw), the statistic is pure algebra with no world, no author and no vectors -- INEXPRESSIBLE flatly, with no truth side to replace |
| reading B (measured) | under the measured reading (r_card_b_raw) the statistic IS expressible as author-indexed vectors and the cross-world path was built and proven bit-exact against k2b -- but its truth side is world['trait'], a pure author-stream object that A and B share bit-identically, so C_ref == C_nat identically and the estimand is degenerate |
| both readings agree on the STOP | True |
| the contrast that makes it sharp | on the SAME pairs the gauge's b-only truth (mu + common) DOES change and R_refresh moves away from R_nat; the two layers differ precisely in whether their truth object carries the frame |
| why it matters | appendix N's ~4.5x gap is not a contest between two readers of one target. The card statistic's target is the person (trait); the gauge's b-only target is person PLUS frame. The taxonomy the Q-line set out to complete is settled by what each layer's truth object contains, and truth-side refreshment cannot be the instrument that settles it |

### 5.1 What this does to appendix N's ~4.5×

The gap is not a contest between two readers of one target. **The card
statistic's target is the person (trait); the gauge's b-only target is person
PLUS frame.** So the Q-line's question — "do card readings transport across
frames?" — cannot be answered by refreshing the truth side, because at the card
layer there is no frame in the truth to refresh. The taxonomy the line set out
to complete is settled by *what each layer's truth object contains*, and this
leg settles it by inspection plus proof rather than by measurement.

Had the leg proceeded, V-Qa would have read POSITIVE and V-Qb NULL, firing cell
4 and publishing *"card reading crosses frames without measurable loss"* as a
measurement. It is an identity. Routing cell 4's consequence is not entailed by
an identity, so the registration's expressibility STOP is the correct exit.

## 6. A measurable neighbour, named not run

| aspect | statement |
|---|---|
| a measurable neighbour | score B's cards against the shared trait and compare to A's -- a frame-sensitivity reading of the card ESTIMATE, which does differ (slow/noise/int are frame-stream). This is a DIFFERENT estimand from the registered truth-side swap and is NAMED, NOT RUN |
| already visible here | the demonstration's per-phi C_nat spread across A-worlds is exactly the within-frame variability that such a reading would formalise |
| **status** | **named for the planner; the executor does not substitute estimands** |

## 7. P3c's values, verified

| quantity | P3c persisted |
|---|---|
| verdict | UNDERPOWERED |
| D_grad | 0.00852887414363202 |
| range_ref | 0.0011121987595310255 |
| range_nat | 0.009641072903163045 |
| R_nat / R_refresh at phi=0.05 | 0.12141191457796047 / -0.0009178005907745429 |
| R_nat / R_refresh at phi=0.98 | 0.1310529874811235 / 0.00019439816875648275 |

## 8. Routing

| # | condition | outcome |
|---|---|---|
| 1 | G0q1/G1q1 failure or INEXPRESSIBLE | **STOP / INEXPRESSIBLE**  <-- THIS LEG |
| 2 | projection fails after escalation | NON_PROJECTABLE |
| 3 | C1'/anchor or C2 battery failure | INSTRUMENT_DEFECT |
| 4 | V-Qa POSITIVE and V-Qb NULL | CARDS_TRANSPORT_FULL -- card reading crosses frames without measurable loss; the taxonomy completes |
| 5 | V-Qa POSITIVE and V-Qb POSITIVE | CARDS_TRANSPORT_PARTIAL -- real transport, real loss |
| 6 | V-Qa NULL | CARDS_FRAME_LOCKED -- the scaffold universality extends to the card layer; major theory note |
| 7 | V-Qa NEGATIVE | CARD_INVERSION_NAMED -- new phenomenon; theory note |
| 8 | any UNDERPOWERED among V-Qa/V-Qb (no higher cell) | UNDERPOWERED (levels and bands reported) |

## 9. Gates

| gate | PASS | detail |
|---|---|---|
| G0q1 | True | P3c's values, the 4.5x operands at source, and the instrument hashes against P3b's persisted sha256s |
| C2 | True | re-run on 4 fresh probe pairs: author objects bit-identical, every frame object differs, determinism, shared basis |
| G1q1b | True | the cross-world path reproduces k2b's own card frame byte-for-byte and its pooled statistic exactly at the zero point |
| G2q1 | None | not reached -- the estimand is degenerate |
| G3q1 | None | not reached |
| C1' | None | not reached; the gauge replication reading is reported descriptively from the demonstration pairs |

## 10. Sides declared (rule 22)

| clause | statement | prior | sided |
|---|---|---|---|
| L-1q1 | CARDS_TRANSPORT_SUBSTANTIAL / CARDS_PARTIAL / CARDS_FRAME_LOCKED / other | 0.40 / 0.35 / 0.15 / 0.10 | categorical |
| V-Qa | C_ref vs 0, NULL-first | — | two-sided |
| V-Qb | L_C = C_nat - C_ref vs 0, NULL-first | — | two-sided |

## 11. Pinned readings

| note | pinned reading |
|---|---|
| RN-Q1-1 | appendix N's 0.827 has TWO persisted readings -- the closed-form prediction r_card_b_pred_raw 0.8271784593117322 (k2b:533-584) and the measured pooled r_card_b_raw 0.8266850143926395 (k2b:392-457 -> :463-489). The companion 0.178 is measured, favouring the second; the digits favour the first. BOTH are pinned and BOTH carried through the expressibility test, because the STOP answer differs between them |
| RN-Q1-2 | the card statistic's truth side is NOT a card: it is world['trait'][idx] (k2b:410), the bare latent trait array. The registration's 'truth-side card panel' names an object that does not exist as a card; the trait array is what can be replaced, and that is what is replaced here |
| RN-Q1-3 | trait_c (k2b:411) feeds BOTH the card (k2b:423) and the centred truth (k2b:444/447); swapping the world wholesale would swap both and give a replication, not a cross-world score. Only the truth-side trait is parameterised; G1q1(b) proves the path by reproducing k2b bit-exactly at the zero point |
| RN-Q1-4 | expressibility is settled by running the cross-world path, not by arguing; the gauge R_nat/R_refresh are computed on the SAME pairs so the two layers are compared on one device in one table |
| RN-Q1-5 | no measurement arm is spent before the expressibility question is answered; the demonstration runs on the pilot salt |

## 12. Rule events

- **Rule 13:** not reached — no verdict boundary exists without a measurement.
- **Rule 25:** not reached; the expressibility clause fires first.
- **Rule 26:** no bounded winner.
- **Rule 27:** no budgeted quantity was consumed.
- **Rule 29:** the domain-pinned predicate was defined for the card cosines and
  is not exercised — no measurement arm ran.
- **Rule 30:** every cited constant read from its persisted source; the card
  statistic carries two source pins and both candidate values.

## 13. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine; a CPython 3.12.12 venv was built outside the repo
   from `requirements-lock-main.txt` verbatim and pinned. Resolved BEFORE any
   hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.

No hypothesis-relevant number was ever computed: the leg stopped before its
first measurement arm, and the demonstration quantities are identities.

## 14. Environment

| component | value |
|---|---|
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| platform | macOS-26.4.1-arm64-arm-64bit |
| python | 3.12.12 |
| python_executable | /private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python |

## 15. Timing

| stage | estimate (s) | measured (s) |
|---|---|---|
| part0 | 150 | 0.606 |
| demonstrate | 60 | 9.843 |
| finalize | 60 | 0.000 |
| pilot / arms / fit | — | -- not reached |

---

*Artifacts: `results/m4_q1_card_transport/` (gitignored) — `part0.json`,
`demonstration.json`, `demonstration.csv`, `decision.json`, `prose_facts.json`,
`report_tables.md`, `run_log.jsonl`. Harness:
`scripts/run_suica_m4_q1_card_transport.py`.*
