# SUICA M4-H6 — Is the S4 residual attackable at all?

Tier: **EXPLORATORY, label-free, synthetic.** Registered in
`docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md`, "M4-H6 registration
(2026-08-03, BEFORE run)", preceded by "M4-H5 planner adjudication note —
the survivor has a name, and no handle" (same date). Ledger row `M4-H6`.
Script: `scripts/run_suica_m4_h6_residual_reproducibility.py`. Artifacts:
`results/m4_h6_residual_reproducibility/{decision.json, gates.json,
disp_rows.csv, offset_shares_by_arm.csv, g3check_rows.csv,
per_rep_delta_construction_checks.csv, per_rep_s4_share_rows.csv,
within_world_pair_rows.csv, across_world_pair_rows.csv, null_draws.csv,
within_world_summary.csv, across_world_summary.csv, per-(world,arm)
partials}`.

## 0. Where this leg picks up

M4-H5 found that the safe lever's repair does not create a new carrier —
it **entrenches** the one M4-E2 already found largest at `deployed`: S4,
the residual block defined by *exclusion* (whatever survives projecting out
S1, S2 and S3), rises from a 40–45% plurality pre-repair to a 51–52%
majority of what survives at the harmless winner (`basis_shrinkage_1.00`),
in all 3 worlds, under this line's own adopted ordering. Unlike S3 — three
named, code-legible normalization/scale-mode families — **S4 has no
operational construction of its own to attack.** M4-H5's planner
adjudication note framed the one decisive question this leaves: does S4
carry *reproducible* structure across repetitions (something a future basis
could be built to capture), or is it *repetition-specific* — in which case
the ~46% of the displacement that survives the safe lever is irreducible at
this level, and the M4-H basis line closes on that statement.

## 1. Part 0 — what is genuinely new here, registered before compute

**Reuse.** No new Part 0 audit, no new basis-construction formula. Both
arms (`deployed`, `basis_shrinkage_1.00`) are literal calls into h5's own
2-way arm router (`h5._basis_for_h5_arm`), itself a literal call into H4's
own already-anchored `_basis_for_h4_arm`. The world-level offset/shares
computation is a disclosed near-duplicate of H3's/H4's own
`_arm_offset_and_shares_h{3,4}` (themselves near-duplicates of H2's own
`_arm_offset_and_shares`) — unchanged except for the arm-dispatch call.
G3 reuses `h5._g3_spot_check_h5` verbatim, filtered to this leg's 2 arms.

**What is new: a per-repetition analogue of "Delta."** Every predecessor
leg's offset vector is a WORLD-level object built from the GPA
(generalized-Procrustes) consensus of a world's 8 repetitions. No
predecessor leg needed a *per-repetition* version, because no predecessor
leg's leans were about cross-repetition agreement. This leg's entire new
construction is that one object (`_delta_rep_in_consensus_gauge`), built so
it is directly comparable, across repetitions, to the world's own S1/S2/S3
bases:

1. **Native-gauge delta** (existing functions only): `delta_native =
   pad(v2_frame_r) − align(pad(swap_frame_r), pad(v2_frame_r))`. Because the
   optimal Procrustes alignment distance `min_R‖A−BR‖_F` is *symmetric* in
   `(A,B)`, `‖delta_native‖` is provably equal to the already-anchored,
   already-gated Leg-11 `disp_v2` value for that (world, rep, arm) — the
   same scalar every predecessor's `disp_rows.csv` already persists, via a
   differently-ordered but exactly-equal computation.
2. **Gauge rotation.** `R_r`, the rotation `leg14._align` uses internally to
   bring `pad(v2_frame_r)` onto the world's own consensus `a_center`,
   extracted explicitly via a disclosed 3-line near-duplicate of
   `leg14._align`'s own SVD body (`_align` returns only `frame @ R`, never
   `R` itself).
