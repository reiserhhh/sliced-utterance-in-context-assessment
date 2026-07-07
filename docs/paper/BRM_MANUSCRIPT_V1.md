# [BLINDED MANUSCRIPT — Behavior Research Methods]

<!-- Double-blind: no author names, no institution, no identifiable repo URL.
     The public repository is cited as [ANONYMIZED REPOSITORY LINK — view-only
     copy provided for review]; the real URL + seal hash replace it on
     acceptance. Separate title page holds author/affiliation/waseda.jp email.
     Every number in this manuscript must trace to a CLAIMS_LEDGER row; the
     pre-submission round-12 audit re-verifies the full sweep. -->

# Sliced Utterance In-Context Assessment (SUICA): A falsification-first framework for interpretable text-based personality measurement

## Abstract

Language-based personality assessment typically treats topic as a nuisance:
variance associated with what a person writes about is statistically removed
so that "how they write" can be measured. We show — empirically, three
independent ways, and then as an algebraic result — that this default is
self-defeating whenever people choose their own contexts: context choice
mediates person-to-text effects, so partialling contexts out deletes person
signal (the removed retest covariance equals Var(m) + 2Cov(f, m), the
mediated share). Building on this reversal we present SUICA, a measurement
framework that treats a person's spontaneous writing as many small
utterances sliced within self-selected contexts, and reads three channels:
context choice, a context-invariant style base, and person-by-context
signatures. The framework ships with a governance architecture we propose
as reusable methodology: frozen scorers with equivalence gates, data tiers
with a sealed, hash-pinned preregistration ("lockbox"), estimators licensed
against generative worlds that violate the theory's own assumptions, graded
comparison licenses, and an adversarial builder/auditor protocol under which
independent audits caught and corrected 13 builder errors across 11 rounds.
In a complete worked construction on public Reddit and essay corpora
(N = 3,183 development users), channel decomposition shows that trait-grade
signal concentrates in form habits (pronouns, orthography, negation), while
content vocabulary rides on context choice; a preregistered one-shot lockbox
opening confirmed two channel predictions (first-person rate to
Neuroticism, r = .111; political-venue choice to Openness, r = .096) while
the omnibus rule failed (2/7) — reported in full. Code, manifests, and the
sealed preregistration are public.

**Keywords:** personality assessment; natural language; psychometrics;
preregistration; open-vocabulary analysis; idiolect

---

## 1. Introduction

<!-- ~1,600 words. Hook: the topic-as-nuisance default and its quiet failure. -->

A decade of language-based assessment has established that personality
leaves usable traces in everyday writing (Pennebaker & King, 1999; Schwartz
et al., 2013; Park et al., 2015; Eichstaedt et al., 2021; Boyd & Schwartz,
2021). The field's best predictive models, however, purchase their accuracy
with two debts. The first is interpretability: open-vocabulary and
embedding models yield thousands of opaque features whose scores cannot be
audited item-by-item, revised without refitting, or explained to the person
measured. The second debt is quieter and, we will argue, conceptual: the
near-universal treatment of topic and venue as nuisance variance. Whether by
topic modeling, corpus stratification, or residualizing on content, the
default pipeline seeks the person "controlling for" what they chose to
write about.

This paper begins from a falsification. In a corpus of 17.6 million Reddit
comments, we attempted the nuisance treatment in its strongest forms —
naive condition-mean centering, shrunken partial centering, and two-way
fixed-effects centering estimated out-of-sample with cross-fitting — and
every variant REDUCED the disjoint-occasion stability of every style
measure (pooled Δ = −.091, 95% CI [−.102, −.080]; cross-fit fixed-effects
variants −.05 to −.07). The reason is not statistical misfortune but
structure: when contexts are self-selected, context is a mediator of
person→text effects. Conditioning on a mediator removes the mediated
signal; we derive the identity (the removed retest covariance equals
Var(m) + 2Cov(f, m), where m is the person's context-mix term and f the
context-invariant base), its boundary condition (centering is harmless
exactly when contexts are exogenously assigned, as in prompted essays), and
its second-order aggravation under strong person-context coupling. What
the field has treated as cleaning is, under self-selection, deletion.

