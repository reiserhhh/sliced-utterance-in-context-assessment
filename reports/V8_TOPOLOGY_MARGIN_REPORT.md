# SUICA V8 C2 Topology-Margin Report

Status: `V8_C2_TOPOLOGY_MARGIN_PLANTED_PASS`
Scope: planted stable C2 response-operator populations only
Final run: `results/v8_topology_margin/v11_final_20260729`

## 1. Question

The preceding vanishing-individuality experiment showed that ordinary
same-author matching can be generated entirely by group membership. It did
not determine whether the stable population geometry was:

- a finite separated mixture;
- a continuous closed manifold;
- a continuous open manifold; or
- too weak, unstable, or confounded to identify.

This experiment therefore treats author matching and population topology as
different estimands. It asks whether a calibrated, open-set procedure can
recover a planted topology when evidence is sufficient and explicitly refuse
when it is not.

## 2. Planted observation model

Each author has a latent three-dimensional coordinate \(x_u\), embedded in a
15-dimensional response-operator space. Two text halves and two observers
produce four views:

\[
X_{uhm}
=
\sqrt{\rho}\,x_u
+
\sqrt{1-\rho}
\left(
  \sqrt{\omega}\,\xi_{uh}
  +
  \sqrt{1-\omega}\,\nu_{uhm}
\right),
\]

where \(\xi_{uh}\) is half-specific noise, \(\nu_{uhm}\) is observer-specific
noise, \(\omega=0.5\), and
\(\rho=(1+\text{noise ratio})^{-1}\). Discovery, calibration, and
confirmation authors are disjoint.

The planted worlds are four separated groups, a continuous ring, a continuous
open curve, an overlapping mixture, Gaussian and heavy-tailed controls,
half-shuffled and observer-specific attacks, a distribution-matching failure,
and a pearls-on-string bridge continuum. These are technical geometries, not
simulated personality types.

## 3. Estimator

1. Fit a three-dimensional stable PCA/whitening projection on discovery
   authors only.
2. Average the four projected views to estimate the population cloud.
3. Convert Euclidean distances to ordinal dissimilarities:

   \[
   d^\star_{ij}=\widehat F_D(d_{ij}).
   \]

   This equalizes the empirical pairwise-distance distribution while
   preserving filtration order, preventing success from scalar distance
   scale alone.
4. Compute exact H0 persistence on all authors and H1 Vietoris-Rips
   persistence on 64 density-representative K-means medoids.
5. Combine persistence with k-nearest-neighbor Laplacian, conductance,
   density-tree, HDBSCAN, silhouette, and local-linearity diagnostics.
6. Require topology persistence across half-averaged and observer-averaged
   views.
7. Apply sample-size-specific thresholds calibrated without confirmation
   labels. Ambiguous evidence returns `TOPOLOGY_NOT_IDENTIFIABLE`.

The H1 rule is deliberately open-set:

\[
U_C=Q_{.99}(H_1\mid\text{curve}),\qquad
L_R=\max\{Q_{.99}(H_1\mid\text{controls}),
          Q_{.01}(H_1\mid\text{ring})\}.
\]

Values \(H_1\le U_C\) may support an open curve, values \(H_1\ge L_R\) may
support a ring, and the interval \((U_C,L_R)\) forces refusal.

## 4. Why V1 stopped

V1 passed the \(N=320\) power and ambiguity checks but failed the registered
\(N=640\) and wrong-decisive gates:

- minimum \(N=640\) clear-world accuracy: 0.880;
- maximum one-sided 95% upper bound for wrong decisive calls: 0.0645;
- null claim upper bound: 0.0060.

The error was concentrated in ring-to-curve calls. The audit also showed that
an absolute author-AUC requirement was invalid for this estimand: it can reject
a topologically clear population merely because individual matching is below
an unrelated threshold. V1 was therefore retained as `STOP`.

Before V1.1 confirmation, the procedure was changed to keep author AUC as a
diagnostic, introduce an H1 grey refusal interval, remove K=4 silhouette as a
necessary ring condition, calibrate thresholds separately by sample size,
require non-empty invariance eligibility, and use a new seed block.

## 5. V1.1 confirmation

### Clear planted worlds

| Confirmation N | Separated mixture | Ring | Open curve | Minimum |
| ---: | ---: | ---: | ---: | ---: |
| 320 | 0.970 | 0.910 | 0.894 | 0.894 |
| 640 | 1.000 | 0.988 | 0.926 | 0.926 |

Each cell used 500 repetitions. Across these primary clear worlds there were
zero wrong decisive class calls; failures were refusals.

### Ambiguous and adversarial worlds

At both \(N=320\) and \(N=640\), the overlapping mixture, Gaussian null,
heavy-tailed control, half shuffle, observer-specific world, and
distribution-matching failure were refused in 100% of 500 repetitions.

- minimum ambiguous-world refusal: 1.000;
- maximum primary wrong-decisive one-sided 95% upper bound: 0.00597;
- maximum primary null-claim one-sided 95% upper bound: 0.00597.

### H1 open-set separation

