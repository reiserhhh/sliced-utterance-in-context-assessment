# V8 Behavior-v2.1 Fresh-Panel Preflight

## Decision

`V8_BEHAVIOR_V21_FRESH_PREFLIGHT_READY_HUMAN_GATE_CLOSED`

The fresh joint choice-and-expression replication is operationally feasible.
The current Reddit corpus cannot identify the registered exact-condition C2
object. No model calls were made, and fresh execution remains blocked by the
human-observer gate.

## Author and Split Support

The preflight excluded:

- all 240 authors in the full V7 eligible set;
- the complete 180-author registered canonical-fresh candidate pool.

It then streamed the original PANDORA comment source, preserving `link_id`,
rather than relying on the prepared parquet that lacks thread identifiers.
Results:

- candidates scanned: 300;
- candidates with two valid thread-disjoint 32-comment halves: 300;
- pre-extracted authors: 190;
- discovery/calibration/confirmation/reserve: 60/20/80/30;
- maximum cross-half thread overlap: 0;
- new LLM calls: 0.

Median valid comments per selected author ranged from 481 in discovery to
746 in confirmation. Median valid thread count was 381 in discovery and 507
in confirmation. The minimum half time span exceeded 29 days in discovery
and 51 days in confirmation. Text quantity is not the current blocker.

## C2 Identification Audit

An exact condition needed at least 10 discovery authors and 50 discovery
segments. Only five subreddits passed:

- `AskReddit`;
- `INTP`;
- `intj`;
- `mbti`;
- `infp`.

Together they covered only 15.83% of discovery segments. Four of the five are
explicit personality-type communities, making them especially poor anchors
for a general condition-invariant response claim.

Before event/opportunity coding, a necessary structural condition-crossing
check required at least six segments in each left-A, left-B, right-A, and
right-B cell:

- using all conditions: 86.25% of confirmation authors were structurally
  complete;
- using only genuinely supported exact conditions: 0% were complete.

The first number cannot rescue C2: hashing unrelated subreddits into A/B
creates balanced cells but does not make authors respond under shared
conditions. The second number is the relevant identification result.

Therefore the current PANDORA design can test:

\[
\text{joint author profile}
=
\text{C1 selected context/opportunity}
+
\text{observed expression}.
\]

It cannot test:

\[
\text{C2}
=
\text{author-specific response under the same supported condition}.
\]

For PANDORA, the correct future status is
`V8_BEHAVIOR_V21_C2_NOT_IDENTIFIABLE_IN_REDDIT`, unless a new design obtains
real shared-condition coverage. Coarse or global residualization must not be
presented as exact C2.

## Execution Order

1. Complete blind human coding and adjudication of the frozen observer
   hierarchy.
2. If the human gate passes, run discovery plus calibration only for coverage,
   drift, and implementation checks; then freeze all hashes.
3. Open the unchanged 80-author confirmation and separately report coarse
   behavior, C1, and joint scores. Claim a joint increment only if the paired
   AUC-gain interval over C1 has lower bound above zero.
4. Report Reddit C2 as structurally unavailable.
5. Test C2 later in randomized or otherwise fixed-condition repeated text,
   where the same opportunity classes are deliberately observed across
   people.
6. Keep the geometry bridge closed until the human and fresh joint/C1 gates
   pass; a C2 claim requires its own fixed-condition result.

## Claim Boundary

This preflight proves sample and design feasibility only. It is not observer
accuracy, a fresh behavior replication, personality validity, emotion
validity, diagnosis, clinical utility, or a geometry bridge.
