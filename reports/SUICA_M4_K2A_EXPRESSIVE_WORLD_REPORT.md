# SUICA M4-K2a — Instrument leg: an expressive world (slow state + person×occasion channel) and the two-split probe validated

Tier: **EXPLORATORY, label-free, synthetic.** Registered in
`docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md`, section "M4-K2a — Instrument leg: an
expressive world (slow state + person×occasion channel) and the two-split probe
validated" (REGISTERED 2026-08-09, BEFORE RUN, commit `a041ceb`). Theory:
`docs/SUICA_IDENTITY_THEORY_V1.md` dated appendix A (T6′, the two-split state
probe), appendix B (the exact AR variance-of-mean formula), appendix E (E.2/E.3a
— F2's family instantiates **no** person×occasion channel, which is why this leg
exists), appendix G.5. Ledger row `M4-K2a`. Script:
`scripts/run_suica_m4_k2a_expressive_world.py`. Artifacts:
`results/m4_k2a_expressive_world/`.

**This leg adjudicates NO theory branch.** It builds an expressive world and
validates a card-level instrument against *designed identities* — quantities
whose true values are computable in closed form from the generator's own
constants. Its output is an instrument for K2b, plus the honest record of where
the instrument's algebra is exact and where it is not.

Executor's standing: implementation and execution only. The registration text is
binding; everything below labelled **RN-n** is a register-note — an
operationalization of something the registration left as an implementation
choice, or a standing-rule-9 instrument resolution — fixed and written here
**before** any main arm ran.

---

## 0. Part 0 — register-notes, the G4a point predictions, and the gates

**Part-0 computed 2026-08-09 (stage `part0`, wall-time 1.981 s), persisted in
`results/m4_k2a_expressive_world/gates.json` with
`timestamp_utc = 2026-08-09T07:59:22.683396+00:00` and
`results/m4_k2a_expressive_world/part0_predictions.csv`. This section was
written to disk before the `arms` stage was ever invoked** — the script enforces
it: `require_part0()` refuses to run `arms` unless `gates.json` reports
`part0_all_pass` **and** this report file exists.

**No smoke run of any kind preceded Part 0.** Every world generated up to this
point lives on the RESERVED pilot world indices **9501–9502**, whose seeds are
disjoint from the eight main world indices 0–7, and no V-1/V-2/V-3 quantity has
been computed on a main world. All construction checking lives inside G0a/G1a as
the registration requires.

**All five Part-0 gates PASS: `part0_all_pass = true`. P3a does not fire.**

### Register-notes (fixed before any main arm)

