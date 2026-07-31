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
  "fixed_w_cells_at_material_reference": 5,
  "fixed_w_cells": 6,
  "nested_subset_violations": 0,
  "fresh_confirmation_status": "NOT_FRESH_D3",
  "version": "v8-cbq-nested-information-budget-1",
  "timestamp_utc": "2026-07-30T07:36:37.454601+00:00",
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

Positive W means relation excess increased. Positive Q means technical disagreement decreased.

| cell_id                                  |      point |   pointwise_lcb |   pointwise_ucb |   simultaneous_lcb |   simultaneous_ucb |   simultaneous_critical | arm               | metric                             | all_simultaneous_positive   |   material_reference |
|:-----------------------------------------|-----------:|----------------:|----------------:|-------------------:|-------------------:|------------------------:|:------------------|:-----------------------------------|:----------------------------|---------------------:|
| fixed_12_operator::D1::within_a::W::12-8 | -0.088453  |      -0.258657  |       0.0678659 |         -0.328041  |           0.151135 |                 2.68819 | fixed_12_operator | delta_relation_excess_w            | False                       |                 0.03 |
| fixed_12_operator::D1::within_b::W::12-8 |  0.072968  |      -0.0784259 |       0.215713  |         -0.14847   |           0.294406 |                 2.68819 | fixed_12_operator | delta_relation_excess_w            | False                       |                 0.03 |
| fixed_12_operator::D1::cross::W::12-8    |  0.0332056 |      -0.065082  |       0.17464   |         -0.136224  |           0.202635 |                 2.68819 | fixed_12_operator | delta_relation_excess_w            | False                       |                 0.03 |
| fixed_12_operator::D2::within_a::W::12-8 |  0.0942866 |      -0.0793262 |       0.241135  |         -0.134194  |           0.322767 |                 2.68819 | fixed_12_operator | delta_relation_excess_w            | False                       |                 0.03 |
| fixed_12_operator::D2::within_b::W::12-8 |  0.0601219 |      -0.0749106 |       0.208125  |         -0.141007  |           0.26125  |                 2.68819 | fixed_12_operator | delta_relation_excess_w            | False                       |                 0.03 |
| fixed_12_operator::D2::cross::W::12-8    |  0.0396456 |      -0.0395979 |       0.139302  |         -0.0776551 |           0.156946 |                 2.68819 | fixed_12_operator | delta_relation_excess_w            | False                       |                 0.03 |
| fixed_12_operator::D1::within_a::Q::8-12 | -0.0849853 |      -0.244388  |       0.0703374 |         -0.280798  |           0.110828 |                 2.23241 | fixed_12_operator | reduction_technical_disagreement_q | False                       |               nan    |
| fixed_12_operator::D1::within_b::Q::8-12 |  0.076039  |      -0.0755807 |       0.217936  |         -0.106733  |           0.258811 |                 2.23241 | fixed_12_operator | reduction_technical_disagreement_q | False                       |               nan    |
| fixed_12_operator::D2::within_a::Q::8-12 |  0.0925035 |      -0.0799285 |       0.23646   |         -0.0955733 |           0.28058  |                 2.23241 | fixed_12_operator | reduction_technical_disagreement_q | False                       |               nan    |
| fixed_12_operator::D2::within_b::Q::8-12 |  0.060662  |      -0.0721989 |       0.208302  |         -0.105373  |           0.226697 |                 2.23241 | fixed_12_operator | reduction_technical_disagreement_q | False                       |               nan    |
| budget_refit::D1::within_a::W::12-8      | -0.131641  |      -0.335077  |       0.0459717 |         -0.409259  |           0.145976 |                 2.70315 | budget_refit      | delta_relation_excess_w            | False                       |                 0.03 |
| budget_refit::D1::within_b::W::12-8      |  0.0441904 |      -0.117022  |       0.185866  |         -0.172731  |           0.261112 |                 2.70315 | budget_refit      | delta_relation_excess_w            | False                       |                 0.03 |
| budget_refit::D1::cross::W::12-8         |  0.0220279 |      -0.14598   |       0.180099  |         -0.196775  |           0.240831 |                 2.70315 | budget_refit      | delta_relation_excess_w            | False                       |                 0.03 |
| budget_refit::D2::within_a::W::12-8      |  0.0623001 |      -0.0611477 |       0.189821  |         -0.111462  |           0.236062 |                 2.70315 | budget_refit      | delta_relation_excess_w            | False                       |                 0.03 |
| budget_refit::D2::within_b::W::12-8      |  0.0461244 |      -0.109449  |       0.173835  |         -0.146768  |           0.239017 |                 2.70315 | budget_refit      | delta_relation_excess_w            | False                       |                 0.03 |
| budget_refit::D2::cross::W::12-8         |  0.0396196 |      -0.0405474 |       0.116852  |         -0.0732055 |           0.152445 |                 2.70315 | budget_refit      | delta_relation_excess_w            | False                       |                 0.03 |
| budget_refit::D1::within_a::Q::8-12      | -0.121581  |      -0.321249  |       0.054348  |         -0.369787  |           0.126625 |                 2.46452 | budget_refit      | reduction_technical_disagreement_q | False                       |               nan    |
| budget_refit::D1::within_b::Q::8-12      |  0.0488269 |      -0.111169  |       0.189455  |         -0.147856  |           0.24551  |                 2.46452 | budget_refit      | reduction_technical_disagreement_q | False                       |               nan    |
| budget_refit::D2::within_a::Q::8-12      |  0.0698313 |      -0.0518209 |       0.195936  |         -0.0875629 |           0.227225 |                 2.46452 | budget_refit      | reduction_technical_disagreement_q | False                       |               nan    |
| budget_refit::D2::within_b::Q::8-12      |  0.0468966 |      -0.0952172 |       0.174639  |         -0.127146  |           0.220939 |                 2.46452 | budget_refit      | reduction_technical_disagreement_q | False                       |               nan    |

