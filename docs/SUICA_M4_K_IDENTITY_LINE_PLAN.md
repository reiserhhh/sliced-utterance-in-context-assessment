# SUICA M4-K — The Identity Line (IDT empirical program)

Line opened 2026-08-09. Question: does the Identity Theory
(`docs/SUICA_IDENTITY_THEORY_V1.md`) survive contact with the deployed
machinery — specifically its issuer theorems (T3/T5), its card/biography gap
law (T4), and its similarity geometry (T7/T8)?

Tier: EXPLORATORY, label-free, synthetic throughout. The claims ledger
controls. Registrations are appended here BEFORE execution and never edited
after; outcomes are appended after adjudication. Route-index entry at line
synthesis.

## Standing rules (all eight, binding on every K-leg)

1. Designed-null gates state their aggregation rule and multiplicity
   treatment before the run.
2. Every leg pre-states the scale at which its target is measurably non-zero
   and its minimum detectable effect; a noise-floor null is UNDERPOWERED, not
   a null.
3. Verify a non-zero causal channel at every tested parameter value from the
   generator; a null on an inert knob is VACUOUS.
4. Every gate bounds MATERIALITY via an equivalence form — the confidence
   interval must lie inside a margin justified from the generator or the
   effect size — never nil significance on a known-nonzero quantity.
5. Justify the analysis grain for power; do not inherit it.
6. Define the winner jointly over target AND safety, never by the target's
   extremum.
7. Where the safety check has graded levels, report the best arm at each.
8. Verify every factual claim cited to motivate a lean against persisted
   artifacts at full precision before committing the registration.

Execution conventions (binding on dispatched agents): no background jobs, no
monitors — foreground chunked stages with explicit timeouts; Part 0 gates
written into the report BEFORE any arm runs; bit-exact anchor reproduction
from persisted artifacts before new arms; every anomaly self-reported with an
explicit statement of whether it was resolved before or after any
hypothesis-relevant number existed; exactly ONE commit per leg
(`feat(m4-k): ...`), never amended, never pushed by the agent; `results/` is
gitignored — committed deliverables are the script, the report, the plan-doc
outcome append, and the ledger row.

---

## M4-K1 — Issuer theorems: the norm field's three-way split on the deployed machinery

**REGISTERED 2026-08-09, BEFORE RUN.** Planner: this document's author.
Executor: dispatched agent (implementation and execution only; the
registration text is binding).

### Question

T3 proves, in card space, that shared-occasion designs cancel the issuer
exactly, and that free-response designs import issuer error. T3(f) leaves
open whether the DEPLOYED relational gauge inherits that immunity through a
nonlinear frozen map. K1 measures: (i) the designed cancellation, (ii) the
issuer-error law in free designs, (iii) the design × issuer-quality
interaction, and (iv) the deployed gauge's issuer leakage under calibrated
pre-map common shifts.

### Facts cited to motivate leans (rule 8 — re-verified 2026-08-09 against `results/m4_f2_composition/decision.json` at full precision)

- κ=1.0: free_mean = −0.0027727743463521505; shared_mean =
  +0.023390488960374076; paired mean = +0.026163263306726227, CI
  [0.01953599084902978, 0.032790535764422674], t = 9.335105401324688, n = 8
  worlds. Gates all_pass = true. master_seed = 20260802; worlds_per_cell = 8;
  draws_per_world = 20; knobs k48-r0.50-mu0.15-x0.15-e0.70-p0.20_0.80.
- The generator exposes an explicit occasion-mean channel (`w_mu = 0.15`),
  which grounds the common-shift manipulation's calibration.

### Machinery

Reuse `scripts/run_suica_m4_f2_composition.py`'s world generator, designs
(shared-occasion κ=1.0 and free-response, fixed budget) and deployed-gauge
code path VERBATIM (import or minimal extraction with file:line provenance —
no reimplementation of existing constructions). New script:
`scripts/run_suica_m4_k1_issuer_theorems.py`. Fresh master_seed = 20260809
for all NEW arms. 8 worlds. Panel dimensions pinned to F2's (extracted from
the F2 script/artifacts and reported — G0).

### Readers

- **R-rel** — the deployed relational gauge, unchanged: split-half agreement
  as in F2.
- **R-abs** — absolute-card reader, defined ENTIRELY in post-map
  representation space: per-occasion norm μ̂(o) from a norm sample; card =
  occasion-mean deviation; metrics: split-half readability (cosine) and
  rank-1 nearest-neighbor re-identification (gallery = half-1 cards, probes =
  half-2 cards). The representation is the LAST common per-event object the
  deployed gauge consumes before its pairwise/relational step; G2 identifies
  it with file:line and the choice rule is this sentence.

### Arms

Norm arms for R-abs (norm samples disjoint from the panel, same world law):

- `oracle` — norm from N_or = 512 fresh authors (residual issuer error
  reported; note: L1's exactness does not require the oracle to be exact —
  the cancellation holds for ANY common norm vector);
- `est8`, `est32`, `est128` — |P| ∈ {8, 32, 128};
- `biased32` — |P| = 32 drawn from the top half of the world's author-effect
  first principal coordinate; report ‖μ̂_bias − μ̂_oracle‖ against sampling SE
  (bias must exceed it — rule 3).

Design cells: {shared, free} × norm arms × 8 worlds for R-abs.

Common-shift arms (for L5, R-rel primary on the shared design; free design
reported descriptively): pre-map occasion-level common perturbation δ(o)
added to every author's response on occasion o; sizes {0.5×, 1×, 2×} of the
world's author-deviation RMS at the response level (calibration reported);
2× is a stress arm, no gate. R-abs under the same shifts reported
descriptively (its post-map card-space arms already isolate the issuer
algebra).

### Part 0 gates (written into the report before arms)

- **G0 (dims + grain, rule 5).** Extract and pin F2's panel dimensions
  (authors/world, events/author). Grain: per-author identification events,
  authors within world, worlds as strata; justify against MDE (G3).
- **G1 (anchor).** Reload persisted F2 axis-1 CSVs and re-derive the paired
  deltas; must equal `decision.json` values bit-exactly at full float
  precision before any new arm runs.
- **G2 (structural audit).** Read the deployed gauge's computation; verdict
  with file:line citations on whether it consumes only within-occasion
  between-author contrasts post-map. Pre-registered branches: **A** — yes;
  then L5 measures pure map-curvature leakage. **B** — no (norm-position
  enters directly); then L5's leakage has a first-order term. Either way the
  measurement runs; the branch changes interpretation only, and the report
  must say which branch held.
- **G3 (power, rule 2).** Before main arms, from pinned dims compute the MDE
  (80% power, α=.05, paired across 8 worlds) for the L2 contrast
  (rank-1: oracle vs est8, free design) using a reserved-seed pilot world for
  variance. Requirement: MDE ≤ the expected issuer effect derived from
  generator noise ratios (computed in Part 0). If not met: escalate authors
  ×2 once; if still not met, ABORT and report (no arms).
