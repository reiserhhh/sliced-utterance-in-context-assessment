# SUICA M4-K2e — Double matching: does the reader tax raw person-variance, or the occasion-bound species?

**Tier:** EXPLORATORY · label-free · synthetic throughout.
**Banner:** synthetic worlds calibrated to an opened-panel regime, exploratory.
**Registration:** `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md` § "M4-K2e — Double matching …",
REGISTERED 2026-08-09 BEFORE RUN, commit `0db4480`. The registration text is binding; this
executor did implementation and execution only.
**Script:** `scripts/run_suica_m4_k2e_double_matching.py`
**Artifacts:** `results/m4_k2e_double_matching/` (gitignored).
**Theory:** `docs/SUICA_IDENTITY_THEORY_V1.md` T4 (S3), appendices J and K.

---

## Part 0 — gates computed 2026-08-09T10:29:56.366938+00:00 (UTC), written to disk BEFORE any main arm

Part 0 ran on RESERVED pilot worlds **9901–9904** (disjoint from main indices 0…63).
`results/m4_k2e_double_matching/gates.json`, `part0_arms.json`, `part0_predictions.csv`,
`part0_kappa_cells.csv`, `part0_vs_phi_enumeration.csv`, `part0_pilot_field.csv` and
`part0_tables.md` carry every number below at full precision; the `arms` stage refuses to
run unless every Part-0 gate passes **and this report exists on disk** (`require_part0()`).
Part-0 wall time **17.302 s** (share solve 0.211 s, pilot 16.636 s). **No
hypothesis-channel run of any kind preceded this stage** — the only pre-Part-0 execution
was a pure card-algebra check of the registration's closed form (no world built, no field
number produced), whose numbers are re-derived identically here.

### 0.0 Standing-rule-14 self-check (required by G5e)

**No gate and no branch lean in this leg compares quantities across scales without a
registration-pinned link.** G0e re-derives K2b's, K2c's and K2d's own numbers against
themselves; G1e compares **card attenuation to card attenuation** and **variance share to
variance share**; G2e, G4e, every per-pair **cell**, and **L-VAR / L-SPEC / L-NEG / L-UND**
compare **field agreement to field agreement**, within-pair, same instrument, same units.

**L-VS is the one lean that does cross scales** — a field difference against a
design-variance quantity — and it satisfies rule 14 by that rule's **first** clause: the
registration **pins the link function and its coefficient explicitly**
(`D_VS_pred = −0.7220359963712748 × ΔV_person`), so the link is part of the lean, not an
executor choice. The only unpinned cross-scale object is the **q-update**, which the
registration declares *descriptive, no gate*, and which pins its own link (a log-log power
law whose exponent `q` **is** the estimand).

### 0.1 Rule-12 header — every manipulated channel by generator SOURCE OBJECT

| object | source |
|---|---|
| slow AR(φ) latent `xs` | `k2b:333-337` (f2:173-176 form) |
| occasion-keyed shock stream `S(o) ~ N(0, I_k)` | `k2a:174-181` `shock_int_matrix`, salt `m4k2a-shock-int` |
| person loadings `a_i ~ N(0, I_k)` | `k2b:338-341` `a_load`, salt `m4k2b-loading` |
| `u_int = einsum("ij,ojl->iol", a_load, shocks)/√k` | `k2b:342-343` |
| `s_int = A_SCALE · ((u_int · G_PROFILE) @ loadings.T)` | `k2b:344` |
| panel emission of the interaction channel | `k2b:374-375` |
| card-side cell-centring of the channel | `k2b:416`, `k2b:425-426` |
| entry into the attenuation algebra as `C/m`, `C/half` | `k2b:537`, `k2b:549`, `k2b:559`, `k2b:562` |
| `κ(φ)` and `κ_int` | this script `kappa_coefficients()`, read out of `k2b:533-584` unchanged |
| arm weight generalization (a CHOSEN interaction share) | `k2d:206-238` `install_species_weights`, imported and called **unmodified** |
| realized variance shares | `k2b:698-703`, factored into this script's `realized_person_shares()` so it runs on **every** world |

**The one new measurement object** is `realized_person_shares()`. `k2b` computes realized
variance shares only under `verify=True` (one world per arm); G1e's post-arms clause is
about the realized `V_person` share on the **adjudicated** worlds, so it must run
everywhere. Same route, same arithmetic: per-channel `emit_panel`, mean square over every
emitted coordinate, normalized by the total. **Verified bit-exact against k2b's own verify
route on pilot world 9901: residual 0.0 across all six arms and all five channels.**

### 0.2 Register-notes (rule 9 — open conventions fixed BEFORE any hypothesis number)

- **RN-1 (the `V_person` currency for the registered VS prediction).** The registration
  writes `D_VS_pred = −0.7220359963712748 × ΔV_person(realized)`, computed in Part 0.
  "Realized" admits two readings. **PRIMARY, fixed here: the DESIGN variance share via
  `k2b.arm_shares` (slow + interaction)** — the exact currency `κ̂` was fitted in, and G0e
  re-derives all six of K2d's fitted person-variance columns bit-exactly in it, so the
  prediction is consistent with its own coefficient and carries no pilot noise.
  **SECONDARY, reported as rule 9 requires: the pilot-EMPIRICALLY-realized share** (mean
  over the four reserved pilot worlds). **Both predictions are stated below and L-VS is
  scored under both.**
