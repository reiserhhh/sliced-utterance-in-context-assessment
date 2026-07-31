# V8 Spectrum-Matched Orientation-Overlap Audit

Status: `EXPLORATORY_ORIENTATION_OVERLAP_PARTIAL`

This exploratory audit separates spectral concentration from orientation. It subtracts the isotropic floor, freezes an identifiable D0 rank, matches PANDORA/Essays spectra by geometric-mean weights, and compares orientation with spectrum-preserving Haar rotations.

## Data roles

| corpus   | source                                                                                              |   source_rows |   authors |   events | contexts                                           | context_role                 | replicate_type                    | external_labels_loaded   | split_counts                      |
|:---------|:----------------------------------------------------------------------------------------------------|--------------:|----------:|---------:|:---------------------------------------------------|:-----------------------------|:----------------------------------|:-------------------------|:----------------------------------|
| pandora  | /Volumes/mobile3/projects/project persona/data_sets/prepared/suica_tiers_v2/tier_u_comments.parquet |       1055389 |       985 |     7880 | ['AskReddit', 'politics', 'worldnews', 'AskWomen'] | SELF_SELECTED_OBSERVATIONAL  | SOURCE_COMMENT_DISJOINT_TECHNICAL | False                    | {'D0': 420, 'D1': 296, 'D2': 269} |
| essays   | /Volumes/mobile3/projects/project persona/data_sets/prepared/big5/essays_original_prepared.csv      |          2467 |      1200 |     9600 | ['<single_essay_prompt>']                          | SINGLE_DOCUMENT_FIXED_PROMPT | WITHIN_DOCUMENT_PSEUDOREPLICATE   | False                    | {'D0': 463, 'D2': 372, 'D1': 365} |

## D0 identification

| family   | status                  |   epsilon |   rank |   effective_rank_template |
|:---------|:------------------------|----------:|-------:|--------------------------:|
| M        | ORIENTATION_AUDIT_READY | 0.042608  |      2 |                   1.51892 |
| K        | ORIENTATION_AUDIT_READY | 0.0209347 |     12 |                   8.08494 |

## Primary matched-spectrum HS cells

| family   | split   | arm              | metric   |   rank |   observed |   null_mean |     delta |   bootstrap_delta_low |   raw_rotation_p |   exact_intersection_rank |   max_haar_p | detected   |
|:---------|:--------|:-----------------|:---------|-------:|-----------:|------------:|----------:|----------------------:|-----------------:|--------------------------:|-------------:|:-----------|
| M        | D1      | matched_spectrum | hs       |      2 |  0.0273065 |  0.00897334 | 0.0183331 |           -0.00414684 |            0.05  |                         0 |        0.198 | False      |
| M        | D2      | matched_spectrum | hs       |      2 |  0.0438092 |  0.00901412 | 0.034795  |           -0.00226506 |            0.006 |                         0 |        0.016 | False      |
| K        | D1      | matched_spectrum | hs       |     12 |  0.0883565 |  0.0526877  | 0.0356688 |            0.0157117  |            0.002 |                         0 |        0.014 | True       |
| K        | D2      | matched_spectrum | hs       |     12 |  0.126237  |  0.0533459  | 0.0728911 |            0.0254762  |            0.002 |                         0 |        0.002 | True       |

Root fidelity is a secondary view of distributed weak overlap. Principal-angle affinity and exact-intersection rank are diagnostics. Parallel sum is not used as an approximate-overlap test because noisy low-rank subspaces generically have a zero exact intersection.

## Claim boundary

Exploratory orientation-only audit after spectral-order refusal. Matched-spectrum HS is primary, root fidelity is secondary, principal-angle affinity and exact intersection are diagnostics. Current D2 is already opened, so no result is independent confirmation or a psychological construct.
