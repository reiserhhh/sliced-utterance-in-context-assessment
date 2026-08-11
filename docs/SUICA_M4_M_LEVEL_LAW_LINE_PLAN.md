# SUICA M4-M — The Level-Law Completion Line

Line opened 2026-08-11. Question: **can the restored level law
(`field ≈ λ′ − κ′·V_person`, K2f, interpolation-grade) be completed —
its readability exponent identified on a decollinearized corpus, its
predictions sealed at extrapolated configurations, and its tax
coefficient tested for unity across grades?** This line executes K2f's
named follow-up ("a decollinearized corpus for the r-at-level question;
a D1-style seal for the new form") and appendix K's unification
candidate (the κ-invariant).

Tier: EXPLORATORY, label-free, synthetic throughout. The claims ledger
controls. Registrations are appended here BEFORE execution and never
edited after; outcomes are appended after adjudication. Route-index
entry at line synthesis.

## Standing rules (binding on every M-leg)

Rules 1–8 verbatim as in the K-line header
(`docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md:13-30`); rules 9–21 as
canonically tabled in `docs/SUICA_DEFECT_REGISTRY.md` ("The rule set
the defects bought"); rules 22–24 as enacted in the D5 adjudication
(`docs/SUICA_DEFENSE_PHASE_PLAN.md:667-672`): 22 — every band,
tolerance or bound declares its sides; 23 — clauses declare they can do
their job (gate stages named, feasibility argued); 24 — rule 8 extends
to published prose, and report tables carrying artifact numbers are
GENERATED from artifacts, never typed (K2f adjudication convention).
The registry and the originating adjudication texts control over this
shorthand. Unnumbered conventions in force
(`docs/SUICA_DEFECT_REGISTRY.md` "Conventions in force"): round-trip
parsing, df-aware pilots, Part-0 bit-identity verification, chunked
foreground stages, aggregation provenance, salt embedding,
legacy-anchor parser naming; plus the K2f machinery convention — ONE
importlib loader chain per leg (RN-K2F-5).

Execution conventions (binding on dispatched agents): no background
jobs, no monitors — foreground chunked stages with explicit timeouts,
every stage under 600 s; Part 0 gates written into the report BEFORE
any arm runs; bit-exact anchor reproduction from persisted artifacts
before new arms; every anomaly self-reported with an explicit statement
of whether it was resolved before or after any hypothesis-relevant
number existed; exactly ONE commit per leg (`feat(m4-m): ...`), never
amended, never pushed by the agent; `results/` is gitignored —
committed deliverables are the script, the report, the plan-doc outcome
append, and the ledger row. `suica_core/` is frozen and READ-ONLY.

## Line charter (three legs, registered sequentially)

- **M1 — r-at-level on a decollinearized factorial** (registered below).
  The φ knob moves predicted attenuation at EXACTLY fixed V_person
  (`person_share_design` has no φ argument), so a share × φ factorial
  breaks the −0.964 collinearity that made K2f's exponent
  unidentifiable. Was the level law's flatness in r real, or an
  artifact of a corpus that never varied φ below 0.90?
- **M2 — the extrapolation seal** (register ONLY after M1 adjudication;
  blocked if M1 lands NON_IDENTIFIED_UNDERPOWERED). D1-style salted
  prospective seal of the M1-winner's predictions at ≥3 configurations
  OUTSIDE the trained envelope (share above 0.6634207990183637 and/or φ
  outside M1's ladder, with at least one joint-exterior corner), bands
  pre-declared from M1's LOO-RMSE, opened measure-first. 3/3 inside →
  the level law is graded PREDICTIVE (extrapolation); partial → the
  boundary of validity is named.
- **M3 — the one-κ question** (register only after M2 adjudication).
  Is the variance-tax coefficient ONE instrument constant? κ has
  appeared at ~0.72–0.75 in three independent fitting routes plus the
  level refit; M3 measures κ at response grade and level grade across
  new geometries within the frozen instrument's domain, with any
  cross-scale comparison carrying a pinned link (rule 14) or re-designed
  within-instrument. Verdict: common band (an instrument constant, the
  appendix-K species) vs a measured geometry-dependence law.

Line stop conditions: any leg's STOP cell routes back to the planner as
a registration defect before any hypothesis-relevant number exists; the
line closes early if M1 lands R_TERM_ABSENT_AT_LEVEL and M2 seals the
tax-only form (M3 still runs — κ unity is grade-independent).

---

## M4-M1 — r-at-level on a decollinearized factorial

**REGISTERED 2026-08-11, BEFORE RUN.** Planner: this document's author.
Executor: dispatched agent (implementation and execution only; this
registration text is binding).

### Question

K2f restored the level law as an intercept minus the tax — and proved,
in the same breath, that this corpus cannot say whether the intercept
hides λ·r^q: corr(r, V) = −0.9643543785903034 across the 26 rows,
because the legacy legs exercised φ only at {0.90, 0.98} and moved r
almost entirely through share, which also moves V. M1 asks the question
K2f could not: **at level, with V held fixed by design, does the field
depend on readability — and with what exponent?**

### Design mechanism (why this decollinearizes — verified against artifacts 2026-08-11)

- `person_share_design(share, int_share)` has NO φ argument:
  V(0.40) = 0.12000000000000004, V(0.45) = 0.13500000000000004
  (persisted in `results/m4_k2f_level_law/part0.json:fresh_arm` and
  K2f's ANCHORS). φ therefore moves r at EXACTLY fixed V.
- φ's r-leverage is live in the published corpus:
  r(0.30, 0.90) = 0.6758917867864564 vs r(0.30, 0.98) =
  0.645057248597175; r(0.50, 0.90) = 0.558364277337817 vs
  r(0.50, 0.98) = 0.5193517935368367
  (`results/m4_k2f_level_law/compiled_rows.csv`, round-trip). Higher φ
  → lower r; the ladder below extends φ DOWNWARD to raise r at fixed V.
- Share moves V (and r): the trained share envelope is
  [0.02, 0.6634207990183637]; M1's shares sit strictly inside it.

### Facts cited to motivate leans (rule 8 — verified 2026-08-11 against persisted artifacts at full precision)

- K2f winner F2: λ′ = 0.18021628978547316, q′ = −0.009622064624441264,
  κ′ = 0.750086268225045, p = 0.2064406330042716, LOO-RMSE =
  0.0061559195350209; q′ ci95 [−0.3792124136721057, 0.5313115708778163];
  κ′ ci95 [0.5202855978239498, 0.8612166024267973]
  (`results/m4_k2f_level_law/fits.json`).
- Sealed response-grade constants (D1 bundle, opened in D-open):
  λ = 0.17417497661611914, q = 1.8528700746510731,
  κ_hat = −0.7220359963712748. The sealed composite under-predicted all
  26 compiled levels (residuals −0.1611..−0.0597) — evidence that the
  level r-dependence is WEAKER than r^1.85.
- Response-grade q band: **q = 1.83 [1.71, 1.98]**
  (`docs/SUICA_IDENTITY_THEORY_V1.md:805,841`); cross-leg spread
  1.83–1.93 (fragility annex) is a SECOND reading, not the primary band.
- D-open S-4 anchor: r(0.40, 0.90) = 0.6185853753498524,
  measured b-only level 0.09350089316336324 (K2f script ANCHORS,
  bit-exact against `results/dopen_seal_opening/stage1_m4.json`).

### Machinery (rules 9/12 — source objects pinned)

Instrument: K2b's world family and field reader, loaded through K2f's
loader pattern with ONE loader chain (RN-K2F-5). Source objects:
`run_suica_m4_k2b_t4_branch.py` — `build_k2b_world` / `run_field_world`
(985-author K1-pinned panel, F2 m-multiset, 4 contexts);
`run_suica_m4_k2c_matched_pairs.py:predicted_attenuation` (2-arg, →
k2b:533-583); `run_suica_m4_k2e_double_matching.py:person_share_design`.
Arm configuration inherits K2F-FRESH's carrier verbatim (int_share = 0,
same w_int_arm, same panel pins) except (share, φ). Field statistic:
per-world `recovery_b_only`; cell level = mean over worlds (the
`_level_from_raw` aggregation, K2f lineage). New script:
`scripts/run_suica_m4_m1_r_at_level.py`. Seeds: master_seed 20260811;
main worlds salt `m4m1-world`, hash-derived per (cell, world-index
0..31); pilot salt `m4m1-pilot`, indices 0..3 — disjoint streams by
salt. Round-trip parsing everywhere.

### Design (pinned)

Factorial grid: share ∈ {0.10, 0.25, 0.40, 0.60} × φ ∈ {0.60, 0.70,
0.80, 0.90, 0.98} = 20 cells × 32 worlds = 640 fresh worlds. Shares
strictly inside the trained envelope; φ at 0.60–0.80 is an EXTENSION
beyond the exercised {0.90, 0.98} — disclosed as such, guarded by the
pilot (finiteness, non-degeneracy, liveness), and the law claim stays
scoped to the tested grid.

### Part 0 (ALL written into the report before any world runs)

- **G0m (anchors, bit-exact).** (i) predicted_attenuation(0.40, 0.90)
  == 0.6185853753498524; (ii) predicted_attenuation(0.45, 0.90) ==
  0.5889058864943755 and person_share_design(0.45, 0.0) ==
  0.13500000000000004 (K2f part0 fresh_arm); (iii) person_share_design
  (0.40, 0.0) == 0.12000000000000004; (iv) reload
  `results/m4_k2f_level_law/fits.json` and verify EVERY K2f number
  quoted in this registration bit-exactly (F2 params, LOO, both ci95s)
  — a mismatch is a planner citation defect: STOP, report, do not
  repair silently; (v) re-derive Dopen:M-4's level 0.09350089316336324
  from its raw CSV round-trip; (vi) grep the theory doc and verify the
  quoted response band [1.71, 1.98] appears verbatim — mismatch: STOP
  (rule 24).
- **G1m (design arithmetic — no worlds needed).** Compute the realized
  20-point (r, V) table from the pinned deterministic maps and write it
  into the report. Gates: (a) all shares inside
  [0.02, 0.6634207990183637]; (b) V max/min ≥ 2, with V derived from
  `person_share_design`, never assumed linear; (c) within-share r
  max/min ≥ 1.20 in at least TWO share levels; (d) cross-cell
  |corr(r, V)| ≤ 0.30, with corr(r^1.8528700746510731, V) also
  reported (the headline decollinearization numbers, against K2f's
  −0.9643543785903034); (e) no duplicate (r, V) design points.
  Fallback ladder (rule 17, pre-declared, arithmetic only): if (c) or
  (d) fails, extend φ once to {0.45, 0.60, 0.75, 0.90, 0.98} and
  recheck; still failing → **STOP_DESIGN_INFEASIBLE** (planner
  registration defect).
- **G2m (pilot, rule 17 — AFTER G0m/G1m, before main arms).** 4 corner
  cells (share ∈ {0.10, 0.60} × φ ∈ {0.60, 0.98}) × 4 worlds on the
  pilot salt. Checks: (i) all per-world fields finite, non-saturated;
  (ii) **liveness (rule 3)**: at share 0.60, the realized attenuation
  contrast between φ = 0.60 and φ = 0.98 exceeds 2× its pooled SE —
  using the k2b-side realized card-attenuation statistic if one is
  persisted per world (executor pins the source object file:line in
  Part 0; rule 12), else the pilot field contrast at the same corner
  (declared fallback: a liveness check on the outcome, catastrophic
  deadness only). Liveness failure → drop φ extension, fall back to
  exercised-range ladder {0.90, 0.92, 0.94, 0.96, 0.98}, re-run G1m +
  G3m-b; failure there → STOP_DESIGN_INFEASIBLE.
- **G3m (satisfiability/power, rules 11/18/21/23).**
  (a) Sides for every clause (rule 22) written in Part 0.
  (b) **Projected identification power** (the rule-11 check made real):
  σ_w = pooled per-world sd across the 16 pilot worlds, inflated by the
  df-aware factor sqrt(12 / χ²_{0.10, df=12}); then a parametric
  replication (B_proj = 500, seed = master) of the 20-cell experiment
  at truths (λ = 0.18021628978547316, κ = 0.750086268225045, ε = 0)
  × q_truth ∈ {1.0, 1.8528700746510731}, cell noise
  N(0, σ_w²/32), fitting form F1 with the full start grid; width proxy
  = quantile(q̂, .975) − quantile(q̂, .025). Gate: proxy ≤ 0.50 under
  BOTH truths (stricter than L-1's 0.60 to absorb proxy slack,
  disclosed). No projection at q_truth = 0 — structural
  non-identification there is cell R_TERM_ABSENT's subject, not a
  power failure (stated per rule 20's spirit: that branch is
  pre-declared adjudicable, not empty).
  (c) Stage estimates: part0 60 s, pilot 30 s, worlds 4 × 120 s
  (5 cells per chunk), fit 300 s, finalize 60 s; the 2×
  stop-and-report threshold convention applies.
- **G4m (hygiene).** Rule-16 truth table written verbatim into the
  report (below); rule 24: every report table carrying artifact
  numbers is generated from artifacts.

### Fits (pinned)

Fit on the 20 cell means (world-level fitting is minimizer-identical at
equal cell n; noted, not run). FOUR pre-declared forms, no others:

- F1: field = λ·r^q − κ·V (K2f lineage);
- F1e: field = λ·r^q − κ·V − ε, ε bounded [0, 0.05] (T4's nonnegative
  species floor; 0.05 = 3.3× the fragile ≤0.015 band ceiling; the ONLY
  bounded form, stated); near q ≈ 0 its (λ, ε) ridge is singular —
  disclosed; LOO pays for it;
- F2: field = λ·r^q − κ·V·r^p (K2f lineage);
- F3: field = (λ − κ·V)·r^q (K2f lineage).

Optimizer: K2f's OPT verbatim (scipy least_squares, trf, 2-point jac,
ftol/xtol/gtol 1e-14, max_nfev 20000, unbounded except F1e's ε).
Start grid (pinned; K2f's grid extended by q ∈ {−0.5, 0.0} on K2f's
own finding): λ ∈ {0.05, 0.17417497661611914, 0.5}; q ∈ {−0.5, 0.0,
0.5, 1.0, 1.8528700746510731, 3.0}; κ ∈ {0.0, 0.7220359963712748,
2.0}; p ∈ {0.0, 1.0, 1.8528700746510731}; ε ∈ {0.0, 0.01, 0.03}.
Selection by leave-one-CELL-out RMSE (20 refits per form, full grid +
full-data optimum). Parameter CIs: within-cell world-block bootstrap —
each draw resamples 32 world indices with replacement INDEPENDENTLY
per cell, recomputes the 20 cell means, refits from the full-data
optimum start; B = 2000, seed = master; K2f discard rules
(non-convergence, |param| ≥ 1e6), counts disclosed. Cells are never
dropped (the design is fixed; the uncertainty is world sampling within
cells — stated against K2f's row-resample, which faced a different
object). Rule 13: any verdict within Monte-Carlo error of its boundary
re-runs at B = 20000 and scores BOUNDARY if unstable. Tie rule
(pre-declared): if the top two forms' LOO-RMSE differ by < 5% of the
winner's, every verdict must agree across both, else that verdict
reports SPLIT with both values.

### Leans (sides declared, rule 22)

- **L-1 [prior .55] IDENTIFIED:** the LOO winner's q 95% bootstrap CI
  width ≤ 0.60. One-sided (smaller is better).
- **L-2 [conditional on L-1; priors below/overlap/above =
  .55/.35/.10]:** the winner's q CI against the response band
  [1.71, 1.98] — three outcomes, all named: entirely below / overlap /
  entirely above. Two-sided; every outcome informative. Registered
  lean: BELOW (the sealed composite under-predicts all 26 levels; the
  level picture at controlled V is intercept-like; the response-grade
  q was fitted on a pooled curve sharing K2f's collinearity).
- **L-3 [prior .70] TAX STABILITY:** the winner's κ CI overlaps K2f
  F2's κ′ ci95 [0.5202855978239498, 0.8612166024267973]. Two-sided
  overlap; disjoint-low and disjoint-high both named.
- **L-4 (reading, NO gate): (r, V)-sufficiency probe.** Within each
  share level, Spearman(residual, φ) across the 5 φ cells, per share,
  under the winner's fit; a monotone same-sign pattern in ≥3/4 share
  levels is the named finding "φ leaks past (r, V)" — T4's
  form-sufficiency questioned; reported, adjudicating nothing.

### Routing (rules 15/16 — the truth table, every realizable combination to exactly one outcome)

| # | condition | outcome |
|---|---|---|
| 1 | any Part-0/pilot gate fails after its declared ladder | **STOP_DESIGN_INFEASIBLE** (planner defect; no fit is run) |
| 2 | L-1 MISS AND winner λ CI contains 0 | **R_TERM_ABSENT_AT_LEVEL** — the tax-only level law is the COMPLETE level story on this family; level–response dissociation named; q-at-level closes as structurally unposed; M2 proceeds on the tax-only form |
| 3 | L-1 MISS AND winner λ CI excludes 0 | **NON_IDENTIFIED_UNDERPOWERED** — CI reported, no q claim; M2 blocked; leverage redesign named |
| 4 | L-1 HOLD AND L-2 below | **LEVEL_RESPONSE_DISSOCIATION** — q measured at level, below the response band; new named phenomenon; M2 seals the measured law |
| 5 | L-1 HOLD AND L-2 overlap | **SINGLE_EXPONENT_RESTORED** — T4's level form completed with the response exponent; M2 seals |
| 6 | L-1 HOLD AND L-2 above | **ABOVE_BAND_ANOMALY** — named; M2 seals the measured law; theory note required |
| — | L-3 disjoint (either side), any cell 2–6 | modifier **TAX_SHIFT_AT_LEVEL** — pre-registered anomaly fed into M3's charter |
| — | L-3 overlap, any cell 2–6 | modifier: κ's fourth independent appearance is counted |

L-2/L-3 are evaluated only in cells 2–6's L-1 HOLD branches where they
are defined (L-2 needs an identified q; in cell 2 the q question is
unposed and L-2 is recorded N/A; L-3 is evaluated in every cell 2–6
since κ is identified even where q is not — in cell 3, L-3 is reported
descriptively, adjudicating nothing). This enumeration is the full
partition (rule 16); the executor reproduces it in the report verbatim.

### Deliverables and budget

The six deliverables as always: (1)
`scripts/run_suica_m4_m1_r_at_level.py`; (2) artifacts under
`results/m4_m1_r_at_level/` (gitignored); (3)
`reports/SUICA_M4_M1_R_AT_LEVEL_REPORT.md` (tables generated from
artifacts); (4) outcome appended to THIS section (append-only); (5) one
`docs/CLAIMS_LEDGER.md` row (EXPLORATORY); (6) exactly ONE commit
`feat(m4-m): M1 — r-at-level on a decollinearized factorial — <SLUG>`,
never amended, never pushed. Suite (`python -m pytest -q -p
no:cacheprovider`) green before commit. Budget: ~640 worlds ≈ 0.6 s
each plus fits — target < 25 min wall, every stage < 600 s.
