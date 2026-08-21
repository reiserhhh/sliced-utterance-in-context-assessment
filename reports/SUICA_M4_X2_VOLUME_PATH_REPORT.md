# SUICA M4-X2 — the path of expression volume

**Outcome: `WEAKLY_OWNED`.** Crossing #3's first real-data projection. On the primary arm (8,008 disjoint-cohort authors, 14,570,441 within-half adjacencies) the ownership correlation of the per-half lag-1 path parameter is **rho_own = 0.2589** [0.2273, 0.2921] against a pairing-permutation band [-0.0228, 0.0213]; path PRESENCE co-reports at mean r1 = 0.1111 against the marginal-preserving band [-0.005635, -0.003648].

Registration: `docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md`, section "X2 — the path of expression volume (registered BEFORE run, 2026-08-19)", commit 550466f. Run 2026-08-21T00:01:37.475092Z, 630 s.

## Verdict and cell

| field | value |
|---|---|
| cell | `WEAKLY_OWNED` |
| routes on | rho_own, PRIMARY arm (raw adjacency, disjoint pool) |
| Part 0 gate | `PASS` |
| rho_own (primary) | 0.2589 |
| cluster-bootstrap CI (B = 1000, authors) | [0.2273, 0.2921] |
| pairing-permutation band (B = 499) | [-0.0228, 0.0213] |
| #87 region straddle | none |

