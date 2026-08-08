# SUICA M4-J3 — Can the two candidate deployment gates be told apart?

Tier: **EXPLORATORY, label-free, synthetic.** Registered in
`docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md`, "M4-J3 registration
(2026-08-03, BEFORE run)". Ledger row `M4-J3`. Script:
`scripts/run_suica_m4_j3_gate_dissociation.py`. Artifacts:
`results/m4_j3_gate_dissociation/{decision.json, gates.json,
dissociation_evidence.json, dissociation_table.csv,
dissociation_pairwise*.csv, g1_selfcheck.json,
world_discriminator_harm_table.csv, anchor_deployed_table.csv,
anchor_harm_table.csv, new_world_deployed_table.csv,
new_world_harm_rows.csv, lean_b_competence_rows.csv,
lean_b_companion_full_population_rows.csv,
lean_c_threshold_classification_rows.csv, g3_check_rows.csv, per-world
partials}`.

## 0. Where this leg picks up

M4-J2 found the basis-shrinkage repair's 2-world harm boundary is predictable
from at least one measured, pre-application property, but by **two
discriminators confounded across the 8 `D1_WORLDS`**: baseline recovery
competence (Spearman rho=.886 vs. recovery benefit, CI [.185, 1.000]) and
baseline displacement (rank-separates by an even *larger* relative gap,
28.4% vs. error's 20.5%, though its correlation CI merely touches zero) both
rank-separate the identical two harm worlds (`history_gated_ecology`,
`topology_mismatch`). At n=6 neither can be credited over the other. This
leg asks directly: **can the two be dissociated, and if so, which one
actually predicts harm?**

## 1. Design as executed

**Anchor.** All 8 `D1_WORLDS` reused unchanged; every discriminator and harm
value for them is **read directly** from M4-J1's own persisted files
(`disp_rows.csv`, `author_level_truth_rows.csv`, `lean_b_safety_rows.csv`) —
identity by construction, per M4-J2's own established precedent for these
same two discriminators.

**New worlds — Part 0.2, registered before any new compute ran.** Two
avenues, both used:

- **Search.** Of the 15-world catalog, 7 worlds sit outside `D1_WORLDS`. Four
  are hard-blocked (`chart_refused=True` on all 8 archived reps:
  `author_leakage`, `evaluation_support_shift`,
  `hidden_opportunity_source_alias`, `response_leakage_circular`). One more
  (`linear_exogenous_selection`) has degenerate D_true on all 256 archived
  combinations. The two remaining, chart-usable, non-fully-degenerate
  candidates were both included: `endogenous_source_partition_matched`
  (seed-matched to `linear_exogenous_selection`, but its own mechanism has
  `truth_creation=1.0` on all 8 archived reps) and
  `slow_hysteresis_equal_marginal` (seed-matched to
  `fast_return_equal_marginal`, `truth_creation=0.0` and
  `loop_action_geometry` near/crossing zero on all 8 archived reps — an
  **anticipated, pre-stated risk** of the identical near-zero-denominator
  pathology its seed-partner is already known to carry).
- **Construct.** `generate_m4_chart_ecology_world(world=w, spec=spec,
  seed=s)` takes mechanism identity (`world`) and RNG draw (`seed`) as
  independent parameters; `leg3._world_seed`'s own pre-existing
  `matched_groups` table already demonstrates this split is a live feature
  of this program's machinery, not a new invention. Two hybrid worlds were
  built by crossing mechanism and seed-donor across the **extremes of the
  two discriminators**, read directly from M4-J1's own persisted
  `VALID_TRUTH_WORLDS` values (deployed arm, full precision, decided before
  any new compute):
  - `hybrid_hi_error_lo_disp` = mechanism(`condition_alias_ecology`, max
    error 0.9472805) @ seed(`history_gated_ecology`, min displacement
    7.007661)
  - `hybrid_lo_error_hi_disp` = mechanism(`topology_mismatch`, min error
    0.3087223) @ seed(`condition_alias_ecology`, max displacement
    22.730981)

  This selection rule is a parameter-free extremum read of data that already
  existed before this leg's registration was written.

## 2. G0, G2, G6 — reported first, per the outer task's instruction

### G0 POWER

The dissociating-world count is small by construction: 2 purpose-built
hybrids plus 2 found companions. A **pairwise rank inversion** between two
worlds' deployed-arm values, once both are measured, is a **deterministic
fact** — no sampling uncertainty, exactly the shape M4-J2's own G0 used for
its rank-2 separation. But a bare inversion can be noise-level (a fraction
of a percent on either axis), so this leg additionally requires **both**
axes' relative gap to clear a **10% materiality bar**
(`DISSOCIATION_MATERIALITY_RATIO`, reused unchanged from this program's own
`G2_MATERIALITY_RATIO` convention) before calling a pair a genuine
dissociation — reported alongside the unfiltered count for transparency.
`found_slow_hysteresis_equal_marginal` was confirmed pathological exactly as
anticipated (baseline error 7.91×10⁹, the identical order-of-magnitude
signature as M4-J1/M4-J2's own `EXCLUDED_TRUTH_WORLDS`) and excluded from
every dissociation/harm computation, leaving **3 usable new worlds** and
**C(3,2)=3** primary pairwise comparisons. The harm read on a dissociating
world (lean b) is a paired-by-author CI at the identical per-world grain
M4-J1/M4-J2 used, and inherits their identical power characterization
(n up to 8 reps × 2 views × 16 authors = up to 256 per world per budget).

### G2 DISSOCIATION LIVENESS

**Primary reading (pairwise among the 3 usable new worlds): MISSES, cleanly,
at both the bare and the material criterion — 0 of 3 pairs dissociate at
all.**

| world_a | world_b | error_a | error_b | disp_a | disp_b | dissociates (bare) |
|---|---|---:|---:|---:|---:|---|
| hybrid_hi_error_lo_disp | hybrid_lo_error_hi_disp | 0.9530 | 0.3252 | 22.450 | 13.349 | no |
| hybrid_hi_error_lo_disp | found_endogenous_source_partition_matched | 0.9530 | 0.7241 | 22.450 | 18.247 | no |
| hybrid_lo_error_hi_disp | found_endogenous_source_partition_matched | 0.3252 | 0.7241 | 13.349 | 18.247 | no |

The mechanism is itself an honest, disclosed finding, not an assumption:
Part 0.1 stated explicitly that the mechanism/seed split's effect on
`disp_v2` (unlike M4-G2's finding for `offset_norm`) was an *empirical*
question, since `disp_v2` compares against `oracle_basis`, which — unlike
the reference-calibration structure `offset_norm` is built from —
genuinely branches on mechanism identity inside `_condition_panels`. The
measured result: **both constructed hybrids' displacement values track
their MECHANISM donor's own native value almost exactly** (within 1–2%),
not their seed-donor's:

| hybrid | mechanism donor's own native (error, disp) | hybrid's measured (error, disp) |
|---|---|---|
| hybrid_hi_error_lo_disp | condition_alias_ecology: (0.9473, 22.731) | (0.9530, 22.450) |
| hybrid_lo_error_hi_disp | topology_mismatch: (0.3087, 13.182) | (0.3252, 13.349) |

Seed moved each value by only 1–5%, far too small to bridge the ~9.5-unit,
mechanism-driven displacement gap between `condition_alias_ecology` and
`topology_mismatch`. The lever this leg registered as a hypothesis
(seed-swap dissociates the two discriminators) does not, empirically, work
for `disp_v2` the way the analogous lever worked for `offset_norm` in
M4-G2.

**Companion, non-primary evidence (disclosed for thoroughness): a
full-population check** (8 anchor `D1_WORLDS` — with `EXCLUDED_TRUTH_WORLDS`'
2 pathological members screened out first, exactly the same screen already
applied to new worlds — plus the 3 usable new worlds, 9 worlds, C(9,2)=36
pairs) finds exactly **2 materially-dissociating pairs**, both involving
`history_gated_ecology`:

| world_a | world_b | error gap | disp gap |
|---|---|---:|---:|
| history_gated_ecology | topology_mismatch | 48.6% | 88.1% |
| history_gated_ecology | hybrid_lo_error_hi_disp | 41.1% | 90.5% |

**Neither is usable.** The first pair is between the **two worlds M4-J1
already found are BOTH harmed** — comparing them to each other shows a
genuine rank flip (their relative order on error and on displacement
disagrees), but since the dependent variable (harm) is identical on both
sides, the pair carries **zero discriminating power** between competence and
displacement. The second pair is a near-exact echo of the first, since the
hybrid's mechanism donor is `topology_mismatch` itself. Computed (see
Section 6) after lean (a)'s primary MISS was already final, both pairs
classify `BOTH_HARMED` at all four tested (arm, budget) combinations — no
information gained. An initial draft of this companion check omitted the
`EXCLUDED_TRUTH_WORLDS` pathology screen on the anchor side and reported 11
"dissociating" pairs; 6 of those involved `fast_return_equal_marginal` or
`linear_null_ecology`'s own ~10⁹ pathological error and were spurious. This
was caught and fixed in the same assembly pass, before the corrected result
was used for anything (Section 4).

### G6 MOTIVATING-FACT VERIFICATION

Every factual claim the M4-J3 registration cites (and the M4-J2 planner
adjudication note it inherits) was re-derived from M4-J1's persisted
`disp_rows.csv`/`author_level_truth_rows.csv` at full precision.

**The eight-world displacement table is verified CORRECT.** Cited:
`18.22 / 16.93 / 18.61 / 22.73 / 18.33 / 7.01 / 18.69 / 13.18`. Persisted
(full precision, matched 1:1, no duplicates, no misses):

| world | persisted disp_v2 | cited (rounded) |
|---|---:|---:|
| endogenous_creation_expansion | 18.224166 | 18.22 |
| selection_creation_compensation | 16.929591 | 16.93 |
| source_rotated_feedback | 18.613126 | 18.61 |
| condition_alias_ecology | 22.730981 | 22.73 |
| fast_return_equal_marginal | 18.328299 | 18.33 |
| history_gated_ecology | 7.007661 | 7.01 |
| linear_null_ecology | 18.692466 | 18.69 |
| topology_mismatch | 13.182162 | 13.18 |

All 8 matched, `all_eight_values_verified_correct = True`,
`any_cited_fact_found_wrong = False`. **Unlike M4-J2's own motivating-fact
error** (which mis-cited `topology_mismatch` as "mid-range at 13.18" when it
is in fact one of the two lowest), this registration's cited table is
correct as written.

Both cited rank-separation percentages were also re-derived and confirmed:

| discriminator | harm-world max | safe-world min | gap ratio (re-derived) | cited |
|---|---:|---:|---:|---:|
| baseline error | 0.458827 | 0.552703 | **20.46%** | 20.5% |
| baseline displacement | 13.182162 | 16.929591 | **28.43%** | 28.4% |

Both match to within 0.05 points. **No cited fact in this registration was
found wrong.**

## 3. G1, G3, G4 — the other gates

### G1 ANCHOR — PASS

| check | n | max abs diff | tolerance | pass |
|---|---:|---:|---:|---|
| 8 `D1_WORLDS` baseline error/displacement/harm — direct file read | — | **0.0** (identity by construction) | 1e-12 | yes |
| New context-builder self-validation: `history_gated_ecology` rep 0, `disp_v2` | 1 | **0.0** | 1e-12 | yes |
| New context-builder self-validation: same rep, `e_arm_true` by author | 16 | **2.22×10⁻¹⁶** | 1e-12 | yes |

The self-validation independently confirms that this leg's own new
context-builder (`_build_labeled_context`, invoked with
`mechanism_world==seed_world==`an existing anchor world) reproduces M4-J1's
persisted value exactly — validating that passing `expected_geometries=None`
(required since no archived V2 battery exists for the new mechanism/seed
combinations) does not compromise fidelity, and that the mechanism/seed
split degrades correctly to the ordinary case when the two arguments
coincide.

### G3 TRUTH-PATH INVARIANCE — PASS

`max_abs_diff = 0.0` over 12 checks (4 new worlds × 3 `BASIS_ARMS`),
disclosed near-duplicate of `j1._g3_spot_check` trimmed to skip the
`colstd_alpha_0.10`/G6 branch this leg never uses.

### G4 MATERIALITY FORM — compliant

G1 is exact identity-by-construction plus a ≤1e-12 self-check; G2 is an
exact pairwise rank-sign comparison with a registered 10% materiality bar
(no CI); G3 is a ≤1e-12 exact-equality check; lean (a) is a deterministic
existence claim; lean (b) is a classification over paired-by-author,
one-sided (±0.02) equivalence-CI outcomes, identical margin/grain to
M4-J1's own lean (b); lean (c) is an exact classification-accuracy check
against a threshold registered before any new-world outcome was computed.
None is a nil-significance test on a known-nonzero quantity.

## 4. Mechanical findings, disclosed with their resolutions

**(1) Per-repetition chart refusal, caught during world construction —
before any dissociation check or harm read.** `hybrid_lo_error_hi_disp`
(mechanism `topology_mismatch` @ seed-family `condition_alias_ecology`) hit
`chart.refused` at repetition 4 specifically, even though neither donor
world ever refuses across its own 8 native repetitions. This was an
*anticipated* possibility (Part 0.1 stated the construction's fidelity was
empirical, not assumed) but its specific location was not predictable in
advance. Resolved by catching the refusal per-repetition and skipping only
that repetition (a deterministic, outcome-blind response to a hard
compatibility constraint the generator itself imposes), leaving this label
at n=7 reps rather than 8 — disclosed in
`_context_cache/skipped_repetitions_hybrid_lo_error_hi_disp.json` and every
downstream statistic computed on however many contexts actually exist
(never hardcoded to 8). Caught and fixed before any new-world discriminator
or harm number existed.

**(2) Pathology-screen omission in the full-population companion check,
caught in the same assembly pass — before the corrected result was used for
anything.** The first draft of the full-population dissociation check did
not exclude `EXCLUDED_TRUTH_WORLDS` (the 2 anchor worlds M4-G2 already
identified as carrying a ~10⁹ near-zero-denominator pathology) from the
anchor side, and reported 11 "dissociating" pairs. Inspecting them showed 6
involved `fast_return_equal_marginal` or `linear_null_ecology` on one side —
spurious inversions driven entirely by their own known pathology, not by
any genuine competence signal. Fixed by applying the identical pathology
screen already used for new worlds to the anchor population too, leaving
the 2 genuine pairs reported in Section 2. This is exactly the kind of
mechanical problem this program's standing practice requires disclosing
plainly; it was caught before the corrected pairwise table was used to
adjudicate anything, and both readings (11 raw, 5 non-spurious, 2 material)
are preserved in `dissociation_pairwise_full_population.csv`.

**No other mechanical problems.** Every other stage succeeded on its first
invocation.

## 5. Full world × discriminator × harm table

Primary combination = `basis_shrinkage_1.00`, budget 4.0 (M4-J1/M4-J2's own
primary). `NaN`/`None` = not computed (pathological baseline, or — for the
2 `EXCLUDED_TRUTH_WORLDS` anchor rows — inherited from M4-J1's own scope).

| label | world | kind | baseline error (b4) | baseline disp | shrink100 worsens (b4) | shrink100 mean diff | shrink020 worsens (b4) | shrink020 mean diff |
|---|---|---|---:|---:|---|---:|---|---:|
| condition_alias_ecology | condition_alias_ecology | anchor | 0.9473 | 22.731 | No | −0.0033 | No | −0.0035 |
| endogenous_creation_expansion | endogenous_creation_expansion | anchor | 0.5815 | 18.224 | No | −0.0217 | No | −0.0215 |
| fast_return_equal_marginal | fast_return_equal_marginal | anchor (excl.) | 7.02×10⁹ | 18.328 | — | — | — | — |
| **history_gated_ecology** | history_gated_ecology | anchor (HARM) | 0.4588 | **7.008** | **Yes** | **+0.2060** | **Yes** | **+0.1477** |
| linear_null_ecology | linear_null_ecology | anchor (excl.) | 6.80×10⁹ | 18.692 | — | — | — | — |
| selection_creation_compensation | selection_creation_compensation | anchor | 0.5527 | 16.930 | No | +0.0299 | No | +0.0019 |
| source_rotated_feedback | source_rotated_feedback | anchor | 0.5660 | 18.613 | No | +0.0067 | No | −0.0109 |
| **topology_mismatch** | topology_mismatch | anchor (HARM) | **0.3087** | 13.182 | **Yes** | **+0.1091** | **Yes** | **+0.0537** |
| hybrid_hi_error_lo_disp | condition_alias_ecology | constructed | 0.9530 | 22.450 | No | +0.0047 | No | +0.0038 |
| hybrid_lo_error_hi_disp | topology_mismatch | constructed | 0.3252 | 13.349 | **Yes** | **+0.1378** | **Yes** | **+0.0762** |
| found_endogenous_source_partition_matched | endogenous_source_partition_matched | found | 0.7241 | 18.247 | No | +0.0291 | No | +0.0140 |
| found_slow_hysteresis_equal_marginal | slow_hysteresis_equal_marginal | found (pathological) | 7.91×10⁹ | 18.328 | — | — | — | — |

Full CSV: `results/m4_j3_gate_dissociation/world_discriminator_harm_table.csv`.

## 6. Dissociation evidence and its ordering

**The dissociation check used only the `deployed` arm — baseline error and
baseline displacement — and was fully assembled, written to disk, and
printed BEFORE any `--stage harm_arms` invocation existed in this leg's own
execution transcript.** File-timestamp proof
(`order_of_operations_proof` in `decision.json`):

- `dissociation_evidence.json` written: **2026-08-08T15:35:28.97 UTC**
- Earliest `partial_harm_*.csv` written: **2026-08-08T15:39:35.94 UTC**
- `evidence_predates_every_harm_partial`: **True** (all 16 harm partial
  files postdate the evidence file by 4+ minutes)

Operationally: `--stage deployed_only --label all` and `--stage
g1_selfcheck` ran first; `--assemble-dissociation` then read only anchor
files and the `deployed_only` partials, computed G2/lean(a), and printed
`DISSOCIATION NOT ACHIEVED` — at which point `--stage harm_arms` was
invoked for the first time, for full disclosure of the one potentially
informative companion pair identified in Section 2, never to reverse the
already-final lean (a) verdict. `dissociation_evidence.json` and
`dissociation_pairwise_full_population.csv` are reproduced bit-identically
by the final `--assemble` (diffed and confirmed identical).

## 7. Lean-by-lean adjudication

### (a) DISSOCIATION ACHIEVED — **MISSES** (primary reading)

At least two worlds must exist, among those newly searched/constructed, in
which the two discriminators rank oppositely — verified before harm. **0 of
3 pairwise comparisons among the usable new worlds dissociate**, at either
the bare or the 10%-materiality criterion (Section 2). Per the registration's
own branch for this outcome: **this leg's primary reading adjudicates
nothing further.** The full-population companion check does find 2 material
dissociating pairs, but both are between worlds already known (or shown, for
the one new member) to share the identical harm outcome — so even under the
most permissive reading of "two worlds exist," no pair usable for lean (b)
exists anywhere in this leg's evidence.

### (b) COMPETENCE WINS — **NOT ADJUDICATED**

No dissociating pair exists in the primary population (n=0), so there is
nothing for lean (b) to score; `held=False` by construction, with
`not_adjudicated=True` recorded explicitly rather than silently. The
disclosed, non-adjudicating companion (Section 2 / Section 5): both
full-population material pairs classify `BOTH_HARMED` at all four tested
(arm, budget) combinations — `history_gated_ecology` and `topology_mismatch`
are both harmed regardless of which one the discriminators rank as "more
extreme," and `hybrid_lo_error_hi_disp` (freshly computed here) confirms
this by inheriting `topology_mismatch`'s own harmed status almost exactly
(+0.1378 vs. topology's own +0.1091 at the primary combination — same
sign, comparable magnitude, if anything slightly larger). This companion
computation was performed *after* lean (a)'s MISS was already final and
never overrides it.

### (c) THE GATE IS USABLE — **NOT ADJUDICATED**

Lean (b) never crowned a winning discriminator, so lean (c) has nothing to
build a certified threshold test around; `held=False` by construction,
`not_adjudicated=True`. For transparency, both candidate thresholds were
still computed from `VALID_TRUTH_WORLDS` alone
(`threshold_error_b4=0.5058`, `threshold_displacement=15.056`, both
midpoints of the harm-max/safe-min gap, registered in Part 0.3 before any
new-world outcome existed) and applied to every world with a determined
harm outcome (6 anchor + 3 new = 9 worlds): **both thresholds classify all
9 correctly** (100% accuracy each) — but this is disclosed only as a
descriptive curiosity, since with no winning discriminator there is no
principled way to pick which threshold "the gate" should be, and scoring
either one now would be exactly the kind of post-hoc pick the standing
rules prohibit.

## 8. Pivot

**NOT APPLICABLE.** The pivot's own registered precondition is "in the
dissociating worlds" — with zero dissociating worlds in the primary
population, its antecedent is unsatisfied. It neither fires (that would
require a clean miss inside a population that exists) nor cleanly
does-not-fire (that would require lean (a) to have held); `fires=False`,
`not_applicable_dissociation_not_achieved=True`. This is the same shape
M4-G3's own pivot took when its leg was underpowered rather than resolved —
here the leg is not underpowered (G0's rank-inversion criterion is
deterministic, fully powered), it simply found no dissociation to test the
pivot's condition against.

## 9. Verdict

**`DISSOCIATION_NOT_ACHIEVED__GATE_STAYS_PROVISIONAL`.**

Per the registration's own instruction for this branch, stated plainly: **the
two candidates — baseline recovery competence and baseline displacement —
are not separable with the machinery available in this leg, and the harm
boundary's gate stays provisional.** This was a genuine, two-pronged attempt
(search across the full 15-world catalog's remaining chart-usable,
non-degenerate worlds; construction via the mechanism/seed-donor split that
this program's own `matched_groups` machinery already establishes as live)
verified before any harm outcome was touched, not a token gesture: the
search side accounted for every one of the 15 catalog worlds not already in
`D1_WORLDS` (4 hard-blocked, 1 fully degenerate, 2 tried), and the
construction side crossed the two discriminators' measured extremes exactly
as registered. The empirical result — that `disp_v2`, unlike `offset_norm`
in M4-G2, is overwhelmingly driven by mechanism identity rather than by
seed, so a mechanism/seed-donor swap reproduces the mechanism-donor's own
native (error, displacement) pair almost exactly rather than dissociating
it — is a first-class, disclosed finding in its own right, not a shortfall
to be explained away. The one place a genuine, material, non-spurious
dissociation *does* exist (`history_gated_ecology` vs. `topology_mismatch`,
sitting unnoticed in M4-J1's own persisted 8-world data all along) turns out
to be exactly the pair that cannot discriminate the two candidates, because
both members already share the same harm outcome.

**Deployment picture, stated as plainly as the registration requires:**

- The basis-shrinkage repair's harm boundary remains **predictable but not
  specifically attributable** — M4-J2's own verdict
  (`HARM_BOUNDARY_PREDICTABLE_BUT_NOT_SPECIFIC_TO_COMPETENCE__PROVISIONAL_
  GATE_ONLY`) is **neither strengthened nor weakened** by this leg; it is
  simply not yet resolvable with the machinery this leg could bring to bear.
- **No deployment gate can be certified on this evidence.** A gate keyed on
  baseline recovery competence (or on baseline displacement, or on some
  combination) remains a reasonable, data-supported *heuristic* screen
  against deploying the basis-shrinkage repair on an unvalidated corpus, but
  not a certified control — exactly M4-J2's own closing position, unchanged.
- `colstd_alpha_0.10` (the M4-G6 repair) remains entirely unaffected by any
  of this and is still the clean F16 deployment candidate — this leg
  concerns only the basis-shrinkage repair's provisional, uncertified gate.
- The next registration in this line, if this question is pursued further,
  needs either (i) a materially different construction lever than
  mechanism/seed crossing (which this leg found does not move `disp_v2`
  independently of mechanism), or (ii) to accept that competence and
  displacement may not be separable scalars at all in this objective's
  world space, and ask instead whether some other combination or
  transformation of the two (or a third property entirely) predicts harm
  where neither alone, nor a crossing of the two, can.

## 10. Process notes

**Compute.** ~19 minutes of foreground wall-clock from the first new-world
context build (00:22:23 local) to the final `decision.json`
(00:41:38 local), across chunked stages (`smoke_new`, `prep`,
`deployed_only`, `g1_selfcheck`, `assemble-dissociation`, `harm_arms`, `g3`,
`assemble`), each run in the foreground with an explicit long timeout, no
background jobs, no monitors. Internal concurrency inside individual
foreground calls (4 labels' `prep`/`deployed_only`/`harm_arms` launched via
shell `&`/`wait` within one Bash invocation each) followed this program's
own established precedent (M4-J1's "two batches ... concurrent on 10
cores"). Two mechanical problems, both disclosed in Section 4, both caught
and fixed before any hypothesis-relevant number existed.

**Zero rescues, zero post-hoc tuning.** The world-construction rule (Part
0.2), the threshold rule (Part 0.3), and the order-of-operations discipline
(Part 0.4) were all written into the script's own docstring before any new
compute ran. The full-population companion check was computed and disclosed
*because* the primary reading missed, not to manufacture a different answer
— and its own genuine positive result was traced to its root cause (two
already-both-harmed worlds) and reported as uninformative rather than
counted toward lean (a) or (b).

## 11. Scope

Everything here is synthetic, calibrated to the real-text regime, at
EXPLORATORY tier. It licenses a conclusion about whether THIS leg's
registered search-and-construction machinery can dissociate baseline
recovery competence from baseline displacement on THIS generator, and — it
cannot, with the two-pronged attempt actually made. It licenses no claim
about any real corpus, construct, person, or diagnosis, no claim that a
different construction lever would also fail, and no deployment decision by
itself — F16 still requires a new operator ID and seal for the
basis-shrinkage repair regardless of this leg's outcome, and that repair's
provisional-gate status is, if anything, reinforced rather than resolved by
what this leg found.