- **G4 (channel verification, rule 3).** Per norm arm: Var(μ̂ − μ̂_oracle) > 0
  with the expected |P|-ordering; decision-flip count vs oracle > 0 at est8
  in the free design (else the issuer channel is inert at this regime —
  report, do not proceed to L2 adjudication as if live). Per shift size:
  post-map displacement > 0.
- **G5 (hygiene).** Manifest with master_seed 20260809, per-stage seeds,
  wall-times; all stages foreground with timeouts.

### Leans (planner's committed priors) and aggregation (rule 1)

- **L1 [designed identity; prior .95].** Shared design: R-abs distances
  computed WITHOUT algebraic cancellation (norms actually subtracted) give
  identical rank-1 decisions across ALL norm arms — 0 decision flips
  (excluding degenerate ties with top-2 margin < 1e-6, counted and reported)
  — and card-difference matrices agree within 1e-9 relative, 8/8 worlds.
  Failure = implementation defect until proven otherwise (the statement is
  proved); bug-hunt gate, then VOID if irreducible.
- **L2 [issuer error live and lawful; prior .85].** Free design: rank-1
  (oracle) > rank-1(est8); per-world sign 8/8 clean (7/8 qualified, ≤6/8
  fail); pooled author-stratified bootstrap (2000 draws) 95% CI excludes 0;
  monotone in |P| (Spearman over {est8, est32, est128, oracle} = 1.0 in ≥6/8
  worlds).
- **L3 [1/|P| law; manipulation check; prior .90].** Pooled log Var(μ̂ − μ̂_or)
  vs log |P| slope CI within [−1.35, −0.65]. Near-by-construction for iid
  sampling; labeled a manipulation check, not a discovery.
- **L4 [free-design specificity — the T3(e) interaction; prior .70].**
  (oracle − est8 deficit in FREE) − (oracle − est8 deficit in SHARED) > 0;
  per-world sign ≥7/8; pooled CI excludes 0. (The shared-side deficit is 0 by
  L1's design; the interaction is then the free-side deficit itself — stated
  so the contrast survives even if L1's tie-handling excludes cells.)
- **L5 [deployed gauge's issuer robustness; prior .60 — the most
  theory-informative lean].** Equivalence form (rule 4): at shifts {0.5×,
  1×}, the pooled 95% CI for Δagreement = agreement(shifted) −
  agreement(unshifted), shared design, lies INSIDE ±m with
  **m = 0.006540815826681557** (= 0.25 × F2's paired composition effect
  0.026163263306726227 — justification: leakage below a quarter of the
  composition effect cannot dominate the F2 retrodiction's ownership
  question); additionally per-world |Δ| < 2m in 8/8 worlds. The 2× stress arm
  is descriptive.

Cross-reader magnitude comparisons (R-abs vs R-rel "gap" sizes) are
DESCRIPTIVE this leg — different statistics, no common scale; no gate.

Multiplicity: five named leans adjudicated separately; no omnibus claim;
qualified language pre-assigned above.

### Pivots (pre-committed)

- **P1.** L1 fails after the bug-hunt gate → leg VOID (a proved identity
  cannot fail in a correct implementation); fix and re-dispatch.
- **P2.** L2 fails WITH G4-verified live channel → issuer error is
  sub-decision-relevant at F2 dims → T5's absolute-reader price is demoted to
  "sub-MDE at this scale" in the theory doc; no rescue re-runs; line proceeds
  to K2.
- **P3.** L5 fails → T3(f)'s idealization is DEAD for the deployed gauge; the
  registered consequence is that **K1b (decomposition of F2's composition
  effect into issuer-error vs jurisdiction-misalignment shares) becomes the
  next registration INSTEAD of K2**, and the theory doc's F2 retrodiction row
  is annotated, not rewritten.
- **P4.** L4 fails while L1/L2 hold → the free-design-specificity derivation
  is wrong or the shared arms do not share norms as designed → re-run the
  structural audit gate; if the audit is clean, record a theory hit on T3(e)
  (revision, no re-run).

### Deliverables (six, as always)

`scripts/run_suica_m4_k1_issuer_theorems.py`;
`results/m4_k1_issuer/` (manifest.json, gates.json, per-cell CSVs,
decision.json); `reports/SUICA_M4_K1_ISSUER_THEOREMS_REPORT.md` (Part 0
first, written before arms); outcome appended under this section; row
appended to `docs/CLAIMS_LEDGER.md` in the existing format; one commit.

Budget guardrail: target < 45 min wall; if any stage exceeds 2× its Part-0
estimate, stop and report rather than background.

### OUTCOME (appended 2026-08-09, after adjudication — the registration above is unedited)

**Verdict:
`CARD_SPACE_CANCELLATION_EXACT__DEPLOYED_GAUGE_AMPLIFIES_THE_COMMON_SHIFT__T3f_DEAD__K1b_REPLACES_K2`.
L1 HOLD, L2 HOLD (clean), L3 HOLD, L4 HOLD, L5 MISS. **P3 FIRES**; P1/P2/P4 do
not.** Report `reports/SUICA_M4_K1_ISSUER_THEOREMS_REPORT.md`; artifacts
`results/m4_k1_issuer/`; script `scripts/run_suica_m4_k1_issuer_theorems.py`;
87.5 s total compute, all foreground.

Part 0, written before any arm. **G0** authors/world 985, allocated events
12,784, m-multiset {8:272, 12:200, 16:513}, 4 contexts, 565 retained by the
deployed gauge. **G1** bit-exact: the κ=1.0 paired mean re-derives to
+0.026163263306726227, CI [0.01953599084902978, 0.032790535764422674],
t = 9.335105401324688, and m = 0.006540815826681557 is verified `==` 0.25× it.
**G2 BRANCH B** — the gauge does NOT consume only within-occasion between-author
contrasts post-map (absolute path mean into M at `v8:229`/`v8:241`; absolute
quantiles `v8:239-240`; quadratic `lag_product` `v8:246`; `tanh` currents
`v8:258`; fixed D0 standardizer `e1:191`/`v8:488-493`; author-specific replicate
subsets `f1:195`), so L5's leakage has a first-order term. The R-abs
representation is the 64-dim frozen event vector (`v8:171-188`, consumed as
`values` at `v8:225`, feeding both branches). **G3** MDE 0.015394733882434413 ≤
expected issuer effect 0.10126903553299493 → PASS, no author escalation, no
ABORT. **G4** live: |P| ordering est8 3.11e-3 > est32 8.24e-4 > est128 1.58e-4,
361 pilot flips at est8/free, biased32 rms exceeds est32's (narrowly on the
pilot, +24–26 % in the occasion-constant component over the eight worlds), and
all three shift sizes displace the post-map panel (1×: M 11.79 %, K 68.25 %).

