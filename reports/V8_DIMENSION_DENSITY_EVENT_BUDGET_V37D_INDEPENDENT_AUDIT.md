# V8 Dimension-Density-Event-Budget V3.7D Methodology Audit

Ruling: `PASS_WITH_CAVEATS`

This is an artifact- and method-level audit of the sealed confirmation. It is
not an external replication.

## Accepted

- The exploratory in-cohort result was correctly excluded after it exposed
  mean hard-AUC optimism of .098. The confirmation fits the reference router
  and denoising basis on 96 authors and scores disjoint authors.
- The registered outcomes are joint states, so the result does not infer
  bidirectional separation from unrelated marginal averages.
- The 32/96/192 author sets are nested within the same latent world, and
  rank-specific density effects are paired by repetition.
- The low-rank density effect is ordered and large:
  \(\Delta AUC_2=.288\), \(\Delta AUC_4=.104\),
  \(\Delta AUC_8=.022\).
- Random-neighbor AUC is stable across the density manipulation, while
  hard-neighbor AUC declines. This is consistent with local geometric
  crowding rather than generic measurement failure.
- The rank-12 reverse result has a direct capacity diagnosis: the rank-12
  sensitivity raises truth correlation from about .77 to .94 on the same
  observations and improves both Fisher-z correlation and NRMSE.
- All registered budget cells for rank at most 8 improve from 64 to 128
  events.
- The prospective seal, parent seal, provenance manifest, seed uniqueness,
  and artifact hashes pass. A separate same-seed run reproduced all numeric
  result files byte for byte.
- The rank-12 intervals in the frozen runner treat nested author-count rows
  as observations. A stricter repetition-clustered bootstrap was recomputed:
  Fisher-z gain `.713 [.703, .724]`, NRMSE gain
  `.292 [.288, .296]`, and oracle truth correlation
  `.940 [.938, .942]`. The gate remains unchanged.

## Caveats

### Synthetic operator geometry only

The simulator supplies categorical routing cells, known branch structure,
balanced opportunities, and a fixed reference design. It does not discover
events from raw tokens or show that the planted operator exists in human
text.

### Identification is a technical matching estimand

`identity` means same-author cross-session matching among a declared
candidate set. It is not legal identity, deanonymization ability,
psychological identity, or personality validity.

### The reverse separation is controlled misspecification

Rank 12 exceeds the frozen rank-8 estimator capacity by construction. This
cleanly proves that identity can survive incomplete structural recovery, but
does not show that an adaptively selected estimator will make the same error.
Unknown-rank selection remains open.

### Density is candidate-set density

Increasing authors makes hard negatives closer in the planted operator
space. This is an appropriate geometric stress test, but not a claim that a
particular real population has the same density law. Top-1 also necessarily
becomes stricter as the candidate set grows.

### Pairing is latent, not eventwise

Author-count conditions share the latent world and nested author prefixes,
but use independent event samples and independently fitted reference
routers. This avoids event reuse but adds sampling variation. The effect is a
paired latent-world contrast, not a common-random-number contrast.

### One signal-scaling regime

The confirmation fixes total author RMS across ranks. It does not confirm
fixed signal per latent dimension, anisotropic spectra, sparse operators, or
nonlinear manifolds. Those regimes may move or reshape the phase surfaces.

### Empirical gates are not universal probabilities

The .80/.50 thresholds and rates over 40 repetitions are operational frozen
gates. They are not population probability bounds, information-theoretic
limits, or clinical cutoffs.

### Scores remain reference dependent

The operator is measured relative to one fitted router and one synthetic
reference design. Fixed external norms, reference-population transport,
single-author uncertainty, and minimum detectable individual change remain
unresolved.

### Locator validity is inherited, not retested

V3.7D isolates operator geometry and uses known synthetic routing outcomes.
It does not rerun blind event localization. Real-text event discovery remains
separate from the phase result.

## Final ruling

The sealed confirmation supports a narrow but nontrivial theorem: under the
registered synthetic design, structural recovery and same-author
identification can each succeed while the other fails. The pass closes the
V3.7D confirmation question.

It does not close SUICA as a psychological measurement method. The next
technical target should be an adaptive-capacity, fixed-reference experiment
that estimates rank without true-rank access and tests whether the four-state
phase diagram survives reference-population shift. Human repeated-condition
data remain the later bridge from operator geometry to psychological meaning.
