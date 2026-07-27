# V8 Behavior-v2.1 MEPS C2 Support Audit

## Decision

`V8_BEHAVIOR_V21_MEPS_C2_IDENTIFIABILITY_PILOT_ONLY`

The 46-person Japanese MEPS bundle is useful for a shared-prompt ontology and
procedure pilot. It cannot confirm C2 under the frozen opportunity and
repeated-condition requirements.

## Available Design

All 46 participants supplied direct answers to the same three MEPS prompts.
Each answer has three ordered response slots, producing exactly three
candidate observations per participant and condition. Optional AI-assisted
task dialogue exists for 26-27 participants, and free conversation exists for
all 46.

This supports:

- checking whether the five explicit-behavior families are observable under
  shared Japanese prompts;
- estimating opportunity prevalence by prompt;
- comparing condition-specific behavior repertoires;
- testing the end-to-end coding procedure on private fixed-condition text.

## Why It Is Not C2 Confirmation

The registered C2 gate requires at least six opportunities per family/cell,
at least 70% complete participants, and independently repeated shared
conditions. The existing design has:

- three direct answer slots per prompt, below six;
- optional, self-selected AI assistance rather than complete randomized
  repeated opportunities;
- one session and one presentation of each prompt;
- no independent repeat of the same condition.

Splitting one answer or one dialogue into two pieces would create dependent
fragments, not repeated condition observations. Treating the three different
MEPS prompts as replicas would also change the estimand.

Therefore MEPS may be used as an **identifiability and ontology pilot**, not
as a formal C2 test. A future C2 design needs repeated randomized fixed
conditions with enough explicit opportunities in each family.

## Boundary

No raw text, model output, psychological labels, or participant identifiers
were read by this audit. It establishes design support only and cannot
validate personality, emotion, diagnosis, clinical scoring, or C2.