Results. **L1** — 0 rank-1 flips out of 31,520 probe-arm-world cells, 0 ties
excluded, 8/8 worlds, under the reader satisfying T3(c)'s own "common
probe/gallery norm" hypothesis; card-difference matrices agree to 4.09e-16
(that reader) and 4.14e-16 (the deployable per-half reader), both against a
1e-9 bar, with norms actually subtracted. **L2** — free design, pooled
oracle − est8 = +0.09695431472081219, CI [0.08819796954314721,
0.10596763959390862], 8/8 signs (clean), Spearman = 1.0 in 6/8, effect 6.3× the
MDE. **L3** — slope −1.0865327686128703, CI [−1.0989900747656913,
−1.0735206421063670] ⊂ [−1.35, −0.65]. **L4** — interaction
+0.022461928934010153, CI [0.011795685279187819, 0.03248730964467005], 7/8
signs (exactly at the bar); the shared-side deficit is +0.074492 for the
deployable reader and exactly 0.0 for the T3(c)-hypothesis reader. **L5** —
shared design, Δagreement +0.015881141 at 0.5× (CI [0.003952935, 0.027809348],
3/8 within 2m) and +0.092543049 at 1× (CI [0.057780533, 0.127305564], 0/8
within 2m); 2× stress +0.549686516. The 1× leak is **3.54× F2's whole
composition effect**. Free-design shifts are inert by comparison (|Δ| ≤ 0.0045,
8/8 within 2m at every size).

Two disclosed by-products the registration did not ask for. (i) A split-half
re-identification reader **cannot** simultaneously satisfy T3(c)'s "common
probe/gallery norm" hypothesis and remove the occasion effect; the two readers
are inequivalent and both are reported for every cell. (ii) Under the
T3(c)-hypothesis reader, issuer sampling error becomes a person-specific,
occasion-half-**reproducible** component that *improves* re-identification
(pooled −0.050127, CI [−0.056726, −0.043782], 0/8, monotone the wrong way) —
a forged identity that passes T6's own reproducibility discriminator. Both are
inputs to K3 and to any future T5/T6 revision.

Registered consequence of P3, now binding: **K1b replaces K2 as the next
registration** — decompose F2's composition effect into issuer-error vs
jurisdiction-misalignment shares, knowing the statistic responds +0.0925 to a
shift no card can see. IDT §4's F2 retrodiction row is to be **annotated, not
rewritten**, and T3(f) recorded as decided against on the deployed gauge.

### Planner adjudication (2026-08-09, appended after the run)

Leans scored as executed: L1 HOLD (designed identity confirmed at 4.1e-16,
0/31,520 flips), L2 HOLD clean (8/8, 6.3× MDE), L3 HOLD (slope −1.0865 ⊂
[−1.35, −0.65]), L4 HOLD at the bar (7/8, pooled CI excludes 0), **L5 MISS
with a positive sign — amplification, not mere leakage**. P1/P2/P4 do not
fire; **P3 fires and is binding**: K1b (below) replaces K2 as the next
registration; K2's two-channel charter stays queued behind it. Theory
consequences recorded in IDT dated appendix C (T3(f) decided against on the
deployed gauge; T5 price table extended; T6″ frame-refreshed discriminator
proposed from the disclosed forged-identity by-product; F2 retrodiction row
annotated).

**Planner registration defect (ninth in the program's account), recorded not
repaired:** the K1 registration underdetermined R-abs's norm convention —
T3(c)'s hypothesis (one common probe/gallery norm) and the deployable
construction (per-half estimated norms) are inequivalent readers, and the
registration named one reader where two exist. The executing agent caught it
BEFORE the pilot, resolved it by theory argument, computed BOTH readers for
every cell, and pinned the per-lean assignment in Part 0 — the correct
behavior under the conventions. **Standing rule 9 (added 2026-08-09, paid for
by this defect):** a registration that introduces a constructed instrument
pins every convention that changes its hypothesis-relevance, or pre-delegates
the choice with an explicit decision rule; an instrument ambiguity discovered
mid-leg is resolved before any hypothesis-relevant number exists and ALL
readings are reported.

Smoke-run disclosure adjudicated: an 80-author smoke run confirming the
mechanism preceded the report's Part-0 writeup (agent disclosed it with its
numbers, §R-0.10). The leans and priors were committed at c902498 BEFORE
dispatch, so registration-level pre-commitment is intact; recorded, no lean
re-scored. Convention tightened for future dispatches: smoke runs touching
the hypothesis channel run AFTER Part 0 is written, or are declared part of
Part 0.

---

## M4-K1b — Ownership of the composition effect: author-reading or frame-amplification?

**REGISTERED 2026-08-09, BEFORE RUN** (P3's binding consequence). Planner:
this document's author. Executor: dispatched agent.

### Question

K1-L5 proved the deployed gauge converts common-frame content into agreement
(+0.092543049 at a 1× pre-map shift = 3.54× F2's whole composition effect;
free designs inert, |Δ| ≤ 0.0045). F2's shared arms contain NATIVE common
structure (w_mu = 0.15 — the same scale class as the author channel
w_x = 0.15). K1b decomposes F2's composition effect (+0.026163263306726227)
into (i) a **frame-amplification share** — removed when the common structure
is removed — and (ii) a **jurisdiction-alignment share** — surviving its
removal. Secondary question: validate T6″ (frame-refreshed discriminator)
against K1's measured forged identity.

### Facts cited (rule 8)

F2 numbers re-verified 2026-08-09 at artifact precision (K1 registration
above). K1 numbers cited from the agent's run are re-verified bit-exactly by
gate G1b below before any new arm.

### Machinery

Extend K1's script machinery. New script:
`scripts/run_suica_m4_k1b_composition_ownership.py`. **32 fresh worlds**,
master_seed 20260811, F2 knobs, F2 designs (shared κ=1.0, free) and the
deployed gauge unchanged.

### Arms (deployed gauge R-rel throughout the primary question)

- **A0** shared, intact (fresh-seed F2 replication);
- **A2** free, intact;
- **A1** shared, common structure REMOVED — primary path: exact pre-map
  subtraction of the generator's own common channel; pre-registered fallback
  (decision rule, no discretion): if G2b's additivity check fails at 1e-12,
  use twin generation with w_mu = 0 at identical seeds as THE arm;
- **A3** free, common structure removed (specificity control);
- **A4** shared, ESTIMATED subtraction — per-occasion μ̂(o) from 32 disjoint
  authors' responses (the deployable-repair arm).

Per world: Δ0 = A0 − A2; Δ1 = A1 − A3; amplification share
Ŝ = (Δ0 − Δ1)/Δ0 pooled. Removal effects: R_or = A0 − A1; R_est = A0 − A4.

Secondary (card level, K1's R-abs machinery, free design, first 8 of the 32
worlds): reader A (T3(c)-hypothesis, one norm shared across halves) vs
reader A′ (frame-refreshed: INDEPENDENT est8 norm samples per occasion
half). Contrast tracked: rank-1(est8) − rank-1(oracle) under each reader.

### Part 0 gates (written into the report before arms)

- **G0** — dims pinned to K1's (985 authors/world; m-multiset {8:272,
  12:200, 16:513}; 4 contexts; 565 retained); verify unchanged at the fresh
  seeds' first world.
- **G1 (replication gate)** — Δ0 pooled CI (32 worlds) must OVERLAP F2's
  [0.01953599084902978, 0.032790535764422674]. FAIL → **STOP, leg VOID on
  non-replication** (its own headline; no downstream interpretation).
