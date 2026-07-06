# SUICA OP-9 Embedding Baseline (bge-large)

| construct             |   emb_to_construct_cv_r2 |
|:----------------------|-------------------------:|
| first_person_usage_v2 |                    0.896 |
| wcl_07                |                    0.874 |
| wcl_36                |                    0.838 |
| wcl_20                |                    0.829 |
| wcl_11                |                    0.805 |
| wcl_25                |                    0.792 |
| wcl_35                |                    0.752 |
| wcl_02                |                    0.745 |
| wcl_03                |                    0.703 |
| wcl_13                |                    0.684 |
| directive_action_v2   |                    0.679 |
| wcl_45                |                    0.677 |
| wcl_23                |                    0.635 |
| novelty_play_v2       |                    0.627 |
| wcl_22                |                    0.605 |
| wcl_60                |                    0.563 |
| wcl_54                |                    0.559 |
| wcl_15                |                    0.545 |
| tension_core_v2       |                    0.315 |

```json
{
  "model": "BAAI/bge-large-en-v1.5",
  "n_users": 3183,
  "M1_auc_embedding": 0.8910642848252611,
  "M1_auc_suica19": 0.8870736571889877,
  "M1_gap": 0.003990627636273447,
  "M1_gap_material_gt_010": false,
  "M2_pc_retest_top5": [
    0.681,
    0.685,
    0.722,
    0.669,
    0.664
  ],
  "M2_pc_retest_max": 0.7222595087257246,
  "M2_pc_retest_median_top30": 0.4923145424933632,
  "M3_subsumption_material": false,
  "M3_max_r2": 0.8964917070535088,
  "M3_median_r2": 0.6841680110480219,
  "M3_reverse_construct_to_pc_r2_top5": [
    0.79,
    0.827,
    0.574,
    0.673,
    0.673
  ]
}
```
