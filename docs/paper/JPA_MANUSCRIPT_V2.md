# [BLINDED MANUSCRIPT — Journal of Personality Assessment — v2 THEORY PAPER]

<!-- v2 reframing (user direction): a theoretical article that argues the
     theory; the validation program is compressed to a status table + one
     discipline paragraph + supplements. Style per THEORY_PAPER_STYLE_NOTES.
     Every number still traces to a ledger row. v1 (methods framing) is
     retained in the repo for the possible second, methods-venue paper. -->

# Text as Behavior in Chosen Situations: A Theory of Personality Assessment from Spontaneous Language

## Abstract

Language-based personality assessment rests on a contradiction. Its
predictive models succeed largely through topical features — what people
choose to write about — while its measurement practice treats topic and
venue as nuisance variance to be removed. We resolve the contradiction with
a theory that takes the choice seriously: a person's accumulated writing is
behavior distributed over situations the person selected, and personality
enters text through three channels — the selection of contexts, a
context-invariant style base, and person-by-context signatures. From three
axioms we derive results with immediate consequences for practice: raw
stability conflates style with frozen context choice (a simulated corpus
with no personal style at all yields retest r = .64 from choice alone);
statistically removing context means is mediator adjustment that deletes
person signal in exact, derivable amounts, with harmlessness only under
assigned topics; and trait language is licensed only by a purity criterion
separating the channels. The theory explains standing puzzles — why topical
features predict so well, why function words are the perennially robust
markers, why scores transport across platforms directionally but not in
level — and it forbids enough to be risky: its own preregistered omnibus
test failed (2/7) while confirming precisely the two channel predictions
(first-person rate to Neuroticism, r = .111; political-venue choice to
Openness, r = .096). We situate the theory in the lineages of situation
selection, behavioral signatures, representative design, stylometry, and
idiographic measurement, and derive what an assessment instrument built on
it must and must not claim. All materials, formal proofs, and a sealed
preregistration are public.

**Keywords:** personality theory; language-based assessment; situation
selection; behavioral signatures; idiolect; psychometrics

---

## 1. The Paradox

Two findings anchor the past decade of language-based personality
research, and as currently practiced they cannot both be right.

The first is predictive: personality is legible in everyday language, and
it is MOST legible in open-vocabulary features dominated by topics — the
activities, interests, and venues people write about (Schwartz et al.,
2013; Park et al., 2015; Eichstaedt et al., 2021). Open-vocabulary models
outpredict closed dictionaries precisely because they harvest content.

The second is methodological: in the same literature, topic is treated as
contamination. Pipelines residualize on content, stratify corpora by
subreddit or genre, or model topics in order to remove them, on the stated
logic that "how one writes" must be separated from "what one writes about"
before personality can be measured cleanly.

The practice refutes the finding. If topical variance were nuisance, its
removal would sharpen person signal; if topical features carry the best
signal, removing them should cost accuracy — but the field has mostly
treated the tension as an engineering trade-off rather than a theoretical
symptom. We tested the nuisance premise directly, in its strongest forms,
on 17.6 million comments: naive condition-mean centering, shrunken partial
centering, and two-way fixed-effects centering estimated out-of-sample with
cross-fitting. Every variant reduced the disjoint-occasion stability of
every style measure (pooled Δ = −.091, 95% CI [−.102, −.080]; cross-fitted
variants −.05 to −.07). The nuisance premise is not merely unhelpful; it is
backwards.

There is a second, quieter symptom. Text-based reliability is routinely
read the way questionnaire reliability is read: stable scores indicate a
stable disposition. But a writer who merely keeps visiting the same venues
will produce stable scores on any measure that venues influence, whether or
not any personal style exists. In a generative corpus constructed with NO
personal style whatsoever — style determined entirely by venue, venues
chosen with person-stable preferences — the ordinary retest correlation of
a "style" score is r = .64. Stability, by itself, evidences nothing about
style. The field's two most basic instruments of self-understanding —
partialling and reliability — both silently presuppose that contexts are
exogenous, an assumption imported from experimental design into corpora
where every context was chosen.

