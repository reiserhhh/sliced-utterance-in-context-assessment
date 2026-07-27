# V3.7G Post-Confirmation Metric Erratum

Date: 2026-07-26

This is a post-confirmation correction. It does not modify any file covered
by `configs/v8_reliability_spectrum_v37g_seal.json`.

The theory candidate's internal status line says `NOT_YET_SEALED` because it
records its prospective state. The external seal now fixes that exact file;
the historical line is intentionally not rewritten after confirmation.

## Correction

The sealed confirmation plan and theory candidate use the label `NRMSE` for
one registered comparison. The implementation actually computes normalized
mean squared error:

\[
\operatorname{NMSE}(\widehat G,G)
=
\frac{\mathbb E\|\widehat G-G\|^2}
{\mathbb E\|G-\mu_0\|^2}.
\]

No square root is taken. This agrees with:

- the function name `normalized_mse`;
- the output columns `selected_nmse`, `hard_nmse`, and `oracle_nmse`;
- the frozen config keys `maximum_exact_excess_nmse`;
- the decision implementation.

The result is therefore interpreted only as a registered **NMSE** result.
The sealed prose label `NRMSE` is erroneous.

## Consequence

The canonical NMSE reductions are:

- dense-tail: 28.94%;
- broken-spectrum: 20.69%.

If the same point ratios are transformed to a square-root normalized-error
scale, their reductions become approximately:

- dense-tail: 15.71%;
- broken-spectrum: 10.94%.

Those transformed values do not meet 20% and 15% thresholds. V3.7G therefore
does not claim that an NRMSE experiment passed.

The canonical coded decision remains a valid NMSE decision because code,
config field names, stored metrics, and decision arithmetic all agree on
NMSE. The prose conflict nevertheless weakens preregistration clarity and
must be treated as a major caveat.

## Governance

Future preregistrations must include the metric equation next to every gate,
not only an abbreviation. A seal-time test must also assert the exact metric
name and transformation used by the implementation.
