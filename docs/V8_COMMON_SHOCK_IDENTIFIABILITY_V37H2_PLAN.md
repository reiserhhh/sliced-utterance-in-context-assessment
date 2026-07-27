# V8 V3.7H.2 Common-Shock Identifiability Frontier

Status: discovery and power protocol. Confirmation is closed.

## 1. Problem

V3.7H.1 R4 estimates same-author schedule sensitivity from two technical
streams. Its noise correction is unbiased only when the technical streams are
conditionally independent. A shock shared by both streams is invisible to
their difference and can be misclassified as an author-by-schedule response.

V3.7H.2 separates two replication levels:

- technical streams \(r\), which measure scorer/segmentation noise;
- repeated opportunity occasions \(k\), which measure schedule-specific state
  and common-shock variation.

For author \(u\), schedule \(s\), opportunity replicate \(k\), and technical
stream \(r\):

\[
Y_{uskr}
=
W\left[
\mu_0+G_u+\delta_s g(G_u)+C_{usk}+H_{us}
+\sigma_u\epsilon_{uskr}
\right].
\]

\(C_{usk}\) varies across opportunity occasions. \(H_{us}\) is persistent
within an author and schedule and is not identifiable from a persistent
author response without an additional intervention.

## 2. Estimators

Let

\[
\bar Y_{usk\cdot}=\frac{Y_{usk1}+Y_{usk2}}2,
\qquad
\bar Y_{us\cdot\cdot}=\frac1K\sum_k\bar Y_{usk\cdot}.
\]

The legacy estimator removes only technical-stream disagreement:

\[
Q_K^{legacy}
=
\frac{
\mathbb E\|\bar Y_{uB\cdot\cdot}-\bar Y_{uA\cdot\cdot}\|^2
-\widehat V_{\mathrm{stream},K}
}{S_{\mathrm{score}}}.
\]

For \(K\ge2\), the repeated-opportunity estimator uses:

\[
\widehat V_{\mathrm{occasion},K}
=
\mathbb E_u\left[
\frac{s^2_{uA}}K+\frac{s^2_{uB}}K
\right],
\]

\[
s^2_{us}
=
\frac1{K-1}
\sum_k
\left\|
\bar Y_{usk\cdot}-\bar Y_{us\cdot\cdot}
\right\|^2.
\]

Then:

\[
Q_K^{rep}
=
\frac{
\mathbb E\|\bar Y_{uB\cdot\cdot}-\bar Y_{uA\cdot\cdot}\|^2
-\widehat V_{\mathrm{occasion},K}
}{S_{\mathrm{score}}}.
\]

A second centered statistic removes the population-wide schedule mean:

\[
Q_{K,\mathrm{author}}^{rep}
=
\frac{
d^{-1}\sum_j\operatorname{Var}_u(D_{uj})
-\widehat V_{\mathrm{occasion},K}
}{S_{\mathrm{score}}},
\quad
D_u=\bar Y_{uB\cdot\cdot}-\bar Y_{uA\cdot\cdot}.
\]

This distinguishes author-relative schedule sensitivity from a global fixed
schedule shift.

## 3. Registered frontier

- opportunity repeats \(K\in\{1,2,4,8\}\);
- technical-stream correlation \(\rho\in\{0,.3,.6\}\);
- common-shock score energy \(c\in\{0,.01,.05\}\);
- Gaussian and heteroskedastic standardized \(t_5\) technical noise;
- planted author-response score energy
  \(\eta_{\mathrm{score}}\in\{0,.02,.10\}\);
- one frozen random-rotation response geometry;
- 256 authors per panel;
- 100 design-only repetitions per cell.

The \(K=1\) repeated estimator must return `UNIDENTIFIABLE`, not a number.

## 4. Gates

For \(K\ge2\), the repeated estimator is a power candidate only if:

1. every \(\eta=0\) cell has Bonferroni one-sided false-refusal upper
   \(\le .10\);
2. every \(\eta=.10\) cell has Bonferroni one-sided power lower
   \(\ge .80\);
3. simultaneous bias intervals lie inside \([-.005,.005]\) for Gaussian
   cells and \([-.01,.01]\) for heteroskedastic \(t_5\) cells;
4. all \(K=1\) repeated estimates are explicitly unidentifiable;
5. a global score shift triggers total schedule sensitivity but not
   author-centered sensitivity;
6. observationally identical response and persistent-confound worlds are
   classified
   `SCHEDULE_SENSITIVITY_IDENTIFIED_CAUSE_UNIDENTIFIED`.

Legacy \(Q\) is a negative control. Its failure under correlated streams or
common shocks does not fail the new estimator.

## 5. Claim boundary

A pass can establish only that repeated opportunity occasions identify
schedule-sensitivity energy under the registered synthetic worlds. It cannot
identify the psychological cause of a persistent schedule difference, prove
real-text validity, establish personality meaning, or license clinical use.

## 6. D1 and D2 disposition

D1 completed the broad 216-cell frontier. Its only failed gate was the
familywise upper for one \(K=2\), heavy-tail null cell with 2/100 refusals.
All bias, power, global-shift, and causal-alias gates passed.

D2 then froze a fresh-seed 1,000-repetition tail audit at
\(\rho=.6,c=.05\), added \(K=3\), and tightened the null and power gates to
.05 and .90. D2 passed. \(K=2\) remained identifiable but had 11/1000
heavy-tail null refusals; \(K=3,4,8\) had zero in 1,000.

This is still design evidence. \(K=2\) is the validated minimum identifiable
configuration, \(K=3\) the validated minimum robust configuration, and \(K=4\)
the recommended default for a future sealed synthetic confirmation.
