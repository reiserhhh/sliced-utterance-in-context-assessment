# SUICA V7 Observation-Operator Smoke Report

## Scope

This is a **label-free construction smoke test**. It compares observation
operators on a local PANDORA Tier-U reference cohort. Big Five, MBTI, external
criteria, old V3/V4 lockbox results, and raw user text were not used in factor
selection or scoring.

The report establishes only whether each operator can construct a frozen,
author-relative text-structure score with declared support conditions. It does
not name factors or claim personality, clinical, behavioural, or cross-domain
validity.

The four anonymous coordinates shown below are an **operational factor-count
probe** fixed in the run configuration. They are not a discovered factor
inventory or evidence that the underlying psychological object has four
dimensions. The reference cohort is a local eligibility-filtered sample, not
a PANDORA population norm.

## Run

- Config version: `v7-operator-smoke-1`
- Seed: `20260714`
- Schema report: `results/v7_operator_smoke/initial_full_final/data_schema.md`
- Artifact directory: `results/v7_operator_smoke/initial_full_final`

## Operator Summary

| operator   | kind     |   n_authors |   n_features |   n_factors |   confirmation_authors |   confirmation_scoreable_coverage |   median_unit_bootstrap_sem |   mean_technical_view_consistency |   subspace_similarity |   max_principal_angle_deg |   n_confirmation |   frozen_replay_max_abs_diff | evidence_status         | note                                                                                                        |
|:-----------|:---------|------------:|-------------:|------------:|-----------------------:|----------------------------------:|----------------------------:|----------------------------------:|----------------------:|--------------------------:|-----------------:|-----------------------------:|:------------------------|:------------------------------------------------------------------------------------------------------------|
| whole      | whole    |         180 |           48 |           4 |                     50 |                             1.000 |                     nan     |                           nan     |                 0.630 |                    79.833 |               50 |                        0.000 | L1_POPULATION_STRUCTURE | Score mapping exists, but this operator lacks adequate repeated-unit error evidence in this smoke run.      |
| native     | native   |         180 |           48 |           4 |                     50 |                             1.000 |                       0.415 |                             0.406 |                 0.671 |                    66.097 |               50 |                        0.000 | L2_SCOREABLE_CANDIDATE  | Frozen score, local reference norms, and technical unit-resampling diagnostics saved.                       |
| fixed_128  | fixed    |         180 |           48 |           4 |                     50 |                             1.000 |                       0.348 |                             0.431 |                 0.514 |                    88.776 |               50 |                        0.000 | L2_SCOREABLE_CANDIDATE  | Frozen score, local reference norms, and technical unit-resampling diagnostics saved.                       |
| semantic   | semantic |         180 |           48 |           4 |                     50 |                             1.000 |                       0.413 |                             0.347 |                 0.534 |                    85.997 |               50 |                        0.000 | L2_SCOREABLE_CANDIDATE  | Frozen score, local reference norms, and technical unit-resampling diagnostics saved.                       |
| nested     | nested   |         180 |          144 |           4 |                     50 |                             1.000 |                     nan     |                           nan     |                 0.657 |                    69.886 |               50 |                      nan     | L1_POPULATION_STRUCTURE | Nested feature-level scoring is frozen; paired multi-view resampling is deferred to the next V7 experiment. |

## Interpretation Rules

- `L2_SCOREABLE_CANDIDATE` means only that discovery-fit representation,
  aggregation, factor loadings and calibration norms can score confirmation
  authors without refitting, with local technical diagnostics saved.
- Technical view consistency is an even/odd observation comparison, **not**
  cross-day, cross-scenario, or personality reliability.
- `median_unit_bootstrap_sem` is uncertainty under resampling of the observed
  text units. It is unavailable by design for a one-unit whole-text operator.
- `subspace_similarity` is an author-disjoint within-corpus transport
  diagnostic, not a universality claim.

## Next Evidence Step

Freeze any executable L2 operator bundle, then compare it on independent
observation occasions or matched fixed/free text from the same people. Only
after that should external scales be joined as anchors.
