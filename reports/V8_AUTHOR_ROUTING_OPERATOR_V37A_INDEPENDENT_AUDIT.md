# V8 Author Routing Operator V3.7A Independent Audit

Decision: `PASS_WITH_MAJOR_CAVEATS`

## Integrity

- The five sealed implementation files matched their recorded SHA-256 hashes.
- The pre-seal evidence and canonical result artifacts matched their hashes.
- Pre-seal and canonical seed blocks did not overlap.
- The canonical run manifest and seven-file artifact inventory passed.
- No confirmation tuning or personality-label access was found.

## Accepted

- The estimator did not receive the planted author basis.
- A fresh Haar basis was generated in each population.
- Author links and true group labels opened only in scoring.
- The low-rank primary world recovered a stable author-relative operator:
  truth correlation 0.862, split-session reliability 0.650,
  unseen-context reliability 0.824, and within-group AUC 0.963.
- Group-only and unstable-session controls correctly failed the author claim.

## Major caveats

### Invalid variance-component interpretation

The implementation computes component energies by subtracting estimated
finite-sample noise. This is not the PSD cross-session covariance estimator
described by the frozen plan and does not constrain shares to the simplex.
Local verification found negative shares in 184/200 stable populations and
184/200 random populations, plus shares above one in 116/200 random
populations. The registered maximum-error gate cannot rescue an estimator
whose output is not a valid variance decomposition.

### Empirical interval, not formal confidence interval

The interval combines a projected profile standard error with the magnitude
of the projection residual. No probability model shows that the resulting
quantity is a standard error. Empirical coverage was 0.942, but the median
interval width was 0.966 and there was no precision/refusal gate. It must be
reported as an empirical uncertainty band.

### Limited label firewall

The fitting path did not consume true author or group labels. It did consume
the registered number of mixture components, and scorer-only truth
correlation and reliability used true groups for centering. This supports
oracle-group-controlled evaluation, not a fully label-free deployment
estimand.

### Budget threshold, not information limit

At the low full-rank budget, reliability was 0.380 and the registered author
claim failed. However, truth correlation remained 0.694, within-group AUC
0.960, and numerical estimates were returned. The result demonstrates a
registered reliability threshold crossing, not an information-theoretic
limit or literal estimator refusal.

### Compressibility, not exact rank identification

Rank 6 and rank 8 differed by only 0.00025 held-out log-loss units. The
experiment supports a low-rank compressible operator family, but not precise
recovery of the latent dimensionality.

## Narrow final ruling

V3.7A establishes synthetic low-rank operator recovery under the registered
four-group design. Variance-source attribution, formal single-author
intervals, group-free recovery, and an information-theoretic sample limit
remain open.
