# SUICA M4-R1b — clause (iv), re-banded — **IDENTITY_CHANNEL_CERTIFIED**

**Outcome: IDENTITY_CHANNEL_CERTIFIED (routing cell 3).** IDENTITY_CHANNEL_CERTIFIED -- C-R1c closes; with C-R1a/b standing the instrument is certified and R2 becomes registrable

**Measured Δ(w = 0.75) = 0.24614231318551627** [0.24556658406745574, 0.24677281301031784] against a prediction of 0.2476172270351607 and
a corrected band of [0.24311926154851188, 0.25211519252180953] — position **-0.3279068845731195** of the half-width, INSIDE:
**True**. 256 fresh worlds (128 A/B pairs).

The instrument is UNCHANGED. Tier EXPLORATORY, label-free, synthetic. Registered
in `docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md` BEFORE run (commit dec5557).
Every number below is generated from artifacts by code (rule 24).

---

## 1. Why a fresh dose

R1's Δ at w = 0.5 and 1.0 are published, so a re-banded test on those doses
cannot be prospective however honestly it is run — the person deriving the band
can already see the answers. **w = 0.75 has never been measured.** Its
prediction and band were derived from probe worlds, hashed, and stamped before
any fresh-arm world existed (RN-R1B-1/4). R1's doses are re-scored afterwards
under the post-hoc label and route nothing.

| property | value |
|---|---|
| builder | `scripts/run_suica_m4_r1_identity_channel.py:267` (`build_split_world_v2`) |
| R1 function sha256 | 0c9d4c974be0855a4d0c6a654a0bb9f826d2bda7cf2db7880b4c4ecbba02ad48 |
| R1 file sha256 | 4b7f3c1a2db59630bc51168184ea71e8512a9a034c55064f60f15cb4a9b2310f |
| P3b chain hashes match | True |
| w_mu | 0.33541019662496846 (bit-exact: True) |
| injection site | `scripts/run_suica_m4_k2b_t4_branch.py:371` |
| R1 verdict | INSTRUMENT_DEFECT(C-R1c) |
| R1 certificates standing | {'C-R1a': True, 'C-R1b': True, 'C-R1c': False, 'G2r1': True} |
| R1 clause (i) stands (the w = 0 equivalence) | True |

## 2. The corrected band, per defect #61

| term | value | source |
|---|---|---|
| prediction (ratio of means) | 0.2476172270351607 | ratio of means, b/(a+b+d) -- R1's form, unchanged (RN-R1B-3) |
| SE_pred | 0.00045459114785961074 | spread of the algebraic prediction across probe worlds / sqrt(n_probes) |
| SE_meas | 0.0002683462385382117 | per-pair Delta spread across probe pairs / sqrt(128) |
| SE_approx | 0.002186151999363512 | mean over probes of sd_i(b_i/(a_i+b_i+d_i)) / sqrt(n_authors) -- the registration's prescription |
| combined SE | 0.002248982743324414 | sqrt of the sum of squares |
| **half-width** | **0.004497965486648828** | #61: 2*sqrt(SE_pred^2 + SE_meas^2 + SE_approx^2) |
| **band** | **[0.24311926154851188, 0.25211519252180953]** | prediction +/- half-width |
| dominant term | SE_approx | — |
| diagnostic: mean-of-ratios prediction | 0.2504457850274022 | reported, NOT used -- the form is unchanged (RN-R1B-3) |
| diagnostic: form gap | 0.0028285579922415205 | the Jensen/orthogonality gap SE_approx must cover |
| probe pairs / worlds / authors | 16 / 32 / 565 | all pre-measurement (RN-R1B-2) |

All three terms come from **probe worlds** — none from the pilot, which runs
after the stamp (RN-R1B-2). The dominant term is **SE_approx**: SE_pred 0.00045459114785961074,
SE_meas 0.0002683462385382117, SE_approx 0.002186151999363512, combining to 0.002248982743324414 and a half-width of
**0.004497965486648828**.

