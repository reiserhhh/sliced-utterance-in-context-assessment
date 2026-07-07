# SUICA Publication Plan v1

Created: 2026-07-07. Decision basis: the 2026 SJR top-3% list (user-provided)
x Waseda read-and-publish agreements x topical fit.

## Target: Behavior Research Methods (BRM, Springer Nature)

- SJR 2.462, on the top-3% list; THE psychology journal for new research
  methods/instruments with open code.
- Fit: SUICA is exactly a "methods, techniques, and instrumentation" paper —
  a new measurement framework + frozen open-source implementation + a
  falsification-first validation program with a sealed preregistration.
  BRM's TOP Level 2 open-practices culture matches the project's ledger/
  audit/manifest discipline better than any substantive journal.
- Cost: hybrid OA; the Waseda-Springer agreement (2026 quota 68 articles)
  waives the APC. Requirements to satisfy AT ACCEPTANCE:
  1. Corresponding author affiliated with Waseda, using a waseda.jp-family
     address, and holding an eligible status (regular students ARE eligible
     under the Springer deal — 学生(正規生のみ)).
  2. Follow the university library's designated workflow when the article
     is accepted (author selects OA under the agreement in Springer's
     system; institution approves).
- Review: double-blind. CONSEQUENCES for us:
  - Manuscript must not name the author, Waseda, or the identifiable
    public GitHub URL. At submission, reference an ANONYMIZED repository
    view (e.g., an anonymous OSF view-only link or an "identifier redacted
    for review" placeholder); swap in the real public repo + seal-hash
    citation in the accepted version. The seal itself is unaffected (the
    hash is cited, the repo stays public regardless).

## Manuscript spec (from the fetched submission guidelines)

- APA 7, double-spaced, page numbers; abstract <= 250 words; no hard length
  limit (target ~13-16k words + appendices given the material).
- Declarations block (before References): funding / COI / ethics / consent /
  data & materials availability / code availability + **Open Practices
  Statement** (TOP Level 2).
- Statistics: effect sizes + CIs everywhere (we already do), A PRIORI power
  (the prereg power table), disclose ALL DVs/conditions (the ledger IS this
  disclosure — cite it), multiple-testing corrections (BH-FDR preregistered).
- Ethics posture: secondary analysis of public, pseudonymous datasets
  (PANDORA — Gjurković et al.; Essays — Pennebaker & King); no new human
  data collected; no attempt to deanonymize; release ships no user text or
  IDs. State exemption accordingly; cite dataset licenses/terms.

## Paper shape (two-part, as planned since the freeze)

Part 1 (Sections 1-3): the METHOD — rind framework + formal results (F1-F6)
+ the validation architecture (tiers, lockbox, builder/auditor adversarial
protocol, wrong-world licensing, comparison licenses).
Part 2 (Sections 4-6): the WORKED CONSTRUCTION on PANDORA/Essays — the
falsification series, channel decomposition, discovery->confirmation->blind
coding, dev-anchor performance, the sealed lockbox opening #1 reported in
full (2/7: an honest fail with two T4 confirmations), residual
individuality. General discussion: licenses, limitations, the native-corpus
next study.

## Framing decisions (fixed now)

1. LEAD with the falsification result (centering destroys signal + the F4
   theorem): it contradicts the default topic-residualization practice in
   language-based assessment — that is the paper's hook, not SUICA's
   correlations.
2. The adversarial builder/auditor protocol (11 rounds, 13 caught builder
   errors) is reported as a METHOD contribution with its error taxonomy —
   first-class material for BRM's audience, not a confession appendix.
3. The lockbox opening is reported verbatim including the failed omnibus
   rule; the paper's claim is calibrated: two channel-level confirmations
   (first-person -> N; politics-choice -> O), method-level validity of the
   governance, and explicitly bounded comparison licenses.
4. No clinical claims anywhere (Rulebook D forbidden-words list applies to
   the manuscript itself).

## Backups (in order)

1. Journal of Personality Assessment (T&F; SJR 1.287; top-3% list; Waseda
   T&F deal) — reframe slightly toward assessment audience.
2. Multivariate Behavioral Research (T&F family; SJR 2.711) — reframe
   toward the formal/estimator side (F1-F6, wrong-world licensing).
3. Psychological Methods (APA; SJR 4.925) — prestige option; NOT in a
   Waseda deal, but subscription-route submission is free (no OA). Higher
   bar, slower; consider if BRM desk-rejects.

## Submission checklist (to fill before submission)

- [ ] Blinded main document (no names/affiliation/repo URL)
- [ ] Separate title page (author, Waseda affiliation, waseda.jp email)
- [ ] Anonymized repository link for reviewers
- [ ] Abstract <= 250 w; keywords
- [ ] Declarations + Open Practices Statement
- [ ] Every number traced to a ledger row (final number sweep — the round-12
      audit gate before submission)
- [ ] Figures: (1) rind model / channels; (2) validation architecture;
      (3) centering falsification + phase diagram; (4) purity decomposition
      (flesh/rind shares per construct); (5) lockbox opening forest plot;
      (6) seed-pattern stability vs stranger null
- [ ] Co-author/acknowledgment decision for AI assistance per Springer
      policy (LLMs cannot be authors; document AI use in Methods/Acknowledgments)
