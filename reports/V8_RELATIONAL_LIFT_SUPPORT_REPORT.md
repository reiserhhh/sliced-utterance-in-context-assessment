# V8-HJIC-1A Relational-Lift Support Report

Status: `V8_HJIC1A_REPLICATED_RELATIONAL_SUPPORT_PARTIAL`

## Scope

This synthetic battery asks when independent replicated text views license a cross-family relation and when they license a unique dominant mode. Observable licensing is frozen before synthetic truth is opened.

Repetitions: 60.

## World summary

| world                      |   relation_license_rate |   mode_license_rate |   support_failure_rate |   mean_truth_fidelity |   mean_individual_correlation |
|:---------------------------|------------------------:|--------------------:|-----------------------:|----------------------:|------------------------------:|
| COMMON_NUISANCE            |                  0.0000 |              0.0000 |                 1.0000 |              nan      |                        0.4605 |
| CORRELATED_REPLICATE_ERROR |                  0.0000 |              0.0000 |                 0.0500 |              nan      |                        0.2052 |
| LOW_SINGULAR_GAP           |                  1.0000 |              0.0000 |                 0.0000 |                0.9857 |                        0.4155 |
| PRIVATE_AXES               |                  0.0000 |              0.0000 |                 0.0000 |              nan      |                        0.5414 |
| SHARED_LATENT              |                  1.0000 |              0.9333 |                 0.0000 |                0.9770 |                        0.3814 |
| SIMPSON_MIXTURE            |                  0.1333 |              0.0167 |                 0.0000 |                0.9990 |                        0.5451 |

## Key diagnostics

- Shared relation license rate: 1.0000.
- Shared unique-mode license rate: 0.9333.
- Truth fidelity among licensed shared worlds: 1.0000 (n=60).
- Low-gap relation/mode license rates: 1.0000 / 0.0000.
- Maximum negative-world relation license rate: 0.1333.
- Mean individual correlation in shared worlds: 0.3814 (diagnostic, not a gate).

## Gates

- `shared_relation_nonvacuity`: PASS
- `shared_mode_identification`: PASS
- `licensed_relation_fidelity`: PASS
- `negative_world_refusal`: FAIL
- `low_gap_relation_identification`: PASS
- `low_gap_mode_refusal`: PASS
- `truth_isolation`: PASS

## Ruling

A relation license and a unique-axis license are different claims. Stable cross-family structure can be measurable even when no unique dominant direction exists; shared latent variation can also remain underresolved and must then be refused.

Claim boundary: Passing licenses a synthetic, replicated-observation rule for separating relation existence from unique-mode identification. It does not establish that human text follows the generator, that either margin is personality, or that an identified relation transports across populations.