The resolution is not to pick a side but to change what the "noise" is.
Personality psychology has performed this move before. When behavior
refused to stay constant across situations, Mischel and Shoda (1995) did
not defend constancy or abandon personality; they reconceived the
situational variability itself as the signature — if A then X, if B then
Y — and the paradox dissolved. We propose the same move one level down.
The topical variance that language-based assessment deletes is not error
around the person; under self-selection it IS the person, expressed
through a channel the deletion destroys. What follows is a theory built
on that reversal, the formal results it entails, what it explains, and —
because a theory earns credit by what it forbids (Meehl, 1978) — the
risky commitments on which it stands or falls, including one preregistered
test it partly failed.

## 2. Theoretical Background: Five Pillars

The theory is not conjured; each load-bearing element has an established
lineage. We state what each pillar independently establishes, because the
theory is essentially their conjunction.

**Situation selection is behavior.** Persons and environments correspond
because people nonrandomly SELECT their milieus, evoke reactions, and
manipulate settings (Buss, 1987); modern situation research documents that
everyday situation contact and construal are trait-congruent (Rauthmann
et al., 2015). In a text corpus, the venue and topic of every utterance
are recorded selections. A measurement theory that discards them discards
behavior — the very category assessment claims to sample.

**Variability is patterned, and the pattern is personal.** The behavioral
signature literature established that cross-situational variation is not
error but structure: stable, individual if–then profiles (Mischel & Shoda,
1995). Its textual consequence: a person's deviation from their own
baseline within particular context classes is a measurable signature
channel, distinct from their average.

**Assessment should sample the ecology.** Brunswik's representative design
holds that generalization requires sampling situations representatively
from the organism's ecology, not constructing systematic item sets. A
person's accumulated spontaneous writing is exactly such an ecological
sample — abundant, unprompted, produced in the situations of the person's
actual life. The questionnaire is the systematic design; sliced natural
text is the representative one. What the tradition lacked is what makes
the ecological sample usable for measurement: frozen, auditable scoring.

**Individuality lives in form.** A century of stylometry — from
function-word authorship attribution (Mosteller & Wallace, 1963) to the
"human stylome" (van Halteren et al., 2005) and idiolectal co-selection
(Wright, 2017) — shows that the person-unique layer of language is carried
disproportionately by form: function words, orthographic habit,
morphosyntactic co-selection. Psycholinguistics adds that even native
grammars differ stably between individuals (Dąbrowska, 2018). Form
habits are the natural candidates for context-invariant style; content
vocabulary is the natural carrier of context.

**Traits describe distributions; persons exceed factor lists.** Whole
Trait Theory models a trait descriptively as a density distribution of
states (Fleeson, 2001; Fleeson & Jayawickreme, 2015) — and a corpus of
slices is literally such a distribution, with trait scores as its
parameters. At the same time, the idiographic tradition (Allport, 1937),
its modern formalization in non-ergodicity results (Molenaar, 2004;
Fisher et al., 2018), and profile-decomposition psychometrics (Furr, 2008)
jointly caution that no between-person factor structure exhausts an
individual — and give the residual a measurable definition: what remains
after the normative profile is subtracted.

Conjoined, the pillars entail a specific object: spontaneous text is
behavior distributed over selected situations, sampled from the person's
ecology, in which personal signal resides in the selection itself, in
form-borne invariant habits, in patterned situational deviations — and in
a residual no factor list captures. A theory of text-based assessment
should be the formalization of exactly this object. We now give it.

## 3. The Theory

### 3.1 Axioms

**A1 (Slices are behavioral observations.)** A corpus is partitioned into
small fixed-length utterance slices; each slice is one observation of
verbal behavior in a context. A person is represented by the distribution
of their slices — the density-distribution view, applied to text.

