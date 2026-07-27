# SUICA V8 Behavior-v2.1 Candidate Report

## Decision

`V8_BEHAVIOR_V21_CANDIDATE_FROZEN_CONDITION_UNRESOLVED`

The opened PANDORA panel supports a replayable technical candidate based on
soft aggregation of five coarse explicit-behavior families. It does not yet
identify condition-invariant response, observer accuracy, personality,
emotion, diagnosis, or clinical utility. A geometry bridge is not licensed.

## Design

- 24 authors: 18 discovery and 6 calibration;
- two source-disjoint halves per author;
- 12 comments per half;
- two primary-observer repetitions;
- independent-model audit on 8 authors;
- opaque profile identifiers, with paired halves separated across calls;
- no psychological, clinical, market, or geometry labels;
- all author-level aggregation and inference performed by deterministic code.

The observer emits opportunities, atomic event codes, and exact source-span
bindings. It cannot emit person scores, traits, diagnoses, confidence, or
intensity. Duplicate binary events are deterministically merged. Invalid
`self_repair` temporal links are dropped rather than repaired by inference.

## Behavior-v2 Pilot

The high-resolution atomic pilot stopped:

- structured profile coverage: 1.000;
- raw structured-call success: 0.967;
- repeated atomic-event macro-F1: 0.849;
- cross-model atomic-event macro-F1: 0.621;
- usable atomic events: 10;
- current condition-residual AUC at 3/6/12 comments:
  0.561 / 0.449 / 0.385;
- condition/length-only AUC at 3/6/12:
  0.871 / 0.872 / 0.928.

The original `behavior-minus-condition` gate is retired. Condition and
opportunity selection are an identified SUICA channel, not a nuisance
baseline that a conditional response channel must outperform.

## Why Residualization Failed

The discovery panel contains 432 segments across 172 subreddits:

- 58.1% of subreddits contain one segment;
- 62.7% of segments belong to a subreddit represented by one author;
- 76.2% belong to a subreddit represented by at most two authors;
- same-author halves share 3.61 subreddits on average;
- mean left/right subreddit Jaccard is 0.335.

For an in-sample condition estimator

\[
\hat p_{kc}
=
\frac{S_{kc}+\lambda p_k}{N_{kc}+\lambda},
\qquad
e_i=Y_i-\hat p_{kc},
\]

two observations included in the same fitted condition mean acquire negative
residual covariance. Sparse subreddit cells also make condition nearly an
author proxy. A leave-one-author-out correction removed self-inclusion but
did not recover the atomic response object:

- soft LOAO z AUC: 0.499;
- reliability-gated soft LOAO z AUC: 0.492;
- soft posterior atomic rate AUC: 0.412.

Therefore self-inclusion was a real defect, but not the whole explanation.
Conditioning on exact subreddit removes most of the stable observed signal.

## Behavior-v2.1 Candidate

The candidate retains atomic events for evidence but scores five deterministic
superordinate families:

- `stance`;
- `affect`;
- `self_report`;
- `action_guidance`;
- `generativity`.

Subtype disagreement no longer becomes a false absence. Two-run event
indicators are averaged before author aggregation.

Headline opened-panel results:

- soft coarse-family AUC: **0.699**;
- author-cluster 95% interval: **[0.554, 0.798]**;
- author-pairing permutation p: **0.0010**;
- repetition 0/1 AUC: **0.669 / 0.683**;
- coarse cross-model macro-F1: **0.771**;
- reliable nine-atomic-event AUC: **0.667**
  [0.552, 0.777], p=0.0040.

Nested 200-draw resolution analysis:

| Comments per half | Mean coarse AUC |
| ---: | ---: |
| 3 | 0.589 |
| 6 | 0.639 |
| 9 | 0.679 |
| 12 | 0.699 |

The slope against log comment count is +0.0807. This reverses the apparent
negative-resolution result produced by strict intersection plus condition
residualization.

## Remaining Identification Gap

Opportunity/condition selection remains strong:

- soft opportunity-profile AUC: 0.656;
- condition/length control AUC: 0.928;
- condition plus coarse behavior AUC: 0.912;
- paired increment over condition: -0.0208
  [-0.0752, 0.0317].

The attempted condition-matched negative design did not attain overlap:
condition itself retained AUC 0.803 after matching. Its coarse-behavior AUC
of 0.669 therefore cannot be interpreted as condition-independent response.

The current evidence supports a stable author-relative **joint
choice-and-expression profile**. It does not yet separate:

\[
\text{C1: opportunity/context choice}
\quad\text{from}\quad
\text{C2: response under a shared condition}.
\]

## Next Gate

Before any geometry bridge:

1. adjudicated human coding must establish event-family accuracy;
2. the frozen v2.1 hierarchy must run on a fresh author panel;
3. both primary repetitions must remain above AUC 0.55 with a gap at most
   0.08;
4. coarse AUC must be at least 0.60, with cluster CI lower bound above 0.50
   and permutation p at most 0.05;
5. the nested resolution slope must remain non-negative;
6. C1 and C2 must be separated with a design that has actual condition
   overlap, preferably randomized fixed opportunities.

Until then, the valid claim is technical: explicit text events contain a
repeatable author-relative configuration when aggregated at the correct
semantic level.
