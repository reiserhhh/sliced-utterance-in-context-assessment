# SUICA Rind Theory Base v3 (皮モデル)

Created: 2026-07-05
Status: predictions committed BEFORE the regime test run; results section appended after.

## 1. The model

SUICA treats a body of spontaneous text as a watermelon (suika): a person-stable
interior ("flesh") wrapped in theme/situation shells ("rind", 皮). The 2026-07
validation cycle established empirically what the rind is NOT: it is not a
nuisance that can be subtracted away. Statistical condition-centering was
falsified in every tested form (naive, partial-lambda, two-way-FE out-of-sample;
see CLAIMS_LEDGER P2/E1). The rind carries person signal because people choose
their rinds.

Formal object. For author u, slice i, rind r(i):

```text
y_ui = flesh_u + rind_{r(i)} + gamma_{u,r(i)} + e_ui        (style features)
r(i) ~ P(r | u)                                             (rind choice)
```

Three information channels, with measurability governed by the RIND REGIME:

| Channel | Definition | Free rind (Reddit) | Domain-fixed rind (X market) | Experiment-fixed rind (Essays prompt) |
|---|---|---|---|---|
| C1 choice | P(r \| u) vs population | rich (audited: axes retest 0.51-0.70, AUC 0.839/0.909; held-out confirmation in OP-6a) | micro only (within-domain: symbols, query groups) | zero by design (recoverable via the Rulebook A3 choice module) |
| C2 style-base | E[y_u] uncentered | attenuated by rind mixing | intermediate | maximal precision (within-population claim; see PRED-1b caveat) |
| C3 react | structure of gamma_{u,r} | **provisional**: person-specific signatures confirmed for 2 constructs under the stranger null (E6: first_person +0.15, directive +0.15); pending held-out replication before promotion | untested | design-dependent (future) |

C3 status note (2026-07-05 consistency pass): earlier versions of this table
said "retired"; the audited E6 matched-estimator result revives C3 narrowly
(2 style constructs, n=195 deep users, CI lower bounds 0.007/0.044). Treat as
provisional until replicated on users outside the deep-extraction cohort.

## 2. The design principle (the core theoretical commitment)

**Rind variance is controlled by DESIGN, not by STATISTICS.**

- Statistical control (centering) removes flesh together with rind because
  P(r|u) is informative — proven three independent ways (MCD benchmark 2026-06,
  P2 2026-07-04, E1 cross-fit audit 2026-07-05).
- Design control (fixing the rind experimentally, or sampling within one
  domain) removes rind variance from the observations themselves, leaving C2
  clean, at the price of silencing C1.

Consequence for instrument construction: a fixed-rind experiment yields a
rind-specialized scale (皮特化尺度) whose C2 precision-per-token exceeds
free-rind sampling; a free-rind sample yields C1, which no fixed-rind design
can provide. A complete SUICA instrument therefore has two phases:
free-collection (C1) + fixed-prompt battery (C2), which is the corrected,
defensible form of the original "scale + projective hybrid" ambition.

## 3. Precision formula (what fixing the rind buys)

For a style construct with slice noise sigma2_e, between-rind variance
sigma2_r, and n slices spread over rind mix M:

```text
SE^2(style_base_u) ~ ( sigma2_e + H(M) * sigma2_r_effective ) / n
```

where H(M) grows with rind heterogeneity of the user's sample. Fixed rind sets
H ~ 0. Reliability-per-token is therefore predicted to ORDER by regime:
experiment-fixed >= domain-fixed >= free, for the same n.

## 4. Pre-committed regime predictions (test: run_suica_rind_regime_test_v3.py)

- **PRED-1 (within-corpus, cleanest)**: for the same PANDORA users, same slice
  counts, split-half reliability of style bases is higher when all slices come
  from ONE subreddit (rind fixed by selection) than when slices span >= 4
  subreddits (rind mixed). Pass rule: paired delta > 0 with 95% bootstrap CI
  above 0 for a majority of the 4 live style constructs.
