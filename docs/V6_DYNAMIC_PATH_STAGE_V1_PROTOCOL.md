# V6 Dynamic Path Stage V1: Frozen Protocol

Status: `FROZEN_BEFORE_ENDPOINT_EXECUTION`
Date: 2026-07-14

## Aim

This stage tests a narrow question: whether an order-sensitive, nonlinear,
author-conditioned path configuration can be detected in current PANDORA text
after opportunity conditioning. It does not test personality, causality, a
clinical state, or quantum mechanics.

The previously observed two-half design is retained only as a coarse diagnostic.
It cannot identify curvature, transient state, recovery, or a stable response
parameter because all within-half deviations that sum to zero are discarded.

## Frozen Objects

For measurement operator \(m=(\psi,\mathcal S,\mathcal A)\), the
author-cross-fitted residual comment path is

\[
X^m_{urt}=\psi_m(T_{urt})-
\widehat{\mathbb E}_{-u}[\psi_m(T)\mid C_{ur},Q_{urt},h(t)].
\]

For lag \(b\in\{1,2,4\}\), a pooled nonlinear conditional model estimates
\(\mu^m_{0,b}(H)\). The candidate author-by-subepoch path object is

\[
G^m_{u,b}=\frac{1}{|R_u|}\sum_{r\in R_u}\frac{1}{n_{r,b}}
\sum_t\left[\phi_m(X^m_{ur,t+b})-\widehat\mu^m_{0,b}(H^m_{urt})\right].
\]

The implementation fixes history order one, Gaussian RFF dimensions 64/64, and
Ridge \(\alpha=10\). It also records the second-order multiscale object

\[
K^m_{u,b}=\mathbb E_r[\Delta_b X^m\Delta_b X^{m\top}\mid u]-K^m_{0,b}.
\]

The display equation above is conceptual. The executable definitions are frozen
in [`v6_dynamic_path_stage_v1.json`](../configs/v6_dynamic_path_stage_v1.json).

## Window Design

Each original early and late half is split once at a complete same-condition
run boundary. Two fixed schemes are evaluated:

- `transition_balanced`: choose the boundary that balances retained transitions.
- `time_balanced`: choose the boundary closest to the half's calendar midpoint.

The resulting four non-overlapping subepochs are the only primary windows.
Each original half needs at least two complete runs and 12 transitions; each
subepoch needs at least one complete run and six transitions. Authors, not
windows or transitions, are inferential units. No run may be split and no
transition may cross a run, condition, or sampling gap.

## Gates

Before fitting any endpoint outcome, metadata feasibility must show at least 300
fixed-hash endpoint authors and at least 80% matched-condition coverage at
Jaccard \(\ge .10\). If either gate fails, PANDORA dynamic confirmation stops.
Relaxing thresholds, adding windows, or changing estimator families after a
failure is prohibited in this stage.

If feasibility passes, the primary family uses word and character TF-IDF
operators under `transition_balanced` windows at lags 1, 2, and 4. It uses
author-block bootstrap and 4,999 stratified permutations with max-T correction.
Promotion requires, for the same lag, own-versus-stranger AUC at least .55,
ordered-minus-shuffled AUC at least .03 with simultaneous lower bound above 0,
and no sign reversal in at least four of five community-hash sensitivity folds.

Only after that family passes may representation/partition robustness and
cross-channel numeric-event-to-text correspondence be evaluated. Raw text
examples stay sealed through the numeric stages.

## Measurement Dependence

Changing a segmentation, representation, or aggregation after text has already
been written changes the estimator, not the historical text. This stage tests
operator robustness, not physical measurement disturbance. Active assessment
reactivity requires future randomized, counterbalanced prompt sequences and
cannot be inferred from observational PANDORA or fixed-order MEPS.

## Boundaries

- A pass identifies an unknown PANDORA-conditioned author-path candidate.
- It does not identify a stable individual response operator, a personality
  trait, a causal mechanism, or a cross-language object.
- MEPS may later be used only for a same-session, fixed-protocol profile check.
- No MBTI, Big Five, or other external labels are read in this stage.
