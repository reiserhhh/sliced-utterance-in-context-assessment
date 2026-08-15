# SUICA M4-S — The Selection Line

Line opened 2026-08-16, by the owner's direction: pursue the
selection conjecture on BOTH synthetic and real data. The
conjecture (the owner's, arriving from the identity era's mechanism
results): **the gauge reads frames — but WHICH frames a person
chooses is person-owned; selection-proximity should imply
personality-proximity.** This is the rind model's choice channel
returning with a mechanism: the context meter becomes a person
reader when the person picks the contexts.

The claim decomposes (adjudication standard for every S-leg):
**(a)** selection is a person-stable signature — already supported
at the program's strongest real-data tiers (choice-axis stability
5/5 holdout; H6 politics/news → openness, lockbox-confirmed
r=+0.096 q=.006); **(b)** selection-similarity ⇒ TRAIT-similarity —
NOT a theorem but a coupling strength, false in worlds where
selection is driven by non-trait identity. The synthetic track
measures (b) as a LAW OF THE COUPLING (with the γ=0 falsification
arm); the real track measures (b) as a corpus fact with the
direction geometry (T8) handled.

Tier: EXPLORATORY throughout. The ledger controls. Standing rules
1–33 and ALL conventions bind (#43 planner-arithmetic; #56
inheritance; #57 pilot second moments; #59/#60 estimand
non-degeneracy and shared components; #61 prediction bands; #62
channel coverage; #63 frame-controlled forms; #64 sign
conventions). Execution conventions as always; `suica_core/`, k2b,
P3b/v2 instruments READ-ONLY.

## REAL-DATA GOVERNANCE (binding on every SR-leg)

`docs/SUICA_REALTEXT_GOVERNANCE.md` R-G1..R-G8 in force: **no
person claims, ever** (corpus-level aggregate statistics only); NO
cross-corpus author linkage; committed artifacts and reports carry
NO user text, NO user IDs, aggregates only (`results/` stays
gitignored regardless); the Essays confirm-half LABELS remain
sealed and untouchable (one lockbox opening remains); the native
corpus stays paused (owner 2026-07-12; not unpaused by this line);
identity-flavored stability claims carry split-half (T6″-pattern)
forms. Data access per `docs/DATA_ACCESS.md`; sources read from the
private repo paths, never copied into this repo.

## Line charter

- **S1 — the choice-enabled generator** (synthetic; registered
  below): endogenous context selection with a coupling knob γ
  (trait-driven ↔ style-driven), certified.
- **S2 — the transfer law** (synthetic; register after S1): sealed
  r_transfer(γ) curve with the γ=0 null and T8 direction handling.
- **SR0 — the real-data reconnaissance** (registered below;
  artifact/data-manifest only, STRICT no-peeking): pin the
  selection-signature objects (per-user subreddit distributions /
  the 12 choice axes), gold labels, split-half feasibility,
  reliability ceilings, and SR1's power analysis — computing NO
  selection×trait statistic of any kind.
- **SR1 — the selection-geometry test on PANDORA** (register ONLY
  after SR0): the Mantel-style pairwise test, sealed, permutation
  null, direction geometry, R-G compliant.

---

## M4-S1 — the choice-enabled generator

**REGISTERED 2026-08-16, BEFORE RUN.** Planner: this document's
author; executor: dispatched agent. Instrument leg: certificates
only; the sharp law is S2's.

### The extension (rules 9/12 — minimal extraction with provenance; the v2 lineage)

`build_choice_world(author_seed, frame_seed, phi_slow, w_style,
beta, gamma)` inside `scripts/run_suica_m4_s1_choice_generator.py`,
extending the v2 builder (imported by file, hashes verified).
Mechanism: per-author preference over the family's 4 contexts,

    pi_a = softmax( beta · [ gamma · u(trait_a) + (1−gamma) · v(style_a) ] )

