# V8 Scale-Free Replicated-Density Resolution Protocol

Status: `FORMAL_REAL_TEXT_TECHNICAL_PROTOCOL`

## Objective

This protocol asks whether a replicated real-text density contains a
reproducible anisotropic region at any capacity without selecting a hard
factor rank. It separates four statements that earlier drafts conflated:

\[
\text{replicated anisotropic density}
\not\Rightarrow
\text{capacity compressibility}
\not\Rightarrow
\text{cross-corpus coverage}
\not\Rightarrow
\text{cross-family relation}.
\]

## Scale-free filter

For a trace-one replicated PSD density \(\rho\), dimension \(d\), capacity
\(c=k/d\), and sharpness budget \(q\in(0,1]\), define

\[
\mathcal P(c,q)=
\left\{
P:
0\preceq P\preceq I,\ 
\operatorname{tr}P=k,\ 
\|P-cI\|_F^2\le qk(1-c)
\right\}.
\]

The resolution gain is

\[
\Gamma_\rho(c,q)=
\max_{P\in\mathcal P(c,q)}
\langle P-cI,\rho\rangle.
\]

The sharpness constraint is an upper bound. If the spectrum has a tied
eigenspace, the invariant optimizer may use less than the budget. The
implementation reports both requested and achieved sharpness and never
manufactures an arbitrary hard axis inside a tie.

## Data and information order

- Every corpus contributes exactly eight technical events per author.
- D0 is split into a filter-fit and an internal replication half.
- The D0 density must replicate against its Haar orientation null.
- The complete path \(k=1,\ldots,d-1\) and frozen
  \(q\in\{.10,.25,.50,.75,1\}\) are evaluated.
- D1 discovers a region with one simultaneous author-bootstrap band and one
  maximum-Haar family.
- D2 confirms only cells discovered by D1.
- X is refused if D1 or D2 has fewer than 48 authors.

The tau-indexed frontier is retained as a development artifact only. Tau is
the dual variable used to solve a fixed \(q\), not a cross-corpus parameter.

## Claim boundary

A confirmed cell means that a D0-fitted capacity-limited filter retains
replicated anisotropic density in both D1 and D2 beyond the isotropic and
rotation controls. It does not identify a hard factor, prove a low-rank
model, establish common directions across corpora, or name personality,
emotion, state, behavior, causality, diagnosis, or clinical validity.
