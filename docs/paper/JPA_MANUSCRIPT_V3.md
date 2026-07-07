# [BLINDED MANUSCRIPT — Journal of Personality Assessment — v3]

<!-- v3: humanized register per real-paper calibration (Boyd & Schwartz
     2021 register analysis + Fleeson/Borsboom structures). Changes from
     v2: conventional headings; flowing literature review with specific
     study engagement; hedged, plain prose; aphorisms cut to a handful;
     minimal bold; longer connected paragraphs; standard Discussion with
     Limitations. Content claims unchanged; every number ledger-traceable. -->

# Text as Behavior in Chosen Situations: Toward a Theory of Personality Assessment From Spontaneous Language

## Abstract

People reveal themselves in what they write, and a sizable literature now
uses everyday language to assess personality. We argue that this
literature rests on an unexamined assumption it inherited from
experimental design: that the contexts of writing are exogenous, so that
topic and venue variance can be treated as noise and removed. In
observational corpora the assumption is false, because writers choose
their contexts, and the choices are themselves expressions of personality.
We develop this observation into a framework in which spontaneous text is
behavior distributed over selected situations, reaching measurement
through three channels: the selection of contexts, a context-invariant
style base, and person-by-context signatures. Three formal results follow.
Raw score stability conflates style with stable context choice, so that a
simulated corpus containing no personal style at all still yields retest
correlations near .64. Statistical removal of context means operates as
adjustment for a mediator and deletes person signal in derivable amounts;
it is harmless only when contexts are assigned. Trait interpretation
therefore requires a purity criterion that separates the channels. The
framework accounts for several standing puzzles, including the predictive
advantage of open-vocabulary features and the persistent robustness of
function-word markers, and it survived a preregistered, hash-sealed
confirmatory test in a qualified way that we report in full: the omnibus
criterion failed (2 of 7 hypotheses), while the two hypotheses tied
directly to the proposed channels were confirmed. We discuss implications
for how text-based instruments should be built, what they may claim, and
the studies that would extend or falsify the account.

**Keywords:** personality assessment; verbal behavior; situation
selection; behavioral signatures; idiolect; language analysis

---

## Introduction

Over the past two decades, the language people produce in ordinary life
has become a serious source of personality data. Pennebaker and King
(1999) showed that stylistic word use is reliable across time and genre;
Yarkoni (2010) mapped word-level correlates of the Big Five across nearly
700 bloggers; and Schwartz et al. (2013), analyzing roughly 700 million
words from 75,000 social media users, found that open-vocabulary language
features recover personality, gender, and age with striking specificity.
Language-based assessments correlate with self-reports, agree with
informant reports, and are stable over months (Park et al., 2015). For a
field that has long wanted behavioral alternatives to the questionnaire,
these are encouraging results, and they have encouraged applications
ranging from large-scale epidemiology to clinical screening.

Less attention has been paid to a methodological habit that runs through
much of this work. Because personality is understood as something that
should hold across situations, and because text varies enormously with
what it happens to be about, researchers routinely treat topical and
situational variance as a nuisance. The moves are familiar: residualize
features on topic models, stratify corpora by forum or genre before
analysis, or restrict measurement to closed style dictionaries precisely
because content words seem contaminated by circumstance. The intuition is
reasonable on its face. It is also, we will suggest, in quiet conflict
with the field's own findings, since the open-vocabulary features that
predict best are largely topical (Schwartz et al., 2013; Eichstaedt et
al., 2021). If what people write about were mostly noise around the
person, removing it should have helped.

We recently put the nuisance assumption to a direct test in a corpus of
17.6 million forum comments, applying context centering in the strongest
forms we could construct, including two-way fixed-effects estimates fitted
out of sample with cross-fitting. Every variant lowered the
disjoint-occasion stability of every style measure we examined; pooled
across measures the loss was Δ = −.09 (95% CI [−.10, −.08]). The result
seemed paradoxical only until we considered where the "nuisance" variance
comes from. In observational corpora nobody assigns topics. Writers
choose their venues and subjects, the choices repeat, and repeated choice
is exactly the kind of consistent, psychologically expressive behavior
that assessment is supposed to capture. Statistically controlling for
context in such data amounts to adjusting away a pathway through which
personality reaches the page.

