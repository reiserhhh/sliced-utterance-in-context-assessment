# SUICA M4-L3 — The taxometer, and the partition-propagated completeness meter

**Tier: EXPLORATORY.** Banner: *synthetic worlds calibrated to an opened-panel
regime, exploratory*. Card space only; the deployed gauge is never invoked.

- **Registration (binding, before run):** `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md`
  section "M4-L3 — The taxometer, and the partition-propagated completeness
  meter", commit `034bf48`.
- **Theory:** `docs/SUICA_IDENTITY_THEORY_V1.md` appendices P, Q and R (R.1 the
  measured η-floor law; R.3 the meter certified on TRUE/GIVEN partitions only,
  its estimated-partition form owed to this leg), plus the L2-charter
  derivation 3 (the bulk-excess route for η̂) and derivation 4 (the same-data
  optimistic bias).
- **Script:** `scripts/run_suica_m4_l3_taxometer_meter.py`.
- **Artifacts:** `results/m4_l3_taxometer_meter/` (gitignored).
- **Standing rule 20 is FIRST APPLIED here**: if the rule-18 joint check finds
  ANY lean's condition-set empty, the leg STOPS before the arms as a
  registration defect (routing P1N).

---

## Part 0 — gates computed 2026-08-09T16:58:15.148600+00:00 (UTC), written to disk BEFORE any main arm

`run_arms()` calls `require_part0()`, which REFUSES to run unless `gates.json`
exists with `part0_all_pass = true` **and** `rule20_stop = false` **and** this
report file exists on disk. Part 0 ran on the RESERVED pilot worlds 9901–9904
and on a prediction-only seed stream; no main world (indices 0–7) existed when
any number below was computed.

**Verdict: all five Part-0 gates PASS. G0N ✓ · G1N ✓ · G2N ✓ · G3N ✓ · G4N ✓.
The rule-20 verdict is NO STOP — every lean's JOINT condition-set is non-empty.**
Total Part-0 compute 207.344 s (anchors 5.061, pilot 11.278, rule-18/20 joint
173.100, predictions 17.893).

### 0.0 Standing-rule-14 self-check (required by G4N)

Every gate and every lean compares card-space quantities to card-space
quantities, and the registration's own rule-14 note for this leg ("η̂-vs-η,
share-vs-share, deviation-vs-ARI — no cross-scale gate") is satisfied literally:

- **X-1** and **X-2** compare **η̂ to η** — the same dimensionless mixture
  fraction on the same `[0,1]` scale.
- **X-3** regresses a normalized variance-**SHARE** deviation on a
  dimensionless partition-agreement **deficit**, and then compares the
  corrected **SHARE** to the designed **SHARE**.
- **X-4** compares a **difference of two shares** to zero.

No gate and no lean crosses scales or instruments. Rule 14 has nothing to bind.

### 0.1 Design as registered, and the register-notes (standing rule 9)

`master_seed 20260824`; 8 worlds × 512 authors per cell; `G = 4` equal groups;
`k_tau = 3`; `m = K_LATENT = 48`, card `DIM = 64`; occasion/state/noise as in
K2a (`phi_slow .90`, `n_occ 8`, `w_int 0`, `N_REP 2`). The grid is fixed
completely by the registration — L2's C-grid at fresh seeds, η ∈ {0, .25, .5,
.75, 1} × two identity energies at L1's Δ — so **there is no ladder to solve and
no adjustment knob in this leg**. 10 cells, card space only.

| symbol | value |
|---|---|
| `Delta` | 5.928950380606693 (L1's) |
| `sigma_b^2` (ρ.35-equivalent) | 7.098091393554051 |
| `sigma_b^2` (ρ.55-equivalent) | 16.111540782194115 |
| `eta` levels | 0, 0.25, 0.5, 0.75, 1 |

M4-L2's leg script is imported as a module and called **UNMODIFIED**
(`type_geometry_l2`, `latent_identity_l2`, `typed_trait_l2`,
`build_typed_world_l2`, `occasion_scheme`, `cards_for_cell`, `audit_meter_l2`,
`estimated_s`, `subspace_overlap`, `predicted_boundary_error_l2`,
`projection_gain`; and `measure_cell_world`/`all_cells`/`world_seed_for` for the
G0N anchor), and transitively M4-L1's typed world (`kmeans_lloyd`,
`spectral_labels`, `adjusted_rand_index`, `hungarian_accuracy`,
`boundary_error_rate`, `latent_type_vectors`, `card_space_type_basis`,
`centred_with_trait`, `_norm_dot`, `group_centre`) and K2a's expressive world.
`suica_core/` is untouched and no file outside the leg script is modified.

**Register-notes (rule 9), all fixed in the script before any number:**

- **PN-1** the ten cells; **PN-2** the world seed (salt `m4l3-world`, disjoint
  from k2a's, L1's and L2's, so no world of this leg coincides with any earlier
  world, and every cross-cell contrast is exactly paired within a world).
- **PN-3** the taxometer uses the FULL-panel canonical splits (interleaved
  {0,2,4,6}/{1,3,5,7}, contiguous {0,1,2,3}/{4,5,6,7}); the METER keeps L2's
  MN-5 cross-fitting inside the audit half. Realized full-panel contrast
  `c_int − c_cont = 0.0969198750000001` — L1's own value, and the numerator of
  the 2.1537750000000058× conditioning ratio anchored in G0N.
- **PN-4** THE η̂ ESTIMATOR (below).
- **PN-5** the alignment-angle SECOND READING.
- **PN-6** the propagation model's regression form (below).
- **PN-7** conjunctive sub-clause aggregation (identical to L1's RN-11 / L2's
  MN-9); **PN-8** one paired world-block resample applied to every cell;
  **PN-9** every rule-18/20 clause evaluated with the SAME PAIRED structure the
  finalize stage uses.

### 0.2 PN-4 — the η̂ estimator, in closed form

For the two canonical occasion splits σ ∈ {interleaved, contiguous}, form the
symmetrized cross-covariance of the two half-cards,
`C_sigma = sym[(1/n) Σ_i d_i^(σ,1) d_i^(σ,2)ᵀ]`. Observation noise is
independent across halves and drops out entirely, so

    E[C_sigma] = A_mat + c_sigma B_mat,
    A_mat = w_mu² M Cov(trait) Mᵀ    (the PERSISTENT covariance)
    B_mat = w_slow² M Mᵀ             (the STATE-CHANNEL shape)

