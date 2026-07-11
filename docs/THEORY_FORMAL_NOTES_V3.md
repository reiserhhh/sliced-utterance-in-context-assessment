# SUICA Theory Formal Notes v3 — F11: the motion layer at scale (V6 program)

Created 2026-07-12. Extends F1–F6 (V1) and F7–F10 (V2). Operator directive: mount a
large-scale program on the F10.8 discovery (coherence that exists only in motion), reach
every corner by repeated experiment, identify theorem-level similarities with advanced
mathematical tools, extend them to personality inference, and complete THEORY V6.

Discipline unchanged: predictions and kill conditions are REGISTERED AND COMMITTED BEFORE
each run; wrong leans are recorded, not repaired. All work is Tier-U / label-free; the
Essays corpus is used TEXT-ONLY (the loader reads columns user_id and text and never the
trait columns; no seal is touched; the confirm-half label budget is unaffected).

## F11.0 — The motion layer, consolidated model

Per text (comment/essay), window k of m:

    w_k = p + k·s + g_k        p ~ (μ_u, Π)   person/text level
                               s ~ (σ_u, Σ_flow)  ordered drift along the text
                               g_k ~ (0, Γ)   gust (transient co-fluctuation)

plus the F10.6/F10.7 position structure entering through E[w_k] as inner (boundary-zone)
and outer (relative-t) profiles. Established so far (F10.8): Γ has factor structure
partly invisible in level space (B-gust1: replication .829, level-visibility 0.972,
vocabulary-disjoint loadings); Σ_flow has at least one certified factor (statically
visible); the person-level invisible candidate failed replication at gate ≥3.

## F11.1 — E1 registered predictions: gust robustness sweep (PANDORA)

Arms on the m=3 cohort (618 comments): (a) venue-class replication (classes with >= 60
comments), (b) temporal median-split replication, (c) user-demeaned q contrasts, (d)
window-scale 64 tokens (same comments, first/mid/last 64-token windows).
LEANS: gust1 congruence >= .6 across venue classes; >= .7 across time halves; >= .8 under
user-demeaning (gusts are within-comment objects; person effects should barely matter);
scale-64 congruence positive but attenuated (.4–.6) — gusts may have a characteristic
token scale. KILL: venue congruence at chance (~.23 random baseline) would demote gust1
to a venue-composition artifact.

## F11.2 — E2 registered predictions: Essays transport (the far corner)

Essays = different register (stream-of-consciousness), different population, long
documents (dense interiors that PANDORA lacks). Battery transports via the frozen wcl
transform (built for Essays transport) + v2 scorers. Windows: 128 tokens, cap 12,
endpoint-preserving; leak mask per window, drop essay on any hit.
(a) Position profiles: first_person monotone decline TRANSPORTS (lean YES, flow-type);
    tension closing jump ATTENUATES or vanishes (lean: it is a Reddit discourse act —
    open); directive opening elevation OPEN.
(b) Law-of-the-wall (matched-asymptotics analogy): on m >= 4 essays the within-essay
    position model composite = inner(start-zone) + inner(end-zone) + outer(t) beats both
    single-coordinate models by essay-level CV for the MIXED constructs; overlap check =
    single-coordinate models agree in the interior and disagree at boundaries.
(c) Flow/gust separation on (first, mid, last) triples: gust structure EXISTS on Essays
    (supra-edge, author-half replication) — lean YES.
(d) CROSS-CORPUS HEADLINE BET: Essays gust1 congruent with PANDORA gust1 with |cos| >= .5
    (lean; random baseline ~.23). KILL: failure demotes the gust factor from
    corpus-general to register-specific (still real, smaller claim).
(e) Essay-level flow-only retry (the F10.8 phase-C death, transported): supra-edge +
    author-half replicating + L-invisible motion component on Essays — OPEN, lean YES at
    this power (each essay carries m ~ 4-6 windows).

## F11.3 — E3 registered predictions: gust dynamics

