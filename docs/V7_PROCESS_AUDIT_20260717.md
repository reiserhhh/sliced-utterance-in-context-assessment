# V7 / v0.2.0 Process Audit Record (2026-07-17)

An adversarial audit of the V7 evolution and the v0.2.0 release completed
2026-07-17. The operator accepted the process findings and ordered
remediation. This document is the permanent record of those findings and of
the standing rules adopted in response. Verdict shape: the SUBSTANCE of the
V7 results survived independent verification (numbers reproduce; the max-T
machinery and the W10-downgrade grounds were independently verified); the
PROCESS around the release violated the program's own governance in the
specific ways inventoried below.

## 1. The six v0.2.0 tag re-points

The v0.2.0 tag was deleted and re-created six times within 25 minutes on
2026-07-15. The dangling tag objects remain in the object database and were
recovered during the audit (tag object -> tagged commit):

| # | tag object | tagged commit |
|---|---|---|
| 1 | 92003ba | 5259f1b (the "freeze" commit) |
| 2 | cf955b9 | 607fa20 |
| 3 | 9ec7cf4 | 3a7e1e2 |
| 4 | 629b3f2 | df3fdae |
| 5 | df23e56 | bd78982 |
| 6 (live) | 1be09a5 | ebbdce6 |

Each re-point silently changed what "v0.2.0" refers to. In addition,
`release/v0.2.0/LOCKBOX_MANIFEST.json` was regenerated five times AFTER the
declared freeze. A tag that moves six times and a lockbox manifest that is
regenerated post-freeze do not constitute a freeze. The existing v0.2.0 tag
is now immutable-as-is (warts recorded here); it must never be re-pointed or
deleted again.

## 2. Squash-commit loss of registration verifiability

The release history was squashed in a way that destroyed the commit-level
evidence chain by which "registered BEFORE run" claims are verified: a
registration is only provable when the commit containing the frozen
config/predictions demonstrably precedes the run artifacts. After the squash,
several registration claims in release documents can no longer be
independently re-derived from the release repo's own history and rest on the
research repo's (intact) history instead.

## 3. The E4 post-hoc timeline

E4's own-vs-stranger alignment AUC family (.719--.805, max-T p=.005; 48-arm
.791--.862) shipped labeled "registered" but was designed and first run
minutes AFTER the 8/10 fine-view linear-transport failures were on disk.
Timeline (2026-07-15 UTC):

- r1 17:10:53Z — same-source endpoints only;
- registry config mtime 17:12:39Z — the endpoint registry was modified;
- r2 17:15:31Z — source-disjoint transport added; 8/10 endpoints FAIL;
- r3 17:21:17Z — the alignment family added; 10/10 PASS.

The alignment result stands as computed (machinery independently verified),
but its tier is POST-HOC EXPLORATORY. Corrected 2026-07-17 in
`docs/V7_DISCOVERY_LEDGER.md` (row V7.2-E4) and
`docs/V7_OPERATOR_INDEXED_MULTIVIEW_V71.md`.

## 4. In-place-edit inventory

House rule: adjudications and dated log entries are append-only; corrections
carry true dates. The following violations were found and are now disclosed
in the affected documents:

- **Backdated downgrade markers.** The "DOWNGRADED 2026-07-12" markers on the
  CLAIMS_LEDGER V6-W10 and V6-E4 rows were written during the 2026-07-15 V7
  work but dated 07-12; every commit in both repos through 2026-07-13 carries
  the opposite (pre-downgrade) text. Corrected 2026-07-17 in
  `docs/CLAIMS_LEDGER.md` and `docs/THEORY_FORMAL_NOTES_V3.md`.
- **Phantom citation.** The W10 downgrade cited a "Later audit" that existed
  nowhere as a document. Its grounds are real and independently verified;
  they are now recorded as `docs/V7_W10_AUDIT.md`.
- **df3fdae** edited a dated 2026-07-12 audit-log entry in place ("T8 stands
  (rank(ker(A))>=1...)" -> "the narrow T8 operator statement stands...").
  Disclosed 2026-07-17 in `docs/CLAIMS_LEDGER.md`; the edit's content is
  adopted as the controlling adjudication, the method acknowledged as a
  violation.
- **bd78982** ("docs: retract legacy external-validity wording") and
  **ebbdce6** ("docs: align legacy W10 narrative with V7 audit") rewrote
  historical wording in place rather than appending dated corrections.
- **Freeze-commit row rewrites.** The freeze commit **5259f1b** deleted
  recorded caveats from the release CLAIMS_LEDGER V5PORT row: the convergence
  numbers, the laugh_rate-"www" scorer-defect caveat, and the note naming the
  unregistered opening-#2 candidates. Kills and caveats are never deleted.

## 5. Deleted-caveat restoration

The V5PORT material deleted by 5259f1b was recovered verbatim from the
research repo's authoritative `docs/SUICA_CLAIMS_LEDGER.md` and restored into
the release `docs/CLAIMS_LEDGER.md` V5PORT row as a dated appended
restoration (2026-07-17), not a silent rewrite.

## 6. Related status reconciliations closed in this cycle

- TGEO-P9 carried three inconsistent statuses across documents
  (CLAIMS_LEDGER "CONFIRMED... passes all gates" vs PAPER2_MOTION_SKELETON
  "EXPLORATORY... cross-fit null pending" vs T8-prime's 3-instrument claim
  demonstrated only for 2). Reconciled 2026-07-17: pre-V7-standard status
  stands as recorded; V7-standard cross-fit re-audit is PENDING; T8-prime's
  "instruments do not certify kernel rank" is demonstrated for 2/3
  instruments (W10, E4), TGEO-P9 the open third.
- RELEASE_NOTES_V020 effective-rank range corrected 22.8--22.9 ->
  22.7--22.9 (WORD12 artifact value 22.7496), with the TGEO-P3 rank-4 vs W4b
  capacity-descriptor bridge paragraph added (different objects; neither
  overturns the other).

## 7. Standing rules going forward

1. **Release tags are immutable.** A published tag is never deleted or
   re-pointed. Anything that would change a tagged state gets a version bump
   (as v0.2.1 does for this remediation). Lockbox manifests are generated
   once, before the tag, and never regenerated after it.
2. **Adjudications are append-only with true dates.** Ledger rows, audit-log
   entries, and downgrade markers may only be corrected by dated appended
   notes carrying the date the correction was actually made. Backdating a
   marker is itself a findable violation.
3. **Registration commits precede runs.** A family is "registered" only if
   the commit freezing it verifiably precedes the first run artifact.
   Families added after results are on disk are POST-HOC EXPLORATORY and must
   ship labeled as such. History operations (squashes, rebases) that destroy
   the registration evidence chain are prohibited on release branches.
