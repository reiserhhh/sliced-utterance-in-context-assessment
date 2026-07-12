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

## F12.4 — Exact finite-n correction of the centered moment estimators (derived and
## registered 2026-07-12, before the W3 run)

**Derivation (Fable, closed form; the deployed estimator centers D2 within text, which
biases the naive inversion — quantified exactly here).** With n = m−2 D2 rows per text
and MA(1) gusts, D2 is MA(3) with autocovariances (all linear in γ0, γ1):
c0 = 6γ0 − 8γ1, c1 = −4γ0 + 7γ1, c2 = γ0 − 4γ1, c3 = γ1, c_h≥4 = 0. Within-text
centering subtracts the mean D2, and the pooled centered moments have EXACT expectations

    Ā(n) = (4γ0 − 4γ1)/n²        A_end(n) = (3γ0 − 4γ1)/n   [n ≥ 4]
    E[S0](n)    = (6 − 4/n²)·γ0 + (−8 + 4/n²)·γ1
    E[symS1](n) = (−4 + 2(n−2)/(n²(n−1)))·γ0 + d(n)·γ1,
        d(n) = 7 − 4/n² for n ≥ 4;  d(3) = 56/9  [BOUNDARY CORRECTION]

CORRECTION (caught post-registration by the deployment agent's independent derivation,
confirmed by direct n = 3 enumeration and 1.5M-text Monte Carlo): the closed-form
simplification of A_end dropped the c3 clip at n = 3 — the lag-3 term cannot enter the
boundary sum there, so A_end(3) = (3γ0 − 5γ1)/3 and d(3) = 56/9, not the formula's
59/9 (a, b, c are exact at all n ≥ 3). The registered verification constants (n = 6)
are unaffected; the W3 Essays re-inversion, whose largest stratum is m = 5 (n = 3), was
RERUN with the exact d(3) and the recorded numbers below are the corrected-formula ones.

(mixed corpus: pool the coefficients with row weights n_t for S0 and pair weights
n_t − 1 for symS1). The identities are linear with the SAME scalar coefficients for
every matrix entry, so the corrected multivariate inversion is the 2×2 solve
(Γ0, B) = M(m-composition)⁻¹ (S0, symS1). VERIFICATION VALUES (to be reproduced by the
executing agent): at θ = .4, m = 8 (n = 6): E[S0] = 9.9867, E[symS1] = −7.3440; the
NAIVE inversion on these gives θ̂ = 0.4408 — matching the deployment agent's empirical
0.44–0.45; at θ = 0, m = 8 the naive B̂ bias is −0.0178·γ0.

**Quantitative consequence registered as a prediction:** W2b's Essays B̂ diag mean
(−0.0103, with Γ̂0 ≈ 0.73 and mixed m 5–12) is CONSISTENT WITH PURE CENTERING BIAS AT
θ = 0 (predicted ≈ −0.013·0.73/0.73-scale). W2a is unaffected (its simulation null ran
the same centered pipeline — internally consistent by construction).

**W3 registered leans (BEFORE the run).** (i) Synthetic θ = .4, m = 8: naive θ̂ =
0.4408 ± sampling (validating the closed form); corrected recovers 0.40. (ii) Essays
re-inversion with the corrected map: mean diag B̂ moves to ≈ 0 (|mean| < .004); the
small-θ constructs (tension .070, wcl_23 .103, wcl_54 .057) shrink by more than half;
wcl_60 stays clearly positive (corrected diag θ̂ ≥ .25). KILL: if the corrected Essays
B̂ mean does not move toward 0, the "W2b's tiny negative B̂ is centering artifact"
reading is wrong. (iii) Deployment: motion.py's inversion switches to the corrected
solve (naive kept as an option for comparability); the documented bias note becomes a
resolved item.

## F12.5 — Lag-2 identities: MA-vs-AR discrimination (registered 2026-07-12, before W4)

**The gap.** The signed memory coefficient r = B/Γ0 cannot distinguish a one-step MA
echo (γ_h = 0 for h ≥ 2) from a decaying AR carry-over (γ_h = φ^h γ0). Lag-2 structure
can.

**F12.5.1 (general identity).** The uncentered Δ² autocovariance sequence is the
fourth-difference filter applied to the gust autocovariance sequence:
S_h = Σ_l [1, −4, 6, −4, 1]_l · γ_{h+l−2}. In particular S2 = γ0 − 4γ1 + 6γ2 − 4γ3 + γ4
(this reproduces S0 = 6γ0 − 8γ1 + 2γ2 and S1 = −4γ0 + 7γ1 − 4γ2 + γ3 as the h = 0, 1
cases). Under MA(1), γ_{h≥2} = 0, so S2 is EXACTLY PREDICTED by the identified pair:
S2_pred = Γ0 − 4B (entrywise, symmetrized).

**F12.5.2 (discriminator).** R2 ≡ S2_obs − S2_pred(Γ̂0, B̂), all three moments taken with
their EXACT within-text-centering corrections. Under MA(1), E[R2] = 0; under AR(1) with
small φ, R2 ≈ 6φ²γ0 > 0; R2 < 0 falls outside both one-parameter families (→ MA(2)+).
METHOD NOTE (the d(3) lesson): centering-corrected coefficient maps for S0/S1/S2 are to
be computed by EXACT ENUMERATION (Toeplitz covariance of the D2 rows under the
hypothesized γ-structure, centering projection P = I − J/n, read the pooled moments), not
by hand-simplified closed forms. S2 pairs exist for n ≥ 3 (n − 2 per text).

**F12.5.3 (per-construct scalar overidentification).** For each construct, fit both
one-parameter families to the centered (S0, S1, S2)_cc diagonal triple — MA(1): (γ0, θ);
AR(1): (γ0, φ), the AR map computed by exact enumeration from the AR(1) Toeplitz — and
compare overidentification residuals (2 parameters, 3 moments, 1 dof each).