On Essays m >= 4 (and PANDORA m >= 4 descriptively): within-text detrended residuals
projected on the gust axis give a per-window gust series γ_k.
(a) AR(1) of γ_k vs within-essay order-permutation null: LEAN ≈ 0 (white gusts — iid
    assumption holds); significant positive AR would upgrade "gusts" to "weather"
    (mean-reverting OU-like state, a different math object).
(b) |γ_k| vs position: LEAN boundary-elevated (gusts cluster where discourse work is
    done — openings/closings).

## F11.4 — E4 registered predictions: person-level retry (PANDORA)

Power raise on the F10.8 phase-C failure: gates >= 5 and >= 8 long comments; and the
sharp arm residualizes user mean-slope vectors against the user-level static top-4 frame
BEFORE factoring (invisibility by construction; the question becomes existence +
replication). LEAN: at gate >= 5 with residualization, at least one motion component
clears the edge with half-replication >= .5. KILL: failure at both gates bounds the
person-level flow-only factor below current-corpus detectability (native-corpus item).

## F11.5 — Measurement-economics theorem (registered as theory; instrument deferred)

In the F11.0 model with N texts of m windows each: the level estimate μ̂_u has
Var ≈ (Var(p) + Γ_c/m)/N (occasion-limited: dominated by 1/N), while the gust-structure
estimate from within-text contrasts accumulates (m−2) contrasts per text:
Var(Γ̂ entries) ∝ 1/(N·(m−2)) (token-limited). Consequently DIFFUSION-TYPE (motion)
descriptors are cheap in occasions and expensive in tokens; LEVEL-TYPE descriptors are
the reverse. This is the discrete analogue of the classical diffusion-statistics
asymmetry (drift error ~ 1/√T, diffusion error ~ 1/√n within-path). Single-text
sufficiency instrument (cross-text reliability of one-text gust loadings vs one-text
level scores at matched token budgets) is DESIGNED but not executable on current corpora
(PANDORA: too few m >= 4 texts per user; Essays: one text per person) — declared open for
the native corpus (OP-36).

## F12 — MA(1) gusts: exact identities, an identifiability theorem, and the correction
## of our own flow estimator (registered 2026-07-12, before the W2 runs)

Process note (operator directive): analysis/planning by Fable, execution by Sonnet
agents; mathematical reduction to the base model over lexical narration; iterate
experiment -> correction -> theory.

**F12.1 (model (M′) and exact identities; derived, not fitted).** Replace iid gusts in
(M) with MA(1): g_k = η_k − θ η_{k−1} (multivariate: g_k = η_k − Θ η_{k−1}). Write
Γ0 = Cov(g_k), Γ1 = Cov(g_k, g_{k+1}), B = (Γ1 + Γ1ᵀ)/2; E3's anti-persistence means B
has a negative direction. Exact consequences:

(i) Second differences Δ²w_k = w_{k+1} − 2w_k + w_{k−1} kill level and linear drift
    PER TRIPLE (no OLS, no leverage). Univariate lag-1 autocorrelation of Δ² under (M′):

        ρ1(Δ²)(θ) = −(4(1+θ²) + 7θ) / (6(1+θ²) + 8θ),

    equal to −2/3 iff θ = 0, strictly decreasing to −3/4 as θ → 1. This is the
    leverage-free replacement for E3: the iid hypothesis pins ρ1(Δ²) at −2/3 exactly.

(ii) Multivariate moment identities: S0 ≡ Cov(Δ²) = 6Γ0 − 8B and sym S1 ≡
     sym Cov(Δ²_k, Δ²_{k+1}) = −4Γ0 + 7B. Hence the EXACT inversions

        Γ̂0 = (7·S0 + 8·sym S1)/10,       B̂ = (6·Γ̂0 − S0)/8.

(iii) Wide difference d = (w_{m−1} − w_0)/(m−1) has Cov(d) = Σ_flow + 2Γ0/(m−1)²
     with NO Γ1 term (endpoint gap ≥ 2), so a CORRECTED flow estimator exists on m ≥ 5:

        Σ̂_flow(corrected) = Cov(d) − 2Γ̂0/(m−1)²   (per-m stratum, precision-pooled).