with `c_sigma = k2a.ar_cross_cov`. This is exactly L1's validated scalar
two-split machinery (RN-8: `V_full = A + B v`, `C_sigma = A + B c_sigma`) lifted
to the covariance matrix, and the trait term cancels **exactly** (not merely in
expectation) in `C_int − C_cont`. Solving,
`B̂_mat = (C_int − C_cont)/(c_int − c_cont)`, `Â_mat = C_cont − c_cont B̂_mat`.

With `W := U_m Λ_m^(−1/2)` the inverse square root of the state shape on its
rank-`m` range, `(M Mᵀ)^(−1/2) M = L` is orthonormal, so
`K := Wᵀ Â_mat W = (w_mu²/w_slow²) Cov(trait)` in **latent** coordinates. Hence,
exactly:

- pooled `K`: `k_tau` spikes and `m − k_tau` bulk values `c (1−η) σ_b²/m`;
- within-group `K`: trace `= c σ_b²`;

and

    kappa_hat := median of the bottom (m − k_tau) eigenvalues of K_pooled
    Sigma_hat := trace(K_within)
    eta_hat   := 1 − m · kappa_hat / Sigma_hat

The common factor `c = w_mu²/w_slow²` cancels, so **η̂ needs no design
constant, and in the noiseless limit η̂ = η identically at every η.** η̂ is
reported RAW (unclipped); a clipped companion is reported and never gated. The
MEDIAN over the bulk is the pinned robustification: the bulk is flat by the
identity above, so the median is consistent, and it is insensitive to the few
smallest whitened directions where the whitener's own error is largest.

**Which estimate of the state shape (pinned before Part 0, after a disclosed
3.2 s feasibility probe on the PREDICTION STREAM ONLY).** The card bulk is NOT
flat: derivation 3 wrote "+(1−η)σ_b²/m per dim", true in LATENT coordinates but
not in card coordinates, because `M Mᵀ = A_SCALE² L diag(G_PROFILE²) Lᵀ` spreads
every isotropic latent channel over a **2.3884×** eigenvalue range. Four
readings, all computed in every cell and all reported:

| reading | state shape | status |
|---|---|---|
| **PRIMARY `state`** | the panel-exact realized state channel's **innovation** second moment, `Σ_{i,t≥1}(s_it − φ s_{i,t−1})(·)ᵀ / (n(n_occ−1)(1−φ²))` | the MATRIX analogue of L2's MN-6 per-world panel-exact `B̂` calibration, which the L2 planner adjudication accepted verbatim as "derived from generator truth about the STATE channel (not about the labels)". Label-free in exactly the sense the registration asks, and using no more generator information than the certified meter it is paired with. |
| `split` | `B̂_mat` itself | the STRICTLY data-only reading |
| `oracle` | the generator's own `M Mᵀ` | pure upper bound |
| `flat` | none | derivation 3 taken literally |

The innovation form is used rather than the marginal second moment because at
φ = .90 the eight occasion draws are nearly collinear: realized condition ratios
are **3.52** (marginal), **2.63** (innovation), **2.3884** (true).

**The feasibility probe, disclosed with timing (anomaly 1).** A 3.2 s
prediction-stream probe (no world of any index generated, no artifact written,
no hypothesis channel touched) preceded Part 0 and showed the strictly
data-only whitener is unusable at these dimensions: `B̂_mat`'s eigenvalue spread
gives a condition ratio of **16.07** against the true 2.3884, because
`1/(c_int − c_cont) = 10.32` amplifies a `d/n = 0.125` covariance error. That
route is therefore a reported COMPANION, never the PRIMARY, and the decision was
taken before any pilot or main world of this leg existed.

**PN-5 — the SECOND READING (alignment angle).** In the same whitened
coordinates: `U_w` = top-`k_tau` eigenvectors of `K_within`; `U_b` = an
orthonormal basis of the span of the `G` provisional group centroids of the
whitened cards, grand mean removed (dimension `G − 1 = k_tau` here); overlap =
mean squared canonical cosine; calibrated as
`eta_hat_angle := (overlap − k_tau/m)/(1 − k_tau/m)` because a random
`k_tau`-frame in the `m`-dim range has expected overlap `k_tau/m`. This reading
is EXPECTED to saturate — the within-group spike-to-bulk ratio is
`η m/((1−η) k_tau) = 16η/(1−η)`, already 5.33 at η = 0.25 — so it is a DETECTOR
of alignment, not a calibrated meter of it. It gates nothing.

### 0.3 PN-6 — the propagation model and the correction

    observation unit : one CELL.  The registration's own words are "audit
                       deviation regressed on (1-ARI) ACROSS CELLS", so n = 10
                       rows, each the cell's world-mean deviation against its
                       world-mean (1 - ARI).
    response y       : dev = S_id(estimated partition) - target(same partition),
                       both from l2.audit_meter_l2, cross-fitted PRIMARY
    regressor x      : 1 - ARI(the partition the audit used, vs generator g)
    PRIMARY form     : OLS  y = a + b x            (registration-literal)
    correction       : S_id_corrected := S_id - (a_hat + b_hat x)
    oracle anchor    : the pooled TRUE-partition deviation on the identical
                       audit half and the identical calibrated meter (L2's
                       "or_" reading, which R.3 certified); the clause is
                       "the anchor lies inside the fit's intercept CI".

Every fit is **refit inside each paired world-block bootstrap replicate**, so
the corrected meter's CI carries the correction's own uncertainty.

**Declared second readings (fixed before any hypothesis number, both reported,
routing checked under both):** (A) `y = a + b √x` — ARI is a pair-counting
index, so near a correct partition `1 − ARI` grows faster than the
misassignment RATE the leaked type energy is linear in; the deviation is
therefore concave in `1 − ARI` and √ is the one-parameter concave companion.
(B) `x = 1 − Hungarian accuracy` (the misassignment rate itself), same linear
form.

