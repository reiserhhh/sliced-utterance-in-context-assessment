# OP-31 Prospective Seal #1 — time's lockbox (label-free, budget-free)

Sealed 2026-07-07. The predictions below concern an X-market collection
window strictly AFTER this commit. They are STRUCTURAL (need no labels) and
are fixed by the content hash; the scorer
(`scripts/run_suica_op31_prospective_seal_v1.py --score`) runs only when the
future data exists. This is the seal of record (the script's PREDICTIONS
dict is the machine copy; this doc is the human copy; both are tracked).

- **self_sha256** = `670b867fc4098ad1ef4dfc9d5d67af68edcb0ddab8164a88c9ef2123756bea78`
- Window: next X-market collection strictly after the seal commit date.
- Eligibility: >= 20 EN posts/account, disjoint early/late halves by timestamp.

Predictions:
- **P31-1**: same-account early/late symbol-choice cosine AUC vs random-pair >= 0.65 (C1 miniaturization, PRED-2 re-tested on fresh accounts).
- **P31-2**: first-person style-base disjoint-occasion retest >= 0.35 (conservative floor for X's short posts).
- **P31-3**: within-window FORM word rates have higher split-half reliability than CONTENT rates (form/content ordering, within-corpus — distinct from PRED-4's cross-corpus geometry).
- **P31-4**: >= 11 of the 21 OP-33 co-selection axes (transported transform) retest >= 0.25 on the fresh window.

Success rule: **>= 3 of 4 hold.** No re-fitting, no post-hoc prediction edits.
Why this matters: a confirmation here cannot be back-fitted, because the
text is written after the seal. Re-arm each round with a new window; costs
zero lockbox budget.
