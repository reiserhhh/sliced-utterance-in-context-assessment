# SUICA M4-K2b — The T4 branch: card algebra or reader floor?

Tier: **EXPLORATORY, label-free, synthetic.** Registered in
`docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md`, section "M4-K2b — The T4 branch: card
algebra or reader floor? (dissociation on the validated instrument)"
(REGISTERED 2026-08-09, BEFORE RUN, commit `791034e`), together with the K2a
planner adjudication immediately above it, whose two riders this leg binds.
Theory: `docs/SUICA_IDENTITY_THEORY_V1.md` T4 (§3), appendices A, B, E, G
(§G.3's F5 truth-object compositions), H. Ledger row `M4-K2b`. Script:
`scripts/run_suica_m4_k2b_t4_branch.py`. Artifacts:
`results/m4_k2b_t4_branch/`.

The question: **T4-simple** says the card/biography gap is CARD algebra — trait
recovery is governed by the state share and persistence through the (K2a-
measured) attenuation formula, and the deployed gauge tracks it. **T4-reader-
mediated** says the deployed gauge imposes its own floor that card algebra does
not move. K2b dissociates them on K2a's certified instrument: manipulate the
state share and persistence, run BOTH channels per arm, and see which moves.

Executor's standing: implementation and execution only. The registration text is
binding; everything below labelled **RN-n** is a register-note — an
operationalization of something the registration left as an implementation
choice, or a standing-rule-9 instrument resolution — fixed and written here
**before** any main arm ran.

---

## 0. Part 0 — register-notes, the point predictions, and the six gates

**Part 0 computed 2026-08-09 (stage `part0`, wall-time 21.475 s), persisted in
`results/m4_k2b_t4_branch/gates.json` with
`timestamp_utc = 2026-08-09T08:40:11.784643+00:00` plus
`part0_predictions.csv`, `part0_tables.md` and `part0_pilot_field.csv`. This
section was written to disk BEFORE the `arms` stage was ever invoked** — the
script enforces it: `require_part0()` refuses to run `arms` unless `gates.json`
reports `part0_all_pass` **and** this report file exists.

**No smoke run of any hypothesis channel preceded Part 0.** Every world touched
up to this point lives on the RESERVED pilot indices **9601–9602**, disjoint
from the eight main world indices 0–7. One scoping execution of the same
construction (pilot world 9601, arm A3's weights) preceded the writing of the
script itself; it produced only construction and timing quantities plus the
pilot recovery numbers that Part 0 then recomputed and persisted — it touched no
main world, and it is disclosed here rather than hidden (anomaly i).

**All six Part-0 gates PASS: `part0_all_pass = true`.**

### Register-notes (fixed before any main arm)

**RN-1 — the occasion/event grid (rule 9).** The registration requires panels
"in the deployed gauge's input format at K1-pinned dims (985 authors, F2
m-multiset, 4 contexts)" and "fixed n_occ", while K2a's validated instrument ran
`n_occ` occasions × `N_REP = 2` events. The two are reconcilable in exactly one
way that keeps a *source-anchored* occasion convention: **N_REP = 1, occasion
label = the author's own local sequential event index**, which IS F2's `shared`
design (`f2.occasion_labels`, `scripts/run_suica_m4_f2_composition.py:96-118`).
The number of occasions is therefore the author's own `m_i ∈ {8, 12, 16}` — the
K1-pinned F2 m-multiset `{8: 272, 12: 200, 16: 513}` — rather than one global
`n_occ`; "fixed n_occ" is honoured as *the occasion grid is not a manipulated
factor in this leg* (K2a swept it; K2b does not). Every prediction below is
therefore computed **per author at that author's own m** and pooled exactly, not
evaluated at a single nominal m.

**RN-2 — the arm weight vectors (rule 9).** The registration pins
`share = w_slow²` as a fraction of the non-noise signal variance, `w_int = 0`
primary, one companion at `(.30, .9, w_int equal-share)`, but not the base
split. Resolved:

- non-noise signal variance `V_s := w_mu² + w_slow² + w_int² + w_c²`, held FIXED
  at `1 − w_e² = 0.30` (RN-3);
- `w_slow² = share · V_s`;
- the remaining `(1 − share)·V_s` splits **equally over the ACTIVE non-state
  signal channels** — `{mu, common}` in the primary arms, `{mu, int, common}` in
  the companion. "w_int equal-share" therefore means *an equal share with the
  other non-state signal channels*, which leaves the registered state share
  untouched in the companion (0.30 there too).

| arm | share | φ_slow | A (`mu`) | B (`slow`) | C (`int`) | Cc (`common`) | E (`noise`) |
|---|---|---|---|---|---|---|---|
| `A1` | .02 | .90 | 0.147 | 0.006 | 0 | 0.147 | 0.70 |
| `A2` | .10 | .90 | 0.135 | 0.030 | 0 | 0.135 | 0.70 |
| `A3` | .30 | .90 | 0.105 | 0.090 | 0 | 0.105 | 0.70 |
| `A4` | .50 | .90 | 0.075 | 0.150 | 0 | 0.075 | 0.70 |
| `A5` | .30 | .98 | 0.105 | 0.090 | 0 | 0.105 | 0.70 |
| `A6` | .50 | .98 | 0.075 | 0.150 | 0 | 0.075 | 0.70 |
| `C1` (companion, descriptive) | .30 | .90 | 0.070 | 0.090 | 0.070 | 0.070 | 0.70 |

**RN-3 — the variance budget is the deployed gauge's own (rule 12).** `w_e` is
NOT a free choice here: `results/m4_f1_panel_sizing/calibration_record.json`'s
selected knobs (`k48-r0.50-mu0.15-x0.15-e0.70-p0.20_0.80`) fix `w_e = 0.70`, and
at F2's κ=1.0 shared design the remaining 0.30 splits **exactly 1:1** between
`mean_part` and the occasion-common channel. K2b holds BOTH invariants at every
arm and spends only the state share, which is the registered lever. This keeps
the leg inside the regime every other M4 leg measured, and it is why the
`mu:common` ratio is 1:1 in all six primary arms.

**RN-4 — one seed per world index, shared by all arms.** `world_seed_for(w) =
stable_bucket(f"{20260816}-{w}", salt="m4k2b-world")` depends on the world index
ONLY, so every arm sees the same trait vectors, the same AR innovations, the
same frame shocks, the same interaction loadings and the same noise, bit for bit
(K2a's RN-8 idiom). Arm contrasts are exactly paired; the φ arms differ only in
the AR recursion's coefficient, applied to shared innovations.

**RN-5 — the card's reference norm cell: `(context, m)` (rule 9 + T3).** T3's
exact cancellation of the frame channel requires a **shared occasion set**. In
this panel the occasion set is determined by `(context, m)`: authors with
different `m` average different prefixes of the same frame stream, so a
context-only norm would leave an m-dependent frame residue inside the card. The
card is therefore the deviation from the mean of the author's own
`(context, m)` cell, taken over the gauge's RETAINED set (so the two channels
describe the same 565 authors). Twelve cells, sizes 17–94 (`gates.json`
`G0b.retained_cell_sizes`); every finite-cell `(1 − 1/n_cell)` factor enters the
predictions exactly. **Measured consequence: the centred frame channel's max
absolute value over all arms and pilot worlds is 9.992007221626409e-16 — T3's
designed cancellation, at floating-point zero.**

**RN-6 — T4-simple's field-recovery prediction: the LINK (rule 9, the one
convention that matters most).** The registration asks for "Part-0 point
predictions of T4-simple's field recovery per arm from the validated algebra"
and scores `L-B` on `Spearman(predicted attenuation, measured field recovery)`
and on `S/P`. The algebra delivers an attenuation `r(card → b)`; the link from
`r` to a field-agreement number is not written. Pinned **before any arm**:

- **PRIMARY (registered clauses are scored on this): the identity link.**
  `predicted field recovery(arm) := r(card → b)(arm)`. This is T4-simple's
  literal content — *the deployed gauge tracks the card's trait recovery* — and
  it is the only link under which "predicted attenuation" and "predicted field
  recovery" are the same object, which is how the registration writes them.
  `P := r(A1) − r(A4) = 0.26881418197391516`.
- **SECOND READING: the squared link** `r²` (a relation matrix is bilinear in
  cards). `P_squared = 0.3724535373423484`. Every L-B/L-C clause is recomputed
  on it and reported.
- **THIRD READING, explicitly DESCRIPTIVE and fitting no registered branch: the
  efficiency-normalized swing.** If the gauge tracked the card algebra faithfully
  but at an arm-independent efficiency λ < 1, both `S` and the level would be
  compressed by λ while the ordering survived. `λ := mean measured recovery /
  mean predicted attenuation`, and `S/(λ·P)` is reported so the planner can see
  the compression-vs-floor distinction the registered partition does not name.
  It scores nothing.
- The **Spearman clause is link-invariant** under any monotone link, and is
  reported as the robust part of L-B.

**RN-7 — the b-only truth field, and why the strict reading is dead (rule 9,
both readings reported, one of them measured to be degenerate).** The
registration writes: "truth = mean_part-only responses through the same frozen
map — G4b verifies the construction bit-exactly by generating with
`w_slow = w_int = w_e = 0`". Those two clauses are not the same object, because
zeroing exactly those three weights leaves `w_mu·mean_part + w_c·common(o)`.
Both readings were constructed and measured in Part 0:

- **STRICT reading (`mean_part` alone, frame dropped): DEGENERATE, and provably
  so.** A strictly `mean_part`-only panel is *constant across the author's
  events*. The deployed transition branch subtracts a permuted-path null
  (`f1.featurize_panel`, `scripts/run_suica_m4_f1_panel_sizing.py:195-224`), and
  every permutation of a constant path is that same path — so `K ≡ 0` for every
  author. Measured: **`max|K| = 4.440892098500626e-16`** against
  `max|M| = 1.0`. The soft relation matrix is a cross-covariance in `K`
  (`suica_core/v8_realtext_relation_field.py:892-902`), so the truth field
  collapses: **field norm 0.0006675856745354268 (pure round-off) against the
  operative b-only field's 0.15214367930549447**, and the "recovery" it produces
  is meaningless noise (**−0.024495680267977205** on the pilot). It is not a
  reader floor; it is an empty object.