## Held-panel budget curve

| arm               | split   |   budget | component   | metric                   |       point |     observed |     null_mean |   pointwise_lcb |   pointwise_ucb |
|:------------------|:--------|---------:|:------------|:-------------------------|------------:|-------------:|--------------:|----------------:|----------------:|
| fixed_12_operator | D1      |        4 | within_a    | relation_excess_w        |  0.0164933  |  0.0130684   |  -0.00342486  |     -0.125717   |        0.165344 |
| fixed_12_operator | D1      |        4 | within_b    | relation_excess_w        |  0.0630618  |  0.0652644   |   0.00220252  |     -0.119608   |        0.231499 |
| fixed_12_operator | D1      |        4 | cross       | relation_excess_w        | -0.0233572  | -0.0253488   |  -0.00199162  |     -0.149985   |        0.132744 |
| fixed_12_operator | D1      |        4 | within_a    | technical_disagreement_q |  0.986956   |  0.986956    | nan           |      0.84112    |        1.1268   |
| fixed_12_operator | D1      |        4 | within_b    | technical_disagreement_q |  0.935021   |  0.935021    | nan           |      0.768257   |        1.1163   |
| fixed_12_operator | D1      |        6 | within_a    | relation_excess_w        |  0.0552018  |  0.0547322   |  -0.000469577 |     -0.0917873  |        0.202507 |
| fixed_12_operator | D1      |        6 | within_b    | relation_excess_w        |  0.0934318  |  0.0981963   |   0.00476459  |     -0.11007    |        0.292681 |
| fixed_12_operator | D1      |        6 | cross       | relation_excess_w        | -0.0141056  | -0.00929413  |   0.00481151  |     -0.183066   |        0.177743 |
| fixed_12_operator | D1      |        6 | within_a    | technical_disagreement_q |  0.945306   |  0.945306    | nan           |      0.799503   |        1.09139  |
| fixed_12_operator | D1      |        6 | within_b    | technical_disagreement_q |  0.902034   |  0.902034    | nan           |      0.702471   |        1.10442  |
| fixed_12_operator | D1      |        8 | within_a    | relation_excess_w        |  0.158967   |  0.150281    |  -0.0086857   |      0.00236978 |        0.281948 |
| fixed_12_operator | D1      |        8 | within_b    | relation_excess_w        |  0.0905104  |  0.0856709   |  -0.00483953  |     -0.0929379  |        0.300433 |
| fixed_12_operator | D1      |        8 | cross       | relation_excess_w        |  0.103452   |  0.107593    |   0.00414026  |     -0.0176023  |        0.237002 |
| fixed_12_operator | D1      |        8 | within_a    | technical_disagreement_q |  0.849832   |  0.849832    | nan           |      0.72732    |        1.00538  |
| fixed_12_operator | D1      |        8 | within_b    | technical_disagreement_q |  0.914399   |  0.914399    | nan           |      0.705449   |        1.0972   |
| fixed_12_operator | D1      |       10 | within_a    | relation_excess_w        |  0.111924   |  0.108148    |  -0.00377652  |     -0.0475666  |        0.301062 |
| fixed_12_operator | D1      |       10 | within_b    | relation_excess_w        |  0.154045   |  0.149025    |  -0.00502022  |     -0.0309196  |        0.331471 |
| fixed_12_operator | D1      |       10 | cross       | relation_excess_w        |  0.0829656  |  0.0846112   |   0.00164564  |     -0.0548562  |        0.229969 |
| fixed_12_operator | D1      |       10 | within_a    | technical_disagreement_q |  0.891898   |  0.891898    | nan           |      0.703818   |        1.04975  |
| fixed_12_operator | D1      |       10 | within_b    | technical_disagreement_q |  0.851591   |  0.851591    | nan           |      0.674063   |        1.03529  |
| fixed_12_operator | D1      |       12 | within_a    | relation_excess_w        |  0.0705136  |  0.0651964   |  -0.00531721  |     -0.105482   |        0.23915  |
| fixed_12_operator | D1      |       12 | within_b    | relation_excess_w        |  0.163478   |  0.16234     |  -0.00113839  |     -0.00433047 |        0.348653 |
| fixed_12_operator | D1      |       12 | cross       | relation_excess_w        |  0.136658   |  0.136348    |  -0.000310059 |      0.00120596 |        0.253643 |
| fixed_12_operator | D1      |       12 | within_a    | technical_disagreement_q |  0.934817   |  0.934817    | nan           |      0.768232   |        1.10276  |
| fixed_12_operator | D1      |       12 | within_b    | technical_disagreement_q |  0.83836    |  0.83836     | nan           |      0.654871   |        1.00505  |
| fixed_12_operator | D2      |        4 | within_a    | relation_excess_w        |  0.00202466 | -0.000916507 |  -0.00294116  |     -0.14914    |        0.173859 |
| fixed_12_operator | D2      |        4 | within_b    | relation_excess_w        |  0.082077   |  0.0781337   |  -0.00394324  |     -0.108149   |        0.239591 |
| fixed_12_operator | D2      |        4 | cross       | relation_excess_w        |  0.025448   |  0.0292704   |   0.00382241  |     -0.090769   |        0.12416  |
| fixed_12_operator | D2      |        4 | within_a    | technical_disagreement_q |  1.00092    |  1.00092     | nan           |      0.830019   |        1.15088  |
| fixed_12_operator | D2      |        4 | within_b    | technical_disagreement_q |  0.921881   |  0.921881    | nan           |      0.764591   |        1.10993  |
| fixed_12_operator | D2      |        6 | within_a    | relation_excess_w        |  0.0124805  |  0.00855497  |  -0.00392553  |     -0.123969   |        0.17411  |
| fixed_12_operator | D2      |        6 | within_b    | relation_excess_w        |  0.100621   |  0.0940995   |  -0.00652181  |     -0.0602904  |        0.272776 |
| fixed_12_operator | D2      |        6 | cross       | relation_excess_w        |  0.0254172  |  0.0313361   |   0.0059189   |     -0.0602454  |        0.115115 |
| fixed_12_operator | D2      |        6 | within_a    | technical_disagreement_q |  0.991448   |  0.991448    | nan           |      0.830159   |        1.12727  |
| fixed_12_operator | D2      |        6 | within_b    | technical_disagreement_q |  0.906521   |  0.906521    | nan           |      0.736303   |        1.06554  |
| fixed_12_operator | D2      |        8 | within_a    | relation_excess_w        |  0.0324471  |  0.0300203   |  -0.00242681  |     -0.134788   |        0.181008 |
| fixed_12_operator | D2      |        8 | within_b    | relation_excess_w        |  0.112694   |  0.103634    |  -0.00906016  |     -0.0382199  |        0.26619  |
| fixed_12_operator | D2      |        8 | cross       | relation_excess_w        |  0.105513   |  0.113577    |   0.00806422  |     -0.00646291 |        0.21763  |
| fixed_12_operator | D2      |        8 | within_a    | technical_disagreement_q |  0.96998    |  0.96998     | nan           |      0.82441    |        1.13585  |
| fixed_12_operator | D2      |        8 | within_b    | technical_disagreement_q |  0.897036   |  0.897036    | nan           |      0.742318   |        1.04597  |
| fixed_12_operator | D2      |       10 | within_a    | relation_excess_w        |  0.087836   |  0.0877412   |  -9.47973e-05 |     -0.0573656  |        0.22335  |
| fixed_12_operator | D2      |       10 | within_b    | relation_excess_w        |  0.160768   |  0.150978    |  -0.0097903   |      0.0458024  |        0.318889 |
| fixed_12_operator | D2      |       10 | cross       | relation_excess_w        |  0.123372   |  0.127892    |   0.00451977  |     -0.0132959  |        0.23654  |
| fixed_12_operator | D2      |       10 | within_a    | technical_disagreement_q |  0.912269   |  0.912269    | nan           |      0.780104   |        1.05639  |
| fixed_12_operator | D2      |       10 | within_b    | technical_disagreement_q |  0.849736   |  0.849736    | nan           |      0.690191   |        0.965817 |
| fixed_12_operator | D2      |       12 | within_a    | relation_excess_w        |  0.126734   |  0.122875    |  -0.00385906  |      0.0176869  |        0.274454 |
| fixed_12_operator | D2      |       12 | within_b    | relation_excess_w        |  0.172816   |  0.164271    |  -0.00854469  |      0.0227039  |        0.335958 |
| fixed_12_operator | D2      |       12 | cross       | relation_excess_w        |  0.145158   |  0.148744    |   0.00358609  |      0.038322   |        0.249932 |
| fixed_12_operator | D2      |       12 | within_a    | technical_disagreement_q |  0.877477   |  0.877477    | nan           |      0.731366   |        0.985676 |
| fixed_12_operator | D2      |       12 | within_b    | technical_disagreement_q |  0.836373   |  0.836373    | nan           |      0.672405   |        0.984792 |
| budget_refit      | D1      |        4 | within_a    | relation_excess_w        |  0.0527935  |  0.054285    |   0.00149149  |     -0.0972795  |        0.206918 |
| budget_refit      | D1      |        4 | within_b    | relation_excess_w        |  0.107892   |  0.105344    |  -0.00254833  |     -0.0945881  |        0.279977 |
| budget_refit      | D1      |        4 | cross       | relation_excess_w        |  0.00237428 |  0.00456797  |   0.00219369  |     -0.114639   |        0.180149 |
| budget_refit      | D1      |        4 | within_a    | technical_disagreement_q |  0.945725   |  0.945725    | nan           |      0.792614   |        1.09436  |
| budget_refit      | D1      |        4 | within_b    | technical_disagreement_q |  0.896253   |  0.896253    | nan           |      0.730987   |        1.0921   |
| budget_refit      | D1      |        6 | within_a    | relation_excess_w        |  0.110453   |  0.119708    |   0.00925478  |     -0.0275921  |        0.265546 |
| budget_refit      | D1      |        6 | within_b    | relation_excess_w        |  0.129254   |  0.125415    |  -0.00383887  |     -0.0664718  |        0.309963 |
| budget_refit      | D1      |        6 | cross       | relation_excess_w        |  0.0523927  |  0.0498986   |  -0.0024941   |     -0.0792639  |        0.198747 |
| budget_refit      | D1      |        6 | within_a    | technical_disagreement_q |  0.880303   |  0.880303    | nan           |      0.724349   |        1.01669  |
| budget_refit      | D1      |        6 | within_b    | technical_disagreement_q |  0.875375   |  0.875375    | nan           |      0.695535   |        1.06562  |
| budget_refit      | D1      |        8 | within_a    | relation_excess_w        |  0.191325   |  0.187008    |  -0.00431762  |     -0.00951559 |        0.340808 |
| budget_refit      | D1      |        8 | within_b    | relation_excess_w        |  0.121133   |  0.112978    |  -0.00815499  |     -0.0363155  |        0.24389  |
| budget_refit      | D1      |        8 | cross       | relation_excess_w        |  0.117774   |  0.113327    |  -0.00444747  |     -0.0254637  |        0.311776 |
| budget_refit      | D1      |        8 | within_a    | technical_disagreement_q |  0.813237   |  0.813237    | nan           |      0.667075   |        1.01175  |
| budget_refit      | D1      |        8 | within_b    | technical_disagreement_q |  0.887187   |  0.887187    | nan           |      0.763767   |        1.04384  |
| budget_refit      | D1      |       10 | within_a    | relation_excess_w        |  0.100934   |  0.103431    |   0.0024972   |     -0.0811622  |        0.28656  |
| budget_refit      | D1      |       10 | within_b    | relation_excess_w        |  0.141492   |  0.14073     |  -0.000762328 |     -0.034067   |        0.314078 |
| budget_refit      | D1      |       10 | cross       | relation_excess_w        |  0.0975714  |  0.0904837   |  -0.0070877   |     -0.0425299  |        0.245499 |
| budget_refit      | D1      |       10 | within_a    | technical_disagreement_q |  0.896578   |  0.896578    | nan           |      0.717605   |        1.07633  |
| budget_refit      | D1      |       10 | within_b    | technical_disagreement_q |  0.859876   |  0.859876    | nan           |      0.692722   |        1.03312  |
| budget_refit      | D1      |       12 | within_a    | relation_excess_w        |  0.0596839  |  0.0651964   |   0.00551242  |     -0.128265   |        0.233629 |
| budget_refit      | D1      |       12 | within_b    | relation_excess_w        |  0.165323   |  0.16234     |  -0.00298299  |     -0.00261367 |        0.337326 |
| budget_refit      | D1      |       12 | cross       | relation_excess_w        |  0.139802   |  0.136348    |  -0.0034545   |     -0.00949353 |        0.290521 |
| budget_refit      | D1      |       12 | within_a    | technical_disagreement_q |  0.934817   |  0.934817    | nan           |      0.760887   |        1.11996  |
| budget_refit      | D1      |       12 | within_b    | technical_disagreement_q |  0.83836    |  0.83836     | nan           |      0.665256   |        1.00492  |
| budget_refit      | D2      |        4 | within_a    | relation_excess_w        |  0.0108158  |  0.011463    |   0.000647147 |     -0.142758   |        0.185793 |
| budget_refit      | D2      |        4 | within_b    | relation_excess_w        |  0.062837   |  0.0602137   |  -0.00262321  |     -0.0965318  |        0.268554 |
| budget_refit      | D2      |        4 | cross       | relation_excess_w        |  0.0264539  |  0.0306904   |   0.00423651  |     -0.0543912  |        0.124416 |
| budget_refit      | D2      |        4 | within_a    | technical_disagreement_q |  0.988545   |  0.988545    | nan           |      0.815262   |        1.14191  |
| budget_refit      | D2      |        4 | within_b    | technical_disagreement_q |  0.940053   |  0.940053    | nan           |      0.735628   |        1.0964   |
| budget_refit      | D2      |        6 | within_a    | relation_excess_w        |  0.038362   |  0.0416854   |   0.00332336  |     -0.106704   |        0.200884 |
| budget_refit      | D2      |        6 | within_b    | relation_excess_w        |  0.100385   |  0.0977439   |  -0.00264122  |     -0.0604195  |        0.243076 |
| budget_refit      | D2      |        6 | cross       | relation_excess_w        |  0.0259269  |  0.0269417   |   0.00101481  |     -0.0907301  |        0.117996 |
| budget_refit      | D2      |        6 | within_a    | technical_disagreement_q |  0.958339   |  0.958339    | nan           |      0.796324   |        1.10309  |
| budget_refit      | D2      |        6 | within_b    | technical_disagreement_q |  0.90427    |  0.90427     | nan           |      0.763308   |        1.06077  |
| budget_refit      | D2      |        8 | within_a    | relation_excess_w        |  0.0518439  |  0.0526919   |   0.000847957 |     -0.0779734  |        0.176891 |
| budget_refit      | D2      |        8 | within_b    | relation_excess_w        |  0.111971   |  0.117568    |   0.00559726  |     -0.0332316  |        0.274699 |
| budget_refit      | D2      |        8 | cross       | relation_excess_w        |  0.104162   |  0.109376    |   0.00521365  |      0.00197058 |        0.202766 |
| budget_refit      | D2      |        8 | within_a    | technical_disagreement_q |  0.947308   |  0.947308    | nan           |      0.82344    |        1.07651  |
| budget_refit      | D2      |        8 | within_b    | technical_disagreement_q |  0.88327    |  0.88327     | nan           |      0.721513   |        1.02625  |
| budget_refit      | D2      |       10 | within_a    | relation_excess_w        |  0.0854285  |  0.0912306   |   0.00580214  |     -0.0794553  |        0.213153 |
| budget_refit      | D2      |       10 | within_b    | relation_excess_w        |  0.139975   |  0.145371    |   0.00539602  |     -0.0315261  |        0.33152  |
| budget_refit      | D2      |       10 | cross       | relation_excess_w        |  0.124434   |  0.129415    |   0.0049813   |      0.00281069 |        0.205521 |
| budget_refit      | D2      |       10 | within_a    | technical_disagreement_q |  0.90879    |  0.90879     | nan           |      0.785042   |        1.0724   |
| budget_refit      | D2      |       10 | within_b    | technical_disagreement_q |  0.855231   |  0.855231    | nan           |      0.664971   |        1.02391  |
| budget_refit      | D2      |       12 | within_a    | relation_excess_w        |  0.114144   |  0.122875    |   0.00873068  |      0.0215202  |        0.203787 |
| budget_refit      | D2      |       12 | within_b    | relation_excess_w        |  0.158095   |  0.164271    |   0.00617598  |     -0.001406   |        0.327284 |
| budget_refit      | D2      |       12 | cross       | relation_excess_w        |  0.143782   |  0.148744    |   0.0049627   |      0.0288367  |        0.25527  |
| budget_refit      | D2      |       12 | within_a    | technical_disagreement_q |  0.877477   |  0.877477    | nan           |      0.787029   |        0.969075 |
| budget_refit      | D2      |       12 | within_b    | technical_disagreement_q |  0.836373   |  0.836373    | nan           |      0.666808   |        0.993665 |

