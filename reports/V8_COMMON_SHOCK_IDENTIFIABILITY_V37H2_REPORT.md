# V8 V3.7H.2 Common-Shock Identifiability Report

Date: 2026-07-26

Final design decision:
`REPEATED_OPPORTUNITY_IDENTIFICATION_PASS_WITH_REPLICATION_BOUNDARY`

Confirmation status: closed.

## Why this experiment was necessary

V3.7H.1 R4 uses two technical streams within each schedule. Under conditional
stream independence, their half-difference estimates technical noise. A shock
shared by both streams is absent from that contrast and can be mistaken for a
stable author-by-schedule response.

V3.7H.2 introduced a second replication level:

- \(r\): technical streams within one opportunity occasion;
- \(k\): repeated opportunity occasions under the same schedule.

The synthetic endpoint model is:

\[
Y_{uskr}
=
W\left[
\mu_0+G_u+\delta_sg(G_u)+C_{usk}+H_{us}
+\sigma_u\epsilon_{uskr}
\right].
\]

\(C_{usk}\) is a transient common shock. \(H_{us}\) is persistent within an
author and schedule.

## Estimators

The legacy estimator subtracts only within-occasion technical disagreement:

\[
Q_K^{legacy}
=
\frac{
\mathbb E\|\bar Y_B-\bar Y_A\|^2
-\widehat V_{\mathrm{stream},K}
}{S_{\mathrm{score}}}.
\]

For \(K\ge2\), V3.7H.2 estimates the variance of opportunity-replicate means:

\[
\widehat V_{\mathrm{occasion},K}
=
\mathbb E_u\left[
\frac{s^2_{uA}}K+\frac{s^2_{uB}}K
\right],
\]

\[
Q_K^{rep}
=
\frac{
\mathbb E\|\bar Y_B-\bar Y_A\|^2
-\widehat V_{\mathrm{occasion},K}
}{S_{\mathrm{score}}}.
\]

The author-centered form removes a global schedule mean:

\[
Q_{K,\mathrm{author}}^{rep}
=
\frac{
d^{-1}\sum_j\operatorname{Var}_u(D_{uj})
-\widehat V_{\mathrm{occasion},K}
}{S_{\mathrm{score}}}.
\]

\(K=1\) is explicitly unidentifiable.

## D1 broad frontier

D1 tested:

- \(K=1,2,4,8\);
- stream correlation \(0,.3,.6\);
- common-shock score energy \(0,.01,.05\);
- Gaussian and heteroskedastic standardized \(t_5\) noise;
- response score energy \(0,.02,.10\);
- 100 repetitions in each of 216 cells.

Integrity:

- 21,600 metric rows;
- 22,100 unique RNG streams;
- all numeric and identification contracts passed.

Seven of eight gates passed. The sole failure was the familywise null upper
bound:

- worst cell: \(K=2,\rho=.6,c=.05,t_5,\eta=0\);
- 2/100 refusals;
- Bonferroni one-sided upper .1081 versus registered .10.

This was not mean bias. The cell mean was -.000684 and the simultaneous bias
interval was [-.00242, .00105]. All 54 material cells at \(\eta=.10\)
were 100/100, with minimum familywise lower .9325.

The legacy estimator was directly refuted:

- contaminated-null refusal rate: 92.03%;
- repeated estimator contaminated-null refusal rate: 4/5,400;
- Gaussian maximum simultaneous absolute bias bound: .00187;
- heavy-tail maximum simultaneous absolute bias bound: .00284.

## D2 focused tail audit

D2 was frozen before execution with fresh seeds. It did not combine D1 data,
change \(Q=.01\), or relax a gate. Instead it:

- added \(K=3\);
- fixed the worst frontier at \(\rho=.6,c=.05\);
- retained Gaussian and heteroskedastic \(t_5\);
- ran \(\eta=0,.02,.10\);
- used 1,000 repetitions per cell;
- tightened false-refusal upper from .10 to .05;
- tightened material-power lower from .80 to .90.

Integrity:

- 30,000 metric rows;
- 35,000 unique RNG streams;
- 1,000 global-shift and causal-alias assays;
- all manifests and numeric contracts passed.

### Null calibration

| \(K\) | Gaussian | Heteroskedastic \(t_5\) | Worst familywise upper |
| ---: | ---: | ---: | ---: |
| 2 | 1/1000 | 11/1000 | .02224 |
| 3 | 0/1000 | 0/1000 | .00506 |
| 4 | 0/1000 | 0/1000 | .00506 |
| 8 | 0/1000 | 0/1000 | .00506 |

