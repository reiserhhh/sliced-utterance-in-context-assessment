# V8-M3-HJIC-SEAM-1 Formal Report

Status: `V8_M3_HJIC_SEAM1_PARTIAL`

This battery tests the complete registered arrow from synthetic raw event paths through a frozen generator-blind M3 quotient to an HJIC context relation field and its explicit refusal modes.

## World summary

| world                         |   relation_license_rate |   seam_license_rate |   cancellation_rate |   ecological_rate |   mismatch_rate |   d1_d2_agreement |
|:------------------------------|------------------------:|--------------------:|--------------------:|------------------:|----------------:|------------------:|
| BALANCED_CONTEXT_CANCELLATION |                  1.0000 |              1.0000 |              1.0000 |            0.0000 |          0.0000 |            1.0000 |
| ECOLOGICAL_ONLY               |                  0.0000 |              0.0000 |              0.0000 |            0.8500 |          0.0000 |            1.0000 |
| ESTIMATION_ATTENUATION        |                  0.9833 |              0.9500 |              0.0000 |            0.0000 |          0.0000 |            1.0000 |
| GLOBAL_INVARIANT              |                  0.9667 |              0.9667 |              0.0000 |            0.0000 |          0.0000 |            1.0000 |
| MECHANISM_FAMILY_MISMATCH     |                  0.0000 |              0.0000 |              0.0000 |            0.0000 |          1.0000 |            1.0000 |
| MICRO_GAUGE_ALIAS             |                  1.0000 |              1.0000 |              0.0000 |            0.0000 |          0.0000 |            1.0000 |

## Headline diagnostics

- Clean seam license: 0.9667.
- Clean relation fidelity q05 / relative error q95: 0.9932 / 0.1843.
- Covariance decomposition error q95: 1.839e-15.
- Primary population 95% coverage: 0.9427 (905/960); nested sensitivity 0.9479.
- Gauge output q95 / identity license / seam license: 6.003e-16 / 0.0000 / 1.0000.
- Attenuation correction win rate / median error reduction: 0.9667 / 0.6101.
- Cancellation detect / false global: 1.0000 / 0.0000.
- Ecological detect / false individual relation: 0.8500 / 0.0000.
- Mechanism mismatch detect / false seam license: 1.0000 / 0.0000.

## Gates

- `clean_end_to_end_recovery`: PASS
- `aggregation_commutation`: PASS
- `population_uncertainty_coverage`: PASS
- `gauge_alias_refusal`: PASS
- `attenuation_correction`: PASS
- `balanced_context_cancellation`: PASS
- `ecological_only_refusal`: FAIL
- `mechanism_family_mismatch_refusal`: PASS
- `independent_confirmation_agreement`: PASS
- `truth_isolation`: PASS

## Ruling

The licensed object is an observable event-to-relation procedure, not a unique hidden mechanism. A stable out-of-family periodic signal is reported as estimator-family mismatch rather than erased or relabelled as absence.

Claim boundary: Passing identifies, in registered synthetic worlds, an end-to-end observable procedure from event paths through a generator-blind replicated M3 quotient to a context-indexed HJIC relation field. It separates within-context, ecological, attenuation, gauge-alias, and mechanism-family failure modes. It does not identify a unique micro mechanism and does not establish personality meaning, human prevalence, causal interpretation, language invariance, diagnosis, or clinical validity.
