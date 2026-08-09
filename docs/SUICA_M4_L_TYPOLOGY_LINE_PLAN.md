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

---

## L2 charter + planner derivation (dated append, 2026-08-10 — BEFORE L1
adjudication; the L2 registration follows L1 per L1's routing)

L1's arms are the pure poles (ISO / ALIGNED). Real worlds live on the
continuum between them. This iteration's planner question, solved by
derivation while L1 runs: **what are the laws on the η-continuum, and
what can be done LABEL-FREE?** Let the identity decompose as
b = √(1−η)·b_iso + √η·b_aligned (η = the aligned fraction of identity
energy; b_aligned isotropic WITHIN S).

**Derivation 1 (the interpolated projection gain).** Distance-based
grouping suffers the identity energy retained in the working space.
Raw space: E_raw = σ_b². After projection onto S (dim k_τ of m):
E_proj = η·σ_b² + (1−η)·σ_b²·(k_τ/m). Hence the projection gain

    G(η) = E_raw / E_proj = 1 / (η + (1−η)·k_τ/m)

— at η = 0 it is m/k_τ (L1's ISO prediction, = 16 at 48/3); at η = 1 it
is exactly 1 (no gain, the ALIGNED pole). One-parameter law, registered
as L2's quantitative prediction curve.

**Derivation 2 (the floor generalizes).** Along a boundary normal
u ∈ S, post-projection identity sd is
σ_u²(η) = η·σ_b²/k_τ + (1−η)·σ_b²/m, so the irreducible error floor per
boundary is ≈ Φ(−Δ/(2σ_u(η))) — continuous in η, reducing to L1's
ALIGNED floor at η = 1 and to a negligible floor at η = 0. Consequence
worth stating plainly: **the owner's conjecture degrades GRACEFULLY —
identity removal by projection buys G(η), never less than 1, and the
un-buyable remainder is exactly the aligned fraction.**

**Derivation 3 (label-free estimability of η — the spectral taxometer).**
The pooled card covariance separates the poles by WHERE identity energy
sits: ISO identity raises the BULK (all m dims, +(1−η)σ_b²/m per dim);
ALIGNED identity feeds the same k_τ SPIKES as the types. Since the
per-card noise variance is independently estimable from split-half
disagreement (the K2a-validated machinery), the bulk excess over noise
identifies (1−η)σ_b², label-free. The aligned share then needs one more
number (total σ_b²), obtainable within-group AFTER provisional grouping
— which motivates the CROSS-FITTED design below. Detectability caveat,
stated as the registered form: the type spikes are label-free
recoverable only above the spiked-covariance (BBP-type) threshold —
type-axis variance must exceed ~√(m/N) × bulk variance; L2's Part 0
computes the exact constant for its dims and MUST verify every arm sits
on the intended side (rule 3/17).

**Derivation 4 (the audit needs cross-fitting).** Auditing completeness
on ESTIMATED groups is biased optimistic: assignment to nearest centroid
truncates within-group variance at the boundaries (overfitting absorbs
identity into the partition), so the same-data audit UNDERSTATES
surviving identity. The honest instrument is cross-fitted: cluster on
one half of occasions/persons, audit on the held-out half. L2 validates
the cross-fitted audit against the oracle-group audit (L1's V-4
calibration) and measures the same-data bias as a named quantity.

**L2's charter (registration to be written after L1 adjudicates, per
routing):** arms on the η-continuum (η ∈ {0, .25, .5, .75, 1} at 2–3
identity shares), label-free instruments only — estimated-S projection
(spiked-PCA), the spectral taxometer η̂, the cross-fitted completeness
audit — against L1's oracle companions as upper bounds. Leans: (i) G(η)
curve containment; (ii) floor curve containment; (iii) η̂ operating
characteristic (monotone, calibrated at the poles L1 certified); (iv)
cross-fitted audit tracks oracle audit while same-data audit shows the
predicted optimistic bias. Rule-16 enumeration and the full gate set as
always; margins from L1's realized variances.

### OUTCOME (appended 2026-08-09, after run; append-only)

**`SHADOWS_FAIL__V1HV2HV3MV4M__P2L` — V-1 HOLD · V-2 HOLD · V-3 MISS · V-4 MISS
→ P2L.** Report: `reports/SUICA_M4_L1_TYPED_WORLD_REPORT.md`. Script:
`scripts/run_suica_m4_l1_typed_world.py`. Δ = 5.928950380606693 (RN-10
bisection to predicted ρ_id=0 oracle ARI 0.99; the ladder did NOT fire —
no cell saturated). All six Part-0 gates passed; K2a anchor cell
`phi0.9_occ8_intzero` re-derived BIT-EXACTLY (residual 0.0, 2048 rows ×
35 columns); reconstruction residual 2.22e-16; ISO and ALIGNED at
ρ_id=0 bit-identical (0.0); oracle removal reproduces the ρ_id=0 card to
3.12e-16. 14 cells × 8 worlds × 512 authors; 51.62 s adjudicated compute.

