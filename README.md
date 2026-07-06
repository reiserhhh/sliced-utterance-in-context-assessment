# Sliced Utterance In-Context Assessment (SUICA)

SUICA is a text-behavior measurement framework: it treats a person's
spontaneous writing as many small behavioral observations ("sliced
utterances") measured inside their naturally occurring contexts, and builds
interpretable, frozen, auditable scores from them — a scale-construction
method situated between questionnaires and free-response assessment.

*Suica (スイカ) is Japanese for watermelon: the method's core "rind model"
holds that topic/situation is not noise to strip away but the rind that
carries person signal through self-selection — a claim this project first
falsified in its naive form (statistical condition-centering destroys
signal) and then rebuilt as a design principle (control context by design;
measure choice as a channel).*

## What is in this release (v0.1.0-prereg-sealed)

- **Method** — `docs/THEORY.md` (rind model, three channels: choice / style /
  react), `docs/RULEBOOK.md` (binding experiment-design rules, each traced to
  measured evidence), `docs/VALIDATION_PLAN.md` (the P0-P5 falsification
  framework).
- **Worked example** — `docs/WORKED_EXAMPLE_MANUAL.md`: the complete,
  audited construction of a 19-construct battery + 12 choice axes on PANDORA
  (Reddit), with development-tier anchor performance (e.g., MBTI
  thinking-feeling ridge CV r = 0.346; Essays Big5 transport mean r ~ 0.144
  from 19 interpretable scores) and score-interpretation rules.
- **Audit trail** — `docs/CLAIMS_LEDGER.md`: every claim with status, seven
  adversarial audit rounds, retractions included. The ledger is the
  authoritative record; prose may not exceed ledger status.
- **AI operating standard** — `docs/AI_ANALYST_GUIDE.md`: role separation
  (scorer/builder/coder/auditor/interpreter/human), fixed prompts, guardrails
  G1-G11 (each traceable to a caught failure).
- **Sealed preregistration** — `docs/PREREGISTRATION.md`: the external-validity
  confirmation (lockbox: PANDORA Big5 + MBTI bridge + Essays confirm-half)
  is UNOPENED (budget 2/2). The initial commit hash of this repository is
  the seal. Anyone with data access can perform the opening exactly once
  under the frozen rules.
- **Code** — `suica_core/` + `scripts/` (the full validation pipeline) +
  `tests/` (39 tests, no data needed).

## Quickstart (no data required)

```bash
pip install -r requirements.txt
python -m pytest -q tests/test_suica.py          # 39 passed
python scripts/run_suica_synthetic_ground_truth_v2.py   # P0: estimator
python scripts/run_suica_p0b_thin_cell_regime_v3.py     # P0-B: thin cells
```

These synthetic harnesses verify the entire estimator layer against planted
ground truth without any real data. To reproduce the worked example, obtain
the datasets per `docs/DATA_ACCESS.md` (this release ships no user text, no
user IDs; SHA-256 manifests allow byte-identical preparation checks).

## Honest summary of evidence status

Confirmed at held-out grade (T3): choice-axis stability (5/5 axes,
shrinkage 0.027), 15/15 discovered constructs on unseen users, react
signatures for 2 constructs under the stranger null. Falsified and retired:
condition-mean centering (three independent ways), affect word-rates as
trait or occasion-state measures, attention-weight interpretation as
measurement evidence. Sealed: all confirmatory external validity (see
PREREGISTRATION). Scope: English, one platform + student essays; dialogue
and clinical use are designed but untested (OPEN_PROBLEMS OP-7/8/14).

## Provenance

Frozen from the private development repository `project persona` at commits
`154822a`, `05be394`, `cad83d5`, `c27727b`, `1c417fa`, `8447541`, `5189168`,
`b9f65a6`, `0650936`, `5485a02` (+ the freeze commit recorded in
`docs/FREEZE_NOTES.md`). Built with AI-assisted research under the
builder/auditor protocol documented in the guide; seven audit rounds caught
and corrected real artifacts in five of them — the audit trail is part of
the method.
