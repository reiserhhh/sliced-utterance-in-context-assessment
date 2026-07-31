# V8-HJIC-1A Replicated Relational-Lift Support

Status: `PROSPECTIVE_SYNTHETIC_PROTOCOL__TRUTH_LOCKED_FROM_LICENSE`

## 1. Correction to HJIC-1

HJIC-1 incorrectly required almost every shared-latent world to issue a
structural license. Shared latent variation is not sufficient for finite-sample
identification. The corrected target is:

\[
\Pr\left(
  \operatorname{corr}
  \left(
    \widehat R^\times,
    R^\star
  \right)\ge .80
  \mid \delta_{\mathrm{relation}}=1
\right)\ge .95.
\]

The synthetic truth \(R^\star\) is opened only after the observable license
\(\delta_{\mathrm{relation}}\) has been frozen. A minimum license rate prevents
the rule from passing by refusing every world.

## 2. Replicated estimator

Let \(B^{(1)},B^{(2)}\) and \(M^{(1)},M^{(2)}\) be independent text-derived
views of two readout families. Declared nuisance \(Z\) is residualized by
cross-fitting. Marginal replicated covariance is:

\[
\Sigma_B^\times
=
\frac{
  \operatorname{Cov}(B^{(1)}_\perp,B^{(2)}_\perp)
  +
  \operatorname{Cov}(B^{(2)}_\perp,B^{(1)}_\perp)^\top
}{2},
\]

with an analogous definition for \(\Sigma_M^\times\). The cross-family object
is:

\[
C_{BM}^\times
=
\frac{
  \operatorname{Cov}(B^{(1)}_\perp,M^{(2)}_\perp)
  +
  \operatorname{Cov}(B^{(2)}_\perp,M^{(1)}_\perp)
}{2}.
\]

The full-axis relation matrix is:

\[
R_{ij}^\times
=
\frac{C_{BM,ij}^\times}
{\sqrt{\Sigma_{B,ii}^\times\Sigma_{M,jj}^\times}}.
\]

## 3. Observable support

Whitening is not performed in every numerically positive direction. For each
margin, replicate two is independently permuted relative to replicate one.
The 99th percentile of the null maximum eigenvalue defines a support floor.
Only observed eigenvectors above that floor are retained.

The retained bases \(U_B,U_M\) are then frozen. The supported operator is:

\[
\mathcal K^\times
=
\left(U_B^\top\Sigma_B^\times U_B\right)^{-1/2}
U_B^\top C_{BM}^\times U_M
\left(U_M^\top\Sigma_M^\times U_M\right)^{-1/2}.
\]

Bootstrap and cross-family permutations reuse the frozen bases. No latent
rank, oracle relation, or truth norm participates in support selection.

## 4. Two licenses

The relation license requires:

- condition-permutation \(p\le .01\);
- a top supported singular value above permutation and bootstrap uncertainty;
- independent author-split stability of text relations, anchor relations, and
  their cross-match;
- cross-replicate directional agreement and a bootstrap confidence cone of at
  least `.80`;
- valid supported whitening;
- no collapse after declared nuisance conditioning;
- no raw-versus-conditioned Simpson reversal.

The unique-mode license additionally requires:

\[
\sigma_1(\mathcal K^\times)-\sigma_2(\mathcal K^\times)
>
2\epsilon_{\mathrm{op},.95}.
\]

Thus a relation matrix may be licensed while its dominant axis remains
unidentified.

## 5. Registered worlds

| World | Required behavior |
|---|---|
| `SHARED_LATENT` | Relation and separated dominant mode may be licensed; licensed relations must match locked truth |
| `LOW_SINGULAR_GAP` | Relation may be licensed, but a unique mode must be refused |
| `COMMON_NUISANCE` | Relation refused after cross-fit conditioning |
| `CORRELATED_REPLICATE_ERROR` | Within-replicate shared error must not create a cross-replicate license |
| `SIMPSON_MIXTURE` | Reference-sensitive reversal refused |
| `PRIVATE_AXES` | Stable margins without a cross-family relation refused |

## 6. Frozen gates

- `SHARED_LATENT` relation license rate is at least `.20`.
- `SHARED_LATENT` unique-mode license rate is at least `.80`.
- Among licensed `SHARED_LATENT` worlds, truth fidelity at least `.80` occurs
  in at least `.95` of repetitions.
- Maximum relation-license rate across the four negative worlds is at most
  `.05`.
- `LOW_SINGULAR_GAP` relation-license rate is at least `.80`, while its
  unique-mode license rate is at most `.05`.
- Observable licensing reads synthetic truth in exactly zero repetitions.

## 7. Boundary

This is a theorem-directed synthetic identifiability battery. It can validate
the logic of replicated support, relation refusal, and mode refusal. It cannot
name a relation, establish human personality validity, replace same-person
multi-condition data, or show that a real embedding has the simulated error
structure.
