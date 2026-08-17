# SUICA M4-T1: Hierarchical Selection Identity

Status: exploratory mechanism discovery. This line is label-free by design.

## Question

Does an author's context-selection profile contain a reproducible hierarchy of
conditional innovations? In particular, can a residual left at one group level
become stable author information after the population is split at the next
level?

The proposed object is

\[
\pi_u-\bar\pi = \sum_{l=1}^{L} d_l(u)+r_L(u),
\qquad
d_l(u)=m_l(u)-m_{l-1}(u),
\]

where \(m_l(u)\) is the centroid of the nested selection group containing
author \(u\) at level \(l\). The terminal residual \(r_L\) is not declared
noise: it is tested for remaining same-author information.

## Design

1. Use the existing SR1 early/late subreddit-frequency matrices. No comment
   body and no personality label is read by the primary experiment.
2. Split authors into five folds. In each fold, fit a binary Hellinger-space
   selection tree using only the early vectors of the other four folds.
3. Freeze the tree and route both early and late vectors of held-out authors.
4. At each depth, test whether the child selected by the early half predicts
   the late vector better than its parent centroid.
5. Build a conditional null by permuting late vectors only among held-out
   authors sharing the same early parent node. This preserves the coarser group
   and tests the additional tail branch.
6. Compare flat Hellinger matching, hierarchical-path matching, and terminal
   within-leaf residual matching.
7. Repeat after removing explicitly named personality/typology communities.
   This is a sensitivity arm, not a redefinition of the primary object.

## Primary readings

- cross-half predictive gain by depth;
- within-parent permutation p-value by depth;
- early/late branch and prefix agreement above the conditional null;
- same-author AUC from hierarchical paths versus flat Hellinger AUC;
- terminal residual same-author AUC within frozen leaves.

## Interpretation rules

- A positive held-out branch gain means that a residual at the parent level
  contains reproducible structure at the child level.
- A rare branch is not identity merely because it is rare. It must replicate
  across halves and held-out authors.
- Positive terminal-residual AUC means the fitted depth has not exhausted the
  stable author structure.
- Results establish selection-based author information, not personality. A
  psychological interpretation requires a later, separately registered
  external-connection study.
- Failure of the cleaned arm means the apparent identity hierarchy is specific
  to explicit typology communities or their ecology.

## Controls

- planted hierarchical-choice simulation;
- author-null simulation with identical population choice probabilities;
- held-out-author tree fitting;
- within-parent permutation rather than unrestricted pair permutation;
- explicit-personality-community ablation;
- no Big5/MBTI labels during model construction or primary scoring.

## Outputs

- `results/m4_t1_hierarchical_selection_identity/summary.json`
- `results/m4_t1_hierarchical_selection_identity/metrics_by_depth.csv`
- `results/m4_t1_hierarchical_selection_identity/per_user_depth.csv`
- `reports/SUICA_M4_T1_HIERARCHICAL_SELECTION_IDENTITY_REPORT.md`

## Completed reading (2026-08-17)

The mechanism test completed on held-out PANDORA authors. The primary full arm
retained five stable conditional levels; the arm excluding explicitly named
personality/typology communities retained four. At each retained level, all
three criteria agreed: the early child centroid improved late-half fit over
the parent, the late half locally replayed the early child above a
within-parent permutation null, and the early child reduced uncertainty about
the late child by positive permutation-corrected conditional mutual
information. In the cleaned arm, levels five and six still showed branch
replay and excess information, but their centroid-gain confidence intervals
crossed zero. They are therefore recorded as reproducible categorical code,
not confirmed predictive innovations.

The result supports a mixed representation:

\[
\pi_u-\bar\pi
=\sum_{l=1}^{L}d_l(u)+r_L(u),
\qquad
I(C_{u,l}^{early};C_{u,l}^{late}\mid P_{u,l})>0,
\]

where the discrete innovations are reproducible but do not exhaust identity.
Terminal within-leaf residual AUC remained above `.94` in both arms and above
`.94` across all resolution checks. Increasing tree depth therefore does not
turn the tail into a finite list of ever-smaller types. The current evidence
is more consistent with **nested conditional choices plus a continuous or
higher-order author coordinate**.

This is a label-free author-identity result. It does not identify personality,
and it does not license naming branches. The next scientific leg must separate
stable identity carried by topic/community history from psychologically valid
person-level structure using condition-matched controls and an independently
specified external-connection analysis.

---

