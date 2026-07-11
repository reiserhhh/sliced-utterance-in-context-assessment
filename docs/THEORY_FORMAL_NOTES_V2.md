# SUICA Theory Formal Notes v2 — F7–F10: invariance, aggregation geometry, spectral nulls, factor fluidity

Created 2026-07-11. Extends F1–F6 (SUICA_THEORY_FORMAL_NOTES_V1.md). Source of the
mathematical apparatus: the field program's T-geometry reformulation
(trading-agent-claude, `docs/SUICA_V5_TGEOMETRY_REFORMULATION_20260711.md`, layers I–III),
ported and instantiated on PANDORA. Discipline inherited from that document: **each formal
layer must emit at least one new falsifiable instrument; anything that only renames existing
results is cut.** Empirical instantiations: results/suica_tgeo_p1_phi_linearity,
results/suica_tgeo_p2_time_reversal, results/suica_tgeo_p3_mp_edge.

## F7 — Inference as invariance: the null suite is a subgroup lattice

**Definition.** Let G act on the labeled data (user labels, condition labels, occasion
orders, half labels). A statistic carries G-signal iff its sampling distribution is not
invariant under the G-action. Every null this program has run is a choice of G:

| Our null (historical row) | Group G | Invariance asserted under H0 |
|---|---|---|
| Stranger null (OP-32, E6 v3) | derangement class of S_N | person-exchangeability of profile pairings |
| Leak-mask permutation (W-E) | S_N on survivor labels | mask sufficiency |
| Shuffled-fit null (E11) | S_N on fit targets | direction-fit exchangeability |
| Per-world seeds / sign conventions (WW suite) | (Z/2)^N sign flips | conditional symmetry of residuals |
| Contiguous-halves rule | trivial group (forbidden shuffle) | refusal to assert time-exchangeability |

**F7.1 (artifact, formal definition).** An artifact is a statistic that is constant on a
larger orbit than the analyst believed. (The field program diagnosed a live artifact this
way; upstream's E4 stranger-null lesson — react signatures absorbed by the stranger baseline
— is the same object: the "signature" statistic was nearly constant on the pairing orbit.)

**F7.2 (new instrument, ported I-1 — time-reversal null).** Author-level stationarity
asserts invariance under per-author occasion-sequence reversal (an involution). Reversal
maps each author's time slope to its negative, so the per-author sign-flip group (Z/2)^N
yields an exact null for the mean slope. PANDORA instantiation: T-GEO-P2 (K=4 equal-count
blocks, span >= 180 days; arms: pooled conditions vs top-1 condition to separate style drift
from venue-mix drift).

## F8 — Aggregation as Möbius flow: the phi-coordinate

**F8.1 (phi-linearization; theorem, ported with proof).** Let phi(r) = r/(1-r). The
Spearman-Brown family r_W = W·rho / (1 + (W-1)·rho) satisfies exactly

    phi(r_W) = W · phi(rho).

Proof: phi(r_W) = W·rho / (1 + (W-1)rho - W·rho) = W·rho/(1-rho) = W·phi(rho). ∎
Reliability lives on the projective line; rho_1 is the infinitesimal generator of a
one-parameter Möbius subgroup; the SB step-up S(r) = 2r/(1+r) is phi(S(r)) = 2·phi(r).

