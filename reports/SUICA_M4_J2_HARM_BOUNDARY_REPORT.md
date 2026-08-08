# SUICA M4-J2 — Is the harm boundary predictable, or is the basis-shrinkage repair undeployable in principle?

Tier: **EXPLORATORY, label-free, synthetic.** Registered in
`docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md`, "M4-J2 registration
(2026-08-03, BEFORE run)". Ledger row `M4-J2`. Script:
`scripts/run_suica_m4_j2_harm_boundary.py`. Artifacts:
`results/m4_j2_harm_boundary/{decision.json, gates.json, part0_inventory.csv,
full_inventory_separation_table.csv, disp_v2_recomputed_rows.csv,
g1_share_anchor_rows.csv, benefit_rows.csv, per-world partials}`.

## 0. Where this leg picks up, and what it tests

M4-J1 found the M4-H3/H4 basis-shrinkage repair worsens recovery decisively
in exactly two of eight `D1_WORLDS` — `history_gated_ecology` and
`topology_mismatch` — at both certified ratios (0.20, 1.00), both truth
budgets, all 8 (arm, world, budget) cells `OUTSIDE` the ±0.02 margin by
2.68×–10.3×. Neither harm world is a `HIGH_GAP_WORLDS` member, so the
original 3-world certification could not have surfaced this. M4-J1's own
executing agent declined to speculate about what the two harm worlds share.

This leg asks directly: is the harm boundary predictable from a property
measurable **before** applying the repair? If yes, the repair is salvageable
behind a gating rule. If no, one cannot know in advance whether a new corpus
is a harm case, and the repair is undeployable in principle — a measured
limit, not a shortfall.

## 1. Design as executed

**World set.** `D1_WORLDS` (8, `j1.D1_WORLDS`, reused verbatim). `HARM_WORLDS`
= `{history_gated_ecology, topology_mismatch}` (M4-J1's own named finding —
both certified ratios, both budgets, decisively OUTSIDE the margin). Every
rank-separation test and every correlation is computed over
`VALID_TRUTH_WORLDS` (6 of 8, `j1.VALID_TRUTH_WORLDS`, M4-G2's inherited
restriction) — see "Ambiguity resolution #1" below for why.

**Part 0 discriminator inventory (registered, fixed hypothesis space), at
`deployed`, all 8 worlds:**

| # | discriminator | source | new compute? |
|---|---|---|---|
| (i) | baseline recovery error | `e_arm_true`, author-grain mean, c=1.0, read directly from M4-J1's `author_level_truth_rows.csv` | no — direct file read |
| (ii) | baseline displacement | `disp_v2`, median over 8 reps, read directly from M4-J1's `disp_rows.csv` | no — direct file read |
| (iii) | S3 share | M4-E2's registered-order `S3_norm_scale_modes` share of the offset `delta`, via `h2._arm_offset_and_shares` | yes — literal reuse of h2/e2 machinery on 5 worlds H2 never touched |
| (iv) | S4 share | the same decomposition's `S4_residual` share (free from the same call) | yes (same call as iii) |
| (v) | conditioning statistic | condition number κ = max(eig_retained)/min(eig_retained) of `h2._ingredients_for_arm(context,"deployed")`'s retained eigenspectrum — the exact object H3's shrinkage repair regularizes (`lambda = ratio × median(eig_retained)`); median over 8 reps → one number per world. Companion reading of the same item: effective rank (participation ratio) = (Σeig)²/Σeig² | yes — literal reuse of `h2._ingredients_for_arm`, independently cross-checked against `leg10._freeze_ingredients` |

No new basis-construction or estimator code was written. Discriminators
(iii)–(v) are computed by literal, unchanged calls into
`h2._arm_offset_and_shares` / `h2._ingredients_for_arm` / `e2.*`; the only new
code is the glue that runs H2's own per-world recipe on the 5 worlds H2 never
covered (H2 is a 3-world leg), plus the rank-separation / bootstrap-Spearman
helpers this leg's world-level grain requires.

**Registered ambiguity resolution #1 — world scope for adjudication.** Part
0's own text says "measure... on all eight worlds," but the PIVOT text says
"...separates the two harm worlds from the **six safe ones**" — six, not
eight. `linear_null_ecology`/`fast_return_equal_marginal` were never
classified safe *or* harmful by M4-J1 (they are `EXCLUDED_TRUTH_WORLDS`,
untested for safety) — folding them into a "harm vs. safe" comparison is a
category error. **Reading A** (literal Part 0, n=8): published in full in the
inventory table below. **Reading B** (the PIVOT's own "six safe ones," n=6 =
`VALID_TRUTH_WORLDS`): **adopted for every rank test, every correlation, and
every adjudicated lean** — it is the only population where "safe" is an
actually-established status, and "recovery BENEFIT" (lean a's dependent
variable) is only a non-pathological quantity there in the first place
(deployed's own `e_arm_true` averages ~7×10⁹ in the 2 excluded worlds, the
same inherited near-zero-denominator pathology M4-J1's own lean (b)/(c)
excluded them for).

