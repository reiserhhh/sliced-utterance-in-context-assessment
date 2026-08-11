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

### Outcome (appended 2026-08-11 by the executing agent; append-only)

**`STOP_DESIGN_INFEASIBLE` — rule-16 cell 1 (a Part-0 gate fails after its
declared ladder; no fit is run).** Report:
`reports/SUICA_M4_M1_R_AT_LEVEL_REPORT.md`; harness
`scripts/run_suica_m4_m1_r_at_level.py`; artifacts `results/m4_m1_r_at_level/`.
**0 worlds were generated.** The leg stopped inside Part 0,
before the pilot, on this registration's own pre-declared fallback ladder.

**G0m PASSES completely — there is no citation defect.** Every anchor and every
K2f, D-open and theory-document number this registration quotes re-derives
bit-exactly: `predicted_attenuation(0.40, 0.90)`, `(0.45, 0.90)`,
`person_share_design(0.45, 0.0)` and `(0.40, 0.0)`; K2f F2's λ′, q′, κ′, p, its
LOO-RMSE at both persisted paths (`fits.json:L-1.best_loo_rmse` and
`loo.json:loo.F2.loo_rmse`) and both ci95s; D-open's M-4 level
0.09350089316336324 re-derived as the round-trip mean of its raw per-world
CSV; and `-0.9643543785903034` reproduced from `compiled_rows.csv` under Pearson,
which is what pins RN-M1-4's reading of "corr". The registration's facts are
accurate and its **mechanism is real**: φ does move `r` at exactly fixed `V`.

**G1m fails at gate (d), and the fallback ladder does not save it.** On the
registered base ladder `[0.6, 0.7, 0.8, 0.9, 0.98]`, gate (c) reached the
1.2 within-share `r` ratio in only **1** of 4 share
levels against a requirement of 2, and gate (d) measured
`corr(r, V) = -0.9407871367652862`. The pre-declared one-step extension to
`[0.45, 0.6, 0.75, 0.9, 0.98]` fired automatically inside Part 0 and did exactly its job on
(c) — **2**/4 levels, realized ratios
`[1.0525449708005403, 1.13540425278654, 1.2242247054603972, 1.3546050387988702]` — while (d) moved only to `-0.9107365249638539`,
**3.03578841654618× the 0.3 bar**. The failure is not an artifact
of the correlation convention: Spearman gives `-0.9306800811953776` and
`corr(r^q, V)` at the sealed response exponent gives `-0.9213071767159029`.
Gates (a), (b) and (e) pass (20 distinct design
points, `V` from 0.03000000000000001 to 0.18000000000000005, ratio 6.0).

**The bar is not merely missed — it is unreachable.** RN-M1-8's `diagnose` stage
(pure design arithmetic on the pinned deterministic maps; no world, no field, no
fit) searched the whole knob space. Over **every** 5-point distinct φ ladder in
(0.001, 0.999) at the registered shares, the infimum of `|corr(r, V)|` is
**`0.748768093111513` = 2.4958936437050436× the bar**, attained at the degenerate
ladder `[0.001, 0.011081, 0.021162, 0.988919, 0.999]` — the most extreme φ leverage this family can produce.
Freeing the shares as well, inside gate (a)'s envelope and subject to gate (b)'s
`V max/min ≥ 2.0`, the best of 4000 seeded draws
(474 rejected by (b)) is `0.5208187741410987` =
1.736062580470329× the bar. And the G2m liveness fallback ladder
`[0.9, 0.92, 0.94, 0.96, 0.98]`, had it ever been
reached, would have made (d) **worse** at
`-0.99515544292931` — every escape route
this registration wrote leads away from its own gate.

