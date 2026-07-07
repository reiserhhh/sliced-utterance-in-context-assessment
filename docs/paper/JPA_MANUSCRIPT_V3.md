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

The framework needs three assumptions, none exotic. First, a corpus can be
read as a sample of behavioral observations. We partition each person's
text into slices of fixed token length and treat each slice as one
observation of verbal behavior in a context, so that a person is
represented by a distribution of observations rather than by a single
document. This is the density-distribution view of traits (Fleeson, 2001)
transposed to text, and it matters for the same reason it mattered there:
means, spreads, and contingencies of the distribution are different
quantities, and collapsing them loses information. Second, every slice
carries a context label, and in free ecologies the context was chosen.
The choice distribution appears to be quite stable in its own right; in
our development corpus, the similarity of a user's venue distribution
across time separates same-user from different-user pairs with an area
under the curve near .84, before any style measure enters. Third, we
assume slice scores decompose additively into a person base, a context
effect, a person-by-context interaction, and noise. We treat this as a
working approximation rather than a metaphysical commitment; several of
its testable consequences are examined below, and one of our own
estimators exists mainly to sound an alarm when the approximation fails.

Under these assumptions, personality can reach a text score through
exactly three routes: through the choice distribution itself, through the
context-invariant base, and through the structure of the interaction
term. We refer to these as the choice, base, and signature channels. The
point of naming them is not taxonomy but bookkeeping: every claim about
"style" is implicitly a claim about which channel carries the observed
covariance, and the channels behave differently under the operations
researchers routinely apply.

Three propositions make this concrete. Proofs are elementary and given in
the Appendix; we state the content in words.

*Proposition 1 (stability is a composite).* The mean of a person's slice
scores estimates the sum of their base and a choice-weighted mixture of
context effects. Because the choice distribution is stable, the mixture
term is stable too, and retest correlations of raw scores therefore
reflect both channels at once. The practical consequence is easy to
underestimate. In a simulated corpus built to contain no personal style
whatsoever, only styled venues and person-stable venue preferences,
ordinary disjoint-occasion retest correlations still reach .64. High
"reliability" of a text measure, taken alone, does not indicate a style
trait; it indicates only that something person-linked is stable, and
that something may be the person's taste in venues.

*Proposition 2 (centering is mediator adjustment).* Subtracting estimated
context means from scores removes the mixture term, and with it every
part of the person signal that travels through choice. Under independence
of choice and context effects, the removed retest covariance can be
written in closed form, and simulation with known ground truth reproduces
it almost exactly (predicted −1.335, observed −1.332 in covariance
units). When choice and context effects are coupled, as they are whenever
people seek out venues that suit their style, the estimated context
effects additionally absorb part of the base itself, and centering
removes more than the closed form predicts; in our simulations the
regression of estimated on true context effects reaches a slope of 1.40
under strong coupling. The boundary condition is the useful part: when
contexts are assigned rather than chosen, the mixture term is null and
centering is harmless. This is, we believe, why the same operation that
behaves sensibly in prompted-essay research quietly damages measurement
in social media corpora.

*Proposition 3 (identification needs disjointness).* If stability is a
composite, separating the channels requires comparing scores computed on
disjoint sets of contexts, so that shared context effects cannot carry
the correlation. Splitting at the level of individual venues removes most
of the mixture; splitting at the level of venue categories removes
mediation that operates through correlated context effects within a
category. From this we derive a purity criterion for trait language: a
construct is described as a style trait only when its category-disjoint
stability remains substantial while its estimated choice-mediated share
is small. The thresholds we use (disjoint stability of at least .15 with
a mediated share below .30) are operational conventions, not derived
constants, and we flag them as such.

Two further elements complete the framework. The first is a residual
layer. Following Furr's (2008) decomposition, we subtract the normative
profile from each person's vector of construct scores and treat what
remains, the distinctive profile, as a measurable quantity in its own
right. The theoretical motivation comes from the idiographic tradition
and from non-ergodicity arguments (Molenaar, 2004; Fisher et al., 2018):
between-person structure should not be expected to exhaust the
individual. Empirically it does not. Distinctive profiles correlate with
themselves at a median of .50 across occasions months apart, against a
stranger-pairing baseline of essentially zero, and the correlation rises
to .68 when computed on form-based constructs alone. A further sign
points the same way: roughly a third of the person-identifying signal
recoverable by a modern text embedding lies outside our construct list
altogether, yet is itself stable across occasions. Individuals appear to
be codable well beyond what any fixed factor list captures, which is
what the idiographic tradition has said all along, now with a number
attached.

