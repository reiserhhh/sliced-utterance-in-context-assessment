# SUICA M4-C.3.3 Mechanism Decomposition

## Status

Post-hoc decomposition of the frozen C3.3 endpoint. It does not alter the
preregistered `M4_C33_NO_GO_INFORMATION_LIMIT` decision.

## Main decomposition

- Passive opportunity, `K=8 - K=1`: geometry delta
  `0.0611`
  [0.0364,
  0.0824].
- Orthogonal excitation at `K=8`: geometry delta
  `0.0192`
  [0.0033,
  0.0372].
- Most endpoint improvement therefore comes from repeated observable
  opportunity. Excitation contributes a smaller conditional increment.
- The arm mean peaks at `K=4 excitation`; the `K=8` arm does not improve
  further, so the observed frontier is saturating rather than unlimited.

## Arm means

|   k | intervention   |   fisher_minimum_information |   baseline_geometry |   oracle_swap_geometry |   creation_headroom |   fisher_geometry |   fisher_gain |   hazard_relative_degradation |
|----:|:---------------|-----------------------------:|--------------------:|-----------------------:|--------------------:|------------------:|--------------:|------------------------------:|
|   1 | excitation     |                      80.7302 |              0.6152 |                 0.8969 |              0.2817 |            0.6978 |        0.0826 |                        0.0173 |
|   1 | passive        |                      53.3927 |              0.6181 |                 0.8969 |              0.2789 |            0.6721 |        0.0540 |                        0.0220 |
|   2 | excitation     |                     163.1323 |              0.6197 |                 0.8969 |              0.2773 |            0.7360 |        0.1163 |                        0.0031 |
|   2 | passive        |                     106.1568 |              0.6455 |                 0.8969 |              0.2514 |            0.7146 |        0.0691 |                        0.0242 |
|   4 | excitation     |                     326.8956 |              0.6293 |                 0.8969 |              0.2676 |            0.7585 |        0.1291 |                        0.0072 |
|   4 | passive        |                     213.3943 |              0.6550 |                 0.8969 |              0.2420 |            0.7239 |        0.0689 |                        0.0133 |
|   8 | excitation     |                     657.9622 |              0.6386 |                 0.8969 |              0.2584 |            0.7523 |        0.1137 |                        0.0009 |
|   8 | passive        |                     430.9983 |              0.6611 |                 0.8969 |              0.2359 |            0.7332 |        0.0721 |                        0.0084 |

## Paired contrasts

| contrast                           |   high_k | high_intervention   |   low_k | low_intervention   |   geometry_delta |   geometry_ci_lower |   geometry_ci_upper |   information_ratio |   positive_repetitions |   total_repetitions |
|:-----------------------------------|---------:|:--------------------|--------:|:-------------------|-----------------:|--------------------:|--------------------:|--------------------:|-----------------------:|--------------------:|
| total_K8exc_minus_K1pass           |        8 | excitation          |       1 | passive            |           0.0802 |              0.0613 |              0.0989 |             13.0378 |                      8 |                   8 |
| opportunity_passive_K8_minus_K1    |        8 | passive             |       1 | passive            |           0.0611 |              0.0364 |              0.0824 |              8.1895 |                      7 |                   8 |
| opportunity_excitation_K8_minus_K1 |        8 | excitation          |       1 | excitation         |           0.0545 |              0.0376 |              0.0778 |              8.1297 |                      8 |                   8 |
| excitation_increment_K1            |        1 | excitation          |       1 | passive            |           0.0257 |             -0.0005 |              0.0505 |              1.6095 |                      6 |                   8 |
| excitation_increment_K2            |        2 | excitation          |       2 | passive            |           0.0214 |             -0.0006 |              0.0443 |              1.6065 |                      5 |                   8 |
| excitation_increment_K4            |        4 | excitation          |       4 | passive            |           0.0346 |              0.0149 |              0.0575 |              1.5928 |                      8 |                   8 |
| excitation_increment_K8            |        8 | excitation          |       8 | passive            |           0.0192 |              0.0033 |              0.0372 |              1.5880 |                      7 |                   8 |

## World heterogeneity

| world                               |   low_geometry |   high_geometry |   endpoint_delta |   high_fisher_gain |   high_creation_headroom |   high_recovered_headroom |
|:------------------------------------|---------------:|----------------:|-----------------:|-------------------:|-------------------------:|--------------------------:|
| endogenous_creation_expansion       |         0.7258 |          0.8022 |           0.0764 |             0.1480 |                   0.2752 |                    0.5378 |
| endogenous_source_partition_matched |         0.5330 |          0.5743 |           0.0413 |             0.0656 |                   0.4049 |                    0.1621 |
| history_gated_ecology               |         0.7829 |          0.8458 |           0.0629 |            -0.0163 |                   0.0755 |                   -0.2157 |
| selection_creation_compensation     |         0.6426 |          0.7442 |           0.1017 |             0.2431 |                   0.3000 |                    0.8104 |
| source_rotated_feedback             |         0.6762 |          0.7950 |           0.1188 |             0.1283 |                   0.2363 |                    0.5430 |

## Repetition endpoints

|   repetition |   high_geometry |   high_gain |   high_creation_headroom |   high_recovered_headroom | frozen_repetition_gate   |
|-------------:|----------------:|------------:|-------------------------:|--------------------------:|:-------------------------|
|            0 |          0.5780 |      0.0452 |                   0.2832 |                    0.1596 | False                    |
|            1 |          0.7011 |      0.1420 |                   0.3642 |                    0.3897 | True                     |
|            2 |          0.8807 |      0.0363 |                   0.1102 |                    0.3300 | True                     |
|            3 |          0.7864 |      0.3450 |                   0.4399 |                    0.7844 | True                     |
|            4 |          0.8021 |      0.0612 |                   0.1770 |                    0.3459 | True                     |
|            5 |          0.6968 |      0.0673 |                   0.2367 |                    0.2843 | False                    |
|            6 |          0.7651 |     -0.0136 |                   0.1199 |                   -0.1135 | False                    |
|            7 |          0.8085 |      0.2265 |                   0.3358 |                    0.6746 | True                     |

## Interpretation boundary

Observable creation information is causally useful in these synthetic worlds,
but it is not sufficient for uniform loop reconstruction. The residual is
mechanism-dependent: `history_gated_ecology` remains negative while
`selection_creation_compensation` recovers most oracle headroom. The next
experiment should therefore target heterogeneous creation laws or latent
history state, not merely increase `K` or replace the embedding/kernel.

This is a synthetic mechanism result. It is not personality validity, natural
text validity, or authorization for M4-D.