3. **`delta_rep = delta_native @ R_r`.** This is *not* an independent
   second alignment of `swap_frame_r` onto `a_center` (which would use a
   *different* rotation and silently corrupt the rep's own v2-vs-swap
   relative geometry). It is the algebraic identity `align(B@R, A@R) =
   align(B, A) @ R` for orthogonal `R` (proof: `‖AR − BRQ‖_F = ‖A −
   B(RQRᵀ)‖_F` for every `Q ∈ O(W)`, and conjugation by `R` is a bijection
   on `O(W)`, so the argmin transports exactly) — i.e. `delta_rep` is
   exactly "rigidly rotate the (v2, swap) *pair* into `a_center`'s gauge
   together, preserving their mutual geometry," not two independent,
   geometry-corrupting alignments.

This matters because S1/S2 (and S3's n1 sub-family) are provably
right-`O(W)`-gauge **invariant** by construction (pattern ⊗ full column
space), but S3's n2/n3 sub-families are gauge-**equivariant** — built
directly from `a_center`'s own realized right-singular-vectors and
row-blocks. A per-rep delta left in its own uncontrolled native gauge would
give *wrong*, rep-specific-noise-contaminated S3/S4 shares. A synthetic
unit test (not part of the leg's own compute, run before any real data) put
a number on exactly this: a gauge-invariant toy basis gave identical shares
(0.0156170419530426 vs. 0.0156170419530426) on `delta_native` and
`delta_rep`; a gauge-equivariant toy basis (mirroring n2's own
construction) gave *different* shares (0.0257 vs. 0.0340) — confirming the
alignment step is not optional. `‖delta_rep‖ = ‖delta_native‖` exactly
(rotation preserves the Frobenius norm) and the whole construction is
gated, below, against real data.

Once `delta_rep` is in `a_center`'s gauge, `e2._sequential_shares` — the
same function, same `bases` dict every predecessor leg already builds — is
reused verbatim to extract `S4_residual`'s own component vector for that
repetition. **No new S1/S2/S3/S4 decomposition math exists anywhere in this
file; the only new code is the coordinate-frame bookkeeping above.**

**Scope decision 1 (registered order only).** Unlike M4-H5, this leg's own
registration never asks for a reverse-order companion — the leans and pivot
are stated purely in terms of "S4's direction," with no ordering-sensitivity
instruction. Registered order (S1→S2→S3→S4) only is computed; this is a
scope decision made explicitly before compute, not an oversight.

**Scope decision 2 (no truth-recovery machinery).** Citing M4-H5's own
identical, already-adjudicated precedent: this leg's registered
Design/Leans/Gates never mention `TRUTH_BUDGETS`. Reading A (ADOPTED, same
as H5): out of scope. G3 "truth-path invariance where applicable" is
satisfied by the same lightweight world-build faithfulness spot-check H5
used, gating no lean.

**The registered null — repetition-shuffled, never a synthetic-random-matrix
null, and never zero.** M4-E2 disclosed that
`_procrustes_cosine(A,B) = nuclear_norm(AᵀB)/(‖A‖‖B‖)` is a sum of
non-negative singular values — inflated even for two *independent* random
Gaussian matrices of the relevant shape. The registered, deciding
comparator here is instead: pool, per arm, the 24 real, already-computed
`S4_residual` components (3 worlds × 8 reps, fixed order `k = world_index×8
+ repetition`); draw 200 random permutations of `{0..23}` (**shared across
both arms**, so arm-to-arm comparisons are not muddied by independent
permutation noise); chunk each into 3 groups of 8; within each pseudo-group
compute all C(8,2)=28 pairwise `|Procrustes cosine|` values (already
non-negative by construction — "absolute value" in the registration's own
words needs no extra `abs()`); pool the 3×28=84 values per draw and take
their mean. This is ONE null distribution per arm (200 draws), used as the
comparator for *every* agreement number this leg reports, exactly as
required. Because the null is built from REAL, already-computed vectors
(not synthetic Gaussians), whatever "inflation" the statistic carries from
S4's own realized rank/shape is present identically in both the real
statistic and the null — the apples-to-apples comparison M4-E2's disclosure
demands. The synthetic random-matrix null (E2's own construction) is
computed too, but only as a **disclosed, non-deciding companion**, reported
in G0 below.

## 2. Design as executed

Worlds: the 3 `HIGH_GAP_WORLDS`, unchanged. Arms: `deployed` (reference,
disclosed companion throughout) and `basis_shrinkage_1.00` (M4-H4's
HARMLESS winner — leans are evaluated here). Grain: **PAIR** — the
agreement statistic is inherently defined per pair of repetitions, the
metric's own natural finest unit (mirroring H2's own adoption of REP grain
for `disp_v2` for the identical reason). WITHIN-WORLD n=28 (C(8,2), one
world); ACROSS-WORLD n=192 pooled (3 world-pairs × 64), per-world-pair n=64
reported as a disclosed companion. CI: `g1._paired_world_ci` — this line's
own generic one-sample t-CI helper, reused unchanged, applied directly to
the pair-level array — the same simplicity convention this entire line uses
throughout (no new statistical machinery for the CI itself).

Execution, entirely foreground with explicit per-call timeouts, no
background jobs, no monitors: a synthetic unit test of the new construction
(before any real compute); `--smoke` (one rep, both arms, 5.6s); `--world W
--stage g3` for all 3 worlds (context build 35.3–39.7s/world for 8 reps);
`--world W --arm A` for all 3 worlds × 2 arms (1.1–3.2s each, reusing the
per-world context cache); `--assemble`. Total wall-clock under 3 minutes of
compute across all stages.

## 3. G0 POWER — the null's spread and the design's MDE, stated first

| arm | null median | null q05 | null q95 | null std (draw means) | pooled pair std | MDE @ within-world (n=28) | MDE @ across-world (n=192) |
|---|---|---|---|---|---|---|---|
| `deployed` | 0.3779 | 0.3740 | 0.3821 | 0.00258 | 0.02814 | 0.0109 | 0.0040 |
| `basis_shrinkage_1.00` | 0.3260 | 0.3217 | **0.3313** | 0.00281 | 0.03617 | 0.0140 | 0.0051 |

Grain justification: PAIR is the metric's own natural finest unit (Section
2). MDE is computed from the null's own pooled pair-level std (a
non-circular, pre-adjudication variance proxy — computed and reported
*before* any real within/across-world number is compared to it) using the
standard t-based half-width formula. Context, stated before adjudicating:
the null's own q95 sits 0.6687 (harmless) / 0.6179 (deployed) below the
trivial ceiling of 1.0, and 0.1687 / 0.1179 away from lean (c)'s own
registered 0.5 materiality bar — both an order of magnitude larger than the
within-world MDE (0.0140/0.0109), so this design is comfortably powered to
detect a *material* effect (something approaching lean (c)'s own bar) had
one existed. It is **not**, however, comfortably powered to resolve an
effect at the scale of the null's own draw-to-draw noise (~0.003) — a
caveat honestly carried into Section 6's per-world reading, where one
world's miss is a genuine knife-edge rather than a clean rejection.

**Disclosed random-matrix-null companion (E2's own construction,
reused verbatim, never the decider):** q95 = 0.4599 (harmless) / 0.4592
(deployed) — **substantially above** the repetition-shuffled null's own
q95 (0.3313 / 0.3821). This is an empirical confirmation, on this leg's own
data, of exactly the divergence M4-E2's disclosure (and this leg's own
registration, citing it) warned about: two
independent random (48,13) Gaussian matrices are *more* dissimilar in this
nuclear-norm-cosine statistic than two real, already-structured S4 vectors
randomly re-paired — using the random-matrix null as the decider would have
been the wrong, non-apples-to-apples comparison the registration explicitly
ruled out.

