# V8 Resolution Filtration V3.7H Discovery Report

Date: 2026-07-26

Status: `DISCOVERY_COMPLETE_NOT_CONFIRMED`

This report concerns a 30-repetition synthetic mechanism experiment. It does
not establish a real-text construct, personality validity, clinical validity,
or a universal martingale theorem.

## Research question

V3.7G estimated a reliability spectrum at fixed event budgets. V3.7H asks
whether one jointly calibrated estimator, applied to genuinely nested event
prefixes,

\[
\mathcal F_{32}\subset\mathcal F_{64}\subset
\mathcal F_{128}\subset\mathcal F_{256}\subset\mathcal F_{512},
\]

behaves as an observable approximate resolution filtration:

1. later estimates reduce scorer-only risk;
2. uncertainty contracts without losing registered coverage;
3. score updates contain little predictable drift in stationary worlds;
4. the score and unresolved channels remain exactly reversible.

The tested error scale is explicitly normalized mean squared error:

\[
\operatorname{NMSE}(\widehat G,G)
=
\frac{\mathbb E\|\widehat G-G\|^2}
{\mathbb E\|G-\mu_0\|^2}.
\]

No square root is taken.

## Design

Each repetition used disjoint reference, calibration, coherence-probe,
interval-fit/radius, and evaluation panels. The same event streams generated
all five cumulative prefixes. One spectral response rule was selected jointly
across budgets without evaluation truth. Synthetic truth was scorer-only.

The four primary worlds were:

- exact rank 12;
- dense stable tail;
- broken spectrum;
- long-memory event noise.

Stress worlds included null authors, author permutation, one- and two-occasion
state, informative precision, Student-t event noise, reference-panel shift,
and an author-specific opportunity schedule drift. An independently planted
oscillating-operator assay tested whether the observable coherence probe could
detect a known non-filtration.

## Discovery results

Integrity checks all passed:

- 1,800 budget-level rows and 1,560 transition rows matched the design;
- all 5,760 derived RNG seeds were unique;
- one candidate rule was shared across all budgets within each world;
- latent truth was constant across budgets;
- nested-prefix identity error was zero;
- maximum score/path reconstruction error was \(2.12\times10^{-15}\);
- the sealed V3.7G parent hash matched.

### Core worlds

| World | NMSE reduction, 32 to 512 | Radius ratio, 512 / 32 |
| --- | ---: | ---: |
| Exact rank 12 | 90.03% [89.93%, 90.12%] | 0.298 [0.292, 0.305] |
| Dense tail | 81.50% [81.35%, 81.64%] | 0.424 [0.415, 0.432] |
| Broken spectrum | 79.59% [79.45%, 79.73%] | 0.417 [0.409, 0.424] |
| Long memory | 80.27% [80.14%, 80.40%] | 0.437 [0.429, 0.445] |

Across all registered core transitions:

- maximum simultaneous upper bound for observable update predictability
  \(\kappa\): 0.00296, below the 0.03 candidate gate;
- maximum simultaneous upper bound for cross-author mean-update energy:
  0.00547, below 0.01;
- worst simultaneous upper bound for adjacent NMSE change: -0.02433,
  so every adjacent budget improved risk;
- worst simultaneous upper bound for adjacent radius ratio: 0.88162;
- minimum simultaneous lower bound for model-assisted latent coverage:
  0.95026;
- effective degrees of freedom increased monotonically in every core
  transition.

The result supports an **estimator- and function-class-bounded approximate
resolution filtration** in the four registered synthetic stationary worlds.
It does not prove

