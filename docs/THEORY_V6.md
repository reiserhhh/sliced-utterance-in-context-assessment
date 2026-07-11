# SUICA THEORY V6 — Text as a Realized Path: the Unified Static + Motion Theory

Created 2026-07-12. Status: theory document, Tier-U/T1 throughout; no seals touched.
v6.1 (same day): the F12/W2 correction cycle (Fable-planned, Sonnet-executed) struck
E3's bounce claim (leverage artifact — gust axes are white), unified wcl_60's three
anomalies as sparse-burst dynamics, retracted the bid-ask-bounce sub-analogy, added the
exact MA(1) moment inversions as standing audit equipment, and downgraded the P9 flow
factor to conditional-on-iid-gusts (F12.2 identifiability theorem).
v6.2 (same day): the F12.4 exact finite-n centering-bias correction (closed form,
independently verified) re-inverted the Essays moments: the corpus-mean gust memory is
FAINTLY POSITIVE (B̂ diag mean +0.030, CI [+.014, +.048], 500/500 bootstrap draws > 0),
carried by content constructs (wcl_35/36/03, first_person, wcl_13 — each CI-solid),
with wcl_60 the lone anti-persistent exception — construct-by-construct agreement
between the two leverage-free instruments. "White gusts" is superseded by "faintly
persistent gusts with a sparse-burst exception"; the model generalizes to signed-memory
MA(1) and the deployed API reports the signed memory coefficient as primary.
v6.3 (same day): lag-2 discrimination (F12.5/W4) refines the memory taxonomy — decaying
carry-over (wcl_35/36/13, AR-type, φ̂ ≈ +0.08–0.10, cross-moment-consistent with their
lag-1 coefficients) vs one-step echo (first_person, wcl_03, MA-type) vs sparse bounce
(wcl_60, MA, θ̂ = +0.235) — and surfaces an unanticipated PERIOD-2 gust signature
(wcl_20/wcl_22: CI-solid positive lag-2 excess that neither MA(1) nor AR(1) can produce;
lag-3 identity registered as the W5 separator).
v6.4 (same day): the ladder inversion (F12.6/W5) hit a STRUCTURAL indeterminacy —
within-text centering has a near-null "smooth ladder" direction (σ_min = 0.0087 of the
exact 5×5 map), so lag coordinates beyond ~2 are ill-posed at feasible n; the Nyquist
spectral functional f(π) IS tightly estimable and confirms the period-2 ordering with
disjoint CIs (wcl_20 1.033 / tension 1.016 top vs wcl_60 0.557 / first_person 0.628
bottom). New principle (F12.6.3): parameterize gust texture by well-conditioned spectral
functionals, not autocovariance ladders — the estimable-functional move.

v6.5 (same day): the normalized Nyquist ratio ρ_π = f(π)/γ0 (F12.7/W6) becomes the
deployed one-number dynamics fingerprint (white 1; bounce > 1; carry-over < 1): wcl_60's
predicted ranking INVERSION confirmed CI-solid (ρ_π = 2.51 [1.28, 7.35]); the carry-over
set sits below 1 (3/5 CI-solid); the "period-2 standing wave" reading of wcl_20 DIED
informatively (ρ_π = .770 CI-solid BELOW 1 — its lag-2 excess lives inside a
carry-over-dominated spectrum; even-lag anomaly, W7 = f(π/2) shape separator). Two new
exact facts from deployment verification: pure-m=5 truncated compositions are exactly
singular (3s0+4s1+2s2 ≡ 0 at n=3), and the 5-moment γ0 left-functional is
ill-conditioned (|w| ≈ 39-70) — the hybrid functional (f_π from the 5-moment solve, γ0
from the truncated solve) is the queued deployment fix.