**W4 registered leans (BEFORE the run).** (a) Corpus-mean diag R2 slightly POSITIVE
(bootstrap CI excluding 0 on the positive side) — the carry-over decays over more than
one window. (b) Content carry-over constructs (wcl_35, wcl_36, wcl_03, first_person,
wcl_13) classify AR-type (R2 > 0; AR fit beats MA). (c) wcl_60 classifies MA-type
(burst-echo is one-step: R2 ≈ 0; MA fit beats AR). KILL semantics: R2 ≈ 0 everywhere →
MA(1) suffices and the AR extension is REJECTED on parsimony; widespread R2 < 0 → both
families fail and the model moves to MA(2)+.

## F12.6 — The gust ladder: lag-structure inversion and the period-2 question
## (registered 2026-07-12, before W5; REFINES the W5 sketch in F12.5 results)

**Design correction (recorded).** F12.5's closing line proposed lag-3 as the period-2
separator (γ3 < 0 under oscillation). That works only for PHASE-LOCKED alternation. The
observed wcl_20/22 shape (lag-1 ≈ 0, lag-2 large positive) fits an AR(2)-even process
(x_k = a2·x_{k−2} + η, a1 ≈ 0 — a damped standing wave), which predicts γ3 ≈ 0 and
γ4 = a2·γ2 > 0; MA(2) predicts γ3 = γ4 = 0. The general instrument is therefore the
LADDER INVERSION, not one more residual.

**F12.6.1 (instrument).** Extend the exact-enumeration centering maps to S3 and S4
(lag-h pairs need n ≥ h+1; lag-4 draws only on m ≥ 7 texts, ≈ 1.1k pairs — thin,
declared). Build the exact centered 5×5 linear map (γ0..γ4) → (S0..S4) from the pooled
n-composition (unit-vector enumeration; report the condition number), invert for the
GUST LADDER γ̂0..γ̂4 per construct (assuming γ_{h≥5} = 0), bootstrap over texts for CIs.
Also report the Nyquist spectral value f(π) = γ0 − 2γ1 + 2γ2 − 2γ3 + 2γ4 (period-2
energy) per construct.

**F12.6.2 (classification by ladder shape).** MA(2) echo: γ3, γ4 ≈ 0 with γ2 > 0.
Damped standing wave (AR(2)-even): γ4/γ2 = a2 ∈ (0, 1), γ3 ≈ 0. Phase-locked
alternation: γ3 < 0. AR(1) carry-over: geometric ladder γ2/γ1 ≈ γ1/γ0. MA(1): ladder
dies after lag 1.

**W5 registered leans (BEFORE the run).** (a) wcl_20/22: γ2 CI-solid positive AND
γ4 > 0 with γ4/γ2 ∈ (0.1, 0.9) — the damped-standing-wave reading (a sustained ~2-window
≈ 256-token rhythm; guess: paragraph-scale alternation), rather than MA(2) (γ4 ≈ 0).
(b) wcl_60: ladder confined to lag 1. (c) wcl_35/36/13: geometric-ish decay consistent
with their AR φ̂ ≈ +0.1. (d) The 5×5 inversion is expected ill-conditioned at high lags
(centering attenuation grows with h) — if the bootstrap CIs on γ3/γ4 are too wide to
classify, the verdict is INDETERMINATE-AT-THIS-N, recorded as such (no forcing).
KILL: γ4 CI-solid NEGATIVE for wcl_20/22 would reject both registered families and
reopen the model class.

## F12.7 — The normalized Nyquist ratio: a one-number dynamics fingerprint
## (registered 2026-07-12, before W6)

**Definition.** ρ_π ≡ f(π)/γ0, the period-2 spectral energy relative to total gust
variance. Exact reference values: white = 1; MA(1) memory θ: ρ_π = (1+θ)²/(1+θ²)
(bounce θ = .4 → 1.69; carry-over θ = −.4 → 0.31); AR(1) φ: ρ_π = (1−φ)/(1+φ)
(φ = +.1 → 0.82); AR(2)-even a2: ρ_π = (1+a2)/(1−a2) (a2 = .4 → 2.33). One number
separates bounce/alternation (> 1), carry-over (< 1), white (= 1).

**Resolution of the W5 units puzzle (prediction, not post-hoc):** W5's RAW f_π ranked
wcl_60 lowest — but wcl_60 is the certified bouncer, which must have HIGH relative
Nyquist energy; its low raw value reflects a small γ0 in pooled-standardized units.
Under normalization the ranking must INVERT for wcl_60. Estimation: f_π and γ0 via the
exact left-functionals of the centered moment map (the W5 left-solve is well-conditioned,
|v| ≈ 4.1, unlike the ladder coordinates); graceful degradation to a lag-2-truncated
functional when lag-3/4 pairs are scarce (flagged mode).

**W6 registered leans (BEFORE the runs).** Essays, normalized ratios with bootstrap CIs:
(a) wcl_60 ρ_π > 1, CI-solid (bounce; ≈ 1.4–1.7 at its θ̂ ≈ .23–.34). (b) The carry-over
set (wcl_35/36/13, first_person, wcl_03) ρ_π < 1 (≈ .8–.95). (c) wcl_20 and tension
ρ_π > 1 (the period-2 flag, now in the right units). (d) Deployment: motion.py gains
period2_energy (normalized ρ_π per construct) with synthetic tests recovering the four
reference values above. KILL: wcl_60 ρ_π ≤ 1 CI-solid would contradict its certified
bounce and reopen the wcl_60 story.

