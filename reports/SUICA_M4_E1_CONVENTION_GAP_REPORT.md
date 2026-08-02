# SUICA M4-E1 — Convention Gap on Real-Text Relation Fields

> **BANNER: opened-panel adaptive chain, exploratory.** The D1/D2 real-text panels
> consumed here were opened by the V8 realtext route and are part of the route's
> declared adaptive exploratory chain (route index section 7 item 1). No
> fresh-panel confirmatory claim is made or licensed by this report. Label-free
> throughout: PANDORA = frozen `tier_u_comments.parquet` via the existing V8
> loaders only (columns author/body/created_utc/subreddit); Essays read text-only
> (usecols `user_id,text`, the V6-E2 precedent); no label columns anywhere.

Registered spec: `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md` section
M4-E1 (registered 2026-08-02 before run, loop cycle 10). Script:
`scripts/run_suica_m4_e1_convention_gap.py`. Artifacts:
`results/m4_e1_convention_gap/`.

## Part 0 — REGISTERED KNOB ADJUDICATION (written before the run)

The registered design asks where a ridge/penalty convention enters the V8
real-text relation-field estimate, and directs: if the estimator is penalty-free,
say so, adjudicate the closest convention knob, and register-note the
substitution before running. Findings from code inspection
(`suica_core/v8_realtext_relation_field.py`), before any compute:

1. **The deployed real-text relation-field estimator is penalty-free.** The
   evaluation path (`evaluate_corpus_local`) builds the field per context as
   `soft_relation_matrix(left, right)` on `project_family_soft` projections:
   a positive-part density filter (`_positive_density` -> `_density_sqrt`,
   clip-at-zero, trace-one) followed by a cross-replicate covariance normalized
   by positive-part energies. No lambda appears anywhere on this path.
