# V8 Dimension-Density-Budget V3.7D Confirmation

Status: `PROSPECTIVELY_SEALED_BEFORE_CONFIRMATION`

## Registered question

Can operator recovery and author identification be separated in both
directions on entirely new authors?

\[
R=\mathbf 1(r_{\rm truth}\ge .80,\ R_{\rm split}\ge .50),
\]

\[
I=\mathbf 1(\mathrm{AUC}_{\rm hard}\ge .80,\ \mathrm{Top1}\ge .50).
\]

The primary outcomes are the joint events \(R=1,I=0\) and \(R=0,I=1\),
not separate marginal pass rates.

## Paired design

Each of 40 fresh repetitions generates one group-free 288-author world:

- 96 authors fit the fixed reference router and cross-session stable basis;
- 192 disjoint authors form the maximum evaluation pool;
- 32- and 96-author evaluations are nested preregistered random prefixes of
  that pool;
- ranks 2/4/8/12 use nested columns of one rank-12 latent basis;
- 64- and 128-event panels share latent probabilities but use independent
  `SeedSequence` event streams.

The primary estimator rank remains frozen at 8. The true-rank estimator is a
post-primary capacity sensitivity only.

## Frozen gates

1. At rank 2 and 128 events, at least 80% of repetitions jointly show
   recovery without identity for both 96 and 192 authors.
2. The paired rank-2 hard-AUC difference between 32 and 192 authors has mean
   at least .20 and bootstrap 95% lower bound above zero.
3. The density drop is dimension-dependent:
   \(\Delta AUC_2>\Delta AUC_4>\Delta AUC_8\), and
   \(\Delta AUC_2-\Delta AUC_8\) has a lower bound above zero.
4. Random-neighbor AUC changes by at most .05 between 32 and 192 authors.
5. At rank 8 and 128 events, at least 75% of repetitions jointly recover and
   identify for every author count.
6. At rank 12 and 128 events, at least 75% jointly identify without complete
   recovery for every author count.
7. On the exact same rank-12 events, the oracle-rank estimator has mean truth
   correlation at least .90, positive paired Fisher-z improvement, and
   positive paired NRMSE improvement, both with 95% lower bounds above zero.
8. For ranks at most 8, the within-repetition mean Fisher-z improvement from
   64 to 128 events has a lower bound above zero, with at least 8/9 cells
   positive.
9. All training/evaluation author sets, event streams, parent hashes, numeric
   outputs, and artifact inventories pass.

Rates are empirical reproducibility gates, not lower confidence bounds on
population probabilities.

## Licensed theorem boundary

A pass permits only the statement that, in this synthetic paired design,
operator recovery and identity resolution are bidirectionally separable.
Psychological, real-text, causal, and clinical interpretations remain closed.
