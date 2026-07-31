# V8 Spectrum-Matched Orientation-Overlap Audit

Status: `ORIENTATION_UNDERRESOLVED`

This exploratory audit separates spectral concentration from orientation. It subtracts the isotropic floor, freezes an identifiable D0 rank, matches PANDORA/Essays spectra by geometric-mean weights, and compares orientation with spectrum-preserving Haar rotations.

## Data roles

| corpus   | source                                                                                              |   source_rows |   authors |   events | contexts                                           | context_role                 | replicate_type                    | external_labels_loaded   | split_counts                      |
|:---------|:----------------------------------------------------------------------------------------------------|--------------:|----------:|---------:|:---------------------------------------------------|:-----------------------------|:----------------------------------|:-------------------------|:----------------------------------|
| pandora  | /Volumes/mobile3/projects/project persona/data_sets/prepared/suica_tiers_v2/tier_u_comments.parquet |       1055389 |       384 |     3072 | ['AskReddit', 'politics', 'worldnews', 'AskWomen'] | SELF_SELECTED_OBSERVATIONAL  | SOURCE_COMMENT_DISJOINT_TECHNICAL | False                    | {'D0': 164, 'D1': 117, 'D2': 103} |
| essays   | /Volumes/mobile3/projects/project persona/data_sets/prepared/big5/essays_original_prepared.csv      |          2467 |       320 |     2560 | ['<single_essay_prompt>']                          | SINGLE_DOCUMENT_FIXED_PROMPT | WITHIN_DOCUMENT_PSEUDOREPLICATE   | False                    | {'D0': 126, 'D1': 99, 'D2': 95}   |

## D0 identification

| family   | status                         |   epsilon |   rank |   effective_rank_template |
|:---------|:-------------------------------|----------:|-------:|--------------------------:|
| M        | D0_ORIENTATION_UNDERRESOLVED   | 0.0425424 |      3 |                   1.67931 |
| K        | ORIENTATION_RANK_UNDERRESOLVED | 0.0630099 |    nan |                 nan       |

## Primary matched-spectrum HS cells

| family   | split   | arm              | metric   |   rank |   observed |   null_mean |      delta |   bootstrap_delta_low |   raw_rotation_p |   exact_intersection_rank |   max_haar_p | detected   |
|:---------|:--------|:-----------------|:---------|-------:|-----------:|------------:|-----------:|----------------------:|-----------------:|--------------------------:|-------------:|:-----------|
| M        | D1      | matched_spectrum | hs       |      3 |  0.0265753 |  0.00962163 | 0.0169537  |           -0.00265041 |             0.05 |                         0 |         0.05 | False      |
| M        | D2      | matched_spectrum | hs       |      3 |  0.0207541 |  0.013005   | 0.00774907 |           -0.00230824 |             0.2  |                         0 |         0.55 | False      |

Root fidelity is a secondary view of distributed weak overlap. Principal-angle affinity and exact-intersection rank are diagnostics. Parallel sum is not used as an approximate-overlap test because noisy low-rank subspaces generically have a zero exact intersection.

## Claim boundary

Exploratory orientation-only audit after spectral-order refusal. Matched-spectrum HS is primary, root fidelity is secondary, principal-angle affinity and exact intersection are diagnostics. Current D2 is already opened, so no result is independent confirmation or a psychological construct.
