# SUICA Claims Ledger

Governance: SUICA_METHOD_VALIDATION_PLAN_V2.md section 5. One row per claim.
Statuses: `supported` / `directional` / `computed_pending_audit` / `failed` /
`retired` / `not_run`. A claim may be cited in prose only at its ledger status.
No number may be written here that is not computed by a script from a CSV/JSON
artifact.

## Evidence-tier taxonomy (added 2026-07-05 referee sweep; every reported
number belongs to exactly one tier)

| Tier | Meaning | Examples |
|------|---------|----------|
| T1 exploratory | computed on dev data, criteria post hoc or evolving | strategy searches (retired), E7 factor interpretations, E5 initial run |
| T2 same-data pre-committed | criteria fixed in the script docstring before running, but on the already-explored dev tier | P1, P2, PRED-1..3, E5/E7 v2 criteria |
| T3 held-out confirmed | selection and confirmation on disjoint users/data | OP-5 B-half confirmations, OP-6a choice-axis holdout, E1 cross-fit refutation |
| T4 lockbox confirmatory | frozen config + committed prereg + single opening | none yet (P5 pending; budget 2) |

Paper rule: T1 numbers are narrative only; headline claims require T2 or
higher; "confirmed" requires T3+; external-validity claims require T4.
Six-plus analysis rounds ran on the same Tier-U dev pool — T2 "pre-committed"
labels do NOT license confirmatory language (referee R3-4); only T3/T4 do.

## Active propositions (plan v2)

| ID | Claim | Evidence | Status | Notes |
|----|-------|----------|--------|-------|
| P0 | SUICA estimator chain is computationally correct (recovers planted effects; nulls stay null) | results/suica_synthetic_ground_truth_v2/p0_results.json | **pass (audited)** | rank recovery 0.96-0.98 (W1); dominant component 15/15; null FPR 0.06 (artifact p0_results.json, post seed-fix; the initial hash-salted run printed 0.075); react recovery r=0.94; scorer equivalence exact. Audit: MixedLM benchmark had silently skipped (module missing at run time); auditor ran it — MoM 0.744/0.008/0.017/0.232 vs MixedLM 0.736/0.009/0.028/0.227, matches. Hash-salted world seeds fixed to constants post-audit; auditor's fixed-seed rerun reproduced the pass (0.97+) |
| P1 | Disjoint-text, time-gapped base test-retest reaches SB-corrected r >= 0.60 for >= 3 constructs (median >= 0.50) | results/suica_p1_disjoint_retest_v2_s128/ | **fail (audited)** | n=1,437, gap median 115d. SB r: first_person 0.725, directive 0.526, tension 0.354, novelty 0.269, adversity 0.059. Only 1/5 passes; median 0.354. Same verdict at s96. Audit reproduced exactly; no deflating bug. **Audit addendum: the RAW (uncentered) variant would PASS (SB 0.856/0.650/0.650/0.446/0.166; 3/5 >= 0.60, median 0.650)** — P1's failure is caused by the centering mechanism, not absence of text signal. Volume curve: first_person reaches 0.86 at ~4.5k tokens/half; tension/novelty plateau (state-driven, not volume-limited) |
| P2a | Condition centering improves cross-condition-set stability for lexicon-rate constructs (pooled delta CI > 0) | results/suica_p2_condition_centering_v2_s128/ | **fail (audited)** | n=3,726. Pooled delta = -0.091, CI [-0.102, -0.080]: centering REDUCES stability for all 5 constructs. Same at s96 (-0.094). Audit attacks defeated: oracle centering gives same deltas (LOO noise irrelevant); restricting to conditions with >= 20 or >= 50 users keeps all deltas negative. Caveat retained: stability != validity — raw stability partly reflects stable venue self-selection |
| P2b | Condition centering improves cross-condition-set stability for node-occupancy scores (pooled delta CI > 0) | results/suica_p2_condition_centering_v2_s128/ | **fail (audited)** | mean node r: centered 0.096 vs raw 0.163; delta -0.067, CI negative. Audit: self-inclusion bias measured at +0.0005 (negligible); matched-noise global-reference control (0.172 > 0.163) shows the condition-relative reference itself causes the loss |
| P3 | Frozen SUICA scores are not redundant with generic lexica (R^2 <= 0.75 majority) | results/suica_p3_redundancy_v2_s128/ | **pass (audited, with caveats)** | All 23 targets Empath CV R^2 <= 0.428 (max = raw first_person; choice axes 0.01-0.36). Audit: no CV leakage, bit-exact reproduction. Caveats: Empath input capped at 24k chars vs full-slice targets (biases toward non-redundancy); the 5 fe_base rows are moot after E1 overturn |
| P4 | person x condition variance exists beyond noise; react signature split-half >= 0.30 for >= 2 constructs | results/suica_p4_variance_components_v2_s128/ | **partial (audited)** | Interaction share CI>0 for 2/5 (first_person 0.051, directive 0.039). React signature medians 0.009-0.187, all < 0.30 (nulls ~0; first_person 0.187 is real but small signal; criterion is attenuation-heavy on few-slice cells). MoM: first_person person=16.2%/condition=5.5%. Audit correction: the earlier "MixedLM corroborates: tension condition=45.3% (topic-driven)" claim is STRUCK — that fit is degenerate (empirical condition eta^2 = 0.97%); correct reading: tension is ~95% slice-level residual, person ~2-5% either way |
| P5 | <= 10 preregistered directional external hypotheses, single lockbox opening, BH-FDR in-set | results/suica_lockbox_opening_1/OPENING_REPORT.json + reports/suica_lockbox_opening_1.md | **OPENED 2026-07-07 — FAIL by the preregistered rule (T4)** | Opening #1 of 2 SPENT (budget 2->1). Sealed prereg executed at commit cd63d13 (script sha256 d2d0c51f..., pre-opening adversarial audit passed all 10 checkpoints; sentinel 2026-07-06T18:52Z). Eligible Big5 1,058 (est. 1,108, dev 4.5%), bridge 303 (est. 326, dev 7.1%). **RESULT: 2/7 confirmatory passes (rule required >=4); no significant wrong-direction effects.** T4-CONFIRMED: H2 first_person -> Neuroticism r=+0.111 [+0.051,+0.170] q=0.002 (same direction, similar magnitude as the Essays dev-half orientation +0.122 — different corpus, population, and anchor instrument); H6 politics/news choice axis -> Openness r=+0.096 [+0.036,+0.155] q=0.006. NOT confirmed: H1 tension->N +0.052 ns (consistent with its no-trait verdict), H3 novelty->O -0.046 ns, H4 directive->A +0.029 ns, H7 venue entropy->O -0.009 ns (all 3 declared entropy variants null), H8 gaming->E -0.041 ns (predicted direction, underpowered). H5 secondary: directive->is_T +0.063 [-0.051,+0.174], predicted direction, underpowered exactly as preregistered. TF_cont pole flip applied per F5 (bridge file codes F-positive; flip decided from mbti_type_resolved BEFORE predictor contact). Delta-R^2 add-on UNINFORMATIVE: frozen F8 convention (Empath-194, ridge alpha=10) gives negative CV R^2 for both baselines at this n — recorded as-is, no re-tuning. NO re-analysis permitted; opening #2 (last) reserved for a future revised battery. Essays confirm-half labels remain UNTOUCHED by this opening (H1-H8 are PANDORA-only; the Essays lockbox portion is still sealed). **Round-8 audit: UPHELD** — independent recomputation of all 8 hypotheses from predictors+labels reproduces every r/p/CI/q to 1.1e-16; sentinel hashes match; no second-look traces (no artifact newer than the report; predictors mtime precedes sentinel); tf_flip verified (bridge TF_cont is literally a binary F-indicator, corr with contains-T = -1.0000); public-tag chain of custody verified (GitHub peeled tag == seal commit; sealed PREREGISTRATION byte-identical); delta-R^2 negative CV R^2 confirmed as the frozen convention overfitting at n (train 0.26-0.30 vs test negative on every fold), not a bug. Extraction note: cap 400 = expected-value seeded thinning (realized max 451), mirroring the frozen Tier-U extractor |

