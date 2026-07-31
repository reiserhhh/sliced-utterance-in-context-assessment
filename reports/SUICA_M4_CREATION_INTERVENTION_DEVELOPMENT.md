# SUICA M4-C.3.2 Creation Intervention Development

## Decision

`M4_C32_KERNEL_PATH_STOP`

The C3.1 relational budget identified creation as the largest symmetric loss
allocation. This development experiment tests that diagnosis by changing only
the creation estimator. Response and choice edges remain frozen at their
discovered-route estimates:

\[
L^{(j)}_u=A^{(j)}_uR^D_uD^D_u.
\]

The candidate basis is a calibration-only centered RBF relation kernel,
transported to selection and evaluation conditions by Nyström extension.
Ranks and bandwidths are development arms, not confirmed hyperparameters.

## Design

- repetitions: `4`
- worlds: `endogenous_source_partition_matched, endogenous_creation_expansion, source_rotated_feedback, history_gated_ecology, selection_creation_compensation`
- kernel ranks: `[2, 4, 8, 12]`
- bandwidth scales: `[0.5, 1.0, 2.0]`
- response/choice intervention status: frozen
- endpoint: author-pair geometry of the physical loop

## Arm results

| arm              |   candidate_creation_only_geometry |   candidate_gain |   candidate_gain_lcb |   creation_headroom |   recovered_headroom |   baseline_creation_geometry |   candidate_creation_geometry |   positive_repetitions | development_candidate   |
|:-----------------|-----------------------------------:|-----------------:|---------------------:|--------------------:|---------------------:|-----------------------------:|------------------------------:|-----------------------:|:------------------------|
| kernel_r12_bw1   |                             0.5316 |          -0.1386 |              -0.2168 |              0.2497 |              -0.5552 |                       0.7141 |                        0.5081 |                      0 | False                   |
| kernel_r12_bw0.5 |                             0.5092 |          -0.1609 |              -0.2802 |              0.2497 |              -0.6446 |                       0.7141 |                        0.5110 |                      0 | False                   |
| kernel_r8_bw1    |                             0.5030 |          -0.1672 |              -0.2594 |              0.2497 |              -0.6697 |                       0.7141 |                        0.4872 |                      0 | False                   |
| kernel_r8_bw0.5  |                             0.4918 |          -0.1784 |              -0.2817 |              0.2497 |              -0.7145 |                       0.7141 |                        0.5039 |                      0 | False                   |
| kernel_r12_bw2   |                             0.4550 |          -0.2152 |              -0.3114 |              0.2497 |              -0.8619 |                       0.7141 |                        0.3875 |                      0 | False                   |
| kernel_r8_bw2    |                             0.4349 |          -0.2353 |              -0.3286 |              0.2497 |              -0.9422 |                       0.7141 |                        0.3814 |                      0 | False                   |
| kernel_r4_bw0.5  |                             0.4084 |          -0.2618 |              -0.3343 |              0.2497 |              -1.0486 |                       0.7141 |                        0.3613 |                      0 | False                   |
| kernel_r4_bw1    |                             0.4069 |          -0.2633 |              -0.3730 |              0.2497 |              -1.0545 |                       0.7141 |                        0.3527 |                      0 | False                   |
| kernel_r4_bw2    |                             0.3415 |          -0.3287 |              -0.4231 |              0.2497 |              -1.3164 |                       0.7141 |                        0.2816 |                      0 | False                   |
| kernel_r2_bw1    |                             0.2911 |          -0.3791 |              -0.4797 |              0.2497 |              -1.5183 |                       0.7141 |                        0.2531 |                      0 | False                   |
| kernel_r2_bw0.5  |                             0.2715 |          -0.3987 |              -0.4874 |              0.2497 |              -1.5968 |                       0.7141 |                        0.2636 |                      0 | False                   |
| kernel_r2_bw2    |                             0.2353 |          -0.4349 |              -0.5178 |              0.2497 |              -1.7419 |                       0.7141 |                        0.1866 |                      0 | False                   |

## Best development arm

- arm: `kernel_r12_bw1`
- creation-only geometry: `0.5316`
- gain over chart baseline: `-0.1386`
- clustered gain LCB: `-0.2168`
- oracle creation headroom: `0.2497`
- recovered headroom: `-0.5552`
- baseline/candidate creation geometry: `0.7141` / `0.5081`
- positive repetitions: `0/4`

## Boundary

Development-only synthetic intervention. Candidate creation estimators are fitted without response outcomes in their basis, then inserted into frozen discovered response and choice edges. A candidate can justify an independent confirmation but cannot reopen M4-C.2, establish personality, validate natural text, or authorize M4-D.

Even a passing development arm still lacks an independent frozen seed,
selection-risk noninferiority, specificity worlds, alias refusal, and
multiplicity protection. Therefore this run can only choose whether an
independent C3.2 confirmation is warranted.
