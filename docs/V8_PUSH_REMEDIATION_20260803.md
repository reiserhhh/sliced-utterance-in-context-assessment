# V8 Push Remediation — 2026-08-03

Scope: the unpushed V8/M3/M4 drop (5 commits landing 2026-08-01, ~890 files,
`4eb0124..b137dae`) plus the subsequent M4-D/E/F arc was reviewed on
2026-08-01. Substance verdict was TRUST (15/15 headline numbers traced to
artifacts, 9 recomputed from row data exactly; suite green). Governance
verdict was MAJOR_ISSUES, concentrated in one campaign. This document is the
dated, append-only adjudication that clears the push gate. Every edit it
mandates is either an append or a marked inline correction; no original text
is deleted, no history is rewritten, no run artifact is modified.

Items 1–5 below were the registered push blockers; item 6 codifies process
rules; item 7 is the research-repo reconciliation.

---

## Item 1 — PANDORA external-connection campaign (most severe)

**Facts (artifact-backed).** On 2026-07-28, Big5 labels (1,401 users), four
MBTI-axis label sets (9,042 users), and the strict both-label bridge cohort
were joined in one day with no registration document written before the
join — the program's largest single-day label consumption. Two full runs
executed the same morning (UTC, from `decision.json` `completed_utc`):

- 04:29:15Z `full_20260728` (official-prepared-input pipeline; geometry-ready
  3,813; strict-bridge n=78): bridge v8_canonical element r = **−.103**
  (permutation p=.673). Companion rows: nuisance_only **+.384** (p=.028),
  v8_plus_nuisance **+.463** (p=.009), v7_author48 **+.438** (p=.0074).
- ≈04:34Z: run-1 `REPORT.md` duplicated byte-identically as
  `REPORT_OFFICIAL_PREPARED_INPUT.md`.
- 05:04:42Z `operator_aligned_clean_20260728` (frozen native operator +
  leakage cleaning; geometry-ready 7,523; strict-bridge n=264): bridge
  v8_canonical element r = **+.498** (permutation p=.0086).

Only run 2 was written up (`reports/V8_PANDORA_EXTERNAL_CONNECTION_REPORT.md`
and ledger row V8-PAN-EXT1 cite only `operator_aligned_clean_20260728`). No
tracked file disclosed run 1, its null, or the order. No `run_manifest.json`
exists in any of the three run directories.

**Verdict.** The bridge headline is **POST_HOC_OPERATOR_SELECTED
EXPLORATORY**: the operator was switched after observing the first null, the
headline contrast "V8 beyond nuisance" flips sign across the two operators
(≈−.49 → +.289), and the selection was undisclosed. This is the same failure
family as the V7-era E4 post-hoc case, here with label contact. What survives
untouched: the direct-prediction nulls (Big5 r=−.005, MBTI AUC .544, both
below nuisance), label-blind scoring, zero source/bridge overlap in both
runs, and the report's own claim boundary.

**Actions taken.** Report addendum "Post-hoc adjudication (2026-08-03)" with
the full timeline and both runs' numbers; ledger row V8-PAN-EXT1-ADJ1;
annotations at every tracked citation of the .498 figure
(`docs/V8_MATHEMATICAL_RESEARCH_ROUTE.md`,
`docs/SUICA_UNIFIED_THEORY_SYSTEM_V8.md` §12). Forward rule (binding):
operator fixed and registered before any label join; every operator run on
the question reported together; fresh folds or fresh data for any
confirmatory tier.

## Item 2 — Essays confirm-half text consumption

**Facts.** `load_essays_events`
(`scripts/run_suica_v8_realtext_relation_field.py`) reads the TEXT of every
Essays row (`usecols=[user_id, text]`; label columns never loaded) and orders
authors by fresh salt `"v8rt-essays"`, bypassing the frozen 50/50 dev/confirm
split. Executed 2026-07-29..30 in `v8_corpus_local_composition_residual`,
`v8_conditional_concordance_spectrum`, `v8_exchangeable_background_audit`
(smoke+audit each).

**Verdict.** Label budget INTACT (labels never read). Text-untouched status
of the confirm-half **SPENT**. Not a label-leak event; it is the loss of a
design resource that must be recorded, not hidden.

**Actions taken.** Dated note in `docs/V7_LOCKBOX_V020.md`; README holdout
sentence qualified; governance note in the loader docstring; ledger row
V8-ESSAYS-TEXT1; research-repo audit entry (item 7). Rule: no future design
may claim a text-blind Essays holdout; text-blind designs need fresh data.