- **G1b (anchor)** — re-derive K1's L5 1× value +0.092543049 and L2's
  +0.09695431472081219 from `results/m4_k1_issuer/` artifacts bit-exactly.
- **G2b (surgical verification)** — response(with common) − oracle_common ==
  twin response(w_mu=0) at identical seeds, max abs diff ≤ 1e-12 per event,
  2 pilot worlds; verify author+noise channels bit-identical and the removed
  channel exactly the common one. Additivity fails → declare and use the
  fallback path.
- **G3b (power, rule 2)** — from a 4-world pilot, sd of per-world (Δ0 − Δ1);
  require MDE(80%, α=.05, paired t, n=32) ≤ 0.0130816 (= a 50% share of
  F2's effect). Pilot forecast misses → escalate 32→64 worlds once; still
  short → run and pre-declare the attained resolution, with claims tiered to
  it. Aspirational resolution 0.0065408 (25% share) reported against
  achieved MDE.
- **G4b (channel liveness, rule 3)** — reproduce the 1× amplification on 3
  fresh-seed worlds (sign + CI excluding 0); confirm the native common
  channel's RMS lies within [0.5×, 2×] of the author-deviation RMS (the
  scale-comparability premise).
- **G5** — hygiene: manifest, per-stage seeds, wall-times, foreground
  chunks, no monitors.

### Leans (planner's committed priors) and aggregation (rule 1)

32 worlds; per-world signs: clean ≥26/32, qualified ≥21/32, else fail;
pooled paired bootstrap 2000 draws, 95% CI; leans adjudicated separately, no
omnibus.

- **L-a [prior .70]** — the amplification share is material: (Δ0 − Δ1)
  pooled CI excludes 0 AND Ŝ ≥ 0.25.
- **L-b [prior .60]** — a jurisdiction-alignment share survives: Δ1 pooled
  CI > 0. (A MISS here with a large Ŝ is the retrospective-consequence
  branch — see P2b.)
- **L-c [prior .75]** — specificity: A3 − A2 pooled CI inside
  ±0.006540815826681557 (same margin and justification as K1-L5).
- **L-d [prior .65]** — T6″ holds: under reader A′ the forged advantage
  collapses — |rank-1(est8) − rank-1(oracle)| pooled CI inside ±0.0251
  (half K1's forged effect 0.050127) — while oracle rank-1 moves < 0.01
  between A and A′ (frame refreshment must not damage genuine identity).
- **L-e [prior .55; adjudicated ONLY if (Δ0 − Δ1) CI excludes 0, else
  INAPPLICABLE]** — the deployable repair works: R_est CI excludes 0 and
  pooled R_est/R_or ≥ 0.5.

### Pivots (pre-committed)

- **P1b** — G1 fails → leg VOID on non-replication; F2 non-replication
  becomes its own registered follow-up.
- **P2b** — L-a HOLD, L-b MISS, and Ŝ point estimate ≥ 0.75 → REGISTERED
  CONSEQUENCE: the program's append-only retrospective mechanism opens for
  every consumer of "composition works at fixed budget" (M4-F synthesis
  §2/§3, the displacement-resolution doc's F-row, IDT §4 row 1): dated
  claim-strength downgrade to "composition changes what the gauge reads;
  author-reading share not established", and the D3 design prior re-typed
  accordingly.
- **P3b** — L-d MISS (forged advantage survives frame refreshment) → T6″ is
  wrong as stated; the forged component is not issuer-sampling content; its
  localization becomes the next registration; the discriminator stays
  flagged unsafe.
- **P4b** — G2b fails on BOTH paths (channels not separable) → leg blocked,
  report, redesign; no silent arm substitution.

### Deliverables

The six as always: script; `results/m4_k1b_composition_ownership/`
(manifest.json, gates.json, per-cell CSVs, decision.json);
`reports/SUICA_M4_K1B_COMPOSITION_OWNERSHIP_REPORT.md` (Part 0 first);
outcome appended here; ledger row; ONE commit
(`feat(m4-k): K1b — ...`), never amended, not pushed by the agent. Budget:
target < 30 min wall; stop-and-report at 2× any Part-0 stage estimate.

### OUTCOME (appended 2026-08-09, after adjudication — the registration above is unedited)

**Verdict:
`REGISTERED_DECOMPOSITION_DEGENERATE_BY_CONSTRUCTION__SHARE_IS_UNITY_BY_IDENTITY__COMPOSITION_EFFECT_SURVIVES_AUTHOR_DELETION__FRAME_OWNED__T6dd_MISS__P2B_FIRES`.
L-a HOLD (by construction), L-b MISS (by construction), L-c HOLD, L-e HOLD,
L-d MISS (overshoot, not survival). **P2b FIRES; P3b fires mechanically with a
FALSE stated antecedent; P1b/P4b do not.** Report
`reports/SUICA_M4_K1B_COMPOSITION_OWNERSHIP_REPORT.md`; artifacts
`results/m4_k1b_composition_ownership/`; script
`scripts/run_suica_m4_k1b_composition_ownership.py`; 303.9 s total compute,
all foreground, 240 deployed-gauge runs.

Part 0, written before any arm. **G0** dims `==` K1's on every field (985
authors, 12,784 events, {8:272, 12:200, 16:513}, 4 contexts, 565 retained).
**G1b** bit-exact: K1's L5 1× re-derives to +0.09254304863282958 (sd
0.041580915483140586, CI [0.05778053334840726, 0.1273055639172519]) and L2 to
+0.09695431472081219. **G2b PRIMARY PATH** — three-channel reconstruction
residual exactly 0.0, subtraction vs twin 1.11e-16 ≤ 1e-12, removed channel's
across-author spread within a (context, occasion) exactly 0.0; the fallback
does not fire. **G3b** MDE(n=32) 0.005151623455652202 ≤ bar 0.0130816 and ≤ the
aspirational 0.0065408; no escalation. **G4b SPLIT** — 3/3 positive, +0.0807,
native-common/author-deviation RMS ratio 0.8529867606271943 ∈ [0.5, 2], but the
n=3 CI [−0.0288, +0.1902] fails a clause that is **unsatisfiable at the anchor's
own effect size** (K1's sd 0.041581 gives an n=3 half-width 0.10329 > the anchor
mean 0.092543; smallest satisfiable n = 4); pre-declared remedy at the anchor's
own n=8: 8/8 positive, +0.10049101454141054, CI [+0.0503319615961654,
+0.1506500674866557]. **G1 (replication) PASS** — Δ0 = +0.02416454033421539, CI
[0.02115502110256099, 0.027207370259371894] (paired-t [0.020951696576987606,
0.027377384091443174]), 32/32 signs, overlapping F2's [0.01953599084902978,
0.032790535764422674] on both readings; P1b does not fire.

