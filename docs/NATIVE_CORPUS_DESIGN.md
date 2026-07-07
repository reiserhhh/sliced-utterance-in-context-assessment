# SUICA-Native Corpus Design v1 — the instrument's own data

Created: 2026-07-07. PANDORA was the development substrate; it did its job
(falsified the wrong mechanism, found the two real channels, froze an
audited estimator layer) and is now exhausted for four independent reasons,
each established by a specific result in this project. A SUICA-native corpus
is not a nicety — it is the unique design that resolves all four at once.

## 1. Why PANDORA cannot answer the next questions (four proven necessities)

| # | Necessity | The result that forces it |
|---|---|---|
| N1 | STATE timescale | states live below the month scale (E5/E7; OP-16); Reddit gives no session structure to sample states at |
| N2 | DIALOGUE register | clinical target is dialogue; all PANDORA evidence is posts/essays. OP-7a (Reddit reply turns) is a precursor only |
| N3 | Cross-REGIME comparability | PRED-4 FAIL + F4: document type is not a covariate; regime and population are confounded because NO author appears in multiple regimes. Only within-person multi-regime data separates them |
| N4 | LANGUAGE | JP scorer is machinery-grade (stage 1/3); stage 3 needs a within-JP longitudinal corpus |

One design closes all four: the same people, writing in multiple regimes,
across multiple sessions, in both languages.

## 2. Core design — 2 regimes x 2 sessions, within-person

Each participant contributes, in a fixed order counterbalanced across
participants:

- **Arm A (free regime)**: open self-expression prompts ("write about
  whatever is on your mind", 3-5 loose topics of the participant's choice) —
  the C1 channel is ALIVE (they choose their rind). ~1,500-2,500 words.
- **Arm B (fixed regime)**: identical structured prompts for everyone
  (assigned topics + a fixed AI-dialogue interview, Rulebook G) — the C1
  channel is CLOSED BY DESIGN, so per F4's boundary condition, condition
  adjustment is legitimate here and Arm B yields the clean C2 (flesh)
  measurement. ~1,500-2,500 words.
- **Two sessions** >= 2 weeks apart (state timescale N1; disjoint-occasion
  retest without the same-text inflation OP-15 warns about).
- **Dialogue block** inside Arm B: fixed-prompt AI interviewer; measure the
  assistant-echo rate (does the model's wording leak into the subject's
  turns — the OP-7 contamination check) and run the C3 if-then signature
  analysis on subject turns.

This yields, per person: free-vs-fixed (regime factor, N3), session1-vs-2
(occasion factor, N1), monologue-vs-dialogue (register factor, N2), and —
run in EN and JP cohorts — the language factor (N4). All as DESIGNED factors,
so measurement-invariance testing is possible instead of guessed.

## 3. Anchor battery (external validity, the lockbox's role but native)

Each participant completes, once per session:
- Big Five (BFI-2, 60 items) + a brief state affect scale (PANAS) per
  session for the state track.
- MBTI-style forced-choice OR the bridge instrument, for continuity with
  PANDORA's axes (optional).
- Optional informant report (one peer rates the participant) — enables
  Furr distinctive-ACCURACY analysis (the residual-individuality layer,
  OP-32, gets a criterion it never had).

Text scores are frozen (v4 battery + choice + co-selection OP-33) BEFORE
labels are analyzed; a native preregistration seals the confirmatory
hypotheses exactly as the PANDORA lockbox did.

## 4. Sample size and power

Target N = 120 per language (240 total), each with 2 sessions x 2 regimes.
- Rationale: at observed-r ~ 0.15-0.25 for the F-family flesh constructs,
  N=120 gives power 0.79-0.99 (two-tailed alpha .05) for the primary
  direction hypotheses — matched to the PANDORA lockbox power table.
- Measurement invariance (configural/metric/scalar across regimes) needs
  ~100+ per group for stable fit; N=120 is adequate for the 2-group
  (free/fixed) test that PRED-3/PRED-4 could only gesture at.
- Distinctive-accuracy (OP-32 with informants): N=120 gives a stable
  normative profile and detects distinctive-accuracy r >= 0.20 at power
  ~0.85.

## 5. What each necessity gets tested with

- **N1 state**: session1-vs-2 within-regime retest gives the trait floor;
  within-session state deviation gives the state ceiling; the gap is the
  per-occasion state precision at KNOWN occasion boundaries (unlike E5's
  inferred months). Feasibility bar: contiguous SB >= 0.30 (currently 0.27).
- **N2 dialogue**: monologue-vs-dialogue transport of the F-family (OP-7a
  made native and label-anchored); assistant-echo rate < a pre-set ceiling
  or the dialogue scores are flagged contaminated.
- **N3 regime**: free-vs-fixed measurement invariance. Metric invariance
  (equal loadings) would license cross-regime rank comparison; scalar
  (equal intercepts) would license level comparison — the thing PRED-4
  showed we CANNOT assume. This is the definitive test of the comparison
  licenses (L3).
- **N4 language**: EN-vs-JP within-construct validity (D1 stage 3); no
  cross-language numeric comparison, only within-language structure.

## 6. Ethics and consent (OP-14, now in scope)

- IRB-equivalent protocol: informed consent covering text analysis + AI
  interview + optional informant; right to withdraw and delete; no
  clinical claims returned to participants (research instrument, not
  diagnosis — Rulebook D-forbidden-words applies to participant-facing
  text too).
- Data minimization: store text + anchor scores + hashes; no other PII.
  The public release ships aggregate results and SHA-256 manifests only,
  exactly as the current repo does.
- AI-interviewer transcripts retained for the echo-rate audit; the
  interviewer prompt is fixed and published (no adaptive probing that
  could induce demand characteristics).

## 7. Build order (each phase gated on the previous)

1. Instrument freeze: v4 battery + OP-33 co-selection axes + choice module,
   scorer hash-pinned; native preregistration drafted and SEALED (public
   commit) before any collection.
2. Pilot N=10/language: prompt calibration, echo-rate baseline, word-count
   feasibility, JP tokenizer check on real dialogue.
3. Main collection N=120/language.
4. Frozen scoring -> single native lockbox opening -> measurement-invariance
   + direction hypotheses + state precision + distinctive accuracy.
5. Adversarial audit of the opening (the standing builder/auditor protocol).

## 8. Relationship to the two lockboxes

- The PANDORA lockbox (budget 1 remaining, Essays confirm-half untouched)
  stays reserved for a v4 composite re-test on the SAME population — it
  answers "does the corrected battery confirm where the v3 one failed?".
- The NATIVE corpus answers the four necessities PANDORA structurally
  cannot. They are complementary, not substitutes: one fixes the battery's
  external validity on the original population, the other extends the
  instrument to the situations it was ultimately built for.

## 9. Cost honesty

This is a human-subjects data-collection study: it needs IRB, recruitment,
compensation, and months of calendar time. It is correctly OUT of scope for
the methods paper (which reports the instrument + its PANDORA validation +
the honest limitations). The design lives here so the paper can point to it
as the specified next study, not a vague "future work".
