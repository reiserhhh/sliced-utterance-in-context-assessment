# V6 Formal Measurement Objects and Identification

Status: synthetic-theory specification, 2026-07-13. No dynamic coordinate is named as
personality in this document.

## Observation and latent path

For author `u`, occasion `o`, context/register `r`, and window `t`, define

```text
w_uort = mu_C/O(ort) + a_u + B_u phi(z_ort) + g_uort.
```

`mu_C/O` is the condition/opportunity baseline, `a_u` the fixed-reference author level,
`B_u` the author response operator, `z` a declared condition/opportunity coordinate,
`phi` a predeclared response basis on that coordinate, and `g` the short-run innovation
field. A linear `phi(z)=z-E_Q[z]` is a special case, not the general definition. Raw
counts are an observation layer:

```text
D ~ Bernoulli(1-pi)
Y | D=1,O,w ~ Binomial(O, sigmoid(w))
Y=0 | D=0.
```

`O=0` means no expression opportunity, not a zero construct score. With hidden `O`,
opportunity, structural zero, and response rate are generally not separately identified.

## Mean, flow, and gust

For a preregistered target distribution `Q`:

```text
M_u(Q) = E_Q[w - mu_C/O | u] = a_u
F_uort = B_u phi(z_ort)
g_t = sum_l Phi_l g_(t-l) + H_t^(1/2) epsilon_t.
```

The last equation permits colored, cross-coupled, heteroskedastic gusts. For weights
`q_t`, the correct aggregation variance is

```text
Var(sum_t q_t g_t) = sum_s sum_t q_s q_t Gamma_st.
```

The familiar `Omega/m` law is only the stationary short-memory, uniform-weight limit.
Unit roots, long memory, random slopes, unresolved low-frequency cycles, or aliasing
trigger refusal.

## Identification

`B_u` requires a full-rank, sufficiently excited within-author design:

```text
G_u = sum_o Z_uo' V_uo^(-1) Z_uo > 0.
```

Refuse an individual operator when the design is rank deficient, its condition ratio is
below `1e-3`, opportunities are hidden, common support is absent, the registered
condition-coverage criterion fails, or conditions are endogenous to the innovation.
Hierarchical shrinkage may predict an operator but does not repair individual
identification.

If `z` is latent, `(B_u,z)` is rotationally non-identifiable. Only the product or
subspace is interpretable unless anchors fix the rotation.

## Selection, fixed response, and condition geometry

The free-selection and fixed-condition phases are different estimands. In a free phase,

```text
C_ui ~ Categorical(softmax(lambda L a_u + eta_u)).
```

The empirical selection profile estimates `pi_u(c)=P(C_ui=c | u)`. If `lambda != 0`,
the population condition baseline includes selection-linked author variation. Therefore
population condition centering changes the level estimand; it is not a universal
denoising operation. A balanced fixed phase instead assigns condition coordinates
independently of the author and identifies conditional expression only over its covered
support.

For continuous condition space, prompt count alone is not a support guarantee. Given a
predeclared target measure `Q_z` and fixed support `S`, record a coverage diagnostic such
as

```text
rho(S, Q_z) = E_(z ~ Q_z) min_(s in S) ||z-s||.
```

and freeze a maximum admissible `rho` or an equivalent fill-distance criterion before
reading outcomes. The condition map `z`, basis `phi(z)`, support `S`, and reference
measure `Q_z` are part of the estimator. A coarse proxy or a narrow region can leave an
operator rank-positive while still making its response function nontransportable away
from that region.

## T8-prime

For fixed support and weights `q`, let `A_q = q' tensor I_p`. Then

```text
R^(mp) = ran(A_q*) direct-sum ker(A_q).
```

If `h` belongs to `ker(A_q)`, `A_q(x+h)=A_qx`. This proves only that a mean-only
instrument cannot distinguish those paths. It does not establish stable author
differences, new traits, or dimensions beyond questionnaires.

## Minimum design

- One occasion licenses path description only.
- At least two independent occasions are needed to identify repeatability.
- Formal acceptance uses at least three: discovery, independent retest, and context
  stress test.
- A discrete `d`-condition operator needs at least `d+1` distinct support points and
  repeated critical support across occasions. A continuous-basis operator needs full
  rank for `[1, phi(z)]` **and** a preregistered coverage diagnostic over its intended
  condition region; a count of equal prompts alone is insufficient.
- In the registered synthetic calibration only, a binary contrast first cleared its
  numerical gate at 2 conditions x 2 repeats; a 4-condition breadth-qualified contrast
  cleared it at 4 x 2. These are not human collection requirements.
- Recovery requires baseline plus at least three post-stimulus points; multidimensional
  recovery additionally requires controllability, observability, sufficient Hankel rank,
  and non-aliased sampling.
- Cross-lag matrices are predictive, not causal, without independent perturbation and
  instantaneous-confounding control.

## Verdict vocabulary

- `REFUSE`: identification assumptions fail.
- `UNDECIDED`: identified but insufficiently powered.
- `FALSIFIED`: estimator misses in an identified, adequately powered world.
- `SUPPORTED-SYNTHETIC`: estimator passes in planted worlds; no human construct claim.