v6.6 (same day): the spectral shape pair (rho_pihalf, rho_pi) deployed with the hybrid
per-functional denominator (F12.8/W7; |w_gamma0| 39 -> 4; AR(2) calibration 1.41 -> 1.75;
MA(1) quarter-frequency invariant exact): wcl_20's even-lag anomaly CONFIRMED CI-solid
(rho_pihalf .645 [.428, .914]); wcl_60's one-step-echo invariant survives; and wcl_07
emerged as the only CI-solid Delta_shape (+.540) — a damped ~4-window oscillation
(AR(2)-even, a2 ~ −0.2 post-hoc). The signed two-parameter family (odd-lag memory x
even-lag oscillation) is queued as the W8 unification hypothesis.

v6.7 (same day): the AR(2) texture triangle (F12.9/W8) closes the texture arc — gust
dynamics reduce to model (M'''): level + flow + AR(2)-textured gusts (a1, a2 on the
stationarity triangle: carry-over a1 > 0; even structure a2 CI-solid at BOTH signs —
wcl_20 +0.30, wcl_07 −0.16) plus a NON-NESTED MA-echo class (first_person/wcl_03 = the
two worst AR(2) fits of 19, as "not nested" predicts). One letter-fired kill (wcl_60
fits as well as median) was ruled UNDECIDABLE by an explicit power argument (its
functional sds are 7-13x the field) with the target claim separately refuted — the
program's first power-annotated kill adjudication. Promoted to T7 below.

v6.8 (same day): W9 resolved the PANDORA long-text flag as a CAP-ARTIFACT STRATUM —
Tier-U extraction truncates bodies at 1,500 chars, so 512+-token texts are
definitionally non-prose (chars/token 2.48 vs 4.79; markdown pipe tables in 14/72);
all PANDORA within-text dynamics claims are retroactively artifact-stratum and OUT OF
SCOPE under the frozen extraction (the native corpus carries dynamics). The registered
quote/list/code stripper was a no-op (kill fired as registered); the mechanism family
survived under the corrected taxonomy via the executing agent's provenance dig.

**Lineage.** v3/v4 (this project): the static rind theory — text scores decompose into
choice, base, and signature channels; frozen v4 battery and composite. v5 (field
deployment, imported): form-first evolution and the T-geometry mathematical layer
(invariance, projective aggregation, spectral nulls; F7–F9). F10 (operator conjectures,
2026-07-11): factor fluidity — frames flow with conditions, individuality as axes,
continuization, functionalization, flow-only factors. F11 / V6 (this document): the
motion layer at scale, cross-corpus, with the theorem-similarity mapping and the
personality-inference extension. Formal backing: SUICA_THEORY_FORMAL_NOTES_V1/V2/V3;
every number is ledger-traceable (SUICA_CLAIMS_LEDGER.md); every directional prediction
was committed before its run and its fate is recorded (Section 7).

---

## 1. The object

A person u emits texts; each text is read as a REALIZED PATH: windows k = 0..m−1 of
fixed token length carry a battery vector w_k ∈ R^p (p = 19, dictionary-disjoint wcl
clusters + v2 lexica). The V6 generative skeleton per text:

    w_k = p_text + k·s + g_k                                   (M)

    p_text = μ_u + venue/base structure     level     Cov = Π
    s      = drift along the text           flow      Cov = Σ_flow
    g_k    = transient co-fluctuation       gust      Cov = Γ, anti-persistent (E3)

with the static rind decomposition (v4) living inside p_text: y = f_u + b_r + γ_u,r +
ε, r ~ π_u (choice / base / signature channels), and the position layer (F10.6/7)
entering E[w_k] as construct-specific profiles — flow-type (functions of relative
position t), boundary-type (functions of zone distance), or flat.

The PERSON, in V6, is the generator tuple:

    P_u = ( μ_u,           level trait vector          — v4 object
            shape_u,       position profiles           — F10.7 recipes
            style_u,       motion style: loadings on Σ_flow/Γ factor structure — F11/E4
            U_u )          personal frame on Gr(k,p)   — F10.3/P6

Each component has its own estimator, its own nulls, and its own data economics (T4).

## 2. The measurement mapping (theorem set)

**T1 (aggregation kills motion at 1/m).** Level aggregation reads Cov_L = Π + Γ/m (+
vanishing flow terms with centered indices). Proof: independence of g_k across windows;
LLN on the window mean. Univariate face = F8.2's clustered-noise curvature; the φ
coordinate φ(r) = r/(1−r) makes reliability growth exactly linear, φ(r_W) = W·φ(ρ)
(F8.1, proof in notes V2). CONSEQUENCE: "stop and the togetherness disappears" is a
theorem, not a metaphor — any coherence carried by Γ alone is erased by averaging.

**T2 (contrast identification).** On m = 3 support with ℓ = (w₂−w₀)/2 and
q = (w₀−2w₁+w₂)/√6: Cov_ℓ = Σ_flow + Γ/2, Cov_q = Γ, Cov(ℓ, q) = 0; hence
Σ̂_flow = Cov_ℓ − Cov_q/2 is identified without any permutation machinery. Proof: direct
computation under (M). This is how flow factors and gust factors are separated (F10.8).

**T3 (support identifiability).** On 3-point support, a monotone flow in t and an
additive boundary-zone model are observationally equivalent; they separate only on
texts realizing (start-distance ≥ 2 AND end-distance ≥ 2) cells — deep interiors. Proof:
parameter counting on the five observable (τ, δ) cells (notes V3/F10.7). CONSEQUENCE:
"out-of-range prediction" is not optional decoration; it is the ONLY way to identify the
flow coordinate. Instantiated: first_person transports as a function of relative t
(deep-interior MAE 1.114 vs zones 4.167 vs constant 1.365 — F10.7/P8b).

**T4 (measurement economics — occasions vs tokens).** Under (M) with N texts of m
windows: Var(level estimate) ≍ (Var(p) + Γ_c/m)/N — occasion-limited; Var(gust-structure
estimate) ≍ 1/(N·(m−2)) — token-limited, accumulating (m−2) contrasts per text. Discrete
analogue of the drift-vs-diffusion asymmetry in diffusion statistics (drift needs time
span; diffusion needs sampling frequency). CONSEQUENCE: motion-style descriptors are
cheap in occasions and expensive in tokens; level traits are the reverse. A single long
text can, in principle, estimate motion style but never a norm-referenced level — the
formal basis for position of motion constructs in AI-native, single-document assessment.

**T5 (nameability, restated from F10.2).** An axis earns a name only if its frame is
(i) condition-invariant and (ii) person-shared. Empirical status by layer: the four
population level factors pass time-invariance (P3/P4) and fail person-sharedness at the
frame level (P6: personal frames disperse, self > stranger, sharpened by residualizing
the shared frame); position bends PC3/PC4 (P5); so even the static battery's axes are
nameable only as population coordinates, not as person structures. Motion-layer axes are
unnameable by default and are handled as machine coordinates (constitutive-AI stance).

**T6 (portability follows visibility — new empirical law, falsifiable).** Motion factors
WITH a level shadow transport across corpora; statically INVISIBLE structure is
register-local. Evidence: the first_person-led slope factor crosses Reddit → Essays at
congruence .940 (second factor .782; static frames .923 at rank 1), while the PANDORA
flow-only gust factor — robust inside Reddit (time .956/.971, user-demeaning .982,
64-token scale .622, large venues .926/.896) — lands at .200 (random ≈ .23) on Essays.
Similarity: integrated covariance (asset-fundamental, portable) vs microstructure noise
(market-specific) in realized-covariance theory. [v6.1 correction: E3's apparent
NEGATIVE lag-1 "bounce" was struck by the leverage-free Δ² instrument (W2a) — Essays
gust axes are WHITE (ρ1(Δ²) = −.640 vs iid null −.649, p = .87); the certified texture
is construct-level, not axis-level: the zero-inflated wcl_60 bounces (θ̂ ≈ .09,
p = .0005) and content constructs carry over mildly, while PANDORA's thin long-comment
stratum shows format-periodic alternation (quote/list structure), not an MA(1) field.
The realized-covariance analogy stands on the portability split; the bid-ask-bounce
sub-analogy is RETRACTED.] FALSIFIER:
exhibit a statically invisible factor that transports across registers — one clean
counterexample breaks the law.

**T7 (spectral texture of gusts; the F12 arc consolidated).** Under within-text
centering, gust dynamics are estimable ONLY through well-conditioned spectral
functionals (F12.6.3): the signed memory r_c, and the hybrid shape pair
(rho_pihalf, rho_pi) with per-functional left-solve conditioning (F12.8). Exact
invariants: iid gusts pin ρ1(Δ²) = −2/3, (rho_pihalf, rho_pi) = (1, 1); MA(1) of ANY
memory pins rho_pihalf = 1. The texture family is the AR(2) stationarity triangle plus
a non-nested MA-echo class (F12.9/W8: even-lag structure CI-solid at both signs of a2;
echoes = worst AR(2) residuals). Every estimator carries its exact finite-n centering
correction (F12.4, incl. the d(3) = 56/9 boundary) and its composition-dependent
calibration; power is a per-construct property (denominator instability can render a
test undecidable — recorded, not forced). Personality reading: texture parameters are
register-anchored machine coordinates (T5/T6 apply); their person-level stability is
untested (native-corpus item).

## 3. Theorem-similarity table (advanced tools ↔ SUICA objects)

| mathematical tool / theorem | SUICA object | what transfers | where the analogy is bounded |
|---|---|---|---|
| Itô/semimartingale decomposition (drift + martingale) | (M): level + flow·k + gust | which statistics read which layer; differencing reads the martingale part | our "time" is token position; increments are windows, not infinitesimal |
| Realized covariance vs microstructure noise; Epps-type locality | gust matrix Γ vs level/drift structure; T6 portability law | portable-fundamental vs local-texture split | no trading mechanism; "market" = register/genre; the bid-ask-bounce sub-analogy was tested and RETRACTED (W2a: axes white; wcl_60 the lone sparse-burst bouncer) |
| MA(1) moment inversion; Δ² prewhitening (exact ρ1 = −2/3 under iid) | F12 identities: Γ̂0 = (7S0+8·symS1)/10, B̂ = (6Γ̂0−S0)/8; leverage-free dynamics test | exact estimator + audit of our own flow estimator (Σ̂ = Σ_flow + (2/3)B on m=3) | m = 3 support cannot separate Σ_flow from B (F12.2 theorem) |
| Martingale LLN / averaging | T1: Γ/m attenuation — "stop and coherence disappears" | exact | — |
| Spearman–Brown as Möbius flow; projective line (F8) | φ(r) = r/(1−r) linearization; composites blend in φ | exact theorem | — |
| Marchenko–Pastur edge (RMT) | factor claims vs shuffle edges (P3, F10.8, F11) | exact null construction | heteroscedasticity → empirical edges preferred |
| Grassmann manifold, principal angles, frame bundles | condition-indexed frames V(t); personal frames U_u; nameability = flat shared section (T5) | distance/holonomy language; instruments P4–P6 | no connection is estimated; "flatness" tested only at sampled conditions |
| Boundary-layer theory / matched asymptotics (inner-outer) | position profiles: zone coordinates vs similarity coordinate t (F10.7) | coordinate-race DESIGN; identifiability (T3) | composite inner+outer model gave no CV gain at current SNR (E2b) — analogy is a design tool, not a fitted necessity |
| Group-theoretic invariance (F7 lattice) | every null = subgroup choice; artifact = statistic constant on a larger orbit | exact | — |
| Drift-vs-diffusion estimation asymmetry | T4 measurement economics | rate structure (occasions vs tokens) | constants differ; discrete windows |

## 4. Extension to personality inference (人格推論への拡張)

**4.1 What a text stream can tell about a person, by layer.**
- LEVEL (μ_u): needs many occasions and norms; the v4 battery + purity gates + φ-space
  composites. Choice channel is signal here (F3/F8.4).
- SHAPE (position profiles): scoring recipes by shape class (F10.7): flow-type
  constructs → t-regression; boundary-type → zone offsets (open/close/interior);
  plateau → interior-only. GENRE-ANCHORED: directive and wcl_22 flip signs between
  Reddit and Essays (E2a) — position norms must be built per register.
- MOTION STYLE (style_u): person-level loadings on motion factors — established as
  statically invisible, replicating individual differences (E4: replication .777–.784
  with static congruence ≤ .03). By construction, NO level-reading instrument
  (questionnaires included) can measure them: they are erased by any averaging (T1).
  They are also register-anchored (T6) — a motion style is a (person × register)
  property until proven portable.
- FRAME (U_u): orientation as identity (F10.3/P6); principal-angle metric; exploratory.

**4.2 Inference licenses (what may be claimed today).**
- Motion-style dimensions exist, replicate, and are orthogonal to the static battery —
  Tier-U facts.
- ANY claim linking motion styles to Big5/MBTI or clinical outcomes is UNLICENSED: it
  requires a new prospective seal (not opening #2's registered candidates). The native
  corpus (OP-36) and the single-text sufficiency instrument (F11.5) are the designed
  vehicles.
- Vector/axis naming remains unlicensed (T5); deployment is machine-facing.

**4.3 Assessment design consequences.**
- A short questionnaire and a long text are NOT interchangeable: they live on opposite
  sides of T4 (occasions-rich/tokens-poor vs occasions-poor/tokens-rich). A single long
  document supports motion-style estimation; population-referenced level claims need
  either norms or many occasions.
- Battery v-next admits MOTION CONSTRUCTS as first-class candidates under the F10.8
  gates (supra-edge, person-disjoint replication, level-invisibility, vocabulary-overlap
  screen) plus a T6 portability tag (portable / register-local).
- The pass-A opening-share confound (F10.6) gets a principled fix: position-conditional
  scoring per shape class.

## 4.4 Deployment (v6.1, 実戦)

The surviving estimators ship as an operational module in the public package:
suica_core/motion.py — text_windows / motion_profile(texts, scorer, axis=None) returning
level, slope, Γ̂0, B̂, per-construct θ̂, gust-corrected flow spectrum, and a mandatory
licenses list encoding T4/T5/T6 (sample-standardized, register-anchored, no trait
inference; F12.2 support caveat). Implemented Sonnet-to-spec, planner-audited line-by-
line against the F12 identities, and covered by 12 synthetic-recovery tests (MA(1)
recovery at θ ∈ {0, .4}, planted-flow recovery after gust correction, the T4
estimability guard, leak-drop semantics); full package suite 59/59. Known finite-sample
θ̂ bias documented in the module and listed as an open instrument (Section 6).

## 5. Battery v-next gates (registry addition)

A motion-space construct enters the registry iff: (1) supra empirical shuffle edge;
(2) person-disjoint half replication ≥ .5; (3) level-space visibility inside the shuffle
band (for flow-ONLY claims) or declared visible (for portable motion factors);
(4) vocabulary-overlap screen for mixed v2×wcl loadings; (5) T6 tag from a second
register. The frozen v4 level battery and composite weights are untouched by V6.

## 6. Open instruments (designed, not yet executable / not yet run)

- Single-text sufficiency (F11.5): needs many long texts per person — native corpus.
- Leverage-free gust dynamics: DONE (W2a, F12) — outcome: axes white, wcl_60 bounces,
  content constructs carry over; E3's bounce struck.
- Format-aware PANDORA windowing: RESOLVED (W9/F12.10) — the m ≥ 4 stratum is a
  1,500-char extraction-cap artifact (non-prose, table-dense); PANDORA within-text
  dynamics are permanently out of scope under the frozen extraction; the native corpus
  carries the dynamics program.
- Analytic finite-m centering-bias correction: DONE (F12.4, closed form; verified
  analytically, by 4M-text Monte Carlo, and out-of-sample; deployed as the default
  inversion). Successor item: MA-vs-AR gust discrimination via lag-2 moment identities
  (S2) — the signed memory coefficient cannot tell a one-step MA echo from a decaying
  AR carry-over; the lag-2 structure can.
- Small-venue gust heterogeneity (E1: power vs true heterogeneity at n ≤ 75).
- Person-level motion style portability (needs a second register with per-person volume).
- wcl_13 super-linearity (F8.3 flag); OP-33 co-selection axes under the MP edge.
- Motion-style ↔ Tier-L relevance: new seal required; explicitly deferred.

## 7. Registered-vs-outcome record (the honesty table of the F10–F11 program)

| registration (commit) | lean | outcome |
|---|---|---|
| P4 time flow (60ce99c) | population frame rigid | ✓ rigid (p = .24–.66) |
| P5 position (60ce99c) | rotation small; first_person opening-high; directive closing-high | rotation REAL (PC3/4); first_person ✓; directive ✗ (p=.104) |
| P6 personal axes (60ce99c) | self > stranger raw AND residualized | ✓ both; gap WIDENS residualized (.277 vs .216) |
| P7 continuization (e839ed9) | edge-localized everywhere | ✗ construct-specific: first_person true flow; tension/directive boundary |
| P8a interpolation (c5a9b4f) | curvature helps tension/directive | ✗ person baseline wins for boundary types |
| P8b coordinate race (c5a9b4f) | first_person zones | ✗ relative-t decisive (1.114 vs 4.167) |
| P9 flow-only factors (a493ff6) | exists at gust layer; ordered flow too weak; person-level open | gust ✓ (all gates, vocab-disjoint); ordered flow CERTIFIED (lean too pessimistic); person-level died at rep .150 |
| E1 gust robustness (8e2b0ba) | venue ≥.6; time ≥.7; demeaned ≥.8; scale64 .4–.6 | large venues .90–.93 ✓; small venues FAIL (power?); time .86–.97 ✓; demeaned .982 ✓; scale64 .622 ✓ |
| E2 Essays transport (8e2b0ba) | first_person transports; gust congruence ≥ .5; essay-level invisible factor exists; composite wins CV | first_person ✓ (+ curvature); **gust .200 — KILLED as registered**; invisible factor ✗ (visible factors transport .94 instead); composite ✗ (no CV gain) |
| E3 gust dynamics (8e2b0ba) | AR ≈ 0 white; boundary-elevated magnitude | ✗ anti-persistent (−.31 vs null −.19, bounce); magnitude arm INCONCLUSIVE (leverage flaw, recorded) — E3's bounce later STRUCK by W2a |
| E4 person retry (8e2b0ba) | ≥1 component, rep ≥ .5 at gate ≥5 residualized | ✓ rep .777 (gate 5) / .784 (gate 8) |
| W2a Δ² dynamics (da07462) | Essays axes anti-persistent, θ ∈ [.1, .5] | ✗ axes WHITE (gust1_E p = .87, θ̂ = 0) — E3 struck as leverage artifact; wcl_60 the lone certified bouncer (θ̂ = .091, p = .0005); mild positive carry-over in content constructs; PANDORA m ≥ 4 non-white but format-suspect and unstable (wcl_11 flips −.20 → −.98 between arms) |
| W2b corrected separation (da07462) | corrected λ1 rises; rep < .5; bounce factor exists, congruent with Γ0 | B̂ ≈ 0 so λ1 falls, not rises (premise wrong); rep .308 ✓; bounce factor ✗ on every gate (perm p = .98, rep .108, congr .026) |
| W3 corrected re-inversion (0a4a97a) | corrected B̂ mean ≈ 0 (\|mean\| < .004); small-θ constructs shrink > half; wcl_60 ≥ .25 | POINT LEAN KILLED: B̂ mean = +.0303, CI [+.014, +.048], 500/500 draws > 0 — the naive negative was centering artifact (its CI contains the predicted −.013) hiding REAL mild positive memory; per-construct predictions ✓ (tension .070→.017, wcl_54 .057→.004, wcl_23 .103→.048, wcl_60 .34); "white gusts" superseded by faint persistence + wcl_60 bounce; instruments converge with W2a construct-by-construct |
| W9 format-aware (e2b2240) | raw anchor reproduces W2a; formatting concentrated in long texts; stripping removes >= half the excess | anchors bit-exact x2; census INVERTED (0/72 long texts have quote/list/code lines); KILL FIRED (stripper no-op) — and the provenance dig found the true mechanism: 1,500-char extraction cap makes m >= 4 definitionally non-prose (chars/token 2.48; pipe tables 14/72) -> PANDORA dynamics = ARTIFACT-STRATUM, out of scope under frozen extraction |
| W8 AR(2) triangle (e04d5e0) | carry-over (a1~+.1, a2~0); wcl_20 a2~+.15 / wcl_07 a2~-.15..-.2; wcl_60 worst residual; echoes worse than carry-over | (a) direction holds; (b) CONFIRMED CI-solid both signs (wcl_07 -0.16 [-.28,-.02]; wcl_20 +0.30 [+.04,+.32], a1=.68 boundary surprise); (c) FAILED — kill letter-fired, ruled UNDECIDABLE by power (sds 7-13x field), target claim refuted via (d); (d) HOLDS emphatically (echoes = 2 worst fits of 19) |
| W7 shape pair (eabc17b) | carry-over set Delta>0; wcl_20/22 below them, rho_pihalf depressed; wcl_60 rho_pihalf ~ 1; hybrid restores AR(2) calibration | (a) 4/5 directional (wcl_03 flips sign), none solid; (b) wcl_20 rho_pihalf = .645 CI-SOLID depressed (even-lag confirmed), ordering P=.912 strong lean; (c) invariant survives (CI includes 1; unstable denominator noted); hybrid held with no fallback, calibration 1.41 -> 1.75, 72/72 tests; UNREGISTERED: wcl_07 only CI-solid Delta (+.540) = damped 4-window oscillation -> W8 signed-(memory, a2) unification queued |
| W6 Nyquist ratio (ed971f1) | wcl_60 rho_pi > 1 CI-solid (ranking inversion); carry-over set < 1; wcl_20/tension > 1 | (a) CONFIRMED 2.51 [1.28, 7.35], inversion exact; (b) 3/5 CI-solid below 1; (c) FAILED INFORMATIVELY — wcl_20 .770 CI-solid BELOW 1 (standing-wave reading dead; even-lag anomaly inside carry-over spectrum); gamma0 5-moment functional ill-conditioned (premise half-wrong, registered fallback absorbed it); KILL not fired |
| W5 gust ladder (6669ccc) | wcl_20/22 standing-wave (g4/g2 in (0.1,0.9)); wcl_60 lag-1-confined; memory set geometric; indeterminate-if-CIs-wide registered as (d) | (d) FIRED structurally: centering null direction (sigma_min .0087) makes lag coordinates ill-posed — coordinates unresolved 19/19, class rule vacuous (design flaw recorded); f(pi) tightly resolved and CONFIRMS the period-2 ordering with disjoint CIs (wcl_20 1.033/tension 1.016 vs wcl_60 .557/first_person .628); KILL not fired; new estimable-functional principle F12.6.3 |
| W4 MA-vs-AR (5064a0a) | corpus R2 CI-solid positive; memory set AR; wcl_60 MA | corpus R2 +.021 directional only (CI spans 0); memory set 3/5 AR (wcl_35/36/13, φ̂ consistent with lag-1) with first_person/wcl_03 = one-step echo; wcl_60 MA ✓; UNREGISTERED: period-2 signature in wcl_20/wcl_22 (CI-solid lag-2 excess, both families fail) → W5 lag-3 separator |

Score: roughly half the leans held. The program's value is exactly that the instruments,
not the leans, decided — and that both corpora, both directions of surprise, and one
design flaw are on the record.

## 8. Governance

All F10–F11 work is Tier-U / label-free; the Essays loader reads user_id and text only
(trait columns never loaded); frozen v4 battery, composite weights, seals, and the
opening budget are untouched; the trading deployment's code was never executed (formulas
and documents ported with attribution). Motion constructs are candidates, not members.
