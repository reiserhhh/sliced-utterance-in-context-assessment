# SUICA M4-L1 — A typed world: the identity tax on grouping, the ISO/ALIGNED dichotomy, and the completeness audit calibrated

**Tier:** EXPLORATORY · label-free · synthetic throughout · CARD SPACE ONLY.
**Banner:** synthetic worlds calibrated to an opened-panel regime, exploratory.
**Registration:** `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md` § "M4-L1 — Instrument leg: a typed
world, the identity tax on grouping, the dichotomy, and the completeness audit calibrated",
REGISTERED 2026-08-09 BEFORE RUN, commit `e4a0e4e`. The registration text is binding; this
executor did implementation and execution only.
**Script:** `scripts/run_suica_m4_l1_typed_world.py`
**Artifacts:** `results/m4_l1_typed_world/` (gitignored).
**Theory:** `docs/SUICA_IDENTITY_THEORY_V1.md` appendix P (R1 circularity→EM, R2 the geometry
dichotomy with the SNR factor m/k_τ and the ALIGNED floor Φ(−Δ/(2σ_{b,u})), R3 the completeness
audit, R4 the identity tax); appendices A/H (the two-split probe, the exact AR algebra, the
validated instrument).

---

## Part 0 — gates computed 2026-08-09T15:15:38.432185+00:00 (UTC), written to disk BEFORE any main arm

Part 0 ran on **RESERVED pilot worlds 9901–9904** (the 4-world pilot convention standing after
K2e; disjoint from main world indices 0…7 and from every other leg's reserved indices).
`results/m4_l1_typed_world/gates.json`, `part0_predictions.csv`, `part0_pilot_cells.csv`,
`part0_enumeration_leans.csv`, `part0_enumeration_routing.csv` and `part0_tables.md` carry every
number below at full precision. The `arms` stage refuses to run unless every Part-0 gate passes
**and this report exists on disk** (`require_part0()`, l1:1425-1435).

Part-0 wall time **29.841949939727783 s** (Δ search 0.7906858921051025; predictions
20.94041395187378; pilot pass 7.671478033065796; K2a anchor 0.39937305450439453; power/rule-11
0.01609492301940918).

**No hypothesis-channel run of any kind preceded this stage.** Two things preceded it and are
disclosed with their timing in §3: (a) a PURE-ALGEBRA prototype of the R2 card-space geometry
and of the Δ-free floor identity — no world of any index was generated, no `build_world` call
was made, and its only outputs were the closed forms reproduced in §0.2 below; (b) a
CONSTRUCTION smoke of the leg's own code path on RESERVED pilot world 9901 at 128 authors
(shapes, reconstruction, one k-means call), which touched no main world.

### 0.0 Standing-rule-14 self-check (required by G5L)

**CARD SPACE ONLY. No gate and no lean in this leg compares quantities across scales or
instruments.** G0L re-derives K2a's own artifacts against K2a's own code path. G1L compares card
panels to card panels. V-1, V-2, V-3(a), V-3(c), V-3(d) compare **ARI to ARI**. V-3(b) compares a
card-space **per-boundary misassignment RATE** to the closed-form rate Φ(−Δ/(2σ_{b,u})) — same
units, no link. V-4 compares a normalized **variance SHARE** to a normalized variance share.
**There is no cross-scale gate here, so rule 14 has nothing to bind.**

### 0.1 Design as registered, and the register-notes (standing rule 9)

`master_seed` **20260822**; **14 cells × 8 worlds × 512 authors**; `G = 4` equal groups of 128;
`k_τ = 3`; `k = 48` latent, `DIM = 64`, `n_occ = 8`, `n_rep = 2`, `φ_slow = 0.90`, `w_int = 0`
(all inherited from K2a/F2 unchanged). 10 main cells = {ISO, ALIGNED} × ρ_id ∈ {0, .15, .35,
.55, .75}; 4 companions = the oracle REMOVAL and oracle PROJECTION variants of each geometry's
ρ_id = .55 cell.

Everything generative is K2a's, imported as a module and **not reimplemented** (rule 12):
`k2a.build_world` (k2a:184-236) — its `trait` return is the ONE thing this leg replaces;
`k2a.arm_weights('zero')` (k2a:129-138); `k2a.centered_channels` (k2a:250-259); `k2a.card`
(k2a:262-276); `k2a.splits` (k2a:335-340); `k2a.ar_mean_var/ar_set_var/ar_cross_cov`
(k2a:282-300); `k2a.suff_stats_for_world` (k2a:417-454) and `k2a.world_seed_for` (k2a:158-168)
for the G0L anchor only; `k2a.read_csv_rt` (k2a:118-120), `k2a.ci_of` (k2a:519-521),
`k2a.mc_sd_of_endpoint` (k2a:524-532). **`suica_core` is not touched**, and no file outside the
leg script was modified.

**NEW objects in this leg**, named by THIS script's line numbers (rule 12): `TETRAHEDRON`
(l1:191-193), `SIGMA_TAU2_PER_DELTA2` (l1:194), `identity_only_z` (l1:197-211), `sigma_b2_of`
(l1:213-222), `type_geometry` (l1:225-246), `latent_type_vectors` (l1:248-252),
`latent_identity` (l1:254-263), `typed_trait` (l1:265-279), `card_space_type_basis`
(l1:281-287), `build_typed_world` (l1:289-297), `cards_for_variant` (l1:306-377), `kmeans_lloyd`
(l1:380-425), `spectral_labels` (l1:428-433), `adjusted_rand_index` (l1:436-449),
`hungarian_accuracy` (l1:452-458), `boundary_error_rate` (l1:461-482),
`predicted_boundary_error` (l1:485-524), `group_centre` (l1:551-556), `audit_meter`
(l1:559-604), `pred_population` (l1:610-638), `predict_cell` (l1:656-679), `delta_search`
(l1:729-745), `build_enumeration` (l1:791-840), `measure_cell_world` (l1:843-893).

| RN | what the registration left open | resolution, pinned before any hypothesis number |
|---|---|---|
| RN-1 | the cell list | 10 main + 4 companions; a companion is a CARD VARIANT of its parent cell, same world, same draws, exactly paired (l1:152-163) |
| RN-2 | the world seed | keyed on the WORLD INDEX ONLY, salt `m4l1-world` — every cell of a world shares loadings, slow state, frame, noise, group assignment g, subspace S and the raw identity draw ξ **bit-for-bit** (l1:166-176) |
| RN-3 | the centroid configuration | the REGULAR SIMPLEX (tetrahedron) in S, scaled so all six pairwise separations equal Δ **exactly**; consequence σ_τ² = 3Δ²/8, and the ALIGNED floor is the same number on all six boundaries (l1:191-194) |
| RN-4 | what ρ_id means | an ENERGY share: σ_b² = E‖b_i‖² is the TOTAL within-type identity energy, **the same for both geometries** (R2's own reading), and Δ is held FIXED, so sweeping ρ_id sweeps σ_b² alone: σ_b² = (3Δ²/8)·ρ/(1−ρ) (l1:213-222) |
| RN-5 | the identity draw | both geometries consume the SAME ξ ~ N(0,I₄₈) — ISO scales it, ALIGNED projects onto S and scales — so the arms are maximally paired and **coincide exactly at ρ_id = 0** (l1:225-263) |
| RN-6 | grouping-instrument conventions | PRIMARY = Lloyd, k-means++ D² seeding, 64 restarts in one batch from `stable_bucket("<world_seed>-<cell>-<instrument>", salt='m4l1-kmeans')`, assignment ties → lowest cluster index, empty cluster re-seeded at the farthest point, convergence at unchanged labels ∨ max centroid shift < 1e-10 ∨ 300 iterations, restart ties → lowest restart index, **no scaling** (raw cards). SECOND = top-3 PCA of the pooled cards (column mean subtracted explicitly before the SVD) then the same k-means. Metric = ARI vs generator g; Hungarian-matched accuracy (`linear_sum_assignment`, maximizing) as second reading (l1:355-458) |
| RN-7 | what "the error" is for the floor clause | THE per-boundary misassignment event, measured directly: `⟨c_i − (τ_g+τ_h)/2, τ_h−τ_g⟩ > 0`, averaged over authors and the G−1 boundaries adjacent to each author's own type (l1:461-482). Rate-vs-rate against Φ(−Δ/(2σ_u)) |
| RN-8 | the completeness-audit meter | the T6′ two-split probe applied to within-TRUE-group deviation cards; PRIMARY = the **solved** two-split form B̂ = (C_int − C_cont)/(c_int − c_cont), Â_b = C_cont − B̂·c_cont, **Ŝ_id = Â_b/V_full**, using only K2a's validated AR algebra; SECOND = the contiguous-only form with B from the design; THIRD = the raw ρ_int, ρ_cont and their GAP (l1:530-604) |
| RN-9 | which prediction V-2 is scored against | the **R2 geometric prediction** = the nearest-TRUE-centroid (oracle) ARI of the card law, from an INDEPENDENT re-implementation on the prediction-only stream `m4l1-pred`; the instrument-behaviour prediction (the registered PRIMARY run on draws from the same law) is the declared second reading, and V-2 is scored under both (l1:606-679) |
| RN-10 | the Δ rule and its one-step ladder | §0.2 below (l1:681-727) |
| RN-11 | sub-clause → lean aggregation | CONJUNCTIVE: any MISS → MISS; else any BOUNDARY → BOUNDARY; else HOLD. UNREALIZABLE sub-clauses are excluded from the conjunction and disclosed in the tag (l1:762-776) |
| RN-12 | BOUNDARY in the routing | a rule-13 BOUNDARY lean is NOT counted as a MISS; the tag travels downstream (l1:778-788) |
| RN-13 | the bootstrap | ONE paired world-block resample (B = 2000, seed = master_seed), applied identically to EVERY cell, so every cross-cell contrast is paired inside the bootstrap (l1:1459-1465) |

### 0.2 RN-10 — the Δ choice, and a proved registration defect (rule 11 + rule 17)

**Derived a priori, before any number was computed.** In this parameterization the identity-only
per-boundary z-score is **Δ-free**, because σ_b² is tied to Δ through ρ_id:

    z(dims, ρ) = (Δ/2) / (σ_b/√dims),  σ_b² = (3Δ²/8)·ρ/(1−ρ)
               = √(2·dims/3) / √(ρ/(1−ρ))

so **ISO: z = 5.65685…/√(ρ/(1−ρ))** and **ALIGNED: z = 1.41421…/√(ρ/(1−ρ))**, and R2's SNR factor
m/k_τ = 16 is exactly the ratio of the two z². The registered grid's floors are therefore fixed
numbers, independent of Δ:

| ρ_id | ISO z | ISO floor Φ(−z) | ALIGNED z | ALIGNED floor Φ(−z) |
|---:|---:|---:|---:|---:|
| 0.15 | 13.466006584482772 | 1.239582298845414e-41 | 3.366501646120693 | 0.00038064063922746405 |
| 0.35 | 7.708992893275453 | 6.340723736515734e-15 | 1.9272482233188633 | 0.026974351402524972 |
| 0.55 | 5.11681719253465 | 1.5536726050242252e-07 | 1.2792042981336624 | 0.10041256134757275 |
| 0.75 | 3.2659863237109046 | 0.000545417588062648 | 0.8164965809277261 | 0.20710808912126252 |

**The registration defect this proves.** The ISO arm's identity-only per-boundary error never
exceeds 5.45e-4 anywhere on the registered grid: **the ISO ρ_id = .35 cell cannot be brought to
mid-range by identity at ANY Δ.** Any mid-range ISO ARI must therefore be manufactured by the
ρ-INDEPENDENT state/observation channel, which depresses the ρ_id = 0 cell by very nearly the
same amount. G2L's registered band clause (ISO mid cell ARI < 0.95) and V-1's registered bar
(ρ_id = 0 ARI ≥ 0.95 **in 8/8 worlds**) therefore share a vanishing feasible window in Δ — the
two clauses are jointly satisfiable only where both sit within ≈ ±0.005 of ARI 0.95, which is
below the design's per-world ARI scatter. This is a **rule-11 unsatisfiability**, proved (not
estimated), and recorded as registration defect **#27** in §3.

**The pinned rule, declared before any pilot ARI existed** (l1:681-727):

1. **Δ₀ := bisection so the Part-0 predicted ρ_id = 0 oracle ARI equals 0.99** (V-1's bar 0.95
   plus headroom, because V-1 is a per-WORLD 8/8 clause, not a pooled one). Bracket [1, 20],
   ≤ 40 iterations, common random numbers (24 fixed prediction populations at every Δ, so the
   objective is a deterministic function of Δ).
2. G2L evaluates **both** the registered band clause ARI ∈ (0.05, 0.95) on the four mid cells
   (geometry × ρ_id ∈ {.35, .55}) **and** the machinery section's saturation clause (no main
   cell at pilot ARI ≥ 0.999 or ≤ 0.001).
