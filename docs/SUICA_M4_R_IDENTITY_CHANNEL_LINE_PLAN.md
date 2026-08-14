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
