# V8 V3.7H.4D R2D Conditional-Heterogeneity Gate-0

Status: prospective protocol; no Gate-0 outcome inspected at registration.

## Question

R2C established registered-cell calibration but failed individual
conditional prediction. Before fitting an expensive posterior-predictive
model, Gate-0 asks whether the current data-generating process contains a
non-negligible base-level target at all:

\[
V_c=\operatorname{Var}(p_i\mid c),\qquad
p_i=P\{D(O,S)=1\mid Q_i,\psi_i,c\}.
\]

This is a resource and identifiability gate, not an R2D model test.

## Frozen design

- eight registered cells: two noise families by four `m=4` core/halo
  geometries;
- 50 fresh latent bases per cell, 400 bases total;
- cells use independent latent bases; there is no cross-geometry shared-world
  cluster;
- latent world, interaction \(Q_i\), geometry, and acquisition law are fixed
  within a base;
- 32 independent outcome-panel pairs per base;
- opportunity counts, panel shocks, technical noise, and the 99-sign
  detector stream are fresh for every outcome;
- unchanged CRC/low-rank/HC diagnostics and Holm `.05`;
- 12,800 detector outcomes in the formal run.

No R2B/R2C outcomes, external labels, probability clipping, or
outcome-fitted calibration are used.

## Variance estimand

For \(S_i\) detections among \(R=32\) outcomes:

\[
\widehat V_c=
\operatorname{Var}_{i\in c}(S_i/R)
-
\frac1{n_c}\sum_{i\in c}
\frac{S_i(R-S_i)}{R^2(R-1)}.
\]

The estimator is not truncated at zero. Eight cell intervals use 20,000
base-block bootstrap draws and one-sided simultaneous max-deviation bounds.
Each resampled unit retains all 32 outcomes from one base. The pooled
estimate is the equal-cell mean.

## Predictive split

The first 16 outcomes form A and the last 16 form B. The base estimate is the
frozen Jeffreys value:

\[
\widehat p_i^A=\frac{S_i^A+1/2}{17}.
\]

It predicts all B outcomes and is compared with a leave-one-base-out
registered-cell Jeffreys mean fitted only from other bases' A outcomes.
Paired log-loss and Brier gains are bootstrapped by resampling bases within
registered cells.

## Gates

`GO_CONDITIONAL_TARGET_DEMONSTRATED` requires all:

1. pooled Brier-gain lower 95% bound above `.005`;
2. pooled log-loss-gain lower 95% bound above `.02`;
3. at least two cells with simultaneous variance lower bound above `.005`;
4. positive point gains in both Gaussian and heteroskedastic-\(t_5\) arms.

`STOP_NO_EXPLOITABLE_CONDITIONAL_TARGET` is triggered only when:

1. pooled variance upper 95% bound is at most `.005`.

The A-to-B gains cannot trigger STOP: they measure one noisy finite-sample
Jeffreys estimator, not the best possible posterior estimator. Their failure
therefore does not prove absence of a base-level target.

All other valid outcomes are
`INCONCLUSIVE_INCREASE_REPLICATES_ONLY`; the only allowed follow-up is to
increase outcomes per base from 32 to 64 without changing bases, cells,
estimands, or thresholds. Hierarchical seed derivation preserves every latent
base and the first 32 outcome streams. If the 64-replicate run remains
inconclusive, the decision is `INCONCLUSIVE_RESOURCE_LIMIT`; adding bases
requires a separately registered fresh protocol.

## Claim boundary

Passing would show exploitable base-level conditional heterogeneity for the
registered synthetic detector. Stopping would show that its power is
primarily design/cell-level in this data-generating process. Neither outcome
identifies personality, a psychological construct, semantics, diagnosis,
causality, or clinical validity.
