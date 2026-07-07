# EXPL-1 — Fit-gradient baseline (EXPLORATORY, NON-CONFIRMATORY)

> EXPLORATORY / NON-CONFIRMATORY — post-opening reuse of spent labels (EXPL-1)
>
> Labels spent at opening #1; reuse here is exploratory. Same 1,058
> eligible users, same gate, fixed folds (KFold 5, shuffle, rs=42).

| rung | model | E | N | A | C | O | mean |
|---|---|---|---|---|---|---|---|
| 1 full fit | ridge over tf-idf 1-grams | +0.314 | +0.302 | +0.288 | +0.183 | +0.275 | +0.272 |
| 2 weight fit | ridge over 16 frozen features | +0.091 | +0.166 | -0.008 | +0.097 | +0.105 | +0.090 |
| 3 no fit | preregistered single constructs | — | +0.111 (first person) | — | — | +0.096 (politics choice) | — |

External anchor (different user set/protocol): official LR-N mean r = .246 (n=1,402), LR-NP mean r = .293 (n=1,386),
reproduced in results/pandora_paper_baseline_reproduction (delta <= .0014).
