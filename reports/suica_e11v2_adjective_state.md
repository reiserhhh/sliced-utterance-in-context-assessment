# SUICA E11 v2 Adjective Projection (state)

| target   |   rank_stability |   n_sig_axes | axis_E              | axis_A              | axis_C              | axis_N              | axis_O              | enrichment_beyond_null   |
|:---------|-----------------:|-------------:|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:-------------------------|
| state_f1 |            0.904 |            0 | +0.004[-0.01,+0.01] | +0.020[+0.00,+0.03] | +0.013[-0.00,+0.02] | -0.012[-0.03,+0.00] | +0.020[+0.00,+0.03] | False                    |
| state_f3 |            0.904 |            0 | -0.002[-0.01,+0.01] | +0.009[-0.00,+0.02] | +0.010[-0.00,+0.02] | +0.018[+0.01,+0.02] | -0.002[-0.01,+0.01] | False                    |
| state_f5 |            0.946 |            0 | -0.008[-0.02,+0.00] | -0.023[-0.03,-0.01] | -0.032[-0.04,-0.02] | +0.012[+0.00,+0.02] | -0.008[-0.02,+0.00] | False                    |

## Top-10 contrast adjectives (value [bootstrap CI], !lex = lexical-coupling flag)

- **state_f1**: optimistic(+2.8[+1.9,+3.2]), instructional(+2.3[+1.4,+2.9]), organized(+2.0[+0.8,+2.3]), contented(+2.0[+0.8,+2.6]), conventional(+2.0[+0.5,+3.2]), inefficient(+2.0[+1.0,+2.9]), stable(+1.9[+0.9,+2.7]), artistic(+1.8[+0.8,+2.5]), considerate(+1.8[+0.6,+2.3]), creative(+1.7[+0.7,+2.3])
- **state_f3**: hesitant(+2.7[+1.7,+3.0]), insecure(+2.4[+1.5,+2.9]), anxious(+2.3[+1.4,+2.7]), fretful(+2.1[+1.2,+2.6]), shy(+2.1[+1.3,+3.0]), nervous(+2.0[+1.2,+2.4]), simple(+1.8[+0.8,+2.6]), trustful(+1.7[+0.7,+2.3]), nostalgic(+1.7[+0.9,+2.3]), pragmatic(+1.6[+0.6,+2.3])
- **state_f5**: impractical(+3.5[+2.5,+4.1]), negligent(+2.9[+2.1,+3.3]), demanding(+2.6[+1.9,+3.0]), inefficient(+2.4[+1.6,+3.1]), imperturbable(+2.2[+0.8,+2.9]), impulsive(+2.2[+1.6,+2.6]), careless(+2.1[+1.5,+2.6]), inconsistent(+2.1[+1.1,+2.6]), simple(+2.0[+0.6,+2.8]), harsh(+2.0[+1.3,+2.4])

```json
{
  "mode": "state",
  "n_units": 1175,
  "V2_1_median_rank_stability": 0.9041437974240669,
  "V2_1_pass": true,
  "V2_2_targets_with_sig_axis": 0,
  "V2_2_pass": false,
  "V2_3_mean_jaccard": 0.043634727845254156,
  "V2_3_pass": true,
  "V2_4_null_axis_hit_rate": 0.026,
  "V2_4_pass": false,
  "axis_thresholds_99pct": {
    "E": 0.07585356407206514,
    "A": 0.07765854298674303,
    "C": 0.0716576644679201,
    "N": 0.0651770209960084,
    "O": 0.07623537737666192
  },
  "enrichment_odds_thr_95pct": 8.0
}
```