## 4. G2 NULL LIVENESS — the null must actually move

| arm | n draws | min | q05 | median | q95 | max | std | range |
|---|---|---|---|---|---|---|---|---|
| `deployed` | 200 | 0.3709 | 0.3740 | 0.3779 | 0.3821 | 0.3859 | 0.00258 | 0.01505 |
| `basis_shrinkage_1.00` | 200 | 0.3188 | 0.3217 | 0.3260 | 0.3313 | 0.3334 | 0.00281 | 0.01467 |

Both arms' null distributions are genuine, non-degenerate, sub-maximal
distributions — std bounded well away from 0, range ≈0.015, comfortably
below the trivial self-identical ceiling of 1.0 (median 0.326–0.378, not
≈1.0). **Live for both arms** (`gates.json → G2_null_liveness.all_live =
true`). This is a real, moving null, not a frozen one.

## 5. G1 ANCHOR, G3, G4

### G1 ANCHOR — exact to ≤1e-12 (world level) / ≤1e-9 (per-repetition delta)

| chain | comparator | max abs diff | pass |
|---|---|---|---|
| `deployed` shares (registered+reverse+standalone+family) | M4-E2 `decision.json['offset_table']` | **0.0** | yes |
| `basis_shrinkage_1.00` displacement (24 rows) | M4-H4 `disp_rows.csv` | **0.0** | yes |
| **registered-literal, combined** | | **0.0** | **yes** |
| disclosed superset: `basis_shrinkage_1.00` shares vs. H4's `offset_shares_by_arm.csv` | H4 | 9.02e-17 | yes |
| disclosed superset: `deployed` displacement vs. H3's AND H4's `disp_rows.csv` | H3/H4 | 0.0 | yes |
| **NEW: per-repetition delta vs. already-anchored `disp_v2`** (48 checks) | this leg's own `disp_rows.csv`, same assemble pass | 7.11e-15 (tol 1e-9) | yes |
| **NEW: rotation-extraction gate** (48 checks, vs. `leg14._align`) | — | 0.0 (tol 1e-12) | yes |
| **NEW: norm-preservation gate** (48 checks) | — | 1.07e-14 (tol 1e-12) | yes |

