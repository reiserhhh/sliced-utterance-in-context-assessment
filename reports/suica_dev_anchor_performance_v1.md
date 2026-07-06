# SUICA Dev-Tier Anchor Performance (T2 orientation; LOCKBOX SEALED)

MBTI = Tier-D labels (lockbox users excluded); Big5 = Essays dev-half labels
(confirm half untouched). These numbers are development-tier orientation for
the worked-example manual, NOT confirmatory external validity.

| target            |    n |   ridge_cv_r_full_battery |   ridge_cv_r_style_only | best_univariate       |   best_r |   q_lt_05_count |
|:------------------|-----:|--------------------------:|------------------------:|:----------------------|---------:|----------------:|
| EI_cont           | 3183 |                     0.139 |                   0.128 | choice_ax_02          |   -0.086 |              15 |
| SN_cont           | 3183 |                     0.12  |                   0.112 | wcl_45                |    0.099 |               5 |
| TF_cont           | 3183 |                     0.346 |                   0.339 | wcl_03                |    0.316 |              22 |
| JP_cont           | 3183 |                     0.182 |                   0.172 | wcl_15                |   -0.108 |              17 |
| Extraversion      | 1255 |                   nan     |                   0.141 | wcl_35                |   -0.112 |               3 |
| Neuroticism       | 1255 |                   nan     |                   0.16  | first_person_usage_v2 |    0.122 |               7 |
| Agreeableness     | 1255 |                   nan     |                   0.109 | wcl_23                |   -0.133 |               3 |
| Conscientiousness | 1255 |                   nan     |                   0.117 | wcl_23                |   -0.114 |               4 |
| Openness          | 1255 |                   nan     |                   0.194 | first_person_usage_v2 |   -0.127 |               7 |

## Top univariate edges per target (q_BH < 0.05)

| feature               |      r |     p |    n |   q_bh | target            | source              |
|:----------------------|-------:|------:|-----:|-------:|:------------------|:--------------------|
| choice_ax_02          | -0.086 | 0     | 3177 |  0     | EI_cont           | pandora_tierD_mbti  |
| choice_ax_05          | -0.085 | 0     | 3177 |  0     | EI_cont           | pandora_tierD_mbti  |
| wcl_11                | -0.075 | 0     | 3183 |  0     | EI_cont           | pandora_tierD_mbti  |
| wcl_15                |  0.072 | 0     | 3183 |  0     | EI_cont           | pandora_tierD_mbti  |
| wcl_22                | -0.067 | 0     | 3183 |  0.001 | EI_cont           | pandora_tierD_mbti  |
| wcl_45                |  0.099 | 0     | 3183 |  0     | SN_cont           | pandora_tierD_mbti  |
| wcl_54                |  0.093 | 0     | 3183 |  0     | SN_cont           | pandora_tierD_mbti  |
| wcl_36                | -0.076 | 0     | 3183 |  0     | SN_cont           | pandora_tierD_mbti  |
| first_person_usage_v2 | -0.053 | 0.003 | 3183 |  0.021 | SN_cont           | pandora_tierD_mbti  |
| choice_ax_06          |  0.048 | 0.006 | 3177 |  0.04  | SN_cont           | pandora_tierD_mbti  |
| wcl_03                |  0.316 | 0     | 3183 |  0     | TF_cont           | pandora_tierD_mbti  |
| first_person_usage_v2 |  0.227 | 0     | 3183 |  0     | TF_cont           | pandora_tierD_mbti  |
| wcl_36                |  0.198 | 0     | 3183 |  0     | TF_cont           | pandora_tierD_mbti  |
| wcl_54                | -0.194 | 0     | 3183 |  0     | TF_cont           | pandora_tierD_mbti  |
| wcl_11                | -0.148 | 0     | 3183 |  0     | TF_cont           | pandora_tierD_mbti  |
| wcl_15                | -0.108 | 0     | 3183 |  0     | JP_cont           | pandora_tierD_mbti  |
| wcl_23                | -0.102 | 0     | 3183 |  0     | JP_cont           | pandora_tierD_mbti  |
| choice_ax_03          |  0.102 | 0     | 3177 |  0     | JP_cont           | pandora_tierD_mbti  |
| choice_ax_05          | -0.085 | 0     | 3177 |  0     | JP_cont           | pandora_tierD_mbti  |
| novelty_play_v2       | -0.083 | 0     | 3183 |  0     | JP_cont           | pandora_tierD_mbti  |
| wcl_35                | -0.112 | 0     | 1255 |  0.001 | Extraversion      | essays_devhalf_big5 |
| wcl_25                | -0.102 | 0     | 1255 |  0.003 | Extraversion      | essays_devhalf_big5 |
| wcl_03                |  0.082 | 0.004 | 1255 |  0.024 | Extraversion      | essays_devhalf_big5 |
| first_person_usage_v2 |  0.122 | 0     | 1255 |  0     | Neuroticism       | essays_devhalf_big5 |
| novelty_play_v2       | -0.098 | 0.001 | 1255 |  0.005 | Neuroticism       | essays_devhalf_big5 |
| wcl_60                | -0.094 | 0.001 | 1255 |  0.005 | Neuroticism       | essays_devhalf_big5 |
| wcl_13                |  0.086 | 0.002 | 1255 |  0.011 | Neuroticism       | essays_devhalf_big5 |
| wcl_07                | -0.074 | 0.009 | 1255 |  0.031 | Neuroticism       | essays_devhalf_big5 |
| wcl_23                | -0.133 | 0     | 1255 |  0     | Agreeableness     | essays_devhalf_big5 |
| wcl_54                | -0.098 | 0     | 1255 |  0.005 | Agreeableness     | essays_devhalf_big5 |
| wcl_03                |  0.076 | 0.007 | 1255 |  0.044 | Agreeableness     | essays_devhalf_big5 |
| wcl_23                | -0.114 | 0     | 1255 |  0.001 | Conscientiousness | essays_devhalf_big5 |
| wcl_15                | -0.089 | 0.002 | 1255 |  0.01  | Conscientiousness | essays_devhalf_big5 |
| wcl_36                |  0.089 | 0.002 | 1255 |  0.01  | Conscientiousness | essays_devhalf_big5 |
| wcl_60                | -0.087 | 0.002 | 1255 |  0.01  | Conscientiousness | essays_devhalf_big5 |
| first_person_usage_v2 | -0.127 | 0     | 1255 |  0     | Openness          | essays_devhalf_big5 |
| wcl_02                | -0.121 | 0     | 1255 |  0     | Openness          | essays_devhalf_big5 |
| wcl_36                | -0.109 | 0     | 1255 |  0.001 | Openness          | essays_devhalf_big5 |
| wcl_35                |  0.093 | 0.001 | 1255 |  0.005 | Openness          | essays_devhalf_big5 |
| wcl_22                |  0.088 | 0.002 | 1255 |  0.007 | Openness          | essays_devhalf_big5 |
