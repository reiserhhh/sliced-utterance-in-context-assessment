# V8 Adaptive Rank and Fixed Reference V3.7E Plan

Status: `PROSPECTIVELY_SEALED_BEFORE_CONFIRMATION`

## Question

V3.7D showed identity without full recovery when a true rank-12 operator was
forced through a rank-8 estimator. V3.7E asks whether that reverse separation
survives an estimator that does not know the true rank but selects capacity
only from disjoint calibration authors.

The fixed external-reference object is

\[
D_u^{(0)}
=
\operatorname{ilr}(\Pi_u^{Q_0})
-
\operatorname{ilr}(\Pi_{P_0}^{Q_0}).
\]

The paired estimators are fixed rank 8, adaptive rank, and scorer-only true
rank. Recovery and identity retain the V3.7D definitions.

## Adaptive selector

Candidate ranks are `0/2/4/6/8/10/12/16/20/24`. Four author folds estimate a
cross-session denoiser on training authors and score symmetric prediction
error on held-out calibration authors. The one-standard-error rule selects
the smallest admissible rank. True rank, evaluation authors, truth profiles,
and identity metrics are unavailable to selection.

## Author separation

Every world contains:

- 256 external-reference authors;
- 128 calibration authors;
- 96 evaluation authors.

The three sets are disjoint. The fixed router is fitted only once on the
external-reference authors. Denoising rank and basis are fitted only on the
calibration authors. All primary scores use the evaluation authors.

## Registered worlds

- true rank `4/8/12/16`;
- event budget `64/128`;
- flat and geometrically decaying spectra;
- fixed total author RMS `.30`;
- author-by-context response RMS `.20`, generated as a low-rank
  \(B_u z_c\) term whose discovery-design mean is fixed;
- 60 confirmation repetitions after discovery and content sealing.

The primary opportunity/population-shift arms use rank 8, 128 events, and the
flat spectrum.

## Reference refutations

1. Opportunity shift changes context exposure but not author response.
   Equal-\(Q_0\) standardization must reduce systematic same-author drift
   relative to a naive exposure-weighted profile. The registered comparison
   averages eight independent panels; single-panel variance remains reported
   separately rather than being mislabeled as transport bias.
2. Population shift plants a common movement in one author direction.
   The fixed reference must retain its direction and magnitude; refitting the
   reference on the shifted target cohort must erase most of it.
3. Permuting calibration-session pairs must collapse selected rank and
   matching performance.

## Decisions

- `PASS_MISSPECIFICATION_EXPLAINED`: adaptive estimation closes the rank-12
  oracle gap and changes identity-only into recovery-plus-identity.
- `PASS_REVERSE_SEPARATION_PERSISTS`: adaptive estimation closes the oracle
  gap but identity-only remains common.
- `STOP_SELECTOR_INVALID`: rank selection fails its controls or cannot close
  the oracle gap.
- `STOP_REFERENCE_NONTRANSPORTABLE`: opportunity or population-shift gates
  fail.
- all other patterns: `STOP_AMBIGUOUS`.

Single-author confidence regions are explicitly deferred to V3.7F. This
experiment establishes no personality, human-text, or clinical claim.

## Frozen confirmation gates

The confirmation uses 60 fresh worlds and canonical seed `20410617`.

1. Numeric output, 256/128/96 author separation, all event seeds, paired
   worlds, row count, parent seal, and artifact inventory must pass.
2. Session-permuted calibration must select rank at most 2 and produce
   hard-neighbor AUC in `[.45,.55]` in at least 90% of worlds.
3. Rank 24 may be selected in at most 5% of all registered cells.
4. At true rank 8, adaptive versus fixed-rank Fisher-z may not be below
   `-.05`, and hard-neighbor AUC may not be below `-.03`.
5. At true rank 12, adaptive estimation must close at least .80 of the
   fixed8-to-oracle Fisher-z gap, with bootstrap lower bound at least .60.
   The paired NRMSE closure lower bound must exceed zero.
6. Opportunity standardization must reduce eight-panel systematic drift by
   at least 50% on average, with bootstrap lower bound above zero.
7. Fixed-reference population-shift direction cosine must be at least .90
   and amplitude must be in `[.80,1.20]`. Target-cohort recentering may retain
   at most .40.
8. `PASS_MISSPECIFICATION_EXPLAINED` additionally requires fixed-rank
   identity-only rate at least .75 and adaptive identity-only rate at most
   .25. `PASS_REVERSE_SEPARATION_PERSISTS` instead requires adaptive
   identity-only rate at least .75 after the oracle-gap gate passes.

The pre-seal smoke series and 16-world discovery output are development
artifacts and are forbidden from confirmation scoring.
