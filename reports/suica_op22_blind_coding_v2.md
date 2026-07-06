# SUICA OP-22 Blind Coding v2 Results

| construct   |   n_items |   acc_deepseek |   acc_qwen30 |   acc_llama30 |   acc_mistral20 |   acc_pooled |   coders_above_chance |   human_correct |   human_n |   t2_pooled | t1_llm_pass   | t2_pass   | op22_pass   | human_pass   |
|:------------|----------:|---------------:|-------------:|--------------:|----------------:|-------------:|----------------------:|----------------:|----------:|------------:|:--------------|:----------|:------------|:-------------|
| wcl_02      |        16 |          0.875 |        0.688 |         0.812 |           0.562 |        0.734 |                     4 |               8 |         8 |       0.875 | True          | True      | True        | True         |
| wcl_03      |        16 |          0.75  |        0.562 |         0.688 |           0.5   |        0.625 |                     4 |               3 |         8 |       0.458 | True          | False     | False       | False        |
| wcl_07      |        16 |          1     |        0.875 |         0.812 |           0.562 |        0.812 |                     4 |               7 |         8 |       0.792 | True          | True      | True        | True         |
| wcl_11      |        16 |          0.938 |        0.875 |         0.938 |           0.562 |        0.828 |                     4 |               7 |         8 |       0.958 | True          | True      | True        | True         |
| wcl_13      |        16 |          0.75  |        0.438 |         0.312 |           0.375 |        0.469 |                     3 |               3 |         8 |       0.875 | False         | True      | False       | False        |
| wcl_15      |        16 |          0.688 |        0.625 |         0.5   |           0.312 |        0.531 |                     3 |               3 |         8 |       0.25  | True          | False     | False       | False        |
| wcl_20      |        16 |          1     |        1     |         0.938 |           0.562 |        0.875 |                     4 |               7 |         8 |       1     | True          | True      | True        | True         |
| wcl_22      |        16 |          0.438 |        0.438 |         0.25  |           0.562 |        0.422 |                     3 |               2 |         8 |       0.708 | False         | False     | False       | False        |
| wcl_23      |        16 |          0.875 |        0.812 |         0.812 |           0.688 |        0.797 |                     4 |               6 |         8 |       0.708 | True          | False     | False       | True         |
| wcl_25      |        16 |          0.75  |        0.812 |         0.875 |           0.625 |        0.766 |                     4 |               6 |         8 |       0.833 | True          | True      | True        | True         |
| wcl_35      |        16 |          1     |        1     |         1     |           0.938 |        0.984 |                     4 |               7 |         8 |       1     | True          | True      | True        | True         |
| wcl_36      |        16 |          0.938 |        0.875 |         0.812 |           0.625 |        0.812 |                     4 |               5 |         8 |       0.917 | True          | True      | True        | True         |
| wcl_45      |        16 |          0.938 |        1     |         0.938 |           0.875 |        0.938 |                     4 |               7 |         8 |       1     | True          | True      | True        | True         |
| wcl_54      |        16 |          0.562 |        0.625 |         0.562 |           0.438 |        0.547 |                     4 |               2 |         8 |       0.667 | True          | False     | False       | False        |
| wcl_60      |        16 |          0.75  |        0.438 |         0.438 |           0.25  |        0.469 |                     3 |               0 |         8 |       0.708 | False         | False     | False       | False        |

```json
{
  "constructs_op22_pass": 8,
  "has_human": true,
  "pairwise_agreement": {
    "deepseek~qwen30": 0.7833333333333333,
    "deepseek~llama30": 0.7625,
    "deepseek~mistral20": 0.6,
    "qwen30~llama30": 0.7291666666666666,
    "qwen30~mistral20": 0.575,
    "llama30~mistral20": 0.6541666666666667
  }
}
```