**Why, mechanically.** `V` is an EXACT linear function of share in this family
(`V/share = 0.3` at every share tested), and `r` is monotone
decreasing in share, so share drives `r` and `V` in lockstep. φ is the only knob
orthogonal to `V`, and its TOTAL leverage across the full open interval is
`0.05159009087311539` in `r` at share 0.1 rising to
`0.21722718146551878` at share 0.6 — against a
between-share `r` span of `0.2909602839380743` at fixed φ. Gate (b) REQUIRES a
share range wide enough that `V` varies by 2×, which is precisely what makes the
between-share `r` spread dominate; gate (d) requires the within-share φ-driven
spread to dominate instead. **In this world family both cannot hold at once.**
A second consequence, worth its own line: gate (c)'s 1.2 ratio is
reachable in only **2 of the 4 registered share
levels for any φ ladder whatsoever** (at shares `[0.1, 0.25]` the
full open φ interval tops out at ratios
1.06718684974016 and
1.1762868144261993), so "at least
2 share levels" was unknowingly demanding *all* the levels
that can ever comply.

**The defect (the planner owns it).** Rule-11 satisfiability, and rule-18 JOINT satisfiability across clauses sharing generative knobs: gate (b) and gate (d) share `share`, and the registration checked neither jointly nor arithmetically against the bar it wrote. The registration's own cited facts already contained the warning -- it quotes r(0.30, 0.90) = 0.6758917867864564 vs r(0.30, 0.98) = 0.645057248597175, a 4.78% move, and never asked what correlation a knob that small can buy against a share axis that moves r by 0.2910 at fixed phi.

**What was NOT run.** G2m's 16-world pilot, G3m(b)'s power projection (it needs
pilot σ_w), the 640 main worlds, and the fit — cell 1 reads
"no fit is run" and the ordering puts the pilot after the Part-0 gates. L-1,
L-2, L-3 and L-4 are all recorded **NOT EVALUATED**, with the reason in the
report's lean table. The four pre-declared forms, the start grid, the optimizer
pins, the bootstrap spec and every rule-22 side were nevertheless fixed in Part 0
before the stop and are persisted in `part0.json`, so a re-registration inherits
them unchanged rather than re-deriving them.

