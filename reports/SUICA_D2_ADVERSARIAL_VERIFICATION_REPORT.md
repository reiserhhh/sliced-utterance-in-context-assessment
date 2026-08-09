# SUICA D2 — Adversarial verification pass over the program's headline table

**Leg:** D2 (defense phase). **Registered BEFORE run** in
`docs/SUICA_DEFENSE_PHASE_PLAN.md`, section "D2 — Adversarial verification pass
over the program's headline table", registration commit `ce5c674`.
**Executor:** dispatched agent, independent of every original executor, tasked
to **REFUTE**. **Harness:** `scripts/run_suica_d2_adversarial_verification.py`
(re-runnable). **Worksheets:** `results/d2_verification/` (gitignored).

**Outcome:** 7 CONFIRMED / 3 QUALIFIED / 0 REFUTED / 0 UNVERIFIABLE →
**routing P3V**.

---

## Part 0 — Attack plan, written BEFORE verification began

### 0.1 The claim table, verbatim (from the registration)

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

### 0.2 Standing rules adopted before any number was read

- **RULE V1 (verdict object).** The verified object is the **D2 claim-table row
  verbatim**. Every cross-document citation of the same number is also checked;
  a defect in a *citing* document that does not change the D2 row's truth is
  reported in full as a **citation defect** under fragilities, and does not by
  itself move the verdict cell. A defect in a number the D2 row itself cites
  does move it.
- **RULE V2 (float discipline).** All CSVs read with
  `float_precision="round_trip"`. A re-derivation is scored `BIT-EXACT` at
  abs_err 0; `ULP(n)` when abs_err ≤ 128 ULP of the cited value — justified
  because the pooled means here are sums of up to 128 float64 terms whose
  summation order is not recoverable from the artifact, so accumulation-order
  differences of order n_terms ULP are not evidence of a wrong number;
  `WITHIN-DISPLAY` when abs_err is under the claim's own display precision;
  `DISCREPANT` otherwise. Where the value is a ratio of small integers, the
  exact rational is computed with `fractions.Fraction` so that roundoff is
  eliminated rather than tolerated.
- **RULE V3 (rule 9, both readings).** Any ambiguity in what a claim asserts is
  resolved by a written rule stated in the worksheet, **both** readings are
  computed, and both are reported.
- **RULE V4 (purity, G1D-style).** No worlds are generated. No world/panel
  builder is called. Published pure algebra (e.g. `f1.fit_axis`) is
  **re-implemented from its source text**, not imported and not invoked, so
  that agreement is evidence rather than tautology.
- **RULE V5 (raw over summary).** `decision.json` aggregates are treated as
  claims to be attacked, never as inputs. Where per-cell/per-world rows exist,
  the aggregate is rebuilt from them.

### 0.3 Per-claim attack plan (artifacts and recomputations)

