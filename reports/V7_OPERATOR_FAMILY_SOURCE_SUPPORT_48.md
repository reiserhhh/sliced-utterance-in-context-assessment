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
| shared_subspace           | WORD12_TFIDF_SVD24                     | all_views                | all_views                |       0.130 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | whole                    | native                   |       0.375 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | whole                    | sentence_pack_160        |       0.415 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | whole                    | fixed_128_cross          |       0.425 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | whole                    | fixed_128_within_comment |       0.421 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | native                   | whole                    |       0.721 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | native                   | sentence_pack_160        |       0.958 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | native                   | fixed_128_cross          |       0.438 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | native                   | fixed_128_within_comment |       0.946 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | sentence_pack_160        | whole                    |       0.756 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | sentence_pack_160        | native                   |       0.960 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | sentence_pack_160        | fixed_128_cross          |       0.487 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | sentence_pack_160        | fixed_128_within_comment |       0.972 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_cross          | whole                    |       0.847 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_cross          | native                   |       0.433 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_cross          | sentence_pack_160        |       0.501 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_cross          | fixed_128_within_comment |       0.514 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_within_comment | whole                    |       0.764 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_within_comment | native                   |       0.950 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_within_comment | sentence_pack_160        |       0.973 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | WORD12_TFIDF_SVD24                     | fixed_128_within_comment | fixed_128_cross          |       0.498 |          0.005 | FWER_SUPPORTED           |
| source_disjoint_transport | WORD12_TFIDF_SVD24                     | whole                    | whole                    |       0.089 |          0.005 | FWER_SUPPORTED           |
| source_disjoint_transport | WORD12_TFIDF_SVD24                     | native                   | native                   |      -0.115 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | WORD12_TFIDF_SVD24                     | sentence_pack_160        | sentence_pack_160        |      -0.105 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | WORD12_TFIDF_SVD24                     | fixed_128_cross          | fixed_128_cross          |      -0.177 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | WORD12_TFIDF_SVD24                     | fixed_128_within_comment | fixed_128_within_comment |      -0.124 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| shared_subspace           | CHAR35_TFIDF_SVD24                     | all_views                | all_views                |       0.139 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | whole                    | native                   |       0.359 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | whole                    | sentence_pack_160        |       0.387 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | whole                    | fixed_128_cross          |       0.399 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | whole                    | fixed_128_within_comment |       0.384 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | native                   | whole                    |       0.669 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | native                   | sentence_pack_160        |       0.956 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | native                   | fixed_128_cross          |       0.445 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | native                   | fixed_128_within_comment |       0.942 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | sentence_pack_160        | whole                    |       0.701 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | sentence_pack_160        | native                   |       0.954 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | sentence_pack_160        | fixed_128_cross          |       0.496 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | sentence_pack_160        | fixed_128_within_comment |       0.964 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_cross          | whole                    |       0.828 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_cross          | native                   |       0.493 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_cross          | sentence_pack_160        |       0.550 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_cross          | fixed_128_within_comment |       0.561 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_within_comment | whole                    |       0.719 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_within_comment | native                   |       0.943 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_within_comment | sentence_pack_160        |       0.967 |          0.005 | FWER_SUPPORTED           |
| directed_edge             | CHAR35_TFIDF_SVD24                     | fixed_128_within_comment | fixed_128_cross          |       0.506 |          0.005 | FWER_SUPPORTED           |
| source_disjoint_transport | CHAR35_TFIDF_SVD24                     | whole                    | whole                    |       0.049 |          0.005 | FWER_SUPPORTED           |
| source_disjoint_transport | CHAR35_TFIDF_SVD24                     | native                   | native                   |      -0.070 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | CHAR35_TFIDF_SVD24                     | sentence_pack_160        | sentence_pack_160        |      -0.077 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | CHAR35_TFIDF_SVD24                     | fixed_128_cross          | fixed_128_cross          |      -0.152 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| source_disjoint_transport | CHAR35_TFIDF_SVD24                     | fixed_128_within_comment | fixed_128_within_comment |      -0.077 |          1.000 | UNRESOLVED_VIEW_SPECIFIC |
| cross_representation      | WORD12_TFIDF_SVD24->CHAR35_TFIDF_SVD24 | whole                    | whole                    |       0.518 |          0.005 | FWER_SUPPORTED           |
| cross_representation      | CHAR35_TFIDF_SVD24->WORD12_TFIDF_SVD24 | whole                    | whole                    |       0.516 |          0.005 | FWER_SUPPORTED           |
| cross_representation      | WORD12_TFIDF_SVD24->CHAR35_TFIDF_SVD24 | native                   | native                   |       0.291 |          0.005 | FWER_SUPPORTED           |
| cross_representation      | CHAR35_TFIDF_SVD24->WORD12_TFIDF_SVD24 | native                   | native                   |       0.267 |          0.005 | FWER_SUPPORTED           |
| cross_representation      | WORD12_TFIDF_SVD24->CHAR35_TFIDF_SVD24 | sentence_pack_160        | sentence_pack_160        |       0.296 |          0.005 | FWER_SUPPORTED           |
| cross_representation      | CHAR35_TFIDF_SVD24->WORD12_TFIDF_SVD24 | sentence_pack_160        | sentence_pack_160        |       0.291 |          0.005 | FWER_SUPPORTED           |
| cross_representation      | WORD12_TFIDF_SVD24->CHAR35_TFIDF_SVD24 | fixed_128_cross          | fixed_128_cross          |       0.208 |          0.005 | FWER_SUPPORTED           |
| cross_representation      | CHAR35_TFIDF_SVD24->WORD12_TFIDF_SVD24 | fixed_128_cross          | fixed_128_cross          |       0.219 |          0.005 | FWER_SUPPORTED           |
| cross_representation      | WORD12_TFIDF_SVD24->CHAR35_TFIDF_SVD24 | fixed_128_within_comment | fixed_128_within_comment |       0.299 |          0.005 | FWER_SUPPORTED           |
| cross_representation      | CHAR35_TFIDF_SVD24->WORD12_TFIDF_SVD24 | fixed_128_within_comment | fixed_128_within_comment |       0.294 |          0.005 | FWER_SUPPORTED           |

