# V7 Fixed/Free Occasion Protocol

## Purpose

This protocol separates two quantities that natural text alone cannot identify:

\[
q_u(c)=P(C_{ut}=c\mid c\ \text{was exposed to }u),
\qquad
y_{ust}=\mu_{c_t}+a_{us}+B_u\phi(c_t)+\epsilon_{ust}.
\]

`q` is an author-conditioned **choice/opportunity profile** in a free phase.
`B` is an author-specific **response operator** in a fixed phase.  Neither is
a personality score, clinical assessment, or external-validity result at this
stage.

## Free Phase: Estimate q Only

Each row must log every exposed condition, not only the topic eventually
chosen. Required fields are `participant_id`, `session_id`, `opportunity_id`,
`condition_id`, `exposure_recorded`, and `selected`. The prompt menu must be
randomized or counterbalanced, with skip available and logged.

For each participant-condition cell, the registered estimator is the Jeffreys
posterior:

\[
\widehat q_{uc}=\frac{n_{uc}^{\mathrm{selected}}+1/2}
{n_{uc}^{\mathrm{exposed}}+1},
\]

with Beta\((n_{uc}^{\mathrm{selected}}+1/2,
n_{uc}^{\mathrm{exposed}}-n_{uc}^{\mathrm{selected}}+1/2)\) intervals.

Free text must **not** be used to estimate `B`: natural topic selection and
response are endogenous in that phase.

## Fixed Phase: Estimate B Only

Every participant completes each fixed condition on at least two independent
sessions. Condition order and assignment must be independently randomized per
session and logged in `assignment_randomized`. The required output is a frozen
text-geometry vector, not a named psychological trait.

Before fitting `B_u`, verify for each participant:

1. every condition has at least two distinct sessions;
2. the person-level condition design has full column rank;
3. residual degrees of freedom are positive; and
4. source, prompt, scorer, and observation-operator versions are frozen.

The fixed phase must **not** be used to estimate `q`, because exposure is
experimenter-controlled rather than freely selected.

## Refusal States

- `REFUSE_Q_OPPORTUNITY_UNOBSERVED`: text exists but the opportunity menu or
  non-chosen alternatives were not logged.
- `REFUSE_B_INSUFFICIENT_INDEPENDENT_REPLICATION`: fewer than two sessions per
  person-condition, rank deficiency, or no fixed phase.
- `REFUSE_B_NONRANDOMIZED_ASSIGNMENT`: condition assignment was not recorded
  as randomized.

The current MEPS + AI conversation material is a fixed-condition feasibility
source only. Unless its event-level exposure and independent repetition fields
are complete, it must remain outside q/B estimation, training, and external
validity claims.

## Repeated-Measurement Error Gate

Before estimating uncertainty, a generalizability coefficient, a state/trait
decomposition, or a minimum detectable change, the fixed phase must also pass
the stronger participant x condition x occasion preflight in
`docs/V7_REPEATED_MEASUREMENT_ERROR_PROTOCOL.md`. It requires frozen scorer,
representation, and window/operator versions as well as complete repeated
cells. Passing q/B design eligibility alone is not enough to claim a reliable
person score.

## Machine Check

```bash
python scripts/validate_suica_v7_fixed_free_dataset.py \
  --input path/to/occasion_rows.parquet \
  --output-dir results/v7_fixed_free_validation/run_001
```

The validator computes only design eligibility and licensed q summaries. A
non-zero exit status is the expected safe outcome for incompletely logged
historical datasets.
