# SUICA Defense Phase — Plan (registrations and outcomes)

Phase opened per the charter (`docs/SUICA_DEFENSE_PHASE_CHARTER.md`);
resumed 2026-08-10 after the M4-L line closed. All standing rules 1–21
and conventions bind. Defense legs license no new theory claims; they
strengthen, qualify, or kill existing ones.

---

## D1 — Prospective seal #2: the measured laws must predict, not describe

**REGISTERED 2026-08-10, BEFORE RUN.** Planner: this document's author.
Executor: dispatched agent. The cheapest, highest-leverage defense: the
program's laws (K-line and L-line) are sealed as QUANTITATIVE
predictions for configurations NOBODY HAS RUN, before anyone runs them.
A future opening leg runs the configurations FIRST, then unseals.

### Protocol authority

OP-31 ("prospective seal #1, the time lockbox") is the precedent. The
executor LOCATES its protocol and artifacts (search docs/, scripts/,
results/ for lockbox/seal/OP-31 naming), follows its sealing mechanics
(salted hash; where salt and plaintext live; what is committed), and
cites them. If OP-31's protocol is unlocatable or incompatible, the
fallback is pre-declared: salted SHA-256; the sealed plaintext bundle
under `results/d1_sealed/` (gitignored) with a copy instruction for the
owner in the report; ONLY the hash, the salt-handling statement, and
the opening protocol are committed. The deviation is disclosed.

### The registered prediction set (computed from PUBLISHED constants and formulas ONLY)

