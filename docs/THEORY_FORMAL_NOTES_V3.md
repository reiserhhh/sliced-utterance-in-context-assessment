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
