# SUICA M4-X — the expression-response line (Where × What, What × When on metadata)

Opened 2026-08-19, after the R-line's full close. The 4W empirical state
(`SUICA_4W_EMPIRICAL_STATE.md`) records crossings #2 (Where × What,
condition response) and #3 (What × When, state trajectories) as the last
crossings with no real-data measurement. This line opens them WITHOUT
reading a single text body: the comments file carries
`word_count_quoteless` — the author's OWN-WORD count per comment, quotes
removed — a crude but honest expression-volume scalar (What-adjacent:
how much one says, not what one says; the boundary is permanent and
named on every claim).

Governance: label-free throughout the opening phase (`author_profiles.csv`
never opened); NO text bodies read (metadata columns only); ID-leak
universe = all 10,296 names under the #83 HEAD-identical policy;
aggregates only; EXPLORATORY corpus-level; no person claims; no
psychological naming (verbosity is a technical expression-volume object).

## Line charter

- **X1 (registered below):** the venue response of expression volume —
  crossing #2's first real-data projection: do communities condition an
  author's verbosity, and is the author×community response profile
  REPRODUCIBLE (persistent across the author's own time halves)?
- **X2 (named, not registered):** What × When paths — burst/order/dwell
  structure of expression volume in event time (the U1 machinery pointed
  at y instead of state identity).
- **X3 (named, not registered):** the stage-E trait join (verbosity level
  / response profile vs Big5) — the literature's classic claims meet the
  dissociation family; only under fresh stamps, only after X1/X2.

---

## X1 — the venue response of expression volume (registered BEFORE run, 2026-08-19)

### 4W header

- **Which 4W object.** Crossing #2 (Where × What): the condition-response
  operator R_v's first real-data projection — the persistence of the
  author×community interaction profile of y = log(1 + wcq). The theory's
  projection caution binds: profile persistence is ONE static projection
  of the response operator; a null is a statement about this projection.
- **What is fixed.** y = log(1 + word_count_quoteless) (pinned #70;
  word_count as sensitivity); halves by the author's FULL-STREAM median
  created_utc (≤ to early); communities = raw subreddit names (no
  vocabulary floor — the estimand needs no cross-author support floor;
  a W1-law-vocabulary restriction is a sensitivity arm); cell (u, c, h)
  eligible at n_min comments; author eligible at ≥ k_min shared
  communities whose BOTH halves are eligible.
- **What varies.** Cohort (disjoint primary; Big5 replication); n_min ∈
  {10 primary, 5}; k_min = 3; raw vs law-vocabulary community universe.
- **What falsifies.** R inside its permutation band AND the interaction
  covariance share CI including 0 → NO_REPRODUCIBLE_RESPONSE for this
  projection.
- **Layer.** R.

### Census (planner arithmetic #43; predicates exact per #77/#78, run 2026-08-19)

| quantity (exact predicate) | value |
|---|---|
| rows parseable (author+subreddit+created_utc+wcq) | 17,640,062 of 17,640,062 |
| wcq = 0 share | 0.0000 |
| authors | 10,296 (1,401 Big5 + 8,895 disjoint) |
| pool, disjoint, n=10/k=3 | **4,342** (PRIMARY) |
| pool, disjoint, n=5/k=3 | 5,842 (sensitivity) |
| pool, Big5, n=10/k=3 | **615** (replication arm) |
| median shared eligible communities (n=5) | 4 (disjoint) / 3 (Big5) |
| within-cell sd of y (median, n=5 early cells) | 0.9070 |
| R width projection (#79b: sd of a 3-point per-author correlation ≈ 0.5–0.7; SE ≈ 0.6/√4342) | ≈ ±0.018 at the primary pool — detection from R ≈ 0.02 |

Antecedent verification (#84): the per-author correlation is defined at
k_min = 3 (df = 1, noisy per author, powerful in the mean over 4,342);
no saturation risk (within-cell noise bounds every per-author correlation
away from 1 — headroom exists by construction and is REPORTED from the
realized distribution); the null's coordinate is the mechanism's own
(community-label permutation); all design parameters named here.

### Estimands (transforms pinned #70; own nulls #68/#66)

Within each half, on the eligible cell grid: double-centered deviations
v_{u,c,h} = ȳ_{u,c,h} − ā_{u,h} − b̄_{c,h} + ḡ_h (author and community
means over eligible cells, unweighted; the incomplete-design caveat is
named and the permutation null preserves the design exactly).

1. **R (response-profile persistence):** mean over eligible authors of
   corr_c(v_{u,·,early}, v_{u,·,late}) over the author's shared eligible
   communities. Own null: community labels permuted within
   (author, half) among that author's eligible cells, B = 499; band =
   2.5/97.5 percentiles; cluster bootstrap over authors B = 1000 for the
   CI on R.
2. **The reproducible variance budget** (cross-half covariance trick —
   attenuation-free): shares of comment-level Var(y) from
   (a) author: cov over authors of half-means; (b) community: cov over
   communities of half-means (size-weighted; unweighted sensitivity);
   (c) interaction: cov over eligible cells of (v_early, v_late),
   unweighted (weighted sensitivity); residual = remainder. Same
   permutation null for the interaction share; cluster bootstrap CIs.
3. Descriptives (non-verdict): per-cohort budgets; the realized
   per-author correlation distribution (the headroom report); community
   count sensitivity.

### Cells (NULL-first #55; effect-size keyed #75 on the interaction share, with R co-reported)

1. **NO_REPRODUCIBLE_RESPONSE** — R inside its band AND interaction
   share CI includes 0.
2. **RESPONSE_TRACE** — detected; interaction share < 0.02 of total
   variance.
3. **IDIOSYNCRATIC_RESPONSE** — share ∈ [0.02, 0.10].
4. **RESPONSE_MAJOR** — share > 0.10.

Boundary rationale: author-main verbosity shares in the literature run
~0.2–0.4 on log scales and community norms ~0.05–0.15; a persistent
interaction at 2–10% of total variance would be a real second-order
channel. CI membership decides; straddles reported as straddles.
Big5-replication and law-vocabulary divergences carry #73 flags; the
primary routes.

### Registered leans

- Interaction DETECTED and small: R ∈ (0.05, 0.30], share ∈
  (0.005, 0.05] — the RESPONSE_TRACE/IDIOSYNCRATIC boundary region.
  Rationale: on the log scale, "personal baseline × venue norm"
  (multiplicative) is ADDITIVE and lands entirely in the mains; the
  interaction asks for more than that — genuine per-author venue
  idiosyncrasy — and the dissociation-family record counsels modesty
  about second-order channels.
- Descriptive leans: author main share ∈ [0.15, 0.45]; community main ∈
  [0.02, 0.15].
- Replication lean: Big5 cohort same cell (#73 if not).

### Deliverables and discipline

Standard six: `scripts/run_suica_m4_x1_venue_response.py` + tests
(double-centering correctness on a hand toy; permutation preserves the
design; covariance-budget recovery on a synthetic two-way world with
planted shares — the #76 operating point: planted shares at realistic
magnitudes {author .3, community .08, interaction .02} and a null world
{interaction 0}, both must be recovered before the real arm, A1 stop on
failure; headroom report; ID-leak helper); gitignored
`results/m4_x1_venue_response/` (fresh metadata cache with anchors:
17,640,062 parseable rows, 10,296 authors); report
`reports/SUICA_M4_X1_VENUE_RESPONSE_REPORT.md` (rule-24 tables; budget
table with CIs and null bands per cohort; R with band and CI; headroom
distribution; boundaries: metadata-only, expression VOLUME not content,
the projection caution, no psychological naming); outcome appended here;
one CLAIMS_LEDGER row (EXPLORATORY, label-free, corpus-level,
metadata-only named); ONE commit
`feat(m4-x): X1 — the venue response of expression volume — <VERDICT>`;
suite green (1304 + new); ID-leak scan under #83 (universe 10,296).
SEED = 20260819; B_perm = 499; B_boot = 1000. `author_profiles.csv`
never opened; no text bodies read.