## Planner adjudication of T1 and line adoption (2026-08-17, appended by the M-line planner)

The T-line is hereby adopted into the standing loop discipline
(rules 1–33, all conventions, six deliverables,
registration-committed-before-run). **T1's own ledger typing is
upheld exactly as written — EXPLORATORY, NOT PREREGISTERED — and
its numbers enter future legs only as G0 anchors requiring
bit-verification** from `results/m4_t1_hierarchical_selection_identity/`.
The work itself is strong: frozen held-out trees, a triple gate
(centroid gain + within-parent replay + permutation-corrected
conditional MI), planted and author-null controls both clean
(0.9407/0.4957 path AUC), resolution sensitivity, and the
personality-community ablation. `suica_core/` received a NEW module
only (git-verified additive; frozen operators untouched;
owner-directed); my legs continue to write under `scripts/` and
import the T1 core by file with provenance. The 4W theory document
(`SUICA_4W_PERSON_INTERPRETER_THEORY.md`) is adopted as the line's
map; its §11 four-questions template becomes a REGISTRATION SECTION
of every future leg (the 4W header).

---

## M4-T2 — the condition-matched residual audit, and the taste-transport falsifier

**REGISTERED 2026-08-17, BEFORE RUN.** Planner: the M-line planner;
executor: dispatched agent. The 4W doc's priority 1, with its
priority 4 (the Where-version of frame refresh) folded in as Arm B.
Label-free throughout: no Big5/MBTI value is read at any stage;
aggregates only; IDs confined to gitignored intermediates.

### 4W header (the §11 template)

- **Object:** Where × Who — the terminal within-leaf residual
  r_L(u) whose same-author AUC T1 measured at 0.9552 (full) /
  0.9417 (clean).
- **Fixed:** T1's frozen base tree and leaf assignments
  (`per_user_depth.csv`, config seed 20260817, d6/l30); the
  training-fold community embedding (Arm B); the SR0 vocabulary
  (1191, floor 15).
- **Varied:** stranger-match strata (observability calipers,
  Arm A); support disjointness (Arm B).
- **Falsifiers:** Arm A — the residual AUC collapses into the
  permutation null band under full observability matching
  (SUPPORT ARTIFACT); Arm B — no transport onto disjoint support
  (LOYALTY-ONLY identity).
- **Layer:** R (relational, label-free author-identity evidence).

### Question

T1 proved the tail exists; T2 asks WHAT CARRIES IT. Candidates
(4W doc §10.1): observability/support (volume, span, entropy,
breadth); specific community loyalty (self-history); a continuous
taste coordinate that GENERALIZES to unseen communities; deeper
structure. Arms A and B separate the first three.

### Arm A — matched-stranger audit (does the residual survive observability matching?)

Within each frozen leaf, the same-author statistic compares
score(early_u, late_u) against score(early_u, late_v) for strangers
v in the same leaf. **Matching construction (pinned):** the
stranger set for target u is restricted to v whose LATE-half
observables match u's LATE-half observables — cumulative caliper
ladder, all quantities selection-side:

1. L0 (anchor): unmatched — must reproduce T1's leaf-residual AUC
   within bootstrap error (G0 anchor, not a verdict);
2. L1: in-vocabulary comment volume, |log2 ratio| ≤ 0.5;
3. L2: + active time span, |Δ| ≤ 90 days;
4. L3: + selection entropy, |Δ| ≤ 0.5 bits;
5. L4: + community breadth (distinct in-vocab communities),
   ratio ∈ [0.7, 1.43].

Per level: AUC with user-bootstrap CI (B = 1000) and a
WITHIN-LEAF × WITHIN-STRATUM permutation null (late halves
permuted among matched candidates; B = 999; method pinned per
#66 — the null band is the permutation's own, no closed forms).
Admissible-pair attrition reported per level; a level whose
admissible stranger pool drops below 5 per target on median is
UNDERRESOLVED and says so.

### Arm B — taste transport onto disjoint support (the Where refresh)

**Embedding (pinned):** per T1 fold, PPMI + SVD (d = 64) of the
TRAINING authors' EARLY user×community matrix (sqrt counts);
community vectors frozen per fold; held-out users never touch the
fit (rule 12: file:line of the construction in Part 0). Per
held-out user: **centroid_E** = count-weighted embedding centroid
of the FULL early half; **centroid_Lnew** = centroid of LATE-half
communities ABSENT from that user's early half (≥ 3 such in-vocab
communities required; attrition reported). Same-author statistic:
cos(centroid_E(u), centroid_Lnew(u)) vs cos(centroid_E(u),
centroid_Lnew(v)) for leaf-and-L1-matched strangers; AUC,
bootstrap CI, within-leaf×stratum permutation null as Arm A.
**This is selection identity under support refreshment: the
person's taste predicting communities they had not yet joined.**

