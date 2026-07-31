# V8 Same-Author Context Geometry Transport

Status: `CONTEXT_TRANSPORT_UNDERRESOLVED`

This opened-panel experiment tests whether the same authors preserve opportunity-filtered relation geometry across two observed text contexts after each context first passes its own technical replication gate.

## Decision

```json
{
  "status": "CONTEXT_GEOMETRY_TRANSPORT_COMPLETED",
  "overall_status": "CONTEXT_TRANSPORT_UNDERRESOLVED",
  "eligible_pairs": 3,
  "transportable_pairs": 0,
  "no_overlap_pairs": 6,
  "version": "v8-cbq-context-transport-1",
  "events_per_context": 8,
  "eligibility_events_per_context": 8,
  "timestamp_utc": "2026-07-29T19:34:40.345235+00:00",
  "claim_boundary": "Opened-panel same-author cross-context technical transport audit. It reuses the D1/D2 panels opened by RGC and is exploratory rather than an independent replication. It tests whether opportunity-filtered author-relation correspondence survives between registered observed contexts. It cannot establish personality, emotion, cognition, causal situation response, construct invariance, cross-corpus coordinates, diagnosis, or clinical validity."
}
```

## Pair status

| pair_id                                                          | corpus   | context_a                  | context_b                  |   authors |   authors_D0 |   authors_D1 |   authors_D2 | feasibility   | status                                | transport_scales   |
|:-----------------------------------------------------------------|:---------|:---------------------------|:---------------------------|----------:|-------------:|-------------:|-------------:|:--------------|:--------------------------------------|:-------------------|
| pandora::AskReddit::politics                                     | pandora  | AskReddit                  | politics                   |       184 |           74 |           51 |           59 | ELIGIBLE      | WITHIN_CONTEXT_GEOMETRY_UNDERRESOLVED |                    |
| pandora::AskReddit::worldnews                                    | pandora  | AskReddit                  | worldnews                  |       164 |           70 |           44 |           50 | ELIGIBLE      | WITHIN_CONTEXT_GEOMETRY_UNDERRESOLVED |                    |
| pandora::AskReddit::AskWomen                                     | pandora  | AskReddit                  | AskWomen                   |       163 |           80 |           39 |           44 | ELIGIBLE      | WITHIN_CONTEXT_GEOMETRY_UNDERRESOLVED |                    |
| pandora::politics::worldnews                                     | pandora  | politics                   | worldnews                  |        72 |           29 |           19 |           24 | NO_OVERLAP    | NO_OVERLAP                            |                    |
| pandora::politics::AskWomen                                      | pandora  | politics                   | AskWomen                   |         8 |            4 |            1 |            3 | NO_OVERLAP    | NO_OVERLAP                            |                    |
| pandora::worldnews::AskWomen                                     | pandora  | worldnews                  | AskWomen                   |         6 |            1 |            4 |            1 | NO_OVERLAP    | NO_OVERLAP                            |                    |
| x_market::china_korea_memory_context::foundry_equipment_cycle    | x_market | china_korea_memory_context | foundry_equipment_cycle    |         5 |            2 |            1 |            2 | NO_OVERLAP    | NO_OVERLAP                            |                    |
| x_market::china_korea_memory_context::ai_accelerator_readthrough | x_market | china_korea_memory_context | ai_accelerator_readthrough |         3 |            0 |            0 |            3 | NO_OVERLAP    | NO_OVERLAP                            |                    |
| x_market::foundry_equipment_cycle::ai_accelerator_readthrough    | x_market | foundry_equipment_cycle    | ai_accelerator_readthrough |         6 |            2 |            2 |            2 | NO_OVERLAP    | NO_OVERLAP                            |                    |

## Information-budget feasibility

This table is a support audit, not an outcome search. It shows the number of same-author context pairs remaining before any held-panel metric is read.

