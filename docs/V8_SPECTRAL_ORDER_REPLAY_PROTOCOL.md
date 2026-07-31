# V8 Shared-Gauge Spectral-Order Replay Protocol

Status: `POST_HOC_REPLAY_PROTOCOL`

## Question

The local resolution experiment produced opposite nested masks:

- Essays appeared more spectrally concentrated than PANDORA for the
  order-free marginal family M.
- PANDORA appeared more spectrally concentrated than Essays for the
  order-specific transition family K.

Those directions were observed before this protocol. This experiment can
reject corpus-local scaling and unequal author count as sufficient
explanations, but it cannot provide a fresh independent confirmation.

## Estimand

For trace-one replicated density \(\rho\), descending eigenvalues
\(\lambda_1\ge\cdots\ge\lambda_d\), capacity \(c=k/d\), and sharpness budget
\(q\),

\[
\Gamma_\rho(c,q)=
\max_{0\preceq P\preceq I,\,
\operatorname{tr}P=k,\,
\|P-cI\|_F^2\le qk(1-c)}
\langle P-cI,\rho\rangle.
\]

At \(q=1\),

\[
\Gamma_\rho(k/d,1)
=
\sum_{i=1}^{k}\lambda_i-\frac{k}{d}.
\]

The complete \(q=1\) curve is the spectral Lorenz excess. It encodes the
ordered spectrum and is invariant under orthogonal rotation inside the
declared gauge. It is not invariant to changing that gauge.

## Design

- PANDORA and Essays are represented by exactly eight technical events per
  author.
- A pair-symmetric robust diagonal gauge is fitted on equal D0 author counts.
- No full whitening is allowed.
- D1 and D2 use the same author count in both corpora.
- D0 outer bootstrap refits the gauge and supplies a split-replication
  sup-norm tolerance.
- Author bootstrap supplies simultaneous bands over every nontrivial
  capacity.
- The registered directions are Essays minus PANDORA for M and PANDORA minus
  Essays for K.
- D1 defines the positive-capacity region. D2 evaluates that frozen region
  once.

The q=1 Lorenz curve is primary. The q<1 field is a consistency diagnostic,
not an additional independent discovery family. Haar rotation is not a
valid null because eigenvalues are rotation invariant.

## Decision

A family replay is supported only if:

1. D1 and D2 simultaneous lower curves stay above the D0 technical tolerance;
2. each contains at least one strictly positive region;
3. the D1-frozen region has positive D2 integrated advantage with a positive
   bootstrap lower bound.

## Boundary

A pass licenses a shared-gauge spectral-order candidate in these already
observed authors. It does not establish a common eigendirection, a
cross-corpus factor, personality, emotion, state, language universality,
causality, diagnosis, or clinical validity. Fresh authors or a new D3 are
required for confirmation.