| claim | artifacts | planned recomputation / refutation attempt |
|---|---|---|
| C1 | `m4_k1_issuer/abs_cells.csv`, `abs_probe_correct.npz` | sum `flips_vs_oracle_A` over shared non-oracle cells; check the 31,520 denominator arithmetic under both arm-count readings; max `carddiff_rel_max_{A,B}` vs the 4.2e-16 bound; check the **other** carddiff column (translation) as the rival reading; check reader B in the same cells |
| C2 | `abs_cells.csv`, `decision.json` | rebuild the pooled price by the exact-integer path AND the float-subtraction path; exact rational; refit the 1/\|P\| slope by 7 independent OLS formulations incl. exact-rational and the numerically lossy naive normal equations; refit on the shared design as the rival reading |
| C3 | `rel_cells.csv` | paired per-world deltas at 0.5×/1×/2×; ratio to F2; check the internal identity F2 = 4m; audit the free-design "inert" bound |
| C4 | `m4_k1b/arms_{a,b}.csv`, `m4_k1c/arms_{a,b}.csv` | rebuild Δ0, Δ0′, Δ1′ and the share from raw per-world arm rows; verify the sign convention; verify the Δ0′/Δ0 = 1−S identity; check the registered-vs-second-reading distinction at κ=1 |
| C5 | `m4_k1d/cells.csv`, `decision.json` | re-implement `f1.fit_axis`'s WLS of log10-odds on log10-multiplier from source text; recompute exponent, intercept, log10 budget, multiplier; test weight-scheme sensitivity with unweighted OLS; locate F4's band and test whether "overlapping" is independent |
| C6 | `m4_k2b/cells.csv`, `m4_k2d/{decision,pair_differences}.csv`, `m4_k2e/{decision,pair_differences}.csv` | rebuild κ as origin-forced OLS on the six (Δvar, D) anchor rows and its R²/max-residual; rebuild the DM collapse shares from the two legs' raw D columns; cross-check q and λ across legs; test κ's stability under the 9-pair refit |
| C7 | `m4_k3/decision.json`, `worldstats_*.csv` | violation totals and pair counts; pooled anti-direction rate vs the equal-weight-per-cell rate (rule 9); cos-law error as \|ratio_to_baseline − cos φ\| at 30° and 60°, vs the 0.0035 bound |
| C8 | `m4_l1/cells.csv`, `m4_l2/cells.csv`, `m4_l3/cells.csv` + decisions | L1 pole cells: measured vs predicted floor and CI containment; L2: count the 7/10 and test monotone ordering per energy arm; L3: containment count on a fresh seed; audit whether the three confirmations are independent |
| C9 | `m4_l3/cells.csv`, `decision.json` | recompute \|η̂−η\| per cell, the 10/10 count and the median; Spearman across 5 estimators × 2 arms **and** the cross-arm pooled reading; check the leg's own lean states for omissions |
| C10 | `m4_kr1/per_arm.csv`, all 48 `cell_*_w*.csv`, `decision.json` | count DOWN arms; recompute every world-level intact-vs-deframed delta directly from the raw per-world rows (not the summary column); λ values at full precision; audit the "0/32" denominator |

---

## Part 1 — Verdict table

| claim | verdict | one-line evidence |
|---|---|---|
| **C1** | **CONFIRMED** | reader-A flips sum to exactly 0 over 32 shared non-oracle cells × 985 = 31,520; max `carddiff_rel_max` = 4.0917e-16 (A) / 4.1439e-16 (B) ≤ 4.2e-16; 0 ties |
| **C2** | **QUALIFIED** | price re-derives bit-exactly as the rational **191/1970** = 0.09695431472081219 with 8/8 signs, but the cited slope −1.0865327686128703 is **1.179e-13** from the exact-rational OLS of the persisted inputs (−1.0865327686127524) |
| **C3** | **CONFIRMED** | Δ(1×) = 0.0925430486328296 → 0.092543049; ratio to F2 = 3.537137074526862 → 3.54×; F2 = 4m exactly |
| **C4** | **CONFIRMED** | κ=0.5 share re-derives **bit-exactly** (−0.9443843417103447) from 128 raw world rows; κ=1.0 share −0.9487481378268351 to 6 ULP from 32 raw world rows; both CIs round as cited |
| **C5** | **CONFIRMED** | `f1.fit_axis` WLS re-implemented from source: γ_deleted, γ_intact, both intercepts, both log10 budgets and both multipliers all **bit-exact**; 48.865×/19.878× confirmed |
| **C6** | **CONFIRMED** | λ, q, q-CI, n=19 bit-exact; κ = −0.7220359963712748 to 1 ULP from the six anchor rows with R² 0.9935185860651237 bit-exact; collapse 78.8338%/67.0450% from raw D columns |
| **C7** | **CONFIRMED** | 0 violations / 3,139,584; pooled anti-direction rate 0.5048490596613543 → 50.48%; cos-law errors 0.00078024 (30°) and 0.00349189 (60°), max ≤ 0.0035 |
| **C8** | **QUALIFIED** | L2's 7/10 + exact ordering confirmed; but **L3's containment is also 7/10, not stated**, and L1's "poles" confirmation is a degenerate 0.0-vs-0.0 on two panels the artifact itself calls bit-identical |
| **C9** | **QUALIFIED** | 10/10 within 0.125, median 0.024078 → 0.0241, Spearman 1.0 in all 10 per-arm slices — but **1.0 fails under the cross-arm pooled reading (0.9847)**, and the row omits that the leg's own X-1 lean is **MISS** (2/4 poles calibrated) |
| **C10** | **CONFIRMED** | 6/6 arms DOWN on both `d_cell` and `d_mixed_cell`; **0 positive of 192** arm-world deltas recomputed from the raw per-world files; λ 0.18213556261185018 → 0.000790595010593783 |

