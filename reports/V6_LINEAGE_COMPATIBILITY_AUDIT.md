# SUICA V6 Lineage Compatibility Audit

## Scope

This is a label-free compatibility audit, not a personality prediction or a vote
between versions. It keeps conditional fixed-rind expression, natural selection
plus expression, and condition-residualized expression as separate objects.

- source comments after explicit personality-report guard: `1,466,085`
- external labels read: `False`
- raw text persisted: `False`

## A. Fixed-rind compatibility endpoint

**Relation:** `INCONCLUSIVE_NOT_A_REVERSAL`.

- confirmation authors before frozen span/view filters: `1,087`
- complete paired authors: `32`
- fixed/mixed median evaluated-token ratio: `1.000`
- fixed/mixed median time-span ratio: `0.902`
- vector same-author AUC, fixed/mixed: `0.6805` / `0.5766`

| construct             |   n_authors |   r_fixed |   r_mixed |   delta |   ci_lo |   ci_hi |   bootstrap_finite_fraction |
|:----------------------|------------:|----------:|----------:|--------:|--------:|--------:|----------------------------:|
| first_person_usage_v2 |          32 |    0.8231 |    0.6096 |  0.2135 | -0.0205 |  0.4782 |                           1 |
| directive_action_v2   |          32 |    0.6145 |    0.1851 |  0.4295 |  0.0303 |  0.7986 |                           1 |
| novelty_play_v2       |          32 |    0.4943 |    0.071  |  0.4234 | -0.178  |  0.7644 |                           1 |
| tension_core_v2       |          32 |    0.1386 |    0.1266 |  0.012  | -0.4749 |  0.3845 |                           1 |

Interpretation: the table tests the historical **conditional-expression precision**
claim with event-disjoint, time-spread technical views. It does not measure a
personality trait. `tension_core_v2` is reported but does not count toward the
historical three-construct decision because its old positive effect was already
retracted as a temporal-clustering artifact.

## B. Natural residualization sensitivity

**Relation:** `INVESTIGATE_SCOPE_OR_IMPLEMENTATION_DIFFERENCE`.

- J1-compatible selected events/authors: `176,160` / `3,670`
- discovery-supported subreddit conditions: `945`
- rows using frozen discovery grand-mean fallback: `42,848`
- residual minus raw same-author AUC: `+0.0499`

| representation               |   n_confirmation_authors |   observed_auc |   null_auc_median |   null_auc_q95 |   permutation_p |
|:-----------------------------|-------------------------:|---------------:|------------------:|---------------:|----------------:|
| raw_anchor_coordinates       |                     1195 |         0.6002 |            0.5003 |         0.5082 |           0.005 |
| discovery_condition_residual |                     1195 |         0.65   |            0.5003 |         0.5121 |           0.005 |

Subtracting a discovery-only population condition mean creates a different
object. It cannot be called a cleaner personality signal merely because it is
residualized.

## C. Existing J1 reference (not rerun)

- cached J1 decision: `J1_GEOMETRY_REPLICATES`
- claim boundary: `reproducible_natural_joint_process_geometry_only`
- ordered dependence tested: `False`
- cross-representation geometry correlation: `0.9062662006451998`

| representation      |   n_confirmation_authors |   observed_auc |   null_auc_median |   null_auc_q95 |   permutation_p |
|:--------------------|-------------------------:|---------------:|------------------:|---------------:|----------------:|
| word_1to2_tfidf_svd |                     1195 |         0.9894 |            0.5008 |         0.5139 |           0.005 |
| char_3to5_tfidf_svd |                     1195 |         0.9907 |            0.4989 |         0.5122 |           0.005 |

J1 and fixed-rind reliability are not competing estimates: J1 intentionally
retains author-selected subreddit choice, while A fixes one selected rind before
examining expression. J3's calibrated refusal remains a refusal of one finite
order-specific operator, not a reversal of either result.

## D. Assumption delta ledger

| claim_id            | prior_estimand                                                    | v6_counterpart                                                                | outcome                                        | relation                                     |
|:--------------------|:------------------------------------------------------------------|:------------------------------------------------------------------------------|:-----------------------------------------------|:---------------------------------------------|
| PRED-1              | fixed selected rind vs mixed rind scalar split-half precision     | event-disjoint, span-constrained fixed vs mixed scalar technical views        | INCONCLUSIVE_NOT_A_REVERSAL                    | NEEDS_SCOPE_REVIEW                           |
| C2/CENTERING        | raw selection-plus-expression versus condition-centred expression | discovery-only subreddit mean subtraction on J1-compatible anchor coordinates | INVESTIGATE_SCOPE_OR_IMPLEMENTATION_DIFFERENCE | COMPATIBLE_DIFFERENT_ESTIMAND                |
| V6-J1               | not present in V3/V4                                              | natural selection-expression-transition geometry                              | J1_GEOMETRY_REPLICATES                         | NEW_SEPARATE_OBJECT                          |
| V6-J3               | old dynamic/motion hypotheses under their own support worlds      | finite centred within-block ordered-transition operator                       | REFUSE_NO_CALIBRATED_ORDER_SUPPORT             | COMPATIBLE_DIFFERENT_ESTIMAND_NOT_A_REVERSAL |
| V6_FACTOR_DISCOVERY | predefined lexical construct reliability                          | new shared low-dimensional factor-axis confirmation                           | NO_NEW_FACTOR_FAMILY_CONFIRMED                 | NOT_A_TEST_OF_PRIOR_CONSTRUCT_VALIDITY       |

## Decision

- Old V3/V4 conclusions remain historical claims with their own estimands;
  this audit only changes their status if the same-direction compatibility test
  reverses under the frozen event-disjoint implementation.
- V6 factor nonconfirmation does not erase prior predefined construct findings: a
  low-dimensional shared-axis test is not a test of scalar construct reliability.
- No result here licenses a personality, clinical, causal, cross-language, or
  cross-domain claim.