**Executor correction recorded (anomaly 2).** An earlier draft of the script
pinned the (cell, world) grain instead of the registration's "across cells".
On the Part-0 prediction stream that grain is dominated by the per-panel
`B̂_cal` sampling noise and attenuates R² from **0.82 to 0.026** — it would have
made X-3a unreachable by construction. Corrected to the registration's own
grain BEFORE any arm ran; both grains are reported in `decision.json`
(`r2_at_cell_world_row_grain`).

### 0.4 G0N — anchors, construction, tolerances

| anchor | registration | re-derived | bit-exact |
|---|---|---|---|
| pooled same-data bias | `-0.005767022729929317` | `-0.005767022729929317` | **true** (residual 0.0) |
| conditioning ratio | `2.1537750000000058` | `2.1537750000000058` | **true** (from k2a's own AR algebra: `0.0969198750000001 / 0.04499999999999993`) |
| `B̂_cal` band | `0.2519 – 0.2521` | `0.2519088212714649 – 0.2521478508144498` | **true** at the quoted 4-decimal precision |
| L2 `C_rho55eq_eta0` (8 columns × 8 worlds) | persisted | re-measured through **L2's own path on L2's own worlds** | **true**, row-by-row |
| L2 `C_rho55eq_eta1` (8 columns × 8 worlds) | persisted | re-measured through **L2's own path on L2's own worlds** | **true**, row-by-row |

The two re-derived L2 cells carry the floor-curve anchors
(`boundary_err_true_card` 0.0 and 0.098388671875; `floor_pred_identity`
3.528253032967815e-07 and 0.10075606861240993) and the audit-table anchors
(`xf_S_id` 0.2444451044170753 / 0.19595319752468268, `xf_target`
0.25599311645224254 / 0.22575044770825609, `sd_S_id` 0.2434682245150412 /
0.185928902506104, `or_S_id` 0.24366832317734588 / 0.2382575515699197,
`or_target` 0.24965117962576905 / 0.24615313884363155, `xf_B_hat_cal`
0.25207496249751904 / 0.2521478508144498) — every one reproduced **bit-exactly,
row by row**, and the pooled same-data bias recomputed from all ten persisted
L2 C-cell files with residual exactly 0.0. All artifacts read with
`float_precision='round_trip'`.

**Construction:** reconstruction residual `2.220446049250313e-16`; all six
realized latent separations equal Δ to `1.7763568394002505e-15`;
`|realized η − designed| ≤ 0.02239770876615821`.

**A tolerance defect corrected pre-arms (anomaly 3).** L2 gated the realized
identity ENERGY at a flat 3% and passed at 2.9% — a realized-luck bar of the
defect-#35 class. The realized energy's own sampling sd is
`√(2[(1−η)²/m + η²/k_tau]/n)`, i.e. 0.0090 at η = 0 but **0.0361 at η = 1**,
because the aligned component has only `k_tau = 3` effective dimensions. This
leg therefore gates on the DESIGN-DERIVED 4-sigma band
`4√(2[(1−η)²/m + η²/k_tau]/n)` (0.0361 at η = 0 rising to 0.1443 at η = 1).
Realized maximum relative deviation `0.05969940197215595`; **band violations 0**.

### 0.5 G1N — non-degeneracy, liveness, realizability (rules 10 + 3 + 17)

Rule 10: the type channel, the identity channel and the η mixture all move the
card panel (minimum per-world RMS `0.045376525116919274`,
`0.04954894580915059`, `0.07100343853298338`), and the two canonical occasion
splits have a non-zero AR contrast `0.0969198750000001` (the taxometer's
denominator). Rule 3: the whitener keeps m = 48 strictly positive eigenvalues in
every cell (minimum kept eigenvalue `0.023691793463938723`, maximum condition
ratio `2.7195798986032176`).

**Rule 17 realizability, at the registration's own bar (η̂ CI half-width < 0.3
at every grid point):**

| cell | pilot η̂ (PRIMARY) | CI half-width (n=8) | oracle-whitener half-width | pilot η̂ (TRUE partition) | pilot angle reading |
|---|---:|---:|---:|---:|---:|
| `C_rho35eq_eta0` | -0.010843809324256576 | 0.1405415789534831 | 0.15407676788587335 | -0.007051581926260514 | 0.03479707664933567 |
| `C_rho35eq_eta0.25` | 0.1880800313697114 | 0.11931488234593718 | 0.12898844072928312 | 0.20019753167823565 | 0.38365298309695345 |
| `C_rho35eq_eta0.5` | 0.3632620361455502 | 0.10568348010576362 | 0.11146548887738486 | 0.3933322105852633 | 0.7576135828685742 |
| `C_rho35eq_eta0.75` | 0.5389948797949744 | 0.10527591165344011 | 0.11043449928589899 | 0.5823150047074286 | 0.8613104804003993 |
| `C_rho35eq_eta1` | 0.7742653957732979 | 0.05067099772807898 | 0.05473682983266195 | 0.8087559740687773 | 0.8986183942999371 |
| `C_rho55eq_eta0` | 0.013698348808189154 | 0.07019189808497561 | 0.07985827354980311 | 0.016567964116228573 | 0.026938345975656156 |
| `C_rho55eq_eta0.25` | 0.23358349442567336 | 0.0704379091293739 | 0.07469914894166173 | 0.25998877144730603 | 0.7356109260370127 |
| `C_rho55eq_eta0.5` | 0.4444439704114316 | 0.06373960563000539 | 0.06199692997367689 | 0.49966042511785874 | 0.8940161918089268 |
| `C_rho55eq_eta0.75` | 0.64191356407101 | 0.04335077108154572 | 0.04171891032336859 | 0.7067024125729793 | 0.9350689824706067 |
| `C_rho55eq_eta1` | 0.8885023211270981 | 0.030047652554862716 | 0.031222511047541233 | 0.9188459992110589 | 0.9542050106021289 |

Maximum half-width **0.1405 < 0.3**: the PRIMARY route is REALIZABLE and **the
pre-declared rule-17 fallback did NOT fire** (`eta_route =
primary_state_innovation_whitener`). The fallback ladder, pinned before any
pilot number, is EXACTLY ONE step: if the PRIMARY route's pilot CI half-width
reaches 0.3 in any cell it is dropped and the pure-oracle `M Mᵀ` whitener is
promoted and disclosed; if that also fails, both drop and X-1/X-2 score
UNREALIZABLE, which routes to P2N by the total routing function.