**The prediction's form is deliberately unchanged** (RN-R1B-3). R1's algebraic
prediction is the ratio-of-means b/(a+b+d), and #61 fixes the *band*, not the
predictor — so keeping the form makes this a test of the convention rather than
of a quietly improved predictor. The per-author form is reported as a
diagnostic: 0.2504457850274022, a gap of 0.0028285579922415205 from the prediction, which is exactly
the Jensen/orthogonality error SE_approx exists to cover.

## 3. Ordering

| quantity | value |
|---|---|
| prediction.json sha256 | dd5912a4c219c651df501488ed3bdcd5455bdb968865579c93f13570fcb57c95 |
| bytes | 9128 |
| stamp UTC | 2026-08-14T08:43:42.897504+00:00 |
| **fresh-arm worlds generated before the stamp** | **0** |
| probe worlds before the stamp (by design) | 32 |
| arm artifact existed at stamp time | False |
| permit UTC | 2026-08-14T08:44:01.203270+00:00 |
| seconds stamp -> permit | 18.305773 |
| permit re-hash matches the stamp | True |

The band was stamped with **0 fresh-arm worlds in existence**, and the
arm refused to run until it re-read the stamp from disk and re-hashed
`prediction.json` to a match (18.305773 s later). Probe worlds necessarily
precede the stamp — they are the band's inputs — and are counted separately.

## 4. The projection

| pairs | truth | role | truth value | SE(mean) | P(contained) | bar | PASS |
|---|---|---|---|---|---|---|---|
| 128 (registered) | algebraic truth | power | 0.2476172270351607 | 0.0002683462385382117 | 1.0 | 0.8 | True |
| 128 (registered) | displaced: prediction - 3.0*band | false-fire | 0.23412333057521423 | 0.0002683462385382117 | 0.0 | 0.1 | True |

At the corrected band's width: containment holds with probability 1.0 at
the algebraic truth (bar 0.8) and only 0.0 at a truth displaced three
band-widths below it (bar 0.1). The band is simultaneously wide enough to accept
the truth and tight enough to reject a displaced one — which is what a
containment test has to be. Escalation did not fire (False).

## 5. The verdict

| quantity | value |
|---|---|
| **measured Delta(0.75)** | **0.24614231318551627** |
| 95% CI | [0.24556658406745574, 0.24677281301031784] |
| SEM | 0.0003013110871435664 |
| prediction | 0.2476172270351607 |
| band | [0.24311926154851188, 0.25211519252180953] |
| half-width | 0.004497965486648828 |
| signed error | -0.0014749138496444325 |
| **position in band** | **-0.3279068845731195** |
| **INSIDE** | **True** |
| distance outside | 0.0 |
| realized ratio-of-means on the arm | 0.2472339809026845 |
| realized mean-of-ratios on the arm | 0.249997832965661 |
| measured - mean-of-ratios | -0.0038555197801447283 |

Measured **0.24614231318551627** [0.24556658406745574, 0.24677281301031784] against prediction 0.2476172270351607: signed error -0.0014749138496444325,
**-0.3279068845731195** of the half-width. **INSIDE = True.**

### 5.1 Is the correction load-bearing, and did the pinned form choice help?

| question | quantity | value |
|---|---|---|
| is SE_approx load-bearing? | residual / SE_approx | -0.6746620775105513 |
|  | residual / SEM of the measurement | -4.8949869838067945 |
|  | R1-style half-width, 2*sqrt(SE_pred^2 + SE_meas^2) | 0.0010557704588591693 |
|  | **would this leg PASS under R1's band form?** | **False** |
|  | position under R1's band form | -1.3970023855736367 |
| did the pinned form choice help? | realized ratio-of-means on the arm | 0.2472339809026845 |
|  | realized mean-of-ratios on the arm | 0.249997832965661 |
|  | residual vs the arm's ratio-of-means | -0.001091667717168232 |
|  | residual vs the arm's mean-of-ratios | -0.0038555197801447283 |
|  | position had the mean-of-ratios form been stamped | -0.8571697118594949 |
|  | would the alternative form still PASS? | True |

