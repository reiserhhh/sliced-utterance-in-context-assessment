# SUICA V7 Registered Cross-Representation Operator Family

## Design

This run freezes five observation operators and two representations before any
result inspection: `whole`, `native`, `sentence_pack_160`,
`fixed_128_cross`, `fixed_128_within_comment`; `WORD12_TFIDF_SVD24` and
`CHAR35_TFIDF_SVD24`. The selected cohort excludes reconstructed E0, E1, and
E2 author cohorts. No external label was read.

All shared-subspace, directed-edge, same-operator cross-representation, and
source-disjoint technical-transport endpoints are corrected together by one
synchronized max-T permutation family (`B=199`). A failed endpoint is
`UNRESOLVED_VIEW_SPECIFIC`; it is not evidence that an operator's private
structure is absent or noise.

## Endpoints

| family_component          | representation                         | source                   | target                   |   statistic |   max_t_fwer_p | status                   |
|:--------------------------|:---------------------------------------|:-------------------------|:-------------------------|------------:|---------------:|:-------------------------|
| shared_subspace           | WORD12_TFIDF_SVD24                     | all_views                | all_views                |       0.113 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | whole                    | native                   |       0.334 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | whole                    | sentence_pack_160        |       0.368 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | whole                    | fixed_128_cross          |       0.421 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | whole                    | fixed_128_within_comment |       0.374 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | native                   | whole                    |       0.704 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | native                   | sentence_pack_160        |       0.942 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | native                   | fixed_128_cross          |       0.401 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | native                   | fixed_128_within_comment |       0.930 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | sentence_pack_160        | whole                    |       0.749 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | sentence_pack_160        | native                   |       0.943 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | sentence_pack_160        | fixed_128_cross          |       0.449 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | sentence_pack_160        | fixed_128_within_comment |       0.968 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_cross          | whole                    |       0.848 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_cross          | native                   |       0.382 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_cross          | sentence_pack_160        |       0.445 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_cross          | fixed_128_within_comment |       0.460 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_within_comment | whole                    |       0.762 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_within_comment | native                   |       0.931 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_within_comment | sentence_pack_160        |       0.967 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_within_comment | fixed_128_cross          |       0.459 |          0.005 | FWER_SUPPORTED           |
| source_disjoint_transport | WORD12_TFIDF_SVD24                     | whole                    | whole                    |       0.022 |          0.005 | FWER_SUPPORTED           |
| source_disjoint_transport | WORD12_TFIDF_SVD24                     | native                   | native                   |      -0.239 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | WORD12_TFIDF_SVD24                     | sentence_pack_160        | sentence_pack_160        |      -0.256 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | WORD12_TFIDF_SVD24                     | fixed_128_cross          | fixed_128_cross          |      -0.163 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | WORD12_TFIDF_SVD24                     | fixed_128_within_comment | fixed_128_within_comment |      -0.263 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| shared_subspace           | CHAR35_TFIDF_SVD24                     | all_views                | all_views                |       0.117 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | whole                    | native                   |       0.373 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | whole                    | sentence_pack_160        |       0.395 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | whole                    | fixed_128_cross          |       0.394 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | whole                    | fixed_128_within_comment |       0.400 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | native                   | whole                    |       0.684 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | native                   | sentence_pack_160        |       0.944 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | native                   | fixed_128_cross          |       0.372 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | native                   | fixed_128_within_comment |       0.932 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | sentence_pack_160        | whole                    |       0.722 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | sentence_pack_160        | native                   |       0.943 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | sentence_pack_160        | fixed_128_cross          |       0.429 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | sentence_pack_160        | fixed_128_within_comment |       0.962 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_cross          | whole                    |       0.828 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_cross          | native                   |       0.426 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_cross          | sentence_pack_160        |       0.482 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_cross          | fixed_128_within_comment |       0.488 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_within_comment | whole                    |       0.732 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_within_comment | native                   |       0.933 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_within_comment | sentence_pack_160        |       0.961 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_within_comment | fixed_128_cross          |       0.434 |          0.005 | FWER_SUPPORTED           |
| source_disjoint_transport | CHAR35_TFIDF_SVD24                     | whole                    | whole                    |       0.077 |          0.005 | FWER_SUPPORTED           |
| source_disjoint_transport | CHAR35_TFIDF_SVD24                     | native                   | native                   |      -0.125 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | CHAR35_TFIDF_SVD24                     | sentence_pack_160        | sentence_pack_160        |      -0.143 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | CHAR35_TFIDF_SVD24                     | fixed_128_cross          | fixed_128_cross          |      -0.101 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | CHAR35_TFIDF_SVD24                     | fixed_128_within_comment | fixed_128_within_comment |      -0.140 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| cross_representation      | WORD12_TFIDF_SVD24->CHAR35_TFIDF_SVD24 | whole                    | whole                    |       0.479 |          0.005 | FWER_SUPPORTED           |
| cross_representation      | CHAR35_TFIDF_SVD24->WORD12_TFIDF_SVD24 | whole                    | whole                    |       0.442 |          0.005 | FWER_SUPPORTED           |
| cross_representation      | WORD12_TFIDF_SVD24->CHAR35_TFIDF_SVD24 | native                   | native                   |       0.255 |          0.005 | FWER_SUPPORTED           |
| cross_representation      | CHAR35_TFIDF_SVD24->WORD12_TFIDF_SVD24 | native                   | native                   |       0.195 |          0.005 | FWER_SUPPORTED           |
| cross_representation      | WORD12_TFIDF_SVD24->CHAR35_TFIDF_SVD24 | sentence_pack_160        | sentence_pack_160        |       0.254 |          0.005 | FWER_SUPPORTED           |
| cross_representation      | CHAR35_TFIDF_SVD24->WORD12_TFIDF_SVD24 | sentence_pack_160        | sentence_pack_160        |       0.199 |          0.005 | FWER_SUPPORTED           |
| cross_representation      | WORD12_TFIDF_SVD24->CHAR35_TFIDF_SVD24 | fixed_128_cross          | fixed_128_cross          |       0.177 |          0.005 | FWER_SUPPORTED           |
| cross_representation      | CHAR35_TFIDF_SVD24->WORD12_TFIDF_SVD24 | fixed_128_cross          | fixed_128_cross          |       0.161 |          0.005 | FWER_SUPPORTED           |
| cross_representation      | WORD12_TFIDF_SVD24->CHAR35_TFIDF_SVD24 | fixed_128_within_comment | fixed_128_within_comment |       0.263 |          0.005 | FWER_SUPPORTED           |
| cross_representation      | CHAR35_TFIDF_SVD24->WORD12_TFIDF_SVD24 | fixed_128_within_comment | fixed_128_within_comment |       0.198 |          0.005 | FWER_SUPPORTED           |

