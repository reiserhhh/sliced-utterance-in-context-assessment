# V8 Residual Geometry Correspondence

Status: `NONLINEAR_RESIDUAL_GEOMETRY`

The experiment compares author-by-author relation matrices after the exchangeable M background quotient, D0-frozen declared-opportunity coordinate filtration, and replicate-specific nuisance-kernel conditioning. It asks whether geometry survives without a stable global factor axis.

## Decision

```json
{
  "status": "RESIDUAL_GEOMETRY_CORRESPONDENCE_COMPLETED",
  "overall_geometry_status": "NONLINEAR_RESIDUAL_GEOMETRY",
  "corpus_status": {
    "pandora": "SCALAR_CONCORDANCE_ONLY",
    "essays": "NONLINEAR_RESIDUAL_GEOMETRY",
    "x_market": "SCALAR_CONCORDANCE_ONLY"
  },
  "filtered_linear_spectrum_status": "NO_REPLICATED_LOW_DIMENSIONAL_AXIS",
  "version": "v8-cbq-rgc-1",
  "timestamp_utc": "2026-07-29T18:47:54.839360+00:00",
  "claim_boundary": "Opened-panel axis-free residual-geometry audit. It tests whether D0-frozen opportunity-filtered technical replicates preserve author-to-author relation geometry under linear kernels, RBF kernels, or local neighborhoods. It cannot establish personality, emotion, cognition, a latent factor, causality, cross-corpus common coordinates, diagnosis, or clinical validity."
}
```

## D0 scale audit

| cell_id                          | corpus   | split   | metric             |   authors |     observed |    null_mean |       excess |   raw_p |   bootstrap_lcb |   delta_excess_vs_linear |   delta_bootstrap_lcb |   max_t_p |   delta_max_t_p |
|:---------------------------------|:---------|:--------|:-------------------|----------:|-------------:|-------------:|-------------:|--------:|----------------:|-------------------------:|----------------------:|----------:|----------------:|
| pandora::D0::linear_krc          | pandora  | D0      | linear_krc         |        81 | -0.00720179  | -0.00161657  | -0.00558522  |    0.51 |             nan |             nan          |                   nan |       nan |             nan |
| pandora::D0::rbf_krc_0.5         | pandora  | D0      | rbf_krc_0.5        |        81 |  0.0264009   | -0.00103938  |  0.0274403   |    0.2  |             nan |               0.0330255  |                   nan |       nan |             nan |
| pandora::D0::rbf_krc_1           | pandora  | D0      | rbf_krc_1          |        81 | -0.000322933 | -0.00128294  |  0.000960004 |    0.48 |             nan |               0.00654522 |                   nan |       nan |             nan |
| pandora::D0::rbf_krc_2           | pandora  | D0      | rbf_krc_2          |        81 | -0.00567888  | -0.00152193  | -0.00415694  |    0.52 |             nan |               0.00142828 |                   nan |       nan |             nan |
| pandora::D0::local_overlap_0.05  | pandora  | D0      | local_overlap_0.05 |        81 |  0           |  0.0452675   | -0.0452675   |    1    |             nan |             nan          |                   nan |       nan |             nan |
| pandora::D0::local_overlap_0.1   | pandora  | D0      | local_overlap_0.1  |        81 |  0.0308642   |  0.100075    | -0.0692106   |    0.89 |             nan |             nan          |                   nan |       nan |             nan |
| pandora::D0::local_overlap_0.2   | pandora  | D0      | local_overlap_0.2  |        81 |  0.120635    |  0.195575    | -0.0749399   |    0.92 |             nan |             nan          |                   nan |       nan |             nan |
| essays::D0::linear_krc           | essays   | D0      | linear_krc         |        61 |  0.0773816   |  0.000961019 |  0.0764206   |    0.01 |             nan |             nan          |                   nan |       nan |             nan |
| essays::D0::rbf_krc_0.5          | essays   | D0      | rbf_krc_0.5        |        61 |  0.102121    |  0.00168861  |  0.100432    |    0.01 |             nan |               0.0240118  |                   nan |       nan |             nan |
| essays::D0::rbf_krc_1            | essays   | D0      | rbf_krc_1          |        61 |  0.0843385   |  0.00113095  |  0.0832075   |    0.01 |             nan |               0.00678695 |                   nan |       nan |             nan |
| essays::D0::rbf_krc_2            | essays   | D0      | rbf_krc_2          |        61 |  0.079132    |  0.00100436  |  0.0781276   |    0.01 |             nan |               0.00170705 |                   nan |       nan |             nan |
| essays::D0::local_overlap_0.05   | essays   | D0      | local_overlap_0.05 |        61 |  0.0655738   |  0.0597229   |  0.00585086  |    0.37 |             nan |             nan          |                   nan |       nan |             nan |
| essays::D0::local_overlap_0.1    | essays   | D0      | local_overlap_0.1  |        61 |  0.18306     |  0.108103    |  0.0749572   |    0.18 |             nan |             nan          |                   nan |       nan |             nan |
| essays::D0::local_overlap_0.2    | essays   | D0      | local_overlap_0.2  |        61 |  0.325137    |  0.202696    |  0.12244     |    0.03 |             nan |             nan          |                   nan |       nan |             nan |
| x_market::D0::linear_krc         | x_market | D0      | linear_krc         |        42 |  0.306208    | -0.00389662  |  0.310105    |    0.01 |             nan |             nan          |                   nan |       nan |             nan |
| x_market::D0::rbf_krc_0.5        | x_market | D0      | rbf_krc_0.5        |        42 |  0.25443     | -0.00298966  |  0.25742     |    0.01 |             nan |              -0.0526854  |                   nan |       nan |             nan |
| x_market::D0::rbf_krc_1          | x_market | D0      | rbf_krc_1          |        42 |  0.204427    | -8.15896e-05 |  0.204509    |    0.01 |             nan |              -0.105596   |                   nan |       nan |             nan |
| x_market::D0::rbf_krc_2          | x_market | D0      | rbf_krc_2          |        42 |  0.270525    | -0.00228242  |  0.272807    |    0.01 |             nan |              -0.0372978  |                   nan |       nan |             nan |
| x_market::D0::local_overlap_0.05 | x_market | D0      | local_overlap_0.05 |        42 |  0.238095    |  0.0875421   |  0.150553    |    0.02 |             nan |             nan          |                   nan |       nan |             nan |
| x_market::D0::local_overlap_0.1  | x_market | D0      | local_overlap_0.1  |        42 |  0.275862    |  0.12278     |  0.153083    |    0.02 |             nan |             nan          |                   nan |       nan |             nan |
| x_market::D0::local_overlap_0.2  | x_market | D0      | local_overlap_0.2  |        42 |  0.482456    |  0.220096    |  0.26236     |    0.02 |             nan |             nan          |                   nan |       nan |             nan |