Two things a reader is owed, and neither is flattering by construction.

**SE_approx is load-bearing.** The residual is -0.6746620775105513 of SE_approx — but
-4.8949869838067945 of the measurement's own SEM. The measurement is far more precise than
the prediction is accurate, which is the entire content of defect #61. Under
R1's band form — 2·√(SE_pred² + SE_meas²), half-width 0.0010557704588591693 — this leg
would have landed at -1.3970023855736367 and **PASSED = False**. The identical
failure would have recurred at a fresh dose. The correction is not cosmetic.

**The pre-pinned form choice was the favourable one, and I did not know that
when I pinned it.** RN-R1B-3 kept R1's ratio-of-means, and Part 0 named the
mean-of-ratios as "what the measurement actually estimates". It is not: the
measurement sits below *both* forms — -0.0014749138496444325 from the stamped ratio-of-means
and -0.0038555197801447283 from the arm's mean-of-ratios (0.249997832965661). Had the mean-of-ratios
been stamped instead, the position would have been -0.8571697118594949 — still inside
(True), but near the edge. So the containment verdict is robust to the
form choice, while the comfort of the margin is not. The residual is therefore
**not** the Jensen form gap; it runs the other way and is larger, and SE_approx
covers it because that spread sets the right *scale* for the derivation's error,
not because it names its mechanism.

## 6. Secondary — R1's doses re-scored (post-hoc, adjudicating nothing)

| R1 dose | R1 measured | R1 predicted | gap | this leg's half-width | would be inside | label |
|---|---|---|---|---|---|---|
| 0.5 | 0.1273886225517469 | 0.12739898980740494 | -1.0367255658033647e-05 | 0.004497965486648828 | True | re-scored against THIS leg's corrected half-width; POST-HOC, adjudicates nothing (RN-R1B-1) |
| 1.0 | 0.36609324420972367 | 0.3695134875442334 | -0.0034202433345097427 | 0.004497965486648828 | True | re-scored against THIS leg's corrected half-width; POST-HOC, adjudicates nothing (RN-R1B-1) |

Reported as consistency readings only. The registration is explicit that these
cannot adjudicate, and the routing uses w = 0.75 alone.

## 7. Routing

| # | condition | outcome |
|---|---|---|
| 1 | G0 / hash mismatch | STOP |
| 2 | projection fails after escalation | NON_PROJECTABLE |
| 3 | V-R1b inside the corrected band | **IDENTITY_CHANNEL_CERTIFIED -- C-R1c closes; with C-R1a/b standing the instrument is certified and R2 becomes registrable**  <-- THIS LEG |
| 4 | V-R1b outside | BAND_STILL_WRONG -- the derivation error model is inadequate; handback with the realized decomposition |

## 8. Gates

| gate | PASS | detail |
|---|---|---|
| G0 | True | instrument unchanged: R1 builder hashes recorded, the P3b chain verified, w_mu bit-exact, R1's C-R1a/C-R1b and clause (i) standing |
| G2r1b | True | rule-29 predicate; pilot AFTER the stamp |
| G3r1b | True | escalation fired: False |
| V-R1b | True | prospective containment at the fresh dose w = 0.75 |

## 9. Sides declared (rule 22)

| clause | statement | prior | sided |
|---|---|---|---|
| G3r1b | power >= 0.8 at the algebraic truth and false-fire <= 0.1 at prediction - 3.0*band | — | one-sided each |
| V-R1b | measured Delta(0.75) inside the corrected band | 0.7 | two-sided containment |

## 10. Pinned readings