|   events_per_context |   events_per_replicate | pair_id                       | context_a   | context_b   |   authors |   authors_D0 |   authors_D1 |   authors_D2 | held_panel_admissible   |
|---------------------:|-----------------------:|:------------------------------|:------------|:------------|----------:|-------------:|-------------:|-------------:|:------------------------|
|                    8 |                      4 | pandora::AskReddit::politics  | AskReddit   | politics    |       184 |           74 |           51 |           59 | True                    |
|                    8 |                      4 | pandora::AskReddit::worldnews | AskReddit   | worldnews   |       164 |           70 |           44 |           50 | True                    |
|                    8 |                      4 | pandora::AskReddit::AskWomen  | AskReddit   | AskWomen    |       163 |           80 |           39 |           44 | True                    |
|                    8 |                      4 | pandora::politics::worldnews  | politics    | worldnews   |        72 |           29 |           19 |           24 | False                   |
|                    8 |                      4 | pandora::politics::AskWomen   | politics    | AskWomen    |         8 |            4 |            1 |            3 | False                   |
|                    8 |                      4 | pandora::worldnews::AskWomen  | worldnews   | AskWomen    |         6 |            1 |            4 |            1 | False                   |
|                   12 |                      6 | pandora::AskReddit::politics  | AskReddit   | politics    |       104 |           44 |           23 |           37 | False                   |
|                   12 |                      6 | pandora::AskReddit::worldnews | AskReddit   | worldnews   |        80 |           31 |           23 |           26 | False                   |
|                   12 |                      6 | pandora::AskReddit::AskWomen  | AskReddit   | AskWomen    |       120 |           60 |           28 |           32 | True                    |
|                   12 |                      6 | pandora::politics::worldnews  | politics    | worldnews   |        33 |           15 |           10 |            8 | False                   |
|                   12 |                      6 | pandora::politics::AskWomen   | politics    | AskWomen    |         3 |            2 |            0 |            1 | False                   |
|                   12 |                      6 | pandora::worldnews::AskWomen  | worldnews   | AskWomen    |         0 |            0 |            0 |            0 | False                   |
|                   16 |                      8 | pandora::AskReddit::politics  | AskReddit   | politics    |        63 |           26 |           14 |           23 | False                   |
|                   16 |                      8 | pandora::AskReddit::worldnews | AskReddit   | worldnews   |        35 |           14 |            8 |           13 | False                   |
|                   16 |                      8 | pandora::AskReddit::AskWomen  | AskReddit   | AskWomen    |        84 |           47 |           17 |           20 | False                   |
|                   16 |                      8 | pandora::politics::worldnews  | politics    | worldnews   |        17 |            7 |            6 |            4 | False                   |
|                   16 |                      8 | pandora::politics::AskWomen   | politics    | AskWomen    |         1 |            0 |            0 |            1 | False                   |
|                   16 |                      8 | pandora::worldnews::AskWomen  | worldnews   | AskWomen    |         0 |            0 |            0 |            0 | False                   |
|                   24 |                     12 | pandora::AskReddit::politics  | AskReddit   | politics    |        30 |           16 |            6 |            8 | False                   |
|                   24 |                     12 | pandora::AskReddit::worldnews | AskReddit   | worldnews   |        17 |            8 |            2 |            7 | False                   |
|                   24 |                     12 | pandora::AskReddit::AskWomen  | AskReddit   | AskWomen    |        50 |           29 |           10 |           11 | False                   |
|                   24 |                     12 | pandora::politics::worldnews  | politics    | worldnews   |         5 |            3 |            1 |            1 | False                   |
|                   24 |                     12 | pandora::politics::AskWomen   | politics    | AskWomen    |         0 |            0 |            0 |            0 | False                   |
|                   24 |                     12 | pandora::worldnews::AskWomen  | worldnews   | AskWomen    |         0 |            0 |            0 |            0 | False                   |

## Held-out cells