- **OPERATIVE reading (the registration's own G4b construction: arm weights with
  `w_slow = w_int = w_e = 0`): used.** The frame channel is author-invariant, so
  the field's PERSON content is still `b` alone — which is what "b-only" names —
  while the within-author variation the frozen map needs is present.
  Arm-matched (each arm's own `w_mu`, `w_c`) as the registration literally
  writes it; since RN-3 holds `mu:common` at 1:1 in every primary arm, the truth
  object differs across arms only by an overall scale.
- **MIXED truth (L-D / F5-style continuity):** the same generation with `w_e = 0`
  only — F5's Variant-A analogue (`scripts/run_suica_m4_f5_gauge_validity.py:
  225-280`), keeping state and interaction.

**RN-8 — resampling (rule 13 spec).** Card channel: **authors within world,
worlds as strata**, `B = 2000`, `seed = master_seed = 20260816` — K2a's
registered form, reused by calling `k2a.bootstrap_cell`
(`scripts/run_suica_m4_k2a_expressive_world.py:489-516`) under ONE disclosed
single-object patch (`k2a.pooled_stats` → this leg's `pooled_card_stats`, which
is k2a:459-486 restricted to the two occasion splits — there is no same-occasion
replicate at `N_REP = 1`). Per K2a **rider (i)**, only GAP-level and attenuation
quantities carry gates; the split halves are reported but never gated. Per K2a
**rider (ii)**, a **world-block** resample of the same card statistics is
computed and reported alongside every containment verdict. Field channel: the
resampling unit is the WORLD (one recovery number per arm per world), with a
single shared set of resampled world indices across all arms so every contrast
stays paired; `B = 2000`, `seed = master_seed`; the paired-t interval is
reported as a second reading. Stability rechecks at `B = 20000` for any clause
whose boundary lies within 2 Monte-Carlo endpoint sd's.

**RN-9 — machinery reuse (rule 12).** Source objects, each cited by file:line:

| object | source |
|---|---|
| trait `b` := `mean_part` | `scripts/run_suica_m4_f2_composition.py:178` (mirrored in `build_k2b_world`, `w_mu` factored out) |
| slow state (AR, pinned scalar φ) | `scripts/run_suica_m4_f2_composition.py:172-176` |
| frame channel `common(context, o)` | `scripts/run_suica_m4_f2_composition.py:121-126` (`f2().shock_vector`, called unchanged) |
| person×occasion channel | `scripts/run_suica_m4_k2a_expressive_world.py:174-181` (`k2a.shock_int_matrix`, called unchanged) |
| latent→64 map | `scripts/run_suica_m4_f2_composition.py:196` |
| orthonormal basis | `suica_core/v8_context_relation_field.py:78-84` |
| panel layout (K1-pinned dims) | `scripts/run_suica_m4_f2_composition.py:205-222` |
| deployed featurize | `scripts/run_suica_m4_f1_panel_sizing.py:166-229` |
| deployed field + agreement | `scripts/run_suica_m4_e1_convention_gap.py:230-258` |
| truth-object pattern | `scripts/run_suica_m4_f5_gauge_validity.py:225-372, 494, 505` |
| two-split probe + attenuation algebra | `scripts/run_suica_m4_k2a_expressive_world.py:282-381, 417-486` |
| pure-F2 sanity world | `scripts/run_suica_m4_f2_composition.py:276-370` (`run_axis1_world`, called unchanged) |

`suica_core/` is READ-ONLY and untouched. New objects in this leg, by
`scripts/run_suica_m4_k2b_t4_branch.py` line number as committed (rule 12):
`arm_weights` **:198**, `world_seed_for` **:223**, `layout` **:238**,
`build_k2b_world` **:316**, `emit_panel` **:359**, `occ_splits` **:388**,
`card_channel_frame` **:392**, `pooled_card_stats` **:463**,
`bootstrap_card` **:505**, `bootstrap_card_worldblock` **:512**,
`arm_predictions` **:533**, `field_from_vectors` **:592**,
`run_field_world` **:607**, `spearman` **:710**, `spearman_exact_p` **:718**,
`run_diagnostic` (post-hoc) **:1552**.

### The point predictions, computed BEFORE any arm

| arm | share | φ | w_int | A | B | Cc | ρ_int pred | ρ_cont pred | **GAP pred** | **r(card→b) pred** | T4-simple field recovery pred (identity) | (squared) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `A1` | .02 | .90 | 0 | 0.147 | 0.006 | 0.147 | 0.5602154972 | 0.5556207911 | 0.0045947060 | 0.8271784593 | 0.8271784593 | 0.6842242035 |
| `A2` | .10 | .90 | 0 | 0.135 | 0.030 | 0.135 | 0.5659896153 | 0.5435574495 | 0.0224321658 | 0.7849057220 | 0.7849057220 | 0.6160769925 |
| `A3` | .30 | .90 | 0 | 0.105 | 0.090 | 0.105 | 0.5796507290 | 0.5160841299 | 0.0635665991 | 0.6758917868 | 0.6758917868 | 0.4568297074 |
| `A4` | .50 | .90 | 0 | 0.075 | 0.150 | 0.075 | 0.5923037993 | 0.4918961444 | 0.1004076549 | 0.5583642773 | 0.5583642773 | 0.3117706662 |
| `A5` | .30 | .98 | 0 | 0.105 | 0.090 | 0.105 | 0.6123814345 | 0.5945391442 | 0.0178422903 | 0.6450572486 | 0.6450572486 | 0.4160988540 |
| `A6` | .50 | .98 | 0 | 0.075 | 0.150 | 0.075 | 0.6413294197 | 0.6135307404 | 0.0277986793 | 0.5193517935 | 0.5193517935 | 0.2697262854 |
| `C1` companion | .30 | .90 | eq | 0.070 | 0.090 | 0.070 | 0.4971859939 | 0.4318394955 | 0.0653464984 | 0.5914054902 | 0.5914054902 | 0.3497604538 |

**Predicted orderings (the sharp clauses).** GAP, descending:
`A4 > A3 > A6 > A2 > A5 > A1`. Attenuation, descending:
`A1 > A2 > A3 > A5 > A4 > A6`. The two orderings are **different**, and neither
is the state-share order alone: φ interleaves `A5` (share .30, φ .98) *between*
`A3` and `A4` on attenuation, and drops `A5` *below* `A2` on the gap. A measured
ordering match is therefore not a one-parameter coincidence.

**P (identity link) = r(A1) − r(A4) = 0.26881418197391516.**
**P (squared link) = 0.3724535373423484.**

### G0b — format, retention, and the two anchors

- **The gauge accepts the expressive world's panels.** 985 authors, 12784
  events, m-multiset `{8: 272, 12: 200, 16: 513}`, 4 contexts
  (`AskReddit, AskWomen, politics, worldnews`), all 4 resolved, **565 retained**
  (D1/D2 ∩ resolved ∩ `event_count ≥ MIN_RETAINED_EVENTS = 8`), constant across
  arms and worlds. D0 = 420 authors carry `calibrate_d0_soft`.
- **K2a bit-exact re-derivation.** Cell `phi0.9_occ8_intzero` re-derived from
  K2a's own `world_seed_for`/`suff_stats_for_world` at K2a's seeds and compared
  to the persisted `results/m4_k2a_expressive_world/cell_phi0.9_occ8_intzero.csv`
  (round-trip parsed): 2048 rows × 35 columns, **max absolute residual exactly
  0.0**. Instrument continuity is bit-exact.
- **Pure-F2 sanity world** (unmodified `f2.run_axis1_world`, κ=1.0, shared, K1
  dims, 20 draws): **agreement 0.017013597299456222** on the raw layout (13202
  events, 565 retained), **inside K1d's ×1 intact per-world range
  [0.0006462726940075391, 0.0254557937918022]** (K1d cell mean 0.012984341423949919).
  Second reading on this leg's own floored layout (12784 events):
  **0.021853063018134767**, also inside. Consistency, not a bit-anchor, exactly
  as registered — the gauge path is THE code.

### G1b — power (rule 2 + the charter's ≥3×MDE requirement)

2-world gauge pilot on the reserved indices 9601–9602, all six primary arms.
Paired `A1 − A4` differences: `0.13478068975820856`, `0.09056898284940687`;
**pilot paired sd = 0.031262397763045804** (1 df — its fragility is disclosed,
and the realized sd from the eight main worlds is reported in §1 as a second
reading).

| n worlds | MDE(80%, α=.05, paired) | P / MDE | meets 3× |
|---|---|---|---|
| **8** | **0.03604444203738883** | **7.4578538820** | **yes** |
| 16 | 0.02342878788776386 | 11.4736700533 | yes |
| 32 | 0.01598797018434708 | 16.8135278509 | yes |

**No escalation: 8 worlds per arm.** `abort_report = false`.

### G2b — rule 10 (arms differ) and rule 3 (the lever is live)

- Panels differ: minimum RMS change vs `A1` over the other six cells
  **0.01736197411054363** (floor 1e-6); the full contrast set is
  A2 0.0173619741, A3 0.0419772225, A4 0.0611390816, A5 0.0441310275,
  A6 0.0630332311, C1 0.0679371382.
- **Realized variance shares within 0.0006364661666182214 absolute** of design
  across all seven arms (K2a/defect-#19's ABSOLUTE reading; the relative reading
  is reported in `part0_tables.md`). **State-share deviation ≤
  0.0005206075051435999** in every arm, including `A1`'s design share of 0.006.
- **The designed lever moves the card channel in the predicted order on the
  pilot: Spearman(predicted, measured) = 1.0 on the GAP and 1.0 on the
  attenuation**, over all six arms. Pilot card gaps: A1 0.0020294071,
  A2 0.0199155645, A3 0.0612557929, A4 0.0982717179, A5 0.0154779602,
  A6 0.0255208085. Pilot card attenuations: A1 0.8262571268, A2 0.7845062034,
  A3 0.6759811632, A4 0.5588496562, A5 0.6453177191, A6 0.5203944469.

### G3b — satisfiability with DIRECTIONS (rule 11) and the rule-13 spec

`B = 2000`, `seed = 20260816`, stability at `B = 20000`. All seven registered
clauses are arithmetically satisfiable under the pilot statistics; the full
table with directions is in `part0_tables.md` and `gates.json`. The two that
needed real arithmetic:

- **L-B's Spearman clause**: the minimum attainable exact permutation p at n=6
  is `1/720 = 0.0013888888888888889 ≤ .005` — satisfiable (this is the check
  rule 11 exists for; a `p ≤ .0005` clause would have been *unsatisfiable* at
  six arms).
- **L-C's CI clause**: projected `1.96·se(S) = 0.02166374` against
  `P/2 = 0.13440709` — satisfiable with 6.2× headroom.
- L-A's containment clauses: projected main-run half-widths
  0.0024534476–0.0031057307 (gap) and 0.0016852664–0.0029726109 (attenuation).
- L-C's clause is one-sided **in content** (an upper bound); the registration
  says "pooled CI upper bound", so it is evaluated on the 97.5th percentile of
  the registered two-sided CI, with the one-sided 95th percentile reported
  alongside. L-D's clause is likewise predicted-positive but registered as
  "CI excluding 0", so it is evaluated two-sided with the one-sided reading
  reported.

### G4b — truth construction, VERIFIED in Part 0 (not asserted)

Following the convention the K2a adjudication added ("any bit-identity claim
stated in Part 0 is VERIFIED in Part 0"):

| check | residual |
|---|---|
| b-only truth panel vs the LITERAL registered generation (arm weights, `w_slow = w_int = w_e = 0`) | **0.0** |
| mixed truth panel vs the literal generation (`w_e = 0`) | **0.0** |
| five-channel reconstruction of the live panel | **0.0** |
| estimated field via an independent route (fresh featurize of the retained subset vs masking the already-computed full-panel features) | **0.0** |

Plus RN-7's degeneracy measurement of the strict reading:
`max|K| = 4.440892098500626e-16`, strict field norm
`0.0006675856745354268` vs operative b-only field norm `0.15214367930549447`.

### G5b — hygiene

Round-trip parsing (`float_precision="round_trip"`) on every artifact read;
manifest with master seed 20260816, per-stage seeds and wall-times; **stages
chunked (`part0` / `arms` with `--arms` selection / `finalize`), all foreground
with explicit timeouts, zero background jobs, zero monitors** (K1d anomaly-i
lesson). `results/` is gitignored.

---

## 1. Outcome

Executed exactly as registered, at the Part-0-selected **8 worlds per arm** (no
escalation). 6 primary arms + 1 descriptive companion × 8 worlds = **56
deployed-gauge world runs** on 985-author panels with **565 retained** authors
and 4 resolved contexts, plus 14 reserved-pilot gauge runs and 2 pure-F2 sanity
runs in Part 0. Card channel: 4520 pooled authors per arm.
**Total compute 59.20 s** (part0 21.474 s, arms 14.285 s + 19.111 s,
finalize 2.540 s, post-hoc diagnostic 1.790 s).

**Verdict:
`PARTIAL__BOTH_MECHANISMS_LIVE__POSITIVE_CONTROL_EXACT__LD_HOLD`.
L-A HOLD, L-B MISS, L-C MISS, **PARTIAL FIRES**, L-D HOLD. **P4b fires**;
P1b, P2b, P3b do not.**

### The two channels, per arm

| arm | share | φ | **card GAP** measured [95% CI] | GAP pred | **card r(card→b)** measured [95% CI] | r pred | **field recovery (b-only)** [95% CI] | mixed-truth recovery [95% CI] |
|---|---|---|---|---|---|---|---|---|
| `A1` | .02 | .90 | 0.0067716 [0.0041777, 0.0093654] | 0.0045947 | 0.8266854 [0.8247796, 0.8283724] | 0.8271785 | 0.1778886 [0.1688805, 0.1841638] | 0.1810416 [0.1708557, 0.1872710] |
| `A2` | .10 | .90 | 0.0247577 [0.0221654, 0.0273245] | 0.0224322 | 0.7843170 [0.7822792, 0.7861867] | 0.7849057 | 0.1506896 [0.1440455, 0.1605190] | 0.1681069 [0.1589421, 0.1792730] |
| `A3` | .30 | .90 | 0.0659988 [0.0633472, 0.0687160] | 0.0635666 | 0.6752447 [0.6726873, 0.6776206] | 0.6758918 | 0.1096226 [0.0979846, 0.1205745] | 0.1824682 [0.1692981, 0.1931844] |
| `A4` | .50 | .90 | 0.1028370 [0.1000835, 0.1057370] | 0.1004077 | 0.5578201 [0.5547693, 0.5607048] | 0.5583643 | 0.0754395 [0.0594445, 0.0897724] | 0.2023457 [0.1908236, 0.2117955] |
| `A5` | .30 | .98 | 0.0198695 [0.0175288, 0.0222171] | 0.0178423 | 0.6445124 [0.6419197, 0.6469492] | 0.6450572 | 0.1157482 [0.1035492, 0.1297088] | 0.1456281 [0.1394975, 0.1522363] |
| `A6` | .50 | .98 | 0.0297479 [0.0274668, 0.0320110] | 0.0277987 | 0.5190816 [0.5159151, 0.5220259] | 0.5193518 | 0.0691836 [0.0575131, 0.0816988] | 0.1241990 [0.1129211, 0.1339914] |
| `C1` companion | .30 | .90 (w_int eq) | 0.0688488 [0.0657741, 0.0719837] | 0.0653465 | 0.5912102 [0.5882816, 0.5940579] | 0.5914055 | 0.0725774 | 0.1822902 |

Card CIs: authors-within-world bootstrap, worlds as strata, B=2000,
seed=20260816 (the registered form). Field CIs: world-block bootstrap on shared
resampled indices, B=2000, seed=20260816.

### L-A [prior .85] — the positive control: **HOLD, and exactly**

- **GAP containment 6/6** (threshold 5). **Attenuation containment 6/6.**
- **Both orderings match EXACTLY.** GAP: predicted and measured are both
  `A4 > A3 > A6 > A2 > A5 > A1`. Attenuation: predicted and measured are both
  `A1 > A2 > A3 > A5 > A4 > A6`. These are two *different* orderings, and
  neither is the state-share order: the card resolves the φ effect, placing
  `A5` (share .30, φ .98) between `A3` and `A4` on attenuation and below `A2` on
  the gap, exactly where the AR algebra puts it.
- **Rider (ii)'s second reading agrees**: under a world-block resample the
  containment is also 6/6 and 6/6.
- **Attenuation accuracy: largest absolute error 0.00064703, largest RELATIVE
  error 0.0975%** — K2a's appendix-B formula, generalized over the heterogeneous
  m-multiset `{8, 12, 16}` and the finite `(context, m)` norm cells, is exact on
  the deployed panel to under a tenth of a percent.
- **The one blemish, diagnosed (see §1.4): the GAP sits a near-constant
  +0.00195…+0.00243 above prediction in all six arms** — inside every CI, but at
  ~0.85 of the half-width each time. The companion cell `C1` is the only cell
  whose GAP CI misses (measured 0.0688488 vs predicted 0.0653465, CI
  [0.0657741, 0.0719837]); it carries no gate.
- **The lever is unambiguously live**: the manipulation moved the card GAP by a
  factor of **15.2×** from `A1` to `A4` (0.0067716 → 0.1028370) and the card
  attenuation from 0.8266854 to 0.5578201.

**P1b does not fire. The theory reading is licensed.**

### L-B [prior .25] — T4-simple: **MISS**

- **Spearman(predicted attenuation, measured field recovery) = 0.9428571429**,
  not 1. **Exact permutation p (720 orderings, one-sided) = 0.0083333333** —
  above the registered .005. The single inversion is `A3`/`A5`: predicted
  `A3 > A5` by 0.0308345, measured `A5 > A3` by 0.0061256 with CI
  [−0.0021104, +0.0154459] (5/8 worlds positive) — **not significant**. The card
  channel got this same pair right; the field channel cannot resolve it.
- **S = 0.1024492, P = 0.2688142, S/P = 0.3811151** with CI
  [0.3276799, 0.4410191]. `S/P ∉ [0.5, 2]` — the ratio clause fails outright,
  and the CI does not even reach 0.5.

### L-C [prior .65] — T4-reader-mediated: **MISS, on one clause, by 1.5–1.7 se**

- Clause (a) `S < P/3`: **FALSE**. `S = 0.10244915371617286` against
  `P/3 = 0.08960472732463838` — S **exceeds** the bar by **0.01284443**, which
  is **1.53 se** (paired-t, sd_paired = 0.0236708) or **1.65 se** (world-block
  bootstrap, se = 0.0077724).
- Clause (b) pooled CI upper `< P/2`: **TRUE**. Upper endpoint 0.1185522 (
  one-sided 95th percentile 0.1159621) against `P/2 = 0.1344071`.
- L-A holds, so the branch's precondition was met. **L-C fails only because the
  gauge moved slightly MORE than a floored reader may move.**

### PARTIAL (named branch) — **FIRES, on both of its clauses**

- `S/P = 0.3811151367233824 ∈ [1/3, 1/2]` ✓ (the registered band, entered from
  above — 0.0478 above 1/3 and 0.119 below 1/2);
- `Spearman = 0.9428571429 ∈ (0, 1)` with `p = 0.00833 < .05` ✓.

**Both mechanisms are live.** The card lever moved the deployed gauge, in almost
exactly the predicted order, at **38% of the predicted absolute swing**.

### L-D [prior .60] — the gauge reads the mixture better than the trait: **HOLD**

Mixed-truth recovery exceeds b-only recovery in **6/6** arms, with the per-arm
95% CI of the difference excluding 0 in **5/6** (threshold 5). The one miss is
`A1`: difference +0.0031529, CI [−0.0008678, +0.0066365] (6/8 worlds positive) —
which is what the design predicts, because at share .02 there is almost no state
for the mixed truth to add. The difference grows monotonically with the state
share within each φ level: A1 +0.0031529, A2 +0.0174173, A3 +0.0728456,
A4 +0.1269062; A5 +0.0298799, A6 +0.0550154. At `A4` the gauge recovers the
**mixture** at 0.2023457 while recovering the **trait** at 0.0754395 — it reads
2.7× more of the state-inclusive object than of the person.

### 1.1 Rule 13 — Monte-Carlo verdict stability

**0 clauses triggered, 0 BOUNDARY.** Every gated clause — the twelve card
containment clauses, L-C's CI clause, L-B's S/P upper clause, and the six L-D
per-arm CI clauses — sits further than 2 Monte-Carlo endpoint sd's from its
boundary at B=2000, so no B=20000 recheck was required. (`rule13_stability.csv`
is therefore not written; `decision.json.rule13.triggered = 0`.) Note that
L-C's *failing* clause `S < P/3` is a **point** comparison, not an interval
clause, so rule 13 does not reach it — its margin is reported above in se units
instead.

### 1.2 The link sensitivity — the finding the planner most needs

**The branch verdict is not link-invariant, and the registration did not pin the
link** (RN-6). On the same measurements:

| link | P | S/P | L-B | L-C clause (a) | L-C clause (b) | branch |
|---|---|---|---|---|---|---|
| **identity (PRIMARY, registered clauses scored here)** | 0.2688142 | 0.3811151 | MISS | FALSE | TRUE | **PARTIAL** |
| squared (`r²`, declared second reading) | 0.3724535 | 0.2750656 | MISS | TRUE | TRUE | **L-C would HOLD → P2b** |

Under the squared link both L-C clauses hold with L-A holding, so the registered
partition would have delivered `T4-reader-mediated` and fired P2b. Under the
identity link it delivers PARTIAL and fires P4b. **The two readings disagree on
the T4 branch.** The Spearman clause is link-invariant (any monotone link
preserves ranks), so `Spearman ∈ (0,1)` with `p < .05` — PARTIAL's second
clause — is satisfied under **both** links; the registered partition suppresses
it under the squared link only because L-C is checked first.

The adjudication above is scored on the PRIMARY link, as declared in Part 0
before any arm. The disagreement is reported, not resolved by the executor.

### 1.3 Two descriptive readings that fit no registered branch

1. **The gauge is MORE than proportionally hurt by the state channel.** In
   absolute terms the swing is small (S/P = 0.381). In RELATIVE terms it is
   large: field recovery falls **57.59%** from `A1` to `A4`
   (0.1778886 → 0.0754395) while the card attenuation falls only **32.50%**
   (0.8271785 → 0.5583643). With `λ := mean measured recovery / mean predicted
   attenuation = 0.1741750` (an arm-independent reader efficiency),
   **`S/(λ·P) = 2.1881165`** — after removing a pure multiplicative efficiency,
   the gauge over-responds to the state share by more than 2×. This is neither
   "the gauge tracks the card algebra" nor "the gauge is floored"; it is a third
   shape, and it is the reason the absolute-swing partition cannot classify this
   result cleanly.
2. **The companion cell (descriptive, no gate).** Adding the person×occasion
   channel at equal share (`C1`) drops b-only field recovery from `A3`'s
   0.1096226 to **0.0725774** while leaving mixed-truth recovery essentially
   unchanged (0.1824682 → 0.1822902). Card-side, `C1`'s attenuation prediction
   is met (0.5912102 vs 0.5914055, contained), and its GAP is the one card cell
   whose CI misses. Occasion-bound person content behaves, at the reader, like
   more state.

### 1.4 The card GAP's +0.002 offset, diagnosed post-hoc

Stage `diagnostic` (post-hoc, flagged as such, `post_hoc_diagnostic.json`;
`decision.json` and `gates.json` untouched), on the eight main worlds:

| control (arm A1's weights, channels switched off) | predicted | measured GAP |
|---|---|---|
| `trait_only` (B = 0, E = 0) | 0 exactly, ρ = 1 on both splits | **0.0 exactly, ρ_int = ρ_cont = 1.0 exactly**, all three m |
| `state_off` (B = 0) | 0 exactly | +0.0020534 |
| `noise_only` (B = 0, A = 0) | 0 exactly | +0.0029522 |

- The card construction itself is **exact**: with only the trait and the frame
  present, both split-half ρ's are **1.0 to the last bit** in every m-cell —
  T3's frame cancellation and the two-split algebra are exactly right.
- The offset is carried **entirely by the noise channel**, and the pooled GAP
  estimator is **unbiased** on centred iid noise: a 400-replicate Monte-Carlo at
  this panel's own cell sizes gives mean −0.00030923 (se 0.00047843) at m=8,
  +0.00037341 (se 0.00057943) at m=12, −0.00013342 (se 0.00036251) at m=16 —
  all within 1 se of zero, with per-world sd matching the analytic
  `1/√(N·D)` (0.0098821, 0.0112709, 0.0074436).
- So the +0.002 is **one shared realization**, not a bias: RN-4 pairs every arm
  on the same world seeds, so the identical realized noise cross-term enters all
  six arms with nearly the same weight `(E/h)/var_card`. Scaling the measured
  `noise_only` gap by that weight at `A1` predicts +0.00228 against the observed
  +0.00218. The registered author-bootstrap covers it (6/6 containment). It is
  disclosed because a reader comparing point values across arms would otherwise
  mistake a common realization for a systematic algebra error.

### 1.5 What the leg establishes

- **The instrument transfers.** K2a's two-split probe and appendix-B attenuation
  algebra, ported to the deployed gauge's own panel (985 authors, heterogeneous
  m, 4 contexts, `(context, m)` norm cells), reproduce the designed identities
  at ≤0.0975% relative error on attenuation and exact ordering on both
  statistics. The K2a anchor cell re-derives bit-exactly (residual 0.0) and the
  pure-F2 sanity world lands inside K1d's own range.
- **The lever is live at the card and the gauge follows it, imperfectly.**
  15.2× on the card GAP; a monotone-but-for-one-insignificant-inversion field
  response; 38% of the predicted absolute swing.
- **T4's branch is NOT resolved by this design.** Neither T4-simple (L-B MISS on
  both clauses) nor T4-reader-mediated (L-C MISS by 1.5 se on its point clause)
  survives, and the verdict flips between PARTIAL and L-C with the choice of
  link the registration left open. K2c must decompose, and must pin the link.
- **The gauge reads the mixture, not the person** (L-D HOLD, 6/6): at share .50
  it recovers the state-inclusive object 2.7× better than the trait. That is the
  F5 plateau's shape, measured here against a trait-only truth object for the
  first time.

### 1.6 Pivots

| pivot | fires | consequence |
|---|---|---|
| **P1b** (L-A fails → INSTRUMENT-FAIL) | **no** | — |
| **P2b** (L-C with L-A → IDT re-typing) | **no** (would fire under the squared link — §1.2) | — |
| **P3b** (L-B → T4-simple lives) | **no** | — |
| **P4b** (PARTIAL) | **YES** | K2c is the decomposition design; **no re-typing of T4 either way** |

### 1.7 Anomalies, with timing

- **(i) Pre-Part-0 scoping run, disclosed.** Before the leg script existed, one
  scoping execution on RESERVED pilot world 9601 with arm A3's weights confirmed
  that the gauge accepts the panel format, measured the per-world cost
  (~0.6 s) and established the strict-b-only degeneracy that RN-7 rests on. It
  produced pilot recovery numbers (0.1181 b-only, 0.2096 mixed) that Part 0 then
  recomputed and persisted. **No main world (indices 0–7) was touched, and every
  Part-0 declaration — the RN-6 link choice above all — was fixed in the script's
  source before `--stage part0` ran.** Resolved before any hypothesis-relevant
  number on an adjudicated world existed.
- **(ii) Registration ambiguity: the truth object (rule 9).** "mean_part-only
  responses" and "generating with `w_slow = w_int = w_e = 0`" name different
  objects. Both were built and measured in Part 0; the strict reading is
  **degenerate** (`max|K| = 4.44e-16`, field norm 6.68e-04 vs the operative
  1.52e-01, "recovery" −0.0245 of pure round-off) because a constant path's
  permutation null equals the path itself. The registration's own G4b
  construction was used. Resolved BEFORE any arm.
- **(iii) Registration ambiguity: the link (rule 9), and it changes the
  verdict.** See §1.2. Resolved before any arm by declaring the identity link
  PRIMARY and the squared link a second reading; the disagreement between them
  was only visible after the arms and is reported, not adjudicated.
- **(iv) One crash, no result contamination.** The first `finalize` invocation
  raised `KeyError: 'r_card_b_pred_raw'` in the ordering block (the cells frame
  names that column `r_card_b_raw_pred`). Fixed and rerun; the crash occurred
  before any lean was computed, and no artifact other than a partially-written
  `cells.csv` (immediately overwritten) existed at the time.
- **(v) `C1`'s GAP CI misses its prediction.** Companion cell, explicitly
  registered as descriptive with no gate; reported for completeness.
- **(vi) `A1`'s L-D CI includes 0** under both the two-sided and one-sided
  readings (one-sided lower −7.13e-05). This is the design's own prediction at
  share .02, not a failure; L-D's registered threshold is ≥5/6.
- **(vii) No background jobs, no monitors, every stage foreground and chunked**
  (max stage 21.474 s against the 600 s shell cap).

### 1.8 Artifacts

`scripts/run_suica_m4_k2b_t4_branch.py`;
`results/m4_k2b_t4_branch/` — `manifest.json`, `gates.json`,
`part0_predictions.csv`, `part0_tables.md`, `part0_pilot_field.csv`,
`arm_{A1..A6,C1}_card.csv` (per-author sufficient statistics, 4520 rows each),
`arm_{A1..A6,C1}_field.csv`, `cells.csv`, `decision.json`,
`post_hoc_diagnostic.json` (gitignored);
`reports/SUICA_M4_K2B_T4_BRANCH_REPORT.md`; the outcome append under M4-K2b in
`docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md`; ledger row `M4-K2b`.
