# SUICA M4-W — the disjoint-cohort transport line

Opened 2026-08-18, directly after the U-line's full close. The U-line left
one interval open (whether the common mass outlasts the distinctive tail —
7/7 point estimates one side, no CI excluding zero) and ruled same-corpus
escalation out as significance-chasing. The recon that opened this line:
the PANDORA comments file contains **10,296 distinct authors**, of whom
**8,895 are OUTSIDE the 1401 Big5 cohort** — a disjoint cohort on the same
platform, 14.6M comments, with the full event structure the selection
machinery needs (MBTI9K and TWITTER corpora were reconned and REJECTED:
no per-comment venue/timestamp columns).

Transport semantics (Q-line vocabulary): a LAW transports when its
re-instantiated measurement on a fresh cohort reproduces it; an INSTRUMENT
transports when the frozen artifact does. W1 runs the law arms as primary
and the instrument arms as sensitivity.

Governance: label-free THROUGHOUT the line's opening phase —
`author_profiles.csv` is never opened (the disjoint authors' MBTI labels
stay closed); the ID-leak scan universe widens to ALL 10,296 author names;
the cohort listing itself is a gitignored artifact built by predicate;
aggregates only; EXPLORATORY corpus-level; no person claims; no
cross-corpus author linkage (none exists — one file, disjoint subsets).

## Line charter

