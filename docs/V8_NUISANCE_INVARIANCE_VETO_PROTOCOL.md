# V8-HJIC-1B Nuisance-Invariance Veto

Status: `PROSPECTIVE_SYNTHETIC_PROTOCOL__HJIC1A_PARTIAL_PRESERVED`

## 1. Motivation

HJIC-1A correctly separated relation existence from unique-mode
identification, but falsely licensed 8 of 60 `SIMPSON_MIXTURE` repetitions.
The failed result remains preserved. HJIC-1B adds an observable veto; it does
not lower a threshold or use synthetic truth.

## 2. Symmetric condition-sensitivity statistic

For a frozen relation space:

\[
\Delta_Z=\widetilde R_{\mathrm{raw}}-\widetilde R_{\mathrm{cond}}.
\]

Global sensitivity is:

\[
\eta_Z=
\frac{\|\Delta_Z\|_F}
{\max(
  \|\widetilde R_{\mathrm{raw}}\|_F,
  \|\widetilde R_{\mathrm{cond}}\|_F,
  \tau_R
)},
\qquad \tau_R=.10.
\]

Localized sensitivity is:

\[
d_Z=\max_{ij}|\Delta_{Z,ij}|.
\]

The maximum statistic is:

\[
T_Z=\max(\eta_Z/.10,\ d_Z/.10).
\]

The symmetric denominator prevents a nearly zero conditioned relation from
creating an unbounded ratio. The cell statistic prevents a localized Simpson
effect from disappearing in a Frobenius average.

## 3. Resampling

- Author-block bootstrap moves both replicated views, anchors, nuisance rows,
  and fold assignments together.
- The nuisance residualizer is refit inside every bootstrap sample.
- The replicated support basis and relation axes remain frozen.
- Nuisance permutations move the complete nuisance row by author; columns are
  never permuted independently.
- Each permutation refits the residualizer and recomputes \(T_Z\).

Material instability requires both:

\[
\operatorname{LCB}_{.99}(\eta_Z)>.10
\quad\text{or}\quad
\operatorname{LCB}_{.99}(d_Z)>.10,
\]

and:

\[
p_{\mathrm{perm}}(T_Z)\le .01.
\]

The final relation license is:

\[
\delta_{\mathrm{final}}
=
\delta_{\mathrm{HJIC1A}}
\land
\neg I_Z.
\]

If the relation is vetoed, the unique-mode license is also zero.

## 4. Added breaking worlds

| World | Attack and required interpretation |
|---|---|
| `LOCALIZED_SIMPSON` | One relation cell is condition-sensitive; local max statistic must veto |
| `NULL_HIGH_DIM_NUISANCE` | Twenty irrelevant nuisance columns must not cause a false veto |
| `WEAK_RELATION` | Weak cross-family structure must be underresolved, not mislabeled as nuisance instability |
| `COLLIDER_OR_DESCENDANT_Z` | Conditioning induces a relation; sensitivity must veto, without calling the raw relation causal truth |

Existing shared, low-gap, common-nuisance, correlated-error, Simpson, and
private-axis worlds remain in the battery.

## 5. Frozen gates

- `SHARED_LATENT` final relation license at least `.95`, unique-mode license
  at least `.80`.
- `NULL_HIGH_DIM_NUISANCE` final relation license at least `.95`.
- Nuisance false-veto rate in both positive worlds at most `.05`.
- Truth fidelity at least `.80` in at least `.95` of licensed positive worlds;
  truth remains post-license only.
- `LOW_SINGULAR_GAP` relation license at least `.95` and mode license at most
  `.05`.
- Both Simpson worlds have instability detection at least `.95` and final
  license at most `.05`.
- Collider sensitivity detection at least `.95` and final license at most
  `.05`.
- Weak relation final license at most `.05` and nuisance-veto rate at most
  `.05`.
- Common nuisance, correlated replicate error, and private axes each have
  final relation license at most `.05`.
- Truth usage by licensing is exactly zero.

## 6. Boundary

`NUISANCE_INVARIANCE_VETO` means only that the global relation is materially
sensitive to a declared conditioning operation. It cannot determine whether
the conditioned variable is noise, a confounder, mediator, moderator,
collider, descendant, or part of the construct. A vetoed relation may still
support context-specific local relations in a separate model.