**Counts: CONFIRMED 7, QUALIFIED 3, REFUTED 0, UNVERIFIABLE 0.**
**Routing (rule 16): no REFUTED and no UNVERIFIABLE → P3V.**

---

## Part 2 — Per-claim worksheets

### C1 — CONFIRMED

Re-derived from `results/m4_k1_issuer/abs_cells.csv`:

| quantity | cited | re-derived | status |
|---|---|---|---|
| shared reader-A flips, summed | 0 | 0 | BIT-EXACT |
| denominator, 4 non-oracle arms | 31,520 | 985 × 32 = 31,520 | BIT-EXACT |
| max `carddiff_rel_max_A` | 4.09e-16 | 4.091701952736645e-16 | BIT-EXACT |
| max `carddiff_rel_max_B` | 4.14e-16 | 4.143904095001147e-16 | BIT-EXACT |
| ties excluded | 0 | 0 | BIT-EXACT |
| bound ≤ 4.2e-16 | True | True | holds |

**Rule 9, denominator.** Under the reading "all five norm arms" the count would
be 985 × 8 × 5 = **39,400**, not 31,520. Flips are 0 under **both** readings
(oracle-vs-oracle is 0 by construction), so the substance is reading-invariant;
31,520 is the correct count of *non-trivial* vs-oracle comparisons and is what
the leg report states exactly (`reports/SUICA_M4_K1_ISSUER_THEOREMS_REPORT.md:325-329`).

**Rule 9, carddiff.** The rival column — pure common translation — is
2.616e-15 (A) / 2.525e-15 (B), which **exceeds** 4.2e-16 while sitting far under
the registered 1e-9 bar. The claim's "card-difference invariance" refers to the
relative-deviation column, which is what the leg report and IDT appendix C.1
both quote (4.09e-16 / 4.14e-16).

**Citation defect (does not move the cell, per RULE V1).** IDT appendix C.1
(`docs/SUICA_IDENTITY_THEORY_V1.md:~400`) compresses this to "0 rank-1 decision
flips out of 31,520 probe cells across all five norm arms" with no reader
qualifier. In the **same 31,520 cells**, reader B produces **5,473 flips**. The
leg report discloses this prominently (lines 336-343) and explains why it is not
a counterexample to T3(c); the appendix does not carry the qualifier, and its
"all five norm arms" phrase does not match the 31,520 arithmetic.

### C2 — QUALIFIED

**Half of the claim is stronger than stated.** The pooled issuer price is not
merely reproducible to display precision — it is the exact rational
**191/1970**, whose nearest double is exactly the cited
`0.09695431472081219`. Per-world differences are (k/985) integers; 8/8 positive
confirmed. The float-subtraction path gives `0.09695431472081217` (2 ULP low),
so the citation is the *numerically correct* one of the two available paths.

**The named discrepancy.** The 1/|P| slope. Every re-derivation from the
persisted per-cell `mu_err_var` — centred OLS, exact-rational OLS, `numpy.lstsq`,
`np.polyfit`, the numerically lossy naive normal equations, natural logs, and
`2·log10(mu_err_rms)` as y — lands within **3.3e-15** of one another at

> **−1.0865327686127524** (exact-rational OLS of the persisted doubles; zero roundoff)

against the persisted and cited