**F12.2 (identifiability theorem — our own P9 estimator is contaminated).** On adjacent
3-point support, Cov_ℓ = Σ_flow + Γ0/2 (the ℓ kernel is γ1-free) and Cov_q = Γ0 − (4/3)B,
so the F10.8 estimator satisfies EXACTLY

        Σ̂ = C_ℓ − C_q/2 = Σ_flow + (2/3)B.

Σ_flow and B are therefore NOT separately identifiable on m = 3; the P9 "ordered flow
factor" (λ1 = .486, rep .809) is certified only under B = 0. With B in the E3 direction
the estimator is biased along B's structure. STATUS DECISION (theory-level): the P9 flow
claim is DOWNGRADED to conditional-on-iid-gusts pending an m ≥ 5 correction in that
register (PANDORA m ≥ 5 is too thin: ~41 comments).

**F12.3 (registered leans for the W2 runs; Sonnet executes).**
(a) W2a Δ² dynamics: Essays ρ1(Δ²) below the iid simulation null (matched m's, same
    centering pipeline); gust-axis θ̂ in [.1, .5]. KILL: ρ1(Δ²) consistent with the iid
    null strikes E3's anti-persistence as pure leverage artifact and restores white gusts.
(b) W2b corrected separation (Essays m in 5..12): corrected λ1(Σ̂_flow) RISES vs the
    uncorrected value (the +2/3·B contamination is negative-leaning), but author-half
    replication stays < .5 — flow remains uncertified on Essays (lean).
(c) Bounce factor: λ1(−B̂) exceeds the within-text permutation null; author-half
    replication ≥ .6; top eigenvector congruent with Γ̂0's top ≥ .6 (bounce structure ≈
    gust structure, common-θ reading). Level-visibility: open.
(d) The F12.2 downgrade of P9 stands regardless of W2 outcomes (it is a theorem).

## F12 results (W2a/W2b, run AFTER registration da07462; Sonnet-executed under Fable
## specs; W2b agent validated the inversions on synthetic MA(1) at six θ values)

**W2a — leverage-free Δ² dynamics.**
Essays primary arm (1,349 texts 5 ≤ m ≤ 12, 4,746 pairs; iid simulation null mean
−0.6487, band [−.663, −.634]):
- **gust axes are WHITE: gust1_E ρ1 = −0.6402, p = .871 (θ̂ = 0); gust1_P −0.6581,
  p = .095 (θ̂ = .036). The registered kill fired against E3: its anti-persistence
  (−0.31 vs pairing null −0.19) was the OLS-leverage artifact. E3's bounce claim is
  STRUCK.**
- The one certified bouncer: **wcl_60, ρ1 = −0.6711, p = .0005, θ̂ = .091** (sensitivity
  arm p = .034) — the zero-inflated apostrophe construct. Bounce = burst-recovery of
  sparse events. This UNIFIES wcl_60's three anomalies (F8.3 asymptote violation, the v5
  hurdle regime, θ > 0) under one mechanism: sparse event bursts.
- Systematic MILD POSITIVE persistence (ρ1 significantly LESS negative than null;
  one-sided p ≥ .97) for content-flavored constructs: first_person (.9955), wcl_36
  (.997), wcl_07 (.998), wcl_13/35/15 (~.996-.998), wcl_02/03 (.98), novelty (.971) —
  topic carry-over, |Δρ1| ≈ .015-.024. The gust field is white on average with a
  textured split: sparse constructs bounce, content constructs carry over slightly.