- **W1 (registered below):** slow-time law transport — the decay-rate
  contrast Λ at ~9× authors (closing the U-line's open middle) + the
  sealed-prediction transport table (floor share, D, λ ordering).
- **W2 (named, not registered):** fast-time transport — U1's order
  channel (rho, dwell dominance, cross-thread share) and the T-line
  branch-code transport (T1's open item).
- **W3 (named, not registered):** the label side, only after W1/W2 close
  label-free and only under a fresh stamped design (the disjoint cohort's
  labels are MBTI axes, not Big5 — a different join class needing its own
  governance review).

---

## W1 — slow-time law transport and the closing of the middle (registered BEFORE run, 2026-08-18)

### 4W header

- **Object.** The U-line's slow-time laws as SEALED PREDICTIONS carried to
  a disjoint author cohort: (1) the decay-rate contrast Λ (the open
  middle); (2) DRIFT_WITH_CORE's floor share and D; (3) the layer ordering
  (λ_taste smallest). When × transport; author structure only.
- **Fixed (pinned BY FORMULA per #81, with provenance).** Block
  construction, bins, epoch-matched exact stratified cross baseline,
  within-quarter permutation, paired cluster bootstrap — all from the
  committed U2/U2b/U2c runners (`scripts/run_suica_m4_u2_persistence_curve.py`,
  `scripts/run_suica_m4_u2b_persistence_budget.py`,
  `scripts/run_suica_m4_u2c_decay_rate_contrast.py`), reused by
  import-by-file. Key formulas quoted: block features √(count/K), L2, over
  the arm's vocabulary; E(b) = mean self cosine − epoch-matched exact
  stratified cross mean (quarter = 91.3 d from corpus min);
  λ_row from OLS of log E_row(b) on realized per-bin mean gap (years),
  five verdict bins, 3y+ descriptive only; Λ = λ_distinct − λ_common;
  intersection predicate per block: m ≤ common-events ≤ K − m; K = 50.
- **Varied.** The cohort (disjoint 8,895); the vocabulary instantiation
  (law arm: SR0's RULE re-instantiated on this cohort → floor 89,
  1,443 communities; instrument arm: the frozen 1191 vocabulary and the
  frozen 32-community Common set applied as-is); typology ablation.
- **What falsifies.** Λ CI strictly below 0 (DISTINCT_SLOWER) refutes the
  U-line's provisional sign on fresh authors; transport-table BREAKS
  refute cohort-generality of the corresponding law.
- **Layer.** R.

### Census (planner arithmetic #43; predicates exact per #77/#78, executed 2026-08-18)

| quantity (exact predicate) | value |
|---|---|
| disjoint events (parseable author+subreddit+created_utc) | 14,634,702 |
| authors_seen | 8,895 |
| law-arm vocabulary (floor ceil(0.01·8895) = 89 users) | **1,443**; coverage 0.7587 |
| typology names in law vocabulary / in Common(0.5) | 22 / **8** |
| law-arm Common(0.5) | **71 communities** |
| pool (≥ 4 K=50 in-vocab blocks) | **6,111**; 213,489 blocks; 18 quarters |
| self pairs 2–3y / 3y+ | 2,591,663 / 1,004,737 |
| **gate (2–3y intersection, m=10): pairs / authors** | **1,211,631 / 3,241** |
| gate at m=5 | 1,790,865 / 3,746 |
| Λ width projection (#79b/#80b: √N scaling of U2c's REALIZED 0.1206 at 424 authors; m=10 primary avoids the m=5 per-unit-noise inflation) | **≈ ±0.044** vs sealed point +0.074 |

Anchor gates (#78): the executor re-executes these exact predicates and
must reproduce every census number above (STOP on mismatch). Sufficiency
targets (trivially cleared, stated for form): ≥ 400 authors and ≥ 100k
pairs in the 2–3y intersection.

### Sealed predictions (source values from committed U-line artifacts)

| quantity | source (cohort 849/424) | transport question |
|---|---|---|
| Λ | +0.0741 [−0.0558, +0.1854] | does the CI now EXCLUDE zero, and which side? |
| floor share E(2–3y)/E(0–90d), full row | 0.5348 [0.4203, 0.6320] | REPRODUCES / SHIFTS / BREAKS |
| D = E(0–90d) − E(2–3y), full row | 0.3058 [0.2364, 0.3855] | same |
| λ_full | 0.2943 [0.1895, 0.4405] | same |
| ordering: λ_taste smallest of four rows | held in both U2c arms | ORDER HOLDS / ORDER BREAKS |

Transport classification (effect-size keyed #75): REPRODUCES = target CI ∩
source CI nonempty AND same sign/cell; SHIFTS = disjoint CIs, same
sign/cell; BREAKS = different sign/cell. The table is SECONDARY; flags per
#73; it never routes the verdict.

### Verdict estimand and cells

Λ on the law arm at q = 0.5 (re-derived Common = 71 communities), m = 10,
paired cluster bootstrap B = 1000 (identical author draws across rows;
replicates with non-positive E dropped and counted). Null machinery
(#80a-compliant, pinned): per-bin E null centers by within-quarter
permutation (B = 499, expected 0); the Λ permutation null is posed on the
LINEAR slope contrast (domain-safe form — the log fit runs on real data
only, where all realized E > 0); the verdict criterion is the bootstrap CI.

1. **SIGN_UNRESOLVED** — Λ CI straddles 0 (interval statement; with the
   projected ±0.044 this now costs the provisional sign real credibility).
2. **COMMON_STANDING** — Λ CI > 0: the middle CLOSES; the T-line
   proposition acquires its When clause on fresh authors.
3. **DISTINCT_SLOWER** — Λ CI < 0: the provisional sign REFUTED on fresh
   authors; the U-line reading is re-examined before any theory move.

### Arms

| arm | role |
|---|---|
| LAW: re-derived vocab 1443, Common(0.5)=71, m=10, pool 6,111 | PRIMARY (verdict + transport table) |
| INSTRUMENT: frozen 1191 vocab + frozen 32-community Common | sensitivity; #73 flags vs law arm |
| clean_no_explicit_personality (23 names removed from the law vocab; 22 present; re-split, rerun Λ + floor share) | co-reported; #73 flags — the typology-enriched cohort (8/71 in Common) makes this arm's divergence informative |
| m = 5 | sensitivity |
| taste row (per-fold PPMI+SVD d=64, 5 folds, training-first-half-only, purity asserted) | the ordering prediction |
| 3y+ | descriptive only |

### Registered leans

- Λ > 0 with point ≈ +0.07/y (the sealed U2c point; disclosed-knowledge
  lean, not a fresh prediction).
- Floor share and D REPRODUCE (the DRIFT_WITH_CORE law is cohort-general).
- λ_taste smallest (ORDER HOLDS).
- Clean-arm lean (weak, informative either way): Λ survives the typology
  ablation within its CI class — the U-line's identity-robust pattern; a
  large clean-arm shift would localize the slow common mass in the
  typology communities themselves.

### Deliverables and discipline

Standard six: `scripts/run_suica_m4_w1_slow_transport.py` + tests
(cache-builder anchors; census-predicate reproduction; formula-level
contract tests against the imported U2c estimator on a shared toy;
permutation/bootstrap pairing invariants; ID-leak helper over the WIDENED
universe — all 10,296 names); gitignored `results/m4_w1_slow_transport/`
(includes the disjoint events cache and the cohort listing — never
committed); report `reports/SUICA_M4_W1_SLOW_TRANSPORT_REPORT.md`
(rule-24 tables; verdict + transport table; null centers; projection vs
realized; the eq-12 projection caution; three-year scoping language;
config block); outcome appended here; one CLAIMS_LEDGER row (EXPLORATORY,
label-free, corpus-level, disjoint-cohort transport named); ONE commit
`feat(m4-w): W1 — slow-time law transport — <VERDICT>`, never amended,
never pushed by the executor. Suite green (1197 + new) before commit.
`author_profiles.csv` is NEVER opened. SEED = 20260818; B_perm = 499;
B_boot = 1000.

---

## W1 outcome (executor, 2026-08-18)

**`COMMON_STANDING`. The U-line's open middle CLOSES.**

`Λ = λ_distinct − λ_common = +0.0911/y [+0.0628, +0.1490]` on the LAW arm at
the registered q = 0.5 / m = 10 (125,555 blocks; 1,211,631 self pairs and
3,241 contributing authors in the 2–3y bin; paired cluster bootstrap
B = 1000, all 1,000 replicates retained). The bootstrap interval — the
registered verdict criterion — lies strictly above zero on a cohort that
shares no author with the one that produced the provisional sign. The
DISTINCTIVE carrier decays faster than the COMMON carrier; over the observed
three-year window the common mass is the standing part.

Realized half-width **0.0431** against the registered projection **±0.044**
(ratio 0.979) — the #79b/#80b √N scaling was accurate to 2%.

### Census (#78) — every pinned predicate re-executed, 16 of 16 PASS

Disjoint events 14,634,702; authors_seen 8,895; floor ceil(0.01·8895) = 89 →
1,443 communities at coverage 0.7587; Common(0.5) = 71 communities carrying
0.5022 of the in-vocabulary mass; typology names 22 in vocabulary / 8 in
Common; pool 6,111 authors and 213,489 blocks over 18 quarters; self pairs
2–3y 2,591,663 (3y+ 1,004,737); gate m=10 1,211,631 pairs / 3,241 authors;
gate m=5 1,790,865 / 3,746. Nothing drifted; the leg never needed its STOP.

### The four-row rate table (LAW arm)

| row | λ (1/y) | 95% CI | R² | F = E(2–3y)/E(0–90d) | D |
|---|---|---|---|---|---|
| full (1,443) | 0.1236 | [0.0591, 0.2520] | 0.925 | 0.7360 | 0.1408 |
| common (71) | 0.0901 | [0.0362, 0.2069] | 0.942 | 0.8014 | 0.1117 |
| distinctive (1,372) | 0.1812 | [0.1045, 0.3223] | 0.923 | 0.6392 | 0.1734 |
| taste (PPMI+SVD d=64) | 0.1010 | [0.0854, 0.1345] | 0.982 | 0.7838 | 0.0610 |

Nulls (#80a-compliant): per-bin within-quarter permutation centres are
≤ 5e-05 in absolute value, i.e. zero to four decimals as the construction
requires. The Λ null is posed on the LINEAR slope contrast — realized
+0.0236 against a null centre of +0.00006 and a null band
[−0.00083, +0.00086], all 499 replicates finite. The LOG-form null retains
only 37 of 499 replicates (a relabelling drives E(b) through zero), which is
why the registration put the null on the linear form; neither null routes.

### Arms — all four land in the same cell

| arm | Λ | 95% CI | cell |
|---|---|---|---|
| LAW (q=0.5, m=10, Common 71) | +0.0911 | [+0.0628, +0.1490] | `COMMON_STANDING` |
| m = 5 sensitivity | +0.0953 | [+0.0648, +0.1509] | `COMMON_STANDING` |
| INSTRUMENT (frozen 1191 / Common 32) | +0.0644 | [+0.0168, +0.1107] | `COMMON_STANDING` |
| clean_no_explicit_personality (22 removed) | +0.0780 | [+0.0484, +0.1397] | `COMMON_STANDING` |

The instrument arm is the informative one for transport semantics: 1,187 of
the 1,191 frozen community names exist in the disjoint stream, but the frozen
32-community Common set holds only **0.3473** of that cohort's mass where it
held 0.50 on the source. The frozen artifact does NOT carry its own mass
split — and the contrast survives anyway, weaker and still strictly positive.
The LAW transports; the INSTRUMENT transports too, at a cost in effect size.

The clean arm matters here because the cohort is typology-enriched: removing
the 22 explicit-typology communities (leaving 1,421, re-blocked, re-pooled,
mass split re-derived to Common(0.5) = 84) moves Λ from +0.0911 to +0.0780,
same cell, overlapping intervals. The slow common mass is NOT localized in
the typology forums.

### Sealed-prediction transport table (SECONDARY — never routed)

| quantity | source | target | classification |
|---|---|---|---|
| Λ | +0.0741 [−0.0558, +0.1854] | +0.0911 [+0.0628, +0.1490] | **BREAKS** (cell) |
| floor share, full row | 0.5348 [0.4203, 0.6320] | 0.7360 [0.5453, 0.8568] | **REPRODUCES** |
| D, full row | 0.3058 [0.2364, 0.3855] | 0.1408 [0.0850, 0.2224] | **SHIFTS** |
| λ_full | 0.2943 [0.1895, 0.4405] | 0.1236 [0.0591, 0.2520] | **REPRODUCES** |
| ordering: λ_taste smallest | ORDER HOLDS | ORDER BREAKS | **BREAKS** |

Two BREAKs, and both need reading rather than reciting:

1. **Λ "BREAKS" as a PRECISION GAIN, not a contradiction.** The intervals
   OVERLAP and the sealed source point +0.0741 lies INSIDE the target
   interval. The source half-width was 0.1206 and could not exclude zero;
   the target's is 0.0431 and does. The registered rule keys on the CELL, so
   it lands in BREAKS — the substance is confirmation of the source's
   direction at a width the source never had. The planner should decide
   whether the #75 classification wants a fourth label for this case.
2. **The ordering BREAKS narrowly.** λ_taste = 0.1010 is rank 2 of 4,
   0.0109/y above the slowest row (`common` at 0.0901), and the taste row's
   own interval [0.0854, 0.1345] CONTAINS the common row's point. Order
   slowest-first: common 0.0901 < taste 0.1010 < full 0.1236 < distinct
   0.1812.

Floor share and D split classification for one reason: the disjoint cohort's
curve is FLATTER at both ends. The sealed values imply a source curve running
0.6574 → 0.3516; the target full row runs 0.5332 → 0.3925. Lower start,
higher finish — the RATIO reproduces while the DIFFERENCE shifts down. Part
of that gap is the disclosed provenance asymmetry (the sealed floor share and
D come from U2's 849-author POOL arm while Λ and λ_full come from U2c's
INTERSECTION set), and this leg does not separate the two contributions.

### Registered leans

- **L1 (Λ > 0 at ≈ +0.07/y): HELD** — realized +0.0911, cell
  `COMMON_STANDING`.
- **L2 (floor share and D REPRODUCE): PARTIAL** — floor share REPRODUCES, D
  SHIFTS.
- **L3 (λ_taste smallest): MISSED**, narrowly — rank 2, inside its own CI of
  the winner.
- **L4 (clean arm survives within CI class): HELD.**

### Governance

Label-free throughout — `author_profiles.csv` was never opened, and the
disjoint authors' MBTI labels stay closed. The ID-leak universe was widened
to all 10,296 author names as registered; the scan returns **0 NEW hits**.
Three raw hits exist in `docs/CLAIMS_LEDGER.md` and all three are DICTIONARY
COLLISIONS — candidate author names that are ordinary English words or bare
digit runs, occurring in prose committed long before this line opened. They
are separated from leaks mechanically, never by hand: a hit counts as
pre-existing only when the same scanner produces the identical hit, same file
and same line, on that file's version at HEAD. W1's own outputs have no HEAD
version and therefore zero tolerance, and they are clean. **This is a
governance finding the planner should rule on: at 10,296 candidates the
substring scan has a false-positive floor, and the widened universe will keep
paying it on every future leg.**

The cohort-composition caveat binds every claim above: the disjoint cohort is
PANDORA's MBTI-labelled population, typology-enriched by construction (8 of
71 Common communities are typology names). A law that transports here has
been carried to a different KIND of author population on the same platform,
not to a fresh sample of the same one.

Artifacts: `results/m4_w1_slow_transport/` (gitignored — includes the events
cache and the disjoint cohort listing, never committed). Report:
`reports/SUICA_M4_W1_SLOW_TRANSPORT_REPORT.md`. Runtime ≈ 24 minutes;
17 estimator calls; SEED 20260818, B_perm 499, B_boot 1000.
