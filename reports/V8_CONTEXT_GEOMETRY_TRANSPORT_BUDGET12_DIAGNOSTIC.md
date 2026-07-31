# V8 Same-Author Context Geometry Transport

Status: `CONTEXT_TRANSPORT_UNDERRESOLVED`

This opened-panel experiment tests whether the same authors preserve opportunity-filtered relation geometry across two observed text contexts after each context first passes its own technical replication gate.

## Decision

```json
{
  "status": "CONTEXT_GEOMETRY_TRANSPORT_COMPLETED",
  "overall_status": "CONTEXT_TRANSPORT_UNDERRESOLVED",
  "eligible_pairs": 1,
  "transportable_pairs": 0,
  "no_overlap_pairs": 8,
  "version": "v8-cbq-context-transport-budget12-diagnostic",
  "events_per_context": 12,
  "eligibility_events_per_context": 12,
  "timestamp_utc": "2026-07-29T19:34:20.894666+00:00",
  "claim_boundary": "Post-open information-budget diagnostic on the same opened D1/D2 chain and the only PANDORA context pair retaining at least 24 authors in both held panels at 12 events per context. It may localize underresolution but cannot promote transport, choose a production budget, establish personality, or override the registered eight-event result."
}
```

## Pair status

| pair_id                                                          | corpus   | context_a                  | context_b                  |   authors |   authors_D0 |   authors_D1 |   authors_D2 | feasibility   | status                                | transport_scales   |
|:-----------------------------------------------------------------|:---------|:---------------------------|:---------------------------|----------:|-------------:|-------------:|-------------:|:--------------|:--------------------------------------|:-------------------|
| pandora::AskReddit::politics                                     | pandora  | AskReddit                  | politics                   |       104 |           44 |           23 |           37 | NO_OVERLAP    | NO_OVERLAP                            |                    |
| pandora::AskReddit::worldnews                                    | pandora  | AskReddit                  | worldnews                  |        80 |           31 |           23 |           26 | NO_OVERLAP    | NO_OVERLAP                            |                    |
| pandora::AskReddit::AskWomen                                     | pandora  | AskReddit                  | AskWomen                   |       120 |           60 |           28 |           32 | ELIGIBLE      | WITHIN_CONTEXT_GEOMETRY_UNDERRESOLVED |                    |
| pandora::politics::worldnews                                     | pandora  | politics                   | worldnews                  |        33 |           15 |           10 |            8 | NO_OVERLAP    | NO_OVERLAP                            |                    |
| pandora::politics::AskWomen                                      | pandora  | politics                   | AskWomen                   |         3 |            2 |            0 |            1 | NO_OVERLAP    | NO_OVERLAP                            |                    |
| pandora::worldnews::AskWomen                                     | pandora  | worldnews                  | AskWomen                   |         0 |            0 |            0 |            0 | NO_OVERLAP    | NO_OVERLAP                            |                    |
| x_market::china_korea_memory_context::foundry_equipment_cycle    | x_market | china_korea_memory_context | foundry_equipment_cycle    |         4 |            2 |            1 |            1 | NO_OVERLAP    | NO_OVERLAP                            |                    |
| x_market::china_korea_memory_context::ai_accelerator_readthrough | x_market | china_korea_memory_context | ai_accelerator_readthrough |         3 |            0 |            0 |            3 | NO_OVERLAP    | NO_OVERLAP                            |                    |
| x_market::foundry_equipment_cycle::ai_accelerator_readthrough    | x_market | foundry_equipment_cycle    | ai_accelerator_readthrough |         5 |            1 |            2 |            2 | NO_OVERLAP    | NO_OVERLAP                            |                    |

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

| cell_id                                         | pair_id                      | corpus   | context_a   | context_b   | split   |   scale | component   |   authors |   observed |    null_mean |    excess |   raw_p |   bootstrap_lcb |   normalized_cross_excess |   normalized_cross_excess_lcb |   holm_p |
|:------------------------------------------------|:-----------------------------|:---------|:------------|:------------|:--------|--------:|:------------|----------:|-----------:|-------------:|----------:|--------:|----------------:|--------------------------:|------------------------------:|---------:|
| pandora::AskReddit::AskWomen::D1::0.5::within_a | pandora::AskReddit::AskWomen | pandora  | AskReddit   | AskWomen    | D1      |     0.5 | within_a    |        28 |  0.0651612 |  0.00150453  | 0.0636566 |  0.114  |     -0.135411   |                 nan       |                    nan        |   0.114  |
| pandora::AskReddit::AskWomen::D1::0.5::within_b | pandora::AskReddit::AskWomen | pandora  | AskReddit   | AskWomen    | D1      |     0.5 | within_b    |        28 |  0.162408  |  0.00208194  | 0.160326  |  0.0025 |     -0.0514294  |                 nan       |                    nan        |   0.0075 |
| pandora::AskReddit::AskWomen::D1::0.5::cross    | pandora::AskReddit::AskWomen | pandora  | AskReddit   | AskWomen    | D1      |     0.5 | cross       |        28 |  0.135949  |  0.000484249 | 0.135465  |  0.0005 |     -0.0359343  |                   1.34092 |                    nan        |   0.003  |
| pandora::AskReddit::AskWomen::D2::0.5::within_a | pandora::AskReddit::AskWomen | pandora  | AskReddit   | AskWomen    | D2      |     0.5 | within_a    |        32 |  0.122791  |  0.000255528 | 0.122536  |  0.0055 |     -0.00672851 |                 nan       |                    nan        |   0.011  |
| pandora::AskReddit::AskWomen::D2::0.5::within_b | pandora::AskReddit::AskWomen | pandora  | AskReddit   | AskWomen    | D2      |     0.5 | within_b    |        32 |  0.164445  | -8.87232e-05 | 0.164534  |  0.0005 |     -0.00910556 |                 nan       |                    nan        |   0.003  |
| pandora::AskReddit::AskWomen::D2::0.5::cross    | pandora::AskReddit::AskWomen | pandora  | AskReddit   | AskWomen    | D2      |     0.5 | cross       |        32 |  0.148936  | -4.67169e-06 | 0.14894   |  0.0005 |      0.0268605  |                   1.04895 |                      0.310196 |   0.003  |

## Interpretation boundary

Post-open information-budget diagnostic on the same opened D1/D2 chain and the only PANDORA context pair retaining at least 24 authors in both held panels at 12 events per context. It may localize underresolution but cannot promote transport, choose a production budget, establish personality, or override the registered eight-event result.