## Item 3 — V8 thesis §12 tier wording

`docs/SUICA_UNIFIED_THEORY_SYSTEM_V8.md` §12 listed "limited external
relationships under explicit protocols" under "Supported within named
domains" — stronger than the ledger's own EXPLORATORY row. Fixed in place:
now "limited exploratory external relationships", with the post-hoc
operator-selection caveat and a pointer here.

## Item 4 — F16 hash-drift statement vs green lock tests

**Facts (three-way check, 2026-08-03).** Run-time `source_lock`
expected/observed hashes in the persisted decisions were compared with the
committed tree:

- R2E: 9/9 and 9/9 (smoke, discovery) match.
- R2E1: discovery 10/10 match; the corrected smoke's runner hash differs —
  the runner was corrected between smoke and discovery on 2026-07-27, and the
  tree matches the surviving discovery state.
- R2E2: 11/11 and 11/11 match.
- R2D (`v8_posterior_predictive_orbit`): 5/5, 5/5, 5/5 match.
- H4C: `detector_source_lock: true` recorded at run time (2026-07-26); the
  config lock (3 hashes) matches the committed tree.

All five legacy lock tests pass against the committed tree (16 tests, green).

**Verdict.** **RECONCILED — STALE TEXT, NO RE-BAKE.** The gap ledger's
2026-07-30 sentence "currently detect hash drift" described a transient
pre-commit working-tree state that was reverted before commit `4eb0124`. The
committed sources equal the originally locked run-time sources; F16's own
refusal rule ("do not relabel or rerun the old frozen protocol against
changed source") was not violated in the committed history.

**Actions taken.** F16 row evidence sentence corrected in
`docs/SUICA_FOUNDATION_GAP_LEDGER.md` plus a dated reconciliation note;
ledger row V8-F16-ADJ1.

## Item 5 — small factual corrections

1. **README test count**: "release audit: 302 passed" → 970 passed
   (2026-08-03 full suite; the sealed v0.2.1 tag tree remains at its own
   count and is verified separately by CI).
2. **V37F check count**: report said "All 25 frozen checks passed";
   `decision.json` `checks` holds **24** named checks. Corrected inline with
   a dated note.
3. **V37F budget index**: the dense-tail residual AUC .8635 [.8437, .8817] is
   the 256-event-budget cell. Per-budget profile (`cell_summary.csv`):
   32→.8896, 64→.9518, 128→.9497, 256→.8635, **512→.5393**. Annotated so the
   number cannot be quoted budget-free.
4. **R2B refusal-coverage figures**: rate .0125, the two refused cells,
   rank-6 retention, and `SUPPORT_SHIFT`-only reasons are artifact-backed
   (`decision.json`, `metrics.csv`). The two coverage fractions .6875/.75 are
   **SESSION_RECOMPUTED_UNPERSISTED** (recomputed during the 2026-08-01
   review; bundles persist score matrices only) and are downgraded
   accordingly; `refusal_coverage_note.json` records this beside the
   artifacts.
5. **PANDORA provenance**: the report now names its run directory and notes
   the missing `run_manifest.json` in all three run dirs (folded into
   item 1's addendum).

## Item 6 — process rules (codified)

Appended to `docs/V7_PROCESS_AUDIT_20260717.md`: (1) registration commits
precede execution, results commit separately — a seal sharing one commit with
its outcome is EXPLORATORY by construction; (2) date-typed run-suffixes that
are not execution dates (e.g. `smoke_20260816` executed 2026-07-29) are
banned; (3) a numeric lockbox over V8-era headline numbers is queued for
v0.3.0.

## Item 7 — research-repo reconciliation

A dated audit entry in the research repository's
`docs/SUICA_CLAIMS_LEDGER.md` (Audit log) records the V8-era label events
from that repo's standpoint: the full-scale PANDORA re-join and the post-hoc
operator selection (adjudicated release-side), and the Essays confirm-half
text consumption with label budget unchanged.

---

## Verification and gate release

- Full suite after these edits: **970 passed** (docs/appends plus one
  docstring; no behavior touched).
- CI: the per-push job verifies the sealed v0.2.1 tag tree in a worktree and
  is unaffected by these main-branch edits.
- Run artifacts were not modified; one new derived file was added beside the
  R2B artifacts (`refusal_coverage_note.json`).

With items 1–5 landed and item 7 recorded, the 2026-08-01 review's push block
is **lifted**. The v0.3.0 lockbox (item 6.3) is queued work, not a push
blocker.
