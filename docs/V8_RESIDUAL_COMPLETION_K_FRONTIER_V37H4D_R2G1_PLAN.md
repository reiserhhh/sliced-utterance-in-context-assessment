# V8 V3.7H.4D-R2G.1 Score-Resolution Limit

Status: prospective follow-up after the frozen R2G confirmation returned
`INCONCLUSIVE_BOUNDED_COMPLETION`.

R2G established:

- the registered linear and nonlinear common omissions exist;
- omniscient/oracle subtraction makes their population floor practically zero;
- frozen \(K=4\) score-only models reduce but do not eliminate the floor;
- null, unobservable-shock, and overfit controls behave correctly.

R2G.1 tests whether this remaining floor is input measurement error rather
than a failure of factor existence.

## Paired limit

The score opportunity count is:

\[
K_s\in\{1,4,16,64,\infty\}.
\]

`0` in machine artifacts denotes the noiseless \(K_s=\infty\) limit. Target
opportunities remain fixed at four. Every finite \(K_s\) within a root shares
the same latent factors, target observations, and prefix-compatible score
noise stream.

The frozen R2G discovery choices are reused:

- linear rank 4 for `common_low_rank`;
- quadratic rank 4 for `nonlinear_common`;
- rank 0 for `pure_iid` and `irreducible_common_shock`.

No rank, map, or threshold is selected in R2G.1.

## Sample-size boundary

Training group counts `{32,128}` separate:

- factor-score resolution, controlled by \(K_s\);
- mapping-estimation precision, controlled by training groups.

Confirmation always uses 128 fresh groups.

## Decision

`PASS_FACTOR_COMPLETENESS_LIMIT` requires, for both noise families and at
128 training groups:

- linear and nonlinear learned residuals reach practical zero at
  \(K_s=\infty\);
- pure iid remains practically zero;
- the score-unavailable common shock retains a floor above `.01`;
- finite-to-infinite phi and floor decrease in both completable worlds.

This is an existence result under noiseless factor observation. It does not
state that finite text can reach the limit, or that the recovered factors are
psychological constructs.