3. The ladder has exactly **ONE** step: Δ₁ = 1.5·Δ₀ if any mid cell is FLOORED; Δ₁ = Δ₀/1.5 if
   any mid cell is SATURATED.
4. **GUARD:** the step is REFUSED, and the triggering clause recorded UNREALIZABLE with the
   proof above, if it would drive the predicted ρ_id = 0 ARI below 0.97 — manufacturing a V-1
   MISS would route the leg to P1L on an instrument artifact, the one outcome the registration
   reserves for a real instrument defect.
5. A band clause failing **from above on an UNSATURATED cell does not trigger the ladder** (a
   cell at ARI 0.98 is not "saturated at 1"); it is recorded as the rule-11 unsatisfiability.

**Result: Δ = 5.928950380606693** (35 bisection iterations), σ_τ² = 13.182169730886095,
σ_b²(ρ) = σ_τ²·ρ/(1−ρ). **The ladder did NOT fire** (no cell saturated), so no step and no
refusal was needed; clause 5 applied to the two ISO mid cells.

### 0.3 G0L — construction, the designed coincidences, and the K2a anchor: **PASS**

| check | value | criterion |
|---|---:|---|
| five-channel reconstruction residual (max over pilot worlds) | **2.220446049250313e-16** | ≤ 1e-12 ✓ |
| K2a anchor cell `phi0.9_occ8_intzero`, 2048 rows × 35 columns re-derived from k2a's own code path vs the persisted artifact | **max abs residual 0.0 — BIT-EXACT** ✓ | bit-exact |
| K2a anchor persisted readbacks (round-trip parser) | ρ_contiguous **0.8298442703284798**, GAP **0.09302852291619967** | reported |
| \|realized ρ_id − designed\| (max over all cells × pilot worlds) | **0.017261584710480116** | ≤ 0.02 ✓ |
| all six realized latent separations vs Δ (max abs deviation) | **1.7763568394002505e-15** | ≤ 1e-9 ✓ |
| in-leg ARI vs `sklearn.metrics.adjusted_rand_score`, 64 random label pairs | **3.69712940817557e-17** | ≤ 1e-12 ✓ |
| PCA grand-mean norm of the pooled cards (max) | **5.358030947101785e-17** | reported (the cards are author-centred by construction) |

