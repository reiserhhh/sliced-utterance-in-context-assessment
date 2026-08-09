# SUICA Identity Theory v1 (IDT) — Identity as the Reproducible Component of Deviation

Status: **THEORY DRAFT v1, registered 2026-08-09.** Tier: EXPLORATORY.
Empirical program: `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md` (legs K1..K3).
The claims ledger controls. This document states the theory, its proofs where
elementary, its retrodictions against persisted program measurements, and its
registered falsifiable predictions. It is appended to, never rewritten.

Division of labor for this line (program owner's directive, 2026-08-09):
theory/registration/adjudication by the planner; implementation and execution
by dispatched agents.

---

## 0. The conjecture being formalized

Program owner, 2026-08-09 (two messages, paraphrased with permission of
context):

- **C-1 (structured residual).** Within the same group and the same topic, the
  per-person deviation that classical analysis treats as error is not
  measurement error but identity itself.
- **C-2 (indeterminate magnitude).** That is why the "error's" size is
  indeterminate and appears unmeasurable.
- **C-3 (certificate).** It functions like an identification card.
- **C-4 (similarity and direction, second message).** If identity exists, are
  deviation-close people personality-close? Deviations have direction: a pair
  can be close in distance yet opposite in direction — how does the theory
  close this?

IDT retains C-1, C-3 and C-4's substance, and converts C-2 from an obstacle
into a theorem, with two repairs: a **reproducibility discriminator** (not all
deviation is identity) and **frame-relativity** replacing unmeasurability.

## 1. Frame and objects

A **frame** is F = (P, O, h, U):

- P — the reference sample ("issuer"): the persons whose behavior defines the
  norm;
- O — the occasion universe ("jurisdiction"): the occasion-generating process
  ν, its support and design (shared vs person-specific occasion sets);
- h — the horizon ("expiry"): the time span the universe covers;
- U — the representation ("units"): coordinates in which behavior is a vector;
  in SUICA, the frozen map plus basis.

Objects, all P-type indexed by O in V8's typing discipline:

- behavior x(i,o) ∈ R^m for person i on occasion o, in representation U;
- **norm field** μ̂(o) = mean_{j∈P} x(j,o);
- **deviation field** d(i,o) = x(i,o) − μ̂(o);
- **card** c(i) = mean over person i's sampled occasions of d(i,o), from n
  occasions; r_i = ‖c(i)‖; θ_ij = angle between c(i), c(j);
- **readability** ρ_i = cos(c⁽¹⁾(i), c⁽²⁾(i)) over disjoint occasion halves;
- **identifiability** I = rank-1 re-identification rate: probe cards from one
  half matched by nearest neighbor against a gallery of cards from the other.

## 2. Axioms (modeling commitments, frame-indexed — not metaphysics)

- **A1 (decomposition).** x(i,o) = μ(o) + b(i) + s(i,o) + ε(i,o), with
  E_i[b] = 0; s the state process with person-specific within-horizon mean
  s̄_i(O) (possibly nonzero); ε exchangeable noise. Every component is defined
  relative to (population, ν, U); none is metaphysically absolute.
- **A2 (diversity).** Var_i[b] > 0 at some scale of U.
- **A3 (state structure).** s has autocorrelation time τ_s under the occasion
  process; ε has none.

## 3. Results

Status tags: [PROVED] — elementary proof, stated here; [IMPORTED] — proved
earlier in the program; [PRINCIPLE] — stated, not proved; [OPEN] — registered
branch to be decided by a K-leg.

### T1 — Gauge trichotomy: "the magnitude is indeterminate" is a theorem [PROVED]

Three independent gauge channels move ‖c‖, each with a distinct signature:

1. **Units (U, scalar subgroup).** c ↦ γc, γ>0: all norms scale, all angles
   and shares are fixed (degree-0; the M4-H1 identity [IMPORTED]).
2. **Issuer sampling (P).** μ̂ = μ + δ_P with δ_P = O_p(σ_pop/√|P|): every
   card translates by −δ_P — a **common translation**; the centered
   configuration is exactly invariant (T2).
3. **Jurisdiction (O).** ν → ν′ moves c(i) by s̄_i(ν′) − s̄_i(ν) — a
   **person-specific** shift; the centered configuration genuinely changes.

Beyond the scalar subgroup, U-freedom (diagonal/general basis change) also
moves angles; that freedom is real and materially large in this machinery —
the M4-H line moved the frame displacement by 45.79% through basis
normalization alone [IMPORTED].

**Consequence.** A frame-free "size of identity" does not exist; requesting it
is a type error. C-2's felt indeterminacy is the superposition of three gauges
— and each is detectable by its signature: common translation (issuer error)
vs person-specific shift (jurisdiction change) vs coordinate effects (units).

### T2 — The invariant layer [PROVED]

The centered-card configuration — the Gram matrix of {c_i − c̄} up to overall
scale; equivalently every angle and every norm **ratio** between centered
cards — is exactly invariant under scalar-U and issuer translation. Shares and
cosines are degree-0 in any per-world scalar [IMPORTED: M4-H1, confirmed at
2.22e-16]. Identity claims should be typed on this layer.

### T3 — Issuer cancellation [PROVED in card space]

On shared occasions with a common norm:

- (a) within-occasion contrasts x(i,o) − x(j,o) are exactly norm-free;
- (b) card differences c_i − c_j are exactly issuer-free;
- (c) nearest-neighbor re-identification with a common probe/gallery norm is
  exactly invariant to μ̂ — the norm cancels term-by-term in every distance.

Corollaries:

- (d) **Relative identity needs no issuer; absolute identity does.** The
  person-configuration is issuer-free; the individual card is not.
- (e) **Free-response designs break the cancellation twice**: person-specific
  occasion sets O_i import issuer-sampling error (mean_{O_i} μ̂ − mean_{O_j} μ̂
  no longer cancels) AND jurisdiction misalignment (s̄_i(O_i) vs s̄_j(O_j)
  confound the comparison).
- (f) For the **deployed relational gauge** the cancellation is an
  idealization to be TESTED, not assumed: the frozen map is nonlinear, so a
  pre-map common shift need not cancel post-map. [OPEN → K1 lean L5.]

Retrodiction: M4-F2's composition law — free −0.0027727743463521505 vs shared
+0.023390488960374076, paired +0.026163263306726227, CI [0.019536, 0.032791],
t=9.3351, 8 worlds (artifact precision, re-verified 2026-08-09) — is (e)
appearing as measurement. K1 decomposes its ownership between the issuer-error
and jurisdiction-misalignment channels.

### T4 — Card ≠ biography [PROVED as algebra; empirical form OPEN → K2]

The card estimates b_i + s̄_i(O) + O_p(n^{−1/2}); the trait is b_i; the gap is
s̄_i(O).

- (a) **State helps the card and poisons the biography.** Person-specific s̄_i
  adds between-person dispersion — identifiability RISES — while shifting
  cards off b, capping trait recovery at the attenuation factor
  σ_b/√(σ_b² + Var_i[s̄_i]). A forged watermark: it makes the card easier to
  read and wrong about its holder.
- (b) Var_i[s̄_i(O)] shrinks only as the occasion universe spans many state
  correlation times (h/τ_s grows) — not with more occasions inside a fixed
  span, not with more authors, not with more text per author.

Retrodictions: M4-F5's dissociation (internal agreement 0.0061→0.3861 while
long-window truth recovery plateaus 0.0225→0.1501; same-occasion recovery
0.1497→0.6371 — synthesis precision); F10 (the foundation gap) is T4 stated as
typing: within one jurisdiction, b and s̄ are not separately identified.

**Open branch.** M4-F9 measured occasion spreading (B8−B1 long-window
difference −0.0163, CI [−0.0559, +0.0233]) and found no gain. T4-simple
predicts spreading helps only via h/τ_s; whether F9's arms changed h/τ_s or
only the arrangement inside a fixed span decides between **T4-simple** and
**T4-reader-mediated** (the gauge itself is state-inclusive: M4-F6 showed the
gauge is B-invariant, 0.0297–0.0365). That derivation from persisted F6/F9
artifacts is K2's Part 0 and the theory's first internal falsification
opportunity. [OPEN]

### T5 — No anchor-free reading [PRINCIPLE]

Every reader anchors somewhere, and each anchor has a price:

| reader | anchor | price |
|---|---|---|
| absolute (card) | issuer estimate μ̂ | sampling error, O_p(1/√|P|) (T3e) |
| relational (configuration/NN) | co-present gallery | composition dependence: decisions change with who else is read |
| coordinate | representation U | basis dependence (the M4-H territory) |

Conjecture **C-NFI** ("no free issuer"): no reader is invariant to all three.
Stated, not proved. K1 measures the first two prices on the same worlds.

### T6 — The discriminator: deviation is identity iff it reproduces [DEFINITIONAL + measured instances]

**Id(i | F) := the occasion-resample-stable component of d(i,·).**

