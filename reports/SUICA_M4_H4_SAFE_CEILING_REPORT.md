# SUICA M4-H4 — Where does the safe region end, and does the lever generalize?

Tier: **EXPLORATORY, label-free, synthetic.** Registered in
`docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md`, "M4-H4 registration
(2026-08-03, BEFORE run)", preceded by "M4-H3 planner adjudication note"
(same date, seventh standing rule). Ledger row `M4-H4`. Script:
`scripts/run_suica_m4_h4_safe_ceiling.py`. Artifacts:
`results/m4_h4_safe_ceiling/{decision.json, gates.json, disp_rows.csv,
g2_liveness_rows.csv, truth_recovery_rows.csv, author_level_truth_rows.csv,
g3check_rows.csv, offset_shares_by_arm.csv, g5_arm_by_metric_table.csv}`.

## 0. Where this leg picks up

M4-H3 found the safe lever's joint winner (`basis_shrinkage_0.50`, 41.56%
displacement reduction) sitting AT its own registered, non-extendable
ladder's upper endpoint, with reduction still rising — the safe ceiling was
unlocated. Separately, S3's registered-order share fell materially in 2 of 3
worlds at that winner but ROSE in `source_rotated_feedback` at **every**
rung H3 tested (0.02 through 0.50) — a total, ladder-wide non-response in
one specific world. M4-H4 extends the ladder upward
(`lambda / median(retained eig)` in `{0.50, 1.0, 2.0, 4.0, 8.0}`, with 0.50
carried forward as the bridge/anchor point) to answer three registered
questions: does a rung finally turn unsafe (locating the ceiling)? Does
`source_rotated_feedback` ever respond (testing whether its non-response was
structural or merely a strength effect)? And, per the seventh standing rule
(harmless vs actively-good winners must both be reported), does the
actively-good ceiling sit strictly below the harmless one?

## 1. Part 0 — inherited from H2 via H3, unchanged

