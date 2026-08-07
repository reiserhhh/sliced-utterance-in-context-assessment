# SUICA M4-F5 -- Is The Certificate Valid? (Gauge Validity Audit of the Split-Half Agreement Statistic)

> **BANNER: synthetic worlds calibrated to an opened-panel regime, exploratory.**
> This leg consumes NO new real-text evidence. It reuses M4-F4's exact swept
> cells (identical world seeds, identical gauge/D0/halving) and adds a
> truth-referenced recovery readout computed by the IDENTICAL deployed
> featurize -> project -> field path applied to noise-free author
> representations. No label columns anywhere; no claim about the real
> relation field's content, personality, emotion, diagnosis, or any
> individual.

Registered spec: `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md`
sections "M4-F4 planner adjudication note" (source of the registered
secondary offset-corrected refit) and "M4-F5 registration (2026-08-03,
BEFORE run) -- is the certificate valid?" (loop cycle 14+, panel design laws
line, leg 5). Script: `scripts/run_suica_m4_f5_gauge_validity.py`.
Artifacts: `results/m4_f5_gauge_validity/`.

## Part 0 -- REGISTERED ADJUDICATIONS AND OPERATIONALIZATIONS (written before the run)

The registration fixes the reused cell design (M4-F4's exact swept cells),
the truth-referenced recovery functional (the field-agreement functional
between the finite-panel estimated field and the world's true field), the
requirement for at least two truth variants with disclosed sensitivity, the
three leans, the pivot, and four gates (G1-G4). It leaves the truth-path
operationalization itself as the leg's main researcher degree of freedom,
per the task's own framing. Every implementation choice is fixed here,
BEFORE any compute, transcribed from the script's own docstrings/comments.

### 0.1 Reuse boundary (what is imported/called unchanged vs. newly written)

Directly imported/called, never reimplemented: `f1().load_spec`,
`f1()._directions`, `f1().e1()`, `f1().build_layout`, `f1().featurize_panel`,
`f1().half_indices`, `f1().knob_tag`, `f1().fit_axis`, `f1().bootstrap_axis`
(secondary check only), `f1()._log_odds` (from
`scripts/run_suica_m4_f1_panel_sizing.py`); `f2().occasion_labels`,
`f2().shock_vector`, `f2().generate_world_composed`, `f2().run_gate_g1`
(from `scripts/run_suica_m4_f2_composition.py`); `f3().world_seed_for`,
`f3().run_gate_g3` (from `scripts/run_suica_m4_f3_composition_scaling.py`);
`f4().build_live_tasks`, `f4().build_holdout_task`, `f4().cell_name_live`,
`f4().cell_name_null`, `f4().seed_suffix_for_mult`, `f4().AUTHOR_MULTS`,
`f4().KAPPAS`, `f4().HOLDOUT_AUTHOR_MULT`, `f4().DESIGN` (from
`scripts/run_suica_m4_f4_author_axis.py`) -- guaranteeing byte-identical
task construction (`seed_key` strings above all) to what produced M4-F4's
own persisted `cells.csv`/`null_cells.csv`/`prediction.json`.

`f3().run_sweep_world` itself is deliberately **not** called directly, even
though it is the function that produced M4-F4's own numbers, because it
does not expose the intermediate `vectors_list`/`calibration`/retained-set/
`weights` this leg's truth computation needs -- those are local variables
inside it, not return values. `run_truth_sweep_world` (new in this script)
is a disclosed structural near-duplicate of it (the SAME pattern M4-F4 itself
used for its own null-world engine, `run_null_sweep_world`, relative to
`f3().run_sweep_world`): every downstream primitive it calls
(`f1().build_layout`, `f2().generate_world_composed`, `f1().featurize_panel`,
`module.calibrate_d0_soft`, `module.resolved_contexts`, `f1().half_indices`,
`module.project_soft`, `module.deployed_soft_field`, `module.field_agreement`)
is the identical unchanged function `f3().run_sweep_world` itself calls, in
the same order, with the same seed derivation (`f3().world_seed_for` on
`f4()`'s own `seed_key` strings, the same `corpus = f"m4f3-{seed_key}-w{world}"`
convention) -- so the split-half agreement this function produces reproduces
M4-F4's own persisted value as a **verified byproduct**, not a re-derivation
on a different code path. This is exactly what gate G2 checks.

Newly written, because no prior leg has it: `run_truth_sweep_world` (above);
`generate_truth_vectors_exact` / `generate_truth_vectors_long` (the two
registered truth-path variants, Part 0.3 below); `field_from_vectors` (the
shared featurize -> project -> field helper, applied identically to the
finite sample and to both truth variants -- the registration's own
"IDENTICAL deployed path... differing ONLY in the input" requirement); the
adjudication code (leans a/b/c, the pivot, the two-variant combination
rule, Part 0.7); the registered secondary offset-corrected refit.

### 0.2 Cell scope: EXACTLY M4-F4's own persisted cells

Authors x{1,2,4,8,16} at kappa in {0.5,1.0} (10 cells) plus the authors x32
holdout at kappa=1.0 only (1 cell -- matching M4-F4's own holdout, which was
never run at kappa=0.5) = **11 cells total**, identical world seeds
(`f3().world_seed_for` on `f4()`'s own `seed_key` strings), identical knobs
(read verbatim from `results/m4_f1_panel_sizing/calibration_record.json`,
`k48-r0.50-mu0.15-x0.15-e0.70-p0.20_0.80`, no new calibration search).

### 0.3 THE TRUTH PATH -- two registered variants, written BEFORE compute

Both variants are noise-free, and both are computed via `field_from_vectors`
-- the SAME `featurize_panel -> project_soft(calibration) -> deployed_soft_field`
chain the finite-sample ESTIMATE field uses (Part 0.4 below). This is the
registration's own explicit requirement ("the identical deployed path...
differing ONLY in the input being noise-free").

**Variant A (analytic, exact-T).** A bit-identical replay of
`f2().generate_world_composed`'s own kappa>0 draw sequence (fresh
`rng=np.random.default_rng(world_seed)`; `loadings`, `z`, `zeta`, `phi`, the
`t_max`-step AR(1) `x` -- IDENTICAL to the live world's own values by
construction -- and a stream-order-preserving but UNUSED noise draw) with
the SAME `f2().shock_vector` calls and the SAME kappa blend, producing
`mean_part` and `state_part` bit-identical to the live world's own values.
Differs from the live event stream ONLY in that the idiosyncratic per-event
Gaussian noise term (`sqrt(w_e)*sigma_iso*noise`) is never added. This
answers: *"what would this exact author, in this exact world realization,
have produced with zero per-event measurement-type noise?"*

**Variant B (large-sample asymptotic).** The SAME author-level invariants
(`loadings`/`z`/`zeta`/`phi`/`mean_part`, replayed bit-identically to
Variant A/live), but the STATE process is resampled over `T_LARGE` synthetic
occasions per RETAINED author instead of the observed finite T (observed
range: 8-16 events/author, mean 13.4). The shared context-occasion shock
reuses the UNCHANGED `f2().shock_vector` for occasion indices
`0..T_LARGE-1` -- the SAME deterministic per-(context,occasion) function the
live world uses, so Variant B stays grounded in the SAME world's actual
realized context-level process, merely sampled far longer, not a fresh
alternate world. The author-private AR(1) state is redrawn over `T_LARGE`
steps using a freshly, deterministically-seeded stream (salt
`"m4f5-truth-long"`, keyed off `world_seed` and the chunk start) with the
SAME per-author `phi` -- statistically valid because `x_i,t` is
already-stationary from t=0 (`x_i,0 ~ N(0,1)` unconditionally), so a fresh
long realization characterizes the same population moments a literal
continuation would, without the added complexity of threading the live
world's own short path forward. Also noise-free, matching Variant A.
Processed in author-index chunks (`TRUTH_CHUNK_SIZE`) to bound peak memory
at the largest (x32, ~18,080 retained authors) cell -- correctness is
chunk-boundary-independent because every per-author quantity is independent
across authors.

**T_LARGE and chunk-size revision, disclosed (a pre-compute engineering
change, not a result-dependent one).** A pilot measurement on the x32
holdout cell (world 0, before any of the 11 registered cells were computed)
at the originally-planned `T_LARGE_PRIMARY=150`/`TRUTH_CHUNK_SIZE=1500`
measured 6.5GB peak RSS for a single world -- unsafe at 8-way parallelism on
this 24GB machine (would risk ~50GB+ peak). Both constants were revised
DOWNWARD before any registered cell was computed: **`T_LARGE_PRIMARY=80`**
(~5-10x the observed per-author range) and **`TRUTH_CHUNK_SIZE=1000`**,
which reduced peak RSS to 4.0GB/world on the same pilot cell. No
agreement/truth number had been observed at the time of this revision; it
is an engineering safety change, not a result-dependent one, and is
disclosed here rather than silently folded into the constant.

Both variants answer a DIFFERENT question (A: "this realization, no
measurement noise"; B: "this world's long-run/population signature") --
reporting both, and their gap, is the registered sensitivity requirement. A
further sensitivity check (`T_LARGE_SENSITIVITY=320`, 4x the primary) is run
on 2 representative cells (`base1x_shared_k10` [mult=1] and
`authors_x32_holdout_shared_k10` [mult=32], the smallest and largest swept
points) to confirm Variant B is not materially sensitive to the specific
`T_LARGE` choice -- reported in Part 1 below.

### 0.4 The finite-sample ESTIMATE field

`field_from_vectors` applied to the actual retained authors' own FULL
(unsplit) observed event vectors -- i.e. the field a practitioner would get
from using ALL of the available (noisy, finite) evidence for each retained
author, not an artificially-halved subset. This is DIFFERENT from either
split-half field (each of which uses only a random 50% of an author's own
events) and is the natural "best estimate from the finite panel" the
registration's truth-recovery functional compares against.

### 0.5 G4 truth-path invariance, operationalized as two checks

(i) `field_from_vectors` fed the SAME finite retained vectors via a FRESH
`featurize_panel` call, compared EXACTLY (max abs diff over every context's
matrix) against the SAME quantity computed via projecting the
ALREADY-computed full-population `raw_m`/`raw_k` (masked to retained
authors) through the SAME calibration -- two independent code routes to the
identical mathematical object, checked on EVERY world of every cell (not
merely "a degenerate case", though one is highlighted in Part 1 per the
registration's own phrasing -- computing it everywhere is strictly stronger
than the minimum required and costs no extra `featurize_panel` calls, since
route (ii) only masks already-computed arrays). (ii) By construction,
Variant A/B and the estimate all go through the literal SAME
`field_from_vectors` function -- the "truth path" and "estimate path" are,
code-wise, the identical function; the only difference is which
`vectors_list` is passed in.

### 0.6 Lean/pivot kappa scope: POOLED across both kappas (unlike M4-F4)

UNLIKE M4-F4 (whose leans were kappa=1.0-primary / kappa=0.5-context), this
leg's registered leans (a) and (b) explicitly say "every swept cell" /
"pooled" with no kappa restriction, and lean (c) is explicitly a
kappa=0.5-vs-kappa=1.0 comparison. So (a)/(b) pool ALL 11 cells (both
kappas) and (c) compares across kappas by construction. This reading is not
ambiguous (unlike the M4-F4 G0 aggregation gap); it follows directly from
the registered text, which is why it is recorded here as a plain
operationalization rather than a disclosed post-hoc resolution.

### 0.7 Two-variant combination rule (this leg's own operationalization, registered before compute)

The registered text does not specify how to combine Variant A and Variant B
into one leg-level verdict. Disclosed here, BEFORE compute: each lean is
evaluated SEPARATELY under each variant; **a lean is adjudicated HOLD only
if BOTH variants HOLD** (conservative AND), so a favorable variant cannot be
selected after the fact to rescue a lean the other variant would MISS.
**The PIVOT fires if EITHER variant triggers either registered pivot
condition** (conservative OR), for the same reason in the opposite
direction -- a pivot-triggering result under either operationalization of
"truth" is enough to withdraw the certificate, since the entire point of
running two variants is not to be able to explain one away by picking the
other.

### 0.8 Lean (b) "interpolated on the measured curve" operationalization

An ordinary-least-squares LINEAR fit of truth_recovery on agreement (both in
raw, not log-odds, space -- both are already bounded similarity-type scores,
so no transform is registered) over the kappa=1.0 points (mult
1,2,4,8,16,32 -- six points, the widest available range), evaluated at
agreement=0.5. Since the maximum MEASURED kappa=1.0 agreement in this entire
sweep is 0.386 (the x32 holdout -- M4-F4's own fitted .5-agreement budget of
46.11x lies OUTSIDE every measured cell), evaluating at 0.5 is necessarily
an EXTRAPOLATION beyond the measured range; this is disclosed plainly
wherever the number is reported, per the registration's own anticipation of
this outcome ("extrapolated with the status stated plainly if .5 is not
reached in range").

### 0.9 Lean (c) "at equal agreement" operationalization

kappa=0.5's own 5 measured agreement values (mult 1,2,4,8,16) fall entirely
inside kappa=1.0's wider measured range (max 0.386 at x32), so kappa=1.0's
truth-recovery-vs-agreement curve is INTERPOLATED (linear, same transform as
0.8) at each of kappa=0.5's 5 own agreement values, and compared directly to
kappa=0.5's own measured truth recovery at that (mult, kappa=0.5) cell.
Lean (c) HOLDs only if EVERY one of the 5 matched-agreement absolute
differences is <=.1 (the strict every-point reading, consistent with this
line's own established convention for this style of rule, e.g. M4-F4's own
monotone-decline check).

### 0.10 Secondary check (not a lean) SE treatment

The per-cell G0 null offset is subtracted from the MEAN only
(`corrected_mean = live_mean - null_mean`); the corrected point's own
`agreement_se` is left UNCHANGED (the live cell's own SE) -- the literal
reading of "subtracting an offset" as a location-only adjustment. An
alternative (quadrature-combined SE, `sqrt(live_se^2+null_se^2)`, since live
and null are independent computations) is also computed and reported for
disclosed sensitivity; the primary (unchanged-SE) reading controls per this
register-note. No bootstrap CI is recomputed for the corrected fit (scope
discipline: the registration calls this "a secondary check, not a lean",
and asks only for "the corrected gamma and .5-agreement budget").

### 0.11a Process disclosure: what the pre-Part-0 pilot runs saw

Before this Part 0 text was finalized, two single-world ENGINEERING pilots
were run at reduced `draws=3` (not the registered `draws=20`): `base1x_shared_k10`
world 0, and `authors_x32_holdout_shared_k10` world 0 (the latter run twice,
before and after the T_LARGE/chunk-size revision in 0.3). Their purpose was
exclusively to validate (i) that `run_truth_sweep_world`'s split-half output
bit-reproduces M4-F4's own persisted per-draw values (it does, to the last
printed digit: `0.006507426753914965` vs `0.006507426753914966`), (ii) that
the G4 degenerate check lands at exact `0.0` (it did, both times), and (iii)
peak memory/wall-time, which drove the T_LARGE/chunk-size revision in 0.3.
These pilots incidentally printed illustrative truth-recovery values from 2
of the 11 registered cells (world 0 only, `draws=3`, not the registered
design): base1x_shared_k10 truth_exact~0.137, truth_long~0.002; the x32
holdout truth_exact~0.617, truth_long~0.10-0.15 (varying with the T_LARGE
revision). Disclosed here so a reader can judge for themselves: **no lean
threshold, no combination rule, and no extrapolation method was chosen or
adjusted because of these numbers.** Every numeric bar this leg's leans use
(Spearman>=.9, target>=.7, kappa-diff<=.1, the PIVOT's <.5 floor) is copied
VERBATIM from the registered text (reproduced in the Leans/PIVOT-IF
paragraphs above). The two genuinely-invented methodological choices (0.7's
AND/OR two-variant combination rule; 0.8/0.9's linear-fit interpolation
method) were fixed by structural reasoning about what the registered text
requires, decided and written into the script's docstrings before the
pilots were run, not revised afterward. The T_LARGE/chunk-size revision
itself was memory-driven (0.3), not accuracy- or result-driven. None of the
11 registered cells had its full 8-world x 20-draw design computed before
this Part 0 was written.

### 0.11 G4 tolerance

`<=1e-9`, not literal bit-identical `0.0`. This allows for floating-point
summation-order noise between differently-batched `featurize_panel` calls
processing the same underlying values (batch composition can affect BLAS
internal blocking, in principle, even though every per-author quantity is
mathematically independent of its batch-mates). Disclosed as a register-note
before compute; Part 1 reports whether the observed diffs in fact needed
this tolerance or landed at exact `0.0`.

---

*(Everything below this line was written after the run. Part 0 above was
not edited after compute began.)*

## Part 1 -- OUTCOME

**PIVOT FIRES. THE GAUGE IS NOT A VALID CERTIFICATE. Verdict:
`GAUGE_INVALID_CERTIFICATE_WITHDRAWN_46_1X_BUDGET_AND_26K_RECOMMENDATION_WITHDRAWN`.**
Split-half agreement correlates strongly with truth-referenced recovery in
rank terms (pooled Spearman 0.991 / 0.982 across both truth variants,
comfortably above the registered 0.9 bar), but the registration's OWN
zero-tolerance co-movement clause ("no cell pair where agreement rises and
truth recovery falls") is violated under BOTH truth variants, and under the
large-sample variant the extrapolated truth recovery at the .5-agreement
point (0.200) sits far below even the pivot's own 0.5 floor -- not a
marginal miss. Per the registration's own consequence, stated plainly:
**the .5 target, the 46.1x budget, and the ~26,052-author D3 recommendation
that M4-F4 produced are WITHDRAWN**, pending respecification of the
certification target against a truth-referenced criterion. Lean (c) (kappa
stability) HOLDs cleanly under both variants -- the agreement-to-truth
MAPPING'S magnitude is stable across kappa where matched -- but this does
not rescue leans (a) or (b), and does not gate the pivot.

Run: 11 cells (10 sweep cells, mult 1/2/4/8/16 x kappa 0.5/1.0, plus the
authors x32 holdout at kappa=1.0) in six foreground chunks (mults 1-8 both
kappas together: 8 cells in ~23 minutes at `--workers 8`; mult 16 both
kappas: ~7.6 minutes at `--workers 4`, reduced for memory; the x32 holdout:
~9.5 minutes at `--workers 3`, reduced further -- `n_authors_total` growing
from 985 at 1x to 31,520 at 32x, `n_retained` from 565 to 18,080); gates and
finalize each under a minute; the (non-gating) T_LARGE sensitivity check on
2 cells a separate, later chunk. Total main-pipeline compute ~40 minutes.
`MASTER_SEED=20260802` (M4-F1's/M4-F2's/M4-F3's/M4-F4's own), knobs read
verbatim from M4-F1's `calibration_record.json`
(`k=48, rho=.50, w_mu=.15, w_x=.15, w_e=.70, phi in [.20,.80]`) -- this leg
performs no new calibration search. A pre-compute memory-safety revision to
`T_LARGE_PRIMARY`/`TRUTH_CHUNK_SIZE` is disclosed in Part 0.3.

## Gates (all green)

- **G1** (kappa<=0 free cell reproduces M4-F1's persisted `base1x` to
  <=1e-12; direct call to `f2().run_gate_g1`, unchanged): abs diffs
  9.9e-17 (agreement_mean), 1.1e-16 (agreement_se), 0.0
  (d0_eff_rank_M_mean), 7.1e-15 (d0_eff_rank_K_mean), 0 (n_retained) --
  every diff at least 3 orders of magnitude inside the 1e-12 bar.
  **PASS.**
- **G2** (every one of M4-F4's own 11 persisted cells, freshly recomputed
  by `run_truth_sweep_world` on identical world seeds, reproduces
  `results/m4_f4_author_axis/cells.csv` to <=1e-12): max abs diff across
  all 11 cells x 5 checked fields (`agreement_mean`, `agreement_se`,
  `d0_eff_rank_M_mean`, `d0_eff_rank_K_mean`, `n_retained`) is **8.3e-17**
  -- floating-point noise, not a substantive mismatch; every one of M4-F4's
  own numbers is reproduced. **PASS.**
- **G3** (gauge invariance; direct call to `f3().run_gate_g3()`, which
  itself calls `f2().run_gate_g3()`): batched feature map vs. deployed
  `v8.build_feature_panel` bit-identical; halving vs.
  `e1().split_half_frames` identical. **PASS.**
- **G4** (truth-path invariance: the finite-sample field computed via a
  fresh `field_from_vectors` call on the retained-only subset agrees with
  the SAME field computed via the independent masked-full-population
  route): max diff across all 11 cells x 8 worlds = **exactly 0.0** (not
  merely inside the registered 1e-9 tolerance -- literal bit-identical
  equality on every one of 88 world-checks). Highlighted degenerate case
  (per the registration's own phrasing): `base1x_shared_k05`, `max_diff=0.0`.
  **PASS.**

`results/m4_f5_gauge_validity/gates.json` carries the full detail for all
four gates.

## The full agreement-vs-truth-recovery table (both variants, sorted by agreement -- co-movement made visible, not asserted)

| cell | kappa | author_mult | agreement | truth_recovery (Variant A: exact) | truth_recovery (Variant B: asymptotic, T=80) | n_retained |
|---|---|---|---|---|---|---|
| base1x_shared_k10 | 1.0 | 1 | 0.006117 | 0.149679 | 0.022525 | 565 |
| base1x_shared_k05 | 0.5 | 1 | 0.007953 | 0.177277 | 0.015325 **<- B DOWN** | 565 |
| authors_x2_shared_k05 | 0.5 | 2 | 0.009970 | 0.169715 **<- A DOWN** | 0.023041 | 1130 |
| authors_x4_shared_k05 | 0.5 | 4 | 0.022487 | 0.203598 | 0.028853 | 2260 |
| authors_x2_shared_k10 | 1.0 | 2 | 0.033189 | 0.210521 | 0.058047 | 1130 |
| authors_x8_shared_k05 | 0.5 | 8 | 0.042870 | 0.247954 | 0.038491 **<- B DOWN** | 4520 |
| authors_x4_shared_k10 | 1.0 | 4 | 0.058590 | 0.278867 | 0.064263 | 2260 |
| authors_x16_shared_k05 | 0.5 | 16 | 0.095219 | 0.323159 | 0.081307 | 9040 |
| authors_x8_shared_k10 | 1.0 | 8 | 0.132660 | 0.373184 | 0.088927 | 4520 |
| authors_x16_shared_k10 | 1.0 | 16 | 0.229053 | 0.500941 | 0.132169 | 9040 |
| authors_x32_holdout_shared_k10 | 1.0 | 32 | 0.386124 | 0.637054 | 0.150105 | 18080 |

Three DOWN-flags total across 10 consecutive-in-agreement steps x 2
variants (20 step-comparisons): 1 for Variant A (step 2->3, both kappa=0.5),
2 for Variant B (step 1->2, cross-kappa same mult; step 5->6, cross-kappa
different mult). **All three are entirely accounted for by mixing kappa=0.5
into the pooled, agreement-sorted ordering: restricted to kappa=1.0 ALONE
(the 6-point primary line: base1x through the x32 holdout), BOTH variants
are perfectly monotonic in agreement with zero violations.** This is
reported as informative context, not as a rescue -- the registration's lean
(a) text says "across every swept cell" / "pooled" with no kappa
restriction (Part 0.6), so the pooled violations are what the registered
rule is adjudicated on, and they stand.

**Statistical context for the three violations (supplementary, not a
registered test, reported exactly as M4-F4's own G0 addendum reported
supplementary context alongside its decisive reading).** Gap vs. combined
per-cell SE (`sqrt(se_lower^2+se_higher^2)`) at each violating step:
Variant A (base1x_k05 vs x2_k05): gap 0.00756 vs combined SE 0.01335
(0.57 SE). Variant B step 1 (base1x_k10 vs base1x_k05): gap 0.00720 vs
combined SE 0.00663 (1.09 SE). Variant B step 2 (x2_k10 vs x8_k05): gap
0.01956 vs combined SE 0.01629 (1.20 SE). All three sit under 1.2 SE --
plausible under sampling noise given only 8 worlds/cell, not dramatic
reversals. The registered rule carries no significance threshold (mirroring
this line's convention of unsoftened "any"/"every" rules, e.g. M4-F4's own
monotone-decline check), so this does not change the adjudicated verdict;
it is reported so a reader who would weigh a materiality threshold
differently can see every number needed to do so.

## Point fits and the extrapolation to agreement=0.5 (Part 0.8)

| variant | kappa=1.0 linear fit (truth = slope*agreement + intercept) | max measured agreement | truth recovery AT agreement=0.5 | status |
|---|---|---|---|---|
| A (exact) | slope=1.257, intercept=0.181 | 0.386 (x32 holdout) | **0.810** | EXTRAPOLATED (0.5 is 1.30x the max measured point) |
| B (asymptotic, T=80) | slope=0.317, intercept=0.041 | 0.386 (x32 holdout) | **0.200** | EXTRAPOLATED (same) |

The two variants disagree enormously on target adequacy -- Variant A's
extrapolation clears the registered 0.7 bar with room to spare; Variant B's
lands at 0.200, below even the PIVOT's own 0.5 floor, not merely below
lean (b)'s stricter 0.7 bar. This divergence is itself a central finding:
whether the .5-agreement point "corresponds to a field worth having"
depends enormously on which noise-free construction "truth" means, exactly
the sensitivity the registration anticipated when it required at least two
variants.

## Lean (c): kappa-matched truth recovery (Part 0.9)

kappa=0.5's own 5 measured agreement values, with kappa=1.0's
truth-recovery-vs-agreement curve (the SAME linear fit used above)
interpolated at each (no extrapolation needed -- all 5 fall inside
kappa=1.0's measured range):

| variant | max |abs diff| across the 5 matched points | HOLD (<=.1 at every point)? |
|---|---|---|
| A (exact) | 0.0240 (at authors_x2_shared_k05) | **Yes** |
| B (asymptotic) | 0.0285 (at base1x_shared_k05) | **Yes** |

Both variants HOLD lean (c) with comfortable margin (max gap ~0.024-0.029,
well under the 0.1 bar) -- the agreement-to-truth mapping's MAGNITUDE is a
stable property of the gauge across kappa, even though (per the table
above) its exact rank-ordering is not perfectly preserved once kappa=0.5 is
pooled in.

## Lean adjudication (Part 0.7's two-variant AND-combination rule)

- **Lean (a) MISS.** Rule: Spearman>=.9 pooled AND no agreement-up/
  truth-down cell pair. Variant A: rho=0.991 (passes) but 1 violation
  (fails) -> MISS. Variant B: rho=0.982 (passes) but 2 violations (fails)
  -> MISS. Combined (AND): **MISS**.
- **Lean (b) MISS.** Rule: truth recovery >=.7 at the .5-agreement point.
  Variant A: 0.810, HOLD. Variant B: 0.200, MISS. Combined (AND, since one
  variant MISSes): **MISS**.
- **Lean (c) HOLD.** Rule: |truth(k05) - truth(k10 interpolated)| <=.1 at
  every one of kappa=0.5's own 5 agreement values. Variant A: max 0.024,
  HOLD. Variant B: max 0.029, HOLD. Combined (AND): **HOLD**.

## Pivot adjudication

**PIVOT FIRES**, overdetermined by two independent registered clauses:

1. **Co-movement violation** (both variants): agreement rose while truth
   recovery fell for at least one cell pair, under BOTH Variant A (1
   violation) and Variant B (2 violations). Per Part 0.7's registered OR
   rule, either alone is sufficient.
2. **Target adequacy below .5** (Variant B only): truth recovery at the
   .5-agreement point is 0.200, decisively below the pivot's own 0.5 floor
   -- not a marginal miss (Variant A's own 0.810 sits at the opposite
   extreme, underscoring how variant-dependent this reading is).

Registered consequence, stated exactly as pre-committed: **the .5
agreement target, the 46.1x author-multiple budget, and the
~26,052-author D3 panel recommendation that M4-F4 produced are ALL
WITHDRAWN**, pending respecification of the certification target against a
truth-referenced criterion -- which becomes the registered next question
for this line.

## Registered secondary check: offset-corrected refit of M4-F4's author-axis law (not a lean)

| kappa | reading | n qualifying | gamma | .5-agreement budget (mult) | vs. M4-F4's original 46.11x |
|---|---|---|---|---|---|
| 1.0 (primary) | SE unchanged (adopted) | 4 of 5 | 1.1192 | **44.77x** | 0.971x (3% LOWER) |
| 1.0 (primary) | SE quadrature (disclosed alternative) | 4 of 5 | 1.1101 | 45.32x | 0.983x (2% LOWER) |
| 0.5 (context) | SE unchanged | 4 of 5 | 1.1906 | 113.40x | -- (kappa=0.5 was never the primary line) |

**The letter of the registered check passes (corrected budget 44.77x does
not exceed 46.1x, let alone by a factor of 2) -- but the MECHANISM the
planner note pre-recorded is not what produced this number, and that
discrepancy is disclosed plainly rather than smoothed over.** The planner
note's mechanism: "an offset lifts the small-n points, flattens the
log-log slope, and therefore biases gamma DOWNWARD and the budget UPWARD."
What actually happened: subtracting the null offset from `author_mult=1`'s
mean (0.006117 -> 0.003326) does not merely "lift" that point -- because
its `agreement_se` is held unchanged (Part 0.10) while its mean drops, the
corrected point now FAILS `fit_axis`'s own qualifying bar
(`mean - 2*se > 0`; corrected: `0.003326 - 2(0.001743) = -0.00016 < 0`) and
is DROPPED from the fit entirely (`n_qualifying` falls from 5 to 4, at
BOTH SE readings). The resulting 4-point fit's gamma (1.1192) is
marginally HIGHER than the original 5-point fit's gamma (1.0959) --
opposite in direction to "biases gamma downward" -- and the lower budget
follows from that, not from a flattened slope. In short: the corrected
budget number satisfies the planner's pre-recorded expectation
(<=46.1x), but for a DIFFERENT reason (a point exiting the fit's
qualifying set, not a lift-and-flatten of a fully-retained 5-point fit).
No bootstrap CI was recomputed for the corrected fit (Part 0.10: scope
discipline, this is a secondary check, not a lean).

## T_LARGE sensitivity check (Part 0.3, non-gating)

Quadrupling `T_LARGE` (80 -> 320) on the two representative cells (smallest
and largest swept points, kappa=1.0):

| cell | Variant B @ T=80 | Variant B @ T=320 | mean |diff| (8 worlds) | max |diff| (8 worlds) |
|---|---|---|---|---|
| `base1x_shared_k10` (mult=1) | 0.022525 | 0.005485 | 0.027767 | 0.058829 |
| `authors_x32_holdout_shared_k10` (mult=32) | 0.150105 | 0.143463 | 0.029445 | 0.066702 |

(T=80 column cross-checked against the main sweep's own `truth_recovery_long_mean`
for these two cells in `cells.csv` -- `0.150105` and `0.022525` respectively,
matching to every reported digit, since both computations call
`generate_truth_vectors_long` with the identical `t_large=T_LARGE_PRIMARY` on
identical world seeds.)

**Reading this correctly: Variant B is STABLE, not under-converged.**
Quadrupling T does NOT move the x32 cell's truth recovery toward Variant A's
0.637 -- it moves slightly DOWN (0.150 -> 0.143). At the base1x cell it also
moves down, more substantially (0.023 -> 0.005). **The ~4x gap between
Variant A and Variant B is therefore a real property of what the two
constructions target, not a finite-`T_LARGE` convergence artifact** -- this
leg does NOT get to explain away Variant B's low target-adequacy reading (or
the pivot's second firing clause, below) by claiming `T_LARGE_PRIMARY=80` was
simply too small. If anything, more data pushes Variant B's own recovery
value further from Variant A's, not closer.

## On the co-movement violations: statistical context does not change the verdict, but is reported plainly

The Variant A co-movement violation (`base1x_shared_k05` -> `authors_x2_shared_k05`,
Part 1's table above) fired on agreement rising `0.00795 -> 0.00997` while
truth recovery fell `0.17728 -> 0.16972`. The two truth-recovery SEs at that
step are **0.0104 and 0.0084** -- the drop (0.00756) is well inside their
combined uncertainty (0.57 combined-SE, computed above), i.e. **this clause
fired mechanically on a difference that is not statistically distinguishable
from zero.** Said plainly, without softening the adjudicated verdict: the
registered rule carries no significance threshold (Part 0's own discipline,
matching this line's convention elsewhere), so the MISS stands as computed
-- but a reader should know this specific instance of the co-movement clause
is a weak trigger, not a dramatic reversal.

**This does not matter to the overall outcome, because the pivot does not
depend on it.** The pivot's third firing clause -- Variant B's extrapolated
truth recovery at the .5-agreement point, 0.200, against the 0.5 floor -- is
a gap of 0.300, roughly an order of magnitude larger than any SE anywhere in
this dataset, and the T_LARGE sensitivity check above independently confirms
it is not a convergence artifact. **Clause 3 fires on a large, stable
margin and is sufficient on its own to withdraw the certificate**, with or
without the weaker co-movement clause. The two Variant-B co-movement
violations (Part 1's table) are themselves somewhat firmer (1.09 and 1.20
combined-SE) than the Variant-A one, but the adjudicated verdict does not
lean on any of the three co-movement instances being individually decisive
-- it is the target-adequacy clause, on the large-sample variant, that
carries the finding.

## Interpretation: what do the two truth variants appear to target? (clearly separated from the adjudication above -- this is a reading, not a registered claim)

At kappa=1.0, the three quantities grow at very different RATES across the
authors x1->x32 sweep:

| quantity | x1 (base1x) | x32 (holdout) | growth factor |
|---|---|---|---|
| agreement (split-half) | 0.0061 | 0.3861 | **63x** |
| Variant A (exact) truth recovery | 0.1497 | 0.6371 | **4.3x** |
| Variant B (asymptotic) truth recovery | 0.0225 | 0.1501 | **6.7x, plateauing** (T=320 gives 0.143, not higher) |

Agreement (a within-realization reproducibility statistic, comparing two
random halves of the SAME short occasion sequence) grows by far the most.
Variant A -- "this exact realization, noise removed, same finite T" -- is
recovered reasonably well and grows only modestly (the panel already
captures most of the recoverable structure even at x1). Variant B -- an
occasion-universe-averaged, more trait-like characterization of the SAME
author/context, deliberately averaging the AR(1) state process toward its
stationary (zero-mean) long-run behavior -- is recovered far more weakly at
every scale and, per the sensitivity check above, does not improve with a
larger truth-side sample. The pattern reads as consistent with: **the finite
panel and its split-half agreement statistic are well-suited to certifying
an occasion-bound, state-inclusive configuration, but poorly suited to
certifying a longer-horizon, more trait-like target** -- exactly the
distinction `docs/SUICA_FOUNDATION_GAP_LEDGER.md`'s **F10** ("State/trait
distinction... State/trait depends on occasion universe and horizon, not
feature appearance... No trait claim from same-session split-half
stability") already flags as a general, program-wide open point. This leg
does not test F10 directly and makes no F10 claim -- it is offered here only
as a plausible READING of why Variant B behaves as it does, not as an
additional registered finding.

## Honest anomalies and disclosures

1. **A pre-compute memory-safety revision to T_LARGE_PRIMARY/
   TRUTH_CHUNK_SIZE** (150->80, 1500->1000) was made after a pilot on the
   x32 cell measured 6.5GB peak RSS/world at the original values -- unsafe
   at 8-way parallelism on this 24GB machine. No agreement/truth number had
   been observed at the time; disclosed in full in Part 0.3.
2. **Two single-world engineering pilots ran before Part 0 was finalized**
   (reduced `draws=3`, world 0 of `base1x_shared_k10` and
   `authors_x32_holdout_shared_k10`), exposing illustrative but partial
   truth-recovery numbers. No lean threshold, combination rule, or
   extrapolation method was chosen or revised because of them -- disclosed
   in full, with the specific numbers seen, in Part 0.11a.
3. **Variant B (asymptotic) truth recovery is uniformly and substantially
   lower than Variant A (exact) at every single cell** (e.g. x32 holdout:
   0.637 vs 0.150) -- not merely on the extrapolated .5-agreement point.
   This is a substantive finding, not an artifact: under kappa>0, the
   state term's cross-occasion variability is governed by the shared
   context-occasion shock (and, at kappa<1, the author-private AR(1)
   process); a SHORT finite sample's own field, even using ALL its
   available (noisy) data, apparently tracks "the specific short
   realization it was drawn from" (Variant A) far more closely than it
   tracks "the long-run/population signature of that realization"
   (Variant B). This reads as exactly the failure mode the registration
   was built to detect: split-half agreement, computed from two SHORT
   halves of the SAME short realization, is well-positioned to certify
   REPRODUCIBILITY of that realization, but that is a different thing
   from certifying convergence to a stable, generalizable signature.
4. **Reduced worker counts were required for the two largest cells**
   (mult=16: `--workers 4`; the x32 holdout: `--workers 3`, vs. `--workers
   8` for mults 1-8) purely for memory safety (Part 0.3) -- this changes
   wall-clock time only, not any computed value (every cell's own 8 worlds
   are still computed with the identical per-world seed derivation
   regardless of how many run concurrently).
5. **Two independent code routes to the finite-sample field agree to
   literal bit-identical `0.0` on all 88 world-checks** (G4) -- stronger
   than the registered `<=1e-9` tolerance required, and stronger than "a
   degenerate case" (the registration's own minimum ask): this leg checked
   it on every world of every cell as a free byproduct of the pipeline
   structure (Part 0.5).
6. **A column-naming bug in the (non-gating) sensitivity stage, found and
   fixed after that stage completed, self-reported here rather than
   silently corrected.** `T_LARGE_PRIMARY`/`T_LARGE_SENSITIVITY` were
   revised from an earlier draft's 150/600 down to 80/320 (Part 0.3,
   memory safety) before ANY of the 11 registered cells were computed --
   but `run_sensitivity_world`'s output dict still used the OLD values as
   hardcoded literal column-name strings (`"truth_recovery_long_t150"`,
   `"truth_recovery_long_t600"`), which were never updated when the
   constants changed. **The underlying NUMBERS were always correct** --
   both call sites passed `t_large=T_LARGE_PRIMARY` (80) and
   `t_large=T_LARGE_SENSITIVITY` (320) respectively, never the stale
   literals -- confirmed independently by cross-checking the "T=80" column
   against the main sweep's own `truth_recovery_long_mean` for the same two
   cells in `cells.csv`: `0.150105` and `0.022525`, matching to every
   reported digit. Only the CSV column headers and log-line labels were
   wrong. This did not touch gates G1-G4, any of the 11 main cells, or the
   adjudicated leans/pivot (all computed via `run_truth_sweep_world`, which
   never had this bug -- its own `t_large` field always correctly reported
   the live constant, not a literal). Fixed in the script (column names now
   derive from the constants directly, so the label cannot drift from the
   computation again) and the two already-computed sensitivity CSVs were
   relabeled in place (a column rename on already-correct data, not a
   recompute) before this report was written.

## Decision boundary

Exploratory, synthetic-calibrated, label-free. This leg audits, and does
NOT itself replace, the certification target M4-F1-M4-F4 built: the
deployed split-half agreement statistic correlates with truth-referenced
recovery in RANK terms but fails this leg's registered, zero-tolerance
co-movement and target-adequacy leans, and the pivot fires on two
independent registered grounds. Per the registration's own pre-committed
consequence, the .5 agreement target, the 46.1x author-multiple budget, and
the ~26,052-author D3 panel recommendation are WITHDRAWN. This licenses a
finding about the GAUGE's certification validity under this calibrated
synthetic instrument only -- it does not itself supply a replacement
truth-referenced target (that respecification is the registered next
question this line now owns), and it makes no claim about the real relation
field's actual content, personality, emotion, diagnosis, or any individual.
It does not reopen or repair M4-F3's own merged events-axis consequence
(still a GAUGE problem, connected to the M4-E2 objective-redesign open
problem); it also does not, by itself, tell us whether the AUTHOR axis
specifically (as opposed to the agreement statistic generally) is a
promising direction -- Variant A's own extrapolated 0.810 keeps that door
open, Variant B's 0.200 closes it, and that unresolved disagreement is
exactly why the certificate is withdrawn rather than merely re-scaled.
Artifacts: `results/m4_f5_gauge_validity/{decision.json, gates.json,
cells.csv, cell_*.csv, draws_*.csv, sensitivity_t_large.csv,
sensitivity_t_large_summary.csv}`.
