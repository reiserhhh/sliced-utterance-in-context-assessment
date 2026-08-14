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
