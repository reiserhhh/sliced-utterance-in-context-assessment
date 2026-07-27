# V8 V3.7H.4D Reference-Measure Frontier Plan

Status: prospective synthetic discovery protocol, frozen before execution.

## Purpose

H.4 used double-centered interactions, so the planted residual could not
change the registered author or condition main effects. Real text need not
respect that orthogonality.

H.4D defines an author score relative to a fixed condition reference measure
and tests whether that score remains comparable under condition-selection
shift, nonorthogonal interactions, limited support, and out-of-family residual
geometry.

No real text, external label, personality construct, diagnosis, or clinical
claim is used.

## Estimand

For author \(u\), condition \(c\), panel \(p\), opportunity \(k\), and score
dimension \(j\):

\[
Y_{ucpkj}
=
m_{ucj}+L_{ucpj}+\varepsilon_{ucpkj},
\]

\[
m_{ucj}
=
\mu_j+S_{s(u)j}+G_{g(u)j}+A_{uj}+H_{cj}+Q_{ucj}.
\]

Conditions are sampled from an author- and environment-dependent measure:

\[
\pi_{e,u,c}
\propto
\pi^\star_c
\exp(\delta_e v_c+\zeta x_u w_c).
\]

The common reference is uniform over the 16 registered conditions:

\[
\pi^\star_c=1/16.
\]

The formal author score is:

\[
\theta^\star_{uj}
=
\sum_c\pi^\star_c
\left[
m_{ucj}
-\sum_v\nu_vm_{vcj}
\right],
\qquad
\nu_u=1/N.
\]

Reference sensitivity is:

\[
\Delta\theta_u(\pi_1,\pi_0)
=
\sum_c(\pi_{1c}-\pi_{0c})
\left[m_{uc}-\bar m_{\cdot c}^{\,\nu}\right].
\]

When \(Q\) is not centered under the selected reference, changing \(\pi\)
changes author position. This is not automatically measurement error.

## Worlds

1. `additive`: \(Q=0\), full support.
2. `noncentered`: rank-one \(Q_{uc}=\gamma b_ug_c\) with nonzero
   \(\pi^\star\)-mean condition loading.
3. `reference_shift`: one fixed \(m_{uc}\), two full-support environments
   separated by registered Jensen-Shannon divergence.
4. `support_violation`: author groups have structural zero probability on
   conditions with positive \(\pi^\star\) mass.
5. `full_rank`: diffuse, approximately flat-spectrum interaction.
6. `minority_local`: interaction exists only for a minority of authors and
   conditions.
7. `near_kernel`: residual structure is strong but its common-reference score
   projection is small.
8. `aq_alias`: \((A,Q)\) and \((A+r,Q-r)\) generate identical observations.

The A/Q alias must return `CAUSE_UNIDENTIFIED`.

## Frozen design

- 256 authors: 8 societies, 4 groups per society, 8 authors per group;
- stratified author split inside every group: 4 train, 2 calibration, 2 test;
- 16 conditions and 6 score dimensions;
- 4 panels: train environments on panels 1-2, fresh test acquisitions on
  panels 3-4;
- nested opportunity prefixes \(K=64,128,256\), primary \(K=128\);
- Gaussian and standardized heteroskedastic \(t_5\) noise;
- stable interaction shares \(\omega=.05,.20\);
- reference-shift JSD targets .05 and .15;
- support coverage targets 1.00, .90, and .75.

Main cells use 100 repetitions. Boundary cells use 60 Gaussian repetitions.
The new detector receives 1,000 fresh additive controls per noise mode.

## Observation-only estimator

Naive score:

\[
\widehat\theta^{naive}_{u,e}
=
\frac1K\sum_i
\left(Y_{uei}-\widehat\mu_{c(i)}\right).
\]

Common-reference score uses stabilized Hajek weights:

\[
w_{ueic}
=
\frac{\pi^\star_c}{\widehat\pi_{e,u,c}},
\]

\[
\widehat\theta^\star_{u,e}
=
\frac{\sum_iw_{ueic}
(Y_{uei}-\widehat\mu_c)}
{\sum_iw_{ueic}}.
\]