**Registered ambiguity resolution #2 — what "separates cleanly" means, and a
disclosed, not-softened finding.** Lean (b)'s own words define "separates" as
a pure RANK criterion. Applied identically to displacement for lean (c)'s
specificity check, full-precision recomputation (not the rounded 2-decimal
report table) shows displacement **also** places the two harm worlds as the
exactly-two-lowest of six — contradicting the registration's own motivating
text ("`topology_mismatch` is mid-range at 13.18"). This is reported plainly
below as a MISS on the literal rank criterion, not softened, with a
correlation-based companion check (the stronger test lean (a) itself uses) to
see whether competence's relationship to benefit is any tighter than
displacement's.

## 2. G0 and G2 (reported first, per the outer task's instruction)

### G0 POWER

n=8 `D1_WORLDS` is small; every truth-derived quantity (baseline error,
benefit) is further restricted to `VALID_TRUTH_WORLDS`, **n=6**, by inherited
precedent. Two things this design can and cannot detect, stated plainly:

- **CAN detect at full power**: an exact rank-2 separation. Once all 6
  world-level values are measured, whether the 2 harm worlds are the top/
  bottom 2 of 6 is a **deterministic fact**, not a sampling estimate — there
  is no power question for leans (b)/(c)'s own rank criterion.
- **CANNOT detect at useful power in general**: a Spearman correlation's
  sign and CI-exclusion-of-zero at n=6. A nonparametric bootstrap over 6
  points with replacement has only **C(11,6) = 462 distinct resamples** —
  disclosed explicitly rather than hidden behind a large `n_boot` (20,000
  draws were run; only 462 of the underlying value-combinations are
  distinct). CIs at this n are wide by construction. Where a CI includes
  zero, this leg reports **UNDERPOWERED for that comparison**, never a
  confident null, per the second standing rule. No prior leg in this line
  used the world itself as the unit of analysis, so no persisted effect-size
  table exists to cite an MDE against; realized CI half-widths are reported
  per comparison instead so the reader can see directly how wide they are
  (e.g. the conditioning-number correlation's CI is **[-1.0, 1.0]** — the
  entire possible range of Spearman's rho, i.e. this comparison has
  essentially zero realized power at this n).

### G2 DISCRIMINATOR LIVENESS

Registered bar: range ≥ 5% of median |value|. **All 5 discriminators live**:

| discriminator | min | max | median | range/median | live |
|---|---:|---:|---:|---:|---|
| baseline_recovery_error (budget 4) | 0.309 | 7.02×10⁹ | 0.574 | 1.22×10¹⁰ | yes |
| baseline_displacement | 7.008 | 22.731 | 18.276 | 0.860 | yes |
| S3_share | 0.287 | 0.386 | 0.335 | 0.297 | yes |
| S4_share | 0.401 | 0.509 | 0.448 | 0.239 | yes |
| conditioning_number κ | 26,043 | 419,522 | 165,307 | 2.380 | yes |

**Caveat on baseline_recovery_error's ratio**: the enormous range/median
ratio is an artifact of the 2 `EXCLUDED_TRUTH_WORLDS`' pathological ~7×10⁹
values, not a meaningful characterization of "how much this discriminator
varies among usable worlds." Restricted to `VALID_TRUTH_WORLDS` alone, the
range is 0.309–0.947 (range/median ≈ 1.09) — still comfortably live, reported
here for honesty since the headline ratio is not informative on its own.
**No discriminator is VACUOUS.**

## 3. G1, G3, G4 (the other gates)

### G1 ANCHOR — PASS

