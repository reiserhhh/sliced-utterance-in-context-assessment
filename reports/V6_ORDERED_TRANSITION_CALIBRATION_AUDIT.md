# SUICA V6 J3 Calibration Audit

## Calibration revision before any PANDORA dynamic endpoint

The first synthetic J3 calibration used absolute delta-AUC targets. It failed:
authors with a common serial process but different static path variances could
produce nonzero real-minus-shuffled differences. This was not a reason to
relax the gate. It showed that the question is discriminability between a
variance-heterogeneous null and an author-specific transition alternative.

The frozen v2 calibration therefore uses relative separation:

\[
Q_{0.05}(\Delta_{\mathrm{moderate}}) >
Q_{0.95}(\Delta_{\mathrm{null}}),
\qquad
\mathrm{median}(\Delta_{\mathrm{weak}}) >
\mathrm{median}(\Delta_{\mathrm{null}}).
\]

It also searches longer per-view support (24 through 144 events). This revision
was made using synthetic data only, before real PANDORA ordered-transition
operators were constructed. It is an audit trail, not evidence about humans.