- Positive instance [IMPORTED]: the author axis is a validated law — M4-F4,
  γ=1.096 [0.984, 1.218], ×32 holdout predicted 0.4012 / observed 0.3861.
- Negative instance [IMPORTED]: the S4 residual — M4-H6, 0/3 worlds clear the
  repetition-shuffled null (knife-edge −0.0009 in the closest) — deviation
  with nothing reproducible is NOT identity and cannot be captured by any
  basis.

C-1 is retained exactly in this form: the structured residual is the
reproducible part; the rest is honest noise. The per-person readability ρ_i is
itself a person-level coordinate (the "biometric menagerie" coordinate):
**how legible one's card is, is part of one's identity.**

### T7 — Direction reads, magnitude gauges [PROVED noiseless; noisy form → K3]

With all other cards fixed: per-person directional scaling c_i ↦ αc_i (α>1)
never decreases person i's nearest-neighbor margin; norm-preserving rotation
by angle φ degrades the match with the person's own reproducible direction as
cos φ. The certificate is carried by **direction on the invariant layer**;
magnitude is partly gauge (T1) and partly a real individuation coordinate
(distinctiveness). The face-space caricature effect is this theorem in another
literature's clothing.

### T8 — Similarity geometry: when are "deviation-close" people "pattern-close"? [PROVED in card space; estimator form → K3]

This answers C-4.

- (a) **Decomposition (law of cosines).**
  ‖c_i − c_j‖² = (r_i − r_j)² + 2 r_i r_j (1 − cos θ_ij).
  Raw deviation distance conflates **magnitude mismatch** with **direction
  mismatch** — the profile-similarity elevation/scatter/shape problem
  (Cronbach–Gleser), restated in card space.
- (b) **Anti-direction bound.**
  cos θ_ij < 0 ⟺ ‖c_i − c_j‖² > r_i² + r_j².
  An opposite-direction pair is therefore ALWAYS farther from each other than
  either is from the norm (‖c_i − c_j‖ > max(r_i, r_j)). Contrapositive: if
  two people are mutually closer than either is to the group norm, their
  directions cannot be opposite; for r_i = r_j = r, mutual distance < r forces
  θ < 60°. **The feared case — "distance-close but direction-opposite" —
  exists only in the near-norm regime (both r small).**
- (c) **And exactly there, direction is unreadable.** Direction-estimate
  fidelity degrades as r/σ_noise → 0; two independent noise vectors in R^m
  have cos = O_p(m^{−1/2}) (spurious near-orthogonality); distances among
  near-norm people concentrate (spurious "everyone average looks alike"). The
  paradox dissolves into a power statement: **where distance and direction can
  disagree, neither is readable; where identity is readable, distance-close
  implies direction-close up to the explicit magnitude term in (a).**
- (d) **The licensed similarity estimator.** "Personality closeness" is
  **disattenuated distinctive shape similarity**:
  cos(ĉ_i, ĉ_j) computed on reproducible components (T6), on the invariant
  layer (T2), divided by √(ρ_i ρ_j) (attenuation correction). Magnitude match
  (r_i vs r_j) is a SEPARATE coordinate (individuation match), and readability
  (ρ_i, ρ_j) a third. Three coordinates, never folded into one distance.
- (e) **Identification consequence.** Misidentification is driven by ANGULAR
  crowding of the gallery near c_i's direction, not by raw-distance crowding.
  [→ K3]

## 4. Retrodiction table

| persisted measurement | value (precision as available) | speaks to |
|---|---|---|
| M4-F2 composition law | shared +0.0233905 vs free −0.0027728; paired +0.0261633 [0.019536, 0.032791], t=9.3351, 8 worlds (artifact precision) | T3(e); ownership split → K1 |
| M4-F4 author-axis law | γ=1.096 [0.984, 1.218]; holdout 0.4012 predicted / 0.3861 observed | T6 positive instance; the card's growth law |
| M4-F5 dissociation | agreement 0.0061→0.3861; long-window recovery plateau ≈0.15; same-occasion 0.1497→0.6371 | T4(a) |
| M4-F6 gauge B-invariance | 0.0297–0.0365 across B | T4 reader-mediated branch input |
| M4-F9 spread null | B8−B1 = −0.0163, CI [−0.0559, +0.0233] | T4 branch decision → K2 Part 0 |
| M4-H1 share invariance | identity proved; confirmed 2.22e-16 | T1(1), T2 |
| M4-H2–H4 basis materiality | 45.79% displacement reduction via normalization | T1's non-scalar U-freedom is material |
| M4-H6 S4 non-reproducibility | 0/3 worlds; knife-edge −0.0009 | T6 negative instance |
| F10 foundation gap | state/trait depends on occasion universe and horizon | T4 as typing |

## 5. Registered predictions (the K-line)

- **K1 (registered 2026-08-09, dispatched).** L1 designed card-space
  cancellation (0 decision flips across norm arms in shared design, ≤1e-9);
  L2 issuer error live and monotone in |P| in free design; L3 the 1/|P|
  variance law (manipulation check); L4 issuer-quality × design interaction
  (the penalty is free-design-specific); L5 the deployed relational gauge's
  issuer leakage is bounded: |Δ agreement| < 0.0065408 (= 0.25 × F2's
  composition effect) under calibrated pre-map common occasion shifts.
  Registration with leans, pivots, gates, MDE and aggregation rules:
  `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md`.
- **K2 (charter).** The card/biography gap law in h/τ_s at fixed budget;
  Part 0 reconciles T4 with F9/F6 at artifact precision and computes the
  T4-point-prediction for F9's exact parameters BEFORE any new run; decides
  T4-simple vs T4-reader-mediated.
- **K3 (charter).** The T7/T8 package: caricature (α) vs rotation (φ)
  dissociation; the anti-direction bound as a designed identity plus its
  violation rate in ESTIMATED cards as a pure noise function; disattenuated
  distinctive cosine recovers generator-true pattern similarity where raw
  distance fails (near-norm and unequal-norm regimes, sign-predictable);
  angular vs distance crowding; ρ_i predicts per-person identification.

## 6. What IDT answers to the origin conjecture

- **C-1 upheld, with the discriminator.** Identity is the reproducible
  component of deviation; the non-reproducing remainder is honest noise
  (measured instances on both sides: F4 vs H6).