**A2 (Contexts are chosen, and choice is person-stable.)** Each slice
carries its context r (venue/topic shell). Contexts are self-selected in
free ecologies, and the person's context distribution π_u is a stable
personal attribute (the situation-selection pillar, recorded rather than
inferred).

**A3 (Additive decomposition.)** Slice scores decompose as
y = f_u + b_r + γ_{u,r} + e: a context-invariant personal base f, a
context effect b, a person-by-context interaction γ, and slice noise.

### 3.2 The three channels, as consequences

From A1-A3, personality enters text through exactly three routes: the
choice distribution π_u (C1); the invariant base f_u (C2); the structure
of γ_{u,r} (C3 — the behavioral signature, in text). Nothing else in the
model carries person indices. Channels are not metaphor; they partition
the person-bearing terms of A3.

### 3.3 Formal results

*(Proofs and simulation verifications in Supplement A; stated here in
words first.)*

**Theorem 1 (Composite stability).** The raw person mean measures
f_u + m_u, where m_u = Σ_r π_ur·b_r is the context-mix term; because π_u
is stable (A2), m_u is stable. Hence retest stability of raw scores
conflates C2 with frozen C1: shared-context retest covariance equals
Var(f) + Var(m) + 2Cov(f, m). Corollary (demonstrated): with f ≡ 0, raw
retest still reads r = .64. Stability licenses no trait language without
channel separation.

**Theorem 2 (Centering is mediator adjustment).** Removing estimated
context means subtracts m̂_u. Under choice-effect independence the removed
retest covariance is exactly Var(m) + 2Cov(f, m) (oracle simulation:
−1.332 observed vs. −1.335 predicted); under person-context coupling the
removal exceeds even this, because estimated context effects absorb the
personal base of those who chose the context (estimated-on-true slope
1.40 at coupling κ = .7; observed removal −1.583 vs. first-order −1.294).
Boundary condition: with exogenously assigned contexts, m ≡ 0 and
centering is harmless. Topic control is cleaning only in assigned designs;
under self-selection it is deletion, in derivable amounts.

**Theorem 3 (Identification requires disjointness).** Splitting a person's
contexts into disjoint sets removes the mix-mix covariance term (under
independent context effects and choice-effect uncoupling), so disjoint-set
retest isolates the flesh term up to coupling cross-terms — an upper
bound; a class-disjoint variant additionally removes category-level
mediation. This yields an operational PURITY CRITERION: a construct may be
described in trait language only if its class-disjoint stability is
substantial while its choice-mediated share is small.

**Result 4 (Loading-weighted precision).** Context heterogeneity taxes
reliability in proportion to the construct's context loading: venue-mix
entropy costs precision on context-borne constructs and spares form-borne
ones.

**Result 5 (Overidentification: the theory polices itself).** Transport
across occasions or registers is bounded by √(rel₁·rel₂); independent
mediation estimators must agree; disagreement is a built-in
misspecification alarm. (It has fired in our own data; affected estimates
are reported as intervals.)

**Corollary (Comparison licenses).** Scores are comparable only within the
radius their channel composition supports: within-context monitoring;
cross-theme for purity-passing constructs; cross-register with per-register
norms; cross-regime, direction and within-population rank ONLY — level
comparison across free/assigned/domain-locked regimes is forbidden by
Theorem 2's boundary structure, and no covariate adjustment can restore it.

### 3.4 The idiographic layer

Let the normative profile be the population mean over constructs; a
person's SEED PATTERN is their deviation profile after its removal (Furr,
2008). The theory adds a third descriptive layer to assessment — position
(scores on channel-separated constructs), configuration (if-then
signatures), residual (the seed pattern) — and makes a falsifiable claim:
the residual is not noise but stable individuality. Measured: across
occasions months apart, seed patterns correlate at median r = .505 against
a stranger null of −.02 (and .684 using form constructs alone), while
roughly a third of machine-identifiable person signal remains outside the
factor list altogether yet person-stable. No two seed patterns need
coincide; that is not a poetic flourish but the operational content of
the fingerprint intuition — individuals are codable without being
exhaustible by factors.

