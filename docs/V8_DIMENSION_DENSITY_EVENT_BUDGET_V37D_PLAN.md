# V8 Dimension-Density-Event-Budget Phase Diagram V3.7D

Status: `EXPLORATORY_DEVELOPMENT`

## Purpose

V3.7C recovered the synthetic author operator at every planted rank, but
rank-2 hard-neighbor identity AUC was much lower than rank 4/6/8. V3.7D tests
whether this is geometric crowding rather than estimator instability.

The experiment isolates operator geometry from blind event localization. It
uses balanced independent categorical event panels and a truly group-free
latent generator: no group label, group count, or within-group centering
enters the data-generating process.

## Grid

- latent rank \(K\): 2, 4, 8, 12;
- authors \(U\): 32, 96, 192;
- events per context-session: 16, 32, 64, 128;
- fixed total author RMS and fixed per-latent-dimension signal regimes;
- eight independent populations per cell.

The V3.7C working rank 8 is the primary estimator. An oracle-rank projection
is a post-primary sensitivity analysis, not the headline method.

The denoising basis and fixed reference router are fitted on 96 training
authors. Every reported recovery, reliability, margin, and identity metric is
computed on a disjoint set of 32, 96, or 192 new authors. This author-inductive
split corrects an in-cohort limitation discovered in the first exploratory
run; that excluded run is
`results/v8_dimension_density_budget/v37d_exploratory_20260726`.

## Geometry

For author \(u\),

\[
\epsilon_u=\|\widehat D_u-D_u\|,
\qquad
m_u=\min_{v\ne u}\|D_u-D_v\|.
\]

The experiment reports the relative nearest-neighbor margin, estimation error,
error-to-margin ratio, and a conservative cross-session identity certificate:

\[
\|\widehat D_u^{(1)}-\widehat D_u^{(2)}\|_{\rm upper}
<
\min_{v\ne u}
\|\widehat D_u^{(1)}-\widehat D_v^{(2)}\|_{\rm lower},
\]

where upper and lower distances use triangle-inequality bounds from truth.

## Critical surfaces

Recovery and identity are evaluated separately:

\[
N_{\rm recover}^{*}(K,\mathrm{SNR})
\]

requires truth correlation at least .80 and split reliability at least .50.

\[
N_{\rm identify}^{*}(K,U,\mathrm{SNR})
\]

requires hard-neighbor AUC at least .80 and top-1 at least .50.

These thresholds describe this simulator and estimator only. V3.7D is
exploratory; no canonical psychological claim is available.