| check | n | max abs diff | tolerance | pass |
|---|---:|---:|---:|---|
| `disp_v2` (this leg's recomputation) vs M4-J1's persisted `disp_rows.csv`, **all 8 worlds** | 64 | **0.0** | 1e-12 | yes |
| S3/S4 shares + `offset_norm` vs H2's persisted `offset_shares_by_arm.csv`, 3 `HIGH_GAP_WORLDS` | 3 worlds × 3 fields | **5.55×10⁻¹⁷** | 1e-12 | yes |
| `leg10._freeze_ingredients` vs `h2._ingredients_for_arm` (independent cross-check, not a registered anchor) | 64 reps | **0.0** | — | consistent |

The `disp_v2` anchor is stronger than M4-J1's own self-anchor: M4-J1 anchored
only its 3 `HIGH_GAP_WORLDS` against upstream sources (Leg14/H3/H4/G7) and
then trusted the same machinery for 5 more; this leg's `disp_v2`
recomputation is checked against M4-J1's own file directly on **all 8**
worlds, since M4-J1's file already covers all 8. This is what licenses
`FRESH_COMPANION_WORLDS` as an extension for S3/S4/conditioning, the same way
M4-J1 licensed them for displacement/recovery/c-invariance. Baseline error,
displacement and benefit are **read, not recomputed**, from M4-J1's own
files — identity by construction.

### G3 TRUTH-PATH INVARIANCE — N/A, stated as such

This leg introduces no new truth-recovery (flat-vs-regenerated) computation.
Every truth-derived number (baseline error, benefit) is read directly from
M4-J1's own persisted files, which already passed M4-J1's own G3 (max abs
diff 0.0 over 48 checks, all 8 worlds).

### G4 MATERIALITY FORM — compliant

G1 is exact ≤1e-12 reproduction; G2 is a range/median-ratio bound; lean (a)
and the full-inventory correlations are CI-exclusion-of-zero bounds (not raw
p-values); lean (b)/(c) and the full-inventory rank checks are exact gap
bounds with the gap size reported (not nil-significance). None is a
significance test on a known-nonzero quantity.

## 4. Part 0 full inventory — all 8 worlds, Reading A

| world | harm? | baseline error (b4) | baseline error (b8) | displacement | S3 share | S4 share | κ (conditioning) | eff. rank |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| topology_mismatch | **yes** | 0.3087 | 0.3049 | 13.182 | 0.3263 | 0.5086 | 273,750 | 2.565 |
| history_gated_ecology | **yes** | 0.4588 | 0.4583 | 7.008 | 0.2868 | 0.4808 | 26,043 | 2.025 |
| selection_creation_compensation | no | 0.5527 | 0.5479 | 16.930 | 0.3830 | 0.4015 | 400,417 | 2.609 |
| source_rotated_feedback | no | 0.5660 | 0.5656 | 18.613 | 0.2953 | 0.4464 | 212,255 | 2.249 |
| endogenous_creation_expansion | no | 0.5815 | 0.5766 | 18.224 | 0.3323 | 0.4269 | 101,971 | 2.563 |
| condition_alias_ecology | no | 0.9473 | 0.9468 | 22.731 | 0.3502 | 0.4880 | 419,522 | 1.846 |
| linear_null_ecology | *excl.* | 6.80×10⁹ | 4.84×10⁹ | 18.692 | 0.3372 | 0.4487 | 118,359 | 2.502 |
| fast_return_equal_marginal | *excl.* | 7.02×10⁹ | 5.12×10⁹ | 18.328 | 0.3863 | 0.4444 | 112,251 | 2.609 |

(sorted by baseline error; `linear_null_ecology`/`fast_return_equal_marginal`
carry M4-G2's inherited truth-denominator pathology and are excluded from
every rank/correlation test below, per ambiguity resolution #1.)

## 5. Rank separation + correlation, all 5 discriminators, VALID_TRUTH_WORLDS (n=6)

Correlation is Spearman rho vs. `basis_shrinkage_1.00`'s recovery benefit at
budget 4.0 (bootstrap CI, seed 20260803, 20,000 resamples).

| discriminator | separates by rank (low) | gap (abs / ratio) | separates by rank (high) | Spearman rho | CI | excludes 0 |
|---|---|---:|---|---:|---|---|
| **baseline_recovery_error (b4)** | **yes** | 0.0939 / **1.205** | no | **0.886** | **[0.185, 1.000]** | **yes** |
| baseline_displacement | **yes** | 3.747 / **1.284** | no | 0.829 | **[0.000, 1.000]** | **no** (boundary) |
| S3_share | no | -0.031 (no threshold) | no | 0.486 | [-0.800, 1.000] | no |
| S4_share | no | -0.107 (no threshold) | no | -0.314 | [-1.000, 0.806] | no |
| conditioning_number κ | no | -171,779 (no threshold) | no | 0.257 | **[-1.000, 1.000]** | no |
| effective_rank (companion) | no | -0.719 (no threshold) | no | -0.143 | [-1.000, 1.000] | no |

**Reading this table plainly, as instructed**: baseline error separates by
BOTH tests decisively. Displacement separates by rank — with an even
slightly LARGER relative gap (1.284 vs. baseline error's 1.205) — but its
correlation CI's lower bound sits at **exactly 0.000**, a boundary case, not
a decisive exclusion; it does not pass the stricter, CI-based test the way
baseline error does. S3, S4, conditioning number and effective rank separate
by neither test, with the conditioning-number and effective-rank
correlations spanning the CI's entire possible range ([-1, 1]) — genuinely
uninformative at this n, reported as such rather than as a confident null.

## 6. Lean-by-lean adjudication

### (a) BASELINE COMPETENCE PREDICTS HARM — **HOLDS**

Spearman rho = **0.886** between deployed baseline error and
`basis_shrinkage_1.00`'s recovery benefit across `VALID_TRUTH_WORLDS`
(budget 4.0), bootstrap CI **[0.185, 1.000]**, excluding zero, direction
positive — exactly the direction the registration specifies (low baseline
error → the repair harms; high baseline error → the repair helps).
Companions: budget 8.0 (rho=0.886, CI [0.185,1.000], holds identically);
`basis_shrinkage_0.20` at budget 4.0 (rho=0.771, CI **[0.000, 1.000]** — a
weaker, boundary-case companion, same direction, does not itself decisively
exclude zero). **Primary combination and its budget companion both hold; the
milder-ratio companion is directionally consistent but marginal.**

### (b) IT SEPARATES CLEANLY — **HOLDS**

`history_gated_ecology` (0.4588) and `topology_mismatch` (0.3087) are exactly
the two lowest baseline-error worlds of the six; the next-lowest safe world,
`selection_creation_compensation`, sits at 0.5527 — a gap of **0.0939**
(safe-world minimum is 20.5% above the harm-world maximum). This is an exact,
fully-powered rank fact at n=6 (see G0), not a sampling estimate.

### (c) DISPLACEMENT MAGNITUDE IS NOT THE DISCRIMINATOR — **MISSES on the literal rank criterion; genuine, disclosed, not softened**

Applying lean (b)'s own rank test to displacement: `history_gated_ecology`
(7.008) and `topology_mismatch` (13.182) are ALSO exactly the two lowest of
six, gap **3.747** (safe-world minimum 16.930 is 28.4% above the harm-world
maximum — a *larger* relative gap than baseline error's own 20.5%). This
directly contradicts the registration's own motivating framing
("`topology_mismatch` is mid-range at 13.18") once checked at full precision
rather than eyeballed from the rounded report table. **This leg reports this
as a miss, not a softened or reworded pass** — a 2-of-6 rank coincidence is,
on its own, a weak criterion (only 462 distinct 6-point bootstrap resamples
exist at this n; two discriminators both landing on the same 2 extreme
values by rank alone is not decisive evidence of independent predictive
value for both).

The correlation companion offers real, if partial, specificity: baseline
error's benefit-correlation CI is comfortably clear of zero (lower bound
0.185); displacement's touches zero exactly (lower bound 0.000) — weaker,
not decisively distinct, a genuine boundary case. **Net reading: the rank
test does not distinguish the two discriminators; the correlation test
shows baseline error somewhat more decisively related to benefit than
displacement, but not by a wide margin, and not enough to certify
displacement is "not the discriminator" in a clean sense.**

## 7. Pivot

**PIVOT DOES NOT FIRE.** The registered condition — "no discriminator in the
registered inventory separates the two harm worlds from the six safe ones" —
requires **every** discriminator to fail. `baseline_recovery_error` alone
already separates, decisively, by both the rank test (gap 0.0939, exact) and
the correlation test (CI [0.185, 1.000], excluding zero) — a single,
pre-registered, primary, directional test, sufficient on its own to resolve
the pivot's existential condition without needing the other four items'
both-direction, multiplicity-exposed checks. **The harm boundary is
predictable from at least one measured, pre-repair-applicable world
property.** The basis-shrinkage repair is therefore **not** undeployable in
principle in the sense this leg's registered pivot tests.

## 8. Verdict

**`HARM_BOUNDARY_PREDICTABLE_BUT_NOT_SPECIFIC_TO_COMPETENCE__PROVISIONAL_GATE_ONLY`.**

This is the honest middle finding the registration's three independent leans
were built to allow: (a) HOLDS, (b) HOLDS, (c) MISSES on its own literal
criterion. Reported plainly, not softened toward either a clean "gateable"
story or a clean "undeployable" one.

**Deployment picture, stated plainly:**

- The pivot does not fire — a candidate gating signal exists. A rule of the
  shape *"do not apply the basis-shrinkage repair where deployed baseline
  recovery error is low (roughly, below where the safe worlds cluster,
  ≈0.55 in this synthetic regime)"* is directly supported: rank-exact and
  correlation-CI-excluding-zero at the primary (ratio 1.00, budget 4.0)
  combination, direction-consistent across every budget/ratio combination
  tested (3 of 3 combinations positive-direction; 2 of 3 decisively
  CI-excluding zero).
- But **specificity is not cleanly established**. Baseline displacement — a
  DIFFERENT, mechanistically distinct quantity — achieves the identical rank
  separation (by an even larger relative gap) and only narrowly misses the
  correlation test (CI touching exactly zero, not decisively excluding it).
  This leg cannot rule out that "low baseline error" is standing in for a
  broader "this world is atypical on several correlated axes at once"
  property rather than a specific, understood causal channel. The other
  three registered candidates (S3 share, S4 share, conditioning number /
  effective rank) show **no** signal by either test — genuinely uninformative
  at this world count (the conditioning-number correlation's CI spans the
  entire possible range), not confident nulls.
- **Practical recommendation**: a gate keyed on baseline recovery competence
  (and/or displacement, since the two move together in this sample) is a
  reasonable, data-supported provisional safeguard against deploying the
  basis-shrinkage repair on a new, unvalidated corpus — but it should be
  treated as a heuristic screen, not a certified deployment gate, until
  validated on a larger, independent world set that can separate "low
  baseline error" from "low baseline displacement" as candidate mechanisms
  (they are too entangled in this 6-world sample to tell apart) and until a
  mechanism is identified for WHY low-baseline-competence worlds respond
  adversely to the shrinkage lever. This is consistent with, and extends
  without resolving, the open mechanism question M4-J1's hand-off explicitly
  left unaddressed.

## 9. Process notes

**Compute.** All 8 worlds' Part 0 computation ran in the foreground,
sequentially, quoted `"$PY"` throughout (M4-J1's own postmortem: an unquoted
interpreter path containing a space broke word-splitting on its first
parallel-launch attempt — this leg avoided that class of error by quoting
every invocation and, given the realized per-world cost, never needed
parallelism at all). Context loading reused M4-J1's own cached pickles
(`results/m4_j1_repair_generalization/_context_cache/contexts_{world}.pkl`,
read-only — cache hits, no writes into M4-J1's directory) rather than
rebuilding from scratch, since no new context content was needed beyond what
M4-J1 already built and persisted. Per-world Part 0 cost: 0.9–3.2 seconds
(context load from cache: <0.1s; S1/S2 pattern construction + GPA/shares:
0.9–1.6s typical, one outlier at 3.2s for the first world run — no truth
regeneration was needed since baseline error/displacement/benefit are read
directly from M4-J1's files, not recomputed). Total foreground wall-clock
for all 8 worlds plus assembly: well under two minutes. Zero Tracebacks or
RuntimeErrors on any computational content; `--smoke` (run first, on
`topology_mismatch`) caught nothing that needed fixing.

**Zero rescues, zero post-hoc tuning.** The ambiguity resolutions above
(world-scope for adjudication; what "separates cleanly" means) were written
into the script's own docstring — including the specific, falsifiable
prediction that a literal rank test would ALSO separate displacement —
**before** the Part 0 compute stage was run. The subsequent code mechanically
computed what the docstring committed to; the finding that lean (c) misses on
its own literal criterion was disclosed as found, not reworded, softened, or
replaced with a more favorable test chosen after seeing the number.

**No mechanical problems.** Every stage succeeded on its first invocation.

## 10. Scope

Everything here is synthetic, calibrated to the real-text regime, at
EXPLORATORY tier. It licenses a conclusion about whether THIS leg's five
registered candidate properties, measured on THIS 8-world synthetic set,
predict the basis-shrinkage repair's 2-world harm boundary found by M4-J1 —
they partially do, led by baseline recovery competence, with an unresolved
specificity question against baseline displacement. It licenses no claim
about any real corpus, construct, person, or diagnosis, no claim that the
identified candidate generalizes beyond this world set, and no deployment
decision by itself — F16 requires a new operator ID and seal for the
basis-shrinkage repair regardless of this leg's outcome, and this leg's own
"provisional gate only" reading means that decision should not proceed on
this evidence alone even if the operator wishes to adopt the repair with a
gate attached.