World-level shares/offsets match H5's own persisted numbers bit-for-bit
(e.g. `basis_shrinkage_1.00` on `endogenous_creation_expansion`:
`offset_norm=7.914436`, `S4_residual=0.514003`, identical to H5's own
`offset_shares_by_arm.csv` to full float precision) — confirmed by direct
CSV comparison, not merely the gate boolean. The per-repetition
construction — genuinely new to this leg, since no predecessor computed
this — is tied to already-anchored `disp_v2` values (tolerance 1e-9,
E2's own tolerance for two independently-ordered computations of a
symmetric Procrustes distance) and to `leg14._align` itself (tolerance
1e-12, a pure floating-point identity, the same SVD evaluated twice). All
three anchor families pass. `gates.json → G1_anchor.pass = true`.

### G3 — world-build faithfulness (scope-reduced; gates no lean)

`h5._g3_spot_check_h5`, reused unchanged, filtered to this leg's 2 arms: 6
checks (3 worlds × 2 arms), **max_abs_diff = 0.0**. Passes. Re-certifies the
shared context-build machinery this leg still depends on; adjudicates
nothing (Section 1, scope decision 2).

### G4 MATERIALITY FORM

G0: MDE from the null's own pair-level std, no borrowed arbitrary
percentage bar — context given against the null's own q95, the 1.0
ceiling, and lean (c)'s own registered 0.5 bar. G1: degenerate
exact-equality against independently-persisted comparators plus the new
internal-consistency check described above. G2: the null's own spread
(std, range) reported and confirmed non-degenerate and sub-ceiling — not a
nil-significance test. G3: degenerate exact-equality, faithfulness only,
non-gating. Lean (a): per-world CI-vs-null-q95 equivalence test
(`ci_lo > null_q95`), aggregated to a ≥2-of-3-worlds count. Lean (b): the
identical CI-based logic applied on the other side (`ci_hi ≤ null_q95`),
per the registration's own control framing — not a bare point-estimate
read (though that reading is disclosed alongside and agrees). Lean (c):
per-world absolute threshold classification (≥0.5), applied only where
lean (a) already qualified. No gate is a nil-significance test on a
known-nonzero quantity.

## 6. Within-world and across-world agreement, against the null's q95

### Within-world (lean a), evaluated at the HARMLESS winner; `deployed` disclosed

