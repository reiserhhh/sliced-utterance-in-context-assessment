# SUICA M4-R3 — the taxometer on identity mixtures

**Outcome: `DILUTION_LAW_HOLDS__PARTIAL__BUDGET_HOLDS`**

- **P1 (routes):** `DILUTION_LAW_HOLDS` (cell 3) — registered lean `DILUTION_LAW_HOLDS`, MET.
- **P2 (co-primary):** `PARTIAL` — registered lean `SIGNED_DISSOCIATION_CONFIRMED`, **MISSED**  ⚑ #73 flag raised.
- **P3 (co-primary):** `BUDGET_HOLDS` — registered lean `BOUND_MEASURED (weakly at w = 2)`, **MISSED**.

Registered BEFORE the run in `docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md` ("M4-R3", commit 4597c33), against the derivation in `docs/SUICA_R3_IDENTITY_RECONCILIATION_NOTE.md` (commit 1bbda62). EXPLORATORY, synthetic, card space only, label-free. The style channel is **planted**; nothing here bears on any real corpus, and no psychological construct is named or implied.

Run 2026-08-18T20:18:33.345236+00:00; total wall time 20.3 s; 128 world-cells.

## 1. What was predicted, before any world of this leg existed

The note's composition theorem (section 2): style_a is isotropic, so it contributes ONLY to the isotropic pool and the excess-aligned pool is untouched. With V_s/V_b = w² pinned by construction,

```
    η̂(η₀, w) = η₀ / (1 + w²)
```

These eight numbers are the registration's, not this run's. The acceptance band is **the L3 CERTIFICATION BUDGET ±0.125** on the 8-world cell mean (`l3.X2_TOL` = 0.125; identical: yes) — the instrument's own certified error, not a tolerance invented here.

## 2. Prediction vs read — the eight registered cells (σ_b² = rho55eq)

| η₀ | w | style share | registered prediction | η̂ cell mean ± sd | 95% CI | η̂_oracle mean | abs(η̂ − pred) | band ±0.125 | oracle in band |
|---|---|---|---|---|---|---|---|---|---|
| 0.25 | 0 | 0.00 | **0.250** | 0.2451 ± 0.0648 | [0.1910, 0.2993] | 0.2473 | 0.0049 | **IN** | in |
| 0.25 | 0.5 | 0.20 | **0.200** | 0.2158 ± 0.0576 | [0.1677, 0.2640] | 0.1968 | 0.0158 | **IN** | in |
| 0.25 | 1 | 0.50 | **0.125** | 0.1424 ± 0.0245 | [0.1220, 0.1629] | 0.1218 | 0.0174 | **IN** | in |
| 0.25 | 2 | 0.80 | **0.050** | 0.0759 ± 0.0224 | [0.0572, 0.0947] | 0.0474 | 0.0259 | **IN** | in |
| 0.6 | 0 | 0.00 | **0.600** | 0.5566 ± 0.0785 | [0.4909, 0.6222] | 0.5974 | 0.0434 | **IN** | in |
| 0.6 | 0.5 | 0.20 | **0.480** | 0.4464 ± 0.0591 | [0.3971, 0.4958] | 0.4768 | 0.0336 | **IN** | in |
| 0.6 | 1 | 0.50 | **0.300** | 0.2756 ± 0.0280 | [0.2522, 0.2990] | 0.2962 | 0.0244 | **IN** | in |
| 0.6 | 2 | 0.80 | **0.120** | 0.1204 ± 0.0153 | [0.1076, 0.1332] | 0.1168 | 0.0004 | **IN** | in |

**8/8** cell means inside the certification band. Monotone strict decrease in w: η₀ = 0.25 → yes, η₀ = 0.6 → yes. 
No violating step.

Flat clause (`max−min < 0.05` where the predicted drop ≥ 0.13): η₀ = 0.25 predicted drop 0.200, observed spread 0.1692 → flat **no**, η₀ = 0.6 predicted drop 0.480, observed spread 0.4362 → flat **no**.

## 3. Instrument vs law — what the oracle localizes

