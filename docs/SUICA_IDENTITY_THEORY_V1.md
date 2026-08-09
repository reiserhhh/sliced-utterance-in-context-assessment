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
