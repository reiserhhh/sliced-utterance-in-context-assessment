# C2 purity decomposition v1 (Tier-U, label-free)

| construct             |   rho_raw |   rho_shared_matched |   rho_cond_disjoint |   rho_class_disjoint |   c1_share | ci             |   mix_share_cov |   mediated_total | verdict                | H(M)_low>high   |
|:----------------------|----------:|---------------------:|--------------------:|---------------------:|-----------:|:---------------|----------------:|-----------------:|:-----------------------|:----------------|
| first_person_usage_v2 |     0.683 |                0.48  |               0.346 |                0.268 |      0.279 | [0.208, 0.349] |           0.305 |            0.398 | partial_mediation      | False           |
| directive_action_v2   |     0.409 |                0.212 |               0.112 |                0.1   |      0.471 | [0.226, 0.662] |           0.402 |            0.229 | relabel_C1C2_composite | True            |
| tension_core_v2       |     0.316 |                0.09  |               0.081 |                0.053 |    nan     | [0.0, 0.551]   |           0.398 |            0     | undetermined           | True            |
| novelty_play_v2       |     0.382 |                0.261 |               0.108 |                0.033 |      0.587 | [0.428, 0.723] |           0.911 |            0.588 | relabel_C1C2_composite | True            |
| adversity_recovery_v2 |     0.129 |                0.007 |               0.016 |                0.028 |    nan     | [None, None]   |           1     |            0     | undetermined           | False           |

See docstring for estimand definitions and the pre-committed interpretation rule; estimators licensed by wrong-world suite W-B/W-B2.

Round-9 note: estimators licensed by W-B/W-B2/W-B2c/W-B3 (class-disjoint licensed by W-B2c; mediated_total = UPPER bound on mediation under coupling). Flesh shares are BANDS per the F6.3 alarm (first_person ~0.56-0.72); interpretation rule revision history in FALSIFIER_MATRIX. Full corrections: ledger C2-PURITY row.