### 0.6 G2N — standing rules 18 + 20, the JOINT condition-sets

Every lean's clauses are reduced to SETS OF DESIGN POINTS over the
`(Δ, σ_b²)` plane — the only generative knobs the leans share once the η grid is
fixed by the registration — and INTERSECTED within each lean. The grid is
Δ-factors {0.7, 1.0, 1.4} × energy-factors {0.5, 1.0, 2.0} (9 points, 8
prediction replicates each, the same n the arms use); the registered design
point is `d1_e1`. Emptiness is decided over the WHOLE plane, not at the
registered point.

| clause | # points where it holds | points |
|---|---:|---|
| X-1a monotone (Spearman = 1) at BOTH energies | 9 | all |
| X-1b pole CI contains 0 at η=0 (both energies) | 6 | all except the three `e2` points |
| X-1c pole CI contains 1 at η=1 (both energies) | 9 | all |
| X-2 \|η̂ − η\| ≤ 0.125 in ≥8/10 cells | 9 | all |
| X-3a propagation fit R² ≥ 0.7 | 8 | all except `d0.7_e2` |
| X-3b oracle anchor inside the intercept CI | 9 | all |
| X-3c corrected meter tracks in ≥8/10 cells | 2 | `d1.4_e0.5`, `d1.4_e1` |
| X-4 corrected same-data bias CI excludes 0 (optimistic) | 9 | all |

| lean | JOINT condition-set | registered point inside? |
|---|---|---|
| **X-1** | 6 points (`d0.7_e0.5`, `d0.7_e1`, `d1_e0.5`, `d1_e1`, `d1.4_e0.5`, `d1.4_e1`) | **yes** |
| **X-2** | 9 points (all) | **yes** |
| **X-3** | 2 points (`d1.4_e0.5`, `d1.4_e1`) | **no** |
| **X-4** | 9 points (all) | **yes** |

**RULE-20 VERDICT: NO STOP.** No lean's condition-set is empty, so the leg
proceeds to the arms. Two facts are recorded for the planner now, before the
arms, in the spirit of L2's defect #31:

1. **X-3's registered point is OUTSIDE its own condition-set on the prediction
   stream** — because of clause X-3c (corrected tracking), which the prediction
   stream reaches only at Δ × 1.4, where the partitions are good enough that the
   correction has little left to do (`n_corrected_tracking` = 10 and 9 there
   against 3 at the registered point). This is NOT an empty set and NOT a rule-20
   stop; it is a pre-registered forecast that **X-3 is the lean at risk**, and it
   is on the record before any arm ran.
2. **X-1b fails at every high-energy point (`e2`)**: doubling σ_b² breaks the
   η = 0 pole calibration while leaving the η = 1 pole intact. The registered
   energies are not in that regime.

Per-point diagnostics (prediction stream, before any world):

| point | R² (cell grain) | R² (cell×world grain) | intercept | slope | intercept ½-width | oracle anchor | corrected tracking | corrected bias | ½-width |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `d0.7_e0.5` | 0.86773 | 0.00087 | -0.03010 | -0.02410 | 0.03164 | -0.01857 | 7/10 | -0.01178 | 0.00240 |
| `d0.7_e1` | 0.77909 | 0.00646 | -0.02927 | -0.02089 | 0.03098 | -0.01743 | 7/10 | -0.01213 | 0.00172 |
| `d0.7_e2` | 0.54151 | 0.01377 | -0.02655 | -0.01803 | 0.02830 | -0.01545 | 6/10 | -0.01168 | 0.00127 |
| `d1_e0.5` | 0.90481 | 0.01375 | -0.02246 | -0.05568 | 0.03180 | -0.01857 | 6/10 | -0.00502 | 0.00187 |
| **`d1_e1`** | **0.82024** | 0.02635 | **-0.02350** | **-0.03596** | 0.02946 | **-0.01743** | **3/10** | **-0.00747** | 0.00120 |
| `d1_e2` | 0.70348 | 0.03121 | -0.02295 | -0.02441 | 0.02672 | -0.01545 | 4/10 | -0.00844 | 0.00138 |
| `d1.4_e0.5` | 0.94945 | 0.00314 | -0.01907 | -0.08794 | 0.03149 | -0.01857 | 10/10 | -0.00136 | 0.00057 |
| `d1.4_e1` | 0.90015 | 0.01818 | -0.01929 | -0.05747 | 0.02953 | -0.01743 | 9/10 | -0.00267 | 0.00106 |
| `d1.4_e2` | 0.71624 | 0.03598 | -0.01935 | -0.03360 | 0.02594 | -0.01545 | 6/10 | -0.00533 | 0.00111 |

All 28 clause pairs are enumerated in `gates.json`
(`G2N.rule18_rule20_joint.pairwise`) and in `part0_tables.md`.

### 0.7 G3N — the rule-19 fidelity table

The full table is in `results/m4_l3_taxometer_meter/part0_tables.md` and in
`gates.json` (`G3N.fidelity_table`); it is summarized here.