**The leg's principal structural finding, derived and disclosed BEFORE any arm
(Part 0 §G2b / R-0.2), then confirmed at machine precision: the registered
decomposition is DEGENERATE in F2's generator.** `occasion_mode` enters
`f2.generate_world_composed` only through `occasion_labels → shock_x`
(f2:180-193), and at κ=1.0 `blended_x == shock_x` exactly (f2:195), so removing
the common channel makes the shared and free panels the SAME panel
(twin(shared) − twin(free) = 0.0 exactly). Δ1 = A1 − A3 is therefore identically
zero (measured −6.27e-18, max per-world |Δ1| 1.01e-16) and Ŝ ≡ 1
(1.0000000000000002, CI [0.99999999999999940, 1.000000000000001]). This holds
for ANY operationalization of "remove the common structure" — de-commonizing at
preserved variance is literally F2's own free design, giving Δ1 = 0 again. L-a
HOLDs and L-b MISSes as arithmetic, not as measurement, and P2b's registered
trigger is satisfied by that identity.

Measured leans. **L-c HOLD** — A3 − A2 = +0.0006924504528088422, CI
[−0.0012007858348831182, +0.002624154951447348] ⊂ ±0.006540815826681557 (2.5×
inside); removing the occasion channel from a free design is materially inert.
**L-e HOLD (applicable)** — R_or = +0.02347208988140655 (CI [0.020699778192917094,
0.026399521942678278], 32/32), R_est = +0.022155075482892434 (CI
[0.019464560887616736, 0.024830430727009353], 32/32), ratio **0.943890194474869**
[0.902330511257102, 0.9879058376381377]: a per-occasion norm estimated from 32
disjoint authors strips 94 % of what an oracle subtraction strips. This is the
only registered lean whose HOLD is a measurement.

**Standing rule 9 resolution, and the reading that actually answers the
question.** The registration names the removed channel two ways that pick out
different objects: by semantics the occasion-common channel (the state slot at
κ=1, weight √w_x, f2:195-196), by name `w_mu`, which in the code is the
per-author mean (f2:178) — the AUTHOR channel. Resolved before any
hypothesis-relevant number: the registered arm is the semantic one (the lean
texts are only coherent under it); the literal-`w_mu` reading was computed in
full as a disclosed second reading adjudicating nothing. It is the only arm in
the design that can dissociate the two shares, and it is emphatic: with every
trace of author identity deleted, **Δ1′ = A1′ − A3′ = +0.04709060297774369** (CI
[0.042167168538819556, 0.052023150832290276], 32/32) — the composition contrast
**doubles**. Frame share of Δ0 = **1.948748137826835** [1.7631609956850758,
2.1520391802330505]; author-reading share = **−0.9487481378268351**
[−1.1583888879836097, −0.7532210144189037]. Deleting the authors RAISES shared
agreement by +0.023006372890384656 [0.018958716925446557, 0.026933761216768787],
31/32 worlds, while the free design reads zero with or without authors (A2
−0.000917, A3′ −0.000837, difference −8.03e-05 with a CI straddling 0). On the
deployed gauge at F2's dimensions there is **no detectable author-reading share
in the composition effect**, and its point estimate is negative — this, not the
Ŝ ≡ 1 identity, is the live evidence for P2b's content.

Secondary (T6″, 8 worlds, 1024-author norm pool split into two disjoint 512
sub-pools so the oracle arm is frame-refreshed too). Reader A (one shared norm):
est8 − oracle = **+0.058756345177664974** [+0.05228426395939086,
+0.06535532994923858], 8/8 — K1's forged advantage (+0.050127) reproduces at
fresh seeds. Reader A′ (independent norms per occasion half): **−0.06230964467005076**
[−0.07106916243654822, −0.05418781725888325], 0/8 — the forgery is destroyed and
inverted into a genuine issuer penalty, while the oracle moves only
**0.0025380710659898** (< the registered 0.01 bar). **L-d MISSES its registered
±0.0251 zero-equivalence band by overshooting on the correct side.** P3b's
mechanical trigger ("L-d MISS") fires, but its stated antecedent ("forged
advantage survives frame refreshment") is FALSE: T6″'s direction and its
do-no-harm clause are vindicated; only its zero-equivalence operationalization
fails. Reported as fitting no registered branch; planner adjudicates.

Registration defects recorded, not repaired (both caught before any
hypothesis-relevant number): (i) the channel-naming ambiguity above (standing
rule 9 applied as written); (ii) G4b's CI clause is unsatisfiable at n=3 given
the anchor's own variance. Executor deviations, both declared in Part 0 before
the arms: the disclosed second reading (rule-9 mandated) and G4b's n=8
supplementary reading (target n fixed by the anchor's arithmetic, not by running
until the gate passed).

### Planner adjudication (2026-08-09, appended after the run)

Leans scored as executed: L-a HOLD and L-b MISS **by construction** (Ŝ ≡ 1
as an arithmetic identity of the generator at κ=1.0), L-c HOLD (specificity,
2.5× inside the margin), L-d MISS **by overshoot on the correct side** (the
forgery did not survive refreshment — it inverted into an honest issuer
penalty), L-e HOLD (the deployable de-framing repair removes 94.389% [90.233,
98.791] of what oracle removal removes).

**P2b fires, substantively.** The degeneracy is not a technicality: at κ=1.0,
removing the occasion-common structure makes the shared and free designs THE
SAME PANEL — there is nothing else that distinguishes them — so 100% frame
ownership of Δ0 is proved by construction, the strongest form available. The
rule-9 second reading is the live confirmation on the only arm able to
dissociate the shares: deleting every trace of author identity DOUBLES the
composition contrast (Δ1′ = +0.04709060297774369 [0.042167, 0.052023],
32/32); author-reading share = −0.9487481378268351 [−1.1584, −0.7532];
author deletion RAISES shared agreement (+0.023006, 31/32). **At κ=1.0 the
composition effect contains no author reading; author content is a net drag
on the gauge's number.** This is M4-F7's coefficient-0 finding propagated at
last to F2's attribution — the F-line knew the κ=1.0 author channel was
structurally absent and never carried that fact into the composition
headline. The retrospective mechanism opens TODAY, scoped to what is proved:
dated notes appended to `docs/SUICA_M4_F_PANEL_DESIGN_SYNTHESIS.md` and
`docs/SUICA_DISPLACEMENT_PROBLEM_RESOLVED.md` (κ=1.0 attribution only);
IDT carries appendix D. F4/F5's κ-dependence is NOT annotated yet — their
manifests are re-derived at artifact precision in K1c's Part 0 first.

**P3b adjudicated as fitting no registered branch** (the agent's flag was
correct): the mechanical trigger fired on a FALSE antecedent — the forged
advantage did not survive refreshment (reader A +0.058756 [0.052284,
0.065355] 8/8, replicating K1's +0.050127; reader A′ −0.062310 [−0.071069,
−0.054188] 0/8; oracle stability 0.002538 < 0.01). T6″'s direction and
do-no-harm clause are VINDICATED; what failed is my zero-equivalence
operationalization — a rule-4 violation by the planner (a zero band imposed
on a quantity that is nonzero by construction under refreshment: the honest
issuer-noise penalty). T6″ v2 (sign form — no reader may PROFIT from frame
error under refreshment) is formulated in IDT appendix D and carries a
confirmatory lean in K1c.

