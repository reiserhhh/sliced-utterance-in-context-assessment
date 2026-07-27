# V8 V3.7H.4D R1 Reference-Contrast Frontier Report

Date: 2026-07-26

Machine decision:
`V8_REFERENCE_CONTRAST_FRONTIER_V37H4D_R1_PARTIAL_REFERENCE_CONTRAST`

Scientific decision:
`REFERENCE_CONTRAST_CORE_PASS_MINORITY_SENSITIVITY_UNRESOLVED`

Status: internal prospective discovery; not sealed confirmation.

## Why R1 was necessary

The original H.4D smoke test attempted to estimate the absolute contribution
of interaction \(Q\) after removing author means. That projection was
algebraically forced near zero and contradicted the A/Q observational alias:

\[
A'_u=A_u+r_u,
\qquad
Q'_{uc}=Q_{uc}-r_u.
\]

R1 replaced the unidentifiable target with:

\[
C_{\delta\pi}(M)_u
=
\sum_c\delta\pi_c
\left(M_{uc}-\bar M_{\cdot c}\right),
\qquad
\sum_c\delta\pi_c=0.
\]

This contrast is invariant to the A/Q gauge transformation.

## Design

- 256 authors with 128/64/64 stratified train/calibration/test split;
- 16 conditions, 6 score dimensions, 4 panels;
- primary opportunity budget K=128;
- Gaussian and heteroskedastic standardized \(t_5\) noise;
- 99 shared author-level wild-sign null draws;
- CRC, cross-panel low-rank, and Higher-Criticism channels with Holm alpha
  .05;
- 1,000 W0 calibration repetitions per noise;
- 100 repetitions per main world/noise cell;
- 60 Gaussian repetitions per sensitivity boundary cell;
- 3,760 Monte Carlo rows across 22 registered design cells;
- 11,280/11,280 unique seeds.

Run manifest and artifact inventory passed.

## New detector calibration

| Noise | W0 false refusals | Rate | Simultaneous upper | False sensitive |
| --- | ---: | ---: | ---: | ---: |
| Gaussian | 26/1000 | .026 | .03787 | 0/1000 |
| Heteroskedastic \(t_5\) | 24/1000 | .024 | .03550 | 0/1000 |

The geometry-preserving wild-sign detector passed its registered W0
calibration. W0 estimated contrast magnitude was .0078/.0090 and no W0 cell
was called reference-sensitive.

## Common-reference transport

At JSD=.15 and interaction share .20:

| Noise | Mean RCG | Simultaneous RCG lower | D-star upper | Score correlation lower |
| --- | ---: | ---: | ---: | ---: |
| Gaussian | .8079 | .8004 | .1013 | .99498 |
| Heteroskedastic \(t_5\) | .8132 | .8053 | .1008 | .99504 |

Under the correctly specified synthetic propensity model and full support,
fixed-reference weighting recovered a stable author position across
acquisition environments.

This does not establish robustness to propensity misspecification.

## Gauge-invariant contrast

The strong contrast-sensitive world produced:

- Gaussian mean \(D_C=.6392\);
- heteroskedastic \(t_5\) mean \(D_C=.6472\);
- 100/100 residual detections and sensitive classifications in both modes.

The strong contrast-kernel world produced:

- Gaussian mean \(D_C=.00388\);
- heteroskedastic \(t_5\) mean \(D_C=.00633\);
- 100/100 residual detections and near-kernel classifications;
- 0/100 false sensitive classifications in both modes.

Therefore:

> A reproducible residual can exist without changing the registered reference
> contrast, and a reference-sensitive residual can be distinguished from that
> kernel using observation-only independent panels.

This is the main R1 result.

## Support and attribution boundaries

At structural support coverage .75:

- 100/100 cells per noise returned `REFUSE_NONOVERLAP`;
- no invalid formal score was emitted.

The A/Q alias had identity error below \(10^{-12}\). The implementation
returned `CAUSE_UNIDENTIFIED_AQ` in all registered cells and never emitted a
specific attribution.

The identity is a valid mathematical non-identification proof. The 100%
classification rate is not learned performance because the alias governance
output is keyed to the registered world and specific attribution is
hard-coded false.

## Out-of-family residual geometry

Full-rank interaction:

- effective rank approximately 47.43;
- 100/100 detections in both noise modes;
- 100/100 detections without requiring the low-rank channel.

This shows that the omnibus detector is not restricted to the registered
rank-three channel.

Minority-local interaction failed its strict gate:

| Noise | Overall detection | Non-low-rank detection | Frozen lower bound |
| --- | ---: | ---: | ---: |
| Gaussian | 93/100 | 91/100 | .8482 |
| Heteroskedastic \(t_5\) | 84/100 | 83/100 | .7560 |

CRC was the strongest channel (91/83), while HC detected only 63/59. The
registered lower-bound target above .90 was not met.

An independent seed reconstruction found that missed cells contained only
about 3.8 active test authors on average versus about 6.8 in detected cells.
The gate therefore mixed detector power with realized minority support.

## Decision

The overall machine status remains `PARTIAL` because one frozen gate failed.

The scientific result is:

> In the registered synthetic worlds, SUICA can estimate a gauge-invariant
> cross-reference author response under common support, can distinguish
> residual existence from registered contrast relevance, and can refuse
> structural nonoverlap. Sensitivity to randomly allocated minority-local
> structure remains unresolved.

## What is not established

- arbitrary minority/local detection;
- a proof that the residual itself is non-low-rank;
- absolute separation of \(A\) and \(Q\);
- robustness to unknown or misspecified propensity;
- multiple-reference response-operator recovery;
- real-text, personality, psychological, causal, diagnostic, or clinical
  validity.

## Next experiment

R2 must condition on minority information budget rather than global effect
share alone:

\[
\mathcal I_M
=
\sum_{u\in M\cap T}
\sum_{c\in C_M}
\frac{
n_{uc}\lVert Q_{uc}\rVert^2
}{
\sigma_{uc}^2
}.
\]

It should fix active test authors at \(m=2,4,8,16\), compare global-energy
and active-cell-SNR arms, estimate minimum \(m_{90}\), and confirm it with
fresh seeds without modifying the R1 detector.

## Artifacts

- `docs/V8_REFERENCE_CONTRAST_FRONTIER_V37H4D_R1_PLAN.md`
- `configs/v8_reference_contrast_frontier_v37h4d_r1.json`
- `suica_core/v8_reference_measure_frontier.py`
- `scripts/run_suica_v8_reference_contrast_frontier_v37h4d_r1.py`
- `tests/test_v8_reference_contrast_frontier_v37h4d_r1.py`
- `results/v8_reference_contrast_frontier/v37h4d_r1_discovery_3760rep_20260726/`
