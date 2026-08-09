# SUICA M4-K2c — Matched-attenuation pairs: is the reader a transform of card algebra, or does it read state composition? (link-free)

**Tier:** EXPLORATORY · label-free · synthetic throughout.
**Banner:** synthetic worlds calibrated to an opened-panel regime, exploratory.
**Registration:** `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md` § "M4-K2c — Matched-attenuation
pairs …", REGISTERED 2026-08-09 BEFORE RUN, commit `8adb0a9`. The registration text is
binding; this executor did implementation and execution only.
**Script:** `scripts/run_suica_m4_k2c_matched_pairs.py`
**Artifacts:** `results/m4_k2c_matched_pairs/` (gitignored).
**Theory:** `docs/SUICA_IDENTITY_THEORY_V1.md` T4 (S3), appendices H and I.

---

## Part 0 — written to disk 2026-08-09T09:14:02.941062+00:00 (UTC), BEFORE any main arm

Part 0 ran on RESERVED pilot worlds **9701–9702** (disjoint from main indices 0…63).
`results/m4_k2c_matched_pairs/gates.json` and `part0_arms.json` carry every number below
at full precision; the `arms` stage refuses to run unless every Part-0 gate passes **and
this report exists on disk** (`require_part0()`). Part-0 wall time **11.615 s**
(share solve 0.107 s, pilot 11.131 s).

### 0.0 Standing-rule-14 compliance (verified, as instructed)

**No gate and no branch lean in this leg compares quantities across scales.**
G0c′ re-derives K2b's own numbers against themselves; G1c′ compares **card attenuation to
card attenuation**; G2c′, G4c′, L-1, L-2 and PARTIAL-C compare **field agreement to field
agreement**. The single cross-scale object is **L-3**, which the registration itself
declares *descriptive-to-lean, no branch weight*; and L-3 does pin its link — a log-log
power law whose exponent `q` **is** the estimand, so rule 14's first clause is satisfied
for it, while its second clause (link-free redesign) is satisfied by everything that
adjudicates T4. This is the defect-#20 repair applied to K2c's own design.

### 0.1 Register-notes (rule 9 — open conventions fixed BEFORE any hypothesis number, all readings reported)

- **RN-1 (seed lineage).** K2c's own lineage: `master_seed 20260817`, salt
  `m4k2c-world`; the world seed depends on the **world index only**, so both arms of a
  pair — which differ in φ — share the trait `b`, the AR innovations, the frame shocks,
  the interaction loadings and the noise **bit-for-bit**. `D_k` is therefore a
  within-world difference.
- **RN-2 (corpus-tag provenance).** `k2b.run_field_world` is called **unmodified**
  (registration: "reuse its machinery wholesale"), so the corpus tag it builds keeps the
  literal prefix `m4k2b-`. The tag is only a hash label seeding the deployed
  transition-null permutation streams (`f1:199-206`); prefixing every K2c arm id with
  `K2C-` makes every tag disjoint from every K2b tag, which is what the fresh lineage
  requires.
- **RN-3 (which MDE in `m_k = max(0.020, MDE_k)`).** The registration does not say.
  **PRIMARY: the REALIZED-sd MDE at the executed n** (the resolution the leg actually
  achieved); **SECOND READING: the Part-0 pilot MDE.** Both are computed and reported per
  pair. (At the pilot values both margins are 0.020 anyway — see §0.5.)
- **RN-4 (the registered partition is INCOMPLETE — fixed before any arm).** L-1 (3/3 pairs
  `|D_k|` CI inside ±m_k) and L-2 (≥2/3 pairs CI excluding 0, one sign) are **not mutually
  exclusive**: a difference can be statistically resolved and still sit strictly inside the
  materiality margin (e.g. D = 0.012, CI [0.004, 0.019]). The registration gives no
  precedence. **Resolution:** simultaneous fire is scored **BOTH_FIRE**, a *named
  non-registered outcome* reported as such — **not** as either branch; **T4 is not
  re-typed on it**; both readings are reported at full precision; the substantive reading
  offered to the planner is "composition-sensitivity is real but sub-material at the
  registered margin". Symmetrically, 0/3 significant **without** 3/3 equivalence is
  `NO_REGISTERED_BRANCH` (underpowered — rule 2), not L-1.