- PANDORA m ≥ 5 (29 texts, 95 pairs; wide null [−.74, −.53]): axes −0.797/−0.805
  (p < .0005) and several constructs SATURATE the MA(1) boundary (wcl_02 −0.846; in the
  m ≥ 4 arm wcl_36 −0.995, wcl_11 −0.976, novelty −0.967) while wcl_11 FLIPS from −0.203
  (m 5-12) to −0.976 (m 4-12) — arm-flipping plus ρ1 ≈ −1 signals near-deterministic
  window ALTERNATION, i.e., FORMAT PERIODICITY (quote/reply and list structure in long
  Reddit comments), not an MA(1) gust field. Register-local texture (consistent with
  T6); psychology NOT claimable; format-aware windowing = new open instrument.

**W2b — corrected separation + bounce factor (Essays, 1,349 texts, 8,793 windows).**
- **B̂ ≈ 0**: diag mean −0.0103 against Γ̂0 diag ≈ 0.73 (implied mean θ ≈ .014);
  per-construct implied θ nonzero for 10/19, led by wcl_60 = .43 (diag method — cruder
  than W2a's .09, same unique flag), wcl_23 = .10, tension = .07.
- **Bounce factor: DOES NOT EXIST** — λ1(−B̂) = .175 with permutation p = .98 (observed
  SMALLER than 98% of order-permutation draws), half-replication .108, congruence with
  Γ̂0 = .026. Registered lean (c) wrong on every gate — coherent with W2a: no common
  bounce structure because the average memory is zero.
- Corrected flow: λ1(Σ̂_flow) = .0307 (comparator without the 2Γ̂0/(m−1)² subtraction:
  .1036 — the drop is removal of gust inflation, not of B contamination, since B̂ ≈ 0),
  half-replication .308, bootstrap point-below-CI bias noted by the executing agent —
  **flow remains UNCERTIFIED on Essays** with the correct machinery.
- P9 status: the F12.2 downgrade STANDS (it is a theorem). B̂ ≈ 0 was measured on Essays
  and by T6 must not be transported to Reddit; PANDORA's own long-text dynamics are
  non-white and format-suspect — so the P9 flow factor stays CONDITIONAL on iid gusts,
  now with the added note that the one measurable register shows B ≈ 0.

**F12.3 scorecard.** (a) WRONG as leaned — axes white; the designed alternative (strike
E3) is what fired; wcl_60 the exception at θ̂ .09 (below the leaned [.1,.5] band edge).
(b) "rises" WRONG (premise of large negative B false); "replication < .5" RIGHT (.308).
(c) WRONG on all gates. (d) stands. Net theory movement: one wrong claim deleted (E3
bounce), three anomalies unified (wcl_60), the gust model cleaned to
white-with-textured-exceptions, and the flow estimator's audit machinery (exact
inversions) now standing equipment.

## F11 results (V6-E1..E4, run AFTER registration commit 8e2b0ba, same day)

**E1 — gust robustness (PANDORA m=3, n=618; gust1 recomputed, leads wcl_02/wcl_11).**
Temporal median split: congruence .956 / .971, cross .864 — TIME-ROBUST. User-demeaning:
.982 — person effects irrelevant (as registered: within-comment object). Scale 64 tokens:
.622 — persists attenuated (upper edge of the registered .4–.6 band). Venue classes: the
two classes with n ≥ 140 replicate at .926 / .896; the two with n ≤ 75 fail (.173 / .147)
— POWER vs true heterogeneity UNRESOLVED at this n (recorded; the registered ≥ .6 lean is
therefore only partly right).

