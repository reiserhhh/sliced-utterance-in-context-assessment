# SUICA M4-K1d — Does the author-axis law survive author deletion? (the F4 re-reading)

Tier: **EXPLORATORY, label-free, synthetic.** Registered in
`docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md`, section "M4-K1d — Does the author-axis
law survive author deletion? (the F4 re-reading)" (REGISTERED 2026-08-09,
BEFORE RUN, commit `234a4d1`). Theory under test:
`docs/SUICA_IDENTITY_THEORY_V1.md` dated appendices E (the world-family lemma)
and F (author content is interference; F.5 states exactly what this leg
decides). Ledger row `M4-K1d`. Script:
`scripts/run_suica_m4_k1d_replicate_axis.py`. Artifacts:
`results/m4_k1d_replicate_axis/`.

Executor's standing: implementation and execution only. The registration text
is binding; everything below labelled "register-note" is an operationalization
of something the registration left as an implementation choice, or a standing
rule 9 instrument resolution, fixed and written here **before** any main arm
stage ran.

---

## 0. Part 0 — gates and register-notes, written before any main arm

**Part-0 gates computed 2026-08-09 (stage `part0`, wall-time 94.430 s),
persisted in `results/m4_k1d_replicate_axis/gates.json` with
`timestamp_utc = 2026-08-09T06:54:52.670247+00:00`. This section was written to
disk before any main arm stage was invoked.** The only compute that has touched
the deployed gauge at this point is the registered Part-0 pilot — reserved
worlds **9401–9402**, 2 cells (×1, ×16) × 2 arms × 2 worlds = **8 gauge runs** —
whose seeds are disjoint from the 8 main worlds (indices 0–7) and are never
adjudicated. **No smoke run of any kind preceded it**; `part0` was invoked
exactly once.

**All five Part-0 gates PASS: `part0_all_pass = true`. P3d does not fire.**

### G0d — pin F4's cells, dims and fitter; re-verify the cited numbers

**Grid pinned** from F4's own constructors (`f4().AUTHOR_MULTS`,
`f4().seed_suffix_for_mult`, `f4().HOLDOUT_AUTHOR_MULT`, `f4().DESIGN`):
**{×1, ×2, ×4, ×8, ×16}** at κ = 1.0, shared design, cells
`base1x_shared_k10`, `authors_x{2,4,8,16}_shared_k10`, holdout
`authors_x32_holdout_shared_k10`.

**Fitter pinned** — no new fitter is written in this leg:
`f1().fit_axis` (`scripts/run_suica_m4_f1_panel_sizing.py:807-865`) — WLS of
log₁₀-odds on log₁₀(mult), delta-method weights at f1:826-841, qualifying rule
`mean > 0 and mean − 2·se > 0`; and `f1().bootstrap_axis` (f1:869-908), 2000
resamples. Engine pinned: `f3().run_sweep_world`
(`scripts/run_suica_m4_f3_composition_scaling.py:261`), seeds via
`f3().world_seed_for` (f3:202, salt `m4f3-world`).

Every cited F4 number is **re-derived from `results/m4_f4_author_axis/`'s raw
per-cell CSVs through F4's own fitter** — never read off a summary — and then
checked against both the persisted `decision.json` and the registration text.

| anchor | re-derived on **F4's own code path** | == persisted == registration |
|---|---|---|
| γ (authors, shared, κ=1.0, ×1..×16) | **1.0959430140456936** | ✔ |
| γ bootstrap CI95 | **[0.9843434774823611, 1.2176831424523908]** | ✔ |
| ×32 holdout predicted agreement | **0.4012353096433611** | ✔ |
| ×32 holdout observed agreement | **0.38612436657934157** | ✔ |
| intercept / status / n_qualifying | −1.823415640598357 / FITTED / 5 | ✔ |
| master_seed / worlds / draws | 20260802 / 8 / 20 | ✔ |

**All five cited numbers reproduce BIT-EXACTLY. G0d PASS.**

