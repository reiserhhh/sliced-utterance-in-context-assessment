# OP-34 SB-corrected gate sensitivity (no relabel)

| construct             |   class_disj_raw |   rel_early |   rel_late |   class_disj_SBcorrected |   share | family_raw                 | family_SBcorrected     | CHANGED   |
|:----------------------|-----------------:|------------:|-----------:|-------------------------:|--------:|:---------------------------|:-----------------------|:----------|
| first_person_usage_v2 |           0.2682 |       0.467 |      0.467 |                   0.5744 |   0.279 | F-family (flesh trait)     | F-family (flesh trait) | False     |
| directive_action_v2   |           0.0997 |       0.197 |      0.227 |                   0.4711 |   0.471 | C-family (venue signature) | composite              | True      |
| tension_core_v2       |           0.0528 |       0.176 |      0.162 |                   0.3123 | nan     | undetermined               | undetermined           | False     |
| novelty_play_v2       |           0.0328 |       0.038 |      0.013 |                   1      |   0.587 | C-family (venue signature) | composite              | True      |
| wcl_60                |           0.3646 |       0.697 |      0.698 |                   0.5228 |   0.053 | F-family (flesh trait)     | F-family (flesh trait) | False     |
| wcl_03                |           0.1404 |       0.329 |      0.279 |                   0.463  |   0.508 | composite                  | composite              | False     |
| wcl_36                |           0.1593 |       0.359 |      0.307 |                   0.4802 |   0.385 | composite                  | composite              | False     |
| wcl_11                |           0.1021 |       0.262 |      0.276 |                   0.3794 |   0.492 | composite                  | composite              | False     |
| wcl_45                |           0.1591 |       0.339 |      0.28  |                   0.5163 |   0.32  | composite                  | composite              | False     |
| wcl_25                |           0.0749 |       0.159 |      0.16  |                   0.4689 |   0.538 | C-family (venue signature) | composite              | True      |
| wcl_02                |           0.0415 |       0.052 |      0.097 |                   0.5837 |   0.593 | C-family (venue signature) | composite              | True      |
| wcl_07                |           0.1096 |       0.142 |      0.179 |                   0.6862 |   0.336 | composite                  | composite              | False     |
| wcl_54                |           0.0956 |       0.177 |      0.195 |                   0.5146 |   0.329 | C-family (venue signature) | composite              | True      |
| wcl_22                |           0.0998 |       0.143 |      0.156 |                   0.6678 |   0.376 | C-family (venue signature) | composite              | True      |
| wcl_13                |           0.1694 |       0.23  |      0.268 |                   0.6826 |   0.014 | F-family (flesh trait)     | F-family (flesh trait) | False     |
| wcl_35                |           0.074  |       0.153 |      0.2   |                   0.4231 |   0.611 | C-family (venue signature) | composite              | True      |
| wcl_15                |           0.1349 |       0.31  |      0.263 |                   0.4723 |   0.333 | composite                  | composite              | False     |
| wcl_23                |           0.1687 |       0.278 |      0.313 |                   0.5719 |   0.172 | F-family (flesh trait)     | F-family (flesh trait) | False     |
| wcl_20                |           0.0211 |       0.037 |      0.049 |                   0.4929 |   0.595 | C-family (venue signature) | composite              | True      |

{
  "n_changed": 8,
  "changed": [
    {
      "construct": "directive_action_v2",
      "family_raw": "C-family (venue signature)",
      "family_SBcorrected": "composite"
    },
    {
      "construct": "novelty_play_v2",
      "family_raw": "C-family (venue signature)",
      "family_SBcorrected": "composite"
    },
    {
      "construct": "wcl_25",
      "family_raw": "C-family (venue signature)",
      "family_SBcorrected": "composite"
    },
    {
      "construct": "wcl_02",
      "family_raw": "C-family (venue signature)",
      "family_SBcorrected": "composite"
    },
    {
      "construct": "wcl_54",
      "family_raw": "C-family (venue signature)",
      "family_SBcorrected": "composite"
    },
    {
      "construct": "wcl_22",
      "family_raw": "C-family (venue signature)",
      "family_SBcorrected": "composite"
    },
    {
      "construct": "wcl_35",
      "family_raw": "C-family (venue signature)",
      "family_SBcorrected": "composite"
    },
    {
      "construct": "wcl_20",
      "family_raw": "C-family (venue signature)",
      "family_SBcorrected": "composite"
    }
  ],
  "note": "SENSITIVITY ONLY \u2014 no registry relabel; candidates for round-11 audit"
}
