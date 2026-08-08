# SUICA M4-H3 — The safe lever's ladder, with the winner defined jointly

Tier: **EXPLORATORY, label-free, synthetic.** Registered in
`docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md`, "M4-H3 registration
(2026-08-03, BEFORE run)", preceded by "M4-H2 planner adjudication note"
(same date, sixth standing rule). Ledger row `M4-H3`. Script:
`scripts/run_suica_m4_h3_safe_lever_ladder.py`. Artifacts:
`results/m4_h3_safe_lever_ladder/{decision.json, gates.json, disp_rows.csv,
g2_liveness_rows.csv, truth_recovery_rows.csv, author_level_truth_rows.csv,
g3check_rows.csv, offset_shares_by_arm.csv, g5_arm_by_metric_table.csv}`.

## 0. Where this leg picks up

M4-H2 found a real, mechanistically-certified carrier in basis construction
(`basisvar_whitening_unscaled`, dropping the whitening's `1/sqrt(eig)` term
entirely): it closed 64.71% of Leg 14's displacement gap, and S3's
registered-order share collapsed an order of magnitude (.337→.040) in 3/3
worlds, exactly the predicted subspace — but it destroyed truth-referenced
recovery (+.274/+.277, 12–14x outside the ±0.02 margin). M4-H2's own dose
response, computed but not adjudicated under its registration's target-only
winner rule, showed the mildest qualifying arm
(`basisvar_whitening_shrinkage`, λ = 0.10 × median retained eigenvalue) was
the only SAFE one: 28.9% reduction with recovery genuinely IMPROVING. The
planner's own adjudication note named this a registration defect — the
sixth of its family — and added the sixth standing rule: **the winning arm
must be the best arm passing BOTH the target metric and the anti-cosmetic
check, never the target extremum.** M4-H3 finds that safe lever's optimum
and ceiling: a registered, non-extendable ladder of shrinkage ratios
bracketing M4-H2's working value of 0.10, with every lean evaluated at the
JOINT winner (defined by the sixth standing rule) rather than the arm with
the largest raw reduction.

## 1. Part 0 — inherited from M4-H2, varied at one line

This leg performs no new Part 0 audit. M4-H2's own inventory of
`context["v2_basis"]`'s construction (its file, lines 26–197) classified
six steps as CANDIDATE CARRIER; M4-H3 holds five of them at deployed
default (source-scale, centering, rank-retention threshold, intercept
scale, source panel — all exactly as M4-H2's own `deployed` arm computes
them) and varies ONLY the sixth, item 8a: whitening scale, REGULARIZED
reading, `m4_condition_manifold_estimator.py:580-583`
(`whitening = eigenvectors[:, retained] / sqrt(eig)`, regularized form
`1/sqrt(eig + λ)`). This leg's only new code is a parameterized
near-duplicate of M4-H2's own shrinkage branch
(`run_suica_m4_h2_basis_normalization.py:530-533`), varying λ/median(retained
eig) instead of M4-H2's hardcoded 0.10.

**Registered ladder (NON-EXTENDABLE): {0.02, 0.05, 0.10, 0.20, 0.50}** —
one point 5x milder than M4-H2's working value, one 2x milder, the working
value itself, one 2x stronger, one 5x stronger.

**Arms.** `deployed` (anchor — literal call to `h2._basis_for_arm(context,
"deployed")`, not reimplemented) + five `basis_shrinkage_<ratio>` ladder
rungs (this leg's only new construction code) + `whitening_unscaled` (the
KNOWN-UNSAFE REFERENCE, anchor — literal call to
`h2._basis_for_arm(context, "basisvar_whitening_unscaled")`). Verified
empirically, not merely asserted: since none of this leg's arm names match
M4-H2's `_ingredients_for_arm`'s three special-cased strings, every ladder
rung falls through to deployed defaults for source-scale/centering/rank-
tolerance automatically — confirmed by a width-invariance check (Section 3)
showing WIDTH is identical across all 7 arms within every one of the 24
(world, repetition) cells, so this leg's reductions carry no width confound.