- **S-1 (η-floor curve, new config):** m=96, k_τ=4, G=5, n_occ=8,
  identity energy at the ρ.55-equivalent; η ∈ {0, 0.5, 1}: predicted
  per-boundary error rates from σ_u²(η) = η·σ_b²/k_τ + (1−η)·σ_b²/m
  (appendix R.1's law).
- **S-2 (tax ratio, new config):** the boundary z-ratio √(m/k_τ) =
  √24 at that config, with the predicted ARI-drop direction.
- **S-3 (window-width conjecture, first quantitative seal):** the
  localization-window widths at two (d/n) settings — (48, 512) [known
  empty] and (192, 256) [conjectured open] — from the L2 energy
  criterion plus the (d/n)^¼ scaling; sealed as interval predictions.
- **S-4 (K-line variance-tax law):** predicted b-only field recovery
  at a NEW state arm (share .40, φ .90) on the K2b instrument, from
  field ≈ λ·r^q − κ·V_person with the published λ = 0.17417497661611914,
  q = 1.8528700746510731, κ = 0.7220359963712748 and the validated
  attenuation algebra.
- **S-5 (taxometer):** predicted η̂ reading ± its certified budget at a
  new η = 0.6, ρ.45-equivalent cell.

Each entry is sealed with: the formula, the constants' provenance
(file + field), the computed value(s), and a falsification band (the
prediction's own registered tolerance, rule-19 compliant: each band on
the law's OWN quantity).

### Gates

- **G0D (provenance)** — every constant re-derived bit-exactly from
  persisted decision.json/gates.json files (round-trip parsing), cited
  by path and field.
- **G1D (purity, rule-3 analogue)** — THIS LEG GENERATES NO WORLD of
  any kind. Prediction arithmetic only. Any world generation is a
  defect → STOP. (The point of a prospective seal is that the sealed
  values were computable without touching the target configurations.)
- **G2D (seal integrity)** — the committed hash re-verifies against
  the sealed bundle; the bundle contains the full prediction table,
  the salt-handling statement, and the opening protocol.
- **G3D (rule 16, trivial)** — outcomes: SEAL-COMPLETE (all five
  entries computed, sealed, hash committed) / SEAL-PARTIAL (any entry
  uncomputable from published constants — named, sealed without it) /
  SEAL-FAIL (protocol failure). One of three, enumerated.

### Opening protocol (registered now, binding later)

The seal opens ONLY in a future registered leg (D-open) that: (1) runs
the five configurations FRESH, adjudicating against the sealed bands
BEFORE unsealing; (2) then unseals and verifies the hash; (3) scores
each entry PREDICTED/MISSED with no re-fitting. Trigger: the program
owner's request, or the defense phase reaching D4, whichever first.

### Deliverables

The six: `scripts/run_suica_d1_prospective_seal.py`; the sealed bundle
per protocol; `reports/SUICA_D1_PROSPECTIVE_SEAL_REPORT.md` (protocol
citation, provenance table, the HASH, the opening protocol — never the
plaintext values); outcome appended here; ledger row; ONE commit
(`feat(defense): D1 — ...`), never amended, not pushed by the agent.
Budget: arithmetic only; target < 10 min wall.

### OUTCOME (appended 2026-08-10, after run) — `SEAL-COMPLETE`

**All five entries sealed. Zero world generations. 0.875 s wall.**

- **sha256 (salted)** = `3a1971b827210b7f3611b4769496f9d55d4ea815b6b8b577cae81f64b1fe00f8`
- report: `reports/SUICA_D1_PROSPECTIVE_SEAL_REPORT.md`; script:
  `scripts/run_suica_d1_prospective_seal.py`; bundle:
  `results/d1_sealed/D1_SEALED_BUNDLE.json` (gitignored; the report carries
  the owner's copy instruction).

**Protocol.** OP-31 was located (`docs/OP31_PROSPECTIVE_SEAL.md`;
`scripts/run_suica_op31_prospective_seal_v1.py`). Its HASH MECHANIC was
adopted verbatim (op31:64-65, canonical `sort_keys` JSON SHA-256). Its
CONCEALMENT MODEL is incompatible — OP-31 could commit plaintext because its
target text did not yet exist, whereas D1's five configurations are runnable
today — so the registration's pre-declared fallback supplies the storage
model (salted hash, gitignored bundle, hash-only commit). Deviation disclosed
in the report's Part 0.1.

**G0D.** All 14 constants round-trip bit-exactly (residual `0.0` on every
row), plus a six-row source-object drift check and a FORMULA round-trip: the
three K2c pair arms re-derived through the very functions S-4 calls
(`predicted_attenuation`, `person_share_design`) reproduce K2c/K2d's
persisted `r` and `V_person` bit-exactly. Two provenance corrections to this
registration's own text, disclosed not silently followed: (i) κ is NOT in
`results/m4_k2d_frontier_carrier/decision.json` — it lives in the sibling
`post_hoc_descriptive.json` under `kappa_ols_through_origin`, re-derived
bit-exactly by K2e; (ii) every persisted κ field is NEGATIVE where this
registration writes it positive, which is the same arithmetic under the
law's own minus sign.

**G1D PASS, enforced in code.** Fifteen world/panel/card generators replaced
by raising stubs before any entry was computed; **0** fired. RNG calls
attributed by IMMEDIATE calling frame: exactly **one** SUICA-attributed call
in the whole run (`suica_core/v8_realtext_relation_field.py:198`,
`frozen_random_directions`, the FROZEN GAUGE DIRECTIONS reached through
`k2b.layout()` while S-4 asks for `r` — a frozen operator constant,
independent of `share` and `phi`, not a world), disclosed as purity note
D1-PN-1; 46 third-party `scipy.stats` import-time calls counted and
excluded. A G2D sub-gate additionally searches the committed report for every
one of the 49 prediction-bearing numeric leaves: **0 leaks**, with two
published L2 window edges whitelisted and their unavoidable overlap
disclosed in Part 0.2.

**G2D PASS.** The bundle was re-read from disk and re-hashed after writing;
the recomputed hash equals the committed one. The bundle carries the full
five-entry prediction table, the salt-handling statement and the opening
protocol. `--verify` re-runs this check standalone.

**Five rule-9 pins worth the planner's attention** (all written to Part 0
BEFORE the seal): **RN-D1-3** S-1 seals the LATENT floor, not
`l2.predicted_boundary_error_l2` — the card-space realization needs a world's
loadings, so calling it would have violated G1D; l2:391-393 certifies the two
coincide when M is an isometry. **RN-D1-4** for a regular simplex `G` changes
the boundary COUNT (`C(5,2)=10`) not the per-boundary RATE, and `n_occ` does
not enter the identity-only floor at all; the registered config is internally
consistent (`k_tau = G-1`). **RN-D1-1/2** "ρ.55-equivalent" is read as L2's
term of art (a fixed number transported unchanged), with the Δ-free
`rho_id=0.55` form at G=5's own simplex constant sealed as a NAMED COMPANION
that cannot be promoted at opening time. **RN-D1-5** S-3's `d` is pinned to
the LATENT dimension `m` (k2a:89), not `DIM=64` — which makes the
registration's "known empty" label at `(48, 512)` true by L2's own
measurement rather than by extrapolation. **RN-D1-6/7/8** every band constant
is DERIVED from a persisted record (L2's ten-cell W-3 containment record; the
9-pair κ residual record; L3 X-2's certified `±0.125`); the only free choices
are two safety factors and the S-3 multiplier, all fixed before any value
existed.

**Note for D-open.** S-3 is the one entry whose miss is cheap: it is
CONJECTURE-GRADE and its failure kills the `(d/n)^(1/4)` window conjecture
only. S-1/S-2/S-4/S-5 misses fall on the measured laws. S-2 in particular is
exact algebra with no numeric freedom — a miss there would mean the
boundary-z derivation itself is wrong.

### Planner adjudication (2026-08-10, appended after the run)

**SEAL-COMPLETE accepted.** The hash mechanic is OP-31's verbatim; the
concealment deviation was pre-declared and is correct (D1's targets are
runnable today, OP-31's were not). G1D's purity was ENFORCED, not
asserted (15 generators stubbed, 0 fired; the single SUICA-attributed
RNG call is the frozen gauge-direction constant, disclosed as D1-PN-1
and correctly judged not-a-world). **Planner defect #39 (rule-8 family,
recorded):** my registration cited κ at the wrong path AND with the
wrong sign convention; the executor corrected with disclosure and
re-derived bit-exactly from the true sources. Noted for the record:
OP-31's own results-bundle is absent on this machine — its seal of
record is the tracked doc + script constant.

**OWNER ACTION REQUIRED (surfaced in the session report):** the sealed
plaintext bundle exists ONLY at
`results/d1_sealed/D1_SEALED_BUNDLE.json` on this machine (gitignored,
mode 0600). It must be copied off-machine; a lost bundle voids the
seal. The committed hash proves nothing without it.

---

## D2 — Adversarial verification pass over the program's headline table

**REGISTERED 2026-08-10, BEFORE RUN.** Planner: this document's author.
Executor: dispatched agent, INDEPENDENT of every original executor and
tasked to REFUTE, not to confirm. Artifact-space only — a G1D-style
purity gate binds (no world generation; verification by re-derivation
and cross-document consistency only).

### The claim table (10 rows, verbatim targets)

- **C1** K1-L1: shared-design cancellation exact — 0 flips / 31,520,
  card-difference invariance ≤ 4.2e-16.
- **C2** K1-L2/L3: issuer price +0.09695431472081219 pooled with 8/8
  signs; 1/|P| slope −1.0865327686128703 ⊂ [−1.35, −0.65].
- **C3** K1-L5: deployed-gauge amplification +0.092543049 at 1× =
  3.54× F2's composition effect (+0.026163263306726227).
- **C4** K1b/K1c′: author-reading share −0.949 [−1.158, −0.753] at
  κ=1.0 and −0.9443843417103447 [−1.2340, −0.7046] at κ=0.5.
- **C5** K1d: γ_deleted = 1.2446190431788744 [1.1185, 1.3579]
  overlapping F4's band; half-agreement budget 48.865× → 19.878×.
- **C6** T4 composite constants: λ = 0.17417497661611914,
  q = 1.8528700746510731 [1.7147, 1.9996], κ = −0.7220359963712748
  (R² 0.9935185860651237); K2e DM collapse 67.04–78.83%.
- **C7** K3: anti-direction bound 0 violations / 3,139,584; binds at
  50.48%; rotation cos-law max error ≤ 0.0035.
- **C8** L-line floor law: three independent confirmations (L1 poles,
  L2 curve 7/10 + exact ordering, L3 fresh-seed reproduction).
- **C9** L3 taxometer: |η̂ − η| ≤ 0.125 in 10/10 with median 0.0241;
  ordering Spearman 1.0 under every reading.
- **C10** K-R1: de-framing harms — all six arms DOWN, 0/32 worlds
  positive anywhere; λ 0.1821 → 0.0008.

### Method (per claim)

Re-derive every cited number from persisted artifacts at full precision
(round-trip parsing; raw per-cell files preferred over summaries);
attempt refutation: recomputation where formulas are published,
cross-document consistency (decision/gates vs report vs plan-doc vs
ledger vs IDT appendices), unit and sign checks, CI-endpoint
recomputation from persisted draws where present. Verdict per claim ∈
{CONFIRMED, QUALIFIED (named discrepancy at or below display
precision), REFUTED (a cited number is wrong at full precision, with
the true value), UNVERIFIABLE (artifact gap — name the missing file)}.
Enumerated; no other cell.

### Routing (rule 16)

- Any REFUTED → **P1V:** the planner writes a dated correction and
  claim-strength downgrade for that row (the program's retrospective
  mechanism); remaining rows still reported.
- Any UNVERIFIABLE → **P2V:** the missing artifacts feed D3's lockbox
  specification (that is D3's charter input).
- All CONFIRMED/QUALIFIED → **P3V:** the headline table gains a
  D2-verified stamp (dated note in IDT and both syntheses).

### Deliverables

The six: `scripts/run_suica_d2_adversarial_verification.py` (the
re-derivation harness); `results/d2_verification/` (per-claim
worksheets — gitignored); `reports/SUICA_D2_ADVERSARIAL_VERIFICATION_REPORT.md`
(per-claim verdicts with evidence); outcome appended here; ledger row;
ONE commit (`feat(defense): D2 — ...`), never amended, not pushed by
the agent. Budget: artifact-space; target < 30 min wall.

### D2 outcome (appended 2026-08-10, AFTER run)

Executed by a dispatched agent independent of every original executor,
refute-tasked. Harness
`scripts/run_suica_d2_adversarial_verification.py` (re-runnable, 0.5 s);
worksheets `results/d2_verification/` (gitignored); report
`reports/SUICA_D2_ADVERSARIAL_VERIFICATION_REPORT.md` (Part 0 attack plan
written before verification, then per-claim worksheets).

**Verdicts: C1 CONFIRMED, C2 QUALIFIED, C3 CONFIRMED, C4 CONFIRMED,
C5 CONFIRMED, C6 CONFIRMED, C7 CONFIRMED, C8 QUALIFIED, C9 QUALIFIED,
C10 CONFIRMED — 7 / 3 / 0 / 0.** No REFUTED, no UNVERIFIABLE: every
artifact the ten rows need exists locally and every headline number
re-derives at least to display precision. **Routing: P3V** (P1V and P2V
do not fire).

The three qualifications, named exactly:

- **C2** — the pooled issuer price is *stronger* than cited (it is the
  exact rational 191/1970, whose nearest double is the cited
  0.09695431472081219, 8/8 signs). But the 1/|P| slope
  −1.0865327686128703 persisted in `m4_k1_issuer/decision.json` is
  **1.179e-13** away from the exact-rational OLS of that same file's
  `mu_err_var` column, which is **−1.0865327686127524**. Seven
  independent estimator formulations agree with each other to 3.3e-15
  and all disagree with the citation identically, so this is not
  float64 noise; the fit consumed low-bit-different inputs upstream of
  the persisted CSV. Digits 14–17 only; L3's operative clause
  (slope ⊂ [−1.35, −0.65], a manipulation check) is untouched.
- **C8** — L2's "7/10 + exact ordering" is confirmed exactly. The other
  two confirmations are weaker than the row implies: **L1's poles are a
  0.0-vs-0.0 check** on two cells the artifact itself records as
  BIT-IDENTICAL panels (`/leans/V-1/note`), and **L3's containment is
  7/10, not stated** — its three misses are cells with a degenerate
  [0,0] measured CI against predictions of 3.57e-14, **2.18e-04** and
  3.34e-07, the middle one not excusable as machine scale. The three
  confirmations are three seed-and-grid variations of ONE prediction,
  not three independent predictions.
- **C9** — all cited numbers re-derive (10/10 within 0.125; median
  0.024078 → 0.0241; Spearman exactly 1.0 in all 10 per-arm slices
  across 5 estimators × 2 energy arms). Two qualifications: the
  universal "**under every reading**" fails for the cross-arm pooled
  reading (**0.9847**, all three principal estimators); and the row is
  silent on lean **X-1**, whose state is **MISS** — only 2/4 poles are
  calibrated, with both η=0 poles' CIs **excluding** the true value
  (η̂ = 0.0924 CI [0.0315, 0.1554]; η̂ = 0.0495 CI [0.0089, 0.0915]).
  The taxometer is biased up at zero and the leg routed P2N.

Four **citation defects** found outside the D2 rows, for the planner's
P3V stamp rather than for the verdict cells: (i) IDT appendix C.1's
"31,520 … across all five norm arms" — 31,520 is four non-oracle arms
(five gives 39,400) — and it drops the reader-A qualifier while reader
B has **5,473** flips in the same cells (the leg report discloses this,
the appendix does not); (ii) IDT appendix C.2's "free designs are inert
(|Δ| ≤ 0.0045)" — the true max is **0.004512746557818383**, so the
inequality as written is false by 1.27e-05; (iii) the C2 slope above;
(iv) C10's "0/32 worlds positive anywhere" — the quantifier ranges over
**192** arm-world deltas, all recomputed here from raw and all
non-positive, so the true statement is strictly stronger.

Near-misses and fragilities recorded even where CONFIRMED: C7's cos-law
bound uses **99.8%** of its own 0.0035 headroom (measured 0.00349189);
C5's γ is **weight-scheme dependent** (unweighted OLS moves it 0.007–0.010)
and its "overlapping F4's band" is the same interval restated, not two
independent estimates; C6's q is three different numbers across legs
(1.8329 / 1.8529 / 1.9338) with R² 0.868 for the 19-arm fit, and κ's
R² 0.9935 rests on six leveraged pairs (the 9-pair refit moves it to
−0.7146, with two pairs at Δvar ≈ 0 producing per-pair κ of 4.6e+14 and
null); C10's de-framed λ = 0.0008 is a boundary value on an
**unidentified** power law, not a fitted estimate.

Purity gate held: no worlds generated, no world/panel builder called,
`suica_core/` untouched; `f1.fit_axis` was re-implemented from source
text rather than imported so that C5's bit-exact agreement is evidence
and not a tautology. Budget: harness 0.5 s, leg wall **~80 min against a
< 30 min target — over budget, disclosed**; the overrun is entirely in
reverse-engineering undocumented aggregation formulas (C5's WLS, C6's κ
regression, C7's cos-law) from persisted artifacts, with the three
timed anomalies listed in the report's Part 6.

### Planner adjudication (2026-08-10, appended after the run)

**P3V executes: the 10-row headline table is D2-VERIFIED (7 CONFIRMED /
3 QUALIFIED / 0 REFUTED / 0 UNVERIFIABLE)** — an adversarial,
refute-tasked, independent re-derivation from raw per-cell rows, with
every failed refutation attempt on the record. The three QUALIFIED rows
and four citation defects are WORDING debts, all mine, none numeric at
claim level; they are corrected by dated note (IDT appendix T), never
rewritten. Highlights of the verification's strength: C4's share
bit-exact from 128 raw world rows; C5's fitter re-implemented from
source text so bit-exactness is evidence, not tautology; C10's 0/192
recomputed from the 48 raw per-world files.

**Planner defect #40 (recorded, 4 instances, rule-8-in-prose):**
appendix C.1's "five arms" (31,520 is four; reader-A only); appendix
C.2's "≤ 0.0045" (true max 0.004512746557818383); K-R1's "0/32 worlds"
(true and stronger: 0/192 arm-worlds); synthesis wording on the floor
law's "three confirmations" and the taxometer's "every reading"
(cross-arm pooled Spearman is 0.985, not 1.0). One upstream artifact
note: K1's persisted L3 slope differs from the exact-rational OLS of
its own CSV by 1.18e-13 (−1.0865327686128703 vs −1.0865327686127524) —
sub-display-precision, containment unaffected, recorded.

**Fragility annex adopted (binds D1's opening expectations):** q is
three numbers across legs (1.8327/1.8529/1.9338; 19-arm R² 0.868); κ's
R² 0.9935 rests on six leveraged pairs (9-pair refit −0.7146; two
Δvar≈0 pairs degenerate); γ is weight-scheme dependent (±0.01); C7's
cos-law bound consumes 99.8% of its own headroom; de-framed λ = 0.0008
is a boundary value on an unidentified power law. **Convention added:
every future leg's decision.json aggregates name their computing
function (file:line) — D2's 55-minute overrun was the price of
undocumented aggregation.** D2's budget overrun (85 vs 30 min) is
accepted as disclosed and well-caused.

---

## D3 — The artifact lockbox: verification must survive this machine

**REGISTERED 2026-08-10, BEFORE RUN.** Planner: this document's author.
Executor: dispatched agent. D2 proved every headline claim re-derives
from local artifacts — which all live in gitignored, machine-local
`results/` trees. D3 makes that verification portable: a
content-addressed archive whose MANIFEST is committed, so that any
future holder of (repo + archives) can re-run D2's harness.

### Scope (the archive set)

The thirteen `results/` trees named in D2's registration, plus
`results/d1_sealed/` and `results/d2_verification/`. Per tree: a
deterministic tar (sorted paths, fixed mtimes) compressed, its SHA-256,
and a per-file manifest (path, size, SHA-256).

### Gates

- **G0X (completeness)** — the manifest covers every file D2's harness
  read (cross-checked against the harness's own input list) and every
  file in the fifteen trees; any file present-but-unreadable is a
  defect.
- **G1X (integrity)** — after writing, every archive is re-read,
  re-hashed, and one sampled file per tree is extracted and compared
  byte-for-byte.
- **G2X (purity)** — no world generation; archival I/O only.
- **G3X (rule 16, trivial)** — LOCKBOX-COMPLETE / LOCKBOX-PARTIAL
  (named gaps) / LOCKBOX-FAIL.

### Committed vs local

COMMITTED: the manifest (`docs/SUICA_D3_LOCKBOX_MANIFEST.json` — paths,
sizes, per-file and per-archive SHA-256, creation protocol). LOCAL
(gitignored): the archives under `results_lockbox/`, with the owner
copy instruction repeated in the report (same standing as D1's bundle:
off-machine copies are the owner's action).

### Deliverables

The six: `scripts/run_suica_d3_artifact_lockbox.py`; the archives +
committed manifest; `reports/SUICA_D3_ARTIFACT_LOCKBOX_REPORT.md`;
outcome appended here; ledger row; ONE commit
(`feat(defense): D3 — ...`), never amended, not pushed by the agent.
Budget: I/O only; target < 15 min wall.

### D3 outcome (appended 2026-08-10, AFTER run)

**G3X: LOCKBOX-COMPLETE. Zero named gaps.** Harness
`scripts/run_suica_d3_artifact_lockbox.py` (re-runnable, 11.5 s);
archives `results_lockbox/` (gitignored, local); committed manifest
`docs/SUICA_D3_LOCKBOX_MANIFEST.json` (79 KB, 363 file entries); report
`reports/SUICA_D3_ARTIFACT_LOCKBOX_REPORT.md` (Part 0 — scope
reconciliation, pinned conventions, tool versions — written and flushed
to disk BEFORE the first archive was built).

**Scope reconciliation, and a wording debt in this registration.** The
Scope paragraph above says "the thirteen `results/` trees named in D2's
registration, plus `results/d1_sealed/` and `results/d2_verification/`",
and G0X then calls the total "the fifteen trees". Enumerating what D2's
claim table actually names gives **fifteen** `m4_*` trees, not thirteen —
C6's T4-composite row alone covers five (`k2a`/`k2b`/`k2c`/`k2d`/`k2e`)
and C4 covers both `k1c_ownership_live_knob` and
`k1c_prime_author_share`. The true total is **15 + 2 = 17**. D3 archived
all **17** — the superset, so nothing the registration intended is
missing under either reading. **Planner defect #41 (rule-8-in-prose,
recorded):** the same arithmetic slip carried twice in one section.

**Contents: 17 trees, 363 files, 168,659,718 source bytes →
72,392,388 archive bytes (42.9%).** Largest trees `m4_k2c_matched_pairs`
(37 files / 47.7 MB), `m4_k2d_frontier_carrier` and
`m4_k2e_double_matching` (35 files / ~41 MB each); smallest
`results/d1_sealed` (2 files / 20 KB).

**G0X PASS.** D2's input list was extracted **by AST from D2's own
source**, not read off by eye: 20 distinct literal `rt()`/`js()` paths,
all 20 covered, plus 2 f-string path templates expanding to 48 archived
files (the K-R1 per-world `cell_*_{intact,deframed}_w*.csv` chunks) —
**68 D2 input files covered, 0 uncovered, 0 templates matching nothing**.
Every one of the 363 files was opened and read to EOF while hashing: no
unreadable file, no symlink, no special file, no size drift. D2's single
non-`results/` read (`docs/SUICA_M4_F_PANEL_DESIGN_SYNTHESIS.md`) is a
tracked repo file, recorded as covered-by-git rather than by the lockbox.

**G1X PASS 17/17.** Every archive re-read from disk, re-hashed against
its in-memory hash, decompressed and checked against its inner-tar hash,
and one sampled member per tree (D3-R6: largest file) extracted and
byte-compared with the original — **16,380,860 sampled bytes, all
identical**.

**Determinism: DETERMINISTIC.** The D3-R7 probe (`m4_kr1_deframing_repair`,
most files) built twice in-process is byte-identical. Stronger, unplanned:
the harness ran as **three separate processes** and all 17 archive
SHA-256s were identical across every invocation, so determinism survives
process restart.

**G2X purity ENFORCED, not asserted:** stdlib imports only — not even
`numpy` — audited by a `sys.modules` scan at exit (0 `suica*` modules at
entry, 0 at exit). 0 worlds, 0 panels, 0 RNG calls, `suica_core/`
untouched.

Four observations, none changing a verdict. (1) The scope arithmetic
above. (2) **`results_lockbox/` was NOT gitignored** when the leg began
(`git check-ignore` returned 1); the rule was added to `.gitignore` in
this leg's single commit — disclosed because it is a repository change
the registration did not itemise, and without it ~69 MB of archives
would have been commit-eligible. (3) **The committed manifest now
carries an *unsalted* SHA-256 of `results/d1_sealed/D1_SEALED_BUNDLE.json`.**
D1's public commitment is deliberately *salted*, and the salt exists to
stop an adversary confirming a *guessed* plaintext; the registration
binds this manifest to a per-file SHA-256 for every file in every
in-scope tree, `d1_sealed` included, so it was published as instructed.
Practical leak nil (a ~20 KB JSON, not a short guessable string) and the
net effect is a strictly stronger commitment — flagged anyway, because it
narrows a protection D1 bought on purpose. The sealed bundle itself was
archived as **opaque bytes**: never parsed, never printed, never
summarised. (4) Source file modes are normalised away (D3-R3) so the
archive hashes do not inherit this volume's permission quirks; `d1_sealed`
is mode 0700 here, not the 0600 D1's adjudication records.

**Protocol, pinned by written rule before the run (rule 9).** Compressor
by the rule *"zstd iff `import zstandard` succeeds in the declared
interpreter, else gzip"* — `zstandard` is **not importable** in the venv
(a `zstd` CLI exists on this machine but the rule says *in the venv*, and
stdlib gzip is the more portable choice for an archive meant to survive
this machine), so **gzip**, `compresslevel=9`, `mtime=0`, no FNAME.
Tar: `USTAR_FORMAT`, members sorted by UTF-8 byte order, explicit
directory entries, `mtime=0`, `uid=gid=0`, empty `uname`/`gname`, fixed
0600/0700 modes, no atime/ctime field in the format at all. Member paths
carry the `results/` prefix so `tar -xzf` at the repo root restores in
place. **Both** the inner-tar and the compressed-archive SHA-256 are
recorded (D3-R5), so content identity survives a future zlib version
change. Verified with stock system tools outside the harness: BSD
`tar -tzf` lists members cleanly, `shasum -a 256` reproduces the
manifest hashes, and a `tar -xzf` + `diff -r` round trip of
`m4_l1_typed_world` reports no difference.

**Budget: 11.5 s harness, leg well inside the < 15 min target.** No
run-time anomalies.

**OWNER ACTION REQUIRED (same standing as D1's bundle, repeated in the
report's Part 8):** the 17 archives exist ONLY at `results_lockbox/` on
this machine, gitignored, 72,392,388 bytes total. The manifest is
committed; the archives cannot be. **Copy the directory off-machine** —
a committed manifest whose archives no longer exist proves only that the
bytes were once hashed, not that anything is still verifiable.

### Planner adjudication (2026-08-10, appended after the run)

**LOCKBOX-COMPLETE accepted.** Determinism verified across process
restarts (stronger than registered); D2-input coverage proved by AST
extraction, 68/68; G1X 17/17 with 16.4 MB of byte-compared samples;
purity held at stdlib-only. The gitignore gap was found pre-run and
fixed in-commit, disclosed.

**Ruling on anomaly 2 (the unsalted bundle hash in the committed
manifest):** SAFE AS PUBLISHED, no redaction. D1's bundle EMBEDS its
32-byte random salt inside the sealed bytes, so the manifest's unsalted
SHA-256 commits to content containing 256 bits of entropy — a
confirm-a-guess attack must guess the salt too. Net effect is a
strictly stronger commitment, exactly as the executor analyzed.
**Convention added (defense):** every sealed artifact EMBEDS its salt
within the sealed bytes (as D1 did), so any future manifest, backup, or
lockbox hash of a sealed file remains guess-proof by construction.

**Planner defect #41 recorded** (rule-8-in-prose, twice in one
section): the D3 registration's "thirteen trees…the fifteen" — D2's
table names fifteen m4 trees; true scope 17. The executor archived the
superset and reconciled in Part 0, correctly. Mode-bit volume quirk
(0600 recorded vs 0700 reported) noted, no action.

**OWNER ACTION (updated, cumulative):** copy off-machine —
`results/d1_sealed/` (the seal's plaintext+salt) AND `results_lockbox/`
(17 archives, 72,392,388 bytes). With those two copies plus the repo,
every headline verification and the D1 opening survive this machine.

---

## D4 — Real-text governance rule (planner-written; operationalizes IDT §8)

**EXECUTED 2026-08-10 as a planner document** —
`docs/SUICA_REALTEXT_GOVERNANCE.md` (normative, append-only). Defense
legs license no new theory claims; this one licenses REFUSALS. Summary
of its binding rules: no per-person claims outside a sealed,
owner-signed protocol; identity readings on real text REQUIRE the
frame-refreshed discriminator (T6″ — shared-frame reproducibility may
not be published as person-content, per T9); NO cross-corpus author
linkage is ever computed (the capability T3/T6 prove possible is
exactly what governance forbids exercising outside owner-signed defense
audits with no retained linkage tables); de-framing is diagnostic-only
(scaffold corollary); any grouping published on real text carries its
completeness defect (cross-fitted, with the precision statement); raw
text never enters the release repo; sealed artifacts embed salts;
exceptions only via new study ID + owner sign-off + D2-style adversarial
pass. Native-corpus work remains paused by the owner's 2026-07-12
decision; nothing here unpauses it.

---

## D5 — The rule machine, replayed (the defense phase's closing leg)

**REGISTERED 2026-08-10, BEFORE RUN.** Planner: this document's author.
Executor: dispatched agent. Document-space only (purity: no worlds, no
artifact recomputation — this leg audits the METHOD, not the numbers).

### Question

The program has recorded 41 planner defects and paid for 21 standing
rules plus conventions. Replay: for each recorded defect #1–#41, would
TODAY'S rule set have caught it, and at what stage? The output is a
coverage table and at most three PROPOSED (not enacted) refinements.

### Method

1. **Compile the defect registry** — `docs/SUICA_DEFECT_REGISTRY.md`:
   one row per defect (#1–#41): where recorded (doc+section), one-line
   description, the rule it paid for (if any), family. Sources: the
   M4-D/G plan docs (defects 1–8 era), the M4-K plan doc (#9–#26), the
   M4-L plan doc (#27–#38), the defense plan (#39–#41). This registry
   is itself a durable deliverable.
2. **Replay classification** per defect: (a) covering rule(s) today;
   (b) catch stage under today's gates — REGISTRATION-TIME (rule
   text/enumeration/satisfiability would refuse it), PART-0 (a gate
   catches it before arms), POST-HOC (only adjudication catches it),
   UNCOVERED (no current rule addresses the class); (c) whether the
   historical catch stage was later than today's (the machine
   improved) or the same.
3. **Coverage stats** + at most three proposed refinements for
   UNCOVERED classes, each with the defect(s) motivating it — PROPOSED
   status only; enactment is the planner's, by dated note.

### Gates

G0R: registry completeness — every defect number cited in any plan doc
appears exactly once (grep-verified, counts reported). G1R: purity
(document reads only). G2R (rule 16): verdict ∈ REPLAY-COMPLETE /
REPLAY-PARTIAL (named gaps) / REPLAY-FAIL.

### Deliverables

The six: `scripts/run_suica_d5_rule_replay.py` (the grep/compile
harness); `docs/SUICA_DEFECT_REGISTRY.md` (committed — the registry IS
a deliverable); `reports/SUICA_D5_RULE_REPLAY_REPORT.md` (the coverage
table + proposals); outcome appended here; ledger row; ONE commit
(`feat(defense): D5 — ...`), never amended, not pushed by the agent.
Budget: document-space; target < 20 min wall.
