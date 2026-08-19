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

---

## X1 outcome (executor, 2026-08-19)

**VERDICT — `A1_STOP__SYNTHETIC_GATE_FAILED`.** Part 0 failed on BOTH of its
clauses, so the A1 stop fired before any real estimand was computed. There is
no corpus value of R, of the variance budget, or of the headroom distribution
anywhere in this leg's artifacts. The registered cells are UNSCORED —
`NO_REPRODUCIBLE_RESPONSE` is *not* the outcome; the leg reached no reading of
crossing #2 in either direction.

Harness `scripts/run_suica_m4_x1_venue_response.py`; tests
`tests/test_m4_x1_venue_response.py`; artifacts
`results/m4_x1_venue_response/` (gitignored); report
`reports/SUICA_M4_X1_VENUE_RESPONSE_REPORT.md`. Runtime 39.8 s end to end
(17.6M-row metadata stream 17.5 s). SEED 20260819, B_perm 499, B_boot 1000.

### The census reproduced exactly (#78) — all ten pins

17,640,062 parseable rows of 17,640,062 streamed; wcq = 0 share 0.0000 (119
rows); 10,296 authors = 1,401 Big5 + 8,895 disjoint; pools **4,342** (disjoint
n=10/k=3, PRIMARY), **5,842** (disjoint n=5/k=3), **615** (Big5 n=10/k=3); law
vocabulary floor 89 = ceil(0.01 x 8,895) giving exactly **1,443** communities.
Two inherited cross-checks also land on the nose: 14,634,702 disjoint events
(W1's cache) and 3,005,360 Big5 events (U2's `ANCHOR_EVENTS`). The eligibility
predicate is therefore not in doubt.

Two NON-GATING descriptives in the census table did not reproduce and are
recorded as anomalies: the within-cell sd of y (registered 0.9070, observed
0.9035 over disjoint n=5 early cells, ddof=1), and the median shared eligible
communities (registered 4 disjoint / 3 Big5; observed 5.0 / 4.0 over authors
with at least one shared pair and 7.0 / 8.0 over eligible authors — off by one
under the first reading in both cohorts). Neither gates anything.

### Part 0 — what the gate found (all numbers synthetic; no real y)

The world is built at the primary arm's REALIZED design density by reusing the
real skeleton (4,342 authors, 5,369 communities, 42,141 occupied slots, the
real per-cell comment counts) and planting entirely synthetic y. Tolerance
`max(0.01, 3 x replicate sd)` over 8 replicates; the 0.01 floor is half the
width of the registration's own TRACE/IDIOSYNCRATIC boundary.

| planted | value | recovered (8 reps) | tolerance | bias | status |
|---|---|---|---|---|---|
| author main | 0.3000 | 0.3261 | 0.0217 | +0.0261 | FAIL |
| community main | 0.0800 | 0.1351 | 0.0268 | +0.0551 | FAIL |
| interaction | 0.0200 | 0.0613 | 0.0100 | +0.0413 | FAIL |

Null world (interaction planted at exactly 0.0000): the estimator returns
0.0458 +- 0.0014 over 8 replicates; on the scored replicate 0.0482 with a
cluster-bootstrap CI [0.0566, 0.0738] that excludes 0 **and does not even
cover its own point estimate**, and R = 0.4524 against a permutation band
[0.2184, 0.2439]. Both honesty clauses fail.

