# V8 Event-Set Composition Knockout

Status: `NATURAL_EVENT_SET_COMPOSITION_EXCESS_NOT_DETECTED`

Pseudo event sets preserve corpus, split, context, event position, all event marginals, and local text-length rank, while independently breaking within-author event co-occurrence at every order slot.

## Result

| split   | metric   |   rank |   observed |   pseudo_mean |   observed_minus_pseudo |   raw_p |   max_t_p |
|:--------|:---------|-------:|-----------:|--------------:|------------------------:|--------:|----------:|
| D1      | hs       |      2 | 0.0483974  |     0.0403506 |              0.00804677 |    0.29 |      0.6  |
| D1      | fidelity |      2 | 0.202432   |     0.157273  |              0.0451592  |    0.2  |      0.42 |
| D2      | hs       |      2 | 0.00741098 |     0.0456701 |             -0.0382591  |    0.98 |      1    |
| D2      | fidelity |      2 | 0.0830113  |     0.167477  |             -0.0844658  |    0.92 |      1    |

## Reallocation quality

| corpus   | split   |   same_author |   mean_absolute_length_difference |
|:---------|:--------|--------------:|----------------------------------:|
| left     | D0      |             0 |                           42.5775 |
| left     | D1      |             0 |                           41.7529 |
| left     | D2      |             0 |                           46.3093 |
| right    | D0      |             0 |                            0      |
| right    | D1      |             0 |                            0      |
| right    | D2      |             0 |                            0      |

## Claim boundary

Exploratory event-set composition knockout on opened PANDORA and Essays authors. Pseudo sets preserve corpus, D0/D1/D2 split, context, event position, every event-vector marginal, and local text-length rank while breaking natural within-author co-occurrence. A pass can attribute EPSG to natural event-set composition under this operator; it cannot identify personality, cognition, causality, universality, diagnosis, or clinical validity.
