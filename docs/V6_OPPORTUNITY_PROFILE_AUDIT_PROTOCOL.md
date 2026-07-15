# V6 Opportunity-Profile Source Audit Protocol

Status: frozen before execution, 2026-07-14.

## Aim

This is a negative-control extension of the V6 residual-source audit. The
existing residualizer removes linear, per-comment surface effects and supported
condition-by-half means. It does not by itself test whether residual author
retrieval is driven by a person's *distribution* of visible expression
opportunities, such as persistent formatting mix or cadence.

The audit therefore asks:

\[
P\bigl(d(R_{u,e},R_{u,l}) < d(R_{u,e},R_{v,l})\bigr) > 0.5
\]

after matching late stranger `v` to late target `u` on successively richer
observable profiles. `R` is the frozen static residual representation. The
probability is a matched same-author AUC, not a trait validity coefficient.

## Data contract

- Local PANDORA Tier-U comments only: author, body, timestamp, subreddit.
- Existing `prepare_units` filtering and personality-report guard apply before
  any representation or profile calculation.
- No Big Five, MBTI, Enneagram, clinical, demographic, or outcome columns may
  be read.
- No raw text, user identifier, embedding, or per-user opportunity profile may
  be exported.

## Frozen source representation

The runner reuses `configs/v6_factor_discovery_raw.json` unchanged:

1. discovery-only word/bigram TF-IDF plus 24-dimensional SVD;
2. author-cross-fitted Ridge residualization of ten per-comment surface fields,
   half, their interaction, and supported condition-by-half mean;
3. static author-by-half residual object;
4. discovery-only static projection, then confirmation author views.

This audit is not a re-fit or a search for an alternative representation.

## Matching hierarchy

All stranger matching is target-late matching. Each target is matched only to a
different confirmation author's late view, sampled from its 25 nearest eligible
candidates. The following stages are fixed:

| Stage | Numeric profile | Community rule |
|---|---|---|
| coarse | log selected comment count, log selected condition count | none |
| surface_mean | coarse + ten format means | none |
| surface_distribution | prior + ten within-view format SDs | none |
| surface_time | prior + span, median/max gap, long-run support | none |
| surface_time_plus_community | surface_time | soft Jaccard cost, weight 1 |
| surface_time_plus_community_caliper | surface_time | Jaccard >= .10 plus soft cost |

Format fields are token/character length, URL, quote, list, code, digit,
question, exclamation, and punctuation rates. They are observed *opportunity
descriptors*, not content factors or personality variables.

## Primary endpoint and decision

The primary object is `static_residual`; `static_full` and `static_factor` are
secondary accounting views. The primary row is the strict final stage.

- coverage `< .75`: `REFUSE_INSUFFICIENT_MATCHED_SUPPORT`;
- coverage `>= .75` and bootstrap AUC lower bound `> .50`:
  `SURVIVES_OBSERVED_OPPORTUNITY_PROFILE_SCREEN`;
- upper bound `< .50`: `COMPATIBLE_WITH_OBSERVED_OPPORTUNITY_PROXY`;
- otherwise: `UNDECIDED_AFTER_OBSERVED_OPPORTUNITY_SCREEN`.

Neither survival nor collapse identifies a causal source. Unobserved semantic
topic, role, identity, moderation, editing, and latent opportunity remain
possible explanations. The audit excludes dynamic objects because PANDORA lacks
the registered repeated-condition epoch x technical-replica support.

## Post-run matching-quality QA

After the primary endpoint was run, two descriptive quality checks were added:
the matched-to-random standardized profile-distance ratio and the matched minus
random community-Jaccard difference. They test whether the nearest-pool
mechanism actually improves observed-profile similarity relative to random
non-self pairs. They are explicitly **not** a revised endpoint, a gate, or a
causal-balance certificate; the primary decision above is unchanged.
