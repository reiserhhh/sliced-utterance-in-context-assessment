# SUICA M4-H5 — Under the safe lever, what carries the surviving ~54%?

Tier: **EXPLORATORY, label-free, synthetic.** Registered in
`docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md`, "M4-H5 registration
(2026-08-03, BEFORE run)", preceded by "M4-H4 planner adjudication note"
(same date). Ledger row `M4-H5`. Script:
`scripts/run_suica_m4_h5_residual_carrier.py`. Artifacts:
`results/m4_h5_residual_carrier/{decision.json, gates.json, disp_rows.csv,
g3check_rows.csv, offset_shares_by_arm.csv, share_table.csv,
knife_edge_rows.csv}`.

## 0. Where this leg picks up

M4-H4 swept all three of its own leans and located the safe lever's
harmless ceiling at ratio 1.0 (`basis_shrinkage_1.00`, 45.79% displacement
reduction, CI [7.515,9.025] rep grain) and, separately, confirmed the
actively-good ceiling at ratio 0.2 (`basis_shrinkage_0.20`, H3's own winner,
34.66% reduction, recovery CI entirely on the better side). At the harmless
ceiling, S3's registered-order share collapses materially in 3/3 worlds —
but **54% of the displacement survives**. M4-E2 had already found, at
`deployed`, that the residual (S4) was the largest SINGLE piece
(.4015–.4464 registered order) even before any repair. M4-H5 asks the
obvious next question: under the repair, does that residual become a new,
attackable dominant carrier — or is what survives genuinely distributed,
setting ~46% as the practical ceiling of subspace-targeted repair?

## 1. Part 0 — inherited unchanged; this leg's only new code is a 2-way router

This leg performs **no new Part 0 audit and touches no basis-construction
formula**. All three arms are literal calls into already-anchored,
already-adjudicated predecessor dispatch functions:

- `deployed` and `basis_shrinkage_1.00` (H4's HARMLESS winner) →
  `h4._basis_for_h4_arm` / `h4._arm_offset_and_shares_h4`.
- `basis_shrinkage_0.20` (H3's ACTIVELY-GOOD winner) →
  `h3._basis_for_h3_arm` / `h3._arm_offset_and_shares_h3` (H4's own ladder
  starts at 0.50 and does not know this ratio).

Both winners are **registered by name** in the outer M4-H5 registration —
no winner-selection computation happens in this leg.

**What "decompose the residual displacement" means, stated precisely.**
Throughout this line, an arm's `registered_shares`/`reverse_shares` are
ALREADY the S1–S4 sequential decomposition of THAT ARM's OWN offset vector.
At a repaired arm, that offset's norm IS "the surviving displacement" M4-H4
measured (45.79%/34.66% reduced), and its shares ARE "what fraction of that
surviving displacement each subspace carries." H3/H4 already compute this
for every arm they touch — so this leg's job is to gather deployed's,
`basis_shrinkage_1.00`'s and `basis_shrinkage_0.20`'s own share
decompositions, **freshly recomputed** (fresh context build, this leg's own
output directory, so G1 is a real end-to-end test) and anchored to
`<=1e-12` against three independently-persisted comparators.

**Scope reduction, disclosed (ambiguity, resolved, stated before compute).**
The M4-H5 registration's Design/Metrics/Leans sections name only
displacement and S1–S4 shares — unlike every prior G/H2/H3/H4 registration,
`TRUTH_BUDGETS`/truth-referenced recovery is never mentioned. **Reading A
(ADOPTED):** Metric 3 is out of this leg's scope — already adjudicated at
both repaired arms by H3 (lean c) and H4 (lean b/c); recomputing it here
changes no adjudicated quantity, so the "oracle" stage and the
`TRUTH_BUDGETS` regeneration loop are skipped entirely (a genuine
compute-scope reduction). **Reading B (disclosed, not adopted):** "G3
truth-path invariance where applicable" could be read as requiring the full
truth machinery regardless. **Resolution:** G3 is honored under Reading A's
own reduced scope — a lightweight world-build faithfulness spot-check
(budget=1.0 regen vs. flat-style refit, h2's own `_g3_spot_check` pattern,
restricted to this leg's 3 arms) still runs and is gated (Section 3), so
"where applicable" is satisfied without resurrecting a metric this leg does
not adjudicate on.

**G2, redefined for this leg.** H2/H3/H4's own G2 asked whether an arm's
*basis* differs materially from deployed's. This leg's G2 — registered as
"DECOMPOSITION LIVENESS" — asks whether the arm's own *share decomposition*
differs materially from deployed's, answered directly from the shares this
leg already computes (no basis-distance computation needed). Materiality
bound: reuses `LEAN_B_MATERIALITY_RATIO = 0.10` (H3's own Part 0 constant,
itself citing H2's `G2_MATERIALITY_RATIO`), generalized from "S3's share
alone" to "at least one of the four subspace shares," so as not to
presuppose which subspace would turn out to move.

## 2. Design as executed

Worlds: H4's own three `HIGH_GAP_WORLDS`, unchanged. Arms: `deployed`,
`basis_shrinkage_1.00`, `basis_shrinkage_0.20`. One metric family at every
arm: M4-E2's S1–S4 shares, both registered order (`S1→S2→S3→S4`) and
reverse order (`S3→S2→S1→S4`) — M4-E2 disclosed ordering sensitivity, M4-H1
reproduced it exactly, this leg keeps the comparison live throughout, per
the outer task's explicit instruction. `disp_v2` is also computed, but only
as the G1 anchor target — it is not one of this leg's adjudicating metrics
(already adjudicated by H3/H4 themselves).

**Grain.** Shares: world census (n=3), no CI — identical convention to
M4-E2/H2/H3/H4's own Metric-2 treatment. Displacement: anchor-only, not
recomputed as its own CI in this leg.

## 3. Gates

### G0 POWER (MDE statement before adjudicating, citing H3's/H4's own numbers)

No half-width/MDE is computable for the shares metric in the usual CI
sense — no finer sampling unit is defined at the world level (the same
convention every predecessor leg used for its own Metric 2). What is
stated instead, before any lean is adjudicated:

1. **This leg's own freshly computed shares** (3 arms × 3 worlds × 2
   orderings × 4 subspaces, n=72) range **[0.0099, 0.5288]** — the 0.40
   pivot bar sits well inside this demonstrated dynamic range, not at a
   floor or ceiling.
2. **The actual empirical target (S4) is cited from M4-E2's own persisted
   numbers as already measurably non-zero and already near the pivot bar
   BEFORE any repair**: registered-order S4 share at `deployed` =
   {`endogenous_creation_expansion`: 0.4269, `selection_creation_compensation`:
   0.4015, `source_rotated_feedback`: 0.4464} — all 3 worlds already ≥0.40,
   matching the M4-G registration's own "largest single piece is the
   residual at .40–.45" framing. This leg's question is therefore not being
   asked at a noise floor.
3. The finest resolution of the "≥2/3 of 3 worlds" count is 1/3, 2/3 or
   3/3 — no intermediate value is possible. Order-sensitivity and any
   near-tie against the 0.40 bar or between the top-2 subspaces are
   computed for every (arm, world, ordering) and disclosed explicitly
   (`knife_edge_rows.csv`, Section 4) — this design's own substitute for a
   half-width.

**Metric-1 anchor context (not adjudicating):** H4's own rep-grain
half-width for `basis_shrinkage_1.00` = 0.7549; reduction 45.79%, CI
[7.515,9.025]. H3's own for `basis_shrinkage_0.20`: reduction 34.66%, CI
[5.613,6.905]. Cited only to support that the two repaired arms are
non-degenerately different from deployed — already independently
established by H3's/H4's own G1/G2 gates.

**Rule-3 (vacuous-knob) check:** H4's own G2 BASIS LIVENESS certified
`basis_shrinkage_1.00` live at **7.01×** its own 10% bar; H3's own G2
certified `basis_shrinkage_0.20` live at **5.39×**. This leg's own G2
(Section 3, below) independently re-verifies the *share decomposition*
itself, not merely the basis, moves materially.

### G1 ANCHOR — all three arms to ≤1e-12

| chain | comparator | max abs diff | pass |
|---|---|---|---|
| `deployed` shares (registered+reverse+standalone+family) | M4-E2 `decision.json['offset_table']` | **0.0** | yes |
| `basis_shrinkage_1.00` displacement (24 rows) | M4-H4 `disp_rows.csv` | **0.0** | yes |
| `basis_shrinkage_0.20` displacement (24 rows) | M4-H3 `disp_rows.csv` | **0.0** | yes |
| **registered-literal, combined** | | **0.0** | **yes** |
| disclosed superset: repaired-arm shares vs. H3's/H4's own `offset_shares_by_arm.csv` | H3/H4 | 9.71e-17 | yes |
| disclosed superset: `deployed` displacement vs. H3's AND H4's own `disp_rows.csv` | H3/H4 | 0.0 | yes |
| **overall (registered-literal + disclosed superset)** | | **1.78e-15** | **yes** |

The registered-literal chain — the three comparators the M4-H5 registration
names by name ("shares vs M4-E2 for `deployed`; displacement vs M4-H3/M4-H4
for the repaired arms") — is **exactly 0.0**. The disclosed superset (full
share decomposition for the repaired arms against H3's/H4's own persisted
CSVs, and `deployed`'s displacement against both) is **not required by the
registered clause** but can only strengthen G1; its own max is
1.78e-15 — floating-point noise, 3 orders of magnitude under the 1e-12
tolerance, and it cannot change which arms pass since it only adds checks.
This is a real end-to-end test: every arm is rebuilt from a fresh context in
this leg's own output directory, not a copy of H3's/H4's cache.

### G2 DECOMPOSITION LIVENESS

Materiality bound: ≥10% relative movement (`LEAN_B_MATERIALITY_RATIO`,
reused) in at least one of the four registered-order subspace shares,
required in **every** world.

| arm | world | max \|relative share delta\| | subspace with largest move | live |
|---|---|---|---|---|
| `basis_shrinkage_1.00` | `endogenous_creation_expansion` | 36.8% | S2 | yes |
| `basis_shrinkage_1.00` | `selection_creation_compensation` | 30.7% | S4 | yes |
| `basis_shrinkage_1.00` | `source_rotated_feedback` | 51.6% | S2 | yes |
| `basis_shrinkage_0.20` | `endogenous_creation_expansion` | 27.8% | S2 | yes |
| `basis_shrinkage_0.20` | `selection_creation_compensation` | 22.6% | S4 | yes |
| `basis_shrinkage_0.20` | `source_rotated_feedback` | 34.6% | S2 | yes |

**Both arms LIVE in all 3 worlds**, 2.3×–5.2× the 10% bar. (S2's own
relative move is often numerically largest because its deployed baseline
share is tiny — 0.012–0.026 — so small absolute changes register as large
relative ones; S4's own absolute share deltas, the quantity this leg's
leans actually adjudicate on, are reported directly in Section 5 and are
themselves 0.060–0.123, 6.0–12.3 percentage points, at the harmless
winner.)
The decomposition demonstrably differs from deployed's — not assumed.

### G3 — world-build faithfulness (scope-reduced; does not gate any lean)

Budget=1.0 freshly-regenerated panels reproduce `context['flat']`-sourced
refits exactly, all 3 arms, one spot-check per world (9 checks total).
**`max_abs_diff = 0.0`.** Passes. Per the disclosed scope-reduction
(Section 1), this re-certifies the shared context-build machinery this leg
still depends on; it does not gate any lean, since Metric 3 (truth
recovery) is out of this leg's registered scope.

### G4 MATERIALITY FORM

G0: no CI-based bar for the shares metric (world-census, no sampling unit,
per the established convention); Metric-1 numbers cited as anchor context
only. G1: degenerate exact-equality (≤1e-12) against three independently-
persisted comparators, registered-literal and disclosed-superset both
reported. G2: relative-share-delta materiality bound (≥10% in ≥1 of 4
subspaces, every world), reusing `LEAN_B_MATERIALITY_RATIO`'s own
convention. G3: degenerate exact-equality (≤1e-12), faithfulness only, not
lean-gating. Lean (a): per-subspace, per-world absolute threshold
classification (share ≥ 0.40) aggregated to a ≥2-of-3-worlds count against
a fixed registered bar. Lean (b): categorical identity check. Lean (c):
set-membership check built from the same absolute-threshold classification
as lean (a), independently re-applied at the second arm. No gate is a
nil-significance test on a known-nonzero quantity.

## 4. The full arm × subspace × world share table, both orderings

**Registered order (S1→S2→S3→S4, ADOPTED for adjudication):**

| arm | world | S1 safety complement | S2 supervision span | S3 norm/scale modes | **S4 residual** |
|---|---|---|---|---|---|
| `deployed` | endogenous creation expansion | 0.2285 | 0.0122 | 0.3323 | **0.4269** |
| `deployed` | selection creation compensation | 0.2002 | 0.0154 | 0.3830 | **0.4015** |
| `deployed` | source rotated feedback | 0.2319 | 0.0264 | 0.2953 | **0.4464** |
| `basis_shrinkage_1.00` (HARMLESS) | endogenous creation expansion | 0.2260 | 0.0167 | 0.2433 | **0.5140** |
| `basis_shrinkage_1.00` (HARMLESS) | selection creation compensation | 0.1487 | 0.0140 | 0.3126 | **0.5247** |
| `basis_shrinkage_1.00` (HARMLESS) | source rotated feedback | 0.1910 | 0.0400 | 0.2624 | **0.5066** |
| `basis_shrinkage_0.20` (ACTIVELY GOOD) | endogenous creation expansion | 0.2161 | 0.0156 | 0.3037 | **0.4646** |
| `basis_shrinkage_0.20` (ACTIVELY GOOD) | selection creation compensation | 0.1925 | 0.0170 | 0.2984 | **0.4921** |
| `basis_shrinkage_0.20` (ACTIVELY GOOD) | source rotated feedback | 0.1916 | 0.0355 | 0.3212 | **0.4517** |

Under registered order, **S4 is the only subspace to ever clear 0.40** at
either repaired arm, in any world — S3 comes closest (up to 0.3126 at the
harmless winner, up to 0.3212 at the actively-good winner) but its own
maximum across all 6 repaired-arm cells (0.3212) still sits 0.079 below the
bar. S4 itself rises from an already-elevated deployed baseline (0.40–0.45)
to **0.51–0.52** at the harmless winner and **0.45–0.49** at the
actively-good winner — in every one of the 3 worlds, at both arms.

**Reverse order (S3→S2→S1→S4, disclosed companion — M4-E2's own ordering-
sensitivity comparison kept live, per the outer task's instruction):**

| arm | world | S1 safety complement | S2 supervision span | S3 norm/scale modes | **S4 residual** |
|---|---|---|---|---|---|
| `deployed` | endogenous creation expansion | 0.1632 | 0.0261 | 0.4459 | **0.3649** |
| `deployed` | selection creation compensation | 0.1232 | 0.0112 | 0.5288 | **0.3369** |
| `deployed` | source rotated feedback | 0.1225 | 0.0119 | 0.4984 | **0.3672** |
| `basis_shrinkage_1.00` (HARMLESS) | endogenous creation expansion | 0.1672 | 0.0237 | 0.3629 | **0.4461** |
| `basis_shrinkage_1.00` (HARMLESS) | selection creation compensation | 0.1388 | 0.0178 | 0.3811 | **0.4623** |
| `basis_shrinkage_1.00` (HARMLESS) | source rotated feedback | 0.1145 | 0.0240 | 0.4302 | **0.4313** |
| `basis_shrinkage_0.20` (ACTIVELY GOOD) | endogenous creation expansion | 0.1385 | 0.0185 | 0.4486 | **0.3945** |
| `basis_shrinkage_0.20` (ACTIVELY GOOD) | selection creation compensation | 0.1468 | 0.0099 | 0.4350 | **0.4083** |
| `basis_shrinkage_0.20` (ACTIVELY GOOD) | source rotated feedback | 0.1123 | 0.0187 | 0.5109 | **0.3581** |

Under reverse order, **at deployed and at `basis_shrinkage_0.20`, S3 (not
S4) is the larger of the two in every world** — reproducing the exact
ordering-sensitivity M4-E2 disclosed for `deployed` (its own registered
report already showed S3 dominant under reverse order there). At
`basis_shrinkage_1.00` specifically, S4 is still the larger of the two in
all 3 worlds, but the margin in `source_rotated_feedback` is a genuine
knife-edge: S4 = 0.4313 vs. S3 = 0.4302, a gap of **0.0012** (Section 6).

**Full CSV**: `results/m4_h5_residual_carrier/share_table.csv` (72 rows: 3
arms × 3 worlds × 2 orderings × 4 subspaces).
`results/m4_h5_residual_carrier/knife_edge_rows.csv` (18 rows: top-1-vs-
top-2 gap for every arm/world/ordering) — only **2 of 18** combinations
have a top-1-vs-top-2 gap under 0.02: the `basis_shrinkage_1.00` /
`source_rotated_feedback` / reverse-order knife-edge above (gap 0.0012),
and `deployed` / `selection_creation_compensation` / registered-order
(S4=0.4015 vs. S3=0.3830, gap 0.0185 — already known from M4-E2's own
disclosure that deployed's own picture is close in places). Of the
remaining 16, the smallest gap is 0.0267 and 14 of the 16 are ≥0.08 — the
0.0012 knife-edge is the closest of all 18 comparisons by more than an
order of magnitude.

## 5. G2 delta evidence — the decomposition demonstrably differs (not assumed)

Absolute registered-order share deltas vs. `deployed`, per world (the
quantity these leans actually adjudicate on):

| arm | world | ΔS1 | ΔS2 | ΔS3 | **ΔS4** |
|---|---|---|---|---|---|
| `basis_shrinkage_1.00` | endogenous creation expansion | −0.0025 | +0.0045 | −0.0890 | **+0.0871** |
| `basis_shrinkage_1.00` | selection creation compensation | −0.0515 | −0.0014 | −0.0703 | **+0.1232** |
| `basis_shrinkage_1.00` | source rotated feedback | −0.0409 | +0.0136 | −0.0328 | **+0.0601** |
| `basis_shrinkage_0.20` | endogenous creation expansion | −0.0125 | +0.0034 | −0.0286 | **+0.0376** |
| `basis_shrinkage_0.20` | selection creation compensation | −0.0077 | +0.0016 | −0.0846 | **+0.0906** |
| `basis_shrinkage_0.20` | source rotated feedback | −0.0403 | +0.0091 | +0.0259 | **+0.0052** |

S4's own share rises in **all 6** (arm, world) cells — by 0.5 to 12.3
percentage points — even in `source_rotated_feedback` at
`basis_shrinkage_0.20`, where S3 itself does *not* fall (the world H3 found
totally non-responsive at every rung up to 0.50; S4 still gains 0.5 points
there, the smallest movement in the table but not a null). **S1 also falls
in all 6 of 6 cells** (by 0.3 to 5.2 points); S2 moves in both directions
(5 of 6 cells rise, 1 falls) and stays small throughout (never exceeding
0.040 in absolute share at either repaired arm, any world). The
qualitative picture is consistent across both repaired arms: whatever mass
S3 sheds does not stay lost — it is picked up disproportionately by S4, not
spread evenly across S1/S2/S3's complement.

## 6. Leans — adjudicated exactly as registered

### Lean (a) A NEW DOMINANT CARRIER EXISTS (at the HARMLESS winner) — **HOLDS**

Registered order (ADOPTED): **S4_residual is the only subspace clearing
0.40**, and it clears in **3 of 3 worlds** (0.5140, 0.5247, 0.5066) — not
merely the registered 2-of-3 bar. S1 (0.149–0.226), S2 (0.014–0.040) and S3
(0.243–0.313) never approach 0.40 in any world at this arm.

Reverse order (disclosed companion): **agrees exactly** — S4 is again the
sole qualifier, 3/3 worlds (0.4461, 0.4623, 0.4313), while S3 clears 0.40
in only 1 of 3 worlds there (`source_rotated_feedback`, 0.4302 — the same
world as the knife-edge in Section 4). **The pivot does not fire under
either ordering** (`pivot.would_fire_under_reverse_order_companion = False`,
`orderings_agree_on_pivot_decision = True`).

### Lean (b) IT IS S4 — **HOLDS**

The subspace lean (a) identifies is `S4_residual` under both orderings —
unambiguous, since it is the sole qualifier both ways. This is the SAME
block M4-E2 originally found the largest single piece at `deployed`
(0.4015–0.4464); the repair does not dethrone it — it entrenches it.

### Lean (c) STRENGTH-INVARIANT — **HOLDS under the ADOPTED registered
order; MISSES under the disclosed reverse-order companion — genuinely
order-sensitive, disclosed rather than smoothed over**

Re-running the identical ≥0.40-in-≥2/3-worlds test at the ACTIVELY-GOOD
winner (`basis_shrinkage_0.20`):

- **Registered order:** S4 is again the sole qualifier (0.4646, 0.4921,
  0.4517 — 3/3 worlds), and it is both a qualifying carrier AND the primary
  carrier there. Lean (c) HOLDS under both the membership reading (is the
  harmless winner's carrier ALSO qualifying at the actively-good winner —
  yes) and the stricter primary-carrier reading (is it also the single
  largest there — yes).
- **Reverse order:** **S3, not S4**, is the sole qualifier at
  `basis_shrinkage_0.20` (S3 = 0.4486, 0.4350, 0.5109 — 3/3 worlds; S4 =
  0.3945, 0.4083, 0.3581 — only 1/3 worlds, `selection_creation_
  compensation` at 0.4083). Under reverse order, the carrier identified at
  the harmless winner (S4) does **not** qualify at the actively-good winner
  — lean (c) MISSES.

**This is a real, quantified order-sensitivity, not a rounding artifact.**
It traces directly to Section 4's reverse-order table: at `deployed` and at
`basis_shrinkage_0.20`, S3 is already the larger of {S3, S4} under reverse
order in every world (by margins of 0.027–0.192) — reproducing M4-E2's own
disclosed reverse-order picture, where S3 (not S4) dominates at deployed.
The repair at ratio 0.20 is comparatively mild (34.66% displacement
reduction, vs. 45.79% at ratio 1.0) and does not push S4 far enough past S3
under reverse order to flip which one clears the bar in enough worlds — at
`basis_shrinkage_1.00`, the stronger repair, it does (barely, in
`source_rotated_feedback`: the 0.0012 knife-edge). Per the outer task's
instruction, **the ADOPTED reading is registered order** (the primary
convention this entire line has used since M4-E2), and lean (c) is recorded
as **HELD** on that adopted reading — but the reverse-order disagreement is
reported with full prominence, not folded into a single unqualified "HOLDS."

## 7. Verdict

**PIVOT DOES NOT FIRE** — under the harmless winner, S4 clears the
registered 0.40 bar in 3 of 3 worlds (not just the required 2 of 3), under
both orderings, and this is not a knife-edge finding at that arm (smallest
margin over the bar: 0.5066 − 0.40 = 0.1066, about **89×** the 0.0012
knife-edge gap that DOES appear elsewhere in this same table, Section 4).

- **(a) A NEW DOMINANT CARRIER EXISTS — HOLDS**, decisively, both orderings.
- **(b) IT IS S4 — HOLDS**, decisively, both orderings.
- **(c) STRENGTH-INVARIANT — HOLDS under the adopted registered order;
  MISSES under the disclosed reverse-order companion.** The disagreement is
  real and traced to its source (Section 6), not glossed over.

**Verdict:
`NEW_DOMINANT_CARRIER_FOUND__IS_S4__STRENGTH_INVARIANT__ORDER_SENSITIVE_AT_ACTIVELY_GOOD_ARM`.**

Read plainly: the safe lever's repair does not create a *new* dominant
carrier out of nothing — it takes the carrier M4-E2 already found largest
at `deployed` (S4, the residual block) and makes it *more* dominant, in
every world, at both repaired arms, under the line's own adopted ordering
convention. Whether that dominance is a property of the repair *strength*
specifically (only shows up once the repair is aggressive enough to also
be net-neutral rather than actively-good, per H4's own G0 finding that the
harmless winner's recovery is a well-powered null while the actively-good
winner's is significantly improved) is exactly what the reverse-order
disagreement at the milder arm suggests, and is disclosed as an open
question rather than adjudicated away.

## 8. Mechanical notes

**One mechanical issue, found and fixed before any hypothesis-relevant
number was read.** During review of this leg's first `--assemble` output,
a disclosure string inside `gates.G0_power.rule3_vacuous_check` cited H4's
and H3's own G2 BASIS LIVENESS ratios directly (`ratio_to_deployed_median_
disp_v2`, e.g. 0.70 for `basis_shrinkage_1.00`) but labeled them "Nx its
own 10% bar" without first dividing by the bar — producing a misleading
"0.70x the bar" string that reads as *below* the bar (i.e. NOT live) when
the arm is in fact live at 7.01× the bar (H4's own report states this
figure directly). **This was a labeling bug in one disclosure sentence
only** — it did not touch G1, G2, G3, any share value, any lean, the pivot,
or the verdict, all of which are computed independently of this string.
Found and fixed (divide by `materiality_ratio` before formatting) after
`--assemble` had already run once and all lean/pivot/verdict numbers
already existed; `--assemble` was re-run (a pure re-derivation from already-
persisted per-world/per-arm partials, no world/arm recompute) and produced
an **identical** verdict, identical lean holds, identical G1/G2/G3 pass
booleans — confirming the fix changed only the one prose string.

**No other mechanical problems.** The smoke test (single-rep context, all 3
arms, deployed-vs-`context['v2_basis']` exact match, uniform width=13
across arms, and a full 3-arm g3-style spot check at 0.0 abs diff) passed
on the first attempt. All 3 worlds' g3 stages, all 9 (world, arm) compute
stages, and the assemble stage completed clean on the first attempt,
entirely foreground with explicit per-call timeouts (no background jobs, no
monitors). Wall-clock was substantially lighter than H2/H3/H4 because this
leg's disclosed scope reduction (Section 1) skips the oracle-stage
`TRUTH_BUDGETS` loop entirely: context build 35–40s/world (8 reps), each
arm stage 1.1–3.2s (vs. H2/H3/H4's own 21–28s/arm, which paid for two
truth-recovery budgets this leg does not compute), total wall-clock across
all 3 worlds + assemble under 3 minutes. Data-integrity check before any
hypothesis-relevant number was read: `disp_rows` 72 rows (3 worlds × 3 arms
× 8 reps, exact), `g3check_rows` 9 rows (3 × 3, exact), `offset_shares_by_
arm` 9 rows (3 × 3, exact), `share_table` 72 rows (3 × 3 × 2 × 4, exact),
`knife_edge_rows` 18 rows (3 × 3 × 2, exact) — all as expected, all checked
before adjudication.

## 9. Hand-off

The safe lever's harmless repair does not merely fail to remove the
displacement's largest single piece — it **entrenches** it: S4's share
rises in all 6 (arm, world) cells tested (Section 5), and remains the sole
subspace clearing 0.40 at both repaired arms under the adopted ordering
(Section 6). Per the registration's own framing, since the pivot does not
fire, this is reported as the finding it is, not softened: **there is a new
attackable target after all — S4, the residual block — but it is now the
majority of the surviving displacement (51–52% of it, at the harmless
winner) rather than a plurality (40–45% of the pre-repair total), and
"attacking S4" is a fundamentally different kind of problem than attacking
S3 was.** S3 had a concrete, code-legible operational construction (three
named families of normalization/scale modes, Leg 10/M4-E2's own
inventory). S4 is *defined* as whatever the S1+S2+S3 projection does not
explain — it has no operational construction of its own to intervene on
without first giving it one. The order-sensitivity at the actively-good
arm (Section 6, lean c) narrows where that next question should start:
under the milder, actively-good repair, S3 is still reverse-order dominant
at `deployed`-like margins, and only the stronger, harmless-only repair
pushes S4 durably ahead of S3 under both orderings — suggesting S4's
apparent takeover may itself be a **strength effect of pushing past the
actively-good ceiling**, not an intrinsic property of removing S3-type mass
per se. This is a new, narrower, unregistered question this leg's own
design surfaces (via the two-ordering, two-arm comparison it was asked to
keep live) but does not resolve — proposing or running a construction for
S4 is future work, not performed here.