## 4. What the Theory Explains

A theory should retrodict the field's robust findings more economically
than the assumptions it replaces.

**Why open-vocabulary features predict so well.** They harvest C1. Topic
and venue words carry the choice channel that closed style dictionaries
exclude by design; the prediction advantage of open vocabularies over
closed ones (r ≈ .31–.41 vs. .21–.29; Schwartz et al., 2013) is, on this
theory, mostly channel coverage, not lexical resolution.

**Why function words are the perennial markers.** They are flesh. The
stylometric constant — that attribution and stable individual style ride
on form — is the C2 channel seen from another discipline. In our own
inventory, the constructs that survive the purity criterion are precisely
form habits (pronoun rate, apostrophe omission, negation, profanity),
while every content-vocabulary construct fails it; the strongest
flesh-pure construct in the inventory is an orthographic habit invisible
to human raters (0/8 in blind coding) yet held at r_B = .649 on unseen
users — individuality in form, exactly where stylometry said it lives.

**Why scores transport directionally but not in level.** Theorem 2's
boundary structure implies levels are regime-bound (venue norms, prompt
constraints, platform production limits), while direction of
construct-anchor relations rides on f and π structure. Observed: a battery
fitted on Reddit transported unchanged to student essays keeps mean
directional validity (r ≈ .144) at the level of an opaque embedding
transfer (≈ .153), while level comparability fails; and the theory's two
channel predictions confirmed across the corpus boundary in the sealed
test below.

**Why affect word-rates disappoint as traits.** Affect vocabulary is
mostly slice-level and occasion-level variance (state, in the
density-distribution sense) with heavy context loading (Result 4): its
raw stability is context-borne, its purified stability near zero — our
tension construct is the in-house demonstration, undetermined under the
purity criterion and dead as a trait, exactly as the whole-trait
distinction predicts for a state-like quantity sampled at the wrong
timescale.

**Why the person-situation debate recurs in every text pipeline.** The
pipeline choice "residualize context or not" restages the 1968 debate
inside an estimator. The theory's answer is the same as the field's
eventual answer: the variance in dispute belongs to the person via
selection and signature; treat it as a channel, control it by design.

## 5. What the Theory Forbids, and How It Has Fared

Risky content, stated as prohibitions and standing predictions
(full empirical status of every claim: Table 2; all artifacts public).

**Forbidden: topic control under self-selection.** Falsified as predicted,
three independent ways (Section 1); the theorem supplies the mechanism and
the exact cost.

**Forbidden: trait language from raw stability.** The purity criterion
must be passed first; applying it to our own 19-construct inventory
demoted most of it (4 flesh-pure, 8 venue-borne, 6 composite, 1
undetermined) — including constructs we had previously described as
style.

**Forbidden: cross-regime level comparison.** No covariate can restore it
(Theorem 2); the tested statistical shortcut (restricting to form
coordinates) also failed empirically, leaving design (within-person
multi-regime sampling) as the only route — a designed study we specify.

**Standing predictions.** Assigned-context corpora are the boundary
condition where centering turns harmless (testable on any prompted
corpus); flesh concentrates in form under every scorer revision;
prospective, hash-sealed structural predictions about not-yet-written text
are on public record awaiting their windows.

**The sealed test, reported whole.** One preregistered, one-shot
confirmatory opening was executed against quarantined labels (hypotheses,
directions, eligibility, correction, and success rule sealed in public
beforehand). The omnibus rule FAILED: 2 of 7 hypotheses at BH-FDR q < .05
where 4 were required. The two that confirmed are the theory's two core
channels — first-person rate to Neuroticism (r = .111, 95% CI [.051,
.170], q = .002) and political-venue choice to Openness (r = .096, [.036,
.155], q = .006) — and the five that failed are, without exception,
constructs the purity criterion (derived afterward, applied
retrospectively) classifies as venue-borne or undetermined. We report
this as the discipline functioning: the framework's own admission gate,
had it existed at preregistration time, would have forbidden most of the
failed hypotheses; the channels the theory is actually about survived a
test designed to kill them.

