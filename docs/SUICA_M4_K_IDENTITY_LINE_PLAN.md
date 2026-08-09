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

## M4-K3 — charter

The similarity-geometry package (T7/T8): caricature (α-scaling) vs rotation
(φ) dissociation; the anti-direction bound as a designed identity in card
space plus its violation rate in ESTIMATED cards as a pure noise function
(predictable from ρ); disattenuated distinctive cosine recovers
generator-true pattern similarity where raw deviation distance fails —
sign-predictable failures in the near-norm and unequal-norm regimes; angular
crowding (not distance crowding) drives misidentification; readability ρ_i
predicts per-person identification (the menagerie coordinate).