η̂_oracle is the note's excess-alignment reader applied to the REALIZED latent identity+style vectors: `(raw aligned share − d_T/D)/(1 − d_T/D)` with d_T = 3, D = 48, zero point 0.0625. It reads the LAW as realized in each world; η̂ reads the law THROUGH the certified whitening pipeline. Divergence between them is the instrument, not the law.

- η₀ = 0.25: oracle all in band yes, oracle monotone yes; instrument all in band yes, instrument monotone yes.
- η₀ = 0.6: oracle all in band yes, oracle monotone yes; instrument all in band yes, instrument monotone yes.

**Localization.** Instrument and law agree everywhere on this grid. The largest instrument−law gap is 0.0408 at η₀ = 0.6, w = 0 (style share 0.00) and the smallest is 0.0022 at η₀ = 0.25, w = 0 — both far inside the ±0.125 budget. There is therefore **no case on this grid where η̂ misses a registered prediction while η̂_oracle hits it**: the localizer never has to fire, because the instrument does not miss. The whitening precondition is the reason it does not: the whitener is estimated from the STATE channel's innovations, which the style channel does not touch, so adding style leaves the whitening shape exactly where the L3 certification put it and moves only the isotropic mass the estimator is designed to divide out.

## 4. P2 — the signed dissociation