**Two designed coincidences, reported as exact identities, not as findings:**

- **ISO and ALIGNED at ρ_id = 0 are BIT-IDENTICAL panels**: max abs card difference **0.0**
  (same ξ at zero scale, RN-5). V-1 therefore scores 8 distinct worlds twice — disclosed.
- **The oracle-REMOVAL companion reproduces the ρ_id = 0 card**: max abs difference
  **3.122502256758253e-16** (floating-point only). V-3(d) is consequently a **designed identity**,
  the registration's own "upper bound sanity", and is reported as such rather than as an
  empirical result. (This is the K1b lesson — Ŝ ≡ 1 by construction — applied prospectively.)

Realized ρ_id per level (pilot means): ISO 0.000000 / 0.150396 / 0.350703 / 0.550761 / 0.750574;
ALIGNED 0.000000 / 0.151158 / 0.351969 / 0.552038 / 0.751466. The ALIGNED deviations are the
larger ones because the identity energy is carried by 3 latent dimensions rather than 48
(relative sd √(2/3)/√512 = 3.6% on σ_b², vs 0.9% for ISO) — an expected sampling fact of the
geometry, not a construction error.

### 0.4 G1L — rule-10 non-degeneracy: **PASS**

Card-panel RMS changes, minimum over the four pilot worlds:

| manipulation | min RMS card change |
|---|---:|
| drop the TYPE channel (ζ = b only) | **0.04595543588971581** |
| ISO vs ALIGNED at ρ_id = .55 | **0.06196665557808347** |
| ρ_id = 0 vs ρ_id = .55 (worse of the two geometries) | **0.04988488404198821** |
| ISO vs ALIGNED **at ρ_id = 0** | **0.0** — DESIGNED identity, reported, not a gate input |

Criterion: every registered manipulation changes the card panel with RMS > 1e-6. ✓

### 0.5 G2L — rule-3 liveness and rule-17 realizability: **PASS**

Pilot cell ARI (mean over the four RESERVED worlds), both instruments, and the type-subspace
estimability check:

| cell | PRIMARY ARI | SECOND (spectral) ARI | top-3 eigengap ratio | in band (0.05,0.95) | saturated |
|---|---:|---:|---:|---|---|
| `ISO_rho0` | 0.993481900879526 | 0.992177 | 3.4552 | — | no |
| `ISO_rho0.15` | 0.9908828473318589 | 0.990883 | 3.3025 | — | no |
| `ISO_rho0.35` | 0.9895833204008752 | 0.988279 | 3.0258 | **false (from ABOVE)** | no |
| `ISO_rho0.55` | 0.9727827122307798 | 0.967626 | 2.6299 | **false (from ABOVE)** | no |
| `ISO_rho0.75` | 0.9069970759825239 | 0.881320 | 2.0206 | — | no |
| `ALIGNED_rho0` | 0.993481900879526 | 0.992177 | 3.4552 | — | no |
| `ALIGNED_rho0.15` | 0.9268642704797658 | 0.926854 | 3.9649 | — | no |
| `ALIGNED_rho0.35` | 0.6922129657330174 | 0.695372 | 4.9418 | **true** | no |
| `ALIGNED_rho0.55` | 0.4257539445702166 | 0.425525 | 6.7906 | **true** | no |
| `ALIGNED_rho0.75` | 0.18717569916313742 | 0.181113 | 11.6138 | — | no |

- **rule 3 (liveness):** every registered knob is live — G1L shows the type channel, both
  geometries and every ρ_id level change the card panel; the top-k_τ eigengap is > 0 in every
  cell (min absolute gap **16.460513284934507**, min ratio **2.0205543669094723**), so the type
  subspace is estimable label-free.
- **rule 17 (realizability):** **no cell is saturated** at ARI 0 or 1 (band (0.001, 0.999)),
  so the ladder does not fire. The registered (0.05, 0.95) band clause holds on **2/4** mid
  cells — both ALIGNED — and fails **from above** on both ISO mid cells, which is the
  §0.2 unsatisfiability realized exactly as proved. Per RN-10 clause 5 this is recorded as an
  UNREALIZABLE clause with its proof, not as a ladder trigger.
- Gate verdict: **PASS** on the machinery section's saturation criterion, with the band clause
  scored 2/4 and its two failures proved unrealizable jointly with V-1.

### 0.6 G3L — power (4-world pilot), rule-11 satisfiability with directions, rule-13 spec: **PASS**

MDE at the main grain (n = 8 worlds) from the 4-world pilot sd, `(t_{.975,3} + t_{.80,3})·sd/√8`
(rule-16 convention: ≥ 4 pilot worlds, no df inflation needed). Full table in
`part0_tables.md`; the clauses that gate a lean:

| clause | pilot mean | pilot sd (world) | MDE at n=8 | direction |
|---|---:|---:|---:|---|
| ARI `ISO_rho0` | 0.993481900879526 | 0.0025990536524339025 | 0.003823 | two-sided containment |
| ARI `ISO_rho0.15` | 0.990883 | 0.002599 | 0.003824 | two-sided containment |
| ARI `ISO_rho0.35` | 0.989583 | 0.007351 | 0.010814 | two-sided containment |
| ARI `ISO_rho0.55` | 0.972783 | 0.006522 | 0.009594 | two-sided containment |
| ARI `ISO_rho0.75` | 0.906997 | 0.028474 | 0.041888 | two-sided containment |
| ARI `ALIGNED_rho0.35` | 0.692213 | 0.035931 | 0.052858 | two-sided containment |
| ARI `ALIGNED_rho0.55` | 0.425754 | 0.024370 | 0.035851 | two-sided containment |
| floor rate `ALIGNED_rho0.35` | 0.025879 | 0.005710 | 0.008400 | two-sided containment of Φ(−Δ/(2σ_{b,u})) |
| floor rate `ALIGNED_rho0.55` | 0.099284 | 0.009866 | 0.014514 | two-sided containment of Φ(−Δ/(2σ_{b,u})) |
| audit Ŝ_id `ISO_rho0` (= `ALIGNED_rho0`) | 0.003447 | 0.019978 | **0.029389** | two-sided equivalence within margin |
| audit Ŝ_id `ISO_rho0.35` | 0.156340 | 0.018657 | 0.027446 | two-sided containment of the designed share (0.149879) |
| audit Ŝ_id `ALIGNED_rho0.55` | 0.293936 | 0.007689 | 0.011311 | two-sided containment of the designed share (0.290041) |

