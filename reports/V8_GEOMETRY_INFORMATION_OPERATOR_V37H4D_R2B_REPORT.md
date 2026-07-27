# V8 V3.7H.4D R2B Geometry Information Operator

Date: 2026-07-27

Decision:
`V8_GEOMETRY_INFORMATION_OPERATOR_V37H4D_R2B_PARTIAL_OPERATOR_PREDICTIVE_NOT_SUFFICIENT`

Status: internally prospective synthetic mechanism study. This is not a
real-text, personality, or psychological validation.

## Question

R2 showed that equal scalar residual information can yield very different
power under different interaction geometries. R2B tested whether a finite
geometry operator could explain that difference without changing the frozen
99-draw wild-sign CRC/HC detector.

The scalar model used total residual information, its square, nominal active
authors, and noise mode. The registered operator model added effective author
and cell support, cross-panel spectral concentration, whitened halo leakage,
condition coherence, and effective author-contribution support.

An entire geometry family and a disjoint base-seed fold were absent from every
outer training set. Ridge strength was selected only inside grouped training
folds. Geometry-family names were never predictor features.

## Design integrity

- 1,800 independent base worlds;
- seven paired geometries per base;
- 12,600 rows;
- Gaussian and heteroskedastic \(t_5\) noise;
- \(m=4,8,16\), four active conditions, K=128;
- exact paired scalar-information matching;
- 18,000/18,000 unique source seed streams.

All source-lock, row-count, pairing, seed, numeric, information-match,
operator-identity, and projection checks passed. Maximum scalar-information
matching error was \(6.70\times10^{-16}\).

## Registered results

Paired iid-minus-intrinsic power differences:

| Noise | m | Difference | 95% CI |
| --- | ---: | ---: | ---: |
| Gaussian | 4 | .6767 | [.6233, .7300] |
| Gaussian | 8 | .2100 | [.1633, .2567] |
| \(t_5\) | 4 | .6167 | [.5600, .6733] |
| \(t_5\) | 8 | .1833 | [.1400, .2267] |

The geometry operator improved out-of-family prediction over the scalar
model:

- log-loss gain: .04650, 95% CI [.03671, .05655];
- Brier gain: .02228, 95% CI [.01893, .02566];
- intrinsic-zero-sum log-loss gain: .26359, 95% CI [.23960, .28651].

Held-out family calibration:

| Family | Observed power | Scalar prediction | Operator prediction | Operator absolute error |
| --- | ---: | ---: | ---: | ---: |
| author concentrated | .909 | .839 | .842 | .068 |
| balanced antiphase | .669 | .879 | .699 | .030 |
| condition concentrated | .898 | .841 | .969 | .071 |
| halo sweep | .913 | .839 | .731 | **.183** |
| iid halo | .919 | .838 | .928 | .009 |
| intrinsic zero sum | .638 | .884 | .723 | .085 |
| rank-one coherent | .997 | .825 | .973 | .024 |

## Why the result is partial

The predeclared effective sign-support coefficient was not identified:

\[
\hat\beta_{\mathrm{sign}}=-3.819,\qquad
95\%\,CI=[-13.703,6.064].
\]

Both mechanism panels contain the same stable planted interaction under
positive precision weighting. Consequently author cross-panel contributions
are almost always positive, sign coherence is essentially one, and effective
sign support is nearly collinear with effective author-energy support. The
failed coefficient is not evidence of a negative sign-support effect; it is
evidence that the registered design could not separate the two quantities.

The halo family also exposed a discontinuous randomization-resolution
boundary. At \(m=4,\lambda=0\), CRC-or-HC power was .127, but at
\(\lambda=.03\) it was 1.000. Observed CRC magnitude barely changed; the
author-level wild-sign orbit and its attainable Holm-adjusted p-values did.
The additive logistic meta-model had no coordinate for that discrete orbit.

## Bounded post-hoc diagnostic

An outcome-informed coordinate reduction was run only to choose the next
experiment. Retaining whitened halo leakage alone, in addition to the scalar
model, yielded out-of-family point estimates:

- log-loss gain .10282;
- Brier gain .04118;
- maximum family calibration error .08880.

This is not confirmation and may not be promoted. It indicates that the next
prospective object should model the randomization orbit and support
filtration directly, rather than add more correlated summary coordinates.
The current leakage coordinate also uses known planted support and is not
yet an observable real-text statistic.

## Scientific conclusion

Supported:

\[
\mathcal I_M(Q_1)=\mathcal I_M(Q_2)
\centernot\Rightarrow
P_D(Q_1)=P_D(Q_2),
\]

and a small set of geometry descriptors improves prediction of frozen
detector power across unseen synthetic families.

Not supported:

- that the six-coordinate operator is sufficient;
- that the registered sign-support axis is separately identified;
- universal cross-geometry calibration;
- an observable real-text geometry operator;
- any personality, construct, diagnostic, causal, or clinical claim.

## Artifacts

- `docs/V8_GEOMETRY_INFORMATION_OPERATOR_V37H4D_R2B_PLAN.md`
- `configs/v8_geometry_information_operator_v37h4d_r2b.json`
- `configs/v8_geometry_information_operator_v37h4d_r2b_analysis.json`
- `suica_core/v8_geometry_information_operator.py`
- `scripts/run_suica_v8_geometry_information_operator_v37h4d_r2b.py`
- `scripts/analyze_suica_v8_geometry_information_operator_v37h4d_r2b.py`
- `results/v8_geometry_information_operator/v37h4d_r2b_discovery_12600rows_20260727/`
- `results/v8_geometry_information_operator/v37h4d_r2b_logo_audit_20260727/`
