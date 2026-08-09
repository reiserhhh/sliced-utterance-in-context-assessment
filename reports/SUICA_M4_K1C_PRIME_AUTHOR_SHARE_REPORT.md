# SUICA M4-K1c′ — Author-reading share at the live knob (κ = 0.5)

Tier: **EXPLORATORY, label-free, synthetic.** Registered in
`docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md`, section "M4-K1c′ — Author-reading
share at the live knob: the non-degenerate remainder of K1c" (REGISTERED
2026-08-09, BEFORE RUN, commit `9a1d877`). Theory under test:
`docs/SUICA_IDENTITY_THEORY_V1.md` dated appendices D (D.1 the κ=1.0
frame-ownership result, D.3 T6″ v2, D.4 the de-framing repair) and E (the
world-family lemma; E.3(b) names Ŝ_auth as the only live ownership question
inside F2's family). Ledger row `M4-K1c′`. Script:
`scripts/run_suica_m4_k1c_prime_author_share.py`. Artifacts:
`results/m4_k1c_prime_author_share/`.

Executor's standing: implementation and execution only. The registration text
is binding; everything below labelled "register-note" is an operationalization
of something the registration left as an implementation choice, or a standing
rule 9 instrument resolution, fixed and written here **before** any main arm
stage ran.

---

## 0. Part 0 — gates and register-notes, written before any main arm

**Part-0 gates computed 2026-08-09 (stage `part0`, wall-time 15.273 s),
persisted in `results/m4_k1c_prime_author_share/gates.json` with
`timestamp_utc = 2026-08-09T06:06:17.808770+00:00`. This section was written
to disk before any main arm stage was invoked.** The only compute that has
touched the deployed gauge at this point is the registered Part-0 pilot
(reserved worlds 9401–9402, 6 arms × 2 worlds = **12 gauge runs**), whose
seeds are disjoint from the 128 `main` worlds and from the 8 `abs` worlds and
are never adjudicated. **No smoke run of any kind preceded it**; the two
Part-0 invocations that exist are disclosed as anomaly A-1 below (an
instrument fix between them, made before any hypothesis-relevant number
existed).

**All five Part-0 gates PASS: `part0_all_pass = true`. P4′ does not fire.**

### G0′ — inheritance anchors, re-derived bit-exactly

Every anchor the registration names is **recomputed from K1c's RAW persisted
rows, or re-run from the generator — never read off a summary** — and then
checked against BOTH the persisted summary AND the registration text. All
seven are bit-exact.

| anchor | re-derived | source of the re-derivation | == persisted == registration |
|---|---|---|---|
| G3c MDE, (Δ0−Δ1), n=128 | **0.0015876092906212693** | `pilot_cells.csv` → sd(Δ0−Δ1) → MDE formula | ✔ |
| G3c MDE, (Δ0−Δ0′), n=128 | **0.0021362771506247724** | `pilot_cells.csv` → sd(Δ0−Δ0′) → MDE formula | ✔ |
| K1c pilot sd, (Δ0−Δ0′) | **0.008560686670660837** | `pilot_cells.csv` | ✔ |
| G4c AR-state ratio band | **1.0772786802493795 – 1.0860125411681176** | `g4c_liveness.csv` | ✔ |
| G4c author-MEAN ratio band | **2.8194500501220903 – 2.865341972610127** | `g4c_liveness.csv` | ✔ |
| G4c common-channel share | **0.27447485652733755** | `g4c_liveness.csv` | ✔ |
| A5-vs-A6 panel gap | **0.3310376783451957** | **re-run from the generator** at K1c's own persisted world seed 6845424899141898945 (world 9302), via `k1c._design_independence_report` | ✔ |

Companion (G1′'s target, at artifact precision, from
`results/m4_f2_composition/decision.json`): κ=0.5 free
**0.0005009098594400375**, shared **0.009337063556542562**, paired
**0.008836153697102524**, CI **[0.004418364530893362, 0.013253942863311687]**,
and `shared − free == paired` with gap exactly **0.0**.

Panel dims (rule 5, inherited from K1c's G0c and K1's G0, field-by-field):
985 authors/world, 12,784 allocated events, multiset {8:272, 12:200, 16:513},
4 contexts, 565 retained by the deployed gauge — all ✔. Knobs
`k48-r0.50-mu0.15-x0.15-e0.70-p0.20_0.80` read from F1's
`calibration_record.json`. Grain: per-world paired design contrasts, 128
worlds as the unit, authors nested within world.

**Register-note R-0.1 (registration-text inaccuracy, disclosed, not
repaired).** The registration says these anchors are to be re-derived "from
`results/m4_k1c_ownership_live_knob/decision.json`". That file carries the
A5-vs-A6 panel gap (under `adjudication.G2c`) but **not** the two G3c MDEs and
**not** the G4c ratios — those live in `gates.json` in the same directory. The
gate is satisfied in the stronger form described above (raw rows and the
generator, checked against the summary *and* the registration text), so the
inaccuracy costs nothing.

**Register-note R-0.2 (rule 9, instrument convention; fixed before any
hypothesis-relevant number).** pandas 3.0.2's **default** CSV float parser does
not round-trip float64: `to_csv` writes the exact repr, but `read_csv` returns
a neighbouring double (measured here: `1.0772786802493795` →
`1.0772786802493797`). Under the default parser the seven anchors above
reproduce only to ~2 × 10⁻¹⁵ relative, which is not "bit-exact". **Written
rule, adopted for the whole leg: every persisted per-cell artifact is read
with `float_precision="round_trip"`** (function `read_cells`). All seven
anchors then match bit-exactly, and this leg's own pooled statistics are
exactly reproducible from its own CSVs. Consequence for a K1c number, recorded
for the record: K1c's rule-11 line quoted its pilot R_est as
`0.004051794736468587`; recomputed from the same CSV with round-trip parsing
it is `0.004051794736468588` (1 ULP). K1c's own gate values are unaffected —
they were computed in memory.

**G0′ PASS.**

### G2′ — rule 10: non-degeneracy of the REGISTERED contrasts at fresh seeds

Reserved fresh worlds 9401–9402 (group `pilot`, master_seed 20260813), 985
authors, both designs, panel level.

| quantity | world 9401 | world 9402 |
|---|---|---|
| **A5 vs A6 panel RMS** (bar > 1e-6) | **0.06929976550687832** | **0.06923291177968123** |
| A5 vs A6 panel max-abs (second reading) | 0.3373434343154096 | 0.32771753382098273 |
| A0 vs A2 panel RMS | 0.06929976550687832 | 0.06923291177968123 |
| A0 vs A1 input RMS (`common_part`) | 0.049660611183466215 | 0.0495022679562676 |
| A0 vs A1 input max-abs | 0.18804793947146423 | 0.18679061314297404 |
| common share of response RMS | 0.2798692394750911 | 0.2792645992090243 |

**The registered contrast is non-degenerate by five orders of magnitude**
(0.0692 against a 1e-6 bar), and A0-vs-A1 inputs differ at every world.
**G2′ PASS. P4′ does not fire.**

**Structural note, and the reason the leg is well-posed.** The A5-vs-A6 panel
RMS is **bit-identical** to the A0-vs-A2 panel RMS at both worlds. That is an
exact identity, not a coincidence: A5 = shared − `mean_part` and
A6 = free − `mean_part` subtract the *same* design-invariant object (f2:178)
from both designs, so (A5 − A6) ≡ (A0 − A2) as panels. **Δ0 − Δ0′ is therefore
a purely GAUGE-level quantity**: at panel level the two design contrasts are
literally the same object, so any non-zero Δ0 − Δ0′ is the nonlinear frozen
map's use of author content, not a difference in what the design does. This is
exactly the measurement K1c was blocked from making, and it is not an identity
in either direction.

**A1's status (registered).** The A1-degeneracy identity — `response −
common_part` is design-invariant at every κ ∈ (0,1] — is a PROVED fact (K1c
G2c source proof over f2:180 / 184-193 / 151-177 / 178 / 195 / 196 / 197; IDT
appendix E.1) and is **cited, not re-tested**. A3 is not an arm of this leg;
Δ1 and Ŝ_frame are not quantities of this leg. A1 is retained solely as the
**ORACLE DE-FRAMING REFERENCE**: by that same identity its gauge value *is*
the no-composition baseline, so R_or = A0 − A1 is the full de-framing move
against which the estimated repair R_est = A0 − A4 is scored.

### G3′ — power (rule 2)

Fresh 2-world pilot, all six arms, 12 gauge runs, 14.5 s.

| quantity | value |
|---|---|
| inherited MDE(80 %, α=.05, paired t, n=128) for (Δ0−Δ0′) | **0.0021362771506247724** |
| K1c pilot sd (n=8) | 0.008560686670660837 |
| fresh pilot sd (n=2, ddof=1) — primary | **0.003757879890017854** |
| fresh pilot sd (n=2, ddof=0) — second reading | 0.002657222353116182 |
| ratio fresh / K1c | **0.43896944656283826** |
| "within 2×", two-sided reading (0.5 ≤ r ≤ 2) — primary | **FAILS (0.439 < 0.5)** |
| "within 2×", one-sided power-relevant reading (r ≤ 2) | PASSES |
| MDE recomputed at the fresh sd | **0.0009377603985145934** |
| registered bar | 0.004418076848551262 |
| **controlling MDE for this leg** | **0.0021362771506247724** |

**Register-note R-0.3 (rule 9, two open conventions in one clause; resolved
before the numbers).** (i) "within 2×" admits a two-sided (0.5–2) and a
one-sided (≤2) reading. **Both are computed and reported; the two-sided
reading is primary and it MISSES** — the fresh sd is *smaller* than K1c's, not
larger. (ii) The registration's own fallback is then executed unconditionally:
the MDE is recomputed at the fresh sd (0.00093776) and re-checked against the
bar 0.004418076848551262 — it passes, as does the inherited MDE. **G3′ PASS on
every reading.** (iii) The *controlling* MDE is fixed by written rule as the
**larger (more conservative)** of the two, i.e. the inherited
**0.0021362771506247724**: an sd from n = 2 has one degree of freedom and may
never be used to claim more resolution than the inherited n = 8 pilot
supports.

Fresh reserved-pilot dispersion for the other registered contrasts (n=2,
ddof=1): Δ0 0.0051414232155799116; Δ0′ 0.0013835433255620585; (A6−A2)
0.0037694521482095704; (A5−A0) 1.157225819171765e-05; R_or
0.0022502378355698975; R_est 0.0032472897468629946.

*Disclosed with its status attached, exactly as K1c disclosed the same
object:* the fresh pilot's Δ0 − Δ0′ is **negative at 2/2 reserved worlds**
(−0.01777816248096422, −0.012463717774731856; mean −0.015120940127848037) —
the same sign K1b measured at κ=1.0 and K1c's reserved pilot measured 8/8.
**This is reserved-seed power material, NOT an answer to L-1.** No CI, no sign
band and no share exists for it, and none will be quoted from it.

### G4′ — liveness of the deleted channel (rule 3)

The channel arms A5/A6 actually delete is the author **MEAN** channel
`mean_part` (f2:178). Between-author variance, intact vs that channel zeroed,
at the fresh pilot worlds:

| reading | world 9401 | world 9402 | K1c's inherited band |
|---|---|---|---|
| **author-MEAN ratio (registered)** | **2.8552376916466695** | **2.864645232241155** | 2.8194500501220903 – 2.865341972610127 |
| author AR-state ratio (reported) | 1.0817049201258067 | 1.0822239823705524 | 1.0772786802493795 – 1.0860125411681176 |
| common-channel share of response RMS | 0.2798692394750911 | 0.2792645992090243 | 0.27447485652733755 |

Both readings exceed 1 at 2/2 fresh worlds and both sit inside K1c's inherited
bands. **The channel this leg deletes is live; a null here would not be
vacuous. G4′ PASS.**

### G5′ — hygiene, rule 11 (satisfiability) and rule 12 (source-object naming)

**Rule 12 compliance header** (also carried verbatim at the top of the
script). Every manipulated object named by generator source object:

| object | source object | used by |
|---|---|---|
| occasion-common channel | `common_part` = √w_x·a·(((√κ·`shock_x`)·g)@Lᵀ); `shock_x` built at **f2:184-193** from `occasion_labels` (**f2:180**) and `shock_vector` (**f2:120-126**); blend split at **f2:195** | A1 removes it exactly (oracle de-framing reference); A4 subtracts an ESTIMATED stand-in |
| author MEAN channel | `mean_part` = √w_mu·a·((z·g)@Lᵀ), **f2:178** | A5 (shared) and A6 (free) remove it exactly — the channel of Δ0′ |
| author AR state | `x`, **f2:151-177** (init f2:173, recursion f2:175-176, φ f2:171), entering as the √(1−κ) half of **f2:195** | not manipulated by any arm; G4′ second reading only |
| design | `occasion_mode`, **f2:180** | A0/A5/A4/A1 shared; A2/A6 free |

**Hygiene.** master_seed **20260813**; seed recipe
`v8.stable_bucket(f'{MASTER_SEED}-{group}-w{world}-{knob_tag}',
salt='m4k1c-world', modulus=2**63-1)` — K1c's recipe verbatim, with
`MASTER_SEED` the single changed input, so every arm of a world shares one
world seed and design contrasts are exactly paired. Groups: `main` 0–127,
`pilot` [9401, 9402] (reserved), `abs` 0–7. A4 norm pool:
`stable_bucket(f'{world_seed}-normpool', salt='m4k1c-normpool')`. Bootstrap
seeds listed per statistic in `manifest.json`. All stages foreground with
explicit timeouts; **zero background jobs, zero monitors, zero
sleep-and-poll**. Python 3.14.3 / numpy 2.4.4 / pandas 3.0.2 / scipy 1.17.1.

**Rule 11 — all fourteen CI/magnitude clauses of the K1c′ registration,
checked at the FRESH pilot sd before arms. Thirteen satisfiable; ONE
UNSATISFIABLE at the fresh pilot point, and it is disclosed here in advance
of any adjudication.**

| registered clause | half-width at fresh pilot sd (n=128) | reference | satisfiable |
|---|---|---|---|
| G1′: Δ0 CI overlaps F2's κ=0.5 CI | 0.000899258514224337 | overlap is monotone-easier in width | ✔ (unconditionally) |
| L-1: (Δ0−Δ0′) CI excludes 0 | 0.0006572704375494232 | fresh pilot point −0.015120940127848037 | ✔ |
| L-1: Ŝ_auth > 0 | — | sign clause, no interval | ✔ |
| L-2: \|A6−A2\| CI inside ±0.004418076848551262 | 0.0006592944786118607 | margin | ✔ |
| L-3 applicability: R_or CI excludes 0 | 0.0003935769237074436 | fresh pilot point 0.0009610293520168323 | ✔ |
| **L-3: R_est CI excludes 0** | **0.0005679658784305253** | **fresh pilot point −0.0003999071796674143** | **✘ at the fresh n=2 point** |
| — same clause, second reference | 0.000809411049756907 | K1c's inherited n=8 pilot point 0.004051794736468588 | ✔ |
| L-3: pooled R_est/R_or ≥ 0.5 | — | fresh pilot ratio −0.4161237935429989 (n=2) | ✔ (magnitude clause) |
| L-4: reader-A′ (est8−oracle) CI upper < +0.005 | — | K1b anchor −0.06230964467005076, CI [−0.07106916243654822, −0.05418781725888325] | ✔ |
| L-4: oracle stability < 0.01 | — | K1b anchor move 0.0025380710659898 | ✔ |
| G2′: A5-vs-A6 panel RMS > 1e-6 | — | measured min 0.06923291177968123 | ✔ |
| G3′: MDE(n=128) ≤ 0.004418076848551262 | — | inherited 0.0021362771506247724 / fresh-sd 0.0009377603985145934 | ✔ |
| G4′: liveness ratio > 1 at every fresh pilot world | — | measured 2.855–2.865 | ✔ |
| P2′: (Δ0−Δ0′) CI upper < 0.25 × Δ0 point | — | pilot CI upper est. −0.014463669690298614 vs bound −0.00014220531980969962 | ✔ (reachable) |
| rule 1: signs clean ≥ 104/128, qualified ≥ 85/128 | — | counting clause | ✔ |

**Register-note R-0.4 (rule 11's finding, stated before arms).** The one
unsatisfiable clause is **L-3's "R_est CI excludes 0"** *at the fresh
two-world pilot point*: |−0.00040| < half-width 0.00057. It is reported at
both available references, and at K1c's inherited eight-world pilot point
(0.004051794736468588, half-width 0.000809) the same clause is comfortably
satisfiable. **An n = 2 point estimate of a small quantity is not a sound
basis for declaring a registered clause unreachable**, so the clause is NOT
pre-emptively voided; it is flagged here so that, whichever way L-3 lands, the
reader knows the resolution question was on the record before the arms ran.
Note also that the fresh pilot's R_or point is only 0.00096 (n=2) — if the
128-world R_or CI does not exclude 0, **L-3 is INAPPLICABLE by its own
registered condition**, and that possibility is likewise on the record now.

**G5′ PASS.**

### Part-0 register-notes (fixed before any main arm)

**R-0.5 — where G1′ sits in the stage order.** The registration lists G1′
among the Part-0 gates, but Δ0 is defined on the 128 `main` worlds, so G1′ is
not computable until `arms_a` has run. Resolved: Part 0 = G0′, G2′, G3′, G4′,
G5′ (all on reserved seeds, all written above before any main arm); then
`arms_a` (A0, A2 × 128); then **G1′ as a hard gate before `arms_b`**, enforced
in code — `arms_b` raises unless `gates.json` records `G1'.pass == true`, and
every arm stage raises unless `G2'.pass == true` (`_require_g2p_pass`). There
is no flag to override either.

**R-0.6 — arms, machinery and the fresh-seed lever.** All six arms
(A0/A2/A5/A6/A4/A1) and the entire secondary reader path were already
implemented in `scripts/run_suica_m4_k1c_ownership_live_knob.py` and were
never run on an adjudicated world. This leg imports them and changes exactly
one thing: `k1c.MASTER_SEED` 20260812 → **20260813**, applied in every process
(parent and each `ProcessPoolExecutor` child) at module-load time. Seed salts,
corpus tags, budget label, the A4 norm-pool construction, the channel mirror,
the bootstrap machinery and the secondary reader are inherited **verbatim**.
Fresh-seed check: `main` world 0 seed is **7930912223678171078** here versus
**3936073819076212475** in K1c.

**R-0.7 — A4's estimated norm at a live-AR knob.** Inherited from K1c's R-0.3
unchanged: the disjoint pool's idiosyncratic content is `mean_part + ar_part +
noise_part` with the panel's own C(c,o) (carrying its √κ factor) substituted
for the pool's occasion channel, which reduces bit-exactly to K1b's
construction at κ=1.0. |P| = 32 authors **per context** (4 contexts).

**R-0.8 — L-3's ratio grain.** "pooled R_est/R_or" is the ratio of pooled
means, mean(A0−A4)/mean(A0−A1), bootstrapped paired over worlds — K1b's and
K1c's own operationalization, inherited.

**R-0.9 — the secondary's two disjoint sub-pools.** T6″ v2 runs on 8 `abs`
worlds with a 1024-author norm pool split into two disjoint 512-author halves;
reader A takes gallery and probe norms from the same half, reader A′ takes them
from different halves (frame refreshment). est8 is the first 8 authors of a
half. Inherited verbatim from `k1c.run_sec_world`.

**Part-0 stage estimates, for the registration's stop-at-2× rule:** `part0`
≤ 180 s (actual **15.273 s**); `arms_a` ≤ 500 s; `gate_g1p` ≤ 60 s; `arms_b`
≤ 900 s; `sec` ≤ 400 s; `finalize` ≤ 120 s. Any stage exceeding 2× its
estimate stops the leg and is reported.

---

## 1. Outcome

**Verdict slug:**
`NO_AUTHOR_READING_SHARE_AT_THE_LIVE_KNOB__AUTHOR_DELETION_ENLARGES_THE_COMPOSITION_EFFECT__FREE_SIDE_SPECIFIC__DEFRAMING_REPAIR_DEPLOYABLE_0p73__T6dd_V2_HOLDS__P2PRIME_FIRES`

**HEADLINE. At the live-author knob the composition effect does not merely
survive author deletion — deleting the author channel nearly DOUBLES it
(Δ0′/Δ0 = 1.9443843417103448), so the author-reading share is
Ŝ_auth = −0.9443843417103447 [−1.2340432099315712, −0.7045965411263232].
That is, to three decimals, K1b's κ=1.0 value (−0.9487481378268351
[−1.1584, −0.7532]) — measured on a knob where the author channel is
objectively live (author-mean liveness ratio 2.855–2.865, AR-state ratio
1.082). L-1 MISSES and P2′ FIRES, in a form STRONGER than the pivot's own
wording: the author-reading share is not "bounded below 25 %", it is bounded
below ZERO.**

### Gates

| gate | verdict |
|---|---|
| G0′ inheritance anchors | **PASS** — all seven bit-exact (after the round-trip parsing rule, R-0.2) |
| **G1′ replication** | **PASS** — Δ0 = **0.007448566560020627**, boot CI **[0.006337565267918393, 0.008585684601869065]**, wholly INSIDE F2's κ=0.5 CI [0.004418364530893362, 0.013253942863311687]; paired-t CI [0.006288628975045103, 0.008608504144996152] agrees; signs 106/128 positive, band **clean** |
| G2′ non-degeneracy (rule 10) | **PASS** — A5-vs-A6 panel RMS 0.06929976550687832 / 0.06923291177968123 vs a 1e-6 bar |
| G3′ power (rule 2) | **PASS** — controlling MDE 0.0021362771506247724 (two-sided 2× band missed at ratio 0.439; fallback executed, fresh-sd MDE 0.0009377603985145934, both inside the 0.004418076848551262 bar) |
| G4′ liveness (rule 3) | **PASS** — author-MEAN ratio 2.8552376916466695 / 2.864645232241155, > 1 at 2/2 |
| G5′ hygiene + rules 11, 12 | **PASS** — 13/14 clauses satisfiable, the one flag disclosed in advance (R-0.4) and later satisfied in fact |

### Arms (128 worlds, 768 deployed-gauge runs, 565 authors retained per run)

| arm | construction | pooled agreement |
|---|---|---|
| A0 | shared, intact | 0.01077241982344781 |
| A2 | free, intact | 0.003323853263427182 |
| A5 | shared, `mean_part` (f2:178) deleted | **0.015111086166526903** |
| A6 | free, `mean_part` deleted | **0.0006282099790355089** |
| A1 | shared, `common_part` removed exactly — oracle de-framing reference | 0.004587139851428791 |
| A4 | shared, ESTIMATED per-(context, occasion) subtraction, \|P\|=32/context | 0.006227786063060049 |

### Primary quantities

| quantity | pooled | 95 % bootstrap CI (2000 paired draws) | signs | band |
|---|---|---|---|---|
| Δ0 = A0−A2 | 0.007448566560020627 | [0.006337565267918393, 0.008585684601869065] | 106+/22− | clean |
| Δ0′ = A5−A6 | **0.014482876187491394** | [0.013223715021599436, 0.01581035481469913] | **127+/1−** | clean |
| Δ0 − Δ0′ | **−0.007034309627470767** | [−0.008163458312738956, −0.005873004730301863] | 20+/**108−** | clean |
| **Ŝ_auth = (Δ0−Δ0′)/Δ0** | **−0.9443843417103447** | **[−1.2340432099315712, −0.7045965411263232]** | — | — |
| R_or = A0−A1 | 0.0061852799720190175 | [0.005177265953630964, 0.007144206387567167] | 109+/19− | clean |
| R_est = A0−A4 | 0.004544633760387759 | [0.003502130735750378, 0.005619815780497545] | 94+/34− | qualified |
| R_est/R_or | **0.7347498869811525** | [0.6376184714475329, 0.820668361509718] | — | — |
| A5−A0 (shared side) | +0.004338666343079094 | [0.003181212764783094, 0.005525751177585165] | 92+/36− | qualified |
| A6−A2 (free side) | −0.0026956432843916727 | [−0.003871657497627448, −0.0015998336172598471] | 38+/90− | qualified |

**Decomposition identity, verified:** (Δ0 − Δ0′) = −[(A5−A0) + (A2−A6)] to
**3.469446951953614e-18** across all 128 worlds. The gap is exactly the sum of
two effects that point the same way: deleting the author-mean channel **raises**
shared agreement by +0.00434 (92/128) **and lowers** free agreement by −0.00270
(90/128).

### Leans

| lean | prior | rule | verdict |
|---|---|---|---|
| **L-1** an author-reading share exists | .35 | (Δ0−Δ0′) CI excludes 0 **with Ŝ_auth > 0** | **MISS** — the CI excludes 0 decisively, but on the WRONG SIDE (Ŝ_auth = −0.944) |
| **L-2** free-side author-deletion specificity | .70 | \|A6−A2\| CI inside ±0.004418076848551262 | **HOLD** — CI [−0.00387, −0.00160] inside the margin |
| **L-3** deployable de-framing at the live knob | .80 | R_est CI excludes 0 **and** R_est/R_or ≥ 0.5; applicable only if R_or CI excludes 0 | **HOLD** (applicable: R_or CI excludes 0) — ratio 0.735 [0.638, 0.821] |
| **L-4** T6″ v2 (sign form) | .80 | under A′, est8−oracle ≤ 0, CI upper < +0.005, oracle stability < 0.01 | **HOLD** — see below |

**L-2, stated precisely (rule 4).** The equivalence HOLDS: the free-side
response to author deletion lies inside the registered materiality margin.
It is **not** zero — the CI excludes 0 at −0.0027, and the sign band is
*qualified* (90/128), not clean. Author deletion measurably lowers free-design
agreement; the claim licensed is that it does so **immaterially**, which is
what the registered equivalence form asks and all it licenses.

**L-3, and a κ-dependence worth recording.** The estimated per-occasion
subtraction recovers **73.47 %** [63.76 %, 82.07 %] of what oracle
common-removal recovers at κ=0.5, against K1b's **94.39 %** [90.23 %, 98.79 %]
at κ=1.0 — non-overlapping intervals. The repair is still deployable and still
**UNADOPTED** under F16 discipline (changing the frozen gauge is a new-operator
event with its own study ID and seal); it queues beside `colstd_alpha_0.10`
exactly as before, now with a knob-dependent efficacy figure attached.

### Secondary — T6″ v2 (L-4), 8 `abs` worlds, κ=0.5, 985-author panels

| reader | oracle rank-1 | est8 rank-1 | est8 − oracle, pooled (author-stratified bootstrap) | worlds positive |
|---|---|---|---|---|
| **A** (same 512-author half for gallery and probe norms) | 0.3805837563451777 | 0.4352791878172589 | **+0.05469543147208122** [0.04809644670050761, 0.06142131979695432] | **8/8** |
| **A′** (frame-refreshed: disjoint 512-author halves) | 0.3786802030456853 | 0.292005076142132 | **−0.0866751269035533** [−0.09517766497461928, −0.07778870558375636] | **0/8** |

Oracle stability |rank1(A′) − rank1(A)| = **0.0019035532994924331** < 0.01.
CI upper bound under A′ = −0.07778870558375636 < +0.005. Readability follows
the same inversion (est8 0.4445 → 0.3670; oracle 0.4013 → 0.3999).
**L-4 HOLDS. P3′ does not fire.** This is T9's forgery signature and its
licensed counter-operation, reproduced at the live knob and LARGER than K1b's
κ=1.0 measurement (−0.0623): a reader that shares its frame with the gallery
*profits* from a cheap 8-author norm; refresh the frame and the same norm
inverts into an honest issuer penalty, while the oracle barely moves.

### Pivots

| pivot | fires |
|---|---|
| P1′ (G1′ fails → VOID on non-replication) | no — Δ0 replicates, CI wholly inside F2's |
| **P2′ (L-1 MISS with (Δ0−Δ0′) CI upper < 0.25 × Δ0 point)** | **YES** — CI upper **−0.005873004730301863** < bound **0.0018621416400051568** |
| P3′ (L-4 fails → T6″ v2 dead) | no — L-4 HOLDS |
| P4′ (G2′ fails → STOP) | no — non-degenerate by five orders of magnitude |

**P2′'s registered consequence is the planner's to execute; the executor only
reports that the antecedent is satisfied — and satisfied more strongly than
the pivot's own wording anticipates.** The pivot text reads "author share
bounded below 25 % at the live knob". Measured: the share is bounded below
**zero**, with a CI upper bound of −0.70. The registered consequence — the
retrospective widening WITH the family lemma ("in this world family the
composition effect carries no material author-reading share at any tested
knob, and the jurisdiction-alignment channel for person-specific state does
not exist in the family by construction; the D3 'recruit authors' prior
survives only as frame-readout economics"), and the F4/F5 review on K1c's
G4c-info facts becoming the next registration — is therefore reached on a
stronger antecedent than it was written for.

### What the leg establishes

1. **The κ=1.0 attribution was not a κ=1.0 artefact.** K1b measured
   Ŝ_auth = −0.9487481378268351 at a knob where M4-F7 had already shown the
   author state inert. This leg measures **−0.9443843417103447** at a knob
   where the author channels are objectively live (G4′: author-mean ratio
   2.855–2.865, AR ratio 1.082, both > 1 at 2/2 fresh worlds; K1c's inherited
   8-world bands agree). The two intervals overlap almost entirely. **Author
   liveness in the WORLD does not buy the composition effect any author
   content in the GAUGE.**
2. **The measurement is gauge-level by construction, and that is the point.**
   A5 = shared − `mean_part` and A6 = free − `mean_part` subtract the same
   design-invariant object, so (A5−A6) ≡ (A0−A2) *as panels* — verified
   bit-identical at both fresh pilot worlds. Δ0 − Δ0′ is therefore purely the
   deployed nonlinear map's response to author content, and it is large,
   negative and clean (108/128).
3. **Author content is a net DRAG on the composition contrast, on both sides
   and for different reasons.** Deleting it raises shared agreement (+0.0043,
   92/128) and lowers free agreement (−0.0027, 90/128); the two add to the
   whole gap to 3.5e-18.
4. **The de-framing repair is deployable at the live knob but weaker there**
   (73.5 % vs 94.4 % at κ=1.0, non-overlapping) — a κ-dependence that did not
   exist in the record before.
5. **T6″ v2 survives its confirmatory test at the live knob with a larger
   inversion than at κ=1.0** (−0.0867 vs −0.0623), with the oracle stable to
   0.0019.

### Anomalies, with timing

- **A-1 (executor instrument fix; both invocations BEFORE any main arm, on
  reserved seeds only).** The `part0` stage was invoked twice: 06:03:10–06:03:26
  UTC and 06:06:01–06:06:17 UTC. The first returned **G0′ FAIL** — the
  inheritance anchors reproduced only to ~2e-15 relative, not bit-exactly.
  Cause diagnosed as pandas 3.0.2's default CSV float parser (R-0.2), not a
  substantive discrepancy. Three Part-0-only changes followed: round-trip
  parsing everywhere, the conservative controlling-MDE rule (R-0.3 iii), and
  the second reference on L-3's rule-11 clause (R-0.4). **Both invocations
  touched only reserved pilot worlds 9401–9402 (12 gauge runs each, 24 total
  on reserved seeds); no main world, no `abs` world, and no
  hypothesis-relevant number existed at either point.** The report's Part 0
  was written after the second invocation and before `arms_a` (06:08:41).
- **A-2 (registered clause missed in Part 0, before any main arm).** G3′'s
  "fresh pilot sd within 2× of K1c's" MISSES on the two-sided reading
  (ratio 0.43896944656283826 < 0.5) because the fresh sd is *smaller*. The
  registration's own fallback was executed and passes on every reading; the
  larger, inherited MDE was adopted as controlling.
- **A-3 (rule 11 flag, raised before arms, later falsified by the data).**
  One of fourteen clauses — "L-3: R_est CI excludes 0" — was unsatisfiable at
  the fresh two-world pilot point (|−0.00040| < hw 0.00057). R-0.4 declined to
  treat an n=2 point as decisive and recorded the n=8 second reference. At 128
  worlds R_est = 0.004544633760387759 with CI [0.00350, 0.00562] — the clause
  was satisfiable in fact, and L-3 HOLDS.
- **A-4 (disclosure, not a deviation).** L-2's equivalence HOLDS while its
  underlying CI excludes zero, and its sign band is *qualified* (90/128), not
  clean. Recorded so the claim is not over-read as "no free-side effect".
- **A-5 (planner registration-text inaccuracy; detected in Part 0).** G0′'s
  anchors are said to live in K1c's `decision.json`; two of the three families
  live in `gates.json` (R-0.1). Recorded, not repaired; the gate was satisfied
  in a stronger form.
- **No result fell outside a registered branch.** Every lean, gate and pivot
  resolved to a registered outcome; the only over-delivery is P2′'s antecedent
  being satisfied more strongly than its own text anticipates.
- **No background jobs, no monitors, no smoke runs, no stage over its Part-0
  estimate.** Longest stage `arms_b` 516.877 s against a 900 s estimate; the
  2× stop-and-report rule never engaged.

### Artifacts

- script `scripts/run_suica_m4_k1c_prime_author_share.py`
- `results/m4_k1c_prime_author_share/manifest.json`, `gates.json`,
  `pilot_cells.csv` (12 reserved-seed gauge runs), `g4p_liveness.csv`
  (2 worlds), `arms_a.csv` (256 runs), `arms_b.csv` (512 runs),
  `sec_cells.csv` + `sec_probe_correct.npz` (8 worlds × 2 arms × 2 readers),
  `decision.json`
- stage wall-times: `part0` 15.274 s, `arms_a` 260.244 s, `gate_g1p` 0.020 s,
  `arms_b` 516.877 s, `sec` 1.265 s, `finalize` 0.263 s — **793.9 s total**
  (≈13.2 min), plus the discarded first `part0` invocation (~16 s), all
  foreground. **768 adjudicated deployed-gauge runs** on 128 fresh worlds,
  plus 24 on reserved Part-0 seeds.

**Claim boundary.** Synthetic throughout; a decomposition of a synthetic
composition effect in a world calibrated to the opened PANDORA D-panel regime,
read through the deployed frozen machinery. Licenses IDT grammar (typing rules
and design priors) only. No claim about any corpus, construct, person, or
diagnosis. No seal, no independent verification (open-exploration phase rules).
