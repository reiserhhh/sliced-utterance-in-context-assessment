# V8 Permutation-Orbit Set/Phase Protocol

Status: exploratory protocol on already-opened PANDORA and Essays authors.

For one four-event multiset \(\mathcal M_{ur}\), enumerate every
\(\pi\in S_4\) and define

\[
\mu_{ur}=E_\pi K(\pi\mathcal M_{ur}),\qquad
V_{ur}=\operatorname{Cov}_\pi[K(\pi\mathcal M_{ur})],
\]

\[
z_{ur}(\pi)=K(\pi\mathcal M_{ur})-\mu_{ur}.
\]

The event-set susceptibility object is

\[
G_c^{set}=E_{u,r}[V_{ur}].
\]

It records what variation the unordered event sets permit under reordering.
It is not evidence that the observed order carries information.

Its cross-corpus test uses two nested nulls. A full Haar null tests arbitrary
orientation. The primary block-Haar null preserves the four frozen K feature
families (lag product 64, delta variance 64, transition RFF 16, current 8)
and their spectra while rotating coordinates within each block. This prevents
the shared feature-map architecture from being counted as data-specific
cross-corpus geometry.

After fitting one equal-corpus D0 diagonal feature gauge, every orbit is
regularized in its own support:

\[
q_{ur}(\pi)
=
z_{ur}(\pi)
\left(
V_{ur}+\alpha\bar\lambda_{ur}I
\right)^{-1/2},
\qquad \alpha=.10.
\]

The implementation evaluates the equivalent thin-SVD expression, so null
directions are never inverted. The observed phase is \(q_{ur}(id)\). Its
replicated covariance is compared with 1,999 worlds that independently choose
one of all 24 orders for every author, technical replicate, and corpus, then
rebuild the full density-to-orientation statistic. HS/fidelity across D1/D2
share one maxT family.

The four possible rulings are:

| set geometry | phase excess | interpretation |
| --- | --- | --- |
| detected | not detected | common permutation susceptibility only |
| detected | detected | susceptibility plus sequence-sensitive phase |
| not detected | detected | phase without common set geometry |
| not detected | not detected | no stable decomposition under this operator |

Even a phase detection would establish sequence-sensitive adjacency structure
only. It cannot establish time direction, cognition, personality, diagnosis,
universality, or clinical validity. Fresh authors are required for
confirmation.
