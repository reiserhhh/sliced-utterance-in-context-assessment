# SUICA D5 — The rule machine, replayed

Registered in `docs/SUICA_DEFENSE_PHASE_PLAN.md` § "D5 — The rule machine,
replayed (the defense phase's closing leg)", commit `eb972ea`, BEFORE run.
Executor: dispatched agent (implementation and execution only). Executed
2026-08-10. Document-space only.

**Verdict (G2R, controlling): `REPLAY-PARTIAL`** — five named coverage gaps
(#15, #16, #34, #40, #41) plus one named numbering gap in the pre-#9 era.
The second reading and why it was not adopted are in §5.

---

## Part 0 — source inventory and the rule set, written before any classification

### 0.1 Purity (G1R)

Document space only. The harness imports stdlib alone
(`os`, `re`, `sys`, `time`), asserts at entry and exit that no `suica*`
module is in `sys.modules`, generates no world, and opens no `results/`
tree. It reads tracked `.md` files under `docs/` and `reports/` and writes
two of them. No artifact was recomputed and no number in this report is a
measurement — this leg audits the METHOD, not the numbers. **No `results/`
path was cited for context either.** G1R **PASS**.

### 0.2 Sources read

| source | what it supplied |
|---|---|
| `docs/SUICA_DEFENSE_PHASE_PLAN.md` | the D5 registration (binding); defects #39 (D1 adj.), #40 (D2 adj.), #41 (D3 outcome + adj.); the salt-embedding and aggregation-provenance conventions |
| `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md` | defects #1–#4 (M4-F4/F6/F7/F8 outcomes + adjudications) and rules 1–4 as created |
| `docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md` | defects #5–#8 (M4-G3, M4-H2, M4-H3, M4-J2) and rules 5–8 as created; the "first seven were defects in RULES" enumeration that fixes the pre-#9 order |
| `docs/SUICA_M4_F_PANEL_DESIGN_SYNTHESIS.md` §4 | "Four planner registration defects of one family" — the F-line's own count |
| `docs/SUICA_M4_G_OBJECTIVE_LINE_SYNTHESIS.md` §4 | "Two further planner registration defects" — the G-line's own count, one of which produced no rule |
| `docs/SUICA_DISPLACEMENT_PROBLEM_RESOLVED.md` | "Seven standing methodological rules, every one paid for by a planner registration defect" — the 2026-08-03 count |
| `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md` | the standing-rules 1–8 header; defects #9–#26; rules 9–17 as created; the execution conventions |
| `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md` | defects #27–#38; rules 18–21 as created |
| `docs/SUICA_IDENTITY_THEORY_V1.md` (appendices) | defect↔rule cross-references (#20/#21/#22/#30/#31/#33/#40) used to check the registry's rule attributions |
| `docs/CLAIMS_LEDGER.md` | leg-level defect citations; ledger row format |
| `reports/*.md` (leg reports) | executor-side timing of catches (#9, #13, #18–#20, #22, #24, #27, #29, #31–#33, #38, #41) |
| `docs/SUICA_M4_K_IDENTITY_LINE_SYNTHESIS.md`, `docs/SUICA_M4_L_TYPOLOGY_LINE_SYNTHESIS.md`, `docs/SUICA_THEORY_ROUTE_INDEX.md` | range citations, picked up by the scan |

### 0.3 The rule set as it stands today (1–21), one line each, with provenance

| rule | paid for by | one line | origin |
|---|---|---|---|
| 1 | #1 | Designed-null gates state their aggregation rule (per-cell vs trend) and multiplicity treatment before the run. | M4-D plan, M4-F4 outcome |
| 2 | #2 | Pre-state the scale at which the target is measurably non-zero and the MDE; a noise-floor null is UNDERPOWERED, not a null. | M4-D plan, M4-F6 adj. |
| 3 | #3 | Verify a non-zero causal channel at every tested parameter value from the generator; a null on an inert knob is VACUOUS. | M4-D plan, M4-F7 adj. |
| 4 | #4 | Every gate bounds MATERIALITY via an equivalence form; never nil significance on a known-nonzero quantity. | M4-D plan, M4-F8 adj. |
| 5 | #5 | Justify the analysis grain for power; do not inherit the line's default. | M4-G plan, M4-G3 adj. |
| 6 | #6 | Define the winner jointly over target AND safety, never by the target's extremum. | M4-G plan, M4-H2 adj. |
| 7 | #7 | Where the safety check has graded levels, state which level qualifies and report the best arm at each. | M4-G plan, M4-H3 adj. |
| 8 | #8 | Verify every factual claim cited to motivate a lean against persisted artifacts at full precision before committing the registration. | M4-G plan, M4-J2 adj. |
| 9 | #9 | A constructed instrument's registration pins every convention that changes its hypothesis-relevance, or pre-delegates with an explicit decision rule; mid-leg ambiguities resolve before any hypothesis-relevant number and ALL readings are reported. | M4-K plan, K1 adj. |
| 10 | #11 | A registered manipulation is derived from generator SOURCE and Part 0 proves non-degeneracy before arms. | M4-K plan, K1b adj. |
| 11 | #12 | Every registered gate is checked for arithmetic satisfiability under the cited anchor statistics at registration time. | M4-K plan, K1b adj. |
| 12 | #10 + K1c's two rule-9 ambiguities | Manipulations and channels are specified by generator SOURCE OBJECT (file:function/variable), never by knob names alone. | M4-K plan, K1c adj. |
| 13 | none (L-1's fragility) | Interval clauses name their resampling spec; verdict stability checked at ≥10× B; a boundary inside MC error scores BOUNDARY. | M4-K plan, K1d adj. |
| 14 | #20 | Cross-scale/cross-instrument leans pin the LINK function, or are re-designed within-instrument. | M4-K plan, K2b adj. |
| 15 | #17 + #21 | The adjudication space is a PARTITION, verified by ENUMERATION at registration time. | M4-K plan, K2c adj. |
| 16 | #22 | The rule-15 enumeration covers the FULL adjudication object — cells, lean predicates, pivot routing — as one truth table. | M4-K plan, K2d adj. |
| 17 | #25 + #26 | Every registered stratum and task carries a generator-derived realizability argument or a Part-0 realizability check with a pre-declared fallback ladder. | M4-K plan, K3 adj. |
| 18 | #27 | Rule-11 satisfiability is checked JOINTLY across all clauses sharing generative knobs. | M4-L plan, L1 adj. |
| 19 | #30 | Every lean bar is derived from the theorem's OWN quantity and scale, and names which theorem-quantity it shadows. | M4-L plan, L1 adj. |
| 20 | #31 + #32 | An empty joint condition-set STOPS the leg before arms, unless empty-set was pre-declared adjudicable. | M4-L plan, L2 adj. |
| 21 | #37 | CI-containment bars on instrument validations carry a registered absolute-error budget. | M4-L plan, L3 adj. |

Conventions in force (unnumbered): round-trip CSV parsing; ≥4-world pilots
with df-awareness for sd-based gates; Part-0 verification (not assertion) of
bit-identity claims; foreground chunked stages with Part 0 written before
arms; aggregation provenance (`decision.json` aggregates name their computing
function at file:line); salt embedding in sealed artifacts; legacy-anchor
parser naming.

### 0.4 The pre-#9 reconciliation (G0R's explicit requirement)

Four counts exist in the corpus and they disagree. They disagree because
they were written on different dates and count different objects:

| source | count | what it counts |
|---|---|---|
| F-synthesis §4 | **four** | F-line only: F4, F6, F7, F8 |
| G-synthesis §4 | **two further** | G-line only: G3's grain defect (→ rule 5), and G1's 25% actionable-bar defect, "recorded as a registration critique with no lean re-scored on it" — **no rule at that date** |
| `SUICA_DISPLACEMENT_PROBLEM_RESOLVED.md` (2026-08-03) | **seven rules** | the rule set at arc close: aggregation, power, channel, materiality, grain, joint winner, graded levels — i.e. rules 1–7, adding the H-line's two (H2, H3) that the G-synthesis predates |
| M4-J2 record / M4-K plan header | **eight** | the first seven "were defects in RULES — aggregation, power, channel, materiality form, grain, winner definition, graded levels", plus J2's evidence defect as the eighth |

**Resolution adopted:** F(4) + G(1 rule-producing) + H(2) + J(1) = **8**, in
that chronological order, which is exactly the J2 enumeration's own ordering
and is confirmed by the next defect being labelled "ninth in the program's
account" (`docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md`, K1 adjudication). The
registry's #1–#8 assignment is therefore derived from the corpus, not invented
— and the registry **says so** in its numbering note.

**Rule-9 disclosure — both readings written.** Under a second reading that
counts every *recorded registration critique* rather than every
*rule-producing defect*, the pre-#9 era contains **nine** items: the extra is
G1's 25% actionable bar, which the G-synthesis records as a defect but which
the J2 enumeration does not number, because rule 6 was later paid for by H2's
instance of the same class. The registry adopts the eight-item reading and
annotates #6's row with the G1 instance. This is named as a gap in §5.

### 0.5 G0R — registry completeness (mechanical)

Harness: `scripts/run_suica_d5_rule_replay.py`. It scans every tracked `.md`
under `docs/` and `reports/`, restricted to lines containing the word
"defect", extracts `#N` citations and expands `#A–#B` ranges, and checks each
cited number against the registry.

Two corpus states are reported, because this harness is re-runnable and its
own deliverables cite defect numbers (see anomaly A-6): **AUDITED** = the
corpus D5 read, before this leg's documents existed; **REPRODUCIBLE** = the
corpus after this commit, which is what a later re-run sees. G0R passes in
both.

| metric | AUDITED (pre-deliverable) | REPRODUCIBLE (post-commit) |
|---|---|---|
| registry rows | **41** (contiguous #1..#41, 0 duplicates) | **41** |
| distinct defect numbers cited | **41** | **41** |
| citing lines | **103** | **118** |
| range citations expanded | **17** (`#9–#26`, `#27–#38`, `#31–#35`, D5's own `#1–#41` twice, …) | **24** |
| cited but absent from the registry | **0** | **0** |
| registry rows never cited numerically | **0** | **0** |
| **G0R** | **PASS** | **PASS** |

Per-number citation counts, REPRODUCIBLE state (mentions, not rows): #1=6
#2=7 #3=4 #4=4 #5=4 #6=4 #7=4 #8=4 · #9=13 #10=10 #11=9 #12=10 #13=8 #14=8
#15=16 #16=9 #17=10 #18=8 #19=9 #20=12 #21=12 #22=10 #23=10 #24=8 #25=14
#26=12 · #27=15 #28=10 #29=9 #30=18 #31=18 #32=12 #33=21 #34=11 #35=12 #36=13
#37=13 #38=11 · #39=5 #40=7 #41=7. (AUDITED state, same order: 3 4 2 2 2 2 2 2
· 6 8 7 8 6 6 12 7 8 6 7 9 9 7 7 6 12 10 · 13 8 7 15 15 10 18 9 10 11 11 9 ·
3 4 5.)

**Honest reading of the pre-#9 counts.** #3–#8 are cited numerically *only*
by D5's own `#1–#41` range: the era predates the `#N` convention. The
mechanical check would therefore be vacuous there, so the harness also scans
for the era's ORDINAL anchors and found all eight —
`M4-F4's G0 ambiguity` (M4-D plan L1368/L1401/L1836; F6 report L202),
`second registration defect of this kind` (M4-D L1494),
`third registration defect of the same family` (M4-D L1671),
`Fourth planner registration defect` (M4-D L1836),
`Fifth planner registration defect` (M4-G L617),
`sixth of its family` (M4-G L1749; H3 report L25),
`Standing rule (seventh)` (M4-G L1957),
`Eighth planner defect` (M4-G L2901).

---

## 1. The replay classification

Stage vocabulary, ordered: **REGISTRATION-TIME** (rule text, enumeration or
satisfiability check refuses the registration) < **PART-0** (a gate catches it
before arms) < **POST-HOC** (only adjudication catches it) < **UNCOVERED**
(no current rule addresses the class).

| # | family | covering rule(s) TODAY | today | historical | improved? |
|---|---|---|---|---|---|
| #1 | aggregation | 1 | REGISTRATION-TIME | POST-HOC | yes |
| #2 | power | 2, 5 | REGISTRATION-TIME | POST-HOC | yes |
| #3 | channel-liveness | 3, 8 | PART-0 | POST-HOC | yes |
| #4 | materiality | 4 | REGISTRATION-TIME | POST-HOC | yes |
| #5 | grain | 5, 2 | REGISTRATION-TIME | POST-HOC | yes |
| #6 | winner-definition | 6 | REGISTRATION-TIME | POST-HOC | yes |
| #7 | graded-safety | 7, 6 | REGISTRATION-TIME | POST-HOC | yes |
| #8 | fact-verification | 8 | REGISTRATION-TIME | POST-HOC | yes |
| #9 | instrument-pinning | 9, 12 | REGISTRATION-TIME | PART-0 | yes |
| #10 | fact-verification | 8, 12 | REGISTRATION-TIME | POST-HOC | yes |
| #11 | degeneracy | 10, 12 | PART-0 | POST-HOC | yes |
| #12 | satisfiability | 11 | REGISTRATION-TIME | PART-0 | yes |
| #13 | degeneracy | 10, 12 | PART-0 | PART-0 | same (the rule already worked) |
| #14 | fact-verification | 8 | REGISTRATION-TIME | PART-0 | yes |
| #15 | **clause-direction** | **none** | **UNCOVERED** | PART-0 | **no** |
| #16 | **gate-stage-feasibility** | **none** | **UNCOVERED** | PART-0 | **no** |
| #17 | partition | 15, 16 | REGISTRATION-TIME | POST-HOC | yes |
| #18 | aggregation | 1, 13 | REGISTRATION-TIME | PART-0 | yes |
| #19 | satisfiability | 11, 9, 18 | REGISTRATION-TIME | PART-0 | yes |
| #20 | link | 14 | REGISTRATION-TIME | PART-0 | yes |
| #21 | partition | 15, 16 | REGISTRATION-TIME | POST-HOC | yes |
| #22 | partition | 16, 15 | REGISTRATION-TIME | PART-0 | yes |
| #23 | graded-safety | 7, 16 | REGISTRATION-TIME | POST-HOC | yes |
| #24 | fact-verification | 8 | REGISTRATION-TIME | PART-0 | yes |
| #25 | realizability | 17 | PART-0 | PART-0 | same |
| #26 | realizability | 17 | PART-0 | PART-0 | same |
| #27 | joint-satisfiability | 18, 11, 20 | REGISTRATION-TIME | PART-0 | yes |
| #28 | degeneracy | 10, 3 | PART-0 | POST-HOC | yes |
| #29 | instrument-pinning | 9, 19 | REGISTRATION-TIME | PART-0 | yes |
| #30 | shadow-fidelity | 19 | REGISTRATION-TIME | POST-HOC | yes |
| #31 | empty-set | 20, 18 | REGISTRATION-TIME | PART-0 | yes |
| #32 | empty-set | 20, 18 | REGISTRATION-TIME | PART-0 | yes |
| #33 | shadow-fidelity | 19 | REGISTRATION-TIME | PART-0 | yes |
| #34 | **lean-identifiability** | **none** | **UNCOVERED** | POST-HOC | **no** |
| #35 | precision-budget | 2, 21 | REGISTRATION-TIME | POST-HOC | yes |
| #36 | materiality | 4, 21, 19 | REGISTRATION-TIME | POST-HOC | yes |
| #37 | precision-budget | 21, 4 | REGISTRATION-TIME | POST-HOC | yes |
| #38 | grain | 5 | REGISTRATION-TIME | PART-0 | yes |
| #39 | fact-verification | 8, 12 | REGISTRATION-TIME | PART-0 | yes |
| #40 | **prose-citation** | **none** | **UNCOVERED** | POST-HOC | **no** |
| #41 | **prose-citation** | **none** (strict rule 8); rule 8 under a broad reading | **UNCOVERED** | PART-0 | **no** |

Full rows — where each defect is recorded, its one-line description, the rule
it paid for, and its family — are in the committed registry,
`docs/SUICA_DEFECT_REGISTRY.md`.

---

## 2. Coverage statistics

**Total defects: 41.** Per era: F/G-line (pre-#9) **8**, K-line **18**,
L-line **12**, defense **3**.

| catch stage | TODAY | HISTORICALLY |
|---|---|---|
| REGISTRATION-TIME | **30** | 0 |
| PART-0 | **6** | 21 |
| POST-HOC | **0** | 20 |
| UNCOVERED | **5** | 0 |

**Improved vs historical: 33 improved, 3 same, 5 not-improved.** The three
"same" are #13, #25 and #26 — all PART-0 both times, and all three are the
machine already working (#13 is the 74-second rule-10 stop; #25/#26 are
rule-17's realizability ladders, which were pre-declared fallbacks before the
rule existed). The five not-improved are exactly the five UNCOVERED classes:
historically they were caught by executor vigilance or a pre-declared
fallback, and no rule enacted since would catch them.

**The single most consequential number is POST-HOC = 0.** Historically
20 of 41 defects (49%) were only found at adjudication, after the numbers
existed — the expensive kind, because a post-hoc catch either voids a leg or
retypes a published claim. Under today's rule set, every covered defect is
refused at registration or stopped in Part 0. The residual risk has moved
entirely into the UNCOVERED column: five classes that would still be caught
late, or not at all.

**Family distribution** (22 families; registry §"Family counts"):
fact-verification **5** (#8, #10, #14, #24, #39); degeneracy 3 (#11, #13,
#28); partition 3 (#17, #21, #22); then 11 families of two — aggregation,
empty-set, graded-safety, grain, instrument-pinning, materiality,
precision-budget, prose-citation, realizability, satisfiability,
shadow-fidelity; then 8 singletons — channel-liveness, clause-direction,
gate-stage-feasibility, joint-satisfiability, lean-identifiability, link,
power, winner-definition. **fact-verification is the program's single most
recurrent failure mode at 5/41, and it grows to 7/41 if the two
prose-citation defects are read as rule-8 instances — which is exactly what
the corpus does when it types them "rule-8-in-prose".** That is the argument
for proposal P3.

---

## 3. Proposed refinements — status PROPOSED, enactment is the planner's

Three, the registered maximum, each motivated by named defects. None is
enacted here; none is applied to any past adjudication.

**P1 (proposed rule 22) — clause DIRECTION is declared.** Every band,
tolerance or bound clause states whether it is one-sided or two-sided AND
which side improvement lies on; a two-sided band on a quantity where one
direction is an improvement is a registration defect. *Motivated by #15*
(G3′'s "within 2×" sd clause was two-sided, so it failed when the fresh
variance was SMALLER — an equivalence band that punished improvement). The
record itself states the gap: "rule 11 checks satisfiability, not clause
DIRECTION — direction is the registrant's job and this one was wrong." Since
then the lesson has travelled as prose ("one-sided clauses stated as
one-sided (defect #15's lesson)"), never as a rule.

**P2 (proposed rule 23) — clauses declare that they CAN do their job:
evaluability and discriminability.** For every gate: name the stage at which
all its inputs exist, and place it there. For every lean that names two
alternatives: name the observable that differs between them under the
registered design, or re-design. *Motivated by #16* (G1d was listed among
"Part 0 gates" though unmeasurable before the intact arm exists) *and #34*
(W-4 had no clause able to distinguish "the constant is wrong" from "the
partition is wrong"; only a post-hoc TRUE-groups control could tell them
apart). Rules 11/18/20 check arithmetic and joint satisfiability — whether a
clause CAN be satisfied — and rule 19 checks that the bar is on the right
quantity. Neither checks whether the clause can be *evaluated when it is
scheduled* or can *separate the alternatives it names*.

**P3 (proposed rule 24) — rule 8 extends to published prose.** Every numeric
or enumerative claim in a synthesis, appendix, registration scope statement or
ledger row is verified against its artifact or its own enumeration before the
document is committed — not only the facts cited to motivate a lean.
*Motivated by #40* (four wrong claims in appendix and synthesis prose: "five
arms" for four, "≤ 0.0045" against 0.004512746557818383, "0/32 worlds" against
0/192 arm-worlds, "every reading" against a pooled Spearman of 0.985) *and
#41* (the D3 registration's scope arithmetic wrong twice in one section).
Both are typed in the corpus itself as "rule-8-in-prose" — an extension named
three times and never enacted. Both were caught only because a dedicated
adversarial pass (D2) or a scope reconciliation (D3's Part 0) happened to run;
neither was mandated by any rule. Note the asymmetry P3 would remove: rule 8
already makes a wrong motivating fact fatal (#8's "a wrong motivating fact
makes the control test the wrong thing"), while a wrong published number is
currently governed by nothing.

---

## 4. Gates

| gate | result |
|---|---|
| **G0R** registry completeness | **PASS** — 41 rows, contiguous #1..#41, 0 duplicates; 41 distinct numbers cited over 103 citing lines and 17 expanded ranges; 0 cited-but-absent; 0 rows never cited. Pre-#9 era reconciled explicitly in Part 0 §0.4 against the F-synthesis's four, the G-synthesis's two more, the displacement doc's seven rules and the J2/K-header eight, with the alternative nine-item reading written. |
| **G1R** purity | **PASS** — stdlib-only harness, `sys.modules` audited at entry and exit (0 `suica*`), no world generated, no `results/` path opened or cited. |
| **G2R** verdict | **`REPLAY-PARTIAL`** — gaps named in §5. |

---

## 5. Verdict, and the reading that was not adopted

**`REPLAY-PARTIAL`.** Named gaps:

- **G-a (numbering).** The pre-#9 era admits two defensible counts: **eight**
  (rule-producing defects, the J2 enumeration's own basis — adopted) and
  **nine** (every recorded registration critique, adding G1's 25%
  actionable-bar defect, which the G-synthesis records and the J2 enumeration
  does not number). The registry adopts eight and annotates #6 with the G1
  instance. Only the planner can retire the alternative.
- **G-b … G-f (coverage).** Five defect classes have no covering rule today:
  **#15** clause-direction, **#16** gate-stage-feasibility, **#34**
  lean-identifiability, **#40** and **#41** prose-citation. Proposals P1–P3
  address all five; none is enacted.

**The reading not adopted.** Read narrowly — "did the replay execute?" — the
verdict would be `REPLAY-COMPLETE`: all 41 defects are classified, G0R passed
mechanically, no defect's record was too thin to place, and UNCOVERED is an
output category the registration explicitly anticipates (it asks for proposals
about exactly that). That reading is available and is recorded here. It was
not adopted because a verdict of COMPLETE, published while five defect classes
have no covering rule and the era's own count is ambiguous, would state more
than this leg established. Rule 9's habit — resolve the ambiguity in writing,
report both readings — applies to the leg's own verdict as much as to its
instruments. The planner adjudicates.

---

## 6. Anomalies, with timing

- **A-1 (scanner, ~15 min in; before any classification number was reported).**
  The first harness run returned **G0R FAIL**: one cited number — a spurious
  ZERO — had no registry row. Cause: the citation regex `#\s*(\d{1,3})` matched the markdown
  heading `### 0.2 RN-10 — the Δ choice, and a proved registration defect` in
  `reports/SUICA_M4_L1_TYPED_WORLD_REPORT.md:91` — the third `#` of `###`
  followed by whitespace and `0`. Fixed by requiring no whitespace after `#`
  and no preceding `#`. **The fix changed the SCANNER only; no classification
  value changed**, and the classification table was authored in the harness
  before the first run, so no hypothesis-relevant judgement was made after
  seeing a count. Distinct numbers cited went 42 → 41, citing lines 108 → 103.
- **A-2 (precision, disclosed not special-cased).** Three lines in
  `docs/CLAIMS_LEDGER.md` (289, 290, 413) contain the word "defect" and also
  the lockbox tokens "opening #1" / "opening-#2" / "opening #2", so they are
  counted as citations of #1 (×1) and #2 (×2). This is a precision artifact of
  a keyword-scoped scan; **G0R needs recall** — every cited number must have a
  row — which is unaffected. Left in rather than filtered, so the counts in
  §0.5 are the raw scan's.
- **A-3 (numbering, resolved in Part 0 before classification).** The pre-#9
  count reconciliation, §0.4 — resolved to eight with the nine-item reading
  written, per rule 9.
- **A-4 (historical-stage ambiguity, disclosed at classification time).**
  Three rows carry a second reading, all recorded in the registry's note
  column: **#23** (the record places the defect in the planner's adjudication
  → POST-HOC adopted; "executed graded, as above" also reads as a pre-arms
  resolution → PART-0), **#24** (PART-0 adopted, since K2e's solved shares are
  Part-0 objects — K2e report L163 — though the defect is recorded in the
  adjudication), and **#36** (the L doc types it "rule-19 class, third of the
  #30/#33 family"; the replay reads it as squarely rule 4, nil-form on a
  known-nonzero quantity — both readings give REGISTRATION-TIME, so nothing
  downstream turns on it). **#5**'s historical stage is recorded POST-HOC
  though the agent flagged the underpowering before the adaptive arms; the
  four-value vocabulary has no mid-leg value and the leg fit no registered
  branch.
- **A-6 (self-reference, found at the final re-run, after the classification
  was complete and unchanged by it).** The harness scans `docs/` and
  `reports/`, so **its own deliverables enter the corpus it audits**: after
  the report, the plan append and the ledger row were written, citing lines
  went 103 → 118 and expanded ranges 17 → 24. G0R passed in both states and no
  classification changed, but two consequences are recorded. (i) §0.5 reports
  both corpus states, so a later re-run's numbers are predicted rather than
  contradicted. (ii) The failure mode is real: the ledger row's prose quoted
  the literal spurious token from A-1 verbatim, which the scanner then read as
  a citation of a defect number that does not exist — G0R FAILED on the
  leg's own writing. Fixed by wording the anomaly without the literal token
  in all three documents, **not** by teaching the scanner to ignore it: a gate
  that special-cases the number it dislikes is not a gate. The registry is
  intended to be a fixed point under re-running, and it is one only as long as
  prose about defect numbering avoids emitting tokens it does not mean.
- **A-5 (budget).** Wall time ≈ 33 min against a < 20 min target. The overrun
  is all source reading: the pre-#9 era's defects are recorded ordinally
  across two ~2–3k-line plan documents and had to be read, not grepped.
  Harness runtime itself is 0.10 s.

---

## 7. What this leg does not license

Nothing here is a measurement, a theory claim or a repair. The registry is a
bibliographic object: it records where each defect is written down and what
rule it bought. The replay's stages are judgements about rule TEXT, not
demonstrations that any future registration will actually be refused — a rule
catches a defect only when the registrant applies it, which is precisely how
#22 (rule 15 applied at the wrong level) and #23 (rule 7 not applied at the
routing level) happened after their rules existed. Two of the 41 defects are
instances of a rule being under-applied rather than absent; the replay counts
those as covered TODAY, which is the optimistic reading, and it is named as
such here.