The second element is a set of comparison licenses. Because channels
respond differently to changes of platform, prompt, and language, a score
earns comparability only within a stated radius, and the radius differs
by construct family. Within-person monitoring in a fixed context is the
least demanding case; comparisons across themes require purity;
comparisons across registers require register-specific norms; and
comparisons of score levels across regimes (free versus assigned versus
domain-locked writing) are not licensed at all, because Proposition 2
implies that no statistical adjustment can equate them. We found it
useful to encode these licenses in the released software, which declines
out-of-license comparisons rather than leaving the matter to a footnote.

## Empirical Evidence

The evidence summarized here comes from a development program conducted
on public corpora, with every analysis, correction, and retraction
recorded in a public claims ledger; we report the parts that bear on the
framework's claims and keep procedural detail in the Supplement. The
main corpus is PANDORA (Gjurković et al., 2021), 17.6 million Reddit
comments from roughly ten thousand users; development analyses used
3,183 users with sufficient text in disjoint time windows. A second
corpus of prompted student essays (Pennebaker & King, 1999) served as
the assigned-context contrast. Confirmation labels were quarantined from
the start behind a preregistration sealed by the initial commit hash of
a public repository, and were read exactly once.

*The centering test.* Proposition 2 predicts that removing context means
from self-selected text should reduce, not improve, the stability of
person scores. It does. Across the five style measures of our initial
battery, condition-mean centering lowered disjoint-occasion stability in
every case, with a pooled change of −.09 (95% CI [−.10, −.08]); partial
centering at any shrinkage level behaved the same way; and two-way
fixed-effects centering estimated out of sample, the strongest version we
could construct, still cost between .05 and .07 per measure once a
self-estimation leak in our first attempt was found and corrected. On
the assigned-context side, the same operations are unproblematic, as the
boundary condition requires.

*Where the person signal lives.* Applying the purity criterion of
Proposition 3 to our full inventory of nineteen lexical constructs sorted
them cleanly. Four passed as candidate style traits, and all four are
form habits: first-person rate, apostrophe omission, negation, and
profanity. Every construct defined by content vocabulary failed, with
estimated choice-mediated shares between roughly .33 and .61; six were
mixed; one (an affect composite) had too little disjoint stability to
classify at all. The apostrophe case is worth a sentence, because it is
the strongest style trait in the inventory (category-disjoint stability
.37) while being invisible to people: in blind coding, human raters
identified it at chance (0 of 8), whereas the construct held a
cross-validated stability of .65 on users never seen during its
construction. Individuality in written language seems to reside
disproportionately in small mechanical habits, which is precisely what
the stylometric tradition would have predicted, and content vocabulary
behaves like what it is, a record of where the writer goes. Consistent
with this division, character n-gram co-selection axes, fitted on one
half of the users and transported to the other, added twenty-one
dimensions of stable signal not redundant with the word-level battery,
about fifteen of them form-like.

*Transport.* The framework expects direction to travel better than
level. A battery fitted entirely on Reddit and applied without
refitting to the student essays retained directional validity (mean
cross-validated correlation with Big Five scores of about .14,
comparable to a transported text-embedding baseline of about .15), while
score levels and covariance structure did not transport; within Reddit,
all nineteen constructs survived a register shift from top-level posts
to replies once volume was matched, with level shifts confined to two
venue-linked constructs.

*The sealed test.* The strongest evidence, in both directions, comes
from the preregistered opening. Seven directional hypotheses over
quarantined Big Five labels (n = 1,058 eligible users) and one secondary
bridge hypothesis were fixed in public, with eligibility rules,
Benjamini-Hochberg correction, a priori power calculations, and a
success rule of at least four of seven confirmed, before any label was
read; the analysis script itself was hash-pinned after an adversarial
audit, and ran once. The omnibus rule failed: two of seven hypotheses
survived correction. The two survivors are the two that follow most
directly from the framework's channels: first-person rate predicted
Neuroticism (r = .111, 95% CI [.051, .170], q = .002), and choice of
political venues predicted Openness (r = .096, [.036, .155], q = .006).
No significant effect ran opposite to its preregistered direction. The
five failures were, without exception, hypotheses about constructs that
the purity criterion, derived after the fact, classifies as venue-borne
or unclassifiable; had the criterion existed at preregistration time, it
would have barred most of them from confirmatory testing. We report the
failure as a failure. What the opening licenses is deliberately narrow:
the two channel-level directional claims, at small effect sizes, in one
population. What it illustrates more broadly is that the framework's
admission rules and its confirmatory record point the same way.

