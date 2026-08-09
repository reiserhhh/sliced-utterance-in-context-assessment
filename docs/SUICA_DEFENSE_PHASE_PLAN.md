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