**Lean (b)'s registered materiality margin (Part 0, before compute).**
"S3's share falls MATERIALLY" is operationalized as a **≥10% RELATIVE fall**
from deployed's own S3 share, in ALL THREE worlds (census). This reuses
M4-H2's own `G2_CONDITION_MATERIALITY_RATIO = 0.10` convention — the same
constant, the same "does this move by at least a tenth of the reference
scale" shape of question, now applied to share movement instead of basis
distance.

**Winner definition (sixth standing rule).** The JOINT winner is the arm
with the largest REP-GRAIN displacement reduction among arms whose recovery
does NOT worsen — one-sided equivalence, margin ±0.02 (M4-H2's own
`LEAN_C_MARGIN`, reused unchanged), BOTH truth-budget variants required.
This filter is applied to every one of the six non-deployed arms, not a
pre-selected candidate.

## 2. Design as executed

Worlds: M4-H2's own three `HIGH_GAP_WORLDS`, all 8 repetitions — imported
unchanged. Three metrics computed at **every** arm (all 7, not only the
eventual winner): (1) Leg 14's `disp_v2` (PRIMARY); (2) M4-E2's S1–S4
shares; (3) truth-referenced recovery, both `TRUTH_BUDGETS = (4.0, 8.0)`.

**Metric grains, justified fresh for this leg (not inherited by citation
alone).** Metric 1: REP grain (n=24) PRIMARY — `disp_v2` is already a
per-repetition quantity under this leg's own arm construction (each
repetition gets its own basis, GPA frame, and quotient distance to
deployed), no aggregation needed to reach it; WORLD grain (n=3) companion.
Metric 2: WORLD-level census (n=3, no CI) — a world's GPA-consensus share
is a single deterministic statistic, no finer sampling unit is defined.
Metric 3: AUTHOR grain (n up to 384) PRIMARY — each (world, repetition,
view, author) is an independent forced-route refit against the analytic
`D_true`; WORLD grain (n=3) companion.

## 3. Gates

### G0 POWER (MDE stated before adjudicating, citing M4-H2's own numbers)
**Metric 1.** The registered 25% bar in absolute terms is
0.25 × 18.059 (M4-H2's own persisted deployed pooled rep-grain mean,
reproduced here to 9.7e-17 — Section G1) = **4.515**. M4-H2's own largest
rep-grain half-width across its six arms, on the identical worlds/reps/
metric, was 0.888 — 5.1x smaller than the bar. This design's REALIZED
half-widths (0.433–0.737 across the six arms here) are all comfortably
under 4.515 (6.1x–10.4x smaller); **no arm is underpowered for lean (a)**.

**Metric 3.** The winner-eligibility margin is ±0.02 (one-sided); this
line's own strict `G0_FRACTION_BAR = 0.01` (half the margin) is the
disclosure threshold. Realized author-grain half-widths: 0.0026–0.0099 for
the five ladder rungs (all under 0.01, none flagged), 0.0172/0.0171 for
`whitening_unscaled` (nominally over the strict bar — but, as M4-H2 itself
found and this leg reproduces exactly, its OUTSIDE classification sits
12–14x the margin's own width away from the boundary, decisive regardless).
**The joint winner's own recovery comparison (half-width 0.0099/0.0099) is
comfortably under the strict bar — its null (Section 6) is a genuine,
well-powered null, not underpowered.**

### G1 ANCHOR
`deployed` and `whitening_unscaled` reproduce M4-H2's own PERSISTED
row-level values to ≤1e-12 — three independent chains, FULL row-level joins
(not spot checks):

| chain | source | n checks | max abs diff |
|---|---|---|---|
| `disp_v2` per rep | `m4_h2_basis_normalization/disp_rows.csv` | 48 (24×2 arms) | see below |
| `offset_norm` + 15 share fields | `m4_h2_basis_normalization/offset_shares_by_arm.csv` | 6 (3 worlds×2 arms) | see below |
| `e_arm_true` per (rep,view,author,budget) | `m4_h2_basis_normalization/truth_recovery_rows.csv` | 3072 (1536×2 arms) | see below |

**`max_abs_diff_overall = 9.71e-17`** (floating-point noise, ~1e5x smaller
than the 1e-12 tolerance), **G1 PASSES**. This is a real test, not a
pass-through: `deployed` here is independently rebuilt via a fresh context
build in this leg's own output directory (not a copy of M4-H2's cache), and
`whitening_unscaled` is a literal call into M4-H2's own arm-dispatch
function — the anchor certifies the shared machinery end-to-end.