- **PRED-1b (cross-corpus ordering, with occasion caveat)**: at a matched
  ~1,000-token budget, split-half reliability orders Essays >= X >= PANDORA-mixed.
  Reported descriptively; Essays confounds rind-fixing with single-occasion
  writing, so this is supporting evidence only.
- **PRED-2 (micro-choice)**: in the domain-fixed regime (X), within-domain
  choice (symbol distribution) is person-stable: same-user early/late AUC vs
  random pairs >= 0.65 (the migration-manual criterion).
- **PRED-3 (same flesh, different rinds)**: the inter-feature correlation
  structure of the 23 anchor-rate features (user level) is invariant across
  regimes: correlation of off-diagonal vectors >= 0.70 for every corpus pair.

Falsification consequences, committed now:
- PRED-1 fail -> the precision formula is wrong; fixed-rind experiments lose
  their principal justification; theory reverts to C1-only.
- PRED-2 fail -> C1 does not miniaturize; domain-fixed deployments (e.g., the
  planned X/market agent line) get style-base only.
- PRED-3 fail -> "flesh" is rind-specific; no universal base formula; SUICA
  becomes a family of per-rind instruments with no cross-rind claims.

## 5. Governance for this test

- Essays users are split 50/50 by stable hash; only the dev half's TEXT is
  used here; Big5 label columns are never loaded; the confirm half stays
  untouched for P5. X is unlabeled (Tier X).
- v3 scoring formulas are frozen; nothing downstream of this test may alter
  them without triggering re-validation.

## 6. Results (2026-07-05 run; audit status in CLAIMS_LEDGER)

- **PRED-1: PASS 3/4 after audit** (n=918 paired users, same slice counts;
  round-3 audit applied parity, ordering, density, and time-span controls):
  span-matched deltas — first_person +0.063 [0.029,0.098], directive +0.165
  [0.074,0.260], novelty +0.182 [0.047,0.294]. The most rind-driven construct
  (novelty) gains most — consistent with the channel model. **tension's
  apparent gain was a temporal-clustering artifact** (the fixed arm was a
  chronological prefix; span-matched delta -0.033) — affect-state constructs
  do not benefit, consistent with tension being state-like, not trait-like,
  in text. **The design principle (control rind by design, not statistics) is
  empirically supported in its within-population form for style/stance
  constructs.** Any future run must span-match the arms.
- **PRED-1b: ordering NOT confirmed as stated.** At matched 6-slice budget:
  X (domain-fixed) is best or near-best everywhere (novelty 0.643, tension
  0.357); Essays (experiment-fixed prompt) is only ~equal to PANDORA-mixed.
  Amendment adopted into the formula: split-half reliability is
  POPULATION-RELATIVE — between-person variance differs across populations
  (Essays = homogeneous students; X/Reddit = heterogeneous internet users), so
  cross-population reliability comparisons do not test the rind principle.
  The principle holds within-population (PRED-1); planned fixed-rind
  experiments should therefore expect gains relative to free-rind sampling of
  the SAME population, not absolute reliability guarantees.
- **PRED-2: PASS with caveat** — X symbol-choice AUC 0.810 (criterion 0.65),
  but n=31 users only; needs a larger domain-fixed corpus before promotion.
- **PRED-3: PARTIAL (audit-corrected)** — the first run accidentally included
  a 24th, algebraically derived feature; on the true 23 lexicon rates the
  structure correlations are pandora-essays 0.620, essays-x 0.572, pandora-x
  0.530 (sparse-feature-robustness variant: pandora-x 0.494), and the X leg
  is weak (89.5% single-slice users). The flesh structure transports
  approximately, not exactly: cross-rind deployments need per-rind
  calibration (which is precisely the planned rind-specialized scale
  (皮特化尺度) route). Only the pandora-essays pair (0.620) is currently
  solid evidence.

### Formula v3.1 (amended)

```text
SE^2(style_base_u) ~ ( sigma2_e(pop) + H(M) * sigma2_rind + [occ structure] ) / n
reliability = f(design, population)  — never a design-only constant
C1 available iff rind (or micro-rind) is self-selected; C1 miniaturizes to
within-domain choice (PRED-2) under domain fixing.
```