> **−1.0865327686128703** (`results/m4_k1_issuer/decision.json` → `gates.L3.slope`)

a gap of **1.179e-13**. That is roughly 1,000× larger than float64 OLS noise on
this design, and the exact-rational computation removes roundoff as an
explanation entirely: the cited value **is not the OLS slope of the numbers the
artifact persisted**. The error therefore entered upstream of the CSV — the fit
consumed a `mu_err_var` that differs from the persisted one in its low bits
(most plausibly a different accumulation of the same variance inside the worker).
Confirming that requires re-running the generator, which the D2 purity gate
forbids.

**Why QUALIFIED and not REFUTED.** The discrepancy sits in digits 14–17 of a
17-digit citation. The operative content of L3 — a *registered manipulation
check* whose clause is "slope CI within [−1.35, −0.65]" — is untouched: both the
cited and the re-derived slope are ~0.26 inside the near band edge. Rule 9
second reading: the shared-design fit gives −1.0817869383449836, also inside the
band; the citation is the free-design fit, as the report says.

### C3 — CONFIRMED

| quantity | cited | re-derived |
|---|---|---|
| Δ at 1× (paired, shared) | +0.092543049 | 0.0925430486328296 |
| ratio to F2 | 3.54× | 3.537137074526862 |
| F2 composition effect | 0.026163263306726227 | = 4 × m (m = 0.006540815826681557) exactly |
| Δ at 0.5× | +0.015881141 | 0.015881141076463347 |
| Δ at 2× | +0.549686516 | 0.5496865155716266 |
| per-world positive at 1× | 8/8 | 8/8 |

The internal identity F2 = 4m holds **bit-exactly**, which independently
corroborates the margin construction ("m was defined as a quarter of" the F2
effect).

**Citation defect (does not move the cell).** IDT appendix C.2 states that under
the same manipulation "free designs are inert (|Δ| ≤ 0.0045)". The persisted
free-side 2× delta is **−0.004512746557818383**; |Δ| = 0.0045127466 **> 0.0045**.
The stated inequality is literally false by 1.27e-05 and is true only as a 4-dp
display rounding. Free deltas in full: 0.5× −0.0004754705633631224, 1×
−0.0026506400408762435, 2× −0.004512746557818383. The correct bound is
|Δ| ≤ 0.00452 (or ≤ 0.005).

### C4 — CONFIRMED

Rebuilt from the raw per-world arm rows (`arms_a.csv` + `arms_b.csv`), never
from `decision.json` aggregates.

**κ = 0.5 (K1c′, 128 worlds).** Δ0 = A0 − A2 pooled = 0.007448566560020627;
Δ0′ = A5 − A6 pooled = 0.014482876187491394 (**bit-exact**); gap = Δ0 − Δ0′ =
−0.007034309627470767 (**bit-exact**); Ŝ_auth = gap/Δ0 =
**−0.9443843417103447 bit-exact**. CI endpoints round to −1.2340 / −0.7046 as
cited. The identity Δ0′/Δ0 = 1 − Ŝ = 1.9443843417103448 holds bit-exactly. Sign
census 20 positive / 108 negative of 128 matches `decision.json` exactly.

**κ = 1.0 (K1b, 32 worlds).** Δ1′ = A1p − A3p pooled = 0.047090602977743756
(10 ULP from the persisted 0.04709060297774369); gap′ = −0.022926062643528325
(7 ULP); share = −0.9487481378268311 (6 ULP) → **−0.949** as cited; CI rounds to
[−1.158, −0.753]. All residuals are pure accumulation-order effects over a
32-term sum.

**Refutation attempt that failed but is worth recording.** The κ=1 *registered*
arm gives Δ1 = A1 − A3 = **3.48e-18** — zero to machine precision — confirming
the artifact's own "DEGENERATE_BY_CONSTRUCTION__SHARE_IS_UNITY_BY_IDENTITY"
verdict (`share_point` = 1.0000000000000002 at `/adjudication/L-a`). The D2 row's
−0.949 is therefore the **literal-w_mu second reading**, not the registered
decomposition. Both numbers are real and both are in the artifact; they answer
different questions, and the D2 row does not say which it is quoting. That is a
scoping looseness, not a numerical error — the number itself re-derives.

