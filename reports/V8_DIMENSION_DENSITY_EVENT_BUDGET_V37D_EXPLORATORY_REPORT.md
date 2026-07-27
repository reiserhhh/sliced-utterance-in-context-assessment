# V8 Dimension-Density-Event-Budget V3.7D Exploratory Report

Decision: `EXPLORATORY_PASS / CONFIRMATION_REQUIRED`

## Correction discovered during exploration

The first phase diagram fitted the cross-session denoising basis and scored
the same authors. Compared with a disjoint-author analysis, this raised
hard-neighbor AUC by 0.098 on average and by 0.184 at 16 events. Mean truth
correlation changed by only -0.011. The in-cohort artifact is therefore
excluded:

`results/v8_dimension_density_budget/v37d_exploratory_20260726`

The corrected analysis fits the reference router and stable basis on 96
training authors, then scores 32, 96, or 192 entirely new authors.

## Corrected design

- latent ranks: 2, 4, 8, 12;
- evaluation authors: 32, 96, 192;
- event budgets: 16, 32, 64, 128 per context-session;
- fixed-total and fixed-per-latent-dimension signal regimes;
- eight independent populations per cell;
- 768 total corrected populations;
- fixed V3.7C working estimator rank 8;
- true-rank projection used only as a scorer sensitivity.

## Main results at 128 events, fixed total signal

| Rank | Authors | Truth r | Split rel. | Hard AUC | Top-1 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 32 | .980 | .887 | .883 | .293 |
| 2 | 96 | .973 | .873 | .707 | .141 |
| 2 | 192 | .978 | .887 | .607 | .079 |
| 4 | 32 | .966 | .873 | .968 | .727 |
| 4 | 96 | .976 | .859 | .927 | .538 |
| 4 | 192 | .969 | .855 | .863 | .406 |
| 8 | 32 | .953 | .849 | .996 | .906 |
| 8 | 96 | .947 | .829 | .974 | .823 |
| 8 | 192 | .957 | .849 | .970 | .773 |
| 12 | 32 | .791 | .800 | .984 | .855 |
| 12 | 96 | .779 | .808 | .964 | .741 |
| 12 | 192 | .775 | .793 | .938 | .630 |

## Two crossing phase boundaries

Rank 2 shows **recovery without identification**. Truth correlation stays
above .97 while local identity declines sharply as author count increases.
Changing from the fixed rank-8 projection to the true rank-2 projection
changes AUC by only about -.004 on average, so this is geometric crowding,
not rank mismatch.

Rank 12 shows **identification without full recovery**. The fixed rank-8
estimator retains enough stable coordinates for AUC above .93, but truncates
the full operator and leaves truth correlation near .78. The scorer-only
rank-12 projection restores truth correlation to about .94.

Therefore recovery and identification are not nested validity levels. Their
critical surfaces can cross:

\[
N_{\rm recover}^{*}
\not\equiv
N_{\rm identify}^{*}.
\]

## Density and budget

At 128 events, increasing evaluation authors from 32 to 192 barely changes
rank-2 truth correlation (-.002) but lowers hard AUC by .276 and top-1 by
.214. Across all 768 populations, packing load correlates negatively with
hard AUC (\(\rho=-.441\)); relative nearest-neighbor margin correlates
positively (\(\rho=.432\)).

After author holdout, average performance rises monotonically with event
budget. Under fixed-total signal, 16 to 128 events changes:

- truth correlation: .412 to .920;
- split reliability: .254 to .847;
- hard AUC: .589 to .898;
- top-1: .047 to .576.

## Margin diagnostics

The normalized prototype-margin diagnostic tracks identity, but the strict
cross-session triangle-inequality certificate is nearly always zero (maximum
.012). It is a valid sufficient bound but too conservative to be an
operational gate and should remain descriptive.

## Interpretation boundary

The corrected experiment supports a synthetic author-inductive separation
among operator recovery, reliability, and identity resolution. It does not
establish personality, real-text factors, clinical assessment, or universal
sample-size thresholds.

## Next gate

Freeze a fresh-seed confirmation on the 64/128-event boundary cells with 40
populations per cell. No exploratory population may enter that confirmation.
