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

---

## X1b outcome (executor, 2026-08-19)

**VERDICT — `A1_STOP__SYNTHETIC_GATE_FAILED`.** Part 0 passed **8 of its 9
clauses** and failed one, so the A1 stop fired again and no real estimand was
computed. There is no corpus value of R, of the variance budget or of the
headroom distribution anywhere in this leg's artifacts. The four cells and all
five leans are UNSCORED; `NO_REPRODUCIBLE_RESPONSE` is expressly NOT the
outcome.

The registered repair itself **succeeded completely.** What failed is the one
object the X1b registration explicitly declined to change.

Harness `scripts/run_suica_m4_x1b_venue_response_fe.py`; tests
`tests/test_m4_x1b_venue_response_fe.py`; artifacts
`results/m4_x1b_venue_response_fe/` (gitignored); report
`reports/SUICA_M4_X1B_VENUE_RESPONSE_FE_REPORT.md`. Runtime about 45 s end to end,
entirely off X1's committed 13.6 MB cell cache — the comments file was not
re-streamed. SEED 20260819, B_perm 499, B_boot 1000.

### The design repair — the planner's census reproduced to the unit (#78)

The pinned chain (no fixed-point iteration) reproduces every blocking anchor:

| s | authors | communities | shared pairs | fill | med authors/comm | singleton communities | LCC |
|---|---|---|---|---|---|---|---|
| 3 | 3,686 | 1,145 | 32,415 | 0.0077 | 11.0 | 1 (0.0009) | 1.000 |
| **5 (PRIMARY)** | **3,665** | **1,000** | **31,899** | 0.0087 | **12.5** | **0** | **1.000** |
| 8 | 3,595 | 780 | 30,561 | 0.0109 | 16.0 | 0 | 1.000 |

The inherited anchors also hold: 17,640,062 parseable rows, 10,296 authors
(1,401 + 8,895), vocabulary floor 89 giving exactly 1,443 communities. The
published fill / median / singleton cross-checks agree at every floor.
Attrition at s = 5: 140,026 eligible cells → 37,414 shared pairs → 36,612
after the support floor → 31,899 after the k ≥ 3 floor → 31,899 in the LCC
(the graph was **already connected** before step 5, so the exactness argument
is valid, not merely assumed). In-leg arm censuses: s = 8 gives 3,595 authors;
n_min = 5 gives 5,094 authors / 1,243 communities / 56,460 pairs; the
word_count arm shares the primary design exactly; the Big5 replication gives
**408 authors**, above the in-leg #69 floor of 300, so it would have carried a
#73 comparison had a cell been reached.

### The estimator repair — exact, and demonstrated on the SAME null world

Alternating projections converge in 28 sweeps per half; the residual AUTHOR
means are ≤ 3.9e-11 and the residual COMMUNITY means ≤ 2.8e-17 on the realized
incomplete grid — the thing a single double-centering cannot do.

| skeleton | estimator | interaction share, null world (mean ± sd of 8) | R |
|---|---|---|---|
| X1's registered skeleton (4,342 × 5,369) | X1 double-centering | **0.0458 ± 0.0014** | 0.4464 |
| X1's registered skeleton | X1b exact FE | 0.0000 ± 0.0001 | 0.0017 |
| X1b skeleton (3,665 × 1,000) | X1 double-centering | 0.0183 ± 0.0014 | 0.2436 |
| **X1b skeleton** | **X1b exact FE** | **−0.0000 ± 0.0001** | **0.0000** |

The top-left cell reproduces X1's committed 0.0458 exactly, which validates
the comparison. Two things follow. (a) The leak was the PROJECTION, not the
grid: the FE reads zero even on X1's own sparse skeleton, while support
conditioning alone would only have taken double-centering from 0.0458 to
0.0183 — still nine times the TRACE boundary's half-width. (b) On the scored
replicate with full inference on both sides, the old estimator gives
0.0176 with CI [0.0241, 0.0286] (covering neither 0 nor its own point) and
R = 0.2442 against band [0.0636, 0.0965]; the new one gives −0.0001 with CI
[−0.0003, 0.0002] and R = 0.0078 against band [−0.0166, 0.0166]. Support
conditioning is still worth its place — it is what makes the mains estimable
and the graph connected — but the registration's estimator clause is what
purchased the zero.

### Part 0 — the nine clauses

| # | clause | value | status |
|---|---|---|---|
| 1 | recovery — author main | 0.3220 for 0.3000, tol 0.0179 | **FAIL** |
| 2 | recovery — community main | 0.1072 for 0.0800, tol 0.0424 | PASS |
| 3 | recovery — interaction | 0.0170 for 0.0200, tol 0.0100 | PASS |
| 4 | null world — share CI covers 0 | [−0.0003, 0.0002] | PASS |
| 5 | null world — share inside its band | −0.0001 in [−0.0011, 0.0010] | PASS |
| 6 | null world — R inside its band | 0.0078 in [−0.0166, 0.0166] | PASS |
| 7 | ablation — author-only leakage | 0.0001 < 0.0050 | PASS |
| 8 | ablation — community-only leakage | 0.0001 < 0.0050 | PASS |
| 9 | #85b bootstrap-zero — null CI covers 0 | yes, and it covers its own point | PASS |

