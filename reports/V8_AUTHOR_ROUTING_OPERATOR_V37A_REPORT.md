# V8 Author Routing Operator V3.7A Report

Canonical engine decision: `V8_AUTHOR_ROUTING_OPERATOR_V37A_PASS`

Independent methodology decision: `PASS_WITH_MAJOR_CAVEATS`

Scientific promotion:
`SYNTHETIC_LOW_RANK_OPERATOR_RECOVERY_PASS__INFERENCE_COMPONENTS_OPEN`

## Question

V3.7A tested whether an anonymous author's conditional routing probabilities
contain a stable, recoverable deviation after shared context and planted group
structure are controlled. The primary world used a fresh hidden rank-6 Haar
subspace in every population. The estimator did not receive the planted basis
or author identity links during fitting.

The estimated object was

\[
D_u
=
\operatorname{ilr}(\Pi_u^Q)
-
\operatorname{ilr}(\Pi_{\mathrm{reference}}^Q),
\]

where all authors were integrated over one frozen reference design \(Q\).

## Canonical evidence

The canonical seed was `20310429`; 200 independent confirmation populations
were evaluated after the internal content seal.

| Metric | Mean | 95% interval |
| --- | ---: | ---: |
| Truth correlation | 0.8621 | [0.8596, 0.8646] |
| Probability RMSE | 0.0415 | [0.0412, 0.0419] |
| Independent split-session reliability | 0.6495 | [0.6462, 0.6527] |
| Unseen-context reliability | 0.8243 | [0.8218, 0.8268] |
| Same-author AUC | 0.9863 | [0.9854, 0.9871] |
| Within-group same-author AUC | 0.9626 | [0.9607, 0.9643] |
| Within-group top-1 | 0.7507 | [0.7439, 0.7574] |
| Held-out log-loss gain | 0.0523 | [0.0520, 0.0526] |
| ECE | 0.0095 | [0.0091, 0.0099] |
| Stable author claim | 193/200 | lower bound 0.9353 |

Calibration selected rank 6 and ridge penalty 3. Rank 8 was nearly tied:
held-out log loss was 1.28250 for rank 6 and 1.28275 for rank 8. The evidence
therefore supports a low-dimensional compressible structure, not exact
identification of true rank 6.

## Controls and capacity boundary

- The group-only world had ordinary same-author AUC 0.8478 but within-group
  AUC 0.5004 and zero author claims. This confirms that ordinary matching can
  be driven by group membership.
- The session-unstable world had split-session reliability -0.0148 and zero
  claims.
- Registered context, opportunity, cue-leakage, random, and non-overlap
  controls did not promote stable author structure.
- Full-rank 48D recovery at 128 events per context-session reached truth
  correlation 0.8844 and reliability 0.6324.
- The same 48D world at 32 events retained truth correlation 0.6940 and
  within-group AUC 0.9598, but reliability fell to 0.3800 and the registered
  author claim did not open.
- A rank-2 world was recoverable by the selected low-rank family. A rank-12
  world produced only 2/200 claims, marking a capacity boundary for this
  design.

The 32-versus-128 event contrast is an empirical budget/reliability boundary.
It is not an information-theoretic impossibility result.

## Independent audit corrections

The canonical engine passed all registered gates, but three inferential
subclaims are not accepted:

1. The variance-share routine is not a valid nonnegative variance-component
   estimator. It directly subtracts finite-sample noise energy. Negative
   estimated shares occurred in 184/200 stable populations and 184/200 random
   populations; 116/200 random populations also produced a share above one.
   The registered variance-share gate is therefore retired as evidence.
2. The reported operator interval is an empirical uncertainty band. It adds
   the absolute projection residual to a standard-error term without a
   derived sampling law. Its 0.942 coverage is descriptive, not a calibrated
   95% confidence interval; the median width was 0.966.
3. The estimator did not use true group labels, but it was told that four
   mixture components existed. Truth correlation and within-group metrics
   opened true groups in the scorer. The current result is therefore recovery
   under a registered four-group synthetic design, not fully group-free
   measurement.

The internal SHA-256 seal, run manifest, and artifact inventory all verify.
The seal is not an external immutable preregistration because the worktree was
dirty and the sealed files were initially untracked.

## Supported conclusion

In the registered four-group synthetic DGP, an anonymous author's hidden
low-rank routing-probability deviation is recoverable across independent
sessions and unseen in-domain contexts. The result survives group-only,
session-instability, opportunity, cue-leakage, random, and non-overlap
controls.

The result does not establish a personality dimension, thought process,
intelligence parameter, clinical measurement, arbitrary 48D recovery,
formal single-author confidence interval, valid variance decomposition, or
real-text localization.

## Next gates

1. Replace known-\(K\) and scorer-only true-group centering with a group-free
   estimand and sensitivity analysis over discovered \(K\).
2. Replace direct variance subtraction with a constrained PSD random-effects
   or hierarchical covariance estimator.
3. Derive or simulate-calibrate single-author uncertainty with a width and
   refusal gate.
4. Test blind event localization separately before any real-text claim.