- **RN-2 (VS-62's φ assignment).** "ΔV_person maximized within φ ∈ {.90, .98}" — all four
  ordered assignments are enumerated in Part 0 (pure card algebra). The two same-φ
  assignments give ΔV = 0 identically; the two mixed assignments give ±0.017242228237951546,
  i.e. the maximum |ΔV| is attained by both. The **signed** maximum under this leg's
  `D = field(a) − field(b)` convention, and continuity with K2c/K2d where arm a is always
  the φ .90 arm, selects **φ_a = .90, φ_b = .98**.
- **RN-3 (which G1e clause applies to which pair).** The registration states the double
  clause "**per DM pair**". The VS pair's ΔV_person is **maximized by design**, so applying
  the person clause to it would void the very pair the registration built. Fixed: the
  **attenuation** clause applies to all three pairs; the **V_person** clause applies to the
  two DM pairs only.
- **RN-4 (pilot convention — the registration's explicit choice).** **CHOSEN: the 4-world
  pilot** (the registration's primary option), not the 2-world + χ² inflation. Reason: K2d
  anomaly A-5 — which bought this convention — showed a 2-world pilot estimating the paired
  sd on **one** degree of freedom and underestimating the realized sd by 2.05×–7.83×. Four
  worlds give **3 df** for 12 extra arm-worlds (≈8 s). The χ²-90% inflation factor
  `√(df/χ²_{.10,df})` is **reported as a disclosure** at both df (df=3 → **2.265765949425734**;
  df=1 → **7.957896561090547**, which is exactly the scale of K2d's observed shortfall);
  the **gate** is the registered plain 4-world MDE. χ² quantiles cross-checked against
  `scipy.stats.chi2.ppf` — **bit-exact at both df**.
- **RN-5 (seed lineage).** K2e's own: `master_seed 20260819`, salt `m4k2e-world`, seed a
  function of the **world index only**, so both arms of every pair share trait, AR
  innovations, frame shocks, interaction loadings and noise bit-for-bit and every `D` is a
  within-world difference.
- **RN-6 (provenance).** `k2b.run_field_world` is called unmodified, so corpus tags keep
  the literal prefix `m4k2b-`; every K2e arm id is prefixed `K2E-`, making every tag
  disjoint from K2b/K2c/K2d. Hash labels only.
- **RN-7 (VOID handling; K2d's precedent).** A VOID pair is scored **INDET** for lean
  purposes, with `cell_raw` recorded. Under the registered predicates this is fully routed
  in every case (the rule-16 enumeration below covers INDET explicitly), so no unrouted
  outcome can arise from a void.
- **RN-8 (a VOID VS pair).** L-VS cannot be scored HOLD on a pair whose matching gate
  failed; a VOID VS pair scores L-VS **MISS** with status VOID, and both raw readings are
  still reported.
- **RN-9 (`CI lower(|D|)`, inherited verbatim from K2d RN-2/RN-3).** `|D|`'s interval lower
  endpoint is `min(|lo|,|hi|)` when the D-interval excludes 0 and **exactly 0** when it
  includes 0. "CI inside ±M" and "≥ M" are **inclusive**.
- **RN-10 (declared descriptive, no gate, no branch weight).** Two companions are computed
  in `finalize` under rules fixed here: (i) the **q-update** over 25 arms (registered
  descriptive); (ii) a **κ re-fit over 9 pairs** (3 K2c + 3 K2d + 3 K2e) by the same
  OLS-through-the-origin. Neither gates anything.

### 0.3 The solvability argument, verified numerically (G1e, Part-0 half)

The registration's closed form is **exact, not a linearization**, and the reason is worth
stating because it is what makes the double match possible at machine precision.
`k2b:541-543` writes the per-cell card variance as
`var_card = A + Bv·ar_set_var(arange(m), φ) + C/m + E/m`, so with

* `κ(φ) = Σ_cell n·kap·ar_set_var(arange(m), φ) / Σ_cell n·kap`
* `κ_int = Σ_cell n·kap·(1/m) / Σ_cell n·kap`

the attenuation is `r² = A·K1 / (N·(A + Bv·κ(φ) + (C+E)·κ_int))`. Matching the **person
total** (`v_B + w_B = v_A`) holds the trait weight `A = (1−v)·V_s/2` — hence the whole
attenuation numerator — **identical across the pair**, and `E` is fixed, so
`r(a) = r(b) ⟺ v_A·κ(.90) = v_B·κ(.98) + w_B·κ_int`. Two linear equations, two unknowns.

| quantity | value |
|---|---|
| `κ(.90)` | `0.6748147425129817` |
| `κ(.98)` | `0.9194934207437646` |
| `κ_int` | `0.08461422543701025` |
| ordering `κ_int < κ(.90) < κ(.98)` (the registration's positivity condition) | **True** |
| `κ(.98)/κ(.90)` | `1.3625258385122765` |
| `κ(.90)/κ_int` | `7.975 …` (`7.975214…`) |

The last row is the whole leg in one number: **the card charges persistent state ≈8× what
it charges occasion-bound state**, which is exactly the exchange rate the recombination
trades along.

#### The solved shares and BOTH matching residuals

| pair | kind | target r | arm a (share, int, φ) | r(a) | V_person(a) | arm b (share, int, φ) | r(b) | V_person(b) | \|Δr\| | \|ΔV\| | matched |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `DM-68` | double-matched | 0.68 | `DM68a` (`0.29267462506992153`, 0, .90) | `0.68` | `0.0878023875209765` | `DM68b` (`0.20690025098519338`, `0.08577437408472816`, .98) | `0.68` | `0.08780238752097648` | **0.0** | **1.388e-17** | **True** |
| `DM-56` | double-matched | 0.56 | `DM56a` (`0.4973617623232523`, 0, .90) | `0.5600000000000002` | `0.1492085286969757` | `DM56b` (`0.3515995738630727`, `0.14576218846017958`, .98) | `0.5600000000000002` | `0.1492085286969757` | **0.0** | **0.0** | **True** |
| `VS-62` | variance contrast | 0.62 | `VS62a` (`0.39758432365362883`, 0, .90) | `0.6200000000000001` | `0.11932306584918852` | `VS62b` (`0.3401102295271236`, 0, .98) | `0.62` | `0.10208083761123697` | **1.110e-16** | `0.017242228237951546` (by design) | **True** (attenuation clause; RN-3) |

Closed-form residuals: `v_B + w_B − v_A` = **0.0** and **0.0**; the linear constraint
`v_B·κ(.98) + w_B·κ_int − v_A·κ(.90)` = **2.7755575615628914e-17** and **0.0**.
Both DM pairs satisfy **both** ≤1e-12 clauses — 2/2, and by ~5 orders of margin.

**Continuity note (not a defect):** `DM68a` and `DM56a` solve to shares **bit-identical**
to K2c's `P2a`/`P3a` and K2d's `SP68slow`/`SP56slow`. The a-arms of this series are the
same object at every level; only the b-arms change.

**Instrument-boundary note (K2d anomaly A-2).** The registration warned that "w_int here
exceeds K2a's validated range". Measured, it does **not**: the solved interaction signal
fractions are `0.08577437408472816` (DM-68b) and `0.14576218846017958` (DM-56b) against
K2a's validated equal-share ceilings `(1−v_B)/3` = `0.26436658300493554` and
`0.21613347537897576` — **both inside**, and far below K2d's 0.2807/0.3769. Realized
interaction **variance** shares are `0.02573231222541845` and `0.04372865653805388`. The
registration's instruction stands regardless and is obeyed: **no GAP-based clause gates
anything in this leg**; GAP is reported descriptively only.

### 0.4 The REGISTERED quantitative prediction for VS-62 (L-VS)

`κ̂ = −0.7220359963712748` (G0e re-derives it bit-exactly, below).

| reading | ΔV_person | predicted `D_VS` |
|---|---|---|
| **DESIGN (PRIMARY, RN-1)** | `0.017242228237951546` | **`−0.012449509445450275`** |
| pilot-realized (SECONDARY, RN-1) | `0.017443052563754738` | `−0.012594511837627172` |

The two readings differ by **0.000145002392176897** — 69× smaller than the ±0.010
tolerance, so they cannot disagree on the tolerance clause and can disagree on containment
only in a measure-zero band. **L-VS holds iff the measured `D_VS` CI contains the predicted
value AND `|D_VS − pred| ≤ 0.010`** (prior .70).

### 0.5 Rule-16 — the FULL adjudication object, enumerated as one truth table

This leg is rule 16's **first full application**: the enumeration must cover cells, lean
predicates **and** routing, with every realizable combination routed to exactly one
outcome. Three layers, all verified before any hypothesis number existed.

**Layer 1 — the per-pair cell space (K2d's table verbatim, M1 = 0.020, M2 = 0.010).**
`k2d.enumerate_cell_space()` called unmodified: **25 155** `(point, lo, hi)` triples
searched against a 6-clause truth table (sign carried as c6, since the registration folds
it into the cell NAME), **30/64** clause combinations realizable, **0 overlaps**, all
**seven** signed cells realized. **PASS.**

**Layer 2 — the four lean predicates over all 7 × 7 = 49 ordered DM-cell pairs.**

- **L-VAR [prior .60]** := both DM ∈ {NULL, WEAK-NULL}
- **L-SPEC [.30]** := ≥1 DM ∈ {MAT-SIG(+), SUB-SIG(+)} and no DM in a negative-sign cell
- **L-NEG [.05]** := ≥1 DM ∈ {MAT-SIG(−), SUB-SIG(−)}
- **L-UND [.05]** := any other combination
- Precedence (registered): **L-NEG > L-SPEC > L-VAR > L-UND**

Enumerated **before** precedence is applied, so a nonzero overlap would be a registration
defect that precedence could not hide: **49/49 unique, 0 overlap, 0 gap.** The
registration's own gloss — "L-UND ⟺ at least one INDET and no significant cell" — was
checked as a separate predicate on all 49 combinations: **0 mismatches**. All four leans
realized; counts **L-NEG 24, L-SPEC 16, L-UND 5, L-VAR 4**. **PASS.**

*Why it partitions, stated as rule 16 requires:* L-NEG fires iff a negative significant
cell is present; L-SPEC's own definition excludes negatives, so the two are disjoint before
precedence ever applies (the registered precedence is therefore confirmatory, not
load-bearing); L-VAR requires both cells bounded, hence neither positive nor negative
significant, disjoint from both; and the remainder — no significant cell, not both bounded
— is exactly "≥1 INDET with no significant cell", which is L-UND.

**Layer 3 — routing over all 49 × 2 = 98 (DM-cell-pair, L-VS) combinations.**

| lean | L-VS | outcome | # cell-pairs |
|---|---|---|---|
| L-NEG | hold / miss | **P-NEG** | 24 / 24 |
| L-SPEC | hold / miss | **P-SPEC** | 16 / 16 |
| L-UND | hold / miss | **P-UND** | 5 / 5 |
| L-VAR | hold | **P-VAR** | 4 |
| L-VAR | miss | **P-VAR-WEAK** | 4 |

**98 routed, 0 gap, 0 overlap, all five named outcomes reachable. PASS.** With RN-7 (VOID →
INDET) every void configuration also lands inside this table. **A result fitting no
registered branch is therefore impossible in this leg** — if one appears it is itself a
reportable defect.

Registered consequences, restated verbatim in substance:

- **P-VAR** — the estimand is CONFIRMED as the registered form; **T4 CLOSES as
  T4-reader-amplified-variance: `field ≈ λ·r^q − κ·V_person`** (q ≈ 1.85 [1.71, 2.00],
  κ ≈ 0.722), reader-borne in substance, species-blind. Next registration: the constructive
  repair test (de-framing vs κ and λ).
- **P-VAR-WEAK** — DM nulls without the quantitative law; H-VAR survives qualitatively, the
  coefficient form does not; re-estimate before closure (one more leg).
- **P-SPEC** — species-specific reader; occasion-bound content is intrinsically expensive
  beyond (r, V); T4 closes in the composition form; the repair design becomes
  interaction-specific.
- **P-NEG** — fits neither; both accounts wrong as stated; modeling leg next; no closure.
- **P-UND** — escalation already spent → report resolution attained; the DM question
  carries to a 64-world K2e′ only if the user asks.

### 0.6 G0e — anchors, bit-exact from persisted artifacts (round-trip parsed)

**Every anchor re-derives with residual exactly 0.0.**

| anchor | value | residual |
|---|---|---|
| K2d `FR-45` D | `−0.009879385607257792` CI `[−0.015395490382080454, −0.004577741752997643]` → cell `SUB-SIG(-)` | 0.0 / 0.0 / 0.0, cell match |
| K2d `SP-68` D | `+0.030350909608369947` CI `[+0.02348894741478388, +0.03692045553170193]` → `MAT-SIG(+)` | 0.0 / 0.0 / 0.0, cell match |
| K2d `SP-56` D | `+0.027060778175001646` CI `[+0.020297134101083764, +0.03382765210646028]` → `MAT-SIG(+)` | 0.0 / 0.0 / 0.0, cell match |
| K2d q-update (19 arms) | `1.8528700746510731` CI `[1.7147417060355998, 1.999586491101811]`, R² `0.8679753334914586` | 0.0 / 0.0 / 0.0 |
| κ̂ (6-pair OLS through origin) | `−0.7220359963712748` | 0.0 (and equals the script constant) |
| κ̂'s R² vs mean | `0.9935185860651237` | 0.0 |
| κ̂'s max abs residual | `0.002518007987644547` | 0.0 |
| all six fitted `person_var_a`/`person_var_b`/`Δvar` columns | re-derived from each leg's own `part0_arms.json` shares through `k2b.arm_shares` | **bit-exact 6/6** |
| K2c `P1`/`P2`/`P3` D | `−0.0033349254353831808` / `−0.012167516605861444` / `−0.01355928388620139`, all six CI endpoints | 0.0 |
| K2c pooled q (13 arms) | `1.9337620539521978` CI `[1.7337263621727161, 2.1932591297891246]` | 0.0 |
| λ | `0.17417497661611914` | 0.0 |
| K2b `A1` / `A4` field recovery | `0.177888649457317` / `0.07543949574114414` | 0.0 |

The `k2d.install_species_weights` dispatcher re-verified on this leg's own share grid:
post-patch `"zero"` bit-exact vs the original (**True**), the `"int:0.0"` route equals
`"zero"` bit-exactly (**True**), `"int:(1−s)/3"` reproduces `"equal"` to
**2.7755575615628914e-17**.

Panel (K1-pinned, unchanged): **985 authors**, m-multiset {8: 272, 12: 200, 16: 513},
4 contexts (`AskReddit`, `AskWomen`, `politics`, `worldnews`), **565 retained**,
12 784 events.

### 0.7 G2e — power on the 4-WORLD pilot (RN-4)

| pair | pilot paired sd (3 df) | MDE target | MDE @32 | MDE @64 | selected n | escalated | short at max |
|---|---|---|---|---|---|---|---|
| `DM-68` | `0.013859298475125471` | 0.010 | **`0.007087568013460388`** | `0.004929933426377166` | **32** | False | False |
| `DM-56` | `0.012906498291869087` | 0.010 | **`0.006600311308931841`** | `0.004591009960624228` | **32** | False | False |
| `VS-62` | `0.014316905602352171` | 0.010 | **`0.007321585748447807`** | `0.005092710256439116` | **32** | False | False |

**No pair escalates; all three meet the registered MDE ≤ 0.010 at n = 32.**

**Disclosure, not a gate (RN-4).** Under the χ²-90% one-sided inflation at 3 df
(factor **2.265765949425734**) the MDEs at n=32 would be `0.016058770269137542` /
`0.014954760619387362` / `0.016588999684633766` — **all three would escalate, and all three
would still be short at n=64**. That is the conservative upper bound on σ from a 3-df
estimate, not an estimate of σ; the registration's gate is the plain 4-world MDE and that
is what is applied. **Stated here in advance so that, if the realized sd again exceeds the
pilot's, the reader can see the shortfall was disclosed before the arms ran and not
discovered afterwards.** For scale: the same inflation at 1 df is **7.957896561090547**,
which is precisely the size of K2d's observed 2-world underestimate (2.05×–7.83×).

Pilot paired differences (4 worlds; part of the registered power computation, hence
hypothesis-adjacent and disclosed here rather than later):
`DM-68` `[+0.008823, −0.010230, +0.017914, +0.020275]` (mean **+0.00919572**);
`DM-56` `[+0.039725, +0.018757, +0.017907, +0.009370]` (mean **+0.02143969**);
`VS-62` `[−0.032606, −0.025309, −0.002216, −0.007848]` (mean **−0.01699…**).

### 0.8 G4e — liveness (rules 3 + 10)

| pair | panel RMS a vs b | realized int a | realized int b | realized V_person a | realized V_person b | ΔV realized | pilot field a | pilot field b |
|---|---|---|---|---|---|---|---|---|
| `DM-68` | `0.03830234445970283` | **0.0** | **`0.025655135232831427`** | `0.08783292657045505` | `0.08772244275874794` | **`+0.00011048381170711274`** | `0.11535691579673385` | `0.10616119807506672` |
| `DM-56` | `0.04993085684825631` | **0.0** | **`0.04365499567195155`** | `0.14926946507061198` | `0.14909428682542886` | **`+0.00017517824518312186`** | `0.09200893306847056` | `0.07056924370936048` |
| `VS-62` | `0.030393418153440023` | 0.0 | 0.0 | `0.11932046600449671` | `0.10187741344074197` | `+0.017443052563754738` (by design) | `0.09728643913924492` | `0.11428139641936054` |

The interaction channel is **live in both DM-b arms** and **exactly 0.0** in the four
`w_int = 0` arms. Within-pair panels differ (RMS ≫ 1e-6). Across the three designed levels
(.56 < .62 < .68) pilot card attenuation runs **0.56287 < 0.62263 < 0.68196** and pilot
field recovery **0.08129 < 0.10578 < 0.11076** — both strictly increasing, per prediction.
Max |realized − design| variance share **0.0038281832228469204** (≤ 0.01). Frame-channel
centred residual **1.1657341758564144e-15**. New realized-share route vs `k2b`'s verify
route: residual **0.0**. **No GAP clause gates anything.**

The DM pairs' realized ΔV_person are **45× and 29× inside** the ±0.005 post-arms margin
already at pilot scale — the double match survives contact with actual emitted panels, not
just the algebra.

### 0.9 G3e — rule-11 satisfiability with directions, and the rule-13 spec

`B = 2000`, seed = master (20260819); rule-13 stability re-checked at `B = 20000` whenever a
gated clause boundary lies within 2 Monte-Carlo sd of the estimate.

Projected (conservative, unpaired) within-pair attenuation half-widths **0.00176666 /
0.00215555 / 0.00195215** against ±0.005 — satisfiable. Projected `1.96·se(D)` **0.00480200
(DM-68) / 0.00447187 (DM-56) / 0.00496055 (VS-62)**:

- **MAT-SIG** needs `1.96·se < M1 − M2 = 0.010` → satisfiable on all three.
- **NULL** needs `1.96·se < M2 = 0.010` → satisfiable on all three. **This is the clause
  L-VAR needs, so it is the leg's binding satisfiability requirement, and it is met** — an
  H-VAR null is reachable, i.e. the leg can actually return its .60-prior lean.
- **WEAK-NULL / SUB-SIG / INDET** reachable by construction (layer-1 partition).
- **L-SPEC** is one-sided *in content* (under H-SPECIES the int-carrying b arm is worse, so
  the species signature is **positive D**) and scored on the two-sided CI as registered.
- **L-VS**: projected `1.96·se(D_VS) = 0.00496055` against the ±0.010 tolerance; both HOLD
  and MISS reachable. **Informativeness, disclosed:** the ratio `1.96·se / tol = 0.4961`, so
  the CI is about half the tolerance — neither clause is vacuous and the containment clause
  is the sharper of the two.
- **GAP**: no clause. **q-update**: descriptive, no gate.

All 13 registered clauses satisfiable with a stated direction.

### 0.10 G5e — hygiene and the stage budget

Round-trip parsing everywhere (`float_precision='round_trip'`); foreground chunked stages
(`part0`, `arms --worlds a-b`, `finalize`); **0 background jobs, 0 monitors**. Mean world
build **0.01913 s**; per-arm-world **0.68678 s**; **192 arm-worlds** → arms-stage estimate
**133.086 s**, **stop-and-report threshold 266.172 s**. Recommended chunk 16 worlds.

**Part 0 all pass: G0e ✓ G1e ✓ G2e ✓ G3e ✓ G4e ✓ G5e ✓ + rule-16 layers 1/2/3 ✓.**

---

## Results — executed 2026-08-09, finalize written 2026-08-09T10:36:00.992525+00:00 (UTC)

**VERDICT:
`DM68_SUBSIG_POS__DM56_SUBSIG_POS__L_SPEC__LVS_HOLD__MATCH_EXACT__P_SPEC`**

**Both double-matched pairs return a POSITIVE, significant, SUB-MATERIAL D. L-SPEC fires
(prior .30, against L-VAR's .60). L-VS HOLDS under both registered readings. Routing:
(L-SPEC, any) → P-SPEC. 0 pairs VOID; rule 13 clean.**

The leg's two halves point in different directions and both are informative:

1. **H-VAR is refuted as a COMPLETE account.** With predicted attenuation matched to 0.0
   and total person variance matched to ≤1.4e-17 in the design and ≤9.3e-05 in the emitted
   panels, `D` is not zero: **+0.006424 [+0.000695, +0.012065]** at r = .68 and
   **+0.008918 [+0.002382, +0.015253]** at r = .56, both CIs excluding 0, in the direction
   the species hypothesis predicts. The registration's own solvability argument states the
   consequence in advance: *"if D ≠ 0, something beyond (r, V_person) matters and H-VAR is
   dead regardless of which ingredient carries it."*
2. **But the κ coefficient is RIGHT where it applies.** On the pure-variance axis the
   registered point prediction lands: `D_VS` measured **−0.010598 [−0.015214, −0.005701]**
   against the Part-0 registered **−0.012450**; the CI contains it and
   `|D − pred| = 0.001851 ≤ 0.010`. Both clauses, both currencies.

So the reader *does* tax raw person variance at ≈0.72 per unit — and *additionally* pays a
species surcharge that the variance law scores at exactly zero.

### 1.1 G1e post-arms — the DOUBLE match survived, 0 VOID

| pair | measured r(a) | measured r(b) | Δr | Δr 95% CI | inside ±0.005 | realized V_person(a) | realized V_person(b) | ΔV_person | inside ±0.005 |
|---|---|---|---|---|---|---|---|---|---|
| `DM-68` | `0.6798544664841454` | `0.6800294041192296` | `−0.0001749376350842491` | `[−0.0005411014896656907, +0.00018526562015489794]` | **True** (9.24× tighter) | `0.08781700762249339` | `0.08775808258497561` | **`+5.892503751778579e-05`** | **True** (84.9× tighter) |
| `DM-56` | `0.5598271826369814` | `0.560108078123301` | `−0.00028089548631959893` | `[−0.0008237012933283633, +0.00023652116090917252]` | **True** (6.07×) | `0.149257883350746` | `0.14916443729016027` | **`+9.344606058571577e-05`** | **True** (53.5×) |
| `VS-62` | `0.619838045803416` | `0.6200797805020005` | `−0.00024173469858457253` | `[−0.0006773900204662175, +0.0001789132334958615]` | **True** (7.38×) | `0.1193051791237513` | `0.10197391473094536` | `+0.017331264392805933` (maximized by design; clause N/A per RN-3) | — |

**0 pairs VOID.** The two invariants the law depends on are equalized in the *measured*
panels, not merely in the algebra — which is what licenses reading `D ≠ 0` as evidence
about something else. Realized V_person differences are 53–85× inside their margin; realized
attenuation differences 6–9× inside theirs.

Card positive control (no gate anywhere in this leg): measured attenuation contains its
Part-0 prediction **6/6**, max relative error **0.031%**. **GAP also contains its prediction
6/6** (max relative error 4.47%) — corroborating the Part-0 boundary note that this leg's
solved `w_int` shares sit *inside* K2a's validated range, unlike K2d's, which is where A-2's
misses came from. GAP still gates nothing.

### 1.2 D per pair, the assigned CELL, and the realized power

| pair | D | 95% CI (paired world-block bootstrap, B=2000) | CELL | \|D\| as % of level | worlds with D>0 | realized paired sd | realized MDE | pilot underestimate |
|---|---|---|---|---|---|---|---|---|
| `DM-68` | **`+0.006424123811148958`** | `[+0.000695362260562535, +0.012064857982504633]` | **SUB-SIG(+)** | 5.191% | 21/32 | `0.016964470110389283` | `0.008675535485111296` | **1.224×** |
| `DM-56` | **`+0.008917886817207595`** | `[+0.002382409106492113, +0.015253364806094327]` | **SUB-SIG(+)** | 10.109% | 22/32 | `0.01836237173776747` | `0.009390414587971527` | **1.423×** |
| `VS-62` | **`−0.010598278269700216`** | `[−0.015213711891300446, −0.005701069068586025]` | SUB-SIG(−) | 9.253% | 6/32 positive | `0.013863240970850356` | `0.007089584183805738` | **0.968×** |

Paired-t CIs agree on every sign: `[+0.000308, +0.012540]`, `[+0.002298, +0.015538]`,
`[−0.015597, −0.005600]`.

**RN-4 is vindicated.** The 4-world pilot underestimated the realized paired sd by
**1.22× / 1.42× / 0.97×** — against K2d's **2.05×–7.83×** on 2-world pilots. **All three
realized MDEs (0.008676 / 0.009390 / 0.007090) meet the registered 0.010 target**, so
unlike K2d there is **no post-hoc power shortfall and no tiered claim**. The planner's new
pilot convention did exactly what it was added to do.

**Honesty note on effect size vs power (disclosed, no branch consequence).** Both DM
effects sit *below* their own realized MDE (`|D|/MDE` = **0.74** and **0.95**) while their
CIs exclude 0: they are detected at this realization but at the edge of the design's
80%-power envelope, and both are **sub-material at both margins** (|D| < M1 = 0.020;
lower(|D|) = 0.000695 / 0.002382 < M2 = 0.010). The species surcharge is real and small.
`D_VS`, by contrast, is **1.49×** its realized MDE.

### 1.3 The lean, with the rule-16 enumeration check stated

Cells `(DM-68, DM-56) = (SUB-SIG(+), SUB-SIG(+))`; neither pair VOID, so no RN-7
substitution applied. **Exactly one registered predicate fires: L-SPEC** — ≥1 DM in
{MAT-SIG(+), SUB-SIG(+)} and no DM in a negative-sign cell. `n_predicates_true = 1`, so the
registered precedence (L-NEG > L-SPEC) never had to be invoked.

**Enumeration check, as rule 16 requires it be stated:** the four predicates were verified
in Part 0 — *before any hypothesis number existed* — to **partition all 7 × 7 = 49 ordered
DM-cell pairs**: 49/49 unique, **0 overlap, 0 gap**, checked *before* precedence is applied
so that precedence could not mask an overlap; the registration's own gloss
("L-UND ⟺ ≥1 INDET and no significant cell") was evaluated as an independent predicate and
agreed on **all 49**; all four leans realized (L-NEG 24, L-SPEC 16, L-UND 5, L-VAR 4). The
routing layer covers all **98** (cell-pair, L-VS) combinations with **0 gaps and 0
overlaps** and every one of the five named outcomes reachable. **Rule 16's first full
application is clean — the first K-leg whose adjudication object contained no defect at any
level.** Consequently no result could have fitted "no registered branch", and none did.

### 1.4 L-VS — the registered quantitative test of the estimand

| reading | predicted D_VS | measured D_VS | CI contains pred | \|D − pred\| | ≤ 0.010 | HOLDS |
|---|---|---|---|---|---|---|
| **DESIGN (PRIMARY, RN-1)** | `−0.012449509445450275` | `−0.010598278269700216` | **True** | **`0.0018512311757500587`** | **True** | **True** |
| pilot-realized (SECONDARY) | `−0.012594511837627172` | `−0.010598278269700216` | **True** | `0.0019962335679269555` | **True** | **True** |

Both readings agree. For the record the *arms*-realized ΔV_person is
`0.017331264392805933` (design `0.017242228237951546`, pilot `0.017443052563754738`) — the
three currencies span 0.0002 in ΔV, i.e. 0.00014 in the prediction.

**L-VS HOLDS (prior .70).** The κ ≈ 0.722 coefficient, fitted post-hoc on six pairs in K2d,
made a genuine out-of-sample point prediction on a fresh pair and hit it to
**0.0019 (14.9% of the prediction, 39% of the CI half-width)**.

### 1.5 ROUTING — P-SPEC fires

`(L-SPEC, L-VS hold) → **P-SPEC**`, and by the registered table L-SPEC routes to P-SPEC
under *either* L-VS state, so the outcome is robust to the L-VS clause. Registered
consequence, verbatim in substance: **species-specific reader — occasion-bound content is
intrinsically expensive beyond (r, V); T4 closes in the composition form; the repair design
becomes interaction-specific.**

Two qualifications this executor is obliged to attach, neither of which changes the
routing:

- **The registration itself pre-empted the carrier question.** The DM-b arms differ from
  their a-arms in *two* ingredients — species (interaction for slow) and φ (.98 for .90) —
  and the registration states that the φ shift "is part of the recombination and is benign
  under BOTH hypotheses given the two matches". So P-SPEC is the registered reading of
  `D ≠ 0`; the leg does **not** separate "species" from "φ" as the carrier.
- **A descriptive triangulation that bears on it** (no gate, no branch weight): `VS-62` is a
  *pure φ contrast* at ΔV > 0, and its residual from the κ law is only **+0.001851**, while
  the DM residuals — which are their whole D, since ΔV = 0 there — are **+0.006424** and
  **+0.008918**, i.e. **3.5× and 4.8×** the φ-only residual. Under the κ law, the φ axis is
  almost fully accounted for by ΔV; the unexplained part scales with the interaction share.
  That points at the species ingredient, but it is a 3-pair descriptive, not a test.

### 1.6 How much of K2d's species finding was ΔV_person in disguise

This is the number K2e was built to produce:

| level | K2d species D (ΔV unmatched) | K2e species D (ΔV matched) | share of K2d's effect that was raw variance |
|---|---|---|---|
| r ≈ .68 | `+0.030350909608369947` | `+0.006424123811148958` | **78.83%** |
| r ≈ .56 | `+0.027060778175001646` | `+0.008917886817207595` | **67.04%** |

So K2d's headline ("occasion-bound content costs 2.0–2.5× persistent content") was
**two-thirds to four-fifths an accounting artefact of unmatched person variance** — exactly
the confound K2d's own brief flagged — and **one-fifth to one-third a genuine species term**
that survives double matching. The genuine remainder is significant but **sub-material at
both registered margins**: the material composition finding of K2d does **not** survive at
matched V_person.

### 1.7 Δmixed (descriptive, no gate)

| pair | Δmixed | 95% CI | excludes 0 | ratio to \|D\| |
|---|---|---|---|---|
| `DM-68` | `+0.022363025673266007` | `[+0.015616157515529062, +0.02866212562482846]` | True | **3.48×** |
| `DM-56` | `+0.04316489195301383` | `[+0.03361772648687074, +0.05183505234229541]` | True | **4.84×** |
| `VS-62` | `+0.041970037252073336` | `[+0.03617508746956292, +0.047578041377977096]` | True | **3.96×** |

All three positive with CIs excluding 0 — including the two DOUBLE-MATCHED pairs, where the
trait channel's D is at the edge of detectability. K2d found the mixture "trade" to be a
property of the persistence axis and *absent* on its species pairs (SP-68 Δmixed CI included
0). Here it is present and loud on **both** double-matched pairs. Reading (flagged as
reading): once total person variance is held fixed, the two arms differ in what the reader
*assigns* far more than in what it *loses* — the mixture channel is where the species
difference is legible, at 3.5–4.8× the amplitude of the trait channel. Card-side ledger:
within-pair GAP ratios **4.669 / 4.696 / 3.993** (K2c's series ran 4.04/4.08/3.98; K2d's
species pairs ran 1.79/1.75 — the DM pairs look like *persistence* pairs to the card, which
is what a φ-carrying recombination should look like).

### 1.8 q-update (descriptive, no gate) and the κ re-fit

**q over 25 arms = `1.8327227969464843`, CI `[1.7109560851209855, 1.9795061744015678]`**,
R² `0.854621603166378`, one-sided 5th pct `1.7311635750465104`, λ-invariance residual
`4.440892098500626e-16`, shift vs K2d's 19-arm value **`−0.020147277704588795`**. The
quadratic reading survives its fourth extension; the CI's upper end has now dipped just
below 2.0 for the first time.

**κ re-fit over 9 pairs (declared descriptive in Part 0, RN-10):**
`κ = −0.7145934082034173` (K2d's 6-pair value `−0.7220359963712748`, shift `+0.00744`),
R² vs mean **0.939492050214398** (was 0.9935), max |residual| **0.008917886817207595** (was
0.00252). The degradation is entirely the two DM pairs: they sit at Δvar = 0, carry no
leverage on an origin-forced slope, and their residual *is* their D. Per-pair κ on the seven
pairs with nonzero Δvar now spans **[−0.837, −0.509]** with VS-62 at **−0.6146698746495273**.

### 1.9 Rule 13

**0 clauses triggered, 0 BOUNDARY.** Closest approaches (post-hoc descriptive):
**4.03 MC-sd** (DM-68 — the `c1 CI excludes 0` clause, the leg's tightest), 12.30 (DM-56),
18.97 (VS-62). The G1e attenuation clauses and the L-VS containment clause were all far
from their boundaries.

### 1.10 Rule 14, verified on this leg's own gates

G0e re-derives K2b/K2c/K2d numbers against themselves; G1e is card-vs-card and
share-vs-share; G2e/G4e, every cell, and L-VAR/L-SPEC/L-NEG/L-UND are field-vs-field
within-pair. **L-VS is cross-scale and legal under rule 14's first clause** — the
registration pins the link and its coefficient. The q-update and the κ re-fit are declared
descriptive with no gate.

### 1.11 Compute and hygiene

6 arms × **32 worlds** (no escalation), `master_seed 20260819`, salt `m4k2e-world`,
K1-pinned panel (985 authors, 565 retained, 4 resolved contexts), card channel 18 080 pooled
authors/arm, **192 adjudicated deployed-gauge world runs** + 24 reserved-pilot runs (worlds
9901–9904). **Total compute 142.548 s** — part0 **17.307**, arms **56.527 + 56.697 =
113.224** against a Part-0 estimate of **133.086** (2× stop threshold **266.172**),
finalize **12.017**. Foreground chunked stages, **0 background jobs, 0 monitors, 0 crashes,
0 re-runs, no stage over its Part-0 estimate**. Python 3.14.3, numpy 2.4.4, pandas 3.0.2.

### 1.12 Anomalies (with timing)

- **A-1 (pre-Part-0, before any world or field number existed; resolved before Part 0 was
  written).** This executor ran a pure card-algebra check of the registration's closed form
  — κ(.90)/κ(.98)/κ_int and the two matching residuals — to validate the derivation before
  writing ~1 100 lines of script. No world was built, no field number produced, and every
  number is re-derived identically inside `--stage part0` and written to disk. Disclosed for
  completeness; **impact: none**.
- **A-2 (Part 0, before any hypothesis number).** The registration asserts that this leg's
  `w_int` "exceeds K2a's validated range". Measured, it does not: solved interaction signal
  fractions `0.0858`/`0.1458` against K2a's equal-share ceilings `0.2644`/`0.2161`. The
  registration's instruction (no GAP-based gate) was obeyed regardless, and the disclosure
  is corroborated after the fact — **GAP contained its prediction 6/6**, where K2d's two
  large-`w_int` arms had missed. **Impact: none** (nothing was gated on GAP either way).
- **A-3 (Part 0, before any hypothesis number).** The χ²-90% df-inflated reading of the
  4-world pilot would have escalated all three pairs to 64 worlds and still declared them
  short. It is a conservative upper bound on σ from a 3-df estimate, not an estimate of σ;
  the registered gate is the plain 4-world MDE. Disclosed **in Part 0, before the arms ran**
  — and the realized sds then came in at 0.97×–1.42× of the pilot's, so the plain reading
  was right and every realized MDE met the target. **Impact: none.**
- **A-4 (Part 0, continuity, not a defect).** `DM68a`/`DM56a` solve to shares bit-identical
  to K2c's `P2a`/`P3a` and K2d's `SP68slow`/`SP56slow`.
- **A-5 (Part 0, provenance).** Corpus tags read `m4k2b-K2E-<arm>-w<k>` because
  `k2b.run_field_world` is unmodified; hash labels only, disjoint from K2b/K2c/K2d.
- **A-6 (finalize, after the numbers existed).** Both DM effects are significant yet below
  their own realized MDE (0.74× and 0.95×). Disclosed in §1.2; no repair attempted, and
  none is available that would not be a post-hoc design change. It is the reason the
  species remainder is reported as **sub-material and replication-fragile** rather than as a
  settled magnitude.

### 1.13 Brief to the planner

1. **P-SPEC fires, but the finding it carries is the OPPOSITE in size to K2d's.** The
   material species term of K2d shrinks by 67–79% under double matching and lands
   **sub-material at both margins**. The honest one-line summary is: *the reader taxes raw
   person variance at κ ≈ 0.72 (now confirmed out-of-sample), and pays a small additional
   surcharge on occasion-bound content that is significant but below materiality.*
2. **The candidate law is nearly right, and its error has a shape.** `field ≈ λ·r^q −
   κ·V_person` predicted VS-62 to 0.0019 and predicts the DM pairs to be null; they are
   +0.0064 and +0.0089. The residual grows with the interaction share (0.0257 → 0.0437
   variance share gives 0.0064 → 0.0089), which is a *linear-in-w_int* surcharge of slope
   ≈ 0.14 — descriptively, `field ≈ λ·r^q − κ·V_person − c·V_int` with c small. That is a
   one-parameter extension, testable on the same machinery, and this executor did not
   register it.
3. **The carrier is still not isolated.** Species and φ move together in the DM-b arms by
   the registration's own construction. The clean follow-up is a same-φ double match, which
   requires a third state species (or a φ-graded slow channel) to satisfy both constraints
   at fixed φ — currently inexpressible on this instrument.
4. **Rule 16 worked, and cost nothing.** First K-leg with a defect-free adjudication object
   at every level; the Part-0 enumeration took milliseconds and the "fits no registered
   branch" failure mode was structurally impossible.
5. **The 4-world pilot convention should be made standing.** 1.22×/1.42×/0.97× realized-sd
   ratios against K2d's 2.05×–7.83×, for 8 seconds of compute.