**F8.2 (curvature = clustered noise).** Under slice-clustered noise with cluster-shock
variance V_c (the field program's day shocks; our within-condition venue shocks), the
designed-aggregation curve is phi(W) = a·W/(1 + b·W): concave with asymptote a/b, and b
estimates the clustered-noise share. Under the parallel model b = 0.

**F8.3 (new falsifier — asymptote consistency check).** The saturating fit is itself
falsifiable: the fitted asymptote phi_max must not fall below the realized phi at large
aggregation (the full-half retest). Violation rejects the simple saturation form for that
construct (its small-W curvature is not clustered noise).

**PANDORA instantiation (T-GEO-P1, n = 2,767, label-free, nested designed subsets,
W in {1,2,4,8}, Spearman primary).** Directional expectation (F near-linear, C saturating)
did NOT hold as a family split; what the geometry actually found is finer:

| construct | fam | phi ratios W2/W4/W8 (pred 2/4/8) | fitted phi_max | full-half phi (realized) | verdict |
|---|---|---|---|---|---|
| tension_core | und | 1.29 / 1.70 / 3.63 | 0.49 | 0.46 (r=.316) | saturation model CONSISTENT — tension's ceiling is real; "no-trait" gets a geometric signature |
| first_person | F | 1.84 / 3.27 / 5.20 | 3.58 | 2.16 (r=.684) | mild curvature, consistent |
| wcl_23 | F | 2.14 / 3.90 / 6.45 | 2.18 | 1.16 (r=.537) | near-linear at small W, consistent |
| wcl_60 | F | 1.38 / 1.69 / 2.27 | 0.79 | **2.44 (r=.709) — VIOLATES F8.3** | saturation form REJECTED: small-W curvature is not clustered noise; consistent with slice-level ZERO-INFLATION (apostrophe opportunities are sparse per 128 tokens) — the v5 hurdle regime exists INSIDE PANDORA, at slice granularity, for sparse form habits |
| wcl_13 | F | 3.08 / 6.10 / 10.59 | — | — | SUPER-linear (ratios exceed the parallel bound) — W=1 noise heavier-tailed than the model admits; flagged for follow-up |
| novelty | C | 2.04 / 4.38 / 9.10 | — | — | near-linear — see F8.4 |
| wcl_02 / wcl_25 / wcl_35 | C | sub-linear (5.27 / 4.45 / 4.20 at W8) | 3.0 / 1.5 / 1.4 | 1.22 / 1.10 / 0.82 | consistent mild saturation |

**F8.4 (scope note — what phi-curvature can and cannot see).** Stable venue choice is
person-stable across halves, so for C-family constructs the choice-mediated component m_u
behaves as SIGNAL in a retest, not as clustered noise; phi-linearity therefore does NOT
detect the choice channel (novelty runs near-linear while being .59 choice-mediated). The
phi instrument reads the NOISE geometry; the purity decomposition (F3) reads the SIGNAL
provenance. They are complementary, not redundant.

**F8.5 (standing rule, adopted).** Composite constructs must be blended in phi-space, not
r-space: under independent-noise composition the additive object is phi. The frozen v4
composite weights are r-space blends; any composite refit for opening #2 derives weights in
phi first (rule recorded; frozen weights untouched).

## F9 — Spectral nulls: factor claims against random-matrix edges

**F9.1 (instrument).** For a user x construct matrix (n x p, standardized), eigenvalues of
the correlation matrix under pure noise concentrate below the Marchenko-Pastur edge
lambda_+ = (1 + sqrt(p/n))^2. A factor claim requires (i) eigenvalue above the edge —
empirical within-column-shuffle edge preferred over the analytic constant
(heteroscedasticity caveat, field round-13 N2); (ii) cross-half replication of the
supra-edge eigenvector (loading congruence).

**PANDORA instantiation (T-GEO-P3, n = 2,941 x 19).** Analytic MP edge 1.167; empirical
within-column-shuffle edge 1.169 (500 draws — heteroscedasticity mild here). **Exactly 4
components exceed the edge, and all 4 replicate across halves** (early/late eigenvector
congruence .985 / .980 / .932 / .939). The battery's factor structure is real and stable by
the RMT criterion. Follow-up target: OP-33's 48 co-selection axes (requires re-scoring).

## F10 — Factor fluidity: the frame as a field (proposed 2026-07-11, user conjecture)

**Motivating conjecture (user, verbatim intent).** Factors are not fixed; they FLOW with
conditions (time, position within a text, venue — to be explored). If so, factors likely
cannot be NAMED, but they take on a stronger role as AXES OF INDIVIDUALITY.

**Context from F9.** T-GEO-P3 already constrains this: the population between-person frame
is time-stable at half scale (4 supra-MP factors, early/late congruence .93–.99). So if
flow exists, it must live (a) at finer condition scales than the half split, or (b) at the
PERSON level — each person carrying their own frame — which is exactly where the conjecture
points ("individuality as axes"). The population average frame can be rigid while the
person-level frames disperse and drift.

**F10.1 (frame field).** For a condition variable t (time block, text position, venue), let
C(t) be the between-person correlation operator of the battery and V_k(t) ∈ Gr(k, p) the
span of its top-k eigenvectors — a point on the Grassmann manifold. Factor FIXITY (H0) is
the assertion that t ↦ V_k(t) is constant up to sampling noise; per F7 this is invariance
of the chordal distance d(V_k(t), V_k(t')) = sqrt(k − ||V_tᵀV_t'||²_F) under the group that
permutes condition labels within person. Factor FLOW is rejection of that invariance.

**F10.2 (nameability criterion).** An axis is eligible for a NAME only if the frame is
(i) condition-invariant (F10.1 H0 holds over the tested t) and (ii) person-shared (the
person-indexed frames U_u concentrate near a common point of the Grassmannian). If (i) or
(ii) fails, the surviving invariants are the eigenvalue spectrum and the person-level frame
itself: the axis stops being a population construct and becomes a personal quantity. This
gives mathematical form to the program's standing rule that vectors are not entitled to
names by default (vector interpretation unlicensed until calibrated).

**F10.3 (individuality as axes).** Person frame: U_u = leading eigenvector (or top-k frame)
of person u's WITHIN-person slice correlation. The conjecture's positive content: U_u is
trait-like — orientation, not only scores, is a personal signature. If it holds, the SUICA
person representation extends from the score vector f_u to the pair (f_u, U_u) ∈ R^p ×
Gr(1, p), and interperson distance gains a principal-angle term. Deployment is AI-native by
construction: an axis needs no name to be used.

**F10.4 (instruments and falsifiers — predictions REGISTERED BEFORE the runs).**

| instrument | design | registered prediction | falsifier |
|---|---|---|---|
| T-GEO-P4 time flow | P2 block design (K=4, span ≥180d), per-block between-person corr, top-4 chordal distance d(1,4) + path length; null = within-user block-label permutations (500); arms pooled/top1 | NO detectable flow beyond null at block scale (P3 constraint); if pooled flows but top1 does not → venue-mix flow, mirroring P2 | flow detected on top1 arm would OVERTURN the fixed-population-frame reading of F9 |
| T-GEO-P5 position flow | comments ≥288 tokens: open = first 128, close = last 128 tokens; per-construct paired mean shift (user-level primary) + open/close frame distance; null = per-comment open/close swaps, (Z/2)^N | mean-level shifts exist (hunches, stated for honesty: directive_action higher at close; first_person higher at open); frame rotation small | large frame rotation would relocate "style trait" claims to position-conditional claims |
| T-GEO-P6 personal axes | per user per half: leading eigenvector of within-person slice corr (gate ≥12 slices/half; top1 arm ≥8); self early↔late |cos| vs stranger null (cyclic-shift derangements, F7 row 1); noise ceiling = within-half odd/even split; SHARP arm: residualize slices against the population top-4 frame first | self > stranger raw AND residualized (γ-channel precedent: E6 v3 profile signatures); early↔late ≈ odd/even ceiling (frames stable, no strong within-person drift) | **the conjecture DIES if residualized self ≤ stranger** (personal frames = noisy copies of the shared frame); early↔late ≪ odd/even ceiling would instead CONFIRM temporal flow of personal frames |

**F10.5 (stated caveats, before results).** (a) P4 block means have heteroscedastic noise
across blocks (slice counts vary within user); the exchangeability null is approximate.
(b) P6 person frames are estimated from ~21 slices per half; estimation noise is symmetric
between self and stranger pairings, so the comparison remains valid, but congruence
magnitudes are attenuated — the odd/even ceiling is the honest yardstick. (c) P5 "position
in text" is confounded with discourse function (openings and closings do different jobs);
this instrument reads the confound deliberately, as a first probe. (d) All three are
label-free Tier-U; no seals, no frozen objects touched.

## F10 results (T-GEO-P4/P5/P6, run AFTER the registration commit 60ce99c, same day)

**P4 — time flow of the population frame: PREDICTION HELD (rigid).** Pooled arm
(n = 4,454): D14 = .2848 vs null mean .2603 (p = .342); PATH = .8248 vs .7624 (p = .244).
Venue-held arm (n = 3,278): D14 = .2266 vs .2457 (p = .662); PATH p = .096. No movement
beyond the within-user block-permutation null at block scale — consistent with F9's
early/late congruence .93–.99. λ spectra flat across blocks.

**P5 — position flow: prediction PARTLY WRONG (frame rotation is real).** 21,496 comments
≥ 288 tokens (3,614 users; frame cohort 1,380 users ≥ 5 comments). Frame: chordal(open,
close) = .4919 vs swap-null p95 .3475 (p < .002); per-PC best congruence [.965, .940,
.732, .780] — PC1/PC2 position-invariant, PC3/PC4 REORIENT, while eigenvalue spectra
barely move (orientation shifts, strength does not). Mean shifts (user level, close −
open): first_person −0.687 (p < .0005; registered hunch CONFIRMED — openings are
first-person territory), tension +0.055 (p < .0005), directive +0.026 (p = .104 —
registered hunch FAILED, recorded); wcl_36/54/22/15/25 lower at close, wcl_02 higher.

**P6 — personal axes: CONJECTURE SUPPORTED; kill condition NOT triggered.** Pooled arm
(n = 2,430 users, ≥ 12 slices per half):

| variant | self | stranger | p | ceiling early/late (odd-even) |
|---|---|---|---|---|
| raw | .2567 | .2237 | < .0033 | .2554 / .2508 |
| residualized (pop top-4 projected out) | .2769 | .2155 | < .0033 | .2805 / .2917 |

Self-congruence sits AT the odd/even ceiling → within-person frame rotation is at most
mild (the ceiling uses half-sized estimates, so exactly zero is not claimable — a
φ-correction of frame congruence is the natural F8×F10 follow-up). The decisive row is
the residualized one: the self−stranger gap WIDENS (.061 vs .033) after the shared
four-factor frame is projected out — personal orientation is not a noisy copy of the
population factors. Venue-held arm (n = 938, ≥ 8 slices): raw ns (.204 vs .199,
p = .173) but residualized significant (.2435 vs .2078, p < .0033) — within a single
venue the personal orientation appears once the shared frame is removed. Alignment
dispersion: median best |cos| of personal axes vs population PC1–4 = .4929 (IQR
.394–.598) against a random-direction median .3332 (p95 .5475); best-match shares
.42/.27/.17/.14 across the four PCs — the population frame describes individual frames
poorly.

**F10 verdict.** The population frame is rigid in time (P4, confirming F9); position
within a text bends the third and fourth axes while leaving the first two and the
spectrum intact (P5); and the person-level frame is a stable, individually informative
orientation that the population factors do not capture (P6). Nameability (F10.2) fails at
clause (ii) — person-sharedness — exactly as the conjecture proposed: the axes' role
shifts from named population constructs to carriers of individuality. The F10.3
representational consequence now has empirical backing: (f_u, U_u) with a principal-angle
term is a licensed exploratory object. Naming individual axes remains UNLICENSED (the
E11-v2 calibration rule applies unchanged); all congruence magnitudes are attenuated by
~21-slice-per-half estimation and only ORDER claims (self vs stranger, self vs ceiling)
are made.

**F10 follow-ups (ledger-noted).** (a) φ-correct the odd/even ceiling to bound true
temporal rotation of personal frames; (b) identify WHICH loadings move in the PC3/PC4
position reorientation; (c) position-conditional scoring (open/close as micro-registers)
as parallel-form material; (d) whether personal-axis geometry carries Tier-L signal —
requires a NEW seal (NOT opening #2's registered candidates); deferred.

## Status

F7–F9 are formal apparatus plus first instantiations, all three computed label-free on
Tier-U (T-GEO-P1/P2/P3; ledger rows carry the authoritative numbers). F10 was registered
as conjecture + instruments + falsifiers at commit 60ce99c BEFORE the runs; T-GEO-P4/P5/P6
results above landed the same day (ledger rows TGEO-P4/P5/P6). The manuscript carries the
compact version (exploratory subsection + A.7(iv), v5.6, EN/JA/ZH).

**T-GEO-P2 result (time-reversal drift, K=4 blocks, span >= 180 days, sign-flip null 2000
draws).** Pooled arm (n = 4,454): first_person mean slope −0.224/yr (p < .0005), directive
−0.036 (p < .0005), tension −0.016 (p < .0005), novelty ns. Venue-constant arm (top-1
condition, n = 3,278): **first_person −0.247/yr (p < .0005) — the drift survives holding
the venue fixed**, i.e., it is within-person change, not venue-mix change; tension and
directive lose significance (their pooled drift WAS venue-mix drift — the two-arm design
separated the channels as intended); novelty +0.015 (p = .049, borderline). Reading:
first_person shows the classic maturation pattern — rank-order stable (raw .68) with
mean-level decline — which is what a genuine trait-like quantity does in longitudinal
personality data; it also marks a boundary condition for within-person monitoring (L1):
drift must be modeled, not assumed away. Nothing here touches frozen batteries, seals, or
labels. The wcl_60
F8.3 violation is the headline theoretical yield: it independently rediscovers, from pure
aggregation geometry, the zero-inflation phenomenon that motivated the v5 hurdle formula —
two instruments, two registers, one mechanism.
