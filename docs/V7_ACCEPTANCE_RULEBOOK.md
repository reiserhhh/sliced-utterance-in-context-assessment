# V7 Evidence and Promotion Rulebook

This document records evidence states for V7.  It is not a legacy lockbox and
not a mechanism for cancelling exploratory branches because they do not match
older Big Five/MBTI results.

## Evidence Labels

Every V7 run writes an append-only discovery ledger.  A row must state the
operator, source population, fitted artifacts, author split, feature schema,
support rule, error rule, and result status.  Candidate IDs use anonymous
codes such as `SU7-FC-0001@v1`; names are prohibited at this stage.

## Slice-Family Rule

Each slicing scheme is an explicitly indexed observation operator. A failed
universal precision comparison does not delete the operator or relabel its
private structure as noise. Conversely, high agreement between two operators
does not permit their scores to be silently pooled. Any consensus score needs
a discovery-fitted aggregation rule and independent confirmation; any
view-private score must retain its operator index and uncertainty record.

## What a First-Pass Operator Result Can Establish

| Evidence | Permitted conclusion | Not permitted |
| --- | --- | --- |
| Reproducible feature matrix | Text has a repeatable representation under this operator. | A trait was measured. |
| Frozen score on unseen authors | An author-relative coordinate can be produced without refitting. | The coordinate is a personality score. |
| Low unit-bootstrap SEM | The score is technically stable under resampling these observations. | Cross-day or cross-situation reliability. |
| Disjoint-observation correlation | This operator has within-document technical consistency. | Trait stability or clinical reliability. |
| Discovery/confirmation subspace similarity | A population structure transports within this corpus/sampling design. | Universality across languages, platforms, or cultures. |

## Promotion Logic

An operator is retained for deeper V7 analysis when it is executable, gives
unseen authors a frozen score, declares its refusal region, and returns
technical error information.  It is labelled `L2_SCOREABLE_CANDIDATE` only
after these artifacts are saved.  It is labelled `L3_INTERNALLY_REPLICATED`
only when confirmation data were never used to fit its representation,
aggregation, factor loadings, or norms.

There is deliberately no global numerical cutoff in this first rulebook. The
next evidence stage compares uncertainty, support coverage and transport
across observation operators. A weak result is logged as an empirical
property, not rewritten into a psychological null.

These labels are local implementation milestones, not a single evidence
ladder. The authoritative structure is the multidimensional lattice in
`docs/V7_EVIDENCE_STATUS_LATTICE.md`. Geometry replication, scoreability,
conditional uncertainty, repeated-measurement reliability, external validity,
and cross-domain transport must be reported separately.

## V7.2 Reproducibility Gate

An `IMPLEMENTATION_ACCEPTED` V7 projection run must contain all of the
following before any numerical result is quoted:

1. a schema-valid frozen bundle or multiview runtime;
2. discovery/calibration/confirmation split provenance;
3. a full admissible rank search and calibration one-standard-error selection;
4. bootstrap feature-space loading-subspace alignment;
5. persisted scalers, representations, maps and model runtime;
6. a replay fixture plus saved expected confirmation values; and
7. an artifact SHA-256 inventory that passes on reload.

If selected rank equals the admissible maximum, report
`RANK_UNRESOLVED_AT_ADMISSIBLE_BOUNDARY`. If the shared loading subspace
recurs but anonymous axis matching does not have a positive assignment margin,
report `FACTOR_AXES_NOT_IDENTIFIED_SUBSPACE_ONLY`. Neither condition can be
resolved by naming or deleting axes.

## V7.3/7.4 Remediation Outcomes

W2 established a required distinction between raw cross-view covariance and a
train-fitted context-adjusted estimand in simulation. W3 established that
source-disjoint temporal geometry must be compared to equal-budget random
source halves; temporal ordering is not a privileged stability test. W4
compared consensus covariance, concat-PCA, and ridge SUMCOR RGCCA under
correspondence-breaking nulls. All methods can pass a technical shared-geometry
test, but rank selection reached the registered grid boundary at both 8 and 16
in independent cohorts. Thus rank is an algorithmic capacity parameter, not a
factor count. The complete status is recorded in
`docs/V7_REMEDIATION_CLOSURE.md`.

An internally replicated geometry may be recorded even while reliability and
external validity remain untested. However, no psychological, personality,
clinical, temporal-trait, or cross-domain score claim is permitted without its
own repeated-measurement, anchor, uncertainty, and transport coordinates.

## E2 Condition/Opportunity Accounting

E2 treats recorded context as a measured surface, not an automatic nuisance.
Its three distinct questions must remain distinct in the ledger:

1. **Observed selection recurrence:** does an author's context-choice profile
   recur across source-disjoint halves relative to the discovery population?
2. **Context-surface predictability:** does the discovery-fitted recorded
   surface predict a material amount of comment-vector variation?
3. **Context transport:** does the context-carried author component predict
   the total author configuration in held-out authors?

An exchangeable matched partial screen is a fourth, separate test of residual
author alignment under declared observed matching. It must construct disjoint
strata only from calibration-frozen metadata and permute B identities only
within those strata. A candidate-pool or unrestricted-author derangement null
is nonexchangeable and must return `REFUSE_INVALID_MATCHED_NULL`. Passing one
endpoint cannot substitute for another. In particular, strong same-author
retrieval of the context-carried component is not proof that context
reconstructs total author structure, and none of these endpoints licenses a
causal, trait, clinical, or personality conclusion.

## Prohibited Shortcuts

- Do not select an operator because it maximises an external scale correlation
  in the same data.
- Do not refit TF-IDF, dimensional reduction, aggregation scaling, factor
  loadings or norms on calibration/confirmation authors.
- Do not replace unavailable SEM with zero.
- Do not turn same-author retrieval or AUC into personality validity.
- Do not use the V3/V4 lockbox as a V7 gate.
- Do not residualize topic, situation, or selection by default merely because
  they predict text; first declare the estimand and record what signal the
  transformation removes.
- Do not average, concatenate, or select between slice views after inspecting
  confirmation endpoints without registering that operation as a new operator.
- Do not treat a non-significant operator difference as evidence that a
  view-private component is absent. Use `UNRESOLVED_VIEW_SPECIFIC` unless a
  separately registered equivalence / recurrence design supports a stronger
  conclusion.
- Do not open external labels until the bundle hash, untouched anchor cohort,
  and multiplicity plan pass `validate_suica_v7_external_anchor.py`.
- Do not estimate free-choice `q` from text without logged exposure menus, or
  fixed-condition response `B` without independently randomized repeated
  conditions. The validators must refuse those cases.