## Held-out D1/D2

| cell_id                          | corpus   | split   | metric             |   authors |    observed |    null_mean |       excess |   raw_p |   bootstrap_lcb |   delta_excess_vs_linear |   delta_bootstrap_lcb |   max_t_p |   delta_max_t_p |
|:---------------------------------|:---------|:--------|:-------------------|----------:|------------:|-------------:|-------------:|--------:|----------------:|-------------------------:|----------------------:|----------:|----------------:|
| pandora::D1::linear_krc          | pandora  | D1      | linear_krc         |        66 | -0.0792504  |  0.00229209  | -0.0815425   |    0.98 |     -0.228563   |             nan          |          nan          |      1    |          nan    |
| pandora::D1::rbf_krc_0.5         | pandora  | D1      | rbf_krc_0.5        |        66 |  0.0208122  | -0.000219314 |  0.0210315   |    0.38 |     -0.129015   |               0.102574   |           -0.0675259  |      1    |            0.28 |
| pandora::D1::rbf_krc_1           | pandora  | D1      | rbf_krc_1          |        66 | -0.0289796  |  0.00270229  | -0.0316819   |    0.76 |     -0.172028   |               0.0498606  |           -0.0385982  |      1    |            0.38 |
| pandora::D1::rbf_krc_2           | pandora  | D1      | rbf_krc_2          |        66 | -0.0602735  |  0.00257951  | -0.062853    |    0.9  |     -0.204823   |               0.0186895  |           -0.015538   |      1    |            0.34 |
| pandora::D1::local_overlap_0.05  | pandora  | D1      | local_overlap_0.05 |        66 |  0.106061   |  0.0751454   |  0.0309152   |    0.27 |     -0.0759045  |             nan          |          nan          |      1    |          nan    |
| pandora::D1::local_overlap_0.1   | pandora  | D1      | local_overlap_0.1  |        66 |  0.2        |  0.1045      |  0.0955005   |    0.12 |     -0.0454297  |             nan          |          nan          |      0.96 |          nan    |
| pandora::D1::local_overlap_0.2   | pandora  | D1      | local_overlap_0.2  |        66 |  0.272727   |  0.196281    |  0.0764463   |    0.12 |     -0.0344169  |             nan          |          nan          |      0.93 |          nan    |
| pandora::D2::linear_krc          | pandora  | D2      | linear_krc         |        45 |  0.190464   | -0.0065529   |  0.197017    |    0.01 |      0.0197019  |             nan          |          nan          |      0.1  |          nan    |
| pandora::D2::rbf_krc_0.5         | pandora  | D2      | rbf_krc_0.5        |        45 |  0.182276   | -0.00544128  |  0.187718    |    0.01 |     -0.0148901  |              -0.0092994  |           -0.201795   |      0.18 |            1    |
| pandora::D2::rbf_krc_1           | pandora  | D2      | rbf_krc_1          |        45 |  0.162963   | -0.00759809  |  0.170561    |    0.01 |     -0.0311376  |              -0.0264563  |           -0.127223   |      0.19 |            1    |
| pandora::D2::rbf_krc_2           | pandora  | D2      | rbf_krc_2          |        45 |  0.180418   | -0.00722687  |  0.187645    |    0.01 |     -0.00676114 |              -0.00937176 |           -0.0404254  |      0.14 |            1    |
| pandora::D2::local_overlap_0.05  | pandora  | D2      | local_overlap_0.05 |        45 |  0.0444444  |  0.0998878   | -0.0554433   |    0.78 |     -0.102414   |             nan          |          nan          |      1    |          nan    |
| pandora::D2::local_overlap_0.1   | pandora  | D2      | local_overlap_0.1  |        45 |  0.0819672  |  0.125683    | -0.0437158   |    0.75 |     -0.131895   |             nan          |          nan          |      1    |          nan    |
| pandora::D2::local_overlap_0.2   | pandora  | D2      | local_overlap_0.2  |        45 |  0.234694   |  0.204082    |  0.0306122   |    0.36 |     -0.0934594  |             nan          |          nan          |      1    |          nan    |
| essays::D1::linear_krc           | essays   | D1      | linear_krc         |        49 | -0.0141555  | -0.000263185 | -0.0138923   |    0.7  |     -0.126679   |             nan          |          nan          |      1    |          nan    |
| essays::D1::rbf_krc_0.5          | essays   | D1      | rbf_krc_0.5        |        49 |  0.144788   | -0.00674267  |  0.151531    |    0.01 |      0.0551633  |               0.165423   |            0.0354584  |      0.01 |            0.01 |
| essays::D1::rbf_krc_1            | essays   | D1      | rbf_krc_1          |        49 |  0.0304987  | -0.00465277  |  0.0351515   |    0.14 |     -0.0590793  |               0.0490438  |           -0.0119163  |      0.99 |            0.13 |
| essays::D1::rbf_krc_2            | essays   | D1      | rbf_krc_2          |        49 | -0.00182388 | -0.00204106  |  0.000217185 |    0.47 |     -0.0990575  |               0.0141095  |           -0.017303   |      1    |            0.78 |
| essays::D1::local_overlap_0.05   | essays   | D1      | local_overlap_0.05 |        49 |  0.520408   |  0.0584416   |  0.461967    |    0.02 |      0.0321913  |             nan          |          nan          |      0.03 |          nan    |
| essays::D1::local_overlap_0.1    | essays   | D1      | local_overlap_0.1  |        49 |  0.302041   |  0.107772    |  0.194269    |    0.02 |     -0.0523699  |             nan          |          nan          |      0.09 |          nan    |
| essays::D1::local_overlap_0.2    | essays   | D1      | local_overlap_0.2  |        49 |  0.316327   |  0.205504    |  0.110823    |    0.02 |     -0.0482015  |             nan          |          nan          |      0.18 |          nan    |
| essays::D2::linear_krc           | essays   | D2      | linear_krc         |        50 | -0.00795072 | -0.00494552  | -0.00300521  |    0.62 |     -0.0899646  |             nan          |          nan          |      1    |          nan    |
| essays::D2::rbf_krc_0.5          | essays   | D2      | rbf_krc_0.5        |        50 |  0.123043   |  0.00479681  |  0.118246    |    0.01 |      0.0279125  |               0.121251   |            0.00856702 |      0.01 |            0.01 |
| essays::D2::rbf_krc_1            | essays   | D2      | rbf_krc_1          |        50 |  0.0159702  | -0.00173788  |  0.0177081   |    0.27 |     -0.0621663  |               0.0207133  |           -0.0414403  |      1    |            0.83 |
| essays::D2::rbf_krc_2            | essays   | D2      | rbf_krc_2          |        50 | -0.0113488  | -0.00489164  | -0.00645719  |    0.63 |     -0.10065    |              -0.00345199 |           -0.0309039  |      1    |            1    |
| essays::D2::local_overlap_0.05   | essays   | D2      | local_overlap_0.05 |        50 |  0.04       |  0.0411111   | -0.00111111  |    0.54 |     -0.0381461  |             nan          |          nan          |      1    |          nan    |
| essays::D2::local_overlap_0.1    | essays   | D2      | local_overlap_0.1  |        50 |  0.104      |  0.1         |  0.004       |    0.45 |     -0.0560132  |             nan          |          nan          |      1    |          nan    |
| essays::D2::local_overlap_0.2    | essays   | D2      | local_overlap_0.2  |        50 |  0.206      |  0.205111    |  0.000888889 |    0.51 |     -0.0584459  |             nan          |          nan          |      1    |          nan    |
| x_market::D1::linear_krc         | x_market | D1      | linear_krc         |        39 |  0.141658   | -0.007014    |  0.148672    |    0.04 |     -0.104846   |             nan          |          nan          |      0.54 |          nan    |
| x_market::D1::rbf_krc_0.5        | x_market | D1      | rbf_krc_0.5        |        39 |  0.321038   | -0.00611738  |  0.327156    |    0.01 |      0.0523186  |               0.178483   |           -0.0857297  |      0.05 |            0.26 |
| x_market::D1::rbf_krc_1          | x_market | D1      | rbf_krc_1          |        39 |  0.320695   | -0.0062037   |  0.326898    |    0.01 |      0.0514965  |               0.178226   |           -0.0833772  |      0.05 |            0.26 |
| x_market::D1::rbf_krc_2          | x_market | D1      | rbf_krc_2          |        39 |  0.273893   | -0.00574019  |  0.279633    |    0.01 |     -0.00127484 |               0.130961   |           -0.141476   |      0.08 |            0.55 |
| x_market::D1::local_overlap_0.05 | x_market | D1      | local_overlap_0.05 |        39 |  0.333333   |  0.0971251   |  0.236208    |    0.06 |     -0.0936487  |             nan          |          nan          |      0.57 |          nan    |
| x_market::D1::local_overlap_0.1  | x_market | D1      | local_overlap_0.1  |        39 |  0.275862   |  0.117903    |  0.157959    |    0.15 |     -0.0827873  |             nan          |          nan          |      0.93 |          nan    |
| x_market::D1::local_overlap_0.2  | x_market | D1      | local_overlap_0.2  |        39 |  0.336207   |  0.225705    |  0.110502    |    0.06 |     -0.031768   |             nan          |          nan          |      0.88 |          nan    |
| x_market::D2::linear_krc         | x_market | D2      | linear_krc         |        31 |  0.237376   | -0.00121287  |  0.238589    |    0.01 |     -0.0278132  |             nan          |          nan          |      0.18 |          nan    |
| x_market::D2::rbf_krc_0.5        | x_market | D2      | rbf_krc_0.5        |        31 |  0.325714   | -0.00764005  |  0.333354    |    0.01 |      0.0425753  |               0.0947649  |           -0.236294   |      0.09 |            0.9  |
| x_market::D2::rbf_krc_1          | x_market | D2      | rbf_krc_1          |        31 |  0.324918   | -0.00780172  |  0.332719    |    0.01 |      0.0388464  |               0.0941303  |           -0.234896   |      0.09 |            0.9  |
| x_market::D2::rbf_krc_2          | x_market | D2      | rbf_krc_2          |        31 |  0.309843   | -0.0108162   |  0.32066     |    0.01 |     -0.0359531  |               0.0820705  |           -0.235918   |      0.09 |            0.9  |
| x_market::D2::local_overlap_0.05 | x_market | D2      | local_overlap_0.05 |        31 |  0.516129   |  0.113718    |  0.402411    |    0.01 |      0.0303226  |             nan          |          nan          |      0.01 |          nan    |
| x_market::D2::local_overlap_0.1  | x_market | D2      | local_overlap_0.1  |        31 |  0.516129   |  0.113718    |  0.402411    |    0.01 |      0.0303226  |             nan          |          nan          |      0.01 |          nan    |
| x_market::D2::local_overlap_0.2  | x_market | D2      | local_overlap_0.2  |        31 |  0.444444   |  0.185185    |  0.259259    |    0.02 |     -0.00820734 |             nan          |          nan          |      0.16 |          nan    |

## Reading rule

`DISTRIBUTED_LINEAR_GEOMETRY` means linear author-relation kernels repeat despite the absence of a stable low-dimensional axis. `NONLINEAR_RESIDUAL_GEOMETRY` additionally requires one RBF scale to beat linear KRC in both held-out panels. `PERSISTENT_LOCAL_RESIDUAL_GEOMETRY` requires two adjacent neighborhood scales in both panels. All families use one maxT correction. The current panels are opened; fresh D3 is required for promotion.

## Boundary

Opened-panel axis-free residual-geometry audit. It tests whether D0-frozen opportunity-filtered technical replicates preserve author-to-author relation geometry under linear kernels, RBF kernels, or local neighborhoods. It cannot establish personality, emotion, cognition, a latent factor, causality, cross-corpus common coordinates, diagnosis, or clinical validity.
