# V8 V3.7H.4D R2C Independent Theory Audit

Date: 2026-07-27

Ruling:
`ACCEPT_GROUP_CELL_ORBIT / REJECT_INDIVIDUAL_CONDITIONAL_ORBIT`

## What R2C estimated

R2C estimated:

\[
\Omega(M)=P_S\{D(M,S)=1\mid M\},
\]

where the observed mechanism panel \(M\) is held fixed and only the
wild-sign randomization stream \(S\) is redrawn.

The individual prediction target is different:

\[
\pi^\star(M)=P\{D(O,S)=1\mid M\},
\]

where \(O\) contains new opportunity counts, measurement noise, panel shock,
mask, and residualization error.

R2C integrated the first source of randomness but not the second.

## Audit findings

- Source locks, 10,800 rows, 1,200 paired bases, information matching, and
  panel separation passed.
- The halo discontinuity replicated on fresh seeds with lower confidence
  bounds .877/.863.
- The row-level machine `REFUTED` decision is correct: orbit log loss was
  approximately 1.110 versus .447 for frozen R2B.
- Exact orbit probabilities of one occurred 4,397 times, but 286 of those
  independent outcomes did not reject.
- Within-cell support-spectrum correlations of .628/.775/.790 reject the
  interpretation of pooled .995/.994/.960 correlations as individual
  reliability.
- The 36 cell confidence bounds are cellwise, not a simultaneous 36-cell
  familywise interval.

## Group calibration boundary

Within a registered cell \(C\), panels 0/1 and 2/3 are conditionally
exchangeable. Therefore:

\[
E[\Omega(M)\mid C]
=
P\{D(O,S)=1\mid C\}.
\]

The low mean cell error verifies this exchangeability and the implementation
of the finite detector orbit. It is not evidence that \(\Omega(M)\) explains
which particular base world will reject.

The nontrivial R2C findings are:

1. diffuse halo changes the finite randomization frontier;
2. the orbit reconstructs registered population-cell power;
3. it does not provide stable within-cell conditional prediction.

## Required next object

Probability clipping or an outcome-fitted calibration curve is invalid. The
missing estimand is posterior predictive:

\[
\pi^\star(M)
=
\int
P\{D(O,S)=1\mid Q,\psi\}
\,p(Q,\psi\mid M,\mathcal C)\,dQ\,d\psi,
\]

where \(Q\) is stable latent interaction, \(\psi\) contains opportunity and
noise parameters, and \(\mathcal C\) is independent calibration evidence.

With only two mechanism panels, \(Q\) and unknown measurement variance are
not nonparametrically separable. Any operational result must either use
independent repeated-panel/W0 calibration or refuse.