**Disclosed, NOT a registered gate:** `basis_shrinkage_0.10` uses the
identical formula and ratio as M4-H2's own `basisvar_whitening_shrinkage`.
Internal-consistency check: **0.0 exact** across all 24 `disp_v2` checks —
this leg's own re-derivation of M4-H2's middle rung is bit-identical.

### G2 BASIS LIVENESS
Materiality margin: 10% of deployed's median `disp_v2` (17.615, M4-H2's own
`G2_CONDITION_MATERIALITY_RATIO` convention).

| arm | median basis distance vs deployed | ratio to 10% bar | live |
|---|---|---|---|
| `basis_shrinkage_0.02` | 4.585 | 2.60x | yes |
| `basis_shrinkage_0.05` | 6.374 | 3.62x | yes |
| `basis_shrinkage_0.10` | 7.850 | 4.46x | yes |
| `basis_shrinkage_0.20` | 9.494 | 5.39x | yes |
| `basis_shrinkage_0.50` | 10.939 | 6.21x | yes |
| `whitening_unscaled` | 22.292 | 12.66x | yes |

**All six arms LIVE**, smallest 2.6x the bar — no arm's result is VACUOUS.
Monotone in ratio, as expected from the construction.

### G3 TRUTH-PATH INVARIANCE
Dual computation (`context["flat"]`-sourced vs freshly re-flattened
budget=1.0 panels), all 7 arms, one spot-check per world. **`max_abs_diff =
0.0`** across 21/21 checks, tolerance 1e-12. **PASSES.**

### G4 MATERIALITY FORM
G0: CI-half-width-vs-bar equivalence bound per metric, MDE stated citing
M4-H2's own numbers before adjudicating. G1/G3: degenerate exact-equality
(1e-12), not significance tests. G2: ratio-to-scale liveness bound (10%).
Lean (a): paired CI-excludes-zero AND ≥25%-of-mean point bar, both
required, at the joint winner only. Lean (b): relative-fall equivalence
bound (≥10%) across a 3-world census, at the joint winner only. Lean (c):
strict-direction classification (CI entirely negative, both budgets) at the
joint winner only — stronger than the winner-eligibility filter's own
equivalence band. Winner definition itself: one-sided WITHIN/OUTSIDE
equivalence at ±0.02, both budgets, applied to every arm. No gate is a
nil-significance test on a known-nonzero quantity.

**Disclosed robustness check on the ±0.02 margin's sidedness.** The outer
registration's "equivalence, ±.02" is ambiguous between one-sided ("worse
by more than 0.02" disqualifies; better never does) and two-sided (CI must
lie entirely inside [−0.02,+0.02]). Both readings were computed for every
arm/budget: **they agree exactly on every classification** (WITHIN for all
five ladder rungs at both budgets; OUTSIDE for `whitening_unscaled` at
both). The one-sided reading is adopted (matching M4-H2's own lean-(c)
convention for the identical "does not worsen" question, and the natural
reading of "does not worsen" itself), but the choice does not change any
number reported here.

### G2 (width) — disclosed companion: no width confound
Width is IDENTICAL across all 7 arms within every one of the 24 (world,
repetition) cells (0/24 disagreements) — this leg's shrinkage-only
intervention never touches the rank-retention step. Width does vary mildly
BETWEEN repetitions (12 in 3 of 24 cells, 13 in the rest) — a pre-existing
property of the deployed `rank_tolerance=1e-6` threshold, orthogonal to
this leg and affecting every arm identically within a given (world, rep).
No width-normalization companion is needed; every reduction reported below
is a clean basis-shape effect.

## 4. G5 — JOINT-WINNER COMPLIANCE: the full table and both picks

**Full arm × {displacement, recovery both variants, S3 share} table**
(sorted by rep-grain reduction, descending; deployed is the zero-reduction
reference and is excluded from ranking):

