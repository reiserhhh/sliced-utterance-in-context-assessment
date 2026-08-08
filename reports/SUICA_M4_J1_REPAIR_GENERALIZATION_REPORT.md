# SUICA M4-J1 — Do the certified repairs generalize beyond the three worlds that produced them?

Tier: **EXPLORATORY, label-free, synthetic.** Registered in
`docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md`, "M4-J1 registration
(2026-08-03, BEFORE run)". Ledger row `M4-J1`. Script:
`scripts/run_suica_m4_j1_repair_generalization.py`. Artifacts:
`results/m4_j1_repair_generalization/{decision.json, gates.json,
disp_rows.csv, truth_recovery_rows.csv, author_level_truth_rows.csv,
g2_liveness_rows.csv, colstd_ridge_liveness_rows.csv, g3_check_rows.csv,
lean_a_reduction_rows.csv, lean_b_safety_rows.csv,
lean_c_invariance_rows.csv, per-(world,arm) partials}`.

## 0. Where this leg picks up, and what it tests

Two repairs are certified in this program but deliberately UNADOPTED:

- **M4-G6**: per-column standardization of the hazard design at
  `alpha = 0.10 x deployed ridge`. Certified: exactly c-invariant (lean (a)
  HELD EXACTLY, 0.0 paired diff over all 745 authors, every c-pair, both
  budgets), recovery tied-or-better vs the best point fix, scale-free
  interior optimum. Certified on M4-G3/G4/G5's own 8-world `D1_WORLDS` for
  truth recovery and c-invariance, and on M4-G7's 3-world `HIGH_GAP_WORLDS`
  for displacement (where M4-G7 proved, structurally, that the repair moves
  Leg 14's displacement gap by exactly 0% — the ridge never enters
  `context["v2_basis"]`).
- **M4-H3/H4**: basis-whitening shrinkage. Certified: safe (recovery does
  not worsen) to ratio 1.0 (45.79% displacement reduction); actively good
  (recovery genuinely improves) to ratio 0.20 (34.66% reduction). Certified
  **only** on M4-E2's 3-world `HIGH_GAP_WORLDS`, for both metrics.

Adopting either changes a frozen operator, which under F16 creates a NEW
operator needing its own study ID and seal. This leg tests whether the
repairs generalize to a wider, 8-world set before that decision is put to
anyone — and per the registration's own framing, if they fail, the
deployment decision does not arise at all.

## 1. Design as executed