## Source-Disjoint Alignment Control

This separate AUC family does not require a linear coordinate map. It compares
each source-disjoint left half with its own right half against right-half
strangers. It distinguishes stable relative author positioning from failure of
the stricter linear transport endpoint above. Its max-T correction is confined
to the ten registered alignment endpoints and is not pooled with R2 values.

| representation     | operator                 |   alignment_auc |   alignment_max_t_fwer_p | alignment_status   |
|:-------------------|:-------------------------|----------------:|-------------------------:|:-------------------|
| WORD12_TFIDF_SVD24 | whole                    |           0.852 |                    0.005 | FWER_SUPPORTED     |
| WORD12_TFIDF_SVD24 | native                   |           0.824 |                    0.005 | FWER_SUPPORTED     |
| WORD12_TFIDF_SVD24 | sentence_pack_160        |           0.834 |                    0.005 | FWER_SUPPORTED     |
| WORD12_TFIDF_SVD24 | fixed_128_cross          |           0.791 |                    0.005 | FWER_SUPPORTED     |
| WORD12_TFIDF_SVD24 | fixed_128_within_comment |           0.837 |                    0.005 | FWER_SUPPORTED     |
| CHAR35_TFIDF_SVD24 | whole                    |           0.862 |                    0.005 | FWER_SUPPORTED     |
| CHAR35_TFIDF_SVD24 | native                   |           0.824 |                    0.005 | FWER_SUPPORTED     |
| CHAR35_TFIDF_SVD24 | sentence_pack_160        |           0.812 |                    0.005 | FWER_SUPPORTED     |
| CHAR35_TFIDF_SVD24 | fixed_128_cross          |           0.825 |                    0.005 | FWER_SUPPORTED     |
| CHAR35_TFIDF_SVD24 | fixed_128_within_comment |           0.821 |                    0.005 | FWER_SUPPORTED     |

## Claim Boundary

These results can establish only registered, author-aligned transport within
the declared corpus, operator family, and representations. They do not name
factors, establish a universal best slice, identify personality, or license
clinical interpretation. `FWER_SUPPORTED` establishes only a registered
endpoint. A stronger `SHARED_WITHIN_OPERATOR_SET` label additionally requires
bootstrap loading-subspace recurrence and an independent fresh confirmation
family; it is not granted by this run alone.

## Artifacts

- `results/v7_operator_family/e4_source_support_48_20260715_r2/registered_endpoints.csv`
- `results/v7_operator_family/e4_source_support_48_20260715_r2/max_t_null.parquet` (or CSV fallback)
- `results/v7_operator_family/e4_source_support_48_20260715_r2/source_disjoint_alignment.csv`
- `results/v7_operator_family/e4_source_support_48_20260715_r2/source_disjoint_alignment_max_t_null.parquet` (or CSV fallback)
- `results/v7_operator_family/e4_source_support_48_20260715_r2/run_manifest.json`
- `results/v7_operator_family/e4_source_support_48_20260715_r2/artifact_inventory.json`
