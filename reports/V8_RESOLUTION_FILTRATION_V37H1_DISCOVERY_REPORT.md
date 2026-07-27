# V8 Resolution Filtration V3.7H.1 Discovery Report

Date: 2026-07-26

Decision:
`RISK_CONTRACTIVE_RESOLUTION_FLOW_NOT_POSTERIOR_MARTINGALE`

Status: discovery only; no confirmation seed exists.

## Why V3.7H.1 was needed

V3.7H showed strong risk and uncertainty contraction but failed to detect an
author-specific opportunity drift with its adjacent-update \(\kappa\) gate.
V3.7H.1 introduced:

1. a scorer-only posterior projection identity;
2. a non-redundant observable budget-32 history;
3. one jointly selected predictor of cumulative movement from budget 32 to
   budgets 64, 128, 256, and 512;
4. explicitly named one-sided familywise bootstrap bounds.

The oscillating-assay export bug was also repaired. Assay rows no longer
inherit main-arm risk, proxy-loss, or decomposition fields.

## Integrity

- 30 independent repetitions;
- 1,800 budget-level rows;
- 2,160 transition/path rows;
- 5,910 unique RNG streams out of 5,910;
- zero nested-prefix error;
- maximum reconstruction error \(2.44\times10^{-15}\);
- exact scorer projection algebra error \(1.74\times10^{-16}\);
- 29 targeted V3.7G/H/H.1 tests passed before discovery.

## Scorer-only projection result

For \(m<n\), V3.7H.1 tested:

\[
D_{m,n}
=
R_n-R_m+U_{m,n},
\]

where \(R_m\) is scorer-only NMSE and \(U_{m,n}\) is normalized update
energy. A true posterior martingale would have \(D_{m,n}=0\).

All core adjacent NMSE changes were strongly negative. Risk therefore
decreased at every resolution step. However, the registered
\([-0.01,0.01]\) equivalence gate failed.

Largest systematic early-step defects:

| World | Transition | Mean projection defect |
| --- | --- | ---: |
| Broken spectrum | 32 to 64 | 0.01492 |
| Dense tail | 32 to 64 | 0.01252 |
| Exact rank 12 | 32 to 64 | 0.01386 |
| Long memory | 32 to 64 | 0.01805 |

At later budgets, defects mostly moved closer to zero, although their signs
depended on the spectrum. The exact algebraic equivalence between the defect
and posterior-orthogonality form held to machine precision, so this is not a
calculation bug.

The fitted path is therefore not an empirical posterior martingale. It is a
cross-validated sequence of changing regularization operators:

\[
M_m=\widehat\mu_0+W_m(\bar X_m-\widehat\mu_0).
\]

Its updates can carry operator-estimation and regularization drift even while
true risk decreases.

## Observable cumulative-path result

Using only:

\[
Z_{32}
=
[M_{32}-\widehat\mu_0,\ U_{32},\
X^{(1)}_{32}-X^{(2)}_{32}],
\]

the probe panel jointly selected one predictor across four horizons. The
evaluation-panel pooled cumulative predictability was:

| World | Mean pooled cumulative \(\kappa\) | One-sided familywise interval |
| --- | ---: | ---: |
| Broken spectrum | 0.00834 | [0.00511, 0.01163] |
| Dense tail | 0.00983 | [0.00735, 0.01237] |
| Exact rank 12 | 0.01128 | [0.00821, 0.01441] |
| Long memory | 0.01018 | [0.00830, 0.01210] |
| Opportunity drift | 0.15074 | [0.14777, 0.15355] |

The strict core upper gate of 0.01 failed. The richer predictor detects a
small but repeatable component of ordinary regularization flow. Opportunity
drift nevertheless produces roughly fourteen times the core signal and is
cleanly separated.

This resolves the V3.7H detector problem without restoring a martingale
claim:

\[
\text{core path}:
\quad
\kappa^{cum}\approx .008-.011,
\]

\[
\text{opportunity drift}:
\quad
\kappa^{cum}\approx .151.
\]

## Theory update

The supported object is:

> an externally referenced, information-conserving,
> risk-contractive resolution flow with measurable regularization drift.

It is not:

> an exact or operationally equivalent posterior martingale.

This distinction is scientifically useful. A measurement system does not
need zero path drift to improve with more evidence. It does need to estimate
its normal resolution-flow drift and distinguish it from materially larger
condition/opportunity responses.

The next refusal rule should therefore be calibrated against the stationary
core-flow distribution, not against zero. More importantly, the same authors
must be scored under at least two explicitly varied opportunity schedules.
Without such variation, stable condition response and stable author
structure remain construct-aliased.

## Current boundary

Accepted:

- monotone scorer-only risk improvement in four synthetic core worlds;
- uncertainty contraction with registered model-assisted coverage;
- reversible score and unresolved channels;
- a measurable core regularization flow;
- strong observable separation of the planted opportunity drift.

Rejected:

- the posterior-martingale formulation at the registered \(\pm0.01\) margin;
- a universal zero-\(\kappa\) definition of valid measurement;
- treating one stable opportunity schedule as sufficient for trait
  identification.

Still open:

- paired-schedule operational refusal;
- matched power across low-rank, random-rotation, and nonlinear drift;
- public seal and fresh-seed confirmation;
- every real-text and psychological-validity question.

## Reproducibility

Artifacts:
`results/v8_resolution_filtration/v37h1_discovery_30rep_20260726/`

Config:
`configs/v8_resolution_filtration_v37h1_discovery.json`

Core:
`suica_core/v8_resolution_filtration_h1.py`

Runner:
`scripts/run_suica_v8_resolution_filtration_v37h.py`