| lean | theorem quantity | predicted value / curve | the bar | why the bar is on that quantity |
|---|---|---|---|---|
| **X-1** | **η itself** (the registration says so: "shadows: η itself") | PN-4's identity is EXACT in the noiseless limit — η̂ = η at every η. Prediction stream at the registered point (8 replicates), PRIMARY: 0.049524, 0.278052, 0.503840, 0.742381, 0.985718 (ρ.35eq) and 0.042144, 0.253407, 0.465541, 0.704505, 0.992073 (ρ.55eq); pure-oracle whitener 0.025924…0.984966 and 0.036687…0.991826 (near-identical); strictly data-only whitener 0.796299…1.135568 and 0.588675…1.093214 (**unusable**); NO whitening −0.568587…−0.158778 and −0.096847…0.418076 (**unusable** — the shape repair is what makes the route work). Monotone by construction; the poles are the calibration test (at η=0 the bulk IS the whole signal, at η=1 the bulk is pure estimation error) | Spearman(η̂, η) = 1 on each 5-point grid at both energies, AND η̂'s CI contains 0 at η=0 and 1 at η=1 in all four pole cells | rule 19: the taxometer's estimand is η, on η's own [0,1] scale; the bar is an ordering plus two point-calibrations OF THAT SAME NUMBER |
| **X-2** | η again, at the CALIBRATION grain: \|η̂ − η\| | zero bias in the noiseless limit, so the error is pure estimation error with two identified sources — the whitener's own error (isolated by the oracle-whitener reading) and provisional-grouping error, which BOTH truncates Σ̂ and leaks type energy into S, so the predicted bias sign is POSITIVE relative to the true-partition reading and grows as ARI falls | \|η̂ − η\| ≤ 0.125 (half the grid spacing) in ≥8/10 cells | the error in the units of its own estimand, at the resolution the grid itself defines |
| **X-3** | appendix R.3's open object: the ESTIMATED-partition audit deviation as a function of PARTITION QUALITY, and the corrected meter built from it | leaked type energy enters in proportion to the misassignment rate, so dev is monotone decreasing in (1−ARI) and CONCAVE in it. **On L2's own persisted 10 C-cells the registration-literal LINEAR fit gives R² = 0.8272283113384643, slope −0.03599958160292834, intercept −0.013395323781245904 against an oracle anchor of −0.007498461325399086** — the shape clause is predicted to pass and the ANCHOR clause is the one at risk, exactly because of the predicted concavity (the √ companion there gives R² = 0.9276111054158521, intercept −0.00622742849266543). Fresh-seed prediction stream at the registered point: R² = 0.8202396875636956, slope −0.035963688245683495, intercept −0.0234971097002013, anchor −0.017434371532954903; √ companion R² = 0.9099631008744096; misassignment-rate companion R² = 0.7861303640290177 | R² ≥ 0.7 AND the anchor inside the intercept's paired CI AND the corrected meter's CI contains the designed share in ≥8/10 cells on ESTIMATED partitions | share-vs-share throughout; the anchor is the SAME share difference measured on the true partition, so the clause at ARI=1 compares like with like |
| **X-4** | L2-charter derivation 4's SIGN, under the CORRECTED meter | the corrected bias stays negative and of L2's order, because the propagation term is fitted on the cross-fitted deviations and applied to each reading at ITS OWN (1−ARI), and the two ARIs are nearly equal — the correction subtracts almost the same number from both and cannot cancel the truncation term. Prediction stream at the registered point: −0.00747 ± 0.00120 | pooled (same-data corrected − cross-fitted corrected) CI excludes 0 on the NEGATIVE side | derivation 4 predicts a SIGN on a difference of two shares; the size is reported and deliberately NOT gated |

**Pilot MDEs (4 reserved pilot worlds → main design n = 8), rule-11
directions.** 61 interval clauses are tabulated in `part0_tables.md`. The
η̂ clauses run from MDE 0.0393 (`C_rho55eq_eta1`) to 0.1838
(`C_rho35eq_eta0`); the pooled X-4 clause has pilot mean
−0.008227750802971147, world sd 0.003059085461326524 and **MDE
0.004500241684731064** at n = 8, i.e. the predicted effect is 1.83× its own MDE.
Rule-13 spec: B = 2000 at seed = master_seed, with a ≥10×B (20000) recheck at
any clause whose boundary lies within 2 Monte-Carlo endpoint sds.

### 0.8 G4N — hygiene, rule 16, round-trip, chunking

Full-object enumeration, no gaps and no overlaps:

- **Layer A** (sub-clause states → lean state): 88 rows = 88 expected = 88
  unique keys, every row assigned.
- **Layer B** (rule-20 stop × lean states⁴ → route): 162 rows = 162 expected =
  162 unique keys, every row assigned; route counts P1N 81, P2N 54, P3N 18,
  P4N 9; **all four routes reachable**. Restricted to the registered 2⁴
  HOLD/MISS grid with no rule-20 stop: 16 rows, P2N 8, P3N 4, P4N 4.

Every artifact is read back with `float_precision='round_trip'`; stages are
chunked (`part0` 207.344 s, both other stages far below the 600 s bound); the
rule-12 source-object header is at the top of the leg script and reproduced in
`gates.json` (`G4N.rule12_source_objects`).

---

## Part 1 — the arms, and the leans

10 cells × 8 main worlds × 512 authors = 80 world-cells, 40 960 author-cards.
Arms 22.385 s, finalize 0.686 s; **total adjudicated compute 230.416 s**
(Part 0's 207.345 s were written to disk and enforced in code by
`require_part0()` before any arm ran) against a < 25 min budget.

### VERDICT: `TAXOMETER_DEAD__X1MX2HX3MX4H__P2N`

**X-1 MISS · X-2 HOLD · X-3 MISS · X-4 HOLD → P2N.** Routing precedence: X-1 is
not HOLD, so P2N fires and X-3's state does not enter the route.

**But P2N's registered reading — "the taxometer is dead at these dims" — is not
what was measured.** The taxometer ORDERS perfectly and is CALIBRATED inside the
registration's own tolerance in every one of the ten cells. X-1 misses on two of
its four pole cells, both at η = 0, where a finite-sample bias of +0.049 and
+0.092 is resolved by a CI half-width of 0.041 and 0.062.

### 1.1 The taxometer (question A): η̂ against designed η

PRIMARY route = bulk-excess with the panel-exact state-innovation whitener,
provisional grouping = L1's PRIMARY (Lloyd) instrument.

