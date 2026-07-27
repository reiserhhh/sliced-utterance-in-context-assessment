# V8 V3.7H.1 R4 Independent Mathematical Audit

Date: 2026-07-26

Ruling:
`DESIGN_POWER_PASS_CONFIRMATION_NO_GO`

## Accepted

The implemented score-space statistic is dimensionally coherent:

\[
Q_m=
\frac{
\mathbb E\|\bar M^B_m-\bar M^A_m\|^2
-\widehat V_{\mathrm{stream},m}
}{
d^{-1}\operatorname{tr}
(W_m\widehat\Sigma_GW_m^\top)
}.
\]

Under independent, zero-mean technical streams, the two within-schedule
half-differences exactly estimate the technical contribution to the
schedule-mean difference. Heteroskedasticity alone does not invalidate this
identity. R4's \(Q\) tracks the scorer-side planted effect to within a maximum
cell-mean difference of approximately .00145.

The implementation also correctly makes paired \(Q\) the only operational
refusal channel. Cumulative \(\kappa\) is diagnostic.

The registered directional Clopper-Pearson decisions use \(\alpha/15\). The
null upper and material-power lower gates pass. These are separate one-sided
families, not a joint two-sided 95% interval over all reported lower and upper
tails.

## Identification failure still open

If technical streams are correlated, the null bias contains:

\[
b=
\frac1d\left[
\operatorname{tr}\Sigma_{A_1A_2}
+\operatorname{tr}\Sigma_{B_1B_2}
-2\operatorname{tr}\Sigma_{\bar A\bar B}
\right].
\]

A schedule-specific common shock is shared by the two technical streams and
therefore disappears from their difference. The current correction cannot
distinguish that shock from opportunity response. Heavy tails with finite
second moment do not necessarily create bias, but can invalidate the current
finite-sample threshold calibration.

`interval_claim_allowed=true` must mean only "not refused by this detector."
It cannot mean that condition invariance has been established.

## Confirmation ruling

Confirmation remains closed because:

- R4 is a developed power run, not a sealed fresh-seed confirmation;
- its DGP assumes independent Gaussian streams, correct pairing, and a
  persistent response affecting every author;
- common shock, correlated stream, heavy tail, pairing error, minority,
  near-kernel, transient, and reversal worlds remain open;
- the working tree is not clean or sealed;
- a single observed \(Q\) has no registered three-state uncertainty rule.

The next experiment is a repeated-opportunity common-shock identification
frontier. It must compare \(K=1\) with \(K=2,4,8\) and estimate schedule
variation across opportunity replicates rather than relying only on technical
stream differences.