**E2 — Essays transport (2,309 essays m ≥ 2, median m = 5, 12,039 windows; loader reads
user_id/text ONLY).**
(a) Position: first_person lin −1.058 (p < .0005) TRANSPORTS, and gains significant
negative curvature on long essays (−0.447, p < .0005 — fast early drop); tension closing
rise present but attenuated (+0.078, p = .0005) — the registered "attenuates or vanishes"
was half right; directive SIGN-FLIPS (+0.142 close-elevated on Essays vs opening-elevated
in the PANDORA m=3 stratum) — genre-dependent, consistent with the earlier
stratum-dependence flag; wcl_22 curvature also flips sign across corpora.
(b) Law-of-the-wall: composite CV gain ≈ 0 or negative for 12/13 highlight constructs —
registered lean WRONG. Position structure is real (a) but explains a SMALL share of
within-essay window variance; single-coordinate models suffice at current SNR; the
matched-asymptotics reading stays a metaphor, not a fitted necessity.
(c) Gust structure exists on Essays (gust1_E λ = 1.598, replication .933) but is
statically VISIBLE (2.236) and first_person-led — no statically invisible gust factor
found on Essays.
(d) **HEADLINE BET FAILED AS REGISTERED-KILLABLE: gust1_E × gust1_P = .200 (random
baseline ≈ .23) — the PANDORA gust factor is REGISTER-SPECIFIC, not corpus-general.**
(e) Essay-level flow-only (invisible) factor: NOT found (lean WRONG) — instead the
statically VISIBLE motion factors TRANSPORT ACROSS CORPORA: D-comp1_E × D-comp1_P = .940,
D-comp2 × best = .782; static frames rank-1 congruence .923. Flow certification fails on
Essays (λ₁(Σ̂) = .109 below its own bootstrap band, replication .098).

**E3 — gust dynamics (Essays m ≥ 4, 1,805 texts; PANDORA m ≥ 4 descriptive).**
AR(1) of gust projections: −0.314 (gust1_E) / −0.339 (gust1_P) vs within-text pairing
null [−0.21, −0.17], p < .002 — gusts are ANTI-PERSISTENT beyond the detrending baseline:
overshoot-then-compensate at adjacent windows (MA(1)-like bounce; the microstructure
analogy sharpens — negative lag-1 autocorrelation is the bid-ask-bounce signature).
Registered "white" lean WRONG in an informative direction. CAVEAT: OLS-detrending
leverage geometry contributes to adjacency structure and this null does not fully remove
it — flagged; a leverage-free redesign (second-difference prewhitening) is the follow-up.
The position-magnitude arm is INCONCLUSIVE BY DESIGN FLAW (endpoint leverage mechanically
shrinks endpoint residuals; observed edge−interior −0.22 is confounded) — recorded, not
interpreted.

**E4 — person-level retry (PANDORA).** REGISTERED LEAN CONFIRMED: the F10.8 phase-C death
was a power artifact. Gate ≥ 5 residualized (static congruence ≤ .03 by construction):
comp2 λ = 1.641, half-replication .777; comps 3/4/6 replicate .60–.64. Gate ≥ 8
residualized comp1: λ = 2.137, replication .784, loadings {wcl_35 +.45, wcl_22 −.42,
wcl_07 +.41, tension +.40} — the recurring motion cluster, now established as a
PERSON-LEVEL, statically invisible, replicating individual-difference dimension.

**F11 synthesis (the V6 empirical laws).**
1. LAYERED MOTION: level Π / drift Σ_flow / gust Γ each carry factor structure.
2. **PORTABILITY FOLLOWS VISIBILITY** (new empirical law, falsifiable): motion factors
   WITH level shadows transport across corpora (.94/.78); statically INVISIBLE structure
   is register-local (gust1: robust within Reddit — time .96, users .98, scale .62, large
   venues .9 — yet .20 across corpora). Math similarity: integrated covariance
   (fundamental, portable) vs microstructure noise (market-specific) in
   realized-covariance theory. Falsifier: an invisible factor that transports.
3. GUSTS BOUNCE: anti-persistent adjacent-window dynamics (with the leverage caveat).
4. PERSON MOTION-STYLE EXISTS: statically invisible, replicating at .6–.78 — a new
   individual-difference layer, readable only in motion (occasions-cheap, tokens-hungry
   per the F11.5 economics).
5. POSITION IS REAL BUT SMALL at window granularity, and genre-bends (directive/wcl_22
   sign flips) — position-conditional norms must be corpus-anchored.

The V6 document (SUICA_THEORY_V6.md) carries the full synthesis, the mathematical
similarity table, and the personality-inference extension.
