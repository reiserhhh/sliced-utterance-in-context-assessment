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
  "version": "v8-cbq-context-transport-budget8-on-budget12-support",
  "events_per_context": 8,
  "eligibility_events_per_context": 12,
  "timestamp_utc": "2026-07-29T19:34:19.232379+00:00",
  "claim_boundary": "Post-open matched-support diagnostic. It holds the twelve-event-eligible author cohort fixed while replaying eight events per context. Event composition and full estimator refitting still differ, so it does not isolate a pure information-budget effect. It cannot promote transport, establish personality, or override the registered result."
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

| cell_id                                         | pair_id                      | corpus   | context_a   | context_b   | split   |   scale | component   |   authors |    observed |    null_mean |      excess |   raw_p |   bootstrap_lcb |   normalized_cross_excess |   normalized_cross_excess_lcb |   holm_p |
|:------------------------------------------------|:-----------------------------|:---------|:------------|:------------|:--------|--------:|:------------|----------:|------------:|-------------:|------------:|--------:|----------------:|--------------------------:|------------------------------:|---------:|
| pandora::AskReddit::AskWomen::D1::0.5::within_a | pandora::AskReddit::AskWomen | pandora  | AskReddit   | AskWomen    | D1      |     0.5 | within_a    |        28 |  0.00243048 | -0.000495839 |  0.00292632 |  0.4665 |      -0.151891  |                 nan       |                           nan |   0.933  |
| pandora::AskReddit::AskWomen::D1::0.5::within_b | pandora::AskReddit::AskWomen | pandora  | AskReddit   | AskWomen    | D1      |     0.5 | within_b    |        28 |  0.0750115  | -0.0014492   |  0.0764607  |  0.075  |      -0.134272  |                 nan       |                           nan |   0.375  |
| pandora::AskReddit::AskWomen::D1::0.5::cross    | pandora::AskReddit::AskWomen | pandora  | AskReddit   | AskWomen    | D1      |     0.5 | cross       |        28 |  0.0537014  | -0.000659485 |  0.0543609  |  0.078  |      -0.0729301 |                   3.63418 |                           nan |   0.375  |
| pandora::AskReddit::AskWomen::D2::0.5::within_a | pandora::AskReddit::AskWomen | pandora  | AskReddit   | AskWomen    | D2      |     0.5 | within_a    |        32 | -0.0312339  | -0.000896607 | -0.0303373  |  0.7345 |      -0.20671   |                 nan       |                           nan |   0.933  |
| pandora::AskReddit::AskWomen::D2::0.5::within_b | pandora::AskReddit::AskWomen | pandora  | AskReddit   | AskWomen    | D2      |     0.5 | within_b    |        32 |  0.0503422  |  0.00186526  |  0.048477   |  0.1525 |      -0.129639  |                 nan       |                           nan |   0.4575 |
| pandora::AskReddit::AskWomen::D2::0.5::cross    | pandora::AskReddit::AskWomen | pandora  | AskReddit   | AskWomen    | D2      |     0.5 | cross       |        32 |  0.0495473  |  9.81411e-05 |  0.0494492  |  0.0575 |      -0.069011  |                 nan       |                           nan |   0.345  |

## Interpretation boundary

Post-open matched-support diagnostic. It holds the twelve-event-eligible author cohort fixed while replaying eight events per context. Event composition and full estimator refitting still differ, so it does not isolate a pure information-budget effect. It cannot promote transport, establish personality, or override the registered result.
