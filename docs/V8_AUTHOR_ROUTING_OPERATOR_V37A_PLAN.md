# V8 Author-Specific Routing Operator V3.7A

Status: `PROSPECTIVELY_SEALED_BEFORE_CONFIRMATION`

Seal: `configs/v8_author_routing_operator_v37a_seal.json`

## 1. Estimand

V3.7A asks whether a stochastic routing-probability deviation can be recovered
for an anonymous author packet and remain stable in unseen contexts:

\[
P(Y=k\mid u,c,s,i,q)
=
\operatorname{softmax}_k
\left[
S_{iqk}
+C_{iqk}^{\mathsf T}\phi(z_c)
+G_{g(u),iqk}
+A_{u,iqk}
+E_{us,iqk}
\right].
\]

Every logit block sums to zero over outgoing branch \(k\). Group effects sum to
zero across groups, author effects sum to zero within group, context
descriptors are centered, and session deviations have zero mean across the two
sessions.

The measurement object is not a fitted author classifier. It is the
probability-simplex deviation under one frozen uniform reference design:

\[
D_u
=
\operatorname{ilr}(\Pi_u^Q)
-\operatorname{ilr}(\Pi_{\mathrm{reference}}^Q).
\]

## 2. Identifiability correction

The first pre-seal diagnostic used an unstructured 48-dimensional author
operator with 32 events per context-session. It produced strong matching but
only about 0.51 truth correlation and 0.52 split-session reliability after
regularized probability estimation. The data could recognize authors but
could not recover all 48 coordinates precisely.

V3.7A therefore separates three arms:

| Arm | True author structure | Events/context/session | Role |
| --- | --- | ---: | --- |
| LR6 | hidden Haar rank 6 | 32 | primary structured-operator estimand |
| F48-high | full rank 48 | 128 | information-limit confirmation |
| F48-low | full rank 48 | 32 | registered underpowered refusal |

For LR6, a fresh random orthonormal basis
\(\Phi_A\in\mathbb R^{48\times6}\) is drawn in every population. The estimator
never receives it. Author coordinates are centered within hidden audit group,
then normalized once to RMS 0.30. Group, context, and session components use
independent random subspaces and are not orthogonalized against the author
basis.

This is not circular: the estimator does not know the planted basis, receives
a new basis in each population, selects complexity by discovery likelihood,
and is scored on the reconstructed operator and projection matrix rather than
unidentifiable factor coordinates.

## 3. Registered design

- four incoming, cue, and outgoing branches;
- 96 anonymous packets, balanced over four hidden scorer-only groups;
- 12 discovery contexts from a three-dimensional Sobol design;
- eight unseen confirmation contexts inside the discovery convex hull;
- four extrapolation contexts used only as a stress diagnostic;
- two independent sessions per author-context;
- 32 events per context-session in LR6 and 128 in F48-high;
- 80 discovery and 200 confirmation populations per scenario.

The context basis contains three coordinates and their three pairwise
interactions. Pooled available-branch probabilities must remain in
`[0.05, 0.75]`; normalized outcome entropy must be at least 0.55.

## 4. Estimator and label firewall

1. Fit a mask-aware anonymous reference router \(S+C(z)\) using discovery
   contexts only.
2. Build split-session packet profiles without opening author matches.
3. Fit a four-component diagonal Gaussian mixture to discover stable centers;
   true group labels remain closed.
4. Estimate a PSD cross-session residual covariance and its hidden subspace.
5. Select rank from `{0,2,4,6,8,12}` and lambda from
   `{0.3,1,3,10,30,100,300}` by discovery-context held-out log loss.
6. Project packet profiles into the discovery-only subspace and integrate all
   packets over the same \(Q_{\mathrm{ref}}\).
7. Open author matches and hidden groups only in the scorer.

Packet IDs may aggregate events but may not be model features. Observed cue,
context, or opportunity frequencies never become score weights. No
personality labels are read.

Split-session reliability for a learned low-rank basis is scored only on
confirmation contexts. The full-rank identity branch learns no projection and
may use the complete context panel for its information-limit diagnostic.

Projection residual is retained as approximation uncertainty in confidence
intervals; it is not silently discarded as noise.

## 5. Registered scenarios

| Scenario | Expected decision |
| --- | --- |
| stable_author_lr6 | claim |
| context_only | no claim |
| group_only | all-stranger matching may rise; within-group chance |
| session_unstable | no stable claim |
| opportunity_only | no claim |
| cue_leakage | no claim |
| random | no claim |
| opportunity_nonoverlap | refuse |
| full_rank_high_budget | recover |
| full_rank_low_budget | information-limit refusal |
| rank2_stress / rank12_stress | model-misspecification diagnostics |

Rank stress does not alter the LR6 primary gate. A rank-12 failure is a
capacity boundary, not evidence that no author operator exists.

## 6. Metrics and gates

Primary metrics are scorer-only within-group truth correlation, probability
RMSE, independent split-session and unseen-context reliability, same-author
AUC and retrieval, held-out log-loss gain, ECE, interval coverage, variance
shares, and planted-versus-recovered subspace score.

LR6 requires:

- truth correlation lower bound at least 0.70;
- probability RMSE upper bound at most 0.08;
- split-session reliability lower bound at least 0.60;
- unseen-context reliability lower bound at least 0.55;
- same-author AUC lower bound at least 0.80;
- top-1 lower bound at least 0.20 and within-group top-1 at least 0.15;
- log-loss gain lower bound at least 0.01 nat/event;
- ECE upper bound at most 0.06;
- interval coverage between 0.90 and 0.98;
- variance-share maximum absolute error at most 0.08;
- subspace score lower bound at least 0.70;
- author-claim rate lower bound at least 0.80.

Selected rank must be 4, 6, or 8. Neither rank nor lambda may hit a search
boundary. F48-high reliability must be at least 0.60. F48-low reliability must
remain at most 0.55 and produce no author claim.

Controls require author-claim rate upper bound at most 0.05; group-only
within-group AUC upper bound at most 0.55; session-unstable reliability upper
bound at most 0.20; non-overlap refusal lower bound at least 0.95.

## 7. Governance and boundary

All pre-seal construction and power seeds are permanently excluded in the
machine-readable config. A new canonical seed must be written before the
content-hash seal.

Any confirmation tuning, hidden-label use by the estimator, identity feature,
or observed-frequency score weighting is a global implementation stop.

A PASS licenses only recovery of a structured hidden-low-rank synthetic
routing operator plus a separately budgeted full-rank information limit. It
does not establish arbitrary-48D recovery and does not make \(D_u\) a
personality, intelligence, reasoning, thought-style, clinical, causal, or
real-text parameter. V3.7B blind localization is separate and cannot run until
V3.7A passes.