## Source-Disjoint Alignment Control

This separate AUC family does not require a linear coordinate map. It compares
each source-disjoint left half with its own right half against right-half
strangers. It distinguishes stable relative author positioning from failure of
the stricter linear transport endpoint above. Its max-T correction is confined
to the ten registered alignment endpoints and is not pooled with R2 values.

| representation     | operator                 |   alignment_auc |   alignment_max_t_fwer_p | alignment_status   |
|:-------------------|:-------------------------|----------------:|-------------------------:|:-------------------|
| WORD12_TFIDF_SVD24 | whole                    |           0.796 |                    0.005 | FWER_SUPPORTED     |
| WORD12_TFIDF_SVD24 | native                   |           0.741 |                    0.005 | FWER_SUPPORTED     |
| WORD12_TFIDF_SVD24 | sentence_pack_160        |           0.748 |                    0.005 | FWER_SUPPORTED     |
| WORD12_TFIDF_SVD24 | fixed_128_cross          |           0.719 |                    0.005 | FWER_SUPPORTED     |
| WORD12_TFIDF_SVD24 | fixed_128_within_comment |           0.741 |                    0.005 | FWER_SUPPORTED     |
| CHAR35_TFIDF_SVD24 | whole                    |           0.805 |                    0.005 | FWER_SUPPORTED     |
| CHAR35_TFIDF_SVD24 | native                   |           0.761 |                    0.005 | FWER_SUPPORTED     |
| CHAR35_TFIDF_SVD24 | sentence_pack_160        |           0.775 |                    0.005 | FWER_SUPPORTED     |
| CHAR35_TFIDF_SVD24 | fixed_128_cross          |           0.720 |                    0.005 | FWER_SUPPORTED     |
| CHAR35_TFIDF_SVD24 | fixed_128_within_comment |           0.760 |                    0.005 | FWER_SUPPORTED     |

## Claim Boundary

These results can establish only registered, author-aligned transport within
the declared corpus, operator family, and representations. They do not name
factors, establish a universal best slice, identify personality, or license
clinical interpretation. `FWER_SUPPORTED` establishes only a registered
endpoint. A stronger `SHARED_WITHIN_OPERATOR_SET` label additionally requires
bootstrap loading-subspace recurrence and an independent fresh confirmation
family; it is not granted by this run alone.

## Artifacts

- `results/v7_operator_family/e4_v72_full_20260715_r3/registered_endpoints.csv`
- `results/v7_operator_family/e4_v72_full_20260715_r3/max_t_null.parquet` (or CSV fallback)
- `results/v7_operator_family/e4_v72_full_20260715_r3/source_disjoint_alignment.csv`
- `results/v7_operator_family/e4_v72_full_20260715_r3/source_disjoint_alignment_max_t_null.parquet` (or CSV fallback)
- `results/v7_operator_family/e4_v72_full_20260715_r3/run_manifest.json`
- `results/v7_operator_family/e4_v72_full_20260715_r3/artifact_inventory.json`
