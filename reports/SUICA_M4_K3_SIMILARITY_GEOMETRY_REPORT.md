# SUICA M4-K3 — The similarity geometry, measured (T7/T8)

**Tier:** EXPLORATORY · label-free · synthetic throughout.
**Banner:** synthetic worlds calibrated to an opened-panel regime, exploratory.
**Registration:** `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md` § "M4-K3 — The similarity geometry,
measured (T7/T8 — the origin question's empirical stamp)", REGISTERED 2026-08-09 BEFORE RUN,
commit `740e600`. The registration text is binding; this executor did implementation and
execution only.
**Script:** `scripts/run_suica_m4_k3_similarity_geometry.py`
**Artifacts:** `results/m4_k3_similarity_geometry/` (gitignored).
**Theory:** `docs/SUICA_IDENTITY_THEORY_V1.md` T7, T8(a)–(e); appendix H (the validated
instrument); appendix L (T4 closed — K3 completes IDT v1's registered empirical program).

---

## Part 0 — gates computed 2026-08-09T11:17:42.431754+00:00 (UTC), written to disk BEFORE any main arm

Part 0 ran on **RESERVED pilot worlds 9601–9604** (the 4-world pilot convention made standing
after K2e; disjoint from main world indices 0…7). `results/m4_k3_similarity_geometry/gates.json`,
`part0_mc_predictions.csv`, `part0_pilot_world_stats.csv`,
`part0_pilot_world_stats_resolved.csv`, `part0_enumeration_leans.csv`,
`part0_enumeration_routing.csv` and `part0_tables.md` carry every number below at full
precision. The `arms` stage refuses to run unless every Part-0 gate passes **and this report
exists on disk** (`require_part0()`).

Part-0 wall time **10.961 s** (K2a anchor 0.066 s; Monte-Carlo predictions 1.781 s; pilot pass 1
4.644 s; pilot pass 2 under the resolved strata mode 4.453 s). **No hypothesis-channel run of any
kind preceded this stage** — there was no smoke run, no exploratory world, and no number from a
main world index existed at any point before this section was written.

**CARD SPACE ONLY.** The deployed gauge is never invoked in this leg.

### 0.0 Standing-rule-14 self-check (required by G5k)

**No gate and no lean in this leg compares quantities across scales or instruments.** G0k
re-derives K2a's own artifacts against K2a's own code path. G1k compares card panels to card
panels. G3k compares an estimated-card noise scale to an estimated-card noise scale and to the
card-space attenuation algebra. L-1 compares a card-space cosine sign to a card-space cosine
sign; L-2(a)/(c) compare hit rate to hit rate; L-2(b) compares a card-space cosine to a
card-space Monte-Carlo prediction in the same units; L-3 compares Spearman to Spearman; L-4
compares AUC to AUC; L-5 is a Spearman between two card-space per-author coordinates. **There is
no cross-scale gate here, so rule 14 has nothing to bind.**

### 0.1 Design as registered, and the register-notes (standing rule 9)

`master_seed` **20260820**; **3 configs × 8 worlds × 512 authors**; `n_rep = 2` events per
occasion; `K_LATENT = 48`, `DIM = 64` (inherited from K2a/F2 unchanged).

| id | cell | φ_slow | n_occ | w_int |
|---|---|---:|---:|---|
| c1 | `phi0.9_occ8_intzero` | 0.90 | 8 | 0 |
| c2 | `phi0.9_occ32_intzero` | 0.90 | 32 | 0 |
| c3 | `phi0.9_occ8_intequal` | 0.90 | 8 | equal-share |

Everything generative is K2a's, called as an imported module and **not reimplemented**:
`k2a.build_world` (k2a:184-236), `k2a.arm_weights` (k2a:129-138), `k2a.centered_channels`
(k2a:250-259), `k2a.card` (k2a:262-276), `k2a.splits` (k2a:335-340), `k2a.cell_predictions`
(k2a:343-381), `k2a.ar_mean_var/ar_set_var/ar_cross_cov` (k2a:282-300). **`suica_core` is not
touched.** Rule-12 naming: **the TRUE CARD is `cen["trait"]`** — the author-centred `mean_part`
vector (k2a:210, mirroring f2:178) — and **the ESTIMATED CARD is `k2a.card(...)`** over all
occasions and both reps.

- **RN-1 — world seeds.** `stable_bucket(f"{20260820}-{φ}-{n_occ}-{w_int}-{world}",
  salt="m4k3-world")`, a salt disjoint from K2a's `m4k2a-world`. The seed depends on
  (config, world) only, so **all six T7 arms of a world share every non-trait channel
  bit-for-bit** and the manipulation contrast is exactly paired.
- **RN-2 — the T7 operator.** Acts on `cen["trait"]`, i.e. **on the card**, per T7's own
  statement ("with all other cards FIXED, c_i ↦ α c_i"; "norm-preserving rotation of c_i").
  **No re-centring**, so every non-designated author's true card is bit-identical across arms
  (verified in G1k). Rotation: `c' = cos φ · c + sin φ · ‖c‖ · v̂` with `v̂ ⟂ c` drawn once per
  designated author and **shared between 30° and 60°** (the two angles are nested in one plane).
  Designated set: **51 of 512 authors** (10%), drawn per world from salt `m4k3-manip`.
  Arms: `base`, `scale1.5`, `scale2`, **`scaleEQ30` (α = 1.5176380902050415)**, `rot30`, `rot60`.
  *The exact same-displacement partner of a rotation by φ is a scaling by α = 1 + 2 sin(φ/2)*
  (both displace the card by 2 r sin(φ/2) = |α−1| r). **α_eq(60°) = 2.0 exactly** — already a
  registered arm — while the registration's 1.5 approximates α_eq(30°) = 1.5176380902050415 to
  3.4% **in the anti-conservative direction** for lean (c); `scaleEQ30` is added so that lean
  (c)'s "same-displacement" is exact. The registration's own α ∈ {1.5, 2} remain the arms lean
  (a) is scored on.
- **RN-3 — occasion splits.** **R = 8 distinct balanced random splits** per (config, world), salt
  `m4k3-splits`. K2a's canonical interleaved/contiguous splits are computed as SECONDARY
  readings and reported.
- **RN-4 — the identification protocol, and its PRE-DECLARED difficulty ladder.** The
  registration leaves gallery/probe/misidentification open; rule 9 requires them pinned with an
  explicit decision rule where a choice is delegated. **Closed gallery of all 512 authors, one
  direction, match = argmax cosine, rank-1 hit = the argmax is the probe's own author, a
  MISIDENTIFICATION EVENT is a rank-1 miss.** Difficulty levels (all pure K2a card machinery):
  **PA** probe = card over split half 1, gallery = card over split half 2; **PB** probe = ONE
  occasion of half 1, gallery = card over half 2; **PC** probe = ONE occasion of half 1, gallery
  = the occasion of half 2 at MAXIMAL lag. Pairings: **MATCHED** (probe and gallery from the same
  arm — T7's "the person IS different"; lean (a)) and **CROSS** (probe from the arm, gallery from
  the BASELINE enrolment — "the person changed SINCE enrolment"; lean (c), *the only pairing
  under which a norm-preserving rotation is not a no-op by isotropy*). **Ladder:** score on PA;
  if PA is DEGENERATE in any config (pooled baseline miss rate outside [0.02, 0.98], or zero
  per-author hit-rate variance — rule 10) fall to PB, then PC, applied to ALL configs so the
  strata stay comparable. Every level's numbers are reported whatever is scored. **ρ_i is ALWAYS
  PA's two-split reproducibility** (the K2a estimator), independent of the scored difficulty.
- **RN-4b (DESCRIPTIVE, NON-GATING)** — top-5 crowding readings and an r-only AUC, so L-4's
  sensitivity to "nearest competitor" vs "local density" vs "distinctiveness" is visible.
  PRIMARY stays the nearest competitor. *Added during Part 0 after the pilot's ΔAUC sign was
  seen (see anomaly A-3); declared descriptive and excluded from every gate.*
- **RN-5 — disattenuation.** ρ̄_i = mean over the R splits of cos(ĉ_i^{S1}, ĉ_i^{S2});
  **PRIMARY** divides by √(ρ̃_i ρ̃_j) with ρ̃ = clip(Spearman-Brown(ρ̄), 0.01, 1) (SB maps a
  half-card reliability to the full card the cosine is computed on). The no-SB reading is
  reported as secondary. **L-5 is invariant to this choice** — SB and clipping are monotone in
  ρ̄_i, and Spearman is rank-based.
- **RN-6 — strata (PARTITIONS, rules 15/16), computed PER WORLD on TRUE card norms r_i.**
  L-1: 3 tertiles of the pair geometric mean √(r_i r_j) → NORM-LOW / NORM-MID / NORM-HIGH (the
  direct instantiation of T8(c)'s near-norm regime). L-3: NEAR-NORM (both r in the bottom
  quintile), STRONG (both top quintile), UNEQUAL (r ratio > threshold), MID (remainder), with
  precedence UNEQUAL > NEAR-NORM > STRONG > MID so the four are disjoint; overlap counts
  enumerated below.
- **RN-7 — the UNEQUAL ladder, and its pre-declared fallback.** The registered ladder
  3 → 2.5 → 2 is run and reported. **If the last rung still yields < 200 pairs**, UNEQUAL is
  replaced by **UNEQUAL-Q = one author in the TOP r-quintile and the other in the BOTTOM
  r-quintile** — the same magnitude-mismatch regime, operationalised by quintile contrast
  rather than by an absolute ratio, disjoint from NEAR-NORM and STRONG by construction.
- **RN-8 — the noise model.** An INDEPENDENT re-implementation of the estimated-card law from
  the validated attenuation algebra (IDT appendix B / K2a `cell_predictions`), **not** a call
  into `build_world`: `ĉ = √A·c + √B·s̄ + √C·ū + √E·ē` with per-coordinate latent variances
  1, `ar_mean_var(n_occ, φ)`, `1/n_occ`, and isotropic `SIGMA_ISO²/(n_occ·N_REP)`, every channel
  centred over authors exactly as `k2a.centered_channels` does. It builds no world of this leg
  and touches no hypothesis channel. **G3k verifies its scale against the pilot worlds BEFORE
  the L-1 and L-2b predictions are consumed.**
- **RN-9 — the anti-direction check is not a tautology.** `‖c_i−c_j‖²` is computed **from the
  difference vector** and `r_i²+r_j²` **from the norms**, never by algebraic expansion. On
  ESTIMATED cards the identity `cos < 0 ⟺ d² > r_i²+r_j²` holds for *any* vectors, so the
  registered "violation rate in estimated cards" is read as the bound **used as an inference
  rule**: the estimated cards say "not anti-direction" (`d̂² ≤ r̂_i²+r̂_j²`, equivalently
  `cos θ̂ ≥ 0`) while the TRUE directions **are** opposite. That is the quantity the noise model
  predicts, and it is what T8(c) says should be large exactly in the near-norm stratum.
- **RN-10 — sub-clause → lean aggregation (CONJUNCTIVE).** any MISS → MISS; else any BOUNDARY →
  BOUNDARY; else HOLD. An UNREALIZABLE sub-clause is EXCLUDED from the conjunction and disclosed
  (a design shortfall is never scored as a theory failure).
- **RN-11 — BOUNDARY and routing.** A BOUNDARY lean (rule 13) is **not** counted as a MISS; the
  routing outcome carries the BOUNDARY tag downstream.
- **RN-12 — the underpower rule (standing rule 2, applied uniformly to EVERY clause).** Let Δ be
  the realised quantity, B the clause's decisive boundary, MDE its **realised** minimum
  detectable effect ((t_{.975,n−1}+t_{.80,n−1})·sd/√n on the same blocks). Then **HOLD** if the
  registered criterion is satisfied; **MISS** if it fails and |Δ − B| ≥ MDE (the failure is
  resolved at the design's own power); **BOUNDARY** otherwise — *"a noise-floor null is
  UNDERPOWERED, not a null"*. Rule 13's own BOUNDARY (verdict flips at 10×B) also maps to
  BOUNDARY. This rule is stated here, before any main arm, and applies to L-2c, L-3a, L-3b, L-3c
  and L-4 alike; **it does not rescue L-4**, whose pilot effect is 3.05× its own MDE.

**Bootstrap.** Blocks are (config, world); resampling is **stratified by config**, B = 2000,
seed = `MASTER_SEED`, with the ≥10×B (20 000) recheck at rule-13 boundaries. Every statistic is
a per-world scalar and the pooled statistic is the mean over resampled blocks.

### 0.2 G0k — construction and the K2a anchor: **PASS**

- **Five-channel reconstruction residual (max over 12 pilot world-builds): 2.220446049250313e-16**
  — criterion ≤ 1e-12.
- **K2a anchor re-derived BIT-EXACTLY.** `results/m4_k2a_expressive_world/cell_phi0.9_occ8_intzero.csv`,
  **2048 rows × 35 columns**, re-derived through K2a's own `world_seed_for` /
  `suff_stats_for_world` at K2a's own `master_seed = 20260815`, read back with
  `float_precision="round_trip"`: **column list identical, max |residual| = 0.0, 35/35 columns
  bit-exact.** K2a's published pooled statistics for that cell re-derived through K2a's own
  `pooled_stats`, **max residual 0.0** on all eight:

  | statistic | published = re-derived |
  |---|---|
  | `gap` | 0.09302852291619967 |
  | `rho_interleaved` | 0.9228727932446795 |
  | `rho_contiguous` | 0.8298442703284798 |
  | `r_card_b_raw` | 0.7356436826896012 |
  | `r_card_b_cen` | 0.7370474868136508 |
  | `rho_same_occ` | 0.9341881819136586 |
  | `gap_cos` | 0.09436146465759876 |
  | `gap_pearson` | 0.09302852291619967 |

- **Per-stratum pair counts (grain, rule 5).** 130 816 pairs per world (512 authors). L-1
  tertiles per world: **43 606 / 43 605 / 43 605** in every config. L-3 under the registered
  definition per world: NEAR-NORM **5 253**, STRONG **5 253**, MID **120 310**, **UNEQUAL 0**.

### 0.3 G1k — non-degeneracy (rule 10), strata, and the two ladders: **PASS**

- **Rule 10, the T7 operator is live and exactly paired:** every non-designated author's true
  card is **bit-identical across all six arms** (max |Δ| = 0.0); the minimum designated-author
  card RMS change over all arms and pilot worlds is **0.08540117597664273** (≫ 1e-6); the induced
  group-norm drift (the price of not re-centring, per RN-2) is at most
  **0.007818732296240796** per coordinate.
- **THE REGISTERED UNEQUAL STRATUM IS UNREALIZABLE IN THIS WORLD FAMILY.** Pairs with r-ratio
  above each rung, pooled over the 4 pilot worlds × 3 configs (1 569 792 pairs):
  **ratio > 3 → 0; ratio > 2.5 → 0; ratio > 2 → 19.** The largest r-ratio observed anywhere in
  the pilot is **2.1368466268097563**. The full registered ladder therefore fails the ≥200-pair
  gate at every rung, and **RN-7's pre-declared fallback UNEQUAL-Q activates** (`uneq_mode =
  "quintile"`). *This is a registration defect, not a result: F2's family draws every author's
  trait latent from the same N(0, I_48), so distinctiveness is near-homogeneous by construction
  (r has relative sd ≈ 0.10) and the absolute magnitude-mismatch regime T8 names does not exist
  at these thresholds.* Recorded as defect **#25** in §3.
- **Strata under the resolved mode, pooled over 4 pilot worlds, identical in all 3 configs:**
  NEAR-NORM **21 012**, UNEQUAL-Q **41 616**, STRONG **21 012**, MID **439 624** — all ≥ 200.
  L-1 tertiles ≥ 174 420 pooled. **Overlaps under the registered definition: 0 / 0 / 0**
  (UNEQUAL×NEAR, UNEQUAL×STRONG, NEAR×STRONG) — the precedence never had to be invoked.
- **THE REGISTERED IDENTIFICATION TASK IS AT CEILING; RN-4's LADDER FALLS TO PC.** Pooled
  baseline miss rate and minimum per-author hit-rate variance, per level and config:

  | level | c1 miss / var | c2 miss / var | c3 miss / var | non-degenerate? |
  |---|---|---|---|---|
  | PA (split-half) | **0.0** / 0.0 | **0.0** / 0.0 | 0.0001220703125 / 0.0 | NO |
  | PB (one-occasion probe) | 0.0001220703125 / 0.0 | 0.0072021484375 / 0.0010137557983398438 | 0.04296875 / 0.010023534297943115 | NO |
  | **PC (one-vs-one @ max lag)** | **0.02752685546875** / 0.007656097412109375 | **0.4619140625** / 0.12196248769760132 | **0.403564453125** / 0.075711190700531 | **YES** |

  At the split-half protocol the card identifies its author **perfectly** — 0 misses in 512
  authors × 8 splits × 4 worlds in both no-interaction configs — so the registered "per-author
  rank-1 hit rate" would have been a constant and L-2(a), L-4 and L-5 would all have been
  arithmetically unscorable. **PC is scored; PA and PB are reported everywhere.** Recorded as
  defect **#26** in §3.

### 0.4 G3k — noise-model liveness (rule 3), BEFORE the predictions are consumed: **PASS**

Every estimated-card noise-scale statistic, noise model vs the pilot worlds, and the pilot worlds
vs the closed-form attenuation algebra. Criterion |relative error| ≤ 0.02; **realised maximum
0.008190068766055221**.

| config | ‖ĉ‖² model vs world | r̄ model vs world | sd(cos θ̂) model vs world | own-dir cos model vs world | card_var_norm vs algebra | attenuation vs algebra |
|---|---:|---:|---:|---:|---:|---:|
| c1 | +0.0024415698630133507 | +0.0019273801942743226 | +0.0016949309632095099 | +0.0025942937054299225 | −0.003331947035577338 | −0.007812747298397232 |
| c2 | −0.000028582918059868542 | −0.003930375738044131 | −0.00025767324439539095 | −0.0007513712822727213 | −0.0020983646958707314 | −0.003052099202137083 |
| c3 | +0.006933656125284276 | +0.0007378137582434824 | −0.0013191702945265578 | +0.0002455883868048386 | −0.008190068766055221 | −0.006608792476355899 |

Absolute anchors (pilot worlds): card attenuation **0.732308520075803 / 0.8308968091742818 /
0.7094404590791521** against the appendix-B algebra's **0.7380749128572432 / 0.8334405524193496 /
0.7141601956067911**. **The validated algebra is live at K3's own configs, so the L-1 and L-2b
Monte-Carlo predictions rest on a verified input.**

### 0.5 Part-0 Monte-Carlo predictions (40 replicate 512-author populations per config)

**L-1 — estimated-card violation rate** (the bound used as an inference rule, RN-9):

| config | NORM-LOW | NORM-MID | NORM-HIGH |
|---|---:|---:|---:|
| c1 | **0.16595709306058798** ± 0.000338959335101381 | **0.1574079807361541** ± 0.0003514621286447617 | **0.1495568168787983** ± 0.00031772530317063507 |
| c2 | **0.13590044947942942** ± 0.0002795299082522397 | **0.12735810113519092** ± 0.0002976816152401813 | **0.11969842907923404** ± 0.0002510213100639733 |
| c3 (descriptive) | 0.1727571893776086 ± 0.00032595528706326 | 0.16467492260061917 ± 0.00030859248492764194 | 0.15666036005045295 ± 0.00029367485882117537 |

The prediction is **monotone decreasing in the pair norm** in every config — T8(c)'s "where
distance and direction can disagree, neither is readable" as a quantitative ordering, predicted
before any main world existed.

**L-2b — own-direction match, cos φ_rot × attenuation** (Monte-Carlo, with the ratio-of-
expectations closed form beside it):

| config | base | rot30 (MC / closed form) | rot60 (MC / closed form) |
|---|---:|---:|---:|
| c1 | 0.7342083434598684 | **0.6352503830035988** / 0.6391916244303585 | **0.36623579777050147** / 0.3690374564286217 |
| c2 | 0.8302724971733362 | **0.7186198881065604** / 0.7217806909392929 | **0.4147025248233634** / 0.4167202762096749 |
| c3 | 0.7096146894170314 | **0.61403602580516** / 0.6184808717671451 | **0.3541573869608272** / 0.3570800978033956 |

Pooled (equal blocks per config) predictions scored against: **rot30 0.6559687656384188**,
**rot60 0.3783652365182307**. MC standard errors ≤ 0.00066.

### 0.6 G2k — power (4-world pilot), rule-11 satisfiability with directions, rule-13 spec: **PASS, with one rule-11 flag**

B = 2000, seed = `MASTER_SEED`, ≥10×B = 20 000 at boundaries. **23 clauses.** MDE =
(t_{.975,n−1}+t_{.80,n−1})·sd_pilot/√n at the main design's n (8 world-blocks per config,
12 for pooled clauses).

| clause | pilot sd | n | MDE(80%,.05) | pilot point | registered direction |
|---|---:|---:|---:|---:|---|
| L-1 c1 NORM-LOW containment | 0.00323501 | 8 | 0.00372937 | 0.1651435582259322 | contains 0.16595709306058798 |
| L-1 c1 NORM-MID | 0.002614 | 8 | 0.00301346 | 0.15840499942667124 | contains 0.1574079807361541 |
| L-1 c1 NORM-HIGH | 0.00301391 | 8 | 0.00347448 | 0.1504930627221649 | contains 0.1495568168787983 |
| L-1 c2 NORM-LOW | 0.00248975 | 8 | 0.00287022 | 0.13657524193918266 | contains 0.13590044947942942 |
| L-1 c2 NORM-MID | 0.0027551 | 8 | 0.00317612 | 0.12840270611168444 | contains 0.12735810113519092 |
| L-1 c2 NORM-HIGH | 0.00160011 | 8 | 0.00184463 | 0.11925811260176586 | contains 0.11969842907923404 |
| L-2a scale1.5 [PC/MATCHED] | 0.178213 | 12 | 0.158273 | **+0.264297385620915** | one-sided CI lower ≥ −0.01 |
| L-2a scale2 [PC/MATCHED] | 0.202365 | 12 | 0.179723 | **+0.3049428104575163** | one-sided CI lower ≥ −0.01 |
| L-2b rot30 | 0.0451549 | 12 | 0.0401027 | 0.6538682069484102 | contains 0.6559687656384188 |
| L-2b rot60 | 0.0241122 | 12 | 0.0214144 | 0.37518878565968516 | contains 0.3783652365182307 |
| L-2c rot30 vs scaleEQ30 [PC/CROSS] | 0.140306 | 12 | 0.124608 | **−0.25592320261437906** | < 0, CI excludes 0 |
| L-2c rot60 vs scale2 [PC/CROSS] | 0.168828 | 12 | 0.149938 | **−0.6147875816993464** | < 0, CI excludes 0 |
| L-3b c1 NEAR-NORM | 0.0092772 | 8 | 0.0106949 | 0.11448330800519214 | ≥ 0.10, CI excludes 0 |
| L-3b c1 UNEQUAL-Q | 0.0114366 | 8 | 0.0131843 | 0.1294279238826852 | ≥ 0.10, CI excludes 0 |
| L-3b c2 NEAR-NORM | 0.00992622 | 8 | 0.0114431 | 0.1392413701971995 | ≥ 0.10, CI excludes 0 |
| L-3b c2 UNEQUAL-Q | 0.0128726 | 8 | 0.0148398 | 0.14358441913027484 | ≥ 0.10, CI excludes 0 |
| L-3b c3 NEAR-NORM | 0.0048081 | 8 | 0.00554285 | **0.09205443575521045** | ≥ 0.10, CI excludes 0 |
| L-3b c3 UNEQUAL-Q | 0.0117533 | 8 | 0.0135493 | 0.1248153546334613 | ≥ 0.10, CI excludes 0 |
| L-3c c1 sign | 0.0055504 | 8 | 0.00639859 | **+0.004567212943886573** | < 0, CI excludes 0 |
| L-3c c2 sign | 0.0494216 | 8 | 0.056974 | −0.04950109618746818 | < 0, CI excludes 0 |
| L-3c c3 sign | 0.0714478 | 8 | 0.0823662 | −0.028190269805350467 | < 0, CI excludes 0 |
| L-4 ΔAUC [PC] | 0.0526807 | 12 | 0.0467864 | **−0.14281436869910788** | > 0, CI excludes 0 |
| L-5 Spearman [PC] | 0.150353 | 12 | 0.133531 | **+0.5309308546866448** | ≥ 0.30, CI lower > 0.15 |

**Rule-11 flag (3 clauses): L-3c in all three configs.** The pilot's rank-error-vs-magnitude-share
Spearman (+0.0046 / −0.0495 / −0.0282) is **smaller than its own MDE** (0.0064 / 0.0570 / 0.0824),
so the design cannot resolve L-3(c) at n = 8 worlds. Under **RN-12** an unresolved failure there
scores **BOUNDARY**, not MISS. The mechanism is visible in the pilot: even inside the UNEQUAL-Q
stratum the magnitude term `(r̂_i−r̂_j)²` carries only **2.10% / 2.71% / 1.92%** of squared
estimated-card distance, because this world family's distinctiveness is near-homogeneous
(defect #25 again).

**No other clause is flagged.** Every other signed clause's pilot point exceeds its own MDE
(L-2a 1.67×/1.70×, L-2c 2.05×/4.10×, L-3b 10.7×/9.8×/12.2×/9.7×/16.6×/9.2×, L-4 3.05×, L-5 3.98×).

**Disclosed at Part 0, before any main arm: the pilot's L-4 ΔAUC sign is the OPPOSITE of the
registered lean** (−0.1428, i.e. distance crowding beats angular crowding), and it is 3.05× its
own MDE. Angular AUC on the pilot is **0.49683 — chance** — while distance AUC is **0.639644**
and the pure-distinctiveness AUC(−r_i) is **0.667483**. The descriptive top-5 and estimated-card
readings agree (Δ = −0.164326 and −0.205384). **No design change was made in response** (see
anomaly A-3).

### 0.7 G4k — the rule-16 enumeration (the full adjudication object): **PASS**

Two layers, both generated programmatically into
`part0_enumeration_leans.csv` and `part0_enumeration_routing.csv`.

- **Layer A — sub-clause → lean.** Every combination of sub-clause states in
  {HOLD, MISS, BOUNDARY, UNREALIZABLE} for each lean's sub-clauses (L-1: 1; L-2: 6 = 2 α + 2 φ +
  2 displacement pairs; L-3: 4 = a + b·NEAR-NORM + b·UNEQUAL + c; L-4: 1; L-5: 1), i.e.
  4 + 4096 + 256 + 4 + 4 = **4364 rows, 4364 expected, 4364 unique keys, all assigned — 0 gaps,
  0 overlaps.**
- **Layer B — (true-card identity, five lean states) → route.** 2 × 3⁵ = **486 rows, 486
  expected, 486 unique keys, all assigned — 0 gaps, 0 overlaps.** Route counts:
  **P1 243, P2 131, P3 80, P4 32; all four routes reachable.** A result fitting no registered
  branch is structurally impossible.

Routing precedence, exactly as registered: **P1** if the TRUE-card identity fails (VOID);
else **P2** if ≥2 of {L-1(noise law), L-2, L-3, L-4, L-5} MISS; else **P3** if exactly 1 MISS
(QUALIFIED); else **P4** (T7/T8 [MEASURED]). BOUNDARY leans are not MISSes and carry their tag
downstream (RN-11).

### 0.8 G5k — hygiene: **PASS**

Round-trip parsing (`float_precision="round_trip"`) on every artifact read; foreground chunked
stages, longest Part-0 sub-stage 4.644 s (limit 600 s); rule-12 source-object header (§0.1);
rule-14 self-check (§0.0); **0 background jobs, 0 monitors**.

**Part-0 verdict: G0k ✓ G1k ✓ G2k ✓ G3k ✓ G4k ✓ G5k ✓ — `part0_all_pass = true`.**
Two registration defects (#25, #26) were resolved by pre-declared decision rules before any
hypothesis-relevant main-world number existed. The arms may run.

---

## Part 1 — arms

Three chunked foreground stages, all far inside the 600 s limit and inside every Part-0 estimate:
**c1 8 worlds in 2.38 s · c2 8 worlds in 4.23 s · c3 8 worlds in 2.55 s**; finalize 0.708 s.
**24 (config, world) blocks · 12 288 authors · 3 139 584 true-card pairs · 6 arms × 8 splits ×
3 protocols × 2 pairings per world.** No re-runs, no background jobs, no monitors, no stage over
2× its Part-0 estimate.

Artifacts: `worldstats_<cell>.csv` (per-world scalars, the bootstrap blocks),
`authors_<cell>.csv` (per-author grain: r, ρ̄, ρ_SB, crowding coordinates, per-arm hit rates and
own-direction cosines), `decision.json`, `manifest.json`.

## Part 2 — results

### L-1 (anti-direction bound, T8b) [prior .90] — **HOLD**

**THE TRUE-CARD IDENTITY IS EXACT: violation count = 0 out of 3 139 584 pairs, in all 24
worlds.** No P1. The check is not a tautology (RN-9): `‖c_i−c_j‖²` came from the difference
vector and `r_i²+r_j²` from the norms, and the smallest absolute slack anywhere was
**3.100077310413951e-07** — i.e. the closest any pair came to the boundary was seven orders of
magnitude above double-precision noise, so the count 0 is a structural zero, not a rounding
accident. The bound is a *live* constraint here, not a vacuous one: **50.48%** of all pairs are
genuinely anti-direction (cos θ_true < 0), and every single one of them satisfies
‖c_i−c_j‖² > r_i²+r_j². The same identity checked on ESTIMATED cards gave **0 mismatches** in
either direction, confirming it is an algebraic property of any vectors and therefore that the
registered "violation rate in estimated cards" must be the inference-rule reading (RN-9).

**The noise law: 6/6 strata within the Part-0 Monte-Carlo CI** (threshold ≥5/6).

| config:stratum | measured | 95% CI | Part-0 MC prediction | \|error\| |
|---|---:|---|---:|---:|
| c1:NORM-LOW | 0.16607806265192865 | [0.16454150518277302, 0.16794162500573317] | 0.16595709306058798 | 0.00012096959134066942 |
| c1:NORM-MID | 0.15737874097007226 | [0.1562234118793716, 0.1585598698543745] | 0.1574079807361541 | 0.000029239766081851082 |
| c1:NORM-HIGH | 0.14941233803462906 | [0.14833147001490654, 0.1504730678821236] | 0.1495568168787983 | 0.00014447884416923795 |
| c2:NORM-LOW | 0.1354716094115489 | [0.1346918285327707, 0.13643205636838968] | 0.13590044947942942 | 0.0004288400678805204 |
| c2:NORM-MID | 0.12734778121775026 | [0.12611756105951152, 0.12819344111913772] | 0.12735810113519092 | 0.000010319917440659854 |
| c2:NORM-HIGH | 0.11977984176126591 | [0.11895990998738677, 0.1204535747047357] | 0.11969842907923404 | 0.00008141268203186447 |

**Largest error 0.00043; the predicted monotone ordering in pair norm is reproduced exactly in
both configs** (0.1661 > 0.1574 > 0.1494 and 0.1355 > 0.1273 > 0.1198). T8(c) is now a measured
quantity: the "distance-close but direction-opposite" inference fails **16.6%** of the time among
the least distinctive pairs and **11.98%** among the most distinctive, and the validated
attenuation algebra predicts the whole surface to four decimals *before the worlds existed*.

**Descriptive (c3, the interaction-share config, not gated):** 0.17119490437095813 /
0.16403508771929826 / 0.15555555555555556 against predictions 0.1727571893776086 /
0.16467492260061917 / 0.15666036005045295 — the ordering is again exact and errors are
0.00156 / 0.00064 / 0.00110, but the CI contains the prediction in only **1 of 3** strata: with
the person×occasion channel live, the measured violation rate runs **slightly BELOW** the model,
i.e. the model marginally over-states the damage the interaction channel does to direction
reading. Sub-0.002 in absolute terms, and outside L-1's registered 6 strata.

### L-2 (caricature vs rotation, T7) [prior .80] — **HOLD** (all six sub-clauses)

Scored at protocol **PC** (RN-4's ladder), 51 designated authors per world, 24 blocks.

**(a) Caricature never hurts — and helps a lot.** α = 1.5: Δ hit rate
**+0.26521650326797386**, one-sided 95% lower **+0.25071486928104575** (floor −0.01), CI
[+0.24744434232026147, +0.28115042892156860]; baseline 0.6993464052287582 → 0.9645629084967320.
α = 2: Δ **+0.29901960784313725**, one-sided lower **+0.28380310457516340**, CI
[+0.28124744689542486, +0.31607434640522875]; → 0.9983660130718954. **Scaling a person's card by
2 takes them from a 30% miss rate to a 0.16% miss rate.** All readings agree in sign
(PA +0.0/+0.0 at ceiling, PB +0.0167/+0.0182, PC/CROSS +0.151/+0.204).

**(b) Rotation degrades own-direction match as cos φ × attenuation — to three decimals.**

| angle | measured cos(ĉ_rot, c_true) | 95% CI | Part-0 MC prediction | \|error\| | closed form | cos φ |
|---|---:|---|---:|---:|---:|---:|
| 30° | **0.6539858793019451** | [0.6494936942373705, 0.6584810040058980] | 0.6559687656384398 | 0.0019828863364946825 | 0.6598177290455988 | 0.8660254037844387 |
| 60° | **0.3752800977082475** | [0.3696953138252358, 0.3806349344020846] | 0.3783652365182307 | 0.0030851388099831790 | 0.3809459434805640 | 0.5000000000000001 |

Both CIs contain their predictions. The measured **ratio to the unrotated baseline**
(0.7558388139282565) is **0.8652451650412608** at 30° and **0.4965081056870265** at 60°, against
cos 30° = 0.8660254037844387 and cos 60° = 0.5 — **errors of 0.00078 and 0.00349 on a pure
theorem constant**. Per config the containment is uniform (c1 0.6328/0.3630 vs 0.6353/0.3662;
c2 0.7194/0.4145 vs 0.7186/0.4147; c3 0.6097/0.3483 vs 0.6140/0.3542).

**(c) At equal displacement, rotation is catastrophic and scaling is a gift.** 30° (displacement
0.5176380902050415 r, matched by α = 1.5176380902050415): Δ = **−0.2505106209150327**, CI
[−0.2617442810457516, −0.2383578431372549]; hit rates 0.6017156862745098 (rotated) vs
0.8522263071895425 (scaled). 60° (displacement 1.0 r, matched EXACTLY by α = 2): Δ =
**−0.6095792483660131**, CI [−0.6222452001633987, −0.5959967320261438]; 0.2940155228758170 vs
0.9035947712418301. **Both CIs exclude 0 with the registered sign.** The dissociation is the
whole content of T7: the same displacement of the card, spent on magnitude, raises rank-1 from
0.699 to 0.904; spent on direction, it drops it to 0.294.

*Protocol note (reported, not gated): under MATCHED pairing a norm-preserving rotation is a
no-op by isotropy (PA/MATCHED Δ = 0.0 exactly), which is why RN-4 pins (c) on CROSS — the
enrolment-on-file pairing is the only one in which "same displacement" is a meaningful contrast.*

### L-3 (disattenuated distinctive cosine, T8d) [prior .75] — **BOUNDARY**

Strata under RN-7's fallback UNEQUAL-Q (defect #25). Per-world Spearman over 5 253 / 10 609 /
5 253 / 109 701 pairs, pooled over 8 worlds per config.

**(a) The disattenuated distinctive cosine beats raw deviation distance in ALL 12 strata —
12/12, no exceptions.** HOLD.

| config:stratum | Spearman(true cos, disatt. cosine) | Spearman(true cos, −raw distance) | Δ | 95% CI |
|---|---:|---:|---:|---|
| c1:NEAR-NORM | 0.448256589196397 | 0.3402069672356703 | 0.10804962196072668 | [0.09897247399504375, 0.11843831788944181] |
| c1:UNEQUAL-Q | 0.5190826993454845 | 0.389962029247936 | 0.12912067009754852 | [0.12082093120800383, 0.13638527775620020] |
| c1:STRONG | 0.5981519413623593 | 0.4582437864934724 | 0.1399081548688869 | [0.13117199906605800, 0.14788007010512633] |
| c1:MID | 0.5292016279980978 | 0.3808787490346696 | 0.14832287896342805 | [0.14473797553022222, 0.15247935676904814] |
| c2:NEAR-NORM | 0.6034123390140134 | 0.45646498549433623 | 0.14694735351967717 | [0.13508399955600262, 0.15885993823821410] |
| c2:UNEQUAL-Q | 0.6681168461407303 | 0.5112346382061184 | 0.15688220793461183 | [0.14777756060991470, 0.16626103562673128] |
| c2:STRONG | 0.7386336759040075 | 0.5842649612395237 | 0.15436871466448385 | [0.14327801303456067, 0.16633360542050302] |
| c2:MID | 0.6782017666930815 | 0.4880849884572668 | 0.19011677823581477 | [0.18616434812238192, 0.19402882820243478] |
| c3:NEAR-NORM | 0.4050872366214323 | 0.298873767198753 | 0.10621346942267929 | [0.10165507620379016, 0.11061434083534315] |
| c3:UNEQUAL-Q | 0.4898476453284791 | 0.3634921028605437 | 0.12635554246793543 | [0.11720875532251535, 0.13644541301461535] |
| c3:STRONG | 0.5678352447741143 | 0.4288717508520796 | 0.13896349392203466 | [0.12653849813766155, 0.15341875907463567] |
| c3:MID | 0.4949013739181639 | 0.35442826392101484 | 0.14047310999714904 | [0.13745866565336148, 0.14408828387863706] |

**(b) The margin is MATERIAL in both sign-predicted failure regimes, in all three configs —
6/6 HOLD.** NEAR-NORM Δ = 0.10804962196072668 / 0.14694735351967717 / 0.10621346942267929 and
UNEQUAL-Q Δ = 0.12912067009754852 / 0.15688220793461183 / 0.12635554246793543, every point ≥ the
0.10 margin and every CI excluding 0. The tightest call is **c1:NEAR-NORM at 0.1080** — 3.45
MC-sd from the margin, the leg's closest approach; rule 13's ≥10×B recheck was not triggered
(threshold 2 MC-sd).

*Secondary readings (RN-5): the Spearman-Brown and no-SB disattenuations and the plain raw
cosine agree to ≤ 0.0009 everywhere — at these ρ̄ levels (0.898 / 0.954 / 0.796) the
disattenuation's benefit over the raw cosine is negligible, and **the entire 0.10–0.19 margin
over raw distance comes from using ANGLE rather than DISTANCE, not from the ρ correction.***

**(c) UNDERPOWERED — BOUNDARY, per RN-12 / standing rule 2.** The directional decomposition's
signed statistic (Spearman between raw distance's rank error and the pair's magnitude share) is
**−0.01694017094962738** CI [−0.03352520660784818, +0.00954685330033195] in c1 (MDE
0.03861288466450699, |Δ|/MDE = 0.44 → **BOUNDARY**); **−0.04621816130011088** CI
[−0.07111762978594310, −0.02459518791877905] in c2 (**HOLD**, correct sign, CI excludes 0);
**−0.020796856607491712** CI [−0.04449647314605348, +0.00468106207217058] in c3 (MDE
0.04292357670645535, |Δ|/MDE = 0.48 → **BOUNDARY**). All three signs are as predicted in the
point estimate except c1's, which is also negative. **The reason is a world fact, flagged at
Part 0 (rule-11 flag) and confirmed here: the magnitude channel barely exists.** Mean magnitude
share `(r̂_i−r̂_j)²/‖ĉ_i−ĉ_j‖²` even inside the UNEQUAL-Q stratum is **0.0200 / 0.0270 / 0.0201**,
against 0.0087 / 0.0083 / 0.0093 in NEAR-NORM and 0.0076 / 0.0064 / 0.0088 in STRONG. Raw
distance in this world family is **97–99% direction**, so there is almost no magnitude error for
the decomposition to attribute. Conjunctively (RN-10), L-3 = **BOUNDARY**.

### L-4 (angular vs distance crowding, T8e) [prior .70] — **MISS**

**ΔAUC = −0.13660955666602007, CI [−0.15360262438180616, −0.12045724498671546]** — the CI
excludes 0 **on the wrong side**, at 2.92× the clause's realised MDE. This is a resolved
refutation, not a null: RN-12 does not apply.

| reading | AUC angular | AUC distance | ΔAUC |
|---|---:|---:|---:|
| **PC, TRUE cards (PRIMARY)** | **0.5004568269748008** | **0.6370663836408208** | **−0.13660955666602007** |
| PC, ESTIMATED cards | 0.5141770651311098 | 0.7327394993600193 | −0.2185624342289096 |
| PC, top-5 (descriptive) | 0.49917319478827676 | 0.6558649496967002 | −0.15669175490842335 |
| PA (ceiling protocol) | 0.6624745624745625 | 0.721082621082621 | −0.05860805860805859 |
| PB | 0.49247189201695196 | 0.7078854050974824 | −0.21541351308053047 |

Per config at PC: c1 0.5068992155890785 / 0.6594086259487701 (Δ −0.15250941035969162, miss rate
0.027069091796875); c2 0.4931485270529565 / 0.6414769988311553 (Δ −0.14832847177819874, miss rate
0.465301513671875); c3 0.5013227382823672 / 0.6103135261425370 (Δ −0.10899078786016980, miss rate
0.396301269531250). **Every reading, every config, every protocol has the same sign.**

**Angular crowding of the true gallery is at CHANCE (0.5005).** And the descriptive control
(RN-4b) explains why distance crowding is not the winner it looks like: the AUC of **pure
distinctiveness −r_i is 0.6642618045442069** — *higher than distance crowding's 0.6371*. Distance
crowding carries **no crowding information beyond the probe's own norm**; it is a disguised
readability measure, and it wins only because readability is what actually drives
misidentification here. At PA the pattern shifts (angular 0.662 does beat chance) but distance
still wins and −r_i wins outright (0.797).

### L-5 (menagerie, T6/ρ) [prior .80] — **HOLD**

**Spearman(ρ_i, per-author rank-1 hit rate) = 0.5398496888120623, CI [0.5224112257093820,
0.5552609497288873]** — point ≥ 0.30 and CI lower **0.522 > 0.15** with room to spare. Per
config **0.36873772221036416 / 0.5591395467057239 / 0.6916717975200989**. Secondary ρ readings
(K2a's canonical splits, RN-3): interleaved 0.4234870609682624, contiguous 0.5436502167104303.
Across protocols: PA 0.07278050787500535 (the ceiling protocol, where hit rate is nearly
constant), PB 0.2960724814671313, PC 0.5398496888120623. **Readability predicts who gets
identified — the menagerie coordinate is real and it is the strongest per-person predictor this
leg measured.**

### Rule 13

**B = 2000, seed = `MASTER_SEED`, ≥10×B = 20 000 at boundaries. 23 clauses, 0 TRIGGERED, 0
rule-13 BOUNDARY.** Closest approaches (MC-sd of the deciding endpoint from the clause
boundary): **3.451** (L-3b c1:NEAR-NORM margin), 6.274 (L-3c c3), 11.674 (L-3b c3:NEAR-NORM),
13.841 (L-2b rot60 containment), 13.870 (L-3c c1) — all above the 2 MC-sd trigger, so no
10×B recheck was required. The **2 BOUNDARY scorings in this leg (L-3c c1, L-3c c3) come from
RN-12 (standing rule 2, underpower), not from rule 13**; `decision.json`'s `rule13.n_boundary`
counts both and is disambiguated here.

### Routing

| lean | state |
|---|---|
| L-1 (anti-direction bound + noise law) | **HOLD** |
| L-2 (caricature vs rotation) | **HOLD** |
| L-3 (disattenuated distinctive cosine) | **BOUNDARY** (a HOLD 12/12, b HOLD 6/6, c UNDERPOWERED) |
| L-4 (angular vs distance crowding) | **MISS** |
| L-5 (menagerie) | **HOLD** |

TRUE-card identity OK → no P1. Exactly **1 MISS** (BOUNDARY is not a MISS, RN-11) → **P3:
QUALIFIED — T7/T8 move to [MEASURED except the named piece]; the missing piece (T8e, the
crowding claim) gets its own follow-up charter.**

**Verdict slug: `L1_HOLD__L2_HOLD__L3_BOUNDARY__L4_MISS__L5_HOLD__P3`.**

## Part 3 — defects, anomalies, and the brief to the planner

### Registration defects (recorded, not repaired)

- **#25 — the UNEQUAL stratum is unrealizable in this world family, at every rung of its own
  ladder.** r-ratio > 3 → 0 pairs; > 2.5 → 0; > 2 → 19 out of 1 569 792 pilot pairs; largest
  ratio anywhere 2.1368466268097563 (main arms: 1.9874524383338983). F2's family draws every
  author's trait latent from the same N(0, I₄₈), so ‖c‖² is a fixed weighted χ² with relative sd
  ≈ 0.21 and the absolute magnitude-mismatch regime T8(a) names **does not exist** at these
  thresholds. Rule-11 family (a gate the anchor statistics make unsatisfiable), caught at Part 0
  by the registration's own ≥200-pair gate, resolved by RN-7's pre-declared quintile-contrast
  fallback. **Instrument boundary for the planner: heterogeneous distinctiveness is a new
  generator requirement, not a knob this family has.**
- **#26 — the registered rank-1 identification task is at ceiling, so L-2(a), L-4 and L-5 were
  arithmetically unscorable as posed.** At the split-half protocol the card identifies its author
  perfectly (0 misses in 512 authors × 8 splits × 4 pilot worlds in both no-interaction configs;
  3.05e-05 pooled miss rate in the main arms), making "per-author rank-1 hit rate" a constant.
  Same rule-11 family as #12. Resolved by RN-4's pre-declared difficulty ladder, which fell to
  PC (one-vs-one at maximal occasion lag; miss rates 0.027 / 0.465 / 0.396).

### Anomalies, all with timing

- **A-1 (pre-Part-0, no world of this leg built).** `--stage part0` was invoked three times.
  Invocation 1 (before any K3 world existed) died with a `KeyError` on a K2a `cells.csv` column
  name while assembling the G0k anchor table; it built K2a's own anchor worlds and nothing else.
  Invocation 2 ran Part 0 to completion. Invocation 3 re-ran it after two Part-0 **completeness**
  patches (below). **All three touched only RESERVED pilot worlds 9601–9604 and K2a's own anchor
  cell; no main world index was generated at any point, and this report's Part 0 was written
  after invocation 3 and before the first arm.**
- **A-2 (Part 0, before any main arm, before any hypothesis number existed).** Two gaps in this
  executor's own Part-0 objects were found and closed: (i) G2k's MDE table had no rows for the
  L-3(b) UNEQUAL clauses or for L-3(c), because pilot pass 1 ran under the *registered* UNEQUAL
  definition whose stratum is empty — fixed by a second pilot pass on the SAME reserved worlds
  under the resolved mode (`part0_pilot_world_stats_resolved.csv`); (ii) `max_mde` and the
  rule-11 scan were not NaN-safe. Neither changed any registered criterion.
- **A-3 (Part 0, after the pilot's L-4 sign was visible, before any main arm).** The pilot's
  ΔAUC came out **negative** (−0.1428, 3.05× its own MDE) — the opposite of the registered lean.
  **No design change was made in response.** Two descriptive, explicitly non-gating readings were
  added (RN-4b: top-5 crowding, and the AUC of −r_i), and the sign was disclosed in Part 0 §0.6
  before the arms ran. The main arms reproduced it (−0.1366) and the descriptive control turned
  out to be the explanation.
- **A-4 (Part 0, rule-11 flag, before any main arm).** L-3(c) was flagged unsatisfiable at n = 8
  worlds in all three configs (pilot points 0.0046 / 0.0495 / 0.0282 against MDEs
  0.0064 / 0.0570 / 0.0824). RN-12 — the uniform application of standing rule 2 — was written
  into Part 0 **before** the arms, and it scored c1 and c3 BOUNDARY as designed. RN-12 is applied
  to every clause in the leg, and it did **not** rescue L-4.
- **A-5 (Part 0, construction).** The registration's α ∈ {1.5, 2} is not the exact
  same-displacement partner set for φ ∈ {30°, 60°}: α_eq(60°) = 2 exactly, but α_eq(30°) =
  1.5176380902050415, so the registered 1.5 under-displaces by 3.4% **in the direction that
  favours lean (c)**. Arm `scaleEQ30` was added so that (c) is exact; the registration's own arms
  remain what (a) is scored on. Both readings are reported and agree.
- **A-6 (finalize, after the numbers existed).** `decision.json`'s `rule13.n_boundary = 2`
  counts RN-12 underpower boundaries, of which rule 13 itself contributed **zero**; disambiguated
  in Part 2. No repair attempted.

No crashes after A-1, no re-runs of any arm, no background jobs, no monitors, no stage over its
Part-0 estimate. Total compute ≈ 21 s (Part 0 10.961 s + arms 9.16 s + finalize 0.708 s).

### The brief to the planner

1. **T7 is measured, cleanly and quantitatively.** The caricature/rotation dissociation is not a
   sign test: rotation degrades the own-direction match by **cos φ × attenuation to within
   0.0020 and 0.0031** of a Monte-Carlo prediction made before the worlds existed, and the
   measured ratio to baseline reproduces cos 30° and cos 60° to **0.00078** and **0.00349**. At
   *equal card displacement*, direction costs 0.61 of rank-1 accuracy where magnitude *gains*
   0.20. Direction reads; magnitude gauges.
2. **T8(b) is an exact designed identity and T8(c) is now a calibrated noise law.** Zero
   violations in 3.14 M pairs with seven orders of magnitude of slack, on a bound that binds
   (50.5% of pairs are genuinely anti-direction); and the estimated-card failure rate of the
   inference is predicted stratum-by-stratum to ≤ 0.00043 by the K2a algebra, with the near-norm
   ordering exactly as T8(c) says.
3. **T8(d) holds and its margin is bigger than its own justification.** The disattenuated
   distinctive cosine beats raw deviation distance in **12/12** strata by 0.106–0.190 Spearman,
   material in both sign-predicted failure regimes in all three configs. But the secondary
   readings say the ρ-correction contributes ≤ 0.001 of that: **the margin is the angle, not the
   disattenuation.** At ρ̄ ≈ 0.80–0.95 the correction has nothing to do; a config with genuinely
   heterogeneous readability would be needed to make the third coordinate earn its keep.
4. **T8(e) is FALSIFIED as stated, and the replacement is legible.** Angular crowding of the
   gallery is at **chance** (AUC 0.5005) for predicting misidentification; raw-distance crowding
   looks better (0.6371) only because it is a disguised distinctiveness measure — pure −r_i beats
   it outright (0.6643). **What drives misidentification in this world family is the probe's own
   readability, not the gallery's geometry of either kind.** That is not a small correction to
   T8: it removes "crowding" from the identification story and hands it to the menagerie
   coordinate, which L-5 independently confirms at Spearman 0.540. A repair charter should ask
   whether angular crowding recovers predictive power when the competitor field is made
   adversarial by construction (a planted near-direction twin), which this family never produces.
5. **Two instrument boundaries, both new.** (i) F2's family has **near-homogeneous
   distinctiveness** — the magnitude channel is 1–3% of squared distance even in the most
   unequal quintile-contrast pairs, so every magnitude-mismatch claim in T8(a) is currently
   untestable here; (ii) the split-half identification task is **at ceiling**, so anything scored
   on rank-1 accuracy needs the harder protocol pinned. Both should be written into the next
   registration rather than rediscovered.
6. **The 4-world pilot earned its keep again**, and in a new way: it did not merely size the
   MDEs, it caught **both** registration defects and the L-4 sign before a single main world was
   built. Realised sds tracked the pilot's closely (e.g. L-3b c1:NEAR-NORM pilot 0.00928 vs
   realised sd behind a CI half-width of 0.0097).