There is a precedent for the reorientation we propose. When behavioral
consistency across situations proved elusive, one response was to defend
traits and another was to abandon them; the resolution that endured did
neither. Mischel and Shoda (1995) argued that the situational variability
itself is structured, that stable if-then profiles are signatures of
personality rather than error around it. Our proposal applies the same
lesson to verbal behavior. The context-linked variance that language
researchers remove is not error around the person. In self-selected
corpora, a good portion of it appears to be the person, expressed through
a channel that the removal destroys.

This article develops that claim into a framework with testable
commitments. We first review the evidence that context choice is
personal, drawing on situation-selection research, the behavioral
signature literature, Brunswik's representative design, stylometry, and
work on within-person distributions. We then state the framework and
derive its formal consequences, including an account of when the standard
practices (centering, reliability interpretation) mislead and when they
are safe. We summarize the empirical evidence to date, including a
preregistered confirmatory test that the framework passed only in part,
and we close with what the account implies for building and interpreting
text-based instruments. Throughout, we try to claim no more than the
evidence licenses; the framework forbids several common practices, and
its own record under those prohibitions is part of the argument.

## Why Context Choice Is Personal

Four lines of research, none of them ours, converge on the premise that
doing something *somewhere* is informative about the doer.

The first is the situation literature. Buss (1987) distinguished
selection, evocation, and manipulation as mechanisms by which persons and
environments come to correspond, and placed nonrandom selection of
settings first among them. Contemporary situation research has made the
point quantitative: in experience-sampling work, the situations people
report themselves in, and how they construe them, track their traits with
regularity (Rauthmann et al., 2015; Rauthmann & Sherman, 2023). Extraverts
are found in more social situations partly because they arrange to be.
In a text corpus this mechanism is not inferred but logged: the venue and
subject of every post is a recorded act of selection. Treating that
record as noise discards behavior of precisely the sort personality
psychology spent decades arguing matters.

The second line concerns what happens within situations. Shoda, Mischel,
and Wright (1994) observed children across repeated camp situations and
found that profiles of situation-behavior contingencies, the if-then
signatures, were stable and discriminative even when average behavior was
not. The textual analogue is straightforward to state: how a writer's
style shifts when they enter a particular kind of venue may itself be a
stable personal pattern, distinct from their average style. We treat such
signatures as a third measurement channel, and note that they require
their own null model, since some style shift in a venue is normative for
everyone who posts there.

Third, there is an old argument that assessment should sample the
ecology. Brunswik's representative design holds that generalization
requires sampling stimuli and situations from the organism's actual
environment rather than constructing systematic item sets (Dhami,
Hertwig, & Hoffrage, 2004). Viewed this way, the accumulated writing of a
person's daily life is not a poor cousin of the standardized test but the
more representative sample, closer in spirit to Mehl's naturalistic
sound-sampling of daily speech (Mehl, Gosling, & Pennebaker, 2006) or to
the thin slices of expressive behavior from which observers judge
strangers with surprising accuracy (Ambady & Rosenthal, 1992). What the
ecological tradition has lacked in text is standardized scoring, and that
lack, rather than any shortage of behavior, is what a text instrument has
to supply.

Fourth, a century of stylometry indicates where in language the personal
layer resides. Attribution work from Mosteller and Wallace (1963) onward
has repeatedly found that individuals are identified less by what they
discuss than by small habits of form: function words, punctuation and
orthographic habits, favored constructions. Van Halteren et al. (2005)
argued from such regularities for a "human stylome," and forensic work on
idiolect points the same way (Wright, 2017). Psycholinguistics adds that
stable individual differences extend even to native grammatical knowledge
(Dąbrowska, 2018). If context-invariant personal style exists in text, it
should live disproportionately in form; content vocabulary, by contrast,
is the natural carrier of situation. We will see that this division is
almost exactly what channel-separated measurement recovers.

