# SUICA V7 Cross-View Effective-Rank Diagnostic

## Scope

This diagnostic describes the spectrum of split-centered off-diagonal cross-view covariance after subtracting a split-specific correspondence-breaking null envelope. It retains positive observed modes above the registered 95-percent null envelope. It measures distributed shared-text geometry in a frozen common-coordinate representation; it neither selects a factor count nor names components.

### Split Profiles

| representation     | split        |   n_authors |   n_positive_excess |   entropy_effective_rank |   participation_effective_rank |   excess_energy_90_rank |
|:-------------------|:-------------|------------:|--------------------:|-------------------------:|-------------------------------:|------------------------:|
| WORD12_TFIDF_SVD24 | discovery    |         120 |                  46 |                   32.034 |                         24.297 |                      31 |
| WORD12_TFIDF_SVD24 | calibration  |          36 |                  34 |                   21.457 |                         16.835 |                      19 |
| WORD12_TFIDF_SVD24 | confirmation |          44 |                  37 |                   22.750 |                         17.021 |                      21 |
| CHAR35_TFIDF_SVD24 | discovery    |         120 |                  45 |                   31.931 |                         24.673 |                      30 |
| CHAR35_TFIDF_SVD24 | calibration  |          36 |                  33 |                   20.238 |                         15.741 |                      18 |
| CHAR35_TFIDF_SVD24 | confirmation |          44 |                  37 |                   22.928 |                         16.720 |                      21 |

### Excess-Profile Similarity

| representation     | reference_split   | target_split   |   excess_profile_cosine |
|:-------------------|:------------------|:---------------|------------------------:|
| WORD12_TFIDF_SVD24 | discovery         | calibration    |                   0.984 |
| WORD12_TFIDF_SVD24 | discovery         | confirmation   |                   0.986 |
| CHAR35_TFIDF_SVD24 | discovery         | calibration    |                   0.976 |
| CHAR35_TFIDF_SVD24 | discovery         | confirmation   |                   0.978 |

## Decision

```json
{
  "status": "CROSSVIEW_EFFECTIVE_RANK_DESCRIBED",
  "rank_interpretation": "CAPACITY_DESCRIPTOR_NOT_FACTOR_COUNT",
  "spectrum_estimand": "POSITIVE_OBSERVED_MODES_ABOVE_SPLIT_SPECIFIC_BROKEN_CORRESPONDENCE_95_PERCENT_ENVELOPE",
  "null_calibration": "SPLIT_SPECIFIC_AUTHOR_COUNT",
  "coordinate_requirement": "Common frozen feature coordinates within one representation only.",
  "cohort_commitment": {
    "cohort_recipe": {
      "cohort_id": "v7.3-w4b-multiview-rank-extension-1",
      "seed": 20260716,
      "min_comments_per_user": 32,
      "max_users": 200
    },
    "n_authors": 200,
    "membership_sha256": "89c33105707a549d7d5ac2dfe77d5160c0d330e306904c920a620bff0384a677",
    "raw_identifiers_persisted": false
  },
  "confirmation_reused_from_w4b": true,
  "claim_boundary": "No factor count, personality, causal, clinical, or universal-language claim."
}
```

## Boundary

Entropy effective rank, participation rank, and 90%-energy rank are capacity descriptors of a representation-specific positive-excess covariance spectrum. They are not the number of human traits, scales, psychological factors, or clinical states. The method requires common frozen feature coordinates; it is not invariant to independent rotations, arbitrary domain transforms, or different embedding runtimes. Confirmation rows reuse the registered W4b cohort and are therefore a derived technical diagnostic, not a new independent replication.

Artifacts: `results/v7_multiview_spectrum/w4b_effective_rank_corrected_20260715`
