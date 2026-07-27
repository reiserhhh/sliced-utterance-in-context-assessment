# V8 Group-Free Routing Transport V3.7C

Status: `PROSPECTIVELY_SEALED_BEFORE_CONFIRMATION`

## 1. Purpose

V3.7C is a correction experiment for the independent-audit findings in
V3.7A and V3.7B. It asks three bounded questions:

1. Can a stable author-relative routing operator be recovered without a known
   group count or true-group centering?
2. Does a geometry-and-order locator transport beyond the exact planted
   pause-cusp family and refuse observationally nonidentifiable labels?
3. Does operator recovery survive independent oracle-test events and
   registered MAR/MNAR missingness?

No psychological or real-text label is opened.

## 2. Group-free estimand

For a common reference opportunity design \(Q_{\mathrm{ref}}\),

\[
D_u
=
\operatorname{ilr}(\Pi_u^{Q_{\mathrm{ref}}})
-
\operatorname{ilr}(\Pi_{\mathrm{ref}}^{Q_{\mathrm{ref}}}).
\]

The estimator globally centers independent session profiles and estimates the
PSD cross-session covariance

\[
\widehat C
=
\frac{
(X-\bar X)^\mathsf T(Y-\bar Y)
+
(Y-\bar Y)^\mathsf T(X-\bar X)
}{2(n-1)}.
\]

Negative eigenvalues are truncated. Candidate projector rank and profile
shrinkage are selected only by discovery-context log loss. No mixture model,
known group count, or group label enters fitting.

The frozen candidate sets are rank
\(\{0,2,4,6,8,12,16\}\), author shrinkage
\(\{0.3,1,3,10,30,100,300\}\), and locator threshold
\(\{0.20,0.25,0.30,0.35,0.40,0.45\}\). A rank must first pass the
discovery-only reliability floor. The smallest rank within 0.001 log-loss of
the discovery optimum is selected.

Primary author matching uses difficult negatives chosen from each author's
nearest discovery-profile neighbors. True groups open only after all primary
metrics are frozen, as a sensitivity audit.

## 3. Independent event design

Every population contains independent random streams for:

- latent routing probabilities;
- reference-router training counts;
- blind-locator training counts;
- oracle-comparator training counts;
- oracle-test counts;
- path geometry;
- missingness;
- bootstrap summaries.

Blind and oracle gains are scored on the same independent oracle-test panel.
Blind-versus-truth and blind-versus-independent-oracle correlations therefore
do not share event-level sampling noise.

All streams derive from recorded `SeedSequence` spawn keys. Integer-offset
seed derivation is prohibited.

## 4. Locator transport and identifiability

The frozen V3.7B score remains the locator. V3.7C adds:

- asymmetric and multi-peak out-of-family transitions;
- lower-amplitude, higher-noise transitions;
- smooth, bend, pause, cue-bend, near-crossing, and speed-wave negatives;
- an observationally isomorphic control in which identical path draws receive
  independent latent junction labels.

For a true event, unconditional error is

\[
e_i
=
\begin{cases}
|\widehat t_i-t_i^*|,&\text{detected},\\
T,&\text{missed}.
\end{cases}
\]

P95 is computed over all positives. The isomorphic control must have AUC near
0.5 and produce `NONIDENTIFIABLE_FROM_TRAJECTORY`; forced discrimination is a
failure.

## 5. Common-reference missingness correction

Blind, oracle, MAR, and MNAR profiles use one reference router fitted only on
independent discovery oracle-training counts. Available cases may not define
their own reference population.

For observed event indicator \(M_i\) and propensity \(\pi_i\), IPW uses

\[
\widehat L_{\mathrm{IPW}}
=
\sum_i\frac{M_i}{\widehat\pi_i}\ell_i.
\]

The augmented multinomial total for outcome \(k\) is

\[
\widehat T_k^{\mathrm{AIPW}}
=
N\widehat m_k
+
\sum_{i:M_i=1}
\frac{\mathbf 1(Y_i=k)-\widehat m_k}{\widehat\pi_i}.
\]

MAR reports available-case, IPW, and AIPW results. MNAR does not receive a
point-identification claim; a frozen gamma grid defines a sensitivity
envelope.

## 6. Arms

| Arm | Role |
| --- | --- |
| `core_lr` | hidden rank cycles through 2/4/6/8; no group effect; 128 events |
| `low_budget` | 32-event registered reliability boundary |
| `group_mix` | stable group plus author effect; true groups scorer-only |
| `out_of_family` | asymmetric/multi-peak transition transport |
| `high_noise` | lower signal and higher trajectory noise |
| `mar` | observed-covariate-dependent missingness |
| `mnar` | outcome-dependent missingness sensitivity envelope |

The first smoke at 32 events stopped at truth correlation about 0.59 and
hard-neighbor AUC about 0.69. A pre-seal information curve reached truth
correlation 0.81 at 64 events and 0.96 at 128 events for rank 6. The primary
budget is therefore 128 events per context-session; the 32-event arm is
retained as a negative capacity control rather than hidden.

Discovery uses 24 populations. Confirmation uses 80 populations per arm.
An eight-population smoke and a bounded pre-seal power run precede the new
canonical seed and content seal.

The pre-seal ledger is frozen in the configuration. It records three smoke
runs, the 64/128-event information curve, and the bounded power run. None of
those results may enter the canonical confirmation set. A nonpositive oracle
log-loss gain makes gain retention undefined rather than numerically
unbounded; this is expected for the registered 32-event capacity control.

## 7. Decision boundary

A PASS supports only group-free synthetic operator recovery and transport
within the registered perturbation families. An out-of-family failure closes
the transport claim but does not invalidate V3.7A's matched-family result.
The isomorphic control formalizes a nonidentifiability boundary rather than a
classifier target.

Personality, cognition, intelligence, clinical interpretation, arbitrary
real-text event discovery, and external validity remain closed.
