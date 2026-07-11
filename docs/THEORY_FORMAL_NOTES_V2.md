# SUICA Theory Formal Notes v2 — F7–F9: invariance, aggregation geometry, spectral nulls

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

## Status

F7–F9 are formal apparatus plus first instantiations, all three computed label-free on
Tier-U (T-GEO-P1/P2/P3; ledger rows carry the authoritative numbers).

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
