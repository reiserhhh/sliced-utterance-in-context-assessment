# v4 composite — channel-family dev performance + frozen weights

| target            |   C_ONLY |   FULL31 |   F_ONLY |   F_PLUS_C |   F_PLUS_Ccons |   STYLE19 |
|:------------------|---------:|---------:|---------:|-----------:|---------------:|----------:|
| Agreeableness     |  nan     |  nan     |    0.117 |    nan     |          0.118 |     0.109 |
| Conscientiousness |  nan     |  nan     |    0.119 |    nan     |          0.103 |     0.117 |
| EI_cont           |    0.12  |    0.139 |    0.036 |      0.124 |        nan     |   nan     |
| Extraversion      |  nan     |  nan     |   -0.001 |    nan     |          0.082 |     0.141 |
| JP_cont           |    0.134 |    0.182 |    0.105 |      0.16  |        nan     |   nan     |
| Neuroticism       |  nan     |  nan     |    0.15  |    nan     |          0.16  |     0.16  |
| Openness          |  nan     |  nan     |    0.111 |    nan     |          0.192 |     0.194 |
| SN_cont           |    0.095 |    0.12  |    0.039 |      0.094 |        nan     |   nan     |
| TF_cont           |    0.27  |    0.346 |    0.228 |      0.292 |        nan     |   nan     |

F-family = first_person_usage_v2, wcl_60, wcl_13, wcl_23
C-family constructs = directive_action_v2, novelty_play_v2, wcl_25, wcl_02, wcl_54, wcl_22, wcl_35, wcl_20

Weights for {FULL31, F_PLUS_C} x MBTI axes frozen in v4_frozen_weights.json (opening-#2 candidates; sealed at commit).
Conventions identical to dev_anchor v1 (RidgeCV logspace(-1,3,9), KFold5 seed42). Tier-D orientation only; no lockbox contact.