**Register-note R-0.1 (rule 9 — two parser readings, both reported; a
correction to the standing round-trip convention's reach).** This line's
standing convention (adopted 2026-08-09 from K1c′'s anomaly 1) is that every
artifact re-derivation passing through a CSV parse uses
`float_precision="round_trip"`. Applied here it **does not** reproduce F4's
published numbers bit-exactly, and the reason is instructive: F4 computed its
own summaries by reading its own freshly written CSVs with pandas' **default**
parser, so F4's published values are the default-parser images of its true
in-memory float64s. Both readings are therefore reported:

| quantity | F4's own path (default parser) | round-trip parsing |
|---|---|---|
| γ | 1.0959430140456936 | 1.0959430140456938 |
| γ CI95 | [0.9843434774823611, 1.2176831424523908] | [0.9843434774823602, 1.2176831424523904] |
| ×32 predicted | 0.4012353096433611 | 0.40123530964336135 |
| ×32 observed | 0.38612436657934157 | 0.3861243665793416 |
| WRMSE (R-0.2) | 0.056254146729854085 | 0.05625414672985413 |

Maximum relative deviation between the two readings: **9.023053842666835e-16**
(≤ 2 ULP). **Written rule for this leg:** the *bit-exactness* claim of G0d is
adjudicated on F4's own code path (the only path that can reproduce numbers
F4 actually computed); the round-trip reading is reported alongside as the
faithful reconstruction of F4's true in-memory quantities, and
`float_precision="round_trip"` governs **all K1d-own artifacts** without
exception, so this leg's own numbers are exactly reproducible from its own
CSVs. Program note: the round-trip convention is correct going forward but
**cannot retroactively reproduce a legacy number computed under the default
parser** — the two are not interchangeable, and a future gate that demands
"bit-exact" against a pre-convention artifact must say which parser it means.

**Panel dims pinned (rule 5), from the persisted cells:**

| cell | authors/world | retained by the gauge | events/world | F4 s/world |
|---|---|---|---|---|
| ×1 | 985 | 565 | 13,202 | 8.438 |
| ×2 | 1,970 | 1,130 | 26,404 | 16.817 |
| ×4 | 3,940 | 2,260 | 52,808 | 32.894 |
| ×8 | 7,880 | 4,520 | 105,616 | 66.370 |
| ×16 | 15,760 | 9,040 | 211,232 | 132.574 |
| ×32 (holdout) | 31,520 | 18,080 | 422,464 | 267.644 |

Knobs `k48-r0.50-mu0.15-x0.15-e0.70-p0.20_0.80`, read from F1's
`calibration_record.json` (status CALIBRATED).

### G2d — rule 10: non-degeneracy of the deletion, per cell

Reserved fresh worlds 9401–9402, this leg's own seed lineage
(`k1d_*`, MASTER_SEED 20260814). The deleted arm's panel is the intact panel
minus `mean_part` broadcast over each author's events, so the elementwise
difference panel **is** `mean_part` and its RMS is exact and closed-form.

| cell | panel Δ RMS (bar > 1e-6), w9401 / w9402 | panel Δ max-abs, w9401 |
|---|---|---|
| ×1 | 0.06825177531394482 / 0.06838550847726373 | 0.37624883414083443 |
| ×2 | 0.06847021413977063 / 0.06846079392987091 | 0.30946816814559447 |
| ×4, ×8, ×16 | all in [0.06825177531394482, 0.06860615411231898] | — |

**Minimum over all 10 (cell × world) readings: 0.06825177531394482 against a
1e-6 bar — 4.8 orders of margin. G2d PASS. P3d does not fire.**

**Extraction bit-exactness.** This script's memory-bounded
`author_mean_part` (which replays only f2:151/164/165/167/168/178) is verified
**bit-identical** to the canonical surgery object
`k1b.channels(...)["mean_part"]` — the line-for-line mirror of f2:151-197 used
by K1b's A1′/A3′ and K1c′'s A5/A6:

| cell | shape | max-abs difference vs `k1b.channels` |
|---|---|---|
| ×1 (world seed 1112890606816365508) | (985, 64) | **0.0** |
| ×2 (world seed 7159334142205293242) | (1970, 64) | **0.0** |

### G3d — power (rule 2) and rule 11 satisfiability

Registered pilot: 2 reserved worlds × the smallest and largest grid cells ×
both arms = 8 gauge runs (93.4 s wall at 8 workers).

| world | γ₂ intact | γ₂ deleted | Δγ₂ | level ×1 | level ×16 |
|---|---|---|---|---|---|
| 9401 | 1.1498967351369496 | 1.2271801943162888 | +0.07728345917933921 | +0.011425173833025524 | +0.18286276897432469 |
| 9402 | 1.130517411515308 | 1.0172794455006688 | −0.1132379660146392 | +0.025319240757148604 | +0.1838969152564562 |

**Register-note R-0.3 (rule 9, instrument convention, fixed before any main
arm).** The pilot has only two grid points, so the fitted 5-point exponent
cannot be formed from it. The pilot statistic is the **2-point log-odds slope**
γ₂ = [L(A₁₆) − L(A₁)] / log₁₀(16), with L = `f1()._log_odds` (the identical
transform F4's own fitter regresses in), computed **per world per arm**;
Δγ₂ per world is the paired quantity. This is a *conservative* proxy for the
registered 5-point fit — it averages nothing over the interior of the grid —
and the projection to the main design is hw = t₀.₉₇₅,₇ · sd/√8 (t = 2.3646).

| projected quantity | pilot sd | projected half-width at n = 8 |
|---|---|---|
| Δγ₂ | 0.13471899171598767 | **0.11262789561542542** |
| γ₂ intact | 0.013703251147671363 | 0.011456204653799611 |
| γ₂ deleted | 0.14842224286365904 | 0.12408410026922505 |
| level contrast ×1 | 0.009824588940307147 | 0.008213561900508648 |
| level contrast ×16 | 0.0007312518488340587 | 0.0006113418446056799 |

**The registered ±0.25 equivalence band is satisfiable: the projected Δγ
half-width 0.11262789561542542 is 0.45× the band.** Band justification, as
registered: F4's own bootstrap CI half-width is
(1.2176831424523908 − 0.9843434774823611)/2 = **0.11666983248501485**, so
±0.25 is 2.143× it.

**Rule 11 — every registered CI clause checked for satisfiability, with its
direction stated explicitly (defect #15's lesson):**

| clause | direction | satisfiable |
|---|---|---|
| L-1a: \|Δγ\| CI inside ±0.25 | **two-sided EQUIVALENCE band** — correct form; an equivalence clause is two-sided by construction, unlike the sd clause that produced defect #15 | ✔ (hw 0.1126 < 0.25) |
| L-1b: γ_deleted CI overlaps [0.984, 1.218] | **two-sided OVERLAP** (non-disjointness); its negation is P2d's DISJOINT case | ✔ |
| G1d: γ_intact CI overlaps [0.984, 1.218] | **two-sided OVERLAP** | ✔ |
| L-2: per-point level CI **lower edge > 0** | **ONE-SIDED**, stated one-sided on purpose | ✔ (pilot level ×1 0.01837 > hw 0.00821; ×16 0.18338 > hw 0.00061) |
| L-3: WRMSE ratio CI **upper edge ≥ 1** | **ONE-SIDED** — the MISS branch requires the whole CI *below* 1 | ✔ structurally (5 points, 3 residual dof; the 2-point pilot has 0 residual dof and cannot bound a WRMSE) |

**All five clauses satisfiable. G3d PASS.**

### G4d — rule 3: the deleted channel is LIVE at this knob

`mean_part`'s share of the response RMS at κ = 1.0, computed from the full
generator at both pilot worlds and both pilot cells:

| cell | world | response RMS | `mean_part` RMS | **share** | deleted-panel RMS |
|---|---|---|---|---|---|
| ×1 | 9401 | 0.17655696701040804 | 0.06825177531394482 | **0.3865708415229027** | 0.16282721995350877 |
| ×1 | 9402 | 0.17634812249446674 | 0.06838550847726373 | **0.38778699489363405** | 0.16224287873988058 |
| ×16 | 9401 | 0.17671623700885872 | 0.06844039336595353 | **0.38728978459700136** | 0.1629308721962074 |
| ×16 | 9402 | 0.17730927424831652 | 0.06849479328010771 | **0.3863012443679778** | 0.16357635501368314 |

**Share ∈ [0.3863012443679778, 0.38778699489363405] > 0 at every pilot world.
G4d PASS. P3d does not fire.** The deletion removes roughly 38.7 % of the
response's RMS mass; the intact/deleted panel RMS ratio is ≈ 1.084.

### G5d — hygiene, rule 12 (source-object naming), rule 11, rule 5

**Rule-12 header — every channel named by its source object:**

| channel | source object | this leg |
|---|---|---|
| author MEAN | `mean_part = sqrt(w_mu)*a*((z*g) @ loadings.T)` — **f2:178** | **DELETED** by exact pre-map subtraction |
| author AR state | `x`, f2:172-176, entering only through `blended_x` (f2:195) with coefficient `sqrt(1-kappa)` | **coefficient exactly 0 at κ=1.0** (M4-F7) — nothing to delete |
| occasion-common | `shock_x` from `f2().shock_vector` (f2:121-126), fed by `occasion_labels` (f2:180) through f2:184-193, blended f2:195, mapped f2:196 | UNTOUCHED |
| isotropic noise | `sqrt(w_e)*sigma_iso*noise`, f2:177 / f2:197 | UNTOUCHED |
| grid cells | `f4().AUTHOR_MULTS`, `f4().seed_suffix_for_mult`, `f4().HOLDOUT_AUTHOR_MULT`, `f4().DESIGN` | F4's own constructors |
| fitter | `f1().fit_axis` + `f1().bootstrap_axis` | F4's own, unchanged |

**Consequence, stated once:** at κ = 1.0 the deleted arm removes the **entire**
author channel, not a part of it. This is the same surgery K1b's A1′/A3′ and
K1c′'s A5/A6 performed, at K1b's own knob.

Hygiene: master_seed **20260814**, 8 worlds/cell, 20 draws/world, κ = 1.0,
shared design, reserved pilot worlds 9401–9402, `float_precision="round_trip"`
on every K1d artifact, **no background jobs, no monitors, no smoke runs**,
label-free, EXPLORATORY.

Grain (rule 5): **worlds are the bootstrap unit** (8 per cell). The two arms of
a cell are paired *by construction* — identical `seed_key`/`world`/`knob_tag`
gives an identical `world_seed` and an identical corpus tag, so the deleted
panel is the intact panel minus `mean_part` on the same world. Per-point sign
counts are over those same 8 worlds.

**G5d PASS.**

### G-info-F5 — what F5's truth-recovery quantities correlate against (REPORT-ONLY)

No adjudication. Derived from `scripts/run_suica_m4_f5_gauge_validity.py` and
`results/m4_f5_gauge_validity/` (11 swept cells at κ ∈ {0.5, 1.0}).

Both quantities are the **deployed field functional**
`module.field_agreement(field_est_full, field_true_*, weights)` evaluated
between the finite-sample ESTIMATED field (built from the actual noisy panel)
and a **noise-free generator TRUTH field** pushed through the identical
featurize → project → field path:

- **`truth_recovery_exact`** — **f5:494**. Truth object from
  `generate_truth_vectors_exact` (**f5:225-280**):
  `events_true = mean_part + state_part` (**f5:279**), with the comment
  "no + sqrt(w_e)*sigma_iso*noise term". Components: `mean_part` (**f5:260**) =
  AUTHOR content (f2:178's object); `state_part` (**f5:278**) built from
  `blended_x = sqrt(1-kappa)*x + sqrt(kappa)*shock_x` (**f5:277**), where `x` is
  the **author-private AR(1) state** and `shock_x` is the **occasion-common**
  shock from the unchanged `f2().shock_vector` (**f2:121-126**).
- **`truth_recovery_long`** — **f5:505**. Truth object from
  `generate_truth_vectors_long` (**f5:303-372**):
  `events_long = mean_part_chunk + state_part` (**f5:367**), noise-free.
  Components: `mean_part` (**f5:331**, "bit-identical to live's own
  mean_part") = AUTHOR content; `x_long` (**f5:348-352**) = the author-private
  AR(1) state **redrawn** over `t_large` with the same per-author φ (f5:330);
  `shock_long` (**f5:354-362**) = occasion-common content from the **same**
  `f2().shock_vector` on the same world seed (**f5:360**).

**Verdict from source: MIXED — both truth objects are author content PLUS
occasion-common content, with the noise channel excluded.** Quantified from
the F1-calibrated variance shares `w_mu = 0.15`, `w_x = 0.15`, `w_e = 0.70`:

| knob | author-mean share of truth variance | author-AR share | occasion-common share |
|---|---|---|---|
| κ = 1.0 | **0.50** | 0.00 (`sqrt(1-kappa) = 0` exactly at f5:277) | **0.50** |
| κ = 0.5 | **0.50** | **0.25** | 0.25 |

The excluded isotropic noise channel is **70 %** of the *response* variance, so
neither truth object is the response. At F4's own knob (κ = 1.0) the object
F5's truth-recovery correlates against is **exactly half author content and
half occasion-common content**; at κ = 0.5 it is **75 % author content**. No
adjudication is offered here; this feeds the eventual F5 re-typing and the
line synthesis.

### Part-0 register-notes (fixed before any main arm)

**R-0.2 (rule 9 — the L-3 instrument).** F4's fitter returns **no** scalar
goodness-of-fit; its fit object returns only status / exponent / intercept /
`half_agreement_mult` / `n_qualifying` / `points`. The registered "F4's fit
diagnostic" is therefore operationalized as **that fitter's own objective
value**: the weighted RMS residual of its own WLS,
`WRMSE = sqrt( Σ wⱼ rⱼ² / Σ wⱼ )` with `rⱼ = yⱼ − (b + m·xⱼ)`, computed from
`fit_axis`'s own returned qualifying `points`, its own slope/intercept, and its
own delta-method weights **copied verbatim from f1:826-841**. No new fit, no
new weights, no new points. Lower is better, so "the deleted arm's fit quality
is no worse" is **ratio = WRMSE_intact / WRMSE_deleted ≥ 1**, and the clause is
one-sided (MISS iff the whole CI lies below 1). Sanity value on F4's own data:
WRMSE = 0.056254146729854085.

**R-0.3 (pilot statistic).** See G3d above.

**R-0.4 (seed lineage).** `seed_key` = `k1d_<F4's own suffix>_k10` under
MASTER_SEED **20260814**, through `f3().world_seed_for` unchanged. This makes
both the world draws **and** the corpus tag (`m4f3-k1d_…-w{world}`, which keys
the split-half permutation `f1().half_indices` and the transition-null streams
in `f1().featurize_panel`) fresh, so the intact arm is a genuinely independent
replication rather than F4's own realization re-fitted. `budget_label` stays
F4's `"f3.0"`.

**R-0.5 (paired bootstrap scheme, rule 1).** Worlds are the bootstrap unit.
Each of 2000 draws resamples one index vector of length 8 **with replacement**
and applies it to **both arms and every cell simultaneously**, which preserves
the by-construction arm pairing. Δγ, the WRMSE ratio, and every per-point level
contrast are computed inside that same loop, so they share the resample.
Per-arm marginal γ CIs are additionally reported from **F4's own**
`bootstrap_axis` (seeds: intact 2000 — F4's own κ=1.0 seed — and deleted 2001);
the paired-bootstrap per-arm CIs are reported as the second reading. Paired
seed 20260814. G1d is adjudicated on F4's own `bootstrap_axis` CI.

**R-0.6 (G1d's timing).** G1d is listed among the Part-0 gates but is a
statement about the *main* intact arm, which cannot exist before the arms run.
As in K1c′, it is evaluated in its own stage the moment the main grid
completes and **before** the holdout and finalize stages, and the stop is
enforced in code (`_require_g1d`, and `run_g1d` raises on failure with the P1d
VOID text).

**R-0.7 (economy — the ×32 decision, fixed in Part 0, never mid-run).** The
registered inclusion rule is "include ×32 iff Part-0 pilot shows the ×16 cell's
wall-time × 2 arms keeps the leg under budget". Two readings are recorded:

- *Reading 1, the literal ×16 clause*: the ×16 cell at 2 arms projects to
  **183.615 s**; the leg without ×32 projects to **510.184 s** against the
  registered 2700 s target — satisfied.
- *Reading 2, the total projection* (**controlling**, because the clause asks
  whether *the leg* stays under budget): part0 94.430 s (measured) + arms
  355.754 s + finalize allowance 60 s + ×32 holdout 734.460 s =
  **1244.643 s ≈ 20.7 min**, under the 2700 s target.

Cost model: the pilot's measured unit cost is **5.737965673208237 s per world
per author-multiple** (linear in author count, as F4's own persisted seconds
confirm), with waves = ⌈(2 arms × 8 worlds)/workers⌉. Measured peak RSS per
worker: **392.89 MB** at ×1, **1262.27 MB** at ×16 → projected **2524.53 MB** at
×32, so the ×32 stage runs at 4 workers (≈ 10.1 GB) rather than 8.

**Decision: ×32 INCLUDED**, as a two-arm holdout on F4's own predict-then-
holdout discipline. Stop-and-report triggers at 2× any stage estimate.

---

## 1. Outcome

**Verdict:
`AUTHOR_AXIS_IS_A_REPLICATE_AXIS__EXPONENT_SURVIVES_AUTHOR_DELETION__DELETION_RAISES_LEVEL_AT_EVERY_SCALE__FIT_QUALITY_NO_WORSE`.**
L-1 HOLD (at the registered resolution — see §1.5, the verdict sits ON the
band edge), L-2 HOLD (maximal), L-3 HOLD (a non-rejection). **No pivot fires:
P1d no, P2d no, P3d no.**

### Gates

| gate | verdict | headline number |
|---|---|---|
| G0d | **PASS** | all five cited F4 numbers bit-exact on F4's own path; round-trip reading ≤ 9.023053842666835e-16 relative |
| G1d | **PASS** | γ_intact = **1.1186793702102118**, CI **[0.9810050210740082, 1.2375507404943047]** — *contains* F4's [0.9843434774823611, 1.2176831424523908] entirely |
| G2d | **PASS** | min panel Δ RMS **0.06825177531394482** vs 1e-6 bar; extraction bit-identical to `k1b.channels` (0.0) |
| G3d | **PASS** | projected Δγ half-width 0.11262789561542542 = 0.45× the ±0.25 band; 5/5 clauses satisfiable, one-sided ones marked |
| G4d | **PASS** | `mean_part` share of response RMS ∈ [0.3863012443679778, 0.38778699489363405] |
| G5d | **PASS** | rule-12 header, round-trip parsing, no background jobs (see anomaly A-1), no monitors, no smoke runs |
| G-info-F5 | report-only | truth objects are **MIXED**: exactly ½ author / ½ occasion-common at κ=1.0; ¾ author at κ=0.5; noise (70 % of response variance) excluded |

### Arms

Fresh master_seed **20260814**, κ = 1.0, shared design, 8 worlds/cell, 20
draws/world, 5 grid cells × 2 arms + the ×32 holdout × 2 arms = **96
adjudicated deployed-gauge runs** (plus 8 reserved Part-0 pilot runs).
`n_retained` constant within every cell; the two arms of a cell share a
world seed and a corpus tag by construction.

| ×mult | authors | retained | intact agreement | deleted agreement | level contrast | sign |
|---|---|---|---|---|---|---|
| ×1 | 985 | 565 | 0.012984341423949919 | 0.02501913224637748 | **+0.012034790822427564** [0.007356784950485979, 0.016901893574717598] | **8/8** |
| ×2 | 1,970 | 1,130 | 0.025300868968189855 | 0.047023073538801925 | **+0.02172220457061207** [0.01483111754607788, 0.02827874394205289] | **8/8** |
| ×4 | 3,940 | 2,260 | 0.061692728389969254 | 0.13563537782697538 | **+0.07394264943700614** [0.056074977239569, 0.08788976962524267] | **8/8** |
| ×8 | 7,880 | 4,520 | 0.1114218512750435 | 0.23614149024109704 | **+0.12471963896605351** [0.11233023681675906, 0.13557629644464192] | **8/8** |
| ×16 | 15,760 | 9,040 | 0.2303380736262515 | 0.439864728860116 | **+0.2095266552338645** [0.18374683443545525, 0.23123797419787803] | **8/8** |
| ×32 (holdout) | 31,520 | 18,080 | 0.4285829511595591 | 0.6694153296715588 | +0.2408 (not a lean point) | — |

### Fits (F4's own fitter, unchanged)

| arm | status | γ | γ CI95 (F4's own `bootstrap_axis`) | intercept | ½-agreement author budget | WRMSE |
|---|---|---|---|---|---|---|
| intact | FITTED (5/5 qualify) | **1.1186793702102118** | [0.9810050210740082, 1.2375507404943047] | −1.8894482476010845 | 48.86511436544155× | 0.02582730063382273 |
| deleted | FITTED (5/5 qualify) | **1.2446190431788744** | [1.1184843238134545, 1.3578623870533717] | −1.6159690196248342 | **19.877619351988358×** | 0.036507761119991364 |

Paired world-level bootstrap (2000 draws, registered seed 20260814, 0 failures,
0 non-positive-exponent draws): γ_intact CI [0.9507444100667262,
1.279651087486173]; γ_deleted CI [1.0975872535699003, 1.361922480014338].

### Leans

**L-1 HOLD, stated precisely (rule 4) — and the HOLD is at the band's edge.**
Δγ = γ_deleted − γ_intact = **+0.1259396729686626**, paired bootstrap CI
**[0.016883362223958802, 0.24832554505807228]**. Both registered clauses are
satisfied: the CI lies inside ±0.25 (upper margin **0.0016744549419277222**,
0.67 % of the band), and γ_deleted's CI [1.1184843238134545,
1.3578623870533717] overlaps F4's [0.9843434774823611, 1.2176831424523908] on
[1.1184843238134545, 1.2176831424523908]. **But the CI excludes zero at every
resolution and every seed tried**: author deletion does not leave the exponent
alone, it **steepens** it. Only the *immateriality* of that steepening is
licensed, and §1.5 shows the immateriality itself is Monte-Carlo fragile.
L-1's registered consequence of HOLD (re-typing F4's row to "replicate axis";
re-typing the D3 prior to "recruit replicates, not words") is the **planner's**
to execute; this leg only adjudicates.

**L-2 HOLD, maximal.** The deleted arm's level exceeds the intact arm's at
**5/5** grid points with the one-sided clause satisfied at every one (CI lower
edge > 0), and the sign is positive in **8/8 worlds at every point — 40/40
world-points**. The contrast is not a fixed offset: it grows from +0.0120 at
×1 to +0.2095 at ×16, i.e. **author deletion buys more the more replicates you
have**, which is the level-side twin of the slope result.

**L-3 HOLD — as a NON-REJECTION, not as evidence of improvement.**
WRMSE_intact = 0.02582730063382273, WRMSE_deleted = 0.036507761119991364,
**ratio (intact/deleted) = 0.7074468507924991**, CI **[0.3859105177244442,
2.142092546684852]**. The registered one-sided clause ("CI including or above
1") is satisfied because the interval contains 1, but the point estimate is
*below* 1 — in-sample the deleted arm fits its own power law slightly worse —
and the interval is wide enough to be uninformative (a 5.6-fold span). The
registered claim holds; nothing stronger is licensed.

**Disclosed second reading for L-3 (rule 9), pointing the other way.** L-3's
own sentence is about the law's *prediction*. F4's own predict-then-holdout
diagnostic, applied to both arms at ×32:

| arm | predicted | observed (se) | log-odds gap | within F4's factor-2 band (0.3010299956639812) |
|---|---|---|---|---|
| intact | 0.38377206783108325 | 0.4285829511595591 (0.019782918131416874) | **+0.08074971490742865** | ✔ |
| deleted | 0.6439648605439744 | 0.6694153296715588 (0.024556321599382074) | **+0.049043636423744374** | ✔ |

Out of sample the **deleted** arm extrapolates *better* (gap 0.0490 vs 0.0807),
both comfortably inside F4's own band. In-sample and out-of-sample disagree in
sign; both are reported and neither is adjudicated beyond the registered
clause. (Side observation, not a gate: the fresh intact arm *under*-predicts
its ×32 cell where F4's own arm *over*-predicted — F4 predicted 0.4012353096433611
and observed 0.38612436657934157; here 0.38377206783108325 predicted vs
0.4285829511595591 observed.)

### 1.5 The one thing this leg cannot resolve, disclosed in full (rule 9)

**The registered ±0.25 equivalence band is saturated, and the registered
bootstrap resolution cannot say which side of it Δγ falls on.**

| reading | Δγ CI95 upper edge | inside ±0.25? |
|---|---|---|
| **registered**: B = 2000, seed 20260814 (fixed in Part 0 R-0.5, written to disk 06:54:52 UTC, before the 06:57 arms) | **0.24832554505807228** | **YES**, by 0.0016744549419277222 |
| same seed, B = 100000 (Monte-Carlo error ≈ 7× smaller) | **0.25167594529642967** | **NO**, by 0.0016759452964296706 |
| B = 2000, nine alternative seeds | range **0.24591238773899995 – 0.2735840002946045** | **HOLD at 5 of 10 seeds** |

Artifacts: `l1_bootstrap_stability.csv`, `l1_bootstrap_highB.csv`.

**The registered reading controls the verdict** — B = 2000 and the paired seed
were both fixed before any arm ran — so **L-1 is HOLD**. But the honest
statement of what was measured is: *the exponent-equivalence claim lies exactly
on its own registered tolerance boundary, and the leg does not resolve it.*
What the leg **does** resolve, at every resolution and all ten seeds:

- **Δγ > 0** (CI excludes zero 10/10 seeds; at B = 100000, [0.018706401614875023,
  0.25167594529642967]) — the axis gets **steeper**, not merely survives;
- **L-2** — the level rises at every scale, 40/40 world-points;
- **L-3's** non-rejection (10/10 seeds).

**Registered-branch gap, reported as such.** Under the high-B reading the
configuration would be "L-1 MISS **with** γ_deleted's CI still **overlapping**
F4's band". P2d's antecedent requires MISS **and DISJOINT**, so P2d would
**not** fire, and no other registered branch covers it. That outcome — the
equivalence band exceeded while the bands still overlap — **fits no registered
branch**. It is not hypothetical here: the measurement sits on exactly that
boundary. Recommended for the planner's defect account.

### Pivots

| pivot | antecedent | fires |
|---|---|---|
| P1d | G1d fails → VOID on non-replication | **NO** — F4's law replicates; the fresh intact CI *contains* F4's whole band |
| P2d | L-1 MISS **with** γ_deleted CI DISJOINT from F4's band | **NO** — L-1 HOLD at the registered resolution, and the CIs overlap under every reading tried |
| P3d | G2d/G4d fail (deletion inert) | **NO** — deletion removes 38.7 % of the response RMS and 4.8 orders above the panel bar |

### What the leg establishes

At F4's own knob, on fresh seeds, with the entire author channel deleted:
**the author-scaling law is not a law about authors.** Its exponent survives
deletion inside the registered band (at the band's edge, §1.5), its *level*
rises at every scale, and the ½-agreement budget **more than halves** —
48.87× intact vs **19.88×** deleted. The generator's author-mean content is a
**drag on the axis it was named after**: removing it buys both a higher level
everywhere and a (slightly, robustly) steeper slope. This extends IDT appendix
F's "author content is interference" from the *level* of the composition
contrast to the *slope* of the scaling law, and it is the empirical content
behind re-typing "recruit authors" as "recruit replicates" — a re-typing that
is the planner's to execute, on an antecedent this report certifies as HOLD
and simultaneously certifies as sitting on its own tolerance boundary.

### Anomalies, with timing

- **A-1 (execution discipline, disclosed).** The `holdout` stage was invoked as
  a foreground command (07:07:40 UTC); the **shell harness** detached it to the
  background at its own 600 s cap (task `bwoku4qaf`) and re-attached on
  completion (exit 0, 710.3 s, 07:19:31 UTC). No background job was *launched*
  by the executor, no monitor was used, the invocation/stage/worker count/
  outputs are exactly those of the foreground call, and the two ×32 cell CSVs
  were written by the same process. Timing: after G1d (07:07:26) and during
  hypothesis-relevant compute; no number was altered.
- **A-2 (Part 0, before any arm).** G0d's bit-exactness is obtainable only on
  F4's *own* code path (pandas default parser). The standing round-trip
  convention deviates from F4's published values by ≤ 2 ULP
  (9.023053842666835e-16 relative). Resolved as register-note R-0.1 before any
  main arm; round-trip governs all K1d-own artifacts. Program note: the
  round-trip convention cannot retroactively reproduce a number computed under
  the default parser.
- **A-3 (after the arms — necessarily, it is a property of the result).** L-1's
  equivalence verdict is Monte-Carlo fragile: §1.5. Registered reading
  controls; both readings reported.
- **A-4 (registration-design gap).** "L-1 MISS with OVERLAP" fits no registered
  branch (§1.5).
- **A-5 (rule 9).** L-3's in-sample instrument and its out-of-sample second
  reading disagree in sign; both reported, neither adjudicated beyond the
  registered clause.
- **A-6 (registration-text observation, recorded not repaired).** G1d is listed
  among the "Part 0 gates" but is unmeasurable before the main intact arm
  exists. Resolved as register-note R-0.6 (own stage, code-enforced stop)
  before any arm ran.
- **Timing discipline.** Stage estimates vs actual: arms 355.754 s est →
  **529.1 s** (1.487×), ×32 holdout 734.460 s est → **710.3 s** (0.967×),
  finalize 60 s allowance → 0.5 s. **The 2× stop-and-report rule never
  engaged.** Total stage wall **1334.4 s**; wall-clock 06:53:17 → 07:20:05 UTC
  = **26.8 min** against the registered < 45 min target.

### Artifacts

`results/m4_k1d_replicate_axis/`: `manifest.json`, `gates.json`,
`decision.json`, `pilot_cells.csv`, `cells.csv`, `level_contrasts.csv`,
`cell_{intact,deleted}_x{1,2,4,8,16,32}.csv` (12 per-cell CSVs),
`l1_bootstrap_stability.csv`, `l1_bootstrap_highB.csv`. Script:
`scripts/run_suica_m4_k1d_replicate_axis.py`.