\[
\mathbb E[M_{m'}\mid\mathcal F_m]=M_m
\]

for all measurable functions or all data-generating processes.

### Coherence assay

The planted oscillating estimator produced transition-level \(\kappa\)
means of 0.110, 0.141, 0.335, and 0.491. Three of four simultaneous lower
bounds exceeded 0.10. The probe can therefore detect a sufficiently strong,
history-predictable violation; near-zero core \(\kappa\) is not explained
only by an inert detector.

## Opportunity-drift identification boundary

The opportunity stress world is the most important discovery result.
Its event-level schedule is still nested, but after the first 32 events each
new event block contains an author-specific response:

\[
X_{u,t}=G_u+B G_u+\varepsilon_{u,t}.
\]

The response is centered across authors, so it does not appear as a population
mean shift. It is also aligned with stable author geometry, so the estimator
can absorb it as if it were increasingly precise author structure.

Observed trajectory:

| Budget | True NMSE | Observable proxy NMSE | Coverage | Radius |
| --- | ---: | ---: | ---: | ---: |
| 32 | 0.802 | 0.716 | 0.973 | 2.401 |
| 64 | 0.761 | 0.384 | 0.380 | 1.704 |
| 128 | 0.886 | 0.220 | 0.017 | 1.335 |
| 256 | 1.028 | 0.139 | 0.000 | 1.049 |
| 512 | 1.140 | 0.098 | 0.000 | 0.799 |

Thus the observable proxy becomes steadily better while scorer-only error
becomes 42.2% worse from budget 32 to 512. The interval becomes narrower
around a biased center and latent coverage collapses.

Single-transition coherence remained small
(\(\kappa=0.008\) to \(0.036\)). This is not evidence that no opportunity
effect exists. It exposes a mathematical weakness of local diagnostics:
small author-specific increments can accumulate coherently even when each
increment explains only a small fraction of noisy update energy and the
cross-author mean is approximately zero.

Consequently:

\[
\text{local near-martingale behavior}
\not\Rightarrow
\text{long-horizon construct invariance}.
\]

The original candidate check requiring opportunity-drift \(\kappa>0.10\) in
three transitions is not an appropriate hard positive-control gate. The
oscillating assay is the detector-sensitivity control. Opportunity drift is a
stress/identification world and must be judged by cumulative path bias,
calibration failure, or explicit design refusal.

This result independently reinforces SUICA's earlier design principle:
condition and opportunity structure cannot always be subtracted
statistically after observation. When a condition response is geometrically
aligned with stable author variation, the condition must be fixed,
randomized, logged, or represented explicitly in the measurement design.

## Scientific ruling

Provisional ruling:
`CORE_DISCOVERY_PASS_WITH_OPPORTUNITY_IDENTIFICATION_BOUNDARY`

Independent mathematical ruling:
`NO_GO_FOR_CONFIRMATION`

Accepted at discovery level:

- nested evidence can produce monotone risk reduction and uncertainty
  contraction under registered stationary synthetic worlds;
- a continuous reliability spectrum activates additional dimensions without
  deleting the unresolved channel;
- the observable local-coherence assay is sensitive to a planted oscillating
  violation;
- exact information-channel reconstruction is preserved.

Not accepted:

- a universal martingale or filtration theorem;
- automatic separation of stable author structure from author-specific
  opportunity response;
- latent coverage under unlogged condition drift;
- any real-text, personality, cross-language, or clinical claim.

## Next experiment

Before a V3.7H confirmation can be frozen, add a prospective cumulative
path-drift assay. At minimum it should compare:

\[
\Delta_{0:k}M_u=M_u(m_k)-M_u(m_0)
\]

against its stationary calibration distribution and test whether cumulative
displacement is predictable from the initial author profile even when every
local \(\kappa_k\) is small.

A valid next gate must:

1. remain low in all four stationary core worlds;
2. detect the registered opportunity-drift world without scorer truth;
3. distinguish ordinary uncertainty contraction from biased-center
   contraction;
4. preserve an explicit refusal outcome when opportunity history is missing;
5. be frozen before any fresh confirmation seed is generated.

The current discovery output is not eligible to be relabeled as confirmation.

## Reproducibility

Discovery artifacts:
`results/v8_resolution_filtration/v37h_discovery_30rep_20260726/`

Runner:
`scripts/run_suica_v8_resolution_filtration_v37h.py`

Core implementation:
`suica_core/v8_resolution_filtration.py`

Config:
`configs/v8_resolution_filtration_v37h_discovery.json`

Regression suite after completion: `543 passed`.
