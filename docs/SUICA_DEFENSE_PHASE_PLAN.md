# SUICA Defense Phase — Plan (registrations and outcomes)

Phase opened per the charter (`docs/SUICA_DEFENSE_PHASE_CHARTER.md`);
resumed 2026-08-10 after the M4-L line closed. All standing rules 1–21
and conventions bind. Defense legs license no new theory claims; they
strengthen, qualify, or kill existing ones.

---

## D1 — Prospective seal #2: the measured laws must predict, not describe

**REGISTERED 2026-08-10, BEFORE RUN.** Planner: this document's author.
Executor: dispatched agent. The cheapest, highest-leverage defense: the
program's laws (K-line and L-line) are sealed as QUANTITATIVE
predictions for configurations NOBODY HAS RUN, before anyone runs them.
A future opening leg runs the configurations FIRST, then unseals.

### Protocol authority

OP-31 ("prospective seal #1, the time lockbox") is the precedent. The
executor LOCATES its protocol and artifacts (search docs/, scripts/,
results/ for lockbox/seal/OP-31 naming), follows its sealing mechanics
(salted hash; where salt and plaintext live; what is committed), and
cites them. If OP-31's protocol is unlocatable or incompatible, the
fallback is pre-declared: salted SHA-256; the sealed plaintext bundle
under `results/d1_sealed/` (gitignored) with a copy instruction for the
owner in the report; ONLY the hash, the salt-handling statement, and
the opening protocol are committed. The deviation is disclosed.

### The registered prediction set (computed from PUBLISHED constants and formulas ONLY)