Table 2 summarizes each commitment of the framework, the test it has
faced, and its current status, with sources for every number.

## Discussion

The framework began as an attempt to explain one uncomfortable result,
and its value should be judged by how much else it organizes. Several
standing features of the literature follow naturally once text is read
as behavior in chosen situations. The predictive advantage of
open-vocabulary methods over closed dictionaries (Schwartz et al., 2013;
Kern et al., 2014) is expected, because topical features carry the
choice channel that style dictionaries exclude by construction; on this
reading the advantage reflects channel coverage more than lexical
resolution. The decades-long robustness of function words as individual
markers, from authorship attribution to Pennebaker's program, is equally
expected, because form habits are where the context-invariant base
lives. The common observation that language models and dictionaries
alike transfer poorly across platforms in level, while rank-order
relations survive in attenuated form, matches the framework's boundary
structure: levels are regime-bound, direction travels. And the repeated
disappointment of affect word-rates as trait measures has a simple
description here: they are heavily context-loaded and behave as states
sampled at the wrong timescale, which is what the density-distribution
view would suggest.

The account also forbids things, and the prohibitions are its most
practical output. It forbids topic and venue centering as a default in
self-selected corpora, and specifies the design alternative (assigned
contexts) under which the same operation becomes safe. It forbids trait
interpretation from reliability alone, supplying instead an operational
purity check that our own inventory largely failed. And it forbids
comparing score levels across free, assigned, and domain-locked writing,
a comparison that current practice performs implicitly whenever
platform-trained models are applied elsewhere. We would regard the
framework as damaged if a well-designed study showed context centering
improving disjoint-occasion person stability in a clearly self-selected
corpus, or showed level comparability across regimes achieved by
statistical adjustment alone.

Several limitations bound what we claim. All trait-level evidence comes
from one platform plus one prompted-essay corpus, in English, from
people who write a great deal; eligibility rules discard light writers,
and nothing here speaks to them. The corpora carry no demographics, so
measurement invariance across age, gender, or device could not be
examined. The confirmed effects are small (r ≈ .10-.11), far below what
any individual-level decision would require, and we make no applied
claims. The omnibus preregistered criterion failed, and although the
pattern of failures is informative, it was diagnosed with a criterion
built afterward; the diagnosis is a hypothesis about the next study, not
a rescue of this one. Finally, the program was largely executed by AI
systems under human direction. We treated that as a reason for stricter
governance rather than lighter: estimators were licensed against
generative worlds violating the framework's own assumptions,
confirmatory material sat behind a one-shot public seal, and an
adversarial audit with full recomputation rights caught thirteen real
errors across eleven rounds, all documented. The audit trail is part of
the evidence, in the same sense that a telescope's calibration record is
part of an observation.

Two studies would move the account decisively. The first is a
within-person, multi-regime design: the same participants writing in
free and assigned contexts, twice, in two languages, with questionnaire
and informant anchors. That single design tests level equating across
regimes (the one comparison we currently forbid), state structure below
the month timescale, dialogue registers, and the cross-language
generality of the form-based channel, and its full specification is
public. The second is already running in a weak form: structural
predictions about text not yet written, sealed by hash in advance. Both
follow the same policy that produced the present results, which is to
make the framework easy to kill and then report whether it died.

Personality assessment has long treated the standardized test and the
spontaneous sample as belonging to different traditions, one scorable
and one rich. A person's accumulated writing suggests the distinction is
not fundamental. What people write about, where they choose to write it,
and the small mechanical habits that persist regardless are all behavior;
read together, under rules that respect which channel carries which
signal, they yield an assessment that is standardized in scoring and
ecological in origin. The present framework is one way to make that
reading precise, and, so far, it has survived its own tests only in the
places it said it would.

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
