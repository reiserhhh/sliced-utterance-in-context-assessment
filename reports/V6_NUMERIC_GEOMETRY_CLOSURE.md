# SUICA V6 Numeric Geometry Closure

Date: 2026-07-14. Status: `SUPPORTED_INTERNAL_CONDITIONAL_NO_MATERIAL_MARGIN` for
static residual relational geometry; `PARTIAL_COARSE_ORDER_ONLY` for dynamic
residual geometry.

## Object and boundary

Source comments entered only once through the already frozen discovery-side
word/bigram TF-IDF to 24-SVD mapping and opportunity-conditioned residualization.
The resulting audit cache contains paired floating-point matrices only: no text,
terms, author IDs, labels, or construct names. All results below are therefore
about numeric relational structure under this representation, not semantic
interpretation.

For early and late residual matrices `R^(E), R^(L)`, the global quotient geometry
was tested by centered kernel alignment and the rank order of pairwise distances.
At scale `k`, local-to-broad relations were tested by

\[
J_k=\frac{1}{n}\sum_u
\frac{|N_k^E(u)\cap N_k^L(u)|}{|N_k^E(u)\cup N_k^L(u)|}.
\]

Every null leaves both numerical point clouds unchanged and permutes only their
early-to-late author linkage. The primary geometry audit used 999 permutations
and Bonferroni correction over 18 object-metric tests. The scale audit used
1,999 permutations and Bonferroni correction over 12 object-scale tests.

## Results

### Static residual field

- `n=1,640`, 24 observed coordinates; effective rank `16.49/16.55` and local
  intrinsic-dimension estimate `14.41/14.21` in early/late views. These are
  geometric complexity estimates, not factor counts.
- Global geometry is above the linkage null: CKA `.0396` versus null 95th
  percentile `.0113`; pairwise-distance Spearman `.2597`; all three primary
  tests have Bonferroni `p=.018`.
- It is not a stable microscopic cluster system. At `k=5`, neighbour overlap is
  not above null. It is positive from `k=10` through `k=200`; the normalized
  excess rises from `.0012` to `.0263`.
- The same broad profile survives the early/late condition-overlap sensitivity
  (`Jaccard >= .10`, `n=1,393`): positive from `k=10` through `k=200`, with
  normalized excess `.0017` to `.0307` and adjusted `p=.006`.

**Mathematical reading:** a high-dimensional, weak but reproducible *broad
relational field* remains after the current factor projection. It is not a set
of fixed local author groups and is not rescued as a catalog of named axes.

### Dynamic residual field

- `n=635`, 10 observed descriptors; effective rank `5.68/5.67` and local
  intrinsic-dimension estimate `6.88/6.79`.
- There is no stable kernel geometry or local neighbourhood geometry: CKA `.0105`
  has adjusted `p=1.0`, and the `k=5` through `k=50` neighbourhood profile is
  not familywise positive.
- The only surviving numerical trace is broad distance ordering: pairwise-distance
  Spearman `.0985`, adjusted `p=.036`; neighbourhood overlap appears only at
  `k=100` and `k=200` (adjusted `p=.006`). Those scales cover roughly 16% and
  31% of available dynamic authors, respectively.
- The condition-overlap sensitivity has the same pattern: no local signal, then
  broad-scale overlap at `k=100/200`.

**Mathematical reading:** current dynamic descriptors preserve at most a coarse
ordering or dispersion relation. They do not support a stable local manifold,
discrete dynamic factor, or identifiable author transition operator.

## Resolution of the apparent contradiction

The earlier V6 factor audit rejected discrete static and dynamic axes, while the
new numerical audit detects a static relational map. These findings are
compatible. A coordinate axis may fail transport or individual reliability even
when the relative distances among many authors remain weakly reproducible. The
appropriate current measurement object is thus a quotient geometry, not a
named factor score:

\[
\mathcal G^{(h)}=(D^{(h)},A_k^{(h)},\Sigma^{(h)}),
\]

where `D` is pairwise distance order, `A_k` is the neighbourhood graph at scale
`k`, and `Sigma` is the spectrum. This is a corpus- and representation-conditional
text-path object. It is not yet a personality construct.

## Binding limits

- No result establishes Big Five, MBTI, emotion, clinical state, or another
  external construct.
- Condition-overlap restriction is a sensitivity analysis, not causal control;
  latent topic, role, identity, persistent state, and representation artifacts
  remain viable explanations.
- The observed effects are statistically detected but small in absolute
  neighbourhood excess. No practical materiality margin was preregistered.
- One PANDORA corpus cannot distinguish a stable author dynamic from persistent
  state. The dynamic author-operator claim remains refused.

## Next mathematical gate

Do not inspect or name text examples yet. First test whether the same quotient
geometry transports across independently frozen numeric representations (for
example word/character versus embedding spaces) using alignment-free distance or
Gromov-Wasserstein-style comparison. If the static broad field disappears under
representation change, it is a representation-specific artifact. If it survives,
then a repeated fixed-condition human design can test whether it is an
author-by-context object rather than a corpus-wide selection field.