## F12.8 — The spectral shape pair: mid-frequency separator and the hybrid functional
## (registered 2026-07-12, before W7)

**Definitions.** f(π/2) = γ0 − 2γ2 + 2γ4; ρ_{π/2} = f(π/2)/γ0; shape pair =
(ρ_{π/2}, ρ_π); Δ_shape = ρ_{π/2} − ρ_π. Exact references: white (1, 1), Δ = 0.
MA(1) ANY θ: ρ_{π/2} = 1 EXACTLY (γ2 = 0) — a sharp invariant. AR(1) φ:
ρ_{π/2} = (1−φ²)/(1+φ²) ≈ .98 at φ = .1, so Δ_shape ≈ +.16 > 0. AR(2)-even a2:
ρ_{π/2} = (1−a2)/(1+a2) — strongly depressed. Even-lag anomaly (γ2 > 0) hits ρ_{π/2}
directly: Δ_shape is pushed NEGATIVE. So the sign of Δ_shape separates carry-over
(positive) from even-lag anomaly (negative), and ρ_{π/2} = 1 tests pure-MA(1) stories.

**Hybrid functional (deployment fix, from the W6 conditioning findings).** Numerator
spectral functionals (f_π, f_{π/2}) from the 5-moment left-solves (|w| ≈ 4, conditioned);
the DENOMINATOR γ0 from the truncated-3 left-solve (|w| ≈ 5.8) — per-functional
conditioning discipline. Prediction: the hybrid restores the deployed AR(2) m = 8
calibration toward the asymptotic value (the executing agent computes the exact expected
value of the shipped estimator and asserts against IT, per established practice).

**W7 registered leans (BEFORE the runs).** (a) Essays: carry-over set (wcl_35/36/13,
first_person, wcl_03) Δ_shape > 0. (b) wcl_20/22: Δ_shape BELOW the carry-over set's,
lean CI-separable at least against wcl_35; ρ_{π/2} depressed. (c) wcl_60: ρ_{π/2} ≈ 1
(pure-MA(1) invariant); CI-solid deviation from 1 would break its one-step-echo story.
(d) Deployment: hybrid mode ships with the shape pair as "spectral_shape_by_construct";
all reference invariants tested (MA(1) ρ_{π/2} = 1 exactly is the cleanest new test).
KILL: wcl_20 Δ_shape ≥ the carry-over set CI-solid would kill the even-lag-anomaly
reading as well, reopening the model class for W4's R2 excess.

## F12.9 — The signed two-parameter unification: AR(2) texture triangle
## (registered 2026-07-12, before W8)

**Claim.** The four observed gust textures are regions of ONE family: AR(2) gusts
x_k = a1 x_{k-1} + a2 x_{k-2} + eta on the stationarity triangle. Carry-over =
(a1 > 0, a2 ~ 0); bounce = (a1 < 0); interleaved carry-over / period-2 = (a1 ~ 0,
a2 > 0); damped period-4 = (a1 ~ 0, a2 < 0). MA(1) is NOT nested — genuine one-step
echoes must FAIL the AR(2) fit, which retests W4's MA-vs-AR verdicts from a new angle.

**Instrument (W8).** Per construct, fit (a1, a2) to the THREE hybrid estimable
functionals (signed memory r_c, rho_pihalf, rho_pi) by grid least squares over the
stationarity triangle (references exact via Yule-Walker + the enumeration engine's
exact-on-composition expected functionals); 3 moments, 2 parameters, 1 dof —
overidentification residual = the fit gate. Bootstrap CIs on (a1, a2) and residual.

**W8 registered leans (BEFORE the run).** (a) wcl_35/36/13: a1 ~ +0.1, a2 ~ 0, small
residual. (b) wcl_20: a1 ~ 0, a2 ~ +0.15; wcl_07: a1 ~ 0, a2 ~ -0.15..-0.2; both small
residuals (the family's raison d'etre). (c) wcl_60: WORST overid residual of the 19
(genuine MA bounce, not AR-representable) — this is the sharp test. (d) first_person /
wcl_03 (one-step echoes): residual larger than the carry-over set's. KILL: if wcl_60
fits AS WELL as the median construct, W4's MA-vs-AR distinction was noise and the
taxonomy collapses to AR(2)-only.

## F12.10 — Format-aware windowing: lifting or confirming the PANDORA flag
## (registered 2026-07-12, before W9)

**Question.** W2a flagged PANDORA's long-comment dynamics as uninterpretable (rho1(Delta2)
saturating toward -1, theta boundary hits, wcl_11 arm-flip) with QUOTE/LIST FORMAT
PERIODICITY as the suspected mechanism. W9 tests the mechanism directly: strip Reddit
formatting (quote lines starting with ">"/"&gt;", list markers, code fences/inline code,
collapsed whitespace) BEFORE tokenization, re-window, re-run the leverage-free Delta2
dynamics on the same texts; plus a format census (quote/list/code line shares by length
stratum).

**W9 registered leans (BEFORE the run).** (a) The raw arm reproduces W2a's numbers
(anchor; assert direction and magnitude within bootstrap noise). (b) Format census:
formatting is CONCENTRATED in long comments (m >= 4 share >> m = 2-3 share). (c)
Stripping moves the gust-axis rho1(Delta2) TOWARD the iid band by at least half the
excess and reduces theta-saturation counts — the format hypothesis. KILL: if the
stripped dynamics are UNCHANGED (excess persists), the format hypothesis dies and
PANDORA long comments carry genuine extreme register texture (the flag then becomes a
finding). (d) Cohort shrinkage after stripping is expected and reported (quotes removed
-> shorter texts); conclusions stay diagnostic at this n (~50-70 texts), stated.

## F13 — EXPL-3: do motion-layer features add exploratory detection power?
## (registered 2026-07-12, before the run; operator-ordered)

