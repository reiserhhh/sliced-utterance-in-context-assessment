# V8 Common-Ball Incremental V3.4 Independent Audit

Decision: `PASS_TECHNICAL_PLANTED_ONLY`

## Verified

- All 11 prospective-seal hashes match the executed files.
- The run manifest and all nine result-artifact hashes verify.
- The five targeted tests pass.
- Across 500 paired confirmation populations, both the complete per-view
  tensor \(A_{ijz\epsilon v}\) and its view-intersected form had zero
  mismatches. An independent recomputation also found zero mismatches.
- All three pairwise comparators returned identical paired outputs 500/500.
- The MEB estimator claimed the feasible six-author groups 500/500
  (one-sided 95% lower 0.9940) and claimed the infeasible six-author groups
  0/500 (one-sided 95% upper 0.00597).
- The paired decision delta was 1.000 with bootstrap 95% CI [1.000, 1.000].
- All four 200-population controls passed.

## Accepted theorem

For the registered finite threshold grid, there exist paired configurations
\(X^+\) and \(X^-\) such that

\[
A(X^+)=A(X^-),
\qquad
\rho_{\mathrm{MEB}}(X^+)=0.90R,
\qquad
\rho_{\mathrm{MEB}}(X^-)=1.10R.
\]

Therefore no function of that binary pair-adjacency tensor alone can
correctly determine common-ball feasibility in both worlds.

The strict accepted statement is:

> Complete binary pair adjacency on the registered finite threshold grid
> does not determine multi-author common-ball feasibility.

The plan wrote this operationally as conditional information. The run did
not estimate conditional mutual information numerically; the result is more
precisely a constructive non-identifiability counterexample.

## Required limits

This is not evidence that pairwise geometry is insufficient. The continuous
distance matrices differ. A complete Euclidean distance matrix determines

\[
G=-\frac12 J D^{\circ2} J
\]

and therefore the point configuration up to isometry, including its minimum
enclosing ball. V3.4 establishes information lost by finite binary
thresholding, not information beyond complete continuous distance geometry.

The adjacency tensor already exposes the four planted groups. MEB adds only
whether all six members share one ball; it does not discover a new group.
Perfect recovery is expected in this deliberately separated, low-noise
planted construction and demonstrates identifiability rather than empirical
prevalence.

The internal content-hash seal predates the results and verifies, but the
worktree is dirty and the files are uncommitted. It is not an immutable
third-party preregistration.

## Psychological boundary

Intersection multiplicity, incident-line count, and common-ball feasibility
cannot currently be called personality similarity. The accepted technical
name is:

> same-condition multi-author common-center feasibility.

Topic, prompt, expression opportunity, platform, embedding geometry, or
observer bias can produce the same structure.

## Next real-text gate

Use fresh authors under genuinely shared fixed conditions, with at least two
independent texts or views per author-condition. Freeze the representation,
radius grid, threshold, and refusal rules on discovery data. Confirmation
must include condition/topic-matched nulls, author/view shuffles, observer
perturbations, boundary refusals, and a full continuous-distance comparator.

Only a relation that is stable across views, exceeds matched nulls, and later
links to independent psychological or behavioral evidence may be discussed
as a candidate personality-similarity signal.
