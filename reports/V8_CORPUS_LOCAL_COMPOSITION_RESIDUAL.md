# V8 Corpus-Local Composition Residual

Status: `CORPUS_LOCAL_COMPOSITION_RESIDUAL_NOT_DETECTED`

D0 natural sets freeze one rank-10 K support per corpus. D0 pseudo sets estimate context/replicate marginal-orbit baselines. D1/D2 test the Frobenius norm of signed cross-replicate covariance; no positive-part density is used.

## Result

| corpus   | split   |   rank |   observed_signed_frobenius |   pseudo_mean |   observed_minus_pseudo |   raw_p |   max_t_p |
|:---------|:--------|-------:|----------------------------:|--------------:|------------------------:|--------:|----------:|
| pandora  | D1      |     10 |                    116.883  |      116.679  |                0.203563 |    0.41 |     0.865 |
| pandora  | D2      |     10 |                    119.05   |      116.393  |                2.65658  |    0.3  |     0.8   |
| essays   | D1      |     10 |                     42.6993 |       45.0615 |               -2.36213  |    0.77 |     0.995 |
| essays   | D2      |     10 |                     44.3655 |       46.5701 |               -2.20457  |    0.75 |     0.995 |

## Claim boundary

Exploratory corpus-local signed composition-residual test on opened authors. D0 natural sets freeze a rank-10 K support; D0 pseudo sets estimate context/replicate marginal-orbit baselines. D1/D2 use signed cross-replicate covariance without positive-part projection. A pass licenses a corpus-local stable event-composition residual only, not cross-corpus transport, sequence dynamics, personality, cognition, diagnosis, or clinical validity.
