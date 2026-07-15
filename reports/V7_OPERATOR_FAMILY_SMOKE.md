# SUICA V7 Registered Cross-Representation Operator Family

## Design

This run freezes five observation operators and two representations before any
result inspection: `whole`, `native`, `sentence_pack_160`,
`fixed_128_cross`, `fixed_128_within_comment`; `WORD12_TFIDF_SVD24` and
`CHAR35_TFIDF_SVD24`. The selected cohort excludes reconstructed E0, E1, and
E2 author cohorts. No external label was read.

All shared-subspace, directed-edge, same-operator cross-representation, and
source-disjoint technical-transport endpoints are corrected together by one
synchronized max-T permutation family (`B=29`). A failed endpoint is
`UNRESOLVED_VIEW_SPECIFIC`; it is not evidence that an operator's private
structure is absent or noise.

## Endpoints

| family_component          | representation                         | source                   | target                   |   statistic |   max_t_fwer_p | status                   |
|:--------------------------|:---------------------------------------|:-------------------------|:-------------------------|------------:|---------------:|:-------------------------|
| shared_subspace           | WORD12_TFIDF_SVD24                     | all_views                | all_views                |      -0.089 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | whole                    | native                   |      -0.129 |          0.667 | UNRESOLVED_VIEW_SPECIFIC |
| directed_edge             | WORD12_TFIDF_SVD24                     | whole                    | sentence_pack_160        |      -0.078 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | whole                    | fixed_128_cross          |       0.161 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | whole                    | fixed_128_within_comment |      -0.062 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | native                   | whole                    |       0.600 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | native                   | sentence_pack_160        |       0.928 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | native                   | fixed_128_cross          |       0.167 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | native                   | fixed_128_within_comment |       0.893 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | sentence_pack_160        | whole                    |       0.661 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | sentence_pack_160        | native                   |       0.931 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | sentence_pack_160        | fixed_128_cross          |       0.197 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | sentence_pack_160        | fixed_128_within_comment |       0.929 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_cross          | whole                    |       0.789 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_cross          | native                   |       0.020 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_cross          | sentence_pack_160        |       0.093 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_cross          | fixed_128_within_comment |       0.113 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_within_comment | whole                    |       0.661 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_within_comment | native                   |       0.897 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_within_comment | sentence_pack_160        |       0.929 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_within_comment | fixed_128_cross          |       0.219 |          0.033 | FWER_SUPPORTED           |
| source_disjoint_transport | WORD12_TFIDF_SVD24                     | whole                    | whole                    |      -0.240 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | WORD12_TFIDF_SVD24                     | native                   | native                   |      -0.509 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | WORD12_TFIDF_SVD24                     | sentence_pack_160        | sentence_pack_160        |      -0.538 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | WORD12_TFIDF_SVD24                     | fixed_128_cross          | fixed_128_cross          |      -0.530 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | WORD12_TFIDF_SVD24                     | fixed_128_within_comment | fixed_128_within_comment |      -0.513 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| shared_subspace           | CHAR35_TFIDF_SVD24                     | all_views                | all_views                |      -0.017 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | whole                    | native                   |       0.153 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | whole                    | sentence_pack_160        |       0.194 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | whole                    | fixed_128_cross          |       0.246 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | whole                    | fixed_128_within_comment |       0.205 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | native                   | whole                    |       0.571 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | native                   | sentence_pack_160        |       0.920 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | native                   | fixed_128_cross          |       0.165 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | native                   | fixed_128_within_comment |       0.905 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | sentence_pack_160        | whole                    |       0.620 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | sentence_pack_160        | native                   |       0.919 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | sentence_pack_160        | fixed_128_cross          |       0.217 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | sentence_pack_160        | fixed_128_within_comment |       0.931 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_cross          | whole                    |       0.756 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_cross          | native                   |       0.145 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_cross          | sentence_pack_160        |       0.222 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_cross          | fixed_128_within_comment |       0.215 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_within_comment | whole                    |       0.637 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_within_comment | native                   |       0.899 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_within_comment | sentence_pack_160        |       0.927 |          0.033 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_within_comment | fixed_128_cross          |       0.240 |          0.033 | FWER_SUPPORTED           |
| source_disjoint_transport | CHAR35_TFIDF_SVD24                     | whole                    | whole                    |      -0.241 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | CHAR35_TFIDF_SVD24                     | native                   | native                   |      -0.555 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | CHAR35_TFIDF_SVD24                     | sentence_pack_160        | sentence_pack_160        |      -0.524 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | CHAR35_TFIDF_SVD24                     | fixed_128_cross          | fixed_128_cross          |      -0.474 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | CHAR35_TFIDF_SVD24                     | fixed_128_within_comment | fixed_128_within_comment |      -0.528 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| cross_representation      | WORD12_TFIDF_SVD24->CHAR35_TFIDF_SVD24 | whole                    | whole                    |       0.256 |          0.033 | FWER_SUPPORTED           |
| cross_representation      | CHAR35_TFIDF_SVD24->WORD12_TFIDF_SVD24 | whole                    | whole                    |       0.228 |          0.033 | FWER_SUPPORTED           |
| cross_representation      | WORD12_TFIDF_SVD24->CHAR35_TFIDF_SVD24 | native                   | native                   |      -0.030 |          0.033 | FWER_SUPPORTED           |
| cross_representation      | CHAR35_TFIDF_SVD24->WORD12_TFIDF_SVD24 | native                   | native                   |      -0.142 |          0.833 | UNRESOLVED_VIEW_SPECIFIC |
| cross_representation      | WORD12_TFIDF_SVD24->CHAR35_TFIDF_SVD24 | sentence_pack_160        | sentence_pack_160        |      -0.047 |          0.033 | FWER_SUPPORTED           |
| cross_representation      | CHAR35_TFIDF_SVD24->WORD12_TFIDF_SVD24 | sentence_pack_160        | sentence_pack_160        |      -0.147 |          0.900 | UNRESOLVED_VIEW_SPECIFIC |
| cross_representation      | WORD12_TFIDF_SVD24->CHAR35_TFIDF_SVD24 | fixed_128_cross          | fixed_128_cross          |      -0.030 |          0.033 | FWER_SUPPORTED           |
| cross_representation      | CHAR35_TFIDF_SVD24->WORD12_TFIDF_SVD24 | fixed_128_cross          | fixed_128_cross          |      -0.194 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| cross_representation      | WORD12_TFIDF_SVD24->CHAR35_TFIDF_SVD24 | fixed_128_within_comment | fixed_128_within_comment |      -0.033 |          0.033 | FWER_SUPPORTED           |
| cross_representation      | CHAR35_TFIDF_SVD24->WORD12_TFIDF_SVD24 | fixed_128_within_comment | fixed_128_within_comment |      -0.123 |          0.433 | UNRESOLVED_VIEW_SPECIFIC |

