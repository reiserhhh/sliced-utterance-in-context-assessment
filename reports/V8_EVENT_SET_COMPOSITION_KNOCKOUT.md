# V8 Event-Set Composition Knockout

Status: `NATURAL_EVENT_SET_COMPOSITION_EXCESS_NOT_DETECTED`

Pseudo event sets preserve corpus, split, context, event position, all event marginals, and local text-length rank, while independently breaking within-author event co-occurrence at every order slot.

## Result

| split   | metric   |   rank |   observed |   pseudo_mean |   observed_minus_pseudo |   raw_p |   max_t_p |
|:--------|:---------|-------:|-----------:|--------------:|------------------------:|--------:|----------:|
| D1      | hs       |     10 |   0.176556 |      0.168837 |             0.00771855  |   0.325 |     0.635 |
| D1      | fidelity |     10 |   0.36165  |      0.337816 |             0.0238341   |   0.185 |     0.405 |
| D2      | hs       |     10 |   0.242198 |      0.241185 |             0.00101248  |   0.48  |     0.75  |
| D2      | fidelity |     10 |   0.413814 |      0.413977 |            -0.000163414 |   0.495 |     0.755 |

## Reallocation quality

| corpus   | split   |   same_author |   mean_absolute_length_difference |
|:---------|:--------|--------------:|----------------------------------:|
| left     | D0      |             0 |                           13.6599 |
| left     | D1      |             0 |                           19.1358 |
| left     | D2      |             0 |                           20.3148 |
| right    | D0      |             0 |                            0      |
| right    | D1      |             0 |                            0      |
| right    | D2      |             0 |                            0      |

## Claim boundary

Exploratory event-set composition knockout on opened PANDORA and Essays authors. Pseudo sets preserve corpus, D0/D1/D2 split, context, event position, every event-vector marginal, and local text-length rank while breaking natural within-author co-occurrence. A pass can attribute EPSG to natural event-set composition under this operator; it cannot identify personality, cognition, causality, universality, diagnosis, or clinical validity.
