# SUICA M4-K2d — The frontier and the carrier: does the composition term cross materiality, and which state species carries it?

**Tier:** EXPLORATORY · label-free · synthetic throughout.
**Banner:** synthetic worlds calibrated to an opened-panel regime, exploratory.
**Registration:** `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md` § "M4-K2d — The frontier and the
carrier …", REGISTERED 2026-08-09 BEFORE RUN, commit `9565e5f`. The registration text is
binding; this executor did implementation and execution only.
**Script:** `scripts/run_suica_m4_k2d_frontier_carrier.py`
**Artifacts:** `results/m4_k2d_frontier_carrier/` (gitignored).
**Theory:** `docs/SUICA_IDENTITY_THEORY_V1.md` T4 (S3), appendices I and J.

---

## Part 0 — written to disk 2026-08-09T09:49:45.591528+00:00 (UTC), BEFORE any main arm

Part 0 ran on RESERVED pilot worlds **9801–9802** (disjoint from main indices 0…63).
`results/m4_k2d_frontier_carrier/gates.json`, `part0_arms.json`,
`part0_predictions.csv`, `part0_trade_sensitivity.csv` and `part0_tables.md` carry every
number below at full precision; the `arms` stage refuses to run unless every Part-0 gate
passes **and this report exists on disk** (`require_part0()`). Part-0 wall time
**10.234 s** (share solve 0.254 s, pilot 9.593 s). No hypothesis-channel run of any kind
preceded this stage.

### 0.0 Standing-rule-14 self-check (required by G5d′)

**No gate and no branch lean in this leg compares quantities across scales.** G0d′
re-derives K2b's and K2c's own numbers against themselves; G1d′ compares **card
attenuation to card attenuation**; G2d′, G4d′, every per-pair **cell** assignment, **L-F**,
**L-S** and **L-M** compare **field agreement to field agreement**, within-pair, same
instrument, same units. The single cross-scale object is the **q-update**, which the
registration declares *descriptive, no gate*, and which pins its own link (a log-log power
law whose exponent `q` **is** the estimand).

### 0.1 Rule-12 header — the interaction channel by generator SOURCE OBJECT

K2d's only new physics is `w_int > 0` in two arms. Every object it uses is already built,
unconditionally, in **every** K2b world, and was typed and certified by K2a:

| object | source |
|---|---|
| occasion-keyed shock stream `S(o) ~ N(0, I_k)` | `k2a:174-181` `shock_int_matrix`, salt `m4k2a-shock-int` (disjoint from f2's `m4f2-shock`) |
| person loadings `a_i ~ N(0, I_k)` | `k2b:338-341` `a_load`, salt `m4k2b-loading` |
| `u_int = einsum("ij,ojl->iol", a_load, shocks)/√k` | `k2b:342-343` |
| `s_int = A_SCALE · ((u_int · G_PROFILE) @ loadings.T)` | `k2b:344` |
| panel emission of the channel | `k2b:374-375` (`if "int" in active and w["int"] != 0.0`) |
| card-side cell-centring and entry into the two-split card | `k2b:416`, `k2b:425-426` |
| entry into the attenuation algebra as `C/m` (full set) and `C/half` (each split) | `k2b:537`, `k2b:549`, `k2b:559`, `k2b:562` |

The `C/m` form is the point: the interaction channel is **person** content that averages
down like noise — occasion-bound, zero-persistence — which is exactly the second species
the registration wants to trade against slow-AR content.

**The one new object** is the arm-weight parameterization (k2b:198-210 admits only
`"zero"`/`"equal"`): `install_species_weights()` in this leg's script, a **disclosed
single-object dispatcher** (the K1/K2b `k2a_pooled_stats_patched` precedent) installed on
`k2b.arm_weights` so that `arm_shares` (k2b:212-213) and `arm_predictions` (k2b:533-584)
inherit it unchanged. It **delegates verbatim** for `"zero"`/`"equal"`. Verified in Part 0
on an 8-point share grid: post-patch `"zero"` is **bit-exact** vs the original (True), the
`"int:0.0"` route equals `"zero"` **bit-exactly** (True), and the `"int:(1-s)/3"` route
reproduces `"equal"` to **2.7755575615628914e-17** (a different arithmetic order for the
same quantity).

### 0.2 Register-notes (rule 9 — open conventions fixed BEFORE any hypothesis number)

- **RN-1 (the one free design parameter).** "SP-68-int (mixed species: smaller slow share
  s68′ + w_int chosen so predicted attenuation matches SP-68-slow's)" fixes **one**
  equation (the match) on **two** unknowns (s′, w_int), so s′ must be pinned by a written
  rule. The registration's own words bound it on both sides: **"mixed species" excludes
  s′ = 0** (that would be int-*only*, not mixed) and **"smaller" excludes s′ = s**. FIXED
  before any world was built: **s′ = s/2**, the half-trade — the unique scale-free
  interior fraction, and the one that maximizes the species contrast subject to keeping
  the arm genuinely mixed. A **pure-algebra sensitivity table** (no world, no field
  number; §0.4) reports the solved interaction share at trade fractions {0.25, 0.50, 0.75}
  so the reader can see what the other conventions would have bought at card level.
- **RN-2 ("CI lower(|D|)").** |D|'s interval lower endpoint is `min(|lo|,|hi|)` when the
  D-interval **excludes** 0, and **exactly 0** when it includes 0 (0 is then an admissible
  value of |D|). Under this definition the MAT-SIG sub-clause "lower(|D|) ≥ M2" implies
  "CI excludes 0", which is what makes the enumeration table's first column non-redundant.
- **RN-3 (endpoints).** "CI inside ±M" is **inclusive** (`-M ≤ lo and hi ≤ M`); "≥ M" is
  inclusive. Ties fall on the side the symbols put them.
- **RN-4 (λ).** K2b's arm-independent reader efficiency 0.17417497661611914 is used ONLY
  as the q-update's intercept scale; the OLS slope is λ-invariant, verified numerically.
- **RN-5 (seed lineage).** K2d's own lineage: `master_seed 20260818`, salt `m4k2d-world`;
  the world seed depends on the **world index only**, so both arms of every pair — which
  differ in share, φ and w_int — share the trait `b`, the AR innovations, the frame
  shocks, the interaction loadings `a_i` and the noise **bit-for-bit**. Every `D` is a
  within-world difference.
- **RN-6 (corpus-tag provenance).** `k2b.run_field_world` is called **unmodified**, so the
  tag it builds keeps the literal prefix `m4k2b-`; it is a hash label seeding the deployed
  transition-null permutation streams (f1:199-206). Prefixing every K2d arm id with
  `K2D-` makes every tag **disjoint** from every K2b and K2c tag.
- **RN-7 (rule 15's own failure — see §0.6).** The per-pair cell table **is** a partition,
  verified by enumeration. The **lean-level** predicates the registration builds on top of
  it are **not**. Pre-declared readings, fixed before any hypothesis number, following
  K2c's RN-4 precedent (the standing convention in this line for a result that fits no
  registered branch — or more than one):
  - FR-45 = **MAT-SIG(+)** → no pivot is routed → **L-F MISSES** and the outcome is the
    NAMED NON-REGISTERED cell **`FRONTIER-SIGN-REVERSAL`**, reported as such; T4 is not
    re-typed on it.
  - SP cells **(SIG, INDET)** in either order → SPECIES-SPECIFIC *and* SPECIES-MIXED both
    fire → NAMED NON-REGISTERED **`SPECIES-BOTH-FIRE`**, both readings reported, no L-S
    branch claimed.
  - SP cells **(NULL/WEAK-NULL, INDET)** in either order → no registered outcome → NAMED
    NON-REGISTERED **`SPECIES-PARTIAL-UNDERPOWERED`** (one pair bounded null, one pair
    unresolved), reported as such.

### 0.3 The SOLVED shares (G1d′, Part-0 half — the designed identity)

Every share below is **computed**, by bisection-to-adjacent-doubles on the K2a-validated
attenuation algebra (`k2b.arm_predictions`), before any world existed. Arm b of each pair
is solved to arm a's **achieved** attenuation, so the within-pair predicted difference is
bounded by the solver's own resolution, not by the target's representability.

| pair | kind | target r | arm a (slow share, int share, φ) | r(a) | arm b (slow share, int share, φ) | r(b) | \|Δr\| | matched (≤1e-12) |
|---|---|---|---|---|---|---|---|---|
| `FR-45` | frontier | 0.45 | `FR45a` (0.6634207990183637, 0.0, 0.90) | 0.45000000000000007 | `FR45b` (0.6061873016248464, 0.0, 0.98) | 0.45000000000000007 | **0.000000e+00** | True |
| `SP-68` | species | 0.68 | `SP68slow` (0.29267462506992153, 0.0, 0.90) | 0.68 | `SP68int` (0.14633731253496077, **0.2806659454238726**, 0.90) | 0.6800000000000002 | **1.110223e-16** | True |
| `SP-56` | species | 0.56 | `SP56slow` (0.4973617623232523, 0.0, 0.90) | 0.5600000000000002 | `SP56int` (0.24868088116162615, **0.37685012551875713**, 0.90) | 0.5600000000000002 | **0.000000e+00** | True |

**3/3 matched. G1d′ Part-0 half PASSES.**

Two continuity facts worth recording (no gate): the two SP **slow** arms are solved to the
same targets at the same φ as K2c's P2a and P3a, and the solver returns **bit-identical**
shares — `0.29267462506992153` and `0.4973617623232523` — so `SP-68-slow` and `SP-56-slow`
are K2c's P2a and P3a *by design*, at a different seed lineage. And the frontier arm's
slow share is **0.663**: reaching attenuation 0.45 requires two thirds of the non-noise
signal variance to be state, versus 0.293 at 0.68 and 0.497 at 0.56.

### 0.4 RN-1 trade sensitivity — pure card algebra, no world, no field number

| pair | trade fraction f (s′ = f·s) | s′ | solved int fraction t | realized variance share of int | \|Δr\| | selected |
|---|---|---|---|---|---|---|
| `SP-68` | 0.25 | 0.0731686562675 | 0.420998918136 | 0.12629968 | 0.000e+00 | |
| `SP-68` | **0.50** | 0.146337312535 | **0.280665945424** | **0.08419978** | 1.110e-16 | **RN-1** |
| `SP-68` | 0.75 | 0.219505968802 | 0.140332972712 | 0.04209989 | 0.000e+00 | |
| `SP-56` | 0.25 | 0.124340440581 | 0.565275188278 | 0.16958256 | 0.000e+00 | |
| `SP-56` | **0.50** | 0.248680881162 | **0.376850125519** | **0.11305504** | 0.000e+00 | **RN-1** |
| `SP-56` | 0.75 | 0.373021321742 | 0.188425062759 | 0.05652752 | 0.000e+00 | |

The exchange rate the card demands is **1 unit of slow share ≈ 1.92 units of interaction
share** at SP-68 and **≈ 1.52** at SP-56: persistent state attenuates the card far more per
unit of variance than occasion-bound state does (`v_full(m,φ)` vs `1/m`), so the int arm
must carry *more total* non-trait person content to sit at the same attenuation. That is a
property of the design, stated here before any field number exists, and it is the reason
the species question is not the same question as "how much person content is there".

### 0.5 Part-0 point predictions — all 6 arms, computed before any world

| arm | pair | slow share | int share | φ | A (μ) | B (slow) | C (int) | Cc (frame) | E (noise) | GAP pred | r(card→b) pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `FR45a` | FR-45 | 0.663420799018 | 0 | 0.90 | 0.05048688 | 0.19902624 | 0.00000000 | 0.05048688 | 0.70000000 | 0.1277904902 | 0.450000000000 |
| `FR45b` | FR-45 | 0.606187301625 | 0 | 0.98 | 0.05907190 | 0.18185619 | 0.00000000 | 0.05907190 | 0.70000000 | 0.0325702565 | 0.450000000000 |
| `SP68slow` | SP-68 | 0.29267462507 | 0 | 0.90 | 0.10609881 | 0.08780239 | 0.00000000 | 0.10609881 | 0.70000000 | 0.0621402572 | 0.680000000000 |
| `SP68int` | SP-68 | 0.146337312535 | 0.280665945424 | 0.90 | 0.08594951 | 0.04390119 | 0.08419978 | 0.08594951 | 0.70000000 | 0.0335132537 | 0.680000000000 |
| `SP56slow` | SP-56 | 0.497361762323 | 0 | 0.90 | 0.07539574 | 0.14920853 | 0.00000000 | 0.07539574 | 0.70000000 | 0.0999465981 | 0.560000000000 |
| `SP56int` | SP-56 | 0.248680881162 | 0.376850125519 | 0.90 | 0.05617035 | 0.07460426 | 0.11305504 | 0.05617035 | 0.70000000 | 0.0557432625 | 0.560000000000 |

### 0.6 The rule-15 ENUMERATION — the adjudication space, and where the registration's own space fails

**(a) The per-pair cell table IS a partition — verified.** 25 155 (point, lo, hi) triples
searched with point ∈ [lo, hi]; **30 of 64** clause combinations are logically realizable;
**0 overlaps**; the map is total; **all seven signed cells are realized**. The clause
vector is (c1) CI excludes 0, (c2) |D| ≥ M1, (c3) lower(|D|) ≥ M2 under RN-2, (c4) CI ⊆
±M2, (c5) CI ⊆ ±M1, (c6) D > 0 — c6 added because the registration folds the **sign** into
the cell NAME (`MAT-SIG(sign)`), and without it two opposite-sign results would share a
truth-table row. The full 64-row table is in `gates.json`; the 30 realizable rows are in
`results/m4_k2d_frontier_carrier/part0_tables.md`. **PASS.**

| CI vs 0 | further test | cell |
|---|---|---|
| excludes 0 | \|D\| ≥ M1 = 0.020 **and** lower(\|D\|) ≥ M2 = 0.010 | **MAT-SIG(sign)** |
| excludes 0 | otherwise | **SUB-SIG(sign)** |
| includes 0 | CI ⊆ ±M2 | **NULL** |
| includes 0 | CI ⊆ ±M1 but ⊄ ±M2 | **WEAK-NULL** |
| includes 0 | CI ⊄ ±M1 | **INDET** |

**(b) The L-S predicate space is NOT a partition — 8 overlaps and 4 gaps of 49.**
Enumerating all 49 ordered (SP-68 cell, SP-56 cell) combinations against the registration's
three L-S predicates plus the named SPECIES-UNDERPOWERED: **37 unique, 8 OVERLAP, 4 GAP.**

- **OVERLAP (8):** any (SIG, INDET) combination in either order. SPECIES-SPECIFIC's clause
  ("≥1 ∈ {MAT-SIG, SUB-SIG} with sign agreement across any significant pairs") is
  satisfied trivially when there is exactly one significant pair, and SPECIES-MIXED's
  clause explicitly names "one significant and one INDET". Both fire.
- **GAP (4):** (NULL/WEAK-NULL, INDET) in either order. Not both null → not GENERAL; no
  significant pair → not SPECIFIC; not opposed-sign and not sig+INDET → not MIXED; not
  INDET+INDET → not UNDERPOWERED. Nothing fires.

**(c) The pivot routing over FR-45's cell has 1 gap of 7.** P2d″ ← MAT-SIG(−); P3d″ ←
{NULL, WEAK-NULL}; P4d″ ← {SUB-SIG(±), INDET}. **MAT-SIG(+) is unrouted** — a *material and
significant* frontier effect in the direction **opposite** to K2c's unanimous sign has no
registered consequence.

**This is rule 15's first application, and it caught its own registration.** Rule 15 was
created (2026-08-09, paid for by defects #17 and #21) precisely to require an
enumeration-verified partition at registration time; the K2d registration verified the
per-pair table and not the predicates built on it. Recorded as a registration defect, not
repaired; RN-7 pre-declares the readings **before any hypothesis number exists**. Note the
gaps and overlaps all involve **INDET**, so a well-powered leg may never touch them — but
that is luck, not design, and the enumeration is what tells us which it was.

### 0.7 G0d′ — anchors, bit-exact (PASS)

Re-derived from persisted artifacts by round-trip parsing, then compared to the persisted
values with `==`:

| anchor | persisted | re-derived | residual | bit-exact |
|---|---|---|---|---|
| K2b A1 field recovery | 0.177888649457317 | 0.177888649457317 | 0.0 | True |
| K2b A4 field recovery | 0.07543949574114414 | 0.07543949574114414 | 0.0 | True |
| λ (arm-independent reader efficiency) | 0.17417497661611914 | 0.17417497661611914 | 0.0 | True |
| K2c D(P1) | −0.0033349254353831808 | −0.0033349254353831808 | 0.0 | True |
| K2c D(P1) CI | [−0.007617710100740499, +0.0011074921964934288] | identical | [0.0, 0.0] | True |
| K2c D(P2) | −0.012167516605861444 | −0.012167516605861444 | 0.0 | True |
| K2c D(P2) CI | [−0.017430001829670642, −0.006619210190334735] | identical | [0.0, 0.0] | True |
| K2c D(P3) | −0.01355928388620139 | −0.01355928388620139 | 0.0 | True |
| K2c D(P3) CI | [−0.018647677326514903, −0.008674340005325598] | identical | [0.0, 0.0] | True |
| K2c pooled q (13 arms) | 1.9337620539521978 | 1.9337620539521978 | 0.0 | True |
| K2c q CI | [1.7337263621727161, 2.1932591297891246] | identical | [0.0, 0.0] | True |

Route: round-trip re-read of `results/m4_k2c_matched_pairs/arm_*_field_w*.csv` and
`part0_predictions.csv`; the D CIs reproduced with K2c's own world-block picks
(`default_rng(20260817).integers(0, 32, (2000, 32))`); the pooled q by calling K2c's own
`l3_pooled_q` **unmodified** at its own seed and B. **Additional self-check:** K2d's
generalized `pooled_q` (which must handle three or more world-groups) reproduces K2c's
two-group fit **bit-identically** — `q` and both CI endpoints equal. Panel dims are
K1-pinned and unchanged: **985 authors/world, m-multiset {8:272, 12:200, 16:513}, 4
contexts, 565 retained, 12 784 events**.

### 0.8 G2d′ — power (rule 2), 2-world pilot, PER PAIR

| pair | pilot paired sd | MDE target | MDE(80%,.05,paired) @32 | @64 | selected n | escalated | short at max |
|---|---|---|---|---|---|---|---|
| `FR-45` | 0.00764050330697439 | 0.020 | **0.003907310816809561** | 0.0027178267871929437 | **32** | False | False |
| `SP-68` | 0.009848005090851033 | 0.010 | **0.0050362149284528595** | 0.0035030639947365356 | **32** | False | False |
| `SP-56` | 0.0026002797488501686 | 0.010 | **0.0013297685742952022** | 0.0009249534581274694 | **32** | False | False |

**All three pairs meet their registered MDE at n = 32. No escalation. No claim is tiered.**
t-quantiles from `scipy.stats.t.ppf` via K2c's verified table (K2c anomaly A-1's correction
inherited). Pilot paired differences (2 worlds each, the registered gate's own inputs):
FR-45 [−0.006395891750674697, +0.004409411649404969]; SP-68 [+0.05790158177539493,
+0.043974399413594115]; SP-56 [+0.03333652745951739, +0.0370138783463054].

### 0.9 G4d′ — liveness (rule 3) and non-degeneracy (rule 10) (PASS)

**The interaction channel is live exactly where it is designed to be, and exactly zero
where it is not.** Realized variance shares of the `int` channel in the emitted panel:

| arm | design int fraction of signal | design int variance share | **realized** int variance share | live |
|---|---|---|---|---|
| `FR45a` | 0 | 0.0 | **0.0** | — |
| `FR45b` | 0 | 0.0 | **0.0** | — |
| `SP68slow` | 0 | 0.0 | **0.0** | — |
| `SP68int` | 0.2806659454238726 | 0.0841997836271618 | **0.08561182681052686** | **YES** |
| `SP56slow` | 0 | 0.0 | **0.0** | — |
| `SP56int` | 0.37685012551875713 | 0.11305503765562716 | **0.11479125952660524** | **YES** |

| pair | kind | panel RMS a vs b | realized slow a / b | realized int a / b | pilot field a / b | non-degenerate |
|---|---|---|---|---|---|---|
| `FR-45` | frontier | 0.03975443 | 0.19938144 / 0.18206197 | 0.0 / 0.0 | 0.04873799 / 0.04973123 | True |
| `SP-68` | species | 0.05457700 | 0.08811628 / 0.04397357 | 0.0 / 0.08561183 | 0.11889570 / 0.06795770 | True |
| `SP-56` | species | 0.06389755 | 0.14959435 / 0.07462342 | 0.0 / 0.11479126 | 0.07053067 / 0.03535547 | True |

Across the three designed attenuation levels both channels move per prediction (strictly
increasing with the target):

| designed level | pilot card attenuation | pilot field recovery |
|---|---|---|
| FR-45 (0.45) | 0.44972184 | 0.04923461 |
| SP-56 (0.56) | 0.55892119 | 0.05294307 |
| SP-68 (0.68) | 0.67873560 | 0.09342670 |

Frame-channel centred residual (T3's designed cancellation, measured not assumed)
**1.4432899320127035e-15**; max |realized − design| variance share **0.0027394841786333723**
(≤ 0.01).

### 0.10 G3d′ — rule-11 satisfiability with DIRECTIONS; rule-13 spec (PASS)

Every registered clause is arithmetically satisfiable under the pilot statistics at the
selected n; directions stated. B = 2000 at seed = master for every interval; rule 13
re-runs any clause whose boundary lies within 2× the Monte-Carlo sd of its endpoint at
B = 20 000. Projected (conservative, unpaired) within-pair card half-widths FR-45
0.00240058 / SP-68 0.00182815 / SP-56 0.00217426 against the ±0.005 margin; projected
1.96·se(D) FR-45 0.00264730 / SP-68 0.00341216 / SP-56 0.00090095, so **MAT-SIG is
reachable** (it needs 1.96·se < M1 − M2 = 0.010) and **NULL is reachable** (it needs
1.96·se < M2 = 0.010) in all three pairs — the dual-margin design is not self-defeating at
this n. Full clause table with notes in `part0_tables.md`.

### 0.11 G5d′ — hygiene (PASS)

Round-trip parsing on every artifact read (`float_precision="round_trip"`); foreground
chunked stages (`part0`, `arms --worlds a-b`, `finalize`); **0 background jobs, 0
monitors**; rule-12 header §0.1; rule-14 self-check §0.0. World build 0.0194280743598938 s
mean. **Part-0 stage estimate for the arms stage: 153.49013137817383 s total (0.792951742808024 s
per arm-world × 192 arm-worlds); stop-and-report threshold 306.98026275634766 s.**
Recommended chunk 16 worlds.

### 0.12 The adjudication space, restated as it will be scored

- **Per-pair cell** by the table in §0.6(a), with `D = field(a) − field(b)`, a = the φ.90
  arm for FR-45 and the **slow** arm for the SP pairs, from a paired **world-block**
  bootstrap (B = 2000, seed = master, picks shared across arms).
- **L-F [prior .55]** := FR-45 ∈ **MAT-SIG(−)** → **P2d″**. FR-45 ∈ {NULL, WEAK-NULL} →
  **P3d″**. FR-45 ∈ {SUB-SIG(±), INDET} → **P4d″**. FR-45 = MAT-SIG(+) → RN-7's
  `FRONTIER-SIGN-REVERSAL`.
- **L-S** over the two SP pairs: **SPECIES-GENERAL** [.35] := both ∈ {NULL, WEAK-NULL};
  **SPECIES-SPECIFIC** [.45] := ≥1 ∈ {MAT-SIG, SUB-SIG} with sign agreement among
  significant pairs; **SPECIES-MIXED** [.20] := significant pairs with opposed signs, or
  one significant and one INDET; INDET+INDET → SPECIES-UNDERPOWERED. Overlaps/gaps per
  RN-7. **The sign is itself a finding:** D < 0 (slow arm recovers LESS) means the
  persistent species costs the reader more than the card-equivalent occasion-bound
  species; D > 0 means the occasion-bound species costs more.
- **L-M [prior .70]** := FR-45's Δmixed has K2c's direction (**positive** — the higher-state
  arm recovers MORE of the mixture) with CI excluding 0. SP pairs' Δmixed: descriptive.
- **q-update:** pooled `q` over all **19** arms (6 K2b + 7 K2c + 6 K2d), descriptive, **no
  gate**.
- **P1d″:** a pair whose measured within-pair card-attenuation difference CI leaves ±0.005
  is **VOID** for its claims; ≥2 void → the leg reports and stops.

---

## Part 1 — Results (written after the arms ran)

Executed exactly as Part 0 fixed it. **6 arms × 32 worlds** (no pair escalated),
`master_seed 20260818`, K1-pinned panel (985 authors, 565 retained, 4 resolved contexts),
card channel **18 080 pooled authors/arm**, **192 adjudicated deployed-gauge world runs**
+ 12 reserved-pilot runs (worlds 9801–9802). **Total compute 136.046 s** — part0 10.239,
arms 58.011 + 55.755, finalize 12.041. The arms stage ran in **113.766 s** against a
Part-0 estimate of 153.490 s and a stop-and-report threshold of 306.980 s. No background
jobs, no monitors, no re-runs, no crashes, no stage over its estimate.

### 1.1 VERDICT

**`FRONTIER_SUBSIG_NEG__L_F_MISS__SPECIES_SPECIFIC__MATCH_EXACT__LM_HOLD`**

| object | outcome |
|---|---|
| **FR-45 cell** | **SUB-SIG(−)** — significant, K2c's direction, **sub-material at both margins** |
| **L-F [prior .55]** | **MISS** (the cell is not MAT-SIG(−)) |
| **pivot** | **P4d″ FIRES** — the frontier is UNRESOLVED; P1d″/P2d″/P3d″ all false; **T4 is not re-typed** |
| **SP-68 cell** | **MAT-SIG(+)** |
| **SP-56 cell** | **MAT-SIG(+)** |
| **L-S** | **SPECIES-SPECIFIC** — the registration's *uniquely assigned* outcome (no overlap, no gap touched), sign **POSITIVE** in both pairs |
| **carrier (the sign, itself a finding)** | the **occasion-bound, zero-persistence** species costs the reader MORE than the card-equivalent persistent species |
| **L-M [prior .70]** | **HOLD** |
| **pairs VOID** | **0** |
| **rule 13** | 0 clauses triggered, 0 BOUNDARY |
| **q-update (19 arms, descriptive)** | q = 1.8528700746510731 [1.7147417060355998, 1.999586491101811] |

**Every result landed in a cell the registration names, uniquely.** The enumerated
overlaps and gaps of §0.6 were not touched — all four gap and eight overlap combinations
require an INDET pair, and no pair was INDET. RN-7 was pre-declared and did not have to
fire.

### 1.2 G1d′ post-arms — the designed identity survived contact (0 VOID; P1d″ does not fire)

| pair | measured r(a) | measured r(b) | measured difference | 95% CI | se | inside ±0.005 | VOID |
|---|---|---|---|---|---|---|---|
| `FR-45` | 0.448748736350754 | 0.44897951432908695 | **−0.00023077797833293** | [−0.0008398955660289976, +0.00035977483314042] | 0.0003094264737877023 | True | False |
| `SP-68` | 0.6791176532067729 | 0.6792356606451361 | **−0.00011800743836321015** | [−0.000496488108276616, +0.00023821148793192715] | 0.00019168101065538716 | True | False |
| `SP-56` | 0.5588692694299885 | 0.5589722706192591 | **−0.00010300118927064617** | [−0.0006023120725398596, +0.00037126125269053235] | 0.000251789355697565 | True | False |

The CIs are **6.0× / 10.1× / 8.3× tighter** than the ±0.005 margin. **The species pair is
matched as exactly as the persistence pair** — trading slow-AR content for interaction
content at the algebra's exchange rate lands the card within 1.2e-4 of its twin, which is
what licenses reading any field difference as composition rather than attenuation.

**Card positive control (no gate, continuity):** measured attenuation contains its Part-0
prediction in **6/6** arms, max |relative error| **0.278%** (FR45a −0.278%, FR45b −0.226%,
SP68slow −0.130%, SP68int −0.112%, SP56slow −0.202%, SP56int −0.184%). The two-split GAP
contains its prediction in **4/6** — see anomaly A-2.

### 1.3 The adjudication quantity D and its CELL

`D = field(a) − field(b)`; a = the φ.90 arm (FR-45) or the **slow** arm (SP pairs); paired
world-block bootstrap, B = 2000, seed = master, picks shared across arms; n = 32 per pair.

| pair | field(a) | field(b) | **D** | 95% CI | se | \|D\| | lower(\|D\|) | **CELL** |
|---|---|---|---|---|---|---|---|---|
| `FR-45` | 0.05705094660907048 | 0.06693033221632827 | **−0.009879385607257792** | [−0.015395490382080454, −0.004577741752997643] | 0.002762055036511434 | 0.009879 | 0.004578 | **SUB-SIG(−)** |
| `SP-68` | 0.12039037534592587 | 0.0900394657375559 | **+0.030350909608369947** | [+0.02348894741478388, +0.03692045553170193] | 0.00349410094639657 | 0.030351 | 0.023489 | **MAT-SIG(+)** |
| `SP-56` | 0.08225219735962576 | 0.0551914191846241 | **+0.027060778175001646** | [+0.020297134101083764, +0.03382765210646028] | 0.0035258444913037874 | 0.027061 | 0.020297 | **MAT-SIG(+)** |

Clause vectors (c1 excludes 0, c2 |D|≥M1, c3 lower(|D|)≥M2, c4 CI⊆±M2, c5 CI⊆±M1, c6 D>0):
FR-45 `(T, F, F, F, T, F)`; SP-68 `(T, T, T, F, F, T)`; SP-56 `(T, T, T, F, F, T)`. Point
sign consistent with the CI in 3/3. Per-world sign counts: FR-45 8/32 positive (i.e. 24/32
negative), SP-68 **29/32** positive, SP-56 **26/32** positive. Paired-t CIs agree with the
bootstrap in all three pairs (FR-45 [−0.015536, −0.004223]; SP-68 [+0.023036, +0.037666];
SP-56 [+0.019723, +0.034398]).

**Rule 15 did the exact job it was created for.** FR-45 is *statistically resolved and
materially small at the same time* — K2c's BOTH_FIRE configuration, reproduced at the
frontier. Under K2c's non-partitioned space this leg would have been unclassifiable a
second time; under the enumerated dual-margin table it is one cell, **SUB-SIG(−)**, with a
registered pivot attached.

### 1.4 The frontier: the term does NOT cross materiality — and the leg says why

L-F predicted MAT-SIG(−) at attenuation 0.45. The direction is right (**negative, as in
all three K2c pairs — 4/4 pairs now**), the significance is there (CI excludes 0 by 27.7
Monte-Carlo sd), and the size is **not**: |D| = 0.00988 is **half of M1** and its CI's
lower magnitude 0.00458 is **below M2** — the term fails the materiality test at *both*
margins.

And the reason is visible in the leg's own numbers. The composition term does not keep
growing in absolute size as attenuation falls; **it tracks the recovery level, which is
collapsing faster**:

| leg | pair | predicted r | recovery level (mean of the pair) | \|D\| | \|D\| as % of level |
|---|---|---|---|---|---|
| K2c | P1 | 0.78 | 0.160380 | 0.003335 | 2.079% |
| K2c | P2 | 0.68 | 0.126038 | 0.012168 | 9.654% |
| K2c | P3 | 0.56 | 0.089030 | 0.013559 | 15.230% |
| **K2d** | **FR-45** | **0.45** | **0.061991** | **0.009879** | **15.937%** |

From 0.56 to 0.45 the **fraction** flattened (15.23% → 15.94%) while the **level** fell 30%
— so the absolute term fell 27%, from 0.013559 to 0.009879. K2c's planner adjudication
expected "a fourth, higher-state target would very likely breach the margin"; the measured
answer is that it cannot, because an absolute margin is being chased by a quantity that is
approximately proportional to a recovery that is going to zero. **The composition term
along the (share, φ) iso-attenuation direction peaked near attenuation 0.56 and is now
declining in absolute terms.**

### 1.5 The carrier: SPECIES-SPECIFIC, and the carrier is the OCCASION-BOUND species

Both species pairs are **MAT-SIG** at the dual margins, with **the same sign**, and the
sign is **positive**: `field(slow arm) > field(int arm)`.

| pair | slow-arm design | int-arm design | D | \|D\| / M2 | \|D\| as % of level |
|---|---|---|---|---|---|
| `SP-68` | slow 0.2927, int 0 | slow 0.1463, **int 0.2807** | **+0.030351** | 3.04× | 28.85% |
| `SP-56` | slow 0.4974, int 0 | slow 0.2487, **int 0.3769** | **+0.027061** | 2.71× | 39.38% |

At card attenuation matched to 1e-16 in prediction and ~1e-4 in measurement, replacing half
the persistent state with its card-equivalent amount of **occasion-bound** person content
costs the reader **25–30% of its remaining trait recovery**. So:

1. **The composition term is real, material, and 2.7–3.1× larger in the species direction
   than in the persistence direction at the same attenuation** (SP-68's |D| = 0.0304 vs
   K2c P2's 0.0122 at r = 0.68; SP-56's 0.0271 vs K2c P3's 0.0136 at r = 0.56 — both
   almost exactly 2.5× and 2.0×). The frontier probe was looking down the *weak* axis.
2. **The carrier is not persistent author-state.** The registration's own framing —
   "driven by persistent author-state specifically, or by ANY non-trait person content" —
   gets an answer that is neither of the offered readings in its intuitive form: the
   reader is species-*specific*, but it is the **occasion-bound, zero-persistence** species
   that is expensive. Persistent state, which the card punishes hardest (per unit variance
   it attenuates ≈ 1.9× / 1.5× more than interaction content at these designs, §0.4), is
   the species the *reader* handles comparatively well.
3. The card sees the contrast too, in the opposite ledger: within-pair GAP ratios
   `gap(a)/gap(b)` = **1.789** (SP-68) and **1.749** (SP-56) at matched attenuation, versus
   **3.882** for FR-45 (continuing K2c's 4.04 / 4.08 / 3.98 series).

### 1.6 A POST-HOC descriptive companion that unifies all six pairs (not a registered claim)

Computed **after** `decision.json` existed and disclosed as such; `decision.json` untouched;
written to `results/m4_k2d_frontier_carrier/post_hoc_descriptive.json`.

Score each pair by the difference in **total non-trait person variance share** (slow +
interaction, as a fraction of total panel variance) rather than by anything the card
weights:

| leg | pair | r | person var (a) | person var (b) | Δvar = a − b | D | κ = D/Δvar |
|---|---|---|---|---|---|---|---|
| K2c | P1 | 0.78 | 0.032764 | 0.026214 | +0.006550 | −0.003335 | −0.509131 |
| K2c | P2 | 0.68 | 0.087802 | 0.073265 | +0.014537 | −0.012168 | −0.837004 |
| K2c | P3 | 0.56 | 0.149209 | 0.130770 | +0.018438 | −0.013559 | −0.735387 |
| K2d | FR-45 | 0.45 | 0.199026 | 0.181856 | +0.017170 | −0.009879 | −0.575385 |
| K2d | SP-68 | 0.68 | 0.087802 | **0.128101** | **−0.040299** | **+0.030351** | −0.753151 |
| K2d | SP-56 | 0.56 | 0.149209 | **0.187659** | **−0.038451** | **+0.027061** | −0.703777 |

**One coefficient fits all six**, across two orthogonal design directions and attenuation
0.45–0.78: OLS through the origin gives **κ = −0.7220359963712748**, R² (against the mean)
**0.9935185860651237**, max |residual| **0.002518007987644547**; the six per-pair κ have
mean −0.6856391504742056, sd 0.12131302641134484, range [−0.837, −0.509].

Read plainly: **at matched card attenuation, the reader loses ≈ 0.72 units of trait
recovery per unit of raw non-trait person variance — regardless of which species that
variance is in.** The card, by contrast, weights the two species by `v_full(m, φ) ≈ 0.77`
vs `1/m ≈ 0.07–0.125`. The apparent "species specificity" of §1.5 is then not the reader
preferring one species: it is the reader **counting person content by raw variance while
the card counts it by its own averaging weights** — and the matched-attenuation design,
which equalizes the card's count, necessarily *unequalizes* the reader's. This also
explains the frontier's failure without any new mechanism: along the (share, φ) direction
Δvar is small and shrinking (+0.0184 at r = 0.56 → +0.0172 at r = 0.45), so the term cannot
grow. **This is a hypothesis with 6 points and no registration behind it. It is offered as
the next leg's estimand, not as a finding.**

### 1.7 L-M [prior .70] — HOLD, and 9.2× louder than the trait channel

FR-45's Δmixed = **+0.09057085992114061**, CI [+0.08492199727666237, +0.09605704140944434],
se 0.00283114911630157 — **positive (K2c's direction) with the CI excluding 0**. L-M
**HOLDS**. At the frontier the mixture trade is **9.17×** the b-only |D| (K2c's ratio at
matched attenuation was ≈ 4.3×): what the reader gains on the state-inclusive mixture it
loses on the trait, and the exchange rate steepens as attenuation falls.

SP pairs' Δmixed (**descriptive only**, as registered): SP-68 **+0.0034648537544723487** CI
[−0.006000959455307166, +0.012538706167386207] (**includes 0**); SP-56
**+0.011889777605738044** CI [+0.003576082895872018, +0.020335025870763784] (excludes 0).
A clean dissociation: in the **persistence** direction the mixture channel moves *opposite*
to the trait channel and much larger; in the **species** direction it moves the *same* way
and much smaller. The K2c "trade" is a property of the persistence axis, not of composition
in general.

### 1.8 q-update over all 19 arms (descriptive, NO GATE)

Pooled OLS of `log(field/λ)` on `log(predicted attenuation)` over **19 arms** (6 K2b + 7
K2c + 6 K2d), world blocks resampled within each leg-group, B = 2000, seed = master:

**q = 1.8528700746510731, CI [1.7147417060355998, 1.999586491101811]**, one-sided 5th
percentile 1.73739381617801, **R² = 0.8679753334914586**. λ-invariance verified: q at λ_K2b
minus q at λ = 1 is **2.220446049250313e-16**. Against K2c's 13-arm
**1.9337620539521978** [1.7337263621727161, 2.1932591297891246], the shift is
**−0.08089197930112468** — the quadratic reading survives (q > 1, CI excludes 1), but note
what happened to the fit: **R² fell from 0.958 to 0.868**. The six new arms include two
pairs sitting at *identical* x with field values 25–30% apart, which is the composition
term made visible as scatter in the pooled curve. A single power law in card attenuation
is no longer a good description of 19 arms, and its degradation is not noise — it is the
term this leg measured.

### 1.9 Power, honestly: the 2-world pilot under-estimated the paired sd

The registered gate G2d′ is evaluated in Part 0 on the pilot and **passed** for all three
pairs with no escalation. The **realized** paired sd was larger than the pilot's:

| pair | pilot paired sd | realized paired sd | ratio | pilot MDE @32 | **realized MDE @32** | target | \|D\| / realized MDE |
|---|---|---|---|---|---|---|---|
| `FR-45` | 0.00764050 | 0.015689164414951044 | 2.05× | 0.00390731 | **0.008023351258716671** | 0.020 | 1.23 |
| `SP-68` | 0.00984801 | 0.020289709969008626 | 2.06× | 0.00503621 | **0.010376044619923088** | 0.010 | 2.93 |
| `SP-56` | 0.00260028 | 0.020351803224591312 | 7.83× | 0.00132977 | **0.010407798764832322** | 0.010 | 2.60 |

FR-45 meets its target at the realized sd; **the two SP pairs miss theirs by 3.8% and
4.1%** (0.010376 and 0.010408 against 0.010). This is disclosed, not repaired: the
registered gate is a Part-0 gate on the pilot, and re-escalating after seeing the
hypothesis numbers would be exactly the post-hoc design change the discipline forbids. The
shortfall is also inconsequential — both SP effects are **2.6–2.9× their own realized
MDE** and land MAT-SIG with lower |D| CI endpoints of 0.0235 and 0.0203, more than double
M2. **No claim in this leg is tiered.** The structural lesson stands on its own: a 2-world
pilot estimates a paired sd on **1 degree of freedom**, and here it was off by up to 7.8×
in the direction that flatters the design.

### 1.10 Rule 13 (B = 2000 → 20 000)

**0 clauses triggered, 0 BOUNDARY.** No gated interval endpoint came within 2× its
Monte-Carlo sd of its boundary, so no clause required the 10×B re-run. Closest approaches,
in units of the endpoint's Monte-Carlo sd (post-hoc descriptive, `decision.json` untouched):
**FR-45 27.75**, **SP-68 21.75**, **SP-56 14.23**. G1d′'s matching clauses were likewise far
from ±0.005. Nothing in this leg's verdict is Monte-Carlo fragile.

### 1.11 What this leg does NOT decide (limitations, not hedges)

- **The frontier is unresolved, and P4d″'s registered remedy is predicted by this leg's own
  data to fail.** P4d″ says "K2e extends the frontier or the worlds (once)". Extending the
  frontier **downward** will not work: §1.4 shows the absolute term is already declining
  with the level. Extending the **worlds** will not work either: the term is not
  underpowered — FR-45's whole CI lies inside ±M1, so more worlds tighten an interval that
  is already bounded below materiality. What would work is changing the **direction** of
  the probe (the species axis is 2–3× louder at the same attenuation) or replacing the
  absolute margin with a level-relative one — but the margin is registered and this
  executor does not get to change it.
- **The species result cannot separate "species" from "raw person variance".** §1.6 shows a
  single raw-variance coefficient fits all six pairs, including the sign reversal. To
  separate "the reader is species-specific" from "the reader counts raw variance", a design
  must match **raw non-trait person variance** across arms while varying species — the
  mirror image of this leg's matching, and cheap to build with the same machinery.
- **Both facts are consequences of the same choice**: matching on the card's currency. The
  design did exactly what it was registered to do; what it cannot do is tell us which
  currency the *reader* uses without a second matching.

### 1.12 Anomalies (with timing)

- **A-1 (Part 0, before any hypothesis number existed).** The registration's **lean-level**
  adjudication space is not a partition, on rule 15's first application. Enumeration found
  **8 overlaps and 4 gaps of 49** in L-S, and **1 unrouted cell (MAT-SIG(+)) of 7** in the
  pivot routing (§0.6). Resolved before arms by RN-7's pre-declared named non-registered
  readings, following K2c's RN-4 precedent. **Did not bind:** every pair landed in a
  non-INDET cell, and all twelve pathological combinations require an INDET pair.
- **A-2 (finalize, after the hypothesis numbers existed).** The two-split **GAP** prediction
  from K2a's algebra is contained by its measured CI in **4/6** arms; the two misses are
  exactly the two arms carrying a large `w_int` — SP68int measured 0.03517425778896466 CI
  [0.033598, 0.036701] vs prediction 0.033513253705482804 (**+4.96%**), SP56int measured
  0.05760690373660443 CI [0.055945, 0.059244] vs 0.05574326247680422 (**+3.34%**); the four
  w_int = 0 arms sit at +0.61% … +1.69% and all contain. K2a validated the algebra at
  `w_int ∈ {0, equal-share}`; these arms carry interaction variance shares of 0.084 and
  0.113, well outside that. **Impact on this leg: none.** GAP is not a gated quantity here,
  the gated quantity is the **attenuation**, which contains its prediction in **6/6** at max
  0.278% relative error and matches within-pair 6–10× inside the ±0.005 gate. Recorded as
  an instrument note for K2a's algebra at large `w_int`.
- **A-3 (Part 0, provenance).** Because `k2b.run_field_world` is called unmodified, deployed
  corpus tags literally read `m4k2b-K2D-<arm>-w<k>`; they are hash labels only and every K2d
  tag is disjoint from every K2b and K2c tag (RN-6).
- **A-4 (Part 0, continuity, not a defect).** `SP-68-slow` and `SP-56-slow` are solved to the
  same targets at the same φ as K2c's P2a and P3a, and the solver returns **bit-identical**
  shares (0.29267462506992153, 0.4973617623232523) — the two legs share those two design
  cells exactly, at different seed lineages.
- **A-5 (finalize, after the numbers existed).** The realized paired sd exceeded the 2-world
  pilot's by 2.05×–7.83×, leaving the two SP pairs 3.8%/4.1% short of their registered MDE
  target at the executed n (§1.9). Disclosed, not repaired; no claim tiered because both
  effects are ≥ 2.6× their own realized MDE.

No crashes, no re-runs, no background jobs, no monitors, no stage over its Part-0 estimate.

### 1.13 K2d's brief to the planner

1. **The frontier question is answered in substance even though L-F missed.** Along the
   (share, φ) iso-attenuation direction the composition term **does not cross materiality at
   0.45, and cannot be made to** by pushing attenuation lower — it is ≈ 16% of a recovery
   level that is itself collapsing. P4d″'s "extend the frontier or the worlds once" is the
   registered remedy; this leg's own data predicts both variants fail, and the reason is
   quantitative, not rhetorical (§1.4, §1.11).
2. **The material composition term exists — on the other axis.** The species pairs are
   MAT-SIG at both margins with unanimous sign and effects 2.0–2.5× the persistence-axis
   effects at the same attenuation. If the planner wants T4 re-typed on a **material**
   composition term, the evidence is already here; it just is not the evidence L-F asked
   for, and this executor will not re-route a registered lean to collect it.
3. **A concrete estimand for the next registration.** `field ≈ λ·r^q − κ·V_person` with
   **κ ≈ 0.72 (R² 0.9935 over six pairs, both directions, r ∈ [0.45, 0.78])** — the reader
   counts non-trait person content by **raw variance**, the card counts it by its own
   averaging weights, and every result in K2c and K2d is the gap between those two
   accountings. The discriminating design is the mirror of this leg's: **match raw person
   variance, vary species** — if D goes to zero there, "species-specific" is dead and
   κ·V_person is the term.
4. **Rule 15 works, and it needs to be applied one level up.** The per-pair table was
   enumerated and was a partition; the predicates *built on* that table were not, and the
   registration verified only the former. The rule should read: enumerate the space of
   **verdicts**, not the space of **cells**.
5. **q is now a worse description than it was.** 19 arms, q = 1.853 [1.715, 2.000], but
   R² 0.958 → 0.868. Two arms at identical x and 25–30% apart in y are not scatter; the
   pooled power law is being asked to absorb the very term the line is trying to name.