The constructive consequence is a reframing we call the rind model, after
the watermelon: topic and venue are not packaging to discard but the rind
that carries person signal, because people pick their rinds. A text-based
instrument should therefore read three channels: (C1) context CHOICE
itself — which venues, which topics, in what proportions; (C2) a style
BASE — habits that survive crossing from rind to rind; and (C3)
person-by-context SIGNATURES — the if-then patterning of behavior across
situation classes, the textual descendant of behavioral signatures
(Mischel & Shoda, 1995). Context variance is controlled by DESIGN
(fixing or sampling rinds) and never by statistical subtraction.

Frameworks are cheap; what we principally offer BRM's readership is the
validation machinery that made this one falsifiable at every joint:

1. **Frozen, interpretable scoring.** All scores are counts from fixed
   lexica and fixed context maps, version-pinned with equivalence gates
   (a scorer revision that changes any frozen score by any amount restarts
   the validation chain — measured, not asserted).
2. **Wrong-world licensing of estimators.** Every estimand used for a claim
   must first demonstrate, in generative worlds that VIOLATE the model's
   assumptions one at a time, that it distinguishes the theory being true
   from being false. Two licensing failures were caught this way and are
   reported as recorded FAILs with their mechanism.
3. **Tiered data governance with a sealed lockbox.** Development labels are
   quarantined from confirmation labels; the confirmatory analysis was
   preregistered, hash-sealed in a public repository, and executed exactly
   once by a script whose own hash was pinned by an adversarial pre-audit.
   We report the opening verbatim: the omnibus success rule FAILED (2 of 7
   hypotheses at BH-FDR q < .05; the rule required 4), while the two
   confirmations are precisely the framework's two core channels.
4. **An adversarial builder/auditor protocol.** Every substantive result was
   attacked by an independent auditor with full recomputation rights before
   entering the claims ledger. Across 11 rounds the audits caught 13 real
   builder errors — self-estimation leakage, optimizer boundary collapse,
   estimand asymmetries, a construct-identity swap caused by silently
   refitting a clustering, and interpretive overstatements — each recorded
   with its correction. We propose the protocol, and its error taxonomy, as
   a reusable reproducibility method for computational measurement work.

Two further contributions follow from the framework rather than preceding
it. Channel decomposition of every construct in the inventory shows that
trait-grade, context-invariant signal concentrates in FORM habits —
pronoun use, orthographic habit (apostrophe omission), negation, profanity
— while content vocabulary owes its apparent stability to context choice;
this aligns the instrument with the forensic-stylometry finding that
individuality lives in co-selection of form (van Halteren et al., 2005;
Wright, 2017), and yields an admission gate (a "flesh-purity" criterion)
that would have prevented, in advance, the specific hypothesis that failed
most clearly at confirmation. And a residual-individuality layer
operationalizes the idiographic intuition that no factor list exhausts a
person (Allport, 1937; Molenaar, 2004): after subtracting the normative
profile, the remaining deviation pattern is stable across months (median
profile r = .505 against a stranger null of −.02; .684 on form constructs
alone) — measurable individuality beyond the factor structure, quantified
with the profile-decomposition discipline of Furr (2008).

We present the framework and its formal results (Section 2), the
validation architecture (Section 3), the worked construction with its
falsification series and confirmations (Sections 4-5), and the licensing
limits — what comparisons the instrument does and does not permit —
together with the designed next study (Section 6).

## 2. The rind framework and formal results

<!-- TO WRITE NEXT: model equation; channels; F1-F6 with proofs in appendix;
     number sources: THEORY_FORMAL_NOTES, wrong-world suite (W-B 0.637 etc.),
     phase diagram cells; boundary condition; comparison licenses preview. -->

## 3. Validation architecture

