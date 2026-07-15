# SUICA V6 Nuisance-Alpha Sensitivity Audit

## Scope

This is a predeclared scorer-perturbation audit. The source representation is
fit once on discovery authors. The nuisance residualization is then rebuilt at
Ridge alpha `(1.0, 10.0, 100.0)`; each resulting static configuration is standardized
against its own discovery reference. Same-half cross-alpha geometry is compared
under a row-linkage permutation null. No alpha is selected as a winner.

## Frozen settings

- nuisance Ridge alphas: `(1.0, 10.0, 100.0)`
- tested comparisons: all pairwise alpha values in early and late halves
- confirmation rows per comparison: at most `128`
- linkage permutations: `99`
- familywise correction: Bonferroni across `24` tests
- source text, terms, author IDs, and external labels: not exported or inspected after mapping

## Scale diagnostics

|   nuisance_ridge_alpha |   mean_norm_early |   mean_norm_late |
|-----------------------:|------------------:|-----------------:|
|                 1.0000 |            4.7562 |           4.5744 |
|                10.0000 |            4.7563 |           4.5744 |
|               100.0000 |            4.7573 |           4.5741 |

## Results

| comparison                 |   n_users | status                                     |   linear_cka |   linear_cka_bonferroni_p |   rbf_cka |   rbf_cka_bonferroni_p |   distance_spearman |   distance_spearman_bonferroni_p |   neighbour_jaccard |   neighbour_jaccard_bonferroni_p |
|:---------------------------|----------:|:-------------------------------------------|-------------:|--------------------------:|----------:|-----------------------:|--------------------:|---------------------------------:|--------------------:|---------------------------------:|
| alpha_1__alpha_10__early   |       128 | NO_SCORER_PERTURBATION_ROBUSTNESS_DETECTED |       1.0000 |                    0.2400 |    1.0000 |                 0.2400 |              1.0000 |                           0.2400 |              0.9972 |                           0.2400 |
| alpha_1__alpha_10__late    |       128 | NO_SCORER_PERTURBATION_ROBUSTNESS_DETECTED |       1.0000 |                    0.2400 |    1.0000 |                 0.2400 |              1.0000 |                           0.2400 |              1.0000 |                           0.2400 |
| alpha_10__alpha_100__early |       128 | NO_SCORER_PERTURBATION_ROBUSTNESS_DETECTED |       1.0000 |                    0.2400 |    0.9999 |                 0.2400 |              0.9999 |                           0.2400 |              0.9844 |                           0.2400 |
| alpha_10__alpha_100__late  |       128 | NO_SCORER_PERTURBATION_ROBUSTNESS_DETECTED |       1.0000 |                    0.2400 |    1.0000 |                 0.2400 |              1.0000 |                           0.2400 |              0.9943 |                           0.2400 |
| alpha_1__alpha_100__early  |       128 | NO_SCORER_PERTURBATION_ROBUSTNESS_DETECTED |       0.9999 |                    0.2400 |    0.9999 |                 0.2400 |              0.9999 |                           0.2400 |              0.9815 |                           0.2400 |
| alpha_1__alpha_100__late   |       128 | NO_SCORER_PERTURBATION_ROBUSTNESS_DETECTED |       1.0000 |                    0.2400 |    1.0000 |                 0.2400 |              1.0000 |                           0.2400 |              0.9943 |                           0.2400 |

## Reading rule

Passing all four tests means the corresponding same-half relational geometry is
robust to this local residualization-strength perturbation. It does not mean
the nuisance model is causal, complete, or optimized, and it cannot establish
cross-time or cross-context stability.