## Operator diagnostics

| arm               |   fit_budget |   application_budget | context   |   bandwidth |   active_nuisance_columns |   background_coverage |   background_fixed_point_rate |
|:------------------|-------------:|---------------------:|:----------|------------:|--------------------------:|----------------------:|------------------------------:|
| fixed_12_operator |           12 |                   12 | AskReddit |     12.8234 |                        44 |                     1 |                     0.0495181 |
| fixed_12_operator |           12 |                   12 | AskWomen  |     12.8914 |                        44 |                     1 |                     0.0500142 |
| budget_refit      |            4 |                    4 | AskReddit |     13.0155 |                        43 |                     1 |                     0.0534439 |
| budget_refit      |            4 |                    4 | AskWomen  |     12.6549 |                        40 |                     1 |                     0.0490221 |
| budget_refit      |            6 |                    6 | AskReddit |     12.9564 |                        44 |                     1 |                     0.0495748 |
| budget_refit      |            6 |                    6 | AskWomen  |     12.5806 |                        43 |                     1 |                     0.0491213 |
| budget_refit      |            8 |                    8 | AskReddit |     12.837  |                        44 |                     1 |                     0.0502338 |
| budget_refit      |            8 |                    8 | AskWomen  |     12.7843 |                        44 |                     1 |                     0.0497236 |
| budget_refit      |           10 |                   10 | AskReddit |     12.8667 |                        44 |                     1 |                     0.0492007 |
| budget_refit      |           10 |                   10 | AskWomen  |     12.9584 |                        44 |                     1 |                     0.0512585 |
| budget_refit      |           12 |                   12 | AskReddit |     12.8234 |                        44 |                     1 |                     0.0495181 |
| budget_refit      |           12 |                   12 | AskWomen  |     12.8914 |                        44 |                     1 |                     0.0500142 |

## Interpretation boundary

Opened-panel nested information-budget mechanism experiment on the previously inspected AskReddit--AskWomen D0/D1/D2 author cohort. The fixed-12 operator arm may distinguish added input information from budget-specific estimator refitting, but the result is development sensitivity rather than fresh confirmation. The deterministic reveal ladder is one content-blind design and does not establish optimal sampling. The experiment cannot establish personality, emotion, cognition, construct validity, causal situation response, population norms, language invariance, diagnosis, or clinical use.