The union reader is the two-draw AUC (RN-R3-6): a freshly drawn ε field per author, sharing τ, b and style; pooled same-author-vs-different AUC on the cosine of centered cards over the full 512×512 cross-draw matrix. **Its null is 0.5** and is stated (#68) — the two draws are exchangeable under the same-author hypothesis; no composite subtlety in this design.

| η₀ | w | AUC (union reader) cell mean | η̂ cell mean | AUC, ε+slow refreshed (2nd reading) |
|---|---|---|---|---|
| 0.25 | 0 | 1.0000 | 0.2451 | 0.9518 |
| 0.25 | 0.5 | 1.0000 | 0.2158 | 0.9679 |
| 0.25 | 1 | 1.0000 | 0.1424 | 0.9910 |
| 0.25 | 2 | 1.0000 | 0.0759 | 0.9999 |
| 0.6 | 0 | 1.0000 | 0.5566 | 0.9184 |
| 0.6 | 0.5 | 1.0000 | 0.4464 | 0.9435 |
| 0.6 | 1 | 1.0000 | 0.2756 | 0.9824 |
| 0.6 | 2 | 1.0000 | 0.1204 | 0.9999 |

AUC strictly rises across all w steps for both η₀: **no**. η̂ strictly falls across all w steps for both η₀: yes. → `PARTIAL`.

**Why PARTIAL, precisely: the registered PRIMARY reader is at its CEILING, not silent.** Under the registration-literal construction the two draws differ ONLY in ε — τ, b, style AND the slow state are shared bit-for-bit — so the cards are separated by their persistent content at every w: the AUC cell mean is exactly 1.0000 in all 8 cells, perfect separation, spread 0.0000. The registered clause "AUC strictly rises" therefore **cannot fire** in this design: its antecedent is degenerate (a #59-class degenerate antecedent, found at execution, not at registration). This is a property of the reader, not of the worlds.

The declared second reading — the same two-draw contrast with the slow state ALSO refreshed, so the only shared content is the persistent author card content itself — is off the ceiling and **strictly rises in w for both η₀** (largest span 0.0815), against a strictly falling η̂ over the identical worlds. The signed dissociation the note names is therefore VISIBLE in these worlds; it is the registered reader that cannot show it. Per rule, the routing above is the registered reader's: `PARTIAL`, #73 flag raised. The second reading routes nothing.

## 5. P3 — the whitening bias against the realized style share

| η₀ | w | style share | abs(η̂ − η̂_oracle) of cell means | signed bias | 95% CI (signed, paired) | mean per-world abs(bias) — 2nd reading | vs 0.125 budget |
|---|---|---|---|---|---|---|---|
| 0.25 | 0 | 0.00 | 0.0022 | -0.0022 | [-0.0515, +0.0471] | 0.0437 | under |
| 0.25 | 0.5 | 0.20 | 0.0190 | +0.0190 | [-0.0257, +0.0637] | 0.0440 | under |
| 0.25 | 1 | 0.50 | 0.0207 | +0.0207 | [+0.0031, +0.0382] | 0.0230 | under |
| 0.25 | 2 | 0.80 | 0.0285 | +0.0285 | [+0.0101, +0.0469] | 0.0285 | under |
| 0.6 | 0 | 0.00 | 0.0408 | -0.0408 | [-0.1052, +0.0235] | 0.0700 | under |
| 0.6 | 0.5 | 0.20 | 0.0303 | -0.0303 | [-0.0748, +0.0142] | 0.0544 | under |
| 0.6 | 1 | 0.50 | 0.0206 | -0.0206 | [-0.0401, -0.0012] | 0.0239 | under |
| 0.6 | 2 | 0.80 | 0.0036 | +0.0036 | [-0.0088, +0.0160] | 0.0108 | under |

**Crossing:** no in-grid crossing through style share 0.80.

Maximum cell-mean bias anywhere on the grid: 0.0408; maximum style share reached: 0.80. → `BUDGET_HOLDS`.

## 6. Second readings (declared before the run; they route nothing)

### 6.1 The other η̂ variants, same cells

| η₀ | w | prediction | η̂ (primary, P grouping) | η̂ true partition | η̂ oracle whitener | η̂ split whitener | η̂ no whitening (flat) | η̂ alignment angle |
|---|---|---|---|---|---|---|---|---|
| 0.25 | 0 | 0.250 | 0.2451 | 0.2643 | 0.2280 | 0.6836 | 0.0366 | 0.7083 |
| 0.25 | 0.5 | 0.200 | 0.2158 | 0.2331 | 0.1935 | 0.6188 | 0.0853 | 0.6839 |
| 0.25 | 1 | 0.125 | 0.1424 | 0.1587 | 0.1298 | 0.5090 | 0.1148 | 0.5667 |
| 0.25 | 2 | 0.050 | 0.0759 | 0.0918 | 0.0665 | 0.3643 | 0.1044 | 0.2210 |
| 0.6 | 0 | 0.600 | 0.5566 | 0.6052 | 0.5431 | 0.8598 | 0.2204 | 0.9073 |
| 0.6 | 0.5 | 0.480 | 0.4464 | 0.4969 | 0.4269 | 0.7582 | 0.2341 | 0.8905 |
| 0.6 | 1 | 0.300 | 0.2756 | 0.3223 | 0.2637 | 0.6029 | 0.2168 | 0.8576 |
| 0.6 | 2 | 0.120 | 0.1204 | 0.1550 | 0.1134 | 0.3965 | 0.1455 | 0.6528 |

### 6.2 The second identity energy (rho35eq) — RN-R3-1

| η₀ | w | prediction | η̂ cell mean ± sd | η̂_oracle mean | AUC | band |
|---|---|---|---|---|---|---|
| 0.25 | 0 | 0.250 | 0.2655 ± 0.1353 | 0.2473 | 1.0000 | in |
| 0.25 | 0.5 | 0.200 | 0.2239 ± 0.1053 | 0.1968 | 1.0000 | in |
| 0.25 | 1 | 0.125 | 0.1569 ± 0.0618 | 0.1218 | 1.0000 | in |
| 0.25 | 2 | 0.050 | 0.0807 ± 0.0276 | 0.0474 | 1.0000 | in |
| 0.6 | 0 | 0.600 | 0.5650 ± 0.1501 | 0.5974 | 1.0000 | in |
| 0.6 | 0.5 | 0.480 | 0.4620 ± 0.1161 | 0.4768 | 1.0000 | in |
| 0.6 | 1 | 0.300 | 0.3067 ± 0.0753 | 0.2962 | 1.0000 | in |
| 0.6 | 2 | 0.120 | 0.1303 ± 0.0270 | 0.1168 | 1.0000 | in |

Routing on the second energy: rho35eq → P1 `DILUTION_LAW_HOLDS`, P2 `PARTIAL`, P3 `BUDGET_HOLDS`. Routing invariant across energies: yes.

### 6.3 Realized design quantities

| η₀ | w | realized style share | mean ARI (provisional grouping vs generator) | mean whitener condition | worlds |
|---|---|---|---|---|---|
| 0.25 | 0 | 0.0000 | 0.8336 | 2.7264 | 8 |
| 0.25 | 0.5 | 0.1986 | 0.8056 | 2.7264 | 8 |
| 0.25 | 1 | 0.4995 | 0.7576 | 2.7264 | 8 |
| 0.25 | 2 | 0.8002 | 0.6134 | 2.7264 | 8 |
| 0.6 | 0 | 0.0000 | 0.6052 | 2.7264 | 8 |
| 0.6 | 0.5 | 0.1991 | 0.5942 | 2.7264 | 8 |
| 0.6 | 1 | 0.5002 | 0.5648 | 2.7264 | 8 |
| 0.6 | 2 | 0.8006 | 0.4783 | 2.7264 | 8 |

## 7. Certifications

**C-R3a (zero-default, A1 stop).** At w = 0 the R3 world is BIT-IDENTICAL to the unmodified L3 world (every cards_for_cell_l3 array, the taxometer's full-panel halves, and every taxometer reading). 24 world-cells × 22 compared objects each → **PASS** (A1 stop: **no**).

**G0 anchor.** R3 pipeline at w=0 re-run on L3's OWN world seeds and k-means convention, compared world-for-world to L3's committed cell artifact. Against `results/m4_l3_taxometer_meter/cell_C_rho55eq_eta0.25.csv`: 8/8 worlds matched; max |Δ η̂_P| = 8.327e-17, max |Δ η̂_T| = 5.551e-17; L3 cell mean 0.270739614140447 vs R3 cell mean 0.270739614140447 (identical: yes) → **PASS**. The residual is the committed CSV's decimal round-trip, not a pipeline difference: the cell mean recomputed from the same worlds is bit-identical.

**ID-leak scan (#83 HEAD-identical policy).** 10280 cohort IDs (universe: results/m4_sr0_recon/cohort_authors.csv, results/m4_w1_slow_transport/disjoint_cohort_authors.csv) scanned over 5 committed files, of which 3 are leg-authored (zero tolerance): **0 NEW hits**, 4 pre-existing dictionary collisions reproduced identically at HEAD, 4 raw → **PASS**. Fixed point (#83 convention): the scan is run twice and the numbers printed here are verified to be the numbers of the report that carries them — yes. The leg is synthetic and reads no corpus; the scan runs regardless.

## 8. Boundaries

- **Synthetic, card space, EXPLORATORY.** Layer V instrument world. Every number here is a property of a generator this program wrote. Nothing is transported to any corpus, and no psychological construct is named, measured or implied.

- **The style channel is planted**, isotropically, in the latent per-author vector. "Style" here is a CHANNEL LABEL for a non-trait author-persistent isotropic offset — it is not a claim about writing style, and it is not calibrated against any observed corpus.

- **What the instruments read.** From the note's 2×2:

| | trait-borne | non-trait |
|---|---|---|
| **aligned with T** | within-type trait residue | b_aligned (the L-line's η-carrier) |
| **isotropic** | — (trait lives in trait axes) | style_a (the R-line's channel); b_iso |

  η̂ reads the ROW margin (excess alignment, blind to semantics); the union reader reads PERSISTENCE — the union of every cell. **No single program instrument reads a cell.** This leg measures the two margins on the same worlds; it does not give any instrument the missing axis.

- **The band is imported, not chosen.** ±0.125 is L3's own certified error budget. A cell inside the band is not evidence the law is exact there; it is evidence the law is not distinguishable from the read at the instrument's certified resolution.

- **η₀ = 0.6 is off the L3 grid.** L3 certified η ∈ {0, .25, .5, .75, 1}; 0.6 is interpolated inside that range, not extrapolated.

- **Eight worlds per cell.** Every interval here is a Student-t interval on 8 replicates; cross-cell contrasts are exactly paired within world (shared loadings, state, noise, group assignment, type subspace, both identity draws and the style direction).

## 9. Config

```json
{
  "leg": "M4-R3",
  "banner": "synthetic worlds calibrated to an opened-panel regime, card space only, label-free, EXPLORATORY",
  "registration": "docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md section 'M4-R3', commit 4597c33",
  "derivation": "docs/SUICA_R3_IDENTITY_RECONCILIATION_NOTE.md, commit 1bbda62",
  "imported_machinery": "scripts/run_suica_m4_l3_taxometer_meter.py (UNMODIFIED, imported by file)",
  "seed": 20260819,
  "world_salt": "m4r3-world",
  "style_salt": "m4r3-style",
  "kmeans_salt": "m4r3-kmeans",
  "twodraw_salt": "m4r3-twodraw",
  "world_seed_convention": "stable_bucket(f'{SEED}-{world}', salt='m4r3-world', modulus=2**31-1) (L3's convention, disjoint salt)",
  "world_seeds": [
    1755086476,
    1292063731,
    548177571,
    678403447,
    1534838760,
    769064418,
    1732751681,
    1593555787
  ],
  "worlds_per_cell": 8,
  "w_grid": [
    0.0,
    0.5,
    1.0,
    2.0
  ],
  "eta0_grid": [
    0.25,
    0.6
  ],
  "n_authors": 512,
  "k_tau": 3,
  "d_latent": 48,
  "d_card": 64,
  "g_groups": 4,
  "n_occ": 8,
  "phi_slow": 0.9,
  "n_restart": 64,
  "w_int_arm": "zero",
  "arm_weights": {
    "mu": 0.5,
    "slow": 0.5,
    "int": 0.0,
    "common": 0.5,
    "noise": 0.5
  },
  "delta": 5.928950380606693,
  "energy_primary": "rho55eq",
  "sigma_b2": {
    "rho55eq": 16.111540782194115,
    "rho35eq": 7.098091393554051
  },
  "band_is_l3_certification_budget": 0.125,
  "l3_X2_TOL": 0.125,
  "band_equals_l3_budget": true,
  "flat_bar": 0.05,
  "flat_applies_if_pred_drop": 0.13,
  "eta_primary_key": "eta_hat_P",
  "oracle_zero_point_dT_over_D": 0.0625,
  "registered_predictions": {
    "eta0=0.25": {
      "w=0": 0.25,
      "w=0.5": 0.2,
      "w=1": 0.125,
      "w=2": 0.05
    },
    "eta0=0.6": {
      "w=0": 0.6,
      "w=0.5": 0.48,
      "w=1": 0.3,
      "w=2": 0.12
    }
  },
  "style_shares": {
    "w=0": 0.0,
    "w=0.5": 0.2,
    "w=1": 0.5,
    "w=2": 0.8
  },
  "ci_level": 0.95
}
```

**Register-notes (rule 9; pinned before any main-grid number):**

- RN-R3-1 identity energy: PRIMARY rho55eq (L2/L3 anchor family); rho35eq run in full as a declared second reading, routes nothing
- RN-R3-2 world-seed convention: L3's, salt m4r3-world, SEED 20260819, world index 0..7
- RN-R3-3 style entry point: LATENT per-author vector, alongside b, before the M-map; D = 48; skipped (not zero-scaled) at w = 0
- RN-R3-4 primary eta_hat = eta_hat_P (state-innovation whitener x provisional Lloyd grouping), L3's own primary
- RN-R3-5 oracle reader on realized b+style, d_T = 3, D = 48
- RN-R3-6 two-draw union reader: PRIMARY refreshes eps only (registration-literal); SECOND refreshes eps and the slow state
- RN-R3-7 k-means seed convention, L3's form, disjoint salt
- RN-R3-8 cell mean over 8 worlds, sd ddof=1, Student-t 95% CI
- RN-R3-9 P3 crossing by linear interpolation in style share on the cell-mean bias; second reading = mean per-world absolute bias

**Artifacts** (gitignored, `results/m4_r3_taxometer_mixtures/`): `config.json`, `config.sha256.json`, `certification_c_r3a.json`, `g0_anchor.json`, `worlds.csv`, `cells.csv`, `p1.json`, `p2.json`, `p3.json`, `id_leak_scan.json`, `decision.json`, `manifest.json`. Every table above is generated from them (rule 24).
