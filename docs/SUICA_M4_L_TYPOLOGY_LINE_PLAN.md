# SUICA M4-L — The Typology Line (IDT-R: the reverse reading)

Line opened 2026-08-09 (evening) on the program owner's directive: study
the REVERSE direction — does removing identity make correct personality
GROUPING possible, and is the old "error = 0 ⇒ no identity" hypothesis
provable? Theory: `docs/SUICA_IDENTITY_THEORY_V1.md` appendix P (theorems
R1–R3, the geometry dichotomy, the completeness audit). Tier:
EXPLORATORY, label-free, synthetic, card-space. The claims ledger
controls. The defense phase charter stays shelved per the owner's
direction; this line takes precedence.

All standing rules 1–17 and conventions bind (round-trip parsing; 4-world
pilots with df-awareness; Part-0 verification of bit-identity claims;
chunked stages < 600 s; rule-16 full-object enumeration; rule-17
realizability with fallback ladders).

---

## M4-L1 — Instrument leg: a typed world, the identity tax on grouping, the dichotomy, and the completeness audit calibrated

**REGISTERED 2026-08-09, BEFORE RUN.** Planner: this document's author.
Executor: dispatched agent. This leg builds the TYPE layer, validates the
R-theorems' measurable shadows against Part-0 predictions, and calibrates
the completeness audit. It adjudicates instrument validity, not the
open taxometric question (that is L2+).

### Machinery

`scripts/run_suica_m4_l1_typed_world.py`, extending K2a's expressive
world IN THE LEG SCRIPT (suica_core untouched; rule-12 source naming).
Type layer added to the trait channel:

    mean_part_i = τ_{g(i)} + b_i

- g(i): G = 4 groups, equal sizes, assigned by seeded rng;
- τ_g: centroids in a k_τ = 3-dimensional random subspace S of the
  k = 48 latent space, pairwise separation set by knob Δ (realized
  separations reported);
- b_i (within-type identity), TWO GEOMETRIES per arm:
  **ISO** — isotropic in all 48 dims; **ALIGNED** — supported in S;
  identity share ρ_id := σ_b²/(σ_b² + σ_τ²) is the swept knob;
- occasion/state/noise channels as in K2a (φ_slow .90, n_occ 8,
  w_int 0), so cards and ρ_i come from the validated machinery.

Grouping instruments (pinned per rule 9/12, both computed everywhere):
PRIMARY = Lloyd's k-means on cards with known G, 64 seeded restarts,
best-objective; SECOND READING = spectral (top-k_τ PCA projection of
pooled cards, then k-means — the R2 "projection" operation). Agreement
metric: ARI against generator truth g (Hungarian-matched accuracy as
second reading).

### Arms (master_seed 20260822; 8 worlds × 512 authors per cell)

Grid: geometry ∈ {ISO, ALIGNED} × ρ_id ∈ {0, 0.15, 0.35, 0.55, 0.75}
at fixed Δ (chosen in Part 0 so the ISO ρ_id=0.35 cell sits mid-range,
rule-17 realizability: no cell saturated at ARI 0 or 1 in the pilot;
pre-declared adjustment ladder on Δ, one step, disclosed). Plus, on the
ISO and ALIGNED ρ_id=0.55 cells: an **oracle-removal companion**
(cards recomputed with b_i subtracted using generator truth — the upper
bound of the owner's conjecture) and an **oracle-projection companion**
(projection onto true S). 10 main cells + 4 companions.

### Part 0 gates

- **G0L (construction + anchors)** — reconstruction residual ≤ 1e-12;
  realized ρ_id and Δ within tolerance per cell; K2a anchor cell
  re-derived bit-exactly; per-cell ARI-relevant dims reported (rule 5).
- **G1L (rule 10)** — the type channel changes panels; ISO vs ALIGNED
  differ; b=0 arms differ from b>0 arms.
- **G2L (rule 3 + rule 17)** — liveness and realizability: pilot ARI in
  (0.05, 0.95) for the mid cells (else the Δ ladder fires, once,
  disclosed); type-subspace estimability check (top-k_τ eigengap > 0
  reported).
- **G3L (power, 4-world pilot)** — MDEs for every CI clause; rule-11
  satisfiability with directions; rule-13 spec (B=2000, seed=master,
  ≥10×B at boundaries).
- **G4L (Part-0 predictions)** — computed BEFORE arms from appendix P's
  R2 geometry: per-cell predicted ARI-degradation ordering in ρ_id;
  the ALIGNED error floor Φ(−Δ/(2σ_{b,u})) per boundary at each ρ_id;
  the ISO projection-gain factor; the audit's expected surviving-identity
  share per cell (= designed b-share through the validated T6″ machinery).
- **G5L (hygiene + rule 16)** — enumeration over the four leans' 2^4
  outcomes with the routing below; round-trip; chunked; rule-14
  self-check (all card-space, ARI-vs-ARI and share-vs-share; no
  cross-scale gate).

### Leans (aggregation: per-cell CIs vs Part-0 predictions, paired
world-block bootstrap B=2000; leans separate)