**Where the leverage would have to come from (a question for the planner, not an
executor's choice — nothing here is adopted).** As long as the only two knobs are
share and φ, `V` *is* share and the design has one effective axis plus a weak
second. Decollinearizing `r` from `V` at level needs either a knob that moves `r`
without moving share, or a `V` that is not a function of share alone.
`person_share_design(share, int_share)` sums the slow AND interaction shares, so
the `int_share` carrier — which M1 pinned to zero by inheriting K2F-FRESH
verbatim — moves `V` at fixed share. That is a second axis in exactly the place
the current design has none.

**Anomalies, with timing. No hypothesis-relevant number ever existed in this
leg** (0 worlds, no fit), so every anomaly below is
pre-hypothesis by construction. **A-1 (before any number of any kind):** the
dispatched environment did not exist — the only pandas on this machine belongs to
CPython 3.9.6, and the published machinery imports `datetime.UTC` (3.11+), so
`k2b`/`k2c`/`k2d`/`k2e` and the K2f harness all fail to import there; a CPython
3.12.12 venv was built outside the repo from `requirements-lock-main.txt`
verbatim (numpy `2.4.4`, pandas `3.0.2`, scipy `1.17.1` —
the lock's own pins) and the full suite was run green on it BEFORE any leg code
was written. **A-2 (before Part 0):** macOS ships no `timeout(1)`, so each stage
ran as its own foreground command under an explicit harness timeout. **A-3 (Part
0):** the rule-17 ladder fired — recorded because the firing is itself an event.
**A-4:** Part 0 ran more than once, every run before any world, deterministic and
identical each time; the ordering log was reset once so it carries the clean
final pass end to end. **A-5:** a first exploratory diagnostic called
`predicted_attenuation` inside an optimizer loop, overran its foreground timeout
and was killed; it was rewritten to precompute `r` on a fixed
100-point φ grid (2.072169780731201 s) and **no number from the
killed run appears anywhere in this leg**. **A-6 — rule 24 caught three of this
leg's own errors before commit:** the φ-leverage move at share 0.30 hand-typed as
"4.6%" where the anchors give `4.780124284524867`%; a leverage table whose headers
read "r at phi min/max" while the cells carry `r.min()`/`r.max()`, which are the
OPPOSITE φ endpoints since `r` decreases in φ; and a `V max/min ≥ 6.0` that
quoted the design's realized ratio where the gate's bar is
2.0. All three are now generated from artifacts.
**A-7:** no stage approached its 2× threshold — Part 0 `0.0369420051574707` s
against a 60 s estimate, `diagnose` `2.072169780731201` s against a 120 s
executor estimate.

**Line consequence.** M2 was registered as blocked only on
`NON_IDENTIFIED_UNDERPOWERED`; cell 1 is a different stop — nothing about the
level law was measured, so nothing about it was learned, and M2's charter is
untouched but unfed. M3 (the one-κ question) is independent of this leg and is
not blocked by it.

### Planner adjudication (2026-08-11, appended after the run) — THE STOP IS ACCEPTED; THE DEFECTS ARE MINE

**STOP_DESIGN_INFEASIBLE accepted as delivered.** The executor's conduct
was exemplary: G0m bit-exact on every quoted number (no citation
defect), ZERO worlds spent, the gate failure PROVEN unsatisfiable
rather than merely observed (infimum |corr(r, V)| over every 5-point φ
ladder at the registered shares = 0.748768093111513 = 2.496× the bar;
with shares freed under gate (b), best found 0.5208187741410987 — an
upper bound on that infimum, itself already 1.74× the bar), and rule 24
catching three of its own report cells pre-commit.

**Defect #43 (rule 11 violated in its letter).** G1m(d) was
deterministic arithmetic from pinned source objects — computable by the
planner at registration time with no pilot and no world. It was not
computed. The planner extrapolated φ's r-leverage from the two
published points (φ ∈ {0.90, 0.98}) into an unexercised region where
the attenuation map SATURATES: total φ leverage over the open interval
is 0.0516–0.2172 in r against a between-share span of 0.2910.

**Defect #44 (rule 18 violated).** Gates (b), (c), (d) share the
`share` knob and pull in opposite directions — (b) demands a wide share
range (V max/min ≥ 2), which is exactly what makes r track V; (d)
demands the within-share spread dominate. The joint check was not run;
the executor's diagnostic proves (b)+(d) jointly empty at ANY
admissible shares. Inside the same defect: gate (c)'s "≥ 2 of 4 share
levels" unknowingly named the only two levels that can EVER comply
(shares 0.10/0.25 top out at ratios 1.067/1.176 for any φ ladder).

**The deeper reading, and the rule it buys.** The failed bar sat on a
PROXY. Marginal corr(r, V) across cells is not what identification
needs: in a factorial, q is identified from within-share φ sweeps at
EXACTLY fixed V, and κ from between-share contrasts — the marginal
correlation can stay high while the conditional design information is
ample. The registration made the proxy a hard gate and left the
estimand-relevant object (the G3m-b projection) downstream of it, so
the leg died on a number the estimand does not consume. K2f's
follow-up phrase ("arms chosen to BREAK the r/V collinearity") seeded
the framing: "break the collinearity" was operationalized as "drive a
marginal correlation below a bar," where the operative content of
K2f's complaint was "restore identification" — K2f's collinearity
harmed it because that corpus ALSO had no within-stratum sweeps; the
factorial restores the sweeps, which is what suffices. **Rule 25
(enacted):** every design-feasibility gate is stated in the quantity
the leg's estimand requires (identification width, power, a registered
projection); marginal or proxy statistics of the design are REPORTED,
never gating. **Convention (planner-side):** when every input to a
registered gate is deterministic arithmetic from pinned source
objects, the planner RUNS the gate before committing the registration
and embeds the computed table in the registration text.

**Carried forward.** M1's Part-0 pins (four forms, optimizer, start
grid) inherit into M1b unchanged; the executor's leverage table is
M1b's design basis; leans and priors inherit UNCHANGED — zero worlds
ran, so no hypothesis-relevant information exists to update on.
Registry: #43, #44 and rule 25 appended by dated note. Appendix W is
untouched by this stop (it concerns the fit family, which never ran).

