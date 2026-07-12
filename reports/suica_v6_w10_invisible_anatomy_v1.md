# V6-W10 -- Anatomy of the invisible (motion-only) gust factor

F15, registered commit 52421ea, docs/SUICA_THEORY_FORMAL_NOTES_V3.md. Label-free (Tier-U + Essays TEXT only).

CAPPED-CORPUS RUN: Both caches derive from the CURRENT CAPPED Tier-U / Essays extraction (docs/SUICA_THEORY_FORMAL_NOTES_V3.md F14/N1): comment bodies are capped, which limits observed m (mostly m=3 in the PANDORA m>=3 slice used here). An uncapped re-extraction (tier_u_comments_uncapped_v1.parquet) is registered to follow N1; this is the CAPPED-corpus version of W10.

## Axis: gust1_P

Top eigenvalue 2.2226 from 618 PANDORA m==3 texts. Drift guard (top-2 |loading| in {wcl_02, wcl_11}): PASS (['wcl_02', 'wcl_11']). novelty_play_v2 loading: -0.0044.

| construct | loading |
|---|---|
| wcl_02 | -0.4713 |
| wcl_11 | +0.4538 |
| wcl_07 | -0.4039 |
| wcl_20 | +0.3129 |
| wcl_25 | -0.2467 |
| wcl_35 | +0.2213 |
| wcl_22 | -0.2069 |
| first_person_usage_v2 | +0.1959 |
| tension_core_v2 | -0.1779 |
| directive_action_v2 | -0.1727 |
| wcl_03 | -0.1460 |
| wcl_15 | -0.1151 |
| wcl_13 | -0.0922 |
| wcl_23 | -0.0841 |
| wcl_54 | +0.0618 |
| wcl_45 | -0.0455 |
| wcl_36 | +0.0440 |
| wcl_60 | +0.0209 |
| novelty_play_v2 | -0.0044 |

## A. Activation anatomy (PANDORA, m>=3)

2196 windows, 687 texts.

### |a_w| (magnitude) marker table

| marker | r_centered | r_raw | perm_p (centered) | n |
|---|---|---|---|---|
| allcaps_token_share | 0.160963 | 0.223483 | 0.0 | 2196 |
| digit_per100 | 0.127052 | 0.180736 | 0.0 | 2196 |
| comma_per100 | -0.075747 | -0.117071 | 0.002 | 2196 |
| position_t | -0.031615 | -0.017542 | 0.176 | 2196 |
| novelty_jump | 0.026451 | -0.105717 | 0.06 | 1509 |
| quote_per100 | 0.004885 | -0.006109 | 0.896 | 2196 |
| qmark_per100 | -0.00328 | -0.107234 | 0.848 | 2196 |
| novelty_level | 0.002888 | -0.099056 | 0.806 | 2196 |
| token_count | None | None | None | 2196 |

### signed a_w (direction) marker table

| marker | r_centered | r_raw | perm_p (centered) | n |
|---|---|---|---|---|
| allcaps_token_share | -0.084984 | -0.040624 | 0.0 | 2196 |
| quote_per100 | -0.08187 | -0.040279 | 0.0 | 2196 |
| qmark_per100 | 0.066258 | 0.026825 | 0.0 | 2196 |
| comma_per100 | -0.041664 | -0.022479 | 0.102 | 2196 |
| novelty_level | -0.015571 | -0.011257 | 0.29 | 2196 |
| novelty_jump | 0.003545 | 0.021701 | 0.826 | 1509 |
| digit_per100 | -0.001104 | -0.000529 | 0.98 | 2196 |
| position_t | -0.0 | -0.0 | 1.0 | 2196 |
| token_count | None | None | None | 2196 |

## B. Person susceptibility (PANDORA)

n_users=81 (>=2 qualifying m>=3 texts), n_texts_pooled=458

- r_susceptibility (|a| split-half): 0.441232
- r_direction (signed a split-half): -0.127939
- ICC-style share var(user means)/var(all) for |a|: 0.380736

Order assumption: Section B 'text order' for the odd/even split-half is taken as ascending cid -- the pipeline's own sequential assignment order (each user's texts in their original tier_u_comments.parquet row order). No timestamp column is loaded anywhere in this script (label/metadata-minimal, text-only governance), so this order is a documented ASSUMPTION, not a verified chronological order.

## C. Essays contrast (matched within-text column-shuffle null, 200 draws)

| corpus | n_windows | obs_var | null_mean | null [2.5%,97.5%] | ratio | p(null>=obs) |
|---|---|---|---|---|---|---|
| PANDORA | 2196 | 1.686372 | 1.004999 | [0.91442, 1.111339] | 1.677984 | 0.0 |
| Essays | 11667 | 1.03505 | 0.999944 | [0.973466, 1.025284] | 1.035108 | 0.005 |

Expectation: PANDORA ratio >> 1, Essays ratio ~ 1.

## Notes / ambiguities

- Both caches derive from the CURRENT CAPPED Tier-U / Essays extraction (docs/SUICA_THEORY_FORMAL_NOTES_V3.md F14/N1): comment bodies are capped, which limits observed m (mostly m=3 in the PANDORA m>=3 slice used here). An uncapped re-extraction (tier_u_comments_uncapped_v1.parquet) is registered to follow N1; this is the CAPPED-corpus version of W10.
- Section B 'text order' for the odd/even split-half is taken as ascending cid -- the pipeline's own sequential assignment order (each user's texts in their original tier_u_comments.parquet row order). No timestamp column is loaded anywhere in this script (label/metadata-minimal, text-only governance), so this order is a documented ASSUMPTION, not a verified chronological order.
- gust1_P's sign is whatever np.linalg.eigh returns for this data (arbitrary but deterministic/reproducible); 'signed a_w' / 'direction' readings inherit that fixed sign convention, consistent with prior W2a/W6 usage of the same axis.
- perm_p_centered tests r_centered specifically: a within-text shuffle of a_w is the natural exchangeability null for the within-text-demeaned correlation. It is NOT a valid null for r_raw, whose between-text covariance component survives a within-text-only shuffle; r_raw is reported for transparency/comparison only, without a matching p-value.
- Essays window text was reconstructed and row-for-row aligned to the cache per the DATA governance spec (see [align] Essays log line), but is not used numerically in Sections A-C: Section A's marker analysis is PANDORA-only per the registration, and Section C only needs Essays' numeric residual/activation, not its markers.
- ALL-CAPS token share requires >=2 alphabetic chars per token (excludes single-letter words such as the pronoun 'I' from inflating the share); this is a reasonable but not spec-dictated convention.
- token_count is a STRUCTURALLY DEGENERATE marker in this design: windows are built as exactly WIN=128-token slices (run_suica_tgeo_p7_flow_curve_v1 / run_suica_v6_e2_essays_motion_v1), and re-tokenizing the joined window text deterministically returns exactly 128 tokens every time (verified), so token_count has zero variance across all windows and its correlation with a_w is undefined (reported as null/None rather than a misleading 0).
