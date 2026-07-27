# V8 Blind Junction Localization V3.7B

Status: `PROSPECTIVELY_SEALED_BEFORE_CONFIRMATION`

Seal: `configs/v8_blind_junction_localization_v37b_seal.json`

V3.7B removes the oracle junction window from V3.7A. It asks whether a locator
that reads only trajectory geometry and order can find a transition window,
infer incoming and outgoing branches, and preserve the anonymous routing
operator.

The locator may read only a path tensor. It may not read cue, author, hidden
group, context, session, outgoing truth, or personality labels. Those fields
open only after localization for event aggregation or scoring.

Rare missed events can create partial cell masks even when panel-level recall
is high. V3.7B therefore uses equal-context, mask-aware \(Q\) aggregation:
unobserved local cells are omitted from that packet-cell mean, never filled
with fabricated events, and complete packet-cell non-overlap is refused.

Synthetic paths contain variable speed, smooth bends, a localized pause-cusp
signature, near crossings, and cue-aligned distractor bends. Negative paths
include smooth curvature, bend-only, pause-only, cue-distractor, and
near-crossing attacks. A true junction is not defined by spatial intersection
alone.

Discovery selects one threshold from
`{0.20,0.25,0.30,0.35,0.40,0.45}` using geometry-only precision, recall, F1,
location error, and false-junction burden. The selected threshold, locator
window, branch directions, V3.7A rank 6, and V3.7A lambda 3 are frozen before
confirmation.

Confirmation gates:

- precision lower bound at least 0.85;
- recall lower bound at least 0.75;
- F1 lower bound at least 0.80;
- median localization error at most one window and P95 at most two;
- false junctions at most 5 per 1000 negative paths;
- blind-versus-oracle routing-operator correlation lower bound at least 0.80;
- at least 80% of oracle held-out log-loss gain retained;
- blind author-claim rate lower bound at least 0.80;
- mean available opportunity fraction lower bound at least 0.95 under
  mask-aware \(Q\) aggregation;
- cue-leak control author-claim rate upper bound at most 0.05.

A PASS is synthetic and procedural only. It does not identify thought nodes,
intelligence, personality, clinical states, or real-text junctions.