**RN-1 — the occasion/event grid, and where the slow state ticks (rule 9).**
The registration writes the response as `x(i,t,o)` with `t` an event index and
`o` an occasion index, and G4a requires `Var(s̄)` "from the exact AR sum
(appendix B's formula, **m = n_occ**)". Those two are only consistent if the
slow state ticks **once per occasion**. Pinned accordingly: each author has
**n_occ occasions × N_REP = 2 events per occasion**; `slow_i` is an AR(1) on the
occasion grid with exactly `m = n_occ` ticks, shared by both events of an
occasion; `noise(i,t)` is per **event**. Occasions are **shared across all
authors** (a shared-occasion design), which is what makes `common(o)` a genuine
frame channel. The two events per occasion exist so that V-3's "same-occasion
signature" is measurable at all — without a within-occasion replicate the
occasion-bound channel has no reader-visible footprint.

**RN-2 — "equal-share" (rule 9).** The registration pins `w_int ∈ {0,
equal-share}` and "weights sum-of-squares normalized per arm" but not the base
shares. Resolved as the literal reading: **every ACTIVE channel carries an equal
variance share, normalized per arm.**

| arm | active channels | share each | weight each |
|---|---|---|---|
| `w_int = 0` | mu, slow, common, noise | 1/4 = 0.25 | 1/2 = 0.5 |
| `w_int = equal` | mu, slow, int, common, noise | 1/5 = 0.20 | 1/√5 = 0.4472135955 |

The per-arm renormalization is exactly what the fifth channel's arrival changes;
this is why the two `w_int` arms have *different* predictions for every
quantity, not just for the interaction ones.

**RN-3 — source objects (rule 12).** Every channel is named by its generator
source object, not by a knob name:

| channel | source object |
|---|---|
| trait `b` := `mean_part` | `scripts/run_suica_m4_f2_composition.py:178`, mirrored in `build_world` with `w_mu` factored to 1 (the arm weight is applied separately). **The registered definition — `trait b := this vector` — is used verbatim.** |
| `slow_i(t)` | `run_suica_m4_f2_composition.py:172-176` (the author-AR recursion), mirrored with f2's per-author logistic `phi` matrix replaced by the **pinned scalar** `φ_slow` the registration demands. Stationary by construction (`x[:,0] ~ N(0,I)`, innovation `√(1−φ²)`) — so the marginal variance is exactly 1 and appendix B's formula applies without an initial-condition correction. |
| `common(o)` | `run_suica_m4_f2_composition.py:121-126` — `f2().shock_vector(world_seed, "K2A_COMMON", o, k)`, **called unchanged**. |
| latent→64 map | `run_suica_m4_f2_composition.py:196` (`a·((·*g) @ loadings.T)`), with `a` from f2:165, `g` from f2:164, basis from `suica_core/v8_context_relation_field.py:78-84`. |
| `noise(i,t)` | `run_suica_m4_f2_composition.py:177,197` (`σ_iso·N(0,I₆₄)`, `σ_iso` from f2:166). |
| **NEW** `s_int(i,o)` | this script: `shock_int_matrix()` at **k2a:168-175**, the per-author loading `a_i` at **k2a:213-216**, the interaction latent `u_int` and `s_int` at **k2a:217-219**. `a_i ~ N(0,I_k)` from a fresh seeded rng (salt `m4k2a-loading`); `S(o) ∈ R^{k×k}` from an occasion-keyed stream on salt **`m4k2a-shock-int`**, disjoint from f2's `m4f2-shock`, so independence of `common(o)` is by construction and is checked numerically in G0a. `u_int(i,o) = a_iᵀS(o)/√k`, then the same f2:196 map. |
| the extended generator | **k2a:178-241** (`build_world`); the deviation/card constructors **k2a:244-273**; the exact AR algebra **k2a:276-297** (`ar_mean_var` is appendix B's formula verbatim); the Part-0 predictions **k2a:337-388**; the pooled estimators **k2a:453-481**; the registered bootstrap **k2a:483-511**. |
| deterministic hash | `suica_core/v8_realtext_relation_field.py:138-140`. |

**The mirror is verified, not asserted** (rule 8 — a claim about code is a
factual claim). Calling f2's *own* `generate_world_composed` with
`w_mu = 1, w_x = 0, w_e = 0` makes f2:197's other two terms carry coefficients
`√0 = 0`, so its output *is* `mean_part` — a bit-exact oracle for this leg's
trait plus latent→64 mirror (and transitively for the loadings, `z`, `g`, `a`
and the rng stream order). **Max absolute residual against f2's own object:
0.0 — bit-identical — in all six (φ_slow, n_occ) configurations**
(`mirror_audit` in `post_hoc_world_bootstrap.json`; see anomaly (vi) for its
timing). The AR mirror differs from f2's *only* by the pinned scalar `φ_slow`
the registration demands, and is verified by G2a's ACF readback.

`suica_core/` is untouched. Generator constants inherited from F2's calibrated
knobs (f2:816-818): `k = 48`, output `DIM = 64`, `g = linspace(0.85, 0.55, 48)`,
`a = √(2/Σg²)`, `σ_iso = √(2/64)`. Every unit-scale channel therefore has pooled
per-entry variance **v = 2/64** exactly; the arm shares are shares of that.

*Reading of "per-author unit loading a_i":* "unit" is read as **unit variance
per component** (`a_i ~ N(0, I_k)`), not unit norm — this is the reading under
which the registration's own `/√k` is the correct normalizer (`Var(u_int) =
‖a_i‖²/k → 1`). Under a unit-*norm* reading the `/√k` would leave the channel at
variance `1/k` and the "equal-share" arm could not exist. Recorded because it is
a genuine reading choice.

**RN-4 — "realized shares within 1% of design" (rule 9).** Read as **1
percentage point, absolute** (`|realized − design| ≤ 0.01` in share units), the
natural reading for a quantity already expressed as a fraction. The **relative**
reading is reported alongside for every cell (rule 9: all readings). The
absolute reading is also the only *satisfiable* one, and this is derivable
rather than convenient: a channel built from `N` independent latent k-vectors
has realized-variance relative sd `√(2Σg⁴)/(Σg²·√N) = 0.2103605552/√N`, so with
2 pilot worlds

- trait (`N = 256·2` author draws): **0.930%**
- `common(o)`, n_occ=8 (`N = 8·2` occasion draws): **5.259%**
- `common(o)`, n_occ=32: **2.630%**

A 1%-relative gate on `common(o)` at n_occ=8 would be a 0.19σ requirement — it
would fail with probability ~0.85 on a *correct* generator. That is a rule-11
unsatisfiability, and it is why the absolute reading controls.

**RN-5 — pooled statistics (rule 9).** ρ and r are computed in the
**uncentred (known-mean-zero) pooled-entry** form,
`ρ = ΣᵢΣ_d u_id v_id / √(ΣΣu² · ΣΣv²)`, pooling over authors × 64 coordinates.
Justification: cards are *exactly* author-centred by construction and the trait
has zero population mean, so the uncentred form is the correct lower-variance
estimator **and** it makes the ratio-of-expectations prediction exact. Two
second readings are computed and reported for every cell: the conventionally
mean-centred pooled Pearson, and the **mean per-author cosine** (IDT §1's
`ρ_i = cos(c⁽¹⁾(i), c⁽²⁾(i))`, whose expectation is the same ratio only to
first order).

**RN-6 — the truth object for `r(card → b)` (rule 9).** Primary: the **raw**
`mean_part` vector, exactly as the registration defines `trait b`. Because cards
are author-centred and the raw trait is not, the *exact* algebra of the
registered construction carries a factor `√((n−1)/n)`:

  `r_raw = √((n−1)/n) · σ_b/√(σ_b² + Var(s̄) + Var(s̄_int) + σ_e²/n_eff)`

Second reading: the card against the **author-centred** trait, for which the
registered formula holds with **no** correction. Both are exact and both are
predicted and reported. At n = 256 the factor is 0.9980449.

**RN-7 — the split schemes.** `interleaved` = even occasions vs odd occasions;
`contiguous` = first `n_occ/2` vs last `n_occ/2`; both halves use both reps.
`same_occ` = all `n_occ` occasions, rep 0 vs rep 1. `same_occ_half` = the first
`n_occ/2` occasions, rep 0 vs rep 1.

**RN-8 — the V-3 estimators, and the equivalence margin.** "The interaction
channel's contribution to the CONTIGUOUS-split reproducible component" is
measured as an **exact term-drop ablation**: the `w_int·s_int` term is removed
and *every other channel is bit-identical* (no renormalization — this is a
channel-deletion counterfactual in K1c′/K1d's own idiom, not a different arm).
The **reproducible component** is the cross-half **covariance** (the numerator),
not the correlation — the interaction unavoidably changes ρ's *denominator* by
adding card variance, and that is a noise-floor effect, not reproducibility. In
normalized units `ĉov = Σᵢ⟨c1ᵢ,c2ᵢ⟩/(n·64·v)`:

  `covint(split) := ĉov(with int) − ĉov(int dropped)`

*Directions (rule 11).* V-3a is **one-sided upper**: an occasion-shared channel
can only *add* reproducible covariance, so the registered clause is
`upper 95% < +δ_int` (defect-#15's lesson). A two-sided TOST reading is reported
as a second reading. V-3b is **one-sided lower**: the predicted same-occasion
contribution is positive, so the clause is `lower 95% > 0`.

*The n_occ-derived margin, with its satisfiability rule pre-stated.* The unit is
the leakage one accidentally shared occasion would produce between two
`m_h`-occasion halves: `δ_unit = C/m_h²` (= `(1/m_h)` of the channel's own
same-occasion contribution `C/m_h`). Because the estimator carries an
**occasion-level** noise component that the registered authors-within-world
bootstrap cannot see — analytically `sd ≈ 1/(m_h·k·√W)`, since
`tr(S(o)S(o′)ᵀ)/k²` has sd `1/k` per occasion pair — the margin is set by the
pre-stated ladder: **δ_int = ν·δ_unit for the smallest ν ∈ {1, 2, 4} whose
margin is at least 2× the projected main-grid half-width** (author bootstrap ⊕
the analytic occasion-level sd). If no ν ≤ 4 qualifies, V-3a is declared
**UNDERPOWERED at that cell** (rule 2: a noise-floor null is not a null), never
a failure. The ladder's outcome is in G3a below; results at all three ν are
reported regardless (rule 9).

**RN-9 — the ACF gate's level and multiplicity (rule 1 + rule 9).** G2a's
registered form is "measured ACF at lag 1 within CI of φ_slow per cell"; it
pins neither the CI level nor the multiplicity treatment. Pinned: the
authors-within-world bootstrap (B = 2000, seed = master_seed), **family-wise 95%
over the 6 DISTINCT (φ_slow, n_occ) pairs** (Bonferroni, per-cell level 0.05/6)
— 6, not 12, because the two `w_int` arms of a pair share the world seed and
therefore have a *bit-identical* slow latent. A 12-of-12 requirement at an
uncorrected per-cell 95% level would fail ~26% of the time on a correct
generator. **Both readings are reported**, and G2a additionally checks the
measured value against an independently Monte-Carlo'd `E[φ̂]` for this exact
estimator so that "bias" and "fluctuation" are not confused. This resolution was
fixed while Part 0 was being computed, before any main arm and before any
V-1/V-2/V-3 number existed.

**RN-10 — world seeds and pairing.** `world_seed = stable_bucket(f"{20260815}-{φ}-{n_occ}-{w}",
salt="m4k2a-world")`, depending on `(φ_slow, n_occ, world)` **only** — so the
two `w_int` arms of a `(φ, n_occ)` pair share `b`, `slow`, `common`, `noise` and
`a_i` bit-for-bit and the `w_int` contrast is exactly paired. Main worlds
`w ∈ {0..7}`, reserved pilot worlds `w ∈ {9501, 9502}`.

**RN-11 — aggregation (rule 1).** Per-cell CIs against the Part-0 predictions;
bootstrap over **authors within world, worlds as strata**, B = 2000, seed =
master_seed (20260815); 8 worlds × 256 authors = **2048 pooled authors per
cell**. Leans scored separately; **no omnibus**. Rule 13: every clause carries
this resampling spec; a clause whose boundary lies within 2× the Monte-Carlo sd
of its own CI endpoint is re-checked at B = 20000 and scored **BOUNDARY** if the
verdict moves.

### G4a — the point predictions, computed BEFORE any arm

Derivation. Write `A = w_mu²`, `B = w_slow²`, `C = w_int²`, `E = w_e²`,
`F = w_c²` (shares; `A+B+C+E+F = 1`). Each unit-scale channel contributes pooled
per-entry variance `v = 2/64`, so all of the following are in units of `v` and
`v` cancels from every ratio.

1. **The frame channel drops out exactly.** `d(i,o,j) = x(i,o,j) − mean_l
   x(l,o,j)` and `common(o)` is author-invariant, so it cancels **exactly** —
   T3's designed cancellation, measured at 0.0 (not 1e-16: the term never enters
   the centred panel). Hence `F` appears in no card prediction.
2. **Author-centring.** With authors i.i.d., `Cov(Xᵢ−X̄, Yᵢ−Ȳ) = (1−1/n)Cov(Xᵢ,Yᵢ)`.
   The factor multiplies every card variance and every card covariance alike, so
   it **cancels exactly in ρ**, and survives only in `r` against the *raw* trait
   (RN-6) and in the raw covariance quantities of V-3.
3. **Slow-state variance over an occasion set** `S`, `|S| = m`:
   `V(S) = (1/m²) Σ_{o,o′∈S} φ^{|o−o′|}`. For contiguous `S` this is exactly
   appendix B's `(1/m²)[m + 2Σ_{d=1}^{m−1}(m−d)φ^d]`; the code computes the
   general double sum and the contiguous case reproduces the closed form.
4. **Interaction** is i.i.d. across occasions (verified in the construction:
   `E[u(i,o)ⱼu(i,o′)ⱼ] = 0` for `o ≠ o′` because `S(o) ⫫ S(o′)`, both mean
   zero), so `Var(s̄_int over m occasions) = C/m` and its cross-set covariance is
   0. **Noise** averages over `m·N_REP` events: `E/(m·N_REP)`.
5. **Two-split probe.** With `S1, S2` disjoint, `|S1| = |S2| = m_h = n_occ/2`:

   `ρ(split) = [A + B·Cov(S1,S2)] / √[(A + B·V(S1) + C/m_h + E/(2m_h))·(A + B·V(S2) + C/m_h + E/(2m_h))]`

   Interleaved: within-half lags are even (`φ^{2d}`), cross lags odd. Contiguous:
   within-half lags are appendix B's, cross lags span the halves. `gap =
   ρ_interleaved − ρ_contiguous`.
6. **Attenuation**, full card (`m = n_occ`, both reps, `n_eff = 2·n_occ`):

   `r = √A / √(A + B·V_AR(n_occ, φ) + C/n_occ + E/(2·n_occ))`

   which is the registered
   `σ_b/√(σ_b² + Var(s̄) + Var(s̄_int) + σ_e²/n_eff)` term for term, with
   `Var(s̄)` the **exact AR sum at m = n_occ**. Against the raw trait, multiply
   by `√((n−1)/n) = 0.9980449` (RN-6).
7. **Same-occasion (rep) split, all occasions:** the halves share trait, slow and
   interaction in full, and differ only in noise:
   `ρ_same = (A + B·V_AR + C/n_occ) / (A + B·V_AR + C/n_occ + E/n_occ)`.
8. **V-3 predictions** (normalized covariance, RN-8): `covint(contiguous) = 0`,
   `covint(interleaved) = 0`, `covint(same_occ) = (C/n_occ)(1−1/n)`,
   `covint(same_occ_half) = (C/m_h)(1−1/n)`.

**The 12-cell prediction table (`part0_predictions.csv`, computed before any
world of the main grid existed):**

| cell | φ | n_occ | w_int | ρ_int pred | ρ_cont pred | **gap pred** | r(card→b) pred (raw b) | r pred (centred b) | Var(s̄), m=n_occ | ρ same-occ pred |
|---|---|---|---|---|---|---|---|---|---|---|
| `phi0.5_occ8_intzero` | 0.5 | 8 | zero | 0.8505256242 | 0.6764880952 | 0.1740375289 | 0.8510600526 | 0.8527271650 | 0.3127441406 | 0.9130582442 |
| `phi0.5_occ8_intequal` | 0.5 | 8 | equal | 0.7280652418 | 0.5870351240 | 0.1410301179 | 0.8148339920 | 0.8164301424 | 0.3127441406 | 0.9200124980 |
| `phi0.5_occ32_intzero` | 0.5 | 32 | zero | 0.9532208589 | 0.8376619735 | 0.1155588854 | 0.9492418399 | 0.9511012772 | 0.0898437500 | 0.9721254355 |
| `phi0.5_occ32_intequal` | 0.5 | 32 | equal | 0.9033430233 | 0.7962959579 | 0.1070470653 | 0.9361029109 | 0.9379366108 | 0.0898437500 | 0.9728813559 |
| `phi0.9_occ8_intzero` | 0.9 | 8 | zero | 0.9229877440 | 0.8300843947 | 0.0929033494 | 0.7366319498 | 0.7380749129 | 0.7731890281 | 0.9341477597 |
| `phi0.9_occ8_intequal` | 0.9 | 8 | equal | 0.8161211322 | 0.7381031885 | 0.0780179436 | 0.7127639867 | 0.7141601956 | 0.7731890281 | 0.9382163514 |
| `phi0.9_occ32_intzero` | 0.9 | 32 | zero | 0.9756548407 | 0.7493359022 | 0.2263189385 | 0.8318111461 | 0.8334405524 | 0.4240045223 | 0.9785260932 |
| `phi0.9_occ32_intequal` | 0.9 | 32 | equal | 0.9355340087 | 0.7219224923 | 0.2136115165 | 0.8229274643 | 0.8245394688 | 0.4240045223 | 0.9789775278 |
| `phi0.98_occ8_intzero` | 0.98 | 8 | zero | 0.9374627632 | 0.9155289839 | 0.0219337793 | 0.7036964308 | 0.7050748776 | 0.9490439164 | 0.9397312665 |
| `phi0.98_occ8_intequal` | 0.98 | 8 | equal | 0.8367241096 | 0.8181426023 | 0.0185815073 | 0.6828010739 | 0.6841385895 | 0.9490439164 | 0.9431571152 |
| `phi0.98_occ32_intzero` | 0.98 | 32 | zero | 0.9824895688 | 0.8954649316 | 0.0870246373 | 0.7375581699 | 0.7390029474 | 0.8154564332 | 0.9830779817 |
| `phi0.98_occ32_intequal` | 0.98 | 32 | equal | 0.9503359090 | 0.8674054112 | 0.0829304978 | 0.7313438620 | 0.7327764664 | 0.8154564332 | 0.9833595714 |

**The predicted (φ_slow, n_occ) gap ordering V-1 must reproduce exactly**
(descending gap, within each `w_int` arm; the two arms' orderings are *not* the
same, which is itself a prediction):

- `w_int = 0`: **(0.9, 32) ≻ (0.5, 8) ≻ (0.5, 32) ≻ (0.9, 8) ≻ (0.98, 32) ≻ (0.98, 8)**
- `w_int = equal`: **(0.9, 32) ≻ (0.5, 8) ≻ (0.5, 32) ≻ (0.98, 32) ≻ (0.9, 8) ≻ (0.98, 8)**

Note the non-monotonicity the algebra insists on: the gap is **not** increasing
in φ. At φ = 0.98 with n_occ = 8 the state barely decorrelates even across
contiguous halves (`Var(s̄) = 0.949` of a single-occasion state), so both splits
share it and the gap nearly vanishes (0.0219/0.0186); at φ = 0.9 with n_occ = 32
the contiguous halves *do* decorrelate while the interleaved halves still share
lag-1 structure, and the gap is maximal (0.2263/0.2136). The ordering swap
between the two arms — (0.98, 32) overtakes (0.9, 8) once the interaction
channel is present — is a prediction of the renormalization in RN-2, not of the
AR algebra.

### G0a — channel construction

**PASS.** Criterion: reconstruction residual ≤ 1e-12 **and**
`|realized share − design| ≤ 0.01` (absolute, RN-4).

- **Five-channel reconstruction residual, max over all 12 cells × 2 pilot
  worlds: 2.220446049250313e-16** (machine epsilon; the response is the exact
  sum of its five weighted channels).
- **Realized variance shares: max absolute deviation 0.0069843772** (≤ 0.01 ✔).
  Max *relative* deviation **0.0305321845** (3.05%), which the 1%-relative
  reading would fail — see RN-4: the deviation is dominated by `common(o)`,
  whose realized variance is estimated from only `n_occ` independent occasion
  draws (analytic relative sd **5.259%** at n_occ=8, **2.630%** at n_occ=32), so
  3.05% is **0.58σ**. The trait channel's analytic relative sd is 0.930% and its
  largest observed deviation is 0.457 percentage points (1.83% relative, 1.97σ).
  **And it cannot matter:** the dominant contributor, `common(o)`, is exactly
  cancelled in card space (G1a below), so its realized-share fluctuation touches
  no V-1/V-2/V-3 quantity.
- **Stream independence:** max |corr(common latent, interaction latent)| over
  all cells = **0.0724678130**, against a sampling sd of 1/√(n_occ·k) =
  **0.0510310363** (n_occ=8) / **0.0255155182** (n_occ=32) — i.e. **1.42σ**,
  consistent with the constructed independence (disjoint hash salts).

Per-cell reconstruction residual is 2.220e-16 in **all 12 cells**; per-cell share
deviations range 0.001004–0.006984 (absolute) and 0.004016–0.030532 (relative).

### G1a — rule 10: non-degeneracy

**PASS.** Criterion: every **non-zero** channel changes the card panel by
RMS > 1e-6, and the two `w_int` arms differ in both the response and the card
panel.

- **Minimum card-panel RMS change over all non-zero channels and all 12 cells:
  0.0097964619** — four orders of magnitude above the 1e-6 floor. Ranges by
  channel: mu 0.0790–0.0898, slow 0.0236–0.0868, int 0.0143–0.0286, noise
  0.0098–0.0223.
- **`w_int = 0` vs `w_int = equal`, paired on identical world seeds:** response
  panel RMS gap ≥ **0.0808514536**, card panel RMS gap ≥ **0.0172921872**. The
  registered `w_int` contrast is live in both spaces.
- **Disclosed, and NOT a gate input: `common(o)`'s card-panel residual is
  EXACTLY 0.0 in every cell.** This is not a degeneracy of a registered
  contrast — it is **T3's designed cancellation**, realized exactly because the
  occasion grid is shared across authors (RN-1). None of V-1, V-2, V-3 involves
  the common channel; the channel exists so that the world is a frame-bearing
  world for K2b's deployed-gauge use, and so that this leg's card space is the
  *post-cancellation* space the theory says it is. Reported here because a
  channel with an exactly-zero footprint in the leg's own measurement space is
  exactly what rule 10 asks to be surfaced.

### G2a — rule 3: liveness and the pinned decorrelation time

**PASS** on the registered form under RN-9's pinned level and multiplicity.

- **Every non-zero channel's realized share > 0** in every cell; minimum live
  share **0.1938938** (the `int` channel at φ=0.98, n_occ=8, design 0.20).
- **Lag-1 ACF of the slow latent** (pooled ratio-of-sums over 256 authors × 48
  latent coordinates × 2 pilot worlds; the pooled estimator's ratio bias is
  O(1/(#series·m)) so Kendall's single-series AR bias does not apply):

| (φ, n_occ) | E[φ̂] (independent MC, 4·10⁵ series) | measured | per-cell CI95 | contains φ | family-wise CI95 (6 tests) | contains φ |
|---|---|---|---|---|---|---|
| (0.5, 8) | 0.49914905 | 0.50178176 | [0.49779806, 0.50591428] | ✔ | [0.49615804, 0.50712770] | ✔ |
| (0.5, 32) | 0.50020547 | 0.50068711 | [0.49868880, 0.50259144] | ✔ | [0.49804327, 0.50330339] | ✔ |
| (0.9, 8) | 0.90001523 | 0.90229627 | [0.90021584, 0.90433631] | **✘** | [0.89951701, 0.90518228] | ✔ |
| (0.9, 32) | 0.90013954 | 0.90029219 | [0.89927814, 0.90129541] | ✔ | [0.89894990, 0.90165531] | ✔ |
| (0.98, 8) | 0.98004618 | 0.97979164 | [0.97883154, 0.98072039] | ✔ | [0.97849071, 0.98100506] | ✔ |
| (0.98, 32) | 0.97991142 | 0.98000735 | [0.97956941, 0.98045453] | ✔ | [0.97943909, 0.98059809] | ✔ |

**Both readings reported (rule 9): 10/12 cells contain φ at the uncorrected
per-cell 95% level; 12/12 at the family-wise level, which is what the gate
uses.** The single per-cell miss is at (φ=0.9, n_occ=8), 2.23σ, and it is a
**fluctuation, not a bias**: the independent Monte-Carlo of this exact estimator
gives `E[φ̂] = 0.90001523` at that setting, and the largest |E[φ̂] − φ| anywhere
in the grid is **0.0008509472** (itself ~1.6× the MC's own standard error). With
6 independent tests, P(≥1 miss at the uncorrected level) = 1 − 0.95⁶ = 26.5%,
so one miss is the expected outcome, not evidence against the construction.
The φ_slow knob is live and reads back at the pinned value in every cell.

### G3a — power (rule 2), satisfiability and directions (rule 11), rule-13 spec

**PASS.** 2-world pilot (reserved worlds 9501–9502, 512 authors), B = 400
author bootstrap. MDE = 2.8·se (α = .05 two-sided, 80% power).

| cell | se(gap) | MDE(gap) | se(r) | MDE(r) | δ_unit = C/m_h² | ν chosen | δ_int margin | V-3a satisfiable | V-3b z | V-3b satisfiable |
|---|---|---|---|---|---|---|---|---|---|---|
| `phi0.5_occ8_intzero` | 0.00278417 | 0.00779568 | 0.00174149 | 0.00487617 | — | — | — | — | — | — |
| `phi0.5_occ8_intequal` | 0.00402347 | 0.01126572 | 0.00219376 | 0.00614252 | 0.01250000 | **1** | 0.01250000 | ✔ | 23.75 | ✔ |
| `phi0.5_occ32_intzero` | 0.00178685 | 0.00500317 | 0.00062409 | 0.00174744 | — | — | — | — | — | — |
| `phi0.5_occ32_intequal` | 0.00207389 | 0.00580689 | 0.00082635 | 0.00231378 | 0.00078125 | **4** | 0.00312500 | ✔ | 13.18 | ✔ |
| `phi0.9_occ8_intzero` | 0.00153959 | 0.00431085 | 0.00287456 | 0.00804877 | — | — | — | — | — | — |
| `phi0.9_occ8_intequal` | 0.00257499 | 0.00720996 | 0.00326036 | 0.00912902 | 0.01250000 | **1** | 0.01250000 | ✔ | 19.19 | ✔ |
| `phi0.9_occ32_intzero` | 0.00255054 | 0.00714152 | 0.00210411 | 0.00589152 | — | — | — | — | — | — |
| `phi0.9_occ32_intequal` | 0.00264126 | 0.00739552 | 0.00219245 | 0.00613885 | 0.00078125 | **4** | 0.00312500 | ✔ | 11.67 | ✔ |
| `phi0.98_occ8_intzero` | 0.00081398 | 0.00227915 | 0.00311494 | 0.00872183 | — | — | — | — | — | — |
| `phi0.98_occ8_intequal` | 0.00192407 | 0.00538740 | 0.00325183 | 0.00910513 | 0.01250000 | **1** | 0.01250000 | ✔ | 17.19 | ✔ |
| `phi0.98_occ32_intzero` | 0.00112190 | 0.00314132 | 0.00298798 | 0.00836633 | — | — | — | — | — | — |
| `phi0.98_occ32_intequal` | 0.00131035 | 0.00366899 | 0.00304488 | 0.00852566 | 0.00078125 | **4** | 0.00312500 | ✔ | 9.58 | ✔ |

**Directions, stated as rule 11 requires:**

- **V-1** — two-sided: the measured gap's CI must **contain** the Part-0
  prediction, in ≥ 10/12 cells; **plus** an exact ordering match of the six
  (φ, n_occ) cells within *each* `w_int` arm.
- **V-2** — two-sided: the measured `r(card→b)` CI must **contain** the
  prediction, in ≥ 10/12 cells.
- **V-3a** — **one-sided upper**: `upper 95% < +δ_int` (the interaction cannot
  contribute *negative* reproducible covariance by construction). Two-sided TOST
  reported as a second reading.
- **V-3b** — **one-sided lower**: `lower 95% > 0`.

**Satisfiability.** V-1 and V-2 are *containment* clauses, always satisfiable in
form but *sharper the more data there is* — this is disclosed, not hidden. On
the main grid (8 worlds, 2048 authors) the se will be ≈ 1/2 the pilot's, so the
95% half-widths will be roughly **0.0008–0.0040 on the gap** (predictions span
0.0186–0.2263, i.e. a 0.5%–5% relative tolerance) and **0.0006–0.0032 on r**
(predictions span 0.683–0.949, i.e. a **0.07%–0.45% relative tolerance**). V-2
is therefore an extremely stringent test of the attenuation algebra — a 0.3%
systematic error anywhere in the derivation will fail it. Two known O(1/n)
effects are pre-declared and will be reported per cell: (i) the ratio-estimator
bias of a pooled Pearson (estimated by the bootstrap's own bias, mean of
replicates minus point estimate), and (ii) the authors-within-world bootstrap
conditions on the realized occasion-level draws, so its CI is *conditional* and
slightly narrower than an unconditional one; the analytic occasion-level sd is
reported for the V-3 statistics where it dominates.

V-3a and V-3b are satisfiable in **all 6** `w_int > 0` cells under the RN-8
ladder: ν = 1 at n_occ = 8 (margin 0.0125 vs projected half-width 0.00381–0.00390,
≥ 3.2× headroom) and ν = 4 at n_occ = 32 (margin 0.003125 vs projected half-width
0.00102–0.00111, ≥ 2.8× headroom). At n_occ = 32 the ν = 1 margin (0.00078)
is *below* the projected half-width (~0.00105) — that is precisely the
unsatisfiability the pre-stated ladder exists to handle, and it is handled by
widening the margin rather than by narrowing the claim after the fact. Results
at ν = 1, 2, 4 are all reported. V-3b's predicted z ranges **9.58–23.75**.

**Rule-13 spec (first application in the K-line).** Resampling spec: **B = 2000,
seed = master_seed = 20260815**, authors within world, worlds as strata. At
adjudication every registered clause's distance from its boundary is compared to
**2× the Monte-Carlo sd of that CI endpoint** (`sd(q_α) = √(α(1−α)/B)/φ(z_α)·se`,
= 0.0598·se at α = 0.025 and 0.0620·se at α = 0.05, i.e. MC half-widths ~6% of
one se); any clause inside that band is re-run at **B = 20000 (10×)** and scored
**BOUNDARY** — neither HOLD nor MISS — if the verdict moves, with the status
carried into every downstream consequence.

### G5a — hygiene

**PASS.** `float_precision="round_trip"` on every artifact read
(`read_csv_rt`); all persisted floats written at full repr precision; rule-12
source-object header for every channel (RN-3), with the three NEW objects cited
by this script's own line numbers; `suica_core/` untouched; `results/` is
gitignored; the run is fully seeded from `MASTER_SEED = 20260815` with the
reserved pilot indices disjoint from the main grid.

---

## 1. Outcome

**Verdict: `TWO_SPLIT_PROBE_VALIDATED__ATTENUATION_ALGEBRA_EXACT__INTERACTION_OCCASION_BOUND`.**
V-1 **HOLD**, V-2 **HOLD**, V-3 **HOLD**; **no pivot fires** (P1a no, P2a no,
P3a no). Rule 13 triggered 6 stability re-checks at B = 20000; **0 BOUNDARY** —
every triggered verdict is stable at 10× B.

Main grid: 12 cells × 8 worlds × 256 authors = **2048 pooled authors per cell**,
`master_seed = 20260815`, main world indices 0–7 (disjoint from the reserved
pilot 9501–9502). Card space only; the deployed gauge was never invoked.
Stage wall-times: `part0` 1.983 s, `arms` 1.997 s, `finalize` 6.749 s,
post-hoc `diagnostic` 0.189 s — **10.9 s of compute in total**, against a
< 20 min budget. `decision.json` `timestamp_utc = 2026-08-09T08:03:31.817816+00:00`.

### V-1 [prior .80] — the two-split probe reads τ_s: **HOLD**

Clause (a): the measured `ρ_interleaved − ρ_contiguous` CI contains the Part-0
prediction in **11 of 12 cells** (threshold ≥ 10).

| cell | gap predicted | gap measured | CI95 (authors within world, B=2000) | se | boot bias | contains |
|---|---|---|---|---|---|---|
| `phi0.5_occ8_intzero` | 0.1740375289 | 0.1761519955 | [0.1733919098, 0.1789392128] | 1.421e-03 | −2.749e-05 | ✔ |
| `phi0.5_occ8_intequal` | 0.1410301179 | 0.1441264277 | [0.1406206036, 0.1476745027] | 1.813e-03 | +1.208e-05 | ✔ |
| `phi0.5_occ32_intzero` | 0.1155588854 | 0.1152193772 | [0.1136062718, 0.1169171310] | 8.460e-04 | +2.354e-05 | ✔ |
| `phi0.5_occ32_intequal` | 0.1070470653 | 0.1053668542 | [0.1034565041, 0.1074401909] | 1.012e-03 | +3.571e-05 | ✔ |
| `phi0.9_occ8_intzero` | 0.0929033494 | 0.0930285229 | [0.0914444734, 0.0946382600] | 7.988e-04 | +1.489e-05 | ✔ |
| **`phi0.9_occ8_intequal`** | **0.0780179436** | **0.0751940996** | **[0.0727689244, 0.0778969999]** | 1.318e-03 | +4.985e-05 | **✘** |
| `phi0.9_occ32_intzero` | 0.2263189385 | 0.2271750752 | [0.2246453829, 0.2298074947] | 1.344e-03 | +3.211e-05 | ✔ |
| `phi0.9_occ32_intequal` | 0.2136115165 | 0.2150803526 | [0.2122505745, 0.2179151157] | 1.430e-03 | +2.865e-05 | ✔ |
| `phi0.98_occ8_intzero` | 0.0219337793 | 0.0219042426 | [0.0210952359, 0.0226938194] | 4.053e-04 | −2.572e-06 | ✔ |
| `phi0.98_occ8_intequal` | 0.0185815073 | 0.0195085945 | [0.0176529239, 0.0213490994] | 9.405e-04 | +1.265e-05 | ✔ |
| `phi0.98_occ32_intzero` | 0.0870246373 | 0.0867847460 | [0.0856601036, 0.0879500944] | 5.845e-04 | +3.336e-05 | ✔ |
| `phi0.98_occ32_intequal` | 0.0829304978 | 0.0842162414 | [0.0829126187, 0.0856552143] | 7.014e-04 | +3.609e-05 | ✔ |

The single miss, `phi0.9_occ8_intequal`, misses by **0.0001209** — the
prediction sits 0.00012 above the CI's upper edge, i.e. 0.092 se. Rule 13 fired
on it (distance 1.21e-04 vs 2× MC sd 1.58e-04) and the verdict is **STABLE** at
B = 20000 (CI [0.07266122, 0.07771081], still excluding 0.07801794). It is a
genuine, stable miss of a very tight interval, not a Monte-Carlo artefact — see
§1.4 for what causes it.

Clause (b): **the (φ_slow, n_occ) ordering matches the prediction EXACTLY, in
both arms and in the pooled 12-cell reading.**

| arm | predicted order (descending gap) | measured order | match |
|---|---|---|---|
| `w_int = 0` | (0.9,32) ≻ (0.5,8) ≻ (0.5,32) ≻ (0.9,8) ≻ (0.98,32) ≻ (0.98,8) | identical | ✔ |
| `w_int = equal` | (0.9,32) ≻ (0.5,8) ≻ (0.5,32) ≻ **(0.98,32) ≻ (0.9,8)** ≻ (0.98,8) | identical | ✔ |
| all 12 cells | (see `decision.json`) | identical | ✔ |

This is the strongest single result in the leg. The ordering is **not**
monotone in φ_slow and **not** monotone in n_occ; the algebra predicts a
specific interleaving of the two factors, including the **arm-dependent swap**
of (0.98, 32) and (0.9, 8) that only the RN-2 renormalization produces — and
the measurement reproduces all 12 positions. A probe that merely "went up with
persistence" would not have passed this.

### V-2 [prior .80] — the attenuation algebra: **HOLD, 12/12**

The measured `r(card → b)` CI contains the Part-0 prediction in **all 12 cells**
under the registered raw-trait reading, and in **all 12** under the
author-centred second reading (RN-6).

| cell | r predicted (raw b) | r measured | CI95 | se | boot bias |
|---|---|---|---|---|---|
| `phi0.5_occ8_intzero` | 0.8510600526 | 0.8522393044 | [0.8504775994, 0.8539105060] | 8.601e-04 | −2.804e-05 |
| `phi0.5_occ8_intequal` | 0.8148339920 | 0.8161172071 | [0.8139338055, 0.8181461369] | 1.067e-03 | −4.777e-05 |
| `phi0.5_occ32_intzero` | 0.9492418399 | 0.9496233986 | [0.9489895652, 0.9502612006] | 3.193e-04 | −1.994e-06 |
| `phi0.5_occ32_intequal` | 0.9361029109 | 0.9362481790 | [0.9354864412, 0.9369992656] | 3.963e-04 | −2.349e-06 |
| `phi0.9_occ8_intzero` | 0.7366319498 | 0.7356436827 | [0.7328510491, 0.7385907831] | 1.451e-03 | +5.637e-05 |
| `phi0.9_occ8_intequal` | 0.7127639867 | 0.7121493433 | [0.7090211797, 0.7153231538] | 1.601e-03 | +5.912e-05 |
| `phi0.9_occ32_intzero` | 0.8318111461 | 0.8311300797 | [0.8291224711, 0.8330808315] | 9.976e-04 | −1.389e-06 |
| `phi0.9_occ32_intequal` | 0.8229274643 | 0.8220025321 | [0.8199092624, 0.8240518821] | 1.051e-03 | +9.598e-06 |
| `phi0.98_occ8_intzero` | 0.7036964308 | 0.7058043332 | [0.7024178084, 0.7091408352] | 1.706e-03 | +3.117e-05 |
| `phi0.98_occ8_intequal` | 0.6828010739 | 0.6845089751 | [0.6809371189, 0.6879861672] | 1.806e-03 | +4.700e-05 |
| `phi0.98_occ32_intzero` | 0.7375581699 | 0.7390514425 | [0.7359927675, 0.7420172017] | 1.518e-03 | −2.317e-05 |
| `phi0.98_occ32_intequal` | 0.7313438620 | 0.7330846966 | [0.7299959326, 0.7360321400] | 1.550e-03 | −2.447e-05 |

Largest absolute error anywhere: **0.0021079** (`phi0.98_occ8_intzero`); largest
*relative* error **0.30%**. The bootstrap's own bias estimate never exceeds
**5.9e-05**, i.e. the pooled-Pearson ratio bias flagged in G3a is one to two
orders below the CI half-widths and changes no verdict. G3a projected a
0.07%–0.45% relative tolerance for this clause and the algebra met it in every
cell. **`r = σ_b/√(σ_b² + Var(s̄) + Var(s̄_int) + σ_e²/n_eff)`, with `Var(s̄)`
the exact AR sum at m = n_occ, is exact on this world to within measurement
error at 2048 authors.** No rule-13 trigger fired on any V-2 clause.

### V-3 [prior .75] — the interaction channel is typed correctly: **HOLD, 6/6 and 6/6**

Clause (a) — **the interaction contributes nothing reproducible across
occasion-disjoint halves.** One-sided upper 95% of the int channel's
contribution to the CONTIGUOUS cross-half covariance, against the RN-8 margin:

| cell | measured | CI95 | one-sided upper 95% | ν | δ_int margin | pass | occ-inflated upper | pass | TOST |
|---|---|---|---|---|---|---|---|---|---|
| `phi0.5_occ8_intequal` | +0.0000040315 | [−0.0011082801, +0.0011232971] | +0.0009552093 | 1 | 0.01250000 | ✔ | +0.0031770884 | ✔ | ✔ |
| `phi0.5_occ32_intequal` | −0.0001239597 | [−0.0006507744, +0.0003604809] | +0.0002918912 | 4 | 0.00312500 | ✔ | +0.0007450111 | ✔ | ✔ |
| `phi0.9_occ8_intequal` | +0.0007649003 | [−0.0006261215, +0.0021084595] | +0.0017942043 | 1 | 0.01250000 | ✔ | +0.0039940829 | ✔ | ✔ |
| `phi0.9_occ32_intequal` | −0.0004443477 | [−0.0010557907, +0.0001589120] | +0.0000596104 | 4 | 0.00312500 | ✔ | +0.0004638923 | ✔ | ✔ |
| `phi0.98_occ8_intequal` | −0.0008262085 | [−0.0021204597, +0.0004893927] | +0.0003026776 | 1 | 0.01250000 | ✔ | +0.0023949349 | ✔ | ✔ |
| `phi0.98_occ32_intequal` | −0.0001701318 | [−0.0007807813, +0.0004754332] | +0.0003564428 | 4 | 0.00312500 | ✔ | +0.0007551793 | ✔ | ✔ |

**All three readings agree in all six cells**: the registered one-sided upper
bound, the occasion-level-inflated upper bound (widening by the analytic
occasion-level sd the registered bootstrap cannot see), and the two-sided TOST.
Every one of the six also clears the **strictest ν = 1** margin: the largest
one-sided upper bound anywhere is **+0.0017942** against ν=1 margins of
0.0125 (n_occ=8) and 0.00078125 (n_occ=32) — the n_occ=32 cells have upper
bounds 0.0000596–0.0003564, all **below** even the unwidened one-shared-occasion
unit. Expressed as a fraction of one shared occasion's worth
(`λ = covint_contiguous / covint_same_occ_half`, margin `1/m_h`), |λ| ≤ 0.0374
everywhere against margins of 0.25 (n_occ=8) and 0.0625 (n_occ=32).
Second reading, the INTERLEAVED split (also predicted 0, not a registered
clause): measured −0.0005868 … +0.0001650, upper 95% ≤ +0.0011551 — same
conclusion.

Clause (b) — **the same-occasion signature is present and lands on its predicted
magnitude.** One-sided lower 95% > 0 in **all six** cells, and — beyond what
V-3(b) asked — the measured signature matches the Part-0 point prediction
`(C/n_occ)(1−1/n)` in all six:

| cell | predicted | measured | CI95 | one-sided lower 95% | > 0 | half-set: predicted | measured |
|---|---|---|---|---|---|---|---|
| `phi0.5_occ8_intequal` | 0.0249023437 | 0.0244149457 | [0.0233671536, 0.0255100459] | 0.0235296848 | ✔ | 0.0498046875 | 0.0491834984 |
| `phi0.5_occ32_intequal` | 0.0062255859 | 0.0060738268 | [0.0055597121, 0.0065573072] | 0.0056454030 | ✔ | 0.0124511719 | 0.0125090941 |
| `phi0.9_occ8_intequal` | 0.0249023437 | 0.0256279639 | [0.0243644801, 0.0269175031] | 0.0245708674 | ✔ | 0.0498046875 | 0.0503919371 |
| `phi0.9_occ32_intequal` | 0.0062255859 | 0.0058179152 | [0.0052664068, 0.0063659359] | 0.0053630373 | ✔ | 0.0124511719 | 0.0118760140 |
| `phi0.98_occ8_intequal` | 0.0249023437 | 0.0243540189 | [0.0230413765, 0.0256169906] | 0.0232962428 | ✔ | 0.0498046875 | 0.0481040102 |
| `phi0.98_occ32_intequal` | 0.0062255859 | 0.0063110494 | [0.0057137128, 0.0069471065] | 0.0058152228 | ✔ | 0.0124511719 | 0.0128518481 |

The predicted signature is contained in the measured CI in **6/6** cells (this
point-prediction check was computed in Part 0 but is not itself a registered
clause — reported as a bonus designed-identity confirmation). **The object IDT
appendix E.2 said F2's family could not express now exists, is measurable, and
behaves exactly as typed: it is invisible across occasions and fully visible
within one.**

### 1.4 The one thing that did not come out exact, diagnosed (rule 9)

`ρ_interleaved` **on its own** contains its prediction in only **8 of 12**
cells, while `ρ_contiguous` is **12/12** and `ρ_same_occ` is **12/12**. The
failure is not random across the design:

| arm | ρ_interleaved contains prediction | ρ_contiguous | gap |
|---|---|---|---|
| `w_int = 0` (6 cells) | **6/6** | 6/6 | 6/6 |
| `w_int = equal` (6 cells) | **2/6** | 6/6 | 5/6 |

**Every miss is in a cell that has an interaction channel; no cell without one
misses.** The cause is the effect pre-declared in G3a: the registered bootstrap
resamples *authors within world*, so it **conditions on each world's realized
occasion-level draws** — including the interaction shocks `S(o)`, whose realized
second moments fluctuate with relative sd `√(2/k) = 20.4%` per occasion, i.e.
`√(2/(k·m_h·W)) = 3.61%` (n_occ=8) / 1.80% (n_occ=32) on the card's interaction
variance after averaging. That term is 14% of `ρ_interleaved`'s denominator at
n_occ=8, giving an expected ±0.0017–0.0019 wobble in `ρ_interleaved` that the
conditional CI (se ≈ 0.0010–0.0015) does not cover. The observed deviations in
the `w_int > 0` arm are +0.0034, −0.0014, −0.0023, +0.0001, −0.0000, +0.0007 —
exactly that scale, and of both signs (no bias).

Two independent confirmations that this is a **coverage** effect and not an
algebra error:

1. The **design contrast itself**: 6/6 containment where the channel is absent,
   2/6 where it is present, with the same estimator and the same algebra.
2. **Post-hoc world-block diagnostic** (`post_hoc_world_bootstrap.{csv,json}`,
   flagged post-hoc, **not** a lean input): resampling the 8 world blocks —
   which *does* include the occasion-level component — raises `ρ_interleaved`
   containment in the `w_int > 0` arm from **2/6 to 5/6** (overall 8/12 →
   10/12). It simultaneously *lowers* the gap's containment (11/12 → 9/12) and
   `ρ_interleaved` in the `w_int = 0` arm (6/6 → 5/6), which is the expected
   behaviour of an 8-block percentile interval — such intervals under-cover
   badly at that block count. The registered authors-within-world reading
   therefore remains the controlling one, and the world-block reading is
   evidence about the *variance component*, not a better CI.

**Why V-1's registered statistic survives while its component does not:** both
splits use `m_h` occasions, so the interaction contributes the identical
`C/m_h` term to both denominators, and the occasion-level wobble largely
cancels in the difference. The registration chose the **gap** — appendix A's
own object — and the gap is precisely the contrast that is robust to the
channel's occasion-level sampling. That is a property of T6′'s estimator worth
recording for K2b: *read the difference, not either half.*

The one gap miss (`phi0.9_occ8_intequal`, 0.00012 outside a 0.0051-wide
interval, stable at B = 20000) is the residue of the same effect in the one cell
where the cancellation is least complete — its `ρ_interleaved` deviation is
−0.0023 against `ρ_contiguous` +0.0006.

**Second readings for the gap (rule 9, all reported):** the mean per-author
**cosine** form (IDT §1's `ρ_i`) contains the prediction in only **5/12** cells
— expected and pre-declared, since `E[cos] ≠ ratio of expectations` at finite
dimension, so the closed-form prediction is only first-order correct for that
estimator; the mean-centred pooled **Pearson** form gives **11/12**, agreeing
cell-for-cell with the registered uncentred form. Anyone building on T6′ should
use a pooled second-moment form, not a mean-of-cosines.

### Rule 13 — Monte-Carlo verdict stability (first application in the K-line)

Spec as registered: B = 2000, seed = master_seed = 20260815; any clause whose
boundary lies within 2× the Monte-Carlo sd of its own CI endpoint is re-checked
at B = 20000. **Six clauses triggered; all six are STABLE; zero BOUNDARY.**

| cell | clause | boundary | MC sd of endpoint (B=2000) | distance to boundary | verdict B=2000 | verdict B=20000 | status |
|---|---|---|---|---|---|---|---|
| `phi0.5_occ8_intequal` | gap_cos | 0.14103012 | 1.09e-04 | 1.72e-04 | contains: no | contains: no | STABLE |
| `phi0.9_occ8_intequal` | gap | 0.07801794 | 7.90e-05 | 1.21e-04 | contains: no | contains: no | STABLE |
| `phi0.9_occ8_intequal` | rho_interleaved | 0.81612113 | 6.90e-05 | 9.40e-05 | contains: no | contains: no | STABLE |
| `phi0.9_occ8_intequal` | gap_pearson | 0.07801794 | 7.90e-05 | 1.23e-04 | contains: no | contains: no | STABLE |
| `phi0.98_occ32_intequal` | gap | 0.08293050 | 4.20e-05 | 1.80e-05 | contains: **yes** | contains: **yes** | STABLE |
| `phi0.98_occ32_intequal` | gap_pearson | 0.08293050 | 4.20e-05 | 1.70e-05 | contains: **yes** | contains: **yes** | STABLE |

Note `phi0.98_occ32_intequal`: the prediction sits **1.8e-05** inside the CI's
lower edge — 0.43 MC sd — and holds at 10× B (B=20000 CI
[0.08287352, 0.08560472], still containing 0.08293050). Under K1d's experience
this is exactly the configuration that would have been mis-read as a clean HOLD;
rule 13 checked it and it is genuinely stable. **The rule cost 6 extra bootstrap
runs (≈ 4 s) and changed no verdict — its first application is a clean bill of
health, which is the outcome a stability rule should mostly produce.**

### Pivots

- **P1a** (V-1 fails in ≥ 3 cells → STOP the K2 line): **does not fire.** One
  failing cell (`phi0.9_occ8_intequal`); its full geometry is published in §1.1
  and §1.4 regardless.
- **P2a** (V-3 fails → redesign the interaction channel): **does not fire.**
- **P3a** (G1a/G2a fail → STOP): **does not fire**; Part 0 passed.

### What the leg establishes

1. **An expressive world exists.** IDT appendix E.2's gap is closed: this world
   carries a slow person state with a pinned, verified τ_s **and** a genuine
   person×occasion interaction channel, on top of F2's own trait, frame and
   noise objects, with exact five-channel reconstruction (2.22e-16) and every
   channel live.
2. **T6′'s two-split probe is validated as an instrument.** Its predicted
   magnitude is met in 11/12 cells and — the sharper test — its full
   **(φ_slow, n_occ) ordering is reproduced exactly in both arms**, including a
   non-monotone pattern and an arm-dependent rank swap that no crude
   "persistence ⇒ bigger gap" heuristic would produce.
3. **T4's attenuation algebra is exact**, 12/12, to ≤ 0.30% relative error under
   CI half-widths as tight as 0.0006. `Var(s̄)` from the exact AR sum at
   m = n_occ is the right object; the interaction and noise terms enter exactly
   as `C/n_occ` and `E/(2·n_occ)`.
4. **The interaction channel is occasion-bound as typed**: zero reproducible
   contribution across occasion-disjoint halves within even the strictest
   one-shared-occasion margin, and a same-occasion signature that matches its
   predicted magnitude in all six cells.
5. **A usable caution for K2b**: `ρ_interleaved` alone is not a reliable
   card-level readout when a person×occasion channel is present and the CI is
   conditioned on occasions — the occasion-level variance component is real and
   the registered bootstrap does not see it. **Read the gap.** Any K2b clause
   about a single split's ρ must either use a world-level resample or carry the
   analytic occasion-level term.
6. **The three second readings that disagree are recorded**, so nobody rebuilds
   the probe on the wrong estimator: mean-of-cosines 5/12, mean-centred Pearson
   11/12, uncentred pooled (registered) 11/12.

### Anomalies, with timing

- **(i) The ACF gate's level and multiplicity were unpinned — caught and
  resolved BEFORE any hypothesis-relevant number existed.** While computing
  Part 0, the registered G2a form ("within CI of φ_slow per cell") was found to
  name neither a CI level nor a multiplicity treatment; at an uncorrected
  per-cell 95% level, 1 of 6 independent tests missed (φ=0.9, n_occ=8, 2.23σ)
  — the *expected* outcome, since P(≥1 miss) = 26.5%. Resolved by RN-9 before
  the report's Part 0 was written and before the `arms` stage was invoked:
  family-wise 95% over the 6 distinct (φ, n_occ) pairs, **both readings
  reported**, plus an independent Monte-Carlo of `E[φ̂]` for this exact
  estimator which showed the deviation is a fluctuation, not a bias
  (`E[φ̂] = 0.90001523` at that setting; max |E[φ̂] − φ| = 8.51e-04 anywhere).
  The only worlds touched at that point were the reserved pilot 9501–9502; no
  V-1/V-2/V-3 quantity existed.
- **(ii) The "within 1% of design" share gate was ambiguous, and the relative
  reading is unsatisfiable — resolved before arms.** RN-4 pins the absolute
  reading and derives why: `common(o)`'s realized variance rests on only n_occ
  occasion draws (analytic relative sd 5.26% at n_occ=8), so a 1%-relative gate
  would be a 0.19σ demand on a correct generator. Both readings reported
  (absolute max 0.0069844 ✔; relative max 0.0305322 ✘-under-that-reading).
  Resolved during Part 0, before any main arm.
- **(iii) `common(o)` has an exactly-zero footprint in this leg's measurement
  space.** Disclosed in G1a and excluded from the gate by argument, not by
  convenience: it is T3's designed cancellation, it involves no registered
  contrast, and the channel's purpose is to make the world frame-bearing for
  K2b. Known and stated in Part 0, before arms.
- **(iv) The post-hoc world-block bootstrap (§1.4) was added AFTER the
  registered adjudication**, in response to the ρ_interleaved pattern. It is
  labelled post-hoc throughout, written to its own artifact, and is not an input
  to any lean; `decision.json` was produced before it existed and was not
  rewritten.
- **(vi) The generator-mirror claim was verified AFTER the arms, not before.**
  The script's docstring asserted that this leg's `mean_part` mirror is
  bit-identical to f2's own object; at Part 0 that was an *assertion*, not a
  measurement (`gates.json` carries a vestigial `mirror_residual_max = 0.0`
  that was never written to). Rule 8 makes a claim about code a factual claim,
  so it was verified — against f2's own `generate_world_composed` used as a
  bit-exact oracle — in the `diagnostic` stage, **after** `arms` and
  `finalize`. Result: **max |residual| = 0.0, bit-identical, in all six
  (φ_slow, n_occ) configurations.** The check therefore confirms rather than
  changes anything, but its timing is late and is recorded as such; `gates.json`
  and `decision.json` were not rewritten, so the Part-0 audit trail
  (`timestamp_utc = 2026-08-09T07:59:22.683396+00:00`, before `arms`) stands
  untouched. Had the residual been non-zero, the leg would have been reported
  as defective rather than adjudicated.
- **(v) Nothing else.** `part0` was invoked exactly three times, all before the
  report existed and all on reserved pilot worlds (the first two invocations
  preceded RN-9's and G2a's ACF-CI machinery being added; the outputs of all
  three are identical for G0a/G1a/G3a/G4a, which are seeded deterministically).
  `arms` was invoked exactly once, `finalize` exactly once, `diagnostic` exactly
  once. No background job, no monitor, no stage exceeded 7 s.

### Artifacts

`results/m4_k2a_expressive_world/` (gitignored): `manifest.json`, `gates.json`,
`part0_predictions.csv`, `part0_tables.md`,
`cell_phi{0.5,0.9,0.98}_occ{8,32}_int{zero,equal}.csv` (12 files, per-author
sufficient statistics), `cells.csv`, `rule13_stability.csv`, `decision.json`,
`post_hoc_world_bootstrap.{csv,json}` (post-hoc).
