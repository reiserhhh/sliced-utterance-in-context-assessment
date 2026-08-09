# SUICA M4-K-R1 — The constructive repair test: does de-framing make the reader a better TRAIT instrument?

Registration: `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md` section "M4-K-R1 — The
constructive repair test" (REGISTERED 2026-08-09, BEFORE RUN, commit `fa19b1e`),
binding, unedited. Theory: `docs/SUICA_IDENTITY_THEORY_V1.md` appendix L (T4's
closed form `field ~ lambda*r^q - kappa*V_person - eps_species`) and appendix
D.2/D.4 (T9's counter-operations; the certified-but-unadopted de-framing
repair). Script: `scripts/run_suica_m4_kr1_deframing_repair.py`. Artifacts:
`results/m4_kr1_deframing_repair/` (gitignored).

Tier: EXPLORATORY, label-free, synthetic throughout. Banner: *synthetic worlds
calibrated to an opened-panel regime, exploratory*. Nothing here is a claim
about persons; every statement is a law about an instrument–world pair.

Executor standing: implementation and execution only.

---

## Part 0 — gates computed 2026-08-09T11:59:09.281220+00:00 (UTC), written to disk BEFORE any main arm

Part-0 stage wall-time 81.999 s (G0r anchors 0.044 s, 4-world pilot 27.357 s,
G4r 13.110 s, the three rule-9 second readings 41.458 s). No main world index
existed when this section was written. No background jobs, no monitors; every
stage foreground and chunked.

### 0.0 Standing-rule-14 self-check (required by G5r)

Every gated quantity in this leg is **recovery vs recovery on the same
instrument at the same scale**: `d_a = recovery_deframed(a) −
recovery_intact(a)`, both produced by `e1.field_agreement` (e1:245-258) against
the same intact b-only truth field, in the same units, on the same paired
worlds. The margin `m_rec = 0.010` and the MDE target live in that same
recovery scale. **No gate and no lean in this leg compares across scales or
instruments**, so rule 14's first clause is not engaged and its second clause
(re-design to be within-instrument) is satisfied by construction. The
`(Δλ, Δq, Δκ)` parameter story *is* cross-scale in content — a card-space
attenuation enters as the regressor — and is therefore reported as
**DESCRIPTIVE with CIs and NO gate**, exactly as the registration words it.

### 0.1 Design as registered, and the register-notes (standing rule 9)

`master_seed 20260821`; 32 worlds per cell; 12 cells = K2b's six state arms
A1..A6 (identical solved shares, taken from `k2b:97-105`) × {G-intact,
G-deframed}. Reserved pilot worlds 9601–9604, disjoint from main indices 0..31.
`B = 2000`, seed = master; `B = 20000` for rule 13. Per cell: b-only field
recovery, mixed recovery (descriptive), card channel.

The registration left four conventions open. Each is pinned here **before any
hypothesis-relevant number existed**, by written rule, and **all readings are
reported** (§0.6).

- **RN-2 — the truth object stays INTACT under G-deframed (PRIMARY).** The
  estimand is the trait field, held fixed across gauge variants; the de-framing
  hook acts on the gauge's *observed* input path only. Justification is
  measured, not asserted: K2b's own G4b recorded that the strict trait-only
  panel's field has maximum context norm `0.0006675856745354268` against the
  b-only panel's minimum `0.15214367930549447`, and that its recovery is
  `−0.024495680267977205` (noise). De-framing a b-only truth panel
  (`w_mu*trait + w_c*common`) leaves `w_mu*trait` minus a donor residual — i.e.
  that degenerate object — so a both-panels reading would measure a
  truth-object collapse, not a reader property. SECOND READING
  (`deframe_truth=True`) reported in §0.6.
- **RN-2b — disclosed, not a choice.** `calibrate_d0_soft` is fitted on
  whatever the operator observes (k2b:679), so under G-deframed the intact
  truth panels are mapped through the de-framed calibration. The truth field is
  therefore *not* bit-identical across variants; the induced difference is
  measured (§0.5) and reported.
- **RN-3 — the donor channel list is K1b's, literally (PRIMARY
  `k1b_literal`).** k1b:296 builds the donor average out of the pool's
  `mean_part + noise_part`: the donors' entire occasion channel is dropped and
  the panel's common vector put in its place (k1b:303-306). In K1b's family the
  occasion channel at κ=1.0 *is* the common channel. The expressive world's
  `slow` and `int` are occasion-channel members with no K1b counterpart, so the
  literal transcription is `donor = w_mu*trait + w_e*noise` plus the panel's
  `w_c*common(c,o)`. SECOND READING (`expressive`: donors also carry their own
  slow state) reported in §0.6. `w_int = 0` in all six arms, so the two
  readings differ by the donor slow-state term alone.
- **RN-5 — one 32-donor block per CONTEXT, read at every occasion (PRIMARY
  `per_context`).** k1b:299-306 holds the block fixed per context, so the donor
  trait error is a per-context constant. SECOND READING (`per_occasion`: a
  fresh disjoint 32-donor block for every `(context, occasion)`) reported in
  §0.6.
