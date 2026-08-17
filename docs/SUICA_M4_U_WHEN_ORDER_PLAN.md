# SUICA M4-U — the When line (order, path, and slow time)

Opened 2026-08-18 by the planner, directly continuing the owner's 4W program
(`docs/SUICA_4W_PERSON_INTERPRETER_THEORY.md`) after the T-line measurement
phase closed (`docs/SUICA_M4_T_LINE_SYNTHESIS.md`, commit 2245b97).

## Line charter

The T-line answered the Where × Who crossing on **bags** (static per-author
selection distributions): identity is metric-borne, taste-dominated, and the
proposition "identity lives in the distinctive; personality lives in the
common" closed the measurement phase. Every T-line object was a static mean.

The 4W theory's §2.4 states that When studies **order mechanisms** — the
higher-order path information that "appears only in motion and vanishes in
static means" — whose general object is the author transition kernel
K_u (eq 12), of which any fixed-window statistic is only a projection. The
theory's own caution is binding here: an unstable or null projection does NOT
falsify the dynamics; it only shows that projection missed.

The U-line therefore asks, in order of technical readiness:

- **U1 (registered below)**: does the ORDER of community selections carry
  reproducible author structure beyond the bag? (fast time, event order)
- **U2 (named, not registered)**: the personal persistence curve — self-
  similarity of the selection signature as a function of calendar gap, with an
  epoch-matched cross-author baseline; fixed point vs drift vs floor.
  (slow time)
- **U3 (named, not registered)**: Who × When trait join — do order/dwell
  coordinates couple to Big5 beyond the bag channel? Label join only inside a
  stamped stage-E design; not before U1 closes label-free.

Governance: the whole line is corpus-level EXPLORATORY. U1 and U2 are
label-free (no Big5/MBTI value is read). R-G1..R-G8 bind: no person claims,
no cross-corpus author linkage, no user text or user IDs in committed
artifacts (ID-leak scan against the 1401 cohort IDs is a blocking gate),
aggregates only. The native corpus stays paused (owner 2026-07-12).

---

## U1 — order-borne selection identity (registered BEFORE run)

### 4W header (registration section, mandatory since the T-line)

- **Which 4W object.** When — the first-order projection of the author
  transition kernel K_u (theory eq 12) over coarse Where states, plus dwell
  (stay) statistics. The claim target is crossing #4 (Who × When): whether
  order carries author structure that the Where bag cannot see. Identity
  information only; no psychological naming (§5.4 binds: technical object).
- **What is fixed / what is varied.** Fixed: SR0 cohort and vocabulary
  (1191 communities at floor 15, reproduction bit-verified 2026-08-18);
  per-author median-timestamp early/late halves (T6'' pattern); Hellinger
  conventions; 5-fold author cross-fitting with per-fold training-early-only
  state maps. Varied: real event order vs within-half order-shuffled events
  (the exact-bag null); state resolution C ∈ {12, 24, 48}; raw vs
  session-restricted vs cross-thread adjacency; full vs
  clean_no_explicit_personality vocabulary.
- **What falsifies.** If the order excess ρ (defined below) is
  indistinguishable from its own shuffle null in the primary arm at every
  registered C, the verdict is NO_ORDER_CHANNEL **for this projection** —
  explicitly not a falsification of eq-12 dynamics (the theory's projection
  caution is quoted into the verdict whatever it is).
- **V/R/P layer.** R (representation/measurement) for the real-data claim;
  V for the synthetic authentication worlds.

### Question and estimand

