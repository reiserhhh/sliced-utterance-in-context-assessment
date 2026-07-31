# V8 Nested Information-Budget Experiment

Status: `INFORMATION_BUDGET_EFFECT_UNDERRESOLVED`

This opened-panel mechanism experiment keeps the author cohort and 12-event source pool fixed, then reveals literal nested subsets at 4/6/8/10/12 events per context. The primary 12-minus-8 contrast separates a 12-event-frozen operator arm from a budget-specific refit arm.

## Decision

```json
{
  "status": "NESTED_INFORMATION_BUDGET_COMPLETED",
  "overall_status": "INFORMATION_BUDGET_EFFECT_UNDERRESOLVED",
  "pair_id": "pandora::AskReddit::AskWomen",
  "authors": 120,
  "budgets": [
    4,
    6,
    8,
    10,
    12
  ],
  "primary_contrast": "12-8",
  "fixed_w_all_positive": false,
  "fixed_w_simultaneous_all_positive": false,
  "fixed_q_all_positive": false,
  "fixed_q_simultaneous_all_positive": false,
  "refit_w_simultaneous_all_positive": false,
  "fixed_w_cells_at_material_reference": 4,
  "fixed_w_cells": 6,
  "nested_subset_violations": 0,
  "schedule_sensitivity_designs": 15,
  "schedule_positive_fraction_min": 0.6,
  "schedule_positive_fraction_max": 1.0,
  "fresh_confirmation_status": "NOT_FRESH_D3",
  "version": "v8-cbq-nested-information-budget-1",
  "timestamp_utc": "2026-07-30T07:41:30.758566+00:00",
  "claim_boundary": "Opened-panel nested information-budget mechanism experiment on the previously inspected AskReddit--AskWomen D0/D1/D2 author cohort. The fixed-12 operator arm may distinguish added input information from budget-specific estimator refitting, but the result is development sensitivity rather than fresh confirmation. The deterministic reveal ladder is one content-blind design and does not establish optimal sampling. The experiment cannot establish personality, emotion, cognition, construct validity, causal situation response, population norms, language invariance, diagnosis, or clinical use."
}
```

## Nested design audit

|   budget | context   |   authors |   events |   events_per_replicate |   subset_violations_from_previous | source_indices            |
|---------:|:----------|----------:|---------:|-----------------------:|----------------------------------:|:--------------------------|
|        4 | AskReddit |       120 |      480 |                      2 |                                 0 | 0,1,10,11                 |
|        4 | AskWomen  |       120 |      480 |                      2 |                                 0 | 0,1,10,11                 |
|        6 | AskReddit |       120 |      720 |                      3 |                                 0 | 0,1,4,5,10,11             |
|        6 | AskWomen  |       120 |      720 |                      3 |                                 0 | 0,1,4,5,10,11             |
|        8 | AskReddit |       120 |      960 |                      4 |                                 0 | 0,1,4,5,6,7,10,11         |
|        8 | AskWomen  |       120 |      960 |                      4 |                                 0 | 0,1,4,5,6,7,10,11         |
|       10 | AskReddit |       120 |     1200 |                      5 |                                 0 | 0,1,2,3,4,5,6,7,10,11     |
|       10 | AskWomen  |       120 |     1200 |                      5 |                                 0 | 0,1,2,3,4,5,6,7,10,11     |
|       12 | AskReddit |       120 |     1440 |                      6 |                                 0 | 0,1,2,3,4,5,6,7,8,9,10,11 |
|       12 | AskWomen  |       120 |     1440 |                      6 |                                 0 | 0,1,2,3,4,5,6,7,8,9,10,11 |

## Primary paired deltas

Positive W means relation excess increased. Positive Q means technical
disagreement decreased. W and Q reuse the same relation matrices, so they are
complementary diagnostics rather than independent evidence.

