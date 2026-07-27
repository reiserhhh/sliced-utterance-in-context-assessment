# SUICA V8 Vanishing-Individuality Experiment

## Decision

`V8_EPSILON_HIERARCHY_CORE_PASS_GEOMETRY_UNRESOLVED`

The hierarchical limit model passed every registered core check. The
experiment validates separation of group-level, individual-level, unstable,
choice-only, and observer-specific planted structure. It does not yet identify
whether a stable group-level geometry is intrinsically discrete or continuous.

No psychological, personality, emotion, diagnostic, or clinical construct was
used or validated.

## Hypothesis

The author-specific C2 operator was decomposed as

\[
B_u=B_0+G_{k(u)}+\varepsilon D_u,
\]

where \(G_{k(u)}\) is a shared group operator, \(D_u\) is a zero-mean
within-group individual deviation, and \(\varepsilon\) controls the magnitude
of individuality.

Under independent half-specific measurement error,

\[
C_{\mathrm{stable}}
=
\Sigma_G+\varepsilon^2\Sigma_D.
\]

After subtracting discovery-only group centers,

\[
C_{\mathrm{residual}}
=
\varepsilon^2\Sigma_D
\longrightarrow 0
\quad\text{as}\quad
\varepsilon\longrightarrow0.
\]

This predicts that ordinary author matching may remain high at
\(\varepsilon=0\) because it mixes within-group and between-group negatives.
Only author matching against strangers from the same group isolates
individual-level structure.

## Design

- 500 independent repetitions;
- 60 discovery, 20 calibration, and 80 confirmation authors;
- four balanced planted groups;
- eight shared factorial conditions and five behavior families;
- two independent halves;
- six fixed observations per author-condition-family-half;
- 999 group-preserving pairing permutations;
- discovery-only scaling, calibration-only ridge selection, and a single
  confirmation opening.

The battery included null, group-only, individual-only, joint, six
\(\varepsilon\) levels, continuous-manifold, C1-group-confound,
observer-artifact, and half-unstable worlds.

## Main Separation Result

| Planted world | Author-all AUC | Author-within-group AUC | Group AUC |
| --- | ---: | ---: | ---: |
| Null | 0.4998 | 0.4997 | 0.5001 |
| Group only | 0.8644 | 0.5001 | 0.9800 |
| Individual only | 0.8610 | 0.8657 | 0.4889 |
| Joint | 0.9470 | 0.8065 | 0.9389 |
| Half-unstable | 0.5008 | 0.5011 | 0.4995 |

The group-only result is the central finding. Ordinary author AUC remained
0.864 even though the planted individual deviation was exactly zero.
Within-group author AUC returned to 0.500. Therefore a high ordinary author
AUC can be produced entirely by group membership and is not, by itself,
evidence of individual differences.

## Epsilon Limit

| Epsilon | Within-group AUC | Pairing power | Estimated residual energy | Oracle residual energy |
| ---: | ---: | ---: | ---: | ---: |
| 0.00 | 0.5006 | 0.006 | 0.396 | 0.000 |
| 0.05 | 0.5061 | 0.026 | 0.181 | 0.075 |
| 0.10 | 0.5216 | 0.080 | 0.303 | 0.299 |
| 0.25 | 0.6073 | 0.976 | 1.060 | 1.860 |
| 0.50 | 0.8083 | 1.000 | 3.864 | 7.456 |
| 1.00 | 0.9808 | 1.000 | 14.522 | 29.814 |

The oracle residual followed

\[
C_{\mathrm{residual}}\propto\varepsilon^{1.9995}
\]

with \(R^2=0.999999\), matching the theoretical square law. The finite-sample
score followed \(\varepsilon^{1.6867}\), \(R^2=0.9930\). Ridge shrinkage,
binomial sampling, and a nonzero estimation-noise floor compress the measured
exponent without changing the monotonic law.

The registered minimum detectable individuality was
\(\varepsilon_*=0.50\). At \(\varepsilon=0.25\), the pairing test had high
power but within-group AUC was only 0.607, below the measurement-strength
gate. Values below the detection boundary must be reported as
`INDIVIDUAL_STRUCTURE_BELOW_DETECTION_LIMIT`, not as zero individuality.

## What the Residual Becomes

At \(\varepsilon=0\), estimated residual energy remained nonzero even though
the oracle individual residual was exactly zero. Its within-group AUC and
type-I rate were null. The remaining magnitude is therefore finite-sample
estimation dispersion, not stable author structure.

The correct distinction is:

- stable cross-half covariance above the registered null: recoverable
  individual structure;
- broad single-half residual without cross-half persistence: unstable
  variation or measurement error;
- stable ordinary author matching but null within-group matching: group-only
  structure;
- stable within one observer but null across observers: observer fingerprint.

The observer-artifact world made the last point explicit: primary
within-group AUC was 0.8673, but cross-observer AUC was 0.4989.

## C1 and C2

When group membership affected only context selection, C1 group AUC reached
0.9931 while C2 group AUC remained 0.5001. A group relation in selected
contexts therefore does not imply a group relation in response under fixed
conditions.

## Discrete Versus Continuous Geometry

The planted discrete group world was easily clustered
(confirmation ARI 0.987). The continuous-manifold world preserved its
distance geometry (Spearman 0.877) and favored local-manifold prediction by
0.060 normalized MSE.

However, in the discrete world the mixture predictor beat the local-manifold
predictor by only 0.017, below the registered 0.05 materiality margin.
Flexible local predictors can approximate discrete groups, so predictive
accuracy alone cannot identify topology.

The valid conclusion is:

> Stable group-level geometry is identifiable, but its discrete or continuous
> topology is not identified by the current predictive comparison.

## Consequences for SUICA

1. Every future author-similarity result must report author-all,
   author-within-group or local-neighborhood, and group-level comparisons.
2. Residual magnitude alone is not evidence. Stable cross-half covariance is
   the primary residual object.
3. Cross-observer persistence is necessary before stable behavior structure
   can be separated from observer fingerprint.
4. Cluster stability does not license a psychological type interpretation.
5. Low-amplitude individual structure requires an explicit detection-limit
   statement.
6. C1 choice groups and C2 response groups remain distinct estimands.

## Next Mathematical Gate

The next proposed battery is `V8_C2_TOPOLOGY_MARGIN_PLANTED_V1`. It should
match mean, covariance, and AUC across separated mixtures, continuous
manifolds, low-density bridges, and overlapping mixtures, then test topology
with persistent homology, graph conductance, Laplacian eigengaps, density
cluster trees, and cross-half/cross-observer barcode stability.

## Artifacts

- `results/v8_vanishing_individuality/v1_final_20260725/decision.json`
- `results/v8_vanishing_individuality/v1_final_20260725/world_summary.csv`
- `results/v8_vanishing_individuality/v1_final_20260725/seed_metrics.csv`
- `results/v8_vanishing_individuality/v1_final_20260725/report.md`
- `results/v8_vanishing_individuality/v1_final_20260725/run_manifest.json`