Within-author event order is destroyed by shuffling each half's event
sequence while preserving that half's bag EXACTLY. Any drop in same-author
discrimination from order-sensitive features is therefore pure order
information. The composite discrimination statistic states its own null
(convention #68): the shuffle null does NOT sit at 0.5 — shuffled bigram
features still discriminate authors through their marginals, so the null
walks near the bag ceiling. The registered primary effect size is therefore
ceiling-aware:

    rho = (AUC_real − mean AUC_shuffle) / (1 − mean AUC_shuffle)

the fraction of the discrimination error remaining at the bag-implied null
that real order removes. Raw excess AUC is reported alongside; cells key on
rho (convention #75; effect size primary, detection secondary).

### Census (planner arithmetic, convention #43, run 2026-08-18)

Streamed 17,640,062 comment rows restricted to the 1401-author SR0 cohort
(no bodies read; scratchpad only). Vocabulary reproduction: floor
ceil(0.01·1401) = 15 → **1191 communities — bit-identical to SR0**.

| quantity | value |
|---|---|
| cohort authors with events | 1401 |
| vocabulary coverage of event stream | 0.7814 (OOV share 0.2186) |
| per-author vocab events, median (q25) | 379 (91) |
| early-half vocab events, median | 188 |
| late-half vocab events, median | 185 |
| adjacent-pair timestamp tie rate | 0.1152 |
| adjacent gaps ≤ 1 h | 0.6609 |
| adjacent gaps ≤ 24 h | 0.9207 |
| median of author-median gap | 2.83 h |
| calendar span, median (q25–q75) | 1157 d (642–1536) |
| pool: both halves ≥ 50 vocab events | **984** |
| pool: both halves ≥ 100 vocab events | 821 |
| pool: both halves ≥ 30 vocab events | 1100 |

Registered pools (convention #69 — pool sizes, not caliper widths): primary
pool = **984 authors** (≥ 50 vocab events in each half); sensitivity pool =
821 (≥ 100). The SR0 split-half rule (≥ 40 total) gave N=1304; U1's stricter
per-half floor is required because bigram features live in a squared space.

### Design

**Event stream.** Columns author, subreddit, created_utc, link_id only.
Events sorted per author by created_utc with a STABLE sort; ties (11.52% of
adjacent pairs) keep stream order — pinned; ties attenuate real order signal
and cannot create it (the shuffle null re-randomizes ties too). Halves by the
author's own median timestamp (SR0 rule, boundary events to early on ≤).

**States.** Per fold, communities are clustered into C states using ONLY
training authors' early halves: spherical k-means (cosine) on √(author-count)
community columns, C primary 24, sensitivity {12, 48} (endpoints named
against vocabulary size 1191, convention #74), seed SEED+1000·fold, n_init
10. Out-of-vocabulary events map to one extra OOV state (index C), so
adjacency is real — no splicing. Communities with zero training-early mass
also map to OOV. State count C+1; feature dimension (C+1)².

**Features (transforms pinned with the verdict, convention #70).**
Primary: the bigram Hellinger sphere — joint next-event counts
n_u(i, j) + α smoothing (α = 0.5) → joint probabilities P_u(i, j) →
elementwise √ → L2 normalization. This is the occupancy-weighted conditional
representation (√(P(i)·P(j|i))), exactly parallel to the T-line's unigram
Hellinger sphere. Secondary lens: unweighted conditional rows
(√ of row-normalized P(j|i), concatenated) — upweights rare rows.
Scalar arm: stay rate s_u = P(next state = current state), scored by
−|s_u^early − s_v^late|; its shuffle null is the bag-concentration pseudo-stay
Σ_j π_j² and is stated as such (#68).

**Discrimination.** Pooled same-author-vs-different AUC on cosine between
early features of u and late features of v, computed within each fold's test
authors under that fold's state map (purity: zero test-author mass in any
map — asserted), then unweighted mean over the 5 fold AUCs.

**The exact-bag null.** B = 499 within-half order shuffles (each half's event
sequence permuted independently, per author, batched and vectorized — the
T2 paid lesson binds: no per-user Python loops × B). Contract test: the
per-half bag (bincount over states) is EXACTLY invariant under the shuffle.
Null band = 2.5/97.5 percentiles of the B pooled AUCs; the null's location is
reported as the bag-implied pseudo-order AUC (#68). Power note (convention
#66): the null-sd method is the empirical percentile over B = 499; the
minimal detectable rho implied by the realized band width is reported, and
any equivalence statement carries the band-width-vs-ε projection (#71,
ε = 0.05 on rho).

**Uncertainty.** Cluster bootstrap over authors, B = 1000, for the CI on rho
(bands carry uncertainty; bias corrections, if any, correct predictions —
convention #67 dual stamping n/a here, no G2 object).

**Arms.**

| arm | role |
|---|---|
| raw adjacency, full vocab, C=24 | PRIMARY (verdict) |
| session-restricted (gap ≤ 3600 s) | secondary — fast-path order |
| cross-thread only (link_id differs) | co-primary decomposition — free-selection order with reply-chain mechanics removed (the theory's opportunity-structure control for crossing #4) |
| C ∈ {12, 48} | sensitivity |
| conditional-rows lens | secondary lens |
| stay-rate scalar | secondary channel |
| ≥100-events pool (821) | sensitivity |
| clean_no_explicit_personality (23 names removed, restated map) | governance echo; divergence from full arm flagged per #73 |

Descriptives registered as non-verdict-moving: same-thread share of
same-state stays (reply-chain mechanics share); OOV state occupancy;
realized transitions per author.

### Synthetic authentication (Part 0, gate before the real arm)

Three worlds, N = 900 synthetic authors, event counts drawn to match the
census median (379), C_true = 24:

- **W_null** — each author draws events iid from an author-specific Dirichlet
  bag. Target: rho CI includes 0 and |rho| < 0.05 (estimator honesty — must
  NOT detect).
- **W_sticky** — stay probability s_u ∈ {0.1, 0.25, 0.5} (3 knob points),
  otherwise iid from the bag. The chain P(i→j) = s·1[i=j] + (1−s)·π_j has
  stationary distribution EXACTLY π (identity proven in-registration:
  Σ_i π_i P(i→j) = s·π_j + (1−s)·π_j = π_j). Target: rho > 0 detected,
  monotone in s.
- **W_transition** — author-specific Metropolis-Hastings chains with target
  stationary π_u and author-specific proposal kernels (block-structured
  preferences); MH guarantees the stationary exactly. Contract test: empirical
  stationary within tolerance; acceptance formula unit-tested. Target:
  rho > 0 detected, monotone in the proposal-structure strength (3 points).

A world where the shuffle-null location fails to sit near the bag AUC fails
the gate (null mechanics broken). Part 0 must pass before the real arm runs;
a failed gate STOPS the leg before any real-data stamp (A1 hardening binds).

### Classification cells (NULL-first, convention #55; effect-size keyed, #75)

On the PRIMARY arm's rho with 95% cluster-bootstrap CI:

1. **NO_ORDER_CHANNEL** — CI lower ≤ 0 in the primary arm at every C; if
   additionally CI upper < 0.05, the scoped statement "no order channel
   beyond rho 0.05 in this projection" attaches with the band-width
   projection (#71).
2. **ORDER_TRACE** — CI lower > 0 and point rho < 0.10.
3. **ORDER_CHANNEL** — point rho ∈ [0.10, 0.33].
4. **ORDER_MAJOR** — point rho > 0.33 (order removes over a third of the
   remaining discrimination error).

CI-boundary straddles are reported as straddles; the verdict then takes the
interval statement, not the point (T-line #75 lesson). Full-vs-clean or
raw-vs-cross-thread divergence takes a #73 flag: primary arm routes the
verdict; divergences are named, never averaged away.

### Registered leans (before run)

- Primary lean: an order channel EXISTS but is small —
  rho in (0.02, 0.15], i.e., ORDER_TRACE to lower ORDER_CHANNEL. Rationale:
  66% of adjacencies are within 1 h (session bursts are real and plausibly
  author-stable), but the T-line showed the bag already carries identity to
  0.9837, and the dissociation lesson warns against expecting new channels to
  be large.
- Secondary lean: the stay-rate scalar alone detects (its own rho > 0) —
  burstiness is author-owned.
- Decomposition lean: the cross-thread arm retains most of the primary rho
  (free-selection order, not reply mechanics, carries the channel) — held
  weakly; a mechanics-dominated result is the informative surprise.

### Deliverables (standard six) and discipline

Script `scripts/run_suica_m4_u1_order_identity.py` + tests
`tests/test_m4_u1_order_identity.py`; gitignored
`results/m4_u1_order_identity/`; report
`reports/SUICA_M4_U1_ORDER_IDENTITY_REPORT.md` with rule-24 generated tables;
outcome appended to this plan doc; one CLAIMS_LEDGER.md row (EXPLORATORY,
label-free, corpus-level); exactly ONE commit
`feat(m4-u): U1 — order-borne selection identity — <VERDICT>`, never amended,
never pushed by the executor. Suite must be green (1021 + new) before commit.
Blocking gates: fold-purity assertion, exact-bag shuffle invariance test,
MH stationarity contract, ID-leak scan (0 of 1401 cohort IDs in any committed
artifact), timestamps in prose verified against artifacts.

Config pins: SEED = 20260818; folds = 5 (KFold shuffle=True, random_state =
SEED); per-fold cluster seed SEED+1000·fold; α = 0.5; B_shuffle = 499;
B_bootstrap = 1000; C primary 24; pools 984/821; data =
`/Volumes/mobile3/projects/project persona/data_sets/PANDORA_official/all_comments_since_2015.csv`
(columns author, subreddit, created_utc, link_id only; no bodies);
cohort = `results/m4_sr0_recon/cohort_authors.csv`; vocabulary reconstruction
via the T1 pattern (import by file, provenance stated).
