# V8 Adaptive Rank and Fixed Reference V3.7E Report

Decision:
`V8_ADAPTIVE_RANK_FIXED_REFERENCE_V37E_PASS_MISSPECIFICATION_EXPLAINED`

Methodology ruling: `PASS_WITH_CAVEATS`

## Question

V3.7D showed a reverse separation at true rank 12: a fixed rank-8 estimator
could identify authors while failing to recover the full operator. V3.7E
tested whether that state survives when rank is selected without true-rank
access and when profiles are tied to an external reference design.

Three estimators used the same event panels:

- fixed rank 8;
- adaptive rank selected by four-fold author-level cross-session prediction;
- true-rank oracle used only by the scorer.

Reference, calibration, and evaluation authors were disjoint
`256/128/96` sets.

## Integrity

- Canonical seed: `20410617`; 60 fresh worlds; 960 registered cells.
- All 16 frozen checks passed.
- The V3.7E prospective seal and V3.7D parent seal passed.
- All 3,960 metric-recorded seeds were unique.
- External reconstruction found 9,840/9,840 unique component streams and
  zero overlap with 3,280 smoke/discovery streams.
- The artifact inventory passed 6/6.
- No external labels or raw identifiers were read.

## Adaptive capacity result

For the flat-spectrum 128-event arm:

| True rank | Selected rank | Fixed truth r | Adaptive truth r | Oracle truth r | Fixed hard AUC | Adaptive hard AUC |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 4 | .977 | .982 | .982 | .925 | .938 |
| 8 | 8 | .967 | .967 | .967 | .985 | .985 |
| 12 | 12 | .783 | .952 | .952 | .968 | .993 |
| 16 | 16 | .672 | .938 | .938 | .950 | .996 |

The one-standard-error selector chose the true flat-spectrum rank in every
registered population at both 64 and 128 events. It never selected the upper
rank-24 boundary. Under the decaying spectrum it selected effective rank
4--8 rather than literal rank 8--16, which is the intended behavior for a
predictive-rank selector.

At true rank 12:

- fixed rank8 identity-without-recovery rate: `.933`;
- adaptive identity-without-recovery rate: `.000`;
- adaptive recovery-plus-identity rate: `1.000`;
- Fisher-z fixed-to-oracle gap closure: `1.000 [1.000, 1.000]`;
- NRMSE gap closure: `1.000 [1.000, 1.000]`.

Thus the V3.7D rank-12 reverse state was caused by registered estimator
under-capacity. It was not a persistent property after adaptive capacity.

The session-pair permutation control selected rank 0 in all 60 worlds and
returned hard-neighbor AUC exactly `.500`.

## Fixed-reference stress

The opportunity arm planted a low-rank author-by-context response
\(B_u z_c\), changed context exposure, and averaged eight independent panels
to separate systematic transport bias from single-panel noise.

| Metric | Mean | Bootstrap 95% interval |
| --- | ---: | ---: |
| Standardized drift | .288 | descriptive |
| Naive exposure-weighted drift | .521 | descriptive |
| Drift reduction | .686 | [.669, .703] |
| Population-shift direction cosine | .998 | [.997, .998] |
| Population-shift amplitude | 1.006 | [.998, 1.014] |

The same planted shift measured against unprojected raw truth had amplitude
`.939`; the registered amplitude compares like with like in the selected
score space.

Recentring on the target cohort erased its mean shift by construction. A
router-only target refit without explicit cohort centering retained a mean
`.182` of the planted projected shift. This distinction prevents the
algebraic negative control from being misreported as empirical
identification.

## Theoretical correction

V3.7D established that recovery and identification are logically distinct.
V3.7E now separates two causes of recovery failure:

\[
\|D_u-\widehat D_u\|^2
=
\underbrace{\|(I-P_{\hat r})D_u\|^2}_{\text{capacity bias}}
+
\underbrace{\|P_{\hat r}D_u-\widehat D_u\|^2}_{\text{sampling error}}.
\]

The rank-12 reverse separation belonged to the first term. Author density
crowding belongs to the identity margin and is not repaired by rank
selection. The durable result is therefore asymmetric:

- accurate recovery need not imply individual identification in a crowded
  low-dimensional population;
- identification without recovery can occur under estimator
  misspecification, but did not persist after adaptive capacity in the
  registered flat-spectrum worlds.

## Licensed conclusion

Within this synthetic routing family, author-disjoint cross-session rank
selection can recover effective operator capacity, diagnose the V3.7D
rank-12 failure as fixed-rank misspecification, and preserve registered
opportunity/population contrasts against a frozen external router.

This does not establish an absolute external norm, universal rank selection,
single-author uncertainty, personality, real-text factors, clinical
assessment, or human change measurement.

## Artifacts

- `results/v8_adaptive_rank_fixed_reference/v37e_confirmation_final_20260726/decision.json`
- `results/v8_adaptive_rank_fixed_reference/v37e_confirmation_final_20260726/metrics.csv`
- `results/v8_adaptive_rank_fixed_reference/v37e_confirmation_final_20260726/cell_summary.csv`
- `configs/v8_adaptive_rank_fixed_reference_v37e_seal.json`
- `reports/V8_ADAPTIVE_RANK_FIXED_REFERENCE_V37E_EXTERNAL_SEED_AUDIT.json`
- `reports/V8_ADAPTIVE_RANK_FIXED_REFERENCE_V37E_INDEPENDENT_AUDIT.md`
