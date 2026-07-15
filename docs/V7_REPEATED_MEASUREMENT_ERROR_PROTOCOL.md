# V7 Repeated-Measurement Error Protocol

## Purpose

V7 does not treat one document, one model runtime, or one observation operator
as an independently interpretable person score. Before any generalizability
coefficient, minimum detectable change, or latent state-trait claim is fitted,
the study must provide a fully logged fixed-condition repeated-measurement
table and pass the mechanical preflight.

For a frozen anonymous component `k`, the future G-study model is:

\[
Y_{pcok}=\mu_k+P_{pk}+C_{ck}+O_{ok}+PC_{pck}+PO_{pok}+CO_{cok}+PCOe_{pcok}.
\]

`P` is not called a trait by this equation alone. The operational questions
are instead: how much is a stable participant-relative component, how much is
person-by-condition specificity (`PC`), how much is occasion/state dependence
(`PO`), and how much is remaining error (`PCOe`)?

## Required Observations

Every scored fixed-condition row requires:

- `participant_id`, `condition_id`, `occasion_id`, `session_id`;
- independently logged `assignment_randomized`;
- frozen `scorer_hash`, `operator_registry_version`, `window_operator_id`,
  and `representation_hash`;
- anonymous `component_id` and numeric `score_value`.

The minimal eligible design has at least two participants, two conditions, and
two occasions, with every participant-condition cell observed on at least two
occasions. This is an eligibility lower bound, not a recommended sample size
or a claim that the resulting variance components will be precise.

## Mechanical Gate

```bash
python scripts/run_suica_v7_gstudy_lst_preflight.py \
  --input path/to/fixed_repeated_scores.parquet \
  --output-dir results/v7_measurement_preflight/run_001
```

The only passing state is
`REPEATED_MEASUREMENT_DESIGN_READY_FOR_GSTUDY_LST`. The preflight returns a
refusal for missing score cells, incomplete crossing, non-randomized
assignment, or scoring/runtime version drift. It writes only aggregate design
coverage, never participant identifiers.

## Error-Protocol Contract

The score table alone is insufficient. Before fitting variance components,
validate a separate design manifest:

```bash
python scripts/validate_suica_v7_error_protocol.py \\
  --manifest configs/v7_error_protocol_manifest.template.json \\
  --output results/v7_error_protocol/preflight.json
```

The manifest must distinguish a globally shared calendar occasion from an
occasion nested within each participant, declare session order and carryover
control, bind the exact geometry bundle hash, and state whether the D-study
targets relative rank order, absolute level, or both separately. It must also
predeclare the estimator and interval method, a multivariate geometry outcome,
and joint perturbation of scorer/runtime, window/operator, and reference norm.

The passing state `ERROR_DECOMPOSITION_PROTOCOL_READY` licenses only a future
fit. It does not supply a reliability coefficient, single-text confidence
interval, minimum detectable difference, or state-trait interpretation.

## What Still Requires New Data

Passing the preflight does not estimate reliability. A future registered study
must fit variance components on an independent score cohort, predeclare the
D-study target (number of conditions and occasions), quantify scorer/window
perturbation, and then compute uncertainty and minimum detectable change.
The current MEPS + AI archive remains a one-session fixed-condition
feasibility source, not a G-study/LST dataset.