- **C-2 converted into structure.** Unmeasurable at n=1 within one
  jurisdiction (F10); measurable across occasions at a lawful rate (the
  F4-type growth law); magnitude forever frame-bound (T1's trichotomy);
  pattern frame-stable on the invariant layer (T2).
- **C-3 sharpened.** Certificates have an issuer (P), a jurisdiction (O), and
  an expiry (h) — there is no issuer-free ID. Relative identity is issuer-free
  (T3); absolute identity is not. The readable card is state-inclusive (T4):
  it is a real certificate, occasion-stamped, and it is not a biography.
- **C-4 answered by T8.** "Same personality" = shape similarity of
  reproducible deviations after disattenuation, reported alongside — never
  merged with — magnitude match and readability. Raw distance alone is not a
  licensed similarity reading. The opposite-direction fear is confined by the
  anti-direction bound to the near-norm regime, where nothing is readable
  anyway.

## 7. Literature anchors (positioning only — citation pass PENDING)

Names and years are anchors for a future verified reference pass; no specific
claims are asserted from memory, per the program's no-invented-citations rule.
Error-reinterpretation lineage: Cronbach 1957; Cronbach & Gleser 1953;
generalizability theory 1972; Epstein 1979; Lacey & Lacey 1958; Fleeson 2001;
Molenaar 2004; Kenny & La Voie 1984. Behavioral signatures: Shoda, Mischel &
Wright 1994; Mischel & Shoda 1995. Norm-based coding: Valentine 1991; Leopold
et al. 2001; Rhodes & Jeffery 2006. Fingerprinting: Finn et al. 2015; Gratton
et al. 2018; Seitzman et al. 2019. Profile similarity (T8's ancestors):
Cronbach & Gleser 1953; Furr 2008 (normative vs distinctive similarity).
Behavioral biometrics: Mosteller & Wallace 1964; Koppel et al. 2009;
Stamatatos 2009; Doddington et al. 1998; Monrose & Rubin 2000; Narayanan et
al. 2012. Ecology's operational definition: Dingemanse & Dochtermann 2013;
Westneat, Wright & Dingemanse 2015; Cleasby, Nakagawa & Schielzeth 2015.
Sociolinguistics and social psychology: Weinreich, Labov & Herzog 1968; Le
Page & Tabouret-Keller 1985; Eckert 2012; Bucholtz & Hall 2005; Brewer 1991;
Turner et al. 1987 (meta-contrast); NLP: Wegmann et al. 2022; Rivera-Soto et
al. 2021; Pennebaker & King 1999.

## 8. Ethics note

If the residual is the identity, then content-scrubbing is not anonymization:
T6+T3 imply re-identification from deviation patterns that carry almost no
content. This binds to program governance: no per-person claims at this tier;
synthetic worlds only; the deanonymization consequence is to be treated in the
deferred defense phase, not exploited here.

## 9. Scope and tier

EXPLORATORY. Synthetic worlds calibrated to the real-text regime, through the
deployed frozen machinery. IDT licenses grammar — typing rules, design priors,
reader constructions, refusals — and no claim about any corpus, construct,
person, or diagnosis. The claims ledger controls.

---

## Dated appendix A (2026-08-09, planner derivation, same day as v1): T6′ — the discriminator has a split-scheme gauge, and that gauge is a measurement channel

T6 defines Id(i|F) as the occasion-resample-stable component of the deviation
field. Derivation: **which component is "stable" depends on the resampling
scheme**, because slow state is shared or separated by the split design:

- **Interleaved splits** (odd/even occasions): both halves sample the same
  state eras → s̄ is SHARED between halves → the "reproducible" component is
  b + s̄ (the occasion-bound card, state included).
- **Contiguous splits** (first half vs last half): state drift sits BETWEEN
  the halves → if the half-span exceeds τ_s, s̄ decorrelates across halves →
  the "reproducible" component approaches b alone.

So T6 as stated in v1 was under-specified: Id(i|F) requires a DECLARED split
scheme, and the scheme is part of the frame's expiry structure (h). This is
not a defect but a channel:

**T6′ (two-split state probe).** ρ_interleaved(i) − ρ_contiguous(i) is a
per-person, card-level, reader-free estimator of the state share of person
i's card at horizon h — the certificate's expiry date read off the difference
between two split designs. In-generator it is exactly predictable from the
same AR algebra as T4(b); on real designs it needs no access to the truth.

Consequence for K2: the leg becomes a TWO-CHANNEL discrimination with an
internal positive control (see plan-doc K2 charter refinement of this date).

## Dated appendix B (2026-08-09, planner derivation): F9 reconciliation — T4-simple is NOT tested by F9, and the branch stays open on purpose

Registered question: does F9's null (B8−B1 long-window = −0.01632278580727804,
CI [−0.05594321814077245, +0.02329764652621637], κ=0.5, gap=40, m_common=8,
AR(1) φ∈[0.2,0.8], authors ×16 — artifact precision, re-verified today)
falsify T4-simple, which predicts occasion spreading improves trait recovery?

Derivation (arithmetic verified before committing this note):

1. The arrangement manipulation is REAL at card level: Var(s̄)/σ_s² for one
   contiguous block of 8 is 0.17773 (φ=.2) / 0.31274 (φ=.5) / 0.60486 (φ=.8)
   vs 0.12500 for 8 gap-40 singletons — a 1.42×–4.84× reduction.
2. But the long-window baseline it acts on is tiny: r(B1) = 0.05963369493652382.
   Under the attenuation form r = σ_b/√(σ_b²+V), the predicted B8 gain is
   +0.0716 ONLY under the absurd bound (ALL card variance is state at φ=.8 —
   excluded by the generator's own weights, w_e=.70); +0.0116 under a generous
   half-state budget; **+0.0029 at the generator-plausible x-channel weight
   (w_x=.15)**. Every physically plausible prediction sits deep inside F9's CI
   (half-width 0.0396; power against +0.003–.012 is ~5–10%).

**Verdict: F9's pivot rightly closed the PANEL question (no affordable trait
axis via arrangement), but as a test of T4's mechanism it is structurally
uninformative — the arrangement lever is too weak at this state share, not
wrong.** T4-simple vs T4-reader-mediated remains open and moves to K2, whose
design must manipulate the state SHARE and persistence (α, τ_s), where
T4-simple's predicted swing can be made ≥3× the MDE — not the arrangement at
a fixed tiny share, where no affordable world count discriminates.

Two annotations, flagged as post-hoc readings of persisted numbers (they
become predictions only if K2 registers them fresh):

- F9 lean (b): same-occasion recovery DROPPED significantly under spread
  (−0.03173098873449674, CI [−0.05238696612924556, −0.01107501133974793]).
  T4(a)'s watermark reading fits the sign: at B1 the state era is coherent —
  the state-inclusive object is sharp and same-occasion recovery profits from
  it; at B8 the object averages 8 decorrelated eras and blurs. The state was
  subsidizing the same-occasion reading.
- F9's long-window row (0.0596, 0.0495, 0.0785, 0.0433 across B=1,2,4,8) is
  non-monotone at se≈0.01 — the signature of a floor plus noise, consistent
  with (not probative of) a reader-set floor.

## Dated appendix C (2026-08-09, after M4-K1): T3(f) decided AGAINST the idealization — the deployed gauge AMPLIFIES the frame; and T6 is forgeable without frame refreshment

M4-K1 executed (agent commit 10cea75; adjudication in the plan doc). What it
did to the theory:

**C.1 — What survived, at machine precision.** The card-space layer is fully
intact. T3(a–c): 0 rank-1 decision flips out of 31,520 probe cells across all
five norm arms (0 ties excluded), card-difference matrices invariant to
4.09e-16 / 4.14e-16 against a 1e-9 bar — with norms actually subtracted, no
algebraic shortcut. T3(e)'s issuer price on a deployable absolute reader is
large, lawful, and free-design-specific: oracle − est8 = +0.09695431472081219,
CI [0.08819796954314721, 0.10596763959390862], 8/8 worlds, 6.3× MDE; the
1/|P| law lands at slope −1.0865327686128703, CI [−1.0990, −1.0735]; the
design × issuer-quality interaction is +0.022461928934010153, CI
[0.011796, 0.032487], 7/8.

**C.2 — What died: T3(f).** Structural audit (G2) returned Branch B: the
deployed gauge consumes norm position directly (absolute means and quantiles,
quadratic lag products, tanh currents, a fixed D0 standardizer). And L5
MISSED with a POSITIVE sign: a pre-map common occasion shift — content no
card-space contrast can see — INCREASES the gauge's split-half agreement:
Δ = +0.015881141 at 0.5× (CI [0.003953, 0.027809]), **+0.092543049 at 1× (CI
[0.057781, 0.127306]) — 3.54× the entire F2 composition effect** — and
+0.549686516 at the 2× stress arm, while free designs are inert (|Δ| ≤
0.0045). The deployed relational gauge is not issuer-robust; it is
**issuer-amplifying**: shared-frame content is read as agreement. T5's price
table gains a line — the relational reader's price is not only gallery
composition but amplification of shared-frame content into apparent identity
consistency.

**C.3 — Annotation to §4's F2 retrodiction row (annotation, not rewrite).**
The ownership of F2's +0.026163263306726227 is now genuinely open: F2's
shared arms contain NATIVE common structure (w_mu = 0.15, the same scale
class as the author channel w_x = 0.15), and the gauge responds to a 1×
common shift with 3.54× the whole effect. Until M4-K1b decomposes it, the F2
row licenses only "composition changes what the gauge reads" — NOT
"composition improves author reading". The D3 design prior inherits this
caveat.

**C.4 — T6″ (frame-refreshed discriminator).** K1's disclosed by-product:
under the T3(c)-hypothesis reader in the free design, issuer sampling error
becomes a person-specific, occasion-half-REPRODUCIBLE component that IMPROVES
re-identification (est8 beats oracle: pooled −0.050127, CI [−0.056726,
−0.043782], 0/8 in the registered direction, monotone the wrong way) — **a
forged identity that passes T6's own discriminator**, manufactured by issuer
error interacting with person-specific occasion sampling. Patch, now part of
the theory and under test as K1b lean L-d: **Id(i|F) requires stability under
JOINT resampling of occasions AND frame** (the issuer re-estimated
independently per replicate). Reproducibility measured under a shared frame
is forgeable; reproducibility under frame refreshment is the licensed
discriminator.

**C.5 — Reader-design lemma (informal, from the same by-product).** A
split-half re-identification reader cannot simultaneously satisfy T3(c)'s
common-norm hypothesis and remove the occasion effect; the two constructions
are inequivalent instruments. Every constructed reader must declare which it
is (plan-doc standing rule 9). Input to K3.

## Dated appendix D (2026-08-09, after M4-K1b): the composition effect at κ=1.0 is frame-owned by construction; T9 (the forgery principle); T6″ v2

**D.1 — Frame ownership proved, not estimated.** K1b's registered surgery
turned out to be an identity at κ=1.0: removing the occasion-common structure
makes the shared and free designs the SAME panel — nothing else distinguishes
them — so Ŝ ≡ 1 exactly (CI width ~1e-16). The rule-9 second reading supplied
the live dissociation: deleting every trace of author identity DOUBLES the
composition contrast (Δ1′ = +0.04709060297774369 [0.042167, 0.052023],
32/32); the author-reading share of F2's κ=1.0 effect is
**−0.9487481378268351 [−1.1584, −0.7532]**; author deletion RAISES shared
agreement (+0.023006, 31/32); the free design reads zero with or without
authors. **At κ=1.0, composition's gain is entirely shared-frame content, and
author content is a net drag.** (Consistent with M4-F7's coefficient-0
finding, whose attribution consequence had never been propagated to F2's
headline.) The κ=0.5 knob — where the author channel is live — is K1c's
question, and no claim is made about it here.

**D.2 — T9, the forgery principle (two levels, one genus).** [MEASURED at
κ=1.0; live-knob form under test in K1c.] Frame content forges
identity-like statistics at both levels the theory cares about:

- *individual*: issuer error × person-specific sampling manufactures a
  person-stable, occasion-half-reproducible component that IMPROVES
  re-identification (appendix C.4; replicated at fresh seeds in K1b:
  +0.058756 [0.052284, 0.065355], 8/8) — a forged card;
- *collective*: shared occasions inject common content that the deployed
  gauge reads as agreement (the whole κ=1.0 composition effect) — a forged
  consensus.

Reproducibility and agreement statistics are frame-forgeable. The licensed
counter-operations are **frame refreshment** (individual level: the forgery
is destroyed and inverts into an honest issuer penalty, −0.062310
[−0.071069, −0.054188], 0/8) and **frame removal/contrast** (collective
level: K1b's surgery). A statistic that has passed neither operation may not
be read as identity content.

**D.3 — T6″ v2 (sign form).** The v1 operationalization (zero-equivalence
band after refreshment) was a planner rule-4 violation: under refreshment the
expected value is NOT zero but the honest issuer-noise penalty. Correct form:
**under frame refreshment, no reader may PROFIT from frame error** —
est-frame minus oracle must be ≤ 0 within tolerance; a positive advantage
under refreshed frames is the forgery signature. The measured inversion
(−0.0623) with oracle stability 0.00254 vindicates the direction and the
do-no-harm clause. Confirmatory lean at the live knob rides K1c (L-e″).

**D.4 — The de-framing repair (certified, unadopted).** Per-occasion
ESTIMATED mean subtraction pre-map removes **94.389% [90.233, 98.791]** of
what oracle common-structure removal removes (K1b L-e HOLD, 32/32 on both
removals). Realizable outside synthetic worlds; UNADOPTED under F16
discipline (changing the frozen gauge is a new operator with its own study
ID); queues beside `colstd_alpha_0.10`.

**D.5 — §4 F2 row, second annotation.** The κ=1.0 attribution is CLOSED
(frame-owned, proved by construction and by live author-deletion). The κ=0.5
attribution is OPEN → K1c. Retrospective dated notes with this scope were
appended today to the M4-F panel synthesis and the displacement-resolution
document under P2b's registered consequence.

## Dated appendix E (2026-08-09, after M4-K1c's Part-0 stop): the world-family lemma — composition in F2's family is common-channel-carried at EVERY κ, and the person×occasion channel does not exist there

M4-K1c never ran its arms: its rule-10 gate proved the planner's registered
frame-share decomposition degenerate at EVERY κ, not only at κ=1.0, and
stopped the leg in 74 seconds with zero adjudicated worlds (P4c).

**E.1 — The lemma (source-proved, empirically exact).** In F2's
`generate_world_composed`: the design (`occasion_mode`) has exactly one
consumer, `occasion_labels → shock_x` — the `common_part`. The `mean_part`,
`ar_part` and `noise_part` are drawn before the design enters and are
design-invariant; `state_part` is linear in the blend, so
**response − common_part is design-invariant for every κ ∈ (0,1]**
(empirically: shared-vs-free gaps of the other three channels exactly 0.0;
post-removal panels equal at 3.3e-16; through the deployed gauge |Δ1| ≤
7.81e-17 across all pilot worlds). Consequences: (i) Ŝ_frame ≡ 1 at every κ
is a fact about the WORLD, not a gauge measurement — K1b's κ=1.0 attribution
was correct but too narrow; (ii) exact common-removal is a design-collapsing
operation in this family at any κ (standing rules 10 and 12 exist because
two planner registrations in a row missed this).

**E.2 — What this does to IDT's A1.** F2's family instantiates s(i,o) only
in its degenerate corner: s(i,o) = common(o) + AR_i(t). There is **no
person×occasion interaction channel**. The jurisdiction-alignment question —
"does shared-occasion design align PERSON-SPECIFIC state content?" — is
therefore UNTESTABLE in this family: not falsified, not supported —
inexpressible. T3(e)'s two free-design penalties collapse into one there.
(This is also why the panel line's laws should be re-read as laws of a
family without if-then signatures: the world cannot represent the very
object Shoda-style behavioral signatures are about.)

**E.3 — Consequences downstream.** (a) K2 gains a fifth design requirement:
introduce a person×occasion interaction channel (`w_int`) so state share,
alignment, and the two-split probe act on a world that can express them.
(b) The only live ownership question inside the existing family is Ŝ_auth
(author-deletion), which is NOT degenerate (A5-vs-A6 panel gap
0.3310376783451957 — exactly the design gap) — registered as M4-K1c′.
(c) K1c's report-only κ facts: F4's adjudicated claims are κ=1.0-only by its
own record; F5 carries a HELD κ-stability lean. The F4/F5 re-reading remains
queued as its own registration; this appendix does not annotate them.

**E.4 — Method note.** Rule 10's gate converted a wrong registration into a
74-second stop — the first time a standing rule caught the planner before
compute was spent. Rule 12 (source-object naming for channels and
manipulations) was added after two same-family naming defects.

## Dated appendix F (2026-08-09, after M4-K1c′): the negative author share is κ-invariant; author content is interference; the repair is knob-dependent

**F.1 — The share.** At the live knob (κ=0.5; author channels CERTIFIED live:
AR intact/zeroed ratio ~1.08, author-mean ratio ~2.86), with the composition
effect itself replicating INSIDE F2's own CI (Δ0 = 0.007448566560020627
[0.006338, 0.008586] vs F2's [0.004418, 0.013254]):
**Ŝ_auth = −0.9443843417103447 [−1.2340432099315712, −0.7045965411263232]**
— the same number to three decimals as K1b's −0.949 at κ=1.0. Deleting every
trace of author identity nearly doubles the composition contrast
(Δ0′/Δ0 = 1.944; Δ0′ positive in 127/128 worlds). The negative share is not
a κ=1.0 artefact.

**F.2 — Author content is interference, decomposed.** The exact identity
(Δ0 − Δ0′) = −[(A5−A0) + (A2−A6)] (verified at 3.5e-18) splits the effect:
deleting authors RAISES shared-design agreement (A5−A0 = +0.004338666343079094,
92/128) and LOWERS free-design agreement (A6−A2 = −0.0026956432843916727,
90/128). In both designs author content interferes with the gauge's frame
reading rather than feeding it. Note also the panel-level fact: at this knob
(A5−A6) ≡ (A0−A2) AS PANELS — the deletion subtracts a design-invariant
object — so the entire Ŝ_auth story is GAUGE-level, exactly where T9 says
forgery lives.

**F.3 — T9 status: measured at both knobs.** Individual forgery at κ=0.5:
+0.0547 (8/8) under a shared frame → **−0.0867 (0/8)** under frame
refreshment (a larger inversion than κ=1.0's −0.0623), oracle stable at
0.0019. T6″ v2 (sign form) HOLDS at both knobs.

**F.4 — The de-framing repair is knob-dependent.** R_est/R_or =
**0.7347 [0.6376, 0.8207] at κ=0.5** vs **0.9439 [0.9023, 0.9879] at κ=1.0**
— non-overlapping. Deployment caveat recorded on the certified-unadopted
repair: its removal fraction is regime-dependent and must be re-measured in
any target regime before an adoption decision.

**F.5 — What remains of "composition", and the next question.** The
phenomenon is real (replicates inside F2's CI), frame-owned at every tested
knob, with author content as interference. The surviving design content of
"recruit authors, not words" is now a single question: does M4-F4's scaling
exponent (γ = 1.096) survive author deletion? If yes, the author axis is a
REPLICATE axis (frame-readout economics — more noise-bodies averaging the
same frame); if no, scaling and composition ownership dissociate. Registered
as M4-K1d before run.

## Dated appendix G (2026-08-09, after M4-K1d): the author axis is a replicate axis; interference extends from level to slope

**G.1 — The result.** At F4's own knob (κ=1.0, shared), fresh seeds, F4's own
fitter: the law replicates strongly (γ_intact = 1.1187 [0.9810, 1.2376] —
the fresh CI CONTAINS F4's whole band), and **survives total deletion of the
author channel**: γ_deleted = 1.2446 [1.1185, 1.3579], overlapping F4's band
under every reading. Δγ = +0.1259 [0.0169, 0.2483] — inside the registered
±0.25 immateriality band, **boundary-seated** (registered B=2000 reading
holds by 0.0017; a 100000-draw reading lands outside by 0.0017; the positive
SIGN is robust at 10/10 seeds). L-1 HOLD under its registration; every
consequence carries the boundary status; standing rule 13 (Monte-Carlo
verdict stability) was created from this.

**G.2 — Interference, now at the slope.** Deleting the authors RAISES the
level at every scale (40/40 world-points; +0.0120 at ×1 growing to +0.2095
at ×16), steepens the exponent, predicts BETTER out-of-sample on F4's own
×32 protocol (holdout gap 0.0490 deleted vs 0.0807 intact), and **more than
halves the half-agreement budget (48.865× → 19.878× authors)**. The axis
named after authors is cheaper and cleaner without them. With K1b/K1c′ this
completes the arc: author content is interference to the deployed gauge's
frame reading at the composition LEVEL and at the scaling SLOPE. **The
"author axis" is a replicate axis: frame-readout economics, where any
noise-bodies averaging the same frame would serve.** The D3 prior re-types:
recruit replicates, not words.

**G.3 — F5's truth objects are mixed (source-derived fact, K1d G-info-F5).**
`truth_recovery_exact/long` in F5 are field agreements against noise-free
mixtures: at κ=1.0 exactly **½ author-mean + ½ occasion-common**; at κ=0.5
**¾ author (½ mean + ¼ AR) + ¼ common** (noise, 70% of response variance,
excluded). Every F5 "truth recovery" number is recovery of that mixture, not
of a trait. Recorded so no reader mistakes it; any re-adjudication of F5's
rows would be its own registered leg. This composition table is also a
required input to K2b's T4-branch reading.

**G.4 — Method.** Defects #16 (a gate unmeasurable at its registered
position) and #17 (a pivot space with a gap exactly where the measurement
landed) recorded; rule 13 added; the legacy-parser naming convention added
for pre-round-trip artifacts.

**G.5 — What the K-line still owes.** K2a (instrument: expressive world with
slow state + person×occasion channel; two-split probe validated against
designed identities — registered, dispatched), then K2b (the T4 branch:
simple vs reader-mediated, on the validated instrument), then K3 (similarity
geometry, T7/T8), then the line synthesis.

## Dated appendix H (2026-08-09, after M4-K2a): the instrument holds — T6′ and the attenuation algebra are now measured objects

M4-K2a validated the expressive world and both card-level instruments
against Part-0 point predictions computed before any arm (10.9 s of
compute, card-space only):

- **T6′ (two-split probe) is real and quantitative:** measured
  ρ_interleaved − ρ_contiguous contained the algebraic prediction in 11/12
  cells and matched the predicted ORDERING exactly — including its
  non-monotonicity in φ_slow and an arm-dependent rank swap. The probe
  reads τ_s.
- **Appendix B's attenuation formula is exact in practice:** 12/12 cells,
  max relative error 0.30%, against r = σ_b/√(σ_b² + Var(s̄_slow) +
  Var(s̄_int) + σ_e²/n_eff) with the exact AR sum.
- **The person×occasion channel is typed correctly:** its contribution to
  contiguous-split reproducibility is 0 within margins (6/6, TOST, even at
  the strictest submargin) while its same-occasion signature is present and
  matches the predicted magnitude (6/6) — the family can now express the
  content appendix E showed it lacked.
- **Rule 13's first application:** six boundary-near clauses triggered the
  ≥10×B stability check; all STABLE; zero BOUNDARY.
- **Estimator lesson (binding rider on K2b):** read the GAP, not either
  split half — the authors-within-world bootstrap conditions on realized
  occasion shocks and under-covers half-level predictions (8/12), while GAP
  and attenuation quantities are immune.

Status change: T6′ and the attenuation algebra move from [PROVED in card
space] to **[MEASURED]**. K2b (the T4 branch) is registered and dispatched
on this instrument.

## Dated appendix I (2026-08-09, after M4-K2b): the T4 branch returns PARTIAL — and a third form is named

**I.1 — The verdict.** On the validated instrument, with the positive
control EXACT (6/6 + 6/6 containment; both card orderings exactly as
predicted, and different from each other — the card resolves the φ effect),
the deployed gauge's b-only trait recovery does NEITHER registered thing:
it does not track card algebra proportionally (L-B MISS: Spearman 0.943
with one non-significant inversion, p = .0083 > .005; S/P = 0.381 outside
[0.5, 2]) and it is not floored (L-C MISS on the point clause by 1.5–1.7
se). **PARTIAL fires — both mechanisms live.** T4 stays [OPEN].

**I.2 — The discovery: over-response.** Field recovery falls **−57.6%**
across the design while card algebra prescribes **−32.5%**; against an
arm-independent efficiency λ = 0.1742, S/(λP) = **2.19**. The reader loses
the trait FASTER than the card does — qualitatively the interference
account's prediction (appendices F/G) appearing on the state axis. Named as
the third candidate form: **T4-reader-amplified**. Also L-D HOLD: the gauge
recovers the MIXTURE better than the trait in 6/6 arms (2.7× at the highest
state share) — the frame-preference again.

**I.3 — The method lesson (rule 14).** The registration compared card
attenuation to field agreement without pinning the LINK between their
scales, and the branch verdict is link-sensitive (identity link → PARTIAL;
squared link → MEDIATED). Scored on the pre-declared primary; defect #20;
**rule 14**: cross-scale leans pin their link, or are redesigned
within-instrument. K2c is the within-instrument design: matched-attenuation
pairs — same predicted card attenuation, different state composition; any
within-pair field difference is composition-sensitivity, measured
field-vs-field, no link anywhere.

**I.4 — What K2c decides.** L-1: field is a function of attenuation alone →
**T4-simple-with-link** (over-response = link curvature; appendix G's slope
claim would be REVISED accordingly). L-2: composition-sensitivity at fixed
attenuation → **T4-reader-mediated (composition form)**, and the
constructive repair test (does de-framing raise trait recovery?) follows.
Registered before run with a partitioned space and equivalence margins.

## Dated appendix J (2026-08-09, after M4-K2c): the strict function form is dead, the link is quadratic, and the composition term is real but small — so far

**J.1 — Composition-sensitivity is real; the strict function form is
falsified.** With within-pair predicted attenuation matched to 1e-16 and
measured matches 23×–143× inside the gate, the field still differs:
unanimous sign across three pairs, 2/3 significant at n=32, monotone in
state content (|D| = 2.08% / 9.65% / 15.23% of level; the more-share /
less-persistent arm reads the person worse). The field is NOT a function of
card attenuation alone.

**J.2 — But sub-material at the registered margin** (all |D| CIs inside
±0.020) over attenuation 0.56–0.78 — with the record keeping the honest
clause: the MARGIN, not the physics, kept the function form's equivalence
alive (closest case by 0.533 se). The registered space turned out not to be
a partition (significant-but-sub-material satisfied both leans; scored as a
named non-registered outcome under a pre-declared rule; T4 not re-typed).
Defect #21; standing rule 15 (enumeration-verified partitions) created.

**J.3 — The link is measured: q = 1.9338 [1.7337, 2.1933], R² 0.958 over
13 arms.** The K2b over-response is approximately QUADRATIC — the reader
loses the trait like the square of the card's attenuation. This
retroactively explains K2b's link-sensitivity: the squared reading was
close to the truth. Emerging named form (hypothesis, not adjudicated):
**field ≈ λ·r_card^q − c(state composition)**, q ≈ 2, c > 0 growing with
state content, carrier unresolved (iso-attenuation pairs in (share, φ)
move both together).

**J.4 — The trade.** At matched attenuation, the mixture channel moves
OPPOSITE and 4.3× larger (all CIs excluding 0): what the reader gains on
the mixture it loses on the trait — T9's frame-preference, now visible as
a within-pair exchange rate.

**J.5 — K2d (registered).** Frontier: does c() cross materiality at
attenuation ≈ 0.45? Carrier: species pairs trading slow-AR against the
K2a-validated interaction channel at matched attenuation and fixed φ —
species-general vs species-specific, with the sign itself a finding. Dual
margins (0.020 continuity; 0.010 = the observed effect scale, so
sub-material can no longer hide effects of the size already seen);
rule-15 enumeration as the adjudication space. Either closure re-types T4;
the constructive repair question follows the ownership.

## Dated appendix K (2026-08-09, after M4-K2d): the composition term peaks; the species term is material; one coefficient explains everything so far

**K.1 — The (share, φ) composition axis is bounded by its own peak.** At
attenuation 0.45 the term is SUB-SIG(−) (−0.0099 [−0.0154, −0.0046]): the
relative effect kept growing (2.08 → 9.65 → 15.23 → 15.94% of level) but
the level collapsed faster — the ABSOLUTE term peaked near r ≈ 0.56 and
fell 27% by the frontier. This axis never crosses materiality anywhere on
the tested curve, and not because of margin generosity.

**K.2 — The material term is the SPECIES.** At matched attenuation AND
matched φ, replacing persistent author-state with occasion-bound
interaction content costs 2.0–2.5× more trait recovery: SP-68
+0.0304 [+0.0235, +0.0369], SP-56 +0.0271 [+0.0203, +0.0338] — both
MAT-SIG(+) under both margins; the first MATERIAL composition finding of
the series. Gloss (flagged as gloss): occasion-KEYED person content looks
like frame to a frame-preferring reader — it is read into the mixture and
subtracted from the person; T9's grammar, now with a price tag.

**K.3 — The unifying candidate.** One coefficient fits all six K2c+K2d
pairs, including the sign reversal: **D ≈ −0.722 × Δ(total non-trait
person variance)**, R² 0.9935, max residual 0.0025. Candidate law:
**field ≈ λ·r_card^q − κ·V_person** — the reader taxes RAW person
variance, species-blind; K2d's species result would then be ΔV in
disguise. K2d cannot separate them (species and ΔV confounded); K2e's
double-matched pairs (attenuation AND V_person matched, species free) are
the link-free discriminator, with the −0.722 slope promoted to a
registered quantitative prediction on a fresh pair. Under H-VAR the T4
closure would read: **T4-reader-amplified-variance** — the reader loses
the trait like r^q and pays a further tax proportional to total person
state, whatever its species.

**K.4 — Method.** Rule 15 held at the cell level and caught its own
registration one level up (lean predicates and pivot routing
unpartitioned — defect #22 → rule 16: the enumeration covers the FULL
adjudication object). Pilot convention tightened (≥4 worlds or df
inflation — K2d's 2-world pilots underestimated realized sd by up to
7.8×, disclosed, inconsequential there). Instrument boundary recorded:
K2a's two-split GAP predictions are validated only to equal-share w_int;
attenuation predictions held at 0.278% max error even beyond it.

## Dated appendix L (2026-08-09, after M4-K2e): T4 CLOSES — the reader-borne composite form

**L.1 — Double matching decides.** With BOTH predicted attenuation and
total person variance matched to ≤1e-16 (measured: attenuation 6–9×,
V_person 54–85× inside their gates), K2d's "material species effect"
collapses by **67.04–78.83%** — it was ΔV_person in disguise. The variance
law was simultaneously confirmed OUT-OF-SAMPLE on a fresh pure-φ pair:
predicted D = −0.0124, measured −0.0106 [−0.0152, −0.0057], error 0.0019
(both registered clauses). What survives of the species term: SUB-SIG(+)
in both DM pairs (+0.0064 [+0.0007, +0.0121]; +0.0089 [+0.0024, +0.0153])
— genuine, sign-consistent, but sub-material at both margins and below its
own realized MDE (0.74×, 0.95×): replication-fragile.

**L.2 — T4: [OPEN] → [CLOSED, composite reader-borne form].**

    field ≈ λ · r_card^q − κ · V_person − ε_species(occasion-bound)

λ ≈ 0.174; **q = 1.83 [1.71, 1.98]** (the reader loses the trait like the
square of card attenuation); **κ ≈ 0.72** (the reader taxes raw
person-state variance, species-blind, beyond card algebra — quantitatively
predicted and confirmed); **ε_species** bounded ≤ 0.0153 (CI upper) at
these dims, fragile. The card/biography gap is **reader-borne in
substance**: T4-simple survives only as the r-dependence inside a
quadratic link; the flat floor is dead; **the F5 plateau re-attributes to
the reader's own transformations, not to the card's information content.**
Scope as always: this closes the branch for THE DEPLOYED READER on this
world family, EXPLORATORY tier — it is a law about the instrument-world
pair, not about persons.

**L.3 — Method.** Defects #23 (routing consequence written at MAT grade,
fired at SUB grade — executed graded per rule 7) and #24 (a false
conservative premise about the instrument's validated range — rule-8
family) recorded. The 4-world pilot is now a standing convention.

**L.4 — What remains of IDT v1's program.** K3 (T7/T8 similarity geometry
— the empirical stamp on the origin question C-4) is registered and
dispatched; on P4 (all leans hold) the theory's registered empirical
program is COMPLETE and the next planner actions are the line synthesis
and IDT v1.1 consolidation, then K-R1 (the constructive repair test:
does de-framing move λ, κ, or trait recovery — T9's counter-operations
tested constructively).