Propensity coefficients and condition profiles are fit only on train authors
and panels 1-2. Pseudocount is selected only on calibration authors. Test
authors and panels 3-4 are opened once.

Generator \(A,Q,\pi\) values are prohibited from fitting, tuning, detection,
or refusal decisions. Oracle quantities are evaluation-only.

## Overlap refusal

Author-level reference coverage:

\[
\Omega_{u,e}
=
\sum_c\pi^\star_c
I(N_{u,e,c}>0).
\]

Weight effective sample size:

\[
ESS_{u,e}
=
\frac{(\sum_iw_i)^2}{\sum_iw_i^2}.
\]

A formal score requires:

\[
q_{.05}(\Omega)\ge.95,
\qquad
q_{.05}(ESS)\ge32,
\]

and no empirical group-by-condition structural zero in the training
acquisition. Otherwise output `REFUSE_NONOVERLAP`; no oracle imputation or
low-rank extrapolation is allowed.

## Residual detector

Three independent-panel channels are used:

- CRC for replicated residual direction;
- singular-energy concentration for low-rank structure;
- Higher Criticism over cellwise cross-panel products for sparse/minority
  structure.

The three p-values use Holm familywise alpha .05. Adding Higher Criticism
defines a new detector; H.4C calibration does not carry over.

## Metrics

\[
nSTE
=
\frac{
\operatorname{RMSE}
(\widehat\theta^\star,\theta^\star)
}{
\operatorname{SD}(\theta^\star)
},
\]

\[
D^\star
=
\frac{
\operatorname{RMSE}
(\widehat\theta^\star_{\pi_0}
-\widehat\theta^\star_{\pi_1})
}{
\operatorname{SD}(\theta^\star)
},
\]

\[
RCG
=
1-
\frac{
MSE(\widehat\theta^\star_{\pi_0},
\widehat\theta^\star_{\pi_1})
}{
MSE(\widehat\theta^{naive}_{\pi_0},
\widehat\theta^{naive}_{\pi_1})
}.
\]

Also report common-reference Pearson correlation, overlap refusal,
diagnostic-specific detection, effective rank, score-projection ratio,
invalid formal-score output, and A/Q attribution.

## Frozen gates

New detector W0:

- per-noise simultaneous one-sided false-refusal upper below .05;
- full-support false overlap-refusal upper below .05;
- simultaneous nSTE upper below .15;
- panel 3-4 score correlation lower above .85.

Reference shift at JSD .15 and \(\omega=.20\):

- simultaneous RCG lower above .50;
- \(D^\star\) upper below .20;
- common-reference correlation lower above .90;
- naive-minus-reference paired error lower above zero.

Support violation at coverage .75:

- `REFUSE_NONOVERLAP` lower above .90;
- invalid formal-score output upper below .05.

Strong \(\omega=.20\) structure:

- `noncentered`, `full_rank`, and `minority_local` detection lower above .90;
- `full_rank` cannot pass only through the low-rank channel;
- `minority_local` must be detected by CRC or Higher Criticism.

Near-kernel at \(\omega=.20,\alpha=.02\):

- residual detection lower above .90;
- false "score changed" upper below .05;
- output `STRUCTURE_DETECTED_SCORE_NEAR_KERNEL`.

A/Q alias:

- observation identity error at most \(10^{-12}\);
- `CAUSE_UNIDENTIFIED` lower above .95;
- specific attribution upper below .05.

Weak effects, JSD .05, and coverage .90 are sensitivity boundaries only.

## Decisions

- `PASS_REFERENCE_TRANSPORT_AWARE`;
- `PARTIAL_REFERENCE_DEPENDENT`;
- `REFUTED_REFERENCE_STABILITY`;
- `STOP_INTEGRITY`.

`CAUSE_UNIDENTIFIED`, `REFUSE_NONOVERLAP`, and
`STRUCTURE_DETECTED_SCORE_NEAR_KERNEL` are valid cell-level outputs.

## Claim boundary

Even a pass establishes only synthetic common-reference score transport and
refusal behavior under the registered worlds. Algebraic energy, rank, kernel,
reference, and alias identities are construction checks. Real text,
psychological validity, diagnosis, clinical use, and arbitrary-world
calibration remain closed.