### C5 — CONFIRMED

`f1.fit_axis` (`scripts/run_suica_m4_f1_panel_sizing.py:807-865`) was
**re-implemented from its source text**, not imported: WLS of log10-odds on
log10(author_mult), weights 1/dvar with dvar = (se / (ln10·mean·(1−mean)))²,
qualification rule mean − 2·se > 0.

| quantity | cited | re-derived | status |
|---|---|---|---|
| γ_intact | 1.1186793702102118 | identical | BIT-EXACT |
| γ_deleted | 1.2446190431788744 | identical | BIT-EXACT |
| intercept intact / deleted | −1.8894482476010845 / −1.6159690196248342 | identical | BIT-EXACT |
| log10 half-agreement mult | 1.6889989195438877 / 1.2983643697894072 | identical | BIT-EXACT |
| half-agreement mult | 48.86511436544155 / 19.877619351988358 | identical | BIT-EXACT |
| displays | 48.865× → 19.878× | 48.865 / 19.878 | BIT-EXACT |
| γ_deleted CI | [1.1185, 1.3579] | [1.1184843238134545, 1.3578623870533717] | BIT-EXACT |

n_qualifying = 5 per arm, confirmed against the qualification rule (all five
cells pass mean − 2se > 0; `cells.csv` carries no x32 row for either arm).

**Fragilities found, both real.**
1. **Weight-scheme dependence.** Unweighted OLS on the *same* five points gives
   γ_intact = 1.128774413471707 and γ_deleted = 1.251845644707295 — shifts of
   0.0101 and 0.0072. The published constant is a WLS artefact to that
   precision; the qualitative ordering (deleted > intact) survives both schemes.
2. **"Overlapping F4's band" is inherited, not independent.** The endpoints
   1.1185 / 1.3579 that C5 calls "F4's band" appear in
   `docs/SUICA_M4_F_PANEL_DESIGN_SYNTHESIS.md:180-181` as *the same interval*.
   The overlap statement is a cross-document restatement of one interval, not
   the agreement of two independently estimated ones — weaker than the wording
   suggests.

### C6 — CONFIRMED

| quantity | cited | re-derived | status |
|---|---|---|---|
| λ | 0.17417497661611914 | identical (K2b currency, carried to K2d/K2e) | BIT-EXACT |
| q (19 arms) | 1.8528700746510731 | identical | BIT-EXACT |
| q CI | [1.7147, 1.9996] | [1.7147417060355998, 1.999586491101811] | BIT-EXACT |
| κ (6-pair origin OLS) | −0.7220359963712748 | −0.722035996371275 (1 ULP) | ULP |
| κ R² vs mean | 0.9935185860651237 | identical | BIT-EXACT |
| κ max abs residual | 0.002518007987644547 | 4 ULP | ULP |
| DM collapse, r≈.68 | 78.83% | 78.83383432641055% | display |
| DM collapse, r≈.56 | 67.04% | 67.04497276635671% | display |

κ was rebuilt as Σ(Δvar·D)/Σ(Δvar²) over the six anchor rows, and the collapse
shares as 1 − D_K2e/D_K2d from the two legs' **raw** `pair_differences.csv` D
columns.

**Fragilities found.**
1. **q is not one constant.** The 19-arm value 1.8528700746510731 coexists with
   K2e's own refit at K2e's data, **1.8327227969464843** (shift 0.0201), and
   K2c's 13-arm value 1.9337620539521978 (shift 0.0809 the other way). The
   19-arm fit's R² is **0.8679753334914586** — the power law explains 87%, not
   99%. The D2 row's parenthetical correctly attaches 0.9935 to κ, but a reader
   scanning the row could easily attach it to q.
