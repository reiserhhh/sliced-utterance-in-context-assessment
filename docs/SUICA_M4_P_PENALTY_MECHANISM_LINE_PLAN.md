# SUICA M4-P — The Penalty-Mechanism Line

Line opened 2026-08-14, on the N-line's close. Question: **WHY does
the level price concentrate where cards read best?** The readability
penalty (appendix Z.1: the steep negative r-channel, λ identified,
sealed in scoped form by M2) has two named mechanisms that predict
OPPOSITE SIGNS under frame-side manipulation at fixed (share, φ):

- **H-SCAFFOLD** — the reader reads the person THROUGH the
  person×frame interaction (K-R1's scaffold corollary; K2b G4b: the
  b-only field's within-author occasion variation IS the frame).
  More common-frame content → more scaffold → b-only recovery RISES.
- **H-CONTAMINATION** — common-frame content is nuisance the
  deployed gauge AMPLIFIES (K1: +0.0925 at a 1× shift = 3.54× the
  F2 composition effect). More → recovery FALLS.

A sign is a cheap, decisive first cut. Tier: EXPLORATORY, label-free,
synthetic. The ledger controls. Registrations before run, append-only.
Standing rules 1–32 bind (K-line header; registry; D5; M-line 25–29;
N-line 30–32 — originating texts control); all conventions in force
(planner-run registration arithmetic incl. every gate-consumed
quantity; ladders checked against every gate sharing a knob; routing
tables verified disjoint-and-covering AND consequence-entailed;
domain-pinned predicates; executed provenance; estimator-noise
floors; two-sided bar reachability). Execution conventions as the
M/N lines (ONE commit per leg `feat(m4-p): ...`, never amended,
never pushed; chunked foreground stages < 600 s; `suica_core/`
READ-ONLY).

## Line charter

- **P1 — the frame-injection sign probe** (registered below).
- **P2 — the dose curve** (named; register only after P1 lands a
  sign): shift-size sweep, functional form, interaction with r.
- **P3 — the de-frame interplay** (named): does K1b/K1c′'s estimated
  de-framing invert or null the P1 sign, connecting the penalty to
  the certified-unadopted repair's deployment caution?

---

## M4-P1 — the frame-injection sign probe

**REGISTERED 2026-08-14, BEFORE RUN.** Planner: this document's
author; executor: dispatched agent (implementation and execution
only; this text is binding). No seal — the leans are split, so no
sealable point prediction exists; ordering is the standard
Part-0-before-worlds discipline.

### Facts cited to motivate leans (rule 8 — sources named; executor re-verifies at full precision)

- K1's common-shift finding: the deployed relation-field gauge
  amplifies common-frame content, +0.0925 at a 1× shift = 3.54× the
  F2 composition effect (`docs/SUICA_V8_IDT_INTEGRATION.md` §1;
  K1's plan-doc outcome controls).
- K1's calibration recipe: "pre-map occasion-level common
  perturbation δ(o) added to every author's response on occasion o;
  sizes … of the world's author-deviation RMS at the response level
  (calibration reported)" (`docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md`
  — K1 registration, Common-shift arms).
- K-R1's scaffold corollary and K2b G4b's frame-carried substrate
  (K-line plan, K-R1 outcome/adjudication).
- The unperturbed anchor: M2's C4 = (share 0.25, φ 0.05, n = 192)
  measured mean 0.12239759528671845
  (`results/m4_m2_scoped_seal/decision.json:per_cell.C4.mean`).

### Machinery (rules 9/12 — delegation with decision rule, K1 precedent)

K2b world family, K2F-FRESH carrier verbatim (int_share = 0), ONE
loader chain. NEW manipulation, transplanted from K1's recipe into
this family: a pre-map occasion-level common perturbation δ(o) added
to EVERY author's response on occasion o, drawn once per world per
occasion (seeded from the leg's lineage), scaled so its realized
response-level RMS equals s × (the world's author-deviation RMS at
the response level), s the arm's shift size; calibration persisted
per world. **The injection point is the LAST common per-occasion
object every author's response shares before the frozen map; the
executor identifies it with file:line in Part 0, and the choice rule
is this sentence** (rule 12; the K1 R-abs precedent pattern). The
frozen map and `suica_core/` are untouched — the perturbation lives
in world construction, upstream of the reader.

### Design

Arms: shift s ∈ {0, 0.5, 1.0} × base cells {(share 0.25, φ 0.05),
(share 0.25, φ 0.60)} = 6 arms × 192 worlds = 1152 fresh worlds.
Base cells sit in the high-r region where the penalty lives
(r = 0.785015540293945 / 0.7558507450373838, planner-computed,
interior); two φ levels give a within-leg replication. Salts
`m4p1-world` / `m4p1-pilot`, master_seed 20260814. Field statistic:
per-world `recovery_b_only`, as everywhere.

### Part 0 (all before any world)

- **G0p1 (bit-exact).** (i) The two base-cell r values above from
  the pinned maps; (ii) the cited K1/K-R1 sentences located and
  quoted verbatim from their controlling documents (rule 24); (iii)
  M2's C4 mean at full precision from its persisted source.
  Mismatch → STOP.
- **G1p1 (rule 10 non-degeneracy + rule 3 liveness, executed).** On
  pilot worlds: (a) the injection provably moves the pre-map object
  (norm delta > 0 at machine precision, reported); (b) the realized
  response-level RMS of δ matches its calibration target within 5%
  per world; (c) at s = 0 the pipeline is BIT-IDENTICAL to the
  unperturbed construction (the injection path proven inert at zero
  — no accidental contamination).
- **G2p1 (pilot).** 4 worlds × {0, 1.0} × both base cells on
  `m4p1-pilot` (16 worlds), rule-29 predicate
  (|recovery_b_only| ≥ 0.995 saturation, finiteness, nonzero
  variance; NO positivity clause).
- **G3p1 (rule 25 projection).** σ from the pilot's s = 0 worlds
  (df-inflated per the 4-world convention); the verdict quantity is
  the OLS slope b̂ of per-world recovery on s over {0, 0.5, 1.0}
  (world-level, 192/arm): SE(b̂) computed exactly for the design;
  declared minimum-interesting slope |b| = 0.01 per 1× shift (the
  within-share penalty's own magnitude scale, appendix Z.1
  arithmetic). Gate: MDE(2·SE) ≤ 0.01; once-only escalation to
  384/arm; still failing → NON_PROJECTABLE handback.
- **G4p1.** Routing below planner-verified disjoint-and-covering
  AND consequence-entailed (#46+#54 conventions); rule 24 generated
  tables; stage estimates: part0 90 s, pilot 40 s, worlds 6 chunks
  (1 arm each, ~120 s), fit 120 s, finalize 60 s; 2×
  stop-and-report.

### Verdicts (rule 22; equivalence per rule 4)

Per base cell: b̂ with world-bootstrap 95% CI (B = 2000; 20000 at
rule-13 boundaries). Classification: POSITIVE (CI > 0) / NEGATIVE
(CI < 0) / NULL (CI inside the ±0.01 equivalence margin) /
UNDERPOWERED (CI straddles 0 and exits the margin). A quadratic
coefficient in s is reported descriptively (no gate). Cross-cell
agreement is the second verdict.

### Leans (sides declared)

**L-1p1 [scaffold(+) .45 / contamination(−) .40 / null-or-split
.15].** Registered honestly split — this is a genuine fork: K-R1's
scaffold says the frame CARRIES the reading; K1's amplification says
the gauge DRINKS the frame. Either sign re-types the readability
penalty's owner.

### Routing (rule 16 — disjoint, covering, consequences entailed)

| # | condition | outcome |
|---|---|---|
| 1 | any G0p1/G1p1 failure | **STOP** (citation/instrument defect; no arms) |
| 2 | projection fails after escalation | **NON_PROJECTABLE** (handback) |
| 3 | both cells POSITIVE | **SIGN_SCAFFOLD** — the penalty's owner is frame-scaffolding; P2 doses it |
| 4 | both cells NEGATIVE | **SIGN_CONTAMINATION** — the gauge's amplification owns the penalty; P2 doses it; connects to K1's +0.0925 quantitatively |
| 5 | both cells NULL | **FRAME_INSENSITIVE** — neither named mechanism owns the penalty at this scale; a third mechanism is named, not invented |
| 6 | cells disagree in classification (any mix incl. UNDERPOWERED on one side) | **SPLIT_OR_UNDERPOWERED** — the φ-dependence or the power shortfall is named; P2's design inherits the diagnosis |

### Deliverables and budget

`scripts/run_suica_m4_p1_frame_injection.py`;
`results/m4_p1_frame_injection/` (gitignored);
`reports/SUICA_M4_P1_FRAME_INJECTION_REPORT.md` (generated tables);
outcome append HERE; one `docs/CLAIMS_LEDGER.md` row (EXPLORATORY);
exactly ONE commit `feat(m4-p): P1 — the frame-injection sign probe
— <SLUG>`, never amended, never pushed; suite green first. 1152
worlds (2304 at escalation) + 16 pilot; target < 30 min wall, every
stage < 600 s.

### M4-P1 outcome (appended after execution; registration above unedited)

**SIGN_SCAFFOLD — routing cell 3.** Both base cells POSITIVE and in
agreement (B1=POSITIVE, B2=POSITIVE; cross-cell agreement True).
**1152 fresh worlds** (192/arm × 6 arms). No seal — the
leans were registered honestly split, so no sealable point prediction existed.
Harness `scripts/run_suica_m4_p1_frame_injection.py`; report
`reports/SUICA_M4_P1_FRAME_INJECTION_REPORT.md`; artifacts
`results/m4_p1_frame_injection/` (gitignored).

**The sign is positive and it is not close.** b̂ = **0.3217400470171695**
[0.3125381894506993, 0.3316075999536289] at B1 (φ 0.05) and **0.34654236945734695** [0.3383230195793485, 0.3553320781635022] at B2
(φ 0.60) — 32× and 35× the declared minimum-interesting slope of
0.01, with both CIs far outside the ±0.01 equivalence margin.
**H-SCAFFOLD wins; H-CONTAMINATION is refuted at this scale in this family.**
More common-frame content makes b-only recovery RISE, steeply.

| cell | φ | s | n | mean | SEM | mean realized δ RMS |
|---|---|---|---|---|---|---|
| B1 | 0.05 | 0.0 | 192 | 0.11873302020953876 | 0.0017776895611196061 | 0.0 |
| B1 | 0.05 | 0.5 | 192 | 0.1794583899390327 | 0.0021742290750443875 | 0.03720787207513443 |
| B1 | 0.05 | 1.0 | 192 | 0.44047306722670826 | 0.0046458635448118155 | 0.07443049350172602 |
| B2 | 0.6 | 0.0 | 192 | 0.12904388025689947 | 0.001732157030280773 | 0.0 |
| B2 | 0.6 | 0.5 | 192 | 0.18906423691764004 | 0.0021547765918366528 | 0.03864141541522801 |
| B2 | 0.6 | 1.0 | 192 | 0.47558624971424646 | 0.004089574666712558 | 0.077341447932803 |

**The dose response is convex, not linear** (descriptive, no gate). Arm means
run 0.11873302020953876 → 0.1794583899390327 → 0.44047306722670826 at B1 and 0.12904388025689947 →
0.18906423691764004 → 0.47558624971424646 at B2: the half-dose moves recovery barely, the
full dose moves it enormously. Quadratic coefficients 0.40057861511636317 and
0.4530033122717317, both positive and both larger than the linear slope itself.
P2's dose-curve design should not assume linearity — the interesting structure
is between s = 0.5 and s = 1.0.

**The injection point, identified as the registration requires.** The object is
`world['common']` (4, 16, 64), built at `scripts/run_suica_m4_k2b_t4_branch.py:337`, returned at
`scripts/run_suica_m4_k2b_t4_branch.py:349`, and **last read before the frozen map at `scripts/run_suica_m4_k2b_t4_branch.py:377`**
— the `emit_panel` line that folds the common channel into every author's
response. That call is at `scripts/run_suica_m4_k2b_t4_branch.py:615`, one line before the map's entry at
`scripts/run_suica_m4_k2b_t4_branch.py:616`. Nothing between them is both common and per-occasion. δ(o) is
added to `common[c, o, :]` for EVERY context, so every author on occasion o
receives the identical response-level shift w["common"]·δ(o). `suica_core/` and
k2b were not edited: the harness perturbs the returned array between k2b's own
`build_k2b_world` and k2b's own `run_field_world`.

**G0p1 PASS.** Both base-cell r values bit-exact from the pinned maps
(0.785015540293945 / 0.7558507450373838); M2's C4 mean bit-exact at source; all 7
citation anchors located and quoted verbatim **by code** — each anchor
substring is found in its controlling document and the containing paragraph
lifted, so rule 24 covers the quotations as well as the tables.

**G1p1 PASS on all three clauses.** (a) The injection moves the pre-map object:
‖Δcommon‖_F ∈ [14.227782891799846, 14.883213260576998], every array bit-changed.
(b) Calibration lands to **1.8675090942348197e-16** relative error against a
0.05 band — the scale is solved in closed form and the realized RMS
recomputed from the scaled δ before persisting, so this tests an executed
number. (c) **s = 0 is BIT-IDENTICAL** to the unperturbed construction on
8 worlds (max |difference| 0.0): the injection
path is proven inert at zero.

**G3p1 PASS.** σ from the pilot's s = 0 worlds pooled within cell (df
6), df-inflated ×1.6498974741130894 on M1b's χ²(0.10) convention:
0.02686397191341203 → 0.04432279940458349. RN-P1-4 makes SE(b̂) exact for this design
(σ/√(n/2)), giving SE 0.004523676771373484 and **MDE(2·SE) = 0.009047353542746968 ≤
0.01**. Escalation to 384/arm did not fire (False).

**The unperturbed arm replicates M2's anchor.** P1's B1 s = 0 mean
0.11873302020953876 against M2's C4 0.12239759528671845 on the same base cell:
difference -0.0036645750771796964, z = -1.3707691436547715, within two pooled SEM
(True). Different salt, so a distributional replication, not a
bit-identity claim.

**Two findings about the shared machinery, both caught before any arm ran.**

1. **The corpus label is part of the frozen map's input (RN-P1-8).** k2b builds
   `corpus = f"m4k2b-{arm_id}-w{world_index}"` (k2b:613) and the map's output
   depends on it: the SAME world read under two different arm labels returns
   recovery_b_only 0.13207502282291814 vs 0.11984192209116917 — **0.0122 apart,
   larger than this leg's 0.01 bar**. Because `world_index` is also in the
   string this is exchangeable per-world noise rather than a per-arm offset, and
   it is already inside the σ the projection uses; but the arm tag was made
   s-INDEPENDENT (`P1-{cell}`) so the three s-arms share the identical corpus at
   matched world index and any corpus effect cancels exactly in b̂. World seeds
   still differ per arm, so the registered 1152 fresh worlds stand. **G1p1(c)
   failed on the first pilot for exactly this reason — the control had been
   given a different label — which is the gate doing its job on the harness.**
   Recorded for successors: any leg whose arm label varies with the manipulated
   factor should confirm the label is not confounded with the contrast.
2. **K1's own implementation defines the calibration, and it is not the obvious
   one (RN-P1-2).** The registration transplants K1's recipe, so K1's code
   controls (rules 9/12). `_author_deviation_rms`
   (`scripts/run_suica_m4_k1_issuer_theorems.py:337-361`) centres each response
   on its **(context, occasion)** cell mean, averages each author's deviations
   **over that author's occasions** to one vector per author, and takes the RMS
   over (author × dim). That is a much smaller quantity than a raw per-response
   deviation RMS and therefore sets a much smaller dose at the same s. It was
   transplanted literally; the two alternative readings are computed and
   persisted per world but never used to calibrate. One deliberate departure is
   disclosed as RN-P1-7: K1 SETS δ's per-component σ to s·rms, while this
   registration says the REALIZED RMS must EQUAL the target, so δ is rescaled
   exactly — the two agree to ~2% at 1024 draws and both clear G1p1(b), but the
   P1 text is the binding one.

**Rule events.** Rule 13: 0 boundary events — no B = 20000 re-run
(both CIs sit far from 0 and from the equivalence margin). Rule 26: no bounded
winner. Rule 29: in force as G2p1, held at every pilot arm and every full arm.
Rule 30: every constant verified against its persisted source before Part 0 and
every quoted sentence extracted by code. The slope identity b̂ = mean(s=1) −
mean(s=0) was verified against a full OLS witness on all 3n points at both
cells (True / True).

**Executor self-report.** Two standing anomalies, both resolved before any
hypothesis-relevant number existed: A-1 the dispatched interpreter is absent (a
pinned CPython 3.12.12 venv was built from the lockfile); A-2 `timeout(1)`
is absent on macOS (foreground stages under explicit sub-600 s timeouts).

**Registration-defect candidate (1).** The verdict classification is **not
disjoint**: POSITIVE (CI > 0) and NULL (CI inside ±0.01) overlap — a CI
like (0.001, 0.005) satisfies both. Rule 16 is met on the routing table but not
on the classification feeding it. Pinned before any number as RN-P1-5
(equivalence wins, per rule 4), with the sign-first ordering also computed; the
two agree at both cells here (True / True), so nothing
turned on it this time. Non-blocking.
