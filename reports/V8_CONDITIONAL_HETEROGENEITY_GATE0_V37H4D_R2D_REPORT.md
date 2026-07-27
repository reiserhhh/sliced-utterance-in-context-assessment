# V8 V3.7H.4D R2D Conditional-Heterogeneity Gate-0

Date: 2026-07-27

Machine decision:
`V8_R2D_GATE0_STOP_NO_EXPLOITABLE_CONDITIONAL_TARGET`

Scientific decision:
`REGISTERED_DGP_POWER_IS_PRIMARILY_CELL_LEVEL`

Status: fresh-seed repeated-outcome synthetic resource gate. This is not an
R2D model test, real-text validation, or psychological validation.

## Question

R2C reconstructed registered-cell power but failed to predict which
particular fresh panel pair would reject. Gate-0 therefore tested whether the
registered data-generating process contained enough base-level conditional
heterogeneity to justify fitting a posterior-predictive R2D model.

For base \(i\) in registered cell \(c\):

\[
p_i=P\{D(O,S)=1\mid Q_i,\psi_i,c\},
\qquad
V_c=\operatorname{Var}(p_i\mid c).
\]

If \(V_c\) is negligible, no estimator can materially improve Brier score
over the cell probability, even if the latent base were known exactly.

## Design and integrity

- 8 independent cells: Gaussian or heteroskedastic \(t_5\), crossed with
  four `m=4` core/halo geometries;
- 50 fresh latent bases per cell, 400 bases total;
- 32 independent outcome-panel pairs per fixed base;
- 12,800 unchanged 99-sign CRC/low-rank/HC/Holm detector outcomes;
- fresh opportunity counts, panel shocks, technical noise, and detector
  streams for every outcome;
- 20,000 base-block bootstrap draws;
- no external labels, R2C outcomes, probability clipping, or
  outcome-fitted calibration.

All eight protocol checks passed: source locks, row and base counts,
replicate completeness, globally unique hierarchical seed streams,
information matching, one fixed latent interaction per base, and numeric
integrity. The run manifest and artifact inventory also reverified without
failure.

## Primary resource result

The pooled method-of-moments estimate was:

\[
\widehat V_{\mathrm{pooled}}=.002925,
\qquad 95\%\ CI=[.001456,.004114].
\]

The preregistered STOP boundary was an upper confidence bound at most `.005`.
It was crossed. Thus, under the registered eight-cell mixture, even an oracle
that knew each base's true \(p_i\) could not be expected to improve Brier
score over the cell mean by more than `.005`.

No 64-replicate continuation is permitted or needed: that continuation was
reserved for an inconclusive variance interval, whereas this interval
crossed the frozen futility boundary.

## Cell structure

| Noise | Geometry | \(V_c\) | pointwise 95% CI | simultaneous lower |
| --- | --- | ---: | ---: | ---: |
| Gaussian | core only | -.00031 | [-.00130, .00071] | -.00562 |
| Gaussian | lambda .01, support 8 | .00324 | [-.00061, .00703] | -.00208 |
| Gaussian | lambda .01, all 64 | .00559 | [.00121, .01009] | .00028 |
| Gaussian | lambda .03, support 8 | .00218 | [-.00122, .00578] | -.00314 |
| \(t_5\) | core only | -.00058 | [-.00156, .00038] | -.00590 |
| \(t_5\) | lambda .01, support 8 | .00121 | [-.00235, .00530] | -.00411 |
| \(t_5\) | lambda .01, all 64 | .00843 | [.00255, .01468] | .00312 |
| \(t_5\) | lambda .03, support 8 | .00364 | [-.00009, .00737] | -.00168 |

Negative estimates are retained rather than truncated and indicate sampling
noise around a near-zero variance component.

The all-author halo is a bounded local exception: both noise families have
the largest point estimates there. It did not pass the registered
simultaneous `.005` lower-bound gate, and the pooled protocol correctly
stopped. It may motivate a new, separately registered heterogeneity-surface
study; it cannot retrospectively promote this result.

## A-half to B-half prediction

The first 16 outcomes estimated a base-specific Jeffreys probability and
predicted the independent final 16. The comparator was a leave-one-base-out
cell Jeffreys mean fitted only on other bases' A outcomes.

- log-loss gain: **-.02283**, 95% CI [-.03098, -.01490];
- Brier gain: **-.00761**, 95% CI [-.01065, -.00465].

Both gains were negative in Gaussian and \(t_5\) arms. This supports the
resource STOP, but did not trigger it: finite A-half estimation noise can
make a weak estimator fail even when \(V_c>0\).

## Consequences for R2B, R2C, and R2D

R2B remains valid as a group/design-level geometry operator. R2C remains
valid as a registered-cell calibration result and invalid as an individual
conditional predictor. Gate-0 now shows why a full R2D posterior model is
not justified in the current DGP: its average base-level target is too small,
not merely hidden by an insufficient model.

This does not show that individual conditional structure is impossible in
SUICA or in real text. It shows that the current synthetic generator varies
geometry mainly between registered cells while leaving too little
within-cell base heterogeneity. A future synthetic world intended to study
individual response operators must explicitly vary psychologically
meaningful base parameters within condition cells rather than treating
individuality as incidental Monte Carlo variation.

## Next experiment

Do not fit full R2D. The next bounded mechanism study should map the local
heterogeneity surface suggested by the all-author halo:

\[
V(\lambda,s,\nu)
=
\operatorname{Var}\!\left[
P\{D=1\mid Q,\lambda,s,\nu\}
\mid \lambda,s,\nu
\right],
\]

where \(s\) is author support and \(\nu\) is noise family. It should use fresh
bases, repeated outcomes, and a grid around `support=64`, with no
post-outcome predictor fitting. Its purpose is to determine whether the
local peak is a stable geometry-driven phase boundary or sampling variation.

## Claim boundary

Supported:

- base-level detector probability varies weakly but nonzero on average;
- the registered pooled variance is below the practical resource threshold;
- current detector power is primarily design/cell-level;
- full R2D is not a justified use of compute for this DGP.

Not supported:

- absence of all individual heterogeneity;
- personality, psychological constructs, semantics, diagnosis, causality,
  or clinical use;
- transfer of this synthetic futility bound to real text.

## Artifacts

- `docs/V8_CONDITIONAL_HETEROGENEITY_GATE0_V37H4D_R2D_PLAN.md`
- `configs/v8_conditional_heterogeneity_gate0_v37h4d_r2d.json`
- `suica_core/v8_conditional_heterogeneity_preflight.py`
- `scripts/run_suica_v8_conditional_heterogeneity_gate0_v37h4d_r2d.py`
- `results/v8_posterior_predictive_orbit/v37h4d_r2d_conditional_heterogeneity_gate0_12800outcomes_20260727/`
