# V8 Resolution Filtration V3.7H.1 Plan

Status: `DISCOVERY_PROTOCOL_NOT_SEALED`

V3.7H.1 repairs the identification failure found in V3.7H. It separates
three questions that one local coherence statistic cannot answer:

1. does the synthetic scorer path satisfy an approximate posterior projection
   identity;
2. is long-horizon score movement predictable from the initial observable
   history;
3. does the score remain invariant across explicitly varied opportunity
   schedules for the same authors.

No confirmation seed may exist until this protocol, its code, and its power
curve have been independently audited and publicly sealed.

## A. Scorer-only projection identity

For scorer-only truth \(T\), external origin \(z\), and budgets \(m<n\):

\[
S_T=d^{-1}\mathbb E\|T-z\|^2,
\]

\[
R_m=\frac{d^{-1}\mathbb E\|T-M_m\|^2}{S_T},
\qquad
U_{m,n}=\frac{d^{-1}\mathbb E\|M_n-M_m\|^2}{S_T}.
\]

The projection defect is:

\[
D_{m,n}=R_n-R_m+U_{m,n}.
\]

It must equal the orthogonality form:

\[
D_{m,n}
=
-\frac{2d^{-1}\mathbb E
\langle T-M_n,M_n-M_m\rangle}{S_T}.
\]

Required outputs:

- `true_nmse_left`;
- `true_nmse_right`;
- `true_nmse_delta`;
- `update_nmse`;
- `projection_defect`;
- `posterior_orthogonality`;
- `projection_algebra_error`.

Candidate core gates:

- one-sided familywise upper of adjacent true-NMSE change at most 0.005;
- two one-sided 97.5% familywise bounds keep \(D\) within
  \([-0.01,0.01]\);
- algebra error at most \(10^{-10}\).

## B. Observable cumulative path

Anchor every path at budget 32:

\[
C_m=M_m-M_{32},
\qquad m\in\{64,128,256,512\}.
\]

The budget-32 observable history is:

\[
Z_{32}
=
[M_{32}-z,\ U_{32},\
X^{(1)}_{32}-X^{(2)}_{32}].
\]

It intentionally excludes the redundant raw profile because
`profile = score + unresolved`.

One predictor specification is selected by probe-panel inner CV jointly
across all four horizons. Candidate families are:

- linear ridge;
- reduced-rank ridge with ranks 4, 8, 16, and 32;
- random Fourier ridge with 256 features;
- ridge alpha 1, 10, 100, or 1000.

Evaluation reports:

\[
\kappa_m^{cum}
=
1-
\frac{\sum_u\|C_{u,m}-\widehat h_m(Z_{u,32})\|^2}
{\sum_u\|C_{u,m}\|^2},
\]

and the equal-horizon average \(\kappa_{\mathrm{pool}}^{cum}\).

Candidate gates:

- core pooled cumulative \(\kappa\) simultaneous upper at most 0.01;
- registered opportunity pooled cumulative \(\kappa\) lower at least 0.02.

These values are discovery candidates, not confirmed constants.

## C. Paired opportunity schedules

The same authors are observed under two independently noised schedules:

\[
X^A_{u,m}=z+G_u+\varepsilon^A_{u,m},
\]

\[
X^B_{u,m}=z+G_u+f_mg(G_u)+\varepsilon^B_{u,m},
\]

with:

\[
f_m=[0,.5,.75,.875,.9375].
\]

The same frozen \(W_m\) scores both schedules. A separate same-schedule null
uses no drift in either arm.

At each budget, define noise-corrected schedule excess:

\[
Q_m
=
\frac{
\mathbb E\|M^B_m-M^A_m\|^2
-V_{\mathrm{stream},m}
}{S_{\mathrm{obs}}},
\]

where \(V_{\mathrm{stream},m}\) is estimated from within-schedule stream
differences. The final denominator must be in the same score space as the
numerator:

\[
S^{score}_m
=
d^{-1}\operatorname{tr}
\left(
W_m\widehat\Sigma_GW_m^\top
\right).
\]

Thus the operational statistic is:

\[
Q_m^{score}
=
\frac{
\mathbb E\|M^B_m-M^A_m\|^2
-V_{\mathrm{stream},m}
}{S^{score}_m}.
\]

Candidate endpoint gates:

- same-schedule null \(Q_{512}\) one-sided upper at most 0.01;
- opportunity pair \(Q_{512}\) one-sided lower at least 0.01;
- a triggered schedule difference forces
  `interval_claim_allowed=false`.

Conversely, `interval_claim_allowed=true` means only that this registered
detector did not refuse. It is not evidence that condition invariance has been
proved.

The paired statistic is the only operational refusal channel. Cumulative
\(\kappa\) remains a mechanism diagnostic because its predictive power
depends on whether the response map is shared and learnable across panels.
Decision-facing one-sided bounds use a Bonferroni familywise correction over
the complete geometry-by-\(\eta\) table. Lower- and upper-direction families
are not combined into a joint two-sided 95% statement. Raw and score-space
planted effect sizes are scorer-only metadata and enter neither detector.

## D. Matched power curve

All alternatives are matched by endpoint response energy:

\[
\eta
=
\frac{d^{-1}\mathbb E\|f_{512}g(G)\|^2}{S_T}.
\]

Registered geometries:

- rank-4 linear;
- full-rank random rotation;
- rank-8 nonlinear tanh.

Registered levels:

\[
\eta\in\{0,.02,.05,.10,.20\}.
\]

Each cell requires 100 design-only repetitions. The paired-schedule detector
alone controls operational refusal; the cumulative-path result is retained as
a transport-sensitive diagnostic.

Power qualification candidates:

- \(\eta=0\): one-sided false-refusal upper at most 0.10;
- \(\eta=.10,.20\): all geometry-specific paired-refusal lower bounds at
  least 0.80;
- \(\eta=.02,.05\): diagnostic minimum-detectable-strength estimation only.

## E. World classification

Primary core:

- exact-rank nested Gaussian;
- dense-tail nested Gaussian;
- broken-spectrum nested Gaussian;
- long-memory dense nested.

Primary safety/control:

- paired same-schedule null;
- paired random-rotation opportunity at \(\eta=.10\);
- material-power cells at \(\eta=.10,.20\).

Diagnostic:

- the old unpaired opportunity world;
- oscillating implementation assay;
- null and author-permutation worlds;
- state, precision, heavy-tail, and reference-shift worlds;
- low-power cells at \(\eta=.02,.05\).

## F. Confirmation lock

Before confirmation:

1. every new metric has a synthetic unit test;
2. oscillating rows contain no inherited main-arm fields;
3. all max-T outputs state the one-sided familywise direction;
4. power calibration uses design seeds only;
5. an independent audit approves code, formulas, and gates;
6. a clean commit, SHA-256 seal, and external timestamp exist;
7. only then is a fresh 80-repetition confirmation seed generated.

Confirmation failure cannot be repaired by threshold tuning or rerunning the
same version.
