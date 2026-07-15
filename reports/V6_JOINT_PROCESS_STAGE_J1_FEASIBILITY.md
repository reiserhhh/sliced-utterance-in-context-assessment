# SUICA V6 Joint-Process J1: J0 Feasibility

## Frozen question

Does the local raw PANDORA source supply enough naturally selected events and
ordered transitions to estimate the **joint selection-expression-transition**
object? This is not a matched-topic test. `subreddit` remains an observed
selection component rather than a nuisance to remove.

## Provenance and data boundary

- source SHA-256: `532ffc13a5b1333265e0dc32f290894a28d6211fa98e0746cbe41bf3bf8d914a`
- source comments: `1540040`
- excluded by explicit personality-report leakage guard: `28488`
- retained metadata events: `1466085`
- threshold selected by synthetic calibration: `{'min_events': 24, 'min_transitions': 8}`
- technical replication: `2` disjoint
  views made of consecutive `3`-event blocks
- total support required for those disjoint views: `48`
  events and `32` within-block transitions
- external labels read: `False`
- embeddings/factors/text endpoints fit: `False`
- raw text persisted: `False`

## Cohort support

| cohort       |   n_authors |   n_eligible_authors |   eligible_fraction |   median_events_eligible |   median_transitions_eligible |   median_selection_count_eligible |   total_transitions::within_day |   authors_with_transitions::within_day |   total_transitions::one_to_seven_days |   authors_with_transitions::one_to_seven_days |   total_transitions::one_to_thirty_days |   authors_with_transitions::one_to_thirty_days |   total_transitions::one_to_six_months |   authors_with_transitions::one_to_six_months |   total_transitions::over_six_months |   authors_with_transitions::over_six_months |
|:-------------|------------:|---------------------:|--------------------:|-------------------------:|------------------------------:|----------------------------------:|--------------------------------:|---------------------------------------:|---------------------------------------:|----------------------------------------------:|----------------------------------------:|-----------------------------------------------:|---------------------------------------:|----------------------------------------------:|-------------------------------------:|--------------------------------------------:|
| calibration  |        1242 |                 1216 |               0.979 |                      350 |                           349 |                                45 |                          197514 |                                   1216 |                                 119079 |                                          1216 |                                   38059 |                                           1195 |                                   6639 |                                          1103 |                                  335 |                                         270 |
| confirmation |        1218 |                 1195 |               0.981 |                      355 |                           354 |                                44 |                          194425 |                                   1195 |                                 117485 |                                          1194 |                                   38585 |                                           1175 |                                   6767 |                                          1094 |                                  366 |                                         298 |
| discovery    |        2540 |                 2475 |               0.974 |                      353 |                           352 |                                44 |                          403174 |                                   2475 |                                 242218 |                                          2475 |                                   78384 |                                           2425 |                                  13382 |                                          2224 |                                  700 |                                         559 |

## Decision

`PROCEED_J1` — confirmation cohort has sufficient author-level natural-event support.

The raw PANDORA schema contains no independently observed global expression
opportunity variable. Therefore this gate licenses only a joint natural-process
object. It does **not** license separate conditional-expression, causal,
personality, clinical, or cross-language claims. Text length is recorded only
for later sensitivity analysis and is not residualized from the primary object.

## Next action

If `PROCEED_J1`, construct frozen joint-process objects in an author-disjoint
discovery/calibration/confirmation design. If `REFUSE_J1_SUPPORT`, do not lower
the calibration threshold or substitute artificial fixed-topic windows.
