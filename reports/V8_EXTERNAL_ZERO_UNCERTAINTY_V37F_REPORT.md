# V8 External Zero, Nested Uncertainty, and Residual Sufficiency V3.7F

Canonical decision:
`V8_EXTERNAL_ZERO_UNCERTAINTY_V37F_PASS_EVENT_NOISE_ZERO_TOTAL_FLOOR_POSITIVE`

## Scope

V3.7F replaced the claim that omitted coordinates are noise with a falsifiable
question: do those coordinates retain stable cross-session author
information? It also replaced the calibration-cohort origin from V3.7E with
two independent external reference panels and added a nested technical error
model.

No human text, personality labels, or identifiers were read.

## Design

Each of 30 fresh worlds contained four disjoint panels:

- 256 router-reference authors;
- 256 zero/norm-reference authors;
- 128 calibration authors;
- 96 evaluation authors.

Four worlds were crossed with event budgets 32/64/128/256/512:

- exact `hard_rank12`;
- power-law `dense_tail48`, where all 48 stable directions were nonzero;
- `dense_state_alias`;
- cross-session `author_permutation`.

The canonical run produced 600 main cells and 120 nested-uncertainty cells.
All 11,790 registered RNG streams were unique. The V3.7E parent seal and
V3.7F prospective seal passed.

## Results

All 24 frozen checks passed. *(2026-08-03 correction: the original text said
25; `decision.json` `checks` holds 24 named checks —
`docs/V8_PUSH_REMEDIATION_20260803.md`, item 5.)*

| Result | Canonical estimate |
| --- | ---: |
| Evaluation-cohort effect on a fixed score | 0 |
| Population-shift direction cosine | 0.9984 |
| Population-shift amplitude | 0.9990 |
| Permutation selected-rank <=2 rate | 1.000 |
| Permutation residual AUC | 0.4990 |
| Exact-rank oracle residual AUC | 0.4983 [0.4861, 0.5111] |
| Dense-tail residual AUC (at event budget 256) | 0.8635 [0.8437, 0.8817] |
| Dense-tail conditional residual gain | 0.3635 [0.3430, 0.3823] |
| Exact-rank normalized capacity floor | 0.0102 |
| Dense hard capacity floor | 0.0546 |
| Dense information-conserving floor | 0.0326 |
| Dense floor reduction | 35.0% [27.4%, 42.4%] |
| Event-only fitted asymptotic floor | 0.0035 [0.0022, 0.0049] |
| Dense state-alias infinite floor | 0.2434 [0.2394, 0.2476] |
| Event-only coverage | 0.9442 |
| Full nested coverage | 0.9519 |
| 256/64 full-region radius ratio | 0.6198 |
| External-zero variance reduction, 64 to 256 | 74.6% |
| Null-change false positive | 0.0521 |
| Two-MDC power | 1.000 |

*2026-08-03 annotation (`docs/V8_PUSH_REMEDIATION_20260803.md`, item 5):* the
dense-tail residual AUC row above is budget-indexed, not budget-invariant.
Per-budget means from `cell_summary.csv`
(`v37f_confirmation_final_20260726`): 32 → 0.8896, 64 → 0.9518, 128 → 0.9497,
256 → 0.8635, 512 → 0.5393. At the 512-event budget the omitted-coordinate
residual signal collapses toward chance; do not quote 0.8635 without its
budget.

At 256 events, event variation was the largest registered uncertainty source
in both tracked worlds. Calibration/rank/subspace selection remained
material, especially in `dense_tail48`. The balanced functional-ANOVA
reconstruction error was below \(4\times10^{-16}\).

## Interpretation

The experiment supports three narrow propositions.

1. A score origin can be kept external to calibration and evaluation authors.
2. Finite event-sampling error becomes very small with increasing event
   budget in the exact-rank world.
3. Low-energy coordinates omitted at finite budget can retain strong stable
   author information. Hard deletion is therefore not a defensible default.

The appropriate V8 formulation is information-preserving reliability
weighting:

\[
\text{observed path}
=
\text{stable scored channel}
+\text{condition/state channels}
+\text{unresolved stable channel}
+\text{event uncertainty}.
\]

The result does **not** show that total error is mathematically zero. The
state-alias world retains a large positive floor even as event sampling is
removed. It also does not show that every natural-language token contains
personality; the dense-tail world is a synthetic existence construction.

## Reproducibility

The complete canonical run was repeated from the sealed configuration. Nine
core outputs, including all metrics, uncertainty tables, decision, and
report, were byte-identical.

Canonical artifacts:
`results/v8_external_zero_uncertainty/v37f_confirmation_final_20260726/`.

Prospective seal:
`eb6bfca308847348c3487c87b7e90de2f27be0e8b4529cf4835e2ba3bd6b8ff7`.
