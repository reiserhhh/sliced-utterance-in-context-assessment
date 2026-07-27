# V8 V3.7H.4D R2 Minority Information Frontier

Date: 2026-07-27

Discovery decision:
`V8_MINORITY_INFORMATION_FRONTIER_V37H4D_R2_DISCOVERY_M90_SELECTED`

Mechanism decision:
`V8_H4D_R2_RANDOM_SUPPORT_EXPLAINED_SCALAR_INFORMATION_GEOMETRY_REFUTED`

Status: internal prospective synthetic discovery; not a real-text or
psychological validation.

## Question

H4D-R1 detected minority-local structure in 91/100 Gaussian and 83/100
heavy-tail cells. Random allocation had placed only about 3.8 active authors
in missed test panels and 6.8 in detected panels. R2 separated:

1. realized minority support;
2. global-energy versus active-cell-SNR normalization;
3. scalar residual information;
4. residual geometry after the frozen centering operator.

The R1 detector remained unchanged: 99 author-level wild-sign draws, CRC,
cross-panel rank-three concentration, Higher Criticism, and Holm alpha .05.

## Design and integrity

- 256 authors; 128/64/64 train/calibration/test;
- 16 conditions, 6 dimensions, 4 panels, primary K=128;
- fixed test support \(m=2,4,8,16\);
- random support with \(4m\) authors drawn from all 256;
- four condition-quartile-balanced active conditions;
- Gaussian and variance-standardized heteroskedastic \(t_5\);
- global effect share .20 and active-cell SNR 15.0 arms;
- iid sparse block plus intrinsic-zero-sum counterexample;
- 11,000 Monte Carlo rows and 33,000/33,000 unique seeds.

Row count, numeric integrity, support count, source provenance, artifact
inventory, and grand-mean projection compatibility all passed. Maximum
projection difference was \(3.55\times10^{-15}\).

## Fixed-support frontier

CRC-or-HC power:

| Arm | Noise | m=2 | m=4 | m=8 | m=16 |
| --- | --- | ---: | ---: | ---: | ---: |
| Global share | Gaussian | .627 | .850 | .977 | 1.000 |
| Global share | \(t_5\) | .647 | .853 | .987 | 1.000 |
| Active SNR | Gaussian | .227 | .763 | 1.000 | 1.000 |
| Active SNR | \(t_5\) | .240 | .770 | .990 | 1.000 |

Both planted families selected \(m=8\) under the discovery rule requiring
power at least .93 at the candidate and all larger support values in both
noise modes.

Within the fixed iid active-SNR family, the standardized logistic slopes of
power against \(\log(1+\mathcal I_R)\) were:

- Gaussian: 3.008 [2.636, 3.379];
- \(t_5\): 2.721 [2.393, 3.049].

This is a within-family relation, not a universal scalar threshold.

## Random-support transport

Random support retained the full hypergeometric distribution, including
\(M_T=0\) zero-information cells. A logistic curve fitted only on fixed iid
cells predicted aggregate random-support power:

| Arm | Noise | Observed | Predicted | Difference 95% CI |
| --- | --- | ---: | ---: | ---: |
| Global share | Gaussian | .795 | .769 | [.009, .044] |
| Global share | \(t_5\) | .790 | .798 | [-.026, .010] |
| Active SNR | Gaussian | .728 | .728 | [-.015, .016] |
| Active SNR | \(t_5\) | .731 | .728 | [-.013, .018] |

All intervals remained inside the registered +/- .05 prediction band.
Realized support and residual information therefore explain the R1 random
split instability within the iid planted family.

## Geometry counterexample

The intrinsic-zero-sum structure carried comparable or greater scalar
residual information but substantially lower power:

| Noise | m | Intrinsic/IID information | IID power | Intrinsic power | Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| Gaussian | 4 | 1.086 | .763 | .095 | -.668 |
| Gaussian | 8 | 1.086 | 1.000 | .810 | -.190 |
| \(t_5\) | 4 | 1.060 | .770 | .145 | -.625 |
| \(t_5\) | 8 | 1.081 | .990 | .760 | -.230 |

IID centering retained about .923 of signal energy and spread about
.061-.065 of residual energy outside the intended active block. Intrinsic
zero-sum retained 1.000 and had effectively zero halo.

Therefore:

\[
\mathcal I_R(Q_1)\approx\mathcal I_R(Q_2)
\not\Rightarrow
P_D(Q_1)\approx P_D(Q_2).
\]

For this author-level sign-randomized detector, effective author sign support,
cell sparsity, spectral concentration, and centering halo matter in addition
to total whitened energy.

## W0 scope

Discovery W0 was 5/300 Gaussian and 10/300 \(t_5\), with simultaneous upper
bounds .0385 and .0604. The latter reflected discovery precision and was not
used as a confirmation result. R2A therefore used 1,000 fresh W0 repetitions
per noise.

## Decision

The valid discovery conclusion is:

> In the registered iid sparse-Q family, realized minority support and
> residual information explain random-split power, and \(m=8\) is a valid
> prospective confirmation candidate. A scalar information budget is not
> sufficient across residual geometries.

The result does not establish a universal minority boundary, non-low-rank
geometry, psychological meaning, or real-text validity.

## Artifacts

- `docs/V8_MINORITY_INFORMATION_FRONTIER_V37H4D_R2_PLAN.md`
- `configs/v8_minority_information_frontier_v37h4d_r2.json`
- `suica_core/v8_minority_information_frontier.py`
- `scripts/run_suica_v8_minority_information_frontier_v37h4d_r2.py`
- `scripts/analyze_suica_v8_minority_information_frontier_v37h4d_r2.py`
- `results/v8_minority_information_frontier/v37h4d_r2_discovery_11000rep_20260727/`
- `results/v8_minority_information_frontier/v37h4d_r2_mechanism_audit_20260727/`
