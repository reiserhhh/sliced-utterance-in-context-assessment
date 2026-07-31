# V8 Spectrum-Matched Orientation-Overlap Protocol

Status: `EXPLORATORY_PROTOCOL_AFTER_SPECTRAL_ORDER_REFUSAL`

## Question

The shared-gauge replay did not establish that either corpus spectrally
majorizes the other. Spectral concentration and direction overlap are
logically independent. This audit asks whether PANDORA and Essays place their
replicated anisotropic mass in approximately similar directions after their
spectra are matched.

## D0 template

For corpus \(s\),

\[
A_s^{(\epsilon)}
=
U_s\operatorname{diag}
\left[(\lambda_{s,i}-1/d-\epsilon)_+\right]U_s^\top .
\]

D0 technical halves calibrate \(\epsilon\). The shared rank is the smaller
identified rank, capped at 48. For identified strengths
\(\alpha_{P,i},\alpha_{E,i}\), the matched spectrum is

\[
\bar\alpha_i
=
\frac{\sqrt{\alpha_{P,i}\alpha_{E,i}}}
{\sum_j\sqrt{\alpha_{P,j}\alpha_{E,j}}}.
\]

Near-degenerate D0 blocks receive equal weights. Both corpora then have the
same spectrum, so remaining differences are directional.

## Metrics

Primary:

\[
S_{\mathrm{HS}}
=
\frac{\operatorname{tr}(\Sigma_P\Sigma_E)}
{\sqrt{\operatorname{tr}(\Sigma_P^2)
\operatorname{tr}(\Sigma_E^2)}}.
\]

Secondary:

\[
S_F
=
\left\|\Sigma_P^{1/2}\Sigma_E^{1/2}\right\|_*.
\]

Diagnostic:

\[
S_{\mathrm{PA}}
=
\frac1r\|U_P^\top U_E\|_F^2.
\]

The PSD parallel sum is retained only as an exact-intersection concept:
\(\operatorname{Ran}(A:B)=\operatorname{Ran}(A)\cap\operatorname{Ran}(B)\).
Noisy low-rank subspaces generically have zero exact intersection, so a zero
parallel sum cannot refute approximate directional overlap.

## Controls and boundary

- one PANDORA/Essays shared robust gauge;
- equal event and author counts;
- D0 split-half orientation gate;
- native-spectrum and matched-spectrum arms;
- spectrum-preserving Haar null;
- author bootstrap including D0 gauge refitting;
- max-Haar correction across registered families, arms, and metrics.

Current D2 has already been used in the spectral replay. Any positive result
is exploratory and requires fresh D3 or new authors for confirmation. No
orientation result names personality, emotion, state, behavior, causality,
diagnosis, or clinical validity.