**V-4's ρ_id = 0 margin is therefore pinned at 0.029389351349840543** (the registration's "margin
from pilot"), as an equivalence (rule 4), not a nil-significance test.

**rule 11, satisfiability with directions** (all seven clause groups checked against the pilot
statistics):

| lean | direction | satisfiable | number |
|---|---|---|---|
| V-1 | one-sided lower, per world, 8/8 | **yes** | pilot mean 0.993482, world sd 0.002599 → the bar 0.95 is 16.7 world-sd below the mean |
| V-2 | two-sided containment + exact ordering | **yes** | predicted ISO ordering is strictly decreasing (0.99267, 0.99097, 0.98513, 0.97255, 0.91712) |
| V-3(a) | one-sided lower, CI excludes 0 | **yes** | predicted pooled ALIGNED−ISO = **−0.4052893256656327**, z = **33.35** |
| V-3(b) | two-sided containment | **yes** | pilot floor rates 0.025879 / 0.099284 vs closed forms 0.026974 / 0.100413, MDEs 0.0084 / 0.0145 |
| V-3(c) | one-sided (ISO ≥ ½; ALIGNED ≤ ¼) | **yes, but PREDICTED MISS on the ISO half** — see below |
| V-3(d) | one-sided lower ≥ 0.95 | **yes** — but it is a DESIGNED IDENTITY (G0L residual 3.1e-16) |
| V-4 | equivalence at ρ=0; containment elsewhere | **yes** | margin 0.029389, pilot Ŝ_id at ρ=0 = 0.003447 |

**A pre-registered predicted MISS (V-3c, ISO half).** From the Part-0 predictions at Δ:

    predicted ISO deficit    = 0.025372902308074652
    predicted ISO restoration= 0.003873187493447894   → fraction 0.15265055004035916  (bar 0.5)
    predicted ALIGNED deficit= 0.5448752010371112
    predicted ALIGNED restor.= −0.0015496831257334476 → fraction −0.0028441065454691146 (bar 0.25)

**Derivation of the predicted miss.** R2's (k_τ/m) reduction is an **ENERGY** statement: it
governs the *k*-means objective, i.e. whether Δ² ≳ σ_b² + noise holds in the ambient space. At
ρ_id = .55 the ambient condition is **already satisfied** (σ_b²/Δ² = **0.4583333…**), so Lloyd
already resolves the four types and the ISO cell's ARI deficit is **boundary-normal Bayes error**
— which projection onto S cannot touch, because the boundary normal lies **inside** S and
projection leaves the per-direction variance along it unchanged. The registered ½-deficit bar is
therefore predicted to fail. The energy condition is violated only at ρ_id = .75
(σ_b²/Δ² = 1.125), which is outside the registered companion grid; a post-hoc diagnostic at that
ρ_id is registered here as a READING ONLY (§2.6).

**rule-13 spec:** B = 2000 at seed = master_seed for every interval clause; a ≥ 10×B (20 000)
recheck at any clause whose boundary lies within 2 Monte-Carlo endpoint sds of the estimate; a
verdict that flips is scored BOUNDARY, neither HOLD nor MISS.

### 0.7 G4L — the Part-0 R2 predictions, computed BEFORE any arm: **PASS**

Derivation: the card law is c_i = M(τ_{g(i)} + b_i) + w_slow·M·s̄_i + w_noise·ē_i with
M = A_SCALE·L·diag(G_PROFILE) (f2:196 / k2a:210), Var(s̄) = `k2a.ar_mean_var(8, .90)` =
0.7731890281250001 and the observation term SIGMA_ISO²/(n_occ·n_rep) — K2a's validated algebra.
The R2 prediction of per-cell ARI is the **nearest-TRUE-centroid (oracle) ARI** of that law,
averaged over 64 (main cells) / 12 (companions) independent replicate populations drawn on the
prediction-only stream `m4l1-pred`. Identity enters the boundary-normal variance with its full
energy/48 (ISO) or energy/3 (ALIGNED).

| cell | σ_b²/Δ² | **pred ARI (R2 oracle)** | sd | pred ARI (instrument) | pred ARI (spectral) | per-boundary floor |
|---|---:|---:|---:|---:|---:|---:|
| `ISO_rho0` | 0.000000 | **0.9926694715723663** | 0.005613 | 0.988727 | 0.986553 | 0.0 |
| `ISO_rho0.15` | 0.066176 | **0.9909657938725764** | 0.006228 | 0.985695 | 0.983542 | 1.2396e-41 |
| `ISO_rho0.35` | 0.201923 | **0.9851334204782212** | 0.008199 | 0.977501 | 0.976214 | 6.3407e-15 |
| `ISO_rho0.55` | 0.458333 | **0.9725492075749163** | 0.012337 | 0.963355 | 0.959556 | 1.5537e-07 |
| `ISO_rho0.75` | 1.125000 | **0.9171184440448555** | 0.018986 | 0.898709 | 0.888119 | 5.4542e-04 |
| `ALIGNED_rho0` | 0.000000 | 0.9926694715723663 | 0.005613 | 0.988727 | 0.986553 | 0.0 |
| `ALIGNED_rho0.15` | 0.066176 | 0.9297487... | 0.018689 | 0.922738 | 0.920656 | 3.8064e-04 |
| `ALIGNED_rho0.35` | 0.201923 | 0.7051583... | 0.031183 | 0.709789 | 0.711228 | 2.6974e-02 |
| `ALIGNED_rho0.55` | 0.458333 | 0.4419456... | 0.036788 | 0.443852 | 0.438668 | 1.0041e-01 |
| `ALIGNED_rho0.75` | 1.125000 | 0.2063446... | 0.027985 | 0.191842 | 0.195024 | 2.0711e-01 |
| `ISO_rho0.55_removal` | 0.458333 | 0.9882858... | 0.005894 | 0.988727 | 0.986553 | — |
| `ISO_rho0.55_projection` | 0.458333 | 0.9676444... | 0.016275 | 0.967228 | 0.967228 | — |
| `ALIGNED_rho0.55_removal` | 0.458333 | 0.9895799... | 0.004428 | 0.988727 | 0.986553 | — |
| `ALIGNED_rho0.55_projection` | 0.458333 | 0.4467601... | 0.033177 | 0.442303 | 0.440597 | — |

**Predicted ARI-degradation ordering (all 10 main cells, the registration's first named
predicted object):**

    ISO_rho0 = ALIGNED_rho0 > ISO_rho0.15 > ISO_rho0.35 > ISO_rho0.55 > ALIGNED_rho0.15
             > ISO_rho0.75 > ALIGNED_rho0.35 > ALIGNED_rho0.55 > ALIGNED_rho0.75

**Predicted ISO ordering strictly decreasing in ρ_id: TRUE.**

