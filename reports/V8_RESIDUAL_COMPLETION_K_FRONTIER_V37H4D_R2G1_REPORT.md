# V8 V3.7H.4D-R2G.1 Score-Resolution Limit

Date: 2026-07-27

Machine gate:
`V8_R2G1_PASS_FACTOR_COMPLETENESS_LIMIT`

Scientific decision:
`PARTIAL_CONSTRUCTIVE_EXISTENCE`

## Question

R2G showed that known completable structure had an oracle-zero residual but
the learned \(K=4\) factor score retained a floor. R2G.1 tested whether this
gap disappears as score observation becomes exact:

\[
K_s\in\{1,4,16,64,\infty\}.
\]

Target resolution remained fixed at four. Thirty paired roots were run under
Gaussian and standardized Student-\(t_5\) noise, using both 32 and 128
training groups. The 3,360 source streams were unique; latent factors and
target observations were deliberately held common across \(K_s\) within a
root.

## Primary results

The following values use 128 training groups and report mean learned
cross-view population-floor ratio.

| World | Noise | \(K=1\) | \(K=4\) | \(K=16\) | \(K=64\) | \(K=\infty\) |
|---|---|---:|---:|---:|---:|---:|
| linear common | Gaussian | .05084 | .02240 | .00418 | .00049 | .00009 |
| linear common | \(t_5\) | .05249 | .02334 | .00466 | .00086 | .00049 |
| nonlinear common | Gaussian | .05539 | .03809 | .01167 | .00184 | .00014 |
| nonlinear common | \(t_5\) | .05430 | .03731 | .01145 | .00181 | .00024 |
| unavailable shock | Gaussian | .10041 | .10041 | .10041 | .10041 | .10041 |
| unavailable shock | \(t_5\) | .10057 | .10057 | .10057 | .10057 | .10057 |

At \(K=\infty\), confirmation upper bounds were:

| World | Noise | Phi upper | Floor-ratio upper |
|---|---|---:|---:|
| linear common | Gaussian | .00591 | .00114 |
| linear common | \(t_5\) | .00597 | .00179 |
| nonlinear common | Gaussian | .00599 | .00110 |
| nonlinear common | \(t_5\) | .00594 | .00181 |
| pure iid | Gaussian | .00584 | .00049 |
| pure iid | \(t_5\) | .00582 | .00100 |

All are far inside the registered practical-zero thresholds of `.02` and
`.01`. The same practical-zero thresholds were already passed descriptively
at \(K=64\). The score-unavailable shock retained lower floor bounds of
`.0871` and `.0930`, so the system did not create false completeness.

## Resolution law

After subtracting the directly observed infinite-resolution floor, the
empirical finite-\(K\) decay was approximately:

\[
b(K)-b(\infty)\propto K^{-\alpha}.
\]

Across \(K=1,4,16,64\):

| World | Gaussian \(\alpha\) | \(t_5\) \(\alpha\) |
|---|---:|---:|
| linear common | 1.17 | 1.19 |
| nonlinear common | .84 | .85 |

Over \(K=4,16,64\), the local exponents increased to approximately
`1.45-1.49` for the linear map and `1.12-1.14` for the nonlinear map. These
are empirical finite-range rates, not universal constants.

## Theoretical update

Let

\[
\Delta_{K,m}=S_{\mathrm{omit}}-\widehat S_{K,m}.
\]

The registered synthetic results support:

\[
R_{K,m}
=
\underbrace{\Delta_{K,m}}_
{\text{factor measurement/estimation error}}
+
\underbrace{U}_{\text{unavailable common structure}}
+
\underbrace{\varepsilon}_{\text{independent target noise}}.
\]

For authors aggregated inside one group:

\[
M(n;K,m)
=
b_{\mathrm{joint}}(K,m)+\frac{a}{n}+o(n^{-1}),
\]

where the common term is generally:

\[
b_{\mathrm{joint}}(K,m)
=
b_U+b_\Delta(K,m)
+2E\langle U,\Delta^c_{K,m}\rangle.
\]

The additive expression \(b_U+b_\Delta\) is valid only when the unavailable
component and factor-completion error are orthogonal.

The experiment directly established, inside the registered synthetic class:

\[
b_\Delta(K_s=\infty,m=128)
<\delta_{\mathrm{practical}}
\]

for the registered linear and quadratic score-sufficient worlds. Standard
consistency arguments would extend this to \(m\to\infty\) under correct model
specification, but that limit was not empirically tested.

If a society averages \(G\) independent groups with \(n\) authors each, the
appropriate hierarchy is:

\[
M(G,n;K,m)
=
b_{\mathrm{soc}}(K,m)
+\frac{b_{\mathrm{group}}(K,m)}{G}
+\frac{a_{\mathrm{author}}(K,m)}{Gn}
+o((Gn)^{-1}).
\]

R2G.1 changed \(n\), not \(G\). Its fitted floor is therefore a
group-common floor. The planted group factor would itself average down if
the number of independent groups increased.

This directly supports the user's possibility in a restricted form:

> In a score-sufficient synthetic world, a non-zero within-group residual
> floor can result from finite measurement of a shared factor rather than an
> irreducible error. At high score resolution, a frozen low-complexity map can
> recover that planted structure on fresh groups.

## Boundaries

The result does not prove exact zero, complete real-text factors, social-scale
zero across \(G\to\infty\), or psychological meaning. `K=infinity` is an
ideal noiseless factor observation; target noise and individual residual
energy remain, and cross-view \(R^2\) is only about `.10`.

The positive worlds were constructed so that the frozen linear/quadratic
families contain the correct map. R2G.1 is therefore an estimator-capability
and constructive-existence result, not discovery of unknown clean SUICA
factors. Real text may also have non-ergodic state, condition selection,
representation misspecification, and unavailable common causes.

The reported `lo/hi` values are empirical root quantiles, not simultaneous
confidence or tolerance bounds. The margins are large and all observed
infinite-resolution completable roots had phi below `.0061` and floor ratio
below `.0021`, but a paper-grade confirmation still needs a registered
simultaneous inference procedure. The finite-range \(\alpha\) values remain
descriptive.

The next real-data test should estimate the same frontier using independent
comment subsets per author while keeping centers and factor maps frozen. It
must be described as a real-text approximation to \(K\), not as literal
repeated measurements of an unchanged person.

## Artifacts

- `docs/V8_RESIDUAL_COMPLETION_K_FRONTIER_V37H4D_R2G1_PLAN.md`
- `configs/v8_residual_completion_k_frontier_v37h4d_r2g1.json`
- `scripts/run_suica_v8_residual_completion_k_frontier_v37h4d_r2g1.py`
- `results/v8_residual_completion_frontier/v37h4d_r2g1_k_frontier_30rep_20260727/`
- `reports/V8_RESIDUAL_COMPLETION_K_FRONTIER_V37H4D_R2G1_INDEPENDENT_MATH_AUDIT.md`
