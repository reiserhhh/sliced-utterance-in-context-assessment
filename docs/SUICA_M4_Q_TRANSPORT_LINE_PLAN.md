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

### M4-Q1 outcome (appended after execution; registration above unedited)

**INEXPRESSIBLE — routing cell 1; modifiers: none.**
STOP / INEXPRESSIBLE. Stopped at the registration's own expressibility clause, answered by code in Part 0 + the demonstration. **0 measurement
pairs drawn** (16 demonstration pairs on the pilot salt). Harness
`scripts/run_suica_m4_q1_card_transport.py`; report
`reports/SUICA_M4_Q1_CARD_TRANSPORT_REPORT.md`; artifacts
`results/m4_q1_card_transport/` (gitignored).

**THE CARD LAYER'S b-TRUTH IS FRAME-FREE BY CONSTRUCTION, SO TRUTH-SIDE FRAME
REFRESHMENT IS A NULL OPERATION THERE.** The registration's own expressibility
clause is the right exit, and it was reached by code rather than by argument.

**The statistic has two readings and the registration does not disambiguate
(RN-Q1-1).** Appendix N says "card attenuation 0.827 vs field recovery 0.178",
and two persisted objects round to 0.827: the CLOSED-FORM prediction
`r_card_b_pred_raw` = 0.8271784593117322 (`scripts/run_suica_m4_k2b_t4_branch.py:533`, `arm_predictions`) and
the MEASURED pooled `r_card_b_raw` = 0.8266850143926395
(`scripts/run_suica_m4_k2b_t4_branch.py:392-457` → `pooled_card_stats`). The companion 0.178
(0.177888649457317) is measured, which favours the second; the digits favour
the first. **Both were pinned and both carried through the expressibility test,
because the STOP has a different route under each.**

- **Reading A (closed form): INEXPRESSIBLE flatly.** `arm_predictions` is pure
  algebra over retained cell sizes and four variance shares. It takes no world,
  touches no author, forms no vector, and **has no truth side to replace**.
- **Reading B (measured): expressible, but the estimand is degenerate.** The
  64-dim per-author vectors do exist inside `card_channel_frame` (the card
  `full` and the truth `trait`), contracted row-wise — so a cross-world path is
  constructible, and it was built and **proven bit-exact against k2b**
  (G1q1(b) = True on 16 checks: the path reproduces k2b's own
  frame byte-for-byte and its pooled statistic exactly when both arguments are
  A). But its truth side is `world['trait']` — a pure AUTHOR-stream object.

**Both readings agree on the STOP.**

**The registration's phrase names an object that does not exist (RN-Q1-2).**
"C_ref replaces only the truth-side card panel" presupposes the truth side is a
card panel. It is not: the estimate side is a card (a centred channel mixture
with the frame channel excluded by construction, k2b:422-428) while the truth
side is world['trait'][idx], scripts/run_suica_m4_k2b_t4_branch.py:410 -- the BARE LATENT TRAIT ARRAY, not a card. The harness replaced exactly the object that can be
replaced and reported the mismatch. The trap was avoided explicitly (RN-Q1-3):
`trait_c` feeds BOTH the card and the centred truth, so swapping the world
wholesale would have produced a B-world replication rather than a cross-world
score; only the truth-side trait was parameterised.

**The result: C_ref ≡ C_nat, identically.** Not "within noise" — to the last
bit, on every pair at both φ (True, max |L_C| = 0.0). A
and B share the author seed by construction — which is precisely what C2a
certifies — so B's trait is bit-identical to A's (True) and
swapping the truth side changes nothing.

**The contrast that makes the finding sharp** — same pairs, same device:

| φ | n | C_nat | C_ref | L_C | R_nat | R_refresh | R_nat − R_refresh |
|---|---|---|---|---|---|---|---|
| 0.05 | 8 | 0.7846736299843141 | 0.7846736299843141 | 0.0 | 0.11439067415413948 | 0.0009056149726381045 | 0.1134850591815014 |
| 0.98 | 8 | 0.6763296428445553 | 0.6763296428445553 | 0.0 | 0.1362886208874512 | -0.007950204144913695 | 0.14423882503236488 |