Registered regions on rho_own (#87, half-width 0.011): `PATH_NOT_OWNED` = CI includes 0 or point < 0.139; `AT_BOUNDARY(0.15)` = [0.139, 0.161]; `WEAKLY_OWNED` = (0.161, 0.489); `AT_BOUNDARY(0.50)` = [0.489, 0.511]; `STRONGLY_OWNED` = above 0.511 (the trait-join-eligible level).

## Census and the blocking anchors (#78)

| registered predicate | registered | observed | status |
|---|---|---|---|
| rows parseable (author+subreddit+created_utc+wcq) | 17,640,062 | 17,640,062 | `PASS` |
| authors | 10,296 | 10,296 | `PASS` |
| Big5 cohort authors seen | 1,401 | 1,401 | `PASS` |
| disjoint authors | 8,895 | 8,895 | `PASS` |
| pool: >= 50 events in EACH half, disjoint | 8,008 | 8,008 | `PASS` |
| pool: >= 50 events in EACH half, Big5 | 1,116 | 1,116 | `PASS` |
| cross-thread share of within-half adjacencies, disjoint (5 dp) | 0.73159 | 0.73159 | `PASS` |
| cross-thread share of within-half adjacencies, Big5 (5 dp) | 0.62054 | 0.62054 | `PASS` |
| degenerate halves (sd = 0), disjoint | 0 | 0 | `PASS` |
| degenerate halves (sd = 0), Big5 | 0 | 0 | `PASS` |
| median adjacencies per half, disjoint | 348 | 348 | `PASS` |
| median adjacencies per half, Big5 | 491.75 | 491.75 | `PASS` |

## Part 0 — the gate on the REALIZED skeleton (wholly synthetic y)

Real per-author sequence lengths and real half splits; every y in this section is planted. No corpus value enters Part 0.

### ROUTING clauses (A1-stopping)

| # | clause | observed | required | status |
|---|---|---|---|---|
| i | ownership recovery on the author-owned AR(1) world (planted rho_own = 0.50) | 0.4977 over 8 replicates (sd 0.0119), gap -0.0023 | abs(gap) <= max(0.02, 3 x rep sd) = 0.0357 | `PASS` |
| ii | the COMMON-PATH null world: presence WITHOUT ownership — rho_own CI covers 0 and the point sits inside the pairing band | rho_own +0.0085, CI [-0.0197, 0.0384], band [-0.0203, 0.0217] | CI covers 0 AND point inside band | `PASS` |
| iii | the iid world: mean r1 inside its permutation band AND rho_own inside its pairing band | mean r1 -0.004565 in [-0.005659, -0.003678]; rho_own +0.0131 in [-0.0225, 0.0234] | both inside | `PASS` |
| iv | marginal preservation: each half's multiset is BIT-EXACTLY invariant under the shuffle | 16,016 cells, bit-exact True, index array a permutation True, never leaves its own cell True | all three exact | `PASS` |
| v | #85b bootstrap-zero on the common-path world: the cluster-bootstrap CI covers 0 AND covers its own point | CI [-0.0197, 0.0384] vs 0 and vs +0.0085 | covers both | `PASS` |

### DESCRIPTIVE clauses (annotate, never stop)

| # | clause | observed | required | status |
|---|---|---|---|---|
| D1 | mean-r1 recovery against the planted phi mapping, author-owned AR(1) world | +0.1927 observed vs +0.1923 predicted (Marriott-Pope) | annotate only, never stops | `ANNOTATED` |
| D2 | mean-r1 recovery against the planted phi mapping, common-path world | +0.1918 observed vs +0.1925 predicted | annotate only, never stops | `ANNOTATED` |

### The ownership mapping (#76 operating point, derived here)

```
rho = V / sqrt((V + A_e)(V + A_l)), A_h = (1 - phi_bar^2 - V) * E_u[1/(n_{u,h} - 1)]
```
| quantity | value |
|---|---|
| phi_bar (mean AR parameter) | 0.2000 |
| m_early = E_u[1/(n_early - 1)] | 0.00465751 |
| m_late = E_u[1/(n_late - 1)] | 0.00467906 |
| A_early (mean sampling variance of r1, early) | 0.00445043 |
| A_late (mean sampling variance of r1, late) | 0.00447102 |
| V = Var_u(phi_u) solving rho_own = 0.50 | 0.00446072 |
| sd(phi_u) planted | 0.066789 |
| rho implied by the solution | 0.500000 |

## Arms — presence and ownership, each against its own null

| arm | authors | cells | adjacencies | presence mean r1 | presence band (B = 499) | detected | rho_own | CI (B = 1000) | pairing band | cell |
|---|---|---|---|---|---|---|---|---|---|---|
| PRIMARY — raw adjacency, disjoint pool | 8,008 | 16,016 | 14,570,441 | 0.1111 | [-0.005635, -0.003648] | yes | 0.2589 | [0.2273, 0.2921] | [-0.0228, 0.0213] | `WEAKLY_OWNED` |
| cross-thread-only adjacency, disjoint pool | 8,008 | 16,016 | 10,659,581 | 0.0545 | [-0.006454, -0.003859] | yes | 0.1062 | [0.0713, 0.1394] | [-0.0200, 0.0209] | `PATH_NOT_OWNED` |
| venue-residualized y, raw adjacency, disjoint pool | 8,008 | 16,016 | 14,570,441 | 0.0917 | [-0.005820, -0.003643] | yes | 0.2204 | [0.1864, 0.2534] | [-0.0225, 0.0213] | `WEAKLY_OWNED` |
| REPLICATION — raw adjacency, Big5 pool | 1,116 | 2,232 | 2,989,174 | 0.1773 | [-0.006953, -0.001800] | yes | 0.6367 | [0.5894, 0.6785] | [-0.0572, 0.0549] | `STRONGLY_OWNED` |
| sensitivity — floor 100 events/half, disjoint pool | 6,863 | 13,726 | 14,402,480 | 0.1150 | [-0.003999, -0.002226] | yes | 0.3341 | [0.2977, 0.3653] | [-0.0246, 0.0251] | `WEAKLY_OWNED` |

Presence carries an unregistered annotation interval (the same author cluster bootstrap applied to the presence mean), printed here so the point is not bare; it routes nothing:

| arm | presence mean r1 | cluster-bootstrap CI (annotation, NOT registered) |
|---|---|---|
| PRIMARY — raw adjacency, disjoint pool | 0.1111 | [0.1094, 0.1127] |
| cross-thread-only adjacency, disjoint pool | 0.0545 | [0.0530, 0.0562] |
| venue-residualized y, raw adjacency, disjoint pool | 0.0917 | [0.0901, 0.0932] |
| REPLICATION — raw adjacency, Big5 pool | 0.1773 | [0.1689, 0.1860] |
| sensitivity — floor 100 events/half, disjoint pool | 0.1150 | [0.1133, 0.1168] |

## Retention of the ownership

| arm | rho_own | retention vs primary | lean (>= 0.50) |
|---|---|---|---|
| cross-thread-only adjacency, disjoint pool | 0.1062 | 0.4104 | BROKEN |
| venue-residualized y, raw adjacency, disjoint pool | 0.2204 | 0.8516 | held |

## Attenuation arithmetic (ANNOTATION — design arithmetic, not an estimator; nothing routes on it)

The registered attenuation note says the per-half r1 carries sampling noise that depresses rho_own, and that the RAW rho_own routes with no disattenuation. This table makes that note quantitative on each arm's own realized skeleton: `A` is the mean sampling variance of r1 implied by the arm's pair counts and its own mean r1, and `Var(phi)` is the across-author path-parameter variance that the arm's rho_own would imply under the SAME first-order model Part 0 plants. It is printed so the arm divergences can be read; it is not an estimator and no verdict touches it.

| arm | median pairs/cell | mean r1 | rho_own | A_early | A_late | implied Var(phi) | implied sd(phi) |
|---|---|---|---|---|---|---|---|
| PRIMARY — raw adjacency, disjoint pool | 348.0 | 0.1111 | 0.2589 | 0.004600 | 0.004621 | 0.001610 | 0.0401 |
| cross-thread-only adjacency, disjoint pool | 266.0 | 0.0545 | 0.1062 | 0.006169 | 0.006288 | 0.000740 | 0.0272 |
| venue-residualized y, raw adjacency, disjoint pool | 348.0 | 0.0917 | 0.2204 | 0.004618 | 0.004640 | 0.001309 | 0.0362 |
| REPLICATION — raw adjacency, Big5 pool | 492.0 | 0.1773 | 0.6367 | 0.004154 | 0.004180 | 0.007303 | 0.0855 |
| sensitivity — floor 100 events/half, disjoint pool | 447.0 | 0.1150 | 0.3341 | 0.003034 | 0.003042 | 0.001524 | 0.0390 |

## Registered leans (report against; they never route)

| lean | registered | observed | status |
|---|---|---|---|
| presence positive and detected against its own band (magnitude deliberately un-leaned, #57) | mean r1 > 0 and outside the permutation band | mean r1 = +0.1111, band [-0.005635, -0.003648] | `HELD` |
| ownership rho_own in (0.30, 0.60] | (0.30, 0.60] | 0.2589 | `BROKEN` |
| the cross-thread arm retains MOST of the ownership | retention >= 0.50 | 0.4104 | `BROKEN` |
| the venue-residualized arm retains MOST of the ownership | retention >= 0.50 | 0.8516 | `HELD` |
| the Big5 replication lands in the SAME cell | WEAKLY_OWNED | STRONGLY_OWNED | `BROKEN` |

## #73 flags

| arm | primary cell | arm cell | rho_own | CI | note |
|---|---|---|---|---|---|
| cross_thread | `WEAKLY_OWNED` | `PATH_NOT_OWNED` | 0.1062 | [0.0713, 0.1394] | #73 divergence; the primary routes |
| big5 | `WEAKLY_OWNED` | `STRONGLY_OWNED` | 0.6367 | [0.5894, 0.6785] | #73 divergence; the primary routes |
| cross_thread | `WEAKLY_OWNED` | `PATH_NOT_OWNED` | 0.1062 | [0.0713, 0.1394] | #87 straddle: the CI crosses region edge(s) 0.139 |

## Honest anomalies

- **the presence permutation band sits entirely BELOW zero.** A uniform permutation of a FINITE sequence has a small negative expected lag-1 correlation, so the marginal-preserving null is a bias-offset band, not a zero band. The primary arm's null mean is -0.004680 against the analytic offset -E[1/pairs] = -0.004668. Detection is untouched: the point sits about 58 band-widths above the upper edge.
- **the Big5 REPLICATION arm reads STRONGLY_OWNED while the primary reads WEAKLY_OWNED (#73).** Rho_own 0.6367 [0.5894, 0.6785] against the primary's 0.2589. This is NOT an attenuation artifact: the two arms' sampling variances are comparable (A ~ 0.004154 vs 0.004600), and the implied across-author path-parameter variance differs by a factor of 4.5. The Big5 cohort also carries the higher presence (0.1773 vs 0.1111). The primary routes; the divergence is a cohort fact, reported and not resolved.
- **the floor-100 sensitivity arm reads higher than the primary.** Rho_own 0.3341 against 0.2589 — the SAME cell, and the gap is what the registered attenuation note predicts: longer halves, less per-half noise. The implied Var(phi) agrees to 5% (0.001524 vs 0.001610), so the two arms are reading one object at two precisions.
- **the cross-thread arm's cell is boundary-sensitive (#87 straddle).** Rho_own 0.1062 [0.0713, 0.1394] crosses the 0.139 region edge, so `PATH_NOT_OWNED` is a straddle verdict and not a clean one. What is NOT ambiguous: the arm's implied Var(phi) is 46% of the primary's, so the loss is not only the smaller adjacency count — a real part of the owned rhythm is reply-chain mechanics, as U1's 43.8% precedent priced.
- **the cluster-bootstrap interval is asymmetric about its point on the null world.** On the common-path world the point is +0.0085 inside [-0.0197, 0.0384] — an interval that covers 0 and its own point but is not centred on it. X1c recorded the same asymmetry; it is conservative on the side that matters here, and the primary's CI is far from every region edge.

## Boundaries

- **Metadata only; expression VOLUME and not content (permanent).** The only text-derived quantity in this leg is `word_count_quoteless`, the author's own-word count per comment. No body was read, no topic, no style, no sentiment. Every claim here is about the RHYTHM OF HOW MUCH is written, never about what is written.
- **The What x When projection caution (eq-12).** `r1` is ONE static projection of the trajectory kernel: the lag-1 event-time autocorrelation of a single scalar. A flat r1 would not falsify dynamics, and a detected r1 is a LOWER bound on the kernel, not a measurement of it. Nothing here speaks about longer lags, about calendar time, or about any other coordinate of the path.
- **No psychological naming.** Verbosity rhythm is a technical expression-volume object. It is not a trait, a state, a disposition or a preference, and the leg is label-free: `author_profiles.csv` was never opened.
- **EXPLORATORY, corpus-level.** No person-level claim is licensed. The per-author r1 values exist only as the population of a mean and of one correlation.
- **Cohort composition.** The disjoint cohort is TYPOLOGY-ENRICHED by construction (PANDORA's non-Big5 authors are MBTI-labelled users), so it is a platform sample with a selection, not a population sample.
- **The attenuation note.** The per-half r1 carries sampling noise of about 1/sqrt(348) ~ 0.054 at the median half, which ATTENUATES the ownership correlation. No disattenuation is registered and none is applied: the raw rho_own routes, and it is a LOWER bound on the ownership of the underlying per-half path parameter.
- **Pool selection.** The pool floors at 50 events in EACH half, so the leg speaks for authors who are ACTIVE ON BOTH SIDES of their own median. Nothing here speaks for short-lived or low-volume accounts.

## Governance

| gate | status |
|---|---|
| Census / blocking anchors (#78, 12 predicates) | `PASS` |
| Part 0 realized-skeleton gate (5 ROUTING clauses) | `PASS` |
| ID-leak scan (0 NEW hits of 10,296 author names over the committed files; 4 pre-existing dictionary collisions carried unchanged from HEAD) | `PASS` |

## Configuration

```json
{
  "adjacency": "consecutive events WITHIN a half",
  "author_profiles_csv": "NEVER OPENED (label-free)",
  "b_boot": 1000,
  "b_perm": 499,
  "boundary_regions": {
    "half_width": 0.011,
    "high": 0.5,
    "low": 0.15
  },
  "cohort": "/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment/results/m4_sr0_recon/cohort_authors.csv",
  "columns_read": [
    "author",
    "subreddit",
    "created_utc",
    "link_id",
    "word_count_quoteless"
  ],
  "comments": "/Volumes/mobile3/projects/project persona/data_sets/PANDORA_official/all_comments_since_2015.csv",
  "halves": "full-stream median of the author's created_utc, <= early",
  "leg": "M4-X2",
  "n_synth_replicates": 8,
  "order": "per-author stable sort by created_utc (ties keep stream order)",
  "phi_bar_ar": 0.2,
  "phi_bar_common": 0.2,
  "phi_clip": 0.95,
  "pool_floor_primary": 50,
  "pool_floor_sensitivity": 100,
  "registration": "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md, section X2, commit 550466f",
  "rho_true_target": 0.5,
  "seed": 20260819,
  "seed_boot": 20260822,
  "seed_part0": 20260820,
  "seed_perm": 20260821,
  "tol": "max(0.02, 3.0 x replicate sd)",
  "y": "log1p(word_count_quoteless)"
}
```

Config SHA-256: `f48cc5fc9213e26a15b0285729146e787e6bff78e1df93f17ff85063c511f3e6`. Artifacts: `results/m4_x2_volume_path/` (gitignored). Every table above is generated from those artifacts (rule 24).

