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
