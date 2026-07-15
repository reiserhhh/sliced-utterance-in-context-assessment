# Sliced Utterance In-Context Assessment (SUICA)

**English** | [日本語](README.ja.md) | [简体中文](README.zh.md)

SUICA is a text-behavior measurement framework: it treats a person's
spontaneous writing as many small behavioral observations ("sliced
utterances") measured inside their naturally occurring contexts, and builds
auditable, reference-relative coordinates from them — a methodological
foundation for future text-based assessment between questionnaires and
free-response methods, not a completed personality scale.

*Suica (スイカ) is Japanese for watermelon: the method's core "rind model"
holds that topic/situation is not noise to strip away but the rind that
carries person signal through self-selection — a claim this project first
falsified in its naive form (statistical condition-centering destroys
signal) and then rebuilt as a design principle (control context by design;
measure choice as a channel).*

## What is in this release (v0.2.0)

- **V7 technical core** — operator-indexed relative text geometry, frozen
  geometry bundles, refusal rules, multiview calibration, uncertainty and
  future-data gates. The highest supported claim is
  `OPERATOR_INDEXED_RELATIVE_TEXT_GEOMETRY_WITHIN_DECLARED_DOMAIN`; it is not a
  personality, reliability, clinical, universal-language, or market claim.
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
- **Sealed preregistration** — `docs/PREREGISTRATION.md`: the seal is the
  initial commit hash of this repository. **Opening #1 was performed on
  2026-07-07** under the frozen rules (commit-pinned script, adversarial
  pre-audit): the preregistered success rule **FAILED** (2/7 hypotheses at
  BH-FDR q<.05; the rule required >=4/7) — recorded in full in
  `reports/suica_lockbox_opening_1.md`. H2 (first-person -> Neuroticism,
  r=+0.111, q=.002) and H6 (politics/news choice -> Openness, r=+0.096,
  q=.006) confirmed at lockbox tier. One opening remains; the Essays
  confirm-half labels are still untouched.
- **Code** — `suica_core/` + `suica_sim/` + `scripts/` + `tests/`. The V7
  release lockbox is independently verifiable without restricted corpora.

## Quickstart (no data required)

```bash
pip install -r requirements.txt
python -m pytest -q tests/test_suica.py          # 39 passed
python -m pytest -q -p no:cacheprovider          # release audit: 301 passed
python scripts/verify_suica_v020_lockbox.py       # portable v0.2.0 seal
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
measurement evidence. Confirmatory (T4, lockbox opening #1, 2026-07-07):
the preregistered success rule FAILED (2/7; recorded in full, no
re-analysis) — first-person -> Neuroticism (r=+0.111) and politics/news
choice -> Openness (r=+0.096) are the two lockbox-confirmed relations;
tension, novelty, directive, venue entropy and gaming choice did not
confirm. One opening remains sealed. Scope: English, one platform + student
essays; dialogue and clinical use are designed but untested (OPEN_PROBLEMS
OP-7/8/14 — OP-7a register-proxy and OP-8 stage 1 closed 2026-07-07, see
CLAIMS_LEDGER).

V6 raw-text factor rediscovery (2026-07-13) did **not** promote a new factor
inventory. A discovery-only, label-free 24-dimensional text basis retained
distributed author information after opportunity control (Static
own-vs-stranger AUC 0.691), but Static, Hybrid, and Dynamic factor spaces all
failed author-disjoint confirmation. This is recorded as a boundary result,
not converted into post-hoc named constructs; see
`reports/V6_FACTOR_DISCOVERY_REPORT.md`.

V6 nonlinear-path audit (2026-07-14): a phase-coupled synthetic world proves
that linear mean/covariance/lag summaries need not exhaust path information;
however, neither the degree-two/three path-signature screen nor a held-out RFF
conditional-transition embedding detected an order-stable signal in unseen
PANDORA authors. The nonlinear object is therefore a validated **theoretical
candidate**, not a detected human-text construct. See
`docs/V6_NONLINEAR_PATH_OBJECTS.md`.

V7.2 operator-indexed multiview audit (2026-07-15): fixed cross-comment
slicing did not show a robust universal precision advantage, so slicing is
retained as one observation view rather than promoted as a universal best
operator. On a fresh 600-author, label-free condition/opportunity audit, total
source-disjoint author geometry (AUC .916 [.890, .938]), observed context
selection recurrence, and a **within-stratum exchangeable** matched partial
screen (AUC .834 [.766, .896], 86/109 retained authors) reproduced. The
matched screen’s selected Jaccard caliper was 0.0, so it is conditional on
metadata balance rather than proof of literal same-topic equivalence. The
recorded primary subreddit/time surface itself explained only R2=.0045
[.00024, .00768] and did not robustly transport to the total configuration.
This is evidence for operator-indexed author-relative text geometry with
unresolved condition accounting, **not** a personality factor, causal context
effect, or clinical score. See
`docs/V7_OPERATOR_INDEXED_MULTIVIEW_V71.md` and
`reports/V7_CONDITION_OPPORTUNITY.md`.

V7.2 registered operator family (2026-07-15): on 240 new authors excluding
all 1,020 earlier V7 authors, five operators and word/char representations
showed same-source transport in a synchronized max-T family. The decisive
boundary is source-disjoint replication: fine-grained linear coordinate maps
did not transport, but source-disjoint own-vs-stranger position alignment did
(AUC .719--.805; 48-comment sensitivity .791--.862). SUICA therefore has
evidence for reproducible **relative text geometry**, not fixed named axes or
personality measurement. See `reports/V7_OPERATOR_FAMILY.md`.

V7.3 theoretical closure audit (2026-07-15): the primary object is no longer
an unidentified factor coordinate. It is a frozen, identifier-free landmark
distance profile under an operator- and reference-indexed regularized
Mahalanobis geometry. A real held-out smoke scored 98.6% of discovery, 92.2%
of calibration, and 79.2% of confirmation authors; out-of-reference rows are
explicit radial-envelope refusals, not a general OOD diagnosis. Corrected W2 simulations separate nonlinear geometry from
linear coordinates, W3 uses 25 random partitions, W4 uses split-specific null
spectra and paired method-difference intervals, and W7 proves that unpaired
cross-domain coordinates are not identified. All six corrected evidence
bundles passed their original run-manifest/inventory audit and are distributed
as deidentified aggregate snapshots with source hashes. Version 0.2.0 seals
`V7_THEORETICAL_CORE_CLOSED_WITH_EMPIRICAL_GATES`. Reliability, external
construct validity, and paired cross-domain transport remain separate
future-data gates. See `reports/V7_THEORY_CLOSURE_AUDIT.md`,
`docs/V7_EVIDENCE_STATUS_LATTICE.md`, and `docs/V7_LOCKBOX_V020.md`.

## Provenance

Frozen from the private development repository `project persona` at commits
`154822a`, `05be394`, `cad83d5`, `c27727b`, `1c417fa`, `8447541`, `5189168`,
`b9f65a6`, `0650936`, `5485a02` (+ the freeze commit recorded in
`docs/FREEZE_NOTES.md`). Built with AI-assisted research under the
builder/auditor protocol documented in the guide; seven audit rounds caught
and corrected real artifacts in five of them — the audit trail is part of
the method.
