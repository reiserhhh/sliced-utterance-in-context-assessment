# V8 Persistent Incidence Multiplicity Report

Code-gate status: `V8_INCIDENCE_MULTIPLICITY_PLANTED_PASS`

Independent methodology audit: `PARTIAL`

Canonical run:
`results/v8_incidence_multiplicity/v23_final_20260726/`

## Research question

When author response trajectories meet in a shared latent space, does the
intersection identify a common response mechanism, and does the number of
trajectories through an intersection measure similarity?

The result is conditional. Intersection multiplicity alone is not a
similarity measure. A useful candidate relation requires the same authors to
form a condition-matched common intersection across a nontrivial range of
uncertainty radii and conditions, while remaining specific relative to a
population-wide common anchor. The current refusal gate separately requires
stable population-level pair geometry across independent views.

## Estimand

For author \(u\), shared condition \(z\), let
\(\widehat\sigma_u(z)\) combine cross-view dispersion and residual scale.
The implementation freezes the condition-specific population radius

\[
\widehat r(z)=\operatorname{median}_u\widehat\sigma_u(z)
\]

and uses the isotropic uncertainty ball

\[
T_u(z,\epsilon)
=
\left\{
y:
\|y-\widehat f_u(z)\|_2
\le \epsilon\widehat r(z)
\right\}.
\]

A set of authors \(H\) is an incidence hyperedge only if all uncertainty
tubes share one common point:

\[
\bigcap_{u\in H} T_u(z,\epsilon)\ne\varnothing.
\]

Its multiplicity is \(m(H)=|H|\). Its pair-specific contribution is
downweighted by

\[
s(H)=\frac{n-|H|}{n-2},
\]

so a common anchor containing all \(n\) authors contributes zero
pair-specific evidence. A population group claim additionally requires at
least two components of multiplicity at least three whose union covers at
least 75% of authors.

## Registered result

The V2.3 run used 24 authors, four planted groups, 65 conditions, two text
halves, two observers, 120 calibration repetitions per world, 160 untouched
confirmation repetitions per world, and separate challenge and sensitivity
seed blocks.

| Gate | V2.3 result |
| --- | ---: |
| Minimum clear-world co-membership AUC | 1.000 |
| Minimum clear-world median F1 | 1.000 |
| Minimum clear-world median ARI | 1.000 |
| Minimum clear-world group-claim rate | 0.950 |
| Multiplicity median absolute error | 0.000 |
| Condition localization error | 0.0255 |
| Minimum cross-view Spearman | 0.8485 |
| Worst per-null-world false-claim upper 95% | 0.0185 |
| Isolated-transverse claim upper 95% | 0.0185 |
| Attack refusal rate | 1.000 |
| Minimum fresh-challenge AUC | 1.000 |
| Fresh-challenge non-refusal rate | 1.000 |
| Condition reparameterization consistency | approximately 1.000 |

All five registered null worlds had 0/160 group claims separately. All
observer-only, half-only, condition-permuted, and partial-support attacks
were refused.

## What the number of connected trajectories means

| World | Raw maximum multiplicity | Recovered multiplicity | Group claim |
| --- | ---: | ---: | ---: |
| Regional planted groups, 2D/3D | 6 | 6 | 1.00 |
| Tangent nonlinear planted groups | 6 | 6 | 1.00 |
| Common anchor plus planted groups | 24 | 6 | 0.95 |
| Global common anchor only | 24 | 3 local median | 0.00 |
| Isolated transverse contacts | 6 | 3 local median | 0.00 |
| Pair-map equivalence control | 4 | 1 | 0.00 |

The contrast is decisive:

- multiplicity 24 can mean only that every author shares one condition
  anchor; it need not contain any pair-specific or group-specific relation;
- multiplicity 6 can recover a planted common-response group when the same
  membership persists over conditions, radii, halves, and observers;
- isolated transverse contacts can rank planted pairs almost perfectly
  (AUC 0.997) but still fail to form a stable population partition;
- local triplets exist inside null worlds, but they do not repeat as a
  population-covering system.

The information-bearing object is therefore not an intersection point or
its degree alone. It is the signature

\[
\mathcal I_H
=
\left(
H,\ z,\ m(H),\
\rho_\epsilon,\
\rho_{\text{view}},\
\tau_{\text{tangent}},\
s(H),\
\kappa_{\text{coverage}}
\right),
\]

