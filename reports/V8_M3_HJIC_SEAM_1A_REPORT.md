# V8-M3-HJIC-SEAM-1 Formal Report

Status: `V8_M3_HJIC_SEAM1A_BETWEEN_NULL_PARTIAL`

This battery tests the complete registered arrow from synthetic raw event paths through a frozen generator-blind M3 quotient to an HJIC context relation field and its explicit refusal modes.

## World summary

| world                         |   relation_license_rate |   seam_license_rate |   cancellation_rate |   ecological_rate |   mismatch_rate |   d1_d2_agreement |
|:------------------------------|------------------------:|--------------------:|--------------------:|------------------:|----------------:|------------------:|
| BALANCED_CONTEXT_CANCELLATION |                  0.9333 |              0.9333 |              0.9333 |            0.0000 |          0.0000 |            0.9667 |
| ECOLOGICAL_ONLY               |                  0.0000 |              0.0000 |              0.0000 |            0.9667 |          0.0000 |            1.0000 |
| ESTIMATION_ATTENUATION        |                  0.9000 |              0.9000 |              0.0000 |            0.0000 |          0.0000 |            0.9500 |
| GLOBAL_INVARIANT              |                  0.9667 |              0.9667 |              0.0000 |            0.0000 |          0.0000 |            0.9833 |
| HELDOUT_D0_NULL               |                  0.0000 |              0.0000 |              0.0000 |            0.0000 |          0.0000 |            1.0000 |
| MECHANISM_FAMILY_MISMATCH     |                  0.0000 |              0.0000 |              0.0000 |            0.0000 |          1.0000 |            1.0000 |
| MICRO_GAUGE_ALIAS             |                  0.9333 |              0.9333 |              0.0000 |            0.0000 |          0.0000 |            0.9500 |

## Headline diagnostics

- Clean seam license: 0.9667.
- Clean relation fidelity q05 / relative error q95: 0.9897 / 0.1963.
- Covariance decomposition error q95: 1.681e-15.
- Primary population 95% coverage: 0.9062 (870/960); nested sensitivity 0.9177.
- Gauge output q95 / identity license / seam license: 7.853e-16 / 0.0000 / 0.9333.
- Attenuation correction win rate / median error reduction: 0.9667 / 0.6162.
- Cancellation detect / false global: 0.9333 / 0.0000.
- Ecological detect / false individual relation: 0.9667 / 0.0000.
- Mechanism mismatch detect / false seam license: 1.0000 / 0.0000.
- Held-out-null / mismatch false ecological classification: 0.0000 / 0.0000.

## Gates

- `clean_end_to_end_recovery`: PASS
- `aggregation_commutation`: PASS
- `population_uncertainty_coverage`: PASS
- `gauge_alias_refusal`: FAIL
- `attenuation_correction`: PASS
- `balanced_context_cancellation`: FAIL
- `ecological_only_refusal`: PASS
- `mechanism_family_mismatch_refusal`: PASS
- `heldout_between_null_safety`: PASS
- `independent_confirmation_agreement`: PASS
- `truth_isolation`: PASS

## Ruling

The licensed object is an observable event-to-relation procedure, not a unique hidden mechanism. A stable out-of-family periodic signal is reported as estimator-family mismatch rather than erased or relabelled as absence.

Claim boundary: Passing establishes only that a D0-calibrated between-context relation null, distinct from the max-context local null, restores registered synthetic ecological classification without increasing individual or held-out-null false licenses. Measurement-operator drift remains intentionally present and unlicensed; personality, causal, human, language, diagnostic, and unique-mechanism claims remain outside scope.
