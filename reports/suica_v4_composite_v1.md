# v4 composite — channel-family dev performance + frozen weights

| target            |   C_ONLY |   FULL31 |   F_ONLY |   F_PLUS_C |   F_PLUS_Ccons |   STYLE19 |
|:------------------|---------:|---------:|---------:|-----------:|---------------:|----------:|
| Agreeableness     |  nan     |  nan     |    0.006 |    nan     |          0.095 |     0.109 |
| Conscientiousness |  nan     |  nan     |    0.033 |    nan     |          0.108 |     0.117 |
| EI_cont           |    0.112 |    0.139 |    0.058 |      0.118 |        nan     |   nan     |
| Extraversion      |  nan     |  nan     |    0.102 |    nan     |          0.1   |     0.141 |
| JP_cont           |    0.151 |    0.182 |    0.034 |      0.151 |        nan     |   nan     |
| Neuroticism       |  nan     |  nan     |    0.099 |    nan     |          0.169 |     0.16  |
| Openness          |  nan     |  nan     |    0.148 |    nan     |          0.199 |     0.194 |
| SN_cont           |    0.054 |    0.12  |    0.047 |      0.066 |        nan     |   nan     |
| TF_cont           |    0.243 |    0.346 |    0.239 |      0.28  |        nan     |   nan     |

F-family = first_person_usage_v2, wcl_35
C-family constructs = directive_action_v2, novelty_play_v2, wcl_60, wcl_02, wcl_07, wcl_22, wcl_23

Weights for {FULL31, F_PLUS_C} x MBTI axes frozen in v4_frozen_weights.json (opening-#2 candidates; sealed at commit).
Conventions identical to dev_anchor v1 (RidgeCV logspace(-1,3,9), KFold5 seed42). Tier-D orientation only; no lockbox contact.