where \(H\) is membership, \(\rho_\epsilon\) is scale persistence,
\(\rho_{\text{view}}\) is population-level cross-view stability,
\(\tau_{\text{tangent}}\) describes local co-motion, \(s(H)\) is population
specificity, and \(\kappa_{\text{coverage}}\) records whether local
hyperedges assemble into a population structure. In V2.3,
\(\tau_{\text{tangent}}\) is a recorded diagnostic rather than a group-claim
gate, and \(\rho_{\text{view}}\) is a global pair-score Spearman statistic
rather than per-hyperedge membership replication.

## Interpretation

The planted result supports this narrow mathematical proposition:

> Persistent, condition-matched, population-specific incidence can identify
> shared latent response mechanisms even when a population-wide intersection
> is uninformative.

This makes stable incidence hyperedges plausible candidates for
personality-relevant similarity, because they describe authors who respond
similarly under the same conditions rather than authors who merely use
similar words. It does not yet show that they are personality signals.
External psychological or behavioral validation is required before that
name is available.

Conceptually, the intersection is an observable event produced by similar
conditional response operators:

\[
\text{operator similarity}
\longrightarrow
\text{persistent incidence pattern}
\longrightarrow
\text{candidate author relation}.
\]

The causal arrow cannot yet be reversed in real text.

## Correction trail

- V2 used the largest local null hyperedge to calibrate a threshold and
  suppressed the tangent world.
- V2.1 calibrated population-level claims and recovered the tangent world,
  but a pooled null bound hid 8/160 false claims in the common-anchor world.
- V2.2 corrected to per-world null bounds, but only 80 calibration trials
  made the 0.03 upper-bound gate mathematically unreachable even at zero
  errors.
- V2.3 raised calibration to 120 trials, added a pre-run power check, froze a
  new seed, and passed the untouched confirmation panel.

The rejected results remain part of the audit trail and are not headline
evidence.

## Limits

- This is a planted-world identification result, not real-text validity.
- Calibration uses known synthetic group labels; a real unsupervised
  threshold procedure remains open.
- The implemented uncertainty sets are pooled isotropic balls, not
  author-specific full-covariance Mahalanobis tubes.
- Tangent compatibility is recorded but not used by the frozen group
  decision, and hyperedge membership is not yet replicated separately in
  each view.
- Complete-link clustering proposes candidate common balls but does not
  enumerate every possible subset. Across conditions and radii, selected
  hyperedges are joined by transitive closure; a future chain-of-hyperedges
  null must test whether this can bridge distinct mechanisms.
- Nominal results are at noise SD 0.03. The regional group remained
  recoverable at 0.06, but the common-anchor-plus-groups world refused at
  0.06 and both clear worlds included in the sensitivity panel refused at
  0.12. At noise 0.01, common-anchor-plus-groups also refused because its
  near-degenerate pair rankings reduced cross-view Spearman. This
  non-monotone refusal behavior is a known boundary, even though it fails
  closed rather than making a false group claim.
- The registered worlds cover affine, quadratic tangent, RBF nonlinear, 3D,
  heteroskedastic, and several attack geometries, not arbitrary manifolds.
- The nonlinear challenge is not fully model-agnostic: its RBF form is
  approximable by the frozen polynomial/RBF fitting basis. Rank
  reparameterization consistency is also guaranteed largely by the
  rank-coordinate design and is a sanity check rather than independent
  evidence.
- V2 through V2.3 form an adaptive method-development sequence over the same
  broad simulator family. Fresh seeds prevent direct reuse of observations,
  but a future independently designed generator family is still needed to
  test simulator-family overfitting.
- No result establishes personality, compatibility, diagnosis, clinical
  meaning, or interpersonal affinity.
- A fitted whole-map integrated-distance baseline also reaches AUC 1.0 in
  every clear and challenge world. V2.3 has not established incremental
  information beyond ordinary trajectory distance.

## Next empirical bridge

The next valid step is not to name the hyperedges. It is to estimate the same
incidence signature in held-out, same-condition human texts and test:

1. whether hyperedge membership repeats across independent text halves;
2. whether it survives opportunity, prompt, language, and observer controls;
3. whether within-hyperedge authors are closer on external psychological or
   behavioral criteria than matched nonmembers;
4. whether the relation adds information beyond whole-map distance.

See `reports/V8_INCIDENCE_MULTIPLICITY_INDEPENDENT_AUDIT.md`.
