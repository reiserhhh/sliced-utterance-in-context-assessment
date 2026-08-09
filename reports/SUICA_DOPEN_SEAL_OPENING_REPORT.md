# SUICA D-open — opening prospective seal #2: do the measured laws PREDICT?

Banner: **synthetic worlds calibrated to an opened-panel regime, exploratory; this leg MEASURES FIRST and UNSEALS SECOND**

Registration: `docs/SUICA_DEFENSE_PHASE_PLAN.md` section "D-open — Opening prospective seal #2" (REGISTERED 2026-08-10, BEFORE RUN, commit `f0e89b9`), together with D1's committed opening protocol (`reports/SUICA_D1_PROSPECTIVE_SEAL_REPORT.md`, "Opening protocol", commit `4dad82e`). Charter: `docs/SUICA_DEFENSE_PHASE_CHARTER.md`. Executor standing: implementation and execution only; the registration text is binding.

**The product of this leg is the ORDERING, not the score.** Everything in Part 1 was measured, written to disk and hashed before a single byte of `results/d1_sealed/D1_SEALED_BUNDLE.json` was read. That claim is enforced in code (Part 0.3) and attested with timestamps (Part 1.0).

Part 0 written at `2026-08-10T05:33:00Z` — BEFORE Stage 1.

---

## Part 0.1 — Anchors (G0O)

| anchor | value / path |
|---|---|
| D1 committed hash (salted) | `3a1971b827210b7f3611b4769496f9d55d4ea815b6b8b577cae81f64b1fe00f8` |
| public hash record | `results/d1_sealed/D1_PUBLIC_HASH.json` (`sealed_utc` 2026-08-09T17:41:45.071110+00:00) |
| sealed bundle | `results/d1_sealed/D1_SEALED_BUNDLE.json` (20 205 bytes, gitignored) |
| hash construction | `sha256((salt + json.dumps(predictions, sort_keys=True)).encode()).hexdigest()`; salt lives INSIDE the bundle |
| D2 fragility annex | `docs/SUICA_IDENTITY_THEORY_V1.md` dated appendix T — **binds interpretation, may not move any band** |
| master seed | `20260825` (registration G3O); `B = 2000`, `B_high = 20000` |

**Machinery reuse (rule 12), by source object.** Every measurement runs the published leg functions **unmodified**:

| measurement | source objects |
|---|---|
| M-1 / M-2 | `scripts/run_suica_m4_l2_threshold_continuum.py` — `build_typed_world_l2`, `cards_for_cell`, `measure_cell_world`, `predicted_boundary_error_l2`; through them `scripts/run_suica_m4_l1_typed_world.py` — `latent_type_vectors`, `kmeans_lloyd`, `boundary_error_rate`, `adjusted_rand_index`, `identity_only_z`; and `scripts/run_suica_m4_k2a_expressive_world.py` — `build_world`, `card`, `centered_channels`, `arm_weights` |
| M-3 | `scripts/run_suica_m4_l2_threshold_continuum.py` — `pred_population_l2`, `pred_instruments`, `pred_floor_closed_form`, `ladder_grid`, `solve_ladder`, `joint_satisfiability` |
| M-4 | `scripts/run_suica_m4_k2b_t4_branch.py` — `arm_weights`, `world_seed_for`, `build_k2b_world`, `run_field_world`; law inputs from `run_suica_m4_k2c_matched_pairs.predicted_attenuation` and `run_suica_m4_k2e_double_matching.person_share_design` |
| M-5 | `scripts/run_suica_m4_l3_taxometer_meter.py` — `world_seed_for`, `measure_cell_world`, `taxometer` (PRIMARY route `eta_hat_P`) |

Only the reused modules' **registration-fixed dimension constants** move, by RN-DO-1/RN-DO-2 below, inside a context manager that restores every one of them on exit. No function body is edited, copied or forked. `suica_core/` is untouched.

## Part 0.2 — The configuration table and the rule-9 pins (fixed BEFORE Stage 1)

| # | registered configuration | as executed |
|---|---|---|
| **M-1** | L1 machinery at m=96, k_τ=4, G=5, n_occ=8, ρ.55-equivalent energy; η ∈ {0, 0.5, 1}; measured per-boundary error rates (true-card); 8 worlds × 512 authors | Δ = `5.928950380606693`, σ_b² = `16.111540782194115`, DIM = 128, w_int = zero, φ_slow = 0.90; measured object = `boundary_err_true_card` = `l1.boundary_error_rate(true_card, centroids, group)`, the same field L2's W-3 and L3 read |
| **M-2** | same config, ISO vs ALIGNED at matched identity energy: floor ratio and ARI-drop direction | ISO = η 0, ALIGNED = η 1, identical σ_b² and identical worlds (exactly paired) |
| **M-3** | T-arm ladder at (m=48, n=512) and (m=192, n=256) | L2's own grid `geomspace(0.75, 9.0, 34)`, 6 prediction replicates, σ_b² = ρ.55-eq, η = 0, k_τ = 3, G = 4; DIM 64 / 256 |
| **M-4** | K2b instrument, one new arm (share .40, φ .90), 32 worlds | `k2b.arm_weights(0.40, "zero")`, worlds 0…31 via `k2b.world_seed_for`; measured object = `recovery_b_only` |
| **M-5** | L3 taxometer at η = 0.6, ρ.45-equivalent | L3's own G=4 / k_τ=3 / m=48 / 8 worlds × 512; measured object = `eta_hat_P` (PRIMARY route) |

**RN-DO-1 (rule 9) — the DIMENSION TRANSPORT.** k2a's generator constants are *functions* of `(K_LATENT, DIM)`: `G_PROFILE = linspace(0.85, 0.55, K_LATENT)` (k2a:91), `A_SCALE = sqrt(2/Σ G_PROFILE²)` (k2a:92), `SIGMA_ISO = sqrt(2/DIM)` (k2a:93), and `loadings = _orthonormal_loadings(rng, DIM, K_LATENT)` which **requires DIM ≥ m** (96 orthonormal columns do not fit in R⁶⁴). `DIM = 64` is therefore *unrealizable* at m ∈ {96, 192}; this is a mechanical fact about the published generator, not a choice. The transport that leaves every published FORMULA untouched carries the family's own design ratio: **DIM(m) = 4m/3** → 64 / 128 / 256 at m = 48 / 96 / 192. At m = 48 it reproduces k2a/L1/L2/L3 exactly, which is checked in Part 0.4.

