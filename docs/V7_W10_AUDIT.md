# V7 W10 Audit Record — the downgrade of V6-W10 (invisible-factor anatomy)

Recorded 2026-07-17. This document is the audit record that the CLAIMS_LEDGER
V6-W10 row and THEORY_FORMAL_NOTES_V3 previously cited only as "later audit"
without a document existing anywhere. The downgrade itself occurred in the
2026-07-15 V7 audit (its ledger marker was previously backdated to 2026-07-12;
that backdating is corrected in `docs/CLAIMS_LEDGER.md` and inventoried in
`docs/V7_PROCESS_AUDIT_20260717.md`). The GROUNDS below are real and were
independently verified against the original script
(`scripts/run_suica_v6_w10_invisible_anatomy_v1.py` in the research repo,
historical twin at `/Volumes/mobile3/projects/project persona`).

## Scope

V6-W10 (F15, "anatomy of the invisible factor") reported a person-level
susceptibility result on the gust1_P motion axis: split-half stability of mean
|activation| r = .441, ICC-share .381, n = 81 Tier-U users, with a
PANDORA/Essays activation variance-ratio contrast of 1.678 / 1.035. The
original text called this an "amplitude trait". All of those numbers are
preserved unchanged; this audit changes their LICENSE, not their values.

## The four verified grounds

1. **cid-parity split-half (script line ~32).** The person split-half was
   computed on odd/even comment-id parity halves, which is not a validated
   time or occasion split. Parity splits interleave adjacent material and
   inflate reliability; the program's own OP-15 precedent measured roughly
   2.5x inflation for parity/adjacency splits relative to honest contiguous
   halves (cf. the E5-P-E5c adjudication: parity 0.352/0.390 vs contiguous
   0.157/0.049).

2. **Same-sample axis fit (script lines ~407-417).** The gust1_P axis was fit
   on the same PANDORA m=3 texts that were subsequently scored — discovery and
   evaluation overlap. The axis is therefore partly tuned to the evaluation
   sample, and any person-level statistic computed from its activations
   inherits that optimism.

3. **Selection optimism uncorrected by the null.** The column-shuffle null
   never repeats the axis-selection step inside the null draws. A null that
   scores a FIXED axis against shuffled data does not price the optimism of
   having selected that axis on the same data; the reported significance is
   therefore an upper bound on evidence, not a calibrated test.

4. **Missing controls.** No opportunity controls (length, boundaries, format
   affordance), no format controls (the W9 cap-artifact stratum borders this
   cohort), and no matched-stranger baseline (the E4-react lesson: person
   "signatures" can be mostly shared population profiles until a stranger null
   subtracts the normative component).

## Conclusion (the downgrade)

The `.441` split-half is a **descriptive same-sample candidate**, not an
amplitude trait, not a stable person parameter, and not a person-level
measurement. The registered kill (r < .1) not firing is uninformative at this
tier because the estimator was inflated by grounds 1-3 in unknown combination.
The Essays contrast direction (1.678 vs 1.035) remains a valid descriptive
observation about where the factor's variance lives.

## Registered path to rescue-or-burial

A cross-fitted rerun under SIM-P3/P5/P6, registered before execution, with all
three of:

1. **Axis estimated on disjoint authors** — the gust1_P (or successor) axis is
   fit on an author set disjoint from every scored user (cross-fitted; no
   same-sample axis contact).
2. **Person-level split-half on held-out texts** — contiguous or time-gapped
   halves (no cid-parity), computed only on texts never touched by axis
   estimation.
3. **Matched-stranger null + opportunity/format controls** — the person
   statistic must clear a matched-stranger baseline, with opportunity and
   format covariates recorded, and the null must repeat axis selection.

If the person-level susceptibility survives all three, the candidate is
rescued at the appropriate tier; if not, it is buried and the row records the
burial. Either outcome closes the claim honestly.

## Companion: the V6-E4 downgrade (same audit, same family of defects)

The V6-E4 row ("person-level motion-style retry", gate>=5 comp2 lam 1.641 rep
.777; gate>=8 comp1 lam 2.137 rep .784 — values preserved) was downgraded on
parallel grounds in the same 2026-07-15 V7 audit: the static frame, the
residualization, the rank choice, and the axis were all fitted on the same
users; the shuffle null destroyed projection-induced dependence rather than
pricing it; and component matching allowed many-to-one best matches. Required
rescue path: outer-user cross-fit, refit-inside-the-null, and
one-to-one/projector-based component confirmation (SIM-P3/P4). E4's separate
V7.2-E4 post-hoc-labeling issue (the own-vs-stranger alignment family) is a
distinct finding recorded in `docs/V7_DISCOVERY_LEDGER.md` and
`docs/V7_PROCESS_AUDIT_20260717.md`.

## Cross-references

- `docs/CLAIMS_LEDGER.md` — V6-W10 and V6-E4 rows (dated corrections applied
  2026-07-17).
- `docs/THEORY_FORMAL_NOTES_V3.md` — F15 results section (citation updated to
  this document).
- `docs/V7_PROCESS_AUDIT_20260717.md` — the process findings (backdating,
  in-place edits, tag re-points) surrounding this downgrade.
- T8-prime (`docs/THEORY_V6.md`): W10 is one of the three instruments behind
  the "instruments do not certify kernel rank" claim; with W10 and E4
  downgraded, that claim is demonstrated for 2/3 instruments — TGEO-P9's
  cross-fit re-audit is the open third (see the TGEO-P9 row marker,
  2026-07-17).
