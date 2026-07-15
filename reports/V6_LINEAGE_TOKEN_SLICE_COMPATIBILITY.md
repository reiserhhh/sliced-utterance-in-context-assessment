# SUICA V6 Lineage Token-Slice Compatibility

## Scope

This is a token-slice replication of the historical PRED-1 estimand, not an
event-disjoint or temporal-dynamics result. It uses no external labels and
persists no raw text.

- source comments after personality-report guard: `1,466,085`
- confirmation candidates before span/token support: `1,212`
- complete paired authors: `584`
- fixed/mixed median span ratio: `0.886`
- fixed/mixed vector same-author AUC: `0.7023` / `0.6383`

## Frozen construct contrast

**Relation:** `UPHELD_LEGACY_TOKEN_ESTIMAND`.

| construct             |   n_authors |   r_fixed |   r_mixed |   delta |   ci_lo |   ci_hi |   bootstrap_finite_fraction |
|:----------------------|------------:|----------:|----------:|--------:|--------:|--------:|----------------------------:|
| first_person_usage_v2 |         584 |    0.8205 |    0.7371 |  0.0834 |  0.0457 |  0.127  |                           1 |
| directive_action_v2   |         584 |    0.6371 |    0.351  |  0.2861 |  0.1959 |  0.3663 |                           1 |
| novelty_play_v2       |         584 |    0.5062 |    0.3378 |  0.1684 |  0.0644 |  0.2653 |                           1 |
| tension_core_v2       |         584 |    0.2948 |    0.1847 |  0.1101 |  0.0015 |  0.2128 |                           1 |

## Interpretation

The token-slice result is compared only with the historical PRED-1 claim. It
cannot validate or invalidate V6's event-level joint-process geometry or the
J3 ordered-transition refusal. `tension_core_v2` is descriptive and is not
part of the historical three-construct criterion.