### Power

- \(\eta=.10\): every identified cell was 1000/1000;
- familywise one-sided lower: .99494;
- \(\eta=.02\), \(K=2\): Gaussian 998/1000, heavy-tail 986/1000;
- \(\eta=.02\), \(K\ge3\): all cells 1000/1000.

### Bias

- maximum Gaussian simultaneous absolute bias bound: .000633;
- maximum heavy-tail simultaneous absolute bias bound: .000584;
- pooled mean error: \(-2.1\times10^{-6}\);
- pooled RMSE: .00279.

## Replication law

Under the focused worst-case frontier, legacy null bias followed:

\[
\mathbb E Q_K^{legacy}\approx\frac{b}{K}.
\]

Empirical log-log slopes were:

- Gaussian: -0.9994;
- heteroskedastic \(t_5\): -1.0003.

Thus averaging more occasions attenuates legacy contamination but does not
identify or remove it at finite \(K\).

For the repeated estimator, null standard deviation followed approximately:

\[
\operatorname{sd}(Q_K^{rep})\propto K^{-1.12}.
\]

Empirical slopes:

- Gaussian: -1.1169, \(R^2=.9994\);
- heteroskedastic \(t_5\): -1.1313, \(R^2=.9996\).

This gives SUICA a concrete replication theory:

> technical replication estimates scorer noise; opportunity replication
> identifies transient condition noise; additional occasions contract the
> refusal statistic's tail uncertainty.

## Global shift and causal alias

The author-centered statistic correctly separated a global fixed schedule
shift:

- total \(Q\) mean: .09999;
- author-centered \(Q\) mean: .000013;
- total detection: 1000/1000, familywise lower .9963;
- author detection: 0/1000, familywise upper .00368.

Persistent response and persistent schedule confound were constructed with
identical observations:

- maximum data identity error: 0.

The only valid conclusion is:

`SCHEDULE_SENSITIVITY_IDENTIFIED_CAUSE_UNIDENTIFIED`.

No observational estimator can assign a psychological cause when the
likelihoods are identical.

## Operating boundary

- \(K=1\): mathematically unidentifiable;
- \(K=2\): validated minimum identifiable configuration, with a 1.1% observed
  false-refusal tail in the worst heavy-tail cell;
- \(K=3\): validated minimum robust configuration, with 0/1000 false refusals
  in both noise modes;
- \(K=4\): recommended confirmation default because it passed both the
  original broad grid and the focused tail audit with lower uncertainty and a
  more symmetric repeated design;
- \(K=8\): lower uncertainty, not required by current synthetic evidence.

The validated minimum is therefore \(K\ge3\), while \(K=4\) remains the
recommended default for a sealed synthetic confirmation. \(K=2\) is the
validated minimum identifiable low-cost configuration.

## What is now established

Within the registered synthetic worlds:

1. technical-stream replication alone cannot remove shared opportunity
   shocks;
2. repeated opportunity occasions yield an approximately unbiased
   score-space schedule-sensitivity estimator;
3. total and author-relative schedule effects can be separated;
4. replication depth controls tail uncertainty;
5. persistent causal source remains non-identifiable without a stronger
   intervention.

Not established:

- robustness to pairing errors or informative missing occasions;
- minority-only response;
- near-kernel response hidden by the frozen scorer;
- transient or reversing response with zero endpoint;
- real token routing, real text, personality meaning, or clinical validity.

The D2 method and gates are sufficiently specified to seal a bounded
synthetic confirmation with \(K=4\) primary, \(K=3\) minimum, and \(K=2\)
boundary control. That confirmation has not started: the implementation must
first be committed, hashed, externally timestamped, and assigned a fresh
unseen seed.

The next discovery priority is a minority-by-near-kernel frontier. Mean
schedule energy can miss a large response affecting only a small author
fraction, especially when the response lies in a low-gain direction of the
frozen score operator.

## Reproducibility

D1:
`results/v8_common_shock_frontier/v37h2_power_100rep_20260726/`

D2:
`results/v8_common_shock_frontier/v37h2_d2_tail_power_1000rep_20260726/`

Plan:
`docs/V8_COMMON_SHOCK_IDENTIFIABILITY_V37H2_PLAN.md`

Core:
`suica_core/v8_common_shock_frontier.py`

Runner:
`scripts/run_suica_v8_common_shock_frontier_v37h2.py`