| arm | world | n pairs | mean | CI | null q95 | CI excludes q95 (held)? | gap (CI-lo − q95) |
|---|---|---|---|---|---|---|---|
| `basis_shrinkage_1.00` | endogenous_creation_expansion | 28 | 0.3360 | [0.3232, 0.3489] | 0.3313 | **no** | −0.0081 |
| `basis_shrinkage_1.00` | selection_creation_compensation | 28 | 0.3183 | [0.3053, 0.3313] | 0.3313 | **no** | −0.0260 |
| `basis_shrinkage_1.00` | source_rotated_feedback | 28 | 0.3447 | [0.3304, 0.3590] | 0.3313 | **no** | **−0.0009** |
| `deployed` (disclosed) | endogenous_creation_expansion | 28 | 0.3864 | [0.3769, 0.3958] | 0.3821 | no | −0.0052 |
| `deployed` (disclosed) | selection_creation_compensation | 28 | 0.3782 | [0.3665, 0.3900] | 0.3821 | no | −0.0156 |
| `deployed` (disclosed) | source_rotated_feedback | 28 | 0.3902 | [0.3806, 0.3997] | 0.3821 | no | −0.0015 |

**0 of 3 worlds HELD at the harmless winner** (registered bar: ≥2 of 3).
Half-widths (0.0129–0.0143) are of the same order as the gaps themselves —
the CI-based test is unambiguous in all 3 worlds, but `source_rotated_
feedback` is a genuine near-miss: its CI lower bound sits only **0.0009**
below the null's q95, the closest of all 6 (arm, world) comparisons by
nearly an order of magnitude (next closest: `deployed`/`source_rotated_
feedback` at 0.0015 — the **same world**, at **both** arms). At the raw
point-estimate level (not the registered CI-based test), 2 of 3 worlds at
the harmless winner sit marginally *above* q95 (`endogenous_creation_
expansion` +0.0047, `source_rotated_feedback` +0.0134) while
`selection_creation_compensation` sits *below* it even at the point
estimate (−0.0130) — no consistent direction across worlds, which is itself
informative: the near-miss in `source_rotated_feedback` is not backed up by
a second corroborating world.

Worth naming directly: `source_rotated_feedback` is the same world M4-H3
found "totally non-responsive" to the shrinkage lever at every rung up to
0.50, which M4-H4 then resolved as a strength effect rather than a
structural immunity. Here it is again the outlier — the single world
closest to showing within-world reproducibility, at both arms — without
crossing the registered bar. A fourth appearance of this world's
idiosyncrasy in this line, disclosed rather than smoothed over, and not
adjudicated as anything beyond what the numbers show.

### Across-world (lean b, the control), evaluated at the HARMLESS winner; `deployed` disclosed

| arm | grouping | n pairs | mean | CI | null q95 | CI ≤ q95 (held)? |
|---|---|---|---|---|---|---|
| `basis_shrinkage_1.00` | endogenous⟷selection | 64 | 0.3215 | [0.3113, 0.3317] | 0.3313 | borderline (ci_hi 0.0004 above) |
| `basis_shrinkage_1.00` | endogenous⟷source_rotated | 64 | 0.3256 | [0.3179, 0.3333] | 0.3313 | borderline (ci_hi 0.0020 above) |
| `basis_shrinkage_1.00` | selection⟷source_rotated | 64 | 0.3224 | [0.3133, 0.3315] | 0.3313 | borderline (ci_hi 0.0003 above) |
| `basis_shrinkage_1.00` | **POOLED (n=192)** | 192 | **0.3232** | **[0.3180, 0.3283]** | 0.3313 | **yes** |
| `deployed` (disclosed) | **POOLED (n=192)** | 192 | 0.3752 | [0.3711, 0.3792] | 0.3821 | yes |