| Confirmation N | Curve ceiling \(U_C\) | Ring floor \(L_R\) | Refusal gap |
| ---: | ---: | ---: | ---: |
| 80 | 0.0758 | 0.2038 | 0.1280 |
| 160 | 0.0874 | 0.2332 | 0.1458 |
| 320 | 0.0631 | 0.2644 | 0.2014 |
| 640 | 0.0500 | 0.2840 | 0.2340 |

All four calibration sizes have a positive ring/curve gap.

### Invariance

The rule was attacked with coordinate permutation and invertible affine
changes before the discovery projection.

| Confirmation N | Baseline eligible | Conditional invariance |
| ---: | ---: | ---: |
| 320 | 0.924 | 0.974 |
| 640 | 0.969 | 0.982 |

These are conditional rates among baseline-identifiable repetitions, not an
unconditional claim that every transformed sample is identifiable. Counting
all repetitions, agreement was 0.958 at N=320 and 0.964 at N=640. The
registered attack applies a full-rank affine transformation, refits the
discovery-only whitening, and then tests coordinate permutation. It therefore
establishes invariance after canonicalization, not raw-coordinate invariance.

## 6. Identification boundary

The sensitivity analysis supplies the most important limitation:

- at \(N=80\), clear-world accuracy was only 0.467-0.653;
- at \(N=160\), it was 0.793-0.893;
- gap ratios 1 and 2 were always refused, while gap 4 was recovered at 0.967;
- gap 6 fell to 0.880, so the decision rule is not monotone in separation;
- increasing the noise ratio from 0.10 to 0.25 caused all three clear worlds
  to be refused in every repetition;
- pearls-on-string worlds with fewer than 20 bridge authors were correctly
  forced to refuse;
- even with bridge mass 0.10 or 0.20, ring recovery was only 0.313 and 0.487.

The method therefore has a calibrated local identification region, not a
universal topology guarantee. Its favorable property is conservative
failure: outside the registered margin it usually refuses rather than
inventing a class. Low-N sensitivity runs also show non-zero false decisive
rates and are not covered by the primary \(N\ge320\) claim. The N=640 curve
point estimate of 0.926 passes its registered point-estimate gate, but its
Wilson 95% lower bound is approximately 0.900 and does not support the stronger
claim that population accuracy has been proven above 0.90 at 95% confidence.

The ordinal transform preserves filtration order but changes the scale:
persistence lifetimes are properties of the empirical rank-distance
filtration, not original Euclidean distances. Primary confirmation uses a new
seed block relative to V1. Some sensitivity cases reuse seed indices within
V1.1 and must be read as boundary diagnostics rather than independent
replication.

Absolute author AUC is not a topology threshold. Distribution matching still
includes a discovery-to-confirmation AUC-gap check alongside mean and
covariance checks, so author matching is not absent from all refusal logic.
The calibrated `minimum_author_matching_auc` field is retained in the artifact
for audit compatibility but is not consumed by the V1.1 classifier.

## 7. Scientific interpretation

V1.1 resolves the narrow technical question left open by the
vanishing-individuality experiment:

> Under a planted stable C2 response-operator model, sufficient sample size,
> low observation noise, and registered topology margins, discrete groups,
> a continuous ring, and a continuous open curve can be distinguished after
> equalizing the scalar distance distribution. Weak, confounded, unstable, or
> intermediate cases can be refused explicitly.

This supports three methodological conclusions:

1. population topology and individual identity are separate estimands;
2. stable author geometry need not be forced into a finite type system; and
3. an unknown dynamic coordinate may be characterized first by its invariants,
   neighborhood structure, persistence, and response geometry before any
   semantic or psychological naming.

It does **not** show that real authors form these topologies. It does not
identify personality factors, emotion, state, diagnosis, clinical utility, or
the psychological meaning of a dynamic axis. Those require real fixed-
condition repeated data, independent observer validation, and external
behavioral or construct links.

## 8. Decision

`V8_C2_TOPOLOGY_MARGIN_PLANTED_PASS`

This closes the planted mathematical identifiability subproblem. The next
scientific gate is not more threshold tuning on these simulated worlds. It is
to apply the frozen open-set procedure to eligible real C2 coordinates and
allow `TOPOLOGY_NOT_IDENTIFIABLE` as a valid outcome.

## 9. Reproducibility artifacts

- Configuration: `configs/v8_topology_margin_v11.json`
- Runner: `scripts/run_suica_v8_topology_margin.py`
- Core: `suica_core/v8_topology_margin.py`
- Unit tests: `tests/test_v8_topology_margin.py`
- Final decision:
  `results/v8_topology_margin/v11_final_20260729/decision.json`
- Primary seed metrics:
  `results/v8_topology_margin/v11_final_20260729/primary_seed_metrics.csv`
- Sensitivity metrics:
  `results/v8_topology_margin/v11_final_20260729/sensitivity_seed_metrics.csv`
- Thresholds, run manifest, and artifact inventory are stored in the same
  final result directory.
- Independent audit: `reports/V8_TOPOLOGY_MARGIN_INDEPENDENT_AUDIT.md`