| cell_id                                  |      point |   pointwise_lcb |   pointwise_ucb |   simultaneous_lcb |   simultaneous_ucb |   simultaneous_critical | arm               | metric                             | all_simultaneous_positive   |   material_reference |
|:-----------------------------------------|-----------:|----------------:|----------------:|-------------------:|-------------------:|------------------------:|:------------------|:-----------------------------------|:----------------------------|---------------------:|
| fixed_12_operator::D1::within_a::W::12-8 | -0.0848307 |      -0.280401  |       0.110204  |         -0.358946  |           0.189285 |                 2.75677 | fixed_12_operator | delta_relation_excess_w            | False                       |                 0.03 |
| fixed_12_operator::D1::within_b::W::12-8 |  0.0759319 |      -0.108069  |       0.24772   |         -0.167915  |           0.319779 |                 2.75677 | fixed_12_operator | delta_relation_excess_w            | False                       |                 0.03 |
| fixed_12_operator::D1::cross::W::12-8    |  0.0286995 |      -0.101172  |       0.174807  |         -0.163619  |           0.221018 |                 2.75677 | fixed_12_operator | delta_relation_excess_w            | False                       |                 0.03 |
| fixed_12_operator::D2::within_a::W::12-8 |  0.0904121 |      -0.0701323 |       0.248042  |         -0.132829  |           0.313653 |                 2.75677 | fixed_12_operator | delta_relation_excess_w            | False                       |                 0.03 |
| fixed_12_operator::D2::within_b::W::12-8 |  0.0598919 |      -0.07927   |       0.197037  |         -0.13506   |           0.254844 |                 2.75677 | fixed_12_operator | delta_relation_excess_w            | False                       |                 0.03 |
| fixed_12_operator::D2::cross::W::12-8    |  0.0360447 |      -0.0594223 |       0.134767  |         -0.0959211 |           0.168011 |                 2.75677 | fixed_12_operator | delta_relation_excess_w            | False                       |                 0.03 |
| fixed_12_operator::D1::within_a::Q::8-12 | -0.0851331 |      -0.277553  |       0.108976  |         -0.336043  |           0.165777 |                 2.56561 | fixed_12_operator | reduction_technical_disagreement_q | False                       |               nan    |
| fixed_12_operator::D1::within_b::Q::8-12 |  0.07607   |      -0.106964  |       0.245993  |         -0.14961   |           0.30175  |                 2.56561 | fixed_12_operator | reduction_technical_disagreement_q | False                       |               nan    |
| fixed_12_operator::D2::within_a::Q::8-12 |  0.0923496 |      -0.0677565 |       0.249554  |         -0.114007  |           0.298706 |                 2.56561 | fixed_12_operator | reduction_technical_disagreement_q | False                       |               nan    |
| fixed_12_operator::D2::within_b::Q::8-12 |  0.060595  |      -0.0782391 |       0.197765  |         -0.118995  |           0.240185 |                 2.56561 | fixed_12_operator | reduction_technical_disagreement_q | False                       |               nan    |
| budget_refit::D1::within_a::W::12-8      | -0.122897  |      -0.302823  |       0.0652469 |         -0.388143  |           0.142349 |                 2.78955 | budget_refit      | delta_relation_excess_w            | False                       |                 0.03 |
| budget_refit::D1::within_b::W::12-8      |  0.0484082 |      -0.151953  |       0.214351  |         -0.205446  |           0.302263 |                 2.78955 | budget_refit      | delta_relation_excess_w            | False                       |                 0.03 |
| budget_refit::D1::cross::W::12-8         |  0.022175  |      -0.120142  |       0.180556  |         -0.190803  |           0.235153 |                 2.78955 | budget_refit      | delta_relation_excess_w            | False                       |                 0.03 |
| budget_refit::D2::within_a::W::12-8      |  0.0715933 |      -0.093545  |       0.233124  |         -0.160435  |           0.303621 |                 2.78955 | budget_refit      | delta_relation_excess_w            | False                       |                 0.03 |
| budget_refit::D2::within_b::W::12-8      |  0.046063  |      -0.0935224 |       0.181463  |         -0.145516  |           0.237642 |                 2.78955 | budget_refit      | delta_relation_excess_w            | False                       |                 0.03 |
| budget_refit::D2::cross::W::12-8         |  0.0400114 |      -0.0535164 |       0.129043  |         -0.0857494 |           0.165772 |                 2.78955 | budget_refit      | delta_relation_excess_w            | False                       |                 0.03 |
| budget_refit::D1::within_a::Q::8-12      | -0.12145   |      -0.292926  |       0.0644596 |         -0.369905  |           0.127004 |                 2.66058 | budget_refit      | reduction_technical_disagreement_q | False                       |               nan    |
| budget_refit::D1::within_b::Q::8-12      |  0.0491512 |      -0.150408  |       0.213038  |         -0.191113  |           0.289415 |                 2.66058 | budget_refit      | reduction_technical_disagreement_q | False                       |               nan    |
| budget_refit::D2::within_a::Q::8-12      |  0.0691878 |      -0.0952498 |       0.230588  |         -0.150683  |           0.289059 |                 2.66058 | budget_refit      | reduction_technical_disagreement_q | False                       |               nan    |
| budget_refit::D2::within_b::Q::8-12      |  0.0465475 |      -0.0914982 |       0.181448  |         -0.134452  |           0.227547 |                 2.66058 | budget_refit      | reduction_technical_disagreement_q | False                       |               nan    |