| arm | reduction (rep, n=24) | 95% CI | clears 25% | world-grain reduction | S3 mean (3w) | S3 falls ≥10% all 3w | recovery Δ @4x | class @4x | recovery Δ @8x | class @8x | safe (both budgets) | actively good (both budgets) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `whitening_unscaled` | **64.71%** | [10.950, 12.423] | yes | 64.54% | 0.0403 | yes | +0.2741 | OUTSIDE (worse) | +0.2774 | OUTSIDE (worse) | **NO** | no |
| `basis_shrinkage_0.50` | **41.56%** | [6.790, 8.221] | yes | 41.76% | 0.2979 | **no** | −0.0043 | WITHIN (no change) | −0.0031 | WITHIN (no change) | **YES** | **no** |
| `basis_shrinkage_0.20` | 34.66% | [5.613, 6.905] | yes | 35.27% | 0.3078 | no | −0.0102 | WITHIN (improved) | −0.0093 | WITHIN (improved) | YES | yes |
| `basis_shrinkage_0.10` | 28.93% | [4.635, 5.814] | yes | 29.62% | 0.3115 | no | −0.0111 | WITHIN (improved) | −0.0103 | WITHIN (improved) | YES | yes |
| `basis_shrinkage_0.05` | 23.17% | [3.655, 4.713] | no | 24.15% | 0.3194 | no | −0.0103 | WITHIN (improved) | −0.0095 | WITHIN (improved) | YES | yes |
| `basis_shrinkage_0.02` | 16.04% | [2.464, 3.330] | no | 17.40% | 0.3308 | no | −0.0077 | WITHIN (improved) | −0.0071 | WITHIN (improved) | YES | yes |
| `deployed` (reference) | — | — | — | — | 0.3368 | — | — | — | — | — | — | — |

(`basis_shrinkage_0.10`'s row is bit-identical to M4-H2's own
`basisvar_whitening_shrinkage`, per the disclosed check in Section 3.)

**Recovery-safety filter, every non-deployed arm:** ALL FIVE ladder rungs
qualify ("does not worsen", both budgets). Only `whitening_unscaled` fails.

**Joint winner (registered rule — largest reduction among the safe pool):
`basis_shrinkage_0.50`, 41.56% reduction.**

**Target-only winner (what the DEFECTIVE, pre-sixth-standing-rule rule
would have picked): `whitening_unscaled`, 64.71% reduction, recovery
DESTROYED (+0.274/+0.277, OUTSIDE both budgets).** This is exactly the
failure the sixth standing rule exists to prevent, reproduced here on
schedule: the target-only pick is, again, the most aggressive and least
safe arm tested.

**Disclosed ambiguity, resolved and verified not to matter.** Is
`whitening_unscaled` (named "the known-unsafe reference (anchor)" in the
registration, listed separately from "the... ladder") eligible for
joint-winner selection? Both readings computed: eligible → joint winner
`basis_shrinkage_0.50`; ladder-only → joint winner `basis_shrinkage_0.50`.
**Identical**, since the reference fails the safety filter under its own
G1-anchored reproduction of M4-H2's OUTSIDE finding either way. The
ladder-only reading is adopted (matching the registration's own naming),
but this is a disclosed robustness check, not a live fork.

## 5. Ladder-boundary disclosure

**The joint winner (`basis_shrinkage_0.50`) sits AT the top endpoint of the
registered, non-extendable ladder.** Per the outer task's explicit
instruction, this is stated plainly and not extended in this script: the
true optimum of the safe lever may lie beyond ratio 0.50. Any extension
requires its own leg — not performed here. (Reduction is monotonically
increasing in ratio across the tested range — 16.0% → 23.2% → 28.9% →
34.7% → 41.6% — with no sign of flattening yet at 0.50, so "the ceiling is
higher than this ladder reaches" is the honest reading, not "the ladder
happened to bracket the true optimum.")

## 6. Leans — adjudicated ONLY at the joint winner (`basis_shrinkage_0.50`)

### Lean (a) SAFE AND EFFECTIVE — **HOLDS**
Reduction 41.56% (rep grain, n=24), 95% CI [6.790, 8.221] — excludes zero,
clears the 25% bar by 1.66x (world-grain companion agrees: 41.76%). Not a
knife-edge: the point estimate is 66% larger than the bar itself.

### Lean (b) MECHANISTICALLY CONSISTENT — **MISSES**
S3's registered-order share at the joint winner, by world:

| world | deployed | winner (ratio=0.50) | relative fall | falls ≥10%? |
|---|---|---|---|---|
| `endogenous_creation_expansion` | 0.3323 | 0.2705 | **18.6%** | yes |
| `selection_creation_compensation` | 0.3830 | 0.3212 | **16.1%** | yes |
| `source_rotated_feedback` | 0.2953 | 0.3019 | **−2.2%** (a RISE) | **no** |

Falls materially in 2 of 3 worlds; in `source_rotated_feedback`, S3's share
does not fall AT ALL at the joint winner — it is slightly HIGHER than
deployed's. **This miss does not depend on the registered 10% floor**: even
under M4-H2's own looser "falls at all" binary criterion (no magnitude
requirement), `source_rotated_feedback` still fails, since 0.3019 > 0.2953.
**And the miss is not a property of exactly where the joint winner landed:
NO rung on the entire registered ladder achieves a material (or even any)
S3 fall in `source_rotated_feedback`** — its S3 share is 0.317/0.318/
0.316/0.321/0.302 at ratios 0.02/0.05/0.10/0.20/0.50 respectively, always
ABOVE deployed's 0.295. The mean S3 share across all 3 worlds DOES decline
monotonically with ratio (0.337 → 0.331 → 0.319 → 0.311 → 0.308 → 0.298),
so the aggregate, Part-0-predicted mechanism is directionally present — but
it is not uniform, and this leg's registered census (3 worlds, all must
agree) correctly refuses to certify it as such.