### Exploratory positive finding (dev tier, 2026-07-04)

Condition-CHOICE distribution stability (early vs late halves, >= 90-day gap,
n=2,758 Tier-U users, top-300 subreddit space): same-user cosine median 0.608
vs random-pair 0.022, **AUC = 0.909**. Choice is by far the most stable
person-level signal in this data — far above any content-deviation base score
(P1). Supports pivoting the SUICA measurement object toward
{style-stable rates (e.g., first-person usage) + condition-choice profile},
i.e., the MCD RESULT_1 direction. Exploratory: computed once, label-free, not
yet preregistered.

### Interpretation shift recorded 2026-07-04 (ADJUDICATED: upheld by audit rounds 2-3 — P2/E1 verdicts and the OP-6a/E3 held-out choice results confirm this reading)

P2's decisively negative delta inverts the core mechanism claim: on PANDORA,
condition (subreddit) composition carries person signal (self-selection), so
raw scores are MORE stable than condition-centered scores. This is consistent
with (a) MCD RESULT_1, where context-CHOICE log-ratios beat response-deviation
features, and (b) the earlier context_fixed_deviation benchmark failure
(0.079 vs baseline 0.194). The empirically supported reading: **condition
choice is signal; deviation under fixed conditions is mostly noise at
realistic text volumes** (react medians 0.01-0.19). The strongest surviving
person measure is first-person usage (style/function-word trait), which is a
known result in the literature, not a novel SUICA discovery.

## Exploration phase E1-E4 (2026-07-05, Tier U, decision rules pre-committed in script docstrings)

| ID | Hypothesis | Evidence | Status | Result |
|----|-----------|----------|--------|--------|
| E1-R1 (lexicon) | Centering rescued by subtracting two-way-FE condition effects (person composition purged) instead of raw condition means | results/suica_e1_e2_centering_rescue_v2_s128/ (+ s96) | **OVERTURNED by audit** | In-sample deltas (+0.037..+0.064) were a **self-estimation leak**: c_hat was estimated on pooled A+B slices, so the user's own data entered both bases via b_hat. Audit's causal controls: rand-half estimation (same noise, leak kept) stays positive (+0.027..+0.047); user-fold / cross-fit estimation (leak removed) flips ALL constructs significantly negative (tension -0.070 [-0.090,-0.050], directive -0.074, adversity -0.046, first_person -0.067; novelty -0.207). Same collapse at s96. **No form of condition centering tested (naive / partial / FE out-of-sample) adds stability on this data — P2's original negative verdict stands, now against the strongest rescue attempt** |
| E1-R1 (occupancy) | Same, for 24-node content-region shares | same | **OVERTURNED by audit** | Audit reproduced +0.053 in-sample exactly, then flipped it out-of-sample: cross-fit -0.071 [-0.077,-0.066], user-fold -0.062 (= the naive-centering penalty) |
| E2-R2 | Partial (lambda) naive centering has an interior optimum | e2_lambda_curve.csv | upheld (audited) | No: monotone decreasing from lambda=0 for all constructs. Harmful at any dose |
| E1-P1-FE | FE centering on temporal retest | p1_fe_vs_raw.csv | consistent-with-audit | raw > FE everywhere (first_person 0.730 vs 0.547). Note: here c_hat was estimated per half (no pooled-set leak), and FE already lost — the audit cites this as corroboration of the leak diagnosis |
| E3-R4 | Choice distribution converts into stable interpretable scale axes (12 content classes of conditions) | results/suica_e3_e4_choice_class_v2_s128/ | **upheld (audited)** | Independently recomputed exactly: 6/13 axes with early-late retest r >= 0.50 (gaming 0.7027, sports 0.679, politics/news 0.571, life-planning 0.533, tech/beauty 0.532, narrative media 0.508; n=3,204 unique authors, disjoint halves, half-specific references; robust to dropping log-ratio, raw-share r=0.660); profile AUC 0.839; mean inter-axis abs r = 0.131. **LEAKAGE FLAG: class 11 contains MBTI subreddits — choice_ax_11 excluded from any external Big5/MBTI validation** |
| E4-R3 | React revives at situation-class granularity with thick cells (ipsative CAPS signature) | class_react_signatures.csv | **OVERTURNED as individual-signature evidence** | Medians reproduce (first_person 0.502, n=62), but the builder's within-user permutation null was the WRONG null (and the ledger's earlier "nulls ~0" was false — artifact nulls are -0.23/-0.15; with m~4 shared classes the permutation expectation is -1/(m-1)). Against the correct STRANGER null (u-early vs v-late over shared classes) the normative baseline is 0.310/0.280/0.253 — the "signatures" are mostly shared population class profiles; person-specific increments ~0.19 (first_person), ~0.12 (directive), ~0.06 (novelty) on 4-point profiles. React stays retired; any future attempt must use stranger-corrected nulls and thicker cells |

### SUICA v3 architecture (REVISED after audit)

`SUICA_v3(u) = { style-base (raw, uncentered rates), choice axes (venue-selection channel), residual_quality }`

- The FE-base "deviation channel" is empty: no construct benefits from any
  tested centering out-of-sample. Deviation-under-fixed-condition is retired as
  a scoring mechanism on this data (kept only as a falsified-hypothesis record).
- react is retired again pending stranger-null-corrected, thick-cell designs.
- The original v1 base (naive-centered) remains retired permanently.

## Rind theory base v3 regime test (2026-07-05, predictions pre-committed in docs/SUICA_RIND_THEORY_BASE_V3.md)