### Verdicts (rule 22; NULL-first per #55)

- **V-T2a (Arm A at L4):** COLLAPSED (AUC CI inside the permutation
  null band ± its own spread — equivalence first) / STRONG_SURVIVAL
  (CI entirely above the null band AND point ≥ 0.90) / PARTIAL
  (above the null band, below 0.90) / UNDERRESOLVED.
- **V-T2b (Arm B):** TRANSPORTS (CI above the null band) /
  LOYALTY_ONLY (inside) / UNDERRESOLVED.
- Readings (no gates): the AUC-by-ladder curve (which caliper bites
  hardest — the support decomposition); clean-arm replication of
  both arms (T1's 23-community ablation); per-leaf heterogeneity.

### Leans (sides declared)

**L-T2 [SURVIVES(strong or partial)+TRANSPORTS .35 /
SURVIVES+LOYALTY_ONLY .30 / COLLAPSED .20 / underresolved-mixed
.15].** Honest uncertainty: volume alone is enormously
author-informative in frequency space, and loyalty alone can carry
a 0.95 AUC; the interesting world is the one where both falsifiers
fail.

### Routing (rule 16 — disjoint, covering, entailed)

| # | condition | outcome |
|---|---|---|
| 1 | G0 anchor or reconstruction failure | **STOP** |
| 2 | V-T2a COLLAPSED | **SUPPORT_ARTIFACT_MAJOR** — T1's tail re-typed by dated note; the 4W doc's §5.2 gains a correction |
| 3 | V-T2a survival + V-T2b TRANSPORTS | **CONTINUOUS_TASTE_COORDINATE** — the tail is a generalizing person-level Where structure; priority 2 (tree+tail joint representation) becomes registrable on a certified object |
| 4 | V-T2a survival + V-T2b LOYALTY_ONLY | **HISTORY_IDENTITY** — stable but non-generalizing; typed as community-history; the psychological-candidate reading narrows sharply |
| 5 | any UNDERRESOLVED verdict (no higher cell) | **UNDERRESOLVED** (attrition and pool sizes reported; redesign named) |

### Gates

- **G0t2 (bit-exact):** T1's summary.json / metrics_by_depth.csv /
  per_user_depth.csv reproduce the adjudication-cited numbers
  (0.9552, 0.9417, 0.7461, 0.7317, depth gates, N 1304/1269);
  the L0 anchor reproduces the leaf-residual AUC within bootstrap
  error; SR0 vocabulary/floor at source. Frequency matrices
  reconstructed through the T1 core module (imported by file,
  ONE loader chain, provenance pinned) and verified against every
  persisted summary statistic that exists.
- **G1t2 (#59 non-degeneracy):** matched-stranger AUC is not
  forced (calipers restrict the comparison set, they do not
  equalize content); centroid_Lnew is nonempty for the retained
  cohort; the embedding's held-out purity (training-fold-only fit)
  verified by construction log.
- **G2t2 (projection, #66-compliant):** pilot permutation
  calibration on a 200-user subsample fixes the achievable null
  bandwidths at each ladder level BEFORE the full run; if the L4
  or Arm-B bands cannot separate 0.5 from 0.75 at the realized
  pool sizes, the leg declares UNDERRESOLVED-by-design and stops
  (N is corpus-fixed; there is no escalation to buy).
- **G3t2:** rule-29 predicates (AUC ∈ [0,1], null 0.5); rule 24
  generated tables; the R-G compliance block (label-free, no IDs
  in committed artifacts, ID-leak scan of the report); stages
  < 600 s; target < 45 min.

### Deliverables

The six as always: `scripts/run_suica_m4_t2_matched_residual.py`;
`results/m4_t2_matched_residual/` (gitignored);
`reports/SUICA_M4_T2_MATCHED_RESIDUAL_REPORT.md`; outcome append
HERE; one ledger row (EXPLORATORY, label-free); exactly ONE commit
`feat(m4-t): T2 — the condition-matched residual audit — <SLUG>`,
never amended, never pushed; suite green first (report the new
suite count — T1 added tests).