## Source-Disjoint Alignment Control

This separate AUC family does not require a linear coordinate map. It compares
each source-disjoint left half with its own right half against right-half
strangers. It distinguishes stable relative author positioning from failure of
the stricter linear transport endpoint above. Its max-T correction is confined
to the ten registered alignment endpoints and is not pooled with R2 values.

| representation     | operator                 |   alignment_auc |   alignment_max_t_fwer_p | alignment_status         |
|:-------------------|:-------------------------|----------------:|-------------------------:|:-------------------------|
| WORD12_TFIDF_SVD24 | whole                    |           0.577 |                    0.700 | UNRESOLVED_VIEW_SPECIFIC |
| WORD12_TFIDF_SVD24 | native                   |           0.551 |                    0.933 | UNRESOLVED_VIEW_SPECIFIC |
| WORD12_TFIDF_SVD24 | sentence_pack_160        |           0.570 |                    0.833 | UNRESOLVED_VIEW_SPECIFIC |
| WORD12_TFIDF_SVD24 | fixed_128_cross          |           0.585 |                    0.600 | UNRESOLVED_VIEW_SPECIFIC |
| WORD12_TFIDF_SVD24 | fixed_128_within_comment |           0.570 |                    0.833 | UNRESOLVED_VIEW_SPECIFIC |
| CHAR35_TFIDF_SVD24 | whole                    |           0.640 |                    0.133 | UNRESOLVED_VIEW_SPECIFIC |
| CHAR35_TFIDF_SVD24 | native                   |           0.588 |                    0.467 | UNRESOLVED_VIEW_SPECIFIC |
| CHAR35_TFIDF_SVD24 | sentence_pack_160        |           0.607 |                    0.267 | UNRESOLVED_VIEW_SPECIFIC |
| CHAR35_TFIDF_SVD24 | fixed_128_cross          |           0.614 |                    0.267 | UNRESOLVED_VIEW_SPECIFIC |
| CHAR35_TFIDF_SVD24 | fixed_128_within_comment |           0.614 |                    0.267 | UNRESOLVED_VIEW_SPECIFIC |

## Claim Boundary

These results can establish only registered, author-aligned transport within
the declared corpus, operator family, and representations. They do not name
factors, establish a universal best slice, identify personality, or license
clinical interpretation. `FWER_SUPPORTED` establishes only a registered
endpoint. A stronger `SHARED_WITHIN_OPERATOR_SET` label additionally requires
bootstrap loading-subspace recurrence and an independent fresh confirmation
family; it is not granted by this run alone.

## Artifacts

- `results/v7_operator_family/e4_v72_quick_20260715_r3/registered_endpoints.csv`
- `results/v7_operator_family/e4_v72_quick_20260715_r3/max_t_null.parquet` (or CSV fallback)
- `results/v7_operator_family/e4_v72_quick_20260715_r3/source_disjoint_alignment.csv`
- `results/v7_operator_family/e4_v72_quick_20260715_r3/source_disjoint_alignment_max_t_null.parquet` (or CSV fallback)
- `results/v7_operator_family/e4_v72_quick_20260715_r3/run_manifest.json`
- `results/v7_operator_family/e4_v72_quick_20260715_r3/artifact_inventory.json`