- **RN-4 — the corpus tag is VARIANT-INVARIANT.** `f1.featurize_panel`
  (f1:166-229) seeds its transition-null permutation streams per
  `(corpus, author, offset)`; a variant-dependent tag would change the null
  draws and destroy the pairing. The tag is `m4kr1-<arm>-w<world>` — arm and
  world only, as K2b's was (k2b:673).
- **RN-6 — the world seed depends on the WORLD INDEX ONLY** (K2b's RN-8
  convention at this leg's salt `m4kr1-world`), so both gauge variants and all
  six arms share trait, slow innovations, frame shocks and noise bit-for-bit:
  the intact-vs-deframed contrast is exactly paired.
- **RN-7 — t-quantiles come from scipy, not a hard-coded table.** K2b's
  `t_{.80,31}` constant was `+1.0e-04` off (planner note A-1 under rule 15);
  this leg uses `scipy.stats.t.ppf` throughout.

**Disclosed single-object patch (the K1/K2b precedent).**
`k2d.install_species_weights()` (k2d:206-238) is installed because
`k2e.rederive_anchors` requires it for the K2c/K2d/K2e arms' interaction
shares. It **delegates verbatim** for the `"zero"` arm all six of this leg's
arms use; `k2d.verify_species_weights()` proves that bit-exactly over its
8-point share grid — `zero_arm_bit_exact_after_patch = True`,
`int_zero_route_equals_zero_arm_bit_exact = True`, equal-arm maximum absolute
deviation `2.7755575615628914e-17`.

### 0.2 G0r — anchors, bit-exact: **PASS**

Criterion: every anchor named by G0r re-derived **bit-exactly** (residual
`== 0.0`) from persisted artifacts under round-trip parsing.

| anchor | persisted | re-derived | residual | bit-exact |
|---|---|---|---|---|
| K2b A1 b-only recovery | 0.177888649457317 | 0.177888649457317 | 0.0 | yes |
| K2b A2 b-only recovery | 0.1506896317900927 | 0.1506896317900927 | 0.0 | yes |
| K2b A3 b-only recovery | 0.10962256916514518 | 0.10962256916514518 | 0.0 | yes |
| K2b A4 b-only recovery | 0.07543949574114414 | 0.07543949574114414 | 0.0 | yes |
| K2b A5 b-only recovery | 0.11574817692039557 | 0.11574817692039557 | 0.0 | yes |
| K2b A6 b-only recovery | 0.06918364030560309 | 0.06918364030560309 | 0.0 | yes |
| K2b λ | 0.17417497661611914 | 0.17417497661611914 | 0.0 | yes |
| K2d 19-arm q | 1.8528700746510731 | 1.8528700746510731 | 0.0 | yes |
| K2e 6-pair κ̂ | −0.7220359963712748 | −0.7220359963712748 | 0.0 | yes |
| K1c′ R_est/R_or | 0.7347498869811525 | 0.7347498869811525 | 0.0 | yes |

Routes: the six recoveries are round-trip re-reads of
`results/m4_k2b_t4_branch/arm_<a>_field.csv` meaned over K2b's 8 worlds and
compared with its `decision.json`; λ, q and κ̂ come through
`k2e.rederive_anchors()` (k2e:596-745) called **unmodified**, whose own
`all_bit_exact` is `True` (it also re-derives K2c's three D_k with CIs and
K2d's six-pair κ companion); K1c′'s ratio is `mean(A0−A4)/mean(A0−A1)` over its
128 worlds from `arms_a.csv`/`arms_b.csv` (k1c′:999-1003). K2e's 25-arm q
(appendix L's headline) is quoted at `1.8327227969464843
[1.7109560851209855, 1.9795061744015678]`; the 9-pair κ companion at
`−0.7145934082034173`.

**Extra anchor (this leg's own):** the six Part-0 card predictions recomputed
through `k2b.arm_predictions` match K2b's persisted `part0_predictions.csv` at
residual `0.0` on `r_card_b_pred_raw`, `gap_pred`, `rho_interleaved_pred` and
`rho_contiguous_pred`. Predicted attenuations (the regressor for q, and
variant-invariant by G2r): A1 `0.8271784593117322`, A2 `0.7849057220233866`,
A3 `0.6758917867864564`, A4 `0.558364277337817`, A5 `0.645057248597175`,
A6 `0.5193517935368367`.

### 0.3 G2r — designed invariance of the CARD channel (rule 10): **PASS**

Criterion: the card channel is **bit-identical** across gauge variants —
SHA-256 of the float64 numeric block equal in every cell **and** maximum
absolute column-sum difference `== 0.0`. Any difference is an implementation
defect and STOPS the leg.

Pilot result: 24/24 cells (6 arms × 4 pilot worlds) SHA-256-equal;
`max_abs_sum_diff = 0.0`; `max_abs_gap_diff = 0.0`. Structurally the card
channel (k2b:381-457) is a function of the world channels and the arm weights
only and never touches the gauge's input path; the byte check is a **defect
detector for accidental coupling** (in-place mutation of the world by the
de-framing path), and in the main run the card frame is deliberately recomputed
*after* each variant's gauge run so such a mutation would surface. The same
check is re-run over all 12 main cells at finalize and is a STOP condition
there.

### 0.4 G4r — de-framing liveness (rule 3): **PASS**

(i) The subtraction moves the gauge's input panels in **every** arm. Per-arm
RMS of `panel_intact − panel_deframed` (mean over the 4 pilot worlds), against
the intact panel's own RMS:

| arm | de-framing RMS | intact panel RMS | ratio |
|---|---|---|---|
| A1 | 0.0727299047176135 | 0.17651075161560004 | 0.41204234898961034 |
| A2 | 0.07009115476156356 | 0.1765075789117773 | 0.39709997266801106 |
| A3 | 0.06301378524681472 | 0.17652907359534603 | 0.3569598138336121 |
| A4 | 0.0550361719360779 | 0.17656334001548002 | 0.31170780939719794 |
| A5 | 0.06301378524681472 | 0.1765498866543398 | 0.35691773266434873 |
| A6 | 0.0550361719360779 | 0.17660031695430886 | 0.3116425433727687 |

Minimum per-world RMS over all arms `0.05427195663608337 > 0`.

(ii) **The F2-composition collapse, through K1b's own machinery.** K1b's A0
(shared, intact), A1 (shared, ORACLE common removal) and A4 (shared, ESTIMATED
per-(context, occasion) norm from 32 disjoint authors) were re-run at world 0
through `k1b._arm_world` / `k1b.arm_task` **unmodified** and reproduce K1b's
persisted per-world rows **bit-exactly**: A0 `0.008037373438839491`, A1
`−0.006087038691756484`, A4 `−0.0038127992738790474`, all residuals `0.0`. At
that world `R_or = 0.014124412130595974`, `R_est = 0.01185017271271854`, ratio
`0.8389851983325359` — collapse directionally intact, and between K1c′'s pooled
`0.7347498869811525` (κ=0.5) and K1b's pooled `0.943890194474869` (κ=1.0).
Descriptive, as registered; a single world is not a pooled estimate. What this
buys is stronger than consistency: it proves the object this leg transcribes
**is** K1b's A4 construction, invoked through K1b's own code.

(iii) **RN-2b measured.** The intact b-only truth field mapped through the two
variants' calibrations differs: maximum absolute entry difference
`0.007537607590715613`, minimum matrix cosine `0.6823271962928399` over
6 arms × 4 pilot worlds. Disclosed; the recovery in each variant is always a
cosine between two fields the *same* calibration produced.

### 0.5 G1r — power (4-world pilot, ≥4 worlds per rule 16's convention): **PASS**

`MDE(80%, α=.05, paired, n) = (t_{.975,n-1} + t_{.80,n-1}) · sd_pilot(d_a)/√n`,
scipy quantiles. Registered target: `MDE ≤ 0.010` for `d_a`; escalate 32→64
once; still short → run and tier.

| arm | pilot d (4 worlds) | sd(d) | MDE n=32 | MDE n=64 | meets 0.010 at 32 |
|---|---|---|---|---|---|
| A1 | −0.155460, −0.158640, −0.167097, −0.184600 | 0.0130588854 | 0.0066782413 | 0.0046452196 | yes |
| A2 | −0.117654, −0.137755, −0.158063, −0.154969 | 0.0185912964 | 0.0095074854 | 0.0066131683 | yes |
| A3 | −0.101658, −0.086767, −0.115492, −0.121242 | 0.0153932685 | 0.0078720317 | 0.0054755903 | yes |
| A4 | −0.064505, −0.057144, −0.081884, −0.079594 | 0.0119204192 | 0.0060960359 | 0.0042402505 | yes |
| A5 | −0.112008, −0.101925, −0.123267, −0.114265 | 0.0087673237 | 0.0044835605 | 0.0031186545 | yes |
| A6 | −0.077025, −0.052448, −0.080724, −0.083043 | 0.0141269054 | 0.0072244207 | 0.0050251249 | yes |

Worst-case MDE at n=32 is `0.009507485400921578 ≤ 0.010` in every arm:
**n = 32 selected, no escalation, no tiering.**

**Pilot sign disclosed before the arms (rule 9 timing):** all six pilot `d_a`
are NEGATIVE and 15–37× the projected half-width. No design element was changed
in response; the registration's adjudication object, margins, priors, precedence
and routing are untouched. The pilot's own per-cell recoveries (mean over the
4 pilot worlds) were: intact 0.173295 / 0.158373 / 0.118057 / 0.076685 /
0.128041 / 0.088045 and de-framed 0.006846 / 0.016263 / 0.011768 / 0.005904 /
0.015175 / 0.014735 for A1..A6.

### 0.6 Rule-9 second readings (all reported; none gating)

Each alternative convention was run on the same 4 pilot worlds, all 6 arms,
against the same intact-variant baseline. `d` is the reading's own
intact-vs-deframed difference; "shift" is `d − d_primary`.

| reading | arms with the same sign as PRIMARY | max abs shift vs PRIMARY | range of d |
|---|---|---|---|
| RN-3 `donor_channels=expressive` (donors carry their own slow state) | 6/6 | 0.000897 | −0.166035 … −0.071219 |
| RN-5 `pool_scheme=per_occasion` (fresh 32 donors per occasion) | 6/6 | 0.012476 | −0.176191 … −0.079085 |
| RN-2 `deframe_truth=True` (de-frame the truth panels too) | 6/6 | 0.039393 | −0.139650 … −0.031389 |

(RN-3 per arm: A1 −0.166035, A2 −0.141890, A3 −0.105393, A4 −0.071219,
A5 −0.112531, A6 −0.073355. RN-5: A1 −0.176191, A2 −0.152339, A3 −0.117423,
A4 −0.079085, A5 −0.123431, A6 −0.085786. RN-2: A1 −0.139650, A2 −0.120961,
A3 −0.076021, A4 −0.031389, A5 −0.089172, A6 −0.035695.)

**Every open convention gives the same sign in every arm.** The primary
convention is not the most extreme one (RN-5 is), nor the least (RN-2 is), and
the largest disagreement between any two readings, 0.039393, is smaller than
the smallest primary effect, 0.070782. The leg's verdict does not turn on any
rule-9 choice.

### 0.7 G3r — rule-11 satisfiability with directions, and the rule-13 spec: **PASS**

Resampling: ONE pick matrix `default_rng(20260821).integers(0, 32, (2000, 32))`
shared by every arm and BOTH gauge variants, so `d_a` is resampled paired.
Rule 13: every interval clause is re-checked at `B = 20000` when the boundary
(0) lies within 2× the Monte-Carlo sd of the relevant CI endpoint; a verdict
flip scores the clause BOUNDARY.

| clause | direction | satisfiable | note |
|---|---|---|---|
| `d_A1` 95% CI vs 0 | two-sided CI; the sign of the excluded interval assigns the cell | yes | pilot sd 0.0130588854; projected half-width at n=32 0.0045246730; pilot abs d 36.787× that half-width |
| `d_A2` 95% CI vs 0 | as above | yes | sd 0.0185912964; hw 0.0064415556; 22.061× |
| `d_A3` 95% CI vs 0 | as above | yes | sd 0.0153932685; hw 0.0053334954; 19.929× |
| `d_A4` 95% CI vs 0 | as above | yes | sd 0.0119204192; hw 0.0041302145; 17.138× |
| `d_A5` 95% CI vs 0 | as above | yes | sd 0.0087673237; hw 0.0030377227; 37.155× |
| `d_A6` 95% CI vs 0 | as above | yes | sd 0.0141269054; hw 0.0048947230; 14.977× |
| `Δλ` CI vs 0 (DESCRIPTIVE, no gate) | two-sided | yes | `Δλ = (mean_a d_a)/mean_a r_pred(a)`; `r_pred` is variant-invariant card algebra |
| `Δq` CI vs 0 (DESCRIPTIVE, no gate) | two-sided | yes | q = OLS slope of log(mean recovery) on log(r_pred) over the 6 arms via `k2d.pooled_q`, unmodified; x is variant-invariant, so Δq is a pure y-shift slope difference. **Flagged now:** log is undefined at a non-positive bootstrap mean recovery, and the de-framed cells sit near zero — the count of non-finite draws is reported at finalize and the CI is taken over the finite draws |
| lean predicates partition all `(n_up, n_down)` | deterministic | yes | see §0.8 |

### 0.8 Rule-16 enumeration — the FULL adjudication object as one truth table: **PASS**

All `(n_up, n_down)` with `n_up + n_down ≤ 6`: **28 realizable cells**, each
routed to exactly **one** lean and one pivot under the registered precedence
`L-R3 > L-R1 > L-R2 > L-R4`.

- L-R1 (helps, prior .45) := `n_up ≥ 5 AND n_down = 0` → **2 cells** — (5,0), (6,0) → P-R1
- L-R2 (neutral, prior .30) := `n_up + n_down ≤ 1` → **3 cells** — (0,0), (1,0), (0,1) → P-R2
- L-R3 (harms, prior .10) := `n_down ≥ 2` → **15 cells** → P-R3
- L-R4 (mixed, prior .15) := remainder → **8 cells** → P-R4

`2 + 3 + 15 + 8 = 28`. **Raw-predicate overlaps: 0** — the four predicates are
already pairwise disjoint before precedence is applied (L-R1 forces `n_down=0`
while L-R3 forces `n_down≥2`; L-R1 forces `n_up+n_down≥5` while L-R2 forces
`≤1`; L-R3 forces `n_up+n_down≥2`), so the registration's own remark that
L-R1/L-R3 are "impossible jointly, kept for form" is confirmed and extends to
every pair. **Unrouted cells: 0.** All four leans are reachable at 6 arms.

### 0.9 G5r — hygiene: **PASS**

Round-trip parsing (`float_precision='round_trip'`) on every artifact read;
foreground chunked stages (`part0`, `arms --worlds LO:HI`, `finalize`), longest
Part-0 sub-stage 41.458 s against the 600 s limit; 0 background jobs, 0
monitors; `suica_core/` untouched. Rule-12 source-object header is in the
script docstring and in `gates.json.G5r.rule12_source_objects`; the μ̂
construction is named there by K1b source objects —
`A4_AUTHORS_PER_CONTEXT` (k1b:87), `estimated_occasion_norm` (k1b:278-307),
`_gen_estimated` (k1b:263-276), the donor channel list `idio := mean_part +
noise_part` (k1b:296), the frame substitution `c_vec` (k1b:303-306), the
norm-pool seeding (k1b:290-292) and the pre-map subtraction (k1b:270-275).
Rule-17 realizability: both gauge variants are realizable at every arm by
construction (the 32-donor-per-context pool exists in every world of this
family), and G4r measures the liveness rather than assuming it.

**`arms` is refused unless every Part-0 gate passes AND this report exists on
disk.**

---

## Part 1 — arms

12 cells (A1..A6 × {G-intact, G-deframed}) × 32 worlds = 384 deployed-gauge
runs on the estimated panel plus 768 truth-panel maps, plus 384 card-channel
recomputations, executed in four foreground chunks of 8 worlds: 54.908 s /
55.023 s / 54.931 s / 54.826 s (Part-0 estimate 55 s per chunk from the
4-world pilot; none exceeded it, let alone 2×). 985 authors per world, 565
retained by the deployed gauge, 4 resolved contexts.

**G2r re-checked on the FULL run and PASSED: 192 arm-world card frames
byte-identical across gauge variants** (SHA-256 of the float64 numeric block
equal in every one), `max_abs_sum_diff = 0.0`, `max_abs_gap_diff = 0.0`. The
card frame is recomputed *after* each variant's gauge run precisely so that an
in-place mutation of the world by the de-framing path would show up here. It
did not. The designed invariance holds, so nothing in this leg's contrast comes
from the card side. Pooled card values (identical in both variants) — gap /
attenuation: A1 0.0042082516338342035 / 0.8270259455525812; A2
0.022090586940961776 / 0.784875913653862; A3 0.06332667157670913 /
0.6761014919525692; A4 0.10026522213069033 / 0.5587781794927005; A5
0.01748972753751199 / 0.6451188494827447; A6 0.027468175098059655 /
0.5195716303380183.

## Part 2 — results

### 2.1 The per-arm table (32 paired worlds, world-block bootstrap B=2000, seed 20260821)

| arm | recovery G-intact [95% CI] | recovery G-deframed [95% CI] | d_a = def − int [95% CI] | cell | worlds with d>0 | \|d\|/realized MDE |
|---|---|---|---|---|---|---|
| A1 | 0.1802539896876199 [0.16856489864434882, 0.1907641497206838] | −0.002323535074059783 [−0.009302508993494097, 0.005267227467529713] | **−0.1825775247616797** [−0.19234838093937226, −0.1719028269878068] | DOWN | 0/32 | 12.343 |
| A2 | 0.15817065330134786 [0.14792398545792293, 0.1676061880574323] | −0.0021303896682008227 [−0.009913934403191988, 0.006116512297935118] | **−0.1603010429695487** [−0.17003739193186954, −0.14986656070119625] | DOWN | 0/32 | 11.063 |
| A3 | 0.11450455159268326 [0.10402975844304778, 0.12445101818926099] | 0.001331198693243309 [−0.007119319245767284, 0.010090140056042883] | **−0.11317335289943996** [−0.12180877697065692, −0.10406864323069726] | DOWN | 0/32 | 8.701 |
| A4 | 0.07788655650456981 [0.06953097592510986, 0.08606461960977776] | 0.0008341570693264815 [−0.007328999233365228, 0.009045432227164054] | **−0.07705239943524334** [−0.08351381987096262, −0.07073386188274594] | DOWN | 0/32 | 8.236 |
| A5 | 0.11817481684598696 [0.10821773244119023, 0.12725093757630992] | 0.002018622329167797 [−0.005499374796153279, 0.009307327288425165] | **−0.11615619451681918** [−0.12478259690529406, −0.10782550577056155] | DOWN | 0/32 | 9.341 |
| A6 | 0.0815095100586942 [0.07125003737754441, 0.09057662001559172] | 0.003440825026036933 [−0.005404385123972094, 0.012451279276579949] | **−0.07806868503265725** [−0.0864873927537404, −0.0697211441408005] | DOWN | 0/32 | 6.277 |

Every `d_a` is negative, every CI excludes 0 on the negative side, every
`|d_a|` exceeds the registered margin `m_rec = 0.010` by 7.7×–18.3× (7.705× at A4, 18.258× at A1), and the
sign is unanimous across all 192 arm-worlds (0/32 positive in every arm). The
de-framed reader's b-only recovery is **statistically indistinguishable from
zero in all six arms** — every de-framed CI contains 0, and two of the six
point estimates are negative.

**(n_up, n_down) = (0, 6).**

### 2.2 The lean, with the Part-0 enumeration statement

The Part-0 truth table (§0.8) routes all 28 realizable `(n_up, n_down)` cells
to exactly one lean each under the registered precedence
`L-R3 > L-R1 > L-R2 > L-R4`, with 0 raw-predicate overlaps and 0 unrouted
cells. `(0, 6)` satisfies `n_down ≥ 2` and therefore falls in L-R3's 15-cell
block; it satisfies neither `n_up ≥ 5 ∧ n_down = 0` (L-R1's 2 cells) nor
`n_up + n_down ≤ 1` (L-R2's 3 cells), so precedence is not even needed to
resolve it.

**L-R3 (harms) FIRES [prior .10]. Routing: P-R3.**

### 2.3 The parameter story (DESCRIPTIVE, no gate — as registered)

**λ.** λ := mean measured recovery / mean predicted card attenuation, K2b's own
definition (k2b:1465), refit over this leg's six arms under each variant.

| variant | λ [95% CI] |
|---|---|
| G-intact | 0.18213556261185018 [0.1680078327427061, 0.19469045033998522] |
| G-deframed | 0.000790595010593783 [−0.009569575395921523, 0.011703480813718777] |

**Δλ = −0.1813449676012564 [−0.1930474869292865, −0.16906308385859692]**, cell
DOWN, se 0.006067226923053933. The de-framed reader's efficiency coefficient is
zero: its CI contains 0 and excludes everything above 0.0118.

Incidental but worth recording: G-intact's λ = 0.18214 replicates K2b's
persisted λ = 0.17417497661611914 at a **fresh master seed and 4× the worlds**,
with K2b's value inside this leg's CI.

**q.** q := OLS slope of log(mean recovery) on log(predicted attenuation) over
the six arms, through `k2d.pooled_q` (k2d:644-670) called unmodified; the
regressor is variant-invariant by G2r.

| variant | q [95% CI] | r² | estimable |
|---|---|---|---|
| G-intact | **1.8132149668419377 [1.6568262349122915, 2.0051274012464915]** | 0.9591902951156096 | yes |
| G-deframed | — | — | **no** |

G-intact's q is an **out-of-sample confirmation of T4's closed form** (appendix
L: q = 1.83 [1.71, 1.98], fitted over 25 arms across K2b–K2e): a fresh
master seed, 32 fresh worlds, this leg's six arms alone, r² = 0.959, and
appendix L's point value sits inside the CI.

**Δq is NOT ESTIMABLE, and no substitute is invented.** T4's form is a power
law whose exponent is identified by a log-log slope, which requires a positive
pooled recovery in every arm. Under G-deframed the pooled recovery is negative
in A1 (−0.002323535074059783) and A2 (−0.0021303896682008227), and 1627 of the
2000 paired bootstrap draws are non-finite. The spread over the 373 finite
draws is `[−9.002768641394967, −1.16465858646393]`; it is **a selected subset,
not a confidence interval**, and is recorded for disclosure only. The
statement that survives is stronger and simpler than a Δq: under G-deframed
there is no positive scale for the power law to have an exponent of.

**Δκ is NOT ESTIMABLE, and no pair is invented.** The K2e-style κ regression
regresses a within-pair field-recovery difference D on a within-pair
ΔV_person, and is identified only when the pair's predicted card attenuation is
MATCHED so the λr^q term cancels — K2c/K2d/K2e constructed such pairs to ≤1e-16.
This leg reuses K2b's six state arms, which are **not** attenuation-matched:
the 15 pairwise |Δr_pred| run from 0.030834538189281502 (A3–A5, the closest)
through 0.039012483800980324 (A4–A6) and 0.042272737288345574 (A1–A2) up to
0.3078266657748955, none of them 0. Independently, the de-framing manipulation
changes **neither** r **nor** V_person — it changes only the gauge's input — so
no intact-vs-deframed contrast carries ΔV_person leverage at all. Per the
registration ("if not, state so and report the pieces that are estimable — do
not invent pairs"), κ is reported for neither variant; the standing anchor
κ̂ = −0.7220359963712748 is untouched by this leg.

### 2.4 Mixed recovery (descriptive)

| arm | mixed G-intact [95% CI] | mixed G-deframed [95% CI] | Δ mixed [95% CI] | cell |
|---|---|---|---|---|
| A1 | 0.18412177187898604 [0.17231303219036617, 0.19457551860903718] | 0.0002903429792258114 [−0.006581763151380171, 0.007773753801949987] | −0.18383142889976023 [−0.1936284654434597, −0.17300897411967409] | DOWN |
| A2 | 0.17909830322409553 [0.1686530405487726, 0.18930637035519773] | 0.012488287753126687 [0.004124886328402641, 0.021366237558006616] | −0.16661001547096885 [−0.17648639071935865, −0.1562152549134791] | DOWN |
| A3 | 0.18415690153476327 [0.1731203554774792, 0.19501488482749568] | 0.05721729166524973 [0.04853544462768109, 0.06653182563802115] | −0.12693960986951355 [−0.13510490936748595, −0.11904973051478973] | DOWN |
| A4 | 0.20187878281414162 [0.1932741983101749, 0.2110337650358791] | 0.11245395538246192 [0.10493890702360442, 0.12020756153576105] | −0.0894248274316797 [−0.09541325741882674, −0.08383872720263048] | DOWN |
| A5 | 0.1477009704233117 [0.13837247949488324, 0.15635638512434508] | 0.01430915874494363 [0.005871669163216806, 0.022225302762562096] | −0.13339181167836808 [−0.14108314957070475, −0.12613190901194635] | DOWN |
| A6 | 0.13468034734537454 [0.12704623039141455, 0.14309678182112473] | 0.02976088372370963 [0.020464617630900413, 0.038803532497694186] | −0.1049194636216649 [−0.11031034415922705, −0.09996106132263567] | DOWN |

6/6 DOWN, 0 UP — but **graded by state share**, which the b-only channel is
not: the mixed target retains occasion-varying person content after the frame
is removed, and the more of it an arm has, the more survives. Relative
collapse of mixed recovery: A1 −0.998, A2 −0.930, A5 −0.903, A6 −0.779,
A3 −0.689, A4 −0.443. Against a b-only relative collapse of −0.958 to −1.013
in every arm.

### 2.5 Rule 13

**8 interval clauses, 0 TRIGGERED, 0 BOUNDARY.** The six `d_a` clauses sit
273.5–559.9 Monte-Carlo standard deviations from their boundary (A1 559.869,
A2 498.134, A3 384.660, A5 415.349, A4 363.608, A6 273.469 — the closest
approach in the leg); the Δλ clause sits 466.497 MC-sd away. All six `d_a`
cells and the Δλ cell are unchanged at B = 20000 (endpoints re-reported in
`decision.json`). The Δq clause is NOT_APPLICABLE, the quantity not being
estimable.

### 2.6 Routing

**P-R3 (registered): "de-framing HARMS trait reading — a deployment caution is
added to the certified repair's record; the mechanism question (what did the
frame content scaffold?) becomes a named charter."** The executor executes the
routing and names, but does not answer, the mechanism charter.

Verdict slug: **`L-R3__DEFRAMING_HARMS_TRAIT_READING__nup0_ndown6__P-R3`**.

### 2.7 POST-HOC descriptive (no gate, no lean input; the K2b precedent)

Computed after the lean was assigned; nothing in the adjudication consumes it.

| arm | designed frame variance share | designed state variance share | relative collapse, b-only | relative collapse, mixed |
|---|---|---|---|---|
| A1 | 0.147 | 0.006 | −1.012890 | −0.998423 |
| A2 | 0.135 | 0.030 | −1.013469 | −0.930271 |
| A3 | 0.105 | 0.090 | −0.988374 | −0.689301 |
| A4 | 0.075 | 0.150 | −0.989290 | −0.442963 |
| A5 | 0.105 | 0.090 | −0.982918 | −0.903121 |
| A6 | 0.075 | 0.150 | −0.957786 | −0.779026 |

The b-only collapse is **total and essentially arm-independent** (95.8%–101.3%)
even though the frame's designed variance share halves from A1 to A4/A6 —
i.e. it is not proportional to how much frame there is. K2b's own G4b already
recorded the arithmetic that explains it: in this world family the b-only truth
panel is `w_mu·trait + w_c·common`, whose **only within-author occasion
variation is the frame**, and a relational gauge fed the trait alone produces a
degenerate field (max context norm 0.0006675856745354268 against the b-only
panel's minimum 0.15214367930549447; recovery −0.024495680267977205). Remove
the frame from the estimate and there is nothing left for a frame-carried
target to agree with. What the frame content *scaffolds* — and whether a target
that does not ride on it would behave differently — is P-R3's named charter,
not a claim of this leg.

## Part 3 — defects, anomalies, and the brief to the planner

### Registration defects

**None found.** The registration's enumeration was already a partition before
precedence (0 raw overlaps, 0 gaps, §0.8); every gate was arithmetically
satisfiable (§0.7); the escalation ladder was not needed; and P-R3's own
wording ("the mechanism question — what did the frame content scaffold? —
becomes a named charter") anticipated the mechanism this run exhibits. Two
instrument boundaries the registration could not have priced are recorded
below as findings, not defects.

### Findings that bound future registrations

- **F-1 — the b-only target in the F2/K2b world family is frame-carried.** Any
  registration that manipulates the frame on the ESTIMATE side and scores
  against a b-only target is scoring, in part, frame-vs-frame agreement. The
  numbers are K2b's own (G4b) and this leg's §2.7. A future de-framing test
  that wants a frame-free target must either build a world whose trait channel
  carries within-author occasion variation of its own, or score against the
  mixed target (which this leg reports, and which is graded by state share
  rather than flat).
- **F-2 — T4's closed form has no exponent where the reader's level is zero.**
  q is a log-log slope; it exists only on a positively-scaled reader. Any
  future registration asking for Δq across an intervention that can drive the
  level to zero should pre-declare a level gate (e.g. "q is refit only where
  the pooled recovery CI excludes 0 in every arm") rather than discovering
  non-estimability at finalize.

### Anomalies, all with timing

- **A-1 (before any hypothesis number existed).** The first `--stage part0`
  invocation died in `k2e.rederive_anchors` with
  `ValueError: unknown w_int arm 'int:0.2806659454238726'` — K2e's anchor chain
  requires `k2d.install_species_weights()` (k2d:206-238) to be installed first.
  Resolved by installing it and recording `k2d.verify_species_weights()`'s
  bit-exactness proof in G0r (§0.1). The failure occurred inside the anchor
  stage, before any pilot world was built; no hypothesis-relevant number
  existed.
- **A-2 (after the arms, before the report's Part 2 was written).**
  `--stage finalize` was run twice. The first run reported
  `delta_q.point = NaN` and a CI computed over a nan-contaminated array; the
  script was then patched so that non-estimability is stated explicitly with
  its reason and the finite-draw spread is labelled "NOT A CI", and a POST-HOC
  relative-collapse table was added. **No estimator, margin, lean predicate,
  precedence or routing was changed, and no arm was re-run.** Every number in
  §2.1–§2.5 is bit-identical between the two finalize runs (both are
  deterministic functions of the same 12 persisted cell CSVs and the same
  seeded pick matrices); the second run only replaces a NaN with a statement.
  Disclosed rather than hidden because the first run did produce
  hypothesis-relevant output.
- **A-3 (disclosed at adjudication; no design change).** The 4-world pilot
  **under-estimated the realized per-arm sd of `d_a` by 1.5×–2.8×** (realized
  MDEs at n=32: A1 0.014792488302599547, A2 0.014489639069133028, A3
  0.013007026588566027, A4 0.009355759704207758, A5 0.012435257878345176, A6
  0.01243756674479708, against the pilot projections 0.0066782413 / 0.0095074854
  / 0.0078720317 / 0.0060960359 / 0.0044835605 / 0.0072244207). Five of the six
  realized MDEs therefore exceed the registered 0.010 target, which the pilot
  said would be met. **This changes nothing in the adjudication**: every
  measured `|d_a|` is 6.3×–12.3× its own *realized* MDE and 7.7×–18.3× the
  registered margin `m_rec = 0.010`, and the sign is unanimous in 192/192
  arm-worlds. This is the same under-estimation rule 16's convention note
  recorded from K2d (2-world pilots under by 2.05×–7.83×); at 4 worlds it is
  smaller but still present, and a future registration should consider a
  df-based inflation factor on pilot-sd MDEs even at 4 worlds.
- **A-4 (before the arms, §0.5).** All six pilot `d_a` were negative and 15–37×
  the projected half-width. Disclosed in the Part-0 report as written, before
  any main world index existed; no design element, margin, prior, predicate or
  route was altered in response.
- **A-5 (before the arms, §0.4(iii)).** The intact b-only truth field is not
  bit-identical across gauge variants, because `calibrate_d0_soft` is fitted on
  what the operator observes: maximum absolute entry difference
  0.007537607590715613, minimum matrix cosine 0.6823271962928399. This is
  RN-2b, a property of the deployed gauge rather than a choice; each variant's
  recovery is always a cosine between two fields the same calibration produced.

No crashes after A-1. No arm was ever re-run. No stage exceeded its Part-0
estimate. Total compute **≈ 302 s** (Part 0 82.000 s; arms 54.908 + 55.023 +
54.931 + 54.826 s; finalize 0.070 s).

### The brief to the planner

1. **The answer is unambiguous and it is the .10-prior branch.** Per-occasion
   estimated de-framing, applied to the deployed gauge's input, does not merely
   fail to improve the reader as a trait instrument — it **abolishes** it.
   b-only recovery falls to statistical zero in all six state arms (every
   de-framed CI contains 0; two point estimates are negative), λ falls from
   0.18214 to 0.00079, and T4's exponent has no positive scale left to be an
   exponent of. This is not a power artefact: 0/32 worlds positive in every
   arm, effects 6.3×–12.3× their realized MDEs, rule 13 clean at 273–560 MC-sd.
2. **It is not a rule-9 artefact either.** All three open conventions — donor
   channel list, donor pool scheme, and whether the truth panels are de-framed
   too — give the same sign in 6/6 arms, and the largest disagreement between
   any two readings (0.039393) is smaller than the smallest primary effect
   (0.070782). The primary convention is the middle one, not the extreme.
3. **T9's counter-operation is re-typed by measurement, not by argument.**
   Frame removal is a *hygiene* operation on what a statistic MEANS (K1b/K1c′:
   it removes 94.4%/73.5% of the frame amplification, and this leg reproduces
   K1b's A0/A1/A4 bit-exactly to prove it is the same object). It is **not** an
   enhancement of the reader as a measuring instrument, and on this
   world-family/target pair it is destructive to it. The certified-unadopted
   repair's record should carry that deployment caution: *the de-framing repair
   makes agreement statistics honest and makes trait recovery, as this family's
   b-only target defines it, disappear.*
4. **The mechanism charter P-R3 names has a strong candidate already visible,
   and the planner should decide whether it counts as an answer or a
   confound.** In this family the b-only truth panel's only within-author
   occasion variation *is* the frame, so the b-only field is a frame field
   modulated by the trait, and K2b's G4b measured that the trait alone yields a
   degenerate field. On that reading, what de-framing destroys is the
   *carrier*, and the honest question the charter should ask is: **is there any
   target in this world family that de-framing leaves readable?** The mixed
   channel says "partly, and in proportion to state share" (relative collapse
   −0.443 at A4 against −0.998 at A1) — which is a second, softer finding the
   charter can start from.
5. **One free confirmation to bank.** On 32 fresh worlds at a fresh master
   seed, the intact gauge reproduces T4's closed form: q = 1.8132149668419377
   [1.6568262349122915, 2.0051274012464915], r² = 0.959, with appendix L's
   1.83 [1.71, 1.98] inside the interval, and λ = 0.18214 with K2b's persisted
   0.17417 inside its interval. Appendix L's headline is now confirmed
   out-of-sample from six arms alone.
6. **Nothing is adopted, and nothing about F16 changes.** L-R1 did not fire, so
   no adoption memo is drafted. The de-framing repair remains certified and
   unadopted, now with a measured deployment caution attached rather than an
   open question.