**The measured ARI ordering reproduces the Part-0 prediction cell for
cell**, both instruments. The identity tax (R4) is real and geometry-
dependent: ISO loses 0.0994690680231981 of ARI across ρ_id 0→.75,
ALIGNED loses 0.8102662 — **8.1×** at matched total identity energy. The
dichotomy (R2) is measured at full strength: pooled ALIGNED−ISO at
ρ_id ∈ {.35,.55} = **−0.4128850283258326** [−0.4305262035508016,
−0.3953012811449916]. The ALIGNED floor Φ(−Δ/(2σ_{b,u})) predicts the
noise-free per-boundary rate to 2.3% (ρ=.35: 0.027750651041666664 vs
0.027118834519294123, contained) and 6.7% (ρ=.55: 0.107421875 vs
0.10068281660598428, not contained) — 1/2 cells, clause HOLDs.

**The two misses.**

- **V-3 fails on the oracle-PROJECTION clause alone** — ISO restoration
  fraction **0.13468401332369143** [−0.0258742, 0.2774669] against the
  registered ½ bar (ALIGNED 0.003369541289360893 ≤ ¼ ✓; removal ✓ but a
  designed identity). This miss was **PRE-REGISTERED in Part 0 §0.6 with
  its derivation and a predicted value of 0.15265055004035916**. A
  post-hoc unregistered diagnostic at ρ_id=.75 — where R2's ambient
  energy condition Δ² ≳ σ_b² is violated (σ_b²/Δ² = 1.125) — gives a
  restoration fraction of **0.1495074669143142**, i.e. FLAT, not rising.
  **Reading:** R2's m/k_τ factor is an ENERGY statement about the
  k-means objective; ARI at these separations is owned by the
  boundary-normal Bayes error, which projection provably cannot change
  because the boundary normal lies inside S. The ISO half of R2 needs
  its estimand re-stated as a consistency THRESHOLD, not achieved ARI.
- **V-4 fails on tracking, 5/8 < 6** — a calibration OFFSET, not a
  structural failure. The meter's numerator error is a near-constant
  +0.0011…+0.0023, traced entirely to the realized two-split state
  coefficient **B̂ = 0.245861** (design 0.25, −1.66%), which propagates
  as +0.002754 into Â. The designed null at ρ_id=0 HOLDS as an
  equivalence (Ŝ_id = 0.010918432922059714 [0.0006823, 0.0198269] inside
  the pilot margin 0.029389351349840543) though its CI excludes 0. The
  declared second reading (contiguous-only, design B) also tracks 5/8
  with the offset reversed in sign, so the MISS is robust to the reading.
  Rule 13 triggered on both razor-thin calls; both STABLE at B = 20 000.

**Routing robustness:** P2L under the registered readings and under both
declared second readings (V-2 on the instrument prediction → 3 misses →
still P2L; V-4 on the contiguous meter → still 5/8).

**Registration defects recorded (#27–#30):** #27 G2L's (0.05,0.95) band
clause and V-1's 0.95 bar are **jointly unsatisfiable on the ISO arm**,
PROVED — the identity-only boundary z is Δ-free (ISO 5.65685/√(ρ/(1−ρ)),
ALIGNED 1.41421/√(ρ/(1−ρ))), so the ISO arm's identity-only floor never
exceeds 5.45e-4 on the registered grid; handled by RN-10's pre-declared
guard, band clause 2/4 (both ALIGNED), both ISO failures **from above**
and unsaturated. #28 V-3(d) is a designed identity, not a test. #29 the
floor clause had no registered comparand (RN-7 pinned the noise-free
TRUE-card rate before arms). #30 V-3(c)'s bar tests a proposition R2 does
not make.

**Consequence for L2 (theory-repair note owed first, per P2L).** Decouple
Δ from σ_b so the consistency threshold can be crossed; re-state R2's ISO
half as a threshold claim and test it there; give the completeness audit
its one calibration constant (per-world B̂, or bias-corrected target with
the B̂ error in the CI) — either moves tracking from 5/8 to 8/8 on these
numbers. The taxometric decision instrument L2 was to open is NOT damaged:
its discriminating signal (the ALIGNED floor and the 8.1× tax) is exactly
the part that measured cleanly.
