# V8 V3.7H.4D-R2G Residual Completion Frontier

Date: 2026-07-27

Confirmation decision:
`V8_R2G_INCONCLUSIVE_BOUNDED_COMPLETION`

The decision is not a failure of the factor-existence hypothesis. It states
that the frozen bounded score-only models at four score opportunities did not
reach the registered practical-zero thresholds.

## Design

Each unit supplied four independent observations:

\[
(A_s,A_t,B_s,B_t).
\]

Models read only score observations and predicted independent target
observations. Centers, feature maps, ranks, and regularization were fitted
outside confirmation. Discovery froze:

- `linear rank=4` for author and linear-common omission;
- `quadratic rank=4` for nonlinear-common omission;
- `rank=0` for pure iid, unavailable common shock, and overfit null.

Confirmation used 60 fresh roots under Gaussian and standardized
Student-\(t_5\) noise. All 8,640 registered source streams were unique.

## Confirmation results

The table reports mean normalized cross-view within-group floor ratios.
Values near zero mean that increasing the number of authors inside one
registered group leaves no persistent group-common floor.

| World | Noise | Raw | Learned | Oracle admissible |
|---|---|---:|---:|---:|
| author low-rank | Gaussian | .00009 | .00023 | .00007 |
| author low-rank | \(t_5\) | .00023 | .00015 | .00011 |
| common low-rank | Gaussian | .07813 | .02529 | .00001 |
| common low-rank | \(t_5\) | .07771 | .02480 | -.00006 |
| nonlinear common | Gaussian | .05738 | .03966 | .00001 |
| nonlinear common | \(t_5\) | .05769 | .04026 | .00011 |
| unavailable common shock | Gaussian | .10203 | .10229 | .09996 |
| unavailable common shock | \(t_5\) | .10205 | .10223 | .09940 |

Linear completion removed about 68% of the common floor:

- Gaussian reduction: `.6765 [.6187, .7183]`;
- \(t_5\) reduction: `.6813 [.6208, .7394]`.

It nevertheless missed practical zero:

- learned phi upper bounds: `.0232` and `.0227`, above `.02`;
- learned floor-ratio upper bounds: `.0314` and `.0316`, above `.01`.

Nonlinear completion removed about 30%:

- Gaussian reduction: `.3078 [.1969, .4053]`;
- \(t_5\) reduction: `.3018 [.1830, .4095]`.

Its remaining floor was approximately `.040`, while the oracle floor was
zero within Monte Carlo uncertainty.

## Control findings

The controls all passed.

1. Pure iid residuals stayed below both practical-zero thresholds.
2. Author-only low-rank omission had strong cross-view structure
   (\(\phi\approx.0506\)) but a zero social floor. Therefore aggregation zero
   does not prove factor completeness.
3. The score-unavailable common shock retained a floor near `.10`.
4. The omniscient oracle removed that shock, proving that algebraic
   subtraction and admissible prediction are different claims.
5. The unrestricted decision tree reached training \(R^2=1.0\), but fresh
   confirmation \(R^2\) was approximately `-1.02`. A training residual of zero
   is therefore not factor completeness.

## Ruling

R2G established that current non-zero floors can contain structured,
theoretically removable omission. It also showed that a clean factor's
existence does not guarantee its recoverability from a finite noisy score
observation.

The unresolved term after R2G was:

\[
S_{\mathrm{omit}}-\widehat S_{K=4,m},
\]

where \(K\) is score resolution and \(m\) is factor-model estimation support.
R2G.1 was therefore required before deciding whether this term represented
model inadequacy or finite measurement error.

## Artifacts

- `docs/V8_RESIDUAL_COMPLETION_FRONTIER_V37H4D_R2G_PLAN.md`
- `docs/V8_RESIDUAL_COMPLETION_FRONTIER_V37H4D_R2G_SMOKE_CORRECTION.md`
- `configs/v8_residual_completion_frontier_v37h4d_r2g.json`
- `suica_core/v8_residual_completion_frontier.py`
- `scripts/run_suica_v8_residual_completion_frontier_v37h4d_r2g.py`
- `results/v8_residual_completion_frontier/v37h4d_r2g_discovery_24rep_20260727/`
- `results/v8_residual_completion_frontier/v37h4d_r2g_confirmation_60rep_20260727/`
