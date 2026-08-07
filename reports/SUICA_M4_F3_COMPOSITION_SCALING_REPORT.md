# SUICA M4-F3 -- Level or Rate? Paired Within-World/Within-Kappa Exponent Comparison (shared-occasion vs free-response design, on M4-F1's own sweep protocol)

> **BANNER: synthetic worlds calibrated to an opened-panel regime, exploratory.**
> This leg consumes NO new real-text evidence. It reuses M4-F1's
> `M4F1RelationWorld` sweep protocol (multiplier scaling on two axes,
> log-log OLS fits, bootstrap over worlds, one held-out validation cell) and
> M4-F2's context-occasion common-shock generator (`generate_world_composed`,
> kappa in [0,1], `free`/`shared` occasion design) UNCHANGED, combining them
> in one new sweep that was absent from both prior legs. No label columns
> anywhere; no claim about the real relation field's content, personality,
> emotion, diagnosis, or any individual.

Registered spec: `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md`
section "M4-F3 registration (2026-08-03, BEFORE run) -- level or rate? the
decisive fork" (loop cycle 14, panel design laws line, leg 3). Script:
`scripts/run_suica_m4_f3_composition_scaling.py`. Artifacts:
`results/m4_f3_composition_scaling/`.

## Part 0 -- REGISTERED ADJUDICATIONS AND OPERATIONALIZATIONS (written before the run)