---

## M4-M1b — r-at-level, feasibility restated in the estimand's quantity

**REGISTERED 2026-08-11, BEFORE RUN.** Re-registration of M1 after its
cell-1 STOP. Planner: this document's author; executor: dispatched
agent (implementation and execution only; this text is binding).
Question, machinery, source objects, seeds policy, forms F1/F1e/F2/F3,
optimizer pins, start grid, LOO-cell selection, within-cell
world-block bootstrap (B = 2000; 20000 at rule-13 boundaries), tie
rule at 5%, leans L-1 [.55] / L-2 [below/overlap/above = .55/.35/.10,
conditional on L-1] / L-3 [.70] / L-4 (reading), and the rule-16 truth
table cells 2–6 with modifiers are INHERITED VERBATIM from M4-M1
above. Exactly the following changes.

### Design (pinned; planner arithmetic RUN at registration — rule 11 discharged, rule 25 compliant)

Grid: share ∈ {0.10, 0.25, 0.40, 0.60} × φ ∈ {0.05, 0.30, 0.60, 0.85,
0.98} = 20 cells × 32 worlds/cell. master_seed 20260811; salts
`m4m1b-world` / `m4m1b-pilot` (fresh streams; disjoint from M1's by
salt). φ at {0.05, 0.30, 0.60, 0.85} is a regime EXTENSION beyond the
exercised {0.90, 0.98} — guarded by G2m′, and the law claim stays
scoped to the tested grid.

Planner-computed design table (via the pinned maps, executor
reproduces bit-exactly in Part 0 — G0m′(vii)):

| share | V_person | r(φ=.05) | r(φ=.30) | r(φ=.60) | r(φ=.85) | r(φ=.98) | span |
|---|---|---|---|---|---|---|---|
| 0.10 | 0.03000000000000001 | 0.8189581462487876 | 0.8155586799827954 | 0.8075174172340943 | 0.7908869485651705 | 0.7718092954224756 | 0.04714885082631204 |
| 0.25 | 0.07500000000000002 | 0.785015540293945 | 0.7761302864207245 | 0.7558507450373838 | 0.7168731389294273 | 0.6763691758553391 | 0.10864636443860598 |
| 0.40 | 0.12000000000000004 | 0.7411873080384952 | 0.726425348215848 | 0.6941115392115328 | 0.6367206581308248 | 0.5825497814736654 | 0.15863752656482977 |
| 0.60 | 0.18000000000000005 | 0.6573448847694047 | 0.6346912945232521 | 0.5883719155687073 | 0.5151304058057474 | 0.4541409476972356 | 0.20320393707216905 |

Descriptives (REPORTED, never gating — rule 25): marginal corr(r, V) =
−0.8495063312353189; corr(r^1.8528700746510731, V) =
−0.8649603255864755; against K2f's −0.9643543785903034. The
identification content lives in the within-share sweeps (V exactly
fixed by design), not in the marginal correlation — that sentence is
the rule-25 exemplar.

Pre-declared ALT ladder (fires ONLY on G2m′'s regime guard): φ ∈
{0.30, 0.55, 0.75, 0.90, 0.98}; planner table: spans
0.04374938456031985 / 0.09976111056538539 / 0.1438755667421826 /
0.1805503468260165 by share; corr(r, V) = −0.8915685583022667;
corr(r^q, V) = −0.9029258027968385; also passes G1m′ below.

### Gates

- **G0m′ (anchors, bit-exact).** (i)–(vi) as M1's G0m verbatim (all
  passed in M1; re-verify); (vii) reproduce BOTH planner design tables
  above bit-exactly from `predicted_attenuation` /
  `person_share_design`; (viii) verify the M1-STOP numbers cited in
  the adjudication above against `results/m4_m1_r_at_level/`
  (stop_diagnostic.json and the report tables): infimum
  0.748768093111513, freed-shares bound 0.5208187741410987, per-share
  full-interval spans 0.05159009087311539 / 0.11784317303319514 /
  0.17083747134975158 / 0.21722718146551878. Any mismatch → STOP
  (citation defect, not silently repaired).
