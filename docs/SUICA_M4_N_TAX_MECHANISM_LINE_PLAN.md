# SUICA M4-N — The Tax-Mechanism Line

Line opened 2026-08-11, on the M-line's close. Question: **WHY is the
tax a curve?** Appendix CC (planner derivation, committed before this
line runs) shows M3's A-quad is exactly a shifted square α(V) = c′ +
A0·(1 − V/V*)² — a square-agreement mechanism from a reader already
convicted of quadratic loss twice. On-support the square form is
observationally identical to A-quad; its real content is TRANSPORT:
matched-attenuation differences must read the LOCAL tax κ_resp(V̄) =
κ0 − κ2·V̄ exactly. This line tests transport first (N1), and only
then lets the mechanism grow.

Tier: EXPLORATORY, label-free, synthetic throughout. The claims
ledger controls. Registrations appended BEFORE execution, never
edited; outcomes appended after adjudication. Standing rules 1–29
bind (K-line header 1–8 verbatim; registry table 9–21; D5 22–24;
M-line adjudications 25–29 — the registry and originating texts
control); all M-line conventions in force (planner-run registration
arithmetic; disjoint-and-covering routing verified mechanically;
domain-pinned predicates; consumption budgets; representation
licensing). Execution conventions as the M-line header (ONE commit
per leg `feat(m4-n): ...`, never amended, never pushed by the agent;
chunked foreground stages < 600 s; `suica_core/` READ-ONLY).

## Line charter

- **N1 — the response-transport seal** (registered below): seal
  κ_resp(0.0525), κ_resp(0.1875) and their decline BEFORE any world;
  measure with fresh matched-attenuation pairs. 3/3 → the curve
  transports and CC's mechanism earns its next test; ≤1/3 → the
  curve is level-only and CC.1 dies as physics (CC.3's pre-registered
  honesty).
- **N2 — the frame-floor question** (named, register only after N1):
  is c′ = −0.0824 the frame-carried baseline? Interface with K2b's
  G4b trait-only floor; artifact forensics first.
- **N3 — the extrapolant question** (named): A-quad vs A-sat beyond
  V = 0.21 (divergence grows with V; generator caps V ≤ 0.3; regime
  risk to be argued before any registration).
- **N4 — the target-2 forensic** (named): why the 9-pair pipeline
  reads 0.715 where the law retrodicts 0.749 (artifact-space).

---

## M4-N1 — the response-transport seal

**REGISTERED 2026-08-11, BEFORE RUN.** Planner: this document's
author; executor: dispatched agent. The K2f Stage-2 ordering governs:
predictions computed in Part 0, HASHED (salt embedded in the sealed
bytes), THEN worlds — permit gate re-reads the stamp from disk; zero
pre-stamp generations; the pilot runs AFTER the stamp (RN-K2F-4).
Salts `m4n1-world` / `m4n1-pilot`, master_seed 20260811.

### Why differences test the curve exactly (the registered algebra)

Under the M-line's level structure, a difference at MATCHED r cancels
the channel λ·r^q and the constant exactly: D = α(V_hi) − α(V_lo) =
−ΔV·[κ0 − κ2·V̄] under A-quad, with NO approximation. So κ̂ = −D/ΔV
estimates the local tax at the pair's midpoint V̄ — response-grade
numbers the level fit never consumed.

### Design (pairs; planner arithmetic and bracketing run at registration — #43 convention)

Two matched-attenuation pairs, ΔV = 0.045 each (V = 0.3·share is
exact arithmetic):

- **pair-LO (V̄ = 0.0525):** cell A = (share 0.10, φ_a), cell B =
  (share 0.25, φ = 0.05), with φ_a solving r(0.10, φ_a) =
  r(0.25, 0.05) = 0.785015540293945. Existence by monotonicity + IVT:
  r(0.10, 0.85) = 0.7908869485651705 > target >
  r(0.10, 0.98) = 0.7718092954224756 → φ_a ∈ (0.85, 0.98).
- **pair-HI (V̄ = 0.1875):** cell C = (share 0.55, φ_c), cell D =
  (share 0.70, φ = 0.05), with φ_c solving r(0.55, φ_c) =
  r(0.70, 0.05) = 0.5967380569813433. Existence: r(0.55, 0.60) ≈
  0.617 (between the computed 0.6453873930804982 at share 0.50 and
  0.5883719155687073 at share 0.60) > target > r(0.55, 0.98) ≈ 0.487
  (same bracketing) → φ_c ∈ (0.60, 0.98).

Executor solves both roots in Part 0 by bisection on the pinned
deterministic map to |Δr| ≤ 1e-9 (channel-cancellation bias bound
|λ·q·r^{q−1}|·1e-9 < 1e-9, disclosed); all four realized r are
INTERIOR to [0.4541409476972356, 0.8189581462487876] by construction
(equal to interior targets). 384 worlds per cell × 4 cells = 1536
worlds; measurement SE per κ̂ ≈ √2·σ_w/(√384·0.045) ≈ 0.0432
(σ_w = 0.026889438327132725, pinned, G0-verified).

### The sealed predictions (Part 0 → hash → worlds)

The predictor: M3's full pipeline recomputed deterministically from
persisted per-world data (pinned seed; G0 verifies the point
parameters bit-exactly), each bootstrap draw of (c, κ0, κ2)
propagated:

- **S1:** κ̂_LO vs κ(0.0525) = κ0 − κ2·0.0525 (planner sanity
  0.8781). Band = [draw 2.5% − 2·SE_meas, draw 97.5% + 2·SE_meas].
- **S2:** κ̂_HI vs κ(0.1875) (planner sanity 0.6671). Same band
  construction.
- **S3:** Δκ̂ = κ̂_LO − κ̂_HI vs κ2·0.135 (planner sanity 0.2110);
  band from the joint draws ⊕ 2·SE_diff.
- A-sat's co-predictions for all three are written INSIDE the hashed
  file (tie handling, K2f precedent); they adjudicate nothing unless
  the A-quad/A-sat distinction becomes outcome-relevant, in which
  case SPLIT is reported.

### Leans (sides declared; all containments two-sided)

- **L-1n1 [.60]:** S1 inside. **L-2n1 [.60]:** S2 inside.
- **L-3n1 [.55]:** S3 inside AND Δκ̂ > 0 — the decline replicated in
  response space; the constant-tax alternative predicts Δ = 0.

### Gates

- **G0n1 (bit-exact).** (i) The pair table and bracketing above
  reproduced from the pinned maps; roots solved to tolerance; V̄
  exact. (ii) Every M3 number quoted here and in appendix CC
  verified at full precision against `results/m4_m3_tax_curve/`
  (curve params + CIs, LOO table, closure table, projection powers);
  CC's identities (V* = 0.6143507762088093, A0 =
  0.29489267237567145, c′ = −0.08241868972288329) recomputed from
  the persisted parameters. (iii) σ_w at source. Mismatch → STOP.
- **G1n1 (rule 29).** Regime predicate: |per-world recovery_b_only|
  ≥ 0.995 saturation; finiteness; nonzero within-cell variance. NO
  positivity clause.
- **G2n1 (rule 25 projection, BEFORE the stamp; no new data).**
  Parametric replication (B_proj = 2000, seed = master) at truths
  CURVE (M3 central: κ0 = 0.9601680204204508, κ2 =
  1.562877770472943) and CONSTANT (κ = the A-lin chord
  0.7729284648259515 — executor recomputes exactly from M3's A-lin
  fit; if its persisted value differs, the persisted value
  controls): PASS iff P(Δκ̂ > 2·SE_diff | CURVE) ≥ 0.8 AND
  P(Δκ̂ > 2·SE_diff | CONSTANT) ≤ 0.1 at 384/side; once-only
  escalation to 768/side (3072 worlds, budget ×2, declared); fail →
  **NON_PROJECTABLE** handback.
- **G3n1 (rule 27 budgets, before the stamp).** Sealed band total
  widths: S1 ≤ 0.30, S2 ≤ 0.30, S3 ≤ 0.35 — over-budget →
  **VOID_FOR_WIDTH** (excluded from the count; if fewer than 3
  remain, cell 4 is unreachable).
- **G4n1 (ordering + pilot).** K2f G1f enforcement (permit only by
  re-hash from disk; ordering log persisted). Pilot AFTER stamp: 4
  worlds each at cells A and D (`m4n1-pilot`), G1n1 predicate only;
  regime failure → **UNRESOLVED_SEAL** (predictions stand
  unmeasured; RN-K2F-4's accepted cost).
- **G5n1.** Stages: part0 360 s (M3 recompute + projection + stamp),
  pilot 30 s, worlds 4 chunks × 1 cell (~230 s each; ×2 at
  escalation), measure 120 s, finalize 60 s; 2× stop-and-report;
  routing below planner-verified disjoint-and-covering; rule 24
  generated tables.

### Routing (rule 16 — disjoint and covering)

| # | condition | outcome |
|---|---|---|
| 1 | any G0n1 mismatch | **STOP** (citation defect) |
| 2 | projection fails after escalation | **NON_PROJECTABLE** (handback; no worlds) |
| 3 | pilot regime failure | **UNRESOLVED_SEAL** (predictions on record, unmeasured) |
| 4 | 3 valid predictions AND 3/3 inside (S3 also requiring Δκ̂ > 0) | **CURVE_TRANSPORTS_TO_RESPONSE** — the mechanism survives its first test; the sealed 0.722 difference-fit acquires its secant reading; N2 becomes registrable |
| 5 | exactly 2 of the valid predictions inside | **PARTIAL_TRANSPORT** — the miss names the break (level-vs-response or magnitude); theory note required |
| 6 | ≤ 1 inside | **NO_TRANSPORT** — the curve is level-only; CC.1 dies as physics (CC.3); the line closes early |
| — | any prediction VOID_FOR_WIDTH | modifier **VOID_FOR_WIDTH(n)**; with < 3 valid, cell 4 unreachable and the best available is cell 5's grade |
| — | A-quad/A-sat co-predictions disagree on any verdict | modifier **FORM_SPLIT** (reported; adjudicates per the tie rule) |

### Deliverables and budget

`scripts/run_suica_m4_n1_response_transport.py`;
`results/m4_n1_response_transport/` (gitignored);
`reports/SUICA_M4_N1_RESPONSE_TRANSPORT_REPORT.md` (generated
tables); outcome append HERE; one `docs/CLAIMS_LEDGER.md` row
(EXPLORATORY); exactly ONE commit `feat(m4-n): N1 — the
response-transport seal — <SLUG>`, never amended, never pushed;
suite green first. 1536 worlds (3072 at escalation) + 8 pilot;
target < 30 min wall, every stage < 600 s.
