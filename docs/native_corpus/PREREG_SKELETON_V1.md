# SUICA-Native Corpus — Preregistration Skeleton v1 (to be sealed before main collection)

Slots marked [SEAL] are fixed at the sealing commit; pilot (N=10/language) may inform
them; pilot data never enters confirmatory analyses.

## H-slots (from DESIGN §5; exact statistics fixed at seal)

- H-N1 (state timescale): within-regime S1-S2 retest of the frozen battery gives the
  trait floor; within-session deviation the state ceiling. Feasibility bar: contiguous
  SB >= .30. [SEAL: constructs, estimator hashes, thresholds]
- H-N2 (dialogue transport): F-family constructs transport monologue -> dialogue with
  rank correlation >= [SEAL]; dialogue blocks above the echo ceiling excluded.
- H-N3 (regime invariance): configural/metric/scalar invariance free vs fixed for the
  frozen battery; metric pass licenses cross-regime rank claims (L3), scalar pass
  licenses level claims. [SEAL: fit criteria]
- H-N4 (language): within-JP structure replicates within-EN structure (congruence >=
  [SEAL]); no cross-language numeric comparison.
- H-M (MOTION LAYER x anchors — the first licensed test): person-level motion
  descriptors (signed memory, rho_pi, shape pair, slope projections; estimator =
  suica_core/motion.py at hash [SEAL]) against BFI-2 anchors and against the informant
  distinctive-accuracy criterion. Directional slots to be filled from EXPL-4a/4b
  posteriors WITHOUT reusing their data. [SEAL: <= 8 directional hypotheses + BH]
- Power: N=120/language -> .79-.99 at r .15-.25 (DESIGN §4); motion hypotheses count
  toward the same BH family.

## Analysis order (locked)

frozen scoring -> seal check -> single opening -> invariance -> directions -> state
precision -> distinctive accuracy -> adversarial audit (builder/auditor protocol).

## Consent skeleton (IRB draft appendix; operator finalizes)

Participation = 2 remote writing sessions (~60-90 min each, >= 14 days apart) including
a fixed-script AI interview; questionnaires (BFI-2 once, brief mood scale each session);
optional: one person who knows you rates a short questionnaire about you. Data stored as
text + questionnaire scores under a hashed ID; no name, contact, or account identifiers
retained with the text; withdrawal deletes all records on request; results are reported
only in aggregate; this is a research instrument — no individual assessments or clinical
feedback are produced or returned. AI-interview transcripts are retained for a scripted-
ness audit. [JP mirror to be finalized with the EN at IRB submission.]