| cell_id                                          | pair_id                       | corpus   | context_a   | context_b   | split   |   scale | component   |   authors |   observed |    null_mean |      excess |   raw_p |   bootstrap_lcb |   normalized_cross_excess |   normalized_cross_excess_lcb |   holm_p |
|:-------------------------------------------------|:------------------------------|:---------|:------------|:------------|:--------|--------:|:------------|----------:|-----------:|-------------:|------------:|--------:|----------------:|--------------------------:|------------------------------:|---------:|
| pandora::AskReddit::politics::D1::0.5::within_a  | pandora::AskReddit::politics  | pandora  | AskReddit   | politics    | D1      |     0.5 | within_a    |        51 |  0.0983456 | -0.00134868  |  0.0996942  |    0.01 |     -0.00290114 |                nan        |                    nan        |     0.18 |
| pandora::AskReddit::politics::D1::0.5::within_b  | pandora::AskReddit::politics  | pandora  | AskReddit   | politics    | D1      |     0.5 | within_b    |        51 |  0.120075  | -0.00411925  |  0.124194   |    0.01 |      0.00189297 |                nan        |                    nan        |     0.18 |
| pandora::AskReddit::politics::D1::0.5::cross     | pandora::AskReddit::politics  | pandora  | AskReddit   | politics    | D1      |     0.5 | cross       |        51 |  0.0682327 | -0.00305264  |  0.0712853  |    0.01 |     -0.0158057  |                  0.640641 |                     -0.248606 |     0.18 |
| pandora::AskReddit::politics::D2::0.5::within_a  | pandora::AskReddit::politics  | pandora  | AskReddit   | politics    | D2      |     0.5 | within_a    |        59 |  0.0854309 | -0.00530746  |  0.0907384  |    0.01 |     -0.0174233  |                nan        |                    nan        |     0.18 |
| pandora::AskReddit::politics::D2::0.5::within_b  | pandora::AskReddit::politics  | pandora  | AskReddit   | politics    | D2      |     0.5 | within_b    |        59 |  0.055163  | -0.00108952  |  0.0562525  |    0.02 |     -0.0164333  |                nan        |                    nan        |     0.24 |
| pandora::AskReddit::politics::D2::0.5::cross     | pandora::AskReddit::politics  | pandora  | AskReddit   | politics    | D2      |     0.5 | cross       |        59 |  0.0246169 |  0.002077    |  0.0225399  |    0.11 |     -0.0551986  |                  0.31549  |                    nan        |     0.44 |
| pandora::AskReddit::worldnews::D1::0.5::within_a | pandora::AskReddit::worldnews | pandora  | AskReddit   | worldnews   | D1      |     0.5 | within_a    |        44 |  0.0604836 | -0.000383056 |  0.0608667  |    0.03 |     -0.0661894  |                nan        |                    nan        |     0.3  |
| pandora::AskReddit::worldnews::D1::0.5::within_b | pandora::AskReddit::worldnews | pandora  | AskReddit   | worldnews   | D1      |     0.5 | within_b    |        44 |  0.094852  |  0.00638219  |  0.0884699  |    0.02 |     -0.0129227  |                nan        |                    nan        |     0.24 |
| pandora::AskReddit::worldnews::D1::0.5::cross    | pandora::AskReddit::worldnews | pandora  | AskReddit   | worldnews   | D1      |     0.5 | cross       |        44 |  0.0405207 | -0.00504211  |  0.0455628  |    0.03 |     -0.0317603  |                  0.620902 |                    nan        |     0.3  |
| pandora::AskReddit::worldnews::D2::0.5::within_a | pandora::AskReddit::worldnews | pandora  | AskReddit   | worldnews   | D2      |     0.5 | within_a    |        50 |  0.0782657 |  0.00258072  |  0.075685   |    0.03 |     -0.0792576  |                nan        |                    nan        |     0.3  |
| pandora::AskReddit::worldnews::D2::0.5::within_b | pandora::AskReddit::worldnews | pandora  | AskReddit   | worldnews   | D2      |     0.5 | within_b    |        50 |  0.0543621 | -0.00346686  |  0.057829   |    0.04 |     -0.0455567  |                nan        |                    nan        |     0.3  |
| pandora::AskReddit::worldnews::D2::0.5::cross    | pandora::AskReddit::worldnews | pandora  | AskReddit   | worldnews   | D2      |     0.5 | cross       |        50 |  0.0547738 | -0.000768798 |  0.0555426  |    0.01 |     -0.0233385  |                  0.839554 |                    nan        |     0.18 |
| pandora::AskReddit::AskWomen::D1::0.5::within_a  | pandora::AskReddit::AskWomen  | pandora  | AskReddit   | AskWomen    | D1      |     0.5 | within_a    |        39 | -0.0021382 | -0.00353656  |  0.00139836 |    0.5  |     -0.0771216  |                nan        |                    nan        |     1    |
| pandora::AskReddit::AskWomen::D1::0.5::within_b  | pandora::AskReddit::AskWomen  | pandora  | AskReddit   | AskWomen    | D1      |     0.5 | within_b    |        39 |  0.010456  |  0.0049173   |  0.00553866 |    0.4  |     -0.139782   |                nan        |                    nan        |     1    |
| pandora::AskReddit::AskWomen::D1::0.5::cross     | pandora::AskReddit::AskWomen  | pandora  | AskReddit   | AskWomen    | D1      |     0.5 | cross       |        39 |  0.0406654 |  0.00294127  |  0.0377242  |    0.07 |     -0.050572   |                 13.5553   |                    nan        |     0.36 |
| pandora::AskReddit::AskWomen::D2::0.5::within_a  | pandora::AskReddit::AskWomen  | pandora  | AskReddit   | AskWomen    | D2      |     0.5 | within_a    |        44 |  0.0434245 | -0.000235136 |  0.0436596  |    0.06 |     -0.0590688  |                nan        |                    nan        |     0.36 |
| pandora::AskReddit::AskWomen::D2::0.5::within_b  | pandora::AskReddit::AskWomen  | pandora  | AskReddit   | AskWomen    | D2      |     0.5 | within_b    |        44 |  0.0879087 |  5.55141e-05 |  0.0878532  |    0.01 |     -0.0216453  |                nan        |                    nan        |     0.18 |
| pandora::AskReddit::AskWomen::D2::0.5::cross     | pandora::AskReddit::AskWomen  | pandora  | AskReddit   | AskWomen    | D2      |     0.5 | cross       |        44 | -0.0333125 | -0.00311041  | -0.0302021  |    0.92 |     -0.107978   |                 -0.487661 |                    nan        |     1    |

## Interpretation boundary

Opened-panel same-author cross-context technical transport audit. It reuses the D1/D2 panels opened by RGC and is exploratory rather than an independent replication. It tests whether opportunity-filtered author-relation correspondence survives between registered observed contexts. It cannot establish personality, emotion, cognition, causal situation response, construct invariance, cross-corpus coordinates, diagnosis, or clinical validity.
