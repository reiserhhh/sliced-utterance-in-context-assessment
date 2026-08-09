# SUICA M4-K1 — Issuer theorems: the norm field's three-way split on the deployed machinery

Tier: **EXPLORATORY, label-free, synthetic.** Registered in
`docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md`, section "M4-K1 — Issuer theorems"
(REGISTERED 2026-08-09, BEFORE RUN; commit `c902498`). Theory under test:
`docs/SUICA_IDENTITY_THEORY_V1.md` §1, §3 T3/T5, §5. Ledger row `M4-K1`.
Script: `scripts/run_suica_m4_k1_issuer_theorems.py`. Artifacts:
`results/m4_k1_issuer/{manifest.json, gates.json, abs_cells.csv,
abs_probe_correct.npz, rel_cells.csv, decision.json}`.

Executor's standing: implementation and execution only. The registration text
is binding; everything below labelled "register-note" is an operationalization
of something the registration left as an implementation choice, fixed and
written here **before** any arm stage ran.

---

## 0. Part 0 — gates and register-notes, written before any arm

**Gates computed 2026-08-09T04:26:19.338758+00:00 UTC**
(`results/m4_k1_issuer/gates.json`, stage wall-time 1.739 s).
**This section was written to disk at 2026-08-09T04:27 UTC, before the `abs`
and `rel` arm stages were invoked.** No number from the eight adjudicated
worlds existed at that moment.

### G0 — dimensions pinned, grain justified (rule 5)

Extracted from `results/m4_f1_panel_sizing/realtext_panel_reference.json`
through `f2.build_layout_common` (`scripts/run_suica_m4_f2_composition.py:205-222`):

