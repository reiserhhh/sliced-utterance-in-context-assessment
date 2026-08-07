# SUICA M4-G1 — Whitening Intervention: Is the Scale Family an Actionable Lever, or Only a Carrier?

Tier: **EXPLORATORY** (open-exploration phase, operator directive 2026-08-01).
Registered before run: `docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md`, "M4-G1
registration" (2026-08-03, BEFORE run); ledger row M4-G1. Script:
`scripts/run_suica_m4_g1_whitening_intervention.py`. Artifacts:
`results/m4_g1_whitening_intervention/`. Machinery imported from Leg 4
(context build, forced-route refit, analytic D_true, generator regeneration),
Leg 3 (world seed, relative error), Leg 9 (row-norm swap), Leg 10 (freeze
ingredients, Tikhonov whitening rebuild), Leg 11 (stacked-frame quotient
machinery), Leg 14 (GPA Frechet mean, quotient distance) — the SAME
functions M4-E2 used. No estimator internals are copied.

## Headline, stated up front

**PIVOT DOES NOT FIRE. LEAN (a) HOLDS. LEAN (b) MISSES DECISIVELY. LEAN (c)
MISSES. Verdict: `COSMETIC_LEVER_OFFSET_WITHOUT_TRANSFER`.** Every one of the
seven non-baseline arms moves the discovery objective's frame displacement
(offset) substantially and in the SAME direction — down — with a clean,
monotone dose-response from mild shrinkage through aggressive truncation to
the identity control. At least one adequately-powered arm
(`truncated_90`, 52.8% reduction, paired 95% CI [5.28, 8.46] on the raw
offset difference, half-width inside the G0 power bar) clears the registered
25% actionable bar, so **lean (a) HOLDS on solid ground, not merely on
underpowered noise**. But at the arm the registration's OWN rule selects for
lean (b) — `truncated_50`, the candidate arm with the single lowest mean
offset — truth-referenced recovery does not improve, it **collapses**: the
analytic-derivative relative error rises from a baseline ~0.567 to ~0.928
(budget=4x) / ~0.928 (budget=8x), a paired 95% CI entirely on the "worse"
side at both truth variants (n=384 author-reps each). **Lean (b) MISSES
decisively, under BOTH variants, exactly as the registration requires before
declaring a miss.** Lean (c) also MISSES — the `identity` arm (zero
amplification) has the LOWEST offset of every arm tested, not merely a
higher one than the best regularized arm, an outright inversion of the
"not simply whitening bad" expectation. Per the registration's own
second recorded outcome: **the scale family is a COSMETIC lever** — it can
shrink the discovery objective's self-consistency metric essentially at
will, but shrinking it does not recover truth, and past a modest point makes
recovery dramatically worse. A disclosed, non-gating companion reading
(below) sharpens this into a dose-response: only the MILDEST shrinkage
settings (which do not clear the 25% actionable bar) show small,
statistically real IMPROVEMENTS in recovery; everything that clears the bar
makes recovery worse, and the worst-offset-scoring interventions
(truncation, identity) are catastrophic for recovery. Full numbers below.

## Part 0 — registered operationalizations (written into the script BEFORE compute; transcribed here)

### 0.1 Arms (registered; none added or dropped)

Reusing Leg 10's freeze-ingredients rebuild of the reference-calibration
covariance eigendecomposition (bit-near-exactly validated against the frozen
V2 transform by Leg 10 itself), which retains 12 of 16 raw candidate features
on every one of the 24 (world, rep) contexts probed (one context showed 11):