**Disclosed side observation, not adjudicated by any lean:** unlike M4-H2's
`whitening_unscaled` (where the mass leaving S3 landed disproportionately
in S1, safety-complement, .220→.532), this leg's mild ladder shows S1
roughly flat-to-slightly-LOWER (deployed .220 → .185–.200 across the
ladder) while S4 (residual) absorbs most of the modest shift (.425 →
.46–.49). The redistribution pattern at mild shrinkage is qualitatively
different from the pattern at the extreme.

### Lean (c) ACTIVELY GOOD — **MISSES**
Author-grain (n=384) paired diff, joint winner minus deployed:

| budget | mean diff | 95% CI | classification |
|---|---|---|---|
| 4x | −0.00427 | [−0.01419, 0.00566] | WITHIN (qualifies), NOT improved |
| 8x | −0.00305 | [−0.01293, 0.00683] | WITHIN (qualifies), NOT improved |

Both CIs straddle zero — the joint winner's recovery is statistically
indistinguishable from deployed's, not worse (satisfying winner
eligibility) and not distinguishably better (missing the stronger lean).
This is a genuine, well-powered null: half-widths 0.0099/0.0099 sit
comfortably under this line's own strict 0.01 power bar (G0, Section 3),
so the miss is not a power artifact. World-grain companion agrees in shape
(straddles zero, wider CI as expected at n=3): +0.0115 [−0.0199, 0.0429]
(4x), +0.0052 [−0.0467, 0.0572] (8x).

## 7. Dose-response companion (disclosed, non-adjudicating)

The registered rule picks `basis_shrinkage_0.50` because it has the largest
reduction among arms that merely do not worsen. It is NOT the arm that
best satisfies all three leans simultaneously. From the Section 4 table:
`basis_shrinkage_0.20` (34.66% reduction) independently clears the 25% bar
AND its recovery is IMPROVED (CI entirely negative) at both budgets —
i.e., had the registered rule instead been "largest reduction among
ACTIVELY GOOD arms" (a stricter, non-registered alternative), the pick
would have been `basis_shrinkage_0.20`, and leans (a) and (c) would both
have HELD. **Lean (b) would still have MISSED at `0.20`** — its own
`source_rotated_feedback` S3 share (0.3212) also sits above deployed's
(0.2953), for the same reason as at 0.50 (Section 6) — so the
mechanism-uniformity gap is a property of the whole safe range, not an
artifact of the registered rule's specific choice.

