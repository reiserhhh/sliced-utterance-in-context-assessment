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
| P0 | SUICA estimator chain is computationally correct (recovers planted effects; nulls stay null) | results/suica_synthetic_ground_truth_v2/p0_results.json | **pass (audited)** | rank recovery 0.96-0.97 (W1); dominant component 15/15; null FPR 0.075; react recovery r=0.94; scorer equivalence exact. Audit: MixedLM benchmark had silently skipped (module missing at run time); auditor ran it — MoM 0.744/0.008/0.017/0.232 vs MixedLM 0.736/0.009/0.028/0.227, matches. Hash-salted world seeds fixed to constants post-audit; auditor's fixed-seed rerun reproduced the pass (0.97+) |
| P1 | Disjoint-text, time-gapped base test-retest reaches SB-corrected r >= 0.60 for >= 3 constructs (median >= 0.50) | results/suica_p1_disjoint_retest_v2_s128/ | **fail (audited)** | n=1,437, gap median 115d. SB r: first_person 0.725, directive 0.526, tension 0.354, novelty 0.269, adversity 0.059. Only 1/5 passes; median 0.354. Same verdict at s96. Audit reproduced exactly; no deflating bug. **Audit addendum: the RAW (uncentered) variant would PASS (SB 0.856/0.650/0.650/0.446/0.166; 3/5 >= 0.60, median 0.650)** — P1's failure is caused by the centering mechanism, not absence of text signal. Volume curve: first_person reaches 0.86 at ~4.5k tokens/half; tension/novelty plateau (state-driven, not volume-limited) |
| P2a | Condition centering improves cross-condition-set stability for lexicon-rate constructs (pooled delta CI > 0) | results/suica_p2_condition_centering_v2_s128/ | **fail (audited)** | n=3,726. Pooled delta = -0.091, CI [-0.102, -0.080]: centering REDUCES stability for all 5 constructs. Same at s96 (-0.094). Audit attacks defeated: oracle centering gives same deltas (LOO noise irrelevant); restricting to conditions with >= 20 or >= 50 users keeps all deltas negative. Caveat retained: stability != validity — raw stability partly reflects stable venue self-selection |
| P2b | Condition centering improves cross-condition-set stability for node-occupancy scores (pooled delta CI > 0) | results/suica_p2_condition_centering_v2_s128/ | **fail (audited)** | mean node r: centered 0.096 vs raw 0.163; delta -0.067, CI negative. Audit: self-inclusion bias measured at +0.0005 (negligible); matched-noise global-reference control (0.172 > 0.163) shows the condition-relative reference itself causes the loss |
| P3 | Frozen SUICA scores are not redundant with generic lexica (R^2 <= 0.75 majority) | results/suica_p3_redundancy_v2_s128/ | **pass (audited, with caveats)** | All 23 targets Empath CV R^2 <= 0.428 (max = raw first_person; choice axes 0.01-0.36). Audit: no CV leakage, bit-exact reproduction. Caveats: Empath input capped at 24k chars vs full-slice targets (biases toward non-redundancy); the 5 fe_base rows are moot after E1 overturn |
| P4 | person x condition variance exists beyond noise; react signature split-half >= 0.30 for >= 2 constructs | results/suica_p4_variance_components_v2_s128/ | **partial (audited)** | Interaction share CI>0 for 2/5 (first_person 0.051, directive 0.039). React signature medians 0.009-0.187, all < 0.30 (nulls ~0; first_person 0.187 is real but small signal; criterion is attenuation-heavy on few-slice cells). MoM: first_person person=16.2%/condition=5.5%. Audit correction: the earlier "MixedLM corroborates: tension condition=45.3% (topic-driven)" claim is STRUCK — that fit is degenerate (empirical condition eta^2 = 0.97%); correct reading: tension is ~95% slice-level residual, person ~2-5% either way |
| P5 | <= 10 preregistered directional external hypotheses, single lockbox opening, BH-FDR in-set | (Phase 4; budget 2 openings remaining) | not_run | lockbox NOT opened |

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
| E9b | A person can be interpreted via the measured profiles of their embedding neighbors ("position -> profile translation", k=50, vs random-neighbor null) | same | **pass (round-7 audited)** | **PASS 18/19** (bar 8). Labeling corrected per audit: the values first_person 0.577 / family 0.573 / positive-enthusiasm 0.531 / apostrophe 0.293 are NEIGHBOR-READ r's (random-neighbor null ~0; deltas +0.28..+0.59, draw-dependent at the low edge). Audit verified: self-exclusion (0 self-inclusions in 3,183), fair null, independent kNN reproduction exact; borrowed-vs-early r=0.729 vs late 0.577 confirms the reported number is honestly cross-occasion. Sole failure: tension — consistent with its no-trait verdict |

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
| E11v2-trait | Metric adjective profiles with the four v1 fixes | results/suica_e11v2_adjective_trait/ | computed_pending_audit | V2-1 stability PASS (median bootstrap rank stability 0.868, v1 was 0.622); V2-3 discriminance PASS (0.080); **V2-2 FAIL: only 1/19 clears the permutation-calibrated marker-axis bar** — v1's ten enrichments confirmed as calibration artifacts (G11 family). CI-coherent weak alignments persist (novelty->E+/O+ +0.07; tension->N+; directive/profanity->A-). RULING: adjective profiles = descriptive aids with CIs; the licensed construct-trait bridge = dev-anchor label relations. Round-7 addendum: V2-4 also FAILS (null axis hit rate 0.026 > 0.02 — permutation calibration slightly anti-conservative); shuffled-score-fit null check remains open (round-7 INCOMPLETE item) |
| E11v2-state | Same machinery on the horizontal-cut state modes (f1/f3/f5; within-person centered month embeddings from the 4070) | results/suica_e11v2_adjective_state/ | computed_pending_audit | Direction stability 0.904-0.946; discriminant 0.044; 0/3 clear the strict marker-axis bar; CI-coherent leans match the modes' working interpretations (f1 positivity -> A+/O+/N-; f3 reflective -> N+; f5 -> C-/A-). Same ruling as traits: descriptive aids with CIs. Round-7 addendum: V2-4 FAIL (0.026) applies here too |
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

## Audit log

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
