# SUICA V8 Canonical-Orbit Geometry Method Audit

Status: `INTERNAL_FRESH_AUTHOR_CONFIRMATION_PASS__BEHAVIOR_OBJECT_STOP`

Run date: 2026-07-25
Primary run:
`results/v8_spectral_geometry_audit/pandora_opened_panel_v4_scale_residual_20260725`

## Question

The constrained interpreter failed to connect the frozen V7 geometry to a
small explicit behavior codebook. This audit asks a narrower upstream
question: did the sorted landmark-distance representation itself discard
source-disjoint author structure?

No personality labels, clinical labels, or new LLM calls were used.

## Failure diagnosis

The previous geometry-to-behavior bridge stopped with
`V8_BRIDGE_STOP_NO_CONFIRMATION`:

- selected cross-modal author AUC: 0.493;
- geometry self-author AUC: 0.466;
- behavior self-author AUC: 0.551;
- distance alignment: 0.012, permutation p=0.460;
- registered stable links: 0.

The 16 sorted landmark distances had mean absolute inter-column correlation
0.826, effective rank 1.446, and 82.8% of variance in PC1. Sorting preserved a
radial distance distribution but destroyed which landmark generated each
distance. The explicit behavior view was also weak at the available
three-segment resolution. Therefore renderer or prompt tuning was not
justified.

## Canonical structural identity

Let \(L_1,\ldots,L_m\) be frozen landmarks, \(D\) their internal distance
matrix, and \(d(x)=(\|x-L_1\|,\ldots,\|x-L_m\|)\) the query-to-landmark
distances. Each landmark receives the intrinsic fingerprint

\[
f_i = \operatorname{sort}\{D_{ij}:j\ne i\}.
\]

When all \(f_i\) are unique, lexicographically sorting the fingerprints
defines an anonymous structural order \(\pi_D\). The canonical coordinate is

\[
\phi_{\mathrm{can}}(x;D)=P_{\pi_D}d(x).
\]

It is invariant to a common Euclidean isometry and to arbitrary input
landmark permutations:

\[
\phi_{\mathrm{can}}(Tx;PDP^\top)
=\phi_{\mathrm{can}}(x;D).
\]

The current 16-landmark graph has 16 unique fingerprints, including after
rounding to three decimals. The implementation refuses fingerprint
collisions rather than treating them as proven graph automorphisms.

The selected scale-residual coordinate removes profile-wide radius:

\[
\phi_{\mathrm{csr}}(x)
=S_{\mathrm{discovery}}\left[
\phi_{\mathrm{can}}(x)-\overline{\phi_{\mathrm{can}}(x)}\mathbf 1
\right],
\]

where \(S_{\mathrm{discovery}}\) is fit only on the discovery partition. This
tests the shape of relative landmark proximity, not absolute distance from the
landmark system.

## Opened-panel results

The post-hoc scale-residual follow-up passed every registered exploratory
control:

| Endpoint | Result |
| --- | ---: |
| Canonical scale-residual cosine AUC | 0.774 |
| Author-cluster cosine estimate | 0.796 |
| Author-cluster 95% interval | [0.687, 0.886] |
| Permutation p | 0.00020 |
| Sorted-distance cosine AUC | 0.498 |
| Paired delta over sorted | +0.280 [0.154, 0.387] |
| Spectral-energy cosine AUC | 0.609 |
| Paired delta over spectral energy | +0.197 [0.088, 0.312] |
| Scale-matched hard-negative AUC | 0.754 |
| Topology-coupling shuffle mean AUC | 0.503 |
| Topology-coupling shuffle drop | 0.271, p=0.0020 |
| Canonical/indexed equivalence error | 0 |
| Maximum invariance error | \(3.68\times10^{-14}\) |

The original whitened 48-dimensional author coordinate remained an
information upper bound at cosine AUC 0.895. A 16-landmark system spans at
most 15 affine directions, so the remaining gap is expected and motivates a
future landmark-capacity audit.

## Interpretation

The result supports a specific mechanism: stable author-relative information
was carried by the coupling between query distances and structurally
identified landmarks. Global sorting erased that coupling. The useful
information is not merely overall radius; the scale-residual representation
performed better and survived scale-matched negatives.

This does not establish a personality construct, psychological validity,
diagnosis, clinical utility, or cross-domain score transport. It demonstrates
source-disjoint author geometry on a panel that had already been opened under
earlier estimands. The selected scale-residual candidate is therefore
exploratory on this first panel.

## Internal fresh-author confirmation

The registered follow-up excluded all 240 authors in the full V7 eligible set
before deterministic hash sampling from the PANDORA raw-comment pool. It
yielded 156 source-eligible authors and 89 frozen-geometry-ready authors. No
external labels, new LLM calls, or raw identifiers were used.

| Endpoint | Fresh result |
| --- | ---: |
| Ready authors / source-eligible authors | 89 / 156 |
| Ready-support rate, Wilson lower | 0.571, 0.492 |
| Canonical scale-residual cosine AUC | 0.691 |
| Author-cluster cosine estimate | 0.689 |
| Author-cluster 95% interval | [0.636, 0.740] |
| Permutation p | 0.00010 |
| Sorted-distance cosine AUC | 0.497 |
| Paired delta over sorted | +0.190 [0.118, 0.261] |
| Spectral-energy cosine AUC | 0.578 |
| Paired delta over spectral energy | +0.109 [0.056, 0.161] |
| Scale-matched hard-negative AUC | 0.625 |
| Topology-coupling shuffle drop | 0.190, p=0.0010 |
| Maximum invariance error | \(4.57\times10^{-14}\) |

The primary registered gate and the stricter independent audit both passed.
This upgrades the mathematical claim to an internally confirmed PANDORA
author-geometry mechanism. It does not provide independent-corpus replication
or psychological meaning.

## Behavior reconnection

The bounded no-new-LLM reconnection has been completed. Canonical geometry
self-author AUC rose to 0.735, but behavior self-author AUC remained 0.556.
Cross-modal AUC was 0.547 [0.447, 0.616], with zero stable registered links.
The current three-segment/six-event behavior object is therefore stopped.

The next gates are a higher-resolution behavior study with more temporal
segments, a broader observable event ontology and an independently coded
subset, plus independent-corpus replication of canonical geometry before the
frozen V7 release object changes. See
`reports/V8_CANONICAL_BEHAVIOR_BRIDGE_REPORT.md`.
