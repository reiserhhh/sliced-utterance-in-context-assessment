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

### Planner adjudication (2026-08-09, appended after the stop)

**P4c fired correctly, and the stop is the leg's success.** Rule 10's Part-0
gate — created yesterday's-equivalent from defect #11 — converted a wrong
registration into a 74-second stop with ZERO adjudicated worlds: the first
time a standing rule caught the planner before compute was spent. All
Part-0 products (MDEs, liveness ratios, satisfiability table, the A5/A6
non-degeneracy value, the F4/F5 κ facts) are sound and are inherited by the
re-registration below.

**Planner registration defect #13, recorded not repaired:** K1c's G2c
rationale ("√(1−κ) > 0 keeps the author AR state in the panel, so
common-removal must not collapse shared/free") is a non-sequitur — the
retained state is design-INVARIANT, so it cannot carry the contrast. Same
family as #11; the difference is that this time the rule-10 gate caught it,
which is the system working as designed.

**Standing rule 12 (added 2026-08-09, paid for by defect #10 plus K1c's two
rule-9 ambiguities — one naming family):** registered manipulations and
channels are specified by generator SOURCE OBJECT (file:function/variable,
e.g. `common_part` per f2:184-195), never by knob names or natural-language
channel descriptions alone; the gloss is secondary. Executor deviations
endorsed: computing G3c/G4c after G2c's failure produced exactly the Part-0
inheritance that makes K1c′ dispatchable without a new pilot.

**Theory consequence recorded as IDT appendix E (the world-family lemma):**
in F2's family, author content is design-invariant BY CONSTRUCTION at every
κ; the composition contrast is carried by `common_part` alone; Ŝ_frame ≡ 1
is a world fact, not a gauge measurement; and the family contains NO
person×occasion interaction channel — the jurisdiction-alignment question
for person-specific state is INEXPRESSIBLE there, so K2 gains a fifth design
requirement (introduce `w_int`). The only live ownership question inside the
family is Ŝ_auth — registered now as K1c′.

---

## M4-K1c′ — Author-reading share at the live knob: the non-degenerate remainder of K1c

**REGISTERED 2026-08-09, BEFORE RUN.** Planner: this document's author.
Executor: dispatched agent. Inherits K1c's Part-0 products as persisted in
`results/m4_k1c_ownership_live_knob/` (G0c, G1bc, G3c, G4c, G5c PASS) and
the arms already implemented in
`scripts/run_suica_m4_k1c_ownership_live_knob.py`.

### Question

With the common channel present (27.4% of response RMS) and the author
channels objectively live at κ=0.5 (AR intact/zeroed ratio
1.0772786802493795–1.0860125411681176; author-mean ratio
2.8194500501220903–2.865341972610127), does the composition contrast REQUIRE
author content — or does author deletion leave it intact or larger, as K1b
measured at κ=1.0?

### Arms (κ=0.5, 128 fresh worlds, master_seed 20260813)

- **A0** shared intact; **A2** free intact;
- **A5** shared author-deleted; **A6** free author-deleted;
- **A4** shared estimated per-occasion subtraction (|P|=32);
- **A1** shared exact common-removal — RETAINED not as a frame-share arm
  (Ŝ_frame ≡ 1 is a world fact) but as the ORACLE DE-FRAMING REFERENCE: by
  the proved identity its gauge value is the no-composition baseline, so
  R_or = A0−A1 anchors the repair ratio.

Quantities per world: Δ0 = A0−A2; Δ0′ = A5−A6; Ŝ_auth = (Δ0−Δ0′)/Δ0;
R_or = A0−A1; R_est = A0−A4.

Secondary (8 worlds): T6″ v2 at κ=0.5 — readers A vs A′ exactly as K1c wired
and never ran; contrast rank-1(est8) − rank-1(oracle).

### Part 0 gates

- **G0′ (inheritance anchor)** — re-derive bit-exactly from
  `results/m4_k1c_ownership_live_knob/decision.json`: both G3c MDEs
  (0.0015876092906212693, 0.0021362771506247724), the G4c ratios quoted
  above, and the A5-vs-A6 panel gap 0.3310376783451957.
- **G1′ (replication, now evaluable)** — Δ0 pooled CI (128 worlds) OVERLAPS
  F2's κ=0.5 CI [0.004418364530893362, 0.013253942863311687]; FAIL → leg
  VOID on non-replication, STOP.
- **G2′ (rule 10)** — non-degeneracy of the REGISTERED contrasts at fresh
  seeds: A5 vs A6 panels differ (RMS > 1e-6) on both pilot worlds; A0 vs A1
  inputs differ. The A1-degeneracy identity is a proved fact and is cited,
  not re-tested.
- **G3′ (power)** — inherited MDE 0.0021362771506247724 for (Δ0−Δ0′) at
  n=128; confirm fresh-seed pilot sd (2 worlds) within 2× of K1c's pilot sd,
  else recompute MDE and re-check the bar 0.004418076848551262.
- **G4′ (rule 3)** — author-MEAN channel liveness (the channel A5/A6
  delete) ratio > 1 at fresh pilot worlds; AR ratio and common-channel share
  reported.
- **G5′ (hygiene + rules 11 and 12)** — manifest, seeds, wall-times,
  foreground; rule-11 satisfiability line at fresh pilot sd; rule-12
  compliance header in the script naming every manipulated object by source
  object (`common_part` per f2:184-195 blend split; author `mean_part`
  f2:178; author AR `x` f2:151-177).

### Leans (planner's committed priors) and aggregation (rule 1)

128 worlds; per-world signs: clean ≥104/128, qualified ≥85/128, else fail;
pooled paired bootstrap 2000 draws, 95% CI; leans separate; no omnibus.

- **L-1 [prior .35 — basis disclosed: K1b's κ=1.0 sign and K1c's
  reserved-seed pilot sign are both negative; the pilot adjudicates nothing,
  priors are beliefs]** — an author-reading share exists: (Δ0−Δ0′) pooled CI
  excludes 0 with Ŝ_auth > 0.
- **L-2 [prior .70]** — author-deletion specificity on the free side:
  |A6−A2| pooled CI inside ±0.004418076848551262.
- **L-3 [prior .80; ADJUDICATED ONLY IF R_or CI excludes 0, else
  INAPPLICABLE]** — deployable de-framing at the live knob: R_est CI
  excludes 0 and pooled R_est/R_or ≥ 0.5.
- **L-4 [prior .80]** — T6″ v2 (sign form): under A′, est8 − oracle ≤ 0 with
  pooled CI upper bound < +0.005; oracle stability between A and A′ < 0.01.

### Pivots (pre-committed)

- **P1′** — G1′ fails → VOID on non-replication (own follow-up).
- **P2′** — L-1 MISS with (Δ0−Δ0′) CI upper < 0.25 × Δ0 point estimate →
  author share bounded below 25% at the live knob → REGISTERED CONSEQUENCE:
  the retrospective widens WITH the family lemma: "in this world family the
  composition effect carries no material author-reading share at any tested
  knob, and the jurisdiction-alignment channel for person-specific state
  does not exist in the family by construction; the D3 'recruit authors'
  prior survives only as frame-readout economics" — and the F4/F5 review
  (on K1c's G4c-info facts) becomes the next registration.
- **P3′** — L-4 fails → T6″ v2 dead; forged-component localization is next.
- **P4′** — G2′ fails on A5/A6 at fresh seeds → STOP, defect, no arms.

### Deliverables

The six: `scripts/run_suica_m4_k1c_prime_author_share.py` (may import from
K1c's script); `results/m4_k1c_prime_author_share/` (manifest.json,
gates.json, per-cell CSVs, decision.json — gitignored);
`reports/SUICA_M4_K1C_PRIME_AUTHOR_SHARE_REPORT.md` (Part 0 first); outcome
appended here; ledger row; ONE commit (`feat(m4-k): K1c' — ...`), never
amended, not pushed by the agent. Budget: 6 arms × 128 worlds ≈ 768
deployed-gauge runs + the 8-world secondary; target < 30 min wall;
stop-and-report at 2× any Part-0 stage estimate.

### OUTCOME (appended 2026-08-09, after execution — the registration above is unedited)

**Verdict:
`NO_AUTHOR_READING_SHARE_AT_THE_LIVE_KNOB__AUTHOR_DELETION_ENLARGES_THE_COMPOSITION_EFFECT__FREE_SIDE_SPECIFIC__DEFRAMING_REPAIR_DEPLOYABLE_0p73__T6dd_V2_HOLDS__P2PRIME_FIRES`.
**L-1 MISS, L-2 HOLD, L-3 HOLD, L-4 HOLD; P2′ FIRES; P1′/P3′/P4′ do not.**
All five Part-0 gates PASS plus G1′. Report
`reports/SUICA_M4_K1C_PRIME_AUTHOR_SHARE_REPORT.md`; artifacts
`results/m4_k1c_prime_author_share/`; script
`scripts/run_suica_m4_k1c_prime_author_share.py`; **793.9 s total (≈13.2 min),
all foreground, 768 adjudicated deployed-gauge runs on 128 fresh worlds
(master_seed 20260813) plus 24 on reserved Part-0 seeds**.

**The headline: at the LIVE knob the composition effect does not merely
survive author deletion — deleting the author-mean channel nearly DOUBLES it.**
Δ0 = **0.007448566560020627** [0.006337565267918393, 0.008585684601869065]
(106+/22−, clean); Δ0′ = **0.014482876187491394** [0.013223715021599436,
0.01581035481469913] (**127+/1−**, clean); Δ0−Δ0′ =
**−0.007034309627470767** [−0.008163458312738956, −0.005873004730301863]
(20+/**108−**, clean); **Ŝ_auth = −0.9443843417103447 [−1.2340432099315712,
−0.7045965411263232]**, i.e. Δ0′/Δ0 = 1.9443843417103448. That is, to three
decimals, K1b's κ=1.0 value (−0.9487481378268351 [−1.1584, −0.7532]) — but
measured where G4′ certifies the author channels LIVE (author-mean liveness
ratio 2.8552376916466695–2.864645232241155; AR-state ratio
1.0817049201258067–1.0822239823705524, both > 1 at 2/2 fresh pilot worlds,
both inside K1c's inherited 8-world bands). **Author liveness in the WORLD
buys the composition effect no author content in the GAUGE.** Decomposition
identity verified to 3.469446951953614e-18: the gap is exactly
−[(A5−A0) + (A2−A6)] — deleting the author channel RAISES shared agreement
(+0.004338666343079094, 92/128, qualified) AND LOWERS free agreement
(−0.0026956432843916727, 90/128, qualified).

**The measurement is gauge-level by construction, which is what makes it
worth making.** A5 = shared − `mean_part` (f2:178) and A6 = free − `mean_part`
subtract the same design-invariant object, so (A5−A6) ≡ (A0−A2) *as panels* —
verified bit-identical at both fresh pilot worlds (RMS 0.06929976550687832 /
0.06923291177968123). Δ0 − Δ0′ is therefore purely the deployed nonlinear
map's use of author content, and it is large, negative and clean.

Part 0, written to the report before any main arm (stage `part0`, 15.273 s,
`timestamp_utc = 2026-08-09T06:06:17.808770+00:00`; 12 gauge runs, all on
reserved worlds 9401–9402). **G0′ PASS** — all seven inheritance anchors
re-derived from K1c's RAW rows or re-run from the generator and bit-exact
against both the persisted summary and the registration text: MDEs
**0.0015876092906212693** / **0.0021362771506247724**, K1c pilot sd
0.008560686670660837, AR band 1.0772786802493795–1.0860125411681176,
author-mean band 2.8194500501220903–2.865341972610127, common share
0.27447485652733755, and the A5-vs-A6 panel gap **0.3310376783451957**
re-run from the generator at K1c's own persisted world seed
6845424899141898945. **G2′ PASS** — A5-vs-A6 panel RMS 0.0692 against a 1e-6
bar (five orders of margin); A0-vs-A1 inputs differ at both worlds; the A1
degeneracy identity CITED, not re-tested. **G3′ PASS with a disclosed clause
miss** — the fresh 2-world sd 0.003757879890017854 is 0.43896944656283826× of
K1c's, so the two-sided "within 2×" reading MISSES (the fresh sd is
*smaller*); the registration's own fallback was executed and the fresh-sd MDE
0.0009377603985145934 is inside the 0.004418076848551262 bar, as is the
inherited MDE; by written rule the LARGER (inherited) MDE
**0.0021362771506247724** controls, since an n=2 sd may never buy more claimed
resolution than the inherited n=8 pilot. **G4′ PASS.** **G5′ PASS** with
rule-12's source-object header (occasion-common `common_part` per the f2:195
blend split fed by f2:180/184-193/120-126; author `mean_part` f2:178; author
AR `x` f2:151-177; design `occasion_mode` f2:180) and rule 11 run over
**fourteen** clauses: thirteen satisfiable, ONE flagged — "L-3: R_est CI
excludes 0" was unsatisfiable at the fresh n=2 pilot point (|−0.00040| < hw
0.00057). Register-note R-0.4 declined to treat an n=2 point as decisive,
recorded K1c's n=8 second reference (0.004051794736468588, hw 0.000809), and
the 128-world result then satisfied the clause comfortably. **G1′ PASS** —
Δ0's CI lies wholly INSIDE F2's κ=0.5 CI [0.004418364530893362,
0.013253942863311687]; bootstrap and paired-t readings agree.

**L-2 HOLD, stated precisely (rule 4):** |A6−A2| = −0.0026956432843916727
[−0.003871657497627448, −0.0015998336172598471] lies inside the registered
±0.004418076848551262 margin, so the equivalence holds — but the CI excludes
zero and the sign band is *qualified* (90/128), so author deletion measurably
lowers free-design agreement; only its IMMATERIALITY is licensed.

**L-3 HOLD, with a new κ-dependence:** R_or = 0.0061852799720190175
[0.005177265953630964, 0.007144206387567167] (109+/19−, clean) excludes 0, so
the lean is applicable; R_est = 0.004544633760387759 [0.003502130735750378,
0.005619815780497545] (94+/34−, qualified); ratio **0.7347498869811525**
[0.6376184714475329, 0.820668361509718] ≥ 0.5. The estimated per-occasion
subtraction recovers **73.47 %** of oracle de-framing at κ=0.5 against K1b's
**94.39 %** [90.23, 98.79] at κ=1.0 — **non-overlapping intervals**. Still
certified, still UNADOPTED under F16 discipline, now with a knob-dependent
efficacy figure. (A1's gauge value is the no-composition baseline by the
family lemma; Ŝ_frame was never computed and is not a quantity of this leg.)

**L-4 HOLD — T6″ v2 confirmed at the live knob, with a LARGER inversion than
at κ=1.0.** Under reader A (gallery and probe norms from the same 512-author
half) est8 BEATS oracle by **+0.05469543147208122** [0.04809644670050761,
0.06142131979695432], **8/8 worlds** — the forgery. Under reader A′
(frame-refreshed, disjoint halves) the same norm inverts to
**−0.0866751269035533** [−0.09517766497461928, −0.07778870558375636],
**0/8** — versus K1b's −0.06230964467005076 at κ=1.0. Oracle rank-1 moves only
**0.0019035532994924331** (bar 0.01); CI upper −0.0778 < +0.005. P3′ does not
fire; T9's forgery principle and its licensed counter-operation both replicate.

**P2′ FIRES, on a STRONGER antecedent than its own wording.** (Δ0−Δ0′) CI
upper **−0.005873004730301863** < 0.25 × Δ0 = **0.0018621416400051568**, with
L-1 MISS. The pivot text says "author share bounded below 25 % at the live
knob"; measured, the share is bounded below **ZERO**, CI upper −0.70. The
registered consequence (retrospective widening WITH the family lemma; the D3
"recruit authors" prior surviving only as frame-readout economics; the F4/F5
review on K1c's G4c-info facts becoming the next registration) is the
planner's to execute — the executor only reports that the antecedent is
satisfied, and satisfied more strongly than the text anticipates.

Anomalies, all disclosed with timing: (i) `part0` was invoked TWICE
(06:03:10–06:03:26 and 06:06:01–06:06:17 UTC) — the first returned G0′ FAIL
because pandas 3.0.2's DEFAULT csv float parser does not round-trip float64
(`1.0772786802493795` reads back as `...97`), so the anchors matched only to
~2e-15 relative; the written rule
`float_precision="round_trip"` was adopted for the whole leg and two other
Part-0-only changes made (conservative controlling MDE; the L-3 second
reference). **Both invocations touched only reserved pilot worlds 9401–9402;
no main or `abs` world, and no hypothesis-relevant number, existed at either
point**; the report's Part 0 was written after the second and before `arms_a`
(06:08:41). Side finding: K1c's published pilot R_est 0.004051794736468587 is
1 ULP off its own CSV under round-trip parsing (0.004051794736468588); K1c's
gate values, computed in memory, are unaffected. (ii) G3′'s two-sided 2×
clause missed (A-2 above), in Part 0, before any main arm. (iii) The rule-11
flag was a false alarm, as R-0.4 predicted it might be. (iv) L-2's equivalence
holds over a non-null effect (disclosed, not over-read). (v) Registration-text
inaccuracy: G0′'s anchors are said to live in K1c's `decision.json`; two of
three families live in `gates.json` — recorded, not repaired, gate satisfied
in the stronger form. No result fell outside a registered branch. No
background jobs, no monitors, no smoke runs; longest stage `arms_b` 516.877 s
against a 900 s estimate, so the 2× stop-and-report rule never engaged.

### Planner adjudication (2026-08-09, appended after the run)

Leans scored as executed: **L-1 MISS on the wrong side, clean** — the
author-reading share at the live knob is −0.9443843417103447
[−1.2340432099315712, −0.7045965411263232], the same number to three decimals
as K1b's −0.949 at κ=1.0, measured with the author channels CERTIFIED live
(G4′) and the composition effect itself replicating INSIDE F2's own CI (G1′).
L-2 HOLD (qualified; equivalence over a disclosed non-null effect), L-3 HOLD
(R_est/R_or = 0.7347 [0.6376, 0.8207]), L-4 HOLD (T6″ v2 at the live knob:
forgery +0.0547, 8/8 → inversion −0.0867, 0/8; oracle stable 0.0019).

**P2′ fires on a stronger antecedent than its own text** — the share is
bounded below ZERO (CI upper −0.7046), not merely below 25%. Its registered
consequence executes today: the retrospective widens with the family lemma
(dated note II appended to `docs/SUICA_M4_F_PANEL_DESIGN_SYNTHESIS.md` and
`docs/SUICA_DISPLACEMENT_PROBLEM_RESOLVED.md`), and **the F4 re-reading is
the next registration (M4-K1d, below)**. Theory consequences: IDT appendix F
(κ-invariant negative share; author-as-interference decomposition
A5−A0 = +0.0043 / A6−A2 = −0.0027 with the identity verified at 3.5e-18; the
de-framing repair's NEW κ-dependence 0.7347 vs 0.9439, non-overlapping —
a deployment caveat on the certified-unadopted repair; T9 now measured at
both knobs).

**Planner registration defects recorded (program account #14, #15):**
- **#14** — G0′'s anchor location misstated (`decision.json` for two families
  that live in `gates.json`). Rule-8 hygiene family; gate satisfied in the
  stronger form (raw-row re-derivation).
- **#15** — G3′'s "within 2×" sd clause was TWO-SIDED, so it fails when the
  fresh variance is SMALLER — an equivalence band that punishes improvement.
  The registered fallback absorbed it. One-sided (≤ 2×) was the intent; rule
  11 checks satisfiability, not clause DIRECTION — direction is the
  registrant's job and this one was wrong.

**Convention added to this line's execution conventions (dated 2026-08-09,
from K1c′ anomaly 1):** all artifact re-derivations that pass through CSV
parse with `float_precision="round_trip"` — pandas 3.0.2's default parser
does not round-trip float64, which is fatal to bit-exact anchor gates. (Side
finding on record: K1c's published pilot R_est is 1 ULP off its own CSV under
round-trip parsing; its in-memory gate values are unaffected.)

---

## M4-K1d — Does the author-axis law survive author deletion? (the F4 re-reading)

**REGISTERED 2026-08-09, BEFORE RUN** (P2′'s registered consequence).
Planner: this document's author. Executor: dispatched agent.

### Question

K1b/K1c′ proved the composition effect carries no author-reading share at
either knob — author content is INTERFERENCE to the gauge's frame reading.
M4-F4's headline is a different object: the author-SCALING law (agreement
grows with author count, γ = 1.096 [0.984, 1.218], ×32 holdout predicted
0.4012 / observed 0.3861, shared design, κ=1.0 — its adjudicated claims are
κ=1.0-only by its own record, per K1c G4c-info). Under frame ownership the
sharpest re-reading question is: **is the author axis a law about AUTHORS at
all, or a law about averaging more noise-bodies over the same frame?** If
agreement growth with "authors" persists when every trace of author identity
is deleted, the axis is frame-readout economics — a REPLICATE axis — and the
D3 prior "recruit authors, not words" re-types to "recruit replicates".

### Facts cited (rule 8)

F4: γ = 1.096 [0.984, 1.218], holdout predicted 0.4012 / observed 0.3861,
shared κ=1.0, master_seed 20260802 (from the F-line synthesis row and K1c
G4c-info's artifact re-derivation; Part 0 re-verifies against
`results/m4_f4_author_axis/` at full precision with round-trip parsing).
K1b: author deletion at κ=1.0 raises shared agreement +0.023006 (31/32).
At κ=1.0 the author AR state has coefficient exactly 0 (M4-F7), so author
deletion removes `mean_part` (f2:178) only — rule-12 source-object naming.

### Machinery

`scripts/run_suica_m4_k1d_replicate_axis.py`, importing F4's cell
construction and K1b/K1c′'s deletion surgery. Fresh master_seed 20260814.
8 worlds (F4's own grain). Author grid pinned to F4's own cells in Part 0
(expected {×1, ×2, ×4, ×8, ×16}; ×32 reserved as holdout ONLY if the intact
arm's fit demands it — economy note, its inclusion rule is: include iff
Part-0 pilot shows the ×16 cell's wall-time × 2 arms keeps the leg under
budget). Two arms per cell: **intact** and **author-deleted** (`mean_part`
removed; at this knob that is the entire author channel).

### Quantities

Per arm: agreement-vs-authors curve; fitted exponent γ via F4's own fitting
procedure (Part 0 extracts it with file:line provenance — no new fitter).
Δγ = γ_deleted − γ_intact (bootstrap over worlds, 2000 draws). Per-cell level
contrast: agreement_deleted − agreement_intact.

### Part 0 gates

- **G0d** — pin F4's cells, dims, fitting procedure from
  `results/m4_f4_author_axis/` + its script, at full precision, round-trip
  parsing; re-verify the cited γ, CI, holdout numbers bit-exactly.
- **G1d (replication)** — the INTACT arm's fitted γ CI (fresh seeds) must
  overlap F4's [0.984, 1.218]; FAIL → leg VOID on non-replication, STOP.
- **G2d (rule 10)** — non-degeneracy: deleted-arm panels differ from intact
  per cell (RMS > 1e-6); the deletion is `mean_part` only at this knob,
  stated from source (f2:178; M4-F7's coefficient-0 result for the AR term).
- **G3d (power + rule 11)** — pilot (2 worlds, smallest and largest grid
  cells, both arms): bootstrap precision of γ per arm; verify the L-1
  equivalence band ±0.25 is satisfiable (band justified as ~2× F4's own CI
  half-width 0.117); verify every CI clause satisfiable at pilot sd;
  one-sided clauses stated as one-sided (defect #15's lesson).
- **G4d (rule 3)** — deletion channel live: `mean_part` share of response
  RMS at κ=1.0 > 0 per pilot world; report the share.
- **G5d** — hygiene; `float_precision="round_trip"` everywhere; rule-12
  header (`mean_part` f2:178; grid cells by F4's own constructors).
- **G-info-F5 (report-only)** — from F5's script and artifacts: derive what
  `truth_recovery_exact` and `truth_recovery_long` correlate AGAINST (the
  generator truth objects), and state from source whether those objects are
  common-channel content, author content, or mixed. No adjudication; feeds
  the eventual F5 re-typing and the line synthesis.

### Leans (planner's committed priors) and aggregation (rule 1)

8 worlds; grid-cell contrasts pooled by paired bootstrap (2000); leans
separate; no omnibus.

- **L-1 [prior .70]** — the exponent survives deletion: |Δγ| bootstrap CI
  inside ±0.25 AND γ_deleted's CI overlaps F4's [0.984, 1.218].
  **Registered consequence of HOLD:** F4's row re-types "author axis →
  replicate axis (frame-readout economics)" by dated note; the D3 prior
  re-types "recruit replicates, not words". (Not a pivot — the consequence
  of the lean holding, pre-stated.)
- **L-2 [prior .75]** — author-as-interference at every scale: the deleted
  arm's level exceeds the intact arm's at every grid point (per-point pooled
  CI > 0 at ≥ 4/5 points; sign counts reported per point).
- **L-3 [prior .55]** — the law's PREDICTION improves or holds under
  deletion: the deleted arm's own power-law fit quality (F4's fit
  diagnostic, extracted in G0d) is no worse than the intact arm's (ratio CI
  including or above 1).

### Pivots (pre-committed)

- **P1d** — G1d fails → VOID on non-replication (F4's law does not
  reproduce at fresh seeds — its own headline event, next registration).
- **P2d** — L-1 MISS with γ_deleted CI DISJOINT from F4's band → the
  scaling law is author-borne even though the composition effect is not —
  ownership and scaling dissociate; the reconciliation becomes the next
  registration and NO retrospective re-typing of F4 occurs.
- **P3d** — G2d/G4d fail (deletion inert at this knob) → STOP, defect.

### Deliverables

The six: script; `results/m4_k1d_replicate_axis/` (manifest.json,
gates.json, per-cell CSVs, decision.json — gitignored);
`reports/SUICA_M4_K1D_REPLICATE_AXIS_REPORT.md` (Part 0 first); outcome
appended here; ledger row; ONE commit (`feat(m4-k): K1d — ...`), never
amended, not pushed by the agent. Budget: grid × 2 arms × 8 worlds with ×16
cells heavy — target < 45 min wall; stop-and-report at 2× any Part-0 stage
estimate; the ×32 holdout inclusion rule is G0d's economy note, decided in
Part 0, not mid-run.

### Outcome (2026-08-09, appended after the run — executor's adjudication)

**`AUTHOR_AXIS_IS_A_REPLICATE_AXIS__EXPONENT_SURVIVES_AUTHOR_DELETION__DELETION_RAISES_LEVEL_AT_EVERY_SCALE__FIT_QUALITY_NO_WORSE`.
L-1 HOLD (on the band's edge), L-2 HOLD (maximal), L-3 HOLD (a
non-rejection). No pivot fires.** Fresh master_seed 20260814, κ=1.0, shared
design, F4's grid {×1,×2,×4,×8,×16} plus the ×32 holdout (admitted by the
Part-0 economy rule), 8 worlds/cell, 20 draws/world, two arms per cell
(intact; author-deleted = `mean_part` f2:178 removed by exact pre-map
subtraction, which at this knob is the ENTIRE author channel since the AR
coefficient `sqrt(1-kappa)` is exactly 0 at f2:195 per M4-F7) — **96
adjudicated deployed-gauge runs**, plus 8 reserved Part-0 pilot runs on
worlds 9401–9402. Wall-clock 06:53:17→07:20:05 UTC = **26.8 min** against the
< 45 min target; the 2× stop-and-report rule never engaged.

**G1d PASS, and the replication is strong, not marginal.** The fresh intact
arm's fitted exponent is **γ = 1.1186793702102118** with F4's own
`bootstrap_axis` CI **[0.9810050210740082, 1.2375507404943047]**, which
*contains* F4's [0.9843434774823611, 1.2176831424523908] entirely. **P1d does
not fire; F4's author-axis law reproduces at fresh seeds.** G0d PASS with all
five cited F4 numbers bit-exact on F4's own code path (round-trip parsing
deviates by ≤2 ULP, 9.023053842666835e-16 relative — see the report's R-0.1: a
round-trip convention cannot retroactively reproduce a legacy number computed
under pandas' default parser). G2d PASS at 0.06825177531394482 against a 1e-6
bar, with this leg's memory-bounded `mean_part` extraction verified
**bit-identical (0.0)** to `k1b.channels`'s canonical mirror. G3d PASS
(projected Δγ half-width 0.11262789561542542 = 0.45× the ±0.25 band; 5/5
clauses satisfiable, one-sided clauses stated one-sided). G4d PASS: the
deleted channel carries **38.6–38.8 %** of the response RMS at every pilot
world. G5d PASS.

**L-1 HOLD, stated precisely (rule 4).** Δγ = γ_deleted − γ_intact =
**+0.1259396729686626** [0.016883362223958802, 0.24832554505807228]
(paired world-level bootstrap, 2000 draws, registered seed 20260814);
γ_deleted = **1.2446190431788744** [1.1184843238134545, 1.3578623870533717],
overlapping F4's band on [1.1184843238134545, 1.2176831424523908]. Both
registered clauses are met, **but the CI excludes zero**: deletion does not
leave the exponent alone, it **steepens** it. **The equivalence verdict is
Monte-Carlo fragile and this must travel with the result:** at the registered
B = 2000 the upper edge is 0.24832554505807228 (inside ±0.25 by
0.0016744549419277222); at B = 100000 with the SAME registered seed it is
0.25167594529642967 (outside by 0.0016759452964296706); across nine
alternative B = 2000 seeds the upper edge ranges 0.2459–0.2736 and the clause
holds at **5 of 10 seeds**. The registered reading controls — B and the seed
were both fixed in Part 0 (R-0.5, on disk 06:54:52 UTC, before the 06:57
arms) — so **L-1 is HOLD**, but the exponent-equivalence claim sits exactly on
its own registered tolerance boundary and this leg does not resolve which side
it falls on. **What IS resolved at every resolution and all ten seeds: Δγ > 0.**

**Registered-branch gap (for the planner's defect account).** Under the high-B
reading the configuration is "L-1 MISS **with** γ_deleted's CI still
**overlapping** F4's band". P2d requires MISS **and DISJOINT**, so P2d would
not fire, and **no registered branch covers that outcome** — reported as
fitting no registered branch. Not hypothetical: the measurement sits on
exactly that boundary.

**L-2 HOLD, maximal.** The deleted arm's level exceeds the intact arm's at
**5/5** grid points with the one-sided clause (CI lower edge > 0) satisfied at
every one, sign positive in **8/8 worlds at every point — 40/40 world-points**.
The contrast is not an offset but grows with scale: **+0.012034790822427564**
(×1), **+0.02172220457061207** (×2), **+0.07394264943700614** (×4),
**+0.12471963896605351** (×8), **+0.2095266552338645** (×16). Author deletion
buys more the more replicates there are.

**L-3 HOLD as a NON-REJECTION.** WRMSE ratio (intact/deleted) =
**0.7074468507924991** [0.3859105177244442, 2.142092546684852] — the interval
contains 1, so the registered one-sided clause is satisfied, but the point
estimate is below 1 (in-sample the deleted arm fits its own power law slightly
worse) and the interval is uninformatively wide. Disclosed second reading
(rule 9), pointing the other way: on F4's own predict-then-holdout diagnostic
at ×32, the **deleted** arm extrapolates better — log-odds gap
**0.049043636423744374** (predicted 0.6439648605439744, observed
0.6694153296715588) vs the intact arm's **0.08074971490742865** (predicted
0.38377206783108325, observed 0.4285829511595591), both inside F4's own
factor-2 band 0.3010299956639812.

**What the leg establishes.** At F4's own knob, on fresh seeds, with the
entire author channel deleted: **the author-scaling law is not a law about
authors.** The exponent survives inside the registered band (at its edge), the
level rises at every scale, and the ½-agreement author budget **more than
halves** — 48.86511436544155× intact vs **19.877619351988358×** deleted. The
generator's author-mean content is a **drag on the axis it was named after**.
This extends IDT appendix F's "author content is interference" from the LEVEL
of the composition contrast to the SLOPE of the scaling law. **L-1's
registered consequence of HOLD (re-typing F4's row "author axis → replicate
axis"; re-typing the D3 prior to "recruit replicates, not words") is the
PLANNER's to execute** — this leg only adjudicates, and it hands over an
antecedent that is HOLD *and* boundary-seated.

**G-info-F5 (report-only, no adjudication).** F5's `truth_recovery_exact`
(f5:494) and `truth_recovery_long` (f5:505) are the deployed field functional
between the finite-sample ESTIMATED field and a **noise-free generator TRUTH
field**: `events_true = mean_part + state_part` (f5:279, from
`generate_truth_vectors_exact` f5:225-280) and `events_long = mean_part_chunk
+ state_part` (f5:367, from `generate_truth_vectors_long` f5:303-372).
**From source the truth objects are MIXED**: `mean_part` (f5:260 / f5:331) is
AUTHOR content (f2:178's object); `state_part` is built from
`blended_x = sqrt(1-kappa)*x + sqrt(kappa)*shock_x` (f5:277 / f5:364) whose
`x` is the author-private AR(1) state (redrawn in the long variant, f5:348-352,
with the same per-author φ) and whose `shock_x`/`shock_long` is
occasion-common content from the unchanged `f2().shock_vector` (f2:121-126,
called at f5:360). With F1's calibrated shares w_mu=0.15, w_x=0.15, w_e=0.70:
at **κ=1.0** the truth object is **exactly ½ author-mean and ½
occasion-common** (the AR term's coefficient is exactly 0); at **κ=0.5** it is
**¾ author** (½ mean + ¼ AR) and ¼ common. The isotropic noise channel — 70 %
of the RESPONSE variance — is excluded from both. No adjudication offered;
this feeds the F5 re-typing and the line synthesis.

**Anomalies, all disclosed with timing.** (i) The `holdout` stage was invoked
in the FOREGROUND (07:07:40 UTC) and the shell harness detached it to the
background at its own 600 s cap, re-attaching on completion (exit 0, 710.3 s):
no background job was launched by the executor, no monitor was used, and the
invocation/stage/workers/outputs are exactly the foreground call's. (ii) G0d's
parser reading (Part 0, before any arm). (iii) L-1's Monte-Carlo fragility
(necessarily discovered after the arms; both readings reported, registered
reading controls). (iv) The "MISS with OVERLAP" registered-branch gap.
(v) L-3's in-sample and out-of-sample readings disagree in sign; both
reported. (vi) Registration-text observation, recorded not repaired: G1d is
listed among the "Part 0 gates" but is unmeasurable before the main intact arm
exists — resolved before any arm as register-note R-0.6 (own stage,
code-enforced stop). Stage estimates vs actual: arms 355.754 → 529.1 s
(1.487×), ×32 holdout 734.460 → 710.3 s (0.967×). No background jobs launched,
no monitors, no smoke runs.

### Planner adjudication (2026-08-09, appended after the run)

Leans scored as executed: **L-1 HOLD — the registered reading controls, and
the verdict is BOUNDARY-SEATED** (registered B=2000 upper 0.24832554505807228
inside ±0.25 by 0.0017; B=100000 outside by 0.0017; 5/10 alternate seeds;
Δγ > 0 at 10/10 seeds and both B). No re-scoring — re-choosing among readings
after seeing them would break the same discipline the registration protects —
but every consequence below carries the boundary status in its text. L-2 HOLD
maximal (40/40 world-points; the contrast GROWS with scale, +0.0120 at ×1 →
+0.2095 at ×16). L-3 HOLD as a non-rejection, with the rule-9 second reading
(F4's own predict-then-holdout) favoring the DELETED arm out-of-sample
(gap 0.0490 vs 0.0807). G1d replication is strong (fresh intact CI contains
F4's whole band). No pivot fires.

**L-1's registered consequence executes today:** F4's row re-types
**"author axis → replicate axis (frame-readout economics)"** and the D3
prior re-types **"recruit replicates, not words"** — dated note III appended
to `docs/SUICA_M4_F_PANEL_DESIGN_SYNTHESIS.md` (which also records the
G-info-F5 truth-object fact), addendum to
`docs/SUICA_DISPLACEMENT_PROBLEM_RESOLVED.md`, theory consequences in IDT
appendix G. The honest content of the re-typing: the law survives total
author deletion with its form intact and its exponent within F4's own band
under every reading; the axis is STEEPER (Δγ +0.1259 [0.0169, 0.2483],
sign robust), HIGHER at every scale, better-predicting out-of-sample, and
less than half as expensive (half-agreement budget 48.865× → 19.878×)
without the authors it was named after. Author-mean content drags the axis —
interference extended from the composition LEVEL (K1b/K1c′) to the scaling
SLOPE.

**Planner registration defects recorded (#16, #17):**
- **#16** — G1d was listed among "Part 0 gates" though unmeasurable before
  the intact arm exists; the executor's R-0.6 stage-with-enforced-stop was
  the correct repair-in-place. Registration structure flaw.
- **#17** — the pivot space had a GAP: P2d covered "L-1 MISS ∧ γ_deleted
  DISJOINT" but not "MISS ∧ OVERLAPPING", and the measurement sat exactly on
  that boundary. Future pivot antecedents must PARTITION the outcome space.

**Standing rule 13 (added 2026-08-09, paid for by L-1's fragility):** every
registered interval clause names its resampling spec (B and seed policy) in
the registration; at adjudication the executor checks verdict stability at
≥10× B, and if the clause boundary lies within achievable Monte-Carlo error
of the estimate, the lean is scored **BOUNDARY** — neither HOLD nor MISS —
and every downstream consequence carries that status. (Applied prospectively
from K2a; K1d's HOLD stands under its own registration.)

**Convention note (from anomaly ii):** a bit-exact anchor against a
PRE-round-trip-convention artifact must name the parser that produced the
legacy number; K1d's dual-reading table is the template.

---

## M4-K2a — Instrument leg: an expressive world (slow state + person×occasion channel) and the two-split probe validated

**REGISTERED 2026-08-09, BEFORE RUN.** Planner: this document's author.
Executor: dispatched agent. Purpose: IDT appendix E.3(a) — the F2 family
cannot express person×occasion content, and K2's T4-branch adjudication
needs (i) a world that can and (ii) a validated card-level state probe
(appendix A's two-split probe). **This leg builds and VALIDATES the
instrument against designed identities; it adjudicates NO theory branch.**

### Machinery

`scripts/run_suica_m4_k2a_expressive_world.py` — the extended generator
lives in the LEG SCRIPT (suica_core untouched; f2 imported for its objects,
rule-12 naming). Response of author i, event t, occasion o:

  x(i,t,o) = w_mu·mean_part_i + w_slow·slow_i(t) + w_int·s_int(i,o)
             + w_c·common(o) + w_e·noise(i,t)

- `mean_part_i` — f2:178's object (the trait; **trait b := this vector**);
- `slow_i(t)` — f2's author AR construction (f2:172-176) with PINNED φ_slow
  per arm (the state whose τ_s the probe must read);
- `s_int(i,o) = ⟨a_i, shock_int(o)⟩/√k` — NEW person×occasion interaction:
  per-author unit loading a_i (fresh seeded rng) applied to an
  occasion-keyed shock stream independent of `common(o)`;
- `common(o)` — f2:121-126's shock object (the frame channel);
- weights sum-of-squares normalized per arm; realized shares reported.

### Arms (card-space only — no deployed-gauge runs in this leg)

φ_slow ∈ {0.5, 0.9, 0.98} × n_occ ∈ {8, 32} × w_int ∈ {0, equal-share};
12 cells × 8 worlds, master_seed 20260815. Occasions iid within cell
(spacing/decorrelation structure per cell pinned in Part 0).

### Part 0 gates

- **G0a** — channel construction verified: four-channel reconstruction
  residual ≤ 1e-12; realized variance shares within 1% of design per cell.
- **G1a (rule 10)** — each channel's presence changes panels (RMS > 1e-6);
  w_int = 0 vs equal-share differ; no registered contrast degenerate.
- **G2a (rule 3)** — liveness: every channel's share > 0 in every non-zero
  arm; slow-state decorrelation time consistent with pinned φ_slow
  (measured ACF at lag 1 within CI of φ_slow per cell).
- **G3a (power + rule 11 + rule 13)** — 2-world pilot; per-cell MDEs for
  V-1..V-3; every CI clause satisfiability-checked with DIRECTIONS stated;
  resampling spec: B = 2000, seed = master_seed, verdict-stability check at
  ≥10× B for any clause landing within 2× its Monte-Carlo half-width of a
  boundary (rule 13's first application).
- **G4a** — Part-0 point predictions COMPUTED BEFORE ARMS from the appendix
  A/B algebra: per (φ_slow, n_occ) cell, the predicted two-split gap
  ρ_interleaved − ρ_contiguous and the predicted trait attenuation
  r(card → b) = σ_b/√(σ_b² + Var(s̄) + Var(s̄_int) + σ_e²/n_eff), with
  Var(s̄) from the exact AR sum (appendix B's formula, m = n_occ).
- **G5a** — hygiene; round-trip parsing; rule-12 header for ALL new objects
  (defined in-script, line numbers cited at commit).

### Leans (designed-identity validations; 12 cells; per-cell CI vs Part-0 prediction; pooled paired bootstrap B=2000)

- **V-1 [prior .80]** — the two-split probe reads τ_s: per-cell measured
  ρ_int − ρ_contig within CI of the Part-0 prediction in ≥10/12 cells, and
  the (φ_slow, n_occ) ordering matches the predicted ordering exactly.
- **V-2 [prior .80]** — attenuation algebra: measured r(card → b) within CI
  of prediction in ≥10/12 cells.
- **V-3 [prior .75]** — the interaction channel is typed correctly: with
  iid occasions its contribution to the CONTIGUOUS-split reproducible
  component is 0 within an equivalence margin derived from n_occ (one-sided
  where applicable, defect-#15 lesson), while its same-occasion signature
  has CI excluding 0 in every w_int > 0 cell — occasion-bound person
  content, the object the family lacked.

### Pivots (pre-committed)

- **P1a** — V-1 fails in ≥3 cells → the probe algebra (appendix A) is wrong
  as coded or as derived → STOP the K2 line pending theory repair; the
  failure cells' full geometry published.
- **P2a** — V-3 fails → the interaction construction is not occasion-bound
  as typed → redesign the channel (instrument defect, no theory
  consequence).
- **P3a** — G1a/G2a fail → STOP, defect, no arms.

### Deliverables

The six: script; `results/m4_k2a_expressive_world/` (manifest.json,
gates.json, per-cell CSVs, decision.json — gitignored);
`reports/SUICA_M4_K2A_EXPRESSIVE_WORLD_REPORT.md` (Part 0 with the point
predictions first, timestamped before arms); outcome appended here; ledger
row; ONE commit (`feat(m4-k): K2a — ...`), never amended, not pushed by the
agent. Budget: card-space only — target < 20 min wall; stop-and-report at 2×
any Part-0 stage estimate.

### OUTCOME (appended 2026-08-09, after execution — the registration above is unedited)

Executed as registered. Script `scripts/run_suica_m4_k2a_expressive_world.py`;
report `reports/SUICA_M4_K2A_EXPRESSIVE_WORLD_REPORT.md` (Part 0, with the G4a
point-prediction table, written to disk before the `arms` stage — enforced in
code by `require_part0()`); artifacts `results/m4_k2a_expressive_world/`.
12 cells × 8 worlds × 256 authors (2048 pooled authors/cell), 2 events per
occasion, `master_seed 20260815`, reserved Part-0 pilot worlds 9501–9502,
card space only — the deployed gauge was never invoked. **Total compute 10.9 s**
(part0 1.983 s, arms 1.997 s, finalize 6.749 s, post-hoc diagnostic 0.189 s).

**Verdict:
`TWO_SPLIT_PROBE_VALIDATED__ATTENUATION_ALGEBRA_EXACT__INTERACTION_OCCASION_BOUND`.
V-1 HOLD, V-2 HOLD, V-3 HOLD. No pivot fires (P1a/P2a/P3a all no).**

- **Part 0 — all five gates pass.** G0a: five-channel reconstruction residual
  **2.220446049250313e-16**; realized shares within **0.0069843772** absolute of
  design (relative max 0.0305321845, dominated by `common(o)`, whose realized
  variance rests on only n_occ occasion draws — analytic relative sd 5.259% at
  n_occ=8, so 0.58σ); the two occasion-keyed streams read independent
  (|corr| ≤ 0.0724678130 against a sampling sd of 0.0510310363 = 1.42σ).
  G1a: minimum card-panel RMS change over all non-zero channels
  **0.0097964619** (floor 1e-6); w_int arms differ by RMS ≥ 0.0808514536
  (response) / 0.0172921872 (card). **`common(o)`'s card-panel residual is
  EXACTLY 0.0 — T3's designed cancellation, disclosed and excluded from the gate
  by argument.** G2a: pooled lag-1 ACF reads back the pinned φ_slow in 12/12
  cells family-wise (10/12 at an uncorrected per-cell 95%; the single miss is a
  2.23σ fluctuation, confirmed against an independent Monte-Carlo of the
  estimator's own expectation, max |E[φ̂] − φ| = 8.51e-04). G3a: MDEs per cell,
  every clause satisfiability-checked with DIRECTIONS stated, the V-3a
  equivalence margin set by a pre-stated ν∈{1,2,4} ladder (ν=1 at n_occ=8,
  ν=4 at n_occ=32). G4a: the 12-cell point-prediction table computed from the
  appendix A/B algebra before any arm.
- **V-1 [.80] HOLD.** Gap CI contains the Part-0 prediction in **11/12** cells
  (threshold 10), and — the sharper clause — **the (φ_slow, n_occ) ordering
  matches the prediction EXACTLY in both arms and in the pooled 12-cell
  reading**, including the algebra's non-monotonicity in φ and the
  arm-dependent (0.98,32)/(0.9,8) rank swap that only RN-2's renormalization
  produces. The single miss (`phi0.9_occ8_intequal`) is 0.00012 outside a
  0.0051-wide interval and STABLE at B=20000.
- **V-2 [.80] HOLD, 12/12** (and 12/12 under the author-centred second
  reading). Largest absolute error 0.0021079, largest relative error **0.30%**,
  under CI half-widths as tight as 0.0006. `r = σ_b/√(σ_b²+Var(s̄)+Var(s̄_int)
  +σ_e²/n_eff)` with the exact AR sum at m = n_occ is exact on this world to
  within measurement error at 2048 authors.
- **V-3 [.75] HOLD, 6/6 and 6/6.** The interaction's contribution to the
  CONTIGUOUS cross-half reproducible covariance clears the margin in all six
  cells under **all three readings** (registered one-sided upper,
  occasion-inflated upper, two-sided TOST) — and clears even the strictest ν=1
  margin: largest one-sided upper anywhere **+0.0017942**, |λ| ≤ 0.0374 of one
  shared occasion's worth. The same-occasion signature has one-sided lower CI
  > 0 in all six cells **and lands on its predicted magnitude `(C/n_occ)(1−1/n)`
  in 6/6**. The interleaved split (second reading, also predicted 0) agrees.
  **IDT appendix E.2's missing object now exists, is measurable, and is typed
  correctly: invisible across occasions, fully visible within one.**
- **Rule 13, first application: 6 clauses triggered, ZERO BOUNDARY** — every
  triggered verdict stable at B=20000, including `phi0.98_occ32_intequal`'s gap
  sitting 1.8e-05 (0.43 MC sd) inside its CI edge. Cost ≈ 4 s; changed no
  verdict.

**The one non-exactness, and the K2b consequence (report §1.4).**
`ρ_interleaved` **alone** contains its prediction in only 8/12 cells — and the
misses partition perfectly by design: **6/6 containment where there is no
interaction channel, 2/6 where there is.** Cause (pre-declared in G3a): the
registered authors-within-world bootstrap CONDITIONS on each world's realized
occasion-level draws, including the interaction shocks `S(o)`, whose realized
second moments fluctuate at relative sd √(2/k)=20.4% per occasion (3.61% on the
card's interaction variance at n_occ=8) — a ±0.0017–0.0019 wobble the
conditional CI (se ≈ 0.0010–0.0015) cannot cover. A post-hoc world-block
resample (flagged post-hoc, not a lean input) raises w_int>0 containment from
2/6 to 5/6, confirming a coverage effect rather than an algebra error.
**V-1's registered statistic survives because both splits carry the identical
`C/m_h` interaction term, so the wobble largely cancels in the DIFFERENCE.**
Standing consequence for K2b: *read the gap, not either half*; any clause about
a single split's ρ must use a world-level resample or carry the analytic
occasion-level term. Recorded second readings for the same object:
mean-of-cosines **5/12**, mean-centred pooled Pearson **11/12**, registered
uncentred pooled **11/12** — build on a pooled second-moment form, not a
mean-of-cosines.

**Two registration ambiguities were caught and resolved BEFORE any main arm and
before any hypothesis-relevant number existed** (rule 9, both readings reported
in the report's Part 0): (i) G2a's ACF clause pinned neither CI level nor
multiplicity — resolved to family-wise 95% over the 6 distinct (φ, n_occ)
pairs, since a 12-of-12 uncorrected per-cell 95% requirement fails 26.5% of the
time on a correct generator; (ii) "realized shares within 1% of design" is
unsatisfiable under a 1%-relative reading (a 0.19σ demand on `common(o)` at
n_occ=8) — resolved to the absolute percentage-point reading, with the
derivation. A third disclosure carries no ambiguity: `common(o)` is exactly
inert in this leg's measurement space by T3, which is why its share
fluctuation cannot touch V-1/V-2/V-3.

**Construction audit (rule 8), run after the arms and disclosed as such:**
this leg's `mean_part` + latent→64 mirror is verified **bit-identical
(residual 0.0)** to f2's own `generate_world_composed` in all six
(φ_slow, n_occ) configurations, using f2's own generator with
`w_mu=1, w_x=0, w_e=0` as a bit-exact oracle. It was an asserted docstring
claim at Part 0 and became a measured one only in the post-arms `diagnostic`
stage; `gates.json`/`decision.json` were not rewritten, so the Part-0 audit
trail is untouched.

**The instrument is delivered and K2b is unblocked** on the T4-simple vs
T4-reader-mediated branch, with a validated card-level positive control and a
world that can express person×occasion content.

### Planner adjudication (2026-08-09, appended after the run)

V-1 HOLD (11/12 + EXACT ordering including the non-monotone structure and
the arm-dependent rank swap — the probe reads τ_s), V-2 HOLD (12/12,
attenuation algebra exact to ≤0.30% relative — appendix B's formula is now
MEASURED), V-3 HOLD (6/6 + 6/6 — the interaction channel is occasion-bound
person content as typed). Rule 13's first application worked as designed:
6 boundary-near clauses triggered, all STABLE at 10×B, zero BOUNDARY. No
pivot fires. **The instrument is CERTIFIED for K2b**, with two riders that
K2b's registration binds: (i) **read the GAP** (ρ_int − ρ_contig), never
either split half alone — the registered authors-within-world bootstrap
conditions on realized occasion shocks and under-covers half-level
predictions (8/12) while GAP-level containment is immune; (ii) per-half
predictions, if ever wanted, need world-block resampling (the agent's
post-hoc check, correctly flagged as such).

**Planner registration defects recorded (#18, #19):** #18 — G2a's ACF
clause pinned neither CI level nor multiplicity (executor resolved to
family-wise 95% over 6 before arms, both readings reported); #19 — "shares
within 1% of design" was ambiguous (absolute vs relative) and relatively
UNSATISFIABLE for the common channel at n_occ draws (a rule-11-family
miss; resolved to absolute before arms). **Convention added:** any
bit-identity claim stated in Part 0 is VERIFIED in Part 0, not asserted
(K2a anomaly vi: the mean_part-mirror identity was asserted at Part 0 and
measured only post-arms — it passed at residual exactly 0.0, but the
ordering was wrong).

---

## M4-K2b — The T4 branch: card algebra or reader floor? (dissociation on the validated instrument)

**REGISTERED 2026-08-09, BEFORE RUN.** Planner: this document's author.
Executor: dispatched agent. This is the K2 charter executed on the K2a
instrument, with all five refinement requirements and both K2a riders.

### Question

T4-simple: the card/biography gap is CARD algebra — trait recovery is
governed by the state share and persistence via the (now-measured)
attenuation formula, and the deployed gauge tracks it. T4-reader-mediated:
the deployed gauge imposes its own floor (frame reading — K1/K1b/K1c′/K1d's
arc), which card algebra does not move. K2b dissociates them: manipulate
the state share and persistence on the expressive world, run BOTH channels
per arm — the validated card-level GAP probe (positive control) and the
deployed gauge's trait recovery — and see which moves.

### Arms

Six state configurations at fixed n_occ and fixed budget, master_seed
20260816, 8 worlds each (escalation ladder in G1b):

A1 (share .02, φ .9) · A2 (.10, .9) · A3 (.30, .9) · A4 (.50, .9) ·
A5 (.30, .98) · A6 (.50, .98)

where share = w_slow² fraction of non-noise signal variance; w_int = 0 in
the primary arms (one descriptive companion cell at (.30, .9, w_int
equal-share), no gate). Panels emitted in the deployed gauge's input format
at K1-pinned dims (985 authors, F2 m-multiset, 4 contexts).

### Channels per arm

- **Card channel (positive control, reader-free):** the two-split GAP
  ρ_interleaved − ρ_contiguous and card attenuation r(card → b), computed
  exactly as K2a validated them, with Part-0 point predictions from the
  same algebra. Per K2a rider (i), only GAP-level and attenuation
  quantities carry gates — no split-half-alone gate.
- **Field channel (the deployed gauge):** long-window trait recovery :=
  field agreement between the gauge's estimated field and the b-only truth
  field (truth = mean_part-only responses through the same frozen map —
  G4b verifies the construction bit-exactly by generating with
  w_slow = w_int = w_e = 0). The F5-style MIXED-truth recovery is computed
  alongside, descriptively (continuity with G-info-F5's composition table).

### Part 0 gates

- **G0b (format + consistency anchor)** — the gauge accepts the expressive
  world's panels; retained-author count reported; one K2a cell re-derived
  bit-exactly with K2a's seeds (instrument continuity); a pure-F2 sanity
  world (unmodified generator, κ=1.0, shared, K1 dims) run once — its
  agreement must fall inside K1d's ×1 intact per-world range (consistency,
  not bit-anchor; rule-12 provenance that the gauge path is THE code).
- **G1b (power, rule 2 + the charter's ≥3×MDE requirement)** — Part-0
  point predictions of T4-simple's field recovery per arm from the
  validated algebra; 2-world gauge pilot for sd; REQUIRE: predicted
  extreme-arm swing (A1 vs A4) ≥ 3× MDE(80%, α=.05, paired, n=8).
  Escalate worlds 8→16→32 once each if not; still short at 32 →
  ABORT-report.
- **G2b (rule 10 + rule 3)** — arms differ in panels; the manipulation
  moves the card channel per prediction on the pilot (liveness of the
  designed lever); state share realized within tolerance per arm.
- **G3b (rule 11 + rule 13)** — every clause satisfiability-checked with
  directions; resampling spec B=2000, seed=master; stability at ≥10×B for
  boundary-near clauses; one-sided clauses one-sided.
- **G4b (truth construction)** — b-only truth field verified bit-exactly
  against the w_slow=w_int=w_e=0 generation; rule-12 names all objects.
- **G5b (hygiene)** — round-trip parsing; stages CHUNKED under the shell's
  600 s cap (K1d anomaly-i lesson); no background jobs, no monitors.

### Adjudication space (PARTITIONED — defect #17's lesson)

With L-A the positive control and S := measured extreme-arm field-recovery
swing vs P := T4-simple's predicted swing:

- **L-A [prior .85]** — positive control: card GAP and attenuation track
  Part-0 predictions across arms (per-arm CI containment ≥5/6 on each,
  ordering exact). FAIL → INSTRUMENT-FAIL branch: STOP, back to
  instrument work; no theory adjudication.
- **L-B (T4-simple) [prior .25]** — field recovery tracks the card
  algebra: Spearman(predicted attenuation, measured field recovery) = 1
  across 6 arms (exact permutation p ≤ .005) AND S/P ∈ [0.5, 2] with
  pooled CI inside [0.33, 3].
- **L-C (T4-reader-mediated) [prior .65]** — the floor: S < P/3 with
  pooled CI upper bound < P/2, while L-A HOLDS (the lever moved the card,
  not the gauge).
- **PARTIAL (named branch, no prior — reported if neither L-B nor L-C)** —
  S/P ∈ [1/3, 1/2] or ordering partially tracks (Spearman ∈ (0,1) with
  p < .05): both mechanisms live; K2c designs the decomposition.
- **L-D [prior .60, descriptive-to-lean]** — the gauge reads the mixture
  better than the trait: mixed-truth recovery > b-only recovery in 6/6
  arms (per-arm CI excluding 0 in ≥5/6).

### Pivots (pre-committed)

- **P1b** — L-A fails → INSTRUMENT-FAIL (no theory reading; K2a′ next).
- **P2b** — L-C holds with L-A → **T4-reader-mediated becomes the
  registered form in IDT** (T4 branch resolved on a live, powered,
  positive-controlled channel); the F5 plateau re-attributes to the
  reader; registered follow-up candidate: does the certified de-framing
  preprocessor raise b-only recovery? (constructive repair question).
- **P3b** — L-B holds → T4-simple lives; K2c is the quantitative gap law
  (h/τ_s sweep on this instrument).
- **P4b** — PARTIAL → K2c is the decomposition design; no re-typing of T4
  either way.

### Deliverables

The six: `scripts/run_suica_m4_k2b_t4_branch.py`;
`results/m4_k2b_t4_branch/` (manifest.json, gates.json, per-arm CSVs,
decision.json — gitignored); `reports/SUICA_M4_K2B_T4_BRANCH_REPORT.md`
(Part 0 with predictions first); outcome appended here; ledger row; ONE
commit (`feat(m4-k): K2b — ...`), never amended, not pushed by the agent.
Budget: 6 arms × 8 worlds gauge runs + pilot + companion cell; target
< 40 min wall; stop-and-report at 2× any Part-0 stage estimate.

### OUTCOME (appended 2026-08-09, after execution — the registration above is unedited)

Executed as registered. Script `scripts/run_suica_m4_k2b_t4_branch.py`; report
`reports/SUICA_M4_K2B_T4_BRANCH_REPORT.md` (Part 0, with the point-prediction
table and all six gates, written to disk before the `arms` stage — enforced in
code by `require_part0()`); artifacts `results/m4_k2b_t4_branch/`.
6 primary arms + 1 descriptive companion × 8 worlds on the K1-pinned panel
(985 authors, F2 m-multiset `{8:272, 12:200, 16:513}`, 4 contexts, **565
retained**, 4 resolved), `master_seed 20260816`, reserved Part-0 pilot worlds
9601–9602, 56 adjudicated deployed-gauge world runs + 14 pilot runs + 2 pure-F2
sanity runs; card channel 4520 pooled authors/arm. **Total compute 59.20 s**
(part0 21.474 s, arms 14.285 s + 19.111 s, finalize 2.540 s, post-hoc
diagnostic 1.790 s).

**Verdict:
`PARTIAL__BOTH_MECHANISMS_LIVE__POSITIVE_CONTROL_EXACT__LD_HOLD`.
L-A HOLD, L-B MISS, L-C MISS, PARTIAL FIRES, L-D HOLD. **P4b fires**; P1b, P2b,
P3b do not.**

- **All six Part-0 gates pass.** G0b: gauge accepts the expressive world's
  panels (565 retained, constant across arms/worlds); the K2a anchor cell
  `phi0.9_occ8_intzero` re-derives from K2a's own seeds **bit-exactly (residual
  0.0** over 2048 rows × 35 columns); the pure-F2 sanity world reads
  **0.017013597299456222**, inside K1d's ×1 intact per-world range
  **[0.0006462726940075391, 0.0254557937918022]** (this leg's own floored layout
  reads 0.021853063018134767, also inside). G1b: `P = r(A1) − r(A4) =
  0.26881418197391516`; 2-world pilot paired sd 0.031262397763045804 → MDE(80%,
  α=.05, paired, n=8) **0.03604444203738883**, **P/MDE = 7.4578538820 ≥ 3** —
  **no escalation, 8 worlds**; realized-sd recheck at finalize gives MDE
  0.027291585561437 and P/MDE 9.8497092215. G2b: arms differ (min panel RMS
  0.01736197411054363); the lever moves the card in the PREDICTED order on the
  pilot (Spearman **1.0** on both GAP and attenuation); realized shares within
  **0.00063647 absolute** of design, state-share deviation ≤ **0.00052061**.
  G3b: every clause satisfiability-checked with directions (including the one
  that mattered — the minimum attainable exact permutation p at n=6 is
  1/720 = 0.00138889 ≤ .005). G4b: b-only and mixed truth panels verified
  **bit-exact (0.0)** against the literal `w_slow=w_int=w_e=0` and `w_e=0`
  generations, five-channel reconstruction 0.0, estimated field route-invariant
  0.0. G5b: chunked foreground stages, no background jobs, no monitors.
- **L-A [.85] HOLD, and exactly.** Card GAP CI contains the Part-0 prediction in
  **6/6** arms and card attenuation in **6/6** (threshold 5), under BOTH the
  registered authors-within-world bootstrap and rider (ii)'s world-block
  resample. **Both orderings match EXACTLY** — GAP `A4>A3>A6>A2>A5>A1`,
  attenuation `A1>A2>A3>A5>A4>A6` — two *different* orderings, neither the
  share order: the card resolves the φ effect. Attenuation error ≤
  **0.00064703 absolute / 0.0975% relative**. The lever moved the card GAP
  **15.2×** (0.0067716 → 0.1028370). **P1b does not fire; the theory reading is
  licensed.**
- **L-B [.25] MISS on both clauses.** Spearman(predicted attenuation, measured
  field recovery) = **0.9428571429**, exact permutation p (720 orderings) =
  **0.0083333333** > .005; the single inversion is `A3`/`A5`, whose measured
  difference is **+0.0061256, CI [−0.0021104, +0.0154459]** — not significant
  (the card channel got that pair right; the field cannot resolve it).
  **S = 0.1024492, S/P = 0.3811151, CI [0.3276799, 0.4410191]** — outside
  [0.5, 2] and not reaching it.
- **L-C [.65] MISS, on one clause, by 1.5–1.7 se.** `S < P/3` is **FALSE**:
  0.10244915371617286 vs 0.08960472732463838, exceeding the bar by
  **0.01284443** = 1.53 se (paired-t) / 1.65 se (world-block bootstrap). The CI
  clause HOLDS (upper 0.1185522 < P/2 = 0.1344071) and L-A holds. **The gauge
  moved slightly MORE than a floored reader may move.**
- **PARTIAL FIRES on both of its clauses:** `S/P = 0.3811151 ∈ [1/3, 1/2]` and
  `Spearman = 0.9428571 ∈ (0,1)` with `p = 0.00833 < .05`. Both mechanisms are
  live: the card lever moved the deployed gauge, in almost exactly the predicted
  order, at **38% of the predicted absolute swing**.
- **L-D [.60] HOLD.** Mixed-truth recovery > b-only recovery in **6/6** arms,
  per-arm CI excluding 0 in **5/6** (threshold 5). The miss is `A1`
  (+0.0031529, CI [−0.0008678, +0.0066365]) — the design's own prediction at
  share .02. The difference grows monotonically with the state share
  (A1 +0.0031529, A2 +0.0174173, A3 +0.0728456, A4 +0.1269062; A5 +0.0298799,
  A6 +0.0550154). At `A4` the gauge recovers the MIXTURE at 0.2023457 and the
  TRAIT at 0.0754395 — **2.7× more of the state-inclusive object than of the
  person.** This is the F5 plateau's shape, measured for the first time against
  a trait-only truth object.
- **Rule 13: 0 clauses triggered, 0 BOUNDARY** — every gated interval clause
  sits further than 2 Monte-Carlo endpoint sd's from its boundary at B=2000.
  (L-C's *failing* clause is a point comparison, outside rule 13's reach; its
  margin is reported in se units above.)

**THE FINDING THE PLANNER MOST NEEDS — the branch verdict is LINK-SENSITIVE,
and the registration did not pin the link.** RN-6 resolved it before any arm
(identity link PRIMARY, squared link a declared second reading, both reported).
On the same measurements: identity link → `S/P = 0.3811151` → L-C clause (a)
FALSE → **PARTIAL, P4b**. Squared link (`P = 0.3724535`, `S/P = 0.2750656`) →
**both L-C clauses TRUE with L-A holding → L-C HOLD → P2b**. The Spearman
clause is link-invariant, so PARTIAL's ordering clause is satisfied under both;
the partition suppresses it under the squared link only because L-C is checked
first. **Scored on the PRIMARY as declared; the disagreement is reported, not
resolved by the executor.**

**A descriptive shape that fits no registered branch (report §1.3).** In
absolute terms the swing is small (S/P = 0.381); in RELATIVE terms it is large —
field recovery falls **57.59%** from A1 to A4 (0.1778886 → 0.0754395) while the
card attenuation falls **32.50%** (0.8271785 → 0.5583643). With an
arm-independent reader efficiency `λ = 0.1741750`, **`S/(λ·P) = 2.1881165`**:
after removing a pure multiplicative efficiency the gauge **over-responds** to
the state share by more than 2×. Neither "tracks the card algebra" nor
"floored" — a third shape, and the reason an absolute-swing partition cannot
classify this result. Companion cell (descriptive): adding the person×occasion
channel at equal share drops b-only recovery from A3's 0.1096226 to
**0.0725774** while leaving mixed-truth recovery unchanged (0.1824682 →
0.1822902) — occasion-bound person content behaves, at the reader, like more
state.

**Two registration ambiguities caught and resolved BEFORE any arm (rule 9, all
readings reported).** (i) **The truth object**: "mean_part-only responses" and
"generating with `w_slow = w_int = w_e = 0`" are different objects, and the
strict reading is **DEGENERATE** — a constant-per-event panel's permutation
null equals the path itself, so the deployed transition branch is identically
zero (`max|K| = 4.440892098500626e-16`), the truth field collapses to round-off
(norm 6.68e-04 vs the operative 1.52e-01) and its "recovery" is meaningless
(−0.0245). The registration's own G4b construction (which retains the
author-invariant frame channel, so the field's PERSON content is still `b`
alone) was used. (ii) **The link** — see above; this one changes the branch.
A third resolution carries no ambiguity: RN-5's `(context, m)` norm cell, forced
by T3 (exact frame cancellation needs a shared occasion set, and the occasion
set here is determined by the author's own `m`); measured centred-frame residual
**9.992007221626409e-16**.

**Post-hoc diagnostic, run after the adjudication and flagged as such
(`post_hoc_diagnostic.json`; `decision.json`/`gates.json` untouched).** The card
GAP sits a near-constant **+0.00195…+0.00243** above prediction in all six arms
(contained 6/6, but at ~0.85 of the half-width each time). Diagnosed: with only
the trait and the frame present, both split-half ρ's are **1.0 to the last bit**
and the GAP is **exactly 0.0** in every m-cell — the card construction and T3's
cancellation are exact. The offset is carried entirely by the noise channel, and
the pooled GAP estimator is **unbiased** on centred iid noise (400-replicate MC
at this panel's cell sizes: means −0.00030923/+0.00037341/−0.00013342 against
se's 0.00047843/0.00057943/0.00036251, per-world sd matching the analytic
`1/√(N·D)`). It is therefore **one shared realization** — RN-4 pairs every arm
on the same world seeds — and the registered bootstrap covers it.

**K2c's brief, from this leg:** decompose (the registered PARTIAL consequence),
and **pin the link** — the branch cannot be adjudicated by an absolute-swing
partition whose verdict moves with an unregistered functional form. The
descriptive over-response (`S/(λP) = 2.19`) is the quantity K2c should target.

### Planner adjudication (2026-08-09, appended after the run)

Scored on the pre-declared PRIMARY (identity link, RN-6): **L-A HOLD exactly
(positive control perfect — 6/6 + 6/6 containment under both resamples, both
orderings EXACT, and the two orderings DIFFER, so the card instruments
resolve the φ effect), L-B MISS, L-C MISS on the point clause by 1.5–1.7 se
(its CI clause held), PARTIAL fires on both clauses, L-D HOLD (the gauge
reads the mixture better than the trait in 6/6 arms; 2.7× at A4). P4b is the
registered outcome: no re-typing of T4 either way; K2c decomposes.** The
squared-link second reading (which would have given L-C HOLD → P2b) is
disclosed and NOT resolved — re-choosing among links after seeing the
verdicts is the exact failure the discipline exists to prevent.

**The substantive discovery this leg leaves behind:** the field's response
to state share fits NEITHER registered mechanism cleanly — the gauge
**over-responds**: field recovery falls −57.59% across the design while the
card algebra says −32.50%; against an arm-independent efficiency λ =
0.1741750, S/(λ·P) = **2.1881165**. The reader loses the trait FASTER than
the card does — qualitatively what the interference account (appendices
F/G) predicts, and now a THIRD named candidate form for T4:
**T4-reader-amplified**. K2c adjudicates between "the field is a monotone
transform of card attenuation" (link curvature only — T4-simple-with-link)
and "the field responds to state COMPOSITION beyond attenuation"
(genuinely reader-borne pathology), on a design that needs NO link at all.

**Planner registration defect #20, recorded not repaired:** the K2b
registration compared quantities on two different scales (card attenuation
vs field agreement) without pinning the link function, and the branch
verdict is link-sensitive. The executor's RN-6 (identity PRIMARY, declared
before arms) preserved adjudicability; the defect is the registration's.
**Standing rule 14 (added 2026-08-09, paid for by #20):** when a lean
compares quantities across scales or instruments, the registration pins the
LINK function and its justification as part of the lean; absent that, the
lean must be re-designed to be within-instrument (link-free). K2c applies
the second clause.

---

## M4-K2c — Matched-attenuation pairs: is the reader a transform of card algebra, or does it read state composition? (link-free)

**REGISTERED 2026-08-09, BEFORE RUN.** Planner: this document's author.
Executor: dispatched agent. P4b's registered consequence, designed under
rule 14's link-free clause.

### Question

K2b showed the field over-responds to state share relative to card algebra
under the identity link, and the verdict flips under a squared link. The
link-free question underneath: **is field recovery a FUNCTION of card
attenuation alone** (then the reader is a fixed monotone transform of card
algebra — T4-simple-with-link, the over-response being link curvature), **or
does it depend on the state's COMPOSITION at fixed attenuation** (then the
reader carries its own state pathology — T4-reader-mediated/amplified in
substance)? Matched-attenuation pairs decide: same predicted card
attenuation, different (share, φ_slow) composition. Any field difference
within a matched pair is composition-sensitivity, measured field-vs-field —
no cross-scale link anywhere in the gates.

### Arms (master_seed 20260817; 32 worlds per arm)

Three matched pairs plus the K2b anchor, all w_int = 0, K1-pinned panel
dims, the K2a/K2b machinery unchanged:

- **Pair 1 (target attenuation ≈ 0.78):** P1a = (share s1a, φ .90) vs
  P1b = (share s1b, φ .98);
- **Pair 2 (target ≈ 0.68):** P2a = (s2a, .90) vs P2b = (s2b, .98);
- **Pair 3 (target ≈ 0.56):** P3a = (s3a, .90) vs P3b = (s3b, .98);
- **A1-anchor** = K2b's A1 (.02, .90) re-run at this seed lineage
  (continuity cell, no gate beyond G0c′ anchor use).

The shares s·· are COMPUTED IN PART 0 from the validated attenuation
algebra (K2a V-2, error ≤0.30%) so that within-pair predicted attenuations
are EQUAL to machine precision; realized (measured) attenuation equality is
then a designed identity to verify, not assume (G2c′).

### Part 0 gates

- **G0c′ (anchors)** — re-derive bit-exactly from
  `results/m4_k2b_t4_branch/decision.json`: A1/A4 field recoveries
  (0.1778886…, 0.0754395…), S/P = 0.3811151367233824, λ = 0.1741750,
  S/(λP) = 2.1881165; K2a anchor cell as in K2b's G0b.
- **G1c′ (matching, the designed identity)** — Part-0: within-pair
  predicted attenuation difference ≤ 1e-12. Post-arms (adjudicated with the
  arms but gating them): within-pair MEASURED card attenuation difference
  pooled CI inside ±0.005 (justified: 5× K2a's max attenuation error
  0.00065; if matching fails, the pair is VOID — composition claims need
  the match).
- **G2c′ (power, rule 2)** — 2-world pilot; MDE(80%, α=.05, paired, n=32)
  for within-pair field difference must be ≤ 0.020 (justified: the K2b
  over-response scale — differences at or above this are the ones that
  would carry the composition story; smaller real differences are declared
  sub-resolution, claims tiered). Escalate 32→64 once; still short → run
  and tier.
- **G3c′ (rule 11 + rule 13)** — satisfiability with directions; B=2000,
  seed=master; ≥10×B stability for boundary-near clauses.
- **G4c′ (rule 3)** — lever liveness: across-pair (between targets) card
  and field movements present per prediction; within-pair composition
  contrast verified non-degenerate (panels differ, rule 10).
- **G5c′ (hygiene)** — round-trip; chunked stages < 600 s; rule-12 header;
  no background jobs/monitors.

### Adjudication space (PARTITIONED, link-free)

Let D_k = field(P_ka) − field(P_kb) within pair k, pooled paired bootstrap.

- **L-1 (function-of-attenuation) [prior .40]** — 3/3 pairs: |D_k| pooled
  CI inside ±m_k where m_k = max(0.020, MDE_k) (equivalence form, rule 4).
  Registered consequence: T4 re-types **T4-simple-with-link** — the reader
  is a fixed monotone transform of card algebra; the link exponent q is
  then estimated on all K2b+K2c arms and reported with CI (descriptive, no
  gate).
- **L-2 (composition-sensitive) [prior .45]** — ≥2/3 pairs: D_k CI
  excludes 0 AND all significant D_k share one SIGN (direction reported;
  sign consistency is part of the lean). Registered consequence: T4
  re-types **T4-reader-mediated (composition-reading form)**; the follow-up
  candidate is the constructive repair test (does de-framing raise b-only
  recovery — the P2b follow-up inherited).
- **PARTIAL-C (named)** — exactly 1/3 significant, or significant D_k with
  MIXED signs: composition-sensitivity exists but is not uniform; K2d
  designs the localization.
- **L-3 [prior .70, descriptive-to-lean]** — pooled q (fit of
  log(field/λ) on log(attenuation) across K2b's 6 + K2c's 7 arms): q > 1
  with CI excluding 1 (the over-response is real across the pooled curve,
  whatever the branch).

### Pivots (pre-committed)

- **P1c′** — G1c′ matching fails in ≥2 pairs → the attenuation algebra
  does not transfer to gauge dims at matched-pair precision → instrument
  question returns to K2a′; no theory adjudication.
- **P2c′** — L-1 holds → T4-simple-with-link registered in IDT; the
  interference account's slope claim (appendix G) is REVISED to "link
  curvature, not extra pathology" — a real theory correction, stated as
  such.
- **P3c′** — L-2 holds → T4-reader-mediated (composition form) registered
  in IDT; constructive repair test becomes the next registration.
- **P4c′** — PARTIAL-C → K2d localization.

### Deliverables

The six: `scripts/run_suica_m4_k2c_matched_pairs.py`;
`results/m4_k2c_matched_pairs/`; `reports/SUICA_M4_K2C_MATCHED_PAIRS_REPORT.md`
(Part 0 with computed shares and predictions first); outcome appended here;
ledger row; ONE commit (`feat(m4-k): K2c — ...`), never amended, not pushed
by the agent. Budget: 7 arms × 32 worlds (compute scale: K2b's whole leg ran
59 s at 8 worlds × 7 arms) — target < 15 min wall; stop-and-report at 2× any
Part-0 stage estimate.

### OUTCOME (appended 2026-08-09, after execution — the registration above is unedited)

Executed as registered. Script `scripts/run_suica_m4_k2c_matched_pairs.py` (the K2b
apparatus imported and called UNMODIFIED); report
`reports/SUICA_M4_K2C_MATCHED_PAIRS_REPORT.md` (Part 0 — computed shares, all seven
arms' predictions, all six gates — written to disk at 09:14:02Z BEFORE the `arms`
stage, enforced in code by `require_part0()`); artifacts
`results/m4_k2c_matched_pairs/`. 7 arms × **32 worlds** (power ladder selected 32,
**no escalation**), `master_seed 20260817`, K1-pinned panel (985 authors, **565
retained**, 4 resolved), card channel 18 080 pooled authors/arm, **224 adjudicated
deployed-gauge world runs** + 14 reserved-pilot runs (worlds 9701–9702).
**Total compute 154.739 s** (part0 11.620, arms 64.638 + 65.168, finalize 13.313) —
inside the Part-0 estimate (178.088 s), far inside the 2× stop threshold (356.176 s).

**Verdict: `BOTH_FIRE__SIGNIFICANT_BUT_SUB_MATERIAL__MATCH_EXACT__L3_HOLD`.
L-1 FIRES and L-2 FIRES SIMULTANEOUSLY, L-3 HOLDS, PARTIAL-C does not fire,
0 pairs VOID. NO PIVOT FIRES — P1c′, P2c′, P3c′, P4c′ all false. T4 is NOT
re-typed.**

- **All six Part-0 gates pass.** **G0c′**: all six K2b anchors re-derived from
  persisted artifacts **bit-exactly, residual 0.0** — A1 field 0.177888649457317,
  A4 field 0.07543949574114414, S 0.10244915371617286, S/P 0.3811151367233824,
  λ 0.17417497661611914, S/(λP) 2.1881164799198363; K2a anchor cell
  `phi0.9_occ8_intzero` re-derived from K2a's own seeds bit-exactly (2048 rows × 35
  columns, residual 0.0). **G1c′ (Part-0 half)**: the COMPUTED shares —
  **P1 (target .78): s_1a = 0.10921276830855525, s_1b = 0.0873786568216755;
  P2 (.68): 0.29267462506992153 / 0.24421800730418725; P3 (.56):
  0.4973617623232523 / 0.4359007987784457** — give within-pair predicted
  attenuation differences **1.110223e-16 / 0.0 / 0.0**, all ≤ 1e-12, 3/3.
  **G2c′**: 2-world pilot paired sd 0.00719109 / 0.02243239 / 0.03661105 →
  MDE(80%, .05, paired, n=32) **0.00367748 / 0.01147180 / 0.01872269**, all ≤ 0.020,
  **no escalation**. **G4c′**: across the four designed levels the pilot card
  attenuation (0.82560 → 0.77771 → 0.67693 → 0.55635) and the pilot field recovery
  (0.17916 → 0.15770 → 0.12756 → 0.08829) are both strictly decreasing; within-pair
  panels differ (RMS 0.01577 / 0.02597 / 0.03408) and the composition contrast is
  non-degenerate; frame-channel centred residual 1.2212453270876722e-15.
  **G3c′/G5c′**: every clause satisfiability-checked with directions; foreground
  chunked stages, 0 background jobs, 0 monitors.
- **G1c′ post-arms: the designed identity SURVIVED CONTACT, 0 VOID.** Measured
  within-pair card attenuation differences **−3.500143943835354e-05** (CI
  [−0.000199412, +0.000137024]), **−0.00012046646286067997** (CI [−0.000445341,
  +0.000219353]), **−0.00021915556724860785** (CI [−0.000700178, +0.000279593]) —
  **23×–143× tighter than the ±0.005 margin**. **P1c′ does not fire; the composition
  reading is licensed.** Instrument continuity (no gate): card attenuation contains
  its Part-0 prediction 7/7 and the card GAP 7/7, max relative attenuation error
  0.171%.
- **D_k = field(P_ka) − field(P_kb), paired world-block bootstrap B=2000:**
  **P1 −0.0033349254353831808** CI [−0.007617710100740499, +0.0011074921964934288];
  **P2 −0.012167516605861444** CI [−0.017430001829670642, −0.006619210190334735];
  **P3 −0.01355928388620139** CI [−0.018647677326514903, −0.008674340005325598].
  **L-1 [.40] fires** (3/3 inside ±m_k, m_k = 0.020 under BOTH RN-3 readings).
  **L-2 [.45] fires** (2/3 significant — P2, P3 — and **all significant D_k share one
  sign, NEGATIVE**; P1 is negative too, just unresolved). **PARTIAL-C does not fire.**
- **RN-4 (fixed in Part 0, before any hypothesis number): the registered
  adjudication space is NOT A PARTITION — L-1 and L-2 are not mutually exclusive, and
  BOTH FIRED.** A difference can be statistically resolved and still lie inside the
  materiality margin, which is exactly what happened. Scored as the named
  NON-REGISTERED outcome **BOTH_FIRE**, reported as such; **T4 is not re-typed either
  way**; both readings reported at full precision.
- **THE SUBSTANCE, which the partition failed to capture.** At card attenuation
  matched to 1e-16, the field difference is **real, unanimous in sign (3/3 negative),
  and monotone in state content**: |D_k| is **2.079% / 9.654% / 15.230%** of the pair's
  own recovery level. The direction: **the arm with MORE state share (and less
  persistence) loses MORE of the person.** So the field is **not** a function of card
  attenuation alone — *T4-simple-with-link is falsified as a strict claim*, surviving
  only as an approximation with a ≤0.02 error budget over attenuation 0.56–0.78, and
  the error is growing. **It was the materiality margin, not the physics, that kept
  L-1 alive: P3's equivalence clause holds by 0.001352 = 0.533 se of D_k** (8.92 MC
  endpoint sd, so rule 13 correctly does not flag it — but the sampling headroom is
  half a standard error, and a fourth, higher-state target would very likely breach
  the margin). The composition contrast is loud in the CARD — measured GAP_a/GAP_b =
  **4.04 / 4.08 / 3.98** at matched attenuation — and the reader converts that 4×
  card difference into a 2–15% trait difference.
- **The descriptive (mixed-truth) channel says the same thing 4.3× louder, and with
  the OPPOSITE sign.** At matched attenuation the higher-share arm recovers **more of
  the state-inclusive mixture**: Δmixed = **+0.00690393** CI [+0.00309391,
  +0.01096980], **+0.02470275** CI [+0.01918629, +0.03053346], **+0.05849219** CI
  [+0.05194404, +0.06514736]; Δ(mixed − b-only) = +0.01023885 / +0.03687027 /
  +0.07205148, every CI excluding 0. K2b's L-D reappears as a within-pair, link-free,
  attenuation-matched statement: **what the reader gains on the mixture it loses on
  the trait.**
- **L-3 [.70, descriptive-to-lean, NO branch weight] HOLD.** Pooled OLS of
  log(field/λ) on log(attenuation) over **13 arms** (K2b's 6 + K2c's 7):
  **q = 1.9337620539521978, CI [1.7337263621727161, 2.1932591297891246]**, one-sided
  5th pct 1.7596140020708688, **R² = 0.9581580947902524**; q > 1 and CI excludes 1.
  RN-5 second reading (x = measured attenuation): q = 1.9360338584090482, CI
  [1.7342166898270828, 2.196563507630189] — same verdict. RN-6: the slope is
  **exactly** λ-invariant (q at λ_K2b minus q at λ=1 = 0.0). K2b's two-arm
  over-response S/(λP) = 2.1881 is now a **smooth pooled exponent across two legs**,
  not an artifact of two extreme arms.
- **Rule 13: 0 clauses triggered, 0 BOUNDARY.** Closest approaches (post-hoc
  descriptive, decision.json untouched): 8.34 MC-sd (P1's zero-exclusion), 8.92 MC-sd
  (P3's equivalence), 15.73 MC-sd (P2's equivalence); all others ≥ 40 MC-sd.
- **Rule 14 verified on this leg's OWN gates, as instructed: no gate and no branch
  lean compares quantities across scales.** G0c′ re-derives K2b numbers against
  themselves; G1c′ is card-vs-card; G2c′/G4c′/L-1/L-2/PARTIAL-C are field-vs-field.
  L-3 is the single cross-scale object, and the registration declares it
  descriptive-to-lean with no branch weight — and it pins its own link (a log-log
  power law whose exponent IS the estimand), so rule 14's first clause is satisfied
  for it and its second clause for everything that adjudicates T4.
- **Continuity (no gate):** `A1anc` (.02, .90) at the fresh lineage reads
  0.1785831487097378 CI [0.17058563431737153, 0.18747529579718702] against K2b's A1
  at 0.177888649457317 — difference +0.0006944992524207938, well inside the CI.
- **What K2c does NOT decide (limitation, not a hedge):** a matched-attenuation pair
  necessarily moves share and persistence TOGETHER along the iso-attenuation curve.
  K2c establishes THAT the field reads composition at fixed attenuation and IN WHICH
  DIRECTION, but cannot say whether the carrier is the state SHARE or the state
  PERSISTENCE. Breaking that collinearity needs a third state parameter (or an n_occ
  lever) — the natural K2d localization.
- **Anomalies (with timing).** **A-1 (Part 0, before any hypothesis number):** K2b's
  hardcoded t-quantile table carries t_{.80,31} = 0.8534705711311653, which is
  +1.0027543422130858e-04 above the correct 0.853370295696944; **impact on K2b: none**
  (K2b selected n=8 and never evaluated its n=32 entry). K2c uses scipy-verified
  values (max abs deviation vs `scipy.stats.t.ppf` **0.0**, scipy 1.17.1). **A-2
  (structural, resolved in Part 0 as RN-4):** the registered space is not a partition;
  it bit. **A-3 (provenance, RN-2):** because `k2b.run_field_world` is called
  unmodified, the deployed corpus tags literally read `m4k2b-K2C-<arm>-w<k>`; they are
  hash labels only and every K2c tag is disjoint from every K2b tag. No crashes, no
  re-runs, no background jobs, no monitors, no stage over its Part-0 estimate.

**K2c's brief to the planner:** (i) do not re-type T4 on this leg — the registered
space could not classify the result; (ii) the link-free question is nonetheless
answered in substance — composition-sensitivity at fixed attenuation is real,
unanimous in sign, and monotone in state content, so the strict "fixed monotone
transform of card attenuation" reading is dead; (iii) if the planner wants a decision
rather than a tie, the next registration must either extend the target range downward
(a fourth pair at attenuation ≈ 0.45, where the margin will be breached) or lower the
materiality margin with a justification that is not K2b's swing scale — **and it must
make its adjudication space an actual partition**; (iv) the mixture channel carries
the same effect 4.3× larger and with the opposite sign, which is where a constructive
repair test would have the most signal to work with.

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