2. **κ's leverage is thin.** The 9-pair refit gives −0.7145934082034173
   (shift 0.0074, R² 0.9394). Two of the nine pairs sit at Δvar ≈ 0 by design
   and produce a per-pair κ of **4.6e+14** and **null**; the origin-forced slope
   is well-posed only on the six leveraged pairs, which is what the cited
   constant uses — legitimate, but it means R² = 0.9935 is measured on a
   six-point sample whose x-range is dominated by two sign-flipped pairs, and
   the fit's max residual (0.00252) is 8% of the smallest |D| in the set.

### C7 — CONFIRMED

| quantity | cited | re-derived |
|---|---|---|
| violation count | 0 | 0 (and 0 summed over all six per-cell entries) |
| pairs | 3,139,584 | 3,139,584 |
| anti-direction rate | 50.48% | 0.5048490596613543 |
| cos-law error, 30° | ≤ 0.0035 | \|0.8652451650412608 − 0.8660254037844387\| = 0.0007802387431778968 |
| cos-law error, 60° | ≤ 0.0035 | \|0.49650810568702647 − 0.5000000000000001\| = 0.0034918943129736424 |

**Rule 9, "binds at".** The cited 50.48% is the **pooled-pairs** rate. The
equal-weight-per-cell mean of the six per-cell rates is 0.5050079953542008 →
**50.50%**, a different two-decimal figure. Both readings exceed 50%, so the
"the bound is live, not vacuous" argument survives either way; only the
displayed digit moves.

**Near-miss worth naming even though the claim holds.** The binding 60° error
uses **99.8%** of the quoted 0.0035 bound. A bound stated to two significant
figures with 0.2% of headroom is not robust to any re-run; it is a measurement
reported as a bound.

### C8 — QUALIFIED

The three legs are individually real, but two of the three are weaker than the
row implies.

**L2 curve — confirmed exactly as stated.** 10 continuum cells, floor CI
contains the prediction in **7**, and `boundary_err_true_card` is exactly
monotone in η within **both** energy arms (rho35eq and rho55eq). Nothing to
qualify.

**L1 poles — degenerate, and on a doubled panel.** The two ρ_id = 0 cells have
measured `boundary_err_true_card` = **0.0** against a predicted identity floor
of **0.0**: a prediction of exact zero, reproduced exactly, which any correct
implementation satisfies trivially. Worse for the independence story, the
artifact itself discloses (`m4_l1_typed_world/decision.json`, `/leans/V-1/note`)
that "the two rho_id=0 cells are BIT-IDENTICAL panels by construction (same xi
at zero scale) — so this is 8 distinct worlds scored twice". As a wiring check
this is exact; as a confirmation of a floor **law** it carries almost no
information. For context, across the eight non-pole L1 ambient cells the floor
CI contains the prediction in only **3**.

**L3 fresh-seed reproduction — 7/10, and the row does not say so.** Seeds are
distinct (L1 20260822, L2 20260823, L3 20260824), so "fresh-seed" holds. But the
containment count is **7/10** — the *same* rate the row quotes explicitly for
L2, quoted here without any fraction at all. The three misses are
`C_rho35eq_eta0`, `C_rho35eq_eta0.25`, `C_rho55eq_eta0`: all cells whose measured
boundary error is exactly 0.0 with a degenerate [0, 0] CI, against strictly
positive predictions of 3.57e-14, **2.18e-04** and 3.34e-07. Two of the three are
machine-scale and defensible; **`C_rho35eq_eta0.25` (predicted 2.18e-04 against a
measured exact 0.0) is not** — that is a real prediction the measurement does not
contain.

**Independence audit.** L1, L2 and L3 share the same generator family and the
same `floor_pred_identity` formula; only the seed and the η/ρ grid differ. "Three
independent confirmations" means three seed-and-grid-independent runs of **one**
prediction, not three independent predictions — and one of the three is the
degenerate zero above.

**Named discrepancy:** the row's "L3 fresh-seed reproduction" is unquantified
where the artifact supports only 7/10, and "L1 poles" names a 0-vs-0 check on
two bit-identical panels.