**Predicted audit reading (the registration's fourth named predicted object).** The T6′ meter is
designed to read the b-share exactly, so the expected surviving-identity share per cell is the
designed b-share itself: 0 at ρ_id = 0, and (pilot-realized) 0.0547 / 0.1499 / 0.2854 / 0.4941
(ISO) and 0.0558 / 0.1527 / 0.2900 / 0.5003 (ALIGNED) at ρ_id = .15/.35/.55/.75 — i.e. the
audit's completeness defect is predicted to equal the b-share, R3's "impossibility half" made
into a number.

### 0.8 G5L — hygiene, rule 14, rule 16: **PASS**

- **Round-trip parsing everywhere** (`k2a.read_csv_rt`, `float_precision='round_trip'`) on every
  artifact re-read.
- **Chunked, foreground stages**; Part 0 at 29.84 s is far inside the 600 s chunk rule.
- **rule 14** self-check: §0.0 — nothing to bind.
- **rule 16 enumeration, the FULL adjudication object** (`part0_enumeration_leans.csv`,
  `part0_enumeration_routing.csv`):
  - **Layer A** (sub-clause → lean): 304 rows = 4² + 4² + 4⁴ + 4² expected, 304 unique keys, all
    assigned. No gap, no overlap.
  - **Layer B** (leans → routing): **81 rows = 3⁴**, 81 unique keys, all assigned, all four
    routes reachable — P1L 27, P3L 24, P4L 16, P2L 14.
  - **The registered 2⁴ = 16-row subtable** (HOLD/MISS only, no BOUNDARY): **P1L 8, P2L 4,
    P3L 3, P4L 1**, reproduced in full in §2.7.

**Part-0 verdict: G0L PASS · G1L PASS · G2L PASS · G3L PASS · G4L PASS · G5L PASS →
`part0_all_pass = true`; the arms stage is unlocked.**

**Stage estimates declared here, with the 2× stop threshold:** arms ≈ 8 worlds × 14 cells at the
pilot's measured 1.92 s/world → **≈ 16 s, stop at 32 s**; finalize (bootstraps B = 2000 and
20 000 over 8 blocks) → **≈ 20 s, stop at 40 s**; post-hoc diagnostic → **≈ 8 s, stop at 16 s**.

---

## Part 1 — arms

The `arms` stage ran **after** Part 0 was on disk (enforced in code by `require_part0()`), at
Δ = 5.928950380606693: **14 cells × 8 main worlds (indices 0…7) × 512 authors = 112 world-cells,
57 344 author-cards**, in **12.932733058929443 s** (1.62 s/world) — inside the Part-0 estimate of
16 s and well inside its 2× stop threshold. `finalize` took **0.0736379623413086 s** (both
bootstraps, B = 2000 and the rule-13 B = 20 000, over 8 world blocks). The post-hoc diagnostic
(§2.6) took **6.768013954162598 s** and ran only after `decision.json` had been written.

Every cell of a world shares the loadings, the slow state, the frame channel, the noise, the
group assignment, the type subspace and the raw identity draw ξ **bit-for-bit** (RN-2), and one
paired world-block resample is applied to every cell (RN-13), so every contrast reported below
is a within-world paired contrast.

## Part 2 — results

### 2.1 Per-cell ARI: measured vs the Part-0 R2 prediction, both instruments

PRIMARY = Lloyd k-means on cards, 64 restarts, known G. SECOND = top-3 PCA then the same
k-means. CIs are the paired world-block bootstrap (B = 2000, seed = master_seed).

| cell | **PRIMARY ARI** | CI95 | pred (R2 oracle) | contains | pred (instrument) | contains | SECOND ARI | CI95 | Hungarian acc |
|---|---:|---|---:|---|---:|---|---:|---|---:|
| `ISO_rho0` | **0.9947840261129702** | [0.9915196, 0.9980463] | 0.9926694715723663 | **yes** | 0.988727 | no | 0.9947840261129702 | [0.9915196, 0.9980463] | 0.998047 |
| `ISO_rho0.15` | **0.9928347358211247** | [0.9895779, 0.9960938] | 0.9909657938725764 | **yes** | 0.985695 | no | 0.9928324 | [0.9895469, 0.9967380] | 0.997314 |
| `ISO_rho0.35` | **0.9863450503413698** | [0.9817923, 0.9915482] | 0.9851334204782212 | **yes** | 0.977501 | no | 0.9844121 | [0.9773006, 0.9908856] | 0.994873 |
| `ISO_rho0.55` | **0.9664213102607500** | [0.9537028, 0.9774188] | 0.9725492075749163 | **yes** | 0.963355 | yes | 0.9644518 | [0.9548159, 0.9753801] | 0.987305 |
| `ISO_rho0.75` | **0.8953149580897721** | [0.8756696, 0.9136906] | 0.9171184440448555 | **NO** | 0.898709 | yes | 0.8855671 | [0.8604542, 0.9088464] | 0.959717 |
| `ALIGNED_rho0` | **0.9947840261129702** | [0.9915196, 0.9980463] | 0.9926694715723663 | yes | 0.988727 | no | 0.9947840261129702 | [0.9915196, 0.9980463] | 0.998047 |
| `ALIGNED_rho0.15` | **0.9150944** | [0.8958190, 0.9331277] | 0.9297487 | yes | 0.922738 | yes | 0.9126779 | [0.8935260, 0.9300289] | 0.967529 |
| `ALIGNED_rho0.35` | **0.7064312** | [0.6895873, 0.7238264] | 0.7051583 | yes | 0.709789 | yes | 0.7065183 | [0.6902789, 0.7229786] | 0.880859 |
| `ALIGNED_rho0.55` | **0.4205651** | [0.4011246, 0.4393934] | 0.4419456 | NO | 0.443852 | no | 0.4228574 | [0.4044022, 0.4394872] | 0.736328 |
| `ALIGNED_rho0.75` | **0.1845178** | [0.1564823, 0.2106017] | 0.2063446 | yes | 0.191842 | yes | 0.1804900 | [0.1538810, 0.2088616] | 0.563721 |
| `ISO_rho0.55_removal` | **0.9947840261129702** | [0.9915196, 0.9980463] | 0.9882858 | no | 0.988727 | no | 0.9947840 | [0.9915196, 0.9980463] | 0.998047 |
| `ISO_rho0.55_projection` | **0.9702410** | [0.9593902, 0.9805191] | 0.9676444 | yes | 0.967228 | yes | 0.9702410 | [0.9593902, 0.9805191] | 0.988770 |
| `ALIGNED_rho0.55_removal` | **0.9947840261129702** | [0.9915196, 0.9980463] | 0.9895799 | no | 0.988727 | no | 0.9947840 | [0.9915196, 0.9980463] | 0.998047 |
| `ALIGNED_rho0.55_projection` | **0.4225003** | [0.4018264, 0.4423208] | 0.4467601 | no | 0.442303 | no | 0.4229257 | [0.4020378, 0.4429328] | 0.737305 |

**Measured ARI-degradation ordering (10 main cells):**

    ISO_rho0 = ALIGNED_rho0 > ISO_rho0.15 > ISO_rho0.35 > ISO_rho0.55 > ALIGNED_rho0.15
             > ISO_rho0.75 > ALIGNED_rho0.35 > ALIGNED_rho0.55 > ALIGNED_rho0.75

— **identical, cell for cell, to the Part-0 predicted ordering.** The SECOND (spectral) reading
gives the same ordering and tracks PRIMARY to within 0.010 in every cell.

### 2.2 V-1 (designed sanity) [prior .85] — **HOLD**

