# Paper 2 Skeleton — The Motion Layer of Text: Spectral Texture, Fluid Factors, and
# What a Single Document Can Measure

Created 2026-07-12 (end of the overnight V6 program, cycles F10→F12/W9). Status:
skeleton for the SECOND paper; the JPA manuscript (paper 1, v5.7) is untouched. All
claims below are ledger-traceable; every directional prediction was registered and
committed before its run.

## One-paragraph thesis

Personality-from-text research reads LEVELS — averages over a person's words. We show
that text also carries a MOTION layer: ordered drift along a document, transient
co-fluctuation (gusts) with construct-specific spectral texture, and person-indexed
factor frames — and that this layer is (i) mathematically separable from levels by
exact contrast identities, (ii) partly invisible to any level-reading instrument
(questionnaires included) as a theorem, not a metaphor, (iii) governed by a
measurement economics that makes single long documents informative about motion but
never about norm-referenced levels, and (iv) estimable only through well-conditioned
spectral functionals, for which we ship a tested open-source estimator suite.

## Section plan

1. INTRODUCTION — from levels to paths (paper 1 recap: choice/base/signature; the
   fluidity conjectures F10).
2. MODEL — (M'''): w_k = level + k·drift + gust; AR(2)-textured gusts ⊕ non-nested
   MA-echo class; position profiles by shape class (flow / boundary / flat).
3. THEOREMS (with proofs; the mathematical core) —
   T1 aggregation kills motion at 1/m ("stop and the coherence disappears");
   T2 exact contrast identification (ℓ/q algebra);
   T3 support identifiability (deep interiors license the flow coordinate);
   T4 measurement economics (occasions vs tokens);
   T5 nameability (condition-invariance ∧ person-sharedness);
   T6 portability follows visibility (empirical law with falsifier);
   T7 spectral texture (estimable functionals; exact invariants ρ1(Δ²) = −2/3,
   MA(1) ⇒ ρ_{π/2} = 1; finite-n centering corrections incl. d(3) = 56/9;
   per-functional conditioning).
4. INSTRUMENT SUITE — Δ² prewhitening; exact moment inversions Γ̂0/B̂; hybrid
   spectral shape pair (ρ_{π/2}, ρ_π); AR(2) triangle fit; all with
   composition-corrected calibration tables and power annotations.
5. FINDINGS (Essays primary; PANDORA where in scope) — see evidence table below.
6. THE ARTIFACT CHAPTER (methods contribution in its own right) — OLS-leverage
   pseudo-bounce (E3, struck by W2a); centering near-null direction (lag coordinates
   ill-posed → estimable functionals); extraction-cap artifact stratum (PANDORA m ≥ 4
   is non-prose; pipe tables); the power-annotated kill adjudication (wcl_60).
7. PERSONALITY INFERENCE — person tuple (μ, shape, style, U); motion styles as
   statically invisible replicating individual differences (rep .78); licenses (all
   Tier-U; trait links require new seals); AI-native reading (machine coordinates).
8. LIMITATIONS & THE NATIVE CORPUS — register anchoring (T6); single-text sufficiency
   instrument awaits many-long-texts-per-person data; person-level texture stability
   untested.

## State of evidence (headline table; ledger rows in parentheses)

| claim | status |
|---|---|
| Motion-only coherence exists (gust factor: supra-edge, person-disjoint rep .829, level-invisible, vocab-disjoint) | CONFIRMED, register-local (F10.8/T-GEO-P9; T6 via V6-E2: cross-corpus .200) |
| Portability follows visibility (level-shadowed motion factors transport .94/.78) | CONFIRMED as empirical law with falsifier (V6-E2) |
| Person-level motion style (statically invisible individual differences) | ESTABLISHED within-register, rep .777/.784 (V6-E4); portability untested |
| Gust memory: faint positive corpus mean, CI-solid (+.030 [.014, .048]) | CONFIRMED after exact centering-bias correction (W3; naive negative was artifact) |
| Memory taxonomy: decaying carry-over / one-step echo / sparse bounce | CONFIRMED construct-by-construct across two leverage-free instruments (W2a×W3×W4) |
| Even-lag structure at both signs (wcl_20 a2 = +.30; wcl_07 a2 = −.16, both CI-solid) | CONFIRMED (W7 quarter-frequency + W8 triangle) |
| MA-echo class not AR-representable (echoes = worst AR(2) fits) | CONFIRMED (W8, lean d) |
| wcl_60 unifies three anomalies as sparse-burst dynamics; parametric identity | Sign facts CONFIRMED; MA-vs-AR UNDECIDED-LOW-POWER (W8, power-annotated kill) |
| "Period-2 standing wave" reading of wcl_20 | KILLED at net energy (ρ_π .77 CI-solid < 1); survives as even-lag anomaly (W6/W7) |
| E3 anti-persistence ("bounce") | STRUCK — OLS-leverage artifact (W2a) |
| PANDORA within-text dynamics | ARTIFACT-STRATUM (1,500-char cap; out of scope under frozen extraction) (W9) |
| Flow factor (ordered drift co-movement) | CONDITIONAL on PANDORA (F12.2 contamination theorem); uncertified on Essays (λ1 .031, rep .308) |

## Deployment (reproducibility core of the paper)

suica_core/motion.py: windows → exact centered moment maps → corrected inversions →
signed memory r_c → hybrid shape pair → guards (T4 economics, singularity, leak
semantics) → mandatory license strings. 72/72 tests incl. synthetic recovery at exact
reference values and the MA(1) quarter-frequency invariant. Every estimator's
finite-composition calibration is computable by the enumeration engine (shipped).

## What the paper needs before drafting

(1) Person-level texture stability on a many-texts-per-person register (native corpus
OP-36 or the market register, governance permitting); (2) the single-text sufficiency
instrument (T4's empirical face); (3) figure plan: the (a1, a2) triangle with construct
placements + CI ellipses; the shape-pair plane; the honesty table as a figure; (4)
decision: venue (BRM methods-flavored vs Assessment) after paper 1's disposition.