The registration fixes the mechanism (reuse M4-F2's kappa/design world
unchanged), the two sweep axes and their multiples, the two kappa levels, the
held-out cell, the primary statistic (paired-by-world `delta_gamma`,
bootstrapped over worlds), the three leans, the pivot, and four gates. It
leaves several implementation-level choices open. Per the process rule ("if
the spec cannot be executed as written... state the minimal disclosed
deviation... and proceed only if it preserves the registered comparison"),
every one of those choices is fixed here, BEFORE any gate or sweep compute,
with the reasoning that forced each choice.

### 0.1 Reuse boundary (what is imported/called unchanged vs. newly written)

Directly imported/called, never reimplemented:
`f1().load_spec`, `f1()._directions`, `f1().e1()`, `f1().build_layout`,
`f1().featurize_panel`, `f1().half_indices`, `f1().knob_tag`, `f1().fit_axis`,
`f1().bootstrap_axis`, `f1()._log_odds` (from
`scripts/run_suica_m4_f1_panel_sizing.py`); `f2().generate_world_composed`
(the kappa shared-occasion generator -- kappa<=0 delegates bit-for-bit to
`f1().generate_world`), `f2().run_gate_g1`, `f2().run_gate_g3` (called
directly, not reimplemented, from `scripts/run_suica_m4_f2_composition.py`).

Newly written, because neither prior leg has it: a per-world sweep engine
(`run_sweep_world`) combining `f1().build_layout`'s multiplier scaling with
`f2().generate_world_composed`'s kappa/design axis -- F2's own
`run_axis1_world` cannot be reused verbatim here because its "raw" layout
branch hardcodes `author_mult=event_mult=1` (it exists only to reproduce
M4-F1's exact base1x cell for F2's own gate) and its "common" layout branch
applies a Q-divisibility floor this leg has no reason to need (no crossed
axis exists in M4-F3); gates G2 and G4 (new pairing/budget properties this
leg's design introduces, absent from F1/F2); the paired-by-world bootstrap of
`delta_gamma = gamma_shared - gamma_free` (the registration's own declared
PRIMARY statistic -- built by refitting `f1().fit_axis` on ONE shared
per-draw world-index resample applied to both designs, which is a different
construction from `f1().bootstrap_axis`'s own independent-per-cell
resampling; that function answers a different question, "each design's own
marginal exponent CI," and is reused verbatim for exactly that deliverable).

### 0.2 The kappa x axis crossing: fully factorial (register-note resolving an instruction ordering ambiguity)

The registration states kappa levels ("1.0 primary... 0.5... robustness")
and the two sweep axes ("events/author x {1,2,4,8}... authors x {1,2,4}...
for BOTH designs, on identical world seeds") in two separate bullets, without
explicitly re-stating which axis gets which kappa treatment. Three of the
three registered leans and the pivot are specified entirely on "the events
axis at kappa=1.0," which could be read as license to run only a reduced
kappa=0.5 slice (or skip it for the authors axis). This leg reads the
instruction literally and fully-factorially instead: BOTH axes are swept at
BOTH kappa levels for BOTH designs (base1x once per design x kappa, reused as
the mult=1 anchor for both axis fits at that design x kappa -- exactly as
M4-F1's own single base1x cell anchored both of its axes). Reasoning: (i) it
is the most literal reading of "for BOTH designs, on identical world seeds"
combined with the kappa bullet, with no unregistered asymmetric choice about
which axis or design gets the robustness treatment; (ii) compute cost is not
prohibitive at this budget scale (estimated from M4-F1's own persisted
per-world timings: ~17-20 wall-minutes at 8 parallel workers for the full
grid, run in chunked foreground calls); (iii) it gives an honest secondary
read on the authors axis and the kappa=0.5 robustness axis instead of
leaving them as unmeasured registration text. The events axis at kappa=1.0
remains the ONLY axis/kappa combination that gates any lean or the pivot;
everything else is reported as disclosed secondary context (0.10).

### 0.3 The paired-seed design (register-note, mirroring M4-F2's own Part 0.7 exactly)

For a given `(axis, mult, kappa)` point, the `free` and `shared` cells share
one `world_seed` AND one `corpus` string per world index
(`world_seed_for(seed_key, world, knob_tag)`, `seed_key` independent of
design; `corpus = f"m4f3-{seed_key}-w{world}"`, `budget_label="f3.0"`
constant everywhere). Consequently `z`/`zeta`/`x`/`noise`/`loadings` AND the
split-half draw indices AND the transition-null permutations are IDENTICAL
between the paired `free_*`/`shared_*` cells at a given world index; only the
kappa/occasion_mode blend passed into `generate_world_composed` differs. This
maximizes power for the registered primary statistic (paired-by-world
`delta_gamma`, bootstrapped over worlds) exactly as M4-F2's Part 0.7 argued
for its own paired statistic, and is what licenses gate G2's "identical world
seed AND identical event budget" as an exact-equality check rather than a
tolerance check.

### 0.4 No common-budget truncation (unlike M4-F2; register-note explaining why none is needed)

M4-F2 needed a "largest common budget across cells" truncation (its own Part
0.3) because its crossed-context axis required per-author counts divisible
by `Q in {2,4}`. M4-F3 has no crossed axis at all -- both sweep axes are pure
multiplier scaling of `f1().build_layout(reference, author_mult, event_mult)`,
exactly as M4-F1's own sweep used it, for every one of this leg's cells
(base1x, events, authors, and the holdout), at every design and kappa. No
divisibility escape clause is triggered and none of M4-F2's Part 0.3/0.5
truncation or featurizability-wall machinery applies here.

### 0.5 base1x is one cell per (design, kappa), reused as the mult=1 anchor for both axes

Registered design implies "events/author x {1,2,4,8}" and "authors x
{1,2,4}" share the same mult=1 point (M4-F1's own base1x). This leg computes
exactly one `base1x_{design}_{kappa_tag}` cell per of the four
(design,kappa) combinations (`author_mult=1, event_mult=1`) and reuses it as
the mult=1 row in BOTH the events-axis and the authors-axis `f1().fit_axis`
call at that same (design, kappa) -- structurally identical to how M4-F1's
own `SWEEP_CELLS` list has exactly one `base1x` entry consumed by both of its
axis fits.

### 0.6 G1 vs. this leg's own base1x sweep cells (register-note distinguishing two different computations)

G1 (`f2().run_gate_g1`, called directly) reproduces M4-F1's persisted
`base1x` row using M4-F1's OWN exact seed recipe (`seed_group="base1x"`,
corpus tag `m4f1`, salt `m4f1-world`, budget label `f1.0`, the
RAW/untruncated layout, kappa=0, design irrelevant since kappa<=0 ignores
it) -- this is a completely different computation from this leg's OWN
`base1x_free_k05`/`base1x_free_k10`/`base1x_shared_k05`/`base1x_shared_k10`
sweep cells (kappa in {0.5, 1.0}, this leg's own `m4f3-world` seed scaffold).
They intentionally answer different questions (gate correctness vs. the
registered sweep) -- exactly the same distinction M4-F2's own Part 0.3 drew
between its G1 gate and its adjudicated cells.

### 0.7 G2 and G4: two independent, deliberately different-grained checks of the same underlying invariant

**G2** ("within-kappa/within-world pairing... cell-by-cell exact equality")
is the FINE-grained check: for every `(axis, mult, kappa)` point, per WORLD,
`world_seed_free == world_seed_shared` and `n_events_free == n_events_shared`
(96 rows = 12 points x 8 worlds). **G4** ("per-multiple budget conservation...
between the two designs") is read as the COARSER, independent check: for
each swept multiple, the total event count is identical not just between the
two designs at a fixed kappa (G2's scope) but across BOTH kappa levels too --
catching any accidental kappa-dependent count leakage that a same-kappa-only
comparison would not by itself rule out. Both gates are computed from the
SAME underlying calls this leg's actual sweep uses
(`world_seed_for`/`f1().build_layout`), not a separately-retyped formula, so
a real code-path bug would surface as a genuine mismatch rather than being
definitionally impossible to detect. In this leg's construction (pure
multiplier scaling, no truncation), design and kappa provably never affect
`build_layout`'s event counts and `world_seed_for` never takes design as an
argument at all -- so both gates are EXPECTED to hold trivially by
construction. They are computed and reported anyway, exactly as M4-F2's own
G4 "designed null" was expected to hold at kappa=0 and was still verified
rather than assumed.

### 0.8 The paired-by-world bootstrap of delta_gamma: exact algorithm (this leg's own construction, the registration's declared primary statistic)

For `draws=2000` iterations: draw ONE set of `n_worlds=8` world indices with
replacement (`rng.integers(0, 8, size=8)`); apply that SAME index set to
EVERY cell's `world_values` in both the free-side axis rows and the
shared-side axis rows (recomputing each resampled cell's mean/SE exactly as
`f1().bootstrap_axis` does for its own single-axis resampling); refit
`f1().fit_axis` (verbatim) on each side; if BOTH fits reach at least
DEGENERATE status with a positive exponent (the same qualifying condition
`f1().bootstrap_axis` itself uses), record
`delta = gamma_shared - gamma_free`; otherwise count the draw as a bootstrap
failure. The 2.5/97.5 percentiles of the collected deltas are the reported
CI. Seeded per (axis, kappa) combination for reproducibility (`events_k05`,
`events_k10`, `authors_k05`, `authors_k10`), independent of the marginal
bootstraps' own seeds.

### 0.9 Held-out validation: staged exactly as M4-F1's own predict-then-holdout discipline

"Mirror the sweep and power-law FITTING protocol you must mirror (...held-out
validation cell...)" is read to include M4-F1's own TEMPORAL discipline, not
only its statistical form: the events-axis (shared, kappa=1.0) fit and its
log-odds prediction at 16x are computed and persisted to `prediction.json`
via the `predict` stage BEFORE the `holdout` stage is ever allowed to run
(`run_holdout` refuses if `prediction.json` is absent) -- exactly
`f1().run_holdout`'s own refusal condition on `prediction_16x.json`. This
avoids any hindsight-fitting bias in the factor-2 validation check.

### 0.10 Fittable-cell-count discipline (the registration's own explicit warning, operationalized)

Per the registration ("do not fit a law on fewer cells than M4-F1's own
registered standard... if an axis is degenerate, say so and do not
manufacture an exponent"): every fit's `status` (`FITTED` requires >=3
qualifying cells per `f1().fit_axis`'s own unchanged rule; `DEGENERATE` is 2;
`UNFITTABLE` is <2) is reported plainly. Lean (b)'s budget claim and lean
(c)'s holdout validation additionally REQUIRE the shared/kappa=1.0 events fit
to reach `FITTED` (not merely `DEGENERATE`) to be adjudicated HOLD --
mirroring M4-F1's own lean-c discipline ("DEGENERATE fits cannot hold") --
even though the registration does not restate this requirement verbatim for
M4-F3's leans b/c. The authors axis here has only 3 possible multiples
(`{1,2,4}`, one fewer than M4-F1's own `{1,2,4,8}`), so it can reach `FITTED`
only if all three qualify simultaneously; it gates no registered lean or the
pivot (all three leans and the pivot are specified on the events axis at
kappa=1.0 only) and is reported as secondary context.

### 0.11 A mechanical loading fix, discovered at gate compute time and disclosed here before any gate number exists (process-rule disclosure)

The first invocation of `--stage gates` failed before producing any number:
`f2().run_gate_g1`'s internal `ProcessPoolExecutor.map(run_axis1_world, ...)`
raised `PicklingError: Can't pickle <function run_axis1_world ...>: it's not
the same object as run_suica_m4_f2_composition.run_axis1_world`. Root cause:
neither F1's nor F2's own `_load_script` helper registers the dynamically
loaded module in `sys.modules` -- this was never needed before, because when
F1 or F2 is run directly its own top-level functions live in
`sys.modules['__main__']`, which multiprocessing's pickle-by-reference
lookup always finds. This leg is the first to call a DYNAMICALLY LOADED
module's own internal `ProcessPoolExecutor` call from a third script: this
script's own directory is auto-added to `sys.path[0]` (standard CPython
behavior), which lets a competing, separately path-imported copy of
`run_suica_m4_f2_composition` register itself in `sys.modules` under the
same name pickle's identity check looks up -- a DIFFERENT Python object than
the one `f2()`'s cache holds, so pickling by reference fails the identity
check. Fix applied to THIS script's own `_load_script` only (`sys.modules[mod_name]
= module` before `exec_module`, the textbook-correct pattern for a
dynamically loaded module meant to support reflection/pickling): zero edits
to `run_suica_m4_f1_panel_sizing.py` or `run_suica_m4_f2_composition.py`
themselves, zero change to what any function computes -- this only makes an
already-registered reuse ("call `f2().run_gate_g1` directly") mechanically
functional. No gate or sweep number existed before this fix landed.

### 0.12 A third possible outcome the registration's two named branches did not anticipate (disclosed before seeing any result)

The registration frames the decisive fork as binary: lean (a) HOLDs
(`delta_gamma > 0`, CI excluding 0) or the pivot fires (CI includes 0). A
paired bootstrap CI can also land entirely NEGATIVE (excludes 0 on the
negative side) -- `gamma_shared` reliably LOWER than `gamma_free`. Neither
registered branch's literal text covers this case. This report commits, before
seeing the sweep result, to detecting and flagging this third case explicitly
rather than silently filing it under either named branch, per the standing
instruction: "If an outcome lands outside every registered branch, say
exactly that."

*(Everything below this line was written after the run; nothing above was
edited after compute began.)*

---

## Part 1 -- OUTCOME

**0/3 leans; pivot FIRES: `COMPOSITION_BUYS_LEVEL_NOT_RATE_GAUGE_PROBLEM_MERGES_WITH_M4E2`.
delta_gamma's paired bootstrap CI on the events axis at kappa=1.0 is
`[-0.839, +0.039]` -- includes 0, exactly the registered pivot condition.
But the mechanism behind that number is NOT "two clean power laws differing
only in intercept" (the registration's own framing of what a level-only
difference would look like): under kappa>0, NEITHER design's events axis
even reaches a fittable power law at all (free is DEGENERATE at kappa=0.5,
UNFITTABLE at kappa=1.0; shared is UNFITTABLE at both kappas) -- the axis
that was cleanly FITTED at kappa=0 in M4-F1 (gamma=.153) stops behaving like
a power law once ANY context-occasion shock exists, under either design.
The secondary (non-gating) authors axis tells a sharply different story:
under the SHARED design specifically, it goes from M4-F1's own kappa=0
DEGENERATE finding to a clean, low-failure-rate FITTED law at BOTH kappa=0.5
(gamma=0.860) and kappa=1.0 (gamma=1.104) -- a genuine rate change, just on
the axis the registration did not make decisive.**

Run: gates (G1 Monte Carlo + G2/G4 pure arithmetic + G3 direct reuse) under a
minute; sweep 24 cells x 8 worlds x 20 draws in three foreground chunks
(base1x group 39s, events group 422s, authors group 211s -- all at
`--workers 8` on a 10-core machine); the events x16 shared/kappa=1.0
held-out cell 140s; predict and finalize (bootstrap-only, no further Monte
Carlo) each under 15s. Total leg compute ~14 minutes. `MASTER_SEED=20260802`
(M4-F1's/M4-F2's own), knobs reused verbatim from M4-F1's
`calibration_record.json` (`k=48, rho=.50, w_mu=.15, w_x=.15, w_e=.70, phi in
[.20,.80]`) -- this leg performs no new calibration search.

## Gates (all green)

- **G1** (kappa<=0 free cell reproduces M4-F1's persisted `base1x` to
  <=1e-12; computed via a direct call to `f2().run_gate_g1`, not
  reimplemented): `agreement_mean` abs diff **9.89e-17**, `agreement_se` abs
  diff **1.12e-16**, `d0_eff_rank_M_mean` abs diff **0.0**,
  `d0_eff_rank_K_mean` abs diff **7.11e-15**, `n_retained` exact (565=565) --
  identical diffs to M4-F2's own G1 (expected: it is the literal same
  function call against the same M4-F1 target row). **PASS.**
- **G2** (within-kappa/within-world pairing, cell-by-cell): 12
  `(axis,mult,kappa)` points x 8 worlds = 96 rows, `world_seed_free ==
  world_seed_shared` and `n_events_free == n_events_shared` at every single
  row (verified via the actual `world_seed_for`/`f1().build_layout` calls the
  sweep itself uses). **PASS**, trivially by construction as disclosed in
  Part 0.7 -- design is not an input to either function in this leg.
- **G3** (gauge invariance, direct call to `f2().run_gate_g3`): batched
  feature map vs. deployed `v8.build_feature_panel` -- max abs diff M = 0.0,
  K = 0.0 (bit-identical); halving vs. `e1().split_half_frames` -- 120/120
  identical. **PASS.**
- **G4** (per-multiple budget conservation across kappa AND design): 6
  multiples (`base1x`=1, `events`={2,4,8}, `authors`={2,4}) each allocate an
  identical event total at both kappa=0.5 and kappa=1.0 -- `base1x`=13,202;
  `events_x2`/`authors_x2`=26,404; `events_x4`/`authors_x4`=52,808;
  `events_x8`=105,616 (matches M4-F1's own raw, untruncated per-multiplier
  totals exactly, since this leg applies no truncation -- Part 0.4). **PASS**,
  trivially by construction as disclosed in Part 0.7.

`results/m4_f3_composition_scaling/gates.json` carries the full G2 96-row
table and G4's per-multiple detail.

## Sweep results: cell means (8 worlds each; `n_retained=565` D1+D2 authors identically across every non-holdout cell, `n_retained` scaling exactly with `author_mult` on the authors axis -- 1,130 at 2x, 2,260 at 4x, confirming no cell-specific retention-floor interaction)

| axis | mult | kappa | free mean (se) | shared mean (se) |
|---|---|---|---|---|
| base1x | 1 | 0.5 | +0.004714 (0.002302) | +0.007953 (0.002582) |
| base1x | 1 | 1.0 | +0.003656 (0.001347) | +0.006117 (0.001743) |
| events | 2 | 0.5 | +0.000711 (0.001387) | +0.002439 (0.001427) |
| events | 2 | 1.0 | +0.003159 (0.002258) | +0.001856 (0.001502) |
| events | 4 | 0.5 | +0.004102 (0.002032) | +0.004551 (0.002851) |
| events | 4 | 1.0 | +0.003762 (0.001939) | **-0.001300** (0.002278) |
| events | 8 | 0.5 | +0.002490 (0.001937) | +0.000940 (0.003206) |
| events | 8 | 1.0 | **-0.001135** (0.002220) | **-0.005461** (0.003256) |
| events | 16 (holdout) | 1.0 | -- | **-0.001715** (0.002602) |
| authors | 2 | 0.5 | +0.006062 (0.002904) | +0.009970 (0.002558) |
| authors | 2 | 1.0 | +0.002196 (0.002378) | **+0.033189** (0.001929) |
| authors | 4 | 0.5 | +0.002669 (0.001899) | +0.022487 (0.002819) |
| authors | 4 | 1.0 | +0.002989 (0.001718) | **+0.058590** (0.005162) |

The events axis is flat-to-declining at kappa=1.0 for BOTH designs from mult
1 through 8 (free: .0037 -> .0032 -> .0038 -> **-.0011**; shared: .0061 ->
.0019 -> **-.0013** -> **-.0055**), and the held-out 16x shared/kappa=1.0
cell (-.0017) stays negative rather than resuming a rise. The authors axis
under `shared` design grows sharply with both mult and kappa (base1x .0061
-> 4x **.0586** at kappa=1.0); under `free` design it stays flat near the
base1x level at both kappa (.0022-.0030).

## Point fits (`f1().fit_axis`, verbatim; `FITTED` needs >=3 qualifying cells of 4 (events) or 3 (authors) -- Part 0.10)

| axis | design | kappa | status | n qualifying | exponent | .5-agreement budget (mult) |
|---|---|---|---|---|---|---|
| events | free | 0.5 | DEGENERATE | 2 of 4 | (not licensed -- see Part 0.10) | -- |
| events | shared | 0.5 | **UNFITTABLE** | 1 of 4 | -- | -- |
| events | free | 1.0 | **UNFITTABLE** | 1 of 4 | -- | -- |
| events | shared | 1.0 | **UNFITTABLE** | 1 of 4 | -- | -- |
| authors | free | 0.5 | DEGENERATE | 2 of 3 | (not licensed) | -- |
| authors | shared | 0.5 | **FITTED** | 3 of 3 | **0.860** | 330.6x |
| authors | free | 1.0 | **UNFITTABLE** | 1 of 3 | -- | -- |
| authors | shared | 1.0 | **FITTED** | 3 of 3 | **1.104** | 45.4x |

Compare M4-F1's own kappa=0 events-axis reference: FITTED, gamma=0.1532,
budget 1.08192e14x (`results/m4_f1_panel_sizing/decision.json` `fits.events`,
read programmatically, not retyped). No kappa>0 events-axis cell in this leg
comes anywhere near that FITTED status on either design.

## Each design's marginal gamma with its own CI (`f1().bootstrap_axis`, verbatim, 2000 resamples/combination -- reused exactly as M4-F1 built it for a single-axis marginal CI, distinct from the paired statistic below)

| axis | design | kappa | exponent 95% CI | resamples failed/nonpositive |
|---|---|---|---|---|
| events | free | 0.5 | [0.0040, 1.2208] | 1648/2000 |
| events | shared | 0.5 | [0.0082, 1.2820] | 1729/2000 |
| events | free | 1.0 | [0.0177, 1.3130] | 1220/2000 |
| events | shared | 1.0 | [0.0065, 1.0338] | 1983/2000 |
| authors | free | 0.5 | [0.0068, 1.3003] | 1539/2000 |
| authors | shared | 0.5 | [0.3757, 1.5320] | 1/2000 |
| authors | free | 1.0 | [0.0146, 1.1614] | 1399/2000 |
| authors | shared | 1.0 | **[0.7192, 1.4536]** | **0/2000** |

Every events-axis marginal CI is built from a MINORITY of resamples that
happened to produce a positive-exponent fit at all (as low as 17/2000 =
0.85%, `events_shared_k10`) -- these CIs must be read as evidence the
underlying regime is essentially unfittable, not as precise interval
estimates of a real exponent (`f1().bootstrap_axis`'s own filter accepts
ANY positive exponent from a `DEGENERATE`-or-better fit, so a handful of
noise-driven 2-point slopes dominate a mostly-empty resample pool). The two
`authors, shared` rows are the opposite case: 2000/2000 and 1999/2000
resamples qualified -- a stable, well-powered result, not a fluke.

## The primary statistic: paired-by-world bootstrap of delta_gamma = gamma_shared - gamma_free (2000 resamples per axis/kappa, ONE shared world-index resample per draw applied to both sides -- Part 0.8)

| axis | kappa | n valid / 2000 | delta_gamma point | delta_gamma CI95 | CI excludes 0 (+) |
|---|---|---|---|---|---|
| events | 0.5 | 59 | n/a (neither point-fit >= DEGENERATE-and-qualifying on both sides) | [-1.176, +0.420] | no |
| **events** | **1.0** | **18** | **n/a (both UNFITTABLE)** | **[-0.839, +0.039]** | **no** |
| authors | 0.5 | 327 | +0.495 | [-0.669, +1.021] | no |
| authors | 1.0 | 700 | n/a (free UNFITTABLE) | [-0.589, +1.330] | no |

The decisive row (events, kappa=1.0) is built from only **18 of 2000**
paired resamples (0.9%) -- both sides' refits simultaneously reached at
least `DEGENERATE`-with-positive-exponent in only those 18 draws. This CI is
reported exactly as computed, per the registration, but its own construction
is a strong independent signal of the same finding the point fits already
show directly: the events axis at kappa=1.0 does not behave like a
fittable power law under either design, so a "delta between two exponents"
is barely a defined quantity here at all.

## The .5-agreement budget extrapolation under the shared design at kappa=1.0

**Not computable.** `events_shared_k10`'s fit status is `UNFITTABLE` (1 of 4
cells qualifies -- only `base1x_shared_k10`; `events_x2/4/8_shared_k10` all
fail the `mean - 2*SE > 0` qualifying bar, and two of the three are
negative-mean). `f1().fit_axis` returns no `exponent`/`intercept` for an
`UNFITTABLE` status, so no budget number exists to extrapolate -- reporting
one would be exactly the "manufactured exponent" the registration's own
Part 0.10 discipline forbids. (For contrast, M4-F1's own free-response,
kappa=0 events-axis budget was 1.08192e14x, `results/m4_f1_panel_sizing/decision.json`.)

## Held-out validation (events x16, shared design, kappa=1.0)

Observed: `agreement_mean = -0.001715` (se 0.002602, 8 worlds x 20 draws,
`n_retained=565`). No prediction existed to validate against
(`holdout_prediction.status = "EVENTS_AXIS_UNFITTABLE_HOLDOUT_IS_A_PROBE"`,
persisted to `prediction.json` BEFORE this cell was computed, per Part 0.9's
predict-then-holdout staging) -- the cell was run as a probe, exactly as
M4-F1's own precedent handles an unfittable axis. The observed value is
negative, consistent with (not contradicting) `events_x8_shared_k10`'s
already-negative -.0055 and the flat-to-declining shape at every other
tested multiple under kappa=1.0.

## Supplementary, non-registered context: paired raw-agreement diffs per multiple (`f2()._paired_ci`, reused verbatim; NOT the primary statistic -- delta_gamma is -- but shows the shape the fits above are trying to summarize)

| axis | mult | kappa | shared - free | 95% CI | t | excludes 0 (+) |
|---|---|---|---|---|---|---|
| events/base1x | 1 | 0.5 | +0.00324 | [-0.00167, +0.00815] | 1.56 | no |
| events | 2 | 0.5 | +0.00173 | [-0.00136, +0.00482] | 1.32 | no |
| events | 4 | 0.5 | +0.00045 | [-0.00513, +0.00603] | 0.19 | no |
| events | 8 | 0.5 | -0.00155 | [-0.00558, +0.00248] | -0.91 | no |
| events/base1x | 1 | 1.0 | +0.00246 | [-0.00199, +0.00691] | 1.31 | no |
| events | 2 | 1.0 | -0.00130 | [-0.00761, +0.00500] | -0.49 | no |
| events | 4 | 1.0 | -0.00506 | [-0.01113, +0.00101] | -1.97 | no |
| events | 8 | 1.0 | -0.00432 | [-0.01446, +0.00581] | -1.01 | no |
| authors | 2 | 0.5 | +0.00391 | [+0.00038, +0.00743] | 2.62 | **yes** |
| authors | 4 | 0.5 | +0.01982 | [+0.01448, +0.02516] | 8.77 | **yes** |
| authors | 2 | 1.0 | +0.03099 | [+0.02580, +0.03618] | 14.12 | **yes** |
| authors | 4 | 1.0 | +0.05560 | [+0.04371, +0.06749] | 11.06 | **yes** |

Full table: `results/m4_f3_composition_scaling/supplementary_paired_agreement_diffs.csv`.
At NO multiple on the events axis does the shared-minus-free paired diff
exclude zero (positively or at all); at every tested multiple on the
authors axis (2x and 4x, both kappas) it excludes zero decisively, and the
diff GROWS with mult and with kappa. This is the same pattern the point
fits report, shown at the level the fits were built from.

## Lean adjudication

- **Lean (a) MISS.** Rule: `delta_gamma > 0` on the events axis at
  kappa=1.0, paired bootstrap CI excluding 0. Observed CI `[-0.839, +0.039]`
  includes 0.
- **Lean (b) MISS.** Rule: the shared/kappa=1.0 events-axis .5-agreement
  budget falls below 1e6x. `events_shared_k10`'s fit status is `UNFITTABLE`
  -- per Part 0.10's discipline (mirroring M4-F1's own lean-c rule), a
  DEGENERATE/UNFITTABLE fit cannot license a HOLD budget claim regardless of
  what a forced extrapolation might say, and none was computed at all here.
- **Lean (c) MISS.** Rule: the held-out x16 shared/kappa=1.0 cell validates
  the fitted law within factor 2. There is no fitted law to validate against
  (`EVENTS_AXIS_UNFITTABLE_HOLDOUT_IS_A_PROBE`); `within_factor2=False` by
  construction.
- **PIVOT FIRES.** Registered rule: delta_gamma's paired bootstrap CI
  includes 0 on the events axis at kappa=1.0. `[-0.839, +0.039]` includes 0.
  **`ci_excludes_zero_negative` is also false** (the CI's upper bound,
  +0.039, is positive) -- so this result falls cleanly inside the
  registered pivot branch, not the undeclared third "reliably negative"
  outcome flagged in Part 0.12; that third case was checked for and did not
  occur.

**Verdict: `COMPOSITION_BUYS_LEVEL_NOT_RATE_GAUGE_PROBLEM_MERGES_WITH_M4E2`.**
Per the registration, this MERGES the panel-design-laws line with the M4-E2
objective-redesign open problem (`docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md`
M4-E2 outcome: `OFFSET_SPREAD_NO_SINGLE_OBJECTIVE_TERM`), which becomes the
registered next question for this thread. As the registration itself
anticipated: "the M4-F2 pivot pointed at the same destination from the
other side; arriving there twice by independent routes would be a strong
result, not a disappointment" -- M4-F2's own pivot did not fire on its
composition-at-fixed-budget test, but this leg's SCALING test of that same
composition reaches the identical GAUGE-problem destination by a different
route.

## What the results say (interpretation, hedged -- separate from the adjudicated verdict above)

**The pivot firing here does not mean "shared design buys the same shape of
law as free, just shifted."** The registration's own framing of a level-only
outcome implicitly assumed both designs would still produce SOME fittable
power law. That did not happen for either design on the events axis at
kappa>0: M4-F1's kappa=0 events-axis law (gamma=.153, itself already too
weak to matter at any feasible budget) does not survive the introduction of
ANY context-occasion shock at all, regardless of whether occasions are
literally shared or not. A hedged mechanical reading: M4-F1 itself diagnosed
that adding events per author "sharpens features while dissolving the
realized-state heterogeneity the field rides on" (signal and noise shrink
together) even at kappa=0; once a shared occasion-indexed component also
exists in the data-generating process, that same effect may interact with
the growing SHARED component in a way that erodes rather than merely dilutes
the split-half CONTRAST as events accumulate -- consistent with, but not
proven by, the flat-to-negative shape observed at every kappa=1.0 events
multiple and the negative 16x holdout. This is offered as a candidate
mechanism, not a demonstrated one; no further compute was run to isolate it,
per the no-post-hoc-rescue rule.

**The authors axis is where a real rate change was actually measured.**
M4-F1's own kappa=0 authors axis was DEGENERATE (flat 1x->2x at the floor).
Under the SHARED design at kappa>0, it becomes cleanly `FITTED` at both
tested kappa levels, with an exponent that itself GROWS with kappa (0.860 at
0.5, 1.104 at 1.0) and a vanishingly small bootstrap failure rate (1/2000
and 0/2000) -- the most stable fit in this entire leg. Under `free` design
the authors axis stays UNFITTABLE/DEGENERATE at both kappas, tracking the
free/shared distinction the registration's whole mechanism argument was
built on. This axis gates no registered lean (Part 0.10) and was
deliberately restricted to 3 multiples by the registration, so it cannot
license a headline claim on its own -- but it is the clearest evidence in
this leg's own data that shared-occasion composition CAN change a rate, just
not on the axis (events) the registration made decisive. This reframes the
open question the pivot hands off: not "can composition ever buy a rate"
(this leg's own authors-axis data suggests yes) but "why does it buy a rate
on the authors axis and not the events axis" -- a question for the
M4-E2-merged gauge-problem line to inherit, not one this leg resolves.

## Honest anomalies and disclosures

1. **This leg's own base1x/kappa=1.0 paired diff (+0.0025, CI including 0,
   Part 1's cell-means table) is much smaller than, and not the same
   comparison as, M4-F2's own headline shared-minus-free/kappa=1.0 result
   (+0.0262, CI excluding 0, `reports/SUICA_M4_F2_COMPOSITION_REPORT.md`).**
   These are DIFFERENT computations sharing only the same knobs/kappa/
   mechanism: different seed scaffolds (`m4f3-world`/`base1x_k10` here vs.
   `m4f2-world`/`axis1` there -- uncorrelated world draws), and different
   layouts (this leg's raw, untruncated `f1().build_layout(reference,1,1)`,
   Part 0.4, vs. M4-F2's own common-budget-truncated layout, its Part 0.3,
   which collapses per-author counts to only 3 distinct values `{8,12,16}`
   instead of this leg's 5 `{8,10,12,14,16}` -- a plausible but UNVERIFIED
   contributor, since a more clustered count distribution changes how many
   authors land on identical shared-occasion indices within a context). This
   discrepancy is disclosed, not investigated further or reconciled --
   doing so now, after seeing both results, would be exactly the kind of
   post-hoc analysis the process rules forbid.
2. **Every events-axis fit in this leg is `DEGENERATE` or `UNFITTABLE`,
   never `FITTED`** (0 of 4 design/kappa combinations reach 3 qualifying
   cells) -- the registration's own Part-0.10-mirrored discipline (no
   manufactured exponent from an under-qualified fit) binds on EVERY events
   number in this report, not just the decisive kappa=1.0 cell.
3. **The paired delta_gamma bootstrap's `n_valid` is small everywhere**
   (18-700 of 2000), smallest exactly on the decisive events/kappa=1.0 row
   (18). The CI is reported as registered, but its own thinness is itself
   evidence for, not a caveat weakening, this leg's central finding (the
   events axis barely produces a well-defined exponent to difference at
   all).
4. **A mechanical `sys.modules` loading fix was required before any gate
   number existed** (Part 0.11) -- zero edits to
   `run_suica_m4_f1_panel_sizing.py` or `run_suica_m4_f2_composition.py`,
   confined entirely to this script's own module-loading helper.
5. **No new calibration search was run.** Per the registration ("mirror
   M4-F1's sweep protocol exactly... your exponents must be directly
   comparable to M4-F1's gamma_events=.153"), the knobs are read verbatim
   from `results/m4_f1_panel_sizing/calibration_record.json`
   (`k48-r0.50-mu0.15-x0.15-e0.70-p0.20_0.80`).
6. **Compute parallelism was faster than pre-registration estimates**
   (Part 0's ~17-20 minute estimate vs. the ~14 minutes actually observed,
   `time`-measured per chunk) -- a pure execution-speed observation with no
   bearing on the registered comparison; disclosed because Part 0.2's
   cost-tractability argument for running the full kappa x axis grid cited
   the (more conservative) pre-run estimate.

## Decision boundary

Exploratory, synthetic-calibrated, label-free. This leg licenses a D3
panel-scaling-DESIGN finding, not a positive one: at kappa>0 (any amount of
context-occasion shared structure), the events axis -- the axis M4-F1's own
scale sweep found weakly fittable at kappa=0 -- does not produce a fittable
power law under either free-response or shared-occasion collection design,
so composition's earlier win (M4-F2, at one fixed budget) does not extend
into a usable SCALING law on the axis that would need one; the registered
pivot fires and this line now merges with the M4-E2 objective-redesign open
problem. It separately, non-bindingly documents that the authors axis (not
gating any lean) shows a genuine rate change specifically under the shared
design, which the merged line inherits as an open question rather than a
resolved one. It makes no claim about the real relation field's content,
about personality, emotion, diagnosis, or any individual, and does not
certify (or refute) any real-text relation structure. Artifacts:
`results/m4_f3_composition_scaling/{decision.json, gates.json, prediction.json,
cells.csv, cell_*.csv, draws_*.csv, supplementary_paired_agreement_diffs.csv}`.