The X1 pathologies are all gone: the CI now covers its own point estimate, the
permutation band now brackets the artifact instead of sitting below it, and
both ablations are three orders of magnitude inside their clause (author-only
0.0001 against X1's 0.0383; community-only 0.0001 against 0.0078).

### The one failing clause, and its mechanism

The author main share is estimated PRE-FE — from the cross-half covariance of
author half-means, X1's definition, which the X1b registration explicitly kept
("mains are estimated pre-FE; only the interaction object changes"). That
estimator's target is not Var(a). An author's half-mean is a_u PLUS that
author's own average of the community main and of the interaction over the
communities they occupy, and that composition average is the same in both
halves up to cell-size reweighting, so the cross-half covariance keeps it. The
size of the term is a design constant: E[1/k_u] = 0.1909 over the 3,665
eligible authors predicts a bias of 0.1909 × (0.08 + 0.02) = **0.0191**
against an observed **+0.0220**. The support floor raised authors-per-community
from X1's 2.0 to 12.5 and thereby fixed the community main (0.1072 for 0.0800
now sits inside its tolerance, against X1's 0.1351); it does not raise
communities-per-author, so it cannot touch the author main.

A second, smaller and opposite bias is now on the record: the two-way
projection removes A + C − 1 = 4,664 dimensions from 31,899 cells, so a white
planted interaction retains 0.8538 of itself. That predicts 0.0171 for a
planted 0.0200 against the observed 0.0170 — the interaction estimand is
CONSERVATIVE by a computable factor, and passes its clause with room to spare.

### Defect candidates recorded for the planner (nothing below was run)

1. **The main-share estimators are MARGINAL, not main.** Their target is
   Var(a) plus a composition term whose divisor is communities-per-author, so
   no support conditioning can move them. Candidates: read the mains off the
   SAME two-way projection that now carries the interaction (effect variances
   with their sampling variance removed), or re-state the clause so the mains
   are scored against their own marginal targets. Neither was run.
2. **Routing clauses and descriptive clauses are gated together.** The cells
   route on the interaction share and R, and both now behave exactly; the leg
   nevertheless stops on a co-reported descriptive component. A planner may
   wish to separate the two so a descriptive bias downgrades a number instead
   of stopping a leg — or may deliberately keep them together, since a budget
   that over-reads its largest component is not a budget.
3. **The FE's degrees of freedom are worth pinning.** Either correct the
   interaction share for the (A + C − 1)/M projection loss or register the
   estimand explicitly as a LOWER bound.

### Governance

Metadata only; `word_count_quoteless` and `word_count` are the sole
text-derived quantities; no body was read; `author_profiles.csv` was never
opened. The ID-leak scan over all 10,296 author names cleared with **0 NEW
hits** (4 pre-existing dictionary collisions carried unchanged from HEAD:
three in `CLAIMS_LEDGER.md`, one in this plan at the line where the X1
adjudication quotes the colliding word). The new boundary is named on every
claim: the analysis universe is now WELL-SHARED VENUES by construction.

## X1b planner adjudication (2026-08-19)

**Registered outcome ACCEPTED: `A1_STOP__SYNTHETIC_GATE_FAILED` — as
routed, 8 of 9 clauses passing. No cell; the corpus remains unread on
crossing #2.** But the situation is categorically different from X1's
stop, and the adjudication must say so precisely:

**The repair WORKED for everything that routes.** The exact-FE
estimator reads the null world at −0.0000 ± 0.0001 with R = 0.0000 —
and reads ZERO even on X1's own registered skeleton (0.0458 → 0.0000),
proving the leak was THE PROJECTION, NOT THE GRID (support conditioning
alone would only have bought 0.0458 → 0.0183). Recovery, both
ablations, both null clauses, and the new #85b bootstrap-zero clause
all pass. The verdict-routing machinery (interaction share + R) is now
CERTIFIED EXACT on the realized skeleton, twice over.

**The one failing clause is a DESCRIPTIVE object with a solved
mechanism.** The author-main share was registered PRE-FE (X1's
definition, deliberately kept): its estimand is MARGINAL, not main —
an author's half-mean carries the author's own composition average of
the community main and the interaction, persistent across halves by
construction. The bias is design-predicted: E[1/k_u]·(0.08+0.02) =
+0.0191 against +0.0220 observed; the mirror contamination shows in
the null world's community main (0.1139 vs 0.0800). No support floor
can move it (floors raise authors-per-community, not
communities-per-author). Also quantified: the FE projection removes
A+C−1 of P dimensions, making the interaction share conservative by
exactly P/(P−A−C+1)⁻¹ = 0.8538 (predicted 0.0171, observed 0.0170).

**Defect #86 (planner, purchased; registry thirty-third note).** Three
parts, from the executor's candidates, all adopted. (a) GATE CLAUSE
GRANULARITY: the gate bundled verdict-routing clauses with descriptive
clauses, so a descriptive bias with a solved mechanism stopped a leg
whose routing machinery is exact. Convention: gates separate ROUTING
clauses (A1-stopping) from DESCRIPTIVE clauses (failure → the
descriptive is reported WITH its dual-stamped bias annotation per #67,
never a stop). (b) ESTIMAND NAMING (#59/#81 family): "author main
share" was in fact the MARGINAL author share; budget components name
their estimand exactly, and marginal estimands are gate-scored against
MARGINAL targets (planted value + the design-composition term,
computable from the skeleton). (c) DF PINNING: a projection estimator's
dimension loss is pinned; the df-corrected share routes, the raw share
is co-reported (#67 dual stamp). Also noted: the #83 baseline is now 4
pre-existing collisions — the fourth introduced by the PLANNER's own
adjudication commit quoting the flagged word; the policy absorbed it
correctly, and the lesson (do not quote flagged usernames into
committed prose, even common-word ones) is recorded here without a
number.

**Executor discipline noted:** seeds deliberately NOT re-chosen after
the failure (gate-shopping refused a second time); the FE stopping rule
tightened so BOTH residual group means are ≤ 1e-10 on exit; the
bootstrap-FE weighted-projection equivalence proven by contract test.

---

## X1c — the venue response, clause-separated gate (registered BEFORE run, 2026-08-19)

Third and final registration of this estimand. Everything inherits
X1b (design chain at s = 5: 3,665 × 1,000, 31,899 shared pairs,
LCC 1.000; exact-FE estimator; arms; cells; leans; boundaries;
governance) except the following #86-compliant changes:

1. **Gate restructure (#86a).** ROUTING clauses (A1-stopping):
   df-corrected interaction-share recovery within max(0.01, 3·rep sd);
   null-world share CI covers 0 with point inside the permutation band;
   null-world R inside its band; both ablation leakages < 0.005; the
   #85b bootstrap-zero clause. DESCRIPTIVE clauses (report-gated):
   marginal author and community shares scored against their MARGINAL
   TARGETS — planted value plus the design-composition term, both
   derived from the skeleton with pinned formulas (the executor pins
   and prints the derivation); a descriptive failure annotates, never
   stops.
2. **Estimand naming and correction (#86b/c).** The verdict routes on
   the DF-CORRECTED reproducible interaction share:
   share_corr = share_raw · P/(P − A − C + 1) (numerics pinned from
   the realized skeleton). Raw co-reported (#67). Cell boundaries
   unchanged (0.02 / 0.10 on share_corr). R unchanged. The budget
   table reports the MARGINAL author/community shares under that name
   with their design-composition bias annotations, plus the
   FE-interaction rows.
3. Everything else — B_perm = 499, B_boot = 1000, SEED = 20260819,
   seeds inherited, standard six, ONE commit
   `feat(m4-x): X1c — the venue response, clause-separated gate —
   <VERDICT>`, suite green (1410 + new), #83 scan (baseline 4
   pre-existing) — verbatim from X1b.

## X1c outcome (executor, 2026-08-19)

**VERDICT — `RESPONSE_TRACE`.** Part 0's five ROUTING clauses all passed, the
two DESCRIPTIVE clauses passed as well, the A1 stop did not fire, and the real
arms ran. Crossing #2 has its first corpus reading: on the primary arm the
DF-CORRECTED reproducible author × community interaction carries **0.0190** of
comment-level Var(y), cluster-bootstrap CI **[0.0171, 0.0193]**, permutation
band [−0.0016, 0.0017]; raw **0.0162** [0.0146, 0.0165] under the #67 dual
stamp. **R = 0.2788** [0.2598, 0.2934] against a permutation band
[−0.0161, 0.0152]. The interaction is DETECTED and it is SMALL — the whole CI
sits below the 0.02 TRACE/IDIOSYNCRATIC boundary, so the cell is not a
straddle.

Harness `scripts/run_suica_m4_x1c_venue_response.py`; tests
`tests/test_m4_x1c_venue_response.py` (45); artifacts
`results/m4_x1c_venue_response/` (gitignored); report
`reports/SUICA_M4_X1C_VENUE_RESPONSE_REPORT.md`. Runtime about 121 s end to
end, entirely off X1's committed 13.6 MB cell cache — the 17.6M-row comments
file was not re-streamed for the third leg running. SEED 20260819, B_perm 499,
B_boot 1000, seeds inherited and not re-chosen.

### Anchors (#78) — all nine, exact

17,640,062 parseable rows; 10,296 authors = 1,401 Big5 + 8,895 disjoint;
vocabulary floor 89 giving exactly 1,443 law communities; the predicate chain
at s = 3 / 5 / 8 giving 3,686 / 1,145 / 32,415, **3,665 / 1,000 / 31,899**
and 3,595 / 780 / 30,561, with **0 singleton communities and LCC author
coverage 1.000** at the primary floor. Attrition at s = 5: 140,026 eligible
cells → 37,414 shared pairs → 36,612 → 31,899 → 31,899 (already connected
before the LCC step). The alternating projection converges in 31 sweeps per
half on the corpus arm with residual author means ≤ 4.9e-11 and residual
community means ≤ 6.3e-17.

### The gate, separated (#86a)

| family | clause | value | status |
|---|---|---|---|
| ROUTING | (i) recovery, DF-CORRECTED interaction | 0.0199 for 0.0200, gap −0.0001, tol 0.0100 | PASS |
| ROUTING | (ii) null world — share CI covers 0 AND point inside band | CI [−0.0004, 0.0002]; −0.0001 in [−0.0012, 0.0012] | PASS |
| ROUTING | (iii) null world — R inside band | 0.0078 in [−0.0166, 0.0166] | PASS |
| ROUTING | (iv) ablations — author-only and community-only leakage | 0.0001 and 0.0001, both < 0.0050 | PASS |
| ROUTING | (v) #85b bootstrap-zero | the null CI covers 0 and its own point | PASS |
| DESCRIPTIVE | marginal AUTHOR share vs its MARGINAL TARGET | 0.3220 for a target of 0.3267, gap −0.0047, tol 0.0179 | PASS |
| DESCRIPTIVE | marginal COMMUNITY share vs its MARGINAL TARGET | 0.1072 for a target of 0.1077, gap −0.0006, tol 0.0424 | PASS |

**The df correction, pinned.** P = 31,899, A = 3,665, C = 1,000, rank removed
A + C − 1 = 4,664, residual df 27,235, retained fraction 0.8538, factor
**1.1712502**. It converts a raw recovery of 0.0170 (gap −0.0030 against the
planted 0.0200) into 0.0199 (gap −0.0001). X1b's prediction of the projection
loss is confirmed to the fourth decimal by an estimator that now corrects for
it.

**The marginal targets, derived and printed.** The estimator of a main share
is a cross-half covariance of size-weighted half-means, so it targets the
planted component PLUS the unit's own composition average of everything else
that persists. With `w[u,c,h] = n[u,c,h] / Σ_c' n[u,c',h]`,
`t[u,c,h] = n[u,c,h] / Σ_u' n[u',c,h]`, `κ_u = Σ_c w[u,c,e] w[u,c,l]`,
`λ_c = Σ_u t[u,c,e] t[u,c,l]` and `Ŵ_c` the normalized `n[c,e] + n[c,l]` size
weights the budget already uses:

```
T_a = v_a (1 − 1/A) + (v_c + v_g)·mean_u[κ_u]
      − v_c·Σ_c w̄[c,e] w̄[c,l] − v_g·mean_u[κ_u]/A
T_c = v_c (1 − Σ_c Ŵ_c²) + v_a·(Σ_c Ŵ_c λ_c − Σ_u φ[u,e] φ[u,l])
      + v_g·(Σ_c Ŵ_c λ_c − Σ_c Ŵ_c² λ_c)
```

On the realized skeleton mean_u[κ_u] = **0.2905**, which is **52% larger** than
the 1/k_u heuristic X1b used (0.1909) — the gap is entirely cell-size
inequality, and it is why X1b's first-order prediction (+0.0191) undershot the
observed bias (+0.0220) while the exact term (+0.0290 composition − 0.0024
mean-removal = +0.0267) brackets it. Author target 0.3267, community target
0.1077 (size-weighted mean_c[λ_c] = 0.0937). Scored against the PLANTED
components instead — X1b's clause — the author gap is +0.0220 against a
tolerance of 0.0179 and that clause still FAILS, exactly as before: #86a is
what let the leg through, and the estimator was not quietly changed to make it
pass. The NULL world scores its own targets as a free cross-check and passes
both (author 0.3220 for 0.3209; community 0.1139 for 0.1059). The derivation
was verified against simulation on both a synthetic design (contract test) and
the realized skeleton (48 replicates: author 0.3262 ± 0.0008 se against a
target of 0.3267, community 0.1084 ± 0.0020 against 0.1077).

### The corpus reading

PRIMARY arm: 3,665 disjoint authors × 1,000 law communities, 31,899 shared
pairs, 63,798 eligible cells, 6,811,576 comments, comment-level
Var(y) = 1.2423.

| quantity | value | CI | band |
|---|---|---|---|
| interaction share, DF-CORRECTED (routes) | **0.0190** | [0.0171, 0.0193] | [−0.0016, 0.0017] |
| interaction share, raw (#67) | 0.0162 | [0.0146, 0.0165] | [−0.0014, 0.0015] |
| R | **0.2788** | [0.2598, 0.2934] | [−0.0161, 0.0152] |
| MARGINAL author share | 0.1804 | [0.1729, 0.1882] | — |
| MARGINAL community share | 0.0928 | [0.0898, 0.1075] | — |
| residual | 0.7106 | [0.6931, 0.7180] | — |

Both of cell 1's conditions are refused: R is far outside its band and the
share's CI excludes 0. The mains are reported under their true name — this
arm's composition weights are κ̄ = 0.2905 and λ̄ = 0.0937, so inverting the
2 × 2 mixing as an ANNOTATION ONLY (not a registered estimand, nothing routes
on it) implies an author main near 0.1526 and a community main near 0.0767.

| arm | corrected share [CI] | R | cell | #73 |
|---|---|---|---|---|
| PRIMARY (n=10, s=5, wcq) | 0.0190 [0.0171, 0.0193] | 0.2788 | RESPONSE_TRACE | — |
| s = 8 | 0.0189 [0.0172, 0.0193] | 0.2738 | RESPONSE_TRACE | none |
| n_min = 5 | 0.0208 [0.0192, 0.0214] | 0.2192 | IDIOSYNCRATIC_RESPONSE (STRADDLE) | **#73** |
| y = word_count | 0.0188 [0.0170, 0.0191] | 0.2777 | RESPONSE_TRACE | none |
| Big5 replication (408 authors) | 0.0177 [0.0131, 0.0189] | 0.2823 | RESPONSE_TRACE | none |

The five arms span 0.0031 of total variance. The single #73 is a BOUNDARY
CROSSING: the n_min = 5 arm's CI [0.0192, 0.0214] touches both cells and is
reported as a straddle, with its point at 0.0208 placing it in
IDIOSYNCRATIC_RESPONSE. The Big5 replication carries 408 authors, above the
in-leg #69 floor of 300, and lands in the primary cell — the replication lean
is scored and HELD rather than waived.

**All five registered leans HELD** (six rows, because the share lean is
reported on both scales): R = 0.2788 in (0.05, 0.30]; the interaction share in
(0.005, 0.05] on the RAW scale the lean was written for (0.0162) and also on
the corrected scale the verdict routes on (0.0190); the marginal author share
0.1804 in [0.15, 0.45]; the marginal community share 0.0928 in [0.02, 0.15];
the Big5 replication in the primary cell. The registration's own reasoning —
"personal baseline × venue norm is additive in log and lands in the mains, so
the interaction asks for more" — is vindicated: the interaction is real and it
is second-order.

**Headroom, about the MEAN (#84 as restated by #85).** 3,665 authors scored,
0 undefined; realized per-author correlation mean 0.2788, sd 0.5021, median
0.3501, 2.76% above 0.99, 9.55% above 0.90, 73.64% positive, extremes at
±1.0000. Per-author saturation is acknowledged and is NOT a ceiling: at k = 3
a three-point correlation reaches ±1 whenever three points line up. The
bounded object is the mean, and it separates cleanly from Part 0's synthetic
null world (0.2788 against 0.0078).

### Honest anomalies

1. **The cluster-bootstrap interval is not symmetric about its point**; every
   arm's point sits near the upper edge (primary: point 0.0162 raw against a
   bootstrap mean of 0.0155). The mechanism is the resample's sparsity — a
   bootstrap author multiset holds about 63% of the distinct authors, so each
   replicate's projection removes a larger fraction of its own design than the
   full design's, while the pinned factor stays at the realized skeleton's
   value (which is what the registration fixes). The direction is CALIBRATED,
   not argued: Part 0's planted world has a known truth of 0.0200 and shows
   the same asymmetry — point 0.0204, interval [0.0188, 0.0206] — and still
   covers it. The corpus intervals are therefore conservative on the low side
   only, and no cell assignment is at risk.
2. **The estimand lives on the cell boundary.** Four arms sit at 0.0177–0.0190
   and one at 0.0208, against a registered boundary of 0.0200. The cells did
   their job, but the leg's headline is a few thousandths of total variance
   from a different label.
3. Non-gating, inherited from X1: the two census descriptives that did not
   reproduce in X1 (within-cell sd; median shared communities) were not
   re-examined here.

### Deviation

X1b's X1-versus-X1b estimator-comparison grid was NOT re-run. It was a
one-time demonstration of the repair, already adjudicated, and re-running it
would add nothing to a leg whose purpose is the corpus reading; X1b's
artifact holds it. Nothing else in the registration was skipped, and nothing
was added to the routing path.

### Defect candidates recorded for the planner (nothing below was run)

1. **The df factor is pinned at the realized design and does not follow the
   bootstrap.** The registration is explicit that P/A/C come from the realized
   skeleton, and that is what was done; the consequence is anomaly 1. A future
   registration can either correct each replicate by its OWN residual-df
   fraction, or declare the interval one-sidedly conservative — which is what
   this report does, with the planted world as its calibration.
2. **The mains are now correctly NAMED but still not ESTIMATED.** #86b gave
   the marginal estimators exact targets; it did not give the leg an estimator
   of Var(a) or Var(b). The 2 × 2 inversion printed here is arithmetic on the
   design, not an estimator with a null or a CI. Any leg that wants the mains
   as objects — X3's trait join is the obvious one — needs them read off the
   same two-way projection that now carries the interaction, with their
   sampling variance removed, and registered with their own gate.
3. **Cell boundaries drawn before the estimand's scale was known.** The
   0.02 / 0.10 boundaries were set in X1 on literature priors; the corpus
   answer landed within 0.001 of the first one, and one arm crossed it. A
   planner may wish to register a boundary REGION (report both cells when the
   CI touches both) rather than a point, so that "straddle" is a first-class
   outcome and not an annotation on a cell.

### Governance

Metadata only; `word_count_quoteless` and `word_count` are the sole
text-derived quantities; no body was read; `author_profiles.csv` was never
opened. The ID-leak scan over all 10,296 author names cleared with **0 NEW
hits** (4 pre-existing dictionary collisions carried unchanged from HEAD:
three in `CLAIMS_LEDGER.md`, one in this plan). Every boundary is carried
forward, plus the one X1c adds: the routing statistic is DF-CORRECTED and the
two main shares are MARGINAL, named and annotated as such on every table.

## X1c planner adjudication + the X1 arc CLOSES (2026-08-19)

**Verdict ACCEPTED: `RESPONSE_TRACE`, with the boundary-region
annotation adopted as part of the verdict.** Routing 5/5 (df-corrected
recovery at gap −0.0001), descriptive 2/2 against the exact marginal
targets — and the executor's integrity demonstration is noted with
approval: scored against X1b's planted-component clause the author gap
STILL fails (+0.0220), so the gate structure, not a quietly changed
estimator, is what let the leg through. Both readings printed side by
side. The marginal-target derivation went past the planner's
first-order heuristic (κ̄ = 0.2905 vs 1/k̄ = 0.1909 — cell-size
inequality explains X1b's undershoot) and was verified by simulation
twice.

**Crossing #2's first corpus reading, formalized.** Expression volume
is venue-conditioned in three layers on this corpus: the personal
baseline (marginal share 0.1804; 2×2-inverted true main ≈ 0.153), the
venue norm (0.0928; ≈ 0.077), and a SMALL, REAL, PERSISTENT
idiosyncratic response: **df-corrected reproducible interaction share
0.0190 [0.0171, 0.0193] against a ±0.0017 band; profile persistence
R = 0.2788 [0.2598, 0.2934] against ±0.016; 73.6% of authors
positive; REPRODUCED on the Big5 cohort (0.0177, same cell, lean
held).** The response operator's first projection is NON-EMPTY — the
first crossing where the personal second-order channel is present
rather than silent. All five registered leans HELD, on both the raw
scale the lean was written for and the corrected scale the verdict
routes on. The registration's reasoning stands: multiplicative
baseline × norm lands in the mains; the interaction asked for more,
and the corpus has more — about 1.9% of variance worth.

**The honest fragility, carried into the verdict.** The estimand lives
ON the registered boundary: arms span 0.0177–0.0208 against the 0.0200
line set from literature priors; one #73 straddle (n_min = 5 at 0.0208
[0.0192, 0.0214]). The DETECTION is unambiguous (CI 10× outside the
band); the LABEL is boundary-sensitive. Licensed sentence: "a real,
persistent idiosyncratic venue response at the TRACE/IDIOSYNCRATIC
boundary (≈ 2% of variance)" — never the bare cell name without the
boundary note.

**Defect #87 (planner, purchased; registry thirty-fourth note).** Two
parts. (a) Cell boundaries were registered as POINTS from literature
priors with no boundary-region provision, and the corpus landed within
0.001 of one — "straddle" had to work as an annotation where it
deserves first-class status. Convention: every effect-size
classification registers a BOUNDARY REGION (default: ± the projected
CI half-width) inside which the verdict IS the region statement
("AT the boundary"), first-class, not an annotation. (b) The pinned df
factor is not recomputed per bootstrap replicate, making the interval
one-sidedly conservative — the executor calibrated this against the
planted world (truth covered; low side only) rather than arguing it.
Convention: projection-dependent corrections are recomputed inside
every resample, or the one-sided conservatism is declared WITH a
planted-world calibration. Also adopted from the executor's
candidates: any leg wanting the MAINS as objects (X3's trait join)
must first build main ESTIMATORS (the marginals are now correctly
named but still not estimators of Var(a)/Var(b)) under their own gate.

**The X1 arc closes: X1 (A1 stop, projection leak caught) → X1b
(A1 stop, routing machinery certified, descriptive mechanism solved) →
X1c (reading).** Three registrations, two stops, zero real-data
contamination, one boundary-honest reading — the gate discipline's
full showcase, with defects #85–#87 as its tuition. The X-line
continues: X2 (What × When paths of expression volume) and X3 (the
stage-E trait join, now with a validated coordinate and the
main-estimator prerequisite) are named, not queued.

---

## X2 — the path of expression volume (registered BEFORE run, 2026-08-19)

Crossing #3 (What × When): the first real-data projection of expression
STATE TRAJECTORIES — does expression volume have reproducible path
structure in event time, and is the path parameter an AUTHOR attribute?
Metadata-only, as the line charter binds.

### 4W header

- **Object.** The lag-1 event-time autocorrelation of y = log1p(wcq)
  within an author-half — one static projection of the What × When
  trajectory kernel; the eq-12 projection caution binds (a flat r1 does
  not falsify dynamics; it is a statement about this projection).
- **Fixed.** y pinned (#70); per-author stable order by created_utc
  (ties keep stream order); halves by full-stream median (≤ early);
  adjacency = consecutive events WITHIN a half (never across the
  boundary); r1 per (author, half) requires sd > 0 (censused: zero
  degenerate halves).
- **Varied.** Raw adjacency vs cross-thread-only (link_id differs) vs
  venue-residualized (y minus the global community-half mean b̄_{c,h}
  computed over ALL events in that community-half); cohort (disjoint
  primary, Big5 replication); pool floor 50 vs 100 events/half.
- **What falsifies.** Ownership ρ_own CI including 0 → the path
  parameter is not an author attribute at this power (PATH_NOT_OWNED).
- **Layer.** R.

### Census (planner arithmetic #43; #77/#78 exact; #57 — NO estimand
value was evaluated: r1 was never computed; degenerate halves counted
by sd = 0 alone)

| quantity (exact predicate) | disjoint | Big5 |
|---|---|---|
| pool: ≥ 50 events in EACH half (all events) | **8,008** | **1,116** |
| cross-thread share of within-half adjacencies | 0.73159 | 0.62054 |
| degenerate halves (sd = 0) | 0 | 0 |
| median adjacencies per half | 348.0 | 491.75 |
| ownership width projection (analytic 1/√N) | ±0.0112 | ±0.0299 |

Inherited anchors: 17,640,062 parseable rows; 10,296 authors
(1,401 + 8,895). Per-half r1 sampling noise (analytic): ≈ 1/√348 ≈
0.054 — named as the attenuation floor on ρ_own (the ownership
correlation reads the attenuated per-half parameter; no disattenuation
is registered — raw ρ_own routes).

### Estimands (own nulls #68/#66; transforms pinned #70)

1. **Path presence (co-reports):** mean over (author, half) of r1,
   against the MARGINAL-PRESERVING within-half permutation null
   (each half's y sequence permuted; the per-half marginal is EXACTLY
   invariant — contract test, the U1 exact-bag pattern on a scalar);
   B = 499; band = 2.5/97.5 percentiles.
2. **Ownership ρ_own (ROUTES):** Pearson over pool authors of
   (r1_early, r1_late). Own null: author pairing permuted between
   halves, B = 499. Cluster bootstrap over authors B = 1000 for the CI.
3. Arms as above; each arm carries its own presence + ownership pair.

### Gate (Part 0, #85/#86-compliant, on the REALIZED skeleton — real
per-author sequence lengths and half splits, wholly synthetic y)

ROUTING clauses (A1-stopping): (i) ownership recovery on a planted
world — per-author AR(1) with author-owned φ_u at a #76-declared
operating point (across-author ownership ρ_true = 0.5; 8 replicates;
tol max(0.02, 3·rep sd)); (ii) the COMMON-PATH null world (every author
the same φ̄ > 0: presence WITHOUT ownership — ρ_own CI must cover 0,
point inside band; the design's decisive honesty check); (iii) the iid
world (no path at all: mean r1 inside band AND ρ_own inside band);
(iv) marginal-preservation contract (bit-exact per-half marginals under
the shuffle); (v) #85b bootstrap-zero on the common-path world.
DESCRIPTIVE clauses (annotate, never stop): mean-r1 recovery against
the planted φ̄ mapping on both non-null worlds.

### Cells (NULL-first #55; effect-size keyed #75; #87 boundary REGIONS
declared: half-width = the projected CI half-width, 0.011 primary)

On ρ_own (primary arm): 1 **PATH_NOT_OWNED** — CI includes 0 or point
below 0.15 − 0.011; **AT_BOUNDARY(0.15)** — point inside
[0.139, 0.161] (first-class verdict); 2 **WEAKLY_OWNED** —
(0.161, 0.489); **AT_BOUNDARY(0.50)** — [0.489, 0.511]; 3
**STRONGLY_OWNED** — above 0.511 (the U3 reliability-gate level:
trait-join eligible). Presence co-reports with its own band. Arm
divergences carry #73 flags; the primary routes.

### Registered leans

- Presence: mean r1 positive and clearly detected (session structure
  alone should produce it) — magnitude deliberately un-leaned (#57:
  no pilot was taken).
- Ownership: ρ_own ∈ (0.30, 0.60] — WEAKLY_OWNED toward the upper
  boundary; rationale: the U3 slow-coordinate reliabilities ran
  0.77–0.94, but r1's per-half sampling noise (≈ 0.054) attenuates,
  and rhythm is plausibly less stable than level.
- Cross-thread arm retains most of the ownership (rhythm is not just
  reply mechanics) — held moderately; the U1 precedent (43.8%
  mechanics) prices the alternative.
- Venue-residualized arm retains most (rhythm is not venue-routing).
- Big5 replication: same cell (#73 if divergent).

### Deliverables and discipline

Standard six: `scripts/run_suica_m4_x2_volume_path.py` + tests
(marginal-preservation bit-exactness; AR-world construction and the
common-path null's honesty on a toy; ownership/pairing-permutation
correctness; anchors; #83 helper); gitignored
`results/m4_x2_volume_path/` (fresh event cache: author, created_utc,
link hash, y — anchors above); report
`reports/SUICA_M4_X2_VOLUME_PATH_REPORT.md` (rule-24; gate table with
ROUTING/DESCRIPTIVE sections; presence + ownership per arm with bands
and CIs; boundaries: metadata-only, expression VOLUME not content, the
projection caution, no psychological naming, cohort caveat); outcome
appended here; one CLAIMS_LEDGER row; ONE commit
`feat(m4-x): X2 — the path of expression volume — <VERDICT>`; suite
green (1455 + new); #83 scan (baseline 4 pre-existing).
SEED = 20260819; B_perm = 499; B_boot = 1000.

---

## X2 outcome (executor, 2026-08-19)

**`WEAKLY_OWNED`.** All five ROUTING clauses of Part 0 passed and both
DESCRIPTIVE clauses annotated cleanly, so the A1 stop did not fire and
crossing #3 has its first corpus number. Runtime about 640 s (one stream pass
over the 17,640,062-row comments file, then everything vectorised off a
fresh gitignored event cache).

### The census reproduced the planner's table to the unit (#78)

| registered predicate | registered | observed |
|---|---|---|
| rows parseable | 17,640,062 | 17,640,062 |
| authors (Big5 + disjoint) | 10,296 (1,401 + 8,895) | 10,296 (1,401 + 8,895) |
| pool ≥ 50 events in EACH half, disjoint | 8,008 | 8,008 |
| pool ≥ 50 events in EACH half, Big5 | 1,116 | 1,116 |
| cross-thread share of within-half adjacencies, disjoint | 0.73159 | 0.73159 |
| cross-thread share of within-half adjacencies, Big5 | 0.62054 | 0.62054 |
| degenerate halves (sd = 0) | 0 / 0 | 0 / 0 |
| median adjacencies per half | 348.0 / 491.75 | 348.0 / 491.75 |

Definition pinned by the anchor: "median adjacencies per half" is the
MEDIAN OVER AUTHORS of the MEAN of that author's two half adjacency
counts. The Big5 quarter-fraction 491.75 is reachable no other way, and
that is what fixed the reading. In-leg census: the floor-100
sensitivity pool is **6,863** disjoint authors; the primary arm carries
16,016 cells, 14,586,457 events and 14,570,441 within-half adjacencies;
the cross-thread arm keeps 10,659,581 of them. Zero cells were
undefined and zero authors were dropped on any arm.

### Part 0 — the gate on the realized skeleton (wholly synthetic y)

| # | ROUTING clause | observed | status |
|---|---|---|---|
| i | ownership recovery, author-owned AR(1) at planted ρ_own = 0.50 | 0.4977 over 8 replicates (sd 0.0119), gap −0.0023, tolerance 0.0357 | **PASS** |
| ii | COMMON-PATH null world: presence WITHOUT ownership | ρ_own +0.0085, CI [−0.0197, 0.0384], band [−0.0203, 0.0217] | **PASS** |
| iii | iid world | mean r1 −0.004565 in [−0.005659, −0.003678]; ρ_own +0.0131 in [−0.0225, 0.0234] | **PASS** |
| iv | marginal preservation, BIT-EXACT | 16,016 cells; multisets bit-exact; the index array is a permutation; no index leaves its own cell | **PASS** |
| v | #85b bootstrap-zero on the common-path world | CI [−0.0197, 0.0384] covers 0 and covers its own point | **PASS** |

| # | DESCRIPTIVE clause | observed |
|---|---|---|
| D1 | mean-r1 recovery, AR(1) world | +0.1927 observed vs +0.1923 predicted (Marriott–Pope) |
| D2 | mean-r1 recovery, common-path world | +0.1918 observed vs +0.1925 predicted |

The **ownership mapping** was derived, printed and solved rather than
tuned. With g(φ) ≈ φ and Bartlett's Var(r1) = (1 − φ²)/n, the per-half
errors carry no cross-half covariance, so ρ_own = V / √((V+A_e)(V+A_l))
with A_h = (1 − φ̄² − V)·E_u[1/(n_{u,h} − 1)]. On the realized skeleton
m_e = 0.00465751, m_l = 0.00467906, and the bisection solution at
φ̄ = 0.20, ρ = 0.50 is V = 0.00446072, i.e. **sd(φ_u) = 0.066789** —
the readable special case V = A (plant exactly as much across-author φ
variance as the estimator's own sampling variance). The COMMON-PATH
world is the design's decisive honesty check and it behaved: presence
0.1918 — as strong as the owned world's 0.1927 — with ρ_own +0.0085 and
a CI covering zero. A world with a path but no owner was **not** called
owned.

### The corpus reading

| arm | authors | adjacencies | presence mean r1 | band | ρ_own | CI | pairing band | cell |
|---|---|---|---|---|---|---|---|---|
| **PRIMARY** raw adjacency, disjoint | 8,008 | 14,570,441 | **+0.1111** | [−0.005635, −0.003648] | **0.2589** | [0.2273, 0.2921] | [−0.0228, 0.0213] | `WEAKLY_OWNED` |
| cross-thread only | 8,008 | 10,659,581 | +0.0545 | [−0.006454, −0.003859] | 0.1062 | [0.0713, 0.1394] | [−0.0200, 0.0209] | `PATH_NOT_OWNED` **#73** + **#87 straddle** |
| venue-residualized | 8,008 | 14,570,441 | +0.0917 | [−0.005820, −0.003643] | 0.2204 | [0.1864, 0.2534] | [−0.0225, 0.0213] | `WEAKLY_OWNED` |
| Big5 replication | 1,116 | 2,989,174 | +0.1773 | [−0.006953, −0.001800] | 0.6367 | [0.5894, 0.6785] | [−0.0572, 0.0549] | `STRONGLY_OWNED` **#73** |
| floor-100 sensitivity | 6,863 | 14,402,480 | +0.1150 | [−0.003999, −0.002226] | 0.3341 | [0.2977, 0.3653] | [−0.0246, 0.0251] | `WEAKLY_OWNED` |

**PRESENCE is unambiguous on every arm** — the primary's mean r1 sits
about 58 band-widths above the upper edge of its own
marginal-preserving band. **OWNERSHIP routes at 0.2589**, a CI that
clears the 0.161 region edge by 0.066 and the 0.489 edge by 0.197: the
primary cell is `WEAKLY_OWNED` and it is **not** a straddle. Retention
ratios: venue-residualized **0.8516**, cross-thread **0.4104**.

### Leans: two held, three broke

| lean | registered | observed | status |
|---|---|---|---|
| presence positive and detected (magnitude un-leaned, #57) | > 0 and outside the band | +0.1111 vs [−0.005635, −0.003648] | **HELD** |
| ρ_own ∈ (0.30, 0.60] | (0.30, 0.60] | 0.2589 | **BROKEN** (low) |
| cross-thread retains most | ≥ 0.50 | 0.4104 | **BROKEN** |
| venue-residualized retains most | ≥ 0.50 | 0.8516 | **HELD** |
| Big5 same cell | `WEAKLY_OWNED` | `STRONGLY_OWNED` | **BROKEN** (high) |

The ownership lean broke LOW and the Big5 lean broke HIGH, which is one
fact seen twice — see the attenuation arithmetic below.

### Attenuation arithmetic (ANNOTATION; nothing routes on it)

The registration named the attenuation and refused to correct for it.
Inverting the SAME first-order model Part 0 plants — A from each arm's
own pair counts and its own mean r1, then V from its own ρ_own — reads:

| arm | median pairs/cell | A | implied Var(φ) | implied sd(φ) |
|---|---|---|---|---|
| primary | 348.0 | 0.004600 | 0.001610 | 0.0401 |
| cross-thread | 266.0 | 0.006169 | 0.000740 | 0.0272 |
| venue-residualized | 348.0 | 0.004618 | 0.001309 | 0.0362 |
| Big5 | 492.0 | 0.004154 | 0.007303 | 0.0855 |
| floor-100 | 447.0 | 0.003034 | 0.001524 | 0.0390 |

Three readings follow, and they are the leg's real content beyond the
cell. (1) The **floor-100 arm is the primary at a better precision**:
0.3341 against 0.2589, but the implied Var(φ) agrees to 5%
(0.001524 vs 0.001610). Two ρ, one object. (2) The **Big5 divergence is
NOT attenuation**: its A is if anything smaller, and its implied Var(φ)
is **4.5×** the primary's, with the higher presence to match
(0.1773 vs 0.1111). The label-carrying cohort genuinely has more
across-author dispersion in this path parameter than the disjoint
cohort does. (3) The **cross-thread loss is not only arithmetic**: its
implied Var(φ) is 46% of the primary's on top of a larger A, so a real
part of the owned rhythm is reply-chain mechanics — U1's 43.8%
precedent priced this and the lean paid.

### Honest anomalies

- The presence permutation band sits **entirely below zero**. A uniform
  permutation of a finite sequence has a small negative expected lag-1
  correlation; the primary's null mean is −0.004680 against the
  analytic offset −E[1/pairs] = −0.004668. It is a bias-offset band,
  not a zero band. Detection is untouched.
- The Big5 arm reads **above the trait-join-eligible level** (0.6367,
  CI entirely above 0.511) while the primary does not. Whatever X3
  intends to join, it will join it on the cohort that reads
  `STRONGLY_OWNED`, and the two cohorts do not agree.
- The cross-thread cell is a **#87 straddle**: its CI crosses 0.139, so
  `PATH_NOT_OWNED` there is boundary-sensitive and should be read as
  "at or below the low boundary", not as a clean null.
- The cluster-bootstrap interval is asymmetric about its point on the
  null world (+0.0085 inside [−0.0197, 0.0384]) — X1c's asymmetry,
  unchanged, conservative on the side that matters, and far from every
  region edge on the primary.

### Boundaries carried

Metadata only, expression VOLUME and not content (permanent — no body
was read); the What × When projection caution (r1 is ONE static
projection of the trajectory kernel, so 0.2589 is a lower bound on the
kernel's ownership and a flat r1 would not have falsified dynamics); no
psychological naming; EXPLORATORY corpus-level, no person claims; the
disjoint cohort is TYPOLOGY-ENRICHED by construction; the attenuation
note (raw ρ_own routes, no disattenuation); and NEW — the pool floors
at 50 events in EACH half, so the leg speaks only for authors active on
both sides of their own median.

### Deviations and defect candidates (none run)

- **Deviation (recorded):** the leg builds its OWN event cache rather
  than reusing X1's. X1's cache aggregates over (author, community,
  half) and carries neither event order nor `link_id`, so it cannot
  serve a path estimand. One stream pass, five metadata columns, no
  bodies.
- **Deviation (recorded):** two unregistered ANNOTATIONS are printed —
  a cluster-bootstrap interval on the presence mean, and the
  attenuation arithmetic above. Both are labelled in the report; the
  verdict touches neither.
- **Defect candidate (#87 follow-on):** the registered region
  half-width 0.011 was the ANALYTIC 1/√N projection, and the realized
  cluster-bootstrap half-widths are 0.032 (primary) and 0.045 (Big5) —
  three to four times wider. A region set from the analytic width
  under-covers the interval it is meant to price; future legs should
  set the region from the REALIZED interval or say why not.
- **Defect candidate:** presence and ownership are reported per arm,
  but the arms' pool sizes differ (8,008 / 6,863 / 1,116), so the
  cross-arm comparison is partly a precision comparison. A leg that
  wants arms comparable should match precision, not just floor it.
- **Defect candidate:** the lag-1 projection is one coordinate. The
  Big5/disjoint dispersion gap (4.5×) is the kind of thing that could
  be a genuine cohort difference or a selection artifact of how the
  1,401 were sampled; neither this leg nor X1 can separate them.

## X2 planner adjudication (2026-08-19)

**Verdict ACCEPTED: `WEAKLY_OWNED`** — ρ_own = 0.2589 [0.2273, 0.2921],
clean of both boundary regions (clears the 0.161 edge by 0.066); the
gate passed FIRST TRY, all five routing clauses, with the decisive
common-path clause doing exactly its job (presence 0.1918 in the
unowned world, as strong as the owned world's 0.1927, and the gate
refused to call it owned). The ownership mapping was derived and
bisection-solved, not tuned — and the executor's Marriott–Pope
small-sample handling of the r1 bias (the presence null band sits at
the analytic −E[1/pairs], an offset band, not a zero band) is exactly
the standard the line now runs at. The X1-arc tuition (#85–#87) bought
X2 a clean first gate.

**Crossing #3's first reading, formalized.** Expression volume has REAL
path structure in event time (presence +0.1111, ~58 band-widths out),
and the rhythm parameter is an author attribute — weakly, on the
disjoint cohort. Retention decomposition: **85.2% of the ownership
survives venue-residualization** (the rhythm is intrinsic, not venue
routing) and **41.0% survives the cross-thread restriction** — with
implied Var(φ) at 46%, a real part of the owned rhythm IS reply-chain
mechanics (U1's 43.8% precedent priced it; the lean broke exactly
there and pays the same lesson twice: fast-time channels are
mechanics-heavy). Lean record: 2 held, 3 broke (ρ_own low of the lean;
cross-thread retention; Big5 cell) — honest, and each break carries
information.

**The flag for X3 (the leg's most consequential row).** The Big5
cohort reads ρ_own = 0.6367 [0.5894, 0.6785] — STRONGLY_OWNED, above
the trait-join-eligible 0.511 line — while the primary reads 0.2589,
and the attenuation arithmetic shows this is NOT precision: implied
Var(φ) is 4.5× the disjoint cohort's, with higher presence too. The
label-carrying cohort genuinely differs on this object. Carried into
X3 with the standing caveat the executor named: neither X1 nor X2 can
separate a genuine cohort difference from a selection artifact of how
the 1,401 were chosen (test-takers may be atypical posters); every X3
claim inherits this caveat verbatim.

**Defect #88 (planner, purchased; registry thirty-fifth note).** Two
parts. (a) The #87 boundary-region half-width was priced from the
ANALYTIC null sd (1/√N = 0.011) while the realized bootstrap
half-widths run 0.032–0.045 — the region under-covers the interval it
prices; the convention is corrected: region widths are priced from the
PROJECTED BOOTSTRAP width of the non-null estimate (#79b machinery),
never from the null sd. (b) Arms with different pool sizes make
cross-arm comparisons partly precision comparisons — the W2
size-matching lesson extends WITHIN legs: cross-arm ownership
comparisons use the implied-variance scale (as the executor's
annotation did) or size-matched subpools. The two unregistered
annotations (presence bootstrap; attenuation arithmetic) are accepted
as labelled.

**Program milestone: every 4W crossing now has a real-data reading.**
Crossing #1 (T/W lines), #2 (X1c), #3 (this leg), #4 (U-line). The 4W
empirical-state document receives its completion addendum with this
commit.
