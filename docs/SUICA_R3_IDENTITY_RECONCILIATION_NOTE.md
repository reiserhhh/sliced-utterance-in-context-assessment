# R3 — the identity reconciliation note

Planner derivation, 2026-08-19, discharging the debt the R-line's close
named: "the typology-η identity and the style-channel identity are
different formal objects; the reconciliation derivation precedes any
registration" (`SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md`, phase close).
This note IS that derivation. It registers nothing; it makes a future R3
leg registrable without committing the #59 class of error (degenerate
estimand/antecedent). Numeric checks: scratchpad, three claims verified
to 3 decimals; the note states each check inline.

## 1. The two objects, restated with provenance

- **η-identity (L-line).** World: x = μ + τ_g + b + s + ε with the type
  layer τ_g as signal and identity b as interference. Decomposition
  (L-plan, C-arm definition): b = √(1−η)·b_iso + √η·b_aligned, with
  b_aligned supported on the type-discriminative subspace T (dim d_T)
  and b_iso isotropic in card space (dim D). **η is a GEOMETRIC
  parameter: the aligned fraction of identity variance.** The taxometer
  η̂ (L3) is certified ±0.125 with median error 0.024 across the η grid
  INCLUDING η = 0 — so η̂ reads ≈ 0 on isotropic identity even though a
  realized isotropic vector has raw aligned share ≈ d_T/D > 0.
  Formalization adopted here: **η̂ is an EXCESS-alignment reader**,
  η̂ ≈ (raw share − d_T/D)/(1 − d_T/D). Numeric check: pure isotropic
  reads −0.0001; η ∈ {.25, .5, .75} read {.2515, .4981, .7521}.
- **Style-channel identity (R-line).** World: `build_split_world_v2`
  plants style_a — one vector per author, entering the RESPONSE path at
  the trait's emission site with weight w_style (units of w_mu),
  card-visible, author-persistent, NON-TRAIT (R1b certified;
  frame-crossing and gauge-invisible, R2; taxed ~12× cheaper than state
  content, R2b). **Style-identity is a SEMANTIC/CHANNEL type: which
  content class carries the per-author offset**, with no geometric
  commitment — style_a is drawn isotropically with respect to any type
  structure.

The name "identity" is overloaded across a TWO-AXIS space:

| | trait-borne | non-trait |
|---|---|---|
| **aligned with T** | within-type trait residue | b_aligned (L-line's η-carrier) |
| **isotropic** | — (trait lives in trait axes) | style_a (R-line's channel); b_iso |

η̂ reads the ROW margin (excess alignment, blind to semantics). T6″ and
the completeness meter read PERSISTENCE (the union of every cell —
anything author-stable and card-visible). The trait partial (labels)
reads the COLUMN margin. **No single program instrument reads a cell.**
The 4W theory's Id(u|F) (eq 10) is the union object — what T6″
certifies — and both named identities are its components separated by
(alignment, semantics).

## 2. The composition theorem

Point η̂ at a v2-class trait/style mixture whose per-author persistent
card content is c_a = w_mu·trait-residue_a + w_style·style_a (+ any
L-style b). Because style_a is isotropic, it contributes ONLY to the
isotropic pool; the excess-aligned pool is untouched. Writing V_al for
the excess-aligned variance and V_iso for the total isotropic variance
before style:

    η_read(w_style) = V_al / (V_al + V_iso + w_style²·V_s)

For the clean case (identity b with parameter η₀, style with variance
matched to b): **η_read(w) = η₀ / (1 + w²·V_s/V_b)** — a hyperbolic
dilution with NO free parameters once the v2 certificates pin V_s/V_b.
Numeric check at η₀ = 0.6: read {.5994, .4803, .2983, .1198} against
predicted {.60, .48, .30, .12} for w ∈ {0, .5, 1, 2}.

## 3. The two forgery directions (#59, now precise)

1. **Style masks typedness (low-η̂ forgery).** A strongly typed world
   plus a heavy style channel reads LOW η̂ — the isotropic bath dilutes
   the excess share hyperbolically. "η̂ low" therefore licenses
   "typology-applicable" ONLY after a style audit (T6″-vs-η̂ contrast,
   §4). The L3 certification never met this case: L-worlds had no
   non-trait isotropic channel beyond b_iso itself.
2. **Trait residue fakes aligned identity (high-η̂ forgery).** Pure
   within-type trait dispersion — no identity of ANY kind — is aligned
   with T by construction and reads η̂ = 1.0 (numeric check: exactly
   1.0). "η̂ high" therefore licenses "aligned identity interference"
   ONLY after the trait column is removed or priced (the labels-side
   partial, or a trait-frozen world arm).

Both directions are instances of one sentence: **η̂ is a geometry
reader, not a semantics reader; the two named identities differ on the
axis η̂ cannot see.**

## 4. What the other instruments measure on mixtures

- **T6″ (frame-refreshed discriminator):** the union channel — it
  RISES with w_style while η̂ FALLS. This signed dissociation is the
  instrument-level signature that the two identities are different
  axes, and it is the registerable centerpiece below.
- **Completeness meter:** prices the union variance (w_mu² + w_style²
  pools jointly); its propagation law (L3) is alignment-blind and
  should transport to mixtures unchanged — a checkable invariance.
- **Whitening-shape precondition (L3):** style inflates the isotropic
  spectrum, changing the whitened shape; η̂'s certified bias budget
  holds only within a bounded style share. A validity bound in
  w_style²·V_s/(V_b+V_iso) must be measured, not assumed.

## 5. Registerable predictions (named, NOT queued; a future R3 leg
registers against this note)

- **P1 (dilution seal):** η̂ on v2 mixtures follows
  η₀/(1 + w²·V_s/V_b) with all constants pinned by existing
  certificates — a parameter-free curve, D1-seal class.
- **P2 (signed dissociation):** across the same w grid, T6″
  discrimination strictly rises while η̂ strictly falls — the formal
  home of the program's real-data dissociation family.
- **P3 (validity bound):** the L3 bias budget (±0.125, +O(0.05) pole)
  holds up to a measurable style-share threshold; beyond it the
  whitening precondition fails in a stated direction.

## 6. The real-text shadow

The dissociation family (S1's γ = 0; SR2's trait-silent taste; U3's
trait-silent When coordinates; the S-line/U-line typology-ablation
asymmetries) is this two-axis structure observed in the wild:
re-identification instruments read the union channel; trait coupling
reads the trait column; a carrier can be strong on one axis and silent
on the other because the axes are orthogonal by construction, not by
accident. The reconciliation therefore does not merely license R3 — it
gives the program's most-replicated empirical pattern its formal
statement: **"identity without personality" is not a paradox; it is the
off-diagonal of a 2×2 the instruments were never able to read as one.**

## 7. Status

The #59 debt named at the R-line close is DISCHARGED. A future R3 leg
(η̂ + T6″ + completeness meter against v2 style/trait mixtures, cells
keyed on P1–P3) is now registrable; it is NOT registered today. No
existing number changes; no instrument is re-certified by this note.