**No post-hoc rescue is performed here.** The registered winner is
`basis_shrinkage_0.50`, and Section 6's HOLD/MISS/MISS stands as the
leg's adjudicated result. This section exists only to name, explicitly,
that the sixth standing rule's "largest reduction among safe arms" is a
real improvement over the old target-only rule (it excludes the truly
harmful arm) but is not itself a "best arm overall" rule — a future leg
could register a stronger selection criterion (e.g., largest reduction
among ACTIVELY GOOD arms) if that distinction becomes decision-relevant.

## 8. Verdict

**PIVOT DOES NOT FIRE** — a jointly-qualifying arm exists at ≥25%
(`basis_shrinkage_0.50`, 41.56%). Per the registered adjudication:

- **(a) SAFE AND EFFECTIVE — HOLDS.** 41.56% reduction, CI excludes zero,
  1.66x the bar.
- **(b) MECHANISTICALLY CONSISTENT — MISSES.** S3 falls materially in 2/3
  worlds; `source_rotated_feedback` does not fall at all, at the winner OR
  anywhere on the tested ladder.
- **(c) ACTIVELY GOOD — MISSES.** Recovery is a genuine, well-powered null
  at the winner (CI straddles zero), not improved, not worsened.

**Verdict: `SAFE_BUT_MECHANISM_NOT_CONFIRMED_AT_WINNER`.** The safe lever
IS real and effective at the joint winner — a genuine, CI-backed 41.56%
reduction of Leg 14's displacement gap with recovery provably not worsening
(a well-powered null, not an underpowered non-result) — but the mechanism
Part 0 predicted (uniform S3 collapse) is only PARTIALLY confirmed there
(2 of 3 worlds), and the stronger "actively good" claim, which DOES hold
at every milder rung tested (0.02–0.20), does NOT hold at the specific arm
the registered joint-winner rule selects. This is a new shape of outcome
for this line: previous "carrier found" legs (M4-G1, M4-H2) always found
lean (b) HOLDING decisively at their winner and lean (c) MISSING
decisively; here, for the first time, it is lean (a) alone that holds
cleanly at the registered winner, with both (b) and (c) landing in a
genuine middle ground (partial-but-real mechanism; null-but-not-harmful
recovery) rather than a clean HOLD or a decisive MISS.

## 9. Mechanical notes

No mechanical problems: the smoke test, all three context+oracle stages,
all three G3 spot-checks, all 21 (world, arm) compute stages, and the
assemble stage completed with zero Tracebacks or RuntimeErrors, first
attempt, all run synchronously in the foreground with explicit long
timeouts (no background jobs, no monitors, per the process rules). Every
foreground stage's wall-clock matched M4-H2's own reported order of
magnitude: context+oracle ~187–191s/world, each arm stage ~21–28s/world
after the shared regeneration cache warmed. One data-integrity check
performed before any hypothesis-relevant number was read: `disp_rows`
(168 rows), `truth_recovery_rows` (10752 rows, 14 degenerate references —
identical count to M4-H2's own, confirming the degenerate flag is
arm-invariant as designed), and `author_level_truth_rows` (n=384 per
arm×budget, uniformly) all checked clean, zero unexpected NaNs, before
Section 3–8's numbers were computed.

## 10. Hand-off

The safe lever's ceiling within this registered ladder is 41.56% at ratio
0.50, sitting at the ladder's own upper boundary with no sign of
flattening — the true safe ceiling is not yet located and would require a
new, separately-registered ladder extending past 0.50 (this script does
not do so, per its own registration). Separately, and orthogonal to the
ladder question: this leg's own dose-response (Section 7) shows the
"actively good" property (lean c) is available within the tested range
(ratios 0.05–0.20) but is traded away by the registered "largest-reduction-
among-safe" rule in favor of more raw displacement reduction at 0.50 — a
distinction between "safe" and "actively good" that this line has not
previously had to draw, since M4-G1's and M4-H2's own safe arms were also
their most-reduced safe arms. Finally, lean (b)'s partial confirmation
(2 of 3 worlds, robust across the WHOLE ladder, not a winner-specific
artifact) means `source_rotated_feedback` behaves differently from the
other two `HIGH_GAP_WORLDS` under mild whitening-scale regularization
specifically — a world-specific mechanism question this leg's own design
does not resolve and does not claim to.
