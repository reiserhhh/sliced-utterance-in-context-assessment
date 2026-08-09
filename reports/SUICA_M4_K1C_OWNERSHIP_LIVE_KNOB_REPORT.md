# SUICA M4-K1c — Ownership at the live-author knob (κ = 0.5), and T6″ v2

Tier: **EXPLORATORY, label-free, synthetic.** Registered in
`docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md`, section "M4-K1c — Ownership at the
live-author knob (κ=0.5), and T6″ v2" (REGISTERED 2026-08-09, BEFORE RUN,
commit `a6d1eb2`). Theory under test: `docs/SUICA_IDENTITY_THEORY_V1.md`
dated appendices C and D (D.1 the κ=1.0 frame-ownership result, D.3 T6″ v2,
D.5 the open κ=0.5 attribution). Ledger row `M4-K1c`. Script:
`scripts/run_suica_m4_k1c_ownership_live_knob.py`. Artifacts:
`results/m4_k1c_ownership_live_knob/`.

Executor's standing: implementation and execution only. The registration text
is binding; everything below labelled "register-note" is an operationalization
of something the registration left as an implementation choice, or a standing
rule 9 instrument resolution, fixed and written here **before** any arm stage
could run.

**HEADLINE (Part 0, gate G2c): the registered A1/A3 decomposition is
DEGENERATE at κ = 0.5 — and, proved from source, at EVERY κ ∈ (0, 1]. Pivot
P4c fires: STOP, planner defect, NO ARMS RUN.** Standing rule 10 — written
into the plan doc yesterday, paid for by K1b's identical degeneracy at
κ = 1.0 — did exactly the work it was created to do, at a cost of 74.3 s
instead of a 900-run leg.

---

## 0. Part 0 — gates and register-notes, written before any arm

**Part-0 gates computed 2026-08-09 (stage `part0`, wall-time 74.255 s),
persisted in `results/m4_k1c_ownership_live_knob/gates.json` with
`timestamp_utc = 2026-08-09T05:38:19.357506+00:00`.**
**This section was written to disk before any arm stage was invoked, and no
arm stage ever ran** (G2c's registered hard stop forbids them; the script
enforces it in code — `_require_g2c_pass`, which raises on any of `arms_a`,
`gate_g1c`, `arms_b`, `sec`). The only compute that has touched the deployed
gauge in this leg is the registered G2c construction check (reserved worlds
9301–9302, 12 runs) and the registered G3c power pilot (reserved worlds
9101–9108, 56 runs) — both Part-0 objects on reserved seeds that are never
adjudicated. No smoke run of any kind preceded them.

### G0c — dims pinned to K1's, verified at the fresh seeds

Extracted from `results/m4_f1_panel_sizing/realtext_panel_reference.json`
through `f2.build_layout_common` (`scripts/run_suica_m4_f2_composition.py:205-222`)
and compared field-by-field against `results/m4_k1_issuer/gates.json` G0:

| pinned quantity | K1 | K1c | match |
|---|---|---|---|
| authors / world | 985 | **985** | ✔ |
| events allocated / world | 12,784 | **12,784** (raw 13,202) | ✔ |
| events / author multiset | {8:272, 12:200, 16:513} | **{8:272, 12:200, 16:513}** | ✔ |
| contexts | AskReddit, AskWomen, politics, worldnews | same 4 | ✔ |
| retained by the deployed gauge | 565 | **565** | ✔ |
| knobs | `k48-r0.50-mu0.15-x0.15-e0.70-p0.20_0.80` | same (read from F1's `calibration_record.json`) | ✔ |

Fresh-seed structural check at κ = 0.5: world 0 of seed group `main`
(`world_seed = 3936073819076212475`) generated, every author's event block at
shape `(m_i, 64)` — generation only, no gauge. **G0c PASS.**

**Grain (rule 5).** The unit of the primary question is the per-world paired
design contrast; 128 worlds are the sample; authors are nested inside a world
and enter only through the gauge's own aggregation. The secondary question's
unit is the per-author probe card, authors nested in 8 worlds (K1's grain).

### G1bc — K1b's anchors re-derived bit-exactly, before anything else

Recomputed from `results/m4_k1b_composition_ownership/arms_a.csv` +
`arms_b.csv` (not read off the summary), then compared to
`decision.json` **and** to the values quoted in this leg's registration:

| anchor | re-derived from CSVs | persisted `decision.json` | registration text | bit-exact |
|---|---|---|---|---|
| Δ0 (K1b, κ=1.0) | **0.02416454033421539** | 0.02416454033421539 | +0.02416454033421539 | ✔ |
| Δ1′ (author deleted) | **0.04709060297774369** | 0.04709060297774369 | +0.04709060297774369 | ✔ |
| L-e ratio R_est/R_or | **0.943890194474869** | 0.943890194474869 | 0.943890194474869 | ✔ |

F2's own κ = 0.5 block, re-verified at artifact precision from
`results/m4_f2_composition/decision.json` (G1c's replication target):
`kappa` 0.5, `free_mean` **0.0005009098594400375**, `shared_mean`
**0.009337063556542562**, paired `mean` **0.008836153697102524**, CI
**[0.004418364530893362, 0.013253942863311687]** — every field `==` the
registration's quoted value, and `shared_mean − free_mean == mean` exactly
(ULP gap 0.0). **G1bc PASS.**

### G2c — rule 10: non-degeneracy, proved from source then measured — **FAILS**

#### G2c.1 — the source derivation (before any number existed)

The registration's stated premise is: *"at κ=0.5 the blended coefficient
√(1−κ) = √0.5 > 0 keeps the author AR state in the panel, so common-structure
removal must NOT collapse shared/free into the same panel."* **The first
clause is true; it does not entail the second.** Reading
`f2.generate_world_composed` (`scripts/run_suica_m4_f2_composition.py:129-198`):

1. **`f2:180`** — `labels = occasion_labels(counts, occasion_mode)` is the
   *only* place `occasion_mode` is consumed in the whole function.
2. **`f2:184-193`** — `labels` feeds exactly one object:
   `shock_x[i,t] = shock_vector(world_seed, context, occ, k)`.
3. **`f2:151-177`** — `rng = default_rng(world_seed)`; `loadings`, `z`,
   `zeta`, `phi`, `x`, `noise` are all drawn from that single generator
   *before* the label loop, and `shock_vector` (`f2:120-126`) opens its own
   independent generator. F2's own docstring states the invariance explicitly
   (`f2:139-145`): at a fixed `world_seed` those quantities are identical
   across κ, and a fortiori across `occasion_mode`.
4. **`f2:178`** — `mean_part = √w_mu · a · ((z·g) @ Lᵀ)` → design-invariant.
5. **`f2:197`** — `noise_part = √w_e · σ_iso · noise` → design-invariant.
6. **`f2:195`** — `blended_x = √(1−κ)·x + √κ·shock_x`. The first term is
   design-invariant; **the second is the only design-carrying term in the
   generator.**
7. **`f2:196`** — `state_part = √w_x · a · ((blended_x·g) @ Lᵀ)` is *linear*
   in `blended_x`, so it splits exactly:
   `state_part = ar_part + common_part`, with
   `ar_part = √w_x·a·((√(1−κ)·x·g)@Lᵀ)` design-invariant and
   `common_part = √w_x·a·((√κ·s_{c,o}·g)@Lᵀ)` design-carrying.

**Therefore `response − common_part = mean_part + ar_part + noise_part` is
design-invariant for every κ ∈ (0,1].** A1 and A3 are the *same panel*, and
Δ1 = A1 − A3 ≡ 0. Retaining the AR state does not help, because the AR state
is precisely one of the design-invariant channels. The same conclusion holds
*a fortiori* for K1b's literal object (`response − state_part =
mean_part + noise_part`).

**κ-dependence: none.** κ rescales `common_part` by √κ but does not change
*which* channel carries the design. **No value of κ rescues the registered
decomposition.** K1b's degeneracy at κ = 1.0 was reported there as a property
of the κ = 1.0 identity `blended_x == shock_x`; it is in fact the general
case, and this leg is where that becomes visible.

*Contrapositive, for the record:* a non-degenerate frame-share arm in this
generator must retain some design-carrying content — an **estimated** or
**partial** common subtraction, or a change at the level of
`occasion_labels` — never an exact removal of the common channel.

*What is NOT degenerate:* Δ0 = A0 − A2 and Δ0′ = A5 − A6 both retain
`common_part`; `Ŝ_auth = (Δ0 − Δ0′)/Δ0` is a live measurement. Only Δ1,
Ŝ_frame and lean L-a″ are identities.

#### G2c.2 — the empirical verification (reserved worlds 9301, 9302)

Panel level, full 985-author layout, both designs, at κ = 0.5:

| check | world 9301 | world 9302 |
|---|---|---|
| four-channel reconstruction residual (mean+state+noise vs response), max abs | **0.0** | **0.0** |
| blend split residual, `state_part − (ar_part + common_part)`, max abs | 2.498e-16 | 2.776e-16 |
| `mean_part` shared vs free, max abs | **0.0** | **0.0** |
| `ar_part` shared vs free, max abs | **0.0** | **0.0** |
| `noise_part` shared vs free, max abs | **0.0** | **0.0** |
| `common_part` shared vs free, max abs | **0.32733131995696163** | **0.3310376783451957** |
| **panel A1 vs A3** (common removed), max abs | **3.331e-16** | **3.331e-16** |
| **panel A1w vs A3w** (whole state removed), max abs | **2.220e-16** | **2.220e-16** |
| panel A5 vs A6 (authors deleted), max abs | **0.32733131995696174** | **0.3310376783451957** |
| panel A0 vs A2 (intact), max abs | 0.32733131995696174 | 0.3310376783451957 |
| twin(shared) vs twin(free), shock channel zeroed, max abs | **0.0** | **0.0** |
| subtract-common vs twin, max abs | 2.498e-16 | 2.776e-16 |
| `common_part` RMS / `ar_part` RMS over events | 0.048045 / 0.048365 | 0.047839 / 0.048335 |

The derivation is confirmed exactly: the *only* channel that differs between
the shared and the free panel is `common_part`, and the A0-vs-A2 panel
difference equals the A5-vs-A6 panel difference to the last digit — because
after author deletion the remaining design-carrying content is unchanged.

Gauge level (deployed R-rel, 20 draws, 565 retained), same reserved worlds:

| quantity | world 9301 | world 9302 | max abs |
|---|---|---|---|
| Δ0 = A0 − A2 | +0.006904425383711211 | +0.004216732746104294 | — |
| **Δ1 = A1 − A3** (registered reading) | −1.734723475976807e-17 | −8.673617379884035e-18 | **1.734723475976807e-17** |
| **Δ1 = A1w − A3w** (rule-9 second reading) | +3.729655473350135e-17 | −1.6479873021779667e-17 | **3.729655473350135e-17** |

**Registered threshold: Δ1 must not be identically 0 at 1e-12. Measured
1.73e-17 — five orders of magnitude below the threshold, and consistent with
pure floating-point subtraction residue.** Both readings fail identically.

**G2c VERDICT: DEGENERATE. Consequence, as registered: P4c FIRES — STOP,
registration defect, NO ARMS.**

### G3c — power (rule 2), reserved 8-world pilot 9101–9108

Run as a Part-0 object before the stop was acted on, so the planner has the
resolution facts for the re-registration. Seven arms × 8 reserved worlds =
56 deployed-gauge runs, 58.5 s.

- pilot Δ0 = A0 − A2: 0.0036356667301342726, 0.01642470033128599,
  0.017135966700884724, 0.0015945478579621319, 0.009310137444826103,
  0.0060580677655579975, 0.01027720347895456, 0.00037006214721764866
- pilot Δ1 = A1 − A3: −3.21e-17, −5.59e-17, −7.81e-17, −1.04e-17, +2.26e-17,
  +2.17e-18, +1.91e-17, −2.78e-17 — **the designed identity, confirmed
  end-to-end through the deployed gauge on eight independent reserved seeds**
- pilot Δ0′ = A5 − A6: 0.026624914333870618, 0.024302273478658494,
  0.03363745072749547, 0.00956413635832475, 0.009509350025625706,
  0.01083746845748395, 0.011629457249265947, 0.020144890376579173
- sd of (Δ0 − Δ1) = **0.006362014258526332**; sd of (Δ0 − Δ0′) =
  **0.008560686670660837**
- 80 %-power multiplier at n = 128: t(.975,127) + t(.80,127) =
  2.8232801742461984
- **MDE(80 %, α=.05, paired t, n=128), (Δ0 − Δ1) = 0.0015876092906212693**
- **MDE(80 %, α=.05, paired t, n=128), (Δ0 − Δ0′) = 0.0021362771506247724**

Both are **inside the registered bar 0.004418076848551262** (2.78× and 2.07×
inside) **and inside the aspirational resolution 0.002209038424275631**. No
escalation to 256 worlds; no claim tiering would have been needed.
**G3c PASS.**

> **Disclosure, flagged as such.** The pilot Δ0′ column exceeds the pilot Δ0
> column in 8/8 reserved worlds, so pilot (Δ0 − Δ0′) is negative in 8/8
> (mean −0.010180448568810086). That is the same sign K1b measured at κ=1.0.
> **This is reserved-seed Part-0 power material and is NOT this leg's answer
> to L-b″** — the lean was never adjudicated, the 128 adjudicated worlds were
> never run, and no bootstrap CI, sign band or share was computed on it. It is
> recorded only because rule 2 requires the pilot to be reported and because
> the planner will want it when re-registering.

### G4c — liveness at κ = 0.5 (rule 3), the inverse of F7/F8's inertness test

Computed on the eight pilot worlds' own seeds, on f2's generator directly
(M4-F8's G6 construction, `scripts/run_suica_m4_f8_occasion_axis_live.py:
~700-800`, re-expressed here for f2's ragged per-author layout; between-author
variance = trace of the between-author covariance of each author's own mean
event vector).

**(i) Author channel live at κ = 0.5 — YES, on both readings.**

| reading | ratio min | max | mean | > 1 at every world |
|---|---|---|---|---|
| AR state intact vs zeroed (**registered**: the √(1−κ) term, `f2:195`) | **1.0772786802493795** | 1.0860125411681176 | 1.0822512197016676 | ✔ 8/8 |
| author-mean channel intact vs zeroed (the channel A5/A6 actually delete) | **2.8194500501220903** | 2.865341972610127 | 2.8435202098986503 | ✔ 8/8 |

At κ = 1.0 the first ratio is exactly 1 by construction (M4-F7's inertness
result); here it is 1.077–1.086, i.e. the AR state contributes ≈ 7.7–8.6 % of
between-author variance at this knob. The author-*mean* channel is far more
live (ratio ≈ 2.84) and is the one the registered author-deletion arms remove
— reported alongside under rule 9, because the registration's liveness clause
and its A5/A6 arms name different channels.

**(ii) Removal channel live — YES.** The removed `common_part` is non-zero at
every pilot world (max abs 0.1770–0.2213) and carries **27.4 %** of the
response RMS on average (`removed_over_response_rms_mean =
0.27447485652733755`). A0 and A1 inputs genuinely differ.

**(iii) Informational — sign of the author-deletion response at this knob.**
Not computed as a hypothesis-relevant quantity: the arms that would supply it
(A5 − A0 on the 128 adjudicated worlds) are blocked by G2c. The reserved
pilot's Δ0′ > Δ0 pattern is disclosed above under G3c with its status
attached. **G4c PASS.**

### G4c-info — which κ did F4 and F5 actually run at? (report-only, adjudicates nothing)

Re-derived at artifact precision from the persisted `cells.csv`,
`decision.json` and `gates.json` of each leg. **Neither leg persisted a
`manifest.json`** (both `manifest_json_present = false`); the κ facts come
from the cell table and the decision record.

| fact | M4-F4 (`results/m4_f4_author_axis/`) | M4-F5 (`results/m4_f5_gauge_validity/`) |
|---|---|---|
| experiment id | `M4-F4_author_axis_law_or_artifact` | `M4-F5_gauge_validity` |
| master_seed | 20260802 | 20260802 |
| worlds/cell × draws/world | 8 × 20 | 8 × 20 |
| knob_tag | `k48-r0.50-mu0.15-x0.15-e0.70-p0.20_0.80` | same |
| κ values present in `cells.csv` | **0.5 and 1.0** | **0.5 and 1.0** |
| cells per κ | 5 at κ=0.5, 6 at κ=1.0 | 5 at κ=0.5, 6 at κ=1.0 |
| world-runs per κ | 40 at κ=0.5, 48 at κ=1.0 | 40 at κ=0.5, 48 at κ=1.0 |
| κ that carries the adjudicated claims | **κ = 1.0 only** | κ=1.0 primary; κ=0.5 is lean_c's own subject |
| leans | a HOLD, b HOLD, c HOLD — all three stated at κ=1.0 | a MISS (co-movement), b MISS (target adequacy), **c HOLD (κ stability)** |

F4's own decision record states the κ status verbatim: *"kappa=0.5 is the
registered robustness axis; it gates no lean or the pivot (all three leans,
the budget claim, the holdout, and the pivot are specified at kappa=1.0 only,
mirroring M4-F3's own treatment of its non-decisive kappa) and is reported
for context."* F4's holdout cell is `authors_x32_holdout_shared_k10` — κ=1.0.
F5's `t_large_primary` = 80.

**Consequence for the planner's pending retrospective (stated, not
adjudicated): both F4 and F5 ran BOTH knobs and persisted both; F4's
adjudicated claims are κ=1.0-only, so K1b's κ=1.0 frame-ownership finding is
in scope for F4's headline; F5 additionally carries an adjudicated κ-stability
lean that HELD, i.e. F5 already tested and reported the κ=0.5 leg of its own
claim.** No further adjudication here, as registered.

### G5c — hygiene, and rule 11 (arithmetic satisfiability of every CI clause)

`results/m4_k1c_ownership_live_knob/manifest.json`: master_seed **20260812**;
seed recipe `v8.stable_bucket(f'{MASTER_SEED}-{group}-w{world}-{knob_tag}',
salt='m4k1c-world', modulus=2**63-1)` — the same recipe `f2.run_axis1_world`
computes internally (`f2:288-291`), so every arm of a world shares one world
seed and design contrasts are exactly paired. Groups: `main` (0–127, never
run), `pilot` (9101–9108), `g2c` (9301–9302), `abs` (0–7, never run). A4's
norm pool: `stable_bucket(f'{world_seed}-normpool', salt='m4k1c-normpool')`.
Bootstrap seeds listed per statistic in the manifest. All stages foreground
with explicit timeouts; **zero background jobs, zero monitors, zero
sleep-and-poll**. Python 3.14.3 / numpy 2.4.4 / pandas 3.0.2.

**Rule 11 — every CI clause in the K1c registration, checked satisfiable at
the pilot sd BEFORE arms. All ten clauses are satisfiable; the
unsatisfiable-clause list is empty.** (This is the check that K1b's G4b
defect, program account #12, created.)

| registered clause | half-width at pilot sd (n=128) | reference | satisfiable |
|---|---|---|---|
| G1c: Δ0 CI overlaps F2's κ=0.5 CI | 0.001112745488887191 | overlap is monotone-easier in width | ✔ (unconditionally) |
| L-a″: (Δ0−Δ1) CI excludes 0 | 0.0011127454888871938 | pilot point 0.008100794057102949 | ✔ |
| L-b″: (Δ0−Δ0′) CI excludes 0 | 0.0014973033834037816 | pilot point −0.010180448568810086 | ✔ |
| L-c″: \|A3−A2\| CI inside ±0.004418076848551262 | 0.0009236085890751873 | margin | ✔ |
| L-c″: \|A6−A2\| CI inside ±0.004418076848551262 | 0.0011335194525164446 | margin | ✔ |
| L-d″: R_est CI excludes 0 | 0.000809411049756907 | pilot R_est 0.004051794736468587 | ✔ |
| L-e″: reader-A′ (est8−oracle) CI upper < +0.005 | — | K1b anchor −0.06230964467005076, CI [−0.07106916243654822, −0.05418781725888325] | ✔ |
| L-e″: oracle stability < 0.01 | — | K1b anchor move 0.0025380710659898 | ✔ |
| G3c: MDE(n=128) ≤ 0.004418076848551262, both gaps | — | 0.0015876092906212693 / 0.0021362771506247724 | ✔ |
| G4c: liveness ratio > 1 at every pilot world | — | no CI clause | ✔ |

**G5c PASS.** Note the contrast with K1b: the registration's *statistical*
clauses are all sound at this design — what failed is the *structural*
premise, which is exactly what rule 10 (and not rule 11) exists to catch.

**Part-0 stage estimates, for the registration's stop-at-2× rule:** `part0`
≤ 300 s (actual **74.255 s**); `arms_a` ≤ 400 s, `arms_b` ≤ 1200 s, `sec`
≤ 200 s, `finalize` ≤ 120 s — the last four never invoked.

---

### Part-0 register-notes (fixed before any arm)

**R-0.1 — standing rule 9: what "K1b's verified exact surgery" removes at a
knob where the blend is non-trivial.** The registration's A1/A3 arms say
"occasion-common structure removed (K1b's verified exact surgery)". At κ=1.0
those two descriptions name one object, because `blended_x == shock_x`
(`f2:195`). At κ=0.5 they name **different** objects: the semantic
"occasion-common structure" is `common_part = √w_x·a·((√κ·s·g)@Lᵀ)`, while
K1b's literal code object is the whole state slot `state_part`, which also
deletes the author AR state. **Resolved before any hypothesis-relevant number
existed:** the registered arm is the *semantic* one (A1/A3 = subtract
`common_part`), because the registration's own G2c rationale relies on the AR
state being **retained** ("√(1−κ) > 0 keeps the author AR state in the
panel"), which is only true of that reading. The literal-K1b reading was
implemented in full as arms **A1w/A3w** and computed at every G2c cell as the
disclosed second reading. **Both readings are degenerate, identically** (Δ1
1.73e-17 and 3.73e-17), so the choice changes nothing about this leg's
outcome; it is recorded because rule 9 requires it.

**R-0.2 — standing rule 9: which channel G4c's liveness clause names.** G4c(i)
says "author channel … between-author variance ratio (author state intact vs
zeroed)". "Author state" is the AR state `x` (the √(1−κ) term); "author
channel" in the A5/A6 arms is the author-mean channel `mean_part` (`f2:178`) —
the exact ambiguity that produced planner defect #10. Both readings are
computed and reported (1.077–1.086 and 2.819–2.865); both clear the ">1 at
every pilot world" bar, so the ambiguity is again non-decisive here.

**R-0.3 — A4's estimated norm at a knob where the AR state is live.** K1b's
`estimated_occasion_norm` built the disjoint pool's idiosyncratic content as
`mean_part + noise_part`, correct at κ=1.0 where the pool's AR contribution is
identically zero. At κ=0.5 the pool authors also carry `√(1−κ)·x`, so the
faithful κ-generalization of "an estimated per-occasion norm from |P| = 32
disjoint authors' **responses**" is
`idio = mean_part + ar_part + noise_part`, with the panel's own `C(c,o)`
(now carrying its √κ factor) substituted for the pool's occasion channel.
This reduces bit-exactly to K1b's construction at κ=1.0. Implemented that way;
never exercised on an adjudicated world (A4 ran only on the reserved G3c
pilot).

**R-0.4 — G2c's empirical check runs the deployed gauge on reserved seeds.**
The registration asks for "per-world Δ1 not identically 0 at 1e-12", which is
a statement about the gauge's output, not the panel. Reserved worlds
9301–9302 (group `g2c`, disjoint from `main` and `pilot`) carry it; those 12
runs plus the 56 pilot runs are the leg's entire gauge budget. Declared here
as Part-0 objects.

**R-0.5 — the stop is enforced in code, not by discipline alone.**
`_require_g2c_pass()` raises `AssertionError` on `arms_a`, `gate_g1c`,
`arms_b` and `sec` whenever `gates.json` records `G2c.pass == false`. There is
no flag to override it.

**R-0.6 — G3c and G4c were computed even though G2c stops the leg.** The stop
is registered as "no **arms**". G3c's pilot and G4c's liveness diagnostic are
Part-0 objects on reserved seeds, they are registered deliverables, they cost
59 s, and their outputs (resolution at n=128, channel liveness at κ=0.5) are
precisely what a re-registration needs. Running them is disclosed here as an
executor decision, made before the numbers existed, and it changes no lean:
every lean is recorded as NOT ADJUDICATED.

---

## 1. Outcome — P4c fires, no arms

**Verdict slug:**
`REGISTERED_FRAME_SHARE_DECOMPOSITION_DEGENERATE_AT_EVERY_KAPPA__PROVED_FROM_SOURCE_BEFORE_ARMS__P4C_FIRES__NO_ARMS_RUN`

| gate | verdict |
|---|---|
| G0c dims | **PASS** |
| G1bc anchors | **PASS** (all three K1b anchors bit-exact; F2 κ=0.5 block exact) |
| **G2c non-degeneracy** | **FAIL — DEGENERATE** (Δ1 max 1.73e-17 vs a 1e-12 bar) |
| G3c power | **PASS** (both MDEs inside the bar and the aspirational resolution) |
| G4c liveness | **PASS** (both author-channel readings > 1 at 8/8 worlds; removal channel 27.4 % of response RMS) |
| G4c-info | report-only, delivered |
| G5c hygiene + rule 11 | **PASS** (0 unsatisfiable clauses of 10) |
| G1c replication | **NEVER EVALUATED** (needs the 128-world arms) |

| lean | prior | verdict |
|---|---|---|
| L-a″ frame share is the majority | .55 | **NOT ADJUDICATED** (Ŝ_frame is an identity ≡ 1; the arms were not run) |
| L-b″ an author-reading share exists | .50 | **NOT ADJUDICATED** |
| L-c″ free-side specificity | .70 | **NOT ADJUDICATED** |
| L-d″ deployable repair at the live knob | .60 | **NOT ADJUDICATED** |
| L-e″ T6″ v2 (sign form) | .80 | **NOT ADJUDICATED** |

| pivot | fires |
|---|---|
| P1c (G1c fails → VOID on non-replication) | no — G1c never evaluated |
| P2c (L-b″ MISS with a bounded author share) | no — L-b″ never measured |
| P3c (L-e″ fails → T6″ v2 dead) | no — L-e″ never measured |
| **P4c (G2c degenerate → STOP, planner defect, no arms)** | **YES** |

### What the leg establishes

1. **A source-level structural theorem about F2's generator**, stronger than
   K1b's κ=1.0 statement: `occasion_mode` reaches the response through exactly
   one channel (`f2:180 → 184-193 → 195`), so *any* exact removal of the
   occasion-common content makes the shared and free designs the same panel.
   **The registered frame/author decomposition is impossible at every κ,
   not just at κ=1.0.** K1b's report attributed the collapse to the κ=1.0
   identity `blended_x == shock_x`; that attribution was too narrow, and this
   leg corrects it before it could cost a second 900-run leg.
2. **The author channel IS live at κ=0.5** (ratios 1.077–1.086 for the AR
   state, 2.819–2.865 for the author-mean channel, 8/8 worlds) — so a null at
   this knob would not be vacuous under rule 3. The knob is fine; the
   *contrast* was not.
3. **The design is well powered** for both registered gaps at n=128
   (MDE 0.00159 and 0.00214 against a 0.00442 bar). The leg did not stop for
   want of resolution.
4. **Every CI clause of the registration is arithmetically satisfiable**
   (rule 11's first clean pass).

### The re-registration this implies (executor's input, planner decides)

The registered question — *does the composition effect at κ=0.5 carry any
author-reading share?* — is **answerable with the arms already implemented**,
because the author-deletion contrast is NOT degenerate: at panel level A5 and
A6 differ by 0.331, exactly as A0 and A2 do. A K1c′ that drops A1/A3/Ŝ_frame
and keeps `Δ0 = A0−A2`, `Δ0′ = A5−A6`, `Ŝ_auth = (Δ0−Δ0′)/Δ0`, plus A4 for the
repair lean and the unchanged secondary, needs 5 arms × 128 worlds = 640 runs
and inherits this leg's Part 0 wholesale (G0c, G1bc, G3c, G4c, G5c all pass;
G3c's MDE for (Δ0−Δ0′) is 0.00214). If a genuine *frame-share* arm is wanted,
it must retain design-carrying content — an estimated or partial common
subtraction, or a manipulation at the level of `occasion_labels` — never an
exact channel removal.

### Anomalies, with timing

- **A-1 (planner registration defect; detected in Part 0, before any
  hypothesis-relevant number existed).** G2c's stated rationale — "√(1−κ) > 0
  keeps the author AR state in the panel, so common-structure removal must NOT
  collapse shared/free into the same panel" — is a non-sequitur: the retained
  AR state is design-invariant. Recorded, not repaired. This is the second
  instance of the family that produced standing rule 10.
- **A-2 (rule-9 instrument ambiguity, ×2; resolved before any
  hypothesis-relevant number).** "K1b's verified exact surgery" and
  "occasion-common structure" name different objects at κ<1 (R-0.1);
  "author state" (G4c) and "author channel" (A5/A6) name different channels
  (R-0.2). Both resolved by written rule, both readings computed and reported,
  neither decisive.
- **A-3 (executor decision, disclosed).** G3c and G4c were computed after G2c
  had already failed (R-0.6). Cost 59 s; adjudicates nothing.
- No background jobs, no monitors, no smoke runs. No stage exceeded its
  Part-0 estimate (74.255 s against a 300 s estimate; the 2× stop-and-report
  rule never engaged).

### Artifacts

- script `scripts/run_suica_m4_k1c_ownership_live_knob.py`
- `results/m4_k1c_ownership_live_knob/manifest.json`, `gates.json`,
  `g2c_cells.csv` (12 gauge runs), `pilot_cells.csv` (56 gauge runs),
  `g4c_liveness.csv` (8 worlds), `decision.json`
- total compute **74.3 s**, all foreground, **68 deployed-gauge runs**, all on
  reserved seeds; 0 adjudicated worlds.

**Claim boundary.** Synthetic throughout; a source-level structural result
about M4-F2's generator plus Part-0 diagnostics on reserved seeds. Licenses
IDT grammar only. No claim about any corpus, construct, person, or diagnosis.
No seal, no independent verification (open-exploration phase rules).
