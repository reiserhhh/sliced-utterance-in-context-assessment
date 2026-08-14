# SUICA M4-Q — The Transport Line

Line opened 2026-08-14, on the P-line's close. Question: **what
survives frame refreshment?** The P-line proved the deployed
relation-field gauge reads frame-agreement (appendix II: gradient
~88% frame-owned, cross-frame levels near zero, injected boost
96–97% frame-vs-frame). Appendix N's instrument-role typing says
cards dominate the gauge ~4.5× at trait reading. The missing
mechanism half: **do CARD readings transport across frames?** If
cards transport where the gauge does not, the taxonomy completes —
cards read persons, the gauge reads frames — with both halves
measured by ONE device (P3b's certified split-seed instrument). If
cards are frame-locked too, K-R1's scaffold universality
("person content has no frame-free expression in this family")
extends from the field to the card layer — a deeper claim either
way.

Tier: EXPLORATORY, label-free, synthetic. The ledger controls.
Registrations before run, append-only. Standing rules 1–32 bind;
ALL conventions in force, including the P-line's four (#55
NULL-first classifications; #56 inheritance is not exemption; #57
pilot correlations never consumed — projections/bands use
independence with a stated margin, df-inflation licenses variances
only; #58 pivots carry sub-cases). Execution conventions as the
M/N/P lines (ONE commit per leg `feat(m4-q): ...`, never amended,
never pushed; chunked foreground stages < 600 s; `suica_core/`, k2b
and the P3b instrument READ-ONLY — Q-legs import the instrument by
file with provenance).

## Line charter

- **Q1 — card transport under frame refreshment** (registered
  below).
- **Q2 — the tax under refreshment** (named): does the tax curve
  κ(V) survive frame-fixed scoring? Register only after Q1.
- **Q3 — reader-side vs generator-side refreshment on one design**
  (named): the two T9 layers compared head-to-head.

---

## M4-Q1 — card transport under frame refreshment

**REGISTERED 2026-08-14, BEFORE RUN.** Planner: this document's
author; executor: dispatched agent. No seal (bounded classifications,
split leans).

### Question and device

Same A/B paired worlds as P3c (P3b's certified instrument, imported
by file with provenance; C2 battery re-run on 4 fresh probes; C1′
anchor on R_nat as instrument certificate). NEW quantities at the
CARD layer: per world-pair,

- **C_nat** — the published card-level b-recovery statistic of the
  A-world (cards from A scored against A's b-truth in card space);
- **C_ref** — A's cards scored against B's b-truth cards (same
  persons, fresh frame; author-indexed card vectors, cosine per
  author, mean — the card-layer analogue of R_refresh).

**Rule-12 delegation with decision rule:** the card statistic is
THE published card-level b-recovery used in K-R1's instrument-role
comparison (the ~4.5× vs the gauge; appendix N) — the executor pins
its source object file:line in Part 0 and reuses it verbatim for
C_nat; C_ref replaces only the truth-side card panel with the
B-world's, everything else identical. If the published statistic is
not expressible as author-indexed card vectors admitting
cross-world scoring, STOP as INEXPRESSIBLE (an instrument finding).

### Design

share 0.25 × φ ∈ {0.05, 0.98} × 384 A/B pairs each (768 pairs,
1536 worlds; the gauge quantities R_nat/R_refresh are ALSO computed
on the same pairs as a free within-leg replication of P3c's
levels). Salts `m4q1-author` / `m4q1-frameA` / `m4q1-frameB` /
`m4q1-pilot`, master_seed 20260814.

### Part 0

- **G0q1 (bit-exact).** (i) P3c's endpoint dual table and D_grad /
  range_ref values verified against `results/m4_p3c_transportable_gradient/`;
  (ii) the K-R1 4.5× comparison's numbers located at source (the
  card attenuation 0.827-family values; quote verbatim, rule 24);
  (iii) instrument hashes match P3b's persisted function/file
  sha256s. Mismatch → STOP.
- **G1q1 (rule 10).** (a) C2 battery re-run PASS; (b) the C_ref
  operator's zero-point identity: scoring A's cards against A's own
  truth cards through the C_ref code path reproduces C_nat
  bit-exactly; (c) at s… (no injection in this leg — clause (c) is
  the A/B frame-difference proof, inherited).
- **G2q1 (pilot).** 4 pairs × both φ; rule-29 predicate on C_nat,
  C_ref (domain: card cosines in [−1, 1], null 0, saturation
  |·| ≥ 0.995); equivalence bands ε_C (for C_ref vs 0) and ε_L
  (for the transport loss) computed df-inflated, VARIANCES ONLY
  (#57: independence with margin 1.25 on any covariance-dependent
  SE, stated).
- **G3q1 (rule 25).** Projection (B_proj = 2000) at truths
  {CARDS_TRANSPORT: C_ref = C_nat_pilot; CARDS_FRAME_LOCKED:
  C_ref = 0}: PASS iff both classifications reached at ≥ 0.8 power
  with ≤ 0.1 false-fire at 384 pairs/φ; once-only escalation to 768
  ON THIS GATE; else NON_PROJECTABLE.
- **G4q1.** Routing verified disjoint-and-covering,
  consequence-entailed, NULL-first; rule 24; stages: part0 150 s,
  pilot 60 s, worlds 4 chunks (~230 s), score+fit 180 s, finalize
  60 s; target < 40 min.

### Verdicts (rule 22; NULL-first)

Per φ and pooled: **V-Qa** C_ref vs 0 (NULL inside ±ε_C / POSITIVE
/ NEGATIVE / UNDERPOWERED); **V-Qb** the transport loss L_C =
C_nat − C_ref vs 0 (same classes, band ε_L). The card transport
share C_ref/C_nat is quoted ONLY as UNBUDGETED descriptive with its
CI (the P3b lesson). The gauge-side replication (R_refresh levels
vs P3c) is a reading, no gate.

### Leans (sides declared)

**L-1q1 [CARDS_TRANSPORT_SUBSTANTIAL (V-Qa POSITIVE with C_ref ≥
half of C_nat, descriptive) .40 / CARDS_PARTIAL (V-Qa POSITIVE,
smaller) .35 / CARDS_FRAME_LOCKED (V-Qa NULL) .15 / other .10]** —
the theory expects cards to carry b directly (post-map deviation
objects), but the P3c shock (gauge levels ≈ 0 cross-frame) tempers
confidence; K-R1's "no frame-free expression" could extend to the
card layer.

### Routing (rule 16 — disjoint, covering, consequences entailed)

| # | condition | outcome |
|---|---|---|
| 1 | G0q1/G1q1 failure or INEXPRESSIBLE | **STOP / INEXPRESSIBLE** |
| 2 | projection fails after escalation | **NON_PROJECTABLE** |
| 3 | C1′/anchor or C2 battery failure | **INSTRUMENT_DEFECT** |
| 4 | V-Qa POSITIVE and V-Qb NULL | **CARDS_TRANSPORT_FULL** — card reading crosses frames without measurable loss; the taxonomy completes (cards read persons, the gauge reads frames) |
| 5 | V-Qa POSITIVE and V-Qb POSITIVE | **CARDS_TRANSPORT_PARTIAL** — real transport, real loss; both quantified (loss share descriptive) |
| 6 | V-Qa NULL | **CARDS_FRAME_LOCKED** — the scaffold universality extends to the card layer; appendix N's 4.5× re-reads as within-frame only; major theory note |
| 7 | V-Qa NEGATIVE | **CARD_INVERSION_NAMED** — new phenomenon; theory note |
| 8 | any UNDERPOWERED among V-Qa/V-Qb (no higher cell) | **UNDERPOWERED** (levels and bands reported) |

### Deliverables and budget

`scripts/run_suica_m4_q1_card_transport.py`;
`results/m4_q1_card_transport/` (gitignored);
`reports/SUICA_M4_Q1_CARD_TRANSPORT_REPORT.md` (generated tables);
outcome append HERE; one ledger row (EXPLORATORY); exactly ONE
commit `feat(m4-q): Q1 — card transport under frame refreshment —
<SLUG>`, never amended, never pushed; suite green first. 1536
worlds (+escalation ×2) + pilot; every stage < 600 s.