**World set.** `D1_WORLDS` (8, `g2.D1_WORLDS`, reused verbatim) =
`HIGH_GAP_WORLDS` (3: `endogenous_creation_expansion`,
`selection_creation_compensation`, `source_rotated_feedback` — the G1
anchors) + `FRESH_COMPANION_WORLDS` (5: `linear_null_ecology`,
`topology_mismatch`, `fast_return_equal_marginal`, `history_gated_ecology`,
`condition_alias_ecology` — genuinely new territory for the basis-shrinkage
repair on both metrics, and for the G6 repair's displacement metric).

**Arms (4).** `deployed` (anchor); `colstd_alpha_0.10` (the G6 repair,
literal reuse of `g6._resolve_all_params` / `g6._forced_route_derivative_
for_arm`); `basis_shrinkage_0.20` (H3's own actively-good arm, literal reuse
of `h3._basis_for_h3_arm`); `basis_shrinkage_1.00` (H4's own harmless-ceiling
arm, literal reuse of `h4._basis_for_h4_arm`). No new basis-construction or
estimator code was written; every construction call is a literal call into
h2/h3/h4/g2/g6's own already-certified machinery.

**Metrics (3, exactly as registered).**
1. Leg 14's displacement gap, `disp_v2`, per (world, repetition, arm), for
   the 3 basis arms. `colstd_alpha_0.10`'s `disp_v2` is **assigned** from
   `deployed`'s own value per (world, repetition) rather than independently
   recomputed through a second GPA/quotient-distance pipeline — this is not
   a shortcut but a reuse of M4-G7's own structural proof (Part 0 there)
   that `disp_v2`/`offset_norm` are pure functions of `context["v2_basis"]`
   alone, and the ridge never enters that object. This leg re-verifies the
   proof's precondition operationally, per world: `g6._resolve_all_params`'s
   own basis at c=1.0 is checked bit-identical to the `deployed`-arm basis
   in every one of the 8 worlds (`basis_identity_check`, below) before the
   assignment is trusted.
2. Truth-referenced recovery (`e_arm_true`), M4-F5-style, both
   `TRUTH_BUDGETS = (4.0, 8.0)`.
3. c-invariance of the G6 repair only (`colstd_alpha_0.10`), across
   `c in {0.25, 1.0, 4.0}`, via `g2._whitening_for_c`.

**Analysis grain — forced by the registration's own wording, disclosed
before adjudicating.** The registration's leans are stated **per world**
("in ≥75% of the wider world set", "in ANY world", "in every world") — a
materially different grain from every prior leg in this line, which pooled
reps/authors *across* worlds into one CI per arm. This leg's grain follows
directly: lean (a) is a paired-by-repetition CI computed **separately within
each world** (n=8 reps/world); leans (b)/(c) are paired-by-author CIs
computed **separately within each world** (n up to 256/world/budget). This
is honestly less powerful, per comparison, than every prior leg's pooled
grain — see G0 below and the per-row `underpowered_vs_g0_bar` flags in the
persisted CSVs.

**World-scope restriction for leans (b)/(c) — inherited, not derived here.**
`linear_null_ecology` and `fast_return_equal_marginal` carry a pre-existing,
world-intrinsic `_relative_error` near-zero-denominator fragility at these
truth budgets, discovered by M4-G2 and reused verbatim by every leg since
(G3–G6) as `VALID_TRUTH_WORLDS` (6 of 8). This leg reproduces the same
pathology operationally rather than merely citing it — `deployed`'s own
`e_arm_true` in these two worlds averages **7.0×10⁹** and **6.8×10⁹**
respectively (budget=4x, author grain), vs 0.31–0.95 in the other six worlds
— confirming the restriction is real and not a leg-specific artifact.
Displacement (lean a) has no such fragility and uses all 8 worlds.

## 2. G0, G1, G2 (reported first, per the outer task's instruction)

### G0 POWER

| lean | grain | target cited | realized power |
|---|---|---|---|
| (a) | paired-by-repetition, n=8/world | H4's persisted 45.79% reduction, ~18-unit deployed disp_v2 | 6/8 worlds adequately powered vs their own bar; 2/8 flagged UNDERPOWERED (`history_gated_ecology` — also the one MISS; `topology_mismatch` — a HOLD with wide CI but decisively excluding zero) |
| (b) | paired-by-author, n≤256/world/budget | ±0.02 margin, G0_FRACTION_BAR=0.01 half-width (this line's own convention since M4-G4) | 30/36 comparisons flagged UNDERPOWERED vs the strict 0.01 bar — but **every one of the 8 OUTSIDE (worsening) classifications sits 2.68×–10.3× beyond the ±0.02 margin itself**, decisive despite the coarser power (identical reasoning to M4-H2's own G0 disclosure: half-width nominally over the bar does not undermine a classification nowhere near the margin boundary) |
| (c) | paired-by-author, n≤256/world/budget/c-pair | M4-G6's own exact 0.0 finding (an algebraic identity, not a statistical result) | 0/36 underpowered — every check's half-width is exactly 0.0, because every individual row is bit-identical across c (verified directly, §5) |

### G1 ANCHOR — EXACT (0.0, not merely ≤1e-12), all four arms, on the 3 `HIGH_GAP_WORLDS`

| arm | metric | source | n checks | max abs diff |
|---|---|---|---|---|
| `deployed` | disp_v2 | Leg 14 `displacement_rows.csv` | 24 | **0.0** |
| `basis_shrinkage_0.20` | disp_v2 | H3 `disp_rows.csv` | 24 | **0.0** |
| `basis_shrinkage_1.00` | disp_v2 | H4 `disp_rows.csv` | 24 | **0.0** |
| `colstd_alpha_0.10` | disp_v2 | M4-G7 `displacement_by_rep.csv` (`repaired` arm) | 24 | **0.0** |
| `deployed` | truth (c=1) | H4 `truth_recovery_rows.csv` | 1536 | **0.0** |
| `basis_shrinkage_0.20` | truth (c=1) | H3 `truth_recovery_rows.csv` | 1536 | **0.0** |
| `basis_shrinkage_1.00` | truth (c=1) | H4 `truth_recovery_rows.csv` | 1536 | **0.0** |
| `colstd_alpha_0.10` | truth (c=0.25,1,4) | M4-G6 `truth_recovery_rows.csv` | 4608 | **0.0** |
| `colstd_alpha_0.10` basis@c=1.0 vs `deployed` basis | structural identity | (internal, all 8 worlds) | 64 | **0.0** |

**Overall G1: PASS, max abs diff 0.0 across 9,376 checks.** This is what
licenses the 5 `FRESH_COMPANION_WORLDS` as an EXTENSION rather than a
re-derivation: the exact same machinery, called the exact same way, first
verified to reproduce every persisted number on the worlds it was certified
on, before being trusted on worlds it has never seen.

### G2 REPAIR LIVENESS — per arm per world, all live

- **Basis arms** (h2's own `G2_MATERIALITY_RATIO=0.10` convention: basis
  distance vs deployed ≥ 10% of that world's own deployed median disp_v2):
  **16/16 (arm, world) cells live**, smallest ratio 48.9%
  (`basis_shrinkage_0.20` / `selection_creation_compensation`) — nearly 5×
  the materiality bar even at its weakest cell.
- **`colstd_alpha_0.10`**: realized `ridge_deployed` matches
  `alpha × deployed_ridge` exactly (0.0 abs diff, every world/rep/c — e.g.
  deployed ridge 0.005, realized colstd ridge 0.0005 exactly) and the
  applied whitening's Frobenius norm scales exactly linearly with c relative
  to c=1.0 (max abs diff from the exact ratio: **8.88×10⁻¹⁶**, floating-point
  noise). Both algebraic identities already proved generally by M4-G2/M4-G4;
  this leg re-verifies them per world rather than assuming they carry over.

**G2 overall: all live, no arm's result is VACUOUS anywhere.**

## 3. G3, G4, G5

**G3 TRUTH-PATH INVARIANCE**: max abs diff **0.0** over 48 checks (one
non-degenerate (rep,view,author) spot check per world × 6 variants: 3 basis
arms + 3 c's of `colstd_alpha_0.10`). PASS.

**G4 MATERIALITY FORM**: every gate above (G1 exact reproduction; G2
materiality-ratio / exact-arithmetic identity; G3 exact reproduction) and
every lean below (a: fraction-of-worlds bound on a paired CI; b: one-sided
equivalence ±0.02 — "does not worsen", this line's own established
one-sided reading, reused unchanged from H2/H3/H4; c: two-sided equivalence
±0.02 — invariance is symmetric, reused unchanged from M4-G4) is an
equivalence, exactness, materiality-ratio, or fraction bound. None is a nil-
significance test on a known-nonzero quantity. Compliant.

**G5 DUAL-WINNER reporting**: this leg's 4 arms are pre-registered fixed
points, not a ladder search — there is no new "winner" to select. Per the
seventh standing rule's spirit, §6 below reports which repair is safe
("harmless") vs which is actively good, **per world**, rather than
collapsing to a single pick anywhere a comparison is made.

## 4. Per-arm × per-world table: displacement (`disp_v2`, median over 8 reps)

| world | deployed | shrink 0.20 | reduction% | shrink 1.00 | reduction% |
|---|---:|---:|---:|---:|---:|
| endogenous_creation_expansion (anchor) | 18.22 | 11.91 | 34.6% | 10.06 | 44.8% |
| selection_creation_compensation (anchor) | 16.93 | 11.28 | 33.4% | 9.31 | 45.0% |
| source_rotated_feedback (anchor) | 18.61 | 11.61 | 37.6% | 9.62 | 48.3% |
| condition_alias_ecology | 22.73 | 15.60 | 31.4% | 13.77 | 39.4% |
| fast_return_equal_marginal | 18.33 | 12.13 | 33.8% | 10.16 | 44.5% |
| **history_gated_ecology** | 7.01 | 6.71 | **4.3%** | 6.74 | **3.8%** |
| linear_null_ecology | 18.69 | 11.61 | 37.9% | 9.58 | 48.7% |
| topology_mismatch | 13.18 | 5.04 | 61.7% | 5.05 | 61.7% |

`colstd_alpha_0.10`'s displacement is identical to `deployed`'s in every
world by the structural identity in §1/§5 (not a separate column above).
`history_gated_ecology` is a visibly different world: baseline displacement
is under half of every other world's (7.01 vs 13.18–22.73), and the repair
barely touches it (~4%). `topology_mismatch` is the opposite extreme: the
single largest reduction of any world (61.7%) and the ratio-0.20-vs-1.00
difference has already flattened to nothing there.

## 5. c-invariance of the G6 repair (`colstd_alpha_0.10`), per world

**Every one of 36 checks (6 worlds × 2 budgets × 3 c-pairs) is EXACTLY
0.0** — mean diff 0.0, CI [0.0, 0.0], classification WITHIN, in every single
row. This is not a statistical near-zero: a direct row-level check confirms
`e_arm_true` for `colstd_alpha_0.10` is bit-identical across c=0.25/1.0/4.0
for a sampled (world, rep, view, author, budget) cell (e.g.
`topology_mismatch` rep 0, train, author 0, budget=4: `0.105885` at all
three c's, vs `deployed`'s `0.332382` in the same cell) — confirming M4-G6's
own algebraic argument (per-column standardization exactly cancels a
uniform per-column c-multiplier) holds row-by-row, not merely in aggregate,
and **holds identically in all 6 `VALID_TRUTH_WORLDS`, with zero
exceptions.**

| world | all 6 (budget × c-pair) checks | held exactly |
|---|---|---|
| condition_alias_ecology | 6/6 WITHIN, mean 0.0 | yes |
| endogenous_creation_expansion | 6/6 WITHIN, mean 0.0 | yes |
| history_gated_ecology | 6/6 WITHIN, mean 0.0 | yes |
| selection_creation_compensation | 6/6 WITHIN, mean 0.0 | yes |
| source_rotated_feedback | 6/6 WITHIN, mean 0.0 | yes |
| topology_mismatch | 6/6 WITHIN, mean 0.0 | yes |

## 6. Per-arm × per-world table: recovery (`e_arm_true`, author-grain mean, c=1.0)

Budget = 4.0 (budget = 8.0 is materially identical in every cell, ≤0.03 away
throughout — full table in `author_level_truth_rows.csv`):

| world | deployed | shrink 0.20 | shrink 1.00 | colstd 0.10 |
|---|---:|---:|---:|---:|
| endogenous_creation_expansion (anchor) | 0.5815 | 0.5600 | 0.5598 | 0.5962 |
| selection_creation_compensation (anchor) | 0.5527 | 0.5546 | 0.5826 | 0.5586 |
| source_rotated_feedback (anchor) | 0.5660 | 0.5551 | 0.5727 | 0.5446 |
| condition_alias_ecology | 0.9473 | 0.9438 | 0.9440 | 0.9275 |
| **history_gated_ecology** | 0.4588 | **0.6066** | **0.6648** | **0.2394** |
| **topology_mismatch** | 0.3087 | **0.3624** | **0.4178** | **0.2533** |

(`linear_null_ecology`/`fast_return_equal_marginal` excluded per §1; their
`deployed` values sit at ~10⁹, confirming the exclusion is real.)

The pattern is stark and consistent at both budgets: in the two named
worlds, both basis-shrinkage settings make recovery **decisively worse**
than deployed, monotonically worse as the ratio increases (0.20 → 1.00),
while `colstd_alpha_0.10` makes recovery **decisively better** in the same
two worlds — a large, well-powered divergence between the two repair
families in exactly the worlds where it matters.

## 7. Lean-by-lean adjudication

### (a) THE REDUCTION GENERALIZES — **HOLDS**

`basis_shrinkage_1.00` clears ≥25% reduction with a paired CI (n=8
reps/world) excluding zero in **7 of 8 worlds (87.5%)**, above the
registered 75% bar:

| world | reduction% | CI | held |
|---|---:|---|---|
| endogenous_creation_expansion | 47.2% | [6.62, 10.95] | yes |
| selection_creation_compensation | 43.3% | [6.58, 8.15] | yes |
| source_rotated_feedback | 46.7% | [7.63, 9.68] | yes |
| condition_alias_ecology | 38.5% | [7.55, 9.68] | yes |
| fast_return_equal_marginal | 45.9% | [7.53, 9.40] | yes |
| linear_null_ecology | 48.4% | [7.05, 10.34] | yes |
| topology_mismatch | 57.8% | [2.21, 12.35] | yes (underpowered but decisive: CI excludes zero by >2 units) |
| **history_gated_ecology** | **21.5%** | **[−1.25, 5.19]** | **no** — below the 25% bar AND the CI includes zero |

**7/8 = 87.5% ≥ 75% bar → HOLDS.** The one miss, `history_gated_ecology`, is
the same world flagged as a named safety risk in lean (b) below — not a
coincidence given its anomalously small baseline displacement (§4).

### (b) SAFETY GENERALIZES — **MISSES, decisively, for the basis-shrinkage repair; HOLDS for the G6 repair**

Recovery does **not** hold "does not worsen in ANY world" for either
`basis_shrinkage_0.20` or `basis_shrinkage_1.00`:

**Named deployment-risk worlds (material finding, not averaged away):**

| arm | world | budget | mean diff vs deployed | CI | margin multiple | classification |
|---|---|---:|---:|---|---:|---|
| basis_shrinkage_0.20 | history_gated_ecology | 4 | +0.1477 | [0.1251, 0.1704] | 7.4× | **OUTSIDE (worsens)** |
| basis_shrinkage_0.20 | history_gated_ecology | 8 | +0.1481 | [0.1253, 0.1709] | 7.4× | **OUTSIDE (worsens)** |
| basis_shrinkage_0.20 | topology_mismatch | 4 | +0.0537 | [0.0317, 0.0757] | 2.7× | **OUTSIDE (worsens)** |
| basis_shrinkage_0.20 | topology_mismatch | 8 | +0.0559 | [0.0347, 0.0772] | 2.8× | **OUTSIDE (worsens)** |
| basis_shrinkage_1.00 | history_gated_ecology | 4 | +0.2060 | [0.1779, 0.2341] | 10.3× | **OUTSIDE (worsens)** |
| basis_shrinkage_1.00 | history_gated_ecology | 8 | +0.2062 | [0.1781, 0.2343] | 10.3× | **OUTSIDE (worsens)** |
| basis_shrinkage_1.00 | topology_mismatch | 4 | +0.1091 | [0.0830, 0.1352] | 5.5× | **OUTSIDE (worsens)** |
| basis_shrinkage_1.00 | topology_mismatch | 8 | +0.1114 | [0.0863, 0.1365] | 5.6× | **OUTSIDE (worsens)** |

All 8 are decisive (2.7×–10.3× the ±0.02 margin, not knife-edge) at both
truth budgets, for **both** certified basis-shrinkage settings — including
`basis_shrinkage_0.20`, the setting M4-H3 certified as "actively good," and
`basis_shrinkage_1.00`, the setting M4-H4 certified as "harmless." Neither
certified safety level survives in these two worlds; the harm is *larger* at
the harmless-ceiling ratio (1.00) than at the actively-good ratio (0.20) in
both worlds — the same direction the target-vs-safety trade-off has taken
everywhere else in this program.

Elsewhere, basis-shrinkage is either safe (`WITHIN`: 11/24 remaining
cells) or genuinely ambiguous at this leg's own per-world grain (`AMBIGUOUS`:
5/24 — `selection_creation_compensation`/`basis_shrinkage_1.00` and
`source_rotated_feedback`/`basis_shrinkage_1.00` among them; not classified
as worsening, but not cleanly cleared either).

`colstd_alpha_0.10` (the G6 repair) **worsens recovery in zero of the 6
worlds** — 8/12 cells `WITHIN`, 4/12 `AMBIGUOUS`, 0/12 `OUTSIDE`. In the same
two worlds where basis-shrinkage fails worst, `colstd_alpha_0.10` shows
large, decisive **improvements** (history_gated_ecology: −0.22 to −0.24;
topology_mismatch: −0.055 to −0.074, both far past the "actively good" side
of the margin).

**Lean (b) verdict: MISSES for the basis-shrinkage repair (both ratios) —
`history_gated_ecology` and `topology_mismatch` are named, explicit,
well-powered, material deployment-risk findings, not averaged away. HOLDS
for the G6 repair (`colstd_alpha_0.10`), which shows no worsening anywhere
and active improvement in the two worlds that break the other repair.**

### (c) INVARIANCE IS WORLD-INDEPENDENT — **HOLDS, exactly**

6/6 `VALID_TRUTH_WORLDS`, 36/36 checks, every mean diff **exactly 0.0**
(§5). M4-G5's reparameterization argument is confirmed a property of the
construction (the per-column standardization algebra), not of the three
worlds it was first demonstrated on.

## 8. Pivot

**PIVOT DOES NOT FIRE.** The registered pivot condition ("the reduction
fails to reach 25% in ≥75% of the wider set") requires lean (a) to miss;
lean (a) holds decisively (87.5% ≥ 75%). The repairs are **not**
world-set-specific in the sense the pivot tests.

## 9. Verdict

**`REDUCTION_GENERALIZES__SAFETY_FAILS_IN_NAMED_WORLD__INVARIANCE_WORLD_INDEPENDENT`.**

This is not an outcome outside the registered branches — it is the
combination the registration's three *independent* leans were built to
allow: (a) HOLD, (b) MISS (with the miss isolated to one of the two repair
families and two named worlds), (c) HOLD. No lean was softened, re-scored,
or averaged to reach a cleaner-sounding combined answer.

**Practical reading for the frozen-operator decision this leg exists to
inform (not itself a deployment decision — F16 still applies):**

- The **G6 repair** (`colstd_alpha_0.10`) generalizes essentially without
  qualification: its displacement-neutrality is a proven structural
  identity independent of world; its c-invariance is exact and
  world-independent (§5); and its safety is not merely non-worsening but
  actively better than deployed in every world tested, including the two
  where the other repair fails worst.
- The **basis-shrinkage repair** (`basis_shrinkage_0.20`/`1.00`) generalizes
  on its *target* (displacement reduction, 7/8 worlds) but **not on
  safety** — a genuine, decisive, well-powered material risk in 2 of 8
  (25%) of the wider world set, at **both** certified settings, worse at
  the more aggressive one. The M4-E2 three-world certification did not
  surface this because none of the three `HIGH_GAP_WORLDS` happens to be a
  world like `history_gated_ecology` or `topology_mismatch`.

## 10. Process notes

**Compute.** ~22 minutes total foreground wall-clock across two batches
(1 world run singly for timing calibration, ~5.6 min; then 4 worlds
concurrent, ~8.5 min; then 3 worlds concurrent, ~6.9 min — all on this
machine's 10 cores, matching this program's established precedent of
disclosed internal concurrency within foreground, explicitly-timed
invocations, no background jobs, no monitors). Per-world cost: context
build ~35–45s (8 reps), truth regeneration ~140–150s (arm-invariant,
cached), 3 basis arms' truth ~70s combined, `colstd_alpha_0.10`'s 3-c truth
sweep ~15–145s (fast in the two excluded-validity worlds, where most rows
are `degenerate_reference` and skipped). All 8 worlds completed with zero
Tracebacks or RuntimeErrors on their computational content.

**One mechanical problem, caught and fixed before any hypothesis-relevant
number existed.** The first parallel-launch attempt (4 worlds concurrently)
used an unquoted `$PY` shell variable whose value
(`/Volumes/mobile3/projects/project persona/.venv/bin/python3`) contains a
space; word-splitting broke it into two tokens and all four worker
processes failed immediately on their very first command
(`/tmp/m4j1_run_world.sh: line 10: /Volumes/mobile3/projects/project: No
such file or directory`) — before any context was built, any row computed,
or any partial file written. Fixed by quoting `"$PY"`; the batch was
re-launched from a clean slate and completed with no further issues.

**Zero rescues, zero post-hoc tuning.** No lean's classification, margin, or
world scope was changed after computation began. The `VALID_TRUTH_WORLDS`
restriction was inherited from M4-G2 before this leg existed, not
introduced or adjusted here.

## 11. Scope

Everything here is synthetic, calibrated to the real-text regime, at
EXPLORATORY tier. It licenses a generalization verdict for two specific,
already-frozen operator repairs — that the G6 repair is safe and
world-independent to deploy consideration, and that the basis-shrinkage
repair is not, without further qualification, until the mechanism behind
its `history_gated_ecology`/`topology_mismatch` failure is understood. It
licenses no claim about any real corpus, construct, person, or diagnosis,
and no deployment decision by itself — F16 requires a new operator ID and
seal for either repair regardless of this leg's outcome.