<!-- TO WRITE: tiers U/D/L; lockbox budget; evidence tiers T1-T4; frozen
     scorer + equivalence gates; wrong-world licensing table (9 worlds, 7
     pass, 2 recorded FAILs with mechanism); builder/auditor protocol with
     the 13-error taxonomy table (ledger audit log); comparison licenses
     L0-L4. Sources: FALSIFIER_MATRIX, CLAIMS_LEDGER audit log, COMPARISON_
     LICENSES. -->

## 4. Worked construction I: falsification and channels (development tier)

<!-- TO WRITE as Studies:
  4.1 Data and tiers (PANDORA 17.6M comments; N=3,183 half-eligible; Essays
      dev half 1,255; funnels table). Ethics: secondary public data.
  4.2 Study 1 — centering falsified 3 ways + F4 empirics (P2 -.091; E1
      cross-fit; phase diagram; Essays boundary).
  4.3 Study 2 — choice channel: axes held out (5/5, r_B .48-.68, shrinkage
      .027); purity decomposition (flesh/rind shares per construct, with
      bands per the estimator-agreement alarm); form/content division;
      register transport 19/19 (opposite-half, volume-matched).
  4.4 Study 3 — inventory growth under gates: open-vocabulary A/B (15/15),
      co-selection axes (21/48, ~15 form), blind coding with legibility
      classes (8/15; machine-only construct human 0/8), flesh-purity gate
      families F4/C8/comp6/und1.
-->

## 5. Worked construction II: anchors and the sealed confirmation

<!-- TO WRITE:
  5.1 Development-tier anchor performance (TF CV r=.346 from 31 scores; JP
      .182; EI .139; SN .120; Essays transport mean .144; expectation frame
      vs full-text baselines .25-.32; parse/base-rate disclosures).
  5.2 The lockbox opening (preregistered, one-shot): full 8-row table
      (H1-H8), BH-FDR, SUCCESS RULE FAILED 2/7 — reported verbatim; H2
      first_person->N r=.111 [.051,.170] q=.002; H6 politics->O r=.096
      [.036,.155] q=.006; power table a priori; eligibility funnel
      1,412->1,058/303; ΔR² add-on uninformative (frozen convention
      overfits, disclosed); no re-analysis; remaining budget.
  5.3 Residual individuality: seed-pattern stability .505/.684 vs stranger
      null; identification AUC .887/.891; the 32% unfactored share (M3).
-->

## 6. General discussion

<!-- TO WRITE: what is licensed (L0-L4 table as the honest deliverable);
     what failed and why that is the method working; limitations (one
     platform + students, English, heavy writers, no demographics);
     the native-corpus design (2 regimes x 2 sessions x 2 languages) as the
     specified next study; AI-assisted research disclosure. -->

## Open Practices Statement

<!-- All code, frozen lexica, class maps, manifests (SHA-256), the sealed
     preregistration (tag + hash), all audit rounds, and every reported
     number's source artifact are available at [ANONYMIZED REPOSITORY LINK].
     No raw user text or user identifiers are redistributed; dataset access
     follows the original publishers' terms (PANDORA; Essays). The
     confirmatory analysis was preregistered and executed once; the
     preregistration seal is the repository's initial commit hash. -->

## Declarations

<!-- Funding: [tbd]. COI: none. Ethics: secondary analysis of public
     pseudonymous datasets; no new data collection; exemption statement.
     Consent: not applicable (secondary public data). Data availability:
     per original dataset publishers; manifests provided. Code availability:
     public repository (anonymized for review). AI use: manuscript and
     analyses developed with AI assistance under the builder/auditor
     protocol documented in Section 3; final responsibility rests with the
     author. -->

## References

<!-- APA 7. Core: Pennebaker & King 1999; Schwartz et al. 2013; Park et al.
     2015; Eichstaedt et al. 2021; Boyd & Schwartz 2021; Mischel & Shoda
     1995; Fleeson 2001; Molenaar 2004; Fisher et al. 2018; Furr 2008;
     van Halteren et al. 2005; Wright 2017; Dąbrowska 2018; Biber 1988;
     Mosteller & Wallace 1963; Gjurković et al. 2021 (PANDORA); Yarkoni
     2010; Kern et al.; Benjamini & Hochberg 1995. -->
