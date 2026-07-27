# V8 V3.7H.4D R2B Independent Theory Audit

Date: 2026-07-27

Ruling:
`ACCEPT_GEOMETRY_MATTERS / REJECT_OPERATOR_SUFFICIENCY`

## Accepted evidence

- All 12,600 rows and 1,800 seven-geometry base blocks are complete.
- Information matching, source locks, projection checks, and seed uniqueness
  passed.
- Outer prediction simultaneously held out the target geometry family and
  the target base seeds.
- The four paired iid-minus-intrinsic lower confidence bounds exceed .10.
- Operator gains in log loss, Brier score, and the intrinsic held-out family
  are positive beyond their registered thresholds.

The defensible theorem is limited to the frozen synthetic detector:

\[
\text{scalar precision energy is not sufficient for detector power,}
\]

and geometry-aware information improves cross-family prediction.

## Audit qualifications

1. The repository was dirty. Manifests establish artifact consistency, not
   an externally timestamped preregistration.
2. The design document names ten geometry coordinates, while the formal
   predictive config uses six. The exact six-coordinate config, rather than
   the broader prose list, defines the executed model.
3. The sign-support direction gate used a full-data clustered GLM, whereas
   the primary comparison used grouped LOGO ridge prediction.
4. Effective sign support and author-energy support are nearly perfectly
   collinear in this DGP. The sign coefficient therefore cannot carry the
   intended interpretation.
5. Bootstrap intervals condition on the already fitted out-of-fold models;
   they do not include complete algorithm-refitting uncertainty.
6. Family-mean calibration understates the local halo failure. The
   \(m=4,\lambda=.03\) cell has observed power 1.00 but predicted power only
   about .25-.28.
7. All operator descriptors are oracle synthetic quantities derived from
   planted interaction and expected variance. Operational estimation from
   observed text remains open.

## Required correction

Do not lower the failed gates and do not add geometry labels. Retire the
unidentified sign-coefficient gate. The next prospective experiment must
model the finite author-level permutation orbit itself, using a mechanism
panel independent of the final outcome panel.

For author contributions

\[
z_u=\langle R_{2u},R_{3u}\rangle,\qquad
p_u=\frac{|z_u|}{\sum_v|z_v|},
\]

retain the contribution-support spectrum

\[
N_1=\exp\left(-\sum_u p_u\log p_u\right),\quad
N_2=\left(\sum_u p_u^2\right)^{-1},\quad
N_\infty=(\max_u p_u)^{-1},
\]

and estimate the probability that an independent 99-draw, three-channel
Holm procedure rejects. The mechanism score must not read the outcome panel,
geometry label, or final detector result.

Promotion requires fresh-seed calibration across halo strengths, support
sizes, and both noise modes. If only oracle descriptors work, retain the
mathematical mechanism and reject operational measurement claims.
