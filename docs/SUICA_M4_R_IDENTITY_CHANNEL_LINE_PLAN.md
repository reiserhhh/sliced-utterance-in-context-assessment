# SUICA M4-R — The Identity-Channel Line

Line opened 2026-08-14, on the Q-line's close. Question: **make the
founding question posable.** This program began with the conjecture
that the residual is not error but IDENTITY — an ID card. Five
closed lines later, the k2b family's verdict is structural: its
cards carry ONLY biography (the trait); there is no non-trait author
channel for any instrument to find (appendix KK). The R-line builds
one: a per-author, persistent, non-trait STYLE channel planted into
the card-visible response path, with a zero-default weight so the
extension certifies backward bit-identity. Once certified, the
program's identity instruments (the centred cross-frame cosine, the
frame-refreshed discriminator, the taxometer, the completeness
meter) can be pointed at a world that can answer YES or NO.

Tier: EXPLORATORY, label-free, synthetic. The ledger controls.
Registrations before run, append-only. Standing rules 1–33 bind;
ALL conventions in force (notably: #59 non-degeneracy of estimand
contrasts and cell antecedents; #60 disattenuation identities name
their shared component; #57 pilot correlations never consumed; #56
inheritance is not exemption; the #43 planner-arithmetic family).
Execution conventions as always (ONE commit per leg
`feat(m4-r): ...`, never amended, never pushed; chunked foreground
stages < 600 s; `suica_core/`, k2b and the P3b instrument
READ-ONLY — R-legs import P3b's builder and EXTEND it inside their
own scripts by minimal extraction with provenance).

## Line charter

- **R1 — the identity-channel instrument** (registered below):
  build `build_split_world_v2` (planted style channel,
  zero-default), certify backward identity / channel placement /
  quantitative recoverability.
- **R2 — the identity phenomenology** (named; register only after
  R1 certifies): does the gauge tax style like it taxes trait?
  does style transport across frames (it must — it is
  author-stream — the test is that the INSTRUMENTS see it)?
  does the frame-refreshed discriminator (T6″ pattern) separate
  planted style from forged frame-stability?
- **R3 — the taxometer on identity mixtures** (named): η̂ and the
  completeness meter against style/trait mixture worlds.

---

## M4-R1 — the identity-channel instrument

**REGISTERED 2026-08-14, BEFORE RUN.** Planner: this document's
author; executor: dispatched agent. An INSTRUMENT leg: no theory
verdict, only certificates.

### The extension (rules 9/12 — minimal extraction with provenance)

`build_split_world_v2(author_seed, frame_seed, phi_slow, w_style)`,
inside `scripts/run_suica_m4_r1_identity_channel.py`, extending
P3b's certified builder (imported by file, hashes verified):

- **style_a** — one vector per author, dimension DIM, drawn on the
  AUTHOR stream as its LAST draw (prefix property: all existing
  author objects remain bit-identical);
- **placement** — style enters the RESPONSE path at exactly the
  site where the trait enters (the w_mu·trait term in the panel
  emission; executor pins file:line and mirrors it as
  + w_style·style_a per response), so the card picks up
  w_style·style_c̄ precisely as it picks up the trait — a
  card-visible, author-persistent, NON-TRAIT channel;
- **w_style units** — multiples of the trait weight w_mu (executor
  pins w_mu's persisted value); w_style = 0 is the default.

### Certification battery (the leg IS the battery)

- **C-R1a (backward identity):** at w_style = 0, worlds, panels,
  cards and fields BIT-IDENTICAL to the P3b builder — 8 probe
  pairs × φ ∈ {0.05, 0.60}; any difference → INSTRUMENT_DEFECT.
- **C-R1b (channel placement):** style_a is author-stream
  (bit-identical across frame seeds, C2a-style), independent of
  trait (per-world author-level cos(style, trait): mean within 2·SE
  of 0, realized values reported); the card's style component is
  CENTRED style (verified against the composition, the #60
  lesson — the shared component of an A/B pair at w_style > 0 is
  w_mu·trait_c + w_style·style_c, NAMED here as required).
- **C-R1c (quantitative recoverability):** at w_style ∈ {0.5, 1.0}
  × 128 A/B pairs (share 0.25, φ 0.60): the centred cross-frame
  excess Δ_style = cos_AB − r̂_A·r̂_B (r̂ scored against the CENTRED
  TRAIT ONLY — so the planted style appears as excess) must be (i)
  ≈ 0 at w_style = 0 (the Q1b-corrected null re-confirmed on v2);
  (ii) POSITIVE at 0.5 and 1.0; (iii) MONOTONE (Δ(1.0) > Δ(0.5),
  CIs disjoint or ordering stable at B = 20000); (iv) INSIDE the
  algebraic prediction band derived in Part 0 from the composition
  weights (deterministic arithmetic: the expected excess from a
  planted share, executor derives and persists BEFORE the arms;
  rule 30 — executed provenance).
- **Non-degeneracy (#59, discharged at registration):** Δ_style at
  w > 0 is not forced — it depends on realized norms and the
  planted weight; the w = 0 null is the Q1b-verified behaviour of
  the UNEXTENDED builder, not an identity of the extension.

### Design

share 0.25, φ 0.60; w_style ∈ {0, 0.5, 1.0} × 128 A/B pairs each
(384 pairs, 768 worlds) + the C-R1a/b probe sets. Salts
`m4r1-author` / `m4r1-frameA` / `m4r1-frameB` / `m4r1-pilot`,
master_seed 20260814. G2r1 pilot: 4 pairs at w ∈ {0, 1.0},
rule-29 predicate; bands variances-only (#57). G3r1 projection:
detection power for Δ_style at w = 1.0 ≥ 0.8 with ≤ 0.1 false-fire
at w = 0, at 128 pairs; once-only escalation to 256 ON THIS GATE.
G4r1: routing disjoint/covering/entailed/antecedent-nondegenerate;
rule 24; stages: part0 150 s (incl. the algebraic band), pilot
60 s, worlds 3 chunks (~200 s), score 120 s, finalize 60 s; target
< 35 min.

### Leans

**L-1r1 [CERTIFIED .70 / a named certificate fails .25 / other
.05].**

### Routing (rule 16)

| # | condition | outcome |
|---|---|---|
| 1 | G0/import/hash failure | **STOP** |
| 2 | projection fails after escalation | **NON_PROJECTABLE** |
| 3 | all four certificates PASS | **IDENTITY_CHANNEL_CERTIFIED** — R2 becomes registrable; the founding question is posable |
| 4 | any certificate fails | **INSTRUMENT_DEFECT(name)** — the failing certificate is the finding; handback |

### Deliverables and budget

`scripts/run_suica_m4_r1_identity_channel.py`;
`results/m4_r1_identity_channel/` (gitignored);
`reports/SUICA_M4_R1_IDENTITY_CHANNEL_REPORT.md` (generated
tables); outcome append HERE; one ledger row (EXPLORATORY); exactly
ONE commit `feat(m4-r): R1 — the identity-channel instrument —
<SLUG>`, never amended, never pushed; suite green first. 768 worlds
(+probes, +escalation ×2) ; every stage < 600 s.

### M4-R1 outcome (appended after execution; registration above unedited)

**INSTRUMENT_DEFECT(C-R1c) — routing cell 4.** INSTRUMENT_DEFECT(name) -- the failing certificate is the finding. Harness
`scripts/run_suica_m4_r1_identity_channel.py`; report
`reports/SUICA_M4_R1_IDENTITY_CHANNEL_REPORT.md`; artifacts
`results/m4_r1_identity_channel/` (gitignored). 768 worlds
(128 A/B pairs per dose) plus the probe sets.

**THE CHANNEL WORKS; MY BAND WAS TOO TIGHT.** C-R1a, C-R1b and G2r1 all PASS.
C-R1c fails on its **fourth clause only**, and the failure is in the Part-0
band, not in the planted channel.

**The extension needs no k2b edit.** The trait enters the response path at
exactly one site — **`scripts/run_suica_m4_k2b_t4_branch.py:371`**: `v += w["mu"] * world["trait"][i][None, :]`. The registration asks
for the mirror `+ w_style·style_a` there and specifies w_style in multiples of
w_mu (**0.33541019662496846**, bit-exact against the persisted value: True).
Writing w_style = m·w_mu, `w_mu·trait + w_style·style = w_mu·(trait + m·style)`
EXACTLY, so publishing `trait_eff = trait + m·style` as the world's `trait`
makes k2b's own UNEDITED `emit_panel` carry style at precisely the trait's site,
in the observed panel and in every truth panel using `"mu"`. `trait_pure` and
`style` are published separately for C-R1c and C-R1b. k2b, `suica_core/` and the
P3b builder stay READ-ONLY; P3b's hashes match P3c's persisted (True).
`style_z` is the LAST author-stream draw, so the prefix property preserves every
earlier draw.

**C-R1a PASS** — backward bit-identity at w_style = 0 across 16
probes at φ ∈ {0.05, 0.60}: objects True, panels True,
cards True, fields True (4 checks). The
extension is inert at zero, so every prior result on the P3b builder stands.

**C-R1b PASS** — style is author-stream (True: bit-identical
across frame seeds), independent of trait (cos(style_c, trait_c) =
0.002430979842622228, SE 0.0014745152709377159, within 2 SE of zero: True), and
the card recomposes exactly from its named parts (True). **The shared
component is NAMED as #60 requires: w_mu * trait_c + w_style * style_c (centred trait PLUS centred style).** r̂ is scored against
the CENTRED TRAIT ONLY, deliberately, so the planted style appears as excess
rather than being absorbed — the direct lesson of Q1b's defect.

**C-R1c — three clauses pass, the fourth fails.**

| w_style | n | measured Δ | 95% CI | predicted | persisted band | inside | measured − predicted |
|---|---|---|---|---|---|---|---|
| 0.0 | 128 | 0.00027221510546395313 | [-0.00015154691455664595, 0.0006871194716920599] | 0.0 | [0.0, 0.0] | False | 0.00027221510546395313 |
| 0.5 | 128 | 0.1273886225517469 | [0.12695536488518774, 0.12783525151445932] | 0.12739898980740494 | [0.12677339619614159, 0.1280245834186683] | True | -1.0367255658033647e-05 |
| 1.0 | 128 | 0.36609324420972367 | [0.3654769305968154, 0.3667285934456878] | 0.3695134875442334 | [0.3680053945830404, 0.37102158050542644] | False | -0.0034202433345097427 |

- **(i) PASS** — Δ = 0.00027221510546395313 [-0.00015154691455664595, 0.0006871194716920599] at w = 0, inside ±0.00075116719103521;
  the Q1b-corrected null re-confirmed on v2.
- **(ii) PASS** — POSITIVE at both doses.
- **(iii) PASS** — MONOTONE: P(Δ₁.₀ > Δ₀.₅) = 1.0 and
  P(Δ₀.₅ > Δ₀.₀) = 1.0 at B = 2000.
- **(iv) FAIL** — containment in the Part-0 band: False / True /
  False.

**The band's defect, diagnosed POST HOC (routing nothing).** The band was
persisted before the arms as required and it ROUTES — retuning after seeing the
measurement is exactly the move this programme forbids, so the verdict stands.
But it has two flaws, both mine:

| w_style | persisted band width | degenerate? | SE_pred | SE_meas | gap / combined SE | inside a CORRECTED band |
|---|---|---|---|---|---|---|
| 0.0 | 0.0 | True | 0.0 | 0.00021684323861539953 | 1.2553543619903362 | True |
| 0.5 | 0.0012511872225267062 | False | 0.0003127968056316807 | 0.0002233080066693018 | -0.02697499342954882 | True |
| 1.0 | 0.003016185922386061 | False | 0.000754046480596509 | 0.00032032174018175404 | -4.174779893852667 | False |

(a) **At w = 0 the band is degenerate**: the prediction is exactly 0 at every
probe world, so its SE is exactly 0 and the band has **zero width** — no
measured value except a literal 0.0 could pass. Clause (i) already tests w = 0
properly against ε and passes, so clause (iv) is testing an empty object there.
(b) **At w > 0 the band carries only the prediction's probe spread**, ignoring
the measurement's SE and — decisively — the DERIVATION's approximation error:
the algebra assumes per-author orthogonality of t, s and n (realized
cos = 0.002430979842622228, not 0) and equates a ratio of means with a mean of ratios
(Jensen). Both grow with b, which is the observed pattern exactly: the gap is
-8.137627836536472e-05 of the prediction at w = 0.5 and -0.009256071699142823 at w = 1.0, the
latter -4.174779893852667 combined SE — outside even a measurement-aware band.

**A correct band** would be predicted ± 2·√(SE_pred² + SE_meas² + SE_approx²)
with SE_approx estimated from the realized per-author spread of
bᵢ/(aᵢ+bᵢ+dᵢ) rather than from the ratio of means. That is the handback.

**The algebraic band itself (executed provenance, persisted BEFORE the arms).**
With a = E‖w_mu·trait_c‖², b = E‖w_style·style_c‖², d = E‖frame remainder‖²,
Δ = b/(a+b+d) in expectation — exactly 0 at w = 0 and increasing thereafter.
a, b, d were MEASURED on probe worlds; predictions 0.0 / 0.12739898980740494 /
0.3695134875442334.

**G3r1 PASS**: false-fire 0.043 at w = 0 (bar 0.1), power 1.0 at
the algebraic w = 1.0 truth (bar 0.8); escalation did not fire (False).

**Rule events.** Rule 13: 0 events, B = 2000. Rule 25: passed.
Rule 26: no bounded winner. Rule 27: no budgeted consumption. Rule 29: the
predicate ran at every arm. Rule 30: the band derived from MEASURED probe norms
and persisted before the arms; w_mu and the P3b hashes verified at source. #57:
no pilot correlation consumed — Δ is a per-pair scalar. #59: Δ at w > 0 is not
forced; the w = 0 null is the unextended builder's verified behaviour. #60: the
shared component is named.

**Executor self-report.** Two standing anomalies, both resolved before any
hypothesis-relevant number existed: A-1 the dispatched interpreter is absent (a
pinned CPython 3.12.12 venv built from the lockfile); A-2 `timeout(1)` is
absent on macOS. **The band's defect is a third, and it is mine** — but unlike
A-1/A-2 it could not be caught before the measurement existed, which is why it
is reported as a diagnosed failure rather than a corrected one.

**Registration-defect candidates: none.** The registration specified clause (iv)
correctly; what failed is the executor's construction of the band it names. Worth
recording as a convention candidate for the planner: **a prediction band tested
for containment must carry the derivation's approximation error, not only the
prediction's sampling spread — and a band whose predicted value is a
deterministic constant has zero width and cannot be a containment test at all.**
That is the rule-32 estimator-noise-floor family applied to a PREDICTION rather
than a measurement.

**What this leaves.** The channel is planted, inert at zero, author-stream,
trait-independent, card-visible, and recoverable with a monotone dose response
matching the composition arithmetic to within 1%. What is NOT certified is the
quantitative containment claim, because the band that was supposed to test it
could not. A successor leg re-banding clause (iv) — with no change to the
instrument — would close it.

### Planner adjudication of R1 (2026-08-14, appended after the run) — THE CHANNEL WORKS; THE BAND WAS THE DEFECT

**INSTRUMENT_DEFECT(C-R1c) accepted — and localized: clauses
(i)/(ii)/(iii) PASS, C-R1a/C-R1b PASS, the projection PASSES; what
failed is the planner's Part-0 band, on clause (iv) alone.** The
channel is planted (Δ monotone P = 1.0, matching the composition
arithmetic to −0.008% at w = 0.5 and −0.93% at w = 1.0), inert at
zero (bit-identical objects, panels, cards, fields — every prior
P3b result stands), author-stream, trait-independent
(cos = +0.0024, within 2 SE of 0), with the shared component named
per #60. The executor's construction is more minimal than the
registration asked: **no site mirroring at all** — w_mu·trait +
w_style·style = w_mu·(trait + m·style), so publishing trait_eff
lets k2b's own unedited `emit_panel` (k2b:371, w_mu =
0.33541019662496846) carry style at exactly the trait's site, with
trait_pure kept separate for scoring.

**Defect #61 (mine).** The containment band (a) had ZERO WIDTH at
the deterministic w = 0 point — a band around a constant cannot be
a containment test (rule 31's one-reachable-side pathology, at the
band level); and (b) omitted two error sources at w > 0 — the
measurement's SE and, decisively, the DERIVATION'S approximation
error (realized non-orthogonality + Jensen), which grows with the
planted share exactly as the −4.17-SE gap at w = 1.0 shows.
**Convention (rules 31/32 family, applied to predictions): a
containment band on a derived prediction carries width
2·√(SE_pred² + SE_meas² + SE_approx²), with SE_approx estimated
from the realized deviation of the derivation's assumptions;
deterministic points are tested by equivalence bands (ε), never by
containment.** The executor's refusal to retune after seeing the
measurement was correct and is the reason the defect is clean.

---

## M4-R1b — clause (iv), re-banded and tested prospectively

**REGISTERED 2026-08-14, BEFORE RUN.** Planner: this document's
author; executor: dispatched agent. The instrument is UNCHANGED
(same script's builder, same hashes); only clause (iv) is re-posed.
Because R1's measured Δ values are on the record, a re-banded test
on the SAME doses adjudicates nothing prospectively — so the
primary test is a FRESH dose.

### Design

- **Primary (prospective containment):** w_style = **0.75** (never
  measured) × 128 A/B pairs (256 worlds; share 0.25, φ 0.60; salts
  `m4r1b-author` / `m4r1b-frameA` / `m4r1b-frameB` / `m4r1b-pilot`,
  master_seed 20260814). Part 0 derives the algebraic prediction at
  0.75 AND the corrected band per the #61 convention — SE_approx
  from the realized per-author spread of bᵢ/(aᵢ+bᵢ+dᵢ) on the
  PROBE worlds (pre-measurement objects), persisted and hashed
  BEFORE the fresh arms (K2f ordering; the pilot after the stamp).
- **Secondary (re-scoring, adjudicating nothing):** R1's persisted
  w ∈ {0.5, 1.0} measurements against the corrected band — reported
  as consistency readings with the post-hoc label.
- **w = 0 clause:** re-typed as the EQUIVALENCE test it always was
  — R1's clause (i) result stands as its verdict (no new worlds).

### Verdicts and routing (rule 16)

**V-R1b:** measured Δ(0.75) inside the corrected band — two-sided
containment. Lean [.70]. Cells: **STOP** (G0/hash mismatch) /
**NON_PROJECTABLE** (projection at the corrected band's width:
false-fire ≤ 0.1 under Δ = algebraic − 3·band, power ≥ 0.8 at the
algebraic truth; escalation to 256 pairs once, ON THIS GATE) /
**IDENTITY_CHANNEL_CERTIFIED** (V-R1b inside — C-R1c closes; with
C-R1a/b standing, the instrument is certified and R2 becomes
registrable) / **BAND_STILL_WRONG** (outside — the derivation error
model is inadequate; handback with the realized decomposition).

### Deliverables and budget

`scripts/run_suica_m4_r1b_reband.py`; `results/m4_r1b_reband/`
(gitignored); `reports/SUICA_M4_R1B_REBAND_REPORT.md` (generated
tables); outcome append HERE; one ledger row (EXPLORATORY); exactly
ONE commit `feat(m4-r): R1b — clause (iv) re-banded — <SLUG>`,
never amended, never pushed; suite green first. 256 worlds
(+escalation ×2) + pilot; target < 20 min, every stage < 600 s.

### Outcome of M4-R1b (executed 2026-08-14, append-only)

**`IDENTITY_CHANNEL_CERTIFIED` (rule-16 cell 3).** Clause (iv)
closes prospectively at a dose that had never been measured.

- **The corrected band, all three terms from PROBE worlds** (the pilot runs
  after the stamp, so no term may come from it). Prediction at w = 0.75 =
  `0.2476172270351607` (ratio-of-means, R1's form, unchanged — RN-R1B-3);
  SE_pred = `0.00045459114785961074`, SE_meas = `0.0002683462385382117`, SE_approx =
  `0.002186151999363512`; combined `0.002248982743324414`; half-width
  `0.004497965486648828`; band `[0.24311926154851188, 0.25211519252180953]`. **SE_approx dominates** — it is
  4.809050967351109x SE_pred and 8.146758498544077x
  SE_meas, i.e. the term R1's band omitted was the only one that mattered.
- **Ordering.** `prediction.json` hashed `dd5912a4c219c651df501488ed3bdcd5455bdb968865579c93f13570fcb57c95` and stamped
  2026-08-14T08:43:42.897504+00:00 with **0 fresh-arm
  worlds in existence**; the arm re-read the stamp from disk and re-hashed to a
  match 18.305773 s later. 32
  probe worlds necessarily precede the stamp — they are the band's inputs — and
  are counted separately (RN-R1B-4).
- **G3r1b PASS.** At the corrected width: power
  1.0 at the algebraic
  truth (bar 0.8) and false-fire
  0.0
  at prediction − 3·band (bar 0.1). Escalation fired: False.
- **V-R1b PASS.** Measured Δ(0.75) = `0.24614231318551627` [0.24556658406745574, 0.24677281301031784],
  signed error `-0.0014749138496444325`, **position -0.3279068845731195** of
  the half-width. INSIDE.
- **The correction is load-bearing, not a convenient widening.** The residual is
  -0.6746620775105513 of SE_approx but
  -4.8949869838067945 of the measurement's own SEM — the
  measurement is far more precise than the prediction is accurate, which is the
  whole content of #61. **Under R1's band form** (2·√(SE_pred² + SE_meas²),
  half-width `0.0010557704588591693`) **this leg would have
  landed at -1.3970023855736367 and FAILED
  (False)** — the identical failure would have
  recurred at a fresh dose.
- **Secondary (post-hoc, adjudicating nothing).** R1's gaps re-scored against
  this half-width: w = 0.5 gap `-1.0367255658033647e-05` (inside:
  True), w = 1.0 gap
  `-0.0034202433345097427` (inside:
  True). Reported as consistency
  readings only; the routing uses w = 0.75 alone (RN-R1B-1). The w = 0 clause is
  re-typed as equivalence and R1's clause (i) stands as its verdict.
- **Executor anomaly A-3, AFTER the verdict existed.** The report template —
  written before the run — asserted the measurement would sit closer to the
  per-author mean-of-ratios, that being "what the measurement actually
  estimates" (Part 0's own words). It does not: the measurement is
  `-0.0038555197801447283` from the arm's
  mean-of-ratios versus `-0.0014749138496444325` from the stamped
  ratio-of-means, so **the pre-pinned form was the closer one and I did not know
  that when I pinned it**. Had the mean-of-ratios been stamped the position would
  have been -0.8571697118594949 — still inside
  (True), but near the edge. The containment verdict is
  robust to the form choice; the comfort of the margin is not. The residual is
  therefore NOT the Jensen form gap — it runs the other way and is larger, and
  SE_approx covers it because that spread sets the right *scale* for the
  derivation's error, not because it names its mechanism. The false sentence was
  replaced by §5.1's generated decomposition. No number changed;
  `prediction.json` is untouched and still re-hashes to the stamp.
- **Consequence.** With C-R1a, C-R1b and clauses (i)–(iii) standing from R1, the
  identity channel is **certified**: planted, inert at zero, author-stream,
  trait-independent, card-visible, monotone in dose, and quantitatively
  recoverable inside a band fixed before the measurement existed. M4-R2 becomes
  registrable. Nothing here bears on the k2b family's own worlds — the channel
  is planted, not discovered, and appendix KK's boundary is unmoved.
- Rule 13: 0 events. Report: `reports/SUICA_M4_R1B_REBAND_REPORT.md`.
- **No registration-defect candidates.** The registration specified the leg
  correctly, including the prescription for SE_approx.

### Planner adjudication of R1b (2026-08-14, appended after the run) — CERTIFIED, WITH THE CORRECTION PROVEN LOAD-BEARING

**IDENTITY_CHANNEL_CERTIFIED accepted — zero registration defects.**
Δ(0.75) = 0.24614231318551627 landed inside the #61-corrected band
[0.24311926154851188, 0.25211519252180953] at position −0.328, with
the stamp preceding every fresh world (0 at stamp; permit by
re-hash +18.3 s). Two facts elevate this beyond a pass: (i) **the
correction is load-bearing** — under R1's band form the same fresh
dose FAILS at −1.397; SE_approx (0.002186) dominates SE_pred (4.8×)
and SE_meas (8.1×) — the omitted term was the only one that
mattered; (ii) the executor's A-3 (its own template expectation
about the mean-of-ratios form was WRONG — the pre-pinned
ratio-of-means was closer, verdict robust to the choice, margin
comfort not) is the rule-30 culture auditing even its own prose
post-verdict, disclosed with timing. **C-R1c closes; with C-R1a/b
standing, the identity-channel instrument is CERTIFIED. The
founding question is posable. R2 is registrable.**

---

## M4-R2 — the gauge meets the identity channel

**REGISTERED 2026-08-14, BEFORE RUN.** Planner: this document's
author; executor: dispatched agent. Three questions, one of them
SEALED — the program's laws predicting the consequence of the new
channel:

1. **Interference (SEALED):** does planted identity CROWD OUT the
   reading of biography? The tax curve says yes, quantitatively:
   style adds author-persistent variance, raising the EFFECTIVE
   person share, and the N-line curve prices that.
2. **Within-frame style reading (DESCRIPTIVE ONLY):** at w = 1.0
   (equal weights), trait and style enter the response
   EXCHANGEABLY, so R_S ≈ R_T is a symmetry, not a finding (#59
   discharged by declaring it descriptive).
3. **Cross-frame style reading (VERDICT):** style is author-stream
   — it is PRESENT in both worlds of a pair. Can the gauge read it
   across frames? The P-line predicts NO even though the identity
   exists — the sharpest form of the gauge's limitation.

### Design

v2 builder (certified; hashes verified), share 0.25, φ 0.60,
w_style ∈ {0, 1.0} × 192 A/B pairs each (384 pairs, 768 worlds).
Salts `m4r2-author` / `m4r2-frameA` / `m4r2-frameB` / `m4r2-pilot`,
master_seed 20260814. Truth panels: the pipeline's own construction
fed with trait_pure and with style (executor pins the truth-panel
machinery file:line, rule 12; the truth semantics are the
pipeline's, unchanged). Quantities per pair: R_T_nat (A-gauge vs
A's trait_pure truth), R_S_nat (vs A's style truth), R_S_ref (vs
B's style truth), at both w.

### The sealed prediction (Part 0 → hash → worlds; #61-compliant band)

ΔR_T = R_T_nat(w=1) − R_T_nat(w=0), predicted from the N-line curve
at the EFFECTIVE person share: the executor derives V_eff on probe
worlds from realized channel variances (the share accounting of
`person_share_design`'s own semantics, pinned file:line), computes
the curve prediction α(V_eff) − α(V_design) from M3's persisted
(c, κ0, κ2), and carries the r-channel's shift and every
derivation approximation inside SE_approx (the #61 convention:
band = 2·√(SE_pred² + SE_meas² + SE_approx²); planner sanity value
≈ −0.06, expressly approximate, executor recomputes). Prediction +
band hashed BEFORE any fresh world (K2f ordering; pilot after
stamp).

### Verdicts (rule 22; NULL-first; #57 bands)

- **V-R2a (sealed):** measured ΔR_T inside the band — two-sided.
  Leans [.45 inside / .25 negative-but-outside / .20 NULL (no
  interference — the law does not transport to the new channel) /
  .10 other].
- **V-R2c:** R_S_ref(w=1) vs 0, NULL-first (ε from pilot,
  variances only). Lean NULL [.60] — the gauge cannot read identity
  across frames even when it exists.
- Descriptive: R_S_nat vs R_T_nat at w = 1 (the exchangeability
  reading, no gate); R_S_nat(w=0) as the null anchor (style drawn
  but weightless — expected ≈ 0, anchor not verdict).

### Gates

G0r2: R1/R1b certified values + instrument hashes + M3 curve params
at source; the truth-panel machinery pinned. G1r2: C2-style battery
on 4 fresh probes; per-pair frame difference; style-truth panels
differ from trait-truth panels provably (norm delta; #59). G2r2:
pilot 4 pairs × both w, rule-29 predicate on all three scorings.
G3r2: projection — power ≥ 0.8 for V-R2a at the curve truth and
false-fire ≤ 0.1 at ΔR_T = 0; V-R2c false-fire ≤ 0.1 at 0 with
power ≥ 0.8 at R_S_ref = R_S_nat(w=1)'s pilot value; 192 pairs,
once-only escalation to 384 ON THIS GATE. G4r2: routing
disjoint/covering/entailed/antecedent-nondegenerate; rule 24;
stages part0 240 s (derivation + stamp), pilot 60 s, worlds 4
chunks, score 180 s, finalize 60 s; target < 45 min.

### Routing (rule 16)

| # | condition | outcome |
|---|---|---|
| 1 | G0/G1 failure | **STOP / INSTRUMENT_DEFECT** |
| 2 | projection fails after escalation | **NON_PROJECTABLE** |
| 3 | V-R2a inside AND V-R2c NULL | **IDENTITY_CROWDS_BIOGRAPHY_AND_STAYS_UNREADABLE** — the tax curve transports to the new channel; the gauge pays the identity tax yet cannot read the identity; the founding answer's gauge half is complete |
| 4 | V-R2a inside AND V-R2c POSITIVE | **IDENTITY_PARTIALLY_READABLE** — the gauge reads planted identity across frames; P-line's limitation is trait-specific; major theory note |
| 5 | V-R2a NULL AND V-R2c NULL | **LAW_DOES_NOT_TRANSPORT** — the curve is design-V-specific (a channel-accounting finding); the gauge still cannot read identity |
| 6 | V-R2a negative-but-outside (either side) | **INTERFERENCE_MISPRICED** — interference real, the law's price wrong; the band decomposition names the gap |
| 7 | any other combination incl. UNDERPOWERED | **MIXED_OR_UNDERPOWERED** — every verdict reported; nothing upgraded |

### Deliverables and budget

`scripts/run_suica_m4_r2_gauge_meets_identity.py`;
`results/m4_r2_gauge_meets_identity/` (gitignored);
`reports/SUICA_M4_R2_GAUGE_MEETS_IDENTITY_REPORT.md` (generated
tables); outcome append HERE; one ledger row (EXPLORATORY); exactly
ONE commit `feat(m4-r): R2 — the gauge meets the identity channel —
<SLUG>`, never amended, never pushed; suite green first. 768 worlds
(+escalation ×2) + pilot; every stage < 600 s.

### Outcome of M4-R2 (executed 2026-08-14, append-only)

**`INTERFERENCE_MISPRICED` (rule-16 cell 6).** Modifier:
INTERFERENCE_REAL_BUT_SMALLER_THAN_PRICED. **Interference is real, and the tax curve
overprices it by 11.64546777328575x.**

- **A registration defect had to be pinned before any number (RN-R2-1).** The
  registration derives V_eff from "the share accounting of
  `person_share_design`'s own semantics". That function's IMPLEMENTATION
  (k2e:240) is literally `slow + int`, which EXCLUDES the `mu` channel where
  style lives — so style RAISES the denominator, LOWERS V_eff, and makes the
  sealed prediction POSITIVE (0.006457447033500374). That
  contradicts the registration's own mechanism sentence in the same paragraph
  ("style adds author-persistent variance, RAISING the effective person share")
  and its sanity value (-0.06). All three readings
  were computed and persisted BEFORE the stamp. The routing reading is **C =
  (slow + int + style)/total** on four grounds: it is the function's SEMANTICS
  (the author-persistent share that is NOT the target trait; #56), it reduces to
  V_design exactly at w = 0, it lands inside M3's fitted domain [0.03, 0.21], and
  it is the only reading consistent with the registration's stated mechanism.
  Reading A inverts the sign; reading B (-0.13444453250196647)
  fails the w = 0 reduction and extrapolates outside the fitted domain. The
  sanity value corroborates C but does NOT gate (rule 30; RN-Q2-6 precedent).
- **The sealed prediction.** V_design 0.07500000000000002 → V_eff
  0.16849932384036667; α 0.1448569748507095 → 0.07287295056531737;
  prediction **-0.07198402428539213**. Band per #61: SE_pred 0.0006102321051948493,
  SE_meas 0.0014077434928863272, **SE_approx 0.00613560574702563** (r-channel shift
  0.0061129257838192326, V_eff spread
  6.0788117635513934e-05, mu non-additivity
  0.0005235466065273388); half-width
  0.012649076305708377; band [-0.08463310059110052, -0.05933494797968376]. The r-channel shift dominates and
  is real: this instrument reads 0.13255563513927227 at w = 0 where M3's curve
  says 0.1448569748507095, a gain of 0.9150794104038479.
- **Ordering.** Hashed `bb15b6104d302ebeb50b91c256404c10029c2da115fdda3c23167c6172bd6065`, stamped 2026-08-14T09:05:07.805460+00:00 with
  **0 fresh-arm worlds in existence**
  (64 probe + 12
  battery worlds necessarily precede it — they are the band's inputs). Arms
  re-read the stamp and re-hashed to a match 300.316706 s
  later. Pilot after the stamp.
- **V-R2a OUTSIDE.** Measured ΔR_T = **-0.00618129092680336** [-0.008110727559547634, -0.004257287226729858],
  SEM 0.0009787401813587634, position **5.202176962826352** of the half-width.
  Not a null: the 2·SEM scale is only 0.0019574803627175267 and the CI excludes
  zero. R_T_nat falls 0.12425035254824575 →
  0.11806906162144237. Interference is REAL and NEGATIVE; the
  law's price is wrong by more than an order of magnitude.
- **THE DISCLOSURE THAT MATTERS MOST.** Reading A — the literal implementation,
  which I did NOT pin — **would have been inside**, at position
  -0.9991826798135466, i.e. inside by
  0.0008173201864534185 of the half-width. Had it
  been pinned, the leg would have routed to a different cell. Two things stop
  that from rescuing it on the merits: its prediction has the OPPOSITE SIGN to a
  measurement whose CI excludes zero, and it clears the bar only by grazing —
  the half-width is 2.046348643915037x the entire measured
  effect, so the band is too coarse to discriminate a small negative
  interference from a small positive one. Both candidate prices are wrong; the
  band cannot adjudicate between them. This is reportable only because the pin
  and all three readings were persisted before the measurement existed.
- **V-R2c INDETERMINATE** (registered form): R_S_ref(w=1) =
  -0.00023760593803822915 [-0.003567179813180193, 0.0030463008905367156] against ε = 0.003493124558101321. **The classification
  is bootstrap-noise-limited**: the lower edge misses −ε by
  -7.405525507887204e-05, which is -0.7385675960969138 of that
  percentile's Monte-Carlo SE (0.00010026875734899506);
  at B = 20000 the interval is [-0.003471613813457244, 0.0030552232664270047] and the
  classification would be **NULL**. Q2's rule-13
  trigger tests a boundary's TAIL FRACTION and is silent when the instability
  lives in the PERCENTILE VALUE, so it did not fire (0
  events). The registered B = 2000 reading is what is reported and routes; the
  high-B reading is a disclosed diagnostic, NOT a re-resolution. Nothing turns on
  it — cell 6 fires on V-R2a alone.
- **The w = 0 anchor's registered expectation is WRONG, structurally.** The
  registration expected R_S_nat(w=0) ≈ 0. It is 0.08866022322041145, close to
  R_T_nat's own 0.12425035254824575. Cause: the pipeline's truth
  panels are `emit_panel(..., active=("mu","common"))` and therefore CARRY THE
  FRAME, so the anchor measures frame agreement, not style reading. Anchor, not
  verdict — nothing routes — but the number must not be read as framed.
- **Consequently the registered V-R2c form conflates two things**, and the
  frame-controlled contrast is sharper (RN-R2-8, DIAGNOSTIC): the paired
  increment R_S_ref(w=1) − R_S_ref(w=0) = **-0.002400251449476367** [-0.004531674544523817, -0.00036827981268627977]
  (excludes zero: True) against a within-frame increment
  R_S_nat(w=1) − R_S_nat(w=0) = **0.030522666132592052**
  [0.02844019394597627, 0.032630214283184106] — ratio
  -0.07863832861289213. A full-strength identity channel buys the
  gauge 0.030522666132592052 of readable identity within
  frame and NOTHING across frames — slightly negative, in fact. That is the
  sharpest form yet of the P-line's limitation: **the identity is there, it is
  readable, and a frame refresh erases the gauge's access to it entirely.**
- **Descriptive (#59, gates nothing).** Exchangeability at w = 1: R_S_nat
  0.11918288935300352 vs R_T_nat 0.11806906162144237, ratio 1.0094336968234094,
  difference 0.0011138277315611274 [-0.0015157844324500396, 0.003842021426323359] — the construction's symmetry, as
  registered.
- **Gates.** G0r2 PASS (R1/R1b slugs, instrument hashes, M3 A-quad CONSUMABLE at
  source, OLS refit reproduces the persisted θ, α at V_design persisted).
  G1r2 PASS (C2-style battery on 4 fresh probes; truth panels
  provably differ). G2r2 PASS. G3r2 PASS: power 1.0
  at the curve truth, false-fire 0.0 at ΔR_T = 0, V-R2c false-fire
  0.0445 and power
  1.0;
  escalation fired: False.
- **Disclosed ordering fact (A-4).** SE_meas must come from pre-measurement
  objects, so probe pairs were scored at BOTH doses before the stamp; a probe
  ΔR_T (-0.01589391381974946) therefore existed
  beforehand. It was never consumed: the prediction contains no R term at all,
  SE_meas takes only the difference's standard deviation, and the gain takes only
  the w = 0 level (#57, variances only).
- Rule 13: 0 events. Report:
  `reports/SUICA_M4_R2_GAUGE_MEETS_IDENTITY_REPORT.md`.
- **Three registration-defect candidates**, all non-blocking and all pinned or
  disclosed before they could route: (1) RN-R2-1, the V_eff share-accounting
  ambiguity, which flips the sealed prediction's SIGN and is load-bearing for the
  cell; (2) the w = 0 anchor's "expected ≈ 0", contradicted by the pipeline's own
  frame-carrying truth panels; (3) rule 13's trigger, which catches tail-fraction
  instability but not percentile-value instability — a convention candidate.