**Question (operator).** How much did detection power improve v4 -> v5 -> V6? Confirmed-
tier power is deliberately unchanged (no new seal). v4 -> v5 exploratory weight-fit was
+51% (.0902 -> .1361, EXPL-2 arm C). V6's contribution is UNMEASURED — EXPL-3 measures it
on the SAME spent opening-#1 labels under the same governance (exploratory banner; gate
replicated verbatim; H2/H6 reproduced to < 1e-9 BEFORE any fitting; ledger row; no new
labels; Essays confirm half untouched).

**Feasibility pre-check (measured label-free, recorded).** tier_l_comments is 1,500-char
capped like Tier-U (max = 1500; 7,047 at exactly 1500) — so m >= 3 windows are
prose-impossible (93 users have any); the V6 feature set REDUCES to the slope/position
layer on m = 2 long texts (open/close pairs): 10,300 texts across 1,050/1,412 Tier-L
users (median 5 per user; 715 users >= 3, 541 >= 5). Spectral texture (r_c, rho_pi,
shape pair) is NOT computable for labeled users under the frozen extraction — the cap
consequence reaches the detection question itself, and is part of the answer.

**Feature set (per user, over their m >= 2 long texts; axes estimated on TIER-U data
only — no label leakage).** (1) mean close-open 19-vector projected on the PANDORA
slope factors D-comp1/D-comp2 (P8-cache recomputation) and on the A-comp3 motion-cluster
axis; (2) per-construct mean diffs for first_person / tension / directive / novelty;
(3) mean OPENING-window first_person level (position-conditional level); (4) log1p
n_long_texts + coverage indicator; mean-imputation for users without coverage.

**Arms.** C = EXPL-2 union anchor (must reproduce .1361 exactly from its artifact);
D = C + motion features; M = motion features alone. Per-trait RidgeCV (EXPL-2 protocol),
plus a single-feature x trait screen on covered users.

**Registered leans.** Delta(C -> D) mean r in [+.005, +.02] (orthogonality bounds the
add); ONE single-feature surprise |r| >= .10 in Agreeableness or Openness from the
motion set; M alone in [.03, .07]. KILL: Delta <= 0 means the position/slope layer adds
NO exploratory signal at this cap — recorded as the honest v4->v5->V6 detection verdict.

## F15 — W10: the anatomy of the invisible factor (registered 2026-07-12, before run;
## operator focus: "what interests me most is the properties of motion-only factors")

**Known properties (consolidated).** Stable (person-disjoint rep .78-.83); theorem-
invisible to averaging instruments (T1); register-local (T6: .20 cross-corpus; and
Essays hosts NO invisible gust factor — all its gust components are level-visible);
carried by the recurring cluster {wcl_02, wcl_07, wcl_11, wcl_20(, tension, wcl_22,
wcl_35)} — the SAME constructs flagged for anomalous spectral texture (wcl_20 even-lag,
wcl_07 period-4). NEW HYPOTHESIS registered: the invisible factor is a SHARED RHYTHM
component — the cross-construct face of the individual spectral anomalies.

**Instrument (W10, on existing caches; uncapped upgrade after N1).**
(a) ACTIVATION ANATOMY: per-window gust1_P activation (within-comment detrended
residual projected on the axis) correlated with LOADING-EXOGENOUS window markers:
question density, quote-character share, digit share, comma density, novelty_play level
and its window-to-window jump (topic-shift proxy), and window position — what is
textually happening when the factor fires.
(b) PERSON SUSCEPTIBILITY: per Tier-U user with >= 2 m=3 comments: split-half stability
of mean |activation| (susceptibility) and of mean signed activation (directionality).
(c) ESSAYS CONTRAST: same activation machinery on Essays windows via gust1_P — expected
near-chance variance ratio (the factor should barely exist there).

**Registered leans.** (a) activation is question/quote-marker enriched (the
conversational-burst reading of the Reddit-local factor) and topic-shift adjacent
(positive |activation| x novelty-jump); position effect weak. (b) susceptibility
split-half r >= .3 (a stable person property — the first PERSONAL trait-like quantity of
a motion-only object); signed directionality weaker but > 0. (c) Essays activation
variance ratio ~ 1 vs its own shuffle (factor absent). KILL: susceptibility r < .1 would
demote motion-only structure to comment-level texture with NO person anchoring — the
"person x register" reading would lose its person half.

## F15 results (W10, run AFTER registration 52421ea; alignment asserts 43,818/43,818
## and 12,039/12,039 rows; axis drift guard passed {wcl_02 −.47, wcl_11 +.45})

**(a) Activation anatomy — registered lean WRONG in an informative direction.** The
factor does NOT fire on question/quote markers; it fires on EMPHATIC/NUMERIC bursts:
allcaps token share r_centered = .161 (perm p < .002), digits/100 chars = .127
(p < .002); question/quote markers weaker. Reading: gust1 = bursts of shouty/numeric
texture (score-talk, emphasis) coordinated across the style clusters. CAVEAT
(recorded): estimated on the capped m >= 3 stratum (687 texts), which borders the W9
format-dense band — the digit enrichment may be partly stratum texture; the N1 uncapped
re-run adjudicates.

**(b) Person susceptibility — the headline: the first person-anchored trait-like
quantity of a motion-only object.** Split-half r of mean |activation| = **.441**
(clears the registered >= .3 lean; ICC-share .381; n = 81 users, capped-corpus-limited).
Signed DIRECTION r = −.128 — my "weaker but positive" lean WRONG: people are stable in
HOW STRONGLY they gust, not in which direction. Susceptibility is an amplitude trait.
KILL (r < .1) not fired.