with u, v PINNED deterministic 4-dim projections (executor pins
them from the world's own loadings-derived coordinates, file:line,
decision rule: the first four principal author-coordinates of each
channel, orthonormalized; disclosed in Part 0). The author's
occasion-to-context exposure is drawn from pi_a (the selection
mechanism IS frame-exposure choice — mechanistically the point);
beta = 0 recovers uniform exposure. The executor maps the layout /
common-channel indexing exactly (P3's report already charted it)
and pins the minimal exposure-reallocation that preserves the
shared-frame objects per context; if author-specific exposure is
structurally impossible without editing k2b, STOP as
**INFEASIBLE_CHOICE** (an instrument finding, the P3 pattern).

### Certificates (the leg IS the battery; #61-compliant bands everywhere)

- **C-S1a (neutral anchor):** at beta = 0, field levels replicate
  the v2/M1c share-.25 row distributionally (2·√2·SEM per cell,
  the C1′ pattern); selection frequencies uniform within
  multinomial bands.
- **C-S1b (signature):** at beta = beta* (pinned in Part 0 so that
  realized selection entropy drops by a declared, detectable
  margin — arithmetic from pi, no worlds), realized per-author
  frequency vectors match pi_a within multinomial noise
  (per-author χ² within band), and the signature is
  SPLIT-HALF STABLE (occasion-split correlation of frequency
  vectors, band from multinomial arithmetic).
- **C-S1c (coupling placement):** ACROSS authors within worlds,
  corr(selection-similarity, trait-similarity) is POSITIVE at
  γ = 1 and ZERO at γ = 0 (equivalence band from permutation
  arithmetic) — with γ = 0 worlds still showing the SAME
  selection-signature stability (identity-driven selection: stable
  but trait-uninformative — the (b)-decomposition made physical).
  Generous certificate bands; the quantitative law is S2's.
- Non-degeneracy (#59): none of C-S1b/c is forced — exposure draws
  are stochastic and the couplings live in u, v, γ; the shared
  component of any A/B comparison is named (#60): author-stream
  objects only.

### Design

γ ∈ {0, 1} × 24 worlds each + beta = 0 anchor arm 8 worlds (56
worlds total; each world carries the full 985-author panel, so
author-pair statistics are abundant). share 0.25, φ 0.60,
w_style = 1.0 (the identity channel ON — γ = 0 needs a live
non-trait driver). Salts `m4s1-author` / `m4s1-frameA` /
`m4s1-pilot`, master_seed 20260816. Rule-29 predicates; #57 bands
(variances only, margin 1.25); projection gate (rule 25): C-S1c
detection power ≥ 0.8 at γ = 1 with false-fire ≤ 0.1 at γ = 0,
from pilot 4 worlds/arm; once-only escalation to 48 worlds/arm ON
THIS GATE. Stages < 600 s each; target < 45 min.

### Routing (rule 16 — disjoint, covering, entailed)

| # | condition | outcome |
|---|---|---|
| 1 | G0/import/hash failure | **STOP** |
| 2 | exposure reallocation structurally impossible | **INFEASIBLE_CHOICE** (instrument finding; redesign handback) |
| 3 | projection fails after escalation | **NON_PROJECTABLE** |
| 4 | all certificates PASS | **CHOICE_GENERATOR_CERTIFIED** — S2 registrable |
| 5 | any certificate fails | **INSTRUMENT_DEFECT(name)** — handback |

Deliverables: the six as always;
`reports/SUICA_M4_S1_CHOICE_GENERATOR_REPORT.md`; ONE commit
`feat(m4-s): S1 — the choice-enabled generator — <SLUG>`.

---

## M4-SR0 — the real-data reconnaissance (STRICT no-peeking)

**REGISTERED 2026-08-16, BEFORE RUN.** Planner: this document's
author; executor: dispatched agent. Artifact/data-manifest leg —
**it computes NO statistic linking selection to any label**, and
its script's Part 0 enumerates every quantity it is allowed to
produce (the no-peek gate is CODE, not intention).

### Mandate

1. **Sources pinned** (paths, sizes, columns; NO content beyond
   schema + row counts in the report): the raw PANDORA comment
   table (`data_sets/PANDORA_official/all_comments_since_2015.csv`
   — verify the subreddit and timestamp fields exist),
   `author_profiles.csv` (gold labels; verify the Big5 columns and
   the N=1401 gold cohort's identifiability BY COUNT ONLY), the
   prepared Big5 CSV (1401 rows), and the choice-channel lineage
   code in this repo (`scripts/suica_v2_lib.py` and the v2-era
   choice constructions; pin file:line of the 12-axis constructor
   or report NOT_FOUND honestly).
2. **The selection-signature object DEFINED** for SR1: per-user
   subreddit frequency vectors over a pinned vocabulary (frequency
   floor declared from counts alone), plus the 12-axis projection
   if its constructor is located; sparsity and coverage statistics
   (selection-side ONLY).
3. **Split-half feasibility:** timestamp-based halves per user
   (T6″-pattern); per-user comment counts distribution; the
   stability CEILING estimated from selection-side split-half
   agreement (labels untouched).
4. **SR1 power analysis:** N, pair counts, Mantel permutation
   plan, minimum detectable Mantel-r at the declared α — from
   selection-side reliabilities and label-side variances computed
   SEPARATELY (never jointly).
5. **R-G compliance block:** the report carries aggregates only;
   no user IDs, no text excerpts, no per-user rows; Essays and
   native corpus untouched; no cross-corpus linkage.

### Hard no-peek gate

The script computes selection-side objects and label-side
MARGINALS (variances, counts) in SEPARATE stages that never join;
any joint selection×label quantity is structurally absent from the
code (G-SR0 verifies by enumeration of produced artifacts; rule 24
tables generated). Violation = the leg is void.

### Routing

| # | condition | outcome |
|---|---|---|
| 1 | a pinned source missing/schema-broken | **SOURCE_GAP(name)** — the manifest reports what exists; SR1 blocked pending owner/planner |
| 2 | all sources pinned, signature object defined, power adequate | **SR1_READY** — SR1 registrable |
| 3 | sources pinned but power inadequate at N | **UNDERPOWERED_DESIGN** — the analysis says what N or reliability would suffice; SR1 blocked |

Deliverables: the six as always;
`reports/SUICA_M4_SR0_RECON_REPORT.md` (aggregates only); ONE
commit `feat(m4-s): SR0 — real-data reconnaissance — <SLUG>`.
Budget: no world generation; data reads chunked (the comment table
may be large — streamed counting, memory-bounded, stages < 600 s).
