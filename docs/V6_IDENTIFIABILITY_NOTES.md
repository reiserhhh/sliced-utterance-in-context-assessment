# V6 identifiability notes

Status: **simulation-licensed / human-unvalidated** (2026-07-12).

## Unified object

For person `u`, occasion `o`, window `k`, and construct `c`, the working generator is

```text
O_uokc ~ Poisson(E_uok exp(alpha_c + d_c' z_uok + q_c' a_u))
g_uok  = sum_l Phi_l g_uo,k-l + eta_uok
x_uok  = mu + Lambda a_u + B z_uok + H(a_u tensor z_uok)
         + s_uo t_k + R_u g_uok
Y_uokc | O_uokc ~ Binomial(O_uokc, logistic(x_uokc))
```

`O` is expression opportunity, `z` context/register, `a_u` stable person position,
`Phi/Q` path memory and coupling, and `R_u` the person response operator. A multiscale
path may be written `g_k=sum_b L_b h^(b)_floor(k/b)`. These are separable objects only
under the corresponding observation, positivity, excitation, and rank conditions.

## Licensed statements

1. Short-memory stationary motion attenuates at the long-run-covariance rate `Omega/m`.
2. Three windows do not generally identify flow separately from endpoint memory.
3. Observed opportunity permits response-rate estimation; hidden Poisson opportunity
   and response intensity are not separately identifiable under thinning equivalence.
4. Cross-construct lag coupling is estimable only with a full lag model and calibrated
   null; diagonal-only models can mislabel coupling as a new factor.
5. Frequencies above Nyquist are observationally aliased. The original frequency cannot
   be recovered from the sampled path without additional design information.
6. A person response operator is identifiable only under sufficient excitation.
7. Added dynamic person dimensions concern conditional innovation rank, not marginal
   dynamic rank and not path-space orthogonality alone.

## Not licensed before human data

- That human text follows this generator.
- That any V6 dynamic coordinate is personality rather than opportunity, format, or state.
- That a stable synthetic response operator transfers across register or language.
- That Big5/MBTI/Enneagram are averaging-operator outputs.
- Clinical, diagnostic, individual-decision, or norm-referenced interpretation.

The native experiment must estimate opportunity/format covariates, cross-fit every axis,
repeat people across conditions and occasions, and compare same-person with matched
stranger controls. Simulation reduces design waste; it cannot replace that evidence.