**Planner registration defects recorded (program account #10–#12), none
repaired away:**
- **#10** — K1's registration asserted "the generator exposes an explicit
  occasion-mean channel (`w_mu = 0.15`)". FALSE: `w_mu` weights the AUTHOR
  mean channel (f2:178). The numeric facts were artifact-verified; the
  code-semantics claim was cited from a knob NAME without reading the source.
  Recorded as a rule-8 violation instance (claims about code are factual
  claims).
- **#11** — the registered decomposition was degenerate by construction at
  the registered knob. **Standing rule 10 (added 2026-08-09, paid for by
  this):** a registered manipulation must be derived from generator source to
  preserve the design's defining contrast, and the leg's Part 0 must prove
  non-degeneracy before arms.
- **#12** — G4b demanded a CI-excludes-zero clause at n=3 that the anchor's
  own sd makes unsatisfiable. **Standing rule 11 (added 2026-08-09, paid for
  by this):** every registered gate is checked for arithmetic satisfiability
  under the cited anchor statistics at registration time.

The de-framing repair (L-e) — per-occasion ESTIMATED mean subtraction pre-map
— removes 94.4% of the frame amplification and is realizable outside
synthetic worlds. It is **UNADOPTED**, deliberately: changing the frozen
gauge is an F16 new-operator event with its own study ID and seal. It queues
beside `colstd_alpha_0.10` as the second certified-but-unadopted repair.

---

## M4-K1c — Ownership at the live-author knob (κ=0.5), and T6″ v2

**REGISTERED 2026-08-09, BEFORE RUN.** Planner: this document's author.
Executor: dispatched agent. This leg exists because K1b's answer at κ=1.0 is
total but structurally special (no author channel exists there); the open
scientific question is the knob where authors are LIVE.

### Question

At κ=0.5 the author AR channel has coefficient √(1−κ) = √0.5 > 0 (the F-line
ran F4/F5-adjacent work and F9 at this knob for exactly that reason). Does
the composition effect at κ=0.5 (+0.008836153697102524, CI
[0.004418364530893362, 0.013253942863311687] — artifact precision,
re-verified in K1's registration) carry ANY author-reading share, or is it
frame-owned at every tested knob?

### Machinery

Extend K1b's script. New script:
`scripts/run_suica_m4_k1c_ownership_live_knob.py`. **128 fresh worlds**,
master_seed 20260812, F2 knobs, κ=0.5 designs, deployed gauge unchanged.

### Arms (all κ=0.5)

- **A0** shared intact; **A2** free intact;
- **A1** shared, occasion-common structure removed (K1b's verified exact
  surgery); **A3** free, removed (specificity);
- **A4** shared, ESTIMATED per-occasion subtraction (|P|=32 disjoint authors);
- **A5** shared, author channel deleted (K1b's second-reading surgery, now
  REGISTERED); **A6** free, author-deleted.

Quantities per world: Δ0 = A0−A2; Δ1 = A1−A3; Δ0′ = A5−A6;
R_or = A0−A1; R_est = A0−A4;
Ŝ_frame = (Δ0−Δ1)/Δ0; Ŝ_auth = (Δ0−Δ0′)/Δ0.

Secondary (8 worlds, K1b's secondary machinery at κ=0.5): readers A vs A′
(frame-refreshed, disjoint 512-author norm sub-pools); contrast
rank-1(est8) − rank-1(oracle).

### Part 0 gates (written into the report before arms)

- **G0c** — dims pinned to K1's; verify at first fresh world.
- **G1c (replication)** — Δ0 pooled CI (128 worlds) OVERLAPS
  [0.004418364530893362, 0.013253942863311687]; FAIL → leg VOID on
  non-replication, STOP.
- **G1bc (anchors)** — re-derive bit-exactly from
  `results/m4_k1b_composition_ownership/decision.json`: Δ0
  +0.02416454033421539; Δ1′ +0.04709060297774369; L-e ratio
  0.943890194474869.
- **G2c (rule 10)** — non-degeneracy PROOF from source at κ=0.5 (blended
  coefficient √0.5 > 0 on the author AR state, with f2 line citations), then
  empirically: A1 and A3 panels differ per world; per-world Δ1 not
  identically 0 at 1e-12. Degenerate → STOP, registration defect, no arms.
- **G3c (power)** — 8-world pilot; MDE(80%, α=.05, paired t, n=128) must be
  ≤ 0.004418076848551262 (a 50% share of the κ=0.5 effect) for BOTH
  (Δ0−Δ1) and (Δ0−Δ0′); escalate 128→256 once on a failed forecast; still
  short → run with claims tiered to attained resolution. Aspirational
  resolution 0.002209038424275631 (25% share).
- **G4c (liveness, rule 3)** — (i) author channel live at κ=0.5:
  between-author variance ratio (author state intact vs zeroed) > 1 at every
  pilot world (the inverse of M4-F7's inertness diagnostic); (ii) removal
  channel live: A0 vs A1 inputs differ; (iii) informational: sign of the
  author-deletion response of shared agreement at this knob.
- **G4c-info (feeds the retrospective; report-only)** — re-derive from F4's
  and F5's persisted manifests/artifacts, at artifact precision, which κ each
  ran at; no adjudication this leg.
- **G5c (hygiene + rule 11)** — manifest, per-stage seeds, wall-times,
  foreground chunks; AND a gate-satisfiability line: every CI clause in this
  registration checked satisfiable at pilot sd before arms, reported.

### Leans (planner's committed priors) and aggregation (rule 1)

128 worlds; per-world signs: clean ≥104/128, qualified ≥85/128, else fail;
pooled paired bootstrap 2000 draws, 95% CI; leans separate; no omnibus.

- **L-a″ [prior .55]** — frame share is the majority at the live knob:
  (Δ0−Δ1) CI excludes 0 AND Ŝ_frame ≥ 0.5.
- **L-b″ [prior .50 — the discriminating measurement]** — an author-reading
  share exists: (Δ0−Δ0′) CI excludes 0 with Ŝ_auth > 0. (K1b's κ=1.0 sign
  was negative; at the live knob this is genuinely open.)
- **L-c″ [prior .70]** — free-side specificity: |A3−A2| and |A6−A2| pooled
  CIs inside ±0.004418076848551262 (margin = 50% of this knob's effect,
  K1b's margin logic rescaled).
- **L-d″ [prior .60; ADJUDICATED ONLY IF (Δ0−Δ1) CI excludes 0, else
  INAPPLICABLE]** — deployable repair at the live knob: R_est CI excludes 0
  and pooled R_est/R_or ≥ 0.5.
- **L-e″ [prior .80]** — T6″ v2 (sign form): under reader A′,
  est8 − oracle ≤ 0 with pooled CI upper bound < +0.005, and oracle
  stability between A and A′ < 0.01. An honest penalty is the EXPECTED null;
  profit from frame error is the forgery signature.

### Pivots (pre-committed)

- **P1c** — G1c fails → VOID on non-replication (own follow-up).
- **P2c** — L-b″ MISS with (Δ0−Δ0′) CI upper < 0.25 × Δ0 point estimate →
  author share bounded below 25% at the live knob → REGISTERED CONSEQUENCE:
  the retrospective widens to "no tested knob shows a material
  author-reading share in the composition effect; the D3 'recruit authors'
  prior survives only as frame-readout economics", and the F4/F5 review
  (from G4c-info's κ facts) becomes the next registration.
- **P3c** — L-e″ fails → T6″ v2 dead as well; the discriminator is flagged
  unsafe; localization of the forged component becomes the next leg.
- **P4c** — G2c degenerate → STOP (planner defect, no arms).

### Deliverables

The six: script; `results/m4_k1c_ownership_live_knob/` (manifest.json,
gates.json, per-cell CSVs, decision.json — gitignored);
`reports/SUICA_M4_K1C_OWNERSHIP_LIVE_KNOB_REPORT.md` (Part 0 first); outcome
appended here; ledger row; ONE commit (`feat(m4-k): K1c — ...`), never
amended, not pushed by the agent. Budget: ~7 arms × 128 worlds ≈ 900
deployed-gauge runs; target < 30 min wall; stop-and-report at 2× any Part-0
stage estimate.

### OUTCOME (appended 2026-08-09, after execution — the registration above is unedited)

**Verdict:
`REGISTERED_FRAME_SHARE_DECOMPOSITION_DEGENERATE_AT_EVERY_KAPPA__PROVED_FROM_SOURCE_BEFORE_ARMS__P4C_FIRES__NO_ARMS_RUN`.
**G2c FAILS: the registered A1/A3 decomposition is DEGENERATE at κ=0.5 — and,
proved from f2's source, at EVERY κ ∈ (0,1]. P4c FIRES: STOP, planner defect,
NO ARMS RUN.** L-a″/L-b″/L-c″/L-d″/L-e″ all **NOT ADJUDICATED**; P1c/P2c/P3c
do not fire (their antecedents were never measured). Report
`reports/SUICA_M4_K1C_OWNERSHIP_LIVE_KNOB_REPORT.md`; artifacts
`results/m4_k1c_ownership_live_knob/`; script
`scripts/run_suica_m4_k1c_ownership_live_knob.py`; **74.3 s total compute**,
all foreground, **68 deployed-gauge runs, every one on a reserved Part-0 seed;
0 adjudicated worlds**. Standing rule 10 — added yesterday and paid for by
K1b — did exactly the work it was created to do, at 74 s instead of a 900-run
leg.

Part 0, written to the report before anything else. **G0c** dims `==` K1's on
every field (985 authors, 12,784 allocated events, {8:272, 12:200, 16:513}, 4
contexts, 565 retained), fresh κ=0.5 world 0 seed 3936073819076212475.
**G1bc** bit-exact from `results/m4_k1b_composition_ownership/arms_a.csv` +
`arms_b.csv` (recomputed, not read off the summary): Δ0
**0.02416454033421539**, Δ1′ **0.04709060297774369**, L-e ratio
**0.943890194474869**, each `==` `decision.json` `==` the registration text;
F2's κ=0.5 block re-verified at artifact precision (free 0.0005009098594400375,
shared 0.009337063556542562, paired 0.008836153697102524, CI
[0.004418364530893362, 0.013253942863311687], `shared − free == paired`
exactly).

**G2c — the leg's result. The registration's premise is a non-sequitur, and
the decomposition is degenerate at every knob.** From source:
`occasion_mode` enters `f2.generate_world_composed` at exactly one place
(`f2:180`), feeding exactly one object (`f2:184-193`, `shock_x`); `loadings, z,
zeta, phi, x, noise` are drawn from a single `default_rng(world_seed)` **before**
that loop while `shock_vector` opens its own generator (`f2:120-126`, invariance
stated at `f2:139-145`); so `mean_part` (`f2:178`) and `noise_part` (`f2:197`)
are design-invariant, and `state_part` (`f2:196`), being LINEAR in
`blended_x = √(1−κ)x + √κ·shock_x` (`f2:195`), splits exactly into a
design-invariant `ar_part` and the sole design-carrying `common_part`.
**Therefore `response − common_part` is design-invariant for every κ ∈ (0,1]:
A1 and A3 are the same panel and Δ1 ≡ 0.** √(1−κ) > 0 does keep the author AR
state in the panel — but that state is design-invariant, so it cannot rescue
the contrast. κ rescales `common_part` by √κ and changes nothing about WHICH
channel carries the design. **K1b's report attributed the collapse to the
κ=1.0 identity `blended_x == shock_x`; that attribution was too narrow — the
collapse is general.** Measured on reserved worlds 9301–9302 at 985 authors:
`mean_part`, `ar_part`, `noise_part` shared-vs-free **exactly 0.0**;
`common_part` shared-vs-free **0.32733131995696163 / 0.3310376783451957** (the
only design-carrying channel, and equal to the A0-vs-A2 panel gap to the last
digit); post-removal panel A1 vs A3 **3.331e-16**; twin(shared) vs twin(free)
**exactly 0.0**; four-channel reconstruction residual **exactly 0.0**. Through
the deployed gauge: **Δ1 = −1.734723475976807e-17 and −8.673617379884035e-18**
(bar: not identically 0 at 1e-12 — missed by five orders of magnitude), and the
rule-9 second reading (K1b's literal whole-state object, arms A1w/A3w) is
degenerate identically (Δ1 max 3.729655473350135e-17). The registered
end-to-end confirmation repeats on all eight G3c pilot worlds (|Δ1| ≤ 7.81e-17).
**A5/A6 are NOT degenerate**: panel A5 vs A6 = 0.3310376783451957, exactly the
A0-vs-A2 gap.

**G3c PASS** (reserved 8-world pilot 9101–9108, 56 gauge runs): sd(Δ0−Δ1)
0.006362014258526332 → **MDE(80 %, α=.05, paired t, n=128) = 0.0015876092906212693**;
sd(Δ0−Δ0′) 0.008560686670660837 → **MDE = 0.0021362771506247724**. Both inside
the registered bar 0.004418076848551262 (2.78× / 2.07×) **and** inside the
aspirational 0.002209038424275631. No escalation; the leg did not stop for want
of power. *Disclosed with its status attached:* pilot Δ0′ exceeds pilot Δ0 in
8/8 reserved worlds (pilot mean Δ0−Δ0′ = −0.010180448568810086, the same sign
K1b measured at κ=1.0) — **reserved-seed power material, NOT an answer to
L-b″**, which was never adjudicated and for which no CI, sign band or share
exists.

**G4c PASS — the knob is fine; the contrast was not.** Author AR state intact
vs zeroed (the registered reading, M4-F8's G6 diagnostic re-expressed on f2's
generator): between-author variance ratio **1.0772786802493795–1.0860125411681176**,
mean 1.0822512197016676, **> 1 at 8/8** worlds (at κ=1.0 this ratio is exactly
1 by M4-F7's inertness result). Author-MEAN channel (the one A5/A6 actually
delete, reported under rule 9): **2.8194500501220903–2.865341972610127**, 8/8.
Removal channel live: `common_part` carries **27.4 %** of response RMS
(0.27447485652733755), non-zero at every pilot world. G4c(iii) not computable
without the blocked arms.

**G4c-info (report-only, adjudicates nothing).** Neither F4 nor F5 persisted a
`manifest.json`; κ facts re-derived from `cells.csv` / `decision.json` /
`gates.json` at artifact precision. **Both legs ran BOTH knobs and persisted
both**: 5 cells / 40 world-runs at κ=0.5 and 6 cells / 48 world-runs at κ=1.0,
each at master_seed 20260802, 8 worlds/cell × 20 draws, knob_tag
`k48-r0.50-mu0.15-x0.15-e0.70-p0.20_0.80`. **F4's adjudicated claims are
κ=1.0-ONLY** — its own record states κ=0.5 "gates no lean or the pivot (all
three leans, the budget claim, the holdout, and the pivot are specified at
kappa=1.0 only …) and is reported for context"; holdout cell
`authors_x32_holdout_shared_k10`; leans a/b/c all HOLD. **F5 carries an
adjudicated κ-stability lean that HELD** (lean_c), with lean_a (co-movement)
and lean_b (target adequacy) MISS; `t_large_primary` = 80. Planner's
retrospective scope follows from this; no adjudication here.

**G5c PASS, and rule 11's first clean pass**: all ten CI clauses of the K1c
registration checked arithmetically satisfiable at the pilot sd before arms —
empty unsatisfiable list. Half-widths at n=128: Δ0 0.001112745488887191,
(Δ0−Δ1) 0.0011127454888871938 vs pilot point 0.008100794057102949, (Δ0−Δ0′)
0.0014973033834037816 vs pilot point −0.010180448568810086, |A3−A2|
0.0009236085890751873 and |A6−A2| 0.0011335194525164446 vs margin
0.004418076848551262, R_est 0.000809411049756907 vs pilot point
0.004051794736468587; L-e″'s two clauses satisfiable at K1b's own anchor
(reader-A′ −0.06230964467005076 [−0.07106916243654822, −0.05418781725888325],
oracle move 0.0025380710659898). **The registration's statistical clauses were
sound; the structural premise was not — precisely the division of labour
between rules 11 and 10.**

Registration defects recorded, not repaired (all caught in Part 0, before any
hypothesis-relevant number existed): (i) **G2c's stated rationale is a
non-sequitur** — the retained AR state is design-invariant, so √(1−κ) > 0
cannot prevent the collapse; (ii) rule-9 ambiguity, "K1b's verified exact
surgery" vs "occasion-common structure" name different objects at κ<1 (the
registered arm was resolved to the semantic reading, since G2c's own rationale
presupposes the AR state is retained; the literal reading was computed in full
as A1w/A3w and is degenerate identically); (iii) rule-9 ambiguity, G4c's
"author state" vs the A5/A6 arms' "author channel" (both readings computed,
both live). Executor deviations, both declared in Part 0 before the numbers:
the A1w/A3w second reading, and computing G3c/G4c after G2c had already failed
(the stop is registered as "no ARMS"; these are Part-0 objects on reserved
seeds, cost 59 s, adjudicate nothing).

**Executor's input to the re-registration (planner decides).** The registered
question is answerable with the arms already implemented, because the
author-deletion contrast is not degenerate. A K1c′ dropping A1/A3/Ŝ_frame and
keeping Δ0 = A0−A2, Δ0′ = A5−A6, Ŝ_auth = (Δ0−Δ0′)/Δ0, plus A4 for the repair
lean and the unchanged secondary, is 5 arms × 128 worlds = 640 runs and
inherits this Part 0 wholesale (G0c/G1bc/G3c/G4c/G5c all pass; MDE for
(Δ0−Δ0′) = 0.0021362771506247724). A genuine *frame-share* arm, if still
wanted, must retain design-carrying content — an ESTIMATED or PARTIAL common
subtraction, or a manipulation at the level of `occasion_labels` — never an
exact channel removal, at any κ.

---

## M4-K2 — charter (register only after K1 adjudication, unless P3 fires)

The card/biography gap law: T4's branch decision. Part 0 re-derives F5/F6/F9
cited numbers from persisted artifacts at full precision (rule 8) and
computes the T4-simple point prediction for F9's exact design (did B-spread
change h/τ_s, or only arrangement within a span?) BEFORE any new run. Then a
h/τ_s sweep at fixed budget: lean — long-window trait recovery is monotone in
h/τ_s with the averaging form while identifiability stays ~flat; pivot — if
trait recovery is flat where T4-simple's predicted gain exceeds the MDE on a
G4-verified live channel, T4-simple is dead and T4-reader-mediated becomes
the registered form (the gauge's state-inclusiveness carries the plateau).

### K2 charter refinement (dated append, 2026-08-09 — planner derivation, BEFORE K1 adjudication and BEFORE K2 registration)

The F9 reconciliation the charter assigned to K2's Part 0 was completed
planner-side today (theory doc, dated appendix B): **F9 does not discriminate
T4-simple vs T4-reader-mediated** — the arrangement lever at F9's state share
predicts +0.0029..+0.0116 under T4-simple (bound +0.0716 only under an
assumption the generator's own weights exclude), all inside F9's CI
[−0.0559, +0.0233]. Power against the plausible prediction: ~5–10%.
Consequently K2's registration (still to be written AFTER K1 adjudication,
unless P3 fires) shall:

1. Manipulate the state SHARE and persistence (α, τ_s / φ, and the κ blend)
   — not the arrangement at fixed share. Rule-2 requirement: the sweep must
   include at least two points where T4-simple's point-predicted swing in
   long-window recovery is ≥3× the design MDE (predictions computed in
   Part 0 from generator constants BEFORE arms).
2. Run TWO channels per arm (theory doc appendix A):
   - card-level, reader-free: the two-split state probe
     ρ_interleaved − ρ_contiguous, whose in-generator prediction follows the
     same AR algebra — the INTERNAL POSITIVE CONTROL that the manipulated
     share actually moved at card level;
   - field-level, reader-involved: the deployed long-window truth recovery.
3. Adjudicate the branch by dissociation: if the card channel tracks the
   designed share while field recovery stays floored where T4-simple
   predicts ≥3×MDE swings → T4-reader-mediated PROVEN on a live, powered
   channel. If field recovery tracks the attenuation curve → T4-simple
   holds. If BOTH move but with incompatible forms → report as fitting no
   registered branch.
4. Re-verify today's cited F9/F2 numbers at artifact precision as a
   mechanical Part-0 gate (rule 8), since this refinement cites them.

## M4-K3 — charter

The similarity-geometry package (T7/T8): caricature (α-scaling) vs rotation
(φ) dissociation; the anti-direction bound as a designed identity in card
space plus its violation rate in ESTIMATED cards as a pure noise function
(predictable from ρ); disattenuated distinctive cosine recovers
generator-true pattern similarity where raw deviation distance fails —
sign-predictable failures in the near-norm and unequal-norm regimes; angular
crowding (not distance crowding) drives misidentification; readability ρ_i
predicts per-person identification (the menagerie coordinate).