**(c) Essays contrast.** PANDORA activation variance ratio 1.678 (p < .005) vs Essays
1.035 (p = .005) — direction as registered; Essays carries a whisper, not zero (flagged
rather than rounded down).

**Consolidated portrait of the motion-only factor (operator's question).** A register-
local, averaging-invisible coordination of style clusters that fires in emphatic/numeric
bursts; individuals differ stably in its AMPLITUDE (susceptibility .44) but not its
direction; essentially absent in solitary stream-of-consciousness writing; its carrier
constructs are the same ones bearing anomalous spectral texture (shared-rhythm
hypothesis, still open — uncapped data next).

## F14 — The N-program: building the comparison substrate (registered 2026-07-12,
## operator-ordered "execute the native corpus etc.")

**Mandate.** EXPL-3 showed the comparison substrate itself is missing: the 1,500-char
extraction cap blocks the motion layer for labeled users. Three tracks, all frozen-
object-safe (parallel NEW artifacts only):

**N1 (uncapped parallel re-extraction).** The RAW dump (all_comments_since_2015.csv,
5.3 GB) is uncapped (sampled max 29,189 chars; > 1,500 in 1.1% of comments). Re-extract
Tier-L and Tier-U comment sets with the v2 rules MINUS the cap (sanity cap 30,000 chars,
documented) into NEW files tier_{l,u}_comments_uncapped_v1.parquet. Frozen v2 artifacts
untouched. Diagnostics: per-tier m-distribution; texture-capable coverage (m >= 3 / 5 /
7) among gated opening-#1 users. LEANS: >= 60% of gated users gain >= 1 text with
m >= 5; >= 30% gain >= 3 such texts.

**EXPL-4a (Essays dev half; the motion-layer x questionnaire test the cap denied us).**
Single-essay motion features (slope vector projections + q-contrast gust magnitudes +
where m >= 5 crude spectral values) vs Big5 on the DEV half only — the split rule read
from the seal documents; confirm-half labels remain UNTOUCHED (opening budget 1 intact);
exploratory banner. LEANS: any single motion feature |r| >= .08 in <= 3 of 50 cells;
incremental over a level-feature baseline in [+.00, +.02]; honest coin-flip overall.

**EXPL-4b (after N1): uncapped Tier-L motion features x spent opening-#1 labels** under
the EXPL-3 triple-assert governance, now WITH the spectral layer where per-user data
permits. LEAN: Delta over EXPL-3's D in [+.000, +.015]. STANDING KILL: if 4a and 4b both
land <= 0, the conclusion "questionnaire-criterion insensitivity to the motion layer"
becomes the recorded verdict pending BEHAVIORAL criteria (the native corpus's job).

**N4 (native corpus collection instrument, OP-36 execution to the autonomy boundary).**
Deliver the ready-to-run collection pack per SUICA_NATIVE_CORPUS_DESIGN_V1: bilingual
prompt battery (Arm A free / Arm B fixed + AI-interview script per Rulebook G), session
protocol (2 x 2, >= 2 weeks), assistant-echo monitor spec, data schema, anonymization
plan. Participant recruitment and IRB are operator-side by nature and are the ONLY
missing pieces after this deliverable.

## F13 results (EXPL-3, run AFTER registration 36293aa; all governance gates passed
## before fitting: gate n=1,058, H2/H6 to <1e-9, EXPL-2 anchor .1361 exact)

**Numbers.** Coverage 787/1,058 users (74.4%; median 4 long texts). Arms: C = .1361
(anchor), D = C + 10 motion features = **.1370 (Delta +0.0009)**, M = motion alone =
.0300 (Openness-carried, +.127). Single-feature screen 10x5: **zero |r| >= .10 hits**;
closest = open_first_person -> Neuroticism +.096.

**Adjudication.** Lean 1 MISSED LOW (+.0009 vs the [+.005, +.02] band; the Delta <= 0
kill does not fire by letter, but the practical verdict is the kill's spirit: NO
MEANINGFUL ADD). Lean 2 FAILED (no single-feature hit; the near-miss is in the wrong
trait). Lean 3 at the band's lower edge (.0300). Mechanistic reading: the one
label-relevant position feature (open_first_person -> N +.096) is plausibly the H2
signal (first_person -> N +.111) REPACKAGED through the position lens — its content was
already in arm C. This is theory-consistent: components with level shadows were already
captured; the level-orthogonal motion components carry no measured trait signal here.

**The v4 -> v5 -> V6 exploratory detection ledger (spent labels, weight-fit tier):
.0902 -> .1361 (+51%) -> .1370 (+0.7%).** Confirmed tier unchanged throughout (2/7 at
opening #1; no new seal). CRITICAL SCOPE NOTE: the 1,500-char cap makes the V6 SPECTRAL
layer (r_c, rho_pi, shape pair) uncomputable for labeled users — EXPL-3 measured only
the position/slope layer. The honest summary: V6's contribution to DETECTION on PANDORA
is ~nil; V6's contribution is new measurement objects (motion styles, frames, texture)
whose trait relevance is untestable on this corpus and awaits the native corpus and a
new seal.

## F12.10 results (W9, run AFTER registration e2b2240; anchors bit-exact twice —
## cache dynamics = W2a to 0.0e+00, raw rebuild = P8 cache to 0.0e+00)

**Lean (b) FAILED INVERTED; lean (c)'s KILL FIRED ON THE LETTER; and the executing
agent's provenance dig found the true mechanism, which the registered taxonomy missed.**
The registered stripper (quotes/lists/code) was a no-op: 0 of 72 long texts contain even
one such line; stripped dynamics identical (excess −.1199 vs −.1194; saturations 7 = 7).
The registered format hypothesis is dead AS TAXONOMIZED.

**The actual mechanism — CAP-ARTIFACT STRATUM (provenance evidence, all numeric).**
(i) Tier-U bodies are hard-truncated at 1,500 characters at extraction
(extract_suica_tier_u_comments_v2.py:67); 21,733 of 35,181 candidates sit at exactly
1,500. (ii) Normal prose runs ~4.8 chars/token, so m ≥ 4 (512+ tokens) within 1,500
chars is DEFINITIONALLY IMPOSSIBLE FOR PROSE; the cohort's chars/token median is 2.48
(min 1.02) vs 4.79 in the m = 2–3 stratum. (iii) The stratum is populated by
punctuation-dense formats: markdown pipe TABLES (pipe-line share > .5 in 14/72 texts,
mean share .194 — column-periodic, a textbook Δ²-saturation generator) and other
dense-format objects. VERDICT: the PANDORA m ≥ 4 stratum is an extraction-cap artifact,
not a register: **all PANDORA within-text dynamics claims (the W2a PANDORA arm, E3's
PANDORA descriptive) are retroactively marked ARTIFACT-STRATUM — neither psychology nor
"register texture"**. Standing rule: PANDORA within-text dynamics are OUT OF SCOPE under
the current frozen extraction (re-extraction would touch frozen prep — not done); the
native corpus carries the dynamics program.

**Additional fragility caught by the anchor:** gust1_P's PANDORA θ̂ swings 0.02 ↔ 0.48
purely on the pooled-sd convention (per-arm vs full-cache) at n = 69 — dynamics
conclusions on that axis were standardization-dependent, consistent with the
artifact-stratum verdict.

**Scorecard.** (a) anchors ✓✓ bit-exact; (b) inverted (formatting ABSENT from the long
stratum — because the long stratum is not prose at all); (c) kill fired as registered,
and the mechanism FAMILY (format periodicity) is vindicated under the corrected
taxonomy (tables + cap), discovered by the agent's Reviewer-style provenance dig — the
program's clearest case of the executing agent out-reasoning the registration.

## F12.9 results (W8, run AFTER registration e04d5e0; grid 6,564 triangle points,
## five integrity asserts passed incl. white and AR(1) grid rows to 1e-9/1e-6)

**Lean (b) — the family's raison d'etre: CONFIRMED with CI-solid signs.** wcl_07
a2 = −0.16, CI [−0.28, −0.02] (damped period-4, squarely in the registered band; a1 ~ 0
as sketched). wcl_20 a2 = +0.30, CI [+0.04, +0.32] solid positive — but with an
UNANTICIPATED large a1 = +0.68 (optimum at a1+a2 = 0.98, near the stationarity
boundary): near-integrated persistence PLUS even structure, not the "interleaved" pure
a1 ~ 0 texture the lean sketched (sketch corrected, sign conclusion stands).

**Lean (d) — HOLDS emphatically and carries the MA class.** The two one-step-echo
constructs are the WORST AR(2) fits of all 19 (wcl_03 resid 0.830, first_person 0.524
vs carry-over set 0.067–0.154) — exactly what "MA(1) is not nested" predicts, delivered
where the instruments have power.

**Lean (c) FAILED as registered; the KILL fires by letter and is ruled UNDECIDABLE by
mechanism (recorded in full).** wcl_60 ranks 8/19 (ratio to median 1.18). But its
functional sds are 7–13x the field (gamma0 = 0.22 denominator; 29/300 draws dropped) —
the weighted overidentification test has NO POWER for wcl_60 (its resid CI spans
[0.003, 1.76]; under wcl_03's sds its deviations would rank worst by an order of
magnitude). Ruling: the kill predicate presupposed comparable test power, which fails;
the kill's TARGET claim ("the MA-vs-AR distinction was noise") is separately REFUTED by
lean (d). Consequence: wcl_60's PARAMETRIC identity (MA vs AR) is downgraded to
UNDECIDED-LOW-POWER; only its sign facts stand (anti-persistent lag-1, rho_pi > 1
CI-solid). Honest note: this is the program's first letter-fired kill set aside by an
explicit power argument — the reasoning, sd table, and both readings are in the JSON.

**F12.9 verdict — the unification, amended.** Gust texture = AR(2) STATIONARITY
TRIANGLE plus a NON-NESTED MA-ECHO CLASS: carry-over cluster (a1 > 0, a2 ~ 0), even
structure at both signs of a2 (wcl_20 +, wcl_07 −, both CI-solid), echoes
AR(2)-unrepresentable (worst residuals), wcl_60 bounce-region placement power-limited.
Model (M''') = level + flow + AR(2)-textured gusts (+) MA-echo exceptions — four ad-hoc
textures reduced to one two-parameter family plus one discrete class. Promoted to
THEORY V6 as T7.

## F12.8 results (W7a Essays + W7b deployment, run AFTER registration eabc17b)

**Conditioning: the registered hybrid design HELD with no fallback** (|w_pi| = 4.10,
|w_pihalf,5| = 7.05 < 20, |w_gamma0,trunc| = 5.77 on Essays; deployment m = 8: 2.09 /
4.27 / 4.07-vs-39.1 old). Two exact invariants asserted at runtime on the actual
composition (white -> (1,1,0); MA(1) -> rho_pihalf = 1) — both passed to 1e-9.

**Adjudication.** (a) Carry-over set Delta_shape > 0: 4/5 directional (wcl_36 +.094,
wcl_13 +.094, wcl_35 +.065, first_person +.048; wcl_03 the exception at −.030), none
CI-solid. (b) **wcl_20's even-lag reading CONFIRMED in the cleanest number:
rho_pihalf = 0.645 [0.428, 0.914] — CI-solid depressed**; ordering P(Delta[wcl_20] <
Delta[wcl_35]) = .912 (strong lean, short of solid), wcl_22 weaker (.756); tension shows
the same shape (Delta −.159). (c) wcl_60: rho_pihalf = 1.962 [0.898, 5.846] — CI
includes 1, the pure-MA(1) invariant SURVIVES (unstable denominator gamma0 = .22 noted;
point far from 1, undecided in the strong sense). KILL not fired.

**Unregistered finding (third consecutive poke by this family): wcl_07 is the ONLY
CI-solid Delta_shape, POSITIVE +0.540 [+0.092, +1.245]** (rho_pihalf = 1.478) —
elevated quarter-frequency with sub-white Nyquist implies gamma2 < 0 alongside positive
gamma1: a damped ~4-window (~512-token) oscillation. Post-hoc reading (labeled as such):
AR(2)-even with NEGATIVE a2 fits almost exactly ((1−a2)/(1+a2) = 1.5 at a2 = −0.2 vs
observed 1.478). Together with wcl_20 (a2 > 0, period-2) this suggests the UNIFYING
two-parameter family — signed odd-lag memory (theta/phi) x signed even-lag oscillation
(a2) — covering every texture seen so far: carry-over, bounce, period-2, period-4.
QUEUED AS W8 (to be registered before any run): joint signed-(memory, a2) fit per
construct with the shape pair + rho_ladder moments; leans to be written at registration.

**Deployment (W7b).** Hybrid denominator + shape pair shipped
("spectral_shape_by_construct", "delta_shape_by_construct", "period2_denominator",
"shape_mode"); AR(2) m = 8 calibration recovered 1.41 -> 1.75 (asymptotic 2.33; residual
gap = numerator truncation of gamma6, documented); noise roughly halved by the hybrid;
72/72 tests.

## F12.7 results (W6a, run AFTER registration ed971f1)

**Conditioning postscript (premise half-failed, registered fallback absorbed it).** The
"well-conditioned left-solve" premise holds for f_π (|w| = 4.10) but NOT for the
5-moment γ0 functional (|w| = 70.4 — it projects 0.61 onto the centering near-null
direction; wcl_60/wcl_07 got negative point γ0 and 300+ dropped draws). The registered
lag-2-truncated fallback (|w_γ0| = 5.77, cond(M3) = 110, all 19 γ0 positive) is the
HEADLINE mode; 5-moment reported for transparency. Estimable-functional discipline now
reads: check the LEFT-solve norm per functional, not per instrument.

**Adjudication (truncated headline mode, mode-corrected reference values printed).**
(a) wcl_60 ρ_π = 2.513, CI [1.280, 7.354] — **CI-SOLID ABOVE 1; the registered ranking
INVERSION happened exactly** (lowest raw f_π → highest normalized ρ_π); KILL not fired;
point above the predicted 1.4–1.7 band (wide upper CI, 40 small-γ0 draws dropped).
(b) Carry-over set below 1: wcl_35 .752 [.607, .970], wcl_36 .768 [.647, .930], wcl_13
.807 [.689, .959] CI-solid; first_person .841 [.714, 1.015] and wcl_03 .863 [.717,
1.058] directional — 3/5 solid, 2/5 grazing.
(c) **FAILED INFORMATIVELY: wcl_20 ρ_π = 0.770 [.645, .967] — CI-solid BELOW one, the
OPPOSITE side**; tension .904 spans 1. wcl_20 carries the largest absolute f_π AND the
largest γ0: its W4 lag-2 excess coexists with lag-1 carry-over that pulls net Nyquist
energy sub-white. VERDICT: the "period-2 standing wave" reading of wcl_20/22 is DEAD at
the net-energy level; what survives is an EVEN-LAG ANOMALY inside a carry-over-dominated
spectrum (W4's R2 remains a real model-misfit signal). The separator is spectral SHAPE:
f(π/2) = γ0 − 2γ2 + 2γ4 should be DEPRESSED for wcl_20/22 (positive γ2) — queued as W7.
Unregistered: wcl_23 is the only other point > 1 (1.110 [.845, 1.622]), consistent with
its W3 second-bouncer rank. Corpus mass sits at ρ_π ≈ .75–1.0 — the faint carry-over
again, now in spectral units.

## F12.6 results (W5, run AFTER registration 6669ccc; engine cross-checks to 9e-16 on
## the W3/W4 blocks; truncation aliasing quantified pre-run — f_π is the most
## aliasing-robust output, and damped alternation can flip g3's sign, both recorded)

**The registered indeterminacy scenario (lean d) FIRED — and it is structural, not
sampling.** SVD of the exact centered 5×5 map: singular values [14.9, 10.1, 4.05, 0.81,
**0.0087**]; the near-null right vector [0.61, 0.57, 0.45, 0.28, 0.12] is a smooth
"raise the whole ladder" direction that within-text centering renders nearly invisible.
Consequently the individual γ1..γ4 coordinates are unresolvable at this n for every
construct (all point ladders are near-proportional to the null vector; all CIs span 0),
the classification rule fired vacuously (19/19 "MA1" — a rule-design flaw of the
registration, recorded as such), lean (a) is unadjudicable (wcl_20/22 g4/g2 points sit
in the registered band but their CIs span everything), and the KILL did not fire.

**What IS resolved — the spectral functional.** The Nyquist energy f(π) = γ0 − 2γ1 +
2γ2 − 2γ3 + 2γ4 lies away from the null direction and is tightly estimated for all 19
constructs. Its ordering CONFIRMS the W4 period-2 flag at the functional level, with
disjoint CIs at the extremes: wcl_20 f_π = 1.033 [0.833, 1.225] and tension = 1.016
[0.806, 1.260] highest — exactly the two flagged constructs — versus wcl_60 = 0.557
[0.271, 0.965] and first_person = 0.628 [0.515, 0.744] lowest (wcl_20 vs first_person:
non-overlapping CIs).

**F12.6.3 (estimable-functional principle; theorem-grade lesson).** Under within-text
centering, gust dynamics beyond lag ~2 are ill-posed in LAG COORDINATES at feasible n
(the centering null direction); the estimable objects are WELL-CONDITIONED SPECTRAL
FUNCTIONALS of the gust spectrum (f at Nyquist and similarly placed frequencies). The
right parameterization of the motion layer's dynamic texture is frequency-domain — (r_c,
f_π/γ̂0-normalized) — not the autocovariance ladder. This is the deconvolution-style
ill-posedness → estimable-functional move, and it aligns the program with why
realized-covariance theory works with integrated spectral quantities. Deployment
increment (queued W6): expose a normalized period-2 energy in motion.py alongside the
signed memory coefficient.

## F12.5 results (W4, run AFTER registration 5064a0a; enumeration engine reproduced the
## W3 coefficient set incl. d(3)=56/9 to ≤ 9e−16; planted-recovery checks passed at
## MA θ=.4, AR φ∈{.15,.5}; centering attenuates the lag-2 map to (0.708, −3.480) from
## the uncentered (1, −4) — the enumeration mandate vindicated again)

**Scorecard.** (a) Corpus diag-mean R2 = +0.0210, frac>0 = .942, CI [−0.0052, +0.0461]
— direction as leaned, CI NOT solid: the corpus-level decaying-carry-over claim stays
directional. (b) Memory-set classification 3/5: wcl_35/wcl_36/wcl_13 AR-win with φ̂ =
+0.100/+0.095/+0.080 — cross-moment CONSISTENCY with their W3 lag-1 r_c (+0.098/+0.092/
+0.079); first_person and wcl_03 flip to MA (θ̂ = −0.085/−0.070): still positive
one-step memory, but the carry-over does NOT extend to lag 2 — a refined taxonomy:
DECAYING carry-over (wcl_35/36/13) vs ONE-STEP echo (first_person, wcl_03). Per-construct
winner calls are suggestive (all R2 CIs span 0 for these). (c) wcl_60 MA-type CONFIRMED
(second-largest margin; θ̂ = +0.235). Neither registered kill fires.

**Unregistered discovery — the period-2 signature.** The only CI-SOLID R2 constructs are
NOT the memory set: wcl_20 (R2 = +0.175, CI [+0.064, +0.283]) and wcl_22 (+0.119,
[+0.040, +0.197]) — and for both, BOTH one-parameter families fail (RSS 2–3 orders above
the well-fit constructs; fitted θ, φ ≈ 0). Weak lag-1 with large positive lag-2 is
producible by neither MA(1) nor AR(1) (AR needs γ2 = φ²γ0 bounded by the lag-1 level):
an EVEN-LAG / PERIOD-2 gust signature on Essays (tension borderline shows the same
shape, +0.085 CI [−0.013, +0.194]) — structurally reminiscent of the PANDORA
format-periodicity flag, now appearing register-internally for a construct subset.
Registered follow-up: lag-3 identity (the Δ⁴ filter at h = 3) separates period-2
oscillation (γ3 < 0 expected) from MA(2) (γ3 = 0); this is the W5 instrument. The F12.5.2
"outside both families" branch fired in the UNANTICIPATED R2 > 0 form — recorded.

## F12.4 results (W3 + bootstrap, run AFTER registration 0a4a97a; Sonnet-executed with
## independent verification — analytic re-derivation, 4M-text Monte Carlo, and an
## out-of-sample check at θ = .6, m = 10 chosen by the agent)

**The registered point lean was KILLED as written — and the sub-claim survived in a
stronger form.** Corrected inversion on Essays (1,349 texts, coefficients from the
actual n-composition: A = 5.7836, B = −7.7836, C = −3.9348, D = 6.7345 (exact d(3))):

- Corrected B̂ diag mean = **+0.0303, bootstrap CI [+0.0136, +0.0484], 500/500 draws
  > 0** — not ≈ 0 as leaned. The naive mean (−0.0103) has CI [−0.0248, +0.0054]:
  spans zero AND contains the F12.4-predicted pure-centering value (−0.0178·Γ̂0 ≈
  −0.013) — the bias formula is quantitatively confirmed on real data. Verdict: the
  naive negative WAS centering artifact (sub-claim right), but what it was hiding is
  not zero — it is REAL, MILD, POSITIVE gust memory. "White gusts" (v6.1) is revised.

- Construct-level convergence with W2a: positive with CI excluding 0 — wcl_35 +.098,
  wcl_36 +.092, first_person +.083, wcl_13 +.079, wcl_03 +.070 (the same
  content-flavored carry-over set W2a flagged on the less-negative side of its null);
  negative — wcl_60 only (r_c = −.308, CI [−.873, −.035]: SIGN solid, magnitude tail
  beyond MA(1) identifiability |r| ≤ .5, so θ-conversion of the CI is not licensed);
  13 of 19 span zero. **The two leverage-free instruments now agree
  construct-by-construct.** Per-construct registered predictions all held (tension
  .070 → .017, wcl_54 .057 → .004, wcl_23 .103 → .048, wcl_60 stays ≥ .25 at .34).

- Model revision (M″): signed-memory MA(1), θ ∈ (−1, 1] — every F12 identity is
  polynomial in θ and holds unchanged; the operational primary output becomes the
  SIGNED memory coefficient r_c = B̂_cc/Γ̂0_cc ∈ [−.5, .5) (positive = carry-over,
  negative = bounce), with θ reported only where meaningful. MA-vs-AR discrimination
  needs lag-2 moments (S2 identities) — registered as the next identifiability step.

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