## Dated appendix M (2026-08-09, after M4-K3): v1.1 consolidation — the theory as measured

K3 returned P3 (QUALIFIED): the registered empirical program of IDT v1 is
COMPLETE. The theorem status table, controlling as of this date:

| object | status | anchor measurements |
|---|---|---|
| T1 gauge trichotomy | PROVED | H1 import; K1's three channels each live |
| T2 invariant layer | PROVED + MEASURED | cancellation at 4.1e-16, 0/31,520 flips (K1) |
| T3(a–e) issuer theorems | PROVED + MEASURED | issuer price +0.0970 (6.3×MDE); 1/|P| slope −1.0865; free-design specificity +0.0225 (K1) |
| T3(f) deployed-gauge immunity | **DECIDED AGAINST** | the gauge AMPLIFIES common shifts: +0.0925 at 1× = 3.54× F2's effect (K1) |
| T4 card ≠ biography | **CLOSED, composite reader-borne** | field ≈ λ·r^q − κ·V_person − ε_species; q = 1.83 [1.71, 1.98]; κ ≈ 0.72 confirmed out-of-sample; ε ≤ 0.015 fragile (K2b–K2e); F5 plateau re-attributed to the reader |
| T5 no anchor-free reading | PRICED (C-NFI still conjecture) | absolute: issuer error; relational: composition + amplification (K1, K1b) |
| T6 discriminator | PATCHED TWICE, both patches MEASURED | T6′ split-scheme probe (11/12 + exact ordering, K2a); T6″ v2 frame refreshment (forgery +0.055/+0.059 → inversion −0.062/−0.087 at both knobs) |
| T7 direction reads | **MEASURED** | caricature +0.265/+0.299; rotation cos-law to ≤0.0035 error; rotation > scaling harm, CIs exclude 0 (K3) |
| T8(a) decomposition | PROVED; magnitude channel tiny in this family | 1–3% of squared distance (instrument boundary) |
| T8(b) anti-direction bound | **MEASURED EXACT** | 0 violations / 3,139,584 true-card pairs; BINDS at 50.48%; noise law 6/6 (K3) |
| T8(c) near-norm unreadability | SUPPORTED | via the validated noise law (K3 L-1) |
| T8(d) licensed similarity estimator | **MEASURED** | wins 12/12 strata; MATERIAL (ΔSpearman ≥ 0.106) in both predicted failure regimes 6/6; in ρ-homogeneous worlds the margin is the ANGLE, disattenuation neutral (K3) |
| T8(e) angular crowding | **FALSIFIED here, REPLACED** | angular crowding at CHANCE (AUC 0.5005); the driver is the probe's own readability (AUC 0.664) — menagerie, not twins (K3 L-4/L-5) |
| T9 forgery principle | MEASURED at both knobs | individual + collective forgeries and both counter-operations (K1–K2e) |

