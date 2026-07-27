# SUICA M3 Mechanism Atlas Synthesis

Status: synthetic discovery program complete through independent pairwise
decomposition. Cross-family sealed confirmation remains open.

Overall decision:
`M3_INTERMEDIATE_MECHANISM_ATLAS_DISCOVERY_SUPPORTED`.

## 1. Scientific question

The micro-to-meso arrow is not treated as a direct connection:

\[
\mathcal N_u \not\Rightarrow a_u.
\]

Instead, event panels may support several distinct author-level
coarse-grainings:

\[
\mathcal A_u
=
\left(
\mu_u^{\mathrm{shape}},
\mathcal R_u^{\mathrm{condition}},
\mathcal K_u^{\mathrm{temporal}},
\mathcal C_u^{\mathrm{partner}},
\mathcal P_u^{\mathrm{higher-order}}
\right).
\]

The discovery program asks whether these objects are separately recoverable,
whether low-order summaries are sufficient, and whether mechanisms remain
separable under superposition.

## 2. Experiment sequence

### V1: low-order parameter recovery

V1 isolated five simple worlds and compared competing summaries. All expected
families won, null maximum AUC was `0.506`, and the opportunity-only
response-residual maximum was `0.516` after correcting intercept leakage.

Independent audit narrowed the result: the density world still differed in
covariance, the slow-mode world was a binary lag-one process, the interaction
world was a linear slope, and the path world was lag-two memory. The licensed
decision is therefore:

`M3_ATLAS_V1_LOW_ORDER_PARAMETER_RECOVERY_PASS`.

### V2A: low-order-matched attack

The generator then matched or held fixed the cheap statistic:

- equal mean and covariance, different distribution shape;
- equal linear condition slope, different nonlinear response;
- equal lag-one correlation, different AR(2) dynamics;
- equal lag-one and lag-two dependence, different lag-three memory;
- equal linear partner slope, different nonlinear coupling.

Original V1 estimators passed nonlinear condition, AR(2), and nonlinear
interaction, but failed pure distribution shape and lag-three path. This
`PARTIAL` result is retained as evidence that the first estimators were not
general enough.

### V2B: object-matched estimator upgrade

Two mathematically targeted summaries were added:

1. an author-whitened multiscale empirical characteristic function for
   distribution shape beyond mean and covariance;
2. the lag-three partial operator after controlling lag one and lag two.

At 192 events per occasion and 10 seeds:

| World | Higher-order AUC | Cheap AUC | Higher-order geometry | Cheap geometry |
| --- | ---: | ---: | ---: | ---: |
| equal-covariance distribution shape | 0.939 | 0.507 | 0.963 | 0.026 |
| nonlinear condition response | 1.000 | 0.500 | 0.999 | 0.156 |
| matched-lag1 AR(2) slow mode | 0.834 | 0.504 | 0.887 | 0.031 |
| pure lag3 path memory | 0.935 | 0.506 | 0.979 | 0.031 |
| nonlinear partner response | 1.000 | 0.521 | 0.999 | 0.173 |

Null maximum AUC was `0.525`.

### V3: independent pairwise decomposition

Five author parameters were independently permuted, removing the shared
author-order code in V1. All ten mechanism pairs were generated. For every
target mechanism, the audit measured:

- partial geometry with its own truth while controlling the other truth;
- cross-talk with the other truth;
- same-author independent-view AUC;
- counterfactual geometry after deleting only the target mechanism.

| Mechanism | Own partial geometry | Cross-talk | Knockout geometry | AUC |
| --- | ---: | ---: | ---: | ---: |
| AR(2) temporal | 0.841 | 0.019 | 0.008 | 0.801 |
| nonlinear condition | 0.996 | 0.021 | -0.000 | 0.966 |
| distribution shape | 0.882 | 0.072 | -0.001 | 0.911 |
| nonlinear interaction | 0.995 | 0.011 | 0.008 | 0.963 |
| lag3 path | 0.886 | 0.056 | -0.019 | 0.864 |

All mechanisms passed all four pair contexts in which they appeared.

## 3. What was discovered

The results support a **mechanism-selection layer** rather than a universal
direct projection. Stable author geometry can arise through at least five
mathematically distinct channels:

1. standardized distribution shape, not only mean or covariance;
2. nonlinear response to shared conditions;
3. temporal dynamics beyond matched one-step correlation;
4. nonlinear response to another actor's input;
5. higher-order path dependence beyond lower lags.

The opportunity correction is equally important. A regression intercept is
author position, not response coupling. Keeping it inside an operator caused
false interactional identity; removing it returned the opportunity-only
residual channel to chance.

## 4. What remains unproven

V2B uses matched discovery families: Hermite-polynomial worlds are estimated
with Hermite features, AR(2) with VAR(2), lag-three with a lag-three partial
operator, and the distribution world with a deliberately multiscale
characteristic-function summary. V3 therefore proves **synthetic
decomposability under known mechanism classes**, not universal mechanism
discovery.

The following remain open:

1. spline, discontinuous, neural, and hidden-state generators not sharing the
   estimator dictionary;
2. unknown lag/order selection rather than supplying the correct maximum
   order;
3. actor-partner-dyad separation with multiple partners;
4. exact edge-multiset path aliases and tree-like path equivalence;
5. actual MNAR, technical dependence, support failure, and reference drift;
6. persistence in human text and psychological or behavioral interpretation.

## 5. Current formula

The permitted M3 discovery formula is:

\[
\mathfrak M_u^{\mathrm{disc}}
=
\Delta_{P_0}\left[
D_u^\Omega
\oplus R_u^{\mathcal B}
\oplus K_u^{(2)}
\oplus C_u^{\mathcal B}
\oplus P_{u,3\mid1:2}
\right].
\]

Here \(D_u^\Omega\) is a finite multiscale characteristic-function profile
after author centering/scaling; \(R_u^{\mathcal B}\) and
\(C_u^{\mathcal B}\) are nonlinear condition and partner-response projections
on the current finite basis; \(K_u^{(2)}\) is the VAR(2) companion spectrum;
and \(P_{u,3\mid1:2}\) is lag-three memory conditional on the first two lags.
\(\Delta_{P_0}\) makes every object relative to a frozen reference
population. The direct sum is an atlas, not a sum score, and does not imply
that every component is present for every corpus.

## 6. Licensed claim

In registered synthetic worlds, distinct distributional, conditional,
temporal, interactional, and higher-order path mechanisms can generate stable
author geometry. Matched higher-order estimators recover these mechanisms
beyond corresponding low-order statistics, and independently parameterized
mechanisms remain separable in pairwise superposition with target-specific
counterfactual knockout.

No human-text, personality, completeness, clinical, or sealed
cross-family-confirmation claim is licensed.

## 7. Next confirmation worlds

1. **CF-D**: unknown rotations and distributions with matched low-order
   moments but different copulas, tails, or modality; freeze the ECF frequency
   set before generation.
2. **CF-O**: spline, Voronoi/discontinuous, and tanh/softplus condition and
   partner functions with multiple partners and actor/partner/dyad effects;
   keep linear and Hermite projections matched.
3. **CF-KP**: hidden semi-Markov, non-reversible cycle, and nonlinear
   state-space worlds with matched observed low-order autocovariances but
   different dwell hazards, slow modes, or path direction.