## Eight-event content-sampling sensitivity

All 15 ways to reveal four of the six event pairs were scored with the same frozen twelve-event operator. These rows are dependent design sensitivities, not 15 replications.

| split   | component   |   schedules |   positive_fraction |   median_delta |   minimum_delta |   maximum_delta |
|:--------|:------------|------------:|--------------------:|---------------:|----------------:|----------------:|
| D1      | cross       |          15 |            1        |     0.0620266  |       0.0275203 |       0.111354  |
| D1      | within_a    |          15 |            0.6      |     0.00211652 |      -0.140517  |       0.138906  |
| D1      | within_b    |          15 |            0.733333 |     0.0314114  |      -0.0329158 |       0.144705  |
| D2      | cross       |          15 |            1        |     0.0637335  |       0.0060603 |       0.114668  |
| D2      | within_a    |          15 |            0.933333 |     0.0258906  |      -0.0713907 |       0.0958182 |
| D2      | within_b    |          15 |            0.866667 |     0.0290286  |      -0.0461786 |       0.0786484 |

Detailed cells are saved as `schedule_sensitivity.csv`.

## Held-panel budget curve

| arm               | split   |   budget | component   | metric                   |       point |     observed |     null_mean |   pointwise_lcb |   pointwise_ucb |
|:------------------|:--------|---------:|:------------|:-------------------------|------------:|-------------:|--------------:|----------------:|----------------:|
| fixed_12_operator | D1      |        4 | within_a    | relation_excess_w        |  0.0132476  |  0.0130611   |  -0.000186557 |    -0.146079    |        0.178157 |
| fixed_12_operator | D1      |        4 | within_b    | relation_excess_w        |  0.0639129  |  0.0652756   |   0.00136267  |    -0.162072    |        0.265847 |
| fixed_12_operator | D1      |        4 | cross       | relation_excess_w        | -0.0245194  | -0.02535     |  -0.000830666 |    -0.162645    |        0.105768 |
| fixed_12_operator | D1      |        4 | within_a    | technical_disagreement_q |  0.986964   |  0.986964    | nan           |     0.823282    |        1.14192  |
| fixed_12_operator | D1      |        4 | within_b    | technical_disagreement_q |  0.93501    |  0.93501     | nan           |     0.733545    |        1.15826  |
| fixed_12_operator | D1      |        6 | within_a    | relation_excess_w        |  0.0551881  |  0.0546948   |  -0.000493296 |    -0.0945289   |        0.213068 |
| fixed_12_operator | D1      |        6 | within_b    | relation_excess_w        |  0.0983078  |  0.0981769   |  -0.000130874 |    -0.0905292   |        0.279851 |
| fixed_12_operator | D1      |        6 | cross       | relation_excess_w        | -0.00861967 | -0.00933055  |  -0.000710881 |    -0.180688    |        0.1616   |
| fixed_12_operator | D1      |        6 | within_a    | technical_disagreement_q |  0.945343   |  0.945343    | nan           |     0.78854     |        1.09302  |
| fixed_12_operator | D1      |        6 | within_b    | technical_disagreement_q |  0.902053   |  0.902053    | nan           |     0.720657    |        1.08958  |
| fixed_12_operator | D1      |        8 | within_a    | relation_excess_w        |  0.150491   |  0.150303    |  -0.000187746 |    -0.0125726   |        0.314818 |
| fixed_12_operator | D1      |        8 | within_b    | relation_excess_w        |  0.0860015  |  0.0858842   |  -0.000117326 |    -0.0907861   |        0.252556 |
| fixed_12_operator | D1      |        8 | cross       | relation_excess_w        |  0.107395   |  0.107562    |   0.000167467 |    -0.0353506   |        0.265061 |
| fixed_12_operator | D1      |        8 | within_a    | technical_disagreement_q |  0.84981    |  0.84981     | nan           |     0.686681    |        1.01143  |
| fixed_12_operator | D1      |        8 | within_b    | technical_disagreement_q |  0.914187   |  0.914187    | nan           |     0.747711    |        1.08951  |
| fixed_12_operator | D1      |       10 | within_a    | relation_excess_w        |  0.108549   |  0.108008    |  -0.000540443 |    -0.0918094   |        0.311791 |
| fixed_12_operator | D1      |       10 | within_b    | relation_excess_w        |  0.149449   |  0.149065    |  -0.000383735 |    -0.0459841   |        0.336796 |
| fixed_12_operator | D1      |       10 | cross       | relation_excess_w        |  0.0854829  |  0.0845553   |  -0.0009276   |    -0.0781425   |        0.241448 |
| fixed_12_operator | D1      |       10 | within_a    | technical_disagreement_q |  0.892038   |  0.892038    | nan           |     0.691117    |        1.08896  |
| fixed_12_operator | D1      |       10 | within_b    | technical_disagreement_q |  0.851554   |  0.851554    | nan           |     0.666302    |        1.04566  |
| fixed_12_operator | D1      |       12 | within_a    | relation_excess_w        |  0.0656605  |  0.06507     |  -0.000590419 |    -0.11946     |        0.244105 |
| fixed_12_operator | D1      |       12 | within_b    | relation_excess_w        |  0.161933   |  0.162594    |   0.000660553 |    -0.036608    |        0.3609   |
| fixed_12_operator | D1      |       12 | cross       | relation_excess_w        |  0.136094   |  0.13615     |   5.55563e-05 |    -0.0193454   |        0.271494 |
| fixed_12_operator | D1      |       12 | within_a    | technical_disagreement_q |  0.934943   |  0.934943    | nan           |     0.759673    |        1.11667  |
| fixed_12_operator | D1      |       12 | within_b    | technical_disagreement_q |  0.838117   |  0.838117    | nan           |     0.639771    |        1.03396  |
| fixed_12_operator | D2      |        4 | within_a    | relation_excess_w        | -0.00210834 | -0.000897755 |   0.00121059  |    -0.158709    |        0.176531 |
| fixed_12_operator | D2      |        4 | within_b    | relation_excess_w        |  0.0781704  |  0.0781341   |  -3.62838e-05 |    -0.0914515   |        0.242781 |
| fixed_12_operator | D2      |        4 | cross       | relation_excess_w        |  0.0288375  |  0.0292757   |   0.000438125 |    -0.0829647   |        0.154214 |
| fixed_12_operator | D2      |        4 | within_a    | technical_disagreement_q |  1.0009     |  1.0009      | nan           |     0.823255    |        1.15634  |
| fixed_12_operator | D2      |        4 | within_b    | technical_disagreement_q |  0.92188    |  0.92188     | nan           |     0.759229    |        1.08753  |
| fixed_12_operator | D2      |        6 | within_a    | relation_excess_w        |  0.00739397 |  0.00855025  |   0.00115627  |    -0.141642    |        0.169113 |
| fixed_12_operator | D2      |        6 | within_b    | relation_excess_w        |  0.0953066  |  0.0940876   |  -0.00121903  |    -0.0754515   |        0.260523 |
| fixed_12_operator | D2      |        6 | cross       | relation_excess_w        |  0.0305235  |  0.0313625   |   0.000839002 |    -0.0659555   |        0.131768 |
| fixed_12_operator | D2      |        6 | within_a    | technical_disagreement_q |  0.991453   |  0.991453    | nan           |     0.830416    |        1.1402   |
| fixed_12_operator | D2      |        6 | within_b    | technical_disagreement_q |  0.906532   |  0.906532    | nan           |     0.752481    |        1.0742   |
| fixed_12_operator | D2      |        8 | within_a    | relation_excess_w        |  0.0303011  |  0.030037    |  -0.000264045 |    -0.110565    |        0.177912 |
| fixed_12_operator | D2      |        8 | within_b    | relation_excess_w        |  0.106706   |  0.103813    |  -0.00289291  |    -0.0475443   |        0.261487 |
| fixed_12_operator | D2      |        8 | cross       | relation_excess_w        |  0.113073   |  0.113577    |   0.000503937 |    -0.000996219 |        0.22712  |
| fixed_12_operator | D2      |        8 | within_a    | technical_disagreement_q |  0.969964   |  0.969964    | nan           |     0.82452     |        1.10945  |
| fixed_12_operator | D2      |        8 | within_b    | technical_disagreement_q |  0.896854   |  0.896854    | nan           |     0.742483    |        1.04888  |
| fixed_12_operator | D2      |       10 | within_a    | relation_excess_w        |  0.0869705  |  0.0874514   |   0.00048084  |    -0.0625736   |        0.233642 |
| fixed_12_operator | D2      |       10 | within_b    | relation_excess_w        |  0.15373    |  0.151114    |  -0.00261597  |    -0.00407247  |        0.318448 |
| fixed_12_operator | D2      |       10 | cross       | relation_excess_w        |  0.127874   |  0.127894    |   1.97755e-05 |     0.00415563  |        0.250797 |
| fixed_12_operator | D2      |       10 | within_a    | technical_disagreement_q |  0.912559   |  0.912559    | nan           |     0.766119    |        1.06127  |
| fixed_12_operator | D2      |       10 | within_b    | technical_disagreement_q |  0.849594   |  0.849594    | nan           |     0.685375    |        1.00535  |
| fixed_12_operator | D2      |       12 | within_a    | relation_excess_w        |  0.120713   |  0.122739    |   0.00202624  |    -0.0137605   |        0.256119 |
| fixed_12_operator | D2      |       12 | within_b    | relation_excess_w        |  0.166598   |  0.164385    |  -0.00221316  |    -0.00747256  |        0.340781 |
| fixed_12_operator | D2      |       12 | cross       | relation_excess_w        |  0.149118   |  0.148835    |  -0.000282482 |     0.0300522   |        0.263003 |
| fixed_12_operator | D2      |       12 | within_a    | technical_disagreement_q |  0.877614   |  0.877614    | nan           |     0.744062    |        1.01103  |
| fixed_12_operator | D2      |       12 | within_b    | technical_disagreement_q |  0.836259   |  0.836259    | nan           |     0.660899    |        1.0078   |
| budget_refit      | D1      |        4 | within_a    | relation_excess_w        |  0.0551087  |  0.0545061   |  -0.000602522 |    -0.11092     |        0.205583 |
| budget_refit      | D1      |        4 | within_b    | relation_excess_w        |  0.104925   |  0.105249    |   0.000324127 |    -0.100904    |        0.300447 |
| budget_refit      | D1      |        4 | cross       | relation_excess_w        |  0.00469518 |  0.00481786  |   0.00012268  |    -0.136978    |        0.155677 |
| budget_refit      | D1      |        4 | within_a    | technical_disagreement_q |  0.945504   |  0.945504    | nan           |     0.794853    |        1.10997  |
| budget_refit      | D1      |        4 | within_b    | technical_disagreement_q |  0.896341   |  0.896341    | nan           |     0.70481     |        1.09641  |
| budget_refit      | D1      |        6 | within_a    | relation_excess_w        |  0.120195   |  0.11963     |  -0.000564373 |    -0.0354522   |        0.271767 |
| budget_refit      | D1      |        6 | within_b    | relation_excess_w        |  0.124699   |  0.125304    |   0.000604219 |    -0.0633924   |        0.308342 |
| budget_refit      | D1      |        6 | cross       | relation_excess_w        |  0.0513176  |  0.0498666   |  -0.00145103  |    -0.106102    |        0.212006 |
| budget_refit      | D1      |        6 | within_a    | technical_disagreement_q |  0.880381   |  0.880381    | nan           |     0.727981    |        1.03466  |
| budget_refit      | D1      |        6 | within_b    | technical_disagreement_q |  0.875484   |  0.875484    | nan           |     0.693025    |        1.06195  |
| budget_refit      | D1      |        8 | within_a    | relation_excess_w        |  0.187909   |  0.186754    |  -0.00115523  |     0.0099054   |        0.357376 |
| budget_refit      | D1      |        8 | within_b    | relation_excess_w        |  0.114391   |  0.112895    |  -0.00149626  |    -0.0494761   |        0.264297 |
| budget_refit      | D1      |        8 | cross       | relation_excess_w        |  0.112527   |  0.113116    |   0.000589417 |    -0.0416438   |        0.278679 |
| budget_refit      | D1      |        8 | within_a    | technical_disagreement_q |  0.813493   |  0.813493    | nan           |     0.646482    |        0.989721 |
| budget_refit      | D1      |        8 | within_b    | technical_disagreement_q |  0.887268   |  0.887268    | nan           |     0.737005    |        1.05014  |
| budget_refit      | D1      |       10 | within_a    | relation_excess_w        |  0.102757   |  0.103891    |   0.00113363  |    -0.106165    |        0.301923 |
| budget_refit      | D1      |       10 | within_b    | relation_excess_w        |  0.14155    |  0.140603    |  -0.000946838 |    -0.0430199   |        0.318285 |
| budget_refit      | D1      |       10 | cross       | relation_excess_w        |  0.0893739  |  0.0905083   |   0.00113443  |    -0.0634697   |        0.2351   |
| budget_refit      | D1      |       10 | within_a    | technical_disagreement_q |  0.896118   |  0.896118    | nan           |     0.701347    |        1.10419  |
| budget_refit      | D1      |       10 | within_b    | technical_disagreement_q |  0.860009   |  0.860009    | nan           |     0.683589    |        1.04254  |
| budget_refit      | D1      |       12 | within_a    | relation_excess_w        |  0.0650118  |  0.06507     |   5.82515e-05 |    -0.126741    |        0.253194 |
| budget_refit      | D1      |       12 | within_b    | relation_excess_w        |  0.162799   |  0.162594    |  -0.000205196 |    -0.0568178   |        0.355343 |
| budget_refit      | D1      |       12 | cross       | relation_excess_w        |  0.134702   |  0.13615     |   0.00144818  |    -0.0272965   |        0.273081 |
| budget_refit      | D1      |       12 | within_a    | technical_disagreement_q |  0.934943   |  0.934943    | nan           |     0.748419    |        1.1217   |
| budget_refit      | D1      |       12 | within_b    | technical_disagreement_q |  0.838117   |  0.838117    | nan           |     0.645206    |        1.05486  |
| budget_refit      | D2      |        4 | within_a    | relation_excess_w        |  0.0108378  |  0.011728    |   0.000890203 |    -0.153478    |        0.191492 |
| budget_refit      | D2      |        4 | within_b    | relation_excess_w        |  0.0608818  |  0.0602474   |  -0.000634411 |    -0.117674    |        0.252473 |
| budget_refit      | D2      |        4 | cross       | relation_excess_w        |  0.0309142  |  0.0307138   |  -0.000200416 |    -0.0799415   |        0.145459 |
| budget_refit      | D2      |        4 | within_a    | technical_disagreement_q |  0.98828    |  0.98828     | nan           |     0.808775    |        1.14955  |
| budget_refit      | D2      |        4 | within_b    | technical_disagreement_q |  0.94002    |  0.94002     | nan           |     0.750805    |        1.1157   |
| budget_refit      | D2      |        6 | within_a    | relation_excess_w        |  0.0404952  |  0.0423821   |   0.00188689  |    -0.114523    |        0.195922 |
| budget_refit      | D2      |        6 | within_b    | relation_excess_w        |  0.0982826  |  0.0976907   |  -0.000591866 |    -0.0770923   |        0.264875 |
| budget_refit      | D2      |        6 | cross       | relation_excess_w        |  0.0275441  |  0.0271832   |  -0.000360974 |    -0.0842579   |        0.134718 |
| budget_refit      | D2      |        6 | within_a    | technical_disagreement_q |  0.957642   |  0.957642    | nan           |     0.802989    |        1.11224  |
| budget_refit      | D2      |        6 | within_b    | technical_disagreement_q |  0.904325   |  0.904325    | nan           |     0.744429    |        1.07481  |
| budget_refit      | D2      |        8 | within_a    | relation_excess_w        |  0.0513182  |  0.0531982   |   0.00187999  |    -0.0917749   |        0.20441  |
| budget_refit      | D2      |        8 | within_b    | relation_excess_w        |  0.118284   |  0.118024    |  -0.000259842 |    -0.0478898   |        0.290589 |
| budget_refit      | D2      |        8 | cross       | relation_excess_w        |  0.110511   |  0.109462    |  -0.00104902  |    -0.00594628  |        0.219344 |
| budget_refit      | D2      |        8 | within_a    | technical_disagreement_q |  0.946802   |  0.946802    | nan           |     0.794925    |        1.08936  |
| budget_refit      | D2      |        8 | within_b    | technical_disagreement_q |  0.882806   |  0.882806    | nan           |     0.709114    |        1.04633  |
| budget_refit      | D2      |       10 | within_a    | relation_excess_w        |  0.0917461  |  0.0919962   |   0.000250034 |    -0.0551818   |        0.240065 |
| budget_refit      | D2      |       10 | within_b    | relation_excess_w        |  0.145978   |  0.145761    |  -0.000217229 |    -0.0304269   |        0.312949 |
| budget_refit      | D2      |       10 | cross       | relation_excess_w        |  0.13055    |  0.129524    |  -0.00102662  |     0.0036209   |        0.254784 |
| budget_refit      | D2      |       10 | within_a    | technical_disagreement_q |  0.908025   |  0.908025    | nan           |     0.760293    |        1.05381  |
| budget_refit      | D2      |       10 | within_b    | technical_disagreement_q |  0.854843   |  0.854843    | nan           |     0.687596    |        1.02937  |
| budget_refit      | D2      |       12 | within_a    | relation_excess_w        |  0.122912   |  0.122739    |  -0.000172125 |    -0.00601079  |        0.252361 |
| budget_refit      | D2      |       12 | within_b    | relation_excess_w        |  0.164347   |  0.164385    |   3.84447e-05 |    -0.00839566  |        0.346198 |
| budget_refit      | D2      |       12 | cross       | relation_excess_w        |  0.150523   |  0.148835    |  -0.00168733  |     0.0293284   |        0.277061 |
| budget_refit      | D2      |       12 | within_a    | technical_disagreement_q |  0.877614   |  0.877614    | nan           |     0.749769    |        1.00542  |
| budget_refit      | D2      |       12 | within_b    | technical_disagreement_q |  0.836259   |  0.836259    | nan           |     0.654752    |        1.00703  |

