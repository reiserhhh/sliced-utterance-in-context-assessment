# V8 Group-Free Routing Transport V3.7C Independent Audit

Decision: `PASS_WITH_CAVEATS`

## Accepted

- The five sealed V3.7C files and both parent seal hashes verified.
- Selection and confirmation used disjoint populations and event panels.
- The fitting API did not consume true group labels or a known group count.
- The external RNG audit covered streams omitted from the built-in audit and
  found no collision or pre-seal overlap.
- Core, transported-path, high-noise, MAR, negative-control, and
  nonidentifiability gates all passed without post-confirmation tuning.
- The 32-event arm provided a real finite-budget boundary rather than another
  uniformly easy success.
- Under the registered MAR mechanism, AIPW improved over available-case in all
  80 paired repetitions.

## Caveats

### Group-free does not mean label-free

The estimator does not use true author groups, but it still uses known
conditional cells, cue metadata, inferred incoming/outgoing branch labels, a
fixed four-branch dictionary, and an independently fitted reference router.
The claim is group-free conditional operator recovery, not unsupervised
discovery from raw text.

### Pooled success is not uniform identity resolution

The pooled hard-neighbor AUC passed, but the true-rank-2 subset had AUC `.777`
with bootstrap interval `[.769, .785]`, below the pooled `.80` gate. Its truth
correlation `.967` and split reliability `.797` remained high. V3.7C therefore
supports structure recovery across ranks, but not uniformly high individual
identification. The next experiment must model author density and margin
explicitly.

### Rank and shrinkage are working hyperparameters

Rank 8 minimized discovery log loss, while rank 6 had slightly higher
discovery reliability. These results support a compressible subspace, not an
exact latent dimension. Lambda `.3` was selected at the lower candidate
boundary. The frozen rule allowed this, but the optimum may be closer to zero;
the numerical lambda has no construct meaning.

### Transport remains bounded

The out-of-family arm adds asymmetry and secondary peaks, and the high-noise
arm weakens the registered signal. Both retain the same broad pause-cusp and
branch-direction grammar. Passing these arms is stronger than V3.7B's exact
match, but it is not arbitrary-trajectory or real-text event discovery.

### MNAR is not identified

The registered gamma grid includes the true synthetic mechanism. Coverage
`.919` was achieved with mean envelope width `.941`, using empirical
split-half widths rather than a derived single-author confidence model. This
demonstrates sensitivity-analysis behavior, not recovery under unknown MNAR.

### Scores remain reference-design dependent

Profiles are deviations from one fitted \(Q_{\rm ref}\), and pairing metrics
use cohort centering. V3.7C does not yet supply fixed external norms,
single-author uncertainty, or reference-population transport.

### Subspace recovery is in-cohort, not author-inductive

The cross-session denoiser uses paired halves from all authors to estimate its
stable basis, and V3.7C scores those same authors. This is legitimate for
describing the fitted cohort, but it is not evidence that the basis transports
to entirely new authors. V3.7D must fit the denoiser and reference router on
one author set and evaluate all recovery and identity metrics on disjoint
authors.

## Final ruling

V3.7C closes the principal synthetic corrections requested by the V3.7A/B
audits: group-oracle fitting, shared event panels, weak missingness stress,
conditional location error, and RNG reuse. It establishes a bounded
group-free conditional routing estimator.

Its most important result is not the pooled PASS. It is the empirical
separation among:

1. operator recovery;
2. repeated-measurement reliability;
3. local individual identifiability.

No psychological interpretation is licensed until a real repeated-text design
shows that an analogous operator exists and links to behavior or external
constructs.

## Required next experiment

Run a prospectively separated dimension-density-event-budget phase diagram.
Vary latent dimension, author density, event budget, session count, signal
scaling, and lower shrinkage values. Estimate both the recovery surface
\(N_{\rm recover}^*\) and the stricter identification surface
\(N_{\rm identify}^*\), reporting author margin \(m_u\), error
\(\epsilon_u\), and the frequency of \(2\epsilon_u<m_u\).
