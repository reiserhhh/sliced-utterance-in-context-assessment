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
  "timestamp_utc": "2026-07-29T19:34:34.788233+00:00",
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
| pandora::AskReddit::politics::D1::0.5::within_a  | pandora::AskReddit::politics  | pandora  | AskReddit   | politics    | D1      |     0.5 | within_a    |        51 |  0.0984245 | -0.00124781  |  0.0996723  |  0.003  |      -0.0140788 |                nan        |                    nan        |   0.045  |
| pandora::AskReddit::politics::D1::0.5::within_b  | pandora::AskReddit::politics  | pandora  | AskReddit   | politics    | D1      |     0.5 | within_b    |        51 |  0.119786  | -0.000178014 |  0.119964   |  0.0005 |      -0.010329  |                nan        |                    nan        |   0.009  |
| pandora::AskReddit::politics::D1::0.5::cross     | pandora::AskReddit::politics  | pandora  | AskReddit   | politics    | D1      |     0.5 | cross       |        51 |  0.0682076 | -0.000182175 |  0.0683897  |  0.0015 |      -0.0130135 |                  0.62543  |                     -0.126457 |   0.0255 |
| pandora::AskReddit::politics::D2::0.5::within_a  | pandora::AskReddit::politics  | pandora  | AskReddit   | politics    | D2      |     0.5 | within_a    |        59 |  0.0857439 | -0.000656697 |  0.0864006  |  0.0025 |      -0.0195793 |                nan        |                    nan        |   0.04   |
| pandora::AskReddit::politics::D2::0.5::within_b  | pandora::AskReddit::politics  | pandora  | AskReddit   | politics    | D2      |     0.5 | within_b    |        59 |  0.0554598 | -0.0003928   |  0.0558526  |  0.013  |      -0.0274795 |                nan        |                    nan        |   0.13   |
| pandora::AskReddit::politics::D2::0.5::cross     | pandora::AskReddit::politics  | pandora  | AskReddit   | politics    | D2      |     0.5 | cross       |        59 |  0.0247046 |  1.66793e-05 |  0.0246879  |  0.087  |      -0.0388196 |                  0.355389 |                    nan        |   0.435  |
| pandora::AskReddit::worldnews::D1::0.5::within_a | pandora::AskReddit::worldnews | pandora  | AskReddit   | worldnews   | D1      |     0.5 | within_a    |        44 |  0.0609247 |  0.000167053 |  0.0607576  |  0.033  |      -0.0551807 |                nan        |                    nan        |   0.264  |
| pandora::AskReddit::worldnews::D1::0.5::within_b | pandora::AskReddit::worldnews | pandora  | AskReddit   | worldnews   | D1      |     0.5 | within_b    |        44 |  0.0953435 |  0.00110566  |  0.0942378  |  0.0045 |      -0.0118001 |                nan        |                    nan        |   0.063  |
| pandora::AskReddit::worldnews::D1::0.5::cross    | pandora::AskReddit::worldnews | pandora  | AskReddit   | worldnews   | D1      |     0.5 | cross       |        44 |  0.0403779 |  0.000143052 |  0.0402348  |  0.047  |      -0.0336045 |                  0.531728 |                    nan        |   0.329  |
| pandora::AskReddit::worldnews::D2::0.5::within_a | pandora::AskReddit::worldnews | pandora  | AskReddit   | worldnews   | D2      |     0.5 | within_a    |        50 |  0.0783076 |  0.000940159 |  0.0773674  |  0.006  |      -0.0678498 |                nan        |                    nan        |   0.066  |
| pandora::AskReddit::worldnews::D2::0.5::within_b | pandora::AskReddit::worldnews | pandora  | AskReddit   | worldnews   | D2      |     0.5 | within_b    |        50 |  0.0560349 | -0.000618376 |  0.0566533  |  0.028  |      -0.0507165 |                nan        |                    nan        |   0.252  |
| pandora::AskReddit::worldnews::D2::0.5::cross    | pandora::AskReddit::worldnews | pandora  | AskReddit   | worldnews   | D2      |     0.5 | cross       |        50 |  0.0548955 | -2.99209e-05 |  0.0549254  |  0.0045 |      -0.0314857 |                  0.829625 |                    nan        |   0.063  |
| pandora::AskReddit::AskWomen::D1::0.5::within_a  | pandora::AskReddit::AskWomen  | pandora  | AskReddit   | AskWomen    | D1      |     0.5 | within_a    |        39 | -0.0018328 | -0.000140461 | -0.00169234 |  0.5175 |      -0.102437  |                nan        |                    nan        |   1      |
| pandora::AskReddit::AskWomen::D1::0.5::within_b  | pandora::AskReddit::AskWomen  | pandora  | AskReddit   | AskWomen    | D1      |     0.5 | within_b    |        39 |  0.0103724 |  0.00120898  |  0.00916341 |  0.401  |      -0.120273  |                nan        |                    nan        |   1      |
| pandora::AskReddit::AskWomen::D1::0.5::cross     | pandora::AskReddit::AskWomen  | pandora  | AskReddit   | AskWomen    | D1      |     0.5 | cross       |        39 |  0.0406612 |  0.000739707 |  0.0399215  |  0.062  |      -0.058017  |                nan        |                    nan        |   0.372  |
| pandora::AskReddit::AskWomen::D2::0.5::within_a  | pandora::AskReddit::AskWomen  | pandora  | AskReddit   | AskWomen    | D2      |     0.5 | within_a    |        44 |  0.0429633 |  0.00102814  |  0.0419352  |  0.107  |      -0.0782653 |                nan        |                    nan        |   0.435  |
| pandora::AskReddit::AskWomen::D2::0.5::within_b  | pandora::AskReddit::AskWomen  | pandora  | AskReddit   | AskWomen    | D2      |     0.5 | within_b    |        44 |  0.0869914 |  0.000593313 |  0.0863981  |  0.005  |      -0.0410741 |                nan        |                    nan        |   0.063  |
| pandora::AskReddit::AskWomen::D2::0.5::cross     | pandora::AskReddit::AskWomen  | pandora  | AskReddit   | AskWomen    | D2      |     0.5 | cross       |        44 | -0.0340855 |  0.000194354 | -0.0342799  |  0.9355 |      -0.112501  |                 -0.569505 |                    nan        |   1      |

## Interpretation boundary

Opened-panel same-author cross-context technical transport audit. It reuses the D1/D2 panels opened by RGC and is exploratory rather than an independent replication. It tests whether opportunity-filtered author-relation correspondence survives between registered observed contexts. It cannot establish personality, emotion, cognition, causal situation response, construct invariance, cross-corpus coordinates, diagnosis, or clinical validity.