## Operator diagnostics

| arm               |   fit_budget |   application_budget | context   |   bandwidth |   active_nuisance_columns |   background_coverage |   background_fixed_point_rate |
|:------------------|-------------:|---------------------:|:----------|------------:|--------------------------:|----------------------:|------------------------------:|
| fixed_12_operator |           12 |                   12 | AskReddit |     12.7764 |                        44 |                     1 |                     0.0500056 |
| fixed_12_operator |           12 |                   12 | AskWomen  |     12.8659 |                        44 |                     1 |                     0.0500153 |
| budget_refit      |            4 |                    4 | AskReddit |     12.962  |                        43 |                     1 |                     0.0505302 |
| budget_refit      |            4 |                    4 | AskWomen  |     12.6153 |                        40 |                     1 |                     0.050071  |
| budget_refit      |            6 |                    6 | AskReddit |     12.9423 |                        44 |                     1 |                     0.049833  |
| budget_refit      |            6 |                    6 | AskWomen  |     12.5498 |                        43 |                     1 |                     0.0491511 |
| budget_refit      |            8 |                    8 | AskReddit |     12.8252 |                        44 |                     1 |                     0.049691  |
| budget_refit      |            8 |                    8 | AskWomen  |     12.7493 |                        44 |                     1 |                     0.0498727 |
| budget_refit      |           10 |                   10 | AskReddit |     12.8202 |                        44 |                     1 |                     0.0500835 |
| budget_refit      |           10 |                   10 | AskWomen  |     12.9348 |                        44 |                     1 |                     0.0501236 |
| budget_refit      |           12 |                   12 | AskReddit |     12.7764 |                        44 |                     1 |                     0.0500056 |
| budget_refit      |           12 |                   12 | AskWomen  |     12.8659 |                        44 |                     1 |                     0.0500153 |

## Interpretation boundary

Opened-panel nested information-budget mechanism experiment on the previously inspected AskReddit--AskWomen D0/D1/D2 author cohort. The fixed-12 operator arm may distinguish added input information from budget-specific estimator refitting, but the result is development sensitivity rather than fresh confirmation. The deterministic reveal ladder is one content-blind design and does not establish optimal sampling. The experiment cannot establish personality, emotion, cognition, construct validity, causal situation response, population norms, language invariance, diagnosis, or clinical use.
