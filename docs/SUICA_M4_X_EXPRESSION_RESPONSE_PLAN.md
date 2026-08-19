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