- `baseline` — deployed `1/sqrt(eig)` (lambda=0 in Leg 10's own rebuild).
- `shrinkage_{0.01,0.1,1.0}` — `1/sqrt(eig+lambda)`, `lambda = ratio *
  median(eig)`, same retained eigenvector set/width as baseline (13).
- `truncated_{90,75,50}` — drop the smallest-eigenvalue retained directions,
  keeping the top-k directions whose cumulative eigenvalue sum covers >= the
  target fraction of the RETAINED spectral mass, `1/sqrt(eig)` unchanged on
  survivors. Width shrinks by construction.
- `identity` — the retained eigenvectors with scale = 1 (no division at
  all); width unchanged (13).

### 0.2 Two disclosed ambiguities, resolved BEFORE compute

**"lambda / median(eig)".** Two readings of which "eig" the median is taken
over: Reading A (ADOPTED) — median over the 12 RETAINED eigenvalues (the
same array the formula `eig + lambda` already indexes; same-symbol
consistency within one sentence, and the scientifically apt choice since it
scales lambda to the OPERATIVE spectrum, not one that includes never-inverted
directions). Reading B (disclosed, not adopted) — median over all 16 raw
candidate features' eigenvalues (before the rank-tolerance cut). On every
probed context the two differ by 5-10x (e.g. `endogenous_creation_expansion`
rep 0: retained-median 1.215e-3 vs all-16-median 1.62e-4) — not a cosmetic
choice. Reading A is used for every registered lambda in this run; Reading
B's values are persisted alongside in `g2_spectrum_evidence.csv`'s source
computation (script constant `lambda_reading_b_not_adopted`, not surfaced in
the adjudicated tables).

**"identity ... no whitening at all".** Reading A (ADOPTED) — scale = 1 in
the SAME retained eigenbasis: a pure rotation/embedding (the eigenvectors are
already orthonormal), width and rotation identical to baseline, ONLY the
per-direction scale law varies across all eight arms. This gives lean (c) a
clean, apples-to-apples reading (only the scale law differs across every
arm) and matches the registration's own "the ONLY thing that varies is the
whitening applied." Reading B (disclosed, not adopted) — skip the PCA
transform entirely, use raw centered features (width 16, not 13). Rejected
because it confounds TWO changes at once (rotation AND scale), muddying lean
(c)'s "not simply whitening bad" reading, and because it is a materially
different, higher-transcription-risk implementation for a leg whose
registered scope is the SCALE family specifically (M4-G plan doc, "Why this
line exists": "intervene on the whitening SCALE family").

### 0.3 Truth-referenced recovery operationalization (the leg's registered researcher degree of freedom)

This leg's six deliverables exclude the generator/estimator files, so a
hand-derived "soft-label" reconstruction of the generator's own stochastic
target (the most literal transplant of M4-F5's "noise-free input" move) was
**considered and rejected**: it would require independently re-deriving the
generator's private per-category hazard-probability formula outside the
files this leg may touch, a materially higher bit-exactness risk than reusing
an already-validated call. Leg 4's OWN Part 4b ("D-leg resolution scaling")
already exposes the needed reusable primitive: regenerate the world's
dynamic event panels at a different `spec.events` budget via
`generate_m4_chart_ecology_world` UNCHANGED (frozen-world law: identical
`oracle_basis`/`author_parameters` asserted bit-exact across budgets), refit
via the IDENTICAL `_forced_route_derivative` path, compare to the analytic
`D_true`. `_budget_rows_for_world_rep` hardcodes `context["v2_basis"]`, so
(mirroring M4-F5's own precedent of writing a "disclosed structural
near-duplicate" when the original does not expose what a leg needs) this
leg's `_truth_rows_for_context` is a near-duplicate parameterized over an
ARBITRARY arm basis, calling the SAME three primitives Leg 4 Part 4b calls,
in the same order, with the same frozen-world assertions.

**Two registered variants:** budget = 4.0x events (480; the SAME ceiling Leg
4 Part 4b itself validated as "possible" without a fallback grid — an
already-proven multiplier, not a new invention) and budget = 8.0x events
(960; a further doubling, the genuine second, independent finite-sample
point this leg needs, mirroring M4-F5's own sensitivity-check convention of
probing a multiple of the primary). **Budget = 1.0x (i.e. `e_arm_true`
itself) is deliberately NOT one of the two adjudicated variants**: it is
mechanically a fixed affine function of "gap" (`gap_arm = e_arm_true -
e_orc_true`, `e_orc_true` arm-invariant), so a within-author-view, across-arm
paired comparison on it is statistically IDENTICAL to gap's own comparison —
it could never diverge from gap, defeating the entire point of a separate
truth-referenced metric (the motivating precedent: Leg 12 and M4-F5 both
found self-consistency and truth-recovery moving in opposite directions).
Budget = 1.0x is used ONLY for gate G3.

### 0.4 Statistical operationalizations, disclosed

- **G0 / lean (a) paired-by-world CI**: n=3 (one value per world), t-interval
  at df=2, on the raw offset difference (baseline − arm).
- **Lean (b) paired CI**: author-level (view-mean) rows, n up to 384 per
  world-budget-arm combination (3 worlds × 8 reps × 16 authors, minus
  degenerate reference rows), t-interval on (baseline error − arm error).
- **"The setting that minimizes the offset" (lean b/c)**: the single
  candidate arm (`shrinkage_0.01/0.1/1.0`, `truncated_90/75/50` — NOT
  `identity`, which is a control, not a candidate) with the lowest MEAN
  offset across the 3 worlds. This is a point-estimate ranking, applied as
  registered, regardless of whether that specific arm's OWN offset
  comparison to baseline is individually well-powered (G0 is reported
  per-arm, separately, below).
- **Lean (c) aggregation**: "worse ... on the offset metric" is read as
  "worse in every one of the 3 worlds" (this line's established convention
  for unsoftened "every"/"any" rules, e.g. M4-F4's monotone-decline check,
  M4-F5's zero-tolerance co-movement clause); the mean-offset reading is
  reported alongside as a companion (both agree here).

---

*(Everything below this line was computed after the run; Part 0 above was
frozen before compute began.)*

## Part 1 — Outcome

### G0 POWER (reported first, per instruction)

Baseline offset levels, read from M4-E2's persisted `decision.json`
(`offset_table`) and reproduced bit-exactly by this leg's own `baseline` arm
(G1, below): `endogenous_creation_expansion` 13.754107,
`selection_creation_compensation` 11.956016, `source_rotated_feedback`
13.288138; mean 12.999420. Bar = 12.5% of the mean = **1.624928** (absolute
units, half-width). Realized paired-by-world (n=3, df=2, t=4.303) CI
half-widths on the raw offset difference (baseline − arm), per candidate arm:

| arm | half-width | % of bar | status |
|---|---|---|---|
| shrinkage_0.01 | 0.565 | 34.8% | **POWERED** |
| shrinkage_0.1 | 1.245 | 76.6% | **POWERED** |
| shrinkage_1.0 | 2.061 | 126.8% | UNDERPOWERED |
| truncated_90 | 1.594 | 98.1% | **POWERED** (narrowly) |
| truncated_75 | 1.691 | 104.1% | UNDERPOWERED |
| truncated_50 | 2.337 | 143.8% | UNDERPOWERED |

**3 of 6 candidate comparisons are UNDERPOWERED at n=3 worlds** (the design's
only source of world-level replication); this is disclosed exactly as the
gate requires, not softened. Critically, this is NOT a uniform failure: the
three POWERED arms include `truncated_90`, which is also the mildest arm
that (per the per-arm lean-(a) table below) crosses the 25% bar — so lean
(a)'s HOLD does not rest on underpowered ground. But `truncated_50`, the arm
lean (b)/(c) are evaluated at (registration's own "minimizes the offset"
rule), sits in the UNDERPOWERED zone for its OWN offset-vs-baseline
comparison — a fact carried forward explicitly wherever that arm's offset
number is used below. Equivalence form: this is a CI-half-width-vs-margin
bound, not a nil-significance test — compliant with G4 (Part 1, G4 section).

### G2 CHANNEL LIVENESS (reported second, per instruction)

Baseline's per-direction scale factor `1/sqrt(eig)` has mean condition
number **429.65** across the 24 (world, rep) contexts (range 56.4–833.6 —
consistent with Leg 10's own report of "amplifies the weakest retained
direction ~300x"). Pre-declared materiality margin: >= 10% relative change
in condition number, OR any change in retained width. Every arm clears this
by a wide margin:

| arm | width (vs 13) | condition number | relative change | material? |
|---|---|---|---|---|
| shrinkage_0.01 | 13 (unchanged) | 243.41 | 43.3% | **YES** |
| shrinkage_0.1 | 13 (unchanged) | 95.53 | 77.8% | **YES** |
| shrinkage_1.0 | 13 (unchanged) | 31.28 | 92.7% | **YES** |
| truncated_90 | 4 (changed) | 2.11 | 99.5% | **YES** (width + condition) |
| truncated_75 | 3 (changed) | 1.39 | 99.7% | **YES** (width + condition) |
| truncated_50 | 2 (changed) | 1.16 | 99.7% | **YES** (width + condition) |
| identity | 13 (unchanged) | **1.00 exactly** | 99.8% | **YES** |

**All 7 non-baseline arms are material** — the smallest change
(`shrinkage_0.01`, 43.3%) is still >4x the 10% bar. No arm is INERT; no arm's
result is VACUOUS. Equivalence form: magnitude-of-change vs a pre-declared
margin, not a nil-significance test — compliant with G4.

### G1 ANCHOR

`baseline` arm reproduces M4-E2/Leg 14's persisted objects to the registered
<=1e-12 bar, comfortably: basis vs `context["v2_basis"]` **0.0** (exact,
every role, every of 24 reps); GPA offset vs M4-E2's persisted `offset_norm`
**0.0** (exact, all 3 worlds — 13.754107 / 11.956016 / 13.288138 reproduced
to the displayed digit and beyond); `e_arm_true`/gap vs Leg 14's persisted
`gap_rows.csv` (`e_v2_true`) **2.22e-16** max (float roundoff). Companion:
this leg's own independently recomputed `e_orc_true` vs Leg 14's persisted
value, **9.71e-17** max. **PASS**, all four orders of magnitude inside the
bar.

### G3 TRUTH-PATH INVARIANCE

The truth-recovery code path (`_truth_rows_for_context`), evaluated at
budget=1.0 (its own frozen-world short-circuit, reusing
`context["observed"]` with zero regeneration — mirroring Leg 4 Part 4b's own
`if budget == 1.0`), reproduces the gap stage's own `e_arm_true` exactly for
a spot-check subset (2 arms `{baseline, identity}` × 3 worlds, rep 0 /
train / author 0 — chosen to cover both an unchanged-width and a
changed-scale-only arm): **max abs diff = 0.0** across all 6 checks. Not a
significance test — a degenerate exact-equality check, as registered.
**PASS.**

### G4 MATERIALITY FORM — explicit compliance

- **G0** is a CI-half-width-vs-a-generator-derived-margin (12.5% of the
  M4-E2 baseline offset) bound. Not a significance test on the offset
  difference itself.
- **G2** is a magnitude-of-change-vs-a-pre-declared-margin (10% relative, or
  any width change) bound. Not a significance test on whether the whitening
  operator changed AT ALL (which is guaranteed nonzero by construction for
  every arm but `baseline` — testing THAT would have been exactly the
  nil-test-on-a-known-nonzero-quantity M4-F8 was voided for).
- **G3** is a degenerate EXACT-equality check (0.0 achieved), not a
  significance test.
- **Leans (a) and (b)** are themselves registered in equivalence/materiality
  form (a numeric bar — 25% offset reduction; a directional CI excluding
  zero on a quantity whose direction, not mere nonzero-ness, is the claim),
  not nil-hypothesis tests. **Compliant.**

## Per-arm table: offset/gap and both truth-recovery variants

Offset = mean across 3 worlds (GPA consensus quotient distance to the
oracle-anchor swap consensus, this leg's own recomputation, world-level).
Gap/`e_arm_true` (1x) and both truth-recovery variants are AUTHOR-LEVEL
(view-mean) MEDIANS pooled over all 3 worlds x 8 reps x 16 authors (Leg
14/M4-E2's own aggregation convention).

| arm | offset (mean, 3 worlds) | gap (1x, median) | `e_arm_true` (1x, median) | truth recovery error @4x (median) | truth recovery error @8x (median) |
|---|---|---|---|---|---|
| baseline | 12.999 | 0.2152 | 0.5695 | 0.5562 | 0.5581 |
| shrinkage_0.01 | 11.571 | 0.2095 | 0.5644 | 0.5512 | 0.5509 |
| shrinkage_0.1 | 9.755 | 0.2049 | 0.5595 | 0.5539 | 0.5552 |
| shrinkage_1.0 | 7.503 | 0.2212 | 0.5842 | 0.5751 | 0.5760 |
| truncated_90 | 6.129 | 0.5328 | 0.8791 | 0.8801 | 0.8804 |
| truncated_75 | 5.572 | 0.5527 | 0.9053 | 0.9085 | 0.9052 |
| truncated_50 | 5.190 | 0.6221 | 0.9523 | 0.9574 | 0.9558 |
| identity | 4.352 | 0.5105 | 0.8666 | 0.8656 | 0.8658 |

(`e_arm_true`/truth-recovery-error columns are relative errors — LOWER is
better recovery. "Recovery" = 1 minus these values if a similarity reading
is preferred; reported as error throughout to match this program's
established `e_..._true` convention.)

## Lean adjudication

### Lean (a) — ACTIONABLE: >= 25% offset reduction, paired CI excluding zero, at least one candidate arm

| arm | mean reduction | per-world reduction | paired diff CI (baseline−arm) | G0 status | held |
|---|---|---|---|---|---|
| shrinkage_0.01 | 10.9% | 11.7% / 9.8% / 11.4% | [0.863, 1.994] | powered | NO (below 25%) |
| shrinkage_0.1 | **24.9%** | 25.6% / 22.3% / 26.6% | [1.999, 4.489] | powered | NO — **knife-edge, 0.14 points under the bar** |
| shrinkage_1.0 | 42.1% | 42.5% / 38.1% / 45.9% | [3.436, 7.558] | underpowered | YES (on underpowered ground) |
| truncated_90 | **52.8%** | 52.1% / 51.3% / 55.0% | **[5.276, 8.464]** | **powered** | **YES — adequately powered** |
| truncated_75 | 57.1% | 58.4% / 55.9% / 56.9% | [5.736, 9.119] | underpowered | YES (on underpowered ground) |
| truncated_50 | 59.9% | 63.3% / 57.1% / 59.4% | [5.473, 10.146] | underpowered | YES (on underpowered ground) |

**HELD.** Four arms nominally clear the bar, and one of them —
`truncated_90` — does so on ADEQUATELY-POWERED ground (half-width 98.1% of
the G0 bar, CI [5.28, 8.46] comfortably excluding zero). Lean (a) is
therefore adjudicated HELD on solid evidence, independent of the three
underpowered arms' own individually-noisier significance claims.

### Lean (b) — IT TRANSFERS: at `truncated_50` (the offset-minimizing candidate arm), truth recovery improves under BOTH variants

| budget | n (author-reps) | mean error, baseline | mean error, `truncated_50` | paired diff CI (baseline−arm) | improves? |
|---|---|---|---|---|---|
| 4.0x | 384 | 0.5667 | 0.9282 | **[−0.380, −0.343]** | **NO** |
| 8.0x | 384 | 0.5634 | 0.9285 | **[−0.384, −0.347]** | **NO** |

**MISS, decisively, under BOTH variants** — not a marginal miss. The
95% CI on (baseline error − arm error) is entirely negative at both budgets,
meaning `truncated_50` INCREASES relative error by roughly 34–38 percentage
points versus baseline, with tight, stable CIs (half-width ~0.0185–0.0186)
that are essentially identical at 4x and 8x — this is not a
finite-sample-size artifact of either truth variant.

### Lean (c) — NOT SIMPLY "WHITENING BAD": `identity` worse than the best regularized arm on offset, every world

| world | `identity` offset | best regularized (`truncated_50`) offset | identity worse? |
|---|---|---|---|
| endogenous_creation_expansion | 4.4216 | 5.0507 | **NO** |
| selection_creation_compensation | 4.2865 | 5.1279 | **NO** |
| source_rotated_feedback | 4.3488 | 5.3919 | **NO** |

**MISS, in 3/3 worlds** (mean reading agrees: 4.352 vs 5.190). `identity`
has the LOWEST offset of every arm tested in this leg, including every
candidate regularized arm — an outright inversion of "not simply whitening
bad," not merely a failure to confirm it.

### Pivot

Registered rule: fires iff no arm reduces the offset by >= 25% with a
paired CI excluding zero. Lean (a) HOLDS (via `truncated_90`, adequately
powered) — **PIVOT DOES NOT FIRE.**

### Verdict: `COSMETIC_LEVER_OFFSET_WITHOUT_TRANSFER`

Per the registration's own second recorded outcome ("if (a) HOLDS but (b)
MISSES, the finding is that the scale family is a COSMETIC lever — offset
reduction without truth transfer — which is a result about the objective
metric itself and must be reported as prominently as a success would have
been"): **the scale family IS actionable on the offset metric (lean a) but
that reduction does NOT transfer to truth (lean b misses decisively under
both variants), and the mechanism is not "any de-amplification helps" (lean
c misses — `identity`, the most extreme de-amplification, has the single
lowest offset of all eight arms).**

## Honest reading: the dose-response the registered rule does not see (disclosed companion, non-gating, does not change the adjudicated verdict)

The registration's lean (b) test is evaluated at the single arm that
strictly minimizes MEAN offset (`truncated_50`), as registered — the correct
reading, not substituted for a more favorable arm after seeing results. But
the per-arm table above shows the relationship between offset and recovery
is not uniform across the eight arms, and the full picture is
scientifically important enough to report explicitly, computed identically
for every arm (paired, author-level, both budgets), with the SAME statistic
lean (b) itself uses:

| arm | offset reduction (mean) | truth-recovery CI (baseline−arm), budget=4x | truth-recovery CI, budget=8x | reading |
|---|---|---|---|---|
| shrinkage_0.01 | 10.9% | [+0.0038, +0.0072] | [+0.0033, +0.0067] | **real, tiny improvement** |
| shrinkage_0.1 | 24.9% (just under the 25% bar) | [+0.0054, +0.0169] | [+0.0047, +0.0160] | **real, tiny improvement** |
| shrinkage_1.0 | 42.1% | [−0.0165, +0.0066] | [−0.0180, +0.0050] | **ambiguous** (CI includes zero) |
| truncated_90 | 52.8% | [−0.307, −0.264] | [−0.311, −0.267] | **large, decisive worsening** |
| truncated_75 | 57.1% | [−0.325, −0.286] | [−0.329, −0.289] | **large, decisive worsening** |
| truncated_50 (registered) | 59.9% | [−0.380, −0.343] | [−0.384, −0.347] | **large, decisive worsening** |
| identity | (control) | [−0.291, −0.257] | [−0.294, −0.260] | **large, decisive worsening** |

Across the 7 non-baseline arms, Spearman(offset mean, truth-recovery error
@4x) = **−0.786** (descriptive only, n=7 arms, not a registered test): lower
offset associates with WORSE, not better, recovery. **The two arms that show
a real, statistically clean improvement in truth recovery
(`shrinkage_0.01`, `shrinkage_0.1`) are precisely the two that do NOT clear
the registered 25% "actionable" offset-reduction bar** (`shrinkage_0.1`
misses it by 0.14 percentage points — 24.86% vs 25.00%). Every arm that
clears the bar makes recovery worse, and the two arms with the single
lowest offsets in the whole study (`truncated_50`, `identity`) are also
the two with (respectively) the worst and second-worst `e_arm_true`. This
is precisely the pattern this leg's Part 0.3 motivating precedent
(Leg 12, M4-F5) predicted could happen and precisely why the truth-recovery
metric was made mandatory rather than optional: the offset metric alone,
followed to its own minimum, actively leads AWAY from truth.

## Honest anomalies

- **`shrinkage_0.1`'s offset reduction (24.86%) misses the registered 25%
  actionable bar by 0.14 percentage points** — a knife-edge miss in the same
  spirit M4-E2 disclosed for its own sub-40% clause. The pre-coded rule
  (evaluated exactly as registered) reports it as a clean MISS; the honest
  reading is that it sits essentially AT the bar, and — per the dose-response
  table above — it is also the LARGER of the two arms showing a genuine,
  small, statistically clean truth-recovery IMPROVEMENT.
- **G0 is a mixed, not uniform, power picture.** 3 of 6 candidate arms are
  UNDERPOWERED at n=3 worlds (the design's inherent replication ceiling for
  a world-level quantity); lean (a)'s HOLD does not depend on any of them,
  resting instead on `truncated_90` alone, which is adequately powered.
  `truncated_50` — the arm lean (b)/(c) are registered to run on — is itself
  in the underpowered zone for its OWN offset-vs-baseline comparison; this
  does not weaken lean (b)'s MISS (which uses an entirely different,
  well-powered n=384 truth-recovery comparison), but it does mean the exact
  MAGNITUDE of `truncated_50`'s offset reduction (59.9%) carries more
  sampling uncertainty than the headline number alone suggests.
- **`identity` is not merely "not worse" than the best regularized arm — it
  has the single lowest offset of all eight arms tested**, including every
  shrinkage and truncation setting. Read plainly: on this leg's own offset
  metric, the objective is (monotonically, across every arm tried) happiest
  when the whitening amplifies least and/or retains fewest directions, all
  the way to zero amplification. That the SAME ordering is close to the
  worst possible ordering for truth recovery (identity: `e_arm_true`=0.867;
  the three truncated arms: 0.879–0.952; only baseline and mild shrinkage,
  at the HIGH-offset end, recover well) is the central finding of this leg.
- **Retained rank is not rigidly 12.** Leg 10's rank-tolerance cut (1e-6
  relative, cap 12) retained exactly 12 of 16 raw candidate features on 23
  of the 24 (world, rep) contexts probed and 11 on one; this small,
  genuinely-computed variability (not hardcoded) is visible in
  `g2_spectrum_evidence.csv`'s `k_retained`/`width` columns (mean width
  12.875 for baseline/shrinkage/identity).
- **The retained spectrum is extremely top-heavy on all three worlds**: the
  single largest retained eigenvalue alone captures 50.5%–62.4% of the
  retained spectral mass (per-world), so `truncated_50` (retain >=50% of
  mass) keeps only k=1 direction, `truncated_75` keeps k=2, and
  `truncated_90` keeps k=3 — on EVERY world, not by coincidence. The
  "truncated" arms are therefore severe rank collapses (width 2–4 out of
  13), not gentle trims, a direct empirical consequence of this domain's
  spectrum shape rather than a design choice.
- **GPA basin structure narrows sharply as arms de-amplify.** `baseline`
  typically converges to 7–8 distinct basins (of 8 rep-inits);
  `truncated_50` converges to as few as 2 in two of three worlds — the
  discovered frames become far more mutually consistent as the estimator's
  expressiveness is stripped away, a plausible mechanical contributor to
  why the offset metric (built from GPA consensus stability) falls so
  readily under these arms even though truth recovery does not follow.

## Faithfulness chain (all green, refused-not-warned)

| gate | value |
|---|---|
| analytic D_true unit check (24 reps) | max 1.67e-15 |
| basis anchor vs context v2_basis (baseline arm, 24 reps x 3 roles) | 0.0 |
| offset anchor vs M4-E2 persisted (3 worlds) | 0.0 |
| gap/`e_arm_true` anchor vs Leg 14 persisted `gap_rows.csv` (baseline arm) | 2.22e-16 |
| `e_orc_true` anchor vs Leg 14 persisted rows (independent recompute) | 9.71e-17 |
| frozen-world assertion (`oracle_basis`/`author_parameters` unchanged across budgets) | exact equality, all 24 contexts x 2 budgets |
| G3 truth-path degenerate equality (budget=1.0 vs gap stage) | 0.0 (6/6 checks) |
| row-count completeness (offset/gap/truth partials) | exact match to expected counts, all worlds |
| degenerate-reference flag agreement vs Leg 14 | 100% (0 mismatches) |

## Boundaries

Finite synthetic M4-C.2 worlds only (3 registered high-gap worlds x 8
reps); truth-referenced recovery via budget-regenerated (4x/8x events)
finite panels from the SAME frozen world law Leg 4 Part 4b validated,
compared to the analytic `D_true`; the two truth-recovery variants are both
points on a single "more finite data from the same law" axis (Part 0.3
discloses why — this leg's six deliverables cannot touch the
generator/estimator files, ruling out a hand-derived noise-free-target
reconstruction), NOT the conceptually-orthogonal "same-realization-denoised
vs long-run-population" split M4-F5 used; no natural-text, personality, or
clinical claim; no seal, no independent verification (operator directive
2026-08-01). Per the registered hand-off: this leg exonerates neither the
scale family from being an offset-metric lever (it plainly is) nor
declares it a usable estimator fix (it plainly is not, past the mildest
settings, which themselves fall short of "actionable"). The open problem
for any future leg in this line is now sharply framed by the dose-response
table above: whether a NARROWER shrinkage ladder concentrated near
ratio ~0.05–0.3 (between this leg's 0.01/"real but sub-bar" and
1.0/"ambiguous") can find a setting that is BOTH actionable (>=25%) AND
truth-transferring — or whether, as the monotone Spearman pattern suggests,
those two properties are in this objective's structure fundamentally in
tension.