The gauge's b-only truth is `emit_panel(..., active=("mu","common"))` — it
**contains the frame** — so B's truth panel genuinely differs
(True) and R_refresh moves away from R_nat by 0.12886194210693314 on
average, replicating P3c's near-zero cross-frame levels as a free within-leg
reading. **The two layers differ precisely in whether their truth object
carries the frame.**

**What this does to appendix N's ~4.5×.** The gap is not a contest between two
readers of one target: the card statistic's target is the person (trait), while
the gauge's b-only target is person PLUS frame. The Q-line's question therefore
cannot be answered by refreshing the truth side — at the card layer there is no
frame in the truth to refresh. The taxonomy the line set out to complete is
settled by what each layer's truth object CONTAINS, by inspection plus proof
rather than by measurement. (Ratio note, rule 30: the persisted operands give
4.6499788594449205 and 4.6472049617252065; appendix N's "~4.5×" carries a
tilde and no artifact holds a ratio key — the number is prose, not a computed
object.)

**Why the STOP rather than the routing.** Had the leg proceeded, V-Qa would have
read POSITIVE (C_ref ≈ 0.78/0.68, far from 0) and V-Qb NULL (L_C ≡ 0), firing
**cell 4 CARDS_TRANSPORT_FULL** and publishing "card reading crosses frames
without measurable loss" as a MEASUREMENT. It is an identity. Cell 4's
consequence is not entailed by an identity (#46/#54), so the expressibility STOP
is the correct exit and the only honest one.

**A measurable neighbour, NAMED NOT RUN.** Swapping the ESTIMATE side instead —
scoring B's cards against the shared trait and comparing to A's — is a
frame-sensitivity reading of the card estimate, which does differ (slow, noise
and int are frame-stream objects). That is a DIFFERENT estimand from the
registered truth-side swap; the executor does not substitute estimands. The
demonstration's per-φ C_nat spread across A-worlds is the within-frame
variability such a reading would formalise.

**Gates.** G0q1 PASS — P3c's values, the 4.5× operands bit-exact at source, and
the instrument hashes matching P3b's persisted sha256s (True /
True). C2 PASS on 4 fresh probe pairs. G1q1(b) PASS.
G2q1/G3q1/C1′ not reached — the expressibility clause fires first.

**Rule events.** Rule 13/25/27: not reached. Rule 26: no bounded winner. Rule
29: the predicate was defined for the card cosines and not exercised. Rule 30:
every cited constant read from its persisted source; the card statistic carries
two source pins and both candidate values.

**Executor self-report.** Two standing anomalies, both resolved before any
number existed: A-1 the dispatched interpreter is absent (a pinned CPython
3.12.12 venv built from the lockfile); A-2 `timeout(1)` is absent on macOS
(foreground stages under explicit sub-600 s timeouts). No hypothesis-relevant
number was ever computed — the leg stopped before its first measurement arm and
the demonstration quantities are identities.

**Registration-defect candidates (2).** (1) **The estimand was degenerate at
registration time and the degeneracy was computable from persisted sources**:
the card statistic's truth side is `world['trait']` (k2b:410) and P3b's own
certified channel taxonomy places `trait` in the AUTHOR stream — the two facts
sit in the repo and their conjunction forces C_ref ≡ C_nat before any world is
drawn. This is the #43/#44/#51/#53/#56 genus once more, now at the level of an
estimand's *definition* rather than its precision. (2) **Routing cell 4's
consequence is not entailed under the degenerate case**: the cell would have
fired on an identity and published it as a measurement. The #46/#54 mechanical
check verifies disjointness and covering; it does not verify that a cell's
antecedent can only be reached by measurement. The convention worth adding is
that a routing cell whose antecedent is satisfiable by construction must be
guarded by a non-degeneracy clause — the card-layer analogue of rule 10.