Answers to the origin conjecture, final form for v1: **C-1** upheld with
the discriminator — and the discriminator itself needed two frame patches
(reproducibility without frame refreshment is forgeable). **C-2** a
theorem (three gauges), not an obstacle. **C-3** exact: certificates have
issuer, jurisdiction, expiry — and the certificate-reader itself is now
priced (quadratic loss + variance tax). **C-4** measured: personality
closeness is direction on the invariant layer, read after reproducibility
and reliability corrections; the feared distance/direction divergence is
confined to the near-norm regime by an exact bound that BINDS in half of
all pairs; and one estimator lesson beyond the conjecture — who gets
misread is set by their own readability, not by their neighbors, in
sparse galleries.

Method ledger for the line: standing rules 9–17 created, each paid for by
a recorded planner defect (#9–#26); the 4-world pilot, round-trip
parsing, Part-0 verification of bit-identity claims, and chunked-stage
conventions adopted. Companion synthesis:
`docs/SUICA_M4_K_IDENTITY_LINE_SYNTHESIS.md`. Scope unchanged:
EXPLORATORY, synthetic, instrument-world laws — no claims about persons.

## Dated appendix N (2026-08-09, after M4-K-R1): the scaffold corollary — de-framing is diagnostic, never preprocessing

K-R1 asked whether the certified de-framing repair improves the reader as
a trait instrument. **It does the opposite, maximally:** b-only recovery
collapses to zero in all six state arms (d_a from −0.077 to −0.183, 0/32
worlds positive anywhere, 6.3–12.3× realized MDE; λ falls 0.1821 →
0.0008). The planner's prior on this branch was .10 — recorded, not
excused.

**N.1 — The scaffold corollary (T9 refined).** In this family the trait
has no frame-free expression in the field: the b-only truth's only
within-author occasion variation IS the frame (strict trait-only fields
are degenerate, context norms ~7e-4). The reader reads the person THROUGH
the person×frame interaction. Therefore frame REMOVAL destroys forged and
legitimate reading together — bleach the paper and the watermark goes with
the forgery. T9's counter-operations are re-licensed: **frame refreshment
and frame CONTRAST are diagnostic operations; frame removal as
preprocessing is prohibited wherever person content lacks frame-free
expression.** (The certified de-framing repair keeps its composition-
deflation certificate and gains this caution.)

**N.2 — Instrument-role typing (T5's table, closing line).** As a TRAIT
instrument at these regimes the plain card reader dominates the deployed
relation-field gauge by ~4.5× (card attenuation 0.827 vs field recovery
0.178 at the lowest state share). The gauge is an occasion-bound-object
instrument — the F-line's wall, now with its mechanism. Reader licensing:
trait questions → card-family readers with frame-refreshed discriminators
(T6″); occasion-bound-object questions → the relational gauge; never the
converse.

## Dated appendix O (2026-08-09): T10 — the anchor impossibility theorem (C-NFI proved, global form)

T5's conjecture C-NFI is now a theorem in its global form.

**T10 (anchor impossibility).** Let a reader assign to a single probe's
card c ∈ R^m an identity reading Φ(c) (any measurable functional), and
require Φ invariant under (i) arbitrary common translations of card space
(the closure of issuer freedom — realized adversarially by biased issuers,
K1's biased32 channel), and (ii) positive scalar coordinate changes. Then
Φ is constant: translation-invariance alone forces Φ(c) = Φ(c − c) = Φ(0)
for every c. A constant reading carries no identity information.
Consequently every informative reader either (a) consumes an issuer
estimate — paying issuer-sampling error, measured at +0.0970 (6.3×MDE)
with the 1/|P| law at slope −1.0865 (K1) — or (b) reads multi-person
structure, i.e., the centered configuration, which is invariant to common
translations but depends by construction on WHO is co-present — paying
gallery composition — or (c) anchors in fixed coordinates, paying basis
dependence (the M4-H territory, 45.79% materiality). **There is no
anchor-free reading; the three prices are exhaustive at the level of what
a reading may consume.**

Local form (stated, not proved): under sampling issuers (error
O(σ/√|P|)) rather than adversarial ones, the impossibility becomes an
information bound — identity information through the absolute channel is
capped by issuer precision; K1's L2/L3 measurements are this bound's
empirical shadow. The local constant is not derived here.

Status: T5 upgrades from PRICED (C-NFI conjecture) to **PRICED + T10
PROVED (global)**. The certificate metaphor closes exactly: there is no
ID without an issuer, no line-up without a gallery, no reading without
coordinates — only the choice of which price to pay, and the prices are
now measured.

## Dated appendix P (2026-08-09, evening): IDT-R — the reverse reading. Typology, identity removal, and what "error = 0" asserts

Origin (program owner, same date): *the old hypothesis — assuming error = 0
is assuming there is no identity; conversely, if identity were REMOVED,
would correct personality GROUPING become possible? Can this be proven?*

**P.1 — The figure-ground inversion.** Extend A1 with a TYPE layer:

    x(i,o) = μ(o) + τ_{g(i)} + b_i + s(i,o) + ε(i,o)

where g(i) ∈ {1..G} is a latent group, τ_g the type vector (shared within
a group), and b_i the WITHIN-TYPE individual identity (deviation from
one's own type centroid). The K-line read b as the signal and everything
shared as frame; the reverse reading takes τ as the signal and b as
interference. This is the **complementarity principle**, third
instantiation: every layer (frame / type / identity / state / noise) is
signal for exactly one question and interference for the others; a reader
must declare its target layer, and suppression operations are only valid
for the structure they exploit (averaging kills ε; frame refreshment
kills s and issuer forgeries; cross-person pooling reveals τ; and b has
NO intrinsic suppression operation — which is exactly why typology is
hard in identity-bearing worlds, and why identity was the hard signal in
the K-line).

**P.2 — Theorem R1 (circularity, and its resolution). [PROVED]**
"Remove identity, then group" is circular as stated: b_i is DEFINED as
c_i − τ_{g(i)}, so removing it requires knowing g — the very output of
grouping. Made algorithmic, the proposal is exactly alternating
minimization: (given groups, estimate identities as residuals and remove
them) ⇄ (given identity-removed cards — the centroids — re-group). This
is Lloyd's algorithm / EM for a mixture. Consequently: (i) the
procedure's fixed points are the local optima of the joint
type+assignment objective — the conjecture cannot be proven as an
unconditional algorithm, because its algorithmic form inherits
clustering's local-optimum structure; (ii) it IS provably correct in the
separation regime of R2. The owner's proposal, formalized, is the E-step
read as an identity operation — and that identification is itself the
first result.

**P.3 — Theorem R2 (the geometry dichotomy — when identity removal is
possible without knowing groups). [PROVED, sketch]** Let cards be
c_i = τ_{g(i)} + b_i + η_i with types supported in a k_τ-dimensional
subspace S of R^m, minimum centroid separation Δ.

- **ISO case** (identity isotropic: energy σ_b² spread over all m
  dimensions): distance-based grouping suffers the FULL identity energy
  (within-type squared distances inflate by ~2σ_b²), but projection onto
  S (estimable from the top of the pooled spectrum without group labels)
  retains only ~(k_τ/m)·σ_b² of it — an **SNR improvement of order
  m/k_τ**, and grouping is consistent whenever Δ² ≳ (k_τ/m)σ_b² + noise.
  Here the conjecture is TRUE and quantified: identity CAN be suppressed
  before grouping, because it lives off the type axes.
- **ALIGNED case** (identity supported IN S — people differ along the
  same axes that distinguish types): projection removes nothing;
  b displaces persons across type boundaries irreducibly, and grouping
  error has a FLOOR ≈ Φ(−Δ/(2σ_{b,u})) per boundary (σ_{b,u} the
  identity sd along the boundary normal). Here the conjecture is FALSE
  in principle: "removing identity" would remove position in trait space
  itself — the types are discretizations of the very continuum identity
  lives on.

**The dichotomy is the honest answer to "can it be proven": the
conjecture is provable exactly when identity is geometrically off-axis
from type structure — and whether it is, in any given world, is an
empirical taxometric fact, not a theorem.** (This is the classical
types-vs-dimensions question — Meehl's taxometrics — restated as a
subspace geometry condition inside IDT.)

**P.4 — Theorem R3 (what "error = 0" asserts, and the completeness
audit). [PROVED as definition-consequence]** The zero-error/typological
assumption asserts b ≡ 0 and s ≡ 0 within types: all members of a type
are exchangeable. IDT makes this FALSIFIABLE with instruments we already
validated: within-type deviations must carry NO frame-refreshed,
occasion-reproducible component (T6″). Hence:

- **Audit criterion:** a typology's *completeness defect* := the
  surviving-identity share of its within-group deviations (measured by
  the T6″ discriminator). Zero ⟺ the typology's own error-free claim
  holds on that population.
- **Impossibility half:** in an identity-bearing world (σ_b > 0), EVERY
  typology has completeness defect ≥ the b-share — typological
  completeness is impossible there, and its failure is a measurable
  number, not a philosophical complaint.
- **Distinction kept:** partition-CORRECTNESS (groups match g) and
  completeness (no surviving identity) are different properties; correct
  partitions still fail the completeness audit whenever b > 0. The
  owner's 誤差=0 hypothesis is thereby converted from an assumption into
  a STOPPING RULE and audit meter for any grouping method.

**P.5 — R4 (the identity tax on grouping — registered for measurement).**
The K-line measured identity content taxing FRAME reading (negative
author share) and person-variance taxing TRAIT reading (κ ≈ 0.72). The
reverse reading predicts the third tax: grouping accuracy (ARI) declines
in identity share at fixed Δ along an R2-geometry curve, with oracle
identity removal restoring it in ISO worlds and NOT in ALIGNED worlds.
This, the audit calibration, and the dichotomy's floor are the M4-L
line's instrument leg (L1), registered before run in
`docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md`.

**P.6 — Literature anchors (positioning only, citation pass PENDING).**
Taxometrics and the types-vs-dimensions debate: Meehl 1992, 1995;
personality-type literature (resilient/over-/under-controlled types:
Asendorpf; Specht et al.; Herzberg & Roth); mixture separation and
provable clustering (model-based clustering: Fraley & Raftery; separation
conditions for Gaussian mixtures and spectral methods: Achlioptas &
McSherry, Vempala & Wang); EM/Lloyd fixed-point structure. No specific
claims asserted from memory.

Scope unchanged: EXPLORATORY, synthetic, instrument-world claims only.

## Dated appendix Q (2026-08-10, after M4-L1 — the theory-repair note P2L demands): the floor is projection-invariant; the dichotomy relocates; the conjecture reaches its final sharpened form

M4-L1 held the ordinal geometry perfectly (the 10-cell predicted ordering
reproduced cell for cell; the ρ.35 floor contained; the tax ratio 8.15×)
and failed two shadows. Both failures are now understood, and one is a
theorem.

**Q.1 — Floor-invariance lemma. [PROVED]** For any boundary normal
u ∈ S, projection onto S leaves the identity component along u unchanged:
⟨P_S b, u⟩ = ⟨b, u⟩. Hence **no projection can reduce Bayes assignment
error — in ANY geometry.** Measured shadow: oracle-S projection restored
13.5% [−2.6, 27.7] of the ISO deficit at ρ.55 and 15.0% at ρ.75 — flat,
exactly as the lemma demands; the small restoration is centroid-noise
reduction, not floor change.

**Q.2 — The dichotomy relocates.** ISO and ALIGNED differ by the
boundary-normal variance ratio σ²_{u,ALIGNED}/σ²_{u,ISO} = m/k_τ
(z-ratio √(m/k_τ) = 4 at 48/3 — matching L1's Δ-free boundary algebra;
measured ARI-drop ratio 8.145911689523754 at matched identity energy).
**P.3's m/k_τ factor is real; it lives in the FLOOR RATIO between
geometries, not in what projection can buy.**

**Q.3 — R2's ISO half, restated.** Projection's genuine purchase is
centroid LOCALIZATION: below the consistency threshold — where ambient
clustering cannot find the structure at all — the (k_τ/m)-fold energy
reduction lets spiked-PCA + clustering still find it. Above threshold it
buys ~nothing (Q.1). P.3's energy algebra was correct arithmetic attached
to the wrong observable (defect #30 → standing rule 19). The restated
claim is testable only in the ambient-failure regime: M4-L2's W-1.

**Q.4 — The owner's conjecture, final sharpened form.** TRUE identity
removal works trivially (measured: ARI → 0.9948 in both geometries) but
requires knowing b — the R1 circularity. The only label-free surrogate,
projection, provably cannot touch the boundary-normal component (Q.1).
Therefore: **the practical content of "remove identity, then group" is
exactly the removal-vs-projection gap, and that gap IS the
boundary-normal identity variance — unremovable without labels.** Above
the localization threshold, grouping error is floor-bound by the
geometry (η) alone; below it, projection buys localization. What remains
label-free buyable: localization, and the noise/state suppressions
(averaging, frame refreshment) that were never the hard part.

**Q.5 — The audit needed one constant, not a new theory.** L1's V-4 miss
is a single diagnosed calibration constant (B̂ = 0.245861 vs 0.25;
(0.25−B̂)·c_cont = +0.002754 reproduces the offset; ALIGNED cells failed
tracking because their CIs are 1.5–2.4× tighter, not because their bias
is larger). R3 stands; the calibrated cross-fitted meter is L2's W-4.

**Q.6 — Method.** Defects #27–#30 recorded; standing rules 18 (JOINT
satisfiability across knob-sharing clauses) and 19 (every lean bar
shadows the theorem's OWN quantity, stated in a fidelity table) created.

## Dated appendix R (2026-08-10, after M4-L2): the floor curve is measured; the localization window lemma; Q.5 refuted

**R.1 — The η-continuum floor law is MEASURED.** σ_u²(η) = η·σ_b²/k_τ +
(1−η)·σ_b²/m: containment 7/10 at the bar with EXACT η-ordering at both
identity energies (the two void cells are below the run's resolution
quantum — a fact about the grid, not the law). The projection-invariant
floor is now the L-line's central certified object.

**R.2 — The localization window lemma (replacing P2M's registered
reading).** L2's W-1 missed on a window the registration itself made
empty (defect #31, proved pre-arms by the rule-18 joint check): at these
dims, {oracle-S > .8} ≡ {Bayes ceiling > .8}, because the ceiling is set
by the SLOW-STATE channel (2.3× the identity's boundary-normal variance)
and is Δ-free — so no Δ has ambient failing while projection cleanly
succeeds. The MECHANISM is real and measured: the localization gap is
+0.2571 [+0.2409, +0.2769] at the hardest rung (4.28×), declining
monotonically to ~0 where ambient succeeds, with oracle-S ON the ceiling
throughout the hard rungs. **Lemma (stated; width law conjectured at
(d/n)^¼):** the qualitative window [Δ*_ambient, Δ*_Bayes] in which
"ambient fails but projected succeeds" exists only when the ambient
break point lies below the state-set Bayes shoulder; its width is
dimension- and noise-governed and CAN BE EMPTY, as here. R2-ISO's final
status: the floor ratio (proved + measured, 8.15×) plus a continuous,
measured, Δ-declining localization gap — and no guaranteed qualitative
regime. Projection claims end here.

**R.3 — Q.5 is REFUTED, on the record.** Calibrating B̂ made tracking
WORSE (2/10 vs the uncalibrated 5/10); the same calibrated meter on TRUE
groups tracks 10/10; cross-fitting cost the two-split contrast a 2.154×
conditioning loss. The audit's residual error is PARTITION-borne. The
completeness meter is certified ON TRUE/GIVEN PARTITIONS ONLY; the
estimated-partition form requires the propagation instrument (M4-L3's
X-3), and if that fails it is retired, not patched again. The same-data
optimistic bias itself is confirmed (pooled −0.005767 [−0.006439,
−0.005165], 10/10 — L2-charter Derivation 4's sign, clean).

**R.4 — Method.** Defects #31–#35; standing rule 20 (an empty joint
condition-set STOPS the leg pre-arms — rule 10's analogue at the
adjudication layer). W-2's estimated-S ARI claim withdrawn at these dims
(the BBP overlap approaches prediction, 30.1% → 0.5% shortfall with Δ;
the bar was on the wrong quantity — defect #33, rule-19 class).

## Dated appendix S (2026-08-10, after M4-L3 — the M4-L line closes): the reverse question, answered

The owner asked: *does assuming error = 0 assert "no identity" — and
conversely, would REMOVING identity make correct personality grouping
possible? Can this be proven?* After three legs (L1–L3) on top of the
P/Q/R theory, the answer in six measured or proved pieces:

1. **In the error-free world, grouping works** — measured: ARI 0.9948
   at zero identity share, both geometries. The hypothesis's premise
   world behaves as it claims.
2. **True identity removal restores grouping completely** — measured:
   ARI → 0.9948 in both geometries. But true removal requires knowing
   b, which requires the groups: the circularity is R1's theorem, and
   its resolution is EM (the proposal, formalized, IS the E-step).
3. **No label-free surrogate can buy what matters above threshold** —
   the floor-invariance lemma (Q.1, proved; measured flat at
   13.5%/15.0% restoration). What projection CAN buy is localization —
   real, measured at 4.28× on the hardest rung — but its qualitative
   window is dimension-governed and CAN BE EMPTY (the window lemma,
   R.2; empty at these dims).
4. **The true governing quantity is the geometry**: the
   projection-invariant floor curve σ_u²(η) = η·σ_b²/k_τ +
   (1−η)·σ_b²/m — measured three times independently (L1 poles, L2
   curve, L3 fresh-seed reproduction; η-ordering exact every time),
   with the between-geometry tax ratio m/k_τ (z-ratio 4; ARI-drop
   ratio 8.15× at matched energy).
5. **Whether the conjecture applies to a given world is READABLE,
   label-free**: the taxometer η̂ is certified at ±0.125 (10/10 cells,
   median error 0.024, ordering exact under every reading), with a
   known +O(0.05) pole bias and the whitening-shape precondition. The
   types-vs-dimensions question is, in this family, an instrument
   reading, not a debate.
6. **"Error = 0" is now an audit, with a certified meter**: the
   completeness meter (surviving-identity share) is calibrated on true
   partitions, carries the partition-propagation correction
   (deviation ~ (1−ARI), R² 0.89, slope −0.047), and has a measured
   noise floor of ~0.005 absolute — the per-world constant fluctuates
   at the same scale as anything smaller. Typology's zero-error claim
   is testable to that precision, and in identity-bearing worlds it
   fails by exactly the identity share (the impossibility half of R3).

**The one-paragraph answer to the owner:** removing identity DOES make
correct grouping possible — under three conditions now proved or
measured: the removal must be TRUE removal (which requires the groups,
so the two are solved jointly as EM fixed points); the geometry must
permit it (the aligned fraction η sets a floor that no label-free
operation touches); and the geometry itself can be read in advance with
the certified taxometer. And "assuming error = 0" is exactly the
assertion b ≡ 0 — no longer a modeling convenience but a testable claim
with a calibrated meter, precise to ±0.005, beyond which the world's
own per-batch fluctuation takes over. The old hypothesis was not wrong;
it was an audit criterion waiting for its instrument.

**Method.** Defects #36–#38; standing rule 21 (precision budgets on
containment bars). Line synthesis:
`docs/SUICA_M4_L_TYPOLOGY_LINE_SYNTHESIS.md`. Scope as always:
EXPLORATORY, synthetic, instrument-world claims; nothing here licenses
claims about persons.
