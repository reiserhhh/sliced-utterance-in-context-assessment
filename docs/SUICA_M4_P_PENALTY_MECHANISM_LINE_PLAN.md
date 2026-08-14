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