**RN-DO-2 (rule 9) — the SIMPLEX GENERALIZATION.** `l1.TETRAHEDRON` (l1:191-193) is the G=4 regular simplex in R³ at unit pairwise separation, with `SIGMA_TAU2_PER_DELTA2 = 3/8` (l1:194). The general object is the regular (G−1)-simplex — the G standard basis vectors of Rᴳ, centred, scaled to unit pairwise separation, expressed in an orthonormal basis of the all-ones complement — for which `σ_τ²/Δ² = (G−1)/(2G)` exactly: 3/8 at G=4 (l1's own constant, verified) and 0.4 at G=5 (exactly D1's `c_5` in RN-D1-4). Only a rotation separates the construction from `l1.TETRAHEDRON`, and the type frame `S` is a random frame, so the rotation is immaterial.

**RN-DO-3 (rule 9) — the ρ-equivalent energies.** L2's term of art (l2:124-129): `σ_b²(ρ-eq) = (3/8)·L1_DELTA²·ρ/(1−ρ)`, a fixed NUMBER decoupled from Δ. Hence ρ.45-eq = `L1_SIGMA_TAU2 · 0.45/0.55`, computed at run time from `l2.L1_SIGMA_TAU2`.

**RN-DO-4 (rule 9) — "ρ.55-equivalent at m=96", the PRIMARY reading, PINNED NOW.** D1's own RN-D1-1/2 fixes it: the PRIMARY transports `σ_b² = SB2_RHO55 = 16.111540782194115` and `Δ = L1_DELTA` **unchanged** to the new (m, k_τ), and the Δ-free `ρ_id = 0.55` form at G=5's own `c_5 = 0.4` is a **NAMED COMPANION that cannot be promoted at opening time**. This leg MEASURES BOTH (the companion costs three more cells) and **scores on the PRIMARY**. If the bundle at opening reveals an ambiguity in which reading its S-1 config names, both readings are reported and the score stands on the pinned PRIMARY.

**RN-DO-5 (rule 9) — S-3's `d` and the window.** `d` = the LATENT dimension `m` (D1's RN-D1-5), so γ = 48/512 and 192/256. The window is `[oracle-S > 0.80 edge, ambient < 0.30 edge]`, both read off L2's own `joint_satisfiability` clause intervals — the identical fields whose baseline values D1's provenance table cites (`G2M/rule18_joint/clause_delta_intervals/W-1a (…)`). Width = upper − lower; OPEN iff the intersection is non-empty on the grid.

**RN-DO-6 (rule 9) — what S-2's "floor ratio" MEASURES.** S-2 is EXACT ALGEBRA with a `1e-12` algebraic tolerance and no numeric band (D1 Part 0.4, RN-D1-9). Its measured content is therefore three things: (i) the **latent z-ratio** evaluated through the published source object `l1.identity_only_z` at dims = m and dims = k_τ, which must reproduce `√(m/k_τ) = √24` to 1e-12 and be ρ-free; (ii) the **ARI-drop direction**, ISO(η=0) minus ALIGNED(η=1), measured on exactly paired worlds; (iii) the **strict η-ordering** of the measured rates. The card-space *realized* z-ratio (which the non-isometry of M perturbs away from √24) is measured and reported as a **disclosed companion**, never as the scored quantity.

**RN-DO-7 (rule 9) — the routing reading.** "≥4/5 PREDICTED (S-3 counted separately)" admits two readings. **PRIMARY (registration-literal):** ≥4 PREDICTED among all five entries. **DECLARED SECOND:** S-3 excluded from the numerator, so the bar is all four measured-law entries. Both are computed for every one of the 243 enumerated outcomes (Part 0.6); both are reported.

**Integrity disclosure (rule 9, made before Stage 1).** S-1's, S-2's and S-3's formulas, their constants and their configurations are all PUBLISHED in the committed D1 report (Part 0.2 discloses that two of S-3's four baseline edges are literally provenance-table rows). Their predicted values are therefore derivable by anyone from the committed record; the seal's force is not the executor's ignorance but the fact that the values were **committed before the configurations were run**, and that the measurements have **no free parameter to tune** — they are simulations of published machinery at a fixed seed. This executor did not read `scripts/run_suica_d1_prospective_seal.py`, did not evaluate any sealed formula, and persisted no predicted value before the Stage-1 stamp. What is genuinely unknown to Stage 1 and decides four of the five cells is the **bands**, which are derived from persisted records the report never quotes.

## Part 0.3 — G1O: the ordering enforcement, designed before Stage 1

The registration: *the script hashes `measured.json` and records its timestamp BEFORE its first read of the bundle; any earlier access to that path is a defect → STOP.*

Enforcement, not assertion:

1. **A process-wide path guard.** `builtins.open`, `io.open`, `os.open`, `pathlib.Path.open`, `Path.read_text` and `Path.read_bytes` are all wrapped at process start (`install_guard()`, before any subcommand runs). Every call whose target resolves to the bundle path is checked against a permit flag; without the permit the call raises `SystemExit` and the refusal is written to the append-only ordering log. Six entry points are covered because one is not enough: `json.load` uses `builtins.open` via its caller, `pandas` uses `io.open`, and a `Path.read_text` would bypass a `builtins.open`-only guard.
2. **The permit has exactly one issuer.** `grant_permit()` is called only by `stage2`, and refuses unless (a) `measured.json` and `measured.sha256.json` both exist, (b) re-hashing `measured.json` from disk reproduces the stamped SHA-256 bit-exactly — so the measurements cannot be edited after the stamp — and (c) the stamp's timestamp is strictly in the past.
3. **Stage 1 cannot run after the stamp.** `stage1` and `seal` both refuse if the stamp already exists. The ordering is therefore a one-way door in both directions.
4. **An append-only ordering log** (`results/dopen_seal_opening/ordering_log.jsonl`) records every process start, task start/finish, the stamping event and the first bundle read, each with a UTC timestamp and PID. The guard's own bookkeeping counts bundle accesses; the stamp records that count (`bundle_reads_before_stamp`), which must be 0.

## Part 0.4 — G2O: realizability (rule 17), with the pre-declared fallback