The registration states lean (b) as a single "sits at or below" test — this
leg adjudicates on the **pooled** statistic (n=192), which HOLDS at the
harmless winner: CI entirely below q95 (`ci_hi=0.3283` vs. `q95=0.3313`),
a margin of 0.0030 — real, but modest (about 58% of the pooled CI's own
half-width of 0.0051, so this is a genuine but not overwhelming clearance,
disclosed honestly rather than inflated). The 3 individual world-pair CIs
each straddle q95 by a hair (their upper bounds sit 0.0003–0.0020 above it)
— reported for full transparency, but this is exactly the behavior expected
of 3 correlated sub-samples of the same pooled population sitting near a
shared boundary, not a disagreement with the pooled reading; the
point-estimate reading agrees exactly (`readings_agree = true`, pooled mean
0.3232 vs. q95 0.3313). **Lean (b) HOLDS, but by a real-not-large margin**:
across-world agreement sits at/below the null, confirming M4-E2's own
world-specificity finding — the control behaves as the registration
predicted, so lean (a)'s own miss is not an artifact of the measurement
accidentally picking up shared, non-world-specific structure. The modest
size of this margin, relative to the within-world gaps in Section 6 (which
run in the same 0.001–0.03 range around the very same null), is itself
worth naming: within-world and across-world agreement are not merely both
"at the null," they sit at *comparable* distances from it, in a design
whose own MDE is of similar magnitude — the honest reading is that this
leg resolves the qualitative question (no reproducible within-world
direction, and the control confirms the null is the right yardstick)
decisively, while the residual quantitative gaps on both sides are close to
this design's own resolution floor.

## 7. Per-repetition S4 share — a disclosed, expected contrast with H5's world-level table

| arm | world | mean per-rep S4 share | range |
|---|---|---|---|
| `deployed` | endogenous_creation_expansion | 0.7176 | [0.6817, 0.7631] |
| `deployed` | selection_creation_compensation | 0.7211 | [0.6727, 0.7797] |
| `deployed` | source_rotated_feedback | 0.7227 | [0.6650, 0.7750] |
| `basis_shrinkage_1.00` | endogenous_creation_expansion | 0.7885 | [0.7599, 0.8299] |
| `basis_shrinkage_1.00` | selection_creation_compensation | 0.7805 | [0.7275, 0.8284] |
| `basis_shrinkage_1.00` | source_rotated_feedback | 0.7737 | [0.7525, 0.7869] |

These are **not** the same quantity as H5's own world-level, GPA-consensus
S4 shares (0.40–0.45 at `deployed`, 0.51–0.52 at the harmless winner) — an
expected, disclosed contrast, not a discrepancy: a single repetition's own
raw v2-vs-swap displacement has not been denoised by GPA-averaging across 8
reps, so more of it falls outside what the (consensus-fit) S1/S2/S3 bases
explain. Full data: `per_rep_s4_share_rows.csv`.

## 8. Leans, pivot, verdict — adjudicated exactly as registered

**(a) REPRODUCIBLE WITHIN WORLD — MISSES.** 0 of 3 worlds clear the
registered bar (≥2 of 3) at the harmless winner. Decisive in 2 of 3 worlds
(`endogenous_creation_expansion`, `selection_creation_compensation`); a
genuine knife-edge in the third (`source_rotated_feedback`, CI lower bound
0.0009 below q95).

**(b) NOT ACROSS WORLDS — HOLDS**, the control behaves exactly as M4-E2's
world-specificity finding predicted: pooled across-world agreement (0.3232)
sits below the null's own q95 (0.3313), CI entirely below.

**(c) MATERIAL ENOUGH TO CAPTURE — not applicable** (no world qualified
under lean (a)).

**PIVOT FIRES.** Per the registration's own branch:

> **S4 IS REPETITION-SPECIFIC AND NOT ATTACKABLE BY ANY BASIS CONSTRUCTION.**

**Verdict: `PIVOT_S4_REPETITION_SPECIFIC_NOT_ATTACKABLE_BY_ANY_BASIS_
CONSTRUCTION`.**

### Read plainly, with the prominence a discovery deserves

Every repair this program has landed — the estimator's ridge shape and
strength, the basis whitening's shrinkage — worked because a named,
code-legible step existed in the discovery objective to vary. S3 had one:
three normalization/scale-mode families, enumerable from the code with
file:line references. **S4 never had one — it is defined purely by
exclusion, whatever S1+S2+S3 fails to explain — and this leg's finding is
that this is not an accident of description: S4's own direction does not
even agree with itself across 8 independent repetitions of the *same*
world, at a scale this design was well-powered to see if it were anywhere
near material.** The across-world control (lean b) rules out the one
alternative explanation that would have made lean (a)'s miss uninterpretable
— the measurement is not accidentally picking up something shared and
non-specific; it is correctly detecting that repetition-to-repetition
agreement, within a world, is statistically indistinguishable from
repetition-to-repetition agreement across *different* worlds. Both sit at
the same repetition-shuffled null. There is no world-level regularity for a
future basis to lock onto, because the direction itself does not survive
past a single repetition of the underlying synthetic process.

