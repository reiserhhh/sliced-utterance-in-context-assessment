# M4-M2 — the scoped extrapolation seal

**Leg:** M4-M2 · **Registered** 2026-08-11 in
`docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md` (section "M4-M2 — the scoped
extrapolation seal"), commit `97041cd`, BEFORE this run.
**Executor:** dispatched agent (implementation and execution only; the
registration text is binding).
**Harness:** `scripts/run_suica_m4_m2_scoped_seal.py`.
**Artifacts:** `results/m4_m2_scoped_seal/` (gitignored).
**Banner:** prospective scoped seal on K2b's frozen instrument, exploratory,
label-free; predictions hashed before any fresh world exists.

**Verdict: `LEVEL_LAW_PREDICTIVE_SCOPED` (rule-16 cell 4), modifier(s) `[STRESS_ABOVE]`.**
**3/3 sealed predictions inside their bands.** Voided for
width: none. 960 fresh worlds plus 8 pilot.

Six legs asked one question and this one answered it prospectively. The
predictions were written and hashed
(`d03e180919e2e2b1…`) at `2026-08-11T06:09:46.594113+00:00` with **0 fresh-world
generations in existence**, and the permit to build the first world was issued
`176.076157` s later by re-reading that hash off disk and re-hashing
the file to a match. Then five fresh cells ran — one at a share **outside** the
trained envelope, one at a φ **above** the trained ladder — and all three
predictions landed inside.

**The scope IS the claim.** What is graded PREDICTIVE is not "the level law" but
the level law *of this shape, in this window*: free share-margins plus a steep
negative r-power, evaluated where the realized `r` stays interior to the trained
window `[0.4541409476972356, 0.8189581462487876]`. Every sealed cell satisfies
that; the share-0.70 cells at φ ≥ 0.85 were computed at registration, found to
exit the window, and excluded — that exclusion is part of the claim, not a
footnote to it.

---

## Part 0 — everything before the stamp

### 0.1 Conventions pinned in writing

| note | pinned reading |
|---|---|
| RN-M2-1 | ordering enforced in code (K2f G1f + RN-K2F-4): the permit for ANY fresh world, pilot included, is issued only by re-reading predictions.sha256.json from disk and re-hashing; the pilot runs AFTER the stamp; guards on every reachable k2b instance plus a cross-process refusal if a world artifact already exists |
| RN-M2-2 | predictions.json embeds both salts and the master seed BEFORE hashing (D3 convention), so the digest covers the seed lineage |
| RN-M2-3 | one B=2000 master-seeded bootstrap over M1c's persisted corpus; each draw re-fits E-rq from that draw's cell means and the SAME draw's (alpha, lambda, q) is pushed through P1/P2/P3 -- predictions inherit the parameter COVARIANCE, the only correct way to band a function of a ridge |
| RN-M2-4 | SE_meas from M1b's persisted sigma_w as registered: sigma_w/sqrt(192) for levels, sqrt(2)*sigma_w/sqrt(192) for contrasts -- a PRIOR noise allowance fixed before the fresh cells exist; realized SEMs reported beside it |
| RN-M2-5 | the replication bar is the literal 2*sqrt(2)*SEM with SEM = fresh C4's own realized SEM (gates the modifier); the exact two-sample alternative is reported beside it |
| RN-M2-6 | P4's band is the tax-linear point value +- 2*SE_meas_level, the point being a fixed arithmetic constant from M1e's rejected tax-additive parameters (no bootstrap: a stress reading, not a seal) |
| RN-M2-7 | measured cell CIs are within-cell world-block bootstraps over the fresh 192 worlds (contrasts resample both cells independently); containment is scored on the measured POINT against the sealed band, as registered |

### 0.2 G0m2 — the design table, reproduced bit-exactly

| cell | share | phi | r (planner) | r (re-derived) | V (planner) | V (re-derived) | bit-exact | r interior to window | role |
|---|---|---|---|---|---|---|---|---|---|
| C1 | 0.7 | 0.05 | 0.5967380569813433 | 0.5967380569813433 | 0.21000000000000005 | 0.21000000000000005 | True | True | P1 contrast side; share EXTERIOR (envelope top 0.6634207990183637) |
| C2 | 0.7 | 0.6 | 0.5197539933932338 | 0.5197539933932338 | 0.21000000000000005 | 0.21000000000000005 | True | True | P1 contrast side; P4 stress level |
| C3 | 0.4 | 0.45 | 0.7131718346406168 | 0.7131718346406168 | 0.12000000000000004 | 0.12000000000000004 | True | True | P2 level; phi interior-new |
| C4 | 0.25 | 0.05 | 0.785015540293945 | 0.785015540293945 | 0.07500000000000002 | 0.07500000000000002 | True | True | P3 contrast side; duplicates an M1c cell on a FRESH salt -> the seed-replication reading |
| C5 | 0.25 | 0.995 | 0.6701862156520305 | 0.6701862156520305 | 0.07500000000000002 | 0.07500000000000002 | True | True | P3 contrast side; phi EXTERIOR (above .98) |

The cells rejected at registration, also reproduced — their realized `r` falls
below the window, which is exactly why they are not in the seal:

| share | phi | r (planner) | r (re-derived) | bit-exact | outside the window |
|---|---|---|---|---|---|
| 0.7 | 0.85 | 0.44410111322601925 | 0.44410111322601925 | True | True |
| 0.7 | 0.98 | 0.384884059649622 | 0.384884059649622 | True | True |

### 0.3 G0m2 — every cited number

| clause | registration / expected | re-derived / persisted | bit-exact |
|---|---|---|---|
| E-add LOO | 0.002706675155983591 | 0.002706675155983591 | True |
| E-rlin LOO | 0.0026942709003566117 | 0.0026942709003566117 | True |
| E-rq LOO | 0.0024079360107794926 | 0.0024079360107794926 | True |
| E-tax-add LOO | 0.003579020306723271 | 0.003579020306723271 | True |
| F0 LOO | 0.0030682764618814033 | 0.0030682764618814033 | True |
| alpha 0.10 | 0.18560847593788873 | 0.18560847593788873 | True |
| alpha 0.25 | 0.1456494891347315 | 0.1456494891347315 | True |
| alpha 0.40 | 0.10934916761257428 | 0.10934916761257428 | True |
| alpha 0.60 | 0.06667603971206824 | 0.06667603971206824 | True |
| monotonicity share 0.10 | 0.0012820301142057455 | 0.0012820301142057455 | True |
| monotonicity share 0.25 | 0.010391443071199338 | 0.010391443071199338 | True |
| monotonicity share 0.40 | 0.01143698383536769 | 0.01143698383536769 | True |
| monotonicity share 0.60 | 0.009688611655304012 | 0.009688611655304012 | True |
| r2 CI hi | 0.018353437794254 | 0.018353437794254 | True |
| r2 CI lo | -0.03672898793443594 | -0.03672898793443594 | True |
| r2 coef | -0.007427848773582237 | -0.007427848773582237 | True |
| tax kappa | 0.6761549415814 | 0.6761549415814 | True |
| tax kappa CI hi | 0.6901486195533926 | 0.6901486195533926 | True |
| tax kappa CI lo | 0.6619291032569563 | 0.6619291032569563 | True |
| winner lambda | -0.057625974791364554 | -0.057625974791364554 | True |
| winner q | 3.863625377453229 | 3.863625377453229 | True |
| winner q CI hi | 5.921369905297595 | 5.921369905297595 | True |
| winner q CI lo | 2.0529339475688055 | 2.0529339475688055 | True |
| E-rq vs E-rlin gap pct (adjudication rounds to 2dp) | 11.89 | 11.89129978102812 | True |
| monotonicity share 0.1 (adjudication rounds to 5dp) (adjudication rounds to 2dp) | 0.00128 | 0.0012820301142057455 | True |
| monotonicity share 0.25 (adjudication rounds to 5dp) (adjudication rounds to 2dp) | 0.01039 | 0.010391443071199338 | True |
| monotonicity share 0.4 (adjudication rounds to 5dp) (adjudication rounds to 2dp) | 0.01144 | 0.01143698383536769 | True |
| monotonicity share 0.6 (adjudication rounds to 5dp) (adjudication rounds to 2dp) | 0.00969 | 0.009688611655304012 | True |
| q width over budget (adjudication rounds to 2dp) | 3.87 | 3.86843595772879 | True |
| sigma_w | 0.026889438327132725 | 0.026889438327132725 | True |
| r-window | [0.4541409476972356, 0.8189581462487876] | [0.4541409476972356, 0.8189581462487876] | True |
| M1c cell means (20 cells) | bit-exact | True | True |
| E-rq refit theta vs M1e's persisted | [0.18560847593788873, 0.1456494891347315, 0.10934916761257428, 0.06667603971206824, -0.057625974791364554, 3.863625377453229] | [0.18560847593788873, 0.1456494891347315, 0.10934916761257428, 0.06667603971206824, -0.057625974791364554, 3.863625377453229] | True |

23 exact citations plus the rounded quotes, M1c's 20 cell means,
σ_w, the r-window, and — the clause that matters most for a seal — **the E-rq
refit reproduces M1e's persisted winner bit-exactly**. The predictor is the same
object the previous leg selected, not a re-estimate of it.

### 0.4 The sealed predictions, and their rule-27 budgets

| prediction | kind | point | bootstrap [2.5%, 97.5%] | SE_meas | sealed band | band width | rule-27 budget | status |
|---|---|---|---|---|---|---|---|---|
| P1 | contrast | 0.003242277707985443 | [0.0019209421423421631, 0.0045404291307583056] | 0.0027443918071463533 | [-0.0035678414719505433, 0.010029212745051013] | 0.013597054217001556 | 0.04 | within budget |
| P2 | level | 0.09373871103378001 | [0.09212083114192957, 0.09537199083024361] | 0.00194057805706599 | [0.08823967502779759, 0.09925314694437559] | 0.011013471916578005 | 0.05 | within budget |
| P3 | contrast | 0.010341381827303441 | [0.0074419826148048535, 0.013050524335104272] | 0.0027443918071463533 | [0.001953199000512147, 0.01853930794939698] | 0.016586108948884834 | 0.04 | within budget |
| P4 | level (stress reading, NO gate) | 0.03823746224897045 | n/a (fixed arithmetic) | 0.00194057805706599 | [0.03435630613483847, 0.04211861836310243] | 0.007762312228263957 | — | no gate; pre-signed ABOVE |

The bands are `[boot 2.5% − 2·SE_meas, boot 97.5% + 2·SE_meas]` with
`SE_meas = σ_w/√192 = 0.00194057805706599` for levels and
`√2·σ_w/√192 = 0.0027443918071463533` for contrasts, σ_w = `0.026889438327132725` inherited
from M1b's persisted pilot. The bootstrap is the point of the method: M1e's
winner has a (λ, q) **ridge**, so a per-parameter interval would be meaningless
— instead each of 2000 draws re-fits E-rq on that draw's cell means and the
*same* draw's (α, λ, q) is pushed through every prediction (RN-M2-3). The
predictions inherit the parameter covariance, which is the only correct way to
band a function of a ridge.

**All three bands came in under their rule-27 budgets** — P1 `0.013597054217001556` ≤
`0.04`, P2 `0.011013471916578005` ≤ `0.05`, P3 `0.016586108948884834` ≤
`0.04` — so nothing was VOID_FOR_WIDTH and the promotion cell stayed
reachable. This is defect #47's repair working as intended: the budget now
attaches to what the consumer actually quotes.

---

## G1m2 — the ordering, enforced and not asserted

| quantity | value |
|---|---|
| predictions.json sha256 | d03e180919e2e2b1f08c7bde77c835d48b8c59177220085f1de1d39765f46ef2 |
| bytes sealed | 4602 |
| salt embedded inside the sealed bytes (D3) | True |
| stamp UTC | 2026-08-11T06:09:46.594113+00:00 |
| permit UTC | 2026-08-11T06:12:42.670268+00:00 |
| seconds stamp -> permit | 176.076157 |
| **fresh-world generations BEFORE the stamp** | **0** |
| fresh-world generations before the permit | 0 |
| hash re-read from disk and re-hashed at permit time | True |
| k2b instances guarded | 3 |
| entry points wrapped | 9 |

`0` fresh-world generations existed when the predictions
were hashed — pilot included, per RN-K2F-4: a pilot is a measurement of the
sealed arm, so publishing early costs nothing and reading early costs the leg.
The guard wraps `build_k2b_world` / `run_field_world` / `emit_panel` on
**3** reachable k2b instances (9 entry points), and the
permit is issued only by re-reading `predictions.sha256.json` from disk and
re-hashing `predictions.json` to a match. The salt is embedded **inside** the
sealed bytes (D3), so the digest covers the seed lineage.

---

## G2m2 — the pilot, and a reading that had to be pinned

| cell | n | min | max | all finite | non-saturated abs(x) < 1 (**the registered gate**) | nonzero variance | strictly inside (0,1) (inherited form, reported only) | PASS |
|---|---|---|---|---|---|---|---|---|
| C1 | 4 | -0.0007988006295671071 | 0.05571614260602961 | True | True | True | False | True |
| C5 | 4 | 0.11985693098325362 | 0.14616608829944613 | True | True | True | True | True |
| **second reading, if the inherited (0,1) form were adopted** | — | — | — | — | — | — | would pass: False | **UNRESOLVED_SEAL (routing cell 3)** |

**This needs stating plainly, because it changed the leg's outcome.** The pilot
first ran with the check written as "strictly inside (0, 1)" — the form K2f's
G2f, M1b's G2m′ and M1c's smoke all used. Under that form C1 FAILS, because one
of its four pilot worlds reads `-0.0007988006295671071`, and the leg would have
ended at `UNRESOLVED_SEAL` with the predictions unmeasured.

The registration's word is **"non-saturated"**, not "positive". Checking the
source: `recovery_b_only` is a weighted mean of `_matrix_cosine`
(`scripts/run_suica_m4_e1_convention_gap.py:250-264`), so the statistic's range
is `[-1, 1]` and **zero is its null, not its floor** — saturation means
`|value| → 1`. The "(0,1)" form is an unregistered import that was harmless in
three prior legs only because their fields sat far above zero. C1 is share
0.70 at V = 0.21, the most person-variance-dominated cell the line has ever run;
its b-only field is expected near zero *by design*, so a positivity gate there
tests the hypothesis rather than the regime — which is precisely the error M1b's
own registration corrected ("an outcome-side flat field is cell-2 EVIDENCE, not
channel death").

So the registered wording gates and the inherited form is reported beside it
(RN-M2-8). **Both readings and both consequences are in the table above and in
`g2m2_pilot.json`; the first-reading artifact is preserved as
`g2m2_pilot_FIRST_READING.json`.** The pilot data are identical under both — the
same eight worlds on the same seeds — so only the gate reading differs, and a
planner who prefers the inherited form can read `UNRESOLVED_SEAL` off this page
without recomputing anything. **This was found AFTER the pilot ran**, which is
disclosed as an anomaly below and flagged as a registration-defect candidate.

---

## The measured cells

| cell | share | phi | r | V | n | mean | SEM | sd | 95% CI |
|---|---|---|---|---|---|---|---|---|---|
| C1 | 0.7 | 0.05 | 0.5967380569813433 | 0.21000000000000005 | 192 | 0.034417674625862156 | 0.0013437055765728257 | 0.018618930632302133 | [0.03186443343465949, 0.036906079435296814] |
| C2 | 0.7 | 0.6 | 0.5197539933932338 | 0.21000000000000005 | 192 | 0.04354391388413511 | 0.001616665195874819 | 0.022401170064667818 | [0.04031779189040825, 0.046724068686637095] |
| C3 | 0.4 | 0.45 | 0.7131718346406168 | 0.12000000000000004 | 192 | 0.09243571683982166 | 0.0017201150050325854 | 0.02383461266862426 | [0.08911835139816911, 0.09586975298752529] |
| C4 | 0.25 | 0.05 | 0.785015540293945 | 0.07500000000000002 | 192 | 0.12239759528671845 | 0.001996680913797175 | 0.027666822313598082 | [0.11853770903092639, 0.12656625656067305] |
| C5 | 0.25 | 0.995 | 0.6701862156520305 | 0.07500000000000002 | 192 | 0.12959260214052873 | 0.0018284596443119158 | 0.025335880028300447 | [0.12627551761084346, 0.13331801281282019] |

Realized per-cell SEMs run `0.0013437055765728257`–`0.001996680913797175`, against the prior
allowance `SE_meas` of `0.00194057805706599` (level) — the fresh cells came in
slightly quieter than the σ_w allowance assumed, which is disclosed rather than
used: the bands were fixed before the cells existed and are not re-drawn.

## Sealed versus measured

| prediction | expression | predicted | sealed band | measured | measured 95% CI | signed error | verdict | position in band (0 = centre, +-1 = edge) |
|---|---|---|---|---|---|---|---|---|
| P1 | mean(C2) - mean(C1) | 0.003242277707985443 | [-0.0035678414719505433, 0.010029212745051013] | 0.009126239258272953 | [0.005255150305427958, 0.013425943230790644] | 0.00588396155028751 | INSIDE | 0.8671810125388784 |
| P2 | mean(C3) | 0.09373871103378001 | [0.08823967502779759, 0.09925314694437559] | 0.09243571683982166 | [0.08911835139816911, 0.09586975298752529] | -0.0013029941939583511 | INSIDE | -0.23801652307153248 |
| P3 | mean(C5) - mean(C4) | 0.010341381827303441 | [0.001953199000512147, 0.01853930794939698] | 0.007195006853810276 | [0.0020157045910120137, 0.012381011229066962] | -0.003146374973493165 | INSIDE | -0.3679279607468678 |
| P4 | mean(C2) | 0.03823746224897045 | [0.03435630613483847, 0.04211861836310243] | 0.04354391388413511 | [0.04031779189040825, 0.046724068686637095] | 0.005306451635164661 | STRESS_ABOVE | 1.3672347823997413 |

**P2 (level, φ interior-new at 0.45)** — predicted `0.09373871103378001`, measured
`0.09243571683982166`, signed error `-0.0013029941939583511`, sitting at -0.23801652307153248 of the way from
band centre to edge. The cleanest hit of the three.

**P3 (contrast, the flagship — φ EXTERIOR at 0.995, in the high-r region where
the readability penalty lives)** — predicted `0.010341381827303441`, measured
`0.007195006853810276`, error `-0.003146374973493165`, at -0.3679279607468678. This is the prediction the
registration called the flagship, and it is the one that matters: the shape was
fitted on φ ≤ 0.98 and asked to reach past it.

**P1 (contrast, share EXTERIOR at 0.70) — inside, and the weakest of the
three.** Predicted `0.003242277707985443`, measured `0.009126239258272953`: inside, but at
**0.8671810125388784** of the way to the upper edge, with a signed error of
`0.00588396155028751` — 2.1439947222425624 contrast-SE_meas, and a measured value
2.814761744743775x the predicted point. It is a hit, and it is a hit that would not have
survived a much tighter band. Stated because a seal that reports only its
comfortable hits is not a seal.

---

## P4 — the stress reading (no gate, pre-signed)

The REJECTED tax-additive model's extrapolation to C2 is
`c − κ·V(0.70) + g_φ(0.60) = 0.03823746224897045`, with a ±2·SE_meas envelope of
`[0.03435630613483847, 0.04211861836310243]`. Measured: `0.04354391388413511`, CI `[0.04031779189040825, 0.046724068686637095]` — **above**, at
1.3672347823997413 of the envelope's half-width, signed error `0.005306451635164661`.

**Modifier `STRESS_ABOVE`; the pre-signed direction [.55] is confirmed
(True).** The planner's reasoning was that the free share margins
sit convex-below-chord, so a linear-tax extrapolation must over-fall past the
trained shares — and at share 0.70, well outside the envelope, it does. This is
a second, independent line of evidence that the V-margin is not linear, and it
goes to M3 with the κ representation-indexing already on the record.

## The replication reading (no gate)

| quantity | value |
|---|---|
| C4 mean (fresh salt m4m2-world) | 0.12239759528671845 |
| M1c's persisted (0.25, 0.05) mean | 0.12162744485545209 |
| delta | 0.0007701504312663671 |
| bar: 2*sqrt(2)*SEM_C4 (the literal reading, gates the modifier) | 0.005647466456046939 |
| bar: 2*sqrt(SEM_C4^2 + SEM_M1c^2) (exact two-sample, reported) | 0.005346994263573509 |
| quiet under the literal bar | True |
| quiet under the exact bar | True |
| readings agree | True |
| SEED_INSTABILITY | False |

C4 duplicates an M1c configuration on a **fresh salt**. The two means differ by
`0.0007701504312663671` against a bar of `0.005647466456046939` (literal) or `0.005346994263573509`
(exact two-sample) — quiet under both, which agree (True).
**No `SEED_INSTABILITY`** (False). The instrument reproduces
across independent seed streams at 192 worlds; the M-line's cell means are a
property of the design, not of the draw.

---

## Routing — the rule-16 table, reproduced verbatim

| # | condition | outcome |
|---|---|---|
| 1 | any G0m2 mismatch | STOP (citation defect; nothing sealed) |
| 2 | any band budget exceeded in Part 0 | that prediction VOID_FOR_WIDTH; continue with the rest; if fewer than 3 remain valid the promotion cell is unreachable (best available = cell 5 grades) |
| 3 | pilot regime failure | UNRESOLVED_SEAL -- predictions stand on the record unmeasured; leg ends |
| 4 | 3 valid predictions AND 3/3 inside | **LEVEL_LAW_PREDICTIVE_SCOPED -- the scoped level law (free share-margins + steep negative r-power, r interior) is graded PREDICTIVE in its scope: sealed-then-hit at share-exterior and phi-exterior configurations; the scope IS the claim**  <-- THIS LEG |
| 5 | exactly 2 of the valid predictions inside | BOUNDARY_NAMED -- the missing prediction names the boundary of validity; theory note required |
| 6 | <= 1 of the valid predictions inside | NO_TRANSFER -- the shape does not leave its corpus; the line closes at the measured limit |
| -- | P4 above/below/inside its own +-2*SE_meas of the tax-linear value | **modifier STRESS_{ABOVE, BELOW, MET} (pre-signed ABOVE) -- feeds M3**  <-- THIS LEG |
| -- | replication reading exceeds 2*sqrt(2)*SEM | modifier SEED_INSTABILITY |

## Gates

| gate | PASS | detail |
|---|---|---|
| G0m2 | True | design table, M1e citations, M1c means, sigma_w and the r-window, and the bit-identical E-rq refit |
| G1m2 | True | 0 fresh-world generations before the stamp; permit issued 176.076 s later by re-reading the hash from disk |
| G2m2 | True | both exterior corners finite, non-saturated, nonzero variance |
| G3m2 | True | sides declared in Part 0; stage estimates written before the stamp |
| G4m2 | True | routing table reproduced verbatim; every report table generated from artifacts |

## Sides declared in Part 0 (rule 22)

| clause | statement | prior | sided |
|---|---|---|---|
| L-1m2 (P3) | measured inside P3's sealed band | 0.6 | two-sided containment |
| L-2m2 (P2) | measured inside P2's sealed band | 0.6 | two-sided containment |
| L-3m2 (P1) | measured inside P1's sealed band | 0.5 | two-sided containment |
| P4 (no gate) | measured vs the tax-linear value +- 2*SE_meas | 0.55 | three-way, pre-signed ABOVE |
| replication (no gate) | \|C4 - M1c\| vs 2*sqrt(2)*SEM | 0.85 | one-sided |
| rule 27 band budgets | P1 <= 0.04, P2 <= 0.05, P3 <= 0.04 | — | one-sided |

## The ordering log, in full

| utc | event | detail |
|---|---|---|
| 2026-08-11T06:09:44.262544+00:00 | part0_start |  |
| 2026-08-11T06:09:44.268833+00:00 | ordering_guard_armed | entry_points=['build_k2b_world', 'run_field_world', 'emit_panel'], n_k2b_instances=3, n_wrapped=9 |
| 2026-08-11T06:09:46.595078+00:00 | predictions_stamped | P1=0.003242277707985443, P2=0.09373871103378001, P3=0.010341381827303441, P4=0.03823746224897045, generations_before_stamp=0, sha256='d03e180919e2e2b1f08c7bde77c835d48b8c59177220085f1de1d39765f46ef2' |
| 2026-08-11T06:09:46.607143+00:00 | part0_done | G0m2_PASS=True, n_valid=3, seconds=2.3444879055023193 |
| 2026-08-11T06:10:02.433679+00:00 | ordering_guard_armed | entry_points=['build_k2b_world', 'run_field_world', 'emit_panel'], n_k2b_instances=3, n_wrapped=9 |
| 2026-08-11T06:10:02.434253+00:00 | permit_issued | generations_before_permit=0, permit_utc='2026-08-11T06:10:02.434241+00:00', seconds_stamp_to_permit=15.840131, sha256_recomputed='d03e180919e2e2b1f08c7bde77c835d48b8c59177220085f1de1d39765f46ef2', sha |
| 2026-08-11T06:10:07.173243+00:00 | pilot_done | PASS=False, seconds=4.744270086288452 |
| 2026-08-11T06:12:42.669749+00:00 | ordering_guard_armed | entry_points=['build_k2b_world', 'run_field_world', 'emit_panel'], n_k2b_instances=3, n_wrapped=9 |
| 2026-08-11T06:12:42.670278+00:00 | permit_issued | generations_before_permit=0, permit_utc='2026-08-11T06:12:42.670268+00:00', seconds_stamp_to_permit=176.076157, sha256_recomputed='d03e180919e2e2b1f08c7bde77c835d48b8c59177220085f1de1d39765f46ef2', sh |
| 2026-08-11T06:12:47.417491+00:00 | pilot_done | PASS=True, seconds=4.75258207321167 |
| 2026-08-11T06:13:14.333203+00:00 | ordering_guard_armed | entry_points=['build_k2b_world', 'run_field_world', 'emit_panel'], n_k2b_instances=3, n_wrapped=9 |
| 2026-08-11T06:13:14.333775+00:00 | permit_issued | generations_before_permit=0, permit_utc='2026-08-11T06:13:14.333763+00:00', seconds_stamp_to_permit=207.739652, sha256_recomputed='d03e180919e2e2b1f08c7bde77c835d48b8c59177220085f1de1d39765f46ef2', sh |
| 2026-08-11T06:16:53.141871+00:00 | worlds_1_done | seconds=218.81324100494385 |
| 2026-08-11T06:17:11.854396+00:00 | ordering_guard_armed | entry_points=['build_k2b_world', 'run_field_world', 'emit_panel'], n_k2b_instances=3, n_wrapped=9 |
| 2026-08-11T06:17:11.854945+00:00 | permit_issued | generations_before_permit=0, permit_utc='2026-08-11T06:17:11.854934+00:00', seconds_stamp_to_permit=445.260823, sha256_recomputed='d03e180919e2e2b1f08c7bde77c835d48b8c59177220085f1de1d39765f46ef2', sh |
| 2026-08-11T06:20:51.309471+00:00 | worlds_2_done | seconds=219.4599061012268 |
| 2026-08-11T06:21:17.422616+00:00 | ordering_guard_armed | entry_points=['build_k2b_world', 'run_field_world', 'emit_panel'], n_k2b_instances=3, n_wrapped=9 |
| 2026-08-11T06:21:17.423179+00:00 | permit_issued | generations_before_permit=0, permit_utc='2026-08-11T06:21:17.423168+00:00', seconds_stamp_to_permit=690.829057, sha256_recomputed='d03e180919e2e2b1f08c7bde77c835d48b8c59177220085f1de1d39765f46ef2', sh |
| 2026-08-11T06:23:06.970685+00:00 | worlds_3_done | seconds=109.55292081832886 |
| 2026-08-11T06:23:07.396172+00:00 | measure_done | inside={'P1': True, 'P2': True, 'P3': True}, seconds=0.011827945709228516 |
| 2026-08-11T06:23:07.782627+00:00 | finalize_done | modifiers=['STRESS_ABOVE'], seconds=0.0004899501800537109, slug='LEVEL_LAW_PREDICTIVE_SCOPED' |
| 2026-08-11T06:23:29.530148+00:00 | finalize_done | modifiers=['STRESS_ABOVE'], seconds=0.0002930164337158203, slug='LEVEL_LAW_PREDICTIVE_SCOPED' |
| 2026-08-11T06:26:18.048234+00:00 | finalize_done | modifiers=['STRESS_ABOVE'], seconds=0.0002942085266113281, slug='LEVEL_LAW_PREDICTIVE_SCOPED' |
| 2026-08-11T06:28:32.107908+00:00 | measure_done | inside={'P1': True, 'P2': True, 'P3': True}, seconds=0.011612176895141602 |
| 2026-08-11T06:28:32.482299+00:00 | finalize_done | modifiers=['STRESS_ABOVE'], seconds=0.0002770423889160156, slug='LEVEL_LAW_PREDICTIVE_SCOPED' |

---

## Anomaly log — every anomaly, with pre/post-hypothesis timing

The hypothesis-relevant boundary in this leg is **the stamp**: everything before
it is verification and arithmetic on already-published numbers, and every fresh
world came after it.

- **A-1 — the interpreter (before Part 0).** The environment pinned in M4-M1 and
  reused through the line: CPython 3.12.12 from `requirements-lock-main.txt`
  (numpy `2.4.4`, pandas `3.0.2`, scipy `1.17.1`), platform
  `macOS-26.4.1-arm64-arm-64bit`.
- **A-2 — `timeout(1)` absent on this platform (before Part 0).** Every stage
  ran as its own foreground command under an explicit harness-level timeout.
- **A-3 — four of the harness's own embedded constants were wrong, caught BEFORE
  Part 0 ran.** The M1e monotonicity contrasts were first transcribed from the
  M1e report's rounded prose and were wrong in their trailing digits. They were
  corrected by reading the artifacts directly, and a rounded-quote cross-check
  was added alongside the exact one. Had this not been caught, G0m2 would have
  raised a *false* citation defect and stopped the leg. Rule 24's discipline,
  applied to the harness's constants rather than to the report's tables.
- **A-4 — the G2m2 reading, found AFTER the pilot ran (post-hypothesis for C1's
  rough level).** Documented in full above. The inherited "(0,1)" form fails and
  routes to `UNRESOLVED_SEAL`; the registered word "non-saturated", read against
  the statistic's own cosine range, passes. Both readings, both consequences and
  the first-reading artifact are on the record. This is the one judgement in the
  leg that changed its outcome, and it is flagged as a defect candidate rather
  than buried.
- **A-5 — the finalize stage crashed once on a stale key (after `measure`).** The
  pilot's boolean was renamed by A-4's repair and the report-table writer still
  referenced the old name. `decision.json` had already been written; the fix
  touched only the table writer, and `finalize` was re-run to completion. No
  number changed.
- **A-6 — P1 is a hit near the edge.** 0.8671810125388784 of the way to the band
  boundary, disclosed above rather than reported simply as "inside".
- **A-7 — no stage approached its 2× stop-and-report threshold.** Part 0
  `2.3444879055023193` s against 300 s; the three world chunks inside their 420 s
  estimates.

| stage | registration estimate (s) | measured (s) |
|---|---|---|
| part0 | 300 | 2.344 |
| pilot | 30 | 4.753 |
| worlds_1 | 420 | 218.813 |
| worlds_2 | 420 | 219.460 |
| worlds_3 | 420 | 109.553 |
| measure | 120 | 0.012 |
| finalize | 60 | 0.000 |

| component | value |
|---|---|
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| platform | macOS-26.4.1-arm64-arm-64bit |
| python | 3.12.12 |
| python_executable | /private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python |
| scipy | 1.17.1 |

---

## What this establishes, and what it does not

**Established, prospectively.** The scoped level law — free share margins plus a
steep negative r-power, `r` interior to the trained window — **predicted three
configurations nobody had run, at a share above the trained envelope and a φ
above the trained ladder, and hit all three.** The predictions were hashed
before the first world existed, the hash was re-read from disk to open the
permit, and the ordering is enforced in code rather than asserted in prose. The
M-line's object is now PREDICTIVE in its scope.

**Not established, and the report says so.** (i) The claim does not extend to
configurations whose realized `r` leaves the window — the excluded share-0.70,
φ ≥ 0.85 cells are the boundary, computed and named at registration. (ii) The
exponent remains a ridge coordinate, not a constant: appendix Y stands, and what
transferred is the *prediction*, not `q`. (iii) P1's hit sits at 0.8671810125388784 of
the way to its edge on a band the ridge made wide; three hits on three bands is
the registered bar and it was met, but P1 is the one a successor should tighten.

**For M3.** Two independent signals now say the V-margin is not linear: M1e's
κ representation-indexing, and this leg's `STRESS_ABOVE` — the linear-tax
extrapolation over-falls at share 0.70 by `0.005306451635164661`, exactly as pre-signed.
M3's refined question ("in which representation class is the tax an invariant,
and is the V-margin even linear") now has a prospective data point on the second
half of it.

**Registration-defect candidates: one, and it is consequential.** G2m2 says
"finite/non-saturated/nonzero-variance" without pinning what saturation means
for this statistic, while three prior legs establish a conflicting "(0,1)"
convention in code. The two readings route to *different outcomes* here —
`LEVEL_LAW_PREDICTIVE_SCOPED` versus `UNRESOLVED_SEAL` — so this is not the usual "nothing turned
on it" flag: everything turned on it. The executor pinned the registered wording
against the statistic's source-verified range and reported both, but a
successor registration should pin the saturation test explicitly, and the
program should decide once whether the inherited "(0,1)" form is a convention or
a bug in three prior gates.