| note | pinned reading |
|---|---|
| RN-R1B-1 | the primary is a FRESH dose (w = 0.75, never measured) because R1's doses are published and a re-banded test on them cannot be prospective; R1's doses are re-scored afterwards with the post-hoc label and the routing uses w = 0.75 alone |
| RN-R1B-2 | all three SE terms come from PROBE worlds, never the pilot (which runs after the stamp): SE_pred from the prediction's spread across probes, SE_approx from sd_i(b_i/(a_i+b_i+d_i))/sqrt(n_authors) per the registration, SE_meas from the per-pair Delta spread across probe pairs |
| RN-R1B-3 | the prediction's FORM is unchanged (ratio-of-means, as R1) because #61 fixes the band, not the predictor; the per-author form is reported as a diagnostic since the gap between them is what SE_approx must cover |
| RN-R1B-4 | K2f ordering: prediction.json is hashed and stamped before any fresh-arm world exists, the arm re-reads the stamp from disk and re-hashes to a match, and the pilot runs after the stamp; probe worlds precede the stamp by design and are counted separately |
| RN-R1B-5 | BAND_STILL_WRONG is live and would mean the #61 error model is inadequate, not that the channel is absent; R1's other four certificates stand regardless |

## 11. Rule events

- **Rule 13:** no verdict sits near a boundary in the bootstrap tail sense; the
  containment call is at -0.3279068845731195 of the half-width.
- **Rule 25:** the projection gate passed at the registered size.
- **Rule 26:** no bounded winner.
- **Rule 29:** the domain-pinned predicate ran on the pilot and the arm.
- **Rule 30:** the band's three terms are all MEASURED on probe worlds and
  persisted before the arm; the instrument's hashes are verified at source.
- **Rule 31/32 family (#61):** the convention under test — a containment band
  carries 2·√(SE_pred² + SE_meas² + SE_approx²), and the deterministic w = 0
  point is tested by equivalence (R1's clause (i)), never containment.

## 12. What this settles

With C-R1a, C-R1b and R1's clauses (i)–(iii) standing, and clause (iv) now
tested prospectively at a dose never previously measured, **the identity channel
is certified**: planted, inert at zero, author-stream, trait-independent,
card-visible, monotone in dose, and quantitatively recoverable inside a band
derived before the measurement existed.

What it does **not** settle: nothing about the k2b family's own worlds. The
channel is planted, not discovered; appendix KK's structural boundary is
unmoved. This buys the ability to ask the founding question, not an answer to it.

## 13. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine; a CPython 3.12.12 venv was built outside the repo
   from `requirements-lock-main.txt` verbatim and pinned. Resolved BEFORE any
   hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.
3. **A-3 (my own report prose was wrong; AFTER the verdict existed).** The
   report template — written before the run — asserted that the measurement
   would sit closer to the per-author mean-of-ratios, that being "what the
   measurement actually estimates" (Part 0's own words). The data contradict it:
   the measurement is -0.0038555197801447283 from the mean-of-ratios and only -0.0014749138496444325 from the
   stamped ratio-of-means, so the pre-pinned form was the *closer* one. The
   sentence was replaced with §5.1's generated decomposition, which reports the
   contradiction and the counterfactual position under the alternative form.
   This was discovered and corrected AFTER the containment verdict existed. It
   changed no number: `prediction.json` is untouched and still re-hashes to the
   stamp dd5912a4c219c651, the band, the routing and the verdict are as computed. What
   changed is that a claim I could not support was removed.

## 14. Environment

| component | value |
|---|---|
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| platform | macOS-26.4.1-arm64-arm-64bit |
| python | 3.12.12 |
| python_executable | /private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python |
| scipy | 1.17.1 |

## 15. Timing

| stage | estimate (s) | measured (s) |
|---|---|---|
| part0 (band + stamp) | 120 | 1.156 |
| pilot | 30 | 0.587 |
| project | 20 | 0.000 |
| arm | 120 | 6.140 |
| fit | 60 | 0.004 |
| finalize | 30 | 0.000 |

---

*Artifacts: `results/m4_r1b_reband/` (gitignored) — `part0.json`,
`prediction.json`, `prediction.sha256.json`, `pilot.json`, `pilot_field.csv`,
`projection.json`, `arm.csv`, `arm_permit.json`, `fit.json`, `decision.json`,
`prose_facts.json`, `report_tables.md`, `run_log.jsonl`. Harness:
`scripts/run_suica_m4_r1b_reband.py`.*