| ID | Prediction | Evidence | Status | Result |
|----|-----------|----------|--------|--------|
| PRED-1 | Within-population paired test: fixed-rind split-half > mixed-rind (same users, same slice counts) | results/suica_rind_regime_test_v3/pred1_paired_rind.csv | **PASS 3/4 (audited)** | Audit round 3: effect survives parity/ordering/density/time-span controls for first_person (+0.063 [0.029,0.098] span-matched), directive (+0.165 [0.074,0.260]), novelty (+0.182 [0.047,0.294]). **tension delta OVERTURNED as temporal-clustering artifact** (fixed arm was a chronological prefix, median span 216d vs 1,283d; span-matched delta -0.033 [-0.149,0.073]). Pre-committed majority rule still met at 3/4 |
| PRED-1b | Cross-corpus ordering Essays >= X >= PANDORA-mixed at matched budget | pred1b_cross_corpus.csv | upheld-as-recorded (audited) | Ordering NOT confirmed: X best; Essays ~ PANDORA-mixed. Population-relative amendment adopted (legitimate post-hoc patch, itself untested). Audit note: X's win may partly reflect templated market-post repetitiveness |
| PRED-2 | Domain-fixed regime retains micro-choice: X symbol-choice AUC >= 0.65 | rind_regime_results.json | pass (audited, with caveats) | All-pairs AUC 0.820 (builder's 0.810 was a noisier single-permutation estimator); survives threshold loosening (n=76 -> 0.787). Caveats: n=31 primary, corpus has only 17 distinct symbols (top-60 filter vacuous), needs larger domain-fixed corpus |
| PRED-3 | Anchor-rate correlation structure invariant across corpora (all pairs >= 0.70) | rind_regime_results.json | **partial (audited, numbers corrected down)** | Builder's 0.587-0.691 included a 24th algebraically-derived feature (projective_tension_rate). True 23-feature values: pandora-essays 0.620, essays-x 0.572, pandora-x 0.530; sparse-feature-drop variant pushes pandora-x to 0.494 (below the 0.50 fail line). X leg unsound (89.5% single-slice users). Only pandora-essays 0.620 is solid evidence; transportability is approximate at best |

Governance note: Essays used dev-half TEXT only (stable-hash 50/50; frozen at
data_sets/prepared/suica_tiers_v2/essays_regime_dev_half.csv); Big5 label
columns never loaded; Essays confirm-half untouched for P5.

## E5 trait-state spectrum (2026-07-05, OP-1/OP-11; predictions pre-committed in script docstring)

| ID | Claim | Evidence | Status | Result |
|----|-------|----------|--------|--------|
| E5-spectrum | Rind-fixed person x occasion x slice decomposition yields a trait-state spectrum per construct | results/suica_e5_trait_state_spectrum_v3_{quarter,month}/ | **audited, values corrected to MixedLM** | Round-4 audit: MoM is BLIND below ~0.05 state share on this thin-cell layout (planted 0.03 -> printed 0.000; trait inflated ~+0.04; CIs do not cover the bias — P0 validated a different regime). Corrected (MixedLM, month): first_person trait ~0.33, state ~0.10; tension trait ~0.04-0.06, **state <= ~0.02**; slice noise dominates (~0.9 for tension). Headline ordering unchanged; precision wording demoted from "0.000, CI upper 0.002" to "<= ~2% by MixedLM". Venue-pooling attack arbitrated: no hidden cross-venue tension state (pooled MixedLM 0.0014), but pooled MoM would have printed a spurious 5x state — estimator-regime validation is now a standing rule |
| E5-P-E5a | first_person trait > state | e5_results.json | pass (audited) | PASS both granularities, robust across estimators |
| E5-P-E5b | tension is relatively more state-like than first_person (state:trait ratio) | e5_results.json | **prediction FAILED (recorded)** | tension is NOT occasion-state-like; its variance is slice-level (momentary topic), neither trait nor persistent state. Robust to thick-cell restriction, venue pooling, and MixedLM |
| E5-P-E5c | Per-occasion state monitoring feasible at current volumes (split-half >= 0.30) | state_precision.csv | fail (audited, level demoted) | Parity split-half (0.352/0.390) is ~2.5x inflated by same-text adjacency. Honest contiguous halves: first_person 0.157 (SB 0.27 — below the 0.30 bar), tension 0.049. Channel ORDERING survives (first_person best), feasibility level does not: per-occasion state monitoring needs roughly 3-4x more per-occasion text |

Clinical implication (audited): word-rate tension is not a usable
occasion-state monitor in a general population at ~1k tokens/occasion
(true state <= ~2%); the most measurable state channel is within-person
first-person-rate deviation (state share ~0.10, MixedLM), but its honest
per-occasion precision (contiguous SB 0.27) is still below the feasibility
bar. Open outs: clinical populations, more per-occasion text, event-anchored
prompts, richer features (OP-7/OP-11). All variance shares are design-relative
(pooling venues cuts first_person trait 0.355 -> 0.23).

## E6/E7/P1-deep — horizontal-cut round (2026-07-05, round-5 audited)

| ID | Claim | Evidence | Status | Result |
|----|-------|----------|--------|--------|
| E6 signature (OP-2) | With thick cells and the proper STRANGER null, person-specific situation signatures exist | results/suica_e6_react_stranger_null_v3/ (v2 script) + round-5 audit | **signature_revived (audited; script reproduces adjudication)** | v1 estimator mixed estimands (audit round 5); OP-17 fixes folded into the script (matched pair-shared class sets, equal gates >= 5, two-sided fresh-pairing bootstrap). v2 script output: first_person +0.154 [0.007,0.278], directive +0.148 [0.044,0.283] -> pre-committed >= 2-construct rule PASSES (audit's independent estimator: +0.167/+0.179, consistent). novelty +0.006 / adversity +0.044 / tension +0.056 all null — v1's novelty/adversity increments confirmed as class-set artifacts. C3 channel: revived for 2 style constructs, n=195 deep users |
| E7a | Month-level within-person state reliability per feature | results/suica_e7_within_state_discovery_v3/ | fail (audited) | Only 3/23 features >= 0.10 (self_focus 0.136, second_person 0.133, moral_norm 0.118). Month cells average away short-timescale states |
| E7b | Within-person factor structure replicates odd/even months | same | **OVERTURNED as stated (builder criterion vacuous)** | Congruence 0.93-0.99 reproduced but shuffled-month and disjoint-user nulls give the same range; factor month-state reliability only 0.04-0.12 — the pooled within-covariance is mostly slice co-occurrence. Honest replacement: small-but-real month-state covariance exists (cross-half SVD 0.20/0.18/0.14 vs null ~0.07-0.08) |
| E7c (adjudicated) | Above-null decaying month persistence of state factors | same + audit nulls | **2 factors persist** | Against the correct negative null (-0.076): f3 mentalization/certainty/directive mode +0.101 [0.076,0.126] decaying (disattenuated lag-1 ~ 0.64); f1 redemption/social-eval/positive-affect mode +0.070 [0.031,0.116] decaying; f5 non-decaying drift; f4 (distress mode) no clean persistence. Builder's vs-zero criterion was mis-specified (self-flagged, confirmed) |
| E7d | Within (state) factor space differs from between (trait) space | same | **pass (audited)** | Best-match congruence [0.876, 0.775, 0.713, 0.704, 0.545]; robust to assignment method; scaling choice was null-favorable. The horizontal-cut hypothesis is vindicated: state dimensions are not the trait dimensions |
| P1-deep (OP-12) | Cap-400 extraction did not distort conclusions | results/suica_p1_disjoint_retest_v2_deep128/ | pass (audited, one mover) | Verdict cap-invariant (P1 fail; only first_person SB >= 0.60: 0.789). Mover to record: adversity_recovery null at cap-400 (0.030) -> positive on deep (0.129 [0.067,0.197]) |

Design lesson recorded: text states live below the month timescale (E7a fail +
f1/f3 small monthly persistence); occasion sampling for state measurement
should be session/day-scale — which matches the clinical per-session design
(Rulebook G3).

### E7 v2 rerun with OP-17 fixes + OP-16 week probe (2026-07-05)

Script criteria replaced per round-5 audit (fail-able cell-state reliability
instead of vacuous congruence; 200-draw empirical nulls; above-null deltas
with cluster-bootstrap CIs; congruence reported WITH shuffled null).

| Occasion | E7b' cell-state reliability >= 0.10 | E7c' above-null lag-1 delta (all factors) | persistent + decaying (strict) |
|---|---|---|---|
| month (n=1,175) | 1 factor (f5 0.121) -> fail | +0.027..+0.100, all CI > 0 | 2: f1 +0.069 [0.033,0.106], f3 +0.100 [0.079,0.128] — matches round-5 adjudication |
| week (n cells 15k+) | **3 factors (f5 0.134, f2 0.114, f3 0.105) -> pass** | +0.040..+0.099, all CI > 0 | 1 strict (f5); f3 +0.099 decay borderline |

**OP-16 verdict (interim probe): supported** — finer occasions make the state
modes more measurable (E7b' 1 -> 3 factors at week), consistent with states
living below the month scale; the projected optimum is session/day sampling,
untestable on this corpus (cells too thin below week). Congruence null gap
0.007-0.010 confirms the old E7b criterion was uninformative.

## E9 embedding interpretive channel (2026-07-06; criteria pre-committed in script)

| ID | Claim | Evidence | Status | Result |
|----|-------|----------|--------|--------|
| E9a | Construct definitions translate into embedding directions (anchor projection scores are stable AND converge with their lexical counterparts, MTMM) | results/suica_e9_embedding_interpretive_v3/ | **pass (round-7 audited, caveat added)** | **PASS 11/19** (bar 8): anchor-score disjoint-occasion stability 0.40-0.68; convergent r up to 0.815 (gaming), 0.782 (tech), 0.755 (politics) with convergent > max discriminant. Theory-consistent failures: wcl_60 (conv 0.222 — encoders normalize orthography away), novelty (0.258, choice-channel), wcl_13/54/45 (style anchors bleed). **Scrambled-anchor control lesson: random directions are ALSO person-stable (0.49-0.55) — stability alone is meaningless for direction scores; MTMM convergence is the licensing evidence (new guide rule G11)**. Round-7 caveat: convergent magnitudes are same-text-inflated ~35-45% (cross-occasion: gaming 0.815->0.450, tech 0.782->0.484); the MTMM pass count is robust cross-occasion at 10/19 (bar 8; sole flip wcl_07 by -0.0025) — 'translation works' is licensed at the cross-occasion level |
| E9b | A person can be interpreted via the measured profiles of their embedding neighbors ("position -> profile translation", k=50, vs random-neighbor null) | same | **pass (round-7 audited)** | **PASS 18/19** (bar 8). Labeling corrected per audit: the values first_person 0.577 / family 0.573 / positive-enthusiasm 0.531 / apostrophe 0.293 are NEIGHBOR-READ r's (random-neighbor null ~0; deltas +0.30..+0.59 per e9b_neighbor_reading.csv — min passing delta 0.304). Audit verified: self-exclusion (0 self-inclusions in 3,183), fair null, independent kNN reproduction exact; borrowed-vs-early r=0.729 vs late 0.577 confirms the reported number is honestly cross-occasion. Sole failure: tension — consistent with its no-trait verdict |

## E11 quantified adjective projection (2026-07-06; criteria pre-committed)

| ID | Claim | Evidence | Status | Result |
|----|-------|----------|--------|--------|
| E11 | Construct directions can be interpreted as METRIC adjective profiles (tagged person-descriptor lexicon projected onto cross-fitted score-regression directions) | results/suica_e11_adjective_projection_v3/ | **promising_needs_v2 (2/4 criteria)** | PASS: discriminance (pairwise Jaccard 0.085) and enrichment count (10 constructs incl. textbook hits — tension -> anxious/hesitant/irritable/fretful; novelty -> innovative/creative/curious O+ p=.001; directive -> selfish/rude/demanding A- = same direction as preregistered H4; sports -> competitive +4.0; politics -> argumentative +3.8; media -> storytelling +3.9). FAIL: (1) A/B direction stability median 0.622 < 0.70 (wcl_15 collapses at 0.19); (2) scrambled-direction control produced 2/3 spurious enrichments -> the Fisher calibration is anti-conservative (embedding-geometry correlations violate independence); enrichment must be permutation-calibrated against random-direction nulls. Additional pathologies logged: ANTONYM PROXIMITY (uncreative in novelty's top list; verbose+terse both top for wcl_60 — negation prefixes are topic-close in embedding space) and SENSE COLLISION (gaming direction retrieves "passive/efficient" in their game-mechanics senses). v2 fixes specified: bipolar antonym-pair scoring, permutation-calibrated enrichment, direction stabilization with per-adjective bootstrap CIs, sense-collision screen |

## OP-18 scorer v3.1 robustness (2026-07-06, freeze prep)

| ID | Claim | Evidence | Status | Result |
|----|-------|----------|--------|--------|
| OP-18a | Smart-apostrophe normalization (U+2019/U+2018 -> ') does not change headline stability | /tmp logs + reports/suica_p1_disjoint_retest_v2_s128norm.md | closed (robustness demonstrated) | P1 with normalization: first_person 0.570 (vs 0.569), directive 0.355 (0.357), tension 0.213 (0.215), novelty 0.155 (0.155), adversity 0.030 (0.030) — max delta 0.002. v3 numbers stand; normalization adopted as the recommended ingestion default (prep flag --normalize-apostrophes). Lexicon disjointification remains v4 roadmap (formula changes restart validation per F1) |

## E11 v2 + dev-tier anchor performance (2026-07-06)

| ID | Claim | Evidence | Status | Result |
|----|-------|----------|--------|--------|
| E11v2-trait | Metric adjective profiles with the four v1 fixes | results/suica_e11v2_adjective_trait/ | computed_pending_audit | V2-1 stability PASS (median bootstrap rank stability 0.868, v1 was 0.622); V2-3 discriminance PASS (0.080); **V2-2 FAIL: only 1/19 clears the permutation-calibrated marker-axis bar** — v1's ten enrichments confirmed as calibration artifacts (G11 family). CI-coherent weak alignments persist (novelty->E+/O+ +0.07; tension->N+; directive/profanity->A-). RULING: adjective profiles = descriptive aids with CIs; the licensed construct-trait bridge = dev-anchor label relations. Round-7 addendum: V2-4 also FAILS (null axis hit rate 0.026 > 0.02 — permutation calibration slightly anti-conservative); shuffled-score-fit null check remains open (round-7 INCOMPLETE item). **RESOLVED 2026-07-07** (results/suica_e11_shuffled_fit_null_v1/): the geometrically correct null (shuffle scores -> REFIT with the frozen ridge -> marker |
| E11v2-state | Same machinery on the horizontal-cut state modes (f1/f3/f5; within-person centered month embeddings from the 4070) | results/suica_e11v2_adjective_state/ | computed_pending_audit | Direction stability 0.904-0.946; discriminant 0.044; 0/3 clear the strict marker-axis bar; CI-coherent leans match the modes' working interpretations (f1 positivity -> A+/O+/N-; f3 reflective -> N+; f5 -> C-/A-). Same ruling as traits: descriptive aids with CIs. Round-7 addendum: V2-4 FAIL (0.026) applies here too. **RESOLVED 2026-07-07** (shuffled-fit null, within-user permutation): thr ratios 0.27-0.39 (old bar strongly conservative); corrected recount licenses state_f5 -> A-/C- (matching its working interpretation), so the state V2-2 criterion (>= 1) technically passes under the corrected null — but absolute |
| DEV-ANCHOR | Battery <-> anchor orientation WITHOUT opening the lockbox (MBTI = Tier-D n=3,183; Big5 = Essays dev-half n=1,255, battery transported unchanged) | results/suica_dev_anchor_performance_v1/ | **pass (audited, T2 orientation)** — round-7 code/number checks by auditor; the three remaining decisive attacks executed to the auditor's exact spec (mechanical/deterministic): data-level lockbox check = 0 Tier-L users in battery and 0 in any axis join, Essays confirm-half (1,212) untouched; seed stability TF CV r = 0.3449/0.3504/0.3470 (seeds 7/123/2026) vs recorded 0.3456; TF base rate 0.334, dichotomized CV AUC 0.706. Known minor: imputation uses full-data column means pre-split (label-free, auditor-assessed near-zero impact; fix scheduled v3.1 code hygiene) | Ridge CV r: **TF 0.346** (best edge positive-enthusiasm +0.316, 22 q<.05 edges), JP 0.182, EI 0.139, SN 0.120; Essays Big5: O 0.194, **N 0.160 (first-person +0.122 — prereg H2 direction visible at dev tier)**, E 0.141, C 0.117, A 0.109. Context: TF exceeds the entire earlier exploratory record; Essays transport mean r~0.144 ~ bge-large transfer (0.153) with 19 interpretable scores. First label contact of Tier-D MBTI and Essays dev-half logged here; lockbox untouched (budget 2/2 intact) |

## OP-9 embedding baseline (2026-07-05; interpretive rules pre-committed in script)

| ID | Claim | Evidence | Status | Result |
|----|-------|----------|--------|--------|
| OP-9 | The SUICA lexical layer is not subsumed by a modern encoder and holds identification parity | results/suica_op9_embedding_baseline_v3/ | **closed (computed; rules pre-committed)** | bge-large-en-v1.5, n=3,183, same disjoint-occasion battery. M1: AUC embedding 0.891 vs SUICA-19 0.887 (gap +0.004 — immaterial at the 0.10 bar). M2: top embedding-PC retest 0.66-0.72 vs SUICA best ~0.65. M3: subsumption NOT material (median R^2 0.684; majority < 0.80; max 0.896 for the most content-like constructs); reverse construct->PC R^2 0.57-0.83. Verdict: complementary layers; "why lexicons" answer = interpretability + frozen formulas + model-independence at ~zero identification cost. Ops note: encoding offloaded to the Windows 4070 via SSH (17.5 min vs stalled >70 min on MPS); --precomputed path is now the standard for embedding jobs |

### OP-22 round-7 audit note

Two of 120 human-sheet rows ("NONE OR F", "NONE OR A") were cleaned to "E"
by the first-letter regex (it matched the E inside "NONE"), violating the
pre-stated rule; both are wcl_22 items and are wrong answers under either
cleaning — zero numeric impact on any recorded count. wcl_45/wcl_60 rows
reproduced bit-exact; binomial and T2 gates verified.

## OP-5 construct inventory expansion (2026-07-05, round-6 audited)

| ID | Claim | Evidence | Status | Result |
|----|-------|----------|--------|--------|
| OP-5 discovery | A-discover/B-confirm expands the style-channel inventory under audited rules | results/suica_op5_construct_discovery_v3/ | **OP5_success (audited — first run with zero overturned claims)** | 15/15 candidates confirmed on B-half users (never seen in feature construction or selection): r_B 0.378-0.649, all CIs > 0, method-stripped retained. Audit: A/B integrity proven; r_B independently reproduced (max diff 0.010); no volume confound (partial r change <= 0.003); 0/15 exceed the 0.60 single-choice-axis redundancy bar. Caveats: joint-13-axis R^2 makes wcl_02 (sports words) a near choice-duplicate (0.63) and wcl_20/wcl_11 borderline (~0.55) — top-3 (wcl_60/wcl_03/wcl_36) clearly new. wcl_60 confirmed as APOSTROPHE-OMISSION ORTHOGRAPHIC REGISTER (93% of mass from users literally typing "dont"): real typed behavior, rename not invalidate. Provisional inventory: 4 v3 battery + 15 = 19; next gate = blind coding v2 + naming (Rulebook F5) |

New-candidate families (top words in results CSV): style-register (apostrophe
omission 0.649, positive enthusiasm 0.579, epistemic argumentation 0.522,
analytic-formal 0.473, negation-argument 0.454, casual interjection 0.444,
profanity-intensity 0.432) and interest-content (family narrative 0.571,
tech-practical 0.541, media-narrative 0.516, sports 0.502, politics 0.495,
media-consumption 0.451, gaming-mechanics 0.378, descriptive-narrative 0.459).

## Construct set v2 (operational names, per plan fix list)

| v2 id | Formula (frozen 2026-07-04) | Replaces |
|-------|------------------------------|----------|
| novelty_play_v2 | novelty_play_rate | f05_novelty_play_core |
| directive_action_v2 | sqrt(directive_rate * second_person_rate) | f10_directive_action_core |
| adversity_recovery_v2 | 0.6*adversity_recovery_score + 0.4*redemption_growth_rate | suica_adversity_recovery_core |
| first_person_usage_v2 | self_focus_rate | suica_self_positioning_component (renamed: operational, not psychological) |
| tension_core_v2 | 0.40*projective_tension_rate + 0.35*uncertainty_rate + 0.25*conflict_threat_rate | suica_affective_tension_component + suica_tension_uncertainty_core (merged) |

## Retired claims (2026-07-04 review)

| Claim | Reason | Where it appeared |
|-------|--------|-------------------|
| Cross-scenario base stability r ~ 0.88-0.98 as trait-stability evidence | Same-text repartition; measures pipeline determinism | suica_construct_validation_status_20260628.md and downstream |
| 6 validated constructs incl. independent tension pair | tension pair r=0.979 is algebraic (shared ingredient rates) | construct inventory docs |
| "Hybrid projective-scale measurement system" | react/choice not release-grade by own reports (choice AUC ~ 0.55) | theory framework v3 |
| "5/7 factors pass blind validation" as construct validity | Items selected by the score under test; same-family coders; manipulation check only | independent blind validation reports |
| TEG novelty-play bridge "heldout_fdr_supported" | p_fdr = 0.060; single lexical proxy coder | suica_teg_ego_state_bridge_v1.md |
| Cross-language readiness of validated scorer | Scored subset monolingual (en_latin only) | international psychometrics doc |

## FREEZE RECORD (2026-07-06)

The SUICA method is frozen as an independent repository:
`<repo-root>`
- Initial commit: dd5c7805689acd6d5351f7a22864b3ff45eb1d7d
- Tag: v0.1.0-prereg-sealed (the PREREGISTRATION seal)
- Verified at freeze: 39/39 tests + P0 zero-data pass inside the release;
  0 lockbox users in any dev analysis; lockbox budget 2/2 unopened.
- Round-7 freeze audit: E9a/E9b/OP-22 upheld (with recorded caveats),
  E11v2 upheld with V2-4 fail recorded, DEV-ANCHOR promoted after the
  auditor's three remaining mechanical attacks were executed and passed
  (seed stability 0.3449-0.3504; base rate 0.334; AUC 0.706; 0 Tier-L
  leakage). Open round-7 INCOMPLETE items (E11 shuffled-fit null geometry;
  full manual number sweep) are carried in OPEN_PROBLEMS.
- 2026-07-07 seal externalized: public remote
  https://github.com/reiserhhh/sliced-utterance-in-context-assessment
  (tag v0.1.0-prereg-sealed pushed; remote peeled tag hash verified equal to
  the seal commit dd5c7805689acd6d5351f7a22864b3ff45eb1d7d; GitHub Release
  published on the tag).

## Post-freeze continuation (2026-07-07; seal untouched — new work in new rows)

| ID | Claim | Evidence | Status | Notes |
|----|-------|----------|--------|-------|
| SCORER-V4 | Disjoint anchor lexicons remove manufactured between-category covariance while leaving the frozen battery untouched | scripts/suica_v4_lib.py + results/suica_v4_scorer/v4_selftest.json | **computed_pending_audit** | 250 -> 227 words, 20 reassignments each with logged rationale (WORD_MOVES; battery-priority policy). Selftest: disjointness hard-assert PASS; **battery BIT-IDENTICAL to v3 (max abs diff 0.0 on 500 real slices)** — the validated chain does NOT restart; 9 non-battery rates shift (past_temporal -0.62, mentalization -0.36, positive_affect -0.23 mean-rate). CLOSES OP-18 (v3 frozen and unchanged; v4 is the additive successor); delivers the OP-23 instrument fix (E7 re-run under v4 rates still pending). K1 limitation: token-level disjointness only (plan vs planning/plans variants). JP するな lookahead extended per round-8 (stage-2 item) |
| ALL19-GATE | Flesh-purity gate classification of the full 19-construct inventory | results/suica_c2_purity_all19_v1/ | **computed_pending_audit** | Pass-A slices REBUILT with text via the frozen rules and verified cell-exact against the frozen artifact before scoring. Result: **F-family 2** (first_person 0.268/0.279; wcl_35 media-consumption 0.206/0.212), **C-family 7** (directive 0.100/0.471 borderline-at-threshold; novelty; wcl_60 0.077/0.594 — READING REVISED to venue-coupled orthographic register; wcl_02/07/22/23 — profanity venue-normed), **composite 7** (incl. wcl_03, the TF best edge, majority choice-mediated 0.537; wcl_15 = weak-signal subtype 0.082/0.042), **undetermined 3** (tension, wcl_13, wcl_20). CAVEATS: gate conservative (class-disjoint attenuation-uncorrected -> F undercounted; borderline wcl_03/36/11 at class_disj 0.10-0.12; SB-corrected gating = v4.1 item); estimator licenses inherit W-B/B2/B2c/B3 with the same F6.3 band discipline. Honest headline: MOST of the discovered inventory is venue-coupled — the pure-flesh channel is real but thin at word-rate construct technology, strengthening OP-33 (co-selection features) |
| V4-COMPOSITE | Channel-family dev composites + frozen weights (opening-#2 candidates) | results/suica_v4_composite_v1/ | **computed_pending_audit (dev-tier T2 orientation)** | Conventions identical to dev-anchor v1 (imported, not reimplemented); FULL31 REPRODUCES the baseline exactly (TF 0.346 / JP 0.182 / EI 0.139 / SN 0.120 — sanity gate). Channel-clean F_PLUS_C: TF 0.280 / JP 0.151 / EI 0.118 / SN 0.066 — composites carry ~0.07 of TF r. **F_ONLY (2 features!) reaches TF 0.239** ~= C_ONLY's 0.243 from 19 features. Essays transport: F_PLUS_C-constructs ~= STYLE19 for O/N (0.199/0.169 vs 0.194/0.160), weaker for E/C/A. Frozen RidgeCV weights saved for {FULL31, F_PLUS_C} x 4 MBTI axes (v4_frozen_weights.json) — sealed at commit as opening-#2 candidate predictors; deployment keeps FULL31 (max signal, channel-ANNOTATED), trait language licensed only for F-family |
| OP-32-P | Individuality-as-residual pilot: after removing the normative profile (per-construct z within half, Furr 2008 frame), a person's 19-construct DEVIATION profile is stable across disjoint occasions | results/suica_op32_distinctive_residual_pilot_v1/ | **computed_pending_audit (T1 exploratory)** | n=3,183 half-eligible Tier-U users, >= 90-day-gap halves. Distinctive-signature stability median r = 0.505 vs stranger-null median -0.018 (null 97.5pct -0.004; excess +0.523; 94.6% of users above the null band). Distinctiveness MAGNITUDE itself moderately stable (r=0.353). Context (cited, not recomputed): identification AUC battery 0.887 / embedding 0.891 (codability half of the fingerprint thesis) and OP-9 M3 ~32% of embedding-space person-stable signal outside the battery (factor-incompleteness half). CAVEATS: single cohort; within-battery configuration residual only (the outside-battery residual is the M3 share); stranger null handles construct intercorrelation structure; audit next round. Formal home: Furr 2008 normative/distinctive decomposition; stylome (van Halteren 2005); non-ergodicity (Molenaar 2004, Fisher 2018) — see SUICA_LINGUISTIC_FOUNDATIONS_V1.md |
| THEORY-F | Formal derivations F1-F6: raw style mean is a C1+C2 composite (F1/F2); disjoint-set estimand isolates flesh up to the Cov(f,m) cross-term (F3); centering = mediator adjustment removing exactly Var(m)+2Cov(f,m) at first order, with exogenous-assignment boundary condition (F4); H(M) is loading-weighted (F5); overidentifying constraints incl. the transport bound cross <= sqrt(w1*w2) (F6) | docs/SUICA_THEORY_FORMAL_NOTES_V1.md | **computed_pending_audit (derivations + simulation shadows)** | Converts the empirical P2/E1 centering result into an algebraic identity with boundary conditions; first formalization of the model since inception |
| WW-SUITE | Wrong-world identifiability suite: 9 violation worlds vs the frozen estimator layer (per-world seeds after round-9 stream-fragility finding) | results/suica_theory_wrongworld_suite_v1/ | **round-9 audited: 7/9 pass + 2 recorded FAILs, one shared adjudicated mechanism** | FINAL FROZEN NUMBERS. PASS: W-A choice-null (frozen strict AUC deflates under ties to 0.039 — conservative, ties=losses per the E3 convention; mid-tie 0.5001/0.4975 at two sparsity levels; no fabrication), W-B flesh-null (raw retest 0.637 and shared-set 0.430 from choice alone — T4 hole demonstrated; disjoint -0.071; mix_share ~1.0), W-B2 grid (recovery max err 0.052), **W-B2c class-correlated b (round-9 addition — audit caught it referenced-but-missing): class-disjoint arm covariance reads Var(f)=1.005 at 0.890 (within tolerance) while condition-disjoint over-reads at 0.996 (+0.106) => the CLASS-DISJOINT estimand is now wrong-world LICENSED**, W-C timescale (obs month lag1 -0.054 vs analytic alias 0.161 — no fabrication; simplified lag-1 estimator, NOT the E7 MixedLM chain — scope noted), W-D simplified E6-ANALOG congruence null (FPR 0.01; not the full E6 matched estimator — wording per round-9), W-E leak-mask sufficiency (unmasked 0.578 -> masked 0.115 <= null95 0.192 at n_surv=108; DISCLOSURE: survivors gate lowered 100->60 mid-program after an rng-stream shift produced NaN — statistical criterion unchanged, conclusion stream-invariant per audit forensics). RECORDED FAILS (both = population-composition bias under strong flesh-choice coupling; mechanism CONFIRMED by round-9 oracle-b experiment — with true b the F4 identity is exact (-1.332 vs -1.335) and bhat-on-b slope is 1.403 at kappa=0.7 vs 1.002 at kappa=0): W-B3 mediated_total over-estimates under coupling (0.541 vs target 0.426; +0.115 vs +/-0.10 tolerance) => estimator valid as an UPPER bound on mediation; W-PHASE strong-coupling cell over-removes (-1.583 vs first-order -1.294; exogenous +0.010 ~= 0 and kappa=0 -0.316 vs -0.304 PASS — sign/boundary structure confirmed). SUITE-DEFECT LOG: v1 draft's tie-unsafe AUC fabricated 0.947 on the tied null; corrected to the exact frozen E3 strict convention + mid-tie variant (nuance: suite excludes permutation self-pairs, frozen E3 does not — expected ~1 pair at n=800, immaterial). Standing rules: suites replicate frozen estimator conventions exactly; per-world seeds mandatory |
| C2-PURITY | Per-construct decomposition of "style-base stability" into flesh vs choice-mediated shares (Tier-U, label-free; estimators licensed by W-B/W-B2/W-B3) | results/suica_c2_purity_decomposition_v1/ | **computed_pending_audit — THEORY CORRECTION TRIGGERED** | first_person: share 0.279 [0.208,0.349], class-disjoint 0.268 -> flesh-dominant (~72%). directive: 0.471 [0.226,0.662] -> C1+C2 composite. **novelty: 0.587 [0.428,0.723], class-disjoint 0.033 -> RELABELED venue-signature (C1-dominant), not a style trait** (pre-committed rule: share > 0.30 => relabel). tension/adversity: undetermined (shared-matched < 0.10; consistent with no-trait/dead verdicts). H(M) gradient holds for rind-loaded constructs only (F5 refinement). Explains lockbox H3 failure, PRED-1 novelty gain, E9a novelty MTMM fail; the sole flesh-dominant construct (first_person) is the one that passed T4 — channel accounting closes. THEORY_BASE section 7 (v3.2) + registry updated; v4 flesh-purity gate added (class-disjoint >= 0.15 AND share < 0.30). **Round-9 audit (UPHELD-WITH-CORRECTIONS, applied)**: 25/25 estimates recomputed exactly; volume-fairness confirmed (log slice-ratio median +0.000, symmetric); attenuation attack defeated (SB-corrected shares stable: fp 0.283 / novelty 0.615 / directive 0.479). Corrections: (i) the share formula that RAN (1 - cond_disjoint/shared_matched) differs from the matrix's original ((raw - same_rind)/raw) — a derivation-driven revision (F2: same-rind cannot purify) that left the matrix stale until the round-9 revision note; under the original formula tension/adversity would also relabel, but only via near-zero noise correlations the implemented shared>=0.10 guard correctly refuses; (ii) F6.3 misspecification alarm FIRES for first_person (cond-share 0.279 / mediated_total 0.398 / class-share 0.442) and directive (0.471/0.229) -> **flesh shares are BANDS, fp ~0.56-0.72** (mediated_total = upper bound on mediation under coupling per W-B3, so its arm gives flesh >= 0.60); novelty's estimators agree (0.587/0.588); (iii) "explains" downgraded to "consistent with" for H3/E9a (a choice-mediated construct can still predict O through choice, cf. H6 politics r=+0.096 T4); (iv) class-disjoint estimand licensed post hoc by W-B2c; (v) v4 gate marked PROVISIONAL (post-hoc thresholds; fp passes the share arm on point estimate only, CI spans 0.30); (vi) H(M) pre-committed direction violated 2/5 (fp hairline 0.693 vs 0.700; adversity unreadable noise cov_raw ~0.0004) — T9 trigger fired, loading-weighted form adopted as POST-HOC amendment (THEORY 7.4); (vii) tension's selection-conditioned bootstrap CI removed from interpretation |
| OP-8-S1 | A Japanese scorer with the frozen composition formulas is computationally sound (stage 1 of the 3-stage equivalence protocol) | results/suica_ja_scorer_v1/ja_scorer_selftest.json | **pass (round-8 audited, corrections applied; machinery-grade)** | fugashi/MeCab morphemes, 7 forward-translated lexicons, formulas identical to score_slices_v2. Synthetic planted-truth recovery 0.914-0.952 @120 sentences (short-text 40-sentence attenuation 0.868-0.902 disclosed); null 95th-pct \|rho\| 0.24-0.30 consistent with the 2/sqrt(60) noise expectation (audit: all 4 values inside the 40-draw estimator's sampling band); deterministic; audit rerun reproduced exactly. Round-8 adjudication: the 40->120 sentence volume fix is LEGITIMATE harness specification (bar never moved; 120 sentences moves TOWARD the EN P0 volume ~3,960 tokens and stays below it; 40-sent near-misses within n=60 sampling noise; disclosed throughout) — pass certifies machinery, not sensitivity at realistic post lengths. CONFIRMED DEFECT for stage 2: するな prohibitive pattern ~89% false-positive in the X market register (するなど/するなんて/particle-な; 気がするな double-fires uncertainty+directive on overlapping surfaces) — impact bounded (tiny frequency, directive gated by x second_person, selftest unaffected), lookahead extension required. Stages 2 (independent back-check) and 3 (within-JP-language re-validation) OPEN; no measurement claims licensed (protocol doc: SUICA_JP_SCORER_PROTOCOL_V1.md) |
| OP-7a | The frozen style battery transports across the Reddit dialogue-register boundary (top-level broadcast vs reply turns, parent_id t3_/t1_) | results/suica_op7a_dialogue_register_proxy_v1/ | **pass (round-8 audited, corrections applied)** | n=1,976 deep users with >= 6 slices in all 4 register x contiguous-half cells. **19/19 constructs register-robust** (opposite-half cross >= 0.70 x min within-register; e.g. first_person within 0.78/0.86 cross 0.74; directive 0.61/0.65 cross 0.49 — tightest ratio 0.79 = wcl_54, directive 0.81). Material level shifts only for wcl_36 family-narrative (dz +0.86, replies richer in personal narrative) and wcl_02 sports/near-choice (dz +0.56) -> per-register norms recommended for those two. Same-occasion cross runs +0.081 above opposite-half (OP-15 adjacency inflation reconfirmed). Round-8 corrections: "time-separated" was overstated — cross comment SETS are disjoint opposite halves but per-user WINDOWS overlap for 43-55% of users (median midpoint gap ~2 yr); audit's strict-separation AND volume-matched sensitivity checks both leave 19/19 robust (SB-benchmark transports 0.740-0.972; weakest wcl_54 ~0.70-0.75 marginal). Register volume asymmetry (reply 79.9 vs top 45.4 slices) noted; verdicts stable under volume matching. SCOPE: Reddit-internal register boundary = PRECURSOR evidence; OP-7 proper (AI dialogue, echo rate) still needs data collection |

## Audit log

- 2026-07-07 (round 9 — no-lock theory program): FORMAL_NOTES, wrong-world
  suite, and C2 purity decomposition all audited UPHELD-WITH-CORRECTIONS.
  Auditor's own attacks defeated: suite bit-identical rerun; decomposition
  25/25 exact; volume-fairness symmetric; attenuation attack neutralized by
  SB-corrected shares; the composition-bias mechanism CONFIRMED by the
  auditor's oracle-b experiment (identity exact with true b; bhat slope
  1.403 under coupling). Real catches, all applied: F3 needed the pi ⊥ b
  condition (residual cov(m^A,m^B)>0 under coupling); F4 "exactly" needed
  the no-coupling qualifier; stale first-draft numbers in three documents
  replaced by final frozen values; the matrix's original DS share formula
  and W-A/W-B expectations were superseded by the F2 derivation without a
  revision note (added, dated); W-B2c was referenced but NOT implemented —
  the class-disjoint estimand (basis of the novelty relabel) ran unlicensed
  until round 9 implemented and passed it; F6.3 alarm fires for
  first_person/directive -> flesh shares now reported as bands (fp
  ~0.56-0.72); "explains" -> "consistent with"; v4 gate marked provisional;
  H(M) T9 trigger disclosure; W-E gate change disclosed; W-D relabeled
  "simplified E6-analog". Builder overstatement count: rounds 1-9 now show
  builder errors caught in 7 of 9 rounds — the adversarial protocol remains
  the project's most reliable instrument.

- 2026-07-07 (round 8): opening execution + OP-7a + OP-8-S1 audited.
  OPENING UPHELD with exact reproduction (worst deviation 1.1e-16 across all
  r/p/CI/q; chain of custody verified against the PUBLIC GitHub tag — peeled
  hash == seal commit, sealed PREREGISTRATION byte-identical; no second-look
  traces; tf_flip verified from raw types corr=-1.0000; negative delta-R^2
  confirmed as convention-overfitting, not bug). OP-7a UPHELD-WITH-CORRECTIONS
  (19/19 stands under BOTH volume-matched and strict-time-separation
  sensitivity; "time-separated" wording corrected to opposite-half /
  overlapping windows for 43-55% of users; tightest ratio 0.79 not 0.81).
  OP-8-S1 UPHELD-WITH-CORRECTIONS (40->120 sentence volume adjudicated
  legitimate harness specification — bar unmoved, disclosed, moves toward the
  EN P0 volume; するな regex ~89% false-positive in the X register logged as
  a stage-2 fix; null-threshold wording softened to "consistent with").
  Builder wording overstatements caught this round: "transported nearly
  unchanged" (cross-population continuity implied from different corpus +
  anchor instrument) and "all TIME-SEPARATED" — both corrected in rows.

- 2026-07-07 (LOCKBOX OPENING #1): executed under the sealed prereg after the
  pre-opening adversarial audit (sole MUST-FIX was git provenance; script
  committed at cd63d13 with the audited sha256 unchanged, then opened).
  Verdict recorded regardless of outcome per the frozen rule: P5 FAIL, 2/7.
  Reading discipline: the two T4 confirmations are exactly the two channels
  the falsification path had converged on (C2 first-person style base;
  C1 choice), while the five failures are constructs/axes whose dev-tier
  evidence was already weak (tension no-trait; novelty/directive small),
  venue-coupled, or operationally underdetermined (entropy — null under all
  three declared variants). The confirmatory bar did its job; no rescue
  analysis will be run on this opening.

- 2026-07-07 (post-freeze hygiene, pre-opening): (a) FULL-NUMBER SWEEP of the
  worked-example manual by an independent verification agent: 123 numeric
  claims traced, 120 rounding-exact against primary artifacts (all 45
  performance-table cells and every q<.05 edge count recounted exactly).
  Fixes applied to manual+ledger in both repos: P0 recovery range 0.96-0.98
  (was understated 0.96-0.97), ledger P0 null FPR 0.075 -> 0.06 (artifact
  value; 0.075 was the pre-seed-fix run), E9b delta range +0.28 -> +0.30,
  S6 script name v3 -> v2, adjective example CI corrected to the real
  artifact row, "6 rounds" -> "7 rounds", OP-18a wording now discloses the
  tension-SB 0.0022 shift, and the two ledger-only numbers (choice AUC 0.909;
  contiguous SB 0.27) are now provenance-annotated in the manual.
  (b) E11 shuffled-score-fit null geometry closed (see E11v2 row addenda):
  old random-direction bar was CONSERVATIVE (fitted-null thr ratios
  0.59-0.82 trait / 0.27-0.39 state; real FPR of old bar <= 0.0013);
  corrected recount 7/19 trait axis-licensed (V2-2 >= 8 still FAILS),
  state f5 A-/C- licensed; descriptive-only ruling unchanged per
  pre-committed D3.


- 2026-07-05 (round 6): OP-5 and OP-10b audited. OP-5 UPHELD on every attack
  (first zero-correction run): A/B integrity proven, r_B independently
  reproduced (max diff 0.010), no volume confound, 0/15 over the choice-axis
  redundancy bar (caveat: wcl_02 joint-R^2 0.63 near-duplicate; wcl_60
  confirmed as apostrophe-omission orthographic register — rename, not
  artifact). OP-10b's FAIL verdict OVERTURNED as a harness bug: lbfgs
  boundary collapse (incl. one falsely converged fit); converged multi-start
  REML recovers planted 0.05/0.02. Harness fixed (best-llf across
  bfgs/lbfgs/cg) and rerun: P0B PASS -> MixedLM (multi-start) certified as
  the thin-cell headline estimator; the builder's interim "detection floor
  ~0.05" statement is retracted. Standing rule: any variance-component fit
  must be selected by best restricted loglik across multiple optimizers, and
  convergence flags alone must not be trusted.

- 2026-07-04: ledger created. External review session findings incorporated.
  Builder/auditor rule active: analysis authors mark results
  `computed_pending_audit`; an independent audit pass promotes/demotes.
- 2026-07-05 (round 5): E6/E7/P1-deep audited. E6 re-adjudicated UP
  (weak_partial -> signature_revived): builder's estimand asymmetry both
  inflated (novelty/adversity) and understated (first_person/directive)
  increments; fair matched estimator passes the pre-committed 2-construct
  rule. E7b criterion exposed as vacuous (congruence bar cannot fail);
  replaced by cross-half covariance evidence. E7c adjudicated to 2 decaying
  state modes vs the correct negative null. E7d upheld. Bugs recorded in the
  E6/E7 scripts (estimand gates, one-sided bootstrap, single-draw nulls).
  Standing rules added: matched estimands for same-vs-stranger comparisons;
  null distributions from >= 200 draws; any replication criterion must be
  shown capable of failing (include a null world).
- 2026-07-05 (round 3): rind-regime audit completed. PRED-1 demoted 4/4 ->
  3/4 (tension = temporal artifact; fixed arm must be span-matched in any
  future run). PRED-3 corrected (24-feature bug at
  run_suica_rind_regime_test_v3.py:217 — derived feature inflated structure
  agreement; true 23-feature values 0.530-0.620). PRED-2 upheld (all-pairs
  0.820; 17-symbol corpus). Essays governance verified clean (labels never
  loaded; 50/50 split exact). Open process gap: theory doc / scripts /
  results are untracked in git, so pre-commitment is not yet provable —
  requires user authorization to commit.
- 2026-07-05: exploration-phase audit completed. E1 "FE rescue" OVERTURNED
  (self-estimation leak; out-of-sample deltas negative for every construct —
  the strongest rescue attempt confirms P2's original verdict). E4 react
  revival OVERTURNED as individual evidence (wrong null; stranger baseline
  0.25-0.31 absorbs most of the signature). E2/E3/P3 upheld (E3 recomputed
  exactly; P3 bit-exact). Ledger bugs fixed: false "nulls ~0" note on E4;
  stale P3 row. Lesson recorded: any future reference-model estimation must be
  cross-fitted (estimate on data disjoint from the scored units), and react
  claims must use stranger-corrected nulls.
- 2026-07-04 (later): independent adversarial audit completed. All four
  verdicts (P0 pass, P1 fail, P2a/P2b fail, P4 partial) UPHELD after attack;
  headline numbers reproduced exactly by independent reimplementation.
  Corrections applied: (1) P4 MixedLM tension "topic-driven" claim struck as a
  degenerate fit; (2) P0 world seeds fixed to constants (were hash-salted,
  non-reproducible); (3) P0 MixedLM benchmark completed by auditor (MoM matches
  MixedLM). Audit addendum recorded: raw (uncentered) P1 variant would pass —
  P1/P2 failures share one cause: the centering mechanism discards
  self-selection signal. Tier separation verified (0 Tier-L authors in dev
  extraction).