This closes the question M4-H5's planner note left open. Taken together
with the rest of the M4-H line: the safe lever (`basis_shrinkage_1.00`)
removes 45.79% of the displacement without harming truth-referenced
recovery (M4-H4); what survives is dominated by S4 (M4-H5); and S4 itself
is now shown to be irreducible at the level of subspace-targeted repair —
not because no one has yet found the right basis for it, but because
its own direction is not a reproducible property of the world it comes
from. **~46% is the M4-H basis line's definitive ceiling for objective-side
repair at this level.**

## 9. Mechanical notes

**No mechanical problems.** A synthetic unit test of the new per-repetition
delta construction (random matrices, no real data) was written and run
*before* any real compute — it directly verified the symmetric-alignment
identity (native norm exactly reproduces the quotient distance), the
rotation-extraction gate (exactly 0.0), the norm-preservation gate
(1.4e-14), the commutation identity `align(B@R,A@R) = align(B,A)@R`
(5.8e-15), and the gauge-invariance/equivariance contrast that motivates
the whole construction (a toy gauge-invariant basis gave identical shares
on native vs. gauge-aligned delta; a toy gauge-equivariant basis gave
different ones, as it must). The subsequent `--smoke` run on real data
reproduced the same pattern immediately (native norm vs. disp_v2 anchor:
3.6e-15 and 0.0 on the two arms tested). The full run — G3 stage on all 3
worlds, arm stage on all 3 worlds × 2 arms, and `--assemble` — completed
clean on the first attempt, entirely foreground with explicit per-call
timeouts (no background jobs, no monitors), total compute wall-clock under
3 minutes. Data-integrity check before any hypothesis-relevant number was
read: `disp_rows` 48 rows (2×3×8, exact), `g3check_rows`/`offset_shares_
by_arm` 6 rows each (2×3, exact), `per_rep_s4_share_rows`/`per_rep_delta_
construction_checks` 48 rows each (2×3×8, exact), `within_world_pair_rows`
168 rows (2×3×28, exact), `across_world_pair_rows` 384 rows (2×3×64,
exact), `null_draws` 400 rows (2×200, exact) — all as expected, all
checked before adjudication. `gates.json` was confirmed byte-for-byte
identical to `decision.json`'s own `gates` object.

Finite synthetic M4-C.2 worlds only (M4-E2/Leg14/H2/H3/H4/H5's own 3
`HIGH_GAP_WORLDS`); no natural-text, personality, or clinical claim; no
seal, no independent verification (operator directive 2026-08-01).

## 10. Hand-off

The M4-H basis line closes on this statement: the safe, mechanistically-
characterized lever this line built (M4-H2→H4) removes 45.79% of the
discovery objective's frame displacement without harming truth-referenced
recovery — a real, bounded, partial repair, the first this program has had.
What survives is dominated by a block (S4) that M4-H5 showed has no
operational construction of its own, and this leg shows, at a scale it was
well-powered to detect had it been material, that the block's own direction
is **repetition-specific, not a reproducible property of its world** — the
across-world control confirms the measurement itself is behaving correctly
rather than merely being uninterpretable. Converting the open problem M4-H5
left ("can S4 be given a construction at all?") into a measured limit
("no — not because the construction hasn't been found yet, but because the
object itself does not reproduce") is this leg's result, and per the
registration's own instruction it is reported with that prominence: **~46% is
the M4-H line's definitive ceiling for subspace-targeted, objective-side
repair.** Any future attempt to close more of the displacement than that
would need to look past the discovery objective's own S1–S4 decomposition
entirely — a different kind of intervention than anything this line's
thirteen legs (M4-G1 through M4-G7, M4-H1 through M4-H6) have tried.
