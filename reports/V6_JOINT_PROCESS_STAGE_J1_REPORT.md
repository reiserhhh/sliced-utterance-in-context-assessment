# SUICA V6 Joint-Process J1: Label-Free Geometry

## Question

Can two text-disjoint technical views of each author reproduce the same
**natural joint selection-expression-transition geometry**? Observed subreddit
selection remains in the object. This is neither a topic-removal experiment nor
a personality prediction test.

## Frozen data boundary

- source comments seen in memory: `1540040`
- excluded by explicit personality-report guard: `28488`
- selected technical-view events: `234528`
- selected authors: `4886`
- events per author per disjoint view: `24`
- external labels read: `False`
- raw text persisted: `False`

## Same-author geometry

| representation      | cohort       | component        |   n_authors |   same_author_auc |
|:--------------------|:-------------|:-----------------|------------:|------------------:|
| word_1to2_tfidf_svd | discovery    | selection        |        2475 |            0.9814 |
| word_1to2_tfidf_svd | discovery    | expression       |        2475 |            0.872  |
| word_1to2_tfidf_svd | discovery    | event_joint      |        2475 |            0.9872 |
| word_1to2_tfidf_svd | discovery    | transition_joint |        2475 |            0.9848 |
| word_1to2_tfidf_svd | discovery    | joint            |        2475 |            0.9873 |
| word_1to2_tfidf_svd | calibration  | selection        |        1216 |            0.9835 |
| word_1to2_tfidf_svd | calibration  | expression       |        1216 |            0.8658 |
| word_1to2_tfidf_svd | calibration  | event_joint      |        1216 |            0.9882 |
| word_1to2_tfidf_svd | calibration  | transition_joint |        1216 |            0.985  |
| word_1to2_tfidf_svd | calibration  | joint            |        1216 |            0.9882 |
| word_1to2_tfidf_svd | confirmation | selection        |        1195 |            0.9845 |
| word_1to2_tfidf_svd | confirmation | expression       |        1195 |            0.8803 |
| word_1to2_tfidf_svd | confirmation | event_joint      |        1195 |            0.9894 |
| word_1to2_tfidf_svd | confirmation | transition_joint |        1195 |            0.9868 |
| word_1to2_tfidf_svd | confirmation | joint            |        1195 |            0.9894 |
| char_3to5_tfidf_svd | discovery    | selection        |        2475 |            0.9814 |
| char_3to5_tfidf_svd | discovery    | expression       |        2475 |            0.8967 |
| char_3to5_tfidf_svd | discovery    | event_joint      |        2475 |            0.9888 |
| char_3to5_tfidf_svd | discovery    | transition_joint |        2475 |            0.9861 |
| char_3to5_tfidf_svd | discovery    | joint            |        2475 |            0.9887 |
| char_3to5_tfidf_svd | calibration  | selection        |        1216 |            0.9835 |
| char_3to5_tfidf_svd | calibration  | expression       |        1216 |            0.8986 |
| char_3to5_tfidf_svd | calibration  | event_joint      |        1216 |            0.9901 |
| char_3to5_tfidf_svd | calibration  | transition_joint |        1216 |            0.9864 |
| char_3to5_tfidf_svd | calibration  | joint            |        1216 |            0.9897 |
| char_3to5_tfidf_svd | confirmation | selection        |        1195 |            0.9845 |
| char_3to5_tfidf_svd | confirmation | expression       |        1195 |            0.9056 |
| char_3to5_tfidf_svd | confirmation | event_joint      |        1195 |            0.991  |
| char_3to5_tfidf_svd | confirmation | transition_joint |        1195 |            0.988  |
| char_3to5_tfidf_svd | confirmation | joint            |        1195 |            0.9907 |

## Primary confirmation randomization test

| representation      |   n_confirmation_authors |   observed_auc |   null_auc_median |   null_auc_q95 |   permutation_p |
|:--------------------|-------------------------:|---------------:|------------------:|---------------:|----------------:|
| word_1to2_tfidf_svd |                     1195 |         0.9894 |            0.5008 |         0.5139 |           0.005 |
| char_3to5_tfidf_svd |                     1195 |         0.9907 |            0.4989 |         0.5122 |           0.005 |

## Cross-representation confirmation geometry

- word/character joint-geometry correlation: `0.9063`

## Frozen decision

`J1_GEOMETRY_REPLICATES`.

J1 promotion requires both independent text representations to reach
same-author AUC >= `0.55`, each shuffled-alignment
randomization p <= `0.01`, and
cross-representation confirmation geometry r >= `0.2`.

## Interpretation boundary

Passing J1 supports a representation-bounded, author-conditioned natural
text-process geometry under this corpus and this technical split. It does not
identify a personality factor, causal condition effect, clinical state,
cross-language invariant, or a real repeated human occasion. In particular,
`transition_joint` contains source and successor **marginals**; its high AUC
does not yet show that chronological order adds stable author information.
The next valid step is a separately frozen, centred ordered-transition operator
against a within-block order-shuffle null; it is not an external-scale analysis.
