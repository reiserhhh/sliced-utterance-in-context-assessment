# SUICA V8 Evidence-Bound Interpreter Experiment

Execution date: 2026-07-24
Final decision: `V8_INTERPRETER_RENDERER_ONLY`

## Question

This experiment tested the corrected V8 role split:

- SUICA is the sole numerical measurement channel;
- an LLM observer codes explicit, source-bound behavior events;
- deterministic code registers discovery-only SUICA-dimension/event
  relationships and compiles admissible interpretation candidates;
- an LLM interpreter may accept, qualify, reject, and render only those
  candidates;
- an independent LLM critic audits submitted atoms.

No Big Five, MBTI, clinical, market-outcome, or other external labels were
read. The experiment cannot establish personality constructs, diagnosis,
clinical utility, or human psychological validity.

## Evaluation corrections frozen before primary real text

Quick execution exposed and corrected the following evaluation defects before
the PANDORA primary gate:

1. repeated empty output sets no longer count as perfect informative
   stability;
2. the reported multilabel reliability statistic is correctly named Fleiss
   kappa;
3. cache reuse now requires the exact input-payload hash in addition to model,
   prompt, schema, temperature, and thinking mode;
4. observer-complete author coverage must be at least 0.95;
5. discovery links must have the same sign in source-disjoint left and right
   halves;
6. same-author negatives are matched first by hashed condition overlap and
   then text volume;
7. dense candidate sets are deterministically capped at the schema limit of
   eight;
8. the critic follows an explicit pass/qualify/reject rubric;
9. targeted deletion treats all atoms sharing the deleted event code as
   affected.

These corrections are recorded in
`docs/V8_INTERPRETER_STABILITY_PLAN.md`.

## Results

| Stage | Decision | Main result |
| --- | --- | --- |
| Planted formal | `V8_INTERPRETER_PLANTED_GATE_PASS` | All registered technical gates passed |
| PANDORA quick | `V8_INTERPRETER_PANDORA_QUICK_RUNTIME_PASS` | Runtime, safety, repeated-input, critic, E4, and E5 checks passed |
| PANDORA formal | `V8_INTERPRETER_RENDERER_ONLY` | Real-text same-author and neighborhood gates failed |

### Planted formal

- profiles: 200; complete profiles: 200; repetitions: 5;
- parse rate: 1.000; first-attempt valid rate: 1.000;
- observer macro-F1: 0.943;
- candidate-eligible profiles: 166;
- consensus interpretation coverage: 0.988;
- repeated-input weighted Jaccard median and lower bound: 1.000;
- multilabel Fleiss kappa: 0.988;
- evidence-edge F1: 0.980, 95% bootstrap lower bound 0.967;
- critic kappa: 0.976;
- targeted-minus-random deletion effect: 0.479
  [0.403, 0.556];
- forbidden fields: 0.

This establishes that the constrained contract can recover and render known
evidence-bound relations in a planted world. It does not establish a
real-text psychological measurement.

### PANDORA formal

- authors before/after observer completeness: 100/99;
- split: discovery 59, calibration 20, confirmation 20;
- profiles: 198; held-out authors: 40;
- parse rate: 0.9989; first-attempt valid rate: 0.9979;
- observer-complete author rate: 0.990;
- registered links: 14, all source-disjoint half-sign consistent;
- all 14 registered links used the same event code:
  `novelty_expression`;
- candidate-eligible held-out profiles: 3/80 (3.75%);
- candidate retention and exact candidate-set passthrough: 1.000;
- repeated-input atom/evidence stability and critic kappa: 1.000, but only
  among three eligible profiles;
- same-author AUC: 0.500, n=3;
- same-minus-matched-stranger: 0.000;
- neighbor AUC: 0.525 [0.500, 0.563];
- geometry-distance versus interpretation-distance Spearman: 0.062;
- irrelevant perturbation invariance: passed;
- key-evidence deletion checks: passed, n=3;
- forbidden fields: 0.

## Interpretation

The result separates three claims:

1. **Engineering stability passed.** With explicit thinking disabled, closed
   schemas, deterministic candidate compilation, exact evidence IDs, and a
   literal critic rubric, the LLM channel is replayable and safe.
2. **The LLM interpreter added no demonstrated selection information.**
   Candidate retention and exact-set passthrough were both 1.000. In this
   implementation the observer contributes semantic event coding, while the
   interpreter mainly renders the deterministic candidate set.
3. **Real-text assessment validity did not pass.** The discovery mapping
   collapsed to one coarse behavior code and produced candidates for only
   3.75% of held-out profiles. Perfect repeated-input metrics on three
   profiles cannot license same-author or neighborhood interpretation.

The failure is therefore not “LLMs are unstable” and not “SUICA geometry is
invalid.” It is a bottleneck in the current bridge from anonymous SUICA
geometry to the six-code behavior vocabulary. The 16 landmark-distance
coordinates are also likely carrying correlated geometry rather than 16
independent behavior relationships.

## Decision

- Keep SUICA as the sole score channel.
- Keep the LLM behavior observer and evidence-bound renderer as technically
  viable candidate components.
- Do not promote the current interpreter as an assessment channel.
- Do not run secondary Essays, MEPS, or X confirmation after the primary
  PANDORA author/neighborhood gate failed.
- Do not solve this by loosening evidence requirements or by allowing direct
  LLM personality scoring.

## Next research target

The next bounded method study should improve the registered intermediate
representation, not prompt fluency:

1. decorrelate or compress the landmark-distance profile before relation
   registration;
2. expand the behavior ontology through discovery-only, source-bound event
   patterns rather than six single codes;
3. model repeated event rates and event combinations under explicit
   opportunity conditions;
4. require candidate coverage, same-author information, and neighborhood
   alignment jointly on held-out data;
5. compare the LLM observer against a deterministic/human-coded observer
   subset before attributing any increment to LLM assessment.

## Artifacts

- planted formal:
  `results/v8_interpreter_stability/planted_formal_attempt3_normalized_20260724/`
- PANDORA quick:
  `results/v8_interpreter_stability/pandora_quick_v2_20260724/`
- PANDORA formal:
  `results/v8_interpreter_stability/pandora_formal_v2_20260724/`
- frozen plan and amendments:
  `docs/V8_INTERPRETER_STABILITY_PLAN.md`