A fifth consideration frames the whole. Fleeson (2001) showed that a
person's states are best described as a density distribution, with the
trait as parameters of that distribution; a corpus of text slices is such
a distribution, sampled from life rather than elicited by items. And the
idiographic tradition, from Allport (1937) through its modern
formalization in non-ergodicity arguments (Molenaar, 2004; Fisher,
Medaglia, & Jeronimus, 2018), warns that between-person structure does
not exhaust the individual. Furr's (2008) decomposition of profiles into
normative and distinctive components gives that warning a measurable
form, which we adopt for the residual layer of the framework.

Taken together, these literatures suggest a specific reading of a text
corpus: it is behavior, distributed over situations the person chose,
sampled from the person's ecology, in which the personal appears through
selection, through form-borne habits, through patterned situational
shifts, and in a residual that factor lists do not capture. The framework
below is an attempt to make that reading precise enough to be wrong.

## A Framework for Text as Situated Behavior

<!-- v3 TO CONTINUE (register locked by the sections above):
  - Assumptions stated in prose with minimal notation (slices as
    observations; contexts chosen, choice stable; additive decomposition),
    each with its empirical anchor and its testable character.
  - Propositions 1-3 presented as prose-first with one formal line each;
    proofs to Appendix. Prop 1 composite stability (the f=0 corpus, r=.64,
    "reliability is not evidence of style"); Prop 2 centering as mediator
    adjustment (exact cost; oracle -1.332 vs -1.335; coupling slope 1.40;
    boundary condition under assignment); Prop 3 identification via
    disjoint context sets -> the purity criterion.
  - The residual layer (Furr decomposition; seed-pattern stability .505 /
    .684 vs stranger null -.02) in one modest subsection.
  - Comparison licenses as a short subsection with Table 1.
-->

## Empirical Evidence

<!-- v3 TO CONTINUE:
  - Development corpus and tiers in two paragraphs (not a saga).
  - The falsification series (centering, three ways) as evidence FOR Prop 2.
  - Channel separation findings: purity classification of the 19-construct
    inventory (4 form-borne pass; content constructs fail); the
    apostrophe-omission case (human raters 0/8 yet r_B = .649 on unseen
    users) engaged with the stylometry expectation.
  - The preregistered sealed test, reported in full: design, a priori
    power, the 8-row table, omnibus FAIL 2/7, H2 r=.111 q=.002 and H6
    r=.096 q=.006 confirmed; the failed five classified post hoc as
    venue-borne/undetermined by the purity criterion; explicit statement
    of what this does and does not license.
  - Table 2: commitments and status (ledger-derived).
-->

## Discussion

<!-- v3 TO CONTINUE:
  - What the framework explains (open-vocabulary advantage as channel
    coverage; function-word robustness as the C2 channel; directional but
    not level transport; affect word-rates as states).
  - What it forbids (centering under self-selection; trait language
    without purity; cross-regime level comparison) and how practice
    changes.
  - Limitations: one platform plus student essays; English; heavy
    writers; no demographics; effect sizes at confirmation are small
    (r ~ .10-.11) and the instrument supports no individual decisions;
    the failed omnibus is reported as a constraint on claims, not
    explained away.
  - Future directions: the within-person multi-regime study (two regimes,
    two sessions, two languages) as the single design that tests the
    remaining joints; prospective sealed predictions already on record.
  - Closing paragraph: modest; the contribution is a reading of text as
    situated behavior, formal consequences of taking choice seriously,
    and a record of the account surviving, in part, a test built to
    kill it.
-->

## Open Practices Statement

All formal derivations, simulation code, frozen scoring resources, the
complete claims ledger including corrections and retractions, the sealed
preregistration, and the one-shot confirmatory report are available at
[ANONYMIZED REPOSITORY LINK]. No raw user text or identifiers are
redistributed; the source corpora are available from their original
publishers.

## Declarations

<!-- unchanged from v2 skeleton -->

## References

<!-- v3 additions to compile: Shoda, Mischel & Wright 1994; Mehl, Gosling
     & Pennebaker 2006; Ambady & Rosenthal 1992; Dhami, Hertwig & Hoffrage
     2004; Rauthmann & Sherman 2023; plus the v2 list. -->
