# V8 V3.7H.4D R2B Geometry Information Operator

Status: prospective internal synthetic discovery; detector frozen.

## Objective

R2A confirmed an iid-only \(m=8\) operational boundary. R2B explains why
matched scalar residual information does not transport to intrinsic-zero-sum
geometry.

For each panel, the registered weighted residual representative is:

\[
W_p=D_p^{-1/2}(q_R-X\hat b_p),
\qquad
\hat b_p=\arg\min_b(q_R-Xb)'D_p^{-1}(q_R-Xb).
\]

Concatenating panels gives \(W=[W_2|W_3]\) and:

\[
\mathcal I_M=\lVert W\rVert_F^2,
\qquad
G_A=WW^\top.
\]

## Frozen geometry coordinates

- total residual information;
- effective author sign support;
- maximum author leverage;
- effective cell and condition support;
- top-three cross-panel spectral concentration;
- whitened centering halo;
- effective author sign contribution support;
- sign and active-condition coherence;
- author Gram effective rank.

Geometry labels are held-out strata only and may never be predictor features.

## Paired worlds

For each \(m=4,8,16\), noise mode, and 300 base seeds, seven geometries share
the same additive world, opportunity counts, panel shocks, technical noise,
and wild-sign draws:

1. iid halo anchor;
2. intrinsic zero sum;
3. author concentrated;
4. condition concentrated;
5. rank-one coherent;
6. balanced antiphase;
7. halo sweep, cycling lambda 0/.03/.06/.15.

Every geometry is scaled after residual projection to the paired iid scalar
information with relative error at most \(10^{-6}\). The full discovery has
12,600 rows; the base seed is the statistical unit.

## Validation

The scalar model uses log information, log \(m\), noise mode, and a quadratic
information term. The operator model adds the registered geometry
coordinates.

Evaluation leaves out an entire geometry family and a disjoint base-seed fold
simultaneously. Ridge penalty is selected only by inner base-seed grouped CV.
Primary comparisons are paired log loss and Brier improvement with base-seed
cluster bootstrap intervals.

## Gates

- detector source lock and frozen 99-permutation/Holm .05 path;
- complete pairing, unique source streams, information match <= \(10^{-6}\),
  projection compatibility <= \(10^{-12}\);
- iid-minus-intrinsic power lower bound > .10 at m=4/8 in both noises;
- log-loss improvement lower > .02 nats/row;
- Brier improvement lower > .005;
- held-out intrinsic log-loss improvement lower > 0;
- effective sign-support coefficient lower > 0;
- absolute calibration error <= .10 for every held-out geometry.

The result can explain detector sensitivity only. It cannot name or validate a
psychological construct.