| cell | designed η | **η̂ PRIMARY** | 95% CI | error | within 0.125? | η̂ oracle-whitener | η̂ data-only whitener | η̂ no-whitening | **angle (2nd reading)** | ARI (Lloyd) |
|---|---:|---:|---|---:|:--:|---:|---:|---:|---:|---:|
| `C_rho35eq_eta0` | 0 | **0.092384** | [0.031550, 0.155382] | +0.092384 | ✓ | 0.044561 | 0.786725 | −0.575826 | −0.015178 | 0.988967 |
| `C_rho35eq_eta0.25` | 0.25 | **0.312689** | [0.250803, 0.370905] | +0.062689 | ✓ | 0.276136 | 0.871225 | −0.451307 | 0.319468 | 0.934442 |
| `C_rho35eq_eta0.5` | 0.5 | **0.527417** | [0.468836, 0.579526] | +0.027417 | ✓ | 0.501355 | 0.950880 | −0.379311 | 0.703846 | 0.853472 |
| `C_rho35eq_eta0.75` | 0.75 | **0.755013** | [0.687838, 0.820251] | +0.005013 | ✓ | 0.739518 | 1.040762 | −0.315787 | 0.834150 | 0.781738 |
| `C_rho35eq_eta1` | 1 | **1.013071** | [0.896515, 1.117619] | +0.013071 | ✓ | 1.014393 | 1.143053 | −0.255597 | 0.885888 | 0.711362 |
| `C_rho55eq_eta0` | 0 | **0.049464** | [0.008869, 0.091537] | +0.049464 | ✓ | 0.032177 | 0.594403 | −0.076742 | −0.010624 | 0.978561 |
| `C_rho55eq_eta0.25` | 0.25 | **0.270740** | [0.232782, 0.307378] | +0.020740 | ✓ | 0.255787 | 0.711557 | 0.065215 | 0.691757 | 0.807117 |
| `C_rho55eq_eta0.5` | 0.5 | **0.488101** | [0.458926, 0.518994] | −0.011899 | ✓ | 0.473716 | 0.826047 | 0.188653 | 0.872446 | 0.652976 |
| `C_rho55eq_eta0.75` | 0.75 | **0.717676** | [0.691666, 0.744777] | −0.032324 | ✓ | 0.707915 | 0.950054 | 0.287889 | 0.920333 | 0.536382 |
| `C_rho55eq_eta1` | 1 | **1.000506** | [0.940217, 1.053524] | +0.000506 | ✓ | 1.000743 | 1.096619 | 0.382501 | 0.947635 | 0.445569 |

**X-1 (prior .70) — MISS, on sub-clause (b) alone.**

- (a) **HOLD.** Spearman(η̂, η) = **1.0 at both energies**, strictly increasing,
  and 1.0 under *every* declared reading: spectral provisional grouping, TRUE
  partition, oracle whitener, and the alignment angle.
- (b) **MISS, 2/4 pole cells.** η = 1 calibrates at both energies
  (`C_rho35eq_eta1` CI [0.896515, 1.117619] ∋ 1; `C_rho55eq_eta1`
  [0.940217, 1.053524] ∋ 1). η = 0 fails at both: the CI lower bounds are
  **0.031550** and **0.008869**, i.e. the CI excludes 0 from above by 0.0316 and
  0.0089. Rule 13 did not trigger on either (the distances exceed 2 Monte-Carlo
  endpoint sds), so the misses are robust to bootstrap noise.

**X-2 (prior .55) — HOLD, 10/10 cells** (the bar was 8/10). Maximum absolute
error **0.092384**; median absolute error 0.024. It also holds 10/10 under the
TRUE-partition reading and 10/10 under the oracle-whitener reading. This is the
strongest single result of the leg: **at the resolution the 5-point grid itself
defines, the label-free taxometer is calibrated everywhere.**

**Routing is NOT invariant under one declared second reading, and this is
recorded as the leg's most consequential companion.** Under the **pure-oracle
whitener** — the same estimator with the state shape taken from the generator's
`M Mᵀ` instead of from the realized state channel's innovations — all four poles
calibrate: η=0 gives [−0.028313, 0.112146] and [−0.014991, 0.077757] (both ∋ 0),
η=1 gives [0.890498, 1.125840] and [0.937830, 1.056065] (both ∋ 1). X-1 would
then HOLD, X-3 would still MISS, and the route would be **P3N, not P2N**. Two
effects combine: the oracle whitener halves the η = 0 bias (0.0446/0.0322 against
0.0924/0.0495) *and* widens the CI (half-widths 0.070/0.046 against 0.062/0.041).
So **the η = 0 pole miss is roughly half whitener-estimation-borne and half
intrinsic to `Â_mat`'s own sampling error.**

**What the four whitener readings establish about derivation 3.** The
registration's bulk-excess route, taken LITERALLY (flat card-space bulk, no
shape repair), reads η̂ = −0.576 … −0.256 at ρ.35eq and −0.077 … 0.383 at
ρ.55eq — monotone but not remotely calibrated. The strictly data-only whitener
reads 0.787 … 1.143 and 0.594 … 1.097 — monotone but grossly biased upward, its
condition ratio **15.598213** against the truth's 2.3884. Only the state-shape
whitener (condition ratio **2.698127**) delivers a calibrated meter. **The
`G_PROFILE` shape repair is not a refinement of derivation 3; it is what makes
derivation 3 true in card space.**