- **RN-5 (L-3's x-variable).** **PRIMARY: the Part-0 PREDICTED attenuation** — a
  deterministic x, so no errors-in-variables dilution of the slope (which would bias `q`
  *downward*, i.e. against the registered direction). **SECOND READING: the measured card
  attenuation**, x fixed at its point value (x-uncertainty not propagated; K2b's measured
  attenuation error was ≤0.0975% relative — negligible against the y-spread). Both
  reported.
- **RN-6 (L-3's λ).** λ := K2b's arm-independent reader efficiency
  **0.17417497661611914**. The OLS **slope is invariant to λ** (subtracting the constant
  log λ from y cannot change a slope), so L-3's verdict does not depend on this number at
  all; finalize verifies the invariance numerically against λ = 1.
- **RN-7 (t-quantiles).** MDE(80%, α=.05, paired, n) = (t_{.975,n−1} + t_{.80,n−1})·sd/√n
  with `n=32 → (2.039513446396408, 0.853370295696944)` and
  `n=64 → (1.998340542520741, 0.8473639122756463)`; cross-checked against
  `scipy.stats.t.ppf` (scipy 1.17.1), **max abs deviation 0.0**. See anomaly **A-1**.

### 0.2 The COMPUTED shares (G1c′, Part-0 half — the designed identity)

Arm *a* is solved by bisection-to-adjacent-doubles for the nominal target on the
K2a-validated attenuation algebra at φ = .90; arm *b* is then solved to arm *a*'s
**achieved** attenuation at φ = .98, so the within-pair predicted difference is bounded by
the solver's own resolution rather than by the target's representability. Pure algebra —
no world is generated, no gauge is invoked.

| pair | target r | **s_ka** (φ .90) | r(P_ka) | **s_kb** (φ .98) | r(P_kb) | \|Δr\| | matched (≤1e-12) | share gap s_kb − s_ka |
|---|---|---|---|---|---|---|---|---|
| `P1` | 0.78 | **0.10921276830855525** | 0.78 | **0.0873786568216755** | 0.7800000000000001 | **1.110223e-16** | True | −0.0218341114868797 |
| `P2` | 0.68 | **0.29267462506992153** | 0.68 | **0.24421800730418725** | 0.68 | **0.0** | True | −0.0484566177657343 |
| `P3` | 0.56 | **0.4973617623232523** | 0.5600000000000002 | **0.4359007987784457** | 0.5600000000000002 | **0.0** | True | −0.0614609635448066 |

**G1c′ Part-0 clause: PASS, 3/3** (max \|Δr\| = 1.110223e-16 ≤ 1e-12).
The post-arms half of G1c′ (measured within-pair card attenuation difference, pooled CI
inside ±0.005, else the pair is **VOID** for composition claims) is adjudicated with the
arms in §1.

### 0.3 Part-0 point predictions — all 7 arms, computed before any world existed

Panel: K1-pinned — **985 authors**, F2 m-multiset `{8: 272, 12: 200, 16: 513}`, 4 contexts
(`AskReddit`, `AskWomen`, `politics`, `worldnews`), **565 retained**, 12 (context, m) norm
cells. All arms `w_int = 0`, noise share fixed at 0.70, non-noise signal 0.30 with the
non-state remainder split 1:1 over {trait, frame} (K2b's RN-2/RN-3 invariants, unchanged).

| arm | role | share | φ | A (μ) | B (slow) | Cc (frame) | E (noise) | ρ_int pred | ρ_cont pred | **GAP pred** | **r(card→b) pred** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `P1a` | pair | 0.109212768309 | 0.90 | 0.13361808 | 0.03276383 | 0.13361808 | 0.70 | 0.5666427671 | 0.5422101924 | 0.0244325747 | 0.780000000000 |
| `P1b` | pair | 0.0873786568217 | 0.98 | 0.13689320 | 0.02621360 | 0.13689320 | 0.70 | 0.5758670207 | 0.5702575446 | 0.0056094760 | 0.780000000000 |
| `P2a` | pair | 0.29267462507 | 0.90 | 0.10609881 | 0.08780239 | 0.10609881 | 0.70 | 0.5791688569 | 0.5170285997 | 0.0621402572 | 0.680000000000 |
| `P2b` | pair | 0.244218007304 | 0.98 | 0.11336730 | 0.07326540 | 0.11336730 | 0.70 | 0.6034359012 | 0.5886243792 | 0.0148115220 | 0.680000000000 |
| `P3a` | pair | 0.497361762323 | 0.90 | 0.07539574 | 0.14920853 | 0.07539574 | 0.70 | 0.5921429700 | 0.4921963720 | 0.0999465981 | 0.560000000000 |
| `P3b` | pair | 0.435900798778 | 0.98 | 0.08461488 | 0.13077024 | 0.08461488 | 0.70 | 0.6325440473 | 0.6077908902 | 0.0247531571 | 0.560000000000 |
| `A1anc` | anchor | 0.02 | 0.90 | 0.14700000 | 0.00600000 | 0.14700000 | 0.70 | 0.5602154972 | 0.5556207911 | 0.0045947060 | 0.827178459312 |

**The design's whole point, visible in this table:** the two arms of a pair are predicted
to have *identical* card attenuation while their **card GAP differs by 4.4× (P1),
4.2× (P2), 4.0× (P3)** — the persistence signature is loud in the card even where the
attenuation is matched to 1e-16. If the field is a function of attenuation alone, `D_k`
must vanish; if the field reads composition, it must not.

### 0.4 G0c′ — anchors, bit-exact (PASS)

Re-derived by round-trip re-read of `results/m4_k2b_t4_branch/arm_A*_field.csv` and
`part0_predictions.csv`, with `P_identity` from `gates.json` G1b — **residual exactly 0.0
on all six**:

| anchor | persisted (K2b `decision.json`) | re-derived | residual | bit-exact |
|---|---|---|---|---|
| A1 field recovery | 0.177888649457317 | 0.177888649457317 | 0.0 | ✔ |
| A4 field recovery | 0.07543949574114414 | 0.07543949574114414 | 0.0 | ✔ |
| S | 0.10244915371617286 | 0.10244915371617286 | 0.0 | ✔ |
| S/P | 0.3811151367233824 | 0.3811151367233824 | 0.0 | ✔ |
| λ | 0.17417497661611914 | 0.17417497661611914 | 0.0 | ✔ |
| S/(λ·P) | 2.1881164799198363 | 2.1881164799198363 | 0.0 | ✔ |

K2a anchor cell `phi0.9_occ8_intzero` re-derived from K2a's own seeds:
**2048 rows × 35 columns, max abs residual 0.0 (bit-exact)** — the same anchor K2b's G0b
used.

### 0.5 G2c′ — power (rule 2), 2-world pilot

| n | pair | pilot paired sd | MDE(80%, .05, paired) | ≤ 0.020 |
|---|---|---|---|---|
| **32** | `P1` | 0.00719108554729916 | **0.003677481078755207** | True |
| **32** | `P2` | 0.022432392533120446 | **0.011471800543764012** | True |
| **32** | `P3` | 0.03661105054756279 | **0.018722687246097304** | True |
| 64 | `P1` | 0.00719108554729916 | 0.002557963022096392 | True |
| 64 | `P2` | 0.022432392533120446 | 0.007979494920405259 | True |
| 64 | `P3` | 0.03661105054756279 | 0.013023028704746894 | True |

**PASS at n = 32 for 3/3 pairs — NO ESCALATION.** `worlds_selected = 32`.
Pilot equivalence margins m_k = max(0.020, MDE_k) = **0.020** for all three pairs.
Pilot within-pair differences (2 worlds, sign only — not a hypothesis reading):
P1 −0.00413439, P2 −0.00230675, P3 −0.00585531.

### 0.6 G4c′ — liveness (rule 3) and within-pair non-degeneracy (rule 10) (PASS)

Across the four designed attenuation levels, **both channels move strictly monotonically**
on the pilot, in the predicted direction:

| designed level | pilot card attenuation | pilot field recovery |
|---|---|---|
| `A1anc` (pred .8272) | 0.8256025815661774 | 0.1791606151561937 |
| target 0.78 | 0.7777124196848088 | 0.1577040617906094 |
| target 0.68 | 0.6769278418982805 | 0.1275587600350152 |
| target 0.56 | 0.5563494058704399 | 0.0882876752178615 |

Within-pair non-degeneracy (the composition contrast is real, not a relabelling):

| pair | panel RMS a vs b | design share gap | realized state share a → b | non-degenerate |
|---|---|---|---|---|
| `P1` | 0.015771056303408443 | −0.021834111486879748 | 0.03272527761779042 → 0.026297147273000386 | True |
| `P2` | 0.025968121116981404 | −0.048456617765734290 | 0.08763887206448177 → 0.07344059986172077 | True |
| `P3` | 0.034082191904282400 | −0.061460963544806624 | 0.14881668531517814 → 0.13095595095192794 | True |

Frame-channel centred residual max **1.2212453270876722e-15** (T3's designed cancellation,
measured not assumed). Realized-vs-design variance share max abs deviation
**0.005912041781161753** ≤ 0.01.

### 0.7 G3c′ — rule-11 satisfiability with directions; rule-13 spec (PASS)

Resampling spec: **B = 2000, seed = master_seed 20260817**; rule-13 stability re-check at
**B = 20000 (≥10×B)** for any clause whose boundary lies within 2 Monte-Carlo endpoint
sd's of the estimate.

| lean | clause | direction | satisfiable | projected margin evidence |
|---|---|---|---|---|
| G1c′ | measured within-pair card attenuation diff CI inside ±0.005 | two-sided (equivalence) | **True** | projected (conservative, *unpaired*) half-widths P1 0.0013754246, P2 0.0017639586, P3 0.0021790754 vs the ±0.005 margin; the paired bootstrap actually used is strictly tighter |
| L-1 | \|D_k\| CI inside ±m_k, 3/3 | two-sided (equivalence, rule 4) | **True** | projected 1.96·se(D_k) = P1 0.0024915840, P2 0.0077724275, P3 0.0126850819 vs margins 0.020 |
| L-2 | D_k CI excludes 0 in ≥2/3 AND one sign | two-sided per pair; sign consistency deterministic | **True** | exclusion is satisfiable for any non-degenerate CI |
| PARTIAL-C | exactly 1/3 significant, or mixed signs | deterministic given L-2's significant set | **True** | partition complement; RN-4 fixes the simultaneous-fire reading |
| L-3 | pooled q from log(field/λ) on log(attenuation), 6 K2b + 7 K2c arms: q > 1, CI excluding 1 | one-sided in content; evaluated on the registered two-sided 95% CI, one-sided 5th percentile reported alongside | **True** | 13 points spanning predicted attenuation 0.519352…0.827178 |

### 0.8 G5c′ — hygiene (PASS)

Round-trip parsing (`float_precision='round_trip'`) on every artifact read; foreground
chunked stages (`part0`, `arms --worlds a-b`, `finalize`); **0 background jobs, 0
monitors**; rule-12 source-object naming inherited from K2b's G4b table (the generator
objects are literally K2b's, called unmodified).

**Part-0 stage estimates (the stop-and-report basis).** World build 0.01928555965423584 s
mean; per world index, all 7 arms, both channels: **5.565257430076599 s** ⇒ **arms total at
n = 32 ≈ 178.088 s**, chunked at 16 worlds. **Stop-and-report threshold = 2× = 356.176 s.**

### 0.9 Registered adjudication space (restated as it will be scored)

`D_k = field(P_ka) − field(P_kb)`, pooled **paired** world-block bootstrap (shared world
indices, B = 2000, seed = master).

- **L-1 (function-of-attenuation) [prior .40]** — 3/3 pairs `|D_k|` CI inside ±m_k,
  m_k = max(0.020, MDE_k). → P2c′: T4 re-types **T4-simple-with-link**.
- **L-2 (composition-sensitive) [prior .45]** — ≥2/3 pairs `D_k` CI excludes 0 **and** all
  significant `D_k` share one sign. → P3c′: T4 re-types **T4-reader-mediated (composition
  form)**.
- **PARTIAL-C** — exactly 1/3 significant, or significant with mixed signs. → P4c′: K2d.
- **BOTH_FIRE / NO_REGISTERED_BRANCH** — RN-4's completion of the partition; reported as
  such, no re-typing.
- **L-3 [prior .70, descriptive-to-lean, NO branch weight]** — pooled `q` > 1 with CI
  excluding 1.
- **P1c′** — G1c′ matching fails in ≥2 pairs → instrument question, **no theory
  adjudication**.

---

<!-- RESULTS BELOW THIS LINE WERE WRITTEN AFTER THE ARMS RAN -->

## Part 1 — Results (written after the arms ran)

**Executed exactly as registered.** 7 arms × **32 worlds** (Part-0 power ladder selected
32; **no escalation**), `master_seed 20260817`, K1-pinned panel (985 authors, **565
retained**, 4 resolved contexts), card channel 565 × 32 = **18 080 pooled authors/arm**,
**224 adjudicated deployed-gauge world runs** + 14 reserved-pilot runs. Foreground chunked
stages, **0 background jobs, 0 monitors**. **Total compute 154.739 s**
(part0 11.620 s, arms 64.638 s + 65.168 s, finalize 13.313 s) — inside the Part-0 estimate
(178.088 s) and far inside the 2× stop-and-report threshold (356.176 s).

### 1.1 VERDICT

`BOTH_FIRE__SIGNIFICANT_BUT_SUB_MATERIAL__MATCH_EXACT__L3_HOLD`

**L-1 FIRES and L-2 FIRES SIMULTANEOUSLY.** Under **RN-4** (fixed in Part 0, before any
hypothesis number existed) this is a **named NON-REGISTERED outcome**, reported as such:
**T4 is NOT re-typed**, and **no pivot fires** — P1c′, P2c′, P3c′, P4c′ all FALSE.
L-3 HOLDS. Matching is exact: **0 pairs VOID**.

The substance in one sentence: **at card attenuation matched to 1e-16, the field
difference is real, perfectly sign-consistent, and monotone in the composition
contrast — but it is small enough to sit inside the registered materiality margin.**

### 1.2 G1c′ post-arms — the designed identity survived contact (0 VOID; P1c′ does not fire)

| pair | measured r(P_ka) | measured r(P_kb) | **Δ measured** | 95% CI (paired bootstrap) | margin | inside |
|---|---|---|---|---|---|---|
| `P1` | 0.7805266914381881 | 0.7805616928776264 | **−3.500143943835354e-05** | [−0.00019941215262716806, +0.00013702369578437448] | ±0.005 | ✔ |
| `P2` | 0.6806542583317795 | 0.6807747247946402 | **−0.00012046646286067997** | [−0.0004453412577974908, +0.00021935297697847351] | ±0.005 | ✔ |
| `P3` | 0.5607390065039654 | 0.5609581620712140 | **−0.00021915556724860785** | [−0.0007001775976884117, +0.00027959279759260096] | ±0.005 | ✔ |

The realized match is **23×–143× tighter than the registered margin**. The attenuation
algebra transfers to gauge dims at matched-pair precision. **3/3 pairs VALID for
composition claims.**

Instrument continuity (not a registered K2c gate — K2a/K2b certified the instrument):
card attenuation CI contains the Part-0 prediction in **7/7** arms and the card GAP in
**7/7**; max abs attenuation relative error **0.001711003698596066 (0.171%)**.

### 1.3 The adjudication quantity D_k = field(P_ka) − field(P_kb)

Pooled **paired** world-block bootstrap on shared world indices, B = 2000, seed = master.

| pair | field(P_ka) | field(P_kb) | **D_k** | 95% CI | se | realized sd (paired) | MDE_k realized | **m_k** | inside ±m_k | CI excludes 0 | sign | worlds D<0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `P1` | 0.15871254618530495 | 0.16204747162068810 | **−0.0033349254353831808** | [−0.007617710100740499, +0.0011074921964934288] | 0.002223343017693846 | 0.013100049592732043 | 0.006699292365687496 | 0.020 | ✔ | ✘ | − | 20/32 |
| `P2` | 0.11995446641787935 | 0.13212198302374079 | **−0.012167516605861444** | [−0.017430001829670642, −0.006619210190334735] | 0.00273581701593062 | 0.015474502882138934 | 0.007913574546972555 | 0.020 | ✔ | **✔** | − | 27/32 |
| `P3` | 0.08225066394872052 | 0.09580994783492192 | **−0.01355928388620139** | [−0.018647677326514903, −0.008674340005325598] | 0.002538466953859292 | 0.014740157117410176 | 0.007538034214808339 | 0.020 | ✔ | **✔** | − | 26/32 |

**RN-3 second reading (pilot-MDE margins):** identical verdicts — the pilot MDEs
(0.003677, 0.011472, 0.018723) are all ≤ 0.020, so m_k = 0.020 under both readings and
`abs_ci_inside_m_k_pilot_margin` is True 3/3. The two readings do not diverge.

Paired-t intervals (second reading, no bootstrap): P1 [−0.00805799697204763,
+0.001388146101281268]; P2 [−0.01774666984412181, −0.006588363367601078];
P3 [−0.018873677242836215, −0.008244890529566567] — same three verdicts.

- **L-1 [prior .40] FIRES** — 3/3 pairs, `|D_k|` CI inside ±m_k.
- **L-2 [prior .45] FIRES** — **2/3** pairs (P2, P3) with CI excluding 0, and **all
  significant D_k share one sign (negative)**; direction: *the φ = .98 arm recovers MORE*.
  P1's D_k is negative too (−0.00333), just not resolved.
- **PARTIAL-C does not fire** (2 significant, not 1; signs not mixed).
- **BOTH_FIRE** — RN-4's completion of the partition.

### 1.4 What the sign means, and the honest size of the effect

Within a pair, arm *a* has the **larger state share and lower persistence** (φ = .90); arm
*b* the **smaller share and higher persistence** (φ = .98), at **identical predicted card
attenuation**. `D_k < 0` in **3/3 pairs** ⇒ **at fixed attenuation, the arm carrying more
state share (equivalently, less persistent state) loses MORE of the person.** The field is
therefore **not** a function of card attenuation alone.

Magnitude, relative to the arm's own recovery level:

| pair | \|D_k\| / mean pair field level | measured GAP_a / GAP_b | Δ measured GAP (a − b) | D_k / ΔGAP |
|---|---|---|---|---|
| `P1` | **2.079%** | 4.037289 | 0.0188379454 | −0.177032 |
| `P2` | **9.654%** | 4.084957 | 0.0473712628 | −0.256854 |
| `P3` | **15.230%** | 3.980428 | 0.0752732030 | −0.180134 |

The composition contrast is loud in the *card*: at matched attenuation the two arms'
measured card GAPs differ by a factor of **≈4** in all three pairs (the persistence
signature the two-split probe was built to read, K2a/appendix H). The reader converts that
4× card difference into a **2–15%** trait-recovery difference. It grows monotonically with
the target's state content (P1 → P2 → P3), which is why L-1's 3/3 is *fragile*:

> **P3's equivalence clause holds by 0.001352 — only 0.533 se of D_k from the ±0.020
> boundary** (8.92 Monte-Carlo endpoint sd, so rule 13 does not flag it, but the
> *sampling* headroom is half a standard error). A fourth, higher-state target would very
> likely breach the margin. **L-1 should not be read as "the field is a function of
> attenuation"; it should be read as "the composition effect is below 0.020 over the
> attenuation range 0.56–0.78, and rising."**

### 1.5 The descriptive channel says the same thing much louder (mixed truth; no gate)

At matched attenuation, arm *a* recovers **less of the person and MORE of the
state-inclusive mixture** — a straight trade, with every CI excluding 0:

| pair | Δ b-only (= D_k) | **Δ mixed-truth recovery (a − b)** | 95% CI | **Δ (mixed − b-only)** | 95% CI |
|---|---|---|---|---|---|
| `P1` | −0.0033349254 | **+0.00690393** | [+0.00309391, +0.01096980] | **+0.01023885** | [+0.00758742, +0.01300449] |
| `P2` | −0.0121675166 | **+0.02470275** | [+0.01918629, +0.03053346] | **+0.03687027** | [+0.03246204, +0.04166867] |
| `P3` | −0.0135592839 | **+0.05849219** | [+0.05194404, +0.06514736] | **+0.07205148** | [+0.06511950, +0.07932837] |

The sign flips between the two truth objects at *identical card attenuation*. This is
K2b's L-D (the gauge prefers the mixture) reappearing as a **within-pair, link-free,
attenuation-matched** statement: what the reader gains on the mixture it loses on the
trait. On the mixture channel the composition effect is **4.3× (P3) larger** than on the
trait channel.

### 1.6 L-3 [prior .70, descriptive-to-lean, NO branch weight] — HOLD

Pooled OLS of `log(field/λ)` on `log(attenuation)` over **13 arms** (K2b's A1–A6 + K2c's
7), λ = 0.17417497661611914:

- **q = 1.9337620539521978**, 95% CI **[1.7337263621727161, 2.1932591297891246]**,
  one-sided 5th percentile **1.7596140020708688**, **R² = 0.9581580947902524**,
  intercept 0.3848760798299043.
- **q > 1 ✔ and CI excludes 1 ✔ → L-3 HOLDS.**
- **RN-5 second reading (x = measured card attenuation):** q = **1.9360338584090482**,
  CI [1.7342166898270828, 2.196563507630189], R² = 0.9597295088511272 — same verdict.
- **RN-6 λ-invariance verified numerically:** q at λ = K2b's value and q at λ = 1 differ
  by **exactly 0.0**.

The reader loses the trait as roughly the **1.93rd power** of what the card algebra loses
— the K2b over-response (`S/(λP) = 2.1881164799198363`) now measured as a smooth pooled
exponent across two legs and 13 arms, and **not** an artifact of two extreme arms.

### 1.7 Rule 13 (B = 2000 → 20000)

**0 clauses triggered, 0 BOUNDARY.** Closest approaches (post-hoc descriptive, computed
after adjudication from persisted artifacts; `decision.json` untouched): P1's L-2
zero-exclusion clause **8.34 MC-sd**, P3's L-1 equivalence clause **8.92 MC-sd**, P2's L-1
equivalence clause 15.73 MC-sd; all others ≥ 40 MC-sd. Every gated interval clause sits
further than 2 Monte-Carlo endpoint sd's from its boundary at B = 2000, so no ≥10×B
re-check was required.

### 1.8 Continuity: the A1-anchor at a fresh seed lineage (no gate)

`A1anc` (.02, .90) at `master_seed 20260817` / salt `m4k2c-world` reads **b-only recovery
0.1785831487097378**, CI [0.17058563431737153, 0.18747529579718702]; K2b's `A1` at
`20260816` / `m4k2b-world` read **0.177888649457317**. Difference
**+0.0006944992524207938**, well inside the CI — the leg reproduces K2b's anchor cell
under an independent seed lineage.

### 1.9 What this leg does NOT decide (stated as a limitation, not a hedge)

A matched-attenuation pair moves **share and persistence together** along the
iso-attenuation curve — that is what "same attenuation, different composition" *means* in
a two-parameter state model. So K2c establishes **that** the field reads composition at
fixed attenuation and **in which direction**, but it cannot say whether the carrier is the
state **share** or the state **persistence**. That separation is exactly what a K2d
localization would need: a third state parameter (or an n_occ lever) to break the
share/φ collinearity along the iso-attenuation curve.

### 1.10 Anomalies (with timing)

- **A-1 (found in Part 0, BEFORE any main arm; no hypothesis number existed).** K2b's
  hardcoded t-quantile table carries `t_{.80,31} = 0.8534705711311653`, which is
  **+0.00010027543422130858** above the correct **0.853370295696944**. **Impact on K2b:
  none** — K2b's power ladder selected n = 8 and never evaluated its n = 32 entry. K2c
  uses scipy-verified values (RN-7; max abs deviation vs `scipy.stats.t.ppf` **0.0**,
  scipy 1.17.1). Reported, not repaired in K2b's source (K2b's artifacts are sealed).
- **A-2 (structural, foreseen at design time and resolved in Part 0 as RN-4).** The
  registered adjudication space is **not a partition**: L-1 and L-2 can both fire. It
  happened. The resolution was fixed and written to disk before any main arm.
- **A-3 (provenance, RN-2).** Because `k2b.run_field_world` is called unmodified, the
  deployed corpus tags literally read `m4k2b-K2C-<arm>-w<k>`. They are hash labels only,
  and every K2c tag is disjoint from every K2b tag.
- No crashes. No re-runs. No background jobs. No monitors. No stage exceeded its Part-0
  estimate.

### 1.11 K2c's brief to the planner

1. **Do not re-type T4 on this leg** (RN-4). The registered space could not classify the
   result because L-1 and L-2 are not disjoint.
2. **The link-free question IS answered in substance:** composition-sensitivity at fixed
   attenuation is **real (2/3 pairs resolved), unanimous in sign (3/3 negative), and
   monotone in state content (2.1% → 9.7% → 15.2% of level)**. "The field is a fixed
   monotone transform of card attenuation" (T4-simple-with-link) is **falsified as a
   strict claim** — it survives only as an approximation with a ≤0.02 error budget over
   attenuation 0.56–0.78, and the error is growing.
3. **The materiality margin, not the physics, is what kept L-1 alive** — P3 sits 0.533 se
   from breaching it. If the planner wants a decision rather than a tie, the next
   registration should either extend the target range downward (a fourth pair at
   attenuation ≈ 0.45) or lower the margin with a justification that is not K2b's swing
   scale.
4. **L-3 upgrades the over-response from a two-arm ratio to a curve:** q = 1.934,
   CI [1.734, 2.193], R² = 0.958 over 13 arms and two legs.
5. **The mixture channel is where the composition effect is loudest** (up to +0.0585 at
   P3, CI excluding 0) and it points the opposite way from the trait channel. A
   K2d/repair leg that targets the trade directly (does de-framing move the trait side
   without moving the mixture side?) has a much larger effect to work with than D_k.