- **V-1 (designed sanity) [prior .85]** — ρ_id = 0 cells: PRIMARY
  grouping recovers g with ARI ≥ 0.95 in 8/8 worlds, both geometries
  (the world is groupable when the owner's 誤差=0 premise holds by
  construction).
- **V-2 (identity tax, R4) [prior .80]** — ISO cells: ARI strictly
  decreasing in ρ_id (ordering exact) AND per-cell ARI within CI of the
  Part-0 R2 prediction in ≥3/4 non-zero cells.
- **V-3 (the dichotomy, R2) [prior .75]** — at ρ_id ∈ {0.35, 0.55}:
  ALIGNED ARI < ISO ARI with pooled CI excluding 0; the ALIGNED cells'
  error consistent with the floor prediction (CI containment ≥1/2
  cells); oracle PROJECTION restores ISO ρ_id=0.55 by ≥ half its deficit
  to the ρ_id=0 level while restoring ALIGNED by ≤ a quarter of its
  deficit (the conjecture's validity boundary, measured); oracle REMOVAL
  restores BOTH to ARI ≥ 0.95 (upper bound sanity).
- **V-4 (completeness audit, R3) [prior .80]** — the T6″-based
  surviving-identity meter, applied to within-TRUE-group deviations:
  reads 0 within margin on ρ_id = 0 cells (designed null, margin from
  pilot) and tracks the designed b-share within CI in ≥6/8 non-zero
  cells (calibration of the audit as a measuring device).

### Routing (rule 16; precedence top-down)

1. V-1 MISS → **P1L: instrument defect or unrealizable grid** — STOP,
   report, no theory shadow claimed.
2. ≥2 of {V-2, V-3, V-4} MISS → **P2L: appendix P's measurable shadows
   fail** — the R-theorems keep their proofs but lose their claimed
   instrument shadows; theory-repair note before any L2.
3. Exactly 1 MISS → **P3L: QUALIFIED** — the missing piece named,
   follow-up charter; the other pieces stand as measured.
4. All HOLD → **P4L: instrument certified; R2/R3/R4's shadows MEASURED**
   — L2 (realizable removal ladder: split-half averaging / frame
   refreshment / label-free projection vs the oracle bounds; and the
   taxometric decision instrument on unknown-geometry worlds) becomes
   the next registration.

### Deliverables

The six: script; `results/m4_l1_typed_world/` (manifest.json,
gates.json, per-cell CSVs, decision.json — gitignored);
`reports/SUICA_M4_L1_TYPED_WORLD_REPORT.md` (Part 0 with predictions
first, timestamped before arms); outcome appended here; ledger row; ONE
commit (`feat(m4-l): L1 — ...`), never amended, not pushed by the agent.
Budget: card-space; target < 25 min wall; stop-and-report at 2× any
Part-0 stage estimate.