Ablations localize the artifact exactly. Author main ONLY (0.3000, nothing
else): interaction reads 0.0383, R reads 0.4244. Community main ONLY (0.0800,
nothing else): interaction reads 0.0078, R reads 0.0006. The two leaks are
additive (0.0383 + 0.0078 = 0.0461 vs the null world's 0.0458), and the AUTHOR
main through thin communities is the dominant one.

### The mechanism, stated once

Double-centering removes the mains EXACTLY only on a complete grid. On an
incomplete one, `v` retains two residues: a per-COMMUNITY term (the community's
own author-set mean of the author main) and a per-AUTHOR term (the author's own
community-set mean of the community main). Both are the same in EARLY and LATE
by construction, because a main effect does not change across halves — so the
cross-half covariance trick, which is attenuation-free against noise, is
defenceless against them. The per-author term is removed by the within-author
centering inside the correlation, which is why the community main leaks 0.0078
into the share but 0.0006 into R; the per-community term survives both, which
is why the author main leaks into R at 0.4244.

The registered permutation null does not absorb this. Permuting community
labels within (author, half) moves the community MAIN together with the
interaction, injecting within-author variance the real data does not carry, so
the band ([0.0423, 0.0440]) sits BELOW the artifact it is meant to calibrate
(0.0482) — anti-conservative, not conservative.

### Defect candidates recorded for the planner (nothing below was run)

1. **The #84 antecedent verification checked the wrong antecedent.** It
   verified the ceiling (no saturation) and the null's coordinate, and asserted
   that "the estimand needs no cross-author support floor". It never asked
   whether the estimator's ZERO is zero on the realized design. It is not.
2. **The routing statistic is zero-referenced but its zero moves.** Cell 1
   asks whether the share's CI includes 0; on an incomplete grid the
   no-response value is the leak, and the author cluster bootstrap makes the
   grid MORE incomplete (about 63% distinct authors per replicate), so the CI
   tracks the leak rather than the estimand.
3. **The permutation null is not a clean mechanism coordinate here.** A null
   that resamples the interaction while HOLDING both mains fixed would be the
   matching coordinate.
4. **The headroom clause is stated about the wrong object.** At k_min = 3 a
   per-author Pearson correlation over three points is NOT bounded away from 1
   (4.70% of authors above 0.99 on the planted world, extremes rounding to
   +-1.0000). What is bounded is the MEAN over thousands of authors.
5. **Support is a PRIMARY question, not a sensitivity.** The primary design has
   a median of 2.0 eligible authors per community and 5.77% of slots in
   single-author communities; the law-vocabulary arm the registration demoted
   to a sensitivity has 9.0 and 0.32%. The leak scales with exactly that
   sparsity, so a cross-author support floor is a candidate PRIMARY — the
   opposite of what the registration reasoned.

### What still stands

The 4W header, the census, the eligibility predicate, the half rule and the
cell/lean boundaries are all intact and re-usable: only the ESTIMATOR's
calibration failed. The metadata-only boundary held throughout — no text body
was read, `author_profiles.csv` was never opened, and the ID-leak scan over all
10,296 author names cleared with 0 NEW hits (3 pre-existing dictionary
collisions in `CLAIMS_LEDGER.md`, carried unchanged from HEAD under the W1
policy).

## X1 planner adjudication (2026-08-19)

**Registered outcome ACCEPTED: `A1_STOP__SYNTHETIC_GATE_FAILED` — no
cell, and expressly NOT `NO_REPRODUCIBLE_RESPONSE`.** The gate
architecture did precisely what #76/#84 built it to do: it caught a real
estimator defect on the realized design BEFORE any real estimand ran
(39.8 s leg; ten anchors exact; the real skeleton reused with wholly
synthetic signal). The executor's restraint is noted with approval
twice: Part 0 was NOT run on the better-conditioned law-vocabulary
skeleton (choosing an arm by gate performance after a failure is a
planner re-registration, not an executor pivot), and the #83 scan
caught a PANDORA username ("independent") inside the executor's own
docstring — the widened-universe policy working end to end.

**The mechanism, owned.** Double-centering removes mains EXACTLY only
on a complete grid. The registered primary grid has fill 0.0018 with a
median of 2.0 eligible authors per community and 5.77% single-author
slots; v therefore retains per-community residues of the author main
and per-author residues of the community main — IDENTICAL across
halves — and the "attenuation-free" cross-half covariance has no
defence: the null world read share 0.0458 (2.3× the registered TRACE
boundary) and R = 0.45, with the registered permutation null sitting
BELOW the artifact (it moves the community main together with the
interaction). Ablations localize the leak to the author main.

**Defect #85 (planner, purchased; registry thirty-second note).** Three
parts. (a) The estimator's ZERO POINT was never verified on the
REALIZED design geometry — #84's antecedent checks covered the ceiling
and the null's coordinate but not whether zero reads zero on this
skeleton; (b) the zero-reference is not bootstrap-stable (the author
cluster bootstrap makes the grid ~37% more incomplete and moves the
zero); (c) the registration's "the estimand needs no cross-author
support floor" was exactly backwards — the ESTIMAND needs no semantic
floor, but the ESTIMATOR needs cross-author SUPPORT, so support
conditioning (fill, units-per-condition, singleton share, connectivity)
is a PRIMARY design parameter. Convention: every estimator whose
exactness depends on design completeness carries a zero-point gate ON
THE REALIZED SKELETON (real incidence, synthetic signal), verified
under bootstrap resampling as well; support conditioning is censused
and pinned as primary design; nulls hold fixed everything the estimand
claims to have removed. Minor (#77 family, non-gating): two census
descriptives did not reproduce under ambiguous predicate readings
(within-cell sd 0.9035 vs 0.9070; the shared-communities median) — the
gated pool counts matched to the unit.

**X1b is registered below** (the SR4/U2c completion pattern): design
repaired (law vocabulary + support floor, censused on X1's committed
cache) AND estimator repaired (exact two-way fixed effects on the
connected component), with the gate that failed here required to PASS
there before any real number.

---

## X1b — the venue response, repaired design and exact estimator (registered BEFORE run, 2026-08-19)

### What changes from X1 (everything else inherits)

1. **Design (support conditioning as primary, #85c).** Community
   universe = the LAW vocabulary (1,443; floor 89, reproduced on X1's
   cache); pinned predicate order with NO fixed-point iteration:
   (1) cells n ≥ 10, disjoint authors, law communities; (2) shared
   pairs (both halves eligible); (3) community support floor s = 5
   authors with a shared pair; (4) authors with ≥ 3 surviving shared
   communities; (5) largest connected component of the bipartite
   graph. Census (planner, on X1's committed cell cache, 2026-08-19):

   | s | authors | communities | shared pairs | fill | med authors/comm | singletons | LCC |
   |---|---|---|---|---|---|---|---|
   | 3 | 3,686 | 1,145 | 32,415 | 0.0077 | 11.0 | 0.0009 | 1.000 |
   | **5 (PRIMARY)** | **3,665** | **1,000** | **31,899** | 0.0087 | **12.5** | **0.0000** | **1.000** |
   | 8 (sensitivity) | 3,595 | 780 | 30,561 | 0.0109 | 16.0 | 0.0000 | 1.000 |

2. **Estimator (exact zero on any connected design).** Per half,
   two-way fixed effects on the eligible shared cells by alternating
   projections (within-transform demeaning iterated to max-change
   ≤ 1e-10; exact main removal is guaranteed on the connected
   component, and the LCC covers 100% of authors at every s); v = the
   FE residual of the cell mean. R and the interaction covariance
   share defined on v exactly as in X1; the author and community main
   shares from the same cross-half covariances as in X1 (mains are
   estimated pre-FE; only the interaction object changes).
3. **The gate that failed must now pass (Part 0, A1 stop).** The SAME
   realized-skeleton battery, now on the X1b skeleton: planted
   {author .30, community .08, interaction .02}, the NULL world
   (interaction 0), author-only and community-only ablation worlds,
   8 replicates; PASS = recovery within max(0.01, 3·replicate sd),
   null non-detection (share CI covers 0 AND its point within the
   band; R inside band), ablation leakage < 0.005, AND the
   bootstrap-zero check (#85b: the null world's cluster-bootstrap CI
   covers 0). Any clause fails → A1 stop, honest report.
4. **Replication arm.** Big5 cohort under the identical predicate
   chain; its pool is censused IN-LEG with a #69 floor of 300 authors
   — below the floor the arm reports as underpowered-descriptive
   rather than flagging #73.

Cells, leans, sensitivities (s = 8; n = 5; word_count), boundaries,
governance, and discipline inherit X1's registration verbatim
(metadata-only; no bodies; no profiles; #83 universe 10,296;
EXPLORATORY; the projection caution). Deliverables: standard six,
`scripts/run_suica_m4_x1b_venue_response_fe.py` + tests (FE exactness
on a hand toy AND on the realized skeleton; gate battery; predicate-
chain reproduction of the census table above as blocking anchors),
gitignored `results/m4_x1b_venue_response_fe/`, report
`reports/SUICA_M4_X1B_VENUE_RESPONSE_FE_REPORT.md`, outcome appended
here, one CLAIMS_LEDGER row, ONE commit
`feat(m4-x): X1b — the venue response, exact estimator — <VERDICT>`;
suite green (1359 + new). SEED = 20260819; B_perm = 499;
B_boot = 1000.