| sub-clause | worlds ≥ 0.95 | min world ARI | mean ARI | state |
|---|---:|---:|---:|---|
| `ISO_rho0` | **8/8** | 0.9843446053856576 | 0.9947840261129702 | HOLD |
| `ALIGNED_rho0` | **8/8** | 0.9843446053856576 | 0.9947840261129702 | HOLD |

Per-world ARI at ρ_id = 0: 0.98434461, 0.98958332, 0.99478143, 0.99478143, 0.99478143, 1.0, 1.0,
1.0. **Disclosed:** the two ρ_id = 0 cells are bit-identical panels (G0L residual 0.0), so this
is 8 distinct worlds scored twice, not 16 independent tests. The world is groupable when the
owner's 誤差 = 0 premise holds by construction. **V-1 HOLD.**

### 2.3 V-2 (the identity tax, R4) [prior .80] — **HOLD** (registered reading), **MISS** under the declared second reading

- **Sub-clause (a), exact ordering:** ISO ARI is **strictly decreasing** in ρ_id —
  0.9947840261129702 > 0.9928347358211247 > 0.9863450503413698 > 0.9664213102607500 >
  0.8953149580897721. Predicted ordering reproduced exactly. **HOLD.**
- **Sub-clause (b), containment of the Part-0 prediction, ≥ 3/4 non-zero cells:** **3/4** under
  the registered R2-oracle prediction (RN-9): ρ_id = .15 ✓, .35 ✓, .55 ✓, **.75 ✗** (measured
  0.8953149580897721, CI [0.8756696, 0.9136906]; predicted 0.9171184440448555 — the prediction
  sits 0.0034 above the CI's upper edge). **HOLD at exactly the threshold.**
- **Declared second reading (RN-9), the instrument-behaviour prediction:** containment **2/4**
  (.55 ✓, .75 ✓; .15 ✗ and .35 ✗ because the prediction MC's k-means runs ~0.007 BELOW the real
  worlds at high ARI). Under this reading sub-clause (b) — and hence V-2 — would be **MISS**.

**The routing is invariant to this choice** (V-2 MISS would give three misses, still ≥ 2 → P2L),
which is stated here rather than left implicit. The registered verdict is the RN-9 one, pinned
in Part 0 before any arm ran: **V-2 HOLD**.

The identity tax itself is measured and it is small in the ISO geometry: from ρ_id = 0 to
ρ_id = .75 the ISO ARI falls by **0.0994690680231981**, while over the same sweep the ALIGNED
ARI falls by **0.8102662** — a factor of **8.1**.

### 2.4 V-3 (the dichotomy, R2) [prior .75] — **MISS**

| sub-clause | measurement | state |
|---|---|---|
| (a) ALIGNED < ISO at ρ_id ∈ {.35, .55}, pooled CI excludes 0 | pooled **−0.4128850283258326**, CI [**−0.4305262035508016**, **−0.3953012811449916**]; per-ρ: .35 → −0.27991380512976693 [−0.2976973, −0.2623496]; .55 → **−0.5458562515218983** [−0.5681311, −0.5244049] | **HOLD** |
| (b) ALIGNED floor CI containment ≥ 1/2 cells | **1/2**. ρ_id = .35: measured **0.027750651041666664** [0.0266927, 0.0288086] vs Φ(−Δ/(2σ_{b,u})) = **0.027118834519294123** ✓. ρ_id = .55: measured **0.107421875** [0.1026200, 0.1122233] vs **0.10068281660598428** ✗ (measured 6.7% above the floor) | **HOLD** (threshold ≥ 1 of 2) |
| (c) oracle PROJECTION restores ISO by ≥ ½ its deficit while restoring ALIGNED by ≤ ¼ | ISO fraction **0.13468401332369143** [−0.0258742, 0.2774669] vs bar 0.5 → **fails**; ALIGNED fraction **0.003369541289360893** [−0.0050290, 0.0111144] vs bar 0.25 → holds | **MISS** |
| (d) oracle REMOVAL restores both to ≥ 0.95 | ISO **0.9947840261129702**, ALIGNED **0.9947840261129702** | **HOLD** — but a **designed identity** (G0L: the removal card reproduces the ρ_id = 0 card to 3.12e-16), so it certifies the construction, not the theory |

**V-3 MISS, on sub-clause (c) alone — and that miss was PRE-REGISTERED in Part 0 §0.6 with its
derivation and its predicted value (0.15265055004035916 vs the measured 0.13468401332369143).**

ISO deficit 0.028362715852220277, restoration 0.0038200043997365096; ALIGNED deficit
0.5742189673741185, restoration 0.0019348545197012679.

### 2.5 V-4 (the completeness audit, R3) [prior .80] — **MISS**

- **Sub-clause (a), the designed null at ρ_id = 0, margin 0.029389351349840543 (pilot-derived):**
  Ŝ_id = **0.010918432922059714**, CI [**0.0006823303588321729**, **0.019826907255164648**] ⊂
  ±0.029389 → **HOLD as an equivalence**. Reported honestly: the CI **excludes 0**, so the meter
  carries a small positive offset at the designed null rather than reading exactly zero.
- **Sub-clause (b), tracking the designed b-share within CI in ≥ 6/8 non-zero cells: 5/8 → MISS.**

| cell | Ŝ_id (PRIMARY, two-split solved) | designed b-share | Ŝ − design | CI95 of the difference | tracks |
|---|---:|---:|---:|---|---|
| `ISO_rho0.15` | 0.064943 | 0.054799 | +0.010143 | [−0.000252, +0.018945] | **yes** |
| `ISO_rho0.35` | 0.159335 | 0.150328 | +0.009006 | [−0.000776, +0.017173] | **yes** |
| `ISO_rho0.55` | 0.294011 | 0.286555 | +0.007456 | [−0.001254, +0.014789] | **yes** |
| `ISO_rho0.75` | 0.501640 | 0.496502 | +0.005138 | [−0.001807, +0.010905] | **yes** |
| `ALIGNED_rho0.15` | 0.064306 | 0.055202 | +0.009104 | [+0.000966, +0.016858] | **no** |
| `ALIGNED_rho0.35` | 0.158778 | 0.151421 | +0.007357 | [+0.000696, +0.014152] | **no** |
| `ALIGNED_rho0.55` | 0.293836 | 0.288496 | +0.005340 | [+0.000127, +0.011004] | **no** |
| `ALIGNED_rho0.75` | 0.502040 | 0.499287 | +0.002753 | [−0.001452, +0.007049] | **yes** |

**The miss is a calibration OFFSET, not a failure of the audit's structure.** Three facts pin it:

1. The meter's error in the numerator is nearly constant: Â_hat − A_design = +0.002284, +0.002245,
   +0.002216, +0.002182, +0.002125 (ISO ρ = 0…0.75) and +0.002284, +0.002006, +0.001799,
   +0.001553, +0.001139 (ALIGNED). The share error is that constant divided by the cell's
   V_full, which is why it shrinks from +0.0109 to +0.0028 as ρ_id grows.
2. **The whole offset is the realized state coefficient.** B̂ = **0.245861** — identical to six
   decimals in every ambient cell, because the two-split difference C_int − C_cont cancels the
   identity term exactly and the η channels are bit-identical across cells. Its deficit from the
   design value 0.25 propagates as (0.25 − 0.245861)·c_cont = **+0.002754** into Â, which
   reproduces the observed numerator error to within 0.0006–0.0016.
3. The failures are the ALIGNED cells, not because their bias is larger (it is *smaller*) but
   because their CIs are **tighter** — the ALIGNED meter has 1.5–2.4× less world-level scatter.
   The design is well enough powered to see a 0.005 offset, and it saw it.

**The second reading (RN-8: contiguous-only with B from the design) also tracks 5/8** — with the
offset reversed in sign (−0.0015 to −0.0042) and the failures on the ALIGNED ρ_id = .35/.55/.75
cells. Its null reads −0.00229339, CI [−0.006532, +0.001901], also inside the margin. **So V-4's
MISS is robust to the meter reading; only the identity of the three failing cells changes.**

### 2.6 Post-hoc diagnostic (UNREGISTERED, not a lean input): where does R2's projection gain live?

Registered in Part 0 §0.6 as the follow-up implied by the predicted V-3(c) miss, run only after
`decision.json` was written. The registered companions sit at ρ_id = .55 where R2's ambient
energy condition Δ² ≳ σ_b² **already holds** (σ_b²/Δ² = 0.4583). At **ρ_id = .75** it is
**violated** (σ_b²/Δ² = **1.125**), so R2's energy argument predicts the projection gain should
appear there. It does not:

| geometry | ambient ARI | + oracle PROJECTION | + oracle REMOVAL | ρ_id = 0 reference | restoration fraction |
|---|---:|---:|---:|---:|---:|
| ISO | 0.8953149580897721 | 0.9101863264862481 | 0.9947840261129702 | 0.9947840261129702 | **0.1495074669143142** |
| ALIGNED | 0.18451778215676737 | 0.18318326951011615 | 0.9947840261129702 | 0.9947840261129702 | **−0.0016470051129556236** |

The ISO restoration fraction is **0.1495** at ρ_id = .75 versus **0.1347** at ρ_id = .55 — flat,
not rising, across a 2.5× change in the energy ratio that straddles R2's ambient threshold.

### 2.7 Rule 13, and the rule-16 routing

**Rule 13** (B = 2000 at seed = master_seed; ≥ 10×B = 20 000 recheck when a clause boundary lies
within 2 Monte-Carlo endpoint sds): **2 clauses triggered, 0 BOUNDARY.**

| cell | clause | boundary | MC sd of endpoint @B=2000 | distance | verdict @2000 | verdict @20000 | status |
|---|---|---:|---:|---:|---|---|---|
| `ISO_rho0.15` | audit meter tracks designed b-share | 0.0 | 0.00029272200099577484 | 0.00025159627109681853 | true | true | **STABLE** |
| `ALIGNED_rho0.55` | audit meter tracks designed b-share | 0.0 | 0.00016549848735816327 | 0.00012664842601441408 | false | false | **STABLE** |

Both of V-4's razor-thin calls survive the 10× recheck: the endpoints at B = 20 000 are
[−0.00025159627109682547, +0.018755579320116268] and [+0.0001686069063876472,
+0.010874315652222745]. **The 5/8 count is not a Monte-Carlo artifact.**

**Rule-16 enumeration, the registered 2⁴ subtable** (81-row full table with BOUNDARY in
`part0_enumeration_routing.csv`; all four routes reachable there — P1L 27, P3L 24, P4L 16,
P2L 14):

| V-1 | V-2 | V-3 | V-4 | misses | route |
|---|---|---|---|---:|---|
| HOLD | HOLD | HOLD | HOLD | 0 | **P4L** |
| HOLD | HOLD | HOLD | MISS | 1 | **P3L** |
| HOLD | HOLD | MISS | HOLD | 1 | **P3L** |
| **HOLD** | **HOLD** | **MISS** | **MISS** | **2** | **P2L ← realized** |
| HOLD | MISS | HOLD | HOLD | 1 | **P3L** |
| HOLD | MISS | HOLD | MISS | 2 | **P2L** |
| HOLD | MISS | MISS | HOLD | 2 | **P2L** |
| HOLD | MISS | MISS | MISS | 3 | **P2L** |
| MISS | HOLD | HOLD | HOLD | 1 | **P1L** |
| MISS | HOLD | HOLD | MISS | 2 | **P1L** |
| MISS | HOLD | MISS | HOLD | 2 | **P1L** |
| MISS | HOLD | MISS | MISS | 3 | **P1L** |
| MISS | MISS | HOLD | HOLD | 2 | **P1L** |
| MISS | MISS | HOLD | MISS | 3 | **P1L** |
| MISS | MISS | MISS | HOLD | 3 | **P1L** |
| MISS | MISS | MISS | MISS | 4 | **P1L** |

### 2.8 ROUTING — **P2L**

    V-1 HOLD · V-2 HOLD · V-3 MISS · V-4 MISS  →  two of {V-2, V-3, V-4} MISS  →  P2L

**P2L: appendix P's measurable shadows fail — the R-theorems keep their proofs but lose two of
their claimed instrument shadows; a theory-repair note is owed before any L2.**

**Verdict slug:** `SHADOWS_FAIL__V1HV2HV3MV4M__P2L`

**Routing robustness:** the route is P2L under the registered readings and *also* under both
declared second readings (V-2 scored on the instrument prediction → 3 misses → P2L; V-4 scored
on the contiguous-only meter → still 5/8 → MISS). No reading available in Part 0 routes this leg
anywhere else.

## Part 3 — defects, anomalies, and the brief to the planner

### 3.1 Registration defects (recorded, not repaired)

- **#27 — G2L's band clause and V-1's bar are jointly unsatisfiable on the ISO arm (PROVED).**
  Because ρ_id ties σ_b to Δ, the identity-only boundary z is Δ-free (ISO 5.65685/√(ρ/(1−ρ)),
  ALIGNED 1.41421/√(ρ/(1−ρ))), so the ISO arm's identity-only per-boundary error never exceeds
  5.45e-4 on the registered grid. No Δ can put the ISO ρ_id = .35 cell inside (0.05, 0.95)
  without pushing the ρ_id = 0 cell below 0.95. Realized exactly: pilot ISO mid cells 0.98958
  and 0.97278, both failing the band **from above**, both unsaturated. Handled by RN-10's
  pre-declared guard; disclosed, not repaired. *Lesson for L2: state the realizability target on
  the arm the theory says is the hard one (here ALIGNED), never on the arm it says is immune.*
- **#28 — V-3(d) is a designed identity, not a test.** Subtracting the generator's b from the
  card reproduces the ρ_id = 0 card exactly (residual 3.12e-16), so "oracle REMOVAL restores both
  to ARI ≥ 0.95" is the ρ_id = 0 cell's own number by construction. It is a valid construction
  certificate and a vacuous theory clause — the K1b Ŝ ≡ 1 pattern, caught prospectively this time.
- **#29 — the floor clause had no registered comparand.** "The ALIGNED cells' error consistent
  with the floor prediction" is unsatisfiable if "error" means the noisy PRIMARY's error, because
  the floor is a strict lower bound on it. RN-7 pinned the only reading under which the clause is
  a test — the per-boundary misassignment rate of the **noise-free TRUE cards** — before arms.
  Under that reading it is a sharp test and it nearly passes (1/2 cells, the second missing by
  0.0019).
- **#30 — V-3(c)'s bar mixes two different quantities.** R2's (k_τ/m) factor is an **energy**
  statement about the k-means objective; ARI at these separations is governed by the
  **boundary-normal Bayes error**, which projection provably cannot change because the boundary
  normal lies inside S. A "≥ half the deficit" bar on ARI therefore tests a proposition R2 does
  not make. This was derived and written into Part 0 §0.6 with a predicted value
  (0.1527) before the arms ran; the measured value is 0.1347.

### 3.2 Anomalies, all with timing

- **(i)** A **pure-algebra prototype** of the R2 card geometry (0.276 s) and a **synthetic-law
  prototype** of the instruments (24.4 s) were run in the scratch directory **before** the leg
  script existed. Neither generated a world of any index — no `build_world` call, no pilot
  index, no main index; both drew from their own prediction-only streams. Their only role was to
  establish the Δ-free floor identity and to confirm that a batched Lloyd converges on this card
  law. **No main-world number existed at any point before Part 0 was written to disk.**
- **(ii)** A **construction smoke** of the leg's own code path (0.026 s) ran on RESERVED pilot
  world 9901 at 128 authors, checking shapes, the reconstruction, one k-means call and the audit
  meter. Pilot indices only; before Part 0 was written; disclosed here rather than in Part 0
  because it is a construction check of the kind G0L/G1L own.
- **(iii)** The first `--stage part0` invocation **crashed after 22.3 s** with a
  `TypeError: measure_cell_world() missing 1 required positional argument` — Δ was omitted at
  two call sites. Fixed (both sites), re-run from scratch. The crash occurred **inside the pilot
  loop, before any gate value was written**, so no number survived it; the Part-0 artifacts are
  from the single clean run at 2026-08-09T15:15:38Z.
- **(iv)** The audit columns of the **companion** cells (`*_removal`, `*_projection`) are **not
  meaningful**: `cards_for_variant` applies the removal/projection to the cards but leaves the
  `b_card` reference unprojected, so those cells' "designed b-share" is computed against a
  transformed denominator (visible as `audit_share_b_design` = 4.57 for
  `ISO_rho0.55_projection`). **No lean reads them** — V-4 scores only the 10 main cells — but
  they are in `cells.csv` and are flagged here so no later reader mistakes them for measurements.
- **(v)** `eigengap_ratio` for the two projection companions is ~1e31 — the projected cards are
  exactly rank 3, so the 4th eigenvalue is at machine zero. Expected; reported.
- **(vi)** The realized ρ_id deviates from the designed value by up to 0.0173 (ALIGNED), against a
  tolerance of 0.02. This is the geometry's own sampling fact — the ALIGNED identity energy is
  carried by 3 latent dimensions, giving relative sd √(2/3)/√512 = 3.6% on σ_b² — not a
  construction error. It was inside the tolerance pinned in G0L before the arms ran.

### 3.3 Total compute and the budget

Adjudicated compute **51.62 s** (Part 0 29.845 + arms 12.933 + finalize 0.074 + post-hoc 6.768),
plus 22.3 s for the crashed first Part-0 attempt and 24.7 s of pure-algebra prototyping.
Every stage came in under its Part-0 estimate; the 2× stop threshold was never approached.
Target was < 25 min; total wall time across all stages was **under 2 minutes**.

### 3.4 The brief to the planner

**What the instrument does deliver, and should be reused in L2.** The typed world works. G0L is
clean to machine precision, the K2a anchor is bit-exact, the two geometries are exactly paired,
the ρ_id = 0 arms are bit-identical panels, oracle removal is an exact identity, and the
**measured ARI ordering across all 10 cells reproduces the Part-0 prediction cell for cell**.
Three of R2/R3/R4's shadows are measured and strong:

- **R4, the identity tax, is real and quantified:** ISO loses 0.0995 of ARI across the ρ_id
  sweep; ALIGNED loses 0.8103 — a factor of 8.1 at matched total identity energy.
- **R2's dichotomy is measured at full strength:** pooled ALIGNED − ISO = **−0.4129**, CI
  [−0.4305, −0.3953]; at ρ_id = .55 alone, −0.5459.
- **R2's ALIGNED floor formula Φ(−Δ/(2σ_{b,u})) is a real predictor:** the noise-free
  per-boundary rate reads 0.027751 against a predicted 0.027119 at ρ_id = .35, and 0.107422
  against 0.100683 at ρ_id = .55 — 2.3% and 6.7% relative, one inside its CI.
- **R3's audit is a working meter:** it reads the b-share to within 0.0028–0.0109 across a share
  range of 0 → 0.50, with an offset whose whole source is identified (B̂ = 0.245861 vs 0.25).

**What failed, and what the failure means.**

1. **The ISO projection-gain shadow does not exist at the ARI level (V-3c).** Not at ρ_id = .55
   (fraction 0.1347), and not at ρ_id = .75 where R2's ambient energy condition is violated
   (fraction 0.1495 — flat). The theorem is not contradicted: R2's m/k_τ factor is about the
   energy that pollutes the *k*-means objective, and Lloyd with 64 restarts is already
   essentially Bayes-optimal on this card law, so there is no objective-pollution loss left for
   projection to recover. What projection cannot do — and R2 never claimed it could — is change
   the boundary-normal variance, and that is what ARI is made of here. **The repair is to
   re-state the ISO half of R2 with its estimand named: the SNR gain m/k_τ is a statement about
   the consistency THRESHOLD (whether a distance grouper can be consistent at all), not about
   achieved ARI above that threshold.** An L2 test of the ISO half must therefore run at
   separations near the threshold, where ambient Lloyd actually breaks — which in this
   parameterization means ρ_id well above 0.75, or an independent σ_b knob decoupled from Δ.
2. **The completeness audit needs one calibration constant (V-4).** The meter is unbiased in
   structure and biased by a constant +0.002754 in the numerator, traced entirely to the realized
   two-split state coefficient B̂ = 0.245861 against a design 0.25 (−1.66%). Both readings of the
   meter miss 6/8 by the same margin with opposite sign, which is the signature of an
   estimator-scale issue, not of a broken audit. **Two candidate repairs for L2, both cheap:**
   (a) estimate B̂ per world rather than pooled, so its error enters as noise rather than bias;
   (b) declare the meter's target as the *bias-corrected* share with the B̂ error propagated into
   the CI. Either would move the tracking count from 5/8 to (on these numbers) 8/8.
3. **Δ and ρ_id must be decoupled in L2.** Tying σ_b² to Δ through ρ_id is what made the ISO arm
   immune at every Δ and produced defect #27. An L2 grid should sweep σ_b at fixed Δ *and* Δ at
   fixed σ_b, so the consistency threshold can be crossed rather than assumed away.

**What P2L means for the line.** R1, R2 and R3 keep their proofs. What this leg removes is the
claim that R2's ISO half and R3's audit come with *ready* instrument shadows: the first needs its
estimand re-stated, the second needs one calibration constant. The taxometric question L2 was to
open — deciding ISO vs ALIGNED on an unknown-geometry world — is **not** damaged by either
finding; if anything it is strengthened, because the discriminating signal (the ALIGNED floor and
the 8.1× tax) is exactly the part that measured cleanly.