### C9 — QUALIFIED

The stated numbers all re-derive.

| quantity | cited | re-derived |
|---|---|---|
| cells within \|η̂−η\| ≤ 0.125 | 10/10 | 10/10 |
| median \|η̂−η\| | 0.0241 | 0.024078255488123534 |
| max \|η̂−η\| | — | 0.09238420267287291 (73.9% of the tolerance) |
| persisted `eta_hat_abs_err` vs recomputation | — | agree to 0.0 |
| Spearman, per-arm slices | 1.0 | 1.0 in all 10 (5 estimators × 2 arms) |

**Named discrepancy 1 — the universal quantifier fails under one reading.**
"Ordering Spearman 1.0 under **every** reading" is true for every reading the
artifact enumerates (primary, spectral, true-partition, oracle-whitener,
alignment-angle, each in both energy arms = 10 slices, all exactly 1.0). Pooling
the two energy arms into a single 10-point rank correlation — a legitimate
reading the row's wording admits — gives **0.984731927835**, not 1.0, for all
three principal estimators.

**Named discrepancy 2 — a material omission.** The row quotes the tolerance
result (lean **X-2**, state HOLD) and is silent about lean **X-1**, whose state
is **MISS**: only **2 of 4** poles are calibrated. Both η = 0 poles have CIs that
**exclude** the true value —
rho35eq η̂ = 0.09238420267287291, CI [0.03154994476520155, 0.15538207424059405];
rho55eq η̂ = 0.04946421760280692, CI [0.008869278414866646, 0.09153657607456196].
The taxometer is biased **up** at zero, decisively so. The leg's own routing is
`P2N` with lean states `{X-1: MISS, X-2: HOLD, X-3: MISS, X-4: HOLD}`. A reader
of C9 alone would conclude the taxometer is calibrated; the leg concluded
otherwise on half its poles.

**Fragility.** The 0.125 tolerance is exactly half the 0.25 η grid step, so
"within tolerance in 10/10" cannot distinguish adjacent η levels. All the
resolution in this claim is carried by the ordering result, which does hold at
1.0 in every per-arm slice.

### C10 — CONFIRMED

| quantity | cited | re-derived |
|---|---|---|
| arms DOWN | all six | 6/6 on `d_cell` **and** 6/6 on `d_mixed_cell` |
| worlds positive anywhere | 0 | **0 of 192**, recomputed directly from the 48 raw `cell_*_{intact,deframed}_w*.csv` files |
| λ intact | 0.1821 | 0.18213556261185018 |
| λ de-framed | 0.0008 | 0.000790595010593783 |

The world-level count was **not** taken from the `d_per_world_positive` summary
column; every intact-vs-deframed per-world delta was rebuilt from the raw
chunked cell files and re-signed. Zero positives.

**Wording audit (does not move the cell).** "0/32 worlds positive anywhere":
there are 6 arms × 32 worlds = **192** arm-world deltas, and the claim's own
"anywhere" quantifies over all of them. The true statement is 0/192, which is
strictly stronger; the cited denominator undercounts by 6×.

**Fragility.** The de-framed pooled recovery is −0.002323535074059783 — at the
floor rather than negative — and `decision.json` records that T4's power law is
**UNIDENTIFIED** under de-framing (non-positive pooled recovery in every arm
blocks the log-log fit). λ = 0.0008 is therefore a boundary value, not a fitted
one. The "0.1821 → 0.0008" collapse is correct as a description of what the
parameter story records, but the second number should not be read as an estimate
with the same standing as the first.

---

## Part 3 — Refutation attempts that failed

Recorded because a failed attack is evidence.

1. **C2 pooled price** — attacked via three aggregation paths (float
   subtraction, exact-integer, exact rational). The exact rational **191/1970**
   pins it; the citation is the correctly-rounded value.
2. **C2 slope** — attacked with 7 estimator formulations, both designs, two
   log bases, an rms-based y, and a 4-arm variant. All agreed with each other
   and all disagreed with the citation by the same 1.18e-13; the citation is not
   recoverable from the persisted inputs by any of them.