**The alignment angle (PN-5's registered second reading) behaves exactly as
predicted in Part 0**: perfectly monotone (Spearman 1.0 at both energies) and
saturating — 0.692 at η = 0.25 and 0.947 at η = 1 in the ρ.55eq column, against
designed 0.25 and 1. It is a DETECTOR of alignment, not a meter of it, and it
would fail the pole clause at η = 1 in both energies ([0.868977, 0.900515] and
[0.942229, 0.952582]).

### 1.2 The partition-propagated meter (question B)

| cell | 1 − ARI(audit partition) | dev (uncorrected) | 95% CI | fitted | **corrected** | 95% CI | tracks? | true-partition dev |
|---|---:|---:|---|---:|---:|---|:--:|---:|
| `C_rho35eq_eta0` | 0.020773 | 0.005038 | [−0.013474, 0.026848] | 0.000236 | 0.004800 | [0.004317, 0.005364] | ✗ | 0.007964 |
| `C_rho35eq_eta0.25` | 0.089383 | −0.003919 | [−0.023319, 0.020209] | −0.003002 | −0.000924 | [−0.002324, 0.000928] | ✓ | 0.005850 |
| `C_rho35eq_eta0.5` | 0.165513 | −0.009918 | [−0.028860, 0.013624] | −0.006594 | −0.003314 | [−0.004591, −0.002092] | ✗ | 0.005030 |
| `C_rho35eq_eta0.75` | 0.243776 | −0.013856 | [−0.033479, 0.010906] | −0.010287 | −0.003577 | [−0.005107, −0.001816] | ✗ | 0.004455 |
| `C_rho35eq_eta1` | 0.308194 | −0.016072 | [−0.036266, 0.010062] | −0.013327 | −0.002757 | [−0.004782, −0.000440] | ✗ | 0.004192 |
| `C_rho55eq_eta0` | 0.040757 | 0.002275 | [−0.014506, 0.021106] | −0.000707 | 0.003005 | [−0.000113, 0.005411] | ✓ | 0.006574 |
| `C_rho55eq_eta0.25` | 0.210790 | −0.010778 | [−0.027886, 0.010359] | −0.008731 | −0.002041 | [−0.003706, −0.000642] | ✗ | 0.003820 |
| `C_rho55eq_eta0.5` | 0.371402 | −0.016372 | [−0.035755, 0.007545] | −0.016310 | −0.000078 | [−0.001382, 0.001606] | ✓ | 0.002746 |
| `C_rho55eq_eta0.75` | 0.476227 | −0.019338 | [−0.039084, 0.005864] | −0.021257 | 0.001903 | [0.000821, 0.002901] | ✗ | 0.001993 |
| `C_rho55eq_eta1` | 0.563246 | −0.022403 | [−0.042531, 0.003855] | −0.025363 | 0.002983 | [0.001747, 0.003911] | ✗ | 0.001656 |

**The propagation fit (PRIMARY, registration-literal linear form, one row per
cell, refit inside every bootstrap replicate):**

    dev = 0.0012162320427350467 - 0.04718966206694972 (1 - ARI)
    R^2  = 0.891596154639982   [0.826187803453253, 0.9273340435266129]
    slope                      [-0.05492139609682376, -0.03718986553430942]
    intercept                  [-0.017136477786541676, 0.02306420791159516]
    oracle anchor = 0.004428032310894993  [-0.014988701299138155, 0.028277087946167102]

Declared second readings: √(1−ARI) gives R² = **0.9780973208413469** (intercept
0.01006200600246863, slope −0.04467896834790874); (1 − Hungarian accuracy) gives
R² = **0.8576211182723725** (intercept 0.00023630338880636237, slope
−0.10300340361599257). The predicted concavity is confirmed: the √ companion
beats the linear form by 0.087 in R², exactly as Part 0 forecast from L2's
persisted cells (0.9276 vs 0.8272 there). At the (cell, world) row grain R²
collapses to **0.040428064883860304** — the grain correction recorded as
anomaly 2 was decisive.

**X-3 (prior .60) — MISS, on sub-clause (c) alone.**

- (a) **HOLD.** R² = 0.8916 ≥ 0.7, with the whole bootstrap CI above the bar.
- (b) **HOLD.** The oracle anchor 0.004428 lies inside the intercept CI
  [−0.017136, 0.023064]; the containment is comfortable, not marginal
  (the anchor sits 0.16 of a half-width from the intercept point estimate).
- (c) **MISS, 3/10** (the bar was 8/10). **And the mechanism is the opposite of
  L2's:** the UNCORRECTED cross-fitted meter tracks **10/10** here, and the
  CORRECTED one tracks 3/10 — because **the correction shrinks the CI by a
  factor of 6–39×.** The uncorrected deviations carry a world-common offset
  (the per-world `B̂_cal` draw, shared by every cell of a world), giving CI
  half-widths ≈ 0.020; the refitted intercept absorbs exactly that offset inside
  each bootstrap replicate, so the corrected deviations have half-widths of
  0.0005–0.0028. At that precision the fit's residual misfit — up to
  **0.004800** in share units, 3.6% of the ρ.35eq target — is resolvable, and
  seven cells reject 0.

So the propagation model is a **good description and an inadequate correction**:
it explains 89% of the between-cell deviation variance and lands its ARI = 1
value on the certified true-partition anchor, but its residual exceeds the
resolution it itself creates.

**X-4 (prior .80) — HOLD, decisively.** Under the CORRECTED meter the pooled
same-data optimistic bias is **−0.007639458871208268**
[−0.008786900570630973, −0.006390021005151330], negative in **10/10** cells,
6.37× its own half-width and 1.70× the pilot MDE (0.004500241684731064). The
RAW (uncorrected) bias is −0.007588169891501556
[−0.009114406065434490, −0.006043047568769170] — the correction moves it by
0.00005, exactly as Part 0 predicted ("the correction subtracts almost the same
number from both and cannot cancel the truncation term"; the two ARIs differ by
at most 0.0039 in any cell). L2's independent value on its own worlds was
−0.005767022729929317. **Derivation 4's sign is now measured three times, on
three world families, and it survives partition correction.**

### 1.3 Free confirmations (not gated in this leg)

- **R.1's η-floor law reproduces on fresh worlds under a fresh master seed.**
  Measured true-card per-boundary rate vs the closed-form floor:
  0.000000/0.000000, 0.000000/0.000218, 0.004069/0.004188, 0.014567/0.013953,
  0.027832/0.027122 (ρ.35eq) and 0.000000/0.000000, 0.009684/0.009785,
  0.041911/0.040059, 0.073405/0.072239, 0.101481/0.100688 (ρ.55eq) — agreement
  to 4.7% or better in every resolvable cell, η-ordering exact at both energies.
- **The two grouping instruments are interchangeable here.** Lloyd vs spectral
  ARI differ by at most 0.0043 in any cell, and the η̂ they induce differ by at
  most 0.00093. The registration's "both L1 instruments" requirement is
  satisfied with a null result.
- **`B̂_cal` on this leg's worlds is 0.247053–0.247370** against L2's
  0.2519088–0.2521479 — a world-family-level draw of the calibration constant on
  the other side of `w_slow² = 0.25`, which is why this leg's true-partition
  deviations are POSITIVE (+0.0017…+0.0080) where L2's were negative
  (−0.0060…−0.0087). **The meter's per-world offset is comparable in size to the
  partition-borne effect the leg is measuring** — a scoping fact the planner
  should carry forward.

### 1.4 Rule 13, and routing robustness

Rule 13: **1 clause triggered, 0 BOUNDARY, STABLE at B = 20 000** — the
corrected-meter containment at `C_rho55eq_eta0` (distance to boundary
0.00011339530536151306 against a Monte-Carlo endpoint sd of
8.600095313305037e-05; verdict `true` at both B = 2000 and B = 20 000, endpoints
[−0.00011233701579071762, 0.005453288292010364]). No pole clause and no X-4
clause came within 2 MC sds of its boundary.

Routing under the declared second readings:

| reading | X-1 | X-3 | route |
|---|---|---|---|
| **PRIMARY (registered)** | MISS | MISS | **P2N** |
| spectral provisional grouping | MISS | — | P2N |
| TRUE-partition grouping | MISS | — | P2N |
| alignment angle | MISS (poles saturate) | — | P2N |
| **pure-oracle whitener** | **HOLD** | MISS | **P3N** |
| √(1−ARI) propagation form | — | MISS (clause c unchanged) | P2N |
| misassignment-rate propagation form | — | MISS (clause c unchanged) | P2N |

**Routing is invariant under every reading except the pure-oracle whitener,
under which it becomes P3N.** That single non-invariance is the leg's headline
caveat and is stated here rather than buried.

### 1.5 Registration defects recorded

- **#36 (rule-19 class, the third of its family after #30 and #33).** X-1's pole
  clause and X-2's calibration clause are bars **on the same quantity at
  inconsistent resolutions**: X-2 declares 0.125 to be the resolution the grid
  itself defines, while X-1 demands exact CI containment of the pole values —
  a tolerance of 0 — at a design whose η = 0 CI half-width is 0.041–0.062 and
  whose estimator has an identified O(0.05) finite-sample bias there. The two
  clauses cannot both be honoured by any estimator whose pole bias exceeds its
  own precision, and the leg's own X-2 result proves the estimator is inside the
  registration's declared resolution everywhere. **X-1(b) is a nil-significance
  test standing in for an equivalence claim** — precisely the pathology the
  M4-F9 charter repaired on the F-line.
- **#37.** X-3's clause (c) has no precision budget. The correction is defined
  so as to remove the world-common nuisance, so it necessarily tightens the CI
  it is then tested against; the bar "the corrected CI contains the designed
  share in ≥8/10" therefore gets HARDER the better the correction works. The
  clause conflates "the correction is right" with "the residual is below the
  post-correction resolution", and the leg measures the second, not the first.
- **#38 (executor-side, recorded for symmetry).** The registration says
  "regressed on (1−ARI) across cells" but does not state the observation grain
  explicitly; the executor's first draft used (cell, world), where the
  per-panel `B̂_cal` noise attenuates R² from 0.89 to 0.040. Corrected pre-arms
  under rule 9 and disclosed as anomaly 2.

### 1.6 Anomalies, with timing

1. **3.2 s pre-Part-0 feasibility probe on the PREDICTION STREAM ONLY** (no
   world of any index generated, no artifact written, no hypothesis channel
   touched), which established that the strictly data-only whitener is unusable
   (condition ratio 16.07 vs 2.3884) and fixed the PRIMARY route before any
   pilot or main world existed.
2. **Regression-grain correction** (defect #38), made pre-arms; both grains
   reported.
3. **G0N energy-tolerance defect corrected pre-arms**: L2's flat 3% bar replaced
   by the design-derived 4σ band `4√(2[(1−η)²/m + η²/k_τ]/n)`; realized maximum
   relative deviation 0.05969940197215595, band violations 0.
4. **Two rule-18/20 clause implementations corrected pre-arms** after the first
   Part-0 execution reported a rule-20 STOP: X-4's clause had used the marginal
   sd of `sd_dev` for a PAIRED difference whose own sd is ~15× smaller, and
   X-3's intercept clause had used a cell-level sd instead of the refitted
   intercept's spread. Both were mis-implementations of the registered clause,
   not tuning; both were fixed before any arm ran, and after the fix the
   rule-20 verdict is NO STOP with X-4's condition-set 9/9. The first (defective)
   Part-0 execution reported `rule20_empty_leans = ["X-4"]`, and this is
   disclosed rather than silently overwritten.
5. **The rule-17 fallback did NOT fire** (max pilot CI half-width 0.1405 < 0.3).
6. Realized η at the η = 0 cells is 0.000294 (sampling), inside the 0.03 gate.

---

## Part 2 — the brief to the planner

1. **The taxometer is not dead; its η = 0 pole is.** Spearman = 1 at both
   energies under every reading, |η̂ − η| ≤ 0.125 in **10/10** cells (X-2 held
   against a .55 prior), and both η = 1 poles calibrate. P2N is executed as
   registered, but its stated reading is not what was measured — the same
   pattern as V-3(c) in L1 and W-1 in L2, and now recorded as defect #36.
2. **Derivation 3 needs a stated amendment.** In card space the "bulk" is not
   flat: `M Mᵀ` spreads every isotropic latent channel over a 2.3884× range, and
   the literal bulk-excess estimator reads η̂ = −0.58 at η = 0. The estimator
   only works after whitening by the state-channel shape, and the leg measures
   exactly how much each version of that shape costs: pure oracle (poles
   calibrate), panel-exact innovations (η = 0 bias +0.05/+0.09), strictly
   data-only (unusable, +0.59/+0.79 at η = 0).
3. **The propagation model is a good description and an inadequate correction.**
   R² = 0.8916 [0.8262, 0.9273], slope −0.0472 [−0.0549, −0.0372], and the
   ARI = 1 intercept lands on R.3's certified true-partition anchor. But the
   correction removes the world-common nuisance and thereby shrinks the meter's
   CI 6–39×, at which precision its own residual (≤ 0.0048 in share units) is
   resolvable in 7/10 cells. Defect #37: the clause has no precision budget.
4. **Derivation 4's sign is now measured a third time and survives correction**:
   −0.007639 [−0.008787, −0.006390], 10/10 cells, against L2's −0.005767.
5. **A scoping fact for whatever follows.** `B̂_cal` moved from 0.2519–0.2521
   (L2's worlds) to 0.2470–0.2474 (L3's), flipping the sign of the
   true-partition deviation from −0.0075 to +0.0044. The meter's per-world
   offset is the same size as the partition-borne error the L-line has been
   chasing since W-4; any further meter work needs more world blocks, not more
   estimator repair.
