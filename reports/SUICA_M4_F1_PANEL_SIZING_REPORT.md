# SUICA M4-F1 — The D3 Panel Sizing Law (author-axis vs events-axis scaling of the field's own agreement gauge)

> **BANNER: synthetic worlds calibrated to an opened-panel regime, exploratory.**
> This leg consumes NO new real-text evidence. The real-text quantities used for
> calibration (effective ranks, internal-agreement level, panel shapes, the
> per-author event-count distribution) are read from artifacts already persisted
> by the V8 realtext route and M4-E1, plus one label-free re-read of the already
> opened PANDORA panel through the deployed loader (author/body/created_utc/
> subreddit only; the M4-E1 precedent) to extract the exact per-author event-count
> multiset. No label columns anywhere; no fresh-panel claim; nothing here
> certifies the real relation field.

Registered spec: `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md` section
M4-F1 (registered 2026-08-02 before run, loop cycle 12). Script:
`scripts/run_suica_m4_f1_panel_sizing.py`. Artifacts:
`results/m4_f1_panel_sizing/`.

## Part 0 — REGISTERED ADJUDICATIONS AND OPERATIONALIZATIONS (written before the run)

### 0.1 The real-text regime to be reproduced (verified from persisted artifacts)

From `results/v8_realtext_relation_field/discovery_20260805/` and
`results/m4_e1_convention_gap/` (all re-checked in this session):

- PANDORA D-panel: 985 authors / 13,202 events / splits D0 420, D1 296, D2 269;
  4 contexts; split-by-context author table D0 = 110/113/96/101 and
  D1 = 88/63/68/77, D2 = 62/65/67/75 (AskReddit/AskWomen/politics/worldnews
  column order as persisted).
- Events per author m in {8,10,12,14,16}, histogram 152/120/111/89/513, mean
  13.40 (full panel) and 13.35 on the 565 opened D1+D2 eval authors (7,542
  events); 61.1% of eval authors have m >= 14. Persisted this session as
  `results/m4_f1_panel_sizing/realtext_panel_reference.json` (exact
  per-(split,context) m multisets).
- D0 soft-calibration effective ranks at full budget: M 42.17, K 38.53
  (Essays 42.24/41.67 — PANDORA is the calibration target; the registered range
  "~39-42" spans the persisted PANDORA pair).
- Quarter-budget K collapse: b = 4 events/author drives the K-family D0
  effective rank to 8.48 (PANDORA) — the deployed map is strongly NONLINEAR in
  path length at the short end (a 4-event path leaves one transition pair per
  replicate).