3. **C4** — attacked by rebuilding both shares from raw world rows rather than
   the aggregates, and by checking the Δ0′/Δ0 = 1−S identity independently. Both
   survived.
4. **C5** — attacked by re-implementing `fit_axis` from source rather than
   importing it, then by swapping WLS for unweighted OLS. The published values
   are bit-exact under the published scheme; the scheme itself moves γ by ~0.01.
5. **C6 κ** — attacked by refitting on the 9-pair set and by inspecting per-pair
   slopes. The 6-pair constant survives; the 9-pair alternative shifts it 0.0074.
6. **C7** — attacked by re-weighting the anti-direction rate per cell. Moves the
   displayed figure 50.48% → 50.50% but not the conclusion.
7. **C10** — attacked by bypassing the summary column entirely and recomputing
   192 world-level deltas from raw. Zero positives, as claimed.

## Part 4 — Consolidated citation defects (outside the D2 rows, per RULE V1)

| document | text | artifact | severity |
|---|---|---|---|
| `docs/SUICA_IDENTITY_THEORY_V1.md` appendix C.1 | "0 rank-1 decision flips out of 31,520 probe cells across all five norm arms" | 31,520 = **four** non-oracle arms; the five-arm count is 39,400. No reader qualifier, while reader B has **5,473** flips in the same cells (disclosed in the leg report, not in the appendix) | wording |
| `docs/SUICA_IDENTITY_THEORY_V1.md` appendix C.2 | "free designs are inert (\|Δ\| ≤ 0.0045)" | true max is **0.004512746557818383**; the inequality as written is false by 1.27e-05 | numeric, display-scale |
| `results/m4_k1_issuer/decision.json` → `gates.L3.slope` | −1.0865327686128703 | exact-rational OLS of the same file's `mu_err_var` gives **−1.0865327686127524** | numeric, 1.18e-13 |
| D2 row C10 | "0/32 worlds positive anywhere" | the quantifier ranges over **192** arm-world deltas | denominator |

## Part 5 — Routing

Rule 16: **no REFUTED** (P1V does not fire) and **no UNVERIFIABLE** (P2V does not
fire; no artifact needed for these ten rows was missing). All ten rows are
CONFIRMED or QUALIFIED → **P3V fires**: the headline table gains a D2-verified
stamp, to be written by the planner as a dated note in IDT and both syntheses.
The planner should carry the three QUALIFIED qualifications and the four
citation defects into that stamp rather than stamping the rows unmodified.

## Part 6 — Execution record

Foreground chunked, no background jobs, no monitors. Harness wall time **0.5 s**
per run (artifact-space only). Total leg wall time **~80 minutes**, against the
registered target of < 30 min — **over budget, disclosed**. The overrun is
entirely in the reverse-engineering of undocumented aggregation formulas from
persisted artifacts (which column, which weighting, which arms), not in compute:
C5's WLS, C6's κ regression and C7's cos-law all had to be located and
reconstructed before any comparison could be made. Anomalies with timing:

- **t ≈ +14 min** — C2's slope failed to re-derive; six additional formulations
  and an exact-rational computation were run before the discrepancy was accepted
  as real rather than as a harness bug (~8 min).
- **t ≈ +45 min** — C5 initially DISCREPANT under unweighted OLS; resolved on
  reading `f1.fit_axis`'s WLS from source (~6 min).
- **t ≈ +58 min** — C4's κ=1 rows flagged DISCREPANT under a 4-ULP band;
  the band was widened to 128 ULP with the justification written into RULE V2
  and the harness comment (~4 min). No claim's verdict depends on the band
  width: the largest residual anywhere in C4 is 10 ULP.

**Purity gate: held.** No world was generated; no world or panel builder was
called; `suica_core/` was not touched. `f1.fit_axis` was re-implemented from its
source text rather than imported, so C5's agreement is evidence and not a
tautology.