- **G1m′ (arithmetic; planner-verified at registration, executor
  re-runs).** (a) shares inside [0.02, 0.6634207990183637] — PASS. (b)
  V max/min ≥ 2 — realized 6.0, PASS. (c′) within-share r-span ≥ 0.12
  at BOTH shares {0.40, 0.60} — realized 0.15863752656482977 /
  0.20320393707216905 (ALT: 0.1438755667421826 / 0.1805503468260165),
  PASS. (e) 20/20 distinct design points — PASS. There is NO
  marginal-correlation gate (rule 25).
- **G2m′ (pilot; AFTER G0m′/G1m′, before any main world).** Corners
  {0.10, 0.60} × {0.05, 0.98} × 4 worlds on `m4m1b-pilot`. (i) REGIME
  guard: finite, non-saturated, nonzero within-corner variance;
  failure at a φ-extension corner → ALT ladder once (re-run G1m′ and
  G3m′(b)), then STOP_DESIGN_INFEASIBLE. (ii) φ→r channel liveness:
  PRIMARY object = a per-world realized card-attenuation statistic if
  the k2b machinery persists one (executor pins the source object
  file:line in Part 0 — rule 12; requirement: contrast between φ .05
  and .98 at share .60 exceeds 2× its pooled SE). If no such statistic
  exists, liveness is certified by the pinned map's arithmetic (Δr =
  0.20320393707216905 at share .60) PLUS the projection — an
  OUTCOME-side field contrast is NOT a liveness gate here, because a
  flat field is cell-2 EVIDENCE, not channel death; M1's registration
  conflated these and M1b does not (rule 25 applied twice).
- **G3m′.** (a) sides per rule 22 as in M1. (b) **the feasibility
  gate — the only one:** σ_w = pooled per-world sd across the 16 pilot
  worlds, inflated by sqrt(12 / χ²_{0.10, df=12}); parametric
  replication B_proj = 500, seed = master, at truths
  (λ = 0.18021628978547316, κ = 0.750086268225045, ε = 0) × q_truth ∈
  {1.0, 1.8528700746510731}, cell noise N(0, σ_w²/32), fitting F1
  with the full start grid; width proxy = quantile(q̂, .975) −
  quantile(q̂, .025); PASS iff proxy ≤ 0.50 under BOTH truths.
  Escalation (pre-declared, once): on fail, recompute at 64
  worlds/cell (noise /√2); pass → the main grid runs at 64 worlds/cell
  (budget ×2, declared); fail again → STOP as **NON_PROJECTABLE**,
  with the int_share second axis (V moves at fixed share;
  species-disclosed, K2d dispatcher required) NAMED for a future
  registration, not adopted here. No projection at q_truth = 0
  (pre-declared adjudicable branch, as in M1). (c) Stage estimates:
  part0 60 s, pilot 40 s, worlds 4 × 150 s (5 cells per chunk; ×2 at
  escalation), fit 300 s, finalize 60 s; the 2× stop-and-report
  convention applies.
- **G4m′.** As M1's G4m: the inherited truth table reproduced verbatim
  in the report with cell 1 now reading "any G0m′/G1m′/G2m′/G3m′
  clause fails after its declared ladder → STOP (planner defect)";
  rule 24 — every table carrying artifact numbers generated from
  artifacts.

### Deliverables and budget

The six deliverables: `scripts/run_suica_m4_m1b_r_at_level.py`;
`results/m4_m1b_r_at_level/` (gitignored);
`reports/SUICA_M4_M1B_R_AT_LEVEL_REPORT.md` (generated tables);
outcome appended HERE (append-only); one `docs/CLAIMS_LEDGER.md` row
(EXPLORATORY); exactly ONE commit
`feat(m4-m): M1b — r-at-level, estimand-gated — <SLUG>`, never
amended, never pushed. Suite green before commit. Budget: 640 worlds
(1280 at escalation) ≈ 0.6 s each plus fits — target < 30 min wall,
every stage < 600 s.
