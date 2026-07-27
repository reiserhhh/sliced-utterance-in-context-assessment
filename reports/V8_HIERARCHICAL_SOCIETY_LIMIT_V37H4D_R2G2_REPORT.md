# V8 R2G.2 Hierarchical Society-Limit Frontier

Date: 2026-07-27

## Ruling

- Original 30-root R2G.2 machine decision:
  `V8_R2G2_PARTIAL_INDEPENDENT_ONLY`.
- Independent 80-root R2G.2A decision:
  `V8_R2G2A_PASS_HEAVY_TAIL_PRECISION`.
- Combined scientific ruling:
  `SUPPORTED_SYNTHETIC_HIERARCHICAL_FORMULA_WITH_IDENTIFIABILITY_BOUNDARY`.

R2G.2A resolves the one heavy-tail precision endpoint. It does not overwrite
or pool the original R2G.2 roots.

## Finite-design identity

Use the per-coordinate Hilbert inner product. If cross-view residuals admit
the nested martingale-difference representation:

\[
R_{sgi}^{v}
=
D_s^{S,v}+D_{sg}^{G,v}+D_{sgi}^{A,v}+\varepsilon_{sgi}^{v},
\]

and the registered groups and authors are independent at their respective
levels, then:

\[
M_\times(G,n)
=
E\langle\bar R_{G,n}^{A},\bar R_{G,n}^{B}\rangle
=
b_S+\frac{b_G}{G}+\frac{b_A}{Gn}.
\]

This is a finite-design projection identity. It is not a claim that real
society, group, and person processes are independent.

For stationary AR(1) groups:

\[
M_\times(G,n)
=
b_S+
\frac{b_G}{G^2}
\left[
G+2\sum_{h=1}^{G-1}(G-h)\rho^h
\right]
+\frac{b_A}{Gn}.
\]

For the triangular array \(\rho_G=1-c/G\):

\[
q_\infty(c)
=
\frac{2(c-1+e^{-c})}{c^2}>0.
\]

This persistent group term can imitate a society-common floor.

## Main numerical results

All intervals below are root-level, 36-family Bonferroni-adjusted t
intervals. They are not distribution-free exact intervals.

### Independent hierarchy

| World | Noise | Estimated \(b_S\) | Estimated \(b_G\) | Estimated \(b_A\) | Truth |
|---|---:|---:|---:|---:|---:|
| author only | Gaussian | .00011 | -.00007 | .07700 | 0 / 0 / .08 |
| author only | \(t_5\) | .00001 | .00036 | .07571 | 0 / 0 / .08 |
| group + author | Gaussian | -.00003 | .06043 | .07976 | 0 / .06 / .08 |
| group + author | \(t_5\) | -.00002 | .06013 | .07776 | 0 / .06 / .08 |

The pure-iid coefficients were all simultaneously inside the registered
\(\pm.01\) practical-zero band.

### Dependent groups

| Registered \(\rho\) | Noise | Recovered \(\hat\rho\) | Held-out NRMSE |
|---:|---:|---:|---:|
| .5 | Gaussian | .5053 | .0205 |
| .5 | \(t_5\) | .4975 | .0196 |
| .9 | Gaussian | .9036 | .0199 |
| .9 | \(t_5\) | .8985 | .0252 |

If these cells are incorrectly fit with the independent formula, they
produce false society terms of approximately `.0106` at \(\rho=.5\) and
`.0366-.0371` at \(\rho=.9\).

### Conditional projection

In the correlated raw hierarchy:

- largest raw cross-level covariance:
  `.04682` Gaussian and `.04686` \(t_5\);
- largest post-projection cross-level covariance:
  `.00098` Gaussian and `.00113` \(t_5\);
- planted martingale coefficients:
  \(b_S=.24180,b_G=.14415,b_A=.08\);
- recovered Gaussian:
  `.24051/.14206/.07368`;
- recovered \(t_5\):
  `.23932/.14809/.07132`.

Conditional centering recovered the registered Hilbert projection. It did
not prove causal or psychological purity.

### Observable, unavailable, and technical common terms

- A score-visible society term was approximately `.0600` before completion
  and practical zero after independent score-view subtraction.
- A score-unavailable society shock remained `.05967` Gaussian and `.05862`
  \(t_5\) in the admissible residual.
- Shared technical noise remained `.05941` Gaussian and `.05916` \(t_5\)
  after the structural oracle, but disappeared only under the omniscient
  oracle.
- Per-society test centering changed an unavailable floor near `.059` into
  numerical zero, demonstrating the registered false-zero attack.

Second-order cross-view statistics alone cannot distinguish a stable
society component from shared measurement noise.

## Heavy-tail precision extension

The original \(t_5\) local-to-unity endpoint returned:

\[
\hat b_S=-.003987,\quad
CI_{\mathrm{sim}}=[-.010884,.002910],
\]

which missed the \(\pm.01\) equivalence boundary by `.000884`.

R2G.2A used 80 new roots and did not pool the original 30:

| Estimand | Mean | Simultaneous interval | Truth |
|---|---:|---:|---:|
| corrected \(b_S\) | -.001284 | [-.005732, .003164] | 0 |
| corrected \(b_G\) | .061738 | [.054868, .068607] | .06 |
| corrected \(b_A\) | .082496 | [.077006, .087986] | .08 |
| \(\theta_\infty\) | .038400 | [.037864, .038935] | .038567 |
| naive \(b_S\) | .033853 | [.033128, .034577] | false attribution |

Corrected held-out NRMSE was `.03286`; naive NRMSE was `.05441`.

The root-level correlation between corrected \(b_S\) and \(b_G\) was
`-.9927`. The total asymptotic floor:

\[
\theta_\infty=b_S+q_\infty(c)b_G
\]

is much more stably identified than its society/group allocation.

## What this proves about "clean factors"

The experiment gives a constructive answer:

1. If every cross-view-common component belongs to the registered
   information set, and the remainder is independent across views with
   summable hierarchical dependence, the cross-view common floor can be
   reduced to practical zero in the synthetic system.
2. This does not make total residual energy zero. Independent measurement
   error remains.
3. A component absent from the score information set does not disappear.
4. Long-range group dependence can preserve a non-zero total limit even when
   the explicit society coefficient is zero.
5. Shared technical noise and stable latent structure can be observationally
   equivalent at second order.

Therefore "all factors are clean" is not sufficient by itself. Zero requires
factor completeness, correct hierarchy/dependence, independent measurement
views, and non-leaky reference construction.

## Boundaries

- No exact-zero theorem was empirically proved.
- The result is synthetic and uses known \(c=1.5\).
- With unknown or unrestricted group covariance, \(b_S\) and persistent
  group dependence may be non-identifiable.
- `society_energy=.06` is a generic spec field and is not injected into the
  local-to-unity world; its true \(b_S\) is zero.
- No real text, personality label, psychological construct, causal claim, or
  clinical conclusion is involved.
- The checkout was dirty and these files were not Git-tracked before the
  runs. Hash manifests exist, but this is not a third-party preregistration
  seal until committed and tagged.

## Artifacts

- `results/v8_hierarchical_society_limit/v37h4d_r2g2_confirmation_30rep_20260727/`
- `results/v8_hierarchical_society_limit/v37h4d_r2g2a_t5_precision_80rep_20260727/`

Both artifact inventories pass.
