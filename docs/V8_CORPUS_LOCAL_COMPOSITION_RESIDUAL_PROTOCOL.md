# V8 Corpus-Local Composition Residual Protocol

Status: exploratory protocol on already-opened PANDORA and Essays authors.

The cross-corpus event-set knockout showed that common EPSG is reproduced by
conditioned event marginals. This final K-branch test asks a different
question: does natural event grouping leave a stable residual within either
corpus, even if that residual is not shared across corpora?

For each corpus, natural D0 sets freeze a rank-10 K support. Ninety-nine D0
pseudo-set worlds estimate context- and technical-replicate-specific
marginal-orbit means. Every author's projected orbit covariance is vectorized
with the standard \(\sqrt 2\) off-diagonal scaling, preserving Frobenius inner
products, and the D0 pseudo mean is subtracted:

\[
r_{u,r}^{comp}
=
\operatorname{vec}_{sym}
[U_c^\top \mathcal G_K(\mathcal M_{u,r})U_c]
-
E_{\sigma,D0}
\operatorname{vec}_{sym}
[U_c^\top \mathcal G_K(\mathcal M^\sigma_{u,r})U_c\mid context,r].
\]

The primary statistic is the Frobenius norm of signed cross-replicate
covariance:

\[
T_c^{comp}
=
\left\|
\frac12
\left[
\operatorname{Cov}_u(r_{u,0},r_{u,1})
+
\operatorname{Cov}_u(r_{u,1},r_{u,0})^\top
\right]
\right\|_F.
\]

No positive-part projection is used. D1 and D2 are compared with 199
context/slot/local-length-matched pseudo-set worlds in one four-cell maxT
family.

A two-split pass within one corpus licenses only a
`corpus-local stable composition residual`. It does not license cross-corpus
orientation, sequence dynamics, personality, cognition, diagnosis, or
clinical validity. If both corpora fail, the K composition/sequence branch is
closed and the conditional marginal orbit-susceptibility operator is the
final explanation under this design.
