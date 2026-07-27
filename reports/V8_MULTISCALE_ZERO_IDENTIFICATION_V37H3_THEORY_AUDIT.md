# V8 V3.7H.3 Theory Audit

Date: 2026-07-26

Ruling: `PARTIAL`

This is a post-run theory audit, not an independent sealed confirmation.

## Accepted

- The balanced hierarchical formula is dimensionally and algebraically
  coherent.
- K=4 finite-sample recovery remains strong under both registered Gaussian and
  heteroskedastic \(t_5\) opportunity/technical noise.
- The ICC=.30 world correctly exposes a non-vanishing aggregation floor.
- The selection assay demonstrates a registered Simpson-style reversal and
  its repair under a balanced reference with positivity.
- The persistent-cause alias is correctly classified as unidentifiable.

## Construction checks, not separate discoveries

- machine-precision reconstruction;
- exactly quadratic symmetric zero paths;
- iid \(-1\) and common-effect 0 aggregation slopes;
- exact persistent-alias equality;
- exact \(p\alpha\eta\) range/kernel identity.

These are useful software and theorem checks. They must not be counted as
independent empirical confirmations.

## Main threat

The generator and estimator share an additive, balanced, orthogonal
coordinate system. A wrong additive model can still reconstruct cell means
exactly while assigning nonlinear interaction or non-ergodic opportunity
structure to the wrong component.

## Next adversary

The minimum high-value test is:

\[
X_{u,c,k,r}
=
\gamma\tanh(a_u^\top M h_c)
+L_{u,k}+\varepsilon_{u,c,k,r},
\]

where \(L_{u,k}\) is author-correlated and non-ergodic. The current additive
estimator must be fitted without receiving the nonlinear generator.

The next protocol should require:

1. simultaneous positive-control false-refusal upper below .05;
2. nonlinear misspecification detection lower above .90;
3. false stable-author energy below .01;
4. held-out-condition nonlinear recovery lower above .80 before any
   nonlinear identification claim;
5. explicit comparison of \(K\to\infty\) and population-size
   \(n\to\infty\) paths;
6. `MODEL_INADEQUATE` when the wrong additive coordinate system cannot be
   safely interpreted.

Until that adversary is passed, V3.7H.3 is a discovery-level additive-world
identification result, not a general multiscale identification theorem.