This leg performs no new Part 0 audit and introduces no new normalization,
scaling, centering or reference choice. It varies the identical single Part
0 step H3 varied (item 8a, whitening scale, regularized reading,
`m4_condition_manifold_estimator.py:580-583`, formula `1/sqrt(eig + λ)`,
`λ = ratio × median(retained eig)`), at a registered ladder EXTENSION
upward: **`{0.50, 1.0, 2.0, 4.0, 8.0}`**. `0.50` is the shared bridge point
with H3's own upper endpoint and is carried as an anchor; `whitening_
unscaled` is retained unchanged as the known-unsafe reference (anchor).

**Arms.** `deployed`, `basis_shrinkage_0.50` and `whitening_unscaled` are
computed by **literal calls into H3's own dispatch function**
(`h3._basis_for_h3_arm`), not reimplemented — bit-identical to H3's
construction by construction. The four genuinely new rungs
(`basis_shrinkage_{1.00,2.00,4.00,8.00}`) are this leg's only new compute:
H3's own `_whitening_for_shrinkage_ratio` (unchanged formula) applied to
H2's own `_ingredients_for_arm`, which falls through to deployed defaults
for source-scale/centering/rank-tolerance automatically, since none of this
leg's arm names match H2's three special-cased strings — exactly as every
prior ladder rung in H2 and H3 already relies on.

**Disclosed superset on G1.** The outer registration's own G1 clause names
only `basis_shrinkage_0.50` and `whitening_unscaled` as anchors. This
script additionally anchors `deployed` against H3's own persisted rows (a
third chain), because `deployed` is the mandatory zero-point for every
metric this leg computes, verifying it is free, and it can only strengthen
G1, never loosen it. Both readings are reported in Section 3; they agree.

**Lean (b)'s materiality margin** is carried forward from H3's Part 0
unchanged: a **≥10% relative fall** of S3's share from deployed's own,
census over all 3 worlds (`LEAN_B_MATERIALITY_RATIO = 0.10`). A no-floor
"falls at all" companion is also computed.

**Winner definition (seventh standing rule).** Two winners are computed and
reported, both restricted to the five ladder rungs (`whitening_unscaled`
excluded as "the known-unsafe reference," per H3's own convention — both
eligibility readings computed, Section 4): **HARMLESS** (largest reduction
among rungs whose recovery does not worsen, one-sided ±0.02, both budgets)
and **ACTIVELY GOOD** (largest reduction among rungs whose recovery is
improved, CI entirely on the better side, both budgets). Every lean below
states explicitly which winner it uses.

## 2. Design as executed

Worlds: H3's own three `HIGH_GAP_WORLDS`, all 8 repetitions — unchanged.
Three metrics at every one of the 7 arms: (1) Leg 14's `disp_v2` (PRIMARY);
(2) M4-E2's S1–S4 shares, reported **per world** (not only the 3-world
mean), since world heterogeneity is now itself a registered question; (3)
truth-referenced recovery, both `TRUTH_BUDGETS = (4.0, 8.0)`. Metric grains
are identical to, and justified identically as, H2/H3 (rep grain n=24
PRIMARY / world n=3 companion for displacement; world census n=3 for
shares; author grain n up to 384 PRIMARY / world n=3 companion for
recovery) — restated fresh per the fifth standing rule, not merely
inherited by citation.

## 3. Gates

### G0 POWER (MDE stated before adjudicating, citing H3's own numbers)
**Metric 1.** H3's own largest rep-grain half-width across its 6 arms, on
the identical worlds/reps/metric design, was 0.737. This design's realized
half-widths range **0.715–0.802** across the six arms here — comfortably
below the 25%-of-mean informational bar (4.515, `= 0.25 × 18.059`, H3's own
persisted deployed mean, reproduced here to 9.7e-17) — no arm is
underpowered for metric 1.

**Metric 3.** The winner-eligibility margin is ±0.02 (one-sided); this
line's own strict `G0_FRACTION_BAR = 0.01` is the disclosure threshold.
Realized author-grain half-widths **rise monotonically with ratio**:
0.0099 (`0.50`) → 0.0115 (`1.00`) → 0.0128 (`2.00`) → 0.0138 (`4.00`) →
0.0146 (`8.00`) → 0.0172 (`whitening_unscaled`). Only `basis_shrinkage_0.50`
sits under the strict 0.01 bar; **all four new rungs, including the
harmless winner `basis_shrinkage_1.00`, are nominally flagged
UNDERPOWERED against this strict internal bar.**

**This is disclosed plainly and checked against the decision-relevant
margin, not silently read as a clean result.** At the harmless winner
(`basis_shrinkage_1.00`): 4x mean diff +0.00496, CI **[−0.00658, 0.01649]**
— the CI's upper bound sits 0.0035 below the 0.02 margin (17.5% of the
margin's width as buffer); 8x mean diff +0.00648, CI **[−0.00502,
0.01798]** — buffer only 0.0020 (10.1% of the margin). **Both
classifications are decisive (the full CI lies below the margin), but with
markedly less headroom than H3's own winner** (`basis_shrinkage_0.50`: 4x
buffer 71.7% of margin, 8x buffer 65.9%). A two-sided reading of the margin
(computed as a robustness check, Section G4) agrees WITHIN at both budgets
for both arms — the classification does not flip under either reading —
but the 8x buffer at the harmless winner is the thinnest margin-clearance
this line has recorded for a HARMLESS (not merely "not yet distinguishable
from worse") classification.

### G1 ANCHOR
Registered-literal (2 chains: `basis_shrinkage_0.50`, `whitening_unscaled`)
and disclosed superset (3 chains: + `deployed`), both against H3's own
persisted `disp_rows.csv` / `offset_shares_by_arm.csv` /
`truth_recovery_rows.csv`, full row-level joins:

| chain set | max abs diff | pass |
|---|---|---|
| registered-literal (2 arms) | 9.71e-17 | yes |
| disclosed superset (3 arms, incl. `deployed`) | 9.71e-17 | yes |

**`max_abs_diff = 9.71445146547012e-17`** — identical in value to H3's own
anchor against H2, because `deployed`'s construction is fully deterministic
(same operations, same order) and reproduces the same floating-point noise
pattern every time it is freshly rebuilt. This is a real end-to-end test:
`deployed` is independently rebuilt via a fresh context build in this leg's
own output directory (not a copy of H3's cache).

**Smoke-test companion (not a registered gate, disclosed):** before any
full-scale compute, the bridge rung was verified bit-for-bit against H3's
own dispatch function directly (`max|diff| = 0.000e+00` across all three
mechanism roles) — this leg's own dispatch for `basis_shrinkage_0.50` calls
`h3._basis_for_h3_arm` literally, so this is an exact-equality identity
check, not a numerical-closeness one.

### G2 BASIS LIVENESS
Materiality margin: 10% of deployed's median `disp_v2` (17.615).

| arm | median basis distance vs deployed | ratio to bar | live |
|---|---|---|---|
| `basis_shrinkage_0.50` | 10.939 | 6.21x | yes |
| `basis_shrinkage_1.00` | 12.345 | 7.01x | yes |
| `basis_shrinkage_2.00` | 13.940 | 7.91x | yes |
| `basis_shrinkage_4.00` | 15.293 | 8.68x | yes |
| `basis_shrinkage_8.00` | 16.309 | 9.26x | yes |
| `whitening_unscaled` | 22.292 | 12.66x | yes |

**All six arms LIVE**, smallest 6.2x the bar, monotone in ratio.

### G3 TRUTH-PATH INVARIANCE
Dual computation, all 7 arms, one spot-check per world. **`max_abs_diff =
0.0`** across 21/21 checks, tolerance 1e-12. **PASSES.**

### G4 MATERIALITY FORM
G0: CI-half-width-vs-bar equivalence per metric, MDE stated citing H3's own
numbers before adjudicating; every underpowered-vs-strict-bar comparison
flagged explicitly (Section G0), never silently read as a clean null. G1/G3:
degenerate exact-equality (1e-12). G2: ratio-to-scale liveness bound (10%).
Lean (a): per-rung one-sided WITHIN/OUTSIDE classification at ±0.02, a
property of the whole ladder. Lean (b): ≥10% relative-fall equivalence
across a 3-world census, at the harmless winner only. Lean (c): ordinal
ratio comparison built from the same one-sided classifications used to
build each pool. No gate is a nil-significance test on a known-nonzero
quantity.

**Disclosed robustness check (two-sided vs one-sided margin reading).**
Computed for every arm/budget on this leg's own data (not cited from H3):
**the two-sided classification agrees with the adopted one-sided reading in
every case that matters to a lean** — in particular, both readings classify
the harmless winner as WITHIN at both budgets (Section G0). The one-sided
reading is adopted (matches H3's own convention and the natural reading of
"does not worsen").

### Width-invariance — a mechanical correction, disclosed
The script's own `width_invariance_check.all_arms_identical_width` flag
reads **`false`** in `decision.json` — but this flag, as literally coded,
tests something stricter and less meaningful than "no width confound": it
collapses every arm's per-repetition min/max into one global set, which
conflates genuine between-repetition width variation (a pre-existing
property of the deployed `rank_tolerance=1e-6` threshold, orthogonal to
this leg, first disclosed by H3) with a potential between-ARM confound
within the same cell. **Found after the hypothesis-relevant numbers already
existed** (during this report's own write-up, verified directly from
`disp_rows.csv`): the correct, finer check — is width identical across all
7 arms within each of the 24 (world, repetition) cells — passes **0/24
disagreements**. Width varies 12→13 only between repetitions (specifically
`endogenous_creation_expansion` rep 6), affecting every arm in that cell
identically, exactly reproducing H3's own disclosed pattern one ladder
further. **No width confound; this leg's reductions are a clean
basis-shape effect**, unaffected by this reporting-layer flag naming issue,
which changes no adjudicated number.

## 4. G5 — DUAL-WINNER COMPLIANCE: the full table and both picks

**Full arm × {reduction, S3 per world, recovery both variants} table**
(sorted by rep-grain reduction, descending):

| arm | ratio | reduction (rep, n=24) | 95% CI | S3 `endogenous` | S3 `selection` | S3 `source_rotated` | S3 falls ≥10% all 3w | recovery Δ@4x | class@4x | recovery Δ@8x | class@8x | HARMLESS | ACTIVELY GOOD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `whitening_unscaled` | — | **64.71%** | [10.950,12.423] | 0.0490 | 0.0238 | 0.0482 | yes | +0.2741 | OUTSIDE | +0.2774 | OUTSIDE | **no** | no |
| `basis_shrinkage_8.00` | 8.0 | **52.20%** | [8.624,10.228] | 0.1783 | 0.2617 | 0.1845 | yes | +0.0605 | OUTSIDE | +0.0630 | OUTSIDE | **no** | no |
| `basis_shrinkage_4.00` | 4.0 | **50.88%** | [8.395,9.983] | 0.2098 | 0.2937 | 0.2077 | yes | +0.0375 | OUTSIDE | +0.0397 | OUTSIDE | **no** | no |
| `basis_shrinkage_2.00` | 2.0 | **48.88%** | [8.048,9.608] | 0.2282 | 0.3107 | 0.2335 | yes | +0.0188 | AMBIGUOUS | +0.0207 | AMBIGUOUS | **no** | no |
| `basis_shrinkage_1.00` | 1.0 | **45.79%** | [7.515,9.025] | 0.2433 | 0.3126 | 0.2624 | **yes** | +0.0050 | WITHIN | +0.0065 | WITHIN | **YES** | no |
| `basis_shrinkage_0.50` | 0.5 | 41.56% | [6.790,8.221] | 0.2705 | 0.3212 | 0.3019 | no (rises) | −0.0043 | WITHIN | −0.0030 | WITHIN | YES | no |
| `deployed` (reference) | — | — | — | 0.3323 | 0.3830 | 0.2953 | — | — | — | — | — | — | — |

**Recovery-safety filter, every non-deployed arm:** `basis_shrinkage_{0.50,
1.00}` qualify (does not worsen, both budgets). `basis_shrinkage_2.00` is
**AMBIGUOUS at both budgets** (its CI straddles the 0.02 margin itself:
e.g. 4x CI [0.006,0.032]) — neither confirmed harmless nor confirmed
unsafe. `basis_shrinkage_{4.00,8.00}` and `whitening_unscaled` are
confirmed **OUTSIDE** (unsafe) at both budgets. **No arm is actively good**
— `basis_shrinkage_0.50`'s and `basis_shrinkage_1.00`'s recovery
directions are `AMBIGUOUS_OR_NO_CHANGE` (CI straddles zero), not
`IMPROVED`.

**HARMLESS winner: `basis_shrinkage_1.00`, 45.79% reduction.** **ACTIVELY
GOOD winner (this leg's own ladder alone): NONE** — the actively-good pool
restricted to `{0.50,...,8.0}` is empty (Section 6 resolves this via the
combined-ladder reading).

**Target-only winner (the original, pre-sixth-standing-rule defect):
`whitening_unscaled`, 64.71% reduction, recovery destroyed (+0.274/+0.277,
OUTSIDE both budgets).** Reproduced exactly, on schedule, a third time.

**What a SINGLE-winner rule would have chosen and hidden.** H3's own
sixth-standing-rule "joint winner" (largest reduction among the harmless
pool, reported alone) would pick **`basis_shrinkage_1.00`** here too — the
identical arm as the harmless winner above, since harmless-only IS that
rule's definition. Reported alone, this hides that: (a) no arm anywhere in
this leg's own tested range is actively good, and (b) the harmless winner's
own recovery classification, while decisive, has markedly less statistical
headroom than H3's — exactly the kind of trade the seventh standing rule
exists to force into the open. The dual-winner report (this section) states
both facts explicitly rather than letting a single "winner: 1.00, 45.8%,
safe" headline stand alone.

**Disclosed ambiguity (reference eligibility), resolved and verified not to
matter.** Both readings (whitening_unscaled eligible / ladder-only) were
computed for both pools; all four agree exactly with the ladder-only
adopted reading, since the reference fails every pool regardless.

## 5. Ceiling-boundary disclosure

**The ceiling IS located, and it is interior — not another endpoint.**
`basis_shrinkage_{4.00, 8.00}` are confirmed **UNSAFE** (author-grain
OUTSIDE the ±0.02 margin at both budgets). The largest confirmed-harmless
ratio in this ladder is **1.0**; the smallest confirmed-unsafe ratio is
**4.0**; every harmless ratio is below every unsafe ratio, so the region is
formally contiguous by this leg's own registered test.

**But this contiguity claim needs one honest qualifier, stated plainly
rather than smoothed over:** `basis_shrinkage_2.00`, sitting between the
harmless winner and the confirmed-unsafe rungs, is **AMBIGUOUS** — neither
confirmed harmless nor confirmed unsafe, because its own CI straddles the
0.02 margin (Section 4). The located ceiling is therefore precise about
**where safety is confirmed to end** (no rung above 1.0 is confirmed
harmless) and precise about **where unsafety is confirmed to begin** (4.0),
but the interval `(1.0, 4.0]` is not fully resolved by this ladder's own
grain — `2.0` specifically would need a tighter design (larger n or a
narrower bracket) to classify decisively. This is disclosed as a genuine
resolution limit of this leg's own design, not glossed into "the ceiling is
exactly 1.0."

## 6. Leans — adjudicated exactly as registered

### Lean (a) CEILING LOCATED — **HOLDS**
At least one ladder rung is unsafe: `basis_shrinkage_4.00` (+0.0375/+0.0397,
OUTSIDE both budgets) and `basis_shrinkage_8.00` (+0.0605/+0.0630, OUTSIDE
both budgets) both clear the confirmed-unsafe bar decisively — their CIs sit
entirely above the 0.02 margin, not merely outside a point estimate. The
harmless region's upper bound is interior to this ladder (at or below 1.0),
not another non-extendable endpoint. **The PIVOT does not fire.**

### Lean (b) GENERALIZES OR NOT (at the HARMLESS winner, `basis_shrinkage_1.00`) — **HOLDS**

This is the leg's central, registered either-way test, and it resolves in
the branch H3 left open:

| world | deployed S3 | winner (ratio=1.0) S3 | relative fall | falls ≥10%? |
|---|---|---|---|---|
| `endogenous_creation_expansion` | 0.3323 | 0.2433 | **26.8%** | yes |
| `selection_creation_compensation` | 0.3830 | 0.3126 | **18.4%** | yes |
| `source_rotated_feedback` | 0.2953 | 0.2624 | **11.1%** | **yes** |

**`source_rotated_feedback` — the world that ROSE or stayed flat at every
single rung H3 ever tested (0.02 through 0.50, always ≥ deployed's 0.2953)
— now falls, clearing the 10% materiality floor with real if modest room
(11.1%, a 1.1-point margin over the floor).** This is not a knife-edge
artifact of exactly where the harmless winner landed: the full ladder shows
a **clean, monotonic decline** in this world's own S3 share once past the
0.50 knife-edge: deployed 0.2953 → `0.50` 0.3019 (the H3-reproduced small
RISE) → `1.00` 0.2624 → `2.00` 0.2335 → `4.00` 0.2077 → `8.00` 0.1845 →
`whitening_unscaled` 0.0482 — a smooth, accelerating fall with ratio, not a
single crossing that happens to land near the winner.

**Per the registration's own either-way framing, this is the finding, not
a failure:** `source_rotated_feedback`'s total non-response at every H3
rung was a **strength effect**, not a structural immunity — the mechanism
Part 0 (H2) predicted (S3-subspace mass moving under whitening-scale
regularization) is present in this world too, it simply required roughly
double H3's own working ceiling (ratio 1.0 vs 0.50) to become visible above
this design's own noise floor. The registered alternative outcome — "the
non-response is structural" — is refuted by this leg's own data, not left
undecided.

### Lean (c) THE LEVELS SEPARATE — **HOLDS** (Reading B, adopted)

**Reading A (this leg's own ladder alone, `{0.50,...,8.0}`): NOT
COMPUTABLE.** The actively-good pool restricted to this leg's own five new
rungs is empty (no arm here shows a CI entirely on the better side) — there
is no actively-good ceiling within this leg's own newly-tested range to
compare against the harmless ceiling of 1.0.

**Reading B (combined ladder to date, ADOPTED): HOLDS.** Combining H3's own
already-G1-anchored, already-adjudicated rungs (`0.02, 0.05, 0.10, 0.20` —
cited from its persisted artifacts, not recomputed) with this leg's own
(`0.50, 1.0, 2.0, 4.0, 8.0`) gives a 9-point ladder whose reduction is
**confirmed monotonic in ratio end to end** (16.0% → 23.2% → 28.9% → 34.7%
→ 41.6% → 45.8% → 48.9% → 50.9% → 52.2%). On this combined ladder:

- **Harmless ceiling: `basis_shrinkage_1.00`, ratio 1.0** (this leg).
- **Actively-good ceiling: `basis_shrinkage_0.20`, ratio 0.2** (H3, cited).

**0.2 < 1.0 — the levels separate by a full order of magnitude in ratio
terms.** Pushing the lever from the actively-good ceiling to the harmless
ceiling buys an additional 45.8% − 34.7% = 11.1 percentage points of
displacement reduction, at the cost of recovery moving from *significantly
better than deployed* (0.20's CI entirely negative) to *statistically
indistinguishable from deployed* (1.00's CI straddling zero, Section G0) —
a concrete, quantified answer to "what pushing harder costs."

**Adopted reading and why:** Reading B, because "the actively-good ceiling"
is a property of the whole registered shrinkage lever this line has been
building across H2→H3→H4, not an artifact of where any one leg's own ladder
happens to start; the cross-leg comparison is valid because `deployed` (the
shared zero point both percentages are computed against) is G1-anchored
bit-identical throughout the entire chain (Section G1). Reading A is
reported because it is the more conservative, this-leg-only construction,
and it is honestly reported as non-computable rather than forced to a
verdict it cannot support.

## 7. Verdict

**PIVOT DOES NOT FIRE** — at least one rung (in fact two) is confirmed
unsafe. Per the registered adjudication:

- **(a) CEILING LOCATED — HOLDS.** `basis_shrinkage_{4.00,8.00}` are
  confirmed unsafe; the harmless region's upper bound (1.0) is interior to
  this ladder. One rung (`2.00`) is honestly reported AMBIGUOUS rather than
  forced into either side (Section 5).
- **(b) GENERALIZES — HOLDS.** At the harmless winner (`basis_shrinkage_
  1.00`), S3 falls materially in 3/3 worlds, including `source_rotated_
  feedback` (11.1%) for the first time anywhere in this line — refuting the
  "structural non-response" alternative the registration reserved for a
  miss.
- **(c) LEVELS SEPARATE — HOLDS** (Reading B, adopted). The actively-good
  ceiling (0.2, from H3) sits strictly below the harmless ceiling (1.0,
  from this leg) — an order of magnitude apart in ratio terms.

**Verdict: `CEILING_LOCATED__MECHANISM_GENERALIZES_3_OF_3_WORLDS__LEVELS_SEPARATE`.**
All three leans HOLD — a clean sweep, and a materially different outcome
shape from every prior carrier-found leg in this line (M4-G1, M4-H2, M4-H3
all left at least one lean missing or in a genuine middle ground). This
leg's own two nuances, both disclosed rather than smoothed over: the
harmless winner's recovery classification, while decisive, has markedly
less headroom than H3's own winner (Section G0), and the safe/unsafe
boundary has one genuinely ambiguous rung (`2.00`) inside it rather than a
single clean threshold (Section 5).

## 8. Mechanical notes

No mechanical problems affecting any hypothesis-relevant number: the smoke
test, all three context+oracle stages, all three G3 spot-checks, all 21
(world, arm) compute stages, and the assemble stage completed with zero
Tracebacks or RuntimeErrors, first attempt, entirely foreground with
explicit long timeouts (no background jobs, no monitors). Wall-clock
matched H2/H3's own reported order of magnitude exactly: context+oracle
186.6s/189.2s/191.2s per world; each arm stage 21–28s after the shared
regeneration cache warmed. One reporting-layer correction, found **after**
the hypothesis-relevant numbers already existed (Section 3, "Width-
invariance"): the script's own coarse `all_arms_identical_width` flag reads
`false` because it conflates between-repetition and between-arm variation;
the correct per-(world,repetition) check, computed directly from
`disp_rows.csv` during this report's write-up, confirms 0/24 disagreements
— no width confound, and no adjudicated number changes. Data-integrity
check before any hypothesis-relevant number was read: `disp_rows` (168
rows, matching 3 worlds × 7 arms × 8 reps exactly), `truth_recovery_rows`
(10,752 rows, matching 3×7×8×2×2×16 exactly), `author_level_truth_rows`
(768 rows per arm, matching 3×8×16×2 budgets exactly) all checked clean.

## 9. Hand-off

The safe lever's harmless ceiling, within the ladder tested to date
(`0.02` through `8.0`), is **ratio 1.0** (45.79% displacement reduction,
recovery statistically indistinguishable from deployed) — located with one
honestly-disclosed unresolved rung (`2.0`, AMBIGUOUS) between it and the
confirmed-unsafe region starting at `4.0`. A leg that wanted to resolve
`2.0` decisively, or narrow the true harmless/unsafe crossing further than
`(1.0, 4.0]`, would need a tighter bracket or larger n at that specific
point — not registered or performed here. Separately, and now settled for
this line: the actively-good ceiling (`0.2`, from H3) sits durably below
the harmless ceiling (`1.0`, from this leg) — the two notions this line
first had to distinguish at H3 are now shown, quantitatively, to diverge by
an order of magnitude, not merely differ at the margin. Most substantively:
`source_rotated_feedback`'s total non-response across the whole of H3's own
ladder is now resolved as a **strength effect, not a structural one** — the
mechanism Part 0 predicted is present in all three `HIGH_GAP_WORLDS`, just
at different thresholds of the same lever. Whether that threshold
heterogeneity itself has a further structural explanation (why does
`source_rotated_feedback` need roughly double the push the other two
worlds needed) is a new, narrower question this leg's design surfaces but
does not resolve.
