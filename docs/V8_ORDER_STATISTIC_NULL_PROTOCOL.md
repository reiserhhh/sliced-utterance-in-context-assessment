# V8 Statistic-Level Conditional Order Null

Status: `EXPLORATORY_MECHANISM_REPAIR`

Feature-level centering does not by itself define a valid null for a nonlinear
density statistic. For each fixed four-event multiset \(X_{ur}\),

\[
\mu(X_{ur})=\frac1{24}\sum_{\pi\in S_4}K(\pi X_{ur}),\qquad
Z_{ur}^{\pi}=K(\pi X_{ur})-\mu(X_{ur}).
\]

Although \(E_\pi Z^\pi=0\), the final density applies positive-part projection
and trace normalization:

\[
\rho(C)=
\frac{[\operatorname{sym}(C)]_+}
{\operatorname{tr}[\operatorname{sym}(C)]_+},
\qquad
E_\pi\rho(\widehat C^\pi)\ne\rho(E_\pi\widehat C^\pi).
\]

The primary null therefore randomizes the complete mapping:

1. preserve author, event multiset, and even/odd replicate membership;
2. enumerate all \(4!=24\) inner permutations for exact centering;
3. independently sample the two replicate orders for every author and corpus;
4. reconstruct replicated density;
5. recompute matched-spectrum HS and root fidelity;
6. compare the native statistic with 1,999 outer random-order worlds;
7. use one maxT family across HS/fidelity and D1/D2.

If more than 5% of null densities have positive rank below the frozen rank
10, the result is refused. A failed randomization gate stops the order claim;
block localization cannot rescue it. A pass would establish exploratory
sequence-sensitive adjacency structure only, not time direction, cognition,
personality, universality, diagnosis, or clinical validity.
