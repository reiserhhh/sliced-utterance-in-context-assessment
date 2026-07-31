# V8 Capacity-Conditioned Support-Coverage Protocol

Status: `EXPLORATORY_MECHANISM_AUDIT__NO_RESULT_ASSUMED`

Date: 2026-07-29

## 1. Why this audit exists

The first real-text transport screen accepted PANDORA as a source for Essays
and X, but only the marginal family M determined that direction. The
transition residual \(K^\circ\) passed every direction. The original
retained-energy statistic can reward a broad, nearly identity-like source
and uses a source-specific floor. It therefore cannot establish support
containment.

This post-result mechanism audit asks a narrower question:

> Under equal text opportunity and a common technical metric, does one
> corpus's replicated support cover another corpus's confirmation density
> better than the reverse direction?

## 2. Equal-opportunity panels

PANDORA, Essays, and X are rebuilt with exactly eight text events per author.
Every comparison uses equal author counts from the two corpora. D0 fits the
metric and filters; D1 and D2 provide independent author confirmation.

Two metrics are frozen:

1. a pair-symmetric robust diagonal metric fitted with equal D0 authors from
   the two corpora;
2. a global robust diagonal metric fitted with equal D0 authors from all
   three corpora.

No pooled full whitening is allowed because it can manufacture complementary
spectra. The global arm prevents pair-specific gauges from being interpreted
as a transitive PANDORA--Essays--X atlas.

## 3. Soft capacity filter

For trace-one density \(\rho_s\), dimension \(d\), capacity \(k\), and
regularization \(\tau>0\), define

\[
P_s(k,\tau)
=
\arg\max_{\substack{0\preceq P\preceq I\\\operatorname{tr}P=k}}
\left[
\operatorname{tr}(P\rho_s)
-
\frac{\tau}{2}
\left\|P-\frac{k}{d}I\right\|_F^2
\right].
\]

If
\(\rho_s=U_s\operatorname{diag}(\lambda_i)U_s^\top\), then

\[
P_s
=
U_s\operatorname{diag}(p_i)U_s^\top,
\qquad
p_i
=
\operatorname{clip}
\left(
\frac{k}{d}+\frac{\lambda_i-\mu}{\tau},
0,1
\right),
\]

where \(\mu\) enforces \(\sum_i p_i=k\).

The frozen grid is

\[
k\in\{4,8,16,24,32\},
\qquad
\tau=m\,\sigma_{\mathrm{pair}},
\quad
m\in\{0.5,1,2,4\},
\]

with \(\sigma_{\mathrm{pair}}\) the RMS spectral departure of both D0
densities from \(I/d\). Results are averaged over the full grid; no best cell
is selected.

## 4. Target-normalized directional coverage

For held-out target density \(\rho_{t,h}\), define

\[
L_{t,h}(P)
=
\operatorname{tr}(P\rho_{t,h})
-
\frac{\tau}{2}
\left\|P-\frac{k}{d}I\right\|_F^2.
\]

The source-covers-target statistic is

\[
C_{s\to t}^{(h)}(k,\tau)
=
\frac{
L_{t,h}(P_{s,0})-k/d
}{
L_{t,h}(P_{t,0})-k/d
}.
\]

Both numerator and denominator are evaluated on the same target density.
The denominator must be positive on at least 80% of the frozen grid; otherwise
the target's native D0 filter has not replicated and the comparison is
refused.

Directional asymmetry is

\[
A_{s,t}^{(h)}
=
\overline C_{s\to t}^{(h)}
-
\overline C_{t\to s}^{(h)}.
\]

Positive \(A\) means the source D0 support covers the target confirmation
density more completely than the reverse direction under the registered
capacity grid. It does not mean literal subspace inclusion.

## 5. Controls and decisions

Every directional result must survive:

- D1 and D2 author-disjoint confirmation;
- 199 author bootstraps;
- full-spectrum Haar-rotation null with Holm correction;
- 39 matched D0 subsamples with at least 80% sign recurrence;
- complete eigenspectrum matching, preserving only orientation;
- the three-corpus global metric with the same direction;
- within-corpus D0 split reliability;
- equal authors and equal eight-event opportunity.

The decision taxonomy is:

- `APPROXIMATE_DIRECTIONAL_COVERAGE_CANDIDATE`: all controls pass and the
  chosen direction's lower interval is at least .80 while the reverse upper
  interval is below .80;
- `DIRECTIONAL_COVERAGE_ASYMMETRY`: all directional controls pass without the
  .80 separation;
- `SHARED_ORIENTATION_NO_DIRECTION`: both orientations exceed the corrected
  rotation null but direction is unresolved;
- `D0_SUPPORT_NOT_REPLICATED`, `NATIVE_SUPPORT_UNDERRESOLVED`, or
  `COVERAGE_UNDERRESOLVED`: the corresponding prerequisite failed.

## 6. Claim boundary

This is an exploratory label-free technical audit designed after observing
the initial transport pattern. It may revise the interpretation of that
pattern. It cannot establish a universal language space, a personality
space, causal transport, a clinical measurement, or cross-language
equivalence.