- **S-1 (η-floor curve, new config):** m=96, k_τ=4, G=5, n_occ=8,
  identity energy at the ρ.55-equivalent; η ∈ {0, 0.5, 1}: predicted
  per-boundary error rates from σ_u²(η) = η·σ_b²/k_τ + (1−η)·σ_b²/m
  (appendix R.1's law).
- **S-2 (tax ratio, new config):** the boundary z-ratio √(m/k_τ) =
  √24 at that config, with the predicted ARI-drop direction.
- **S-3 (window-width conjecture, first quantitative seal):** the
  localization-window widths at two (d/n) settings — (48, 512) [known
  empty] and (192, 256) [conjectured open] — from the L2 energy
  criterion plus the (d/n)^¼ scaling; sealed as interval predictions.
- **S-4 (K-line variance-tax law):** predicted b-only field recovery
  at a NEW state arm (share .40, φ .90) on the K2b instrument, from
  field ≈ λ·r^q − κ·V_person with the published λ = 0.17417497661611914,
  q = 1.8528700746510731, κ = 0.7220359963712748 and the validated
  attenuation algebra.
- **S-5 (taxometer):** predicted η̂ reading ± its certified budget at a
  new η = 0.6, ρ.45-equivalent cell.

Each entry is sealed with: the formula, the constants' provenance
(file + field), the computed value(s), and a falsification band (the
prediction's own registered tolerance, rule-19 compliant: each band on
the law's OWN quantity).

### Gates

- **G0D (provenance)** — every constant re-derived bit-exactly from
  persisted decision.json/gates.json files (round-trip parsing), cited
  by path and field.
- **G1D (purity, rule-3 analogue)** — THIS LEG GENERATES NO WORLD of
  any kind. Prediction arithmetic only. Any world generation is a
  defect → STOP. (The point of a prospective seal is that the sealed
  values were computable without touching the target configurations.)
- **G2D (seal integrity)** — the committed hash re-verifies against
  the sealed bundle; the bundle contains the full prediction table,
  the salt-handling statement, and the opening protocol.
- **G3D (rule 16, trivial)** — outcomes: SEAL-COMPLETE (all five
  entries computed, sealed, hash committed) / SEAL-PARTIAL (any entry
  uncomputable from published constants — named, sealed without it) /
  SEAL-FAIL (protocol failure). One of three, enumerated.

### Opening protocol (registered now, binding later)

The seal opens ONLY in a future registered leg (D-open) that: (1) runs
the five configurations FRESH, adjudicating against the sealed bands
BEFORE unsealing; (2) then unseals and verifies the hash; (3) scores
each entry PREDICTED/MISSED with no re-fitting. Trigger: the program
owner's request, or the defense phase reaching D4, whichever first.

### Deliverables

The six: `scripts/run_suica_d1_prospective_seal.py`; the sealed bundle
per protocol; `reports/SUICA_D1_PROSPECTIVE_SEAL_REPORT.md` (protocol
citation, provenance table, the HASH, the opening protocol — never the
plaintext values); outcome appended here; ledger row; ONE commit
(`feat(defense): D1 — ...`), never amended, not pushed by the agent.
Budget: arithmetic only; target < 10 min wall.

### OUTCOME (appended 2026-08-10, after run) — `SEAL-COMPLETE`

**All five entries sealed. Zero world generations. 0.875 s wall.**

- **sha256 (salted)** = `3a1971b827210b7f3611b4769496f9d55d4ea815b6b8b577cae81f64b1fe00f8`
- report: `reports/SUICA_D1_PROSPECTIVE_SEAL_REPORT.md`; script:
  `scripts/run_suica_d1_prospective_seal.py`; bundle:
  `results/d1_sealed/D1_SEALED_BUNDLE.json` (gitignored; the report carries
  the owner's copy instruction).

**Protocol.** OP-31 was located (`docs/OP31_PROSPECTIVE_SEAL.md`;
`scripts/run_suica_op31_prospective_seal_v1.py`). Its HASH MECHANIC was
adopted verbatim (op31:64-65, canonical `sort_keys` JSON SHA-256). Its
CONCEALMENT MODEL is incompatible — OP-31 could commit plaintext because its
target text did not yet exist, whereas D1's five configurations are runnable
today — so the registration's pre-declared fallback supplies the storage
model (salted hash, gitignored bundle, hash-only commit). Deviation disclosed
in the report's Part 0.1.

**G0D.** All 14 constants round-trip bit-exactly (residual `0.0` on every
row), plus a six-row source-object drift check and a FORMULA round-trip: the
three K2c pair arms re-derived through the very functions S-4 calls
(`predicted_attenuation`, `person_share_design`) reproduce K2c/K2d's
persisted `r` and `V_person` bit-exactly. Two provenance corrections to this
registration's own text, disclosed not silently followed: (i) κ is NOT in
`results/m4_k2d_frontier_carrier/decision.json` — it lives in the sibling
`post_hoc_descriptive.json` under `kappa_ols_through_origin`, re-derived
bit-exactly by K2e; (ii) every persisted κ field is NEGATIVE where this
registration writes it positive, which is the same arithmetic under the
law's own minus sign.

**G1D PASS, enforced in code.** Fifteen world/panel/card generators replaced
by raising stubs before any entry was computed; **0** fired. RNG calls
attributed by IMMEDIATE calling frame: exactly **one** SUICA-attributed call
in the whole run (`suica_core/v8_realtext_relation_field.py:198`,
`frozen_random_directions`, the FROZEN GAUGE DIRECTIONS reached through
`k2b.layout()` while S-4 asks for `r` — a frozen operator constant,
independent of `share` and `phi`, not a world), disclosed as purity note
D1-PN-1; 46 third-party `scipy.stats` import-time calls counted and
excluded. A G2D sub-gate additionally searches the committed report for every
one of the 49 prediction-bearing numeric leaves: **0 leaks**, with two
published L2 window edges whitelisted and their unavoidable overlap
disclosed in Part 0.2.

**G2D PASS.** The bundle was re-read from disk and re-hashed after writing;
the recomputed hash equals the committed one. The bundle carries the full
five-entry prediction table, the salt-handling statement and the opening
protocol. `--verify` re-runs this check standalone.

**Five rule-9 pins worth the planner's attention** (all written to Part 0
BEFORE the seal): **RN-D1-3** S-1 seals the LATENT floor, not
`l2.predicted_boundary_error_l2` — the card-space realization needs a world's
loadings, so calling it would have violated G1D; l2:391-393 certifies the two
coincide when M is an isometry. **RN-D1-4** for a regular simplex `G` changes
the boundary COUNT (`C(5,2)=10`) not the per-boundary RATE, and `n_occ` does
not enter the identity-only floor at all; the registered config is internally
consistent (`k_tau = G-1`). **RN-D1-1/2** "ρ.55-equivalent" is read as L2's
term of art (a fixed number transported unchanged), with the Δ-free
`rho_id=0.55` form at G=5's own simplex constant sealed as a NAMED COMPANION
that cannot be promoted at opening time. **RN-D1-5** S-3's `d` is pinned to
the LATENT dimension `m` (k2a:89), not `DIM=64` — which makes the
registration's "known empty" label at `(48, 512)` true by L2's own
measurement rather than by extrapolation. **RN-D1-6/7/8** every band constant
is DERIVED from a persisted record (L2's ten-cell W-3 containment record; the
9-pair κ residual record; L3 X-2's certified `±0.125`); the only free choices
are two safety factors and the S-3 multiplier, all fixed before any value
existed.

**Note for D-open.** S-3 is the one entry whose miss is cheap: it is
CONJECTURE-GRADE and its failure kills the `(d/n)^(1/4)` window conjecture
only. S-1/S-2/S-4/S-5 misses fall on the measured laws. S-2 in particular is
exact algebra with no numeric freedom — a miss there would mean the
boundary-z derivation itself is wrong.

### Planner adjudication (2026-08-10, appended after the run)

**SEAL-COMPLETE accepted.** The hash mechanic is OP-31's verbatim; the
concealment deviation was pre-declared and is correct (D1's targets are
runnable today, OP-31's were not). G1D's purity was ENFORCED, not
asserted (15 generators stubbed, 0 fired; the single SUICA-attributed
RNG call is the frozen gauge-direction constant, disclosed as D1-PN-1
and correctly judged not-a-world). **Planner defect #39 (rule-8 family,
recorded):** my registration cited κ at the wrong path AND with the
wrong sign convention; the executor corrected with disclosure and
re-derived bit-exactly from the true sources. Noted for the record:
OP-31's own results-bundle is absent on this machine — its seal of
record is the tracked doc + script constant.

**OWNER ACTION REQUIRED (surfaced in the session report):** the sealed
plaintext bundle exists ONLY at
`results/d1_sealed/D1_SEALED_BUNDLE.json` on this machine (gitignored,
mode 0600). It must be copied off-machine; a lost bundle voids the
seal. The committed hash proves nothing without it.

---

## D2 — Adversarial verification pass over the program's headline table

**REGISTERED 2026-08-10, BEFORE RUN.** Planner: this document's author.
Executor: dispatched agent, INDEPENDENT of every original executor and
tasked to REFUTE, not to confirm. Artifact-space only — a G1D-style
purity gate binds (no world generation; verification by re-derivation
and cross-document consistency only).

### The claim table (10 rows, verbatim targets)

- **C1** K1-L1: shared-design cancellation exact — 0 flips / 31,520,
  card-difference invariance ≤ 4.2e-16.
- **C2** K1-L2/L3: issuer price +0.09695431472081219 pooled with 8/8
  signs; 1/|P| slope −1.0865327686128703 ⊂ [−1.35, −0.65].
- **C3** K1-L5: deployed-gauge amplification +0.092543049 at 1× =
  3.54× F2's composition effect (+0.026163263306726227).
- **C4** K1b/K1c′: author-reading share −0.949 [−1.158, −0.753] at
  κ=1.0 and −0.9443843417103447 [−1.2340, −0.7046] at κ=0.5.
- **C5** K1d: γ_deleted = 1.2446190431788744 [1.1185, 1.3579]
  overlapping F4's band; half-agreement budget 48.865× → 19.878×.
- **C6** T4 composite constants: λ = 0.17417497661611914,
  q = 1.8528700746510731 [1.7147, 1.9996], κ = −0.7220359963712748
  (R² 0.9935185860651237); K2e DM collapse 67.04–78.83%.
- **C7** K3: anti-direction bound 0 violations / 3,139,584; binds at
  50.48%; rotation cos-law max error ≤ 0.0035.
- **C8** L-line floor law: three independent confirmations (L1 poles,
  L2 curve 7/10 + exact ordering, L3 fresh-seed reproduction).
- **C9** L3 taxometer: |η̂ − η| ≤ 0.125 in 10/10 with median 0.0241;
  ordering Spearman 1.0 under every reading.
- **C10** K-R1: de-framing harms — all six arms DOWN, 0/32 worlds
  positive anywhere; λ 0.1821 → 0.0008.

### Method (per claim)

Re-derive every cited number from persisted artifacts at full precision
(round-trip parsing; raw per-cell files preferred over summaries);
attempt refutation: recomputation where formulas are published,
cross-document consistency (decision/gates vs report vs plan-doc vs
ledger vs IDT appendices), unit and sign checks, CI-endpoint
recomputation from persisted draws where present. Verdict per claim ∈
{CONFIRMED, QUALIFIED (named discrepancy at or below display
precision), REFUTED (a cited number is wrong at full precision, with
the true value), UNVERIFIABLE (artifact gap — name the missing file)}.
Enumerated; no other cell.

### Routing (rule 16)

- Any REFUTED → **P1V:** the planner writes a dated correction and
  claim-strength downgrade for that row (the program's retrospective
  mechanism); remaining rows still reported.
- Any UNVERIFIABLE → **P2V:** the missing artifacts feed D3's lockbox
  specification (that is D3's charter input).
- All CONFIRMED/QUALIFIED → **P3V:** the headline table gains a
  D2-verified stamp (dated note in IDT and both syntheses).

### Deliverables

The six: `scripts/run_suica_d2_adversarial_verification.py` (the
re-derivation harness); `results/d2_verification/` (per-claim
worksheets — gitignored); `reports/SUICA_D2_ADVERSARIAL_VERIFICATION_REPORT.md`
(per-claim verdicts with evidence); outcome appended here; ledger row;
ONE commit (`feat(defense): D2 — ...`), never amended, not pushed by
the agent. Budget: artifact-space; target < 30 min wall.
