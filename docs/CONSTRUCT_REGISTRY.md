# SUICA Construct Registry v1

Created: 2026-07-05 (referee sweep). Operational names ONLY — psychological
names are earned at T4 (lockbox) or human-criterion evidence, not before
(jingle-fallacy rule, R1-2). Every entry lists channel, evidence tier
(see CLAIMS_LEDGER taxonomy), and caveats.

## Tier A — style-register measures (person-stable text behavior)

| ID | Operational name | Channel | Disjoint-occasion r (T3 where marked) | Caveats |
|----|------------------|---------|----------------------------------------|---------|
| first_person_usage_v2 | First-person pronoun rate | C2 style + C3 signature (provisional) + state deviation (best available) | raw retest SB 0.79-0.86 (T2); E6 signature +0.154 (T3-ish, single cohort) | the single strongest measure in the system |
| directive_action_v2 | Directive+second-person blend | C2 style + C3 signature (provisional) | SB ~0.57-0.65 (T2); E6 +0.148 | contains "don't" — see apostrophe note |
| wcl_60 | Apostrophe-omission register (was: contraction-style cluster) | C2 style | r_B 0.649 (T3) | measures typed orthographic habit; ~3.8% of slices carry smart quotes (device confound bounded); normalize U+2019 in v4 scorer |
| wcl_03 | Positive-enthusiasm vocabulary rate | C2 style | r_B 0.579 (T3) | |
| wcl_45 | Epistemic-argument vocabulary rate | C2 style | r_B 0.522 (T3) | shares words with certainty/mentalization lexicons — disjointify in v4 |
| wcl_54 | Analytic-formal function-word rate | C2 style | r_B 0.473 (T3) | |
| wcl_13 | Negation-argument rate | C2 style | r_B 0.454 (T3) | partially apostrophe-splitting fragments (don/doesn) |
| wcl_15 | Casual-interjection rate | C2 style | r_B 0.444 (T3) | |
| wcl_23 | Profanity-intensity rate | C2 style | r_B 0.432 (T3) | |
| wcl_22 | Concrete-narrative function-word rate | C2 style | r_B 0.459 (T3) | interpretation weakest of the register set |

## Tier B — content-interest measures (choice-coupled; report separately)

| ID | Operational name | r_B | Choice coupling |
|----|------------------|-----|-----------------|
| wcl_36 | Family/personal-narrative vocabulary | 0.571 (T3) | joint-axes R^2 low |
| wcl_11 | Technical-practical vocabulary | 0.541 (T3) | joint R^2 ~0.55 (borderline choice duplicate) |
| wcl_25 | Media-narrative vocabulary | 0.516 (T3) | |
| wcl_02 | Sports vocabulary | 0.502 (T3) | joint R^2 0.63 — NEAR CHOICE DUPLICATE; do not report as independent style |
| wcl_07 | Politics/civic vocabulary | 0.495 (T3) | |
| wcl_35 | Media-consumption vocabulary | 0.451 (T3) | |
| wcl_20 | Gaming-mechanics vocabulary | 0.378 (T3) | joint R^2 ~0.56 (borderline) |
| novelty_play_v2 | Novelty/play vocabulary rate | raw SB ~0.65 (T2) | **RELABELED 2026-07-07: VENUE-SIGNATURE (C1-dominant)** — choice-mediated share 0.587 [0.428,0.723], class-disjoint retest 0.033 (c2_purity decomposition). NOT a style trait; fails the v4 flesh-purity gate; model in the choice family. Consistent with lockbox H3 failure + PRED-1 top gain + E9a MTMM fail (round-9 wording) |

## Tier C — state-unstable / retired-as-trait measures

| ID | Operational name | Status |
|----|------------------|--------|
| tension_core_v2 | Negative-affect+uncertainty vocabulary rate (was: Tension-Uncertainty Core) | NOT a trait (P1 SB 0.35; person share 2-6%), NOT an occasion state (<= ~2% at month/quarter); slice-level topical fluctuation. Retained only as an ingredient for future session-scale state designs (OP-16) |
| adversity_recovery_v2 | Strict adversity-recovery pattern score | near-zero everywhere at cap-400; weak positive on deep data (0.129); keep at T1 |

## OP-22 blind-coding outcomes (2026-07-06; 4-family LLM panel + human, pre-committed rules)

Legibility classification added to every candidate (guide rule G10):

| Legibility class | Constructs | Coding evidence |
|---|---|---|
| human+machine legible | wcl_45 epistemic (LLM 0.938/T2 1.00/human 7/8), wcl_23 profanity (human 6/8; T2 0.708 borderline-fail) | full pass (wcl_45); near (wcl_23) |
| content-tier, trivially legible | wcl_02/07/11/20/25/35/36 — all pass (LLM 0.73-0.98, human 5-8/8) | **coding NOT counted as validity** (topic labels are self-identifying); trait evidence remains T3 stability + choice-coupling |
| machine-mostly | wcl_03 positive-enthusiasm, wcl_13 negation, wcl_15 casual, wcl_54 analytic, wcl_22 concrete-narrative | T1 marginal (0.42-0.63), T2 fails (wcl_15 0.25, wcl_03 0.46 — readers' intensity intuition INVERTS vs count-based score); keep as T3-stable measures with reduced label confidence; rename toward operational wording |
| machine-only | **wcl_60 apostrophe-omission: human 0/8**, LLM pooled 0.469 (DeepSeek alone 0.75) | the researcher's own introspection ("読めない") exactly matched the data; validity basis = mechanism description + r_B 0.649, not reader recognition |

Panel quality: pairwise agreement 0.575-0.783 across 4 genuine families
(deepseek/qwen/llama/mistral-base) — real diversity, unlike the retired
same-family v1 panel. Human uncertainty markers: 11% on content items vs 34%
on style items.

## Candidate state dimensions (NOT constructs; E7, T2)

| ID | Working label | Evidence |
|----|---------------|----------|
| state_f3 | Reflective-opinionated mode | above-null monthly persistence +0.100, decaying; cell-state reliability 0.084-0.105 |
| state_f1 | Positivity/growth-evaluation mode | +0.069, decaying |
| state_f5 | Second-person/agency drift mode | +0.074-0.090, non-decaying at month (drift); best cell-state reliability (0.121-0.134) |

Naming rule: "candidate state dimension" until (a) lexicon-disjoint
recomputation (R2-2) and (b) any external state criterion exists.

## Choice axes (C1; held-out confirmation in OP-6a)

Named by content class: gaming, sports, politics/news, life-planning,
tech/beauty, narrative-media (+ 7 minor). choice_ax_11 (MBTI communities) is
LEAKAGE-EXCLUDED from all external validation. Compositional (sum-constrained)
scores — ipsativity note in Rulebook A3/E3; Thurstonian modeling listed as a
design upgrade for the M-choose-K module.