2. **Where the module's one penalty parameter actually lives.** `spec.ridge =
   1e-5` enters (a) the hard-path whitener `fit_family_support` ->
   `_inverse_sqrt(replicated_covariance(projected), ridge=spec.ridge)`, consumed
   only by the hard whitened estimator `relation_matrix(left, right,
   left_whitener, right_whitener)`; and (b) the alias-audit ridge regression
   (`_fit_alias_audit`), which is a licensing gate, not the field. In the hard
   path the ridge is a *relative eigenvalue floor* (`clip(values, ridge *
   max(values))`): after rank truncation to the top-rank basis the retained
   eigenvalues are O(1) (persisted kth eigenvalues 1.17-1.62 on PANDORA) against
   a floor of 1e-5 x lambda_max, so **the deployed hard-path ridge never binds at
   these ranks** — conventions (i) and (ii) would be bit-identical through that
   knob. The V8 realtext run additionally never licensed the hard path (all
   supports SOFT).
3. **Substituted knob (registered here, before the run):** the module's own
   whitened relation estimator applied in the *full soft-projected space*, where
   the relative floor genuinely binds. Per corpus, per event budget, per
   convention lambda:
   - D0-frozen soft calibration per family F in {M, K}: standardizer center/scale
     (`_fit_standardizer`) + soft filter (`_density_sqrt` of the positive-part
     density of the D0 replicated covariance) — exactly the deployed
     representation, refit per budget on the budgeted D0 events, **shared
     bit-identically by both conventions**.
   - Pooled evaluation panel (opened D1+D2 authors, resolved contexts at the
     pipeline's own floor `minimum_context_authors = 12` on the pooled panel):
     Sigma_F = `replicated_covariance`(proj_F[:,0], proj_F[:,1]); whitener
     W_F(lambda) = `_inverse_sqrt`(Sigma_F, ridge=lambda) — the module's own
     regularized inverse square root with its own relative-floor convention.
   - Field: J_c(lambda) = W_M(lambda) @ C_c @ W_K(lambda) per resolved context c,
     with C_c = `_soft_cross_covariance` on context c — the module's
     `relation_matrix` algebra with pooled-panel whiteners (mirroring the macro
     decomposition's pooled-denominator convention; one penalty per fit, as in
     the arc's V2 field).
   This is a **variant estimator**, not the deployed one; every conclusion below
   carries that caveat. The deployed penalty-free soft field is also run as a
   labeled reference row (`penalty_free_deployed`), outside the leans.
4. **The two conventions.**
   - (i) V2/default: lambda = 1e-5 (the module's `spec.ridge` default), constant
     in n — the penalty floor does not vanish as the event budget grows (the
     arc's Leg 4/Leg 8 V2 semantics).
   - (ii) lambda~1/n: lambda(n) = 1e-5 x (n_quarter / n), with n = pooled
     evaluation-panel event count at the budget and n_quarter its value at the
     1/4 budget. Anchored at the smallest registered budget so the conventions
     coincide where data is scarcest and diverge as n grows; anchoring at full n
     would make the primary detector (gap at full n) identically zero by
     construction, contradicting the registered leans. Consequence, disclosed:
     gap(1/4) = 0 by construction; informative gap rows are 1/2 and 1.
5. **Comparison statistic (the field's own).** Matrix cosine `_matrix_cosine` —
   the statistic the V8 pipeline itself uses to compare relation fields (its
   D1/D2 `matrix_cosine` agreement) — aggregated over resolved contexts by
   author-share weights: agreement(F, F') = sum_c w_c cos(J_c, J'_c);
   disagreement = 1 - agreement. Matrix cosine is scale-invariant per context,
   so no relation denominator is needed on the whitened variant.
6. **Event budgets** {1/4, 1/2, 1}: author-stratified, seeded, nested. Per author
   with m loaded events (time-ordered, already `_spread_events`-capped at 16 for
   PANDORA / 8 chunks for Essays): b(f) = min(m, max(4, 2*int(f*m/2 + 0.5)))
   (even, >= 4 — the frozen feature map needs >= 2 events per replicate path);
   nesting via one seeded per-author permutation shared across fractions
   (selection = first b indices, re-sorted to time order). b(1) = m exactly
   (full budget = the untouched opened panel; asserted). Achieved fractions are
   reported; the floor makes the PANDORA quarter coarser than nominal (m in
   [8,16] -> b(1/4) = 4) and makes Essays quarter == half (m = 8 -> b = 4 both);
   both disclosed as design facts, not findings.
7. **Internal split-half agreement** (>= 20 splits; 24 used): per draw, each
   retained author's budgeted events are randomly halved (seeded, time order
   restored within each half); each half is featurized by the frozen map
   (`build_feature_panel`, transition-null draws = 16 as deployed), projected
   through the *budget's* D0 calibration (frozen across halves and conventions),
   whitened with per-half pooled Sigma at the *budget-level* lambda of the
   convention (the yardstick isolates sampling noise of the budget's field, so
   lambda is not re-evaluated at half-n), and compared by the weighted matrix
   cosine. Feasibility floor: halving needs b >= 8 (each half >= 4 events ->
   paths >= 2). Therefore: PANDORA 1/4 budget (b = 4) internal agreement is
   **NOT MEASURABLE** under the frozen feature map — lean (a) is adjudicated on
   the measurable budgets {1/2, 1}, stated plainly; the 1/2-budget row retains
   only authors with m >= 14 (b(1/2) = 8), so a matched-panel (m >= 14) full-
   budget row is also computed for the clean monotone comparison, with the
   all-author rows reported alongside. Essays: split-half measurable at full
   budget only (b = 8); leans (b)-ratio and (c) use full-n rows, unaffected.
8. **Between-convention gap** at budget f: both conventions on the identical
   full-budgeted panel (features, projections, D0 calibration shared
   bit-identically; only lambda differs): gap(f) = 1 - sum_c w_c
   cos(J_c(lambda_i), J_c(lambda_ii)).
9. **Adjudication map** (from the registered leans): (a) internal agreement
   improves monotonically with n for both conventions on PANDORA (matched-panel
   rows; restricted to measurable budgets); (b) gap(full) > 2 x
   max(internal-disagreement of either convention at full n, all-author rows) on
   PANDORA -> self-infliction OPERATES (through the substituted knob); (c)
   Essays: sign(gap(full) - max internal disagreement(full)) matches PANDORA's
   sign (direction only). PIVOT-IF: gap(full) < 1.2 x min(internal
   disagreements) on PANDORA -> penalty choice immaterial at real-text scale;
   the self-infliction lesson stays synthetic-scoped. Between 1.2 x min and 2 x
   max: neither fires; recorded plainly as the intermediate zone.
10. **Seeds and reproduce-first gates.** Master seed 20260802 (salted stable
    buckets per author/draw); V8 spec seed 20260805 untouched for the frozen
    feature map. Gate 1: rebuilt panels must match the persisted V8
    `data_schema.json` exactly (PANDORA 985 authors / 13202 events / splits
    420-296-269; Essays 1200 / 9600 / 463-365-372). Gate 2: full-budget
    subsample must be the identity (asserted bit-exact).

Corpora: PANDORA primary, Essays secondary (direction only). X out of scope per
the registered design.

*(Results below this line were appended after the run; nothing above was edited
after compute began.)*

---

## Part 1 — OUTCOME

**1/3 leans (c only); registered PIVOT FIRES on PANDORA by a factor of ~4,900:
the between-convention gap at full n is 2.43e-4 against an internal split-half
disagreement of ~1.0. Under the field's own comparison statistic, the penalty
convention is immaterial on real text at current scales — the arc's
self-infliction lesson stays synthetic-scoped — and the run pins down exactly
why: the two conventions are almost perfectly PROJECTIVELY EQUIVALENT on real
text, and the field's own gauge is scale-invariant.**

Verdict string: `PENALTY_CHOICE_IMMATERIAL_AT_REAL_TEXT_SCALE_SELF_INFLICTION_
LESSON_STAYS_SYNTHETIC_SCOPED` (with the substituted-knob caveat of Part 0
attached; the deployed soft estimator itself is penalty-free).

Run: 24 split-half draws per measurable cell, full registered budgets, seeds as
registered, runtime 377 s single process. Faithfulness gates all green:

- Rebuilt opened panels equal the persisted V8 `data_schema.json` exactly
  (PANDORA 985 authors / 13,202 events; Essays 1,200 / 9,600).
- Full-budget subsample is the identity (bit-exact frame equality asserted).
- Per-budget D0 recalibration at f=1 reproduces the persisted V8 support table's
  D0 effective ranks to printed precision (PANDORA M 42.166460 vs persisted
  42.1665, K 38.534629 vs 38.5346; Essays M 42.243044 vs 42.243, K 41.673555 vs
  41.6736).

## Between-convention gap (identical panels, shared upstream bit-for-bit)

| corpus | budget | achieved fraction | eval events n | lambda_inv_n | matrix cosine (i vs ii) | gap = 1 - cos | Frobenius ratio ii/i (companion) | predicted ratio lambda_i/lambda_ii |
|---|---|---|---|---|---|---|---|---|
| pandora | 1/4 | .2997 | 2,260 | 1e-5 (anchor) | 1.000000 | 0 (by anchoring) | 1.000000 | 1.000000 |
| pandora | 1/2 | .5182 | 3,908 | 5.78e-6 | .999959 | 4.13e-5 | 1.728688 | 1.729204 |
| pandora | 1 | 1.0 | 7,542 | 3.00e-6 | .999757 | 2.43e-4 | 3.334381 | 3.337168 |
| essays | 1/4 | .5 (floor) | 2,948 | 1e-5 (anchor) | 1.000000 | 0 | 1.000000 | 1.000000 |
| essays | 1/2 | .5 (= 1/4) | 2,948 | 1e-5 | 1.000000 | ~1e-16 | 1.000000 | 1.000000 |
| essays | 1 | 1.0 | 5,896 | 5.00e-6 | .999888 | 1.12e-4 | 1.998694 | 2.000000 |

The companion Frobenius ratio (unregistered, labeled in Part 0 spirit: recorded
to make the mechanism quantitative) tracks the pure-projective prediction
lambda_i/lambda_ii to 0.03-0.08% at every informative budget. The conventions
DO differ — by a large global rescale (3.33x at PANDORA full n) — but almost
nothing else.

## Internal split-half agreement (24 draws; mean weighted matrix cosine)

| corpus | budget | scope | retained | v2_fixed | lambda_inv_n | penalty_free_deployed (reference) |
|---|---|---|---|---|---|---|
| pandora | 1/4 | all | 0 | NOT MEASURABLE (b=4 < 8, frozen path floor) | — | — |
| pandora | 1/2 | all = matched_m14 | 345 | .00188 (sd .0207) | .00189 (sd .0207) | -.00730 (sd .0307) |
| pandora | 1 | all | 565 | -.00140 (sd .0118) | -.00137 (sd .0118) | -.00819 (sd .0219) |
| pandora | 1 | matched_m14 | 345 | .0000049 (sd .0108) | .0000076 (sd .0107) | -.00494 (sd .0217) |
| essays | 1/4, 1/2 | all | 0 | NOT MEASURABLE (b=4) | — | — |
| essays | 1 | all | 737 | .00057 (sd .0379) | .00046 (sd .0377) | .01444 (sd .0631) |

Every measurable cell is statistically indistinguishable from zero (|mean| <=
0.45 x sd/sqrt(24) for the whitened conventions; the deployed reference reaches
at most |t| ~ 1.8). Internal disagreement is saturated at ~1.0 everywhere, for
the substituted whitened knob AND for the deployed penalty-free estimator.

## Full-n ratio table (the registered detector)

| corpus | gap(full) | internal dis. (v2) | internal dis. (1/n) | gap / max | gap / min | sign(gap - max) |
|---|---|---|---|---|---|---|
| pandora | 2.429e-4 | 1.00140 | 1.00137 | **2.43e-4** | 2.43e-4 | -1 |
| essays | 1.119e-4 | .99943 | .99954 | **1.12e-4** | 1.12e-4 | -1 |

## Per-lean adjudication

- **Lean (a) MISS** (sanity): matched-panel (m >= 14, same 345 authors at both
  budgets) internal agreement does not increase from 1/2 to full budget
  (.00188 -> .0000049 v2; .00189 -> .0000076 1/n). Honest characterization: both
  values are zero within noise at BOTH budgets — there is no internal agreement
  to improve; the monotone-improvement sanity lean is unfulfillable in a
  signal-free regime, and the MISS is a null-regime artifact, not evidence that
  agreement degrades with n. The 1/4 budget is NOT MEASURABLE (registered
  feasibility rule, Part 0 item 7).
- **Lean (b) MISS**: gap(full n) = 2.43e-4 vs threshold 2 x max internal
  disagreement = 2.003. Missed by four orders of magnitude — and in the
  registered pivot direction.
- **PIVOT FIRES**: gap(full) = 2.43e-4 < 1.2 x min internal disagreement =
  1.2016 (ratio 2.43e-4, ~4,900x below the pivot line). Penalty choice is
  immaterial at real-text scale under the field's own agreement statistic; the
  self-infliction lesson stays synthetic-scoped.
- **Lean (c) HOLD** (direction only): Essays shows the same sign as PANDORA
  (gap sits below internal disagreement on both; excess sign -1 = -1).

## Mechanism — why the pivot fires (diagnostics, not post-hoc rescue)

The whitening spectrum explains the projective equivalence exactly. At PANDORA
full budget, the pooled-panel replicated covariance has 121/168 (M) and 113/152
(K) eigenvalues below the V2 relative floor (1e-5 x lambda_max), of which ~81/75
are negative (cross-replicate symmetrized covariances are indefinite); the
lambda~1/n floor at full n (3.0e-6 relative) clips 120/168 and 113/152. **The
band between the two conventions' floors contains exactly one eigenvalue (M) and
zero (K).** So both conventions clip essentially the same block, the clipped
block carries almost all whitened field mass, and the two whitened fields differ
by the global factor sqrt(lambda_i/lambda_ii) per family side — J_ii ~ (n/n_q) x
J_i (measured Frobenius ratio 3.3344 vs predicted 3.3372). The field's own
established comparison statistic — matrix cosine, the pipeline's D1/D2 agreement
gauge — is scale-invariant, so this large penalty effect is projectively
invisible. The arc's synthetic Leg-8 self-infliction was detected by an
ORACLE-referenced, scale-sensitive error (e_orc_true); real text has no oracle,
and the pipeline's own gauge quotients out precisely the component the penalty
convention moves. Essays reproduces the same anatomy (118-125/168, 112-146/152
below floor; ratio 1.9987 vs 2.0 predicted).

## Honest anomalies and scope

1. **The noise yardstick is saturated.** Internal split-half agreement is zero
   within noise at every measurable budget under EVERY convention, including the
   deployed penalty-free estimator. The per-context real-text relation field has
   no split-half-replicable component at these panel scales — consistent with
   the V8 route's own status (`REALTEXT_SOFT_SUPPORT_ONLY_RELATION_UNRESOLVED`,
   a single licensed context, PANDORA D2 worldnews, in the persisted run). The
   pivot therefore fires in a regime where gap (2.4e-4) is compared against
   saturated noise (~1.0); "at current real-text scales" is load-bearing in the
   verdict. If a future panel carries split-half-stable relation signal, the
   ratio should be re-measured there.
2. **Substituted knob** (Part 0): the deployed soft estimator is penalty-free;
   the ridge exists in the module only as the hard-path whitening floor (never
   binding after rank truncation) and the alias-audit regression. The registered
   conventions were compared on the module's own whitening algebra in the full
   soft space — the closest live knob. No claim about the deployed estimator's
   penalty behavior is made (it has none).
3. **Lean (a)'s MISS is a null-regime artifact** (see above), recorded as MISS
   per the registered wording, not reinterpreted into a hold.
4. **Essays 1/4 = 1/2 by design floor** (8 fixed chunks -> both floor to 4
   events/author; achieved fraction 0.5 twice); PANDORA 1/4 achieves 0.30
   rather than 0.25 (even-count floor at 4 of 8-16 events). Disclosed design
   facts.
5. **Gap grows with n by anchoring** (0 -> 4.1e-5 -> 2.4e-4 on PANDORA): the
   registered signature "gap persists or grows" is technically present but
   three-to-four orders of magnitude below the noise floor; the registered
   detector is the ratio, which is unambiguous.
6. The 1/4-budget K-family D0 soft calibration collapses toward low effective
   rank (8.5 PANDORA, 7.7 Essays vs ~39-42 at full) — 4-event paths leave a
   single transition pair per replicate; a reason the quarter budget would have
   been a poor internal-agreement cell even without the path floor.

## Decision boundary

Exploratory, opened-panel adaptive chain. This run compares two penalty
conventions of a variant whitened estimator on label-free technical panels; it
licenses no claim about personality, emotion, diagnosis, causal mechanisms, or
the deployed estimator's substantive findings, and it does not certify the
relation field itself (whose internal replication at these scales is null).
Artifacts: `results/m4_e1_convention_gap/{decision.json, convention_gap_rows.csv,
internal_agreement_rows.csv, ratio_rows.csv, diagnostic_rows.csv}`.
