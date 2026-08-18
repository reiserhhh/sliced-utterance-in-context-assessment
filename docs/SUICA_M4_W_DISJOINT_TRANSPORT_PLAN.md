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