Pilot checks run on RESERVED pilot worlds only (L2's `PILOT_WORLDS` 9901/9902, K2b's 9601, L3's 9901 — all disjoint from the main indices this leg measures), and are reported in Part 0.7 as executed.

| config | realizability bar | pre-declared fallback |
|---|---|---|
| M-1 / M-2 | every measured rate finite; the η ∈ {0.5, 1} cells strictly inside (0, 1); realized σ_b² and realized η match the design; the closed-form z route agrees with `predicted_boundary_error_l2` to machine precision | any non-finite or saturated informative cell → **S-1 UNRESOLVABLE (named)**, never re-designed |
| M-1 η = 0 | **expected to measure exactly 0** and NOT a realizability failure: at m = 96 the identity-only floor is ~1e-13, and D1's sealed band rule already provides an ABSOLUTE band for cells whose predicted rate is ≤ 1e-06 (D1 Part 0.4, RN-D1-6; L2 measured exactly 0.0 at both its own η=0 cells) | — (pre-covered by the sealed band) |
| M-3 | both clause sets non-empty on the FIXED grid `geomspace(0.75, 9.0, 34)` | an empty clause set at a setting → that setting's edge is undefined → **S-3 UNRESOLVABLE (named)**; the grid is NEVER extended or moved |
| M-4 | `recovery_b_only` finite and strictly inside (0, 1); k2b's own G4b route residuals ≈ 0 | non-finite or saturated → **S-4 UNRESOLVABLE (named)** |
| M-5 | `eta_hat_P` finite; bootstrap CI half-width ≤ L3's own G1N bar 0.3 | otherwise → **S-5 UNRESOLVABLE (named)** |

Additionally verified in Part 0.7: DIM(48) = 64 reproduces k2a's own constant, and the G=4 instance of RN-DO-2's simplex reproduces `l1.SIGMA_TAU2_PER_DELTA2 = 3/8`.

## Part 0.5 — G3O: satisfiability with DIRECTIONS, SIDES and STAGES (rules 11/13/18/22/23)

The bands are sealed, so rule-11/18 satisfiability cannot be checked against band NUMBERS. What is checked — and what the rules actually require — is that each clause **can do its job** (rule 23) and that both of its outcomes are reachable (rule 11), jointly across clauses sharing knobs (rule 18).

| entry | clause | sides (rule 22) | improvement lies | stage its inputs exist (rule 23) | both cells reachable? |
|---|---|---|---|---|---|
| S-1 | measured rate inside the sealed relative band (absolute band on the degenerate cell) | two-sided | at the sealed value | Stage 1 for the measurement; Stage 2 for the band | yes — a rate is free in [0,1] and the band is a finite interval |
| S-2 | (i) algebraic ratio ≡ √24 within 1e-12; (ii) ARI drop > 0; (iii) rates strictly increasing in η | (i) two-sided; (ii)/(iii) **one-sided** | (ii) larger drop; (iii) stricter ordering | Stage 1 | yes — the drop can be negative and the ordering can invert |
| S-3 | edges inside interval bands + the binary OPEN/EMPTY call | two-sided on the edges; categorical on the call | at the sealed edges | Stage 1 | yes — plus UNRESOLVABLE if a clause set is empty |
| S-4 | recovery inside the sealed absolute band | two-sided | at the sealed value | Stage 1 | yes |
| S-5 | η̂ inside the sealed absolute band | two-sided | at η = 0.6 | Stage 1 | yes |

**Rule 18 (joint).** S-1 and S-2 share generative knobs (identical worlds, identical cells at m=96). Their clauses are jointly satisfiable by construction: S-1 constrains three rate LEVELS, S-2 constrains an ORDER among the same three plus a paired ARI contrast; a level assignment inside any band can carry any order, so no pair of clauses is empty by design. S-3, S-4 and S-5 sit on disjoint configurations and share no knob with each other or with S-1/S-2. This is verified numerically on the pilots in Part 0.7.

**Rule 13.** Every interval in this report is a paired **world-block** bootstrap at `B = 2000`, `seed = 20260825` (L3's PN-8 construction, `_boot_index`). Cells are assigned on POINT estimates against the sealed bands — the registration's cells are `{PREDICTED, MISSED, UNRESOLVABLE}` with no BOUNDARY cell — so the bootstrap does not decide any cell. Where a sealed band edge falls inside a B=2000 CI, the CI is re-run at `B = 20000` and the stability is reported.

## Part 0.6 — G4O: rule-16 enumeration (5 entries × 3 cells + routing)

The adjudication space is `{PREDICTED, MISSED, UNRESOLVABLE}⁵ = 243` outcomes, each routed to exactly one verdict under BOTH readings of RN-DO-7, plus S-3's own three-state sub-verdict (`CONJECTURE-SUPPORTED` / `CONJECTURE-DEAD` / `CONJECTURE-UNRESOLVED`). The table is built in code (`build_enumeration`), written to `results/dopen_seal_opening/part0_enumeration.csv`, and audited for no-gap/no-overlap (rows = expected = unique keys, every row routed). The audit is reported in Part 0.7.

## Part 0.7 — Part-0 results (appended after `part0` ran, still before Stage 1)

`part0` ran in **5.69 s** (`results/dopen_seal_opening/part0_gates.json`). Zero bundle accesses.

**RN-DO-1 transport, verified.** DIM(48)=64 (= k2a's own `DIM`, so the m=48 setting reproduces the published leg exactly), DIM(96)=128, DIM(192)=256; ratio 4/3 at all three; `DIM ≥ m` at all three, and `DIM = 64` is infeasible at both 96 and 192 — the transport is forced, not chosen.

**RN-DO-2 simplex, verified.** G=4: shape (4,3), pairwise separation deviates from 1 by ≤ `2.22e-16`, `σ_τ²/Δ² = 0.3750000000000001` — matches `l1.SIGMA_TAU2_PER_DELTA2 = 3/8`. G=5: shape (5,4), pairwise deviation ≤ `2.22e-16`, `σ_τ²/Δ² = 0.4` = the closed form `(G−1)/(2G)` = D1's own `c_5`. Both centroids at the origin to 1e-17.

**RN-DO-8 — a REAL defect in the published machinery, found by the Part-0 realizability check and disclosed (executor-attributed).** The first pilot run CRASHED with `IndexError: index -4632847432226133644 is out of bounds for axis 0 with size 5`. Cause: `l2.type_geometry_l2` (l2:220-224, and identically `l1.type_geometry` at l1:239-243) allocates the group label vector with `np.empty(n_authors, dtype=int)` and then fills exactly `G · (n // G)` entries. At G=4 with n=512 that is all of them, so L1/L2/L3 were never exposed; at **G=5 with n=512 the last two authors keep UNINITIALIZED MEMORY as their type label**. There is no guard in the published function. The registered "512 authors" is therefore realized as **n = 510 = 5 × 102**, the largest multiple of G not exceeding it (−0.39 %), and the harness now refuses any `n % G ≠ 0` outright. Had the crash not fired on a garbage index, the run would have silently mislabelled two authors.

**G2O realizability pilots — all PASS** (reserved pilot worlds only; L2 9901/9902, K2b 9601, L3 9901):

| config | pilot readings | verdict |
|---|---|---|
| M-1/M-2 (m=96, k_τ=4, G=5) | measured true-card rates η=0 / 0.5 / 1 = `0.0` / `0.021813725490196077` / `0.06862745098039216`; latent-law rates `2.30592514626126e-13` / `0.02034245439037237` / `0.06982469930521468`; ambient ARI `0.9707` / `0.7154` / `0.4913`; realized σ_b² `16.049363302856463` vs designed `16.111540782194115`; realized-η max deviation `0.0035091764232071387`; **closed-form z route vs `predicted_boundary_error_l2`: residual `0.0`** | PASS — η∈{0.5,1} strictly inside (0,1); η=0 measures exactly 0 as anticipated and is pre-covered by the sealed absolute band |
| M-3 | (48,512): card (512,64), γ=`0.09375`, √γ=`0.30618621784789724`. (192,256): card (256,256), γ=`0.75`, √γ=`0.8660254037844386`. All finite; orthonormal loadings feasible at both | PASS (the grid itself is the remaining check) |
| M-4 (share .40, φ .90) | `recovery_b_only` = `0.10409693427090781`, `recovery_mixed` = `0.20333734955992372`; K2b's own G4b residuals `0.0` (reconstruction and b-only-truth route); realized shares noise `0.7004`, slow `0.1196`, μ `0.0904`, common `0.0896`, int `0.0` | PASS — finite, non-saturated, the designed budget realized |
| M-5 (η=0.6, ρ.45-eq) | σ_b² = `10.785411597997713`; `eta_hat_P` = `0.426630964439929`; realized η `0.6176480801838466`; realized σ_b² `11.067920069314205`; whitener condition `2.7907811490613823` | PASS on realizability (finite, well-conditioned). **Flagged, not acted on:** this single pilot world reads 0.173 below η, i.e. outside L3's certified ±0.125 — a pilot is one world and the arm is eight, and NOTHING may be re-designed on it |

**Rule-18 joint check on the pilot.** At the m=96 config, S-1's three rate levels and S-2's two order clauses hold *simultaneously* on the pilot (rates strictly increasing in η, ambient ARI strictly decreasing) — the shared-knob pair is jointly satisfiable in fact, not only by argument.

**G4O enumeration — PASS.** 243 rows = 3⁵ expected = 243 unique keys; every row routed under both readings. Reading A (primary) yields `LAWS-PREDICT` in **11 / 243** outcomes, reading B in **3 / 243**; the two readings agree on **235 / 243**. Written to `results/dopen_seal_opening/part0_enumeration.csv`.

**Stage estimates (the stop-and-report clock starts here; 2× any estimate ⇒ stop).** m1m2 ≈ 60 s (pilot 4.0 s for 2 worlds × 3 cells; the run is 8 worlds × 3 cells × 2 energies); m3 (48,512) ≈ 90 s (L2's own Part 0 was 93.6 s and the ladder is its bulk); m3 (192,256) ≈ 270 s (the heavy cell: 256-dim cards at n=256); m4 ≈ 60 s (pilot 1.05 s/world × 32); m5 ≈ 15 s (pilot 0.24 s/world × 8). Total ≈ 8 min against the < 40 min leg target.

---

## Part 1 — STAGE 1: the measured table (written BEFORE any unsealing)

### Part 1.0 — G1O ordering attestation

| event | UTC | evidence |
|---|---|---|
| Part 0 written into this report | `2026-08-10T05:33Z` (report edit), `part0` run `2026-08-09T19:15:20.035298+00:00` | `results/dopen_seal_opening/part0_gates.json` |
| Stage-1 tasks | `19:16:33.688787` → `19:19:16.035988` (five tasks, five processes) | `ordering_log.jsonl` |
| **`measured.json` stamped** | **`2026-08-09T19:19:41.985528+00:00`** | `measured.sha256.json` |
| `measured.json` SHA-256 | **`ee6d45a39261aa4f037b3c9260aae9785300f436111eda9b173456cfc4c3c42c`** (30 835 bytes) | re-hashed from disk at Stage 2 |
| bundle accesses BEFORE the stamp | **0** | guard counter recorded in the stamp; no `BUNDLE_ACCESS_REFUSED` event in the log |
| first read of `D1_SEALED_BUNDLE.json` | see Part 2 | `ordering_log.jsonl` event `BUNDLE_FIRST_READ` |

Six processes ran before the stamp (3 × `part0` including two that crashed on the RN-DO-8 defect, 5 × `stage1`, 1 × `seal`); each armed the guard at start, and none touched the bundle path.

### Part 1.1 — M-1: per-boundary error rates at m=96, k_τ=4, G=5, n_occ=8, ρ.55-equivalent

PRIMARY reading (RN-DO-4). 8 worlds × 510 authors; CI = paired world-block bootstrap, B=2000, seed 20260825. Measured object = `boundary_err_true_card`.

| η | **measured true-card rate** | 95 % CI | latent-law rate σ_u²(η) route | realized card-space floor | latent z | realized card z |
|---|---|---|---|---|---|---|
| 0.0 | **`0.0`** | [`0.0`, `0.0`] | `2.30592514626126e-13` | `1.024942949378392e-12` | `7.236272269866327` | `7.033193343891702` |
| 0.5 | **`0.01875`** | [`0.015808823529411764`, `0.021815257352941167`] | `0.02034245439037237` | `0.02055872628064893` | `2.0467268770138602` | `2.042346013202552` |
| 1.0 | **`0.07383578431372549`** | [`0.06801317401960785`, `0.0806985294117647`] | `0.06982469930521468` | `0.07002575430907194` | `1.4770978917519928` | `1.4756001212683532` |

Design realization: realized σ_b² = `16.080728949903097` / `16.12332411674643` / `16.108647372431225` against designed `16.111540782194115`; realized η = `−2.0969001156637525e-05` / `0.5012788696576869` / `0.9999999999999999`; card separation Δ_card = `0.4273138821138501` at all three (shared worlds). The independent z route reproduces `predicted_boundary_error_l2` with residual **`0.0`** in every cell.

**NAMED COMPANION** (RN-DO-4; measured, reported, NOT promoted) — the Δ-free ρ_id=0.55 form at `c_5 = 0.4`, σ_b² = `17.18564350100706`: measured rates `0.0` / `0.02254901960784314` / `0.08033088235294117`, latent-law rates `1.2218507490291066e-12` / `0.023754466353304398` / `0.07633069017621516`.

### Part 1.2 — M-2: ISO vs ALIGNED at matched identity energy

| quantity | measured |
|---|---|
| latent z-ratio via `l1.identity_only_z(96, ρ)/l1.identity_only_z(4, ρ)` | `4.898979485566356` (ρ=.15), `4.898979485566357` (ρ=.35), `4.898979485566357` (ρ=.55), `4.898979485566356` (ρ=.75) — **ρ-free** |
| `√(m/k_τ) = √24` | `4.898979485566356`; **max deviation `8.881784197001252e-16`** (bar: 1e-12) |
| latent z²-ratio `m/k_τ` | `24.0` |
| realized card-space z-ratio (disclosed companion, never scored) | `4.7663278611525115`; z²-ratio `22.717901947131196` |
| ambient ARI, ISO (η=0) | `0.9822510634096403` |
| ambient ARI, ALIGNED (η=1) | `0.4527342464753098` |
| **ARI drop (ISO − ALIGNED)** | **`0.5295168169343305`**, CI [`0.50667283487419`, `0.5513040477672718`] — positive, and positive in **8/8** worlds individually |
| η-ordering of the rates, strict | **TRUE** (`0.0` < `0.01875` < `0.07383578431372549`); strict in the latent law too |

### Part 1.3 — M-3: the T-arm ladder at two (m, n) settings

Grid `geomspace(0.75, 9.0, 34)`, 6 prediction replicates, σ_b² = ρ.55-eq, η = 0, k_τ = 3, G = 4. Edges are grid points read off `l2.joint_satisfiability`'s own clause intervals.

| setting | γ = d/n | ambient<0.30 edge (upper) | oracle-S>0.80 edge (lower) | width (upper − lower) | window |
|---|---|---|---|---|---|
| (m=48, n=512) | `0.09375` | **`2.6977587972014083`** | **`4.238555648405859`** | `−1.5407968512044503` | **EMPTY** (0 grid points) |
| (m=192, n=256) | `0.75` | **`3.645968947059166`** | **`3.9311120913133464`** | `−0.2851431442541803` | **EMPTY** (0 grid points) |

**Provenance check, unprompted and exact:** the (48, 512) row reproduces L2's persisted `gates.json` edges **bit-for-bit** (`G2M/rule18_joint/clause_delta_intervals/W-1a (ambient < 0.30)[1]` and `.../W-1a (oracle-S > 0.80)[0]`). The dimension transport at m=48 is the identity, as RN-DO-1 claims.

Two further measured quantities S-3 speaks to:

- **measured ambient-edge scale factor** (192,256)/(48,512) = **`1.351480699772496`**, against the BBP `(γ₂/γ₁)^¼ = 8^¼ =` `1.681792830507429`.
- **the "projection-invariant" oracle-S edge MOVED**: `4.238555648405859` → `3.9311120913133464` (−7.25 %), where the sealed formula's own text asserts it "does NOT scale with (d,n)".

### Part 1.4 — M-4: the K2b gauge arm (share .40, φ .90), 32 worlds

| quantity | measured |
|---|---|
| **b-only field recovery** | **`0.09350089316336324`**, CI [`0.08624502054643839`, `0.10103687186109606`], bootstrap sd `0.003793676124869706`, 32 world blocks |
| mixed recovery | `0.18346775408888327` |
| gap (mixed − b) | `0.08996686092552006` |
| law inputs at this arm (published algebra) | `r = k2c.predicted_attenuation(.40, .90) =` `0.6185853753498524`; `V_person = k2e.person_share_design(.40, 0) =` `0.12000000000000004` |
| K2b's own G4b verify residuals (world 0) | reconstruction `0.0`, b-only-truth route `0.0` |

### Part 1.5 — M-5: the L3 taxometer at η = 0.6, ρ.45-equivalent

σ_b²(ρ.45-eq) = `10.785411597997713`; Δ = L1's; G=4, k_τ=3, m=48; 8 worlds × 512.

| quantity | measured |
|---|---|
| **η̂ (PRIMARY route `eta_hat_P`)** | **`0.595818186104668`**, CI [`0.5543299454861405`, `0.6320209950669875`], sd `0.01945864161302925` |
| per world | `0.48880549669791185`, `0.6043945449280789`, `0.6022532440616013`, `0.5510410495597324`, `0.6821347687805552`, `0.636277426415693`, `0.6276106431565449`, `0.5740283152372263` |
| CI half-width | `0.0388` (realizability bar 0.3 — PASS) |
| spectral route `eta_hat_S` | `0.5964244532474602` |
| true-partition `eta_hat_T` | `0.6340404573443944` |
| oracle whitener `etaw_oracle_P` | `0.5786908533727368` |
| realized η / realized σ_b² | `0.5973666976120386` / `10.712327695864076` |

Stage-1 wall: m1m2 32.6 s, m3 (48,512) 37.3 s, m3 (192,256) 28.2 s, m4 19.4 s, m5 2.7 s — every stage INSIDE its Part-0 estimate; the "heavy cell" was 28.2 s against a 270 s estimate (n=256 halves the author count, which more than pays for the 256-dim cards). No stop-and-report trigger fired.

---

## Part 2 — STAGE 2: the unsealing

### Part 2.1 — the ordering, closed

| event | UTC |
|---|---|
| `measured.json` stamped (end of Stage 1) | `2026-08-09T19:19:41.985528+00:00` |
| unseal permit granted (re-hash of `measured.json` from disk matched the stamp) | `2026-08-09T19:21:08.676361+00:00` |
| **FIRST read of `D1_SEALED_BUNDLE.json` in the whole leg** | **`2026-08-09T19:21:08.676665+00:00`** (`Path.open`, then `io.open` from the same `json.load`) |
| gap, stamp → first read | **+86.691 s** (strictly positive) |

`bundle_reads_before_stamp` recorded in the stamp: **0**. No `BUNDLE_ACCESS_REFUSED` event appears anywhere in `ordering_log.jsonl` — the guard never had to fire, because nothing tried. The scoring run at `19:24:19.214741+00:00` is the second permitted read.

### Part 2.2 — hash verification

- committed (D1 report + `D1_PUBLIC_HASH.json`): `3a1971b827210b7f3611b4769496f9d55d4ea815b6b8b577cae81f64b1fe00f8`
- recomputed `sha256((salt + json.dumps(bundle["predictions"], sort_keys=True)).encode()).hexdigest()`: **identical**
- **VERDICT: `MATCH`.** Not SEAL-TAMPERED. The seal is valid and the five predictions are the ones committed on 2026-08-09T17:41:45Z under registration commit `4dad82e`.
- The salt was recovered **schema-agnostically** — the harness walks every string leaf in the bundle and keeps the one that reproduces the committed hash — so no assumption about D1's field naming entered the verification. It resolved to `/salt` on the first candidate. Bundle top-level keys: `algebra_round_trip`, `banner`, `hash_construction`, `leg`, `opening_protocol`, `predictions`, `protocol`, `provenance_table`, `purity`, `registration`, `salt`, `salt_handling_statement`, `sha256_salted`, `source_object_checks`.

### Part 2.3 — five bit-exact convergences discovered at opening

The Part-0 pins were written without reading the bundle. Opening it shows that five of them landed on D1's own numbers **bit-for-bit**, which is the strongest available evidence that this leg measured the configurations D1 actually sealed:

| pin | measured / re-derived in Stage 1 | sealed in the bundle | residual |
|---|---|---|---|
| RN-DO-4 primary boundary z, η = 0 / 0.5 / 1 | `7.236272269866327` / `2.0467268770138602` / `1.4770978917519928` | identical | `0.0` / `0.0` / `0.0` |
| RN-DO-4 named companion rates | `1.2218507490291066e-12` / `0.023754466353304398` / `0.07633069017621516` | identical (`companion_delta_free_G5_consistent`) | 0 |
| RN-DO-5 baseline edges at (48,512) | `2.6977587972014083`, `4.238555648405859` | identical | 0 |
| M-4 law inputs | `r = 0.6185853753498524`, `V_person = 0.12000000000000004` | identical | 0 |
| RN-DO-3 ρ.45-equivalent energy | `10.785411597997713` | identical (`cell_energy_sigma_b2`) | 0 |

Note in particular that D1's S-1 entry carries **both** readings under exactly the names RN-DO-4 anticipated (`primary` and `companion_delta_free_G5_consistent`), so the ambiguity flagged in Part 0.2 never materialised: the PRIMARY this leg scored on is the PRIMARY D1 sealed.

---

## Part 3 — the scorecard (scored against each entry's OWN sealed band; no re-fitting)

### S-1 — η-floor curve at an unrun config · MEASURED-LAW · **PREDICTED**

Sealed band rule: relative band `0.39261219454719254` (= 2.0 × the worst of L2's seven usable W-3 cells, `0.19630609727359627` at `C_rho55eq_eta0.25`); absolute band `0.001` for cells with predicted rate ≤ 1e-06.

| η | sealed predicted rate | sealed band [lo, hi] | **measured** | inside |
|---|---|---|---|---|
| 0.0 | `2.30592514626126e-13` | `[0.0, 0.001]` (absolute) | **`0.0`** | **YES** |
| 0.5 | `0.02034245439037237` | `[0.012355758729692102, 0.028329150051052635]` (relative) | **`0.01875`** | **YES** |
| 1.0 | `0.06982469930521468` | `[0.042410670877396514, 0.09723872773303284]` (relative) | **`0.07383578431372549`** | **YES** |

3/3 cells inside. **Disclosed:** the η=0 cell sits exactly ON the closed band's lower edge (`0.0`), which is also the physical floor of a rate — it cannot fall below, so this cell is a one-sided test in fact; D1 anticipated exactly this and provided the absolute band for it.

### S-2 — tax ratio at the same unrun config · EXACT-ALGEBRA · **PREDICTED**

| clause | sealed | measured | verdict |
|---|---|---|---|
| z-ratio = √(m/k_τ) | `4.898979485566356`, tolerance `1e-12` | `4.898979485566356`–`4.898979485566357` across ρ ∈ {.15,.35,.55,.75}; **max deviation `8.881784197001252e-16`** | inside, by 3 orders of magnitude; and ρ-free as claimed |
| z²-ratio = m/k_τ | `24.0` | `24.0` | exact |
| direction: ARI strictly DROPS as η rises | ARI(η=1) < ARI(η=0.5) < ARI(η=0) | `0.4527342464753098` < `0.684770144761943` < `0.9822510634096403` | holds; the ISO−ALIGNED drop is `0.5295168169343305`, CI [`0.50667283487419`, `0.5513040477672718`], positive in 8/8 worlds |
| direction: rate strictly INCREASES in η | strict | `0.0` < `0.01875` < `0.07383578431372549` | holds |
| kill condition | any reversal, or ratio outside tolerance | none fired | — |

Disclosed companion (never scored, RN-DO-6): the card-space *realized* z-ratio is `4.7663278611525115` (z² `22.717901947131196`), 2.7 % below √24 — the non-isometry of M, exactly the gap D1's RN-D1-3 predicted would appear and deliberately did not seal.

### S-3 — localization-window widths at two (d/n) settings · CONJECTURE-GRADE · **MISSED**

| setting | quantity | sealed | sealed band | **measured** | inside |
|---|---|---|---|---|---|
| (48, 512) γ=`0.09375` | lower edge (oracle-S>0.80) | `4.238555648405859` | `[0.9103383787438131, 7.566772918067905]` | **`4.238555648405859`** | YES (exact) |
| | upper edge (ambient<0.30) | `2.6977587972014083` | `[0.5794127937449294, 4.816104800657887]` | **`2.6977587972014083`** | YES (exact) |
| | width / **state** | `−1.5407968512044503` / **EMPTY** | — | `−1.5407968512044503` / **EMPTY** | **YES** |
| (192, 256) γ=`0.75` | lower edge | `4.238555648405859` | `[0.9103383787438131, 7.566772918067905]` | **`3.9311120913133464`** | YES |
| | upper edge | `4.537071403571674` | `[0.974452282424502, 8.099690524718845]` | **`3.645968947059166`** | YES |
| | width / **state** | `0.2985157551658153` / **OPEN** | — | `−0.2851431442541803` / **EMPTY** | **NO** |

**The entry's own PRIMARY FALSIFIER — "the BINARY open/empty call at this setting" — fired.** Both edges land inside their bands, but those bands are ±78.5 % relative and cannot discriminate; the binary call carries the information, and it is wrong at (192,256). Two independent components of the sealed formula failed:

- the **ambient scale factor** is measured `1.351480699772496` against the BBP `(γ₂/γ₁)^¼ = 8^¼ =` `1.681792830507429` — the ambient edge moved 35 %, not 68 %;
- the **projection-invariance clause failed**: the sealed formula states the oracle-S / Bayes-ceiling edge "does NOT scale with (d,n)", and it moved from `4.238555648405859` to `3.9311120913133464`, i.e. **`−0.30744355709251225` (−7.25 %)**.

**Disclosed post-hoc companion, which does NOT move the score.** The window is empty at (192,256) by exactly **one grid point** of L2's own 7.8 %-spaced grid: at Δ = `3.645968947059166` the ambient ARI is `0.209501` (< 0.30 ✓) but oracle-S is `0.781037`, `0.019` short of the 0.80 bar (replicate sd `0.016315` over 6 reps, i.e. ≈2.85 SEM); at the next rung Δ = `3.931112` oracle-S is `0.838214` (✓) but ambient is `0.357326` (✗). Read with `np.interp` instead of on the grid — the reading L2 uses for its own fidelity-row prose, l2:876-880 — (192,256) would be **OPEN** with lower edge `3.7405376086352637`, upper edge `3.820534602607675`, width `0.07999699397241145`, i.e. 27 % of the sealed `0.2985157551658153`. **The grid reading governs** and was pinned as RN-DO-5 in Part 0 before Stage 1: it is the reading D1's own baseline edges are quoted from (`clause_delta_intervals`; L2's `np.interp` companions are the different numbers `2.7089840093109245` / `4.139286609186195`, which the bundle does not use). The interpolated reading is adjudication material, not a score. For completeness, at (48,512) the interpolated reading also says EMPTY (width `−1.3131985279123124`), so the disagreement is confined to the conjectured setting.

**S-3 sub-verdict (registration's separate route): `CONJECTURE-DEAD`.** The `(d/n)^¼` window conjecture earns no quantitative support. Per D1's own framing the window lemma itself stands; only the conjecture dies.

### S-4 — variance-tax law at a new state arm · MEASURED-LAW · **MISSED**

| quantity | value |
|---|---|
| sealed prediction `field ≈ λ·r^q − κ·V_person` | **`−0.015116265289181696`** (level term `0.0715280542753713`, tax `κ·V_person = 0.086644319564553`) |
| sealed band (absolute, 2.0 × the 9-pair κ residual record `0.008917886817207595`) | `[−0.03295203892359688, 0.0027195083452334935]`, width `0.01783577363441519` |
| **measured b-only field recovery, 32 worlds** | **`0.09350089316336324`**, CI [`0.08624502054643839`, `0.10103687186109606`] |
| signed distance above the band's upper edge | `+0.09078138481812975` = **5.09 band widths** = 10.18 × the residual record |

The inputs are not at fault: `r` and `V_person` re-derive **bit-exactly** against the sealed values. The whole CI lies above the band. **MISSED, decisively.**

**Adjudication material for the planner (post-hoc, descriptive, no re-fitting).** Evaluating the *same sealed law* at K2b's own six published arms and comparing with K2b's own persisted `recovery_b_only`:

| arm | share | φ | r | V_person | law | measured | law − measured |
|---|---|---|---|---|---|---|---|
| A1 | .02 | .90 | `0.827178` | `0.0060` | `0.118216` | `0.177889` | `−0.059672` |
| A2 | .10 | .90 | `0.784906` | `0.0300` | `0.089537` | `0.150690` | `−0.061153` |
| A3 | .30 | .90 | `0.675892` | `0.0900` | `0.019306` | `0.109623` | `−0.090317` |
| A4 | .50 | .90 | `0.558364` | `0.1500` | `−0.049141` | `0.075439` | `−0.124581` |
| A5 | .30 | .98 | `0.645057` | `0.0900` | `0.012320` | `0.115748` | `−0.103428` |
| A6 | .50 | .98 | `0.519352` | `0.1500` | `−0.056572` | `0.069184` | `−0.125755` |
| **NEW** | **.40** | **.90** | `0.618585` | `0.1200` | `−0.015116` | **`0.093501`** | **`−0.108617`** |

The law under-predicts the measured level at **every one of K2b's own arms**, by −0.060 to −0.126, and the new arm's −0.109 sits squarely inside that family (between A3 and A4). Meanwhile the *measurement* is exactly where K2b's own monotone share curve puts it: `0.093501` lies between A3 (`0.109623`, share .30) and A4 (`0.075439`, share .50), essentially at their midpoint `0.092531`. **Nothing about the new arm is anomalous; what failed is the law's LEVEL.** Two structural observations, verified against the artifacts: (i) κ was fitted **through the origin on within-pair DIFFERENCES** — `results/m4_k2d_frontier_carrier/post_hoc_descriptive.json` rows carry `D` (a within-pair field difference) against `dvar` (the person-variance difference), with `level` as a separate column — so it is a difference coefficient used here to predict a level; (ii) λ and q come from a 19-arm pooled power law across three legs at R² `0.8679753334914586`, whose spread the D2 fragility annex already flags ("q is three numbers"). The annex **binds interpretation and may not move the band**, and it does not rescue the sign: at the annex's 9-pair κ = −0.7146 the prediction is `−0.01422394572462872`, and at q ∈ {1.8327, 1.9338} it is `−0.014419927309595182` / `−0.017843375026999203`. All negative; the measurement is `+0.093501`.

### S-5 — taxometer reading at a new (η, energy) cell · MEASURED-LAW (certified instrument) · **PREDICTED**

| quantity | value |
|---|---|
| sealed prediction | `0.6` |
| sealed band (the certified ±0.125, L3 X-2, 10/10 within) | `[0.475, 0.725]` |
| **measured η̂ (PRIMARY route `eta_hat_P`), 8 worlds** | **`0.595818186104668`**, CI [`0.5543299454861405`, `0.6320209950669875`] |
| absolute error | **`0.004181813895332009`** — 3.3 % of the certified budget |
| sealed cell energy vs measured | `10.785411597997713` = `10.785411597997713` |

The carried pole-bias note (`+O(0.05)` at η = 0, not applied because η = 0.6 is interior) is vindicated: the interior reading is low by `0.0042`, not high by 0.05.

### Rule 13 — stability at ≥10 × B

No cell is decided by a bootstrap (cells are assigned on point estimates against sealed bands), but every interval this report quotes was re-run at `B = 20000`, same seed:

| interval | B=2000 | B=20000 | max endpoint shift |
|---|---|---|---|
| S-1 η=0 | [`0.0`, `0.0`] | [`0.0`, `0.0`] | `0.0` |
| S-1 η=0.5 | [`0.015808823529411764`, `0.021815257352941167`] | [`0.015931372549019607`, `0.021875`] | `0.0001225490196078427` |
| S-1 η=1 | [`0.06801317401960785`, `0.0806985294117647`] | [`0.06795343137254903`, `0.08057598039215687`] | `0.00012254901960782882` |
| S-4 | [`0.08624502054643839`, `0.10103687186109606`] | [`0.08607758563732214`, `0.10086002031210752`] | `0.00017685154898854083` |
| S-5 | [`0.5543299454861405`, `0.6320209950669875`] | [`0.5570138145909715`, `0.6318730640634624`] | `0.0026838691048310936` |

Every shift is orders of magnitude smaller than the distance from any band edge. No cell is near a Monte-Carlo boundary. (S-3's edges are deterministic grid points; its own closeness is a *grid* margin, quantified above, not a bootstrap one.)

### The scorecard and the routing

| entry | grade | cell |
|---|---|---|
| S-1 η-floor curve | MEASURED-LAW | **PREDICTED** |
| S-2 tax ratio | EXACT-ALGEBRA | **PREDICTED** |
| S-3 window widths | CONJECTURE-GRADE | **MISSED** |
| S-4 variance-tax law | MEASURED-LAW | **MISSED** |
| S-5 taxometer | MEASURED-LAW (certified) | **PREDICTED** |

**PREDICTED 3 / MISSED 2 / UNRESOLVABLE 0.**

| routing reading | count | outcome |
|---|---|---|
| **A (PRIMARY, registration-literal ≥4/5 over all five)** | 3/5 | **PER-ENTRY-ADJUDICATION** |
| B (declared second: all four measured-law entries) | 3/4 | **PER-ENTRY-ADJUDICATION** |
| S-3, separately | binary call wrong at (192,256), empty confirmed at (48,512) | **CONJECTURE-DEAD** |

Both readings agree; the routing is not reading-dependent. `LAWS-PREDICT` does **not** fire.

**VERDICT: `PREDICTED_3_2_0__S3_CONJECTURE_DEAD`.**

### What this establishes, stated no more strongly than the evidence

Three of the program's laws predicted, in advance and without re-fitting, quantities at configurations nobody had run: the **η-floor curve** (3/3 cells inside a band derived from L2's own containment record, at a *new* dimension, a *new* k_τ and a *new* G), the **√(m/k_τ) tax ratio** (exact to `8.9e-16` and ρ-free, with both ordering claims holding), and the **certified taxometer** (`0.0042` error against a `0.125` budget at a new η and a new energy). Two failed: the `(d/n)^¼` **window conjecture**, whose cheap-miss status D1 named in advance and which is now dead (with the honest caveat that it misses by one grid step and the interpolated companion would have said OPEN at 27 % of the predicted width), and the **K-line variance-tax law as a LEVEL**, which is off by 5.09 band widths at the new arm — and, as the post-hoc table shows, by a comparable amount at every arm K2b ever ran, so what D-open falsified is the law's absolute calibration rather than anything specific to share .40.

The interpretation, and only the interpretation, is constrained by the D2 fragility annex; no band was moved by it, and none was moved at all.

### Gate status

| gate | status | evidence |
|---|---|---|
| **G0O** anchors | **PASS** | committed hash re-verified (MATCH); machinery reuse by source object (Part 0.1); the (48,512) row reproduces L2's persisted edges bit-for-bit; five bit-exact convergences with the bundle (Part 2.3); the D2 fragility annex cited, binding interpretation, moving no band |
| **G1O** measure-first ordering | **PASS, ENFORCED** | six open entry points wrapped process-wide; permit issued only after re-hashing `measured.json` from disk; `bundle_reads_before_stamp = 0`; stamp `19:19:41.985528Z` → first bundle read `19:21:08.676665Z`, **+86.691 s**; no refusal event ever fired |
| **G2O** realizability (rule 17) | **PASS** | pilots on reserved worlds only, all four configs finite and non-saturated; the pre-declared UNRESOLVABLE fallback was never needed (0 UNRESOLVABLE cells); the η=0 degenerate cell was anticipated by D1's own band rule; **the check earned its keep** by catching RN-DO-8 |
| **G3O** rules 11/13/18/22/23 | **PASS** | directions, sides and stages tabulated in Part 0.5 before Stage 1; joint satisfiability of the shared-knob pair (S-1, S-2) argued and verified on the pilot; `B = 2000`, seed `20260825` throughout; every quoted interval re-run at `B = 20000` with max endpoint shift `0.0027` |
| **G4O** hygiene + rule 16 + rule 24 | **PASS** | 243-row enumeration, no gap / no overlap, both routings total; rule 24 mechanical re-verification of all 193 long decimals in this report against the artifacts — **one error found and corrected before commit** (the companion σ_b² was quoted as `17.185466737795662` from arithmetic; the artifact says `17.18564350100706`) |

---

## Timing and anomalies

Leg wall time: first tool call `2026-08-09T19:13:54Z` → commit; Stage 1 + Stage 2 compute totals `~124 s`. Target was < 40 min; no stop-and-report trigger fired (every stage came in under its Part-0 estimate, the "heavy cell" at 28.2 s against 270 s).

| # | when | anomaly |
|---|---|---|
| A-1 | `t ≈ 0`, before any measurement | The reused leg scripts each load their own dependencies with `importlib`, so `_load(l2)` and `l3().l2()` are DISTINCT module objects. The first pilot re-pinned the wrong copies and crashed in `latent_type_vectors` on a (4,3)·(3,96) shape mismatch. Fixed by resolving the whole L-line through ONE chain rooted at L3; K2b is deliberately left outside it so M-4 runs at K2b's own 48/64. Corrected before any measured value existed. |
| A-2 | `t ≈ 1 min`, Part-0 realizability | **RN-DO-8, a real defect in published machinery.** `l2.type_geometry_l2` (and `l1.type_geometry`) allocate group labels with `np.empty(n, int)` and fill only `G·(n//G)` entries — at G=5, n=512 the last two authors keep uninitialized memory as their type label, and there is no guard. It crashed here on a garbage index (`-4632847432226133644`); at other allocations it would have silently mislabelled two authors. Resolved by realizing the registered "512 authors" as `n = 510 = 5 × 102` (−0.39 %) and refusing any `n % G ≠ 0`. Fixed before any measured value existed. |
| A-3 | Part 0, disclosed pre-emptively | S-1/S-2/S-3's formulas, constants and configs are fully published in the committed D1 report, so their predicted values are derivable from the committed record by anyone. The seal's force is the commit ORDER plus the absence of any tunable parameter in the measurement — not the executor's ignorance. The executor did not read `scripts/run_suica_d1_prospective_seal.py`, evaluated no sealed formula, and persisted no predicted value before the Stage-1 stamp. What was genuinely unknown at Stage 1, and what decides four of five cells, is the BANDS. |
| A-4 | Stage 2, after the hash matched | The scorer's field-name mapping was written after the bundle was opened (the bundle's schema is not published). This cannot re-fit anything: `measured.json` was frozen and hash-stamped 86.7 s earlier and is re-verified against that hash on every scoring run, and the Part-0 mapping table (Part 0.5 / `MAPPING`) fixed which measured quantity answers which sealed entry before Stage 1. Disclosed rather than hidden. |
| A-5 | Stage 2 | The pilot world for M-5 read `eta_hat_P = 0.426630964439929`, outside the certified ±0.125 — flagged in Part 0.7 and deliberately NOT acted on. The 8-world arm reads `0.595818186104668`. A single pilot world is not a measurement; the discipline of not re-designing on it was correct here. |
| A-6 | Stage 2 | S-3's grid-vs-interpolation reading difference reverses the binary call at (192,256). The grid reading was pinned before Stage 1 and is the reading D1's own baseline edges come from, so the score stands on it; both readings are reported in full (Part 3, S-3). |