| pinned quantity | value |
|---|---|
| authors / world | **985** |
| events allocated / world (F2 common budget) | **12,784** (raw 13,202; 418 dropped by F2's own multiple-of-4 truncation) |
| events / author multiset | **{8: 272, 12: 200, 16: 513}** |
| contexts | AskReddit, AskWomen, politics, worldnews |
| authors retained by the deployed gauge | **565** |
| deployed retention floor | ≥ 8 events (`f2:65 MIN_RETAINED_EVENTS`) |
| knobs | `k48-r0.50-mu0.15-x0.15-e0.70-p0.20_0.80` (read from F1's `calibration_record.json`, never retyped) |

**Grain.** Unit of identification = one author's probe card; authors are nested
in worlds; worlds are strata. Every pooled interval below is an
author-stratified bootstrap with worlds as strata, and every per-world sign
count is over the 8 worlds. Justified against G3's MDE below.

### G1 — anchor, bit-exact (before any new arm)

`results/m4_f2_composition/axis1_cell_{free,shared}_{k05,k10}.csv` reloaded and
the paired deltas re-derived through F2's own `_paired_ci` (`f2:1008-1025`).
Every field is **bit-exact** against `results/m4_f2_composition/decision.json`
at full float precision (`max_abs_diff` = 0.0 on all fields, both κ):

- κ=1.0: free_mean −0.0027727743463521505; shared_mean +0.023390488960374076;
  paired mean **+0.026163263306726227**, sd 0.007927161015034725,
  se 0.0028026746546443446, t = 9.335105401324688, t_crit 2.364624251592784,
  CI [0.01953599084902978, 0.032790535764422674], n = 8.
- κ=0.5: free_mean +0.0005009098594400375; shared_mean +0.009337063556542562;
  paired mean +0.008836153697102524, CI [0.004418364530893362,
  0.013253942863311687], t = 4.729556467471455.
- The registered equivalence margin **m = 0.006540815826681557** is verified
  to be **exactly** 0.25 × the κ=1.0 paired mean (`==`, not within tolerance).

**G1 PASS.**

### G2 — structural audit, with the branch verdict

Question: does the deployed gauge consume only within-occasion between-author
contrasts post-map?

*The representation R-abs is defined on* — "the LAST common per-event object
the deployed gauge consumes before its pairwise/relational step" — is the
**64-dim frozen event vector**. It is the last object indexed by
(author, occasion) that the gauge ever sees, and the last object **common to
both of the gauge's branches**:

- `suica_core/v8_realtext_relation_field.py:171-188` — `frozen_event_vector`,
  text → R^64 (in these synthetic worlds the generator emits this object
  directly; it is the deployed map's output slot).
- `v8:303-308` — `build_feature_panel` stacks the per-event vectors per author.
- `v8:225` — `family_features`: `values = np.asarray(events, dtype=float)`.
  This one array feeds the **M** branch (`v8:229-241`) and the **K** branch
  (`v8:243-263`). Nothing downstream is per-event.
- Batched deployed-equivalent path actually executed here:
  `scripts/run_suica_m4_f1_panel_sizing.py:195` (`path = vectors[offset::2]`),
  consumed as `values` at `f1:117` and `f1:138`.
- The pairwise/relational step begins at
  `scripts/run_suica_m4_e1_convention_gap.py:235-247` (`deployed_soft_field`) →
  `v8:892-895` (`soft_relation_matrix`) → `v8:898-902`
  (`_soft_cross_covariance`) → `v8:376-382` (`_center` / `_cross_covariance`),
  which is the **first and only** between-author centering in the whole path,
  and it acts on per-AUTHOR feature rows, not on per-event responses.

**Verdict: BRANCH B** — the deployed gauge does **not** consume only
within-occasion between-author contrasts post-map; norm position enters
directly, so L5's leakage carries a **first-order term**, not only map
curvature. Evidence, each with file:line:

1. `v8:229` `mean = values.mean(axis=0)` — the author's own **absolute** path
   mean is written straight into M (`v8:241`). First-order in norm position.
2. `v8:239-240` `projections = values @ marginal_directions.T` and their
   quantiles are absolute, not contrasts.
3. `v8:246` `lag_product = np.mean(previous * following, axis=0)` — quadratic
   in absolute position.
4. `v8:258` `np.tanh(previous @ first) * np.tanh(following @ second)` —
   nonlinear in absolute position.
5. `e1:191` `project_soft` standardizes against a **fixed D0-fit** center
   (`v8:488-493 _fit_standardizer`), not an occasion-wise contrast.
6. `f1:195` replicate paths are author-specific occasion subsets and
   `f1:235-247 half_indices` is author-seeded — so a *common* pre-map occasion
   shift arrives post-map as an **author-specific** displacement even through
   the linear M-mean term.

Per the registration, the branch changes interpretation only; the measurement
runs either way.

### G3 — power (rule 2), on a reserved-seed pilot world

Pilot world index **9001**, seed group `pilot` — never adjudicated, never one
of the eight.

- Per-event noise energy from the generator's own knobs: `2·w_e = 1.4`
  (w_e = 0.7, σ_iso² = 2/64, 64 dims).
- Issuer variance added to each card-pair distance at |P| = 8:
  `2·1.4/(n_half·8) = 0.0875` with n_half = 4.
- **Expected issuer effect, derived from those ratios applied to the pilot's
  ORACLE-arm card geometry only** (no est8 result enters): oracle rank-1
  0.5776649746192893 → predicted est8 rank-1 0.4763959390862944 →
  **expected effect 0.10126903553299493**.
- Variance: author bootstrap SE within the pilot world 0.013354033970299885;
  pooled across 8 worlds 0.004721363988297281; 80 %-power multiplier
  (t.975,7 + t.80,7) = 3.2606538959065494 → **MDE = 0.015394733882434413**.
- Requirement MDE ≤ expected effect: **0.0153947 ≤ 0.1012690 → PASS.** No
  author escalation needed; the registered ABORT branch does not fire.
- Disclosed for transparency (reserved world, excluded from adjudication): the
  pilot's *observed* oracle − est8 contrast is 0.1065989847715736.

### G4 — channel verification (rule 3), pilot world

- Norm-error variance by arm (free design, over the used occasions):
  est8 3.1117215163362468e-03 > est32 8.240645537633776e-04 >
  est128 1.5838602310029443e-04 > 0 — **expected |P| ordering holds**.
- Decision flips vs oracle at est8 in the free design: **361** (> 0) — the
  issuer channel is **live**, not inert, at this regime.
- `biased32` bias vs sampling: ‖μ̂_bias − μ̂_or‖ rms 0.028914737485642595 >
  est32's sampling rms 0.028706524585246775. **The bias exceeds sampling — but
  narrowly (+0.7 %)**, because the total rms is dominated by per-occasion
  sampling noise; the occasion-constant component (where an author-effect bias
  must show) is reported per arm in §2 and is the honest read of this check.
- Common-shift calibration: author-deviation RMS at the response level
  **0.08076103893121582** (per-author mean deviation from the
  within-(context,occasion) norm, RMS over authors × dims, computed on the
  shared design's unshifted world). Post-map displacement, relative Frobenius
  change of the deployed feature panel: 0.5× → M 6.07 %, K 33.15 %;
  1× → M 11.79 %, K 68.25 %; 2× → M 23.46 %, K 151.08 %. **All > 0.**

**G4 PASS.**

### G5 — hygiene

`results/m4_k1_issuer/manifest.json`: master_seed **20260809**; seed recipe
`v8.stable_bucket(f'{MASTER_SEED}-{group}-w{world}-{knob_tag}', salt='m4k1-world', modulus=2**63-1)`;
groups `abs`, `rel`, `pilot`, `g4disp`; shift seeds
`stable_bucket(f'{world_seed}-{occasion_mode}', salt='m4k1-shift')`; biased-arm
seed `stable_bucket(f'{world_seed}', salt='m4k1-biased')`; bootstrap seeds
L2 20260810 / L3 20260812 / L4 20260813. Every stage foreground with an
explicit timeout; **zero background jobs, zero monitors**. Part-0 estimates
used for the "stop at 2× estimate" rule: `abs` ≤ 60 s, `rel` ≤ 600 s.

### Part-0 register-notes (operationalizations, fixed before any arm)

**R-0.1 — R-abs occasion structure.** T3(b)/(c)'s cancellation is a statement
about a *common occasion set*. F2's layout gives authors heterogeneous event
counts {8, 12, 16}, so even in F2's `shared` mode (`f2:96-118`, occasion label
= local index t) authors occupy *nested*, not identical, occasion sets, and no
exact identity exists. R-abs therefore reads a **common occasion window of
N_OCC = 8 occasions per author** — exactly the deployed gauge's own retention
floor (`f2:65`) and the minimum of F2's own m-multiset — applied **identically
to both designs**, so the two designs are exactly budget-matched. Authors/world
stays pinned at F2's 985.

**R-0.2 — the free design needs a finite occasion universe.** F2's `free` mode
is the *fully unshared* limit (globally unique labels, `f2:107-117`), under
which no two authors ever share an occasion and a per-occasion norm is not
estimable at all. T3(e)'s own formula — `mean_{O_i} μ̂ − mean_{O_j} μ̂` —
presupposes a common universe with person-specific subsets. R-abs's free design
therefore draws each author's 8 occasions **without replacement from a common
universe of T_FREE = 64**, which is precisely the alternative F2's own
docstring names and declines ("rather than picking an arbitrary finite
occasion-universe size"). Expected pairwise occasion overlap 8·8/64 = 1;
realized overlap reported per world. The generator body
(`f2.generate_world_composed`, `f2:129-198`) runs **verbatim**; only the object
`f2.occasion_labels` produces is supplied by this leg.

**R-0.3 — one jurisdiction.** The occasion shock is per `(context, occasion)`
(`f2:121-126`), so a norm field is only defined within a context. R-abs is not
the per-context relational gauge and has no context axis; the whole R-abs panel
plus its norm pool live in **one** context (`K1`). Pooling F2's four contexts
would mix four different occasion-shock processes into one "norm".

**R-0.4 — norm pool.** One pool of **512** fresh authors per world, disjoint
from the panel, generated in the **same generator call** as the panel (so they
share the world's loadings and law exactly) and observed on **all 64** universe
occasions. `est8/est32/est128` are **nested prefixes** of that pool.
`biased32` draws 32 uniformly from the **top half (256) by the pool's
author-effect first principal coordinate**, operationalized post-map as PC1 of
the authors' mean event vectors (no generator internals are read).

**R-0.5 — the two readers, and which lean each one adjudicates.** This is the
one place where the registration is genuinely underdetermined, and the choice
was fixed here, before any arm, on a theory argument:

- **Reader B (primary, the deployable reader):**
  `c_i^(h) = mean_{o ∈ H_h}( x_i(o) − μ̂(o) )`. The literal "card = occasion-mean
  deviation": each half subtracts the per-occasion norm on exactly the
  occasions that half is built from. This is what an absolute reader can
  actually do in deployment, and it removes the occasion effect exactly.
- **Reader A (the T3(c)-hypothesis reader):**
  `c_i^(h) = mean_{o ∈ H_h} x_i(o) − mean_{o ∈ O_i} μ̂(o)`. T3(c) does not claim
  invariance for any NN reader — it conditions on **"a common probe/gallery
  norm"**, and reader A is the construction that satisfies that hypothesis
  (one norm vector per author, shared by both halves). Reader B does not
  satisfy it (probe norm `mean_{H_2} μ̂` ≠ gallery norm `mean_{H_1} μ̂`), so
  T3(c) makes no prediction about reader B's NN decisions.

Assignment, fixed in advance: **L1's rank-1 clause is adjudicated on reader A**
(the only reader satisfying T3(c)'s stated hypothesis); **L1's card-difference
clause is adjudicated on both readers** (T3(b) needs no such hypothesis);
**L2, L3, L4 are adjudicated on reader B** (T5 prices the deployable reader).
Both readers are computed and reported for every cell.

Halves are `H_1` = the author's first 4 occasions in ascending order, `H_2` =
the last 4 — which in the shared design is one **common** occasion split for
every author, as T3(b) requires, and in the free design is person-specific.

**R-0.6 — norms actually subtracted.** `cards_for_arm` forms
`dev = panel − mu[labels]` element-wise and averages; no algebraic
simplification is used anywhere. Distances are `scipy.spatial.distance.cdist`
on the resulting cards.

**R-0.7 — L1's two measured quantities.** (i) rank-1 decision flips vs the
oracle arm, excluding probes whose top-2 margin < 1e-6 in either arm (counted
and reported); (ii) card-difference agreement, measured two ways per half:
`max |D_arm − D_oracle| / max D_oracle` on the full 985 × 985 pairwise-distance
matrix, and `max_i ‖e_i − ē‖ / max D_oracle` with `e_i = c_i(arm) − c_i(oracle)`
(the "is the arm difference a pure common translation" form of T3's proof).

**R-0.8 — L5's shift.** `δ(o)` is drawn once per (world, design) as standard
Gaussian per occasion label and scaled to {0.5, 1, 2} × the world's
author-deviation RMS, so the three sizes are nested and maximally paired. It is
added to the event vectors **before** `featurize_panel` (genuinely pre-map).
The calibration RMS is computed on the **shared** design's unshifted world for
both designs (in F2's free mode each occasion has exactly one author, so the
within-occasion deviation is identically zero and cannot calibrate anything).
Disclosed consequence: in F2's fully-unshared free mode the "common" shift
degenerates to independent per-event noise — which is exactly why the
registration made the free-design shift descriptive only.

**R-0.9 — aggregation.** L2/L4 pooled intervals: author-stratified bootstrap,
2000 draws, authors resampled within world, worlds as strata, statistic = mean
over worlds of the world's mean per-probe difference, percentile CI. L3: slope
of log10 Var(μ̂ − μ̂_or) on log10 |P| over {8, 32, 128} pooled over the 8 worlds,
CI by world-level bootstrap (2000 draws). L5: F2's own `_paired_ci` (`f2:1008-1025`)
over the 8 per-world Δ's, exactly as the anchor.

**R-0.10 — pre-compute smoke test, disclosed.** Before Part 0 ran, an
80-author / 64-norm-author smoke configuration was executed to check the code
paths. It confirmed the mechanism the reader split in R-0.5 was derived from
(reader A: 0 flips in all shared-design arms, card-difference 3.1e-16; reader
B: nonzero shared-design flips from the `M_2 − M_1` offset; free design: reader
B oracle > est8, reader A inverted). This is hypothesis-relevant information
and is reported here rather than omitted. The reader assignment in R-0.5 was
derived from T3(c)'s stated hypothesis while the script was being written — an
argument, not a measurement — and the smoke run confirmed it; it was fixed
before Part 0, before the pilot, and before any of the eight worlds existed.

---

## 1. Design as executed

Fresh `master_seed = 20260809`, 8 worlds, F2's knobs
`k48-r0.50-mu0.15-x0.15-e0.70-p0.20_0.80`, κ = 1.0 throughout.

| stage | cells | wall | Part-0 estimate |
|---|---|---|---|
| `part0` | G0–G5 + reserved pilot world 9001 | **1.739 s** | — |
| `abs` | {shared, free} × {oracle, est8, est32, est128, biased32} × 8 worlds | **7.258 s** | ≤ 60 s |
| `rel` | {shared, free} × {0, 0.5, 1, 2}× shift × 8 worlds = 64 deployed-gauge runs | **75.253 s** | ≤ 600 s |
| `finalize` | adjudication | **3.228 s** | — |

**Total compute 87.5 s.** All four stages foreground with explicit timeouts, six
worker processes on the `rel` stage only; **no background jobs, no monitors, no
sleep-and-poll**. No stage came near 2× its Part-0 estimate. Every stage
completed clean on its first attempt. Environment: Python 3.14.3, numpy 2.4.4,
pandas 3.0.2, scipy 1.17.1.

Realized R-abs free-design occasion overlap: **0.997** occasions per author pair
(design target 8·8/64 = 1.0). Shared-design overlap 8/8 by construction.

The `rel` unshifted arms reproduce the F2 regime under the new master seed:
shared κ=1.0 agreement **+0.023805408** (F2's persisted +0.023390489), free
**+0.000272314** (F2's −0.002772774).

## 2. R-abs — the absolute card reader (L1–L4)

Mean rank-1 re-identification over 8 worlds, 985 probes against a 985-card
gallery (chance = 1/985 = 0.00102):

| design | reader | oracle | est8 | est32 | est128 | biased32 |
|---|---|---|---|---|---|---|
| shared | **B** (primary) | .592132 | .517640 | .575127 | .586548 | .573350 |
| shared | **A** (T3(c) hypothesis) | **.460914** | **.460914** | **.460914** | **.460914** | **.460914** |
| free | **B** | .589848 | .492893 | .562817 | .584391 | .565736 |
| free | **A** | .324239 | .374365 | .337437 | .325761 | .334772 |

Norm-field quality, pooled: `Var(μ̂ − μ̂_or)` = 3.158e-03 (est8), 7.84e-04
(est32), 1.55e-04 (est128), 8.63e-04 (biased32). Occasion-constant component of
the norm error (rms): est32 **0.012283**, biased32 **0.015500** in the free
design (+26 %), est32 0.014281 vs biased32 0.017730 in the shared design
(+24 %) — the author-effect bias shows exactly where it must, in the
occasion-constant part, far more clearly than in the total rms that G4's pilot
check used (+0.7 % there, +5.1 % pooled over the eight worlds).

### L1 — designed identity: **HOLD**

- **Rank-1 decisions, reader A (the reader satisfying T3(c)'s "common
  probe/gallery norm" hypothesis): 0 flips.** 0 of 985 probes × 4 non-oracle
  arms × 8 worlds = 0/31,520. **0 ties excluded** (no probe had a top-2 margin
  below 1e-6). Clean in **8/8 worlds**. The shared-design rank-1 rate is
  bit-identical across all five arms at .46091370558375633.
- **Card-difference matrices: exact.** Max relative deviation of the full
  985 × 985 pairwise-distance matrix versus the oracle arm, over both halves,
  all arms, all 8 worlds: **4.0917e-16** (reader A) and **4.1439e-16**
  (reader B) against a 1e-9 tolerance. The "pure common translation" form
  (`max_i ‖e_i − ē‖ / max D`) is 2.616e-15 / 2.525e-15. T3(b) is confirmed at
  machine precision for **both** readers, with the norms genuinely subtracted.
- **Disclosed companion, reader B's rank-1 clause: 5,473 flips.** Reader B
  subtracts a *different* norm from probes (`mean_{H_2} μ̂`) than from the
  gallery (`mean_{H_1} μ̂`), so it violates T3(c)'s hypothesis, and the residual
  arm dependence is the single common offset `M_2 − M_1`. This is not a defect
  and not a counterexample to T3(c): it is a measurement of what T3(c)'s
  hypothesis buys. **A split-half re-identification reader cannot satisfy
  "a common probe/gallery norm" and remove the occasion effect at the same
  time** — that is this leg's first theory-relevant by-product.
- No bug-hunt gate was needed; P1 does not fire.

### L2 — issuer error live and lawful (free design): **HOLD, clean**

Reader B (primary): pooled author-stratified bootstrap, 2000 draws, authors
resampled within world, worlds as strata.

- pooled oracle − est8 = **+0.09695431472081219**,
  95 % CI **[0.08819796954314721, 0.10596763959390862]** — excludes 0.
- per-world means +0.09847715736040609, +0.09441624365482233,
  +0.09035532994923857, +0.07614213197969544, +0.10050761421319797,
  +0.11979695431472082, +0.10659898477157360, +0.08934010152284264 —
  **8/8 positive → "clean"** band.
- Spearman over {est8, est32, est128, oracle} = **1.0 in 6/8** worlds (the
  other two are 0.9486832980505139) → monotonicity clause holds at its ≥6/8 bar.
- The measured effect (0.0970) is **6.3×** G3's MDE (0.0154) and lands within
  4 % of the Part-0 prediction from generator noise ratios alone (0.1013).

**Reader A companion — a reversed-sign finding, reported not buried.** Under
the T3(c)-hypothesis reader the issuer error does not price the card at all;
it **improves** re-identification, monotonically in how bad the issuer is:
pooled oracle − est8 = **−0.05012690355329949**, CI
**[−0.05672588832487309, −0.04378172588832487]**, **0/8** worlds positive,
Spearman −1.0 in 5/8 and −0.8 in 3/8. Mechanism, and it is not subtle: reader A
subtracts one norm vector `mean_{O_i} μ̂` per author, identical in both halves,
so the issuer's sampling error becomes a **person-specific constant that
reproduces across occasion halves** — it cancels from the self-match, inflates
every wrong-match distance, and raises readability. By IDT's own T6
discriminator ("deviation is identity iff it reproduces") this spurious
component *passes* as identity. A worse issuer manufactures a better-looking
card. This is a live warning for T5 and T6, not an artifact of the eight
worlds: it is a structural consequence of the reader, visible in every world.

### L3 — the 1/|P| law (manipulation check): **HOLD**

Pooled log10 Var(μ̂ − μ̂_or) on log10 |P| over {8, 32, 128}, 8 worlds:
slope **−1.0865327686128703**, world-bootstrap 95 % CI
**[−1.0989900747656913, −1.0735206421063670]** — inside the registered
[−1.35, −0.65]. The mild steepening past −1 is the expected `1/P − 1/512`
correction from nesting the est arms inside the oracle pool. Labelled a
manipulation check, as registered; no discovery is claimed.

### L4 — free-design specificity (the T3(e) interaction): **HOLD**

Reader B: (oracle − est8 in FREE) − (oracle − est8 in SHARED) =
**+0.022461928934010153**, CI **[0.011795685279187819, 0.03248730964467005]**,
per-world **7/8 positive** (world 4 is −0.015228426395939087) — exactly at the
registered ≥7/8 bar, no better. The shared-side deficit under reader B is
itself large (+0.074492386): a common-occasion design does **not** make the
issuer free for a split-half reader, it only makes it *cheaper*, by 23 %.

Under reader A the registration's own parenthetical is literally exact: the
shared-side deficit is **0.0** to machine precision (L1), so the interaction
equals the free-side deficit exactly, −0.050127 — and therefore MISSES with the
sign reversed, for the same reason L2's reader-A companion does.

## 3. R-rel — the deployed relational gauge under pre-map common shifts (L5)

Common shift `δ(o)` added to every author's response on occasion o **before**
the frozen map, scaled to {0.5, 1, 2} × each world's own author-deviation RMS
(≈ 0.0808; realized σ 0.0403 / 0.0807 / 0.1614 per world). In card space this
manipulation is **exactly invisible** — μ(o) and x(i,o) move by the same δ(o),
so every deviation, card, card difference and NN decision is unchanged (T3(a),
and L1's machine-precision result is the empirical form of it).

Shared design (the gated arms), paired by world, F2's own `_paired_ci`:

| shift | unshifted | shifted | Δ (paired mean) | 95 % CI | inside ±m? | per-world \|Δ\| < 2m |
|---|---|---|---|---|---|---|
| 0.5× | +0.023805408 | +0.039686549 | **+0.015881141** | [0.003952935, 0.027809348] | **NO** | **3/8** |
| 1× | +0.023805408 | +0.116348456 | **+0.092543049** | [0.057780533, 0.127305564] | **NO** | **0/8** |
| 2× (stress, descriptive) | +0.023805408 | +0.573491923 | +0.549686516 | [0.489791160, 0.609581871] | — | 0/8 |

m = 0.006540815826681557; 2m = 0.013081631653363113.

**L5 MISSES, decisively, and in a direction the registration did not
anticipate.** The failure is not that a little issuer signal leaks through the
nonlinear map. It is that the deployed gauge **amplifies** a common occasion
shift into its own agreement statistic:

- at 0.5× the leak is **2.43×** the equivalence margin;
- at 1× the leak is **+0.0925**, i.e. **3.54× F2's entire composition effect**
  (0.026163263306726227) — the very quantity m was defined as a quarter of;
- at 2× the gauge's agreement rises to +0.573, a 24-fold increase over
  unshifted, from a manipulation that moves no card by one bit.
- per-world Δ is positive in 6/8 (0.5×) and 8/8 (1×, 2×) worlds; the two
  negative 0.5× worlds are −0.001154 and −0.000636, i.e. noise-scale.

This is exactly what **G2's branch B** predicted before the run: the gauge never
forms within-occasion between-author contrasts (`v8:229`, `v8:239-240`,
`v8:246`, `v8:258`), so norm position enters at first order, and a *shared*
occasion perturbation is structurally the same object as F2's own κ shock — the
gauge reads "the issuer moved" and "a new shared-occasion signal appeared" as
the same event. G4 had already shown the shift lands post-map (relative
Frobenius change of the deployed feature panel at 1×: M 11.79 %, K 68.25 %).

Free design (descriptive, no gate — and note that in F2's fully-unshared free
mode the "common" shift degenerates to independent per-event noise, R-0.8):
Δ = −0.000475471 (CI [−0.003784609, +0.002833667]) at 0.5×, −0.002650640
(CI [−0.006828030, +0.001526750]) at 1×, −0.004512747 (CI [−0.007458419,
−0.001567074]) at 2×; per-world |Δ| < 2m in **8/8** at every size. So the free
design's agreement is nearly inert to the same perturbation that moves the
shared design by up to +0.55 — the amplification is specific to the design in
which occasions are shared, which is the design F2's composition finding
recommends.

## 4. Pivot status, checked mechanically

| pivot | registered rule | fires? |
|---|---|---|
| **P1** | L1 fails after the bug-hunt gate → leg VOID | **NO** (L1 HOLD, 0 flips, 4.1e-16) |
| **P2** | L2 fails with a G4-verified live channel → T5's price demoted to sub-MDE | **NO** (L2 HOLD; channel verified live: |P| ordering + 361 pilot flips) |
| **P3** | **L5 fails → T3(f)'s idealization is DEAD for the deployed gauge; K1b (decomposing F2's composition effect into issuer-error vs jurisdiction-misalignment shares) becomes the next registration INSTEAD of K2, and the theory doc's F2 retrodiction row is annotated, not rewritten** | **YES — FIRES** |
| **P4** | L4 fails while L1/L2 hold → re-audit; if clean, theory hit on T3(e) | **NO** (L4 HOLD at 7/8) |

## 5. Verdict

**`CARD_SPACE_CANCELLATION_EXACT__DEPLOYED_GAUGE_AMPLIFIES_THE_COMMON_SHIFT__T3f_DEAD__K1b_REPLACES_K2`**

Four of five leans hold. T3(a)–(e) survive contact with the machinery at
machine precision and with the registered signs: the designed cancellation is
exact (0/31,520 flips, 4.1e-16), the issuer's price on a deployable absolute
reader is large, lawful and monotone in |P| (+0.0970, 6.3× MDE, 8/8 clean,
1/|P| slope −1.087), and it is free-design-specific (+0.0225, 7/8). T3(f) — the
one clause the theory itself flagged as an idealization to be TESTED — is dead:
the deployed relational gauge does not merely fail to inherit the immunity, it
converts a card-space-invisible common shift into a **positive** agreement
signal 3.5× the size of the composition effect F2 measured with that same
statistic. The verdict slug was written after adjudication; every number above
was produced by the registered rules.

Two by-products the registration did not ask for and this report does not hide:
(i) a split-half re-identification reader cannot simultaneously satisfy T3(c)'s
"common probe/gallery norm" hypothesis and remove the occasion effect; (ii)
under the reader that *does* satisfy that hypothesis, issuer sampling error
becomes a person-stable, occasion-half-reproducible component that **improves**
re-identification (−0.0501, 0/8, CI excluding zero) — a forged identity that
passes T6's own reproducibility discriminator.

## 6. Anomalies, with their timing relative to hypothesis-relevant numbers

1. **The registration underdetermined R-abs's norm-subtraction convention.**
   T3(c) conditions on "a common probe/gallery norm"; a split-half card reader
   admits two inequivalent constructions (R-0.5). Resolved **before** any
   number from the eight adjudicated worlds and **before** the pilot: the
   assignment was derived from T3(c)'s stated hypothesis while the script was
   being written, and both readers are computed and reported for every cell.
   An 80-author smoke configuration run before Part 0 confirmed the mechanism;
   that smoke run is itself hypothesis-relevant and is disclosed in R-0.10 with
   its numbers.
2. **F2's free mode makes a per-occasion norm inestimable** (fully-unshared
   limit). Resolved before any run by the finite universe T_FREE = 64 (R-0.2),
   which F2's own docstring names as the alternative it declined.
3. **G4's `bias_exceeds_sampling` check passed narrowly on the pilot** (+0.7 %
   in total rms). Noted at Part-0 time, before arms. The eight-world data show
   the bias signature where it belongs — +24 to +26 % in the occasion-constant
   component — so the check is satisfied substantively, not just nominally.
4. **No mechanical failures.** Every stage completed clean on the first
   attempt; no stage was re-run except `finalize`, which was re-run once purely
   to record a more accurate verdict slug (the adjudication numbers are
   deterministic and identical across both runs).
5. **`f2.MASTER_SEED` is overridden to 20260809 inside the `rel` worker**, and
   `f2.occasion_labels` is temporarily replaced inside the R-abs world builder.
   Both are disclosed patches of a single named object; the generator and gauge
   bodies run verbatim.

## 7. Hand-off

Per P3, **K1b replaces K2 as the next registration**: decompose F2's
composition effect (+0.026163263306726227) into issuer-error and
jurisdiction-misalignment shares, now knowing that the statistic used to
measure it responds +0.092543 to a common occasion shift that is invisible to
every card. The theory doc's F2 retrodiction row is to be **annotated, not
rewritten**, and T3(f) recorded as decided against on the deployed gauge with
branch B's first-order mechanism named. The K3 charter (T7/T8) is untouched.
