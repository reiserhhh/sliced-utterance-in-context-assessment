# V8 V3.7H.3 Multiscale Zero-Identification Report

Date: 2026-07-26

Machine gate status:
`V8_MULTISCALE_ZERO_IDENTIFICATION_V37H3_DISCOVERY_PASS`

Scientific decision:
`DISCOVERY_PARTIAL_PASS_ADDITIVE_BALANCED_WORLD_ONLY`

Confirmation status: not sealed and not run.

## Research question

The experiment tested whether society, nested group, author, condition,
author-by-condition response, opportunity, and technical components can be
characterized by different zero and aggregation limits:

\[
X_{sguckr}
=
\mu+S_s+G_{g|s}+A_{u|gs}+H_c+B_{u,c}
+U_{sguck}+\varepsilon_{sguckr}.
\]

The valid target was not "all social-scale error vanishes." The registered
target was narrower:

> In a balanced additive synthetic world, can component-preserving
> projections, repeated opportunities, and aggregation rates distinguish
> independent, common, and mixed sources?

## Design

- 60 independent repetitions;
- Gaussian and heteroskedastic standardized \(t_5\) noise;
- 8 societies, 4 groups per society, 8 authors per group;
- 6 conditions, 4 opportunities, 2 technical streams;
- 6 score dimensions and 2 independent opportunity panels;
- recovery checked at \(K=2,3,4\);
- symmetric zero paths at \(\lambda=.125,.25,.5,1\);
- separate selection, projection-commutator, persistent-alias,
  coarse-graining, and minority-by-near-kernel assays.

Integrity:

- 23,520 zero-path rows;
- 2,520 recovery rows;
- 1,800 coarse-graining rows;
- 60 selection and 60 persistent-alias rows;
- 1,500 minority-by-near-kernel rows;
- 360/360 unique RNG seeds;
- run manifest and artifact inventory passed;
- maximum algebraic reconstruction error
  \(1.78\times10^{-15}\);
- full repository regression: 559 tests passed.

## Finite-sample recovery

The weakest stable component was the author-by-condition response. Minimum
performance across both noise modes and all five stable components was:

| Opportunity repeats | Minimum mean recovery \(R^2\) | Minimum split-panel \(r\) |
| ---: | ---: | ---: |
| 2 | .9112 | .8494 |
| 3 | .9409 | .8940 |
| 4 | .9556 | .9184 |

The K=4 gate passed under both Gaussian and heteroskedastic \(t_5\) noise.
This is nontrivial finite-sample evidence that opportunity replication
improves separation when the registered additive model is correct.

It is not evidence that the same decomposition exists in real text.

## Zero signatures

The symmetric functional was:

\[
Z_{mj}(\lambda)
=
\frac{T_m(X+\lambda F_j)+T_m(X-\lambda F_j)}2-T_m(X).
\]

All diagonal slopes were numerically 2.000. Maximum off-diagonal leakage was
.000743.

This is primarily an algebra and implementation result. With a linear planted
path and a quadratic energy functional, the symmetric construction is
supposed to remove first-order cross terms and leave a
\(\lambda^2\) term. It validates the implemented coordinate system; it does
not independently demonstrate that unknown real-text components follow the
same law.

## Aggregation flow

| Component family | Log-log slope |
| --- | ---: |
| Independent authors into group mean | -1.0003 |
| Author ICC=.30 into group mean | -0.2052 |
| Group-common across authors | 0.0000 |
| Independent groups into society mean | -0.9999 |
| Society-common across groups | 0.0000 |

The important result is not the planted \(-1\) and 0 laws by themselves. It
is the registered counterexample at ICC=.30:

\[
\operatorname{Var}(\bar A_n)
=
\sigma_A^2\left[\rho+\frac{1-\rho}{n}\right].
\]

Aggregation removed the independent part but approached a common-structure
floor. Therefore increasing population size cannot by itself make all
non-personal structure vanish.

## Selection and noncommuting projections

Author-dependent condition choice created a strong direction reversal:

- naive selected-text author correlation: mean \(r=-.9072\);
- balanced condition-standardized correlation: mean \(r=.9972\);
- reversal in 60/60 repetitions;
- direction recovery in 60/60 repetitions.

The empirical group/condition projection commutator was:

- selected design: mean .4722;
- balanced product design: \(4.67\times10^{-17}\).

This shows that sampling measure and condition choice can determine projection
order. It does not establish a causal psychological interaction. The repair
also relied on registered positivity: every author had forced observations in
every condition.

## Non-identification boundaries

### Persistent cause alias

Persistent author response and persistent schedule confound had identical
observations:

- maximum identity error: 0;
- required classification: `CAUSE_UNIDENTIFIED`.

### Minority by near-kernel attenuation

The synthetic geometry satisfied:

\[
\eta_{\mathrm{observable}}
=p\alpha\eta_{\mathrm{individual}}
\]

to machine precision. This is a construction identity, but it records an
important operating boundary: a strong affected-author response can be almost
invisible to a population score when prevalence \(p\) or scorer-visible
fraction \(\alpha\) is small.

## What was established

Within the frozen balanced additive worlds:

1. the hierarchical projection is algebraically consistent;
2. stable components remain recoverable under finite opportunity and
   technical noise;
3. additional opportunity repeats improve the weakest stable response;
4. independent and common components have different aggregation flow;
5. intraclass dependence creates a non-vanishing aggregation floor;
6. condition selection can reverse author position;
7. a balanced reference design can repair that registered reversal;
8. persistent observational aliases must be refused.

## What was not established

- social-scale residuals do not generally converge to zero;
- components are not independently identifiable without a known hierarchy,
  positivity, crossed conditions, and a correctly specified interaction
  space;
- exact reconstruction does not prove correct attribution;
- the current result does not cover nonlinear interactions, dependent or
  non-ergodic opportunity processes, unknown levels, missingness, real text,
  personality meaning, causal interpretation, or clinical use;
- the dirty development tree and reused development protocol are not a sealed
  confirmation.

## Decision

The correct interpretation is:

> V3.7H.3 establishes internally consistent finite-sample identification in a
> balanced additive multiscale synthetic world. It partially supports the
> idea that components can be defined by their disappearance and persistence
> rates. It refutes the unrestricted statement that all social-scale error
> vanishes or that every component can always be solved independently.

The next discovery gate should be a nonadditive misspecification adversary.
It must use a nonlinear author-by-condition response and an author-correlated,
non-ergodic opportunity process while deliberately fitting the current
additive H.3 estimator. The required new capability is not high
reconstruction; it is an explicit `MODEL_INADEQUATE` refusal before false
author or condition attribution.

## Artifacts

- `docs/V8_MULTISCALE_ZERO_IDENTIFICATION_V37H3_PLAN.md`
- `configs/v8_multiscale_zero_identification_v37h3.json`
- `suica_core/v8_multiscale_zero_identification.py`
- `scripts/run_suica_v8_multiscale_zero_identification_v37h3.py`
- `tests/test_v8_multiscale_zero_identification_v37h3.py`
- `results/v8_multiscale_zero_identification/v37h3_discovery_60rep_20260726/`