## 6. Implications for Assessment

**What an instrument looks like.** Two phases by design: free collection
(C1 alive: choice profile + ecological style sampling) and
assigned-context battery (C1 silenced; C2 purified by the boundary
condition) — the corrected form of the old ambition to combine the
questionnaire's standardization with the performance sample's spontaneity.
Scores report in three layers (position, configuration, residual), each
carrying its comparison license; forbidden comparisons are refused by the
released software rather than left to prose.

**What may be claimed.** Trait language only past purity; direction and
rank across regimes, never level; state language only at the timescale the
sampling supports; identity-grade claims (the residual layer) only against
stranger nulls. These are theorems-turned-norms, not stylistic caution.

**Epistemic discipline, in one paragraph.** Because the theory was built
and tested largely by AI systems under human direction, every estimator
was licensed against generative worlds that violate the theory's own
axioms before its output could support a claim; all confirmatory material
sat behind a public hash-sealed preregistration executed exactly once; and
every substantive result passed an adversarial audit with full
recomputation rights, which caught and corrected thirteen builder errors
across eleven rounds — each error, its catch, and the standing rule it
produced being part of the public record. The machinery is described in
the Supplement; its point is single: a theory paper's claims are only as
good as the process that could have falsified them, and this one is
designed to be falsified in public.

**The designed next study.** The theory's remaining untested joints —
state timescales below the month, dialogue registers, cross-regime
level equating, and a second language — are closed by one design: the
same persons sampled in two regimes, two sessions, and two languages,
with anchors and informants; its full specification is public. The
present paper claims exactly what the current evidence licenses, and
specifies what would extend or kill it.

---

## Open Practices Statement

All formal proofs, generative-world licensing suites, the frozen scorers
and context maps, the complete claims ledger (including retractions), the
sealed preregistration and its one-shot opening report, and every number's
source artifact are available at [ANONYMIZED REPOSITORY LINK — view-only
for review]. No raw user text or identifiers are redistributed; dataset
access follows the original publishers' terms.

## Declarations

<!-- Funding: [tbd]. COI: none. Ethics: secondary analysis of public
     pseudonymous corpora; no new data collection. Consent: n/a.
     Data/code availability: public repository (anonymized for review).
     AI use: theory development, analysis, and audit executed by AI
     systems under the governance protocol summarized in Section 6;
     the human author fixed criteria, adjudicated scope, and bears final
     responsibility. -->

## Table 2 (placeholder) — The theory's commitments and their empirical status

<!-- One row per claim: Claim | Derivation | Test | Status (tier) | Source.
     Populate from CLAIMS_LEDGER: T1 composite (W-B .64); T2 centering
     (P2 -.091, E1 crossfit, oracle -1.332/-1.335, coupling 1.40); T3
     purity (F4/C8/comp6/und1); licenses (OP-7a 19/19; PRED-4 fail);
     residual (.505/.684 vs -.02); lockbox (2/7; H2 .111; H6 .096);
     prospective seals (pending). -->

## References

<!-- APA 7. Add: Buss 1987; Rauthmann et al. 2015; Brunswik/representative
     design (Dhami et al. 2004 review); Mosteller & Wallace 1963;
     van Halteren et al. 2005; Wright 2017; Dąbrowska 2018; Fleeson 2001;
     Fleeson & Jayawickreme 2015; Allport 1937; Molenaar 2004; Fisher et
     al. 2018; Furr 2008; Mischel & Shoda 1995; Meehl 1978; Schwartz et
     al. 2013; Park et al. 2015; Eichstaedt et al. 2021; Pennebaker &
     King 1999; Boyd & Schwartz 2021; Meyer et al. 2001; Mihura et al.
     2013; Benjamini & Hochberg 1995; Gjurković et al. 2021. -->