- Internal split-half agreement of the deployed penalty-free field at current
  scale: -0.0082 (sd 0.0219, 24 draws, 565 authors) at full budget; -0.0073
  (sd 0.0307) at the half budget; zero within noise everywhere measurable
  (M4-E1's saturated yardstick).

### 0.2 Generator adjudication (the registered "state your choice and why")

The registered machinery names two generator families: the V8 relation-field
worlds (`suica_core/v8_context_relation_field.simulate_context_relation_world`,
the synthetic counterpart of the realtext relation-field script) and the M3
cross-family worlds (`suica_core/m3_cross_family_generator.
generate_m3_cross_family_world`). Adjudicated against the two registered
requirements — (i) the field's own internal split-half agreement gauge must be
reusable as implemented in M4-E1, and (ii) the calibration must be able to reach
the observed real-text regime — BEFORE any compute:

1. **The M4-E1 gauge halves each author's EVENTS.** It exists only for worlds
   that expose an ordered per-author event stream feeding the deployed frozen
   feature map (`build_feature_panel`: alternating source-disjoint replicates,
   frozen random directions, 16-draw transition-null subtraction). The V8
   HJIC world generator emits post-feature two-view panels with no events at
   all: the E1 gauge cannot be applied to it, and its events/author axis could
   only be swept by INJECTING a modeled view-noise map (for example
   sd ~ 1/sqrt(events)) — which would inject the very events-axis exponent that
   lean (b) is supposed to measure, and which the persisted diagnostics already
   contradict at the short end (K effective rank 38.5 -> 8.5 at b = 4: the
   deployed map's noise is not a smooth 1/sqrt(E) in the swept regime).
   Verdict: the world must be EVENT-LEVEL and the deployed map must be the
   feature map.
2. **No verbatim M3 world can reach the support regime.** The M3 path worlds
   carry scalar author parameters by deliberate design (their audit constraint
   fixes population lag-0:2 covariance and low-order moments across authors), so
   the author-consistent replicated covariance they induce through the deployed
   map has effective rank ~1-3, not ~39-42. Widening them to per-dimension
   parameters fails structurally: with 64 independent per-dim carriers, every
   projection-based feature of the deployed map (RFF phases, quantile
   projections, transition RFF, currents) is a 64-term sum and goes Gaussian by
   CLT — per-dim fourth-moment signals (ARCH) wash out; and the M3 hsmm/cycle
   carriers are M-invisible by construction (author-invariant marginals), which
   would leave a zero M<->K relation field.
3. **Adjudication under the registered escape clause** ("if calibration cannot
   reach the regime, report that honestly and adjudicate what it means before
   proceeding"): no existing generator VERBATIM satisfies both requirements.
   The minimal member of the registered machinery family that does is the
   composition of the two: the V8 relation-field world STRUCTURE (shared
   per-author latent, orthonormal loadings, the HJIC strength-taper profile,
   explicit noise knobs) LIFTED to event level, with the order-sensitive family
   carried by per-factor latent AR(1) state chains — the minimal order-sensitive
   carrier that survives the deployed map's projections (second-moment lag
   structure is per-dimension-visible in the lag/delta blocks and
   projection-stable in the transition-RFF block, unlike per-dim fourth-moment
   carriers). This composed world is registered here as `M4F1RelationWorld`;
   every conclusion carries the caveat that it is a composition of the two
   registered generator families, not a verbatim reuse of either. The honest
   meaning of the failed verbatim calibration is itself recorded as a finding:
   the real-text support regime (effective rank ~40) implies HIGH-DIMENSIONAL
   author-consistent structure that no single-parameter world reproduces.

### 0.3 The composed world (exact equations, registered before compute)

Author i (context c_i fixed by the panel layout of 0.4; latent dimension k;
factor index b = 1..k; event index t = 1..m_i):

- z_i ~ N(0, I_k): persistent author latent (the HJIC shared latent).
- phi_i(b) = phi_lo + (phi_hi - phi_lo) * sigmoid(rho * z_i[b] +
  sqrt(1 - rho^2) * zeta_i[b]), zeta_i ~ N(0, I_k): per-factor AR coefficient —
  the order-sensitive author parameter, correlated with z_i through rho (the
  relation knob; same-latent-two-families is the HJIC relation structure).
- x_t(b) = phi_i(b) * x_{t-1}(b) + sqrt(1 - phi_i(b)^2) * e_t(b),
  e_t ~ N(0, I_k), x_0 ~ N(0, I_k): stationary unit-variance latent state
  chains (the event-level order carrier).
- Event vector (dimension 64 = the deployed map's event dimension):
  v_t = sqrt(w_mu) * L (g o z_i) * a + sqrt(w_x) * L (g o x_t) * a +
  sqrt(w_e) * sigma_iso * eps_t, eps_t ~ N(0, I_64), where L = 64 x k
  orthonormal loadings (HJIC `_orthonormal_loadings`, fresh per replicate
  world), g = linspace(.85, .55, k) (the HJIC left-strength profile),
  o = elementwise product, and (a, sigma_iso) are fixed normalizers chosen so
  that E||v||^2 = 2 exactly (the real frozen event vectors are two unit-norm
  hash blocks, norm sqrt(2)) with variance shares (w_mu, w_x, w_e) summing
  to 1: a^2 = 2 / sum(g^2), sigma_iso^2 = 2/64.
- Replicates, feature families M/K, transition-null subtraction, D0/D1/D2
  panel semantics: the DEPLOYED map exactly (Part 0.5 gates).

Free calibration knobs: k, rho, (w_mu, w_x, w_e), (phi_lo, phi_hi). Fixed by
matching (not tuned): event norm sqrt(2); panel layout (0.4). The world's
relation field is context-invariant (contexts partition authors only); the
sizing law is therefore measured for a context-invariant field — disclosed
scope, since the gauge estimates each context's field separately and averages
their split-half cosines exactly as in M4-E1.

### 0.4 Panel layout, axes, and cells

- Current-scale (1x) panel: the EXACT persisted split-by-context author table
  (420/296/269 by the persisted per-context counts) and the EXACT per-
  (split,context) m multisets from `realtext_panel_reference.json`. Split
  assignment is direct (the persisted counts), bypassing the deployed hash
  assigner — disclosed: shape fidelity is the registered target ("matched
  author count and events/author to the real D1/D2 panels").
- Author axis x{2,4,8}: every split-by-context count multiplied by the factor;
  each cell's m multiset tiled by the factor (events/author distribution held
  exactly fixed). D0 grows with the panel (the deployed pipeline recalibrates
  D0 per panel, as M4-E1 did per budget).
- Events axis x{2,4,8}: author table fixed at 1x; every author's m multiplied
  by the factor (m in [8,16] -> [16,32] -> ... ). The AR chain runs over the
  full ordered stream; alternating replicates share it (the real
  SOURCE_COMMENT_DISJOINT_TECHNICAL semantics).
- Held-out validation cell: events x16 (the cheaper axis both computationally
  and for D3 collection — extending existing authors' streams vs recruiting
  8x authors), computed AFTER the law is fitted and its prediction persisted
  (ordering timestamped in decision.json).
- >= 8 replicate worlds per cell (fresh seeds: z, zeta, chains, noise,
  loadings L all fresh; knob values frozen at the calibrated point); 20
  split-half draws per world (registered floor >= 20; E1 used 24 — 20 chosen
  for budget, above the registered floor).

### 0.5 Estimator and gauge (deployed objects, equality-gated)

- Feature map: a BATCHED reimplementation of `build_feature_panel` /
  `family_features` (needed for compute feasibility), gated at startup against
  the deployed functions on a probe world: max abs feature difference must be
  < 1e-9 (identical algebra, floating-point reduction order may differ). The
  per-(author,offset) transition-null RNG streams are reproduced exactly
  (same `stable_bucket` construction, same 16 sequential `permutation` calls).
- D0 soft calibration, soft projection, deployed penalty-free per-context
  field, and the weighted matrix-cosine agreement: imported VERBATIM from the
  M4-E1 script (`calibrate_d0_soft`, `project_soft`, `deployed_soft_field`,
  `field_agreement`) on top of `v8.soft_relation_matrix` / `v8._matrix_cosine`.
- Split-half gauge: M4-E1 semantics — per draw, each retained author's events
  (b >= 8 required; all authors qualify at 1x since min m = 8) are seeded-
  randomly halved with time order restored; both halves featurized by the
  deployed map; both projected through the WORLD's frozen D0 calibration;
  per-context deployed fields; weighted matrix cosine with first-half context
  weights. The halving is reimplemented in numpy for speed and gated at
  startup against E1's `split_half_frames` (identical selected event indices
  on a probe world; the E1 seed construction `stable_bucket(f"{corpus}-
  {author}-{budget_label}-{draw}", salt="m4e1-half-perm")` is reused
  verbatim with corpus = the world's unique id).
- Resolved contexts: the pipeline's own floor (12 authors per context on the
  eval panel), as deployed. Eval panel = D1+D2 authors in resolved contexts.

### 0.6 Calibration protocol and acceptance bars

Search on the 1x panel (one world per trial, 12 draws) over
(k, rho, w_mu, w_x, w_e, phi range), targeting:

- D0 M effective rank in [39.2, 45.2] (42.17 +/- 3);
- D0 K effective rank in [35.5, 41.5] (38.53 +/- 3);
- internal agreement zero within the E1 band: |mean| <= 0.02 AND |t| <= 2.5
  against zero over the trial draws.

The calibrated point is then verified on the full 1x cell (8 worlds x 20
draws): the three bars must hold on the pooled cell values (agreement bar on
the cell mean with SE across worlds). All trials, accepted or not, are
persisted in `calibration_record.json` with their measured diagnostics.
Companion diagnostic (no acceptance bar, echo of the real regime): the
quarter-budget K effective-rank collapse (b(m, 1/4) per E1's `_budget_size`)
is measured at the calibrated point and reported next to the real 8.48. If NO
knob setting reaches the bars, the registered escape fires: report honestly,
adjudicate, and stop before the sweep.

### 0.7 Fit form (the registered-equivalent form, stated), leans, pivot

Per-world agreement A_w = mean over 20 draws of the draw-level weighted matrix
cosine; cell mean A = mean over worlds; SE = sd over worlds / sqrt(R).

- **Rise criterion (per cell):** A > 0 and A / SE >= 2 (one-sided).
- **Fit form:** under the split-half model A = SNR/(1+SNR), the distance-from-
  floor measure is the odds A/(1-A) (floor = zero agreement, the calibrated
  current-scale value = the E1-measured real level). Per axis, weighted least
  squares of log10(odds(A)) on log10(mult) over QUALIFYING cells (A > 0 and
  A - 2*SE > 0), weights = delta-method 1/Var(log10 odds); mult in {1,2,4,8}
  with the 1x cell shared between axes. An axis is FITTABLE with >= 3
  qualifying cells; a 2-cell fit is reported as DEGENERATE (slope only, no CI,
  cannot support lean (c)). Uncertainty: bootstrap over worlds within cells
  (2,000 resamples), refit, percentile CIs for exponents and the budget.
- **Exponents:** gamma_authors, gamma_events = the fitted slopes (power-law
  exponents in the odds domain).
- **.5-agreement budget:** odds = 1 at A = .5, so mult* = 10^(-beta/gamma) on
  the dominant axis (the larger fitted exponent; if only one axis is fittable,
  that axis).
- **Held-out validation:** predicted log-odds at events x16 from the events-
  axis law, persisted BEFORE the 16x cell is computed; the cell passes if
  |log10(odds_obs) - log10(odds_pred)| <= log10(2) (factor-2 band in the odds
  = distance-from-floor domain). If the observed 16x cell fails the rise
  criterion while the law predicts odds far from floor, validation fails.
- **Lean (a):** at least one swept cell (mult >= 2) passes the rise criterion.
- **Lean (b):** both axes fittable and gamma_authors > gamma_events; if the
  events axis is fittable and the author axis never rises, (b) is a MISS; if
  the author axis is fittable and the events axis never rises, (b) HOLDS; if
  neither axis is fittable, (b) is NOT MEASURABLE (pivot territory).
- **Lean (c):** mult* in [4, 50] on the dominant axis AND the 16x held-out
  cell passes the factor-2 band. A DEGENERATE fit cannot support a (c) hold.
- **PIVOT-IF (registered):** agreement stays ~0 at the largest swept cells —
  operationalized: BOTH 8x cells (author-axis and events-axis) fail the rise
  criterion. Then SIZE-ONLY RESCUE FALSIFIED and the registered hand-off is
  recorded: the D3 design question becomes COMPOSITION (shared-context
  events, within-author condition pairing), not scale. The 16x probe is run
  regardless and reported (as a probe, not a validation) in the pivot case.

### 0.8 Seeds, budget, environment

Master seed 20260802 with `m4f1-*` salts throughout (stable-bucket-derived
per-(cell, world) seeds; the E1 salt namespace is disjoint by the corpus
string, which here is the world id `m4f1-<cell>-w<r>`). The V8 spec seed
20260805 governs the frozen feature-map directions, untouched. All compute
foreground, single machine, multiprocessing over (cell, world) tasks; equality
gates run in the parent before any dispatch. Registered budgets: 8 worlds per
cell, 20 draws per world, >= 20 splits satisfied; 12-draw trials during
calibration search only.

*(Results below this line were appended after the run; nothing above was
edited after compute began.)*

---

## Part 1 — OUTCOME

**1/3 leans (a); the registered pivot does NOT fire — agreement rises off zero
on BOTH axes — but the measured law kills size-only rescue anyway: the fitted
events-axis exponent is 0.153 and the extrapolated .5-agreement budget is
10^14.0x current scale (bootstrap 2.5th percentile 10^2.19 ~ 155x — still
above the registered 50x feasibility band edge); the degenerate author-axis
companion slope (0.404) extrapolates to 5.8e5x. The held-out events-x16 cell
validates the fitted law within factor-2 (obs .0123 vs pred .0107, log-odds
gap .060 vs band .301). Practical conclusion for D3: the same hand-off the
pivot would have issued — COMPOSITION, not scale — reached via a measured
sizing law instead of a flat floor.**

Verdict string: `PANEL_SIZING_LAW_MEASURED_DOMINANT_AXIS_EVENTS` (the events
axis is the only FITTED axis; the author axis is DEGENERATE per the
registered >= 3-qualifying-cell rule).

Run: 8 cells x 8 worlds x 20 draws (+ 15 calibration trials at 12 draws),
3,656 world-seconds total compute, 6-way multiprocessed, seeds as registered.
Prediction persisted 06:43:37Z, holdout computed after, decision 06:48:07Z.

## Equality gates (all green, before any dispatch)

- Batched deployed feature map vs `v8.build_feature_panel` on a probe world:
  max abs diff M = 0.0, K = 0.0 (bit-identical, stronger than the registered
  1e-9 bar; identical per-(author,offset) transition-null RNG streams).
- Numpy halving vs M4-E1 `split_half_frames`: 120/120 author-draw checks,
  identical event indices.

## Calibration (status CALIBRATED, 15 stage-A trials, no stage B needed)

Selected knobs: k = 48, rho = 0.5, variance shares (w_mu, w_x, w_e) =
(.15, .15, .70), phi in [.2, .8]. Trial diagnostics: effM 44.9, effK 39.7,
agreement +.0137 (t 2.39). **Verification on the full 1x cell (8 worlds x 20
draws): effM 42.61 (target 42.17 +/- 3), effK 39.64 (target 38.53 +/- 3),
agreement +.0047 (SE .0046, t 1.03) — all three registered bars hold.**
Companion regime echo (not targeted, not a bar): the quarter-budget K
effective-rank collapse reproduces at 7.7-9.1 vs the real 8.48 — the composed
world inherits the deployed map's short-path nonlinearity. The registered
honest note stands: NO verbatim single-parameter M3 world can reach the
~40-dim support regime (Part 0.2); the real-text support level itself implies
high-dimensional author-consistent structure.

## The two scaling curves (8 worlds per cell; mean agreement, SE over worlds)

| cell | mult | agreement | SE | rises (mean/SE >= 2) | qualifies for fit |
|---|---|---|---|---|---|
| base1x (shared) | 1 | .00473 | .00459 | no | no |
| authors_x2 | 2 | .00472 | .00289 | no | no |
| authors_x4 | 4 | .00811 | .00202 | yes | yes |
| authors_x8 | 8 | .01070 | .00287 | yes | yes |
| events_x2 | 2 | .00798 | .00271 | yes | yes |
| events_x4 | 4 | .00832 | .00299 | yes | yes |
| events_x8 | 8 | .00990 | .00385 | yes | yes |
| events_x16 (held out) | 16 | .01229 | .00369 | yes | (validation only) |

Fits (log10 odds vs log10 mult, WLS per Part 0.7):

- **Events axis: FITTED** (3 qualifying cells). gamma_events = **0.153**
  (bootstrap 95% CI [.021, 1.219]; 590/2000 resamples unfittable-or-
  nonpositive, disclosed), intercept -2.149. .5-agreement budget =
  **10^14.03 x** current events/author (CI [10^2.19, 10^95.9], capped at
  10^300); even the optimistic CI edge (~155x) exceeds the registered [4, 50]
  feasibility band.
- **Author axis: DEGENERATE** (2 qualifying cells — mult 1 and 2 do not
  qualify; slope reported as companion only, no CI licensed). gamma_authors =
  **0.404**, extrapolated budget 5.8e5x.

## Held-out validation (events x16, computed after the prediction was persisted)

Predicted A = .01072 (log10 odds -1.965); observed A = .01229 (SE .0037,
log10 odds -1.905). |log-odds gap| = .060 <= log10(2) = .301 — **within the
factor-2 band; the fitted events law extrapolates correctly to 16x.**

## Per-lean adjudication

- **Lean (a) HOLD**: agreement rises off zero within the swept range — five
  swept cells pass the rise criterion (authors x4/x8, events x2/x4/x8);
  authors_x8 t = 3.7, events_x8 t = 2.6. The calibrated worlds are not stuck
  at an exact floor.
- **Lean (b) MISS** (registered standard): the author axis is not FITTABLE
  under the registered >= 3-qualifying-cell rule (its 1x and 2x cells sit at
  the floor: .00473 -> .00472, exactly flat), so the exponent comparison
  cannot be demonstrated at registered strength. Companion observation
  (no adjudication weight): the degenerate author slope 0.404 exceeds the
  fitted events slope 0.153 — pointing the lean's way, consistent with the
  pairwise-object prediction becoming visible only above ~2x authors.
- **Lean (c) MISS**: dominant (only FITTED) axis = events; .5-agreement
  budget 10^14x is outside [4, 50] by ~12 orders of magnitude (and the
  bootstrap lower edge ~155x is still outside). The holdout HALF of the
  conjunction passes (within factor-2); the band half fails decisively.
- **PIVOT does NOT fire** (registered rule: both 8x cells stay ~0): both 8x
  cells rise off zero. The registered composition hand-off is therefore NOT
  issued by the pivot; see the practical corollary below, which reaches the
  same design decision via the measured law.

## What the law says (interpretation, hedged)

The gauge's SNR grows far more slowly than independent-noise averaging would
predict (naive CLT expectation: gamma ~ 1 on authors, gamma in [1, 2] on
events; measured: 0.15 events / 0.40-degenerate authors). Two world-anatomy
readings, offered as interpretation, not adjudication: (i) on the events
axis, longer streams sharpen the per-half features but simultaneously
dissolve the realized-state heterogeneity that the finite panel's field
partly rides on — signal and noise shrink together, netting a weak exponent;
(ii) on the author axis, the flat 1x->2x segment followed by a rising 4x->8x
segment is the signature of a crossover from a spurious-panel-field-dominated
regime (agreement independent of n) toward the true-relation regime
(agreement ~ n) — the pairwise-object advantage exists but only begins to
express above ~2x current authors, too late to make size-only rescue
feasible.

## Honest anomalies and disclosures

1. **The pivot letter vs the practical verdict.** The registered pivot
   ("agreement stays ~0") did not fire, so SIZE-ONLY RESCUE FALSIFIED is NOT
   the adjudicated verdict. The practical D3 conclusion is nevertheless the
   same as the pivot's hand-off: with a validated events-axis law
   extrapolating to 10^14x (CI edge 155x) and a degenerate author law at
   5.8e5x, no feasible D3 panel reaches .5 agreement by scale alone. The D3
   design question moves to COMPOSITION (shared-context events, within-author
   condition pairing) as a measured-law corollary, not a fired pivot.
2. **Adjudication-code correction before the predict stage** (disclosed): the
   draft script treated DEGENERATE 2-cell fits as fittable for lean (b) and
   dominance, contradicting Part 0.7's letter; corrected to the registered
   text after the sweep artifacts were persisted and before the fits/
   adjudication ran. Sweep data untouched.
3. **Regime drift across cells** (deployed semantics, disclosed): the
   per-panel D0 recalibration shifts effective ranks along the axes — effK
   rises to ~43.4 at authors x8 and falls to ~32.3 at events x8/x16; effM
   falls to ~37.8 at events x16, slipping below the 1x calibration band. The
   bands were calibration bars at 1x, not sweep constraints; the drift is a
   property of the deployed pipeline's recalibration and is reported, not
   corrected.
4. **Bootstrap fragility of the law**: 26-30% of resamples per axis were
   unfittable or non-positive-slope; the exponent CIs are wide ([.02, 1.22]
   events). The budget's order of magnitude is unstable; its INFEASIBILITY is
   stable (the CI never enters [4, 50]).
5. **Author-axis 1x->2x exact flatness** (.00473 -> .00472) is within noise
   (SEs .0046/.0029) — read as floor, not as a measured decline.
6. **Context-invariant world**: the sizing law is measured for a
   context-invariant relation field (Part 0.3 disclosure); per-context
   heterogeneity could only slow convergence further (smaller effective n per
   context), so the infeasibility conclusion is, if anything, conservative.
7. **Composed generator caveat** (Part 0.2): the world is a registered
   composition of the V8-HJIC relation-field structure and event-level
   order-sensitive dynamics through the deployed map — not a verbatim reuse
   of either named generator; no verbatim generator can reach the registered
   regime, and that impossibility is itself part of the finding.

## Decision boundary

Exploratory, synthetic-calibrated. This leg licenses a D3 panel-size DESIGN
prior — the measured statement that split-half field agreement at the
deployed estimator's own gauge grows with exponents ~0.15 (events) / ~0.4
(authors, degenerate) from the calibrated current-scale regime, and that a
.5-agreement panel is not reachable by feasible scaling on either axis. It
makes no claim about the real relation field's content, about personality,
emotion, diagnosis, or any individual, and does not certify (or refute) any
real-text relation structure. Artifacts:
`results/m4_f1_panel_sizing/{decision.json, cells.csv, cell_*.csv, draws_*.csv,
calibration_record.json, prediction_16x.json, gates.json,
realtext_panel_reference.json}`.
