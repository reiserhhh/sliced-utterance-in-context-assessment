# SUICA-Native Corpus — Collection Protocol v1 (executable pack, F14/N4)

Created 2026-07-12. Implements SUICA_NATIVE_CORPUS_DESIGN_V1 to the autonomy boundary:
everything except recruitment, IRB submission, and compensation is specified here so
that collection can start the day those clear. Companion files: PROMPTS_V1.md (bilingual
prompt battery + frozen interviewer script), PREREG_SKELETON_V1.md,
scripts/native_echo_rate_v1.py.

## 1. Design cells (per participant)

2 sessions (S1, S2; >= 14 days apart) x 2 regimes (A free, B fixed). Within each
session both arms are completed; arm ORDER is counterbalanced across participants by
enrollment parity:

| enrollment index | S1 order | S2 order |
|---|---|---|
| even | A then B | B then A |
| odd  | B then A | A then B |

Word targets per arm per session: 1,500-2,500 words (EN) / 2,500-4,200 characters (JP).
Arm B always contains the dialogue block (interviewer script, PROMPTS_V1 section B2) as
its second half. No time limit; single sitting per session preferred, 48 h window
allowed (timestamps recorded).

## 2. Session flow (operator checklist)

S1: consent (if first contact) -> anchor battery part 1 (BFI-2-60) + PANAS(state) ->
arm per order -> arm per order -> close. S2 (>= 14 days): PANAS(state) -> arms per
order -> optional informant nomination -> close. BFI-2 is NOT repeated at S2 (trait
anchor once); PANAS at every session (state track, N1).

## 3. Data records (JSONL, one line per block)

{ "pid": sha256(participant_key + salt), "lang": "en"|"jp", "session": 1|2,
  "arm": "A"|"B", "block": "free_writing"|"fixed_prompts"|"dialogue",
  "order_cell": "even"|"odd", "t_start": iso8601, "t_end": iso8601,
  "text": "...",                      # participant text only, for writing blocks
  "turns": [{"role": "interviewer"|"participant", "text": "...", "t": iso8601}, ...],
  "anchors": {"bfi2": [60 ints]|null, "panas": [20 ints]|null},
  "informant": {"present": bool, "bfi2s": [...]|null} }
Storage: text + anchors + hashes only (no other PII); public release = aggregates +
SHA-256 manifests, exactly as the current repo. Raw JSONL lives outside the public repo.

## 4. Governance (binds collection to the program's standards)

- INSTRUMENT FREEZE BEFORE COLLECTION: v4 battery + choice module + OP-33 axes,
  scorer hash-pinned; motion-layer estimators (suica_core/motion.py at its release
  commit) hash-pinned alongside — the native corpus is the first data where the
  spectral layer meets anchors, and the estimator must be frozen first.
- PREREG SEALED (public commit) before the first main-collection participant;
  PREREG_SKELETON_V1.md carries the hypothesis slots. Pilot (N=10/language) may run
  before sealing; pilot data never enters confirmatory analyses.
- Interviewer prompt is FROZEN and published (PROMPTS_V1 B2); no adaptive probing.
  Assistant-echo rate monitored per echo spec (section 5); dialogue blocks exceeding
  the pilot-set ceiling are flagged contaminated and excluded from F-family scoring.
- Participant-facing text obeys Rulebook D (forbidden clinical words); no scores or
  interpretations are returned to participants.

## 5. Assistant-echo monitor (OP-7 contamination check)

Definition: for each participant turn, echo(turn) = |{content 3-grams in the turn that
appeared in ANY prior interviewer turn}| / |content 3-grams in the turn| (content = after
stopword removal; JP after tokenization). Participant dialogue-block echo rate = mean
over turns. Ceiling: set at pilot as median + 2*MAD of pilot echo rates; pre-registered
before main collection. Reference implementation: scripts/native_echo_rate_v1.py.

## 6. What remains operator-side (the only missing pieces)

(1) IRB submission (Waseda; consent skeleton in PREREG_SKELETON_V1 appendix);
(2) recruitment channel + compensation budget (design: N=120/language + pilot 10);
(3) informant recruitment consent wording sign-off; (4) the go decision to freeze +
seal. Everything else in this pack is ready to execute.
