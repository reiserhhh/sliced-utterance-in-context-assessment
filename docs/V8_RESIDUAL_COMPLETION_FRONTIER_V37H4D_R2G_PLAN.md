# V8 V3.7H.4D-R2G Residual Completion Frontier

Status: prospective protocol written before R2G formal outcomes.

## Question

R2G tests whether a non-zero social aggregation floor is caused by a finite,
reproducible omitted factor system rather than irreducible variation:

\[
R_{\mathcal F}
=X-E[X\mid\mathcal F]
=
\{E[X\mid\mathcal G]-E[X\mid\mathcal F]\}
+\{X-E[X\mid\mathcal G]\}.
\]

The first term is structured omission. The second is irreducible relative to
the registered information set.

## Three zeros

- exact zero: \(E\|R\|^2=0\); not empirically provable with finite data;
- asymptotic zero:
  \(M(n)=E\|\frac1n\sum_iR_i\|^2\rightarrow0\);
- practical zero: the confirmation upper bounds of normalized cross-view
  structure and population floor are at most `.02` and `.01`.

Test-set centering is forbidden. A zero produced by centering is not evidence
of factor completeness.

## Independent score and target observations

Every unit has four observations:

\[
(A_s,A_t,B_s,B_t).
\]

All opportunity-noise streams are independent. A completion model may use
only \(A_s\) to predict \(A_t\), and only \(B_s\) to predict \(B_t\). Residuals
are then compared across A/B:

\[
\widehat C_{AB}
=
\frac{1}{2N}\sum_u
(e_A\otimes e_B+e_B\otimes e_A).
\]

This contract prevents a high-capacity model from copying its evaluation
observation.

## Bounded factor classes

- linear reduced-output-rank Ridge, rank in `{1,2,4,8}`;
- training-fitted rank-8 PCA followed by a degree-2 polynomial map and Ridge;
- random Fourier feature Ridge, same output ranks;
- rank zero;
- an unrestricted decision-tree memorizer used only as an overfit trap.

Rank and family are selected on independent calibration groups by target
prediction loss and a one-SE rule. Confirmation never selects rank, kernel,
center, loading, or regularization.

## Population limits

For group sizes `{4,8,16,32,64,128}`, R2G fits:

\[
M_0(n)=a/n,\quad
M_1(n)=b+a/n,\quad
M_2(n)=b+a n^{-\alpha}.
\]

The registered floor estimand is the \(b\) from \(M_1\). The power model is a
misspecification diagnostic, not a replacement estimand.

## Worlds

1. `pure_iid`: no stable omission; both structure measures should be
   practically zero.
2. `author_low_rank`: stable author omission but no social floor; tests that
   aggregation zero does not imply factor completeness.
3. `common_low_rank`: a linearly recoverable shared factor creates a floor.
4. `nonlinear_common`: score and target are linked nonlinearly; the bounded
   nonlinear path is needed.
5. `irreducible_common_shock`: a target-common component is absent from the
   score information set; admissible completion must refuse zero.
6. `overfit_null`: a memorizer reaches training zero but must fail on fresh
   confirmation groups.

Gaussian and standardized Student-\(t_5\) opportunity noise are both used.

## Decision boundary

`PASS_FINITE_COMPLETION` requires:

- null and overfit controls remain controlled;
- common linear and nonlinear omissions are detected before completion;
- a frozen bounded completion reaches practical zero on fresh groups;
- the unobservable common shock is not falsely declared complete.

`PARTIAL_LINEAR_ONLY` is used when the linear world closes but the nonlinear
world does not. Any false completion of the irreducible or overfit controls is
`REFUTED_FALSE_COMPLETENESS`.

Even a pass establishes only an existence and identifiability result in the
registered synthetic class. It does not prove exact zero, complete
personality factors, or transfer to real text.
